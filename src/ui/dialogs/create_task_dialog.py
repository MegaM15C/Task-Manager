from __future__ import annotations

"""Диалог создания новой задачи."""

from datetime import date
from typing import Optional

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QLineEdit,
    QMessageBox,
    QPushButton,
)

from src.core.models import Category, Task
from src.ui.widgets.overlay_dialog import OverlayDialog
from src.utils.dialog import DialogHelperMixin


class CreateTaskDialog(OverlayDialog, DialogHelperMixin):
    """Диалог «Создание задачи» с полями названия, категории и дедлайна."""

    def __init__(
        self, parent, *, categories: list[Category], task: Task | None = None
    ) -> None:
        """Наполняет комбобокс категориями и настраивает поля ввода."""
        super().__init__(
            parent, title="Создание задачи" if task is None else "Изменение задачи"
        )
        self._categories = categories
        self._task = task

        self._name = QLineEdit(self)
        self._name.setPlaceholderText("Введите название…")
        self._name.setMaxLength(48)
        self._name.setFixedWidth(150)

        self._cat = QComboBox(self)
        self._cat.addItem("Без категории", userData=None)
        for c in categories:
            self._cat.addItem(c.name, userData=c.id)

        self._due = QDateEdit(self)
        today = QDate.currentDate()
        calendar = QCalendarWidget(self)
        calendar.setMinimumDate(today)
        calendar.setGridVisible(False)
        calendar.setFixedSize(320, 240)
        self._due.setCalendarPopup(True)
        self._due.setCalendarWidget(calendar)
        self._due.setMinimumDate(today)
        self._due.setDisplayFormat("dd.MM.yyyy")
        self._due.setDate(today)
        self._due.setFixedWidth(150)

        self._priority = QComboBox(self)
        # Higher number => higher priority
        self._priority.addItem("Низкий", userData=1)
        self._priority.addItem("Средний", userData=2)
        self._priority.addItem("Высокий", userData=3)
        self._priority.addItem("Критический", userData=4)
        self._priority.setCurrentIndex(1)  # default: medium
        self._important = QCheckBox("Важная задача", self)
        self._important.setObjectName("ImportantCheckBox")
        self._important.setToolTip(
            "Помеченная задача отображается с индикатором важности"
        )

        if task is not None:
            self._name.setText(task.title)
            self._set_combo_to_data(self._cat, task.category_id)
            if task.due is not None:
                self._due.setDate(QDate(task.due.year, task.due.month, task.due.day))
            self._set_combo_to_data(self._priority, int(task.priority))
            self._important.setChecked(bool(task.important))

        self.body.addLayout(
            self._row(
                "Название задачи",
                "Название должно кратко описывать суть",
                control_widget=self._name,
            )
        )
        self.body.addWidget(self._divider())
        self.body.addLayout(
            self._row(
                "Выбор категории",
                "Выберите категорию, к которой относится задача",
                control_widget=self._cat,
            )
        )
        self.body.addWidget(self._divider())
        self.body.addLayout(
            self._row(
                "Дата дедлайна",
                "Поставьте отметку, к какому сроку задача должна быть выполнена",
                control_widget=self._due,
            )
        )
        self.body.addWidget(self._divider())
        self.body.addLayout(
            self._row(
                "Приоритет",
                "Выше приоритет — выше задача в списке",
                control_widget=self._priority,
            )
        )
        self.body.addWidget(self._divider())
        self.body.addLayout(
            self._row(
                "Пометка важности",
                "Используйте для задач, требующих повышенного внимания",
                control_widget=self._important,
            )
        )

        create = QPushButton("Создать" if task is None else "Сохранить", self)
        create.setObjectName("AcceptButton")
        create.clicked.connect(self.accept)
        cancel = QPushButton("Отменить", self)
        cancel.clicked.connect(self.reject)

        self.footer.addStretch(1)
        self.footer.addWidget(cancel)
        self.footer.addWidget(create)

    def accept(self) -> None:  # type: ignore[override]
        title = self._name.text().strip()
        if not title:
            QMessageBox.warning(self, "Проверка данных", "Введите название задачи.")
            self._name.setFocus()
            return
        if len(title) > 48:
            QMessageBox.warning(
                self,
                "Проверка данных",
                "Название задачи не должно быть длиннее 48 символов.",
            )
            self._name.setFocus()
            return
        if self._due.date() < QDate.currentDate():
            QMessageBox.warning(
                self,
                "Проверка данных",
                "Дедлайн не может быть раньше сегодняшней даты.",
            )
            self._due.setDate(QDate.currentDate())
            self._due.setFocus()
            return
        super().accept()

    @staticmethod
    def _set_combo_to_data(combo: QComboBox, data) -> None:
        for i in range(combo.count()):
            if combo.itemData(i) == data:
                combo.setCurrentIndex(i)
                return

    def result(self) -> tuple[str, Optional[str], Optional[date], int, bool]:
        """Возвращает введённые пользователем данные о задаче."""
        title = self._name.text().strip()
        cat_id = self._cat.currentData()
        qd = self._due.date()
        due = date(qd.year(), qd.month(), qd.day()) if qd.isValid() else None
        priority = int(self._priority.currentData() or 0)
        important = self._important.isChecked()
        return title, cat_id, due, priority, important
