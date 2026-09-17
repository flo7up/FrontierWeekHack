# 📋 Scenario: AI Agents for Insurance Claims Processing

## Scenario

![scenario](./images/scenario.png)

You work at **ClaimSight Insurance**, a property and auto insurance company that processes hundreds of claims daily. Each claim has associated metrics: document completeness, damage-vs-estimate consistency, fraud risk scoring, and policy coverage matching. Lately, fraudulent claims and processing delays have been costing the company millions.

Your mission: **Build AI agents using Microsoft Foundry** that can triage incoming claims and make intelligent processing decisions — flagging suspicious claims for investigation while fast-tracking legitimate ones.

![orchestration](./images/agentic-orchestration.png)

You'll build two agents:

1. **Claims Triage Agent** — Assesses claim metrics against acceptable thresholds and flags anomalies
2. **Claims Decision Agent** — Takes flagged claims and recommends actions (approve, investigate, request documents, deny)

## The Claims

| Claim | Type | Claimant | Status |
|-------|------|----------|--------|
| CLM-001 | Auto Collision | Maria Torres | 🔴 Critical |
| CLM-002 | Property Water Damage | James Chen | ✅ Normal |
| CLM-003 | Auto Theft | Robert Kim | ⚠️ Warning |
| CLM-004 | Property Fire | Sarah Williams | ✅ Normal |
| CLM-005 | Auto Collision | David Okafor | ⚠️ Warning |

## Prerequisites

- Access to a pre-provisioned Microsoft Foundry resource and model deployment
- **Python 3.10+** installed locally
- A Foundry resource API key
- A terminal (bash, PowerShell, or WSL)

## Structure

All participant exercises run locally through the shared model API. No Azure subscription or portal access is required.

## Challenges

| # | Challenge | Duration | What You'll Do |
|---|-----------|----------|----------------|
| 0 | [Connect](./challenge-0-setup/README.md) | 15 min | Configure and test the shared model |
| 1 | [Build Agents](./challenge-1-build/README.md) | 75 min | Run claims triage and decision roles |
| 2 | [Local Workflow](./challenge-2-workflow/README.md) | 60 min | Orchestrate triage → decision → claims report |

## What You Will Learn

- How instructions shape an agent role
- How a model chooses and calls a local function tool
- How grounded claim metrics improve decisions
- How multiple roles can be orchestrated in Python
- Where production systems need identity, auditability, evaluation, and human approval


## Architecture

![architecture](./images/architecture.png)


## Next Steps

Completing these challenges gives you a working local multi-agent workflow. Here are production directions to discuss after the hands-on section:

**Deploy as a hosted agent endpoint**
Microsoft Foundry can host your agents as persistent, scalable API endpoints — no infrastructure to manage. Once hosted, your claims intake system can submit new claims directly to the Triage Agent and receive a structured decision (approve / investigate / request documents / deny) without any manual triage step.

**Add more tools to your agents**
The `assess_claim` function in this lab uses local mock data. In production you'd replace it with tools that call real systems:
- A `fetch_policy` tool querying your policy management system for the exact coverage terms, exclusions, and limits applicable to a specific claim
- A `check_fraud_database` tool querying a fraud intelligence service for known patterns matching the claimant's history
- A `request_documents` tool that automatically triggers a document request workflow in your DMS when the agent recommends it

**Build a knowledge base**
Upload ClaimSight's insurance policy documents, regulatory compliance guidelines, and fraud pattern library to a Microsoft Foundry knowledge base. Attach it to the Claims Decision Agent as a File Search tool so its recommendations cite actual policy language — producing decisions that are auditable and defensible to regulators.

**Integrate evaluations into CI/CD**
Run your evaluation dataset automatically on every pull request or deployment. If the coherence or relevance score drops below a threshold (e.g. 3.5 out of 5), block the release. In a regulated industry, this isn't just good practice — it's the kind of quality gate that compliance and audit teams expect to see documented.

**Explore advanced agent patterns**
- **Parallelise** triage across all incoming claims simultaneously instead of sequentially
- **Add confidence thresholds** — if the Triage Agent's fraud risk assessment falls in an ambiguous range, route to a senior adjuster rather than passing to the Decision Agent automatically
- **Human-in-the-loop** — for high-value claims (above a configurable threshold), always require human adjuster sign-off before the Decision Agent's recommendation is acted on

**Fine-tune for your domain**
Use your evaluation results to identify systematic errors — claim types the agent consistently misjudges or fraud indicators it underweights. Use those cases to refine system prompts, add targeted few-shot examples, or fine-tune the underlying model on ClaimSight's historical claim decisions.
