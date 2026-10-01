#!/usr/bin/env bash
# scripts/sync_prompts.sh — sube a Langfuse la semilla del prompt si todavía no existe.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH=core/src exec uv run --env-file .env python -c \
  "from catalog.prompts import PROMPT_NAME, sync_seed; from catalog.tracing import langfuse_client; print('creado' if sync_seed(PROMPT_NAME, langfuse_client()) else 'ya existía')"
