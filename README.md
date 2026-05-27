# Task Manager

Десктопный менеджер задач с поддержкой категорий, приоритетов, дедлайнов и резервного копирования. Написан на Python 3.10+ и PySide6.

## Возможности

- Создание задач с названием, категорией, приоритетом, дедлайном и флагом «важная»
- Категории с цветовой маркировкой и иконкой
- Виды: Все задачи / Дедлайны / Важное / Выполненные
- Светлая и тёмная тема с настраиваемым акцентным цветом
- Бесконечная прокрутка (infinite scroll) с подгрузкой задач постранично
- Экспорт / импорт данных в ZIP-архив
- Атомарная запись JSON-файлов (защита от повреждения при аварийном завершении)
- Автоматическое обнаружение повреждённых файлов при запуске с диалогом восстановления

## Структура проекта

```
Task-Manager/
├── main.py                     # Точка входа
├── pyproject.toml              # Метаданные и зависимости
├── task-manager.spec           # PyInstaller spec для сборки .exe / бинарника
├── requirements.txt            # Зависимости (PySide6, platformdirs)
├── resources/icons/            # PNG-иконки интерфейса
└── src/
    ├── core/
    │   ├── models.py           # Модели данных (Settings, Category, Task, ViewKey)
    │   ├── paths.py            # AppPaths — пути к файлам данных
    │   ├── json_io.py          # Безопасное чтение/атомарная запись JSON
    │   ├── repositories.py     # SettingsRepository, CategoriesRepository, TasksRepository
    │   ├── backup.py           # Экспорт/импорт ZIP-архива
    │   └── recovery.py         # StorageRecoveryManager — проверка и восстановление хранилища
    ├── theme/
    │   └── theme.py            # ThemeTokens, DerivedTokens, tokens_from_settings()
    ├── ui/
    │   ├── main_window.py      # MainWindow — главное окно приложения
    │   ├── dialogs/            # CreateTaskDialog, CreateCategoryDialog, SettingsDialog, StorageErrorDialog
    │   ├── widgets/            # Sidebar, TaskItemWidget, SmoothScrollArea, OverlayDialog
    │   └── styles/             # QSS-фрагменты: app, base, typography, buttons, controls, labels, components
    └── utils/
        ├── buttons.py          # HoverEffect — анимация наведения
        ├── icons.py            # Словарь путей к иконкам
        └── dialog.py           # DialogHelperMixin
```

## Пути к данным

| ОС      | Путь                                            |
|---------|-------------------------------------------------|
| Linux   | `~/.config/TaskManagerApp/`                     |
| Windows | `%LOCALAPPDATA%\TaskManagerApp\`                     |
| macOS   | `~/Library/Application Support/TaskManagerApp/` |

Внутри: `data/settings.json`, `data/categories.json`, `data/tasks_pages/page_NNNN.json`, `data/icons/`.

## Требования

- Python 3.10+
- PySide6 6.10.1
- platformdirs 4.3.8

## Установка и запуск (для разработки)

```bash
# Клонировать репозиторий
git clone <repo-url>
cd Task-Manager

# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# Установить зависимости
pip install -r requirements.txt

# Запустить
python main.py
```

В проекте уже есть готовое окружение `.venv/` — можно запускать напрямую:

```bash
.venv/bin/python main.py         # Linux/macOS
.venv\Scripts\python main.py     # Windows
```

## Сборка

Используется единый сборочный скрипт `build.py`. Результат зависит от платформы:

| Платформа | Артефакты                                                         |
|-----------|-------------------------------------------------------------------|
| Linux     | `dist/task-manager` + `dist/task-manager_0.8.0_amd64.deb`        |
| Windows   | `dist/task-manager.exe`                                           |

### Зависимости для сборки

На Linux также требуется `dpkg-deb` для сборки в .deb-пакет (входит в пакет `dpkg`, присутствует в большинстве дистрибутивов).

### Запуск сборки

```bash
python build.py           # сборка для текущей платформы
python build.py --clean   # предварительно очистить build/ и dist/
```

Скрипт запускает PyInstaller через `task-manager.spec`, затем на Linux автоматически упаковывает результат в `.deb` с иконкой и `.desktop`-файлом внутри пакета.

## Wayland и X11

Приложение работает на обоих протоколах. При запуске на Wayland Qt автоматически
использует `wayland` backend. Если нужно принудительно использовать X11 (через XWayland):

```bash
QT_QPA_PLATFORM=xcb python main.py
```

## Иконка и имя в Dock (Linux)

Корректное отображение иконки и имени «Менеджер задач» в системном Dock
(GNOME Activities, KDE Task Manager и др.) требует установленного `.desktop`-файла.

Он автоматически включается в `.deb`-пакет и устанавливается при его установке:

```bash
sudo dpkg -i dist/task-manager_0.8.0_amd64.deb
```

После установки пакета:
- Иконка появляется в Activities / App Grid
- Имя отображается как «Менеджер задач»
- Dock корректно группирует окна приложения

Без установки `.desktop`-файла (запуск бинарника напрямую): иконка в самом окне
будет корректной, но Dock покажет имя бинарного файла и сгенерированную иконку.

## Журнал (логи)

Приложение пишет два потока логов:

| Куда   | Уровень | Путь                                |
|--------|---------|-------------------------------------|
| stderr | INFO+   | (консоль)                           |
| Файл   | DEBUG+  | `~/.config/TaskManagerApp/app.log`  |

Просмотр на Linux:

```bash
tail -f ~/.config/TaskManagerApp/app.log
```

## Устранение неполадок

### Повреждённые файлы данных

При запуске автоматически проверяется целостность JSON-файлов. При обнаружении
повреждения открывается диалог с тремя вариантами:

- **Пересоздать хранилище** — повреждённые файлы перемещаются в `data_backup_YYYYMMDD_HHMMSS/`, создаётся чистое хранилище.
- **Открыть папку хранилища** — открывает директорию данных в файловом менеджере для ручного восстановления.
- **Выйти** — закрыть приложение без изменений.

### Приложение не запускается (нет прав)

```
Критическая ошибка: Не удалось создать директории данных приложения
```

Проверьте права доступа к домашней директории:

```bash
ls -la ~/.config/
chmod 755 ~/.config/
```

### Иконка приложения не отображается в taskbar (Linux)

Убедитесь, что файл `resources/icons/app_icon.png` присутствует и запуск
происходит из корневой директории проекта:

```bash
cd /path/to/Task-Manager && python main.py
```
