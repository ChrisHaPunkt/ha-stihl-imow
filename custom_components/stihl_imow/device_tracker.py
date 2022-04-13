"""Platform for sensor integration."""
import logging

from imow.common.mowerstate import MowerState

from homeassistant import config_entries, core
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.device_tracker.config_entry.TrackerEntity import TrackerEntity

from . import extract_properties_by_type
from .const import DOMAIN, ATTR_COORDINATOR, ATTR_SWITCH
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

    mower_state: MowerState = config[ATTR_COORDINATOR].data
    binary_sensor_entities = {}
    entities, device = extract_properties_by_type(mower_state, bool)

    for entity in entities:
        if not IMOW_SENSORS_MAP[entity][ATTR_SWITCH]:
            binary_sensor_entities[entity] = entities[entity]
    async_add_entities(
        ImowBinarySensorEntity(coordinator, device, idx, mower_state_property)
        for idx, mower_state_property in enumerate(binary_sensor_entities)
    )


"""Device tracker platform that adds support for OwnTracks over MQTT."""
from homeassistant.components.device_tracker import (
    ATTR_BATTERY,
    ATTR_GPS,
    ATTR_GPS_ACCURACY,
    ATTR_LOCATION_NAME,
)
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SOURCE_TYPE_GPS
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    ATTR_DEVICE_ID,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    ATTR_ALTITUDE,
    ATTR_COURSE,
    ATTR_DEVICE_NAME,
    ATTR_SPEED,
    ATTR_VERTICAL_ACCURACY,
    SIGNAL_LOCATION_UPDATE,
)

ATTR_KEYS = (ATTR_ALTITUDE, ATTR_COURSE, ATTR_SPEED, ATTR_VERTICAL_ACCURACY)


class MobileAppEntity(ImowBaseEntity, TrackerEntity, RestoreEntity):
    """Represent a tracked device."""

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._entry.data[ATTR_DEVICE_ID]

    @property
    def location_accuracy(self):
        """Return the gps accuracy of the device."""
        return self._data.get(ATTR_GPS_ACCURACY)

    @property
    def latitude(self):
        """Return latitude value of the device."""
        if (gps := self._data.get(ATTR_GPS)) is None:
            return None

        return gps[0]

    @property
    def longitude(self):
        """Return longitude value of the device."""
        if (gps := self._data.get(ATTR_GPS)) is None:
            return None

        return gps[1]

    @property
    def location_name(self):
        """Return a location name for the current location of the device."""
        if location_name := self._data.get(ATTR_LOCATION_NAME):
            return location_name
        return None

    @property
    def name(self):
        """Return the name of the device."""
        return self._entry.data[ATTR_DEVICE_NAME]

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    async def async_added_to_hass(self):
        """Call when entity about to be added to Home Assistant."""
        await super().async_added_to_hass()
        self._dispatch_unsub = async_dispatcher_connect(
            self.hass,
            SIGNAL_LOCATION_UPDATE.format(self._entry.entry_id),
            self.update_data,
        )

        # Don't restore if we got set up with data.
        if self._data is not None:
            return

        if (state := await self.async_get_last_state()) is None:
            self._data = {}
            return

        attr = state.attributes
        data = {
            ATTR_GPS: (attr.get(ATTR_LATITUDE), attr.get(ATTR_LONGITUDE)),
            ATTR_GPS_ACCURACY: attr.get(ATTR_GPS_ACCURACY),
            ATTR_BATTERY: attr.get(ATTR_BATTERY_LEVEL),
        }
        data.update({key: attr[key] for key in attr if key in ATTR_KEYS})
        self._data = data

    async def async_will_remove_from_hass(self):
        """Call when entity is being removed from hass."""
        await super().async_will_remove_from_hass()

        if self._dispatch_unsub:
            self._dispatch_unsub()
            self._dispatch_unsub = None

    @callback
    def update_data(self, data):
        """Mark the device as seen."""
        self._data = data
        self.async_write_ha_state()
