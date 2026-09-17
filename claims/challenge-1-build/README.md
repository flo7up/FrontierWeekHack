# Challenge 1: Build Agents

Time: 70 minutes, including discussion and an optional experiment.

## Objectives

By the end of this challenge, you will have:

- ✅ A **Claims Triage Agent** that assesses incoming claims and flags risks
- ✅ A **Claims Decision Agent** that analyzes flagged claims and recommends actions
- Both roles tested against fictional claims, with you reviewing the answers

![build](./images/build.png)

## Context

ClaimSight Insurance processes hundreds of claims daily. Each claim has associated metrics: document completeness, damage-vs-estimate consistency, fraud risk score, and policy coverage match. Your agents need to:

1. **Claims Triage**: Compare claim metrics against acceptable thresholds and flag claims that need attention
2. **Claims Decision**: Given a flagged claim, determine the recommended action (approve, investigate, request documents, or deny)

Check out [claims_data.json](./claims_data.json) to see the current batch of claims.

## How It Works

This lab uses the **OpenAI Responses API** with the shared Foundry endpoint and workshop API key. The code runs locally and creates no portal resources.

The code in [agents.py](./agents.py) configures two agent roles, registers a local tool, and runs them against every claim in `claims_data.json`.

## Agents and Tools

| Term | Meaning here |
|------|--------------|
| Model | The shared AI service that produces an answer |
| Prompt | The instructions and question sent to the model |
| Agent role | A model given a particular job, such as explaining a claim's flags |
| Tool | Existing Python code the model can ask to run; `assess_claim` compares saved metrics with saved limits |

The tool calculates which metrics are outside the example limits. It does not detect real fraud or read an actual insurance policy. The model explains the flags and suggests a next step; a person must assess whether that suggestion is justified.

## 1. Run the Supplied Example

Complete [Connect](../challenge-0-setup/README.md) first. Keep the terminal in the main workshop folder. Use the command for your operating system; do not change folders.

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe claims/challenge-1-build/agents.py
```

### macOS or Linux

```bash
./.venv/bin/python claims/challenge-1-build/agents.py
```

Wait for both sections to finish. Several model requests are made, so this can take a few minutes. Do not launch another copy while one is running. To stop a run, click the terminal and press **Ctrl+C** once.

## 2. Check the Answers

With the unchanged [sample data](./claims_data.json), look for:

| Records | What to check |
|---------|---------------|
| CLM-002 and CLM-004 | Metrics within the example limits |
| CLM-001, CLM-003, and CLM-005 | Flags supported by the saved metrics; compare the reported numbers with the data |

You should see a triage report followed by suggestions for CLM-001, CLM-003, and CLM-005. Wording and order can differ each run. A coherent answer is not proof of a correct decision, and a flag is not proof of fraud.

These are two separate examples: the second role receives a batch selected from saved status labels, not the first role's answer. The next challenge introduces a combined process.

## 3. Optional: Change One Instruction

1. In VS Code, open `claims/challenge-1-build/agents.py` ([view code](./agents.py)).
2. Find `class ClaimsDecisionAgent`, then the English instructions between the triple quotes after `self.instructions =`.
3. Add this sentence inside those quotes: **Use plain language. Name the evidence for your recommendation and what a human reviewer still needs to check.** Do not change quotation marks or indentation.
4. Save and rerun the same command. Compare one claim's before/after answer. To undo your experiment, use **Edit > Undo** on your own edit and save again.

Not comfortable editing? Suggest the sentence to a partner or discuss what you expect it to change. That meets the learning goal too.

## 4. Discuss and Move On

- Is each recommendation supported by a supplied metric?
- Did the model invent a policy rule or turn a risk indicator into an accusation?
- Who would need to approve a real claim decision?

**Checkpoint:** explain why checking a number and deciding an insurance claim are different tasks. No claims are approved or denied by this script. Leave the sample data unchanged for the next challenge; its saved status labels do not automatically update when a metric is edited.

Continue to [Challenge 2: Local Workflow](../challenge-2-workflow/README.md).
