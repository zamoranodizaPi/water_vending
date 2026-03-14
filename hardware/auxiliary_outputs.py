"""Auxiliary GPIO output controls."""
from __future__ import annotations

from hardware.gpio_controller import GPIOController


class AuxiliaryOutputs:
    def __init__(self, gpio: GPIOController, courtesy_light, ozone, uv_lamp):
        self.gpio = gpio
        self.courtesy_light = courtesy_light
        self.ozone = ozone
        self.uv_lamp = uv_lamp

    def courtesy_on(self):
        self.gpio.safe_on(self.courtesy_light, "courtesy light")

    def courtesy_off(self):
        self.gpio.safe_off(self.courtesy_light, "courtesy light")

    def ozone_on(self):
        self.gpio.safe_on(self.ozone, "ozone generator")

    def ozone_off(self):
        self.gpio.safe_off(self.ozone, "ozone generator")

    def uv_on(self):
        self.gpio.safe_on(self.uv_lamp, "uv lamp")

    def uv_off(self):
        self.gpio.safe_off(self.uv_lamp, "uv lamp")
