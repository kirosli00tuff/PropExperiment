# Stage E.29 independent review (BasketReviewer, Opus 5.5, fresh context)

**Verdict: GO WITH FIXES.** Nothing is BLOCKING. Two items are SHOULD FIX: the declared grid confirmation was not run,
and the "vanishes" rho of section 7 is not produced. Both need handling in the return and the synthesis. The rest are
NOTEs.

Run 02:53 to 03:15 PDT, 2026-10-22 (times from `date`). Holdout `unlocks_logged` 0 at the start and at 03:11, state
sealed. `free -m` at the start showed 8.2 GB available; it stayed at or above 6.9 GB. Compute ran at nice 10 with
OMP/MKL/OPENBLAS threads set to 1 and at most 4 worker processes (an idle parent coordinated them). I edited nothing
outside reports/stage_e29_briefs/work/review/ and this file. The work/basket mtimes are unchanged, and nothing under
E.28's A3_econ/ or prop_econ/ is newer than E29_tables.md.

Scripts and outputs are in reports/stage_e29_briefs/work/review/:
- check_static.py writes check_static.json (tasks 3 and 4).
- pick_cells.py (task 2).
- review_run.py writes out/*.json and review_run_batch1.log / review_run_batch2.log (tasks 1, 2 and 6).
- compare_review.py writes compare_review.json and compare_review.out.
- cap_pool_plugin.py and test_e29_basket_review.out (task 5).

## Items

1. **NOTE (pass): provenance.** reports/stage_e29_model.md has sha256 f393759f…8164, equal to the declared value
   (`sha256sum`). The current sha256 of E.28's A3_funnel/A3_models/A3_run/A3_inputs/A3_gridcheck .py, A3_inputs.json
   and A3_econ.json equals E29_cells.json `e28_sha256`, and git shows these files and prop_econ/ clean. The current
   e29_basket.py and e29_run.py equal `code_sha256`. The recomputed code fingerprint equals `a86be27ee34cf681`, and
   all 235 cell files carry the fingerprint of the code now on disk (0 stale). Source: check_static.json "provenance".

2. **NOTE (pass): task 1, B0 against E.28.** I recomputed B0 setting (ii), limit and market, at all five firms with
   the E.29 code (review_run.py, tag b0, same seed, the run's bisection). Every value equals A3_econ.json exactly:
   - topstep: 0.32 / 1.32 / 0.54 / 50.532965
   - lucid: 0.33 / 1.33 / 0.77 / 120.8667
   - tradeify: 0.43 / 1.43 / 0.75 / 95.8333
   - mffu: 0.35 / 1.35 / 0.90 / 153.0
   - bulenox: 0.72 / 1.72 / 1.06 / 175.0

   (each row is mu*_lim / mu*_mkt / mu10K / cost per attempt). Every evaluation row is bit-equal to the stored
   cells/ file (compare_review.out, "b0" block: match True and bit-equal True on all 10 cells). Test (a) checks the
   same thing independently and passes (item 5).

3. **NOTE: task 2, two random cells under a different seed.**
   - Selection (pick_cells.py): `numpy.random.default_rng(20261022)` over the 156 computed non-B0 limit-primary cells,
     sorted by cell_id. Pick 1 came from the 117 cells with rho > 0, pick 2 from the remaining 155. The draws were
     limit__primary__bulenox__B3__ii__r0.25 and …__r0.75; I kept them as drawn.
   - Re-run: master seed `A3_funnel.BASE_SEED` = 20261022, which is set in a fresh worker before `build_state`, so
     the draws, cycle indices and campaign indices are all new. Row 0's first z changed from 0.1274 to -2.3328. Same
     bisection.
   - mu*_QM: r0.25 moved 2.05 to 2.04 (-1 step) and r0.75 moved 1.94 to 1.93 (-1).
   - mu10K analogue: r0.25 stayed at 2.98 (0) and r0.75 moved 3.02 to 3.01 (-1).
   - B0 bulenox (ii) under the new seed reproduces 0.72 / 1.06.
   - The "beats B0" flag is "no" in all three comparisons: stored, new cell against stored B0, and new against new B0.
   - All differences are at most 1 step, well inside the 3-step bar. Source: compare_review.json "reseed".

4. **NOTE (pass): task 3, rule mapping on the combined account.**
   - **Funnel entry point.** The combined law enters E.28's funnel through the same call as E.28's pair law:
     e29_basket.py:287 `F.simulate_pools(self.model, p, self.da, self.dx)`, then cycle_stats and campaign_p_reach,
     the same as A3_run.py:71-73. The draws come from `A3_run.build_state`, so Bulenox (needs_max) gets the e2 bridge
     maxima. The intraday min (and max) bridge, the DLL test in day_step_vec, the trailing and EOD floors,
     consistency, the payout rules, the minimum days, caps, buffers, splits, fees and API therefore all act on the
     combined daily P&L (M + S z) exactly as on one contract with (M, S), as sections 3 and 4 declare.
   - **M and S.** I recomputed both from the declaration (members built from A3_econ.json, not from A3_inputs.json)
     on all 3,755 evaluation rows of the 224 computed cells. The largest relative error is 2.8e-13 for M and 0 for S.
     S_usd and S/MLL match on all 228 cells. The inputs v, sigma_T, F_rt and c_lim, with S_rt = 1, agree between
     A3_inputs.json and A3_econ.json for all 20 firm-product pairs.
   - **T split and edge settings.** The T split (20; 10/10; 7/7/6) is correct on all cells. The mu* used in setting
     (i) matches E.28's mu*_lim, mu*_mkt or the extended alone value in all 110 setting-(i) cells. The only "n/a"
     cells are Bulenox B4 (i), because MNQ is above 12 ticks.
   - **Extended alone break-evens.** They agree with E.28: every "> 4" pair comes out above 4.00, Topstep and
     Tradeify MNQ reproduce 3.26 and 3.86, and the market value is the limit value + 1.00.
   - **Best basket and market case.** I re-implemented section 6's rule on integer indices. It picks the same baskets
     (topstep B2, lucid B4, tradeify B2, mffu B2, bulenox B3), and market cells exist for exactly these baskets at
     every rho and both settings.
   - **Topstep B3 2-lot tier.** The wrapper (e29_basket.py:165-237) matches prop_econ.vec._trade_day/simulate_xfas line
     for line except the per-day law choice (`low = cap_minis < lots`, :177, on E.19's tier_cap_vec of the previous
     close). Its law B (QM 7 + ZM 7, MGC dropped) matches section 4 at 32 checked points. Tests (e) pass.
   - **Caps and news window.** Firm caps, the product caps (Topstep QM 3, MGC 30; MFFU MGC 5) and the news window
     are logged in E29_tables.md "Binding-limit log" as checked and non-binding, as declared.
   - **Reporting points, cost per attempt and zero-edge stats.** The reporting points are g = 100/150/200 in (i) and
     E.28 mu*_lim, 50, 100 in (ii). Cost per attempt is identical in (i) and (ii) on all 85 firm-basket-rho pairs.
     The zero-edge stats come from the g = 0 evaluation.

5. **NOTE (pass): task 5, tests.** I ran `PYTHONPATH=…/work/review OMP_NUM_THREADS=1 … nice -n 10 uv run pytest -q
   -p no:cacheprovider -p cap_pool_plugin reports/stage_e29_briefs/work/basket/test_e29_basket.py` and got
   **11 passed in 70.59s**, rc 0 (test_e29_basket_review.out). The plugin only caps the fixture's Pool(5) at 4
   processes (the review's limit); it changes no test logic.

6. **NOTE (pass): task 4, tables against JSON.** check_static.py parses every row of the five per-firm tables and
   compares it with E29_cells.json:
   - 994 numbers in the main tables (S, S/MLL, threshold, vs B0, x10K, cost per attempt) and 1,494 in the reporting
     tables (pass rate, P(payout), EV): 0 mismatches.
   - I also read the B0-check, best-basket, market, alone and sensitivity sections against the JSON by eye; they
     agree.
   - All 160 "beats B0" flags, re-derived on integer grid indices with section 7's rule (threshold at least 2 steps
     below B0 and x10K index not above B0's): 0 mismatches.
   - 27 flags are "yes": Bulenox B1/B2/B3 (i), Topstep B2/B3 (i) and Tradeify B2/B3 (i). No "yes" occurs in
     setting (ii).
   - No cell has both its own and B0's x10K above 4, so the "> 4 vs > 4" edge of the rule never arises.
   - The e29_tables.py:72 float guard (`t < tb - 0.01 - 1e-9`) gives the same flags as the integer rule.

7. **SHOULD FIX: the declared grid confirmation was not run (LOG.md C3).** Declaration sections 1 and 6 call for
   "bisection plus grid confirmation" as in A3_econ.md 2.4. Every one of the 224 thresholds and the 7 alone
   break-evens is "bisection, unconfirmed".

   Task 6 sample (review_run.py tag confirm, `mode: "confirmed"`, e29_basket.grid_confirm, same CRN):
   - The 10 cells requested: each firm's best basket, setting (i), limit, rho 0.25 and 0.5.
   - 11 more: B0 (i) at all five firms (the comparator of every setting-(i) flag), and the best-basket runners-up at
     rho 0.5 with the thinnest margins (lucid B2 (i), lucid B4/B2 (ii), mffu B4/B3 (i), bulenox B1 (i)).
   - Results: **no threshold moved** in any of the 21 cells (k*, mu*_QM, k10K and mu10K: 0 violations on 15 to 21 EV
     points and 32 to 53 P10K points each). The bisection reproduced the stored g exactly, and the from-scratch
     recomputation was equal in every cell.
   - The extended alone MGC break-evens at Topstep (6.37 / 7.37), Tradeify (6.34 / 7.34) and Bulenox (8.30 / 9.30),
     which set the k units of the three best baskets that hold MGC, also confirm unchanged (0 violations on 74 to 103
     points).
   - Source: compare_review.json "confirm" and "alone".

   Confirmation can only lower a threshold (A3 2.4 replaces it with a smaller grid point). B0 (i) and B0's x10K are
   now confirmed. So **all 27 "yes" flags survive confirmation**, and only "no" flags could flip. The exposed ones are
   mffu B3 (i) at rho 0, 0.25 and 0.75 (k* 0.99 against B0 1.00, x10K already at or below 2.56): one step down flips
   each to "yes". Mffu B3 (i) at rho 0.5 is confirmed at 0.99.

   Remaining best-basket risk sits in unconfirmed runners-up:
   - lucid B3 (i) 0.97 would need 2 steps to take over from B4 at 0.96;
   - bulenox B2 (i) 0.96 would need 3 steps to tie B3 at 0.93, and would then win on (ii) 1.32 < 1.99.

   Fix: the return states this as a deviation from the declaration, keeps the "bisection, unconfirmed" label, and
   cites this sample, or the confirmation is run on the cells that carry the answers.

8. **SHOULD FIX: section 7's "vanishes" rho is not produced, and is ill-defined where the benefit grows with rho.**
   E29_tables.md and e29_tables.py report the flags per rho but no crossing rho. At Bulenox the benefit increases
   with rho:
   - B1 (i) k* is 1.00 / 0.98 / 0.95 / 0.93 at rho 0 / 0.25 / 0.5 / 0.75;
   - B3 (i) k* is 0.98 / 0.95 / 0.93 / 0.91;
   - (ii) falls with rho as well.

   So B1 does not beat B0 at rho 0 but does at 0.25 to 0.75, and "the smallest rho at which it no longer beats B0"
   would be rho 0. At Topstep (B1, B4 (i)) the benefit falls with rho; Lucid, MFFU and Tradeify are nearly flat. The
   synthesis must state the crossing per basket and firm, and handle the non-monotone case explicitly.

9. **NOTE: seed noise against thin margins.** Under the new seed, thresholds moved by 1 step (item 3). In the
   confirmed cells, EV one step below the threshold sits within about 2 SE of zero in places: lucid B4 (i) r0.25 is
   -16.5 USD with SE 7.5, and mffu B2 (i) r0.25 is -13.2 with SE 6.7.

   Flags that rest on exactly 2 steps are within seed noise even though they are confirmation-robust: bulenox B1 (i)
   r0.25 at 0.98 and bulenox B3 (i) r0.00 at 0.98, both against 1.00. So is the lucid best-basket tie, which is
   confirmed: B4 and B2 both at 0.96, broken by (ii) 0.41 against 0.46.

10. **NOTE: Topstep B3 at the 2-lot tier.**
    - Near the threshold, 94 to 96% of Topstep B3 funded path-days sit at the 2-lot tier (E29_tables.md share table:
      0.9374 to 0.9588 at k*, and 1.0000 at mu_QM 0.32 in (ii)). The primary form's "no change to the day's P&L
      distribution" therefore governs almost every funded day.
    - The drop-MGC sensitivity raises (i) k* from 0.77-0.80 to 0.93-0.95 (+15 to +16 steps) and k10K from 1.30 to
      1.46-1.55.
    - In (ii) it *lowers* mu*_QM (0.94-0.98 down to 0.87-0.90), because MGC at zero edge only adds cost there. The
      "conservative" label holds in setting (i) only.
    - The Topstep B3 (i) flag stays "yes" under the sensitivity (0.93-0.95 below 1.00, and 1.46-1.55 not above
      1.69). Topstep B3 is not the best basket.

11. **NOTE: Lucid B0 setting (i) k* = 0.98, not 1.00.** The k lattice resolves QM's mu in steps of 0.0033 ticks
    (0.98 × 0.33 = 0.3234), between E.28's 0.32 (EV < 0) and 0.33 (EV ≥ 0). This is consistent, and confirmed
    (item 7). Lucid's setting-(i) flags are judged against 0.98, and the other four firms' against 1.00.

12. **NOTE: code hygiene, no effect on results.** e29_run.py:64 `cell_id` omits the mode. A confirmed-mode run through
    e29_run would therefore overwrite the bisection files in cells/: the fingerprints differ, so the cells are
    recomputed rather than mixed. Write confirmed runs to a separate directory, as this review did (work/review/out/).

## Not checked
- I did not grid-confirm the 203 other limit cells, the 50 market cells, the 8 B3 sensitivity cells, or the alone
  break-evens for MNQ (Topstep, Tradeify, MFFU; Bulenox MNQ is above 12).
- I did not reseed any cell other than the two random picks and Bulenox B0 (ii).
- The section 8 correlations (E29_correlations.*) were outside this brief and are not reviewed.
- The economic plausibility of setting (i)'s units (for example MGC's 6.37-tick alone break-even at Topstep, which
  makes B2 look strong at k = 0.60) is a modelling result. I checked it only for consistency with E.28's model.
