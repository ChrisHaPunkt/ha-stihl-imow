"""The STIHL iMow integration."""
from __future__ import annotations

from imow.api import IMowApi

from homeassistant.config_entries import ConfigEntry, _LOGGER
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
import asyncio
import logging
from homeassistant.core import callback

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS = [
    "sensor",
    "binary_sensor"]


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up STIHL iMow from a config entry."""
    # TODO Store an API object for your platforms to access

    session = async_get_clientsession(hass)
    imow_api = IMowApi(
        aiohttp_session=session,
        email=entry.data["user_input"]["username"],
        password=entry.data["user_input"]["password"],
    )
    await imow_api.get_token()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"mower": entry.data["mower"][0], "credentials": entry.data["user_input"],
                                         "api": imow_api}
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


_LOGGER = logging.getLogger(__name__)


@asyncio.coroutine
def async_setup(hass, config):
    """Set up the an async service example component."""

    @callback
    def my_service(call):
        """My first service."""
        _LOGGER.info('Received data', call.data)

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, 'demo', my_service)

    # Return boolean to indicate that initialization was successfully.
    return True


async def async_unload_entry(
        hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
