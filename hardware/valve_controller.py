import time

from gpiozero import OutputDevice


class ValveControllerError(Exception):
    """Raised when a valve cannot be controlled."""


class ValveController:
    def __init__(self, fill_gpio_pin: int, rinse_gpio_pin: int):
        self.fill_gpio_pin = fill_gpio_pin
        self.rinse_gpio_pin = rinse_gpio_pin
        self.fill_valve = OutputDevice(pin=self.fill_gpio_pin, active_high=True, initial_value=False)
        self.rinse_valve = OutputDevice(pin=self.rinse_gpio_pin, active_high=True, initial_value=False)

    def activate_fill_for(self, seconds: float) -> None:
        self._activate_for(self.fill_valve, seconds)

    def activate_rinse_for(self, seconds: float) -> None:
        self._activate_for(self.rinse_valve, seconds)

    def _activate_for(self, device: OutputDevice, seconds: float) -> None:
        if seconds <= 0:
            return
        try:
            device.on()
            time.sleep(seconds)
        except Exception as exc:
            raise ValveControllerError(f"Error while activating valve: {exc}") from exc
        finally:
            device.off()

    def close(self) -> None:
        self.fill_valve.off()
        self.rinse_valve.off()
        self.fill_valve.close()
        self.rinse_valve.close()
