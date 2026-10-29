# F2_fx: family reader facts for M6E, 6E, M6A, 6A (Stage E.32b, step F2)

Worker: FXReader-OpusHigh (Opus 5.5). Started 2026-10-28 23:03 PDT, finished 2026-10-28 23:17 PDT.
JSON twin: reports/stage_e32b_briefs/F2_fx.json (53 items, built by work/FX/FX_build.py from work/FX/FX_items.py;
each quote is checked word for word against the saved text with whitespace collapsed: 0 failures. Snippet and pointer items are not checked).
Pages: reports/stage_e32b_briefs/pages/FX/ (log.tsv). Reused pages: reports/stage_e28_briefs/pages/A1_fx/ and
reports/stage_e20_briefs/pages/6E/ (sha256 taken from their logs). WebSearch calls: 19 of 60. T6 full-text reads: 4 of 12.
No budget notice was received. This file states facts only and assigns no scores.

Leaders: 6E for M6E (EUR/USD), 6A for M6A (AUD/USD). All four are physically delivered (FX-27 to FX-30). The micros
are not financially settled off the full-size settlement price.

## T1 spread and touch (main-session median requested; none found)

| Code | What was found | Statistic, session, window | Item |
|---|---|---|---|
| 6E | 0.6 pip = 1.2 ticks | time-weighted AVERAGE over the whole trading day, June 2021 (CME FX Market Profile). Not a median, not main-session | FX-1 |
| 6E | TOB size about USD 3.5m (about 23 contracts at 1.20 USD/EUR, my arithmetic) | average for June 2021, whole day; up from USD 1.8m in Jan 2021 | FX-2, FX-53 (new vs E.28 null) |
| 6A | 0.5 pip = 1 tick | MEDIAN over the whole trading day, Dec 2020 (CME FX report 2021 Q1, via Wayback). The December average was 0.75 pip = 1.5 ticks; weekly averages 1.15, then 0.86, then 0.68 pip | FX-3, FX-52 (new vs E.28 null) |
| 6A | TOB size about USD 1.5m (15 to 20 contracts, my arithmetic) | average over 3 days after the tick halving (2020-11-23); before the change: sometimes over USD 6m | FX-4 |
| M6E, M6A | not found | the tick is 1 pip (twice the full-size tick), so the spread is at least 1 micro tick. Forum pointer: "5 tick spread late at night" on M6E, 2010 | FX-5, FX-6 (pointer) |

per_code.median_spread_ticks is null for all four. The whole-day figures are kept in their own fields, so they are
not relabelled as main-session medians.

## T2 crowding

- T2a (sources other than the CFTC). BIS 2018: an estimated 70% of ORDERS on EBS (the spot venue) are submitted by
  algorithms. This measures orders, not volume (FX-7). BIS 2011: HFT is about 24-30% of spot turnover (FX-8). The CFTC
  per-product futures shares are owned by the shared file F2_shared_cftc_automation.json (E.28 had 6E ATS at 82.0% for
  2016-18, the E-micro group at 70.9%, and G10 at 85.4%).
- T2b. FX Micros Market Maker Program for M6E and M6A, 2021-08-01 to 2025-08-31 (FX-9). No extension found after that
  date. 6E and 6A had only partial programs: the FX Futures Calendar Spreads MM Program covered spreads in AD and EC
  during 2021 (FX-10), and the EUR/USD BTIC MM Program ran 2023-02-06 to 2024-01-31 and covered BTIC only (FX-11). No
  program was found for OUTRIGHT 6E or 6A (FX-12). That means "not found", not "none exists".
- T2c. No numeric retail share was found. CME describes the E-micros as products for retail traders (FX-13).

## T3 structural relationships

- Mechanical pairs: M6E with 6E and M6A with 6A share an underlying and are both physically delivered (FX-14, FX-15).
  Calendar spreads use an implied spread book matched by Algorithm K (FX-16). Futures against OTC spot are tied by FX
  Link (median 0.1 pip, TOB about USD 90m, June 2021) and FX Spot+ (CME deck, 2026) (FX-17, FX-18). All of these are
  arbitrage-tight.
- Economic, cross-asset (AUD only): spot AUD/USD against gold, copper and oil, 2000-2009, using 5-minute and daily
  data. Granger causality runs both ways and is stronger at short horizons; the direction from commodity to currency
  dominates. This is an in-sample causality measure, not a trading test (FX-19, CIRANO working paper, full text). On
  daily futures data from 1992 to 2009: no Granger causality, only a contemporaneous link (FX-20, negative).
- No intraday cointegration or lead-lag study was found for EUR/USD against another market. The futures-spot lead-lag
  evidence is under T5.

## T4 scheduled events and absorption speed

- US releases (08:30 ET) and FOMC: the conditional mean adjusts "quickly, effectively amounting to jumps". Sample:
  ABDV, 1992-1998, 5-minute Reuters quotes, full text (FX-21). On EBS EUR/USD, 1999-2004: "generally completed within
  a few minutes", and the expected value a few minutes after a release equals the expected value an hour later
  (Chaboud et al., IFDP 823, full text, FX-22).
- RBA decisions (AUD): a sharp spike in the 10 minutes after the event and stable coefficients for the next 6 hours,
  so no drift. Sample 1993-2004, Kearns-Manners, full text via Wayback (FX-23).
- ECB communication between meetings: a null, with CARs within a few bp by +20 minutes (2008-2016, Fanta 2025). The
  meeting-day times given there are a 13:45 press release and a 14:30 press conference CET. Current times were not
  re-verified (FX-24).
- FOMC: on 12-hour windows the currency appreciates before and partly reverses 12 to 24 hours later (1999-2015,
  dissertation, gross, FX-25). The horizon is hours, not minutes after the release.
- Frequency: ECB 8 meetings a year, RBA 8 a year in 2025-26 (FX-26).
- No post-2010 study was found showing a mean drift of 5 minutes or more after a scheduled release for EUR/USD or
  AUD/USD.

## T5 settlement and price discovery

- Settlement: all four are physically delivered (rulebook chapters 261, 292, 255 and 291; FX-27 to FX-30).
- Information share for EUR/USD:
  - Spot dominated in 2006 (Rosenberg-Traub, full text, FX-31).
  - Spot (EBS) leads CME (Cabrera et al. 2009, abstract, FX-32; Chen-Gau 2010 JBF, abstract, FX-33). In Chen-Gau
    2010 the futures share rises around US releases.
  - Chen-Gau 2022 JFM (abstract) finds the reverse: futures dominate once both markets' order flows are included
    (FX-34).
  - 6E has about 66.5% against the E-mini euro future, 2010 (FX-35).
  - BIS 2018 summary: spot became dominant over futures in the 2000s (FX-36).
- No percentage share for futures against spot was found for any period after 2010, and no AUD study was found.

## T6 intraday directional evidence (5 minutes to the session)

| Item | Study | Venue / product | Horizon | Period | In/out of sample, costs | Finding | Level |
|---|---|---|---|---|---|---|---|
| FX-37 | Breedon-Ranaldo (JMCB 2013; QMUL WP 2012) | EBS spot; EUR/USD, AUD/USD and others | session (hours) | 1997-2007 | in sample; net of EBS bid/ask | a currency falls in its own local hours; EUR/USD strategy net positive (Sharpe 1.3 and 0.9); AUD/USD net negative (-0.51, -0.50) | full text |
| FX-38 | Krohn-Mueller-Whelan (JF 2024) | spot mid-quotes; CME futures dollar portfolio | windows of hours around the fixes | 1999-2019 (CME from 2006) | in sample, gross; liquidity demanders negative after costs | EUR post-London +2.73 bp/day; AUD pre-Tokyo -2.84, post-London +1.93; CME futures post-London +0.64 (t 2.20) | full text (E.20) |
| FX-39 | Evans (JBF 2018) | spot, 21 pairs | 1, 5, 15 min after the month-end fix | 2004-2013 | net of half spread; post-2010 out-of-sample average 3.25% | at 15 min, EUR/USD 3.965% and AUD/USD 9.187% per year | full text (E.20) |
| FX-40 | Melvin-Prins (JFM 2015) | spot, 10 currencies | 60 min before the month-end fix | 2004-2012 | in sample, gross | month-to-date equity return predicts the currency's move | full text (E.20) |
| FX-41 | Baltussen et al. (JFE 2021; shared source) | CME Euro FX and 7 other currency futures | last 30 min | to 2020 | out-of-sample R2 for Euro FX -0.07% | Euro FX null; currency class insignificant in 2000-2020 | reused from E.20 |
| FX-42 | Aalto thesis (2025) | 20 futures including currencies | last 30 min | 2008-2024 | net of costs | "not feasible after transactions costs, especially in bond and currency futures" | abstract |
| FX-43 | Elaut et al. (JFM 2018) | MICEX RUB-USD | first half hour predicts last half hour | 2005-2014 | in sample | intraday momentum | abstract |
| FX-44 | Rentzler et al. (JFM 2006) | 7 CME currency futures | intraday reversal | 1988-2003 | in sample | reversals in 5 of 7 | abstract (E.28) |
| FX-45 | Jiang (2018 WP) | currencies | US hours vs foreign hours | not verified | not known | European currencies gain in US hours | snippet [unverified] |
| FX-46 | Chen et al. (EFMA 2009) | 6E | weekly | 1999-2005 | net | excluded: weekly horizon | full text (E.28) |

Negatives: FX-41 (Euro FX null), FX-42 (not feasible after costs), the AUD/USD net-negative rows in FX-37, and the
Krohn liquidity-demander result in FX-38. No post-2010 study was found that shows intraday predictability out of sample
or net of costs on 6E, 6A, M6E or M6A themselves.

## T7 session structure and handoffs

- Globex trades Sunday to Friday, 17:00 to 16:00 CT, with a 60-minute break from 16:00 CT. The old pit (RTH) hours of
  07:20-14:00 CT serve as the FX day in Baltussen (FX-47).
- FX daily settlement window: 13:59:30-14:00:00 CT (CME client wiki, FX-48). No study of a settlement-window effect
  was found.
- Regional handoff: a currency falls during its own local trading hours, measured on EBS spot 1997-2007. Session hours
  in that study: US 08:00-16:00 NY, Europe 07:00-15:00, Australia 10:00-16:00 local (FX-49).
- Fix handoffs: Tokyo 9:55 JST, ECB 14:15 CET (14:00 CET from July 2016) and London WMR 16:00 show V-shaped USD moves
  (FX-50). The WMR window widened to 5 minutes on 2015-02-15 (FX-51).

## F1 changes against E.28

- 6A median_spread_ticks: was null, now 1 tick (a whole-day median for Dec 2020) (FX-52).
- 6E touch_queue_size: was null, now about USD 3.5m at the TOB in June 2021 (FX-53).
- No other changes were met.

## Searched, not found

The query lists are in F2_fx.json searched_not_found:
- T1: main-session medians and micro spreads.
- T2b: FX Micros MM after 2025-08 and outright 6E/6A programs.
- T4: a post-2010 drift of 5 minutes or more after a release.
- T6: post-2010 out-of-sample or net studies on these products.
- T5: an AUD information share and any post-2015 numeric share.
- T7: a settlement-window effect.

## Gaps

- No main-session median spread for any code. No spread or touch size for the micros. Touch-size contract counts are my
  arithmetic.
- Several studies were read at abstract level only (Chen-Gau 2010 and 2022, Cabrera et al., Malhotra-Corelli, Elaut et
  al., the Aalto thesis). Jiang 2018 is a snippet only.
- Current ECB release times were not re-verified. rba.gov.au answered 403 to curl, so the Wayback copy was used.
