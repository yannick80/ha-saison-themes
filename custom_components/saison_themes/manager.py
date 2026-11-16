"""Runtime logic: writes the theme file, picks the season and applies the theme."""

from __future__ import annotations

from datetime import date
import logging
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DATES,
    DOMAIN,
    MODE_AUTO,
    MODE_OPTIONS,
    SEASON_BIRTHDAY,
    SIGNAL_UPDATE,
    THEME_NAMES,
    THEMES_DIR,
    THEMES_FILENAME,
)
from .logic import active_season, birthdays_today, easter_sunday, merged_options
from .themes import render_themes_yaml

_LOGGER = logging.getLogger(__name__)

ISSUE_THEMES_NOT_LOADED = "themes_not_loaded"
ISSUE_RELOAD_FAILED = "reload_failed"
STORE_VERSION = 1


def themes_file_path(hass: HomeAssistant) -> Path:
    """Path of the generated theme file."""
    return Path(hass.config.path(THEMES_DIR, THEMES_FILENAME))


class SaisonManager:
    """Keeps the active seasonal theme up to date."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self.mode: str = MODE_AUTO
        self.season: str | None = None
        self.applied_season: str | None = None
        self.themes_ok: bool = True
        self._store: Store[dict[str, Any]] = Store(
            hass, STORE_VERSION, f"{DOMAIN}.{entry.entry_id}"
        )
        self._unsub: list[CALLBACK_TYPE] = []

    # ------------------------------------------------------------------ helpers
    @property
    def options(self) -> dict[str, Any]:
        """Options merged with defaults."""
        return merged_options(dict(self.entry.options))

    @property
    def today(self) -> date:
        """Today's date in the configured time zone."""
        return dt_util.now().date()

    @property
    def theme_name(self) -> str | None:
        """Name of the theme for the current season."""
        return THEME_NAMES.get(self.season) if self.season else None

    def birthdays_today(self) -> list[str]:
        """Names with a birthday today."""
        return birthdays_today(self.options[SEASON_BIRTHDAY][CONF_DATES], self.today)

    def easter(self) -> date:
        """Easter Sunday of the current year."""
        return easter_sunday(self.today.year)

    def compute_season(self) -> str:
        """Season that should be active right now."""
        if self.mode != MODE_AUTO:
            return self.mode
        return active_season(self.today, dict(self.entry.options))

    # -------------------------------------------------------------- lifecycle
    async def async_start(self) -> None:
        """Load state, write the theme file and apply the theme."""
        stored = await self._store.async_load() or {}
        if stored.get("mode") in MODE_OPTIONS:
            self.mode = stored["mode"]

        changed = await self._async_write_themes_file()
        if changed:
            await self._async_reload_themes()
        await self.async_apply(force=True)

        self._unsub.append(
            async_track_time_change(
                self.hass, self._handle_midnight, hour=0, minute=0, second=5
            )
        )

    @callback
    def async_stop(self) -> None:
        """Stop listeners."""
        while self._unsub:
            self._unsub.pop()()

    async def async_options_updated(self) -> None:
        """Options changed: rewrite theme file and re-apply."""
        if await self._async_write_themes_file():
            await self._async_reload_themes()
        await self.async_apply(force=True)

    async def async_set_mode(self, mode: str) -> None:
        """Set the mode (auto or a fixed season) and persist it."""
        if mode not in MODE_OPTIONS:
            raise HomeAssistantError(f"Unknown mode {mode}")
        self.mode = mode
        await self._store.async_save({"mode": mode})
        await self.async_apply(force=True)

    async def _handle_midnight(self, _now: Any) -> None:
        await self.async_apply()

    # ----------------------------------------------------------- theme file
    async def _async_write_themes_file(self) -> bool:
        """Write the theme file if its content changed. Returns True if written."""
        content = render_themes_yaml(dict(self.entry.options))
        path = themes_file_path(self.hass)

        def _write() -> bool:
            if path.exists() and path.read_text(encoding="utf-8") == content:
                return False
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return True

        written = await self.hass.async_add_executor_job(_write)
        if written:
            _LOGGER.debug("Theme file written: %s", path)
        return written

    async def _async_reload_themes(self) -> bool:
        """Call frontend.reload_themes. Returns False if the reload failed."""
        try:
            await self.hass.services.async_call(
                "frontend", "reload_themes", blocking=True
            )
        except HomeAssistantError as err:
            _LOGGER.warning("Could not reload themes: %s", err)
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                ISSUE_RELOAD_FAILED,
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key=ISSUE_RELOAD_FAILED,
                translation_placeholders={"error": str(err)},
            )
            return False
        ir.async_delete_issue(self.hass, DOMAIN, ISSUE_RELOAD_FAILED)
        return True

    # ---------------------------------------------------------- apply theme
    async def _async_set_theme(self, name: str) -> None:
        for mode in ("light", "dark"):
            await self.hass.services.async_call(
                "frontend",
                "set_theme",
                {"name": name, "mode": mode},
                blocking=True,
            )

    async def async_apply(self, force: bool = False) -> None:
        """Determine the season and set the backend theme if needed."""
        self.season = self.compute_season()
        if force or self.season != self.applied_season:
            name = THEME_NAMES[self.season]
            try:
                await self._async_set_theme(name)
            except (vol.Invalid, HomeAssistantError):
                # Theme unknown to the frontend. Maybe the include line was added
                # since the last reload: reload once and try again.
                try:
                    if await self._async_reload_themes():
                        await self._async_set_theme(name)
                    else:
                        raise HomeAssistantError("reload failed")
                except (vol.Invalid, HomeAssistantError):
                    self._themes_missing()
                else:
                    self._themes_present()
            else:
                self._themes_present()
            self.applied_season = self.season
        async_dispatcher_send(self.hass, f"{SIGNAL_UPDATE}_{self.entry.entry_id}")

    def _themes_missing(self) -> None:
        self.themes_ok = False
        _LOGGER.warning(
            "Theme '%s' is not known to the frontend. Is 'frontend: themes: "
            "!include_dir_merge_named themes' in configuration.yaml?",
            self.theme_name,
        )
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            ISSUE_THEMES_NOT_LOADED,
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key=ISSUE_THEMES_NOT_LOADED,
            learn_more_url="https://github.com/yannick80/ha_saison_themes#einrichtung",
        )

    def _themes_present(self) -> None:
        self.themes_ok = True
        ir.async_delete_issue(self.hass, DOMAIN, ISSUE_THEMES_NOT_LOADED)


async def async_remove_themes_file(hass: HomeAssistant) -> None:
    """Delete the generated theme file and reload themes."""
    path = themes_file_path(hass)

    def _delete() -> bool:
        if path.exists():
            path.unlink()
            return True
        return False

    if await hass.async_add_executor_job(_delete):
        try:
            await hass.services.async_call("frontend", "reload_themes", blocking=True)
        except HomeAssistantError as err:
            _LOGGER.debug("Reload after removal failed: %s", err)
    for issue in (ISSUE_THEMES_NOT_LOADED, ISSUE_RELOAD_FAILED):
        ir.async_delete_issue(hass, DOMAIN, issue)
