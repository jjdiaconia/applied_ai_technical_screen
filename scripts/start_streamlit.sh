#!/usr/bin/env bash
set -euo pipefail

PORT_VALUE="${PORT:-8501}"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"
export STREAMLIT_SERVER_HEADLESS="true"

if command -v poetry >/dev/null 2>&1; then
  poetry install --only main --no-interaction --no-ansi --no-root
  poetry run streamlit run app.py \
    --server.address 0.0.0.0 \
    --server.port "$PORT_VALUE" \
    --browser.gatherUsageStats false
else
  python -m pip install --upgrade pip
  python -m pip install streamlit openai python-dotenv
  streamlit run app.py \
    --server.address 0.0.0.0 \
    --server.port "$PORT_VALUE" \
    --browser.gatherUsageStats false
fi
