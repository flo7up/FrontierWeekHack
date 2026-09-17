# 🏭 Scenario: Predictive Maintenance — TireForge Industries

## Background

![scenario](./images/scenario.png)

**TireForge Industries** operates a tire manufacturing plant with 5 critical machines:

- **MX-001** (Mixer) — Blends raw rubber compounds
- **EX-002** (Extruder) — Shapes rubber into tire tread profiles
- **CP-003** (Curing Press) — Vulcanizes tires under heat and pressure
- **CU-004** (Cooling Unit) — Gradually cools cured tires
- **IS-005** (Inspection Station) — Quality assurance via vibration analysis

Each machine emits real-time sensor data: temperature, pressure, vibration, and RPM.



## Your Mission

![agentic-orchestration](./images/agentic-orchestration.png)

Build an AI agent system that:

1. **Detects anomalies** — Compares sensor readings against thresholds
2. **Diagnoses faults** — Reasons about root causes from anomaly patterns
3. **Reports health** — Produces a consolidated factory health report

## Challenges

| # | Challenge | What You'll Do | Time |
|---|-----------|---------------|------|
| 0 | [Connect](./challenge-0-setup/README.md) | Configure the shared Foundry model | 15 min |
| 1 | [Build Agents](./challenge-1-build/README.md) | Run anomaly detection and fault diagnosis roles | 75 min |
| 2 | [Local Workflow](./challenge-2-workflow/README.md) | Orchestrate both roles into a health report | 60 min |

## What You Will Learn

- How instructions shape an agent role
- How a model chooses and calls a local function tool
- How grounded tool output reduces hallucination risk
- How multiple roles can be orchestrated in Python
- Where production systems need identity, observability, evaluation, and human approval


## Architecture

![architecture](./images/architecture.png)


## Next Steps

Completing these challenges gives you a working local multi-agent workflow. Here are production directions to discuss after the hands-on section:

**Deploy as a hosted agent endpoint**
Microsoft Foundry can host your agents as persistent, scalable API endpoints — no infrastructure to manage. Once hosted, any system (a SCADA dashboard, a mobile maintenance app, a Slack bot) can send a machine ID and receive a diagnosis in real time, rather than running a Python script manually.

**Add more tools to your agents**
The `check_thresholds` function in this lab uses local mock data. In production you’d replace it with tools that call real systems:
- A `fetch_maintenance_history` tool querying your CMMS (e.g. SAP PM, IBM Maximo) for past failures on that machine
- A `lookup_spare_parts` tool checking inventory availability before recommending a replacement
- A `create_work_order` tool that automatically opens a ServiceNow ticket when the Fault Diagnosis Agent flags a critical issue

**Build a knowledge base**
Upload TireForge’s machine manuals, supplier spec sheets, and historical incident reports to a Microsoft Foundry knowledge base. Attach it to the Fault Diagnosis Agent as a File Search tool so its recommendations are grounded in documented procedures rather than general LLM knowledge.

**Integrate evaluations into CI/CD**
Run your evaluation dataset automatically on every pull request or deployment. If the coherence or relevance score drops below a threshold (e.g. 3.5 out of 5), block the release. This prevents a system prompt edit or model update from silently degrading diagnosis quality in production.

**Explore advanced agent patterns**
- **Parallelise** the anomaly checks across all 5 machines simultaneously instead of sequentially
- **Add confidence thresholds** — if the Anomaly Detection Agent is uncertain, escalate to a human operator rather than passing to Fault Diagnosis automatically
- **Human-in-the-loop** — for critical faults, require a maintenance engineer to approve the recommended action before it triggers a work order

**Fine-tune for your domain**
Use your evaluation results to identify systematic errors — machines the agent consistently misclassifies or fault types it handles poorly. Use those cases to refine system prompts, add targeted few-shot examples, or fine-tune the underlying model on TireForge-specific sensor patterns.
