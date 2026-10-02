# Brief: MemberCoder-A-OpusXHigh (Stage E.9 Task 2, coder A), worker-xhigh on opus

Objective: write the K8 cluster tables (_calendar.py, _releases.py, with their generator) FIRST, then
code K8-flight-01 in both variants (H30 and HEOD; traded MGC q_c 1, signal leg MES), exactly as
reports/stage_e9_member_specs.md states them, with unit tests on synthetic bars.

Read first (by section): reports/stage_e9_member_specs.md header, section 0, section 1, section 5,
section 6 and section 7 (the readings and rulings govern; do not re-read the catalog except to check a
line the spec cites: reports/stage_e0_catalog_K8.md); strategy/stage_e/_template.py;
strategy/stage_e/interface.py; screening/stage_e_freeze.py lines 1-90 (ALLOWED_IMPORTS, BANNED_NAMES;
a member imports only those and its own package strategy.members.k8).
Precedents to adapt (audited and frozen): the calendar table pattern strategy/members/k1/_calendar.py,
k3/_calendar.py, k6/_calendar.py and their generators (reports/stage_e8_briefs/gen_k6_tables.py) and
table tests (tests/test_k6_members_tables.py); the release table pattern strategy/members/k5/_releases.py
and k4/_releases.py; a multi-leg member strategy/members/k6/crushgap.py and
tests/test_k6_members_crushgap.py (engine-level tests with run_engine on synthetic frames, as
tests/test_stage_e_alignment.py lines 140-150 does with an MES signal leg); a rolling-reference member
strategy/members/k4/ovr.py and k5/ovr.py (20 reference dates, warm-up K4-L-09).

Part 1, the tables (spec S0.11; write these first: coder B imports them):
- reports/stage_e9_briefs/gen_k8_tables.py: generates strategy/members/k8/_calendar.py and
  strategy/members/k8/_releases.py from data.group_session.load_group_calendar(group) for equity,
  crypto, metals, energy, fx, rules.sessions.flatten_time_ct, and the frozen release calendar
  reports/stage_e2b_release_calendar.json (record its sha256 and the generator's sources in each
  module's docstring). Table range 2019-05-01..2026-06-19.
- _calendar.py: EQUITY_FULL_SESSIONS (roots MES and MNQ must agree), CRYPTO_FULL_SESSIONS (MBT),
  METALS_FULL_SESSIONS (MGC), ENERGY_FULL_SESSIONS (MCL), FX_FULL_SESSIONS (6C): frozenset[date] of the
  group's trade dates with no early halt and flatten_time_ct(root, d) == 15:08 for every listed root;
  FLIGHT_DATES = sorted EQUITY & METALS, OILCAD_DATES = sorted ENERGY & FX, WKNDBTC_DATES = sorted
  EQUITY & CRYPTO (tuples). A small pure helper for the reference dates is welcome
  (`previous_dates(dates, d, k) -> tuple[date, ...]`: the k most recent elements strictly before d).
- _releases.py: GUARD_INSTANTS: dict root -> tuple[int, ...] (sorted UTC epoch seconds) for "MGC", "6C"
  and "MNQ": every row of the frozen release calendar dated 2019-05-01..2026-06-19 whose "products"
  include the root, plus the lead's corrections in spec section 7 (if any); `in_guard(root, t_ns)`:
  True iff some R satisfies R <= t_ns / 1e9 < R + 120 (integer arithmetic on ns).
- tests/test_k8_members_tables.py: recompute every table from its sources and assert equality; assert
  each group set equals the earlier clusters' frozen set where one exists (strategy.members.k1._calendar
  EQUITY_FULL_SESSIONS, k3 FX_FULL_SESSIONS, k4 ENERGY_FULL_SESSIONS, k5 METALS_FULL_SESSIONS, k7
  CRYPTO_FULL_SESSIONS; check their names by grep) over the common date range; if a set differs, do not
  "fix" it: report every differing date to the lead in your report and keep the K8 table as the spec
  defines it. Pin the research-window counts the lead quotes in section 7 and in_guard's edges (R and
  R + 60 s guarded, R + 120 s and R - 60 s not).

Part 2, K8-flight-01 (spec section 1, readings K8-L-02..K8-L-10):
- strategy/members/k8/flight.py: one member class with a variant field ("H30" or "HEOD"), factories
  make_h30 and make_heod, names "K8-flight-01 H30 MGC" and "K8-flight-01 HEOD MGC", legs
  (LegSpec("MGC", True), LegSpec("MES", False)), trading_windows per spec S0.12, q_c from
  load_frozen_tables().vehicles["MGC"].q_c, ticks from rules.products.product(root).vendor_tick.
  The member collects, per trade date it sees (by CT date and clock, spec S0.4), the defined block
  returns r_k (exact Fractions); Q(d) from the 20 most recent FLIGHT_DATES before d with the warm-up of
  K4-L-09; triggers, C6 skip with in_guard("MGC", fill minute), first non-skipped trigger only, the
  entry-bar-missing rule (K8-L-06), E.3-L-08, T_e from the account (K8-L-07), the H30 / HEOD exits,
  exits resent (E.3-L-22). Keep per-date state small (the r values of at most the last ~25 dates).
- tests/test_k8_members_flight.py (split if large): pin every rule with synthetic bars: block clock
  (t_k from 08:35 to 14:55; the k = 1 bars 08:34 and 08:29; no block at 15:00); r_k exactness and the
  instrument_id guard per computation (an MES roll inside a block: no trigger at t_k, later blocks
  still trigger); Q(d): n < 1,200 no trade, n = 1,200 trades, m = ceil(n/200) at n = 1,200, 1,201, 1,540
  with duplicate values; the trigger r_k <= Q(d) (equality triggers) and r_k < 0 (a non-negative r_k at
  or below Q(d) does not); warm-up (the 20th and 21st eligible dates); reference dates from
  FLIGHT_DATES (a non-full date such as 2025-11-28 is skipped as a reference date and as d); the first
  trigger only (a second trigger the same day does nothing); the C6 skip (an FOMC date's 13:00 trigger
  is skipped and a 13:05 trigger enters; a non-FOMC date's 13:00 trigger enters); the entry bar
  missing at the first trigger (no trade on d); an MES bar arriving late or missing (an MES bar absent
  at t_k - 1 and present one minute later is never used: no trigger at t_k, no forward fill); an MGC
  bar missing at t_k (the engine fills later: T_e is the later minute and H30's exit counts from it);
  H30's exit at T_e + 29 (fill T_e + 30), the cap at 15:04 for late entries (14:40 entry exits at 15:04),
  HEOD at 15:04; a missing exit bar (first later present bar); no MES intent ever; nothing after 15:05.
  Engine-level tests (run_engine on synthetic two-leg frames, as tests/test_stage_e_alignment.py):
  (1) the entry fills on MGC at the open of t_k and the exit at T_e + 30 (H30) and 15:05 (HEOD), no MES
  position; (2) the engine refuses the open when the MES bar at t_k - 1 is missing (D11.5) - which the
  member never emits anyway - and refuses an open on a roll-blackout date of the SIGNAL leg only (pass
  the blackout to the rules object as the runner would; this pins V16(a) end to end with the frozen
  engine, not a member re-implementation). Every test must fail on a mutant of the rule it pins: for
  each literal, time and comparison, run the mutant (change it, run the test, restore) and list the
  mutants and the tests that killed them in your report. Run the freeze static check on your files
  (screening.stage_e_freeze.check_member_source or the cluster check).
- reports/stage_e9_coder_A.md: files, what each test pins, the mutant table, the command lines and
  results, any difference found in the table cross-checks, any question raised. If the harness
  refuses that write, put the full report text in your final message instead.

Run tests with `uv run pytest -q <your test files> tests/test_stage_e_template.py
tests/test_stage_e_freeze.py` with PYTHONPYCACHEPREFIX unset (three bytecode tests fail with it set);
run any python script with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/20d17daf-bbde-4768-93fa-814f35cbb398/scratchpad/coderA/.
Keep every scratch file (mutant scripts, logs) under that coderA/ folder: coder B shares the scratchpad
and uses coderB/. /tmp is a RAM-backed tmpfs: never copy the repository, data/, .venv or .git into it;
mutate files in place and restore them (keep a pristine copy of only the file you mutate). Do not run
the full suite (the lead does). Keep command output short (-q, tail). Run CPU-heavy work at nice 10.

Ambiguity: if the spec leaves any detail open, or two readings could change a trade, STOP and report
the question to the lead (return early with the question); do not choose. Boundaries: no bar file is
opened and no bar loader is called; no web access; write only the files named above (plus
strategy/members/k8/_common.py if you share small helpers with coder B; name it in the report); never
write strategy/members/k8/__init__.py (it exists, 0 bytes, and must stay empty), oilcad.py, wkndbtc.py
or tests/test_k8_members_oilcad*.py / _wkndbtc*.py (coder B's); no change to the harness (screening/,
rules/, data/, strategy/stage_e/) or to any other cluster; no commit; no workers.

Return: the paths, a summary of at most 200 words, and anything you could not finish.
