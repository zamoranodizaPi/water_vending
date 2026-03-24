"""Modern touch-friendly product selection screen for a 1024x600 kiosk."""
from __future__ import annotations

from PyQt5.QtCore import QTimer, QRect, Qt, pyqtSignal
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

from theme import APP_FONT, ORANGE, PRIMARY, PRIMARY_HOVER, SECONDARY, SURFACE, TEXT_PRIMARY, color_with_alpha, refresh_style

HEADER_HEIGHT = 90
CARD_HEIGHT = 280
CARD_MIN_WIDTH = 300
INSTRUCTIONS_HEIGHT = 120
CARD_SELECTED_SCALE = 1.1
CARD_REDUCED_SCALE = 0.9

TITLE_TEXT = "Agua Purificada Lupita"


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

        self.accent_bar = QFrame()
        self.accent_bar.setObjectName("cardAccentBar")
        self.accent_bar.setFixedHeight(4)
        root.addWidget(self.accent_bar)

        body = QVBoxLayout()
        body.setContentsMargins(10, 8, 10, 12)
        body.setSpacing(4)
        root.addLayout(body, 1)

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setFixedHeight(178)
        pixmap = QPixmap(str(self.product["image"]))
        if pixmap.isNull():
            self.icon.setText("Agua")
            self.icon.setStyleSheet(
                f"font-family:{APP_FONT}; font-size:22px; font-weight:700; color:{PRIMARY};"
            )
        else:
            scaled = pixmap.scaled(220, 178, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon.setPixmap(scaled)
        body.addWidget(self.icon, 1, Qt.AlignCenter)

        self.price = QLabel(f"${self.product['price']:.0f}")
        self.price.setAlignment(Qt.AlignCenter)
        self.price.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:28px; font-weight:800; color:{PRIMARY};"
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
        body.addSpacing(4)
        body.addWidget(self.buy_button)

    def _handle_buy_clicked(self):
        print(f"Producto seleccionado: {self.product['name']}")
        self.clicked.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.isEnabled():
            self.clicked.emit()
        super().mousePressEvent(event)

    def setChecked(self, checked: bool):
        self._selected = checked
        self._apply_state()

    def isChecked(self) -> bool:
        return self._selected

    def setEnabled(self, enabled: bool):
        super().setEnabled(True)
        self.set_affordable(enabled)

    def set_affordable(self, affordable: bool):
        self._affordable = True
        self.buy_button.setEnabled(True)
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

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        bubble = QLabel(str(number))
        bubble.setAlignment(Qt.AlignCenter)
        bubble.setFixedSize(36, 36)
        bubble.setStyleSheet(
            f"""
            background-color:{SURFACE};
            color:{PRIMARY};
            border:2px solid {PRIMARY};
            border-radius:18px;
            font-family:{APP_FONT};
            font-size:18px;
            font-weight:700;
            """
        )
        label = QLabel(text)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        label.setWordWrap(True)
        label.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:13px; font-weight:600; color:{SECONDARY};"
        )

        layout.addWidget(bubble, 0, Qt.AlignVCenter)
        layout.addWidget(label, 1)


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
        self._rinse_locked = False
        self._ok_base_text = "Continuar"
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
        icon_box.setFixedSize(94, 94)
        logo = QPixmap(str(self.logo_path))
        if logo.isNull():
            icon_box.setText("L")
        else:
            icon_box.setPixmap(logo.scaled(94, 94, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon_box, 0, Qt.AlignTop)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(0)
        title_col.addStretch(1)
        title = QLabel(TITLE_TEXT)
        title.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:25px; font-weight:800; color:{SURFACE};"
        )
        title_col.addWidget(title)
        title_col.addStretch(1)
        header_layout.addLayout(title_col, 1)

        self.credit_box = ClickableFrame()
        self.credit_box.setObjectName("creditPill")
        self.credit_box.setFixedSize(160, 56)
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
        self.credit_label = QLabel("Crédito\n$0")
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

        self.ok_btn = QPushButton(self._ok_base_text)
        self.ok_btn.setObjectName("confirmButton")
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.setMinimumHeight(48)
        self.ok_btn.setMinimumWidth(180)
        self.ok_btn.clicked.connect(self.ok_pressed.emit)
        top_row.addWidget(self.ok_btn, 0, Qt.AlignRight)
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
            "Coloque garrafón",
            "Presione OK",
        ]
        for index, text in enumerate(steps, start=1):
            steps_row.addWidget(InstructionStep(index, text), 1)
        instructions_layout.addLayout(steps_row)

        root.addWidget(self.instructions_frame)

    def mousePressEvent(self, event):
        if not self.ok_btn.isEnabled():
            top_left = self.ok_btn.mapTo(self, self.ok_btn.rect().topLeft())
            rect = QRect(top_left, self.ok_btn.size())
            if rect.contains(event.pos()):
                self.disabled_control_touched.emit("ok")
        super().mousePressEvent(event)

    def set_credit(self, credit: float):
        self.credit_label.setProperty("warning", False)
        refresh_style(self.credit_label)
        self.credit_label.setText(f"Crédito\n${credit:.0f}")

    def show_credit_warning(self, text: str):
        self.credit_label.setProperty("warning", True)
        refresh_style(self.credit_label)
        self.credit_label.setText(text.replace(": ", "\n"))

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
            card.setChecked(selected)
            if not has_selection:
                card.set_visual_scale(1.0)
            elif selected:
                card.set_visual_scale(CARD_SELECTED_SCALE)
            else:
                card.set_visual_scale(CARD_REDUCED_SCALE)

    def set_product_enabled(self, product_id: str, enabled: bool):
        self.cards[product_id].setEnabled(enabled)

    def set_ok_enabled(self, enabled: bool):
        self.ok_btn.setEnabled(enabled)

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
            self.ok_btn.setText(self._ok_base_text)
            return
        self.ok_btn.setText(f"{self._ok_base_text} ({seconds}s)")

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
