#!/usr/bin/env bash
set -euo pipefail

PORT_VALUE="${PORT:-8501}"

if command -v poetry >/dev/null 2>&1; then
  poetry install --no-interaction --no-ansi
  poetry run streamlit run app.py \
    --server.address 0.0.0.0 \
    --server.port "$PORT_VALUE" \
    --browser.gatherUsageStats false
else
  python -m pip install --upgrade pip
  python -m pip install streamlit openai python-dotenv pytest
  streamlit run app.py \
    --server.address 0.0.0.0 \
    --server.port "$PORT_VALUE" \
    --browser.gatherUsageStats false
fi
