# Stage E.14 Task 4: harness v10, worker notes (V10Coder-OpusXHigh)

Worktree `.claude/worktrees/agent-a94b80ceda0f5c25b`, branch `worktree-agent-a94b80ceda0f5c25b`, based on
main at 77be2a9. Brief: reports/stage_e14_briefs/brief_v10.md. No market data was read, no Databento
or network call was made, no key was read; ml_route_v2/, live/, ops/, rules/, strategy/members/,
.env, REGISTRATION.md and every frozen manifest JSON are untouched. The harness manifest was not
rebuilt.

## 1. Files

Changed (additive; every existing behaviour and every pre-2019-05 refusal unchanged):

| File | Change |
|---|---|
| data/config.py | New E.14 block after the step 2 active names: `STAGE_E14_SESSION_ID = "stage-E.14-2026-10-05"`, `E14_SESSION_CAP_USD = 0.00` (placeholder), `E14_REQUEST_CAP_USD = 3.00` (D13), `STAGE_E14_EXT2010_SESSION_ID = "stage-E.14-ext2010"`, `E14_EXT2010_SESSION_CAP_USD = 0.00`, `E14_BUY_ACCOUNT = ACCOUNT_2_ID`, `HIST_ROOT = data/processed_hist`. Each with its source. `ACCOUNT_2_CAP_USD` stays 249.67; `STEP2_*` still point at the E.12 block. |
| data/pull_step2.py | `--plan es2011\|ext2010` argument; with it `_hist_main` refuses every step 2 option (--status, --set, --roots, --ml-route, --cluster, the window options) and hands the same argv to `data.pull_hist.main`. Docstring paragraph and a `HIST_PLANS` tuple. Nothing else. |
| screening/harness_freeze.py | `DATA_SUBDIRS` + `data/processed_hist`; `ENTRY_MODULES` + the six new modules; `FROZEN_INPUTS` + the six `data/calendars/hist2010/<group>.json`; `TEST_PATTERNS` + `test_e14_*.py`, `_e14_*.py`. |
| .gitignore | `data/processed_hist/` |

Added:

| File | What |
|---|---|
| data/hist_calendar.py | `load_hist_group_calendar(group, *, base, expected_sha256=None) -> HistGroupCalendar` (a `GroupCalendar` subclass: Holiday entries, `HistLateOpen` late opens under the grains convention, SessionSpec rows, coverage 2010-06-01..2019-05-31, `assert_coverage`, `unsourced` with reasons, file sha256, computed counts). |
| data/pull_hist.py | Plans `es2011` (ES, 96 chunks 2011-05-01..2019-05-01) and `ext2010` (NG, NQ, ZN, 6E, GC, ZC; 2010-06-06..2010-07-01 then 106 months, 107 per root); `HistChunk` and `check_hist_chunk`; quote gate and per-plan buy gates; quote-only run and summary; buy run (checks, per-chunk flow, >3% stop, manifests in reports/hist/, free metadata); CLI (`python -m data.pull_hist`, or `python -m data.pull_step2 --plan`). |
| data/hist_store.py | The hist bar stores, `python -m data.hist_store --plan es2011\|ext2010 [--products ...] --harness-sha256 <sha>`; parquet `data/processed_hist/<plan>/<ROOT>/ohlcv-1m_<ROOT>_v_0_<first>_<last>_<plan>.parquet` (0444), summary `reports/hist/bars_<ROOT>_<plan>.json`. |
| data/hist_bars.py | `load_hist_leg(root, plan, *, expected_sha256, ...) -> LegFrame` (the step 2 loader's shape). |
| screening/stage_e14_c2.py | Test C2: `python -m screening.stage_e14_c2 --store-sha256 .. --gex .. --gex-sha256 .. --gex-lag 1\|2 --harness-sha256 .. --freeze-sha256 .. --out ..`, and `... count --gex .. --gex-sha256 .. --gex-lag ..` (`count_gex_negative`). |
| screening/trial_registry.py | Append-only registry; `python -m screening.trial_registry init\|status\|register ...`. |
| ledger/trial_registrations.jsonl | One baseline line, N = 471, citing reports/E.12_RETURN.md:561 ("New program N = 198 + 273 = 471"), written by `init` in this worktree at 2026-10-05 01:02 PDT. |
| tests/_e14_fixtures.py, tests/fixtures/e14_hist/{equity,energy}.json | Synthetic fixtures (calendar payloads clearly marked SYNTHETIC; DBN chunk, manifest, symbology and condition writers). |
| tests/test_e14_{hist_calendar,trial_registry,pull_hist,hist_store,c2,config_v10}.py | The v10 tests. |

## 2. Decisions (each one mine; the lead or Fable may overrule)

D-1 Layout. All hist logic lives in new modules; data/pull_step2.py (already 1,225 lines) only gains
the `--plan` hand-off, data/step2_store.py and data/build_bars.py are called, never edited, and
data/stage_e_bars.py is imported, not changed.

D-2 Session ids. Quotes of both plans ledger under `STAGE_E14_SESSION_ID` (brief). The ext2010 BUY
runs under its own `STAGE_E14_EXT2010_SESSION_ID`, so C2's ES spend never counts against C1's
session cap (a SpendGate session cap sums every line of its session id). The ES buy uses
`STAGE_E14_SESSION_ID` with `E14_SESSION_CAP_USD`.

D-3 Billed above quote. The step 2 path stops on ANY delivery above the quote. The hist path
implements the stage prompt's guardrail literally (`BILLED_OVER_QUOTE_STOP = 0.03`): billed =
quote x delivered / quoted billable bytes; above the quote by more than 3% the chunk is settled pro
rata, recorded in the manifest and the run stops before the next chunk; at most 3% above it is
settled pro rata, recorded (`billed_over_quote_ratio`, `billed_above_quote`) and the run continues
(the session cap, quote x 1.03, still bounds the total). A quote of 0 billable bytes with bytes
delivered counts as above 3%.

D-4 Extra buy checks, all before any vendor call: the gate's session id must be the plan's; what is
left of the session cap must fit the account's headroom; every raw target must be absent and
unsettled or present and settled; no other raw file of the root may overlap a chunk's range.

D-5 Free metadata. After the last chunk the buy run fetches, each file once (0444, never
overwritten): `symbology.resolve` of `<ROOT>.v.0` over [data_start, data_end) to
`VENDOR_ROOT/rolls/<ROOT>_v_0_<start>_<end>_symbology.json`, and
`metadata.get_dataset_condition(start_date=data_start, end_date=data_end)` to
`VENDOR_ROOT/condition/GLBX.MDP3_<start>_<end>.json` (es2011: 2011-05-01_2019-05-01; ext2010:
2010-06-06_2019-05-01; no collision with the step 2 files). A failed fetch stops with a named
error after the chunks; a rerun skips bought chunks and fetches. The store refuses if either file
is missing and never calls the vendor.

D-6 Quote-only. `--quotes-out` is required with `--plan` (E.2b's files refused); `--account`
defaults to acct-2; the summary reports only the quoting account's position (no dependency on
acct-1's external ledger), the total, total x 1.03, the headroom, `fits_headroom_with_3pct` and
`shortfall_usd_with_3pct`.

D-7 Hist calendar loader.
- Refused: unknown group; missing file; not JSON; wrong schema, group, products (each must map to
  the group in GROUP_OF_PRODUCT) or coverage; any entry or unsourced day outside the coverage;
  a weekend entry or weekend unsourced day; a repeated day; an unknown kind; an unknown status or
  time grade; a full closure with a halt/open time or a time grade other than n/a; an early halt
  or late open with time grade n/a or without its HH:MM; sessions that overlap, leave a gap, start
  after 2010-06-01 or end before 2019-05-31; segment offsets other than -1/0; bad year_coverage
  rows.
- UNSOURCED (each reason recorded): "listed" (the file's list), "entry_unverified" (status grade
  unverified, per the brief), plus two I added from calendar_rules.md's own definition:
  "session_unverified" (every weekday of a SessionSpec graded unverified) and "year_not_covered"
  (weekdays of a year whose year_coverage row is missing, unverified or has
  complete_exception_list false, unless the day has its own cme/secondary entry or no-entry
  finding). A time grade of "unverified" alone does NOT make a date unsourced (brief: status
  grade); such entries are counted (`time_unverified_entries`).
- Every late_open entry is a scheduled late open (grains convention: nothing trades before
  `open_ct` CT on the trade date itself), whatever its name.
- Source-id cross-references and the file's own "counts" are not enforced; the loader records
  its own counts (per year, by reason, share of trade dates).

D-8 Hist store. Right after decoding, rows booked outside the plan's trade dates and rows booked to
an unsourced date are dropped and counted (before any check reads a price); a row booked to no
trade date, or to a holdout-class date, raises. Bars inside a scheduled closure beyond the close
minute are kept and flagged automatically and counted (`closure_bars`); close-minute bars are
flagged `in_scheduled_closure` too (flag_frame's unchanged behaviour). Metadata records the plan,
the calendar file's sha256, the closure policy and the unsourced counts.
NOTE for the lead and Fable: bars on an UNSOURCED FULL-CLOSURE weekday (an unverified closure CME
in fact traded) book to the next trade date as closure bars (kept, flagged), not dropped. C2 treats
flagged bars as absent and excludes that next date (D-10 b); C1's later code must do likewise.

D-9 Loader. `load_hist_leg` refuses an unpinned or wrong sha256, a root outside the plan, rows
outside the plan's window or of a holdout class, rows on unsourced dates, mislabelled rows, and a
file whose metadata names another plan or another calendar sha256 than the one it loads.

D-10 C2 rule, as implemented (for the freeze and Fable to confirm):
- a. Every weekday 2011-05-03..2019-04-30 (2,086) is counted once, under its first failing
  condition in this order: unsourced, not_a_trade_date, early_halt, late_open, roll_blackout,
  no_prior_trade_date, prior_trade_date_unsourced, no_gex_row, missing_bar,
  bar_in_scheduled_closure. Missing bars are also counted by bar name.
- b. Added: "prior_trade_date_unsourced": d is excluded when its prior trade date, or any weekday
  between it and d, is unsourced (the prior trade date is then not established). Conservative,
  counted on its own.
- c. A bar flagged `in_scheduled_closure` counts as absent; a bar labelled with another trade date
  counts as missing.
- d. GEX_LAG 1 = the row of the latest CSV date strictly before d (the brief's wording), not "the
  row dated on the calendar's prior trade date": after an NYSE-only holiday on which CME traded
  (an early-halt day) lag 1 takes the last NYSE day's row. The output counts eligible dates whose
  lag-1 row date differs from the prior trade date (`gex_row_date_not_prior_trade_date`).
- e. c = 2.0379 and bar = 3.05685 are decimal literals (a module check ties them to 0.976 +
  0.5191 + 0.5428 and 1.5 x c; the float sum and product differ by one ulp). mean >= bar and
  p <= 0.025 are inclusive; n >= 30.
- f. sd = 0: t = +-inf (p 0 or 1); n < 2: t and p undefined, the test fails.
- g. Run once. Preconditions refuse with NOTHING written and no bar or GEX value read: the
  harness preflight, the marker or --out existing, GEX_LAG not 1 or 2, the freeze file's sha256,
  the registry (C2-T1 and C2-T2 together under that freeze sha256), the store and GEX CSV existing
  and hashing to their pinned values, and the equity calendar existing and loading (it is then
  re-read pinned to the sha256 taken here). The marker is then written before
  any bar or GEX value is read, and every later stop (a loader refusal, a malformed GEX row, any
  error) gives verdict STOPPED with the reason, written to --out. The brief lists "missing file"
  as a STOPPED case; I made existence and hash checks refusals instead, so a mistyped hash cannot
  consume the one evaluation. Lead to confirm.
- h. The output holds no price: verdict and reading, both tests' n, mean, sd, t, p, criteria,
  long/short split, eligibility counts, the rule constants, every input hash (store, calendar,
  GEX CSV, freeze, harness, registry entry, code files) and `trades_sha256` (date, side, g,
  GEX < 0) for the verifier.
- i. GEX CSV: the header must include date, price, dix, gex; only date and gex are parsed; rows
  are sorted by date; a repeated date, an unreadable date or a non-finite gex is refused.

D-11 Trial registry: one registration per test label; ids of the form `C2-T1`; registration runs
the harness preflight first, checks the freeze file's sha256, and writes entry ids `r001-C2`, ...;
the chain (n_before = previous n_after, n_after = n_before + ids) is checked on every read.

D-12 harness_freeze: the six calendar JSONs are FROZEN_INPUTS, so `harness_freeze build` refuses
while any is missing (they are under data/ and would be listed as harness_code anyway once present).
If C1 is dropped and its groups are never built, the lead removes those paths before the rebuild.

## 3. Tests

- New: test_e14_hist_calendar 23, test_e14_trial_registry 21, test_e14_pull_hist 40,
  test_e14_hist_store 19, test_e14_c2 49, test_e14_config_v10 6 = 158 passed.
- New plus the existing tests of every touched module (test_e2b_pull_step2, _e12,
  test_e2b_step2_store, _v9, test_harness_freeze, test_stage_e_config_v8, _keys, test_spend_gate,
  _accounts, test_cross_platform_static, test_stage_e_alignment, test_e2a_bars,
  test_e2a_calendar_equity), on the final code: 436 passed, 2 skipped, 1 failed (the expected
  manifest test below).
- Full suite, once (nice 10, `python -m pytest -q -p no:cacheprovider` with the main checkout's
  .venv python on the worktree code; the worktree has no synced .venv of its own): 6,613 passed,
  19 failed, 31 skipped, 3 xfailed in 12 min 32 s. It ran before the last three edits (the named
  metadata-fetch error, the raw-overlap check, the calendar pre-check in C2) and their three
  tests, which the rerun above covers.
- The 19 failures: 1 expected (below) and 18 environmental, none in a module v10 touches:
  - tests/test_compute_remote_e2e.py (9): the far side runs under `UV_PROJECT_ENVIRONMENT =
    <worktree>/.venv` (tests/_compute_fixtures.py:236), which is empty here, so `import pandas`
    fails;
  - tests/test_screening_runner.py (4), tests/test_k7_members_events.py (3),
    tests/test_holdout.py::TestRealStore (1), tests/test_d1f_holdout2.py::TestRealStores (1):
    they read git-ignored data the worktree does not have (data/processed MES parquet,
    data/vendor/databento/condition/GLBX.MDP3_2019-04-01_2025-04-01.json, data/sealed).
  The lead's full suite in the main checkout (after the merge and the manifest rebuild) is the
  real check.
- Expected failure until the lead rebuilds the manifest:
  tests/test_harness_freeze.py::test_the_real_tree_matches_the_committed_manifest_when_it_exists
  (six new modules unlisted, three listed files changed).

## 4. What the lead must do at merge

1. Copy the six calendar files to `data/calendars/hist2010/{equity,rates,fx,energy,metals,grains}.json`
   and load each once (`from data.hist_calendar import load_hist_group_calendar`); a refusal names
   the entry. Check `counts["unsourced_trade_dates"]` and the share against the 2% stop rules.
2. Quote fresh (no manifest needed; quote-only runs no preflight):
   `uv run python -m data.pull_step2 --quote-only --plan es2011 --quotes-out reports/stage_e14_quotes.json`
   and the same with `--plan ext2010` (C1's top-up figure).
3. Set `E14_SESSION_CAP_USD` = ES quote x 1.03 in whole cents, never above $18.07 (leave
   `E14_EXT2010_SESSION_CAP_USD` at 0.00 and `ACCOUNT_2_CAP_USD` at 249.67).
4. Rebuild the manifest (`uv run --no-sync python -m screening.harness_freeze build`) after steps 1
   and 3, show the diff against v9, and pass the new sha256 on every command.
5. Keep or re-init the registry baseline: the committed `ledger/trial_registrations.jsonl` has the
   baseline line timed 01:02 PDT from this worktree; to retime it, delete the file and run
   `python -m screening.trial_registry init` before any registration.
6. Then, per the stage order: freeze commit; `python -m screening.trial_registry register --test C2
   --ids C2-T1 C2-T2 --freeze reports/stage_e14_prereg_C2.md --freeze-sha256 <sha>
   --harness-sha256 <v10>`; `python -m data.pull_step2 --buy --plan es2011 --account acct-2
   --harness-sha256 <v10>`; `python -m data.hist_store --plan es2011 --harness-sha256 <v10>`;
   `python -m screening.stage_e14_c2 --store-sha256 <from reports/hist/bars_ES_es2011.json> --gex
   <csv> --gex-sha256 <sha> --gex-lag <frozen> --harness-sha256 <v10> --freeze-sha256 <sha> --out
   reports/stage_e14_c2_result.json`.
7. The GEX power count (calendar and GEX only): `python -m screening.stage_e14_c2 count --gex <csv>
   --gex-sha256 <sha> --gex-lag <n>` (also prints the window's unsourced weekday share).
