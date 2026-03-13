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

2. Clonar e instalar Python deps:

```bash
git clone <tu-repo> /opt/water_vending
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
- `coin_input_mode`: `serial_value` o `pulse`
- `coin_pulse_value`: valor de cada pulso (si usas `pulse`)

4. Ejecutar manualmente:

```bash
source .venv/bin/activate
python main.py
```

## Funcionamiento de pago y despacho

- El crédito aumenta automáticamente con cada evento del monedero.
- Cuando el crédito alcanza el precio configurado, el sistema **despacha automáticamente**.
- El despachado activa el relay por `valve_open_seconds`.
- Cada venta queda registrada en SQLite con:
  - `timestamp`
  - `product`
  - `price`
  - `payment_received`

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

## Futuro: aceptador de billetes

La arquitectura permite añadir un lector de billetes como otro módulo de `hardware/` que emita crédito al mismo flujo de la UI.
