"""GPIO wrapper with safe fallbacks and centralized error handling."""
from __future__ import annotations

import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

try:
    from gpiozero import Button, LED, PWMLED
except Exception:  # pragma: no cover - used on non-RPi environments
    Button = None
    LED = None
    PWMLED = None


class GPIOControllerError(RuntimeError):
    """Raised when a GPIO operation fails."""


class NullOutput:
    def __init__(self, name: str):
        self.name = name
        self.is_lit = False

    def on(self):
        self.is_lit = True
        logger.debug("NullOutput(%s) -> on", self.name)

    def off(self):
        self.is_lit = False
        logger.debug("NullOutput(%s) -> off", self.name)

    @property
    def value(self) -> float:
        return 1.0 if self.is_lit else 0.0

    @value.setter
    def value(self, level: float):
        self.is_lit = level > 0
        logger.debug("NullOutput(%s) -> value=%s", self.name, level)


class NullInput:
    def __init__(self, name: str):
        self.name = name
        self.when_pressed: Optional[Callable[[], None]] = None
        self.when_released: Optional[Callable[[], None]] = None
        self.when_held: Optional[Callable[[], None]] = None
        self.hold_time: float = 1.0
        self.hold_repeat: bool = False
        self.is_pressed: bool = False


class GPIOController:
    """Factory for resilient GPIO objects."""

    def setup_output(self, pin: int, name: str):
        if LED is None:
            logger.warning("gpiozero LED unavailable. Using NullOutput for %s", name)
            return NullOutput(name)
        try:
            device = LED(pin)
            device.off()
            return device
        except Exception as exc:
            logger.exception("Failed to configure output %s on pin %s", name, pin)
            return NullOutput(name)

    def setup_pwm_output(self, pin: int, name: str):
        if PWMLED is None:
            logger.warning("gpiozero PWMLED unavailable. Using NullOutput for %s", name)
            return NullOutput(name)
        try:
            device = PWMLED(pin)
            device.value = 0.0
            return device
        except Exception:
            logger.exception("Failed to configure PWM output %s on pin %s", name, pin)
            return NullOutput(name)

    def setup_input(self, pin: int, name: str, *, pull_up: bool = True, bounce_time: float = 0.12):
        if Button is None:
            logger.warning("gpiozero Button unavailable. Using NullInput for %s", name)
            return NullInput(name)
        try:
            return Button(pin, pull_up=pull_up, bounce_time=bounce_time)
        except Exception as exc:
            logger.exception("Failed to configure input %s on pin %s", name, pin)
            return NullInput(name)

    @staticmethod
    def safe_on(device, label: str):
        try:
            device.on()
        except Exception as exc:
            raise GPIOControllerError(f"Failed to turn on {label}: {exc}") from exc

    @staticmethod
    def safe_off(device, label: str):
        try:
            device.off()
        except Exception as exc:
            raise GPIOControllerError(f"Failed to turn off {label}: {exc}") from exc

    @staticmethod
    def safe_value(device, value: float, label: str):
        try:
            device.value = max(0.0, min(1.0, value))
        except Exception as exc:
            raise GPIOControllerError(f"Failed to set {label} level: {exc}") from exc
