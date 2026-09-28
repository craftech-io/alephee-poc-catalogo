#!/usr/bin/env bash
# Corre el agente de catálogo sobre el dataset (modo batch). Ver core/src/catalogo/correr.py.
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PROFILE="${AWS_PROFILE:-sandbox}" AWS_REGION="${AWS_REGION:-us-east-1}"
PYTHONPATH=core/src exec uv run python -m catalogo.correr "$@"
