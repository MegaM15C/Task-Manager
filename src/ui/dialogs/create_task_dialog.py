from __future__ import annotations

"""Диалог создания новой задачи."""

from datetime import date
from typing import Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QComboBox, QDateEdit, QLabel, QLineEdit, QPushButton

from src.core.models import Category
from src.ui.widgets.overlay_dialog import OverlayDialog


class CreateTaskDialog(OverlayDialog):
    """Диалог «Создание задачи» с полями названия, категории и дедлайна."""

    def __init__(self, parent, *, categories: list[Category]) -> None:
        """Наполняет комбобокс категориями и настраивает поля ввода."""
        super().__init__(parent, title="Создание задачи")
        self._categories = categories

        self._name = QLineEdit(self)
        self._name.setPlaceholderText("Введите название…")

        self._cat = QComboBox(self)
        self._cat.addItem("Без категории", userData=None)
        for c in categories:
            self._cat.addItem(c.name, userData=c.id)

        self._due = QDateEdit(self)
        self._due.setCalendarPopup(True)
        self._due.setDisplayFormat("dd.MM.yyyy")
        self._due.setDate(QDate.currentDate())

        self.body.addWidget(QLabel("Название задачи", self))
        self.body.addWidget(self._name)
        self.body.addSpacing(6)
        self.body.addWidget(QLabel("Выбор категории", self))
        self.body.addWidget(self._cat)
        self.body.addSpacing(6)
        self.body.addWidget(QLabel("Дата дедлайна", self))
        self.body.addWidget(self._due)

        create = QPushButton("Создать", self)
        create.setObjectName("PrimaryButton")
        create.clicked.connect(self.accept)
        cancel = QPushButton("Отменить", self)
        cancel.clicked.connect(self.reject)

        self.footer.addStretch(1)
        self.footer.addWidget(cancel)
        self.footer.addWidget(create)

    def result(self) -> tuple[str, Optional[str], Optional[date]]:
        """Возвращает введённые пользователем данные о задаче."""
        title = self._name.text().strip()
        cat_id = self._cat.currentData()
        qd = self._due.date()
        due = date(qd.year(), qd.month(), qd.day()) if qd.isValid() else None
        return title, cat_id, due

