"""The STIHL iMow integration."""
from __future__ import annotations

from imow.api import IMowApi

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .services import async_setup_services

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS = ["sensor", "binary_sensor"]


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
    await imow_api.get_token(force_reauth=True)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "mower": entry.data["mower"][0],
        "credentials": entry.data["user_input"],
        "api": imow_api,
    }
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    await async_setup_services(hass, entry)
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
