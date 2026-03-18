from __future__ import annotations

"""Главное окно приложения с сайдбаром и списком задач."""

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.models import Category, Settings, Task
from src.core.paths import AppPaths
from src.core.repositories import CategoriesRepository, SettingsRepository, TasksRepository
from src.ui.dialogs.create_category_dialog import CreateCategoryDialog
from src.ui.dialogs.create_task_dialog import CreateTaskDialog
from src.ui.dialogs.settings_dialog import SettingsDialog
from src.ui.theme import app_qss, font_from_settings, tokens_from_settings
from src.ui.widgets.sidebar import Sidebar
from src.ui.widgets.task_item import TaskItemWidget


class MainWindow(QMainWindow):
    """Главное окно приложения «Активa».

    Отвечает за:
    - инициализацию репозиториев и загрузку данных;
    - построение основного интерфейса (сайдбар + список задач);
    - обработку событий (инfinite scroll, фильтры, открытие диалогов).
    """

    def __init__(self) -> None:
        super().__init__()
        self._paths = AppPaths()
        self._paths.ensure()

        self._settings_repo = SettingsRepository(self._paths)
        self._cats_repo = CategoriesRepository(self._paths)
        self._tasks_repo = TasksRepository(self._paths, page_size=25)

        self._settings = self._settings_repo.load()
        self._categories: list[Category] = self._cats_repo.load_all()
        self._tasks_repo.ensure_seed_data()

        self._active_view_key = "all"
        self._page_index = 0
        self._loading = False

        self._build_ui()
        self._apply_settings()
        self._reload_sidebar()
        self._reset_and_load_first_page()

    def _build_ui(self) -> None:
        """Создаёт все виджеты главного окна и настраивает layout-ы."""
        self.setWindowTitle("Активa — Task Manager")
        self.setFixedSize(1024, 768)

        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar(root)
        self.sidebar.pin_btn.toggled.connect(self._on_pin_toggled)
        self.sidebar.view_selected.connect(self._on_view_selected)
        self.sidebar.add_category_requested.connect(self._open_create_category)
        self.sidebar.settings_requested.connect(self._open_settings)
        self.sidebar.theme_toggled.connect(self._on_theme_toggled)

        self._sidebar_container = QFrame(root)
        self._sidebar_container.setObjectName("SidebarContainer")
        s_l = QVBoxLayout(self._sidebar_container)
        s_l.setContentsMargins(0, 0, 0, 0)
        s_l.addWidget(self.sidebar)
        self._sidebar_container.setMaximumWidth(0)  # hidden by default
        layout.addWidget(self._sidebar_container)

        self._sidebar_anim = QPropertyAnimation(self._sidebar_container, b"maximumWidth", self)
        self._sidebar_anim.setDuration(180)
        self._sidebar_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._main = QFrame(root)
        self._main.setObjectName("MainArea")
        m = QVBoxLayout(self._main)
        m.setContentsMargins(18, 18, 18, 18)
        m.setSpacing(14)
        layout.addWidget(self._main, 1)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self._view_icon = QLabel("🗒", self._main)
        self._view_icon.setFixedWidth(22)
        self._view_title = QLabel("Все задачи", self._main)
        self._view_title.setObjectName("ViewTitle")
        self._view_title.setStyleSheet("QLabel#ViewTitle { font-size: 18px; font-weight: 900; }")
        header.addWidget(self._view_icon)
        header.addWidget(self._view_title)
        header.addStretch(1)

        add_task = QPushButton("+ Добавить задачу", self._main)
        add_task.setObjectName("PrimaryButton")
        add_task.clicked.connect(self._open_create_task)
        header.addWidget(add_task)
        m.addLayout(header)

        self._scroll = QScrollArea(self._main)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)

        self._list_host = QWidget(self._scroll)
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(10)

        self._spinner = QLabel("Загружаем задачи…", self._list_host)
        self._spinner.setAlignment(Qt.AlignCenter)
        self._spinner.setObjectName("LoadingSpinner")
        self._spinner.setStyleSheet("QLabel#LoadingSpinner { opacity: 0.7; padding: 10px; }")
        self._spinner.hide()

        self._list_layout.addWidget(self._spinner)
        self._list_layout.addStretch(1)
        self._scroll.setWidget(self._list_host)
        m.addWidget(self._scroll, 1)

        self._scroll.verticalScrollBar().valueChanged.connect(self._on_scroll)

        # Hover-to-reveal region
        # Important: we install the filter on the *application* so mouse move
        # events from children still reach us (otherwise hover detection is flaky).
        self.setMouseTracking(True)
        root.setMouseTracking(True)
        self._main.setMouseTracking(True)
        self._scroll.viewport().setMouseTracking(True)
        # Use QApplication.instance() without importing at top to keep imports lean.
        from PySide6.QtWidgets import QApplication

        QApplication.instance().installEventFilter(self)

        self._pinned = False

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Отслеживает движение мыши, чтобы показывать/скрывать сайдбар."""
        if not self.isVisible():
            return super().eventFilter(watched, event)

        if event.type() == QEvent.MouseMove and not self._pinned:
            # We need window-local coordinates regardless of which child emitted the event.
            pos = self.mapFromGlobal(QCursor.pos())
            if 0 <= pos.x() <= 10:
                self._show_sidebar()
            elif pos.x() > self._sidebar_container.maximumWidth() + 20:
                self._hide_sidebar()
        return super().eventFilter(watched, event)

    def _show_sidebar(self) -> None:
        """Запускает анимацию раскрытия сайдбара."""
        if self._sidebar_container.maximumWidth() >= 300:
            return
        self._sidebar_anim.stop()
        self._sidebar_anim.setStartValue(self._sidebar_container.maximumWidth())
        self._sidebar_anim.setEndValue(300)
        self._sidebar_anim.setDuration(500)
        self._sidebar_anim.start()

    def _hide_sidebar(self) -> None:
        """Запускает анимацию скрытия сайдбара."""
        if self._sidebar_container.maximumWidth() <= 0:
            return
        self._sidebar_anim.stop()
        self._sidebar_anim.setStartValue(self._sidebar_container.maximumWidth())
        self._sidebar_anim.setEndValue(0)
        self._sidebar_anim.setDuration(500)
        self._sidebar_anim.start()

    def _on_pin_toggled(self, checked: bool) -> None:
        """Фиксирует сайдбар в раскрытом состоянии или возвращает режим hover."""
        self._pinned = checked
        if checked:
            self._show_sidebar()
        else:
            self._hide_sidebar()

    def _apply_settings(self) -> None:
        """Применяет текущие настройки темы/шрифта ко всему окну."""
        tokens = tokens_from_settings(self._settings)
        self.setStyleSheet(app_qss(tokens))
        self.setFont(font_from_settings(self._settings))
        self.sidebar.set_theme_checked(dark=self._settings.theme == "dark")

    def _reload_sidebar(self) -> None:
        """Обновляет список категорий в сайдбаре."""
        self._categories = self._cats_repo.load_all()
        self.sidebar.set_categories(self._categories)

    def _open_settings(self) -> None:
        """Открывает диалог настроек и сохраняет новые значения при подтверждении."""
        dlg = SettingsDialog(self, self._settings)
        if dlg.exec() == QDialog.Accepted:
            self._settings = dlg.result_settings()
            self._settings_repo.save(self._settings)
            self._apply_settings()

    def _on_theme_toggled(self, dark: bool) -> None:
        """Обрабатывает переключатель темы в сайдбаре (light/dark)."""
        self._settings = Settings(
            accent_color=self._settings.accent_color,
            theme="dark" if dark else "light",
            font_family=self._settings.font_family,
        )
        self._settings_repo.save(self._settings)
        self._apply_settings()

    def _open_create_category(self) -> None:
        """Открывает диалог создания категории и добавляет её в JSON."""
        dlg = CreateCategoryDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        name, color, icon_path = dlg.result()
        if not name:
            return
        self._cats_repo.add(name, color, icon_source_path=icon_path)
        self._reload_sidebar()
        self._reset_and_load_first_page()

    def _open_create_task(self) -> None:
        """Открывает диалог создания задачи и сохраняет новую задачу."""
        dlg = CreateTaskDialog(self, categories=self._categories)
        if dlg.exec() != QDialog.Accepted:
            return
        title, cat_id, due = dlg.result()
        if not title:
            return
        self._tasks_repo.add(title, category_id=cat_id, due=due)
        self._reset_and_load_first_page()

    def _on_view_selected(self, key: str) -> None:
        """Меняет текущий фильтр списка задач (все, дедлайны, важные, категория)."""
        self._active_view_key = key
        if key == "all":
            self._view_icon.setText("🗒")
            self._view_title.setText("Все задачи")
        elif key == "deadlines":
            self._view_icon.setText("📅")
            self._view_title.setText("Дедлайны")
        elif key == "important":
            self._view_icon.setText("⭐")
            self._view_title.setText("Важное")
        elif key.startswith("category:"):
            cid = key.split(":", 1)[1]
            c = next((x for x in self._categories if x.id == cid), None)
            self._view_icon.setText("🏷")
            self._view_title.setText(c.name if c else "Категория")
        self._reset_and_load_first_page()

    def _reset_and_load_first_page(self) -> None:
        """Сбрасывает список и загружает первую страницу задач согласно фильтру."""
        self._page_index = 0
        self._clear_task_widgets()
        self._load_next_page()

    def _clear_task_widgets(self) -> None:
        """Удаляет все виджеты задач из layout-а и пересоздаёт строку со спиннером."""
        while self._list_layout.count() > 0:
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                # spacer/stretch
                pass
        self._spinner = QLabel("Загружаем задачи…", self._list_host)
        self._spinner.setAlignment(Qt.AlignCenter)
        self._spinner.setObjectName("LoadingSpinner")
        self._spinner.hide()
        self._list_layout.addWidget(self._spinner)
        self._list_layout.addStretch(1)

    def _on_scroll(self) -> None:
        """Реагирует на прокрутку: при достижении низа подгружает следующую страницу."""
        if self._loading:
            return
        sb = self._scroll.verticalScrollBar()
        if sb.maximum() <= 0:
            return
        if sb.value() >= int(sb.maximum() * 0.85):
            self._load_next_page()

    def _passes_view_filter(self, t: Task) -> bool:
        """Проверяет, подходит ли задача под текущий выбранный вид (фильтр)."""
        if self._active_view_key == "all":
            return True
        if self._active_view_key == "important":
            return t.important
        if self._active_view_key == "deadlines":
            return t.due is not None
        if self._active_view_key.startswith("category:"):
            cid = self._active_view_key.split(":", 1)[1]
            return t.category_id == cid
        return True

    def _load_next_page(self) -> None:
        """Запускает асинхронную загрузку следующей страницы задач."""
        if self._page_index >= self._tasks_repo.page_count():
            return
        self._loading = True
        self._spinner.show()

        # simulate fetch delay so spinner is visible (and keeps UI smooth)
        QTimer.singleShot(250, self._finish_load_next_page)

    def _finish_load_next_page(self) -> None:
        """Вызывается таймером: фактически подгружает задачи и добавляет их в список."""
        page = self._tasks_repo.load_page(self._page_index)
        self._page_index += 1
        self._spinner.hide()

        filtered = [t for t in page if self._passes_view_filter(t)]
        for t in filtered:
            cat = next((c for c in self._categories if c.id == t.category_id), None)
            w = TaskItemWidget(self._paths, t, category=cat, parent=self._list_host)
            w.toggled_done.connect(self._on_task_done_toggled)
            # Insert above the spinner (spinner should stay at the bottom).
            spinner_index = self._list_layout.indexOf(self._spinner)
            if spinner_index < 0:
                spinner_index = max(0, self._list_layout.count() - 1)
            self._list_layout.insertWidget(spinner_index, w)

        self._loading = False

        # If this view filtered out the entire page, keep paging until we either
        # display something or run out of pages. This preserves the "not all at once"
        # constraint while avoiding an empty list when matches exist in later pages.
        if not filtered and self._page_index < self._tasks_repo.page_count():
            self._load_next_page()

    def _on_task_done_toggled(self, task_id: str, done: bool) -> None:
        """Сохраняет изменение чекбокса выполнения задачи в репозиторий."""
        self._tasks_repo.set_done(task_id, done)

