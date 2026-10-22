# A3_econ work log (EconCoder-OpusXHigh; times PDT from `TZ=America/Vancouver date`)

- 10:25 start. Read READER_RULES.md, ranking spec (sha256 89347e97...a5f verified), stage_e28_STATE.md,
  stage_e26_STATE.md (Task 4 done 02:25: reports/stage_e19_rules.json refreshed, 234 rules, sha256 01155d26... (pre-E.26 copy ebc29f8b..., 214 rules); values used by
  the simulator unchanged vs the pre-E.26 copy, checked by loading both), E.19_RETURN.md sections 1 and 3,
  prop_econ/ (types, rules, funnel, vec, assemble, grid, returns), A2 firm files x5, A2_platforms, A0, A1 x8.
  No outputs existed (fresh spawn). free -m: 11.2 GB available.
- Data rule: the E.19 headline (-250 per cycle) used the bootstrap from the E.12 training stores, which run to
  2024-02-29 (inside the Part B pilot window). READER_RULES forbids reading any data dated 2023-11-01 or later, so
  the bootstrap headline is not re-run. Substitute regression: E.19's own normal-tail twin of the same job (same code,
  seeds and rules file; needs only the published sigma_full values) is re-run and must match E.19's stored record
  exactly; the stored headline record (-250.35) is read from reports/stage_e19_runs/ and cited.
- 10:27 regression A3_regress_e19.py: E.19 normal-tail twin re-run with E.19's grid code, seeds and the pre-E.26
  rules copy (fingerprint d4644acce4988b94 = E.19's): 56 stored numbers reproduced, max abs diff 0.0; same on the
  E.26-refreshed record (fingerprint 6831efc9e8e8a9b1): diff 0.0. Stored headline (bootstrap) record: -250.35
  (SE 7.28) per cycle, cited, not re-run (data rule).
- 10:30 A3_inputs.py -> A3_inputs.json: 47 candidates (sigma known 39), 132 (firm, code) pairs listed or listed-but-
  restricted (topstep 33, lucid 23, tradeify 24, mffu 27, bulenox 25).
- 10:36 tests (test_A3_econ.py): 14 passed. Probe: 1.5-3 s per evaluation; first trial MNQ hit 7.9 GB RSS in the
  campaign/cycle assembly (thousands of rebills per cycle when attempts last 756 days at a small negative drift);
  fixed by assembling 1,000 cycles / 500 campaign replications per block (630-680 MB per worker after the fix).
- 10:44 full run launched: 4 workers, nice 10, setsid; log run_main.log; resumable by pair (pairs/<firm>__<code>.json,
  fingerprint b2314f76a3863639).
- 10:50 memory during the run: total PSS of the 7 run processes 1,264 MB (draws shared copy-on-write by fork); system used 4.6 GB of 15.1 GB.
- 11:00 main run finished (128 pairs + 4 from the time probe = 132 records, fingerprint b2314f76a3863639); the first
  worker was then cut by the usage limit before writing A3_econ.json/.md (no A3_monotone.json, no opt2 records, no
  test output on disk).
- 15:12 re-spawned worker (EconCoder-OpusXHigh, second spawn). Read READER_RULES, spec (sha256 89347e97...a5f
  re-verified), STATE, this log, run_main.log and the code. All 132 pair records present and current (121 computed,
  11 not computed: sigma unknown for SI, SIL, MET). 38 records carry non-monotone cached EV/P10K points: EV(mu) has a
  trough near mu = c (net drift near 0: attempts run to the 756-day horizon paying rebills), so the bisection's
  final bracket alone does not prove the smallest grid point. Fingerprinted files (A3_funnel, A3_models, A3_run,
  A3_inputs.json) left untouched.
- 15:15 tests: 14 passed in 4.6 s (test_A3_econ.out; the prose said 15, corrected). prop_econ/ unchanged (git status).
- 15:17 A3_gridcheck.py written (grid confirmation of every threshold + 0.25-step monotone scan). Trial on lucid NQ
  and tradeify M6A: both confirmed, stored point recomputed bit-for-bit. 15:19:39 full run launched (setsid nohup,
  nice 10, 4 workers, log gridcheck_main.log; 119 pairs to go).
- 16:03 grid check done (rc 0): 121/121 pairs, every threshold confirmed, 0 corrected, 121/121 stored points
  recomputed bit-for-bit; 6,374 lattice points (4,713 new). Monotone scan (A3_monotone.json): EV nondecreasing for 6
  of 8 pairs (fails for topstep MNQ, bulenox ZS); P10K nondecreasing for 8 of 8.
- 16:05 Bulenox Option 2 sensitivity done (25 pairs; identical thresholds to Option 1 except NQ).
- 16:05-16:10 A3_report.py (extended: grid confirmation, tests, runtimes) -> reports/stage_e28_briefs/A3_econ.json
  (132 pairs, 0 missing); A3_write_md.py -> reports/stage_e28_briefs/A3_econ.md. Spec hash re-checked; prop_econ/
  unchanged; fingerprinted files untouched (fingerprint b2314f76a3863639).
