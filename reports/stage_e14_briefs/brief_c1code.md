# Brief: C1Coder-OpusXHigh (Stage E.14 Task 4/5: test C1's frozen code)

You work in your own git worktree, branched from the lead's merge of harness v10 (data.group_session or
data/hist_calendar.py has the hist calendar loader; data/hist_store.py or data/stage_e_bars.py has
`load_hist_leg(root, plan, *, expected_sha256)`; screening/trial_registry.py has the trial registry; read
reports/stage_e14_v10_notes.md first for the exact names). The lead merges and commits. The user is asleep:
decide, record each decision, continue. Read code by section (grep, line ranges).

## Why this code is needed tonight
Test C1 (reports/stage_e13_prereg_ngrepl.md, the ruling document; annex reports/stage_e13_ng_replication_draft.md
sections 2-7 and rulings C1-C21) is frozen tonight and then waits for funds. A later session will only register
it, quote, buy the six ext2010 stores, build them and run the evaluation once, under this freeze, with a harness
that changes nothing but the acct-2 cap and session caps. So every line of C1's code must exist, be tested and be
hashed tonight. Tonight the lead runs only part 1 below (q and M1); nothing tonight touches 2010-2019 data, which
does not exist on disk.

## Hard boundaries
- Put everything in a NEW top-level package c1_replication/ plus tests/test_c1_*.py. Do not edit any existing
  file: ml_route_v2/ (its constants.py must stay byte-identical, rulings C1-C2), data/, rules/, screening/,
  strategy/, sim/. Frozen modules are used, never changed; where the frozen code reads a module-level table or
  calendar that does not cover 2010-2019, the replication supplies it through a documented, tested context that
  is active only inside the replication run and restores everything on exit (prove the frozen files are
  byte-identical and the patched names restored, in a test).
- Never load real market data or the E.12 state in tests: no file under data/vendor, data/processed*,
  data/sealed, ~/.cache/propexp_e12_phase1, no real *.parquet/*.npy/*.pkl. Tests use synthetic worlds
  (ml_route_v2/synthetic.py and the E.12 tests show how) and synthetic fixture files. Do NOT run part 1 on the real
  E.12 state: the lead runs it after the freeze commit. No Databento or network call. No .env, no key.
- Compute: nice 10; tests small.

## Part 1: c1_replication/q_m1.py (Task 5; the lead runs it after the freeze)
CLI `python -m c1_replication.q_m1 --state <E.12 state dir copy> --state-manifest <json of expected sha256 per
file> --out <json> --model-dir <dir outside the repo>`:
1. Verify every E.12 state file against the manifest (45 .npy, gate0B_meta.json, phase1_filter.pkl,
   phase1_panel.pkl, phase1_build.json) BEFORE loading anything. Load with ml_route_v2.phase1.build.load_build
   (its constants-fingerprint check stays on).
2. Reproduce E.12's NG family B rows at h60 and hF from the persisted OOF splits, with NO fit: assert every split
   file gate0B_<h>_sNN.npy exists before any call (so ml_route_v2.gate0._oof only reloads), use exactly the blocks,
   admissible set and trade rule E.12's Gate 0 run used (ml_route_v2/phase1/gate0_stage.py run_gate0 and
   ml_route_v2/gate0.py gate0_b_trades, _top_trades, _b_test). Do not write to ledger/ml_v2_config_ledger.jsonl:
   if a frozen function registers, give it a temporary copy of the ledger and assert the real file's sha256 is
   unchanged. Compare trades, mean and t_B with reports/stage_e12_gate0.json's NG h60 and hF rows to 1e-9 (absolute
   for counts, 1e-9 relative or absolute for floats; state which); any mismatch exits non-zero with "C1 STOP:
   q reproduction mismatch" and writes nothing else.
3. q_h = the smallest |r_hat| among NG's Gate 0 trades at h (ruling C3), printed with full precision (repr).
4. M1 per horizon h in (h60, hF): data = ml_route_v2.cpcv.horizon_data(panel, h, admissible) with E.12's
   admissible pairs (all 81 pairs' ok rows at h, pooled; annex section 2), fit = models.fit_model(
   configs.ridge_spec(gate0.GATE0_RIDGE_LAMBDA), data.X, data.y). Persist the FittedModel payload bytes to
   --model-dir, and record the sha256 of the payload (the coefficient hash), the feature_cols list and its sha256.
5. Also record, per feature, the COUNT of NG rows at h in the E.12 panel where the feature is applicable (flag 1
   or non-n/a, as the panel defines applicability; counts only, no values): the reference for ruling C10.
6. Write --out (reports/stage_e14_c1_model.json): state hashes, the reproduced rows, q per horizon, M1 hashes,
   feature_cols sha256, C10 reference counts, the ML ledger sha256 before and after, versions (numpy, sklearn if
   used, python). Print a short summary (no data values beyond the reproduced statistics and q).
Tests: on a synthetic E.12-like state built in a temp dir by the frozen synthetic pipeline (fit splits written
by _oof once, then reloaded), check the reload path does not refit (e.g. by counting fit calls with a spy), the
mismatch stop, q = min |r_hat| of the trades, and M1 determinism (same payload hash twice).

## Part 2: the replication run (the later session runs it once)
CLI `python -m c1_replication.evaluate --harness-sha256 <sha> --freeze <reports/stage_e14_prereg_C1.md>
--freeze-sha256 <sha> --model <reports/stage_e14_c1_model.json> --model-dir <dir> --store-hashes <json> --out
<json>`, behind a run-once marker (ml_route_v2/phase1/gate0_stage.py:260-264 pattern; the marker is written
before any bar is read; refuse if the marker or --out exists), refusing unless the trial registry holds C1-T1
and C1-T2 registered with this freeze's sha256, after the harness preflight:
1. World (as ml_route_v2.phase1.world.Phase1World's fields): vehicle NG only; bars of NG, NQ, ZN, 6E, GC, ZC
   from the six ext2010 stores via the v10 loader (expected sha256s from --store-hashes), start 2010-06-07 for
   every root (ruling C5), end 2019-04-30 (C6); empty CL and MBT frames (C7) with the equality test (the NG-row
   columns equal those of a context with synthetic CL bars); MES not loaded and every MES-reading signal excluded
   exactly as E.12 (P-1a); the panel's signals = E.12's covered signals (reports/stage_e12_gate0_list.json
   "covered_signals"); calendar, releases, costs (frozen D8 for NG), blackout and legs as Phase1World builds
   them but from the hist sources: the six hist group calendars, the Topstep flatten rows by Rule H-1
   (rules/sessions.py lines 20-40) derived from the hist equity calendar, ENERGY_FULL_SESSIONS from
   reports/stage_e14_cal_energy_full_sessions.json, the NGS table with C13's drop rule and the D8 release list
   (NGS, WPSR, FOMC) from reports/stage_e14_cal_releases.json. Unsourced calendar dates are excluded and counted
   (ruling C12). Every one of these inputs is passed by path and sha256 and checked.
2. Panel: ml_route_v2.pipeline.build_world_panel (or the same calls), NG rows only (C8), per-product causal
   z-scores as normalize.py does (C8). Guards: feature_cols equal to E.12's names and order (C11; from the model
   JSON), and C10: print per feature the count of NG rows where it is applicable (no values) and stop if any
   feature with a non-zero C10 reference count has 0 applicable rows (a C10 stop CLOSES the registered attempt:
   write a STOPPED result, never rerun).
3. Trades: r_hat = models.predict(M1_h, X) with the persisted payload (sha256 checked); trade sign(r_hat) iff
   |r_hat| >= q_h, one contract; g = side x y_gross_h (NG ticks); cost c = cost_long_h or cost_short_h by side.
   All V2.2 exclusions apply as the frozen clock and targets apply them (roll blackout, early close and halt, the
   release-window rule).
4. Statistic and verdict (prereg section 5): per test (T1 = NG h60, T2 = NG hF) gate0._b_test's per-date mean,
   t_B and one-sided p with n_dates - 1 df; pass iff mean g >= 1.5 x c(NG,h) (c = mean cost of the sides taken)
   AND p <= 0.025 AND n_trades >= 30; replication PASS iff T1 or T2 passes. Write the verdict first, then the
   descriptive outputs (C14: the 1.5x slippage case; C15: share of rows above q, long/short split, trades per
   year), all into --out with every input hash.
Tests: a synthetic 2-root or 6-root world in a temp dir end to end (with fake hist calendars and fake stores
through the v10 loader's fixture path or a test double with the same interface), the C10 and C11 stops, the
run-once refusals, the registry refusal, the calendar context restoring the frozen names, and the pass-bar
boundaries.

## Return
Write c1_replication/README.md (what each module does, the exact commands the later session runs, in order) and
reports/stage_e14_c1code_notes.md (files, decisions, every place the replication supplies a table the frozen code
reads and how, tests and counts). Commit to your worktree branch only. Return: (1) worktree path and branch,
(2) a summary of at most 200 words, (3) anything not finished or any place where the frozen code could not be
reused unchanged (stop and report rather than editing a frozen file).
