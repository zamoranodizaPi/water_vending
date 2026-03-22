"""Progress screen used for rinse and filling operations."""
from __future__ import annotations

from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSizePolicy, QFrame

from theme import APP_FONT, PRIMARY, refresh_style


class DispensingScreen(QWidget):
    progress_changed = pyqtSignal(int)
    completed = pyqtSignal()
    emergency_pressed = pyqtSignal()

    def __init__(self, logo_path):
        super().__init__()
        self.setObjectName("dispensingScreen")
        self.logo_path = logo_path
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._elapsed_ms = 0
        self._total_ms = 1
        self._movie = None
        self._build_ui(logo_path)

    def _build_ui(self, logo_path):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(0)

        self.header_container = QFrame()
        self.header_container.setObjectName("header")
        self.header_container.setFixedHeight(78)
        header = QHBoxLayout(self.header_container)
        header.setContentsMargins(18, 10, 18, 10)
        header.setSpacing(12)

        self.logo = QLabel(self.header_container)
        self.logo.setObjectName("logoLabel")
        self.logo.setFixedSize(150, 54)
        self.logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        pix = QPixmap(str(logo_path)).scaled(140, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.logo.setText("Lupita")
            self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:{PRIMARY};")
        else:
            self.logo.setPixmap(pix)

        self.header_title = QLabel("Agua Purificada Lupita")
        self.header_title.setObjectName("headerTitle")
        self.header_title.setAlignment(Qt.AlignCenter)

        header.addWidget(self.logo, 0, Qt.AlignVCenter)
        header.addStretch()
        header.addWidget(self.header_title, 0, Qt.AlignCenter)
        header.addStretch()

        spacer = QWidget(self.header_container)
        spacer.setFixedWidth(150)
        header.addWidget(spacer, 0, Qt.AlignVCenter)
        root.addWidget(self.header_container)

        self.title = QLabel("Proceso")
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.animation = QLabel()
        self.animation.setAlignment(Qt.AlignCenter)
        self.animation.setMinimumHeight(180)
        self.animation.setMaximumHeight(210)

        self.progress = QProgressBar()
        self.progress.setObjectName("processProgress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(56)
        self.progress.setFixedWidth(430)
        self.progress.setStyleSheet(f"QProgressBar{{font-family:{APP_FONT};}}")

        self.emergency_btn = QPushButton("Detener")
        self.emergency_btn.setProperty("variant", "secondary")
        self.emergency_btn.setMinimumHeight(56)
        self.emergency_btn.setMinimumWidth(240)
        self.emergency_btn.setMaximumWidth(320)
        self.emergency_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.emergency_btn.setStyleSheet(f"QPushButton{{font-family:{APP_FONT}; font-size:22px;}}")
        self.emergency_btn.clicked.connect(self.emergency_pressed.emit)
        self.emergency_btn.setVisible(False)

        root.addSpacing(10)
        root.addWidget(self.title)
        root.addSpacing(8)
        root.addWidget(self.animation)
        root.addSpacing(16)
        root.addWidget(self.progress, alignment=Qt.AlignCenter)
        root.addSpacing(14)
        root.addWidget(self.emergency_btn, alignment=Qt.AlignCenter)
        root.addStretch()

    def set_credit(self, credit: float):
        return

    def start(self, title: str, total_seconds: float, gif_path=None, image_path=None, image_size=None, emergency_enabled: bool = False):
        self.title.setText(title)
        self._total_ms = max(500, int(total_seconds * 1000))
        self._elapsed_ms = 0
        self.progress.setValue(0)
        self.emergency_btn.setVisible(emergency_enabled)
        self.animation.clear()
        self.animation.setMovie(None)
        self._movie = None

        if image_path:
            width, height = image_size or (220, 180)
            pix = QPixmap(str(image_path)).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if pix.isNull():
                self.animation.setText("[Imagen no disponible]")
                self.animation.setProperty("role", "secondary")
                self.animation.setStyleSheet("font-size:22px;")
                refresh_style(self.animation)
            else:
                self.animation.setPixmap(pix)
                self.animation.setProperty("role", "")
                self.animation.setStyleSheet("")
                refresh_style(self.animation)
        elif gif_path:
            self._movie = QMovie(str(gif_path))
            if self._movie.isValid():
                self.animation.setMovie(self._movie)
                self._movie.start()
            else:
                self.animation.setText("[Animación no disponible]")
                self.animation.setProperty("role", "secondary")
                self.animation.setStyleSheet("font-size:22px;")
                refresh_style(self.animation)

        self._timer.start(200)

    def stop_now(self):
        self._timer.stop()

    def _tick(self):
        self._elapsed_ms += 200
        pct = min(100, int((self._elapsed_ms / self._total_ms) * 100))
        self.progress.setValue(pct)
        self.progress_changed.emit(pct)
        if pct >= 100:
            self._timer.stop()
            self.completed.emit()
