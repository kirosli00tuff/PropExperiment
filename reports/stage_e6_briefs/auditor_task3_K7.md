# Brief: MemberAuditor-K7-FableXHigh, part 1 (Stage E.6, K7, Task 3: fidelity audit)

Worker file: worker-xhigh. Model: fable. Effort: xhigh. You wrote none of the code, the specs or the tests.
Written by the Stage E.6 lead, 2026-09-27. Times in PDT.

## Objective (one)

For each of K7's six coded members (6 declared trials, all on MBT), check that the module implements its frozen
catalog entry and nothing more, and that each of the lead's readings (specs section 8: the adopted E.3, K4 and K3
readings and K7-L-01..K7-L-12; section 9: the Task 1b rulings) is the narrowest the frozen text allows or is fixed by
a cited reference. Recompute every literal table from its source. Report findings. You do not fix code.

## Inputs (read by section, never whole large files)

- The frozen entries: reports/stage_e0_catalog_K7.md: the banner (lines 1-7), the header and C1-C14 (lines 85-243,
  every bracketed note), the six member sections (K7-cp1-01 249-312, K7-cp2-01 314-370, K7-cp3-01 372-418,
  K7-expiry-01 420-516, K7-rev2h-01 518-593, K7-montrend-01 595-694) and section 7 (lines 944-1026).
  docs/STAGE_E_DESIGN.md D6 lines 348-411 and D9 lines 478-614.
- The lead's specs: reports/stage_e6_member_specs.md (all of it).
- The code: strategy/members/k7/*.py. The tests: tests/test_k7_members*.py. The coders' reports:
  reports/stage_e6_coder_A.md (ports) and reports/stage_e6_coder_B.md (expiry, rev2h, montrend, _calendar), and
  the table generator reports/stage_e6_briefs/gen_k7_calendar.py.
- The contract: strategy/stage_e/_template.py, strategy/stage_e/interface.py, and how the engine calls a member
  (screening/stage_e_engine.py; screening/stage_e_rules.py call_member and account_view).
- The MES references the ports cite: strategy/research/h_daily_bar/_mechanics.py (docstring) and
  h6_prior_close_location.py; strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py lines
  135-182. The audited K4 ports (strategy/members/k4/cp1.py, cp2.py, cp3.py) share the rule body; the K7 ports should
  differ in roots, names and the CT-date handling of K7-L-01 only.
- The frozen sources of the tables: EC-CAL crypto (data.group_session.load_group_calendar("crypto"); data/calendars/crypto.py
  BOOKED_FORWARD, WEEKEND_TO_NEXT_TRADE_DATE_FROM), the engine's session rules (rules.sessions.flatten_time_ct), the two
  Databento condition files under data/vendor/databento/condition/ with data/build_bars.py's mapping (lines 685-687, 728)
  and reports/stage_e2a_bars.json products/MBT degraded, the England-and-Wales list in reports/stage_e4c_release_check.json,
  and the Task 1b check reports/stage_e6_release_check.json and .md (saved pages under reports/stage_e6_briefs/pages/).
  Read JSON with short scripts that print counts and diffs only.
- The freeze declarations the lead will write: reports/stage_e6_briefs/write_k7_freeze.py (run it with
  `PYTHONPATH=. ... --dry-run` only).

## What to check, for every member

1. Every literal and clock time: O 08:30, C 15:00 (from the frozen tables); CP1's 17:00 bar on CT date d-1, 08:59, 14:29,
   14:58; CP2's [08:30, 08:45) range, [08:45, 15:00) eligibility, buffer 20.00 (4 ticks), 75-bar count; CP3's 08:30, 14:59,
   14:58, CLV 0.8 / 0.2; expiry's T_exp - 301 / - 300 / - 2 / - 1 in both T_exp slots (10:00 and 11:00 CT); rev2h's 08:30,
   10:29, 10:30, 12:29, 12:30, 14:29; montrend's 20 decision times (Sunday 18:00-23:00 on CT date d-1, Monday 00:00-13:00),
   t - 1 and t - 60, the 13:59 final exit.
2. Direction: CP1 with the signal; CP2 the break direction; CP3 by CLV; expiry long only; rev2h against sign(r); montrend
   with s_t.
3. Exits and flattens: time, "first bar at or after" when a bar is missing, the resend of a refused exit. CP2: the 75-bar
   count and no C-2 exit. rev2h and montrend: the flatten on the decision - 1 bar and the entry on the decision bar only
   when flat (C2: never one 2q order), hold on an equal target.
4. Sizing: q_c from the frozen table (1), never a literal; exits close the whole position.
5. The tables: recompute CRYPTO_FULL_SESSIONS (with K3-L-11's engine-F condition), VENDOR_DEGRADED and MBTX (the rule,
   the holiday lists, zoneinfo T_exp, and the research-window rows against Task 1b's verdicts and the lead's section 9) in
   your own code; every difference listed.
6. Availability: no input is read before it is available. Each bar is used only after its close. CP3 uses only complete
   bars of earlier trade dates. MBTX and CRYPTO_FULL_SESSIONS are known in advance (contract terms, holiday calendars).
   Rule explicitly on K7-L-03: VENDOR_DEGRADED is the vendor's after-the-fact data-quality list, used only to remove
   trade dates, as C4 requires; say whether it can leak anything into a trade's timing or direction, and whether any
   member reads a hindsight field, a future bar, or the account in a way that leaks the future.
7. K7-L-01 (the program trade date by clock): no member reads a bar outside [d-1 17:00, d 16:00) CT for trade date d, and
   no member identifies a bar by trade_date and clock alone. Check against data/group_session.py lines 20-40 how bars are
   booked on the seven booked-forward holidays and on 24/7 weekends from 2026-06-01, and that the tests cover both.
8. The C4 exclusions for the three new members (CRYPTO_FULL_SESSIONS, VENDOR_DEGRADED, the instrument guard of K7-L-06,
   the missing-entry-bar rule); Family H's rules for CP3; the ports carry no C4 guard beyond D6's.
9. The flatten and the D9 floor: nothing in a member works against the engine's F, entry cap, 2-minute rule or D9.7's
   forced exit; K7-L-07's behaviour after an engine closure. trading_windows match specs S0.12.
10. Nothing more: no filter, guard, re-entry, size rule or state that the entry does not state.
11. The factories, names and legs match specs S0.2 and the freeze script's declarations (6, ordinals 1-6). Every file
    passes screening.stage_e_freeze.check_member_source, and strategy/members/k7/__init__.py is 0 bytes.
12. The tests pin the cases the stage prompt names (entry and exit times, the event window, the flatten, a missing bar at
    a decision time, the expiry instant, a Sunday session open, a trade-date boundary), and they would fail if the rule
    were wrong. Run your own mutants (at least one per literal, time, comparison and direction; change, run the tests,
    restore). Never modify a file under strategy/ or tests/ (the lead's gate suite may be running on them): run mutants on
    copies outside the repository tree, or by monkeypatching in your own scripts under reports/stage_e6_briefs/audit_k7/. Name any test that passes vacuously and any mutant that survives. The E.4 lesson: a rule
    without a failing mutant test is a finding.
13. Each lead reading (adopted and K7-L-01..K7-L-12, and section 9): the narrowest the frozen text allows, or fixed by a
    cited reference? Where you disagree, say which reading you would take and why. Rule in particular on K7-L-03
    (vendor-degraded table), K7-L-05 (expiry kept and run although every research expiry day is a roll-blackout date,
    E.2a L-11), and K7-L-07.
14. Catalog section 7 as settled (K7-L-12): whether each settlement follows the frozen text and the prompt.

You may run the members on synthetic bars through the real engine (the canary kit in tests/_stage_e_canary_kit.py), with
your own scripts under reports/stage_e6_briefs/audit_k7/. Run test files with `nice -n 10 uv run pytest -q <file>`
without PYTHONPYCACHEPREFIX; run scripts with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0f52aad4-207e-43da-84df-b6a0ead28371/scratchpad/.

## Output

reports/stage_e6_member_audit.md, "Part 1: fidelity audit (Task 3)". Include the time you started and ended (PDT) and the
files' sha256 as you audited them; per member a checklist table (items 1-12) with a verdict per item and file:line; a
section on the readings (items 13-14), one line per reading; the table recomputation (item 5) with counts and every
difference; the mutant table; and a findings list. Grade each finding BLOCKING (the module would implement something other
than the frozen entry, or leak), SHOULD FIX (a defect that could change a trade in a case not yet seen, or a test that does
not pin what it claims), or NOTE, with file:line, what is wrong, and the smallest fix inside the frozen entry.
Leave a heading "Part 2: recomputation (Task 6)" with nothing under it. The lead will resume you for it.
Return to the lead: the report path, a summary of at most 200 words (counts by grade, each BLOCKING one named), and
anything you could not finish.

## Boundaries

- Read-only on the repository except your report and your own scripts under reports/stage_e6_briefs/audit_k7/. No edits
  to code, tests, specs, frozen files or manifests (mutants only on copies or by monkeypatching). No git changes.
- Synthetic bars only: never read a real bar file (data/processed*, parquet), never run screening.stage_e_runner, never
  call write_cluster_freeze. No web, no Databento, no TopstepX, no REGISTRATION.md. Do not spawn workers.
- Read files by section and keep command output short (CLAUDE.md context hygiene).
