"""Main screen with modern touch-friendly product selection."""
from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QTimer, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

APP_FONT = "'Roboto','Open Sans','DejaVu Sans'"
HEADER_HEIGHT = 80
CARD_HEIGHT = 220
BUTTON_HEIGHT = 60
SECTION_NOTE_HEIGHT = 44


class ModernProductIcon(QWidget):
    def __init__(self, product_id: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.product_id = product_id
        self.setFixedSize(102, 102)

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#eaf3ff"))
        painter.drawEllipse(4, 4, 94, 94)

        if self.product_id == "gallon":
            self._draw_gallon(painter)
        elif self.product_id == "half_garrafon":
            self._draw_half_bottle(painter)
        else:
            self._draw_full_bottle(painter)

    def _draw_full_bottle(self, painter: QPainter):
        path = QPainterPath()
        path.moveTo(40, 16)
        path.lineTo(62, 16)
        path.lineTo(66, 26)
        path.lineTo(66, 34)
        path.cubicTo(74, 40, 79, 48, 79, 59)
        path.lineTo(79, 80)
        path.cubicTo(79, 87, 74, 91, 67, 91)
        path.lineTo(35, 91)
        path.cubicTo(28, 91, 23, 87, 23, 80)
        path.lineTo(23, 59)
        path.cubicTo(23, 48, 28, 40, 36, 34)
        path.lineTo(36, 26)
        path.closeSubpath()
        painter.setBrush(QColor("#0d6efd"))
        painter.drawPath(path)

        painter.setBrush(QColor(255, 255, 255, 70))
        painter.drawRoundedRect(33, 28, 10, 46, 5, 5)
        painter.setBrush(QColor("#cfe2ff"))
        painter.drawRoundedRect(36, 18, 30, 8, 4, 4)

    def _draw_half_bottle(self, painter: QPainter):
        path = QPainterPath()
        path.moveTo(40, 24)
        path.lineTo(62, 24)
        path.lineTo(65, 34)
        path.lineTo(65, 40)
        path.cubicTo(73, 46, 76, 52, 76, 60)
        path.lineTo(76, 78)
        path.cubicTo(76, 85, 71, 89, 64, 89)
        path.lineTo(38, 89)
        path.cubicTo(31, 89, 26, 85, 26, 78)
        path.lineTo(26, 60)
        path.cubicTo(26, 52, 29, 46, 37, 40)
        path.lineTo(37, 34)
        path.closeSubpath()
        painter.setBrush(QColor("#38bdf8"))
        painter.drawPath(path)

        painter.setBrush(QColor(255, 255, 255, 78))
        painter.drawRoundedRect(36, 34, 9, 36, 5, 5)
        painter.setBrush(QColor("#dbeafe"))
        painter.drawRoundedRect(37, 24, 28, 8, 4, 4)

    def _draw_gallon(self, painter: QPainter):
        body = QPainterPath()
        body.moveTo(34, 30)
        body.cubicTo(28, 34, 24, 41, 24, 50)
        body.lineTo(24, 78)
        body.cubicTo(24, 85, 29, 90, 36, 90)
        body.lineTo(64, 90)
        body.cubicTo(71, 90, 76, 85, 76, 78)
        body.lineTo(76, 48)
        body.cubicTo(76, 42, 73, 37, 69, 34)
        body.lineTo(63, 34)
        body.lineTo(60, 25)
        body.lineTo(43, 25)
        body.lineTo(40, 30)
        body.closeSubpath()
        painter.setBrush(QColor("#2563eb"))
        painter.drawPath(body)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#93c5fd"), 6))
        painter.drawArc(56, 22, 22, 24, 35 * 16, 235 * 16)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 80))
        painter.drawRoundedRect(34, 38, 9, 30, 4, 4)


class ProductCard(QPushButton):
    def __init__(self, product: dict):
        super().__init__()
        self.product = product
        self._hovered = False
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(CARD_HEIGHT)
        self.setMinimumWidth(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("QPushButton{background:transparent; border:none;}")

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(14)
        self.shadow.setOffset(5, 5)
        self.shadow.setColor(QColor("#dbeafe"))
        self.setGraphicsEffect(self.shadow)

        self.shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius", self)
        self.shadow_anim.setDuration(180)
        self.shadow_anim.setEasingCurve(QEasingCurve.OutCubic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.card_frame = QFrame()
        self.card_frame.setMinimumHeight(CARD_HEIGHT)
        self.card_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.card_frame)

        body = QVBoxLayout(self.card_frame)
        body.setContentsMargins(16, 16, 16, 16)
        body.setSpacing(9)

        self.icon_shell = QFrame()
        self.icon_shell.setFixedSize(118, 118)
        self.icon_shell.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.icon_shell.setStyleSheet("QFrame{background:#f8fbff; border-radius:28px;}")
        icon_layout = QVBoxLayout(self.icon_shell)
        icon_layout.setContentsMargins(8, 8, 8, 8)
        icon_layout.addWidget(ModernProductIcon(product["id"]), 0, Qt.AlignCenter)

        self.name = QLabel(product["name"])
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setWordWrap(True)
        self.name.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:18px; font-weight:600; color:#333333; background:transparent;"
        )

        self.volume = QLabel(f"{product['volume_l']} L")
        self.volume.setAlignment(Qt.AlignCenter)
        self.volume.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:13px; font-weight:600; color:#64748b; background:transparent;"
        )

        self.price = QLabel(f"${product['price']:.0f}")
        self.price.setAlignment(Qt.AlignCenter)
        self.price.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:30px; font-weight:800; color:#0d6efd; background:transparent;"
        )

        body.addWidget(self.icon_shell, 0, Qt.AlignCenter)
        body.addSpacing(2)
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
        if not self.isEnabled():
            bg = "#edf1f5"
            border = "#d7dee7"
            shadow = QColor(0, 0, 0, 12)
            blur = 10
        elif self.isChecked():
            bg = "#e7f1ff"
            border = "#0d6efd"
            shadow = QColor("#dbeafe")
            blur = 22
        elif self._hovered:
            bg = "#f0f8ff"
            border = "#8ab4ff"
            shadow = QColor("#dbeafe")
            blur = 18
        else:
            bg = "#ffffff"
            border = "#dbe4f0"
            shadow = QColor("#dbeafe")
            blur = 14

        self.card_frame.setStyleSheet(
            f"QFrame{{background:{bg}; border:3px solid {border}; border-radius:24px;}}"
        )
        self.icon_shell.setStyleSheet(
            "QFrame{background:#f8fbff; border:none; border-radius:28px;}"
            if self.isEnabled()
            else "QFrame{background:#f1f5f9; border:none; border-radius:28px;}"
        )
        self.shadow.setColor(shadow)
        if animated:
            self.shadow_anim.stop()
            self.shadow_anim.setStartValue(self.shadow.blurRadius())
            self.shadow_anim.setEndValue(blur)
            self.shadow_anim.start()
        else:
            self.shadow.setBlurRadius(blur)

    def pulse_attention(self, flashes: int = 3):
        self._hovered = True
        group = QSequentialAnimationGroup(self)
        for _ in range(flashes):
            grow = QPropertyAnimation(self.shadow, b"blurRadius")
            grow.setDuration(170)
            grow.setStartValue(14)
            grow.setEndValue(22)
            grow.setEasingCurve(QEasingCurve.InOutQuad)

            settle = QPropertyAnimation(self.shadow, b"blurRadius")
            settle.setDuration(170)
            settle.setStartValue(22)
            settle.setEndValue(14)
            settle.setEasingCurve(QEasingCurve.InOutQuad)

            group.addAnimation(grow)
            group.addAnimation(settle)

        self.card_frame.setStyleSheet("QFrame{background:#f0f8ff; border:3px solid #0d6efd; border-radius:24px;}")
        self.shadow.setColor(QColor("#dbeafe"))

        def _done():
            self._hovered = False
            self._apply_state(animated=False)

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
        self._credit_base_style = f"font-family:{APP_FONT}; font-size:21px; font-weight:700; color:white;"
        self._credit_warning_style = f"font-family:{APP_FONT}; font-size:21px; font-weight:700; color:#fff7ed;"
        self._section_base_style = f"font-family:{APP_FONT}; font-size:21px; font-weight:700; color:#1d4ed8;"
        self._section_warning_style = f"font-family:{APP_FONT}; font-size:21px; font-weight:700; color:#b91c1c;"
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("QWidget{background:#f4f7fb;}")
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(22)

        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(HEADER_HEIGHT)
        self.header_frame.setStyleSheet("QFrame{background:#0d6efd; border-radius:22px;}")
        header_shadow = QGraphicsDropShadowEffect(self.header_frame)
        header_shadow.setBlurRadius(12)
        header_shadow.setOffset(0, 4)
        header_shadow.setColor(QColor(13, 110, 253, 45))
        self.header_frame.setGraphicsEffect(header_shadow)
        header = QHBoxLayout(self.header_frame)
        header.setContentsMargins(18, 10, 18, 10)
        header.setSpacing(10)

        self.service_hotspot = TopLeftHotspot()
        self.service_hotspot.setFixedSize(50, 50)
        self.service_hotspot.pressed.connect(self.top_left_corner_pressed.emit)
        self.service_hotspot.setStyleSheet("background:transparent;")

        self.logo = QLabel()
        self.logo.setFixedSize(1024, 110)
        self.logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(1024, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.logo.setText("Lupita")
            self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:white;")
        else:
            self.logo.setPixmap(pix)

        header.addWidget(self.service_hotspot, 0, Qt.AlignVCenter)
        header.addWidget(self.logo, 1, Qt.AlignCenter)
        root.addWidget(self.header_frame)

        self.section_label = QLabel("Seleccione su producto")
        self.section_label.setAlignment(Qt.AlignCenter)
        self.section_label.setMinimumHeight(SECTION_NOTE_HEIGHT)
        self.section_label.setStyleSheet(self._section_base_style)
        root.addWidget(self.section_label)

        self.credit_box = QFrame()
        self.credit_box.setMinimumHeight(68)
        self.credit_box.setStyleSheet("QFrame{background:#0a58ca; border:none; border-radius:20px;}")
        credit_layout = QHBoxLayout(self.credit_box)
        credit_layout.setContentsMargins(20, 10, 20, 10)
        credit_layout.setSpacing(14)

        coin_wrap = QFrame()
        coin_wrap.setFixedSize(48, 48)
        coin_wrap.setStyleSheet("QFrame{background:#ffd24d; border:none; border-radius:22px;}")
        coin_inner = QVBoxLayout(coin_wrap)
        coin_inner.setContentsMargins(0, 0, 0, 0)
        coin = QLabel()
        coin.setAlignment(Qt.AlignCenter)
        coin_pix = QPixmap(str(self.coin_image_path)).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if coin_pix.isNull():
            coin.setText("$")
            coin.setStyleSheet(f"font-family:{APP_FONT}; font-size:20px; font-weight:800; color:#7c4a00;")
        else:
            coin.setPixmap(coin_pix)
        coin_inner.addWidget(coin)

        self.credit_label = QLabel("Credito Disponible: $0")
        self.credit_label.setStyleSheet(self._credit_base_style)

        self.countdown_label = QLabel("")
        self.countdown_label.setMinimumHeight(50)
        self.countdown_label.setMinimumWidth(180)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:17px; font-weight:700; color:white; background:#0847a6; border:none; border-radius:16px; padding:6px 12px;"
        )
        self.countdown_label.setVisible(False)

        credit_layout.addWidget(coin_wrap)
        credit_layout.addWidget(self.credit_label, 1)
        credit_layout.addWidget(self.countdown_label, 0, Qt.AlignRight)
        root.addWidget(self.credit_box)

        self.alert_label = QLabel("")
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setMinimumHeight(SECTION_NOTE_HEIGHT)
        self.alert_label.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:18px; font-weight:700; color:#c62828;"
        )
        self.alert_label.setVisible(False)
        root.addWidget(self.alert_label)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(25)
        grid.setVerticalSpacing(20)
        for idx, product in enumerate(self.products):
            card = ProductCard(product)
            card.clicked.connect(lambda _, pid=product["id"]: self.product_selected.emit(pid))
            self.cards[product["id"]] = card
            grid.addWidget(card, 0, idx)
        root.addLayout(grid)

        button_row = QHBoxLayout()
        button_row.setSpacing(0)
        button_row.addStretch()

        self.ok_btn = QPushButton("Seleccionar producto")
        self.ok_btn.setMinimumHeight(BUTTON_HEIGHT)
        self.ok_btn.setMinimumWidth(410)
        self.ok_btn.setMaximumWidth(410)
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_shadow = QGraphicsDropShadowEffect(self.ok_btn)
        button_shadow.setBlurRadius(14)
        button_shadow.setOffset(5, 5)
        button_shadow.setColor(QColor("#dbeafe"))
        self.ok_btn.setGraphicsEffect(button_shadow)
        self.ok_btn.setStyleSheet(
            f"QPushButton{{font-family:{APP_FONT}; font-size:26px; font-weight:700; background:#0d6efd; color:white; border:none; border-radius:18px; padding:10px 28px;}}"
            "QPushButton:hover{background:#0b5ed7;}"
            "QPushButton:pressed{background:#0a58ca;}"
            "QPushButton:disabled{background:#94a3b8; color:#e2e8f0;}"
        )
        self.ok_btn.clicked.connect(self.ok_pressed.emit)

        button_row.addWidget(self.ok_btn)
        button_row.addStretch()
        root.addLayout(button_row)

        self.instructions = QLabel("Toque una tarjeta para elegir el envase y luego presione el boton azul.")
        self.instructions.setAlignment(Qt.AlignCenter)
        self.instructions.setWordWrap(True)
        self.instructions.setMinimumHeight(SECTION_NOTE_HEIGHT)
        self.instructions.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:15px; font-weight:600; color:#475569; background:#e9eef6; border:none; border-radius:14px; padding:8px 12px;"
        )
        root.addWidget(self.instructions)

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
        normal_style = "QFrame{background:#0a58ca; border:none; border-radius:20px;}"
        flash_style = "QFrame{background:#0d6efd; border:none; border-radius:20px;}"

        def _tick():
            if state["step"] >= 6:
                self.credit_box.setStyleSheet(normal_style)
                return
            self.credit_box.setStyleSheet(flash_style if state["step"] % 2 == 0 else normal_style)
            state["step"] += 1
            QTimer.singleShot(150, _tick)

        _tick()

    def blink_enabled_products(self):
        for card in self.cards.values():
            if card.isEnabled():
                card.pulse_attention(3)

    def play_idle_attention_animation(self):
        self.blink_enabled_products()
