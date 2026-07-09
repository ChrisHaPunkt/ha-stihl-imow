"""Platform for sensor integration."""

import logging
from typing import Any

from homeassistant import core
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from imow.common.mowerstate import MowerState

from . import extract_properties_by_type
from .const import ATTR_SWITCH, DOMAIN
from .coordinator import ImowConfigEntry, ImowDataUpdateCoordinator
from .entity import ImowBaseEntity, add_mower_entities
from .maps import IMOW_SENSORS_MAP

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: ImowConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    coordinator = config_entry.runtime_data

    def _build(
        mower_id: str, mower_state: MowerState
    ) -> list["ImowSwitchSensorEntity"]:
        properties, device = extract_properties_by_type(mower_state, bool)
        return [
            ImowSwitchSensorEntity(coordinator, mower_id, device, prop)
            for prop in properties
            if prop in IMOW_SENSORS_MAP
            and IMOW_SENSORS_MAP[prop][ATTR_SWITCH]
        ]

    config_entry.async_on_unload(
        add_mower_entities(coordinator, async_add_entities, _build)
    )


class ImowSwitchSensorEntity(ImowBaseEntity, SwitchEntity):
    """Representation of a switch."""

    def __init__(
        self,
        coordinator: ImowDataUpdateCoordinator,
        mower_id: str,
        device_info: dict[str, Any],
        mower_state_property: str,
    ) -> None:
        """Switches change device settings -> config entity category."""
        super().__init__(
            coordinator, mower_id, device_info, mower_state_property
        )
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return bool(self.get_value_from_mowerstate())

    async def _async_set(self, value: bool) -> None:
        """Push a new setting value to the mower and refresh."""
        try:
            await self.coordinator.api.update_setting(
                self.mower_id, self.property_name, value
            )
        except Exception as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="update_setting_failed",
                translation_placeholders={"error": str(err)},
            ) from err
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self._async_set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self._async_set(False)
