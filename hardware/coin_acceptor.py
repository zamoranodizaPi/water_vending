"""Coin acceptor handler for a normally-open pulse train on GPIO19.

Each coin is reported as a LOW pulse of about 100 ms with the line held HIGH by
the Raspberry Pi pull-up the rest of the time.
"""
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
    """Read a normally-open coin acceptor that drives the line LOW per pulse."""
    def __init__(
        self,
        pin: int,
        on_coin: Callable[[int], None],
        *,
        flush_window_s: float = 0.3,
        min_gap_us: int = 40000,
        min_width_us: int = 70000,
        max_width_us: int = 130000,
        poll_ms: int = 50,
        parent=None,
    ):
        super().__init__(parent)
        self.pin = pin
        self.on_coin = on_coin
        self.flush_window_s = flush_window_s
        self.min_gap_us = min_gap_us
        self.min_width_us = min_width_us
        self.max_width_us = max_width_us
        self._pulse_start_tick = 0
        self._last_count_tick = 0
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
        self._callback = self._pi.callback(self.pin, pigpio.EITHER_EDGE, self._pulse_callback)

    def _pulse_callback(self, gpio: int, level: int, tick: int):
        print(f"GPIO: {gpio} Level: {level} Tick: {tick}")
        if level == 0:
            self._pulse_start_tick = tick
            return

        if level != 1 or self._pulse_start_tick == 0:
            return

        width_us = pigpio.tickDiff(self._pulse_start_tick, tick)
        self._pulse_start_tick = 0
        print(f"Ancho LOW: {width_us}us")

        if width_us < self.min_width_us or width_us > self.max_width_us:
            print(f"Pulso ignorado por ancho fuera de rango: {width_us}us")
            return

        if self._last_count_tick != 0:
            gap_us = pigpio.tickDiff(self._last_count_tick, tick)
            print(f"Intervalo entre conteos: {gap_us}us")
            if gap_us < self.min_gap_us:
                print(f"Pulso ignorado por rebote: {gap_us}us")
                return

        self._last_count_tick = tick
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
