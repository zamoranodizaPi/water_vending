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
        min_pulse_width_s: float = 0.03,
        min_interval_s: float = 0.04,
        pulse_value: int = 1,
    ):
        self.gpio = gpio
        self.input_device = input_device
        self.on_coin = on_coin
        self.min_pulse_width_s = min_pulse_width_s
        self.min_interval_s = min_interval_s
        self.pulse_value = pulse_value
        self._pressed_at: float | None = None
        self._last_accepted_at: float = 0.0
        self.input_device.when_pressed = self._pulse_started
        self.input_device.when_released = self._pulse_finished

    def _pulse_started(self):
        self._pressed_at = time.monotonic()

    def _pulse_finished(self):
        released_at = time.monotonic()
        if self._pressed_at is None:
            return
        pulse_width = released_at - self._pressed_at
        interval = released_at - self._last_accepted_at
        self._pressed_at = None
        if pulse_width < self.min_pulse_width_s:
            return
        if interval <= self.min_interval_s:
            return
        self._last_accepted_at = released_at
        self.on_coin(self.pulse_value)
