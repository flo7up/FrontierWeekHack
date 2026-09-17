# 📞 Scenario: Call Center Triage — NovaTel Communications

Choose this scenario if you are interested in customer service, or are unsure which scenario to pick. The code is provided; your job is to run it, inspect the answers, and try an optional instruction change.

**[Start with Connect](./challenge-0-setup/README.md).** All companies, people, and calls below are fictional. No customers are contacted and no accounts or payments are changed.

## Background

![scenario](./images/scenario.png)

**NovaTel Communications** is a telecom provider handling hundreds of customer calls daily across their support center. Today's queue has 7 active calls spanning different issue types:

- **CALL-001** — Maria Gonzalez (Premium, 3 years) — Unexpected charge dispute
- **CALL-002** — James Liu (Basic, 4 months) — Internet dropping repeatedly
- **CALL-003** — Priya Sharma (Premium, 18 months) — Wants to cancel (moving)
- **CALL-004** — Robert Chen (Business, 2 years) — Adding 7 phone lines
- **CALL-005** — Sarah Mitchell (Basic, 5 years) — Can't navigate new app
- **CALL-006** — David Park (Premium, 1 year) — Charged for returned device
- **CALL-007** — Emma Wilson (Basic, 8 months) — Suspected account hack



## Your Mission

Run the supplied examples to see how a system:

1. **Classifies intent** — Determines what each customer needs (billing, tech, cancellation, upsell, support, security)
2. **Advises resolution** — Recommends the best handling strategy based on customer context
3. **Produces a shift report** — Consolidated triage with prioritized action items

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
- How grounded customer context improves recommendations
- How multiple roles can be orchestrated in Python
- Where production systems need identity, observability, evaluation, and human review



## Questions to Take Away

- Did the suggested response use the customer's actual sample details?
- Which refund offers or promises would need a policy check?
- What validation is missing before AI classifications could route calls automatically?

This is a learning example, not a live contact-center system. Use only the supplied fictional data: prompts and tool results are sent to the shared cloud model. Monitoring, formal evaluations, and deployment are discussion topics, not extra exercises to finish today.
