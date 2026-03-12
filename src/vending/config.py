from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import yaml


@dataclass
class HardwarePins:
    fill_valve: int
    rinse_valve: int
    flow_sensor: int
    door_sensor: int
    interior_light: int
    uv_lamp: int
    ozone_machine: int


@dataclass
class ButtonPins:
    full: int
    half: int
    gallon: int
    ok: int
    rinse: int
    emergency_stop: int


@dataclass
class VendingConfig:
    hardware: HardwarePins
    buttons: ButtonPins
    prices: Dict[str, int]
    liters: Dict[str, float]
    pulse_window_ms: int


DEFAULT_CONFIG_PATH = Path("config/default.yaml")


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> VendingConfig:
    raw = yaml.safe_load(path.read_text())
    return VendingConfig(
        hardware=HardwarePins(**raw["hardware"]),
        buttons=ButtonPins(**raw["buttons"]),
        prices=raw["prices"],
        liters=raw["liters"],
        pulse_window_ms=raw.get("pulse_window_ms", 300),
    )
