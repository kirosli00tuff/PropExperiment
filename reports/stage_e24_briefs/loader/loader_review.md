# Stage E.24 A2: review of the multi-day loader fix (mdio/) — LoaderReviewer-FableXHigh

Reviewer: LoaderReviewer-FableXHigh (worker-xhigh, fable), independent of the coder. Times PDT from `date`
and file mtimes, 2026-10-18. Review ran 06:16 to about 06:35. Nothing under review was modified; nothing was
committed. Scope: reports/stage_e24_briefs/brief_reviews.md section A2 against
reports/stage_e24_briefs/loader/loader_report.md, pins.md and replay_compare.json.

Files reviewed (sha256 prefixes, equal to the coder's report table): mdio/__init__.py 7b1bcb73,
mdio/bounded.py 1b5f8401, mdio/book_files.py d93ecf2c, mdio/trigger_books.py 083c9c9c,
tests/test_mdio_bounded.py 07741689, tests/test_mdio_book_files.py 2cae68e4,
reports/stage_e24_briefs/loader/replay_e23.py b639a68c, pin_inventory.py 72037e3b. 1,014 lines in all.

## Verdict line

**APPROVE WITH FIXES** — BLOCKING 0, SHOULD FIX 2, NOTE 9.

## Check results (brief items 1 to 7)

### (1) No pinned file changed — holds

- `git diff HEAD --stat`: empty (no tracked file modified). The seven pinned files re-hashed match pins.md:
  base_rules/context.py e7b9e8ee, base_rules/store.py 7ce90cda, multiday/book.py 7566d6b4, multiday/run.py
  2b6e31c5, trigger_hold/book.py 298c8619, trigger_hold/run.py 0cda36dc, trigger_hold/evaluate.py bb3c59e3
  (the latter also equals `MIRRORED_SHA256` in mdio/trigger_books.py:35).
- E.16 guardrail `git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md`:
  rc 0. `git diff --quiet HEAD -- ml_route_v2 rules sim screening data/holdout.py live ops`: rc 0.
- E22-F1 list `sha256sum -c --quiet reports/stage_e22_f1_files.sha256`: rc 0 (list sha bb3bf3b3 unchanged).
- Every freeze line of reports/stage_e24_briefs/start_checks.txt (lines 1288-1377) re-run, same text as at
  start: check_frozen.py ALL_OK (E.1 32/32, E.2a 4/4); harness v13 `preflight OK: dd2bcc60...` with mdio/
  present (fresh PYTHONPYCACHEPREFIX); K1-K8 cluster freezes OK (11/44/30/12/11/27/6/4 members); v2 freeze OK
  91 files; E.16 freeze prints the same two pre-existing `changed:` lines (screening/stage_e_verdict.py,
  data/stage_e_bars.py); E.18 the same pre-existing `pin mismatch: reports/stage_e2b_harness_freeze.json`;
  E.20 H6 the same `bad ['data/stage_e_bars.py']`; E.20 search the same REFUSED on the harness json; E.21
  `freeze verified: 18 inputs`; E.23 `freeze verified: 20 inputs, 5 ids`; pinned documents
  reports/stage_e14_prereg_C1.md afc5c10f, stage_e22_confirmation_list.md 6f2fbf38, stage_e22_prereg_F1.md
  04ef33a6, stage_e23_freeze.json 24dcf4dd, stage_e23_prereg.md db34eac9 all tracked and clean.
- REGISTRATION.md 0 bytes. `data.holdout status`: unlocks_logged 0, all_ok true (top, holdout_2, MCL, MGC,
  MHG, NG).
- pins.md is accurate: base_rules/*, multiday/*, trigger_hold/* and their test globs are pinned (E.16
  guardrail, E.16/E.21/E.23 freezes whose `verify` also refuses new files in those directories); mdio/ and
  tests/test_mdio_*.py are covered by no freeze, guardrail, HARNESS_DIRS entry or members_dir. The choice of a
  new package follows brief step 2 ("else ... a new module"). Part A was correctly not stopped.

### (2) The bound is enforced before rows reach memory where the format allows, and asserted — holds, with one disclosed limit

Read against the frozen base_rules.store (`_checked_input`, `_read`, `read_era`, `load_product`, printed with
inspect) and base_rules.context.store_loader:

- Store skip by name (mdio/bounded.py:105-111, 198-204): `refuse_path` runs first (sealed, research, MES,
  foreign layouts refused even when skipped), then for ext2010 `HP.check_name` (first, last from the name),
  for step 2 the constants STEP2_FIRST..WINDOW_LAST. A store whose first date is after the bound is never
  opened. Verified on the replay by strace: only the four ext2010 parquet files were opened (13 opens each);
  no processed_step2, sealed, holdout, embargo, research or MES path appears.
- Row-group pruning (bounded.py:118-136): a group whose trade_date min is after the bound is never decoded;
  a group without min/max statistics is read and filtered. The real ext2010 stores (footers only read by me,
  no rows): 3 row groups each of 1,048,576 / 1,048,576 / remainder rows, BYTE_ARRAY String trade_date with
  exact min/max and null_count 0 in every group (NQ 2010-06-07..2013-09-30, ..2016-12-21, ..2019-04-30; ZN,
  ZF, ZB likewise ending 2019-04-30). So pruning works on the real stores; the spy test
  (tests/test_mdio_bounded.py:209) shows only groups [0, 1, 2] decoded with 10-date groups and refuses any
  whole-file read.
- Batch filter (bounded.py:139-144, 160-166): every decoded batch (<= 65,536 rows) is filtered in Arrow
  before `_to_frame`, the single pandas conversion point (spied in test line 226). Inside a straddling row
  group this is post-decode truncation, which the coder states plainly (module docstring item 3, report
  section 2 item 3 and section 5). Parquet allows no less without page-index pruning, which pyarrow does not
  expose; disclosed, see NOTE-4.
- Assertion (bounded.py:179-189, 220, 255-256): `check_bound` refuses any kept label or booked day after the
  bound, and `load_product_bounded` re-checks the assembled `td`. `BoundBreached(RuntimeError)` is not a
  StageEBarRefusal, so `load_or_exclude` (base_rules.common, printed) does not turn it into an exclusion
  (test line 240). Mutation checks in the coder's report (no pruning, no skip, no filter) each fail tests.
- Equivalence with the frozen path: `_assemble` (bounded.py:260-295) is the body of the frozen `load_product`
  statement for statement; `read_era_bounded` runs the same `_checked_input`, the same booking check per era,
  the same WINDOW_LAST refusal, `splices_and_blackout`, rolls, `_td` and record. Filtering before a stable
  sort by ts_event gives the same order as filtering after it, and the duplicate check is kept. The frozen
  reader equality test (line 135) and pass C on the real data (no field differing for 4 roots) confirm it.

### (3) Per-unit and per-fill files match E.21's format and content — container and fills yes; holdings rows differ by book type (NOTE-7)

- Container: E.21's reports/stage_e21_runs/per_root/NQ.json has keys schema, root, vehicle, tick_value_cents,
  per_contract_daily_dollars, holdings, fills, counters. mdio's record (book_files.py:43-60) has the same
  keys plus layout, units, book_counters; `schema` is "mdio_per_root/1" and `layout` is E.21's
  "stage_e21_per_root/1"; holdings/fills are keyed by trigger-hold id instead of T1/T2/T3. The test at
  tests/test_mdio_book_files.py:56 checks the shared keys field by field against the frozen
  `multiday.evaluate._root_rows`.
- Fills rows: the key set in the replay's files equals the real E.21 files' key set exactly (date, kind,
  trade, held_after, side, price_ticks, ts, cost_per_contract_cents, cost, event, uncalibrated, locked,
  flat_bar, guard).
- Holdings rows: shared core date, kind, target, excluded, vehicle, mark_price_ticks, price_ticks, sigma, V;
  E.21-only month, e, lookbacks, signal, S_M, S_u, weight (E.21's rebalance-order diagnostics);
  trigger-hold-only net, active_units, divisor (the unit book's). Both come from the frozen
  multiday/book.py:361 (`**o.info`, the order's own info); mdio passes the rows through unchanged.
- Units rows (new): d_e, d_x, u, trigger_id, root, d0, h, ISO dates. Write-once by O_EXCL
  (book_files.py:71), tested.
- Content on the replay: units per trigger-hold equal the recorded `units` (NQ h5 1729, NQ h20 1713, ZN 137,
  ZF 131, ZB 136); fills 429/289/184/160/180; holdings 403/227/154/142/152; last fill, last holding and last
  per-contract date all <= 2019-04-30 (NQ 2019-04-30; ZN, ZF, ZB fills 2019-04-05). My four files are
  byte-identical to the coder's (same sha256 per root), so the writer is deterministic.

### (4) Independent replay equals E.23's recorded discovery numbers — holds

Run by me in my own scratch dir
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/c2dca792-060d-4694-91ef-4a6f3f808f1d/scratchpad/loader_review/
(run/, replay.log, strace_open.txt, compare_independent.py), test mode, `nice -n 10`, 9,880 MB available
before launch, under `strace -f --seccomp-bpf -e trace=open,openat,openat2`, 06:21:26-06:24:09, rc 0:

```
2026-10-18T06:21:26-07:00 freeze verified; roots ['NQ', 'ZN', 'ZF', 'ZB']; bound 2019-04-30
2026-10-18T06:22:24-07:00 pass A: 39624 values, 0 mismatches
2026-10-18T06:23:08-07:00 pass B: 39583 values, 0 mismatches
2026-10-18T06:24:09-07:00 pass C: {'NQ': {'fields_differing': [], 'rows': 2910457, 'max_trade_date': '2019-04-30'}, 'ZN': {... 2768133 ...}, 'ZF': {... 2490263 ...}, 'ZB': {... 2528907 ...}}
2026-10-18T06:24:09-07:00 replay OK: 79207 values, 0 mismatches, max loaded 2019-04-30
```

- My own leaf walker (compare_independent.py, stdlib only, floats bit for bit, not the coder's Compare
  class): discovery_replay.json vs reports/stage_e23_runs/discovery/discovery_result.json: **39,624 leaves,
  0 mismatches**; keys on one side only are run metadata only (discovery_result_sha256, finished_local,
  freeze_sha256, manifest_sha256, registration, registry, schema, started_local, status, test_ids);
  n_trials 538, k 5; units, screen, dsr_descriptive and pbo_descriptive blocks equal. My
  discovery_replay.json sha256 55ae3667... equals the coder's.
- My replay_compare.json equals the coder's in every compared field (bound, roots, n_trials_used,
  header_checks, values_compared_total 79,207, mismatches_total 0, max_loaded_trade_date_overall
  2019-04-30, nothing_after_bound_loaded true, watched_unchanged true, pass_c_bars, per-store table).
- Max loaded trade date per store: NQ/ZN/ZF/ZB ext2010 2019-04-30 (rows kept = rows decoded = 2,910,457 /
  2,768,133 / 2,490,263 / 2,528,907; row groups [0, 1, 2] of 3); the four step 2 stores skipped in all
  three loads, 0 rows, never opened (strace).
- Data limits: nothing after 2019-04-30 loaded; no file dated 2024-03-01 or later; W_cf bars never read. The
  only W_cf-named files opened are reports/stage_e23_events/*__cf.json, trigger-event lists hashed by
  E.23's own `trigger_hold.freeze_manifest.verify` (frozen inputs), not bars (NOTE-9).
- No write: strace shows no write-mode open outside the scratch dir, /dev, /proc, uv's cache, .venv and
  bytecode caches; none under reports/ or ledger/. Watched files unchanged after my run:
  discovery_result.json c3f71384, RUN_ONCE_discovery 7ff27c3e, RUN_ONCE_confirmation 5c7c57e3,
  ledger/trial_registrations.jsonl 25c04088 (the start_checks value); `git status` of those paths empty.

### (5) E.21, E.23 and base_rules suites pass unchanged — holds

`nice -n 10 uv run pytest -q -p no:cacheprovider tests/test_multiday_*.py tests/test_trigger_hold_*.py
tests/test_base_rules_*.py`: **231 passed in 37.11s**, rc 0 (06:26:19-06:26:57); 21 files, all git-clean.
New tests: `tests/test_mdio_bounded.py tests/test_mdio_book_files.py`: 17 passed in 4.32s; `ruff check`
clean.

### (6) Harness v14 — not needed for any invariant

`screening.harness_freeze.HARNESS_DIRS` = rules, sim, screening, funnel, data, ml_route, compute,
strategy/stage_e; the v13 manifest lists 1,065 files, none under mdio/ or tests/test_mdio_*; harness verify
prints `preflight OK` with mdio/ present. No touched file is in the manifest or under a harness directory.
Whether mdio/ should be pinned at all is the lead's call (NOTE-8).

### (7) Will future multi-day stages use the bounded path, and what is not covered

- How a later stage reaches it: a new, unfrozen runner does what trigger_hold/run.py:154-157 does
  (`context_from_freeze`, `ctx.starts = e21_starts(...)`, `ctx.last = <window last>`), then
  `ctx, loader = mdio.bounded.bound_context(ctx, manifest)` and `mdio.bounded.check_bounded(ctx)` before
  its first load. The frozen `trigger_hold.evaluate.discovery` then works unchanged on that ctx (pass A), or
  the runner calls `mdio.trigger_books.read_root_books` per root and `mdio.book_files.write_per_root`
  (pass B). The frozen runners multiday/run.py and trigger_hold/run.py stay unbounded if rerun; by the pins
  nothing in them can change.
- Not covered: enforcement (the bound is opt-in; nothing refuses an unbounded ctx unless the runner calls
  `check_bounded`, SHOULD-FIX-2); the hash and existence of a skipped store (NOTE-6); page-level pruning
  inside a straddling row group (NOTE-4); a step 2 store that is loaded and truncated (a bound inside
  2019-05-06..2024-02-29) has no test (NOTE-3); E.21-style `multiday.evaluate` books keep their own
  `_root_rows` writer (no units file); the confirmation phase on real data (by design, W_cf is never read
  here); a runner that calls both `discovery` and `read_root_books` loads every store twice (NOTE-10).

## Findings

### SHOULD FIX

**SHOULD-FIX-1. mdio/bounded.py:144 — a null trade_date label is dropped silently where the frozen path
refuses the store.** `_keep_mask` ends with `keep.fill_null(False)`, so a row whose trade_date is null is
filtered out before the booking check. Scenario: a store with one null-labelled row. Frozen `read_era`:
`_read` keeps the row, `check_bookings` compares `labels` with the booked days and raises
`TradeDateMismatch` (a StageEBarRefusal), `load_or_exclude` excludes the product and counts "store
refused". Bounded path: the row vanishes, the product loads with one bar fewer, no refusal, no counter, and
`check_bound` cannot see it. Reach: none on the pinned stores (null_count 0 in every row group of the four
ext2010 footers; files sha256-pinned), so this is a divergence in a failure mode only. Fix: refuse instead
of dropping, e.g. in `_keep_mask` (or `read_bounded`) `if col.null_count: raise StoreRefused(f"{where}:
{col.null_count} rows with no trade_date label")`, and a test with one null label asserting the same
refusal class as the frozen path.

**SHOULD-FIX-2. mdio/trigger_books.py:40-47 — the only new entry point does not require a bounded context.**
`read_root_books` calls `load_or_exclude(ctx, ...)` on whatever `ctx.load_bars` is. Scenario: a future
runner builds its context with `context_from_freeze` and forgets `bound_context`; the step 2 store is
decoded in full (W_cf bars in memory), the discovery records are unchanged (the replay shows equality), and
the per-root files are written with no error or log line, so the look-ahead exposure V41 set out to close
is silently back. Results are not corrupted, hence not BLOCKING. Fix: `check_bounded(ctx)` at the top of
`read_root_books` (a keyword `require_bounded: bool = True` lets the synthetic tests at
tests/test_mdio_book_files.py:123,137 opt out explicitly, or they bind a BoundedLoader), and the lead's
stage prompt for any future multi-day read requiring `check_bounded` in the runner's preconditions and
listing mdio/*.py and tests/test_mdio_*.py in that stage's freeze. The lead may prefer the wiring rule alone
and treat this as a NOTE.

### NOTE

**NOTE-3. tests/test_mdio_bounded.py — no test loads and truncates the step 2 store.** The mid-era bound test
(line 167) uses a hist-era bound, so the step 2 store is skipped; the equality test (line 124) loads it
whole. A bound inside the step 2 range exercises the same `read_bounded` with
`data.stage_e_bars.check_bookings`, which (read by me) refuses forbidden dates and label/booking mismatches
and has no completeness check, so the result would be correct; one more case in the mid-era test with
`bound = sd[k]` would show it.

**NOTE-4. Straddling row group: decoded then truncated (disclosed).** bounded.py:160-166. Real row groups
hold about 1M rows (3-4 years), so a future bound inside a store decodes, in 65,536-row batches, up to one
group of later rows and keeps none. pyarrow exposes no page-index pruning, so this is the floor; the coder
says so plainly in the module docstring, report section 2 item 3 and section 5.

**NOTE-5. Pruning trusts footer statistics (disclosed).** A group pruned on wrong statistics would lose
rows before the bound silently; only in a corrupt file, and the files are sha256-pinned. The real footers
carry exact min/max (`has_min_max` true, no truncation of 10-character ISO dates).

**NOTE-6. A skipped store's existence and sha256 are not checked by the bounded load.** bounded.py:203
returns before `_checked_input`. The frozen runners run `base_rules.store.preflight` (hash, no rows) on every
store before the marker, and the replay driver skips preflight deliberately (it would hash the step 2
stores). A future runner must keep preflight, or a missing or wrong step 2 store is noticed only when a
bound crosses 2019-05-06.

**NOTE-7. Per-root files: E.21's container, not E.21's schema string; holdings rows differ by book type.**
See check (3). A consumer keyed on "stage_e21_per_root/1" or on T1/T2/T3 must be adapted; `layout` names
E.21's schema. The holdings key difference comes from the frozen book's per-order info
(multiday/book.py:361), not from mdio.

**NOTE-8. mdio/ is pinned by nothing.** Not a harness directory, not in any freeze. For the next multi-day
read, that stage's freeze should list mdio/*.py and tests/test_mdio_*.py (the E.21/E.23 freezes glob only
their own directories). Lead's decision.

**NOTE-9. The replay opens reports/stage_e23_events/*__cf.json.** These are W_cf trigger-event lists hashed
by E.23's frozen `freeze_manifest.verify` as frozen inputs; no W_cf bar store was opened (strace). Mentioned
so the lead does not read the strace grep as a boundary breach.

**NOTE-10. Double loading.** The replay loads each store three times (pass A, B, C). A future runner that
calls both the frozen `discovery` and `read_root_books` loads twice; the two give identical records by
construction (pass B, 39,583 values). Either build the discovery dict from `read_root_books`' records or
accept the cost.

**NOTE-11. `name_range` runs `HP.check_name` twice for ext2010** (once inside `refuse_path`, bounded.py:108-110).
Harmless.

## Could not do or did not do

- The step 2 truncation case (NOTE-3) was not exercised on real data (it would read W_cf bars, forbidden).
- I did not re-run the coder's mutation checks; the three claimed test failures per mutant are plausible from
  the tests read, but unverified by me.
- Verdicts and whether SHOULD-FIX-2 becomes a wiring rule rather than code are the lead's.

Verdict: APPROVE WITH FIXES (BLOCKING 0, SHOULD FIX 2, NOTE 9).
