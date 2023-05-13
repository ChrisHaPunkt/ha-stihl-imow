"""Platform for sensor integration."""
import logging

from homeassistant import config_entries, core
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers.update_coordinator import UpdateFailed
from imow.common.mowerstate import MowerState

from . import extract_properties_by_type
from .const import ATTR_COORDINATOR, ATTR_ID, ATTR_SWITCH, DOMAIN
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

    coordinator = hass.data[DOMAIN][config_entry.entry_id][ATTR_COORDINATOR]
    switch_entities = {}
    mower_state: MowerState = config[ATTR_COORDINATOR].data
    entities, device = extract_properties_by_type(mower_state, bool)

    for entity in entities:
        if IMOW_SENSORS_MAP[entity][ATTR_SWITCH]:
            switch_entities[entity] = entities[entity]

    async_add_entities(
        ImowSwitchSensorEntity(coordinator, device, idx, mower_state_property)
        for idx, mower_state_property in enumerate(switch_entities)
    )


class ImowSwitchSensorEntity(ImowBaseEntity, SwitchEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, device_info, idx, mower_state_property):
        """Override the BaseEntity with Switch Entity content."""
        super().__init__(coordinator, device_info, idx, mower_state_property)
        self.api = self.coordinator.data.imow

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return bool(self.get_value_from_mowerstate())

    @property
    def state(self):
        """Return the state of the sensor."""
        return (
            STATE_ON if bool(self.get_value_from_mowerstate()) else STATE_OFF
        )

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        try:
            await self.api.update_setting(
                self.key_device_infos["id"], self.property_name, True
            )
            self._attr_is_on = True
            self._attr_state = STATE_ON
            await self.coordinator.async_request_refresh()

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        try:
            await self.api.update_setting(
                self.key_device_infos[ATTR_ID], self.property_name, False
            )

            self._attr_is_on = False
            self._attr_state = STATE_OFF
            await self.coordinator.async_request_refresh()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
