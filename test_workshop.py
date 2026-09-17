"""Offline regression checks for participant setup; no real credentials needed."""

import contextlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import openai

import smoke_test


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