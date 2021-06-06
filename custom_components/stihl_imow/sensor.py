"""Platform for sensor integration."""
from typing import Any, Dict, List

from homeassistant import config_entries, core
from homeassistant.const import TIME_SECONDS, PERCENTAGE
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from imow.api import IMowApi
from imow.common.mowerstate import MowerState
from imow.common.mowertask import MowerTask

from .const import (
    CONF_API_TOKEN,
    CONF_MOWER,
    CONF_MOWER_IDENTIFIER,
    CONF_MOWER_MODEL,
    CONF_MOWER_NAME,
    CONF_MOWER_STATE,
    DOMAIN,
    NAME_PREFIX,
)

INFO_ATTR = {}


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Add sensors for passed config_entry in HA."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    session = async_get_clientsession(hass)
    imow = IMowApi(token=config[CONF_API_TOKEN], aiohttp_session=session)
    entities: List[ImowBaseEntity] = []
    for mower in config[CONF_MOWER]:
        info_entity = ImowInfoEntity(imow, mower)

        entities.append(ImowStateEntity(imow, mower))
        entities.append(info_entity)
        entities.append(ImowInfoChildEntity("CoordinateLatitude", info_entity))
        entities.append(ImowStatisticsEntity(imow, mower))
    async_add_entities(entities, update_before_add=True)


class ImowBaseEntity(Entity):
    """Representation of a Sensor."""

    def __init__(self, imow: IMowApi, mower: dict):
        """Initialize the sensor."""
        super().__init__()
        self.imow = imow
        self.mower_id = mower[CONF_MOWER_IDENTIFIER]
        self.mower_configflow = mower
        self._state = None
        self.attrs: Dict[str, Any] = {}

    @property
    def device_info(self):
        """Provide info for device registration."""
        return {
            "identifiers": {
                # Serial numbers are unique identifiers
                # within a specific domain
                (DOMAIN, self.mower_configflow[CONF_MOWER_STATE]["id"]),
            },
            "name": self.mower_configflow[CONF_MOWER_NAME],
            "manufacturer": "STIHL",
            "model": self.mower_configflow[CONF_MOWER_MODEL],
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"iMow {self.mower_configflow['name']} Info"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes of the device."""
        return self.attrs


class ImowInfoEntity(ImowBaseEntity):
    """Representation of a Sensor."""

    def __init__(self, imow: IMowApi, mower: dict):
        """Initialize the sensor."""
        super().__init__(imow, mower)
        self._name = f"iMow {self.mower_configflow['name']} Battery Level"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{self.mower_id}_info_battery_level"

    @property
    def icon(self) -> str:
        """Icon of the entity."""
        return "mdi:battery"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return PERCENTAGE

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        mower_state: MowerState = await self.imow.receive_mower_by_id(
            self.mower_configflow[CONF_MOWER_IDENTIFIER]
        )
        mower_state_values = dict(mower_state.__dict__)
        self._state = mower_state_values["status"]["chargeLevel"]

        del mower_state_values["api"]
        del mower_state_values["smartLogic"]
        del mower_state_values["status"]
        self.attrs.update(mower_state_values)


class ImowInfoChildEntity(ImowBaseEntity):
    """Representation of a Sensor."""

    def __init__(self, desc, parent: ImowInfoEntity):
        """Initialize the sensor."""
        super().__init__(parent.imow, parent.mower_configflow)

        self._name = f"{NAME_PREFIX}_info_{desc}"
        self.parent = parent
        self.desc = desc

    @property
    def should_poll(self) -> bool:
        """Indicate that this is a silent entity."""
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.desc in self.parent.attrs:
            return self.parent.attrs[self.desc]

        return ""


class ImowStateEntity(ImowBaseEntity):
    """Representation of a Sensor."""

    def __init__(self, imow: IMowApi, mower: dict):
        """Initialize the sensor."""
        super().__init__(imow, mower)
        self._name = f'{NAME_PREFIX}_state_{mower["name"]}'

    @property
    def icon(self) -> str:
        """Icon of the entity."""
        return "mdi:state-machine"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"iMow {self.mower_configflow['name']} State"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{self.mower_id}_state"

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        mower_state: MowerState = await self.imow.receive_mower_by_id(
            self.mower_configflow[CONF_MOWER_IDENTIFIER]
        )
        self._state = MowerTask(mower_state.status["mainState"]).name
        self.attrs.update(mower_state.status)


class ImowStatisticsEntity(ImowBaseEntity):
    """Representation of a Sensor."""

    def __init__(self, imow: IMowApi, mower: dict):
        """Initialize the sensor."""
        super().__init__(imow, mower)
        self._name = f'{NAME_PREFIX}_statistics_{mower["name"]}'

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"iMow {self.mower_configflow['name']} " \
               f"Total Blade Operating Time"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{self.mower_id}_statistics"

    @property
    def icon(self) -> str:
        """Icon of the entity."""
        return "mdi:clock-outline"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TIME_SECONDS

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        statistics: dict = await self.imow.receive_mower_statistics(
            self.mower_configflow[CONF_MOWER_IDENTIFIER]
        )
        self._state = statistics["totalBladeOperatingTime"]
        self.attrs.update(statistics)
