#!/usr/bin/env python3
"""Standalone pigpio monitor for a normally-open coin acceptor on GPIO19."""

from __future__ import annotations

import signal
import sys
import time

import pigpio

GPIO_PIN = 19
MIN_PULSE_US = 40000


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
        self.callback = self.pi.callback(GPIO_PIN, pigpio.FALLING_EDGE, self._on_pulse)

    def _on_pulse(self, gpio: int, level: int, tick: int):
        print(f"GPIO: {gpio} Level: {level} Tick: {tick}")
        if level != 0:
            return

        if self.last_tick != 0:
            delta = pigpio.tickDiff(self.last_tick, tick)
            print(f"Intervalo: {delta}us")
            if delta < MIN_PULSE_US:
                print(f"Pulso ignorado por rebote: {delta}us")
                return

        self.last_tick = tick
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
