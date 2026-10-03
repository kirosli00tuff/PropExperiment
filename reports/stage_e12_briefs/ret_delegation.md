One row per spawn (times PDT from the transcripts; tokens = input + output + cache read + cache creation,
from reports/stage_e10_briefs/cost.py over this session's subagent transcripts; never estimated).

| Agent (description) | Agent file | Model | Effort | Start-end | Wall | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|
| Phase1Coder-OpusXHigh | worker-xhigh | opus | xhigh | 08:07-09:20 | 73 min span (3 rounds) | 40,564,718 | done: ml_route_v2/phase1, 50 tests; not in the prompt's plan (the real-data entry point Gate 0 needed before the freeze); follow-up 1 (MES contingency P-1a, 08:42-08:45) and follow-up 2 (review F-2, F-3, F-8, 09:16-09:20) by SendMessage |
| V23Coder-OpusXHigh | worker-xhigh | opus | xhigh | 08:07-08:44 | 37 min | 31,107,511 | done: V23 defaults, release-window rule, K9 signal, canaries; ml_v2 704 -> 791; edited targets.py, simulate.py, test_ml_v2_cpcv.py outside its list (ruled) |
| MarginFetch-OpusHigh | worker-high | opus | high | 08:07-08:26 | 19 min | 5,975,264 | done: live CME 403 per its terms; stale Wayback for 25/34; ranking switched to E\|m_1\| |
| CalendarBuilder-OpusHigh | worker-high | opus | high | 08:07-08:56 | 48 min | 25,275,373 | done: EC-K9 2019-2024, 240 dates, 884 source rows, cross-checks exact |
| TopstepFacts-OpusMedium | worker-medium | opus | medium | 08:26-08:29 | 3 min | 2,130,037 | done: 150K MLL, scaling plan from the image, prices |
| KeyCapFix-OpusXHigh | worker-xhigh | opus | xhigh | 08:30-09:02 | 33 min | 20,723,465 | done in a git worktree in parallel with the freeze (the prompt had Task 4 after Task 3; the commit order was kept) |
| FreezeReviewer-FableXHigh | worker-xhigh | fable | xhigh | 08:57-09:15 | 18 min | 1,899,346 | done before the freeze commit: 0 blocking, 4 should fix, 9 notes; its commit-order check moved to Gate0Verifier |
| V9Coder-OpusXHigh | worker-xhigh | opus | xhigh | 10:41-10:55 | 14 min | 8,016,802 | done in a second worktree: the v9 closure-ruling path after the user's decision (not in the prompt's plan); loader check passed |
| Gate0Verifier-FableXHigh | worker-xhigh | fable | xhigh | 12:17-12:37 | 20 min | 4,383,294 | done: VERIFIED WITH NOTES (273 tests to 1e-13), plus the v9, MES, MBT and order-of-events checks |

Fable ran two checks, as the prompt's usage note asks (the v9 review was folded into the Gate 0
verification rather than a third Fable spawn). At most four workers ran at once.
