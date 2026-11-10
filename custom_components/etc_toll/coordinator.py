"""DataUpdateCoordinator for ETC Toll (Sri Lanka) integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EtcApiClient, EtcApiError, EtcInvalidCardError
from .const import CONF_CARD_NUMBER, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class EtcDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching ETC card details from portal."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: EtcApiClient,
    ) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.client = client
        self.card_number: str = entry.data[CONF_CARD_NUMBER]

        scan_interval = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.card_number}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest card details from ETC portal."""
        try:
            return await self.client.async_get_card_details(self.card_number)
        except EtcInvalidCardError as err:
            raise UpdateFailed(f"Invalid ETC card {self.card_number}: {err}") from err
        except EtcApiError as err:
            raise UpdateFailed(f"Error communicating with ETC portal: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error fetching ETC card data: {err}") from err
