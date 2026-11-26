"""Date logic for the Saison-Themes integration.

Pure Python without Home Assistant imports, so it can be tested on its own.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
import re
from typing import Any

from .const import (
    CONF_DATES,
    CONF_DAYS_AFTER,
    CONF_DAYS_BEFORE,
    CONF_ENABLED,
    CONF_END,
    CONF_START,
    DEFAULT_OPTIONS,
    PRIORITY,
    SEASON_BIRTHDAY,
    SEASON_EASTER,
    SEASON_STANDARD,
)

_DAY_MONTH = re.compile(r"(\d{1,2})\.(\d{1,2})\.?")
_RANGE_SEASONS = ("halloween", "christmas", "new_year")


def parse_day_month(value: str) -> tuple[int, int]:
    """Parse 'TT.MM' (or 'T.M.') into (month, day). Raises ValueError if invalid."""
    match = _DAY_MONTH.fullmatch((value or "").strip())
    if not match:
        raise ValueError(f"invalid day/month: {value!r}")
    day, month = int(match.group(1)), int(match.group(2))
    if not 1 <= month <= 12 or not 1 <= day <= calendar.monthrange(2024, month)[1]:
        raise ValueError(f"invalid day/month: {value!r}")
    return month, day


def in_window(today: date, start: str, end: str) -> bool:
    """Return True if today lies between start and end (inclusive, year ignored)."""
    s_month, s_day = parse_day_month(start)
    e_month, e_day = parse_day_month(end)
    now = today.month * 100 + today.day
    s = s_month * 100 + s_day
    e = e_month * 100 + e_day
    if s <= e:
        return s <= now <= e
    return now >= s or now <= e  # window crosses the new year


def easter_sunday(year: int) -> date:
    """Easter Sunday (Gregorian calendar, anonymous Gregorian algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741 - names from the published algorithm
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


@dataclass(frozen=True)
class Birthday:
    """One birthday entry."""

    name: str
    month: int
    day: int


def parse_birthdays(text: str) -> tuple[list[Birthday], list[str]]:
    """Parse 'Anna 14.03, Ben 02.07; 23.11'. Returns (birthdays, invalid entries)."""
    result: list[Birthday] = []
    invalid: list[str] = []
    for raw in re_split(text or ""):
        entry = raw.strip()
        if not entry:
            continue
        match = _DAY_MONTH.search(entry)
        if not match:
            invalid.append(entry)
            continue
        try:
            month, day = parse_day_month(match.group(0))
        except ValueError:
            invalid.append(entry)
            continue
        name = (entry[: match.start()] + entry[match.end() :]).strip()
        result.append(Birthday(name=name, month=month, day=day))
    return result, invalid


def re_split(text: str) -> list[str]:
    """Split a list on commas, semicolons and line breaks."""
    return re.split(r"[,;\n]", text)


def birthdays_today(text: str, today: date) -> list[str]:
    """Names of everyone whose birthday is today. 29.02. counts as 28.02. in non-leap years."""
    names: list[str] = []
    birthdays, _ = parse_birthdays(text)
    for bday in birthdays:
        month, day = bday.month, bday.day
        if month == 2 and day == 29 and not calendar.isleap(today.year):
            day = 28
        if (month, day) == (today.month, today.day):
            names.append(bday.name or "Geburtstag")
    return names


def merged_options(options: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Options with defaults filled in for missing keys."""
    merged: dict[str, dict[str, Any]] = {}
    for key, defaults in DEFAULT_OPTIONS.items():
        merged[key] = {**defaults, **(options.get(key) or {})}
    return merged


def active_season(today: date, options: dict[str, Any]) -> str:
    """Determine the season key that applies on the given day."""
    opts = merged_options(options)
    for season in PRIORITY:
        cfg = opts[season]
        if not cfg.get(CONF_ENABLED, True):
            continue
        if season == SEASON_BIRTHDAY:
            if birthdays_today(cfg.get(CONF_DATES, ""), today):
                return season
        elif season == SEASON_EASTER:
            easter = easter_sunday(today.year)
            before = timedelta(days=int(cfg.get(CONF_DAYS_BEFORE, 14)))
            after = timedelta(days=int(cfg.get(CONF_DAYS_AFTER, 7)))
            if easter - before <= today <= easter + after:
                return season
        elif season in _RANGE_SEASONS:
            try:
                if in_window(today, cfg[CONF_START], cfg[CONF_END]):
                    return season
            except ValueError:
                continue
    return SEASON_STANDARD
