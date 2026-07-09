"""BaseEntity for iMow entities."""

from __future__ import annotations

import re

from homeassistant.const import ATTR_MANUFACTURER
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from imow.common.mowerstate import MowerState

from .const import (
    ATTR_ICON,
    ATTR_ID,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_SW_VERSION,
    DOMAIN,
)
from .maps import IMOW_SENSORS_MAP


def to_translation_key(property_name: str) -> str:
    """Convert a mower property name into a snake_case translation key."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", property_name).lower()


class ImowBaseEntity(CoordinatorEntity):
    """Base entity for a STIHL iMow mower property."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device, idx, mower_state_property):
        """Initialize the entity."""
        super().__init__(coordinator)
        self.key_device_infos = device
        self.property_name = mower_state_property
        self._attr_translation_key = to_translation_key(mower_state_property)
        self._attr_unique_id = f"{device[ATTR_ID]}_{mower_state_property}"
        icon = IMOW_SENSORS_MAP.get(mower_state_property, {}).get(ATTR_ICON)
        if icon:
            self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(device[ATTR_ID]))},
            name=device[ATTR_NAME],
            manufacturer=device[ATTR_MANUFACTURER],
            model=device[ATTR_MODEL],
            sw_version=device[ATTR_SW_VERSION],
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    @property
    def mowerstate(self) -> MowerState:
        """Return the mower state from the coordinator."""
        return self.coordinator.data

    def get_value_from_mowerstate(self):
        """Return the value for this entity's property.

        A property name containing ``_`` denotes a nested value
        (e.g. ``status_chargeLevel`` -> ``status["chargeLevel"]``).
        """
        if "_" in self.property_name:
            outer, inner = self.property_name.split("_", 1)
            return getattr(self.mowerstate, outer)[inner]
        return getattr(self.mowerstate, self.property_name)
