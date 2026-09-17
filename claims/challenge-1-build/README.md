# Challenge 1: Build Agents

Time: ~75 minutes

## Objectives

By the end of this challenge, you will have:

- ✅ A **Claims Triage Agent** that assesses incoming claims and flags risks
- ✅ A **Claims Decision Agent** that analyzes flagged claims and recommends actions
- ✅ Both agents tested against real claims data

![build](./images/build.png)

## Context

ClaimSight Insurance processes hundreds of claims daily. Each claim has associated metrics: document completeness, damage-vs-estimate consistency, fraud risk score, and policy coverage match. Your agents need to:

1. **Claims Triage**: Compare claim metrics against acceptable thresholds and flag claims that need attention
2. **Claims Decision**: Given a flagged claim, determine the recommended action (approve, investigate, request documents, or deny)

Check out [claims_data.json](./claims_data.json) to see the current batch of claims.

## How It Works

This lab uses the **OpenAI Responses API** with the shared Foundry endpoint and workshop API key. The code runs locally and creates no portal resources.

![foundry](./images/foundry.png)

The code in [agents.py](./agents.py) configures two agent roles, registers a local tool, and runs them against every claim in `claims_data.json`.

## Agents and Tools

### What is an agent?

In this lab, an agent is a model call configured with instructions and optional tools. The Responses API can invoke tools autonomously and continue the response after your Python code returns each tool result. You configure it with:

- A **name** and **model** (e.g. `gpt-5.4`)
- A **system prompt** — instructions that define its role, personality, and constraints
- One or more **tools** it can call when it needs information or actions beyond its training data

The roles are local configurations: instructions, model, and tools sent with each request.

### What are tools?

Tools extend an agent's capabilities beyond pure language generation. When the model decides it needs information it doesn't have in its context window, it emits a **tool call** — a structured JSON request specifying the tool name and arguments. The SDK intercepts this, runs the corresponding Python function, and feeds the result back to the model. This reasoning loop continues until the agent produces a final response.

From the model's perspective, tools are described by a **JSON schema** (name, description, parameters). The model reads these descriptions and decides autonomously when and how to call them — you never hard-code the decision logic.

### What tools can you add?

| Tool type | What it does | Best for |
|-----------|-------------|----------|
| **Function** | Calls a local Python function you define | Any custom logic: database lookups, APIs, calculations |
| **Code Interpreter** | Lets the agent write and execute Python in a sandbox | Data analysis, chart generation, file processing |
| **File Search** | Semantic search over a Microsoft Foundry knowledge base | Policy docs, manuals, historical records |
| **Bing Search** | Live web search | Real-time information, news |
| **Azure AI Search** | Queries an Azure Search index | Grounded retrieval over your own data at scale |

#### Vector databases and Microsoft Foundry knowledge bases

When your agent needs to answer questions grounded in a large body of documents — policy manuals, product specs, historical records — you need a **vector database**. Unlike keyword search, a vector database converts text into numerical embeddings and finds semantically similar passages at query time. This lets the agent ask a natural-language question and retrieve the right content even when the exact words don’t appear in the query.

**Microsoft Foundry** includes a built-in knowledge base backed by a vector store. You upload documents (PDFs, Word files, plain text) and the service automatically chunks, embeds, and indexes them. When you attach this knowledge base to an agent as a **File Search** tool, the agent queries it at inference time — pulling relevant passages into its context before generating a response, so its answers are grounded in your actual documents rather than model training data alone.

For ClaimSight Insurance, useful knowledge bases would include:

- **Insurance policy documents** — coverage terms, exclusion clauses, and payout limits by policy type (auto, property, liability)
- **Regulatory compliance guidelines** — state-specific claim handling rules, mandatory timelines, and disclosure requirements
- **Fraud pattern library** — documented fraud schemes, red-flag indicator combinations, and historical case summaries

With this in place, the **Claims Decision Agent** could query “what is the coverage limit for water damage on a standard home policy in California?” and retrieve the exact policy terms — grounding its approve/deny recommendation in the actual policy language rather than a general understanding of insurance.

In this challenge the agents use **function tools**. The **Claims Triage Agent** uses `assess_claim` to retrieve full claim metrics — document completeness, fraud risk score, damage estimates — before scoring risk. Without this tool, the agent would have to guess from context alone — with it, every triage decision is grounded in the claim's actual data.

## Get Started

Open [agents.py](./agents.py) and review the implementation of both agents.

```bash
cd claims/challenge-1-build
python agents.py
```

As the script runs, each claim from `claims_data.json` is processed by the **Claims Triage Agent** role first, and the high-risk batch is then processed by the **Claims Decision Agent** role. The raw responses are printed in the terminal.

## Experiment

1. Change one sentence in an agent's instructions and rerun the script.
2. Change one claim metric in [`claims_data.json`](./claims_data.json) and predict the result before rerunning.
3. Inspect `ASSESS_CLAIM_TOOL` and `assess_claim()` to see the contract between the model and Python.
4. Discuss which claim decisions must always remain with a human.

## Success Criteria

- [ ] Claims Triage Agent correctly identifies the 2 warning + 1 critical claim
- [ ] Claims Decision Agent provides reasonable action recommendations
- [ ] Both agents respond coherently when given a claim's metrics

Continue to [Challenge 2: Local Workflow](../challenge-2-workflow/README.md).
