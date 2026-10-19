"""
Preference Group and Row widgets matching Vinegar's layout with cinematic glass reflections.
"""

from __future__ import annotations
from typing import Optional

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class PreferenceRow(QWidget):
    """
    A single setting row with title, description, control on right,
    and optional expandable drawer for detailed configuration.
    """

    clicked = Signal()

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        right_widget: QWidget | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self._hover = False
        self._expanded = False
        self._expandable_widget: Optional[QWidget] = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(18, 14, 18, 14)
        self.main_layout.setSpacing(0)

        # Header Row
        self.row_widget = QWidget(self)
        row_layout = QHBoxLayout(self.row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(14)

        # Text labels
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        self.lbl_title = QLabel(title, self.row_widget)
        self.lbl_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #f8fafc;")

        self.lbl_sub = QLabel(subtitle, self.row_widget)
        self.lbl_sub.setStyleSheet("font-size: 12px; color: #94a3b8;")
        self.lbl_sub.setWordWrap(True)

        text_layout.addWidget(self.lbl_title)
        if subtitle:
            text_layout.addWidget(self.lbl_sub)

        row_layout.addLayout(text_layout)
        row_layout.addStretch()

        if right_widget:
            row_layout.addWidget(right_widget)

        self.main_layout.addWidget(self.row_widget)

    def set_subtitle(self, text: str) -> None:
        """Dynamically updates the subtitle text."""
        self.lbl_sub.setText(text)
        self.lbl_sub.setVisible(bool(text))

    def set_expandable_content(self, widget: QWidget) -> None:
        """Attaches an expandable drawer below this row."""
        self._expandable_widget = widget
        self._expandable_widget.setVisible(False)
        self.main_layout.addWidget(self._expandable_widget)

    def toggle_expand(self) -> None:
        if self._expandable_widget:
            self._expanded = not self._expanded
            self._expandable_widget.setVisible(self._expanded)
            self.update()

    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Subtle row hover lighting
        if self._hover:
            hover_color = QColor(255, 255, 255, 8)
            painter.fillRect(self.rect(), hover_color)

        painter.end()


class PreferenceGroup(QFrame):
    """
    Rounded container card grouping multiple PreferenceRows.
    Decorated with glass specular top rim and frosted obsidian styling.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.group_layout = QVBoxLayout(self)
        self.group_layout.setContentsMargins(0, 4, 0, 4)
        self.group_layout.setSpacing(0)

    def add_row(self, row: PreferenceRow) -> None:
        # If not the first row, add a subtle divider line
        if self.group_layout.count() > 0:
            divider = QFrame(self)
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setFixedHeight(1)
            divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.06); border: none;")
            self.group_layout.addWidget(divider)

        self.group_layout.addWidget(row)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        radius = 16.0
        rect = QRectF(1, 1, w - 2, h - 2)

        # 1. Glassmorphic Background: Frosted Navy Glass
        bg_grad = QLinearGradient(0, 0, 0, h)
        bg_grad.setColorAt(0.0, QColor(14, 26, 52, 220))
        bg_grad.setColorAt(1.0, QColor(9, 17, 36, 235))

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.fillPath(path, QBrush(bg_grad))

        # 2. Specular Top Rim Reflection
        rim_grad = QLinearGradient(0, 0, w, 0)
        rim_grad.setColorAt(0.0, QColor(56, 189, 248, 55))
        rim_grad.setColorAt(0.3, QColor(255, 255, 255, 95))
        rim_grad.setColorAt(0.7, QColor(255, 255, 255, 95))
        rim_grad.setColorAt(1.0, QColor(37, 99, 235, 55))

        rim_pen = QPen(QBrush(rim_grad), 1.2)
        painter.setPen(rim_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, radius, radius)

        painter.end()


class SectionHeader(QWidget):
    """Clean section title with optional right action icon (like 'Components ⚙')."""

    action_clicked = Signal()

    def __init__(self, title: str, action_icon: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 16, 4, 8)
        layout.setSpacing(8)

        lbl = QLabel(title, self)
        lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #cbd5e1; letter-spacing: 0.5px;")
        layout.addWidget(lbl)
        layout.addStretch()

        if action_icon:
            btn = QPushButton(action_icon, self)
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #94a3b8;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.08);
                    color: #ffffff;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(self.action_clicked.emit)
            layout.addWidget(btn)
