![Banner](./assets/images/banner.png)

# AI Agents: A Three-Hour Workshop

Explore what an AI agent can do, what a tool adds, and why people still need to check the result. All Python code is supplied. You will run examples, read their answers, and optionally change a few English instructions, not write a program from scratch. Pair work and facilitator help are welcome.

## Choose Your Scenario

Choose **one** scenario for the session. If you are unsure, Call Center is an accessible starting point. All companies, people, and records are fictional workshop examples.

| Scenario | Domain | What You Build |
|----------|--------|----------------|
| [🏭 Factory](./factory/README.md) | Predictive maintenance | Anomaly detection and fault diagnosis |
| [📋 Claims](./claims/README.md) | Insurance processing | Claims triage and decision support |
| [📞 Call Center](./callcenter/README.md) | Customer support | Intent classification and resolution advice |

## Workshop Agenda

| Stage | Duration | Outcome |
|-------|----------|---------|
| Welcome and Connect | 20 min | Choose a scenario, open the files, and see `WORKSHOP_READY` |
| Build | 70 min | Run two roles, inspect the evidence, and optionally change a prompt |
| Break | 15 min | |
| Local Workflow | 55 min | Follow the selection steps and review a combined report |
| Compare and debrief | 20 min | Share one useful answer, one unsupported claim, and one human check |

## What This Workshop Skips

There are no portal exercises, deployments, shared dashboards, or formal evaluation jobs. The debrief asks how a real system would control access, protect data, track failures, check quality, limit spending, and require human approval. The examples are not production-ready systems or operational advice.

## Before the Session

- Install [VS Code](https://code.visualstudio.com/) and a stable [Python](https://www.python.org/downloads/) version 3.10 or newer; 3.12 is recommended.
- Open [your workshop repository](https://github.com/flo7up/FrontierWeekHack), select **Code > Download ZIP**, and extract it. A GitHub account and Git are not needed for this route.
- In VS Code, use **File > Open Folder** and select the extracted folder containing `requirements.txt` and `smoke_test.py`.
- Obtain the workshop API key privately from the facilitator. The public templates already contain the endpoint and model name.

You do **not** need an Azure subscription, Azure CLI, or access to the Microsoft Foundry portal. All participant exercises use a shared model through its API key.

Python runs on your laptop, but model requests send prompts and sample data to the shared cloud service. Use only the fictional workshop data, not real customer or company information. Keep the key in your local `.env`, never in chat, an AI assistant, screenshots, or the public template.

## Getting Started

1. Open your chosen scenario and complete **Connect > Build Agents > Local Workflow** in order.
2. Keep the terminal at the main workshop folder throughout. Choose only the commands for your operating system.
3. Run each example once, inspect the output, then try one optional change. Different wording on repeated runs is normal.
4. Ask for help or pair with someone if setup blocks you. Do not spend the workshop changing device security settings.

**Success is understanding, not typing speed:** explain an agent's job, identify facts supplied by a tool, and name one answer you would not trust without human review. Editing code is optional.
