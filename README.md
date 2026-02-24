# AI Technical Screen - Thoughtful AI Support Agent

A bootstrapped **Python Poetry** project with a **Streamlit** chat UI for a customer support AI agent.

## Features

- Conversational chat interface using Streamlit
- Retrieval from a hardcoded Thoughtful AI Q&A dataset
- Confidence-scored matching for relevant predefined answers
- Fallback to LLM responses (OpenAI) for non-dataset questions
- Graceful error handling for empty input and fallback failures

## Tech Stack

- Python 3.11+
- Poetry
- Streamlit
- OpenAI Python SDK (optional fallback)

## Local Setup

1. Install Poetry (if needed):
   - https://python-poetry.org/docs/#installation
2. Install dependencies:

```bash
poetry install
```

3. (Optional) enable LLM fallback by creating `.env`:

```bash
cp .env.example .env
# then set OPENAI_API_KEY in .env
```

## Run Locally

```bash
poetry run streamlit run app.py
```

Open the local URL shown in terminal (usually http://localhost:8501).

You can also use the shared startup script:

```bash
bash scripts/start_streamlit.sh
```

## Test

```bash
poetry run pytest -q
```

Run integration tests:

```bash
poetry run pytest -q -m integration
```

Run live OpenAI integration test (real API call, opt-in):

```bash
export OPENAI_API_KEY="<your_key>"
export RUN_LIVE_OPENAI_TESTS=1
poetry run pytest -q -m live_openai
```

Install Playwright browser once (so default test suite can run UI E2E test):

```bash
poetry run playwright install chromium
```

Run only UI E2E test:

```bash
poetry run pytest -q -m e2e_ui
```

## Replit Setup

This repo includes Replit config files:

- `.replit`
- `replit.nix`
- `scripts/start_streamlit.sh`

### Deploy on Replit

1. Push this repo to GitHub.
2. In Replit, choose **Create Repl** -> **Import from GitHub**.
3. Add secrets in Replit:
   - `OPENAI_API_KEY` (optional, enables LLM fallback)
   - `OPENAI_MODEL` (optional, default is `gpt-4o-mini`)
4. Run the Repl. It will execute `bash scripts/start_streamlit.sh`.

The script automatically:

- installs only runtime dependencies (`--only main`) with Poetry when available
- binds Streamlit to `0.0.0.0`
- uses Replit's `$PORT` (or `8501` locally)

### Auto-redeploy on Git push

This repo includes [replit-redeploy.yml](.github/workflows/replit-redeploy.yml), which can auto-trigger Replit deployments after pushes to `main`.

One-time setup:

1. In Replit Deployments, create/get a **Deploy Hook URL** for your app.
2. In GitHub repo settings, add secret `REPLIT_DEPLOY_HOOK_URL` with that hook URL.
3. Push to `main`.

After that, each push to `main` triggers a redeploy in Replit automatically.

## Project Structure

- `app.py` - Streamlit chat application
- `thoughtful_agent/agent.py` - Core orchestration (retrieve or fallback)
- `thoughtful_agent/retriever.py` - Hardcoded knowledge retrieval logic
- `thoughtful_agent/llm_fallback.py` - Optional OpenAI fallback responses
- `thoughtful_agent/data/qa.json` - Predefined Thoughtful AI Q&A data

## Notes

- If `OPENAI_API_KEY` is not set, fallback returns a helpful guidance response.
- You can tune retrieval strictness by adjusting `threshold` in `ThoughtfulSupportAgent`.
