# Brief: Gate0Verifier-FableXHigh (worker-xhigh, fable). Stage E.12 Task 8 (Gate 0 verification)

You verify the ML route v2 Gate 0 verdict of Stage E.12 (prompt docs/prompts/STAGE_E.12.md: read
GUARDRAILS, Task 6 and Task 8). Gate 0 ran ONCE; it must never run again. You recompute the verdict
numbers independently, with your own code, from the training-window data and the frozen rules,
WITHOUT reading the lead's statistics first. Only after your numbers are written to disk do you
open reports/stage_e12_gate0.json and compare.

## Frozen rules (read these, not the lead's outputs)
- docs/STAGE_E_ML_V2_DESIGN.md V2.2 (the c/sigma filter, tau 0.167), V2.2b (Gate 0, families A and
  B, the pass bar, the phase-1 test list), V2.5 (targets), V2.9 (the CPCV partition: 6 calendar
  blocks of floor(n/6) dates, the last taking the remainder, 2 test blocks, 15 splits, purge, a
  one-trade-date embargo each side).
- ml_route_v2/constants.py for the literals. You may READ ml_route_v2/gate0.py, cpcv.py and
  cost_filter.py to learn the exact definitions, but write your own computation (numpy/pandas,
  closed-form ridge), do not import those modules for the statistics.

## Inputs you may read
- The training panel the build saved: ~/.cache/propexp_e12_phase1/stages/panel.pkl and
  filter.pkl (pickles written by ml_route_v2/phase1/build.py; load them read-only; they hold the
  rows, z-scored features, gross targets y_gross_<h> in vehicle ticks, normalized targets
  y_norm_<h>, per-row round-trip cost, ok_<h> flags). Never write into that directory.
- The step 2 stores data/processed_step2/<ROOT>/*.parquet (training window only, 2019-05-06..
  2024-02-29) for the target spot check.
- reports/stage_e12_gate0_list.json (the registered list) and its sha256 in reports/stage_e12_STATE.md.
- ledger/ml_v2_config_ledger.jsonl (registration times), reports/stage_e12_phase1_bars.json
  (store sha256s), reports/step2/purchase_<ROOT>.json, reports/stage_e12_ranking.json.
- NEVER: anything under data/sealed or data/vendor, any research-window or holdout file, any
  research-window parquet row.

## Recompute (write each to your output before any comparison)
1. Admissible pairs: c(p,h) (the mean round trip over p's rows at h) and sigma(p,h) (the sd of the
   gross h-return in vehicle ticks over the same rows), ratio, admissible at <= 0.167, for every
   (vehicle, horizon).
2. Family B for the passing pair (if the verdict is PASS) or, if FAIL, the pair with the largest
   t_B among pairs with >= 30 trades (identify it from YOUR recomputation of every pair's t_B on
   that pair's horizon; if that is too heavy, the lead's choice of pair may be taken from the
   JSON after you have computed the CPCV predictions for its horizon): ridge at lambda 0.1 (alpha =
   lambda x n_train, as models.py states) on the same feature columns, pooled across products,
   one model per horizon; CPCV OOF predictions (mean over the 5 test assignments of each row); the
   pair's top-20% |r_hat| trades (floor(0.2 n), stable order on ties); mean gross per trade, the
   cost multiple (1.5 x the mean round trip of the trades taken), the date-clustered t_B, the trade
   count, the one-sided p.
3. Three family A tests chosen at random with seed = int(<the list sha256>[:8], 16) over the
   registered family-A ids in list order: mean of m_d, t, two-sided p, n_dates, Spearman IC.
4. Holm: with your p for the pair(s) of step 2 and the JSON's p-values for the other tests (only
   now open the JSON), the Holm rank, threshold and decision of the pair at family-wise 0.05 over
   all registered tests (families A and B).
5. Targets spot check from the bars: for 20 rows drawn with the same seed among h60 and h120 rows
   whose entry and exit are outside any release window, recompute open(b_{t+h}) - open(b_t) in
   vehicle ticks from the step 2 parquet (price path units converted as targets.py does) and
   compare with y_gross_<h>.
6. Reconcile (freeze review F-10): the store sha256s in reports/stage_e12_phase1_bars.json against
   reports/step2/bars_<ROOT>.json and the purchase records; the vehicles against
   reports/stage_e12_ranking.json's subset; the list sha256 against STATE; the ledger shows every
   Gate 0 test registered before the result file's time.
7. N: |A| + |B| from the list, and 198 + |A| + |B|.

## Tolerance
Counts and Holm decisions exact. Means, t and p: relative 1e-6 (family A), relative 1e-4 (family
B, an independent ridge solve). A difference beyond tolerance is a finding: find its cause in code
(the lead's or yours) before grading it; never suggest rerunning Gate 0.

## Output
reports/stage_e12_review.md, append Part 2 "Gate 0 verification": your numbers, the comparison
table (yours vs the lead's), findings graded BLOCKING / SHOULD FIX / NOTE, and a one-line verdict:
VERIFIED, VERIFIED WITH NOTES, or NOT VERIFIED (with the discrepancy). Put your scripts in
reports/stage_e12_briefs/gate0verifier/ and your raw outputs there too.

## Boundaries
Read-only except your outputs. No network, no key, no commits, never run `python -m
ml_route_v2.phase1 run`. Compute at nice 10, at most 6 threads, check free memory before loading the
panel (keep peak under half of what is available). Context hygiene: never print a whole frame.

## Return (at most 200 words)
The verdict line, the key numbers side by side, the findings by grade, and anything unchecked.

## Added by the lead after the run (12:16 PDT): the verdict is FAIL, and three more checks
- Gate 0 verdict FAIL; so step 2 is the pair with the largest t_B among pairs with >= 30 trades,
  found from YOUR recomputation of every admissible pair's t_B (closed-form ridge is fast: compute
  all three horizons). Do not read the JSON before your table is written.
- Harness v9 (the user's decision mid-stage; commit 4b1e81e): review `git show 4b1e81e` (the
  data/step2_store.py ruling path and the one-line FROZEN_INPUTS addition). Check that
  reports/stage_e12_closure_rulings.json lists exactly the deep closure bars of the 12 held roots
  (the v8 held summaries are gone: the v9 builds overwrote them; use each v9 summary's
  closure_bars and closure_ruling, and store_builds.log / store_builds_v9.log), that each of the
  12 summaries records the ruling file's sha256 and bars_ruled, that the 15 v8-built stores carry
  no deep closure bar, and that no module on the Gate 0 read path changed between v8 and v9.
- MES contingency P-1a: the build reported MES refused (TradeDateMismatch, 3 rows, first label
  2020-03-30 booked 2020-03-31). Confirm the refusal is genuine (read only those rows' ts_event and
  trade_date from data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet,
  no prices) and that exactly the MES-reading signals were excluded (g17_mes, k8_flight_ret,
  k8_flight_tail).
- MBT: S_X 2024-01-02 from D4's start rule left 41 trade dates and no panel row (warm-up). Recompute
  S_X from the start-rule record in reports/stage_e12_phase1_bars.json (roots.MBT.start_rule) and
  confirm the rule's arithmetic (monthly medians vs 0.25 V_ref).
