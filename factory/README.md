# 🏭 Scenario: Predictive Maintenance — TireForge Industries

Choose this scenario if you are interested in operations or maintenance. The code is provided; your job is to run it, inspect the answers, and try an optional instruction change. No engineering or programming expertise is required to take part with facilitator support.

**[Start with Connect](./challenge-0-setup/README.md).** All companies, readings, and records below are fictional. No real equipment is connected or controlled.

## Background

![scenario](./images/scenario.png)

**TireForge Industries** operates a tire manufacturing plant with 5 critical machines:

- **MX-001** (Mixer) — Blends raw rubber compounds
- **EX-002** (Extruder) — Shapes rubber into tire tread profiles
- **CP-003** (Curing Press) — Vulcanizes tires under heat and pressure
- **CU-004** (Cooling Unit) — Gradually cools cured tires
- **IS-005** (Inspection Station) — Quality assurance via vibration analysis

The sample file contains a saved snapshot of temperature, pressure, vibration, and rotation speed (RPM). These are not live sensor feeds.



## Your Mission

Run the supplied examples to see how a system:

1. **Detects anomalies** — Compares sensor readings against thresholds
2. **Diagnoses faults** — Reasons about root causes from anomaly patterns
3. **Reports health** — Produces a consolidated factory health report

## Challenges

| # | Challenge | What You'll Do | Time |
|---|-----------|---------------|------|
| 0 | [Connect](./challenge-0-setup/README.md) | Open the workshop and test the shared model | 20 min |
| 1 | [Build Agents](./challenge-1-build/README.md) | Run two roles, inspect the evidence, and optionally change a prompt | 70 min |
| 2 | [Local Workflow](./challenge-2-workflow/README.md) | Follow the selection steps and review a combined report | 55 min |

The three-hour session also includes a 15-minute break and a 20-minute debrief. Complete only this scenario. Reading results with a partner is a valid alternative to editing code.

## What You Will Learn

- How instructions shape an agent role
- How a model chooses and calls a local function tool
- How grounded tool output reduces hallucination risk
- How multiple roles can be orchestrated in Python
- Where production systems need identity, observability, evaluation, and human approval


## Questions to Take Away

- What evidence supports a proposed diagnosis, and what is still unknown?
- How would you check the answers against cases reviewed by a maintenance expert?
- Who must approve an action before a real machine can be affected?

This is a learning example, not a validated maintenance system. Use only the supplied fictional data: prompts and tool results are sent to the shared cloud model. Monitoring, formal evaluations, and deployment are discussion topics, not extra exercises to finish today.
