# Challenge 0: Connect

Time: ~15 minutes

Connect the Call Center scenario to the shared workshop model. You do not need an Azure subscription, Azure CLI, or portal access.

## 1. Prepare Python

From the repository root:

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

=== "macOS or Linux"

    ```bash
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

## 2. Create Local Configuration

Copy [`workshop.env.template`](./workshop.env.template) to `callcenter/.env`. The shared endpoint and model deployment name are already filled in. Replace only `XXX` with the API key supplied privately by the facilitator:

```dotenv
API_KEY=XXX
```

Keep the endpoint and model lines unchanged. Edit only your local `.env`, not the public template. Never commit or post the API key, even partially masked. The repository ignores `.env` files.

## 3. Test the Connection

From the repository root:

```bash
python smoke_test.py callcenter
```

Success looks like:

```text
WORKSHOP_READY: callcenter can use model deployment '...'.
```

Continue to [Challenge 1: Build Agents](../challenge-1-build/README.md).