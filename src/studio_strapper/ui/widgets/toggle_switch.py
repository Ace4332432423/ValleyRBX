"""
Cinematic animated toggle switch widget for PySide6 with smooth easing animations.
"""

from __future__ import annotations
from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath
from PySide6.QtWidgets import QWidget


class ToggleSwitch(QWidget):
    """Sleek, fluidly animated toggle switch with glowing gradients."""

    toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None, checked: bool = False) -> None:
        super().__init__(parent)
        self._checked = checked
        self._thumb_position = 1.0 if checked else 0.0
        self.setFixedSize(52, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim = QPropertyAnimation(self, b"thumb_position", self)
        self._anim.setDuration(240)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def get_thumb_position(self) -> float:
        return self._thumb_position

    def set_thumb_position(self, pos: float) -> None:
        self._thumb_position = pos
        self.update()

    thumb_position = Property(float, get_thumb_position, set_thumb_position)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool, animate: bool = True) -> None:
        if self._checked != checked:
            self._checked = checked
            target = 1.0 if checked else 0.0
            if animate:
                self._anim.stop()
                self._anim.setStartValue(self._thumb_position)
                self._anim.setEndValue(target)
                self._anim.start()
            else:
                self._thumb_position = target
                self.update()
            self.toggled.emit(self._checked)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        track_rect = QRectF(0, 0, self.width(), self.height())
        radius = track_rect.height() / 2

        # Draw track background with dynamic glow gradient
        if self._thumb_position > 0.01:
            grad = QLinearGradient(0, 0, self.width(), self.height())
            grad.setColorAt(0.0, QColor(99, 102, 241, int(255 * self._thumb_position)))   # Indigo
            grad.setColorAt(1.0, QColor(168, 85, 247, int(255 * self._thumb_position)))   # Purple
            
            # Blend with off track base
            base_color = QColor(24, 26, 44)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(base_color))
            painter.drawRoundedRect(track_rect, radius, radius)

            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(track_rect, radius, radius)
        else:
            base_color = QColor(24, 26, 44)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(base_color))
            painter.drawRoundedRect(track_rect, radius, radius)

        # Subtle border
        border_color = QColor(80, 85, 120, 160) if self._checked else QColor(45, 48, 75, 180)
        painter.setPen(border_color)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(track_rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        # Thumb
        thumb_diameter = self.height() - 6
        x_min = 3.0
        x_max = self.width() - thumb_diameter - 3.0
        x_pos = x_min + (x_max - x_min) * self._thumb_position
        thumb_rect = QRectF(x_pos, 3.0, thumb_diameter, thumb_diameter)

        # Thumb gradient (pearlescent glow)
        thumb_grad = QLinearGradient(thumb_rect.topLeft(), thumb_rect.bottomRight())
        if self._checked:
            thumb_grad.setColorAt(0.0, QColor(255, 255, 255))
            thumb_grad.setColorAt(1.0, QColor(230, 235, 255))
        else:
            thumb_grad.setColorAt(0.0, QColor(160, 165, 195))
            thumb_grad.setColorAt(1.0, QColor(115, 120, 150))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(thumb_grad))
        painter.drawEllipse(thumb_rect)

        painter.end()
