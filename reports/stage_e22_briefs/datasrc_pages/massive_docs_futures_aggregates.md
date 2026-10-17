> For the full documentation index, see: https://massive.com/docs/llms.txt

# REST
## Futures

### Aggregate Bars (OHLC)

**Endpoint:** `GET /futures/v1/aggs/{ticker}`

**Description:**

Retrieve historical OHLC (open, high, low, close) and volume bars for a futures contract over a date range. Set the bar size with the resolution parameter, from seconds up to a full session, week, month, quarter, or year. Bars are built from the trades in each interval, so an interval with no trades has no bar.

A futures session opens the evening before the date it settles on, so a session bar's window_start is the day before its session_end_date. To load the session that settles on a given date, query window_start for the day before.

Use Cases: Market monitoring, technical analysis, backtesting, trading strategy development.

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `ticker` | string | Yes | The futures contract identifier, including the base symbol and contract expiration (e.g., GCJ5 for the April 2025 gold contract). |
| `resolution` | string | No | The size of each aggregate candle, specified as a number followed by a unit: sec, min, hour, session, week, month, quarter, or year.  Each unit has a maximum multiplier. For instance, minute candles go up to 59min; after that, use 1hour. Requesting an unsupported size returns a 400 Bad Request. |
| `window_start` | string | No | Filter by the start time of each candle. Accepts a YYYY-MM-DD date or a nanosecond Unix timestamp. The value is snapped to the start of the matching candle interval. When omitted, the API returns the most recent candles up to the limit.  Session candles are timestamped at the start of the session, not the trading date they settle on. A futures session opens the evening before it settles, so window_start falls on the day before session_end_date. To pull the session that settles on a given date, set window_start to the day before. For example, window_start=2025-08-05 returns the session that settles on 2025-08-06. Week, month, quarter, and year candles follow the same rule: window_start is the first day of the period and session_end_date is the last trading date in it.  Add a comparison suffix to filter a range: window_start.gte (greater than or equal to), window_start.gt (greater than), window_start.lte (less than or equal to), or window_start.lt (less than).  Examples:  Most recent minute candles: /v1/aggs/ESU5?resolution=1min&limit=5  Session settling 2025-08-06 (pass its start date, 2025-08-05): /v1/aggs/ESU5?resolution=1session&window_start=2025-08-05  Date range: /v1/aggs/ESU5?resolution=1session&window_start.gte=2025-07-01&window_start.lte=2025-07-31  After a timestamp: /v1/aggs/ESU5?resolution=1sec&window_start.gt=1751409877000000000&limit=1000 |
| `limit` | integer | No | The number of results to return per page (default=1000, maximum=50000, minimum=1). |
| `window_start.gte` | string | No | Range by window_start. |
| `window_start.gt` | string | No | Range by window_start. |
| `window_start.lte` | string | No | Range by window_start. |
| `window_start.lt` | string | No | Range by window_start. |
| `sort` | string | No | Sort results by field and direction using dotted notation (e.g., 'ticker.asc', 'name.desc'). |

## Response Attributes

| Field | Type | Description |
| --- | --- | --- |
| `next_url` | string | If present, the URL to the next page of results. |
| `results` | array[object] | N/A |
| `results[].close` | number | The last price within the timeframe. |
| `results[].dollar_volume` | number | The sum of price × size across all trades in the window, expressed in the contract's quoted price units, which are the same units as the bar's open, high, low, and close. Despite the field name, no contract multiplier is applied, so this is not a notional dollar value. See the <a href="/docs/rest/futures/products">Products endpoint</a> for contract multiplier details. Because dollar_volume is a raw sum, you can use it to compute a volume-weighted average price (VWAP) over any span of bars: sum dollar_volume across the bars in the window and divide by the summed volume. |
| `results[].high` | number | The highest price within the timeframe. |
| `results[].low` | number | The lowest price within the timeframe. |
| `results[].open` | number | The opening price within the timeframe. |
| `results[].session_end_date` | string | Also known as the trading date, the date of the end of the trading session, in YYYY-MM-DD format. Sessions are named by this end date, while window_start holds the session's start date, which for session candles is the day before. |
| `results[].settlement_price` | number | The price the contract settled at for this session. Included for session, week, month, quarter, and year candles; for multi-session candles it is the settlement of the final session in the period. Not returned for intraday candles (sec, min, hour). |
| `results[].ticker` | string | The ticker for the contract. |
| `results[].transactions` | integer | The number of transactions that occurred within the timeframe. |
| `results[].volume` | integer | The number of contracts that traded within the timeframe. |
| `results[].window_start` | integer | The timestamp of the beginning of the candlestick’s aggregation window. |
| `status` | string | The status of the response. |

## Sample Response

```json
{
  "request_id": "b452e45b7eaad14151c3e1ce5129b558",
  "results": [
    {
      "close": 2874.2,
      "dollar_volume": 380717446,
      "high": 2877.1,
      "low": 2837.4,
      "open": 2850.4,
      "session_end_date": "2025-02-04",
      "settlement_price": 2875.8,
      "ticker": "GCJ5",
      "transactions": 74262,
      "volume": 133127,
      "window_start": 1738540800000000000
    },
    {
      "close": 2884.8,
      "dollar_volume": 448429944.1,
      "high": 2906,
      "low": 2870.1,
      "open": 2873.7,
      "session_end_date": "2025-02-05",
      "settlement_price": 2893,
      "ticker": "GCJ5",
      "transactions": 83673,
      "volume": 155170,
      "window_start": 1738627200000000000
    }
  ],
  "status": "OK"
}
```


## Plan Access

**Plan Access:** Included in all Futures plans

#### Individual Plans

| Plan | Access |
| --- | --- |
| Futures Basic | Included |
| Futures Starter | Included |
| Futures Developer | Included |
| Futures Advanced | Included |

#### Business Plans

| Plan | Access |
| --- | --- |
| Futures Business CME | Included |
| Futures Business CBOT | Included |
| Futures Business NYMEX | Included |
| Futures Business COMEX | Included |

## Plan Recency

**Plan Recency:** 8-hour historical, 10-minute delayed, or real-time

#### Individual Plans

| Plan | Recency |
| --- | --- |
| Futures Basic | 8-hour historical |
| Futures Starter | 10-minute delayed |
| Futures Developer | 10-minute delayed |
| Futures Advanced | Real-time |

#### Business Plans

| Plan | Recency |
| --- | --- |
| Futures Business CME | Real-time |
| Futures Business CBOT | Real-time |
| Futures Business NYMEX | Real-time |
| Futures Business COMEX | Real-time |

## Plan History

**Plan History:** Records date back to April 3, 2017

#### Individual Plans

| Plan | History |
| --- | --- |
| Futures Basic | 2 years |
| Futures Starter | 2 years |
| Futures Developer | 5 years |
| Futures Advanced | All history |

#### Business Plans

| Plan | History |
| --- | --- |
| Futures Business CME | All history |
| Futures Business CBOT | All history |
| Futures Business NYMEX | All history |
| Futures Business COMEX | All history |
