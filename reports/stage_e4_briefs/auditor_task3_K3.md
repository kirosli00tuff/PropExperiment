# Brief: MemberAuditor-K3-FableXHigh, part 1 (Stage E.4 Part 3, K3, Task 3: fidelity audit)

Worker file: worker-xhigh. Model: fable. Effort: xhigh. You wrote none of the code, the specs or the tests,
and you are not the harness reviewer or the K4 and K5 auditors. Written by the Stage E.4 lead, 2026-09-27. Times in PDT.

## Objective (one)

For each of K3's nine coded members (30 declared trials), check that the module implements its frozen
catalog entry and nothing more, and that each of the lead's readings (specs section 10: the E.3 readings
and K4 readings adopted, K3-L-01..K3-L-11) is the narrowest the frozen text allows or is fixed by a cited reference.
Recompute every literal table from its source. Report findings. You do not fix code.

## Inputs (read by section, never whole large files)

- The frozen entries: reports/stage_e0_catalog_K3.md: the banner (lines 1-7), the header and C1-C12 (lines 62-234, every
  bracketed note), the nine member sections (K3-cp1-01 237-284, K3-cp2-01 285-339, K3-cp3-01 340-379, K3-ldnrev-01 380-478
  with its R-05 banner, K3-ldnmom-01 479-554 with the 01:40 narrowing, K3-mehedge-01 555-647, K3-ecbfix-01 648-725,
  K3-tkypre-01 726-800, K3-tkypost-01 801-855) and section 7 (lines 1115-1177). docs/STAGE_E_DESIGN.md D6 lines 348-411 and
  D9 lines 478-614.
- The lead's specs: reports/stage_e4c_member_specs.md (all of it).
- The code: strategy/members/k3/*.py. The tests: tests/test_e4_k3_members*.py. The coders' reports:
  reports/stage_e4c_coder_A.md (ports and mehedge) and reports/stage_e4c_coder_B.md.
- The contract: strategy/stage_e/_template.py, strategy/stage_e/interface.py, and how the engine calls a
  member (screening/stage_e_engine.py, screening/stage_e_rules.py call_member and account_view).
- The MES references the ports cite: strategy/research/h_daily_bar/_mechanics.py (docstring) and
  h6_prior_close_location.py; strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py
  lines 135-182. E.3's audited K2 ports (strategy/members/k2/cp1.py, cp2.py, cp3.py) run on the same
  07:20 / 14:00 clock as K3's and may be diffed against them (they should differ only in roots and names).
- The frozen sources of the literal tables: EC-CAL FX (data.group_session.load_group_calendar("fx")), the engine's session
  rules (rules.sessions.flatten_time_ct, ruling K3-L-11), the K3 check reports/stage_e4c_release_check.json and .md with its
  saved pages under data/vendor/release_pages/e4c/ and the index files under data/vendor/index_history/ (each with a
  manifest.jsonl). Read JSON with short scripts that print counts and diffs only.
- The freeze declarations the lead will write: reports/stage_e4_briefs/write_k3_freeze.py (run it with
  `PYTHONPATH=. ... --dry-run` only).

## What to check, for every member

1. Every literal and clock time: the port clocks (O 07:20, C 14:00), the CP2 buffers (0.0002, 0.0004 on 6B, 0.000002 on 6J),
   ldnrev's T_L-11/T_L-1 (R-05) and T_L+4/T_L+19, ldnmom's T_L-15/T_L-13/T_L+4, mehedge's T_L-61/T_L-4, ecbfix's 00:59, T_E-1,
   T_E, 15:04, tkypre's 17:29 on d-1 and T_T-1, tkypost's T_T and 00:59, in both clock regimes (mismatch weeks; CST/CDT).
2. Direction: the side or the signal's sign convention (ldnrev contrarian; ldnmom with S; mehedge against R_eq; ecbfix SELL then BUY; tkypre SELL; tkypost BUY).
3. The exit: its time, and "first bar at or after" behaviour when a bar is missing. For CP2, the 75-bar
   count and that there is no C-2 exit.
4. Sizing: q_c from the frozen table (1 on all seven), never a literal; exits close the whole position.
5. The event sets and their instants: recompute FX_FULL_SESSIONS (with K3-L-11's engine-F condition), MONTH_ENDS (coverage
   rule, section 11), EW_BANK_HOLIDAYS, TGT_CLOSING_DAYS, TOKYO_BUSINESS_DAYS, GOTOBI_OR_TOKYO_MONTH_END, the T_L/T_E/T_T
   clock tables (zoneinfo; C9's known-answer tests) and mehedge's R_eq table from the saved Nikkei files (P_a strictly before
   ME(m)'s calendar date) in your own code; check the dropped EUR mehedge trial against the entry's rule and the check's SX5E
   evidence; spot-check the TARGET and Tokyo year-end evidence against the saved pages (the manifests record what was served).
6. Availability: no input is read before it is available. Each bar is used only after its close. CP3 uses only complete bars of earlier
   trade dates; ovr's reference values come only from earlier trade dates. Every table entry is known
   before its trade date (bank holidays and IBA notices published in advance; the FOMC calendar before the year). No member reads a hindsight field, any future bar, or the account in a
   way that leaks the future.
7. The C4 exclusions for the five new members (early halt from the decision bar, the instrument guard,
   the missing-entry-bar rule), C10's non-positive guard where a percent return is computed (mehedge's ln ratio), Family H's rules for CP3; the ports carry no C4 guard beyond D6's.
8. The flatten and the D9 floor: nothing in a member works against the engine's F, entry cap or 2-minute
   rule, or D9.7's forced exit. trading_windows match specs S0.12 (both clock slots; the overnight intervals on d-1).
9. Nothing more: no filter, guard, re-entry, size rule or state that the entry does not state. No micro, E7 or EUR mehedge trial exists.
10. The factories, names and legs match specs S0.2 and the freeze script's declarations (30, ordinals
    1-30). Every file passes screening.stage_e_freeze.check_member_source.
11. The tests pin the cases the stage prompt names (entry and exit times, the event window, the flatten, a
    missing bar at a decision time, a moved or dropped event (a mismatch week; CST/CDT; an E&W, TARGET or Tokyo holiday), the percent-return guard, D9.7's price-limit exit),
    and they would fail if the rule were wrong. Name any test that passes vacuously.
12. Each lead reading (the adopted E.3 and K4 readings and K3-L-01..K3-L-11): is it the narrowest reading the
    frozen text allows, or is it fixed by a reference the spec cites? Where you disagree, say which reading
    you would take and why.
13. The ports against E.3's audited K2 ports (same clock): confirm they differ only in roots and names. Rule on K3-L-04 (the
    early-halt test on trade date d from a table) and K3-L-11 (the engine-F condition) and on the harness inconsistency behind it.
14. Catalog section 7 as settled (K3-L-09): say whether each settlement follows the frozen text and the prompt.

You may run the members on synthetic bars through the real engine (the canary kit in
tests/_stage_e_canary_kit.py), with your own scripts under reports/stage_e4_briefs/audit_k3/. You may also run
the test files (`nice -n 10 uv run pytest -q <file>` without PYTHONPYCACHEPREFIX).

## Output

reports/stage_e4c_member_audit.md, "Part 1: fidelity audit (Task 3)". Include:
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

- Read-only on the repository except your report and your own scripts under reports/stage_e4_briefs/audit_k3/.
  No edits to code, tests, specs, frozen files or manifests. No git changes.
- Synthetic bars only: never read a real bar file (data/processed*, parquet), never run
  screening.stage_e_runner, never call write_cluster_freeze. No web, no Databento, no TopstepX, no
  REGISTRATION.md. Do not spawn workers.
- Read files by section and keep command output short (CLAUDE.md context hygiene).
