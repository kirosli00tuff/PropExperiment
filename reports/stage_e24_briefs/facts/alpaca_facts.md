# Alpaca facts (Stage E.24, AlpacaReader-OpusHigh)

Written 2026-10-18 about 01:47 PDT. Sources: Alpaca's own docs (docs.alpaca.markets, as Markdown source), the Alpaca
Terms and Conditions PDF, the alpaca-py 0.44.0 wheel from PyPI (hash-verified), and one Wayback capture of a deprecated
Alpaca docs page. Saved files are under `reports/stage_e24_briefs/pages/alpaca/` and every fetch is in `alpaca_log.md`
(URL, UTC time, sha256). Forum threads were NOT fetched because the forum ToS bans automated access; anything from them is
marked [unverified, forum]. Confidence: H = verbatim vendor doc or source code; M = vendor text that is ambiguous or that
contradicts other vendor text; L = forum/search snippet only.

Abbreviations for saved files (all in pages/alpaca/):
PT = docs_paper-trading.md (https://docs.alpaca.markets/docs/paper-trading.md, 08:36:39Z);
MD = docs_about-market-data-api.md (https://docs.alpaca.markets/docs/about-market-data-api.md, 08:36:41Z);
HS = docs_historical-stock-data-1.md (https://docs.alpaca.markets/docs/historical-stock-data-1.md, 08:36:43Z);
FAQ = docs_market-data-faq.md (https://docs.alpaca.markets/docs/market-data-faq.md, 08:36:46Z);
AUTH = docs_us_authentication.md (https://docs.alpaca.markets/us/docs/authentication.md, 08:37:35Z);
FR = docs_us_fractional-trading.md (…/us/docs/fractional-trading.md, 08:37:18Z);
MS = docs_us_margin-and-short-selling.md (…/us/docs/margin-and-short-selling.md, 08:37:20Z);
ORD = docs_us_orders-at-alpaca.md (…/us/docs/orders-at-alpaca.md, 08:37:22Z);
PDT1 = docs_us_finra_intraday_margin_end_of_pdt.md (…/us/docs/understanding-finras-new-intraday-margin-rule-and-the-end-of-pdt.md, 08:37:46Z);
PDT2 = docs_us_understanding-the-new-intraday-margin-rule.md (…/us/docs/understanding-the-new-intraday-margin-rule.md, 08:37:27Z);
PDT3 = docs_us_the-intraday-margin-rule.md (…/us/docs/the-intraday-margin-rule.md, 08:37:29Z);
ACC = ref_us_getaccount-1.md (…/us/reference/getaccount-1.md, 08:37:49Z);
PO = ref_us_postorder.md (…/us/reference/postorder.md, 08:37:52Z);
BARS = ref_us_stockbars.md (…/us/reference/stockbars.md, 08:37:54Z);
CA = ref_us_corporateactions-1.md (…/us/reference/corporateactions-1.md, 08:37:57Z);
AUC = ref_us_stockauctions-1.md (…/us/reference/stockauctions-1.md, 08:39:24Z);
WB = wayback_alpaca_deprecated_api-v2.html (https://web.archive.org/web/2023id_/https://alpaca.markets/deprecated/docs/api-documentation/api-v2/ → capture 20241114115907, fetched 08:42:49Z);
PY = alpaca_py_0.44.0/alpaca_py-0.44.0-py3-none-any.whl (https://files.pythonhosted.org/packages/8e/9e/69a2d867988578d6f9e52e35d435d8a43296257cf590fb881a3752de7651/alpaca_py-0.44.0-py3-none-any.whl, 08:43:09Z; sha256 b54673f9…57c03 = PyPI digest), source read from the unzipped `alpaca_py_0.44.0/src/`.

---

## A1. Paper account

**Answer.** Anyone can open a free Paper Only Account with just an email; no funded live account is needed. A new paper
account starts at $100k by default. The balance cannot be edited in place, but you can create new paper accounts (the
dashboard now creates and deletes paper accounts instead of resetting them), and the docs say a reset can use any amount
you configure. So a $25,000 paper account looks possible by opening a new paper account with that balance; the exact
dashboard flow was not seen (no login). Paper trading API base URL: `https://paper-api.alpaca.markets`; market data stays on
`https://data.alpaca.markets`. Paper keys are separate from live keys and are generated in the dashboard; each new paper
account needs new keys. Auth headers are `APCA-API-KEY-ID` / `APCA-API-SECRET-KEY`. **alpaca-py 0.44.0 reads no
environment variables**: keys must be passed as arguments (`api_key=`, `secret_key=`). The `APCA_API_KEY_ID`,
`APCA_API_SECRET_KEY` and `APCA_API_BASE_URL` names come from Alpaca's curl examples and older SDK conventions. Our adapter
would have to read them itself.

Quotes:
- PT: "Anyone globally can create an Alpaca **Paper Only Account**! All you need to do is sign up with your email address."
- PT: "As an Alpaca Paper Only Account holder, you are only entitled to receive and make use of IEX market data."
- PT: "Your initial paper trading account is created with $100k balance as a default setting. You can reset the paper trading account at any time later with arbitrary amount as you configure."
- PT: "Your paper trading account will have a different API key from your live account … In most cases, you need to set an environment variable `APCA_API_BASE_URL = https://paper-api.alpaca.markets`"
- PT: "We've updated the dashboard to allow you to create and delete paper accounts, rather than resetting them." / "Don't forget to generate new API keys for any newly created account." / "You cannot change the account balance after it is created, unless you reset it."
- AUTH: "If you have a paper account, you can call: Trading API endpoints on `paper-api.alpaca.markets` / Market Data API endpoints on `data.alpaca.markets`" and "you cannot use your live account's credentials with the paper API, or vice versa." and "Use the `APCA-API-KEY-ID` and `APCA-API-SECRET-KEY` headers to send your key ID and secret key."
- MD: "API keys can be acquired in the web UI (under the API keys on the right sidebar)."
- PY `alpaca/common/rest.py` `_validate_credentials`: the docstring says "Gathers API credentials from parameters and environment variables", but the body only checks the arguments: `if not oauth_token and not api_key: raise ValueError("You must supply a method of authentication")`. A grep of the whole package for `environ|getenv` finds nothing. `alpaca/common/enums.py`: `TRADING_PAPER = "https://paper-api.alpaca.markets"`.

URL/files/times: PT, AUTH, MD, PY (above). Confidence: H. The "$25,000 by creating a new paper account" route: M (the docs' wording on reset versus create is inconsistent).

## A2. Market data plans and feeds

**Answer.** Trading API users get two plans: **Basic** (free, the default for paper and live) and **Algo Trader Plus**
($99/month). Basic gives real-time data from IEX only and 30 websocket symbols. Historical data goes back to 2016 on both
plans; on Basic the **latest 15 minutes** of SIP history are restricted, at 200 historical calls/min (Plus: unrestricted,
10,000/min). For historical bars, the FAQ says SIP is queryable without a subscription when `end` is at least 15 minutes
old, and that the default `feed` is the best one the subscription allows. The bars reference lists the `feed` default as
`sip`. Two vendor statements conflict with this: the Historical Stock Data page says IEX "is the only feed that can be used
without a subscription", and the paper page says Paper Only Account holders are "only entitled to receive and make use of
IEX market data". **Which feed free-plan daily bars actually come from is therefore not settled by the docs** for a Paper
Only Account. Most likely SIP for queries ending more than 15 minutes ago (FAQ) and IEX otherwise, but the adapter should
pass `feed` explicitly and log it. alpaca-py also has a `delayed_sip` feed value.

Quotes:
- MD: "The **Basic** plan serves as the default option for both Paper and Live trading accounts … this plan only includes limited real-time data: for equities only the IEX exchange".
- MD table: "Pricing | Free | $99 / month"; "Real-time market coverage | IEX | All US Stock Exchanges"; "Websocket subscriptions | 30 symbols | Unlimited"; "Historical data timeframe | Since 2016 | Since 2016"; "Historical data limitation\* | latest 15 minutes | no restriction"; "Historical API calls | 200 / min | 10,000 / min".
- FAQ: "For historical queries, the `end` parameter must be at least 15 minutes old to query SIP data without a subscription. The default value for `feed` is always the "best" available feed based on the user's subscription."
- FAQ: "for example to query any SIP trades or quotes in the last 15 minutes, you need the Algo Trader Plus subscription"
- HS (on `iex`): "ℹ️ This is the only feed that can be used without a subscription."
- BARS schema: `"stock_historical_feed": { "default": "sip", "enum": [ "iex", "otc", "sip", "boats" ]`.
- PT: "As an Alpaca Paper Only Account holder, you are only entitled to receive and make use of IEX market data."
- PY `alpaca/data/enums.py` DataFeed: "DELAYED_SIP (str): SIP data with a 15 minute delay"; `DELAYED_SIP = "delayed_sip"`.

Confidence: H for plan names, price and limits; M for which feed free daily bars use (the vendor pages disagree).

## A3. Historical daily bars: depth, `adjustment`, corporate actions

**Answer.** Stock history runs "Since 2016" on both plans. `adjustment` takes `raw` (default), `split` (price and volume,
forward and reverse splits), `dividend` (price only, cash dividends), `spin-off`, or `all` (all of these), and values can be
combined with commas. So `all` does adjust for cash dividends. **How** it adjusts (multiplicative factor versus subtracting
the dividend, ex-date conventions) is **not documented** on any vendor page found. A forum staff explanation reported in
search snippets says earlier prices are cut by the dividend's percentage of price (a multiplicative factor) and volume is
left alone [unverified, forum]. Users report errors in `all` (a dividend subtracted twice for PFE in 2023, a wrong implied
dividend for TPG in 2026) [unverified, forum]. Corporate actions endpoint: `GET https://data.alpaca.markets/v1/corporate-actions`,
filtered by symbols, `types`, start and end. Types include `cash_dividend` (fields `rate`, `special`, `foreign`, `ex_date`,
`record_date`, `payable_date`, `process_date`), `forward_split`, `reverse_split`, `spin_off`, `capital_gains_distribution`,
and others. Vendor caveat: no guarantee on when corporate actions appear. The old `/v2/corporate_actions/announcements`
endpoints are deprecated.

Quotes:
- BARS: "Specifies the adjustments for the bars.\n\n - `raw`: no adjustments\n - `split`: adjust price and volume for forward and reverse stock splits\n - `dividend`: adjust price for cash dividends\n - `spin-off`: adjust price for spin-offs\n - `all`: apply all above adjustments\n\nYou can combine multiple adjustments by separating them with a comma, e.g. `split,spin-off`." with `"default": "raw"`.
- MD: "Historical data timeframe | Since 2016 | Since 2016".
- CA: "The following types are supported: … cash_dividend … spin_off … capital_gains_distribution"; path `"/v1/corporate-actions"`, server `"https://data.alpaca.markets"`; "Currently Alpaca has no guarantees on the creation time of corporate actions. There may be delays in receiving corporate actions from our data providers".
- us/llms.txt index (docs_us_llms.txt): "[Retrieve Announcements](…/get-v2-corporate_actions-announcements-1.md): This endpoint is deprecated".
- PY `alpaca/data/enums.py` Adjustment has only `RAW, SPLIT, DIVIDEND, ALL`. No `spin-off` member, so `split,spin-off` style combinations cannot be passed through the typed request.
- [unverified, forum, search snippet] "for a cash dividend, the previous stock prices are reduced by the dividend's percentage of price, and only price is therefore adjusted" (forum.alpaca.markets/t/why-is-price-but-not-volume-adjusted-for-dividends/12345, not fetched).

Confidence: H for parameter semantics and history depth; L for the factor method.

## A4. Which close the daily bar carries; timestamp; revisions

**Answer.** Alpaca builds daily bars **from trades**. The close is the price of the last trade whose condition codes may
update open/close. Regular sales and the **Market Center Closing Trade** (condition `6`, the closing-auction print)
update it. The **Market Center Official Close** message (`M`) does **not** update it. Extended-hours trades (`T`, `U`) do
not move the daily close. **Corrected Consolidated Close** (`9`) updates the daily bar's open/close and high/low, so a
daily close can change when the SIP sends a correction. With `feed=sip` the close is therefore the consolidated tape's last
eligible regular-hours trade, in practice usually the primary listing's closing-auction print. With `feed=iex` it is the
last eligible trade on IEX only. Neither is documented to equal the exchange's official closing price. For official
auction prices there is a separate **historical auctions** endpoint (`/v2/stocks/auctions`, SIP only) that returns
closing-auction price, size, exchange and condition per day. Timestamp: the day is the New York calendar day; `t` is the
bar's left edge in RFC-3339 UTC, so a daily bar shows as midnight New York, e.g. `2023-09-29T04:00:00Z` in EDT (05:00Z in
EST). Revisions: apart from the condition-`9` rule, no vendor statement on whether or when bars are restated was found.

Quotes:
- FAQ: "Minute and daily bars are aggregated from trades. The (SIP) timestamp of the trade is truncated to the minute for minute bars and to the day (in New York) for daily bars. … The timestamp of the bar is the left side of the interval".
- FAQ table rows: "`M` | Market Center Official Close | ABC | MD | :red\_circle: | :red\_circle: | :red\_circle:"; "`6` | Market Center Closing Trade | ABC | MD | :green\_circle: | :green\_circle: | :green\_circle:"; "`T` | Extended Hours Trade | ABCO | D | :red\_circle: | :red\_circle: | 🟢"; "`9` | Corrected Consolidated Close | ABC | D | :green\_circle: | :green\_circle: | :red\_circle:"; "Close is set if the update open / close rule is :green\_circle: or if it's :yellow\_circle: and the close price hasn't been set yet".
- FAQ example (feed=sip, timeframe=1Day): `"t": "2023-09-29T04:00:00Z"`, `"c": 171.21`.
- BARS: `"timestamp": { "description": "Timestamp in RFC-3339 format with nanosecond precision."`; `"c": { "description": "Closing price."`.
- AUC: "The historical auctions endpoint provides auction prices for a list of stock symbols between the specified dates."; "Only `sip` is valid for auctions."; "Closing auctions. Every price / exchange / condition triplet is only shown once, with its earliest timestamp."
- PY: alpaca-py 0.44.0 has no auctions method (grep `auction` under `alpaca/data/` finds nothing), so the adapter would have to call that endpoint over raw REST.

Confidence: H for the aggregation rule and timestamp; M that the close equals the closing-auction print in practice (inferred from the rules, not stated); could-not-establish for revision timing.

## A5. Fractional and notional orders

**Answer.** Fractional `qty` or `notional` works for market, limit, stop and stop-limit orders, **time_in_force `day`
only** (no gtc/ioc/fok/opg/cls). Use either `qty` or `notional`; both together → HTTP 400. Up to 9 decimal places. The
asset must have `fractionable: true`. Notional orders cannot be replaced. Fractional orders work in extended and overnight
hours. Fractional shorts: the docs block order sequences that would leave a net short fractional position ("so customers
will not have a net short position"). No page explicitly allows fractional short selling. Treat fractional shares as
long-only; fractional shorts are [unverified] but very likely rejected.

Quotes:
- FR: "Alpaca currently supports fractional trading for market, limit, stop & stop limit orders with a time in force=Day, accommodating both fractional quantities and notional values. … If both qty and notional are entered the request will be rejected with an error status 400." / "Both notional and qty fields can take up to 9 decimal point values." / "Not all assets are fractionable yet so please make sure you query assets details to check for the parameter `fractionable = true`."
- ORD fractional TIF table (parsed from the HTML block): "GTC | No | No | No | No", "DAY | Yes | Yes | Yes | Yes", "IOC/FOK/OPG/CLS | No | No | No | No".
- ORD: "For Fractional Orders, starting on October 27, 2021, customers will not be able to send the following sequence of orders outside of market hours for the same security. This is so customers will not have a net short position."
- ORD: "Notional orders (orders placed using the `notional` field instead of `qty`) cannot be replaced."
- PO: "number of shares to trade. Can be fractionable for only market and day order types." (the reference is narrower than FR, which also allows limit and stop).
- PY `OrderRequest` docstring: "notional … For stocks, only works with MarketOrders. **Does not work with qty**."

Confidence: H for TIF=day and qty/notional exclusivity; M for which order types (FR, PO and PY disagree on limit/stop); L/[unverified] for fractional shorts.

## A6. Short selling in paper

**Answer.** Shorting needs ≥ $2,000 equity (a margin account). Easy-to-borrow (ETB) names: $0 locate and borrow fees for
Trading API users. Hard-to-borrow (HTB) names need an approved locate (round lots of 100, single use, non-refundable fee)
plus a daily borrow fee = HTB market value × rate / 360, charged 3 days over a weekend, in round lots. Check
`borrow_status` / `easy_to_borrow` on `/v2/assets/{symbol}`. **Paper:** short selling is supported, but **borrow fees are
not simulated** ("⛔️ (Coming Soon!)"), and paper does not simulate dividends, so short positions are not charged
dividends. No vendor page says whether paper enforces the HTB locate workflow. Margin on shorts (overnight maintenance):
price < $5 → greater of $2.50/share or 100%; price ≥ $5 → greater of $5.00/share or 30%. The buying-power check prices
an opening short at MAX(limit, ask + 3%) × qty, or ask + 3% for a market short.

Quotes:
- MS: "In order to trade on margin or sell short, you must have $2,000 or more account equity. Accounts with less than $2,000 will not have access to these features and will be restricted to 1x buying power."
- MS: "**Fees:** $0 locate and borrow fees on all ETB shares for Trading API users." / HTB: "Restricted to eligible margin accounts and requires an approved locate before a short-sale order can be submitted." / "`Daily HTB stock borrow fee = Σ((each stock’s HTB short $ market value _ that stock’s HTB rate) / 360)`"
- MS table: "SHORT | share price < $5.00 | Greater of $2.50/share or 100%"; "SHORT | share price >= $5.00 | Greater of $5.00/share or 30%".
- PT table: "Short Selling | ✅ | ✅"; "Borrow Fees | ⛔️ (Coming Soon!) | ✅"; and "Paper trading account **does NOT** simulate dividends."
- ORD: "The calculated value of an opening short sell order is MAX(order’s limit price, 3% above the current ask price) \*order quantity. For market short orders, the value is simply (3% above the current ask price)\* order quantity."

Confidence: H, except whether paper enforces HTB locates (could not establish).

## A7. Margin and buying power

**Answer.** Reg T: 50% initial margin. A margin account with ≥ $2,000 gets 2x overnight; ≥ $2,000 "can further be allowed
to use up to 4x intraday". Under $2,000: 1x (cash). **PDT has ended at Alpaca**: three 2026 docs pages say FINRA's new
intraday margin rule replaces the pattern-day-trader framework, removes the $25,000 minimum and the 4-in-5-days count, and
keeps the standard $2,000 minimum. The effective date at Alpaca is not stated on those pages [unverified]. Account object
(`GET /v2/account`) fields: `buying_power`, `regt_buying_power`, `non_marginable_buying_power`, `effective_buying_power`,
`options_buying_power`, `multiplier` (1/2/4), `equity`, `last_equity`, `cash`, `initial_margin`, `maintenance_margin`,
`last_maintenance_margin`, `sma`, `long_market_value`, `short_market_value`, `shorting_enabled`, `trading_blocked`. The
current reference no longer lists `daytrading_buying_power`, `pattern_day_trader` or `daytrade_count`, but alpaca-py
0.44.0's `TradeAccount` still has them as Optional fields. Overnight maintenance on longs: 30% above $6, 50% for
$2.50–$6, 100% below $2.50, 50%/75% for 2x/3x ETFs. Margin interest is 6.50% (non-elite) / 5.00% (elite) on the overnight
debit balance /360. The docs list no paper-specific margin rule beyond the paper/live feature table (margin ✅ in paper).

Quotes:
- MS: "Alpaca applies a minimum initial margin requirement of 50% for marginable securities and 100% for non-marginable securities per Regulation T".
- MS: "In addition to the 2x buying power afforded to margin accounts, a Reg T Margin Account with $2,000 or greater equity can further be allowed to use up to 4x intraday buying power."
- PDT1 table: "**Minimum Equity Requirement** | $25,000 for Pattern Day Traders | Eliminated (Standard $2,000 Reg T/Rule 4210 Minimum applies)"; "**Trade Counting** | 4 trades in 5 days … | Eliminated".
- PDT2: "Q: Is the Pattern Day Trader (PDT) rule still in effect? … No. The "pattern day trader" designation has been abolished." PDT3: "Yes. The definition of a "pattern day trader" has been eliminated."
- ACC `multiplier`: "valid values 1 (standard limited margin account with 1x buying power), 2 (reg T margin account with 2x intraday and overnight buying power; this is the default for all non-PDT accounts with $2,000 or more equity), 4 (PDT account with 4x intraday buying power and 2x reg T overnight buying power)".
- ACC `buying_power`: "If multiplier = 4, this is your daytrade buying power which is calculated as (last_equity - (last) maintenance_margin) * 4; If multiplier = 2, buying_power = max(equity - initial_margin,0) * 2; If multiplier = 1, buying_power = cash". `regt_buying_power`: "Your buying power under Regulation T (your excess equity - equity minus margin value - times your margin multiplier)". `non_marginable_buying_power`: "Current available non-margin dollar buying power". `last_equity`: "Equity as of previous trading day at 16:00:00 ET".
- PY `alpaca/trading/models.py` TradeAccount: `daytrading_buying_power: Optional[str] = None`, `pattern_day_trader: Optional[bool] = None`, `daytrade_count: Optional[int] = None`, `multiplier: Optional[str] = None`.
- MS: "a competitive and low annual margin interest rate of 5.00% for elite users and 6.50% for non-elite users".

Confidence: H for Reg T, $2,000 and field names; M for the current PDT status and its effective date (the docs pages are FAQs that do not give a date).

## A8. Orders at or near the close; paper fill simulation

**Answer.** MOC/LOC = `type` market/limit with `time_in_force: "cls"`. They execute only in the closing auction, are
routed to the primary exchange, and unfilled quantity is cancelled. **Cutoff: CLS orders submitted after 3:50 pm ET and
before 7:00 pm ET are rejected**; orders after 7:00 pm queue for the next day's close. Whole-share only (fractional CLS:
No). The TIF table marks CLS (and IOC, FOK, OPG) with an asterisk, and the note says "Please contact the sales team for any
TIF marked with a\*". It is **not clear** whether that applies to ordinary Trading API accounts [ambiguous]. **Paper:**
fills are simulated against the real-time NBBO, only once an order is marketable, with no queue position, no market impact
and no size check (10% random partial fills). No vendor docs page says paper simulates the closing auction. Forum staff
replies in search snippets say paper does **not** tell MOC/MOO apart and fills them at the quote, not at the auction price
[unverified, forum]. The paper fill price for a CLS order should therefore be treated as a quote-based fill near 16:00 ET,
not the official close.

Quotes:
- ORD TIF table: "`cls` | Use this TIF with a market/limit order type to submit “market on close” (MOC) and “limit on close” (LOC) orders. This order is eligible to execute only in the market closing auction. Any unfilled orders after the close will be cancelled. CLS orders submitted after 3:50pm but before 7:00pm ET will be rejected. CLS orders submitted after 7:00pm will be queued and routed to the following day’s closing auction. Only available with API v2."
- ORD (opg row): "On open/on close orders are routed to the primary exchange. Such orders do not necessarily execute exactly at 9:30am / 4:00pm ET but execute per the exchange’s auction rules."
- ORD: "***Note****: Please contact the sales team for any TIF marked with a\** ." and whole-qty table "CLS | Yes\* | Yes\* | No | No"; fractional table "CLS | No | No | No | No".
- PT: "the system simulates the order filling based on the real-time quotes." / "Orders are filled only when they become marketable." / "Your order quantity is not checked against the NBBO quantities." / "they will receive partial fills for a random size 10% of the time" / "all orders submitted in paper trading will be matched against the best available current market price (NBBO)."
- PT: paper does not account for "Market impact of your orders", "Order queue position", "Price improvement received", "Regulatory fees", "Dividends".
- [unverified, forum, search snippet] "paper trading doesn't differentiate Market On Open (MOO) and Market On Close (MOC) orders. Those orders do not generally fill at the quote in live trading" (forum.alpaca.markets/t/opening-and-closing-market-prices-in-paper-trading/11664 and /t/accurate-opg-and-cls-prices-for-paper-trading/3762, not fetched).

Confidence: H for the cls semantics and 3:50 pm cutoff; M for the sales-team asterisk; L for paper MOC handling.

## A9. Rate limits

**Answer.** Market data API (Trading API plans): 200 requests/min on Basic, 10,000/min on Algo Trader Plus. Responses
carry `X-RateLimit-Limit/Remaining/Reset` headers, and going over returns 429. Trading API: **200 requests per minute per
API key**, from a deprecated Alpaca docs page (Wayback capture 2024-11-14). No current docs page states the trading limit.
Search snippets say the data subscription does not raise the trading limit and Elite accounts can get 1,000/min
[unverified, forum]. alpaca-py retries 429 and 504 by default (3 attempts, 3 s wait).

Quotes:
- MD: "Historical API calls | 200 / min | 10,000 / min".
- BARS: "Too many requests. You hit the rate limit. Use the X-RateLimit-... response headers to make sure you're under the rate limit."
- WB (deprecated v2 docs, capture 20241114115907): "There is a rate limit for the API requests. When it is exceeded, the API server returns error response with HTTP status code 429. The rate limit is 200 requests every minute per API key."
- PY `alpaca/common/constants.py`: `DEFAULT_RETRY_ATTEMPTS = 3`, `DEFAULT_RETRY_WAIT_SECONDS = 3`, `DEFAULT_RETRY_EXCEPTION_CODES = [429, 504]`.

Confidence: H for data limits; M for 200/min on trading (vendor text, but deprecated); L for the Elite figure.

## A10. alpaca-py 0.44.0 (latest on PyPI, uploaded 2026-08-11)

**Answer (from the 0.44.0 source, not from rendered docs).**
- `TradingClient(api_key=None, secret_key=None, oauth_token=None, paper=True, raw_data=False, url_override=None)`.
  **`paper` defaults to True.** Keys must be passed explicitly (no env-var lookup; see A1).
- `StockHistoricalDataClient(api_key=None, secret_key=None, oauth_token=None, use_basic_auth=False, raw_data=False, url_override=None, sandbox=False)`;
  `get_stock_bars(request)`. Corporate actions: `CorporateActionsClient.get_corporate_actions` (module `alpaca/data/historical/corporate_actions.py`). No auctions method.
- `StockBarsRequest` fields: `symbol_or_symbols`, `timeframe: TimeFrame`, `start: Optional[datetime]`, `end: Optional[datetime]`,
  `limit`, `currency`, `sort`, `adjustment: Optional[Adjustment]` (RAW/SPLIT/DIVIDEND/ALL), `feed: Optional[DataFeed]`
  (IEX, SIP, DELAYED_SIP, OTC, BOATS, OVERNIGHT), `asof: Optional[str]`. Docstring: "Timezone naive inputs assumed to be in
  UTC." `end` "Defaults to now."
- `OrderRequest` (base of `MarketOrderRequest`, `LimitOrderRequest`): `symbol`, `qty: Optional[float]`, `notional: Optional[float]`,
  `side`, `type`, `time_in_force: TimeInForce`, `order_class`, `extended_hours`, `client_order_id`, `legs`, `take_profit`,
  `stop_loss`, `position_intent`. The validator raises "At least one of qty or notional must be provided" and "Both qty and
  notional can not be set." `TimeInForce`: `DAY, GTC, OPG, CLS, IOC, FOK`. Submit with `TradingClient.submit_order(order_data)`.
- `TradingClient.get_account() -> TradeAccount`. Fields listed in A7, plus `account_number`, `status`, `currency`,
  `portfolio_value`, `accrued_fees`, `pending_transfer_in/out`, `transfers_blocked`, `account_blocked`, `created_at`,
  `trade_suspended_by_user`. Numeric fields are **strings** (e.g. `buying_power: Optional[str]`).

Quotes (PY, file `alpaca_py_0.44.0/src/alpaca/...`):
- `trading/client.py` lines 53-60: `def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None, oauth_token: Optional[str] = None, paper: bool = True, raw_data: bool = False, url_override: Optional[str] = None,`
- `data/historical/stock.py` lines 32-40 (as summarised above); `data/requests.py` lines 35-40, 80, 105-107; `trading/requests.py` lines 357-379; `trading/enums.py` lines 245-250; `trading/models.py` lines 529-561.
- Docs example (docs_us_working-with-orders.md, …/us/docs/working-with-orders.md, 08:37:13Z): "trading_client = TradingClient('api-key', 'secret-key', paper=True)".

Confidence: H (source code of the exact version). The rendered alpaca-py docs site was not fetched; the source is authoritative.

---

## What this means for the adapter

1. Paper setup costs nothing and needs no live funding. Create a dedicated paper account (choose $25,000 when creating it,
   if the dashboard offers it; otherwise accept $100k and size positions off our own notional). Generate keys per paper
   account. Our code must read the key env vars itself and pass them to alpaca-py, which does not read env vars.
2. Always pass `feed` explicitly on bars requests and record it. Keep `end` ≥ 15 minutes in the past if requesting SIP on
   the free plan. Test once whether a Paper Only Account can get `feed=sip` history (the docs conflict). Fall back to IEX
   and flag that the IEX close is a single-venue last trade.
3. Pull `adjustment=raw` bars and build our own total-return series from `/v1/corporate-actions` (cash_dividend `rate`,
   `ex_date`, splits). Do not depend on `adjustment=all`, whose method is undocumented and has forum reports of errors.
   alpaca-py cannot pass `spin-off` alone.
4. The daily close is the last eligible trade, not the official close. If the backtest used official closes, either call
   the SIP auctions endpoint over raw REST (alpaca-py has no wrapper) or accept a small basis gap. Daily `t` is midnight
   New York written in UTC: convert with America/New_York before taking the date, never take the UTC date.
5. Paper does not simulate dividends or HTB borrow fees, and probably fills CLS orders at the quote, not the auction. The
   forward ledger must credit and debit dividends itself (longs receive, shorts pay) and treat paper fill prices as
   approximate. If the closing auction matters, compare paper fills with the auctions endpoint.
6. MOC/LOC: submit before 15:50 ET (whole shares only; between 15:50 and 19:00 ET it is rejected). Confirm on the paper
   account that `cls` is accepted without contacting sales (the asterisk). Fractional sizing only works with `day` orders,
   so an MOC strategy must round to whole shares.
7. Shorts: need ≥ $2,000 equity. Prefer ETB names (free). Check `easy_to_borrow`/`borrow_status` before each short. Budget
   for the opening-short buying-power check at ask + 3%.
8. Leverage: 2x overnight on a ≥ $2,000 margin account. PDT counting is gone per the 2026 docs, but keep a guard in case
   the account object still reports `pattern_day_trader`/`daytrade_count`.
9. Rate limits are not binding for a daily strategy (200 data calls/min, about 200 trading calls/min). alpaca-py
   already retries 429.

## Could not establish

- The exact dividend-adjustment formula (factor versus subtraction, ex-date handling) for `adjustment=dividend|all`, and
  whether `capital_gains_distribution` counts as a "cash dividend" for adjustment. No vendor page found; forum not fetchable.
- Whether a Paper Only Account (IEX entitlement) can query SIP historical bars older than 15 minutes (vendor pages conflict).
- Whether and when daily bars are restated after the day, beyond the condition-`9` correction rule.
- Whether paper simulates the closing auction for `cls` orders (no vendor statement; forum snippets say no).
- Whether the "contact the sales team" asterisk on CLS/OPG/IOC/FOK applies to self-directed Trading API accounts.
- Whether paper enforces the HTB locate workflow.
- The date the intraday margin rule (end of PDT) took effect at Alpaca.
- A current docs.alpaca.markets statement of the Trading API rate limit (only the deprecated page states 200/min).
- The dashboard flow for choosing a paper balance on account creation (would need a login; not attempted).
