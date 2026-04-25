from src.theme.theme import ThemeTokens, DerivedTokens
from src.utils.icons import icons


def controls_qss(tokens: ThemeTokens, der_tokens: DerivedTokens) -> str:
    return f"""
        QCheckBox#ImportantCheckBox {{
            background: transparent;
            border: 1px solid {tokens.border};
            border-radius: 10px;
            padding: 8px 10px;
        }}
        QCheckBox#ImportantCheckBox::indicator {{
            background: transparent;
            border: 1px solid {tokens.border};
            border-radius: 4px;  /* ← скругление */
            width: 16px;
            height: 16px;
        }}
        QCheckBox#ImportantCheckBox::indicator:checked {{
            background: {der_tokens.primary_bg};
            border: 1px solid {tokens.border};
            image: url({icons["check"]});
            border-radius: 4px;
        }}

        QCheckBox#TaskCheckBox::indicator {{
            background: transparent;
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid {tokens.border};
        }}
        QCheckBox#TaskCheckBox::indicator:checked {{
            width: 16px;
            height: 16px;
            background-color: {der_tokens.primary_bg};
            border: 1px solid {tokens.border};
            border-radius: 4px;
            image: url("resources/icons/check.png");
            }}

        QLineEdit, QComboBox, QDateEdit {{
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-radius: 10px;
            padding: 8px 34px 8px 10px;
            selection-background-color: {tokens.accent};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            background: {tokens.surface_2};
            border-left: 1px solid {tokens.border};
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
            width: 28px;
        }}
        QComboBox::down-arrow {{
            image: url("resources/icons/arrow_down.png");
            width: 14px;
            height: 14px;
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
        """
