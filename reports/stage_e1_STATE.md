# Stage E.1 STATE

Lead: Opus 5.5, effort max. Ultracode off. Times are America/Vancouver (PDT).
Prompt: docs/prompts/STAGE_E.1.md (committed d218f17; the pasted prompt matches it).

## Start checks (17:41-17:50)

- `git status --short`: (empty, clean)
- `git log --oneline -3`:
  d218f17 docs: Stage E.1 prompt (freeze, account switch, step 1 purchase, ML route draft)
  92f8f88 docs: route literature research to opus; raise the WebSearch session cap to 1000
  01b259a feat: Stage E.0, CME universe research, 61-member catalog and Stage E design draft
- holdout status: holdout-1 all_ok true, unlocks_logged 0, research_has_no_holdout_rows true;
  holdout-2 sealed 13/13, sealed_in_order true, all_ok true, unlocks_logged 0,
  confirmation_has_no_holdout2_rows true
- `wc -c REGISTRATION.md`: 0 REGISTRATION.md
- pytest: running (background), result below when done
- Machine: 20 cores (parallel cap 8), 14 GB RAM, 8 GB available; 366 GB free on /.

## Findings at startup (lead)

- S-1 (17:52). E.0 step 1 re-summed from E.0's quote lines in the ledger (45 admissible
  contracts after U2, i.e. without PL): research window ohlcv-1m $57.28 (920 monthly requests
  across 46 roots with PL; PL $1.42), mbp-1 $45.95 (PL $0.40); total $103.24. D13's $58.42 was
  $0.28 lower than the ledger sum of $58.70 with PL; the fresh quote governs.
- S-2 (17:53). D13 says "the largest single request is one mbp-1 day of MNQ, about $2.7". The
  ledger says MNQ 2026-02-11 is $4.14 and MNQ 2025-11-12 is $3.41, both above the $3.00 request
  cap. The cap is NOT raised. Lead decision (open choice): the purchase path splits any mbp-1
  day request whose quote exceeds the request cap into contiguous time pieces (recursive
  halving), each quoted, gated and ledgered on its own; same data, same total.
- S-3. The step 1 volume is about 27.4 GB billable mbp-1 (uncompressed) and 0.88 GB ohlcv-1m.

## Estimate ETA table (printed in chat 17:44, before the first spawn; its 17:56 anchor was a guess, the real Task 0 end was 17:44)

| # | Task | Owner | Model | Effort | Par/Ser | ETA | Cumulative end (PDT) | Basis |
|---|---|---|---|---|---|---|---|---|
| 0 | Startup, checks, STATE, ETA | lead | opus | max | serial | 15 min | 17:56 | measured |
| 2 | ML literature (4 questions, <= 30 reads) | MLLitReader-OpusHigh | opus | high | parallel from 17:56 | 75 min | 19:10 | E.0 opus readers 33-53 min per cluster; guess |
| 5 | Account registry, pull_universe.py, tests | PurchaseCoder-OpusXHigh | opus | xhigh | parallel from 17:56 | 60 min | 18:56 | E.0 QuoteCoder 12 min for a smaller job; guess |
| 1 | Apply U1-U9, changes log, recount | lead | opus | max | parallel from 17:56 | 100 min | 19:36 | guess |
| 3 | Freeze audit | FreezeAuditor-FableXHigh | fable | xhigh | after 1 | 45 min | 20:21 | E.0 audit 17 min on a larger read; guess |
| 4 | Rulings, manifest, freeze commit | lead | opus | max | after 3 | 30 min | 20:51 | guess |
| 5c | Task 5 commit (after 4) | lead | opus | max | after 4 | 5 min | 20:56 | guess |
| 6a | Quote-only run, set session cap | lead runs path | — | — | after 5c | 15 min | 21:11 | E.0: 5,050 quotes in 54 min, ~1,150 here |
| 6b | Purchase (about 1,150 requests, ~5 GB compressed) | lead runs path (background) | — | — | after 6a | 75 min | 22:26 | guess |
| 9 | ML route draft (during 6b) | lead | opus | max | parallel with 6b | 80 min | (inside 6b) | guess |
| 7 | Integrity checks | lead inline | opus | max | after 6b | 15 min | 22:41 | guess |
| 8 | Spend recomputation (resumed) | FreezeAuditor-FableXHigh | fable | xhigh | after 7 | 20 min | 23:01 | guess |
| R | Return document, progress, STAGES, end checks, Session cost | lead | opus | max | last | 40 min | 23:41 | E.0 entry-writing; guess |

Cumulative estimate: about 6 h of work, ending about 23:40 PDT.

## Task status

| Task | Status | Start | End | Artifacts |
|---|---|---|---|---|
| 0 | done | 17:41 | 17:44 | this file |
| 2 | done (MLLitReader-OpusHigh; 29 full-text reads, 33 queries; Firecrawl out ~17:47, curl fallback; no WebSearch budget notice; 4 items [unverified]) | 17:44 | 18:02 | reports/stage_e1_ml_research.md |
| 5 | code done, commit pending Task 4 (PurchaseCoder-OpusXHigh; 13 + 57 new test cases; full suite 2 failed (known), 1010 passed, 1 xfailed; lead re-ran gate/pull tests: 126 passed) | 17:44 | 18:06 | data/config.py, data/spend_gate.py, data/pull_universe.py, tests |
| 1 | done | 17:45 | 17:57 | docs/STAGE_E_DESIGN.md, docs/NULL_CRITERIA_E.md, reports/stage_e0_catalog*.md/.json, docs/DECISIONS.md (U1-U9), reports/stage_e1_changes.md (96 markdown edits, 32 JSON edits, F-1..F-7) |

Start pytest (17:41-17:45): `2 failed, 940 passed, 1 xfailed, 19 warnings in 242.25s`; the 2 failures are
tests/test_d1f_calendar_build.py::test_2019_2024_quotes_are_verbatim_from_the_extraction and
::test_confirmation_build_end_to_end (the known D.1f pair). As expected.

Task 1 recount: 53 active members, 158 confirmation trials (93 port + 65 new), projected N = 216.
Count finding F-1: D1 has 32 IN rows before U2 (E.0 said 31); 31 after U2 (prompt said 30).
Next: Task 3 (FreezeAuditor-FableXHigh).

Time correction (17:57): the lead first wrote spawn and Task 1 times from memory (17:57, 18:47);
corrected from the transcript timestamps (session 17:40:59; workers 17:44:21 and 17:44:56).
| 3 | running (FreezeAuditor-FableXHigh, spawned 17:59) | 17:59 | | reports/stage_e1_freeze_audit.md |

Task 5 notes for the return document: data/spend_gate.py is in the D.1f harness-freeze manifest, so pull_mes --d1f-* modes now refuse (D.1f is complete); pull_mes, quote_universe and _d1e_quotes still attribute to acct-1 by default (not to be run against the acct-2 key without an account change); a failed download's commit stays counted (overstates, never understates).
| 3 | done (FreezeAuditor-FableXHigh: READY WITH FIXES, 0 BLOCKING, 7 SHOULD FIX, 9 NOTE) | 17:59 | 18:14 | reports/stage_e1_freeze_audit.md |
| 4 | done: rulings, fixes, FROZEN headers, manifest verified (32 files, 0 mismatches, no Stage E product data); freeze commit 848f331; manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c | 18:14 | 18:16 | reports/stage_e1_freeze_rulings.md, reports/stage_e1_freeze.json |
| 5c | done: Task 5 commit b05c506 | 18:16 | 18:16 | — |
| 6a | running: --quote-only | 18:16:54 | | reports/stage_e1_quote_summary.json, reports/stage_e1_quote_run.log |
Time correction (18:17): Task 3 end and the Task 4/5c times above were first written as estimates; corrected from file mtimes, the commit times (848f331 18:16:32, b05c506 18:16:42) and the quote log.
| 9 | draft written (docs/STAGE_E_ML_DESIGN.md, DRAFT; M1-M9; TCN dropped; 36 configurations; <= 16 rules) | 18:17 | 18:22 | docs/STAGE_E_ML_DESIGN.md |
| 6a | done: fresh quote $103.161113 (ohlcv-1m $57.003331, mbp-1 $46.157782; 900 requests -> 904 pieces; 2 MNQ mbp-1 days split to depth 2; largest piece $2.247100); within $104.77 x 1.05 | 18:16:54 | 18:37:46 | reports/stage_e1_quote_summary.json, reports/stage_e1_quote_run.log |
| 6s | session cap set: E1_SESSION_CAP_USD = 113.48 (quote x 1.10) in data/config.py; two tests that pinned the 0.00 placeholder updated to the set value (same strength); 82 gate/pull tests pass | 18:38 | 18:38 | data/config.py, tests/test_spend_gate_accounts.py, tests/test_pull_universe.py (uncommitted) |
| 6b | running: --buy (serial; about 16 s per request, 904 pieces, est. end 22:40-23:00) | 18:38:44 | | reports/stage_e1_buy_run.log, data/vendor/databento/GLBX.MDP3/ |
| 6b | STOPPED 20:59:11 after 619 pieces, $54.14987: quote for ZL ohlcv-1m 2025-08-01..2025-09-01 failed (ConnectionError, 'No route to host': local network outage); gate refused as unpriceable (fail closed). No commit for that request; no partial file. Connectivity re-checked (HTTP 200). Resumed at 20:59 with caps unchanged (open choice O-resume). | 18:38:44 | 20:59:11 | reports/stage_e1_buy_run.log |
| 6b | STOPPED again 21:03:55 (resume 1, attempt 2): download of HE ohlcv-1m 2025-06 failed (ConnectionError); its commit stays unsettled in the ledger (overstates spend by $0.02; never understates). Wi-Fi intermittent. From 21:04: supervised resume loop (scratchpad resume_loop.sh): waits for the vendor host, resumes with unchanged caps, retries only on ConnectionError stops, max 8 attempts; any other stop is final. Logs reports/stage_e1_buy_run_part3..10.log. | 20:59:47 | 21:03:55 | reports/stage_e1_buy_run_part2.log |
| 6b | STOPPED 21:12:33 (attempt 3): quote for LE ohlcv-1m 2026-01 failed (ConnectionError, ledger note), gate refused as unpriceable; the supervisor treated it as non-network (by design). Supervisor v2 from 21:13: also classes an 'unpriceable' stop as network when the ledger's last failed-quote note is a ConnectionError; max 15 attempts (parts 4-18). | 21:04:40 | 21:12:33 | reports/stage_e1_buy_run_part3.log |
| 6b | done: all 904 pieces bought and settled (attempt 16 of the supervisor, finished 23:34:08). Stops: 15, every one a network failure (12 quote ConnectionErrors refused as unpriceable, 3 download ConnectionErrors: HE ohlcv-1m 2025-06, LE, M2K; their first commits stay unsettled in the ledger, overstating committed spend). Ledger E.1: 1,831 quote, 907 commit, 904 settle, 12 refused. | 21:13 | 23:34:08 | reports/stage_e1_buy_run_part1..16.log |
| 6c | holdout status after the purchase: holdout-1 all_ok true, unlocks_logged 0, research_has_no_holdout_rows true; holdout-2 sealed 13/13, all_ok true, unlocks_logged 0 | 23:35 | 23:35 | — |
| 7 | done: 904 files, 358,273,563 records, quoted = settled = $103.161113; 0 gaps, 0 uncovered, 0 files outside 2025-04-01..2026-06-21 (11 mbp-1 files start before their request window by event time, inside the allowed dates; no quarantine); 3 duplicate commits ($0.316080) from failed downloads | 23:36 | 23:37 | reports/stage_e1_purchase.json/.md |
| 8 | running: FreezeAuditor-FableXHigh resumed (SendMessage) | 23:37 | | reports/stage_e1_freeze_audit.md Part 2 |

Note (Task 8, FA Part 2): the 21:03 row's '$0.02' was the first unsettled commit only; the final total of unsettled first commits is $0.316080 (HE, LE, M2K), so the gate's committed session total is $103.477194 against $103.161113 settled.
| 8 | done: VERIFIED (0 blocking, 0 should fix, 5 notes) | 23:37 | 23:42 | reports/stage_e1_freeze_audit.md Part 2 |
| R | done: end checks (23:42), reports/E.1_RETURN.md, progress.md entry, STAGES.md line | 23:38 | 23:46 | reports/E.1_RETURN.md |
