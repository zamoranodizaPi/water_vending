"""Product selection screen with touch-friendly cards."""
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


class ProductScreen(QWidget):
    product_selected = pyqtSignal(dict)
    rinse_requested = pyqtSignal()

    def __init__(self, products, logo_path):
        super().__init__()
        self.products = products
        self.logo_path = logo_path
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        header = QHBoxLayout()
        header.addStretch()

        logo = QLabel()
        logo.setFixedSize(180, 90)
        logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(180, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            logo.setText("LOGO")
            logo.setStyleSheet("font-size: 22px; font-weight: bold; color:#1e88e5;")
        else:
            logo.setPixmap(pix)
        header.addWidget(logo)
        root.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        for idx, product in enumerate(self.products):
            card = self._build_card(product)
            grid.addWidget(card, 0, idx)
        root.addLayout(grid)

        rinse_btn = QPushButton("Rinse")
        rinse_btn.setMinimumHeight(80)
        rinse_btn.setStyleSheet("font-size: 26px; font-weight: bold; background:#2b7; color:white;")
        rinse_btn.clicked.connect(self.rinse_requested.emit)
        root.addWidget(rinse_btn)

    def _build_card(self, product):
        card = QFrame()
        card.setStyleSheet("QFrame{border:2px solid #dddddd; border-radius:12px; background:#ffffff;}")
        lay = QVBoxLayout(card)

        image = QLabel()
        image.setFixedHeight(180)
        image.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(product["image"])).scaled(220, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            image.setText(product["name"])
            image.setStyleSheet("font-size: 20px; color:#607d8b;")
        else:
            image.setPixmap(pix)

        name = QLabel(product["name"])
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("font-size: 24px; font-weight: bold;")

        details = QLabel(f"{product['volume_l']} L  |  ${product['price']:.2f}")
        details.setAlignment(Qt.AlignCenter)
        details.setStyleSheet("font-size: 20px;")

        btn = QPushButton("Select")
        btn.setMinimumHeight(70)
        btn.setStyleSheet("font-size: 24px; font-weight: bold; background:#1976d2; color:white;")
        btn.clicked.connect(lambda: self.product_selected.emit(product))

        lay.addWidget(image)
        lay.addWidget(name)
        lay.addWidget(details)
        lay.addWidget(btn)
        return card
