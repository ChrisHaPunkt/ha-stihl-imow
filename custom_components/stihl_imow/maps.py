from homeassistant.const import TEMP_CELSIUS

IMOW_SENSORS_MAP = {
    "asmEnabled": {
        "type": "power",
        "uom": "W",
        "icon": "mdi:flash-outline",
    },
    "current": {"type": "current", "uom": "A", "icon": "mdi:current-ac"},
    "voltage": {"type": "voltage", "uom": "V", "icon": "mdi:power-plug"},
    "dusty": {
        "type": "dusty",
        "uom": "µg/m3",
        "icon": "mdi:select-inverse",
    },
    "light": {
        "type": "light",
        "uom": "lx",
        "icon": "mdi:car-parking-lights",
    },
    "noise": {"type": "noise", "uom": "Db", "icon": "mdi:surround-sound"},
    "currentHumidity": {
        "type": "humidity",
        "uom": "%",
        "icon": "mdi:water-percent",
    },
    "humidity": {
        "type": "humidity",
        "uom": "%",
        "icon": "mdi:water-percent",
    },
    "currentTemperature": {
        "type": "temperature",
        "uom": TEMP_CELSIUS,
        "icon": "mdi:thermometer",
    },
    "temperature": {
        "type": "temperature",
        "uom": TEMP_CELSIUS,
        "icon": "mdi:thermometer",
    },
}

ENTITY_STRIP_OUT_PROPERTIES = [
    "status_extraStatus",
    "status_extraStatus1",
    "status_extraStatus2",
    "status_extraStatus3",
    "status_extraStatus4",
    "status_extraStatus5",
    "accountId",
    "status_mower",
    "gdprAccepted",
    "endOfContract",
    "cModuleId",
    "externalId",
]
