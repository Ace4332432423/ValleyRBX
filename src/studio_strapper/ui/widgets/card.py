"""
Reusable Card widget for Studio Strapper panels.
"""

from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class Card(QFrame):
    """Sleek styled Card widget with title, description, and custom content layout."""

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("class", "Card")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)

        if title:
            self.title_label = QLabel(title, self)
            self.title_label.setProperty("class", "CardTitle")
            self.main_layout.addWidget(self.title_label)

        if subtitle:
            self.subtitle_label = QLabel(subtitle, self)
            self.subtitle_label.setProperty("class", "CardSubtitle")
            self.subtitle_label.setWordWrap(True)
            self.main_layout.addWidget(self.subtitle_label)

    def add_widget(self, widget: QWidget) -> None:
        self.main_layout.addWidget(widget)

    def add_layout(self, layout) -> None:
        self.main_layout.addLayout(layout)
