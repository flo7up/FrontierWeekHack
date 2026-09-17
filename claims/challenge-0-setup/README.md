# Challenge 0: Connect

Time: 20 minutes, including the welcome and scenario choice.

**Goal:** see `WORKSHOP_READY` in your terminal. You will use the facilitator's model, not create Azure resources. No Azure subscription, CLI, or portal login is needed.

## 1. Open the Workshop Folder

Choose one option. Both use the same files and shared model.

### Option A: GitHub Codespaces (Browser)

1. Sign in to GitHub and open [the workshop repository](https://github.com/flo7up/FrontierWeekHack).
2. Select **Code > Codespaces > Create codespace on main**. You do not need to fork it first.
3. Wait for the build and automatic dependency installation to complete. The first start can take several minutes.
4. Open **Terminal > New Terminal** in the browser editor. Use the **GitHub Codespaces** commands below, even on a Windows laptop: the workspace runs Linux.

No local Python or VS Code installation is needed. Your GitHub account must have Codespaces access and available usage; billing is separate from the facilitator's Azure credits. If Codespaces is unavailable, choose Option B or ask to pair with someone.

### Option B: Local VS Code

If you do not have the files yet, open [the workshop repository](https://github.com/flo7up/FrontierWeekHack), choose **Code > Download ZIP**, and extract it. Open the extracted folder in VS Code using **File > Open Folder**.

The main folder contains `requirements.txt`, `smoke_test.py`, and the three scenario folders. This is what the guides mean by **workshop folder**.

Choose **Terminal > New Terminal** in VS Code. Run every workshop command from this main folder, not from inside `claims`. Copy one line at a time and press Enter; wait for it to finish before the next line.

## 2. Prepare Python Once

### GitHub Codespaces

After automatic setup finishes, check Python in the terminal:

```bash
python --version
```

Python and the required packages are supplied by the container. **Skip the local installation commands below and continue to step 3.** The current Codespaces setup does not create `.venv`; all Codespaces examples use `python` directly. If container setup reports a failure, ask the facilitator before proceeding.

### Local Windows PowerShell

A stable Python version 3.10 or newer must already be installed; 3.12 is recommended. If Python is missing, ask the facilitator for help.

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Local macOS or Linux

```bash
python3 --version
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

For local users, `.venv` keeps the workshop's Python packages together. You do not need to activate it: later local commands use its Python directly. The install may take a few minutes; `Requirement already satisfied` is also a successful result.

## 3. Add Your Private Key

If `claims/.env` already exists, do not overwrite it. Open that file instead and check that it contains the current private key. If it is already configured, skip to step 4.

1. In the Codespaces or VS Code file list, expand the `claims` folder and find `.env.template` directly inside it.
2. Right-click `.env.template`, select **Rename**, and change its name to exactly `.env`. Keep it in the same folder; do not name it `.env.txt`.
3. Open `.env`. Copy and paste the key supplied privately by the facilitator over `XXX`, keeping `API_KEY=` in place. Leave the prefilled endpoint and model lines unchanged, then save. You do not need to type the key.

The final location is **`claims/.env`**, not `claims/challenge-0-setup/.env`. Enter the key only after renaming: never put a real key in a tracked template or commit the local rename/deletion. If `.env.template` is missing, use the [downloadable template](./workshop.env.template) and name the downloaded file `claims/.env`.

Treat the key like a password. Never paste it into chat, an AI assistant, screenshots, or GitHub. Close the file before screen sharing. The ignored `.env` lives on your computer for local setup, or inside your private Codespace for browser setup; it is not committed to the repository. The key authenticates requests sent to the shared model service.

In Codespaces, create or edit `.env` in the browser editor. A file on your laptop is not transferred automatically. If the facilitator provides a ready-made `.env`, upload it into `claims` in the Codespace instead of renaming the template; do not overwrite an existing configuration.

## 4. Check the Connection

From the same main workshop folder:

### GitHub Codespaces

```bash
python smoke_test.py claims
```

### Local Windows PowerShell

```powershell
.\.venv\Scripts\python.exe smoke_test.py claims
```

### Local macOS or Linux

```bash
./.venv/bin/python smoke_test.py claims
```

Wait for a line beginning **`WORKSHOP_READY`**. The check allows 30 seconds. This confirms connectivity, not the quality of future answers.

## If Something Goes Wrong

| What you see | What to do |
|-------------|------------|
| Codespaces unavailable or creation denied | Check your GitHub usage/access with the facilitator, use local VS Code, or pair with someone. |
| Container setup failed | Ask the facilitator to review its creation log. Do not use local Windows commands in the Codespace. |
| No `.venv` in Codespaces | This is expected. Use the **GitHub Codespaces** `python` commands. |
| `py` or `python3` not found | Ask the facilitator to help select an installed Python or work with a partner. |
| Cannot find `requirements.txt`, `smoke_test.py`, or `.venv` | Open a new terminal at the main workshop folder, then use the commands above. |
| `No module named ...` | In Codespaces, after setup finishes, try `python -m pip install --user -r requirements.txt`. Locally, repeat the package-install command using the `.venv` Python above. Ask for help if it still fails. |
| Missing `.env` or replace `XXX` | Check the file location and name from step 3, then save your local file. |
| 401 or 403 | Ask the facilitator to check the key or resource access. Do not share the key in an error report. |
| 404 | Compare the endpoint and model lines with the public template; ask the facilitator if they match. |
| 429 | Wait one minute and retry once. If it persists, ask the facilitator. |
| Network error or timeout | Check connectivity and ask about managed-device restrictions. Do not disable security controls. |

**Checkpoint:** when you see `WORKSHOP_READY`, continue to [Challenge 1: Build Agents](../challenge-1-build/README.md). You do not need to understand every command to move on.

At the end of the session, stop your workspace in [Your Codespaces](https://github.com/codespaces) using **... > Stop codespace**. Closing the browser tab is not an immediate stop. Delete the workspace when no longer needed to avoid continued storage usage, after keeping any non-secret work you need.