# IBKR fact check (IBKRFactChecker-FableXHigh, Stage E.24)

Checked: reports/stage_e24_briefs/facts/ibkr_facts.md (I1 to I9) against ibkr_log.md and the saved pages under reports/stage_e24_briefs/pages/ibkr/. Run 06:12 to 06:25 PDT, 2026-10-18. The lead's 06:19 PDT course correction lifted the 06:40 stop (new stop 07:30) and allowed at most 6 fetches of official IBKR pages for contradicting evidence on I6, I4, I8 and I2; those fetches are logged in pages/ibkr/factcheck/factcheck_fetch_log.md.

Method. (1) Every logged sha256 and byte count in the log's fetch table was recomputed from the file on disk (scratch script hashcheck.py). (2) Every verbatim quote in each fact was searched as a whitespace-normalised substring of the cited saved file, its .txt text extraction and the tag-stripped HTML; where the reader joined two passages with "..." or the file carries line prefixes (`# ` in config.ini, markdown link syntax, bold markers) the pieces were searched separately. (3) The quotes were read against the stated answer. No page was loaded whole: grep, line ranges and short scripts only.

## Hashes

105 rows in the fetch table. 100 carry a sha256; all 100 match the file on disk, byte count included. 5 rows are logged `NA` (rows 2, 54, 84, 85, 96: an empty robots.txt, three rc=1 failures later refetched as rows 87/88, and the PyPI challenge). No HASH MISMATCH anywhere.

## Table

| Fact | Quotes checked | Found | Hash | Label | Reason (one line) |
|---|---|---|---|---|---|
| I1 Gateway, ports, restart, re-auth, IBC, 2FA | 35 | 35 (28 strict; 7 were the reader's "..." joins or `# `-prefixed config.ini lines, every piece present) | OK | OK | All quotes present; the three conflicting re-authentication statements are quoted exactly; the AcceptNonBrokerageAccountWarning quirk ("yes (the default)" comment vs shipped `=no`) is real. |
| I2 Paper account, trial, data sharing | 24 | 24 (one was a "..." join; both halves present in kb1719_rendered2) | OK | OK | Quotes support the hedged answer; the campus page does say "funded" and two lines later "don't need to fund ... must be approved"; the API requirements page says "A funded and opened IBKR Pro account". No saved or fetched page contradicts it. |
| I3 Delayed data | 15 | 15 strict | OK | OK | Delay table row reads `CME | CME | 10 minutes | CME Real-Time`; the off-by-one in the current tick table (ID 74 printed beside "Delayed Close") is real and the legacy table gives 75. |
| I4 Historical bars without a subscription | 16 (+2 absence checks) | 16 strict; 10167 and 10168 absent from both official error lists (the only other hits are SVG path numbers in campus pages) | OK | OVERSTATED | "Not allowed" with "high" confidence rests on one deprecated legacy sentence; the current docs are generic, and two official-site pages fetched today describe a delayed path (see Corrections, C1). |
| I5 Expired futures, pacing | 12 | 12 (one was markdown link syntax) | OK | OK | 2-year rule, small-bar pacing and 50 req/s are quoted exactly; the "lifted for 1 min+" statement is correctly flagged as legacy-only. |
| I6 Settlement vs last trade, date convention | 21 (+ settlement absence probe) | 21 (one was my own misattribution; "The prior day's closing price" is in tws_md_streaming-data row 16 and legacy_tick_types row 71) | OK | OK | The hedged answer ("can be the settlement ... not guaranteed ... treat as not reliably the settlement") is exactly what the legacy and current quotes support; no saved page (grep "settle" over all .txt/.md) documents a settlement price field or whatToShow value for the API. One citation is missing (C2). |
| I7 Twelve micros | 12 (+ row checks) | 12 strict; 7 of 12 margin rows re-read cell by cell (MNQ, MHNG, MZC, M6E, 30Y, MGC, MCL) match the table in the fact, including Has Options; all 12 symbols present with the stated exchange and trading class | OK | OK | MHNG/MNG quirk confirmed: `MNG` occurs only as the trading-class cell of the `NYMEX | MHNG | MICRO HENRY HUB NATURAL GAS | MNG` row. Multiplier and localSymbol are correctly marked [unverified]. |
| I8 Cheapest CME-group data, USD 500 rule | 34 | 34 (33 strict; "$500" is escaped `\$500` in the saved markdown, as the reader also wrote it) | OK | OK | Parsed the raw table rows: `CME Real-Time (L1) [14] | United States | USD 1.55 | N/A` in a `mdata non-pro` row, same for CBOT, COMEX, NYMEX; bundle row `USD 10.00 Base Waived for Activity + USD 0.01 per Snapshot` with footnotes 1,2,3,4,23,24,31; waiver table `USD 10.00 | USD 30.00`. The ambiguity the reader flags (footnote 4 as requirement or waiver; L1 rows sold alone?) stays open: the KB page that might settle it came back as a JavaScript shell. |
| I9 ib_async 2.1.0 | 26 | 26 (five were signature line-wraps or a sentence the text extraction split; all present in the raw api.html) | OK | OK | "Release 2.1.0" and "Version 2.1.0 (2025-12-06)" present; signatures match the docs build. |

Counts: OK 8, OVERSTATED 1, QUOTE NOT FOUND 0, HASH MISMATCH 0, UNSUPPORTED 0, CONTRADICTED 0.

## Corrections the lead must apply

C1 (I4, OVERSTATED). Change the answer from "**Not allowed** per IBKR's docs" to: "No current official page states that historical bars are served without a Level 1 subscription; the deprecated legacy page says the API 'always requires Level 1 streaming real time data to return historical data'; two official-site pages describe a delayed path without saying whether it reaches historical bars." Lower confidence from high to medium and add these two quotes:
- Official error-resolution page for 10089 (fetched 06:20 PDT, pages/ibkr/factcheck/err_delayed_available.html, sha256 in factcheck_fetch_log.md row 1): "Error 10089 notes that clients are requesting market data when they do not maintain a valid market data subscription. To resolve this issue, users must add a market data subscription to the specific user they are requesting market data with. Alternatively, users must request delayed market data prior to requesting market data." (generic "market data"; historical is not named)
- IBKR Campus staff reply, comments under "Using Pandas for Market Data Management" (posted June 27, 2024; reply undated; row 2 of the same log): "It may be that your account is not funded through Interactive Brokers, or that you do not have the relevant market data subscriptions. You may want to consider implementing a call to EClient.reqMarketDataType(3) to request Delayed Market Data prior to the historical market data request." This is an informal support reply on an official page, not documentation.
Adapter consequence: do not hard-code "historical bars will fail without a subscription"; probe `reqMarketDataType(3)` then `reqHistoricalData` on the paper account and record the outcome (errors 162, 354, 10089, 10186 or data). The reader's error-code list itself is correct.

C2 (I6, citation gap). The sentence "IBKR also says its historical data 'gets adjusted, compressed and filtered'" has no source in I6. Add: tws_md_introduction.html, row 17, 08:37:57Z (the quote is verbatim there and is already cited in I5).

C3 (I6, scope of the absence claim). "No documented API field or tick type carries the official settlement price" is true of every saved page (grep "settle" across all 80 text extractions hits only the legacy daily-bar note, the term-structure GUI page, the changelog's "Settlement Type", the margin table and non-API pages). State it as "none in the pages read", since the current docs site was not crawled exhaustively.

C4 (I3/I6 consistency, minor). I6 says "delayed tick 75 is 'The prior day's closing price'". The current page prints 74 beside that text (the off-by-one I3 documents); the legacy table says 75. Cite legacy_tick_types.html (row 71) for the number in I6, as I3 does.

No correction is needed to any number in I7 or I8, to any hash, or to any quote.

## Fetches made (6 of the 6 allowed)

| # | Result | Use |
|---|---|---|
| 1 | 200, 251,048 bytes, err_delayed_available.html | I4 quote (C1) |
| 2 | 200, 610,857 bytes, campus_pandas_market_data.html | I4 quote (C1) |
| 3 | 404 (docs/tws-api/doc/market-data-historical/introduction) | none: URL from the search engine does not exist |
| 4 | 404 (.../market-data-historical/historical-bars/receiving-historical-bars) | none |
| 5 | 404 (docs/tws-api/doc/notes-limitations/limitations/paper-trading) | none; the saved tws_notes-limitations_tws-api-limitations.html already holds the "approved and funded" paper-trading paragraph |
| 6 | 200, 5,801 bytes, kb_subscription_considerations_us.html: JavaScript shell, 27 characters of text | none |

Firecrawl: all four `firecrawl_search` calls returned 402 (account out of credits) at 06:17 PDT; not retried. WebSearch (4 calls) was used to locate URLs only; nothing from a search summary is cited.

## Unchecked or not resolvable from disk

- I8: whether the four USD 1.55 single-exchange L1 subscriptions can be bought without the USD 10 bundle, and whether footnote 4 ("Accounts must generate at least USD 30 in commissions") is a requirement or only the waiver. The KB FAQ that might answer it (ibkrguides.com/kb/subscription-consideration-us-market-data.htm) needs a rendered fetch (scrapling fetch), which would be a seventh fetch.
- I2: a current official API page on paper trading other than the saved limitations/requirements pages. The search engine's URL for one 404'd. The web-search summary claimed an official page says trial accounts are not supported for the API and that an approved-but-unfunded account's paper user can request delayed data; neither claim was verified against a fetched page and neither is used above.
- I6: no contradicting official statement was found; the absence of a settlement field is established only over the pages on disk (C3).
- I7: 5 of 12 margin rows (M2K, 2YY, 10Y, MZS, MZL) were confirmed present with the right exchange and trading class but their margin figures were not re-read cell by cell. Margins are for information only in the fact.
- ib_async source-level quotes (wrapper.py, util.py) are from the `main` branch, as the reader states; the 2.1.0 tag was not compared.
