
## 2026-10-11 — Stage E.20: pattern search with per-product research; H6 FAIL (T1-T3), search screen FAIL; N = 528

Prompt docs/prompts/STAGE_E.20.md (V33 item 5, V34-V37). Lead Opus 5.5 xhigh, ultracode on, session 2b0cd60b. Return:
reports/E.20_RETURN.md.

- **Part A:** 17 ProductReader-<ROOT>-OpusHigh at once (10:33-10:58), one shared brief, shared sources assigned once.
  157 evidence rows; only H6's historical equity figure clears 1.5 x a D8 round trip; 7 features proposed, 0 accepted.
  F6 cut: 34 of the 67-signal library kept, 33 dropped (legs outside the 17 roots; 2010-2019 calendars absent, incl.
  g13-g15 and k9_anncday; k2_fomc_mto after the plan review). GEX source cleared (E.14's copy), so T3 ran.
- **H6** (rest-of-day to last-half-hour momentum on NQ at MNQ cost, 2020-06..2024-02; freeze 22e606f0..., commit
  498fd05; registered r004-E20H6 as E20H6-T1..T3, N 480 -> 483): T1 FAIL (893 trades, gross 1.25 ticks vs 4.08 cost,
  t_B -0.53, p 0.70, Sharpe -0.27); T2 FAIL (446, -3.27, -0.95, 0.83, -0.48); T3 FAIL (134, -3.52, -0.38, 0.65, -0.19);
  no Holm rejection. Overlap with the paper's sample (2019-05..2020-05, descriptive): positive (T1 t 1.16). Fable
  reproduced every trade (VERIFIED WITH NOTES).
- **Search** (ML route v2 net pipeline on 17 roots, t4 = F_X - 60, rod_ret and rod_absratio; plan frozen after a Fable
  BLOCK on the 2010-2019 table swaps (fixed: swap table + Step 6 dry check); pattern_search composes the frozen code;
  freeze 94ee86b0...; registered r005-E20S as E20S-01..45, N 483 -> 528): SCREEN FAIL: median-path t -1.33, PBO 0.60,
  net Sharpe -0.83, DSR(528) about 0; all 45 configurations negative out of sample (best -0.33). No B1 freeze or
  backward read. Fable verified the screen (VERIFIED) and reviewed the code (no leak).
- **Guardrails:** holdout all_ok, 0 unlocks, start and end; REGISTRATION.md 0 bytes; spend ledger unchanged (36,402
  lines, 034a454b...); harness v12 unchanged; v2, E.14, E.16, E.18 freezes verify; no 2010-2019 bar decoded; nothing
  dated 2024-03-01 or later read; no TopstepX call; no purchase; no push. Suites: start 7138 passed, end 7340 passed
  (+85 h6_rod, +117 pattern_search).
- **Pauses:** two usage-limit pauses (11:21-15:10, 17:54-20:10); two Fable workers re-spawned fresh after them.
- **For the user:** both lines are closed; no forward read, no holdout-2, no Combine. Recommended next: the AiTrader
  readout first (V33 item 3), with stopping the futures intraday program as the default if it does not pass.

### Session cost

### Final ETA table

| Task | Owner | Model | Effort | Start | End | Time (min) | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Start checks + start suite | lead | opus | xhigh | 10:21 | 10:46 | 25 |  | done; suite 7138 passed |
| 1 Part A readers x17 | ProductReader-<ROOT>-OpusHigh | opus | high | 10:33 | 10:58 | 25 | 294,770,167 | done (all 17 at once) |
| 5a Code map (workflow, 5 agents) | CodeMapper-*-OpusHigh | opus | high | 10:42 | 10:49 | 7 | 22,376,477 | done (lead's addition) |
| 1c Consolidation | lead | opus | xhigh | 10:58 | 11:01 | 3 |  | done |
| 2 H6 code | H6Coder-OpusXHigh | opus | xhigh | 10:40 | 11:10 | 30 | 31,068,850 | done; follow-up 15:31-15:33 |
| 2 H6 review (1st) | H6Reviewer-FableXHigh | fable | xhigh | 11:12 | 11:21 | 9 | 3,847,856 (both spawns) | stopped: usage limit |
| PAUSE usage limit | - | - | - | 11:21 | 15:10 | 229 |  | excluded from work time |
| 2 H6 review (2nd) + fixes | H6Reviewer-FableXHigh | fable | xhigh | 15:12 | 15:34 | 22 | in the row above | APPROVE WITH FIXES; fixed |
| 3 H6 freeze, commit, register, evaluate | lead | opus | xhigh | 15:34 | 15:38 | 4 |  | done; T1-T3 FAIL |
| 4 H6 verify | VerdictVerifier-FableXHigh | fable | xhigh | 15:39 | 15:55 | 16 | 3,351,142 | VERIFIED WITH NOTES |
| 5 Plan review | PlanReviewer-FableXHigh | fable | xhigh | 15:56 | 16:18 | 22 | 3,872,464 | BLOCK on PR-1; recheck 16:42-16:47 lifted it |
| 5 Swap table (PR-1) | BackwardTables-OpusXHigh | opus | xhigh | 16:19 | 16:40 | 21 | 19,665,357 | done (lead's addition) |
| 6 Build pattern_search + dry check | SearchCoder-OpusXHigh | opus | xhigh | 16:21 | 17:13 | 52 | 73,838,678 | done; fixes 17:29-17:42 |
| 6b Code review | SearchReviewer-FableXHigh | fable | xhigh | 17:12 | 17:29 | 17 | 2,774,580 | APPROVE WITH FIXES (lead's addition) |
| 7 Freeze, check --world, register, search, screen | lead | opus | xhigh | 17:34 | 17:52 | 18 |  | SCREEN FAIL |
| 7 Screen verify (1st) | ScreenVerifier-FableXHigh | fable | xhigh | 17:53 | 17:54 | 1 | 4,340,355 (both spawns) | stopped: usage limit |
| 10 End suite (detached) | - | - | - | 17:53 | 18:12 | 19 |  | 7340 passed |
| PAUSE usage limit | - | - | - | 17:54 | 20:10 | 136 |  | excluded from work time |
| 7 Screen verify (2nd) | ScreenVerifier-FableXHigh | fable | xhigh | 20:12 | 20:25 | 13 | in the row above | see section 5 |
| 8-9 B1 freeze, register, evaluate, verify | - | - | - |  |  |  |  | not run: screen failed |
| 10 End checks, cost, return, progress, commit | lead | opus | xhigh | 20:12 | 20:25 | 13 |  | done |
| Whole stage | lead + workers | | | 10:21 | 20:25 | 239 work (+365 paused; wall 604) | 619,238,168 | initial estimate: about 12 h 40 min to 23:00 on a fail; actual work 3 h 59 min |

### Tokens per model (transcripts; reports/stage_e20_briefs/make_cost.py)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 3,700 | 395,813 | 15,995,270 | 1,791,614 | 18,186,397 |
| claude-opus-5-5 | 5,286 | 2,366,659 | 588,839,967 | 9,839,859 | 601,051,771 |
| all | 8,986 | 2,762,472 | 604,835,237 | 11,631,473 | 619,238,168 |

Delegation share: lead 159,332,242 (25.7%), workers 459,905,926 (74.3%). By model: claude-fable-5-1 2.9%, claude-opus-5-5 97.1%

These are token counts, not plan-credit percentages; the /usage meter is the user's to read.

### Worker spawns (name, model, effort, tokens)

| Spawn (name) | Model | Effort | First (PDT) | Last (PDT) | Tokens |
|---|---|---|---|---|---|
| lead (Opus 5.5) | claude-opus-5-5 | xhigh | 10:21 | 20:25 | 159,332,242 |
| ProductReader-GC-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:53 | 24,482,063 |
| ProductReader-ZT-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:47 | 13,051,890 |
| ProductReader-ZS-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:48 | 13,648,311 |
| ProductReader-6E-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:51 | 16,531,694 |
| ProductReader-CL-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:54 | 22,900,247 |
| ProductReader-UB-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:45 | 10,529,386 |
| ProductReader-TN-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:44 | 9,575,403 |
| ProductReader-ZC-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:56 | 23,882,817 |
| H6Reviewer-FableXHigh | claude-fable-5-1 | xhigh | 15:12 | 15:30 | 2,865,540 |
| ProductReader-ZN-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:57 | 18,955,473 |
| ProductReader-HE-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:50 | 16,924,223 |
| BackwardTables-OpusXHigh | claude-opus-5-5 | xhigh | 16:19 | 16:39 | 19,665,357 |
| ProductReader-ZF-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:50 | 14,707,873 |
| SearchReviewer-FableXHigh | claude-fable-5-1 | xhigh | 17:12 | 17:28 | 2,774,580 |
| H6Coder-OpusXHigh | claude-opus-5-5 | xhigh | 10:40 | 15:33 | 31,068,850 |
| H6Reviewer-FableXHigh | claude-fable-5-1 | xhigh | 11:12 | 11:20 | 982,316 |
| ProductReader-ZL-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:47 | 12,659,465 |
| ScreenVerifier-FableXHigh | claude-fable-5-1 | xhigh | 17:53 | 17:56 | 990,468 |
| VerdictVerifier-FableXHigh | claude-fable-5-1 | xhigh | 15:38 | 15:55 | 3,351,142 |
| ScreenVerifier-FableXHigh | claude-fable-5-1 | xhigh | 20:12 | 20:24 | 3,349,887 |
| SearchCoder-OpusXHigh | claude-opus-5-5 | xhigh | 16:21 | 17:42 | 73,838,678 |
| ProductReader-ZB-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:48 | 14,509,703 |
| PlanReviewer-FableXHigh | claude-fable-5-1 | xhigh | 15:56 | 16:46 | 3,872,464 |
| ProductReader-RTY-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:55 | 22,003,014 |
| ProductReader-NG-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:52 | 17,217,404 |
| ProductReader-NQ-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:54 | 17,508,680 |
| ProductReader-LE-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:57 | 25,682,521 |
| CodeMapper-clock-panel-signals-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:47 | 3,601,316 |
| CodeMapper-leakage-tests-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:48 | 4,562,069 |
| CodeMapper-models-cpcv-selection-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:47 | 3,255,001 |
| CodeMapper-sizing-sim-engine-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:48 | 6,028,124 |
| CodeMapper-phase1-world-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:47 | 4,929,967 |
