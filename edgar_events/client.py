from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

__version__ = "0.2.0"

# edgarevents.com sits behind Cloudflare, which blocks the default
# "Python-urllib/x.y" User-Agent (HTTP 403, error 1010). Send an explicit one.
_USER_AGENT = f"edgar-events-python/{__version__} (+https://github.com/fortifiedai/edgar-events-python)"


class EdgarEventsError(Exception):
    """Raised when the API returns a non-2xx response."""

    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(f"[{status}] {message}")


class EdgarEvents:
    """Client for the EDGAR Events API (https://edgarevents.com).

    The keyed methods (activist_stakes, filings, filings_for_ticker) need an API
    key — mint a free one at https://edgarevents.com/subscribe or POST
    /free-key. The demo() method returns a live keyless sample from the /try
    endpoints and needs no key.

    >>> client = EdgarEvents(api_key="esk_...")
    >>> stakes = client.activist_stakes(min_percent=5.0)
    >>> events = client.filings(ticker="AAPL,MSFT", type="8-K", material=True)
    >>> sample = EdgarEvents().demo("activist-stakes")   # no key needed
    """

    def __init__(self, api_key: str | None = None,
                 base_url: str = "https://edgarevents.com", timeout: float = 30.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, Any] | None = None,
             require_key: bool = True) -> Any:
        if require_key and not self.api_key:
            raise ValueError("this endpoint needs an api_key — get one at "
                             "https://edgarevents.com/subscribe "
                             "(or use demo() for a keyless sample)")
        query = {k: v for k, v in (params or {}).items() if v is not None}
        url = f"{self.base_url}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        headers = {"Accept": "application/json", "User-Agent": _USER_AGENT}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise EdgarEventsError(e.code, e.read().decode(errors="replace")[:300]) from None

    def activist_stakes(self, ticker: str | None = None, min_percent: float | None = None,
                        include_amendments: bool = True, startdt: str | None = None,
                        enddt: str | None = None, limit: int = 50) -> Any:
        """SC 13D activist stakes — holder, target, percent of class, shares.

        ticker: filter to a target ticker.
        min_percent: minimum percent of class held.
        include_amendments: include 13D/A amendments (default True).
        startdt / enddt: YYYY-MM-DD date bounds.
        limit: 1-100.

        GET /activist-stakes -> {"count": int, "events": [...]}.
        """
        return self._get("/activist-stakes", {
            "ticker": ticker, "min_percent": min_percent,
            "include_amendments": include_amendments,
            "startdt": startdt, "enddt": enddt, "limit": limit})

    def filings(self, ticker: str | None = None, type: str | None = None,
                item: str | None = None, material: bool | None = None,
                since: str | None = None, hours: int = 48, limit: int = 100) -> Any:
        """Typed filing events across a ticker universe, with optional filters.

        ticker: comma-separated tickers, e.g. "AAPL,MSFT" (a small default
                universe is used if omitted).
        type:   form type, e.g. "8-K" or "S-1".
        item:   8-K item code, e.g. "2.02".
        material: only material events.
        since:  ISO datetime lower bound.
        hours:  lookback window, 1-168 (default 48).
        limit:  1-500.

        GET /filings -> {"count": int, "universe": [...], "events": [...], "errors": ...}.
        """
        return self._get("/filings", {
            "ticker": ticker, "type": type, "item": item, "material": material,
            "since": since, "hours": hours, "limit": limit})

    def filings_for_ticker(self, ticker: str, type: str | None = None,
                           item: str | None = None, material: bool | None = None,
                           since: str | None = None, hours: int = 72,
                           limit: int = 100) -> Any:
        """Typed filing events for a single ticker.

        GET /filings/{ticker} -> {"ticker": str, "count": int, "events": [...]}.
        """
        return self._get(f"/filings/{urllib.parse.quote(ticker)}", {
            "type": type, "item": item, "material": material,
            "since": since, "hours": hours, "limit": limit})

    def demo(self, kind: str = "activist-stakes") -> Any:
        """A live keyless sample from the /try endpoints — no API key required.

        kind: "activist-stakes", "8k-material-events", or "ipo-filings".

        GET /try/{kind} -> {"sample": true, "count": int, "events": [...], "upgrade": {...}}.
        """
        allowed = {"activist-stakes", "8k-material-events", "ipo-filings"}
        if kind not in allowed:
            raise ValueError(f"kind must be one of {sorted(allowed)}")
        return self._get(f"/try/{kind}", require_key=False)
