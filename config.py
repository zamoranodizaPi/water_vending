import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


@dataclass
class AppConfig:
    # GPIO mapping
    coin_pulse_gpio_pin: int = 12
    select_full_gpio_pin: int = 16
    select_half_gpio_pin: int = 20
    select_gallon_gpio_pin: int = 21
    fill_valve_gpio_pin: int = 17
    rinse_valve_gpio_pin: int = 27
    rinse_select_gpio_pin: int = 25
    ok_button_gpio_pin: int = 24

    # Business rules
    product_full_name: str = "Garrafón completo"
    product_half_name: str = "Medio garrafón"
    product_gallon_name: str = "1 galón"
    price_full: float = 12.0
    price_half: float = 8.0
    price_gallon: float = 5.0
    fill_seconds_full: float = 20.0
    fill_seconds_half: float = 10.0
    fill_seconds_gallon: float = 5.0
    rinse_seconds: float = 2.0
    coin_pulse_value: float = 1.0

    fullscreen: bool = True
    logo_path: str = "assets/images/logo.png"
    background_path: str = "assets/images/fondo.png"


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
        data = json.load(file)

    return AppConfig(**_sanitize(data))


def save_config(config: AppConfig, path: Path | str = DEFAULT_CONFIG_PATH) -> None:
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as file:
        json.dump(asdict(config), file, indent=2, ensure_ascii=False)
