from __future__ import annotations

import datetime as dt
import logging
import threading

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
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
    hardware_error = pyqtSignal(str)

    def __init__(self, config: AppConfig, db: SalesDatabase, valve: ValveController):
        super().__init__()
        self.config = config
        self.db = db
        self.valve = valve

        self.credit = 0.0
        self.dispensing = False

        self.credit_added.connect(self._on_credit_added)
        self.hardware_error.connect(self._on_hardware_error)

        self.coin_acceptor = CoinAcceptor(
            port=config.serial_port,
            baudrate=config.serial_baudrate,
            on_credit=lambda amount: self.credit_added.emit(amount),
            on_error=lambda message: self.hardware_error.emit(message),
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

        footer.addStretch(1)

        self.buy_button = QPushButton("Despachar")
        self.buy_button.setStyleSheet("font-size: 28px; padding: 14px 28px;")
        self.buy_button.clicked.connect(self.try_dispense)
        footer.addWidget(self.buy_button)

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
        self.credit += amount
        self._refresh_credit_label()

    def try_dispense(self) -> None:
        if self.dispensing:
            return

        if self.credit < self.config.price_per_product:
            QMessageBox.information(self, "Pago pendiente", "Saldo insuficiente.")
            return

        self.dispensing = True
        self.stack.setCurrentWidget(self.dispensing_screen)
        self.buy_button.setEnabled(False)

        thread = threading.Thread(target=self._dispense_cycle, daemon=True)
        thread.start()

    def _dispense_cycle(self) -> None:
        try:
            self.valve.open_for(self.config.valve_open_seconds)
            paid = self.credit
            self.credit -= self.config.price_per_product
            timestamp = dt.datetime.now().isoformat(timespec="seconds")
            self.db.log_sale(
                timestamp=timestamp,
                product=self.config.product_name,
                price=self.config.price_per_product,
                payment_received=paid,
            )
        except ValveControllerError as exc:
            self.hardware_error.emit(str(exc))
        except Exception as exc:
            self.hardware_error.emit(f"Unexpected dispensing error: {exc}")
        finally:
            QTimer.singleShot(0, self._finish_dispense)

    def _finish_dispense(self) -> None:
        self.dispensing = False
        self.buy_button.setEnabled(True)
        self.stack.setCurrentWidget(self.idle_screen)
        self._refresh_credit_label()

    def _on_hardware_error(self, message: str) -> None:
        LOGGER.error(message)
        QMessageBox.warning(self, "Error de hardware", message)

    def closeEvent(self, event):  # type: ignore[override]
        self.coin_acceptor.stop()
        self.valve.close()
        super().closeEvent(event)
