"""Common fixtures for STIHL iMow tests."""

from __future__ import annotations

import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stihl_imow.const import (
    CONF_API_TOKEN,
    CONF_API_TOKEN_EXPIRE_TIME,
    CONF_ATTR_EMAIL,
    CONF_ATTR_LANGUAGE,
    CONF_ATTR_PASSWORD,
    CONF_MOWER_IDENTIFIER,
    CONF_MOWER_MODEL,
    CONF_MOWER_NAME,
    CONF_MOWER_VERSION,
    DOMAIN,
)

MOWER_ID = 31466
MOWER_NAME = "Mährlin"
TEST_EMAIL = "user@example.com"
TEST_PASSWORD = "secret"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of the custom integration in every test."""
    yield


def make_mower(mower_id: int = MOWER_ID, name: str = MOWER_NAME):
    """Return a lightweight stand-in for a MowerState from receive_mowers()."""
    return SimpleNamespace(
        id=mower_id,
        name=name,
        deviceTypeDescription="iMow",
        softwarePacket="1.2.3",
    )


@pytest.fixture
def mock_imow_api():
    """Patch the IMowApi used by the config flow with an authenticated mock."""
    expire = datetime.datetime(2026, 8, 8, 10, 0, 0)
    api = AsyncMock()
    api.get_token = AsyncMock(return_value=("test-token", expire))
    api.receive_mowers = AsyncMock(return_value=[make_mower()])
    api.close = AsyncMock()
    with patch(
        "custom_components.stihl_imow.config_flow.IMowApi", return_value=api
    ):
        yield api


@pytest.fixture
def mock_setup_entry():
    """Prevent real entry setup during config-flow tests."""
    with patch(
        "custom_components.stihl_imow.async_setup_entry", return_value=True
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a v2 config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=MOWER_NAME,
        unique_id=str(MOWER_ID),
        version=2,
        data={
            CONF_ATTR_EMAIL: TEST_EMAIL,
            CONF_ATTR_PASSWORD: TEST_PASSWORD,
            CONF_API_TOKEN: "stored-token",
            CONF_API_TOKEN_EXPIRE_TIME: 1786000000.0,
            CONF_MOWER_IDENTIFIER: MOWER_ID,
            CONF_MOWER_NAME: MOWER_NAME,
            CONF_MOWER_MODEL: "iMow",
            CONF_MOWER_VERSION: "1.2.3",
            CONF_ATTR_LANGUAGE: "en",
        },
    )


@pytest.fixture
def mock_runtime_api():
    """Patch the IMowApi used by __init__ / coordinator for setup tests."""
    api = AsyncMock()
    api.get_token = AsyncMock(return_value="stored-token")
    api.access_token = "stored-token"
    api.token_expires = None

    mower_state = MagicMock()
    mower_state.get_statistics = AsyncMock(return_value={})
    api.receive_mower_by_id = AsyncMock(return_value=mower_state)
    api.receive_mower_state_with_statistics = AsyncMock(
        return_value=mower_state
    )

    with patch("custom_components.stihl_imow.IMowApi", return_value=api):
        yield api
