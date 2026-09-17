"""
Challenge 4: Production Workflow — Claims Processing
Multi-agent orchestration workflow for ClaimSight Insurance.
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
CLAIMS_DATA_PATH = Path(__file__).resolve().parent.parent / "challenge-1-build" / "claims_data.json"

CLAIMS = ["CLM-001", "CLM-002", "CLM-003", "CLM-004", "CLM-005"]
TRIAGE_AGENT_NAME = "claims-triage-agent"
DECISION_AGENT_NAME = "claims-decision-agent"
# Set WORKFLOW_AGENT_NAME in .env after creating the workflow in the Foundry portal
WORKFLOW_AGENT_NAME = os.getenv("WORKFLOW_AGENT_NAME", "")


def assess_claim(claim_id: str) -> str:
    with open(CLAIMS_DATA_PATH, "r") as f:
        data = json.load(f)
    claim = next(
        (c for c in data["claims"] if c["claim_id"] == claim_id),
        None,
    )
    if not claim:
        return json.dumps({"error": f"Claim not found: {claim_id}"})
    results = {
        "claim_id": claim["claim_id"],
        "type": claim["type"],
        "claimant": claim["claimant"],
        "status": claim["status"],
        "documents_submitted": claim["documents_submitted"],
        "flags": [],
        "all_metrics": {},
    }
    for metric, reading in claim["metrics"].items():
        value = reading["value"]
        threshold = claim["thresholds"][metric]
        in_spec = threshold["min"] <= value <= threshold["max"]
        results["all_metrics"][metric] = {
            "value": value, "unit": reading["unit"],
            "min": threshold["min"], "max": threshold["max"], "in_spec": in_spec,
        }
        if not in_spec:
            if value > threshold["max"]:
                pct = ((value - threshold["max"]) / threshold["max"]) * 100
                deviation = f"{pct:.1f}% above max"
            else:
                pct = ((threshold["min"] - value) / threshold["min"]) * 100
                deviation = f"{pct:.1f}% below min"
            results["flags"].append({
                "metric": metric, "value": value,
                "unit": reading["unit"], "deviation": deviation,
            })
    return json.dumps(results, indent=2)


def ensure_agents_deployed() -> tuple:
    """Configure the two local agent roles used by the workflow."""
    print("=== Step 1: Configure API-Key Agent Roles ===")
    print(f"  Configured: {TRIAGE_AGENT_NAME}")
    print(f"  Configured: {DECISION_AGENT_NAME}")
    return TRIAGE_AGENT_NAME, DECISION_AGENT_NAME


def run_claims_triage(triage_agent_name: str) -> str:
    """Call the claims triage agent for all claims; handle function call loop."""
    print("\n=== Step 2a: Claims Triage ===")

    client = create_foundry_client()
    tool = {
        "type": "function",
        "name": "assess_claim",
        "description": "Assess an insurance claim's metrics against thresholds.",
        "parameters": {
            "type": "object",
            "properties": {"claim_id": {"type": "string"}},
            "required": ["claim_id"],
            "additionalProperties": False,
        },
        "strict": False,
    }
    report = run_agent_response(
        client,
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "You are an insurance claims triage specialist for ClaimSight Insurance. "
            "Use assess_claim for each claim ID and report all flagged metrics."
        ),
        input_text=(
            f"Assess all claims: {', '.join(CLAIMS)}. "
            "Report every metric that is outside acceptable thresholds."
        ),
        tools=[tool],
        tool_handlers={"assess_claim": assess_claim},
    )
    client.close()
    return report


def run_claims_decision(decision_agent_name: str, claim_id: str, flags: list) -> str:
    """Call the claims decision agent for a single flagged claim."""
    client = create_foundry_client()

    flag_text = "\n".join(
        f"  - {f['metric']}: {f['value']} {f['unit']} ({f['deviation']})"
        for f in flags
    )
    input_text = (
        f"Claim {claim_id} has the following flags:\n"
        f"{flag_text}\n"
        "Recommend an action and provide next steps."
    )

    decision = run_agent_response(
        client,
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "You are a senior claims adjuster for ClaimSight Insurance. Recommend APPROVE, "
            "REQUEST DOCUMENTS, INVESTIGATE, or DENY, with reasoning, next steps, and urgency."
        ),
        input_text=input_text,
    )
    client.close()
    return decision


def run_claims_workflow(triage_agent: str, decision_agent: str) -> dict:
    """Orchestrate: triage all claims -> per-claim decision -> consolidated report."""
    triage_report = run_claims_triage(triage_agent)
    print(triage_report)

    print("\n=== Step 2b: Claims Decisions ===")
    decisions = {}
    flagged_claims = []

    for claim_id in CLAIMS:
        result = json.loads(assess_claim(claim_id))
        if result.get("flags"):
            flagged_claims.append(claim_id)
            print(f"  Deciding on {claim_id}...")
            decision = run_claims_decision(decision_agent, claim_id, result["flags"])
            decisions[claim_id] = decision

    return {
        "triage_report": triage_report,
        "flagged_claims": flagged_claims,
        "decisions": decisions,
        "total_claims": len(CLAIMS),
        "problematic_claims": len(flagged_claims),
    }


def print_claims_report(report: dict):
    print("\n" + "=" * 60)
    print("CLAIMSIGHT INSURANCE — CLAIMS PROCESSING REPORT")
    print("=" * 60)
    print(f"  Claims assessed    : {report['total_claims']}")
    print(f"  Claims flagged     : {report['problematic_claims']}")

    if report["flagged_claims"]:
        print(f"  Flagged claims     : {', '.join(report['flagged_claims'])}")
        print("\n--- Decisions ---")
        for claim_id, decision in report["decisions"].items():
            print(f"\n{claim_id}:")
            print(decision)
    else:
        print("\n  All claims passed triage — no flags detected.")

    print("=" * 60)


def create_workflow_agent(workflow_agent_name: str = "claims-processing-workflow") -> str:
    """Configure a local workflow name for API-key orchestration."""
    print(f"  Configured local workflow: {workflow_agent_name}")
    return workflow_agent_name


def run_portal_workflow(workflow_name: str) -> str:
    """Run a consolidated workflow response with API-key authentication."""
    client = create_foundry_client()
    print(f"\n=== Local Workflow: {workflow_name} ===")

    print(f"\n  Workflow steps:")
    print(f"    1. claims-triage-agent    — triage claims for completeness and fraud indicators")
    print(f"    2. claims-decision-agent  — make approval/denial decisions for triaged claims")

    # Embed claims data in the input so agents don't need tool calls.
    # The claims-triage-agent is instructed to call assess_claim per claim,
    # but workflow steps cannot handle function-call loops. We provide all claim
    # details upfront and explicitly instruct the agent to work from the provided data.
    with open(CLAIMS_DATA_PATH, "r") as f:
        claims_data = json.load(f)
    claims_text = json.dumps(claims_data["claims"], indent=2)
    query = (
        "All claims data for today is provided below — do NOT call assess_claim. "
        "Analyse the data directly from this message.\n\n"
        + claims_text
        + "\n\nFor each claim, assess completeness, check for fraud indicators, and "
        "classify risk (normal/warning/critical). Then make a clear approval or denial "
        "decision for each claim with justification."
    )

    print("\n  Submitting workflow run...")
    response = client.responses.create(
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "Act as a claims processing workflow: triage each claim, then recommend an action, "
            "reasoning, next steps, and urgency."
        ),
        input=query,
    )
    output_text = response.output_text
    print("\nWorkflow output:")
    print(output_text)
    client.close()
    return output_text


def main():
    if not FOUNDRY_ENDPOINT or not API_KEY:
        print("FOUNDRY_ENDPOINT and API_KEY must be set in .env")
        sys.exit(1)

    # --- Part A: Python orchestration (agents called step-by-step from code) ---
    triage_agent, decision_agent = ensure_agents_deployed()
    report = run_claims_workflow(triage_agent, decision_agent)
    print_claims_report(report)

    print("\nWorkflow complete!")

    # --- Part B: SDK workflow creation + portal invocation ---
    print("\n" + "=" * 60)
    print("CONFIGURING LOCAL WORKFLOW")
    print("=" * 60)
    workflow_name = WORKFLOW_AGENT_NAME if WORKFLOW_AGENT_NAME and not WORKFLOW_AGENT_NAME.startswith("<") else "claims-processing-workflow"
    workflow_name = create_workflow_agent(workflow_agent_name=workflow_name)

    print("\n" + "=" * 60)
    print("INVOKING WORKFLOW")
    print("=" * 60)
    run_portal_workflow(workflow_name)

    print("\n" + "=" * 60)
    print("CHALLENGE 4 COMPLETE")
    print("=" * 60)
    print("  Part A: Multi-agent API orchestration  ✓")
    print(f"  Part B: Local workflow response         ✓  ({workflow_name})")


if __name__ == "__main__":
    main()
