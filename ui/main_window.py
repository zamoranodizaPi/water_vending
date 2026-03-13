"""Main kiosk window for the water vending machine."""
from __future__ import annotations

import logging
from datetime import datetime

from PyQt5.QtCore import QObject, QEvent, QTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

from config import settings
from database.sales_db import SalesDB
from hardware.auxiliary_outputs import AuxiliaryOutputs
from hardware.coin_acceptor import CoinAcceptor
from hardware.gpio_controller import GPIOController, GPIOControllerError
from hardware.valve_controller import ValveController
from ui.dispensing_screen import DispensingScreen
from ui.payment_screen import PaymentScreen
from ui.product_screen import ProductScreen

logger = logging.getLogger(__name__)


class InteractionFilter(QObject):
    interacted = pyqtSignal()

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.TouchBegin):
            self.interacted.emit()
        return False


class MainWindow(QMainWindow):
    coin_inserted = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(settings.WINDOW_TITLE)
        self.current_product = None
        self.credit = 0.0

        self.sales_db = SalesDB(settings.DB_PATH)
        self.gpio = GPIOController()
        self._setup_hardware()
        self._setup_ui()

    def _setup_hardware(self):
        pins = settings.PINS
        self.water_valve = self.gpio.setup_output(pins["water_valve"], "water valve")
        self.rinse_valve = self.gpio.setup_output(pins["rinse_valve"], "rinse valve")
        courtesy = self.gpio.setup_output(pins["courtesy_light"], "courtesy light")
        ozone = self.gpio.setup_output(pins["ozone"], "ozone")
        uv = self.gpio.setup_output(pins["uv_lamp"], "uv lamp")
        coin_input = self.gpio.setup_input(pins["coin_input"], "coin input", pull_up=True)

        self.aux = AuxiliaryOutputs(self.gpio, courtesy, ozone, uv)
        self.valves = ValveController(self.gpio, self.water_valve, self.rinse_valve, self.aux)

        self.coin_acceptor = CoinAcceptor(self.gpio, coin_input, self.coin_inserted.emit)
        self.coin_inserted.connect(self._handle_coin)

        self.courtesy_timer = QTimer(self)
        self.courtesy_timer.setSingleShot(True)
        self.courtesy_timer.timeout.connect(self._courtesy_off)

    def _setup_ui(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.product_screen = ProductScreen(settings.PRODUCTS, settings.LOGO_IMAGE)
        self.payment_screen = PaymentScreen(settings.COIN_IMAGE)
        self.dispensing_screen = DispensingScreen()

        self.stack.addWidget(self.product_screen)
        self.stack.addWidget(self.payment_screen)
        self.stack.addWidget(self.dispensing_screen)

        self.product_screen.product_selected.connect(self._go_payment)
        self.product_screen.rinse_requested.connect(self._rinse_nozzle)
        self.payment_screen.back_pressed.connect(self._go_products)
        self.payment_screen.confirm_pressed.connect(self._confirm_dispense)
        self.dispensing_screen.progress_changed.connect(self.valves.update_progress)
        self.dispensing_screen.completed.connect(self._complete_sale)

        self.interactions = InteractionFilter(self)
        self.interactions.interacted.connect(self._touch_interaction)
        self.installEventFilter(self.interactions)

    def show_startup(self):
        if settings.FULLSCREEN:
            self.showFullScreen()
        else:
            self.resize(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            self.show()

    def _touch_interaction(self):
        self._courtesy_on()

    def _courtesy_on(self):
        try:
            self.aux.courtesy_on()
            self.courtesy_timer.start(settings.COURTESY_LIGHT_TIMEOUT_MS)
        except GPIOControllerError as exc:
            logger.error(str(exc))

    def _courtesy_off(self):
        try:
            self.aux.courtesy_off()
        except GPIOControllerError as exc:
            logger.error(str(exc))

    def _go_products(self):
        self.stack.setCurrentWidget(self.product_screen)

    def _go_payment(self, product):
        self._touch_interaction()
        self.current_product = product
        self.payment_screen.set_product(product)
        self.payment_screen.set_credit(self.credit)
        self.stack.setCurrentWidget(self.payment_screen)

    def _handle_coin(self):
        self._touch_interaction()
        self.credit += settings.COIN_VALUE
        self.payment_screen.set_credit(self.credit)
        self.payment_screen.animate_coin()

    def _confirm_dispense(self):
        if not self.current_product:
            return
        if self.credit < self.current_product["price"]:
            QMessageBox.warning(self, "Insufficient credit", "Please insert more coins.")
            return
        self.stack.setCurrentWidget(self.dispensing_screen)
        total_s = self.current_product["volume_l"] * settings.FILL_SECONDS_PER_LITER
        try:
            self.valves.start_dispense()
            self.dispensing_screen.start(total_s)
        except GPIOControllerError as exc:
            QMessageBox.critical(self, "GPIO error", str(exc))
            self._go_products()

    def _complete_sale(self):
        try:
            self.valves.finish_dispense()
        except GPIOControllerError as exc:
            QMessageBox.critical(self, "GPIO error", str(exc))

        sale = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "product": self.current_product["name"],
            "volume": self.current_product["volume_l"],
            "price": self.current_product["price"],
            "payment_received": self.credit,
        }
        self.sales_db.log_sale(sale)
        self.credit = max(0.0, self.credit - self.current_product["price"])
        self.payment_screen.set_credit(self.credit)
        self._go_products()

    def _rinse_nozzle(self):
        self._touch_interaction()
        try:
            self.valves.rinse_start()
            QTimer.singleShot(2500, self.valves.rinse_stop)
        except GPIOControllerError as exc:
            QMessageBox.critical(self, "GPIO error", str(exc))
