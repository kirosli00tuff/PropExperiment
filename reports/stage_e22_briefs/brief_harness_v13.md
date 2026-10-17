# Brief: HarnessBuilder-OpusXHigh, Stage E.22 Part A, harness v13 change set

Lead: E.22 (Opus 5.5, xhigh), 2026-10-16 01:15 PDT. Read first: reports/stage_e22_briefs/partA_harness_audit.md
(the audit of v12; its section 8 lists the changes, with file:line), reports/stage_e22_briefs/partA_rulings.md
(the lead's rulings), reports/stage_e22_price_paths.json (the declaration you pin), reports/E.5_RETURN.md
sections 3 A2 and 5 (the v5 precedent).

## Objective

Write the code and tests of harness v13 so that each of K3, K5, K6, K8 can be confirmed ONCE with
`python -m screening.stage_e_runner --cluster KX --all --window confirmation`, listed, and given verdicts by
`screening.stage_e_verdict`, under one harness version. Member code, the engine, rules, cost tables, calendars
and frozen tables stay byte-identical. You do not build the manifest, commit, or run any confirmation: the lead
does that after an independent Fable review.

## The change set (audit section 8; numbering kept)

- **N1 declared price path.** Pin reports/stage_e22_price_paths.json (sha256 860f4b11d75aaf8bacb52871944d902d858cbe5edaa9c00a0b76921f270bb425,
  schema stage_e_price_paths/1, {"paths": {"MGC": {"path": "GC"}, "MNQ": {"path": "NQ"}}}) as a frozen input
  (screening/harness_freeze.py FROZEN_INPUTS or a pinned-sha constant; your choice, say which). Confirmation branch
  only: data/stage_e_bars.load_confirmation_leg / read_leg_dates take a path root, open the path root's step 2 store,
  refuse unless the two products share group, vendor_tick_fixed and tick size, book on the vehicle's group calendar,
  keep LegFrame.root = the vehicle, record the path file's name and sha256. screening/stage_e_runner._load_frames and
  confirmation_supply_days take S_X and the pinned sha from the path root's start-rule entry and add
  "price_path": {vehicle: path} to the record; the record's s_x stays keyed by the vehicle (value = the path's S_X).
  The research window ignores the mapping (the micro's own research bars stay the screened series). Roll blackout =
  the path store's own splices (declare this reading in your report).
- **N2 start-rule entries for path roots; a buildable K8 set.** screening/stage_e_start_dates: a mapped vehicle or leg
  contributes its PATH root's entry (computed from the path's research store with its E.2a sha and D6 window, and its
  step 2 store) and never opens the vehicle's own step 2 store; K8's set (MGC->GC, MNQ->NQ, MES from D.1f, 6C, MCL,
  MBT) becomes buildable; K5's MGC trials must find GC's entry without rewriting the write-once K5 file (K5's file keeps
  MGC null; the loader merges files; GC can come from the K8 file or a new set id, your choice; no StartRuleConflict
  with K3's 6C or K4's MCL entries). Say exactly which `--set` commands the lead runs.
- **N3 MES as a confirmation leg.** A resolver that opens MES's Stage D confirmation store
  (data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet, the D.1f-pinned sha256 82e256b4...)
  with the step 2 checks, cut at S = 2020-02-03, in _load_frames and confirmation_supply_days. The 3 rows E.12's load
  refused (TradeDateMismatch, first label 2020-03-30 booked 2020-03-31; reports/stage_e12_briefs/phase1_build.log:2):
  identify them first from reports/stage_d1f_confirmation_build.json (flag lists) if it names them; only if not, by a
  diagnostic that prints ts_event, the store's trade-date label and the calendar's booking of the mismatching rows and
  NOTHING else (no price, no volume, no other row). Lead's conditional ruling: if all three are scheduled-closure prints
  (D.1f flagged 3 in_scheduled_closure bars), handle them by enumeration exactly as v9 handles held closure bars for
  step 2 stores (data/step2_store.py:325-395, reports/stage_e12_closure_rulings.json): a new enumerated rulings file
  reports/stage_e22_mes_closure_rulings.json (pinned), the listed rows re-booked to the calendar's date and flagged
  in_scheduled_closure (the engine already skips closure prints), every other mismatch still refuses. If any of the
  three is not a scheduled-closure print, stop N3, write what you found, and report (the lead rules). Also confirm,
  by reading only the parquet's key-value metadata (no rows), that MES's `rolls` metadata parses through the splice
  reader.
- **N4 trials with no record.** A frozen-file or CLI declaration of untestable members (named missing leg) makes
  screen_cluster write a not-run record (status "not_run", reason, no series) for them and continue; any undeclared
  refusal still aborts. stage_e_verdict: add the label "untestable on owned data"; a Tier A/B trial labelled
  "untestable on owned data" or "inconclusive by design" may be listed run: false with no record; it enters Holm at
  p = 1 and is not covered; a plain Tier A/B trial without a record is still refused.
- **N5 K from the list.** Replace the HOLM_K = 9 constant by the list's k_holm, validated 1..9 (the range
  holm_tier_a accepts), echoed in the verdict output; re-pin tests/test_stage_e_verdict.py:653-655. E.22's lists will
  carry k_holm 5 (lead ruling R-E22-A10).
- **R1 run-once marker.** `--run-once-marker PATH` on the runner's confirmation path: refuse if present; after the
  preflight, every member's start-rule and price-path resolution and every store's existence and pinned sha256 check
  (no row read), write the marker with O_CREAT|O_EXCL, mode 0o444 (content: cluster, harness and freeze sha256, the
  list path and sha256 if given via `--list`, member count, created time) BEFORE _load_frames; any later exception
  writes a STOPPED json beside it (E.21 pattern, multiday/run.py:81-166). Without the flag the runner behaves as
  today (research runs and tests unchanged).
- **R2 dry run.** `--dry-run` on the confirmation path: resolve every member's legs, S_X, price paths, store paths
  and pinned sha256, release-calendar coverage, and print one line per member with the expected supply (supply
  counting reads only timestamp/trade_date columns, as confirmation_supply_days already does); writes nothing,
  never runs the engine.
- **R3 (small).** The verdict output records screening.trial_registry.current_n() beside the list's program_n (no
  refusal when they differ: E.22's list fixes N = 533 for the DSR, R-E22-A11).

## Tests

Add or extend tests as audit section 8 lists for each item (loader, runner world fixtures, start dates, verdict),
synthetic data only. Run `nice -n 10 uv run python -m pytest -q -p no:cacheprovider tests/test_stage_e_*.py` plus
any other test file that imports a module you changed (grep), and report counts before/after. Do not run the full
suite (the lead does). Do not use PYTHONPYCACHEPREFIX for pytest (three harness_freeze bytecode tests fail with it).

## Boundaries

- Edit only screening/stage_e_runner.py, screening/stage_e_verdict.py, screening/stage_e_start_dates.py,
  data/stage_e_bars.py, screening/harness_freeze.py (FROZEN_INPUTS / test patterns only), data/step2_store.py only if
  the N3 enumeration needs its existing helper, the two new rulings/declaration inputs, and tests. Nothing under
  strategy/, sim/, rules/, funnel/, base_rules/, multiday/, forward/, microbook/, live/, ops/, ledger/.
- Do NOT write reports/stage_e2b_harness_freeze.json (the manifest), do NOT commit, do NOT run any runner command on
  the confirmation window (no `--window confirmation` run, not even partial), do NOT read any confirmation-window bar
  value except the N3 diagnostic above. Research-window re-runs are also the lead's (they are the power check).
- Other workers are writing forward/, microbook/ and tests/test_forward_*.py, tests/test_microbook_*.py in parallel:
  make sure the v13 manifest patterns do not pick up those paths (check harness_freeze's file/test patterns and say).
- Time box: aim to finish by 02:40 PDT; if something is not done by then, stop, and report it as unfinished.

## Return

Write reports/stage_e22_harness_change.md: every file and function changed with the reason (N1..R3), the tests added
and the pytest counts, the exact lead command sequence afterwards (manifest build, the start-rule `--set` commands,
the research re-runs for power, the dry run, the marker and confirmation run per cluster, the verdict per cluster),
the N3 finding, and numbered open points (O-1, ...). Return the path, a summary of at most 200 words, and anything
unfinished.
