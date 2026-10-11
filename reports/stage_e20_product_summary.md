# Stage E.20 Part A: product summary (lead consolidation, 2026-10-11)

Sources: reports/stage_e20_briefs/product_<ROOT>.md and .json (17 ProductReader-<ROOT>-OpusHigh, opus high,
spawned together 10:33 PDT, all returned by about 10:58), shared notes under reports/stage_e20_briefs/shared/.
Evidence rows are the readers'; every number entering a decision below was read in the reader's file by the lead.
Feature availability matrix: reports/stage_e20_briefs/feature_matrix.py (y yes, n no, p partial, u undetermined,
first letter 2010-2019, second 2019-2024, '.' not applicable on that root's rows).

## 1. Lead rulings

### 1.1 GEX (T3), decided before any NQ bar was read

Cleared (ProductReader-NQ, product_NQ.md 4c): SqueezeMetrics' terms, fetched 2026-10-11T17:34:43Z, sha256
695c1bbd930b8930777190e1fc966b26f35fa12dcb798ed99977c0cd132c169d, byte-identical to E.14's reading; robots.txt
404; the free page offers the CSV through its own download button; one offered file used for one registered test
is not "systematic retrieval" to compile a collection. Copy: E.14's reports/stage_e14_briefs/gex/DIX.csv (sha256
51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62); no new download. T3 is registered (m = 3, N 480 -> 483).

### 1.2 Evidence, in one paragraph

Across 17 roots, 157 evidence rows. The only published effect whose gross per trade clears 1.5 x a root's D8
round trip on its own window is H6's equity figure (Baltussen et al. equity portfolio, about 2.7 bp per trade,
2.64 x the MNQ wall at search-window prices, 0.83 x at 2010-2018 prices; NQ's own row b 6.36, t 7.97, R2_OOS
3.76%, 1996-2020-05). Baltussen's per-market rows are null or small on CL, ZC, ZS, ZL, HE, LE (ROD) and 6E; FV,
UB and NG show in-sample slopes whose per-trade size is under the cost or whose window no decision time reaches.
The Treasury auction cycle (NY Fed SR 1188, cash bonds) is the largest rates effect (1.2-1.6 x on the clock at
full-sample strength, under 1.0 x at 2015-2024 strength) and is already in the library (k2_auction_*). The NG
storage-day short decayed after 2011 (0.70 x). FX fix effects decayed after 2014. Post-2020 evidence on intraday
momentum points to decay (unreviewed SPX retest; Adams et al. 2026 draft; Rosa 2022's out-of-sample loss). No
reader found a sized post-2015 intraday rule for TN, ZL, HE or LE. Blocked or paywalled sources are listed as
gaps in each reader file, never as absence.

### 1.3 The F6 feature cut (lead), from the 67-signal library

Rule: a feature enters only if every leg it reads is one of the 17 roots and every calendar or table it needs
exists causally over both windows (a table a frozen rule derives from a calendar that exists over both windows,
such as a "full sessions" list, counts as existing; the B1 dry check must show it computes); no feature may be
not applicable by design in the backward window. Partial availability caused by a root's window start, the
warm-up, or a session structure whose bars do not exist (rows then excluded for data reasons) does not drop a
feature.

KEPT (35): cp1_ret, cp2_range, cp2_brk, cp3_clv; k1_vwap_dist; k2_auction_mto, k2_auction_msince, k2_fomc_mto,
k2_monthend_msince; k4_eiafade_move, k4_ngpre_mto, k4_ngpre_msince, k4_ovr_ret, k4_ovr_pct; k5_ovr_ret,
k5_ovr_pct; g01_ret30, g02_ret60, g03_ret120, g04_ret_day, g05_gap, g06_rv60, g07_range, g08_prev_ret,
g09_vol_state, g10_logvol30, g11_t_index, g12_dow; g16_month_end; g17_nq, g17_zn, g17_6e, g17_cl, g17_gc,
g17_zc. Plus the two prompt features (rod_ret, rod_absratio): 37 features.

DROPPED (32), with reasons:
| Feature(s) | Reason |
|---|---|
| g17_mbt, k7_montrend_ret, k7_rev2h_ret, k7_expiry_mto, k7_expiry_msince, k8_wkndbtc_move | leg or rows MBT, not one of the 17 roots (MBT listed 2021) |
| g17_mes, k8_flight_ret, k8_flight_tail | leg MES, not one of the 17 roots (listed 2019-05-06); MES not loaded |
| k6_crushgap_gap | leg ZM, not one of the 17 roots |
| k8_oilcad_ret, k8_oilcad_z | applies only on 6C rows; no row in the universe in either window |
| k3_mehedge_req, k3_tkypost_msince, k3_tkypre_msince | apply only on 6J (or 6J/6S) rows; no row in the universe |
| k3_ldnmom_trend, k3_ldnrev_move, k3_ecbfix_mto, k3_ecbfix_msince | their FX fix and session tables start 2019; no 2010-2019 table (6E reader) |
| k1_vxn_regime, k1_vxn_band | the VXN literal table does not cover 2010-2019 (NQ reader) |
| k2_predrift_move | no ISM Services release calendar for 2010-2019 (ZN, ZB, TN readers) |
| k4_apipre_ret | its API dropped-weeks table is undetermined for 2010-2019 (no 2010-2019 API calendar; CL reader) |
| k4_eiamom_r3 | needs the NYSE-not-full-session table, which has no 2010-2019 file and is not derivable from the CME calendars (CL reader) |
| k5_pmfix_move, k5_preauc_msince | no gold fix calendar for 2010-2019 on disk (GC reader) |
| k6_limitcont_dir | no price-limit table before 2019-05-01 (HE, LE readers) |
| k6_wasdepre_drift | no 2010-2019 WASDE calendar (ZC, ZS readers) |
| k9_anncday | its EC-K9 calendar (FOMC, NFP, GDP, ISM, CPI/PPI) exists only for FOMC in 2010-2019 (RTY reader, shared/macro_calendars.md) |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | the 2010-2019 release calendars hold FOMC (and NG storage, WPSR) but not NFP, CPI, PPI, GDP, ISM, WASDE, Crop Production or API; one pooled column cannot be made product-specific without changing a frozen feature (RTY, GC, ZC, LE and other readers) |

Kept with recorded partial row loss in the backward window: cp1_ret on rates before 2011-10-03 (Globex opened
17:30 CT, no 17:00 first bar); cp1/cp2/cp3 and the O_X-based generic features on grains before 2012-05-21 (no
08:30 bar) and cp3's daily bar on grains 2012-05-21..2013-04-05 (session to 14:00; D6's [O, C) bars exist);
livestock rows by session era (LE from 2014-12-15; 08:00 open, Monday 09:05, to 2016-02-28); k2_fomc_mto, whose
frozen 13:00 CT statement filter matches FOMC statements only from 2013-03-20 (earlier statements at 12:15 or
13:15 CT are not events for it; the calendar exists); k2_auction_* with the frozen original-term tenor rule
(ZT has no own-tenor auction in nine 2015-2019 months; ZF 11 mislabels backward, 2 forward); k4_eiafade_move
(one 2010-2019 WPSR time, 2012-11-01, unverified: that date is excluded in E20-B1); k1_vwap_dist and k5_ovr_*
(their full-session tables derive from the 2010-2019 group calendars). 6E's minimum tick was $0.0001 until
2016-01-08, so 1.0 x D8 understates 6E's 2010-2015 costs (E20-B1 reports this beside its result).

Not re-admitted: K5-fomc-01, K6-wasdepost-01 and k2_fomc_msince's reach become timely at t4, but they are not
in the frozen library's code, F6 allows no added feature beyond its list, and no reader proposed them with a
published per-trade size.

### 1.4 Part A proposals (acceptance rule in the plan, section 5.3)

| Root | Proposal | Reader's ratio to D8 | Ruling |
|---|---|---|---|
| RTY | fomc_r1 (first-half-hour return on FOMC days, at t4, h60/hF) | 2.51 | REJECTED (c): the published 7.95 bp per trade (Gao et al., Table 8) is for SPY's 15:30-16:00 ET hold in 1993-2013; no published size exists for the hold the feature would serve (t4 14:08 to 15:08 CT on Russell), so its expected gross under V31 is not established; it is also a conditional of cp1_ret, already in the library (d) |
| ZS | zs_wasde_post_t4 | 2.31 (upper bound, news sign assumed known) | REJECTED (b, c): no 2010-2019 WASDE calendar; the size is an upper bound, not an expected gross |
| 6E | p6e_mehedge_nq | 1.14 | REJECTED (c) |
| 6E | p6e_post_ldnfix | 0.66 | REJECTED (c), and its fix tables start 2019 (b) |
| ZT | zt_cpnauc_mto / msince | 0.75 | REJECTED (c) |
| ZF | zf_auc10y_mto / msince | 0.76 (1.53 full sample, before decay) | REJECTED (c) at post-2014 strength |
| ZB | k2_auc10_mto_zb | 0.79 | REJECTED (c) |

Accepted: none. Part C's added features are the two r_ROD features only.

### 1.5 Process notes

Readers shared one scratchpad and a script named fetch.sh, so a few fetches by the 6E, NG, RTY and ZC readers
landed under pages/LE or pages/GC; the readers moved or removed their own lines and listed the rest (no evidence
file was affected). Terms or robots.txt were read after a fetch in a few cases (arXiv, IDEAS, OpenAlex,
Wikipedia, ou.edu); two such files were deleted and not used (a Wikipedia path, an ou.edu PDF). No reader saw a
web-search over-budget notice; each reader file logs its own search count.


## 2. Feature availability matrix

```
feature               NQ RTY  ZT  ZF  ZN  TN  ZB  UB  6E  CL  NG  GC  ZC  ZS  ZL  HE  LE
cp1_ret               yy  py  yy  py  py  yy  py  py  yy  yy  yy  yy  py  py  py  yy  py
cp2_range             yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy  py  py  py  yy  py
cp2_brk               yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy  py  py  py  yy  py
cp3_clv               yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy  uy  yy  py  yy  py
k1_vwap_dist          yy  nn   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k1_vxn_regime         ny  nn   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k1_vxn_band           ny  nn   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k2_auction_mto         .   .  py  yy  yy  yy  yy  yy   .   .   .   .   .   .   .   .   .
k2_auction_msince      .   .  py  yy  yy  yy  yy  yy   .   .   .   .   .   .   .   .   .
k2_fomc_mto            .   .  py  py  py  yy  py  py   .   .   .   .   .   .   .   .   .
k2_monthend_msince     .   .  yy  yy  yy  yy  yy  yy   .   .   .   .   .   .   .   .   .
k2_predrift_move       .   .  uy   .  ny  nn  ny  uu   .   .   .   .   .   .   .   .   .
k3_ldnmom_trend        .   .   .   .   .   .   .   .  ny   .   .   .   .   .   .   .   .
k3_ldnrev_move         .   .   .   .   .   .   .   .  ny   .   .   .   .   .   .   .   .
k3_mehedge_req         .   .   .   .   .   .   .   .  ny   .   .   .   .   .   .   .   .
k3_ecbfix_mto          .   .   .   .   .   .   .   .  ny   .   .   .   .   .   .   .   .
k3_ecbfix_msince       .   .   .   .   .   .   .   .  ny   .   .   .   .   .   .   .   .
k3_tkypost_msince      .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k3_tkypre_msince       .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k4_apipre_ret          .   .   .   .   .   .   .   .   .  uy   .   .   .   .   .   .   .
k4_eiafade_move        .   .   .   .   .   .   .   .   .  py   .   .   .   .   .   .   .
k4_eiamom_r3           .   .   .   .   .   .   .   .   .  py   .   .   .   .   .   .   .
k4_ngpre_mto           .   .   .   .   .   .   .   .   .   .  yy   .   .   .   .   .   .
k4_ngpre_msince        .   .   .   .   .   .   .   .   .   .  yy   .   .   .   .   .   .
k4_ovr_ret             .   .   .   .   .   .   .   .   .  yy  yy   .   .   .   .   .   .
k4_ovr_pct             .   .   .   .   .   .   .   .   .  yy  yy   .   .   .   .   .   .
k5_ovr_ret             .   .   .   .   .   .   .   .   .   .   .  yy   .   .   .   .   .
k5_ovr_pct             .   .   .   .   .   .   .   .   .   .   .  yy   .   .   .   .   .
k5_pmfix_move          .   .   .   .   .   .   .   .   .   .   .  ny   .   .   .   .   .
k5_preauc_msince       .   .   .   .   .   .   .   .   .   .   .  ny   .   .   .   .   .
k6_crushgap_gap        .   .   .   .   .   .   .   .   .   .   .   .   .  py  py   .   .
k6_limitcont_dir       .   .   .   .   .   .   .   .   .   .   .   .   .   .   .  ny  ny
k6_wasdepre_drift      .   .   .   .   .   .   .   .   .   .   .   .  ny  ny   .   .   .
k7_expiry_mto          .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k7_expiry_msince       .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k7_montrend_ret        .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k7_rev2h_ret           .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k8_oilcad_ret          .   .   .   .   .   .   .   .  ny  py   .   .   .   .   .   .   .
k8_oilcad_z            .   .   .   .   .   .   .   .  ny  py   .   .   .   .   .   .   .
k8_wkndbtc_move       np  nn   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
k9_anncday            ny  ny   .   .  nn  nn   .  uu  ??   .   .   .   .   .   .  ??  uu
g01_ret30             yy  py  yy  yy  yy  yy  yy   .  yy  yy  yy  yy  py  yy  py  py  py
g02_ret60             yy   .  yy  yy  yy  yy  yy   .  yy  yy  yy  yy   .  yy  py  py  py
g03_ret120            yy   .  yy  yy  yy  yy  yy   .  yy  yy  yy  yy  py  yy  py  py  py
g04_ret_day           yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy   .  yy  py  py  py
g05_gap               yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy  py  yy  py  py  py
g06_rv60              yy  py  yy  yy  yy  py  yy  yy  yy  yy  yy  yy   .  yy  py  py  py
g07_range             yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy   .  yy  py  py  py
g08_prev_ret          yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy  py  yy  py  py  py
g09_vol_state         yy  py  yy  yy  yy  py  yy  yy  yy  yy  yy  yy   .  yy  py  py  py
g10_logvol30          yy  py  yy  yy  yy  py  yy  yy  yy  yy  yy  yy   .  yy  py  py  py
g11_t_index           yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy   .  yy  yy  yy  yy
g12_dow               yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy   .  yy  yy  yy  yy
g13_min_to_rel        py  py  py  uy  py  uy  py  py  py  py  yy  py  py  py  py  py  py
g14_min_since_rel     py  py  py  uy  py  uy  py  py  py  py  yy  py  py  py  py  py  py
g15_rel_day           py  py  py  uy  py  uy  py  py  py  py  yy  py  py  py  py  py  py
g16_month_end         yy  py  yy  yy  yy  yy  yy  yy  yy  yy  yy  yy   .  yy  yy  yy  yy
g17_nq                yy  nn  yy  uu  yy  uu  yy  uu  uu   .  yy  uu  uu  uu  uu  uu  yy
g17_zn                uu  uu  yy  nn  yy  nn  nn  uu  uu   .  yy   .  uu  uu  uu  uu  yy
g17_6e                uu  uu  yy  uu  yy  uu  yy  uu  yy   .  yy   .  uu  uu  uu  uu  yy
g17_cl                uu  uu  yy  uu  yy  uu  yy  uu  uu  yy  yy   .  uu  uu  uu  uu  yy
g17_gc                uu  uu  yy  uu  yy  uu  yy  uu  uu   .  yy  yy  uu  uu  uu  uu  yy
g17_zc                uu  uu  yy  uu  yy  uu  yy  uu  uu   .  yy   .  yy  uu  uu  uu  nn
g17_mbt               np  np  np  np  np  np  np  np  np   .  np  np  np  np  ny  uu  np
k8_flight_tail         .   .   .   .   .   .   .   .   .   .   .  ny   .   .   .   .   .
g17_mes               ny  ny  np  ny  np  np  np  ny  np   .  ny  np  ny  np  ny  uu  ny
k8_flight_ret          .   .   .   .   .   .   .   .   .   .   .  ny   .   .   .   .   .
```

## 3. Per-root evidence, proposals and notes

### NQ

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum, NQ regression | 30 min (14:30-15:00 CT) |  |  | gross | NQ 1-min, 1996-04-12..2020-05-01, 6017 days | none per market (see E3) | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | primary |
| E2 | Equity 1/N portfolio eta(r_ROD) | 30 min | 2.72 | 14.31 | gross | 17 equity index futures, to May 2020 | E3 | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | primary |
| E3 | Subsample stability, pooled equity | 30 min |  |  | gross | pooled equity futures 1974-1999 vs 2000-2020 | b_ROD 5.96 (t 4.80) -> 3.98 (t 6.65); R2 3.41 -> 2.34 | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | primary |
| E4 | Gamma conditioning (S&P 500 futures only) | 30 min |  |  | gross | S&P 500 futures, Jan 1996-May 2020; 2930 negative, 3158 positive NG... | none | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | primary |
| E5 | First-half-hour predictor and agreement filter | 30 min | 1.67 | 8.78 | gross | as E2 | r_ROD wins OOS horse race (Table 3) | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | primary |
| E6 | Overnight return -> last half hour; threshold form | 30 min |  |  | unknown | [unverified] S&P 500, Nasdaq 100, DJIA futures; Sep 1997-Dec 2020 (... | The predictability disappears in the out-of-sample period (abstract) | Rosa, Understanding intraday momentum strategies, J. Futures Markets 42(12) (... | unverified |
| E7 | Post-2020 SPX retest (unreviewed blog) | 30 min |  |  | gross | SPX cash, 1,085 sessions 2022-04-14..2026-08-20 | unconditional slope +0.006 (t +0.6); short-gamma interaction +0.055 (t +3.1) | firmtape via dev.to [shared, see shared/equity_class_notes.md] | secondary-only |
| E8 | Persistence 2008-2024 (Aalto thesis) | 30 min |  |  | unknown | 20 equity, bond, FX futures 2008-01..2024-10 | persists; most predictability in last ten minutes; mostly not feasible after costs | Aalto master's thesis [shared, see shared/aalto_thesis_notes.md] | primary |
| E9 | Gamma and intraday momentum after 0DTE |  |  |  | unknown |  |  | Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov (2026 draft) [shared, see s... | unverified |
| E10 | MNQ OHLCV intraday signal falsification (preprint, not a ROD test) | various |  |  | net | MNQ 5-min, 947 days, 2021-2025 | none for ROD | Mesfin, arXiv 2605.04004 (2026) | primary |

Proposed features: none

Unfinished or unverified (reader): 6 items; see product_NQ.md section 6.

### RTY

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Rest-of-day to last half-hour momentum (ROD -> LH), Russell 2000 futures | 30 min (14:30-15:00 CT) |  |  | gross | ER (Russell 2000 ICE/CME, regular before mini), 1993-02-08..2020-05... | Paper's own R2_OOS 3.15%; post-2020 for ER: none found. Equity post-2020: Adams et al. ... | Baltussen, Da, Lammers, Martens, J. Financial Economics 142 (2021) 377-403, T... | primary |
| E2 | Overnight-plus-first-half-hour to last half-hour (ONFH -> LH), Russell 2000 futures | 30 min (14:30-15:00 CT) |  |  | gross | ER 1993-02-08..2020-05-01 | R2_OOS 2.21% for ER, but ES ONFH R2_OOS -1.68% in the same table; the program's CP1 por... | Baltussen et al. (2021) Table B1 Panel B | primary |
| E3 | First half-hour (ONFH) sign -> last half-hour, SPY | 30 min | 2.65 | 5.3 | gross | SPY, 1993-02-01..2013-12-31, half-hour TAQ returns | None post-2013 in the paper. Later: ONFH form weak OOS (Baltussen ES R2_OOS -1.68%); Ro... | Gao, Han, Li, Zhou, J. Financial Economics 129 (2018) 394-414; read as workin... | primary |
| E4 | E3 after bid-ask spread costs | 30 min | 3.16 | 6.32 | net | SPY, 2005-01-01..2013-12-31 (Panel B); 2001-07-01.. (Panel A: 4.46%... | Spread stabilized near 1.2 bp after 2005 (Sec. 5.2) | Gao et al. (2015 WP) Table 10 | primary |
| E5 | First half-hour -> last half-hour, IWM (Russell 2000 ETF), mean-variance form | 30 min |  |  | gross | IWM 2000-05-26..2013-12-31 | None post-2013 | Gao et al. (2015 WP) Table 12 Panel A | primary |
| E6 | First half-hour sign -> last half-hour on FOMC statement days, SPY | 30 min | 7.95 | 15.9 | gross | SPY 1993-02-01..2013-12-31, about 8 FOMC days a year (about 165 tra... | None post-2013. Related pre-FOMC drift disappeared after 2015 (E11, abstract only) | Gao et al. (2015 WP) Table 8 Panel B | primary |
| E7 | Intraday time-series momentum, US (S&P 500 cash index) | 30 min | 2.61 | 5.22 | gross | S&P 500 index (.SPX 09:30-16:00), 2005-10-04..2017-12-29, 1-min data | Paper reports OOS significance in most countries; no post-2017 data | Li, Sakkas, Urquhart, J. Financial Markets 57 (2022) 100619 (accepted manuscr... | primary |
| E8 | Hourly momentum vs market-maker net gamma, E-mini S&P | 10-120 min | -1.144 |  | gross | ES, 01/2018..12/2024, 09:30-16:00 ET | This is itself post-2018 evidence: momentum turns to reversal when hedging needs are high | Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov, 'Do S&P 500 Options Increa... | primary |
| E9 | ROD -> LH retest on SPX in the 0DTE era (UNREVIEWED) | 30 min |  |  | gross | SPX, 1,085 sessions 2022-04-14..2026-08-20 | Unconditional slope +0.006 (t 0.6), flat each year; +0.055 (t 3.1) on short-gamma close... | firmtape, dev.to blog post, 2026-08-27 (unreviewed practitioner) | unverified |
| E10 | Pre-FOMC announcement drift, S&P 500 | 24 h (includes overnight); intraday p... |  |  | gross | SPX 1994-09..2011-03, 131 scheduled meetings (intraday) | E11: essentially disappeared after 2015 (abstract) | Lucca and Moench, NY Fed Staff Report 512 (rev. 2013); J. Finance 70 (2015) | primary |
| E11 | Pre-FOMC drift after 2015 (decay) | 24 h |  |  | unknown | US equities 1994-09..2019-12 | 'essentially disappeared after 2015' | Kurov, Wolfe, Gilbert, Finance Research Letters 40 (2021) | secondary-only |
| E12 | End-of-day momentum/reversal from LETF rebalancing and option gamma imbalance (single s... | to the close |  |  | gross | US stocks 2005-05..2020-07 | 'significant in all subsamples between 2012 and 2019'; LETF effect 'remained constant' | Barbon, Beckmeyer, Buraschi, Moerke, S/BF-HSG WP 2021/14 | primary |
| E13 | Noise-area intraday momentum, SPY (V34 dropped as unsized) | intraday, variable |  |  | net | SPY 2007..early 2024 | Not reported per period here | Zarattini, Aziz, Barbon, 'Beat the Market', WP (2024-05-10; 2025-02-03 version) | primary |
| E14 | Overnight return -> last half-hour; first half-hour not predictive (ETFs, 12 index futu... | 30 min |  |  | unknown | 1999-2014 (search snippet) | n/a | Liu and Tse, Int. Rev. Economics and Finance 48 (2017) | unverified |
| E15 | Intraday momentum and reversal in 20 equity, bond and FX futures, 2008-01..2024-10 (Aal... | n/a |  |  | unknown | 20 futures, 2008-2024 | Abstract: patterns persist, trading 'may not be feasible' after costs | Majorin (Aalto University thesis, 2025); shared, see shared/aalto_thesis_note... | secondary-only |

Proposed features: 
- `fomc_r1`: ratio to D8 2.51, clears 1.5x per reader: True; Published: 20.04%/yr on FOMC-day trades, annualized like a daily return, so 20.04/252 = 7.95 bp per trade gross (SPY, LH 15:30-16:00 ET, 1993-2013, about 165 events, t 2.46). M2K ticks per bp = L/1000: at L = 1,500 / 2,000 / 2,400 that is 11.9 / 15.9 / 19.1 ticks; D8 RT 6.346 ticks ($3.17), ratio...

Unfinished or unverified (reader): 7 items; see product_RTY.md section 6.

### ZT

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | 2Y auction pre-auction price decline (supply pressure), own tenor | 180 min (intraday) | 0.733 | 1.97 | gross | On-the-run cash 2Y note mid quotes, GovPX 1991-2000 and BrokerTec 2... | Pre leg not split by subperiod; combined price pressure (both legs) 1.348 bp 1991-2006,... | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | primary |
| E2 | 2Y auction post-auction price recovery, own tenor | 180 min (intraday) | 0.603 | 1.62 | gross | As E1 | As E1 (combined 0.887 bp in 2015-2024, about 0.44 bp per leg if split equally: about 1.... | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | primary |
| E3 | Auction spillover to the 2Y note from 3Y, 5Y, 10Y auctions (yield pressure, both legs) | two 180-min legs (intraday) | 0.95 | 2.56 | gross | As E1, full sample 1991-2024 only | No subperiod split for spillovers. Own-tenor 2Y yield pressure fell from 0.712 (full) t... | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | primary |
| E4 | Market intraday momentum ROD -> last half hour, US 2-year T-note futures (TU) | 30 min | 0.135 | 0.36 | gross | TU 1991-01-04..2020-05-01, 7153 obs, 08:20-15:00 ET; 1-minute Tickdata | Per-market row is full sample only; class decay: see shared/baltussen_notes.md (NQ read... | Baltussen, Da, Lammers, Martens (2021), JFE 142, 377-403, Table B2 Panel B (d... | primary |
| E5 | End-of-month 2Y Treasury excess return (last trading days of the month) | daily close-to-close over 1-2 days (i... | 2.5 | 6.7 | gross | Daily GSW zero-coupon 2Y, 5Y, 10Y, 1990-2018 (Table 4 subperiod to ... | Table 4: 2Y last-2-days 0.05*** in 2010-2014, 0.01 (n.s.) in 2015-2019; authors: 2015-2... | Hartley and Schwarz (2019), Predictable End-of-Month Treasury Returns, Rodney... | primary |
| E6 | Pre-FOMC (day -1) drift at the short end: null for the 2Y | daily (not intraday) | 0.47 | 1.26 | gross | Daily ACM zero-coupon yields, Sep 1994..Dec 2025 | n/a (null) | Pan and Peng (2026 draft), The Pre-FOMC Drift in Long-Term Treasury Bonds (SAIF) | primary |
| E7 | Pre-FOMC 24h window (2pm to 2pm) in the 2Y Treasury: null | 24 h (includes overnight) |  |  | gross | Benchmark 2Y, Sep 1994..Mar 2011 (pre-2015 sample) | n/a (null) | Lucca and Moench, The Pre-FOMC Announcement Drift, FRBNY SR 512 (rev. Aug 201... | primary |

Proposed features: 
- `zt_cpnauc_mto / zt_cpnauc_msince (2Y-note pressure clock on 2Y, 3Y, 5Y and 10Y auction dates)`: ratio to D8 0.75, clears 1.5x per reader: False; Full sample, 5Y/10Y-auction days: 0.97-1.01 bp yield (two legs) x 1.876 = 1.81-1.90 bp price, about 0.93 bp per 180-min leg (equal split assumed) = 2.5 ticks at P=105. The V2.2 clock captures at most 60 of the 180 pre-auction minutes (t2 10:20 h60) and 120 of the post-auction minutes starting 48 ...

Unfinished or unverified (reader): 6 items; see product_ZT.md section 6.

### ZF

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum ROD->last half hour, FV alone | 30 min | 0.41 | 0.62 | gross | FV 1988-07-06..2020-05-01, 7907 days, 1-min | none for FV in paper; class: Aalto abstract (bonds least feasible after costs) [shared,... | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | primary |
| E1b | Same, government bond 1/N portfolio (class) | 30 min | 0.86 | 1.29 | gross | 16 bond futures to 2020-05 | as E1 | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | primary |
| E2 | 5-year auction pre-auction price pressure (short leg) | 180 min (clock: t2 10:20 CT h60 = clo... | 0.79 | 1.19 | gross | on-the-run 5y note, GovPX 1991-2000, BrokerTec 2001-2024, auctions ... | 5y yield pressure S1 0.869, S2 1.436, S3 2015-2024 0.919***; F S3=S1 0.012; price press... | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | primary |
| E3 | 5-year auction post-auction reversal (long leg) | 180 min (clock: t3 12:50 CT = release... | 1.1 | 1.66 | gross | as E2 | as E2 | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | primary |
| E4 | Cross-tenor auction spillover onto the 5-year (10Y and 7Y auctions) | 2 x 180 min (clock legs as E2/E3) | 1.33 | 2.01 | gross | as E2, full sample only | no subsample for spillovers; 10Y own pressure S3 0.593 vs full 1.192 | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | primary |
| E5 | FOMC and payrolls 3-hour windows: null pre-FOMC and NFP; post-FOMC yield decline (after... | 180 min |  |  | gross | 1997..2024-07-24 | none given | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | primary |

Proposed features: 
- `zf_auc10y_mto / zf_auc10y_msince`: ratio to D8 0.76, clears 1.5x per reader: False; Spillover price pressure 1.259 bp yield x 4.40 = 5.54 bp over both 180-min legs (full sample 1991-2024). Clock shares from the 5y own-auction Figure 2(c) path (assumed to transfer): post leg t3->F 24% = 1.33 bp = 2.01 ticks (ratio 1.53); pre leg t2/h60 17% = 0.96 bp = 1.45 ticks (ratio 1.10). Dec...

Unfinished or unverified (reader): 7 items; see product_ZF.md section 6.

### ZN

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum ROD->LH, bond futures | 30 min | 0.86 | 0.6 | gross | 16 developed bond futures, 1/N portfolio, 1974-12..2020-05, 1-min; ... | Table 5 bonds beta_ROD 3.19*** (8.38) R2 1.28 in 1974-1999 vs 1.53*** (3.61) R2 0.47 in... | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | primary |
| E2 | Intraday momentum and reversal, 20 equity/bond/FX futures 2008-2024 | 30 min |  |  | net | 20 futures indices in equities, bonds and currencies, 2008-01..2024-10 | 'the intraday momentum patterns still exist in our dataset spanning January 2008 to Oct... | Majorin (2025), Intraday momentum in futures markets, Aalto University MSc th... | unverified |
| E3 | 10-year auction day, pre-auction price decline | 180 min | 2.64 | 1.86 | gross | on-the-run cash 10Y, GovPX 1991-06..2000-12, BrokerTec 2001-01..202... | Table 2 10Y yield pressure S1 1991-2006 1.491***, S2 2007-2014 1.732***, S3 2015-2024 0... | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | primary |
| E4 | 10-year auction day, post-auction price recovery | 180 min | 4.2 | 2.96 | gross | as E3 | Table 3 10Y price pressure S1 10.883***, S2 15.222***, S3 2015-2024 5.165* (no leg spli... | Fleming, Liu, Nguyen (2026), FRBNY SR 1188 | primary |
| E5 | Cross-tenor auction spillover into the 10-year | 2 x 180 min |  | 1.55 | gross | as E3, full sample only | none reported for spillovers; own-tenor effect halves after 2014 | Fleming, Liu, Nguyen (2026), FRBNY SR 1188 | primary |
| E6 | 10-year auction day, ZN futures decline ahead of the auction | unstated | 6.0 | 4.2 | gross | US 10-year T-Note futures, Tickdata, 1983-01..2024-08, 382 million ... | none reported | Houweling, Penninga, Martinetti (Robeco), Quant chart: US Treasuries up for a... | primary |
| E7 | Pre-announcement drift (macro releases) | 30 min |  |  | gross | 10-year T-note and ES futures, second-by-second, 2008-01..2014-03 | 'the price drift has increased since 2007'; post-2015 unknown | Kurov, Sancetta, Strasser, Wolfe, ECB WP 1901 (2016); JFQA 54 (2019) | primary |
| E8 | Pre-FOMC drift in Treasuries (null) | 24 h (2pm-2pm) | 0.0 | 0.0 | gross | 1994-2011 and 1980-2011, daily windows | n/a | Lucca and Moench, The Pre-FOMC Announcement Drift, FRBNY SR 512 (rev. 2013); ... | primary |
| E9 | Post-FOMC drift in long bond futures | up to 15 days |  |  | gross | post-GFC transaction-level US and German long bond futures | 'absence of pre-FOMC announcement drift' | Indriawan, Jiao, Tse (2021), J. Banking & Finance 123, 106027 | secondary-only |
| E10 | End-of-month Treasury futures returns (close-to-close, not intraday) | 1 to 5 days incl. overnight | 9.0 | 6.3 | gross | Treasury futures 1990-2018, daily | not reported | Hartley and Schwarz (2019), Predictable End-of-Month Treasury Returns, Wharto... | primary |
| E11 | Month-end index strike time (activity, no returns) | n/a |  |  | unknown | Treasury cash trading activity | strike moved 3 pm to 4 pm ET in January 2021 | Dyer, Fleming, Shachar, Treasury Trading at the Close, Liberty Street Economi... | primary |
| E12 | First-15 to last-15 minute momentum, Chinese Treasury bond futures | 15 min |  |  | unknown | CFFEX Treasury bond futures (years not seen) | unknown | Zhang, Wang, Li (2021), Bond intraday momentum, J. Behavioral and Experimenta... | secondary-only |
| E13 | Intraday trend (>=1 h) and reversion (<=16 min), pooled incl. US 10-year futures | 1 h+ |  |  | gross | 24 futures (US/Can/Ger/UK 10-year among rates), end-of-minute, 2010... | n/a | Safari and Schmidhuber (2025), Trends and Reversion in Financial Markets on T... | primary |

Proposed features: none

Unfinished or unverified (reader): 7 items; see product_ZN.md section 6.

### TN

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | (absence) TN not in the Baltussen et al. ROD->LH sample | last 30 min |  |  | gross | 16 developed bond futures; US contracts TU, FV, TY, US, UB; 1974-2020 | class decay: [shared, see shared/baltussen_notes.md, shared/aalto_thesis_notes.md] | Baltussen, Da, Lammers, Martens, J. Financial Economics 142 (2021) 377-403 | primary |
| E2 | (context, no return effect) TN is one of six CBOT futures buckets in a DV01-volume liqu... | n/a |  |  | unknown | CBOT futures and TRACE, 2017-07-10..2018-06-01 (229 days) | n/a | Baker, McPhail, Tuckman, CFTC staff note, 2018-12-03 | primary |
| E3 | (class pointer, not TN) minute-scale reversion and hours-scale weak trending, pooled ov... | 1 minute |  |  | gross | TickData end-of-minute 2010-2023; rates: US, CA, DE, UK 10-year | none per market | Safari, Schmidhuber, arXiv 2501.16772v2 (2025) | primary |
| E4 | (class pointer) rates-class ROD->LH and other Treasury-futures intraday effects |  | 0.9 |  | gross |  |  | [shared, see shared/rates_class_notes.md]; planning brief line 27-29 | unverified |
| E5 | (class pointer) 10-year auction-day intraday price pressure | hours |  |  | gross | 10Y T-note futures 1983-2024 (Robeco); 33 years intraday (SR1188) | SR1188 snippet: pressure has not risen in recent years | Robeco quant chart 2025-03; Fleming, Liu, Nguyen, NY Fed Staff Report 1188 (2... | secondary-only |
| E6 | (class pointer) post-FOMC drift in long-term US bond futures (multi-day, out of scope) | ~15 days |  |  | unknown |  |  | Indriawan, Jiao, Tse, J. Banking and Finance (2021) | secondary-only |

Proposed features: none

Unfinished or unverified (reader): 6 items; see product_TN.md section 6.

### ZB

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Pre-auction price pressure, 30-year bond, own auction (inverted-V yields around the auc... | 180 min (pre); 180 min (post) | 7.61 | 3.41 | gross | On-the-run cash 30Y (GovPX 1991-2000, BrokerTec 2001-2024-07), 1-mi... | 30Y yield pressure by subsample: 1991-2006 0.394 (ns), 2007-2014 1.448***, 2015-2024 0.... | Fleming, Liu, Nguyen (2026), 'Intraday Price Pressure and Order Flow Around U... | primary |
| E2 | Cross-tenor spillover: 10-year (and 5-, 7-year) auctions put yield pressure on the 30-y... | 180 min (pre) | 8.54 | 3.83 | gross | As E1 (on-the-run cash, 1991-2024) | No subsample split for spillovers. Own-tenor 10Y yield pressure falls from 1.192*** (fu... | Fleming, Liu, Nguyen (2026), FRBNY SR 1188 | primary |
| E3 | Post-FOMC yield decline (unconditional) and nulls before FOMC / around payrolls | up to 180 min after the statement |  |  | gross | On-the-run cash, FOMC 1997-2024-07 (Figure A4) | Not reported by subsample. | Fleming, Liu, Nguyen (2026), FRBNY SR 1188 | primary |
| E4 | Market intraday momentum ROD -> LH, US 30-year T-bond futures row | 30 min | 2.11 | 0.95 | gross | US (ZB) futures, 1-min, panel range Oct 1982 - May 2020 | Full-sample OOS R2 0.22%; post-2020 evidence is the shared Aalto/Adams items (see NQ, Z... | Baltussen, Da, Lammers, Martens (2021), JFE 142, 377-403 (on-disk copy) | primary |
| E5 | End-of-month Treasury returns (daily, not intraday), 30-year futures | 1 to 6 trading days (includes overnight) | 15.0 | 6.72 | gross | Treasury futures (5, 10, 30-year), daily, 1990-2018 | Text: 'The estimates in the final period, from 2015-2018 are smaller than most of the o... | Hartley, Schwarz (2019), 'Predictable End-of-Month Treasury Returns', Rodney ... | primary |
| E6 | Pre-release drift before ISM Non-Manufacturing (Services); 30-year bond futures in robu... | ~30 min |  |  | unknown | ES, ZN (main); E-mini Dow and 30-year bond futures (robustness); 20... | Pre-2015 sample; V34 dropped unsized pre-announcement drift. Class item: see ZN reader. | Kurov, Sancetta, Strasser, Wolfe (2019), JFQA (as logged by Stage E.0, item K... | secondary-only |
| E7 | Post-FOMC drift in long-term US bond futures, signed by the policy surprise; no pre-FOM... | multi-day |  |  | unknown | post-crisis transaction-level data (abstract) | unknown | Indriawan, Jiao, Tse (2021), J. Banking & Finance 123, 106027 | secondary-only |
| E8 | Intraday momentum/reversal in bond futures 2008-2024: persists but mostly not after cos... | intraday |  |  | net | 20 equity, bond, currency futures, 2008-01..2024-10 | after-cost failure stated for bonds | Aalto master's thesis (2025) [shared, see reports/stage_e20_briefs/shared/aal... | secondary-only |

Proposed features: 
- `k2_auc10_mto_zb (minutes to the 10-year note auction close, on ZB rows)`: ratio to D8 0.79, clears 1.5x per reader: False; Pre-auction share of the 1.294 bp total assumed 0.55 (bracket 0.37-0.73) -> 0.712 bp over T_a-180..T_a-1 (09:00-12:00 CT). Short at t2 = 10:20 CT with h120 (exit 12:20): 100/180 of the pre leg minus 20/180 of the post reversal = 0.331 bp yield x D 12 = 3.97 bp = 1.78 ticks at P=140 on the 1991-20...

Unfinished or unverified (reader): 4 items; see product_ZB.md section 6.

### UB

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD->LH intraday momentum, UB's own regression row | 30 min | 2.1 | 1.01 | gross | UB 2010-02-03..2020-05-01, 2564 days, 1-min Tickdata bars, hours 08... | R2_OOS -3.40% on UB (r_ONFH -2.24, 3-variable model -1.92): negative out of sample | Baltussen, Da, Lammers, Martens (JFE 142, 2021) Table B2 Panel B, Table A2 | primary |
| E2 | Pre-auction concession, 30-year bond (UB's auction tenor) | 180 min | 12.075 | 5.8 | gross | on-the-run CASH 30-year bond, GovPX/BrokerTec midquotes, 223 auctio... | 2015-2024 total price pressure 14.224* vs 25.514*** in 2007-2014 (F S3=S2 1.116, n.s.);... | Fleming, Liu, Nguyen, FRBNY Staff Report 1188 (March 2026, revised July 2026)... | primary |
| E3 | Post-auction reversal, 30-year bond | 180 min | 5.031 | 2.41 | gross | as E2 | null over the full sample | Fleming, Liu, Nguyen (2026) Table 3, p.19 | primary |
| E4 | FOMC and employment windows: no auction-style V-shape | - |  |  | unknown | as E2 |  | Fleming, Liu, Nguyen (2026) p.4 | primary |
| E5 | Post-FOMC drift in long-term US bond futures | days (persists 15 days) |  |  | unknown | long-term US and German bond futures, transaction data, post-financ... | none visible | Indriawan, Jiao, Tse (J. Banking & Finance 123, 2021), doi 10.1016/j.jbankfin... | secondary-only |
| E6 | Leveraged-ETF share (mechanism of E1): UB largest among bond futures | - |  |  | unknown | 2006-06..2020-05 | bond diff-in-diff 'positive but insignificantly so' (Section 4.2) | Baltussen et al. (2021) Fig. 4 panel (b) | primary |

Proposed features: none

Unfinished or unverified (reader): 7 items; see product_UB.md section 6.

### 6E

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum ROD->LH, currency futures (Baltussen et al.) | 30 min (last half hour) | 0.337 | 0.75 | gross | 8 US-listed currency futures, 1974-12..2020-05 (Euro FX EC 1999-01-... | Subsample Table 5 Panel B 2000-2020: currency beta_ROD 0.33 (t 1.45), insignificant (19... | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | primary |
| E2 | Post-London-fix U.S. dollar depreciation (EUR appreciates after the 16:00 London fix) | 6 h (10:00-16:00 CT); inside the 6E d... | 2.73 | 6.06 | gross | EUR/USD spot (Refinitiv Tick History), 1999-01..2019-12, intraday | Dollar portfolio post-L by subsample (Table II): 2.80 (99-03), 2.29 (04-09), 1.43 (10-1... | Krohn, Mueller, Whelan (2024), Foreign Exchange Fixings and Returns Around th... | primary |
| E3 | Pre-ECB-fix U.S. dollar appreciation (EUR depreciates 02:00-08:15 ET) | 6.25 h, entirely before t1 (07:50 CT)... | 3.53 | 7.84 | gross | EUR/USD spot, 1999-2019 | Dollar portfolio pre-E by subsample (Table II): -3.43, -1.50, -0.35 (t -0.40), -1.25 (t... | Krohn, Mueller, Whelan (2024), JF | primary |
| E4 | ECB-fix 15-minute reversal and its move after July 2016 | 15 min (below the v2 60-min minimum) | 0.96 | 2.13 | gross | EUR/USD (Olsen, RTH), 1986-2019 in three panels | Turning point moved by 15 min in July 2016 (Panel C: 08:15-08:30 ET -0.07, t -0.44). K3... | Krohn, Mueller, Whelan (2024), JF | primary |
| E5 | End-of-month WMR fix reversal (contrarian after the 4 pm fix) | 1-15 min (below the v2 60-min minimum) |  |  | net | 21 currency pairs, 2004-2013, Gain Capital 1-s data and EBS; fix wi... | Author reports pre-2010 estimates similar and post-2010 out-of-sample average 3.25% acr... | Evans (2018), Forex trading and the WMR Fix, J. Banking & Finance 87, 233-247... | primary |
| E6 | Month-end equity-hedge rebalancing before the 4 pm fix (Melvin and Prins) | 60 min (15:00-16:00 London = 09:00-10... | 1.42 | 3.15 | gross | 10 currencies, 5-min TWAPs from EBS/Reuters, 2004-04-28..2012-12-31... | None found after 2012. The fix window widened from 1 to 5 min on 2015-02-15 (BIS, Debel... | Melvin, Prins (2015), Equity hedging and exchange rates at the London 4 p.m. ... | primary |
| E7 | FOMC-day currency drift and reversal (foreign currencies appreciate before and at the a... | 12-hour half-day windows (overlaps th... |  |  | gross | 17 currencies, 136 scheduled FOMC meetings, 1999-01..2015-12, 15-mi... | Published version (Lee and Wang, RAPS 15(3-4) 2025, 247-287) not retrieved; abstract pe... | Wang (2018), Essays on currency markets, PhD dissertation, Georgia Institute ... | primary |
| E8 | ECB communication outside meeting days: no EUR/USD drift (null) | up to 20 min |  |  | gross | EUR/USD 1-min, 2008-2016 | null result | Fanta (2025), ECB monetary policy communication: an event study on intraday r... | primary |
| E9 | Intraday momentum and reversal in currency futures 2008-2024: not feasible after costs ... | last half hour |  |  | net | 20 equity, bond and currency futures, 2008-01..2024-10 | 'most intraday momentum and reversal trading strategies may not be feasible after trans... | Aalto University master's thesis (2025), read by ProductReader-ZN | secondary-only |

Proposed features: 
- `p6e_mehedge_nq`: ratio to D8 1.14, clears 1.5x per reader: False; Expected figure and ratio are per 1% of relative month-to-date equity return (conditional slope, not an unconditional mean). 1.42 bp per 1% of relative (US minus euro-area) month-to-date equity return over the full 60-min pre-fix hour; the t1/h120 hold (07:50-09:50 CT) overlaps 50 of those 60 min...
- `p6e_post_ldnfix`: ratio to D8 0.66, clears 1.5x per reader: False; Expected figure uses the latest published subsample (dollar portfolio 2014-2019, the closest to the search window). Full sample 1999-2019: EUR post-L 2.73 bp over 10:00-16:00 CT; t2 to F (10:20-15:08 CT, 4.8 of 6 h, pro rata) 2.18 bp = 4.85 ticks, ratio 2.10 to D8. Latest published subsample (dol...

Unfinished or unverified (reader): 8 items; see product_6E.md section 6.

### CL

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD -> LH momentum in CL futures | 30 min |  |  | gross | CL tickdata 1987-01-06..2020-05-01, 8,336 days, 1-min | R2_OOS -1.04% over the full sample (a null) | Baltussen, Da, Lammers, Martens (JFE 142, 2021), Table B3 and Table A3 | primary |
| E2 | EIA-day third half-hour -> last half-hour (USO) | 30 min | 9.32 | 6.28 | gross | USO ETF 1-min 2006-04-10..2019-07-31, 591 EIA Wednesdays | rolling 5-year interaction coefficient 'albeit with a declining trend'; 'not observed' ... | Wen, Indriawan, Lien, Xu, Energy Journal 44(5) 2023 149-171 (accepted version) | primary |
| E3 | Non-EIA-day first half-hour -> last half-hour (USO) | 30 min | 0.94 | 0.63 | gross | USO 2006-04-10..2019-07-31, 2,649 non-EIA days | predictive source is mainly the overnight component (Table 2) | Wen, Indriawan, Lien, Xu 2023 | primary |
| E4 | Overnight component -> last half-hour (USO) | 30 min |  |  | gross | as E3 | n/a | Wen, Indriawan, Lien, Xu 2023 | primary |
| E5 | r3 on non-EIA days (placebo null) | 30 min |  |  | gross | as E3 | n/a | Wen, Indriawan, Lien, Xu 2023 | primary |
| E6 | Pre-EIA buyer-initiated flow; price -0.25% before the release | about 2 h |  |  | unknown | WTI futures (years not verified) | n/a | Rousse and Sevi, Energy Journal 40(2) 2019 139-160 | secondary-only |
| E7 | API and EIA inventory surprises move 5-min CL returns | minutes |  |  | unknown | CL futures about 2013-2014 (search summary) | n/a | Ye and Karali, Energy Economics 59 (2016) 349-364 | secondary-only |
| E8 | Post-WPSR reversion within about 25 minutes | minutes |  |  | unknown | WTI futures around EIA reports | n/a | Geman and Li, Journal of Energy Markets 11(2) 2018 | secondary-only |
| E9 | Intraday overreactions then reversals, energy most | <= 1 h |  |  | gross | 20 commodity futures 2019-11-20..2020-06-03 | 6.5-month sample | Borgards, Czudaj, Van Hoang, Resources Policy (ISSN 0301-4207) | secondary-only |
| E10 | Brent time-of-day long-short (not CL) | intraday |  |  | net | ICE Brent tick data 2010-01..2021-10, 1-min | n/a | Haugom, Ouyang, Smith-Meyer, Stordal et al., Quantitative Finance 2025 | secondary-only |
| E11 | Settlement window 13:28-13:30 CT: no systematic study found | n/a |  |  | unknown | one event | n/a | Ge, Kang, Tang, Yang (AEA 2023 session paper) | secondary-only |
| E12 | Passive-fill adverse selection in CL (execution) | n/a |  |  | n/a | CL Jun24, 2024-04-23, one day | n/a | Lalor and Swishchuk, arXiv 2409.12721 | primary |

Proposed features: none

Unfinished or unverified (reader): 6 items; see product_CL.md section 6.

### NG

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | EIA storage-day short around the WNGSR release (pre- plus post-announcement), whole sample | 120 min (09:00-11:00 ET standard) | 34.3 | 10.3 | gross | NYMEX NG first nearby, 2003-03..2018-12, 699 announcements, 5-minut... | Table 8 Panel B (before 2011) raw 32.85%/yr (63.2 bp/event), Sharpe 4.22; Panel C (afte... | Prokopczuk, Wese Simen, Wichmann (2021), The Natural Gas Announcement Day Puz... | primary |
| E2 | Same storage-day short, after 2011 (the decay result) | 120 min | 5.6 | 1.68 | gross | NG first nearby, 2011..2018-12 (Panel C) | Not significant (p 0.558); net negative after transaction cost; Table 7 Panel B: positi... | Prokopczuk, Wese Simen, Wichmann (2021), Energy Journal 42(2) | primary |
| E3 | Decomposition of the storage-day return: 99% inside (-90,+30); half pre (-90,-5), half ... | n/a (windows of 85 and 35 min) | 37.0 | 11.1 | gross | NG 2003-03..2018-12, 699 announcement days, 5-minute data | See E2; the 60- and 30-minute pre-windows weaken (fn 20: 'the effect steadily decreases'). | Prokopczuk, Wese Simen, Wichmann (2021) | primary |
| E4 | Pre-announcement drift traded on an analyst-forecast predictor (informed-trading signal) | 85 min |  |  | unknown | NG nearby, 2008-07..2016-01, 334 announcements (387 less 53 same-da... | 24-month moving average of strategy returns 'positive for the entire sample period' (to... | Gu and Kurov (2018), J. Futures Markets 38(9) 1079-1096, doi 10.1002/fut.2192... | primary |
| E5 | Market intraday momentum ROD -> LH, NG's own regression row | 30 min (13:00-13:30 CT) |  |  | gross | NG (Tickdata), 1993-01-06..2020-05-01, 6824 obs, 1-minute bars | Not reported per market; post-2020 class evidence: [shared, see reports/stage_e20_brief... | Baltussen, Da, Lammers, Martens (2021), JFE 142, 377-403, Table B3 Panel B (o... | primary |
| E6 | Week-to-week reversal of NG storage surprises; prices impound analyst forecasts before ... | n/a |  |  | unknown | not read | none found | Ederington, Lin, Linn, Yang (2019), EIA Storage Announcements, Analyst Storag... | secondary-only |
| E7 | Leveraged/futures-ETF rebalancing pressure in NG (and VIX, oil, gold, silver) | daily (open to close per a search sum... |  |  | unknown | not read (PDF not obtained; BIS PDF URL redirected to the landing p... | none retrieved | Todorov (2021), Passive funds affect prices: evidence from the most ETF-domin... | secondary-only |
| E8 | Weather-forecast revisions and intraday NG futures moves (00 and 18 UTC runs) | n/a |  |  | unknown | Princeton senior thesis (2022), not peer reviewed; not retrieved | none | Princeton senior thesis 'Weather Forecasts and Natural Gas Futures Price Dyna... | unverified |
| E9 | NG settlement window (13:28-13:30 CT), NG post-release reversal, NG time-of-day seasona... | n/a |  |  | unknown | n/a | Null search result: no post-2015 study found in 6 WebSearch queries and an OpenAlex que... | searches logged in md section 5 | unverified |
| E10 | Intraday patterns in NG futures from HFT data (VPIN/ML signals) | n/a |  |  | unknown | not read | not read | Song, Lopez de Prado, Simon, Wu (2015), Intraday Patterns in Natural Gas Futu... | unverified |

Proposed features: none

Unfinished or unverified (reader): 8 items; see product_NG.md section 6.

### GC

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD->LH market intraday momentum (GC row; commodity portfolio) | 30 min ending 12:30 CT | 1.72 | 3.1 | gross | GC 1984-01-05..2020-05-01, 9044 obs, 1-min | commodity beta_ROD 1.59 (t3.92) 1974-1999 vs 1.04 (t2.86) 2000-2020; GC R2_OOS 0.08%; n... | Baltussen, Da, Lammers, Martens, JFE 142 (2021) 377-403 | primary |
| E2 | London fix window in GC before/after 2015 auction reform | 10/30/60 min | 5.65 | 6.7 | gross | GC Globex 2012-02-14..2015-04-30 | pre 9.41 vs post 5.65 bp, diff -3.76 n.s.; post-reform 'no significant leakage prior to... | Aspris, Foley, Gratton, O'Neill (2017) Transparency in Commodities Markets, E... | primary |
| E3 | PM fix leakage under the pre-2015 telephone fixing (context; published 2014) | 4 min after fix start | 10.0 |  | gross | GC 2007-01-01..2012-12-31, 1504 days, 1-min | regime replaced 2015-03-20; E2 finds no pre-start leakage after | Caminschi & Heaney, J. Futures Markets 34(11) 2014 1003-1039 (UWA AAM) | primary |
| E4 | Hat-shaped 24h gold pattern; drop into AM/PM London fix | 30 min | -1.7 | -3.0 | gross | GC1/GC2 5-min 2001-2018 | PM fix strong 2007-2011, 'small and insignificant' before and after; West significant o... | Donati & Jung, Gold Price Dynamics Around the Clock, CBS MSc thesis 2019 | primary |
| E5 | Abnormal-return-day momentum (S1, look-ahead) and next-day contrarian for gold (S2) | to day end (GMT+3) | 7.0 | 12.6 | gross | broker (MetaQuotes) hourly 2009-01-01..2020-03-31 | none; S2 'Not rejected' vs random; S1 selects days by ex-post daily return | Caporale & Plastun, Financial Markets and Portfolio Management 35 (2021) 353-368 | primary |
| E6 | FOMC surprise response in gold futures | 5-10 min | 23.0 |  | gross | GC 5-min 2007-01-02..2020-12-31 | none | Awartani, Hussain, Virk, IRFA 103486 (2024), AAM | primary |
| E7 | Intraday overreaction-reversal (turning points, ex post) | to next turning point |  |  | gross | 20 futures incl GC, 2019-11-20..2020-06-03 | Covid-dominated; no OOS | Borgards, Czudaj, Hoang, Resources Policy 71 (2021) 101966 | primary |
| E8 | Negative day (open-to-close) returns in COMEX gold | day session |  |  | unknown | COMEX GC front; 1985-2012 (2014 paper) | 'The asymmetry has weakened substantially over the years, but it is still present' (2014) | Blose, Gondhalekar, Kort, J. Econ. Finance 42(3) 2018; Blose & Gondhalekar AE... | secondary-only |
| E9 | Flight to gold after extreme negative 5-min S&P 500 returns (K8-flight source) | minutes |  |  | unknown | 2007-2018 intraday gold and S&P500 |  | Baur & Kuck, Finance Research Letters 33 (2020) | secondary-only |
| E10 | Fix reform, daily gold futures (not intraday) | daily |  |  | unknown | CME Globex SI/GC daily 2008-01-01..2018-06-27 | n/a | Crain, Hoelscher, Jones, ACRN JoFRP 9 (2020) 177-197 | primary |
| E11 | First half-hour momentum in SHFE gold; disappears after night trading | 30 min |  |  | unknown | SHFE gold 2008-01-10..2021-10-20 | predictability disappears after night-session launch | Zhou (Ivy) et al., Night trading momentum..., ACFR conference paper | secondary-only |
| E12 | Macro announcement response in gold futures complete within 90 s | 90 s |  |  | unknown | GC 2006-11-24..2012-12-31 |  | Smales & Yang, IRFA 41 (2015) 292-302 | secondary-only |
| E13 | Fix reform improved spreads and depth in exchange products | n/a |  |  | unknown |  |  | Aspris, Foley, O'Neill, JFM 40(11) 2020 | secondary-only |
| E14 | COMEX settlement window (12:29-12:30 CT) effects |  |  |  | unknown |  | null result of 2 searches: gap, not evidence of absence |  | unverified |

Proposed features: none

Unfinished or unverified (reader): 8 items; see product_GC.md section 6.

### ZC

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD -> last half-hour momentum, corn (CN) | 30 min | 1.44 | 0.26 | gross | CN 1982-07-06..2020-05-01, 1-min, 9,462 days | full-sample R2_OOS -0.01% (negative); Fig.4(c) 2006-06..2020-05 t 2.8 in-sample | Baltussen, Da, Lammers, Martens (2021) JFE 142:377-403, Table B3 Panel B | primary |
| E2 | ROD -> LH, 'Softs' pool (grains, livestock, softs) | 30 min |  |  | gross | 1981-04..2020-05 | R2_OOS -0.01% | Baltussen et al. (2021) Table B3 Panel A | primary |
| E3 | Commodity class eta(r_ROD) portfolio | 30 min | 1.72 |  | gross | to 2020-05 | class beta 1.59 (t 3.92) 1974-1999 vs 1.04 (t 2.86) 2000-2020 | [shared, see shared/baltussen_notes.md] | primary |
| E4 | WASDE surprise response, corn and soybeans | 10 min / 30 min / to close |  |  | gross | 122 WASDE releases, 2010-2021 | corn adjusts very little after 30 min (no post-30-min drift); needs proprietary poll | Anderson, McKenzie, Noyes (2024) NCCC-134 working paper | primary |
| E5 | WASDE-day intraday volatility curve, corn and soybeans | n/a |  |  | unknown | 2013-01..2023-04, 08:30-14:00 CT | n/a | Lee and Park (2024), summarized by co-author E. Park, Southern Ag Today | secondary-only |
| E6 | Intraday jumps around USDA reports, corn | n/a |  |  | unknown | corn nearby, 2008-2015 | n/a | Couleau, Serra, Garcia (2018) NCCC-134; AJAE 2020 | primary |
| E7 | Corn-soy volatility and spillover on USDA days | n/a |  |  | unknown | CME mid-quotes, 11:00 releases | n/a | Bian, Serra, Garcia (2018) NCCC-134 | primary |
| E8 | Adjustment speed after in-session releases | n/a |  |  | unknown | 2009-2014 intraday | n/a | Adjemian and Irwin (2018) AJAE 100(4), p.1169, quoted by Isengildina-Massa (V... | secondary-only |
| E9 | Trend of USDA announcement effects (daily volatility) | daily |  |  | unknown | corn, soybeans, multi-decade daily | generally increasing impact; some reports declining | Ying, Chen, Dorfman (2017) NCCC-134 | primary |
| E10 | Limit-day continuation (9 commodities incl. corn) | next-day close-to-close (includes ove... |  |  | gross | 1991-01-07..2016-05-23 daily | 90%-of-limit moves show small returns | Janardanan, Qiao, Rouwenhorst, JFM 39(8) 2019 (WP Feb 2017) | secondary-only |

Proposed features: none

Unfinished or unverified (reader): 9 items; see product_ZC.md section 6.

### ZS

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD->LH market intraday momentum on soybeans: null; ONFH->LH reversal, negative OOS R2 | last 30 min (12:50-13:20 CT) | 0.0 |  | gross | SY CBOT soybeans, 1-min, 1982-07-06..2020-05-01 (Table B3 panel Apr... | R2_OOS -0.07 (ROD) and -0.04 (ONFH) on SY; pooled Softs ROD R2_OOS -0.01 | Baltussen, Da, Lammers, Martens (2021), J. Financial Economics 142, 377-403, ... | primary |
| E2 | WASDE news -> soybean price reaction grows after 30 minutes (to the day close) | 10 min / 30 min / to close | 14.6 |  | gross | CME nearby corn and soybeans, 2010-2021, 122 WASDE events (26% earl... | none (no OOS, single sample) | Anderson, McKenzie, Noyes (2024), NCCC-134 proceedings | primary |
| E3 | USDA report windows in ZS: volatility spike, no systematic under/overreaction | up to 60 min |  |  | unknown | ZS nearby, Globex time and sales, Jun 2010-May 2014, 59 releases | n/a | Joseph and Garcia (2016), AAEA selected paper, AgEcon 10.22004/ag.econ.235772 | primary |
| E4 | Crush-spread intraday deviations from USDA-implied processing relationship mean-revert;... | not stated |  |  | net | 8,650 trading days, Sep 1990-May 2021 | not stated | Abdoh and Chitavi (2025), Int. Rev. Econ. Finance 101, 104186 | secondary-only |
| E5 | Soybean-complex intraday cointegration depends on liquidity and time of day (no trading... | n/a |  |  | unknown | CME 2015, 243 trading days | n/a | Zhou, Bagnarosa, Gohin, Pennings, Debie (2023), J. Commodity Markets 30, 1003... | primary |
| E6 | Crop Progress good+excellent rating vs next-day November soybean price level | next day (report after the close) |  |  | unknown | Nov ZS, weeks 25-40, 1995-2018, 448 reports | none | Bethlem, Lima, Lima (2023), Revista de Economia e Sociologia Rural 61(2) | primary |
| E7 | Dalian soybean first-30-min -> last-30-min momentum (not the vehicle) | last 30 min |  |  | gross | DCE soybean No.1, 2002-07-01..2013-06-27 | n/a | Jin, Kearney, Li, Yang (2020), J. Futures Markets 40(4) 632-650 (MPRA WP 9713... | primary |
| E8 | Chinese soybean complex reacts to USDA reports at the Dalian open (not the vehicle) | minutes |  |  | unknown | Dalian, Jan 2011-Apr 2021 | n/a | Hu and Mallory (2025), J. Futures Markets 45(11) 2109-2127 | secondary-only |
| E9 | CBOT corn real-time USDA release volatility moderates quickly (class row; see ZC) | n/a |  |  | unknown | CBOT corn | n/a | Adjemian and Irwin (2020), J. Commodity Markets 19, 100110 | secondary-only |

Proposed features: 
- `zs_wasde_post_t4`: ratio to D8 2.31, clears 1.5x per reader: False; UPPER BOUND with perfect news sign: /beta_day-beta_30/ x E/news/ = 0.063 x 0.798 x 0.029 = 14.6 bp over ~11:30-13:15; x 57/105 (t4 window, linear drift assumed) = 7.9 bp; at $12.00/bu [unverified assumption] = 0.95 c = 3.80 ticks ($47.5). Bar-only proxy scales by (2p-1), p unknown; 1.5x needs p >...

Unfinished or unverified (reader): 7 items; see product_ZS.md section 6.

### ZL

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum (r_ROD -> r_LH), soybean oil's own row | last 30 min of the day session |  |  | gross | BO (CBOT soybean oil, Tickdata), 1982-07-06..2020-05-01, 9458 obs, ... | none needed: in-sample null; R2 -0.01%, R2_OOS -0.06%. Pooled 'Softs' group (12 ags inc... | Baltussen, Da, Lammers, Martens (2021), JFE 142, 377-403, Table B3 Panel B (o... | primary |
| E2 | Intraday cointegration of the soybean crush (ZS, ZL, ZM) in the day session; stronger o... | n/a |  |  | unknown | ZS, ZL, ZM CME market-by-order data, all of 2015 (243 trading days)... | one year only; no out-of-sample or post-publication test | Zhou, Bagnarosa, Gohin, Pennings, Debie (2023), 'Microstructure and high freq... | primary |
| E3 | Biofuel-policy events (EPA RVO announcements, CARB quarterly reports, Reuters 'sources'... | 1 day (close to close) |  |  | gross | Daily nearby/first-deferred futures from Bloomberg, 2019..2025-02 (... | none; sample is 2021-2025 only (no backward-window evidence; RD/biofuel demand regime) | Avileis and Swanson (2025), 'Drivers of Commodity Volatility in the Biofuel E... | primary |
| E4 | Crush-spread mean reversion driven by intraday deviations from the USDA-implied process... | unknown |  |  | net | 8650 trading days, 1990-09..2021-05 (bar size unknown) | unknown | Abdoh and Chitavi (2025), 'Mean reversion of the soybean crush spread: A new ... | secondary-only |
| E5 | USDA reports and Dalian (DCE) soybean oil futures: minute volatility and volume react a... | n/a |  |  | unknown | DCE soybean no.1, no.2, soybean oil, soybean meal, 2011-01..2021-04... | trade-war period: reduced impact on DCE soybean oil | Hu and Mallory (2022 NCCC-134; published J. Futures Markets 45(11), 2025) | secondary-only |
| E6 | Intraday momentum/reversal on 31 Chinese commodity futures (minute data, includes the D... | intraday |  |  | net | 31 Chinese commodities, minute bars (years not in abstract) | after-cost failure of intraday variants | Yang, Goncu, Pantelous (2018), Int. Review of Financial Analysis 60, 177-196 | secondary-only |

Proposed features: none

Unfinished or unverified (reader): 5 items; see product_ZL.md section 6.

### HE

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum ROD -> LH (rest-of-day return predicts last half hour), lean h... | 30 min (last half hour, 12:35-13:05 CT) |  |  | gross | CME lean hogs (LH), 1981-04-03..2020-05-01, 9,499 days, 1-minute bars | Null in full sample: t 0.06, adjusted R2 -0.01%, R2_OOS -0.06% (no in-sample or OOS pre... | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | primary |
| E2 | Second-to-last half hour -> last half hour (SLH -> LH), lean hogs alone | 30 min (12:35-13:05 CT) |  |  | gross | as E1 | In-sample t 1.76 (10% level only); the joint model's R2_OOS is -0.06% (no OOS value) | Baltussen et al. (2021), Table B3 Panel B, LH row | primary |
| E3 | Next-day direction after a locked-limit day (limit-induced under-reaction), lean hogs | settlement to settlement (includes th... |  |  | unknown | CME lean hogs, first five nearby contracts, 2014-2019, daily (7,264... | none (single 2014-2019 sample; limit days cluster in 2014) | He, X. (2022), Essays on extreme events in agricultural futures markets, PhD ... | primary |
| E4 | Price path after limit moves: locked-limit days gap beyond the limit next day and stay;... | next-day open to +1 hour (locked); sa... |  |  | gross | CME lean hogs and live cattle, first five nearby, 2014-2019, intraday | none | He (2022) dissertation, ch.3 section on Figure 3.1 | primary |
| E5 | Flash events (large intraday moves) in lean hogs: no reversal documented; moves read as... | n/a (liquidity study) |  |  | unknown | CME lean hogs and corn, 2014-2019, limit order book, 1,253 non-anno... | n/a | He (2022) dissertation ch.2 (= He, Serra, Garcia, AJAE 103(2) 2021, 743-764, ... | primary |
| E6 | Hog report window: NASS Quarterly Hogs and Pigs release time (after HE's 13:05 CT close... | n/a |  |  | unknown | n/a | n/a | USDA NASS notice, Dec. 10, 2018 (ESMIS) | primary |
| E7 | Hog report window: USDA LMR swine report statutory deadlines inside the HE session | n/a |  |  | unknown | n/a | n/a | 7 U.S.C. 1635j (US Code 2024 edition, govinfo) | primary |
| E8 | Limit events lead to persistent price changes (commodity futures, multi-market) |  |  |  | unknown | not read | not read | Janardanan, Qiao, Rouwenhorst (2019), On commodity price limits, J. Futures M... | secondary-only |

Proposed features: none

Unfinished or unverified (reader): 8 items; see product_HE.md section 6.

### LE

| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | LC rest-of-day -> last half-hour momentum (null) | 30 min (12:35-13:05) |  |  | gross | LC 1984-08-14..2020-05-01, 8797 days, 1-min Tickdata | Fig.4(c) 2006-06..2020-05 NW t: LC 0.3, LH -0.6, FC -1.6 | Baltussen, Da, Lammers, Martens (2021) JFE 142:377-403, Table B3 Panel B | primary |
| E2 | LC second-to-last half hour (SLH) -> last half hour | 30 min | 1.5 | 0.72 | gross | as E1 | none per contract | Baltussen et al. (2021) Table B3 Panel B | primary |
| E3 | Commodity-class ROD -> LH momentum (LC in 'Softs') | 30 min | 1.7 | 0.8 | gross | 21 commodity futures 1974-2020 | Table 5 commodity beta_ROD 1.59 (t 3.92) 1974-1999 vs 1.04 (t 2.86) 2000-2020; Softs gr... | Baltussen et al. (2021) Tables 2, 5, 6, B3 | primary |
| E4 | Price-limit continuation next day (LC) | 1 day close-to-close (includes overni... | 36.0 | 16.9 | gross | 9 ag/livestock futures (WP; 12 in JFM), Bloomberg daily 1991-01-07.... | no OOS or post-2016 test; WP Table 3 LC: options-implied return forecasts close-to-open... | Janardanan, Qiao, Rouwenhorst, 'On commodity price limits', WP Feb 2017 (Tabl... | primary |
| E5 | Cattle on Feed surprise reaction (next trading day) | 1 day close-to-close | 11.0 | 5.2 | gross | LC 1977-2016, AR(5)-GARCH(1,1) | report-day variance ratio 1.08 (p 0.43) 2000-2016 vs 1.62 (p 0.00) 1977-1999 | Karali, Isengildina-Massa, Irwin (2019) JARE 44(3):591-604 | primary |
| E6 | USDA livestock report-day volatility (decay) | 1 day close-to-close |  |  | unknown | 1970-2016 | COF on cattle volatility 0.205 (1985-1994) -> 0.097 (2007-2016); H&P 2007-2016 n.s. | Isengildina-Massa, Karali, Irwin, Adjemian (2016) NCCC-134 | primary |
| E7 | Intraday behaviour around LE/HE limit moves | intraday |  |  | unknown | LE, HE intraday futures and options 2014-2019 | n/a | He and Serra (2022) AJAE 104(5):1724-1746 (closed) | secondary-only |
| E8 | Lean hog limit-up: price exceeds limit within 3 days (trade press) | 3 days |  |  | unknown | unknown | unknown | Technical Traders article citing Moore Research | unverified |

Proposed features: none

Unfinished or unverified (reader): 8 items; see product_LE.md section 6.

