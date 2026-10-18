# Stage E.24 A2 recheck: the two SHOULD FIX items of loader_review.md (LoaderRecheck-FableXHigh)

Worker: LoaderRecheck-FableXHigh (worker-xhigh, fable). 2026-10-18 11:25-11:36 PDT. Brief: the "Common rules" and
"A2 LoaderReviewer-FableXHigh" sections of reports/stage_e24_briefs/brief_reviews.md, as a RECHECK of the Wave 2 fixes
only. Inputs: reports/stage_e24_briefs/loader/loader_review.md (APPROVE WITH FIXES, SHOULD FIX 2, NOTE 9),
loader_report.md section "Wave 2 fixes (LoaderFixer-OpusXHigh, 2026-10-18 11:17-11:25 PDT)", the code on disk at 11:25.
Independent: I wrote none of the code, tests or earlier reports. No repo file was edited; my scripts and logs are under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/c2dca792-060d-4694-91ef-4a6f3f808f1d/scratchpad/loader_recheck/.

## Verdict line

**APPROVE** — BLOCKING 0, SHOULD FIX 0, NOTE 3. Both SHOULD FIX items are fixed as the review asked, each with a test
that fails when the fix is undone; nothing pinned changed; the E.21/E.23/base_rules suites and the mdio tests pass; the
data replay did not need re-running (footer evidence below).

## 0. The code I checked is the code the fixer reported

sha256 at 11:27 equals the fixer's "after" column for all four changed files: mdio/bounded.py 45835bac…1323433,
mdio/trigger_books.py bd5303e0…a32da, tests/test_mdio_bounded.py a39bc4ae…6f8512, tests/test_mdio_book_files.py
2b90c805…602c8c. mdio/book_files.py (d93ecf2c…) and mdio/__init__.py (7b1bcb73…) have wave 1 mtimes (01:49, 01:51) and
were not touched in wave 2, as the report says. No other file has an mtime in the 11:17-11:25 window inside mdio/ or
tests/test_mdio_*.

## 1. SHOULD-FIX-1 (null trade_date label dropped silently) — fixed correctly, with tests

Review asked: refuse instead of dropping, same refusal class as the frozen path, a test with one null label.

What the fixer did (read in full, mdio/bounded.py):
- `_keep_mask` (:148-156): `fill_null(True)` at :156. A null label makes `less_equal` null; filled with True the row
  is kept. The rows then pass to the frozen booking check BEFORE the bound assertion (`HP.check_bookings` :226 or
  `data.stage_e_bars.check_bookings` :228, then `check_bound` :232). Both booking checks compare
  `frame["trade_date"].astype(str)` with the booked ISO date (base_rules/hist_plan.py:126-135,
  data/stage_e_bars.py:206-214), so a null label (a Categorical NaN after `to_pandas()`, in the frozen `_read` and in
  the bounded `_to_frame` alike) becomes "nan" and raises `TradeDateMismatch` (a StageEBarRefusal). `load_or_exclude`
  therefore excludes and counts "store refused" exactly as on the frozen path, with the same message (same first
  mismatch row, since both frames are sorted by ts_event and every null row is kept). The fixer's choice of reusing
  the frozen check rather than a new refusal in `_keep_mask` (the review's sketch) is the better one: one refusal
  class, one message, no divergence to maintain.
- `plan_row_groups` (:125-146) with `_may_hold_nulls` (:121-122): a row group whose statistics count a null, or carry
  no null count, is read and filtered instead of pruned. This is a real case the review's sketch missed: min/max
  statistics ignore nulls, so a null row inside a group whose labelled rows all fall after the bound would have been
  pruned unseen even with a refusal in `_keep_mask`. Correct and necessary.
- Module docstring item 3 (:13-21) states both.

Test: tests/test_mdio_bounded.py:333-361, `test_a_row_with_no_trade_date_label_is_refused_as_the_frozen_path_refuses_it`,
4 parametrized cases (ext2010 row 7 in a group decoded in full; ext2010 row 201 in a group whose labelled rows are all
after the bound; step 2 rows 5 and 31, before and after a bound inside the straddling group). Each case runs
`load_or_exclude` on the frozen context and on the bounded context and asserts identical counters and notes,
`{"store refused": 1}`, note starting "TradeDateMismatch: ". The fixture `_write(..., null_rows)` (:63-79) writes the
null into the text trade_date column with `row_group_size` 20, the same layout as the real stores (text labels,
propexperiment metadata), so the footer statistics the fix relies on are real parquet statistics, not mocks.

My mutants (in memory, scratchpad/loader_recheck/mutants.py; no repo file edited; each run its own process):
- M1 `_keep_mask` back to `fill_null(False)`: 4 failed, 19 passed; the 4 failures are the 4 null-label cases.
- M2 `_may_hold_nulls` always False: 1 failed, 22 passed; the failure is the ext2010 row 201 case (pruned group).
Both match the fixer's mutation table.

## 2. SHOULD-FIX-2 (read_root_books does not require a bounded context) — fixed correctly, with tests

What the fixer did: mdio/trigger_books.py:50 `check_bounded(ctx)` is the first statement of `read_root_books`
(import :21, docstring :8-9 and :45-49). No opt-out keyword: the bound is mandatory. `check_bounded`
(mdio/bounded.py:352-360) refuses a loader that is not a `BoundedLoader` and a loader whose bound is not `ctx.last`,
both with `BoundBreached` (RuntimeError, not a StageEBarRefusal, so never an exclusion). The call precedes
`load_or_exclude`, so no bar is loaded first. The mirror of trigger_hold.evaluate.read_root is otherwise unchanged;
`MIRRORED_SHA256` still pins the frozen file (bb3c59e3…, unchanged, git-clean) and its test passes.

Tests: tests/test_mdio_book_files.py:170-193 `test_read_root_books_refuses_a_context_that_is_not_bounded_before_any_load`:
unbounded loader -> BoundBreached "not bounded"; bound moved (ctx.last changed after binding) -> "not ctx.last"; a spy
on `load_bars` shows no load happened in either refusal; the bounded call loads once. The two existing read_root_books
tests (:142, :156) now bind `_BoundedWorld` (:125-137, a BoundedLoader subclass over the synthetic in-memory bars,
bound = ctx.last, asserting no bar after it) and still compare equal to the frozen `read_root` on the unbounded context,
so the equality test is still meaningful. The replay script already binds its context
(reports/stage_e24_briefs/loader/replay_e23.py:162 `bound_context`, :186 `read_root_books(ctx, ...)`), so it stays
compatible.

My mutants:
- M3 `check_bounded` a no-op in trigger_books: 1 failed, 22 passed (the new test). Matches the fixer's M3.
- M4 (my own, not in the fixer's table) `check_bounded` reduced to the isinstance check, bound not compared: 1 failed,
  22 passed; the "not ctx.last" sub-case catches it. So the bound comparison is tested, not only the type.

## 3. Nothing pinned changed

- `git status --short | grep -v '^??'` and `git diff HEAD --stat`: empty. No tracked file differs from HEAD
  (commit 0023572). The only wave 2 changes are the four untracked mdio/test files above.
- `sha256sum -c --quiet reports/stage_e22_f1_files.sha256`: rc 0 (30 files).
- pins.md inventory (reports/stage_e24_briefs/loader/pins.md): the 9 pinned existing files (base_rules/context.py,
  base_rules/store.py, multiday/book.py, run.py, evaluate.py, daily.py, trigger_hold/book.py, run.py, evaluate.py)
  recomputed and compared to the inventory's 16-char prefixes: 9 checked, 0 mismatches. No file was added under
  base_rules/, multiday/, trigger_hold/, tests/test_multiday_*, tests/test_trigger_hold_*, tests/test_base_rules_*
  (`git status --short` on those paths: empty).
- Freeze lines of reports/stage_e24_briefs/start_checks.txt re-run at 11:30-11:32 and equal to the 01:28 output:
  `python3 reports/stage_e2b_briefs/check_frozen.py` ALL_OK; harness v13 verify (fresh PYTHONPYCACHEPREFIX)
  "preflight OK: dd2bcc60…"; E.21 `multiday.freeze_manifest verify --sha256 0bb899e5…` "freeze verified: 18 inputs"
  rc 0; E.23 `trigger_hold.freeze_manifest verify --sha256 24dcf4dd…` "freeze verified: 20 inputs, 5 ids"; E.16
  guardrail `git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md` rc 0;
  E.16 freeze_manifest verify prints the same two "changed:" lines (screening/stage_e_verdict.py, data/stage_e_bars.py)
  as at 01:28 (by design since harness v13, memory note). REGISTRATION.md 0 bytes. `data.holdout status` all_ok true.
- Harness: mdio/ appears nowhere in reports/stage_e2b_harness_freeze.json (grep count 0) and is not under
  `screening.harness_freeze.HARNESS_DIRS` = ('rules', 'sim', 'screening', 'funnel', 'data', 'ml_route', 'compute',
  'strategy/stage_e'). No harness v14 is needed for the fixes (unchanged from the review's item 6).

## 4. Suites

`uv run pytest -q -p no:cacheprovider` at nice 10, logs in scratchpad/loader_recheck/:
- tests/test_mdio_bounded.py tests/test_mdio_book_files.py (11:28:34-11:28:36): `23 passed in 1.45s`, rc 0.
- tests/test_multiday_*.py tests/test_trigger_hold_*.py tests/test_base_rules_*.py (11:28:38-11:29:03):
  `231 passed in 24.95s`, rc 0. Those directories and tests are git-clean.
- `uv run ruff check mdio tests/test_mdio_bounded.py tests/test_mdio_book_files.py`: All checks passed.
I did not run tests/test_forward_*.py: not in my brief, another worker's scope, and being edited concurrently per the
fixer's report (its 5 failures were all in test_forward_f2_late_ca*.py, none mentioning mdio).

## 5. Data replay: not re-run, and shown not to be needed from the footers alone

The fixer's argument rests on the four ext2010 discovery stores having `null_count` 0 in every row group with the
null count actually present (`has_null_count`); if any group lacked a null count, `_may_hold_nulls` would mark it
read-and-straddling and the replay's rows_decoded/straddling would differ. I read the four footers (metadata only,
no row decoded, nice 10; scratchpad/loader_recheck/footers.py; pyarrow 25.0.1) and ran the FIXED `plan_row_groups`
at the replay's bound 2019-04-30:

| root | rows | groups (rows, has_min_max, has_null_count, null_count, _may_hold_nulls, max) | plan read | straddle |
|---|---|---|---|---|
| NQ | 2,910,457 | (1048576, T, T, 0, F, 2013-09-30), (1048576, T, T, 0, F, 2016-12-21), (813305, T, T, 0, F, 2019-04-30) | [0, 1, 2] | [] |
| ZN | 2,768,133 | (1048576, T, T, 0, F, 2013-10-24), (1048576, T, T, 0, F, 2017-03-13), (670981, T, T, 0, F, 2019-04-30) | [0, 1, 2] | [] |
| ZB | 2,528,907 | (1048576, T, T, 0, F, 2014-03-26), (1048576, T, T, 0, F, 2017-11-01), (431755, T, T, 0, F, 2019-04-30) | [0, 1, 2] | [] |
| ZF | 2,490,263 | (1048576, T, T, 0, F, 2014-05-16), (1048576, T, T, 0, F, 2018-01-09), (393111, T, T, 0, F, 2019-04-30) | [0, 1, 2] | [] |

Every group counts its nulls and has none, so fix 1(b) changes no decoded group and fix 1(a) changes no kept row on
these stores; fix 2 adds a check the replay's bounded context passes. The replay's discovery records, book files and
bars are therefore unchanged. replay_compare.json's pass_c_bars carries no per-load row-group fields, so this is a
comparison against the plan, not against recorded loads. Files opened: the four ext2010 parquet footers only, nothing
after 2019-04-30, no step 2, sealed, holdout or MES path, no marker written.

## Findings

### SHOULD FIX

None. Both of the review's SHOULD FIX items are closed.

### NOTE

**NOTE-R1. mdio/bounded.py:90 and :125-128 — "straddling" now also means "read because it may hold a null label".**
`plan_row_groups` appends a group with `_may_hold_nulls` to both `read` and `straddle`, so `EraLoad.straddling`
("read row groups whose statistics straddle the bound", :90) can list a group that does not straddle. Scenario: a
store with a null label in a group wholly after the bound; the EraLoad says straddling=(k,) and the store is then
refused. Reach: corrupt (refused) stores only; none of the pinned stores (table above). Fix: one line in the :90
comment and the :126-128 docstring ("or was read because it may hold unlabelled rows"), or a separate field.

**NOTE-R2. The reach of fix 1 stops at a store skipped by name (bounded.py:215; module docstring item 1).** A null
label inside a store whose NAME puts it after the bound (for example the step 2 store at bound = HIST_LAST) is never
seen, whereas the frozen `read_era` opens every store and refuses the product. This is inside the review's NOTE-6
(a skipped store's existence, hash and contents are unchecked by design) and the fixer's docstring is accurate ("every
decoded batch", "a store ... is never opened"). No action beyond NOTE-6's wiring rule (a future runner keeps
`base_rules.store.preflight`); listed so the lead reads "refuses as the frozen path refuses" as holding for every
opened store, not for a skipped one.

**NOTE-R3. mdio/bounded.py:352-360 — `check_bounded` is a type-and-bound check, not a proof that loads are bounded.**
Any `BoundedLoader` subclass passes it (the tests use exactly that, `_BoundedWorld`); the real guarantee is
`load_product_bounded`'s `check_bound` and the final `td` assertion, which only a loader built by `bound_context`
reaches. Scenario: a future runner subclasses BoundedLoader with its own `__call__`; `read_root_books` accepts it.
Fix: none in code (a subclass is the only way to test this path on synthetic bars); for the lead's stage-prompt
wiring rule (review SHOULD-FIX-2, last sentence), require `mdio.bounded.bound_context` as the construction, not merely
a BoundedLoader instance.

## Could not do or did not do

- Did not re-run the data replay (brief: only if the read path's numbers changed; section 5 shows they did not).
- Did not run tests/test_forward_*.py (another worker's scope, edited concurrently).
- Did not re-check the review's NOTE-4 to NOTE-11 beyond reading the fixer's reasons for leaving them; none is a
  correctness defect and the lead's decisions among them (NOTE-8 pin mdio/ in the next freeze, NOTE-10) are not mine.
- No commit, no edit to any file outside this report and my scratchpad.

Verdict: APPROVE (BLOCKING 0, SHOULD FIX 0, NOTE 3).
