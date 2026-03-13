from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class IdleScreen(QWidget):
    def __init__(self, product_name: str, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Selecciona tu producto")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 42px; font-weight: bold;")

        arrow = QLabel("⬇")
        arrow.setAlignment(Qt.AlignCenter)
        arrow.setStyleSheet("font-size: 72px; color: #1f77b4;")

        product = QLabel(product_name)
        product.setAlignment(Qt.AlignCenter)
        product.setStyleSheet(
            "background: #0066cc; color: white; font-size: 38px; padding: 20px; border-radius: 12px;"
        )

        layout.addWidget(title)
        layout.addWidget(arrow)
        layout.addWidget(product)


class DispensingScreen(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Despachando agua")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 48px; font-weight: bold;")

        animation = QLabel("💧💧💧")
        animation.setAlignment(Qt.AlignCenter)
        animation.setStyleSheet("font-size: 74px;")

        subtitle = QLabel("Por favor espere...")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 32px;")

        layout.addWidget(title)
        layout.addWidget(animation)
        layout.addWidget(subtitle)
