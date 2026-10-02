# Brief: MemberAuditor-K8-FableXHigh, part 1 (Stage E.9, K8, Task 3: fidelity audit)

Worker file: worker-xhigh. Model: fable. Effort: xhigh. You wrote none of the code, the specs or the tests.
Written by the Stage E.9 lead, 2026-10-01. Times in PDT.

## Objective (one)

For each of K8's three coded members (4 declared trials: K8-flight-01 H30 MGC and HEOD MGC, signal leg MES;
K8-oilcad-01 6C, signal leg MCL; K8-wkndbtc-01 MNQ, signal leg MBT), check that the module implements its
frozen catalog entry and nothing more, and that each of the lead's readings (specs section 6: K8-L-01..
K8-L-17 and the adopted earlier readings; section 7: the Task 1b rulings) is the narrowest the frozen text
allows or is fixed by a cited reference. Recompute every literal table from its source. Report findings.
You do not fix code.

## Inputs (read by section, never whole large files)

- The frozen entries: reports/stage_e0_catalog_K8.md: the banner (lines 1-7), the header and C1-C15 (lines
  72-249, every bracketed note), the three member sections (K8-flight-01 252-371, K8-oilcad-01 373-488,
  K8-wkndbtc-01 490-608), section 5 (829-845) and section 6 (848-901). docs/DECISIONS.md V16 (lines 310-321,
  the user's K8 rules). docs/STAGE_E_DESIGN.md D4 lines 274-280, D6's session rows 389-402, D9 lines
  478-616 (D9.5a lines 516-521).
- The lead's specs: reports/stage_e9_member_specs.md (all of it).
- The stage prompt's Task 2 and Task 3 lists: docs/prompts/STAGE_E.9.md (grep "TASK 2" and "TASK 3").
- The code: strategy/members/k8/*.py. The tests: tests/test_k8_members*.py. The coders' reports:
  reports/stage_e9_coder_A.md (tables, flight) and reports/stage_e9_coder_B.md (oilcad, wkndbtc), and the
  table generator reports/stage_e9_briefs/gen_k8_tables.py.
- The contract and the engine's handling of signal legs: strategy/stage_e/_template.py,
  strategy/stage_e/interface.py; screening/stage_e_engine.py (iter_minutes, the shared UTC grid, the order
  of fills and the member call, the refusal engine_leg_missing_bar), screening/stage_e_rules.py
  (call_member, account_view, structural_refusal and _opening_refusal: the window and the union blackout,
  admit_fill: the D9.5a guard), screening/stage_e_align.py (member_window: intersection of legs' dates
  less the union of their roll blackouts, UR-1; leg_coverage on the declared intervals).
- The frozen sources of the tables: EC-CAL (data.group_session.load_group_calendar for equity, crypto,
  metals, energy, fx; data/calendars/*.py; rules.sessions.flatten_time_ct), the frozen release calendar
  reports/stage_e2b_release_calendar.json, and the Task 1b check reports/stage_e9_release_check.json and
  .md (saved pages under reports/stage_e9_briefs/pages/). Read JSON with short scripts that print counts
  and diffs only.
- The freeze declarations the lead will write: reports/stage_e9_briefs/write_k8_freeze.py (run it with
  `PYTHONPATH=. ... --dry-run` only).

## What to check, for every member

1. Every literal and clock time: flight's blocks (77, t_k 08:35..14:55, bars t_k - 1 and t_k - 6), 0.5%
   (m = ceil(n/200)), 20 reference dates, n >= 1,200, r_k < 0, H30 (intent T_e + 29, cap 15:04), HEOD
   (15:04); oilcad's T (65 times 08:05..13:25), bars t - 1 and t - 6, 20 dates, n >= 1,000, ddof 1,
   |z| >= 2.0, exit intent T_e + 14; wkndbtc's Friday 14:59, Sunday 17:59, entry fill 18:00, exit intent
   14:58. q_c from the frozen tables.
2. Direction: flight BUYS MGC; oilcad BUYS 6C when z > 0 (crude up) and SELLS when z < 0; wkndbtc BUYS MNQ
   when G > 0 and SELLS when G < 0.
3. Exits and flattens: times, T_e as the actual fill minute (K8-L-07), "first later bar" when an exit bar is
   missing, the resend of a refused exit, no exit after an engine closure; nothing past the last fill
   (15:05, 13:40, 14:59).
4. Sizing: q_c (1), never a literal; exits close the whole position; no intent ever on a signal leg.
5. The tables: recompute the five group full-session sets (no early halt and engine F 15:08 for every K8
   root of the group), FLIGHT_DATES, OILCAD_DATES, WKNDBTC_DATES and GUARD_INSTANTS (every frozen calendar
   row 2019-05-01..2026-06-19 including the root, plus the section 7 corrections) in your own code; every
   difference listed, and the comparison with the earlier clusters' frozen sets.
6. Availability and cross-leg timing (the prompt's K8 items): no signal-leg bar is read before it has
   closed on the UTC minute grid (a bar is usable only at view time = its open + 60 s, and only the view's
   own bars or earlier ones are used); a missing or late signal bar blocks the trade instead of being
   forward-filled (a signal bar that arrives at a later minute is never used as the earlier minute's bar);
   the traded leg's fill comes strictly after the signal is known (intent emitted on the view at t - 1,
   fill at the open of the traded bar at t or later); no hindsight field; the release instants and
   calendars are known before d.
7. Trade dates: bars identified by CT date and clock per leg; wkndbtc's Friday (d - 3) and Sunday (d - 1)
   bars, both regimes of MBT (the weekend booked to Monday from 2026-06-01), holiday Mondays and the
   Mondays after Good Friday or a Friday early halt.
8. C5's exclusions: every leg's group calendar (K8-L-03); the reference dates and warm-up (K8-L-04,
   K4-L-09); the missing-bar and instrument clauses per computation (K8-L-05, K8-L-06); and that the union
   of the legs' roll blackouts is applied: by the engine and runner (member_window and
   engine_roll_blackout over every leg, signal legs included), and nowhere contradicted by a member.
9. C6: the skip set equals the engine's D9.5a set for the traded root (K8-L-08); a skipped flight trigger
   does not use the day's entry; oilcad's 09:30 on a standard WPSR date is skipped and 09:35 is not;
   exits are not skipped. Check against the engine's admit_fill on synthetic bars that no K8 entry is ever
   deferred by D9.5a in a case the member could know.
10. The flatten and the D9 floor: nothing works against the engine's F, entry cap, 2-minute rule, D11.5's
    signal-leg refusal or D9.7's entry refusal and forced exit; behaviour after an engine closure.
    trading_windows match specs S0.12, and the coverage check on every leg could not fail for a reason
    other than missing bars (for example an interval outside the leg's session on every date).
11. Nothing more: no filter, guard, re-entry, size rule or state that the entry does not state, except the
    narrowings the specs name, each checked in item 13.
12. The factories, names and legs match specs S0.2 and the freeze script's declarations (4, ordinals 1-4,
    traded leg first). Every file passes screening.stage_e_freeze.check_member_source, and
    strategy/members/k8/__init__.py is 0 bytes.
13. The tests pin the cases the stage prompt names (entry and exit times, the event window, the flatten, a
    missing bar at a decision time, a signal bar from the other leg arriving late or missing, a roll date
    on the signal leg only, a guarded entry skipped under C6, the Friday and Sunday clock points), and they
    would fail if the rule were wrong. Run your own mutants (at least one per literal, time, comparison
    and direction; change, run the tests, restore). Never modify a file under strategy/ or tests/ (the
    lead's gate suite may be running on them): run mutants by monkeypatching in your own scripts, or on
    copies of ONLY the files you mutate, under reports/stage_e9_briefs/audit_k8/. Never copy the
    repository, data/, .venv or .git anywhere (E.8 incident: /tmp is a RAM-backed tmpfs). Name any test
    that passes vacuously and any mutant that survives. A rule without a failing mutant test is a finding.
14. Each lead reading (K8-L-01..K8-L-17 and section 7): the narrowest the frozen text allows, or fixed by a
    cited reference? Where you disagree, say which reading you would take and why. Rule in particular on:
    K8-L-03 ("equity-and-crypto" as both calendars), K8-L-04 (reference dates include roll-blackout dates),
    K8-L-06 (flight: a missing entry bar ends the day; oilcad: per decision), K8-L-07 (T_e actual),
    K8-L-08 (C6's set = the engine's D9.5a set), K8-L-09 (exact Fraction for flight, float stdev for
    oilcad), K8-L-11 (flat = no position and no pending order), K8-L-12 (wkndbtc's dates and the MBT
    roll between Friday and Sunday), and K8-L-15 (section 6 settled by V16 and the frozen text).

You may run the members on synthetic bars through the real engine (the canary kit in
tests/_stage_e_canary_kit.py, or run_engine as the member tests do), with your own scripts under
reports/stage_e9_briefs/audit_k8/. Run test files with `nice -n 10 uv run pytest -q <file>` without
PYTHONPYCACHEPREFIX; run scripts with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/20d17daf-bbde-4768-93fa-814f35cbb398/scratchpad/auditor/.

## Output

reports/stage_e9_member_audit.md, "Part 1: fidelity audit (Task 3)". Include the time you started and ended
(PDT) and the files' sha256 as you audited them; per member a checklist table (items 1-13) with a verdict per
item and file:line; a section on the readings (item 14), one line per reading; the table recomputation
(item 5) with counts and every difference; the mutant table; and a findings list. Grade each finding BLOCKING
(the module would implement something other than the frozen entry, or leak), SHOULD FIX (a defect that could
change a trade in a case not yet seen, or a test that does not pin what it claims), or NOTE, with file:line,
what is wrong, and the smallest fix inside the frozen entry. Leave a heading "Part 2: recomputation (Task 6)"
with nothing under it. The lead will resume you for it. If the harness refuses the write, return the full
report text in your final message.
Return to the lead: the report path, a summary of at most 200 words (counts by grade, each BLOCKING one named),
and anything you could not finish.

## Boundaries

- Read-only on the repository except your report and your own scripts under reports/stage_e9_briefs/audit_k8/.
  No edits to code, tests, specs, frozen files or manifests. No git changes.
- Synthetic bars only: never read a real bar file (data/processed*, parquet), never run
  screening.stage_e_runner, never call write_cluster_freeze. No web, no Databento, no TopstepX, no
  REGISTRATION.md. Do not spawn workers.
- Read files by section and keep command output short (CLAUDE.md context hygiene).
