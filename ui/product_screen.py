"""Product selection screen for a 1024x600 vending layout."""
from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QTimer, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap
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

APP_FONT = "'Roboto','Open Sans','DejaVu Sans'"
CARD_MIN_WIDTH = 285
CARD_HEIGHT = 250
BADGE_WIDTH = 300
BADGE_HEIGHT = 60
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 70
HEADER_WIDTH = 1024
HEADER_HEIGHT = 100


class ProductCard(QPushButton):
    def __init__(self, product: dict):
        super().__init__()
        self.product = product
        self._hovered = False
        self._affordable = True
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(CARD_MIN_WIDTH, CARD_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("QPushButton{background:transparent; border:none;}")

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(15, 23, 42, 35))
        self.setGraphicsEffect(self.shadow)

        self.shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius", self)
        self.shadow_anim.setDuration(150)
        self.shadow_anim.setEasingCurve(QEasingCurve.OutCubic)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.card_frame = QFrame()
        self.card_frame.setMinimumSize(CARD_MIN_WIDTH, CARD_HEIGHT)
        self.card_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        root.addWidget(self.card_frame)

        body = QVBoxLayout(self.card_frame)
        body.setContentsMargins(15, 15, 15, 15)
        body.setSpacing(4)

        self.image = QLabel()
        self.image.setFixedSize(120, 130)
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setStyleSheet("background:transparent;")
        pix = QPixmap(str(product["image"])).scaled(100, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.image.setText(product["name"])
            self.image.setStyleSheet(f"font-family:{APP_FONT}; font-size:13px; color:#6B7280;")
        else:
            self.image.setPixmap(pix)

        self.name = QLabel(product["name"])
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setWordWrap(True)
        self.name.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:14px; font-weight:600; color:#374151; background:transparent;"
        )

        self.volume = QLabel(f"{product['volume_l']} L")
        self.volume.setAlignment(Qt.AlignCenter)
        self.volume.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:12px; font-weight:500; color:#6B7280; background:transparent;"
        )

        self.price = QLabel(f"${product['price']:.0f}")
        self.price.setAlignment(Qt.AlignCenter)
        self.price.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:24px; font-weight:700; color:#0D6EFD; background:transparent;"
        )

        body.addWidget(self.image, 0, Qt.AlignHCenter)
        body.addWidget(self.name)
        body.addWidget(self.volume)
        body.addWidget(self.price)
        body.addStretch()

        self._apply_state(animated=False)

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
        if self.isChecked():
            background = "#E7F1FF"
            border = "#0D6EFD"
            blur = 18
            shadow_color = QColor(13, 110, 253, 45)
        elif self._hovered:
            background = "#F8FBFF"
            border = "#D6E4FF"
            blur = 17
            shadow_color = QColor(15, 23, 42, 40)
        elif not self._affordable:
            background = "#FFFFFF"
            border = "#E5E7EB"
            blur = 12
            shadow_color = QColor(15, 23, 42, 24)
        else:
            background = "#FFFFFF"
            border = "#E5E7EB"
            blur = 15
            shadow_color = QColor(15, 23, 42, 35)

        self.card_frame.setStyleSheet(
            f"QFrame{{background:{background}; border:1px solid {border}; border-radius:15px;}}"
        )
        self.shadow.setColor(shadow_color)
        if animated:
            self.shadow_anim.stop()
            self.shadow_anim.setStartValue(self.shadow.blurRadius())
            self.shadow_anim.setEndValue(blur)
            self.shadow_anim.start()
        else:
            self.shadow.setBlurRadius(blur)

    def pulse_attention(self, flashes: int = 3):
        group = QSequentialAnimationGroup(self)
        for _ in range(flashes):
            expand = QPropertyAnimation(self.shadow, b"blurRadius")
            expand.setDuration(170)
            expand.setStartValue(15)
            expand.setEndValue(22)
            expand.setEasingCurve(QEasingCurve.InOutQuad)

            settle = QPropertyAnimation(self.shadow, b"blurRadius")
            settle.setDuration(170)
            settle.setStartValue(22)
            settle.setEndValue(15)
            settle.setEasingCurve(QEasingCurve.InOutQuad)
            group.addAnimation(expand)
            group.addAnimation(settle)

        self.card_frame.setStyleSheet("QFrame{background:#F8FBFF; border:1px solid #B7D1FF; border-radius:15px;}")

        def _done():
            self._apply_state(animated=False)

        group.finished.connect(_done)
        group.start()

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


class ProductScreen(QWidget):
    product_selected = pyqtSignal(str)
    ok_pressed = pyqtSignal()
    rinse_pressed = pyqtSignal()
    disabled_control_touched = pyqtSignal(str)
    top_left_corner_pressed = pyqtSignal()

    def __init__(self, products, logo_path, coin_image_path):
        super().__init__()
        self.products = products
        self.logo_path = logo_path
        self.coin_image_path = coin_image_path
        self.cards = {}
        self._rinse_locked = False
        self._credit_base_style = f"font-family:{APP_FONT}; font-size:19px; font-weight:700; color:white;"
        self._credit_warning_style = f"font-family:{APP_FONT}; font-size:19px; font-weight:700; color:#FFF7ED;"
        self._section_base_style = f"font-family:{APP_FONT}; font-size:20px; font-weight:700; color:#1F2937;"
        self._section_warning_style = f"font-family:{APP_FONT}; font-size:20px; font-weight:700; color:#B91C1C;"
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("QWidget{background:#F1F5F9;}")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 16)
        root.setSpacing(0)

        self.header_frame = QFrame()
        self.header_frame.setFixedSize(HEADER_WIDTH, HEADER_HEIGHT)
        self.header_frame.setStyleSheet("QFrame{background:#FFFFFF; border:none;}")
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        self.service_hotspot = TopLeftHotspot()
        self.service_hotspot.setFixedSize(50, 50)
        self.service_hotspot.pressed.connect(self.top_left_corner_pressed.emit)
        self.service_hotspot.setStyleSheet("background:transparent;")
        self.service_hotspot.setParent(self.header_frame)
        self.service_hotspot.move(0, 0)

        self.logo_box = QFrame()
        self.logo_box.setStyleSheet("QFrame{background:#0A58CA; border:none; border-radius:12px;}")
        self.logo_box.setFixedSize(HEADER_WIDTH, HEADER_HEIGHT)
        self.logo = QLabel(self.logo_box)
        self.logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(1024, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.logo.setGeometry(0, 0, HEADER_WIDTH, HEADER_HEIGHT)
            self.logo.setText("Lupita")
            self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:28px; font-weight:700; color:#FFFFFF;")
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
        self.section_label.setAlignment(Qt.AlignCenter)
        self.section_label.setFixedHeight(32)
        self.section_label.setStyleSheet(self._section_base_style)
        content_layout.addWidget(self.section_label)

        self.credit_box = QFrame()
        self.credit_box.setFixedSize(BADGE_WIDTH, BADGE_HEIGHT)
        self.credit_box.setStyleSheet("QFrame{background:#0A58CA; border:none; border-radius:12px;}")
        credit_layout = QHBoxLayout(self.credit_box)
        credit_layout.setContentsMargins(10, 10, 10, 10)
        credit_layout.setSpacing(10)
        coin = QLabel()
        coin.setFixedSize(32, 32)
        coin.setAlignment(Qt.AlignCenter)
        coin_pix = QPixmap(str(self.coin_image_path)).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if coin_pix.isNull():
            coin.setText("$")
            coin.setStyleSheet(f"font-family:{APP_FONT}; font-size:18px; font-weight:700; color:#FBBF24;")
        else:
            coin.setPixmap(coin_pix)

        self.credit_label = QLabel("Credito: $0")
        self.credit_label.setStyleSheet(self._credit_base_style)

        credit_layout.addWidget(coin)
        credit_layout.addWidget(self.credit_label, 1)

        self.alert_label = QLabel("")
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setFixedHeight(24)
        self.alert_label.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:13px; font-weight:600; color:#B91C1C;"
        )
        self.alert_label.setVisible(False)
        content_layout.addWidget(self.alert_label)

        content_layout.addSpacing(4)

        self.product_row = QHBoxLayout()
        self.product_row.setContentsMargins(0, 8, 0, 0)
        self.product_row.setSpacing(18)
        for product in self.products:
            card = ProductCard(product)
            card.clicked.connect(lambda _, pid=product["id"]: self.product_selected.emit(pid))
            self.cards[product["id"]] = card
            self.product_row.addWidget(card, 1)
        content_layout.addLayout(self.product_row)

        content_layout.addStretch()
        content_layout.addSpacing(12)

        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(0, 0, 0, 0)
        footer_row.setSpacing(16)

        self.ok_btn = QPushButton("Seleccionar producto")
        self.ok_btn.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.setStyleSheet(
            f"QPushButton{{font-family:{APP_FONT}; font-size:18px; font-weight:700; background:#0D6EFD; color:white; border:none; border-radius:15px;}}"
            "QPushButton:hover{background:#0B5ED7;}"
            "QPushButton:pressed{background:#0A58CA;}"
            "QPushButton:disabled{background:#94A3B8; color:#E5E7EB;}"
        )
        self.ok_btn.clicked.connect(self.ok_pressed.emit)
        footer_row.addStretch()
        footer_row.addWidget(self.ok_btn, 0, Qt.AlignVCenter)
        footer_row.addWidget(self.credit_box, 0, Qt.AlignRight | Qt.AlignVCenter)
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
        self.credit_label.setStyleSheet(self._credit_base_style)
        self.credit_label.setText(f"Credito: ${credit:.0f}")

    def show_credit_warning(self, text: str):
        self.credit_label.setStyleSheet(self._credit_warning_style)
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
            self.section_label.setStyleSheet(self._section_base_style)
            return
        self.section_label.setText(text)
        self.section_label.setStyleSheet(self._section_warning_style if warning else self._section_base_style)

    def set_countdown(self, seconds: int | None):
        return

    def pulse_credit_attention(self):
        state = {"step": 0}
        normal_style = "QFrame{background:#0A58CA; border:none; border-radius:12px;}"
        flash_style = "QFrame{background:#0D6EFD; border:none; border-radius:12px;}"

        def _tick():
            if state["step"] >= 6:
                self.credit_box.setStyleSheet(normal_style)
                return
            self.credit_box.setStyleSheet(flash_style if state["step"] % 2 == 0 else normal_style)
            state["step"] += 1
            QTimer.singleShot(140, _tick)

        _tick()

    def blink_enabled_products(self):
        for card in self.cards.values():
            if card.isEnabled():
                card.pulse_attention(3)

    def play_idle_attention_animation(self):
        self.blink_enabled_products()
