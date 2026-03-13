"""Payment screen with live credit and coin animation."""
from __future__ import annotations

from PyQt5.QtCore import QPoint, QPropertyAnimation, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class PaymentScreen(QWidget):
    confirm_pressed = pyqtSignal()
    back_pressed = pyqtSignal()

    def __init__(self, coin_image):
        super().__init__()
        self.coin_image = coin_image
        self._animation = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        self.title = QLabel("Insert coins")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 34px; font-weight: bold;")

        self.selection = QLabel("No product selected")
        self.selection.setAlignment(Qt.AlignCenter)
        self.selection.setStyleSheet("font-size: 24px;")

        self.credit = QLabel("Credit: $0.00")
        self.credit.setAlignment(Qt.AlignCenter)
        self.credit.setStyleSheet("font-size: 38px; color:#00695c; font-weight: bold;")

        self.coin = QLabel(self)
        self.coin.setAlignment(Qt.AlignCenter)
        self.coin.setFixedSize(150, 150)
        pix = QPixmap(str(self.coin_image)).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.coin.setText("COIN")
            self.coin.setStyleSheet("font-size: 28px; font-weight: bold; color:#f9a825;")
        else:
            self.coin.setPixmap(pix)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setMinimumHeight(90)
        self.ok_btn.setStyleSheet("font-size: 30px; font-weight:bold; background:#43a047; color:white;")
        self.ok_btn.clicked.connect(self.confirm_pressed.emit)

        back_btn = QPushButton("Back")
        back_btn.setMinimumHeight(70)
        back_btn.setStyleSheet("font-size: 22px;")
        back_btn.clicked.connect(self.back_pressed.emit)

        root.addWidget(self.title)
        root.addWidget(self.selection)
        root.addWidget(self.credit)
        root.addWidget(self.coin, alignment=Qt.AlignCenter)
        root.addStretch()
        root.addWidget(self.ok_btn)
        root.addWidget(back_btn)

    def set_product(self, product):
        self.selection.setText(
            f"{product['name']} - {product['volume_l']}L - ${product['price']:.2f}"
        )

    def set_credit(self, amount: float):
        self.credit.setText(f"Credit: ${amount:.2f}")

    def animate_coin(self):
        start = QPoint(self.coin.x(), self.coin.y())
        end = QPoint(self.coin.x(), max(20, self.coin.y() - 35))
        self._animation = QPropertyAnimation(self.coin, b"pos")
        self._animation.setDuration(260)
        self._animation.setStartValue(start)
        self._animation.setKeyValueAt(0.5, end)
        self._animation.setEndValue(start)
        self._animation.start()
