"""Offline regression checks for participant setup; no real credentials needed."""

import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import openai

import foundry_api
import smoke_test


class AgentResponseTests(unittest.TestCase):
    def test_tool_round_trips_keep_reasoning_and_report_progress(self):
        client = MagicMock()
        handler = MagicMock(return_value='{"anomalies": []}')
        progress = []
        tool_calls = [
            SimpleNamespace(type="function_call", name="check_thresholds", arguments=json.dumps({"machine_id": machine_id}), call_id=machine_id)
            for machine_id in ("MX-001", "EX-002")
        ]
        client.responses.create.side_effect = [
            SimpleNamespace(id="response-1", output=tool_calls),
            SimpleNamespace(id="response-2", output=[tool_calls[0]]),
            SimpleNamespace(id="response-3", output=[], output_text="Scan complete"),
        ]
        tools = [{"type": "function", "name": "check_thresholds"}]
        result = foundry_api.run_agent_response(
            client, model="gpt-5.4", instructions="Check machines", input_text="Scan",
            tools=tools, tool_handlers={"check_thresholds": handler},
            reasoning_effort="low", on_progress=progress.append,
        )
        self.assertEqual(result, "Scan complete")
        requests = client.responses.create.call_args_list
        self.assertEqual(len(requests), 3)
        for request in requests:
            self.assertEqual(request.kwargs["reasoning"], {"effort": "low"})
            self.assertEqual(request.kwargs["tools"], tools)
        self.assertNotIn("previous_response_id", requests[0].kwargs)
        self.assertEqual(requests[1].kwargs["previous_response_id"], "response-1")
        self.assertEqual(requests[2].kwargs["previous_response_id"], "response-2")
        self.assertEqual([item["call_id"] for item in requests[1].kwargs["input"]], ["MX-001", "EX-002"])
        self.assertEqual(handler.call_count, 3)
        self.assertEqual(progress[0], "Model request 1: waiting for gpt-5.4...")
        self.assertIn("Model request 3 completed in", progress[-1])
        self.assertEqual(progress.count("Running tool: check_thresholds"), 3)

    def test_default_request_keeps_existing_api_options(self):
        client = MagicMock()
        client.responses.create.return_value = SimpleNamespace(output=[], output_text="Ready")
        self.assertEqual(foundry_api.run_agent_response(
            client, model="test-model", instructions="Test", input_text="Hello",
        ), "Ready")
        client.responses.create.assert_called_once_with(
            model="test-model", instructions="Test", input="Hello", tools=[],
        )


class AnomalyScanTests(unittest.TestCase):
    def setUp(self):
        source = Path(__file__).resolve().parent / "factory/challenge-2-workflow/workflow.py"
        with patch.dict(os.environ), patch("dotenv.load_dotenv"):
            self.scan = runpy.run_path(str(source))["run_anomaly_scan"]

    def run_scan(self, model="gpt-5.4", error=None):
        factory = MagicMock()
        client = factory.return_value.__enter__.return_value
        request = client.with_options.return_value.responses.create
        request.return_value = SimpleNamespace(output=[], output_text="Scan complete")
        request.side_effect = error
        output = io.StringIO()
        with patch.dict(self.scan.__globals__, create_foundry_client=factory, MODEL_DEPLOYMENT_NAME=model):
            with contextlib.redirect_stdout(output):
                if error:
                    with self.assertRaises(type(error)):
                        self.scan("anomaly-detection-agent")
                else:
                    self.assertEqual(self.scan("anomaly-detection-agent"), "Scan complete")
        client.with_options.assert_called_once_with(timeout=90.0, max_retries=0)
        factory.return_value.__exit__.assert_called_once()
        self.assertIn("Model request 1: waiting", output.getvalue())
        return request.call_args.kwargs

    def test_scan_requests_low_reasoning_for_workshop_model(self):
        self.assertEqual(self.run_scan()["reasoning"], {"effort": "low"})

    def test_other_deployments_keep_their_reasoning_defaults(self):
        self.assertNotIn("reasoning", self.run_scan(model="other-model"))

    def test_timeout_closes_client_without_retrying(self):
        self.run_scan(error=openai.APITimeoutError(request=MagicMock()))

    def test_batch_tool_supplies_all_five_machines_in_one_round_trip(self):
        factory = MagicMock()
        client = factory.return_value.__enter__.return_value
        request = client.with_options.return_value.responses.create
        request.side_effect = [
            SimpleNamespace(id="response-1", output=[SimpleNamespace(
                type="function_call", name="check_all_thresholds", arguments="{}", call_id="all-machines",
            )]),
            SimpleNamespace(id="response-2", output=[], output_text="Scan complete"),
        ]
        with patch.dict(self.scan.__globals__, create_foundry_client=factory):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(self.scan("anomaly-detection-agent"), "Scan complete")
        self.assertEqual(request.call_count, 2)
        tool = request.call_args_list[0].kwargs["tools"][0]
        self.assertEqual(tool["name"], "check_all_thresholds")
        self.assertEqual(tool["parameters"]["required"], [])
        outputs = request.call_args_list[1].kwargs["input"]
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]["call_id"], "all-machines")
        machines = json.loads(outputs[0]["output"])["machines"]
        self.assertEqual([machine["machine_id"] for machine in machines], ["MX-001", "EX-002", "CP-003", "CU-004", "IS-005"])
        self.assertEqual([machine["machine_id"] for machine in machines if machine["anomalies"]], ["MX-001", "CP-003", "IS-005"])


class ConnectionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.env_path = self.root / "factory" / ".env"
        self.env_path.parent.mkdir()
        self.env_path.write_text(
            "FOUNDRY_ENDPOINT=https://example.test/\nMODEL_DEPLOYMENT_NAME=test-model\nAPI_KEY=test-only-key\n",
            encoding="utf-8",
        )
        for replacement in (
            patch.object(smoke_test, "WORKSHOP_ROOT", self.root),
            patch.object(sys, "argv", ["smoke_test.py", "factory"]),
            patch.dict(os.environ, {}, clear=True),
        ):
            replacement.start()
            self.addCleanup(replacement.stop)

    def run_check(self, text="Ready!", error=None):
        client = MagicMock()
        request = client.with_options.return_value.responses.create
        request.return_value.output_text = text
        request.side_effect = error
        output = io.StringIO()
        with patch.object(smoke_test, "create_foundry_client") as factory:
            factory.return_value.__enter__.return_value = client
            with contextlib.redirect_stdout(output):
                if error is None:
                    smoke_test.main()
                else:
                    with self.assertRaises(SystemExit) as raised:
                        smoke_test.main()
                    self.assertNotIn("sensitive-test-marker", str(raised.exception))
                    return str(raised.exception)
            factory.return_value.__exit__.assert_called_once()
        client.with_options.assert_called_once_with(timeout=30.0, max_retries=0)
        return output.getvalue()

    def test_valid_text_does_not_require_exact_model_wording(self):
        self.assertIn("WORKSHOP_READY", self.run_check("Ready to help!"))

    def test_empty_model_output_is_actionable(self):
        with self.assertRaisesRegex(SystemExit, "returned no text"):
            self.run_check("   ")

    def test_missing_file_mentions_filename_and_setup(self):
        self.env_path.unlink()
        with self.assertRaisesRegex(SystemExit, "not .env.txt"):
            smoke_test.main()

    def test_placeholder_is_rejected_without_network(self):
        self.env_path.write_text(
            "FOUNDRY_ENDPOINT=https://example.test/\nMODEL_DEPLOYMENT_NAME=test-model\nAPI_KEY=XXX\n",
            encoding="utf-8",
        )
        with patch("foundry_api.OpenAI") as constructor:
            with self.assertRaisesRegex(SystemExit, "Replace API_KEY=XXX"):
                smoke_test.main()
            constructor.assert_not_called()

    def test_explicit_scenario_file_overrides_stale_shell_settings(self):
        os.environ["MODEL_DEPLOYMENT_NAME"] = "old-model"
        self.run_check()
        self.assertEqual(os.environ["MODEL_DEPLOYMENT_NAME"], "test-model")

    def test_service_errors_are_actionable_and_do_not_echo_response_bodies(self):
        for error_type, status, expected in (
            (openai.AuthenticationError, 401, "current key"),
            (openai.PermissionDeniedError, 403, "Access was denied"),
            (openai.NotFoundError, 404, "workshop template"),
            (openai.RateLimitError, 429, "retry once"),
            (openai.InternalServerError, 500, "HTTP 500"),
        ):
            with self.subTest(status=status):
                response = MagicMock(status_code=status, request=MagicMock(), headers={})
                error = error_type("sensitive-test-marker", response=response, body={"error": "sensitive-test-marker"})
                self.assertIn(expected, self.run_check(error=error))

    def test_network_and_timeout_errors_are_actionable(self):
        request = MagicMock()
        for error in (openai.APIConnectionError(request=request), openai.APITimeoutError(request=request)):
            with self.subTest(error=type(error).__name__):
                self.assertIn("network restrictions", self.run_check(error=error))


class ScriptImportTests(unittest.TestCase):
    def test_all_scenarios_import_without_environment_files(self):
        source_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(source_root / "foundry_api.py", root / "foundry_api.py")
            for scenario in ("factory", "claims", "callcenter"):
                for relative in ("challenge-1-build/agents.py", "challenge-2-workflow/workflow.py"):
                    with self.subTest(scenario=scenario, script=relative):
                        target = root / scenario / relative
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(source_root / scenario / relative, target)
                        environment = os.environ.copy()
                        environment.pop("PYTHONPATH", None)
                        result = subprocess.run(
                            [sys.executable, "-c", "import runpy, sys; runpy.run_path(sys.argv[1])", str(target)],
                            cwd=target.parent,
                            env=environment,
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )
                        self.assertEqual(result.returncode, 0, result.stderr)
                        env_path = root / scenario / ".env"
                        env_path.write_text(
                            "FOUNDRY_ENDPOINT=https://example.test/\nMODEL_DEPLOYMENT_NAME=scenario-model\nAPI_KEY=test-only-key\n",
                            encoding="utf-8",
                        )
                        environment["MODEL_DEPLOYMENT_NAME"] = "stale-shell-model"
                        result = subprocess.run(
                            [sys.executable, "-c", "import runpy, sys; module = runpy.run_path(sys.argv[1]); assert module['MODEL_DEPLOYMENT_NAME'] == 'scenario-model'", str(target)],
                            cwd=target.parent,
                            env=environment,
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )
                        self.assertEqual(result.returncode, 0, result.stderr)
                        env_path.unlink()


if __name__ == "__main__":
    unittest.main()