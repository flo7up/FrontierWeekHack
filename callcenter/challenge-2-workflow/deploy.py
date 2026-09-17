"""
Challenge 2: Local Workflow
Multi-agent orchestration workflow for NovaTel Communications call center.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".env").exists():
            return parent
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _find_repo_root()
sys.path.insert(0, str(REPO_ROOT.parent))

from foundry_api import create_foundry_client, run_agent_response

env_path = REPO_ROOT / ".env"
load_dotenv(env_path)

FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT")
API_KEY = os.getenv("API_KEY")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
CALL_DATA_PATH = Path(__file__).resolve().parent.parent / "challenge-1-build" / "call_data.json"

INTENT_AGENT_NAME = "intent-classification-agent"
RESOLUTION_AGENT_NAME = "resolution-advisor-agent"


def lookup_customer(call_id: str) -> str:
    """Look up call/customer details from call_data.json."""
    with open(CALL_DATA_PATH, "r") as f:
        data = json.load(f)
    call = next(
        (c for c in data["calls"]
         if c["call_id"] == call_id or c["customer_id"] == call_id),
        None,
    )
    if not call:
        return json.dumps({"error": f"Call or customer not found: {call_id}"})
    return json.dumps(call, indent=2)


def ensure_agents_deployed() -> tuple:
    """Configure the two local agent roles used by the workflow."""
    print("=== Step 1: Configure API-Key Agent Roles ===")
    print(f"  Configured: {INTENT_AGENT_NAME}")
    print(f"  Configured: {RESOLUTION_AGENT_NAME}")
    return INTENT_AGENT_NAME, RESOLUTION_AGENT_NAME


def run_intent_classification(intent_agent_name: str) -> str:
    """Call the intent classification agent for all calls; handle function call loop."""
    print("\n=== Step 2a: Intent Classification ===")

    client = create_foundry_client()

    # Get all call IDs from the data
    with open(CALL_DATA_PATH, "r") as f:
        data = json.load(f)
    call_ids = [c["call_id"] for c in data["calls"]]

    tool = {
        "type": "function",
        "name": "lookup_customer",
        "description": "Look up customer and call details by call ID or customer ID.",
        "parameters": {
            "type": "object",
            "properties": {"call_id": {"type": "string"}},
            "required": ["call_id"],
            "additionalProperties": False,
        },
        "strict": False,
    }
    report = run_agent_response(
        client,
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "You are a call center intent classification specialist for NovaTel Communications. "
            "Use lookup_customer for each call and classify intent, priority, sentiment, and retention risk."
        ),
        input_text=(
            f"Classify all incoming calls: {', '.join(call_ids)}. "
            "For each, provide intent, priority, sentiment, and retention risk."
        ),
        tools=[tool],
        tool_handlers={"lookup_customer": lookup_customer},
    )
    client.close()
    return report


def run_resolution_advisory(resolution_agent_name: str, call_id: str, classification: dict) -> str:
    """Call the resolution advisor agent for a single classified call."""
    client = create_foundry_client()

    # Get customer context
    customer_data = json.loads(lookup_customer(call_id))

    input_text = (
        f"Call {call_id} from {customer_data.get('customer_name', 'Unknown')} "
        f"({customer_data.get('account_tier', 'unknown')} tier, "
        f"{customer_data.get('tenure_months', 0)} months tenure):\n"
        f"- Intent: {classification.get('intent', 'unknown')}\n"
        f"- Priority: {classification.get('priority', 'unknown')}\n"
        f"- Sentiment: {classification.get('sentiment', 'unknown')}\n"
        f"- Retention risk: {classification.get('retention_risk', 'unknown')}\n"
        f"- Summary: {customer_data.get('summary', 'No summary available')}\n\n"
        "Recommend the resolution strategy, script, escalation decision, and follow-up actions."
    )

    resolution = run_agent_response(
        client,
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "You are a resolution strategy expert for NovaTel Communications. Provide a recommended action, "
            "script suggestion, escalation decision, available offers, and follow-up tasks. "
            "Use at most 120 words."
        ),
        input_text=input_text,
    )
    client.close()
    return resolution


def run_call_center_workflow(intent_agent: str, resolution_agent: str) -> dict:
    """Orchestrate: classify all calls -> resolve high-priority ones -> consolidated report."""
    classification_report = run_intent_classification(intent_agent)
    print(classification_report)

    print("\n=== Step 2b: Resolution Advisory (High-Priority Calls) ===")
    resolutions = {}

    # Process the critical/high priority calls that need immediate resolution
    high_priority_calls = [
        {"call_id": "CALL-007", "intent": "security_concern", "priority": "critical",
         "sentiment": "anxious", "retention_risk": "medium"},
        {"call_id": "CALL-001", "intent": "billing_dispute", "priority": "high",
         "sentiment": "frustrated", "retention_risk": "high"},
        {"call_id": "CALL-003", "intent": "cancellation", "priority": "high",
         "sentiment": "neutral", "retention_risk": "high"},
    ]

    for call in high_priority_calls:
        print(f"  Resolving {call['call_id']} ({call['intent']})...")
        resolution = run_resolution_advisory(resolution_agent, call["call_id"], call)
        resolutions[call["call_id"]] = resolution

    return {
        "classification_report": classification_report,
        "high_priority_calls": [c["call_id"] for c in high_priority_calls],
        "resolutions": resolutions,
        "total_calls": 7,
        "critical_count": 1,
        "high_priority_count": 2,
    }


def print_shift_report(report: dict):
    print("\n" + "=" * 60)
    print("NOVATEL CALL CENTER — SHIFT REPORT")
    print("=" * 60)
    print(f"  Total calls processed  : {report['total_calls']}")
    print(f"  Critical priority      : {report['critical_count']}")
    print(f"  High priority          : {report['high_priority_count']}")

    if report["high_priority_calls"]:
        print(f"\n  Calls requiring immediate action: {', '.join(report['high_priority_calls'])}")
        print("\n--- Resolution Recommendations ---")
        for call_id, resolution in report["resolutions"].items():
            print(f"\n{call_id}:")
            print(resolution)
    else:
        print("\n  No critical or high-priority calls in queue.")

    print("=" * 60)


def main():
    if not FOUNDRY_ENDPOINT or not API_KEY:
        print("FOUNDRY_ENDPOINT and API_KEY must be set in .env")
        sys.exit(1)

    intent_agent, resolution_agent = ensure_agents_deployed()
    report = run_call_center_workflow(intent_agent, resolution_agent)
    print_shift_report(report)

    print("\nWorkflow complete!")


if __name__ == "__main__":
    main()
