# Alpaca fact check (Stage E.24, AlpacaFactChecker-FableXHigh)

Written 2026-10-18 06:25 PDT (13:25Z). Checked: `facts/alpaca_facts.md` (01:47 PDT) and `facts/alpaca_log.md`
against the saved pages under `pages/alpaca/`. I did not write the facts. Method: (1) every logged sha256 recomputed
and compared with the file; (2) every quoted fragment (129 fragments across A1-A10) searched as a whitespace-normalised
substring of the cited file, with two looser passes (curly quotes and markdown backslash escapes removed; HTML tags
stripped) and the pass level recorded; pages read by grep and line ranges only; (3) the surrounding text read for each
answer to judge support. After the lead lifted the no-fetch rule, 4 official docs.alpaca.markets pages were fetched
(allowance 6; terms covered by the reader's log: robots allows all, T&C has no scraping clause) and saved under
`pages/alpaca/factcheck/` with `fetch_log_factchecker.tsv`. No broker or data API endpoint, account or key was used.

## Hashes

- 39 log rows: 38 files present, 38/38 sha256 and byte counts match. Row #36 (`alpaca_deprecated_api-v2.html`) is
  absent on disk, as the log's Failures section says (deleted 404 page; its hash equals row #2's 404 page).
- `alpaca_TermsAndConditions.pdf.txt` is on disk but not in the table: the log declares it a derived pdftotext file.
- The wheel's sha256 (row #39) equals the digest in the saved PyPI JSON (`b54673f967c0c814...`); the 0.44.0 upload
  time in that JSON is 2026-08-11T10:15:07Z, matching A10's heading.
- Five files under `pages/alpaca/factcheck/` with their own `fetch_log.tsv` (08:57Z, after the reader finished at
  about 08:50Z; fetcher not named in the reader's log) all match that log's sha256. I used two of them as
  supplementary evidence (marked below); they are not the reader's citations.

## Quote search

129 fragments: 124 found verbatim (whitespace-normalised); 1 found after curly-quote/backslash normalisation
(A6, ORD short-sell buying-power sentence); 1 found after HTML tag stripping (A9, Wayback rate-limit sentence, whose
source has inline tags); 3 not found as typed, all explained and confirmed by inspection:
- A8 "CLS | Yes\* | Yes\* | No | No" and "CLS | No | No | No | No" (and A5's GTC/DAY/IOC-FOK-OPG-CLS rows): the ORD
  page holds these tables as `<HTMLBlock>` HTML, not markdown pipes. Parsing the three tables (ORD lines 497-547,
  663-713, 995-1045) gives exactly the rows the reader states: whole-qty CLS = Yes*, Yes*, No, No; fractional GTC,
  IOC, FOK, OPG, CLS all No, DAY all Yes. The reader labelled them "parsed from the HTML block"; they are
  reconstructions, not verbatim text, and the "IOC/FOK/OPG/CLS" line merges four separate rows.
- A10 `TradingClient.__init__` signature: the source spreads it over lines 53-61, one parameter per line; the
  parameters and defaults (`paper: bool = True`, etc.) are exactly as stated.

## Table

| Fact | Label | Reason (one line) |
|---|---|---|
| A1 Paper account | OK | All 17 fragments verbatim; env-var claim holds (grep hits only the two docstrings, no code reads `environ`/`getenv`); "$25k by creating a new account" correctly hedged M. |
| A2 Plans and feeds | OK | All 14 fragments verbatim; the IEX-only vs SIP-after-15-min conflict is real and correctly left open; MD line 80 and alpaca.markets/data add support for delayed SIP on the free plan (see corrections). |
| A3 Bars depth, adjustment, CA | OK | All 20 fragments verbatim; `all` = split + dividend + spin-off per BARS; cash_dividend fields present in CA; no vendor page on disk (incl. mandatory-corporate-actions.md) states the price-adjustment formula. |
| A4 Daily close | OK | All 15 fragments verbatim; FAQ table columns are open/close, high/low, volume in that order, so the M/6/T/9 readings are right; `U` row (D: red, red, green) confirms the unquoted `U` claim; 171.21 is the `feed=sip` block (iex block closes 171.29). |
| A5 Fractional orders | OK (fix label) | Conclusion right, but "fractional shorts [unverified]" is wrong: FR line 84 states "We do not support short sales in fractional orders. All fractional sell orders are marked long."; FR line 20 confirms pre/post/overnight hours. |
| A6 Short selling | OK | All 10 fragments found; round lots of 100, single-use, non-refundable locates and the 3-day weekend charge are at MS lines 90-92 and 104. |
| A7 Margin, buying power, PDT | OVERSTATED (PDT sentence only) | Reg T 50%, $2,000, 2x overnight, 4x intraday, maintenance table, 6.50%/5.00%, field list: all verbatim. "PDT has ended at Alpaca" exceeds the pages: PDT1 lines 82-83 say a 12-month interim follows SEC approval in which firms may apply either regime; no page says which regime Alpaca applies or from when. |
| A8 Close orders, paper fills | OK | cls row, 3:50 pm/7:00 pm cutoffs, routing sentence, asterisk note (ORD line 382, Trading API docs) and all PT fill statements verbatim; table rows reconstructed from HTML but accurate; forum claim stays [unverified]. |
| A9 Rate limits | OK | MD, BARS (429 and 400 responses carry X-RateLimit-Limit/Remaining/Reset) and constants verbatim; Wayback sentence verbatim after tag stripping, page title "API v2 - Documentation \| Alpaca"; the capture timestamp is not in the saved file (see unchecked). |
| A10 alpaca-py 0.44.0 | OK | Signatures, enums (DataFeed 6 members, Adjustment 4, TimeInForce 6), StockBarsRequest fields, validator messages, TradeAccount fields (numerics as `Optional[str]`), docs example: all confirmed in source; one line cite off (TimeInForce members are lines 229-234, not 245-250). |

Counts: OK 9 (A5 with a required label fix), OVERSTATED 1 (A7, one sentence), QUOTE NOT FOUND 0, HASH MISMATCH 0,
UNSUPPORTED 0, CONTRADICTED 0.

## Corrections the lead must apply

1. **A5, fractional shorts.** Replace "No page explicitly allows fractional short selling. ... fractional shorts are
   [unverified] but very likely rejected" with the vendor statement, FR (docs_us_fractional-trading.md) line 84:
   "We do not support short sales in fractional orders. All fractional sell orders are marked long." Confidence for
   long-only becomes H. Also add FR line 88, "Limit orders are supported for both fractional and notional orders.
   Extended hours are also supported with limit orders (same as whole share orders).", as the basis for the
   extended-hours claim (extended-hours fractional = limit orders; the ORD extended-hours table shows market orders
   No for every TIF).
2. **A7, PDT status.** Soften "**PDT has ended at Alpaca**" to: FINRA's intraday margin rule replaces the PDT
   framework; Alpaca's three pages describe the new rule; PDT1 lines 82-83 state "Following SEC approval, a 12-month
   interim transition period will commence." and "During this 12-month window, member firms may apply either the
   legacy PDT rules or the new intraday margin rules (by account or across the firm) as they transition their
   systems."; PDT2 line 24 adds "individual firms may still maintain their own 'house' requirements". No page states
   which regime Alpaca applies, or a calendar date. Keep the adapter guard on `pattern_day_trader`/`daytrade_count`
   (alpaca-py still carries both; the account reference no longer lists them: confirmed, 0 hits in ACC). Supporting
   but not decisive: docs_us_account-plans.md (#14, updatedAt 2026-07-07) lines 402-403 describe multiplier 2 as
   "the default for all accounts with $2,000 or more equity" and 4 as "accounts with 4x intraday BP and 2x reg T
   overnight BP" with no PDT wording, while ACC still says "non-PDT accounts" and "PDT account".
3. **A7, could-not-establish item.** Change "The date the intraday margin rule took effect at Alpaca" to note that
   PDT1 does give a relative date (12 months after SEC approval, firm's choice during the interim) but no calendar
   date and no Alpaca-specific statement.
4. **A2, free-plan SIP.** Add two vendor lines that support the "SIP when `end` is at least 15 minutes old" reading:
   MD line 80, "similar to the free plan all the standard plans are real time IEX or 15 mins delayed SIP" (Broker API
   section, but it characterises the free plan), and alpaca.markets/data Free plan row "Real-time (latency): Yes, via
   websocket 15 minute delay via API" (pages/alpaca/factcheck/alpaca_data.html, fetched 08:57Z by another worker,
   sha256 b0690ea0...). The Paper-Only-Account IEX sentence (PT line 20) still conflicts; the hedge stays. The `us/`
   variants of MD, HS and FAQ re-fetched at 13:23Z are byte-identical to the reader's copies (same sha256), so the
   conflict is current vendor text, not drift.
5. **A4, `U` code and example.** Add the FAQ row for the unquoted `U` claim: "`U` | Extended Trading Hours | ABCO |
   MD | :red\_circle: | :red\_circle: | :green\_circle:" (line 304). Note that the quoted 171.21 example is the
   `feed=sip` block; the `feed=iex` block for the same day closes at 171.29 (FAQ lines ~96-107), a vendor illustration
   that the daily close depends on the feed.
6. **A1, env-var grep.** "A grep of the whole package for `environ|getenv` finds nothing" should read "finds only two
   docstrings (common/rest.py:342, data/historical/crypto.py:283); no code reads environment variables".
7. **A5/A8, table quotes.** Mark the ORD TIF-table rows as reconstructed from the page's HTML block (tag-stripped),
   not verbatim markdown; split "IOC/FOK/OPG/CLS | No | No | No | No" into its four rows.
8. **A9, Wayback.** Mark the capture timestamp 20241114115907 as taken from the HTTP 302 Location header at fetch
   time; the saved `id_` capture contains no archive marker, so it cannot be re-verified from disk.
9. **A10, line cite.** trading/enums.py `TimeInForce` members are lines 229-234 (class at 228), not 245-250.

## Supplementary findings (no correction needed)

- A3: `pages/alpaca/factcheck/docs_us_mandatory-corporate-actions.md` (another worker's fetch, 08:57Z) covers how
  positions and open orders are handled for dividends, splits, spin-offs and mergers; it does not describe the
  historical-bar price-adjustment formula, so the reader's "not documented on any vendor page found" stands.
- A3: CA lists 16 types (reverse_split, forward_split, unit_split, cash_dividend, stock_dividend, spin_off,
  cash_merger, stock_merger, stock_and_cash_merger, redemption, name_change, worthless_removal, rights_distribution,
  partial_call, reorganization, capital_gains_distribution); fields rate, special, foreign, ex_date, record_date,
  payable_date, process_date all present.
- A4: FAQ line 341: "if a trade only updates the volume, but none of the prices, then no bar is generated", and
  non-minute/non-daily bars are aggregated from minute and daily bars. Consistent with the reader's account.
- A4: FAQ line 183 says the latest endpoints "always return the data as it was received at the time (this is also why
  there is no `adjustment` parameter on the latest bars)". Nothing on restatement of historical bars; the
  could-not-establish item stands.
- A8: ORD line 367 (`day` TIF): "By default, the order is only valid during Regular Trading Hours (9:30am - 4:00pm
  ET). If unfilled after the closing auction, it is automatically canceled."
- A8: ORD line 382 sits in "Order Types vs Supported Time in Force" on the Trading API orders page; it applies to the
  whole-qty rows IOC/FOK/OPG/CLS (market and limit). Whether self-directed accounts must contact sales remains
  ambiguous, as the reader says.
- A7: the `-1` variant of the end-of-PDT page (fetched 13:23Z) differs from the reader's copy only in the front-matter
  `updatedAt` (20:11:42Z vs 19:36:31Z on 2026-04-27) and a trailing `<br />`; no new content.

## Unchecked or not verifiable from disk

- Forum snippets in A3, A8, A9: not fetchable under the forum ToS; they remain [unverified, forum] by design.
- A9: the Wayback capture time (see correction 8) and the claim that no current docs page states the Trading API
  limit: the two llms.txt indexes list only Broker API "Rate Limits" pages, which supports it, but the indexes may not
  be exhaustive.
- A2: whether a Paper Only Account can query SIP history older than 15 minutes: would need an API call, which this
  check did not make.
- A1: the dashboard flow for choosing a paper balance (needs a login; not attempted).
- alpaca-py source was read by grep and line ranges only; not imported or executed.

## Fetches made by this check (pages/alpaca/factcheck/fetch_log_factchecker.tsv)

| UTC | URL | file | HTTP | bytes | sha256 |
|---|---|---|---|---|---|
| 2026-10-18T13:23:16Z | https://docs.alpaca.markets/us/docs/historical-stock-data-1.md | fc_docs_us_historical-stock-data-1.md | 200 | 2765 | f5c481f99797985246a69fc2938871ee2e2820b8ff106b20b1e0493d7a985fad (= reader's HS) |
| 2026-10-18T13:23:19Z | https://docs.alpaca.markets/us/docs/market-data-faq.md | fc_docs_us_market-data-faq.md | 200 | 34729 | b6d9225409d2211b60cfeed72e8716fc1e05f2d7593ffed6dc120a0b5ebaef13 (= reader's FAQ) |
| 2026-10-18T13:23:21Z | https://docs.alpaca.markets/us/docs/about-market-data-api.md | fc_docs_us_about-market-data-api.md | 200 | 7924 | ff3f8537b88c7e2640fc6f60ed0143a7441c9f503e23c1da8c889f04c9b9362f (= reader's MD) |
| 2026-10-18T13:23:23Z | https://docs.alpaca.markets/us/docs/understanding-finras-new-intraday-margin-rule-and-the-end-of-pdt-1.md | fc_docs_us_finra_end_of_pdt-1.md | 200 | 9182 | 6a8d18652430b13e95b362bf3afced4ecb03b2cc7819b3340fd38cb7e56fa4c3 |

Two of the six permitted fetches were not used: the llms.txt indexes list no further Alpaca docs page on bar
adjustment, fractional shorts or Alpaca's PDT transition, so no other official page was likely to contradict A2-A5 or
A7. Scripts used: scratchpad `fc/check_hashes.py`, `fc/check_quotes.py`, `fc/ctx.py`, `fc/fetch_fc.sh` (not in the
repo).
