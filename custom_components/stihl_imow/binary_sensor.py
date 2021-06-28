"""Platform for sensor integration."""
import logging
from datetime import timedelta

import async_timeout
from imow.api import IMowApi
from imow.common.exceptions import LoginError, ApiMaintenanceError
from imow.common.mowerstate import MowerState

from homeassistant import config_entries, core
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    TIME_SECONDS,
    PERCENTAGE,
    TEMP_CELSIUS,
    STATE_ON,
    STATE_OFF,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import (
    async_get_clientsession,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from .const import (
    CONF_API_TOKEN,
    CONF_MOWER,
    CONF_MOWER_IDENTIFIER,
    CONF_MOWER_MODEL,
    DOMAIN,
    NAME_PREFIX,
    API_UPDATE_INTERVALL_SECONDS,
)
from .maps import ENTITY_STRIP_OUT_PROPERTIES
from aiohttp import ClientResponseError

INFO_ATTR = {}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Add sensors for passed config_entry in HA."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    session = async_get_clientsession(hass)
    mower = config[CONF_MOWER][0]
    imow = IMowApi(
        aiohttp_session=session,
        email=config["user_input"]["username"],
        password=config["user_input"]["password"],
    )

    token = await imow.get_token()

    async def async_update_data():
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        entities: dict = {}
        complex_entities: dict = {}
        binary_sensor_entities = {}
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):

                mower_state = await imow.receive_mower_by_id(
                    mower["mower_id"]
                )
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
                return entities

        except ClientResponseError as err:
            # TODO Use token above, reauth with credentials, store new token in config if successful, else raise below
            _LOGGER.warning(f"Config token raises {err.status}")

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
        ImowBinarySensorEntity(coordinator, idx, mower_state_property)
        for idx, mower_state_property in enumerate(coordinator.data)
    )


class ImowBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, idx, mower_state_property):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.idx = idx

        self.mower_conf = coordinator.config_entry.data["mower"][0]
        self.property_name = mower_state_property
        self._attr_is_on = coordinator.data[self.property_name]

    @property
    def state(self) -> StateType:
        """Return the state of the binary sensor."""
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def device_info(self):
        """Provide info for device registration."""
        return {
            "identifiers": {
                # Serial numbers are unique identifiers
                # within a specific domain
                (
                    DOMAIN,
                    self.mower_conf["mower_id"],
                ),
            },
            "name": self.mower_conf["name"],
            "manufacturer": "STIHL",
            "model": self.mower_conf[CONF_MOWER_MODEL],
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.mower_conf['name']} {self.property_name}"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{self.mower_conf['mower_id']}_{self.idx}_{self.property_name}"
