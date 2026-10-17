### 2.4 Order of events (PDT, 2026-10-17; from file mtimes, logs, git and the STATE file)

| Time | Event |
|---|---|
| 02:03:59 | Start checks (reports/stage_e23_briefs/start_checks.txt) |
| 02:04:19-02:28:56 | Start suite, detached at nice 10 (1 failed: the known tests/test_h6_rod_run.py since v13) |
| 02:14-02:21 | Inventory and mechanism briefs, lead spec draft (no outcome read) |
| 02:17-02:29 | P1.1: 10 InventoryReader workers (workflow wf_b90fd95b-792) |
| 02:17-02:33 | P1.2: 11 MechanismReader workers (workflow wf_e33ecfd4-8a1) |
| 02:22-02:42 | BookCoder-OpusXHigh: engine, trend regressors (exact vs E.21), T3 reproduction (exact) |
| 02:24-03:08 | TriggerCoder-OpusXHigh: events extraction; W_cf validations identical |
| 02:33-02:37 | Lead: shortlist and data-use map (reports/stage_e23_briefs/shortlist.md), before any outcome read |
| 02:39 | Prereg draft (reports/stage_e23_prereg.md) |
| 02:46-02:58 | TriggerCoder's first-pass events files carried engine exit-side counters (deleted, regenerated; disclosed) |
| 03:09-03:11 | Power table, freeze 3fdd98d7... built |
| 03:11-03:30 | RegReviewer-FableXHigh and CodeReviewer-FableXHigh (APPROVE WITH FIXES each; 0 BLOCKING) |
| 03:25-03:32 | Fixes (R-01..R-04, R-06, C-01, C-04), freeze rebuilt e0d20d0f..., real preconditions dry run passed |
| 03:32:24 | Freeze commit 25bc321 |
| 03:32-03:33 | Registry refused the first id form (nothing written); ids renamed, power rerun, freeze 24dcf4dd..., dry run |
| 03:33:43 | Commit 75874c4 "E.23 freeze (registry ids)" |
| 03:33:45 | Registration r008-E23, N 533 -> 538 |
| 03:33:54-03:34:35 | Discovery read once (marker written 03:33, before any bar; compute 03:33:57-03:34:34) |
| 03:35:27-03:35:29 | Confirmation step once (marker 03:35; 0 survivors; nothing read) |
| 03:36 | VerdictVerifier-FableXHigh spawned |
| 03:38-05:21 | PAUSE: usage limit (the verifier stopped at its start; nothing written) |
| 05:21 | Resumed; verifier resumed by message |
| 05:21:40 | End checks (reports/stage_e23_briefs/end_checks.txt) |
| 05:22:14 | End suite, detached at nice 10 |
| 05:21-05:28 | VerdictVerifier file-based recomputation (recompute_file_based.json 05:28:19); spot_audit.py written 05:37 |
| 05:41:05 | Verifier ends its turn waiting on a background wait for the suite; Verdict line PENDING |
| 05:41:25 | End suite done (1 failed: the known h6 test; 7728 passed) |
| 05:41-07:21 | STALL: the verifier's wait matched its own command line (`pgrep -f`) and never fired; the lead waited idle (context compacted 06:37) |
| 07:21:27 | User resumed the session |
| 07:22 | Lead killed the stuck wait loop; verifier resumed by message |
| 07:22:25-07:22:35 | Spot audit re-simulation from the ext2010 stores (spot_audit.json) |
| 07:24:49 | Verdict set: VERIFIED WITH NOTES, 0 BLOCKING |
| 07:25-about 07:35 | Return, progress entry, STAGES line, final checks, session cost, final commit |
