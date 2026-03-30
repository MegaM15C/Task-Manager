from __future__ import annotations

"""Формирование темы оформления и QSS-стилей для всего приложения."""


from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
from src.core.models import Settings
from src.theme.theme import ThemeTokens, DerivedTokens

from src.ui.styles.base import base_qss
from src.ui.styles.typography import typography_qss
from src.ui.styles.controls import controls_qss
from src.ui.styles.labels import labels_qss
from src.ui.styles.buttons import buttons_qss, tool_buttons_qss
from src.ui.styles.components import components_qss

def app_qss(tokens: ThemeTokens) -> str:
    primary_bg = QColor(tokens.accent).darker(120).name()
    primary_text = contrast_text_color(primary_bg)
    accent_text = contrast_text_color(tokens.accent)
    derived_tokens = DerivedTokens(primary_bg, primary_text, accent_text)
    """Генерирует общую QSS-строку для приложения на основе токенов темы."""
    return "".join([
        base_qss(tokens),
        typography_qss(tokens),
        buttons_qss(tokens, derived_tokens),
        tool_buttons_qss(tokens),
        labels_qss(tokens, derived_tokens),
        controls_qss(tokens, derived_tokens),
        components_qss(tokens, derived_tokens)
    ])


def font_from_settings(s: Settings) -> QFont:
    """Создаёт базовый QFont на основе настроек пользователя."""
    f = QFont(s.font_family)
    f.setPointSize(14) # TO-DO: Сделать чтобы менялось, в данный момент не работает
    return f




def contrast_text_color(bg_hex: str) -> str:
    """Помогает на основе фона сделать текст более контрасным

    Args:
        bg_hex (str): цвет фона в HEX-формате

    Returns:
        str: HEX цвет текста, белый(#FFFFFF) или черный(#000000)
    """

    c = QColor(bg_hex)

    brightness = (
        0.299 * c.red() +
        0.587 * c.green() +
        0.114 * c.blue()
    )

    return "#000000" if brightness > 186 else "#FFFFFF"