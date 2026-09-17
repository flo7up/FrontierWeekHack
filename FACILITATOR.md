# Facilitator Guide

This workshop is designed for 10 participants sharing one pre-provisioned Microsoft Foundry model deployment. Participants do not need Azure subscriptions, Azure CLI, RBAC assignments, Application Insights access, or portal access.

## Shared Resource

Prepare one dedicated workshop resource and model deployment. The tested workshop deployment has:

- 1,000,000 tokens per minute
- 1,000 requests per minute
- GlobalStandard deployment type

This provides ample headroom for 10 participants. The exercises use independent Responses API calls and do not create shared agent or workflow resources.

## Values to Distribute

The public `workshop.env.template` files already contain the shared endpoint and model deployment name. These are configuration, not credentials; they do not grant access. Keep them current across all three scenarios if you change the deployment.

Send only the workshop API key through a private channel shortly before the workshop. Participants copy the template to their scenario's `.env` and replace `XXX` locally:

```dotenv
API_KEY=XXX
```

Mask the entire key in public examples, not just a few characters. Use a secondary resource key for the workshop. Do not place a real key in this repository, slides, chat recordings, or screenshots. Rotate the distributed key immediately after the workshop.

## Preflight

1. Clone a fresh copy of the repository.
2. Complete Challenge 0 for one scenario using the participant instructions.
3. Run `python smoke_test.py <scenario>`.
4. Run that scenario's Challenge 1 and Challenge 2 once.
5. Confirm the model deployment still shows sufficient TPM and RPM capacity.

## Three-Hour Schedule

| Stage | Duration |
|-------|----------|
| Welcome, scenario choice, and Connect | 20 min |
| Build agent roles and function tool | 70 min |
| Break | 15 min |
| Local multi-agent workflow | 55 min |
| Experiments and production discussion | 20 min |

Ask each participant to choose one scenario. Running all three is not expected.

## During the Workshop

- Stagger the first full workflow run by a few seconds if everyone reaches it together.
- If a participant receives HTTP 429, wait briefly and retry once.
- Remind participants that the API key identifies the shared resource, not an individual user.
- Do not use production resources or data with the shared workshop key.

## Topics for the Debrief

The shortened lab intentionally demonstrates concepts rather than production readiness. Discuss what a real system would add: workload identity, per-user authorization, secret management, observability, evaluation, content safety, cost controls, and human approval for consequential actions.