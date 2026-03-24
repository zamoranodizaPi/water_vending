"""Application settings for the water vending machine."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets" / "images"
AUDIO_DIR = BASE_DIR / "assets" / "audio"
DB_PATH = BASE_DIR / "database" / "sales.db"

WINDOW_TITLE = "Agua Purificada Lupita"
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FULLSCREEN = True
COURTESY_LIGHT_TIMEOUT_MS = 15000

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

LOGO_IMAGE = ASSETS_DIR / "logo.png"
COIN_IMAGE = ASSETS_DIR / "coins.png"
UPSIDE_DOWN_IMAGE = ASSETS_DIR / "garrafonbocaabajo.png"
UPRIGHT_IMAGE = ASSETS_DIR / "garrafonbocaarriba.png"
FILLING_GIF = ASSETS_DIR / "garrafonllenando.gif"
RINSING_GIF = ASSETS_DIR / "garrafonenjuagando.gif"
CHANGE_GIF = ASSETS_DIR / "recojasucambio.gif"
THANKS_GIF = ASSETS_DIR / "agradecimiento.gif"

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
