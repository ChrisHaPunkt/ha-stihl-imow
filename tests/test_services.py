"""Tests for the STIHL iMow intent service."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stihl_imow.const import DOMAIN

from .conftest import MOWER_ID, MOWER_NAME


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_intent_by_name(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """An intent addressed by mower name is dispatched."""
    await _setup(hass, mock_config_entry)
    mower = AsyncMock()
    mock_runtime_api.receive_mower_by_name = AsyncMock(return_value=mower)

    await hass.services.async_call(
        DOMAIN,
        "intent",
        {"mower_name": MOWER_NAME, "action": "toDocking"},
        blocking=True,
    )
    mower.intent.assert_awaited()


async def test_intent_by_device(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """An intent addressed by device id resolves the mower name."""
    await _setup(hass, mock_config_entry)
    mower = AsyncMock()
    mock_runtime_api.receive_mower_by_name = AsyncMock(return_value=mower)

    dev_reg = dr.async_get(hass)
    device = dev_reg.async_get_device(
        identifiers={(DOMAIN, str(MOWER_ID))}
    )
    assert device is not None

    await hass.services.async_call(
        DOMAIN,
        "intent",
        {"mower_device": device.id, "action": "toDocking"},
        blocking=True,
    )
    mower.intent.assert_awaited()


async def test_intent_invalid_action(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """An unknown action value surfaces as a ServiceValidationError."""
    await _setup(hass, mock_config_entry)
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "intent",
            {"mower_name": MOWER_NAME, "action": "bogus"},
            blocking=True,
        )


async def test_intent_mower_not_found(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """A missing mower surfaces as a HomeAssistantError."""
    await _setup(hass, mock_config_entry)
    mock_runtime_api.receive_mower_by_name = AsyncMock(
        side_effect=LookupError("no such mower")
    )
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            "intent",
            {"mower_name": "ghost", "action": "toDocking"},
            blocking=True,
        )
