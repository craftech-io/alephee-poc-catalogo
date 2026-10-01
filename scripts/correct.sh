#!/usr/bin/env bash
# scripts/correct.sh — loads a correction from the catalog team into DynamoDB (stage warroom).
# Only affects attributes the agent decides (worklist.to_decide): a value already resolved
# by an exact match against the channel domain never looks at a correction.
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}"
PYTHONPATH=core/src exec uv run python -m catalog.correct "$@"
