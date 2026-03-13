"""Application settings for the water vending machine."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets" / "images"
DB_PATH = BASE_DIR / "database" / "sales.db"

WINDOW_TITLE = "Purified Water Vending"
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FULLSCREEN = True
COURTESY_LIGHT_TIMEOUT_MS = 15000

PINS = {
    "water_valve": 17,
    "coin_input": 27,
    "rinse_valve": 22,
    "courtesy_light": 5,
    "ozone": 6,
    "uv_lamp": 13,
}

COIN_VALUE = 1.0
FILL_SECONDS_PER_LITER = 1.6

PRODUCTS = [
    {
        "id": "full_garrafon",
        "name": "Full Garrafón",
        "volume_l": 20.0,
        "price": 25.0,
        "image": ASSETS_DIR / "garrafon_full.png",
    },
    {
        "id": "half_garrafon",
        "name": "Half Garrafón",
        "volume_l": 10.0,
        "price": 14.0,
        "image": ASSETS_DIR / "garrafon_half.png",
    },
    {
        "id": "gallon",
        "name": "Gallon",
        "volume_l": 3.8,
        "price": 6.0,
        "image": ASSETS_DIR / "gallon.png",
    },
]

LOGO_IMAGE = ASSETS_DIR / "logo.png"
COIN_IMAGE = ASSETS_DIR / "coins.png"
