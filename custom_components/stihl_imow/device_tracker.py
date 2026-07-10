"""Device tracker platform that adds support for OwnTracks over MQTT."""

import logging
from typing import Any

from homeassistant import core
from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from imow.common.mowerstate import MowerState

from .coordinator import ImowConfigEntry, ImowDataUpdateCoordinator
from .entity import ImowBaseEntity, add_mower_entities

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: ImowConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a tracker for every mower on the account."""
    coordinator = config_entry.runtime_data

    def _build(
        mower_id: str, mower_state: MowerState
    ) -> list["ImowDeviceTrackerEntity"]:
        device = {
            "name": mower_state.name,
            "id": mower_state.id,
            "externalId": mower_state.externalId,
            "manufacturer": "STIHL",
            "model": mower_state.deviceTypeDescription,
            "sw_version": mower_state.softwarePacket,
        }
        return [ImowDeviceTrackerEntity(coordinator, mower_id, device, "")]

    config_entry.async_on_unload(
        add_mower_entities(coordinator, async_add_entities, _build)
    )


class ImowDeviceTrackerEntity(TrackerEntity, ImowBaseEntity):
    """Represent a tracked mower (the device's main feature)."""

    _attr_name = None

    def __init__(
        self,
        coordinator: ImowDataUpdateCoordinator,
        mower_id: str,
        device_info: dict[str, Any],
        mower_state_property: str,
    ) -> None:
        """Override the BaseEntity with DeviceTracker content."""
        super().__init__(
            coordinator, mower_id, device_info, mower_state_property
        )
        # Main feature of the device: no own name, stable unique id.
        self._attr_translation_key = None
        self._attr_unique_id = f"{self.mower_id}_tracker"

    @property
    def source_type(self) -> SourceType:
        """Return the gps accuracy of the device."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        value = getattr(self.mowerstate, "coordinateLatitude")
        return None if value is None else float(value)

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        value = getattr(self.mowerstate, "coordinateLongitude")
        return None if value is None else float(value)
