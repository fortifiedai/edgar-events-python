# edgar-events-python

Python client for the [EDGAR Events API](https://edgarevents.com) — structured SEC filing events (13D activist stakes, 8-K material items, IPO/S-1 filings) without parsing filing HTML yourself.

## Install

```
pip install edgar-events
```

## Use

Mint a free key at [edgarevents.com/subscribe](https://edgarevents.com/subscribe) (or `POST /free-key`), then:

```python
from edgar_events import EdgarEvents

client = EdgarEvents(api_key="esk_...")

# SC 13D activist stakes, resolved to target + holder + percent of class
stakes = client.activist_stakes(min_percent=5.0, limit=10)
for e in stakes["events"]:
    print(e["target"]["name"], e["percent_of_class"], e["form"])

# Typed 8-K events across a set of tickers, item 2.02 (results) only
events = client.filings(ticker="AAPL,MSFT,NVDA", type="8-K", item="2.02", material=True)

# Everything for one ticker over the last week
apple = client.filings_for_ticker("AAPL", hours=168)
```

No key yet? `demo()` pulls a live keyless sample:

```python
sample = EdgarEvents().demo("activist-stakes")   # no api_key needed
print(sample["count"], "sample stakes")
```

## Methods

| Method | Endpoint | Returns |
|---|---|---|
| `activist_stakes(ticker, min_percent, include_amendments, startdt, enddt, limit)` | `GET /activist-stakes` | `{"count", "events": [...]}` |
| `filings(ticker, type, item, material, since, hours, limit)` | `GET /filings` | `{"count", "universe", "events": [...], "errors"}` |
| `filings_for_ticker(ticker, type, item, material, since, hours, limit)` | `GET /filings/{ticker}` | `{"ticker", "count", "events": [...]}` |
| `demo(kind)` | `GET /try/{kind}` (keyless) | `{"sample", "count", "events": [...], "upgrade"}` |

`demo(kind)` takes `"activist-stakes"`, `"8k-material-events"`, or `"ipo-filings"` and needs no key. The other three send your key as an `X-API-Key` header. Every method returns the parsed JSON as a `dict`.

A non-2xx response raises `EdgarEventsError` with `.status` and the response body. Calling a keyed method with no `api_key` raises `ValueError` before any request goes out.

The client depends only on the standard library. For an MCP server built on the same data, see [edgar-events-mcp](https://github.com/fortifiedai/edgar-events-mcp); for runnable consumers, see [edgar-events-examples](https://github.com/fortifiedai/edgar-events-examples).

## License

MIT.
