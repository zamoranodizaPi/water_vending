from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget, QHBoxLayout

from theme import APP_FONT, PRIMARY, SURFACE


class BaseScreen(QWidget):
    def __init__(self, logo_path: str | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.logo_path = logo_path
        self.setObjectName("screen")
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(14, 10, 14, 10)
        self.root.setSpacing(0)
        self._build_header()

    def _build_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header")
        self.header_frame.setFixedHeight(82)
        row = QHBoxLayout(self.header_frame)
        row.setContentsMargins(20, 10, 20, 10)
        row.setSpacing(12)

        self.logo = QLabel(self.header_frame)
        self.logo.setObjectName("logoLabel")
        self.logo.setFixedSize(920, 82)
        self.logo.setAlignment(Qt.AlignCenter)
        if self.logo_path:
            pix = QPixmap(str(self.logo_path)).scaled(900, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if not pix.isNull():
                self.logo.setPixmap(pix)
            else:
                self.logo.setText("Lupita")
                self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:{PRIMARY};")
        else:
            self.logo.setText("Lupita")
            self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:{PRIMARY};")
        row.addWidget(self.logo, 1, Qt.AlignCenter)

        self.root.addWidget(self.header_frame)


class IdleScreen(BaseScreen):
    def __init__(self, product_name: str, logo_path: str | None = None, parent: QWidget | None = None):
        self.product_name = product_name
        super().__init__(logo_path, parent)
        self._build_body()

    def _build_body(self):
        title = QLabel("Seleccione producto")
        title.setObjectName("screenTitle")
        title.setAlignment(Qt.AlignCenter)

        product = QLabel(self.product_name)
        product.setAlignment(Qt.AlignCenter)
        product.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:38px; font-weight:800; color:{SURFACE}; "
            f"background:{PRIMARY}; border-radius:18px; padding:18px 28px;"
        )

        self.root.addSpacing(24)
        self.root.addWidget(title)
        self.root.addSpacing(28)
        self.root.addWidget(product, alignment=Qt.AlignCenter)
        self.root.addStretch()


class DispensingScreen(BaseScreen):
    def __init__(self, logo_path: str | None = None, parent: QWidget | None = None):
        super().__init__(logo_path, parent)
        self._build_body()

    def _build_body(self):
        title = QLabel("Despachando agua")
        title.setObjectName("screenTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Por favor espere...")
        subtitle.setObjectName("bodyText")
        subtitle.setAlignment(Qt.AlignCenter)

        self.root.addSpacing(24)
        self.root.addWidget(title)
        self.root.addSpacing(22)
        self.root.addWidget(subtitle)
        self.root.addStretch()
