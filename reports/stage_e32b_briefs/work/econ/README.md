# E.32b economics (spec section 4 E): code, regression, timing, how to run

EconSetup-OpusXHigh, 2026-10-28 (times PDT). Brief: reports/stage_e32b_briefs/brief_wave_b.md, section B12. Spec:
reports/stage_e32b_ranking_spec.md (sha256 09ebe697...eb58635, checked by the driver at every start), sections 0 and
4. Model: E.28's (reports/stage_e28_briefs/A3_econ.md sections 1 and 2). Nothing here was run on E.32b facts.

## Files

| file | what |
|---|---|
| A3_funnel.py, A3_models.py, A3_run.py | E.28's model, firm mapping and state builder, copied unchanged (COPY_MANIFEST.json: sha256 of source and copy) |
| A3_gridcheck.py, A3_opt2.py, A3_probe.py, A3_regress_e19.py, A3_runtimes.py, A3_flat.py, A3_prose.py, test_A3_econ.py | E.28's other code, copied unchanged (reference; not used by the new pipeline) |
| A3_report.py, A3_write_md.py, A3_inputs.py | copied with one added guard line each that refuses to run (they write E.28 paths or regenerate A3_inputs.json) |
| A3_inputs.json | E.28's inputs (copied), used only by the regression |
| econ32b_core.py | grid, cap, T, bisection, E.28's grid confirmation generalised to the market case and any cap; per-cost outputs |
| econ32b_model.py | binds the core to E.28's simulator with T and sigma_T as parameters |
| econ32b_inputs.py | jobs from F3_vol.json + F4_facts_unmasked.json, and from E.28's A3_inputs.json (regression); firm-limit check |
| econ32b.py | driver: `run`, `collect`, `regress`; resumable parts under parts/<tag>/; writes econ32b.json |
| econ32b_regress.py | the comparison with E.28's A3_econ.json -> REGRESSION.md, regression.json |
| test_econ32b.py | 53 unit tests (synthetic) |
| make_fixture.py, fixture/ | a SYNTHETIC F3/F4-shaped fixture from E.28's inputs (for the timing run only; not facts) |
| run_regress.sh, run_fixture_timing.sh | the two runs made here (logs: regress_run.log, fixture_timing.log, smoke_regress.log) |
| REGRESSION.md, regression.json | the regression result |
| estimate.py, timing.json | the full-run estimate from the measured jobs |
| run_real.sh | the wave-C runner (two passes, chunked under the lock) |
| parts/regress/, parts/fixture/ | one part per job (thresholds, search details, every evaluation) |

## What the code computes (spec section 4 E, applied literally)

Per pair (firm, code) and per "curve" (per-trade law), E.28's model unchanged: T round trips a day, size 1, gross
P&L per trade normal (mean mu, SD sigma_T ticks), daily P&L normal with mean T (mu - c) v and SD sqrt(T) sigma_T v,
E.28's funnel, fees, 20,000 paths and cycles on E.28's common random numbers (seed 20261021), 756-day horizon.

- c_mkt = F_rt / v + S_rt, S_rt = F4 `codes[CODE].spread_S.value` when `sourced` is true, else 1 tick ("u").
- Grid: mu = 0, 0.01, ..., cap with cap = max(4, ceil(0.30 sigma_60)) ticks (0.30 sigma_60 rounded to 1e-9 first,
  so 0.30 x 20 = 6, not 7). The same cap is used for every curve of a pair.
- mu*_mkt: the smallest grid mu with EV >= 0 (EV = mean net cash per cycle incl. the API, E.28's definition), market
  case. mu10K_mkt: the smallest grid mu with P(net cash >= USD 10,000 within 250 trading days) >= 0.5, market case.
  None with `above_cap` true when no grid point qualifies.
- Search: E.28's bisection on the grid index, then E.28's grid confirmation (A3_gridcheck.py) on [0, threshold):
  every 0.10-tick sub-grid point and the region ends, every grid point in the 0.10 ticks below the threshold, every
  grid point of a sub-grid gap with an end near the threshold (EV >= -max(5 SE, USD 100), or P10K >= 0.40); a
  checked point below with f >= 0 replaces the bisection value by the smallest grid point with f >= 0. "Above the
  cap" is confirmed over the whole grid the same way. EV and P10K depend on mu only through d = mu - c, so one cache
  per curve serves every cost on it (primary and spread1 share the primary curve).
- m* = mu*_mkt / sigma_60 and m10K = mu10K_mkt / sigma_60, in every block (sigma_60 units throughout).
- cost_per_attempt: E.28's definition (evaluation fees per attempt at mu = 0, limit case, d = -F_rt / v) on the
  block's own curve; cost_per_attempt_mkt_mu0 (the same at d = -c_mkt) is reported beside it (see "For the lead").
- Blocks per pair: `primary` (T = 20, sigma_T = sigma_1, S sourced), `spread1` (the same curve, S = 1),
  `E_dir60` (T = min(20, floor(L_main / 60)), sigma_T = sigma_60, S sourced), and for the pairs passed with
  --edir-pairs `E_dir: {"30", "120", "240"}` (T = min(20, floor(L_main / h)), sigma_T = sigma_h). Each block has the
  contract's fields (mu_star_mkt, mu10K_mkt, above_cap {mu_star, mu10K}, cost_per_attempt, sigma60, m_star, m10K,
  grid_cap) plus T, sigma_T, h, F_rt_usd, v_usd, S_rt_ticks, c_lim_ticks, c_mkt_ticks and a `search` summary
  (bisection value, f at k and k - 1, confirmation result). Pair inputs and notes are under `inputs`.
- Not computed (listed under `not_computed` with the reason): NQ ("excluded (V49)"), codes whose F3 status is
  `unknown` or whose sigma_1 or sigma_60 is missing ("Layer 1 gate"), pairs not `listed_50k`, unknown fee or tick
  value. An E_dir variant with T = 0 (main session shorter than h) or unknown L_main is noted in the pair's
  `inputs.notes` and left out.
- Firm models are E.28's (A3_models.py). F4 `firms[f].mll_50k` and `dll_50k` are compared with the model's MLL and
  DLL; any difference stops the run (exit 3) unless `--allow-firm-mismatch` is passed. Payout rules, plan prices and
  resets are NOT compared automatically.
- Refusals: spec sha256 different from the frozen one; F3 or F4 `spec_sha256` different; F3 and F4 tick sizes that
  disagree for a code; a firm with no E.28 model.

## How to run on the new inputs (wave C, when the lead asks)

Preconditions: reports/stage_e32b_briefs/F3_vol.json and F4_facts_unmasked.json exist (F4's `pairs` keyed
"firm|CODE"; firm names matched to E.28's models case-insensitively; the output keeps F4's keys). Check
`free -m` (see the memory figures below). From the repo root:

    # pass 1: primary, spread1 and E_dir60 for every computed pair -> reports/stage_e32b_briefs/econ32b.json
    setsid nohup reports/stage_e32b_briefs/work/econ/run_real.sh > /dev/null 2>&1 < /dev/null &
    # pass 2, after the score run names the top 15 (E_dir needs the ranking, the ranking needs E):
    EDIR=<path to a JSON list of "firm|CODE"> setsid nohup reports/stage_e32b_briefs/work/econ/run_real.sh \
        > /dev/null 2>&1 < /dev/null &

run_real.sh runs `econ32b.py run --chunk i/6 --workers 6` six times, each under
`flock reports/stage_e32b_briefs/work/heavy.lock` at nice 10 (other workers can take the lock between chunks), then
`econ32b.py collect`, which writes the output. Log: work/econ/run_real.log (one line per job: pair, curve, seconds,
evaluations, thresholds; "chunk i/6 rc=..." and "collect rc=..." lines; the peak PSS and the lowest MemAvailable
per chunk). Resumable: a job whose part (parts/real/<firm>__<CODE>__<curve>.json) exists with the same job hash is
skipped, so a cut run is restarted with the same command, and pass 2 reruns nothing from pass 1 (the primary,
spread1 and E_dir60 blocks of the rewritten econ32b.json come from the same parts; only generated_pdt and the
E_dir blocks change). Options (environment variables): ONLY="firm|CODE,..." to restrict the run (for example to
the Layer 1 survivors' pairs), ALLOW_FIRM_MISMATCH=1 to keep E.28's firm models when F4's MLL or DLL differ (the
run otherwise stops with rc 3 and prints the differences: a lead decision), WORKERS, N (chunks). The single
command underneath, for one chunk:

    flock reports/stage_e32b_briefs/work/heavy.lock env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 nice -n 10 \
      uv run python reports/stage_e32b_briefs/work/econ/econ32b.py run --tag real \
      --f3 reports/stage_e32b_briefs/F3_vol.json --f4 reports/stage_e32b_briefs/F4_facts_unmasked.json \
      [--edir-pairs FILE] [--only KEYS] [--allow-firm-mismatch] --chunk 0/6 --workers 6

Tests: `uv run pytest -q reports/stage_e32b_briefs/work/econ/test_econ32b.py` (53, under a second);
E.28's own tests on the copied code: `uv run pytest -q reports/stage_e32b_briefs/work/econ/test_A3_econ.py`
(about 1 GB peak; through the lock).

## Timing and memory (measured 2026-10-28/29, this machine, nice 10, 6 workers, under the heavy lock)

One evaluation (one d on one curve: 20,000 attempt and funded paths, 20,000 cycles, the 20,000-replication
campaign) costs about 1.5 s alone (profile: pools 1.1-1.9 s, cycles 0.1 s, campaign 0.2-0.3 s) and 2-3 s per worker
with 6 running (Topstep's long attempts up to 5 s). Throughput on 6 workers: about 1.9 evaluations per wall second.

Timing run (run_fixture_timing.sh, 5 pairs of the synthetic fixture, 13 jobs, fixture_timing.log): wall 1,880 s,
peak PSS 1,757 MB (parent plus 6 workers; parent max RSS 678 MB).

| pair | curve | grid cap (ticks) | evaluations | seconds | s / evaluation |
|---|---|---|---|---|---|
| tradeify ZC | primary + spread1 | 4 | 46 | 122 | 2.66 |
| tradeify ZC | E_dir60 | 4 | 55 | 132 | 2.41 |
| mffu 6E | primary + spread1 | 9 | 63 | 155 | 2.46 |
| mffu 6E | E_dir60 | 9 | 86 | 172 | 2.00 |
| lucid GC (S = 1.5, so spread1 is a separate lattice) | primary + spread1 | 13 | 65 | 143 | 2.20 |
| lucid GC | E_dir60 | 13 | 112 | 263 | 2.34 |
| bulenox MCL | primary + spread1 | 16 | 152 | 348 | 2.29 |
| bulenox MCL | E_dir60 (both above the cap: whole grid checked) | 16 | 161 | 462 | 2.87 |
| topstep MNQ | primary + spread1 | 65 | 170 | 855 | 5.03 |
| topstep MNQ | E_dir60 | 65 | 569 | 1,126 | 1.98 |
| topstep MNQ | E_dir30 | 65 | 299 | 655 | 2.19 |
| topstep MNQ | E_dir120 | 65 | 1,081 | 1,615 | 1.49 |
| topstep MNQ | E_dir240 | 65 | 997 | 1,600 | 1.60 |

What drives the count: the confirmation checks every 0.10 tick below each threshold (E.28's absolute sub-grid), so a
threshold at 30 ticks costs about 300 evaluations, an above-cap result the whole grid (cap / 0.10 + 1), plus dense
fills where P10K >= 0.40 or EV is within max(5 SE, USD 100) of 0. High-sigma codes have wide caps and slowly rising
P10K, hence the MNQ counts.

Estimate for the full run (estimate.py -> timing.json): evaluations per job fitted on the measured jobs as
a + b x cap (primary 60 + 1.8 cap, E_dir60 14 + 8.5 cap), applied to a run of the fixture's shape (116 computable
non-NQ pairs of E.28's list, 232 jobs; the real F3 marks 8 roots unknown, so the real run is likely smaller):

| pass | evaluations | wall on 6 workers | note |
|---|---|---|---|
| 1: primary, spread1, E_dir60 (232 jobs) | about 26,200 | about 3.8 to 4.1 h | worst case (every curve above its cap) 34,200, 5.3 h |
| 2: E_dir 30/120/240, top 15 (45 jobs) | up to about 35,700 | up to about 5.6 h | from the MNQ jobs (cap 65): an upper figure unless the top 15 are high-sigma codes |

Throughput used: 1.78 evaluations per wall second (the slowest regression chunk; the four chunks averaged 1.92).
8 workers were not measured.

Peak memory: about 2.0 GB PSS on 6 workers (regression chunks: 1,879 to 2,032 MB; fixture: 1,757 MB); about 2.5 GB
expected on 8 workers (each worker adds about 250 MB to the parent's 400 MB of shared draws). The lowest
MemAvailable seen during the runs was 6.7 GB (other workers running). 8 workers (the cap) would cut the wall time
by up to a quarter. The fixture's sigma_h = sigma_1m sqrt(h) makes its caps, and so this estimate, conservative if
the real 60-minute sigmas are below the square-root scaling.

## For the lead (ambiguities in spec section 4 and choices made here; none changes the spec)

1. Cost per attempt. E.28 defines it at mu = 0 in the limit case; spec 4 says "E.28's limit case is not used".
   `cost_per_attempt` keeps E.28's definition (d = -F_rt / v); `cost_per_attempt_mkt_mu0` (d = -c_mkt) is beside
   it. It is computed on each block's own curve, so E_dir60's differs from the primary's (Topstep MNQ in the
   fixture: 104 vs 165 USD, attempts end sooner at the higher sigma). The tie rule uses it: say which one.
2. mu10K_mkt is new (E.28 computed mu10K in the limit case only): implemented as E.28's definition with c = c_mkt.
3. Grid cap for E_dir60 and E_dir h: the spec defines the cap from sigma_60 for the pair; the same cap is used for
   every curve of the pair. Longer holds often need more than 0.30 sigma_60 per trade (fixture MNQ E_dir240: mu10K
   above the 65-tick cap; MCL E_dir60: both above the 16-tick cap), which then score 0 and give no value for F5.
4. m* and m10K are in sigma_60 units in every block (E_dir included), not in sigma_T units.
5. T = min(20, floor(L_main / h)) is 0 when the main session is shorter than h (E_dir240 for any L_main < 240):
   such a curve is not computed and is noted in the pair's `inputs.notes`; the same for an unknown L_main (6 F3
   roots have L_main null). A pair without an E_dir60 block has `"E_dir60": null`, which ScoreCoder's E_dir60
   variant will refuse for an eligible pair.
6. Firm models stay E.28's (A3_models.py, Topstep from the E.26-refreshed E.19 record, sha256 01155d26..., unchanged
   since). Only MLL and DLL are checked against F4; plan prices, resets, payout rules and the Topstep XFA rules are
   not. Any MLL/DLL difference stops the run until the lead rules (ALLOW_FIRM_MISMATCH=1 keeps E.28's models).
7. S is taken in ticks as F4 gives it (`spread_S.value` when `sourced` is true), used as is even when fractional (a
   non-integer S does not share the spread1 lattice: more evaluations, no other effect).
8. Which pairs: the default is every listed pair with known sigma_1, sigma_60, fee and tick value (a superset of
   the Layer 1 survivors). ONLY=<survivors' pairs> saves the time of the others.
9. E_dir needs the top 15, which needs E: two passes (above). Pass 2 rewrites econ32b.json with identical primary,
   spread1 and E_dir60 blocks.
10. The confirmation keeps E.28's assumption that EV and P10K do not cross the threshold and back inside one 0.10-
    tick gap whose two ends are both far from it (a unit test documents that such an island is not seen).

## Regression against E.28 (REGRESSION.md, regression.json): PASS

With E.28's own inputs (A3_inputs.json), S = 1, T = 20, sigma_T = sigma_1m, market case only, grid 0 to 5.00 ticks
(so that every E.28 limit-case mu10K <= 4 has its market twin, mu10K + 1.00, on the grid), the new pipeline
(econ32b.py regress, run_regress.sh: 4 chunks under the lock, 6 workers, 23:25 to 00:53 PDT with a 31-minute pause
while the timing run held the lock; 3,369 s of chunk wall time, 6,462 evaluations):

- mu*_mkt identical to E.28's for 121 of 121 computed pairs (where E.28 says "> 4", the new value is above 4 too);
- mu10K_mkt identical to E.28's mu10K + 1.00 for 121 of 121 (above the 5-tick cap exactly where E.28 says "> 4");
- cost per attempt identical (largest difference USD 0); EV at the mu*_mkt grid point within 4.5e-6 USD of E.28's
  stored value (floating point: E.28 passed the unrounded d to the day law, this code d rounded to 1e-9 ticks);
- no threshold corrected by the grid confirmation, none unconfirmed (as in E.28);
  (Note 2026-10-29, ScoreFixer-OpusHigh, review RV1 S3: this line is true of the regression. The real pass 1 had
  two pairs with unconfirmed searches: bulenox|CL and bulenox|NG, blocks primary and spread1, searches mu_star_mkt
  and mu10K_mkt, confirmed false, k_bisection null. The recorded values are confirm()'s k_final, the full-grid
  thresholds mu* 1.76 and mu10K 2.44 ticks, equal to E.28's for these pairs; score32b.py now lists such searches
  in input_checks.)
- the 11 pairs E.28 did not compute (SI, SIL, MET: sigma unknown) are not computed here either.

Also: E.28's own 14 unit tests pass on the copied code in this folder (test_A3_econ_copy.out: 3.3 s, 993 MB peak),
and the 53 new unit tests pass. The fixture output (fixture/econ32b_fixture.json) was read by ScoreCoder's
`s32b_layer2.e_score` for all 15 blocks without error (a format check only; its numbers are synthetic).
