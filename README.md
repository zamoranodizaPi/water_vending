# Lupita Agua Purificada - Control de Vending (Raspberry Pi 3B+)

Proyecto base para una máquina vending de agua en Raspberry Pi 3B+ (Bookworm), con UI HDMI **no táctil**, control por botones físicos, monedero por pulsos y automatización de válvulas/sensores.

## Características implementadas

- Arquitectura modular para servicios (`vending-core`, `coin-pulse`, `ui-kiosk`).
- Máquina de estados con reglas de seguridad.
- Mapeo de GPIO para:
  - Electroválvula de llenado.
  - Electroválvula de enjuague.
  - Sensor de flujo.
  - Sensor de puerta para luz interior.
  - Lámpara UV durante llenado.
  - Generador de ozono al finalizar.
  - Botonera física (completo/medio/galón/ok/enjuague/paro).
- Soporte de monedero por pulsos para monedas de 1/2/5/10.
- UI kiosko adaptada a pantalla 7" (sin interacción touch).
- Generación de imágenes HD basadas en la paleta del logo.

## Estructura

- `src/vending/`: lógica principal y servicios.
- `ui/`: interfaz kiosko.
- `assets/generated/`: fondos, iconografía y recursos visuales de alta resolución.
- `config/default.yaml`: configuración inicial de pines, precios y volúmenes.
- `scripts/generate_assets.py`: generador de recursos gráficos.

## Arranque local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_assets.py
uvicorn src.vending.main:app --reload
```

Luego abre `http://127.0.0.1:8000`.

## Nota sobre logo principal

La interfaz está preparada para usar `assets/logo_principal.svg` como logo principal. Por temas de licencia/origen del arte, en este commit se incluye un **placeholder** y recursos derivados de la paleta; sustituye `assets/logo_principal.svg` por el logo maestro final aprobado por marca.

## Probar en Raspberry Pi

Sigue la guía paso a paso en `docs/prueba_en_raspberry.md` para instalación, pruebas API, kiosko en Chromium, validación de hardware y servicio `systemd`.
