#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "No se encontró .venv/bin/python" >&2
  exit 1
fi

.venv/bin/python -m PyInstaller --clean -y water_vending.spec
