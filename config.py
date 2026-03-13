from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


@dataclass
class AppConfig:
    product_name: str = "Garrafón de agua"
    price_per_product: float = 20.0
    valve_open_seconds: float = 8.0
    relay_gpio_pin: int = 17
    serial_port: str = "/dev/ttyUSB0"
    serial_baudrate: int = 9600
    coin_input_mode: str = "serial_value"  # serial_value | pulse
    coin_pulse_value: float = 1.0
    fullscreen: bool = True
    logo_path: str = "assets/images/logo.png"


def _sanitize(raw: Dict[str, Any]) -> Dict[str, Any]:
    defaults = asdict(AppConfig())
    sanitized = defaults.copy()
    sanitized.update({k: v for k, v in raw.items() if k in defaults})
    return sanitized


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        config = AppConfig()
        save_config(config, config_path)
        return config

    with config_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    return AppConfig(**_sanitize(raw))


def save_config(config: AppConfig, path: Path | str = DEFAULT_CONFIG_PATH) -> None:
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as file:
        json.dump(asdict(config), file, indent=2, ensure_ascii=False)
