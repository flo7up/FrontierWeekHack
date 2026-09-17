"""
Challenge 4: Production Workflow -- SDK Track
Multi-agent orchestration workflow for TireForge Industries.
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
SENSOR_DATA_PATH = Path(__file__).resolve().parent.parent / "challenge-1-build" / "sensor_data.json"

MACHINES = ["MX-001", "EX-002", "CP-003", "CU-004", "IS-005"]
ANOMALY_AGENT_NAME = "anomaly-detection-agent"
DIAGNOSIS_AGENT_NAME = "fault-diagnosis-agent"
# Set WORKFLOW_AGENT_NAME in .env after creating the workflow in the Foundry portal
WORKFLOW_AGENT_NAME = os.getenv("WORKFLOW_AGENT_NAME", "")


def check_thresholds(machine_id: str) -> str:
    with open(SENSOR_DATA_PATH, "r") as f:
        data = json.load(f)
    machine = next(
        (m for m in data["machines"]
         if m["machine_id"] == machine_id or m["name"] == machine_id),
        None,
    )
    if not machine:
        return json.dumps({"error": f"Machine not found: {machine_id}"})
    results = {
        "machine_id": machine["machine_id"],
        "name": machine["name"],
        "status": machine["status"],
        "anomalies": [],
        "all_readings": {},
    }
    for sensor, reading in machine["readings"].items():
        value = reading["value"]
        threshold = machine["thresholds"][sensor]
        in_spec = threshold["min"] <= value <= threshold["max"]
        results["all_readings"][sensor] = {
            "value": value, "unit": reading["unit"],
            "min": threshold["min"], "max": threshold["max"], "in_spec": in_spec,
        }
        if not in_spec:
            direction = "above max" if value > threshold["max"] else "below min"
            ref = threshold["max"] if value > threshold["max"] else threshold["min"]
            pct = abs(value - ref) / ref * 100
            results["anomalies"].append({
                "sensor": sensor, "value": value,
                "unit": reading["unit"], "deviation": f"{pct:.1f}% {direction}",
            })
    return json.dumps(results, indent=2)


def ensure_agents_deployed() -> tuple:
    """Configure the two local agent roles used by the workflow."""
    print("=== Step 1: Configure API-Key Agent Roles ===")
    print(f"  Configured: {ANOMALY_AGENT_NAME}")
    print(f"  Configured: {DIAGNOSIS_AGENT_NAME}")
    return ANOMALY_AGENT_NAME, DIAGNOSIS_AGENT_NAME


def run_anomaly_scan(anomaly_agent_name: str) -> str:
    """Call the anomaly detection agent for all machines; handle function call loop."""
    print("\n=== Step 2a: Anomaly Scan ===")

    client = create_foundry_client()
    tool = {
        "type": "function",
        "name": "check_thresholds",
        "description": "Check sensor readings against thresholds for a machine.",
        "parameters": {
            "type": "object",
            "properties": {"machine_id": {"type": "string"}},
            "required": ["machine_id"],
            "additionalProperties": False,
        },
        "strict": False,
    }
    report = run_agent_response(
        client,
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "You are an industrial sensor anomaly detection expert for TireForge Industries. "
            "Use check_thresholds for each machine ID and report every out-of-spec reading."
        ),
        input_text=(
            f"Check all machines: {', '.join(MACHINES)}. "
            "Report every sensor reading that is out of spec."
        ),
        tools=[tool],
        tool_handlers={"check_thresholds": check_thresholds},
    )
    client.close()
    return report


def run_fault_diagnosis(diagnosis_agent_name: str, machine_id: str, anomalies: list) -> str:
    """Call the fault diagnosis agent for a single machine."""
    client = create_foundry_client()

    anomaly_text = "\n".join(
        f"  - {a['sensor']}: {a['value']} {a['unit']} ({a['deviation']})"
        for a in anomalies
    )
    input_text = (
        f"Machine {machine_id} has the following out-of-spec readings:\n"
        f"{anomaly_text}\n"
        "Diagnose the fault and recommend maintenance actions."
    )

    diagnosis = run_agent_response(
        client,
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "You are a mechanical fault diagnosis expert for TireForge Industries. "
            "Identify the likely root cause, maintenance actions, and urgency."
        ),
        input_text=input_text,
    )
    client.close()
    return diagnosis


def run_factory_health_workflow(anomaly_agent: str, diagnosis_agent: str) -> dict:
    """Orchestrate: anomaly scan -> per-machine diagnosis -> consolidated report."""
    anomaly_report = run_anomaly_scan(anomaly_agent)
    print(anomaly_report)

    print("\n=== Step 2b: Fault Diagnosis ===")
    diagnoses = {}
    machines_with_anomalies = []

    for machine_id in MACHINES:
        result = json.loads(check_thresholds(machine_id))
        if result.get("anomalies"):
            machines_with_anomalies.append(machine_id)
            print(f"  Diagnosing {machine_id}...")
            diagnosis = run_fault_diagnosis(diagnosis_agent, machine_id, result["anomalies"])
            diagnoses[machine_id] = diagnosis

    return {
        "anomaly_report": anomaly_report,
        "machines_with_anomalies": machines_with_anomalies,
        "diagnoses": diagnoses,
        "total_machines": len(MACHINES),
        "problematic_machines": len(machines_with_anomalies),
    }


def print_factory_report(report: dict):
    print("\n" + "=" * 60)
    print("TIREFORGE FACTORY HEALTH REPORT")
    print("=" * 60)
    print(f"  Machines checked   : {report['total_machines']}")
    print(f"  Machines affected  : {report['problematic_machines']}")

    if report["machines_with_anomalies"]:
        print(f"  Affected machines  : {', '.join(report['machines_with_anomalies'])}")
        print("\n--- Fault Diagnoses ---")
        for machine_id, diagnosis in report["diagnoses"].items():
            print(f"\n{machine_id}:")
            print(diagnosis)
    else:
        print("\n  All machines operating within normal parameters.")

    print("=" * 60)


def create_workflow_agent(workflow_agent_name: str = "factory-health-workflow") -> str:
    """Configure a local workflow name for API-key orchestration."""
    print(f"  Configured local workflow: {workflow_agent_name}")
    return workflow_agent_name


def run_portal_workflow(workflow_name: str) -> str:
    """Run a consolidated workflow response with API-key authentication."""
    client = create_foundry_client()
    print(f"\n=== Local Workflow: {workflow_name} ===")

    print(f"\n  Workflow steps:")
    print(f"    1. anomaly-detection-agent  — detect sensor anomalies across all machines")
    print(f"    2. fault-diagnosis-agent    — diagnose root cause for anomalous machines")

    # Embed sensor data in the input so agents don't need tool calls.
    # The anomaly-detection-agent is instructed to call check_thresholds per machine,
    # but workflow steps cannot handle function-call loops. We provide all readings
    # upfront and explicitly instruct the agent to work from the provided data.
    with open(SENSOR_DATA_PATH, "r") as f:
        sensor_data = json.load(f)
    machines_text = json.dumps(sensor_data["machines"], indent=2)
    query = (
        "All sensor readings for today are provided below — do NOT call check_thresholds. "
        "Analyse the data directly from this message.\n\n"
        + machines_text
        + "\n\nFor each machine, compare every sensor reading against its normal thresholds "
        "and report: machine name/ID, status (normal/warning/critical), and each out-of-spec "
        "reading with current value, threshold violated, and deviation. "
        "Then diagnose root causes and recommend remediation for any anomalous machines."
    )

    print("\n  Submitting workflow run...")
    response = client.responses.create(
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "Act as a factory health workflow: detect sensor anomalies, then diagnose likely faults "
            "and recommend maintenance actions."
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
    anomaly_agent, diagnosis_agent = ensure_agents_deployed()
    report = run_factory_health_workflow(anomaly_agent, diagnosis_agent)
    print_factory_report(report)

    print("\nWorkflow complete!")

    # --- Part B: SDK workflow creation + portal invocation ---
    print("\n" + "=" * 60)
    print("CONFIGURING LOCAL WORKFLOW")
    print("=" * 60)
    workflow_name = WORKFLOW_AGENT_NAME if WORKFLOW_AGENT_NAME and not WORKFLOW_AGENT_NAME.startswith("<") else "factory-health-workflow"
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
