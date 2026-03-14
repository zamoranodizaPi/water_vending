"""Main kiosk window for the water vending machine."""
from __future__ import annotations

import logging
import math
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
        self.current_fill_percent = 0

        self.products = {p["id"]: p for p in settings.PRODUCTS}
        self.sales_db = SalesDB(settings.DB_PATH)
        self.gpio = GPIOController()
        self._setup_hardware()
        self._setup_ui()
        self._refresh_product_enablement(initial=True)

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

        self.ok_input = self.gpio.setup_input(pins["ok_input"], "ok input", pull_up=True)
        self.rinse_input = self.gpio.setup_input(pins["rinse_input"], "rinse input", pull_up=True)
        self.emergency_input = self.gpio.setup_input(pins["emergency_stop"], "emergency stop", pull_up=True)
        self.ok_input.when_pressed = self._on_ok_home
        self.rinse_input.when_pressed = self._toggle_rinse_option
        self.emergency_input.when_pressed = self._on_emergency_stop

        self.aux = AuxiliaryOutputs(self.gpio, courtesy, ozone, uv)
        self.valves = ValveController(self.gpio, self.water_valve, self.rinse_valve, self.aux)

        self.courtesy_timer = QTimer(self)
        self.courtesy_timer.setSingleShot(True)
        self.courtesy_timer.timeout.connect(self._courtesy_off)

    def _setup_ui(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.product_screen = ProductScreen(settings.PRODUCTS, settings.LOGO_IMAGE, settings.COIN_IMAGE)
        self.prompt_screen = PromptScreen(settings.LOGO_IMAGE)
        self.progress_screen = DispensingScreen(settings.LOGO_IMAGE)
        self.message_screen = MessageScreen(settings.LOGO_IMAGE)

        self.stack.addWidget(self.product_screen)
        self.stack.addWidget(self.prompt_screen)
        self.stack.addWidget(self.progress_screen)
        self.stack.addWidget(self.message_screen)

        self.product_screen.product_selected.connect(self._set_selected_product)
        self.product_screen.ok_pressed.connect(self._on_ok_home)
        self.product_screen.rinse_pressed.connect(self._toggle_rinse_option)
        self.product_screen.disabled_control_touched.connect(self._on_disabled_control_touched)
        self.prompt_screen.ok_pressed.clicked.connect(self._on_prompt_ok)
        self.progress_screen.progress_changed.connect(self._on_progress_changed)
        self.progress_screen.completed.connect(self._on_progress_completed)
        self.progress_screen.emergency_pressed.connect(self._on_emergency_stop)

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
        if self.stack.currentWidget() == self.product_screen:
            min_price = min(p["price"] for p in settings.PRODUCTS)
            if self.credit < min_price:
                self.product_screen.show_alert("Ingrese credito", ms=3000)

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
        self._courtesy_on()
        self.credit += settings.COIN_VALUE
        self.product_screen.set_credit(self.credit)
        self._refresh_product_enablement()

    def _refresh_product_enablement(self, initial: bool = False):
        min_price = min(p["price"] for p in settings.PRODUCTS)
        if self.credit < min_price:
            self.product_screen.pulse_credit_attention()

        for product in settings.PRODUCTS:
            was_enabled = self.product_screen.cards[product["id"]].isEnabled()
            enabled = self.credit >= product["price"]
            self.product_screen.set_product_enabled(product["id"], enabled)
            if enabled and (not was_enabled) and (not initial):
                self.product_screen.cards[product["id"]].pulse_attention(3)

        has_any = any(self.credit >= p["price"] for p in settings.PRODUCTS)
        self.product_screen.set_ok_enabled(has_any)

        if self.current_product and self.current_product["id"] == "gallon":
            self.product_screen.set_rinse_enabled(False)
            self.product_screen.set_rinse_checked(False)
            self.product_screen.lock_rinse_selection(False)
        else:
            self.product_screen.set_rinse_enabled(True)

    def _show_credit_insufficient(self):
        self.product_screen.show_alert("Credito Insuficiente", ms=3000)
        self.product_screen.show_credit_warning("Credito Insuficiente")
        QTimer.singleShot(3000, lambda: self.product_screen.set_credit(self.credit))

    def _on_disabled_control_touched(self, _control_name: str):
        has_any = any(self.credit >= p["price"] for p in settings.PRODUCTS)
        if not has_any:
            self._show_credit_insufficient()


    def _select_by_gpio(self, product_id: str):
        self._touch_interaction()
        product = self.products[product_id]
        if self.credit < product["price"]:
            self._show_credit_insufficient()
            return
        self._set_selected_product(product_id)

    def _set_selected_product(self, product_id: str):
        product = self.products[product_id]
        if self.credit < product["price"]:
            self._show_credit_insufficient()
            return
        self.current_product = product
        self.product_screen.set_selected(product_id)
        self._refresh_product_enablement()

    def _toggle_rinse_option(self):
        if self.current_product and self.current_product["id"] == "gallon":
            self.product_screen.set_rinse_checked(False)
            self.product_screen.lock_rinse_selection(False)
            return
        if self.product_screen.is_rinse_checked():
            self.product_screen.lock_rinse_selection(True)
            return
        self.product_screen.set_rinse_checked(True)
        self.product_screen.lock_rinse_selection(True)

    def _on_ok_home(self):
        self._touch_interaction()
        if not self.current_product:
            if any(self.credit >= p["price"] for p in settings.PRODUCTS):
                self.product_screen.blink_enabled_products()
                self.product_screen.show_alert("Seleccione un producto", ms=2500)
            else:
                self._show_credit_insufficient()
            return

        if self.credit < self.current_product["price"]:
            self._show_credit_insufficient()
            return

        if self.product_screen.is_rinse_checked() and self.current_product["id"] != "gallon":
            self.flow_step = "await_rinse_position"
            self.prompt_screen.configure(
                "Coloque Garrafón Boca Abajo",
                settings.UPSIDE_DOWN_IMAGE,
                "Presione OK Cuando Termine",
            )
            self.stack.setCurrentWidget(self.prompt_screen)
            return

        self._show_upright_prompt()

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
                logger.error(str(exc))
                self._reset_to_home()
                return
            self.stack.setCurrentWidget(self.progress_screen)
            self.progress_screen.start(
                "Enjuagando",
                settings.RINSE_SECONDS,
                gif_path=settings.RINSING_GIF,
                emergency_enabled=False,
            )
        elif self.flow_step == "await_fill_position":
            self._start_filling()

    def _start_filling(self):
        self.flow_step = "filling"
        self.current_fill_percent = 0
        self.stack.setCurrentWidget(self.progress_screen)
        total_s = self.current_product["volume_l"] * settings.FILL_SECONDS_PER_LITER
        try:
            self.valves.start_dispense()
            self.progress_screen.start(
                "Llenando",
                total_s,
                gif_path=settings.FILLING_GIF,
                emergency_enabled=True,
            )
        except GPIOControllerError as exc:
            logger.error(str(exc))
            self._reset_to_home()

    def _on_progress_changed(self, progress: int):
        self.current_fill_percent = progress
        if self.flow_step == "filling":
            self.valves.update_progress(progress)

    def _on_emergency_stop(self):
        if self.flow_step != "filling":
            return
        self.progress_screen.stop_now()
        try:
            self.valves.finish_dispense()
        except GPIOControllerError as exc:
            logger.error(str(exc))
        self._complete_sale(emergency=True)

    def _on_progress_completed(self):
        if self.flow_step == "rinsing":
            try:
                self.valves.rinse_stop()
            except GPIOControllerError as exc:
                logger.error(str(exc))
                self._reset_to_home()
                return
            self._show_upright_prompt()
            return

        if self.flow_step == "filling":
            try:
                self.valves.finish_dispense()
            except GPIOControllerError as exc:
                logger.error(str(exc))
            self._complete_sale(emergency=False)

    def _complete_sale(self, emergency: bool = False):
        if emergency:
            served_liters = round((self.current_fill_percent / 100.0) * self.current_product["volume_l"], 2)
            raw_charge = served_liters * settings.EMERGENCY_RATE_PER_LITER
            price_to_charge = float(math.ceil(raw_charge)) if raw_charge > 0 else 0.0
        else:
            served_liters = self.current_product["volume_l"]
            price_to_charge = self.current_product["price"]

        sale = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "product": self.current_product["name"],
            "volume": served_liters,
            "price": price_to_charge,
            "payment_received": self.credit,
        }
        self.sales_db.log_sale(sale)

        change = max(0.0, round(self.credit - price_to_charge, 2))

        if emergency:
            self.message_screen.set_message(
                f"Paro activado\nDespachado: {served_liters:.2f} L\nTotal a cobrar: ${price_to_charge:.2f}"
            )
            self.stack.setCurrentWidget(self.message_screen)
            QTimer.singleShot(3200, lambda: self._process_change(change))
            return

        self._process_change(change)

    def _process_change(self, change: float):
        if change > 0:
            self.message_screen.set_message(f"Recoja su cambio\nTotal a reembolsar: ${change:.2f}", settings.CHANGE_GIF)
            self.stack.setCurrentWidget(self.message_screen)
            self.credit = 0.0
            self.product_screen.set_credit(self.credit)
            QTimer.singleShot(3000, self._show_thanks)
        else:
            self.credit = 0.0
            self.product_screen.set_credit(self.credit)
            self._show_thanks()

    def _show_thanks(self):
        self.message_screen.set_message("Gracias por su Compra!!!", settings.THANKS_GIF)
        self.stack.setCurrentWidget(self.message_screen)
        QTimer.singleShot(3000, self._reset_to_home)

    def _reset_to_home(self):
        self.current_product = None
        self.flow_step = None
        self.current_fill_percent = 0
        self.product_screen.set_selected(None)
        self.product_screen.set_rinse_checked(False)
        self.product_screen.lock_rinse_selection(False)
        self._refresh_product_enablement()
        self.stack.setCurrentWidget(self.product_screen)
