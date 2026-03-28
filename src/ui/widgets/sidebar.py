from __future__ import annotations

"""Левый сайдбар с навигацией по видам и категориям задач."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap
from src.core.models import Category
from src.utils.buttons import HoverEffect
from src.ui.theme import ThemeTokens

from src.core.paths import AppPaths
from src.core.repositories import SettingsRepository

class SmoothScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()

        self._anim = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._anim.setDuration(400)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def wheelEvent(self, event):
        sb = self.verticalScrollBar()

        delta = event.angleDelta().y()

        # целевая позиция
        new_value = sb.value() - delta

        new_value = max(sb.minimum(), min(sb.maximum(), new_value))

        self._anim.stop()
        self._anim.setStartValue(sb.value())
        self._anim.setEndValue(new_value)
        self._anim.start()


class Sidebar(QFrame):
    """Сайдбар со списком видов (все/дедлайны/важное) и пользовательских категорий."""

    view_selected = Signal(str)  # view key: all, deadlines, important, category:<id>
    add_category_requested = Signal()
    category_delete_requested = Signal(str)  # category id
    settings_requested = Signal()
    theme_toggled = Signal(bool)  # True => dark
    def __init__(
        self,
        tokens: ThemeTokens,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tokens = tokens
        self._paths = AppPaths()
        self._cat_hovers: list[HoverEffect] = []
        self.setObjectName("Sidebar")
        self.setFixedHeight(750)
        # screen_height = self.parent().height()  # или QApplication.primaryScreen().size().height()
        self.setFixedWidth(300)
        # self.setFixedHeight(int(screen_height))  # 60% от высоты экрана
        # self.setStyleSheet("border-radius: 24px")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)
        
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        title = QLabel("<b>Меню</b>", self)
        title.setStyleSheet("" \
            "font-size: 28px",

        )
        title.setObjectName("SidebarTitle")
        top.addWidget(title)
        top.addStretch(1)

        self.pin_btn =QToolButton(self)
        self._pin_hover = HoverEffect(self.pin_btn, tokens=tokens)
        self.pin_btn.setCheckable(True)
        self.pin_btn.setIcon(QPixmap('resources/icons/expand.png'))
        self.pin_btn.setToolTip("Закрепить сайдбар")
        self.pin_btn.setObjectName("PinButton")
        self.pin_btn.setStyleSheet("""

        """)
        
        self.pin_btn.setFixedSize(34, 34)
        #self.pin_btn.clicked.connect(self.Sidebar._on_pin_toggled)
        top.addWidget(self.pin_btn)

        root.addLayout(top)

        self._nav_all = QPushButton("Все задачи", self)
        self._nav_all.setIcon(QPixmap('resources/icons/all_tasks.png'))
        self._nav_all_hover = HoverEffect(self._nav_all, tokens=tokens)

        self._nav_deadlines = QPushButton("Дедлайны", self)
        self._nav_deadlines.setIcon(QPixmap('resources/icons/deadline.png'))
        self._nav_deadlines_hover = HoverEffect(self._nav_deadlines, tokens=tokens)
        
        self._nav_important = QPushButton("Важное", self)
        self._nav_important.setIcon(QPixmap('resources/icons/important.png'))
        self._nav_important_hover = HoverEffect(self._nav_important, tokens=tokens)

        self._nav_done = QPushButton("Выполненные", self)
        self._nav_done.setIcon(QPixmap('resources/icons/completed_task.png'))
        self._nav_done_hover = HoverEffect(self._nav_done, tokens=tokens)
        
        for b in (self._nav_all, self._nav_deadlines, self._nav_important, self._nav_done):
            b.setObjectName("NavButton")
            b.setCursor(Qt.PointingHandCursor)

        self._nav_all.clicked.connect(lambda: self.view_selected.emit("all"))
        self._nav_deadlines.clicked.connect(lambda: self.view_selected.emit("deadlines"))
        self._nav_important.clicked.connect(lambda: self.view_selected.emit("important"))
        self._nav_done.clicked.connect(lambda: self.view_selected.emit("done"))

        root.addWidget(self._nav_all)
        root.addWidget(self._nav_deadlines)
        root.addWidget(self._nav_important)
        root.addWidget(self._nav_done)

        root.addSpacing(4)
        cats_lbl = QLabel("Категории", self)
        cats_lbl.setObjectName("SidebarSectionLabel")
        root.addWidget(cats_lbl)

        self._cats_container = QWidget()
        self._cats_container.setAttribute(Qt.WA_StyledBackground, True)
        self._cats_container.setStyleSheet("border-radius: 6px;")
        self._cats_layout = QVBoxLayout(self._cats_container)
        self._cats_container.setAutoFillBackground(True)
        self._cats_layout.setContentsMargins(0, 0, 0, 0)
        self._cats_layout.setSpacing(4)
        self._cats_layout.addStretch(1)

        self.scroll = SmoothScrollArea()
        self.scroll.verticalScrollBar().valueChanged.connect(
    lambda _: [w.update() for w in self._cats_container.findChildren(QWidget)]
)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setWidget(self._cats_container)
        root.addWidget(self.scroll, 1)

        self.add_cat = QPushButton("+ Добавить категорию", self)
        self._add_cat_hover = HoverEffect(self.add_cat, tokens=tokens)
        self.add_cat.setObjectName("AddCategoryButton")
        self.add_cat.clicked.connect(self.add_category_requested.emit)
        root.addWidget(self.add_cat)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)

        self._theme_btn = QToolButton(self)
        self._theme_hover = HoverEffect(self._theme_btn, tokens=tokens)
        self._theme_btn.setCheckable(True)
        settings = SettingsRepository(self._paths).load()
        if settings.theme == 'light':
            self._theme_btn.setIcon(
                QPixmap("resources/icons/light_theme_indicator.png")
            )
        else:
            self._theme_btn.setIcon(
                QPixmap("resources/icons/dark_theme_indicator.png")
            )
        self._theme_btn.setToolTip("Переключить тему")
        self._theme_btn.setObjectName("ThemeButton")
        self._theme_btn.setFixedSize(42, 34)
        self._theme_btn.toggled.connect(self.theme_toggled.emit)
        bottom.addWidget(self._theme_btn)

        bottom.addStretch(1)

        self.gear = QToolButton(self)
        self._gear_hover = HoverEffect(self.gear, tokens=tokens)
        self.gear.setIcon(QPixmap("resources/icons/settings.png"))
        self.gear.setToolTip("Настройки")
        self.gear.setObjectName("SettingsButton")
        self.gear.setFixedSize(42, 34)
        self.gear.clicked.connect(self.settings_requested.emit)
        bottom.addWidget(self.gear)

        root.addLayout(bottom)
        # Visual styling is applied globally from `src/ui/theme.py` QSS so it can
        # react to theme changes (light/dark) consistently.

    def set_theme_checked(self, *, dark: bool) -> None:
        """Программно выставляет состояние переключателя темы."""
        self._theme_btn.blockSignals(True)
        self._theme_btn.setChecked(dark)
        self._theme_btn.setIcon(QPixmap())
        if dark:
            self._theme_btn.setIcon(
                QPixmap("resources/icons/dark_theme_indicator.png")
            )
        else:
            self._theme_btn.setIcon(
                QPixmap("resources/icons/light_theme_indicator.png")
            )

        # self._theme_btn.setText("🌙" if dark else "☀")
        self._theme_btn.blockSignals(False)

    def set_categories(self, categories: list[Category]) -> None:
        """Обновляет список кнопок категорий на панели."""
        self._cat_hovers.clear()
        # удаляем старые кнопки (статический отступ/стретч пересоздадим ниже)
        while self._cats_layout.count() > 0:
            item = self._cats_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                # spacer/stretch
                pass

        for c in categories:
            b = QPushButton(f"{c.name}", self._cats_container)
            b.setObjectName("NavButton")
            self._cat_hovers.append(HoverEffect(b, tokens=self._tokens))

            b.setStyleSheet(f"QPushButton#NavButton{{ border-left: 2px solid {c.color}; font-size: 16px}}")
            b.clicked.connect(lambda _=False, cid=c.id: self.view_selected.emit(f"category:{cid}"))
            b.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            b.customContextMenuRequested.connect(
                lambda pos, cid=c.id, btn=b: self._on_category_context_menu(btn.mapToGlobal(pos), cid)
            )
            self._cats_layout.addWidget(b)

        self._cats_layout.addStretch(1)

    def _on_category_context_menu(self, global_pos, category_id: str) -> None:
        menu = QMenu(self)
        delete_action = menu.addAction("Удалить категорию…")
        chosen = menu.exec(global_pos)
        if chosen == delete_action:
            self.category_delete_requested.emit(category_id)

    def apply_theme_tokens(self, tokens: ThemeTokens) -> None:
        self._tokens = tokens
        self._pin_hover.set_tokens(tokens)
        self._theme_hover.set_tokens(tokens)
        self._nav_all_hover.set_tokens(tokens)
        self._nav_deadlines_hover.set_tokens(tokens)
        self._nav_important_hover.set_tokens(tokens)
        self._nav_done_hover.set_tokens(tokens)
        self._gear_hover.set_tokens(tokens)
        self._add_cat_hover.set_tokens(tokens)
        for h in self._cat_hovers:
            h.set_tokens(tokens)
