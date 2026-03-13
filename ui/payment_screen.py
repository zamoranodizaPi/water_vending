"""Instruction and message screens for preparation steps."""
from __future__ import annotations

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class PromptScreen(QWidget):
    ok_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        self.title = QLabel("Instrucción")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:48px; font-weight:800; color:#0f766e;")

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setFixedHeight(300)

        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("font-size:30px; color:#0f172a;")

        ok_btn = QPushButton("OK")
        ok_btn.setMinimumHeight(90)
        ok_btn.setStyleSheet("font-size:42px; font-weight:800; background:#06c167; color:white; border-radius:14px;")
        ok_btn.clicked.connect(self.ok_pressed.emit)

        root.addStretch()
        root.addWidget(self.title)
        root.addWidget(self.image)
        root.addWidget(self.subtitle)
        root.addStretch()
        root.addWidget(ok_btn)

    def configure(self, title: str, image_path, subtitle: str):
        self.title.setText(title)
        pix = QPixmap(str(image_path)).scaled(360, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.image.setText("[Imagen no disponible]")
            self.image.setStyleSheet("font-size:28px; color:#64748b;")
        else:
            self.image.setPixmap(pix)
            self.image.setStyleSheet("")
        self.subtitle.setText(subtitle)


class MessageScreen(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        self.message = QLabel("")
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setStyleSheet("font-size:52px; font-weight:800; color:#075985;")
        lay.addStretch()
        lay.addWidget(self.message)
        lay.addStretch()

    def set_message(self, text: str):
        self.message.setText(text)
