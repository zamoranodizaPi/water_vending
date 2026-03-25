"""Main kiosk window for the water vending machine."""
from __future__ import annotations

import logging
import math
import time
from datetime import datetime

from PyQt5.QtCore import QObject, QEvent, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from config import settings
from database.sales_db import SalesDB
from hardware.auxiliary_outputs import AuxiliaryOutputs
from hardware.button_led_controller import ButtonLedController
from hardware.coin_acceptor import CoinAcceptor
from hardware.email_notifier import send_async_email
from hardware.gpio_controller import GPIOController, GPIOControllerError
from hardware.valve_controller import ValveController
from ui.audio_manager import AudioManager
from ui.config_screen import ConfigCodeScreen, ConfigHoldScreen, ConfigMenuScreen, ConfigTextScreen, ConfigValueScreen
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
    coin_inserted = pyqtSignal(int)
    hardware_product_selected = pyqtSignal(str)
    hardware_ok_pressed = pyqtSignal()
    hardware_emergency_pressed = pyqtSignal()
    hardware_emergency_held = pyqtSignal()
    hardware_service_empty = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(settings.WINDOW_TITLE)
        self.setCursor(QCursor(Qt.BlankCursor))
        self.current_product = None
        self.credit = 0.0
        self.flow_step = None
        self.current_fill_percent = 0
        self._service_lock_active = False
        self._rinse_charge_pending = False
        self._played_75_audio = False
        self._last_input_at: dict[str, float] = {}
        self._selection_reset_timer = QTimer(self)
        self._selection_reset_timer.setSingleShot(True)
        self._selection_reset_timer.timeout.connect(self._clear_selection_to_idle)
        self._selection_countdown_timer = QTimer(self)
        self._selection_countdown_timer.setInterval(1000)
        self._selection_countdown_timer.timeout.connect(self._tick_selection_countdown)
        self._selection_countdown_remaining = 0
        self._prompt_timeout_timer = QTimer(self)
        self._prompt_timeout_timer.setSingleShot(True)
        self._prompt_timeout_timer.timeout.connect(self._handle_prompt_timeout)
        self._prompt_countdown_timer = QTimer(self)
        self._prompt_countdown_timer.setInterval(1000)
        self._prompt_countdown_timer.timeout.connect(self._tick_prompt_countdown)
        self._prompt_countdown_remaining = 0
        self._config_hold_timer = QTimer(self)
        self._config_hold_timer.setInterval(100)
        self._config_hold_timer.timeout.connect(self._poll_config_activation)
        self._config_hold_elapsed_ms = 0
        self._service_level_timer = QTimer(self)
        self._service_level_timer.setInterval(150)
        self._service_level_timer.timeout.connect(self._poll_service_level)
        self._config_mode: str | None = None
        self._config_draft = settings.get_runtime_config()
        self._config_menu_options = [
            "Ajustar precios",
            "Cambiar nombres",
            "Cambiar volúmenes",
            "Cambiar nombre sistema",
            "Cambiar contacto",
            "Ajustar tiempo por litro",
            "Cambiar código",
            "Guardar y salir",
            "Cancelar",
        ]
        self._config_menu_index = 0
        self._config_price_index = 0
        self._config_name_index = 0
        self._config_volume_index = 0
        self._config_contact_field = "correo"
        self._config_new_code = ""
        self._config_edit_value = 0.0

        self.products = {p["id"]: p for p in settings.PRODUCTS}
        self.sales_db = SalesDB(settings.DB_PATH)
        self.audio = AudioManager(settings.AUDIO_FILES, self)
        self.gpio = GPIOController()
        self._setup_hardware()
        self._setup_ui()
        self._config_hold_timer.start()
        self._service_level_timer.start()
        self._refresh_product_enablement(initial=True)
        self._poll_service_level()

    def _setup_hardware(self):
        pins = settings.PINS
        self.water_valve = self.gpio.setup_output(pins["water_valve"], "water valve")
        self.rinse_valve = self.gpio.setup_output(pins["rinse_valve"], "rinse valve")
        courtesy = self.gpio.setup_output(pins["courtesy_light"], "courtesy light")
        ozone = self.gpio.setup_output(pins["ozone"], "ozone")
        uv = self.gpio.setup_output(pins["uv_lamp"], "uv lamp")
        led_full = self.gpio.setup_pwm_output(pins["led_select_full"], "full selector")
        led_half = self.gpio.setup_pwm_output(pins["led_select_half"], "half selector")
        led_gallon = self.gpio.setup_pwm_output(pins["led_select_gallon"], "gallon selector")
        led_ok = self.gpio.setup_pwm_output(pins["led_ok"], "ok button")
        led_emergency = self.gpio.setup_pwm_output(pins["led_emergency"], "emergency button")

        self.coin_acceptor = CoinAcceptor(
            pins["coin_pulse"],
            self.coin_inserted.emit,
            flush_window_s=0.3,
            min_gap_us=30000,
            min_width_us=30000,
            max_width_us=220000,
            poll_ms=50,
            parent=self,
        )
        self.coin_inserted.connect(self._handle_coin)

        self.select_full = self.gpio.setup_input(pins["select_full"], "select full", pull_up=True)
        self.select_half = self.gpio.setup_input(pins["select_half"], "select half", pull_up=True)
        self.select_gallon = self.gpio.setup_input(pins["select_gallon"], "select gallon", pull_up=True)
        self.select_full.when_pressed = lambda: self.hardware_product_selected.emit("full_garrafon")
        self.select_half.when_pressed = lambda: self.hardware_product_selected.emit("half_garrafon")
        self.select_gallon.when_pressed = lambda: self.hardware_product_selected.emit("gallon")

        self.ok_input = self.gpio.setup_input(pins["ok_input"], "ok input", pull_up=True)
        self.emergency_input = self.gpio.setup_input(pins["emergency_stop"], "emergency stop", pull_up=True)
        self.service_level_input = self.gpio.setup_input(pins["service_level"], "service level", pull_up=True)
        self.ok_input.when_pressed = self.hardware_ok_pressed.emit
        self.emergency_input.when_pressed = self.hardware_emergency_pressed.emit
        self.service_level_input.when_pressed = self.hardware_service_empty.emit
        self.emergency_input.hold_time = 10.0
        self.emergency_input.hold_repeat = False
        self.emergency_input.when_held = self.hardware_emergency_held.emit

        self.aux = AuxiliaryOutputs(self.gpio, courtesy, ozone, uv)
        self.valves = ValveController(self.gpio, self.water_valve, self.rinse_valve, self.aux)
        self.button_leds = ButtonLedController(
            self.gpio,
            {
                "full": led_full,
                "half": led_half,
                "gallon": led_gallon,
                "ok": led_ok,
                "emergency": led_emergency,
            },
            settings.PRODUCTS,
            self,
        )

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
        self.config_hold_screen = ConfigHoldScreen(settings.LOGO_IMAGE)
        self.config_code_screen = ConfigCodeScreen(settings.LOGO_IMAGE)
        self.config_menu_screen = ConfigMenuScreen(settings.LOGO_IMAGE)
        self.config_text_screen = ConfigTextScreen(settings.LOGO_IMAGE)
        self.config_value_screen = ConfigValueScreen(settings.LOGO_IMAGE)

        self.stack.addWidget(self.product_screen)
        self.stack.addWidget(self.prompt_screen)
        self.stack.addWidget(self.progress_screen)
        self.stack.addWidget(self.message_screen)
        self.stack.addWidget(self.config_hold_screen)
        self.stack.addWidget(self.config_code_screen)
        self.stack.addWidget(self.config_menu_screen)
        self.stack.addWidget(self.config_text_screen)
        self.stack.addWidget(self.config_value_screen)

        self.product_screen.product_selected.connect(self._set_selected_product)
        self.product_screen.ok_pressed.connect(self._on_ok_home)
        self.product_screen.top_left_corner_pressed.connect(self._add_service_credit)
        self.product_screen.credit_box_pressed.connect(self._add_credit_box_amount)
        self.prompt_screen.ok_pressed.clicked.connect(self._on_prompt_ok)
        self.progress_screen.progress_changed.connect(self._on_progress_changed)
        self.progress_screen.completed.connect(self._on_progress_completed)
        self.progress_screen.emergency_pressed.connect(self._on_emergency_stop)
        self.button_leds.attention_started.connect(self._on_idle_attention_started)
        self.hardware_product_selected.connect(self._select_by_gpio)
        self.hardware_ok_pressed.connect(self._handle_ok_input)
        self.hardware_emergency_pressed.connect(self._handle_emergency_input)
        self.hardware_emergency_held.connect(self._handle_emergency_hold)
        self.hardware_service_empty.connect(self._activate_out_of_service)

        self.interactions = InteractionFilter(self)
        self.interactions.interacted.connect(self._touch_interaction)
        self.installEventFilter(self.interactions)
        self._update_credit_displays()

    def show_startup(self):
        self.audio.play("welcome")
        if settings.FULLSCREEN:
            self.showFullScreen()
        else:
            self.resize(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            self.show()

    def _touch_interaction(self):
        if self._service_lock_active:
            return
        if self._in_config_flow():
            return
        self._courtesy_on()
        self.button_leds.note_interaction()

    def _in_config_flow(self) -> bool:
        return self._config_mode is not None

    def _can_enter_config_mode(self) -> bool:
        return (
            self.stack.currentWidget() in {self.product_screen, self.config_hold_screen}
            and self.flow_step is None
            and self.current_product is None
        )

    def _poll_config_activation(self):
        if self._service_lock_active:
            return
        if self._in_config_flow():
            return
        ok_pressed = bool(getattr(self.ok_input, "is_pressed", False))
        cancel_pressed = bool(getattr(self.emergency_input, "is_pressed", False))
        if self._can_enter_config_mode() and ok_pressed and cancel_pressed:
            self._config_hold_elapsed_ms += self._config_hold_timer.interval()
            self.config_hold_screen.set_progress(int((self._config_hold_elapsed_ms / 10000) * 100))
            if self.stack.currentWidget() != self.config_hold_screen:
                self.stack.setCurrentWidget(self.config_hold_screen)
            if self._config_hold_elapsed_ms >= 10000:
                self._config_hold_elapsed_ms = 0
                self._start_config_login()
            return
        if self.stack.currentWidget() == self.config_hold_screen:
            self.stack.setCurrentWidget(self.product_screen)
        self._config_hold_elapsed_ms = 0
        self.config_hold_screen.set_progress(0)

    def _poll_service_level(self):
        if self._service_lock_active:
            if self.stack.currentWidget() != self.message_screen:
                self.stack.setCurrentWidget(self.message_screen)
            return
        if bool(getattr(self.service_level_input, "is_pressed", False)):
            self._activate_out_of_service()

    def _service_contact_message(self) -> str:
        email = settings.CONTACT_EMAIL or "zamoranodiza@hotmail.com"
        phone = settings.CONTACT_PHONE or "7771033646"
        return (
            "Lo sentimos no tenemos servicio en este momento\n"
            "Contacte a\n"
            f"{email}\n"
            f"{phone}"
        )

    def _send_out_of_service_email(self):
        recipient = settings.CONTACT_EMAIL
        if not recipient:
            return
        now = datetime.now()
        system_name = settings.SYSTEM_NAME or "Vending 1"
        subject = f"Fuera de servicio - {system_name} - {now.strftime('%Y-%m-%d %H:%M:%S')}"
        body = (
            "Alerta de fuera de servicio\n\n"
            f"Sistema: {system_name}\n"
            f"Hora: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            "Motivo: sensor de nivel de agua en cero.\n"
        )
        send_async_email(recipient=recipient, subject=subject, body=body)

    def _activate_out_of_service(self):
        if self._service_lock_active:
            if self.stack.currentWidget() != self.message_screen:
                self.stack.setCurrentWidget(self.message_screen)
            return
        self._service_lock_active = True
        self._config_mode = None
        self._config_hold_elapsed_ms = 0
        self.config_hold_screen.set_progress(0)
        self._selection_reset_timer.stop()
        self._selection_countdown_timer.stop()
        self._selection_countdown_remaining = 0
        self._prompt_timeout_timer.stop()
        self._prompt_countdown_timer.stop()
        self._prompt_countdown_remaining = 0
        self.product_screen.clear_alert()
        self.product_screen.set_selected(None)
        self.product_screen.set_countdown(None)
        self.product_screen.set_section_message(None)
        self.prompt_screen.set_prompt_countdown(None)
        self.progress_screen.stop_now()
        self.current_product = None
        self.flow_step = None
        self.current_fill_percent = 0
        self._rinse_charge_pending = False
        try:
            self.valves.finish_dispense()
        except Exception:
            pass
        try:
            self.valves.rinse_stop()
        except Exception:
            pass
        self.coin_acceptor.shutdown()
        self.button_leds.shutdown()
        self.message_screen.set_message(
            self._service_contact_message(),
            image_path=settings.SORRY_IMAGE,
            image_size=(300, 260),
        )
        self.stack.setCurrentWidget(self.message_screen)
        self.audio.play("out_of_service")
        self._send_out_of_service_email()

    def _config_entry_hold_pressed(self) -> bool:
        return (
            self._can_enter_config_mode()
            and bool(getattr(self.ok_input, "is_pressed", False))
            and bool(getattr(self.emergency_input, "is_pressed", False))
        )

    def _start_config_login(self):
        self._config_mode = "login"
        self._config_draft = settings.get_runtime_config()
        self._config_new_code = ""
        self.config_code_screen.configure("Ingrese código", "Código de acceso", "0000")
        self.stack.setCurrentWidget(self.config_code_screen)

    def _open_config_menu(self):
        self._config_mode = "menu"
        self.config_menu_screen.configure(self._config_menu_options, self._config_menu_index)
        self.stack.setCurrentWidget(self.config_menu_screen)

    def _open_price_screen(self):
        self._config_mode = "price"
        self._config_price_index = 0
        price_keys = ["garrafon", "medio", "galon"]
        self._config_edit_value = float(self._config_draft["precios"][price_keys[self._config_price_index]])
        self._refresh_price_screen()
        self.stack.setCurrentWidget(self.config_value_screen)

    def _refresh_price_screen(self):
        labels = [
            ("Garrafón", "garrafon"),
            ("Medio", "medio"),
            ("Galón", "galon"),
        ]
        name, key = labels[self._config_price_index]
        value = self._config_edit_value
        self.config_value_screen.configure(
            "Ajustar precios",
            f"{name} - Precio actual",
            f"${value:.2f}",
            "P1:+  P2:-  OK:guardar  Cancelar:volver",
        )

    def _open_time_screen(self):
        self._config_mode = "time"
        self._config_edit_value = float(self._config_draft["tiempo_por_litro"])
        self._refresh_time_screen()
        self.stack.setCurrentWidget(self.config_value_screen)

    def _open_name_screen(self):
        self._config_mode = "name"
        self._config_name_index = 0
        self._refresh_name_screen()
        self.stack.setCurrentWidget(self.config_text_screen)

    def _refresh_name_screen(self):
        labels = [
            ("Garrafón", "garrafon"),
            ("Medio", "medio"),
            ("Galón", "galon"),
        ]
        name, key = labels[self._config_name_index]
        self.config_text_screen.configure(
            "Cambiar nombres",
            f"{name} - Nombre visible",
            self._config_draft["nombres"][key],
            max_length=18,
            empty_value="Producto",
        )

    def _open_volume_screen(self):
        self._config_mode = "volume"
        self._config_volume_index = 0
        volume_keys = ["garrafon", "medio", "galon"]
        self._config_edit_value = float(self._config_draft["volumenes"][volume_keys[self._config_volume_index]])
        self._refresh_volume_screen()
        self.stack.setCurrentWidget(self.config_value_screen)

    def _refresh_volume_screen(self):
        labels = [
            ("Garrafón", "garrafon"),
            ("Medio", "medio"),
            ("Galón", "galon"),
        ]
        name, key = labels[self._config_volume_index]
        value = self._config_edit_value
        self.config_value_screen.configure(
            "Cambiar volúmenes",
            f"{name} - Volumen actual",
            f"{value:.2f} L",
            "P1:+0.1  P2:-0.1  OK:guardar  Cancelar:volver",
        )

    def _open_contact_screen(self):
        self._config_contact_field = "correo"
        self._refresh_contact_screen()
        self.stack.setCurrentWidget(self.config_text_screen)

    def _open_system_name_screen(self):
        self._config_mode = "system_name"
        self.config_text_screen.configure(
            "Nombre del sistema",
            "Identificación del vending",
            self._config_draft["nombre_sistema"],
            max_length=20,
            empty_value="Vending 1",
        )
        self.stack.setCurrentWidget(self.config_text_screen)

    def _refresh_contact_screen(self):
        if self._config_contact_field == "correo":
            self._config_mode = "contact_email"
            self.config_text_screen.configure(
                "Cambiar contacto",
                "Correo electrónico",
                self._config_draft["contacto"]["correo"],
                max_length=24,
                empty_value="",
            )
            return
        self._config_mode = "contact_phone"
        self.config_text_screen.configure(
            "Cambiar contacto",
            "Teléfono",
            self._config_draft["contacto"]["telefono"],
            max_length=20,
            empty_value="",
        )

    def _refresh_time_screen(self):
        self.config_value_screen.configure(
            "Tiempo por litro",
            "Ajuste de precisión",
            f"{self._config_edit_value:.2f} seg/L",
            "P1:+0.01  P2:-0.01  OK:guardar  Cancelar:volver",
        )

    def _open_code_change(self):
        self._config_mode = "code_new"
        self.config_code_screen.configure("Nuevo código", "Ingrese nuevo código", "0000")
        self.stack.setCurrentWidget(self.config_code_screen)

    def _save_runtime_settings(self):
        saved = settings.save_runtime_config(self._config_draft)
        settings.apply_runtime_config(saved)
        self.products = {p["id"]: p for p in settings.PRODUCTS}
        self.product_screen.refresh_products()
        self.button_leds.products = sorted(settings.PRODUCTS, key=lambda product: product["price"])
        self._refresh_product_enablement(initial=True)

    def _exit_config_to_home(self):
        self._config_mode = None
        self._config_hold_elapsed_ms = 0
        self.config_hold_screen.set_progress(0)
        self.stack.setCurrentWidget(self.product_screen)
        self._refresh_product_enablement(initial=True)

    def _handle_config_product_button(self, product_id: str):
        if self._config_mode in {"login", "code_new", "code_confirm"}:
            if product_id == "full_garrafon":
                self.config_code_screen.increment_digit()
            elif product_id == "half_garrafon":
                self.config_code_screen.decrement_digit()
            elif product_id == "gallon":
                self.config_code_screen.next_digit()
            return
        if self._config_mode == "menu":
            if product_id == "full_garrafon":
                self.config_menu_screen.move_up()
            elif product_id == "half_garrafon":
                self.config_menu_screen.move_down()
            return
        if self._config_mode == "price":
            if product_id == "full_garrafon":
                self._config_edit_value = round(self._config_edit_value + 1, 2)
            elif product_id == "half_garrafon":
                self._config_edit_value = round(max(0, self._config_edit_value - 1), 2)
            self._refresh_price_screen()
            return
        if self._config_mode in {"name", "system_name", "contact_email", "contact_phone"}:
            if product_id == "full_garrafon":
                self.config_text_screen.increment_char()
            elif product_id == "half_garrafon":
                self.config_text_screen.decrement_char()
            elif product_id == "gallon":
                self.config_text_screen.next_char()
            return
        if self._config_mode == "volume":
            if product_id == "full_garrafon":
                self._config_edit_value = round(self._config_edit_value + 0.1, 2)
            elif product_id == "half_garrafon":
                self._config_edit_value = round(max(0.1, self._config_edit_value - 0.1), 2)
            self._refresh_volume_screen()
            return
        if self._config_mode == "time":
            if product_id == "full_garrafon":
                self._config_edit_value = round(self._config_edit_value + 0.01, 2)
            elif product_id == "half_garrafon":
                self._config_edit_value = round(max(0.01, self._config_edit_value - 0.01), 2)
            self._refresh_time_screen()

    def _handle_config_ok(self):
        if self._config_mode == "login":
            if self.config_code_screen.code() == settings.ACCESS_CODE:
                self._open_config_menu()
            else:
                self.config_code_screen.show_error("Código incorrecto")
            return
        if self._config_mode == "menu":
            option = self.config_menu_screen.current_option()
            self._config_menu_index = self.config_menu_screen.index
            if option == "Ajustar precios":
                self._open_price_screen()
            elif option == "Cambiar nombres":
                self._open_name_screen()
            elif option == "Cambiar volúmenes":
                self._open_volume_screen()
            elif option == "Cambiar nombre sistema":
                self._open_system_name_screen()
            elif option == "Cambiar contacto":
                self._open_contact_screen()
            elif option == "Ajustar tiempo por litro":
                self._open_time_screen()
            elif option == "Cambiar código":
                self._open_code_change()
            elif option == "Guardar y salir":
                self._save_runtime_settings()
                self._exit_config_to_home()
            elif option == "Cancelar":
                self._exit_config_to_home()
            return
        if self._config_mode == "price":
            price_keys = ["garrafon", "medio", "galon"]
            self._config_draft["precios"][price_keys[self._config_price_index]] = self._config_edit_value
            self._open_config_menu()
            return
        if self._config_mode == "name":
            name_keys = ["garrafon", "medio", "galon"]
            self._config_draft["nombres"][name_keys[self._config_name_index]] = self.config_text_screen.text()
            self._open_config_menu()
            return
        if self._config_mode == "system_name":
            self._config_draft["nombre_sistema"] = self.config_text_screen.text()
            self._open_config_menu()
            return
        if self._config_mode == "contact_email":
            self._config_draft["contacto"]["correo"] = self.config_text_screen.text()
            self._config_contact_field = "telefono"
            self._refresh_contact_screen()
            return
        if self._config_mode == "contact_phone":
            self._config_draft["contacto"]["telefono"] = self.config_text_screen.text()
            self._open_config_menu()
            return
        if self._config_mode == "volume":
            volume_keys = ["garrafon", "medio", "galon"]
            self._config_draft["volumenes"][volume_keys[self._config_volume_index]] = self._config_edit_value
            if self._config_volume_index < 2:
                self._config_volume_index += 1
                next_key = volume_keys[self._config_volume_index]
                self._config_edit_value = float(self._config_draft["volumenes"][next_key])
                self._refresh_volume_screen()
            else:
                self._open_config_menu()
            return
        if self._config_mode == "time":
            self._config_draft["tiempo_por_litro"] = self._config_edit_value
            self._open_config_menu()
            return
        if self._config_mode == "code_new":
            self._config_new_code = self.config_code_screen.code()
            self._config_mode = "code_confirm"
            self.config_code_screen.configure("Confirmar código", "Repita el nuevo código", "0000")
            return
        if self._config_mode == "code_confirm":
            if self.config_code_screen.code() != self._config_new_code:
                self.config_code_screen.show_error("Los códigos no coinciden")
                return
            self._config_draft["codigo"] = self._config_new_code
            self._open_config_menu()

    def _on_idle_attention_started(self):
        if self.stack.currentWidget() != self.product_screen:
            return
        if self.current_product is not None or self.flow_step is not None:
            return
        self.product_screen.play_idle_attention_animation()

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

    def _handle_coin(self, amount: int):
        if self._service_lock_active:
            return
        if self._in_config_flow():
            return
        if not self._accept_input("coin", 0.18):
            return
        self._touch_interaction()
        self.credit = min(999.0, self.credit + amount)
        self._update_credit_displays()
        self._sync_selection_countdown()
        self._refresh_product_enablement()
        print(f"Pulso detectado. Crédito: {int(self.credit)}")
        self.audio.queue(["coin_received", "credit_updated"])

    def _accept_input(self, name: str, min_interval_s: float) -> bool:
        now = time.monotonic()
        last_seen = self._last_input_at.get(name, 0.0)
        if now - last_seen < min_interval_s:
            logger.debug("Ignored bouncing input %s", name)
            return False
        self._last_input_at[name] = now
        return True

    def _add_service_credit(self):
        if self._service_lock_active:
            return
        if self._in_config_flow():
            return
        if self.stack.currentWidget() != self.product_screen:
            return
        self.credit += 1.0
        self._update_credit_displays()
        self._sync_selection_countdown()
        self._refresh_product_enablement()
        self.audio.queue(["coin_received", "credit_updated"])

    def _add_credit_box_amount(self):
        if self._service_lock_active:
            return
        if self._in_config_flow():
            return
        if self.stack.currentWidget() != self.product_screen:
            return
        self.credit += 2.0
        self._update_credit_displays()
        self._sync_selection_countdown()
        self._refresh_product_enablement()
        self.audio.queue(["coin_received", "credit_updated"])

    def _update_credit_displays(self):
        self.product_screen.set_credit(self.credit)
        self.prompt_screen.set_credit(self.credit)
        self.progress_screen.set_credit(self.credit)
        self.message_screen.set_credit(self.credit)

    def _refresh_product_enablement(self, initial: bool = False):
        if self._service_lock_active:
            return
        min_price = min(p["price"] for p in settings.PRODUCTS)
        if self.credit < min_price:
            self.product_screen.pulse_credit_attention()

        for product in settings.PRODUCTS:
            was_enabled = self.product_screen.cards[product["id"]].is_affordable()
            affordable = self.credit >= product["price"]
            self.product_screen.set_product_enabled(product["id"], affordable)
            if affordable and (not was_enabled) and (not initial):
                self.product_screen.cards[product["id"]].pulse_attention(3)

        self.product_screen.set_ok_enabled(True)
        self.button_leds.update_home(
            self.credit,
            self.current_product["id"] if self.current_product else None,
        )
        self._update_instruction_focus()

    def _update_instruction_focus(self):
        if self._service_lock_active:
            self.product_screen.set_instruction_focus(None)
            return
        if self.stack.currentWidget() != self.product_screen:
            self.product_screen.set_instruction_focus(None)
            return
        if self.credit > 0 and self.current_product is None:
            self.product_screen.set_instruction_focus(1)
            return
        if self.current_product is not None and self.credit < self.current_product["price"]:
            self.product_screen.set_instruction_focus(2)
            return
        if self.current_product is not None and self.credit >= self.current_product["price"]:
            self.product_screen.set_instruction_focus(3)
            return
        self.product_screen.set_instruction_focus(None)

    def _show_credit_insufficient(self):
        self.audio.play("credit_insufficient")

    def _show_insert_credit_and_return_idle(self):
        if self._service_lock_active:
            return
        if not self.current_product:
            return
        self._selection_countdown_remaining = 30
        self.product_screen.set_countdown(self._selection_countdown_remaining)
        self._selection_countdown_timer.start()
        self._selection_reset_timer.start(30000)
        self.audio.play("credit_insufficient")

    def _sync_selection_countdown(self):
        if self._service_lock_active:
            return
        if not self.current_product:
            return
        if self.credit >= self.current_product["price"]:
            self._selection_reset_timer.stop()
            self._selection_countdown_timer.stop()
            self._selection_countdown_remaining = 0
            self.product_screen.set_countdown(None)
            self._update_credit_displays()
            if self.stack.currentWidget() == self.product_screen:
                QTimer.singleShot(1000, self._notify_ready_for_ok)

    def _notify_ready_for_ok(self):
        if self._service_lock_active:
            return
        if self.stack.currentWidget() != self.product_screen:
            return
        if not self.current_product:
            return
        if self.credit < self.current_product["price"]:
            return
        self.audio.queue(["select_product", "press_ok"])
        self.product_screen.show_alert("Crédito completo. Presione OK", ms=2000)

    def _tick_selection_countdown(self):
        if self._service_lock_active:
            self._selection_countdown_timer.stop()
            return
        if self._selection_countdown_remaining <= 1:
            self._selection_countdown_timer.stop()
            self.product_screen.set_countdown(0)
            return
        self._selection_countdown_remaining -= 1
        self.product_screen.set_countdown(self._selection_countdown_remaining)

    def _clear_selection_to_idle(self):
        if self._service_lock_active:
            return
        self._selection_reset_timer.stop()
        self._selection_countdown_timer.stop()
        self._selection_countdown_remaining = 0
        if self.stack.currentWidget() != self.product_screen:
            return
        self.current_product = None
        self.product_screen.set_selected(None)
        self.product_screen.set_countdown(None)
        self.product_screen.set_section_message(None)
        self._update_credit_displays()
        self._refresh_product_enablement()

    def _select_by_gpio(self, product_id: str):
        if self._service_lock_active:
            return
        if self._in_config_flow():
            self._handle_config_product_button(product_id)
            return
        if self.stack.currentWidget() != self.product_screen:
            return
        if not self._accept_input(f"product:{product_id}", 0.2):
            return
        self._touch_interaction()
        self._set_selected_product(product_id)

    def _set_selected_product(self, product_id: str):
        if self._service_lock_active:
            return
        if self.stack.currentWidget() != self.product_screen:
            return
        product = self.products[product_id]
        if self.credit < product["price"]:
            self.current_product = product
            self.product_screen.set_selected(product_id)
            self._refresh_product_enablement()
            self._show_insert_credit_and_return_idle()
            return

        self._selection_reset_timer.stop()
        self._selection_countdown_timer.stop()
        self.product_screen.set_countdown(None)
        self.current_product = product
        self.product_screen.set_selected(product_id)
        self._refresh_product_enablement()
        self.audio.queue(["select_product", "press_ok"])
        self._show_preparation_prompt()

    def _handle_ok_input(self):
        if self._service_lock_active:
            return
        if self._in_config_flow():
            self._handle_config_ok()
            return
        if not self._accept_input("ok", 0.25):
            return
        if self.stack.currentWidget() == self.product_screen:
            self._on_ok_home()
        elif self.stack.currentWidget() == self.prompt_screen:
            self._touch_interaction()
            self._on_prompt_ok()

    def _handle_emergency_input(self):
        if self._service_lock_active:
            return
        if self._config_entry_hold_pressed():
            return
        if self._in_config_flow():
            self._handle_config_cancel()
            return
        if not self._accept_input("emergency", 0.25):
            return
        if self.stack.currentWidget() == self.message_screen:
            return
        if (
            self.stack.currentWidget() == self.product_screen
            and self.flow_step is None
            and self.current_product is None
        ):
            return
        if self.flow_step == "filling":
            self._on_emergency_stop()
            return
        if self.flow_step == "rinsing":
            return
        self._cancel_to_idle()

    def _handle_config_cancel(self):
        if self._config_mode in {"login", "menu"}:
            self._exit_config_to_home()
            return
        if self._config_mode in {"price", "name", "system_name", "contact_email", "contact_phone", "volume", "time", "code_new"}:
            self._open_config_menu()
            return
        if self._config_mode == "code_confirm":
            self._config_mode = "code_new"
            self.config_code_screen.configure("Nuevo código", "Ingrese nuevo código", self._config_new_code or "0000")

    def _handle_emergency_hold(self):
        if self._service_lock_active:
            return
        if self.stack.currentWidget() != self.product_screen or self.flow_step is not None:
            return
        self._restart_interface()

    def _restart_interface(self):
        logger.info("Restarting interface from idle emergency hold")
        self._selection_reset_timer.stop()
        self._selection_countdown_timer.stop()
        self.credit = 0.0
        self.current_product = None
        self.flow_step = None
        self.current_fill_percent = 0
        self.product_screen.clear_alert()
        self.product_screen.set_selected(None)
        self.product_screen.set_countdown(None)
        self.product_screen.set_section_message(None)
        self._update_credit_displays()
        self.stack.setCurrentWidget(self.product_screen)
        self._refresh_product_enablement(initial=True)

    def _cancel_to_idle(self):
        if self._service_lock_active:
            return
        self._charge_rinse_fee_if_needed()
        self._prompt_timeout_timer.stop()
        self._prompt_countdown_timer.stop()
        self._prompt_countdown_remaining = 0
        self.prompt_screen.set_prompt_countdown(None)
        self._selection_reset_timer.stop()
        self._selection_countdown_timer.stop()
        self._selection_countdown_remaining = 0
        self.flow_step = None
        self.current_product = None
        self.current_fill_percent = 0
        self._rinse_charge_pending = False
        self.product_screen.clear_alert()
        self.product_screen.set_selected(None)
        self.product_screen.set_countdown(None)
        self.product_screen.set_section_message(None)
        self._update_credit_displays()
        self.stack.setCurrentWidget(self.product_screen)
        self._refresh_product_enablement()

    def _on_ok_home(self):
        if self._service_lock_active:
            return
        self._touch_interaction()
        if not self.current_product:
            if any(self.credit >= p["price"] for p in settings.PRODUCTS):
                self.product_screen.blink_enabled_products()
                self.product_screen.show_alert("Seleccione un producto", ms=2500)
                self.audio.play("select_product")
            else:
                self.audio.play("credit_insufficient")
            return

        if self.credit < self.current_product["price"]:
            self._show_credit_insufficient()
            return

        self._show_preparation_prompt()

    def _show_preparation_prompt(self):
        if not self.current_product:
            return
        self._start_prompt_countdown()
        self._prompt_timeout_timer.start(60000)
        self.button_leds.set_prompt_ready()
        if self.current_product["id"] == "full_garrafon":
            self.flow_step = "await_rinse_position"
            self.prompt_screen.configure(
                "Coloque su embase en la cabina",
                settings.UPSIDE_DOWN_IMAGE,
                "Coloque el garrafon boca abajo",
                image_size=(300, 260),
                image_offset_y=0,
            )
        else:
            self.flow_step = "await_fill_position"
            self.prompt_screen.configure(
                "Coloque su embase en la cabina",
                self.current_product["image"],
                "Prepare el envase para llenado",
                image_size=(310, 280),
                image_offset_y=0,
            )
        self.stack.setCurrentWidget(self.prompt_screen)

    def _show_upright_prompt(self):
        self._start_prompt_countdown()
        self._prompt_timeout_timer.start(60000)
        self.button_leds.set_prompt_ready()
        self.flow_step = "await_fill_position"
        self._rinse_charge_pending = True
        subtitle = "Presione OK Cuando Termine"
        if self.current_product["id"] == "full_garrafon":
            subtitle = "Gire el garrafon boca arriba"
        self.prompt_screen.configure(
            "Coloque su embase en la cabina",
            self.current_product["image"],
            subtitle,
            image_size=(310, 280),
            image_offset_y=0,
        )
        self.stack.setCurrentWidget(self.prompt_screen)
        self.audio.play("press_ok")

    def _on_prompt_ok(self):
        if self._service_lock_active:
            return
        self._prompt_timeout_timer.stop()
        self._prompt_countdown_timer.stop()
        self._prompt_countdown_remaining = 0
        self.prompt_screen.set_prompt_countdown(None)
        if self.flow_step == "await_rinse_position":
            self.flow_step = "rinsing"
            self.button_leds.set_processing()
            try:
                self.valves.rinse_start()
            except GPIOControllerError as exc:
                logger.error(str(exc))
                self.audio.play("error")
                self._reset_to_home()
                return
            self.stack.setCurrentWidget(self.progress_screen)
            self.progress_screen.start(
                "Enjuagando",
                settings.RINSE_SECONDS,
                image_path=settings.UPSIDE_DOWN_IMAGE,
                image_size=(350, 300),
                emergency_enabled=False,
                image_offset_y=20,
            )
            self.audio.play("nozzle_cleaning")
        elif self.flow_step == "await_fill_position":
            self._start_filling()

    def _start_filling(self):
        if self._service_lock_active:
            return
        self._prompt_timeout_timer.stop()
        self._prompt_countdown_timer.stop()
        self._prompt_countdown_remaining = 0
        self.prompt_screen.set_prompt_countdown(None)
        self.flow_step = "filling"
        self._rinse_charge_pending = False
        self.current_fill_percent = 0
        self._played_75_audio = False
        self.button_leds.set_processing()
        self.stack.setCurrentWidget(self.progress_screen)
        total_s = self.current_product["volume_l"] * settings.FILL_SECONDS_PER_LITER
        try:
            self.valves.start_dispense()
            self.progress_screen.start(
                "Llenando",
                total_s,
                image_path=self.current_product["image"],
                image_size=(260, 260),
                emergency_enabled=True,
                image_offset_y=0,
            )
            self.audio.queue(["starting_fill", "filling"])
        except GPIOControllerError as exc:
            logger.error(str(exc))
            self.audio.play("error")
            self._reset_to_home()

    def _on_progress_changed(self, progress: int):
        if self._service_lock_active:
            return
        self.current_fill_percent = progress
        if self.flow_step == "filling":
            self.valves.update_progress(progress)
            if progress >= 75 and not self._played_75_audio:
                self._played_75_audio = True
                self.audio.play("seventy_five")

    def _on_emergency_stop(self):
        if self._service_lock_active:
            return
        if self.flow_step != "filling":
            return
        self.progress_screen.stop_now()
        try:
            self.valves.finish_dispense()
        except GPIOControllerError as exc:
            logger.error(str(exc))
            self.audio.play("error")
        self._complete_sale(emergency=True)

    def _on_progress_completed(self):
        if self._service_lock_active:
            return
        if self.flow_step == "rinsing":
            try:
                self.valves.rinse_stop()
            except GPIOControllerError as exc:
                logger.error(str(exc))
                self.audio.play("error")
                self._reset_to_home()
                return
            self._show_upright_prompt()
            return

        if self.flow_step == "filling":
            try:
                self.valves.finish_dispense()
            except GPIOControllerError as exc:
                logger.error(str(exc))
                self.audio.play("error")
            self.audio.queue(["fill_complete", "remove_container"])
            self._complete_sale(emergency=False)

    def _complete_sale(self, emergency: bool = False):
        if self._service_lock_active:
            return
        if emergency:
            served_liters = round((self.current_fill_percent / 100.0) * self.current_product["volume_l"], 2)
            raw_charge = served_liters * settings.EMERGENCY_RATE_PER_LITER
            price_to_charge = float(math.ceil(raw_charge)) if raw_charge > 0 else 0.0
            price_to_charge = min(price_to_charge, self.credit)
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
        if self._service_lock_active:
            return
        if change > 0:
            self.message_screen.set_message(
                f"Recoja su cambio\nTotal a reembolsar: ${change:.2f}",
                image_path=settings.COIN_IMAGE,
                image_size=(200, 200),
            )
            self.stack.setCurrentWidget(self.message_screen)
            self.credit = 0.0
            self._update_credit_displays()
            QTimer.singleShot(3000, self._show_thanks)
        else:
            self.credit = 0.0
            self._update_credit_displays()
            self._show_thanks()

    def _show_thanks(self):
        if self._service_lock_active:
            return
        self.message_screen.set_message(
            "",
            gif_path=settings.THANKS_GIF,
            hide_header=True,
        )
        self.stack.setCurrentWidget(self.message_screen)
        self.audio.play("thanks")
        QTimer.singleShot(3000, self._reset_to_home)

    def _reset_to_home(self):
        if self._service_lock_active:
            self.stack.setCurrentWidget(self.message_screen)
            return
        self._prompt_timeout_timer.stop()
        self._prompt_countdown_timer.stop()
        self._prompt_countdown_remaining = 0
        self.prompt_screen.set_prompt_countdown(None)
        self.current_product = None
        self.flow_step = None
        self.current_fill_percent = 0
        self._rinse_charge_pending = False
        self.product_screen.set_selected(None)
        self._refresh_product_enablement()
        self.stack.setCurrentWidget(self.product_screen)
        self.button_leds.set_completion_flash()

    def _handle_prompt_timeout(self):
        if self._service_lock_active:
            return
        if self.stack.currentWidget() != self.prompt_screen:
            return
        self._cancel_to_idle()

    def _charge_rinse_fee_if_needed(self):
        if self._service_lock_active:
            return
        if not self._rinse_charge_pending:
            return
        fee = min(3.0, self.credit)
        if fee > 0:
            self.credit = round(self.credit - fee, 2)
            self._update_credit_displays()
            self.product_screen.show_alert(f"Se cobraron ${fee:.0f} por enjuague", ms=3000)
        self._rinse_charge_pending = False

    def _start_prompt_countdown(self):
        if self._service_lock_active:
            return
        self._prompt_countdown_remaining = 60
        self.prompt_screen.set_prompt_countdown(self._prompt_countdown_remaining)
        self._prompt_countdown_timer.start()

    def _tick_prompt_countdown(self):
        if self._service_lock_active:
            self._prompt_countdown_timer.stop()
            return
        if self._prompt_countdown_remaining <= 1:
            self._prompt_countdown_remaining = 0
            self.prompt_screen.set_prompt_countdown(0)
            self._prompt_countdown_timer.stop()
            return
        self._prompt_countdown_remaining -= 1
        self.prompt_screen.set_prompt_countdown(self._prompt_countdown_remaining)

    def closeEvent(self, event):
        self._service_level_timer.stop()
        self.coin_acceptor.shutdown()
        self.button_leds.shutdown()
        super().closeEvent(event)
