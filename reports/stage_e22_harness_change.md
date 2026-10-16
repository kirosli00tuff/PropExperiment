# Stage E.22 Part A: harness v13 change set (code and tests only)

Worker: HarnessBuilder-OpusXHigh, 2026-10-16 01:15-01:40 PDT, against
reports/stage_e22_briefs/brief_harness_v13.md, the audit reports/stage_e22_briefs/partA_harness_audit.md
(section 8), the lead's rulings reports/stage_e22_briefs/partA_rulings.md and the declaration
reports/stage_e22_price_paths.json (sha256 860f4b11d75aaf8bacb52871944d902d858cbe5edaa9c00a0b76921f270bb425,
checked). Not done here, by the brief: no manifest build (reports/stage_e2b_harness_freeze.json untouched), no commit,
no runner command on either window over real data, no confirmation-window bar value read except the N3 diagnostic
(section N3). No member code, engine, rules, cost table, calendar, forward/, microbook/, multiday/ or base_rules/
file was edited. Under v12's manifest the preflight now refuses (files changed), as intended until the lead
builds v13.

## Files changed

| File | What |
|---|---|
| data/stage_e_bars.py | N1 price path in the confirmation loader; N3 MES store resolver and enumerated rebookings; R1/R2 store check |
| screening/stage_e_start_dates.py | N1/N2 the declaration reader (pinned sha), mapped set roots, conflict guard at write |
| screening/stage_e_runner.py | N1/N3 in `_load_frames` and `confirmation_supply_days`; N4 declared not-run records; R1 marker; R2 dry run; CLI flags |
| screening/stage_e_verdict.py | N4 not-run Tier A/B trials; N5 K from the list; R3 registry N |
| screening/harness_freeze.py | FROZEN_INPUTS += the two new inputs (nothing else) |
| reports/stage_e22_mes_closure_rulings.json | NEW, mode 0444, sha256 f1cb92c3868d02327358599d211d0dbd1218318dec27278613c9aeb6b3bb2a69 (N3) |
| tests/test_stage_e_loader.py, test_stage_e_start_dates.py, test_stage_e_verdict.py | new v13 tests appended; verdict K pins re-pinned |
| tests/test_stage_e_runner.py | one stub signature (`no_s_x` takes the new `research_root`) |
| tests/test_stage_e_runner_v13.py | NEW: runner world tests for N1, N3, N4, R1, R2 |

Pinning choice (N1, asked by the brief): BOTH. The declaration is listed in `harness_freeze.FROZEN_INPUTS` (so the
v13 manifest hashes it) AND its sha256 is a module constant `screening.stage_e_start_dates.PRICE_PATHS_SHA256`
(so a run refuses a different file even where the preflight is replaced, e.g. in tests). Same for the MES rulings
(`data.stage_e_bars.MES_CLOSURE_RULINGS_SHA256` plus FROZEN_INPUTS).

## N1 declared price path (confirmation branch only)

- `data/stage_e_bars.check_price_path(vehicle, path_root)` (:310): refuses (`PricePathMismatch`, a
  `StageEBarRefusal`) unless the products share `group`, `vendor_tick_fixed` and `tick_size`, the path names
  another root, and neither is MES.
- `confirmation_store(root, step2_root, *, path_root, research_root)` (:429) resolves the file:
  mapped -> the path root's step 2 store; MES -> N3; else the root's own store.
- `load_confirmation_leg(..., path_root=None, research_root=None)` (:475) and `read_leg_dates(...)` (:496) read
  that file with every existing check; rows are booked on the VEHICLE's group calendar (`product(root).group`,
  equal to the path's by the check); the LegFrame keeps `root` = the vehicle and `path`/`sha256` = the path file.
- Roll blackout reading (declared, as the brief asks): for a mapped leg the blackout is the PATH store's own
  splices (its `rolls` metadata booked on the group calendar), i.e. the splices the bars actually have.
- `screening/stage_e_start_dates.load_price_paths(root, expected_sha256=PRICE_PATHS_SHA256)` and `price_paths()`:
  the one reader of the declaration; refuses (`stage_e_runner.PricePathInvalid`) a missing file, another sha256,
  another schema, an unknown product, a chain; returns `PricePaths(paths, file, sha256)` with `store_root(r)`.
- Runner (`_price_paths` :332, `_store_roots` :337, `_load_frames` :351, `confirmation_supply_days` :371): S_X and
  the pinned sha256 come from the PATH root's start-rule entry; frames are keyed by the vehicle; the record gets
  `s_x` keyed by the vehicle (value = the path's S_X), `start_rule` keyed by the path root,
  `price_path` {vehicle: path} (empty `{}` when nothing is mapped) and `price_path_declaration` {path, sha256}.
  The research branch of `_load_frames` is unchanged (the micro's own research bars stay the screened series);
  the research run's power check (`_research_statistics`, which counts the CONFIRMATION supply) does use the
  mapping, and records `price_path` inside `power`.
- Micro's own economics: unchanged code paths, tick value / D8 costs / q_c / eps / release rows all key on the
  vehicle (audit section 2). Test: a 1-tick GC move books gross 100 cents on MGC (MGC $1.00, not GC's $10).

## N2 start-rule entries for path roots; buildable K8

- `set_roots` (cluster sets): each vehicle or leg contributes `declared.store_root(r)`; a mapped root's own
  stores are never asked for; when any root of the set is mapped, the declaration's path and sha256 join the set's
  `inputs` (and so the written file's `inputs`). The ML set is unchanged.
- Real roots now (computed with `set_roots`, no bar read): K8 = 6C GC MBT MCL MES NQ (MGC->GC, MNQ->NQ; MES from
  D.1f's pinned record as before); K5 would be GC MHG but K5's file already exists (write-once) and is NOT
  rebuilt: it keeps MGC null; the runner never asks for MGC's entry once MGC is mapped, and GC's entry comes from
  the K8 file (my choice: no new set id). K3 and K6 are unchanged (no mapped root).
- New guard `_check_agrees` in `write_start_rule`: a new set file that disagrees with any existing file on a shared
  root (S_X, V_ref, medians, first trade dates, step 2 sha) is refused with StartRuleConflict BEFORE it is
  written (the loader would otherwise refuse only at the next run). K8's 6C is checked against K3's file, MCL
  against K4's.
- The lead runs exactly one `--set`: K8 (K3, K4, K5, K6 files exist; reports/stage_e_start_rule_K3.json and _K6.json
  are on disk already). Command in the sequence below.

## N3 MES as a confirmation leg

Finding (diagnostic, brief N3): reports/stage_d1f_confirmation_build.json does NOT name the rows (flag counts
only: `flag_counts.in_scheduled_closure` 3, `validation.bars_in_scheduled_closure` 3), so I ran the allowed
diagnostic (scratchpad n3/diag.py): it checked the file's sha256 against D.1f's pinned 82e256b4... (True), read
only `ts_event` and `trade_date`, booked every row on the equity calendar, and printed ts_event, label, booking
of the mismatching rows only. Output: exactly 3 rows:

| ts_event (ns) | CT | store label | calendar booking |
|---|---|---|---|
| 1585605540000000000 | 2020-03-30 Mon 16:59 | 2020-03-30 | 2020-03-31 |
| 1585691940000000000 | 2020-03-31 Tue 16:59 | 2020-03-31 | 2020-04-01 |
| 1593554340000000000 | 2020-06-30 Tue 16:59 | 2020-06-30 | 2020-07-01 |

All three are scheduled-closure prints: computed from the timestamps alone with the Stage E equity calendar
(`assign_trade_dates`, close-minute rule L-3): in_closure True, boundary False (inside the daily 16:00-17:00 CT
halt, beyond the close minute). They match D.1f's 3 closure-flagged bars by date ("single bars on 2020-03-30,
03-31, 06-30", reports/stage_d1f_run_STATE.md row 2') and the same class as NQ's 2020-03-31 and 2020-06-30 16:59
bars in reports/stage_e12_closure_rulings.json. So the lead's conditional ruling applies; N3 was built.
(I did not read the store's `in_scheduled_closure` column for these rows; the rulings set the flag True.)

- reports/stage_e22_mes_closure_rulings.json (schema `stage_e_mes_closure_rulings/1`, 0444): the ruling text, the
  finding, the store {path, sha256 82e256b4...}, and the 3 entries {root MES, ts_event_ns, ct, store_label,
  trade_date (the booking), ruling "rebook_and_flag"}.
- `load_mes_closure_rulings(store_sha256)` (:349): refuses unless the file hashes to the pinned sha, has the schema,
  names the store being read, and every entry holds exactly the six keys, MES, rebook_and_flag, no repeat.
- `apply_rebookings` (:386): every entry must match exactly one row (same ts_event, CT minute, store label), be a
  closure print beyond the close minute on the calendar, and be booked to the entry's date; then those rows get
  the calendar's trade date and `in_scheduled_closure` True (new frame, nothing mutated). `check_bookings` then
  runs on the whole file: any other mismatch still refuses (TradeDateMismatch).
- Resolver: MES's confirmation leg = `<research_root>/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet`
  (`mes_confirmation_path`), sha256 pinned by MES's start-rule entry (D.1f's), read as a step 2 store and cut at
  S_X; in `_load_frames` and `confirmation_supply_days` (the runner passes its research root; the supply count
  and the research power check now take `research_root`). Without a research root MES refuses
  (ConfirmationStoreMissing, named).
- Rolls metadata (brief: key-value metadata only, no rows): `_meta` + `splices_and_blackout` on the real file
  parse: 19 rolls with `ts_ns`, 19 splice trade dates 2019-06-17..2023-12-13, blackout 57 dates; the file records
  no `splice_trade_dates`/`roll_blackout_dates` of its own (nothing to cross-check).

## N4 trials with no record

- Runner: `--untestable FILE` (schema `stage_e_untestable/1`: {"schema", "cluster", "members": {label: {"label",
  "reason", "missing_leg"}}}), confirmation window and `--all` only. `load_untestable` (:605) checks every member
  is in the freeze, label is "untestable on owned data" (missing_leg must be one of the member's frozen legs) or
  "inconclusive by design" (reason only; see O-5), reason non-empty, exactly those keys. `screen_cluster` (:661)
  writes for each declared member a not-run record (`not_run_member` :642: identity fields, harness and freeze
  sha256, status "not_run", labels [label], reason, missing_leg, `not_run_declaration` {path, sha256}, screen /
  series / power None, no `s_x`, an empty trip list) and continues; any undeclared refusal still aborts (test).
  The cluster record adds `not_run_members` and the declaration.
- Verdict: `LIST_LABELS` += "untestable on owned data"; a Tier A/B trial carrying it or "inconclusive by design"
  may be listed `run: false` (`_trial`); "untestable" can never be listed run; a plain Tier A/B `run: false` is
  still refused ("disagree"), and a run trial without a record is still refused ("marked run in the list, no
  record"). A not-run trial: no record needed; a runner not-run record is checked (identity fields, label in the
  list's labels; no S_X needed) and not used; row status "not run", reason "Tier A listed not run: <label>";
  Holm at p = 1 (in the family, never rejecting); not covered (`not_covered` reason "not run: <label>"); adds no
  series to DSR or PBO. A by-design/untestable trial listed run:false whose member WAS run (record status "run")
  is checked and not used.

## N5 K from the list

`HOLM_K = 9` stays as the upper bound; `parse_list` accepts `k_holm` as an int in 1..9 (bool, str, None, 0, 10
refused); `ConfirmationList.k_holm`; `edge_chain` calls `holm_tier_a(pvalues, clist.k_holm)`; the output's
`k_holm` echoes it. Re-pinned tests/test_stage_e_verdict.py:653-655 (old "K 8 is not 9") as five refusals; new
test: k_holm 5 gives alpha_k 0.01 and threshold 0.01 for one Tier A trial.

## R1 run-once marker

`--run-once-marker PATH` (confirmation `--all` only; optional `--list LIST`, which requires the marker).
`run_confirmation_once` (:789): marker present -> RunOnceRefusal before the preflight; preflight; the list (if
given) must carry the cluster and the preflighted harness, its path and sha256 recorded; `plan_confirmation`
(:712) resolves every member: frozen member and legs (`resolve_member` imports the verified code), leg inputs,
price paths, S_X per store root (empty or missing refuses), each store's existence and pinned sha256 (bytes
hashed, no row read; MES also loads its rulings), release-calendar coverage of S_X..2024-02-29; declared not-run
members listed. Then `write_marker` (O_WRONLY|O_CREAT|O_EXCL, 0o444; content: schema stage_e_run_once/1,
cluster, window, harness and freeze sha256, list, member count, not-run members and declaration, stores, out
dir, created_utc) BEFORE `screen_cluster` (so before any `_load_frames`); any later exception (BaseException)
writes `<marker stem>_STOPPED.json` beside it (O_EXCL, 0o444, error and traceback tail) and re-raises. Without the
flag the runner behaves as before.

## R2 dry run

`--dry-run` (confirmation `--all` only, not with the marker): preflight, `plan_confirmation(..., supply=True)`
(everything R1 resolves plus each member's supply via `confirmation_supply_days`, which reads only `ts_event` and
`trade_date`), one line per member (ordinal, member, s_x per leg, price path, supply days, store names and sha
prefixes; not-run members as "not run (label)"), a closing line; writes nothing, never runs the engine (tested
with the engine and the bar loader replaced by failures).

## R3

`stage_e_verdict.registry_n(program_n)` -> {list_program_n, registry_current_n (screening.trial_registry.
current_n()), registry_error, equal}; the CLI adds it as `program_n_check` to the verdict output; never refuses
(an unreadable registry is recorded by name).

## Manifest patterns (brief: other workers' paths)

`harness_freeze` changes only FROZEN_INPUTS. HARNESS_DIRS (rules sim screening funnel data ml_route compute
strategy/stage_e, plus strategy/members scans) do not include forward/ or microbook/; TEST_PATTERNS
(test_stage_e_*, test_ml_route_*, test_compute_*, test_e2b_*, test_cross_platform_static, test_build_release_calendar,
test_leakage_canaries, test_harness_freeze, _stage_e_*, _compute_fixtures, test_e14_*, _e14_*) match no
tests/test_forward_*.py or tests/test_microbook_*.py (9 test_forward_* files are on disk now, untracked); no entry
module imports forward/ or microbook/. The new tests/test_stage_e_runner_v13.py IS picked up (test_stage_e_*), as
intended. Before the build, the lead should still run `git status --porcelain -- rules sim screening funnel data
ml_route compute strategy tests` and check nothing unexpected sits under a harness directory.

## Tests

Before (baseline, unchanged tree, 01:16): `tests/test_stage_e_*.py` 697 passed.
After: see "Pytest counts" at the end (filled from the logs).
New or changed tests (collected counts): verdict +13 (10 new v13 cases: N4 3 + 5 parametrized, N5 1, R3 1;
plus the K re-pin, 2 cases replaced by 5), loader +19 (N1 1 + 6 parametrized, N3 3 + 8 parametrized, the real
rulings file 1), start dates +5 (N1/N2), runner v13 file +19 (N1 4, N3 2, N4 2 + 4 parametrized, R1 5, R2 2);
total +56. tests/test_stage_e_runner.py: one stub signature only (30 cases, unchanged count).

## Lead command sequence afterwards

(Replace V13 by the sha256 the build prints. Paths as in E.5 and E.12: research root data/processed, step 2 root
data/processed_step2. `uv run python -m data.holdout status` at start and end.)

1. Independent review of this diff (Fable), then the manifest:
   `uv run --no-sync python -m screening.harness_freeze build` (prints V13), then
   `uv run --no-sync python -m screening.harness_freeze verify --expected V13`; commit per the stage prompt
   (the two new reports files are untracked: reports/stage_e22_price_paths.json, reports/stage_e22_mes_closure_rulings.json).
2. Start rule (only K8 is new):
   `uv run python -m screening.stage_e_start_dates --harness-sha256 V13 --set K8 --research-root data/processed --step2-root data/processed_step2`
   Expect products 6C GC MBT MCL MES NQ; inputs carry the declaration; refused if 6C/MCL disagree with K3/K4.
3. Research re-runs for power (one per cluster, fresh out dirs; then the E.5 field-by-field match apart from
   power, harness_sha256, created_utc and the trip files' record_sha256):
   `uv run python -m screening.stage_e_runner --harness-sha256 V13 --cluster K5 --all --window research --research-root data/processed --step2-root data/processed_step2 --out-dir reports/stage_e22_power_k5`
   and the same for K3, K6, K8 (out dirs reports/stage_e22_power_k3, _k6, _k8). K8 needs `--research-root
   data/processed` for MES's store (O-7).
4. Lists (lead): schema stage_e_confirmation_list/1, k_holm 5, program_n 533, start_dates keyed by vehicle and
   leg root (MGC: GC's S_X from the K8 file, MNQ: NQ's S_X, MES 2020-02-03, MBT, MCL, 6C, ...), every frozen member
   listed (K3 30, K5 11, K6 27, K8 4); by-design or untestable Tier A/B trials `run: false` with the exact label.
5. Optional not-run declaration per cluster (only for members that must not be run, e.g. wkndbtc if R-E22-A6
   applies: {"label": "untestable on owned data", "missing_leg": "MBT", "reason": "BTC full-size history for the
   MBT signal path not owned (R-E22-A6)"}): reports/stage_e22_untestable_KX.json, schema stage_e_untestable/1.
6. Dry run per cluster (no marker):
   `uv run python -m screening.stage_e_runner --harness-sha256 V13 --cluster KX --all --window confirmation --research-root data/processed --step2-root data/processed_step2 --out-dir reports/stage_e22_confirm_kx --dry-run [--untestable reports/stage_e22_untestable_KX.json]`
7. Confirmation, once per cluster:
   `uv run python -m screening.stage_e_runner --harness-sha256 V13 --cluster KX --all --window confirmation --research-root data/processed --step2-root data/processed_step2 --out-dir reports/stage_e22_confirm_kx --run-once-marker reports/stage_e22_KX_RUN_ONCE.json --list reports/stage_e22_kx_confirmation_list.json [--untestable reports/stage_e22_untestable_KX.json]`
8. Verdict per cluster:
   `uv run python -m screening.stage_e_verdict --harness-sha256 V13 --list reports/stage_e22_kx_confirmation_list.json --records reports/stage_e22_confirm_kx --out reports/stage_e22_kx_verdict.json`

## Open points

- O-1 `check_price_path` checks group, grid and tick only, as the brief specifies; it cannot tell the
  underlying (MNQ->ES would pass: equity, 0.25, same grid). The pinned declaration is the control.
- O-2 The declaration is keyed by vehicle, not cluster: if K1 (vehicle MNQ) were ever built or confirmed under
  v13, MNQ would read NQ (`--set K1` would compute NQ's entry). No K1 run is planned.
- O-3 MES's Stage D store carries D.1's flag columns (flatten, no-new-positions, halt), not the Stage E group
  policy's. In K8 flight MES is a signal leg; the engine's flag checks key on the ordered (traded) root
  (stage_e_rules.py:409-418, 494-497), so they do not act on MES there. Any traded-MES use would need review.
- O-4 A Tier A not-run trial's edge-chain verdict reads "no edge" (first failing step "holm", p = 1), as for any
  Tier A trial without a series; a distinct wording is the lead's call. The descriptive Holm at K = 9
  (R-E22-A10) is not produced by the module: one call of `holm_tier_a(p, 9)` on the verdict's p values, or a list
  with k_holm 9 run as a second, descriptive verdict.
- O-5 Extension beyond the brief's "untestable": the not-run declaration also accepts "inconclusive by design"
  (reason only), so R-E22-A9's "it is not run" can be honoured under `--all`. Unused, by-design members are run
  as before and their records are checked and not used when listed run:false.
- O-6 The K5 MGC trials' power now counts GC's supply, superseding E.5's supply 0 for them; the research
  re-runs' power objects carry `price_path`.
- O-7 MES is resolved under `--research-root`; give data/processed (where D.1f's store sits) on K8's research and
  confirmation commands, or MES refuses by name.
- O-8 The N3 identification rests on timestamps and the calendar; the store's own `in_scheduled_closure` value
  for the 3 rows was not read (diagnostic limit); D.1f's count (3) and dates match.
- O-9 screening/stage_e_runner.py is now about 910 lines (over the 800 guideline); R1/R2 could move to their own
  module, which the brief's file list did not allow.
- O-10 `--untestable`, `--run-once-marker`, `--list` and `--dry-run` require `--all --window confirmation`
  (parser error otherwise); `--list` requires the marker.
- O-11 Two tests outside the stage_e set fail now and are expected to: (a)
  tests/test_harness_freeze.py::test_the_real_tree_matches_the_committed_manifest_when_it_exists (the tree is no
  longer v12; passes once the v13 manifest is built); (b)
  tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha: h6_rod pins
  HARNESS_SHA256 = v12 ece91ae8... (h6_rod/constants.py:95), so its CLI now refuses at the harness preflight
  instead of the freeze check, and will keep failing under v13 unless h6_rod's pin or the test changes (outside
  this brief's files; the lead's call).

## Pytest counts

All with `nice -n 10 uv run python -m pytest -q -p no:cacheprovider`, no PYTHONPYCACHEPREFIX.

| Run | Before (01:16, unchanged tree) | After (01:32-01:40) |
|---|---|---|
| tests/test_stage_e_*.py | 697 passed | 753 passed (+56 new), 0 failed |
| the 28 other test files importing a changed module (test_c1_loader, test_e14_c2, test_base_rules_store, test_e2b_step2_store, test_e14_config_v10, test_e2b_pull_step2_e12, test_compute_units, test_e2b_pull_step2, test_e2b_step2_store_v9, test_e14_pull_hist, test_e14_hist_store, test_h6_rod_run, test_ml_route_test_entry, test_cross_platform_static, test_pattern_search_world_check, test_ml_route_distil_entry, test_k8_members_oilcad, test_e17_v12_hist_store, test_ml_route_e2e, test_e17_v12_pull_hist, test_harness_freeze, test_ml_v2_phase1_support, test_ml_v2_phase1_world, test_k8_members_flight_engine, test_ml_route_stage_e_adapter, test_ml_route_stage_e_inputs, test_ml_v2_phase1_freeze, test_ml_v2_phase1_gate0) | not run before (no baseline taken) | 672 passed, 1 skipped, 2 failed (O-11, both the real-tree preflight against v12) |

`ruff check` on the five changed modules and four test files: only two pre-existing E501 lines in
screening/harness_freeze.py (:158, :258), none from this change. Holdout: `python -m data.holdout status`
sealed_ok true, unlocks_logged 0 (01:37); REGISTRATION.md 0 bytes.

## Review fixes (lead rulings on reports/stage_e22_harness_review.md, 02:00-02:08 PDT)

Same files only (screening/stage_e_runner.py, screening/stage_e_verdict.py and two test files); no manifest, no
commit, reports/stage_e2b_harness_freeze.json untouched.

- SF-1 `check_out_dir_free(cluster, out_dir)` (runner :712), called first in `plan_confirmation` (now takes
  `out_dir`), so `--dry-run` (`dry_run(..., out_dir)`, the CLI passes `--out-dir`) and the marker path
  (`run_confirmation_once`) both refuse by name (RunnerRefusal "records are written once; use a fresh --out-dir")
  when `out_dir` holds any `{cluster}_*_confirmation*.json` (records and trip lists) or
  `{cluster}_confirmation_cluster.json`, before any marker. Another cluster's files do not count.
- SF-2 `check_list_against_plan(payload, plan, name)` (runner :787), run in `run_confirmation_once` after the plan
  and before `write_marker`: `stage_e_verdict.parse_list` must accept the list (its refusal is re-raised as
  RunOnceRefusal "the verdict would refuse the list"); the list's {member: ordinal} must equal the frozen members'
  exactly (missing, extra or wrong ordinal refuse); the Tier A/B trials listed `run: false` must equal the members
  declared in `--untestable`; `start_dates[root]` must equal the plan's resolved S_X for every leg root of every
  runnable member (vehicle keyed, as the record's `s_x`: MGC carries GC's S_X).
- N-3 `edge_chain` adds `holm_descriptive_k9` {k 9, alpha_k, m, rows, note "descriptive only (R-E22-A10) ..."},
  `holm_tier_a(p, 9)` on the same p values; verdicts still use `holm` at the list's k_holm.
- N-4 the CLI prints the same "<cluster> confirmation: N members, R refused" line (and REFUSED lines, plus
  "NOT RUN member: reason" lines when a declaration was used) on the marker branch too; the line format is
  unchanged (tests/test_stage_e_runner_launch.py pins it).
- N-11 the STOPPED write is wrapped: an OSError there is printed to stderr and the ORIGINAL exception is
  re-raised (`raise exc`); the marker stays.
- N-12 a not-run record's single label must equal `trial.not_run_label` (the first of "untestable on owned data",
  "inconclusive by design" the trial carries), not just any of the trial's labels.

Tests added: runner v13 +14 (SF-1 3 parametrized; SF-2 1 pass + 8 parametrized refusals: parse, missing member,
wrong ordinal, extra member, undeclared run:false, declared but listed run, wrong start date, missing start date;
N-4 1; N-11 1); the R1 marker test now passes a full valid list; verdict +2 (N-3 with p = 0.008 rejecting at K 5
and not at K 9; N-12 with a trial carrying both labels).

Counts after the fixes (`nice -n 10 uv run python -m pytest -q -p no:cacheprovider`):
tests/test_stage_e_*.py 769 passed (753 + 16), 0 failed; the same 28 importing files 672 passed, 1 skipped,
2 failed, the same two as before (O-11: the real tree against the v12 manifest, and h6_rod's pinned v12 harness).
`ruff check` on the changed files: clean.
