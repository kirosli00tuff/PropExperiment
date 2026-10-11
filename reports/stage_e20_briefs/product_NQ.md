# Stage E.20 Part A: product reader NQ (vehicle MNQ)

Reader: ProductReader-NQ-OpusHigh. Written 2026-10-11, 10:32-10:55 PDT. Brief:
`reports/stage_e20_briefs/brief_partA_shared.md`. Shared notes written by this reader:
`shared/baltussen_notes.md` (all 17 roots) and `shared/rosa_2022_notes.md`.

NQ facts used below (root table): vehicle MNQ, tick $0.50 (0.25 index points), D8 round-trip wall
5.412 ticks = $2.71, day-session round-trip mean 4.119 ticks, group equity, O 08:30, C 15:00, F 15:08 CT,
backward window 2010-07-01..2019-05-05, search window 2019-05-06..2024-02-29.

Price levels for converting bp to ticks (public, Wikipedia "Nasdaq-100" annual-close table, saved
`pages/NQ/wiki_nasdaq100.html`, sha256 6ef889c1...e5084e): the mean of the year-end closes 2019-2023
(8,733.07; 12,888.28; 16,320.08; 10,939.76; 16,825.93) = **13,141.4** for the search window, and of
2010-2018 (2,217.86 ... 6,329.96) = **4,129.8** for the backward window. These are cash-index levels; the
futures basis is ignored. One bp at 13,141.4 = 1.314 points = 5.26 MNQ ticks; at 4,129.8 = 0.413 points =
1.65 ticks.

## 1. Evidence (published intraday evidence since 2015, NQ and the equity-index class)

Equity-class literature beyond Baltussen and Rosa (Gao et al. 2018, Adams et al. 2026, the dev.to retest,
other index-futures studies) belongs to the RTY reader: [shared, see
`reports/stage_e20_briefs/shared/equity_class_notes.md`]. Rows E7-E9 below cite shared files that exist on
disk now; the lead merges.

| Id | Effect | Rule | Hold | Gross per trade | Gross/net | Sample | Decay evidence | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum, NQ's own regression | r_LH = a + b r_ROD; r_ROD = P(c-30)/P(c,t-1) - 1, c = 16:00 ET cash close (15:00 CT) | last 30 min of the cash session | not printed for NQ. b x100 = 6.36 (NW t 7.97), R2 4.10%, R2_OOS 3.76% (Clark-West significant at 1%) | gross | NQ (regular contract, then the E-mini), 1-min, 1996-04-12..2020-05-01, 6,017 days | none per market; see E3 | Baltussen, Da, Lammers, Martens, JFE 142 (2021) 377-403, Table B1 Panel B (L3430), Table A1 (L3234) | primary |
| E2 | Same, equity 1/N portfolio trading strategy eta(r_ROD) | long LH if r_ROD > 0, short otherwise | 30 min | 6.86%/yr, SR 1.73, success 0.55; derived **2.72 bp per trade** (/252, factor assumed) = 3.58 pts = **14.3 MNQ ticks ($7.15)** at 13,141.4; 1.12 pts = 4.5 ticks ($2.25) at 4,129.8 | gross ("we do not consider transaction costs"; S&P net Sharpe positive at one tick, no number) | 17 equity index futures (US, EU, Asia), Dec 1974 (per future) to May 2020 | E3 | Same, Table 6 Panel A (L1736) | primary (per-trade figure derived) |
| E3 | Subsample stability | as E1, pooled equity | 30 min | b x100 5.96 (t 4.80), R2 3.41 in 1974-1999 vs 3.98 (t 6.65), R2 2.34 in 2000-2020 | gross | pooled equity futures | coefficient about one third smaller in the later half, still significant | Same, Table 5 (L1661, L1666) | primary |
| E4 | Gamma conditioning | E1's regression split by the sign of NGE_t-1 (S&P 500 option net gamma, OptionMetrics 1996-2017, SqueezeMetrics to May 2020) | 30 min | NGE_t-1 < 0: b 6.63 (t 4.78), R2 3.58; NGE_t-1 >= 0: b 0.82 (t 1.03), R2 0.05 | gross | **S&P 500 futures only**, Jan 1996-May 2020; 2,930 negative and 3,158 positive NGE days | none | Same, Table 7 (L2060-L2061), L1970-L1976 | primary |
| E5 | First-half-hour predictor and the agreement filter | eta(r_ONFH): sign of P(o+30)/P(c,t-1) - 1; eta(r_ONFH, r_ROD): trade only when both signs agree | 30 min | eta(r_ONFH): 4.21%/yr, SR 1.07, success 0.55, derived 1.67 bp (8.8 ticks at 13,141.4); agreement: 5.47%/yr, SR 1.60, success 0.61, per-trade not derivable (share of days traded not printed). NQ r_ONFH row: b 7.45 (t 5.33), R2 2.01, R2_OOS 1.83 | gross | as E2; NQ as E1 | r_ROD beats r_ONFH out of sample (paper's horse race, Table 3) | Same, Table 6 (L1734-L1735), Table B1 (L3430) | primary |
| E6 | Overnight return predicts the last half hour; threshold form | overnight return -> last half hour; "A strategy with thresholds delivers higher returns than a strategy that is always active" | 30 min | **none printed in the abstract**; threshold definition, value, lookback and sample unknown | unknown | [unverified] snippets name S&P 500, Nasdaq 100 and DJIA futures (Pi Trading) and Sep 1997-Dec 2020 | "The predictability disappears in the out-of-sample period" (abstract); "decline in predictability" post-2013 per Zarattini et al. [secondary-only] | Rosa, J. Futures Markets 42(12) (2022) 2218-2234, doi 10.1002/fut.22375; `shared/rosa_2022_notes.md` | abstract primary; rest unverified |
| E7 | Post-2020 retest, SPX (unreviewed blog) | regress last-30-min return on open-to-(close-30) return, SPX | 30 min | slope +0.006 (t +0.6) over 1,085 sessions 2022-04-14..2026-08-20; on short-gamma closes the slope adds +0.055 (t +3.1), 15% of sessions | gross | SPX index (not futures), 2022-2026 | "The unconditional effect is gone" | firmtape via dev.to, saved by the RTY reader `shared/devto_firmtape_spx_retest.txt` [shared, see `shared/equity_class_notes.md`] | secondary-only, unreviewed |
| E8 | Persistence 2008-2024, 20 futures (thesis) | ROD-type predictors -> last half hour | 30 min | no figures; "most of the predictability in the return of the last half an hour stems from the last ten-minute period"; "most intraday momentum and reversal trading strategies may not be feasible after transactions costs, especially in bond and currency futures" | unknown | 20 equity, bond, FX futures, 2008-01..2024-10 | patterns "still exist"; cost feasibility doubtful | Aalto master's thesis; abstract only, [shared, see `shared/aalto_thesis_notes.md`] | primary abstract, no numbers |
| E9 | Gamma and intraday momentum after 0DTE (2026 draft) | high market-maker hedging needs -> weaker momentum or reversal (planning brief) | - | not read here | - | - | - | Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov (2026 draft) [shared, see `shared/equity_class_notes.md`; RTY saved `shared/adams_etal_0dte_fontaine.pdf.txt`] | not verified by this reader |
| E10 | MNQ intraday OHLCV signals, falsification (preprint) | 14 signal families incl. a "Close fade (15:30 entry)" on VVG days; walk-forward | various | "Eleven families fail because gross return before friction is 0.07-1.50 points, below the 2.0-point friction floor"; close fade fails "N<30/fold"; no ROD -> LH test | net of 2.0 pts (8 ticks) | MNQ 5-min, 947 days, 2021-2025 | none for ROD | Mesfin, arXiv 2605.04004 (2026-05-05), `pages/NQ/arxiv_2605.04004.txt` lines 19-27, 339 | primary preprint, unreviewed, not a ROD test |

Out of scope and logged: Yu, Rentzler, Wolf, "NASDAQ-100 Index Futures: Intraday Momentum or Reversal?",
Journal of Investment Management 3(3), 2005 (pre-2015; page 404 on joim.com, not read). No NQ-specific
peer-reviewed intraday study published since 2015 other than Baltussen et al. (NQ is one of its markets)
and Rosa (Nasdaq 100 futures per an unverified snippet) was found in 7 searches.

**Reading of decay and costs (facts, no ruling).**
- Every sized number is gross and ends by May 2020 (Baltussen) or December 2020 (Rosa, unverified). The
  H6 verdict window (2020-06-01..2024-02-29, per `brief_h6_code.md`) lies wholly after Baltussen's NQ
  sample, so it is out of sample for the paper; the overlap window 2019-05-06..2020-05-29 is inside it
  except May 2020.
- Within-sample decline: the pooled equity coefficient falls by about a third from 1974-1999 to
  2000-2020 (E3). Rosa reports out-of-sample disappearance for the overnight predictor (E6). The only
  post-2020 test found (E7) is on SPX cash, unreviewed, and finds a flat unconditional slope with a
  significant short-gamma interaction. E8 says the pattern persists to 2024 but concentrates in the last
  ten minutes and is mostly not cost-feasible.
- Cost arithmetic: E2's derived 2.72 bp is 14.3 MNQ ticks at the search-window price level, 2.64x the
  D8 wall (5.412 ticks); at the backward-window level it is 4.5 ticks, 0.83x. The NQ-specific
  coefficient (6.36) is above the pooled equity one (4.18) and the US pool (5.99), but no NQ-only
  per-trade return is printed.

## 2. Feature availability

Basis: listing dates and calendar coverage only; no bar read. NQ listing: E-mini Nasdaq-100 (NQ) 1999-06-21
(`reports/stage_e0_catalog.md` C8, from the E.0 liquidity JSON) and in Baltussen Table A1 the NQ series runs
1996-04-12..2020-05-01 (regular contract before the mini); MNQ listed 2019-05-06 (E.0 C8, CME press release
read in E.0). E.16 windows: NQ priced from 2010-07 (`reports/stage_e16_windows.json`, products.NQ). Equity
group calendars: 2019-05..2026-06 `data/calendars/equity.py` and the member tables (EQUITY_FULL_SESSIONS
2019-05-01..2026-06-18); 2010-06-01..2019-05-31 `data/calendars/hist2010/equity.json` (E.14, products incl.
NQ and MNQ, 2,325 trade dates, 0 unsourced, evidence "cme"). Equity settlement 15:15 CT until 2020-10-23,
15:00 from 2020-10-26 (`reports/stage_e16_rulings.md` R-S6); the D6 close C = 15:00 CT is the cash close
in both windows.

| Feature | Legs | Calendars / literals | 2010-2019 (NQ backward) | 2019-2024 | Basis / dates |
|---|---|---|---|---|---|
| cp1_ret, cp2_range, cp2_brk, cp3_clv (pooled ports, on MNQ rows) | NQ (own path) | equity group calendar | yes | yes | NQ listed 1999; hist2010/equity.json 2010-06-01..2019-05-31; equity.py 2019-05-01..2026-06-19 |
| k1_vwap_dist | NQ | EQUITY_FULL_SESSIONS | yes (via hist2010/equity.json; the member's own table starts 2019-05-01) | yes | as above |
| k1_vxn_regime, k1_vxn_band | NQ | VXN_CLOSE literal (`strategy/members/k1/_vxn.py`, VXN_RANGE 2019-04-30..2026-06-19) | **no** (as built: no VXN table before 2019-04-30; the Cboe source file under data/vendor was not opened) | yes | literal range |
| k8_wkndbtc_move (on MNQ rows) | MBT (not one of the 17 roots) | WKNDBTC_DATES 2019-05-01..2026-06-18 | **no** (MBT listed 2021-05-03) | partial (from 2021-05-03) | `reports/stage_e0_catalog_K8.md` line 185 |
| k9_anncday (MNQ, M2K, MYM rows) | none (calendar flag) | EC-K9 (`reports/stage_e12_ec_k9_2019_2024.json`, window 2019-05-01..2024-02-29) | **no** file found for 2010-2019 | yes | [shared, see `shared/macro_calendars.md` (RTY)] |
| g01_ret30, g02_ret60, g03_ret120, g04_ret_day, g06_rv60, g07_range, g10_logvol30 | NQ | equity calendar (trade date) | yes | yes | as cp rows |
| g05_gap, g08_prev_ret, g09_vol_state | NQ | equity calendar (prior C_X, early halts) | yes (g09 needs 120 dates of warm-up from the first priced month, 2010-07) | yes | as cp rows |
| g11_t_index, g12_dow, g16_month_end | none | equity calendar | yes | yes | hist2010/equity.json; equity.py |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | none | release calendar, MNQ list = FOMC, NFP, CPI, ISM_SERVICES (`reports/stage_e2b_release_calendar.json`, 2019-05-01..2026-06-21) | **partial**: `reports/stage_e14_cal_releases.json` (2010-06-01..2019-05-31) holds FOMC (72), NGS, WPSR only; no NFP, CPI or ISM Services rows | yes | [shared, see `shared/macro_calendars.md` (RTY)] |
| g17_nq (NQ as G17 lead leg, read on every other product's rows; not applicable on NQ's own rows) | NQ | equity calendar | yes | yes | NQ listed 1999-06-21; hist2010 and equity.py cover both windows |
| g17_zn, g17_6e, g17_cl, g17_gc, g17_zc (read on NQ rows) | ZN, 6E, CL, GC, ZC | their group calendars | per each lead's reader | per each lead's reader | [shared: product_ZN, product_6E, product_CL, product_GC, product_ZC] |
| g17_mbt (read on NQ rows) | MBT (not one of the 17) | crypto calendar | no (listed 2021-05-03) | partial | E.0 K8 catalog |
| g17_mes (read on NQ rows) | MES (not one of the 17) | equity calendar | no (MES listed 2019-05-06) | yes from 2019-05-06 | `reports/stage_e12_gate0_list.json` uncovered_signals lists g17_mes |
| r_ROD(t), abs-r_ROD over its 60-date median (E.20 additions, prompt) | NQ | equity calendar (C = 15:00 CT, prior trade date) | yes (60-date warm-up) | yes | as cp rows |

Notes: (1) In 2010-2019 MNQ did not exist; the NQ path is the full-size contract (D2 lets the full-size
bars stand for the micro). (2) The 2019-2024 calendars of the member modules start 2019-05-01; whether
v2 code reads hist2010 for 2010-2019 is an implementation fact for the lead, not a coverage gap: the
calendar exists. (3) "undetermined": none.

## 3. Proposed features

**None.** Reasons:
- Everything Baltussen et al. size for NQ is a function of r_ROD(t) = P(t)/P(prior C) - 1 at some t, which
  the prompt already adds. At t1 = 09:00 CT = O + 30, r_ROD(t1) is exactly the paper's r_ONFH (E5), so the
  first-half-hour predictor is also already in; at t4 = 14:08 CT r_ROD(t4) is the closest clock point to
  the paper's c - 30 = 14:30.
- The gamma condition (E4) is not computable from bars of the 17 roots or a calendar known in advance; it
  is H6's T3, not a feature under item 3's rule.
- Rosa's threshold (E6) acts on the overnight return, whose raw form is already G5, and its threshold rule
  and size are unverified; the magnitude variant |r_ROD| over its 60-date median is already added.
- The agreement filter eta(r_ONFH, r_ROD) (E5) has no derivable per-trade size (the share of days traded is
  not printed), and it is a product of two already-present values (r_ROD(t1), r_ROD(t)).
- The second-to-last half-hour return (NQ b_SLH 11.54, t 3.26, Table B1) ends at 14:30, which no decision
  time reaches; it has no published per-trade size.

## 4. NQ only: H6 details and the GEX ruling

### 4a. H6 as published (Baltussen et al. 2021; Rosa 2022)

- r_ROD's two prices (L589-L596): P_c-30,t, the price 30 minutes before today's close, and P_c,t-1, the
  previous day's close. Close c for equity futures is the underlying's cash close: "we select the
  observations of the S&P E-Mini between 09:30 and 16:00, as these are the trading hours of the S&P 500"
  (L541-L546). NQ's hours in Table 1 (L895) and Table A1 (L3234): **09:30-16:00** (ET), i.e., 08:30-15:00 CT;
  c - 30 = 15:30 ET = 14:30 CT; the last half-hour window is 15:30-16:00 ET = 14:30-15:00 CT. Prices are
  from one-minute intervals (open and close of each minute, L522-L523).
- Outside-hours data removed; the previous close is "the price at our closing time on the previous day"
  (L625-L632). Days with an early close are removed, as are days under 100 contracts (L527-L534). Roll on
  the volume crossover (L525-L527).
- NQ's own row (Table B1 Panel B, L3430): b_ROD x100 = 6.36 (Newey-West t 7.97), R2 4.10%, R2_OOS 3.76%
  (Clark-West significant at 1%); sample 1996-04-12..2020-05-01, 6,017 observations (Table A1, L3234). For
  r_ONFH: 7.45 (t 5.33), R2 2.01, R2_OOS 1.83.
- Equity portfolio trading strategy (Table 6 Panel A, L1736), 1/N over the 17 equity index futures:
  eta(r_ROD) 6.86%/yr, std 3.96%, Sharpe 1.73, success rate 0.55; gross; derived 2.72 bp per trade at an
  assumed 252 days.
- Negative gamma (Table 7, L2060-L2061): for **S&P 500 futures**, conditioned on NGE_t-1 (the previous
  day's S&P 500 option net gamma exposure, normalised by the index's market value, eq. 15): NGE_t-1 < 0:
  b 6.63 (t 4.78), R2 3.58; NGE_t-1 >= 0: b 0.82 (t 1.03), R2 0.05. No NQ gamma row exists. 2018-2020 NGE
  came from SqueezeMetrics, checked against OptionMetrics 2002-2017 with "virtually identical results"
  (footnote 7, L1998).
- Post-2020 decay: the paper has none (sample ends 2020-05-01). Evidence after it: E7 (SPX 2022-2026,
  unreviewed: unconditional slope t 0.6; short-gamma interaction t 3.1), E8 (2008-2024, no numbers, last ten
  minutes, cost-infeasible mostly), E9 (Adams et al., RTY's file). Within the paper, E3's decline.
- Rosa's threshold form, as published: the abstract only. Predictor = the overnight return; target = the
  last half hour; "A strategy with thresholds delivers higher returns than a strategy that is always
  active"; predictability "disappears in the out-of-sample period". **Threshold variable, value, lookback
  and sample: [unverified]** (the full text is behind Wiley, whose terms forbid automated access; see
  `shared/rosa_2022_notes.md`). Snippet-only claim: active "only when the absolute value of the overnight
  return is larger than a given threshold".

### 4b. Differences between the paper's rule and E.20's F5 rule

| Item | Paper (Baltussen et al.) | E.20 F5 | Difference |
|---|---|---|---|
| Close C | 16:00 ET cash close (15:00 CT), both before and after 2020-10-26 | C = 15:00 CT | none. Note: NQ's futures settlement was 15:15 CT until 2020-10-23 (R-S6); neither rule uses it |
| Prior close | price at 16:00 ET on the previous retained day | P(prior C), the bar ending at 15:00 CT on the previous trade date | same instant; after an early-close day the paper has dropped that day (which prior close it then uses is not stated) while F5 uses the early close as C |
| Signal price | P_c-30 (price at 15:30 ET) | bar ending at C - 30 (closing 14:30 CT) | same |
| Entry price | P_c-30 itself (no execution lag, no spread) | next bar's open (14:30 CT bar), market order | one-tick-scale timing and spread cost in F5 only |
| Exit | P_c, the 16:00 ET (15:00 CT) price | first present bar at or after C - 2 min (14:58 CT), filling at the next open (about 14:59 CT) | **F5 drops the final one to two minutes** of the paper's window; E8 says most LH predictability sits in the last ten minutes, so this cut lands inside the strongest part |
| Hold | 30 minutes | about 29 minutes | as above |
| Early-close days | removed | traded with C = early close, entry early close - 30, exit at the engine flatten F = early close - 15 min (`brief_h6_code.md` lines 18, 82-83) | F5 trades days the paper excludes, with a 15-minute hold |
| Low-volume days | removed below 100 contracts | not a rule (NQ volume far above) | immaterial for NQ |
| Roll | volume crossover of the next contract | the program's continuous path; roll-blackout dates refused by the engine | different roll dates; F5 drops blackout dates |
| Instrument | NQ (regular contract before the mini) | NQ bars (prereg store), MNQ costs | sample: paper 1996-2020; F5 2019-05..2024-02 (verdict 2020-06..2024-02) |
| T1 (unconditional) | eta(r_ROD), equity portfolio and NQ regression | sign of r_ROD | same rule on one market |
| T2 (magnitude) | **no threshold in Baltussen**; Rosa thresholds the overnight return with an unpublished-here rule | abs r_ROD above the median of the previous 60 eligible dates (strict >) | T2 is the planning brief's variant ("trade only when abs r_ROD is above its trailing median"), not a published rule; neither the 60-date lookback nor the median comes from either paper |
| T3 (gamma) | S&P 500 NGE_t-1 < 0 (OptionMetrics, SqueezeMetrics from 2018), tested on **S&P 500 futures** | SqueezeMetrics GEX row dated the previous equity trade date, strictly negative, applied to **NQ** | market extrapolated from ES to NQ; GEX is SqueezeMetrics' dollar construction, the paper's NGE divides by market value (the sign, which is what both tests use, is unaffected by that scaling); zero GEX falls in the non-negative bin in both |
| Costs | none | D8 MNQ round trip, 1.5x cost multiple (brief_h6_code constants) | paper gross only |

### 4c. GEX ruling: **cleared** for one registered test (T3), using E.14's existing copy

**Terms read.** https://squeezemetrics.com/monitor/terms, fetched 2026-10-11T17:34:43Z, raw HTML saved
`reports/stage_e20_briefs/pages/NQ/sm_terms.html`, **sha256
695c1bbd930b8930777190e1fc966b26f35fa12dcb798ed99977c0cd132c169d** (text extract `sm_terms.txt`, sha256
7a1ace8a6bff2458be6a2bff3fd1a871676c42b1589fc09215e992acb1809b89). This is byte-identical to E.14's copy
of 2026-10-05T07:38:50Z (`reports/stage_e14_briefs/pages/gex/terms.html`, same sha256): **the terms have not
changed since E.14's reading.** robots.txt: https://squeezemetrics.com/robots.txt returns HTTP 404 (nginx
error page, sha256 d465172175d35d493fb1633e237700022bd849fa123164790b168b8318acb090, identical to E.14's), so
there are no robots directives. No date or version is printed on the terms page.

Verbatim clauses that bear on the use (from `sm_terms.txt`):
- "You may not access or use the Platform for any purpose other than those for which we make the Platform
  available."
- "As a user of the Platform, you agree not to: ... systematically retrieve data or other content from the
  Platform to create or compile, directly or indirectly, a collection, compilation, database, or directory
  without written permission from us;"
- "... use the Platform as part of any effort to compete with us;"
- "Using the Platform does not give you ownership or license of any intellectual property rights in the
  Platform or in any content, information or data accessed on or through the Platform, including, without
  limitation, any content, information or data obtained from a third-party website."
- "It is your responsibility to comply with any copyright or other intellectual property laws that govern
  the content, information or data accessed on or through the Platform."

How the file is offered: the free DIX page (https://squeezemetrics.com/monitor/dix, fetched
2026-10-11T17:34:52Z, sha256 f8fc33b0...701526, identical to E.14's) shows a download icon
(`<span id ="fileRequest" ...><i class="fa fa-download"></i></span>`), and its script
(`/monitor/static/js/dix.js`, fetched 2026-10-11T17:35:19Z, sha256 145e00f7...de9e) binds it to
`window.location = '/monitor/static/DIX.csv';`. The page describes GEX as "a dollar-denominated measure of
option market-makers' hedging obligations."

**Ruling: cleared.** Reasoning:
1. The only clause that could forbid the use is the ban on systematically retrieving data "to create or
   compile ... a collection, compilation, database, or directory". Downloading once the single file the
   free page offers through its own download button, to compute one registered test's mask, is neither
   systematic retrieval nor the compilation of a collection. Reusing the copy already on disk retrieves
   nothing at all.
2. The use is one the platform makes available (the page offers the file to any visitor), it does not
   compete with SqueezeMetrics, and nothing is redistributed: the terms grant no licence, so the CSV and
   any of its values stay out of git (E.14's `DO_NOT_COMMIT.txt` already covers `DIX.csv`) and out of any
   published report beyond counts and the test result.
3. Residual risk, stated: the terms are written for subscribers and say nothing specific about the free
   CSV; "written permission" would remove all doubt. Nothing in them forbids a single download for private
   research, and robots.txt is absent.

**Copy to use: E.14's (`reports/stage_e14_briefs/gex/DIX.csv`, fetched 2026-10-05T07:43:01Z, sha256
51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62, 3,880 rows, header `date,price,dix,gex`,
first date 2011-05-02, last 2026-10-02 per `fetch_record.txt`; values not read).** It is the better reading
of the terms: it needs no new retrieval, which keeps the use as far as possible from "systematically
retrieve"; it covers the whole search window and the H6 verdict window (2020-06-01..2024-02-29); E.14 found
the window's rows unchanged across seven Wayback captures since 2020-11-29 by row hashes (E.14_RETURN.md item
5), so a fresh copy would add a retrieval and no information for the window. A fresh download would be
justified only for rows after 2026-10-02, which no E.20 test needs. Coverage caveat: the CSV starts
2011-05-02, so it does not cover the backward window's first ten months (2010-07-01..2011-05-01).

## 5. Fetch log, terms read, budget notices

Full log: `reports/stage_e20_briefs/pages/NQ/fetch_log.txt` (URL, UTC, tool, path, sha256, status) and
`shared/rosa_fetch_log.txt`. Summary:

| URL | UTC | Saved | sha256 (first 16) | Status |
|---|---|---|---|---|
| https://squeezemetrics.com/monitor/terms | 2026-10-11T17:34:43Z | pages/NQ/sm_terms.html | 695c1bbd930b8930 | ok (200) |
| https://squeezemetrics.com/robots.txt | 2026-10-11T17:34:47Z | pages/NQ/sm_robots.html | d465172175d35d49 | 404 (no robots file) |
| https://squeezemetrics.com/monitor/dix | 2026-10-11T17:34:52Z | pages/NQ/sm_dix.html | f8fc33b0d6b88dc8 | ok |
| https://squeezemetrics.com/monitor/docs | 2026-10-11T17:34:56Z | pages/NQ/sm_docs.html | e4fe792af74afc1f | ok |
| https://squeezemetrics.com/monitor/static/js/dix.js | 2026-10-11T17:35:19Z | pages/NQ/sm_dix.js | 145e00f742bdc4bf | ok |
| https://ideas.repec.org/a/wly/jfutmk/v42y2022i12p2218-2234.html | 2026-10-11T17:36:09Z | shared/rosa_ideas.html | d4bf996acfc622a6 | ok |
| https://onlinelibrary.wiley.com/robots.txt | 2026-10-11T17:36:38Z | pages/NQ/wiley_robots.txt | 9bb321ba7d7be3a7 | ok |
| https://onlinelibrary.wiley.com/terms-and-conditions (curl; scrapling get; scrapling fetch) | 17:36:45Z; 17:37:00Z; 17:37:06Z | wiley_terms.html; wiley_terms_sg.md; wiley_terms_scrapling_fetch.md | e512cf1c; 87299e07; 2a5622a9136aac4b | 403; Cloudflare; ok (terms read) |
| https://onlinelibrary.wiley.com/doi/full/10.1002/fut.22375 | 2026-10-11T17:36:50Z | pages/NQ/rosa_wiley_full.html | 7f06b14f9cd76134 | blocked (403), then terms-forbid |
| https://law-journals-books.vlex.com/robots.txt; https://vlex.com/terms | 17:37:35Z; 17:38:12Z | vlex_robots.html; vlex_terms.html | 6a0919b8; d5d90f41a2208df9 | ok; terms-forbid |
| https://api.openalex.org/works/doi:10.1002/fut.22375 | 2026-10-11T17:38:22Z | pages/NQ/rosa_openalex.json | 8a709d6fddc57d0e | ok |
| https://arxiv.org/robots.txt; /abs/2605.04004; /pdf/2605.04004 | 17:39:17Z; 17:39:20Z; 17:39:40Z | arxiv_robots.txt; arxiv_2605.04004_abs.html; arxiv_2605.04004.pdf | eda2bc85; b3d8d7c8; d0bd26e424a0c81b | ok |
| https://www.joim.com/robots.txt; joim.com NQ article pages | 17:39:29Z; 17:39:23Z, 17:39:54Z | joim_robots.txt; joim_nq_dl.html | 1b61b647; 0b3c00b3 | ok; 404 |
| https://fred.stlouisfed.org/robots.txt | 17:40:32Z, 17:41Z | none | - | blocked (HTTP/2 error, then hung); FRED not used |
| https://en.wikipedia.org/wiki/Nasdaq-100 | 2026-10-11T17:44:15Z | pages/NQ/wiki_nasdaq100.html | 6ef889c1b0c677c9 | ok |
| https://info.arxiv.org/help/robots.html; en.wikipedia.org, ideas.repec.org, api.openalex.org robots.txt | 17:50:07Z-17:50:14Z | arxiv_robot_policy.html; wiki_robots.txt; ideas_robots.txt; openalex_api_robots.txt | 2b918d81; 48b98d80; 4620fbdb; 16ceb5ee | ok |
| https://colab.ws/articles/10.1002/fut.22375 (WebFetch, not saved) | about 17:38Z | none | - | abstract only; not used as evidence |

Terms read:

| Site | URL | UTC | Ruling |
|---|---|---|---|
| squeezemetrics.com | /monitor/terms; /robots.txt (404) | 17:34:43Z | single download or reuse allowed; no systematic retrieval; no redistribution (section 4c) |
| onlinelibrary.wiley.com | /terms-and-conditions (line 86); robots.txt | 17:37:06Z | automated access forbidden: Rosa full text not fetched |
| vlex.com | /terms, clause (e); robots.txt | 17:38:12Z | automated access forbidden: not fetched |
| arxiv.org | robots.txt; info.arxiv.org/help/robots.html | 17:39:17Z (robots); policy page 17:50:07Z | single-paper download within robots.txt allowed. Deviation: the policy page was read after the PDF fetch (robots.txt before it) |
| en.wikipedia.org | robots.txt (User-agent * allows /wiki/) | 17:50:09Z | allowed. Deviation: read after the page fetch |
| ideas.repec.org | robots.txt (disallows /cgi-bin/ only) | 17:50:11Z | allowed. Deviation: read after the record fetch |
| api.openalex.org | robots.txt ("Allow: /") | 17:50:14Z | allowed. Deviation: read after the API call |
| joim.com | robots.txt (WooCommerce paths only) | 17:39:29Z | allowed; target pages 404 |

Budget notices: none. WebSearch calls used: 7 of about 90. Firecrawl not used. No cmegroup.com fetch.

## 6. Unfinished and unverified items

- Rosa (2022) full text not retrieved (Wiley and vLex terms forbid automated access; OpenAlex: closed,
  no repository copy): its threshold variable, value, lookback, sample and every figure are [unverified].
  A licensed copy is needed to state "Rosa's threshold form as published".
- The 252-day annualisation behind every derived per-trade bp figure is an assumption; the paper does not
  print the factor.
- No NQ-only trading-strategy return is printed in Baltussen et al.; NQ per-trade gross is the equity
  portfolio's derived figure, not NQ's.
- The Table 1 time zone for Chicago products (rates, FX, grains, livestock) is ambiguous between CT and ET
  (flagged in `shared/baltussen_notes.md`); NQ's equity hours are unaffected.
- E9 (Adams et al. 2026) not read by this reader; RTY owns it.
- The NQ listing date 1999-06-21 rests on the E.0 liquidity record (CME source, not re-read here); the
  Baltussen Table A1 series confirms NQ data throughout 2010-2019.
- Terms-before-fetch deviations for arXiv, Wikipedia, IDEAS and OpenAlex (robots or policy read minutes
  after the fetch; all permit the access made).
