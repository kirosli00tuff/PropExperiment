Wall clock: 00:26 to 03:56 PDT, 3:30 of work; no pause and no usage-limit wait.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| # | Task / spawn | Owner | Model | Effort | Start | End | Time [estimate] | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Startup, start checks, briefs | lead | opus | xhigh | 00:26 | 00:38 | 0:12 [0:32] | lead | done |
| 1 | Probe 2012 (Part A) | CalendarProbe-OpusHigh | opus | high | 00:34 | 01:32 | 0:58 [~1:00] | in row 1b | done; rule does not fire (ruled 01:36) |
| 1b | Release calendars NGS, WPSR, FOMC (Part B) | CalendarProbe-OpusHigh | opus | high | 01:32 | 03:06 | 1:34 [~2:00] | 63,037,188 (A+B) | done; 1 WPSR time unsourced |
| 2a | Equity, then rates, FX, grains | CalendarBuilder-Equity-OpusHigh | opus | high | 00:34 | 02:28 | 1:54 [~3:00] | 54,066,402 | done; 0 unsourced |
| 2b | Energy, metals, full sessions | CalendarBuilder-Commod-OpusHigh | opus | high | 00:36 | 01:33 | 0:57 [~2:30] | 27,839,578 | done; 0 unsourced |
| 3 | GEX terms, fetch, timing, count | lead | opus | xhigh | 00:38 | 01:50 | 1:12 [~0:40] | lead | done; C2 STOPPED 01:34 (deviation: C2 stops, Tasks 6-7 shrink) |
| 4a | Harness v10 code | V10Coder-OpusXHigh | opus | xhigh | 00:38 | 01:29 | 0:51 [~2:30] | 56,369,890 | done |
| 4a' | v10 merge, fresh quotes ES and C1, cap | lead | opus | xhigh | 01:29 | 01:56 | 0:27 [in 4c] | lead | done; quotes moved here from Task 6 (open choice 19) |
| 4b | C1 code | C1Coder-OpusXHigh | opus | xhigh | 01:29 | 02:48 | 1:19 [~2:00] | 62,360,972 | done; one 2-minute follow-up |
| 4c | Calendars into v10, loader fixes, manifest, full suite, freeze text | lead | opus | xhigh | 02:15 | 03:06 | 0:51 [~0:45] | lead | done; full suite 6737 passed |
| 4d | Freeze review | FreezeReviewer-FableXHigh | fable | xhigh | 03:06 | 03:26 | 0:20 [~1:00] | 7,044,911 | APPROVE WITH FIXES |
| 4e | Rulings, fixes, two commits | lead | opus | xhigh | 03:26 | 03:29 | 0:03 [~0:20] | lead | done; dc93e9b, 1680982 |
| 5 | M1 fit and q | lead | opus | xhigh | 03:29:54 | 03:29:57 | 0:00 [~0:20] | lead | done; exact |
| 6 | Quotes (in 4a'), no registration, no purchase; report | lead | opus | xhigh | 03:00 | 03:08 | 0:08 [~0:30] | lead | done; nothing bought |
| 7 | C2 result STOPPED; C1 not evaluated | lead | opus | xhigh | 03:08 | 03:27 | (parallel) [~0:30] | lead | done |
| 8 | Verification | VerdictVerifier-FableXHigh | fable | xhigh | 03:30 | 03:39 | 0:09 [~1:00] | 3,488,335 | all MATCH |
| 9 | Rulings, end checks, end suite, return, progress, commit | lead | opus | xhigh | 03:39 | 03:56 | 0:17  [~0:40] | lead | done; end suite 6740 passed |
| Total | Stage E.14 | lead + 7 spawns | | | 00:26 | 03:56 | 3:30 [estimate ~10:19, to ~10:45] | lead 103,133,858; workers 274,207,276; total 377,341,134 | no pause; no usage-limit wait |

### Tokens per model (this session's transcript and its 7 subagent transcripts, 07:20Z to 2026-10-05T11:30:00Z)

Computed with reports/stage_e10_briefs/cost.py (final usage per streamed message); raw output
reports/stage_e14_briefs/cost_raw.txt. Token counts, not plan-credit percentages.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,924 | 138,039 | 9,893,214 | 500,069 | 10,533,246 |
| claude-opus-5-5 | 2,408 | 1,338,038 | 357,781,371 | 7,686,071 | 366,807,888 |
| all | 4,332 | 1,476,077 | 367,674,585 | 8,186,140 | 377,341,134 |

Per spawn: CalendarProbe-OpusHigh (worker-high, opus high) 63,037,188; CalendarBuilder-Equity-OpusHigh (worker-high, opus high) 54,066,402; CalendarBuilder-Commod-OpusHigh (worker-high, opus high) 27,839,578; V10Coder-OpusXHigh (worker-xhigh, opus xhigh) 56,369,890; C1Coder-OpusXHigh (worker-xhigh, opus xhigh) 62,360,972; FreezeReviewer-FableXHigh (worker-xhigh, fable xhigh) 7,044,911; VerdictVerifier-FableXHigh (worker-xhigh, fable xhigh) 3,488,335.

Delegation share: lead 103,133,858 (27.3%), workers 274,207,276 (72.7%). By model:
claude-fable-5-1 10,533,246 (2.8%), claude-opus-5-5 366,807,888 (97.2%).
