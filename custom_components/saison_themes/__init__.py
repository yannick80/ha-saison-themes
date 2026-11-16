"""Saison-Themes: seasonal themes with background images for Home Assistant."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, STATIC_URL
from .manager import SaisonManager, async_remove_themes_file

PLATFORMS: list[Platform] = [Platform.SELECT, Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type SaisonConfigEntry = ConfigEntry[SaisonManager]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Serve the background images (once per Home Assistant run)."""
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                STATIC_URL,
                str(Path(__file__).parent / "backgrounds"),
                cache_headers=True,
            )
        ]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SaisonConfigEntry) -> bool:
    """Set up Saison-Themes from a config entry."""
    manager = SaisonManager(hass, entry)
    entry.runtime_data = manager
    await manager.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    entry.async_on_unload(manager.async_stop)
    return True


async def _async_options_updated(hass: HomeAssistant, entry: SaisonConfigEntry) -> None:
    await entry.runtime_data.async_options_updated()


async def async_unload_entry(hass: HomeAssistant, entry: SaisonConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: SaisonConfigEntry) -> None:
    """Remove the generated theme file when the integration is deleted."""
    await async_remove_themes_file(hass)
