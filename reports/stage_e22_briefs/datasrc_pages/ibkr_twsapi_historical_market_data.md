> This page is for TWS API.

> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://ibkrcampus.com/docs/llms.txt.

# get\_historical\_data()

The `get_historical_data()` function retrieves historical bar data for a given contract. Bars are returned as a list of Bar objects covering the requested duration and bar size.

## Request Arguments

**`contract`** `object` — required

[Contract Object](/tws-api/doc/contracts-financial-instruments/the-contract-object) for the instrument to retrieve market data for.

---

**`end_date_time`** `string` — required

The request's end date and time, formatted as `"YYYYMMDD HH:mm:ss TMZ"`. Pass an empty string to indicate the current moment. Must be left as an empty string when requesting continuous futures contracts or certain `whatToShow` values such as `ADJUSTED_LAST`.

---

**`duration_str`** `string` — required

The total timespan the bars should cover. See [Duration](/tws-api/doc/md/historical-bars#historical-duration) for details.

---

**`bar_size_setting`** `string` — required

The time span covered by each bar. See [Bar Sizes](/tws-api/doc/md/earliest-data-point#historical-bar-sizes) for details.

---

**`what_to_show`** `string` — required

Determines what kind of data should be returned. See [whatToShow](/tws-api/doc/md/earliest-data-point#whattoshow-values) for more details.

---

**`use_rth`** `bool`

Define if data should only be returned from the regular trading session or if extended trading hours should be included. Default: `True`, returning only regular trading session data.

---

**`format_date`** `int32`

Determine the return structure of the date. Pass `1` to return a datetime formatted string or `2` to return an epoch Unix timestamp. Default: `1`.

---

**`timeout`** `int32`

Duration to wait for the response until termination. Function-specific timeout default of 30 seconds.

---

```python
app.get_historical_data(contract=contract, end_date_time="20260708", duration_str="1 D", bar_size_setting="1 hour", what_to_show="TRADES", use_rth=True)
```

## Response Object

Requesting historical bars will return a list containing all Bar objects for the requested duration. Please be aware that directly printing this information may result in the memory address being displayed.

```json wordWrap
[2524872613328: Date: 20251013, Open: 249.31, High: 249.69, Low: 245.56, Close: 247.66, Volume: 187465.43, WAP: 247.952, BarCount: 105768, 2524872614864: Date: 20251014, Open: 246.6, High: 248.85, Low: 244.7, Close: 247.77, Volume: 176034.99, WAP: 247.21, BarCount: 100507, 2524872615120: Date: 20251015, Open: 249.49, High: 251.82, Low: 247.47, Close: 249.34, Volume: 172136.46, WAP: 249.754, BarCount: 96331, 2524872615248: Date: 20251016, Open: 248.28, High: 249.04, Low: 245.13, Close: 247.45, Volume: 235179.94, WAP: 247.351, BarCount: 132811, 2524872615376: Date: 20251017, Open: 248.08, High: 253.38, Low: 247.27, Close: 252.29, Volume: 260673.48, WAP: 250.408, BarCount: 125863]
```

## Example Implementation

```python
from ibapi.sync_wrapper import TWSSyncWrapper
app = TWSSyncWrapper(timeout=30)

# Connect to TWS
if not app.connect_and_start(host="127.0.0.1", port=7496, client_id=0):
    # If the connection fails and False is returned, notify the user and gracefully exit the application.
    print("Failed to connect to TWS")
    exit(1)
else:
    # If the connection succeeded, notify the user.
    print("Connected to TWS")

contract = Contract()
contract.symbol = "AAPL"
contract.secType = "STK"
contract.exchange = "SMART"
contract.primaryExchange = "NASDAQ"
contract.currency = "USD"

hist_data = app.get_historical_data(contract=contract, end_date_time="", duration_str="1 D", bar_size_setting="1 hour", what_to_show="TRADES")
for bar in hist_data:
   print(bar)
```