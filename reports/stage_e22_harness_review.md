# Stage E.22 Part A: independent review of the harness v13 change set (HarnessReviewer-FableXHigh)

Written 2026-10-16, 01:43 to 01:58 PDT (times from `date` and log mtimes), against reports/stage_e22_briefs/brief_harness_review.md.
Reviewed: `git diff HEAD -- screening/ data/ tests/` (data/stage_e_bars.py, screening/harness_freeze.py,
screening/stage_e_runner.py, screening/stage_e_start_dates.py, screening/stage_e_verdict.py, four test files), the
untracked tests/test_stage_e_runner_v13.py, the two new inputs reports/stage_e22_price_paths.json and
reports/stage_e22_mes_closure_rulings.json, and the builder's report reports/stage_e22_harness_change.md (mtime 01:40).
Spec: brief_harness_v13.md (N1-N5, R1-R3), partA_harness_audit.md section 8, partA_rulings.md, docs/STAGE_E_DESIGN.md
D2/D4/D5, docs/NULL_CRITERIA_E.md, reports/stage_e5_harness_review.md, docs/prompts/STAGE_E.22.md A4-A5.
Read-only on code; no manifest build, no commit, no runner command, no confirmation-window bar or parquet read (the
MES store's metadata was not re-read either). Scratch: pytest logs only, under the session scratchpad. The modified
reports/stage_e2b_harness_freeze.json (the lead's manifest work) was ignored as instructed; no reports/stage_e22_power_*
or start-rule output existed at review time.

**Result: 0 BLOCKING, 2 SHOULD FIX, 14 NOTE.** Every v13 behaviour the brief lists is implemented, pinned by a test
and refuses where it must; the two SHOULD FIX items are both about the one-shot nature of the marker run (an abort that
the plan could have caught before the marker is written) and change no number. The change set is fit for the v13
manifest once the lead decides them.

## Findings

| id | class | file:line | failure scenario | suggested fix |
|---|---|---|---|---|
| SF-1 | SHOULD FIX | screening/stage_e_runner.py:712-759 (`plan_confirmation`), :789-835 (`run_confirmation_once`); write_member_record :430-447, write_record :418-427 | The plan resolves members, S_X, price paths, stores and the release calendar, but never looks at `out_dir`. If any `<cluster>_<member>_confirmation.json`, its `_trips.json`, or `<cluster>_confirmation_cluster.json` already exists there (an aborted earlier attempt, a wrong `--out-dir`, a dry run's directory reused), the marker is written (O_EXCL, 0o444), then `write_member_record` refuses "records are written once" on that member, the STOPPED record is written and the marker is consumed; the cluster-record collision fires only after every member has run. The dry run cannot see it either. Under A5 ("each member confirmed once behind a run-once marker") the lead would then need a decision, not a rerun | In `plan_confirmation`, before returning (so both `--dry-run` and the marker path get it): refuse by name if `out_dir` exists and holds any file matching `f"{cluster}_*_{CONFIRMATION_WINDOW}*.json"` or `f"{cluster}_{CONFIRMATION_WINDOW}_cluster.json"`; add a runner test (a planted record in `out_dir` refuses before the marker; the marker is absent afterwards) |
| SF-2 | SHOULD FIX | screening/stage_e_runner.py:800-808 | `--list` is hashed into the marker after checking only `cluster` and `harness_sha256`. A list the verdict would later refuse (a `start_dates` entry that is not the resolved S_X of a store root, e.g. MGC not equal to GC's S_X or MES not 2020-02-03; an ordinal not the freeze's; a `run: false` Tier A/B trial whose member is not in the `--untestable` declaration, or the reverse; a label outside LIST_LABELS; a missing frozen member) is sealed into the marker, the run happens once, and the only repair is a second list whose sha256 differs from the marker's: the pre-registration property the marker exists to protect | Before `write_marker`: `stage_e_verdict.parse_list` on the list (import is cycle-free: stage_e_verdict imports no runner module); refuse unless every frozen member is a trial with its ordinal, the set of Tier A/B trials listed `run: false` equals the declared not-run members, and `start_dates[root]` equals the plan's resolved S_X for every store root of every runnable member (vehicle keyed, as the record's `s_x` is). Tests for each refusal. If the lead prefers no code change: run `parse_list` on the list and compare its `start_dates` with the dry-run lines by hand before step 7, and record that in the STATE file (A5's ListReviewer covers the content, not this agreement) |
| N-1 | NOTE | data/stage_e_bars.py:310-328 | `check_price_path` checks group, `vendor_tick_fixed` and `tick_size` only (as the brief specifies): MNQ -> ES would pass (builder's O-1). The pinned declaration (sha256 in `PRICE_PATHS_SHA256`, FROZEN_INPUTS, and the test that pins `{"MGC": "GC", "MNQ": "NQ"}`) is the control | None required; the test pin is the right place for it |
| N-2 | NOTE | reports/stage_e22_price_paths.json | Mode 664 while the rulings file is 444; the sha256 pin and the manifest protect the bytes, but the two frozen inputs should look alike | `chmod 0444` before the manifest build |
| N-3 | NOTE | screening/stage_e_verdict.py:534-564 | R-E22-A10's descriptive Holm at K = 9 beside the K = 5 result is not produced (builder's O-4); `evaluate` computes one Holm at `clist.k_holm` | The lead's call: a second descriptive verdict with a k_holm 9 list, one call of `holm_tier_a(p, 9)` on the verdict's p values, or a `holm_descriptive_k9` field in `edge_chain` (small, testable) |
| N-4 | NOTE | screening/stage_e_runner.py:880-887 | After a marker run `main` prints nothing (the "members, refused" summary sits under `elif args.all`); the lead sees only the exit code, the records and the marker | Print the same summary for the marker branch |
| N-5 | NOTE | data/stage_e_bars.py:429-442, screening/stage_e_rules.py:212-231, screening/stage_e_engine.py:625-632 | A mapped leg's frame carries GC's `raw_symbol` and `instrument_id`; the engine's splice check ("instrument changed ... with exposure") and `is_roll_session` therefore follow GC's contracts, and the record's `bars["MGC"].path/sha256` name GC's file. All of this is the declared reading (the path store's own splices); nothing keys the tick value, cost table, q_c, eps or calendar on these columns (checked: tick value and costs come from `leg_inputs("MGC")`, test pins 100 cents per GC tick) | None; recorded so the trips' GC symbols under MGC trades surprise nobody |
| N-6 | NOTE | screening/stage_e_runner.py:736 | The dry run refuses whole on a store root with an empty window (`_start_dates` without `allow_empty` raises StartWindowEmpty) rather than listing that member as "would refuse" and continuing; it mirrors the run exactly (the run would abort the cluster there too), so it still finds the abort before the marker | Optional: catch the per-member refusal in the plan and print it as a line, so one dry run shows every abort |
| N-7 | NOTE | screening/stage_e_runner.py:627-632 | A by-design entry in the `--untestable` file must still carry the `missing_leg` key (null); `{"label": "inconclusive by design", "reason": ...}` without it is refused ("must hold exactly label, reason and missing_leg"). Loud, not silent; the builder's command sequence shows the full form but O-5 says "reason only" | The lead's declaration files include `"missing_leg": null` for by-design members; or relax the key check to make `missing_leg` optional for that label |
| N-8 | NOTE | data/stage_e_bars.py:386-426; screening/stage_e_engine.py:584-590, 655-657; screening/stage_e_rules.py:443-445 | The three re-booked MES prints are flagged `in_scheduled_closure`; the engine never fills, marks or forces on them, but `call_member` still shows them to the member (`visible()` masks only HINDSIGHT_FIELDS). After re-booking, each 16:59 CT print sits at the head of the next equity trade date (2020-03-31, 2020-04-01, 2020-07-01), one minute before the 17:00 open, where D.1 had it at the tail of the previous date. Exactly how v9 books NQ's 16:59 prints in the step 2 stores (reports/stage_e12_closure_rulings.json: 2020-03-31 Tue 16:59 -> trade_date 2020-04-01), so K8 flight's MES signal sees the same thing on NQ-style data; pre-existing engine behaviour, not a v13 change | None required; the lead should know in case flight's MES logic reads the first or last bar of a trade date |
| N-9 | NOTE | tests/test_h6_rod_run.py (builder's O-11) | Will keep failing under v13: h6_rod pins HARNESS_SHA256 = v12. h6_rod/ is outside HARNESS_DIRS and the test outside TEST_PATTERNS (verified against the would-be manifest: no h6_rod entry), so the manifest is unaffected; the full suite will show 1 failure | The lead's call: re-pin h6_rod, or record the expected failure in the progress entry |
| N-10 | NOTE | screening/stage_e_runner.py (about 910 lines; builder's O-9) | Over the 800-line guideline; R1/R2 (`plan_confirmation`, `dry_run`, `write_marker`, `run_confirmation_once`, `_plan_line`) are self-contained | Move them to screening/stage_e_run_once.py at the next harness change; not now (the brief fixed the file list) |
| N-11 | NOTE | screening/stage_e_runner.py:826-835 | If writing the STOPPED record itself fails (OSError, a read-only directory), that OSError replaces the engine's exception in the traceback; the marker still exists, so the run is still blocked | Wrap the STOPPED write in `try/except OSError` and re-raise the original |
| N-12 | NOTE | screening/stage_e_verdict.py:427-433 | A not-run record is accepted when its single label is any of the trial's labels, not necessarily `trial.not_run_label`; harmless (both labels mean "not run", the row text uses the list's), but `labels[0] == trial.not_run_label` would be exact when a trial carries both | Optional tightening, with the `check_record` test extended |
| N-13 | NOTE | screening/stage_e_start_dates.py:379-398, reports/stage_e_start_rule_K5.json | GC's entry will live in the K8 file (builder's choice, no new set id) while K5's file keeps MGC null; K5's MGC trials read GC's S_X from the K8 file, and their records' `start_rule` provenance names it. Ordering: the K8 `--set` must precede the K5 research re-run and K5 confirmation (the builder's sequence has it); `_check_agrees` compares the K8 doc's 6C and MCL with K3's and K4's files at write (same stores, so equal unless a store was rebuilt) | Record the choice in the stage notes; nothing to change |
| N-14 | NOTE | screening/stage_e_start_dates.py:394, 379-398 | `set_roots` opens the pinned declaration for every K-set build, so a K1 build (vehicle MNQ) would now compute NQ's entry (builder's O-2); no K1 build is planned, and the declaration is keyed by vehicle as D2/D4 declare it ("per exposure") | None |

Items the brief asked about that turned out correct are listed under "Verified" below, with how.

## 1. N1, the declared price path

- Store, S_X, sha: `confirmation_store` (data/stage_e_bars.py:429-442) resolves a mapped root to
  `_step2_parquet_path(path_root)` only after `check_price_path`; the runner's `_load_frames` (:351-368) and
  `confirmation_supply_days` (:371-396) index S_X and `step2_sha256` by `store_roots[leg.root]` (the path root's
  start-rule entry) and pass `path_root=_source(...)`. The vehicle's own step 2 store is never opened on the mapped
  path: the loader test runs MGC with no MGC store on disk and passes, and refuses `ConfirmationStoreMissing` when
  unmapped. A wrong pin on the path store refuses `ParquetHashMismatch` (tested).
- Economics keyed on the vehicle: `LegFrame.root` = vehicle; `_legs_inputs` -> `leg_inputs(leg.root)` (MGC's D8
  table and tick value); `StageERules(inputs, ...)` and `run_engine({root: frame})` keyed by root; nothing reads the
  product from the frame's `raw_symbol`/`instrument_id` (grep: only the engine's splice guard uses `instrument_id`).
  Runner test: a 1-tick GC move books 100 cents on MGC (GC's tick value is $10).
- Calendar: `read_leg` books on `load_group_calendar(product(root).group)` with root = vehicle; equal to the path's by
  `check_price_path` (test records the groups asked for: only MGC's).
- Research window untouched: `_load_frames`' research branch returns before `_store_roots` is ever called
  (:353-360, unchanged lines); `load_research_leg(leg.root, ...)` reads the vehicle's own research parquet (test pins
  the MGC research file name in the research record and the absence of `price_path`/`s_x`). The only research-run
  effect is inside `power` (the supply count), as D4's power check requires.
- Roll blackout and the D4 union: `splices_and_blackout(root, cal, _meta(path))` reads the PATH store's `rolls` on the
  vehicle's (= path's) calendar; `member_window` unions every leg's blackout (stage_e_align.py:64-72). The declared
  reading (the path store's own splices) is the one consistent with the bars the member actually sees.
- Supply = run window: `confirmation_supply_days` computes `intersection(days per leg from S_X) - union(blackouts)`
  (:388-395); `member_window` for STEP2 computes `common - blackout` from `leg.trade_dates` (stage_e_align.py:64-72),
  where `load_confirmation_leg`'s cut (`d >= start`) equals `read_leg_dates`' cut (`d >= start`). The research-only
  `UNSEEN_ROLL_DATES` exclusion does not apply to STEP2. Same rule.
- Declaration reader: `load_price_paths` refuses a missing file, another sha256, bad JSON, schema, empty paths, a
  non-string path, an unknown product (UnknownProduct -> PricePathInvalid), a group/grid/tick mismatch
  (PricePathMismatch), a chain, MES on either side; the pinned sha256 equals the file's (sha256sum 860f4b11...).

## 2. N2, start-rule entries for path roots

- `set_roots` (stage_e_start_dates.py:379-398): every named vehicle or leg is mapped through `declared.store_root`,
  so a mapped root never enters `build_set`'s loop and its stores are never asked for (test records the paths asked:
  NQ research, NQ step 2 only). The ML set returns before the declaration is read (unchanged).
- V_ref and D6 window of the path root: `build_set` calls `product_start_rule(GC, research_path=GC's research parquet,
  research_sha256=tables.research_parquet_sha256["GC"], window=day_session_window("GC"))`; the frozen tables carry a
  research sha and a D6 window for GC (07:20-12:30) and NQ (08:30-15:00) (checked from the E.2a tables only). D4: "the
  start rule then runs on the full-size contract": satisfied.
- Conflicts: `_check_agrees` (:633-646) compares the new doc with every existing file on shared roots (S_X, V_ref,
  medians, first trade dates, step2 sha) before writing; the loader (`load_start_entries`, unchanged) still refuses at
  load. K8 shares 6C with K3 and MCL with K4 (same stores); K5's MGC-null entry is not in K8. The loader never checks a
  file's root set against `set_roots`, so K5's existing file stays valid under v13 (checked :649-670).
- MES still comes from `mes_from_d1f` (:283-306): the D.1f record's sha256 pinned, S re-run to 2020-02-03, entry's
  `step2_sha256` = the record's confirmation parquet sha256 (82e256b4...).

## 3. N3, MES as a confirmation leg

- Path and pin: `mes_confirmation_path(research_root)` = `<research_root>/MES/` + `data.research_bars.
  CONFIRMATION_PARQUET_NAME` ("ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet"); the file exists under
  data/processed/MES; the expected sha256 is MES's start-rule entry (D.1f's); `read_leg` hashes before any row is
  read. No research root -> `ConfirmationStoreMissing` naming the research root (tested). S = 2020-02-03 comes from the
  K8 file's MES entry (D.1f re-run), applied as the cut like any S_X.
- The three rows: converting the three `ts_event_ns` with zoneinfo gives 2020-03-30 Mon 16:59 CDT, 2020-03-31 Tue
  16:59 CDT, 2020-06-30 Tue 16:59 CDT, inside the equity group's daily 16:00-17:00 CT halt; the loader test on the
  real rulings file recomputes `in_closure` True and `boundary` False for all three from the equity calendar with the
  L-3 rule, and the bookings 2020-03-31, 2020-04-01, 2020-07-01. D.1f's build summary records exactly 3 bars
  in_scheduled_closure (flag_counts and validation both 3, read from reports/stage_d1f_confirmation_build.json), and
  its `trade_date_range[0]` is 2019-05-06, so no MES row lies before STEP2_FIRST_TRADE_DATE (otherwise
  `refuse_trade_dates`, which runs before the label check, would have refused in E.12 ahead of the mismatch it did
  report). The same class as NQ's 16:59 CT prints in reports/stage_e12_closure_rulings.json (there: keep_and_flag,
  booked by the calendar; here: re-labelled to the calendar's date and flagged, the same result). The store's own
  `in_scheduled_closure` value for the rows was not read (builder's O-8); the rulings set it True regardless.
- Any other mismatch still refuses: `apply_rebookings` runs before `check_bookings`, which then checks the whole frame
  (tests: a non-enumerated mismatch refuses TradeDateMismatch in both readers; without rulings the store refuses as
  E.12 did). Rulings file checks: pinned sha256 (sha256sum f1cb92c3... equals the constant), schema, store sha equal
  to the hashed file, exactly six keys, MES, rebook_and_flag, no repeat; each entry must match exactly one row by
  ts_event, CT minute, store label, closure status and booking (8 mutations tested).
- Columns and dtype: `read_leg` reads `BAR_COLUMNS` (E.12 reached the label check on this file, so the Stage D store
  has every column); `apply_rebookings` re-assigns `trade_date` as strings for the whole frame, which every consumer
  already normalizes with `astype(str)`/`str()` (loader cut, `restrict`, the engine's bar iterator). O-3 (D.1 flag
  columns on MES) stands: the rules' flatten/no-new-positions/closure refusals key on the ordered root and MES is
  never ordered in K8.
- Rolls metadata: not re-verified here (would require opening the parquet); the builder's metadata-only parse is the
  evidence.

## 4. N4 and N5

- Runner: `load_untestable` (:605-639) refuses a wrong schema or cluster, an unknown member (through the freeze), a
  spec with other keys, a label outside the two, an empty reason, an untestable entry whose missing leg is not a frozen
  leg; research window refused by `_declared_not_run`. `screen_cluster` writes `not_run_member` records (status
  "not_run", label, reason, missing_leg, declaration provenance, no series, no s_x) and continues; an undeclared
  refusal still aborts (test: StartRuleMissing on NQ aborts before the cluster record).
- Verdict: `_trial` refuses a plain Tier A/B `run: false` ("disagree"), a run trial labelled untestable, an excluded
  trial listed run, an unknown label; `evaluate` still refuses "marked run in the list, no record"; a not-run record is
  accepted only for a Tier A/B trial listed `run: false` with that label (a not-run record on a run-listed trial
  refuses). Not-run trials: `rows[m].get("p_upper", 1.0)` enters Holm at p = 1 in the Tier A family (m counts them,
  R-E22-A13), `covered` False, named in `not_covered` with "not run: <label>", no series (so no DSR variance, no PBO
  set membership; `evaluate` adds a series only when `trial.run`). A by-design trial that was run and is listed
  `run: false` is checked and not used (the row says so).
- K: `parse_list` refuses k_holm absent, bool, str, 0, 10; `ConfirmationList.k_holm` is always set from the list
  (the dataclass default 9 is reachable only by direct construction in tests); `edge_chain` and the output echo it
  (test: K 5 gives alpha_k 0.01, threshold 0.01). Re-pin of tests/test_stage_e_verdict.py:653-655 done as five
  refusals. R-E22-A10's descriptive K = 9: N-3.

## 5. R1, R2, R3

- Marker order (`run_confirmation_once` :789-835): marker exists -> RunOnceRefusal before the preflight (test: a
  planted preflight that would fail is never reached); preflight; list check; `plan_confirmation` (freeze loaded and
  code verified, every runnable member resolved and its legs' inputs loaded, store roots and S_X per store root with
  no `allow_empty`, each store's existence and sha256 by hashing bytes, MES's rulings loaded and matched to the store
  sha, release-calendar coverage of max(S_X)..2024-02-29); `write_marker` O_WRONLY|O_CREAT|O_EXCL, 0o444; then
  `screen_cluster` (the first bar read is inside `_load_frames`; test asserts the marker exists when `_load_frames` is
  entered). `except BaseException` writes `<stem>_STOPPED.json` (O_EXCL, 0o444) and re-raises (tested with a planted
  engine failure). A resolution refusal writes no marker (tested). Gaps: SF-1 (out_dir), SF-2 (list content), N-11.
- Dry run: `dry_run` = preflight + `plan_confirmation(supply=True)`; `confirmation_supply_days` reads `ts_event` and
  `trade_date` only; the CLI test replaces `run_engine` and `load_confirmation_leg` with failures and asserts the out
  dir does not exist afterwards. Flag gating (`--untestable`, `--run-once-marker`, `--list`, `--dry-run` need
  `--all --window confirmation`; `--list` needs the marker; no marker with `--dry-run`) tested via rc 2.
- R3: `registry_n` records list_program_n, registry_current_n, registry_error, equal; never refuses (test with a
  planted TrialRegistryError). The CLI adds `program_n_check`.

## 6. Tests

- `nice -n 10 uv run python -m pytest -q -p no:cacheprovider tests/test_stage_e_*.py` (no PYTHONPYCACHEPREFIX):
  **753 passed, 1 warning (pre-existing RuntimeWarning in stage_e_stats_power.py:218) in 189.9 s**. Equals the
  builder's 753 (697 + 56).
- The 28 other test files importing a changed module (grep for stage_e_bars, stage_e_runner, stage_e_start_dates,
  stage_e_verdict, harness_freeze over tests/test_*.py, minus test_stage_e_*, test_forward_*, test_microbook_*):
  **673 passed, 1 skipped, 1 failed in 299.6 s**. The failure is
  tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha (N-9, the builder's
  O-11 (b)). The builder's other expected failure, test_harness_freeze's real-tree-matches-manifest test, passed in
  this run: the modified reports/stage_e2b_harness_freeze.json in the working tree (the lead's, not reviewed) matches
  the current tree at 01:57 PDT (the run's end, log mtime). Holdout at 01:57: sealed_ok true, unlocks_logged 0;
  REGISTRATION.md 0 bytes.
- What the new tests pin (all synthetic data except the two real-file pins): N1 mapped read keyed/booked as the
  vehicle with the path's splices, pin on the path store, 6 refusal pairs of `check_price_path`, the real
  declaration's mapping and sha256 and FROZEN_INPUTS membership, declaration refusals (missing, other bytes, schema,
  group mismatch, chain, unknown product); N2 `set_roots` mapping and inputs, `build_set` never asking for the
  vehicle's stores, the write-time conflict guard; N3 the rebooked rows flagged and dated, the non-enumerated mismatch
  refusal, the E.12 refusal without rulings, 8 inexact rulings refusals, the real rulings file's three rows recomputed
  from timestamps and the calendar; runner N1 (path S_X, GC file under the MGC key, 100-cent GC ticks, supply from the
  path root, research unmapped, wrong pin refuses, unmapped micro still empty), N3 (MES at 2020-02-03, blackout
  union, closure_bars 1, research root required), N4 (not-run record and continue, undeclared refusal aborts, 4 bad
  declarations, research window refused), R1 (marker before `_load_frames`, 0o444, present marker before preflight,
  no marker on resolution refusal, STOPPED beside it, list for another cluster), R2 (dry run writes nothing, flag
  gating); verdict N4 (3 cases + 5 listing rules), N5, R3.
- Gaps (none blocking): no test that `plan_confirmation` refuses on release-calendar non-coverage; no test of the
  marker's `not_run` list with `--untestable`; SF-1 and SF-2 have no behaviour to test yet.

## 7. Manifest scope and tree

- HARNESS_DIRS (rules sim screening funnel data ml_route compute strategy/stage_e, plus strategy/members scans) and
  TEST_PATTERNS (unchanged) contain no forward/, microbook/, test_forward_* or test_microbook_* pattern.
  `harness_freeze.manifest_categories(REPO_ROOT)` (a listing, nothing written): 1065 files, none under forward/,
  microbook/ or .claude/, no test_forward_*/test_microbook_* (11 such files are untracked in tests/), both v13 inputs
  listed as frozen inputs, tests/test_stage_e_runner_v13.py listed as a stage_e test, no h6_rod entry.
- `git status --porcelain -- rules sim screening funnel data ml_route compute strategy tests`: exactly the five
  modified modules, the four modified test files and the one new test file (plus the 11 Part B tests, outside the
  patterns). No file under strategy/, sim/, rules/, funnel/, base_rules/, multiday/, live/, ops/ changed. Tracked
  changes outside the allowed set: only reports/stage_e2b_harness_freeze.json (the lead's, ignored).
- `harness_freeze.py` diff: FROZEN_INPUTS += the two files, nothing else (4 lines).

## 8. "Each member exactly as its cluster freeze defines it"

`resolve_member`/`verify_cluster_code` are unchanged and run in both the plan and `screen_member`; legs come from the
freeze and are compared (`legs != decl.legs` refuses). The confirmation run differs from the frozen definition only
in the declared ways: a mapped vehicle's bars come from the declared path store (with its contracts and splices, N-5),
MES's bars from the Stage D store with three re-booked prints (N-8), and declared members are not run (recorded in
their records, the cluster record and the marker, with the declaration's sha256). I found no other path.

## Verified, and how

- Diffs read in full for the five modules and five test files; surrounding unchanged code read by section
  (`check_bookings`, `splices_and_blackout`, `read_leg`, `restrict`, `member_window`, `screen_member`,
  `write_member_record`, the engine's bar iterator, `is_closure`, `visible`, `call_member`, `ask_member`, the rules'
  flag refusals, `mes_from_d1f`, `set_roots`, `build_set`, the start-rule loader, `parse_list`, `check_record`,
  `_series`, `_trial_row`, `edge_chain`, `null_statement`, `resolution_table`, `evaluate`, `load_records`).
- sha256sum of the two inputs equals the module constants; `stat` modes 664 and 444.
- Three MES timestamps converted with zoneinfo independently of pandas; D.1f summary fields read from JSON only.
- Frozen tables: research sha and D6 window present for GC, NQ (and MGC, MNQ, MES, MBT, 6C, MCL).
- Store directories: data/processed/GC, NQ, MES (research and confirmation parquets by name only), processed_step2/GC,
  NQ, MGC, MBT exist; processed_step2/MNQ does not (consistent with R-E22-A5).
- holm_tier_a's docstring and `holm_alpha_k` accept K in 1..9; label strings equal across stage_e_stats_power,
  stage_e_runner and stage_e_verdict.
- The import direction: the runner imports stage_e_start_dates at module load; stage_e_start_dates reaches the runner
  lazily through `_runner()`; `__main__` delegates to `screening.stage_e_runner.main()` (C-1), so `PricePathInvalid`
  is one class however the runner is launched.

## Not checked

- No runner, start-rule or verdict command on real data; no parquet opened (the MES `rolls` metadata parse rests on
  the builder's report).
- The full test suite (the lead's); the K8 `--set` build and the research re-runs (the lead's, after the manifest).
- Whether K8 flight's MES logic reads the first or last bar of a trade date (member code, out of scope; see N-8).

## Recheck of the review fixes

02:04 to 02:09 PDT, against the "Review fixes" section of reports/stage_e22_harness_change.md (02:00-02:08) and the
working tree (the manifest dd2bcc60... ignored as instructed). Read: `check_out_dir_free`, `plan_confirmation`,
`dry_run`, `check_list_against_plan`, `run_confirmation_once`, `main` (screening/stage_e_runner.py);
`edge_chain`, `check_record` (screening/stage_e_verdict.py); the new tests in tests/test_stage_e_runner_v13.py
(:440-580) and tests/test_stage_e_verdict.py (N-3, N-12). `nice -n 10 uv run python -m pytest -q
-p no:cacheprovider tests/test_stage_e_runner_v13.py tests/test_stage_e_verdict.py`: **140 passed in 2.9 s**
(log mtime 02:08). No NEW BLOCKING.

| id | status | what I checked |
|---|---|---|
| SF-1 | RESOLVED | `check_out_dir_free(cluster, out_dir)` is the first statement of `plan_confirmation`; it globs `{cluster}_*_confirmation*.json` (records and trip lists) and `{cluster}_confirmation_cluster.json`, refuses by name ("records are written once; use a fresh --out-dir"), ignores another cluster's files and a missing directory. `run_confirmation_once` passes `out_dir`; `dry_run` and the CLI's `--dry-run` branch pass `out_dir=args.out_dir`. Test: 3 planted names refuse both the marker path (no marker afterwards) and the dry run; a K2 file does not block K1 |
| SF-2 | RESOLVED (one residual, R-1 below) | `check_list_against_plan` runs after the plan and before `write_marker`: `stage_e_verdict.parse_list` (its VerdictRefusal re-raised as RunOnceRefusal), {member: ordinal} equal to the frozen members, Tier A/B `run: false` trials equal to the declared not-run members, `start_dates[root]` equal to every runnable member's resolved S_X per leg root. Tests: an agreeing list is sealed (sha256 in the marker, not-run member recorded); 8 contradictions refuse with no marker written. The import stage_e_verdict -> runner direction is cycle-free |
| N-2 | RESOLVED | `stat`: reports/stage_e22_price_paths.json is now 444 |
| N-3 | RESOLVED | `edge_chain` adds `holm_descriptive_k9` = `holm_tier_a(pvalues, 9)` on the same p values with a "descriptive only" note; `holm` and the trial verdicts still use `clist.k_holm`. Test: p = 0.008 rejects at K 5 (threshold 0.01) and not at K 9, and `passes["holm"]` follows K 5 |
| N-4 | RESOLVED | `main` prints "<cluster> confirmation: N members, R refused", NOT RUN and REFUSED lines on both the marker and the plain `--all` branch (one `if args.all` with a conditional call). Test pins the first line |
| N-8 | kept by ruling | no change; the declared keep-and-flag reading, as v9 |
| N-9 | recorded by ruling | no change; the full suite's expected h6_rod failure (pins v12, inside the E.20 H6 freeze) |
| N-11 | RESOLVED | The STOPPED write sits in `try/except OSError`, the failure goes to stderr, `raise exc` re-raises the original exception; the marker stays. Test: `stopped_path` pointed into a missing directory, the planted RuntimeError still propagates, the marker exists |
| N-12 | RESOLVED | `check_record` requires `labels[0] == trial.not_run_label` (the first of the two labels the trial carries). Test: a trial carrying both labels accepts its untestable record and refuses the by-design one |
| N-1, N-5, N-6, N-7, N-10, N-13, N-14 | no change (lead ruling) | not re-checked; nothing in the fixes touches them |

R-1 (NOTE, residual of SF-2, not blocking): `check_list_against_plan` does not compare the list's
`cluster_freeze_sha256` with `plan["cluster_freeze_sha256"]`, nor each trial's `vehicle` with its member's traded
leg; both are refused by the verdict later (`check_record` "cluster_freeze_sha256 differs from the list", `_series`
"series vehicle ... is not the list's"), so a list wrong in either way would still be sealed into the marker. The
SF-2 tests themselves seal a list whose `cluster_freeze_sha256` is "cd" x 32. Two more comparisons in
`check_list_against_plan` (the plan already carries the freeze sha; the traded leg is `decl.legs`' traded root,
available where the plan builds each row) would close it; until then the ListReviewer's check of the list's freeze
sha and vehicles against the freeze file is the guard. Lead's call.

Recheck counts: 0 BLOCKING, 0 NOT RESOLVED among the fixed items (SF-1, SF-2, N-2, N-3, N-4, N-11, N-12 all
RESOLVED), 1 residual NOTE (R-1). Holdout untouched by this recheck (no data command run).
