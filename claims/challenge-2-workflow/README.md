# Challenge 2: Local Workflow

Time: ~60 minutes

Combine the claims triage and decision roles into a local workflow. Every model request uses the shared API key; nothing is created in the Foundry portal.

## Run the Workflow

```bash
cd claims/challenge-2-workflow
python deploy.py
```

The workflow:

1. Calls `assess_claim` for each claim.
2. Produces a grounded triage report.
3. Sends flagged claims to the decision role.
4. Prints one consolidated claims report.

## Explore the Code

Open [`deploy.py`](./deploy.py) and find:

- `run_claims_triage()` — model plus local function-tool loop
- `run_claims_decision()` — second agent role
- `run_claims_workflow()` — Python orchestration

## Experiment

Choose one change, rerun, and compare the result:

- Change a threshold or claim metric in [`claims_data.json`](../challenge-1-build/claims_data.json).
- Require the decision role to cite the flags behind its recommendation.
- Add a rule that denials always require human approval.

Discuss: what would you add before this could influence a real insurance claim?