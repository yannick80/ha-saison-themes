"""Mode selection for Saison-Themes."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SaisonConfigEntry
from .const import MODE_OPTIONS
from .entity import SaisonEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SaisonConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the select entity."""
    async_add_entities([SaisonModeSelect(entry.runtime_data)])


class SaisonModeSelect(SaisonEntity, SelectEntity):
    """Automatic or a fixed theme."""

    _attr_options = MODE_OPTIONS
    _attr_icon = "mdi:palette"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, manager) -> None:
        """Initialize."""
        super().__init__(manager, "mode")

    @property
    def current_option(self) -> str:
        """Current mode."""
        return self.manager.mode

    async def async_select_option(self, option: str) -> None:
        """Change mode."""
        await self.manager.async_set_mode(option)
