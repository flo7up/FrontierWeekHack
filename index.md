![Banner](./assets/images/banner.png)

# Build AI Agents with Microsoft Foundry

This three-hour workshop gives you a practical introduction to tool-using AI agents. Pick one scenario, connect to a shared Microsoft Foundry model, build two agent roles, and combine them in a local workflow.

## Choose Your Scenario

| Scenario | Domain | What You Build |
|----------|--------|----------------|
| [🏭 Factory](./factory/README.md) | Predictive maintenance | Anomaly detection and fault diagnosis |
| [📋 Claims](./claims/README.md) | Insurance processing | Claims triage and decision support |
| [📞 Call Center](./callcenter/README.md) | Customer support | Intent classification and resolution advice |

## Workshop Agenda

| Stage | Duration | Outcome |
|-------|----------|---------|
| Connect | 15 min | Configure the shared endpoint, model, and workshop API key |
| Build | 75 min | Run two agent roles and a local function tool |
| Break | 15 min | |
| Workflow | 60 min | Orchestrate the roles into an end-to-end report |
| Experiment and debrief | 15 min | Change a prompt or input and discuss production concerns |

## What This Workshop Skips

To fit three hours and avoid requiring participant portal access, the hands-on path does not create hosted agents, configure shared Application Insights, or run portal evaluations. The debrief covers why production systems still need identity, secret management, observability, quality evaluation, content safety, cost controls, and human approval.

## What You Need

- Python 3.10 or newer
- A terminal and code editor
- The workshop API key supplied privately by the facilitator; the endpoint and model are prefilled in the public templates

You do **not** need an Azure subscription, Azure CLI, or access to the Microsoft Foundry portal. All participant exercises use a shared model through its API key.

## Getting Started

1. Clone the workshop repository.
2. Pick one scenario.
3. Open its overview and complete Connect, Build, and Local Workflow in order.
4. Never commit or share the workshop API key.
