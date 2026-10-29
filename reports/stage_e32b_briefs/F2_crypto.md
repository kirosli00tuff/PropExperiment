# F2_crypto: family reader facts for MET, ETH, MBT, BTC (Stage E.32b, step F2)

Worker: CryptoReader-OpusHigh (Opus 5.5, high), 2026-10-28 23:04 to 23:20 PDT (times from `date`). WebSearch calls:
20 of 60. Full-text reads for T6: 4 of 12. Facts only, no scoring. Item ids refer to F2_crypto.json. New pages are
under reports/stage_e32b_briefs/pages/CRYPTO/ (log.tsv has the URL, UTC and PDT fetch times, method and sha256).
Reused E.28 facts cite reports/stage_e28_briefs/A1_crypto.json/.md and that stage's pages/A1_crypto/. No E.20
product file exists for any crypto code, and the E.29, E.31 and E.33c RETURN files have no crypto rows.

Quote note: quotes from PDFs write math symbols (T, R2_OOS, eta) as plain text and join hyphenated line breaks.
Parenthesised labels inside a quote are mine.

## Family-wide (all four codes)

### T7 sessions (F1 change)
- Until 2026-05-28: Sunday to Friday, 17:00 to 16:00 CT, with a 60-minute daily break from 16:00 CT. Closed from
  Friday 16:00 CT to Sunday 17:00 CT, so a weekend gap applied (CRYPTO-37, reused).
- From 2026-05-29: 24/7 trading on Globex (CRYPTO-38). CME's 24/7 page, fetched from Wayback with an unresolved
  capture date, mentions "shortened daily maintenance" and a Sunday start "at 4:05 p.m. CT". The exact maintenance
  windows (weekdays 16:00 to 16:02 CT, Saturday 02:00 to 04:00 CT) come only from a search summary [unverified].
- Settlement windows: BTC and ETH daily VWAP from 14:59:00 to 15:00:00 CT (BTC used 15:59 to 16:00 London at
  launch). Final settlement and the daily reference rates are at 16:00 London (CRYPTO-42). No study of a
  settlement-window effect was found.
- Handoff evidence on the underlying:
  - US-morning open to 17:00 EST (the CME break) on spot exchanges: the first half-hour predicts the last half-hour
    (Shen et al. 2022, full text; CRYPTO-39 and CRYPTO-17).
  - Spot activity, volatility and illiquidity peak at 16:00 to 17:00 UTC. This is an activity pattern, not a
    directional one (Brauneis et al. 2024, abstract; CRYPTO-40).
  - The weekend gap ("CME gap"): no academic study found. Fill-rate claims come only from trader posts
    (pointer, negative; CRYPTO-41).

### T4 scheduled events
- No crypto-specific scheduled release. BRR and ETHUSD_RR are price fixings (CRYPTO-31, reused E.28 F7).
- US macro releases and FOMC:
  - Benigno and Rosa (NY Fed SR 1052, full text): Bitcoin is "orthogonal" to monetary and macro news in windows of
    5 minutes before to 25 minutes after and 5 before to 55 after, 2017 to 2022. This is a null level response
    (negative; CRYPTO-27).
  - Ben Omrane et al. (2025 IREF, abstract): 5-minute data, 2016 to 2023. US monetary news moves volatility only,
    and ETH is more sensitive than BTC (CRYPTO-28).
  - Kroner, Mohammed and Vega (Fed Board, 2026): reactions to FOMC, CPI and NFP are "near-instantaneous", and
    volatility, volume and spreads stay elevated for up to about 30 minutes. Known only from a search summary; the
    repost page returned 404 (snippet, pointer; CRYPTO-29).
  - Frino et al. (2025 JFM, abstract): CME futures' share of price discovery rises around macro surprises
    (CRYPTO-30).
- No study documents a post-release drift of 5 minutes or more in BTC or ETH.

### T2 crowding
- T2a: no automated or HFT share of volume from any non-CFTC source (negative; CRYPTO-43). The CFTC series belongs
  to RatesReader's shared file.
- T2b, market-maker and incentive programs in force 2021 to 2026:
  - BTC: Cryptocurrency Futures MM Program, BTC, ETH, SOL and XRP, from 2018-03-05 to 2027-01-31 (CRYPTO-44).
  - ETH: Ether Futures MM Program, 2021-02-08 to 2021-08-31 as filed, and ETH is in the 2026 scope (CRYPTO-45).
  - MBT and MET: Micro BTC program from 2021-05-03; Micro Ether program from 2021-12-06 to 2025-01-31; Bitcoin
    Friday program, which includes MBT, from 2024-09-30 to 2025-07-31; Micro Crypto program from 2025-02-01 to
    2027-01-31 (CRYPTO-46).
  - New and verified from full text: the Micro Cryptocurrency Futures Market-Wide Fee Discount Program (MBT, MET),
    a fee incentive applied automatically to all participants, from 2023-03-01 to 2024-01-31 (CRYPTO-47).
  - Not outright futures: a BTIC/TAS MM program (2022-08-01 to 2025-01-31) and an options MM program
    (CRYPTO-48).
- T2c: no retail share of volume. The CFTC TFF nonreportable shares (MBT 19.9%, ETH 14.6%, BTC 7.0%, MET 3.3% of
  open interest, window W1) are a different statistic, because the reportable level is 1 contract (CRYPTO-49).

### T3 relationships
- MBT/BTC: a micro/full pair, mechanical. MBT's daily settlement is copied from BTC (CRYPTO-32).
- MET/ETH: a micro/full pair, mechanical (CRYPTO-33).
- Calendar spreads are listed for all four codes (CRYPTO-34).
- BTC/ETH: a cross-asset pair, with CME Ether/Bitcoin Ratio futures listed. Lead-lag evidence is mixed: Aleti and
  Mizrach say "BTC leads Ethereum price adjustment" (abstract); Chernoff (2026, abstract, Coinbase 1-minute data
  2022 to 2025) finds BTC leads ETH only in high-volatility regimes, with no lead in calm markets (CRYPTO-35).
- Futures-spot basis: no sourced number (negative; CRYPTO-36).

### T6 directional evidence, 5 minutes to the session

| Item | Study | Venue / product | Horizon | Data | OOS | Costs | Finding | Level |
|---|---|---|---|---|---|---|---|---|
| CRYPTO-20 | Akyildirim, Cepni, Corbet, Uddin 2021, Ann. Oper. Res. | CME BTC (same product) | 5-60 min | 2020-01..2020-09 | yes | gross | logistic accuracy about 54% (51-57%) | full_text (E.28 file) |
| CRYPTO-17 | Shen, Urquhart, Wang 2022, Financial Review | spot, 5 exchanges | last 30 min | 2013-2020 | yes, R2_OOS 1.09-1.61% | breakeven 3/7/10 bps per trade, "not profitable" at the 25 bps fee | positive, gross | full_text |
| CRYPTO-18 | Bouri, Lau, Saeed, Wang, Zhao 2021, IRFA | Bitstamp spot | intraday (hours) | 2014-11..2019-08 | yes | Sharpe 0.74 with an assumed 0.03% fee | positive | full_text |
| CRYPTO-19 | Wen, Bouri, Xu, Zhao 2022, NAJEF | BTC spot, plus ETH | intraday | 2013-03..2020-05 | n/a | n/a | momentum and reversal; timing beats buy-and-hold | abstract |
| CRYPTO-21 | Catania, Sandholdt 2019, JRFM | Bitstamp, Coinbase | up to 6 h | n/a | n/a | n/a | predictability up to 6 h, none at 1 day or more | abstract |
| CRYPTO-22 | Karasinski 2025, CEEJ | 16 cryptos | high frequency | n/a | test only | none | mostly unpredictable (negative) | abstract |
| CRYPTO-23 | Weiss, Gaudiosi, Zhou, Webb 2026, FRL | spot and Deribit perps | around option expiry | n/a | n/a | n/a | reversal around Deribit expiry | abstract |
| CRYPTO-24 | Chernoff 2026, JRFM | Coinbase 1-min | short | 2022-2025 | n/a | n/a | ETH after positive shocks only; no BTC effect | abstract |
| CRYPTO-25 | Quarter-hour effect, arXiv 2607.09426 | Binance perps | 4-12 h; weak at 5 min | n/a | yes | n/a | mixed | reused (E.28) |
| CRYPTO-26 | Moser, Brauneis 2026, IREF | ~400 cryptos | hourly | 2018-07..2022-01 | SPA test | n/a | some candlestick patterns predictive | abstract |
| CRYPTO-52 | Quantpedia (blog) | Gemini spot | 21:00-23:00 UTC | n/a | in sample | none | hour-of-day pattern | pointer |

No intraday directional study on ETH, MET or MBT themselves, and no CME study net of costs (CRYPTO-53, negative).

## Per code

### BTC (CME Bitcoin futures, 5 BTC; leader of MBT)
- T1, spread: no median. CME's weekly liquidity report gives AVERAGE spreads, session not stated:
  - 68.20 points (7.50 bps), 2026-01-05 to 2026-01-09 (CRYPTO-1).
  - 23.60 points (8.09 bps), 2023-04-17 to 2023-04-21 (CRYPTO-2).
  - At the $5 tick these are 13.64 and 4.72 ticks (my arithmetic). CME's own "ticks" column is inconsistent: it
    divides by 0.05, so it is not used.
  - Touch size: none found.
- F1: newer volume figure, ADV 12,167 contracts over 2026-01-05 to 2026-01-09 (E.28 had 13K for Oct 2023;
  CRYPTO-5).
- T5, settlement: financial. Daily settlement is the VWAP of BTC's own Globex trades; final settlement is the BRR at
  16:00 London (CRYPTO-6).
- T5, price discovery against spot is conflicting:
  - Futures lead or dominate: Kapar and Olmo (snippet), Akyildirim et al. 2020 (abstract), Aleti and Mizrach
    (abstract), Frino et al. 2025 ("generally lead", daily fluctuation, abstract).
  - Spot leads: Baur and Dimpfl 2019 (abstract).
  - Shares vary over time: Entrop et al. 2020, Dec 2017 to Mar 2019 (abstract).
  - CME minor: Alexander and Heck 2020 (snippet).
  - Items: CRYPTO-11 to -15 and CRYPTO-54.
- T6, best level: a same-product study, out of sample, gross of costs, 2020 (CRYPTO-20). Spot-venue peer-reviewed
  studies in full text: CRYPTO-17 and -18.

### MBT (Micro Bitcoin, 0.1 BTC)
- T1: no spread or touch size. A pointer only: a forum post in Jan 2022 put the "Micro bitcoin" spread at "25
  point", units undefined (CRYPTO-4).
- T5, settlement: financial, with DAILY settlement copied directly from BTC and final settlement to the BRR
  (CRYPTO-7).
- T5, information share:
  - Pati 2022 (abstract): MBT is about equal to or slightly above BTC (CRYPTO-51).
  - arXiv 2506.08718 (working paper, full text), MBT against Binance spot on five days in 2024: Hasbrouck IS
    0.52 to 0.56 on four days and 0.13 to 0.15 on 2024-08-05, when Binance had 0.84 to 0.87 (CRYPTO-10).
- T6: none on MBT itself. As a satellite it takes BTC's evidence (spec rule; not my call).

### ETH (Ether futures, 50 ETH; leader of MET)
- T1: no spread or touch size. Forum pointer: "around 3 points", Jan 2022 (CRYPTO-4).
- T5, settlement: financial. Daily settlement on ETH's own trades from 14:59 to 15:00 CT; final settlement to
  ETHUSD_RR at 16:00 London (CRYPTO-8).
- T5, information share: no study of CME ether futures against spot was found (negative; CRYPTO-16).
- T6: spot-only abstracts (Wen et al. 2022 includes Ethereum; Chernoff 2026); no CME ether study (CRYPTO-53).

### MET (Micro Ether, 0.1 ETH)
- T1: no spread or touch size. Forum pointer from Jan 2022: "easily > 10 ticks" and "around 35 points"
  (CRYPTO-4).
- T5, settlement: financial, with final settlement to ETHUSD_RR (CRYPTO-9).
  - CME's FAQ says "Daily settlement for Micro Ether futures will be the same as Ether futures", then describes
    ETH's VWAP (CRYPTO-50).
  - It reads as settling to ETH's price, but the wording is ambiguous: it does not say "copied" as the MBT filing
    does. The lead decides.
- T6: as ETH.

## Searched and not found (details in JSON searched_not_found)
- T1: a median main-session spread or touch size for any code (5 WebSearches plus a Wayback CDX check of
  cmegroup.com/reports/; only the BTC report exists).
- T2a and T2c: automated, HFT or retail share for any code.
- T5: an ETH or MET price-discovery study.
- T6: a directional study on ETH, MET or MBT, or a CME crypto study net of costs.
- T7: an academic study of the weekend gap or of the 2026 24/7 switch (the Runa Lee 2026 SSRN paper was not found
  by title).
- T4: a post-release drift study.

## Gaps and failures
- T1: BTC spreads are averages in points, with the session unstated and a one-week window. They are not
  main-session medians, and no figure exists for MBT, ETH or MET. The 27 Jul 2026 CME report capture is corrupted.
- Abstract-only items (several price-discovery and T6 items): the full texts sit on SSRN (blocked) or behind
  paywalls.
- Fetch failures:
  - Kapar and Olmo eprint: 401.
  - araid.es: 404.
  - AUT ACFR Frijns PDF: 403, bot check.
  - Substack repost of Kroner et al.: 404.
  - A Wayback CDX prefix query: 504.
  - Wayback capture-date lookups for the 24/7 page returned nothing.
- Scrapling and Firecrawl were not needed and not used.
- Not finished: ETH's MM-program coverage from 2021-09 to 2026, and MBT's 2024 program modifications (both
  unverified in E.28 and not re-fetched).
