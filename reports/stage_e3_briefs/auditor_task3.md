# Brief: MemberAuditor-FableXHigh, part 1 (Stage E.3, Task 3: fidelity audit)

Worker file: worker-xhigh. Model: fable. Effort: xhigh. You wrote none of the code, the specs or the tests.
Written by the Stage E.3 lead, 2026-09-27.

## Objective (one)

For each of K2's eight coded members (44 declared trials), check that the module implements its frozen
catalog entry and nothing more, and that each of the lead's readings (specs section 10, L-01..L-22) is the
narrowest the frozen text allows. Report findings. You do not fix code.

## Inputs (read by section, never whole large files)

- The frozen entries: reports/stage_e0_catalog_K2.md: the header and common conventions C1-C10
  (lines 27-131) and the eight member sections (K2-cp1-01 137-181, K2-cp2-01 183-227, K2-cp3-01
  229-266, K2-aucpre-01 268-349, K2-aucpost-01 351-403, K2-fomcpost-01 405-463, K2-predrift-01
  465-534, K2-monthend-01 536-592), with every bracketed E.0, E.1 or E.2a note. docs/STAGE_E_DESIGN.md
  D6 lines 348-411 (the port texts govern the ports) and D9 lines 478-614.
- The lead's specs: reports/stage_e3_member_specs.md (all of it).
- The code: strategy/members/k2/*.py. The tests: tests/test_e3_k2_members.py and
  tests/test_e3_k2_members_events.py. The coders' reports: reports/stage_e3_coder_A.md and
  reports/stage_e3_coder_B.md.
- The contract: strategy/stage_e/_template.py, strategy/stage_e/interface.py, and how the engine calls a
  member (screening/stage_e_engine.py, screening/stage_e_rules.py call_member and account_view).
- The MES references the ports cite: strategy/research/h_daily_bar/_mechanics.py (docstring) and
  h6_prior_close_location.py; strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py
  lines 135-182; strategy/research/f_data_native/_stylized_facts.py lines 294-312.
- The frozen sources of the literal tables: reports/stage_e2b_release_calendar.json (sha256
  839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8; read with short scripts that print
  counts and diffs only) and the rates calendar through data.group_session.load_group_calendar("rates").
  The C9 XML check: reports/stage_e3_auction_xml_check.md and .json.
- The freeze declarations the lead will write: reports/stage_e3_briefs/write_k2_freeze.py (run it with
  `--dry-run` only).

## What to check, for every member

1. Every literal and clock time: decision minutes, fill minutes, exit minutes, offsets from O, C, T_a and T,
   the buffer, the CLV cuts, the hold count.
2. Direction: the side or the signal's sign convention.
3. The exit: its time, and "first bar at or after" behaviour when a bar is missing. For CP2, the 75-bar
   count and that there is no C-2 exit.
4. Sizing: q_c from the frozen table, never a literal; exits close the whole position.
5. The event set and its instants: recompute TREASURY_AUCTIONS (per tenor), FOMC_STATEMENT_DATES,
   ISM_SERVICES_DATES and the month-end table in your own code from the frozen sources. Check the tenor
   map, T_a = the instant in CT, DROPPED_AUCTIONS against the XML check, and the coverage (both windows,
   2019-05-06..2026-06-19).
6. Availability: no input is read before it is available. Each bar is used only after its close.
   CP3 uses only complete bars of earlier trade dates. Every event-table entry is known before its
   trade date (auction announced before auction_date, FOMC schedule published before the year,
   ISM release dates and EC-CAL known in advance). No member reads a hindsight field (for example
   vendor_degraded_day or anything the bar's flags know only later), any future bar, or the account in a
   way that leaks the future.
7. The C4 exclusions for the five new members (early halt from the decision bar, the instrument guard,
   the missing-entry-bar rule) and Family H's rules for CP3; the ports carry no C4 guard beyond D6's.
8. The flatten and the D9 floor: nothing in a member works against the engine's F, entry cap or 2-minute
   rule. trading_windows match specs S0.12.
9. Nothing more: no filter, guard, re-entry, size rule or state that the entry does not state.
10. The factories, names and legs match specs S0.2 and the freeze script's declarations. Every file passes
    screening.stage_e_freeze.check_member_source.
11. The tests pin the cases the stage prompt names (entry and exit times, the event-window behaviour,
    the flatten, a missing bar at a decision time, a release that moved), and they would fail if the rule
    were wrong. Name any test that passes vacuously.
12. Each lead reading L-01..L-22: is it the narrowest reading the frozen text allows, or is it fixed by a
    reference the spec cites? Where you disagree, say which reading you would take and why.

You may run the members on synthetic bars through the real engine (the canary kit in
tests/_stage_e_canary_kit.py), with your own scripts under reports/stage_e3_briefs/audit/. You may also run
the two test files (`uv run pytest -q <file>` without PYTHONPYCACHEPREFIX, nice -n 10).

## Output

reports/stage_e3_member_audit.md, "Part 1: fidelity audit (Task 3)". Include:
- the time you started and ended (PDT) and the files' sha256 as you audited them;
- per member, a checklist table (items 1-11), with a verdict per item and file:line;
- a section on the lead's readings (item 12), one line per reading;
- a findings list. Each finding is graded BLOCKING (the module would implement something other than
  the frozen entry, or leak), SHOULD FIX (a defect that could change a trade in a case not yet seen,
  or a test that does not pin what it claims), or NOTE. Give each finding file:line, what is wrong,
  and the smallest fix inside the frozen entry.
Leave a heading "Part 2: recomputation (Task 6)" with nothing under it. The lead will resume you for it.
Return to the lead: the report path, a summary of at most 200 words (the count of findings by grade and
each BLOCKING one named), and anything you could not finish.

## Boundaries

- Read-only on the repository except your report and your own scripts under reports/stage_e3_briefs/audit/.
  No edits to code, tests, specs, frozen files or manifests. No git changes.
- Synthetic bars only: never read a real bar file (data/processed*, parquet), never run
  screening.stage_e_runner, never call write_cluster_freeze. No web, no Databento, no TopstepX, no
  REGISTRATION.md. Do not spawn workers.
- Read files by section and keep command output short (CLAUDE.md context hygiene).
