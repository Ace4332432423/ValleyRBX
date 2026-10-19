"""
Status badge widget for Studio Strapper.
"""

from __future__ import annotations
from PySide6.QtWidgets import QLabel, QWidget


class StatusBadge(QLabel):
    """Pill-shaped status badge with semantic coloring."""

    def __init__(self, text: str, status: str = "ok", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.set_status(status, text)

    def set_status(self, status: str, text: str = "") -> None:
        if text:
            self.setText(text)

        class_map = {
            "ok": "BadgeOk",
            "warning": "BadgeWarn",
            "warn": "BadgeWarn",
            "error": "BadgeError",
            "info": "BadgeInfo",
        }
        self.setProperty("class", class_map.get(status.lower(), "BadgeInfo"))
        self.style().unpolish(self)
        self.style().polish(self)
