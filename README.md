![Workshop banner](./docs/assets/images/banner.png)

# AI Agents: A Three-Hour Workshop

Explore what an AI agent can do, what a tool adds, and why human review still matters. The working Python code is provided: you will run it, read its answers, and optionally change a few plain-language instructions. You do not need to write a program from scratch. Pair work and facilitator help are welcome.

**[Open the workshop guide](https://flo7up.github.io/FrontierWeekHack/)** or choose a scenario below. This is a beginner-friendly adaptation of [Microsoft's FrontierWeekHack](https://github.com/microsoft/FrontierWeekHack), not the original advanced learning path.

## Choose One Scenario

All three teach the same concepts. Complete one, not all three.

| Scenario | What you will explore |
|----------|-----------------------|
| [Call Center](./callcenter/README.md) | Understand customer requests and suggest a response; a useful starting point if you are unsure |
| [Factory](./factory/README.md) | Spot unusual machine readings and suggest questions for a maintenance expert |
| [Claims](./claims/README.md) | Flag insurance claims for review and suggest next steps |

All names, records, and readings are fictional workshop data. Outputs are suggestions for discussion, not operational, financial, or safety advice.

## Three-Hour Agenda

| Activity | Time |
|----------|------|
| Welcome, choose a scenario, and Connect | 20 min |
| Build: run the examples, understand tools, and try a prompt change | 70 min |
| Break | 15 min |
| Local Workflow: run the combined process and inspect its decisions | 55 min |
| Compare results and discuss production risks | 20 min |

Success means explaining an agent's role, identifying the facts it used, and spotting one limitation. Finishing every optional experiment is not required.

## Optional Bonus: Agent Framework DevUI

The [DevUI bonus guide](./docs/bonus-devui.md) adds browser chat and local agent traces using the same private model key. Start one supplied scenario agent, ask a tool-using question, and inspect its inputs, results, and timing in **Traces > OTel Spans**. No Azure portal or Application Insights setup is needed.

Allow 20-30 minutes as an alternative to a prompt experiment or an after-session activity. Bonus packages use a separate `.venv-devui` environment and are not installed by the core setup. In Codespaces, port 8080 must stay **Private**. DevUI has its own temporary login token; do not enter the Foundry API key in its browser login.

## Before the Session

Choose **one** environment. Both run the same workshop; you do not need to set up both.

### Option A: GitHub Codespaces (Browser)

Use this option to avoid installing Python or VS Code on your computer.

1. Sign in to GitHub and open [the workshop repository](https://github.com/flo7up/FrontierWeekHack).
2. Select **Code > Codespaces > Create codespace on main**. You do not need to fork the repository first.
3. Wait for the container build and automatic package installation to finish before running commands. The first start can take several minutes.
4. Open **Terminal > New Terminal** in the browser editor. Follow the **GitHub Codespaces** commands in your scenario guides, even if your laptop runs Windows. The Codespace terminal runs Linux and uses `python`, not a local `.venv`.

You need a GitHub account with Codespaces access and available usage or an approved billing arrangement. Codespaces compute and storage are separate from the facilitator's Azure credits. Check this before the session; if access is unavailable, use Option B or pair with someone.

### Option B: Local VS Code

- Install [Visual Studio Code](https://code.visualstudio.com/) and a stable [Python](https://www.python.org/downloads/) version, 3.10 or newer; 3.12 is a suitable choice.
- Download this repository using **Code > Download ZIP**, then extract it. A GitHub account and Git are not required for this route.
- In VS Code, choose **File > Open Folder** and open the extracted folder containing [requirements.txt](./requirements.txt) and [smoke_test.py](./smoke_test.py).

For either option, obtain the API key privately from the facilitator. No participant Azure subscription, Azure CLI login, or Foundry portal access is required. Model requests use the facilitator's shared resource. Ask for help with managed-device installation restrictions; do not change your organization's security settings.

## Start Here

Open your chosen scenario, then follow **Connect > Build Agents > Local Workflow**. Keep VS Code open on the main workshop folder; every command in the guides starts there.

Keep the API key only in your local `.env` file. Never paste it into chat, an AI assistant, screenshots, or a public repository. Ask the facilitator about errors instead of sharing the configuration file.

In Codespaces, that file lives in your private Codespace, not on your laptop, and your laptop's `.env` is not uploaded automatically. Use the scenario's rename-and-paste instructions inside the browser editor.

## After the Session

Stop running scripts. Codespaces users should visit [Your Codespaces](https://github.com/codespaces), open the workspace's **...** menu, and choose **Stop codespace**. Closing the browser tab does not immediately stop it. Delete the Codespace when no longer needed, after keeping any non-secret work you want; stored workspaces can continue consuming storage allowance. Never publish the key.

## For Facilitators

See [FACILITATOR.md](./FACILITATOR.md) for preflight checks, pacing, shared-resource safeguards, and a fallback when a participant's laptop cannot run Python.
