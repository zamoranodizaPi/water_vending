# Raspberry Pi Water Vending Machine

Software de máquina expendedora de agua para Raspberry Pi con pantalla táctil en modo kiosko.

## Stack técnico

- Python 3
- PyQt5 (interfaz táctil)
- gpiozero (control de relay)
- PySerial (aceptador de monedas)
- SQLite (registro de ventas)

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
│   ├── valve_controller.py
│   └── coin_acceptor.py
├── database/
│   └── sales_db.py
├── assets/
│   └── images/
└── systemd/
    └── water-vending.service
```

## Instalación en Raspberry Pi OS

1. Instalar dependencias del sistema:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv libqt5gui5 libqt5widgets5
```

2. Crear entorno virtual e instalar Python deps:

```bash
cd /opt/water_vending
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Configurar parámetros en `config.json`:

- `price_per_product`
- `valve_open_seconds`
- `relay_gpio_pin`
- `serial_port`

4. Ejecutar manualmente:

```bash
source .venv/bin/activate
python main.py
```

## Autostart con systemd

1. Copiar el servicio:

```bash
sudo cp systemd/water-vending.service /etc/systemd/system/water-vending.service
```

2. Ajustar rutas/usuario en el archivo de servicio según tu instalación.

3. Habilitar y arrancar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable water-vending.service
sudo systemctl start water-vending.service
```

4. Ver estado y logs:

```bash
sudo systemctl status water-vending.service
journalctl -u water-vending.service -f
```

## Notas de hardware

- Relay conectado al pin definido en `relay_gpio_pin`.
- Aceptador de monedas por USB serial (`/dev/ttyUSB0` típicamente).
- El parser serial acepta líneas como `1.0` o `COIN:5`.
- Preparado para integrar un aceptador de billetes agregando otro lector serial similar.
