# Stage E.15 return: C1 STOPPED before registration; Databento locked acct-2; nothing bought, N stays 471

Lead Opus 5.5 xhigh, 2026-10-07 21:56 to 22:50 PDT, session 9488d909. Prompt docs/prompts/STAGE_E.15.md
(HEAD 4bc493f). STATE: reports/stage_e15_STATE.md. Times are PDT unless marked UTC.

## 1. Verdict summary

**C1 (backward NG replication): STOPPED before registration.** The rule: the fresh quote that V27's
pre-approval and the freeze's section 11 put before registration could not be obtained.
- Step 1 passed: all 43 frozen inputs match, the freeze file (afc5c10f...) is unchanged since 1680982, the E.12
  state copy matches (51 files), and the model JSON, both M1 payloads and q match.
- Step 3, the fresh quote under v10 (22:23:51 to 22:28:08): Databento refused all 642 quote calls with
  `403 auth_account_locked` ("Your account has been locked for security reasons."), 642 ledger lines at $0.00.
- The quote tool's JSON nonetheless reported "$57.742330, 0 failed, complete". It silently reused Stage E.14's
  quote lines under the same session id. It is not a fresh quote; it was moved into the briefs folder under a
  name saying so.
- With no fresh quote, the session cap (quote x 1.03) cannot be set. A locked account cannot buy, and
  registration cannot be undone. The lead stopped before registration (22:29).

No T1 or T2 statistic exists: no 2010-2019 byte was bought or read, and there was no evaluation and no marker.
Cost $0.00. Funds: acct-1 $1.61 of headroom, acct-2 $18.07 under the unchanged $249.67 cap. Harness v10
(fde3a49c...) stays in force; no v11 was written. **N stays 471.** Per the freeze's section 8 nothing is learned
about the NG near-miss. C1 stays frozen and valid for a later session once the user clears the lock with
Databento (section 7).

## 2. Guardrail evidence

**Start checks, 22:00** (reports/stage_e15_briefs/start_checks.txt):

```
$ date
Wed Oct  7 22:00:21 PDT 2026
$ git status --short
?? .claude/worktrees/
?? reports/stage_e12_briefs/, stage_e13_briefs/, stage_e14_briefs/ page files: 638 lines (collapsed; full text in reports/stage_e15_briefs/start_checks.txt)
?? reports/stage_e15_briefs/
$ git log --oneline -3
4bc493f docs: Stage E.15 prompt (C1 completion) and V27
0b037e9 Stage E.14 C1 frozen, C2 stopped (not evaluated)
1680982 E.14 freezes, C1 and C2: C1 frozen; C2 stopped before its freeze
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
preflight OK: fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
27756 ledger/databento_spend.jsonl
0312fbc0b1ca2da652ca7caaab2313ccbbc6920ae3a19d9651ff2e94cd1c48fb
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 471 (1 lines)
$ wc -l ledger/trial_registrations.jsonl; sha256sum
1
a73b4de878caa75066a8c24513e354de0a07d34f15d53407c4450e6f0135de0d
```

**Stop-point checks (the post-purchase point; nothing was bought), 22:30** (reports/stage_e15_briefs/stop_checks.txt):

```
$ date
Wed Oct  7 22:30:23 PDT 2026
$ git status --short
 M ledger/databento_spend.jsonl
?? .claude/worktrees/
?? reports/stage_e12_briefs/, stage_e13_briefs/, stage_e14_briefs/ page files: 638 lines (collapsed; full text in reports/stage_e15_briefs/stop_checks.txt)
?? reports/stage_e15_STATE.md
?? reports/stage_e15_briefs/
?? reports/stage_e15_c1_calendar_hashes.json
$ git log --oneline -3
4bc493f docs: Stage E.15 prompt (C1 completion) and V27
0b037e9 Stage E.14 C1 frozen, C2 stopped (not evaluated)
1680982 E.14 freezes, C1 and C2: C1 frozen; C2 stopped before its freeze
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
preflight OK: fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
28398 ledger/databento_spend.jsonl
ef429036642b25c8fd0d4b8adb33967f1ef43b1a3f9532f46e447845698fdea7
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 471 (1 lines)
$ wc -l ledger/trial_registrations.jsonl; sha256sum
1
a73b4de878caa75066a8c24513e354de0a07d34f15d53407c4450e6f0135de0d
```

**End checks, 22:48** (reports/stage_e15_briefs/end_checks_attempt1.txt):

```
$ date
Wed Oct  7 22:48:25 PDT 2026
$ git status --short
 M docs/STAGES.md
 M ledger/databento_spend.jsonl
?? .claude/worktrees/
?? reports/E.15_RETURN.md
?? reports/stage_e12_briefs/, stage_e13_briefs/, stage_e14_briefs/ page files: 638 lines (collapsed; full text in reports/stage_e15_briefs/end_checks_attempt1.txt)
?? reports/stage_e15_STATE.md
?? reports/stage_e15_briefs/
?? reports/stage_e15_c1_calendar_hashes.json
$ git log --oneline -3
4bc493f docs: Stage E.15 prompt (C1 completion) and V27
0b037e9 Stage E.14 C1 frozen, C2 stopped (not evaluated)
1680982 E.14 freezes, C1 and C2: C1 frozen; C2 stopped before its freeze
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
preflight OK: fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
28398 ledger/databento_spend.jsonl
ef429036642b25c8fd0d4b8adb33967f1ef43b1a3f9532f46e447845698fdea7
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 471 (1 lines)
$ wc -l ledger/trial_registrations.jsonl; sha256sum
1
a73b4de878caa75066a8c24513e354de0a07d34f15d53407c4450e6f0135de0d
```

**Suites** (`uv run pytest -q -p no:cacheprovider`, no PYTHONPYCACHEPREFIX, nice 10):

```
start (pytest_start.out): 6740 passed, 2 skipped, 3 xfailed, 54 warnings in 1338.19s (0:22:18)
end   (pytest_end.out):   6740 passed, 2 skipped, 3 xfailed, 54 warnings in 1022.27s (0:17:02)
```

**Order of events (attempt 1), with timestamps (PDT; from `date`, the logs and the ledger):**

| Event | Time | Evidence |
|---|---|---|
| Start checks (v10) | 22:00:21 | start_checks.txt |
| Start suite | 22:00:47-22:23:08 | pytest_start.out: 6740 passed, 2 skipped, 3 xfailed |
| Verification (Step 1) | 22:05-22:06 | verify_freeze.json (started_local / finished_local) |
| Calendar hash file (hashes only) | 22:08 | reports/stage_e15_c1_calendar_hashes.json |
| Fresh quote under v10 (Step 3): FAILED, 642 x 403 auth_account_locked | 22:23:51-22:28:08 (ledger 05:23:54-05:28:08 UTC) | quote_ext2010.log; ledger lines 27,757-28,398 |
| Stop ruled, before registration | 22:29 | STATE |
| Stop-point checks (in place of post-purchase) | 22:30:23 | stop_checks.txt |
| End suite | 22:31:10-22:48:16 | pytest_end.out: 6740 passed, 2 skipped, 3 xfailed |
| End checks | 22:48:25 | end_checks_attempt1.txt |
| v11 commit, registration, buy, store builds, evaluation, Fable check | not run | (the stop) |


## 3. Results per step

### Step 0: startup (21:56 to 22:23)
- HEAD 4bc493f. The tree was clean apart from .claude/worktrees/ and the 638 E.12-E.14 DO_NOT_COMMIT page lines.
- Holdouts all_ok with 0 unlocks. REGISTRATION.md 0 bytes. v10 preflight OK. Cluster freezes K1-K8 OK. v2 freeze
  OK (91 files). N = 471.
- Ledger: 27,756 lines; acct-2 spent $231.599730 of $249.67.
- Start suite (22:00:47 to 22:23:08): 6740 passed, 2 skipped, 3 xfailed. It took 22 minutes against E.14's 16
  because the user's game was running on the machine.

### Step 1: verify the freeze (22:05 to 22:06; reports/stage_e15_briefs/verify_freeze.py, verify_freeze.json)

| Check | Result |
|---|---|
| reports/stage_e14_c1_freeze_inputs.json | sha256 3356d676... as pinned; 43 of 43 entries match by sha256 and bytes (design 4, calendar 8, calendar_report 5, code 10, test 9, e12_state 5, harness 1, quote 1) |
| Freeze reports/stage_e14_prereg_C1.md | sha256 afc5c10f...; tracked; `git diff --quiet HEAD` clean; touched only by 1680982; the blob at 1680982 equals the file |
| E.12 state copy | 51 files (45 .npy) match reports/stage_e14_c1_e12_state_manifest.json (8a38eeb1...), nothing extra (c1_replication.guards.verify_state) |
| Model JSON and M1 | JSON c6075306...; payload files h60 9c2d9986... and hF 153c2bdc... (mode 0444) equal the JSON's sha256s; q_h60 0.033735277284776724 and q_hF 0.0831931045522869 match |
| Harness | v10 preflight OK (fde3a49c...) |

No 2010-2018 Databento file exists under data/vendor/databento. data/processed_hist does not exist, and there is
no marker or result file. The calendar hash file reports/stage_e15_c1_calendar_hashes.json (d5e48579...) was
written at 22:08 from the freeze's own hashes (hashes only, no market data). It is ready for the later session.

### Step 2: harness v11, NOT WRITTEN
Step 2's own rule ran the quote first, under v10, because the session cap is set from it. With no fresh quote
the session cap is undefined, so v10 stays in force (open choice 7). The prepared edit and the test lines it
touches are in section 7, item 4.

### Step 3: fresh quote, STOPPED (reports/stage_e15_briefs/quote_ext2010.log)
- The v10 preflight ran first (22:23:51 to 22:23:53), then `uv run python -m data.pull_step2 --quote-only --plan ext2010
  --account acct-2 --quotes-out reports/stage_e15_quotes_ext2010.json` at nice 10.
- 642 calls, 05:23:54 to 05:28:08 UTC. Every one ledgered as `quote failed: BentoClientError: 403
  auth_account_locked`, usd 0.0, 107 per root (NG, NQ, ZN, 6E, GC, ZC). The ledger went from 27,756 to 28,398
  lines, sha256 ef429036...; account totals are unchanged.
- The tool's own log reads "quoted 642 of 642 chunks; 642 failed", then "TOTAL QUOTED $57.742330 (x 1.03 =
  $59.474600); 0 chunk quote(s) failed". Its JSON says chunks_failed 0, complete true, generated 22:28:08.
- Cause: data.pull_hist.quotes_from_ledger keeps "the latest successful quote of each chunk under session_id".
  Quotes run under STAGE_E14_SESSION_ID, which already holds E.14's 642 successful lines, so a run in which every
  call fails reports E.14's figures as complete.
- The JSON and MD were moved to reports/stage_e15_briefs/quotes_ext2010_ALL_FAILED_not_fresh.json/.md (open
  choice 6).
- No arithmetic against the headroom exists, because there is no fresh quote. Under V27 the headroom would have
  been $291.08 - $231.599730 = $59.480270.

### Steps 4 to 7: NOT RUN
- No registration: N 471, the registry still holds the baseline line only, sha256 a73b4de8....
- No purchase and no store build. The stop-point checks at 22:30 (reports/stage_e15_briefs/stop_checks.txt) show
  holdouts all_ok with 0 unlocks and spend unchanged.
- No evaluation: no marker.
- No Fable check: no verdict number exists (open choice 8).

## 4. Delegation record

No worker was spawned. Every step the session ran (0, 1, 3 and 8) is reserved to the lead, and Step 7, the only
delegated step, had no verdict to check.

| Spawn | Agent file | Model | Effort | Tokens |
|---|---|---|---|---|
| none | | | | |

## 5. Verification

No Fable check ran, because there is no verdict, statistic, P&L or new trial count to verify. The stop rests on
mechanical evidence that anyone can recheck:
- the 642 ledger lines (all `403 auth_account_locked`, all $0.00; `tail -n 642 ledger/databento_spend.jsonl`);
- the per-account totals in the stop and end checks;
- the trial registry at 1 line, N = 471;
- the absence of data/processed_hist, the marker and the result file.

## 6. Open choices (every decision the lead made on its own)

1. **Quote before v11 (Step 2's conditional rule).** The session cap needs the fresh quote, so the quote ran under
   v10 with v11 due before Step 4, as Step 2 allows. The guardrails' list of events puts "v11 commit" before the
   quote, but Step 2's own rule covers exactly this case.
2. **Order quote, then register.** The freeze's section 11 (the later session's list), the model file and the
   prompt all put the quote before registration. The freeze's section 9 numbers registration (step 5) before
   the quote (step 6). Section 11 is the specific instruction for this session and agrees with the prompt, so it
   was followed. It is also the order that guards the spend.
3. **Preflight separately for the quote.** `--quote-only` refuses `--harness-sha256` (data/pull_hist.py
   _check_args). The v10 preflight ran by itself immediately before the quote and is logged in quote_ext2010.log.
4. **The stop.** All 642 quote calls failed with 403 auth_account_locked, so there is no fresh quote. V27
   pre-approves spend only "after a logged quote", with the session cap "= the fresh quote x 1.03". The freeze's
   section 11 says "quote fresh, and stop if ...; then register". Registration is irreversible (+2 on N) and no
   buy can follow on a locked account.
   - Ruled at 22:29: stop before registration. This is a stop the prompt allows: a decision that cannot be undone
     and could reasonably go either way, and a guardrail (the spend pre-approval) that cannot be met.
   - Registering now and buying in a later session would also have been defensible under the freeze. It was
     rejected because the freeze, the model file and the prompt all have the quote gate the registration.
5. **No retry of the quote.** The tool can only re-quote the whole plan: 642 calls, since `--retry-failed`
   skips chunks with an E.14 success. The message says the account is "locked for security reasons", which is
   the account holder's to clear, not a transient error. Repeated calls to a locked account could prolong the
   lock, so the lead did not hammer it.
6. **The misleading quote file.** The tool wrote reports/stage_e15_quotes_ext2010.json/.md showing E.14's total
   as complete. Both were moved, unedited, to reports/stage_e15_briefs/quotes_ext2010_ALL_FAILED_not_fresh.json/
   .md, so no later reader or session takes them as a fresh quote. The quote log keeps the tool's own lines.
7. **No v11.** E14_EXT2010_SESSION_CAP_USD is defined as the fresh quote x 1.03, which does not exist. A v11 with
   only ACCOUNT_2_CAP_USD = 291.08 and a 0.00 session cap would buy nothing, and the next session would need a
   v12 for the cap. v10 stays, and the next session writes v11 with both values in one commit, as the prompt
   intends.
8. **No Fable spawn.** Step 7 recomputes a verdict, and none exists. The stop's evidence is mechanical (ledger
   lines, totals, a one-line registry), and Fable's weekly pool is kept for the evaluation's check in the later
   session.
9. **Calendar hash file written before the quote.** At 22:08 the lead wrote reports/stage_e15_c1_calendar_hashes.json
   (README step 3; sha256 d5e48579...). It is built from the freeze's own hashes, each checked on disk, and
   holds no market data. It is kept and committed for the later session, which must re-verify it (it is
   write-once; reports/stage_e15_briefs/write_hash_files.py refuses to overwrite it).
10. **Post-purchase check at the stop point.** There was no purchase, so the post-purchase guardrail checks ran
    at the stop point, 22:30 (stop_checks.txt).
11. **Push notification.** At 22:31 the lead sent one desktop and mobile notification saying the session stopped
    on the Databento lock, because the user must act on it and was away.
12. **Commit message.** The final commit reads "Stage E.15 stopped before registration: Databento acct-2 locked"
    rather than the prompt's "Stage E.15 C1 evaluated", which would be false (E.14 precedent, its open choice
    23). It holds the ledger's 642 new $0.00 lines, the reports, STATE and the briefs.
13. **Small scripts inline.** The lead wrote three small scripts itself rather than spawning a worker for each
    (CLAUDE.md: small tasks inline): the check script (E.14's plus a registry line), verify_freeze.py and
    write_hash_files.py.
14. **Prepared but not applied (for the later session; section 7, item 4).**
    - The freeze cites tests/test_stage_e_config_v8.py:62-64 as the assertions pinning ACCOUNT_2_CAP_USD. In the
      file, line 62 is a comment, line 63 pins the v8 arithmetic, and the assertions that pin the cap are lines
      64 (`floored == 249.67 == config.ACCOUNT_2_CAP_USD`) and 65 (`funds >= config.ACCOUNT_2_CAP_USD`). Line 66
      holds under any cap.
    - The freeze's governing words are "the test assertions that pin those two values". The lead would apply
      them to lines 64-65 and record the off-by-two citation.
    - The lead would set the session cap by rounding the quote x 1.03 down to the cent, as E.14 did for
      E14_SESSION_CAP_USD (10.412319 -> 10.41).
    - Before the v11 commit, the lead would run the 33 test files that reference either cap, ext2010 or the
      harness manifest, and the full suite at the end.

## 7. Decisions for the user (the lead's recommendation first)

1. **Clear the Databento lock on acct-2** (recommended: now). Databento's message is "403 auth_account_locked:
   Your account has been locked for security reasons." Only the account holder can clear it, through Databento
   support or the portal. The session did not touch the key or the account. It may be related to the recent
   top-up, so it is worth confirming the balance and payment status at the same time.
2. **Then re-run Stage E.15 with one amendment** (recommended). The prompt can run as written: Step 1 will pass
   again, since nothing among the 43 frozen inputs changed. Add one guard to Step 3: the lead computes the fresh
   total from that run's own ledger lines, never from the tool's JSON.
   - The lines to use are this run's (ts at or after the run's start, session STAGE_E14_SESSION_ID), with all 642
     chunks quoted (quoted_usd not null).
   - The tool's log line must read "quoted 642 of 642 chunks; 0 failed".
   - Never use `--retry-failed`: E.14's lines make it skip every chunk.
3. **The quote tool's fallback defect** (recommended: fix after C1, not before). data.pull_hist.quotes_from_ledger
   takes the latest successful line per chunk across the whole session id, so a run in which every call fails
   reports an earlier session's quote as complete and fresh. A fix would change harness code, and C1's freeze
   allows only a harness that differs from v10 in the two caps. Use item 2's lead-side check for C1, and fix the
   tool in the first harness after C1: use only the current run's lines and count its own failures.
4. **v11 as prepared** (recommended: accept for the later session).
   - data/config.py: `ACCOUNT_2_CAP_USD = 291.08` with a V27 comment, and `E14_EXT2010_SESSION_CAP_USD` = fresh
     quote x 1.03 rounded down to the cent, never above $291.08 - $231.599730 = $59.480270 and never above
     $60.00, with its comment.
   - Test assertions: tests/test_e14_config_v10.py:20 (the session cap), 32-33 (291.08);
     tests/test_e14_pull_hist.py:300 (the session cap: the buy is still refused there, without C1's registration);
     tests/test_stage_e_config_v8.py:64-65 (the freeze cites 62-64: open choice 14). Nothing else.
   - At E.14's prices ($57.742330) the session cap would be $59.47.

## 8. Session cost

Attempt 1 (the stop). Wall clock 21:56 to 22:50 PDT, 0:54, with no pause and no usage-limit wait.

### Final ETA table, attempt 1 (actuals; PDT; the initial estimate in brackets)

| # | Task / spawn | Owner | Model | Effort | Start | End | Time [estimate] | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Startup, start checks | lead | opus | xhigh | 21:56 | 22:00 | 0:04 [0:04] | lead | done |
| 0b | Start suite (background) | lead | n/a | n/a | 22:00 | 22:23 | 0:22 [~0:30] | lead | 6740 passed; a game was running on the machine |
| 1 | Verify the freeze | lead | opus | xhigh | 22:05 | 22:06 | 0:01 [done in parallel] | lead | ALL_OK |
| 3 | Fresh quote under v10 | lead | opus | xhigh | 22:23 | 22:28 | 0:05 [0:23] | lead | FAILED: 642 x 403 auth_account_locked; STOP 22:29 |
| 2, 4-7 | v11, register, buy, build, evaluate, Fable | | | | | | not run [~3:25] | | stopped before registration |
| 8 | Stop checks, end suite, return, commit | lead | opus | xhigh | 22:29 | 22:50 | 0:21 [0:40] | lead | end suite 6740 passed |
| Total | Stage E.15, attempt 1 | lead, 0 spawns | | | 21:56 | 22:50 | 0:54 [estimate ~5:10 to ~03:05] | lead 19,122,120; workers 0; total 19,122,120 | no pause |

### Tokens per model, attempt 1 (this session's transcript, 04:50Z to 05:50Z on 2026-10-08)

Computed with reports/stage_e10_briefs/cost.py (final usage per streamed message). Token counts, not plan-credit
percentages. No subagent ran.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 196 | 87,833 | 18,776,386 | 257,705 | 19,122,120 |
| all | 196 | 87,833 | 18,776,386 | 257,705 | 19,122,120 |

Delegation share: lead 100%, workers 0%. By model: claude-opus-5-5 100%.

