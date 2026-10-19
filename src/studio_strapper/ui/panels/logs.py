"""
Logs & Diagnostics Panel for Studio Strapper.
Displays live streaming console logs and CachyOS system audit results.
"""

from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from studio_strapper.core.diagnostics import SystemAuditor
from studio_strapper.ui.widgets.card import Card
from studio_strapper.ui.widgets.status_badge import StatusBadge


class LogsPanel(QWidget):
    """Panel for real-time process log output and CachyOS system audit."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.auditor = SystemAuditor()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 1. Console Output Card
        console_card = Card("Execution Console", "Real-time stdout / stderr stream from Roblox Studio & Wine")
        console_layout = QVBoxLayout()

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(240)
        console_layout.addWidget(self.console)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_clear = QPushButton("🗑️ Clear Console")
        btn_clear.clicked.connect(self.console.clear)
        btn_row.addWidget(btn_clear)

        btn_copy = QPushButton("📋 Copy to Clipboard")
        btn_copy.clicked.connect(self._copy_to_clipboard)
        btn_row.addWidget(btn_copy)

        btn_row.addStretch()

        btn_audit = QPushButton("🔍 Run CachyOS Audit")
        btn_audit.clicked.connect(self.run_audit)
        btn_row.addWidget(btn_audit)

        console_layout.addLayout(btn_row)
        console_card.add_layout(console_layout)
        layout.addWidget(console_card)

        # 2. Audit Results Card
        self.audit_card = Card("CachyOS Platform Audit", "Hardware, multilib, and scheduler compatibility inspection")
        self.audit_layout = QVBoxLayout()
        self.audit_card.add_layout(self.audit_layout)
        layout.addWidget(self.audit_card)

        layout.addStretch()

        # Run initial audit
        self.run_audit()

    def append_log(self, text: str) -> None:
        """Append log line and autoscroll to bottom."""
        self.console.appendPlainText(text)
        self.console.moveCursor(QTextCursor.MoveOperation.End)

    def _copy_to_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        clipboard.setText(self.console.toPlainText())

    def run_audit(self) -> None:
        # Clear existing items in audit layout
        while self.audit_layout.count():
            item = self.audit_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear nested layout
                pass

        results = self.auditor.run_full_audit()
        for res in results:
            row = QHBoxLayout()
            badge = StatusBadge(res["title"], res["status"])
            badge.setMinimumWidth(220)
            row.addWidget(badge)

            detail_lbl = QLabel(res["details"])
            detail_lbl.setWordWrap(True)
            detail_lbl.setStyleSheet("color: #cdd6f4; font-size: 12px;")
            row.addWidget(detail_lbl)
            row.addStretch()

            self.audit_layout.addLayout(row)

            if res.get("fix"):
                fix_lbl = QLabel(f"↳ Fix: {res['fix']}")
                fix_lbl.setStyleSheet("color: #f9e2af; font-size: 11px; margin-left: 24px;")
                self.audit_layout.addWidget(fix_lbl)
