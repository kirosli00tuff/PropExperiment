### Order of events (2026-10-11, PDT; from date, file mtimes, git, the registry and the logs)

| Time | Event | Source |
|---|---|---|
| 10:21-10:24 | Start checks (all pass; N 480; holdout 0 unlocks) | reports/stage_e20_briefs/start_checks.txt |
| 10:24-10:46 | Start test suite: 7138 passed, 3 skipped, 3 xfailed | pytest_start.out |
| 10:33-10:58 | Part A: 17 product readers at once | partA_returns.log, product_<ROOT>.json mtimes |
| 10:58-11:01 | Part A consolidation; GEX source cleared (T3 registered) | reports/stage_e20_product_summary.md |
| 10:56:48 | GEX sign count (148 rows < 0) after T3's status was fixed | transcript; prereg section 6 |
| 10:40-11:10 | h6_rod built (synthetic only) | h6_build.md |
| 11:12-11:21 | H6Reviewer (1st) stopped on the usage limit, no output | transcript mtime |
| 11:21-15:10 | PAUSE: usage limit | - |
| 15:12-15:30 | H6 review (APPROVE WITH FIXES) | reports/stage_e20_review_h6.md |
| 15:33:45 | H6 prereg last written | mtime (verifier) |
| 15:35:17 | H6 freeze manifest written (22e606f0...) | reports/stage_e20_h6_freeze.json |
| 15:35:53 | Commit 498fd05 "E.20 H6 freeze" | git |
| 15:36:20 | Registration r004-E20H6 (N 480 -> 483) | ledger/trial_registrations.jsonl |
| 15:36:38 | H6 run-once marker | reports/stage_e20_H6_RUN_ONCE.json |
| 15:38:15 | H6 result written (T1, T2, T3 FAIL) | reports/stage_e20_H6_result.json |
| 15:39-15:55 | H6 verification (VERIFIED WITH NOTES) | reports/stage_e20_review.md |
| 15:56-16:18 | Search plan review (BLOCK on PR-1) | reports/stage_e20_review_plan.md |
| 16:19-16:40 | 2010-2019 swap table (PR-1) | backward_swap_table.md |
| 16:21-17:13 | pattern_search built; Step 6 dry check passed | search_build.md, stage_e20_dry_check_step6.md |
| 16:42-16:47 | Plan recheck (BLOCK lifted) | review_plan.md "Recheck" |
| 17:12-17:29 | Search code review (APPROVE WITH FIXES) | reports/stage_e20_review_search_code.md |
| 17:35:42 | First search freeze manifest (66436234...); check --world refused (grid assertion); manifest deleted unregistered | search_check_world.log; rulings section 7 |
| 17:42-17:43 | Search freeze manifest 94ee86b0...; check --world passed | world_check.json |
| 17:43:59 | Registration r005-E20S (E20S-01..45; N 483 -> 528) | ledger/trial_registrations.jsonl |
| 17:44:15-17:52:20 | Search run: panel, nested CPCV, final selection, screen FAIL | search_run.log; reports/stage_e20_search.json |
| 17:53-18:12 | End test suite: 7340 passed, 3 skipped, 3 xfailed | pytest_end.out |
| 17:53-17:54 | ScreenVerifier (1st) stopped on the usage limit, no output | transcript |
| 17:54-20:10 | PAUSE: usage limit | - |
| 20:12 | ScreenVerifier re-spawned; end checks (all pass; N 528) | end_checks.txt |

No 2010-2019 bar was decoded (E20-B1 never registered); no NQ bar was read before 15:36:38; Gate 0's NQ rows were not
read; nothing dated 2024-03-01 or later was read (GEX rows after 2024-02-29 cut at load).
