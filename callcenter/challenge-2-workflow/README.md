# Challenge 2: Local Workflow

Time: ~60 minutes

Combine the intent classification and resolution roles into a local workflow. Every model request uses the shared API key; nothing is created in the Foundry portal.

## Run the Workflow

```bash
cd callcenter/challenge-2-workflow
python deploy.py
```

The workflow:

1. Calls `lookup_customer` for each call.
2. Produces a grounded classification report.
3. Sends high-priority calls to the resolution role.
4. Prints one consolidated shift report.

## Explore the Code

Open [`deploy.py`](./deploy.py) and find:

- `run_intent_classification()` — model plus local function-tool loop
- `run_resolution_advisory()` — second agent role
- `run_call_center_workflow()` — Python orchestration

## Experiment

Choose one change, rerun, and compare the result:

- Change a customer or call detail in [`call_data.json`](../challenge-1-build/call_data.json).
- Require the resolution role to explain its escalation decision.
- Add a rule that security concerns always require human review.

Discuss: what would you add before this could route a real customer call?