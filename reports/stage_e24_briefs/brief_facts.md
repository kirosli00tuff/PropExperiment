# Brief B1/C1: fact readers (IBKRReader-OpusHigh, AlpacaReader-OpusHigh; worker-high, opus). Stage E.24

Read-only research from official sources. No broker or data endpoint is called, no account is opened, nothing is
bought, no API key is used or read. Read each site's terms of use (and robots.txt) before any automated fetch and log
what they allow. Save every page used as evidence raw under reports/stage_e24_briefs/pages/<ibkr|alpaca>/ with its
URL, UTC fetch time and sha256 in your log; read saved pages by grep, never whole. Fetch order: WebFetch; on failure
`scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`; Firecrawl only if Scrapling fails.
Keep your own scripts in reports/stage_e24_briefs/scripts/<ibkr|alpaca>/ (private; the other reader has its own).
Space requests to any one site. If a WebSearch returns an over-budget notice, stop searching, write it in your log with
the time and return; never continue from memory. Every fact carries a verbatim quote from a saved page, or is marked
[unverified]. Prefer the vendor's own docs; mark anything from forums or third parties as such.

Output: reports/stage_e24_briefs/facts/<ibkr|alpaca>_facts.md with one numbered row per question below: answer, verbatim
quote(s), URL, saved file, UTC fetch time, confidence; then a short "what this means for the adapter" list and
"could not establish". Plus reports/stage_e24_briefs/facts/<ibkr|alpaca>_log.md (every fetch, terms read, failures).
Return the path, a summary of at most 200 words, and anything unfinished.

## IBKR questions (IBKRReader; official interactivebrokers.com pages, the TWS API docs, ib_async docs on GitHub/readthedocs, IBC on GitHub)
I1. IB Gateway on Linux: install, the paper login, API port defaults (paper vs live), the daily automatic restart and
    the weekly (Sunday) re-authentication; what IBC (IbcAlpha/IBC) automates, how it takes credentials (config.ini
    keys, start-script variables), and whether paper logins need two-factor authentication.
I2. Paper account: requirements (does a paper account need a funded live account? any free trial paper account?),
    and whether a paper account shares the live account's market data subscriptions.
I3. Delayed market data in paper and via API (reqMarketDataType 3/4, the 10- or 15-minute delay for CME futures).
I4. Historical daily bars of CME futures via reqHistoricalData without a subscription: allowed or not; delayed
    historical data rules; the error codes seen without permissions (e.g. 162, 354, 10167, 10168).
I5. Expired futures: includeExpired, how far back expired contracts' history is available (e.g. two years after
    expiry), and the pacing limits for historical requests.
I6. THE KEY QUESTION: is the daily bar's close (whatToShow TRADES; also MIDPOINT, ADJUSTED_LAST, and any settlement
    option) for a CME future the official exchange settlement price or the last trade? Is there any API field or tick
    type that carries the settlement (e.g. tick types for "close" on futures being the prior day's settlement)? Quote
    exactly. Also: the daily bar's date convention and time zone for CME Globex futures (session date vs calendar date),
    and the formatDate / timezone parameters.
I7. Contract definitions for the 12 micros of E22-F1 (MNQ, M2K, MGC, MCL, MNG, M6E, 2YY, 10Y, 30Y, MZC, MZS, MZL):
    exchange codes in IB (CME, COMEX, NYMEX, CBOT), localSymbol format, lastTradeDateOrContractMonth, multiplier,
    and any known quirks (e.g. yield micros quoted in yield; MZC/MZS/MZL product availability at IBKR).
I8. The cheapest CME market data subscription(s) covering these products (CME, CBOT, NYMEX, COMEX; non-professional),
    the price, the bundle names, and the funded-account rule for market data (minimum equity) — with quotes.
I9. ib_async: connect(host, port, clientId), reqHistoricalData signature, qualifyContracts, reqContractDetails,
    disconnect/reconnect events, placeOrder/Trade/fill objects; the version 2.1.0 docs if available.

## Alpaca questions (AlpacaReader; docs.alpaca.markets, alpaca.markets terms/disclosures, alpaca-py docs/GitHub)
A1. Paper account: how to create one, whether it needs a funded live account, default paper balance and whether it can
    be reset/set (e.g. to $25,000), the paper API base URL, and key generation (key id/secret; env names alpaca-py uses).
A2. Market data plans: the free (Basic) plan's feeds (IEX real time; SIP historical with a 15-minute restriction?);
    which feed historical daily bars come from on the free plan; the paid plan and price.
A3. Historical daily bars: how far back; the `adjustment` parameter (raw, split, dividend, all) and what each does;
    whether "all" adjusts for distributions (cash dividends) and how (factor method); the corporate actions endpoint.
A4. Which close the daily bar carries (last trade of the consolidated tape incl. the closing auction, the official
    closing price, or the IEX last trade), the bar timestamp convention and time zone, and whether bars are revised.
A5. Fractional orders: which order types and time-in-force allow fractional quantities, notional orders, long only;
    fractional shorts.
A6. Short selling in paper: easy-to-borrow only? borrow fees in paper; hard-to-borrow handling; margin requirement for
    shorts.
A7. Margin and buying power: Reg T (2x overnight, 4x intraday for pattern day traders), the $2,000 minimum for margin,
    the overnight buying power field names in the account object (e.g. regt_buying_power, non_marginable_buying_power,
    multiplier), and paper specifics.
A8. Order types at or near the close: market-on-close (MOC), limit-on-close (LOC), time_in_force "cls", cutoff times,
    whether paper simulates the closing auction and how paper fills are simulated.
A9. Rate limits (requests per minute for trading and data APIs).
A10. alpaca-py 0.44.0: TradingClient(paper=True), StockHistoricalDataClient, StockBarsRequest fields (timeframe, feed,
     adjustment, start/end), MarketOrderRequest (qty vs notional, time_in_force), get_account fields.
