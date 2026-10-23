# Brief: EngineReviewer-FableXHigh (worker-xhigh, model fable) - Stage E.31 Part 4, pass 2 (before the measurement)

Objective (one): an independent, adversarial review of the engine and stats code against the frozen spec v2, returning
GO or NO GO for running the measurement.
Read: reports/stage_e31_pilot_spec.md (v2, sha256 31d33e68736b3c13ae46afcd0bf8d28411bbb3d96864802a6193cf5f33b9f61a; check),
reports/stage_e31_briefs/R_spec31.md (pass 1; its items 1, 2, 6-9, 11 were adopted into v2 and must be in the code),
reports/stage_e31_briefs/work/pilot/TABLES31.md, research/K_algorithm.md (sections a-d) and research/data_facts.md (a);
code in reports/stage_e31_briefs/work/pilot/: mbo_book31.py, kalgo31.py, measure31_core.py, measure31.py,
README_measure31.md, stats31.py, stats31_core.py, stats31_report.py and their tests (tests/test_book31.py,
test_kalgo31.py, test_measure31.py, test_stats31.py, synth31.py).
Check at least: (1) the K allocator against spec 3.1 and every CME example (recompute two by hand), including the v2
rules (virtual never TOP; FIFO exception tested with the virtual included, the Q = D boundary; TOP Max counting before
and after 2023-10-02; ceil split; post-FIFO pro-rata denominator; leveling order); (2) the book: A/C/M/R semantics,
priority loss rules, snapshots (R then A with F_SNAPSHOT), reads only after F_LAST, T/F handling and the outright
volume Q of a match event (fills of resting orders), events grouped per aggressor per price; (3) fill models (a), (b),
(c) exactly as spec section 4, the 50 ms join and cancel, the 60 s life, through fills, no fill on a touch, the
virtual order placed at the back with the right queue; (4) look-ahead: no quantity at a time later than the decision
time enters a placement, a fill decision, mid0 or a condition (ZS/ZL moves use only data at or before t_f; imbalance
at j); (5) markouts, half-spread, drops and the no-drop variant; ticks from the definitions; sessions in CT (CST/CDT),
the grid boundary (56 DAY grid times), exclusions (holidays, late opens, roll days, book validity, gaps); (6) the loop
(spec section 6); (7) stats: the kill rule exactly spec v2 section 7 (K1 under both variants, ratio of sums per
replicate, day-block bootstrap 2,000 / seed 31, K2 before drops, K3 the mean over DAY dates, the fragile label), the
completeness gate; (8) nothing reads a record on or after 2024-03-01; (9) speed and memory are within the CLAUDE.md
compute limits for a run over about 820 trade dates.
Run the tests (uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests). You may build your own
synthetic cases. You must NOT run the engine on real data, and must not open the purchased files or any measure31
output.
Output: reports/stage_e31_briefs/R_engine31.md: verdict GO or NO GO on the first line; numbered items marked BLOCKING
(must be fixed before the measurement) or ADVISORY, with file:line and the proposed fix.
Boundaries: review only; no edits except your output; no Databento call; no commits. Keep output short.
Return: the path, the verdict, a summary of at most 200 words, and anything unfinished.
