"""Main screen with adaptive product selection and touch-first controls."""
from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QTimer, pyqtSignal, Qt, QRect
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)
from PyQt5.QtGui import QPixmap


class ProductCard(QPushButton):
    def __init__(self, product: dict):
        super().__init__()
        self.product = product
        self.setCheckable(True)
        self.setMinimumHeight(190)
        self.setMinimumHeight(168)
        self._default_style = (
            "QPushButton {border:4px solid #d5d9de; border-radius:24px; background:#f8fafc;}"
            "QPushButton:checked {border:5px solid #06b6d4; background:#dff5f8;}"
            "QPushButton:disabled {color:#9ca3af; background:#efefef;}"
        )
        self._highlight_style = (
            "QPushButton {border:5px solid #22c55e; border-radius:24px; background:#ecfdf5;}"
            "QPushButton:checked {border:6px solid #06b6d4; background:#dff5f8;}"
            "QPushButton:disabled {color:#9ca3af; background:#efefef;}"
        )
        self.setStyleSheet(self._default_style)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)

        image = QLabel()
        image.setAlignment(Qt.AlignCenter)
        image.setFixedHeight(95)
        pix = QPixmap(str(product["image"])).scaled(110, 95, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image.setFixedHeight(92)
        pix = QPixmap(str(product["image"])).scaled(126, 118, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            image.setText(product["name"])
            image.setStyleSheet("font-size:16px; color:#5b6470;")
        else:
            image.setPixmap(pix)

        name = QLabel(product["name"])
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("font-size:20px; font-weight:700; color:#1f2937;")

        volume = QLabel(f"{product['volume_l']}L")
        volume.setAlignment(Qt.AlignCenter)
        volume.setStyleSheet("font-size:16px; color:#4b5563;")

        price = QLabel(f"${product['price']:.0f}")
        price.setAlignment(Qt.AlignCenter)
        price.setStyleSheet("font-size:36px; font-weight:800; color:#0891b2;")
        price.setStyleSheet("font-size:28px; font-weight:800; color:#0ea5c6;")

        lay.addWidget(image)
        lay.addWidget(name)
        lay.addWidget(volume)
        lay.addWidget(price)

        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity)

    def pulse_attention(self, flashes: int = 3):
        self.setStyleSheet(self._highlight_style)
        group = QSequentialAnimationGroup(self)
        for _ in range(flashes):
            fade_out = QPropertyAnimation(self._opacity, b"opacity")
            fade_out.setDuration(240)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.55)
            fade_out.setEasingCurve(QEasingCurve.InOutQuad)

            fade_in = QPropertyAnimation(self._opacity, b"opacity")
            fade_in.setDuration(240)
            fade_in.setStartValue(0.55)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.InOutQuad)

            group.addAnimation(fade_out)
            group.addAnimation(fade_in)

        def _done():
            self._opacity.setOpacity(1.0)
            self.setStyleSheet(self._default_style)

        group.finished.connect(_done)
        group.start()


class ProductScreen(QWidget):
    product_selected = pyqtSignal(str)
    ok_pressed = pyqtSignal()
    rinse_pressed = pyqtSignal()
    disabled_control_touched = pyqtSignal(str)

    def __init__(self, products, logo_path, coin_image_path):
        super().__init__()
        self.products = products
        self.logo_path = logo_path
        self.coin_image_path = coin_image_path
        self.cards = {}
        self._credit_base_style = "font-size:26px; font-weight:800; color:white;"
        self._credit_warning_style = "font-size:26px; font-weight:800; color:white;"
        self._credit_base_style = "font-size:31px; font-weight:800; color:white;"
        self._credit_warning_style = "font-size:31px; font-weight:800; color:white;"
        self._rinse_locked = False
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 10, 18, 10)
        root.setSpacing(10)

        title_row = QHBoxLayout()
        title_row.setSpacing(14)
        title1 = QLabel("Agua Purificada")
        title1.setAlignment(Qt.AlignCenter)
        title1.setStyleSheet("font-size:52px; font-weight:800; color:#0e7490;")
        title2 = QLabel("Lupita")
        title2.setAlignment(Qt.AlignCenter)
        title2.setStyleSheet("font-size:54px; font-weight:700; font-family:'Brush Script MT'; color:#ec4899;")
        root.setContentsMargins(12, 6, 12, 6)
        root.setSpacing(6)

        title_row = QHBoxLayout()
        title1 = QLabel("Agua Purificada ")
        title1.setAlignment(Qt.AlignCenter)
        title1.setStyleSheet("font-size:40px; font-weight:800; color:#0e7490;")
        title2 = QLabel("Lupita")
        title2.setAlignment(Qt.AlignCenter)
        title2.setStyleSheet("font-size:42px; font-weight:700; font-family:'Brush Script MT'; color:#ec4899;")
        title_container = QHBoxLayout()
        title_container.addWidget(title1)
        title_container.addWidget(title2)

        logo = QLabel()
        logo.setFixedSize(192, 144)
        logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(176, 132, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setFixedSize(96, 72)
        logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(88, 66, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            logo.setText("Lupita")
            logo.setStyleSheet("font-size:28px; color:#0e7490;")
        else:
            logo.setPixmap(pix)
        title_row.addStretch()
        title_row.addLayout(title_container)
        title_row.addWidget(logo)
        title_row.addStretch()
        root.addLayout(title_row)

        self.alert_label = QLabel("")
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setVisible(False)
        self.alert_label.setStyleSheet("font-size:32px; font-weight:900; color:#dc2626;")
        root.addWidget(self.alert_label)

        self.credit_box = QFrame()
        self.credit_box.setMinimumHeight(96)
        self.credit_box.setStyleSheet("QFrame{background:#06b6d4; border:none; border-radius:22px;}")
        c_lay = QHBoxLayout(self.credit_box)
        c_lay.setContentsMargins(18, 12, 18, 12)
        c_lay.setSpacing(14)

        coin = QLabel()
        coin.setFixedSize(64, 64)
        coin.setAlignment(Qt.AlignCenter)
        coin_pix = QPixmap(str(self.coin_image_path)).scaled(58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if coin_pix.isNull():
            coin.setText("💰")
            coin.setStyleSheet("font-size:40px;")
        else:
            coin.setPixmap(coin_pix)
        coin.setStyleSheet("background:white; border-radius:14px;")

        self.alert_label.setStyleSheet("font-size:27px; font-weight:900; color:#dc2626;")
        root.addWidget(self.alert_label)

        self.credit_box = QFrame()
        self.credit_box.setFixedHeight(44)
        self.credit_box.setStyleSheet("QFrame{background:#06b6d4; border:none; border-radius:10px;}")
        c_lay = QHBoxLayout(self.credit_box)
        c_lay.setContentsMargins(10, 4, 10, 4)
        c_lay.setSpacing(8)
        coin = QLabel()
        coin.setFixedSize(26, 26)
        coin.setAlignment(Qt.AlignCenter)
        coin_pix = QPixmap(str(self.coin_image_path)).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if coin_pix.isNull():
            coin.setText("💰")
            coin.setStyleSheet("font-size:20px;")
        else:
            coin.setPixmap(coin_pix)
        self.credit_label = QLabel("Crédito Disponible: $0")
        self.credit_label.setStyleSheet(self._credit_base_style)

        self.insert_hint_btn = QPushButton("Insertar $5")
        self.insert_hint_btn.setEnabled(False)
        self.insert_hint_btn.setMinimumHeight(56)
        self.insert_hint_btn.setMinimumWidth(180)
        self.insert_hint_btn.setStyleSheet(
            "QPushButton{font-size:20px; font-weight:800; background:#facc15; color:#111827; border-radius:16px; border:none;}"
            "QPushButton:disabled{color:#111827;}"
        )

        c_lay.addWidget(coin)
        c_lay.addWidget(self.credit_label)
        c_lay.addStretch()
        c_lay.addWidget(self.insert_hint_btn)
        root.addWidget(self.credit_box)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setHorizontalSpacing(10)
        for idx, product in enumerate(self.products):
            card = ProductCard(product)
            card.clicked.connect(lambda _, pid=product["id"]: self.product_selected.emit(pid))
            self.cards[product["id"]] = card
            grid.addWidget(card, 0, idx)
        root.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setMinimumHeight(72)
        self.ok_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ok_btn.setStyleSheet("font-size:38px; font-weight:800; background:#10b981; color:white; border-radius:18px;")
        self.ok_btn.setMinimumHeight(61)
        self.ok_btn.setMinimumWidth(270)
        self.ok_btn.setMaximumWidth(378)
        self.ok_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ok_btn.setStyleSheet("font-size:34px; font-weight:800; background:#10b981; color:white; border-radius:14px;")
        self.ok_btn.clicked.connect(self.ok_pressed.emit)

        self.rinse_btn = QPushButton("☐ Enjuague")
        self.rinse_btn.setCheckable(True)
        self.rinse_btn.setMinimumHeight(72)
        self.rinse_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.rinse_btn.setStyleSheet(
            "QPushButton{font-size:34px; font-weight:700; background:#22c1dc; color:white; border-radius:18px;}"
        self.rinse_btn.setMinimumHeight(61)
        self.rinse_btn.setMinimumWidth(270)
        self.rinse_btn.setMaximumWidth(378)
        self.rinse_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.rinse_btn.setStyleSheet(
            "QPushButton{font-size:26px; font-weight:700; background:#38bdf8; color:white; border-radius:14px;}"
            "QPushButton:checked{background:#22c55e; color:white;}"
        )
        self.rinse_btn.clicked.connect(self._on_rinse_clicked)

        btn_row.addStretch()
        btn_row.addWidget(self.ok_btn)
        btn_row.addSpacing(16)
        btn_row.addWidget(self.rinse_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        instr = QLabel(
            "Instrucciones:\n1. Inserta crédito • 2. Selecciona tu producto • 3. Presiona OK para llenar • 4. Usa Enjuague para limpiar"
        )
        instr.setAlignment(Qt.AlignCenter)
        instr.setStyleSheet("font-size:21px; color:#334155; background:#dce5ef; border-radius:14px; padding:10px;")
        instr.setStyleSheet("font-size:17px; color:#334155; background:#e2e8f0; border-radius:10px; padding:6px;")
        root.addWidget(instr)

    def _on_rinse_clicked(self):
        if self._rinse_locked:
            self.rinse_btn.setChecked(True)
            return
        if self.rinse_btn.isChecked():
            self.rinse_btn.setText("☑ Enjuague")
            self.rinse_pressed.emit()
        else:
            self.rinse_btn.setText("☐ Enjuague")

    def mousePressEvent(self, event):
        for name, btn in (("ok", self.ok_btn), ("rinse", self.rinse_btn)):
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
        self.credit_label.setText(f"Crédito Disponible: ${credit:.0f}")

    def show_credit_warning(self, text: str):
        self.credit_label.setStyleSheet(self._credit_warning_style)
        self.credit_label.setText(text)

    def show_alert(self, text: str, ms: int = 3000):
        self.alert_label.setText(text)
        self.alert_label.setVisible(True)
        QTimer.singleShot(ms, lambda: self.alert_label.setVisible(False))

    def set_selected(self, product_id: str | None):
        for pid, card in self.cards.items():
            card.setChecked(pid == product_id)

    def set_product_enabled(self, product_id: str, enabled: bool):
        self.cards[product_id].setEnabled(enabled)

    def set_ok_enabled(self, enabled: bool):
        self.ok_btn.setEnabled(enabled)

    def set_rinse_enabled(self, enabled: bool):
        self.rinse_btn.setEnabled(enabled)

    def set_rinse_checked(self, checked: bool):
        self.rinse_btn.setChecked(checked)
        self.rinse_btn.setText("☑ Enjuague" if checked else "☐ Enjuague")

    def lock_rinse_selection(self, locked: bool):
        self._rinse_locked = locked

    def is_rinse_checked(self) -> bool:
        return self.rinse_btn.isChecked()

    def pulse_credit_attention(self):
        state = {"step": 0}
        big_style = "QFrame{background:#0ea5e9; border:none; border-radius:22px;}"
        normal_style = "QFrame{background:#06b6d4; border:none; border-radius:22px;}"
        big_style = "QFrame{background:#e0f2fe; border:none; border-radius:0; padding:8px;}"
        normal_style = "QFrame{background:transparent; border:none;}"

        def _tick():
            if state["step"] >= 8:
                self.credit_box.setStyleSheet(normal_style)
                return
            self.credit_box.setStyleSheet(big_style if state["step"] % 2 == 0 else normal_style)
            state["step"] += 1
            QTimer.singleShot(180, _tick)

        _tick()

    def blink_enabled_products(self):
        for card in self.cards.values():
            if card.isEnabled():
                card.pulse_attention(3)
