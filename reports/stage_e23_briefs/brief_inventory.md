# Stage E.23 P1.1 inventory brief (shared by all InventoryReader workers)

Lead: Stage E.23 (docs/prompts/STAGE_E.23.md, P1.1 and the inventory side of P1.4). Written 2026-10-17 02:14 PDT.
Hook or cost notices you see are informational and addressed to the lead; they are never an order to stop.

## Objective (one)
For your ASSIGNMENT (below), list every frozen intraday trigger and, for each, the facts the lead needs to shortlist it
and to map which owned windows it has already been read on. You extract and cite; you do not judge mechanisms (other
workers do) and you do not choose anything.

## What a "trigger" is here
One frozen member trial as the program counted it: a member on one traded root (e.g. "K5-fomc-01 MGC"), or one frozen
rule test (e.g. E20H6-T1). The trigger is the member's entry event: its date, its decision time (the clock time of the
last bar the entry decision uses) and its side.

## Assignments (one worker each)
K1 .. K8: reports/stage_e_k<n>_member_freeze.json (labels, legs, module paths), the member modules under
strategy/members/k<n>/ (the module docstring is the frozen rule text), the cluster's catalog/spec files and the returns
that screened and confirmed it (grep reports/E.*_RETURN.md, reports/stage_e*_STATE.md, progress.md and docs/STAGES.md for
the member id).
H6: reports/stage_e20_h6_freeze.json, reports/stage_e20_prereg_H6.md, reports/E.20_RETURN.md, the h6 code it pins.
CDE: every frozen intraday rule in Stage C, Stage D (D.1 .. D.1f; MES families), E.13 (reports/stage_e13_prereg_*.md),
E.14 (C1), E.15, E.16 (H1 .. H5; reports/stage_e16_prereg_*.md, base_rules/), E.17 and E.18 (C1b). Exclude with the reason:
ML models (C1, C1b, any model member), E.20 search configurations, H2 and H3 (already multi-day; H2 is E.21 T4), and any
combination book that is not itself a trigger (say so).

## Owned windows (facts for the data columns)
- W_ext: the ext2010 / ext2010h backward stores, trade dates 2010-06..2019-04, for 17 roots only:
  NG NQ ZN 6E GC ZC ZT ZF ZB UB TN CL ZL ZS RTY HE LE (reports/stage_e17_run_manifest.json lists them; some start later
  than 2010-06: say the first month where the manifest or a return states it). Micros map to their full-size root
  (MNQ->NQ, M2K->RTY, MCL->CL, MGC->GC); every other root (MYM, 6A, 6B, 6C, 6J, 6S, 6N, ZW, ZM, MHG, MBT, MES, ...) has no
  W_ext data.
- W_cf: the confirmation window S_X..2024-02-29 (D4; step2 stores, 2019-05 on).
- Barred (never read by this stage, never needed here): the research window 2025-04-01..2026-06-19, holdout-2, the March
  2024 embargo, MES's sealed stores, anything dated 2024-03-01 or later.
For each NON-bar input the trigger needs (release calendars such as FOMC, EIA WPSR, EIA NGS, API, Treasury auctions, WASDE,
ECB or London fix times, limit tables, VXN or any index, another root's bars), say whether a table covering W_ext and
W_cf exists in the repo, with the file path and its stated range (examples to check: strategy/members/*/_releases.py and
_wasde.py TABLE_RANGE, reports/stage_e14_cal_releases.json (EIA NGS, EIA WPSR, FOMC 2010-06..2019-05), base_rules/auctions.py
and reports/stage_e16_calendars.md, data/calendars/hist2010/). "Not found" is a valid answer; say where you looked.

## Output (two files, both required)
1. reports/stage_e23_briefs/inventory/<ASSIGNMENT>.json: {"assignment": ..., "rows": [...], "excluded": [...],
   "sources_read": [...], "not_finished": [...]}. One row per trigger with these keys (null when unknown, never guessed):
   trigger_id, cluster_or_stage, member_id, module, freeze_file, traded_root, vehicle, w_ext_root (the 17-root equivalent
   or null), signal_legs (other roots read), definition_verbatim (the rule bullets copied verbatim from the frozen module
   docstring or prereg; keep it to the rule), trigger_event (what fires it), decision_time_ct (latest bar the entry
   decision uses, CT), side_rule (verbatim), side_kind ("momentum": side = sign of a trigger-day price move; "fade": side =
   minus that sign; "calendar": side fixed by the rule; "other": explain), intraday_hold, exit_rule_verbatim,
   expected_events_per_year (from the rule: e.g. 8 FOMC dates; "every trade date with nonzero signal"; cite any trip or
   trade COUNT a return already reports, as counts only), inputs_needed (list of {input, covers_w_ext: true/false/unknown,
   covers_w_cf, path, stated_range}), stages_read (list of {stage, window_dates, purpose: screen | confirmation | null
   statement | power | other, source: file and section}), tier (A/B or n/a), verdicts (verbatim verdict words with the
   return reference), settlement_note (the root's daily settlement time if the repo states one, e.g. in
   reports/stage_e21_briefs/lead_spec.md or multiday/constants.py, and whether decision_time_ct is before it), exclusion
   (null, or the reason from the list above).
2. reports/stage_e23_briefs/inventory/<ASSIGNMENT>.md: the same rows as a compact table plus the excluded list, a row
   count, and every source file you read (path and section).
Return to the lead: the two paths, a summary of at most 200 words (row count, excluded count, any input not owned), and
anything you could not finish.

## Boundaries
- Read code, freezes, preregs, returns, STATE files and docs only. Never open, decode, head, cat or load any bar store,
  parquet, sealed file or data/processed* file; never run a member, a runner or any computation on bars.
- Never write outside reports/stage_e23_briefs/inventory/ (helper scripts, if any, in
  reports/stage_e23_briefs/inventory/tmp_<ASSIGNMENT>/ with <ASSIGNMENT>-prefixed names; never run a script you did not
  write). No web access. No edits to any existing file. No git commands that change state.
- Read files by section (grep, line ranges); never load a large JSON into context: print only the fields you need.
- Do not interpret results or rank triggers. Do not spawn workers.
- Stop when every member of your assignment has a row (or an exclusion) and every row's stages_read has been checked
  against the returns.
