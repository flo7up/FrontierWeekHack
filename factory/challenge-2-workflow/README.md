# Challenge 2: Local Workflow

Time: 55 minutes, including review and an optional experiment.

**Goal:** explain how a sequence of steps differs from a single AI answer. The supplied Python program coordinates the steps; it does not deploy anything, change equipment, or require portal access.

## 1. Run the Combined Example

Finish [Build Agents](../challenge-1-build/README.md) first. Keep the terminal in the main workshop folder, not inside a scenario folder. Choose **GitHub Codespaces** for the browser workspace, regardless of your laptop's operating system; otherwise use the appropriate **Local** command.

### GitHub Codespaces

```bash
python factory/challenge-2-workflow/deploy.py
```

### Local Windows PowerShell

```powershell
.\.venv\Scripts\python.exe factory/challenge-2-workflow/deploy.py
```

### Local macOS or Linux

```bash
./.venv/bin/python factory/challenge-2-workflow/deploy.py
```

This makes several model requests and may take a few minutes. Wait for **`Workflow complete!`** before starting another run. If it appears stuck, press **Ctrl+C** and ask the facilitator; do not repeatedly restart it. For connection errors, use the [Connect troubleshooting table](../challenge-0-setup/README.md#if-something-goes-wrong).

## 2. Follow the Steps

1. The anomaly role requests tool checks and produces a report on all five machines.
2. Python recalculates the threshold checks to select machines with out-of-range readings. It does not interpret the model's report to make this selection.
3. The diagnosis role receives each selected machine's calculated anomalies and suggests causes and next steps.
4. Python collects the results into one report.

With the unchanged [sample data](../challenge-1-build/sensor_data.json), the final report should say **5 machines checked**, **3 affected**: MX-001, CP-003, and IS-005. Model wording will vary. A maintenance suggestion is not a confirmed diagnosis.

## 3. Optional: Make the Report Easier to Review

Open `factory/challenge-2-workflow/deploy.py` ([view code](./deploy.py)). Find `run_fault_diagnosis()` and the `instructions` text containing `Use at most 120 words.` Replace that sentence with:

```text
Use at most 120 words. Separate OBSERVED FACTS, POSSIBLE CAUSES, and HUMAN CHECKS. Do not present a possible cause as confirmed.
```

Change only the English text inside the existing quotation marks. Save, rerun the same command once, and compare one machine's answer. This file has its own instructions; edits from Challenge 1 do not automatically carry over. Reading and discussing this proposed change without editing is equally valid.

## 4. Review as a Group

- Does each proposed cause follow from the available readings?
- Did the model invent a machine type, history, or inspection result?
- Which step is fixed Python logic, and which step is an AI suggestion?
- Does writing "human approval required" in a prompt actually enforce approval? No: a real application would need an explicit approval control.

**Checkpoint:** explain the selection rule and name one claim an engineer would need to verify. Keep the key private, stop running scripts when finished, and join the 20-minute debrief. No real maintenance action has been taken.