# Brief: MemberAuditor-K5-FableXHigh, part 1 (Stage E.4 Part 2, K5, Task 3: fidelity audit)

Worker file: worker-xhigh. Model: fable. Effort: xhigh. You wrote none of the code, the specs or the tests,
and you are not the harness reviewer or the K4 auditor. Written by the Stage E.4 lead, 2026-09-27. Times in PDT.

## Objective (one)

For each of K5's seven coded members (11 declared trials), check that the module implements its frozen
catalog entry and nothing more, and that each of the lead's readings (specs section 10: the E.3 readings
and K4 readings adopted, K5-L-01..K5-L-12) is the narrowest the frozen text allows or is fixed by a cited reference.
Recompute every literal table from its source. Report findings. You do not fix code.

## Inputs (read by section, never whole large files)

- The frozen entries: reports/stage_e0_catalog_K5.md: the banner (lines 1-7), the header and common
  conventions C1-C14 (lines 75-281, with every bracketed note), and the seven member sections (K5-cp1-01 284-339,
  K5-cp2-01 340-392, K5-cp3-01 393-442, K5-preauc-01 443-537, K5-pmfix-01 538-639, K5-fomc-01 640-712, K5-ovr-01
  713-804), section 7 (lines 1030-1085). reports/stage_e1_changes.md line 32 (F-7). docs/STAGE_E_DESIGN.md D6 lines
  348-411 and D9 lines 478-614.
- The lead's specs: reports/stage_e4b_member_specs.md (all of it).
- The code: strategy/members/k5/*.py. The tests: tests/test_e4_k5_members*.py. The coders' reports:
  reports/stage_e4b_coder_A.md and reports/stage_e4b_coder_B.md.
- The contract: strategy/stage_e/_template.py, strategy/stage_e/interface.py, and how the engine calls a
  member (screening/stage_e_engine.py, screening/stage_e_rules.py call_member and account_view).
- The MES references the ports cite: strategy/research/h_daily_bar/_mechanics.py (docstring) and
  h6_prior_close_location.py; strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py
  lines 135-182. E.3's K2 ports and Part 1's audited K4 modules (strategy/members/k4/cp1.py, cp2.py, cp3.py,
  ovr.py) may be diffed against K5's (the rule texts are the same; the clocks differ).
- The frozen sources of the literal tables: reports/stage_e2b_release_calendar.json (sha256
  839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8; FOMC rows), E.3's FOMC table
  (strategy/members/k2/_releases.py), the K5 release check reports/stage_e4b_release_check.json and .md (UK bank
  holidays, no-auction days, auction instants) with its saved pages under data/vendor/release_pages/e4b/ and
  manifest.jsonl, and the metals calendar through data.group_session.load_group_calendar("metals"). Read JSON with short
  scripts that print counts and diffs only.
- The freeze declarations the lead will write: reports/stage_e4_briefs/write_k5_freeze.py (run it with
  `PYTHONPATH=. ... --dry-run` only).

## What to check, for every member

1. Every literal and clock time: decision minutes, fill minutes, exit minutes, offsets from O, C, T and T_P, the CP2
   buffer (MGC 0.40, MHG 0.0020), the CLV cuts, the hold count, preauc's T-31/T-2, pmfix's T_P-1/T_P+1/T_P+11,
   fomc's 12:59/13:04/13:14, ovr's decision times (08:20..12:20 gold, 08:10..11:10 copper), 20 dates, the 80% floor.
2. Direction: the side or the signal's sign convention (preauc always SELL; pmfix and fomc follow s; ovr fades).
3. The exit: its time, and "first bar at or after" behaviour when a bar is missing. For CP2, the 75-bar
   count and that there is no C-2 exit.
4. Sizing: q_c from the frozen table (MGC 1, MHG 2), never a literal; exits close the whole position.
5. The event sets and their instants: recompute GOLD_AM_AUCTIONS, GOLD_PM_AUCTIONS (dates and T_CT via zoneinfo, C10;
   the 5-hour weeks), FOMC_STATEMENT_DATES (and its equality with E.3's table) and METALS_FULL_SESSIONS in your own code
   from the sources, and check that the no-auction days and bank holidays follow specs section 11 and K5-L-03. Spot-check
   the release check's evidence for every no-auction day against the saved pages (the manifest records the capture
   actually served; K4's check mis-dated one) and say whether each follows C9 (announced in advance).
6. Availability: no input is read before it is available. Each bar is used only after its close. CP3 uses only complete bars of earlier
   trade dates; ovr's reference values come only from earlier trade dates. Every table entry is known
   before its trade date (bank holidays and IBA notices published in advance; the FOMC calendar before the year). No member reads a hindsight field, any future bar, or the account in a
   way that leaks the future.
7. The C4 exclusions for the five new members (early halt from the decision bar, the instrument guard,
   the missing-entry-bar rule), C10's non-positive guard where a percent return is computed (ovr), Family H's rules for CP3; the ports carry no C4 guard beyond D6's.
8. The flatten and the D9 floor: nothing in a member works against the engine's F, entry cap or 2-minute
   rule, or D9.7's forced exit. trading_windows match specs S0.12 (including K5-L-08's two slots).
9. Nothing more: no filter, guard, re-entry, size rule or state that the entry does not state. No silver, platinum, GC or HG
   trial exists.
10. The factories, names and legs match specs S0.2 and the freeze script's declarations (11, ordinals
    1-11). Every file passes screening.stage_e_freeze.check_member_source.
11. The tests pin the cases the stage prompt names (entry and exit times, the event window, the flatten, a
    missing bar at a decision time, a moved or dropped event (a 5-hour-week auction; a no-auction day), the percent-return guard, D9.7's price-limit exit),
    and they would fail if the rule were wrong. Name any test that passes vacuously.
12. Each lead reading (the adopted E.3 and K4 readings and K5-L-01..K5-L-12): is it the narrowest reading the
    frozen text allows, or is it fixed by a reference the spec cites? Where you disagree, say which reading
    you would take and why.
13. F-7: diff strategy/members/k5/ovr.py against the audited strategy/members/k4/ovr.py and confirm they differ only in
    the decision clock, the calendar table and the value floor (80% of the possible values) (reports/stage_e1_changes.md
    line 32). Also rule on K5-L-05 (K5's "eligible trade dates (C4)" read as EC-CAL full sessions, as K4-L-08).
14. Catalog section 7 as settled (K5-L-04 on item 1; items 3-6 as frozen): say whether each settlement follows the
    frozen text and the prompt.

You may run the members on synthetic bars through the real engine (the canary kit in
tests/_stage_e_canary_kit.py), with your own scripts under reports/stage_e4_briefs/audit_k5/. You may also run
the test files (`nice -n 10 uv run pytest -q <file>` without PYTHONPYCACHEPREFIX).

## Output

reports/stage_e4b_member_audit.md, "Part 1: fidelity audit (Task 3)". Include:
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

- Read-only on the repository except your report and your own scripts under reports/stage_e4_briefs/audit_k5/.
  No edits to code, tests, specs, frozen files or manifests. No git changes.
- Synthetic bars only: never read a real bar file (data/processed*, parquet), never run
  screening.stage_e_runner, never call write_cluster_freeze. No web, no Databento, no TopstepX, no
  REGISTRATION.md. Do not spawn workers.
- Read files by section and keep command output short (CLAUDE.md context hygiene).
