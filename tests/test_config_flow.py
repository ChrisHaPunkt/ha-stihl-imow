"""Tests for the STIHL iMow config flow."""

from __future__ import annotations

import datetime
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import SOURCE_REAUTH, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from imow.common.exceptions import ApiMaintenanceError, LoginError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stihl_imow.const import (
    CONF_ATTR_EMAIL,
    CONF_ATTR_PASSWORD,
    DOMAIN,
)

from .conftest import (
    MOWER_ID,
    MOWER_NAME,
    TEST_EMAIL,
    TEST_PASSWORD,
    make_mower,
)

USER_INPUT = {CONF_ATTR_EMAIL: TEST_EMAIL, CONF_ATTR_PASSWORD: TEST_PASSWORD}


async def test_user_flow_success(
    hass: HomeAssistant, mock_imow_api, mock_setup_entry
) -> None:
    """A valid login creates an entry keyed by the mower id."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == MOWER_NAME
    assert result["result"].unique_id == str(MOWER_ID)
    assert result["data"][CONF_ATTR_EMAIL] == TEST_EMAIL
    assert mock_setup_entry.called


async def test_user_flow_invalid_auth(hass: HomeAssistant) -> None:
    """Invalid credentials surface as invalid_auth."""
    api = AsyncMock()
    api.get_token = AsyncMock(side_effect=LoginError("bad creds"))
    api.close = AsyncMock()
    with patch(
        "custom_components.stihl_imow.config_flow.IMowApi", return_value=api
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Maintenance/connection issues surface as cannot_connect."""
    api = AsyncMock()
    api.get_token = AsyncMock(side_effect=ApiMaintenanceError("maintenance"))
    api.close = AsyncMock()
    with patch(
        "custom_components.stihl_imow.config_flow.IMowApi", return_value=api
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_already_configured(
    hass: HomeAssistant,
    mock_imow_api,
    mock_setup_entry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """A second entry for the same mower id aborts."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth_success(
    hass: HomeAssistant,
    mock_imow_api,
    mock_setup_entry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Reauth with the same account updates the entry and reloads."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
        },
        data=mock_config_entry.data,
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_ATTR_PASSWORD: "new-secret"}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data[CONF_ATTR_PASSWORD] == "new-secret"


async def test_reauth_wrong_account(
    hass: HomeAssistant,
    mock_setup_entry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Reauth that resolves a different mower aborts with wrong_account."""
    mock_config_entry.add_to_hass(hass)

    api = AsyncMock()
    api.get_token = AsyncMock(
        return_value=("t", datetime.datetime(2026, 8, 8, 10, 0, 0))
    )
    api.receive_mowers = AsyncMock(return_value=[make_mower(mower_id=999)])
    api.close = AsyncMock()
    with patch(
        "custom_components.stihl_imow.config_flow.IMowApi", return_value=api
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": SOURCE_REAUTH,
                "entry_id": mock_config_entry.entry_id,
            },
            data=mock_config_entry.data,
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_ATTR_PASSWORD: "new-secret"}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "wrong_account"
