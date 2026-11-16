"""Theme definitions and YAML generation for the Saison-Themes integration."""

from __future__ import annotations

from typing import Any

import yaml

from .const import (
    CONF_COLOR,
    CONF_GENERAL,
    SEASON_BIRTHDAY,
    SEASON_CHRISTMAS,
    SEASON_EASTER,
    SEASON_HALLOWEEN,
    SEASON_NEW_YEAR,
    SEASON_STANDARD,
    STATIC_URL,
    THEME_NAMES,
    VERSION,
)
from .logic import merged_options

# Everything except the primary color, which comes from the options.
_STYLES: dict[str, dict[str, Any]] = {
    SEASON_HALLOWEEN: {
        "accent": "#9B59B6",
        "icon": "#FF7518",
        "header": "rgba(10, 5, 13, 0.55)",
        "card_light": "rgba(255, 245, 235, 0.82)",
        "text_light": "#1e0c28",
        "card_dark": "rgba(20, 10, 26, 0.72)",
        "bg_dark": "#0a050d",
    },
    SEASON_CHRISTMAS: {
        "accent": "#D4AF37",
        "icon": "#D4AF37",
        "header": "rgba(6, 20, 15, 0.55)",
        "card_light": "rgba(255, 255, 255, 0.82)",
        "text_light": "#0b1f2e",
        "card_dark": "rgba(8, 24, 20, 0.72)",
        "bg_dark": "#0a1a15",
    },
    SEASON_NEW_YEAR: {
        "accent": "#E040FB",
        "icon": "#E6B422",
        "header": "rgba(5, 8, 25, 0.55)",
        "card_light": "rgba(255, 255, 255, 0.82)",
        "text_light": "#0b1030",
        "card_dark": "rgba(10, 14, 40, 0.72)",
        "bg_dark": "#050819",
    },
    SEASON_EASTER: {
        "accent": "#F48FB1",
        "icon": "#F4B400",
        "header": "rgba(124, 179, 66, 0.85)",
        "card_light": "rgba(255, 255, 255, 0.78)",
        "text_light": "#2e3b1f",
        "card_dark": "rgba(30, 36, 24, 0.72)",
        "bg_dark": "#1b2414",
    },
    SEASON_BIRTHDAY: {
        "accent": "#26C6DA",
        "icon": "#FFCA28",
        "header": "rgba(42, 27, 74, 0.6)",
        "card_light": "rgba(255, 255, 255, 0.82)",
        "text_light": "#2a1b4a",
        "card_dark": "rgba(36, 22, 62, 0.72)",
        "bg_dark": "#1c1233",
    },
}

BACKGROUND_FILES: dict[str, str] = {
    SEASON_HALLOWEEN: "halloween.svg",
    SEASON_CHRISTMAS: "weihnachten.svg",
    SEASON_NEW_YEAR: "silvester.svg",
    SEASON_EASTER: "ostern.svg",
    SEASON_BIRTHDAY: "geburtstag.svg",
}


def rgb_to_hex(rgb: list[int] | tuple[int, int, int] | str) -> str:
    """Convert [r, g, b] to '#RRGGBB'. Strings are passed through."""
    if isinstance(rgb, str):
        return rgb
    r, g, b = (max(0, min(255, int(v))) for v in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def build_themes(options: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build all theme definitions as a dict (theme name -> variables)."""
    opts = merged_options(options)
    themes: dict[str, dict[str, Any]] = {
        THEME_NAMES[SEASON_STANDARD]: {
            "primary-color": rgb_to_hex(opts[CONF_GENERAL][CONF_COLOR]),
            "accent-color": "#FF9800",
            "modes": {"light": {}, "dark": {}},
        }
    }
    for season, style in _STYLES.items():
        primary = rgb_to_hex(opts[season][CONF_COLOR])
        background = f"{STATIC_URL}/{BACKGROUND_FILES[season]}?v={VERSION}"
        themes[THEME_NAMES[season]] = {
            "primary-color": primary,
            "accent-color": style["accent"],
            "state-icon-active-color": style["icon"],
            "lovelace-background": f'center / cover no-repeat fixed url("{background}")',
            "app-header-background-color": style["header"],
            "ha-card-border-radius": "16px",
            "modes": {
                "light": {
                    "ha-card-background": style["card_light"],
                    "primary-text-color": style["text_light"],
                },
                "dark": {
                    "ha-card-background": style["card_dark"],
                    "primary-background-color": style["bg_dark"],
                },
            },
        }
    return themes


HEADER = (
    "# Diese Datei wird von der Integration \"Saison-Themes\" automatisch erzeugt.\n"
    "# Aenderungen hier werden ueberschrieben. Farben und Zeitraeume stellst du unter\n"
    "# Einstellungen > Geraete & Dienste > Saison-Themes > Konfigurieren ein.\n\n"
)


def render_themes_yaml(options: dict[str, Any]) -> str:
    """Render the theme file content."""
    body = yaml.safe_dump(
        build_themes(options), sort_keys=False, allow_unicode=True, width=200
    )
    return HEADER + body
