Tokens come from the transcripts, each message at its final usage, counted by reports/stage_e26_briefs/cost.py over
session 488b039c from 2026-10-22T02:19:00Z (19:19 PDT on 10-21) to 11:41:40Z (04:41:40 PDT on 10-22). Output:
reports/stage_e29_briefs/work/lead/cost_raw.txt. The few calls after that (assembly, progress entry, commit and the
closing reply) are not counted. These are token counts, never estimates; plan-meter percentages are the user's
reading.

Wall clock: 10-21 19:19 to 10-22 04:41 = 9 h 22 min. Two pauses are not work: 19:37 to 21:53 (usage limit, reboot
at 20:42; 2 h 16 min) and 22:18 to 02:41 (usage limit, reboot at 22:21; 4 h 23 min). Work: 19:19 to 19:37,
21:53 to 22:18 and 02:41 to 04:41, 2 h 43 min in total.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 526 | 342,679 | 40,635,492 | 1,752,157 | 42,730,854 |

Per spawn:
- CorrMeasurer-OpusHigh: worker-high, opus, high: 1,514,154 (in 34, out 18,754, cache read 1,398,076, cache
  creation 97,290).
- BasketCoder-OpusXHigh: worker-xhigh, opus, xhigh: 8,094,423 (in 92, out 102,245, cache read 7,526,829, cache
  creation 465,257); two parts, both cut by the usage limit.
- BasketReviewer-OpusXHigh: worker-xhigh, opus, xhigh: 8,589,743 (in 108, out 71,931, cache read 8,047,727, cache
  creation 469,977).
- Lead (Opus 5.5, high): 24,532,534 (in 292, out 149,749, cache read 23,662,860, cache creation 719,633).

Delegation share: lead 24,532,534 (57.4%), workers 18,198,320 (42.6%). By model tier, 100% Opus 5.5: Fable is not
on the Pro plan, and no Sonnet or Haiku work was routed. Cache reads are 95.1% of all tokens.

Final ETA table (actuals). No initial estimate table was printed (OC-18). The baseline is the prompt's schedule,
19:19 to the 23:30 return, 4 h 11 min.

| # | Task | Owner | Model | Effort | Start | End | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|---|---:|---|
| 1 | Start checks | lead | opus | high | 19:19 | 19:20 | 1 min | lead | done |
| 2 | Plan, three briefs, Z3 declaration | lead | opus | high | 19:20 | 19:26 | 6 min | lead | done; declaration mtime 19:24:16 (OC-16) |
| 3 | Reference correlations | CorrMeasurer-OpusHigh | opus | high | 19:25:55 | 19:28:58 | 3 min | 1,514,154 | done |
| 4 | Basket module and runner, part 1 | BasketCoder-OpusXHigh | opus | xhigh | 19:25:51 | 19:37:04 | 11 min | 8,094,423 (both parts) | cut by the usage limit; no tests, no cells |
| P1 | **usage-limit pause; reboot 20:42** | | | | 19:37 | 21:53 | 2 h 16 min | | excluded |
| 5 | Coder resumed (reduced scope): tests, grid launch | BasketCoder-OpusXHigh | opus | xhigh | 21:54:37 | 22:02:15 | 8 min | (in 4) | cut again; 9 tests pass; grid launched 21:59:32 |
| 6 | Return skeleton; lead waits on the grid | lead | opus | high | 21:53 | 22:18 | 25 min | lead | done |
| P2 | **usage-limit pause; reboot 22:21 killed the grid at 139 records** | | | | 22:18 | 02:41 | 4 h 23 min | | excluded |
| 7 | Grid run restart (OC-12) | lead, detached | | | 02:41 | 02:51:55 | 11 min | lead | rc 0; 96 run, 139 kept |
| 8 | Collect, tables, final tests | lead | opus | high | 02:51 | 02:53 | 2 min | lead | 11 passed |
| 9 | Independent review (Z5) | BasketReviewer-OpusXHigh | opus | xhigh | 02:53:26 | 03:13:06 | 20 min | 8,589,743 | GO WITH FIXES, 0 BLOCKING |
| 10 | Synthesis drafts | lead | opus | high | 02:54 | 03:15 | 21 min | lead | done, alongside 9 |
| 11 | Grid confirmation of 211 records (SHOULD FIX 7) | lead, detached, 6 processes | | | 03:13 | 04:19 | 66 min | lead | rc 0; 0 of 470 moved |
| 12 | Vanish table (SHOULD FIX 8), text checks, return sections | lead | opus | high | 04:19 | 04:30 | 11 min | lead | four statements corrected |
| 13 | Full suite | lead, detached | | | 04:20:58 | 04:41:00 | 20 min | lead | 1 known failure, 8,090 passed |
| 14 | End checks, cost, assembly, progress, STAGES, commit | lead | opus | high | 04:41 | commit | | lead (to 04:41:40) | done |
| | **Cumulative** | | | | 19:19 | 04:41 | work 2 h 43 min (pauses 6 h 39 min excluded) | **42,730,854** (lead 24,532,534; workers 18,198,320) | baseline 4 h 11 min to the 23:30 return; the calendar end moved to 10-22 through the pauses (OC-11) |
