from __future__ import annotations

"""Виджеты для отображения одной строки задачи и плашки категории."""

from datetime import date
from typing import Optional


from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from src.utils.icons import icons
from src.core.models import Category, Task
from src.core.paths import AppPaths

PILL_HEIGHT = 24


def _human_due(d: Optional[date]) -> str:
    """Возвращает человекочитаемую дату дедлайна (Сегодня/Завтра/ДД.ММ.ГГГГ)."""
    if not d:
        return ""
    today = date.today()
    if d == today:
        return "Сегодня"
    try:
        from datetime import timedelta

        if d == today + timedelta(days=1):
            return "Завтра"
    except Exception:
        pass
    return d.strftime("%d.%m.%Y")


class CategoryPill(QFrame):
    """Небольшой виджет-плашка с цветом и иконкой категории."""

    def __init__(
        self, paths: AppPaths, category: Category, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._paths = paths
        self._category = category
        self.setObjectName("CategoryPill")
        self.setStyleSheet("""
            background-color: rgba(255,255,255,0.1);
            border-radius: 16px;
            """)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.setFixedHeight(PILL_HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        self._icon = QLabel(self)
        self._icon.setFixedSize(14, 14)
        self._icon.setScaledContents(True)
        layout.addWidget(self._icon)

        self._text = QLabel(category.name, self)
        self._text.setObjectName("CategoryPillText")
        layout.addWidget(self._text)

        self._apply_icon()
        self._apply_style()

    def _apply_icon(self) -> None:
        """Пробует загрузить и показать иконку категории из директории icons_dir."""
        if not self._category.icon_filename:
            self._icon.hide()
            return
        p = self._paths.icons_dir / self._category.icon_filename
        if not p.exists():
            self._icon.hide()
            return

        pix = QPixmap(str(p))
        if pix.isNull():
            self._icon.hide()
            return

        # Размер иконки
        size = min(self._icon.width(), self._icon.height())
        pix = pix.scaled(
            size,
            size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Создаём круг
        mask = QPixmap(size, size)
        mask.fill(Qt.GlobalColor.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawEllipse(0, 0, size, size)
        painter.end()

        pix.setMask(
            mask.createMaskFromColor(
                Qt.GlobalColor.transparent, Qt.MaskMode.MaskInColor
            )
        )

        self._icon.setPixmap(pix)
        self._icon.show()

    def _apply_style(self) -> None:
        """Применяет стили плашки (заливка цветом категории и белый текст)."""
        self.setStyleSheet(f"""
            QFrame#CategoryPill {{
                background: {self._category.color};
                border-radius: 4px;
            }}
            QLabel#CategoryPillText {{
                color: white;
                font-weight: 600;
            }}
            """)


class TaskItemWidget(QFrame):
    """Одна строка задачи в списке."""

    toggled_done = Signal(str, bool)
    menu_requested = Signal(str)

    def __init__(
        self,
        paths: AppPaths,
        task: Task,
        *,
        category: Category | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._paths = paths
        self._task = task
        self.setObjectName("TaskItem")
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        self._check = QCheckBox(self)
        self._check.setFixedSize(19, 19)
        self._check.setChecked(task.done)
        self._check.setObjectName("TaskCheckBox")
        self._check.stateChanged.connect(self._on_done_changed)
        layout.addWidget(self._check, 0, Qt.AlignVCenter)

        self._title = QLabel(task.title, self)
        self._title.setObjectName("TaskTitle")
        self._title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self._title, 1, Qt.AlignVCenter)

        self._important: QWidget
        if task.important:
            self._important = QFrame(self)
            self._important.setObjectName("TaskImportant")
            self._important.setFixedHeight(PILL_HEIGHT)
            self._important.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

            important_layout = QHBoxLayout(self._important)
            important_layout.setContentsMargins(8, 4, 8, 4)
            important_layout.setSpacing(5)

            important_icon = QLabel(self._important)
            important_icon.setFixedSize(14, 14)
            important_icon.setScaledContents(True)
            important_icon.setPixmap(QPixmap(icons["important_mask"]))
            important_layout.addWidget(important_icon)

            important_text = QLabel("Важная", self._important)
            important_text.setObjectName("TaskImportantText")
            important_layout.addWidget(important_text)
        else:
            self._important = QLabel("", self)
            self._important.setFixedWidth(1)
        layout.addWidget(self._important, 0, Qt.AlignVCenter)

        self._priority = QFrame(self)
        self._priority.setObjectName("TaskPriority")
        self._priority.setFixedHeight(PILL_HEIGHT)
        self._priority.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self._priority.setProperty("priority", int(task.priority))

        priority_layout = QHBoxLayout(self._priority)
        priority_layout.setContentsMargins(10, 4, 10, 4)
        priority_layout.setSpacing(0)
        priority_text = QLabel(f"П{max(0, int(task.priority))}", self._priority)
        priority_text.setObjectName("TaskPriorityText")
        priority_text.setAlignment(Qt.AlignCenter)
        priority_layout.addWidget(priority_text)

        self._priority.style().unpolish(self._priority)
        self._priority.style().polish(self._priority)
        layout.addWidget(self._priority, 0, Qt.AlignVCenter)

        self._pill: QWidget
        if category:
            self._pill = CategoryPill(paths, category, self)
        else:
            self._pill = QLabel("", self)
            self._pill.setFixedWidth(1)
        layout.addWidget(self._pill, 0, Qt.AlignVCenter)

        self._due = QLabel(_human_due(task.due), self)
        self._due.setObjectName("TaskDue")
        self._due.setFixedWidth(110)
        self._due.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self._due, 0, Qt.AlignVCenter)

        self._menu = QPushButton("⋯", self)
        self._menu.setObjectName("MenuButton")
        self._menu.setFixedSize(34, 34)
        self._menu.clicked.connect(lambda: self.menu_requested.emit(self._task.id))
        layout.addWidget(self._menu, 0, Qt.AlignVCenter)
        # Styling is handled globally by the app QSS for theme consistency.
        self._title.setStyleSheet("QLabel#TaskTitle { font-weight: 600; }")
        self._menu.setStyleSheet(
            "QPushButton#MenuButton { border-radius: 10px; padding: 0px; font-size: 18px; }"
        )

    def _on_done_changed(self) -> None:
        """Излучает сигнал при изменении чекбокса выполнения задачи."""
        self.toggled_done.emit(self._task.id, self._check.isChecked())
