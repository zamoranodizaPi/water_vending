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
- GPIO 16: selección 1 galón
- GPIO 20: selección medio garrafón
- GPIO 21: selección garrafón completo
- GPIO 13: botón OK
- Pin físico 29 / GPIO 5: paro de emergencia
- GPIO 23: LED botón garrafón completo
- GPIO 24: LED botón medio garrafón
- GPIO 25: LED botón galón
- GPIO 8: LED botón OK
- GPIO 7: LED botón paro
- GPIO 17: válvula de llenado
- GPIO 22: válvula de enjuague
- GPIO 27: luz de cortesía
- GPIO 26: lámpara UV
- GPIO 6: ozono

## Precios en pantalla inicial
- Garrafón completo: **$12**
- Medio garrafón: **$8**
- 1 galón: **$5**

## Flujo operativo
1. El monedero agrega crédito por pulsos en GPIO 12.
2. El operador selecciona producto con botones físicos o pantalla.
3. Al completar crédito, parpadea suavemente el LED del producto disponible de mayor precio.
4. Al seleccionar producto, queda fijo su LED y parpadea el LED de OK cuando ya hay crédito suficiente.
5. El garrafón completo siempre ejecuta enjuague antes del llenado. Medio garrafón y galón no enjuagan.
6. Durante el llenado todos los LEDs se apagan, salvo el de paro de emergencia que parpadea.
7. En estado idle, cada minuto corre una secuencia de LEDs de 5 segundos para llamar la atención.
8. Tiempos de llenado:
   - Garrafón completo: 20s
   - Medio garrafón: 10s
   - 1 galón: 5s
9. Al finalizar, todos los LEDs hacen 3 parpadeos rápidos y la máquina vuelve a idle.

## Resolución objetivo
Interfaz adaptativa: escala automáticamente para la resolución de pantalla en uso (base recomendada 800 x 480).

## Imágenes de interfaz
Coloca las imágenes en:
- `assets/images/logo.png`
- `assets/images/background.png`

La UI usa `logo.png` en la esquina superior derecha y `background.png` como fondo principal.

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
