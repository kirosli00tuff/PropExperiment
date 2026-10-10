# Stage prompts

Every prompt that drove a Claude Code stage session, exactly as it was sent,
so any stage's instructions can be audited against its progress.md entry.
From 2026-09-23 on, each new prompt is committed here before it is sent.

| Stage | File | Lead as written | Run | Notes |
|---|---|---|---|---|
| A.1 | STAGE_A.1.md | Opus 5, high | 2026-09-16 | Offline data and XFA rules engine build |
| B–C | STAGE_B-C.md | Opus 5, ultracode | 2026-09-17 | Funnel simulator and backtest harness |
| D.1 | STAGE_D.1.md | Opus 5, ultracode | 2026-09-18 | The final version that ran |
| D.1 (draft) | STAGE_D.1_draft.md | Opus 5, ultracode | not run | Earlier draft, superseded by STAGE_D.1.md after the research-findings gap fixes |
| D.1a | STAGE_D.1a.md | Opus 5, high | 2026-09-18 | Drift benchmark, passive fills, shared runner |
| D.1b | STAGE_D.1b.md | Opus 5, high | 2026-09-18 | C-H4 and Family F |
| D.1c | STAGE_D.1c.md | Opus 5, high | 2026-09-18 | Constraint audit of the XFA flatten |
| D.1d | STAGE_D.1d.md | Opus 5, ultracode | 2026-09-18 and 2026-09-21 | First run hit the weekly limit after 13 minutes; resumed on Fable xhigh |
| D.1e | STAGE_D.1e.md | Fable 5.1, xhigh | 2026-09-22 | Final version, including the Session cost section added after launch |
| D.1f (build) | STAGE_D.1f_build.md | Opus 5.5, xhigh | 2026-09-22 | Final version, autonomous (no startup questions) |
| D.1f (run) | STAGE_D.1f_run.md | Opus 5.5, max | 2026-09-23 | Confirmation run: buy, seal, build, test the frozen list; Fable xhigh verification only |
| E.0 | STAGE_E.0.md | Opus 5.5, max | 2026-09-23 to 24 | CME universe: research per cluster, hypothesis catalog, program design draft, C6 closure; quotes only |
| E.1 | STAGE_E.1.md | Opus 5.5, max | 2026-09-24 | Apply the user's decisions, Fable-audited freeze, Databento account switch, step 1 purchase, ML route draft; no prices read |
| E.2a | STAGE_E.2a.md | Opus 5.5, xhigh, ultracode | 2026-09-25 to 26 | ML route freeze, source-window amendment, per-product rules, calendars, research-window bars, costs, vehicles, epsilon; overnight profile |
| E.2b | STAGE_E.2b.md | Opus 5.5, xhigh | 2026-09-26 | Screening runner, ML pipeline and M7 tests, canaries, step 2 purchase path and free quotes, Windows compute backend and V10, Fable max harness review, harness freeze; no purchase |
| E.3 | STAGE_E.3.md | Opus 5.5, xhigh | 2026-09-26 to 27 | K2 rates: code, Fable-audit and freeze the eight members, screen them on the research window; no purchase |
| E.4 | STAGE_E.4.md | Opus 5.5, xhigh | 2026-09-27 (01:54-10:05) | Harness fix C-1 and trip lists (K2 regression, Fable review, manifest v4), then K4 energy, K5 metals and K3 FX in turn: release-date checks, code, Fable-audit and freeze each cluster's members, screen on the research window; one unattended overnight run; no purchase |
| E.5 | STAGE_E.5.md | Opus 5.5, xhigh | 2026-09-27 | K4 and K5 confirmation: harness v5 (pre-2024 holidays, verdict code) and v6 (spend caps), step 2 purchase with holdout-2 sealed, start rules, power checks, NGS C9 check, hashed lists, one confirmation run per cluster, Fable recomputation |
| E.6 | STAGE_E.6.md | Opus 5.5, xhigh | before the 2026-09-30 reset | K7 bitcoin alone: event checks, code, Fable-audit and freeze six members, screen on the research window; no purchase |
| E.7 | STAGE_E.7.md | Opus 5.5, xhigh | 2026-09-28, before the weekly reset | K1 equity index alone: free VXN history, CPI instants, code, Fable-audit and freeze five members, screen; no purchase |
| E.8 | STAGE_E.8.md | Opus 5.5, xhigh | 2026-09-30 to 10-01 | K6 grains, oilseeds and livestock alone: WASDE and limit checks, code, Fable-audit and freeze seven members, screen; no purchase |
| E.9 | STAGE_E.9.md | Opus 5.5, xhigh | 2026-10-01 | K8 cross-market alone: legs per V16, event and clock checks, code, Fable-audit (cross-leg look-ahead) and freeze three members, screen four trials; no purchase |
| E.10 | STAGE_E.10.md | Opus 5.5, xhigh | 2026-10-02 | Low-frequency full-session holds: literature research and a draft K9 catalog built around the cost wall, Fable adversarial review; no market data, no purchase |
| E.11 | STAGE_E.11.md | Opus 5.5, xhigh (Fable max design review) | 2026-10-03 | ML route v2, a quant-style portfolio model: design draft and full pipeline build on synthetic data, leakage canaries, runtime probe, per-account key fix (harness v7); revised before launch with the research findings and V22 (Gate 0, ridge first, CPCV, drawdown-distance sizing, payout simulation); no market data, no purchase, no training |
| E.12 | STAGE_E.12.md | Opus 5.5, xhigh (Fable xhigh freeze review and Gate 0 verification) | 2026-10-03 | ML route v2 freeze with V23 applied, harness v8 (acct-2 cap, key strip, training-window purchase), phase-1 purchase within the funds on hand, c/sigma filter, Gate 0 run once, free quotes for later phases; then stop |
| E.13 | STAGE_E.13.md | Opus 5.5, xhigh (Fable xhigh adversarial review) | 2026-10-03 | Research and scoping after the Gate 0 fail: multi-day venues (prop firms, a personal micro account), trend and carry evidence and sizing, new information sources, a backward NG replication draft, a ranked plan with pre-registration drafts; no data read, no purchase |
| E.14 | STAGE_E.14.md | Opus 5.5, xhigh (Fable xhigh freeze review and verdict verification) | 2026-10-05 | C1 and C2 together with the funds on hand (V26): calendar probe, calendars, GEX file, harness v10 (cap unchanged), both freezes; C1 through q reproduction then frozen awaiting funds; C2 registered (N to 473), ES bought within $18.07, evaluated once |
| E.15 | STAGE_E.15.md | Opus 5.5, xhigh (Fable xhigh verdict verification) | 2026-10-07 | C1 completion per its E.14 freeze: verify inputs, harness v11 (acct-2 cap 291.08), fresh quote, register (N to 473), buy up to $60, build, evaluate once |
| E.16 | STAGE_E.16.md | Opus 5.5, xhigh (Fable xhigh freeze review) | 2026-10-08 | Part A of the base-rule batch (V29, no Databento): settlement sourcing, overlap audit, multi-day simulator and runners on synthetic data, 2010-2019 livestock and auction calendars, H1-H5 frozen on a 2010-2024 window, E.17 hand-off; no data read, nothing registered |
| E.17 | STAGE_E.17.md | Opus 5.5, xhigh (Fable xhigh harness reviews and verdict verification) | 2026-10-09 | C1 completed (v11, register, buy, evaluate), then the base-rule batch H1-H5 (v12, priority-ordered purchase within a $97 total budget, fallback list, register, run once each, Fable recomputation) |

Model names are as written in each prompt at the time. The routing rules
that apply today are in CLAUDE.md.
