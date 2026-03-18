from __future__ import annotations

"""Базовый диалог с затемняющим оверлеем поверх родительского окна."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class OverlayDialog(QDialog):
    """Фреймлес-диалог, центрированный над окном с полупрозрачным фоном."""

    def __init__(self, parent: QWidget, *, title: str) -> None:
        """Создаёт диалог с общим каркасом: заголовок, кнопка закрытия, body и footer."""
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)

        self._overlay = QWidget(parent)
        self._overlay.setObjectName("Overlay")
        self._overlay.hide()

        self._card = QFrame(self)
        self._card.setObjectName("DialogCard")
        # Styling for overlay/card is provided by app-wide QSS to match current theme.

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.addWidget(self._card)

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self._title = QLabel(title, self._card)
        self._title.setObjectName("DialogTitle")
        self._title.setStyleSheet("QLabel#DialogTitle { font-size: 16px; font-weight: 800; }")
        header.addWidget(self._title)
        header.addStretch(1)

        close = QPushButton("✕", self._card)
        close.setFixedSize(34, 34)
        close.clicked.connect(self.reject)
        close.setObjectName("CloseButton")
        close.setStyleSheet(
            """
            QPushButton#CloseButton {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 10px;
                padding: 0px;
                font-weight: 700;
            }
            QPushButton#CloseButton:hover { background: rgba(255,255,255,0.10); }
            """
        )
        header.addWidget(close)

        card_layout.addLayout(header)

        self.body = QVBoxLayout()
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(10)
        card_layout.addLayout(self.body)

        self.footer = QHBoxLayout()
        self.footer.setContentsMargins(0, 8, 0, 0)
        self.footer.setSpacing(10)
        card_layout.addLayout(self.footer)

        self.setMinimumWidth(520)

    def exec(self) -> int:  # type: ignore[override]
        """Показывает оверлей, центрирует диалог и запускает модальное окно."""
        p = self.parentWidget()
        if p is not None:
            self._overlay.setGeometry(p.rect())
            self._overlay.show()
            self._overlay.raise_()
            self.raise_()
            self._center_in_parent()
        try:
            return super().exec()
        finally:
            self._overlay.hide()
            self._overlay.deleteLater()

    def _center_in_parent(self) -> None:
        """Вычисляет координаты и перемещает диалог в центр родительского окна."""
        p = self.parentWidget()
        if p is None:
            return
        self.adjustSize()
        x = (p.width() - self.width()) // 2
        y = (p.height() - self.height()) // 2
        self.move(max(0, x), max(0, y))

