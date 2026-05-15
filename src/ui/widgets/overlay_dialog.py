from __future__ import annotations

"""Базовый диалог с затемняющим оверлеем поверх родительского окна."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
)


class OverlayDialog(QDialog):
    """Фреймлес-диалог с затемнением и карточкой по центру."""

    def __init__(self, parent: QWidget, *, title: str) -> None:
        super().__init__(parent)

        # === Окно диалога ===
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        # === Оверлей (затемнение) ===
        self._overlay = QWidget(parent)
        self._overlay.setObjectName("Overlay")
        # self._overlay.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        # self._overlay.setAttribute(Qt.WA_StyledBackground, True)

        # === Карточка ===
        self._card = QFrame(self)
        self._card.setObjectName("DialogCard")
        # self._card.setStyleSheet("""
        # QFrame#DialogCard {
        #     background: rgba(30, 30, 30, 0.95);
        #     border-radius: 14px;
        #     border: 1px solid rgba(255,255,255,0.06);
        # }
        # """)

        # Тень
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(Qt.black)
        self._card.setGraphicsEffect(shadow)

        # корневой слой
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.addWidget(self._card)

        # слой карточки
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        self._title = QLabel(title, self._card)
        self._title.setObjectName("DialogTitle")
        self._title.setStyleSheet("""
        QLabel#DialogTitle {
            font-size: 16px;
            font-weight: 800;
        }
        """)
        header.addWidget(self._title)
        header.addStretch(1)

        close = QPushButton("✕", self._card)
        close.setFixedSize(32, 32)
        close.clicked.connect(self.reject)
        close.setObjectName("CloseButton")
        close.setStyleSheet("""
        QPushButton#CloseButton {
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(0,0,0,0.10);
            border-radius: 6px;
            font-weight: 800;
        }
        QPushButton#CloseButton:hover {
            background: #F47174;
        }
        """)
        header.addWidget(close)

        card_layout.addLayout(header)

        # Тело
        self.body = QVBoxLayout()
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(10)
        card_layout.addLayout(self.body)

        # Footer
        self.footer = QHBoxLayout()
        self.footer.setContentsMargins(0, 8, 0, 0)
        self.footer.setSpacing(10)
        card_layout.addLayout(self.footer)

        self.setMinimumWidth(520)

    def exec(self) -> int:  # type: ignore[override]
        """Показ с затемнением."""
        p = self.parentWidget()
        if p is not None:
            self._overlay.setGeometry(p.rect())
            self._overlay.show()
            self._overlay.raise_()

            self.raise_()
            self.activateWindow()
            self._center_in_parent()

        try:
            return super().exec()
        finally:
            self._overlay.hide()  # НЕ удаляем

    def _center_in_parent(self) -> None:
        p = self.parentWidget()
        if p is None:
            return

        self.adjustSize()
        parent_top_left = p.mapToGlobal(p.rect().topLeft())
        x = parent_top_left.x() + (p.width() - self.width()) // 2
        y = parent_top_left.y() + (p.height() - self.height()) // 2
        self.move(x, y)

    def mousePressEvent(self, event):
        """Закрытие при клике вне карточки."""
        if not self._card.geometry().contains(event.pos()):
            self.reject()
        super().mousePressEvent(event)
