# Brief: MemberCoder-B-OpusXHigh (Stage E.8 Task 2, coder B), worker-xhigh on opus

Objective: code K6-limitcont-01 (HE, LE), K6-wasdepre-01 (ZC, ZS) and K6-wasdepost-01 (ZC), q_c 1
each, and the cluster's literal tables (grain and livestock calendars, WASDE dates, livestock limits),
exactly as reports/stage_e8_member_specs.md states them, with unit tests on synthetic bars and table
pins.

Read first (by section): reports/stage_e8_member_specs.md header, section 0 (S0.3, S0.4, S0.6-S0.12
matter most), sections 5-7, section 9 (the readings govern, especially K6-L-06..K6-L-12) and section
10 (Task 1b's rulings, final); check a catalog line only where the spec cites it
(reports/stage_e0_catalog_K6.md); strategy/stage_e/_template.py; strategy/stage_e/interface.py;
screening/stage_e_freeze.py lines 1-90 (ALLOWED_IMPORTS, BANNED_NAMES); rules/price_limits.py lines
1-63 and 690-840 (limit_period, SETTLEMENT_WINDOW_CT, settlement_window_ct, settlement_proxy) and
screening/stage_e_rules.py lines 241-273 and 329-334 (how the engine computes the proxy: the member
must compute the same number).
Precedent to adapt (audited and frozen): strategy/members/k1/_calendar.py and its generator
reports/stage_e7_briefs/gen_k1_tables.py (trade dates and FULL_SESSIONS with the K3-L-11 early-F test);
strategy/members/k4/_calendar.py, _releases.py, _event_common.py, ngpre.py and
tests/test_e4_k4_members_b*.py (release-date members and their table pins); tests/test_k1_members_tables.py.

Order of work:
1. FIRST write strategy/members/k6/_calendar.py (spec S0.11: GRAIN_TRADE_DATES,
   LIVESTOCK_TRADE_DATES, GRAIN_FULL_SESSIONS, LIVESTOCK_FULL_SESSIONS, LIVESTOCK_EARLY_HALT_CT,
   previous_trade_date) through the generator reports/stage_e8_briefs/gen_k6_tables.py; coder A's
   crushgap imports it and waits for the file. Keep those names and types exactly.
2. strategy/members/k6/_wasde.py (WASDE_DATES from the frozen release calendar
   reports/stage_e2b_release_calendar.json rows "release" == "WASDE" at 12:00 America/New_York,
   2019-05-01..2026-06-19; DROPPED_WASDE empty, by ruling R-1b-1, with a comment citing it) and
   strategy/members/k6/_limits.py (LIMIT_PERIODS for HE and LE from rules.price_limits.LIMITS;
   SETTLEMENT_WINDOW_LIVESTOCK; DROPPED_LIMIT_DATES = {"LE": the 14 livestock trade dates
   2026-06-01..2026-06-18}, by ruling R-1b-2, each with its reason: CME SER-9736 sets a new initial
   $0.0850 from trade date 2026-06-01, the frozen table $0.0725), all from the same generator, each
   module recording its sources' sha256.
3. strategy/members/k6/limitcont.py (make_he, make_le), wasdepre.py (make_zc, make_zs), wasdepost.py
   (make_zc), and _event_common.py if you share helpers. Each: a member class with `name`,
   `trading_windows` (S0.12) and `on_minute`.

limitcont in short (spec section 5, K6-L-06..K6-L-09, R-1b-2): c = d's 08:30 bar's instrument_id;
S(c, x) for x = d-1, d-2, d-3 (the three LIVESTOCK_TRADE_DATES before d) is the engine's D9.7 settlement
proxy of trade date x, re-implemented exactly (window [12:59:30, 13:00:00) CT, or the 30 seconds ending
at the early halt; the volume-weighted close of the bars whose minute overlaps the window, else the
last close of x before the window end), using only bars that carry c; L(p, x) = the initial limit in
vendor ticks from LIMIT_PERIODS (HE 160, then 190 from 2025-09-02; LE 260, then 290 from 2025-06-02);
event iff S(d-1) - S(d-2) = +L(d-1) (buy) or -L(d-1) (sell) exactly, and S(d-2) - S(d-3) is neither
+L(d-2) nor -L(d-2); no trade if d-1 or d-2 is in DROPPED_LIMIT_DATES[root]; entry on the 08:44 bar
(must exist and carry c); exit on the first bar at or after 12:58; d in LIVESTOCK_FULL_SESSIONS. The
member keeps the bars it needs from the trade dates it has seen (it sees every bar of its leg in
order); a date it has not seen gives no trade.

Outputs:
- the modules above. Do not write strategy/members/k6/__init__.py (0 bytes, stays empty), cp1.py,
  cp2.py, cp3.py, crushgap.py or _port_common.py (coder A's).
- tests/test_k6_members_tables.py (table pins recomputing every table from its sources: the calendars
  through data.group_session / rules.sessions, the check that every root of a group gives the same F,
  WASDE_DATES from the release calendar JSON (and the 14 research-window dates listed in the spec's
  source section), LIMIT_PERIODS against rules.price_limits.LIMITS and limit_period(root, d) on every
  livestock trade date, every amount an integer number of vendor ticks, DROPPED_LIMIT_DATES exactly
  the 14 LE trade dates; skip with a clear reason only if a source file is absent),
  tests/test_k6_members_limitcont.py, tests/test_k6_members_wasde.py. Pin, with synthetic bars:
  limitcont: the member's settlement proxy equals rules.price_limits.settlement_proxy over
  settlement_window_ct on synthetic bars (a regular day, the fallback with the 12:59 bar missing, an
  early-halt date such as 2025-12-24 with its 12:15 halt, a day with no bar before the window end); a
  limit-up close (exact: buy on the 08:44 bar), one tick short (no trade), a limit-down close (sell);
  the expanded-limit guard (d-2 itself a limit close: no trade on d); the limit period boundary (HE
  2025-09-02: L(d-1) and L(d-2) each from their own date's period); a dropped limit date (LE d-1 or d-2
  in 2026-06-01..06-18: no trade); c's guard (a settlement bar or the 08:44 bar with another
  instrument_id: no trade); a missing 08:30 or 08:44 bar (no trade); d-3 not seen (no trade); d not in
  LIVESTOCK_FULL_SESSIONS (2025-11-28, 2025-12-24: no trade); the exit on the first bar at or after
  12:58. wasdepre and wasdepost: a WASDE date trades and a non-WASDE date does not (use a real
  research-window date such as 2025-06-12, and 2025-10-09, the cancelled October WASDE, which must be
  absent); the moved November 2025 release (2025-11-14 in the table, 2025-11-10 absent); a date in
  DROPPED_WASDE does not trade (monkeypatch a synthetic entry); the signals (Dr from the 08:30 open and
  the 10:29 close; R from the 10:59 and 11:14 closes), zero signal, the direction, a missing signal or
  entry bar, the instrument guard, the exits (wasdepre on the 11:14 bar, or the first later bar if it
  is missing; wasdepost on the first bar at or after 13:13), no intent on bars in [11:00, 11:02) beyond
  what the rule says. Engine-level tests (run_engine on synthetic frames, as the precedent tests do):
  (1) limitcont after a limit-up close: the 08:44 intent fills at 08:45; then the price moves beyond the
  D9.7 stop level and the engine's forced exit closes the position; the member sends no further exit or
  entry that day; (2) the engine refuses the 08:45 open when the price is already beyond the stop
  level, and the member does not retry. Every test must fail on a mutant of the rule it pins: for each
  literal, time and comparison, run the mutant (change, run, restore) and list mutants and killing
  tests in your report. Also run the freeze static check on your files.
- reports/stage_e8_coder_B.md: files, table sources and sha256, what each test pins, the mutant table,
  commands and results, any question you raised. If the harness refuses that write, put the full
  report text in your final message instead.

Run tests with `uv run pytest -q <your test files> tests/test_stage_e_template.py
tests/test_stage_e_freeze.py` with PYTHONPYCACHEPREFIX unset (three bytecode tests fail with it set);
run scripts with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/94d6572b-fdf2-4814-9116-60c2521d80a0/scratchpad/coderB/.
Keep every scratch file under that coderB/ folder: coder A shares the scratchpad and uses coderA/.
Do not run the full suite (the lead does). Keep command output short. Never print the tables; print
counts. Run CPU-heavy work at nice 10.

Ambiguity: if the spec leaves a detail open, or two readings could change a trade, STOP and report the
question to the lead; do not choose. Boundaries: no bar file opened and no bar loader called; no web
access; no edit outside the files named above; no change to the harness (screening/, rules/, data/,
strategy/stage_e/) or to other clusters; no commit; no workers.

Return: the paths, a summary of at most 200 words, and anything you could not finish.
