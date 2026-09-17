"""Run a scenario agent in local Agent Framework DevUI using a Foundry API key."""

import argparse
import importlib.util
from pathlib import Path
import sys
from urllib.parse import urlsplit

from dotenv import dotenv_values


WORKSHOP_ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {
    "factory": (
        "check_thresholds",
        "You help review fictional machine readings for TireForge Industries. "
        "For a machine question, always call check_thresholds with its machine ID. "
        "Report the measured exceptions, possible explanations, and checks a human engineer needs to make. "
        "Do not invent equipment types or present a diagnosis as confirmed.",
    ),
    "claims": (
        "assess_claim",
        "You help review fictional insurance claims for ClaimSight Insurance. "
        "For a claim question, always call assess_claim with its claim ID. "
        "Explain the supplied flags, missing information, and next steps for a human adjuster. "
        "A risk flag is not proof of fraud; do not invent policy terms or make a binding claim decision.",
    ),
    "callcenter": (
        "lookup_customer",
        "You help review fictional customer calls for NovaTel Communications. "
        "For a call question, always call lookup_customer with its call ID. "
        "Explain the likely intent, draft a courteous response, and identify any human review needed. "
        "Refer security concerns to a human. Do not invent refunds, offers, policies, or completed actions.",
    ),
}


def read_settings(scenario: str) -> dict[str, str]:
    env_path = WORKSHOP_ROOT / scenario / ".env"
    if not env_path.is_file():
        raise ValueError(f"Complete Connect first: {scenario}/.env is missing.")
    values = dotenv_values(env_path)
    settings = {name: (values.get(name) or "").strip() for name in (
        "FOUNDRY_ENDPOINT", "MODEL_DEPLOYMENT_NAME", "API_KEY"
    )}
    if not all(settings.values()) or settings["API_KEY"].casefold() == "xxx":
        raise ValueError(f"Check {scenario}/.env: the endpoint, model, and private API key must be filled in.")
    endpoint = urlsplit(settings["FOUNDRY_ENDPOINT"])
    if endpoint.scheme != "https" or not endpoint.hostname or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
        raise ValueError("FOUNDRY_ENDPOINT must be an HTTPS resource URL without credentials, query, or fragment.")
    if endpoint.path.rstrip("/"):
        raise ValueError("Use the resource root for FOUNDRY_ENDPOINT, without /openai/v1 or /api/projects.")
    return settings


def load_scenario_tool(scenario: str):
    script = WORKSHOP_ROOT / scenario / "challenge-2-workflow" / "workflow.py"
    spec = importlib.util.spec_from_file_location(f"bonus_{scenario}_workflow", script)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load the {scenario} workflow tool.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, SCENARIOS[scenario][0])


def build_agent(scenario: str, settings: dict[str, str]):
    from agent_framework import Agent
    from agent_framework.openai import OpenAIChatClient

    client = OpenAIChatClient(
        model=settings["MODEL_DEPLOYMENT_NAME"],
        api_key=settings["API_KEY"],
        base_url=settings["FOUNDRY_ENDPOINT"].rstrip("/") + "/openai/v1",
    )
    return Agent(
        id=f"{scenario}-assistant",
        name=f"{scenario}-assistant",
        description=f"Workshop {scenario} assistant with a local sample-data tool.",
        client=client,
        instructions=SCENARIOS[scenario][1] + " Keep the answer under 150 words. All data is fictional.",
        tools=[load_scenario_tool(scenario)],
    )


def configure_local_tracing() -> None:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider

    trace.set_tracer_provider(TracerProvider())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=SCENARIOS)
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    sys.path.insert(0, str(WORKSHOP_ROOT))
    try:
        settings = read_settings(args.scenario)
        agent = build_agent(args.scenario, settings)
    except ImportError:
        raise SystemExit("Install bonus-devui/requirements.txt in the separate bonus environment first.") from None
    except ValueError as error:
        raise SystemExit(str(error)) from None

    from agent_framework.devui import serve

    configure_local_tracing()
    print("DevUI captures fictional prompts, tool arguments, results, and replies for this session.")
    print("Keep the Codespaces port PRIVATE. No Azure portal or Application Insights is required.")
    print("DevUI's login token is separate from your Foundry API key. Never enter the Foundry key in the UI.")
    serve(
        entities=[agent],
        host="127.0.0.1",
        port=args.port,
        auto_open=False,
        mode="developer",
        auth_enabled=True,
        instrumentation_enabled=True,
    )


if __name__ == "__main__":
    main()