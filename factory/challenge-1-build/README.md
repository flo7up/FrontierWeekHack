# Challenge 1: Build Agents

Time: 70 minutes, including discussion and an optional experiment.

## Objectives

By the end of this challenge, you will have:

- ✅ An **Anomaly Detection Agent** that monitors sensor data and flags abnormal readings
- ✅ A **Fault Diagnosis Agent** that analyzes flagged anomalies and recommends maintenance actions
- Both roles tested against fictional machine readings, with you reviewing the answers

![build](./images/build.png)

## Context

TireForge Industries has 5 machines on the production floor. Each machine emits sensor data including temperature, pressure, vibration, and RPM. Your agents need to:

1. **Anomaly Detection**: Compare current readings against known thresholds and flag machines that are out of spec
2. **Fault Diagnosis**: Given an anomaly, reason about what might be wrong and recommend an action

Check out [sensor_data.json](./sensor_data.json) to see the current state of all machines.

## How It Works

This lab uses the **OpenAI Responses API** with the shared Foundry endpoint and workshop API key. The code runs locally and creates no portal resources.

The code in [agents.py](./agents.py) configures two agent roles, registers a local tool, and runs them against every machine in `sensor_data.json`.

## Agents and Tools

| Term | Meaning here |
|------|--------------|
| Model | The shared AI service that produces an answer |
| Prompt | The instructions and question sent to the model |
| Agent role | A model given a particular job, such as explaining unusual readings |
| Tool | Existing Python code the model can ask to run; `check_thresholds` compares saved readings with saved limits |

The tool calculates which readings exceed limits. The model explains those results and suggests possible causes. It is not connected to real machines and does not know the actual cause of a fault. Giving a role a name does not create a separate hosted agent.

## 1. Run the Supplied Example

Complete [Connect](../challenge-0-setup/README.md) first. Keep the terminal in the main workshop folder. Use the command for your operating system; do not change folders.

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe factory/challenge-1-build/agents.py
```

### macOS or Linux

```bash
./.venv/bin/python factory/challenge-1-build/agents.py
```

Wait for both sections to finish. Several model requests are made, so this can take a few minutes. Do not launch another copy while one is running. To stop a run, click the terminal and press **Ctrl+C** once.

## 2. Check the Answers

With the unchanged [sample data](./sensor_data.json), look for:

| Record | Evidence to check |
|--------|-------------------|
| EX-002 and CU-004 | No readings outside their limits |
| MX-001 | Temperature and vibration above their limits |
| CP-003 | Temperature, pressure, and vibration above their limits |
| IS-005 | Vibration above its limit |

You should see an anomaly report followed by possible diagnoses for MX-001, CP-003, and IS-005. Wording and order can differ each run. Check the facts rather than expecting identical sentences.

These are two separate examples: the second role receives a batch selected from saved status labels, not the first role's answer. The next challenge introduces a combined process.

## 3. Optional: Change One Instruction

1. In VS Code, open `factory/challenge-1-build/agents.py` ([view code](./agents.py)).
2. Find `class FaultDiagnosisAgent`, then the English instructions between the triple quotes after `self.instructions =`.
3. Add this sentence inside those quotes: **Explain your recommendation to a non-engineer. Separate observed facts from possible causes.** Do not change quotation marks or indentation.
4. Save and rerun the same command. Compare one machine's before/after answer. To undo your experiment, use **Edit > Undo** on your own edit and save again.

Not comfortable editing? Suggest the sentence to a partner or discuss what you expect it to change. That meets the learning goal too.

## 4. Discuss and Move On

- Which statements came from measured sample values, and which were guesses?
- Did the model invent a machine type or maintenance detail absent from the data?
- What would an engineer need to verify before taking action?

**Checkpoint:** explain the difference between the tool's calculation and the model's suggestion. No real maintenance action is taken. Leave the sample data unchanged for the next challenge; its saved status labels do not automatically update when a reading is edited.

Continue to [Challenge 2: Local Workflow](../challenge-2-workflow/README.md).
