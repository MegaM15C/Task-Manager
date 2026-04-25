import sys
import platform

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.ui.main_window import MainWindow


def setup_app(app: QApplication):
    icon_path = "resources/icons/app_icon.png"

    app.setWindowIcon(QIcon(icon_path))
    app.setApplicationName("task-manager")

    system = platform.system()

    if system == "Windows":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "task.manager.app"
        )

    elif system == "Linux":
        app.setDesktopFileName("task-manager")


def main() -> int:
    app = QApplication(sys.argv)
    setup_app(app)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
