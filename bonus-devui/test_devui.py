"""Offline checks for the optional DevUI launcher; run in the bonus environment."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import queue
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("workshop_devui", Path(__file__).with_name("devui.py"))
bonus = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bonus)


class DevUIBonusTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.env_path = self.root / "factory" / ".env"
        self.env_path.parent.mkdir()

    def write_settings(self, endpoint="https://example.test/", key="test-only-key"):
        self.env_path.write_text(
            f"FOUNDRY_ENDPOINT={endpoint}\nMODEL_DEPLOYMENT_NAME=test-model\nAPI_KEY={key}\n"
            "APPLICATIONINSIGHTS_CONNECTION_STRING=unused-test-value\n",
            encoding="utf-8",
        )

    def test_configuration_uses_only_three_explicit_file_values(self):
        self.write_settings()
        with patch.object(bonus, "WORKSHOP_ROOT", self.root), patch.dict(os.environ, {"API_KEY": "stale-key"}):
            settings = bonus.read_settings("factory")
        self.assertEqual(settings, {
            "FOUNDRY_ENDPOINT": "https://example.test/",
            "MODEL_DEPLOYMENT_NAME": "test-model",
            "API_KEY": "test-only-key",
        })

    def test_missing_configuration_gives_connect_instruction(self):
        with patch.object(bonus, "WORKSHOP_ROOT", self.root):
            with self.assertRaisesRegex(ValueError, "Complete Connect"):
                bonus.read_settings("factory")

    def test_placeholder_and_blank_keys_are_rejected(self):
        for key in ("XXX", "xxx", "  "):
            with self.subTest(key=key), patch.object(bonus, "WORKSHOP_ROOT", self.root):
                self.write_settings(key=key)
                with self.assertRaisesRegex(ValueError, "private API key"):
                    bonus.read_settings("factory")

    def test_invalid_endpoint_does_not_echo_secret_material(self):
        for endpoint in (
            "http://example.test", "https://user:sensitive-marker@example.test",
            "https://example.test?api-key=sensitive-marker", "https://example.test/#sensitive-marker",
            "https://example.test/openai/v1", "https://example.test/api/projects/test",
        ):
            with self.subTest(endpoint=endpoint), patch.object(bonus, "WORKSHOP_ROOT", self.root):
                self.write_settings(endpoint=endpoint)
                with self.assertRaises(ValueError) as raised:
                    bonus.read_settings("factory")
                self.assertNotIn("sensitive-marker", str(raised.exception))

    def test_each_registered_agent_uses_existing_tool_and_key_client(self):
        settings = {"FOUNDRY_ENDPOINT": "https://example.test/", "MODEL_DEPLOYMENT_NAME": "test-model", "API_KEY": "test-only-key"}
        for scenario, record, identifier in (
            ("factory", "CP-003", "machine_id"),
            ("claims", "CLM-001", "claim_id"),
            ("callcenter", "CALL-007", "call_id"),
        ):
            with self.subTest(scenario=scenario), patch("dotenv.load_dotenv", return_value=False):
                agent = bonus.build_agent(scenario, settings)
                self.assertEqual(agent.name, f"{scenario}-assistant")
                result = json.loads(bonus.load_scenario_tool(scenario)(record))
                self.assertEqual(result[identifier], record)

    def test_main_enables_local_authenticated_instrumented_server(self):
        self.write_settings()
        with patch.object(bonus, "WORKSHOP_ROOT", self.root), patch.object(sys, "argv", ["devui.py", "factory"]), \
                patch.object(bonus, "build_agent", return_value="test-agent") as build, \
                patch.object(bonus, "configure_local_tracing") as tracing, \
                patch("agent_framework.devui.serve") as serve, contextlib.redirect_stdout(io.StringIO()) as output:
            bonus.main()
        build.assert_called_once()
        tracing.assert_called_once()
        serve.assert_called_once_with(
            entities=["test-agent"], host="127.0.0.1", port=8080, auto_open=False,
            mode="developer", auth_enabled=True, instrumentation_enabled=True,
        )
        self.assertNotIn("test-only-key", output.getvalue())

    def test_local_tracing_does_not_install_external_exporters(self):
        with patch("opentelemetry.trace.set_tracer_provider") as set_provider, \
                patch("opentelemetry.sdk.trace.TracerProvider") as provider:
            bonus.configure_local_tracing()
        provider.assert_called_once_with()
        set_provider.assert_called_once_with(provider.return_value)
        provider.return_value.add_span_processor.assert_not_called()

    def test_fresh_process_displays_token_and_protects_api(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        program = (
            "import importlib.util, sys, dotenv; "
            "dotenv.load_dotenv = lambda *args, **kwargs: False; "
            "spec = importlib.util.spec_from_file_location('bonus_server', 'bonus-devui/devui.py'); "
            "bonus = importlib.util.module_from_spec(spec); spec.loader.exec_module(bonus); "
            "bonus.read_settings = lambda scenario: {'FOUNDRY_ENDPOINT': 'https://example.test/', "
            "'MODEL_DEPLOYMENT_NAME': 'test-model', 'API_KEY': 'test-only-key'}; "
            f"sys.argv = ['devui.py', 'factory', '--port', '{port}']; bonus.main()"
        )
        environment = os.environ.copy()
        environment.pop("DEVUI_AUTH_TOKEN", None)
        process = subprocess.Popen(
            [sys.executable, "-u", "-c", program], cwd=ROOT, env=environment,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        lines = queue.Queue()

        def read_output():
            for line in process.stdout:
                lines.put(line.strip())

        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()
        token = None
        token_next = False
        try:
            while True:
                line = lines.get(timeout=30)
                if token_next:
                    token = line
                    token_next = False
                if "authentication enabled with auto-generated token:" in line:
                    token_next = True
                if "Uvicorn running on" in line:
                    break
            self.assertIsNotNone(token, "DevUI did not display a login token")
            endpoint = f"http://127.0.0.1:{port}/v1/entities"
            with self.assertRaises(HTTPError) as raised:
                urlopen(endpoint, timeout=10)
            self.assertEqual(raised.exception.code, 401)
            raised.exception.close()
            with urlopen(Request(endpoint, headers={"Authorization": f"Bearer {token}"}), timeout=10) as response:
                content = response.read().decode()
            self.assertNotIn("test-only-key", content)
            self.assertEqual(json.loads(content)["entities"][0]["name"], "factory-assistant")
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
            reader.join(timeout=5)
            process.stdout.close()


if __name__ == "__main__":
    unittest.main()