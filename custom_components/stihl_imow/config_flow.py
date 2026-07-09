"""Config flow for STIHL iMow integration."""

from __future__ import annotations

import datetime
import logging
from collections.abc import Mapping
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from imow.api import IMowApi
from imow.common.exceptions import ApiMaintenanceError, LoginError

from .const import (
    API_DEFAULT_LANGUAGE,
    CONF_API_TOKEN,
    CONF_API_TOKEN_EXPIRE_TIME,
    CONF_ATTR_EMAIL,
    CONF_ATTR_LANGUAGE,
    CONF_ATTR_PASSWORD,
    CONF_MOWER_IDENTIFIER,
    CONF_MOWER_MODEL,
    CONF_MOWER_NAME,
    CONF_MOWER_VERSION,
    DOMAIN,
)
from .maps import LANGUAGES

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ATTR_EMAIL): cv.string,
        vol.Required(CONF_ATTR_PASSWORD): cv.string,
        vol.Optional(
            CONF_ATTR_LANGUAGE, default=API_DEFAULT_LANGUAGE
        ): vol.In([e.value for e in LANGUAGES]),
    }
)
STEP_REAUTH_SCHEMA = vol.Schema({vol.Required(CONF_ATTR_PASSWORD): cv.string})


async def validate_input(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate credentials and return the config-entry payload.

    ``data`` must contain the email, password, and a language *code* (enum
    name, e.g. ``"en"``). The wrapper uses its own cookie-isolated session for
    this transient check, which is closed again afterwards.
    """
    imow = IMowApi(
        email=data[CONF_ATTR_EMAIL],
        password=data[CONF_ATTR_PASSWORD],
    )
    try:
        token, expire_time = await imow.get_token(
            force_reauth=True, return_expire_time=True
        )
        mowers = await imow.receive_mowers()
    except LoginError as err:
        raise InvalidAuth from err
    except ApiMaintenanceError as err:
        raise CannotConnect from err
    finally:
        await imow.close()

    if not mowers:
        raise CannotConnect

    mower = mowers[0]
    entry_data = {
        CONF_ATTR_EMAIL: data[CONF_ATTR_EMAIL],
        CONF_ATTR_PASSWORD: data[CONF_ATTR_PASSWORD],
        CONF_API_TOKEN: token,
        CONF_API_TOKEN_EXPIRE_TIME: datetime.datetime.timestamp(expire_time),
        CONF_MOWER_IDENTIFIER: mower.id,
        CONF_MOWER_NAME: mower.name,
        CONF_MOWER_MODEL: mower.deviceTypeDescription,
        CONF_MOWER_VERSION: mower.softwarePacket,
        CONF_ATTR_LANGUAGE: data.get(CONF_ATTR_LANGUAGE, "en"),
    }
    return {
        "mower_id": str(mower.id),
        "title": mower.name,
        "data": entry_data,
    }


class StihlImowConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STIHL iMow."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            payload = dict(user_input)
            # Store the language *code* (enum name), not the display value.
            payload[CONF_ATTR_LANGUAGE] = LANGUAGES(
                payload.get(CONF_ATTR_LANGUAGE, API_DEFAULT_LANGUAGE)
            ).name
            try:
                info = await validate_input(self.hass, payload)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["mower_id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info["title"], data=info["data"]
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauth with a new password for the same account."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()
        if user_input is not None:
            payload = {
                **reauth_entry.data,
                CONF_ATTR_PASSWORD: user_input[CONF_ATTR_PASSWORD],
            }
            try:
                info = await validate_input(self.hass, payload)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["mower_id"])
                self._abort_if_unique_id_mismatch(reason="wrong_account")
                return self.async_update_reload_and_abort(
                    reauth_entry, data_updates=info["data"]
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_SCHEMA,
            errors=errors,
            description_placeholders={
                "email": reauth_entry.data[CONF_ATTR_EMAIL]
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
