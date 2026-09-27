# Stage E.3 STATE (K2 rates: code, audit, freeze, screen)

Lead: Opus 5.5 (xhigh). Session started 2026-09-26 23:35 PDT. All times America/Vancouver (PDT).
Harness sha256 cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45.
On resume: read this file first; skip finished tasks.

## Task status

| Task | Status | Start | End | Artifacts | Notes |
|---|---|---|---|---|---|
| 0 Startup | done | 23:35 | 23:47 | this file | start checks passed 23:35-23:40 (tree clean at 9741e63, holdout all_ok 0 unlocks x2, REGISTRATION 0 bytes, check_frozen ALL_OK, preflight OK); suite started 23:40 in background |
| 1 Member specs | done | 23:40 | 23:52 | reports/stage_e3_member_specs.md | 22 lead readings L-01..L-22; strategy/members/k2/__init__.py created empty 23:52 |
| 1b C9 auction XML check | done | 23:47 | 00:05 | reports/stage_e3_auction_xml_check.json/.md | AuctionXmlChecker-OpusMed (worker-medium, opus); brief reports/stage_e3_briefs/auction_xml_check.md |
| 2 Code members | done | 23:53 | 00:24 | strategy/members/k2/, tests/test_e3_k2_members.py, tests/test_e3_k2_members_events.py | MemberCoder-A-OpusXHigh, MemberCoder-B-OpusXHigh (worker-xhigh, opus); briefs reports/stage_e3_briefs/coder_*.md |
| 3 Fidelity audit | done | 00:16 | 00:28 | reports/stage_e3_member_audit.md | MemberAuditor-FableXHigh |
| 4 Rulings, freeze, commit | done | 00:28 | 00:44 | reports/stage_e3_member_rulings.md, cluster freeze file | |
| 5 Screening run | done | 00:43 | 00:51 | reports/stage_e3_k2_screen/ | |
| 6 Recomputation | done | 00:51 | 01:04 | reports/stage_e3_member_audit.md part 2 | |
| 7 Return | done | 01:05 | (see return section 8) | reports/E.3_RETURN.md | |

## Start facts

- Ledger at start: ledger/databento_spend.jsonl, 14,823 lines, sha256 02e7caa257bbee7b84d23a0394c9fae34985e884c1306fb47ea683546f15b1ed.
- Release calendar sha256 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8.

## Log
- 23:47 Start suite run 1 (with PYTHONPYCACHEPREFIX set): 3 failed, 2860 passed (tests/test_harness_freeze.py bytecode tests; they pass without the prefix, confirmed 23:49). The suite is re-run exactly as E.2b ran it (`uv run pytest -q`, no prefix) from 23:50 for the verbatim start record. Rule for this session: pytest runs without PYTHONPYCACHEPREFIX; every Stage E entry point (harness verify, runner, freeze) runs with a fresh prefix.
- 23:52 Specs written (Task 1). 23:53 coders A and B spawned in parallel.
- 00:00 Start suite (run 2, `uv run pytest -q`, no prefix, 23:50:06-00:00:42): `2863 passed, 2 skipped, 1 xfailed, 54 warnings in 633.88s (0:10:33)`, equal to the E.2b end result. Task 0 done.
- 00:08 Task 1b done: 340/340 agree, none unavailable; DROPPED_AUCTIONS empty. Two re-keyed reopenings (2019-11-05 10Y, 2026-01-26 5Y) kept by original_security_term: reading L-23 appended to the specs. Coder B told.
- 00:10 MemberCoder-B done (23:53-00:10): aucpre, aucpost, fomcpost, predrift, _releases.py (340 auctions, 57 FOMC, 86 ISM; DROPPED empty), _event_common.py; tests/test_e3_k2_members_events.py 47 tests; report reports/stage_e3_coder_B.md. Lead ruling R-T2-1 (00:11): a bar's open is read as dataclasses.asdict(bar)["open"] because the frozen static check bans the name `open` even as an attribute; same idiom told to coder A (already used in _port_common.py). All 13 K2 files pass check_member_source (00:12). B's note: the D9.5a guard delays aucpre ZN's 09:00 fill to 09:02 on 3 confirmation-window ISM days (engine rule, as designed).
- 00:13 MemberCoder-A done (23:53-00:13): cp1, cp2, cp3, monthend, _month_end.py (85 months 2019-05..2026-05; 9 of 170 dates early halts), _port_common.py; tests/test_e3_k2_members.py 98 tests; report reports/stage_e3_coder_A.md. Engine finding: a one-leg member is never called on a minute without its leg's bar. File hashes before the audit: reports/stage_e3_briefs/k2_files_pre_audit.sha256. 00:15 full suite started (Task 2 gate). 00:16 MemberAuditor-FableXHigh spawned (worker-xhigh, fable) - Fable available.
- 00:24 Task 2 gate: full suite 00:11:30-00:24:19 `3008 passed, 2 skipped, 1 xfailed, 54 warnings in 766.26s (0:12:46)`.
- 00:28 Task 3 done: audit part 1, 0 BLOCKING, 0 SHOULD FIX, 12 NOTE; all 23 readings agreed; R-T2-1 sound.
- 00:29 Cluster freeze written: reports/stage_e_k2_member_freeze.json sha256 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 (44 decls, 14 files); verified and all 44 resolved 00:31. Rulings reports/stage_e3_member_rulings.md. 00:31 suite for the commit gate started.
- 00:44 Commit gate suite 00:29:58-00:42:43 `3008 passed, 2 skipped, 1 xfailed, 54 warnings in 762.83s (0:12:42)`. Commit a79b47e `feat: K2 member freeze (Stage E.3), cluster freeze sha256 8815a775` (19 files). Task 4 done.
- 00:44 Task 5 started: the frozen runner command, out dir reports/stage_e3_k2_screen, log in scratch run_t5.log.
- 00:43 CRASH C-1 (Task 5, attempt 1, 00:43:15-00:43:26, exit 1): the frozen CLI `python -m screening.stage_e_runner ... --all --window research` raised `screening.stage_e_runner.StartRuleMissing: no frozen S_X for ['ZT']` from _research_statistics -> confirmation_supply_days -> stage_e_start_dates.start_dates_for (runner line 442), after the engine had run the first member (K2-cp1-01 ZT) in memory. No record written, out dir never created, no figure seen. Cause (harness, frozen): under `python -m` the runner is `__main__`; stage_e_start_dates raises its refusals through `_runner()` = `from screening import stage_e_runner`, a second module copy, so `__main__`'s `except (RunnerRefusal, StageEBarRefusal)` does not match and the refusal the tests expect to be recorded as power not_run (tests/test_stage_e_runner.py:94) escapes. 8 raises in stage_e_start_dates go through _runner().
- 00:50 Lead ruling R-T5-1: no member or frozen file changes. Re-run from scratch the same frozen `main()` with the identical argv from the imported module (`python -c "from screening.stage_e_runner import main; ..."`), the path the harness tests exercise; preflight, freeze verification and lower_priority stay inside main/screen_cluster; fresh PYTHONPYCACHEPREFIX; nice 10. Harness CLI bug reported for the user (future manifest).
- 00:47 Lead ruling R-T6-1: the runner's member records carry no trip list (series, n_trips, trade_rate and counters only). For Task 6's rebuild, the auditor replays the frozen engine in memory for exactly two trials (K2-cp1-01 ZN, K2-aucpost-01 ZN) through the runner's own functions (preflight, freeze, loader, _run_member, extract_trips). The replayed series must first equal the recorded series exactly. The recorded run stays the only result. Brief: reports/stage_e3_briefs/auditor_task6.md.
- 00:51 Task 5 done: run 2 (import launch) 00:44:56-00:50:39, stdout `K2 research: 44 members, 0 refused`, exit 0; 45 records in reports/stage_e3_k2_screen/. Result: all 44 fail D5 (Tier B), Tier A empty, no labels, no coverage exclusions, power not_run (StartRuleMissing, recorded) for all. 00:51 auditor resumed for Task 6 (brief reports/stage_e3_briefs/auditor_task6.md).
- 01:02 Task 6 part 2 done (00:51-01:02): item 1 44/44 VERIFIED WITH NOTES (figures to 1e-9; notes: power not run, MLL liquidations in 24 records), item 2 VERIFIED (all Tier B), item 3 VERIFIED (two replays equal the records; own cost rebuild exact), item 4 VERIFIED WITH NOTES (7 predrift date-root pairs untraded, cause not checkable from records), item 5 VERIFIED (N = 102). No DISCREPANCY. 01:05 auditor resumed for the predrift follow-up (3 dates common to ZN and ZB). 01:05 end suite started.
- 01:04 Predrift follow-up done: all 7 untraded (date, root) pairs are s = 0 (bars present, one instrument_id, no halt); replays equal records; VERIFIED.
- 01:13 End suite 01:02:21-01:13:30 `3008 passed, 2 skipped, 1 xfailed, 54 warnings in 668.06s (0:11:08)`. End checks 01:13:47: holdout 1 and 2 all_ok, 0 unlocks; REGISTRATION 0 bytes; check_frozen ALL_OK; preflight OK; K2 freeze verifies; ledger unchanged.
- Return reports/E.3_RETURN.md, progress.md entry and docs/STAGES.md line written; session cost computed last (return section 8).
