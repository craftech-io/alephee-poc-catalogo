#!/usr/bin/env bash
# scripts/map.sh — maps one SKU and prints the listing JSON as the agent delivers it.
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}"
PYTHONPATH=core/src exec uv run python -m catalog.map_one "$@"
