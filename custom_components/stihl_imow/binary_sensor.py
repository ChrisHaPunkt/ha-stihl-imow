"""Platform for sensor integration."""

import logging

from homeassistant import core
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from imow.common.mowerstate import MowerState

from . import extract_properties_by_type
from .const import ATTR_SWITCH
from .coordinator import ImowConfigEntry
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
    ) -> list["ImowBinarySensorEntity"]:
        properties, device = extract_properties_by_type(mower_state, bool)
        return [
            ImowBinarySensorEntity(coordinator, mower_id, device, prop)
            for prop in properties
            if prop in IMOW_SENSORS_MAP
            and not IMOW_SENSORS_MAP[prop][ATTR_SWITCH]
        ]

    config_entry.async_on_unload(
        add_mower_entities(coordinator, async_add_entities, _build)
    )


class ImowBinarySensorEntity(ImowBaseEntity, BinarySensorEntity):
    """Representation of a binary sensor."""

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return bool(self.get_value_from_mowerstate())
