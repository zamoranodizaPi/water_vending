"""Product selection screen for a 1024x600 vending layout."""
from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QTimer, QRect, Qt, pyqtSignal
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

from theme import APP_FONT, PRIMARY, PRIMARY_HOVER, SURFACE, TEXT_SECONDARY, color_with_alpha, refresh_style

CARD_MIN_WIDTH = 285
CARD_MIN_HEIGHT = 250
BADGE_WIDTH = 300
BADGE_HEIGHT = 60
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
HEADER_WIDTH = 1004
HEADER_HEIGHT = 100


class ProductCard(QPushButton):
    def __init__(self, product: dict):
        super().__init__()
        self.product = product
        self._hovered = False
        self._affordable = True
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(CARD_MIN_WIDTH, CARD_MIN_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setObjectName("productCard")
        self.setStyleSheet("QPushButton{background:transparent; border:none;}")

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(color_with_alpha(TEXT_SECONDARY, 70))
        self.setGraphicsEffect(self.shadow)

        self.shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius", self)
        self.shadow_anim.setDuration(150)
        self.shadow_anim.setEasingCurve(QEasingCurve.OutCubic)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.card_frame = QFrame()
        self.card_frame.setObjectName("card")
        self.card_frame.setMinimumSize(CARD_MIN_WIDTH, CARD_MIN_HEIGHT)
        self.card_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.card_frame.setProperty("selected", False)
        self.card_frame.setProperty("hovered", False)
        self.card_frame.setProperty("affordable", True)
        self.card_frame.setProperty("attention", False)
        root.addWidget(self.card_frame)

        card_root = QVBoxLayout(self.card_frame)
        card_root.setContentsMargins(0, 0, 0, 0)
        card_root.setSpacing(0)

        self.accent_bar = QFrame()
        self.accent_bar.setObjectName("accentBar")
        self.accent_bar.setProperty("accent", self._accent_name())
        card_root.addWidget(self.accent_bar)

        body = QVBoxLayout()
        body.setContentsMargins(18, 16, 18, 16)
        body.setSpacing(0)
        card_root.addLayout(body, 1)

        self.image = QLabel()
        self.image.setFixedSize(200, 200)
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setStyleSheet("background:transparent;")
        pix = QPixmap(str(product["image"])).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.image.setText(product["name"])
            self.image.setProperty("role", "secondary")
            self.image.setStyleSheet(f"font-family:{APP_FONT}; font-size:16px;")
            refresh_style(self.image)
        else:
            self.image.setPixmap(pix)

        self.name = QLabel(product["name"])
        self.name.setProperty("role", "name")
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setWordWrap(True)
        self.name.setStyleSheet(f"font-family:{APP_FONT}; font-size:17px; font-weight:600;")

        self.volume = QLabel(f"{product['volume_l']} L")
        self.volume.setProperty("role", "secondary")
        self.volume.setAlignment(Qt.AlignCenter)
        self.volume.setStyleSheet(f"font-family:{APP_FONT}; font-size:15px; font-weight:500;")

        self.price = QLabel(f"${product['price']:.0f}")
        self.price.setProperty("role", "price")
        self.price.setAlignment(Qt.AlignCenter)
        self.price.setStyleSheet(f"font-family:{APP_FONT}; font-size:27px; font-weight:700;")

        body.addWidget(self.image, 0, Qt.AlignHCenter)
        body.addStretch(1)
        body.addWidget(self.name)
        body.addWidget(self.volume)
        body.addWidget(self.price)

        self._apply_state(animated=False)

    def _accent_name(self) -> str:
        return {
            "full_garrafon": "blue",
            "half_garrafon": "orange",
            "gallon": "pink",
        }.get(self.product["id"], "blue")

    def enterEvent(self, event):
        self._hovered = True
        self._apply_state()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_state()
        super().leaveEvent(event)

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._apply_state()

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self._apply_state(animated=False)

    def _apply_state(self, animated: bool = True):
        self.card_frame.setProperty("selected", self.isChecked())
        self.card_frame.setProperty("hovered", self._hovered)
        self.card_frame.setProperty("affordable", self._affordable)
        refresh_style(self.accent_bar)
        if self.isChecked():
            blur = 14
            shadow_color = color_with_alpha(PRIMARY, 70)
        elif self._hovered:
            blur = 12
            shadow_color = color_with_alpha(PRIMARY_HOVER, 60)
        elif not self._affordable:
            blur = 8
            shadow_color = color_with_alpha(TEXT_SECONDARY, 45)
        else:
            blur = 10
            shadow_color = color_with_alpha(TEXT_SECONDARY, 50)

        refresh_style(self.card_frame)
        self.shadow.setColor(shadow_color)
        if animated:
            self.shadow_anim.stop()
            self.shadow_anim.setStartValue(self.shadow.blurRadius())
            self.shadow_anim.setEndValue(blur)
            self.shadow_anim.start()
        else:
            self.shadow.setBlurRadius(blur)

    def pulse_attention(self, flashes: int = 3):
        state = {"step": 0}

        def _tick():
            if state["step"] >= flashes * 2:
                self.card_frame.setProperty("attention", False)
                refresh_style(self.card_frame)
                self._apply_state(animated=False)
                return
            self.card_frame.setProperty("attention", state["step"] % 2 == 0)
            refresh_style(self.card_frame)
            state["step"] += 1
            QTimer.singleShot(170, _tick)

        _tick()

    def set_affordable(self, affordable: bool):
        self._affordable = affordable
        self._apply_state(animated=False)

    def is_affordable(self) -> bool:
        return self._affordable


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
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 5, 10, 16)
        root.setSpacing(0)

        self.header_frame = QFrame()
        self.header_frame.setObjectName("header")
        self.header_frame.setFixedSize(HEADER_WIDTH, HEADER_HEIGHT)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        self.service_hotspot = TopLeftHotspot()
        self.service_hotspot.setFixedSize(50, 50)
        self.service_hotspot.pressed.connect(self.top_left_corner_pressed.emit)
        self.service_hotspot.setParent(self.header_frame)
        self.service_hotspot.move(0, 0)

        self.logo_box = QFrame()
        self.logo_box.setObjectName("logoBox")
        self.logo_box.setFixedSize(HEADER_WIDTH, HEADER_HEIGHT)
        self.logo = QLabel(self.logo_box)
        self.logo.setObjectName("logoLabel")
        self.logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(1004, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.logo.setGeometry(0, 0, HEADER_WIDTH, HEADER_HEIGHT)
            self.logo.setText("Lupita")
            self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:28px; font-weight:700; color:{SURFACE};")
        else:
            self.logo.setGeometry(0, 0, HEADER_WIDTH, HEADER_HEIGHT)
            self.logo.setPixmap(pix)

        header_layout.addWidget(self.logo_box, 0, Qt.AlignCenter)
        root.addWidget(self.header_frame)

        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(16, 0, 16, 0)
        content_layout.setSpacing(0)

        self.section_label = QLabel("")
        self.section_label.setObjectName("sectionLabel")
        self.section_label.setProperty("warning", False)
        self.section_label.setAlignment(Qt.AlignCenter)
        self.section_label.setFixedHeight(32)
        self.section_label.setStyleSheet(f"font-family:{APP_FONT};")
        content_layout.addWidget(self.section_label)

        self.credit_box = ClickableFrame()
        self.credit_box.setObjectName("credit")
        self.credit_box.setProperty("flash", False)
        self.credit_box.setFixedSize(BADGE_WIDTH, BADGE_HEIGHT)
        self.credit_box.pressed.connect(self.credit_box_pressed.emit)
        credit_layout = QHBoxLayout(self.credit_box)
        credit_layout.setContentsMargins(10, 10, 10, 10)
        credit_layout.setSpacing(10)
        coin = QLabel()
        coin.setFixedSize(32, 32)
        coin.setAlignment(Qt.AlignCenter)
        coin_pix = QPixmap(str(self.coin_image_path)).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if coin_pix.isNull():
            coin.setText("$")
            coin.setStyleSheet(f"font-family:{APP_FONT}; font-size:18px; font-weight:700; color:{SURFACE};")
        else:
            coin.setPixmap(coin_pix)

        self.credit_label = QLabel("Credito: $0")
        self.credit_label.setObjectName("creditText")
        self.credit_label.setStyleSheet(f"font-family:{APP_FONT}; font-size:22px; font-weight:700;")

        credit_layout.addWidget(coin)
        credit_layout.addWidget(self.credit_label, 1)

        self.alert_label = QLabel("")
        self.alert_label.setObjectName("alertLabel")
        self.alert_label.setProperty("role", "warning")
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setFixedHeight(24)
        self.alert_label.setStyleSheet(f"font-family:{APP_FONT};")
        self.alert_label.setVisible(False)
        content_layout.addWidget(self.alert_label)

        content_layout.addSpacing(4)

        self.product_area = QWidget()
        self.product_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.product_area_layout = QVBoxLayout(self.product_area)
        self.product_area_layout.setContentsMargins(0, 8, 0, 0)
        self.product_area_layout.setSpacing(0)

        self.product_row = QHBoxLayout()
        self.product_row.setContentsMargins(0, 0, 0, 0)
        self.product_row.setSpacing(18)
        for product in self.products:
            card = ProductCard(product)
            card.clicked.connect(lambda _, pid=product["id"]: self.product_selected.emit(pid))
            self.cards[product["id"]] = card
            self.product_row.addWidget(card, 1)
        self.product_area_layout.addLayout(self.product_row)
        content_layout.addWidget(self.product_area, 9)

        content_layout.addStretch(1)
        content_layout.addSpacing(12)

        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(0, 0, 0, 0)
        footer_row.setSpacing(0)

        self.action_box = QFrame()
        self.action_box.setObjectName("actionBox")
        self.action_box.setGraphicsEffect(QGraphicsDropShadowEffect(self.action_box))
        action_shadow = self.action_box.graphicsEffect()
        action_shadow.setBlurRadius(8)
        action_shadow.setOffset(0, 3)
        action_shadow.setColor(color_with_alpha(TEXT_SECONDARY, 40))
        action_layout = QHBoxLayout(self.action_box)
        action_layout.setContentsMargins(10, 10, 10, 10)
        action_layout.setSpacing(12)

        self.ok_btn = QPushButton("Seleccionar producto")
        self.ok_btn.setProperty("variant", "primary")
        self.ok_btn.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.setStyleSheet(
            f"QPushButton{{font-family:{APP_FONT}; font-size:21px; text-align:left; padding-left:18px;}}"
        )
        self.ok_btn.setGraphicsEffect(QGraphicsDropShadowEffect(self.ok_btn))
        ok_shadow = self.ok_btn.graphicsEffect()
        ok_shadow.setBlurRadius(10)
        ok_shadow.setOffset(0, 3)
        ok_shadow.setColor(color_with_alpha(PRIMARY, 70))
        self.ok_btn.clicked.connect(self.ok_pressed.emit)
        action_layout.addWidget(self.ok_btn, 0, Qt.AlignLeft | Qt.AlignVCenter)
        action_layout.addWidget(self.credit_box, 0, Qt.AlignRight | Qt.AlignVCenter)
        footer_row.addWidget(self.action_box)
        content_layout.addLayout(footer_row)
        root.addWidget(content_frame)

    def mousePressEvent(self, event):
        for name, btn in (("ok", self.ok_btn),):
            if btn.isEnabled():
                continue
            top_left = btn.mapTo(self, btn.rect().topLeft())
            rect = QRect(top_left, btn.size())
            if rect.contains(event.pos()):
                self.disabled_control_touched.emit(name)
                break
        super().mousePressEvent(event)

    def set_credit(self, credit: float):
        self.credit_label.setProperty("role", "")
        refresh_style(self.credit_label)
        self.credit_label.setText(f"Credito: ${credit:.0f}")

    def show_credit_warning(self, text: str):
        self.credit_label.setProperty("role", "warning")
        refresh_style(self.credit_label)
        self.credit_label.setText(text)

    def show_alert(self, text: str, ms: int = 3000):
        self.alert_label.setText(text)
        self.alert_label.setVisible(True)
        QTimer.singleShot(ms, self.clear_alert)

    def clear_alert(self):
        self.alert_label.clear()
        self.alert_label.setVisible(False)

    def set_selected(self, product_id: str | None):
        for pid, card in self.cards.items():
            card.setChecked(pid == product_id)

    def set_product_enabled(self, product_id: str, enabled: bool):
        self.cards[product_id].setEnabled(True)
        self.cards[product_id].set_affordable(enabled)

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
        if not text:
            self.section_label.clear()
            self.section_label.setProperty("warning", False)
            refresh_style(self.section_label)
            return
        self.section_label.setText(text)
        self.section_label.setProperty("warning", warning)
        refresh_style(self.section_label)

    def set_countdown(self, seconds: int | None):
        return

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
            if card.isEnabled():
                card.pulse_attention(3)

    def play_idle_attention_animation(self):
        self.blink_enabled_products()
