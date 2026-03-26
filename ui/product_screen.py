"""Modern touch-friendly product selection screen for a 1024x600 kiosk."""
from __future__ import annotations

from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config import settings
from theme import APP_FONT, ORANGE, PRIMARY, PRIMARY_HOVER, SECONDARY, SURFACE, TEXT_PRIMARY, color_with_alpha, refresh_style

HEADER_HEIGHT = 90
CARD_HEIGHT = 280
CARD_MIN_WIDTH = 300
INSTRUCTIONS_HEIGHT = 120
CARD_SELECTED_SCALE = 1.1
CARD_REDUCED_SCALE = 0.9

class TopLeftHotspot(QWidget):
    pressed = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed.emit()
        super().mousePressEvent(event)


class ClickableFrame(QFrame):
    pressed = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed.emit()
        super().mousePressEvent(event)


class ProductCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, product: dict):
        super().__init__()
        self.product = product
        self._affordable = True
        self._selected = False
        self._has_active_selection = False
        self._interactive = True
        self._base_min_width = CARD_MIN_WIDTH
        self._base_height = CARD_HEIGHT
        self._build_ui()
        self._apply_state()

    def _build_ui(self):
        self.setObjectName("productCard")
        self.setMinimumWidth(CARD_MIN_WIDTH)
        self.setFixedHeight(CARD_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(color_with_alpha("#0f172a", 35))
        self.setGraphicsEffect(shadow)
        self._shadow = shadow

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        body = QVBoxLayout()
        body.setContentsMargins(10, 8, 10, 12)
        body.setSpacing(4)
        root.addLayout(body, 1)

        self.price_corner = QLabel(f"${self.product['price']:.0f}")
        self.price_corner.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.price_corner.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:{SURFACE};"
        )
        self.price_corner.setVisible(False)
        body.addWidget(self.price_corner, 0, Qt.AlignRight | Qt.AlignTop)

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setFixedHeight(178)
        pixmap = QPixmap(str(self.product["image"]))
        if pixmap.isNull():
            self.icon.setText("Agua")
            self.icon.setStyleSheet(
                f"font-family:{APP_FONT}; font-size:22px; font-weight:700; color:{SURFACE};"
            )
        else:
            scaled = pixmap.scaled(220, 178, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon.setPixmap(scaled)
        body.addWidget(self.icon, 1, Qt.AlignCenter)

        self.price = QLabel(f"${self.product['price']:.0f}")
        self.price.setAlignment(Qt.AlignCenter)
        self.price.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:28px; font-weight:800; color:{SURFACE};"
        )
        body.addWidget(self.price)

        self.buy_button = QPushButton(self.product["name"])
        self.buy_button.setObjectName("buyButton")
        self.buy_button.setCursor(Qt.PointingHandCursor)
        self.buy_button.setMinimumHeight(46)
        self.buy_button.setStyleSheet(
            f"""
            QPushButton#buyButton {{
                font-family:{APP_FONT};
                font-size:19px;
                font-weight:700;
                color:{SURFACE};
                border:none;
                border-radius:10px;
                background:qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PRIMARY},
                    stop:1 #f43f5e
                );
                padding:0 18px;
            }}
            QPushButton#buyButton:hover {{
                background:qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PRIMARY_HOVER},
                    stop:1 {ORANGE}
                );
            }}
            QPushButton#buyButton:pressed {{
                padding-top:2px;
                padding-bottom:0px;
                background:qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #db2777,
                    stop:1 #e11d48
                );
            }}
            QPushButton#buyButton:disabled {{
                background:#cbd5e1;
                color:#94a3b8;
            }}
            """
        )
        self.buy_button.clicked.connect(self._handle_buy_clicked)
        button_shadow = QGraphicsDropShadowEffect(self.buy_button)
        button_shadow.setBlurRadius(16)
        button_shadow.setOffset(0, 4)
        button_shadow.setColor(color_with_alpha("#0f172a", 55))
        self.buy_button.setGraphicsEffect(button_shadow)
        body.addSpacing(4)
        body.addWidget(self.buy_button)

    def _handle_buy_clicked(self):
        print(f"Producto seleccionado: {self.product['name']}")
        self.clicked.emit()

    def refresh_product_data(self):
        price_text = f"${self.product['price']:.0f}"
        self.price.setText(price_text)
        self.price_corner.setText(price_text)
        self.buy_button.setText(self.product["name"])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._interactive:
            self.clicked.emit()
        super().mousePressEvent(event)

    def setChecked(self, checked: bool):
        self._selected = checked
        self._has_active_selection = checked
        self._apply_state()

    def isChecked(self) -> bool:
        return self._selected

    def set_selection_state(self, selected: bool, has_active_selection: bool):
        self._selected = selected
        self._has_active_selection = has_active_selection
        self._apply_state()

    def setEnabled(self, enabled: bool):
        self._interactive = enabled
        super().setEnabled(True)
        self.buy_button.setEnabled(enabled)
        self._apply_state()

    def set_affordable(self, affordable: bool):
        self._affordable = True
        self._apply_state()

    def is_affordable(self) -> bool:
        return True

    def set_visual_scale(self, scale: float):
        width = int(self._base_min_width * scale)
        height = int(self._base_height * scale)
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.setFixedHeight(height)
        if scale >= 1.05:
            self.setProperty("selectedScale", True)
        else:
            self.setProperty("selectedScale", False)
        refresh_style(self)

    def pulse_attention(self, flashes: int = 3):
        state = {"step": 0}

        def _tick():
            if state["step"] >= flashes * 2:
                self.setProperty("attention", False)
                refresh_style(self)
                self._apply_state()
                return
            self.setProperty("attention", state["step"] % 2 == 0)
            refresh_style(self)
            state["step"] += 1
            QTimer.singleShot(160, _tick)

        _tick()

    def _apply_state(self):
        self.setProperty("selected", self._selected)
        self.setProperty("affordable", self._affordable)
        show_corner_price = self._has_active_selection and not self._selected and self._interactive
        self.price.setVisible(not show_corner_price)
        self.price_corner.setVisible(show_corner_price)
        self.setWindowOpacity(1.0 if self._interactive else 0.72)
        refresh_style(self)
        if self._selected:
            self._shadow.setBlurRadius(22)
            self._shadow.setColor(color_with_alpha(PRIMARY, 70))
        elif self._affordable:
            self._shadow.setBlurRadius(20)
            self._shadow.setColor(color_with_alpha("#0f172a", 35))
        else:
            self._shadow.setBlurRadius(12)
            self._shadow.setColor(color_with_alpha("#64748b", 24))


class InstructionStep(QFrame):
    def __init__(self, number: int, text: str):
        super().__init__()
        self.setObjectName("instructionStep")
        self._scale = 1.0
        self._base_bubble_size = 36
        self._base_bubble_radius = 18
        self._base_bubble_font = 18
        self._base_label_font = 13
        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(240)
        self._pulse_timer.timeout.connect(self._toggle_pulse)
        self._pulse_grow = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.bubble = QLabel(str(number))
        self.bubble.setAlignment(Qt.AlignCenter)
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.label.setWordWrap(True)

        layout.addWidget(self.bubble, 0, Qt.AlignVCenter)
        layout.addWidget(self.label, 1)
        self._apply_scale()

    def _apply_scale(self):
        bubble_size = int(self._base_bubble_size * self._scale)
        radius = int(self._base_bubble_radius * self._scale)
        bubble_font = int(self._base_bubble_font * self._scale)
        label_font = int(self._base_label_font * self._scale)
        self.bubble.setFixedSize(bubble_size, bubble_size)
        self.bubble.setStyleSheet(
            f"""
            background-color:{SURFACE};
            color:{PRIMARY};
            border:2px solid {PRIMARY};
            border-radius:{radius}px;
            font-family:{APP_FONT};
            font-size:{bubble_font}px;
            font-weight:700;
            """
        )
        self.label.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:{label_font}px; font-weight:600; color:{SECONDARY};"
        )

    def _toggle_pulse(self):
        self._pulse_grow = not self._pulse_grow
        self._scale = 1.1 if self._pulse_grow else 1.0
        self._apply_scale()

    def set_active(self, active: bool):
        if active:
            if not self._pulse_timer.isActive():
                self._pulse_grow = False
                self._pulse_timer.start()
                self._toggle_pulse()
            return
        self._pulse_timer.stop()
        self._scale = 1.0
        self._pulse_grow = False
        self._apply_scale()


class ProductScreen(QWidget):
    product_selected = pyqtSignal(str)
    ok_pressed = pyqtSignal()
    rinse_pressed = pyqtSignal()
    disabled_control_touched = pyqtSignal(str)
    top_left_corner_pressed = pyqtSignal()
    credit_box_pressed = pyqtSignal()

    def __init__(self, products, logo_path, coin_image_path):
        super().__init__()
        self.setObjectName("productScreen")
        self.products = products
        self.logo_path = logo_path
        self.coin_image_path = coin_image_path
        self.cards = {}
        self.steps = []
        self._rinse_locked = False
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        self.header_frame = QFrame()
        self.header_frame.setObjectName("modernHeader")
        self.header_frame.setFixedHeight(HEADER_HEIGHT)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(16, 10, 16, 10)
        header_layout.setSpacing(0)

        self.service_hotspot = TopLeftHotspot()
        self.service_hotspot.setFixedWidth(5)
        self.service_hotspot.pressed.connect(self.top_left_corner_pressed.emit)
        header_layout.addWidget(self.service_hotspot, 0)

        icon_box = QLabel()
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setFixedSize(72, 72)
        logo = QPixmap(str(self.logo_path))
        if logo.isNull():
            icon_box.setText("L")
        else:
            icon_box.setPixmap(logo.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon_box, 0, Qt.AlignVCenter)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(2)
        title_col.addStretch(1)
        title = QLabel(settings.BRAND_TITLE)
        title.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:25px; font-weight:800; color:{SURFACE};"
        )
        title_col.addWidget(title)
        subtitle = QLabel(settings.BRAND_TAGLINE)
        subtitle.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:12px; font-weight:600; color:{SURFACE};"
        )
        title_col.addWidget(subtitle)
        title_col.addStretch(1)
        header_layout.addLayout(title_col, 1)

        self.credit_box = ClickableFrame()
        self.credit_box.setObjectName("creditPill")
        self.credit_box.setFixedSize(190, 56)
        self.credit_box.pressed.connect(self.credit_box_pressed.emit)
        credit_layout = QHBoxLayout(self.credit_box)
        credit_layout.setContentsMargins(12, 8, 12, 8)
        credit_layout.setSpacing(8)

        coin = QLabel()
        coin.setAlignment(Qt.AlignCenter)
        coin.setFixedSize(30, 30)
        coin_pix = QPixmap(str(self.coin_image_path))
        if coin_pix.isNull():
            coin.setText("$")
            coin.setStyleSheet(
                f"font-family:{APP_FONT}; font-size:16px; font-weight:800; color:{TEXT_PRIMARY};"
            )
        else:
            coin.setPixmap(coin_pix.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.credit_label = QLabel("Crédito $0")
        self.credit_label.setObjectName("creditText")
        self.credit_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        credit_layout.addWidget(coin)
        credit_layout.addWidget(self.credit_label, 1)
        header_layout.addWidget(self.credit_box, 0, Qt.AlignVCenter)

        root.addWidget(self.header_frame)

        products_section = QFrame()
        products_section.setObjectName("productsSection")
        section_layout = QVBoxLayout(products_section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(4, 0, 4, 0)
        top_row.setSpacing(12)

        self.section_label = QLabel("Seleccione un producto")
        self.section_label.setObjectName("sectionLabel")
        self.section_label.setProperty("warning", False)
        top_row.addWidget(self.section_label, 1)

        self.countdown_label = QLabel("")
        self.countdown_label.setObjectName("selectionCountdown")
        self.countdown_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.countdown_label.setVisible(False)
        self.countdown_label.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:18px; font-weight:800; color:{PRIMARY};"
        )
        top_row.addWidget(self.countdown_label, 0, Qt.AlignRight)
        section_layout.addLayout(top_row)

        self.alert_label = QLabel("")
        self.alert_label.setObjectName("alertLabel")
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setVisible(False)
        section_layout.addWidget(self.alert_label)

        self.product_area = QWidget()
        self.product_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.product_row = QHBoxLayout(self.product_area)
        self.product_row.setContentsMargins(0, 0, 0, 0)
        self.product_row.setSpacing(18)

        for product in self.products:
            card = ProductCard(product)
            card.clicked.connect(lambda pid=product["id"]: self.product_selected.emit(pid))
            self.cards[product["id"]] = card
            self.product_row.addWidget(card, 1)
        section_layout.addWidget(self.product_area, 1)
        root.addWidget(products_section, 1)

        self.instructions_frame = QFrame()
        self.instructions_frame.setObjectName("instructionsPanel")
        self.instructions_frame.setFixedHeight(INSTRUCTIONS_HEIGHT)
        instructions_layout = QVBoxLayout(self.instructions_frame)
        instructions_layout.setContentsMargins(16, 12, 16, 12)
        instructions_layout.setSpacing(10)

        instructions_title = QLabel("Instrucciones de uso")
        instructions_title.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:20px; font-weight:800; color:{TEXT_PRIMARY};"
        )
        instructions_layout.addWidget(instructions_title)

        steps_row = QHBoxLayout()
        steps_row.setContentsMargins(0, 0, 0, 0)
        steps_row.setSpacing(10)
        steps = [
            "Seleccione producto",
            "Ingrese crédito",
            "Presione OK",
        ]
        for index, text in enumerate(steps, start=1):
            step_widget = InstructionStep(index, text)
            self.steps.append(step_widget)
            steps_row.addWidget(step_widget, 1)
        instructions_layout.addLayout(steps_row)

        root.addWidget(self.instructions_frame)

    def set_credit(self, credit: float):
        self.credit_label.setProperty("warning", False)
        refresh_style(self.credit_label)
        self.credit_label.setText(f"Crédito ${credit:.0f}")

    def show_credit_warning(self, text: str):
        self.credit_label.setProperty("warning", True)
        refresh_style(self.credit_label)
        self.credit_label.setText(text.replace(": ", " "))

    def show_alert(self, text: str, ms: int = 3000):
        self.alert_label.setText(text)
        self.alert_label.setVisible(True)
        QTimer.singleShot(ms, self.clear_alert)

    def clear_alert(self):
        self.alert_label.clear()
        self.alert_label.setVisible(False)

    def set_selected(self, product_id: str | None):
        has_selection = bool(product_id)
        for pid, card in self.cards.items():
            selected = pid == product_id
            card.set_selection_state(selected, has_selection)
            if not has_selection:
                card.setEnabled(True)
                card.set_visual_scale(1.0)
            elif selected:
                card.setEnabled(True)
                card.set_visual_scale(CARD_SELECTED_SCALE)
            else:
                card.setEnabled(False)
                card.set_visual_scale(1.0)

    def set_product_enabled(self, product_id: str, enabled: bool):
        self.cards[product_id].set_affordable(enabled)

    def set_ok_enabled(self, enabled: bool):
        return

    def set_rinse_enabled(self, enabled: bool):
        return

    def set_rinse_checked(self, checked: bool):
        return

    def lock_rinse_selection(self, locked: bool):
        self._rinse_locked = locked

    def is_rinse_checked(self) -> bool:
        return False

    def set_section_message(self, text: str | None, warning: bool = False):
        self.section_label.setText(text or "Seleccione un producto")
        self.section_label.setProperty("warning", warning)
        refresh_style(self.section_label)

    def set_countdown(self, seconds: int | None):
        if seconds is None:
            self.countdown_label.clear()
            self.countdown_label.setVisible(False)
            return
        self.countdown_label.setText(f"Regreso en {seconds}s")
        self.countdown_label.setVisible(True)

    def set_instruction_focus(self, step_number: int | None):
        for index, step in enumerate(self.steps, start=1):
            step.set_active(index == step_number)

    def refresh_products(self):
        for card in self.cards.values():
            card.refresh_product_data()

    def pulse_credit_attention(self):
        state = {"step": 0}

        def _tick():
            if state["step"] >= 6:
                self.credit_box.setProperty("flash", False)
                refresh_style(self.credit_box)
                return
            self.credit_box.setProperty("flash", state["step"] % 2 == 0)
            refresh_style(self.credit_box)
            state["step"] += 1
            QTimer.singleShot(140, _tick)

        _tick()

    def blink_enabled_products(self):
        for card in self.cards.values():
            if card.is_affordable():
                card.pulse_attention(3)

    def play_idle_attention_animation(self):
        self.blink_enabled_products()
