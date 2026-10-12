# Brief: SearchReviewer-FableXHigh (Stage E.20 Step 6b, independent code review before the 45 registrations)

Added by the lead (CLAUDE.md: an independent fable xhigh check of harness code that a verdict rests
on). One objective: an adversarial review of the new pattern_search/ package and its tests against
reports/stage_e20_plan.md (as fixed after review; rulings in reports/stage_e20_rulings.md), before
the search freeze, the 45 registrations and any fit.

Check, at least:
1. Leakage: every value a fitted row sees is available at or before its decision time (the frozen
   signals, t4 rows, rod_ret, rod_absratio); normalization is causal; the risk table is per split and
   fold; purge and embargo come from the frozen CPCV unchanged; the admissibility filter reads
   volatility only; nothing from a test block reaches its own fit or its own sizing; nothing dated
   2024-03-01 or later can enter. Run or extend the perturbation, fold and canary tests (scratch
   files outside tests/, synthetic data only).
2. Faithfulness to the plan: the 35 KEPT signal names passed to build_panel exactly; the two added
   features as plan 5.2 defines them; t4 rows and their horizons; the 45 configurations in the frozen
   CONFIGS order with ids E20S-01..E20S-45; nested_cpcv and final_selection called with the plan's
   arguments; the empty-admissible refusal; the screen's three numbers computed exactly as plan
   section 9 says (path_daily with zeros, median of the 5 path t's, pbo_cscv on config_daily,
   Sharpe of the path average, the 4.0 alarm); every reported item; N_total passed explicitly.
3. Composition: does pattern_search bypass any check the frozen pipeline applies (the panel's drop
   rule and avail check, the CPCV input fingerprint, the register-before-fit rule, constants
   fingerprints)? Does it edit or monkeypatch any hashed file or constant? (`git diff --stat` must be
   empty for ml_route_v2, screening, rules, sim, data, base_rules, c1_replication, h6_rod, strategy.)
4. The guard and run discipline: planted cases; the registry check before any fit; the search freeze
   manifest check; resumability by configuration and split; the state and reports directories.
5. The timing probe in reports/stage_e20_briefs/search_build.md: plausible, and memory within
   CLAUDE.md's limits for the real run.

## Output

reports/stage_e20_review_search_code.md: a verdict (APPROVE, APPROVE WITH FIXES, BLOCK), findings
(SC-n, BLOCKING / SHOULD FIX / NOTE) with file and line, what is wrong, why it matters, and the fix.
Write it progressively. Reply to the lead: the path, a summary of at most 200 words, and anything you
could not check.

## Boundaries

No real data (no store, no GEX CSV), no results of E.12 Gate 0, E.15, E.17, E.18 or H6. Do not run
`python -m pattern_search run` or register anything. Do not edit pattern_search/, tests/ or any
frozen file; report only. No ledger writes, no commits. Do not spawn agents.
