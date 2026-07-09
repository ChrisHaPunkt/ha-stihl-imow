"""Services for the STIHL iMow integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import (
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from imow.api import IMowApi
from imow.common.actions import IMowActions
from imow.common.mowerstate import MowerState

from .const import DOMAIN

IMOW_INTENT_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Optional("mower_device"): str,
            vol.Optional("mower_name"): str,
            vol.Optional("startpoint"): vol.Any(str, int),
            vol.Optional("starttime"): str,
            vol.Optional("endtime"): str,
            vol.Optional("duration"): vol.Any(str, int),
            vol.Required("action"): str,
        },
        cv.has_at_least_one_key("mower_device", "mower_name"),
    )
)

_LOGGER = logging.getLogger(__package__)

SERVICE_INTENT = "intent"


def async_setup_services(hass: HomeAssistant) -> None:
    """Register integration-wide services once."""

    async def async_call_intent_service(service_call: ServiceCall) -> None:
        await _async_intent_service(hass, service_call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_INTENT,
        async_call_intent_service,
        schema=IMOW_INTENT_SCHEMA,
    )


def _get_api(hass: HomeAssistant) -> IMowApi:
    """Return an authenticated IMowApi from a loaded config entry."""
    for entry in hass.config_entries.async_loaded_entries(DOMAIN):
        return entry.runtime_data.api
    raise ServiceValidationError("STIHL iMow is not set up")


async def _async_intent_service(
    hass: HomeAssistant, service_call: ServiceCall
) -> None:
    """Call the correct iMow action."""
    device_registry = dr.async_get(hass)

    if "mower_device" in service_call.data:
        mower_name = device_registry.async_get(
            device_id=service_call.data["mower_device"]
        ).name
    else:
        mower_name = service_call.data.get("mower_name")

    duration = (
        str(service_call.data["duration"])
        if "duration" in service_call.data
        else None
    )
    startpoint = (
        str(service_call.data["startpoint"])
        if "startpoint" in service_call.data
        else None
    )
    starttime = service_call.data.get("starttime")
    endtime = service_call.data.get("endtime")

    api = _get_api(hass)
    try:
        action = IMowActions(service_call.data["action"])
        if not mower_name:
            raise ServiceValidationError("No mower specified")
        upstream_mower_state: MowerState = await api.receive_mower_by_name(
            mower_name
        )
        await upstream_mower_state.intent(
            imow_action=action,
            startpoint=startpoint,
            duration=duration,
            starttime=starttime,
            endtime=endtime,
        )
        _LOGGER.debug("Doing %s with %s", action, upstream_mower_state.name)
    except LookupError as err:
        raise HomeAssistantError(str(err)) from err
    except ValueError as err:
        raise ServiceValidationError(str(err)) from err
