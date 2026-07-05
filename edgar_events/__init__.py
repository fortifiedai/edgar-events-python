"""Python client for the EDGAR Events API (https://edgarevents.com).

Structured SEC filing events — 13D activist stakes, 8-K material items, IPO
filings — over HTTP. Mint a free key at https://edgarevents.com/subscribe, or
call demo() for a keyless live sample.
"""
from .client import EdgarEvents, EdgarEventsError, __version__

__all__ = ["EdgarEvents", "EdgarEventsError", "__version__"]
