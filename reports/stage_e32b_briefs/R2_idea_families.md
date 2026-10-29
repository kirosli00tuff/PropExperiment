# R2 idea families (Stage E.32b, step 3b input): IdeaFamilies-OpusHigh, 2026-10-28

What this file is: the directional idea families a one-contract retail system could run with market orders at holds
from 5 minutes to the session close (overnight holds listed apart), on the 47 codes of spec section 0 (NQ excluded,
V49). It gives each family's mechanism, codes, horizons, evidence (including null, negative and fast-absorption
evidence), data needs and its overlap with R1. It does not rank, score or pick. Full rows, quotes and files are in
R2_idea_families.json (12 families, 122 evidence rows). Item ids refer to F2_<family>.json, SB-n to
F2_shared_baltussen.json, and R1-nn to R1_closed_lines.json.

Sources: the eight F2 family files (T3, T4, T6 and T7 items), the shared Baltussen file, R1 (including its
"Ambiguous: for lead" list), and the E.32 methods brief (front, verdict table, R4, M1). Also the E.28 C3 draft, the
planner notes (used as pointers), and DECISIONS V45 with E.25 DF3. The E.28 C2 deep dives are about method only: none
holds directional evidence at 5 minutes or more. No page was fetched and no WebSearch was used (log:
pages/IDEAS/log.tsv).

## Facts that cut across families

- V38 as amended by V45 item 4 says that no published post-2015 intraday effect on the 17 E.20 roots exceeds 1.5 x the
  D8 round trip. The exceptions are three working-paper effects (pre-refunding ZN, pre-FOMC ZN, ES 3rd-Friday), none
  with a significant post-2015 estimate (DECISIONS:910-916).
- E.25: information is priced within 1 to 5 seconds on ES, NQ, ZN and CL (C3 draft:70-71).
- E.32 front: no commodity-futures study shows positive out-of-sample predictability net of costs at 1-240 minutes.
  Event families and once-a-day families fail on power over 39 months (E.32 methods brief:15-16 and verdict table).
- E.28 C3: on 1-minute bars the robust MES patterns were worth about 0.1 tick against a 2.1-tick round turn.

## Family index

| id | family | codes with direct product evidence | strongest evidence (as recorded) | weakest or contrary evidence | R1 overlap |
|---|---|---|---|---|---|
| F01 | Market intraday momentum into the close | MNQ (via NQ), RTY, YM, ZT ZF ZN ZB, GC, SI, NG, 6A | Baltussen et al. JFE 2021, recursive OOS R2 on product rows (NQ 3.76%, RTY 3.15%, YM 2.18%, ZF 0.93%), gross, to 2020-05 | post-2018 decay or regime (EQUITY-39, -40, -41); null on CL, HG, all grains, 6E; program H6 net negative | R1-14, R1-13, R1-03..09 (CP1), R1-15, R1-18, R1-23 |
| F02 | Energy inventory release drift or reversal | CL QM MCL, NG QG MNG | CL over-reaction half reversed within 4 h (CRUDE-52, 2007-2014); USO slow adjustment (CRUDE-20, in sample) | absorbed within minutes (NATGAS-25..27, CRUDE-14, CRUDE-51); NG net negative after 2011 (NATGAS-39) | R1-06, R1-23 (V39), R1-11/12 |
| F03 | USDA report drift (WASDE, NOPA, others) | ZC ZS ZW ZM ZL and their minis and micros | soybean WASDE reaction grows to the close, 2010-2021 (GRAINS-18, WP) | about 10 min and no under- or overreaction (GRAINS-19, -21); Huang's drift needs the 60-min sign | R1-08, R1-21, R1-23 (grains not named) |
| F04 | US macro release drift | rates, equity, metals, FX, crypto | ES continuing adjustment 10-30 min (EQUITY-17); copper and silver delays (METALS-23, 2002-08) | rates and FX absorbed in seconds to minutes (RATES-19, FX-22); BTC orthogonal (CRYPTO-27) | R1-01 (MES), R1-04 |
| F05 | FOMC post-statement drift | ZT ZF ZN ZB, equity, GC, FX | Treasury yields fall about 3 h after the statement, 1997-2024 (RATES-23, cash) | pre-FOMC equity drift gone after 2015; BTC null; K5-fomc-01 MGC null | R1-04, R1-07, R1-19 |
| F06 | Pre-scheduled drift and supply pressure | ZT ZF ZN ZB, NG | pre-FOMC ZN futures +7.26 bp t 2.82 (2004-2025); auction pressure (RATES-24) | no post-2015 split; auction effect halved 2015-2024; 4-8 events a year | R1-04, R1-13 (H3), R1-19 (V45), R1-06 |
| F07 | Fixes and month-end rebalancing | 6E 6A, ZT ZF ZN ZB, GC SI | Evans month-end fix, net of half spread, post-2010 OOS 3.25%/yr (spot) | liquidity demanders negative after costs (FX-38); LBMA done in minutes after 2015; silver fix gone 2014 | R1-05, R1-07, R1-04, R1-13, R1-18 |
| F08 | Regional-session and overnight-to-day handoffs | 6E 6A, equity, GC, CL, grains, crypto | EUR/USD local-hours effect net of EBS spread, 1997-2007 (FX-37) | European open net Sharpe -0.5 (EQUITY-51); AUD net negative; DCE and corn effects arbitraged (GRAINS-42, -17) | R1-01, R1-03..09 (CP3), R1-13 (H4), R1-10, R1-05 |
| F09 | Cross-market lead-lag and relative value | soy crush codes, ZC calendars, equity, GC/SI, 6A, crypto | crush cointegrated on 180 of 243 day sessions (GRAINS-15, 2015) | ZM crush and propagation closed (R1-21); most links are seconds-scale (CRUDE-33, GRAINS-24) | R1-21, R1-08, R1-10, R1-13, R1-20 |
| F10 | Order-book state at 5 minutes and longer | any; grains (abstract) | lagged imbalance predicts some grains (GRAINS-41, abstract, horizon unknown) | forward predictability insignificant by 5-30 min (E.32 M1); ZM S3 negative | R1-21 (V56 item 2: open for other products), R1-20, R1-11 |
| F11 | Own-price-path trend and reversal | any | Safari-Schmidhuber OOS on 16-24 futures, 2010-2023 | OOS R2 0.55 bp gross; noise-area dropped (V45 item 3); MNQ and NQ preprints negative | R1-01, R1-03..09 (CP2, fades), R1-11, R1-15, R1-21 (S4) |
| F12 | Expiry and option-hedging days | equity, crypto | gamma imbalance drives end-of-day momentum or reversal (Barbon et al., stocks) | ES 3rd-Friday not significant in 2015-23; no evidence on NQ/RTY/YM codes | R1-14 (T3 GEX), R1-23 (C2), R1-09, R1-19 |

## Per family (facts; full rows in the JSON)

### R2-F01 Market intraday momentum into the close
- Mechanism: option market makers short gamma and leveraged ETFs rebalance in the direction of the day's move before
  the close: "Hedging short gamma exposure requires trading in the direction of price movements, thereby creating price
  momentum" (Baltussen file:84-85). The flow is non-informational and comes at a known time.
- Horizon: 30 minutes, entering at close-30. Class closes: equity at the cash close; bonds 13:30-14:00 CT; GC
  12:00-12:30 CT; NG 14:00-14:30 ET; FX at the pit close, 14:00 CT. Overnight: the effect reverts over the next days
  (SB-7).
- Evidence for:
  - 2000-2020 pooled beta_ROD (t), R2%: equity 3.98 (6.65), 2.34; bonds 1.53 (3.61), 0.47; commodity 1.04 (2.86),
    0.12; currency 0.33 (1.45), 0.04, not significant.
  - Product OOS R2: NQ 3.76%, Russell 3.15%, YM 2.18%, SI 1.01%, ZF 0.93%, NG 0.92%, ZN 0.86%, ZT 0.70%, ZB 0.22%,
    6A 0.17%, GC 0.08%.
  - Gross only. The paper says "we do not consider transaction costs" (SB-6). SPY net of spread 2005-2013: 6.52%/yr
    (EQUITY-36).
- Evidence against:
  - Null or negative on CL, HG, ZL, ZC (in sample only), ZM, ZS, ZW, 6E and UB.
  - ES momentum reverses when dealer gamma is high, 2018-2024 (EQUITY-39).
  - SPX flat 2022-2026 (EQUITY-40, pointer only).
  - Rosa 2022: disappears out of sample (abstract).
  - Aalto thesis: not cost-feasible (abstract).
  - Program: NQ T1 gross 1.25 ticks against a 4.08-tick cost (R1-14); E16-H1 gross about a quarter of its cost (R1-13).
- Not in the sample: micros, yield futures, mini grains and crypto futures. Crypto spot: OOS R2 1.09-1.61%, not
  profitable at a 25 bp fee (CRYPTO-17).
- Data: 1-minute bars at close-30 and spreads at the close; GEX or leveraged-ETF AUM to condition. About 252 trades a
  year per product.
- R1 overlap:
  - R1-14: H6 itself, NQ, 2020-06..2024-02.
  - R1-13: E16-H1 and H4, pooled over 27 roots.
  - CP1 ports in every K cluster (R1-03..R1-09).
  - R1-15: ML with r_ROD features.
  - R1-18: the reversal at 5 and 20 days.
  - R1-23: C2 GEX stopped; a stop, not a test.

### R2-F02 Energy inventory release drift or reversal
- Mechanism: digestion of the inventory surprise. Release times: WPSR Wednesday 10:30 ET, WNGSR Thursday 10:30 ET, API
  Tuesday 16:30 ET (that one falls after the session).
- Absorbed in under 5 minutes (strong):
  - NG within 50 ms (NATGAS-27). Longer windows are "similar" (NATGAS-25). The 5-7 minute response matches 100 minutes
    (NATGAS-26).
  - CL estimates at 5, 15 and 30 minutes are "very close" (CRUDE-14).
  - CL: no return predictability over 10:35-15:00 ET (CRUDE-51, null).
- Drift or reversal evidence:
  - Over-reaction on positive surprises, half reversed after 4 h (CRUDE-52, 2007-2014, gross).
  - USO adjustment "completed at the end of the trading day", in sample, absent 2014-2016 (CRUDE-20).
  - Effects last about 25 minutes, then revert (CRUDE-30, abstract).
  - NG pre-release, 85-90 minutes: Sharpe 0.84 using analyst forecasts (NATGAS-40).
  - NG event window after 2011: net -0.90%/yr (NATGAS-39, negative).
- Data: bars or trades around 10:30 ET; consensus forecasts. About 52 events a year per report.
- R1 overlap: R1-06 (K4: NG storage pre-release, API/EIA pre/post, overreaction fade on MCL and NG; ngpre failed
  Holm). R1-23: V39 closed commodity event drift as a standalone stage. R1-11 and R1-12: the NG h60 near miss.

### R2-F03 USDA report drift
- Mechanism: digestion of a large surprise (continuation), or overshoot and correction after small surprises. Releases
  come at 11:00 CT inside the day session since 2013 (GRAINS-22).
- Evidence for:
  - Not significant at 10 minutes, significant at 30; the soybean reaction keeps growing to the close (GRAINS-18,
    2010-2021, WP, full text).
  - Huang 2022 (corn, 2012-2019): 75% of the hour's move by 10 minutes and 90-100% by 35-45 minutes. Big events drift
    +0.65% after minute 10, but only conditional on the 60-minute sign, so the result is not tradable as stated
    (E.32 R4).
- Evidence against:
  - About 10 minutes, with no systematic under- or overreaction (GRAINS-19, abstract; GRAINS-21, full text).
  - Jumps within 2 minutes (GRAINS-23).
  - Volatility gone within minutes (GRAINS-20).
- NOPA: no intraday study at all. RFS news for ZL and the 2025-09-12 reversal are pointers.
- Overnight: Crop Progress (Monday 16:00 ET) and Export Sales (Thursday 07:30 CT) land outside the day session.
- Events: about 49 major USDA days and 39 NOPA days in 39 months (E.32 R4).
- R1 overlap: R1-08 (K6 WASDE pre/post on ZC ZS ZL ZM ZW); R1-21 (E.33 excluded release windows, ZM closed); R1-23
  (event drift closed as a direction; its R1 product list names crude, metals and natgas).

### R2-F04 US macro release drift
- Absorbed fast:
  - ZN: "majority of permanent price changes restricted to the minutes" or seconds (RATES-19); first minute in cash
    (RATES-20).
  - FX: "generally completed within a few minutes" (FX-22).
  - ES order flow within 1 s (EQUITY-19).
  - BTC: orthogonal to the news (CRYPTO-27).
- Slower pieces:
  - ES: "some evidence of continuing adjustment" at t+10 to t+30 minutes (EQUITY-17, 2008-2014).
  - Copper responds with a delay. Gold and silver peak about 30 minutes after the 09:15 releases, and the response
    dissipates within an hour (METALS-23, 2002-2008).
  - Pre-release drift needs the surprise sign (EQUITY-18, RATES-22).
- Gate risk: Topstep Tier 1 windows (CPI, NFP, PPI, FOMC) block the equity and metals minis (planner pointer;
  FirmRules owns this).
- R1 overlap: R1-01 (MES family E), R1-04 (K2 ISM pre-drift).

### R2-F05 FOMC post-statement drift
- For:
  - Cash Treasury yields fall persistently for about 3 hours after the statement; null before FOMC and around payrolls
    (RATES-23, 1997-2024).
  - SPY FOMC-day momentum 20.04%/yr against 6.24% (EQUITY-20).
  - Gold: the adjustment at 10 minutes is three times that at 5 minutes (METALS-25).
- Against: pre-FOMC equity drift gone after 2015 (EQUITY-21); none in Treasuries (RATES-25); BTC orthogonal; K5-fomc-01
  on MGC null (R1-07).
- Overnight: FX appreciation and partial reversal over 12-24 h (FX-25); post-FOMC drift in bond futures over days
  (RATES-26, abstract).
- Power: 8 events a year.
- R1 overlap: R1-04 (K2 fomcpost, Tier B), R1-07, R1-19.

### R2-F06 Pre-scheduled drift and supply pressure
- Pre-FOMC ZN futures, 19:00 ET on day -2 to 12:00 ET on day -1: +7.26 bp, t 2.82, 2004-2025. No post-2015 split. As an
  overnight hold this runs 18:00 CT Monday to 11:00 CT Tuesday (DF3-C5).
- Pre-refunding 10-year cash, the day before the Monday release: +12.62 bp, t 3.32. No futures, no post-2015 split.
- Auctions: pressure before and reversal after over 180-minute windows; own-tenor pressure halved in 2015-2024
  (RATES-24). Robeco chart for ZN (practitioner).
- NG pre-WNGSR (NATGAS-40). Kurov pre-release drift is not tradable ex ante.
- Power: V45 counts 3-15 events in a research window, power 0.11-0.22.
- R1 overlap: R1-04 (auction windows, ISM), R1-13 (H3 auction cycle), R1-19 (the V45 exceptions; open or closed is the
  lead's call), R1-06 (ngpre).

### R2-F07 Fixes and month-end rebalancing
- For:
  - CME futures post-London +0.64 bp/day (t 2.20), 1999-2019, gross (FX-38).
  - Month-end fix at 15 minutes, net of half spread: EUR/USD 3.965%/yr, AUD/USD 9.187%/yr; post-2010 OOS average 3.25%
    (FX-39, spot).
  - Melvin-Prins: 60 minutes before the month-end fix (FX-40).
  - Treasury end-of-month returns, close-to-close (RATES-44, overnight).
- Against: liquidity demanders lose after costs (FX-38). LBMA gold has no leakage after 2015 and is done within minutes
  (METALS-35). The gold PM-fix pattern holds in 2007-2011 only (METALS-28). The silver fix bias ended with the 2014
  auction (METALS-43).
- R1 overlap: R1-05 (London-fix rev/mom, ECB, Tokyo, month-end hedge; ldnrev 6E null at E.22), R1-07 (LBMA windows),
  R1-04 and R1-18 (month-end ZF/ZN/ZB), R1-13 (H2).

### R2-F08 Regional-session and overnight-to-day handoffs
- For: EUR/USD falls in its own local hours, net Sharpe 1.3 and 0.9 on EBS (1997-2007) (FX-37).
- Against:
  - AUD/USD net negative (FX-37).
  - European open (ES): Sharpe 1.1 gross, -0.5 after spreads; an overnight hold (EQUITY-50, -51).
  - COMEX gold day negative, overnight positive, 1985-2012 (abstract).
  - INE night return predicts a day reversal (abstract). USO first half-hour predicts the close.
  - DCE reaction to US overnight moves arbitraged after night trading (GRAINS-42). Corn settlement reversals declined
    after 2012 (GRAINS-17).
  - CBOT soybean meal overnight plus first half-hour: no prediction.
  - Grains 08:30 reopen: untested. CME crypto gap: pointer only, and gone since 24/7 trading began 2026-05-29.
- R1 overlap: R1-01 (clock windows, gaps), CP3 ports (R1-03..09), R1-13 (H4), R1-10 (K8 weekend BTC), R1-05 (Tokyo
  fix).

### R2-F09 Cross-market lead-lag and relative value
- Soy crush: cointegrated on 180 of 243 day sessions and 52 overnight sessions (2015, 1-minute data). No leader, no
  half-life, no trading test (GRAINS-15, -16, -38).
- Program record: ZM crush residual and ZS/ZL propagation are negative net (R1-21). The ZM 2017-05..2020-11 window is
  sealed (V51).
- Other relations:
  - Corn nearby/deferred cointegrated on about 70% of days (GRAINS-46).
  - NQ leads ES by 9-12 minutes and Russell by 8-11 at 60-minute extrema (preprint, no trading test; EQUITY-13).
  - Silver leads gold at 1 minute (thesis).
  - AUD and commodities: 5-minute Granger causality in sample, none daily (FX-19, -20).
  - BTC leads ETH only in volatile regimes (abstract).
- Mini or micro and full-size pairs, WTI-Brent, futures-cash: arbitrage-tight, seconds or milliseconds. Crack spreads:
  daily only.
- Open: the crush with ZS or ZL as the traded leg (untested by the program); Treasury curve spreads (no intraday study).
- R1 overlap: R1-21, R1-08 (crushgap ZS), R1-10 (flight to gold, oil/CAD), R1-13 (H2 NQ/ZN), R1-20 (ZM/ZS/ZL dates
  already read).

### R2-F10 Order-book state at 5 minutes and longer
- Forward order-imbalance predictability is insignificant by 5-30 minutes (CRS 2005, via E.32 M1). Deep order-flow
  forecasts last about two price changes (Kolm et al.).
- Drift-burst reversal on ZC: b -0.20, R2 41.5%, but the event time carries look-ahead.
- Lagged imbalance predicts some grains (GRAINS-41, abstract, horizon unknown). ZM S3 negative (R1-21).
- V56 item 2: "Order-book direction is not closed for other products."

### R2-F11 Own-price-path trend and reversal
- Reversion at 2-16 minutes and weak trend at 1 hour or more. OOS R2 0.55 bp and 0.020 bp, gross (Safari-Schmidhuber,
  2010-2023).
- T-note reversal declined (RATES-46). FX reversals before 2003 (FX-44). Chinese commodities do not cover costs.
- CME BTC ML accuracy about 54% over a 9-month sample, gross (CRYPTO-20).
- Noise-area momentum: dropped on post-publication evidence (V45 item 3). MNQ and NQ preprints negative (EQUITY-43,
  -44).
- R1 overlap is heavy: R1-01 families B, C, G and H; the CP2 and fade members in R1-03..09; R1-11 and R1-15 (ML);
  R1-21 S4.

### R2-F12 Expiry and option-hedging days
- ES 3rd-Friday reversal: -12.89 bp, t -2.40 (2003-2021), not significant in 2015-23 alone. ES only.
- Gamma imbalance drives end-of-day momentum or reversal, and the leveraged-ETF effect is larger (Barbon et al.,
  stocks, full text).
- Dealer gamma flips ES 60-minute momentum (EQUITY-39). Reversal around Deribit expiry (abstract).
- Data: option open interest for GEX.
- R1 overlap: R1-14 (T3 GEX), R1-23 (C2 stopped), R1-09 (K7-expiry not traded), R1-19.

## Searched, not found (from the F2 readers' records)
- A post-2015 study on a CME candidate code, out of sample and net of costs, at 5 minutes to the session: none, for
  any family.
- Intraday crack spreads, Treasury curve spreads, NG and CL calendar-spread reversion.
- Directional settlement-window effects for CL, NG, metals, FX and crypto.
- Intraday studies of NOPA, Export Sales or EPA RFS events.
- Copper and China data; OPEC.

## Gaps and limits
- Nothing new was fetched. The verified levels are those the F2, E.20, E.25 and E.32 files recorded. The Huang,
  Chordia-Roll-Subrahmanyam, Kolm and Christensen-Oomen-Renò numbers come from the E.32 brief's full-text reads.
- Event counts are calendar facts. Holiday shifts are not counted.
- The overlap notes are extraction. Whether a combination re-tests a closed line (Q3) is for the CombinationScorer and
  the lead. R1's ambiguities bear on F01 (V38 "on Topstep"), F06 (V45 exceptions), F12 (C2 stop) and NQ (V49 scope).
