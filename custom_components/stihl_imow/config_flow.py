"""Config flow for STIHL iMow integration."""
from __future__ import annotations

import datetime
import logging
from typing import Any

from imow.api import IMowApi
from imow.common.exceptions import LoginError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_API_TOKEN,
    CONF_API_TOKEN_EXPIRE_TIME,
    CONF_ENTRY_TITLE,
    CONF_MOWER,
    CONF_MOWER_IDENTIFIER,
    CONF_MOWER_MODEL,
    CONF_MOWER_NAME,
    CONF_MOWER_STATE,
    CONF_MOWER_VERSION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema({"username": str, "password": str})


async def validate_input(
        hass: HomeAssistant,
        data: dict[str, Any]
) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA
    with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    try:
        imow = IMowApi()
        token, expire_time = await imow.get_token(
            data["username"], data["password"], return_expire_time=True
        )
    except LoginError:
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    mowers = []
    for mower in await imow.receive_mowers():
        mowers_state = dict(mower.__dict__)
        del mowers_state["api"]
        mowers.append(
            {
                CONF_MOWER_NAME: mower.name,
                CONF_MOWER_IDENTIFIER: mower.id,
                CONF_MOWER_MODEL: mower.deviceTypeDescription,
                CONF_MOWER_VERSION: mower.softwarePacket,
                CONF_MOWER_STATE: mowers_state,
            }
        )
    await imow.close()
    return {
        CONF_API_TOKEN: token,
        CONF_API_TOKEN_EXPIRE_TIME: datetime.datetime.timestamp(expire_time),
        "user_input": data,
        CONF_MOWER: mowers,
    }


class StihlImowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STIHL iMow."""

    VERSION = 1

    def __init__(self):
        """Initialize config flow."""
        self.data = {}
        self.available_mowers = []
        self.token = None
        self.token_expire = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            self.data = await validate_input(self.hass, user_input)
            self.available_mowers = self.data[CONF_MOWER]
            self.token = self.data[CONF_API_TOKEN]
            self.token_expire = self.data[CONF_API_TOKEN_EXPIRE_TIME]

        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:

            return self.async_create_entry(
                title=CONF_ENTRY_TITLE, data=self.data
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
