from __future__ import annotations

"""Формирование темы оформления и QSS-стилей для всего приложения."""

from dataclasses import dataclass

from PySide6.QtGui import QFont

from src.core.models import Settings


@dataclass(frozen=True)
class ThemeTokens:
    """Набор базовых цветов для текущей темы.

    Эти значения затем подставляются в QSS-строку для виджетов.
    """

    accent: str
    bg: str
    surface: str
    surface_2: str
    text: str
    text_muted: str
    border: str


def tokens_from_settings(s: Settings) -> ThemeTokens:
    """Создаёт набор цветовых токенов из объекта Settings."""
    if s.theme == "light":
        return ThemeTokens(
            accent=s.accent_color,
            bg="#F5F6FA",
            surface="#FFFFFF",
            surface_2="#F0F2F7",
            text="#111318",
            text_muted="#5B6270",
            border="#D9DDEA",
        )
    return ThemeTokens(
        accent=s.accent_color,
        bg="#0F1116",
        surface="#151824",
        surface_2="#1B2030",
        text="#E9ECF5",
        text_muted="#A7AFC3",
        border="#2A3147",
    )


def app_qss(tokens: ThemeTokens) -> str:
    """Генерирует общую QSS-строку для приложения на основе токенов темы."""
    return f"""
    * {{
        font-size: 13px;
        color: {tokens.text};
    }}
    QWidget {{
        background: {tokens.bg};
    }}
    QCheckBox#TaskCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid #000000;
        background-color: transparent;
    }}
    QCheckBox#TaskCheckBox::indicator:checked {{
        width: 16px;
        height: 16px;
        background-color: {tokens.accent};
        border: none;
        image: url(resources/icons/check.svg); /* или свой путь */
    }}
    QPushButton {{
        background: {tokens.surface_2};
        border: 1px solid {tokens.border};
        border-radius: 10px;
        padding: 8px 12px;
    }}
    QPushButton:hover {{
        background: {tokens.surface};
    }}
    QPushButton#PrimaryButton {{
        background: {tokens.accent};
        border: none;
        color: white;
        font-weight: 600;
    }}
    QPushButton#PrimaryButton:hover {{
        background: {tokens.accent};
    }}
    QLineEdit, QComboBox, QDateEdit {{
        background: {tokens.surface};
        border: 1px solid {tokens.border};
        border-radius: 10px;
        padding: 8px 10px;
        selection-background-color: {tokens.accent};
    }}
    QComboBox::drop-down {{
        border: 0px;
        width: 26px;
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {tokens.border};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Sidebar */
    QFrame#Sidebar {{
        background: {tokens.surface};
        border-right: 1px solid {tokens.border};
    }}
    QLabel#SidebarSectionLabel {{
        color: {tokens.text_muted};
        font-weight: 700;
        padding-top: 6px;
    }}
    QToolButton#PinButton, QToolButton#ThemeButton, QToolButton#SettingsButton {{
        background: {tokens.surface_2};
        border: 1px solid {tokens.border};
        border-radius: 10px;
    }}

    /* Task item rows */
    QFrame#TaskItem {{
        background: {tokens.surface};
        border: 1px solid {tokens.border};
        border-radius: 14px;
    }}
    QLabel#TaskDue {{
        color: {tokens.text_muted};
    }}

    /* Dialog overlay + card */
    QWidget#Overlay {{
        background: rgba(0, 0, 0, 140);
    }}
    QFrame#DialogCard {{
        background: {tokens.surface};
        border: 1px solid {tokens.border};
        border-radius: 16px;
    }}
    QLabel#LoadingSpinner {{
        color: {tokens.text_muted};
        padding: 10px;
    }}
    QLabel {{
    background: transparent;
    }}
    """


def font_from_settings(s: Settings) -> QFont:
    """Создаёт базовый QFont на основе настроек пользователя."""
    f = QFont(s.font_family)
    f.setPointSize(10)
    return f

