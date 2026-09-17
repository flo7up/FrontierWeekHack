"""Shared API-key authentication for Microsoft Foundry model calls."""

import json
import os
from dataclasses import dataclass
from typing import Callable

from openai import OpenAI


@dataclass(frozen=True)
class ApiKeyAgent:
    """Local agent metadata for API-key-authenticated response calls."""

    name: str
    version: str = "api-key"


def create_foundry_client() -> OpenAI:
    endpoint = os.getenv("FOUNDRY_ENDPOINT", "").rstrip("/")
    api_key = os.getenv("API_KEY", "")

    if not endpoint:
        raise RuntimeError("FOUNDRY_ENDPOINT is not set in the scenario .env file.")
    if not api_key:
        raise RuntimeError("API_KEY is not set in the scenario .env file.")

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
) -> str:
    """Run one response and complete any local function-tool calls."""
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=input_text,
        tools=tools or [],
    )

    while True:
        function_calls = [item for item in response.output if item.type == "function_call"]
        if not function_calls:
            return response.output_text

        outputs = []
        for item in function_calls:
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

        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=outputs,
            tools=tools or [],
            previous_response_id=response.id,
        )