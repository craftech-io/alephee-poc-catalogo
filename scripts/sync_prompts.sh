#!/usr/bin/env bash
# scripts/sync_prompts.sh — uploads the prompt seed to Langfuse if it does not exist yet.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo "Missing .env: copy .env.example to .env and fill in the Langfuse keys" >&2
  exit 1
fi
PYTHONPATH=core/src exec uv run --env-file .env python -c \
  "from catalog.prompts import PROMPT_NAME, sync_seed; from catalog.tracing import langfuse_client; print('created' if sync_seed(PROMPT_NAME, langfuse_client()) else 'already existed')"
