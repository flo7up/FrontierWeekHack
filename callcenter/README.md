# 📞 Scenario: Call Center Triage — NovaTel Communications

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

![agentic-orchestration](./images/agentic-orchestration.png)

Build an AI agent system that:

1. **Classifies intent** — Determines what each customer needs (billing, tech, cancellation, upsell, support, security)
2. **Advises resolution** — Recommends the best handling strategy based on customer context
3. **Produces a shift report** — Consolidated triage with prioritized action items

## Challenges

| # | Challenge | What You'll Do | Time |
|---|-----------|---------------|------|
| 0 | [Connect](./challenge-0-setup/README.md) | Configure the shared Foundry model | 15 min |
| 1 | [Build Agents](./challenge-1-build/README.md) | Run classification and resolution roles | 75 min |
| 2 | [Local Workflow](./challenge-2-workflow/README.md) | Orchestrate both roles into a shift report | 60 min |

## What You Will Learn

- How instructions shape an agent role
- How a model chooses and calls a local function tool
- How grounded customer context improves recommendations
- How multiple roles can be orchestrated in Python
- Where production systems need identity, observability, evaluation, and human review



## Architecture

![architecture](./images/architecture.png)

## Next Steps

Completing these challenges gives you a working local multi-agent workflow. Here are production directions to discuss after the hands-on section:

**Deploy as a hosted agent endpoint**
Microsoft Foundry can host your agents as persistent, scalable API endpoints — no infrastructure to manage. Once hosted, your telephony platform (Twilio, Genesys, Azure Communication Services) can push live call transcripts directly to the Intent Classification Agent and receive triage decisions in real time, replacing manual queue review.

**Add more tools to your agents**
The `lookup_customer` function in this lab uses local mock data. In production you’d replace it with tools that call real systems:
- A `fetch_crm_history` tool querying Salesforce or Dynamics 365 for the customer’s full interaction history
- A `check_active_offers` tool pulling current retention promotions and eligibility rules from a pricing API
- A `create_case` tool that automatically opens a CRM ticket and assigns it to the right queue based on the Resolution Advisor’s recommendation

**Build a knowledge base**
Upload NovaTel’s customer service policy manual, resolution scripts, and product documentation to a Microsoft Foundry knowledge base. Attach it to the Resolution Advisor Agent as a File Search tool so its scripts are grounded in the actual approved playbook — not a hallucinated version of it.

**Integrate evaluations into CI/CD**
Run your evaluation dataset automatically on every pull request or deployment. If the coherence or relevance score drops below a threshold (e.g. 3.5 out of 5), block the release. This prevents a system prompt edit or model update from silently degrading classification accuracy during peak call hours.

**Explore advanced agent patterns**
- **Parallelise** intent classification across all 7 calls simultaneously instead of sequentially
- **Add confidence thresholds** — if the Intent Agent is uncertain between cancellation and billing, flag the call for human review rather than auto-assigning
- **Human-in-the-loop** — for CALL-007 (security incidents), always escalate to a human supervisor regardless of the agent’s confidence level

**Fine-tune for your domain**
Use your evaluation results to identify systematic errors — intent types the agent consistently confuses or customer segments it handles poorly. Use those cases to refine system prompts, add targeted few-shot examples, or fine-tune the underlying model on NovaTel call transcripts.
