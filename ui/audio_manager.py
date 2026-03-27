"""Queued audio playback helper using the same subprocess backend as test_audio.py."""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from collections import deque
from pathlib import Path

from PyQt5.QtCore import QObject, QTimer

logger = logging.getLogger(__name__)


class AudioManager(QObject):
    def __init__(self, audio_files: dict[str, object], parent: QObject | None = None):
        super().__init__(parent)
        self._audio_files = {name: str(path) for name, path in audio_files.items()}
        self._queue: deque[tuple[str, int]] = deque()
        self._missing_logged: set[str] = set()
        self._next_gap_ms = 250
        self._process: subprocess.Popen | None = None

        self._gap_timer = QTimer(self)
        self._gap_timer.setSingleShot(True)
        self._gap_timer.timeout.connect(self._play_next)

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(100)
        self._poll_timer.timeout.connect(self._poll_process)

        self._external_player = self._detect_external_player()
        if self._external_player:
            logger.info("Audio backend: subprocess %s", self._external_player[0])
        else:
            logger.warning("Audio backend unavailable")

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

    def _detect_external_player(self) -> tuple[str, list[str]] | None:
        forced_player = os.getenv("VENDING_AUDIO_PLAYER", "").strip()
        if forced_player:
            forced_path = shutil.which(forced_player) or forced_player
            if Path(forced_path).exists():
                return forced_path, []

        candidates = (
            ("mpg123", ["-q"], ("/usr/bin/mpg123", "/usr/local/bin/mpg123")),
            ("mpg321", ["-q"], ("/usr/bin/mpg321", "/usr/local/bin/mpg321")),
            ("cvlc", ["--play-and-exit", "--quiet"], ("/usr/bin/cvlc", "/usr/local/bin/cvlc")),
            ("vlc", ["--intf", "dummy", "--play-and-exit", "--quiet"], ("/usr/bin/vlc", "/usr/local/bin/vlc")),
            ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet"], ("/usr/bin/ffplay", "/usr/local/bin/ffplay")),
            ("paplay", [], ("/usr/bin/paplay", "/usr/local/bin/paplay")),
            ("aplay", [], ("/usr/bin/aplay", "/usr/local/bin/aplay")),
        )
        for command, base_args, absolute_candidates in candidates:
            resolved = shutil.which(command)
            if resolved:
                return resolved, base_args
            for absolute_path in absolute_candidates:
                if Path(absolute_path).exists():
                    return absolute_path, base_args
        return None

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
            logger.info("Audio player output: %s", stdout.strip())
        if stderr:
            logger.warning("Audio player error output: %s", stderr.strip())
        if result != 0:
            logger.warning("Audio player exit code: %s", result)
        self._process = None
        self._gap_timer.start(self._next_gap_ms)

    def _play_next(self):
        if self._is_busy() or not self._queue:
            return

        name, gap_ms = self._queue.popleft()
        path = self._audio_files.get(name)
        self._next_gap_ms = gap_ms
        if not path:
            logger.warning("Audio key not configured: %s", name)
            self._gap_timer.start(0)
            return

        file_path = Path(path)
        logger.info("Audio requested: key=%s path=%s", name, file_path)
        if not file_path.exists():
            if name not in self._missing_logged:
                logger.warning("Audio file missing: %s", path)
                self._missing_logged.add(name)
            self._gap_timer.start(0)
            return

        if not self._external_player:
            logger.warning("No audio backend could play: %s", path)
            self._gap_timer.start(0)
            return

        command, base_args = self._external_player
        args = [command, *base_args, str(file_path)]
        logger.info("Playing audio with subprocess backend: %s", " ".join(args))
        try:
            self._process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except Exception as exc:
            logger.warning("Failed to start audio player: %s", exc)
            self._process = None
            self._gap_timer.start(0)
            return

        self._poll_timer.start()
