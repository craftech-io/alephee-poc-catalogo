#!/usr/bin/env bash
# Carga una corrección en la memoria de la V3. Ver core/src/catalogo/corregir.py.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH=core/src exec uv run python -m catalogo.corregir "$@"
