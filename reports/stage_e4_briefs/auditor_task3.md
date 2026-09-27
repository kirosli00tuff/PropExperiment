# Brief: MemberAuditor-K4-FableXHigh, part 1 (Stage E.4 Part 1, Task 3: fidelity audit)

Worker file: worker-xhigh. Model: fable. Effort: xhigh. You wrote none of the code, the specs or the tests,
and you are not the harness reviewer. Written by the Stage E.4 lead, 2026-09-27. Times in PDT.

## Objective (one)

For each of K4's eight coded members (12 declared trials), check that the module implements its frozen
catalog entry and nothing more, and that each of the lead's readings (specs section 10: the E.3 readings
adopted, K4-L-01..K4-L-15) is the narrowest the frozen text allows or is fixed by a cited reference.
Recompute every literal table from its source. Report findings. You do not fix code.

## Inputs (read by section, never whole large files)

- The frozen entries: reports/stage_e0_catalog_K4.md: the banner (lines 1-7), the header and common
  conventions C1-C13 (lines 60-230, with every bracketed note), and the eight member sections (K4-cp1-01
  234-282, K4-cp2-01 283-342, K4-cp3-01 343-383, K4-ngpre-01 384-439, K4-apipre-01 514-587, K4-eiafade-01
  588-659, K4-eiamom-01 660-722, K4-ovr-01 723-793). reports/stage_e1_changes.md lines 29 and 32 (F-4,
  F-7). docs/STAGE_E_DESIGN.md D6 lines 348-411 (the port texts govern the ports) and D9 lines 478-614.
- The lead's specs: reports/stage_e4_member_specs.md (all of it).
- The code: strategy/members/k4/*.py. The tests: tests/test_e4_k4_members*.py. The coders' reports:
  reports/stage_e4_coder_A.md and reports/stage_e4_coder_B.md.
- The contract: strategy/stage_e/_template.py, strategy/stage_e/interface.py, and how the engine calls a
  member (screening/stage_e_engine.py, screening/stage_e_rules.py call_member and account_view).
- The MES references the ports cite: strategy/research/h_daily_bar/_mechanics.py (docstring) and
  h6_prior_close_location.py; strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py
  lines 135-182. E.3's K2 port modules (strategy/members/k2/cp1.py, cp2.py, cp3.py) were audited in E.3
  and may be diffed against K4's for the ports (the rule text is the same; only the clock differs).
- The frozen sources of the literal tables: reports/stage_e2b_release_calendar.json (sha256
  839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8), reports/stage_e4_release_check.json
  (sha256 bb1b10719536f5c5bd35ee1d0f2da96e7bcd1c4750f6eb7f560b39f694537e24; its .md; the saved pages
  under data/vendor/release_pages/e4/ with manifest.jsonl), and the energy calendar through
  data.group_session.load_group_calendar("energy"). Read JSON with short scripts that print counts and
  diffs only.
- The freeze declarations the lead will write: reports/stage_e4_briefs/write_k4_freeze.py (run it with
  `PYTHONPATH=. ... --dry-run` only).

## What to check, for every member

1. Every literal and clock time: decision minutes, fill minutes, exit minutes, offsets from O, C and T,
   the CP2 buffer (MCL 0.04, NG 0.004 = 4 ticks of the exposure's most active contract, R-07), the CLV
   cuts, the hold count, eiafade's 0.005 threshold and 13:13 filter, ovr's five times, 20 dates, 80
   values and deciles.
2. Direction: the side or the signal's sign convention (ngpre always SELL; ovr fades).
3. The exit: its time, and "first bar at or after" behaviour when a bar is missing. For CP2, the 75-bar
   count and that there is no C-2 exit.
4. Sizing: q_c from the frozen table (MCL 4, NG 1), never a literal; exits close the whole position.
5. The event sets and their instants: recompute WPSR, NGS, DROPPED_WPSR, DROPPED_NGS, API_DROPPED_WEEKS,
   FEDERAL_MONDAY_HOLIDAYS, NYSE_NOT_FULL and ENERGY_FULL_SESSIONS in your own code from the sources. Check
   T = the instant in CT, the standard flag, and that the drops equal the release check's non-keep
   verdicts (section 11). Spot-check the release check's evidence for the four drops against the saved
   pages it cites, and say whether each verdict follows C9's drop rules (C lines 160-171).
6. Availability: no input is read before it is available. Each bar is used only after its close. apipre's
   Tuesday bars are read after their close and used on Wednesday; CP3 uses only complete bars of earlier
   trade dates; ovr's reference values come only from earlier trade dates. Every table entry is known
   before its trade date (EIA schedules and exception tables published in advance; the drop rules exist
   for the ones that were not). No member reads a hindsight field, any future bar, or the account in a
   way that leaks the future.
7. The C4 exclusions for the five new members (early halt from the decision bar, the instrument guard,
   the missing-entry-bar rule), C10's non-positive guard where a percent return is computed (eiafade,
   ovr), Family H's rules for CP3; the ports carry no C4 guard beyond D6's.
8. The flatten and the D9 floor: nothing in a member works against the engine's F, entry cap or 2-minute
   rule, or D9.7's forced exit. trading_windows match specs S0.12 (including K4-L-07 for apipre).
9. Nothing more: no filter, guard, re-entry, size rule or state that the entry does not state. No RBOB or
   ULSD trial exists.
10. The factories, names and legs match specs S0.2 and the freeze script's declarations (12, ordinals
    1-12). Every file passes screening.stage_e_freeze.check_member_source.
11. The tests pin the cases the stage prompt names (entry and exit times, the event window, the flatten, a
    missing bar at a decision time, a moved or dropped release, the C10 guard, D9.7's price-limit exit),
    and they would fail if the rule were wrong. Name any test that passes vacuously.
12. Each lead reading (the adopted E.3 readings and K4-L-01..K4-L-15): is it the narrowest reading the
    frozen text allows, or is it fixed by a reference the spec cites? Where you disagree, say which reading
    you would take and why.
13. F-7: K4-ovr-01 carries the same rule text as K5-ovr-01 apart from the clock (reports/stage_e1_changes.md
    line 32). Note anything in ovr.py that is energy-specific beyond the decision clock.

You may run the members on synthetic bars through the real engine (the canary kit in
tests/_stage_e_canary_kit.py), with your own scripts under reports/stage_e4_briefs/audit/. You may also run
the test files (`nice -n 10 uv run pytest -q <file>` without PYTHONPYCACHEPREFIX).

## Output

reports/stage_e4_member_audit.md, "Part 1: fidelity audit (Task 3)". Include:
- the time you started and ended (PDT) and the files' sha256 as you audited them;
- per member, a checklist table (items 1-11), with a verdict per item and file:line;
- a section on the lead's readings (item 12), one line per reading, and item 13;
- the table recomputation (item 5) with counts per table and every difference;
- a findings list. Each finding is graded BLOCKING (the module would implement something other than
  the frozen entry, or leak), SHOULD FIX (a defect that could change a trade in a case not yet seen,
  or a test that does not pin what it claims), or NOTE. Give each finding file:line, what is wrong,
  and the smallest fix inside the frozen entry.
Leave a heading "Part 2: recomputation (Task 6)" with nothing under it. The lead will resume you for it.
Return to the lead: the report path, a summary of at most 200 words (the count of findings by grade and
each BLOCKING one named), and anything you could not finish.

## Boundaries

- Read-only on the repository except your report and your own scripts under reports/stage_e4_briefs/audit/.
  No edits to code, tests, specs, frozen files or manifests. No git changes.
- Synthetic bars only: never read a real bar file (data/processed*, parquet), never run
  screening.stage_e_runner, never call write_cluster_freeze. No web, no Databento, no TopstepX, no
  REGISTRATION.md. Do not spawn workers.
- Read files by section and keep command output short (CLAUDE.md context hygiene).
