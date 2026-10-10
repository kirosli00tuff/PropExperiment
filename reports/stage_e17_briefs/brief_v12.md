# Brief: V12Coder-OpusXHigh (worker-xhigh, model opus) - harness v12, plan "ext2010h"

Stage E.17, written by the lead. Spawned only after C1's single evaluation completed (user ruling U1). You work in an
isolated git worktree of /home/kiros-li/Documents/GitHub/PropExperiment; do not commit. Do not spawn workers.

## One objective

Write harness v12's code diff exactly as reports/stage_e16_handoff.md step 8 lists it, plus the `--roots` buy option of
E.17 amendment A4, with tests on synthetic data only. The lead sets the caps, rebuilds the harness manifest, has Fable
review, runs the full suite and commits.

## Read first (by section, never whole large files)

1. reports/stage_e16_handoff.md section 1 step 8 (the binding diff list) and step 9.
2. docs/prompts/STAGE_E.17.md amendment A4 (lines 72-76).
3. base_rules/hist_plan.py (the consumer interface v12 must satisfy: `default_resolver` calls
   `data.pull_hist.get_plan("ext2010h")` and reads `.name`, `.first_trade_date`, `.last_trade_date`; `check_name` needs
   the file `<base>/ext2010h/<ROOT>/ohlcv-1m_<ROOT>_v_0_<first>_2019-04-30_ext2010h.parquet` with
   2010-06-06 <= first <= the root's window start; `check_plan` needs the parquet metadata `plan` = "ext2010h" and a
   `trade_date_range` inside [first, last]) and base_rules/constants.py lines 36-55 (WINDOW_START, HIST_PLAN_OF).
4. reports/stage_e16_windows.json: `products.<ROOT>.start_month` and `chunks_2010_to_2019_04` for the 21 roots of
   `purchase_21_roots.roots` (1,993 chunks: 18 roots start 2010-07 with 106 chunks each, TN 2016-01 40, RTY 2017-06 23,
   HE 2017-07 22).
5. data/pull_hist.py (plans, check_hist_chunk, plan_chunks, gates, buy_policy, require_buy_ready, the CLI),
   data/hist_store.py (plan-driven store builder), data/hist_calendar.py (HIST_GROUPS, the loader),
   data/config.py lines 160-200 (the E.14 block), and the v10 tests tests/test_e14_*.py for the fixture style.
6. reports/stage_e16_calendars/hist2010_livestock.json (its sha256 is in reports/stage_e16_freeze.json) and
   base_rules/calendars.py (how base_rules parses it today).

## The diff (nothing else)

1. data/pull_hist.py
   - A new plan named exactly "ext2010h": test label "E16", test ids ("E16-H1", "E16-H2", "E16-H3", "E16-H4",
     "E16-H5"), the 21 roots in the windows file's order, and PER-ROOT chunk lists: for each root, the monthly chunks
     of `<ROOT>.v.0` from its U2 start month through 2019-04 (end exclusive 2019-05-01), exactly as the windows file
     lists them (1,993 chunks in total). Store trade dates: last 2019-04-30; first 2010-07-01 (the first trade date on
     or after DEFAULT_START, which satisfies check_name for every root, including TN, RTY and HE whose windows start
     later); data window [2010-07-01, 2019-05-01) UTC. Extend HistPlan backward-compatibly (for example an optional
     per-root chunk mapping); "es2011" and "ext2010" must behave byte-for-byte as in v10 (same chunks, keys,
     module-level check, CLI behaviour).
   - `check_hist_chunk` refuses any ext2010h chunk not in its own root's list (for example 6A 2010-06, TN 2015-12, HE
     2017-06).
   - Its own session id for BOTH the quote and the buy of ext2010h (config below), so ext2010h's quote lines are
     separable from E.14's (the quote tool's ledger fallback, E.15, can then never return an older session's line for
     this plan). es2011 and ext2010 keep STAGE_E14_SESSION_ID for quotes and their v10 buy sessions.
   - A4: a `--roots ROOT [ROOT ...]` option that restricts `--buy` (and `--quote-only`) of plan ext2010h to those
     roots: each a root of the plan, distinct, non-empty; refused (RC_REFUSED, before any vendor call) for es2011 and
     ext2010, so C1's plan path is unchanged. Everything else in the buy (preflight, registration of E16-H1..H5 under
     label E16, caps, settle deltas, the 3% stop, the free metadata fetch for the bought roots) is the existing logic.
   - Do NOT fix `quotes_from_ledger`'s fallback (it is not in the diff list; the lead guards every quote by script).
2. data/hist_calendar.py: HIST_GROUPS accepts "livestock"; add data/calendars/hist2010/livestock.json as a BYTE copy
   of reports/stage_e16_calendars/hist2010_livestock.json (assert the sha256 the E.16 freeze records). If the loader
   cannot parse it unchanged, stop and report: do not edit the JSON.
3. data/hist_store.py: build plan "ext2010h" stores for the 21 roots with the same per-root logic as "ext2010" (inputs =
   exactly the root's own chunk list from its purchase manifest; layout
   `processed_hist/ext2010h/<ROOT>/ohlcv-1m_<ROOT>_v_0_2010-07-01_2019-04-30_ext2010h.parquet`; metadata "plan":
   "ext2010h"; the hist group calendar of the root, livestock included). `--plan` accepts ext2010h.
4. data/config.py: `STAGE_E17_EXT2010H_SESSION_ID = "stage-E.17-ext2010h"` and `E17_EXT2010H_SESSION_CAP_USD = 0.00`
   (placeholder: 0.00 refuses every buy; the lead sets it and ACCOUNT_2_CAP_USD from the fresh quote before the
   commit). Do not change ACCOUNT_2_CAP_USD or any other value. Comments in the file's style.
5. Tests (new files tests/test_e17_v12_*.py; synthetic only; tmp ledgers, tmp registries, fake clients):
   - the plan: 1,993 chunks, per-root counts and first/last chunk equal to the windows file, distinct keys, first/last
     trade dates, the session id, es2011/ext2010 unchanged;
   - check_hist_chunk refusals (outside a root's list, past 2019-05-01, another plan's chunk);
   - `--roots`: restricts the items, refuses a non-plan root, duplicates, an empty list and other plans;
   - the buy refuses at the 0.00 cap and without E16-H1..H5 registered under label E16; with a nonzero cap and the
     registration, a fake-client buy of a 2-root selection buys exactly those roots' chunks (no other root touched);
   - the quote of ext2010h writes its ledger lines under the new session id;
   - the livestock calendar loads through data.hist_calendar and equals base_rules.calendars' parse on its trade
     dates, early halts and unsourced dates;
   - the store builder on synthetic ext2010h chunks: a 2010-07 root (whose first trade date 2010-07-01 is partial: the
     2010-06-30 17:00-19:00 CT part of its Globex session lies in the unbought June chunk), a late root (TN), and a
     livestock root (LE); and base_rules.hist_plan's check_name, check_plan (default_resolver) and check_bookings
     accept the written store. If the builder refuses the partial first trade date, STOP and report the exact
     refusal; do not change the plan's dates or drop rows on your own.
   Existing tests: change none, except an assertion that pins a value this diff must change (for example a tuple of
   plan names or groups). List each such change with the reason.

## Boundaries

- Never change a file reports/stage_e16_freeze.json hashes (verify at the end:
  `uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected
  5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4`), nor data/pull_step2.py, screening/, rules/,
  sim/, base_rules/, c1_replication/, ml_route_v2/, strategy/. Do not rebuild reports/stage_e2b_harness_freeze.json.
- No vendor call, no key or .env read, no write to ledger/, no read of data/processed*, data/vendor, data/sealed.
- Tests at nice 10 (`nice -n 10 uv run python -m pytest -q -p no:cacheprovider <files>`): your new files and every
  existing test file that imports data.pull_hist, data.hist_store, data.hist_calendar or data.config. Not the full
  suite (the lead runs it).
- If anything needs a design or statistical decision the spec does not settle, take the conservative option only if
  it is reversible and list it; otherwise stop and report.

## Output

- The diff: `git diff` plus the new files, written to
  /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e17_briefs/v12.diff (apply-able with `git apply` on main
  at the v11+C1 commit).
- A report /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e17_briefs/v12_report.md: files changed, each
  choice and its reason, existing assertions changed, tests run with pass counts, the E.16 freeze verify output,
  anything unfinished.
- Return: the two paths, a summary of at most 200 words, and anything you could not finish.
