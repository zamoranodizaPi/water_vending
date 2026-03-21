"""Main screen with touch-friendly product selection and compact kiosk layout."""
from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QTimer, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

APP_FONT = "'Spicy Rice','DejaVu Sans'"
CARD_HEIGHT = 190
BUTTON_HEIGHT = 56
SECTION_NOTE_HEIGHT = 50


class ProductCard(QPushButton):
    def __init__(self, product: dict):
        super().__init__()
        self.product = product
        self.setCheckable(True)
        self.setMinimumHeight(CARD_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._default_style = (
            f"QPushButton{{font-family:{APP_FONT}; border:3px solid #cbd5e1; border-radius:20px; background:#f8fafc;}}"
            f"QPushButton:checked{{border:4px solid #0891b2; background:#e0f7fa;}}"
            "QPushButton:disabled{color:#94a3b8; background:#e5e7eb; border-color:#cbd5e1;}"
        )
        self._highlight_style = (
            f"QPushButton{{font-family:{APP_FONT}; border:4px solid #22c55e; border-radius:20px; background:#ecfdf5;}}"
            f"QPushButton:checked{{border:4px solid #0891b2; background:#e0f7fa;}}"
            "QPushButton:disabled{color:#94a3b8; background:#e5e7eb; border-color:#cbd5e1;}"
        )
        self.setStyleSheet(self._default_style)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(4)

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setFixedHeight(86)
        pix = QPixmap(str(product["image"])).scaled(100, 86, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.image.setText(product["name"])
            self.image.setStyleSheet("font-size:14px; color:#475569;")
        else:
            self.image.setPixmap(pix)

        self.name = QLabel(product["name"])
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setWordWrap(True)
        self.name.setStyleSheet(f"font-family:{APP_FONT}; font-size:17px; font-weight:800; color:#0f172a;")

        self.volume = QLabel(f"{product['volume_l']}L")
        self.volume.setAlignment(Qt.AlignCenter)
        self.volume.setStyleSheet(f"font-family:{APP_FONT}; font-size:14px; color:#475569;")

        self.price = QLabel(f"${product['price']:.0f}")
        self.price.setAlignment(Qt.AlignCenter)
        self.price.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:900; color:#0891b2;")

        lay.addWidget(self.image)
        lay.addWidget(self.name)
        lay.addWidget(self.volume)
        lay.addWidget(self.price)

        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity)

    def pulse_attention(self, flashes: int = 3):
        self.setStyleSheet(self._highlight_style)
        group = QSequentialAnimationGroup(self)
        for _ in range(flashes):
            fade_out = QPropertyAnimation(self._opacity, b"opacity")
            fade_out.setDuration(220)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.6)
            fade_out.setEasingCurve(QEasingCurve.InOutQuad)

            fade_in = QPropertyAnimation(self._opacity, b"opacity")
            fade_in.setDuration(220)
            fade_in.setStartValue(0.6)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.InOutQuad)

            group.addAnimation(fade_out)
            group.addAnimation(fade_in)

        def _done():
            self._opacity.setOpacity(1.0)
            self.setStyleSheet(self._default_style)

        group.finished.connect(_done)
        group.start()

    def is_affordable(self) -> bool:
        return self.isEnabled()


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
        self._credit_base_style = f"font-family:{APP_FONT}; font-size:22px; font-weight:800; color:white;"
        self._credit_warning_style = f"font-family:{APP_FONT}; font-size:22px; font-weight:800; color:#fff7ed;"
        self._section_base_style = f"font-family:{APP_FONT}; font-size:24px; font-weight:900; color:#0e7490;"
        self._section_warning_style = f"font-family:{APP_FONT}; font-size:24px; font-weight:900; color:#b91c1c;"
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("QWidget{background:#f3f7fb;}")
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 8, 14, 8)
        root.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.service_hotspot = TopLeftHotspot()
        self.service_hotspot.setFixedSize(50, 50)
        self.service_hotspot.pressed.connect(self.top_left_corner_pressed.emit)
        self.service_hotspot.setStyleSheet("background:transparent;")
        top_row.addWidget(self.service_hotspot, 0, Qt.AlignTop | Qt.AlignLeft)

        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(0)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(8)
        brand_row.setAlignment(Qt.AlignCenter)

        title1 = QLabel("Agua Purificada")
        title1.setAlignment(Qt.AlignCenter)
        title1.setStyleSheet(f"font-family:{APP_FONT}; font-size:34px; font-weight:900; color:#0e7490;")
        title2 = QLabel("Lupita")
        title2.setAlignment(Qt.AlignCenter)
        title2.setStyleSheet("font-size:36px; font-weight:700; font-family:'Brush Script MT'; color:#ec4899;")

        brand_row.addWidget(title1)
        brand_row.addWidget(title2)

        self.section_label = QLabel("Seleccione su producto")
        self.section_label.setAlignment(Qt.AlignCenter)
        self.section_label.setMinimumHeight(SECTION_NOTE_HEIGHT)
        self.section_label.setStyleSheet(self._section_base_style)

        title_wrap.addLayout(brand_row)
        title_wrap.addWidget(self.section_label)

        top_row.addLayout(title_wrap, 1)

        logo = QLabel()
        logo.setFixedSize(126, 68)
        logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(120, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            logo.setText("Lupita")
            logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:22px; font-weight:800; color:#0e7490;")
        else:
            logo.setPixmap(pix)
        top_row.addWidget(logo, 0, Qt.AlignTop | Qt.AlignRight)
        root.addLayout(top_row)

        self.credit_box = QFrame()
        self.credit_box.setMinimumHeight(58)
        self.credit_box.setStyleSheet("QFrame{background:#06b6d4; border:none; border-radius:16px;}")
        c_lay = QHBoxLayout(self.credit_box)
        c_lay.setContentsMargins(12, 6, 12, 6)
        c_lay.setSpacing(10)

        coin = QLabel()
        coin.setFixedSize(38, 38)
        coin.setAlignment(Qt.AlignCenter)
        coin_pix = QPixmap(str(self.coin_image_path)).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if coin_pix.isNull():
            coin.setText("$")
            coin.setStyleSheet(f"font-family:{APP_FONT}; font-size:22px; font-weight:900; color:#0f172a;")
        else:
            coin.setPixmap(coin_pix)
        coin.setStyleSheet("background:white; border-radius:12px;")

        self.credit_label = QLabel("Credito Disponible: $0")
        self.credit_label.setStyleSheet(self._credit_base_style)

        self.countdown_label = QLabel("")
        self.countdown_label.setMinimumHeight(SECTION_NOTE_HEIGHT)
        self.countdown_label.setMinimumWidth(180)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:18px; font-weight:800; color:white; background:#0891b2; border-radius:14px; padding:6px 12px;"
        )
        self.countdown_label.setVisible(False)

        c_lay.addWidget(coin)
        c_lay.addWidget(self.credit_label, 1)
        c_lay.addSpacing(8)
        c_lay.addWidget(self.countdown_label, 0, Qt.AlignRight)
        root.addWidget(self.credit_box)

        self.alert_label = QLabel("")
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setMinimumHeight(SECTION_NOTE_HEIGHT)
        self.alert_label.setStyleSheet(f"font-family:{APP_FONT}; font-size:20px; font-weight:900; color:#dc2626;")
        self.alert_label.setVisible(False)
        root.addWidget(self.alert_label)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        for idx, product in enumerate(self.products):
            card = ProductCard(product)
            card.clicked.connect(lambda _, pid=product["id"]: self.product_selected.emit(pid))
            self.cards[product["id"]] = card
            grid.addWidget(card, 0, idx)
        root.addLayout(grid)

        button_row = QHBoxLayout()
        button_row.setSpacing(16)
        button_row.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setMinimumHeight(BUTTON_HEIGHT)
        self.ok_btn.setMinimumWidth(250)
        self.ok_btn.setMaximumWidth(320)
        self.ok_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ok_btn.setStyleSheet(
            f"QPushButton{{font-family:{APP_FONT}; font-size:30px; font-weight:900; background:#10b981; color:white; border:none; border-radius:16px; padding:6px 18px;}}"
            "QPushButton:disabled{background:#94a3b8; color:#e2e8f0;}"
        )
        self.ok_btn.clicked.connect(self.ok_pressed.emit)

        button_row.addWidget(self.ok_btn)
        button_row.addStretch()
        root.addLayout(button_row)

        instructions = QLabel("1. Inserte credito   2. Seleccione producto   3. Presione OK para llenar")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        instructions.setMinimumHeight(SECTION_NOTE_HEIGHT)
        instructions.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:15px; color:#334155; background:#e2e8f0; border-radius:14px; padding:8px 12px;"
        )
        root.addWidget(instructions)

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
        self.credit_label.setText(f"Credito Disponible: ${credit:.0f}")

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
        if not text:
            self.section_label.setText("Seleccione su producto")
            self.section_label.setStyleSheet(self._section_base_style)
            return
        self.section_label.setText(text)
        self.section_label.setStyleSheet(self._section_warning_style if warning else self._section_base_style)

    def set_countdown(self, seconds: int | None):
        if seconds is None:
            self.countdown_label.clear()
            self.countdown_label.setVisible(False)
            return
        self.countdown_label.setText(f"Tiempo: {seconds}s")
        self.countdown_label.setVisible(True)

    def pulse_credit_attention(self):
        state = {"step": 0}
        normal_style = "QFrame{background:#06b6d4; border:none; border-radius:16px;}"
        flash_style = "QFrame{background:#0ea5e9; border:none; border-radius:16px;}"

        def _tick():
            if state["step"] >= 6:
                self.credit_box.setStyleSheet(normal_style)
                return
            self.credit_box.setStyleSheet(flash_style if state["step"] % 2 == 0 else normal_style)
            state["step"] += 1
            QTimer.singleShot(160, _tick)

        _tick()

    def blink_enabled_products(self):
        for card in self.cards.values():
            if card.isEnabled():
                card.pulse_attention(3)

    def play_idle_attention_animation(self):
        self.blink_enabled_products()
