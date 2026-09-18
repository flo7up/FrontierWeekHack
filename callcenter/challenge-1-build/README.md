# Challenge 1: Build Agents

## Objectives

By the end of this challenge, you will have:

- ✅ An **Intent Classification Agent** that analyzes call summaries and categorizes customer intent
- ✅ A **Resolution Advisor Agent** that recommends optimal handling strategies
- Both roles tested against fictional calls, with you reviewing the answers

![build](./images/build.png)

## Context

NovaTel Communications receives hundreds of calls daily. Each call has a summary, customer history, and account context. Your agents need to:

1. **Intent Classification**: Analyze the call to determine what the customer needs (billing dispute, tech issue, cancellation risk, upsell opportunity, etc.)
2. **Resolution Advisory**: Given a classified intent + customer context, recommend the best resolution path with scripts, escalation decisions, and available offers

Check out [call_data.json](./call_data.json) to see today's incoming calls.

## How It Works

This lab uses the **OpenAI Responses API** with the shared Foundry endpoint and workshop API key. The code runs locally and creates no portal resources.

The code in [agents.py](./agents.py) configures two agent roles, registers a local tool, and runs them against every call in `call_data.json`.

## Agents and Tools

| Term | Meaning here |
|------|--------------|
| Model | The shared AI service that produces an answer |
| Prompt | The instructions and question sent to the model |
| Agent role | A model given a particular job, such as identifying why a customer called |
| Tool | Existing Python code the model can ask to run; `lookup_customer` reads a fictional customer's saved details |

The tool retrieves information; it does not decide intent. The model uses those details to suggest a category and response. It cannot actually refund, lock an account, or contact a customer.

## 1. Run the Supplied Example

Complete [Connect](../challenge-0-setup/README.md) first. Keep the terminal in the main workshop folder; do not change folders. Choose **GitHub Codespaces** if using the browser workspace, regardless of your laptop's operating system. Otherwise use the appropriate **Local** command.

### GitHub Codespaces

```bash
python callcenter/challenge-1-build/agents.py
```

### Local Windows PowerShell

```powershell
.\.venv\Scripts\python.exe callcenter/challenge-1-build/agents.py
```

### Local macOS or Linux

```bash
./.venv/bin/python callcenter/challenge-1-build/agents.py
```

Wait for both sections to finish. Several model requests are made, so this can take a few minutes. Do not launch another copy while one is running. To stop a run, click the terminal and press **Ctrl+C** once.

## 2. Check the Answers

With the unchanged [sample data](./call_data.json), look for:

| Record | Expected topic to check |
|--------|-------------------------|
| CALL-001 and CALL-006 | Billing disputes |
| CALL-002 | Technical problem |
| CALL-003 | Cancellation request |
| CALL-004 | Additional services |
| CALL-005 | Account help |
| CALL-007 | Security concern that should be referred to a human |

You should see a classification report followed by suggested responses for CALL-001, CALL-006, and CALL-007. Wording, priority, and order can differ each run. Check whether each suggestion is supported by the data rather than expecting identical sentences.

These are two separate examples: the second role receives a preselected batch of customer records, not the first role's answer. The next challenge introduces a combined process.

## 3. Optional: Change One Instruction

1. In VS Code, open `callcenter/challenge-1-build/agents.py` ([view code](./agents.py)).
2. Find `class ResolutionAdvisorAgent`, then the English instructions between the triple quotes after `self.instructions =`.
3. Add this sentence inside those quotes: **Write an empathetic two-sentence customer response. Do not promise a refund or offer unless the supplied policy allows it.** Do not change quotation marks or indentation.
4. Save and rerun the same command. Compare one call's before/after answer. To undo your experiment, use **Edit > Undo** on your own edit and save again.

Not comfortable editing? Suggest the sentence to a partner or discuss what you expect it to change. That meets the learning goal too.

## 4. Discuss and Move On

- Which details came from the saved customer record?
- Did the model invent an offer, refund amount, or company policy?
- Did it recommend human escalation for the security case?

**Checkpoint:** explain why a useful draft still needs a person's review. No customer accounts or payments are changed. Keep the sample data unchanged for the next challenge.

Continue to [Challenge 2: Local Workflow](../challenge-2-workflow/README.md).
