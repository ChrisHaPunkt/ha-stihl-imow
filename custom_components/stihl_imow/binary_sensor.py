"""Platform for sensor integration."""
import logging

from imow.common.mowerstate import MowerState

from homeassistant import config_entries, core
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import STATE_OFF, STATE_ON

from . import extract_properties_by_type
from .const import DOMAIN
from .entity import ImowBaseEntity
from .maps import IMOW_SENSORS_MAP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Add sensors for passed config_entry in HA."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    mower_state: MowerState = config["coordinator"].data
    binary_sensor_entities = {}
    entities, device = extract_properties_by_type(mower_state, bool)

    for entity in entities:
        if not IMOW_SENSORS_MAP[entity]["switch"]:
            binary_sensor_entities[entity] = entities[entity]
    async_add_entities(
        ImowBinarySensorEntity(coordinator, device, idx, mower_state_property)
        for idx, mower_state_property in enumerate(binary_sensor_entities)
    )


class ImowBinarySensorEntity(ImowBaseEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        return STATE_ON if bool(self.get_value_from_mowerstate()) else STATE_OFF
