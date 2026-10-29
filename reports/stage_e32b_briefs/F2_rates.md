# F2 rates (ROOT RATES): 2YY 5YY 10Y 30Y ZT ZF ZN ZB

Reader: RatesReader-OpusHigh (Stage E.32b, step F2). Started 2026-10-28 22:48 PDT; finished 23:05 PDT. Facts only,
no scores. Item ids refer to `F2_rates.json`; `CFTC-n` ids refer to `F2_shared_cftc_automation.json` (also owned by
this reader). Reused facts cite E.28 `A1_rates.json`/`.md` and E.20 `product_<ROOT>.json` by field path. New pages
are under `pages/RATES/` (log.tsv: 30 rows, 2 of them failed fetches). Helpers: `work/RATES/`.
WebSearch calls: 10 for rates plus 2 for the shared file, 12 in total (budget 70). New full-text reads for T6: 0 (T6 rows are E.20 reuse plus two abstracts).

## Family-wide facts

**Designs.** ZT ZF ZN ZB are physically delivered Treasury futures (CBOT Ch. 21, 20, 19, 18; RATES-28..31).
2YY 5YY 10Y 30Y are yield-quoted micro futures cash-settled to the 3:00 p.m. ET BrokerTec on-the-run benchmark,
daily settlement a 30-second VWAP before 2:00 p.m. CT (RATES-32). The micros settle off a cash fixing, not off a
futures sibling's settlement. Under spec 0, 10Y and ZN are not siblings for price transfer.

**T2a crowding (CFTC, shared file).**
- Interest Rate - US Treasury subgroup ATS share 73.1% (2016-18), 68.4% (2014-16), 64.0% (2012-14) (CFTC-12).
- 10 Yr Note 72.7%, 5 Yr Note 74.0% of volume (2016-18) (CFTC-24, CFTC-25).
- Coughlan-Orlov behavioural HFT share for the 10-year: 45.2% in 2020, 35.8% in 2012 (CFTC-50).
- The DMO 2019 'Financials' group has about 87% automated transactions in 2018, read from a chart (CFTC-59).
- ZT and ZB have no product-level figure (CFTC-29). The micros have no figure at all.
- PTFs supply 70% of ZN liquidity-providing volume (FEDS 2025-038), and JSR 2015 puts PTFs above 50% of Treasury
  futures volume (RATES-9).
- ATS is a FIX-tag flag that is broader than HFT (definition in the shared file).

**T2b programs.**
- Micro yields: Micro Treasury Yield (later Yield) Futures Market Maker Program, 2021-08-16 to 2028-02-29
  (RATES-10, E.28 F7).
- ZT/ZF/ZN/ZB: no market-maker or quoting program for the outrights found in 2021-2026 (3 queries). Found instead:
  - International Incentive Program (IIP), a fee-discount program for non-North-American proprietary firms, in force
    from 2011-12-16 to 2026-01-31. It lists "U.S. Treasury Futures $0.54" and "Micro Treasury Yield Futures $0.21"
    (RATES-11). It is a volume incentive, not quoting. Its table also lists products of other families (E-micro FX,
    Micro E-mini equity, Micro Dow, ag, NG).
  - Invoice Spreads IDB Incentive Program, 2024-09-01 to 2025-02-28 and 2026-08-01 to 2027-07-31. It covers ZT ZF ZN
    ZB only when executed as part of an invoice spread (RATES-12).
  - The "Long-Term U.S. Treasury Bond" MM program (2010-01-10 to 2022-01-31) is the Ultra Bond (UB), not ZB
    (RATES-13). Its start date matches the UB launch; the Chapter 40 name comes from a search snippet.

**T2c retail.** No retail share found. Small manual traders (a proxy) are 19.8% of ZN volume and 14.8% of ZF volume
(2016-18) (CFTC-40, CFTC-41).

**T3 relationships.**
- Curve inter-commodity spreads (implied books), 2023 ADV in legs: FIT/FYT 125,625; TUF 51,533; NOB 12,445
  (RATES-14). Type: mechanical/curve. No intraday study found.
- Calendar roll spreads; trading is concentrated in the front month (RATES-15).
- Micro yields against Treasury futures and on-the-run cash: different designs (RATES-16).
- Futures and BrokerTec cash: millisecond cross-market trading, futures usually lead, reverse often true (RATES-17;
  arbitrage-tight, sub-second).
- Futures order flow and cash yields, weekly (RATES-18).

**T4 events and absorption.**
- NFP (08:30 ET, monthly) in ZN, 2012-2015: permanent price change "restricted to the minutes, or in many cases
  seconds" (RATES-19, CFTC OCE). Balduzzi et al. (cited there): adjustment within the first minute (RATES-20).
  Fleming-Remolona (cash, 1990s abstract): volatility and volume persist; volatility-only (RATES-21).
- Slow-adjustment items:
  - FOMC: yields keep falling for about 3 h after the statement (SR 1188), with nulls before FOMC and around payrolls
    (RATES-23).
  - Auctions (13:00 ET): hours-scale pre-auction pressure and post-auction reversal, halved in 2015-2024 (RATES-24).
  - Pre-announcement drift before some releases in ZN 2008-2014, which needs the surprise sign (RATES-22).
  - Post-FOMC drift over days, abstract only (RATES-26).
  - Pre-FOMC drift: none in Treasuries (RATES-25, negative).
- Auctions per tenor: about 0.23 a week (RATES-27).

**T5 price discovery.**
- Mizrach-Neely (GovPX vs CBOT, to mid-2000s): 5y and 10y spot information shares "typically fail to reach 50% from
  1999 on"; futures shares are highest at long maturities (RATES-33; read from the rendered PDF page).
- Dobrev-Schaumburg 2015: the two markets "can effectively be seen as one" (RATES-34).
- ZT tick-cut study (abstract): price discovery moves to the finer grid (RATES-35).
- No study on the micros (RATES-36).

**T7 session.**
- Globex Sun 17:00 to Fri 16:00 CT, maintenance 16:00-17:00 CT, RTH 07:00-16:00 CT (RATES-49, RATES-50).
- Cash Treasury volume and volatility peak 08:30-09:00 ET with a smaller peak at 14:30-15:00 ET. Trading passes
  Tokyo to London to New York. Overseas changes are unbiased predictors of NY overnight changes (1994; RATES-51).
- Month-end strike moved from 3 pm to 4 pm ET (RATES-52).
- Settlement-window effect: rest-of-day return predicts the last 30 minutes to the end of settlement (Baltussen,
  via E.20; RATES-53).

## Per code

| Code | Spread S (ticks) | Touch (contracts) | Settlement | Best T6 level found (fact, not a score) | Notes |
|---|---|---|---|---|---|
| ZT | 1 (2018, old tick; RATES-1) | 99,471 avg 2018 (RATES-2) | physical (RATES-28) | Baltussen TU row, full text via E.20 (RATES-39), in sample to 2020 | Tick halved early 2019; no current-tick spread found; 2023 cost to trade 1,000 lots 1.78 ticks (RATES-6) |
| ZF | 1 (2018; RATES-1) | 1,319 avg 2018 | physical (RATES-29) | Baltussen FV row (RATES-38) | 1,000-lot cost 1.60 ticks 2023 |
| ZN | 1 (2018 RATES-1; 2013-16 RATES-3; Mar 2020 94% at 1 tick RATES-4) | 2,507 avg 2018 | physical (RATES-30) | Baltussen bond rows incl. TY, R2_OOS 0.86% per E.20 (RATES-37); Safari-Schmidhuber pooled (RATES-42); Robeco auction chart (RATES-43, practitioner) | Trade size median 2 (RATES-7) |
| ZB | 1 (2018) | 377 avg 2018 | physical (RATES-31) | Baltussen US row (RATES-40) | no product-level CFTC automation figure |
| 10Y | 1.67 average, 2024 (RATES-5) | none | cash, BrokerTec 3 pm ET (RATES-32) | none on the micro itself; Treasury futures rows listed with 10Y for information | MM program 2021-2028 |
| 2YY | none found | none | cash, BrokerTec | none on the product | MM program (via 10Y-2YY spread obligations) |
| 5YY | none found | none | cash, BrokerTec | none on the product | as 2YY |
| 30Y | none found | none | cash, BrokerTec | none on the product | as 2YY |

Spread S notes: the CME 2018 statement is ">99% of each trading day" at the minimum increment, so a median of 1 tick
is inferred, not published. Touch sizes are averages, not medians.

## Negative and null evidence

- Pre-FOMC drift absent in Treasuries (RATES-25).
- Majorin 2025 (abstract): "most intraday momentum and reversal trading strategies may not be feasible after
  costs", especially in bond and FX futures (RATES-41).
- Passive ZN fills adversely selected by about half a tick (RATES-47, excluded as a sub-5-minute or passive item).
- Rosa 2022 JFM: overnight-to-last-half-hour momentum disappears out of sample. The asset class is not in the
  abstract, so it is not attributed to rates (RATES-48).
- Own-tenor auction pressure roughly halved in 2015-2024 (RATES-24, E.20 decay field).
- Cusatis et al. 2009 (abstract): negative intraday serial correlation in T-note futures that "declined considerably
  over time" (RATES-46).

## Searched, not found

- T1: no post-2018 spread or touch size for ZT/ZF/ZN/ZB, and none ever for 2YY/5YY/30Y.
- T2b: no outright market-maker program for ZT/ZF/ZN/ZB in 2021-2026 (3 queries; absence is "not found").
- T2c: no retail share.
- T4: no study showing a mean drift of 5 minutes or more after US macro releases in Treasury futures (apart from the
  FOMC 3-hour window and the auction effects).
- T5: no post-2010 numeric information share.
- T6: no new product-level out-of-sample study beyond E.20's rows; nothing on the micros.

## Gaps and failures

- Bank of Canada PDFs (Jiang-Lo-Valente WP 2014-56; Campbell-Hendry WP 2007-43) returned an AWS WAF challenge to
  curl. They are logged as FAILED and not used. Scrapling was not tried (the terms check was not done in time).
- fedinprint.org timed out (curl rc 92/28). Mizrach-Neely was read from E.28's copy as a rendered image instead.
- Fleming-Remolona (scanned, no text layer, no OCR tool): only the abstract was read, from the page image.
- Balduzzi et al. 2001 was not fetched; it is cited through the CFTC 2015 paper.
- Whether IIP was extended past 2026-01-31 was not checked.
- The UB identification of the "Long-Term" bond program rests on a launch-date match plus a search snippet for the
  Chapter 40 title.
- F1: no changed E.28 fact found.
