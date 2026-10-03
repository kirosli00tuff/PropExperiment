# Stage E.12 STATE (resume: read this first; skip finished tasks)

Lead: Opus 5.5 xhigh. Session 8200a1ff-b6ff-45e5-adaa-37850b4a7889. Times America/Vancouver.
Prompt: docs/prompts/STAGE_E.12.md (HEAD at start 8b93e98). Spend session id (Task 4 sets it):
stage-E.12-2026-10-03.

## In force
- Harness: v9 7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9 (commit 4b1e81e, 12:05:01; user decision, closure ruling); v8 452c4a51... (deccd17, 10:02:53); v7 eee8a8b9...
- v2 freeze: commit 9466f2e, manifest sha256 a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b
- Ledger at start: 17400 lines, sha256 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
- acct-1 spent 91.592247 / cap 120.00 (headroom 28.407753); acct-2 spent 124.673761 / cap 125.00
  (headroom 0.326239; after the cap raise to 249.67: headroom 124.996239)
- Holdout: all_ok True, unlocks_logged 0 (start). REGISTRATION.md 0 bytes.
- Start pytest (07:52-08:13, with PYTHONPYCACHEPREFIX): 3 failed, 6317 passed, 2 skipped, 2 xfailed. The 3 are
  test_harness_freeze bytecode tests that fail under PYTHONPYCACHEPREFIX (E.11 saw the same:
  stage_e11_briefs/keyfix_pytest_run1_pycacheprefix.out). Rerun without the prefix: 17 passed
  (pytest_start_harness_rerun.out). Start = 6320 passing; END SUITE RUNS WITHOUT THE PREFIX.
- Purchase done 11:57: 1,543 chunks, $133.723742 (acct-1 $26.797773 -> spent 118.390020/120; acct-2 $106.925969 -> spent 231.599730/249.67); ledger 23,630 lines sha256 e5862e3d...; billed = quoted on every chunk; 0 chunks in 2024-03..2025-03; holdout all_ok, 0 unlocks (postpurchase_checks.txt).
- Stores: all 28 built (15 under v8, 12 held -> built under v9 with 24 ruled bars, NG owned).
- Phase-1 build 12:09-12:14 (v9 + freeze a647cd06...): 28 vehicles; MES REFUSED (TradeDateMismatch, 3 rows, first label 2020-03-30 booked 2020-03-31) -> P-1a: g17_mes, k8_flight_ret, k8_flight_tail excluded; signals covered 64; MBT S_X 2024-01-02 (D4) -> 41 dates, all rows lost to warm-up (no MBT rows); c/sigma 81 pairs, 81 admissible, 0 dropped; constants fp 013fa5a4...; inputs fp 969d3b7e...
- GATE 0 LIST REGISTERED 12:15:26 (before any statistic): reports/stage_e12_gate0_list.json sha256 53e7ef576feba9959360b52a633b793175bce98d62a839fefa0f41baf19fa8ea; |A| 192, |B| 81, 273 entries in ledger/ml_v2_config_ledger.jsonl. New program N = 198 + 273 = 471.
- GATE 0 RAN ONCE 12:15:41-12:15:54: VERDICT FAIL (0 passing pairs). Best NG h60: mean gross 5.569 ticks vs c 1.713 (3.25c), t_B 2.51, p 6.2e-3 vs Holm 1.83e-4 (rank 1/273), 518 trades; NG hF 7.9c t 2.33. No pair t>=3. Pooled B mean g -0.717 vs cost 2.260 ticks, t 0.28, 39,997 trades. Smallest A p 0.015 (g07_range hF). reports/stage_e12_gate0.json sha256 c0af61c2f7c94ac188d4eaedcfb9d8b224947fa299e82aeea058769d99414806; .md 363c5676...; ledger unchanged by the run (aacca512...).
- Gate0Verifier done 12:37: VERIFIED WITH NOTES (0 blocking, 0 should fix, 5 notes), rulings Part 2 written.
- End pytest 12:17-12:39: 6 failed (ALL the real-ledger guard, tripped by the concurrent ext-2010 quote appending to the ledger), 6499 passed. RERUN the 3 files after the quote finishes.
- Task 7: holdout-2 quote done ($31.984359, 364 chunks); ext-2010 running (ETA ~13:25).
- Return: briefs/return_draft.md + assemble_return.py + ret_delegation.md + ret_open_choices.md + progress_entry.md; at the end: end checks, rerun guard tests, cost, assemble, STAGES line, progress entry, commit.

## Lead pre-registration decisions (Task 0, before any spawn; go into the freeze)
- P-1 Phase-1 roots available to features: the phase-1 price paths bought (or owned: NG) plus MES
  (its frozen confirmation store). The owned MCL/MGC/MHG micro stores are not price paths and are
  never read (V2.1). A signal that is not own_path_only and reads a root outside that set is a
  coverage exclusion for phase 1 (V2.3's rule: cannot be computed -> no feature), logged by name.
- P-2 Gate 0 list rule: A = every panel signal x 3 horizons (rows of admissible pairs; a test with
  < 2 dates has t NaN, p 1, counted); B = every admissible (product, horizon) pair at tau 0.167.
  Registered in ledger/ml_v2_config_ledger.jsonl before computation; list JSON hashed into STATE.
- P-3 S_X per price path: D4's frozen start rule (volume-only read of ts_event, volume,
  trade_date; never a price); MES fixed at D4's 2020-02-03; each root's bars cut at S_X.
- P-4 Subset rule application: tier 1 = vehicle 2026 Jan-Aug ADV >= median of the 28; within a
  tier c/sigma_proxy ascending (c = RT_X $, sigma_proxy = CME maintenance margin, vehicle front
  month); overall rank = tier 1 then tier 2. Pass 1: the 7 cluster-best exposures in rank order
  (literal reading); pass 2: all remaining by rank. A pick sits on acct-1 if quote x 1.03 fits its
  remaining headroom, else acct-2 if it fits there, else skipped. NG costs $0 (owned store).
- P-5 Release-window rule (V23 item 11): an entry in product p whose fill lies in
  [r - 5 min, r + 30 min) of a scheduled release r that concerns p is refused if open
  lot-equivalents including the entry would exceed half the tier's maximum position size.
- P-1a MES contingency: if the frozen loader refuses MES's confirmation store, MES is unavailable
  (its signals are coverage exclusions, logged); a refused price-path store stops the run.
- P-6 N_program = 198 (E.9; E.10 and E.11 added nothing: V21, C-08).

## Tasks
| Task | Status | Start | End | Artifacts |
|---|---|---|---|---|
| 0 Startup | done | 07:51 | 08:06 | reports/stage_e12_briefs/start_checks.txt, pytest_start.out, checks.sh |
| 1 V23 design text (lead) | done (V23 applied, FROZEN header, K9, 150K, reset, proxy switch, P-rules) | 08:10 | 08:56 | docs/STAGE_E_ML_V2_DESIGN.md |
| 1 V23Coder-OpusXHigh | done (791 passed, 2 xfailed; gross default, tau 0.167, P-5, K9 signal, canaries, 150K tests) | 08:06 | 08:43 | briefs/v23coder_report.md |
| 1b Phase1Coder-OpusXHigh | done 09:01 (38 phase1 tests pass; package ml_route_v2/phase1/); follow-up done (42 phase1 tests): MES refusal contingency P-1a | 08:06 | 08:40 (follow-up 08:42-08:45) | briefs/phase1coder_report.md |
| 2a MarginFetch-OpusHigh | done (live CME 403 per its terms; 25/34 stale Wayback only; 5 vehicles none) -> LEAD SWITCHED WHOLE RANKING TO FROZEN E|m_1| (V23 item 3 fallback; design V2.1 step 6) | 08:06 | 08:25 | reports/stage_e12_cme_margins.json, briefs/marginfetch_log.md, briefs/margin_pages/ |
| 2b TopstepFacts-OpusMedium | done (MLL $4,500 confirmed; 150K tiers 3/4/5/10/15 from image; reset/Combine prices; B2F $829) -> lead applied to ml_route_v2/account.py ACCOUNT_150K and design V2.0/V2.8/V2.9; PAYOUT_RESET_DELAY_DATES=2 PENDING (constants.py owned by V23Coder) | 08:26 | 08:29 | reports/stage_e12_topstep_150k.md, briefs/topstepfacts_log.md, briefs/topstep_pages/ |
| 2c CalendarBuilder-OpusHigh | done (240 dates, 884 CAL rows, no uncovered span, cross-checks exact; lead ruled: unscheduled FOMC and cancelled 2020-03-18 excluded) | 08:06 | 08:54 | reports/stage_e12_ec_k9_2019_2024.json/.md, briefs/calendarbuilder_log.md, briefs/calendar_pages/ |
| 4 KeyCapFix-OpusXHigh (prep in worktree ../PropExperiment-e12-v8, branch e12-v8, uncommitted) | done (cap 249.67, key strip, E.12 block cap 0.00, --account/--roots/--training-window/interlock, quote-only holdout2/extension, 64 new tests; lead accepts credit_left = cap headroom) | 08:30 | 09:03 | briefs/keycapfix_report.md (sec 5: manifest commands) |
| 3 Freeze: FreezeReviewer 0 BLOCKING / 4 SHOULD FIX (applied) / 9 NOTE; manifest rebuilt: 91 files sha256 a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b; COMMIT 9466f2e 'ML route v2 freeze' at 09:25:53 | done | 08:56 | 09:26 | reports/stage_e12_ml_v2_freeze.json, reports/stage_e12_review.md, reports/stage_e12_rulings.md | reports/stage_e12_ml_v2_freeze.json |
| 4 v8: diff applied 09:28; F-4 verified; E12 session cap 137.73; manifest 452c4a51...; 241 harness tests pass; COMMIT deccd17 10:02:53 | done | 09:28 | 10:03 | reports/stage_e2b_harness_freeze.json, briefs/pytest_v8.out |
| 5 Quote done 09:58 (1601 chunks, 0 failed, $139.340240; ledger 19001 lines); ranking: ALL 28 selected, $133.723742 (acct-1 $26.797773: NQ GC 6E ZL MBT LE HE; acct-2 $106.925969: 20 roots; NG owned); ranking sha256 43f80e90bc26ce5d4997e88e9aaa1fab32c5884bc7a9ea4b4b0fadd4d5422aaf; BUY running in 4 processes from 10:06 | running | 09:27 | | reports/stage_e12_quotes_phase1.json, reports/stage_e12_ranking.json, briefs/buy_*.log |
| 6 DONE (see In force). Stores: UB, CL, ZT built (v8 builder). HELD FOR THE LEAD by the frozen builder (L-3: deep closure bars, no ruling path in code): NQ (6 bars 15:29/16:59 CT, 2020-03-30..07-01), 6A (1 bar 2020-06-30 16:59). GATE 0 NOT RUN: phase1 build must NOT run until the user rules (a: harness v9 enumerated keep-and-flag ruling path; b: drop held roots per F-3; c: wait). Stop condition: guardrail (harness beyond v8) + irreversible either-way (Gate 0 once). USER DECIDED about 10:41 (AskUserQuestion): 'Harness v9: keep and flag'. V9Coder-OpusXHigh spawned in worktree ../PropExperiment-e12-v9 (detached deccd17). Plan: finish buys, attempt all stores under v8, write reports/stage_e12_closure_rulings.json listing exactly the held deep bars, v9 manifest+commit, build held stores, then phase1 build/register/run under v9. Fable check of v9 folded into Gate0Verifier. V9Coder done ~11:00: loader check PASSES (fixtures, real equity/FX calendars); worktree diff data/step2_store.py (+119) and screening/harness_freeze.py (+1 FROZEN_INPUTS line), tests/test_e2b_step2_store_v9.py (22 pass); report briefs/v9coder_report.md. Held so far: NQ 6E 6A 6B 6N. | running | 10:21 | | reports/step2/bars_*.json, briefs/store_builds.log, briefs/build_ready_stores.py |
| 7 Later-phase quotes: holdout-2 $31.984359 (364 chunks); 2010 extension $213.942963 (27 roots, 292 unpriced pre-listing months) | done | 12:15 | 13:16 | reports/stage_e12_quotes_holdout2.json, _ext2010.json |
| 8 Gate0Verifier-FableXHigh: VERIFIED WITH NOTES | done | 12:17 | 12:37 | reports/stage_e12_review.md Part 2 |
| 9 Return (reports/E.12_RETURN.md), progress.md entry, STAGES.md line, end checks (briefs/end_checks.txt), final commit | done | 12:37 | 13:20 | |

## Next
- After Phase1Coder follow-up 2 + full suite: delete uncommitted manifest, rebuild, rerun ml_v2 tests, freeze commit 'ML route v2 freeze'. Rulings: reports/stage_e12_rulings.md.
- NOTE (08:53): earlier STATE times were lead guesses; corrected from file mtimes and agent durations. ml_v2 suite 08:48-08:52: 795 passed, 2 xfailed.
- Lead done: PAYOUT_RESET_DELAY_DATES=2, N alias removed (pipeline.py), synthetic.py tau comments, V2.7 gross note, freeze builder reports/stage_e12_briefs/build_v2_freeze.py (universe check OK 28/28).
- Lead TODO before freeze: K9 design text after CalendarBuilder; header FROZEN; ml_v2 suite (pytest_mlv2_prefreeze.out); FreezeReviewer; full suite.
- Ranking script ready: reports/stage_e12_briefs/rank_phase1.py (--proxy em1 default; dry run OK, 14 tier-1).
Wave 1 running. On the first free slot: TopstepFacts; then KeyCapFix. Then Task 3 freeze.

## Open choices so far (for return section 6)
1. Real-data loader (ml_route_v2/phase1) built and frozen before data: not named in the prompt, needed so Gate 0 code is frozen before any read (Phase1Coder).
2. P-1 coverage rule, P-1a MES contingency, P-2 list rule (dead tests kept, conservative), P-3 S_X via D4 (volume-only research read), P-4 subset application (literal pass 1, 3% reserved per pick), P-5 release window counts the entry, P-6 N 198 from stage records (no machine ledger).
3. Proxy switch to E|m_1| for the whole ranking (CME 403 + ToS; 5 vehicles with no 2026 figure).
4. 150K tier boundaries: lower tier at exact $2,000/$3,000/$4,500; $1,500 inclusive. Reset delay 2 (lower bound); reset cost reported at both paths; Back2Funded not modelled.
5. EC-K9: unscheduled FOMC actions and cancelled 2020-03-18 excluded (decision_time rule).
6. Freeze review run BEFORE the freeze commit (so fixes did not change a Gate 0 rule after the commit); first manifest deleted uncommitted and rebuilt once.
7. v8 prepared in a git worktree in parallel; fresh quote run before the v8 commit (quote-only needs no preflight) so the session cap could go into v8 as the prompt requires.
8. Freeze commit also holds rank_phase1.py and build_v2_freeze.py (hashed by / producing the manifest).
9. pytest runs without PYTHONPYCACHEPREFIX (bytecode tests); start baseline 6320.
10. Buy run in 4 parallel processes over disjoint roots (E.5's 9.6 s/chunk x 1,543 chunks = 4 h serial); caps cannot be crossed by races (planned $133.72 < session cap $137.73).
11. Phase-1 subset = all 28 (the rule's result; the planning guess was 8): phase 2 has no training-window item left.
12. STATE times before 08:53 were corrected from file mtimes.

## FINAL (13:20)
Stage complete. Gate 0 FAIL (verified). Commits: 9466f2e freeze, deccd17 v8, 4b1e81e v9, then the stage commit. Nothing pending. Worktrees ../PropExperiment-e12-v8 and -v9 can be removed by the user.
