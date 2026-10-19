"""
Reflective Pill Button with realistic glass specular highlights and animated breathing glow.
"""

from __future__ import annotations
from PySide6.QtCore import Property, QEasingCurve, QPoint, QPropertyAnimation, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QPushButton, QWidget


class ReflectivePillButton(QPushButton):
    """
    Luxury cinematic pill button with authentic 3D glass reflections,
    metallic sheen, and an animated breathing ambient glow.
    """

    def __init__(
        self,
        text: str = "Run Studio",
        parent: QWidget | None = None,
        gold_theme: bool = True,
    ) -> None:
        super().__init__(text, parent)
        self.gold_theme = gold_theme
        self._glow_intensity = 0.5
        self._hover_progress = 0.0
        self._pressed = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        self.setMinimumWidth(180)

        font = self.font()
        font.setPointSize(12)
        font.setBold(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.8)
        self.setFont(font)

        # Breathing glow animation timer
        self._glow_timer = QTimer(self)
        self._glow_timer.timeout.connect(self._pulse_glow)
        self._glow_delta = 0.02
        self._glow_timer.start(35)

    def _pulse_glow(self) -> None:
        self._glow_intensity += self._glow_delta
        if self._glow_intensity >= 1.0:
            self._glow_intensity = 1.0
            self._glow_delta = -0.025
        elif self._glow_intensity <= 0.35:
            self._glow_intensity = 0.35
            self._glow_delta = 0.025
        self.update()

    def enterEvent(self, event) -> None:
        self._hover_progress = 1.0
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover_progress = 0.0
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())
        radius = h / 2.0

        # Draw outer ambient breathing bloom glow
        glow_alpha = int(40 + (50 * self._glow_intensity) + (40 * self._hover_progress))
        if self.gold_theme:
            glow_color = QColor(245, 158, 11, glow_alpha)  # Amber
        else:
            glow_color = QColor(139, 92, 246, glow_alpha)  # Violet

        glow_rect = QRectF(4, 4, w - 8, h - 8)
        glow_path = QPainterPath()
        glow_path.addRoundedRect(glow_rect, radius, radius)

        # 1. Base Gradient (Lacquered metallic finish)
        base_grad = QLinearGradient(0, 0, 0, h)
        if self.gold_theme:
            if self._pressed:
                base_grad.setColorAt(0.0, QColor(217, 119, 6))   # Amber-600
                base_grad.setColorAt(1.0, QColor(180, 83, 9))    # Amber-700
            elif self._hover_progress > 0:
                base_grad.setColorAt(0.0, QColor(253, 224, 71))  # Yellow-300
                base_grad.setColorAt(0.5, QColor(245, 158, 11))  # Amber-500
                base_grad.setColorAt(1.0, QColor(217, 119, 6))   # Amber-600
            else:
                base_grad.setColorAt(0.0, QColor(251, 191, 36))  # Amber-400
                base_grad.setColorAt(0.6, QColor(245, 158, 11))  # Amber-500
                base_grad.setColorAt(1.0, QColor(180, 83, 9))    # Amber-700
        else:
            base_grad.setColorAt(0.0, QColor(168, 85, 247))
            base_grad.setColorAt(1.0, QColor(99, 102, 241))

        btn_rect = QRectF(1.5, 1.5, w - 3, h - 3)
        btn_path = QPainterPath()
        btn_path.addRoundedRect(btn_rect, radius - 1.5, radius - 1.5)

        painter.fillPath(btn_path, QBrush(base_grad))

        # 2. Specular Top Glass Reflection
        # Mimics light reflecting on a rounded curved glass surface
        refl_h = (h / 2.0) - 1.0
        refl_rect = QRectF(3.0, 2.5, w - 6, refl_h)
        refl_path = QPainterPath()
        refl_path.addRoundedRect(refl_rect, radius - 2, radius - 2)

        refl_grad = QLinearGradient(0, 2, 0, refl_h)
        refl_grad.setColorAt(0.0, QColor(255, 255, 255, 180))
        refl_grad.setColorAt(0.3, QColor(255, 255, 255, 90))
        refl_grad.setColorAt(0.85, QColor(255, 255, 255, 15))
        refl_grad.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.fillPath(refl_path, QBrush(refl_grad))

        # 3. Bottom Inner Rim Shadow
        bottom_h = 5.0
        bottom_rect = QRectF(4.0, h - bottom_h - 2.5, w - 8, bottom_h)
        bottom_path = QPainterPath()
        bottom_path.addRoundedRect(bottom_rect, 2.5, 2.5)
        bottom_grad = QLinearGradient(0, h - bottom_h - 2.5, 0, h - 2.5)
        bottom_grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        bottom_grad.setColorAt(1.0, QColor(0, 0, 0, 60))
        painter.fillPath(bottom_path, QBrush(bottom_grad))

        # 4. Crisp Border Highlight (White on top, dark on bottom for 3D bevel)
        border_grad = QLinearGradient(0, 0, 0, h)
        border_grad.setColorAt(0.0, QColor(255, 255, 255, 220))
        border_grad.setColorAt(0.4, QColor(255, 255, 255, 80))
        border_grad.setColorAt(1.0, QColor(120, 53, 15, 180))

        painter.setPen(QPen(QBrush(border_grad), 1.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(btn_rect, radius - 1.5, radius - 1.5)

        # 5. Text & Play Icon
        text_color = QColor(17, 24, 39) if self.gold_theme else QColor(255, 255, 255)
        painter.setPen(text_color)
        painter.setFont(self.font())

        content_rect = self.rect()
        if self._pressed:
            content_rect.adjust(0, 1, 0, 1)

        painter.drawText(content_rect, Qt.AlignmentFlag.AlignCenter, f"▶  {self.text()}")
        painter.end()


class ReflectiveCircleButton(QPushButton):
    """Circular icon button with glass specular reflection (e.g. for ⋮ menu)."""

    def __init__(self, text: str = "⋮", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setFixedSize(46, 46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hover = False
        self._pressed = False

        font = self.font()
        font.setPointSize(16)
        font.setBold(True)
        self.setFont(font)

    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        radius = h / 2.0

        # Base circle
        btn_rect = QRectF(2, 2, w - 4, h - 4)
        base_grad = QLinearGradient(0, 0, 0, h)
        if self._pressed:
            base_grad.setColorAt(0.0, QColor(20, 24, 44))
            base_grad.setColorAt(1.0, QColor(10, 12, 24))
        elif self._hover:
            base_grad.setColorAt(0.0, QColor(45, 52, 85))
            base_grad.setColorAt(1.0, QColor(25, 29, 52))
        else:
            base_grad.setColorAt(0.0, QColor(32, 38, 64))
            base_grad.setColorAt(1.0, QColor(18, 22, 40))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(base_grad))
        painter.drawEllipse(btn_rect)

        # Specular reflection (upper arc)
        refl_rect = QRectF(4, 3, w - 8, (h / 2.0) - 2)
        refl_grad = QLinearGradient(0, 3, 0, h / 2.0)
        refl_grad.setColorAt(0.0, QColor(255, 255, 255, 100))
        refl_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(refl_grad))
        painter.drawEllipse(refl_rect)

        # Border
        border_color = QColor(255, 255, 255, 60 if self._hover else 25)
        painter.setPen(QPen(border_color, 1.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(btn_rect)

        # Icon text
        painter.setPen(QColor(226, 232, 240))
        painter.setFont(self.font())
        content_rect = self.rect()
        if self._pressed:
            content_rect.adjust(0, 1, 0, 1)
        painter.drawText(content_rect, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()
