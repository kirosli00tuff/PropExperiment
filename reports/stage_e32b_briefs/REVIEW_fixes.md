# REVIEW_fixes: independent check of the session-4 fixes and the E_dir table (Stage E.32b wave F, F4)

Reviewer: FixVerifier-FableXHigh (worker-xhigh, Fable 5.1 at xhigh effort; fresh context, produced none of the work
checked). Work 09:23:22-09:37 PDT 2026-10-29 (times from `date`). Brief: briefs/brief_wave_f.md header, section F4 and
"F4 addendum (lead, 09:23)". B = reports/stage_e32b_briefs. Inputs read by section only; no data file, no Databento
call, no TopstepX, no commit. Holdout status at start (09:23:22) and end (09:36:39): `unlocks_logged: 0`, `all_ok:
true`. Written: this file and B/work/fix4/verify/ (nine scripts, listed at the end). Every key number below was
recomputed by my own scripts from the JSON sources; the reviewers' helpers in work/rv1/ and work/rv2/ were not needed
and were not run.

## Verdict: PASS

No BLOCKING and no SHOULD FIX item. Every RV1 and RV2 BLOCKING and SHOULD FIX item is fixed as the prompt's Step 4
requires, every number I checked reproduces, and no session-4 script reads an outcome or a data file. Seven NOTE items
(wording, timestamps, attribution) are listed for the lead; none changes a score, gate, rank, C, R4 list or prior.

## Findings

### BLOCKING

None.

### SHOULD FIX

None.

### NOTE

- **N1. lead_sections.md header time range.** B/work/R4/lead_sections.md:1 says "revised in session 4, 08:49-09:00
  PDT". STATE rows: L10 08:47:26-08:49:25 (the rewrite) and L12b 09:21-09:22:29 (the six replacements); the file's
  mtime is 09:22:29. Evidence: `stat` and reports/stage_e32b_STATE.md:541, 548. Fix: "08:47-08:49 and 09:22 PDT" (or
  drop the range). The header line is not part of the text quoted into the recommendations file.
- **N2. fix_lead_text_s4.py docstring stamps a time after the event.** B/work/R4/fix_lead_text_s4.py:1 says "~09:24
  PDT"; the script and both files it wrote have mtime 09:22:29, and STATE L12b ends 09:22:29. Fix: "09:22 PDT".
- **N3. Ranking file byline.** reports/stage_e32b_ranking.md:3 reads "Draft by RankingWriter-OpusHigh (worker, Opus
  5.5 at high effort), 2026-10-29 08:53 PDT": the 08:53 rebuild was run by ScoreFixer-OpusHigh (score_fix_report.md
  section 6); lines 8-11 do say wave F rebuilt the file. Fix: name the rebuilder in the byline, or keep the
  RankingWriter's original time (05:4x) beside the rebuild time. Also lines 3-4 still open with "It is built from the
  score run of 2026-10-29 05:40:30 PDT (… score32b_out.json …)" while score32b_out.json is now the 08:51:03 run; the
  same paragraph explains this, so it is a wording overlap, not an error. The file names neither score output's sha256
  (ee74c6a0 / 70809d50); the recommendations file does (lines 1069-1070, 1082-1083).
- **N4. "2026-06-17 onward" boundary (addendum check).** The owned micro ohlcv-1m stores (MNQ, M2K, MYM) run
  2025-04-01 to `end_exclusive` 2026-06-21 (B/F2_data_access.json codes.MNQ/RTY/YM.owned), and the Stage E screens'
  research windows ended 2026-06-17 (B/R1_closed_lines.md:32, 39, 52: "research window 2025-04-01..2026-06-17, 299
  trade dates"). So "2026-06-17 onward" is unread only if that window end is exclusive, and the recommendations' 4.7(a)
  table ("2026-06-17 onward not owned", line 834; the 4.7(c) row :899 "not owned | ohlcv-1m | YM, NQ, RTY | 2026-06-17
  onward"; draft_sections.md:504, 569) overstates by about two trade dates:
  bars to 2026-06-20 are owned, unread. Wording only; no number depends on it. Fix (lead's call): "after the Stage E
  research windows (2026-06-17; owned bars run to 2026-06-20)".
- **N5. "one-day sigma" label in 4.7(a).** reports/stage_e32b_recommendations.md:847 and :915: "at rho 0.5 their one-day
  sigma is USD 544.45 (from USD 316.17, 73.55 and 258.76)". The arithmetic is right (sqrt of the sum of variances plus
  2 x 0.5 x the three cross products = 544.45; MNQ + RTY alone 302.32; MLL ratios 3.67 and 6.62), but the inputs are
  sigma_30 x v per member (one 30-minute trade a day), so the figure is the daily P&L sigma of the pooled strategy at
  one lot each, not the products' one-day price sigma. Fix: "their combined daily P&L sigma at one lot each".
- **N6. LR-Q3b strings omit E.12's MBT lead.** RULINGS.md:86-92 and the Q3 reason strings in R2_combinations.json
  (C112-C116, C138-C139) list "NQ, ZN, 6E, CL, GC, ZC"; E.12 also had g17_mbt live 2024-01-02..2024-02-29
  (reports/stage_e12_phase1_bars.json roots.MBT.first_trade_date 2024-01-02; gate0 rows gate0A_g17_mbt_h60/h120 at
  stage_e12_gate0.md:164, 228). R1Fixer reported this (r1fix_report.md section 4) and the lead recorded it in the
  "LR-Q3b detail" (RULINGS.md:93-95) and in the lead text; the ruling is unaffected. No fix needed beyond the detail
  already written.
- **N7. "same inputs" in the ranking header.** reports/stage_e32b_ranking.md:8-9 says the 08:51:03 rerun used "the same
  inputs"; econ32b.json's hash differs (0567890e -> e5673466, rewritten 07:27:59 by pass 2's collect). Line 18 states
  the rewrite. I could not diff the two econ files (the 0567890e version is not on disk), but the identity of every S,
  E, m*, m10K and limit-case cost in 235 pairs between run 2 and run 3 shows the blocks the scorer reads were
  unchanged. Fix: "the same inputs (econ32b.json rewritten in between by pass 2, with the blocks the scorer reads
  unchanged)".

## Checks performed

Brief item 1 (RV1 S1-S3, N1-N2):
- Scorer: B/work/score/s32b_layer2.py:42-45 `e_score` reads `block.get("cost_per_attempt_mkt_mu0")` for the tie-break
  cost and :49-51 `cost_lim` returns the limit case; :161-164 `pair_row` writes both (`cost_per_attempt` = market,
  `cost_per_attempt_lim` = limit). score32b.py:110 adds `unconfirmed_searches(econ)` to the checks, :114-141 scans
  every block with a `search` record (nested E_dir.<h> included, `inputs` excluded), :315-317 scans ruling patches.
  rank_key (:171-176) unchanged.
- Tests: `uv run pytest -q reports/stage_e32b_briefs/work/score/` -> 178 passed in 0.39 s.
- Run 2 vs run 3 (verify/diff_runs.py, my own recursive diff): 20,275 vs 20,513 leaf paths; 238 new paths (230
  `cost_per_attempt_lim`, 8 input_checks), 35 changed (33 `cost_per_attempt`, `generated_pdt`, the econ sha256); 0
  changed outside those fields. 235 pairs in the same order with no mismatch in S, S_rounded, L1, L2, E, R, A, D, Rel,
  P, m_star, m10K, status, gate_reasons, rank, econ_block, room_a, room_b; layer1, ties, top15, MNQ_ranks, n_ranked,
  L1_below_2, f5_handoff equal; all 28 variants identical. Run 2's cost equals run 3's `cost_per_attempt_lim` on all
  103 ranked pairs; the market value differs on 31. The two cost-decided ties keep their order under either value:
  tradeify|M6A 95.833 (market = limit) over topstep|M6A 98.817 market / 202.801 limit at ranks 94/95; tradeify|M6E
  95.833 over topstep|M6E 98.347 / 206.893 at 101/102 (S 2dp 2.11 and 1.95).
- Hashes: econ32b.json e56734663dd7ef08…, score32b_out.json ee74c6a0aa508ae9…, run2 70809d501bf316c1…; the score
  output's inputs record names econ e5673466; ranking.md mentions e5673466 once (line 18) and 0567890e once (named as
  the 05:40:30 run's), "05678907" 0 times (N2 fixed).
- Table 3a (ranking.md:264) has the two columns "tie-break cost/attempt USD (market case)" and "cost/attempt USD
  (limit case, reported)"; Topstep YM row (:270) shows 49 / 50 (49.03 market, 49.71 limit). Notes :255-263 state the
  market-case rule, both tie values and the S3 econ note.
- S2 sentence (ranking.md:65-68): ETH ADV 19,000 x multiplier 50 = 950,000 ETH a day against MBT 6,678 x 0.1 = 667.8 BTC
  a day (F4_facts_unmasked.json codes.ETH/MBT), ratio 1,423, so ETH's USD notional exceeds MBT's unless one ETH is worth
  less than 1/1,423 of one BTC; the sentence ("crypto's c is 0 throughout and undetermined; ETH … very probably holds
  the family's largest notional ADV"; the known-notional statement for metals, crude, grains, rates) is true.
- S3 (verify/econ_confirmed.py): 762 search records in econ32b.json, 8 with confirmed false, all bulenox|CL and
  bulenox|NG x primary/spread1 x mu_star_mkt/mu10K_mkt, k_bisection null, recorded 1.76 and 2.44 (first violations at
  grid indices 176 and 244), 1301-1302 / 1184 violations of 1339 checked; 0 unconfirmed in any E_dir block. E.28
  regression (work/econ/REGRESSION.md): bulenox|CL and |NG mu* 1.76, mu10K 1.44 + 1 = 2.44: equal. E 3.2848 (rank 27)
  and 3.2694 (rank 28) in the score output. The 8 input_checks entries match my list exactly; ranking.md:260-263 and
  work/econ/README.md:185-189 (dated note under line 184, line 184 itself unchanged) state it.
- N1 (verify/means_n1.py): means over the 103 ranked pairs, half-up at 2 dp: D1 2.86 (2.8617), D2 1.14, D3 3.50
  (3.5049), D4 2.54, D5 2.93, D6 2.71, E 2.08, R 3.97, A 2.25, D 2.78, Rel 2.77, P 1.45, S 2.58: all 13 equal
  ranking.md:569.
- Follow-up items: SCHEMA.md:90-100 dated note, README.md:8 "178 since session 4" and :17-18 LR-ATT line present.

Brief item 2 (RV2 B1 text, S6):
- G17 facts against the frozen code (git log: 9466f2e "ML route v2 freeze", b714751 "C1b freeze", 2237731 "Stage E.20
  pattern search"; `git status` clean for ml_route_v2, pattern_search, c1_replication): generic.py:22-25 definition
  ("the 60-minute log return (x 1e4) of each other cluster's lead price path and of MES … the row's own cluster lead is
  not applicable"); :343 `own_cluster = …`, :351-352 `ok &= view.cluster != own_cluster`; :390-392 one `g17_<lead>`
  per CLUSTER_LEADS value plus SIGNAL_ONLY_ROOTS; ml_route_v2/constants.py:36-38 CLUSTER_LEADS K1 NQ, K2 ZN, K3 6E, K4
  CL, K5 GC, K6 ZC, K7 MBT, SIGNAL_ONLY_ROOTS ("MES",); :23 "M2K": ("K1", "RTY"), :31 "ZL": ("K6", "ZL"); :44 HORIZONS
  h60, h120, hF; :50 equity (09:00, 11:00, 13:00), :57 grains (09:00, 10:00, 11:00). c1_replication/c1b.py:53-54 "which
  G17 never applies on its own cluster's rows". pattern_search/constants.py:59 the six g17 names in KEPT_SIGNALS, :66
  FEATURE_NAMES 36, :17-23 M2K -> RTY and ZL in the 17 vehicles, :30-31 window 2019-05-06..2024-02-29.
  reports/stage_e20_search_freeze.json feature_names: 36 names, g17_nq..g17_zc at positions 29-34 (1-based), then
  rod_ret, rod_absratio. stage_e12_gate0.md:158-164 gate0A_g17_{nq,zn,6e,cl,gc,zc,mbt}_h60, :222-228 at h120; no
  g17_mes row (0 matches); 64 distinct gate0A_*_h60 signals; 27 distinct gate0B_*_h60 products (no MBT row), so the
  "27 products" and "64 signals" statements hold. stage_e12_rulings.md:49 P-1a (g17_mes excluded). stage_e12_phase1_bars
  roots.MBT.first_trade_date 2024-01-02. stage_e20_plan.md:28 "No K7 vehicle (MBT) and no MES. One pooled model per
  horizon over the 17 vehicles", :81-82 t4 = F_X - 60 (14:08 CT equity; 12:18 grains), :138 g17_mbt and g17_mes
  dropped. E.29_RETURN.md:134-148 pairs CL-ZM, CL-GC, CL-NQ, ZM-GC, ZM-NQ, GC-NQ only. Live leads therefore RTY/M2K:
  ZN, 6E, CL, GC, ZC (+ MBT two months in E.12); ZL: NQ, ZN, 6E, CL, GC (+ MBT in E.12). All of R1Fixer's F1-F6 and the
  F3 addendum's corrections to RV2 (no MES in E.12; MBT two months; Family B one pooled ridge per horizon) are right.
- R1 files: R1_closed_lines.json loads; flat diff against work/fix4/r1/R1_closed_lines.json.before: 0 removed, 0
  changed, 2 added (/lines/10/cross_market_features, /lines/14/cross_market_features = R1-11, R1-15); sum n_trials 838,
  n_total 838, trials_by_line sum 838. R1_closed_lines.md: 0 lines removed, 2 added. R2_Q_ratings.md: 0 removed, 11
  added (the errata block, lines 3-13; no rating line changed). R2_dossiers.md: 28 lines inserted at 15-42 (errata
  items 4-7) and the two catalog rows (now :2466, :2469) extended with their originals as exact prefixes
  (difflib: prefix kept = True for both); nothing else changed.
- R2_dossiers_for_rating.md mtime 2026-10-29 05:58:24 PDT (before 06:01); sha256 dc7db33e1b71bb09… as reported.

Brief item 3 (LR-Q3b):
- verify/q3_diff.py: B/R2_combinations.json vs work/R2/R2_combinations_q3bleg.json differ only in lead_patch_v2
  (mode, q3b_to_1, rulings) and, for exactly C112, C113, C114, C115, C116, C138, C139, in Q3 (value 1, reason
  "LR-Q3b: …") with Q3_rater (value 2, the rater's reason) added. No other Q3 or field differs. Primary lead_patch_v2:
  q3_gated 13, q3b_to_1 7, v31_q7 98; q3bleg: q3b_to_1 0.
- verify/r3_recompute.py (my own implementation of spec 8.3: Q4-Q7 bands, K_eff = K_total / (1 + (m - 1) rho) with
  rho 0.5 within a class, Q6 prop and own-broker rules with the USD 6,000 (u) ceiling, Q7 cost and window rules, C
  weights, the tie order C 2dp / Q1 / G(h_c) / code / venue / family, R4 = top 5 distinct (name, family), best
  own-broker; the two readings the spec leaves open are taken as r3 did: a pool's Q4 from its worst member, G(h_c) as
  the members' maximum): for all six runs the input file's sha256 equals the r3 output's recorded input; 0 Q/C/status
  mismatches over 185 combinations; the eligible order (159; v1 172) is identical; R4 lists, n_reaching_2 (5 in every
  run) and best own-broker identical. Primary: C140 ZL F10 topstep 2.75, C138 ZL F09 2.65, C072 MNQ F08 2.55, C021 YM
  F08 2.55, C147 EQ3 F08 2.55; own C141 2.60 (rank 3); C139 2.50 (21), C113 2.50 (18). q3bleg: C138 2.75, C140 2.75,
  C113 2.60, C072 2.55, C021 2.55; own C139 2.60 (rank 6) = the session-3 06:49 list in STATE row D3r3b (:457). q3only
  C021 2.85 first, own C141 (23); nozlw C072, C021, C147, C108, C113 2.50, own C076 2.40 (21); ts150_v2 C140, C138,
  C021, C075, C108, own C141 (3), C072 and C147 2.40; v1 C003, C021, C043, C138, C140, own C044 2.65 (22).
- Sensitivity file hashes in recommendations 3.2 (d3812c40, 08e1bf16, a3b5d54b, e84b024d, 21ccabbb, ed186d0a) equal
  the files' sha256.

Brief item 4 (lead text, verify/eq3_arith.py and reads):
- C values as above. Priors: 0.04 x 0.49 = 0.0196 (about 2%), 0.05 x 0.49 = 0.0245 (about 2.5%), 1 - (1 - 0.0196)(1 -
  0.0245) = 0.0436 (about 4%). Laplace (0 + 1) / (23 + 2) = 0.040; 17 lines with a registered outcome: 18 lines have
  n_trials > 0 and R1-17's closing is "V43 (parked), not a closing", so 17, and (0 + 1) / (17 + 2) = 1/19 = 0.0526.
- EQ3: K_eff = 3 x 870 / (1 + 2 x 0.5) = 1,305; q = 0.19362508 x sqrt(870 / 1,305) = 0.15809; q x sigma_30 (F5_holding
  topstep rows "30".sigma: YM 63.2336, MNQ 147.1039, RTY 51.7514) = 9.997, 23.256, 8.182 ticks -> 10.0 / 23.3 / 8.2;
  single-member 0.193625 x sigma = 12.244 (YM, printed 12.2), 28.483 (MNQ, 28.5), 10.020 (RTY). SR80_test 0.19362508
  from B/work/F5/SR80.json SR80.test (the brief's "B/SR80.json" is at that path).
- RTY: c_f / sigma 2.256 / 51.7514 = 0.0436 ("0.044"), n_cap 13, e80_test 2.78 ("2.8 ticks"), sigma 51.75 ("51.8");
  b_test 0.1650 at 870 dates -> 0.2964 at about 273 and power 0.05 at a true daily Sharpe 0.194 (work/R4/
  recommendations_s3.md:929-933, p7_final.py at N 846).
- C139 2.50, C141 2.60, C141 Q6 3 (margin 4,661.63 < 6,000: 0; sigma_cc 116.84 x USD 6 = 701.05 > 120: 1), c_f 2.503 vs
  Topstep ZL 2.38; ZL gross 2.38 + 1.81 = 4.19 ticks = 0.149 sigma_30 (28.10), n_cap 9; MNQ 2.40 on the Standard Path
  (r3_out_ts150_v2 C072); YM 2.85 under q3only (C021).
- F09.E06 (R2_dossiers_for_rating.md:1300): "NQ leads ES by about 9-12 min and Russell by 8-11 min; Russell leads ES by
  about 5 min" = the lead's wording. E.12 27 products and E.20 17 vehicles including M2K/RTY and ZL: see item 2.
  D2 b: 42 of 47 own ratings (F4_blind_unmasked.json: MZC, MZS, MZW, MZL, MZM 0.5 unknown), 46 of 47 as scored
  (score32b_out.json primary.layer1 D2_parts.b; NQ null). E.20 H6 "T1 gross 1.25 ticks vs 4.08 cost, t -0.53"
  (R1_closed_lines.md:103).

Brief item 5 (recommendations file, verify/lead_text.py and reads):
- All 105 non-heading lines of lead_sections.md from "## Base rates" appear verbatim; all 9 section bodies appear as
  contiguous blocks (my script's one "missing" line is the heading fragment left by the split, not text).
- Section 0 (lines 11-37): 298 words; R4 in order with C, priors ("ZL program about 4% (F10 about 2%, F09 about
  2.5%); YM F08 about 1.5% only if V31 were narrowed; MNQ F08, the EQ3 pool and RTY F09 under 1%"), K0-K4, the stop
  rule with no fallback, D1-D4: all agree with the lead text and r3_out.json; no "about 1.5% each", no RTY fallback.
- 4.0 table ranks 1, 2, 4, 5, 12, own 3 = r3_out.json; tie text G(h_c) 0.0805 (MNQ) < 0.0894 (YM), C147 0.0973 (RTY's)
  recomputed; 3.2 table = the six r3 outputs (R4 lists, own-broker ranks 3/23/21/3/6/22, reach 2.00 = 5).
- 4.7(a) EQ3 table: pooled e80 10.00 / 23.26 / 8.18 ticks (USD 49.98 / 11.63 / 40.91), c_f + e80 12.25 / 27.20 /
  10.44, Standard Path sqrt(n/day) sigma_30 v 316.17 / 73.55 / 258.76, MLL ratios 6.33 / 27.19 / 7.73, K_total 2,610,
  K_eff 1,305, q 0.1581; two-member pool K_total 1,740, K_eff 1,160, q 0.1677, e80 24.67 / 8.68, 273-date K_eff 364:
  all reproduce. 5.1 C141 table: Q 2/2/2/2/3/3/4, C 2.60 rank 3, c_f 2.503, Q6 deductions as above, e80_test 1.81.
- Appendix overlap text (lines 1144-1146) names the live leads ZN, 6E, CL, GC, ZC on M2K/RTY, NQ never applied, E.20's
  decision times 09:00, 11:00, 13:00 and t4 14:08 CT; L11 (lines 442-456) states the facts and LR-Q3b; LR-OF split
  present (:586 "Other families: R1-08 CP ports …; for F10 also R1-11 and R1-15"; :462).
- Grep counts (recommendations / ranking / scope / draft v3): "12.3 ticks", "not a small-cap lag", "priors of 1.5-4%",
  "about 1.5% each", "final build only if", "no cross-market configuration", "measured no correlation", "late-session",
  "E.12 also MES", "05678907": all 0 / 0 / 0 / 0. Both score hashes in section 8 (:1069-1070, :1082-1083); q3bleg
  named 17 times.
- Addendum: the six replacements: old text 0 in lead_sections.md and recommendations.md, 1 in each pre-edit copy
  (lead_sections_s4a.md, work/fix4/recs/recommendations_pre_s4fix.md); new text 1 in each live file, 0 in the copies.
  MNQ read windows (F2_data_access.json codes.MNQ.read_windows): r002-E16, r006-E21, r005-E20S, r003-C1b, r008-E23 =
  "E.16, E.20, E.21, C1b and E.23". 2024-03-01..2025-03-31 = 13 months, about 273 trade dates. E.12 MBT lead: item 2.
  Pooled-power interpolation: pooled per-date Sharpe at rho 0.5 for two members = sqrt(2 / 1.5) = 1.155 x a member's;
  0.194 -> 0.224; recommendations_s3.md:931-933 gives power 0.05 at 0.194 and 0.23 at 0.25 at about 273 dates, so
  about 0.15 by linear interpolation: "far below 80% even pooled" holds. patch_v31_q3_lead.py: diff against .s3.py is
  the docstring, the q3bleg output path, `mode != "q3bleg"` on the Q3b rule, q3bleg added to the V31 list and the
  rulings list: the docstring now matches the code.

Brief item 6 (scope file, verify/edir_table.py):
- S5: gross_detect_test at 30 over the 15 pairs: min 4.194 (topstep|ZL), max 13.200 (mffu|MNQ) -> "4.2-13.2" at
  reports/stage_e32b_holding_scope.md:1357 and the summary. Line 331's "3.3-13.2" is over band members (min 3.285,
  topstep|ZL at 15) and its e80 range 0.9-7.9 (ZL at 15; MNQ at 30) also reproduces.
- E_dir table (:1289-1303): 15 rows x 5 cells (T, E_dir60 with cap, E_dir30, E_dir120, E_dir240; mu*_mkt and mu10K_mkt
  at 2 dp, m* and m10K at 3 dp, "u (>cap)" where above_cap is set and the value null) against econ32b.json pairs.<k>.
  E_dir60 and .E_dir.{30,120,240}: 75 cells, 0 mismatches; cap = max(4, ceil(0.30 sigma_60)) holds for all 15.
- Lead's reading: m10K lowest at 30 (strictly) and non-decreasing in h in 15/15; mu10K above cap at 120 for 4 pairs
  (bulenox|YM, mffu|MNQ, lucid|MNQ, mffu|MYM) and at 240 for 14 (all but topstep|YM); m* lower at 240 than at 30 in
  8/15; exactly 9 zero mu*_mkt cells (topstep|YM and topstep|RTY at 60, 120, 240; tradeify|YM, tradeify|RTY and
  topstep|ZL at 240); mffu|MYM above cap from 60 up; 0 unconfirmed E_dir searches. Summary bullet (:43-47) agrees.
- No PENDING, PLACEHOLDER, "still running" or TODO in the scope, ranking or recommendations files. Scope file 1,384
  lines; diff against work/scope/scope_out_s3_0728.md: 33 lines in 6 regions (43; 1277; 1283-1285 removed;
  1304-1308; 1348; the generated line 1375), as STATE L11 says.

Brief item 7 (process):
- verify/script_reads.py over the 16 scripts run or edited in session 4 (diff_score.py, build_draft_v3.py,
  assemble_s4.py, fix_lead_text_s4.py, patch_v31_q3_lead.py, build_scope.py, score32b.py, s32b_layer2.py, r3_score.py,
  make_rankmd.py, extra_frags.py, assemble.py, make_cost.py, make_fixture.py, dry_run.py, quote_checks.py) plus the
  .py files under work/ modified after 08:40: every path they open is a stage JSON/markdown file, a template, the
  frozen E.32 protocol and seal reports (assemble_s4.py, read-only), or the session transcripts (make_cost.py). None
  opens data/, a parquet, dbn, bar or MBO file, a ledger, an outcome or the holdout; the regex hits are comments and
  field names ("mbo_start", "no market data").
- Holdout: `uv run python -m data.holdout status` at 09:23:22 and 09:36:39 PDT: unlocks_logged 0, unlock_log_ok true,
  all_ok true.

## Could not check

- The 0567890e version of econ32b.json is not on disk, so I could not diff the two econ files directly; the identity
  of every score, E, m*, m10K and limit-case cost across 235 pairs between run 2 and run 3 is the evidence that the
  blocks the scorer reads did not change (N7).
- ScoreFixer's "red check" (the 5 new tests failing on the pre-fix code) and the fixture rerun's 57 changed paths were
  not rerun; the current suite (178 passed) and the pre-edit copies in work/fix4/score/ were checked instead.
- The DelegationTabler (F6) and CostTabler (F5) outputs are outside the F4 brief and were not checked.
- Whether "2026-06-17" is the inclusive or exclusive end of the Stage E research windows (N4) would need the E.3/E.4
  reports; I read only R1_closed_lines.md and F2_data_access.json.
- The pooled-power figure (about 0.15) is an interpolation of two p7_final.py outputs recorded in the session-3 Lead
  check, as the RecsAssembler said; p7_final.py was not rerun.

## Scripts (B/work/fix4/verify/)

diff_runs.py (run 2 vs run 3), means_n1.py (RV1 N1), econ_confirmed.py (RV1 S3, N2, hashes), edir_table.py (scope
section 4), r3_recompute.py (spec 8.3 recomputation, six runs), q3_diff.py (LR-Q3b patch), eq3_arith.py (EQ3, F5, base
rates, crypto notional), lead_text.py (verbatim check, six replacements, grep counts), script_reads.py (what the
session-4 scripts read). Run with `uv run python -I <script>` from the repo root; each prints summaries and mismatches
only.
