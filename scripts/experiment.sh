#!/usr/bin/env bash
# scripts/experiment.sh — corre una versión del agente como experimento de Langfuse.
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}"
PYTHONPATH=core/src exec uv run --env-file .env python -m catalog.experiment "$@"
