from __future__ import annotations

import datetime as dt
import logging
import threading

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import AppConfig
from database.sales_db import SalesDatabase
from hardware.coin_acceptor import CoinAcceptor
from hardware.valve_controller import ValveController, ValveControllerError
from ui.screens import DispensingScreen, IdleScreen


LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    credit_added = pyqtSignal(float)
    dispense_finished = pyqtSignal(float)
    hardware_error = pyqtSignal(str)

    def __init__(self, config: AppConfig, db: SalesDatabase, valve: ValveController):
        super().__init__()
        self.config = config
        self.db = db
        self.valve = valve

        self.credit = 0.0
        self.dispensing = False
        self._lock = threading.Lock()

        self.credit_added.connect(self._on_credit_added)
        self.dispense_finished.connect(self._on_dispense_finished)
        self.hardware_error.connect(self._on_hardware_error)

        self.coin_acceptor = CoinAcceptor(
            port=config.serial_port,
            baudrate=config.serial_baudrate,
            on_credit=lambda amount: self.credit_added.emit(amount),
            on_error=lambda message: self.hardware_error.emit(message),
            input_mode=config.coin_input_mode,
            coin_pulse_value=config.coin_pulse_value,
        )

        self.setWindowTitle("Water Vending")
        self._build_ui()
        self._start_coin_reader()

    def _build_ui(self) -> None:
        container = QWidget()
        self.setCentralWidget(container)

        root_layout = QVBoxLayout(container)

        top_bar = QHBoxLayout()
        top_bar.addStretch(1)
        self.logo_label = QLabel()
        self.logo_label.setFixedHeight(90)
        self.logo_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._load_logo()
        top_bar.addWidget(self.logo_label)
        root_layout.addLayout(top_bar)

        self.stack = QStackedWidget()
        self.idle_screen = IdleScreen(self.config.product_name)
        self.dispensing_screen = DispensingScreen()
        self.stack.addWidget(self.idle_screen)
        self.stack.addWidget(self.dispensing_screen)
        root_layout.addWidget(self.stack)

        footer = QHBoxLayout()
        self.credit_label = QLabel()
        self.credit_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        footer.addWidget(self.credit_label)
        root_layout.addLayout(footer)

        self._refresh_credit_label()
        self.setStyleSheet("background-color: #f5f8fc;")

    def _load_logo(self) -> None:
        pixmap = QPixmap(self.config.logo_path)
        if pixmap.isNull():
            self.logo_label.setText("WATER")
            self.logo_label.setStyleSheet("font-size: 28px; font-weight: bold;")
            return
        self.logo_label.setPixmap(
            pixmap.scaledToHeight(self.logo_label.height(), Qt.SmoothTransformation)
        )

    def _start_coin_reader(self) -> None:
        self.coin_acceptor.start()

    def _refresh_credit_label(self) -> None:
        self.credit_label.setText(
            f"Crédito: ${self.credit:.2f} / Precio: ${self.config.price_per_product:.2f}"
        )

    def _on_credit_added(self, amount: float) -> None:
        with self._lock:
            self.credit += amount
            should_dispense = (not self.dispensing) and self.credit >= self.config.price_per_product

        self._refresh_credit_label()
        if should_dispense:
            self._start_dispense()

    def _start_dispense(self) -> None:
        self.dispensing = True
        self.stack.setCurrentWidget(self.dispensing_screen)
        thread = threading.Thread(target=self._dispense_cycle, daemon=True)
        thread.start()

    def _dispense_cycle(self) -> None:
        try:
            self.valve.open_for(self.config.valve_open_seconds)
            self.dispense_finished.emit(self.config.price_per_product)
        except ValveControllerError as exc:
            self.hardware_error.emit(str(exc))
            self.dispense_finished.emit(0.0)
        except Exception as exc:
            self.hardware_error.emit(f"Unexpected dispensing error: {exc}")
            self.dispense_finished.emit(0.0)

    def _on_dispense_finished(self, charged_amount: float) -> None:
        paid_snapshot = 0.0
        with self._lock:
            if charged_amount > 0:
                paid_snapshot = self.credit
                self.credit = max(0.0, self.credit - charged_amount)
            self.dispensing = False

        if charged_amount > 0:
            timestamp = dt.datetime.now().isoformat(timespec="seconds")
            self.db.log_sale(
                timestamp=timestamp,
                product=self.config.product_name,
                price=self.config.price_per_product,
                payment_received=paid_snapshot,
            )

        self.stack.setCurrentWidget(self.idle_screen)
        self._refresh_credit_label()

        if self.credit >= self.config.price_per_product and not self.dispensing:
            self._start_dispense()

    def _on_hardware_error(self, message: str) -> None:
        LOGGER.error(message)
        QMessageBox.warning(self, "Error de hardware", message)

    def closeEvent(self, event):  # type: ignore[override]
        self.coin_acceptor.stop()
        self.valve.close()
        super().closeEvent(event)
