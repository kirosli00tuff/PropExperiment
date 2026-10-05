# Brief: V10Coder-OpusXHigh (Stage E.14 Task 4: harness v10)

You work in your own git worktree (the Agent tool made it). The lead merges and commits; you do not commit to
main, push, or run anything that spends money. The user is asleep: decide, record each decision in your report,
and continue. Read the code by section (grep, line ranges), as CLAUDE.md's context-hygiene rules require.

## Context (read by section)
- docs/prompts/STAGE_E.14.md (Scope, Guardrails, Task 4, Task 6, Task 7) and CLAUDE.md (Invariants, Compute).
- reports/stage_e13_prereg_gexmom.md (C2: sections 2, 3, 4, 5, 9) and reports/stage_e13_prereg_ngrepl.md (C1:
  sections 2, 9); C1's annex reports/stage_e13_ng_replication_draft.md sections 5 and 8 and rulings C5, C6, C12.
- Code: data/config.py, data/spend_gate.py, data/pull_step2.py, data/step2_store.py, data/build_bars.py (as the
  step 2 store uses it), data/stage_e_bars.py, data/group_session.py, data/cme_calendar.py (Holiday types),
  data/calendars/__init__.py, screening/harness_freeze.py, and their tests (tests/test_e2b_pull_step2*.py,
  tests/test_e2b_step2_store*.py, tests/test_*stage_e_bars*.py; find them by grep).

## Hard boundaries
- NEVER read, decode or open any market data: nothing under data/vendor, data/processed*, data/sealed,
  reports/step2/ bar summaries' values, ~/.cache/propexp_e12_phase1, no *.parquet/*.dbn*/*.npy/*.pkl of real
  data. Tests use synthetic fixtures only. No Databento call of any kind (not even quotes or metadata); no
  network. No .env read, no key printed. Do not touch live/, ops/, REGISTRATION.md, ml_route_v2/ (frozen by its
  own manifest), strategy/members/, rules/ (except reading), or any frozen manifest JSON. Do not rebuild
  reports/stage_e2b_harness_freeze.json: the lead rebuilds it after merging the calendar files. Do not edit
  ACCOUNT_2_CAP_USD (stays 249.67, V26) or any earlier stage's config block.
- Existing behavior for every date and store from 2019-05 on must be byte-for-byte unchanged: all new code is
  additive, and existing tests must still pass.

## What v10 adds (every item with tests)
1. Config (data/config.py), a new E.14 block, the earlier blocks untouched:
   - STAGE_E14_SESSION_ID = "stage-E.14-2026-10-05".
   - E14_SESSION_CAP_USD = 0.00 (placeholder: the lead sets it from the fresh ES quote x 1.03, in whole cents,
     never above acct-2's headroom $18.07, before the manifest). E14_REQUEST_CAP_USD = 3.00 (D13).
   - E14_EXT2010_SESSION_CAP_USD = 0.00: C1's buy stays refused under v10; a later harness may raise only this
     cap and ACCOUNT_2_CAP_USD (the C1 freeze will say so). E14_BUY_ACCOUNT = acct-2's id (acct-1's $1.61 fits
     no root). Comment every constant with its source, as the E.12 block does.
2. Two new plans in data/pull_step2.py (quote-only for both; buy as below), each refusing ANY chunk outside it
   before a vendor call:
   - "es2011" (test C2): ES.v.0, the 96 monthly chunks 2011-05-01..2019-05-01 (exclusive, 00:00 UTC).
   - "ext2010" (test C1): NG, NQ, ZN, 6E, GC, ZC (.v.0), per root the partial chunk 2010-06-06..2010-07-01
     (GLBX.MDP3 starts 2010-06-06; ruling C5's fixed trade-date start 2010-06-07) then the 106 monthly chunks
     2010-07..2019-04, 107 per root, ending 2019-05-01 (exclusive; ruling C6: no May-2019 splice).
   - CLI: `--quote-only --plan es2011|ext2010 --quotes-out <json>` (ledger $0.00 lines under STAGE_E14_SESSION_ID
     and the named --account), and `--buy --plan es2011 --account <acct-2> --harness-sha256 <sha>`.
   - The es2011 buy goes through the existing gate (SpendGate) with the E.14 session id, E14_SESSION_CAP_USD,
     E14_REQUEST_CAP_USD and acct-2 only; it refuses to start when E14_SESSION_CAP_USD is 0.00, when the account
     is not acct-2, or when the C2 registration (item 6) is missing from the trial registry. The ext2010 buy
     refuses while E14_EXT2010_SESSION_CAP_USD is 0.00 and unless C1's registration is present.
   - Per chunk: a billed amount above its quote by more than 3% stops the buy before the next chunk (check what
     the gate already does; add the check if missing) and is recorded.
   - Purchase manifests and raw chunk paths must not collide with any existing file (NG has a step 2 manifest
     reports/step2/purchase_NG.json; never overwrite it). Use plan-specific names, e.g.
     reports/hist/purchase_<ROOT>_<plan>.json. The free metadata the store needs (symbology for the rolls, the
     dataset condition file for the window) is fetched by the buy run (free calls, logged), never by tests.
3. Hist calendars: the lead will drop JSON files in schema "e14_hist_calendar/1"
   (reports/stage_e14_briefs/calendar_rules.md gives the schema) into data/calendars/hist2010/<group>.json for
   equity, rates, fx, energy, metals and grains (coverage 2010-06-01..2019-05-31). Write the loader:
   `data.group_session.load_hist_group_calendar(group) -> GroupCalendar` (or a new module data/hist_calendar.py if
   cleaner), building Holiday entries (kind full_closure / early_halt; late_open as the grains LateOpen
   convention), SessionSpec rows, coverage, assert_coverage (refusing any date outside 2010-06-01..2019-05-31) and
   the set of UNSOURCED dates (excluded and counted by every reader: C1 ruling C12, C2 section 3). It must refuse a
   malformed file, an entry outside coverage, an unknown grade, and treat an entry whose status grade is
   "unverified" as an unsourced date. It records each file's sha256. Tests use fixture JSONs
   (tests/fixtures/e14_hist/...). Never route existing (2019-05 on) callers to it.
4. Stores (a new module, e.g. data/hist_store.py, reusing data/build_bars.py and data/step2_store.py logic where
   it can without changing their behavior):
   - "es2011": ES, trade dates 2011-05-02..2019-04-30 (2011-05-02 is needed for the first date's prior close);
   - "ext2010": each of the six roots, trade dates 2010-06-07..2019-04-30;
   - inputs only the plan's chunks from its purchase manifest (sha256 and record counts checked), refused before
     any file is opened otherwise; rows booked to CME trade dates with the hist calendar of the root's group;
     rows outside the window dropped right after decoding, before any check reads a price; rolls from the free
     symbology over the window; the roll blackout as data/stage_e_bars.py:30-33 (splice date plus the two group
     trade dates before it); unsourced calendar dates excluded and counted;
   - bars inside a scheduled closure beyond the close minute: kept and flagged automatically (v9's
     keep-and-flag principle, fixed now, before any data exists), counted in the summary, never held;
   - the build prints counts only (rows, trade dates, excluded dates by reason, rolls), never a price; writes a
     0444 parquet under a new data root (add it to harness_freeze.DATA_SUBDIRS) and a summary JSON with hashes.
   - loaders in data/stage_e_bars.py (or the new module): `load_hist_leg(root, plan, *, expected_sha256)` giving
     the LegFrame shape the step 2 loader gives, refusing rows outside the plan's window, giving the blackout.
5. Test C2's code: screening/stage_e14_c2.py (a CLI `python -m screening.stage_e14_c2`), exactly the rule of
   reports/stage_e13_prereg_gexmom.md sections 3-5, with no free parameter:
   - inputs: the es2011 store (expected sha256), the hist equity calendar, the GEX CSV (path and expected sha256;
     columns date, price, dix, gex), GEX_LAG (1 = the row of the latest CSV date strictly before d; 2 = two rows
     back; a CLI argument the freeze fixes), --harness-sha256 (preflight first), --freeze-sha256 (the sha256 of
     reports/stage_e14_prereg_C2.md, checked against the file), --out <json>;
   - eligible date d in 2011-05-03..2019-04-30: a trade date of the hist equity calendar; not an early-halt or
     late-open date; not unsourced; not an ES roll-blackout date; its prior trade date exists in the calendar;
     the four bars present: b_14:29, b_14:30, b_15:00 on d and b_14:59 on the prior trade date (b_s = the bar
     starting at s CT); a GEX row per GEX_LAG. Each failing date is counted by reason;
   - R_rod = close(b_14:29 on d) / close(b_14:59 on prior) - 1; side +1 / -1 / 0 (no trade);
     g = side x (open(b_15:00) - open(b_14:30)) / 0.25 (MES ticks);
   - T1 = trades on eligible dates with GEX < 0 (strictly); T2 = trades on every eligible date;
   - c = 0.976 + 0.5191 + 0.5428 = 2.0379 ticks (reports/stage_e2a_costs.md MES check rows 14:30, 15:00; 0.976 =
     1.22 / 1.25); bar = 1.5 x c = 3.05685; per test: n, mean, sd (ddof 1), t = mean / (sd / sqrt(n)), one-sided
     p = Student t survival at t with n - 1 df; pass iff mean >= bar AND p <= 0.025 AND n >= 30. Hypothesis
     verdict PASS iff T1 passes AND mean_T1 > mean_T2; also report "T2 alone passes" per section 5. Any stop
     (store refusal, missing file) gives verdict STOPPED with the reason;
   - run-once: refuses if its marker file reports/stage_e14_c2_RUN_ONCE.json or the --out file exists; writes the
     marker before reading any bar; refuses unless the trial registry (item 6) holds C2-T1 and C2-T2 registered
     with the same freeze sha256;
   - output JSON: verdict, every statistic, eligible counts and exclusions by reason, T1/T2 trade counts and
     long/short split, the hashes of every input; a count-only helper `count_gex_negative(calendar, gex, lag)` for
     the power check (calendar and GEX only, no bars);
   - tests on synthetic bars and a synthetic GEX file, including the timing rule, ties (R_rod = 0), a missing bar,
     an early-close date, a roll blackout, the pass bar's boundary, and the run-once refusals.
6. Trial registry: screening/trial_registry.py and ledger/trial_registrations.jsonl, append-only (never rewrite;
   refuse a duplicate test id; each line: entry_id, test ids, the freeze file path and sha256, harness sha256, N
   before and after, local time America/Vancouver). The first line is a baseline record N = 471 citing
   reports/E.12_RETURN.md ("New program N = 198 + 273 = 471"); the registry reads N from the last line. A CLI:
   `python -m screening.trial_registry register --test C2 --ids C2-T1 C2-T2 --freeze <path> --freeze-sha256 <sha>
   --harness-sha256 <sha>`. Tests use a temporary ledger path; tests must never append to a real ledger file
   (the E.12 lesson).
7. screening/harness_freeze.py: list the new frozen inputs (the six hist calendar JSON paths, the new data root
   in DATA_SUBDIRS) so the lead's manifest rebuild picks them up; keep everything else.

## Tests and checks
- `uv run pytest -q -p no:cacheprovider <your new and touched test files>` and the existing tests of every module
  you touch; print only the tail. Then the full suite once at nice 10 (about 22 minutes; tail only). Report
  counts.
- Compute limits (CLAUDE.md overnight profile): nice 10, no heavy jobs.

## Output and return
- Your branch's diff against main, summarized in reports/stage_e14_v10_notes.md (in your worktree): every file
  changed or added, every decision you made, the tests and their counts, and anything the lead must do at merge
  (the hist calendar copies, the cap value, the manifest rebuild).
- Return: (1) the worktree path and branch, (2) a summary of at most 200 words, (3) anything not finished.
