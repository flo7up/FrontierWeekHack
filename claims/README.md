# 📋 Scenario: AI Agents for Insurance Claims Processing

Choose this scenario if you are interested in document review or decision support. The code is provided; your job is to run it, inspect the answers, and try an optional instruction change.

**[Start with Connect](./challenge-0-setup/README.md).** All companies, people, and claims below are fictional. No claim is approved, denied, or paid by the workshop.

## Scenario

![scenario](./images/scenario.png)

You work at **ClaimSight Insurance**, a property and auto insurance company that processes hundreds of claims daily. Each claim has associated metrics: document completeness, damage-vs-estimate consistency, fraud risk scoring, and policy coverage matching. Lately, fraudulent claims and processing delays have been costing the company millions.

Your mission: **Build AI agents using Microsoft Foundry** that can triage incoming claims and make intelligent processing decisions — flagging suspicious claims for investigation while fast-tracking legitimate ones.

You'll run two supplied agent roles:

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

- VS Code and a stable Python 3.10 or newer, installed before the session
- The workshop files and the API key supplied privately by the facilitator
- A partner or facilitator to help with commands if needed

## Structure

All participant exercises run locally through the shared model API. No Azure subscription or portal access is required.

## Challenges

| # | Challenge | Duration | What You'll Do |
|---|-----------|----------|----------------|
| 0 | [Connect](./challenge-0-setup/README.md) | 20 min | Open the workshop and test the shared model |
| 1 | [Build Agents](./challenge-1-build/README.md) | 70 min | Run two roles, inspect the evidence, and optionally change a prompt |
| 2 | [Local Workflow](./challenge-2-workflow/README.md) | 55 min | Follow the selection steps and review a combined report |

The three-hour session also includes a 15-minute break and a 20-minute debrief. Complete only this scenario. Reading results with a partner is a valid alternative to editing code.

## What You Will Learn

- How instructions shape an agent role
- How a model chooses and calls a local function tool
- How grounded claim metrics improve decisions
- How multiple roles can be orchestrated in Python
- Where production systems need identity, auditability, evaluation, and human approval


## Questions to Take Away

- Is a risk flag evidence of fraud, or a reason to ask more questions?
- Which policy documents and checks would a real adjuster need?
- How would you test for wrong or unfair recommendations before anyone relies on them?

This is a learning example, not an insurance decision system. Use only the supplied fictional data: prompts and tool results are sent to the shared cloud model. Monitoring, formal evaluations, and deployment are discussion topics, not extra exercises to finish today.
