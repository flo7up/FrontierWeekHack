# Challenge 2: Local Workflow

Time: ~60 minutes

Combine the anomaly detection and fault diagnosis roles into a local workflow. Every model request uses the shared API key; nothing is created in the Foundry portal.

## Run the Workflow

```bash
cd factory/challenge-2-workflow
python deploy.py
```

The workflow:

1. Calls `check_thresholds` for each machine.
2. Produces a grounded anomaly report.
3. Sends affected machines to the diagnosis role.
4. Prints one consolidated factory health report.

## Explore the Code

Open [`deploy.py`](./deploy.py) and find:

- `run_anomaly_scan()` — model plus local function-tool loop
- `run_fault_diagnosis()` — second agent role
- `run_factory_health_workflow()` — Python orchestration

## Experiment

Choose one change, rerun, and compare the result:

- Change a threshold or reading in [`sensor_data.json`](../challenge-1-build/sensor_data.json).
- Make the diagnosis instructions require a confidence level.
- Add a rule that critical recommendations require human approval.

Discuss: what would you add before this could trigger a real maintenance action?