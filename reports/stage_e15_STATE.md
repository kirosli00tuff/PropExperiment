# Stage E.15 STATE (C1: verify, v11, quote, register, buy, build, evaluate once, Fable check)

Lead: Opus 5.5 xhigh, session 9488d909-a916-4ea0-81f2-01f4f5654877, started 2026-10-07 21:56 PDT. Prompt
docs/prompts/STAGE_E.15.md (HEAD 4bc493f). Times PDT, from `date`, file mtimes, git and the ledgers.
On resume: read this file first; skip done steps. The run-once marker reports/stage_e14_c1_RUN_ONCE.json, once
written, forbids any second evaluation.

## In force (updated after every step)

- Harness: v10 fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b (until Step 2 commits v11).
- C1 freeze reports/stage_e14_prereg_C1.md afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
  (commit 1680982, unchanged). Inputs list 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e.
- Model JSON c6075306ddfd70cb22a2b32f8017ae41ba6050778e6cb66568d00b94585421e6; M1 h60
  9c2d9986ec788a0abcd08186cf249061f91ed0794d3519532ef779de4ccfb9d8, hF
  153c2bdc25087e0b2f2f236d46fa186e78bb85fa2d50d8702d4c7e5ac4dfbe99; q_h60 0.033735277284776724,
  q_hF 0.0831931045522869. E.12 state manifest 8a38eeb150ba7c063e1f7b4292b00efb0bd10549c61e8202fcb926bc8dab1ad9.
- N = 471 (ledger/trial_registrations.jsonl: 1 line, sha256 a73b4de8...).
- Ledger ledger/databento_spend.jsonl: 27,756 lines, sha256 0312fbc0...; acct-1 spent 118.390020 / cap 120.00
  (headroom 1.609980); acct-2 spent 231.599730 / cap 249.67 (headroom 18.070270).
- Holdouts: all_ok, unlocks_logged 0 (22:00, 22:30).
- Ledger after the failed quote run (22:30): 28,398 lines, sha256 ef429036642b25c8fd0d4b8adb33967f1ef43b1a3f9532f46e447845698fdea7; totals unchanged.
- STOP (22:29): Databento acct-2 locked (403 auth_account_locked); C1 not registered, nothing bought.

## Steps

| Step | Status | Start | End | Artifacts | Notes |
|---|---|---|---|---|---|
| 0 Startup | done | 21:56 | 22:23 | reports/stage_e15_briefs/checks.sh, start_checks.txt, pytest_start.out | HEAD 4bc493f; tree clean apart from .claude/worktrees/ and the E.12-E.14 DO_NOT_COMMIT page folders (638 lines); holdouts all_ok 0 unlocks; REGISTRATION.md 0 bytes; v10 preflight OK; cluster freezes K1-K8 OK; v2 freeze OK 91 files; start suite 22:00:47-22:23:08: 6740 passed, 2 skipped, 3 xfailed, rc 0 (game running on the machine; 22 min) |
| 1 Verify the freeze | done, ALL_OK | 22:05 | 22:06 | reports/stage_e15_briefs/verify_freeze.py, verify_freeze.json (sha256 5e98865e65e38e685b8f28ddeb3894e95490b342e12b10b078dad4696cebe5f1); calendar hash file reports/stage_e15_c1_calendar_hashes.json (d5e48579d2bd70b2e73d7583010e7c7ef61f94cc58fe68b07e7734a12911f6f8, from the freeze's hashes, 22:08) | 43 of 43 inputs match (list sha256 3356d676... ok); freeze tracked, no diff vs HEAD, only commit 1680982, blob = file; E.12 state copy 51 files (45 npy) match; model JSON, both payloads (mode 0444) and q match; v10 preflight OK. No 2010-2018 file under data/vendor/databento; data/processed_hist absent; no marker, no result file |
| 3 Fresh quote (under v10) | STOPPED: no fresh quote (Databento acct-2 locked) | 22:23:51 | 22:28:08 | reports/stage_e15_briefs/quote_ext2010.log; the tool's JSON/MD moved to reports/stage_e15_briefs/quotes_ext2010_ALL_FAILED_not_fresh.json/.md | v10 preflight OK first. All 642 quote calls (05:23:54-05:28:08 UTC) failed: "quote failed: BentoClientError: 403 auth_account_locked" ("Your account has been locked for security reasons."), 642 ledger lines at $0.00 (27,756 -> 28,398 lines, sha256 ef429036...). The tool logged "quoted 642 of 642 chunks; 642 failed" but its JSON reports $57.742330, 0 failed, complete: quotes_from_ledger falls back to the latest successful quote under STAGE_E14_SESSION_ID, i.e. E.14's lines. Not a fresh quote. Ruled 22:29: stop before registration (V27's pre-approval and freeze section 11 need a fresh quote; the session cap is defined from it; registration is irreversible and no buy can follow). No retry: a security lock is the account holder's to clear. |
| 2 Harness v11 | NOT RUN (stop) | | | | v10 stays in force: the session cap cannot be set without a fresh quote; the next session writes v11 with both values |
| 4 Register | NOT RUN (stop) | | | | N stays 471; C1 unregistered |
| 5 Buy and build | NOT RUN (stop) | | | | nothing bought; no 2010-2019 byte exists; stop-point checks 22:30 (reports/stage_e15_briefs/stop_checks.txt): holdouts all_ok 0 unlocks, acct-2 spent 231.599730 |
| 6 Evaluate once | NOT RUN (stop) | | | | no marker, no result |
| 7 Fable verify | NOT RUN (no verdict to verify) | | | | |
| 8 Return, commit (attempt 1) | done | 22:29 | 22:50 | reports/E.15_RETURN.md, progress.md, docs/STAGES.md, end_checks_attempt1.txt, pytest_end.out (6740 passed, 22:31:10-22:48:16) | commit "Stage E.15 stopped before registration: Databento acct-2 locked" |
| ATTEMPT 2 | next | | | | 22:45 user (relayed by the planning chat): the acct-2 lock is cleared; resume from Step 3 in this session: re-run Step 1, fresh quote under v10 with the lead-side guard (reports/stage_e15_briefs/fresh_quote_guard.py: the total summed from the run's own new ledger lines, never the tool JSON, never --retry-failed), then Steps 2, 4-8; an auth or lock error again stops before registration |
