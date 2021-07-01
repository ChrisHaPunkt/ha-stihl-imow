"""Platform for sensor integration."""
import logging
from datetime import timedelta

import async_timeout
from aiohttp import ClientResponseError
from homeassistant import config_entries, core
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import (
    STATE_ON,
    STATE_OFF,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from imow.common.exceptions import ApiMaintenanceError

from .const import (
    CONF_MOWER,
    DOMAIN,
    API_UPDATE_INTERVALL_SECONDS,
)
from .entity import ImowBaseEntity
from .maps import ENTITY_STRIP_OUT_PROPERTIES, IMOW_SENSORS_MAP

INFO_ATTR = {}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Add sensors for passed config_entry in HA."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    mower_id = config[CONF_MOWER]["mower_id"]
    imow = config["api"]

    async def async_update_data():
        """
        Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        complex_entities: dict = {}
        binary_sensor_entities = {}
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):

                mower_state = await imow.receive_mower_by_id(mower_id)
                del mower_state.__dict__["imow"]

                for mower_state_property in mower_state.__dict__:
                    if type(
                        mower_state.__dict__[mower_state_property]
                    ) in [dict]:
                        complex_entities[
                            mower_state_property
                        ] = mower_state.__dict__[mower_state_property]
                    else:
                        if (
                            mower_state_property
                            not in ENTITY_STRIP_OUT_PROPERTIES
                        ):
                            if (
                                type(
                                    mower_state.__dict__[
                                        mower_state_property
                                    ]
                                )
                                is bool
                            ):
                                binary_sensor_entities[
                                    mower_state_property
                                ] = mower_state.__dict__[
                                    mower_state_property
                                ]

                for entity in complex_entities:
                    for prop in complex_entities[entity]:
                        property_identifier = f"{entity}_{prop}"
                        if (
                            property_identifier
                            not in ENTITY_STRIP_OUT_PROPERTIES
                        ):
                            if (
                                type(complex_entities[entity][prop])
                                is bool
                            ):
                                binary_sensor_entities[
                                    property_identifier
                                ] = complex_entities[entity][prop]

                entities = binary_sensor_entities
                device = {
                    "name": mower_state.name,
                    "id": mower_state.id,
                    "externalId": mower_state.externalId,
                    "manufacturer": "STIHL",
                    "model": mower_state.deviceTypeDescription,
                    "sw_version": mower_state.softwarePacket,
                }
                return device, entities

        except ClientResponseError as err:

            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except ApiMaintenanceError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="imow_binarysensor",
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=API_UPDATE_INTERVALL_SECONDS),
    )

    #
    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        ImowBinarySensorEntity(
            coordinator, coordinator.data[0], idx, mower_state_property
        )
        for idx, mower_state_property in enumerate(coordinator.data[1])
    )


class ImowBinarySensorEntity(ImowBaseEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.sensor_data[1][self.property_name]

    @property
    def state(self) -> StateType:
        """Return the state of the binary sensor."""
        return STATE_ON if self.sensor_data[1][self.property_name] else STATE_OFF


