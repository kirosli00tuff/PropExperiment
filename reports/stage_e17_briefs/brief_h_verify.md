# Brief: VerdictVerifier-FableXHigh (worker-xhigh, model fable) - recompute every number entering H1-H5's verdicts

Written by the E.17 lead (hand-off step 15). Independent recomputation by your own scripts. Do not spawn workers. Do
not commit. Write only under reports/stage_e17_h_verify/ (create it) and reports/stage_e17_review.md (append).

## One objective

Recompute, independently of base_rules' statistics and verdict code, every number that enters the verdicts of the
five registered tests E16-H1..E16-H5: per test and cost case (base, stress, slip150) the unit series, n, mean, sd, t,
the Newey-West t and its lag, p_t, p_nw, p = max(p_t, p_nw), the year-stability table and its pass, then Holm at 0.05
across the five (base case), each test's pass bar, and DSR at N. First write your numbers to disk from the run
outputs and the stores; only then open reports/stage_e17_runs/verdict.json and compare.

## Binding rules

- The freeze: reports/stage_e16_freeze.json (manifest sha256 5274aa97...), the pre-registrations
  reports/stage_e16_prereg_H1..H5.md and reports/stage_e16_prereg_common.md (the pass bar, the cost cases, U3a, U3b,
  the windows and fallbacks), reports/stage_e16_rulings.md (R-S*, R-B*, F-*), base_rules/README.md.
- E.17's fallback list (reports/stage_e17_fallback.json and its sha256 in reports/stage_e17_STATE.md) and the run
  manifest reports/stage_e17_run_manifest.json (sha256 in STATE).

## Inputs

- reports/stage_e17_runs/<test>_result.json and <test>_units.jsonl for H1..H5 (one row per unit candidate: fills,
  gross, costs, sigma, status), the markers <test>_RUN_ONCE.json, and verdict.json (read last).
- The stores named in the run manifest (each sha256-checked before you read it) for the independent spot checks.
- The trial registry ledger/trial_registrations.jsonl (N at the verdict).

## Method

1. From the units files alone, rebuild each test's series per cost case (the risk-unit values the statistics use; for
   H5 the combination of the four component series as the pre-registration defines it) and recompute every
   statistic with your own code (numpy/scipy; your own Newey-West with the frozen lags H1, H4, H5 5; H2 1; H3 3).
2. Spot-check the units against the stores, independently of base_rules' simulator: for at least 40 traded units per
   test (H1-H4, stratified by product, era 2010-2019 vs 2019-2024, and long/short), recompute the fill prices from
   the bars at the frozen minutes (the settlement table reports/stage_e16_settlement.json; R-B1 for a scheduled
   closure at S_p), the gross P&L in cents, the base cost per fill (D8, frozen tables), the stress (+1 vehicle tick
   per side) and slip150 costs, and the trailing-20 sigma scaling. Report every mismatch.
3. Check the exclusion counts in each result against the units file (status counts by reason), the fallback
   windows (a fallback root has no unit before 2019-05-06), no unit after 2024-02-29, no unit from 2026-06-21 on,
   and that no holdout-2 or embargo date entered.
4. Holm (base case, alpha 0.05, m = 5), each pass bar (Holm rejects, mean > 0, n >= 30, year stability with the
   frozen thresholds: H2 6 units a year, the others 10), DSR at N (screening.stage_e_verdict's DSR definition, read
   and re-implemented), and N itself from the registry.
5. Assert that every output records the registry path ledger/trial_registrations.jsonl and its sha256 (E.16 recheck
   NOTE R-2), the freeze sha256, the manifest sha256 (H1-H4) and, for H5, its four components' sha256s.

## Boundaries

No vendor call, no key read (never open ..env.swp), no write to ledger/, data/, reports/stage_e17_runs/ or any
frozen file; never run base_rules.run (each test runs once). Print counts and summary numbers only, never price rows.
Check free memory before loading stores; nice 10; at most one store in memory at a time if memory is tight.

## Output

reports/stage_e17_h_verify/ (scripts, recompute.json), and a section
"## H1-H5 verdict recomputation (VerdictVerifier-FableXHigh)" appended to reports/stage_e17_review.md: your numbers,
then the comparison with each result file and verdict.json, findings graded BLOCKING, SHOULD FIX or NOTE with
evidence. Return the paths, a summary of at most 200 words (VERIFIED, VERIFIED WITH NOTES, or NOT VERIFIED per test),
and anything you could not finish.

## Focus points from the lead (added 01:40, after the runs; check them, do not take them as findings)

- H1's base t is about -20 (mean -0.161 risk units). A lead-side descriptive sum over H1's traded units gave mean
  gross/sigma about 0.052 and mean base cost/sigma about 0.208 (the units' sigma appears to be on a different scale
  from gross_cents, x100): check the cost per fill and its units (cents, sigma's unit, the risk-unit conversion) on
  your spot-checked units, since a cost error would swing H1, H4 and H5.
- H5's base-case sd is 5.97 against 2.54 in the stress case and 4.35 in slip150: check the trailing-60 sigma scaling of
  each component series on H5's grid (sparse H2/H3 series, near-zero sigma) against the pre-registration's wording.
- verdict.json was written at 01:39:53; every result's status is "complete".
