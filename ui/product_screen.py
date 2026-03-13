"""Main screen with product selection and touch-first controls."""
from __future__ import annotations

from PyQt5.QtCore import pyqtSignal, Qt
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
        self.setMinimumHeight(240)
        self.setStyleSheet(
            """
            QPushButton {border:3px solid #d5d9de; border-radius:18px; background:#f7f8fa;}
            QPushButton:checked {border:4px solid #11b5d6; background:#dff5f8;}
            QPushButton:disabled {color:#9ca3af; background:#efefef;}
            """
        )

        lay = QVBoxLayout(self)
        lay.setSpacing(6)
        image = QLabel()
        image.setAlignment(Qt.AlignCenter)
        image.setFixedHeight(130)
        pix = QPixmap(str(product["image"])).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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


class ProductScreen(QWidget):
    product_selected = pyqtSignal(str)
    ok_pressed = pyqtSignal()
    rinse_pressed = pyqtSignal()

    def __init__(self, products, logo_path):
        super().__init__()
        self.products = products
        self.logo_path = logo_path
        self.cards = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(12)

        title_row = QHBoxLayout()
        title = QLabel("Agua Purificada Lupita")
        title.setStyleSheet("font-size:54px; font-weight:800; color:#0e7490;")
        logo = QLabel()
        logo.setFixedSize(120, 90)
        logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(110, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            logo.setText("Lupita")
            logo.setStyleSheet("font-size:22px; color:#0e7490;")
        else:
            logo.setPixmap(pix)
        title_row.addStretch()
        title_row.addWidget(title)
        title_row.addSpacing(20)
        title_row.addWidget(logo)
        title_row.addStretch()
        root.addLayout(title_row)

        credit_box = QFrame()
        credit_box.setStyleSheet("QFrame{background:#1ea6e3; border-radius:18px;}")
        c_lay = QHBoxLayout(credit_box)
        coin = QLabel("💰")
        coin.setStyleSheet("font-size:48px; background:white; border-radius:12px; padding:8px;")
        self.credit_label = QLabel("Crédito Disponible: $0")
        self.credit_label.setStyleSheet("font-size:42px; font-weight:800; color:white;")
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size:26px; font-weight:700; color:#fde047;")
        c_lay.addWidget(coin)
        c_lay.addWidget(self.credit_label)
        c_lay.addStretch()
        c_lay.addWidget(self.status_label)
        root.addWidget(credit_box)

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
        self.ok_btn.setStyleSheet("font-size:42px; font-weight:800; background:#06c167; color:white; border-radius:16px;")
        self.ok_btn.clicked.connect(self.ok_pressed.emit)

        self.rinse_btn = QPushButton("Enjuague")
        self.rinse_btn.setMinimumHeight(85)
        self.rinse_btn.setStyleSheet("font-size:40px; font-weight:700; background:#0ea5e9; color:white; border-radius:16px;")
        self.rinse_btn.clicked.connect(self.rinse_pressed.emit)

        btn_row.addWidget(self.ok_btn)
        btn_row.addWidget(self.rinse_btn)
        root.addLayout(btn_row)

        instr = QLabel(
            "Instrucciones:\n1. Inserta crédito • 2. Selecciona tu producto • 3. Presiona OK para llenar • 4. Usa Enjuague para limpiar"
        )
        instr.setAlignment(Qt.AlignCenter)
        instr.setStyleSheet("font-size:24px; color:#334155; background:#e7edf4; border-radius:12px; padding:10px;")
        root.addWidget(instr)

    def set_credit(self, credit: float):
        self.credit_label.setText(f"Crédito Disponible: ${credit:.0f}")

    def set_status(self, text: str):
        self.status_label.setText(text)

    def set_selected(self, product_id: str | None):
        for pid, card in self.cards.items():
            card.setChecked(pid == product_id)

    def set_product_enabled(self, product_id: str, enabled: bool):
        self.cards[product_id].setEnabled(enabled)

    def set_ok_enabled(self, enabled: bool):
        self.ok_btn.setEnabled(enabled)

    def set_rinse_enabled(self, enabled: bool):
        self.rinse_btn.setEnabled(enabled)
