"""Tests for the STIHL iMow diagnostics."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stihl_imow.const import (
    CONF_ATTR_EMAIL,
    CONF_ATTR_PASSWORD,
)
from custom_components.stihl_imow.diagnostics import (
    async_get_config_entry_diagnostics,
)

from .conftest import MOWER_ID


async def test_diagnostics_redacts_secrets(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_runtime_api
) -> None:
    """Diagnostics expose per-mower state with credentials redacted."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    diagnostics = await async_get_config_entry_diagnostics(
        hass, mock_config_entry
    )

    assert diagnostics["entry_data"][CONF_ATTR_EMAIL] == "**REDACTED**"
    assert diagnostics["entry_data"][CONF_ATTR_PASSWORD] == "**REDACTED**"

    mower = diagnostics["mowers"][str(MOWER_ID)]
    assert mower["accountId"] == "**REDACTED**"
    assert mower["coordinateLatitude"] == "**REDACTED**"
    assert mower["machineState"] == "MOWING"
