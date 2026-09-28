# Brief: MemberCoder-A-OpusXHigh (Stage E.7 Task 2, coder A), worker-xhigh on opus

Objective: code the three K1 core ports, K1-cp1-01, K1-cp2-01 and K1-cp3-01, each on MNQ (q_c 1), M2K
(q_c 3) and MYM (q_c 3), exactly as reports/stage_e7_member_specs.md states them, with unit tests on
synthetic bars.

Read first (by section): reports/stage_e7_member_specs.md header, section 0, sections 1-3 and section 8
(the readings govern; do not re-read the catalog except to check a line the spec cites:
reports/stage_e0_catalog_K1.md); strategy/stage_e/_template.py; strategy/stage_e/interface.py;
screening/stage_e_freeze.py lines 1-90 (ALLOWED_IMPORTS, BANNED_NAMES; a member imports only those and
its own package strategy.members.k1).
Precedent to adapt (audited and frozen; same D6 text): strategy/members/k7/cp1.py, cp2.py, cp3.py,
_port_common.py and tests/test_k7_members_ports*.py (E.6); strategy/members/k3/cp*.py for one module
with several exposure factories (make_6e, make_6a, ...).

What is new for K1: three exposures per port, factories make_mnq, make_m2k, make_mym, each returning a
member whose name is "<member id> <root>" (spec S0.2); q_c from load_frozen_tables().vehicles[root].q_c
(1, 3, 3), never a literal; vendor ticks 0.25 (MNQ), 0.10 (M2K), 1.00 (MYM) from rules.products;
O 08:30, C 15:00 from load_frozen_tables().day_session_ct[root]. CP2's buffer is 4 x vendor_tick:
1.00, 0.40, 4 index points. The equity calendar has no booked-forward dates: an exchange holiday such
as Memorial Day is its own trade date with an early halt (bars carry early_halt_ct), and the next trade
date's first bar is the holiday's 17:00 CT reopen (spec S0.4, section 3 "d-1").

Outputs:
- strategy/members/k1/cp1.py, cp2.py, cp3.py, and strategy/members/k1/_port_common.py if you share
  helpers (name any other file you add). Each module: a member class with `name`, `trading_windows`
  (spec S0.12) and `on_minute`, and the three factories. Do not write strategy/members/k1/__init__.py
  (it exists, 0 bytes, and must stay empty) and do not write any file whose name starts with
  _calendar, _vxn, vxnband, vwap or _event (coder B's).
- tests/test_k1_members_ports.py (split into tests/test_k1_members_ports_*.py if large). Pin every
  rule with synthetic bars, on each of the three roots where the root matters (q_c, tick, buffer):
  signal and entry/exit times; a missing signal or entry bar (no trade); a missing exit bar (first
  later bar); the instrument guard; zero signal; CP2's range, the buffer exactly at 1.00 / 0.40 / 4
  (a close exactly at OR_high + buffer triggers, one tick less does not), the first-qualifying-bar-
  uses-the-day rule, the 75-present-bar exit count, no entry from 15:00; CP3's CLV cuts (0.8 and 0.2
  inclusive, exact), range 0, the complete-day rules and warm-up, the early-halt exclusion of d and of
  d-1 (a holiday early-halt date is skipped as d-1); a Sunday 17:00 open for a Monday; the CPI window
  (on a CPI date such as 2025-05-13, bars at 07:25-07:35 CT with a strong move produce no intent from
  any port); the event minutes (on an FOMC or ISM date the ports emit exactly what their rule says at
  09:00 and 13:00: they read no release; the engine moves fills). Every test must fail on a mutant of
  the rule it pins: for each literal and comparison, run the mutant (change it, run the test,
  restore) and list the mutants and the tests that killed them in your report. Also run the freeze
  static check on your files (screening.stage_e_freeze check_cluster_sources or its per-file check).
- reports/stage_e7_coder_A.md: files, what each test pins, the mutant table, the command lines and
  results, any question you raised.

Run tests with `uv run pytest -q <your test files> tests/test_stage_e_template.py
tests/test_stage_e_freeze.py` with PYTHONPYCACHEPREFIX unset (three bytecode tests fail with it set);
run any python script with PYTHONPYCACHEPREFIX set to a fresh directory under /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/99bb7678-38d8-413c-82c8-d103cf2d3163/scratchpad/.
Do not run the full suite (the lead does). Keep command output short (-q, tail). Run CPU-heavy work
at nice 10.

Ambiguity: if the spec leaves any detail open, or two readings could change a trade, STOP and report
the question to the lead (return early with the question); do not choose. Boundaries: no bar file is
opened and no bar loader is called; no web access; no edit outside the files named above; no change
to the harness (screening/, rules/, data/, strategy/stage_e/) or to any other cluster; no commit; no
workers.

Return: the paths, a summary of at most 200 words, and anything you could not finish.
