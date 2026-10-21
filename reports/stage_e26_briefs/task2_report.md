# Stage E.26 Task 2: ACCOUNT_3 (ConfigCoder-OpusXHigh), report

Worktree: /home/kiros-li/Documents/GitHub/PropExperiment/.claude/worktrees/agent-aeca900d4301d6fb8
(branch worktree-agent-aeca900d4301d6fb8, HEAD 71d667f). Nothing committed. The only index change is
`git add -N tests/test_e26_account3.py` (intent-to-add, needed for the patch).
Patch: reports/stage_e26_briefs/task2_config.patch (sha256 75a8197ce3207bc3...; 2 files;
`git apply --check -R` against the worktree passes). No network, no Databento call, no .env read
(the worktree has no .env), no key printed. The tests use fake keys only.

## 1. What changed and why

data/config.py (sha256 f0e7381ec117... at HEAD -> 9c7871a3bcaf...; +17 -2 lines). Lines below are
post-change line numbers.

- :78 `ACCOUNT_3_ID = "acct-3"`, next to ACCOUNT_1_ID and ACCOUNT_2_ID.
- :96-102 `ACCOUNT_3_CAP_USD = 125.00`, with a dated, sourced comment in the file's style: V44 (new,
  temporary, E.28 order-book pilot only, all funds on one contract and one schema, span never
  2024-03-01 or later, wiped by the user after the download is verified); 125.00 is the credit a
  new Databento account opens with (U5: acct-2 opened with $125.00), an upper bound only, and the
  balance check at purchase time governs; no external ledger.
- :113-116 the registry entry, as ruled: `DatabentoAccount("acct-3", ACCOUNT_3_CAP_USD, (), "the
  temporary E.28 pilot account (V44), wiped by the user after the download is verified")`. ACCOUNTS
  is still a MappingProxyType and DatabentoAccount is still frozen.
- :238 a one-line dated comment, and :242 `ACCOUNT_3_ID: "DATABENTO_API_KEY3"` in
  DATABENTO_KEY_ENV_BY_ACCOUNT. The rule "every account in ACCOUNTS has exactly one entry here"
  still holds.
- :3-8 the module docstring now names DATABENTO_API_KEY3 for acct-3 (Stage E.26, V44), read only
  when the caller names acct-3. This is the only edit outside the registry and key-map block. It is
  documentation only; drop it if the lead wants the narrowest diff.
- Unchanged: acct-1 (cap SHARED_ACCOUNT_CAP_USD 120.00, MLCryptoEngine external ledger), acct-2
  (ACCOUNT_2_CAP_USD 355.38, no external ledger), LEGACY_ACCOUNT_ID (acct-1), ACTIVE_ACCOUNT (acct-2,
  :118), E14_BUY_ACCOUNT (acct-2), every session cap, and require_databento_key's code and messages.
- ruff (`.venv/bin/ruff check --no-cache data/config.py tests/test_e26_account3.py`) reports 7 E501
  lines in data/config.py. HEAD also has 7, all in older comments, so the new lines add none. The
  test file is clean.

tests/test_e26_account3.py (new, 28 tests, AAA, fake keys "db-FAKE-..."). An autouse fixture
deletes DATABENTO_API_KEY1/2/3 and DATABENTO_API_KEY. A module fixture checks that the real
ledger and ACCESS doc are byte-identical afterwards. Every ledger and ACCESS doc is under tmp_path.
Coverage:
- registry: acct-3 is registered with cap 125.00, no external ledger and the ruled description;
  acct-1 and acct-2 entries, ACTIVE_ACCOUNT, LEGACY_ACCOUNT_ID and E14_BUY_ACCOUNT are unchanged;
  the key map is exactly {acct-1: KEY1, acct-2: KEY2, acct-3: KEY3} and covers ACCOUNTS; the
  registry, the map and each entry are read-only.
- key: acct-3 reads KEY3 from the environment; from the env file when the environment lacks it; the
  environment wins over the file; a blank or whitespace environment value does not shadow the file;
  a missing, empty, whitespace-only or commented-out KEY3 raises MissingSecretError naming
  DATABENTO_API_KEY3 and acct-3 and no value, with nothing printed, while KEY1 and KEY2 are present
  (so they never stand in). acct-1 and acct-2 still read KEY1 and KEY2, and the default (None) is
  acct-2's KEY2. KEY3 never stands in for acct-1, acct-2 or the default. An unregistered acct-4 still
  has no key.
- spend gate: SpendGate(account="acct-3") takes cap 125.00, no external ledger and the cap label
  "account cap acct-3". It may tighten the cap but never raise it or add an external ledger. With
  legacy, acct-1, acct-2 and acct-3 lines in one ledger, each gate sums only its own account. Its
  quote, commit and settle lines all carry "account": "acct-3", with acct-3's running total.
  acct-3 spend never moves acct-1's or acct-2's total, and acct-2 spend never moves acct-3's. A quote
  beyond acct-3's headroom is refused naming acct-3 (refused ledger line on acct-3, ACCESS note)
  and a quote exactly at the cap is allowed. An unregistered account (gate or ledger line) still
  fails closed.
- quote tools: the --account choices of data.pull_hist and data.pull_step2 accept acct-3 and refuse
  acct-4. A full `data.pull_hist --quote-only --plan es2011 --account acct-3` run with a fake client
  (billable namespaces trapped, none touched) loads the key with account="acct-3" only, writes 96
  $0.00 quote lines all on acct-3 under E.14's quote session, and reports acct-3's position (cap
  125.00, spent 0.0, headroom 125.00). The fake key appears in no output. pull_hist still buys on
  acct-2 only (require_buy_ready refuses acct-3).

## 2. Test runs (exact commands, counts quoted)

Interpreter check (before any edit), from the worktree:
`PYTHONPATH=. /home/kiros-li/Documents/GitHub/PropExperiment/.venv/bin/python -c "import data.config as c; print(c.__file__)"`
printed `/home/kiros-li/Documents/GitHub/PropExperiment/.claude/worktrees/agent-aeca900d4301d6fb8/data/config.py`.

a) New file alone (from the worktree):
`PYTHONPATH=. nice -n 10 /home/kiros-li/Documents/GitHub/PropExperiment/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_e26_account3.py`
-> "28 passed in 0.69s". The same file against HEAD's data/config.py (copied in temporarily, then
restored; `cmp` confirmed the restore) -> "1 error in 0.64s" (collection: ACCOUNT_3_CAP_USD does
not exist at HEAD).

b) Focused: the new file plus the existing account, key, spend-gate and quote tests (every tests/
file matching ACCOUNT_2_ID|acct-2|DATABENTO_KEY_ENV_BY_ACCOUNT|require_databento_key|SpendGate, 12
files) plus tests/test_compute_datarules.py, which iterates ACCOUNTS:
`PYTHONPATH=. nice -n 10 /home/kiros-li/Documents/GitHub/PropExperiment/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_e26_account3.py tests/test_d1f_holdout2.py tests/test_e14_config_v10.py tests/test_e14_pull_hist.py tests/test_e17_v12_pull_hist.py tests/test_e2b_pull_step2.py tests/test_e2b_pull_step2_e12.py tests/test_pull_universe.py tests/test_quote_universe.py tests/test_spend_gate.py tests/test_spend_gate_accounts.py tests/test_stage_e_config_keys.py tests/test_stage_e_config_v8.py tests/test_compute_datarules.py`
-> "4 failed, 524 passed, 1 skipped in 256.96s (0:04:16)" (02:43 PDT). The 4: test_d1f_holdout2
TestRealStores (fails at HEAD too) and the 3 new failures in section 3.

c) Wide targeted run, before and after, used to tell new failures from old ones. The files: 47
tests/ files matching the account patterns above, ACCOUNTS|ACTIVE_ACCOUNT|LEGACY_ACCOUNT_ID|
MissingSecretError|quote_universe|pull_hist|pull_step2|datarules, or the harness patterns
harness_freeze|HARNESS_SHA256|preflight|dd2bcc60|stage_e2b_harness_freeze|data/config\.py|config\.__file__.
The command, run from the worktree with PYTHONPATH=<worktree>, without PYTHONPYCACHEPREFIX, at
nice 10 (junit xml per run):
`nice -n 10 /home/kiros-li/Documents/GitHub/PropExperiment/.venv/bin/python -m pytest -q -p no:cacheprovider -rfE --junitxml=<run>.xml <the 47 files> [+ tests/test_e26_account3.py after]`
- HEAD, on the clean worktree before any edit (ended 02:28 PDT): "11 failed, 1408 passed, 1
  skipped, 1 warning in 544.92s (0:09:04)". This baseline replaces the brief's stash, rerun and
  unstash step, because the stash stack is shared with other sessions; HEAD was tested first instead.
- After the change, with the new file (ended 02:38 PDT): "15 failed, 1432 passed, 1 skipped, 1
  warning in 530.52s (0:08:50)".
- Per-test diff of the two junit files: exactly 4 tests went from passed to failed (section 3), the
  28 new tests pass, and no test went from failed to passed. These 11 fail in both runs, so they
  are pre-existing and not caused by this change:
  - tests/test_compute_remote_e2e.py, 9 tests: the far-side checkout has no pandas ("agent
    verify-code: no answer ... ModuleNotFoundError: No module named 'pandas'"), an environment
    problem in the worktree.
  - tests/test_d1f_holdout2.py::TestRealStores::test_real_holdout2_is_not_yet_sealed_or_verifies
    (real-store state).
  - tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha:
    h6_rod pins v12 (ece91ae8...) and the manifest is v13. This is the known "v13 breaks earlier
    freezes" case.

## 3. Existing tests the change makes fail (not edited; the lead rules)

1. tests/test_stage_e_config_keys.py:56-62 `test_each_account_maps_to_its_numbered_variable` pins the
   key map to exactly `{ACCOUNT_1_ID: KEY1, ACCOUNT_2_ID: KEY2}`. Minimal fix if ruled: add
   `ACCOUNT_3_ID: "DATABENTO_API_KEY3"`.
2. tests/test_stage_e_config_keys.py:256-268 `test_unknown_account_raises_naming_the_account[acct-3]`
   uses "acct-3" as its example of an unregistered account. It is now registered, so the
   MissingSecretError message is the missing-variable one ("DATABENTO_API_KEY3 (the Databento key of
   account acct-3) is not set, ...") and does not contain `repr('acct-3')`. Minimal fix if ruled:
   replace "acct-3" with "acct-4" in the parametrize list at :256.
3. tests/test_e2b_pull_step2_e12.py:446
   `test_holdout2_only_quotes_reach_only_gate_quote_and_report_both_accounts` asserts
   `set(positions) == {"acct-1", "acct-2"}` and fails with `{'acct-1', 'acct-2', 'acct-3'}`. The
   assert at :453-454 (combined_headroom_usd == acct-1 + acct-2 headroom) would fail next, because
   acct-3 adds $125.00. The cause is the code path at data/pull_step2.py:1157, which builds one gate
   per ACCOUNTS entry for the quote summary (section 4). The lead has two options: (a) update the
   test to expect acct-3's position (spent 0.0, cap 125.00, headroom 125.00) and a combined
   headroom that includes it; or (b) keep the step 2 summary on acct-1 and acct-2, which is a code
   change in data/pull_step2.py, outside this brief.
4. tests/test_harness_freeze.py:89-93 `test_the_real_tree_matches_the_committed_manifest_when_it_exists`
   runs hf.check(REPO_ROOT) on the real tree. The single problem it now reports (reproduced
   directly with hf.check(REPO_ROOT, v13 sha)): "data/config.py: sha256 9c7871a3bcaf... differs from
   the frozen f0e7381ec117...". Only a manifest rebuild resolves it (section 5).

No other file needed a change. Neither quote tool hard-codes its account choices (both derive them
from ACCOUNTS). No spend-gate check rejects a third account (resolve_account reads ACCOUNTS).

## 4. Where acct-3 flows through without edits

Post-change line numbers for data/config.py; every other file is unchanged.

- data/spend_gate.py:149-157 `resolve_account` (ACCOUNTS.get): acct-3 resolves. Safe.
- data/spend_gate.py:161-165 `entry_account`: an "account": "acct-3" ledger line now counts as
  acct-3. Before the change, such a line would have closed every gate that reads the ledger
  (UnknownAccountError). Safe, and needed.
- data/spend_gate.py:168-171 `account_committed_usd`: per-account sums, so acct-3 is excluded from
  acct-1 and acct-2 (tested). Safe.
- data/spend_gate.py:250-266 `SpendGate.__init__`, :213-230 `_account_ledgers`, :233-240
  `_account_cap`: an acct-3 gate gets cap 125.00 and no external ledger. Safe. :323 `_append`
  stamps "account": self.account_id. Safe.
- data/spend_gate.py:279-281 `session_spent_usd` sums every line of a session id, whatever its
  account (pessimistic, documented). acct-3 spend under a reused session id would count toward that
  session's cap. Safe, but E.28 should use its own session id. The same holds for the
  quote-dedupe readers keyed by session only: data/pull_hist.py:450-453 `_quoted_keys`,
  data/pull_step2.py:671 `successful_quote_keys`, data/quote_universe.py:423 `already_quoted`.
- data/spend_gate.py:258 SpendGate's default account is still acct-1 (LEGACY), and
  data/config.py `require_databento_key` still defaults to ACTIVE_ACCOUNT (acct-2). Neither default
  is acct-3, so E.28 code must pass account="acct-3" to both the gate and the key loader. If one is
  left out, it lands on acct-1 or acct-2. Safe as written, but a trap for E.28.
- data/pull_hist.py:742 `--account choices=tuple(ACCOUNTS)`: accepts acct-3. At :808, :816 and
  :337-342 / :356-361, a quote gate is built on acct-3 under STAGE_E14_SESSION_ID, or under E.17's
  session for ext2010h. At :830, key_loader(account="acct-3") reads KEY3. The quotes are $0.00
  lines; the plans are es2011, ext2010 and ext2010h only (ohlcv-1m, no order-book plan).
  :396-402 `require_buy_ready` refuses any buy not on E14_BUY_ACCOUNT (acct-2), so acct-3 cannot buy
  through pull_hist (tested). Safe.
- data/pull_step2.py:1006 `--account choices=tuple(ACCOUNTS)`: accepts acct-3. At :1132 and
  :1141, the quote or buy gate is built on the named account. :1186-1201 hands --plan runs to
  pull_hist with the same argv.
  - :1157 on --quote-only, `{a: ... _gate_on(gate_factory, a) for a in ACCOUNTS}` now also builds an
    acct-3 gate at start-check time. It reads only this repo's ledger: acct-3 has no external
    ledger, so it cannot fail closed on a missing file, and no key is read for it (key_loader is
    called once, for the selected account, at :1162). Safe to run, but the output changes: the
    quotes JSON and MD (:718-723 `accounts_summary`, :1217-1223) now show three positions, and
    `combined_headroom_usd` includes acct-3's $125.00. Its docstring says "the E.12 session caps may
    never exceed it", so anyone sizing an E.12-style cap from it would overstate the headroom by
    acct-3's. It is informational, not a gate. This is failure 3 above.
  - :703-716 `account_position`: for acct-3, credit shows its cap. Safe.
  - :612-615 `require_buy_caps` accepts any registered account passed explicitly, so
    `pull_step2 --buy --account acct-3` now passes the account check. It is still behind the
    harness preflight (:1153, which fails until the manifest is rebuilt), the E.12 session cap
    ($137.73, summed over all accounts' E.12 lines), the $3.00 request cap and
    STEP2_TRAINING_WINDOW_ONLY. V44 allows acct-3's funds only for the pilot's one contract and
    schema, so this is a new path for acct-3 spend on step 2 ohlcv-1m chunks. There is no guard
    against it in this diff. Flagged for the lead.
  - :71 the module docstring still says `--account acct-1|acct-2` (stale text only).
- data/pull_universe.py:450-453 and :766-768 (gate on ACTIVE_ACCOUNT only, no --account),
  data/quote_universe.py:270-275 and :765 (E.0 gate on the acct-1 default, key on ACTIVE_ACCOUNT, no
  account option), and data/pull_mes.py:104 and :107: none of these select an account, so none
  can reach acct-3. Unaffected.
- compute/datarules.py:84-90 `default_rules` iterates ACCOUNTS for external ledgers. acct-3 adds
  none. Safe.
- data/config.py `require_databento_key` reads only the variable of the account asked for. The
  unknown-account message lists account ids, never values. Nothing in the repo loops over
  ACCOUNTS or DATABENTO_KEY_ENV_BY_ACCOUNT at import time to read a key.
- Historical scripts that hard-code ("acct-1", "acct-2") (reports/stage_e12_briefs/rank_phase1.py:68,
  :100, :126; reports/stage_e15_briefs/fresh_quote_guard.py:32; reports/stage_e17_briefs/*) are not
  run paths and are unaffected.
- The brief's "quote tool's account selection": the account-selecting quote tools are
  data.pull_hist and data.pull_step2 (--quote-only --account). data.quote_universe has no account
  option.

## 5. Harness impact (nothing rebuilt or edited)

Manifests that pin data/config.py:
- reports/stage_e2b_harness_freeze.json (harness v13, sha256 dd2bcc60...): files["data/config.py"] =
  {sha256 f0e7381ec11727f4..., bytes 16184}, category harness_code. This matches HEAD. After the
  change, hf.check(REPO_ROOT, v13) reports exactly one problem, the data/config.py mismatch above.
- reports/stage_d1f_harness_freeze.json: files["data/config.py"] = a534698fb24435d8.... This was
  already stale at HEAD (HEAD's file is f0e7381e...), so the change does not alter its status.
- reports/stage_e1_freeze.json and reports/stage_e12_ml_v2_freeze.json name data/config.py only in
  note text (E.1: "not frozen by this manifest ... data/config.py's account registry"); neither has a
  hash. No reports/*.sha256 or reports/*/*.sha256 file pins it.
- The new tests/test_e26_account3.py is outside HARNESS_DIRS and does not match
  screening/harness_freeze.py TEST_PATTERNS (:274-277), so v13 neither lists it nor reports it as
  unlisted. A v14 rebuild would not include it unless the patterns change.

Tests that run the harness check or preflight on the real tree, or pin a harness hash:
- tests/test_harness_freeze.py:89-93: real-tree check, now fails (failure 4).
- tests/test_h6_rod_run.py: runs the h6_rod CLI preflight against the real tree with v12
  (h6_rod/constants.py:95). It already fails at HEAD.
- tests/test_pattern_search_run.py and tests/test_pattern_search_world_check.py use
  pattern_search/constants.py:87 (v12) with fake hooks, and pass both before and after.
- No test in tests/ contains the v13 literal dd2bcc60. Every other harness test builds a tiny tmp
  repository and manifest (tests/_compute_fixtures.py:112-122, tests/test_harness_freeze.py tiny
  roots, tests/test_compute_*), and all of them pass after the change.

Run paths that preflight the real tree and will refuse the v13 sha until the manifest is rebuilt:
- Pinned in code: trigger_hold/events.py:69 (HARNESS_SHA256 = dd2bcc60..., "# v13"), used at :263;
  trigger_hold/events_h6.py:108; trigger_hold/events_validate.py:64 (EV.HARNESS_SHA256).
- Taking --harness-sha256:
  - data/pull_step2.py:948, :1153
  - data/pull_hist.py:657, :828
  - data/step2_store.py:496, :540
  - data/hist_store.py:435, :514
  - screening/stage_e_runner.py:476, :645, :665, :781, :846
  - screening/stage_e_start_dates.py:423
  - screening/stage_e_verdict.py:773
  - screening/trial_registry.py:261
  - ml_route/train.py:40
  - ml_route/test.py:89
  - ml_route_v2/phase1/cli.py:62
  - compute/agent.py:54
  - compute/remote.py:70
  - c1_replication/c1b.py:115
  - c1_replication/evaluate.py:549, :605
- pattern_search/run.py:76 and h6_rod/run.py:117 pin v12 and have refused since v13.
- Historical verifier scripts: reports/stage_e15_briefs/verify_freeze.py:115,
  reports/stage_e17_briefs/verify_freeze.py:115, reports/stage_e17_c1_verify/verify_hashes.py:29
  and :83 (older pins).

## 6. Not finished or not verified

- The full suite was not run (brief). The wide targeted run covers 48 files, about 1,450 tests.
- The 9 compute_remote_e2e failures could not be checked in this worktree (no pandas on the far
  side). They fail identically before and after the change, and the change does not touch
  compute/.
- Not decided, because each is reserved for the lead: the three test edits in section 3, whether
  pull_step2's summary should include acct-3, whether `pull_step2 --buy --account acct-3` should be
  blocked, and the harness manifest rebuild.

## Follow-up (lead ruling, harness v14 minimal set; 02:47-02:58 PDT 2026-10-21)

### Edits
Same worktree. data/config.py is unchanged since the first patch, docstring lines kept. No other
file was edited. `git status --short` shows exactly ` M data/config.py`, ` A tests/test_e26_account3.py`,
` M tests/test_e2b_pull_step2_e12.py` and ` M tests/test_stage_e_config_keys.py`.

1. tests/test_stage_e_config_keys.py:62-63 (was :61): a new comment line,
   `# Stage E.26 (V45): acct-3, the temporary E.28 pilot account, reads DATABENTO_API_KEY3.`, and
   the assert changed to
   `assert mapping == {ACCOUNT_1_ID: KEY1, ACCOUNT_2_ID: KEY2, "acct-3": "DATABENTO_API_KEY3"}`.
2. tests/test_stage_e_config_keys.py:257-258 (was :256): a new comment line,
   `# Stage E.26 (V45): acct-3 is registered now (the E.28 pilot account); acct-9 is not.`, and
   the parametrize changed to `["acct-9", "", "ACCT-1", "acct_1"]`. The test body and its assertions
   are unchanged.
3. tests/test_e2b_pull_step2_e12.py:446-450, :457-459 and :463:
   - a new comment line, `# Stage E.26 (V45): the summary covers every registered account, now
     acct-3 (no spend here).`;
   - `set(positions) == {"acct-1", "acct-2", "acct-3"}`;
   - three new asserts: acct-3 spent_usd == 0.0, account_cap_usd == config.ACCOUNT_3_CAP_USD, and
     cap_headroom_usd == approx(ACCOUNT_3_CAP_USD);
   - combined_headroom_usd now also adds acct-3's cap_headroom_usd (trailing `# Stage E.26 (V45)`
     comment);
   - `assert "| acct-3 |" in md`. The .md really contains it, because data/pull_step2.py:1221
     writes one table row per position, and the test passes with it.
   Every other assertion is kept.

Both edited test files match harness_freeze TEST_PATTERNS (`test_stage_e_*.py`, `test_e2b_*.py`),
so v13 lists them. hf.check(REPO_ROOT, v13 sha) in the worktree now reports 3 problems, all of which
the v14 rebuild must cover:
- data/config.py 9c7871a3bcaf... (frozen f0e7381ec117...)
- tests/test_e2b_pull_step2_e12.py 6292c9d680b7... (frozen 2a0bcd4b663b...)
- tests/test_stage_e_config_keys.py e8d9af3c50de... (frozen b919ff500d5f...)

Patch regenerated (`git diff --binary` over the 4 files, the new file intent-to-add):
reports/stage_e26_briefs/task2_config.patch, sha256 0f9f84e0db8d2d4f..., 4 files, +512 -6.
`git apply --check -R` passes. ruff on the two edited test files: "All checks passed!".

### Counts (same 47 files plus the new one, same command and interpreter, ended 02:57 PDT)
- The two edited files alone: "88 passed in 20.67s".
- The 48 files: "12 failed, 1435 passed, 1 skipped, 1 warning in 525.67s (0:08:45)".
- Per-test diff against the HEAD baseline (11 failed, 1408 passed, 1 skipped): the only test that
  changed from passed to failed is tests/test_harness_freeze.py::test_the_real_tree_matches_the_
  committed_manifest_when_it_exists (expected until v14). The other 11 failures are the
  pre-existing ones (9 compute_remote_e2e, d1f_holdout2 TestRealStores, h6_rod_run). The
  `[acct-3]` case was renamed `[acct-9]` and passes, and the 28 new tests pass.

### Every buy path that accepts --account acct-3, and what stops it now

There are two CLIs with an --account option, both deriving their choices from ACCOUNTS:
data/pull_step2.py:1006 and data/pull_hist.py:742.

1. `python -m data.pull_step2 --buy --account acct-3 ...` (step 2 plan, ohlcv-1m only:
   data/pull_step2.py:366 and :380-392). This path is NOT stopped by an account check.
   - What happens, in order:
     - :1094-1106 `_check_buy_args` requires --harness-sha256 and --account, and refuses the
       quote-only plans.
     - :623-628 `require_training_window`: --training-window is required while
       data/config.py:177 `STEP2_TRAINING_WINDOW_ONLY = True`.
     - :1141 the gate is `step2_gate(account="acct-3")`, under STEP2_PURCHASE_SESSION_ID (the E.12
       session, config :183) with session cap $137.73 (config :172/:184) and request cap $3.00.
     - :1153 `harness_freeze.preflight(--harness-sha256)`.
     - :1155 / :612-615 `require_buy_caps` accepts any registered account named explicitly, so
       acct-3 passes.
     - :1162 key_loader(account="acct-3") reads KEY3.
     - run_buy :942-959: preflight again (:948), caps (:949), window (:950), `validate_plan` (:425,
       nothing from 2024-03-01), and `check_chunk` per chunk.
     - per chunk, the gate's authorize: the E.12 session cap, summed over all accounts' E.12 lines;
       the $3.00 request cap; and acct-3's $125.00 account cap.
   - What stops it today:
     - the harness preflight only, because the v13 sha no longer matches. Once the v14 manifest is
       rebuilt and its sha is passed, nothing account-specific stops it.
     - the remaining E.12 session headroom bounds it: $137.73 - $133.723742 = $4.006258. That is
       the E.12 session spend in the worktree's ledger copy at HEAD (36,402 lines: acct-1
       $26.797773 + acct-2 $106.925969); the main tree's live ledger may differ.
     - a chunk already on disk from an acct-1 or acct-2 buy stops the run with ResumeStateError
       (:913-920, "file without a settled ledger line"), because settled keys are per account
       (:954).
   - So after v14, an acct-3 run could spend up to about $4.01 on not-yet-bought training-window
     ohlcv-1m chunks of the step 2 roots. That breaks V44's "pilot only" limit, and no code
     prevents it.
2. `python -m data.pull_hist --buy --plan <es2011|ext2010|ext2010h> --account acct-3` (ohlcv-1m),
   and the same via `data.pull_step2 --plan ... --buy --account acct-3` (data/pull_step2.py:1126,
   handed to pull_hist.main). This path IS stopped by an account check.
   - :768 `_check_args` requires --harness-sha256, --account, and --roots for ext2010h.
   - :818 builds the buy gate on acct-3 under the plan's session.
   - :828 runs the preflight.
   - :829 / :396-402 `require_buy_ready` refuses any account but E14_BUY_ACCOUNT (config :215,
     acct-2): UnknownAccountError "plan ... buys on acct-2 only". This happens before the key is
     loaded (:830) and before any vendor call, and run_hist_buy repeats it at :658.
   - Even without that check, the session caps would bound it: es2011 $0.00 (config :202); ext2010
     $59.47 (:212, $57.817332 spent); ext2010h $65.82 (:232, $64.038166 spent).
3. No other buy or download path can select acct-3. data/pull_universe.py (gate must be on
   ACTIVE_ACCOUNT, :766-768) and data/pull_mes.py:104-107 load the key with
   `require_databento_key()`, which defaults to acct-2's KEY2. So do data/build_mes_bars.py:82 and
   :334, data/step2_store.py:528, data/build_bars_run.py:135 and compute/remote.py:125. None of
   them has an account option.

## Follow-up 2 (lead ruling: enforce V44's "acct-3 is spent only by the E.28 pilot purchase" in code)

Edits made 03:00-03:05 PDT. The 48-file rerun ran 03:05-03:13 PDT. The report and patch were
finished 05:12 PDT, after the usage-limit pause; nothing was redone after it, and the worktree diff
was checked first.

### Edits
1. data/config.py:118-121 adds a 3-line dated comment, "Pilot-only accounts (Stage E.26,
   2026-10-21; V44, V45): spent only by Stage E.28's order-book pilot purchase; no existing puller
   may buy on them (data.pull_step2.require_buy_caps refuses them; data.pull_hist buys on
   E14_BUY_ACCOUNT only)", followed by `PILOT_ONLY_ACCOUNTS: frozenset[str] =
   frozenset({ACCOUNT_3_ID})`. It sits right after ACCOUNTS and before ACTIVE_ACCOUNT. Nothing
   else in the file changed.
2. data/pull_step2.py has two edits:
   - :119 imports PILOT_ONLY_ACCOUNTS from data.config.
   - :613-629 `require_buy_caps`: the docstring gains one sentence (Stage E.26, V44, V45). Before
     `require_account` and the cap check, it now refuses with **Step2Error** when either the named
     account (ACTIVE_ACCOUNT if None) or the gate's account is in PILOT_ONLY_ACCOUNTS, with "step 2
     buy refused: account acct-3 is pilot-only (V44: spent only by Stage E.28's order-book pilot
     purchase); no step 2 buy may run on it".
   - I used Step2Error rather than UnknownAccountError because acct-3 is a registered account, so
     "unknown" would be wrong. Both errors are caught by main's refusal handler (:1171,
     RC_REFUSED), and Step2Error is also caught by the run-stopped handler (:1184).
   - Nothing else in the file changed.
3. tests/test_e26_account3.py gains 8 new test items, 36 in total:
   - `test_acct3_is_the_only_pilot_only_account`
   - `test_pull_step2_buy_on_acct3_refuses_before_any_key_load_or_vendor_call`: full CLI with
     --roots ZN --training-window; the preflight is patched to pass, so the account guard is what
     refuses. It asserts RC_REFUSED, no key load, no client built, no ledger line, no ACCESS note,
     and that the stderr names acct-3, V44 and "pilot-only".
   - `test_pull_step2_run_buy_refuses_a_gate_on_acct3_before_touching_the_client[None|acct-3]`:
     run_buy called directly with a gate on acct-3, whether or not the account is named. Step2Error
     is raised, the client is not touched at all, and no ledger line is written.
   - `test_require_buy_caps_still_passes_acct1_and_acct2_gates`
   - `test_pull_hist_buy_on_acct3_refuses_before_any_key_load_or_vendor_call[es2011|ext2010]`:
     RC_REFUSED, "buys on acct-2 only", no key, no client, no ledger line, no registry file.
   - `test_the_pull_step2_plan_hand_off_on_acct3_is_refused_by_pull_hist`: `pull_step2 --buy
     --plan ext2010 --account acct-3` is refused by pull_hist's account check before any key or
     client. Its default gate only reads the ledger.
   - RED was confirmed before the code edit: the 4 step 2 tests failed. The CLI run returned
     RC_STOPPED (1) after loading the key and building the client, and failed at the first vendor
     quote. run_buy reached the vendor quote too. That proves the gap was real. The 3 pull_hist
     tests already passed.

### Every buy path in data/ and whether it can reach acct-3 now
- data/pull_step2.py: every step 2 buy passes `require_buy_caps`. The CLI calls it at :1163,
  before key_loader at :1170. `run_buy` calls it at :957, right after its preflight (:956) and
  before any client use. `_acquire_kept`, `_acquire_sealed` and `_buy` (the only callers of
  gate.commit, :846, and timeseries.get_range) run only inside run_buy's chunk loop. So acct-3 is
  refused on every pull_step2 buy. It is not refused on quotes, which are $0.00 and still allowed.
- data/pull_step2.py --plan (hand-off, :1126 to pull_hist.main): pull_hist.require_buy_ready
  (:396-402, called at :829 and :658) refuses any account but E14_BUY_ACCOUNT (acct-2), before the
  key load. Tested both directly and through the hand-off.
- data/pull_universe.py: the gate must be on ACTIVE_ACCOUNT (:766-768), and the key is
  require_databento_key()'s default, acct-2. It has no account option, so it cannot reach acct-3.
- data/pull_mes.py: d1f_gate (:184-189) and SpendGate(STAGE_A1_SESSION_ID) (:107) sit on acct-1
  by default, and the key comes from the default (:104); adapter.fetch_range (data/adapter.py:
  111-117) is used only through these. They cannot reach acct-3.
- data/build_mes_bars.py:82 and :334, data/step2_store.py:528, data/build_bars_run.py:135 and
  compute/remote.py:125 load require_databento_key() with no account (acct-2) and have no account
  option. They cannot reach acct-3.
- The E.28 pilot purchase code does not exist yet. It must name acct-3 in both the gate and the
  key loader, and it must not go through pull_step2's buy path, which now refuses acct-3.

### Counts (same 48 files, same command and interpreter; started 03:05:17, ended 03:13 PDT)
- New file alone: "36 passed in 1.50s" (36 items; the 37 new passing items in the 48-file diff are
  these 36 plus the renamed `[acct-9]` case).
- The new file plus tests/test_e2b_pull_step2_e12.py and tests/test_e2b_pull_step2.py: "134 passed
  in 152.16s".
- The 48 files: "12 failed, 1443 passed, 1 skipped, 1 warning in 518.00s (0:08:37)".
- Per-test diff against the HEAD baseline (11 failed, 1408 passed, 1 skipped):
  - The only test that went from passed to failed is tests/test_harness_freeze.py::test_the_real_
    tree_matches_the_committed_manifest_when_it_exists (expected until v14).
  - The other 11 failures are the pre-existing ones (9 compute_remote_e2e, d1f_holdout2
    TestRealStores, h6_rod_run).
  - Every acct-1 and acct-2 buy test in test_e2b_pull_step2*.py and test_e14/e17 pull_hist passes.
  - `[acct-3]` became `[acct-9]`, and 37 new test items pass (36 in the new file, plus `[acct-9]`).
- ruff: data/pull_step2.py and tests/test_e26_account3.py report "All checks passed!".
  data/config.py has 7 E501, the same pre-existing count as HEAD; the new lines are all 100
  characters or fewer.

### Harness check (v13 sha, worktree): the v14 rebuild must cover 4 files
- data/config.py 74f509314ced... (frozen f0e7381ec117...)
- data/pull_step2.py 91f50a84aee0... (frozen 6a57461b03ce...)
- tests/test_e2b_pull_step2_e12.py 6292c9d680b7... (frozen 2a0bcd4b663b...)
- tests/test_stage_e_config_keys.py e8d9af3c50de... (frozen b919ff500d5f...)

tests/test_e26_account3.py is neither listed nor scanned by v13.

### Patch
reports/stage_e26_briefs/task2_config.patch, regenerated with `git diff --binary` over 5 files
(data/config.py, data/pull_step2.py, tests/test_e26_account3.py as intent-to-add,
tests/test_stage_e_config_keys.py, tests/test_e2b_pull_step2_e12.py), +671 -8, sha256
247651d412b36b8d.... `git apply --check -R` passes. `git status --short` lists exactly these 5
files. Nothing is committed and no manifest was touched.
