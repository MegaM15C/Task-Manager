from __future__ import annotations

"""Диалог создания новой категории задач."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
)

from src.utils.dialog import DialogHelperMixin
from src.ui.widgets.overlay_dialog import OverlayDialog


class CreateCategoryDialog(OverlayDialog, DialogHelperMixin):
    """Диалог «Создание категории» с выбором цвета и иконки."""

    def __init__(self, parent) -> None:
        """Создаёт поля ввода названия, цвета и загрузки иконки."""
        super().__init__(parent, title="Создание категории")
        self._icon_path: Optional[Path] = None
        self._color = "#6D5EF6"

        self._name = QLineEdit(self)
        self._name.setPlaceholderText("Введите название…")
        self._name.setMaxLength(24)
        self._name.setFixedWidth(150)

        self._accent_btn = QPushButton("Выбрать цвет", self)
        self._accent_btn.setCursor(Qt.PointingHandCursor)
        self._accent_btn.clicked.connect(self._pick_color)

        self._accent_preview = QPushButton("", self)
        self._accent_preview.setFixedSize(28, 28)
        self._accent_preview.clicked.connect(self._pick_color)
        self._accent_preview.setObjectName("AccentPreview")
        self._set_color_preview()

        icon_row = QHBoxLayout()
        self._icon_lbl = QLabel("Файл не выбран", self)
        self._icon_lbl.setFixedSize(150, 35)
        self._icon_lbl.setObjectName("CategoryIconLabel")
        # self._icon_lbl.setStyleSheet(
        #     """
        #     background: transparent;

        #     border-radius: 8px;
        #     """
        # )
        self._icon_btn = QPushButton("Загрузить файл", self)
        self._icon_btn.clicked.connect(self._pick_icon)
        icon_row.addWidget(self._icon_lbl)
        icon_row.addWidget(self._icon_btn)

        self.body.addLayout(
            self._row(
                "Название категории",
                "Название, которое будет отображаться рядом с задачей",
                control_widget=self._name,
            )
        )

        self.body.addWidget(self._divider())

        self.body.addLayout(
            self._row(
                "Акцентный цвет",
                "Выбор акцентного цвета категории",
                control_layout=self._accent_control(),
            )
        )

        self.body.addWidget(self._divider())

        self.body.addLayout(
            self._row(
                "Иконка категории",
                "Загрузите иконку, которая будет выражать категорию",
                control_layout=icon_row,
            )
        )

        create = QPushButton("Создать", self)
        create.setObjectName("AcceptButton")
        create.clicked.connect(self.accept)
        cancel = QPushButton("Отменить", self)
        cancel.clicked.connect(self.reject)

        self.footer.addStretch(1)
        self.footer.addWidget(cancel)
        self.footer.addWidget(create)

    def accept(self) -> None:  # type: ignore[override]
        name = self._name.text().strip()
        if not name:
            QMessageBox.warning(self, "Проверка данных", "Введите название категории.")
            self._name.setFocus()
            return
        if len(name) > 24:
            QMessageBox.warning(
                self,
                "Проверка данных",
                "Название категории не должно быть длиннее 24 символов.",
            )
            self._name.setFocus()
            return
        super().accept()

    def _accent_control(self) -> QHBoxLayout:
        """Возвращает layout с кнопкой выбора цвета и кругом-превью."""
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)
        h.addWidget(self._accent_btn)
        h.addWidget(self._accent_preview)
        return h

    def _set_color_preview(self) -> None:
        """Обновляет внешний вид круглой кнопки-превью акцентного цвета."""
        self._accent_preview.setStyleSheet(
            f"""
            QPushButton {{
                background: {self._color};
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
        self._icon_lbl.setText(f"{self._icon_path.name}")

    def result(self) -> tuple[str, str, Optional[Path]]:
        """Возвращает введённые данные категории (имя, цвет, путь к иконке)."""
        return (self._name.text().strip(), self._color, self._icon_path)
