#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "No se encontró .venv/bin/python" >&2
  exit 1
fi

PYINSTALLER_CONFIG_DIR="${PYINSTALLER_CONFIG_DIR:-/tmp/pyinstaller}" \
.venv/bin/python -m PyInstaller \
  --clean \
  -y \
  --onefile \
  --windowed \
  --name water_vending \
  --specpath /tmp/pyinstaller-spec \
  --paths "$ROOT_DIR" \
  --add-data "$ROOT_DIR/assets:assets" \
  --add-data "$ROOT_DIR/config/runtime_settings.json:config" \
  --add-data "$ROOT_DIR/config.json:." \
  --add-data "$ROOT_DIR/VERSION.txt:." \
  "$ROOT_DIR/main.py"
