# Brief: MemberCoder-B-OpusXHigh (Stage E.9 Task 2, coder B), worker-xhigh on opus

Objective: code K8-oilcad-01 (traded 6C q_c 1, signal leg MCL) and K8-wkndbtc-01 (traded MNQ q_c 1,
signal leg MBT), exactly as reports/stage_e9_member_specs.md states them, with unit tests on synthetic
bars.

Read first (by section): reports/stage_e9_member_specs.md header, section 0, sections 2, 3, 5, 6 and 7
(the readings and rulings govern; do not re-read the catalog except to check a line the spec cites:
reports/stage_e0_catalog_K8.md); strategy/stage_e/_template.py; strategy/stage_e/interface.py;
screening/stage_e_freeze.py lines 1-90 (ALLOWED_IMPORTS, BANNED_NAMES; a member imports only those
and its own package strategy.members.k8).
Precedents to adapt (audited and frozen): a multi-leg member strategy/members/k6/crushgap.py and
tests/test_k6_members_crushgap.py (engine-level tests with run_engine on synthetic frames, as
tests/test_stage_e_alignment.py lines 140-150 does with an MES signal leg); a rolling-reference,
multi-decision member strategy/members/k4/ovr.py (20 reference dates, warm-up K4-L-09, per-decision
guard K4-L-14) and its tests; MBT's two regimes and CT-date bar selection: strategy/members/k7/montrend.py
(Sunday bars) and its tests (K7-L-01).

The tables: strategy/members/k8/_calendar.py (FX/ENERGY/EQUITY/CRYPTO full sessions, OILCAD_DATES,
WKNDBTC_DATES, a previous-dates helper) and strategy/members/k8/_releases.py (GUARD_INSTANTS, in_guard)
are written by coder A FIRST (spec S0.11). Write your modules against that interface; run your tests
once those files exist (check for them; do not write them yourself; if they are not there within about
20 minutes of your start, report it to the lead).

K8-oilcad-01 (spec section 2, readings K8-L-04..K8-L-11):
- strategy/members/k8/oilcad.py: factory make_6c, name "K8-oilcad-01 6C", legs (LegSpec("6C", True),
  LegSpec("MCL", False)), trading_windows per S0.12, q_c from load_frozen_tables().vehicles["6C"].q_c.
  r_t from integer ticks as a float; s(d) = statistics.stdev over the reference values of the 20 most
  recent OILCAD_DATES before d (warm-up K4-L-09; n >= 1,000; s = 0 no trade); z = r_t / s; |z| >= 2.0;
  entry only when flat (no position, no pending order), C6 skip with in_guard("6C", fill minute),
  per-decision missing-bar rule; exit at T_e + 14 (T_e from the account, K8-L-07), resent if refused.
- tests/test_k8_members_oilcad.py: decision clock (08:05..13:25, 65 a day; no decision at 08:00 or
  13:30); r_t's bars (t - 1 and t - 6: 08:04 and 07:59 for t = 08:05); the instrument guard per
  computation (an MCL roll inside a block: no entry at t, later decisions proceed); c6 > 0; s(d) uses
  ddof 1 (a hand-computed example where ddof 0 would flip the decision); n < 1,000 no trade, n = 1,000
  trades; warm-up (20th and 21st eligible dates); reference dates from OILCAD_DATES; |z| = 2.0 boundary
  (construct values so |z| is exactly representable at 2.0 if possible, else just above and just
  below); sign (z > 0 buys 6C, z < 0 sells); the C6 skip (09:30 on a standard WPSR date is skipped and
  09:35 is not; 13:00 on an FOMC date skipped; 09:30 on a non-WPSR date not skipped); flat-only entries
  (no entry while a position or a pending order exists; the exit intent at T_e + 14 and the decision
  t_e + 15 on the same view: no entry; the next entry possible at t_e + 20); a missing 6C entry bar
  at t - 1 (no entry at t; the next decision still works); an MCL bar arriving late or missing (never
  forward filled); the exit at T_e + 14 / fill T_e + 15, a missing exit bar (first later present bar);
  T_e later than t when the 6C bar at t is missing; engine closure (flat account, later decisions
  apply); no MCL intent ever; nothing after the 13:40 fill.
K8-wkndbtc-01 (spec section 3, readings K8-L-02, K8-L-03, K8-L-12):
- strategy/members/k8/wkndbtc.py: factory make_mnq, name "K8-wkndbtc-01 MNQ", legs
  (LegSpec("MNQ", True), LegSpec("MBT", False)), trading_windows per S0.12 (MNQ (17:59, 18:01) day -1
  and (14:58, 15:00) day 0; MBT (17:59, 18:00) day -1 and (14:59, 15:00) day 0), q_c from the frozen
  vehicles. Store the MBT Friday 14:59 close and instrument_id by CT date; on the view at Sunday 17:59
  CT with both bars present (MBT and MNQ, trade_date d = Sunday + 1, d a Monday in WKNDBTC_DATES and
  d - 3 in WKNDBTC_DATES), compare in integer ticks; G = 0 no trade; C6 skip with in_guard("MNQ", the
  18:00 fill); exit at Monday 14:58 (fill 14:59), resent if refused.
- tests/test_k8_members_wkndbtc.py: the exact clock points (the Friday 14:59 and Sunday 17:59 MBT bars;
  a 15:00 Friday bar, a 14:58 Friday bar, a 17:58 Sunday bar or a Saturday bar after 2026-05-29 never
  used); one instrument_id across P_F and P_S (a roll between them: no trade); P_F from CT date d - 3
  only (a stale Friday from an earlier week is never used); G > 0 buys, G < 0 sells, G = 0 nothing;
  both regimes (a Monday before and after 2026-06-01, where the weekend MBT bars carry Monday's
  trade_date); exclusions (2025-05-26 holiday Monday; 2025-04-21 after Good Friday 2025-04-18; a
  Monday after a Friday early halt such as 2025-11-28 -> 2025-12-01); a missing MNQ 17:59 bar (no trade);
  a missing MBT bar or one arriving late (no trade, no forward fill); the exit at 14:58 / fill 14:59, a
  missing exit bar (first later bar); a non-Monday never trades; no MBT intent ever.
Engine-level tests for both (run_engine on synthetic two-leg frames, as
tests/test_stage_e_alignment.py): oilcad fills on 6C at the open of t and exits at T_e + 15 with no MCL
position; wkndbtc fills on MNQ at Sunday 18:00 and exits Monday 14:59; the engine refuses an open on a
roll-blackout date of the SIGNAL leg only (pass the blackout to the rules object as the runner would:
this pins V16(a) end to end with the frozen engine). Every test must fail on a mutant of the rule it
pins: for each literal, time and comparison, run the mutant (change it, run the test, restore) and list
the mutants and the tests that killed them in your report. Run the freeze static check on your files.
- reports/stage_e9_coder_B.md: files, what each test pins, the mutant table, the command lines and
  results, any question raised. If the harness refuses that write, put the full report text in your
  final message instead.

Run tests with `uv run pytest -q <your test files> tests/test_stage_e_template.py
tests/test_stage_e_freeze.py` with PYTHONPYCACHEPREFIX unset (three bytecode tests fail with it set);
run any python script with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/20d17daf-bbde-4768-93fa-814f35cbb398/scratchpad/coderB/.
Keep every scratch file under that coderB/ folder (coder A uses coderA/). /tmp is a RAM-backed tmpfs:
never copy the repository, data/, .venv or .git into it; mutate files in place and restore them (keep
a pristine copy of only the file you mutate). Do not run the full suite (the lead does). Keep command
output short (-q, tail). Run CPU-heavy work at nice 10.

Ambiguity: if the spec leaves any detail open, or two readings could change a trade, STOP and report
the question to the lead (return early with the question); do not choose. Boundaries: no bar file is
opened and no bar loader is called; no web access; write only the files named above; never write
strategy/members/k8/__init__.py (0 bytes, must stay empty), _calendar.py, _releases.py, _common.py,
flight.py or tests/test_k8_members_tables*.py / _flight*.py (coder A's); no change to the harness
(screening/, rules/, data/, strategy/stage_e/) or to any other cluster; no commit; no workers.

Return: the paths, a summary of at most 200 words, and anything you could not finish.
