"""Physical button LED animations driven from the UI state machine."""
from __future__ import annotations

import time

from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class ButtonLedController(QObject):
    attention_started = pyqtSignal()

    def __init__(self, gpio, leds: dict[str, object], products: list[dict], parent=None):
        super().__init__(parent)
        self.gpio = gpio
        self.leds = leds
        self.products = sorted(products, key=lambda product: product["price"])
        self.product_leds = {
            "full_garrafon": "full",
            "half_garrafon": "half",
            "gallon": "gallon",
        }
        self._mode = "idle"
        self._selected_product_id = None
        self._selected_affordable = False
        self._credit = 0.0
        self._mode_started_at = time.monotonic()

        self._frame_timer = QTimer(self)
        self._frame_timer.setInterval(50)
        self._frame_timer.timeout.connect(self._render)
        self._frame_timer.start()

        self._idle_timer = QTimer(self)
        self._idle_timer.setSingleShot(True)
        self._idle_timer.timeout.connect(self._start_attention)
        self._schedule_idle_attention()
        self._render()

    def note_interaction(self):
        if self._mode in {"idle", "attention"}:
            self._schedule_idle_attention()

    def update_home(self, credit: float, selected_product_id: str | None):
        self._credit = credit
        self._selected_product_id = selected_product_id
        self._selected_affordable = bool(
            selected_product_id and credit >= self._product_price(selected_product_id)
        )
        if selected_product_id:
            self._set_mode("selected")
            return
        if self._highest_affordable_product_id(credit):
            self._set_mode("credit")
            return
        self._set_mode("idle")

    def set_processing(self):
        self._set_mode("processing")

    def set_prompt_ready(self):
        self._set_mode("prompt_ready")

    def set_completion_flash(self):
        self._set_mode("completion")

    def shutdown(self):
        self._frame_timer.stop()
        self._idle_timer.stop()
        for led_name in self.leds:
            self._set_led(led_name, 0.0)

    def _set_mode(self, mode: str):
        if self._mode == mode:
            self._render()
            return
        self._mode = mode
        self._mode_started_at = time.monotonic()
        if mode == "idle":
            self._schedule_idle_attention()
        else:
            self._idle_timer.stop()
        self._render()

    def _schedule_idle_attention(self):
        self._idle_timer.start(60000)
        self._mode_started_at = time.monotonic()
        if self._mode == "attention":
            self._mode = "idle"
        self._render()

    def _start_attention(self):
        self._mode = "attention"
        self._mode_started_at = time.monotonic()
        self.attention_started.emit()
        self._render()

    def _product_price(self, product_id: str) -> float:
        for product in self.products:
            if product["id"] == product_id:
                return product["price"]
        return float("inf")

    def _highest_affordable_product_id(self, credit: float) -> str | None:
        affordable = [product["id"] for product in self.products if credit >= product["price"]]
        return affordable[-1] if affordable else None

    def _blink_value(self, elapsed: float, period: float = 2.0) -> float:
        phase = (elapsed % period) / period
        if phase < 0.5:
            return phase * 2.0
        return (1.0 - phase) * 2.0

    def _set_led(self, led_name: str, level: float):
        try:
            self.gpio.safe_value(self.leds[led_name], level, f"{led_name} led")
        except Exception:
            return

    def _render(self):
        now = time.monotonic()
        elapsed = now - self._mode_started_at
        levels = {name: 0.0 for name in self.leds}

        if self._mode == "attention":
            if elapsed >= 5.0:
                self._mode = "idle"
                self._mode_started_at = now
                self._schedule_idle_attention()
                return
            names = ["gallon", "half", "full", "ok", "emergency"]
            window = 0.33
            for index, name in enumerate(names):
                center = (index * 0.22) % 1.0
                phase = (elapsed / 1.1) % 1.0
                delta = abs((phase - center + 0.5) % 1.0 - 0.5)
                levels[name] = max(levels[name], max(0.0, 1.0 - (delta / window)))

        elif self._mode == "credit":
            product_id = self._highest_affordable_product_id(self._credit)
            if product_id:
                levels[self.product_leds[product_id]] = self._blink_value(elapsed)

        elif self._mode == "selected":
            if self._selected_product_id:
                levels[self.product_leds[self._selected_product_id]] = 1.0
            if self._selected_product_id and self._selected_affordable:
                levels["ok"] = self._blink_value(elapsed)

        elif self._mode == "processing":
            levels["emergency"] = self._blink_value(elapsed)

        elif self._mode == "prompt_ready":
            levels["ok"] = self._blink_value(elapsed, period=1.2)

        elif self._mode == "completion":
            if elapsed >= 0.9:
                self._mode = "idle"
                self._mode_started_at = now
                self._schedule_idle_attention()
                return
            levels = {name: (1.0 if int(elapsed / 0.15) % 2 == 0 else 0.0) for name in self.leds}

        for led_name, level in levels.items():
            self._set_led(led_name, level)
