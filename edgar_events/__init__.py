"""Python client for the EDGAR Events API (https://edgarevents.com).

Structured SEC filing events — 13D activist stakes, 8-K material items, IPO
filings — over HTTP. Get a key from https://edgarevents.com.
"""
from .client import EdgarEvents, EdgarEventsError

__all__ = ["EdgarEvents", "EdgarEventsError"]
__version__ = "0.1.0"
