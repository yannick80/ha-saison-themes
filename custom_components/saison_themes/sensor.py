"""Sensors for Saison-Themes."""

from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SaisonConfigEntry
from .const import ALL_SEASONS
from .entity import SaisonEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SaisonConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors."""
    manager = entry.runtime_data
    async_add_entities(
        [
            ActiveSeasonSensor(manager),
            BirthdayTodaySensor(manager),
            EasterSensor(manager),
        ]
    )


class ActiveSeasonSensor(SaisonEntity, SensorEntity):
    """The currently active season."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ALL_SEASONS
    _attr_icon = "mdi:palette-swatch"

    def __init__(self, manager) -> None:
        """Initialize."""
        super().__init__(manager, "active_season")

    @property
    def native_value(self) -> str | None:
        """Active season key."""
        return self.manager.season

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Theme name, mode and whether the theme is loaded."""
        return {
            "theme": self.manager.theme_name,
            "mode": self.manager.mode,
            "themes_loaded": self.manager.themes_ok,
        }


class BirthdayTodaySensor(SaisonEntity, SensorEntity):
    """Who has a birthday today."""

    _attr_icon = "mdi:cake-variant"

    def __init__(self, manager) -> None:
        """Initialize."""
        super().__init__(manager, "birthday_today")

    @property
    def native_value(self) -> str:
        """Names, comma separated, or 'keiner'."""
        names = self.manager.birthdays_today()
        return ", ".join(names) if names else "keiner"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Names as a list and count."""
        names = self.manager.birthdays_today()
        return {"names": names, "count": len(names)}


class EasterSensor(SaisonEntity, SensorEntity):
    """Easter Sunday of the current year."""

    _attr_device_class = SensorDeviceClass.DATE
    _attr_icon = "mdi:egg-easter"

    def __init__(self, manager) -> None:
        """Initialize."""
        super().__init__(manager, "easter_sunday")

    @property
    def native_value(self) -> date:
        """Easter Sunday."""
        return self.manager.easter()
