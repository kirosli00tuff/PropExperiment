# Stages

Naming convention: `Stage X.Y : Task Z` (per program ways-of-working).
Prompts delivered in chat between BEGIN PROMPT / END PROMPT markers, not
as files. This doc tracks stage scope only; prompt text lives in chat
history, not here.

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
- Stage D.2 — Sealed holdout read under the pre-registered bar.
- Stage E — Practice-account forward test, then one 50K Combine.
