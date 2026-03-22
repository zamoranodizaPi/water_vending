"""Progress screen used for rinse and filling operations."""
from __future__ import annotations

from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSizePolicy, QFrame

from theme import APP_FONT, PRIMARY, SURFACE, refresh_style

HEADER_WIDTH = 1004
HEADER_HEIGHT = 100


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
        root.setContentsMargins(10, 5, 10, 16)
        root.setSpacing(0)

        self.header_container = QFrame()
        self.header_container.setObjectName("header")
        self.header_container.setFixedSize(HEADER_WIDTH, HEADER_HEIGHT)
        header = QHBoxLayout(self.header_container)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(0)

        self.logo_box = QFrame()
        self.logo_box.setObjectName("logoBox")
        self.logo_box.setFixedSize(HEADER_WIDTH, HEADER_HEIGHT)
        self.logo = QLabel(self.logo_box)
        self.logo.setObjectName("logoLabel")
        self.logo.setGeometry(0, 0, HEADER_WIDTH, HEADER_HEIGHT)
        self.logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(logo_path)).scaled(1004, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.logo.setText("Lupita")
            self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:28px; font-weight:700; color:{SURFACE};")
        else:
            self.logo.setPixmap(pix)
        header.addWidget(self.logo_box, 0, Qt.AlignCenter)
        root.addWidget(self.header_container)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 0, 16, 0)
        content_layout.setSpacing(0)

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

        content_layout.addStretch(1)
        content_layout.addWidget(self.title)
        content_layout.addSpacing(10)
        content_layout.addWidget(self.animation, alignment=Qt.AlignCenter)
        content_layout.addSpacing(16)
        content_layout.addWidget(self.progress, alignment=Qt.AlignCenter)
        content_layout.addSpacing(14)
        content_layout.addWidget(self.emergency_btn, alignment=Qt.AlignCenter)
        content_layout.addStretch(1)
        root.addWidget(content)

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
