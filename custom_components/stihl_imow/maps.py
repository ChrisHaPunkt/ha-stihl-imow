"""
Module helps to strip aut unneeded properties.

map icons and classes to properties.
"""
from homeassistant.const import TEMP_CELSIUS, LENGTH_METERS, DEVICE_CLASS_ENERGY

IMOW_SENSORS_MAP = {
    "asmEnabled": {"type": None, "uom": None, "icon": None, },
    "automaticModeEnabled": {"type": None, "uom": None, "icon": None, },
    "childLock": {"type": None, "uom": None, "icon": "mdi:baby-carriage"},
    "circumference": {"type": None, "uom": LENGTH_METERS, "icon": "mdi:go-kart-track"},
    "coordinateLatitude": {"type": None, "uom": None, "icon": "mdi:map"},
    "coordinateLongitude": {"type": None, "uom": None, "icon": "mdi:map"},
    "corridorMode": {"type": None, "uom": None, "icon": "mdi:go-kart-track"},
    "demoModeEnabled": {"type": None, "uom": None, "icon": "mdi:information-outline"},
    "deviceTypeDescription": {"type": None, "uom": None, "icon": "mdi:robot-mower"},
    "edgeMowingMode": {"type": None, "uom": None, "icon": "mdi:axis-arrow-info"},
    "energyMode": {"type": DEVICE_CLASS_ENERGY, "uom": None, "icon": "mdi:lightning-bolt"},
    "firmwareVersion": {"type": None, "uom": None, "icon": "mdi:information-outline"},
    "gpsProtectionEnabled": {"type": None, "uom": None, "icon": "mdi:shield-half-full"},
    "lastWeatherCheck": {"type": None, "uom": None, "icon": "mdi:weather-cloudy"},
    "ledStatus": {"type": None, "uom": None, "icon": "mdi:lightbulb"},
    "machineError": {"type": None, "uom": None, "icon": "mdi:lightning-bolt-outline"},
    "machineState": {"type": None, "uom": None, "icon": "mdi:lightning-bolt-outline"},

    "name": {"type": "power", "uom": None, "icon": "mdi:robot-mower"},
    "rainSensorMode": {"type": "power", "uom": None, "icon": "mdi:weather-pouring"},
    "status_rainStatus": {"type": "power", "uom": None, "icon": "mdi:weather-pouring", },
}

ENTITY_STRIP_OUT_PROPERTIES = [
    "status_extraStatus",
    "status_extraStatus1",
    "status_extraStatus2",
    "status_extraStatus3",
    "status_extraStatus4",
    "status_extraStatus5",
    "status_mainState",
    "status_mower",
    "smartLogic_mower",
    "stateMessage_errorId",
    "stateMessage_legacyMessage",
    "lastNoErrorMainState",
    "unitFormat",
    "imsi",
    "localTimezoneOffset",
    "accountId",
    "gdprAccepted",
    "endOfContract",
    "cModuleId",
    "externalId",
    "codePage",
    "boundryOffset",
    "deviceType",
    "id",
    "mappingIntelligentHomeDrive"
]
