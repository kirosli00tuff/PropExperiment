# E.20 backward window: the 2010-2019 swap table (PR-1) and calendar-only row losses (PR-15)

BackwardTables-OpusXHigh, 2026-10-11 16:35 PDT. Inputs read: plan review findings PR-1, PR-12 and
PR-15; plan sections 2, 5 and 10; c1_replication/context.py and tables.py; base_rules/auctions.py,
calendars.py and costs.py; the frozen readers named below. Only calendars, code and report files
were read. No data store, parquet, dbn or GEX file was opened. No existing file was edited. Every
check below ran in a scratch process; module attributes were swapped in memory there, as C1's
context does, and nothing was written back. Machine-readable copy:
reports/stage_e20_briefs/backward_swap_table.json (`swap_rows`, `feature_verdicts`, `task2`,
`task1_raw`).

"Overlap" means 2019-05-01..2019-05-31. The hist calendars and the E.14 files cover that month,
and so do the frozen 2019-on tables. For the auctions the overlap is 2019-05-01..2019-06-30.

## 1. Sources on disk

| id | path | sha256 | schema | first..last | grade / provenance |
|---|---|---|---|---|---|
| HIST_CAL | data/calendars/hist2010/{equity,rates,fx,energy,metals,grains}.json | b12aee43..., 099ac84e..., 463c256b..., c7a58e90..., 7eb64ead..., 1197496f... (full hashes in JSON) | e14_hist_calendar/1 (data.hist_calendar -> HistGroupCalendar) | 2010-06-01..2019-05-31 | E.14; pinned by C1 (stage_e14_c1_freeze_inputs.json) and the E.16 freeze; byte-equal to reports/stage_e14_cal_<group>.json |
| HIST_LIVESTOCK | reports/stage_e16_calendars/hist2010_livestock.json (byte copy: data/calendars/hist2010/livestock.json) | 802a4dd98a71776af58748c43c2a70772a966a2e37dd08e32fef1ebfe023ba5d | e14_hist_calendar/1 | 2010-06-01..2019-05-31 | E.16 Task 3b; E.16 freeze pin; 25 unsourced dates, 295 scheduled late opens |
| E14_RELEASES | reports/stage_e14_cal_releases.json | 9a051211fe381cd2d1894180259624cc6729e8ddc89649e398b59e13666080a7 | e14_release_calendar/1 (E.2b row format) | 2010-06-01..2019-05-31; WPSR 470 rows (2010-06-03..2019-05-30), NGS 470 rows (same span), FOMC 72 rows (2010-06-23..2019-05-01) | all rows "official". WPSR-2012-11-01 has no instant (listed in unsourced[]). Every NGS row has drop_actual_differs=false. Pinned by C1 and the E.16 freeze |
| E14_ENERGY_FULL | reports/stage_e14_cal_energy_full_sessions.json | 3f2a273a61613a73867929160d777367e06749b963fcf18b0b27e3f325083d74 | {rule, range, ENERGY_FULL_SESSIONS[]} | 2010-06-01..2019-05-31, 2250 dates | E.14; pinned by C1; c1_replication.tables.parse_full_sessions recomputes it from the rule |
| EC_AUC | reports/stage_e16_calendars/ec_auc_2010_2019.json | e3b5f4522dad8e8dd9ad4a1f4fa04750bab769b089c54ced6f67a01a5a00b9e5 | header e16_ec_auc_hist/1; rows in E.2b TREASURY_AUCTION format plus F-04 fields | 2010-01-12..2019-06-27, 684 rows (2/3/5/7/10/30Y) | all "verified"; from the fiscaldata auctions_query (saved page sha256 b68e0b91...); E.16 R-C4; E.16 freeze pin; 12 of 12 rows equal E.2b on 2019-05..06 |
| E2B_FROZEN | reports/stage_e2b_release_calendar.json | 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8 | frozen D8 calendar | 2019-05-01..2026-06-21 | the source of the 2019-on tables |

## 2. Swap table (one row per table or attribute)

| id | module.attribute (file:line) | read by | frozen coverage | 2010-2019 source | schema match | derivation and overlap check | mechanism | verdict |
|---|---|---|---|---|---|---|---|---|
| S1 | data.group_session.load_group_calendar (data/group_session.py:197) and ml_route.inputs._group_calendar (ml_route/inputs.py:228-232, lru_cache) | the clock (clock.session_group :91-102; clock._day_times :132-136 -> inputs.day_times :249-262); _daily halts and intervals (sigma_X,d, CP3, G5, G8, G9, G1-G3 in_session); generic._previous_trade_day (G5, rod_ret); G16; synthetic.training_calendar (the B1 calendar); roll blackout | 2019-05-01..2026-06-19 | HIST_CAL (six groups) + HIST_LIVESTOCK | yes (subclass of GroupCalendar) | Two additions to C1's patch, both checked in this session. (a) **metals**: the hist file's `subgroup_of_product` is empty, so under C1's swap `clock.session_group("MGC")` raises `ClockError: MGC: no metals sub-group`. The ports call session_group for every vehicle, so the failure is not limited to the clock. Fix without editing a file: give the hist metals calendar the frozen calendar's map, via `dataclasses.replace(hist_metals, subgroup_of_product=frozen_map)` (GC and MGC map to gold). (b) **livestock**: C1's loader raises `HistCalendarError: no hist calendar for group 'livestock'`. Add the livestock HistGroupCalendar (data.hist_calendar, harness v12 group). With both additions the frozen `decision_rows` forms rows for every group: ZC 2011-03-01 10:00/10:30/11:00; LE 2015-03-03 08:30/09:30/11:00; MGC 07:50/10:20/12:50 | setattr on both names, caches cleared (C1 PATCHES 1, CACHE_MODULES) | NEEDS-DERIVATION (the two additions) |
| S2 | rules.sessions._DEFAULT, _DEFAULT_LATE (rules/sessions.py:261-276; day_rule :297, flatten_time_ct :327) | the clock's F_X; the S4 rule | 2019-05-01 on | HIST_CAL and HIST_LIVESTOCK holidays and scheduled late opens | yes | C1's dicts hold six groups. day_rule indexes `default_holidays()[group]`, so HE and LE need a livestock key | setattr (C1 PATCHES 2) plus the livestock key | NEEDS-DERIVATION (livestock key) |
| S3 | rules.sessions.TOPSTEP_HOLIDAYS, TOPSTEP_EARLY_CLOSE_LEAD (rules/sessions.py:100, :210) | the clock's F_X for every group (a Topstep row applies to all groups) | rows and leads from 2019 | c1_replication.tables.h1_rows(hist equity): 95 Rule H-1 rows before 2019-05-01, none overlapping the frozen rows; 30-minute lead for 2010-2018 (L-E5-2 as in C1) | yes | C1's own | setattr (C1 PATCHES 3) | SWAP-READY (C1) |
| S4 | strategy.members.k1._calendar.EQUITY_FULL_SESSIONS (_calendar.py:420; read by an import inside signals/k1.py:56-59) | k1_vwap_dist (MNQ rows off the list are not applicable) | 1779 dates, 2019-05-01..2026-06-18 | derived from HIST_CAL equity under S2+S3 | yes once derived | Rule from reports/stage_e7_briefs/gen_k1_tables.py equity_tables(), lines 138-150: an equity trade date with early_halt_ct None AND flatten_time_ct = 15:08 (one F for MNQ, M2K and MYM). Run on the hist calendar under C1's swap: 2247 dates 2010-06-01..2019-05-31, 2203 of them in 2010-07-01..2019-04-30. The two tests disagree on 0 dates. **Overlap: 22 = 22 dates, equal** | setattr | NEEDS-DERIVATION (rule verified) |
| S5 | strategy.members.k2._releases.TREASURY_AUCTIONS (_releases.py:24; read by an import inside signals/k2.py:61-74). AUCTION_TENOR (_event_common.py:43) is date-independent: no swap | k2_auction_mto, k2_auction_msince (six rates vehicles) | 340 rows, 2019-05-08..2026-06-11 | EC_AUC | no as stored; yes after the frozen transform | reports/stage_e3_briefs/gen_k2_releases.py `build()`: every row whose id ends -2Y/-5Y/-10Y/-30Y, with T_a = the instant in CT. Result: 447 rows 2010-01-13..2019-06-26. In 2010-07-01..2019-04-30: 2Y 97, 5Y 107, 10Y 106, 30Y 106. T_a 12:00 CT (433) or 10:30 CT (14). **Overlap 2019-05..06: 7 rows, equal.** The tenor convention is the frozen one, shared with E.2b: tenor comes from original_security_term, so a cross-tenor reopening keeps its old tenor. In the window this puts 9 two-year auctions under 5Y (6) or 7Y (3), and 5 five-year auctions under 7Y. The frozen 2019-05-28 five-year row carries the same 7Y label. Under the frozen rule, ZT therefore lacks 9 events, and ZF has 6 two-year events and lacks 5 five-year ones | setattr (hist rows before 2019-05-01 + frozen rows) | NEEDS-DERIVATION (format transform by the frozen generator; verified) |
| S6 | strategy.members.k2.monthend.EVENT_DATES (monthend.py:49, from _month_end.py:26 MONTH_END; read by an import inside signals/k2.py:90-95) | k2_monthend_msince. **Missing from the plan review's list of eleven**: it is also a literal starting 2019-05 | 85 months, 2019-05..2026-05 | derived from HIST_CAL rates | yes once derived (frozenset of date) | reports/stage_e3_briefs/gen_k2_month_end.py `month_end_rows()`, run unchanged with its calendar bound to hist rates: 108 months 2010-06..2019-05, 212 event dates in the window. **Overlap (2019-05 row): equal.** 11 event dates are early-halt trade dates, listed as in the frozen convention; the clock excludes those dates anyway | setattr (hist set and frozen set) | NEEDS-DERIVATION (rule verified) |
| S7 | strategy.members.k4.eiafade.make_mcl. The EiaFade.wpsr default is bound at import (eiafade.py:81; make_mcl :137-138; WPSR k4/_releases.py:88; read at signals/k4.py:80-97) | k4_eiafade_move (MCL) | 369 rows, 2019-05-01..2026-06-17 | E14_RELEASES WPSR rows | no as stored; yes after the frozen transform: (date, T_W "HH:MM" CT, weekday, standard) | reports/stage_e4_briefs/gen_k4_releases.py `wpsr_rows()` on the E.14 rows, without WPSR-2012-11-01 (the frozen function cannot place a row with no instant). Result: 469 rows 2010-06-03..2019-05-30, 398 standard, T_W 09:30 (399) or 10:00 (70). All 469 pass release_minutes' T_W + 15 <= 13:13 (459 of them in the window). **Overlap: 5 rows, equal.** No drops: the frozen 2019-2024 rows had no WPSR drop check either (DROPPED_WPSR covers the research window only) | factory swap, as C1 did for make_ng: `make_mcl = lambda: EiaFade("MCL", wpsr=hist+frozen)` | NEEDS-DERIVATION (frozen rule; verified) |
| S8 | strategy.members.k4.ngpre.make_ng. The NgPre.ngs default is bound at import (ngpre.py:63; make_ng :106-107; NGS k4/_releases.py:277; read at signals/k4.py:118-126) | k4_ngpre_mto, k4_ngpre_msince (NG) | 367 rows, 2019-05-02..2026-06-18 | E14_RELEASES NGS rows via c1_replication.tables.parse_releases | yes | C1's table: 470 rows (no C13 drops), equal to the frozen generator's `ngs_rows()` on the same file. T_N 09:30 (457) or 11:00 (13). **Overlap: 5 rows, equal.** 461 schedule dates in the window | factory swap (C1 PATCHES 4) | SWAP-READY (C1) |
| S9 | k4._calendar.ENERGY_FULL_SESSIONS; k4.ovr ENERGY_FULL_SESSIONS, _FULL_SESSIONS, _FULL_ORDINALS (k4/_calendar.py:24; k4/ovr.py:40, :72-73, reference_dates :76-80; read by signals/k4.py:158-200) | k4_ovr_ret, k4_ovr_pct (MCL, NG) | 1784 dates, 2019-05-01..2026-06-18 | E14_ENERGY_FULL | yes | None needed: the file equals the frozen rule (energy trade dates with early_halt_ct None) on hist energy. **Overlap: 22 dates, equal.** Without the swap, reference_dates() is empty before 2019-05 and k4_ovr_pct is NaN while applicable. Every MCL and NG row at t2..t4 would then be *dropped as missing*, not flagged | setattr x4 (C1 PATCHES 5) | SWAP-READY (C1) |
| S10 | k5.ovr _FULL_SESSIONS, _FULL_ORDINALS, plus METALS_FULL_SESSIONS in k5.ovr and k5._calendar (k5/_calendar.py:24; k5/ovr.py:44, :75-76, reference_dates :97-101; read through signals/k5.py into k4.ovr_frames) | k5_ovr_ret, k5_ovr_pct (MGC) | 1784 dates, 2019-05-01..2026-06-18 | derived from HIST_CAL metals | yes once derived | Rule of reports/stage_e4_briefs/gen_k5_calendar.py `full_sessions()`: metals trade dates with early_halt_ct None. That function asserts 2019-on coverage, so the same expression is applied via c1_replication.tables.full_sessions_rule. Result: 2250 dates 2010-06-01..2019-05-31. **Overlap: 22 = 22, equal.** Without the swap, MGC rows fail the same way as in S9 | setattr x4 (the C1 PATCHES 5 pattern) | NEEDS-DERIVATION (rule verified) |
| S11 | the release calendar *argument* to targets.build_targets(releases=...) (targets.py:223), with _core.release_times/cpi_times (:323-342) and portfolio.release_window_mask (portfolio.py:91) | targets: D9.5a deferral, D8 event-window cost, the release_window filter. No kept feature reads it (G13-G15 and k9 are dropped) | 2019-05-01..2026-06-21 | E14_RELEASES (FOMC, NGS, WPSR) + EC_AUC before 2019-05-01, merged with E2B_FROZEN by base_rules.costs.combine_rows / build_release_rules (E.16) | yes for the rows that exist. All 17 vehicles have FOMC rows, so release_times never raises | Release types with no 2010-2019 rows: NQ CPI/ISM_SERVICES/NFP; RTY ISM_SERVICES/NFP; ZT ZF TN UB NFP; ZN ZB ISM_SERVICES/NFP; 6E NFP; MCL API_WSB; MGC CPI/G17/NFP; ZC CROP/CROP_ANNUAL/CROP_PROGRESS/WASDE; ZS ZL HE LE CROP/CROP_ANNUAL/WASDE. E.16's conservative fallback (ReleaseRules._fallback_hit, by CT clock time) is a method, not ReleaseCalendar rows, so the frozen targets code cannot read it as is. Writing it as rows at every fallback clock time would also fire the deferral and the release_window filter on every pre-2019-05 date at those times | an argument, not a setattr | NEEDS-DERIVATION (lead decision) |
| S12 | D6 day_session_ct (signals/_daily.py:66-71) and the D8 cost tables (targets.py:72) | ports, G5, G8, sigma_X,d, CP3, rod_ret's C, k1 O, k2 monthend anchor, k5 ovr clocks; target costs | date-independent | none needed | n/a | Kept frozen, as C1 did. Mixed with the hist per-date O_X in the clock (PR-12); see Task 2 | none | NO SWAP NEEDED |
| S13 | k2._releases.FOMC_STATEMENT_DATES (:141) | k2_fomc_mto only (dropped, PR-2) | 57 dates from 2019-05-01 | n/a | n/a | n/a | none | NOT NEEDED |

No table needed by a kept feature is NO-SOURCE.

## 3. Per-feature verdicts

| features | tables | verdict |
|---|---|---|
| cp1_ret, cp2_range, cp2_brk, cp3_clv | S1, S2, S3, S12 | SWAP-READY through the calendars once S1's two additions are in. Without the metals map, MGC fails in the ports too. Row losses: section 4 |
| k1_vwap_dist | S4 (+S1-S3) | NEEDS-DERIVATION, rule verified on the overlap |
| k2_auction_mto, k2_auction_msince | S5 | NEEDS-DERIVATION, verified; frozen tenor convention noted |
| k2_monthend_msince | S6 | NEEDS-DERIVATION, verified (not in PR-1's list) |
| k4_eiafade_move | S7 | NEEDS-DERIVATION, verified. One date without a time (2012-11-01) |
| k4_ngpre_mto, k4_ngpre_msince | S8 | SWAP-READY (C1) |
| k4_ovr_ret, k4_ovr_pct | S9 | SWAP-READY (C1) |
| k5_ovr_ret, k5_ovr_pct | S10 | NEEDS-DERIVATION, verified |
| g01..g12, g16_month_end | S1-S3, S12 | SWAP-READY through the calendars (no literal). G5, G8, G9 and sigma_X,d share the grains losses below |
| g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_zc | none | no table |
| rod_ret, rod_absratio | S1, S12 | SWAP-READY through the calendars |

The derivations above were checked on calendars only (the 2019-05 overlap). PR-1 item 3 still
needs its sentinel-frame dry check of the features under the swapped tables; that was not part of
this brief.

## 4. Task 2 (PR-15): decision bars and port inputs the session structure makes absent

Method: for each root's backward window (plan section 2; end 2019-04-30), each trade date of its
hist group calendar is run through the following, using calendars only:
- the frozen clock rule: exclude closures, early halts and early closes; O_X comes from the hist
  calendar's D6 entry for the date; F_X comes from rules.sessions under the swap; t4 = F_X - 60;
- bar presence: a bar is present when its opening minute lies inside data.group_session.session_intervals of that date;
- the decision bar (opening at t - 1) and the entry bar (opening at t);
- the ports' inputs at the frozen D6 O and C: cp1's first bar and its O+29 bar, cp2's
  [O, O+15) range, cp3's O bar and a prior port-complete day, G5's O bar and the previous date's
  C-1 bar, and the sigma_X,d "complete" day.

Roll-blackout exclusions are data-derived and not counted. Shares are of the window's trade dates.

| root | window | trade dates | kept by clock | dates whose rows are all lost (ports/G5 input absent) | share | which decision times | other calendar effects |
|---|---|---|---|---|---|---|---|
| NQ | 2010-07-01 | 2280 | 2203 | 6 | 0.3% | t1-t4 (cp1 missing) | the 6 dates are 2011-12-27, 2012-01-03, 2012-12-26, 2013-01-02, 2013-12-26, 2014-01-02: Globex first open 05:00 CT on d, so there is no 17:00 bar on d-1 |
| RTY | 2017-07-10 | 466 | 451 | 0 | 0% | none | |
| ZT, ZF, ZN, ZB, UB (each) | 2010-07-01 | 2279 | 2182 | 313 (307 before 2011-10-03 + the same 6 dates) | 13.7% (14.3% of kept) | t1-t4 (cp1 missing) | before 2011-10-03 Globex opened at 17:30 CT, so cp1's 17:00 first bar does not exist |
| TN | 2016-01-11 | 851 | 827 | 0 | 0% | none | |
| 6E | 2010-07-01 | 2280 | 2182 | 6 (same dates) | 0.3% | t1-t4 | |
| CL (MCL), NG, GC (MGC) | 2010-07-01 | 2278 | 2203 | 0 | 0% | none | |
| ZC, ZS, ZL (each) | 2010-07-01 | 2225 | 2199 | 477 (473 before 2012-05-21, 3 late-open dates in 2012-05-21..2013-04-07, and 2012-05-21 itself for cp3) | 21.4% (21.7% of kept) | t1-t4 (no 08:30 bar: cp1, cp2, cp3, G5 and sigma_X,d all absent) | (a) **warm-up extension**: sigma_X,d needs 20 complete dates after 2012-05-21 (2012-06-19), and G9 needs 120 consecutive sigma values (first value about 2012-12-11). So rows are lost until about 2012-12-11, roughly 615 dates (about 27.6%); an estimate from the rule, which the dry check must count. (b) **clock shift**: hist O_X is 09:30 before 2013-04-08 (689 dates, 31.0%), so t1/t2 are 10:00/10:30 instead of 09:00/10:00 (t3 11:00 and t4 12:18 unchanged); 216 kept dates in 2012-05-21..2013-04-07 keep their rows at the shifted times. (c) **F bar absent**: the session closed at 13:15 before 2012-05-21 and in 2013-04-08..2015-07-05, but F_X stays 13:18 (REGULAR_FLATTEN_CT). The bar at F (hF's exit on t1-t4, and h60's exit on t4) is absent on 1031 dates (46.3%), 558 of them (25.1%) in the 2013-04-08 era whose rows are otherwise kept |
| HE | 2017-07-01 | 460 | 453 | 0 | 0% | none | 08:30 era only; 4 hist-calendar unsourced dates |
| LE | 2014-12-15 | 1103 | 1086 | 63 (62 Monday or post-holiday 09:05 late opens in the 08:00 era, plus 2017-01-17) | 5.7% | t1-t4 (t1's bar and the 08:30 port inputs absent) | **08:00 era (2014-12-15..2016-02-26, 296 kept dates, 26.8%)**: hist O_X is 08:00, so t1/t2/t3 = 08:30/09:30/11:00 (instead of 09:00/10:00/11:00). At t1 = 08:30 the ports are not yet known (cp1 09:00, cp2 08:45, cp3 08:31): app = 0 with z = 0, and their flag columns are not features (ALWAYS_APPLICABLE), so the model silently sees a not-applicable state. **G5's value is available at 08:31 > t1, so the frozen assert_causal raises CausalityError** unless those t1 rows are removed. 14 unsourced dates |

The 09:05 livestock era (before 2014-10-27) lies outside every window: LE starts 2014-12-15 and
HE starts 2017-07-01. Clock exclusions by the frozen rule (early halts, early closes and closures)
are in the JSON, per root.

## 5. For the lead (not decided here)

1. **S1 metals map and livestock calendar.** Both are needed before any backward clock or port
   call. C1 never hit them because its world was NG only.
2. **LE 08:00 era t1 rows.** The frozen code raises CausalityError on them, and the ports there
   are silently not applicable. Options: drop t1 rows on those 296 dates, drop the era, or drop
   LE from B1. Each is a design choice.
3. **Grains hF and t4-h60 exit bar** on 1031 dates, because F_X = 13:18 falls after a 13:15
   close. Also the shifted grains t1/t2 before 2013-04-08 and the LE 08:00-era clock times: these
   change what t1/t2 mean (G11 and the per-t_index baselines), they do not lose rows.
4. **S11.** How the release types with no 2010-2019 rows enter the frozen targets and portfolio
   path. E.16's fallback is not expressible as ReleaseCalendar rows without also firing the
   deferral and filter every day.
5. **WPSR-2012-11-01 (no time).** Exclude the date as unsourced, as C1's C12 did, or leave it
   eventless.
6. **Hist-calendar unsourced dates** (LE 14, HE 4, other roots 0). The frozen clock does not
   exclude them; C1 did.
7. **Cross-tenor reopenings in S5** follow the frozen labelling convention. They are recorded
   here, not corrected.
