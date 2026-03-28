from __future__ import annotations

"""Формирование темы оформления и QSS-стилей для всего приложения."""

from dataclasses import dataclass

from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
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
    primary_bg = QColor(tokens.accent).darker(120).name()
    primary_text = _contrast_text_color(primary_bg)
    accent_text = _contrast_text_color(tokens.accent)
    surface_text = _contrast_text_color(tokens.surface)
    """Генерирует общую QSS-строку для приложения на основе токенов темы."""
    return f"""
    * {{
        font-size: 13px;
        color: {tokens.text};
    }}
    QWidget#Header {{
        background-color: {primary_bg};
        border-radius: 12px;                     /* скругление */
        border: 1px solid {tokens.border};
    }}
    QWidget {{
        background: {tokens.bg};
    }}
    QCheckBox#ImportantCheckBox {{
        background: transparent;
        border: 1px solid {tokens.border};
        border-radius: 10px;
        padding: 8px 10px;
    }}
    QCheckBox#TaskCheckBox::indicator {{
        background: transparent;
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid {tokens.border};
    }}
    QCheckBox#ImportantCheckBox::indicator {{
        background: transparent;
        border: 1px solid {tokens.border};
        border-radius: 4px;  /* ← скругление */
        width: 16px;
        height: 16px;
    }}

    QCheckBox#ImportantCheckBox::indicator:checked {{
        background: {primary_bg};
        border: 1px solid {tokens.border};
        image: url(resources/icons/check.png);
        border-radius: 4px;
    }}

    QCheckBox#TaskCheckBox::indicator:checked {{
        width: 16px;
        height: 16px;
        background-color: {primary_bg};
        border: 1px solid {tokens.border};
        border-radius: 4px;
        image: url(resources/icons/check.png); /* или свой путь */
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
        border: 0.6px solid {tokens.border};
        border-radius: 8px;
        color: {accent_text};
        font-weight: 800;
    }}
    QPushButton#PrimaryButton:hover {{
        border: 0.6px solid {tokens.border};
        border-radius: 8px;
        color: {accent_text};
        font-weight: 800;
    }}
    QPushButton#AcceptButton {{
        background: {primary_bg};
        border: 0.6px solid {tokens.border};
        border-radius: 8px;
        color: {primary_text};
        font-weight: 800;
    }}
    QPushButton#AcceptButton:hover {{
        background: {tokens.accent};
        border: 0.6px solid {tokens.border};
        border-radius: 8px;
        color: {primary_text};
        font-weight: 800;
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
        width: 8px;
        margin: 1px;
    }}
    QScrollBar::handle:vertical {{
        background: {tokens.border};
        border-radius: 2px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Sidebar */
    QFrame#Sidebar {{
        background: {tokens.surface};
        border: 1px solid {tokens.border};
        border-radius: 12px
    }}
    QLabel#SidebarSectionLabel {{
        color: {tokens.text_muted};
        font-weight: 700;
        padding-top: 6px;
    }}
    QToolButton#PinButton:hover, QToolButton#ThemeButton:hover, QToolButton#SettingsButton:hover {{
        background-color: rgba(0, 0, 0, 30);  /* слегка темнеет */
        border-radius: 8px;                   /* скругление если нужно */
    }}
    QToolButton#PinButton, QToolButton#ThemeButton, QToolButton#SettingsButton {{
        background: {tokens.surface_2};
        border: 1px solid {tokens.border};
        border-radius: 10px;
    }}

    QFrame#MainArea {{
        border: 1px solid {tokens.border};
        border-radius: 14px;
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
        background: rgba(10, 10, 10, 140);
    }}
    QFrame#DialogCard {{
        background: {tokens.surface};
        border: 1px solid {tokens.border};
        border-radius: 8px;
    }}
    QLabel#LoadingSpinner {{
        color: {tokens.text_muted};
        padding: 10px;
    }}
    QLabel#EmptyState {{
        color: {tokens.text_muted};
        background: {tokens.surface};
        border: 1px dashed {tokens.border};
        border-radius: 12px;
        padding: 14px;
        font-weight: 700;
    }}
    QMenu {{
        background: {tokens.surface};
        border: 1px solid {tokens.border};
        border-radius: 10px;
        padding: 6px;
    }}
    QMenu::item {{
        background: transparent;
        border-radius: 8px;
        padding: 8px 12px;
    }}
    QMenu::item:selected {{
        background: {tokens.surface_2};
    }}
    QLabel#TaskPriority {{
        border: 1px solid {tokens.border};
        border-radius: 8px;
        color: black;
    }}
    QLabel#TaskPriority[priority="1"] {{
    background: #C1E1C1;
    }}
    QLabel#TaskPriority[priority="2"] {{
        background: #B3D9FF;
    }}
    QLabel#TaskPriority[priority="3"] {{
        background: #FFD1A1;
    }}
    QLabel#TaskPriority[priority="4"] {{
        background: #FFB3B3;
    }}
    QLabel {{
        background: transparent;
    }}
    QLabel#CategoryIconLabel {{
        background: transparent;
        border: 1px solid {tokens.border};
        border-radius: 8px;

    }}
    QLabel#ViewTitle {{
        font-size: 18px;
        font-weight: 900;
        color: {accent_text};
    }}
    QPushButton#AccentPreview {{
        border: 2px solid {tokens.border};
        border-radius: 14px;
    }}
    """


def font_from_settings(s: Settings) -> QFont:
    """Создаёт базовый QFont на основе настроек пользователя."""
    f = QFont(s.font_family)
    f.setPointSize(14) # TO-DO: Сделать чтобы менялось, в данный момент не работает
    return f




def _contrast_text_color(bg_hex: str) -> str:
    c = QColor(bg_hex)

    brightness = (
        0.299 * c.red() +
        0.587 * c.green() +
        0.114 * c.blue()
    )

    return "#000000" if brightness > 186 else "#FFFFFF"