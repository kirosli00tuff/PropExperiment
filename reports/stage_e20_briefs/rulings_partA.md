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
