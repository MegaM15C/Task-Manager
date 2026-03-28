from __future__ import annotations

"""Формирование темы оформления и QSS-стилей для всего приложения."""

from dataclasses import dataclass
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


@dataclass(frozen=True)
class DerivedTokens:
    """Значения, которые передаются вспомогательным генераторам QSS-стилей
    """
    primary_bg: str
    primary_text: str
    accent_text: str


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