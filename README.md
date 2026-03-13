# Water Vending (Raspberry Pi)

Aplicación para máquina de llenado de agua en Raspberry Pi con interfaz táctil en PyQt5 y control por GPIO.

## Stack
- Python 3
- PyQt5
- gpiozero
- SQLite

## Estructura

```text
water_vending/
├── main.py
├── config.py
├── config.json
├── requirements.txt
├── ui/
│   ├── main_window.py
│   └── screens.py
├── hardware/
│   ├── gpio_inputs.py
│   └── valve_controller.py
├── database/
│   └── sales_db.py
└── systemd/
    └── water-vending.service
```

## Mapeo GPIO
- GPIO 12: pulsos del monedero
- GPIO 16: selección garrafón completo
- GPIO 20: selección medio garrafón
- GPIO 21: selección 1 galón
- GPIO 17: válvula de llenado
- GPIO 27: válvula de enjuague
- GPIO 25: selección de enjuague (toggle)
- GPIO 24: botón OK

## Precios en pantalla inicial
- Garrafón completo: **$12**
- Medio garrafón: **$8**
- 1 galón: **$5**

## Flujo operativo
1. El monedero agrega crédito por pulsos en GPIO 12.
2. El operador selecciona producto (GPIO 16/20/21).
3. Activa enjuague (GPIO 25).
4. Presiona OK (GPIO 24) para ejecutar enjuague por 2 segundos (GPIO 27).
5. Se indica en pantalla “voltear garrafón y presionar OK”.
6. Al presionar OK de nuevo inicia llenado (GPIO 17):
   - Garrafón completo: 20s
   - Medio garrafón: 10s
   - 1 galón: 5s
7. Se muestra progreso de llenado en barra azul.
8. Al finalizar aparece “Gracias por su compra!!!” durante 2 segundos y vuelve a la pantalla principal.

## Imagen de logo
Coloca la imagen del logo en `assets/images/lupita_logo.png` (ruta configurada por defecto en `config.json`).

## Instalación rápida (Raspberry Pi OS)

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip python3-pyqt5
cd /workspace/water_vending
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Configuración
Editar `config.json` para precios, tiempos y pines.

## Autostart (systemd)
Archivo de ejemplo: `systemd/water-vending.service`

## Troubleshooting
Si aparece `No module named PyQt5`:
```bash
source .venv/bin/activate
pip install -r requirements.txt
# o
sudo apt install -y python3-pyqt5
```
