"""
Module helps to strip aut unneeded properties.

map icons and classes to properties.
"""
from homeassistant.const import (
    LENGTH_METERS,
    DEVICE_CLASS_ENERGY,
    LENGTH_FEET,
    TIME_HOURS,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_TIMESTAMP,
    TIME_SECONDS,
)

IMOW_SENSORS_MAP = {
    "asmEnabled": {
        "type": None,
        "uom": None,
        "icon": None,
    },
    "automaticModeEnabled": {
        "type": None,
        "uom": None,
        "icon": None,
    },
    "childLock": {
        "type": None,
        "uom": None,
        "icon": "mdi:baby-carriage",
    },
    "circumference": {
        "type": None,
        "uom": LENGTH_METERS,
        "icon": "mdi:go-kart-track",
    },
    "coordinateLatitude": {"type": None, "uom": None, "icon": "mdi:map"},
    "coordinateLongitude": {"type": None, "uom": None, "icon": "mdi:map"},
    "corridorMode": {
        "type": None,
        "uom": None,
        "icon": "mdi:go-kart-track",
    },
    "demoModeEnabled": {
        "type": None,
        "uom": None,
        "icon": "mdi:information-outline",
    },
    "deviceTypeDescription": {
        "type": None,
        "uom": None,
        "icon": "mdi:robot-mower",
    },
    "edgeMowingMode": {
        "type": None,
        "uom": None,
        "icon": "mdi:axis-arrow-info",
    },
    "energyMode": {
        "type": DEVICE_CLASS_ENERGY,
        "uom": None,
        "icon": "mdi:lightning-bolt",
    },
    "firmwareVersion": {
        "type": None,
        "uom": None,
        "icon": "mdi:information-outline",
    },
    "gpsProtectionEnabled": {
        "type": None,
        "uom": None,
        "icon": "mdi:shield-half-full",
    },
    "lastWeatherCheck": {
        "type": DEVICE_CLASS_TIMESTAMP,
        "uom": None,
        "icon": None,
    },
    "ledStatus": {"type": None, "uom": None, "icon": "mdi:lightbulb"},
    "machineError": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightning-bolt-outline",
    },
    "machineState": {
        "type": None,
        "uom": None,
        "icon": "mdi:state-machine",
    },
    "mappingIntelligentHomeDrive": {
        "type": None,
        "uom": None,
        "icon": "mdi:state-machine",
    },
    "mowerImageThumbnailUrl": {
        "type": None,
        "uom": None,
        "icon": "mdi:file-image-outline",
    },
    "mowerImageUrl": {
        "type": None,
        "uom": None,
        "icon": "mdi:file-image-outline",
    },
    "name": {"type": "power", "uom": None, "icon": "mdi:robot-mower"},
    "protectionLevel": {
        "type": "power",
        "uom": None,
        "icon": "mdi:shield-half-full",
    },
    "rainSensorMode": {
        "type": "power",
        "uom": None,
        "icon": "mdi:weather-pouring",
    },
    "smartLogic_dynamicMowingplan": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
    },
    "smartLogic_mowingAreaInMeter": {
        "type": None,
        "uom": LENGTH_METERS,
        "icon": "mdi:lightbulb-on-outline",
    },
    "smartLogic_mowingAreaInFeet": {
        "type": None,
        "uom": LENGTH_FEET,
        "icon": "mdi:lightbulb-on-outline",
    },
    "smartLogic_mowingGrowthAdjustment": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
    },
    "smartLogic_mowingTime": {
        "type": None,
        "uom": TIME_HOURS,
        "icon": "mdi:watch",
    },
    "smartLogic_mowingTimeManual": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
    },
    "smartLogic_performedActivityTime": {
        "type": None,
        "uom": TIME_HOURS,
        "icon": "mdi:watch",
    },
    "smartLogic_smartNotifications": {
        "type": None,
        "uom": None,
        "icon": "mdi:cellphone-message",
    },
    "smartLogic_suggestedActivityTime": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
    },
    "smartLogic_weatherForecastEnabled": {
        "type": None,
        "uom": None,
        "icon": "mdi:lightbulb-on-outline",
    },
    "smartLogic_softwarePacket": {
        "type": None,
        "uom": None,
        "icon": "mdi:information-outline",
    },
    "stateMessage_error": {
        "type": None,
        "uom": None,
        "icon": "mdi:message-text",
    },
    "stateMessage_long": {
        "type": None,
        "uom": None,
        "icon": "mdi:message-text",
    },
    "stateMessage_short": {
        "type": None,
        "uom": None,
        "icon": "mdi:message-text",
    },
    "softwarePacket": {
        "type": None,
        "uom": None,
        "icon": "mdi:information-outline",
    },
    "statistics_totalBladeOperatingTime": {
        "type": None,
        "uom": TIME_SECONDS,
        "icon": "mdi:watch",
    },
    "statistics_totalDistanceTravelled": {
        "type": None,
        "uom": LENGTH_METERS,
        "icon": "mdi:map-marker-distance",
    },
    "statistics_totalOperatingTime": {
        "type": None,
        "uom": TIME_SECONDS,
        "icon": "mdi:watch",
    },
    "status_bladeService": {
        "type": None,
        "uom": None,
        "icon": "mdi:knife",
    },
    "status_chargeLevel": {
        "type": DEVICE_CLASS_BATTERY,
        "uom": None,
        "icon": None,
    },
    "status_lastGeoPositionDate": {
        "type": DEVICE_CLASS_TIMESTAMP,
        "uom": None,
        "icon": None,
    },
    "status_lastSeenDate": {
        "type": DEVICE_CLASS_TIMESTAMP,
        "uom": None,
        "icon": None,
    },
    "status_online": {"type": None, "uom": None, "icon": "mdi:antenna"},
    "status_rainStatus": {
        "type": "power",
        "uom": None,
        "icon": "mdi:weather-pouring",
    },
    "team": {
        "type": "power",
        "uom": None,
        "icon": "mdi:account-group",
    },
    "teamable": {
        "type": "power",
        "uom": None,
        "icon": "mdi:account-group",
    },
    "timeZone": {
        "type": "power",
        "uom": None,
        "icon": "mdi:map-clock-outline",
    },
    "version": {
        "type": "power",
        "uom": None,
        "icon": "mdi:information-outline",
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
]
