# Brief: MemberCoder-A-OpusXHigh (Stage E.8 Task 2, coder A), worker-xhigh on opus

Objective: code the three K6 core ports, K6-cp1-01, K6-cp2-01 and K6-cp3-01, each on ZC, ZW, ZS, ZM,
ZL, HE and LE (q_c 1 each), and K6-crushgap-01 (traded ZS, signal legs ZM and ZL), exactly as
reports/stage_e8_member_specs.md states them, with unit tests on synthetic bars.

Read first (by section): reports/stage_e8_member_specs.md header, section 0, sections 1-4 and
section 9 (the readings govern; do not re-read the catalog except to check a line the spec cites:
reports/stage_e0_catalog_K6.md); strategy/stage_e/_template.py; strategy/stage_e/interface.py;
screening/stage_e_freeze.py lines 1-90 (ALLOWED_IMPORTS, BANNED_NAMES; a member imports only those and
its own package strategy.members.k6).
Precedent to adapt (audited and frozen; the same D6 text): strategy/members/k1/cp1.py, cp2.py, cp3.py,
_port_common.py and tests/test_k1_members_ports*.py (E.7, several exposure factories in one module);
strategy/members/k4/cp1.py (commodity, Globex-open first bar) and tests/test_e4_k4_members_a.py.

What is new for K6:
- Seven exposures per port, factories make_zc, make_zw, make_zs, make_zm, make_zl, make_he, make_le,
  each returning a member whose name is "<member id> <root>" (spec S0.2); q_c from
  load_frozen_tables().vehicles[root].q_c, never a literal; vendor ticks from rules.products (ZC, ZW,
  ZS 0.25; ZM 0.10; ZL 0.01; HE, LE 0.025); O and C from load_frozen_tables().day_session_ct[root]
  (grains 08:30/13:15, livestock 08:30/13:00). Two groups with different clocks (grains have a 19:00
  CT evening session before d and the 07:45-08:30 pause; livestock trades 08:30-13:05 only).
- CP1's first bar (spec section 1, K6-L-01, K6-L-02): grains, the earliest bar with trade_date d whose
  CT open is at or after 19:00 on the calendar day before d (a missing 19:00 bar: the first later bar;
  a date with no evening session: the 08:30 bar of d); livestock, the 08:30 bar exactly (missing: no
  trade). CP1 entries at C-31 (grains 12:44, livestock 12:29), exits at the first bar at or after C-2
  (13:13, 12:58).
- CP2's buffer is 4 x vendor_tick: 1.00 (ZC, ZW, ZS), 0.40 (ZM), 0.04 (ZL), 0.100 (HE, LE); eligible
  bars to 13:15 (grains) or 13:00 (livestock).
- CP3's daily bar [08:30, 13:15) grains with C_d the 13:14 close, [08:30, 13:00) livestock with the
  12:59 close; the grain early halts (2025-11-28, 2025-12-24 at 12:05) and livestock early halts
  (12:05, 12:15) make d-1 incomplete (Family H) and d untraded.
- crushgap (spec section 4, K6-L-03..K6-L-05): three legs; the member's view has bars for ZS, ZM and
  ZL; only ZS is traded. GPM in exact integer units (GPM x 10^4 = 22 t_ZM + 11 t_ZL - 25 t_ZS, derived
  from product(root) and the weights 0.022 and 11, not typed as 22/11/25); filter 200 units,
  non-strict; d-1 = previous_trade_date(GRAIN_TRADE_DATES, d); d must be in GRAIN_FULL_SESSIONS. It
  imports strategy.members.k6._calendar, which coder B writes FIRST (GRAIN_TRADE_DATES,
  GRAIN_FULL_SESSIONS, previous_trade_date; spec S0.11). Code the ports first; start crushgap once
  that file exists (check for it; do not write it yourself). Do not write any other coder B file.

Outputs:
- strategy/members/k6/cp1.py, cp2.py, cp3.py, crushgap.py, and strategy/members/k6/_port_common.py if
  you share helpers (name any other file you add). Each module: a member class with `name`,
  `trading_windows` (spec S0.12) and `on_minute`, and its factories. Do not write
  strategy/members/k6/__init__.py (it exists, 0 bytes, and must stay empty), or any file whose name
  starts with _calendar, _wasde, _limits, _event, limitcont, wasdepre or wasdepost (coder B's).
- tests/test_k6_members_ports*.py (split by port if large) and tests/test_k6_members_crushgap.py. Pin
  every rule with synthetic bars, on each root where the root matters (tick, buffer, clock): signal,
  entry and exit times per group; a missing signal or entry bar (no trade); a missing exit bar (first
  later bar); the instrument guard; zero signal; CP1's grain first bar (Sunday 19:00 for a Monday; a
  missing 19:00 bar takes 19:01; a late-open date such as 2025-12-26 takes the 08:30 bar) and the
  livestock 08:30 bar (missing: no trade); CP2's range, the buffer exactly (a close exactly at
  OR_high + buffer triggers, one tick less does not) for all seven roots, the first-qualifying-bar-
  uses-the-day rule, the 75-present-bar exit count, no entry from C (13:15 grains, 13:00 livestock);
  CP3's CLV cuts (0.8 and 0.2 inclusive, exact), range 0, the complete-day rules and warm-up, a limit
  close (a day whose 13:14 close equals its high, CLV 1: buy), the early-halt exclusion of d and of d-1;
  crushgap's GPM identity and units (pin a hand-computed GPM in USD/bu from vendor prices), the filter
  exactly at -0.02 and +0.02 (trades) and one unit inside (no trade), the direction (G <= -0.02 sells
  ZS, G >= +0.02 buys ZS), d-1 from the calendar (a Monday reads the Friday; the Tuesday after a
  Monday holiday reads the Friday; an early-halt d-1 such as 2025-11-28 gives no trade on 2025-12-01),
  the per-leg guard (a missing 13:14 or 08:30 bar on any leg, or an instrument change on any leg: no
  trade), d not in GRAIN_FULL_SESSIONS (no trade), no intent ever on ZM or ZL, the exit on the first ZS
  bar at or after 13:13. Engine-level tests (run_engine on synthetic frames, as the precedent tests
  and tests/test_stage_e_alignment.py do): (1) crushgap with its three legs fills on ZS at the 08:31
  open and holds no ZM or ZL position, and the engine refuses its open when a signal leg lacks the
  08:30 bar (D11.5); (2) one port (CP3 on a grain root) entered, then the price moves beyond the D9.7
  stop level: the engine's forced exit closes it, and the member sends no further exit or entry that
  day. Every test must fail on a mutant of the rule it pins: for each literal, time and comparison,
  run the mutant (change it, run the test, restore) and list the mutants and the tests that killed
  them in your report. Also run the freeze static check on your files
  (screening.stage_e_freeze.check_member_source or the cluster check).
- reports/stage_e8_coder_A.md: files, what each test pins, the mutant table, the command lines and
  results, any question you raised. If the harness refuses that write, put the full report text in
  your final message instead.

Run tests with `uv run pytest -q <your test files> tests/test_stage_e_template.py
tests/test_stage_e_freeze.py` with PYTHONPYCACHEPREFIX unset (three bytecode tests fail with it set);
run any python script with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/94d6572b-fdf2-4814-9116-60c2521d80a0/scratchpad/coderA/.
Keep every scratch file (mutant scripts, logs) under that coderA/ folder: coder B shares the
scratchpad and uses coderB/. Do not run the full suite (the lead does). Keep command output short
(-q, tail). Run CPU-heavy work at nice 10.

Ambiguity: if the spec leaves any detail open, or two readings could change a trade, STOP and report
the question to the lead (return early with the question); do not choose. Boundaries: no bar file is
opened and no bar loader is called; no web access; no edit outside the files named above; no change
to the harness (screening/, rules/, data/, strategy/stage_e/) or to any other cluster; no commit; no
workers.

Return: the paths, a summary of at most 200 words, and anything you could not finish.
