"""BaseEntity for iMow entities."""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import Any

from homeassistant.const import ATTR_MANUFACTURER, EntityCategory
from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from imow.common.mowerstate import MowerState

from .const import (
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_SW_VERSION,
    DOMAIN,
)
from .coordinator import ImowDataUpdateCoordinator
from .maps import DISABLED_BY_DEFAULT_PROPERTIES, PRIMARY_PROPERTIES


def to_translation_key(property_name: str) -> str:
    """Convert a mower property name into a snake_case translation key."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", property_name).lower()


def add_mower_entities(
    coordinator: ImowDataUpdateCoordinator,
    async_add_entities: AddEntitiesCallback,
    build_entities: Callable[[str, MowerState], Sequence[Entity]],
) -> CALLBACK_TYPE:
    """Add entities per mower now and whenever new mowers appear.

    ``build_entities(mower_id, mower_state)`` returns the entities for one
    mower. Returns an unsubscribe callback for the coordinator listener so the
    caller can register it with ``entry.async_on_unload``.
    """
    known: set[str] = set()

    @callback
    def _add_new() -> None:
        new_ids = set(coordinator.data) - known
        if not new_ids:
            return
        known.update(new_ids)
        entities: list[Entity] = []
        for mower_id in new_ids:
            entities.extend(
                build_entities(mower_id, coordinator.data[mower_id])
            )
        if entities:
            async_add_entities(entities)

    _add_new()
    return coordinator.async_add_listener(_add_new)


class ImowBaseEntity(CoordinatorEntity[ImowDataUpdateCoordinator]):
    """Base entity for a STIHL iMow mower property."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ImowDataUpdateCoordinator,
        mower_id: str,
        device: dict[str, Any],
        mower_state_property: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.mower_id = str(mower_id)
        self.key_device_infos = device
        self.property_name = mower_state_property
        self._attr_translation_key = to_translation_key(mower_state_property)
        self._attr_unique_id = f"{self.mower_id}_{mower_state_property}"
        self._attr_entity_registry_enabled_default = (
            mower_state_property not in DISABLED_BY_DEFAULT_PROPERTIES
        )
        self._attr_entity_category = (
            None
            if not mower_state_property
            or mower_state_property in PRIMARY_PROPERTIES
            else EntityCategory.DIAGNOSTIC
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.mower_id)},
            name=device[ATTR_NAME],
            manufacturer=device[ATTR_MANUFACTURER],
            model=device[ATTR_MODEL],
            sw_version=device[ATTR_SW_VERSION],
        )

    @property
    def available(self) -> bool:
        """Return True only while this mower is present in the last poll."""
        return super().available and self.mower_id in self.coordinator.data

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    @property
    def mowerstate(self) -> MowerState:
        """Return this entity's mower state from the coordinator."""
        return self.coordinator.data[self.mower_id]

    def get_value_from_mowerstate(self) -> Any:
        """Return the value for this entity's property.

        A property name containing ``_`` denotes a nested value
        (e.g. ``status_chargeLevel`` -> ``status["chargeLevel"]``).
        """
        if "_" in self.property_name:
            outer, inner = self.property_name.split("_", 1)
            return getattr(self.mowerstate, outer)[inner]
        return getattr(self.mowerstate, self.property_name)
