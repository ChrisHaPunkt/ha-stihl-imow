"""Tests for STIHL iMow setup, unload and migration."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from imow.common.exceptions import LoginError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stihl_imow.const import (
    CONF_ATTR_EMAIL,
    CONF_MOWER_IDENTIFIER,
    DOMAIN,
)

from .conftest import MOWER_ID, MOWER_NAME, TEST_EMAIL, TEST_PASSWORD


async def test_setup_and_unload(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """Setup stores the coordinator on runtime_data and unloads cleanly."""
    mock_config_entry.add_to_hass(hass)

    with patch("custom_components.stihl_imow.PLATFORMS", []):
        assert await hass.config_entries.async_setup(
            mock_config_entry.entry_id
        )
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert mock_config_entry.runtime_data is not None

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_auth_failure_triggers_reauth(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """A LoginError during setup fails setup and starts a reauth flow."""
    mock_config_entry.add_to_hass(hass)

    api = AsyncMock()
    api.get_token = AsyncMock(side_effect=LoginError("expired"))
    with patch("custom_components.stihl_imow.IMowApi", return_value=api):
        assert not await hass.config_entries.async_setup(
            mock_config_entry.entry_id
        )
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress()
    assert any(flow["context"]["source"] == SOURCE_REAUTH for flow in flows)


async def test_migrate_v1_to_v2(
    hass: HomeAssistant, mock_setup_entry
) -> None:
    """A legacy v1 entry migrates to the slim v2 schema with a unique_id."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={
            "token": "old-token",
            "expire_time": 123.0,
            "user_input": {"email": TEST_EMAIL, "password": TEST_PASSWORD},
            "mower": [
                {
                    "name": MOWER_NAME,
                    "mower_id": MOWER_ID,
                    "deviceTypeDescription": "iMow",
                    "version": "1.2.3",
                    "mower_state": {"foo": "bar"},
                }
            ],
            "language": "en",
            "polling_interval": 30,
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.version == 2
    assert entry.unique_id == str(MOWER_ID)
    assert entry.data[CONF_ATTR_EMAIL] == TEST_EMAIL
    assert entry.data[CONF_MOWER_IDENTIFIER] == MOWER_ID
    assert "user_input" not in entry.data
    assert "polling_interval" not in entry.data
    assert "mower" not in entry.data


async def test_entity_unique_id_migration(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_runtime_api,
) -> None:
    """Legacy ``{id}_{idx}_{prop}`` unique ids migrate to ``{id}_{prop}``."""
    mock_config_entry.add_to_hass(hass)
    ent_reg = er.async_get(hass)
    old_sensor = ent_reg.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{MOWER_ID}_3_machineState",
        config_entry=mock_config_entry,
    )
    old_tracker = ent_reg.async_get_or_create(
        "device_tracker",
        DOMAIN,
        f"{MOWER_ID}_99999_",
        config_entry=mock_config_entry,
    )

    with patch("custom_components.stihl_imow.PLATFORMS", []):
        assert await hass.config_entries.async_setup(
            mock_config_entry.entry_id
        )
        await hass.async_block_till_done()

    assert (
        ent_reg.async_get(old_sensor.entity_id).unique_id
        == f"{MOWER_ID}_machineState"
    )
    assert (
        ent_reg.async_get(old_tracker.entity_id).unique_id
        == f"{MOWER_ID}_tracker"
    )
