"""The STIHL iMow integration."""

from __future__ import annotations

import typing

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.typing import ConfigType
from imow.api import IMowApi
from imow.common.exceptions import ApiMaintenanceError, LoginError
from imow.common.mowerstate import MowerState

from .const import (
    CONF_API_TOKEN,
    CONF_API_TOKEN_EXPIRE_TIME,
    CONF_ATTR_EMAIL,
    CONF_ATTR_LANGUAGE,
    CONF_ATTR_PASSWORD,
    CONF_USER_INPUT,
    DOMAIN,
)
from .coordinator import ImowConfigEntry, ImowDataUpdateCoordinator
from .maps import ENTITY_STRIP_OUT_PROPERTIES
from .services import async_setup_services

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.DEVICE_TRACKER,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register integration-wide services once."""
    async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: ImowConfigEntry
) -> bool:
    """Set up STIHL iMow from a config entry."""
    # Dedicated, cookie-isolated session so STIHL's auth/session cookies never
    # leak into HA's shared jar (which would redirect the login to the SPA
    # shell). With auto_cleanup (default), HA detaches/closes it automatically
    # when the config entry is unloaded, so we must not close it ourselves.
    session = async_create_clientsession(hass)

    imow_api = IMowApi(
        aiohttp_session=session,
        email=entry.data[CONF_ATTR_EMAIL],
        password=entry.data[CONF_ATTR_PASSWORD],
        token=entry.data.get(CONF_API_TOKEN),
        lang=entry.data.get(CONF_ATTR_LANGUAGE, "en"),
    )
    try:
        # Reuse the stored token; the wrapper only re-authenticates when the
        # token is missing/expired or a request returns 401.
        await imow_api.get_token()
    except LoginError as err:
        raise ConfigEntryAuthFailed from err
    except ApiMaintenanceError as err:
        raise ConfigEntryNotReady(
            f"STIHL iMow API is unavailable: {err}"
        ) from err

    coordinator = ImowDataUpdateCoordinator(hass, entry, imow_api)
    await coordinator.async_config_entry_first_refresh()

    # Persist a refreshed token so restarts don't force a fresh login.
    _persist_token(hass, entry, imow_api)

    entry.runtime_data = coordinator

    # The stable account id (not the mutable e-mail) is the entry's unique id.
    # Entries created/migrated before this was known are reconciled here, where
    # the account id is available from the fetched mower state.
    account_id = next(
        (str(state.accountId) for state in coordinator.data.values()),
        None,
    )
    if account_id and entry.unique_id != account_id:
        hass.config_entries.async_update_entry(entry, unique_id=account_id)

    await _migrate_entity_unique_ids(hass, entry, set(coordinator.data))
    _migrate_device_identifiers(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ImowConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: ImowConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Allow removing a device only when its mower left the account."""
    coordinator = config_entry.runtime_data
    return not any(
        domain == DOMAIN and str(identifier) in coordinator.data
        for domain, identifier in device_entry.identifiers
    )


async def async_migrate_entry(
    hass: HomeAssistant, entry: ImowConfigEntry
) -> bool:
    """Migrate old config entries to the account-based v3 schema."""
    if entry.version > 3:
        return False

    if entry.version in (1, 2):
        old = entry.data
        if entry.version == 1:
            user_input = old.get(CONF_USER_INPUT, {})
            email = user_input.get("email") or user_input.get("username")
            password = user_input.get("password")
        else:
            email = old.get(CONF_ATTR_EMAIL)
            password = old.get(CONF_ATTR_PASSWORD)
        new_data = {
            CONF_ATTR_EMAIL: email,
            CONF_ATTR_PASSWORD: password,
            CONF_API_TOKEN: old.get(CONF_API_TOKEN),
            CONF_API_TOKEN_EXPIRE_TIME: old.get(CONF_API_TOKEN_EXPIRE_TIME),
            CONF_ATTR_LANGUAGE: old.get(CONF_ATTR_LANGUAGE, "en"),
        }
        hass.config_entries.async_update_entry(
            entry,
            data=new_data,
            version=3,
        )

    return True


async def _migrate_entity_unique_ids(
    hass: HomeAssistant, entry: ImowConfigEntry, mower_ids: set[str]
) -> None:
    """Migrate legacy entity unique ids to the stable scheme.

    Old: ``{mower_id}_{idx}_{property}`` (index-dependent, unstable).
    New: ``{mower_id}_{property}`` (``{mower_id}_tracker`` for the tracker).
    Idempotent: already-migrated ids are left untouched. Handles every mower
    on the account.
    """
    prefixes = {str(mower_id): f"{mower_id}_" for mower_id in mower_ids}

    @callback
    def _migrate(reg_entry: er.RegistryEntry) -> dict[str, str] | None:
        for mower_id, prefix in prefixes.items():
            if not reg_entry.unique_id.startswith(prefix):
                continue
            rest = reg_entry.unique_id.removeprefix(prefix)
            head, _, tail = rest.partition("_")
            if not head.isdigit():
                return None  # already the new scheme
            suffix = tail if tail else "tracker"
            return {"new_unique_id": f"{mower_id}_{suffix}"}
        return None

    await er.async_migrate_entries(hass, entry.entry_id, _migrate)


@callback
def _migrate_device_identifiers(
    hass: HomeAssistant, entry: ImowConfigEntry
) -> None:
    """Reconcile legacy integer device identifiers to the string scheme.

    1.0.x registered the mower device as ``(DOMAIN, <int>)`` while the current
    code uses ``(DOMAIN, <str>)``. Because the identifiers differ, HA would
    otherwise leave the old device empty and create a new one on update. Retype
    the identifier in place, or drop the stale legacy device if the new one was
    already created. Runs before the platforms so entities keep their device.
    The legacy ``int`` identifier only exists at runtime (from `.storage`), so
    the stored value is inspected loosely against the typed ``tuple``.
    """
    dev_reg = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(dev_reg, entry.entry_id):
        normalized: set[tuple[str, str]] = set()
        is_legacy = False
        for domain, identifier in typing.cast(
            "set[tuple[str, object]]", device.identifiers
        ):
            normalized.add((domain, str(identifier)))
            if domain == DOMAIN and not isinstance(identifier, str):
                is_legacy = True
        if not is_legacy:
            continue
        existing = dev_reg.async_get_device(identifiers=normalized)
        if existing is not None and existing.id != device.id:
            dev_reg.async_remove_device(device.id)
        else:
            dev_reg.async_update_device(
                device.id, new_identifiers=normalized
            )


@callback
def _persist_token(
    hass: HomeAssistant, entry: ImowConfigEntry, imow_api: IMowApi
) -> None:
    """Store a rotated token back on the config entry, if it changed."""
    token = imow_api.access_token
    if not token or token == entry.data.get(CONF_API_TOKEN):
        return
    expires = imow_api.token_expires
    hass.config_entries.async_update_entry(
        entry,
        data={
            **entry.data,
            CONF_API_TOKEN: token,
            CONF_API_TOKEN_EXPIRE_TIME: (
                expires.timestamp()
                if expires is not None
                else entry.data.get(CONF_API_TOKEN_EXPIRE_TIME)
            ),
        },
    )


def extract_properties_by_type(
    mower_state: MowerState,
    property_python_type: type,
    negotiate: bool = False,
) -> tuple[dict[str, typing.Any], dict[str, typing.Any]]:
    """Extract Properties used by different Sensors."""
    complex_entities: dict[str, typing.Any] = {}
    entities: dict[str, typing.Any] = {}
    for mower_state_property in mower_state.__dict__:
        if type(mower_state.__dict__[mower_state_property]) in [dict]:
            complex_entities[mower_state_property] = mower_state.__dict__[
                mower_state_property
            ]
        else:
            if mower_state_property not in ENTITY_STRIP_OUT_PROPERTIES:
                if not negotiate:
                    if (
                        type(mower_state.__dict__[mower_state_property])
                        is property_python_type
                    ):
                        entities[mower_state_property] = mower_state.__dict__[
                            mower_state_property
                        ]
                else:
                    if (
                        type(mower_state.__dict__[mower_state_property])
                        is not property_python_type
                    ):
                        entities[mower_state_property] = mower_state.__dict__[
                            mower_state_property
                        ]

    for entity in complex_entities:
        for prop in complex_entities[entity]:
            property_identifier = f"{entity}_{prop}"
            if property_identifier not in ENTITY_STRIP_OUT_PROPERTIES:
                if not negotiate:
                    if (
                        type(complex_entities[entity][prop])
                        is property_python_type
                    ):
                        entities[property_identifier] = complex_entities[
                            entity
                        ][prop]
                else:
                    if (
                        type(complex_entities[entity][prop])
                        is not property_python_type
                    ):
                        entities[property_identifier] = complex_entities[
                            entity
                        ][prop]

    device = {
        "name": mower_state.name,
        "id": mower_state.id,
        "externalId": mower_state.externalId,
        "manufacturer": "STIHL",
        "model": mower_state.deviceTypeDescription,
        "sw_version": mower_state.softwarePacket,
    }
    return entities, device
