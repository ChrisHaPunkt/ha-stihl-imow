"""Device tracker platform that adds support for OwnTracks over MQTT."""
import logging

from homeassistant import config_entries, core
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SOURCE_TYPE_GPS
from imow.common.mowerstate import MowerState

from .const import DOMAIN, ATTR_COORDINATOR, ATTR_NAME
from .entity import ImowBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Add sensors for passed config_entry in HA."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][ATTR_COORDINATOR]

    mower_state: MowerState = config[ATTR_COORDINATOR].data

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
    """Represent a tracked device."""

    def __init__(self, coordinator, device_info, idx, mower_state_property):
        """Override the BaseEntity with DeviceTracker Sensor content."""
        super().__init__(coordinator, device_info, idx, mower_state_property)

    @property
    def source_type(self):
        """Return the gps accuracy of the device."""
        return SOURCE_TYPE_GPS

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

    @property
    def name(self):
        """Return the name of the device."""
        return self.key_device_infos[ATTR_NAME]
