from __future__ import annotations

"""Диалог создания новой категории задач."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QColorDialog,
)

from src.ui.widgets.overlay_dialog import OverlayDialog


class CreateCategoryDialog(OverlayDialog):
    """Диалог «Создание категории» с выбором цвета и иконки."""

    def __init__(self, parent) -> None:
        """Создаёт поля ввода названия, цвета и загрузки иконки."""
        super().__init__(parent, title="Создание категории")
        self._icon_path: Optional[Path] = None
        self._color = "#6D5EF6"

        self._name = QLineEdit(self)
        self._name.setPlaceholderText("Введите название…")

        self._accent_btn = QPushButton("", self)
        self._accent_btn.setFixedSize(34, 34)
        self._accent_btn.setCursor(Qt.PointingHandCursor)
        self._accent_btn.clicked.connect(self._pick_color)
        self._accent_btn.setObjectName("AccentPreview")
        self._set_color_preview()

        icon_row = QHBoxLayout()
        self._icon_lbl = QLabel("Файл не выбран", self)
        self._icon_btn = QPushButton("Загрузить файл", self)
        self._icon_btn.clicked.connect(self._pick_icon)
        icon_row.addWidget(self._icon_lbl, 1)
        icon_row.addWidget(self._icon_btn)

        self.body.addWidget(QLabel("Название категории", self))
        self.body.addWidget(self._name)
        self.body.addSpacing(6)
        self.body.addWidget(QLabel("Акцентный цвет", self))
        self.body.addWidget(self._accent_btn)
        self.body.addSpacing(6)
        self.body.addWidget(QLabel("Иконка категории", self))
        self.body.addLayout(icon_row)

        create = QPushButton("Создать", self)
        create.setObjectName("PrimaryButton")
        create.clicked.connect(self.accept)
        cancel = QPushButton("Отменить", self)
        cancel.clicked.connect(self.reject)

        self.footer.addStretch(1)
        self.footer.addWidget(cancel)
        self.footer.addWidget(create)

    def _set_color_preview(self) -> None:
        """Обновляет внешний вид круглой кнопки-превью акцентного цвета."""
        self._accent_btn.setStyleSheet(
            f"""
            QPushButton#AccentPreview {{
                border-radius: 17px;
                background: {self._color};
                border: 2px solid rgba(255,255,255,0.12);
            }}
            """
        )

    def _pick_color(self) -> None:
        """Открывает цветовой диалог для выбора цвета категории."""
        c = QColorDialog.getColor(QColor(self._color), self, "Акцентный цвет")
        if not c.isValid():
            return
        self._color = c.name()
        self._set_color_preview()

    def _pick_icon(self) -> None:
        """Открывает файловый диалог для выбора иконки категории."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбор иконки",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not file_path:
            return
        self._icon_path = Path(file_path)
        self._icon_lbl.setText(self._icon_path.name)

    def result(self) -> tuple[str, str, Optional[Path]]:
        """Возвращает введённые данные категории (имя, цвет, путь к иконке)."""
        return (self._name.text().strip(), self._color, self._icon_path)

