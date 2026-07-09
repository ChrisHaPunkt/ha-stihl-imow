"""Device tracker platform that adds support for OwnTracks over MQTT."""

import logging

from homeassistant import core
from homeassistant.components.device_tracker import SourceType, TrackerEntity
from imow.common.mowerstate import MowerState

from .const import ATTR_ID
from .coordinator import ImowConfigEntry
from .entity import ImowBaseEntity

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

    device = {
        "name": mower_state.name,
        "id": mower_state.id,
        "externalId": mower_state.externalId,
        "manufacturer": "STIHL",
        "model": mower_state.deviceTypeDescription,
        "sw_version": mower_state.softwarePacket,
    }

    async_add_entities(
        [ImowDeviceTrackerEntity(coordinator, device, 99999, "")]
    )


class ImowDeviceTrackerEntity(TrackerEntity, ImowBaseEntity):
    """Represent a tracked mower (the device's main feature)."""

    _attr_name = None

    def __init__(self, coordinator, device_info, idx, mower_state_property):
        """Override the BaseEntity with DeviceTracker content."""
        super().__init__(coordinator, device_info, idx, mower_state_property)
        # Main feature of the device: no own name, stable unique id.
        self._attr_translation_key = None
        self._attr_unique_id = f"{device_info[ATTR_ID]}_tracker"

    @property
    def source_type(self):
        """Return the gps accuracy of the device."""
        return SourceType.GPS

    @property
    def latitude(self):
        """Return latitude value of the device."""
        if (gpsLat := getattr(self.mowerstate, "coordinateLatitude")) is None:
            return None

        return gpsLat

    @property
    def longitude(self):
        """Return longitude value of the device."""
        if (
            gpsLong := getattr(self.mowerstate, "coordinateLongitude")
        ) is None:
            return None

        return gpsLong
