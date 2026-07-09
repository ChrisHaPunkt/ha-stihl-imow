"""Diagnostics support for the STIHL iMow integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import (
    ATTR_IMOW,
    CONF_API_TOKEN,
    CONF_API_TOKEN_EXPIRE_TIME,
    CONF_ATTR_EMAIL,
    CONF_ATTR_PASSWORD,
)
from .coordinator import ImowConfigEntry

TO_REDACT = {
    CONF_ATTR_EMAIL,
    CONF_ATTR_PASSWORD,
    CONF_API_TOKEN,
    CONF_API_TOKEN_EXPIRE_TIME,
    "accountId",
    "externalId",
    "coordinateLatitude",
    "coordinateLongitude",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ImowConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry, with sensitive data redacted."""
    coordinator = entry.runtime_data
    mower_state = dict(coordinator.data.__dict__)
    # Drop the IMowApi back-reference (not serializable / holds credentials).
    mower_state.pop(ATTR_IMOW, None)

    return {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "mower_state": async_redact_data(mower_state, TO_REDACT),
    }
