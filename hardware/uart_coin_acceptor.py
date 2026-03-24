"""UART coin acceptor reader for frames formatted as 0x48 0x58 XX."""
from __future__ import annotations

import logging
from typing import Callable

from PyQt5.QtCore import QObject, QTimer

logger = logging.getLogger(__name__)

try:
    import serial
except Exception:  # pragma: no cover - optional on non-device environments
    serial = None


class UARTCoinAcceptor(QObject):
    def __init__(
        self,
        on_coin: Callable[[int], None],
        *,
        port: str,
        baudrate: int = 115200,
        poll_ms: int = 50,
        parent=None,
    ):
        super().__init__(parent)
        self.on_coin = on_coin
        self.port = port
        self.baudrate = baudrate
        self.poll_ms = poll_ms
        self.buffer = bytearray()
        self.ser = None

        self._timer = QTimer(self)
        self._timer.setInterval(self.poll_ms)
        self._timer.timeout.connect(self._poll_serial)

        self._open_serial()
        self._timer.start()

    def _open_serial(self):
        if serial is None:
            logger.warning("pyserial unavailable. UART coin acceptor disabled.")
            return
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1,
            )
        except Exception:
            logger.exception("Failed to open UART coin acceptor on %s", self.port)
            self.ser = None

    def shutdown(self):
        self._timer.stop()
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception:
                logger.exception("Failed to close UART coin acceptor cleanly")

    def _poll_serial(self):
        if self.ser is None:
            return
        try:
            available = self.ser.in_waiting
            if available <= 0:
                return
            data = self.ser.read(available)
        except Exception:
            logger.exception("UART coin acceptor read failed")
            return
        if not data:
            return
        self.buffer.extend(data)
        self._process_buffer()

    def _process_buffer(self):
        while len(self.buffer) >= 3:
            if self.buffer[0] != 0x48:
                del self.buffer[0]
                continue
            if self.buffer[1] != 0x58:
                del self.buffer[0]
                continue
            value = int(self.buffer[2])
            del self.buffer[:3]
            print(f"Moneda detectada: {value}")
            self.on_coin(value)
