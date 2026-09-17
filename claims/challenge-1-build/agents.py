"""
Challenge 1: Build Agents — Insurance Claims Processing
Claims Triage Agent and Claims Decision Agent for ClaimSight Insurance.

Usage:
    python agents.py

Builds both agents with system prompts, tools, and conversation handling.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


# Resolve repo root by finding .env in parent directories.
def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".env").exists():
            return parent
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _find_repo_root()
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from foundry_api import ApiKeyAgent, create_foundry_client, run_agent_response

# Load environment
env_path = REPO_ROOT / ".env"
load_dotenv(env_path, override=True)

FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT")
API_KEY = os.getenv("API_KEY")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
CLAIMS_DATA_PATH = Path(__file__).resolve().parent / "claims_data.json"


def _load_claim_batch() -> list[dict]:
    """Load claim records to send as a batch payload in demo requests."""
    with open(CLAIMS_DATA_PATH, "r") as f:
        data = json.load(f)
    return data.get("claims", [])


# =============================================================================
# Tool Function: assess_claim
# This is already implemented — agents can call this to get claim risk analysis
# =============================================================================

def assess_claim(claim_id: str) -> str:
    """
    Reads claims_data.json and checks if a claim's metrics are within acceptable thresholds.
    Returns a JSON string with the analysis.
    """
    with open(CLAIMS_DATA_PATH, "r") as f:
        data = json.load(f)

    claim = None
    for c in data["claims"]:
        if c["claim_id"] == claim_id:
            claim = c
            break

    if not claim:
        return json.dumps({"error": f"Claim '{claim_id}' not found"})

    results = {
        "claim_id": claim["claim_id"],
        "type": claim["type"],
        "claimant": claim["claimant"],
        "date_filed": claim["date_filed"],
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
            "value": value,
            "unit": reading["unit"],
            "min": threshold["min"],
            "max": threshold["max"],
            "in_spec": in_spec,
        }

        if not in_spec:
            deviation = ""
            if value > threshold["max"]:
                pct = ((value - threshold["max"]) / threshold["max"]) * 100
                deviation = f"{pct:.1f}% above max"
            elif value < threshold["min"]:
                pct = ((threshold["min"] - value) / threshold["min"]) * 100
                deviation = f"{pct:.1f}% below min"

            results["flags"].append({
                "metric": metric,
                "value": value,
                "unit": reading["unit"],
                "threshold_min": threshold["min"],
                "threshold_max": threshold["max"],
                "deviation": deviation,
            })

    return json.dumps(results, indent=2)


# Tool definition for the OpenAI Responses API
ASSESS_CLAIM_TOOL = {
    "type": "function",
    "name": "assess_claim",
    "description": "Assess an insurance claim's metrics against acceptable thresholds. Returns flags if any metrics are outside acceptable ranges (completeness too low, fraud risk too high, etc.).",
    "parameters": {
        "type": "object",
        "properties": {
            "claim_id": {
                "type": "string",
                "description": "The claim ID (e.g., 'CLM-001') to assess",
            }
        },
        "required": ["claim_id"],
        "additionalProperties": False,
    },
    "strict": False,
}


# =============================================================================
# Claims Triage Agent
# =============================================================================

class ClaimsTriageAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.instructions = ""

    def create(self):
        """Configure the claims triage agent for API-key calls."""
        self.client = create_foundry_client()

        self.instructions = """
        You are an insurance claims triage specialist for ClaimSight Insurance.
        When asked to assess claims, use the assess_claim tool for each claim.
        For each claim, report:
        - Claim ID, type, and claimant name
        - Risk classification (normal / warning / critical)
        - Each metric that is flagged: current value, threshold violated, deviation
        - Missing documents if completeness is below threshold
        Use ⚠️ for warning and 🔴 for critical flags.
        If all metrics are within acceptable ranges, mark the claim as normal (✅).
        Be concise and structured.
        """

        self.agent = ApiKeyAgent(name="claims-triage-agent")

        return self.agent

    def run(self, input_text: str) -> str:
        """Run the claims triage agent with the given input."""
        return run_agent_response(
            self.client,
            model=MODEL_DEPLOYMENT_NAME,
            instructions=self.instructions,
            input_text=input_text,
            tools=[ASSESS_CLAIM_TOOL],
            tool_handlers={"assess_claim": assess_claim},
        )

    def cleanup(self):
        """Close the API client."""
        if self.client:
            self.client.close()


# =============================================================================
# Claims Decision Agent
# =============================================================================

class ClaimsDecisionAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.instructions = ""

    def create(self):
        """Configure the claims decision agent for API-key calls."""
        self.client = create_foundry_client()

        self.instructions = """
        You are a senior claims adjuster and decision specialist for ClaimSight Insurance.
        Given a list of flags from a claim assessment, your job is to:
        1. Determine the recommended action based on the pattern of flags:
           - High fraud risk score alone → Investigate for potential fraud
           - Low completeness alone → Request missing documents before proceeding
           - High fraud risk + low damage-estimate match → Likely inflated claim, escalate to SIU
           - Low policy coverage match → Partial denial, cover only matched items
           - Multiple critical flags → Compound risk, full investigation required
        2. Recommend specific, actionable next steps for the claims adjuster.
        3. Estimate urgency: IMMEDIATE (potential fraud), WITHIN 48H (missing docs), or STANDARD (routine).
        Be concise. Format your response as:
        RECOMMENDED ACTION: APPROVE / REQUEST DOCUMENTS / INVESTIGATE / DENY
        REASONING: ...
        NEXT STEPS: ...
        URGENCY: ...
        """

        self.agent = ApiKeyAgent(name="claims-decision-agent")

        return self.agent

    def run(self, input_text: str) -> str:
        """Run the claims decision agent with the given input."""
        return run_agent_response(
            self.client,
            model=MODEL_DEPLOYMENT_NAME,
            instructions=self.instructions,
            input_text=input_text,
        )

    def cleanup(self):
        """Close the API client."""
        if self.client:
            self.client.close()


# =============================================================================
# Main — Test both agents
# =============================================================================

def main():
    if not FOUNDRY_ENDPOINT or not API_KEY:
        print("❌ FOUNDRY_ENDPOINT and API_KEY must be set in .env")
        sys.exit(1)

    print("=== Claims Triage Agent ===")
    print("Configuring agent...")

    triage_agent = ClaimsTriageAgent()
    triage_agent.create()
    print(f"✅ Configured: {triage_agent.agent.name} (API key)")

    print("\nAssessing all claims...")
    claim_batch = _load_claim_batch()
    claim_ids = [claim["claim_id"] for claim in claim_batch]
    triage_result = triage_agent.run(
        "You are receiving a batch payload of claims that must be assessed in one run. "
        "Use assess_claim for each claim_id in the payload and summarize all flags.\n\n"
        f"BATCH_CLAIM_IDS: {json.dumps(claim_ids)}\n"
        "BATCH_CLAIM_DATA:\n"
        f"{json.dumps(claim_batch, indent=2)}"
    )
    print(triage_result)

    print("\n=== Claims Decision Agent ===")
    print("Configuring agent...")

    decision_agent = ClaimsDecisionAgent()
    decision_agent.create()
    print(f"✅ Configured: {decision_agent.agent.name} (API key)")

    print("\nDeciding on high-risk claim batch...")
    high_risk_batch = [claim for claim in claim_batch if claim["status"] in {"critical", "warning"}]
    decision_result = decision_agent.run(
        "You are receiving a batch payload of high-risk claims. For each claim, provide: "
        "recommended action, reasoning, next steps, and urgency.\n\n"
        "HIGH_RISK_CLAIM_BATCH:\n"
        f"{json.dumps(high_risk_batch, indent=2)}"
    )
    print(decision_result)

    triage_agent.cleanup()
    decision_agent.cleanup()


if __name__ == "__main__":
    main()
