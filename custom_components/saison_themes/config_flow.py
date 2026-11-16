"""Config and options flow for Saison-Themes."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers import selector

from .const import (
    CONF_COLOR,
    CONF_DATES,
    CONF_DAYS_AFTER,
    CONF_DAYS_BEFORE,
    CONF_ENABLED,
    CONF_END,
    CONF_GENERAL,
    CONF_START,
    DEFAULT_OPTIONS,
    DOMAIN,
    SEASON_BIRTHDAY,
    SEASON_CHRISTMAS,
    SEASON_EASTER,
    SEASON_HALLOWEEN,
    SEASON_NEW_YEAR,
)
from .logic import merged_options, parse_birthdays, parse_day_month

_COLOR = selector.ColorRGBSelector()
_BOOL = selector.BooleanSelector()
_DAY_MONTH = selector.TextSelector(selector.TextSelectorConfig())
_DAYS = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0, max=60, step=1, mode=selector.NumberSelectorMode.BOX
    )
)
_LIST = selector.TextSelector(selector.TextSelectorConfig(multiline=True))


def _range_section(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_ENABLED, default=values[CONF_ENABLED]): _BOOL,
            vol.Required(CONF_START, default=values[CONF_START]): _DAY_MONTH,
            vol.Required(CONF_END, default=values[CONF_END]): _DAY_MONTH,
            vol.Required(CONF_COLOR, default=values[CONF_COLOR]): _COLOR,
        }
    )


def options_schema(current: dict[str, Any]) -> vol.Schema:
    """Build the options form with one collapsible section per season."""
    opts = merged_options(current)
    collapsed = {"collapsed": True}
    return vol.Schema(
        {
            vol.Required(CONF_GENERAL): section(
                vol.Schema(
                    {
                        vol.Required(
                            CONF_COLOR, default=opts[CONF_GENERAL][CONF_COLOR]
                        ): _COLOR
                    }
                ),
                {"collapsed": False},
            ),
            vol.Required(SEASON_HALLOWEEN): section(
                _range_section(opts[SEASON_HALLOWEEN]), collapsed
            ),
            vol.Required(SEASON_CHRISTMAS): section(
                _range_section(opts[SEASON_CHRISTMAS]), collapsed
            ),
            vol.Required(SEASON_NEW_YEAR): section(
                _range_section(opts[SEASON_NEW_YEAR]), collapsed
            ),
            vol.Required(SEASON_EASTER): section(
                vol.Schema(
                    {
                        vol.Required(
                            CONF_ENABLED, default=opts[SEASON_EASTER][CONF_ENABLED]
                        ): _BOOL,
                        vol.Required(
                            CONF_DAYS_BEFORE,
                            default=opts[SEASON_EASTER][CONF_DAYS_BEFORE],
                        ): _DAYS,
                        vol.Required(
                            CONF_DAYS_AFTER,
                            default=opts[SEASON_EASTER][CONF_DAYS_AFTER],
                        ): _DAYS,
                        vol.Required(
                            CONF_COLOR, default=opts[SEASON_EASTER][CONF_COLOR]
                        ): _COLOR,
                    }
                ),
                collapsed,
            ),
            vol.Required(SEASON_BIRTHDAY): section(
                vol.Schema(
                    {
                        vol.Required(
                            CONF_ENABLED, default=opts[SEASON_BIRTHDAY][CONF_ENABLED]
                        ): _BOOL,
                        vol.Optional(
                            CONF_DATES,
                            description={
                                "suggested_value": opts[SEASON_BIRTHDAY][CONF_DATES]
                            },
                        ): _LIST,
                        vol.Required(
                            CONF_COLOR, default=opts[SEASON_BIRTHDAY][CONF_COLOR]
                        ): _COLOR,
                    }
                ),
                {"collapsed": False},
            ),
        }
    )


def validate_options(
    user_input: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str], dict[str, str]]:
    """Normalize and validate. Returns (options, errors, description placeholders)."""
    data = {key: dict(value) for key, value in user_input.items()}
    errors: dict[str, str] = {}
    placeholders: dict[str, str] = {"invalid": ""}

    for season in (SEASON_HALLOWEEN, SEASON_CHRISTMAS, SEASON_NEW_YEAR):
        for key in (CONF_START, CONF_END):
            value = str(data[season].get(key, "")).strip()
            try:
                month, day = parse_day_month(value)
            except ValueError:
                errors[season] = "invalid_day_month"
            else:
                data[season][key] = f"{day:02d}.{month:02d}"

    easter = data[SEASON_EASTER]
    easter[CONF_DAYS_BEFORE] = int(easter[CONF_DAYS_BEFORE])
    easter[CONF_DAYS_AFTER] = int(easter[CONF_DAYS_AFTER])

    dates = str(data[SEASON_BIRTHDAY].get(CONF_DATES) or "").strip()
    _, invalid = parse_birthdays(dates)
    if invalid:
        errors[SEASON_BIRTHDAY] = "invalid_birthdays"
        placeholders["invalid"] = ", ".join(invalid)
    data[SEASON_BIRTHDAY][CONF_DATES] = dates

    for key in data:
        if CONF_COLOR in data[key]:
            data[key][CONF_COLOR] = [int(v) for v in data[key][CONF_COLOR]]

    return data, errors, placeholders


class SaisonThemesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow: one confirmation step, settings live in the options."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm setup."""
        if user_input is not None:
            return self.async_create_entry(
                title="Saison-Themes", data={}, options=DEFAULT_OPTIONS
            )
        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return SaisonThemesOptionsFlow()


class SaisonThemesOptionsFlow(OptionsFlow):
    """Settings: colors, periods and birthdays."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show and save the settings."""
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {"invalid": ""}
        current: dict[str, Any] = dict(self.config_entry.options)
        if user_input is not None:
            data, errors, placeholders = validate_options(user_input)
            if not errors:
                return self.async_create_entry(data=data)
            current = data
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema(current),
            errors=errors,
            description_placeholders=placeholders,
        )
