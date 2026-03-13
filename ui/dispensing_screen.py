"""Progress screen used for rinse and filling operations."""
from __future__ import annotations

from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget


class DispensingScreen(QWidget):
    progress_changed = pyqtSignal(int)
    completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._elapsed_ms = 0
        self._total_ms = 1
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        self.title = QLabel("Proceso")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:54px; font-weight:800; color:#0f766e;")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(52)
        self.progress.setFixedWidth(380)
        self.progress.setStyleSheet("font-size:26px;")

        root.addStretch()
        root.addWidget(self.title)
        root.addSpacing(30)
        root.addWidget(self.progress, alignment=Qt.AlignCenter)
        root.addStretch()

    def start(self, title: str, total_seconds: float):
        self.title.setText(title)
        self._total_ms = max(500, int(total_seconds * 1000))
        self._elapsed_ms = 0
        self.progress.setValue(0)
        self._timer.start(200)

    def _tick(self):
        self._elapsed_ms += 200
        pct = min(100, int((self._elapsed_ms / self._total_ms) * 100))
        self.progress.setValue(pct)
        self.progress_changed.emit(pct)
        if pct >= 100:
            self._timer.stop()
            self.completed.emit()
