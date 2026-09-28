# Brief: MemberAuditor-K1-FableXHigh, part 1 (Stage E.7, K1, Task 3: fidelity audit)

Worker file: worker-xhigh. Model: fable. Effort: xhigh. You wrote none of the code, the specs or the tests.
Written by the Stage E.7 lead, 2026-09-28. Times in PDT.

## Objective (one)

For each of K1's five coded members (11 declared trials: three ports on MNQ, M2K and MYM, K1-vxnband-01 MNQ and
K1-vwap-01 MNQ), check that the module implements its frozen catalog entry and nothing more, and that each of the lead's
readings (specs section 8: the adopted E.3, K4, K3 and K7 readings and K1-L-01..K1-L-16; section 9: the Task 1b rulings)
is the narrowest the frozen text allows or is fixed by a cited reference. Recompute every literal table from its source.
Report findings. You do not fix code.

## Inputs (read by section, never whole large files)

- The frozen entries: reports/stage_e0_catalog_K1.md: the banner (lines 1-7), the header and C1-C12 (lines 78-214, every
  bracketed note), the five member sections (K1-cp1-01 218-275, K1-cp2-01 277-351, K1-cp3-01 353-401, K1-vxnband-01
  403-500, K1-vwap-01 502-593), the ML feature row KF1 (line 725, for K1-L-01 only) and section 7 (lines 933-984).
  docs/STAGE_E_DESIGN.md D5 lines 298-345, D6 lines 348-411 and D9 lines 478-616.
- The lead's specs: reports/stage_e7_member_specs.md (all of it).
- The stage prompt's Task 2 test list: docs/prompts/STAGE_E.7.md (grep "Task 2" and the lines after it).
- The code: strategy/members/k1/*.py. The tests: tests/test_k1_members*.py. The coders' reports:
  reports/stage_e7_coder_A.md (ports) and reports/stage_e7_coder_B.md (vxnband, vwap, _calendar, _vxn), and the table
  generator reports/stage_e7_briefs/gen_k1_tables.py.
- The contract: strategy/stage_e/_template.py, strategy/stage_e/interface.py, and how the engine calls a member and
  processes several intents in one call (screening/stage_e_engine.py ask_member, fill_pending_at_open;
  screening/stage_e_rules.py call_member, gate, account_view).
- The MES references the ports cite: strategy/research/h_daily_bar/_mechanics.py (docstring) and
  h6_prior_close_location.py; strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py lines
  135-182. The audited K7 ports (strategy/members/k7/cp1.py, cp2.py, cp3.py) share the rule body; the K1 ports should
  differ in roots, factories, q_c and ticks only.
- The frozen sources of the tables: EC-CAL equity (data.group_session.load_group_calendar("equity"),
  data/calendars/equity.py), the engine's session rules (rules.sessions.flatten_time_ct), the saved Cboe file
  data/vendor/index_history/vxn/VXN_History.csv with its manifest, and the Task 1b check reports/stage_e7_release_check.json
  and .md (saved pages under reports/stage_e7_briefs/pages/). Read CSV and JSON with short scripts that print counts and
  diffs only.
- The freeze declarations the lead will write: reports/stage_e7_briefs/write_k1_freeze.py (run it with
  `PYTHONPATH=. ... --dry-run` only).

## What to check, for every member

1. Every literal and clock time: O 08:30, C 15:00 (from the frozen tables); CP1's 17:00 bar on CT date d-1, 08:59, 14:29,
   14:58; CP2's [08:30, 08:45) range, [08:45, 15:00) eligibility, buffer 4 x vendor_tick (1.00 / 0.40 / 4), 75-bar count;
   CP3's 08:30, 14:59, 14:58, CLV 0.8 / 0.2; vxnband's 16 / 1600, cuts 20 (strict) and 30 (non-strict), scan [08:30,
   14:29), exit at entry-intent + 30 min, C_prev at 14:59; vwap's TP, [08:30, 14:57) rule window, 20 entries, the hold
   (exit on k+1 or later), the 14:58 final exit.
2. Direction: CP1 with the signal; CP2 the break direction; CP3 by CLV; vxnband fades (sell above U, buy below L); vwap
   with s_t.
3. Exits and flattens: time, "first bar at or after" when a bar is missing, the resend of a refused exit. CP2: the 75-bar
   count and no C-2 exit. vwap: the reversal as two intents on one bar (exit, then entry), their acceptance by the engine,
   the exit-to-flat after the 20th entry, the instrument-change exit.
4. Sizing: q_c from the frozen table (1, 3, 3), never a literal; exits close the whole position.
5. The tables: recompute EQUITY_TRADE_DATES, EQUITY_FULL_SESSIONS (K3-L-11's engine-F condition, three roots) and VXN_CLOSE
   (every row, exact strings, against the saved file's sha256 and the Task 1b verdicts and specs section 9) in your own
   code; every difference listed.
6. Availability: no input is read before it is available. Each bar only after its close. CP3 and vxnband's C_prev use
   only complete bars of earlier trade dates. V for d is the close of an EARLIER calendar date, used from 08:30 CT on d
   (K1-L-01): check that no code path can read V of d itself or of a later date, and whether Cboe's publication time
   (Task 1b item A5) precedes every use. Rule explicitly on K1-L-01 against the stage prompt's "(the catalog KF1 row: from
   08:35 CT on d)". Check that no member reads a hindsight field (vendor_degraded_day, gap flags meant as hindsight), a
   future bar, or the account in a way that leaks the future.
7. Trade dates: no member reads a bar outside [d-1 17:00, d 16:00) CT for trade date d; bars are identified by CT date and
   clock; exchange holidays with an early halt are handled as the specs say (CP1's first bar, CP3's and vxnband's d-1,
   vxnband's V after such a holiday, K1-L-02).
8. The C4 exclusions for the two new members (EQUITY_FULL_SESSIONS, the missing-bar and instrument clauses of K1-L-04 and
   K1-L-07); Family H's rules for CP3 and vxnband's C_prev; the ports carry no C4 guard beyond D6's.
9. The flatten and the D9 floor: nothing in a member works against the engine's F, entry cap, 2-minute rule, D9.12 or
   D9.7's forced exit; behaviour after an engine closure. trading_windows match specs S0.12.
10. Nothing more: no filter, guard, re-entry, size rule or state that the entry does not state.
11. The factories, names and legs match specs S0.2 and the freeze script's declarations (11, ordinals 1-11). Every file
    passes screening.stage_e_freeze.check_member_source, and strategy/members/k1/__init__.py is 0 bytes.
12. The tests pin the cases the stage prompt names (entry and exit times, the event window, the flatten, a missing bar at a
    decision time, the VXN value used only from its availability time, a CPI window), and they would fail if the rule were
    wrong. Run your own mutants (at least one per literal, time, comparison and direction; change, run the tests,
    restore). Never modify a file under strategy/ or tests/ (the lead's gate suite may be running on them): run mutants on
    copies outside the repository tree, or by monkeypatching in your own scripts under reports/stage_e7_briefs/audit_k1/.
    Name any test that passes vacuously and any mutant that survives. The E.4 lesson: a rule without a failing mutant test
    is a finding.
13. Each lead reading (adopted and K1-L-01..K1-L-16, and section 9): the narrowest the frozen text allows, or fixed by a
    cited reference? Where you disagree, say which reading you would take and why. Rule in particular on K1-L-01 (08:30
    against the prompt's 08:35), K1-L-02 (V after early-halt holidays), K1-L-04 (scan ends on a missing bar), K1-L-05
    (exit by clock), K1-L-07 and K1-L-08 (vwap's missing bars and count).
14. Catalog section 7 as settled (K1-L-14): whether each settlement follows the frozen text and the prompt.

You may run the members on synthetic bars through the real engine (the canary kit in tests/_stage_e_canary_kit.py, or
run_engine as the member tests do), with your own scripts under reports/stage_e7_briefs/audit_k1/. Run test files with
`nice -n 10 uv run pytest -q <file>` without PYTHONPYCACHEPREFIX; run scripts with PYTHONPYCACHEPREFIX set to a fresh
directory under /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/99bb7678-38d8-413c-82c8-d103cf2d3163/scratchpad/.

## Output

reports/stage_e7_member_audit.md, "Part 1: fidelity audit (Task 3)". Include the time you started and ended (PDT) and the
files' sha256 as you audited them; per member a checklist table (items 1-12) with a verdict per item and file:line; a
section on the readings (items 13-14), one line per reading; the table recomputation (item 5) with counts and every
difference; the mutant table; and a findings list. Grade each finding BLOCKING (the module would implement something other
than the frozen entry, or leak), SHOULD FIX (a defect that could change a trade in a case not yet seen, or a test that does
not pin what it claims), or NOTE, with file:line, what is wrong, and the smallest fix inside the frozen entry.
Leave a heading "Part 2: recomputation (Task 6)" with nothing under it. The lead will resume you for it.
Return to the lead: the report path, a summary of at most 200 words (counts by grade, each BLOCKING one named), and
anything you could not finish.

## Boundaries

- Read-only on the repository except your report and your own scripts under reports/stage_e7_briefs/audit_k1/. No edits
  to code, tests, specs, frozen files or manifests (mutants only on copies or by monkeypatching). No git changes.
- Synthetic bars only: never read a real bar file (data/processed*, parquet), never run screening.stage_e_runner, never
  call write_cluster_freeze. No web, no Databento, no TopstepX, no REGISTRATION.md. Do not spawn workers.
- Read files by section and keep command output short (CLAUDE.md context hygiene).
