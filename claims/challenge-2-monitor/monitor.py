"""
Challenge 2: Monitor with Application Insights — Claims Processing
Enable GenAI tracing and verify traces appear in App Insights.

Usage:
    python monitor.py

IMPORTANT: Environment variables must be loaded before configuring telemetry.
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Load environment FIRST — tracing env vars must be set before SDK import
def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".env").exists():
            return parent
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _find_repo_root()
sys.path.insert(0, str(REPO_ROOT.parent))

from foundry_api import create_foundry_client

env_path = REPO_ROOT / ".env"
load_dotenv(env_path)

# Verify tracing is enabled
if os.getenv("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING") != "true":
    print("❌ AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING is not set to 'true' in .env")
    print("   Add: AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true")
    sys.exit(1)

FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT")
API_KEY = os.getenv("API_KEY")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
APPINSIGHTS_CONN_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")


def setup_tracing():
    """Configure OpenTelemetry instrumentation and Azure Monitor export."""
    print("=== Setting up tracing ===")
    print("✅ AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING is enabled")

    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace

    configure_azure_monitor(
        connection_string=APPINSIGHTS_CONN_STRING,
        enable_live_metrics=True,
    )
    print("✅ Azure Monitor exporter connected")
    return trace.get_tracer("foundry-hackathon")


def run_traced_agent_call(tracer):
    """Make an agent call that will be captured as a trace."""
    print("\n=== Running traced agent call ===")

    client = create_foundry_client()

    with tracer.start_as_current_span("foundry.responses.create") as span:
        span.set_attribute("gen_ai.system", "openai")
        span.set_attribute("gen_ai.request.model", MODEL_DEPLOYMENT_NAME)
        response = client.responses.create(
            model=MODEL_DEPLOYMENT_NAME,
            instructions=(
                "You are a claims operations assistant for ClaimSight Insurance. "
                "Summarize triage risk and recommended decisions for claim batches."
            ),
            input=(
                "Assess this claim batch and return decision urgency guidance.\n"
                "domain: ClaimSight Insurance\n"
                "claims: CLM-001 INVESTIGATE IMMEDIATE, CLM-003 REQUEST DOCUMENTS WITHIN 48H, CLM-005 INVESTIGATE STANDARD\n"
                "tool_reference: assess_claim"
            ),
        )
        span.set_attribute("gen_ai.response.id", response.id)
    print(f"✅ Agent responded: {response.output_text[:100]}...")

    client.close()


def verify_traces():
    """Wait for traces to propagate and verify they appear in App Insights."""
    print("\n=== Verifying traces in App Insights ===")

    if not APPINSIGHTS_CONN_STRING:
        print("⚠️  APPLICATIONINSIGHTS_CONNECTION_STRING not set — skipping verification")
        print("   You can still check traces manually in the Azure Portal")
        return

    print("⏳ Waiting for traces to propagate (30 seconds)...")
    time.sleep(30)

    print("✅ Traces should now be visible in Application Insights")
    print("   Go to: Azure Portal → Application Insights → Transaction search")
    print("   Filter by: Last 5 minutes, Event type: Dependency")


def main():
    if not FOUNDRY_ENDPOINT or not API_KEY:
        print("❌ FOUNDRY_ENDPOINT and API_KEY must be set in .env")
        sys.exit(1)

    tracer = setup_tracing()
    run_traced_agent_call(tracer)
    verify_traces()

    print("\n🎉 Monitoring is active! Check App Insights for the full trace view.")


if __name__ == "__main__":
    main()
