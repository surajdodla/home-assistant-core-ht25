"""Tests for hue_weather_adaptive component."""

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

SERVICE = "hue_weather_adaptive.apply_weather_mode"


async def test_service_creates_notification(hass: HomeAssistant) -> None:
    """Test service creates a state entity when applied."""
    # Set up the component
    assert await async_setup_component(hass, "hue_weather_adaptive", {})

    # Prepare fake weather
    hass.states.async_set("weather.home", "rainy")
    # call service
    await hass.services.async_call(
        "hue_weather_adaptive",
        "apply_weather_mode",
        {"entity_id": "light.test", "weather_entity": "weather.home"},
        blocking=True,
    )
    await hass.async_block_till_done()

    # Check that the state entity was created
    state = hass.states.get("hue_weather_adaptive.last_action")
    assert state is not None
    assert state.state == "rainy"
    assert "rainy" in state.attributes.get("message", "")
