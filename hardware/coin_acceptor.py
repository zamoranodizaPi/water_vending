"""Coin acceptor handler built on gpiozero input callbacks."""
from __future__ import annotations

import time
from typing import Callable

from hardware.gpio_controller import GPIOController


class CoinAcceptor:
    def __init__(
        self,
        gpio: GPIOController,
        input_device,
        on_coin: Callable[[int], None],
        *,
        min_interval_s: float = 0.05,
        pulse_value: int = 1,
    ):
        self.gpio = gpio
        self.input_device = input_device
        self.on_coin = on_coin
        self.min_interval_s = min_interval_s
        self.pulse_value = pulse_value
        self._last_pulse_at: float = 0.0
        self.input_device.when_pressed = self._coin_detected

    def _coin_detected(self):
        now = time.monotonic()
        if now - self._last_pulse_at < self.min_interval_s:
            return
        self._last_pulse_at = now
        self.on_coin(self.pulse_value)
