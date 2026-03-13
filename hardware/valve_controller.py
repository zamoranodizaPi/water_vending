from __future__ import annotations

import time
from typing import Optional


class ValveControllerError(Exception):
    """Raised when the valve cannot be controlled."""


class ValveController:
    def __init__(self, relay_gpio_pin: int):
        self.relay_gpio_pin = relay_gpio_pin
        self._relay: Optional[object] = None
        self._init_relay()

    def _init_relay(self) -> None:
        try:
            from gpiozero import OutputDevice  # type: ignore

            self._relay = OutputDevice(pin=self.relay_gpio_pin, active_high=True, initial_value=False)
        except Exception as exc:
            raise ValveControllerError(
                f"Unable to initialize relay on GPIO {self.relay_gpio_pin}: {exc}"
            ) from exc

    def open_for(self, seconds: float) -> None:
        if self._relay is None:
            raise ValveControllerError("Relay was not initialized")

        try:
            self._relay.on()
            time.sleep(max(0.0, seconds))
        except Exception as exc:
            raise ValveControllerError(f"Error while opening valve: {exc}") from exc
        finally:
            try:
                self._relay.off()
            except Exception:
                pass

    def close(self) -> None:
        if self._relay is None:
            return
        try:
            self._relay.off()
            self._relay.close()  # type: ignore[attr-defined]
        except Exception:
            pass
