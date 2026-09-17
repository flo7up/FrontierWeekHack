# Challenge 0: Connect

Time: 20 minutes, including the welcome and scenario choice.

**Goal:** see `WORKSHOP_READY` in your terminal. You will use the facilitator's model, not create Azure resources. No Azure subscription, CLI, or portal login is needed.

## 1. Open the Workshop Folder

If you do not have the files yet, open [the workshop repository](https://github.com/flo7up/FrontierWeekHack), choose **Code > Download ZIP**, and extract it. Open the extracted folder in VS Code using **File > Open Folder**.

The main folder contains `requirements.txt`, `smoke_test.py`, and the three scenario folders. This is what the guides mean by **workshop folder**.

Choose **Terminal > New Terminal** in VS Code. Run every workshop command from this main folder, not from inside `claims`. Copy one line at a time and press Enter; wait for it to finish before the next line.

## 2. Prepare Python Once

A stable Python version 3.10 or newer must already be installed; 3.12 is recommended. Use only the commands for your operating system. If Python is missing, ask the facilitator rather than spending the session troubleshooting installation.

### Windows PowerShell

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 --version
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

The `.venv` folder keeps the workshop's Python packages together. You do not need to activate it: later commands use its Python directly. The install may take a few minutes; `Requirement already satisfied` is also a successful result.

## 3. Add Your Private Key

If the facilitator already provided a configured `claims/.env`, keep it and skip to step 4.

1. In VS Code's file list, open `claims/challenge-0-setup/workshop.env.template` ([view template](./workshop.env.template)).
2. Choose **File > Save As**. Save a new file named exactly `.env` in the `claims` folder, one level above `challenge-0-setup`. Do not name it `.env.txt`.
3. In that new file, replace only `XXX` with the key supplied privately by the facilitator, keeping `API_KEY=` in place. Leave the endpoint and model lines unchanged, then save.

The final location is **`claims/.env`**, not `claims/challenge-0-setup/.env`. Keep the public template unchanged.

Treat the key like a password. Never paste it into chat, an AI assistant, screenshots, or GitHub. Close the file before screen sharing. The ignored `.env` stays on your computer; the key authenticates requests sent to the shared model service.

## 4. Check the Connection

From the same main workshop folder:

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe smoke_test.py claims
```

### macOS or Linux

```bash
./.venv/bin/python smoke_test.py claims
```

Wait for a line beginning **`WORKSHOP_READY`**. The check allows 30 seconds. This confirms connectivity, not the quality of future answers.

## If Something Goes Wrong

| What you see | What to do |
|-------------|------------|
| `py` or `python3` not found | Ask the facilitator to help select an installed Python or work with a partner. |
| Cannot find `requirements.txt`, `smoke_test.py`, or `.venv` | Open a new terminal at the main workshop folder, then use the commands above. |
| `No module named ...` | Repeat the package-install command using the `.venv` Python shown above. |
| Missing `.env` or replace `XXX` | Check the file location and name from step 3, then save your local file. |
| 401 or 403 | Ask the facilitator to check the key or resource access. Do not share the key in an error report. |
| 404 | Compare the endpoint and model lines with the public template; ask the facilitator if they match. |
| 429 | Wait one minute and retry once. If it persists, ask the facilitator. |
| Network error or timeout | Check connectivity and ask about managed-device restrictions. Do not disable security controls. |

**Checkpoint:** when you see `WORKSHOP_READY`, continue to [Challenge 1: Build Agents](../challenge-1-build/README.md). You do not need to understand every command to move on.