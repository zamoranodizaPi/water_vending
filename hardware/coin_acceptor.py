from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Optional

import serial
from serial import SerialException


LOGGER = logging.getLogger(__name__)


class CoinAcceptor:
    """Reads coin events from serial.

    Modes:
    - serial_value: each line is a numeric value or `COIN:<value>`
    - pulse: each line represents one pulse; amount = coin_pulse_value
    """

    def __init__(
        self,
        port: str,
        baudrate: int,
        on_credit: Callable[[float], None],
        on_error: Optional[Callable[[str], None]] = None,
        input_mode: str = "serial_value",
        coin_pulse_value: float = 1.0,
    ):
        self.port = port
        self.baudrate = baudrate
        self.on_credit = on_credit
        self.on_error = on_error
        self.input_mode = input_mode
        self.coin_pulse_value = coin_pulse_value

        self._serial: Optional[serial.Serial] = None
        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()

    def start(self) -> None:
        self._running.set()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._serial and self._serial.is_open:
            self._serial.close()

    def _run(self) -> None:
        while self._running.is_set():
            if not self._serial or not self._serial.is_open:
                if not self._connect():
                    time.sleep(2.0)
                    continue

            try:
                raw_line = self._serial.readline().decode("utf-8", errors="ignore").strip()
                if not raw_line:
                    continue
                amount = self._parse_amount(raw_line)
                if amount > 0:
                    self.on_credit(amount)
            except SerialException as exc:
                self._emit_error(f"Serial read error: {exc}")
                self._disconnect()
            except ValueError:
                LOGGER.debug("Ignoring unsupported coin payload")
            except Exception as exc:
                self._emit_error(f"Unexpected coin acceptor error: {exc}")

    def _connect(self) -> bool:
        try:
            self._serial = serial.Serial(self.port, self.baudrate, timeout=1)
            return True
        except SerialException as exc:
            self._emit_error(f"Cannot open serial port {self.port}: {exc}")
            return False

    def _disconnect(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()

    def _parse_amount(self, payload: str) -> float:
        if self.input_mode == "pulse":
            return self.coin_pulse_value

        if payload.upper().startswith("COIN:"):
            return float(payload.split(":", 1)[1])
        return float(payload)

    def _emit_error(self, message: str) -> None:
        LOGGER.warning(message)
        if self.on_error:
            self.on_error(message)
