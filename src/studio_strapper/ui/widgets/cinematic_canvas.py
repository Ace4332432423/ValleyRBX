"""
Cinematic Canvas widget providing atmospheric background lighting and glowing nebula blooms.
"""

from __future__ import annotations
import math
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget


class CinematicCanvas(QWidget):
    """
    Atmospheric background canvas featuring a deep cosmic gradient,
    an ambient radial bloom spotlight behind the hero button, and subtle animated lighting.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._glow_phase = 0.0

        # Slow ambient breathing pulse for the background bloom
        self._ambient_timer = QTimer(self)
        self._ambient_timer.timeout.connect(self._tick_ambient)
        self._ambient_timer.start(45)

    def _tick_ambient(self) -> None:
        self._glow_phase += 0.035
        if self._glow_phase > 2 * math.pi:
            self._glow_phase = 0.0
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 1. Base Rich Navy Blue Gradient
        bg_grad = QLinearGradient(0, 0, 0, h)
        bg_grad.setColorAt(0.0, QColor(10, 25, 48))    # Midnight Navy
        bg_grad.setColorAt(0.4, QColor(12, 32, 64))    # Deep Navy Blue
        bg_grad.setColorAt(1.0, QColor(5, 12, 26))     # Dark Abyss Navy
        painter.fillRect(self.rect(), bg_grad)

        # 2. Ambient Radial Bloom Spotlight (Centered behind Run Studio hero button)
        pulse = (math.sin(self._glow_phase) + 1.0) / 2.0  # 0.0 to 1.0
        bloom_cx = w / 2.0
        bloom_cy = 130.0
        bloom_radius = 290.0 + (30.0 * pulse)

        bloom_grad = QRadialGradient(QPointF(bloom_cx, bloom_cy), bloom_radius)
        # Deep sapphire and subtle cyan electric ambient glow
        bloom_grad.setColorAt(0.0, QColor(37, 99, 235, int(35 + 15 * pulse)))
        bloom_grad.setColorAt(0.4, QColor(2, 132, 199, int(20 + 10 * pulse)))
        bloom_grad.setColorAt(0.75, QColor(15, 23, 42, int(15 + 5 * pulse)))
        bloom_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bloom_grad))
        painter.drawEllipse(QPointF(bloom_cx, bloom_cy), bloom_radius, bloom_radius * 0.75)

        # 3. Soft Vignette around Window Edges
        vignette_grad = QLinearGradient(0, 0, w, 0)
        vignette_grad.setColorAt(0.0, QColor(0, 0, 0, 90))
        vignette_grad.setColorAt(0.08, QColor(0, 0, 0, 0))
        vignette_grad.setColorAt(0.92, QColor(0, 0, 0, 0))
        vignette_grad.setColorAt(1.0, QColor(0, 0, 0, 90))
        painter.fillRect(self.rect(), vignette_grad)

        painter.end()
