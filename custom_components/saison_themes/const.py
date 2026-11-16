"""Constants for the Saison-Themes integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "saison_themes"
VERSION: Final = "1.0.0"

# URL under which the background images are served (no login required, like /local).
STATIC_URL: Final = "/saison_themes_static"

# File written into the user's themes folder (/config/themes/<THEMES_FILENAME>).
THEMES_DIR: Final = "themes"
THEMES_FILENAME: Final = "saison_themes.yaml"

SIGNAL_UPDATE: Final = f"{DOMAIN}_update"

# Season keys, in order of priority (first match wins).
SEASON_BIRTHDAY: Final = "birthday"
SEASON_NEW_YEAR: Final = "new_year"
SEASON_HALLOWEEN: Final = "halloween"
SEASON_CHRISTMAS: Final = "christmas"
SEASON_EASTER: Final = "easter"
SEASON_STANDARD: Final = "standard"

PRIORITY: Final = [
    SEASON_BIRTHDAY,
    SEASON_NEW_YEAR,
    SEASON_HALLOWEEN,
    SEASON_CHRISTMAS,
    SEASON_EASTER,
]

ALL_SEASONS: Final = [SEASON_STANDARD, *PRIORITY]

# Theme names as they appear in the Home Assistant profile settings.
THEME_NAMES: Final = {
    SEASON_STANDARD: "Saison Standard",
    SEASON_HALLOWEEN: "Saison Halloween",
    SEASON_CHRISTMAS: "Saison Weihnachten",
    SEASON_NEW_YEAR: "Saison Silvester",
    SEASON_EASTER: "Saison Ostern",
    SEASON_BIRTHDAY: "Saison Geburtstag",
}

MODE_AUTO: Final = "auto"
MODE_OPTIONS: Final = [MODE_AUTO, *ALL_SEASONS]

# Option keys
CONF_GENERAL: Final = "general"
CONF_ENABLED: Final = "enabled"
CONF_START: Final = "start"
CONF_END: Final = "end"
CONF_COLOR: Final = "color"
CONF_DAYS_BEFORE: Final = "days_before"
CONF_DAYS_AFTER: Final = "days_after"
CONF_DATES: Final = "dates"

DEFAULT_OPTIONS: Final = {
    CONF_GENERAL: {CONF_COLOR: [3, 169, 244]},
    SEASON_HALLOWEEN: {
        CONF_ENABLED: True,
        CONF_START: "15.10",
        CONF_END: "02.11",
        CONF_COLOR: [255, 117, 24],
    },
    SEASON_CHRISTMAS: {
        CONF_ENABLED: True,
        CONF_START: "30.11",
        CONF_END: "06.01",
        CONF_COLOR: [200, 16, 46],
    },
    SEASON_NEW_YEAR: {
        CONF_ENABLED: True,
        CONF_START: "31.12",
        CONF_END: "31.12",
        CONF_COLOR: [230, 180, 34],
    },
    SEASON_EASTER: {
        CONF_ENABLED: True,
        CONF_DAYS_BEFORE: 14,
        CONF_DAYS_AFTER: 7,
        CONF_COLOR: [124, 179, 66],
    },
    SEASON_BIRTHDAY: {
        CONF_ENABLED: True,
        CONF_DATES: "",
        CONF_COLOR: [236, 64, 122],
    },
}
