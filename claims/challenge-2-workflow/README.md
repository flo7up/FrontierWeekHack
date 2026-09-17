# Challenge 2: Local Workflow

Time: 55 minutes, including review and an optional experiment.

**Goal:** explain how a sequence of steps differs from a single AI answer. The supplied Python program coordinates the steps; it does not deploy anything, approve claims, or require portal access.

## 1. Run the Combined Example

Finish [Build Agents](../challenge-1-build/README.md) first. Keep the terminal in the main workshop folder, not inside a scenario folder. Choose **GitHub Codespaces** for the browser workspace, regardless of your laptop's operating system; otherwise use the appropriate **Local** command.

### GitHub Codespaces

```bash
python claims/challenge-2-workflow/workflow.py
```

### Local Windows PowerShell

```powershell
.\.venv\Scripts\python.exe claims/challenge-2-workflow/workflow.py
```

### Local macOS or Linux

```bash
./.venv/bin/python claims/challenge-2-workflow/workflow.py
```

This makes several model requests and may take a few minutes. Wait for **`Workflow complete!`** before starting another run. If it appears stuck, press **Ctrl+C** and ask the facilitator; do not repeatedly restart it. For connection errors, use the [Connect troubleshooting table](../challenge-0-setup/README.md#if-something-goes-wrong).

## 2. Follow the Steps

1. The triage role requests tool checks and produces a report on all five claims.
2. Python recalculates the metric checks to select flagged claims. It does not interpret the model's report to make this selection.
3. The decision role receives each selected claim's calculated flags and suggests next steps.
4. Python collects the results into one report.

With the unchanged [sample data](../challenge-1-build/claims_data.json), the final report should say **5 claims assessed**, **3 flagged**: CLM-001, CLM-003, and CLM-005. Wording will vary. The flags and status labels are teaching examples, not validated fraud findings or policy decisions.

## 3. Optional: Make the Report Easier to Review

Open [workflow.py](./workflow.py) in `claims/challenge-2-workflow`. Find `run_claims_decision()` and the `instructions` text containing `Use at most 120 words.` Replace that sentence with:

```text
Use at most 120 words. Separate SUPPLIED EVIDENCE, MISSING INFORMATION, and HUMAN REVIEW. Never treat a risk flag as proof of fraud.
```

Change only the English text inside the existing quotation marks. Save, rerun the same command once, and compare one claim's answer. This file has its own instructions; edits from Challenge 1 do not automatically carry over. Reading and discussing this proposed change without editing is equally valid.

## 4. Review as a Group

- Is the recommendation supported by the supplied flags?
- Did the model invent a policy rule, document, or fraud finding?
- Which step is fixed Python logic, and which step is an AI suggestion?
- Does writing "human approval required" in a prompt actually enforce approval? No: a real application would need an explicit approval control.

**Checkpoint:** explain the selection rule and name one claim a human adjuster would need to verify. Keep the key private, stop running scripts when finished, and join the 20-minute debrief. No real claim has been approved or denied.