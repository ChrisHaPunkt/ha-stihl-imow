"""Platform for sensor integration."""

import logging

from homeassistant import core
from homeassistant.components.switch import SwitchEntity
from homeassistant.exceptions import HomeAssistantError
from imow.common.mowerstate import MowerState

from . import extract_properties_by_type
from .const import ATTR_ID, ATTR_SWITCH
from .coordinator import ImowConfigEntry
from .entity import ImowBaseEntity
from .maps import IMOW_SENSORS_MAP

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: ImowConfigEntry,
    async_add_entities,
):
    """Add sensors for passed config_entry in HA."""
    coordinator = config_entry.runtime_data
    switch_entities = {}
    mower_state: MowerState = coordinator.data
    entities, device = extract_properties_by_type(mower_state, bool)

    for entity in entities:
        if (
            entity in IMOW_SENSORS_MAP
            and IMOW_SENSORS_MAP[entity][ATTR_SWITCH]
        ):
            switch_entities[entity] = entities[entity]

    async_add_entities(
        ImowSwitchSensorEntity(coordinator, device, idx, mower_state_property)
        for idx, mower_state_property in enumerate(switch_entities)
    )


class ImowSwitchSensorEntity(ImowBaseEntity, SwitchEntity):
    """Representation of a switch."""

    def __init__(self, coordinator, device_info, idx, mower_state_property):
        """Override the BaseEntity with Switch Entity content."""
        super().__init__(coordinator, device_info, idx, mower_state_property)
        self.api = self.coordinator.data.imow

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return bool(self.get_value_from_mowerstate())

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        try:
            await self.api.update_setting(
                self.key_device_infos[ATTR_ID], self.property_name, True
            )
        except Exception as err:
            raise HomeAssistantError(
                f"Error communicating with API: {err}"
            ) from err
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        try:
            await self.api.update_setting(
                self.key_device_infos[ATTR_ID], self.property_name, False
            )
        except Exception as err:
            raise HomeAssistantError(
                f"Error communicating with API: {err}"
            ) from err
        await self.coordinator.async_request_refresh()
