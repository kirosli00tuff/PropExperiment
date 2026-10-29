# R1 closed lines (Stage E.32b, spec section 8.1) - extraction by ClosedLines-SonnetHigh, 2026-10-28 23:28:02 PDT
Full fields (members, all quotes) in R1_closed_lines.json. Facts only; no judgment on overlap. Times PDT. N = 838 (ledger).

## Ledger ladder (ledger/trial_registrations.jsonl; the file has no family/product/window fields, only ids, freeze files, N)
baseline 471 (198 screened + 273 Gate 0); r001-C1 +2 -> 473; r002-E16 +5 -> 478; r003-C1b +2 -> 480; r004-E20H6 +3 -> 483; r005-E20S +45 -> 528; r006-E21 +4 -> 532; r007-E22 +1 -> 533; r008-E23 +5 -> 538; r009-E33 +300 -> 838. Pre-ledger parts: D.1-D.1f 58, K clusters 140, Gate 0 273.
Trials per line: R1-01 58, R1-03 11, R1-04 44, R1-05 27, R1-06 12, R1-07 9, R1-08 27, R1-09 6, R1-10 4, R1-11 273, R1-12 4, R1-13 5, R1-14 3, R1-15 45, R1-16 4, R1-17 1, R1-18 5, R1-21 300 (sum 838; R1-02, 19, 20, 22, 23 add no trials).

## Closed lines (23; types: intraday_screen_confirm 1, passive_execution 1, intraday_screen 8, ml_search 2, replication 1, base_rule_batch 1, intraday_test 1, multiday 2, forward_registered_parked 1, intraday_closure_umbrella 1, passive_execution_measured 1, directional_search 1, product_decision 1, closed_directions_no_trials 1)
### R1-01 [intraday_screen_confirm] MES intraday program (Stage D.1, D.1a, D.1b, D.1d, D.1e, D.1f): 58 Tier A tests in 7 classes C1-C7; families A calendar/clock windows, B opening-range and breakout, C reversal and fade, D vol-regime gates and gaps, E scheduled-macro and calendar, F data-native, G bucket/price-path statistics, H NR4/NR7/inside-day ORB and prior-close follow-through
- products: MES (traded)
- horizons: from 5 minutes to the session close (A-H2 30 min; A-H1 about 60 min; B-H1 hold 5 and 75; D.1d sweep at 5/15/30/60-minute bars) | data: ohlcv-1m MES (docs/STAGES.md:8,48); D.1d sweep at 5/15/30/60-minute bars (STAGES:38-43) | windows: screens D.1/D.1a/D.1b/D.1d/D.1e: research window 2025-04-01..2026-05-13 (289 train-union dates) ; D.1f confirmation 2020-02-03..2024-02-29 (S = 2020-02-03, 1,055 window days); Family H never read before D.1f ; holdout-2 2024-04-01..2025-03-31 sealed (docs/STAGES.md:44-47)
- registrations: none | trials 58 | N 31 after D.1d (STAGES:41-42); N 58 after D.1f (+21 event statistics +6 Family H); pre-ledger; baseline 471 includes them. D.1f class counts of the 58: C1 6, C2 19, C3 16, C4 6, C5 4, C6 1, C7 6 (inventory CDE.json)
- closing: V38/V40 (programme level); D.1f verdict in STAGES, docs/STAGES.md:55: "no member passed confirmation (Holm rejects none of 58); C1–C5 and C7 null under docs/NULL_CRITERIA.md (C5 null by inactivity via E-H3), C6 awaits D.1g; independently verified with no discrepancy; N = 58."
- exceptions: MES enters later only as a leg (STAGES:65: "MES is closed and enters only as a leg")
- notes: all 7 D.1d re-tests at the source grid failed; the 28-statistic 5/15/30/60-minute sweep admitted zero hypotheses (STAGES:38-43)
- members: 58 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-02 [passive_execution] C6 passive execution (C-H4 reversal with resting limit orders); Stage D.1g not run
- products: MES (traded)
- horizons: n/a (reversal, passive fill) | data: would have bought 181 full trade-date MBO days; not bought | windows: none read
- registrations: none | trials 0 | C-H4 is inside R1-01 counts; D.1g not run, no C6 null statement exists
- closing: user decision 2026-09-23 ("C6 closed, Stage D.1g not run"), docs/DECISIONS.md:30-34: "C6, passive execution (C-H4's resting limit orders), is closed as non-deployable on the XFA, and Stage D.1g (a queue-position fill model on 181 purchased MBO days) will not run."
- notes: STAGES:56-60: "A scope decision, not a null: no C6 null statement exists."
### R1-03 [intraday_screen] K1 equity-index screen: CP1 open-to-first-half-hour momentum port, CP2 opening-range breakout, CP3 prior-day close-location, VXN band fade, VWAP stop-and-reverse
- products: MNQ (traded), M2K (traded), MYM (traded), NQ (price path/W_ext), RTY (price path/W_ext), YM (price path)
- horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members | data: 1-minute step bars (Stage E harness; bar-based) | windows: E.7 screen: research window 2025-04-01..2026-06-12, 299 trade dates ; all eleven Tier B, Tier A empty; no confirmation run
- registrations: none | trials 11 | counted in N 198 (STAGES ladder); 5 members, 11 trials on MNQ, M2K, MYM (STAGES:105-107)
- closing: V40 (and V38), docs/DECISIONS.md:728-729: "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read."
- notes: K1-cp3-01 MNQ Tier B rests on four MLL-liquidated days (STAGES:106)
- members: 5 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-04 [intraday_screen] K2 rates screen: CP1/CP2/CP3 ports, pre/post Treasury-auction windows, post-FOMC, ISM pre-drift, month-end
- products: ZT (traded), ZF (traded), ZN (traded), TN (traded), ZB (traded), UB (traded)
- horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members | data: 1-minute step bars (Stage E harness; bar-based) | windows: E.3 screen: research window 2025-04-01..2026-06-17, 299 trade dates (15 roll-blackout, 2 UR-1 removed) ; all 44 Tier B; K2 confirmation never run (STAGES:260 still lists it "planned")
- registrations: none | trials 44 | counted in N 198 (STAGES ladder); 8 members, 44 trials (STAGES:86-88)
- closing: V40 (and V38), docs/DECISIONS.md:728-729: "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read."
- notes: K2-monthend-01 is reused at 5-day holds in R1-18 | E.16 overlap audit (E.16_RETURN:222-229) names K2-aucpre-01/aucpost-01 as the closest tested member of E16-H3 and K2-monthend-01 of E16-H2: "related, not identical"
- members: 8 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-05 [intraday_screen] K3 FX screen: CP1/CP2/CP3, London-fix reversal and momentum (ldnrev, ldnmom), ECB fix, Tokyo fix pre/post, month-end hedge
- products: 6E (traded), 6A (traded), 6B (traded), 6C (traded), 6J (traded), 6N (traded), 6S (traded)
- horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members | data: 1-minute step bars (Stage E harness; bar-based) | windows: E.4c screen: research 2025-04-01..2026-06-17 (299 trade dates) ; E.22 confirmation of K3-ldnrev-01 6E on 2019-05-06..2024-02-29 (1191 trade dates): null
- registrations: none | trials 27 | counted in N 198 (STAGES ladder); 9 members, 30 trials, 27 counted (3 excluded on coverage; STAGES:96-98; N 123 -> 150)
- closing: V40 (and V38), docs/DECISIONS.md:728-729: "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read."
- notes: K3-mehedge-01 on EUR not traded (no free index history); K3-ldnrev-01 6E Tier A -> E.22 null (STAGES:183)
- members: 9 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-06 [intraday_screen] K4 energy screen: CP1/CP2/CP3, NG storage pre-release, API/EIA pre/post, overreaction fade
- products: MCL (traded (CL bars)), NG (traded), CL (price path)
- horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members | data: 1-minute step bars (Stage E harness; bar-based) | windows: E.4 screen: 2025-04-01..2026-06-19 (270 MCL / 269 NG dates) ; E.5 confirmation: NG 2019-05-06..2024-02-29, MCL 2021-07-12..2024-02-29: NULL (K4-ngpre-01 fails Holm)
- registrations: none | trials 12 | counted in N 198 (STAGES ladder); 8 members, 12 trials (STAGES:89-92)
- closing: V40 (and V38), docs/DECISIONS.md:728-729: "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read."
- members: 8 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-07 [intraday_screen] K5 metals screen: CP1/CP2/CP3, LBMA AM/PM auction windows, FOMC, overreaction fade
- products: MGC (traded (GC bars)), MHG (traded (HG bars)), GC (price path)
- horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members | data: 1-minute step bars (Stage E harness; bar-based) | windows: E.4b screen: research 2025-04-01..2026-06-17, 295 trade dates ; E.22 confirmation K5-fomc-01 MGC W_cf 2019-05-06..2024-02-29 (1174 days): null
- registrations: none | trials 9 | counted in N 198 (STAGES ladder); 7 members, 11 trials in STAGES:93, 9 counted (N 114 -> 123; 3 excluded: two MHG ports, pmfix)
- closing: V40 (and V38), docs/DECISIONS.md:728-729: "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read."
- notes: inventory shows 11 K5 rows, counted 9: row/counted mismatch (see ambiguities)
- members: 7 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-08 [intraday_screen] K6 grains/oilseeds/livestock screen: CP1/CP2/CP3, soybean crush gap, WASDE pre/post, livestock limit continuation
- products: ZC (traded), ZS (traded), ZL (traded), ZM (traded), ZW (traded), HE (traded), LE (traded)
- horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members | data: 1-minute step bars (Stage E harness; bar-based) | windows: E.8 screen: research window 2025-04-01..2026-06-19 (264-287 dates per trial) ; E.22 confirmation K6-limitcont-01 HE: null by inactivity (2019-05-06..2024-02-29)
- registrations: none | trials 27 | counted in N 198 (STAGES ladder); 7 members, 27 trials (STAGES:108-110)
- closing: V40 (and V38), docs/DECISIONS.md:728-729: "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read."
- notes: K6-crushgap-01 ZS used ZM 1-minute bars as the signal leg (ZM is also R1-14/R1-21 product)
- members: 7 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-09 [intraday_screen] K7 bitcoin screen: CP1/CP2/CP3, expiry, 2-hour reversal, monthly trend
- products: MBT (traded)
- horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members | data: 1-minute step bars (Stage E harness; bar-based) | windows: E.6 screen: research 2025-04-01..2026-06-17, 265 trade dates ; all six Tier B, Tier A empty
- registrations: none | trials 6 | counted in N 198 (STAGES ladder); 6 members, 6 trials (STAGES:102-104)
- closing: V40 (and V38), docs/DECISIONS.md:728-729: "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read."
- notes: K7-expiry-01 not traded (every research expiry day in a roll blackout)
- members: 6 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-10 [intraday_screen] K8 cross-market screen: equity-flight into gold (H30, HEOD), oil/CAD, weekend bitcoin to NQ
- products: MGC (traded), MES (signal leg), 6C (traded), MCL (signal leg), MNQ (traded), MBT (signal leg)
- horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members | data: 1-minute step bars (Stage E harness; bar-based) | windows: E.9 screen: research 2025-04-01..2026-06-16 (250-280 dates) ; E.22 confirmation: K8-flight-01 HEOD null (2020-02-04..2024-02-29, 944 dates); K8-wkndbtc-01 inconclusive by design (not run)
- registrations: none | trials 4 | counted in N 198 (STAGES ladder); 3 members, 4 trials (STAGES:111-114)
- closing: V40 (and V38), docs/DECISIONS.md:728-729: "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read."
- members: 3 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-11 [ml_search] ML route v2 Gate 0: Family A (64 generic signals x 3 horizons = 192 tests) and Family B (27 products x 3 horizons = 81 product-horizon tests), ridge/LightGBM design, cost-gated
- products: 6A (tested), 6B (tested), 6C (tested), 6E (tested), 6J (tested), 6N (tested), 6S (tested), HE (tested), LE (tested), M2K (tested), MCL (tested), MGC (tested), MHG (tested), MNQ (tested), MYM (tested), NG (tested), TN (tested), UB (tested), ZB (tested), ZC (tested), ZF (tested), ZL (tested), ZM (tested), ZN (tested), ZS (tested), ZT (tested), ZW (tested)
- horizons: h60, h120, hF (minutes; hF = to flat) | data: 1-minute bars, 64-feature library, decision clock | windows: training window 2019-05..2024-02 (S_X 2019-05-06; ZF 2020-10-01, ZT 2021-10-01); 1,067-1,068 dates ; MBT no Gate 0 row; holdout-2 not read
- registrations: ledger baseline (N 471); ledger/ml_v2_config_ledger.jsonl 273 entries | trials 273 | N 198 + 273 = 471 (reports/E.12_RETURN.md:28)
- closing: V24, docs/DECISIONS.md:449-451: "Under the frozen V2.2b, ML route v2 stops: no phase-2 purchase, no V2.6 model, no holdout-2 registration."
- exceptions: V24: "any reuse needs a new pre-registration that counts N = 471" (DECISIONS:453-454) | V43 reopens ML for order-book/limit-order strategies only
- notes: best pair NG h60: mean gross 5.57 ticks vs c 1.71, t_B 2.51, Holm rank 1 of 273 not rejected (reports/E.12_RETURN.md:10-12) | pooled family B mean gross -0.72 ticks vs cost 2.26, t 0.28 (E.12_RETURN:13)
- cross-market [added 2026-10-29 (session 4, RV2 B1/S6)]: includes G17: 60-minute log returns (x 1e4) of the other clusters' lead prices, g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_zc and (E.12 only) g17_mbt (ml_route_v2/signals/generic.py:22-25, 390-392; leads ml_route_v2/constants.py:36-37), never applied on the product's own cluster (generic.py:343, 351-352; c1_replication/c1b.py:53-54). g17_mes is defined but was excluded in E.12 by rule P-1a (MES store refused; reports/stage_e12_rulings.md:49), and MBT's E.12 store starts 2024-01-02 (reports/stage_e12_phase1_bars.json roots.MBT.s_x), so g17_mbt was live only 2024-01-02..2024-02-29. Tested pooled over the 27 products in Family A at h60, h120, hF (reports/stage_e12_gate0.md:158-164, 222-228, 286-292, rows gate0A_g17_*) and as inputs of Family B's ridge (all features, one model per horizon pooled across products, tested per product and horizon; ml_route_v2/gate0.py:11-12); decision times t1-t3 (equity 09:00, 11:00, 13:00 CT; grains 09:00, 10:00, 11:00; ml_route_v2/constants.py:50, 57). Live on M2K (cluster K1, own lead NQ excluded; constants.py:23): ZN, 6E, CL, GC, ZC (MBT from 2024-01-02). Live on ZL (cluster K6, own lead ZC excluded; constants.py:31): NQ, ZN, 6E, CL, GC (MBT from 2024-01-02); ZS and ZM are not G17 leads.
### R1-12 [replication] C1 / C1b backward NG replication (frozen ridge M1 with world-market features)
- products: NG (traded), NQ (feature leg), ZN (feature leg), 6E (feature leg), GC (feature leg), ZC (feature leg)
- horizons: h60, hF | data: 1-minute bars (ext2010 store) | windows: W_ext NG 2010-07..2019-04 (store 2010-06-07..2019-04-30), read once each
- registrations: r001-C1 (2; stopped at guard C10, no statistic); r003-C1b (2; evaluated once) | trials 4 | ledger: r001-C1 N 471->473; r003-C1b N 478->480
- closing: V31 (C1 attempt closed), V32 (NG near-miss closed), docs/DECISIONS.md:578-580: "C1b failed (NG h60 t_B -0.83, hF -0.41; Fable verified); the NG near-miss is closed; N is 480."
- notes: V31 :564 "no statistic exists; the attempt is closed" for C1 | STAGES:160-162: T1 NG h60 mean 0.585 ticks vs bar 2.562; T2 NG hF -0.113 vs 2.649
### R1-13 [base_rule_batch] E.16 forced-flow base rules: H1 settlement-window intraday momentum (pooled), H2 month-end NQ vs ZN pair, H3 Treasury auction cycle, H4 next-day reversal of the settlement-window move, H5 equal-risk combination
- products: NQ (pooled (H1/H4)), YM (pooled (H1/H4)), RTY (pooled (H1/H4)), ZT (pooled (H1/H4)), ZF (pooled (H1/H4)), ZN (pooled (H1/H4)), TN (pooled (H1/H4)), ZB (pooled (H1/H4)), UB (pooled (H1/H4)), 6E (pooled (H1/H4)), 6A (pooled (H1/H4)), 6B (pooled (H1/H4)), 6C (pooled (H1/H4)), 6J (pooled (H1/H4)), 6S (pooled (H1/H4)), 6N (pooled (H1/H4)), CL (pooled (H1/H4)), NG (pooled (H1/H4)), GC (pooled (H1/H4)), HG (pooled (H1/H4)), ZC (pooled (H1/H4)), ZW (pooled (H1/H4)), ZS (pooled (H1/H4)), ZM (pooled (H1/H4)), ZL (pooled (H1/H4)), LE (pooled (H1/H4)), HE (pooled (H1/H4))
- horizons: H1/H4 settlement-window intraday; H2 and H3 hold overnight (multi-day, personal-account venue); H5 combination | data: 1-minute bars | windows: 2010-07..2024-02 on the 17 W_ext roots; 2019-05-06..2024-02-29 on the 10 fallback roots (YM 6A 6B 6C 6J 6S 6N HG ZW ZM)
- registrations: r002-E16 (E16-H1..H5; 5) | trials 5 | N 473 -> 478
- closing: V31, docs/DECISIONS.md:568-571: "The base-rule batch H1 to H5 is closed: all five failed (H1's gross is about a quarter of its D8 cost; H2 positive at p 0.068, not a pass); no rerun or variant on these windows, no purchase of the 10 fallback roots, no holdout-2 read."
- exceptions: H2 (month-end NQ/ZN) noted as a personal-account candidate only, not pursued (V33 item 4, DECISIONS:608)
- notes: H3 roots not extracted (Treasury tenors per E.16 freeze) | E.16 overlap audit closest tested members: H1 CP1 port, H2 K2-monthend-01, H3 K2-aucpre/aucpost-01, H4 CP3 port, H5 none (E.16_RETURN:222-229) | ambiguous: for lead: V28 (DECISIONS:524) says H2 and H3 hold overnight; E.16 overlap audit lists their closest members as intraday-only | DSR at N=478: all about 0 (E.17_RETURN:575)
### R1-14 [intraday_test] H6 rest-of-day to last-half-hour momentum on NQ (Baltussen, Da, Lammers, Martens 2021): T1 always, T2 above trailing |r_ROD| median, T3 negative prior-day GEX
- products: NQ (traded (MNQ cost))
- horizons: last half hour (about 30 min), entry at 14:30 CT | data: 1-minute NQ step2 store | windows: 2020-06-01..2024-02-29 (GEX rows 2020-05-29..2024-02-28), run once
- registrations: r004-E20H6 (3) | trials 3 | N 480 -> 483
- closing: V38, docs/DECISIONS.md:678-679: "The intraday program on Topstep is closed: nothing in 528 trials passed"
- notes: T1 gross 1.25 ticks vs 4.08 cost, t -0.53 (STAGES:172-173) | reversal direction reused at 5/20-day holds in R1-18
- members: 3 rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)
### R1-15 [ml_search] E.20 Part C ML pattern search: ridge and shallow LightGBM, 45 configurations, extra decision time t4 = F_X - 60 min, r_ROD features
- products: NQ (searched), RTY (searched), ZT (searched), ZF (searched), ZN (searched), TN (searched), ZB (searched), UB (searched), 6E (searched), CL (searched), NG (searched), GC (searched), ZC (searched), ZS (searched), ZL (searched), LE (searched), HE (searched)
- horizons: h60, h120, hF | data: 1-minute step2 stores, 36 features | windows: 2019-05-06..2024-02-29 (nested CPCV, 57,775 decision rows); backward 2010-2019 read not run
- registrations: r005-E20S (E20S-01..45; 45) | trials 45 | N 483 -> 528
- closing: V38, docs/DECISIONS.md:679-681: "nothing in 528 trials passed, and no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip (E.20 Part A, 157 evidence rows)"
- exceptions: V45 item 4 amends the sentence: three working-paper effects (see R1-19)
- notes: all 45 configurations negative out of sample; median-path t -1.33, PBO 0.60, net Sharpe -0.83 (STAGES:172-174) | E.20 Part A: 17 root readers, 0 features accepted
- cross-market [added 2026-10-29 (session 4, RV2 B1/S6)]: includes G17: 60-minute log returns (x 1e4) of the other clusters' lead prices, g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_zc, six of the 36 frozen features (pattern_search/constants.py:59, 66; reports/stage_e20_search_freeze.json feature_names), computed by the frozen ml_route_v2 code (pattern_search/panel.py:64, 75; ml_route_v2/signals/generic.py:22-25, 343, 351-352), so never applied on the product's own cluster; g17_mbt and g17_mes dropped by the leg rule (reports/stage_e20_plan.md:138). One pooled model per horizon over the 17 vehicles (stage_e20_plan.md:28) at h60, h120, hF, 2019-05-06..2024-02-29 (pattern_search/constants.py:30-31); decision times t1-t3 (equity 09:00, 11:00, 13:00 CT; grains 09:00, 10:00, 11:00; ml_route_v2/constants.py:50, 57) and t4 = F_X - 60 min (14:08 CT equity, 12:18 CT grains; stage_e20_plan.md:81-82). Live on RTY (vehicle M2K, cluster K1): ZN, 6E, CL, GC, ZC (not NQ). Live on ZL (cluster K6): NQ, ZN, 6E, CL, GC (not ZC; ZS and ZM are not G17 leads).
### R1-16 [multiday] E.21 multi-day: T1 12-month TSMOM (MOP 2012), T2 1/3/12-month trend blend (HOP 2017), T3 equity turn of the month, T4 equal-risk book with H2
- products: NQ (traded), RTY (traded), ZT (traded), ZF (traded), ZN (traded), TN (traded), ZB (traded), UB (traded), 6E (traded), CL (traded), NG (traded), GC (traded), ZC (traded), ZS (traded), ZL (traded), LE (traded), HE (traded)
- horizons: monthly/multi-day (T3 turn of month on NQ and RTY) | data: daily/settlement paths from owned 1-minute stores | windows: 2010-2024 owned data (E.21 return: AQR comparison 2010-07..2024-02)
- registrations: r006-E21 (4) | trials 4 | N 528 -> 532
- closing: V39, docs/DECISIONS.md:697-699: "Trend is recorded as consistent with the published evidence, not established by this program's bar; no further trend variant on 2010-2024."
- notes: T1 net Sharpe 0.50 [-0.06, 1.05], t 1.78, p 0.042; T2 0.44; T3 0.15; T4 0.12; all FAIL on Holm 0.025 (STAGES:177-180) | V39: no ML overlay on trend built (DECISIONS:709)
### R1-17 [forward_registered_parked] E22-F1 micro trend book forward test at USD 25,000 (E.21 trend rule on 12 micros)
- products: MICROS12 (12 micros on E.21 owned paths (list in the E.22 freeze; not extracted))
- horizons: daily | data: daily settlement | windows: forward test, 36 months from the first ledger record after a settlement source is approved; warm-up read approved in V42 (2024-03-01 to start)
- registrations: r007-E22 (1) | trials 1 | N 532 -> 533
- closing: V43 (parked), not a closing, docs/DECISIONS.md:804-806: "no paper trading for now and no 24/7 gateway on the laptop (E22-F1, E22-F1b, E22-F2 and any C1 forward record parked, unregistered, N 538)"
- notes: ambiguous: for lead: V43 says "unregistered" while the ledger holds r007-E22 (N 533)
### R1-18 [multiday] E.23 program triggers at 5- and 20-day holds (entered at the trigger day's settlement; alpha over E.21 trend returns): K2-monthend-01 long ZF/ZN/ZB at 5 days; E20H6-T1 reversal on NQ at 5 and 20 days
- products: ZF (traded), ZN (traded), ZB (traded), NQ (traded)
- horizons: 5 and 20 trading days | data: daily from owned stores | windows: discovery W_ext 2011-07-27..2019-04-30, read once ; confirmation W_cf 2019-05..2024-02 not computed (power 0.18)
- registrations: r008-E23 (E23-MEZFh5, MEZNh5, MEZBh5, H6NQh5, H6NQh20; 5) | trials 5 | N 533 -> 538
- closing: V41, docs/DECISIONS.md:749-751: ""The program's intraday triggers at multi-day holds" is closed as a direction; no variant (other roots, other holds, the opposite H6 direction) is tested on these windows."
- exceptions: W_cf (2019-05..2024-02, trigger-conditional multi-day outcomes unread) and holdout-2 kept for a hypothesis with a stronger prior (DECISIONS:751-754)
- notes: alpha t 0.55/0.38/0.10/-1.61/-0.71; Holm smallest p 0.31 (STAGES:194-195) | the month-end gain is the bonds' drift
### R1-19 [intraday_closure_umbrella] Intraday program closure with its exceptions (E.20 Part A literature, 17 roots, 157 evidence rows; re-dug in E.25)
- products: NQ (scope), RTY (scope), ZT (scope), ZF (scope), ZN (scope), TN (scope), ZB (scope), UB (scope), 6E (scope), CL (scope), NG (scope), GC (scope), ZC (scope), ZS (scope), ZL (scope), LE (scope), HE (scope)
- horizons: intraday | data: published-effect census, no data read | windows: n/a
- registrations: none | trials 0 | covers 528 trials at V38 (N 538 later)
- closing: V38 as amended by V45 item 4, docs/DECISIONS.md:910-916: "no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip, except three working-paper effects whose samples run past 2015, none with a significant post-2015 estimate"
- exceptions: V45: pre-refunding-announcement ZN gain (Wang and Zhao 2025, cash, +12.62 bp, t 3.32) | V45: pre-FOMC ZN drift (Pan and Peng 2026, futures, +7.26 bp, t 2.82, 2004-01..2025-06) | V45: ES 3rd-Friday reversal (Baltussen, Terstegge and Whelan, -12.89 bp, t -2.40, 2003-2021; 2015-23 not significant alone) | V45: "Each gives 3 to 15 events in the research window (power 0.11 to 0.22 at the published sizes), so none can be tested with adequate power on owned data." (DECISIONS:919-921)
- notes: quote of the closure end: "The closure of the intraday program (V38) stays in place." (DECISIONS:922) | E.25 shortlist also named noise-area intraday momentum on MNQ (V34 item 4 had dropped it as "unsized"); never tested (reports/E.25_RETURN.md:13,29)
### R1-20 [passive_execution_measured] Passive spread capture at the touch, one lot, trade-through fills (E.31 ZM order-book pilot); covers ZM, QM (frozen QM pilot never bought) and ZL follow-up (skipped)
- products: ZM (measured), QM (closed by decision, not measured), ZL (closed by decision, skipped), ZS (conditioning data (MBP-1))
- horizons: 10 s markout per fill | data: ZM MBO (front two months), ZS and ZL MBP-1; 156 files, 24.2 GB | windows: 2020-12..2024-02 (39 whole months; 816 trade dates measured, 764 DAY dates usable) ; nothing on or after 2024-03-01
- registrations: none (nothing registered; N 538) | trials 0 | E.31 registered nothing
- closing: V50, docs/DECISIONS.md:1034-1037: "Passive spread capture at the touch with a one-lot at prop-firm simulators is closed. This covers ZM, QM (E.28's frozen QM pilot is closed, never bought) and the ZL follow-up of V49 (skipped). E.29 D2 (baskets around ZM) is not run."
- exceptions: V50 item 2: "Limit orders stay allowed as an execution method for a directional signal. They are not a source of edge in themselves." | V56 item 2: limit orders as execution of a directional signal stay open; "Order-book direction is not closed for other products." (DECISIONS:1149-1152)
- notes: ZM front-month DAY 10 s edge net of Topstep fee -1.234 ticks [-1.252, -1.214]; gross -0.970; K-algorithm -0.29, FIFO -0.25 gross (E.31_RETURN:20-27) | V50 item 4: E.31 read these dates for passive-fill markouts incl. queue-imbalance splits; "Any test of an order-flow signal on these dates is therefore not a clean holdout." (DECISIONS:1046-1050) | V49 item 2: MGC out of passive spread capture (fee 1.5-2.2 ticks vs 1-tick maximum capture): decision, not measurement; MGC kept "only as a possible directional test"
### R1-21 [directional_search] ZM directional 5-60 minute search, five feature sets: S1 crush residual, S2 cross-asset propagation from ZS and ZL, S3 ZM order flow and book state, S4 ZM own price path, S5 all four pooled; x 6 labels x 10 model settings (6 regularised multinomial logits, 4 shallow LightGBM)
- products: ZM (traded), ZS (input), ZL (input)
- horizons: fixed horizons 5, 15, 30, 60 minutes; triple barrier at 15 and 30 | data: ZM MBO plus ZS/ZL MBP-1 (order-book schemas), 59 features, Topstep market orders 1 s latency, fee 0.528 tick | windows: 796 out-of-fold dates 2020-12-30..2024-02-29, 6 blocked folds, 21-date embargo ; test window 2017-05-01..2020-11-30 sealed, unread
- registrations: r009-E33 (300 configurations) | trials 300 | N 538 -> 838
- closing: V56, docs/DECISIONS.md:1146-1148: "ZM's directional route at 5-60 minute holds is closed. There is no E.34 and no purchase. The 2017-05..2020-11 window stays sealed for a future hypothesis family."
- exceptions: V56 item 2: order-book direction not closed for other products; limit orders as execution of a directional signal stay open
- notes: Tier A empty; best loses 1.098 ticks/trade; best daily Sharpe 0.0478 vs binding 0.2007; DSR at most 0.025; BH and Holm reject 0; PBO 0.14 (E.33c_RETURN:15-31) | 61 of 300 met G1 (all lose over 1.0 tick/trade); 8 averaged at least 0.5 tick on at most 55 trades | minimum detectable edge 1.5-4.4 ticks/trade at the trade rates seen (E.33c_RETURN:355-357) | E.33c: "not a null statement in the program's sense"; no statement for all five sets
### R1-22 [product_decision] NQ dropped for the passive limit-order direction
- products: NQ (dropped)
- horizons: n/a | data: n/a | windows: none read
- registrations: none | trials 0 | decision from E.28 ranks 33, 45, 52, 54, 62
- closing: V49 item 1, docs/DECISIONS.md:1010-1016: "NQ is dropped as a candidate at every firm (E.28 ranks 33, 45, 52, 54 and 62), despite Topstep's 0.44-tick break-even. Reasons: very long queues and HFT competition ... Topstep's Tier 1 news windows block NQ. NQ is not used as a pilot or comparison contract."
- notes: ambiguous: for lead: V49 is headed "For the passive limit-order direction (V43, E.28)"; its scope for directional market-order use of NQ is not stated. Ranking spec section 0 treats NQ as "excluded (V49)" | NQ appears in other closed lines: R1-03 (price path of MNQ), R1-12 (feature leg), R1-13, R1-14, R1-15, R1-16, R1-18
### R1-23 [closed_directions_no_trials] Directions closed by the user without a program trial: prediction markets; crypto; commodity event drift as a standalone stage; ML overlay on trend; C2 GEX late-session momentum stopped before freeze
- products: MBT (crypto direction (K7 screened, R1-09)), CRUDE_METALS_NATGAS (commodity event drift direction, no product list given)
- horizons: n/a | data: n/a | windows: none read
- registrations: none | trials 0 | C2 stopped at its power rule, N unchanged
- closing: V39 (and V27 for C2), docs/DECISIONS.md:702-706: "Closed as directions: prediction markets (user), crypto (every prior crypto line closed negative across the user's projects), commodity event drift as a standalone stage (planning research: geopolitical news is priced fast, OPEC drift has decayed; at most an overlay on trend)."
- exceptions: V39: small caps "marginal ... not run now" (DECISIONS:706-709): not closed | V27: C2 "stays stopped with no rerun planned" (DECISIONS:499-501)
- notes: ambiguous: for lead: V27 says C2 stopped at its power rule before its freeze (135 eligible negative-GEX dates, floor 200); a stop, not a test

## Standing decisions that are constraints, not lines
- V28 (docs/DECISIONS.md:509-512): No deep network, reinforcement learning or other ML layer goes onto a rule set that has not passed a pre-registered test; amended by V33 item 5 (E.20) and V43 (order-book/limit-order ML may itself be the strategy)
- V31 (docs/DECISIONS.md:571-576): cost-feasibility gate: every future hypothesis states expected gross per trade from published evidence against the D8 round-trip cost and is dropped if it does not clear the pass multiple
- V33 (docs/DECISIONS.md:596-598): No Combine is bought until a strategy passes a registered test and its follow-up reads with a net Sharpe of about 0.5 or more
- V51 (docs/DECISIONS.md:1062-1067): ZM test window 2017-05-01..2020-11-30 sealed by E.32 Part 0, covers every schema; 2024-03 onward closed unless the user approves

## Lookup by product (role in line; siblings = other codes on the same underlying per spec section 0, with the extra lines they add)
- MCL: R1-06 traded, R1-10 signal leg, R1-11 tested; siblings QM/CL add R1-13,R1-15,R1-16,R1-19,R1-20
- QM: R1-20 closed by decision, not measured; siblings MCL/CL add R1-06,R1-10,R1-11,R1-13,R1-15,R1-16,R1-19
- CL: R1-06 price path, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope; siblings MCL/QM add R1-10,R1-11,R1-20
- MNG: none; siblings QG/NG add R1-06,R1-11,R1-12,R1-13,R1-15,R1-16,R1-19
- QG: none; siblings MNG/NG add R1-06,R1-11,R1-12,R1-13,R1-15,R1-16,R1-19
- NG: R1-06 traded, R1-11 tested, R1-12 traded, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope
- MGC: R1-07 traded, R1-10 traded, R1-11 tested; siblings GC add R1-12,R1-13,R1-15,R1-16,R1-19
- GC: R1-07 price path, R1-12 feature leg, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope; siblings MGC add R1-10,R1-11
- MHG: R1-07 traded, R1-11 tested; siblings HG add R1-13
- HG: R1-13 pooled; siblings MHG add R1-07,R1-11
- M6E: none; siblings 6E add R1-05,R1-11,R1-12,R1-13,R1-15,R1-16,R1-19
- 6E: R1-05 traded, R1-11 tested, R1-12 feature leg, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope
- M6A: none; siblings 6A add R1-05,R1-11,R1-13
- 6A: R1-05 traded, R1-11 tested, R1-13 pooled
- MBT: R1-09 traded, R1-10 signal leg, R1-23 crypto direction
- BTC: none; siblings MBT add R1-09,R1-10,R1-23
- M2K: R1-03 traded, R1-11 tested; siblings RTY add R1-13,R1-15,R1-16,R1-19
- RTY: R1-03 price path/W_ext, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope; siblings M2K add R1-11
- MYM: R1-03 traded, R1-11 tested; siblings YM add R1-13
- YM: R1-03 price path, R1-13 pooled; siblings MYM add R1-11
- MNQ: R1-03 traded, R1-10 traded, R1-11 tested; siblings NQ add R1-12,R1-13,R1-14,R1-15,R1-16,R1-18,R1-19,R1-22
- NQ: R1-03 price path/W_ext, R1-12 feature leg, R1-13 pooled, R1-14 traded, R1-15 searched, R1-16 traded, R1-18 traded, R1-19 scope, R1-22 dropped; siblings MNQ add R1-10,R1-11
- ZT: R1-04 traded, R1-11 tested, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope
- ZF: R1-04 traded, R1-11 tested, R1-13 pooled, R1-15 searched, R1-16 traded, R1-18 traded, R1-19 scope
- ZN: R1-04 traded, R1-11 tested, R1-12 feature leg, R1-13 pooled, R1-15 searched, R1-16 traded, R1-18 traded, R1-19 scope
- ZB: R1-04 traded, R1-11 tested, R1-13 pooled, R1-15 searched, R1-16 traded, R1-18 traded, R1-19 scope
- MZC: none; siblings XC/ZC add R1-08,R1-11,R1-12,R1-13,R1-15,R1-16,R1-19
- MZS: none; siblings XK/ZS add R1-08,R1-11,R1-13,R1-15,R1-16,R1-19,R1-20,R1-21
- MZW: none; siblings XW/ZW add R1-08,R1-11,R1-13
- MZL: none; siblings ZL add R1-08,R1-11,R1-13,R1-15,R1-16,R1-19,R1-20,R1-21
- MZM: none; siblings ZM add R1-08,R1-11,R1-13,R1-20,R1-21
- XC: none; siblings MZC/ZC add R1-08,R1-11,R1-12,R1-13,R1-15,R1-16,R1-19
- XK: none; siblings MZS/ZS add R1-08,R1-11,R1-13,R1-15,R1-16,R1-19,R1-20,R1-21
- XW: none; siblings MZW/ZW add R1-08,R1-11,R1-13
- ZC: R1-08 traded, R1-11 tested, R1-12 feature leg, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope
- ZS: R1-08 traded, R1-11 tested, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope, R1-20 conditioning data, R1-21 input
- ZW: R1-08 traded, R1-11 tested, R1-13 pooled
- ZL: R1-08 traded, R1-11 tested, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope, R1-20 closed by decision, skipped, R1-21 input
- ZM: R1-08 traded, R1-11 tested, R1-13 pooled, R1-20 measured, R1-21 traded
- ES: none; siblings MES add R1-01,R1-02,R1-10
- MES: R1-01 traded, R1-02 traded, R1-10 signal leg
- TN: R1-04 traded, R1-11 tested, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope
- UB: R1-04 traded, R1-11 tested, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope
- 6B: R1-05 traded, R1-11 tested, R1-13 pooled
- 6C: R1-05 traded, R1-10 traded, R1-11 tested, R1-13 pooled
- 6J: R1-05 traded, R1-11 tested, R1-13 pooled
- 6S: R1-05 traded, R1-11 tested, R1-13 pooled
- 6N: R1-05 traded, R1-11 tested, R1-13 pooled
- HE: R1-08 traded, R1-11 tested, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope
- LE: R1-08 traded, R1-11 tested, R1-13 pooled, R1-15 searched, R1-16 traded, R1-19 scope
- No closed line touches (directly or via a same-underlying code): SIL, SI, MET, ETH, 2YY, 5YY, 10Y, 30Y

## Lookup by family or mechanism
- Opening-range / breakout momentum (CP2 port; MES B-H1,B-H3,B-H4, Family H NR4/NR7/inside-day ORB) -> R1-01,R1-03,R1-04,R1-05,R1-06,R1-07,R1-08,R1-09 [members *-cp2-01 on every K cluster; MES B-*, H1-H5]
- Open-to-first-half-hour / overnight-to-decision momentum into the close (CP1 port; E20 H6 rest-of-day; E16-H1 settlement-window) -> R1-01,R1-03,R1-04,R1-05,R1-06,R1-07,R1-08,R1-09,R1-13,R1-14 [*-cp1-01; H6 T1-T3; E16-H1,H4]
- Prior-day close-location continuation or reversal (CP3 port; MES C-H3) -> R1-01,R1-03,R1-04,R1-05,R1-06,R1-07,R1-08,R1-09 [*-cp3-01; MES C-H3]
- Overreaction / spike fade after an intraday move (ovr, C-H1,C-H2, VXN band) -> R1-01,R1-03,R1-06,R1-07 [K4-ovr-01, K5-ovr-01, K1-vxnband-01, MES C-H*]
- Scheduled macro / event windows: FOMC, Treasury auctions, ISM, API/EIA, NG storage, WASDE, LBMA fix, ECB/Tokyo fix -> R1-01,R1-04,R1-05,R1-06,R1-07,R1-08 [K2 aucpre/aucpost/fomcpost/predrift; K3 ldnrev/ldnmom/ecbfix/tky*; K4 ngpre/apipre/eia*; K5 preauc/pmfix/fomc; K6 wasde*]
- Calendar: month-end, turn of the month, weekend, overnight / European-open drift -> R1-01,R1-04,R1-13,R1-16,R1-18 [K2-monthend-01; E16-H2; E21 T3; MES A-H1,A-H3,E-H4]
- Volatility-regime gates, range compression, gaps, sizing -> R1-01,R1-03 [MES D-H1..D-H4; K1-vxnband-01]
- Cross-market relationships: equity flight to gold, oil/CAD, weekend bitcoin, soybean crush gap -> R1-08,R1-10 [K8-*; K6-crushgap-01]
- Crypto (MBT) rules -> R1-09,R1-10 [K7-*; K8-wkndbtc-01]
- ML pooled-feature or model search at 60 minutes, 120 minutes, to flat -> R1-11,R1-12,R1-15,R1-21 [Gate 0 (192+81), C1/C1b M1, E20S-01..45, E33 logit/LightGBM]
- Trend / TSMOM / trend blend and equity turn of month (multi-day) -> R1-16,R1-17,R1-18 [E21 T1-T4, E22-F1, E23]
- Intraday triggers held 5 and 20 days -> R1-18 [E23-MEZFh5/MEZNh5/MEZBh5/H6NQh5/H6NQh20]
- Passive spread capture / resting limit orders (one lot, trade-through) -> R1-02,R1-20 [C-H4/C6; E.31 ZM pilot; QM and ZL by decision]
- Order flow and book state on ZM at 5-60 minutes; crush residual; ZS/ZL propagation; own price path -> R1-21 [E33 sets S1-S5]
- Published-effect census on 17 roots (intraday) -> R1-15,R1-19 [E.20 Part A, E.25 re-dig]

## Ambiguous: for lead
- V49 scope (R1-22): headed "For the passive limit-order direction"; whether NQ is closed for directional market-order use is not stated.
- V38 scope (R1-15, R1-19): V38 says "intraday program on Topstep is closed"; V45 item 4 says "closure of the intraday program (V38) stays in place" without "on Topstep".
- V39 / V41 scope (R1-16, R1-18): "no further trend variant on 2010-2024" and "no variant ... tested on these windows" bind windows; V41 keeps W_cf and holdout-2 for a stronger prior.
- V43 vs ledger (R1-17): V43 calls E22-F1 "parked, unregistered, N 538"; ledger r007-E22 registered it (N 533). It has no outcome; counted in N, not a closed line.
- E.25 shortlist (R1-19): noise-area MNQ (V34 item 4 dropped it as "unsized"), the 3rd-Friday spike and the two ZN drifts were never tested; V45 lists the last three as exceptions to V38. Closed or open is for the lead.
- V27 (R1-23): C2 GEX late-session momentum stopped at its power rule before any test; "stays stopped with no rerun planned".
- docs/STAGES.md:260 still lists "Stage E.3b onward" (K2 confirmation and later cluster confirmations) as planned; V40 (DECISIONS:728-729) closes Stage E intraday clusters. K1, K2, K3 (except ldnrev), K6 (except limitcont), K7 had no confirmation.
- Counts: K5 inventory has 11 rows, STAGES counts 9 trials (N 114 -> 123); K3 30 rows vs 27 counted; K6 inventory excludes 4 of 27 though 27 counted. N ladder (STAGES) used for counts.
- E16-H2/H3: V28 (DECISIONS:524) says they hold overnight; E.16 overlap audit names intraday K2 members as closest.
- MES/ES/other roots are outside the 47-code universe (spec section 0) but are closed lines R1-01, R1-10 (leg).
