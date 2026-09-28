# Brief: MemberCoder-B-OpusXHigh (Stage E.7 Task 2, coder B), worker-xhigh on opus

Objective: code K1-vxnband-01 and K1-vwap-01 (Nasdaq-100, MNQ, q_c 1) and the cluster's literal tables
(equity calendar, VXN), exactly as reports/stage_e7_member_specs.md states them, with unit tests on
synthetic bars and table pins.

Read first (by section): reports/stage_e7_member_specs.md header, section 0 (S0.3, S0.4, S0.6-S0.12
matter most), sections 4-5 and section 8 (the readings govern; check a catalog line only where the
spec cites it: reports/stage_e0_catalog_K1.md); strategy/stage_e/_template.py;
strategy/stage_e/interface.py; screening/stage_e_freeze.py lines 1-90 (ALLOWED_IMPORTS, BANNED_NAMES).
Precedent to adapt (audited and frozen): strategy/members/k7/_calendar.py (CRYPTO_FULL_SESSIONS with
the K3-L-11 early-F test) and its generator reports/stage_e6_briefs/gen_k7_calendar.py;
strategy/members/k3/_mehedge_signal.py (an external index series as a literal table, generated from a
saved file with its sha256, pinned by tests/test_e4_k3_members_m_signal.py); strategy/members/k7/
_event_common.py, rev2h.py, montrend.py and strategy/members/k4/ovr.py (multi-decision members) and
their tests, including the engine-level tests that call screening.stage_e_engine.run_engine on
synthetic frames (grep run_engine in tests/test_k7_members_events.py or tests/test_e4_k4_members_b.py).

Outputs:
- reports/stage_e7_briefs/gen_k1_tables.py, which writes:
  - strategy/members/k1/_calendar.py (spec S0.11): EQUITY_TRADE_DATES and EQUITY_FULL_SESSIONS
    2019-05-01..2026-06-19 from data.group_session.load_group_calendar("equity") (is_trade_date,
    early_halt_ct) and rules.sessions.flatten_time_ct(root, d) for MNQ, M2K and MYM (assert they agree;
    the regular F is 15:08), SOURCE_SHA256 of the calendar module(s), and a comment naming any date
    where the early-halt test and the F test disagree.
  - strategy/members/k1/_vxn.py: VXN_CLOSE (ISO calendar date -> the CLOSE field as its exact decimal
    string, every row dated 2019-04-30..2026-06-19) from data/vendor/index_history/vxn/VXN_History.csv,
    with that file's sha256. ReleaseChecker-OpusMed (Task 1b, running in parallel) is saving that file;
    write the calendar and vwap first. When the file exists, generate the table; the lead will send
    Task 1b's rulings (reports/stage_e7_member_specs.md section 9) as a small follow-up, which may
    change the table. Do not read the release check yourself unless the lead asks.
- strategy/members/k1/vxnband.py and vwap.py (and _event_common.py if you share helpers), each with a
  member class with `name`, `trading_windows` (S0.12), `on_minute` and a factory `make_mnq`. Do
  not write strategy/members/k1/__init__.py (0 bytes, stays empty), cp1.py, cp2.py, cp3.py or
  _port_common.py (coder A's).
- tests/test_k1_members_tables.py (table pins recomputing EQUITY_TRADE_DATES, EQUITY_FULL_SESSIONS and
  VXN_CLOSE from their sources; skip with a clear reason only if a source file is absent),
  tests/test_k1_members_vxnband*.py and tests/test_k1_members_vwap*.py. Pin, with synthetic bars:
  vxnband: C_prev from the most recent complete date (an early-halt or incomplete d-1 skipped; C_prev's
  guard against d's 08:30 bar; a missing 08:30 bar); V taken from the calendar date of the EC-CAL trade
  date before d, never d's own close, and missing V (for example the Tuesday after Memorial Day
  2025-05-27, whose d-1 2025-05-26 has no VXN row) gives no trade; V availability from 08:30 CT on d:
  no decision on any bar before the 08:30 bar of d reads V, and a breach on the 08:30 bar itself trades;
  the band exactly (a close exactly at U or L does not trade, one tick beyond does; test with a V that
  has two decimals); the regime cuts (V = 19.99 and 30.00 trade, 20.00 and 29.99 do not); sell above,
  buy below; the first breach uses the day (a later breach on the other side is ignored); the scan
  window (a first breach on the 14:28 bar trades and exits on the 14:58 bar; on the 14:29 bar it does
  not); a missing scan bar or an instrument change before the first breach ends the day's search; the
  exit on the bar at entry-intent + 30 min and, if missing, the first later bar; not-full-session d
  (early halt or early F) not traded. vwap: the VWAP sign by exact arithmetic (a close exactly at VWAP
  keeps the previous sign; 0 before the first sign), sum(volume) = 0 gives no action, a flat entry in
  s_t's direction, the reversal's two intents on one bar (exit, then entry), the minimum hold (no exit
  on the fill bar k, exit allowed on k+1), no intent while an order is pending, the 20-entry cap counted
  on intents incl. reversal legs and the exit-to-flat after the 20th, no entry from the 14:57 bar, the
  final exit on the 14:58 bar (missing: first later bar), a missing bar ending new entries for the day
  while an open position keeps its exits, an instrument change (no new entry, exit intent on that bar),
  an engine-closed position (flat account: the rule continues), not-full-session d not traded. Both: the
  CPI window (on 2025-05-13 bars at 07:25-07:35 CT produce no intent) and the event minutes (09:00 and
  13:00 bars on ISM and FOMC dates: the members emit exactly what their rule says). Add one
  engine-level test (run_engine on synthetic frames, as the precedent tests do) showing vwap's reversal
  pair is accepted and both fill at the same next open. Every test must fail on a mutant of the rule
  it pins: for each literal, time and comparison, run the mutant (change, run, restore) and list
  mutants and killing tests in your report. Also run the freeze static check on your files.
- reports/stage_e7_coder_B.md: files, table sources and sha256, what each test pins, the mutant table,
  commands and results, any question you raised.

Run tests with `uv run pytest -q <your test files> tests/test_stage_e_template.py
tests/test_stage_e_freeze.py` with PYTHONPYCACHEPREFIX unset (three bytecode tests fail with it set);
run scripts with PYTHONPYCACHEPREFIX set to a fresh directory under /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/99bb7678-38d8-413c-82c8-d103cf2d3163/scratchpad/.
Do not run the full suite (the lead does). Keep command output short. Never print the VXN file or the
tables; print counts. Run CPU-heavy work at nice 10.

Ambiguity: if the spec leaves a detail open, or two readings could change a trade, STOP and report
the question to the lead; do not choose. Boundaries: no bar file opened and no bar loader called; no
web access; no edit outside the files named above; no change to the harness (screening/, rules/,
data/, strategy/stage_e/) or to other clusters; no commit; no workers.

Return: the paths, a summary of at most 200 words, and anything you could not finish.
