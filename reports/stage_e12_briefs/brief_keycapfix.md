# Brief: KeyCapFix-OpusXHigh (worker-xhigh, opus). Stage E.12 Task 4 (harness v8, prepared)

You are a worker in Stage E.12 (prompt docs/prompts/STAGE_E.12.md: read SCOPE, GUARDRAILS, Task 4
and Task 5). Decisions: docs/DECISIONS.md V19 and V23 (lines 341-352, 409-445); E.11 code review
C-10 (reports/stage_e11_rulings.md line 54).

## WHERE YOU WORK (important)
Work ONLY in the git worktree /home/kiros-li/Documents/GitHub/PropExperiment-e12-v8 (branch e12-v8,
at 8b93e98). Never edit files in the main tree /home/kiros-li/Documents/GitHub/PropExperiment (other
workers and the lead's freeze use it). No commits. Run tests from the worktree with the main
tree's venv (the project is not installed; pytest's pythonpath "." imports the worktree's code):
  cd /home/kiros-li/Documents/GitHub/PropExperiment-e12-v8 && \
  PYTHONPYCACHEPREFIX=<fresh dir under /tmp/claude-1000/> nice -n 10 \
  /home/kiros-li/Documents/GitHub/PropExperiment/.venv/bin/python -m pytest -q -p no:cacheprovider <files>
There is no .env in the worktree: no test may need a key, and nothing may print one.

## Objective: the v8 code changes, all to frozen harness files, with tests
1. data/config.py
   - ACCOUNT_2_CAP_USD = 249.67, comment with the arithmetic from the ledger: acct-2's cumulative
     spend 124.673761 (ledger/databento_spend.jsonl at 2026-10-03 07:52 PDT, 17,400 lines, sha256
     0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957) + the user's $125.00 top-up
     of 2026-10-02 (V19) = 249.673761, rounded DOWN to the cent so the cap never exceeds the funds.
     Recompute 124.673761 yourself from the worktree's ledger copy (it is the same file at HEAD) with
     data.spend_gate.account_committed_usd and state it.
   - C-10(b): require_databento_key returns the stripped key (key.strip()); a test proves a
     whitespace-padded value comes back stripped, using monkeypatched env, and that no output
     (capsys) contains the value.
   - A Stage E.12 block, after the E.5 block, in the same style: STAGE_E12_SESSION_ID =
     "stage-E.12-2026-10-03"; E12_SESSION_CAP_USD = 0.00 with a comment that the lead sets it from
     the fresh quote (the selected subset's quote total x 1.03, never above the combined headroom of
     the two accounts) before the v8 manifest; E12_REQUEST_CAP_USD = 3.00 (D13's per-request cap);
     STEP2_TRAINING_WINDOW_ONLY = True; repoint STEP2_PURCHASE_SESSION_ID, STEP2_SESSION_CAP_USD,
     STEP2_REQUEST_CAP_USD to the E.12 block. Earlier blocks stay as they were.
2. docs/ACCESS.md: C-10(a): where it names DATABENTO_API_KEY, name DATABENTO_API_KEY1 (acct-1) and
   DATABENTO_API_KEY2 (acct-2) instead (read the file by grep; change only those lines).
3. data/pull_step2.py (read its module docstring first; keep every existing guard):
   - `--account acct-1|acct-2`: the gate is built on that account (data.config.ACCOUNTS; acct-1's
     gate reads its external ledger as the spend gate already does) and the key loader reads that
     account's key (require_databento_key(account=...)). Required with --buy; the quote default
     stays ACTIVE_ACCOUNT. require_buy_caps accepts any registered account that was passed
     explicitly. The banner names the account, never the key.
   - `--roots R1,R2,...` for --buy and --quote-only: an explicit list, each root one of the 28 v2
     price paths ML_V2_PRICE_PATHS (= ML_ROUTE_ROOTS minus RB, HO, SI; ml_route_v2.constants.UNIVERSE
     values; define the tuple here as a literal with that comment and a check against
     ML_ROUTE_ROOTS, do not import ml_route_v2 into the harness), distinct, non-empty.
   - `--training-window`: each root's plan is its unsealed chunks from its first priced month
     through range=2024-02-01_2024-03-01 only; under this option check_chunk refuses any chunk
     starting on or after 2024-03-01 (a new Step2ChunkError subclass naming the chunk). When
     STEP2_TRAINING_WINDOW_ONLY is True, --buy without --training-window is refused before any
     vendor call.
   - Quote-only additions for Task 7 (both refused with --buy, both reach only gate.quote under
     install_forbidden_guards): `--holdout2-only` (the 13 sealed chunks 2024-03..2025-03 per root,
     priced, never bought) and `--extension-2010` (monthly chunks from 2010-01-01 to 2019-05-01,
     exclusive, per root; a root with no history there fails its quotes like any unpriceable chunk,
     and MBT is skipped by name since its first priced month is 2021-04). These plans are a separate
     type that check_chunk's buy path can never accept.
   - A set name "ml-v2" (the 28 price paths) usable with --quote-only, and `--quotes-out PATH`
     (default reports/stage_e12_quotes.json, plus the .md beside it) so E.2b's quote file is never
     overwritten. The quote summary reports both accounts' positions (spent, cap, headroom) from the
     gates' own arithmetic.
4. Tests, named so the harness manifest freezes them (check screening/harness_freeze.py's test
   patterns; E.11 used tests/test_stage_e_config_keys.py): the cap arithmetic; key strip and no key
   printed; the E.12 block repointing; training-window plans ending at 2024-02 for an ordinary root,
   for MBT (from 2021-04) and refusing a 2024-03 chunk; the interlock; --roots validation; --account
   wiring (gate account and key loader account, with fakes; no network); holdout2-only and
   extension plans refused for --buy and reaching only quote; the quotes-out path. Update existing
   tests that pin 125.00 or E.5's session to read the constants, never weakening a check.
   Run tests/test_e2b_pull_step2.py, test_spend_gate*.py, test_stage_e_config_keys.py,
   test_harness_freeze.py and your new files; record the exact summary lines.
5. Do NOT write or rebuild the harness manifest (reports/stage_e2b_harness_freeze.json): the lead
   sets E12_SESSION_CAP_USD from the fresh quote and builds the v8 manifest in the main tree. Report
   the exact command that builds and verifies it, and list every harness file you changed.

## Boundaries
Only data/config.py, data/pull_step2.py, docs/ACCESS.md and tests in the worktree. No Databento
call, no key, no network, no other harness file unless a test forces it (then report it). No
commits. nice -n 10.

## Return (at most 200 words) + files
Write the report to /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e12_briefs/keycapfix_report.md
(the main tree's reports folder: the only file you write there): every change with file:line, the
`git -C <worktree> diff --stat`, test summary lines, the manifest build command, and anything open.
Return its path, a summary, and open items.
