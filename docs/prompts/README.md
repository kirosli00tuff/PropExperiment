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
| E.1 | STAGE_E.1.md | Opus 5.5, max | pending | Apply the user's decisions, Fable-audited freeze, Databento account switch, step 1 purchase, ML route draft; no prices read |

Model names are as written in each prompt at the time. The routing rules
that apply today are in CLAUDE.md.
