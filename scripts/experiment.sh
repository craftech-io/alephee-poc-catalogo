#!/usr/bin/env bash
# scripts/experiment.sh — runs a version of the agent as a Langfuse experiment.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo "Missing .env: copy .env.example to .env and fill in the Langfuse keys" >&2
  exit 1
fi
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}"
PYTHONPATH=core/src exec uv run --env-file .env python -m catalog.experiment "$@"
