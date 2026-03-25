"""Audit mode screen for operational and sales review."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout

from ui.payment_screen import BrandedScreen


class AuditScreen(BrandedScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.setObjectName("auditScreen")
        self._build_ui()

    def _build_ui(self):
        self.title = QLabel("Auditoría")
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet("font-size:18px; font-weight:700; color:#64748b;")

        self.filter_label = QLabel("")
        self.filter_label.setAlignment(Qt.AlignCenter)
        self.filter_label.setWordWrap(True)
        self.filter_label.setStyleSheet("font-size:16px; font-weight:700; color:#ec4899;")

        self.summary = QLabel("")
        self.summary.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet("font-size:18px; font-weight:600; color:#111827;")

        self.table = QTableWidget(0, 0)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(
            """
            QTableWidget {
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 14px;
                gridline-color: #e2e8f0;
                font-size: 16px;
                color: #111827;
            }
            QHeaderView::section {
                background: #f1f5f9;
                color: #111827;
                font-size: 16px;
                font-weight: 700;
                border: 0;
                border-bottom: 2px solid #e2e8f0;
                padding: 8px;
            }
            """
        )

        self.footer = QLabel("P1/P2: navegar  P3: sección  OK: reiniciar filtro  Cancelar: salir")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setWordWrap(True)
        self.footer.setStyleSheet("font-size:16px; font-weight:700; color:#64748b;")

        self.content_layout.addWidget(self.title)
        self.content_layout.addSpacing(4)
        self.content_layout.addWidget(self.subtitle)
        self.content_layout.addSpacing(4)
        self.content_layout.addWidget(self.filter_label)
        self.content_layout.addSpacing(12)
        self.content_layout.addWidget(self.summary)
        self.content_layout.addSpacing(12)
        self.content_layout.addWidget(self.table, 1)
        self.content_layout.addSpacing(10)
        self.content_layout.addWidget(self.footer)

    def set_view(
        self,
        *,
        title: str,
        subtitle: str,
        filter_text: str,
        summary_lines: list[str],
        headers: list[str],
        rows: list[list[str]],
    ):
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.filter_label.setText(filter_text)
        self.summary.setText("\n".join(summary_lines))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter if col_index > 0 else Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row_index, col_index, item)
