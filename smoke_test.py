"""Verify a workshop scenario can call the shared Foundry model."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, AuthenticationError, NotFoundError, PermissionDeniedError, RateLimitError

from foundry_api import create_foundry_client

WORKSHOP_ROOT = Path(__file__).resolve().parent


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"factory", "claims", "callcenter"}:
        raise SystemExit("Usage: python smoke_test.py <factory|claims|callcenter>")

    scenario = sys.argv[1]
    env_path = WORKSHOP_ROOT / scenario / ".env"
    if not env_path.is_file():
        raise SystemExit(f"Missing {scenario}/.env. Complete Connect step 3; make sure the filename is .env, not .env.txt.")

    load_dotenv(env_path, override=True)
    model = os.getenv("MODEL_DEPLOYMENT_NAME", "")
    if not model:
        raise SystemExit("MODEL_DEPLOYMENT_NAME is not set in the scenario .env file.")

    try:
        with create_foundry_client() as client:
            print(f"Checking the {scenario} connection. This can take up to 30 seconds...")
            response = client.with_options(timeout=30.0, max_retries=0).responses.create(
                model=model,
                input="Reply with exactly: WORKSHOP_READY",
            )
    except RuntimeError as error:
        raise SystemExit(str(error)) from None
    except AuthenticationError:
        raise SystemExit("The API key was not accepted (401). Ask the facilitator for the current key; do not post your .env file.") from None
    except PermissionDeniedError:
        raise SystemExit("Access was denied (403). Ask the facilitator to check the shared resource's access settings.") from None
    except NotFoundError:
        raise SystemExit("Endpoint or deployment not found (404). Check the two public values against the workshop template.") from None
    except RateLimitError:
        raise SystemExit("The shared model is busy or has reached a limit (429). Wait one minute, retry once, then ask the facilitator.") from None
    except APIConnectionError:
        raise SystemExit("Could not reach the model in time. Check your internet connection and ask the facilitator about network restrictions; do not disable security controls.") from None
    except APIStatusError as error:
        raise SystemExit(f"The model service returned HTTP {error.status_code}. Tell the facilitator this status, not your API key.") from None

    if not response.output_text.strip():
        raise SystemExit("Connected, but the model returned no text. Ask the facilitator to check the deployment.")
    print(f"WORKSHOP_READY: {scenario} can use model deployment '{model}'.")


if __name__ == "__main__":
    main()