# edgar-events-python

Python client for the [EDGAR Events API](https://edgarevents.com) — structured SEC filing events (13D activist stakes, 8-K material items, IPO filings) without parsing filing HTML yourself.

## Install

```
pip install edgar-events
```

## Use

Get a key at [edgarevents.com](https://edgarevents.com), then:

```python
from edgar_events import EdgarEvents

client = EdgarEvents(api_key="ee_...")

# Recent 13D activist stakes, resolved to ticker + holder + percent
for stake in client.recent_activist_stakes(hours=72):
    print(stake)

# 8-K material events for a set of tickers, item 2.02 (results) only
events = client.filings(ticker="AAPL,MSFT,NVDA", type="8-K", item="2.02", material=True)

# Everything for one ticker
apple = client.filings_for_ticker("AAPL", hours=168)
```

## Methods

| Method | Endpoint |
|---|---|
| `recent_activist_stakes(hours, limit)` | `/recent-activist-stakes` |
| `recent_8k_material_events(hours, limit)` | `/recent-8k-material-events` |
| `recent_ipo_filings(hours, limit)` | `/recent-ipo-filings` |
| `filings(ticker, type, item, material, since, hours, limit)` | `/filings` |
| `filings_for_ticker(ticker, type, hours, limit)` | `/filings/{ticker}` |

Auth is an `X-API-Key` header, set for you from the `api_key` you pass to the constructor. A non-2xx response raises `EdgarEventsError` with `.status`.

The client depends only on the standard library. For an MCP server built on the same data, see [edgar-events-mcp](https://github.com/fortifiedai/edgar-events-mcp); for runnable consumers, see [edgar-events-examples](https://github.com/fortifiedai/edgar-events-examples).

## License

MIT.
