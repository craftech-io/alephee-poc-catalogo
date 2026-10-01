#!/usr/bin/env bash
# scripts/e2e.sh — end-to-end tests against Bedrock, DynamoDB and the deployed chat (stage warroom).
#
# API_URL must point to the deployed BFF (the `Chat` output printed by `sst deploy`):
# `.sst/outputs.json` from this deploy has no `Chat` key, so pass it explicitly, e.g.:
#   API_URL=<Function URL del BFF (salida Chat de sst deploy)> scripts/e2e.sh
# CHAT_HMAC_SECRET comes from .env through `uv run --env-file .env`.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo "Missing .env: copy .env.example to .env and fill in the keys" >&2
  exit 1
fi
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}" RUN_E2E=1
exec uv run --env-file .env pytest core/tests/e2e -v "$@"
