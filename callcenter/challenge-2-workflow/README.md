# Challenge 2: Local Workflow

Time: 55 minutes, including review and an optional experiment.

**Goal:** explain how a sequence of steps differs from a single AI answer. The supplied Python program coordinates the steps; it does not deploy anything, contact customers, or require portal access.

## 1. Run the Combined Example

Finish [Build Agents](../challenge-1-build/README.md) first. Keep the terminal in the main workshop folder, not inside a scenario folder. Choose **GitHub Codespaces** for the browser workspace, regardless of your laptop's operating system; otherwise use the appropriate **Local** command.

### GitHub Codespaces

```bash
python callcenter/challenge-2-workflow/deploy.py
```

### Local Windows PowerShell

```powershell
.\.venv\Scripts\python.exe callcenter/challenge-2-workflow/deploy.py
```

### Local macOS or Linux

```bash
./.venv/bin/python callcenter/challenge-2-workflow/deploy.py
```

This makes several model requests and may take a few minutes. Wait for **`Workflow complete!`** before starting another run. If it appears stuck, press **Ctrl+C** and ask the facilitator; do not repeatedly restart it. For connection errors, use the [Connect troubleshooting table](../challenge-0-setup/README.md#if-something-goes-wrong).

## 2. Follow the Steps

1. The classification role requests customer lookups and writes a report on all seven calls.
2. Python uses a **fixed example list**: CALL-007 (security), CALL-001 (billing), and CALL-003 (cancellation). These saved classifications, not the model's report, choose the follow-up work.
3. The resolution role receives each selected call's saved classification and customer context and drafts advice.
4. Python collects the results into one shift report.

The report displays **7 calls**, **1 critical**, and **2 high priority** from the fixed example. Changing a classification prompt will not automatically reroute calls or recalculate these counts. This deliberate shortcut keeps the exercise small; reliable automatic routing would require additional validation.

Notice that Challenge 1 used CALL-001, CALL-006, and CALL-007 for its second example. A different selection here is expected, not a missing result.

## 3. Optional: Make the Report Easier to Review

Open `callcenter/challenge-2-workflow/deploy.py` ([view code](./deploy.py)). Find `run_resolution_advisory()` and the `instructions` text containing `Use at most 120 words.` Replace that sentence with:

```text
Use at most 120 words. Include a courteous customer response and HUMAN REVIEW NEEDED. Refer security concerns to a human; do not invent refund offers or company policy.
```

Change only the English text inside the existing quotation marks. Save, rerun the same command once, and compare one call's answer with the [sample record](../challenge-1-build/call_data.json). This file has its own instructions; edits from Challenge 1 do not automatically carry over. Reading and discussing this proposed change without editing is equally valid.

## 4. Review as a Group

- Is the advice supported by the customer record?
- Did the model invent an offer, refund policy, or completed action?
- What is missing before the first model's classifications could drive routing automatically?
- Does a prompt asking for human review enforce it? No: a real application would need an explicit approval control.

**Checkpoint:** identify the fixed selection and one recommendation that needs human review. Keep the key private, stop running scripts when finished, and join the 20-minute debrief. No account, payment, or support ticket has been changed.