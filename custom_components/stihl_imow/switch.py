"""Platform for sensor integration."""
import logging
from datetime import timedelta

import async_timeout
from aiohttp import ClientResponseError
from homeassistant import config_entries, core
from homeassistant.components.switch import SwitchEntity
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from imow.common.exceptions import ApiMaintenanceError

from . import extract_properties_by_type
from .const import (
    CONF_MOWER,
    DOMAIN,
    API_UPDATE_INTERVALL_SECONDS,
)
from .entity import ImowBaseEntity
from .maps import IMOW_SENSORS_MAP

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
        switch_entities = {}
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):

                mower_state = await imow.receive_mower_by_id(mower_id)
                del mower_state.__dict__["imow"]

                entities, device = extract_properties_by_type(
                    mower_state, bool
                )

                for entity in entities:
                    if IMOW_SENSORS_MAP[entity]["switch"]:
                        switch_entities[entity] = entities[entity]

                return device, switch_entities

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
        name="imow_switch_entity",
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
        ImowSwitchSensorEntity(
            coordinator, coordinator.data[0], idx, mower_state_property
        )
        for idx, mower_state_property in enumerate(coordinator.data[1])
    )


class ImowSwitchSensorEntity(ImowBaseEntity, SwitchEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, device_info, idx, mower_state_property):
        """Override the BaseEntity with Switch Entity content."""
        super().__init__(coordinator, device_info, idx, mower_state_property)
        self._attr_is_on = self.sensor_data[self.property_name]

    @property
    def is_on(self) -> bool:
        """State of the entity."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        pass

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        pass
