from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QScrollArea


class SmoothScrollArea(QScrollArea):
    def __init__(self) -> None:
        super().__init__()

        self._anim = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._anim.setDuration(400)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def wheelEvent(self, event) -> None:  # noqa: N802
        scrollbar = self.verticalScrollBar()
        delta = event.angleDelta().y()
        new_value = scrollbar.value() - delta
        new_value = max(scrollbar.minimum(), min(scrollbar.maximum(), new_value))

        self._anim.stop()
        self._anim.setStartValue(scrollbar.value())
        self._anim.setEndValue(new_value)
        self._anim.start()
