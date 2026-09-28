# Brief: MemberCoder-A-OpusXHigh (Stage E.6 Task 2, coder A), worker-xhigh on opus

Objective: code the three K7 core ports, K7-cp1-01, K7-cp2-01 and K7-cp3-01 (bitcoin, MBT, q_c 1),
exactly as reports/stage_e6_member_specs.md states them, with unit tests on synthetic bars.

Read first (by section): reports/stage_e6_member_specs.md header, section 0, sections 1-3 and section 8
(the readings govern; do not re-read the catalog except to check a line the spec cites);
strategy/stage_e/_template.py; strategy/stage_e/interface.py; screening/stage_e_freeze.py lines 1-90
(ALLOWED_IMPORTS, BANNED_NAMES; a member imports only those and its own package strategy.members.k7).
Precedent to adapt (audited and frozen; same D6 text): strategy/members/k4/cp1.py, cp2.py, cp3.py,
_port_common.py and tests/test_e4_k4_members_a*.py (also the K3 ports under strategy/members/k3/).

What is new for K7 (spec S0.4 and K7-L-01): O 08:30, C 15:00 from load_frozen_tables(); a bar is
identified by CT calendar date AND clock, never by trade_date and clock alone. MBT bars carry CME's
trade date, so (a) from 2026-06-01 the weekend bars (Friday 16:02 to Sunday 17:00 CT) carry Monday's
trade_date, and (b) on booked-forward holidays (for example Monday 2026-01-19) the holiday's whole
session (Sunday 17:00 to Monday 16:00 CT) carries the next trade date (Tuesday 2026-01-20), so one
trade date spans two CT dates. CP1's first bar is the 17:00 bar on CT date d-1 (after a booked-forward
Monday: the Monday 17:00 bar); CP2 and CP3 read only bars on CT date d; CP3's d-1 is the most recent
complete daily bar (after a booked-forward Monday: the Friday). CP2's buffer is 4 x vendor_tick =
20.00 (4 ticks); all comparisons in integer ticks of vendor_tick 5.00.

Outputs:
- strategy/members/k7/cp1.py, cp2.py, cp3.py, and strategy/members/k7/_port_common.py if you share
  helpers (name any other file you add). Each module: a member class with `name`, `trading_windows`
  (spec S0.12) and `on_minute`, and a zero-argument factory `make_mbt`. Do not write
  strategy/members/k7/__init__.py (it exists, 0 bytes, and must stay empty) and do not write any file
  whose name starts with _calendar, expiry, rev2h, montrend or _event (coder B's).
- tests/test_k7_members_ports.py (split into tests/test_k7_members_ports_*.py if large). Pin every
  rule with synthetic bars: signal and entry/exit times, a missing signal or entry bar (no trade), a
  missing exit bar (first later bar), the instrument guard, zero signal, CP2's range, buffer 20.00
  exactly (19.99 beyond does not trigger; ties), the first-qualifying-bar-uses-the-day rule, the
  75-present-bar exit count, no entry from 15:00, CP3's CLV cuts (0.8 and 0.2 inclusive), range 0, the
  complete-day rules and warm-up, the early-halt exclusion, a Sunday 17:00 open for a Monday (both
  before 2026-05-29 and after, with weekend bars present that must not be read), and a booked-forward
  trade date spanning two CT dates. Every test must fail on a mutant of the rule it pins: for each
  literal and comparison, run the mutant (change it, run the test, restore) and list the mutants and
  the tests that killed them in your report. Also run the freeze static check on your files
  (screening.stage_e_freeze: check_cluster_sources or its per-file check) and the template's tests.
- reports/stage_e6_coder_A.md: files, what each test pins, the mutant table, the command lines and
  results, any question you raised.

Run tests with `uv run pytest -q <your test files> tests/test_stage_e_template*.py` (find the template
test by grep) with PYTHONPYCACHEPREFIX unset (E.3 found three bytecode tests fail with it set); run any
python script with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0f52aad4-207e-43da-84df-b6a0ead28371/scratchpad/.
Do not run the full suite (the lead does). Keep command output short (-q, tail).

Ambiguity: if the spec leaves any detail open, or two readings could change a trade, STOP and report
the question to the lead (return early with the question); do not choose. Boundaries: no bar file is
opened and no bar loader is called; no edit outside the files named above; no change to the harness
(screening/, rules/, data/, strategy/stage_e/) or to any other cluster; no commit; no workers.

Return: the paths, a summary of at most 200 words, and anything you could not finish.
