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

## Before the Session

- Install [Visual Studio Code](https://code.visualstudio.com/) and a stable [Python](https://www.python.org/downloads/) version, 3.10 or newer; 3.12 is a suitable choice.
- Download this repository using **Code > Download ZIP**, then extract it. A GitHub account and Git are not required for this route.
- In VS Code, choose **File > Open Folder** and open the extracted folder containing [requirements.txt](./requirements.txt) and [smoke_test.py](./smoke_test.py).
- Obtain the API key privately from the facilitator. It is the only secret you need to enter.

No Azure subscription, Azure CLI, portal login, or credit card is required from participants. Model requests use the facilitator's shared resource. Ask for help with managed-device installation restrictions; do not change your organization's security settings.

## Start Here

Open your chosen scenario, then follow **Connect > Build Agents > Local Workflow**. Keep VS Code open on the main workshop folder; every command in the guides starts there.

Keep the API key only in your local `.env` file. Never paste it into chat, an AI assistant, screenshots, or a public repository. Ask the facilitator about errors instead of sharing the configuration file.

## For Facilitators

See [FACILITATOR.md](./FACILITATOR.md) for preflight checks, pacing, shared-resource safeguards, and a fallback when a participant's laptop cannot run Python.
