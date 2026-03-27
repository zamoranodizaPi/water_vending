"""Queued audio playback helper that delegates playback to play_audio.py."""
from __future__ import annotations

import logging
import subprocess
import sys
from collections import deque
from pathlib import Path

from PyQt5.QtCore import QObject, QTimer

from app.paths import resource_root

logger = logging.getLogger(__name__)


class AudioManager(QObject):
    def __init__(self, audio_files: dict[str, object], parent: QObject | None = None):
        super().__init__(parent)
        self._audio_files = {name: str(path) for name, path in audio_files.items()}
        self._queue: deque[tuple[str, int]] = deque()
        self._next_gap_ms = 250
        self._process: subprocess.Popen | None = None
        self._script_path = resource_root() / "play_audio.py"

        self._gap_timer = QTimer(self)
        self._gap_timer.setSingleShot(True)
        self._gap_timer.timeout.connect(self._play_next)

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(100)
        self._poll_timer.timeout.connect(self._poll_process)

        logger.info("Audio delegate script: %s", self._script_path)

    def play(self, name: str, gap_ms: int = 250, interrupt: bool = False):
        self.queue([name], gap_ms=gap_ms, interrupt=interrupt)

    def queue(self, names: list[str], gap_ms: int = 250, interrupt: bool = False):
        if interrupt:
            self.stop()
        for name in names:
            self._queue.append((name, gap_ms))
        if not self._is_busy():
            self._play_next()

    def stop(self):
        self._queue.clear()
        self._gap_timer.stop()
        self._poll_timer.stop()
        if self._process is not None and self._process.poll() is None:
            self._process.kill()
            try:
                self._process.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                pass
        self._process = None

    def _is_busy(self) -> bool:
        if self._gap_timer.isActive():
            return True
        if self._process is not None and self._process.poll() is None:
            return True
        return False

    def _poll_process(self):
        if self._process is None:
            self._poll_timer.stop()
            return
        result = self._process.poll()
        if result is None:
            return
        self._poll_timer.stop()
        stdout = ""
        stderr = ""
        try:
            stdout, stderr = self._process.communicate(timeout=0.1)
        except subprocess.TimeoutExpired:
            pass
        if stdout:
            logger.info("play_audio.py output: %s", stdout.strip())
        if stderr:
            logger.warning("play_audio.py stderr: %s", stderr.strip())
        if result != 0:
            logger.warning("play_audio.py exit code: %s", result)
        self._process = None
        self._gap_timer.start(self._next_gap_ms)

    def _play_next(self):
        if self._is_busy() or not self._queue:
            return

        name, gap_ms = self._queue.popleft()
        self._next_gap_ms = gap_ms

        if name not in self._audio_files:
            logger.warning("Audio key not configured: %s", name)
            self._gap_timer.start(0)
            return
        if not self._script_path.exists():
            logger.warning("Audio delegate script missing: %s", self._script_path)
            self._gap_timer.start(0)
            return

        args = [sys.executable, str(self._script_path), "--key", name]
        logger.info("Delegating audio playback: %s", " ".join(args))
        try:
            self._process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(resource_root()),
            )
        except Exception as exc:
            logger.warning("Failed to start play_audio.py: %s", exc)
            self._process = None
            self._gap_timer.start(0)
            return

        self._poll_timer.start()
