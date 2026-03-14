"""Manages valve and disinfection outputs during dispensing."""
from __future__ import annotations

from hardware.auxiliary_outputs import AuxiliaryOutputs
from hardware.gpio_controller import GPIOController


class ValveController:
    def __init__(self, gpio: GPIOController, water_valve, rinse_valve, aux: AuxiliaryOutputs):
        self.gpio = gpio
        self.water_valve = water_valve
        self.rinse_valve = rinse_valve
        self.aux = aux
        self.ozone_activated = False

    def start_dispense(self):
        self.ozone_activated = False
        self.aux.uv_on()
        self.gpio.safe_on(self.water_valve, "water valve")

    def update_progress(self, progress: int):
        if progress >= 75 and not self.ozone_activated:
            self.aux.ozone_on()
            self.ozone_activated = True

    def finish_dispense(self):
        self.gpio.safe_off(self.water_valve, "water valve")
        self.aux.uv_off()
        self.aux.ozone_off()

    def rinse_start(self):
        self.gpio.safe_on(self.rinse_valve, "rinse valve")

    def rinse_stop(self):
        self.gpio.safe_off(self.rinse_valve, "rinse valve")
