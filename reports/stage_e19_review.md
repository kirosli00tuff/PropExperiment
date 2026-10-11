# Stage E.19 econ review (EconReviewer-FableXHigh, Task 5b)

Brief: reports/stage_e19_briefs/brief_econ_review.md. Phase A (blind) ran 17:43-17:59 PDT on 2026-10-10;
recompute.json carries the `date` stamp `Sat Oct 10 05:54:29 PM PDT 2026` and was written at 17:57:25, when
reports/stage_e19_results.json did not yet exist (checked 17:59:04). Phase B ran 19:27-19:45 PDT after the lead's
message. Everything I wrote is under reports/stage_e19_verify/ (code, logs, JSON) plus this file. Nothing under
prop_econ/, tests/ or any reviewed file was modified.

Grades: BLOCKING = changes a headline number, the zero-edge sign, the break-even edge, the best account size or
path, or a recommendation. SHOULD FIX = a stated number or its interpretation is wrong or misleading without
changing those. NOTE = information for the lead.

## 1. Findings

| id | grade | area | finding | evidence | suggested fix |
|---|---|---|---|---|---|
| ER-1 | SHOULD FIX | statistics (grid.py `_mean_se`, report T1-T7, derived SEs) | The reported Monte Carlo SE of every cycle metric (net mean, its SE, "sens - twin (SE)", the optimum's SE) conditions on the 20,000-path attempt and XFA pools: 20,000 cycles are resampled from a fixed pool, so the pool's own sampling error (P(pass) has a binomial relative SE of 1.1-1.8%, and purchases scale with 1/P(pass)) is omitted. Delta method at f 0.25: total/within = 1.30 (50K zero), 2.07 (100K zero), 2.46 (150K zero), 1.0-1.3 at S 0.5; a three-seed rerun of my simulator (pools redrawn) gives 2.1 (50K), 2.9 (100K), 3.4 (150K) with large sampling error on 3 seeds. | verify/spread.md, verify/spread.json; the delta-method lines in this file section 3; the per-path equality in verify/crosscheck.json shows the differences are pool noise, not model | State that SEs are conditional on the pools, or add the pool component (delta method on P(pass) and mean length, or a pool bootstrap). No sign, ranking, break-even or best-f changes: the band zero-edge nets stay >= 26 total SE below zero; the paired f-gaps share the pools and are little affected. T5 z-scores (unpaired, within-SE) are overstated by the same factor. |
| ER-2 | SHOULD FIX | churn label (report.add_churn, L-19, Q20) | The metric is computed exactly as defined (max error 0.0 over 4,464 records: 21 x mean purchases / mean Combine-phase days, ratios of means). But it cannot discriminate inside the band: a purchase happens once per 21-day rebill, and credits pay most resets, so the rate has a floor near 0.8-1.0 and reaches 1.9 only at f 0.50. It also omits credit resets, which Topstep's clause counts ("Excessive Resets and Trading Combine purchases"). A reset-inclusive per-account rate (start + rebills + every reset) runs 1.02-2.15 per 21 Combine-phase days (> 2.0 in 1.6% of records, all at f >= 0.35; none in the band). The 5-account first-year rate is 4.0-4.9 purchases per 21 days in the band and 6.8-7.7 at f 0.50. | verify/results_checks.json `churn`; T8 columns "Combine breaches/21 d" (0.07-1.44) and "5-slot purch/21 d" | Keep the label but state its floor; judge "excessive" on the reset-inclusive per-account rate (resets = Combine breaches + timeouts) and the 5-account rate, both already in the records; the medium/high thresholds (2.0 / 4.0) never bind on the current metric, so "best f restricted to low" always equals the unrestricted best f (Q20). Under the per-account reading the labels do not change. |
| ER-3 | NOTE | T5 SEs (Q3) | "sens - twin (SE)" uses sqrt(se1^2 + se2^2) even where both sides are the same draws: ccons_inclusive rows read "0 (62)" for a difference that is exactly 0 by construction (strict vs inclusive is measure-zero); keep_d and call-up rows are paired draws with unpaired SEs. | T5 ccons_inclusive rows; grid_questions Q3 | Mark shared-seed rows as paired or report the paired SE from the saved nets. |
| ER-4 | NOTE | zero-edge sign (verdict input) | Within the policy band the zero-edge cycle net is negative in every one of the 1,500 zero-edge records (all families, pricings, DLL, B2F); the least negative is 50K standard zero_k1 f 0.25: -250 (7 within, ~9 total). Positive zero-edge nets exist only at the diagnostic f 0.50 with the DLL on (50K standard +27 / +34 with B2F; 100K standard B2F +0.3) and, ex-API only, in integer-NQ 50K consistency at every band f (+21..+67) and at f 0.35/0.50. The S0 edge (zero drift, costs removed) is about 0 at 50K f 0.25 (-8 +- 9 standard, +3 +- 10 consistency) and positive at f >= 0.35; so the negative sign at zero edge is carried by the cost drag (effective net Sharpe -0.45..-0.52 for k = 1, -1.2..-1.6 for k = 3) plus the API fee, not by the fee structure alone. | verify/results_checks.json `zero_edge_sign`, `S0_costless_zero_drift`; T3 effective Sharpe | Word the verdict as "negative at zero edge inside the policy band under D8 costs (the most cost-favourable reading, L-3); the structure itself is near fair at 50K f 0.25 and user-favourable above the band". |
| ER-5 | NOTE | optimum f (verdict input) | Standard path: the cycle net rises with f through the band in every headline group and keeps rising at 0.35 and 0.50 (f0.50 > f0.25 in all standard-path cells, by >= 3 paired SE in 144/192 cells overall); best of all seven f is 0.50 in 120/192 and 0.35 in 41/192. Consistency path: the optimum is interior once the edge is positive: band argmax 0.20 or 0.15 in 16/192 headline groups (all consistency, S >= 0.5) and f0.50 < f0.25 in 42 cells (all consistency, every size, S0..S1). The 40% best-day rule refuses payouts when a single day is large relative to the window, which higher f makes more frequent. | verify/results_checks.json `optimum_band_pattern`, `diagnostic_f`; T6, T7 | Report the two paths separately: "rising to the band edge and beyond" is a standard-path statement; on the consistency path the band optimum is 0.20-0.25 and the diagnostic f lose. |
| ER-6 | NOTE | conventions the spec left open | My eight independent readings (verify/recompute.json `conventions` C1-C8) all match the code: a reset day is traded by the next attempt; a rebill due on the pass day is paid; a rebill due on a reset day is paid first and its credit pays the reset; no reset after the 60th fail; API periods = ceil(cycle days / 21); Combine consistency strict, XFA consistency inclusive; a request needs amount >= $125 else the window keeps accumulating. | hand paths B1-B4; crosscheck exact equality | Write them into the results' assumptions list (they are only in code comments and funnel_questions.md). |
| ER-7 | NOTE | returns (D8 round trips) | For GC, ZN and 6E the D8 table's `day_session` flag covers 11/14 buckets while 10/13 lie inside the D6 window: one edge bucket straddles the window boundary. The summary follows the table's own flag and reproduces its headline means exactly; effect < 0.1% of the round trip. | verify/er_returns_check.json `d8_rt` | None needed; mention if the RT definition is quoted. |
| ER-8 | NOTE | grid.py `_attempt_pools` | The pool cache key is (f, dll, ccons_inclusive) without the edge; correct only because `group_tasks` groups jobs by (shock config, size, edge). | grid.py 557-575, 206-212 | Add the edge to the key (defensive, no result change). |
| ER-9 | NOTE | day indexing | `payout_days` / `first_payout_day` are 0-based start-of-day indices; `end_day` and cycle `end` are elapsed-day counts. Assembly is consistent (cash at start + index, end at start + end_day), so "days to first payout" means trading days traded before the request. | hand path A2 (payout at index 5 after 5 traded days; end_day 7) | Say "traded days before the first request" in the tables. |
| ER-10 | NOTE | seeds (Q1) | The cost model is in the shock seed, so cost_wall is unpaired with its d8 twin; the T5 unpaired SE is then the right one for that row. Everything else the brief asked to be paired is paired (seed tests pass by reading; shock_seed excludes edge, f, dll, variant). | grid.py 215-229; tests 73-96 | None. |
| ER-11 | NOTE | zero-edge label | zero_k1 is a bot with a net Sharpe of about -0.5 (k = 3: about -1.5) once D8 costs per unit sigma are counted (T3 effective Sharpe, risk-weighted on 200 + 200 replayed rows). The gross drift is exactly 0 (demeaned close, fair-coin direction per day: returns.py draw_layout, verified in my rebuild: |mean r'| < 1e-12 $). | T3; verify/er_returns_check.json | Quote S_eff next to "zero edge" wherever the sign is discussed. |
| ER-12 | NOTE | integer sensitivities | integer_NQ and integer_ZN are f-insensitive in the band (one contract at every f <= 0.30 for a 50K Combine), so their band optimum (0.05 / 0.15) says nothing about f. | T5 integer_NQ rows; results_checks `non_0.25_groups` | Label them so in T5. |
| ER-13 | NOTE | verification coverage | Not recomputed independently in Phase B: campaigns (P50/P80), DLL-on, Back2Funded-on, keep-D, call-up, normal-tail, integer and cost-wall records, post hoc voluntary close / payout fee / copy-traded. Phase C (section 7, lead follow-up) closed the campaign, DLL-on, Back2Funded and keep-D cells the verdict cites: all agree. Still code-reviewed only: call-up, normal-tail, integer, cost-wall, post hoc items. | section 7; verify/phase_c.json | None for the cited cells. |
| ER-14 | SHOULD FIX | wording of the positive zero-edge cell (verdict item 4) | The grid's +27 (SE 11) for 50K standard, DLL on, f 0.50, zero_k1 (and +34 (16) with Back2Funded) reproduces on the same shocks (+16 (10), +37 (15)), but on independent shocks my simulator gives +2.5 (10) and -16 (15). The reported SE conditions on the pools (ER-1); with the pool component the cell is about 1 total SE from zero. Its sign is not established. | section 7, verify/phase_c.json cells 4a/4b | Describe the cell as "indistinguishable from zero", not as a positive zero-edge cell; the statement "no positive zero-edge net inside the band" stands. |

Counts: BLOCKING 0, SHOULD FIX 3 (ER-1, ER-2, ER-14), NOTE 11.

## 2. Phase A (blind)

### 2.1 Returns table (verify/er_returns.py, er_returns_check.json)

Rebuilt from the five stores with my own code: window [O_X, C_X) from screening/vehicles.py D6_SESSIONS (NQ 08:30-15:00,
CL 08:00-13:30, GC 07:20-12:30, ZN and 6E 07:20-14:00 CT), bars whose CT calendar date equals the trade date, keep rule
"bars at exactly O_X and C_X - 1 min exist and one instrument_id in the window", skip precedence as the summary states,
multipliers from tick value / tick size of the E.2a table. Every path matches reports/stage_e19_returns_summary.json:
dates kept (1205 / 1220 / 1214 / 1203 / 1222), skip counts by reason, mean removed, sigma_full (NQ 2999.104, CL
1395.804, GC 1224.601, ZN 368.057, 6E 470.188; to 1e-6), skew, excess kurtosis, w mean and p01 (to 1e-9). The
demeaned close has |mean| < 1.2e-13 $ on every path; w <= min(0, z) holds on every row, long and short (0 violations).
D8 round trips for all nine vehicles match the summary and the table's `headline_day_session` means to 1e-9 (ER-7 on
the bucket flag).

### 2.2 Independent simulator (verify/er_sim.py, recompute.json)

Numpy only, no prop_econ import; own 5-day block bootstrap (seeds 7190001 attempts, 7190002 XFAs, 7190003 cycles),
20,000 attempts, 20,000 XFAs and 20,000 cycles per configuration, common random numbers across f, edge, size and path;
176 s single process at nice 10. Conventions C1-C8 recorded in the JSON (ER-6). Headline at f 0.25 (zero_k1 /
S 0.5 cycle mean net, API included): 50K standard -252 / +274, 50K consistency -291 / +398, 100K standard -1,137 / -58,
100K consistency -1,180 / +196, 150K standard -2,804 / -741, 150K consistency -2,832 / -206. Best band f = 0.25 in all
12 (size, path, edge) cells; the zero-edge net is negative at every band f.

### 2.3 Hand paths (verify/er_hand.py, hand_paths.json, hand_paths.log)

Eleven deterministic paths against prop_econ's scalar reference with the FINAL 50K rules and a hand product (sigma
1000 / 100, RT 10 / 2): a Combine pass (A1); a payout then a breach (A2: payout 490.00 at index 5, floor 0 after it,
n = 1 contract minimum, breach at -458.00); fee terms (B0); fail-rebill-credit-reset-pass (B1: fees (0, 49), (21, 49),
(35, 149), cash (40, 441.0), net 194.00, credit_resets 1); paid reset then rebill (B2); rebill on the reset day (B3);
the 60-attempt cap (B4: 60 purchases, no XFA); floor lock at 0 then floor 0 after a 2,000.00 payout and a breach to a
0.00 balance (C); Consistency refusal on three successive mornings then breach (D); Consistency acceptance (E: 294.00);
the same three days refused on the standard path (E2). All 11 pass to the cent and to the day.

## 3. Phase B comparison

### 3.1 Per-path cross-check on identical shocks (verify/er_crosscheck.py, crosscheck.json)

To separate model differences from draw noise, prop_econ's scalar reference (run_attempt / run_xfa / assemble_cycle)
and vectorized code (simulate_attempts / simulate_xfas / assemble_cycles) were run on MY ShockSet and index draws for
three configurations (50K zero_k1 f 0.25, 150K S 0.5 f 0.15, 100K zero_k1 f 0.05) and both payout paths: passed and
length equal on all 20,000 rows; n_payouts, total gross (to the cent), end_day and first payout day equal on all
20,000 XFAs; cycle net ex API, purchases and end equal on all 20,000 cycles (max |diff| 1e-11 $); the scalar reference
agrees on 1,500 rows and 400 cycles per configuration. The two simulators therefore implement the same model; every
difference in 3.2 is Monte Carlo.

### 3.2 Recomputed numbers against the grid (verify/compare.md, compare.json; spread.md)

Grid headline records: bootstrap, random, all products, d8, continuous, variant base, DLL off, pricing standard, B2F
off, API included, policy max; 20,000 paths and cycles. 60 configurations x 10 metrics with an SE = 600 rows.
z within = (mine - grid) / sqrt(se_mine^2 + se_grid^2) with the grid's own (pool-conditional) SEs; z total = (grid -
mean of my 3 seeds) / (sd across seeds x sqrt(4/3)). Excerpt at f 0.05 and f 0.25 (all 60 rows in compare.md):

| size | path | edge | f | P(pass) mine / grid (z) | cash per XFA mine / grid (z) | P(any) mine / grid (z) | cycle net mine / grid (z within) | z total (3 seeds) | P(no payout) (z) | purchases mine / grid (z within) | net per purchase mine / grid |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 50K | standard | zero_k1 | 0.05 | 0.1567 / 0.1601 (-0.9) | 377 / 384 (-0.9) | 0.574 / 0.583 (-1.8) | -1102 / -1089 (-1.0) | -0.7 | 0.426 / 0.419 (+1.4) | 19.86 / 19.67 (+1.1) | -55.5 / -55.4 |
| 50K | standard | S0.5 | 0.05 | 0.3469 / 0.3513 (-0.9) | 693 / 694 (-0.0) | 0.719 / 0.722 (-0.7) | -176 / -176 (+0.0) | -1.0 | 0.280 / 0.280 (-0.1) | 10.67 / 10.51 (+2.0) | -16.5 / -16.7 |
| 50K | consistency | zero_k1 | 0.05 | 0.1567 / 0.1601 (-0.9) | 393 / 401 (-1.0) | 0.355 / 0.360 (-1.0) | -1106 / -1092 (-1.0) | -0.7 | 0.651 / 0.643 (+1.6) | 19.86 / 19.67 (+1.1) | -55.7 / -55.5 |
| 50K | consistency | S0.5 | 0.05 | 0.3469 / 0.3513 (-0.9) | 997 / 1015 (-0.9) | 0.557 / 0.558 (-0.3) | 83 / 93 (-0.5) | -0.7 | 0.446 / 0.441 (+0.9) | 10.67 / 10.51 (+2.0) | 7.8 / 8.8 |
| 100K | standard | zero_k1 | 0.05 | 0.0748 / 0.0756 (-0.3) | 406 / 404 (+0.3) | 0.683 / 0.691 (-1.7) | -9992 / -9998 (+0.1) | -1.0 | 0.324 / 0.311 (+2.8) | 89.16 / 89.24 (-0.1) | -112.1 / -112.0 |
| 100K | standard | S0.5 | 0.05 | 0.3426 / 0.3466 (-0.8) | 728 / 725 (+0.3) | 0.838 / 0.845 (-2.0) | -2540 / -2445 (-3.6) | +0.5 | 0.165 / 0.152 (+3.5) | 27.02 / 26.09 (+4.6) | -94.0 / -93.7 |
| 100K | consistency | zero_k1 | 0.05 | 0.0748 / 0.0756 (-0.3) | 513 / 517 (-0.5) | 0.417 / 0.424 (-1.3) | -9927 / -9934 (+0.1) | -1.0 | 0.592 / 0.583 (+1.8) | 89.16 / 89.24 (-0.1) | -111.3 / -111.3 |
| 100K | consistency | S0.5 | 0.05 | 0.3426 / 0.3466 (-0.8) | 1360 / 1386 (-1.1) | 0.677 / 0.680 (-0.8) | -1975 / -1834 (-4.4) | +1.0 | 0.323 / 0.320 (+0.8) | 27.02 / 26.09 (+4.6) | -73.1 / -70.3 |
| 150K | standard | zero_k1 | 0.05 | 0.0441 / 0.0447 (-0.3) | 430 / 433 (-0.4) | 0.749 / 0.756 (-1.8) | -53165 / -52841 (-0.7) | -0.7 | 0.299 / 0.296 (+0.5) | 249.37 / 247.85 (+0.7) | -213.2 / -213.2 |
| 150K | standard | S0.5 | 0.05 | 0.3703 / 0.3751 (-1.0) | 764 / 771 (-0.5) | 0.909 / 0.909 (-0.2) | -9098 / -8811 (-3.6) | +1.4 | 0.093 / 0.091 (+0.8) | 45.25 / 43.90 (+3.7) | -201.1 / -200.7 |
| 150K | consistency | zero_k1 | 0.05 | 0.0441 / 0.0447 (-0.3) | 650 / 662 (-1.0) | 0.464 / 0.475 (-2.1) | -53017 / -52686 (-0.8) | -0.7 | 0.566 / 0.561 (+1.0) | 249.37 / 247.85 (+0.7) | -212.6 / -212.6 |
| 150K | consistency | S0.5 | 0.05 | 0.3703 / 0.3751 (-1.0) | 1757 / 1773 (-0.7) | 0.777 / 0.784 (-1.6) | -8218 / -7904 (-3.9) | +1.2 | 0.226 / 0.217 (+2.1) | 45.25 / 43.90 (+3.7) | -181.6 / -180.1 |
| 50K | standard | zero_k1 | 0.25 | 0.1719 / 0.1749 (-0.8) | 448 / 447 (+0.1) | 0.510 / 0.515 (-0.9) | -252 / -250 (-0.2) | -0.3 | 0.486 / 0.482 (+0.8) | 8.06 / 8.06 (+0.1) | -31.3 / -31.1 |
| 50K | standard | S0.5 | 0.25 | 0.3028 / 0.3070 (-0.9) | 796 / 786 (+0.6) | 0.641 / 0.639 (+0.4) | 274 / 278 (-0.2) | +0.1 | 0.358 / 0.360 (-0.3) | 5.36 / 5.33 (+0.6) | 51.2 / 52.1 |
| 50K | consistency | zero_k1 | 0.25 | 0.1719 / 0.1749 (-0.8) | 413 / 416 (-0.3) | 0.254 / 0.258 (-1.0) | -291 / -283 (-0.7) | -0.0 | 0.745 / 0.741 (+0.8) | 8.06 / 8.06 (+0.1) | -36.1 / -35.1 |
| 50K | consistency | S0.5 | 0.25 | 0.3028 / 0.3070 (-0.9) | 934 / 923 (+0.5) | 0.399 / 0.402 (-0.7) | 398 / 384 (+0.7) | -0.7 | 0.598 / 0.597 (+0.2) | 5.36 / 5.33 (+0.6) | 74.3 / 72.0 |
| 100K | standard | zero_k1 | 0.25 | 0.1242 / 0.1298 (-1.7) | 646 / 635 (+0.8) | 0.555 / 0.562 (-1.5) | -1137 / -1063 (-3.9) | +1.5 | 0.445 / 0.434 (+2.1) | 13.78 / 13.20 (+4.7) | -82.5 / -80.5 |
| 100K | standard | S0.5 | 0.25 | 0.2445 / 0.2537 (-2.1) | 1092 / 1072 (+0.9) | 0.684 / 0.691 (-1.4) | -58 / -25 (-1.3) | +0.3 | 0.313 / 0.310 (+0.5) | 8.48 / 8.12 (+4.9) | -6.8 / -3.1 |
| 100K | consistency | zero_k1 | 0.25 | 0.1242 / 0.1298 (-1.7) | 604 / 604 (+0.0) | 0.257 / 0.265 (-1.9) | -1180 / -1098 (-4.0) | +1.3 | 0.742 / 0.734 (+2.0) | 13.78 / 13.20 (+4.7) | -85.6 / -83.2 |
| 100K | consistency | S0.5 | 0.25 | 0.2445 / 0.2537 (-2.1) | 1371 / 1357 (+0.5) | 0.405 / 0.413 (-1.6) | 196 / 263 (-2.2) | +0.3 | 0.592 / 0.584 (+1.7) | 8.48 / 8.12 (+4.9) | 23.1 / 32.4 |
| 150K | standard | zero_k1 | 0.25 | 0.1234 / 0.1283 (-1.5) | 934 / 926 (+0.4) | 0.583 / 0.591 (-1.6) | -2804 / -2696 (-2.9) | +1.1 | 0.415 / 0.412 (+0.5) | 16.43 / 15.92 (+3.3) | -170.7 / -169.3 |
| 150K | standard | S0.5 | 0.25 | 0.2498 / 0.2569 (-1.6) | 1546 / 1535 (+0.4) | 0.711 / 0.715 (-0.9) | -741 / -697 (-1.3) | +0.1 | 0.283 / 0.286 (-0.6) | 9.76 / 9.50 (+2.9) | -75.9 / -73.4 |
| 150K | consistency | zero_k1 | 0.25 | 0.1234 / 0.1283 (-1.5) | 912 / 927 (-0.7) | 0.257 / 0.264 (-1.5) | -2832 / -2701 (-3.3) | +0.9 | 0.743 / 0.736 (+1.4) | 16.43 / 15.92 (+3.3) | -172.4 / -169.6 |
| 150K | consistency | S0.5 | 0.25 | 0.2498 / 0.2569 (-1.6) | 2099 / 2116 (-0.4) | 0.412 / 0.421 (-1.8) | -206 / -131 (-1.6) | +0.2 | 0.586 / 0.577 (+1.8) | 9.76 / 9.50 (+2.9) | -21.1 / -13.8 |

SEs used: P(pass), P(any payout), P(no payout): binomial on 20,000; cycle net: the grid's `net_se` and my per-cycle SE;
cash per XFA and purchases: my per-path / per-cycle SE on both sides (the grid gives none); net per purchase and the
mean lengths have no SE and agree to <= 1.5% (lengths) and to the sign everywhere.

Result: 70 of 600 rows exceed 3 combined within-SEs (purchases 32, cycle net 19, net ex API 18, P(no payout) 1; 68 of
the 70 in 100K and 150K). All are one systematic effect: my attempt pool (one shock draw shared by all 30 attempt
cells) has P(pass) 1-4% lower than the grid's in every cell (z -0.3 to -2.5, never beyond 3), so my cycles make 3-5%
more purchases and the fee-heavy 100K/150K nets are more negative. The per-path equality in 3.1 rules out a model
difference; the pool's sampling error is simply not in the within-cycle SE (ER-1). With the total spread from three
independent seeds of my simulator, the grid's cycle net is within 2.6 total SD of my three-seed mean in all 60
configurations (none beyond 3) and the sign agrees in all 60. P(pass), cash per XFA and P(any payout) agree within 2.5
binomial / within SE in every cell; the best band f is 0.25 in all 12 cells on both sides (the grid's 50K consistency
S 0.5 best f is 0.20 at 391 vs 384 at 0.25, a 7 +- 15 gap; mine has 0.25). The headline reproduces.

Derived quantities recomputed from the records and the saved per-cycle nets: break-even S for all 120 (size, path,
dll, pricing, band f) cells to 0.0; the 50K standard zero_k1 band optimum (best f 0.25, mean -250.35, SE 7.28,
runner-up 0.20, gap 201.52, paired SE 4.06) to the last digit; the npz means equal the records.

## 4. Code review against sim_spec.md and the FINAL rules

Daily step (funnel.day_step, vec.day_step_vec): D_open = B - F; s* = f D; full-size iff no micro or s* >= sigma_full;
n = s*/sigma (floor in integer mode), n >= 1, then n <= cap_minis x (1 or 10); zero edge: close = n sigma z - n k rt,
Sharpe edge: mu = sigma S/sqrt(252) + k rt so close = n sigma (z + S/sqrt(252)), net of costs (L-4); worst = n sigma w
- n k rt in both; DLL stop when worst <= -DLL and DLL < D_open - 1e-6 (L-17 tie), else MLL breach when worst <= -D_open
with P&L -D_open; else the close. Matches sections 2.1-2.8 and my simulator exactly. Tier timing: the XFA cap is read
from `close` = the prior session's close (start balance on day 1; a same-morning payout does not lower it, L-17 #2);
boundary "lower" = balance <= below takes the lower tier (tier_cap, tier_cap_vec). Combine cap = max_minis.

Combine (run_attempt, simulate_attempts): B 0, F -MLL, EOD F = max(F, min(B - MLL, mll_floor_max_rel = 0)); best day =
max daily P&L so far; pass at EOD when B >= target, best < 0.55 B (strict, per combine_consistency_inclusive false;
the inclusive reading is the ccons_inclusive variant) and days >= 2; breach = fail; 756-day timeout = fail with its
own reason. Matches section 3.

XFA (run_xfa, simulate_xfas): request at the start of the day before trading; standard: window winning days (P&L >=
150) >= 5 and (window net > 0 after the first payout, B > 0 before it); consistency: window traded days >= 3, window
net > 0, best <= 0.4 x net (inclusive per the file); amount = floor-to-cent of min(cap (cap_usd_dll when DLL chosen
and dll_doubles_payout_caps), 0.5 B, B - keep_d MLL), only if >= 125; B -= amount, user gets 0.9 x amount, F = 0 for
good after the first payout (mll_after_first_payout_usd), window restarts, the request day's P&L is excluded
(payout_day_counts_toward_next_window false); EOD trailing F = max(F, min(B - MLL, 0)) until the first payout; ends on
breach, call-up or payout limit right after the triggering payout (reason call-up when both), or the 756-day horizon
with the balance worth 0. Matches section 4 and L-17. D_open <= 0 raises (unreachable with the FINAL values).

Fees and cycles (assemble.py): P at time 0; rebills at 21-day steps from the last start or reset, strictly before an
attempt's end and inclusive on a reset day (paid before the reset, L-17); each rebill adds a credit
(rebill_adds_reset_credit); a reset uses a credit else pays R, and restarts the clock (reset_pushes_rebill); no reset
after the 60th fail; a pass ends the subscription, activation paid at the pass attempt's end time = the next trading
day, the XFA starts then; Back2Funded: after a breach before any payout (`_b2f_again` reads before_first_payout_only),
at most max_per_xfa = 2 more XFAs, fee at the breach end, DLL discount on P and B2F only (Q10, L-17); the DLL discount
is taken from the pricing path's dll_discount_monthly_usd (null on standard, so none). Vectorized `_subscriptions_vec`
/ `_emit_rebills` reproduce the scalar `_subscription` (my cross-check: exact on 20,000 cycles). Purchases = START +
REBILL + RESET events. API fee post hoc in grid.cycle_post_hoc: 14.50 x ceil(end / 21) per cycle (Q4), one per user
in campaigns (floor(t / 21) + 1 at a crossing). Split 0.9 from the file; payout fee 0 (ACH $30 post hoc); voluntary
close post hoc per L-15 (Q6). All values come from the rules file (wallet_from, fee_terms); no Topstep number is
hard-coded in prop_econ/ (grep of prop_econ/*.py for every price, target, MLL, cap, payout and fee value in the
file finds only a task-ordering weight, quantile levels and two table captions).

Campaigns (run_campaign): slots in 1..max_active_xfas enforced, each slot runs cycles back to back so at most `slots`
XFAs are live (B2F off in campaigns); events merged per replication in (time, fees before cash) order; a target is
reached at the first event where cumulative cash >= target provided cumulative purchases have not exceeded 400 by then
(purchases on the crossing day count, Q13); P50/P80 = the smallest K reached with that probability (inverted CDF, inf
when the share reached is lower); more cycles are drawn until every open replication is settled, which terminates
because every cycle adds >= 1 purchase. Reviewed by reading only (ER-13).

Common random numbers (grid.py): shock seeds depend on (base seed, phase, size, tail, direction, products, cost,
mode); cycle and campaign seeds on (kind, size, shock config); so every edge, f, DLL, variant, payout path and pricing
of a size shares shocks and index draws (tests 73-96). The cost model in the seed makes wall vs d8 unpaired (ER-10).
Attempt pools are cached per (f, dll, ccons_inclusive) inside a task that fixes the edge (ER-8).

Break-even (report.break_even): first upward crossing of the cycle mean net over S, linear interpolation; "< 0" when
positive at S0, "> 1" when negative at S1; the envelope uses the best band f at each S. Optimum (select_optimum): argmax
of the mean (ties to the smaller f), its SE from the per-cycle nets, the paired SE of the gap to the runner-up from the
per-cycle differences. Both recomputed exactly (section 3.2); the SE caveat is ER-1.

Zero gross drift: the close is demeaned per path (|mean| < 1e-12 $, my rebuild), the direction is a fair coin per path
and day (returns.draw_layout `sign`), and day_step adds no drift at the zero edge; so E[z] = 0 and the only drift is
-n k rt (ER-11). The Sharpe edge is net of costs by construction.

Churn (grid.churn_metrics, report.add_churn): Combine-phase days = the subscription's end time (the XFA start after a
pass, else the last attempt's end) = the sum of attempt lengths; Combine breaches from the attempt reasons; XFA days and
breaches from the chain; the 5-slot first-252-day count chains consecutive cycles of the batch. Rates are ratios of
means. The arithmetic is exact (ER-2 is about the definition).

## 5. Independent view on the three verdict questions

(a) Is the zero-edge negative sign robust? Inside the policy band, yes: negative in every zero-edge record of every
family (1,500 records; bootstrap and normal tails, random and long direction, d8 and wall costs, integer per product,
both DLL and pricing paths, B2F on or off, keep-D, call-ups, both UNSOURCED readings), with the least negative cell at
-250 (about 9 total SE) for 50K standard f 0.25, and the normal tail only less negative (z +1.5 to +13.6 against
bootstrap at zero_k1), so fat tails make it worse, not better. What is not robust is the attribution: the S0 edge
(zero drift with the cost drag removed) is indistinguishable from zero at 50K f 0.25 and positive above the band, and
the only positive zero-edge nets are at f 0.50 with the DLL on. So the sign inside the band rests on (i) D8 costs,
which L-3 takes as the most cost-favourable reading, (ii) the $14.50 API fee (ex-API, integer-NQ 50K consistency is
positive at every band f, +21..+67), and (iii) staying inside the band. Within those three the sign is robust; the
margin at 50K is one API subscription per cycle.

(b) Is the optimum at the top of the band, rising at 0.35 / 0.50, genuine or an artefact? Genuine within the model for
the standard payout path, and a structural property rather than noise: fees are priced per 21 trading days while a
zero-drift account resolves in a time proportional to 1/f^2, P(pass) barely falls with f (0.157 -> 0.172 at 50K), the
user's downside per cycle is capped at the fees so variance is free, and higher f trades more full-size contracts whose
cost per unit sigma is lower (effective Sharpe -0.52 -> -0.45 from f 0.05 to 0.50). The paired gaps are 20-40 paired SE
in the band and remain positive at 0.35 and 0.50 in every standard-path cell. Nothing I found in the code manufactures
the slope: the horizon and the 60-attempt cap bite at low f (making it worse), not at high f; the lot cap only cuts ZN
at 150K and the diagnostic f; liquidation at the floor is the user's view of a breach (the overshoot is the firm's). Two
qualifications. First, it is path-specific: on the consistency path the 40% best-day rule turns the curve over at
0.20-0.35 once the edge is positive (f0.50 < f0.25 in all 42 consistency cells with S >= 0; band argmax 0.20/0.15 in 16
headline groups, all consistency). Second, what the model leaves out all penalizes high f: Topstep's "excessive
resets" clause (resets per account rise from 0.07 to 1.44 per 21 days across f, ER-2), the Responsible Trading Program
when several accounts breach the same day (RR-5), and the trader's own capital at risk per month. So "rising with f"
is a true statement about the modelled payoff on the standard path, and the reason the lead's band cap and churn gate
exist; it is not a Monte Carlo or coding artefact.

(c) Is the L-19 churn metric computed correctly? The arithmetic is exact (21 x mean purchases / mean Combine-phase
days, ratio of means, over 4,464 records; max error 0.0), and Combine-phase days and purchases are what the lead
defined. The definition, however, has a floor near one purchase per 21 days (a rebill every billing period) and credits
pay most resets, so it reads 0.79-1.90 everywhere and the "low" label carries no information inside the band; it also
excludes credit resets, which the quoted clause counts. The reset-inclusive per-account rate is 1.02-2.15 (<= 2.0 at
every band f), and the 5-account first-year rate 4.0-4.9 purchases per 21 days in the band (6.8-7.7 at f 0.50). On the
per-account reading the labels stand; the lead should say which rate the threshold applies to and that the current
one cannot exceed "low" in the band by construction.

## 6. Artifacts (reports/stage_e19_verify/)

er_returns.py, er_returns_check.json, er_returns.npz, er_returns.log (Phase A item 1); er_sim.py, recompute.json
(blind, stamp 17:54:29), recompute_v2_se.json (same seeds, with SEs), recompute_seed100.json, recompute_seed200.json,
er_sim.log, er_sim_run*.out (items 2 and the spread); er_hand.py, hand_paths.json, hand_paths.log (item 3);
er_compare.py, compare.json, compare.md (3.2); er_crosscheck.py, crosscheck.json, er_crosscheck.out (3.1);
er_spread.py, spread.json, spread.md (ER-1); er_results_checks.py, results_checks.json (section 5). The `pages/`
folder and refetch_log.md in the same directory belong to RulesReviewer.

## 7. Phase C: verdict cells (lead follow-up on ER-13, 19:47-19:56 PDT)

Code: verify/er_phase_c.py (my simulator extended with the DLL in both phases, doubled payout caps with the DLL,
keep-D, Back2Funded chains, per-payout records, cycle event times and a 5-slot campaign; no prop_econ simulation code
imported), results verify/phase_c.json, log phase_c.log. Two shock sets: "same" = the grid's own attempt and XFA
ShockSets rebuilt with prop_econ.returns.build_shocks from the job seeds (7507194054930720927 / 11155556327628267487;
the pools are then identical: P(pass), cash per XFA and mean XFAs match to the digit, so only my cycle and campaign
index draws differ from the grid's); "own" = my independent shocks (seeds 7190001 / 7190002, pool-sampling error
included). 20,000 cycles, 20,000 campaign replications, 5 slots, purchase cap 400, Back2Funded off and DLL off in the
campaigns, standard pricing, API fee 14.50 x (floor(t / 21) + 1) at the crossing. SEs: quantiles by a 200-resample
bootstrap over replications (mine; the grid's taken as equal, combined = SE x sqrt 2; a quantile of an integer count
has a resolution of one purchase, so a one-purchase difference is agreement); cycle nets by the within-cycle SE on both
sides (z within). Agreement = within 3 combined SE (or one purchase).

(1) Campaigns, 50K standard path, f 0.25:

| cell | shocks | purchases P50 grid / mine | purchases P80 grid / mine | fees P50 grid / mine (SE) | fees P80 grid / mine (SE) | not reached grid / mine | agree |
|---|---|---|---|---|---|---|---|
| zero_k1, $5,000 | same | 112 / 112 | 164 / 163 | 7,918 / 7,892 (29) | 11,499 / 11,421 (47) | 0.0001 / 0.0001 | yes |
| zero_k1, $10,000 | same | 202 / 201 | 276 / 275 | 14,366 / 14,316 (45) | 19,390 / 19,309 (66) | 0.018 / 0.018 | yes |
| S0.5, $5,000 | same | 51 / 51 | 76 / 76 | 4,052 / 4,063 (17) | 5,934 / 5,934 (28) | 0 / 0 | yes |
| S0.5, $10,000 | same | 86 / 86 | 121 / 121 | 6,900 / 6,928 (27) | 9,530 / 9,554 (35) | 0 / 0 | yes |
| S1, $5,000 | same | 36 / 36 | 53 / 53 | 3,036 / 3,021 (17) | 4,409 / 4,404 (19) | 0 / 0 | yes |
| S1, $10,000 | same | 58 / 57 | 82 / 81 | 4,920 / 4,905 (18) | 6,894 / 6,832 (31) | 0 / 0 | yes |
| zero_k1, $5,000 | own | 112 / 113 | 164 / 166 | 7,918 / 7,966 (34) | 11,499 / 11,584 (46) | 0.0001 / 0.0003 | yes |
| zero_k1, $10,000 | own | 202 / 201 | 276 / 276 | 14,366 / 14,298 (52) | 19,390 / 19,456 (65) | 0.018 / 0.019 | yes |
| S0.5, $5,000 | own | 51 / 51 | 76 / 75 | 4,052 / 4,002 (16) | 5,934 / 5,873 (23) | 0 / 0 | yes |
| S0.5, $10,000 | own | 86 / 85 | 121 / 120 | 6,900 / 6,817 (24) | 9,530 / 9,478 (32) | 0 / 0 | yes |
| S1, $5,000 | own | 36 / 36 | 53 / 54 | 3,036 / 3,040 (13) | 4,409 / 4,450 (18) | 0 / 0 | yes |
| S1, $10,000 | own | 58 / 58 | 82 / 82 | 4,920 / 4,958 (18) | 6,894 / 6,888 (24) | 0 / 0 | yes |

Largest fee difference 1.3% (own shocks, zero_k1 $10,000 P80, z +0.7 on the bootstrap SE; own-shock z up to 2.5 on
fees because the pool component is not in the bootstrap SE). Days P50 for zero_k1 $5,000: grid 570, mine 568 (same)
and 573 (own). All 48 quantities agree.

(2)-(4) Cycle mean net, API included, standard pricing, 50K:

| cell | shocks | grid net (SE) | mine net (SE) | z within | P(pass) grid / mine | cash per XFA grid / mine | mean XFAs grid / mine | agree |
|---|---|---|---|---|---|---|---|---|
| (2) consistency, S0.5, DLL off, f 0.20 | same | 390.7 (15.1) | 413.9 (15.3) | +1.08 | 0.3248 / 0.3248 | 1011.7 / 1011.7 | 1.000 / 1.000 | yes |
| (2) same, Back2Funded on | same | 691.9 (19.3) | 707.0 (19.3) | +0.56 | 0.3248 / 0.3248 | 1011.7 / 1011.7 | 1.823 / 1.825 | yes |
| (2) consistency, S0.5, DLL on, f 0.25 | same | 476.5 (17.1) | 478.9 (16.8) | +0.10 | 0.3121 / 0.3121 | 1023.6 / 1023.6 | 1.000 / 1.000 | yes |
| (2) same, Back2Funded on | same | 905.5 (22.9) | 904.4 (22.5) | -0.04 | 0.3121 / 0.3121 | 1023.6 / 1023.6 | 1.944 / 1.952 | yes |
| (3) standard, S0.5, f 0.25, keep-D 0.5 | same | 486.7 (16.3) | 487.0 (17.2) | +0.01 | 0.3070 / 0.3070 | 1009.5 / 1009.5 | 1.000 / 1.000 | yes |
| (4) standard, DLL on, f 0.50, zero_k1 | same | 27.4 (11.5) | 16.3 (10.4) | -0.72 | 0.1752 / 0.1752 | 560.8 / 560.8 | 1.000 / 1.000 | yes |
| (4) same, Back2Funded on | same | 34.4 (15.7) | 36.6 (15.2) | +0.10 | 0.1752 / 0.1752 | 560.8 / 560.8 | 1.971 / 1.968 | yes |
| (2) consistency, S0.5, DLL off, f 0.20 | own | 390.7 (15.1) | 397.8 (15.4) | +0.32 | 0.3248 / 0.3174 | 1011.7 / 1004.3 | 1.000 / 1.000 | yes |
| (2) same, Back2Funded on | own | 691.9 (19.3) | 718.3 (20.2) | +0.95 | 0.3248 / 0.3174 | 1011.7 / 1004.3 | 1.823 / 1.832 | yes |
| (2) consistency, S0.5, DLL on, f 0.25 | own | 476.5 (17.1) | 481.4 (17.0) | +0.20 | 0.3121 / 0.3053 | 1023.6 / 1025.4 | 1.000 / 1.000 | yes |
| (2) same, Back2Funded on | own | 905.5 (22.9) | 919.6 (22.7) | +0.44 | 0.3121 / 0.3053 | 1023.6 / 1025.4 | 1.944 / 1.952 | yes |
| (3) standard, S0.5, f 0.25, keep-D 0.5 | own | 486.7 (16.3) | 500.4 (17.8) | +0.57 | 0.3070 / 0.3028 | 1009.5 / 1001.7 | 1.000 / 1.000 | yes |
| (4) standard, DLL on, f 0.50, zero_k1 | own | 27.4 (11.5) | 2.5 (10.3) | -1.62 | 0.1752 / 0.1668 | 560.8 / 552.1 | 1.000 / 1.000 | yes (sign: see ER-14) |
| (4) same, Back2Funded on | own | 34.4 (15.7) | -16.4 (14.5) | -2.38 | 0.1752 / 0.1668 | 560.8 / 552.1 | 1.971 / 1.981 | yes (sign: see ER-14) |

All 14 cells agree within 3 combined SE; the DLL stop, the doubled cap, keep-D, and the Back2Funded chain (fee at
the breach, fresh XFA, at most two, before the first payout only; mean XFAs 1.82-1.98) behave identically in the two
implementations on identical pools. The one qualitative point is cell (4): positive on the grid's shocks (+27 / +34,
reproduced as +16 / +37), but +2.5 (10) / -16 (15) on independent shocks; with the pool-sampling component (ER-1) the
cell is about one total SE from zero, so its sign is not established (ER-14). Nothing here changes a headline number,
the in-band zero-edge sign, the break-even edge, the best size or path, or a recommendation.
