#!/bin/bash
set -euo pipefail

APP_USER="${APP_USER:-pi}"
APP_DIR="${APP_DIR:-/opt/water_vending}"
SERVICE_NAME="${SERVICE_NAME:-vending.service}"
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/7] Instalando dependencias del sistema"
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-pyqt5 pigpio git rsync

echo "[2/7] Habilitando pigpiod"
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

echo "[3/7] Copiando aplicación a ${APP_DIR}"
sudo mkdir -p "$APP_DIR"
sudo rsync -a --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'build' \
  --exclude 'dist' \
  --exclude '__pycache__' \
  "$ROOT_DIR"/ "$APP_DIR"/
sudo chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

echo "[4/7] Creando entorno virtual"
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/.venv"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "[5/7] Preparando directorios persistentes"
sudo -u "$APP_USER" mkdir -p "$APP_DIR/logs" "$APP_DIR/database" "$APP_DIR/config"
if [[ ! -f "$APP_DIR/deploy/vending_email.env" && -f "$APP_DIR/deploy/vending_email.env.example" ]]; then
  sudo -u "$APP_USER" cp "$APP_DIR/deploy/vending_email.env.example" "$APP_DIR/deploy/vending_email.env"
fi

echo "[6/7] Instalando servicio systemd"
sudo cp "$APP_DIR/systemd/vending.service" "/etc/systemd/system/${SERVICE_NAME}"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "[7/7] Instalación completada"
echo "Servicio activo: ${SERVICE_NAME}"
