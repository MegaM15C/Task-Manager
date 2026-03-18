"""Точка входа в приложение Task-Manager.

Здесь создаётся объект QApplication, главное окно и запускается цикл
обработки событий Qt.
"""

import sys

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main() -> int:
    """Создаёт приложение Qt, главное окно и запускает цикл событий.

    Возвращает:
        Код завершения приложения, который далее передаётся в SystemExit.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())