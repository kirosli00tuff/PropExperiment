# R1Fixer-OpusHigh report (Stage E.32b wave F, section F2: RV2 B1 text part, S6, N2)

Worker: R1Fixer-OpusHigh (worker-high, opus). Started 08:47 PDT, edits 08:50-08:54 PDT, 2026-10-29 (times from `date`).
Read-only on code and other stages' reports. No data file, no Databento, no holdout, no commit.
Backups of the four edited files before any edit: work/fix4/r1/*.before. Scripts: scratchpad r1fix/texts.py,
apply_r1.py, apply_dossiers.py (session scratchpad; the inserted texts are reproduced below).

## 1. Facts checked against the frozen code (file:line, quoted)

Frozen code state: `git log` on ml_route_v2/signals/generic.py and ml_route_v2/constants.py shows only 39738c3 and
9466f2e "ML route v2 freeze" (2026-10-03), before E.12 and E.20. No local changes (git status clean for ml_route_v2,
pattern_search, c1_replication).

F1. G17 definition. ml_route_v2/signals/generic.py:22-25: "G17: the 60-minute log return (x 1e4) of each other
cluster's lead price path and of MES, from the lead's latest bar closed by t and its latest bar at least 60 minutes
before that, both of the row's trade date ... the row's own cluster lead is not applicable." Signals built at
generic.py:390-392: `for lead in (*CLUSTER_LEADS.values(), *SIGNAL_ONLY_ROOTS): g.append(SignalSpec(f"g17_{lead.lower()}", ...`.
Leads: ml_route_v2/constants.py:36-38: `CLUSTER_LEADS = {"K1": "NQ", "K2": "ZN", "K3": "6E", "K4": "CL", "K5": "GC",
"K6": "ZC", "K7": "MBT"}`, `SIGNAL_ONLY_ROOTS = ("MES",)`. Matches RV2.

F2. Own-cluster rule. generic.py:343 `own_cluster = next((k for k, p in CLUSTER_LEADS.items() if p == lead), None)` and
:351-352 `if own_cluster is not None: ok &= view.cluster != own_cluster`. c1_replication/c1b.py:53-54: "leg CL, NG's
own cluster lead (K4), which G17 never applies on its own cluster's rows". Clusters: constants.py:23 `"M2K": ("K1",
"RTY")`; :31 `"ZL": ("K6", "ZL")`. ZS and ZM are K6 members, not leads (constants.py:30), so no g17_zs or g17_zm exists.
Matches RV2.

F3. E.12 Gate 0 G17 rows. reports/stage_e12_gate0.md:158-164 rows gate0A_g17_nq_h60, _zn_, _6e_, _cl_, _gc_, _zc_,
_mbt_h60; :222-228 the same seven at h120; :286-292 at hF. Family A is "one test per (signal, horizon), pooled over
products" (ml_route_v2/gate0.py:3); Gate 0 has 64 distinct gate0A signals (count of distinct `gate0A_*_h60` names = 64).
Family B: gate0.py:11-12 "ridge at GATE0_RIDGE_LAMBDA on all features, pooled across products, one model per horizon",
tested per (root, horizon).
**Disagreements with RV2 (not written as RV2 stated them):**
- RV2 and the brief say "E.12 also MES, MBT". g17_mes was NOT in E.12: reports/stage_e12_rulings.md:49 "MES store
  refused by the frozen loader at the build (TradeDateMismatch, 3 rows) | Pre-registered lead rule P-1a applied as
  frozen: g17_mes, k8_flight_ret, k8_flight_tail excluded; 64 signals covered." Gate 0 has no g17_mes row. E.12's
  G17 set is NQ, ZN, 6E, CL, GC, ZC, MBT. Written as "E.12 also MBT; g17_mes excluded by P-1a".
- MBT's E.12 store starts 2024-01-02 (reports/stage_e12_phase1_bars.json roots.MBT.s_x, read by script), so g17_mbt
  was live on M2K and ZL rows only 2024-01-02..2024-02-29 (two months of the window). Added as a qualifier.
- RV2 says "inside Family B's per-product models". The code has one ridge per horizon pooled across products (the
  per-product part is the test, not the model). Written as "inputs of Family B's pooled ridge".
- E.12 live leads therefore: on M2K ZN, 6E, CL, GC, ZC (plus MBT from 2024-01-02); on ZL NQ, ZN, 6E, CL, GC (plus MBT
  from 2024-01-02). RV2's lists are the E.20 lists; they hold for E.12 apart from MBT.

F4. E.20 frozen features. pattern_search/constants.py:59 `"g17_nq", "g17_zn", "g17_6e", "g17_cl", "g17_gc", "g17_zc",`
(in KEPT_SIGNALS); :66 `FEATURE_NAMES = (*KEPT_SIGNALS, *ROD_SIGNALS, *ACCEPTED_PART_A)  # 36`.
reports/stage_e20_search_freeze.json, key feature_names only (script): 36 names, the six g17 names at positions 29-34,
then rod_ret, rod_absratio. Computed by the frozen code: pattern_search/panel.py:64 `from ml_route_v2.panel import
assert_window, build_panel`, :75 `panel = build_panel(ctx, targets, mode="train", signals=tuple(signals))`.
g17_mbt and g17_mes dropped by the leg rule (reports/stage_e20_plan.md:138). Universe: pattern_search/constants.py:17-23
(`"M2K": "RTY"` in K1; `"ZL": "ZL"` in K6). "One pooled model per horizon over the 17 vehicles"
(stage_e20_plan.md:28). Live on RTY (vehicle M2K, K1): ZN, 6E, CL, GC, ZC; on ZL (K6): NQ, ZN, 6E, CL, GC. Matches RV2.

F5. E.20 clock, horizons, window. t1-t3: stage_e20_plan.md:78 "t1, t2, t3: the frozen V2.2 rule (clock.decision_rows)";
ml_route_v2/constants.py:50 `"equity": (time(9, 0), time(11, 0), time(13, 0))`, :57 `"grains": (time(9, 0), time(10, 0),
time(11, 0))`. t4: stage_e20_plan.md:81-82 "t4 = F_X - 60 min ...: 14:08 CT for equity, rates, FX, energy and gold;
12:18 for grains". Horizons: ml_route_v2/constants.py:44 `HORIZONS = ("h60", "h120", "hF")`; plan:228 "horizon h60,
h120, hF". Window: pattern_search/constants.py:30-31 SEARCH_FIRST 2019-05-06, SEARCH_LAST 2024-02-29. Matches RV2;
addition: ZL's t4 is 12:18 CT, not 14:08 (RV2 gives only the equity value).

F6. N2 (E.29). reports/E.29_RETURN.md:134-148 section 3.2 table: pairs CL-ZM, CL-GC, CL-NQ, ZM-GC, ZM-NQ, GC-NQ only.
No YM-MNQ, YM-RTY, MNQ-RTY (nor MYM pairs). R2_combinations.json top-level rho_measured = {} (script). Pools in the
dossiers: only EQ3 [YM, MNQ, RTY] and EQ3m [MYM, MNQ, RTY]. Spec rule: reports/stage_e32b_ranking_spec.md:325-326
"rho from E.29 section 3.2's measured correlations where they exist, else 0.5 within an asset class" (section 8.3,
which starts at spec line 298). Matches RV2.

F7. R2_combinations.json (read-only, script): C112-C116 and C138-C139 each carry Q3 (value 1, reason "LR-Q3b: ...")
and Q3_rater (value 2, the rater's reason). Confirms the statement written into R2_Q_ratings.md.

## 2. Edits (before / after)

### 2.1 R1_closed_lines.json (sha256 before 874618368b9ad43b...)
Round-trip check first: `json.dumps(d, indent=1, ensure_ascii=True)` reproduces the file byte for byte, so the only
diff is the new field. Added one field `cross_market_features` at the end of lines R1-11 (file line 2217) and R1-15
(line 2578); diff shows only `]` -> `],` plus the new line in each. No existing value changed. After: the file loads;
sum of n_trials 838, n_total 838, sum of trials_by_line 838.
Values: "[added 2026-10-29 (session 4, RV2 B1/S6)] " followed by the R1-11 and R1-15 texts in 2.2.

### 2.2 R1_closed_lines.md
Before: R1-11 (lines 77-83) and R1-15 (104-110) as written by ClosedLines-SonnetHigh, no cross-market content.
After: one bullet inserted after each line's `- notes:` bullet (new lines 84 and 112):

R1-11: "- cross-market [added 2026-10-29 (session 4, RV2 B1/S6)]: includes G17: 60-minute log returns (x 1e4) of the
other clusters' lead prices, g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_zc and (E.12 only) g17_mbt
(ml_route_v2/signals/generic.py:22-25, 390-392; leads ml_route_v2/constants.py:36-37), never applied on the product's
own cluster (generic.py:343, 351-352; c1_replication/c1b.py:53-54). g17_mes is defined but was excluded in E.12 by rule
P-1a (MES store refused; reports/stage_e12_rulings.md:49), and MBT's E.12 store starts 2024-01-02
(reports/stage_e12_phase1_bars.json roots.MBT.s_x), so g17_mbt was live only 2024-01-02..2024-02-29. Tested pooled over
the 27 products in Family A at h60, h120, hF (reports/stage_e12_gate0.md:158-164, 222-228, 286-292, rows gate0A_g17_*)
and as inputs of Family B's ridge (all features, one model per horizon pooled across products, tested per product and
horizon; ml_route_v2/gate0.py:11-12); decision times t1-t3 (equity 09:00, 11:00, 13:00 CT; grains 09:00, 10:00, 11:00;
ml_route_v2/constants.py:50, 57). Live on M2K (cluster K1, own lead NQ excluded; constants.py:23): ZN, 6E, CL, GC, ZC
(MBT from 2024-01-02). Live on ZL (cluster K6, own lead ZC excluded; constants.py:31): NQ, ZN, 6E, CL, GC (MBT from
2024-01-02); ZS and ZM are not G17 leads."

R1-15: "- cross-market [added 2026-10-29 (session 4, RV2 B1/S6)]: includes G17: 60-minute log returns (x 1e4) of the
other clusters' lead prices, g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_zc, six of the 36 frozen features
(pattern_search/constants.py:59, 66; reports/stage_e20_search_freeze.json feature_names), computed by the frozen
ml_route_v2 code (pattern_search/panel.py:64, 75; ml_route_v2/signals/generic.py:22-25, 343, 351-352), so never applied
on the product's own cluster; g17_mbt and g17_mes dropped by the leg rule (reports/stage_e20_plan.md:138). One pooled
model per horizon over the 17 vehicles (stage_e20_plan.md:28) at h60, h120, hF, 2019-05-06..2024-02-29
(pattern_search/constants.py:30-31); decision times t1-t3 (equity 09:00, 11:00, 13:00 CT; grains 09:00, 10:00, 11:00;
ml_route_v2/constants.py:50, 57) and t4 = F_X - 60 min (14:08 CT equity, 12:18 CT grains; stage_e20_plan.md:81-82).
Live on RTY (vehicle M2K, cluster K1): ZN, 6E, CL, GC, ZC (not NQ). Live on ZL (cluster K6): NQ, ZN, 6E, CL, GC (not
ZC; ZS and ZM are not G17 leads)."

Deviation from the brief's suggested wording: "E.12 also MES, MBT" became "E.12 also MBT; g17_mes excluded by P-1a"
(fact F3).

### 2.3 R2_dossiers.md (sha256 before 058e0608337f03df...)
- Errata: after the session 3 block's item 3 (line 13), inserted a session 4 errata block (28 lines, now lines 14-41):
  header "Lead errata (session 4, 2026-10-29 08:53 PDT; R1Fixer-OpusHigh for RV2 B1, S6 and N2 ...)" and items
  4 (R1-11/R1-15 G17 fact, live leads, file refs; notes that the per-dossier R1-11/R1-15 lines and the RTY|F09 and
  ZL|F09 R1 overlap lists at lines 1242 and 1571 omit it), 5 (RTY|F09 Q3 reason wrong; LR-Q3b Q3 = 1 for C112-C116 and
  C138-C139; leg-level reading Q3 = 2 is the sensitivity), 6 (N2: E.29 3.2 measured only the CL, ZM, GC, NQ pairs;
  pools use the default rho 0.5 within the class, spec 8.3; rho_measured = {}), 7 (R2_dossiers_for_rating.md kept
  exactly as rated). The session 3 header text ("the dossiers below are unchanged") is not edited.
- Catalog rows: the R1-11 row (now line 2466) and R1-15 row (now line 2469) each end with
  " [corrected s4: see errata] Cross-market content: " plus the R1-11 / R1-15 text of 2.2. Nothing else in the rows
  changed.
- N2 wording: this file has no sentence saying "E.29 measured no correlation" (grep for measured no / correl / rho /
  K_eff). Line 71 ("correlation barely mattered in the basket model") is a different statement and is unchanged. So
  item 6 adds the fact; no existing sentence needed rewording.
- R2_dossiers_for_rating.md untouched (sha256 dc7db33e1b71bb09... before and after).

### 2.4 R2_Q_ratings.md (sha256 before 6ec296008bdfd22d...)
Inserted an 11-line block (10 quoted lines and a blank) after the H1 title line, before the "Rater:" line: "Lead errata
(session 4, 2026-10-29 08:53 PDT; ...; no rating line below is changed)": the rater's RTY|F09 and ZL|F09 Q3 lines are
kept as written (Q3 = 2); LR-Q3b replaced the value with 1 for C112-C116 and C138-C139 (reason as in RULINGS.md:86-91);
the RTY|F09 reason "no cross-market configuration closed on RTY or M2K" is wrong as a fact; R2_combinations.json
carries Q3 (1) and Q3_rater (2). The diff has 0 removed lines. "Prepend" was read as "first block under the title".

## 3. Step 5: other places with the same incomplete statements (listed, not edited)

reports/stage_e32b_recommendations.md
- :46 R1 table row R1-11: "ML route v2 Gate 0: Family A (64 generic signals x 3 horizons = 192 tests) and Family B
  (27..." (no cross-market content; truncated family column).
- :50 R1 table row R1-15: "E.20 Part C ML pattern search: ridge and shallow LightGBM, 45 configurations, extra
  decision..." (same).
- :465 ZL table, Q3 row, ZL F09 column: `2: "Family overlap: R1-21 S1 crush residual and S2 propagation closed on ZM
  with ZL as an input leg ...; R1-08 K6-crushgap-01 on ZS; trading ZL on the same residual is the mirror leg (1 if read
  as a close variant)."` (rater's Q3 2, no R1-11/R1-15; LR-Q3b value is 1). Same row, ZL F10 column: "R1-11 ZL
  bar-feature ML (other family)".
- :485 "- ZL in other families' closed lines: R1-08 CP ports (ZL F01 gated at Q3 0), R1-11, R1-13, R1-15, R1-16."
  (under LR-Q3b R1-11 and R1-15 count as F09's own family on ZL; lead's call whether this wording changes).
- :568 RTY table, Q3 row: `2: "Family overlap only: R1-10 K8 cross-market (MGC, 6C, MNQ legs), R1-13 E16-H2 NQ vs ZN
  pair and R1-21 S1/S2 on ZM; no cross-market configuration closed on RTY or M2K."`
- :580 "Closed-line overlap: no cross-market configuration on RTY or M2K."
- :582-583 "R1-11 (M2K Gate 0)" and "R1-15 (RTY searched, E.20's 36 late-session features)" ("late-session" is also
  inaccurate: t1-t3 are 09:00, 11:00, 13:00 CT and t4 14:08 CT on equity).
- :120 "no measured correlation among members, so rho 0.5 within the class per spec 8.3; E.29 section 3.2 measured only
  CL-ZM, CL-GC, CL-NQ, ZM-GC, ZM-NQ, GC-NQ" — correct as written (says the pairs were not measured); listed only
  because it matches the N2 search.

reports/stage_e32b_briefs/work/R4/draft_sections.md
- :187 ZL Q3 row, F09 column: same rater quote as recommendations :465 (and "R1-11 ZL bar-feature ML (other family)" in
  the F10 column).
- :207 "- ZL in other families' closed lines: R1-08 CP ports (ZL F01 gated at Q3 0), R1-11, R1-13, R1-15, R1-16."
- :304 RTY Q3 row: same quote as recommendations :568 ("no cross-market configuration closed on RTY or M2K").
- :316 "Closed-line overlap: no cross-market configuration on RTY or M2K."
- :318-319 "R1-11 (M2K Gate 0)", "R1-15 (RTY searched, E.20's 36 late-session features)".

reports/stage_e32b_ranking.md: no hit (patterns: R1-11, R1-15, bar features, 64-feature, 36 features, r_ROD features,
no cross-market, cross-market config, measured no correlation, E.29, correlat, rho).
reports/stage_e32b_holding_scope.md: no hit for the same patterns (its only E.29 line, :1316, is on payout reachability).

Also found (outside the step-5 file list, not edited):
- reports/stage_e32b_STATE.md:447 (D1-done row): "E.29 measured no correlation between members" (RV2 N2's source).
- R2_dossiers.md per-dossier lines describing R1-11/R1-15 without G17 (covered by errata item 4, not edited), current
  lines 149, 353, 404, 697, 699, 897, 946, 947, 1047, 1049, 1294, 1343, 1344, 1443, 1445, 1617, 1659, 1660 (18 lines;
  for example 1343 "R1-11 (M2K tested): Gate 0 ML over 64 bar features at h60, h120, hF" and 1344 "R1-15 (this product
  (RTY searched)): E20S ML, 36 bar features, h60/h120/hF").
- R2_dossiers_for_rating.md:797-798, 995-996 (RV2's locations) are kept as rated by instruction.

## 4. Not done / open for the lead
- The JSON field and md bullets use the verified wording, not the brief's literal "E.12 also MES, MBT" (F3).
- RULINGS.md LR-Q3b and the R2_combinations.json Q3 reason say the leads are "NQ, ZN, 6E, CL, GC, ZC" for both studies;
  E.12 also had MBT (two months). Not wrong for the ruling; files are outside my write list.
- Whether recommendations :485 / draft :207 ("other families") should change under LR-Q3b is a lead call.
