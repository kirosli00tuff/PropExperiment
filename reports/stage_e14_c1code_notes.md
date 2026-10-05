# Stage E.14 Tasks 4/5: test C1's code, worker notes (C1Coder-OpusXHigh)

Worktree `.claude/worktrees/agent-a87e3dc1a4f58c0e5`, branch `worktree-agent-a87e3dc1a4f58c0e5`, on main 77be2a9
plus the harness v10 merge (e577d55). Brief: reports/stage_e14_briefs/brief_c1code.md. No market data, no E.12
state (neither ~/.cache/propexp_e12_phase1 nor its copy was opened or listed), no Databento, network, .env or key.
q_m1 was NOT run on the real state (the lead runs it after the freeze). No existing file was edited:
ml_route_v2/constants.py is byte-identical (sha256 e107d7fe..., constants fingerprint 013fa5a4..., E.12's), and
reports/stage_e12_ml_v2_freeze.json still verifies on this tree (all 91 files).

## 1. Files (all new)

| File | Lines | What |
|---|---|---|
| c1_replication/__init__.py | 6 | package docstring |
| c1_replication/constants.py | 79 | every C1 parameter and pinned sha256 (section 3) |
| c1_replication/guards.py | 178 | state manifest check, v2 freeze check, ledger copy, no-fit guard |
| c1_replication/q_m1.py | ~390 | part 1: q reproduction, M1, C10 reference, model JSON |
| c1_replication/tables.py | ~300 | release calendar, NGS table (C13), full sessions, Rule H-1 rows |
| c1_replication/context.py | 225 | the table context (section 4) |
| c1_replication/exclusions.py | 121 | ruling C12 from the calendars |
| c1_replication/world.py | 149 | the replication world and E.12's panel call |
| c1_replication/evaluate.py | ~630 | part 2: the single run |
| c1_replication/README.md | | modules and the exact commands, in order |
| tests/_c1_state.py | 119 | synthetic E.12-like state built with the frozen code |
| tests/_c1_fixtures.py | ~240 | SYNTHETIC six-group calendars, release file, legs, M1 |
| tests/test_c1_{q_m1,context,tables,exclusions,world,evaluate,loader}.py | | 71 tests |

evaluate.py is above the 400-line guide; it holds one CLI's preconditions, run and outputs in the order the
docstring states, and splitting it would scatter that order.

## 2. CLIs (README has the full commands)

- `python -m c1_replication.q_m1 --state <copy> --state-manifest <json> [--state-manifest-sha256 <sha>] --out
  reports/stage_e14_c1_model.json --model-dir <dir outside the repo>`; exit 0 written, 3 "C1 STOP: q
  reproduction mismatch" (nothing written), 2 refused.
- `python -m c1_replication.evaluate --harness-sha256 --freeze --freeze-sha256 --model --model-sha256 --model-dir
  --store-hashes --calendar-hashes --out`; exit 2 refused before the marker, 0 PASS/FAIL, 1 STOPPED.
  Additions to the brief's CLI (decision D-3): `--model-sha256` (pins the model JSON) and `--calendar-hashes`
  (the six hist calendars, the release file and the energy full sessions by path and sha256, as the brief
  requires "passed by path and sha256 and checked"); `--state-manifest-sha256` is optional on q_m1.

## 3. Decisions (each mine; the lead or Fable may overrule before the freeze)

- D-1 Reproduction is E.12's own call path: gate0_stage.run_gate0 -> pipeline._gate0 -> gate0.gate0_b_trades
  (the build's admissible pairs, the build's calendar, state dir <state>/gate0), then gate0._b_test exactly as
  gate0_family_b applies it to the NG pairs. Before the call, every split file the run's blocks name must exist;
  during the call gate0.fit_model is replaced by a guard that stops (restored after). Registration goes to a
  temp copy of ledger/ml_v2_config_ledger.jsonl; the real file's sha256 AND the copy's must be unchanged (the copy
  changing would mean a test was not registered with its spec: a stop).
- D-2 Comparison against reports/stage_e12_gate0.json (pinned sha256 c0af61c2...): n_trades, n_dates and n_obs
  exactly; mean_gross_ticks and t_B ABSOLUTE |a - b| <= 1e-9 (inclusive). cost_ticks and p are compared and
  recorded, not gating (the prereg names trades, mean and t_B). Also gating: the build's constants and input
  fingerprints, the gate0B_meta fingerprint, the list sha256 and the covered signals and admissible pairs must equal
  what the report and list (pinned 53e7ef57...) record. q_m1 also checks the v2 freeze (pinned a647cd06...).
- D-3 CLI additions above. The state check is strict: every manifest file present with size and sha256, the 49
  required ones listed (45 npy, meta, 2 pickles, phase1_build.json), and NO other file in the state dir (a stray
  file in ~/.cache/propexp_e14_c1/e12_state_copy refuses q_m1; the real manifest lists 51 files, the 49 plus
  gate0_DONE.json and gate0_run.json). The state is verified again after the run.
- D-4 q_h = min |r_hat| of NG's Gate 0 trades (repr kept); recorded with the count of NG OOF rows with
  |r_hat| >= q_h (equal to the trades unless |r_hat| ties). M1: horizon_data(panel, h, admissible) and
  fit_model(ridge_spec(GATE0_RIDGE_LAMBDA), X, y), fitted twice (the two sha256s must agree, else stop); payloads
  `<model-dir>/c1_m1_<h>.ridge` (0444; an existing file must hold the same bytes); --model-dir must lie outside the
  repository; feature_cols sha256 = sha256 of json.dumps(list, separators=(",", ":")). The model JSON also records
  `feature_cols_follow_from_signals` (whether E.12's feature_cols equal panel.build_panel's rule on the covered
  signals; the evaluation's pre-marker C11 check needs it true; q_m1 prints a WARNING if not).
- D-5 C10 reference and check: per covered signal and per tested h, the count of NG ok_h rows with app_<signal> = 1
  (the panel frame carries app_ for every signal). The evaluation prints the same counts and stops when a signal
  with a non-zero reference count has 0.
- D-6 Ruling C7 (DEVIATION, lead to rule): a frame with NO row cannot run through the frozen code:
  ml_route_v2/signals/generic.py `_lead` computes `b.ts[jj]` with jj clipped to 0 and raises IndexError on an
  empty lead frame (tests/test_c1_world.py shows it). So CL and MBT each get ONE sentinel bar (price 1.0, trade
  date 2019-05-31 14:00 UTC, after the window): no lead bar is closed by any NG decision time, which is E.12's
  state for MBT before its listing (G17 "not applicable", value 0). C7's equality test passes: the whole panel
  frame with the sentinel CL equals the frame with synthetic CL bars on every session. No frozen file changed.
- D-7 Ruling C12, from the calendars alone (exclusions.py), checked BEFORE the marker (a C12 stop is a refusal:
  no bar is read, so the attempt is not used; any calendar fix is a new freeze anyway). Candidates: weekdays of
  the window that the energy calendar does not source as a closure. Excluded (reasons recorded): energy
  unsourced; NG's prior energy trade date or a weekday between unsourced (as C2's rule b); equity unsourced (Rule
  H-1's flatten rows come from it); rates, fx, metals, grains unsourced (a G17 leg's status unknown); a D8 release
  unsourced or graded neither official nor secondary. Stop iff share > 2%. The lead may narrow the groups before
  the freeze (exclusions.LEG_GROUPS). Excluded dates enter as NG's own excluded dates (the decision_rows exclude
  slot V2.2 uses), so they carry no decision row and no z-score history.
- D-8 Rule H-1 for 2010-2019 (tables.h1_rows) follows rules/sessions.py lines 20-40 literally: every equity
  full closure -> markets closed, early halt h -> close-by h - 30 min; every July 3 unsettled; late opens get no
  row; days before 2019-05-01 only. TOPSTEP_EARLY_CLOSE_LEAD gains 2010-2018 at 30 minutes (L-E5-2). Unlike the
  dict comment at rules/sessions.py:111, non-ordinary entries are NOT unsettled: the real equity draft names
  "Hurricane Sandy" and "National Day of Mourning (President G. H. W. Bush)" (also "Good Friday (jobs report)");
  they get H-1 rows (closed or close-by), which removes NG rows on those dates. Lead to confirm.
- D-9 Flagged bars (in_scheduled_closure, vendor_degraded_day) are kept, as E.12's compact_bars kept them
  (counted per root in the output). v10's note D-8 asks C1 to treat bars of an UNSOURCED full-closure weekday as
  absent: here the date after any unsourced energy weekday is excluded instead (D-7's prior rule), so such bars
  never reach an NG row's own date.
- D-10 The release-window rule is applied only as the frozen clock and targets apply it (D9.5a deferral, D8 event
  window); the targets' release_window flag is not a filter, as Gate 0 did not filter on it.
- D-11 NGS table: every NGS row must carry `"drop_actual_differs": true|false` (refused otherwise), so a renamed
  field cannot silently keep a drop row; true removes the row from the K4 table only (it stays in the D8
  calendar, as E.5's drops did). The D8 list = NGS, WPSR, FOMC rows by release name, every grade (as E.2b kept
  its unverified rows); the NG release calendar's coverage = the file's.
- D-12 Pass bar: mean >= 1.5 c, p <= 0.025, n >= 30, all inclusive; a NaN never passes; c = gate0._b_test's mean
  cost of the sides taken; a trade needs |r_hat| >= q AND sign(r_hat) != 0. Descriptive: C14 cost = commission +
  1.5 x (cost - commission) per trade (portfolio._trade_cost_ticks's rule, commission from vehicle_facts); C15
  share = trades / NG ok rows at h, long/short counts and mean g, trades per calendar year.
- D-13 Memory: legs are loaded, compacted and released one at a time (as phase1.world.load_root does).
- D-14 Pre-marker checks also: the NG day session of every hist energy SessionSpec equals D6's frozen (08:00,
  13:30 CT), and every NG candidate date's decision rows are exactly the frozen energy clock 08:30, 10:30, 13:00.

## 4. Every table the replication supplies to frozen code, and how (context.hist_tables)

Each is a module-attribute swap active only inside the context; every original object is put back on exit (also on
an exception); nesting is refused; every functools cache defined in the calendar-reading modules is cleared on
entry and exit. tests/test_c1_context.py proves the names are restored (identity), the files byte-identical,
the v2 freeze still verifying and the caches empty.

| Frozen name | Supplied | Read by |
|---|---|---|
| data.group_session.load_group_calendar, ml_route.inputs._group_calendar | the six pinned hist calendars (any other group raises) | the clock (day_times), sigma halts, in-session checks, G5, G16, training_calendar |
| rules.sessions._DEFAULT, _DEFAULT_LATE | the hist holidays and scheduled late opens per group | flatten (day_rule) |
| rules.sessions.TOPSTEP_HOLIDAYS | frozen rows + Rule H-1 rows (disjoint, checked) | flatten (day_rule) |
| rules.sessions.TOPSTEP_EARLY_CLOSE_LEAD | frozen + 2010-2018 at 30 min | flatten (day_rule) |
| strategy.members.k4.ngpre.make_ng | NgPre("NG", ngs=hist NGS less C13 drops) (NgPre binds the frozen NGS as a dataclass default, so the factory is the one name that can carry another table) | k4_ngpre_mto, k4_ngpre_msince |
| strategy.members.k4._calendar.ENERGY_FULL_SESSIONS; ovr.ENERGY_FULL_SESSIONS, _FULL_SESSIONS, _FULL_ORDINALS | the hist energy full sessions | k4_ovr_ret, k4_ovr_pct (reference dates) |
| (world field, not a patch) releases | NG's D8 ReleaseCalendar from the hist release file | g13-g15, targets (deferral, event-window cost) |
| (world fields) blackout, calendar, costs | v10 roll blackouts (+ C12 dates for NG), training_calendar on the hist energy calendar, frozen D8 | build_world_panel |

Not supplied (no NG row reads them; their vehicles have no rows, so their signals are n/a, as in E.12): K1-K3 and
K5-K9 member tables, K4's WPSR/API/NYSE tables (MCL members), the D6 session table and D8 costs (date-independent).
The synthetic NG-only panel build with E.12's 64 covered signals needs no root beyond NG, NQ, ZN, 6E, GC, ZC, CL
and MBT (checked, 2.2 s for 16 months of bars).

## 5. Tests (synthetic only)

75 passed (about 18 s): test_c1_q_m1 19, test_c1_context 7, test_c1_tables 16, test_c1_exclusions 5,
test_c1_world 4, test_c1_evaluate 23, test_c1_loader 1. They cover: reload without refit (a spy on the frozen
ridge fit counts only M1's 4 fits), on a fake-frame state and on a state built by the frozen synthetic pipeline
(synthetic_universe -> build_world_panel -> _filter -> gate0_b_trades, real signal columns), q = min |r_hat|, M1 determinism and equality with a direct frozen fit, the
mismatch stop and the 1e-9 boundary, manifest/split/ledger/out/model-dir refusals, the CLI exit codes; the
context; the tables; C12; C7; a planted edge PASS and noise FAIL end to end; the marker before any bar; every
pre-marker refusal reading no bar; C10 and C11 stops closing the attempt; C12-excluded dates without rows; the
pass-bar boundaries; the default loader against v10's real load_hist_leg on a fixture store.
Null check (scratch, 30 noise seeds): t mean -0.05 / -0.18, sd 1.01 / 0.99, verdict PASS 2 of 30 (the design's
false-pass rate is about 4.5%).
Regression, one process, the C1 tests first and then the frozen v2 (clock, signals, k9, gate0, phase1 gate0 and
world, targets, panel, e2e), K4 members (e4 a and b), sessions-holidays and v10 (hist calendar, hist store, C2)
tests: 787 passed in 2 min 10 s (nice 10), so the context leaks no state into the frozen tests. The full suite was
not run (the lead's run after the merge is the real check; v10's notes list its 18 environmental failures).

## 6. For the lead (not finished or outside this brief)

1. v10's loader REFUSES four real calendar drafts (equity, rates, energy, metals): their SessionSpec rows end on a
   Friday and restart on the Monday, and data/hist_calendar.py requires valid_to + 1 day == next valid_from. fx
   loads. With the weekend gaps closed in memory all five drafts parse, with 0 unsourced dates, and the real
   energy full-sessions list equals my recomputed rule (2,250 dates). Either the builders set valid_to to the
   Sunday or the loader accepts weekend gaps; if the energy file's bytes change, the full-sessions file's
   source_sha256 must be regenerated (tables.parse_full_sessions refuses a mismatch).
2. Follow-up (lead ruling, 02:4x PDT): a release row with null instant_utc and time_local is accepted ONLY when
   unsourced[] lists its id ({"id", "what", "reason"}); its date becomes an unsourced release date (C12 excludes
   the NG date) and no instant of it reaches the frozen code or the K4 NGS table. Any other null instant is
   refused, and an unsourced[] row naming no release row, or with neither a date nor an id, is refused. On the real
   reports/stage_e14_cal_releases.json (sha256 76d5125b..., as rewritten at 02:47 PDT): 1,012 rows (FOMC 72, NGS
   470, WPSR 470), 1,011 NG instants, NGS table 470 rows, 0 C13 drops, 1 untimed row listed (WPSR-2012-11-01),
   1 unsourced release date (2012-11-01), 4 cancellations. The grains calendar did not exist while I worked.
3. D-6 (C7 sentinel), D-7 (C12 groups), D-8 (H-1 on Sandy and the day of mourning) need the lead's ruling before
   the freeze.
