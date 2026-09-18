"""Shared API-key authentication for Microsoft Foundry model calls."""

import json
import os
from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Literal

from openai import OpenAI


@dataclass(frozen=True)
class ApiKeyAgent:
    """Local agent metadata for API-key-authenticated response calls."""

    name: str
    version: str = "api-key"


def create_foundry_client() -> OpenAI:
    endpoint = os.getenv("FOUNDRY_ENDPOINT", "").rstrip("/")
    api_key = os.getenv("API_KEY", "").strip()

    if not endpoint:
        raise RuntimeError("FOUNDRY_ENDPOINT is not set in the scenario .env file.")
    if not api_key:
        raise RuntimeError("API_KEY is not set in the scenario .env file.")
    if api_key.casefold() == "xxx":
        raise RuntimeError("Replace API_KEY=XXX in your local .env with the key supplied privately by the facilitator.")

    return OpenAI(
        api_key=api_key,
        base_url=f"{endpoint}/openai/v1",
    )


def run_agent_response(
    client: OpenAI,
    *,
    model: str,
    instructions: str,
    input_text: str,
    tools: list[dict] | None = None,
    tool_handlers: dict[str, Callable[..., str]] | None = None,
    reasoning_effort: Literal["low", "medium", "high"] | None = None,
    on_progress: Callable[[str], None] | None = None,
) -> str:
    """Run one response and complete any local function-tool calls."""
    request_options = {}
    if reasoning_effort is not None:
        request_options["reasoning"] = {"effort": reasoning_effort}
    response_input = input_text
    request_number = 0

    while True:
        request_number += 1
        if on_progress:
            on_progress(f"Model request {request_number}: waiting for {model}...")
        started = perf_counter()
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=response_input,
            tools=tools or [],
            **request_options,
        )
        if on_progress:
            on_progress(f"Model request {request_number} completed in {perf_counter() - started:.1f}s.")
        function_calls = [item for item in response.output if item.type == "function_call"]
        if not function_calls:
            return response.output_text

        outputs = []
        for item in function_calls:
            if on_progress:
                on_progress(f"Running tool: {item.name}")
            handler = (tool_handlers or {}).get(item.name)
            if handler is None:
                result = json.dumps({"error": f"Unknown tool '{item.name}'"})
            else:
                result = handler(**json.loads(item.arguments))
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result,
                }
            )

        response_input = outputs
        request_options["previous_response_id"] = response.id