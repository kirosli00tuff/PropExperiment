# Brief: VerdictVerifier-FableXHigh (Stage E.18 Step 6)

You are the independent verifier (worker-xhigh on Fable) of C1b's single registered evaluation. Work in
/home/kiros-li/Documents/GitHub/PropExperiment. All times PDT from `date`. Follow CLAUDE.md's context-hygiene and
compute rules: read files by section, keep output short, run computations at `nice -n 10` with a fresh
PYTHONPYCACHEPREFIX under /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/a6f2d97b-f5fc-4d95-a054-c5010e1ff6d0/scratchpad/,
check MemAvailable before the rebuild (E.17's rebuild peaked at about 2.1 GB, 30-65 s).

## Objective (one)

Recompute C1b's verdict numbers independently, BEFORE reading the lead's statistics, then compare; and check the
order of events. A BLOCKING finding is resolved by finding a code error, never by a second evaluation.

## Inputs

- The freeze: reports/stage_e18_prereg_C1b.md (section 3 C10 as amended, section 5 the pass bar, section 9 the
  order of events); the freeze manifest reports/stage_e18_freeze.json; the C1b code c1_replication/c1b.py and the
  frozen C1 code it wraps (c1_replication/evaluate.py, world.py, context.py, exclusions.py, tables.py, q_m1.py).
- The pinned inputs: reports/stage_e14_c1_model.json (M1 payload sha256s, q_repr, feature_cols, c10_reference),
  the payloads in ~/.cache/propexp_e14_c1/m1, reports/stage_e17_c1_store_hashes.json, reports/stage_e17_c1_calendar_hashes.json,
  reports/stage_e12_gate0_list.json (covered signals).
- Your E.17 predecessor's rebuild scripts, which you may reuse as a starting point: reports/stage_e17_c1_verify/
  (verify_run_counts.py rebuilds the world and panel with the frozen building blocks, never evaluate.run).
- The trial registry ledger/trial_registrations.jsonl; the spend ledger ledger/databento_spend.jsonl (start: 36,402
  lines, sha256 034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700).
- AFTER your own numbers are on disk only: the result reports/stage_e18_c1b_result.json, the marker
  reports/stage_e18_c1b_RUN_ONCE.json and the log reports/stage_e18_briefs/c1b_evaluate.log.

## Checks

1. Recompute (write reports/stage_e18_verify/recompute.json with a `date` timestamp BEFORE opening the result's
   tests, descriptive, guards or trades_sha256, or the log). Rebuild the world and the panel with the frozen
   building blocks (load_calendars, c12_exclusions, hist_tables, build_world with data.hist_bars.load_hist_leg on
   the pinned stores, replication_panel). Then, with your own code: per test (T1 = NG h60, T2 = NG hF) the ok rows,
   r_hat from the M1 payloads (ml_route_v2.models.predict is allowed), the trades sign(r_hat) where |r_hat| >= q_h,
   gross g = side x y_gross_h, cost by side, the per-date mean series, n_trades, n_dates, mean g, mean cost c, the
   1.5 c bar, t_B = mean / (sd / sqrt(n_dates)) with the sd convention gate0._b_test uses (check it in
   ml_route_v2/gate0.py and say which), the one-sided p from Student's t with n_dates - 1 df (scipy), each pass
   criterion and the verdict (PASS iff T1 or T2 passes). Also: the C10 counts and C1b's amended check (only g17_mbt
   and g17_cl exempt; every other live feature must apply on at least one row), the descriptive outputs (C14 the
   1.5x slippage bar; C15 share at or above q, long/short split, trades per year) and trades_sha256 (the encoding in
   evaluate.trades_sha256).
2. Compare with the result file: every number to 1e-9 (counts exactly). Any mismatch: find its cause in code.
3. Order of events with timestamps: the diff review (reports/stage_e18_review.md, first section's times), the dry
   check (reports/stage_e18_dry_check.json started/finished), the freeze commit "C1b freeze" (git log), the
   registration (registry time_local; N 478 -> 480; ids C1b-T1, C1b-T2; freeze sha256 equals the frozen file's and the
   manifest's), the marker (started_local) before any bar-derived output (the log's line order), the result
   (finished_local). Confirm the evaluation ran once (one marker, one result, no other C1b result file).
4. Inputs: the result's input hashes equal the freeze manifest's (model, payloads, q, stores, calendars, code
   sha256 of c1_replication/*.py including c1b.py); the C1 freeze-inputs files unchanged; the spend ledger unchanged
   since the start (no purchase, no Databento call).

## Output

Append to reports/stage_e18_review.md a section "## C1b verdict verification (VerdictVerifier-FableXHigh)": start
and end times, a verdict (VERIFIED, VERIFIED WITH NOTES or NOT VERIFIED), the four checks with evidence, then
findings labelled BLOCKING, SHOULD FIX or NOTE, each with file:line evidence. Scripts and outputs go in
reports/stage_e18_verify/. Return: the path, a summary of at most 200 words (verdict, T1 and T2's decisive numbers
as you computed them, each finding), and anything you could not finish.

## Boundaries

- Never run c1_replication.c1b, c1_replication.evaluate or q_m1 (the evaluation runs once); never write, move or
  delete the marker, the result, the registry, the spend ledger or any frozen file. Write nothing outside
  reports/stage_e18_review.md (append only) and reports/stage_e18_verify/.
- You may read the 2010-2019 ext2010 stores through the frozen loaders to recompute; print counts and statistics,
  never prices or bar rows.
- No holdout, live/, ops/, TopstepX, Databento or network access. No git commit. Do not spawn other agents.

## Facts at hand-off (lead, from `date`, file mtimes and the registry; no statistic given here)

- DiffReviewer-FableXHigh review 11:58-12:14 (reports/stage_e18_review.md first section); rulings R-1..R-5 applied
  12:14-12:15. Dry check 12:16:02-12:16:05. Freeze manifest written 12:17:07 (sha256
  5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03). Commit b714751 "C1b freeze" 12:17:35.
- Registration r003-C1b 12:17:48 (log reports/stage_e18_briefs/c1b_register.log). Evaluation launched 12:18:03
  (detached, nice 10); the log reports/stage_e18_briefs/c1b_evaluate.log ends with rc and the time.
- Extra item for check 1: gate0._b_test reports `mean` as the mean over trades and t_B / p over per-date means; the
  freeze's section 5 describes the statistic as a per-date mean and criterion 1 as "mean gross g >= 1.5 x c". Compute
  both the trade-level mean and the mean of the per-date means for each test, and say whether the verdict depends on
  which one criterion 1 reads.
