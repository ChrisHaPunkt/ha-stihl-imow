"""Tests for STIHL iMow setup, unload and migration."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from imow.common.exceptions import ApiMaintenanceError, LoginError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stihl_imow.const import (
    CONF_ATTR_EMAIL,
    CONF_ATTR_PASSWORD,
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


async def test_migrate_v1_to_v3(
    hass: HomeAssistant, mock_setup_entry
) -> None:
    """A legacy v1 entry migrates to the account-based v3 schema."""
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

    assert entry.version == 3
    assert entry.data[CONF_ATTR_EMAIL] == TEST_EMAIL
    assert "user_input" not in entry.data
    assert "polling_interval" not in entry.data
    assert "mower" not in entry.data
    assert "mower_id" not in entry.data


async def test_migrate_v2_to_v3(
    hass: HomeAssistant, mock_setup_entry
) -> None:
    """A v2 (per-mower) entry migrates to the account-based v3 schema."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id=str(MOWER_ID),
        data={
            CONF_ATTR_EMAIL: TEST_EMAIL,
            CONF_ATTR_PASSWORD: TEST_PASSWORD,
            "mower_id": MOWER_ID,
            "language": "en",
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.version == 3
    assert entry.data[CONF_ATTR_EMAIL] == TEST_EMAIL
    assert entry.data[CONF_ATTR_PASSWORD] == TEST_PASSWORD
    assert "mower_id" not in entry.data


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


async def test_coordinator_auth_error(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """A LoginError during the first data fetch fails setup with an error."""
    mock_config_entry.add_to_hass(hass)

    api = AsyncMock()
    api.get_token = AsyncMock(return_value="stored-token")
    api.access_token = "stored-token"
    api.token_expires = None
    api.receive_mowers = AsyncMock(side_effect=LoginError("expired"))
    with patch("custom_components.stihl_imow.IMowApi", return_value=api):
        assert not await hass.config_entries.async_setup(
            mock_config_entry.entry_id
        )
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR


async def test_coordinator_maintenance_retry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """A maintenance error during the first data fetch retries setup."""
    mock_config_entry.add_to_hass(hass)

    api = AsyncMock()
    api.get_token = AsyncMock(return_value="stored-token")
    api.access_token = "stored-token"
    api.token_expires = None
    api.receive_mowers = AsyncMock(side_effect=ApiMaintenanceError("down"))
    with patch("custom_components.stihl_imow.IMowApi", return_value=api):
        assert not await hass.config_entries.async_setup(
            mock_config_entry.entry_id
        )
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


def test_add_mower_entities_adds_new_mowers() -> None:
    """The dynamic helper adds entities for newly appearing mowers once."""
    from custom_components.stihl_imow.entity import add_mower_entities

    coordinator = MagicMock()
    coordinator.data = {"1": object()}
    coordinator.async_add_listener = MagicMock(return_value=lambda: None)

    added: list = []

    def _build(mower_id, _state):
        return [f"{mower_id}_entity"]

    add_mower_entities(coordinator, added.extend, _build)
    assert added == ["1_entity"]

    listener = coordinator.async_add_listener.call_args[0][0]

    coordinator.data = {"1": object(), "2": object()}
    listener()
    assert added == ["1_entity", "2_entity"]

    listener()  # no new mowers -> no additions
    assert added == ["1_entity", "2_entity"]


async def test_remove_config_entry_device(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_runtime_api,
) -> None:
    """Only devices whose mower left the account can be removed."""
    from custom_components.stihl_imow import (
        async_remove_config_entry_device,
    )

    mock_config_entry.add_to_hass(hass)
    with patch("custom_components.stihl_imow.PLATFORMS", []):
        assert await hass.config_entries.async_setup(
            mock_config_entry.entry_id
        )
        await hass.async_block_till_done()

    present = SimpleNamespace(identifiers={(DOMAIN, str(MOWER_ID))})
    gone = SimpleNamespace(identifiers={(DOMAIN, "999")})

    assert not await async_remove_config_entry_device(
        hass, mock_config_entry, present
    )
    assert await async_remove_config_entry_device(
        hass, mock_config_entry, gone
    )
