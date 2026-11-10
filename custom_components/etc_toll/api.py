"""API client for Expressway ETC (Sri Lanka) portal."""

from __future__ import annotations

import logging
import re
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

URL_QUICK_TOPUP = "https://www.exway.rda.gov.lk/etconline/en/quick-topup"
URL_VALIDATE_CARD = "https://www.exway.rda.gov.lk/etconline/api/topup/validate-card"


class EtcApiError(Exception):
    """Exception for ETC API communication errors."""


class EtcInvalidCardError(EtcApiError):
    """Exception for invalid or not found ETC card."""


class EtcApiClient:
    """Client for querying the Expressway ETC portal."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the client."""
        self._session = session

    async def async_get_card_details(self, card_number: str) -> dict[str, Any]:
        """Fetch card details and current balance from ETC portal."""
        card_num = str(card_number).strip()
        if len(card_num) < 7:
            raise EtcInvalidCardError("The card number must be at least 7 characters.")

        # 1. Fetch quick-topup page to obtain CSRF token and session cookie
        try:
            async with self._session.get(
                URL_QUICK_TOPUP,
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                },
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status != 200:
                    raise EtcApiError(
                        f"Failed to load ETC quick-topup page: HTTP {resp.status}"
                    )
                text = await resp.text()
        except aiohttp.ClientError as err:
            raise EtcApiError(f"Network error accessing ETC portal: {err}") from err

        m_csrf = re.search(
            r"name=[\"']csrf-token[\"']\s+content=[\"']([^\"']+)[\"']", text
        )
        if not m_csrf:
            raise EtcApiError("Could not extract CSRF token from ETC quick-topup page.")
        csrf_token = m_csrf.group(1)

        # 2. Call validate-card endpoint
        api_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-CSRF-TOKEN": csrf_token,
            "Referer": URL_QUICK_TOPUP,
            "Origin": "https://www.exway.rda.gov.lk",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }

        try:
            async with self._session.post(
                URL_VALIDATE_CARD,
                json={"card_number": card_num},
                headers=api_headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                data = await resp.json()
                if resp.status == 200 and data.get("success"):
                    return {
                        "card_number": data.get("card_number", card_num),
                        "balance": float(data.get("balance_rupees", 0.0)),
                        "balance_cents": int(data.get("balance_cents", 0)),
                        "balance_display": str(data.get("balance_display", "")),
                        "status": str(data.get("message", "Active")),
                    }
                if resp.status == 422:
                    msg = data.get("message")
                    if isinstance(data.get("errors"), dict) and "card_number" in data["errors"]:
                        msg = data["errors"]["card_number"][0]
                    raise EtcInvalidCardError(msg or "ETC card not found.")

                raise EtcApiError(
                    f"Unexpected response from ETC server: HTTP {resp.status} - {data}"
                )
        except aiohttp.ClientError as err:
            raise EtcApiError(f"Network error querying ETC card balance: {err}") from err

