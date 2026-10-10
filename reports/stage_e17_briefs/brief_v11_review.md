# Brief: HarnessReviewer-FableXHigh (worker-xhigh, model fable) - review of harness v11 (Stage E.17 step 6)

Written by the E.17 lead. Independent, adversarial check of a frozen-file change. You did not write it. Do not spawn
workers. Do not commit. Write only your review file.

## One objective

Decide whether the uncommitted harness v11 (the working tree of /home/kiros-li/Documents/GitHub/PropExperiment
against HEAD) is exactly what C1's freeze and the hand-off allow, and whether its two cap values are right.

## Binding rules (read these sections)

- reports/stage_e14_prereg_C1.md section 9 step 6 and section 11 (the last paragraph, item (2)): a harness that
  "differs from v10 only in data/config.py (ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and the comments beside
  them) and in the test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33;
  tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64), nothing else".
- reports/stage_e16_handoff.md section 1 steps 5-6: ACCOUNT_2_CAP_USD = acct-2's spend (231.599730 unless the
  ledger moved) + the fresh total x 1.03, rounded UP to the cent; E14_EXT2010_SESSION_CAP_USD = the fresh total
  x 1.03 rounded DOWN to the cent, never above $60.00 (V27).
- docs/prompts/STAGE_E.17.md amendment A1 with docs/DECISIONS.md's V30 amendment (the last V30 entry): total spend in
  the stage at most $124.00; every cap is bounded by it.
- reports/E.15_RETURN.md section 6 item 14: the freeze's citation "test_stage_e_config_v8.py:62-64" is off by two;
  the assertions pinning the cap are lines 64-65 there.
- The lead's reading (open choice, to be checked): tests/test_e14_pull_hist.py:196 also pins
  E14_EXT2010_SESSION_CAP_USD (`(ext.session_id, ext.session_cap_usd) == ("stage-E.14-ext2010", 0.0)`) though the
  freeze's citation list omits it; it failed on v11 and the lead changed it to 59.47 under the freeze's governing
  words "the test assertions that pin those two values". Rule on whether that is within the freeze.
- The v11 manifest sha256 the lead computed: ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292 (v10:
  fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b). ledger/databento_spend.jsonl also shows 642 new
  $0.00 quote lines in `git diff`: they are the quote run's, not part of v11, and are committed later with C1's result.

## Inputs

- `git diff HEAD --stat` and `git diff HEAD` (data/config.py, three test files, reports/stage_e2b_harness_freeze.json).
- The fresh quote: reports/stage_e17_briefs/quote_ext2010.log (its first lines give the ledger line count before the
  run and the UTC start), the ledger ledger/databento_spend.jsonl (read only the lines after that count, by script),
  the lead's guard output reports/stage_e17_briefs/fresh_quote_c1.json. Do not trust either the guard output or the
  tool's JSON: recompute the fresh total yourself from the run's own new ledger lines (one successful quote per chunk
  of plan ext2010's 642: data.pull_hist.plan_chunks(get_plan("ext2010")), session stage-E.14-2026-10-05, account
  acct-2, ts >= the run start, usd 0.0).
- acct-2's spend: `data.spend_gate.SpendGate(session_id="review-readonly", account="acct-2").account_spent_usd()`.
- The v10 manifest is at HEAD (`git show HEAD:reports/stage_e2b_harness_freeze.json`); the v11 manifest is the
  working file.

## Checks (each one PASS or a finding)

1. The changed files are exactly data/config.py, tests/test_e14_config_v10.py, tests/test_e14_pull_hist.py,
   tests/test_stage_e_config_v8.py and reports/stage_e2b_harness_freeze.json; no untracked .py under a harness
   directory (screening.harness_freeze's scan).
2. data/config.py: the only changed statements are the assignments of ACCOUNT_2_CAP_USD and
   E14_EXT2010_SESSION_CAP_USD; every other changed line is a comment beside them.
3. The values: recompute the fresh total; ACCOUNT_2_CAP_USD = ceil_cent(spend + total x 1.03);
   E14_EXT2010_SESSION_CAP_USD = floor_cent(total x 1.03), <= 60.00 and <= 124.00; under the new caps
   `data.pull_hist.require_buy_ready`'s condition holds (session cap left <= account headroom) and the buy cannot
   spend more than the session cap.
4. The tests: only the cited assertions changed (with the off-by-two read of test_stage_e_config_v8.py), each now
   pinning the new value; nothing else in those files changed. Run, at nice 10 with -p no:cacheprovider:
   tests/test_e14_config_v10.py tests/test_e14_pull_hist.py tests/test_stage_e_config_v8.py
   tests/test_spend_gate_accounts.py tests/test_pull_universe.py tests/test_e2b_pull_step2.py
   tests/test_e2b_pull_step2_e12.py tests/test_c1_*.py (report the counts). Do not run the full suite.
5. The manifest: `uv run python -m screening.harness_freeze verify --expected <sha256 of the working manifest>`
   passes (use a fresh PYTHONPYCACHEPREFIX outside the repo); the v11 manifest's entries differ from v10's only in
   the changed files' sha256 and bytes (compare the JSON entries; categories, file list and other fields equal).
6. Nothing in reports/stage_e16_freeze.json changed (`uv run python reports/stage_e16_briefs/freeze_manifest.py
   verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4`).

## Boundaries

No vendor call, no .env or key read, no write to ledger/ or to any repo file except your review file, no commit. Read
large files by section or by script, never whole.

## Output

Write reports/stage_e17_review.md with a section "## v11 review (HarnessReviewer-FableXHigh)": each check, its
result, and findings graded BLOCKING, SHOULD FIX or NOTE, each with the evidence (command and output line). Return the
path, a summary of at most 200 words with your verdict (APPROVE, APPROVE WITH FIXES, or BLOCK), and anything you could
not finish.
