# Stage D.1f adversarial review: holdout-2 leaks, Family H look-ahead, freeze coverage

Reviewer: AdvAuditor-FableMax (Fable 5.1, max), 2026-09-23. Independent of the Opus workers
that wrote the harness and of the Fable verifier (reports/stage_d1f_verification.md, whose
checks are not repeated here; this review builds on them). Nothing under the repo was edited
except this file. Scratch work is under the session scratchpad `review/` (three demonstration
scripts and one pytest log). Zero Databento calls. No H module was run on real bars (R-7):
every H run below is on the synthetic bars of tests/test_d1f_h_daily_bar.py.

Holdout invariant at the start and at the end of this task (`uv run python -m data.holdout
status`): holdout 1 `all_ok true, unlocks_logged 0, research_has_no_holdout_rows true`;
holdout 2 `state not_yet_sealed, chunks_sealed 0, unsealed_plaintext_present [],
unlocks_logged 0` (all_ok false by design before the purchase). REGISTRATION.md is 0 bytes.

Inputs read: the FROZEN list (sections 0, 1, 2.1 A3, 3, 5, 6), docs/NULL_CRITERIA.md 4, the
build STATE file and its rulings, the verification report; the code of data/holdout.py,
data/pull_mes.py, data/adapter.py, data/build_mes_bars.py, data/bars.py, data/research_bars.py,
data/validate.py, data/cme_calendar.py, data/session.py, data/spend_gate.py, data/config.py,
data/splits.py, screening/runner.py, funnel/null_generator.py, sim/engine.py,
strategy/interface.py, every strategy/research/_d1f_*.py, every file under
strategy/research/h_daily_bar/, the four D.1f test files named below, and the freeze dry run
(114 files; regenerated view of its sources and import closure).

## Counts and verdict in one line

0 BLOCKER, 6 SHOULD-FIX, 9 NOTE. Verdict: READY TO FREEZE once the six SHOULD-FIX items are
either applied (all are small, all touch only files that are frozen anyway, all can only be
applied BEFORE the freeze) or explicitly waived by the lead with the manual controls written
into the run prompt (section 5). No path was found by which holdout-2 bars can be read,
decoded beyond the one byte-count decode, summarised or left in plaintext past the seal; no
look-ahead or spec deviation was found in Family H that changes a P&L figure.

## 1. Findings

Severity: BLOCKER = must fix before the freeze; SHOULD-FIX = the harness fails closed or
misreports without it, the fix is small, and it cannot be applied after the freeze; NOTE =
for the lead's record or the run prompt, no code change required.

### F1. SHOULD-FIX. The preflight has no anchor for the manifest's content: an edit plus a re-run of the freeze script passes every check

Failure scenario. After the freeze commit, a harness file is edited (a "quick fix" during
the run session, or an accidental save), `uv run python -m strategy.research._d1f_freeze` is
run again (it is documented as "small and re-runnable", _d1f_freeze.py:1-3) and the new
manifest is committed. `_d1f_preflight.check_manifest` (113-131) compares each file with the
hash the manifest holds, `check_git_anchor` (138-150) asks only that the manifest file is
tracked and clean, and `check_section0` (171-194) verifies the two E-H modules against
`declared_amendments[...]["post_amendment_sha256"]` from the SAME manifest (185-189), which
`build_manifest` fills from the file's current hash (_d1f_freeze.py:162-166). Every check
passes; every output JSON carries the new manifest sha256; only a human comparing that value
with the one recorded at freeze time (STATE 7.1, the progress entry) can notice.

Evidence. Scratch `review/demo_refreeze.py` rebuilds the miniature repository of
tests/test_d1f_confirmation.py::fake_root, edits screening/runner.py and the E-H1 module,
regenerates the manifest exactly as `build_manifest` does, and calls `hash_checks`:

```
1. fresh fake repo:            problems = [] | manifest sha 382adb168179
2. after the edits, old manifest: problems = ['manifest file changed: screening/runner.py',
   'manifest file changed: strategy/research/e_calendar_event/h1_scheduled_macro_drift.py',
   'section 0 file changed: strategy/research/e_calendar_event/h1_scheduled_macro_drift.py']
3. after re-freeze + commit:   problems = [] | manifest sha f0a3c1afefa3 (was 382adb168179)
```

The list (1.5 step 1b) makes "the user's commit" the anchor, so this is a designed reliance
on a human comparison, not a violation of the frozen text; but the runner can carry that
comparison itself at no cost.

Minimal fix (pre-freeze, _d1f_confirmation.py and _d1f_preflight.py only): (a) `main` takes a
required `--manifest-sha256 <hex>` argument (the value the lead prints into the STATE file
and the progress entry, which the run prompt then quotes) and `run_step` refuses when
`pre.manifest_sha256` differs; (b) `_d1f_preflight.EH_AMENDED` becomes a mapping to the two
declared post-amendment hashes (f28529f0... and 7183d9bd..., STATE 7.1) and `check_manifest`
/ `check_section0` compare against those literals as well as the manifest. A sanctioned
re-freeze (a step-4b calendar correction) then means a new declared value in the prompt,
which is what the list intends.

### F2. SHOULD-FIX. Steps 2 to 4b (quote, pull, seal, build) run under code no one verifies against the manifest

Failure scenario. The freeze pins data/pull_mes.py, data/holdout.py, data/adapter.py and
data/build_mes_bars.py, but the puller and the builder never read the manifest:
`grep -n "_d1f_preflight\|hash_checks\|MANIFEST_PATH" data/pull_mes.py data/build_mes_bars.py
data/holdout.py` finds nothing. Only `strategy.research._d1f_confirmation` (steps 5 to 8)
runs `preflight()`. So a change to the sealing or building code after the freeze commit is
detected at step 5, after the money is spent, the 13 chunks are sealed and the parquet is
built under the changed code, and the list's rule then voids the whole run (1.5: "Any change
to a listed file after step 1b voids the run"). The realistic accident: the pull stops on a
crash, a fix is typed into data/pull_mes.py, the pull is resumed; nothing complains for the
rest of the purchase.

Evidence. data/pull_mes.py:300-325 (`main_d1f`) and data/build_mes_bars.py:575-581 (`cli`)
call no hash check; the only checks before a purchase are the spend gate and the sealing
refusals.

Minimal fix (pre-freeze): `main_d1f` and `cli(--confirmation)` call
`_d1f_preflight.hash_checks()` first (a lazy import inside the function, to avoid the
circular import through data.build_mes_bars) and refuse on any problem; `build_confirmation`
writes the manifest sha256 into the build summary and the parquet metadata, and
`_d1f_preflight.check_build` refuses if it differs from the runner's own
`pre.manifest_sha256`. That also gives the run-time inputs an anchor (F5).

### F3. SHOULD-FIX. `strategy/research/` has no `__init__.py`: a file that would run on every import and that the manifest cannot pin

Failure scenario. `strategy/research` is a namespace package (no `__init__.py`; `find`
confirms it is the only frozen package directory without one). If a later session adds one,
say to "make the package regular", its body executes before any `_d1f_*` or `h_daily_bar`
module and can rebind anything. `_d1f_freeze._with_packages` (78-84) records an
`__init__.py` only if it exists at freeze time, and `check_manifest` (113-131) verifies
listed files and new `_d1f_*.py` files only, so the added file is invisible to the freeze.

Evidence. Scratch `review/demo_namespace_init.py` (a throw-away package tree in a temp
directory, the real freeze builder's `import_closure` run over it):

```
closure without an __init__.py: ['pkg/research/mod.py']      run: VALUE = 1
closure after adding __init__.py: ['pkg/research/mod.py']    run: VALUE = 999
```

Minimal fix (pre-freeze): create an empty `strategy/research/__init__.py` now (it then enters
the manifest through `_with_packages`; behaviour is unchanged, every existing import still
resolves), and generalise the `_d1f_*.py` rule in `check_manifest` to refuse any `*.py`
under `strategy/`, `data/`, `screening/`, `sim/`, `funnel/` and `rules/` that the manifest
does not list. The same generalisation closes the sibling hole of a new top-level directory
shadowing a dependency on `sys.path[0]` (the repo root under `python -m`), which is
otherwise only a determined-adversary vector.

### F4. SHOULD-FIX. The git anchor covers the manifest file only; the 28 harness files it lists can stay uncommitted

Failure scenario. `check_git_anchor` runs `git ls-files --error-unmatch` and `git status
--porcelain` on reports/stage_d1f_harness_freeze.json alone (_d1f_preflight.py:141-149). A
freeze commit that adds only the manifest passes the preflight while the code it pins is
untracked or modified in the working tree; the commit then contains no copy of the frozen
harness, so "the commit is the anchor" (1.5 step 1b, NEW-4) holds for the hashes but not for
the sources, and a later `git diff` cannot show what changed.

Evidence. `git status --porcelain` on the 114 dry-run paths today: 12 modified and 16
untracked (the seven `_d1f_*.py`, the release table and the eight `h_daily_bar` files).

Minimal fix (pre-freeze, ~5 lines): `check_git_anchor` runs the same two git calls over
every path in `manifest["files"]` and refuses on any untracked or dirty path. The lead's
freeze commit must then include the harness, which is what NEW-4 intends.

### F5. SHOULD-FIX. The inputs created in the run session are not pinned across steps 5 to 8

Failure scenario. The confirmation parquet, the build summary, the rolls / condition /
symbology JSON files and docs/HOLDOUT2_MANIFEST.json cannot be in the freeze manifest (they
do not exist yet). Steps 5, 6, 7 and 8 are separate processes; `read_step` (146-152) checks
only that the previous step's JSON carries the same manifest sha256, and `_header` (161-166)
records the manifest, list and criteria hashes but not the parquet's. The parquet is written
read-only and the builder refuses to overwrite it, but "move it aside deliberately" is a
documented path (build_mes_bars.py:478), so a parquet rebuilt between step 5 and step 7 (for
example after a calendar correction that step 4b did not require) leaves no trace in the
outputs; `_confirmation_frame` (runner.py:164-177) even keys its cache on mtime and size, so a
new file is silently reloaded.

Minimal fix (pre-freeze): step 5 records the sha256 of the parquet, the build summary, the
three vendor JSON files and docs/HOLDOUT2_MANIFEST.json in its output; `_header` recomputes
them and every later step refuses on a difference (the same pattern as `manifest_sha256`).

### F6. SHOULD-FIX (low). Family H undercounts forced exits in two rare bar patterns

Spec (2.1 A3, H-3): "if no such bar exists, the engine's forced flatten applies and the day
is counted and logged as a forced exit". The runner reads the count from the instance
(`_screen_job`, _d1f_confirmation.py:196-212; `n_forced_exits` at 300-302) and the lead reads
it in the outputs. P&L is unaffected in every case: the engine books the forced close.

Gap A. The exit intent is emitted on the 14:58 bar and that bar is the session's last (a gap
from 14:59 to the halt). The engine cancels the unfilled strategy order at the session change
and closes at the 14:58 bar's close, reason `forced_flatten_session_end` (engine.py:466-491).
`_close_day` (_mechanics.py:285-287) marks a forced exit only when
`day.exit_decision_ns is None`, which it is not, so the day is missing from
`forced_exit_dates`.

Gap B. The window's last trade date never receives `_close_day` (no later bar arrives), so a
position still open at the end of data is closed by `finish()` with reason `end_of_data`
(engine.py:706-713) and never recorded.

Evidence. Scratch `review/demo_h_forced_exit.py` on the test file's synthetic sessions
(H1, the NR4 day of the existing known-answer case):

```
Gap A: engine fills [('09-12 10:01','buy',2,6001.5,'strategy'),
                     ('09-12 14:59','sell',2,6001.5,'forced_flatten_session_end')]
       forced_exit_dates: ()   day-4 record: exit_decision True forced_exit False
Gap B: engine fills [('09-12 10:01','buy',2,6001.5,'strategy'),
                     ('09-12 14:58','sell',2,6001.5,'end_of_data')]
       forced_exit_dates: ()   day-4 record: exit_decision False forced_exit False
Control (14:57 session followed by a later date, the existing test): forced_exit_dates
       (2025-09-12,), record forced_exit True
```

Minimal fix (pre-freeze, runner side, no change to h_daily_bar): in `_screen_job`, derive
the forced-exit dates from the ledger, `{fill trade date for f in
result.events(FillEvent) if f.reason != "strategy"}` (the runner already maps a fill to its
trade date in `_fill_trade_date`, runner.py:288-301), record both the instance's and the
ledger's sets, and refuse or flag when they differ. If the lead prefers the instance to be
right, `_close_day` should mark a forced exit whenever `day.last_position` is non-zero at
session end, and the runner should treat the in-progress last day the same way.

### N1. NOTE. The dataset-condition fetch covers holdout-2 dates, by design of the frozen list

`fetch_condition_d1f` queries 2019-04-01..2025-04-01 (build_mes_bars.py:244, 324-326), so the
frozen condition file, the build summary (`degraded_vendor_days`, 412) and the parquet
metadata (552) hold Databento's per-date condition for the 13 sealed months in plaintext.
This is metadata (date, condition, last-modified), not bars, and the frozen list itself
declares the holdout-2 date 2024-09-18 among the eight comparison dates (1.3), so the range
is what the list expects. No change; recorded so the D.2 declaration knows these dates are
already on disk.

### N2. NOTE. Row-count proxies for the sealed chunks exist in plaintext, and already did before D.1f

The committed ledger (ledger/databento_spend.jsonl) receives `billable_bytes` per quote and
"Delivered uncompressed record bytes N" per settle (adapter.py:134-143) for every chunk,
holdout-2 included; a resumed seal also writes the delivered byte count into the unlock log
(pull_mes.py:258-260, lead ruling 8a/D1). Bytes divided by the record size is a bar count
per month. The hashed reports/stage_d1e_quotes.json already lists the 13 holdout-2 quotes
with their billable bytes (e.g. 2024-04: 1,699,712), so nothing new becomes public; and L-1's
"no row counts" applies to the manifest, which holds none. No change.

### N3. NOTE. One REGISTRATION.md serves both holdouts

`_refuse_unless_ceremony` (holdout.py:289-315) reads the same REGISTRATION.md for either
holdout (HOLDOUT2_PATHS, 134-141), so a registration written for the holdout-1 read also
satisfies the holdout-2 ceremony, and the reverse. The list says "the same REGISTRATION.md
requirement" (1.2), so this is as declared; the D.2 declaration should make the registration
name both holdouts, or add "holdout 2" to the words the holdout-2 ceremony requires in the
file (a holdout.py change is harmless after the D.1f run, STATE 2.4).

### N4. NOTE. Two fail-closed residues the run prompt should name

(a) A holdout-2 chunk whose record-byte decode raises (a corrupt download) stays on disk in
plaintext at its target path: `fetch_range` has already linked and chmod-ed it
(adapter.py:122-129) before `delivered_record_bytes` runs; the resume path decodes it again
(pull_mes.py:255-261) and raises again; a re-buy is refused because the target exists. (b) A
crash mid-download leaves a truncated `.partial` until the next `fetch_range` unlinks it
(adapter.py:115). Both show in `python -m data.holdout status` as
`unsealed_plaintext_present`, and both need a by-hand step that the prompt should spell out
(inspect, then delete the file deliberately and re-run the pull; never seal a chunk whose
decode failed without a lead decision).

### N5. NOTE. Interpreter and library versions are pinned by file, not verified at run time

pyproject.toml and uv.lock are in the manifest; `requires-python = ">=3.12,<3.13"`; there is
no `.python-version`. Nothing in the preflight records `sys.version` or the imported
versions of numpy, pandas, pyarrow and databento, so an environment that drifted from the
lock (a run started from an activated venv instead of `uv run`, or a different 3.12 patch
release) leaves no trace in the outputs. Recommend `_header` records them (and, for
bit-reproducibility of the few BLAS-backed calls such as `np.cov` in the F5.3 threshold,
the run prompt sets `OPENBLAS_NUM_THREADS=1`).

### N6. NOTE. docs/HOLDOUT_MANIFEST.json is outside the manifest

It anchors the research parquet's sha256 (holdout.py:402-403, checked by the preflight's
holdout-1 `all_ok`), and that parquet feeds V_ref (step 5) and the continuity check (step 6).
The file is committed and immutable by design; adding it to `SINGLE_FILES` costs one line and
makes the chain explicit.

### N7. NOTE. data/config.py freezes the external spend-ledger path the pull needs

`EXTERNAL_LEDGER_PATHS` (config.py:26-28) points at a file the STATE (0.4) says is absent on
this machine; `SpendGate.external_spent_usd` fails closed (spend_gate.py:186-195), so the
purchase would be refused. Because data/config.py is in the manifest, repointing it after the
freeze is a re-freeze. It must be resolved before the freeze commit, as the STATE already
says; the freeze script must then be re-run.

### N8. NOTE. Family H audit records mark an entry the engine refused

`_enter` (_mechanics.py:341-347) sets `entry_side` before the engine's acceptance, so on a
roll-blackout day the record shows `entry_side="buy"` and `skip_reason=None` while the ledger
shows the refusal (the existing test `test_one_entry_per_trade_date[True]` pins this). The
trade counts and P&L come from the engine, so nothing in a verdict is affected; the
`DayRecord` is audit-only. No change needed; the reader of `day_records` should know.

### N9. NOTE. The calendar carve-out is sound because two other checks back it

Section 0's data/cme_calendar.py line is checked on the 2025-2026 entry block only
(_d1f_preflight.py:153-168, lead ruling 6.5). Everything else in the file (constants, the
`Holiday` shape, `CALENDAR_COVERAGE`, the 2019-2024 entries) is pinned by the manifest's
whole-file hash, and the step-6 continuity check reproduces the D.1d accounting to the cent
on the train union, which exercises the 2025-2026 behaviour end to end. Nothing to change.

## 2. Area 1, holdout-2: what was checked and found sound

- Chunk set and order: `d1f_chunks` must equal the 58 confirmation plus 13 holdout-2 chunks
  oldest first (pull_mes.py:187-193); `pull_d1f` seals inside the iteration that bought the
  chunk, before the next `fetch_range` (265-270); out-of-order buys are refused before the
  quote (215-221, 266).
- The one decode: `delivered_record_bytes` (adapter.py:147-151) is an in-memory
  `to_ndarray` byte sum, called once per chunk in `fetch_range` (129) and, on resume, once in
  `pull_d1f` (257). No other code path opens a holdout-2 chunk: `build_confirmation` reads
  exactly `confirmation_raw_paths` (build_mes_bars.py:285-287, 475-476), refuses any holdout-2
  file name and any path outside the 58 (290-303), and re-checks `source_file` after loading
  (390-393); the A.1 builder refuses sealed inputs (117-131); `data.holdout main seal` refuses
  once a manifest exists (433-434).
- Sealing: proof in memory, write `xb` + fsync, proof from disk, manifest record, SEALED
  entry, log pin, then unlink of the raw file and its `.partial`, then an existence check
  that raises (holdout.py:638-693). Manifest content per chunk: paths, bytes, two sha256s
  (667-669). A crash after the record is finished on resume only under the same proof
  (696-720, lead ruling D2).
- Re-buy refusals on three layers: `pull_d1f` skips anything either manifest lists or that is
  on disk (247-263); `fetch_range` refuses through `is_sealed_raw` with both manifests
  (adapter.py:70-83, holdout.py:276-286) and through `request_touches_sealed_window`, which
  after sealing blocks ANY schema overlapping a sealed holdout-2 chunk (holdout.py:197-211),
  so a later D.1g book request cannot reach 2024-03..2025-03.
- Symbology and rolls: `resolve_d1f_rolls` and `fetch_raw_symbols_d1f` query
  2019-04-01..2024-03-01 only and refuse a boundary outside it (pull_mes.py:279-297,
  build_mes_bars.py:329-334); nothing about the March 2024 splice or later is fetched.
- Boundaries: the Feb 2024 chunk's last hour (trade date 2024-03-01) is dropped by trade date
  before flags are attached (build_mes_bars.py:347-356, 512-514); the April 2024 session's
  first two hours are inside the sealed March chunk. `confirmation_drops` logs the dropped
  bar counts per date only.
- Loaders and windows: `load_confirmation_bars` pushes down 2019-05-01..2024-02-29 and
  re-checks every row (research_bars.py:183-195, 134-147); `ConfirmationWindow` refuses at
  construction and again in `_screen_confirmation` (runner.py:160-161, 419); a
  `ScreeningWindow` holding confirmation dates is refused by the train-union check (438-441);
  the null generator accepts all-research or all-confirmation frames, never mixed (null_generator.py:92-110);
  `_confirmation_frame` has its own cache (164-177).
- Ceremony: the holdout-2 stage pattern requires "holdout 2" and fullmatches L-3 (holdout.py:98,
  294-296); unlock headings carry "UNLOCK holdout 2" and are counted per holdout (240-249,
  364-365); newline and `#` are refused in stage and reason (297-299); the log's sealed prefix
  is pinned at every seal and re-checked before a re-pin (380-390, 626-628);
  `unlock_holdout` refuses holdout-2 paths (324-326).
- Runner preconditions: steps 5 to 8 refuse unless holdout 1 is `all_ok` with 0 unlocks and
  holdout 2 is `sealed`, `all_ok`, 0 unlocks (_d1f_preflight.py:227-241), so the list cannot
  run while a chunk is unsealed.
- Figures: no output pools mined and confirmation data; V_ref against V_M is the declared
  start rule; the N = 186 accounting uses the 101-member variance (lead ruling b).
- Vendor client: the verifier's audit of databento 0.82.0 (no cache, no temp file, one
  write to `path`) stands; TestVendorAudit pins the version.

## 3. Area 2, Family H: what was checked and found sound

Every bullet of 2.1 A3 was read against strategy/research/h_daily_bar/_mechanics.py and the
six modules, with the engine's ordering (sim/engine.py:685-704: session roll, fills at the
open, MLL, forced flatten, then the strategy) and the interface's timing contract.

- Daily bar: O from the 08:30 bar, H/L over CT [08:30, 15:00), C from the 14:59 bar; complete
  only with both bars, no halt flag and one instrument over its RTH bars (_mechanics.py:193-201,
  293-309). It is finalised when the first bar of a later trade date arrives (275-291), so
  day d's own bar can never be in day d's history; the last `lookback` complete bars are kept
  (290).
- Conditioning: evaluated once, on day d's 08:30 bar, from `_history` only (311-320); the
  instrument guard compares the last `guarded_bars` complete bars with that bar's instrument
  (318-320): 1 for H1, H2, H4, H5, H6 and 2 for H3, exactly the exemptions of NEW-9. Warm-up
  returns None until the lookback is full (120-139, each module's `condition`).
- Clock windows are read on CT date d only (256-258); ETH bars of the previous evening return
  `()`. The OR takes bars with CT time in [08:30, 09:00) inside RTH (306-309) and needs the
  08:30 bar plus 25 bars (325-327); triggers read the completed bar's close, strictly, in
  [09:00, 14:30) (323-339); H6 enters on the 08:30 bar (264-269); one entry per date (262-263);
  fills are the engine's next-open fills (521-533).
- Exit on the first bar with CT time >= 14:58 and before the no-new-positions time (349-360);
  early-halt days trade nothing (313, 328, 343); no stop, no target.
- Percentile: `np.percentile(baseline, q, method="linear")` over the 60 complete ranges
  before d-1 with q literals 33.33 and 66.67 (129-139; h4:31, h5:32); inequalities strict for
  H1 to H3 and the triggers, non-strict for H4, H5 and H6's cuts; CLV in ticks, zero range
  refused (h6:29-43). For a CLV that is exactly a cut (32/40, 8/40) the float division is
  correctly rounded and equals the literal, which the existing test pins.
- Factories take no arguments; `_lookback` is keyword-only, private, defaulted to 61 and
  unused by the factories (h4/h5:47-56); the runner builds one fresh instance per screen and
  keeps it for `forced_exit_dates` (_d1f_confirmation.py:196-212).
- State across dates: `_history`, `_records`, `_day` only; nothing from a later date reaches an
  earlier one; `trade date went backwards` raises (279-281).
- Hindsight: the modules import no loader and name no hindsight field; the engine blanks
  `vendor_degraded_day` before the strategy sees the bar (engine.py:652-655).
- Look-ahead mutants: the verifier's eight mutants and the added N1 test cover the
  off-by-one (day d as "d-1"), the OR end, the trigger on high/low, the non-strict trigger,
  the exit time, the lenient completeness rule, the dropped guard and the re-entry after a
  refusal. I found no further mutant class that the pair of tests would miss.

The one bookkeeping deviation found is F6. The N4 note of the verification (synthetic bars
dated inside the mined range) stands as recorded there.

## 4. Area 3, freeze coverage: what was checked and found sound

- The dry run lists 114 files: everything under screening/, sim/, funnel/, rules/; data/*.py;
  strategy/interface.py; the eight h_daily_bar files; the seven `_d1f_*.py`; the release
  table; every section-0 file (48 entries, parsed to 48); the declaration hashes, the
  criteria and the list; pyproject.toml and uv.lock; the two facts files the runner reads for
  Tier B's signs; and the 86-file repo-internal import closure of the runner, which reaches
  every trial module, `_lead_accounting`, `_d1b/_d1d_accounting`, `_d1e_event_series`, the
  F and G hashed modules and resample.py, data.holdout and data.pull_mes.
- Every file the runner reads at run time that exists at freeze time is in the manifest:
  sim/slippage_calibration.json (sim/costs.py:28), reports/power_gate.json
  (funnel/power_gate.py:56, 244), reports/stage_d1d_accounting.json,
  reports/stage_d1_accounting.json and reports/stage_d1b_accounting.json (the accounting
  modules), reports/stage_d1e_members_events.json and the two facts files
  (_d1e_event_series.py:87-89), data/cme_calendar.py (HOLIDAYS for the roll blackout,
  engine.py:143-161). `funnel/power_gate.py:177` reads reports/funnel_null_baseline.json only
  in its `main()`, which the runner never calls.
- Dynamic imports: an AST scan of every `.py` in the manifest finds no `importlib`,
  `__import__`, `exec(` or `eval(`; the lazy `from data.holdout import ...` imports are ordinary
  `ImportFrom` nodes and are in the closure. The release table and the calendar sources are
  literals in their modules, not JSON read at import.
- Environment: the only `os.environ` read in the closure is the Databento key
  (config.py:67), which cannot affect a result. Randomness is seeded everywhere it is used
  (drift.py:105, 254; _d1f_decisions.py:85, 163; the funnel's own seeds are not on the
  runner's path). Set iteration is sorted where it reaches an output (`plain`,
  `resolve_statistic_dates`, `holm`/`benjamini_hochberg` with a key tie-break); the pool map
  preserves job order.
- The E-H amendment is exactly the declared diff (a defaulted `release_table` field and the
  lookup through `self.release_table`), the combined table shares no key with the old one,
  and the continuity step runs both factories on the train union.
- The preflight refuses on: a missing, untracked or dirty manifest; any listed file missing
  or changed; a `_d1f_*.py` not listed; a section-0 hash mismatch (with the two carve-outs);
  a list or criteria hash differing from the declaration file, or a criteria file that does
  not embed the list's hash; a build summary missing or flagged, a failed step 4b, a missing
  degraded-date comparison, or parquet metadata that disagrees with the summary; unclean
  holdouts. `write_once` and `_refuse_if_decided` stop any step from running twice or after
  step 8.

## 5. Verdict and conditions

READY TO FREEZE, on these conditions:

1. F1, F2 and F3 applied before the freeze commit (together well under 100 lines, in
   _d1f_confirmation.py, _d1f_preflight.py, data/pull_mes.py, data/build_mes_bars.py, plus one
   empty `strategy/research/__init__.py`), the affected tests updated, the full suite green,
   the freeze script re-run and its sha256 printed into the STATE file. If the lead waives any
   of them, the run prompt must carry the manual control instead: the expected manifest
   sha256 to compare against the runner's printed value; "no edit to any manifest file
   between the freeze commit and step 8, whatever happens during the pull"; and a
   `check_manifest` result recorded before the first quote.
2. F4, F5 and F6 at the lead's discretion, but decided now: none can be applied after the
   freeze. For F6, if not fixed, the lead should read `n_forced_exits` as a lower bound and
   the ledger as the truth.
3. N7 resolved (the external ledger path) before the freeze script's final run, and N4's
   manual steps and N5's environment lines written into the run prompt.
4. The freeze commit contains the harness sources, not only the manifest (F4's intent, even
   if the code check is waived).

No finding rests on a number; nothing here enters a verdict.

## 6. Test runs and boundaries

- `uv run pytest tests/test_d1f_h_daily_bar.py tests/test_d1f_confirmation.py
  tests/test_d1f_holdout2.py tests/test_d1f_confirmation_window.py -q` on this working tree:
  248 passed in 52.7 s (scratch log `review/pytest_d1f.log`).
- Scratch scripts, all under the session scratchpad `review/`: `demo_refreeze.py` (F1),
  `demo_namespace_init.py` (F3), `demo_h_forced_exit.py` (F6). None touches the repo; the H
  demonstration uses only the synthetic-bar helpers of the test file.
- Not verifiable here: the live vendor round trip; the 2019-2024 calendar against real bars
  (step 4b in the run session); the runner's wall time on ~1,150 window dates; and that `uv
  run` syncs the environment to uv.lock on the run machine (N5).
