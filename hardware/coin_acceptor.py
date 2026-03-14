"""Coin acceptor handler built on gpiozero input callbacks."""
from __future__ import annotations

from typing import Callable

from hardware.gpio_controller import GPIOController


class CoinAcceptor:
    def __init__(self, gpio: GPIOController, input_device, on_coin: Callable[[], None]):
        self.gpio = gpio
        self.input_device = input_device
        self.on_coin = on_coin
        self.input_device.when_pressed = self._coin_detected

    def _coin_detected(self):
        self.on_coin()
