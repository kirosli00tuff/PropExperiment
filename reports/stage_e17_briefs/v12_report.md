# Harness v12 code diff: report (V12Coder-OpusXHigh, Stage E.17)

Worker: worker-xhigh, model opus. Brief: reports/stage_e17_briefs/brief_v12.md. Worked 22:51-23:15 PDT
2026-10-09 (times from `date`) in the isolated worktree `.claude/worktrees/agent-a463ba71418f7066b`.
No commit, no vendor call, no key or .env read, no write to ledger/, no read of data/processed*,
data/vendor or data/sealed, harness manifest not rebuilt.

Base: the worktree was created at 8e5707c, not the v11+C1 commit. I fast-forwarded the worktree's own
branch to 558a7ce ("E.17 C1 evaluated", a descendant of 8e5707c; `git merge --ff-only`, no commit
created). The diff is against 558a7ce.

## Output

- Diff: reports/stage_e17_briefs/v12.diff, 438,661 bytes, sha256
  `5f68cc84a9ea0e7453c3f68d0ee756c08716c04bb7db08b1b38b07125088b4de`, 9 file sections (`git diff
  --binary 558a7ce` with the four new files marked intent-to-add, then un-marked).
- Apply check: `git apply -R --check` on the worktree passes, and `patch -p1` of the diff onto
  558a7ce copies of the five tracked files reproduces all nine files byte for byte (livestock.json
  included, so its sha256 holds after apply).

## Files changed

| File | Change |
|---|---|
| data/pull_hist.py | plan "ext2010h", per-root chunk lists, its session, `--roots` (A4) |
| data/hist_calendar.py | HIST_GROUPS gains "livestock"; docstring and comment |
| data/hist_store.py | `--plan` accepts ext2010h; docstring |
| data/config.py | `STAGE_E17_EXT2010H_SESSION_ID`, `E17_EXT2010H_SESSION_CAP_USD = 0.00` |
| data/calendars/hist2010/livestock.json | new: byte copy of reports/stage_e16_calendars/hist2010_livestock.json |
| tests/test_e14_hist_calendar.py | one pinned assertion changed (below) |
| tests/test_e17_v12_pull_hist.py | new, 69 tests |
| tests/test_e17_v12_hist_calendar.py | new, 5 tests |
| tests/test_e17_v12_hist_store.py | new, 27 tests |

Tracked-file diff: 5 files, 200 insertions, 20 deletions. Nothing under screening/, rules/, sim/,
base_rules/, c1_replication/, ml_route_v2/, strategy/, and data/pull_step2.py was touched.

## Choices and their reasons

1. **Per-root chunks (HistPlan).** A new last field `root_chunks: tuple[(root, chunks), ...] = ()`
   and a method `chunks_of(root)`. When the field is empty (es2011, ext2010), `chunks_of` returns
   `chunks`, so both v10 plans keep the same chunks, keys, messages and CLI. For ext2010h, `chunks`
   holds the union, which is the 106 months 2010-07..2019-04, so the existing `chunk_range`, log
   line and "no chunk past 2019-05-01" test still read correctly. I used tuples, not a dict, so
   HistPlan stays hashable and frozen.
2. **The plan.** `EXT2010H_START_MONTHS` hard-codes the 21 (root, U2 start month) pairs in the windows
   file's `purchase_21_roots` order. Chunks are `monthly_chunks(start, 2019-05-01)`. Trade dates are
   2010-07-01..2019-04-30 and the data window is [2010-07-01, 2019-05-01). The label is E16, with
   ids E16-H1..E16-H5. A separate module-level check enforces 21 roots, 1,993 chunks, 18 x 106 plus
   TN 40, RTY 23 and HE 22, contiguous lists, each ending at 2019-05-01. The v10 check block is
   byte-identical and still runs over the v10 plans only, because ext2010h joins `PLANS` and
   `HIST_PLAN_NAMES` after it (rebinding, no mutation). The tests cross-check each root's
   start_month, count and first/last chunk against reports/stage_e16_windows.json.
3. **check_hist_chunk.** Membership is now tested against `plan.chunks_of(root)`. For per-root plans
   the message names the root ("is not one of plan ext2010h's 40 TN chunks 2016-01-01..2019-05-01");
   the v10 message is unchanged. `chunks_of` raises the same "is not a root of plan" error for a
   non-root, so `plan_chunks` never silently skips a root.
4. **Quote session.** I added `quote_session_id(plan)` and `plan_quote_gate(plan, account,
   **overrides)` instead of changing `quote_gate`'s signature, so `quote_gate` and the test
   factories of the v10 plans (`lambda account: ...`) stay as they are. `main` gained one keyword,
   `plan_quote_gate_factory` (default `plan_quote_gate`). The v10 plans still call
   `quote_gate_factory(account=...)` exactly as in v10. ext2010h calls the new factory, and the gate
   is refused (RC_REFUSED) unless its session is `stage-E.17-ext2010h`. The buy's `buy_policy` gives
   ext2010h `(STAGE_E17_EXT2010H_SESSION_ID, E17_EXT2010H_SESSION_CAP_USD, E14_REQUEST_CAP_USD)`.
   The request cap is D13's $3.00, the same constant es2011 and ext2010 use; the brief names no
   other.
5. **`--roots` (A4).** `nargs="+"`, `metavar="ROOT"`. `select_roots` runs right after `get_plan`,
   before any gate, preflight, key or client. It refuses the option for es2011 and ext2010 ("is for
   plan ext2010h only"), and for ext2010h it refuses an empty list, repeated roots and non-plan
   roots (HistPlanError, RC_REFUSED). A bare `--roots` with no value is refused by argparse
   (SystemExit 2 == RC_REFUSED), also before any call. Chunks follow the order the roots are given
   (`plan_chunks`' existing semantics), so the lead can list the A3 priority order. The free
   metadata fetch covers only the bought roots, because `run_hist_buy` passes the roots of its
   items. The quote summary's "roots" records the selection; for v10 plans it is unchanged.
   Everything else in the buy is the existing logic.
6. **Livestock calendar.** `cp` byte copy; `cmp` identical; sha256
   `802a4dd98a71776af58748c43c2a70772a966a2e37dd08e32fef1ebfe023ba5d`, equal to the E.16 freeze's
   record for reports/stage_e16_calendars/hist2010_livestock.json. The loader parses it unchanged:
   no stop condition was hit.
7. **Store builder.** No logic change was needed. `expected_names`, `refuse_inputs`,
   `hist_parquet_path` and the manifest reader already go through `plan_chunks` and `get_plan`, so
   each root's inputs are its own list. Only the CLI `--plan` choices and the docstring changed.
   **The partial first trade date is accepted:** a 6A or LE bar at 2010-06-30 19:00 CT (00:00 UTC
   07-01, the first minute of the bought July chunk) books to 2010-07-01 and is kept. Nothing before
   2010-07-01 is read, there was no refusal, and so no stop.
8. **Config.** The new block sits after `HIST_ROOT` and before `DATABENTO_KEY_ENV_BY_ACCOUNT`,
   commented in the file's style. `ACCOUNT_2_CAP_USD` and every other value are unchanged.
9. **Not done, per the brief:** `quotes_from_ledger`'s fallback is unchanged.

## Existing assertions changed

- tests/test_e14_hist_calendar.py:164: `load_hist_group_calendar("livestock", base=FIXTURE_DIR)`
  expecting "unknown hist calendar group" now uses `"crypto"`. Reason: v12 makes livestock a hist
  group (hand-off step 8), so the old call now fails with "does not exist". "crypto" keeps the
  test's intent: a group of data.calendars that has no hist calendar.

No other existing assertion changed.

## Tests run (nice 10, `-p no:cacheprovider`)

- New files plus the four E.14 files: **191 passed** (26 s): test_e17_v12_pull_hist 69,
  test_e17_v12_hist_calendar 5, test_e17_v12_hist_store 27, test_e14_* (4 files) 90.
- Every test file that imports data.pull_hist, data.hist_store, data.hist_calendar or data.config
  (48 files, the 3 new ones included; list from grep, indented imports included): **1514 passed,
  11 skipped, 2 failed** (4 min 31 s, 23:07-23:12 PDT). Neither failure comes from the diff's logic:
  - tests/test_harness_freeze.py::test_the_real_tree_matches_the_committed_manifest_when_it_exists:
    the committed v11 manifest differs on data/config.py, data/pull_hist.py and the other v12
    files. Expected; the lead rebuilds the manifest.
  - tests/test_d1f_holdout2.py::TestRealStores::test_real_holdout2_is_not_yet_sealed_or_verifies:
    the worktree has the committed holdout-2 seal manifest but not the git-ignored data/sealed
    stores (they exist only in the main repo), so `verify_seal` reports not all_ok. No changed
    file is used by data.holdout's seal check.
- Ruff on every touched file: no new findings. data/config.py has 5 E501 findings, and the same 5
  exist at 558a7ce.

## E.16 freeze verify (end of work)

```
$ uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
E.16 freeze OK: 97 files; manifest sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
$ git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md   -> unchanged
```

## For the lead (not decided here)

1. **Placeholder pins.** `E17_EXT2010H_SESSION_CAP_USD = 0.00` is pinned by one assertion,
   tests/test_e17_v12_pull_hist.py `test_the_v12_config_block_holds_the_placeholder_cap`. The test
   `test_the_ext2010h_buy_refuses_at_the_configured_placeholder_cap` skips once the cap is nonzero.
   The zero-cap refusal is tested with an explicit 0.00 gate, so it does not depend on config.
   `ACCOUNT_2_CAP_USD` (291.08) is pinned at tests/test_e14_config_v10.py:31-32 and
   tests/test_stage_e_config_v8.py:65.
2. **Harness manifest coverage.** data/calendars/hist2010/livestock.json is hashed by the manifest
   (data/ is a HARNESS_DIR). tests/test_e17_v12_*.py are not: screening/harness_freeze.py
   TEST_PATTERNS lists `test_e14_*.py` but no `test_e17_*.py`. Adding the pattern is a screening/
   edit, outside this brief.
3. **The CLI path.** data.pull_step2's `--plan` choices stay ("es2011", "ext2010"), and that file is
   outside the diff. Hand-off step 9's quote and step 11's buy of ext2010h therefore run as `uv run
   python -m data.pull_hist ...`; `python -m data.pull_step2 --plan ext2010h` is refused by
   argparse.
4. **`--roots` is optional.** A `--buy --plan ext2010h` without it covers all 21 roots, bounded only
   by the session cap. A4's restriction holds only if the buy command passes `--roots` with the A3
   selection.
5. **Vendor behaviour not testable here.** The buy's free `symbology.resolve` for TN, RTY and HE spans
   the plan's data window [2010-07-01, 2019-05-01), years before their listing. The fakes cannot
   show what the vendor returns for that range. The store test does show that the builder accepts
   symbology starting at the listing (TN, d0 2016-01-10). If the real call errors, the buy raises
   its named "free metadata fetch failed" HistPlanError after the chunks are bought, and a rerun
   skips the bought chunks.
6. **Cosmetic labels.** ext2010h ledger notes still read "Stage E.14 hist purchase (ext2010h, test
   E16)" (HIST_NOTE), and the store metadata's "stage"/"source" strings still say "E.14 ...
   harness v10". This is the same per-root logic, and the real harness sha256 is recorded beside
   them. Left unchanged to keep the diff to the list.
7. **Shared session.** Quote and buy share `stage-E.17-ext2010h`, as the brief requires, so the
   buy's own per-chunk quote lines land in the same session as step 9's quote lines. Step 9's
   guard (only the run's own new lines) is unaffected.

Nothing in the brief was left unfinished.
