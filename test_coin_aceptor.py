#!/usr/bin/env python3
"""Standalone pigpio monitor for a normally-open coin acceptor on GPIO19."""

from __future__ import annotations

import signal
import sys
import time

import pigpio

GPIO_PIN = 18
MIN_GAP_US = 30000
MIN_WIDTH_US = 30000
MAX_WIDTH_US = 220000


class CoinPulseMonitor:
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            print("Error: pigpio no conectado")
            sys.exit(1)

        self.count = 0
        self.last_tick = 0
        self.callback = None

        self.pi.set_mode(GPIO_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(GPIO_PIN, pigpio.PUD_UP)
        self.pulse_start_tick = 0
        self.last_count_tick = 0
        self.callback = self.pi.callback(GPIO_PIN, pigpio.EITHER_EDGE, self._on_pulse)

    def _on_pulse(self, gpio: int, level: int, tick: int):
        print(f"GPIO: {gpio} Level: {level} Tick: {tick}")

        if level == 0:
            self.pulse_start_tick = tick
            return

        if level != 1 or self.pulse_start_tick == 0:
            return

        width_us = pigpio.tickDiff(self.pulse_start_tick, tick)
        self.pulse_start_tick = 0
        print(f"Ancho LOW: {width_us}us")

        if width_us < MIN_WIDTH_US or width_us > MAX_WIDTH_US:
            print(f"Pulso ignorado por ancho fuera de rango: {width_us}us")
            return

        if self.last_count_tick != 0:
            gap_us = pigpio.tickDiff(self.last_count_tick, tick)
            print(f"Intervalo entre conteos: {gap_us}us")
            if gap_us < MIN_GAP_US:
                print(f"Pulso ignorado por rebote: {gap_us}us")
                return

        self.last_count_tick = tick
        self.count += 1
        print(f"Conteos: {self.count}")

    def shutdown(self):
        if self.callback is not None:
            self.callback.cancel()
            self.callback = None
        if self.pi is not None:
            self.pi.stop()
        print(f"Total de conteos: {self.count}")


def main():
    monitor = CoinPulseMonitor()

    def _stop(_signum, _frame):
        monitor.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    print("Monitoreando GPIO19 en modo normalmente abierto.")
    print("Reposo: HIGH, pulso valido: LOW de ~100ms.")
    print("Presiona Ctrl+C para salir.")

    try:
        while True:
            time.sleep(1)
    finally:
        monitor.shutdown()


if __name__ == "__main__":
    main()
