# Facilitator Guide

This workshop is designed for 10 participants sharing one pre-provisioned Microsoft Foundry model deployment. Participants do not need Azure subscriptions, Azure CLI, RBAC assignments, Application Insights access, or portal access.

The audience is not expected to be comfortable coding. Demonstrate one run first, explain the output, and offer pair work. Participants can meet the learning goals by suggesting prompt changes and reviewing answers while a partner operates the laptop.

## Shared Resource

Prepare one dedicated workshop resource and model deployment. The tested workshop deployment has:

- 1,000,000 tokens per minute
- 1,000 requests per minute
- GlobalStandard deployment type

These are shared throughput limits, not a guaranteed per-person allocation or a spending cap. Check the remaining credits and the subscription's actual spending-limit settings before the session. Budget alerts alone do not stop spending. Start with one run per exercise and one optional rerun; avoid load tests or repeated full-batch runs.

The exercises use independent Responses API calls and do not create shared agent or workflow resources. Do not distribute access to a production resource.

## Values to Distribute

The public `workshop.env.template` files already contain the shared endpoint and model deployment name. These are configuration, not credentials; they do not grant access. Keep them current across all three scenarios if you change the deployment.

Send only the workshop API key through a private channel shortly before the workshop. Participants copy the template to their scenario's `.env` and replace `XXX` locally:

```dotenv
API_KEY=XXX
```

Mask the entire key in public examples, not just a few characters. Use a secondary resource key for the workshop. Do not place a real key in this repository, slides, chat recordings, or screenshots. Rotate the distributed key immediately after the workshop.

## Preflight

1. Send the [workshop link](https://flo7up.github.io/FrontierWeekHack/) and software checklist before the day. Ask participants to install VS Code and stable Python, or arrange a prepared partner laptop.
2. Test the ZIP download and open-folder route from [README.md](./README.md), not only an existing developer checkout. There is no Git or Azure CLI requirement.
3. Follow Connect and run each scenario's connection test with the same explicit `.venv` commands participants will use. Never project the open key file.
4. Run both exercises in each scenario before the workshop. Save one example output without credentials for an offline demonstration. Review unsupported claims as teaching examples, not necessarily software failures.
5. Check that the three template endpoints/models are current and that credits, authentication, and deployment capacity are sufficient. Rotate any previously exposed key before distribution.
6. Run the offline checks below. They use dummy data and mocked network responses, not the real key.

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m unittest test_workshop -v
```

### macOS or Linux

```bash
./.venv/bin/python -m unittest test_workshop -v
```

## Three-Hour Schedule

| Stage | Duration |
|-------|----------|
| Welcome, scenario choice, and Connect | 20 min |
| Build agent roles and function tool | 70 min |
| Break | 15 min |
| Local multi-agent workflow | 55 min |
| Experiments and production discussion | 20 min |

Ask each participant to choose one scenario. Running all three is not expected.

## Pacing and Fallback

- At 20 minutes, everyone should have `WORKSHOP_READY` or be paired with someone who does. Do not let one installation consume the session.
- In Build, spend roughly 20 minutes running and reading, 20 explaining roles/tools, 20 on an optional prompt edit, and 10 comparing observations.
- In Workflow, spend roughly 15 minutes running, 15 following the selection rule, 15 on an optional edit, and 10 reviewing limitations.
- If a device is blocked by organizational policy, pair the participant or use an instructor demonstration. Do not ask them to bypass restrictions.
- If the shared service is unavailable, use the saved example outputs and sample records. Ask participants to distinguish facts from guesses and propose a better instruction. This still meets the workshop's learning goal.
- Use a simple comparison: **record / supporting fact / unsupported claim / proposed improvement**. A manual check against sample data introduces evaluation without another service or portal.

## Explain the Shortcuts Honestly

- In Build, the two roles receive separate inputs. The second does not consume the first role's generated answer.
- In Factory and Claims Workflow, Python selects follow-up records by recalculating thresholds. It does not parse the first model's report.
- In Call Center Workflow, the follow-up records and classifications are a fixed example list. Its displayed counts are not model-generated routing decisions.
- Each chapter has its own prompt text. Editing an instruction in Build does not change Workflow's instructions.
- All records are fictional, but their text is sent to the cloud model. Do not substitute real customer, medical, financial, or company data.
- A prompt requesting human review is not an enforced approval mechanism. No real business action is performed by these scripts.

## During the Workshop

- Stagger the first full workflow run by a few seconds if everyone reaches it together.
- If a participant receives HTTP 429, wait one minute and retry once; investigate persistent errors centrally.
- Remind participants that the API key identifies the shared resource, not an individual user.
- Ask for the status/error category only, never the configuration file or API key. Have participants close `.env` before screen sharing.
- A connection check is limited to 30 seconds without automatic retries. Full exercises make multiple calls and take longer; use Ctrl+C rather than starting overlapping copies.

## Close the Session

Stop all runs, rotate the distributed key, check usage, and have participants remove the key from their local configuration. There are no participant-created Azure resources to delete. Each group should share one useful result, one limitation, and one human check it would require before real use.

## Topics for the Debrief

The shortened lab intentionally demonstrates concepts rather than production readiness. Discuss what a real system would add: workload identity, per-user authorization, secret management, observability, evaluation, content safety, cost controls, and human approval for consequential actions.