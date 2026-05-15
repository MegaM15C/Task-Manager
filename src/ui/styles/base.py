from __future__ import annotations

"""Базовые QSS-стили для всего приложения."""

from src.theme.theme import ThemeTokens


def base_qss(tokens: ThemeTokens):
    return f"""
            QWidget {{
                background: {tokens.bg};
            }}

            * {{
                font-size: 14px;
                color: {tokens.text};
            }}
        """
