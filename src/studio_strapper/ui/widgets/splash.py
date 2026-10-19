"""
Cinematic Frameless Splash Window for ValleyRBX Direct Launch mode.
"""

from __future__ import annotations
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

ICON_PATH = "/home/ace/Downloads/2026_10_04_0jq_Kleki.png"


class CinematicSplash(QWidget):
    """Breathtaking glassmorphic splash window shown during direct launch."""

    launch_finished = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(560, 320)

        # Center on screen
        screen = self.screen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(16)

        # Top Header: Logo + Title
        top_layout = QHBoxLayout()
        top_layout.setSpacing(18)

        # App Icon
        self.logo_label = QLabel(self)
        if Path(ICON_PATH).exists():
            pix = QPixmap(ICON_PATH).scaled(68, 68, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pix)
        else:
            self.logo_label.setText("🎮")
            self.logo_label.setStyleSheet("font-size: 40px;")
        top_layout.addWidget(self.logo_label)

        # Titles
        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        title = QLabel("VALLEY RBX", self)
        title.setStyleSheet("font-size: 24px; font-weight: 900; letter-spacing: 2px; color: #ffffff;")
        
        subtitle = QLabel("IGNITING ROBLOX STUDIO RUNTIME", self)
        subtitle.setStyleSheet("font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #c084fc;")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        top_layout.addLayout(title_box)
        top_layout.addStretch()

        layout.addLayout(top_layout)
        layout.addStretch()

        # Status text
        self.status_lbl = QLabel("Initializing Kombucha Wine sandbox...", self)
        self.status_lbl.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 500;")
        layout.addWidget(self.status_lbl)

        # Glowing Progress Bar
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(10)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:0.5 #a855f7, stop:1 #ec4899);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress)

        # Footer notes
        footer = QLabel("CachyOS Kernel • Vinegar Kombucha Wine Handler • FastFlags Injected", self)
        footer.setStyleSheet("color: #64748b; font-size: 10px; letter-spacing: 0.5px;")
        layout.addWidget(footer)

    def set_status(self, text: str, progress: int = 50) -> None:
        self.status_lbl.setText(text)
        self.progress.setValue(progress)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0, 0, self.width(), self.height())
        radius = 24.0

        # Background Gradient: Obsidian to Cosmic Deep Violet
        bg_grad = QLinearGradient(0, 0, self.width(), self.height())
        bg_grad.setColorAt(0.0, QColor(14, 17, 36, 245))
        bg_grad.setColorAt(0.5, QColor(9, 11, 22, 250))
        bg_grad.setColorAt(1.0, QColor(24, 12, 40, 245))

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.fillPath(path, QBrush(bg_grad))

        # Ambient Glow Border
        border_grad = QLinearGradient(0, 0, self.width(), self.height())
        border_grad.setColorAt(0.0, QColor(168, 85, 247, 180))
        border_grad.setColorAt(0.5, QColor(99, 102, 241, 100))
        border_grad.setColorAt(1.0, QColor(236, 72, 153, 160))

        painter.setPen(border_grad)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), radius, radius)

        painter.end()
