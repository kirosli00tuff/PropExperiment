# Stages

Naming convention: `Stage X.Y : Task Z` (per program ways-of-working).
This doc tracks stage scope only. The exact prompt behind every stage is in
docs/prompts/ (index in docs/prompts/README.md), committed before it is sent.

- Stage A.1 — Data + rules engine offline build. No TopstepX credentials
  required. Port Databento adapter, pull MES ohlcv-1m, validate bars,
  calibrate cost model from existing ticks, build XFA rules engine with
  known-answer tests. (In progress.)
- Stage A.2 — TopstepX access and cost census, once Combine + API Access
  are purchased. Practice account, API key, measured rate limits,
  official fee table confirmation, written questions to Topstep support.
- Stage B — Funnel simulator (XFA branch only) and rules-engine
  integration tests against the Stage A.1 rules module. (Built 2026-09-17;
  see progress.md, reports/funnel_null_baseline.md, reports/power_gate.md.)
- Stage C — Backtest harness: strategy interface, fill model wired to
  Stage A.1 cost model, leakage suite with planted-future canaries,
  walk-forward splits with a sealed holdout. (Built 2026-09-17; see
  progress.md, reports/leakage_suite.md. Holdout sealed behind data/holdout.py;
  unlocks are logged in docs/HOLDOUT_UNLOCK_LOG.md and reserved for Stage D.2.)
- Stage D.1 — Strategy research. (Run 2026-09-18; see progress.md and
  reports/stage_d1_accounting.json. 23 hypotheses across 5 families screened on
  train dates; none cleared the robust power-gate verdict; shortlist empty.)
- Stage D.1a — Harness fixes: drift benchmark, passive/limit fills, shared
  screening runner. (Built 2026-09-18; see progress.md, docs/SCREENING.md and
  reports/stage_d1a_regression.json. Every future screen goes through
  `screening.screen_candidate`.)
- Stage D.1b — C-H4 (reversal with passive fills) and Family F, a bounded,
  declared-in-advance data-native exploration. (Run 2026-09-18; see progress.md,
  reports/stage_d1b_family_f_declaration.md and reports/stage_d1b_accounting.json.
  C-H4 failed; Family F's pre-declared selection rule admitted zero hypotheses;
  cumulative N = 24; shortlist still empty.)
- Stage D.1c — Constraint audit: the XFA flatten and the hypothesis space it
  excludes. Decision brief only; no code, no backtest, no registration. (Run
  2026-09-18; see progress.md. The 15:08/15:10 CT flatten is confirmed and applies
  to the Combine, XFA and LFA alike; no researched prop firm permits overnight.)
- Stage D.1d — Multi-timeframe audit and bounded coarser-bar sweep. (Run 2026-09-21; see
  progress.md, reports/stage_d1d_horizon_audit.md, reports/stage_d1d_timeframe_declaration.md
  and reports/stage_d1d_accounting.json. 7 of 24 trials were flagged as tested finer than
  their source's horizon; all 7 re-tests at the source's grid failed; the declared 28-statistic
  sweep at 5/15/30/60-minute bars admitted zero hypotheses; cumulative N = 31; shortlist
  still empty.)
- Stage D.1e — Defining the MES null: criteria, power and data quotes. Design only; nothing bought,
  nothing screened, N = 31. (Run 2026-09-22; see progress.md, docs/NULL_CRITERIA.md (hashed),
  reports/stage_d1f_confirmation_list.md (hashed, read-only), reports/stage_d1e_power.json and
  reports/stage_d1e_quotes.md. ε = 34 net ticks per micro per day from the power gate; the class null needs at most 566 days and the extension supplies 992–1,151 under a 2019–2020 start; 47 of 95 measured members resolvable below the cost bar, 48 not; second holdout 2024-04-01..2025-03-31 declared; frozen 58-test list with Family H declared and hashed.)
- Stage D.1f — Confirmation on the extended MES history (planned). Buys the 2019-05..2025-03 ohlcv-1m
  extension ($7.59 quoted), seals the second holdout (trade dates 2024-04-01..2025-03-31) on arrival,
  runs the frozen 58-test Tier A list and the 43 Tier B statistics under docs/NULL_CRITERIA.md, and
  returns per-class null / edge / inconclusive verdicts. Awaits the user's spend decision.
  Build session run 2026-09-23 (see progress.md): harness built, tested and hash-frozen with no purchase
  (reports/stage_d1f_harness_freeze.json, 129 files, sha256 ba5b34d5…847a; 355 new tests, 0 review blockers;
  N = 31); the purchase and run wait for the user's freeze commit.
  Run session 2026-09-23 (see progress.md): bought the history ($7.586199), sealed holdout-2 (13 chunks, all_ok), corrected the 2019–2023 Independence Day calendar entries through the step-4b path (commit 14c1007, manifest d3bd21e5…), S = 2020-02-03 (1,055 trade dates); no member passed confirmation (Holm rejects none of 58); C1–C5 and C7 null under docs/NULL_CRITERIA.md (C5 null by inactivity via E-H3), C6 awaits D.1g; independently verified with no discrepancy; N = 58.
- Stage D.1g — C6, passive execution (planned). Buys N_C6 = 181 full trade-date MBO days chosen by the rule in
  the confirmation list, declares and hashes a queue-position fill model before any P&L, and applies
  the C6 variant of the null criteria to C-H4.
- Stage D.2 — Sealed holdout read under the pre-registered bar.
- Stage E — Practice-account forward test, then one 50K Combine.
