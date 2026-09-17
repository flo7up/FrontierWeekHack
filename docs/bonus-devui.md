# Bonus: Chat and Inspect Agent Traces

Time: 20-30 minutes. Optional: replace a prompt experiment with this activity, or continue after the core workshop. You do not have to finish it during the three-hour session.

**Goal:** ask a question in Microsoft Agent Framework DevUI, find the tool call it caused, and inspect the facts returned to the agent. No Azure login, hosted agent, or Application Insights resource is required.

## What Is Different?

The core workshop calls the model directly from Python. This bonus wraps the same scenario tool in a Microsoft Agent Framework agent. DevUI adds browser chat and a debug panel for **new runs made through that UI**. It does not show earlier terminal runs or turn the existing workflow into a hosted service.

Each participant runs their own DevUI instance and sees their own session's traces. Only model usage and quota are shared. The supplied bonus has its own concise instructions; edits to Chapter 1 prompts do not automatically appear here.

## 1. Install the Optional Packages

Complete Connect for your chosen scenario first. Its private `.env` should already work with the connection test. Keep the terminal in the main repository folder.

Use a **separate bonus environment** so these packages do not replace the core workshop's dependencies. Install once, using the commands for your environment. Installation may take several minutes. The bonus versions are pinned because DevUI is a beta development tool.

### GitHub Codespaces

```bash
python -m venv .venv-devui
./.venv-devui/bin/python -m pip install -r bonus-devui/requirements.txt
```

### Local Windows PowerShell

```powershell
py -3 -m venv .venv-devui
.\.venv-devui\Scripts\python.exe -m pip install -r bonus-devui/requirements.txt
```

### Local macOS or Linux

```bash
python3 -m venv .venv-devui
./.venv-devui/bin/python -m pip install -r bonus-devui/requirements.txt
```

No activation is needed. The bonus uses `.venv-devui`; the original exercises keep their previous Python commands.

## 2. Start Your Scenario Agent

The example below uses Factory. Replace the final word `factory` with `claims` or `callcenter` for your scenario. It loads that scenario's private `.env`; you do not enter the Foundry API key again.

### GitHub Codespaces or Local macOS/Linux

```bash
./.venv-devui/bin/python bonus-devui/devui.py factory
```

### Local Windows PowerShell

```powershell
.\.venv-devui\Scripts\python.exe bonus-devui/devui.py factory
```

Leave this terminal running. Look for `http://127.0.0.1:8080` and the line **DevUI authentication enabled with auto-generated token**. Copy the token displayed immediately below it privately. It is a temporary **DevUI login token**, not your Foundry API key. Do not screen-share or publish it.

The launcher binds to localhost, enables authentication and tracing, and does not configure an external telemetry exporter. Traces include the fictional prompt, tool input/output, and reply so you can inspect them. Do not use real personal, customer, or company data.

## 3. Open the Browser UI

### In Codespaces

1. Open the **Ports** tab next to Terminal. If port **8080** is missing, choose **Add port** and enter `8080`.
2. Check **Port Visibility** is **Private**, not Public or Organization.
3. Choose **Open in Browser** for that port. Use this forwarded address, not `localhost` typed into your laptop's browser.
4. Sign in to GitHub if prompted. In DevUI's **Authentication Required** screen, paste the **DevUI token** from step 2 and click **Connect**.

Keep the port private even though DevUI also has authentication. Every participant can use port 8080 because each Codespace is separate. Port-forwarding access depends on your GitHub account and organizational policy, not your Azure API key.

### On Your Own Computer

Open `http://127.0.0.1:8080` in a browser on the same computer. Paste the **DevUI token** in **Authentication Required**, then choose **Connect**.

**Never paste the Foundry API key into DevUI's login box.** If you deliberately configured `DEVUI_AUTH_TOKEN` yourself, use that local token instead of expecting an automatically generated one. Leave authentication enabled.

## 4. Ask One Tool-Using Question

Select your assistant in the top dropdown if it is not already selected. Use the matching prompt:

| Scenario | Assistant | Prompt |
|----------|-----------|--------|
| Factory | `factory-assistant` | Use check_thresholds for CP-003. Give the measured exceptions and one human check in under 80 words. |
| Claims | `claims-assistant` | Use assess_claim for CLM-001. Explain the flags and one question for a human adjuster in under 80 words. |
| Call Center | `callcenter-assistant` | Use lookup_customer for CALL-007. Summarize the concern and recommend human escalation in under 80 words. |

Click **Send message** once and wait for the response to finish. One message can require several model calls. Avoid whole-dataset prompts here to conserve shared credits.

## 5. Find the Agent Trace

The debug panel is on the right of the chat. If it is collapsed, expand it; widen the browser or drag the divider if the details are cramped.

1. Choose **Traces**, then **OTel Spans**. A *span* is a recorded operation with timing and attributes; a *trace* groups related spans for one run.
2. Expand the latest turn and its assistant span using the small arrows.
3. Look for a model span such as `chat grok-4.6`, a tool span, and a subsequent model span. Exact order, timings, and counts can vary.
4. Expand `execute_tool check_thresholds`, `execute_tool assess_claim`, or `execute_tool lookup_customer`.
5. Under **Attributes**, find `gen_ai.tool.call.arguments` and `gen_ai.tool.call.result`. Match the requested record ID and returned facts to the answer.
6. Inspect a model span's duration and token usage when reported. The **Tools** tab offers another view of tool calls; **Events** shows the streamed execution events.

For the unchanged Factory sample, CP-003's tool result contains temperature **198.5**, pressure **18.2**, and vibration **7.3**, all outside their example limits. The response should reflect those facts. The trace may show `StatusCode.UNSET` for a span with no explicit error; that alone does not indicate failure.

**Checkpoint:** point to the record ID in the tool arguments, one fact in its result, and the corresponding statement in the response. Did the model add an assumption unsupported by that result?

Traces show the recorded operations and data, not the model's hidden reasoning. A successful tool call or a fluent answer does not prove a recommendation is correct. Parent spans include child time; do not add all span durations together as if they were separate elapsed times.

## 6. Optional Comparison

Start **New Conversation**, then ask about a second record: EX-002, CLM-002, or CALL-001. Compare the tool results with the first conversation. Use one or two messages, not a load test.

The framework, not the participant, manages the tool-call loop in this bonus. If you want to examine the setup, open `bonus-devui/devui.py` in your workspace and find `SCENARIOS` and `build_agent()`. Changing those instructions requires stopping and restarting the server; refresh the UI and use the new DevUI token.

## Troubleshooting

| What you see | What to do |
|-------------|------------|
| Import error or unknown tracing option | Use the pinned bonus requirements and `.venv-devui` commands, not a globally installed `devui` CLI or an older tutorial. |
| Missing `.env` or placeholder key | Finish your scenario's Connect instructions. The launcher expects the same three model settings. |
| Authentication Required or 401 before chat | Use the current **DevUI** token. A restart can generate a different token. Do not use the Foundry key here. |
| Model request reports 401, 403, or 404 after sending | Run the normal connection test or ask the facilitator to check the model configuration. |
| Port already in use | Stop the previous bonus server, or append `--port 8081` to the launch command and forward/open that port instead. |
| Codespaces browser cannot open DevUI | Keep the server running, forward the correct port privately, and use **Open in Browser** while signed into the owning GitHub account. Ask about policy restrictions; do not make it public as a workaround. |
| Traces show No Data | Wait for a new UI response to complete. Use this launcher, which enables instrumentation, and choose Traces > OTel Spans. Terminal runs from earlier challenges are not imported. |
| No tool span | Start a new conversation and explicitly ask to use the tool with a valid sample ID. A general greeting may not call a tool. |
| HTTP 429 or slow response | Wait one minute and retry once. Ask the facilitator if it persists; do not run overlapping requests. |

## Finish Safely

Press **Ctrl+C** in the server terminal, close the forwarded port, and stop the Codespace when finished. Treat the debug view and tokens as private. DevUI is a development sample, not a production portal or a GitHub Pages app. Do not rely on session traces being preserved after restart.

The optional UI's login token and the Foundry model key are separate. Stopping DevUI does not revoke the model key; the facilitator rotates the workshop key separately.