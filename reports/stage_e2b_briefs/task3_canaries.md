# Brief: CanaryCoder-OpusXHigh (Stage E.2b Task 3; worker-xhigh on opus)

Objective: leakage canaries (design D11.9) run through the generalized Stage E runner for one synthetic product of every
group, a cross-product canary, and the ML rule wrapper's canary. Each canary must FAIL LOUDLY when its leak is planted and
PASS when it is not.

Read: reports/stage_e2b_briefs/00_common.md (binding); tests/test_leakage_canaries.py and sim/leakage_canaries.py (the
existing canaries; do not edit either); the runner report reports/stage_e2b_task1_runner_worker.md (section 0 interfaces;
section 8: "use run_engine, StageERules, product_bar_iterator and tests/_stage_e_synthetic.product_frame"); the ML reports
reports/stage_e2b_task2_ml_worker.md (the rule wrapper) and, when it exists, reports/stage_e2b_g4_mltest_worker.md
(ml_route/stage_e_adapter.py, the multi-leg adapter on the Stage E engine, being built now by MLTestCoder).
Groups: equity, rates, FX, energy, metals, grains, livestock, crypto (data/calendars/).

Build tests/test_stage_e_canaries.py (and a helper module under tests/ if needed):
- per group, one synthetic product: (1) planted future bars (a member that peeks ahead must be caught; an honest member
  unaffected by future bars), (2) planted settlement values (a settlement or release value visible before its
  availability time must be caught), (3) a planted bar inside a scheduled closure (the runner must not trade on it and
  must flag or refuse it).
- cross-product: a planted future bar in one leg must not change the other leg's decisions (and a leaking member that
  reads it must be caught).
- the ML rule wrapper's canary through the Stage E engine (via MLTestCoder's adapter; do this part last; if the adapter
  is not there when everything else is done, run it through the existing engine as M7.7 does and report the gap).
- for each canary, a paired test proving it fails when the leak is planted (a canary that cannot be made to fail on a
  planted leak is a BLOCKING finding: stop and report it to the lead).
Every existing canary and runner test passes unchanged (run tests/test_leakage_canaries.py, tests/test_stage_e_*.py).
Ownership: your new test files only. If the runner needs a change to make a canary possible, report it; do not edit it.
Report: reports/stage_e2b_task3_canaries_worker.md. Reply with path, summary <= 200 words, anything unfinished.
