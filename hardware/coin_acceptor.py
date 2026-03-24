"""Coin acceptor handler built on pigpio falling-edge callbacks."""
from __future__ import annotations

import logging
import time
from typing import Callable

from PyQt5.QtCore import QObject, QTimer

logger = logging.getLogger(__name__)

try:
    import pigpio
except Exception:  # pragma: no cover - optional on non-device environments
    pigpio = None


class CoinAcceptor(QObject):
    def __init__(
        self,
        pin: int,
        on_coin: Callable[[int], None],
        *,
        flush_window_s: float = 0.2,
        min_pulse_us: int = 30000,
        poll_ms: int = 50,
        parent=None,
    ):
        super().__init__(parent)
        self.pin = pin
        self.on_coin = on_coin
        self.flush_window_s = flush_window_s
        self.min_pulse_us = min_pulse_us
        self._last_tick = 0
        self._last_pulse_at = 0.0
        self._pending_pulses = 0
        self._pi = None
        self._callback = None

        self._flush_timer = QTimer(self)
        self._flush_timer.setInterval(poll_ms)
        self._flush_timer.timeout.connect(self._flush_if_ready)

        self._setup_pigpio()
        self._flush_timer.start()

    def _setup_pigpio(self):
        if pigpio is None:
            logger.error("pigpio no disponible para el aceptador de monedas")
            return
        self._pi = pigpio.pi()
        if not self._pi.connected:
            logger.error("Error: pigpio no conectado")
            self._pi = None
            return
        self._pi.set_mode(self.pin, pigpio.INPUT)
        self._pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
        self._callback = self._pi.callback(self.pin, pigpio.FALLING_EDGE, self._pulse_callback)

    def _pulse_callback(self, gpio: int, level: int, tick: int):
        if level != 0:
            return
        if self._last_tick != 0:
            delta = pigpio.tickDiff(self._last_tick, tick)
            if delta < self.min_pulse_us:
                return
        self._last_tick = tick
        self._pending_pulses += 1
        self._last_pulse_at = time.monotonic()
        print(f"Pulso detectado → Crédito pendiente: {self._pending_pulses}")

    def _flush_if_ready(self):
        if self._pending_pulses <= 0:
            return
        if (time.monotonic() - self._last_pulse_at) < self.flush_window_s:
            return
        amount = self._pending_pulses
        self._pending_pulses = 0
        self.on_coin(amount)

    def shutdown(self):
        self._flush_timer.stop()
        if self._callback is not None:
            self._callback.cancel()
            self._callback = None
        if self._pi is not None:
            self._pi.stop()
            self._pi = None
