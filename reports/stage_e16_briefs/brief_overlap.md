# Task 2 brief: OverlapAudit-OpusHigh (worker-high, opus). Read brief_common.md first.

Objective: compare each of H1 to H5 (docs/prompts/STAGE_E.16.md "THE FIVE HYPOTHESES" and lead_spec.md section 4)
against every Stage D and Stage E catalog member and every registered or screened test of the program: same signal,
same time window, same products, same data window. Report every near match and how H1 to H5 differ. The lead rules:
a hypothesis identical to a tested member (same signal, window and products) is dropped before registration; a
related one is kept and the relation is written into its freeze. You recommend; you do not rule.

Inputs (read by section; grep first): reports/stage_e0_catalog.md (in particular CP1 and all its clusters'
members, K2-aucpre-01, K2-aucpost-01, K2-monthend-01, X-04, the K1 and K3 members), reports/stage_e0_catalog_K1.md to
_K8.md, reports/stage_e10_catalog_K9.md (and its rulings), the Stage D family declarations
(reports/stage_d1b_family_f_declaration.md, reports/stage_d1d_timeframe_declaration.md, docs/STAGES.md for Stage D's
families A-G and their tests), the frozen Stage E cluster member lists (screening.stage_e_freeze cluster freeze files;
strategy/members/k*/ docstrings only), the ML route v2 signal library (docs/STAGE_E_ML_V2_DESIGN.md; ml_route_v2/signals/
docstrings: k2 auction_phase, month-end and settlement-time features), Stage E.13's drafts (reports/stage_e13_*), C1
and C2 (reports/stage_e14_prereg_C1.md; C2 stopped), ledger/trial_registrations.jsonl (what is registered), and
docs/STAGES.md / progress.md for which members reached a confirmation read and on which dates.

For each H, a table: member id, cluster/family, signal (what it reads), decision time and holding window, products
traded, data window it was screened or confirmed on (research window 2025-04..2026-06; confirmation 2019-05..2024-02;
Gate 0 2019-05..2024-02), result or verdict, similarity (identical / related / unrelated) and the reason in one line.
Then, per H, a one-paragraph recommended "relation" text for its freeze, and a recommendation: drop (identical) or
keep. Also state, per H, whether any program test already READ the 2019-05..2024-02 bars of H's products in H's
time window (data reuse: the H tests' 2019-05..2024-02 segment overlaps E.12's Gate 0 window and any Stage E
confirmation reads; list them), since the freeze must disclose it.

Specific near matches the lead expects you to settle (not exhaustive): CP1's first-half-hour signal into the last 30
minutes (Gao, Han, Li, Zhou) vs H1's rest-of-day-into-last-30-minutes-before-settlement; K2's intraday auction and
month-end slices vs H2 and H3 (multi-day); any Stage D or E member that trades the last 30 minutes before a settlement
or the day-session open after a prior-day move (vs H4); any combination or portfolio member (vs H5).

Output: reports/stage_e16_overlap.md. Boundaries: read-only on the repo; no market data; no web; write only the
output file. Other workers own settlement minutes, calendars and base_rules/.
