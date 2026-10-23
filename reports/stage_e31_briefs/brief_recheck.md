# Brief: ReCheck-FableXHigh (worker-xhigh, model fable) - Stage E.31 Part 4, the one re-check of both review passes

Objective (one): re-check, once, the fixes made after the two reviews, and return GO or NO GO for (A) buying the
remaining 37 months and (B) running the measurement.
(A) Purchase path, changed after pass 1's GO (reports/stage_e31_briefs/R_spec31.md items 4, 5, 12): FixCoder's
changes to reports/stage_e31_briefs/work/pilot/pull31.py (--retry-download, lock), pilot31_common.py, verify31.py
(hard checks), canary_check31.py and their tests; README31.md. Check that the retry path can only re-buy one failed
request once, inside acct-3's 125.00 cap, never a settled one, and that nothing else in --buy/--quote changed in a way
that lets it buy outside spec v2 section 9; that verify31's hard checks are right (and that any check FixCoder relaxed
was wrong as written, for the reason given). Read runs/canary31.md and runs/canary_checks31.log (structure only).
(B) Engine, after pass 2's NO GO (reports/stage_e31_briefs/R_engine31.md item 1 BLOCKING; items 5, 8, 9 advisory):
SimCoder's changes to mbo_book31.py, measure31_core.py, measure31.py and tests; check item 1 is fixed (run its probe:
70-lot sell against a 150-lot TOP order gives [70, 0, 0], the virtual order unfilled) and nothing else regressed.
Lead rulings already made (do not re-open): R_engine31 items 2 (keep Q for model b), 7 (--workers 4), 3, 4, 6, 10, 11
logged; measure31.checked_tick accepts ZS/ZL ticks in USD or cents; spec v2 erratum (section 7 governs the gate).
Run: uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests. No real data run of the engine; no
opening of measure31 outputs; no Databento call (fake clients only); no edits except your output; no commits.
Output: reports/stage_e31_briefs/R_recheck31.md: first line "A: GO|NO GO; B: GO|NO GO"; then numbered items (BLOCKING
or ADVISORY) with file:line. Return: the path, both verdicts, a summary of at most 150 words.
