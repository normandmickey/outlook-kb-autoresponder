# Outlook Autoresponder

Standalone Outlook autoresponder with knowledge-base retrieval.

## V1 scope
- poll Outlook inbox via Microsoft Graph
- load markdown/text knowledge-base files
- retrieve relevant KB snippets with simple search
- generate a grounded reply draft with your own OpenAI-compatible LLM
- create an Outlook reply draft (safe default)
- record processed messages locally to avoid duplicate drafting

## Setup
1. Copy `.env.example` to `.env`
2. Fill in Microsoft Graph credentials and your local LLM settings
3. Put KB files in `knowledge_base/`
4. Create a venv and install deps:
   - `./scripts/bootstrap_venv.sh`
5. Run once:
   - default instance: `./.venv/bin/python scripts/run_once.py`
   - named instance: `./.venv/bin/python scripts/run_once.py --instance support`

## Required Microsoft Graph permissions
Application permissions are the cleanest first pass for this project:
- `Mail.Read`
- `Mail.ReadWrite`

Then grant admin consent in Azure.

## Notes
- V1 is draft-first only
- sensitive topics are still drafted, not auto-sent
- retrieval is simple text matching for now
- processed message IDs are stored in `data/state.json`

## Multiple mailboxes
Use one instance per mailbox under `instances/<name>/`. Each instance can have its own:
- `.env`
- `knowledge_base/`
- `data/state.json`

Example:
- `instances/support/.env`
- `instances/support/knowledge_base/`
- `instances/support/data/`

Run a named mailbox instance with:
- `./.venv/bin/python scripts/run_once.py --instance support`
- `./.venv/bin/python scripts/run_once.py --instance sales`

## Continuous polling
Run one mailbox continuously:
- `./.venv/bin/python scripts/run_once.py --instance support --loop`

Run all configured instances continuously:
- `./.venv/bin/python scripts/run_once.py --all-instances --loop`

Override polling interval:
- `./.venv/bin/python scripts/run_once.py --instance support --loop --poll-seconds 60`

## Run all configured instances once
- `./.venv/bin/python scripts/run_once.py --all-instances`

## systemd templates
Sample unit files are included in `systemd/`:
- `systemd/outlook-autoresponder@.service`
- `systemd/outlook-autoresponder-all.service`

Example usage after installing the repo to `/opt/outlook-kb-autoresponder`:
- `sudo cp systemd/outlook-autoresponder@.service /etc/systemd/system/`
- `sudo systemctl daemon-reload`
- `sudo systemctl enable --now outlook-autoresponder@support`

Or run all mailboxes in one service:
- `sudo cp systemd/outlook-autoresponder-all.service /etc/systemd/system/`
- `sudo systemctl daemon-reload`
- `sudo systemctl enable --now outlook-autoresponder-all`

## Installer
Install to `/opt/outlook-kb-autoresponder` by default:
```bash
./scripts/install.sh
```

Install to a custom path:
```bash
./scripts/install.sh /srv/outlook-kb-autoresponder
```

## Dry-run mode
Preview generated replies without creating Outlook drafts and without marking messages as processed:
```bash
./.venv/bin/python scripts/run_once.py --instance support --dry-run
```

Dry-run all configured instances:
```bash
./.venv/bin/python scripts/run_once.py --all-instances --dry-run
```

## Per-instance logs
Each instance now writes logs to:
- `logs/<instance>.log`

Examples:
- `logs/support.log`
- `logs/sales.log`

Dry-run previews are also written into those logs.

## Local no-Outlook reply testing
You can test retrieval and reply quality without connecting to Outlook.

Using a JSON fixture:
```bash
./.venv/bin/python scripts/test_reply.py --instance support --input samples/pricing_email.json
```

Using inline arguments:
```bash
./.venv/bin/python scripts/test_reply.py \
  --instance support \
  --subject "Refund question" \
  --from-name "Bob Smith" \
  --from-address "bob@example.com" \
  --body "I was charged twice. Can you help?"
```

The test output shows:
- selected KB hits
- decision/confidence
- final drafted reply

Sample fixtures are included in `samples/`.

## Self-signed certificates / local TLS
If your in-house LLM endpoint uses a self-signed certificate, you have two options.

### Safer option
Point the app at a CA bundle or PEM file that trusts your cert:
```bash
LLM_CA_BUNDLE=/path/to/your-ca.pem
```

### Local testing shortcut
Disable TLS verification only for local testing:
```bash
LLM_VERIFY_SSL=false
```

## Windows / direct script note
If Python cannot find the package when running the script directly, either re-run the bootstrap script or use module-style execution:
```bash
python -m scripts.test_reply --instance support --input samples/pricing_email.json
python -m scripts.run_once --instance support --dry-run
```

The bootstrap script also installs the project in editable mode.
