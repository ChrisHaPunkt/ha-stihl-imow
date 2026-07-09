"""Platform for sensor integration."""

import logging

from homeassistant import core
from homeassistant.components.sensor import SensorEntity
from imow.common.mowerstate import MowerState

from . import extract_properties_by_type
from .const import (
    ATTR_LONG,
    ATTR_SHORT,
    ATTR_STATE_CLASS,
    ATTR_TYPE,
    ATTR_UOM,
)
from .coordinator import ImowConfigEntry
from .entity import ImowBaseEntity
from .maps import IMOW_SENSORS_MAP

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: ImowConfigEntry,
    async_add_entities,
):
    """Add sensors for passed config_entry in HA."""
    coordinator = config_entry.runtime_data
    mower_state: MowerState = coordinator.data

    entities, device = extract_properties_by_type(
        mower_state, bool, negotiate=True  # all, but bool
    )

    async_add_entities(
        ImowSensorEntity(coordinator, device, idx, mower_state_property)
        for idx, mower_state_property in enumerate(entities)
        if mower_state_property in IMOW_SENSORS_MAP
    )


class ImowSensorEntity(ImowBaseEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, device_info, idx, mower_state_property):
        """Set device_class, unit and state_class from the sensor map."""
        super().__init__(coordinator, device_info, idx, mower_state_property)
        info = IMOW_SENSORS_MAP.get(mower_state_property, {})
        self._attr_device_class = info.get(ATTR_TYPE)
        self._attr_native_unit_of_measurement = info.get(ATTR_UOM)
        self._attr_state_class = info.get(ATTR_STATE_CLASS)

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.get_value_from_mowerstate()

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        if self.property_name == "machineState":
            return {
                ATTR_SHORT: self.mowerstate.stateMessage[ATTR_SHORT],
                ATTR_LONG: self.mowerstate.stateMessage[ATTR_LONG],
            }
        return None
