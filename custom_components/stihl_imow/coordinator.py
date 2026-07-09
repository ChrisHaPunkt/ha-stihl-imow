"""DataUpdateCoordinator for the STIHL iMow integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from imow.api import IMowApi
from imow.common.exceptions import ApiMaintenanceError, LoginError
from imow.common.mowerstate import MowerState

from .const import API_UPDATE_TIMEOUT, DOMAIN, LOGGER, SCAN_INTERVAL_SECONDS

# Plain alias (not a PEP 695 `type` statement) for compatibility with the
# repo's flake8/pyflakes. ``ImowDataUpdateCoordinator`` is referenced as a
# string so it can be defined further down.
ImowConfigEntry = ConfigEntry["ImowDataUpdateCoordinator"]


class ImowDataUpdateCoordinator(DataUpdateCoordinator[dict[str, MowerState]]):
    """Coordinate polling every STIHL iMow mower on an account."""

    config_entry: ImowConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ImowConfigEntry,
        api: IMowApi,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, MowerState]:
        """Fetch the latest state (incl. statistics) for every mower."""
        try:
            async with asyncio.timeout(API_UPDATE_TIMEOUT):
                mowers = await self.api.receive_mowers()
            result: dict[str, MowerState] = {}
            for mower in mowers:
                async with asyncio.timeout(API_UPDATE_TIMEOUT):
                    result[str(mower.id)] = (
                        await self.api.receive_mower_state_with_statistics(
                            mower.id
                        )
                    )
            return result
        except LoginError as err:
            raise ConfigEntryAuthFailed from err
        except ApiMaintenanceError as err:
            raise UpdateFailed(
                f"Error communicating with API: {err}"
            ) from err
