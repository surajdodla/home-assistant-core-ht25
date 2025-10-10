"""Hue Weather Adaptive Lighting - small component."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.const import CONF_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

DOMAIN = "hue_weather_adaptive"
SERVICE_APPLY = "apply_weather_mode"

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): str,
        vol.Optional("weather_entity", default="weather.home"): str,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Hue Weather Adaptive service."""

    async def handle_apply(call: ServiceCall) -> None:
        """Service to apply weather-based lighting for a given light."""
        weather_ent = call.data.get("weather_entity", "weather.home")
        light_ent = call.data[CONF_ENTITY_ID]

        weather_state = hass.states.get(weather_ent)
        if not weather_state:
            _LOGGER.warning("Weather entity not found: %s", weather_ent)
            return

        condition = (weather_state.state or "").lower()
        # choose temp (Kelvin) and brightness
        if condition in ("sunny", "clear"):
            temp = 6500
            bright = 255
        elif condition in ("rainy", "pouring"):
            temp = 2700
            bright = 150
        else:
            temp = 4500
            bright = 200

        msg = f"Adaptive Lighting applied for '{condition}' → {temp} K @ {bright} brightness"

        # Create a state entity to track the last action
        hass.states.async_set(
            "hue_weather_adaptive.last_action",
            condition,
            {
                "message": msg,
                "temperature": temp,
                "brightness": bright,
                "light_entity": light_ent,
            },
        )
        _LOGGER.info(msg)

    hass.services.async_register(
        DOMAIN, SERVICE_APPLY, handle_apply, schema=SERVICE_SCHEMA
    )
    _LOGGER.info("Hue Weather Adaptive Mode registered")
    return True
