from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsColorizeEffect, QWidget

from src.ui.styles.app import ThemeTokens


class HoverEffect:
    def __init__(
        self,
        widget: QWidget,
        tokens: ThemeTokens,
        strength=1.5,
        anim_duration=1500,
    ):
        self.widget = widget
        self._effect = QGraphicsColorizeEffect(widget)
        self._effect.setColor(QColor(tokens.accent))
        self._effect.setStrength(0)
        widget.setGraphicsEffect(self._effect)

        self._anim = QPropertyAnimation(self._effect, b"strength")
        self._anim.setEasingCurve(QEasingCurve.Type.OutQuint)
        self._anim.setDuration(anim_duration)
        self.strength = strength

        # Переопределяем события наведения
        widget.enterEvent = self.enterEvent
        widget.leaveEvent = self.leaveEvent

    def set_tokens(self, tokens: ThemeTokens) -> None:
        self._effect.setColor(QColor(tokens.accent))

    def enterEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._effect.strength())
        self._anim.setEndValue(self.strength)
        self._anim.start()
        super(self.widget.__class__, self.widget).enterEvent(event)

    def leaveEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._effect.strength())
        self._anim.setEndValue(0)
        self._anim.start()
        super(self.widget.__class__, self.widget).leaveEvent(event)
