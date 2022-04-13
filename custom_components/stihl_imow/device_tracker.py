"""Device tracker platform that adds support for OwnTracks over MQTT."""
import logging

from homeassistant import config_entries, core
from homeassistant.components.device_tracker import (
    ATTR_GPS_ACCURACY,
)
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SOURCE_TYPE_GPS
from imow.common.mowerstate import MowerState

from . import extract_properties_by_type
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
    entities, device = extract_properties_by_type(mower_state, bool)

    async_add_entities(
        [ImowDeviceTrackerEntity(coordinator, device, 999, "lat_long")]
    )


class ImowDeviceTrackerEntity(ImowBaseEntity, TrackerEntity):
    """Represent a tracked device."""

    @property
    def location_accuracy(self):
        """Return the gps accuracy of the device."""
        return self._data.get(ATTR_GPS_ACCURACY)

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

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS
