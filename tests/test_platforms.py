"""Tests for the STIHL iMow entity platforms."""

from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stihl_imow.const import DOMAIN

from .conftest import MOWER_ID


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def test_entity_registry_enabled_default_flag() -> None:
    """Off-by-default properties set enabled_default False, others True."""
    from unittest.mock import MagicMock

    from custom_components.stihl_imow.sensor import ImowSensorEntity

    device = {
        "name": "Mahrlin",
        "model": "iMow",
        "sw_version": "1.2.3",
        "manufacturer": "STIHL",
    }
    coordinator = MagicMock()

    disabled = ImowSensorEntity(coordinator, "31466", device, "circumference")
    assert disabled.entity_registry_enabled_default is False

    enabled = ImowSensorEntity(coordinator, "31466", device, "machineState")
    assert enabled.entity_registry_enabled_default is True



async def test_entities_created_for_all_platforms(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """Setup creates entities for every platform."""
    await _setup(hass, mock_config_entry)

    assert hass.states.async_entity_ids("sensor")
    assert hass.states.async_entity_ids("binary_sensor")
    assert hass.states.async_entity_ids("switch")
    assert hass.states.async_entity_ids("device_tracker")


async def test_sensor_value_and_attributes(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """The machine-state sensor exposes its value and message attributes."""
    await _setup(hass, mock_config_entry)
    ent_reg = er.async_get(hass)

    entity_id = ent_reg.async_get_entity_id(
        "sensor", DOMAIN, f"{MOWER_ID}_machineState"
    )
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == "MOWING"
    assert state.attributes["short"] == "Mowing"
    assert state.attributes["long"] == "Mowing the lawn"


async def test_binary_sensor_value(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """A boolean property becomes a binary sensor."""
    await _setup(hass, mock_config_entry)
    ent_reg = er.async_get(hass)

    entity_id = ent_reg.async_get_entity_id(
        "binary_sensor", DOMAIN, f"{MOWER_ID}_status_online"
    )
    assert entity_id is not None
    assert hass.states.get(entity_id).state == "on"


async def test_device_tracker_position(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """The tracker exposes the mower's GPS position."""
    await _setup(hass, mock_config_entry)
    ent_reg = er.async_get(hass)

    entity_id = ent_reg.async_get_entity_id(
        "device_tracker", DOMAIN, f"{MOWER_ID}_tracker"
    )
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state.attributes["latitude"] == 54.1
    assert state.attributes["longitude"] == 10.6


async def test_switch_turn_on_off(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """Toggling a switch pushes the setting upstream."""
    await _setup(hass, mock_config_entry)
    ent_reg = er.async_get(hass)

    entity_id = ent_reg.async_get_entity_id(
        "switch", DOMAIN, f"{MOWER_ID}_automaticModeEnabled"
    )
    assert entity_id is not None

    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    mock_runtime_api.update_setting.assert_awaited_with(
        str(MOWER_ID), "automaticModeEnabled", False
    )

    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    mock_runtime_api.update_setting.assert_awaited_with(
        str(MOWER_ID), "automaticModeEnabled", True
    )


async def test_switch_error_raises(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """An upstream failure while switching surfaces as HomeAssistantError."""
    await _setup(hass, mock_config_entry)
    ent_reg = er.async_get(hass)

    entity_id = ent_reg.async_get_entity_id(
        "switch", DOMAIN, f"{MOWER_ID}_childLock"
    )
    assert entity_id is not None
    mock_runtime_api.update_setting.side_effect = Exception("boom")

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "switch", "turn_on", {"entity_id": entity_id}, blocking=True
        )
