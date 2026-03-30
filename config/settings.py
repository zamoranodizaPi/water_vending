"""Application settings for the water vending machine."""
from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path

from app.paths import data_root, resource_root

RESOURCE_DIR = resource_root()
DATA_DIR = data_root()
BASE_DIR = DATA_DIR
LOG_DIR = DATA_DIR / "logs"
ASSETS_DIR = RESOURCE_DIR / "assets" / "images"
AUDIO_DIR = RESOURCE_DIR / "assets" / "audio"
DB_PATH = DATA_DIR / "database" / "sales.db"
RUNTIME_CONFIG_PATH = DATA_DIR / "config" / "runtime_settings.json"

WINDOW_TITLE = "Agua Purificada Lupita"
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FULLSCREEN = True
COURTESY_LIGHT_TIMEOUT_MS = 15000
AVAILABLE_THEMES = (
    "arcade_mario",
    "blue_ocean",
    "yellow_industrial",
    "green_nature",
    "sunset_energy",
    "purple_modern",
    "black_gold",
)
AVAILABLE_MODES = ("light", "dark")
LEGACY_THEME_ALIASES = {
    "pink": "sunset_energy",
    "blue": "blue_ocean",
}

PINS = {
    "water_valve": 17,
    "coin_pulse": 18,
    "service_level": 12,
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
RINSE_LITERS = round(RINSE_SECONDS / FILL_SECONDS_PER_LITER, 2)
EMERGENCY_RATE_PER_LITER = 1.0

PRODUCTS = [
    {
        "id": "full_garrafon",
        "name": "Garrafón Completo",
        "volume_l": 19.0,
        "price": 12.0,
        "fill_time_s": round(19.0 * FILL_SECONDS_PER_LITER, 2),
        "image": ASSETS_DIR / "garrafon_full.png",
    },
    {
        "id": "half_garrafon",
        "name": "Medio Garrafón",
        "volume_l": 10.0,
        "price": 8.0,
        "fill_time_s": round(10.0 * FILL_SECONDS_PER_LITER, 2),
        "image": ASSETS_DIR / "garrafon_half.png",
    },
    {
        "id": "gallon",
        "name": "Galón",
        "volume_l": 3.8,
        "price": 5.0,
        "fill_time_s": round(3.8 * FILL_SECONDS_PER_LITER, 2),
        "image": ASSETS_DIR / "gallon.png",
    },
]

DEFAULT_RUNTIME_CONFIG = {
    "precios": {
        "garrafon": 12.0,
        "medio": 8.0,
        "galon": 5.0,
    },
    "nombres": {
        "garrafon": "Garrafón Completo",
        "medio": "Medio Garrafón",
        "galon": "Galón",
    },
    "volumenes": {
        "garrafon": 19.0,
        "medio": 10.0,
        "galon": 3.8,
    },
    "tiempos_llenado": {
        "garrafon": round(19.0 * FILL_SECONDS_PER_LITER, 2),
        "medio": round(10.0 * FILL_SECONDS_PER_LITER, 2),
        "galon": round(3.8 * FILL_SECONDS_PER_LITER, 2),
    },
    "tiempo_por_litro": 1.6,
    "litros_por_enjuague": round(RINSE_SECONDS / FILL_SECONDS_PER_LITER, 2),
    "codigo": "1000",
    "codigo_auditoria": "2000",
    "tema": "sunset_energy",
    "modo": "light",
    "audio_muted": False,
    "titulo": "Agua Purificada Lupita",
    "eslogan": "pureza y bendicion en cada gota",
    "nombre_sistema": "Vending 1",
    "contacto": {
        "correo": "zamoranodiza@hotmail.com",
        "telefono": "7771033646",
    },
}

LOGO_IMAGE = ASSETS_DIR / "logo.png"
COIN_IMAGE = ASSETS_DIR / "coins.png"
UPSIDE_DOWN_IMAGE = ASSETS_DIR / "garrafonbocaabajo.png"
UPRIGHT_IMAGE = ASSETS_DIR / "garrafonbocaarriba.png"
FILLING_GIF = ASSETS_DIR / "garrafonllenando.gif"
RINSING_GIF = ASSETS_DIR / "garrafonenjuagando.gif"
CHANGE_GIF = ASSETS_DIR / "recojasucambio.gif"
THANKS_GIF = ASSETS_DIR / "agradecimiento.png"
SORRY_IMAGE = ASSETS_DIR / "losentimos.png"

AUDIO_FILES = {
    "welcome": AUDIO_DIR / "bienvenida.mp3",
    "credit_received": AUDIO_DIR / "credito_recibido.mp3",
    "credit_insufficient": AUDIO_DIR / "credito_insuficieinte.mp3",
    "select_product": AUDIO_DIR / "seleccione_producto.mp3",
    "selected_product": AUDIO_DIR / "selecciono_producto.mp3",
    "place_container": AUDIO_DIR / "coloque_su_garrafon.mp3",
    "place_container_fill": AUDIO_DIR / "coloque_su_garrafon_llenado.mp3",
    "press_ok": AUDIO_DIR / "presione_ok.mp3",
    "remove_container": AUDIO_DIR / "retire_garrafon.mp3",
    "remove_change": AUDIO_DIR / "retire_su_cambio.mp3",
    "thanks": AUDIO_DIR / "agradecimiento.mp3",
    "product_full_garrafon": AUDIO_DIR / "garrafon_completo.mp3",
    "product_half_garrafon": AUDIO_DIR / "10_litros.mp3",
    "product_gallon": AUDIO_DIR / "galon.mp3",
    "garrafon_boca_abajo": AUDIO_DIR / "garrafon_boca_abajo.mp3",
    "amount_5": AUDIO_DIR / "cinco_pesos.mp3",
    "amount_8": AUDIO_DIR / "ocho_pesos.mp3",
    "amount_10": AUDIO_DIR / "diez_pesos.mp3",
    "amount_12": AUDIO_DIR / "doce_pesos.mp3",
    "amount_15": AUDIO_DIR / "quince_pesos.mp3",
    "amount_20": AUDIO_DIR / "veinte_pesos.mp3",
}

ACCESS_CODE = DEFAULT_RUNTIME_CONFIG["codigo"]
AUDIT_CODE = DEFAULT_RUNTIME_CONFIG["codigo_auditoria"]
AUDIT_RESET_CODE = "3000"
UI_THEME = DEFAULT_RUNTIME_CONFIG["tema"]
UI_MODE = DEFAULT_RUNTIME_CONFIG["modo"]
AUDIO_MUTED = DEFAULT_RUNTIME_CONFIG["audio_muted"]
BRAND_TITLE = DEFAULT_RUNTIME_CONFIG["titulo"]
BRAND_TAGLINE = DEFAULT_RUNTIME_CONFIG["eslogan"]
SYSTEM_NAME = DEFAULT_RUNTIME_CONFIG["nombre_sistema"]
CONTACT_EMAIL = DEFAULT_RUNTIME_CONFIG["contacto"]["correo"]
CONTACT_PHONE = DEFAULT_RUNTIME_CONFIG["contacto"]["telefono"]
SMTP_HOST = os.getenv("VENDING_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("VENDING_SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("VENDING_SMTP_USERNAME", "zamoranodiza@gmail.com")
SMTP_PASSWORD = os.getenv("VENDING_SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("VENDING_SMTP_FROM", SMTP_USERNAME)
SMTP_USE_TLS = os.getenv("VENDING_SMTP_USE_TLS", "1") != "0"
IMAP_HOST = os.getenv("VENDING_IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("VENDING_IMAP_PORT", "993"))
IMAP_USERNAME = os.getenv("VENDING_IMAP_USERNAME", SMTP_USERNAME)
IMAP_PASSWORD = os.getenv("VENDING_IMAP_PASSWORD", SMTP_PASSWORD)
IMAP_USE_SSL = os.getenv("VENDING_IMAP_USE_SSL", "1") != "0"
AUDIT_EMAIL_BODY_KEYWORD = (os.getenv("VENDING_AUDIT_EMAIL_BODY_KEYWORD", "auditorias") or "auditorias").strip().lower()
AUDIT_EMAIL_POLL_MS = max(10000, int(os.getenv("VENDING_AUDIT_EMAIL_POLL_MS", "60000")))
AUDIT_EMAIL_INBOX = os.getenv("VENDING_AUDIT_EMAIL_INBOX", "INBOX")
_AUTHORIZED_AUDIT_EMAILS_RAW = os.getenv("VENDING_AUDIT_EMAILS", "")


def authorized_audit_emails() -> tuple[str, ...]:
    allowed: list[str] = []
    for candidate in (
        CONTACT_EMAIL,
        SMTP_USERNAME,
        *[part.strip() for part in _AUTHORIZED_AUDIT_EMAILS_RAW.split(",")],
    ):
        cleaned = (candidate or "").strip().lower()
        if cleaned and cleaned not in allowed:
            allowed.append(cleaned)
    return tuple(allowed)


def _sanitize_runtime_config(raw: dict | None) -> dict:
    config = deepcopy(DEFAULT_RUNTIME_CONFIG)
    manual_fill_keys: set[str] = set()
    if not isinstance(raw, dict):
        return config
    precios = raw.get("precios", {})
    if isinstance(precios, dict):
        for key in ("garrafon", "medio", "galon"):
            value = precios.get(key)
            if isinstance(value, (int, float)):
                config["precios"][key] = round(float(value), 2)
    nombres = raw.get("nombres", {})
    if isinstance(nombres, dict):
        for key in ("garrafon", "medio", "galon"):
            value = nombres.get(key)
            if isinstance(value, str):
                cleaned = value.strip()
                if cleaned:
                    config["nombres"][key] = cleaned[:18]
    volumenes = raw.get("volumenes", {})
    if isinstance(volumenes, dict):
        for key in ("garrafon", "medio", "galon"):
            value = volumenes.get(key)
            if isinstance(value, (int, float)):
                config["volumenes"][key] = round(max(0.1, float(value)), 2)
    tiempos_llenado = raw.get("tiempos_llenado", {})
    if isinstance(tiempos_llenado, dict):
        for key in ("garrafon", "medio", "galon"):
            value = tiempos_llenado.get(key)
            if isinstance(value, (int, float)):
                config["tiempos_llenado"][key] = round(max(0.1, float(value)), 2)
                manual_fill_keys.add(key)
    tiempo = raw.get("tiempo_por_litro")
    if isinstance(tiempo, (int, float)):
        config["tiempo_por_litro"] = round(max(0.01, float(tiempo)), 2)
    litros_enjuague = raw.get("litros_por_enjuague")
    if isinstance(litros_enjuague, (int, float)):
        config["litros_por_enjuague"] = round(max(0.1, float(litros_enjuague)), 2)
    codigo = raw.get("codigo")
    if isinstance(codigo, str) and len(codigo) == 4 and codigo.isdigit():
        config["codigo"] = codigo
    codigo_auditoria = raw.get("codigo_auditoria")
    if isinstance(codigo_auditoria, str) and len(codigo_auditoria) == 4 and codigo_auditoria.isdigit():
        config["codigo_auditoria"] = codigo_auditoria
    tema = raw.get("tema") or raw.get("theme")
    if isinstance(tema, str):
        cleaned = LEGACY_THEME_ALIASES.get(tema.strip().lower(), tema.strip().lower())
        if cleaned in AVAILABLE_THEMES:
            config["tema"] = cleaned
    modo = raw.get("modo") or raw.get("mode")
    if isinstance(modo, str):
        cleaned = modo.strip().lower()
        if cleaned in AVAILABLE_MODES:
            config["modo"] = cleaned
    audio_muted = raw.get("audio_muted")
    if isinstance(audio_muted, bool):
        config["audio_muted"] = audio_muted
    titulo = raw.get("titulo")
    if isinstance(titulo, str):
        cleaned = titulo.strip()
        if cleaned:
            config["titulo"] = cleaned[:40]
    eslogan = raw.get("eslogan")
    if isinstance(eslogan, str):
        cleaned = eslogan.strip()
        if cleaned:
            config["eslogan"] = cleaned[:56]
    nombre_sistema = raw.get("nombre_sistema")
    if isinstance(nombre_sistema, str):
        cleaned = nombre_sistema.strip()
        if cleaned:
            config["nombre_sistema"] = cleaned[:20]
    contacto = raw.get("contacto", {})
    if isinstance(contacto, dict):
        correo = contacto.get("correo")
        if isinstance(correo, str):
            config["contacto"]["correo"] = correo.strip()[:24]
        telefono = contacto.get("telefono")
        if isinstance(telefono, str):
            config["contacto"]["telefono"] = telefono.strip()[:20]
    for key in ("garrafon", "medio", "galon"):
        if key in manual_fill_keys:
            continue
        config["tiempos_llenado"][key] = round(
            max(0.1, float(config["volumenes"][key]) * float(config["tiempo_por_litro"])),
            2,
        )
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
    global FILL_SECONDS_PER_LITER, RINSE_LITERS, RINSE_SECONDS, ACCESS_CODE, AUDIT_CODE, UI_THEME, UI_MODE, AUDIO_MUTED, BRAND_TITLE, BRAND_TAGLINE, SYSTEM_NAME, CONTACT_EMAIL, CONTACT_PHONE
    sanitized = _sanitize_runtime_config(config)
    PRODUCTS[0]["price"] = sanitized["precios"]["garrafon"]
    PRODUCTS[1]["price"] = sanitized["precios"]["medio"]
    PRODUCTS[2]["price"] = sanitized["precios"]["galon"]
    PRODUCTS[0]["name"] = sanitized["nombres"]["garrafon"]
    PRODUCTS[1]["name"] = sanitized["nombres"]["medio"]
    PRODUCTS[2]["name"] = sanitized["nombres"]["galon"]
    PRODUCTS[0]["volume_l"] = sanitized["volumenes"]["garrafon"]
    PRODUCTS[1]["volume_l"] = sanitized["volumenes"]["medio"]
    PRODUCTS[2]["volume_l"] = sanitized["volumenes"]["galon"]
    PRODUCTS[0]["fill_time_s"] = sanitized["tiempos_llenado"]["garrafon"]
    PRODUCTS[1]["fill_time_s"] = sanitized["tiempos_llenado"]["medio"]
    PRODUCTS[2]["fill_time_s"] = sanitized["tiempos_llenado"]["galon"]
    FILL_SECONDS_PER_LITER = sanitized["tiempo_por_litro"]
    RINSE_LITERS = sanitized["litros_por_enjuague"]
    RINSE_SECONDS = round(RINSE_LITERS * FILL_SECONDS_PER_LITER, 2)
    ACCESS_CODE = sanitized["codigo"]
    AUDIT_CODE = sanitized["codigo_auditoria"]
    UI_THEME = sanitized["tema"]
    UI_MODE = sanitized["modo"]
    AUDIO_MUTED = sanitized["audio_muted"]
    BRAND_TITLE = sanitized["titulo"]
    BRAND_TAGLINE = sanitized["eslogan"]
    SYSTEM_NAME = sanitized["nombre_sistema"]
    CONTACT_EMAIL = sanitized["contacto"]["correo"]
    CONTACT_PHONE = sanitized["contacto"]["telefono"]


def get_runtime_config() -> dict:
    return {
        "precios": {
            "garrafon": float(PRODUCTS[0]["price"]),
            "medio": float(PRODUCTS[1]["price"]),
            "galon": float(PRODUCTS[2]["price"]),
        },
        "nombres": {
            "garrafon": str(PRODUCTS[0]["name"]),
            "medio": str(PRODUCTS[1]["name"]),
            "galon": str(PRODUCTS[2]["name"]),
        },
        "volumenes": {
            "garrafon": float(PRODUCTS[0]["volume_l"]),
            "medio": float(PRODUCTS[1]["volume_l"]),
            "galon": float(PRODUCTS[2]["volume_l"]),
        },
        "tiempos_llenado": {
            "garrafon": float(PRODUCTS[0].get("fill_time_s", PRODUCTS[0]["volume_l"] * FILL_SECONDS_PER_LITER)),
            "medio": float(PRODUCTS[1].get("fill_time_s", PRODUCTS[1]["volume_l"] * FILL_SECONDS_PER_LITER)),
            "galon": float(PRODUCTS[2].get("fill_time_s", PRODUCTS[2]["volume_l"] * FILL_SECONDS_PER_LITER)),
        },
        "tiempo_por_litro": float(FILL_SECONDS_PER_LITER),
        "litros_por_enjuague": float(RINSE_LITERS),
        "codigo": ACCESS_CODE,
        "codigo_auditoria": AUDIT_CODE,
        "tema": UI_THEME,
        "modo": UI_MODE,
        "audio_muted": AUDIO_MUTED,
        "titulo": BRAND_TITLE,
        "eslogan": BRAND_TAGLINE,
        "nombre_sistema": SYSTEM_NAME,
        "contacto": {
            "correo": CONTACT_EMAIL,
            "telefono": CONTACT_PHONE,
        },
    }


apply_runtime_config(load_runtime_config())
