"""Platform for sensor integration."""

import logging
from typing import Any

from homeassistant import core
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from imow.common.mowerstate import MowerState

from . import extract_properties_by_type
from .const import (
    ATTR_LONG,
    ATTR_SHORT,
    ATTR_STATE_CLASS,
    ATTR_TYPE,
    ATTR_UOM,
)
from .coordinator import ImowConfigEntry, ImowDataUpdateCoordinator
from .entity import ImowBaseEntity, add_mower_entities
from .maps import IMOW_SENSORS_MAP

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: ImowConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    coordinator = config_entry.runtime_data

    def _build(
        mower_id: str, mower_state: MowerState
    ) -> list["ImowSensorEntity"]:
        properties, device = extract_properties_by_type(
            mower_state, bool, negotiate=True  # all, but bool
        )
        return [
            ImowSensorEntity(coordinator, mower_id, device, prop)
            for prop in properties
            if prop in IMOW_SENSORS_MAP
        ]

    config_entry.async_on_unload(
        add_mower_entities(coordinator, async_add_entities, _build)
    )


class ImowSensorEntity(ImowBaseEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(
        self,
        coordinator: ImowDataUpdateCoordinator,
        mower_id: str,
        device_info: dict[str, Any],
        mower_state_property: str,
    ) -> None:
        """Set device_class, unit and state_class from the sensor map."""
        super().__init__(
            coordinator, mower_id, device_info, mower_state_property
        )
        info = IMOW_SENSORS_MAP.get(mower_state_property, {})
        self._attr_device_class = info.get(ATTR_TYPE)
        self._attr_native_unit_of_measurement = info.get(ATTR_UOM)
        self._attr_state_class = info.get(ATTR_STATE_CLASS)

    @property
    def native_value(self) -> Any:
        """Return the native value of the sensor."""
        return self.get_value_from_mowerstate()

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes of the device."""
        if self.property_name == "machineState":
            return {
                ATTR_SHORT: self.mowerstate.stateMessage[ATTR_SHORT],
                ATTR_LONG: self.mowerstate.stateMessage[ATTR_LONG],
            }
        return None
