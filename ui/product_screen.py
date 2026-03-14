"""Main screen with adaptive product selection and touch-first controls."""
from __future__ import annotations

from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ProductCard(QPushButton):
    def __init__(self, product: dict):
        super().__init__()
        self.product = product
        self.setCheckable(True)
        self.setMinimumHeight(250)
        self._default_style = (
            "QPushButton {border:3px solid #d5d9de; border-radius:18px; background:#f7f8fa;}"
            "QPushButton:checked {border:4px solid #11b5d6; background:#dff5f8;}"
            "QPushButton:disabled {color:#9ca3af; background:#efefef;}"
        )
        self._highlight_style = (
            "QPushButton {border:4px solid #22c55e; border-radius:18px; background:#ecfdf5;}"
            "QPushButton:checked {border:5px solid #11b5d6; background:#dff5f8;}"
            "QPushButton:disabled {color:#9ca3af; background:#efefef;}"
        )
        self.setStyleSheet(self._default_style)

        lay = QVBoxLayout(self)
        lay.setSpacing(6)
        image = QLabel()
        image.setAlignment(Qt.AlignCenter)
        image.setFixedHeight(130)
        pix = QPixmap(str(product["image"])).scaled(140, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            image.setText(product["name"])
            image.setStyleSheet("font-size:16px; color:#5b6470;")
        else:
            image.setPixmap(pix)

        name = QLabel(product["name"])
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("font-size:24px; font-weight:700; color:#1f2937;")

        volume = QLabel(f"{product['volume_l']}L")
        volume.setAlignment(Qt.AlignCenter)
        volume.setStyleSheet("font-size:20px; color:#4b5563;")

        price = QLabel(f"${product['price']:.0f}")
        price.setAlignment(Qt.AlignCenter)
        price.setStyleSheet("font-size:36px; font-weight:800; color:#0ea5c6;")

        lay.addWidget(image)
        lay.addWidget(name)
        lay.addWidget(volume)
        lay.addWidget(price)

    def pulse_attention(self, flashes: int = 3):
        total_steps = flashes * 2
        state = {"step": 0}

        def _toggle():
            if state["step"] >= total_steps:
                self.setStyleSheet(self._default_style)
                return
            self.setStyleSheet(self._highlight_style if state["step"] % 2 == 0 else self._default_style)
            state["step"] += 1
            QTimer.singleShot(170, _toggle)

        _toggle()


class ProductScreen(QWidget):
    product_selected = pyqtSignal(str)
    ok_pressed = pyqtSignal()
    rinse_pressed = pyqtSignal()

    def __init__(self, products, logo_path):
        super().__init__()
        self.products = products
        self.logo_path = logo_path
        self.cards = {}
        self._credit_base_style = "font-size:42px; font-weight:800; color:white;"
        self._credit_warning_style = "font-size:42px; font-weight:800; color:#ef4444;"
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(12)

        title_row = QHBoxLayout()
        title1 = QLabel("Agua Purificada ")
        title1.setStyleSheet("font-size:52px; font-weight:800; color:#0e7490;")
        title2 = QLabel("Lupita")
        title2.setStyleSheet("font-size:56px; font-weight:700; font-family:'Brush Script MT'; color:#ec4899;")
        title_container = QHBoxLayout()
        title_container.addWidget(title1)
        title_container.addWidget(title2)

        logo = QLabel()
        logo.setFixedSize(132, 99)
        logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(121, 88, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            logo.setText("Lupita")
            logo.setStyleSheet("font-size:22px; color:#0e7490;")
        else:
            logo.setPixmap(pix)
        title_row.addStretch()
        title_row.addLayout(title_container)
        title_row.addSpacing(20)
        title_row.addWidget(logo)
        title_row.addStretch()
        root.addLayout(title_row)

        self.credit_box = QFrame()
        self.credit_box.setStyleSheet("QFrame{background:#06b6d4; border:3px solid #2563eb; border-radius:18px;}")
        c_lay = QHBoxLayout(self.credit_box)
        coin = QLabel("💰")
        coin.setStyleSheet("font-size:48px; background:white; border-radius:12px; padding:8px;")
        self.credit_label = QLabel("Crédito Disponible: $0")
        self.credit_label.setStyleSheet(self._credit_base_style)
        c_lay.addWidget(coin)
        c_lay.addWidget(self.credit_label)
        c_lay.addStretch()
        root.addWidget(self.credit_box)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        for idx, product in enumerate(self.products):
            card = ProductCard(product)
            card.clicked.connect(lambda _, pid=product["id"]: self.product_selected.emit(pid))
            self.cards[product["id"]] = card
            grid.addWidget(card, 0, idx)
        root.addLayout(grid)

        btn_row = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setMinimumHeight(85)
        self.ok_btn.setStyleSheet("font-size:42px; font-weight:800; background:#10b981; color:white; border-radius:16px;")
        self.ok_btn.clicked.connect(self.ok_pressed.emit)

        self.rinse_btn = QPushButton("☐ Enjuague Opcional")
        self.rinse_btn.setCheckable(True)
        self.rinse_btn.setMinimumHeight(85)
        self.rinse_btn.setStyleSheet(
            "QPushButton{font-size:32px; font-weight:700; background:#38bdf8; color:white; border-radius:16px;}"
            "QPushButton:checked{background:#22c55e; color:white;}"
        )
        self.rinse_btn.toggled.connect(self._on_rinse_toggled)
        self.rinse_btn.clicked.connect(self.rinse_pressed.emit)

        btn_row.addWidget(self.ok_btn)
        btn_row.addWidget(self.rinse_btn)
        root.addLayout(btn_row)

        instr = QLabel(
            "Instrucciones:\n1. Inserta crédito • 2. Selecciona tu producto • 3. Presiona OK para llenar • 4. Enjuague es opcional"
        )
        instr.setAlignment(Qt.AlignCenter)
        instr.setStyleSheet("font-size:24px; color:#334155; background:#e2e8f0; border-radius:12px; padding:10px;")
        root.addWidget(instr)

    def _on_rinse_toggled(self, checked: bool):
        self.rinse_btn.setText("☑ Enjuague Opcional" if checked else "☐ Enjuague Opcional")

    def set_credit(self, credit: float):
        self.credit_label.setStyleSheet(self._credit_base_style)
        self.credit_label.setText(f"Crédito Disponible: ${credit:.0f}")

    def show_credit_warning(self, text: str):
        self.credit_label.setStyleSheet(self._credit_warning_style)
        self.credit_label.setText(text)

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

    def is_rinse_checked(self) -> bool:
        return self.rinse_btn.isChecked()

    def pulse_credit_attention(self):
        state = {"step": 0}
        big_style = "QFrame{background:#06b6d4; border:3px solid #2563eb; border-radius:20px; padding:12px;}"
        normal_style = "QFrame{background:#06b6d4; border:3px solid #2563eb; border-radius:18px;}"

        def _tick():
            if state["step"] >= 8:
                self.credit_box.setStyleSheet(normal_style)
                return
            self.credit_box.setStyleSheet(big_style if state["step"] % 2 == 0 else normal_style)
            state["step"] += 1
            QTimer.singleShot(170, _tick)

        _tick()

    def blink_enabled_products(self):
        for card in self.cards.values():
            if card.isEnabled():
                card.pulse_attention(3)
