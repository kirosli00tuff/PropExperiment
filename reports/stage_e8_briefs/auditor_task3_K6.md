# Brief: MemberAuditor-K6-FableXHigh, part 1 (Stage E.8, K6, Task 3: fidelity audit)

Worker file: worker-xhigh. Model: fable. Effort: xhigh. You wrote none of the code, the specs or the tests.
Written by the Stage E.8 lead, 2026-10-01. Times in PDT.

## Objective (one)

For each of K6's seven coded members (27 declared trials: three ports on ZC, ZW, ZS, ZM, ZL, HE and LE;
K6-crushgap-01 ZS with signal legs ZM and ZL; K6-limitcont-01 HE and LE; K6-wasdepre-01 ZC and ZS;
K6-wasdepost-01 ZC), check that the module implements its frozen catalog entry and nothing more, and that each
of the lead's readings (specs section 9: the adopted E.3, K4, K3, K7 and K1 readings and K6-L-01..K6-L-18;
section 10: the Task 1b rulings R-1b-1..R-1b-6) is the narrowest the frozen text allows or is fixed by a cited
reference. Recompute every literal table from its source. Report findings. You do not fix code.

## Inputs (read by section, never whole large files)

- The frozen entries: reports/stage_e0_catalog_K6.md: the banner (lines 1-7), the header and C1-C13 (lines
  55-231, every bracketed note), the seven member sections (K6-cp1-01 235-286, K6-cp2-01 288-334, K6-cp3-01
  336-378, K6-crushgap-01 380-494, K6-limitcont-01 496-594, K6-wasdepre-01 596-680, K6-wasdepost-01
  682-743) and section 7 (lines 1074-1164). The E.0 lead's 01:52 rulings on K6's questions:
  reports/stage_e0_STATE.md line 70. docs/STAGE_E_DESIGN.md D5 lines 298-345, D6 lines 348-411 and D9 lines
  478-616 (D9.3 line 497, D9.7 lines 531-551).
- The lead's specs: reports/stage_e8_member_specs.md (all of it).
- The stage prompt's Task 2 test list: docs/prompts/STAGE_E.8.md (grep "TASK 2" and the lines after it).
- The code: strategy/members/k6/*.py. The tests: tests/test_k6_members*.py. The coders' reports:
  reports/stage_e8_coder_A.md (ports, crushgap) and reports/stage_e8_coder_B.md (limitcont, wasdepre,
  wasdepost, the tables), and the table generator reports/stage_e8_briefs/gen_k6_tables.py.
- The contract: strategy/stage_e/_template.py, strategy/stage_e/interface.py, and how the engine calls a
  member, builds the view for a member with signal legs, and refuses an open when a read leg has no bar
  (screening/stage_e_engine.py ask_member, fill_pending_at_open; screening/stage_e_rules.py call_member,
  gate, account_view, the D9.7 settlement tracker lines 241-273 and prior_settlement lines 329-334).
- The MES references the ports cite: strategy/research/h_daily_bar/_mechanics.py (docstring) and
  h6_prior_close_location.py; strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py
  lines 135-182. The audited K1 ports (strategy/members/k1/cp1.py, cp2.py, cp3.py) share the rule body; the K6
  ports should differ in roots, factories, clocks, ticks and CP1's first bar (K6-L-01, K6-L-02) only.
- The frozen sources of the tables: EC-CAL grains and livestock (data.group_session.load_group_calendar,
  data/calendars/grains.py and livestock.py, rules.sessions), the frozen release calendar
  reports/stage_e2b_release_calendar.json, the frozen limit table and proxy rules/price_limits.py (LIMITS,
  limit_period, SETTLEMENT_WINDOW_CT, settlement_window_ct, settlement_proxy), and the Task 1b check
  reports/stage_e8_release_check.json and .md (saved pages under reports/stage_e8_briefs/pages/). Read JSON
  with short scripts that print counts and diffs only.
- The freeze declarations the lead will write: reports/stage_e8_briefs/write_k6_freeze.py (run it with
  `PYTHONPATH=. ... --dry-run` only).

## What to check, for every member

1. Every literal and clock time: O 08:30 and C 13:15 (grains) / 13:00 (livestock) from the frozen tables;
   CP1's first bar (grains: the earliest bar of d at or after 19:00 CT on the calendar day before d;
   livestock: the 08:30 bar), 08:59, the entry at C-31 (12:44 / 12:29), the exit at C-2 (13:13 / 12:58);
   CP2's [08:30, 08:45) range, [08:45, C) eligibility, buffer 4 x vendor_tick (1.00, 0.40, 0.04, 0.100),
   75-bar count; CP3's 08:30, C-1 (13:14 / 12:59), C-2, CLV 0.8 / 0.2; crushgap's 13:14 and 08:30 bars,
   weights 0.022 and 11, the unit conversion, filter 0.02 USD/bu; limitcont's settlement window, limits,
   08:44 entry, 12:58 exit; wasdepre's 08:30, 10:29, 11:14; wasdepost's 10:59, 11:14, 13:13.
2. Direction: CP1 with the signal; CP2 the break direction; CP3 by CLV; crushgap SELLS ZS after a GPM gap
   down (G <= -0.02) and BUYS after a gap up (C lines 445-448); limitcont buys after a limit-up close;
   wasdepre and wasdepost with the sign of Dr and R.
3. Exits and flattens: time, "first bar at or after" when a bar is missing, wasdepre's exit on the bar at
   11:14 or the first later bar, the resend of a refused exit, no exit after an engine closure. CP2: the
   75-bar count and no C-2 exit.
4. Sizing: q_c from the frozen table (1 for every root), never a literal; exits close the whole position;
   crushgap never sends an intent on ZM or ZL.
5. The tables: recompute GRAIN_TRADE_DATES, LIVESTOCK_TRADE_DATES, GRAIN_FULL_SESSIONS,
   LIVESTOCK_FULL_SESSIONS (K3-L-11's engine-F condition, every root of the group), LIVESTOCK_EARLY_HALT_CT,
   WASDE_DATES (every 12:00 ET WASDE row of the frozen calendar 2019-05-01..2026-06-19; DROPPED_WASDE empty by
   R-1b-1), LIMIT_PERIODS (HE and LE against LIMITS and limit_period on every livestock trade date, in vendor
   ticks) and DROPPED_LIMIT_DATES (the 14 LE trade dates 2026-06-01..06-18 by R-1b-2) in your own code; every
   difference listed. Check R-1b-2's quote against the saved CME page in reports/stage_e8_briefs/pages/.
6. Availability: no input is read before it is available. Each bar only after its close. CP3 uses only
   complete bars of earlier trade dates. crushgap's d-1 closes and limitcont's S(d-1), S(d-2), S(d-3) come
   from earlier trade dates only, and limitcont's proxy is the same number the engine's D9.7 uses (compare the
   member's function with rules.price_limits on synthetic bars, including the fallback and an early-halt day).
   No member reads a hindsight field (vendor_degraded_day), a future bar, or the account in a way that leaks
   the future. The WASDE dates are known before d.
7. Trade dates: bars are identified by CT date and clock; the grain evening session (19:00 CT on the calendar
   day before d) belongs to d; late-open grain dates (2025-11-28, 2025-12-26, 2026-01-02) and early-halt dates
   are handled as the specs say (CP1's first bar, CP3's d-1, crushgap's d-1, limitcont's d-1..d-3).
8. The C4 exclusions for the four new members (the full-session tables, the missing-bar and instrument clauses,
   per leg for crushgap); Family H's rules for CP3; the ports carry no C4 guard beyond D6's.
9. The flatten and the D9 floor: nothing in a member works against the engine's F, entry cap, 2-minute rule,
   D11.5's signal-leg refusal or D9.7's entry refusal and forced exit; behaviour after an engine closure.
   trading_windows match specs S0.12 (and the coverage check could not fail for a reason other than missing
   bars, for example a grain interval on day -1 for a Monday).
10. Nothing more: no filter, guard, re-entry, size rule or state that the entry does not state, except the
    narrowings the specs name (K6-L-07's d-2 guard, R-1b-2's dropped dates), each checked in item 13.
11. The factories, names and legs match specs S0.2 and the freeze script's declarations (27, ordinals 1-27;
    crushgap's legs (ZS traded, ZM and ZL signal)). Every file passes
    screening.stage_e_freeze.check_member_source, and strategy/members/k6/__init__.py is 0 bytes.
12. The tests pin the cases the stage prompt names (entry and exit times, the event window, the flatten, a
    missing bar at a decision time, a moved or dropped release, a limit close, D9.7's limit-proximity exit), and
    they would fail if the rule were wrong. Run your own mutants (at least one per literal, time, comparison
    and direction; change, run the tests, restore). Never modify a file under strategy/ or tests/ (the lead's
    gate suite may be running on them): run mutants on copies outside the repository tree, or by
    monkeypatching in your own scripts under reports/stage_e8_briefs/audit_k6/. Name any test that passes
    vacuously and any mutant that survives. The E.4 lesson: a rule without a failing mutant test is a finding.
13. Each lead reading (adopted and K6-L-01..K6-L-18, and section 10): the narrowest the frozen text allows, or
    fixed by a cited reference? Where you disagree, say which reading you would take and why. Rule in
    particular on: K6-L-01 (grain CP1's "first bar at or after", and the late-open dates, against E.3-L-05's
    exact-bar reading); K6-L-06 (settlements by the D9.7 proxy: does the 01:52 ruling and D9.7 make the proxy
    the frozen input for K6-limitcont-01, or is the member "unimplementable as frozen"?); K6-L-07 (initial
    limit plus the d-2 guard, against the entry's "expanded where in force"); K6-L-08 (exact equality; no
    rounding); R-1b-2 (drop the LE dates rather than use CME's $0.0850); K6-L-03 (GPM units).
14. Catalog section 7 as settled (K6-L-16): whether each settlement follows the frozen text and the prompt.

You may run the members on synthetic bars through the real engine (the canary kit in
tests/_stage_e_canary_kit.py, or run_engine as the member tests do), with your own scripts under
reports/stage_e8_briefs/audit_k6/. Run test files with `nice -n 10 uv run pytest -q <file>` without
PYTHONPYCACHEPREFIX; run scripts with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/94d6572b-fdf2-4814-9116-60c2521d80a0/scratchpad/auditor/.

## Output

reports/stage_e8_member_audit.md, "Part 1: fidelity audit (Task 3)". Include the time you started and ended
(PDT) and the files' sha256 as you audited them; per member a checklist table (items 1-12) with a verdict per
item and file:line; a section on the readings (items 13-14), one line per reading; the table recomputation
(item 5) with counts and every difference; the mutant table; and a findings list. Grade each finding BLOCKING
(the module would implement something other than the frozen entry, or leak), SHOULD FIX (a defect that could
change a trade in a case not yet seen, or a test that does not pin what it claims), or NOTE, with file:line,
what is wrong, and the smallest fix inside the frozen entry. Leave a heading "Part 2: recomputation (Task 6)"
with nothing under it. The lead will resume you for it. If the harness refuses the write, return the full
report text in your final message.
Return to the lead: the report path, a summary of at most 200 words (counts by grade, each BLOCKING one named),
and anything you could not finish.

## Boundaries

- Read-only on the repository except your report and your own scripts under reports/stage_e8_briefs/audit_k6/.
  No edits to code, tests, specs, frozen files or manifests (mutants only on copies or by monkeypatching). No
  git changes.
- Synthetic bars only: never read a real bar file (data/processed*, parquet), never run
  screening.stage_e_runner, never call write_cluster_freeze. No web, no Databento, no TopstepX, no
  REGISTRATION.md. Do not spawn workers.
- Read files by section and keep command output short (CLAUDE.md context hygiene).
