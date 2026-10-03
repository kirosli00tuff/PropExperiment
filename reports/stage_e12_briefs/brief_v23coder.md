# Brief: V23Coder-OpusXHigh (worker-xhigh, opus). Stage E.12 Task 1 (code)

You are a worker in Stage E.12 (prompt: docs/prompts/STAGE_E.12.md; read SCOPE, GUARDRAILS, Task 1).
Decisions in force: docs/DECISIONS.md V23 (read lines 409-445). The design is
docs/STAGE_E_ML_V2_DESIGN.md (the lead edits it in parallel; do not edit it). Anything below that
needs a judgment on a rule: stop and report it, do not decide it.

## Objective
Make the ml_route_v2 build implement the user's V23 decisions as its DEFAULTS, with tests, so the
lead can freeze it. No market data is read (none exists for v2 yet; read no bar row of any store).

## Changes (cite "V23 item n" in comments)
1. ml_route_v2/constants.py
   - COST_GATE_READING = "gross" (item 1: trade iff |r_hat| > k c; hurdles 1.5c / 2c / 3c). Keep the
     "net" reading selectable by the constant (tests still cover both).
   - C_SIGMA_TAU = 0.167 (item 1: 0.25 sigma = the loosest gross hurdle 1.5c -> 1/6, stated 0.167).
   - Gate 0 constants unchanged (1.5c, t >= 3, Holm 0.05 with family A, top 20%, 30 trades,
     ridge lambda 0.1) but their comments cite V23 item 1.
   - N: replace N_PROGRAM_AT_DRAFT with N_PROGRAM_AT_FREEZE = 198 (E.9's program N, docs/STAGES.md
     line 114 and reports/E.9_RETURN.md line 21; E.10 and E.11 added nothing, V21 and code review
     C-08) and update every reference (configs.ConfigLedger.n_total default, pipeline, tests).
   - Module docstring: no longer "DRAFT"; "frozen by the Stage E.12 freeze manifest
     (reports/stage_e12_ml_v2_freeze.json); V23 applied". Do NOT touch the 150K figures,
     PAYOUT_RESET_DELAY_DATES or anything Topstep-related: the lead sets them from a worker's file.
2. ml_route_v2/decide.py and ml_route_v2/cost_filter.py: confirm both read the constants (no
   literal 0.10 or "net" left anywhere: grep the package and the tests); update docstrings.
3. Release-window rule (V23 item 11, E.12 lead rule P-5), in the portfolio layer
   (ml_route_v2/portfolio.py; follow every path that applies V2.8's portfolio caps: the selection
   metric, the engine-run portfolio, the payout simulator's re-sizing if it applies caps):
   an entry in product p whose FILL lies in [r - 5 min, r + 30 min) of a scheduled release r that
   concerns p (the same frozen release list the targets' event-window cost and D9.5a use for p's
   vehicle) is refused if open lot-equivalents INCLUDING this entry would exceed 0.5 x the XFA
   scaling tier's maximum position size in force (the tier at the prior session's close; 50K tiers
   2 / 3 / 5 lots; half = 1.0 / 1.5 / 2.5). Lot-equivalents as V2.8 (minis 1, micros 0.1, MBT 1).
   Refusals are counted in the portfolio's records with reason "release_window". Tests: an entry at
   r - 5 min refused, at r + 30 min allowed (half-open window), one at r + 29 min refused only
   above half the tier, an unrelated product's release not binding, the count of refusals. Name the
   constants RELEASE_WINDOW_BEFORE_MIN = 5, RELEASE_WINDOW_AFTER_MIN = 30,
   RELEASE_WINDOW_TIER_FRACTION = 0.5 in constants.py.
4. K9-anncday-01 as a v2 signal (V23 item 8; design V2.3). New ml_route_v2/signals/k9.py, remove
   K9-anncday-01 from signals.EXCLUDED, register it in REGISTRY / FAMILY_SIGNALS like the other
   fixed-clock members (read signals/k2.py and signals/_events.py for the pattern):
   - one flag signal `k9_anncday` (kind "flag", not normalized), family "K9-anncday-01", cluster
     "K9" (check what the identifier one-hots and FAMILY tables expect for a cluster without
     vehicles; report if K9 needs a special case), value 1.0 iff the row's trade date is in the
     EC-K9 date set, else 0.0; applicable on every row of the member's vehicles MNQ, M2K, MYM
     (reports/stage_e10_catalog_K9.json members[0].vehicles) and not applicable (0, flag 0) on
     other vehicles' rows and on any trade date inside a span the calendar file marks uncovered;
   - availability: the date set is known from official schedules before the member's entry intent
     at 17:59 CT the evening before d (members[0].decision_time_ct); set avail_ts to that instant
     (or earlier) so assert_causal holds; no released value is read;
   - date sets: the research window from reports/stage_e10_catalog_K9.json members[0].event_dates
     (the union of FOMC, NFP, GDP_first_last, ISM_manufacturing_scheduled,
     inflation_earlier_of_CPI_PPI_by_reference_month); the training window from
     reports/stage_e12_ec_k9_2019_2024.json, which CalendarBuilder writes IN PARALLEL with this
     schema: {"schema": "ec_k9/1", "window": ["2019-05-01", "2024-02-29"], "event_dates": {<the same
     five keys>: ["YYYY-MM-DD", ...]}, "date_set": [sorted union], "uncovered_spans":
     [["YYYY-MM-DD", "YYYY-MM-DD"], ...], "sources": [...]}. Read "date_set" and "uncovered_spans";
     check date_set equals the union of the five lists (else raise). Path constants in k9.py.
     Until the file exists, your tests use a fixture file in that schema; one test (skipped while
     the real file is absent) runs assert_causal on the real file over a synthetic row set.
5. Gate 0 canaries under the new defaults (V23 item 1; tests/test_ml_v2_*gate0* and the leakage
   canaries): pure noise fails; a planted gross edge passes; a planted edge between 1.0c and 1.5c
   fails Gate 0 (bar 1); a planted edge in [1.5c, 2.5c) passes Gate 0 under the gross reading. The
   old semantics "passes Gate 0 and is rejected by the cost gate" belonged to the literal reading:
   keep a test that shows it under COST_GATE_READING="net" via monkeypatch, and add the gross-reading
   counterpart (an edge in [1.5c, 2.5c) is NOT rejected by the k = 1.5 gate when predictions exceed
   1.5c). Update the canary docstrings.
6. Every test of ml_route_v2 passes under the new defaults:
   `PYTHONPYCACHEPREFIX=<fresh dir under /tmp/claude-1000/> nice -n 10 uv run pytest -q
   -p no:cacheprovider tests/test_ml_v2_*.py` (record the exact summary line; at start, record the
   baseline count first). Fix tests whose expectations encoded the literal reading or tau 0.10 by
   making them read the constants or pinning the reading with monkeypatch; never weaken a check.

## Boundaries
- Files you own: ml_route_v2/constants.py, decide.py, cost_filter.py, portfolio.py, gate0.py (avoid
  logic changes there), selection_metric.py and payout_sim.py only for item 3,
  ml_route_v2/signals/ (k9.py, __init__.py), tests/test_ml_v2_* except tests/test_ml_v2_phase1*.py.
- Phase1Coder works IN PARALLEL on ml_route_v2/phase1*.py, panel.py, pipeline.py, clock.py and
  tests/test_ml_v2_phase1*.py: do not edit those. If you must, report it instead.
- Nothing under data/, screening/, rules/, sim/, funnel/, compute/, ml_route/, live/, ops/. No key,
  no network, no commits. nice -n 10; at most 6 BLAS threads.

## Return (at most 200 words) + files
Write reports/stage_e12_briefs/v23coder_report.md: every change with file:line, the baseline and
final pytest summary lines, the canary results, any test changed and why, and anything open.
Return its path, a summary and open items.
