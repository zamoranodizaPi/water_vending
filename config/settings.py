"""Application settings for the water vending machine."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets" / "images"
DB_PATH = BASE_DIR / "database" / "sales.db"

WINDOW_TITLE = "Agua Purificada Lupita"
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FULLSCREEN = True
COURTESY_LIGHT_TIMEOUT_MS = 15000

PINS = {
    "water_valve": 17,
    "coin_input": 27,
    "coin_pulse": 12,
    "rinse_valve": 22,
    "courtesy_light": 5,
    "ozone": 6,
    "uv_lamp": 13,
    "select_full": 21,
    "select_half": 20,
    "select_gallon": 16,
}

COIN_VALUE = 1.0
FILL_SECONDS_PER_LITER = 1.6
RINSE_SECONDS = 3

PRODUCTS = [
    {
        "id": "full_garrafon",
        "name": "Garrafón Completo",
        "volume_l": 20.0,
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
