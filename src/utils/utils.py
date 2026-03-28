from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class DialogHelperMixin:
    def _divider(self) -> QFrame:
        """Создаёт горизонтальный разделитель между строками настроек."""
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("QFrame { color: rgba(100,100,100,0); }")
        return line

    def _row(
        self,
        title: str,
        subtitle: str,
        *,
        control_widget=None,
        control_layout: QHBoxLayout | None = None,
        ) -> QHBoxLayout:
        """Строит одну строку настроек: заголовок + описание + контрол справа."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(2)
        t = QLabel(title, self)
        t.setStyleSheet("font-weight: 800;")
        s = QLabel(subtitle, self)
        s.setWordWrap(True)
        left.addWidget(t)
        left.addWidget(s)

        row.addLayout(left, 1)
        row.addStretch(0)

        if control_layout is not None:
            row.addLayout(control_layout, 0)
        elif control_widget is not None:
            row.addWidget(control_widget, 0, Qt.AlignRight | Qt.AlignVCenter)
        return row
