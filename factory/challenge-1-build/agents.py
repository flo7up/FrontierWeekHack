"""
Challenge 1: Build Agents — SDK Track
Anomaly Detection Agent and Fault Diagnosis Agent for TireForge Industries.

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
SENSOR_DATA_PATH = Path(__file__).resolve().parent / "sensor_data.json"


def _load_sensor_batch() -> list[dict]:
    """Load machine data to send as a batch payload in demo requests."""
    with open(SENSOR_DATA_PATH, "r") as f:
        data = json.load(f)
    return data.get("machines", [])


# =============================================================================
# Tool Function: check_thresholds
# This is already implemented — agents can call this to get threshold analysis
# =============================================================================

def check_thresholds(machine_id: str) -> str:
    """
    Reads sensor_data.json and checks if a machine's readings are within thresholds.
    Returns a JSON string with the analysis.
    """
    with open(SENSOR_DATA_PATH, "r") as f:
        data = json.load(f)

    machine = None
    for m in data["machines"]:
        if m["machine_id"] == machine_id or m["name"] == machine_id:
            machine = m
            break

    if not machine:
        return json.dumps({"error": f"Machine '{machine_id}' not found"})

    results = {
        "machine_id": machine["machine_id"],
        "name": machine["name"],
        "status": machine["status"],
        "last_maintenance": machine["last_maintenance"],
        "anomalies": [],
        "all_readings": {},
    }

    for sensor, reading in machine["readings"].items():
        value = reading["value"]
        threshold = machine["thresholds"][sensor]
        in_spec = threshold["min"] <= value <= threshold["max"]

        results["all_readings"][sensor] = {
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

            results["anomalies"].append({
                "sensor": sensor,
                "value": value,
                "unit": reading["unit"],
                "threshold_min": threshold["min"],
                "threshold_max": threshold["max"],
                "deviation": deviation,
            })

    return json.dumps(results, indent=2)


# Tool definition for the OpenAI Responses API
CHECK_THRESHOLDS_TOOL = {
    "type": "function",
    "name": "check_thresholds",
    "description": "Check if a machine's sensor readings are within normal operating thresholds. Returns anomalies if any readings are out of spec.",
    "parameters": {
        "type": "object",
        "properties": {
            "machine_id": {
                "type": "string",
                "description": "The machine ID (e.g., 'MX-001') or name (e.g., 'mixer') to check",
            }
        },
        "required": ["machine_id"],
        "additionalProperties": False,
    },
    "strict": False,
}


# =============================================================================
# Anomaly Detection Agent
# =============================================================================

class AnomalyDetectionAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.instructions = ""

    def create(self):
        """Configure the anomaly detection agent for API-key calls."""
        self.client = create_foundry_client()

        self.instructions = """
        You are an industrial sensor anomaly detection expert for TireForge Industries.
        When asked to check machines, use the check_thresholds tool for each machine.
        For each machine, report:
        - Machine name and ID
        - Status (normal / warning / critical)
        - Each sensor reading that is out of spec: current value, threshold violated, deviation
        Use ⚠️ for warning and 🔴 for critical anomalies.
        If all readings are in spec, mark the machine as normal.
        Be concise and structured.
        """

        self.agent = ApiKeyAgent(name="anomaly-detection-agent")

        return self.agent

    def run(self, input_text: str) -> str:
        """Run the anomaly detection agent with the given input."""
        return run_agent_response(
            self.client,
            model=MODEL_DEPLOYMENT_NAME,
            instructions=self.instructions,
            input_text=input_text,
            tools=[CHECK_THRESHOLDS_TOOL],
            tool_handlers={"check_thresholds": check_thresholds},
        )

    def cleanup(self):
        """Close the API client."""
        if self.client:
            self.client.close()


# =============================================================================
# Fault Diagnosis Agent
# =============================================================================

class FaultDiagnosisAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.instructions = ""

    def create(self):
        """Configure the fault diagnosis agent for API-key calls."""
        self.client = create_foundry_client()

        self.instructions = """
        You are a mechanical fault diagnosis expert for TireForge Industries.
        Given a list of sensor anomalies from a machine, your job is to:
        1. Identify the most likely root cause based on the pattern of anomalies:
           - High temperature + high pressure → likely blockage or restricted flow
           - High vibration alone → likely bearing wear, misalignment, or imbalance
           - High temperature + high vibration → likely bearing failure or lubrication issue
           - Multiple sensors critical → compound failure, escalate immediately
        2. Recommend specific, actionable maintenance steps.
        3. Estimate urgency: IMMEDIATE (stop now), WITHIN 24H, or MONITOR.
        Be concise. Format your response as:
        LIKELY CAUSE: ...
        MAINTENANCE ACTIONS: ...
        URGENCY: ...
        """

        self.agent = ApiKeyAgent(name="fault-diagnosis-agent")

        return self.agent

    def run(self, input_text: str) -> str:
        """Run the fault diagnosis agent with the given input."""
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

    print("=== Anomaly Detection Agent ===")
    print("Configuring agent...")

    anomaly_agent = AnomalyDetectionAgent()
    anomaly_agent.create()
    print(f"✅ Configured: {anomaly_agent.agent.name} (API key)")

    print("\nAnalyzing all machines...")
    machine_batch = _load_sensor_batch()
    machine_ids = [machine["machine_id"] for machine in machine_batch]
    anomaly_result = anomaly_agent.run(
        "You are receiving a batch payload of machines that must be processed in one run. "
        "Use check_thresholds for each machine_id in the payload and return the anomaly summary.\n\n"
        f"BATCH_MACHINE_IDS: {json.dumps(machine_ids)}\n"
        "BATCH_MACHINE_DATA:\n"
        f"{json.dumps(machine_batch, indent=2)}"
    )
    print(anomaly_result)

    print("\n=== Fault Diagnosis Agent ===")
    print("Configuring agent...")

    diagnosis_agent = FaultDiagnosisAgent()
    diagnosis_agent.create()
    print(f"✅ Configured: {diagnosis_agent.agent.name} (API key)")

    print("\nDiagnosing critical machine: curing_press...")
    critical_batch = [machine for machine in machine_batch if machine["status"] in {"critical", "warning"}]
    diagnosis_result = diagnosis_agent.run(
        "Diagnose the following critical-machine batch and provide root cause, "
        "maintenance actions, and urgency for each entry.\n\n"
        "CRITICAL_MACHINE_BATCH:\n"
        f"{json.dumps(critical_batch, indent=2)}"
    )
    print(diagnosis_result)

    anomaly_agent.cleanup()
    diagnosis_agent.cleanup()


if __name__ == "__main__":
    main()
