# Task 4 brief: FreezeReviewer-FableXHigh (worker-xhigh, fable). Read brief_common.md first.

You are the independent, adversarial reviewer of Stage E.16's freeze before its commit. The work you review was
written by Opus workers and the Opus lead; your value is a second model's view. Repo:
/home/kiros-li/Documents/GitHub/PropExperiment (main tree; the freeze candidate is uncommitted there).

Read (by section; grep first): docs/prompts/STAGE_E.16.md (THE prompt: the five hypotheses, windows, pass bar,
guardrails, Task 4's review list); reports/stage_e16_briefs/lead_spec.md; reports/stage_e16_rulings.md (user rulings
U1 to U3b of 2026-10-09 are BINDING: do not flag them as loosening; check they are applied faithfully);
reports/stage_e16_prereg_common.md and reports/stage_e16_prereg_H1.md .. _H5.md; reports/stage_e16_settlement.json/.md;
reports/stage_e16_windows.json; reports/stage_e16_calendars/*.json and reports/stage_e16_calendars.md;
reports/stage_e16_overlap.md; reports/stage_e16_power.json/.md; the code base_rules/ and tests/test_base_rules_*.py;
reports/stage_e16_briefs/runtime_probe.md and release_touch.md; reports/stage_e16_handoff.md; the candidate manifest
reports/stage_e16_freeze.json (written by reports/stage_e16_briefs/freeze_manifest.py). For comparison, the frozen
engine screening/stage_e_engine.py and costs screening/stage_e_frozen.py, data/stage_e_bars.py, data/hist_store.py,
C1's freeze section 11 (reports/stage_e14_prereg_C1.md).

Check, and report each finding graded BLOCKING (must be fixed before the commit), SHOULD FIX (fixed before the
commit unless the lead rules otherwise with a reason) or NOTE:
1. No free parameter: every number, minute, window, threshold, lag, warm-up, tie rule and cost case is fixed in the
   pre-registration or its hashed inputs; nothing is left to the E.17 runner's discretion.
2. No look-ahead: every signal, sigma, H5 scaling and exclusion uses only information available at its decision
   instant under the engine's clock (decide at a bar's close, fill at a later bar's open). Read the code paths, not
   only the text; check the causality tests really perturb the future.
3. The simulator is never more generous than the frozen engine: same fill rule, same D8 costs (base case at size
   one equals the engine's; stress adds one tick per side), the event-window rule and fill guard, roll handling,
   marks; the single-day engine-match test is real (it runs the frozen engine).
4. Windows clear of holdout-2, the March 2024 embargo, MES, the research window and anything from 2026-06-21; the
   loader's refusals cover them; no trade date after 2024-02-29; H3 units ending after 2024-02-29 excluded.
5. The splice rule (store boundary, no double-counted date, rolls, references) and the fallback rule are decidable
   before any bar is read.
6. The pass bars are exactly the prompt's as amended by U3a/U3b: Holm 0.05 across the five, one-sided, n >= 30,
   year stability (10 units; H2 6), the larger-p rule only tightens; DSR, stress and 1.5 x reported only.
7. The settlement table's lead grades and the calendar rulings are defensible and applied by the code (H1/H4 bar
   on lead_grade; listing rule; LE 2010-2014 excluded; livestock weekday opens).
8. The power table's method and inputs are sound and stated for the full and fallback windows.
9. The hand-off's order respects C1's freeze section 11 and U1 (caps-only harness for C1; the plan harness only after
   C1's evaluation), the stale-ledger quote guard, registration before purchase, and the fallback recording.
10. The manifest covers every frozen input (prereg files, base_rules/, its tests, the input tables, the splice and
   fallback rules, the power table) and nothing that is market data.
You may run `uv run pytest -q -p no:cacheprovider tests/test_base_rules_*.py` (synthetic only) and short scripts that
read code, JSON and calendars. You must not read any market-data store, call any vendor, or edit any file except your
output. Do not spawn agents.

Output: reports/stage_e16_review.md: a verdict line (APPROVE, APPROVE WITH FIXES, or REJECT), then findings F-01..
each with grade, file:line, what is wrong, why it matters, and the fix you propose. Return the path, the verdict, the
count per grade, and a summary of at most 200 words.
