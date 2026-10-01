#!/usr/bin/env bash
# scripts/correct.sh — loads a correction from the catalog team into DynamoDB (stage warroom).
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}"
PYTHONPATH=core/src exec uv run python -m catalog.correct "$@"
