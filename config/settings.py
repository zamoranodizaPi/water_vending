"""Application settings for the water vending machine."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets" / "images"
AUDIO_DIR = BASE_DIR / "assets" / "audio"
DB_PATH = BASE_DIR / "database" / "sales.db"
RUNTIME_CONFIG_PATH = BASE_DIR / "config" / "runtime_settings.json"

WINDOW_TITLE = "Agua Purificada Lupita"
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FULLSCREEN = True
COURTESY_LIGHT_TIMEOUT_MS = 15000
COIN_UART_PORT = "/dev/serial0"
COIN_UART_BAUDRATE = 115200
COIN_UART_POLL_MS = 50

PINS = {
    "water_valve": 17,
    "coin_pulse": 12,
    "rinse_valve": 22,
    "courtesy_light": 27,
    "ozone": 6,
    "uv_lamp": 26,
    "select_full": 21,
    "select_half": 20,
    "select_gallon": 16,
    "ok_input": 13,
    # "29" se tomó como pin fisico 29 del header, que corresponde a BCM5.
    "emergency_stop": 5,
    "led_select_full": 23,
    "led_select_half": 24,
    "led_select_gallon": 25,
    "led_ok": 8,
    "led_emergency": 7,
}

COIN_VALUE = 1.0
FILL_SECONDS_PER_LITER = 1.6
RINSE_SECONDS = 3
EMERGENCY_RATE_PER_LITER = 1.0

PRODUCTS = [
    {
        "id": "full_garrafon",
        "name": "Garrafón Completo",
        "volume_l": 19.0,
        "price": 12.0,
        "image": ASSETS_DIR / "garrafon_full.png",
    },
    {
        "id": "half_garrafon",
        "name": "Medio Garrafón",
        "volume_l": 10.0,
        "price": 8.0,
        "image": ASSETS_DIR / "garrafon_half.png",
    },
    {
        "id": "gallon",
        "name": "Galón",
        "volume_l": 3.8,
        "price": 5.0,
        "image": ASSETS_DIR / "gallon.png",
    },
]

DEFAULT_RUNTIME_CONFIG = {
    "precios": {
        "garrafon": 12.0,
        "medio": 8.0,
        "galon": 5.0,
    },
    "tiempo_por_litro": 1.6,
    "codigo": "1000",
}

LOGO_IMAGE = ASSETS_DIR / "logo.png"
COIN_IMAGE = ASSETS_DIR / "coins.png"
UPSIDE_DOWN_IMAGE = ASSETS_DIR / "garrafonbocaabajo.png"
UPRIGHT_IMAGE = ASSETS_DIR / "garrafonbocaarriba.png"
FILLING_GIF = ASSETS_DIR / "garrafonllenando.gif"
RINSING_GIF = ASSETS_DIR / "garrafonenjuagando.gif"
CHANGE_GIF = ASSETS_DIR / "recojasucambio.gif"
THANKS_GIF = ASSETS_DIR / "agradecimiento.png"

AUDIO_FILES = {
    "welcome": AUDIO_DIR / "01_bienvenida.wav",
    "coin_received": AUDIO_DIR / "02_moneda_recibida.wav",
    "credit_updated": AUDIO_DIR / "03_credito_actualizado.wav",
    "credit_insufficient": AUDIO_DIR / "04_credito_insuficiente.wav",
    "select_product": AUDIO_DIR / "05_seleccione_producto.wav",
    "press_ok": AUDIO_DIR / "06_presione_ok.wav",
    "starting_fill": AUDIO_DIR / "07_iniciando_llenado.wav",
    "filling": AUDIO_DIR / "08_llenando.wav",
    "seventy_five": AUDIO_DIR / "09_setenta_y_cinco.wav",
    "fill_complete": AUDIO_DIR / "10_llenado_completo.wav",
    "remove_container": AUDIO_DIR / "11_retirar_garrafon.wav",
    "nozzle_cleaning": AUDIO_DIR / "12_limpieza_boquilla.wav",
    "error": AUDIO_DIR / "13_error.wav",
    "out_of_service": AUDIO_DIR / "14_fuera_de_servicio.wav",
    "thanks": AUDIO_DIR / "15_gracias.wav",
}

ACCESS_CODE = DEFAULT_RUNTIME_CONFIG["codigo"]


def _sanitize_runtime_config(raw: dict | None) -> dict:
    config = deepcopy(DEFAULT_RUNTIME_CONFIG)
    if not isinstance(raw, dict):
        return config
    precios = raw.get("precios", {})
    if isinstance(precios, dict):
        for key in ("garrafon", "medio", "galon"):
            value = precios.get(key)
            if isinstance(value, (int, float)):
                config["precios"][key] = round(float(value), 2)
    tiempo = raw.get("tiempo_por_litro")
    if isinstance(tiempo, (int, float)):
        config["tiempo_por_litro"] = round(max(0.01, float(tiempo)), 2)
    codigo = raw.get("codigo")
    if isinstance(codigo, str) and len(codigo) == 4 and codigo.isdigit():
        config["codigo"] = codigo
    return config


def load_runtime_config() -> dict:
    if not RUNTIME_CONFIG_PATH.exists():
        save_runtime_config(DEFAULT_RUNTIME_CONFIG)
        return deepcopy(DEFAULT_RUNTIME_CONFIG)
    with RUNTIME_CONFIG_PATH.open("r", encoding="utf-8") as file:
        return _sanitize_runtime_config(json.load(file))


def save_runtime_config(config: dict) -> dict:
    sanitized = _sanitize_runtime_config(config)
    RUNTIME_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RUNTIME_CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(sanitized, file, indent=2, ensure_ascii=False)
    return sanitized


def apply_runtime_config(config: dict) -> None:
    global FILL_SECONDS_PER_LITER, ACCESS_CODE
    sanitized = _sanitize_runtime_config(config)
    PRODUCTS[0]["price"] = sanitized["precios"]["garrafon"]
    PRODUCTS[1]["price"] = sanitized["precios"]["medio"]
    PRODUCTS[2]["price"] = sanitized["precios"]["galon"]
    FILL_SECONDS_PER_LITER = sanitized["tiempo_por_litro"]
    ACCESS_CODE = sanitized["codigo"]


def get_runtime_config() -> dict:
    return {
        "precios": {
            "garrafon": float(PRODUCTS[0]["price"]),
            "medio": float(PRODUCTS[1]["price"]),
            "galon": float(PRODUCTS[2]["price"]),
        },
        "tiempo_por_litro": float(FILL_SECONDS_PER_LITER),
        "codigo": ACCESS_CODE,
    }


apply_runtime_config(load_runtime_config())
