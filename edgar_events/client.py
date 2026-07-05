from __future__ import annotations

import urllib.parse
import urllib.request
import json
from typing import Any


class EdgarEventsError(Exception):
    """Raised when the API returns a non-2xx response."""

    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(f"[{status}] {message}")


class EdgarEvents:
    """Client for the EDGAR Events API.

    >>> client = EdgarEvents(api_key="ee_...")
    >>> stakes = client.recent_activist_stakes()
    >>> events = client.filings(ticker="AAPL,MSFT", type="8-K", material=True)
    """

    def __init__(self, api_key: str, base_url: str = "https://edgarevents.com", timeout: float = 30.0):
        if not api_key:
            raise ValueError("api_key is required — get one at https://edgarevents.com")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        query = {k: v for k, v in (params or {}).items() if v is not None}
        url = f"{self.base_url}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        req = urllib.request.Request(url, headers={"X-API-Key": self.api_key,
                                                   "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise EdgarEventsError(e.code, e.read().decode(errors="replace")[:300]) from None

    def recent_activist_stakes(self, hours: int = 48, limit: int = 100) -> Any:
        """Recent resolved 13D activist stakes."""
        return self._get("/recent-activist-stakes", {"hours": hours, "limit": limit})

    def recent_8k_material_events(self, hours: int = 48, limit: int = 100) -> Any:
        """Recent 8-K filings carrying material items."""
        return self._get("/recent-8k-material-events", {"hours": hours, "limit": limit})

    def recent_ipo_filings(self, hours: int = 48, limit: int = 100) -> Any:
        """Recent S-1 and IPO-related filings."""
        return self._get("/recent-ipo-filings", {"hours": hours, "limit": limit})

    def filings(self, ticker: str | None = None, type: str | None = None,
                item: str | None = None, material: bool | None = None,
                since: str | None = None, hours: int = 48, limit: int = 100) -> Any:
        """Filing events across a ticker universe, with optional filters.

        ticker: comma-separated tickers, e.g. "AAPL,MSFT".
        type:   form type, e.g. "8-K".
        item:   8-K item code, e.g. "2.02".
        material: only material events.
        since:  ISO datetime lower bound (overrides hours if set).
        hours:  lookback window, 1-168.
        """
        return self._get("/filings", {"ticker": ticker, "type": type, "item": item,
                                       "material": material, "since": since,
                                       "hours": hours, "limit": limit})

    def filings_for_ticker(self, ticker: str, type: str | None = None,
                           hours: int = 48, limit: int = 100) -> Any:
        """Filing events for a single ticker."""
        return self._get(f"/filings/{ticker}", {"type": type, "hours": hours, "limit": limit})
