from datetime import datetime
from threading import Lock, Thread
import time

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from config import AppConfig
from database.sales_db import SalesDatabase
from hardware.gpio_inputs import GPIOInputs
from hardware.valve_controller import ValveController, ValveControllerError


class MainWindow(QMainWindow):
    ui_credit_updated = pyqtSignal(float)
    ui_selected_product = pyqtSignal(str)
    ui_rinse_changed = pyqtSignal(bool)
    ui_state_changed = pyqtSignal(str)
    ui_error = pyqtSignal(str)
    ui_process_finished = pyqtSignal(float, str)
    ui_progress = pyqtSignal(int)

    def __init__(self, config: AppConfig, db: SalesDatabase, valve: ValveController):
        super().__init__()
        self.config = config
        self.db = db
        self.valve = valve

        self.credit = 0.0
        self.selected_product = ""
        self.selected_price = 0.0
        self.selected_fill_seconds = 0.0
        self.rinse_selected = False
        self.in_process = False
        self.awaiting_fill_confirmation = False
        self._lock = Lock()

        self._build_ui()

        self.ui_credit_updated.connect(self._refresh_credit)
        self.ui_selected_product.connect(self._refresh_selection)
        self.ui_rinse_changed.connect(self._refresh_rinse)
        self.ui_state_changed.connect(self._set_state_text)
        self.ui_error.connect(self._show_error)
        self.ui_process_finished.connect(self._on_process_finished)
        self.ui_progress.connect(self.progress_bar.setValue)

        self.gpio = GPIOInputs(
            coin_pin=self.config.coin_pulse_gpio_pin,
            full_pin=self.config.select_full_gpio_pin,
            half_pin=self.config.select_half_gpio_pin,
            gallon_pin=self.config.select_gallon_gpio_pin,
            rinse_pin=self.config.rinse_select_gpio_pin,
            ok_pin=self.config.ok_button_gpio_pin,
            on_coin=self._on_coin_pulse,
            on_select_full=self._on_select_full,
            on_select_half=self._on_select_half,
            on_select_gallon=self._on_select_gallon,
            on_rinse_toggle=self._on_rinse_toggle,
            on_ok=self._on_ok_pressed,
        )

    def _build_ui(self) -> None:
        self.setWindowTitle("Water Vending")

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(16)

        self.logo = QLabel("", self)
        self.logo.setAlignment(Qt.AlignRight)
        self._load_logo()

        self.title_label = QLabel("Sistema de llenado de agua", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 34px; font-weight: bold;")

        self.credit_label = QLabel("Crédito: $0.00", self)
        self.credit_label.setAlignment(Qt.AlignCenter)
        self.credit_label.setStyleSheet("font-size: 28px;")

        self.selection_label = QLabel("Selección: Ninguna", self)
        self.selection_label.setAlignment(Qt.AlignCenter)
        self.selection_label.setStyleSheet("font-size: 26px;")

        self.rinse_label = QLabel("Enjuague: No", self)
        self.rinse_label.setAlignment(Qt.AlignCenter)
        self.rinse_label.setStyleSheet("font-size: 24px;")

        self.state_label = QLabel(
            "Inserta crédito (GPIO12), selecciona producto (GPIO16/20/21), activa enjuague (GPIO25) y presiona OK (GPIO24)",
            self,
        )
        self.state_label.setWordWrap(True)
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setStyleSheet("font-size: 22px; color: #333;")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar {font-size: 18px; height: 34px;}")

        layout.addWidget(self.logo)
        layout.addWidget(self.title_label)
        layout.addWidget(self.credit_label)
        layout.addWidget(self.selection_label)
        layout.addWidget(self.rinse_label)
        layout.addWidget(self.state_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch()

        self.setCentralWidget(central)

    def _load_logo(self) -> None:
        pixmap = QPixmap(self.config.logo_path)
        if pixmap.isNull():
            self.logo.setText("[LOGO]")
            return
        self.logo.setPixmap(pixmap.scaledToHeight(90, Qt.SmoothTransformation))

    def _on_coin_pulse(self) -> None:
        with self._lock:
            if self.in_process:
                return
            self.credit += self.config.coin_pulse_value
            credit = self.credit
        self.ui_credit_updated.emit(credit)

    def _set_product(self, name: str, price: float, seconds: float) -> None:
        with self._lock:
            if self.in_process:
                return
            self.selected_product = name
            self.selected_price = price
            self.selected_fill_seconds = seconds
        self.ui_selected_product.emit(f"{name} - ${price:.2f}")

    def _on_select_full(self) -> None:
        self._set_product(self.config.product_full_name, self.config.price_full, self.config.fill_seconds_full)

    def _on_select_half(self) -> None:
        self._set_product(self.config.product_half_name, self.config.price_half, self.config.fill_seconds_half)

    def _on_select_gallon(self) -> None:
        self._set_product(self.config.product_gallon_name, self.config.price_gallon, self.config.fill_seconds_gallon)

    def _on_rinse_toggle(self) -> None:
        with self._lock:
            if self.in_process:
                return
            self.rinse_selected = not self.rinse_selected
            value = self.rinse_selected
        self.ui_rinse_changed.emit(value)

    def _on_ok_pressed(self) -> None:
        with self._lock:
            if self.in_process:
                return
            if self.awaiting_fill_confirmation:
                self.in_process = True
                self.awaiting_fill_confirmation = False
                fill_seconds = self.selected_fill_seconds
                product = self.selected_product
                price = self.selected_price
                self.ui_state_changed.emit("Iniciando llenado...")
                Thread(
                    target=self._run_fill_only_cycle,
                    args=(fill_seconds, product, price),
                    daemon=True,
                ).start()
                return

            if not self.selected_product:
                self.ui_state_changed.emit("Primero selecciona un producto")
                return
            if self.credit < self.selected_price:
                self.ui_state_changed.emit("Crédito insuficiente para la selección actual")
                return
            if not self.rinse_selected:
                self.ui_state_changed.emit("Activa enjuague (GPIO25) antes de presionar OK")
                return

            self.in_process = True
            fill_seconds = self.selected_fill_seconds
            product = self.selected_product
            price = self.selected_price

        Thread(target=self._run_rinse_then_wait_cycle, args=(fill_seconds, product, price), daemon=True).start()

    def _run_rinse_then_wait_cycle(self, fill_seconds: float, product: str, price: float) -> None:
        try:
            self.ui_state_changed.emit("Enjuagando garrafón...")
            self._animate_progress(self.config.rinse_seconds)
            self.valve.activate_rinse_for(self.config.rinse_seconds)
            with self._lock:
                self.in_process = False
                self.awaiting_fill_confirmation = True
            self.ui_state_changed.emit("Voltea el garrafón y presiona OK para iniciar llenado")
            self.ui_progress.emit(0)
        except ValveControllerError as exc:
            with self._lock:
                self.in_process = False
                self.awaiting_fill_confirmation = False
            self.ui_error.emit(str(exc))

    def _run_fill_only_cycle(self, fill_seconds: float, product: str, price: float) -> None:
        try:
            self.ui_state_changed.emit("Llenando...")
            self._animate_progress(fill_seconds)
            self.valve.activate_fill_for(fill_seconds)
            self.ui_process_finished.emit(price, product)
        except ValveControllerError as exc:
            with self._lock:
                self.in_process = False
            self.ui_error.emit(str(exc))

    def _animate_progress(self, total_seconds: float) -> None:
        if total_seconds <= 0:
            self.ui_progress.emit(100)
            return
        steps = 100
        interval = total_seconds / steps
        for value in range(steps + 1):
            self.ui_progress.emit(value)
            time.sleep(interval)

    def _on_process_finished(self, charged_amount: float, product: str) -> None:
        with self._lock:
            self.credit = max(0.0, self.credit - charged_amount)
            remaining = self.credit
            self.selected_product = ""
            self.selected_price = 0.0
            self.selected_fill_seconds = 0.0
            self.rinse_selected = False
            self.in_process = False
            self.awaiting_fill_confirmation = False

        self.db.log_sale(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            product=product,
            price=charged_amount,
            payment_received=charged_amount,
        )

        self.ui_credit_updated.emit(remaining)
        self.ui_selected_product.emit("Ninguna")
        self.ui_rinse_changed.emit(False)
        self.ui_progress.emit(0)
        self.ui_state_changed.emit("Proceso completado. Listo para nueva venta")

    def _refresh_credit(self, current_credit: float) -> None:
        self.credit_label.setText(f"Crédito disponible: ${current_credit:.2f}")

    def _refresh_selection(self, selection: str) -> None:
        self.selection_label.setText(f"Selección actual: {selection}")

    def _refresh_rinse(self, selected: bool) -> None:
        self.rinse_label.setText(f"Enjuague: {'Sí' if selected else 'No'}")

    def _set_state_text(self, text: str) -> None:
        self.state_label.setText(text)

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error de hardware", message)

    def closeEvent(self, event):  # type: ignore[override]
        self.gpio.close()
        self.valve.close()
        super().closeEvent(event)
