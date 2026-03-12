# Cómo probar el proyecto en tu Raspberry Pi 3B+ (Bookworm)

Esta guía es para validar el sistema **paso a paso** en hardware real.

## 1) Preparación del sistema

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip chromium-browser git
```

Opcional (recomendado para GPIO en Bookworm):

```bash
sudo apt install -y python3-gpiozero python3-lgpio
```

## 2) Clonar proyecto y crear entorno

```bash
git clone <URL_DE_TU_REPO> water_vending
cd water_vending
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Generar assets de la interfaz

```bash
python3 scripts/generate_assets.py
```

## 4) Levantar la app localmente

```bash
uvicorn src.vending.main:app --host 0.0.0.0 --port 8000
```

Desde la misma Raspberry abre:

- `http://127.0.0.1:8000` (UI kiosko)
- `http://127.0.0.1:8000/api/status` (estado JSON)

## 5) Prueba funcional rápida (sin GPIO real)

En otra terminal:

```bash
curl -X POST http://127.0.0.1:8000/api/select/gallon
curl -X POST http://127.0.0.1:8000/api/coin/5
curl -X POST http://127.0.0.1:8000/api/coin/5
curl -X POST http://127.0.0.1:8000/api/start
curl -X POST http://127.0.0.1:8000/api/complete
curl -X POST http://127.0.0.1:8000/api/ack
curl http://127.0.0.1:8000/api/status
```

Debes observar transición de estados: `IDLE -> WAITING_COIN -> CREDIT_READY -> FILLING -> COMPLETE -> IDLE`.

## 6) Validar botón de emergencia

```bash
curl -X POST http://127.0.0.1:8000/api/emergency
curl http://127.0.0.1:8000/api/status
```

Verifica que `state` sea `EMERGENCY_STOP` y actuadores apagados.

## 7) Probar en pantalla HDMI 7" en modo kiosko

Con la app corriendo, ejecuta Chromium en kiosko:

```bash
chromium-browser --kiosk --incognito --noerrdialogs --disable-infobars http://127.0.0.1:8000
```

## 8) Prueba eléctrica por etapas (recomendado)

1. **Sin carga**: solo LEDs testigo en salidas (sin conectar válvulas/UV/ozono).
2. **Con relés/SSR**: probar activación de cada salida individual.
3. **Con agua real**: primero enjuague, luego llenado corto.
4. **Seguridad**: probar paro de emergencia durante llenado.

## 9) Mapeo sugerido de pruebas por hardware

- Puerta abierta/cerrada: validar luz interior (`interior_light`).
- Llenado: validar `fill_valve=True` y `uv_lamp=True`.
- Enjuague: validar `rinse_valve=True` y `uv_lamp=False`.
- Fin de llenado: validar `ozone_machine=True` tras `/api/complete`.
- Monedero pulso: validar pulsos 1/2/5/10 y acumulación de crédito.

## 10) Correr tests unitarios en la Raspberry

```bash
python3 -m pytest -q
```

## 11) Arranque automático con systemd (opcional)

Archivo `/etc/systemd/system/lupita-vending.service`:

```ini
[Unit]
Description=Lupita Vending API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/water_vending
ExecStart=/home/pi/water_vending/.venv/bin/uvicorn src.vending.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable lupita-vending
sudo systemctl start lupita-vending
sudo systemctl status lupita-vending
```
