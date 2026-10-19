"""
Circular Icon Widget for ValleyRBX.
Masks any source image into a smooth, antialiased circle with a specular border rim.
"""

from __future__ import annotations
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QWidget


class CircularIcon(QLabel):
    """Circular masked icon with a delicate glass specular highlight ring."""

    def __init__(self, image_path: str, size: int = 28, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.image_path = image_path
        self.icon_size = size
        self.setFixedSize(size, size)
        self.setScaledContents(False)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        s = float(self.icon_size)
        rect = QRectF(0.5, 0.5, s - 1.0, s - 1.0)

        path = QPainterPath()
        path.addEllipse(rect)

        # Draw source image clipped to circle
        if Path(self.image_path).exists():
            src_pix = QPixmap(self.image_path)
            if not src_pix.isNull():
                scaled = src_pix.scaled(
                    int(s),
                    int(s),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                painter.save()
                painter.setClipPath(path)
                x_off = (s - scaled.width()) / 2.0
                y_off = (s - scaled.height()) / 2.0
                painter.drawPixmap(int(x_off), int(y_off), scaled)
                painter.restore()
        else:
            # Fallback gradient
            bg_grad = QLinearGradient(0, 0, s, s)
            bg_grad.setColorAt(0.0, QColor(2, 132, 199))
            bg_grad.setColorAt(1.0, QColor(37, 99, 235))
            painter.fillPath(path, QBrush(bg_grad))

        # Specular Outer Border Rim (Light on top, sapphire on bottom)
        rim_grad = QLinearGradient(0, 0, 0, s)
        rim_grad.setColorAt(0.0, QColor(255, 255, 255, 200))
        rim_grad.setColorAt(0.5, QColor(56, 189, 248, 80))
        rim_grad.setColorAt(1.0, QColor(0, 0, 0, 90))

        painter.setPen(QPen(QBrush(rim_grad), 1.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)

        painter.end()
