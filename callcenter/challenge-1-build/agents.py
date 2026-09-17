"""
Challenge 1: Build Agents — SDK Track
Intent Classification Agent and Resolution Advisor Agent for NovaTel Communications.

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
CALL_DATA_PATH = Path(__file__).resolve().parent / "call_data.json"


def _load_call_batch() -> list[dict]:
    """Load call records to send as a batch payload in demo requests."""
    with open(CALL_DATA_PATH, "r") as f:
        data = json.load(f)
    return data.get("calls", [])


# =============================================================================
# Tool Function: lookup_customer
# This is already implemented — agents can call this to get customer context
# =============================================================================

def lookup_customer(call_id: str) -> str:
    """
    Reads call_data.json and returns full context for a given call:
    customer info, account details, call summary, and history.
    """
    with open(CALL_DATA_PATH, "r") as f:
        data = json.load(f)

    call = None
    for c in data["calls"]:
        if c["call_id"] == call_id or c["customer_id"] == call_id:
            call = c
            break

    if not call:
        return json.dumps({"error": f"Call or customer '{call_id}' not found"})

    return json.dumps({
        "call_id": call["call_id"],
        "customer_id": call["customer_id"],
        "customer_name": call["customer_name"],
        "account_tier": call["account_tier"],
        "tenure_months": call["tenure_months"],
        "summary": call["summary"],
        "transcript_snippet": call["transcript_snippet"],
        "open_tickets": call["open_tickets"],
        "last_interaction": call["last_interaction"],
        "status": call["status"],
    }, indent=2)


# Tool definition for the OpenAI Responses API
LOOKUP_CUSTOMER_TOOL = {
    "type": "function",
    "name": "lookup_customer",
    "description": "Look up customer and call details by call ID (e.g., 'CALL-001') or customer ID (e.g., 'CUST-4421'). Returns account tier, tenure, call summary, transcript, and interaction history.",
    "parameters": {
        "type": "object",
        "properties": {
            "call_id": {
                "type": "string",
                "description": "The call ID (e.g., 'CALL-001') or customer ID (e.g., 'CUST-4421') to look up",
            }
        },
        "required": ["call_id"],
        "additionalProperties": False,
    },
    "strict": False,
}


# =============================================================================
# Intent Classification Agent
# =============================================================================

class IntentClassificationAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.instructions = ""

    def create(self):
        """Configure the intent classification agent for API-key calls."""
        self.client = create_foundry_client()

        self.instructions = """
        You are a call center intent classification specialist for NovaTel Communications.
        When asked to classify calls, use the lookup_customer tool to retrieve call details.
        For each call, determine:
        1. PRIMARY INTENT — one of:
           - billing_dispute: Unauthorized charges, refund requests, billing errors
           - technical_issue: Service outages, connectivity problems, device malfunctions
           - cancellation: Customer wants to cancel or is threatening to leave
           - upsell_opportunity: Customer wants to add services, upgrade, or expand
           - account_support: General questions, app help, navigation issues
           - security_concern: Fraud, unauthorized access, suspicious activity
        2. PRIORITY — critical / high / medium / low
        3. SENTIMENT — frustrated / neutral / positive / anxious
        4. RETENTION RISK — high / medium / low (likelihood customer will churn)

        Format your response as a structured classification for each call.
        Use 🔴 for critical, ⚠️ for high, and ✅ for low-risk items.
        """

        self.agent = ApiKeyAgent(name="intent-classification-agent")

        return self.agent

    def run(self, input_text: str) -> str:
        """Run the intent classification agent with the given input."""
        return run_agent_response(
            self.client,
            model=MODEL_DEPLOYMENT_NAME,
            instructions=self.instructions,
            input_text=input_text,
            tools=[LOOKUP_CUSTOMER_TOOL],
            tool_handlers={"lookup_customer": lookup_customer},
        )

    def cleanup(self):
        """Close the API client."""
        if self.client:
            self.client.close()


# =============================================================================
# Resolution Advisor Agent
# =============================================================================

class ResolutionAdvisorAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.instructions = ""

    def create(self):
        """Configure the resolution advisor agent for API-key calls."""
        self.client = create_foundry_client()

        self.instructions = """
        You are a resolution strategy expert for NovaTel Communications call center.
        Given a classified call intent and customer context, recommend the optimal resolution path.

        Your recommendations must consider:
        - Account tier (premium/business get priority handling and more flexibility)
        - Customer tenure (long-term customers get retention offers)
        - Open tickets (existing issues indicate repeat contact — escalate)
        - Sentiment and retention risk

        For each call, provide:
        1. RECOMMENDED ACTION — specific steps for the agent to take
        2. SCRIPT SUGGESTION — what to say to the customer (1-2 sentences)
        3. ESCALATION — Yes/No and reason
        4. OFFERS AVAILABLE — any credits, discounts, or retention offers to extend
        5. FOLLOW-UP — any post-call tasks (ticket creation, callback scheduling, etc.)

        Resolution guidelines by intent:
        - billing_dispute: Verify charge, offer immediate credit if under $100, escalate if over
        - technical_issue: Check known outages first, dispatch technician if persistent
        - cancellation: Offer retention package (discount/free month), escalate if business account
        - upsell_opportunity: Calculate savings, offer bundle discount, schedule follow-up
        - account_support: Walk through solution, offer callback if complex
        - security_concern: ALWAYS escalate to security team, lock account immediately

        Be concise and actionable. Format clearly with headers.
        """

        self.agent = ApiKeyAgent(name="resolution-advisor-agent")

        return self.agent

    def run(self, input_text: str) -> str:
        """Run the resolution advisor agent with the given input."""
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

    print("=== Intent Classification Agent ===")
    print("Configuring agent...")

    intent_agent = IntentClassificationAgent()
    intent_agent.create()
    print(f"✅ Configured: {intent_agent.agent.name} (API key)")

    print("\nClassifying all incoming calls...")
    call_batch = _load_call_batch()
    call_ids = [call["call_id"] for call in call_batch]
    intent_result = intent_agent.run(
        "You are receiving a batch payload of calls for classification in one run. "
        "Use lookup_customer for each call_id in the payload, then provide the classification output.\n\n"
        f"BATCH_CALL_IDS: {json.dumps(call_ids)}\n"
        "BATCH_CALL_DATA:\n"
        f"{json.dumps(call_batch, indent=2)}"
    )
    print(intent_result)

    print("\n=== Resolution Advisor Agent ===")
    print("Configuring agent...")

    resolution_agent = ResolutionAdvisorAgent()
    resolution_agent.create()
    print(f"✅ Configured: {resolution_agent.agent.name} (API key)")

    print("\nAdvising on high-priority batch of calls...")
    high_priority_batch = [
        call for call in call_batch if call["call_id"] in {"CALL-001", "CALL-006", "CALL-007"}
    ]
    resolution_result = resolution_agent.run(
        "You are receiving a batch payload of high-priority calls. For each call, provide: "
        "recommended action, script suggestion, escalation decision, available offers, and follow-up steps.\n\n"
        "HIGH_PRIORITY_CALL_BATCH:\n"
        f"{json.dumps(high_priority_batch, indent=2)}"
    )
    print(resolution_result)

    intent_agent.cleanup()
    resolution_agent.cleanup()


if __name__ == "__main__":
    main()
