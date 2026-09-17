"""Verify a workshop scenario can call the shared Foundry model."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from foundry_api import create_foundry_client


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"factory", "claims", "callcenter"}:
        raise SystemExit("Usage: python smoke_test.py <factory|claims|callcenter>")

    scenario = sys.argv[1]
    env_path = Path(__file__).resolve().parent / scenario / ".env"
    if not env_path.exists():
        raise SystemExit(f"Missing {env_path}. Complete Challenge 0 first.")

    load_dotenv(env_path)
    model = os.getenv("MODEL_DEPLOYMENT_NAME", "")
    if not model:
        raise SystemExit("MODEL_DEPLOYMENT_NAME is not set in the scenario .env file.")

    client = create_foundry_client()
    try:
        response = client.responses.create(
            model=model,
            input="Reply with exactly: WORKSHOP_READY",
        )
    finally:
        client.close()

    if response.output_text.strip() != "WORKSHOP_READY":
        raise SystemExit("The model responded, but the smoke-test output was unexpected.")
    print(f"WORKSHOP_READY: {scenario} can use model deployment '{model}'.")


if __name__ == "__main__":
    main()