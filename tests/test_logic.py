"""Tests for the date logic (logic.py)."""

from __future__ import annotations

from datetime import date

import pytest

from saison_themes import logic
from saison_themes.const import (
    CONF_DATES,
    CONF_ENABLED,
    CONF_START,
    SEASON_BIRTHDAY,
    SEASON_CHRISTMAS,
    SEASON_EASTER,
    SEASON_HALLOWEEN,
    SEASON_NEW_YEAR,
    SEASON_STANDARD,
)


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2024, date(2024, 3, 31)),
        (2025, date(2025, 4, 20)),
        (2026, date(2026, 4, 5)),
        (2027, date(2027, 3, 28)),
        (2038, date(2038, 4, 25)),  # latest possible date
        (2285, date(2285, 3, 22)),  # earliest possible date
    ],
)
def test_easter_sunday(year: int, expected: date) -> None:
    assert logic.easter_sunday(year) == expected


@pytest.mark.parametrize("value", ["14.03", "1.3", "1.3.", " 02.07 ", "29.02"])
def test_parse_day_month_accepts(value: str) -> None:
    logic.parse_day_month(value)


@pytest.mark.parametrize("value", ["", "31.04", "00.01", "01.13", "14-03", "14.03.2026", None])
def test_parse_day_month_rejects(value: str) -> None:
    with pytest.raises(ValueError):
        logic.parse_day_month(value)


def test_in_window_plain_range() -> None:
    assert logic.in_window(date(2026, 10, 15), "15.10", "02.11")
    assert logic.in_window(date(2026, 11, 2), "15.10", "02.11")
    assert not logic.in_window(date(2026, 10, 14), "15.10", "02.11")
    assert not logic.in_window(date(2026, 11, 3), "15.10", "02.11")


def test_in_window_across_new_year() -> None:
    assert logic.in_window(date(2026, 11, 30), "30.11", "06.01")
    assert logic.in_window(date(2026, 12, 31), "30.11", "06.01")
    assert logic.in_window(date(2027, 1, 6), "30.11", "06.01")
    assert not logic.in_window(date(2027, 1, 7), "30.11", "06.01")
    assert not logic.in_window(date(2026, 11, 29), "30.11", "06.01")


def test_birthdays_parsing_and_invalid_entries() -> None:
    birthdays, invalid = logic.parse_birthdays("Anna 14.03, Ben 02.07; 23.11\nKarl 31.04, Lisa")
    assert [(b.name, b.month, b.day) for b in birthdays] == [
        ("Anna", 3, 14),
        ("Ben", 7, 2),
        ("", 11, 23),
    ]
    assert invalid == ["Karl 31.04", "Lisa"]


def test_birthday_without_name() -> None:
    assert logic.birthdays_today("23.11", date(2026, 11, 23)) == ["Geburtstag"]


def test_leap_day_birthday() -> None:
    # celebrated on 28 Feb in non-leap years, on 29 Feb in leap years only
    assert logic.birthdays_today("Max 29.02", date(2027, 2, 28)) == ["Max"]
    assert logic.birthdays_today("Max 29.02", date(2028, 2, 29)) == ["Max"]
    assert logic.birthdays_today("Max 29.02", date(2028, 2, 28)) == []


@pytest.mark.parametrize(
    ("today", "expected"),
    [
        (date(2026, 7, 1), SEASON_STANDARD),
        (date(2026, 10, 31), SEASON_HALLOWEEN),
        (date(2026, 12, 24), SEASON_CHRISTMAS),
        (date(2026, 12, 31), SEASON_NEW_YEAR),  # wins over Christmas
        (date(2027, 1, 6), SEASON_CHRISTMAS),
        (date(2027, 1, 7), SEASON_STANDARD),
        # Easter 2026 is on 5 April; default window 14 days before to 7 days after
        (date(2026, 3, 21), SEASON_STANDARD),
        (date(2026, 3, 22), SEASON_EASTER),
        (date(2026, 4, 12), SEASON_EASTER),
        (date(2026, 4, 13), SEASON_STANDARD),
    ],
)
def test_active_season_defaults(today: date, expected: str) -> None:
    assert logic.active_season(today, {}) == expected


def test_birthday_has_highest_priority() -> None:
    options = {SEASON_BIRTHDAY: {CONF_DATES: "Anna 31.12, Ben 31.10"}}
    assert logic.active_season(date(2026, 12, 31), options) == SEASON_BIRTHDAY
    assert logic.active_season(date(2026, 10, 31), options) == SEASON_BIRTHDAY


def test_disabled_season_is_skipped() -> None:
    options = {SEASON_NEW_YEAR: {CONF_ENABLED: False}}
    assert logic.active_season(date(2026, 12, 31), options) == SEASON_CHRISTMAS


def test_invalid_period_is_skipped_not_fatal() -> None:
    options = {SEASON_HALLOWEEN: {CONF_START: "kaputt"}}
    assert logic.active_season(date(2026, 10, 31), options) == SEASON_STANDARD


def test_options_keep_defaults_for_missing_keys() -> None:
    merged = logic.merged_options({SEASON_HALLOWEEN: {CONF_START: "01.10"}})
    assert merged[SEASON_HALLOWEEN][CONF_START] == "01.10"
    assert merged[SEASON_HALLOWEEN]["end"] == "02.11"
    assert merged[SEASON_CHRISTMAS][CONF_START] == "30.11"
