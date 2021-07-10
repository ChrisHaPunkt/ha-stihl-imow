"""
Module helps to strip aut unneeded properties.

map icons and classes to properties.
"""
import typing

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_TIMESTAMP,
    LENGTH_FEET,
    LENGTH_METERS,
    TIME_HOURS,
    TIME_SECONDS,
)

IMOW_SENSORS_MAP: typing.Dict[str, typing.Dict] = {
    "asmEnabled": {
        "type": None,
        "uom": None,
        "icon": None,
        "switch": False,
        "picture": False,
    },
    "automaticModeEnabled": {
        "type": None,
        "uom": None,
        "icon": "mdi:arrow-decision-auto-outline",
        "switch": True,
        "picture": False,
    },
    "childLock": {
        "type": None,
        "uom": None,
        "icon": "mdi:baby-carriage",
        "switch": False,
        "picture": False,
    },
    "circumference": {
        "type": None,
        "uom": LENGTH_METERS,
        "icon": "mdi:go-kart-track",
        "switch": False,
        "picture": False,
    },
    "coordinateLatitude": {
        "type": None,
        "uom": None,
        "icon": "mdi:map",
        "switch": False,
        "picture": False,
    },
    "coordinateLongitude": {
        "type": None,
        "uom": None,
        "icon": "mdi:map",
        "switch": False,
        "picture": False,
    },
    "corridorMode": {
        "type": None,
        "uom": None,
        "icon": "mdi:go-kart-track",
        "switch": False,
        "picture": False,
    },
    "demoModeEnabled": {
        "type": None,
        "uom": None,
        "icon": "mdi:information-outline",
        "switch": False,
        "picture": False,
    },
    "deviceTypeDescription": {
        "type": None,
        "uom": None,
        "icon": "mdi:robot-mower",
        "switch": False,
        "picture": False,
    },
    "edgeMowingMode": {
        "type": None,
        "uom": None,
        "icon": "mdi:axis-arrow-info",
        "switch": False,
        "picture": False,
    },
    "energyMode": {
        "type": DEVICE_CLASS_ENERGY,
        "uom": None,
        "icon": None,
        "switch": False,
        "picture": False,
    },
    "firmwareVersion": {
        "type": None,
        "uom": None,
        "icon": "mdi:information-outline",
        "switch": False,
        "picture": False,
    },
    "gpsProtectionEnabled": {
        "type": None,
        "uom": None,
        "icon": "mdi:shield-check",
        "switch": True,
        "picture": False,
    },
    "lastWeatherCheck": {
        "type": DEVICE_CLASS_TIMESTAMP,
        "uom": None,
        "icon": None,
        "switch": False,
        "picture": False,
    },
    "ledStatus": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb",
        "switch": False,
        "picture": False,
    },
    "machineError": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightning-bolt-outline",
        "switch": False,
        "picture": False,
    },
    "machineState": {
        "type": None,
        "uom": None,
        "icon": "mdi:state-machine",
        "switch": False,
        "picture": False,
    },
    "mappingIntelligentHomeDrive": {
        "type": None,
        "uom": None,
        "icon": "mdi:state-machine",
        "switch": False,
        "picture": False,
    },
    "mowerImageThumbnailUrl": {
        "type": None,
        "uom": None,
        "icon": "mdi:file-image-outline",
        "switch": False,
        "picture": True,
    },
    "mowerImageUrl": {
        "type": None,
        "uom": None,
        "icon": "mdi:file-image-outline",
        "switch": False,
        "picture": True,
    },
    "name": {
        "type": None,
        "uom": None,
        "icon": "mdi:robot-mower",
        "switch": False,
        "picture": True,
    },
    "protectionLevel": {
        "type": None,
        "uom": None,
        "icon": "mdi:shield-check",
        "switch": False,
        "picture": False,
    },
    "rainSensorMode": {
        "type": None,
        "uom": None,
        "icon": "mdi:weather-pouring",
        "switch": False,
        "picture": False,
    },
    "smartLogic_dynamicMowingplan": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
        "switch": False,
        "picture": False,
    },
    "smartLogic_mowingAreaInMeter": {
        "type": None,
        "uom": LENGTH_METERS,
        "icon": "mdi:lightbulb-on-outline",
        "switch": False,
        "picture": False,
    },
    "smartLogic_mowingAreaInFeet": {
        "type": None,
        "uom": LENGTH_FEET,
        "icon": "mdi:lightbulb-on-outline",
        "switch": False,
        "picture": False,
    },
    "smartLogic_mowingGrowthAdjustment": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
        "switch": False,
        "picture": False,
    },
    "smartLogic_mowingTime": {
        "type": None,
        "uom": TIME_HOURS,
        "icon": "mdi:watch",
        "switch": False,
        "picture": False,
    },
    "smartLogic_mowingTimeManual": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
        "switch": False,
        "picture": False,
    },
    "smartLogic_performedActivityTime": {
        "type": None,
        "uom": TIME_HOURS,
        "icon": "mdi:watch",
        "switch": False,
        "picture": False,
    },
    "smartLogic_smartNotifications": {
        "type": None,
        "uom": None,
        "icon": "mdi:cellphone-message",
        "switch": False,
        "picture": False,
    },
    "smartLogic_suggestedActivityTime": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
        "switch": False,
        "picture": False,
    },
    "smartLogic_weatherForecastEnabled": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
        "switch": False,
        "picture": False,
    },
    "smartLogic_softwarePacket": {
        "type": None,
        "uom": None,
        "icon": "mdi:information-outline",
        "switch": False,
        "picture": False,
    },
    "stateMessage_error": {
        "type": None,
        "uom": None,
        "icon": "mdi:message-text",
        "switch": False,
        "picture": False,
    },
    "stateMessage_long": {
        "type": None,
        "uom": None,
        "icon": "mdi:message-text",
        "switch": False,
        "picture": False,
    },
    "stateMessage_short": {
        "type": None,
        "uom": None,
        "icon": "mdi:message-text",
        "switch": False,
        "picture": False,
    },
    "softwarePacket": {
        "type": None,
        "uom": None,
        "icon": "mdi:information-outline",
        "switch": False,
        "picture": False,
    },
    "statistics_totalBladeOperatingTime": {
        "type": None,
        "uom": TIME_SECONDS,
        "icon": "mdi:watch",
        "switch": False,
        "picture": False,
    },
    "statistics_totalDistanceTravelled": {
        "type": None,
        "uom": LENGTH_METERS,
        "icon": "mdi:map-marker-distance",
        "switch": False,
        "picture": False,
    },
    "statistics_totalOperatingTime": {
        "type": None,
        "uom": TIME_SECONDS,
        "icon": "mdi:watch",
        "switch": False,
        "picture": False,
    },
    "status_bladeService": {
        "type": None,
        "uom": None,
        "icon": "mdi:knife",
        "switch": False,
        "picture": False,
    },
    "status_chargeLevel": {
        "type": DEVICE_CLASS_BATTERY,
        "uom": None,
        "icon": None,
        "switch": False,
        "picture": False,
    },
    "status_lastGeoPositionDate": {
        "type": DEVICE_CLASS_TIMESTAMP,
        "uom": None,
        "icon": None,
        "switch": False,
        "picture": False,
    },
    "status_lastSeenDate": {
        "type": DEVICE_CLASS_TIMESTAMP,
        "uom": None,
        "icon": None,
        "switch": False,
        "picture": False,
    },
    "status_online": {
        "type": None,
        "uom": None,
        "icon": "mdi:antenna",
        "switch": False,
        "picture": False,
    },
    "status_rainStatus": {
        "type": None,
        "uom": None,
        "icon": "mdi:weather-pouring",
        "switch": False,
        "picture": False,
    },
    "team": {
        "type": None,
        "uom": None,
        "icon": "mdi:account-group",
        "switch": False,
        "picture": False,
    },
    "teamable": {
        "type": None,
        "uom": None,
        "icon": "mdi:account-group",
        "switch": False,
        "picture": False,
    },
    "timeZone": {
        "type": None,
        "uom": None,
        "icon": "mdi:map-clock-outline",
        "switch": False,
        "picture": False,
    },
    "version": {
        "type": None,
        "uom": None,
        "icon": "mdi:information-outline",
        "switch": False,
        "picture": False,
    },
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
    "statistics_mower",
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
    "smartLogic_totalActivityActiveTime",
    "smartLogic_mowingArea",
    "status_lastNoErrorMainState",
    "imow",
]
