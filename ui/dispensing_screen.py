"""Dispensing progress screen."""
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
        self.title = QLabel("Dispensing in progress")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 34px; font-weight: bold;")

        self.message = QLabel("Please wait while your container is being filled")
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setStyleSheet("font-size: 24px;")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(50)
        self.progress.setStyleSheet("font-size: 24px;")

        root.addStretch()
        root.addWidget(self.title)
        root.addWidget(self.message)
        root.addWidget(self.progress)
        root.addStretch()

    def start(self, total_seconds: float):
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
