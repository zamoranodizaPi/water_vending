"""Main kiosk window for the water vending machine."""
from __future__ import annotations

import logging
from datetime import datetime

from PyQt5.QtCore import QObject, QEvent, QTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from config import settings
from database.sales_db import SalesDB
from hardware.auxiliary_outputs import AuxiliaryOutputs
from hardware.coin_acceptor import CoinAcceptor
from hardware.gpio_controller import GPIOController, GPIOControllerError
from hardware.valve_controller import ValveController
from ui.dispensing_screen import DispensingScreen
from ui.payment_screen import MessageScreen, PromptScreen
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
        self.flow_step = None
        self.wants_rinse = False

        self.products = {p["id"]: p for p in settings.PRODUCTS}
        self.sales_db = SalesDB(settings.DB_PATH)
        self.gpio = GPIOController()
        self._setup_hardware()
        self._setup_ui()
        self._refresh_product_enablement()

    def _setup_hardware(self):
        pins = settings.PINS
        self.water_valve = self.gpio.setup_output(pins["water_valve"], "water valve")
        self.rinse_valve = self.gpio.setup_output(pins["rinse_valve"], "rinse valve")
        courtesy = self.gpio.setup_output(pins["courtesy_light"], "courtesy light")
        ozone = self.gpio.setup_output(pins["ozone"], "ozone")
        uv = self.gpio.setup_output(pins["uv_lamp"], "uv lamp")

        coin_input_27 = self.gpio.setup_input(pins["coin_input"], "coin input gpio27", pull_up=True)
        coin_input_12 = self.gpio.setup_input(pins["coin_pulse"], "coin pulse gpio12", pull_up=True)
        self.coin_acceptor_27 = CoinAcceptor(self.gpio, coin_input_27, self.coin_inserted.emit)
        self.coin_acceptor_12 = CoinAcceptor(self.gpio, coin_input_12, self.coin_inserted.emit)
        self.coin_inserted.connect(self._handle_coin)

        self.select_full = self.gpio.setup_input(pins["select_full"], "select full", pull_up=True)
        self.select_half = self.gpio.setup_input(pins["select_half"], "select half", pull_up=True)
        self.select_gallon = self.gpio.setup_input(pins["select_gallon"], "select gallon", pull_up=True)
        self.select_full.when_pressed = lambda: self._select_by_gpio("full_garrafon")
        self.select_half.when_pressed = lambda: self._select_by_gpio("half_garrafon")
        self.select_gallon.when_pressed = lambda: self._select_by_gpio("gallon")

        self.aux = AuxiliaryOutputs(self.gpio, courtesy, ozone, uv)
        self.valves = ValveController(self.gpio, self.water_valve, self.rinse_valve, self.aux)

        self.courtesy_timer = QTimer(self)
        self.courtesy_timer.setSingleShot(True)
        self.courtesy_timer.timeout.connect(self._courtesy_off)

    def _setup_ui(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.product_screen = ProductScreen(settings.PRODUCTS, settings.LOGO_IMAGE)
        self.prompt_screen = PromptScreen()
        self.progress_screen = DispensingScreen()
        self.message_screen = MessageScreen()

        self.stack.addWidget(self.product_screen)
        self.stack.addWidget(self.prompt_screen)
        self.stack.addWidget(self.progress_screen)
        self.stack.addWidget(self.message_screen)

        self.product_screen.product_selected.connect(self._set_selected_product)
        self.product_screen.ok_pressed.connect(self._on_ok_home)
        self.product_screen.rinse_pressed.connect(self._on_rinse_home)
        self.prompt_screen.ok_pressed.connect(self._on_prompt_ok)
        self.progress_screen.progress_changed.connect(self._on_progress_changed)
        self.progress_screen.completed.connect(self._on_progress_completed)

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

    def _handle_coin(self):
        self._touch_interaction()
        self.credit += settings.COIN_VALUE
        self.product_screen.set_credit(self.credit)
        self.product_screen.set_status("Moneda recibida")
        QTimer.singleShot(700, lambda: self.product_screen.set_status(""))
        self._refresh_product_enablement()

    def _refresh_product_enablement(self):
        for product in settings.PRODUCTS:
            enabled = self.credit >= product["price"]
            self.product_screen.set_product_enabled(product["id"], enabled)

        has_any = any(self.credit >= p["price"] for p in settings.PRODUCTS)
        self.product_screen.set_ok_enabled(has_any and self.current_product is not None)

        if self.current_product and self.current_product["id"] == "gallon":
            self.product_screen.set_rinse_enabled(False)
        else:
            self.product_screen.set_rinse_enabled(self.current_product is not None)

    def _select_by_gpio(self, product_id: str):
        self._touch_interaction()
        product = self.products[product_id]
        if self.credit < product["price"]:
            self._show_temporary_status("Crédito Insuficiente")
            return
        self._set_selected_product(product_id)

    def _set_selected_product(self, product_id: str):
        self.current_product = self.products[product_id]
        self.product_screen.set_selected(product_id)
        self._refresh_product_enablement()

    def _show_temporary_status(self, text: str, ms: int = 1000):
        self.product_screen.set_status(text)
        QTimer.singleShot(ms, lambda: self.product_screen.set_status(""))

    def _on_ok_home(self):
        if not self.current_product or self.credit < self.current_product["price"]:
            self._show_temporary_status("Crédito Insuficiente")
            return
        self.wants_rinse = False
        self._show_upright_prompt()

    def _on_rinse_home(self):
        if not self.current_product:
            self._show_temporary_status("Seleccione producto")
            return
        if self.current_product["id"] == "gallon":
            self._show_temporary_status("Enjuague no disponible para galón")
            return
        if self.credit < self.current_product["price"]:
            self._show_temporary_status("Crédito Insuficiente")
            return
        self.wants_rinse = True
        self.flow_step = "await_rinse_position"
        self.prompt_screen.configure(
            "Coloque Garrafón Boca Abajo",
            settings.UPSIDE_DOWN_IMAGE,
            "Presione OK Cuando Termine",
        )
        self.stack.setCurrentWidget(self.prompt_screen)

    def _show_upright_prompt(self):
        self.flow_step = "await_fill_position"
        self.prompt_screen.configure(
            "Coloque Garrafón Boca Arriba",
            settings.UPRIGHT_IMAGE,
            "Presione OK Cuando Termine",
        )
        self.stack.setCurrentWidget(self.prompt_screen)

    def _on_prompt_ok(self):
        if self.flow_step == "await_rinse_position":
            self.flow_step = "rinsing"
            try:
                self.valves.rinse_start()
            except GPIOControllerError as exc:
                self._show_temporary_status(str(exc))
                self._reset_to_home()
                return
            self.stack.setCurrentWidget(self.progress_screen)
            self.progress_screen.start("Enjuagando", settings.RINSE_SECONDS)
        elif self.flow_step == "await_fill_position":
            self._start_filling()

    def _start_filling(self):
        self.flow_step = "filling"
        self.stack.setCurrentWidget(self.progress_screen)
        total_s = self.current_product["volume_l"] * settings.FILL_SECONDS_PER_LITER
        try:
            self.valves.start_dispense()
            self.progress_screen.start("Llenando", total_s)
        except GPIOControllerError as exc:
            self._show_temporary_status(str(exc))
            self._reset_to_home()

    def _on_progress_changed(self, progress: int):
        if self.flow_step == "filling":
            self.valves.update_progress(progress)

    def _on_progress_completed(self):
        if self.flow_step == "rinsing":
            try:
                self.valves.rinse_stop()
            except GPIOControllerError as exc:
                self._show_temporary_status(str(exc))
                self._reset_to_home()
                return
            self._show_upright_prompt()
            return

        if self.flow_step == "filling":
            try:
                self.valves.finish_dispense()
            except GPIOControllerError as exc:
                logger.error(str(exc))
            self._complete_sale()

    def _complete_sale(self):
        sale = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "product": self.current_product["name"],
            "volume": self.current_product["volume_l"],
            "price": self.current_product["price"],
            "payment_received": self.credit,
        }
        self.sales_db.log_sale(sale)

        change = self.credit - self.current_product["price"]
        self.credit = max(0.0, change)
        self.product_screen.set_credit(self.credit)

        if change > 0:
            self.message_screen.set_message("Recoja su cambio")
            self.stack.setCurrentWidget(self.message_screen)
            QTimer.singleShot(3000, self._show_thanks)
        else:
            self._show_thanks()

    def _show_thanks(self):
        self.message_screen.set_message("Tome Su Producto\nGracias por su Compra!!!")
        self.stack.setCurrentWidget(self.message_screen)
        QTimer.singleShot(3000, self._reset_to_home)

    def _reset_to_home(self):
        self.current_product = None
        self.wants_rinse = False
        self.flow_step = None
        self.product_screen.set_selected(None)
        self.product_screen.set_status("")
        self._refresh_product_enablement()
        self.stack.setCurrentWidget(self.product_screen)
