# Stage E.26 Task 2 brief: ACCOUNT_3 (ConfigCoder-OpusXHigh)

Stage prompt: /home/kiros-li/Documents/GitHub/PropExperiment/docs/prompts/STAGE_E.26.md, Task 2. V44 in
docs/DECISIONS.md (the last entry) records the user's decision.

## Objective

Add a third Databento account to data/config.py: ACCOUNT_3_ID = "acct-3", key variable
DATABENTO_API_KEY3, selectable exactly the way acct-1 and acct-2 are (require_databento_key(account=...),
data.spend_gate.SpendGate(account=...) and its ledger lines, and the quote tool's account selection),
without changing acct-1's or acct-2's behaviour, their caps, LEGACY_ACCOUNT_ID or the default
ACTIVE_ACCOUNT (stays acct-2). Tests with fake keys only.

Registry entry (lead's ruling): DatabentoAccount("acct-3", ACCOUNT_3_CAP_USD, (), description) with
ACCOUNT_3_CAP_USD = 125.00 and a comment in the file's style giving the source: V44 (a new, temporary
account for the E.28 order-book pilot only, all of its funds on one contract and one schema, the span
never 2024-03-01 or later; the user wipes it after the download is verified); 125.00 is the credit a new
Databento account opens with (U5: acct-2 opened with $125.00), an upper bound only, the balance check at
purchase time governs. No external ledger. Description string: "the temporary E.28 pilot account (V44),
wiped by the user after the download is verified".

## Where you work

You run in an isolated git worktree (your cwd). The main repo at /home/kiros-li/Documents/GitHub/PropExperiment
is being used by the lead for a sealed-data move: never write, edit or run anything that writes there,
except your two output files below. Run tests from your worktree with the main repo's interpreter, e.g.
`/home/kiros-li/Documents/GitHub/PropExperiment/.venv/bin/python -m pytest -q -p no:cacheprovider <files>`,
after confirming `PYTHONPATH=. <that python> -c "import data.config as c; print(c.__file__)"` prints your
worktree's path (if it does not, stop and report). Do not run uv sync or the full suite.

## Allowed changes

- data/config.py: the account registry, DATABENTO_KEY_ENV_BY_ACCOUNT, the new constants and comments,
  nothing else. Keep the file's comment style (dated, sourced comments) and immutability (MappingProxyType,
  frozen dataclass).
- A NEW test file tests/test_e26_account3.py: AAA structure, descriptive names; fake keys only, via
  monkeypatch and tmp_path env files; never the real .env (there is none in your worktree; keep it so).
  Cover at least: acct-3 is registered with its cap and no external ledger; require_databento_key reads
  DATABENTO_API_KEY3 for acct-3 (env, then env file; blank env does not shadow file; missing or empty
  raises MissingSecretError naming the variable, not a value); acct-1 and acct-2 still read KEY1 and
  KEY2 and ACTIVE_ACCOUNT is still acct-2; SpendGate(account="acct-3") sums only acct-3's ledger lines
  and writes ledger lines carrying "account": "acct-3" (use a tmp ledger); acct-3 spend never counts
  toward acct-1 or acct-2 and vice versa; the quote tool's account selection accepts acct-3 (if it
  derives from ACCOUNTS, prove it with a test; never call Databento: mock the client).
- Nothing else. If any other file seems to need a change (the quote tool hard-codes its account
  choices, an existing test pins the registry to exactly two accounts, a spend-gate check rejects a
  third account), STOP before editing it and report the file:line and why. Existing tests are not
  edited by you; the lead rules.

## Facts to report (the lead needs them)

1. The diff (git diff in your worktree) written as a patch to
   /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e26_briefs/task2_config.patch
   (data/config.py and the new test file only; `git diff --binary` plus `git add -N` for the new file).
2. A report at /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e26_briefs/task2_report.md:
   what changed and why; the targeted test runs with exact commands and pass/fail counts, quoted
   (the new file plus the existing account, key, spend-gate and quote tests: grep tests/ for
   ACCOUNT_2_ID, acct-2, DATABENTO_KEY_ENV_BY_ACCOUNT, require_databento_key, SpendGate); for any failing
   existing test, whether it also fails at HEAD in your worktree (git stash, rerun, unstash) so the lead
   can tell new failures from pre-existing ones (some tests may need data files absent from a worktree).
3. Every place a third account flows through without edits: quote tool, spend gate, ledger readers,
   anything iterating ACCOUNTS (file:line), and whether each is safe with acct-3 present (for example a
   loop over ACCOUNTS that would now read a ledger or a key for acct-3 at import or start-check time).
4. Harness impact: data/config.py is listed in reports/stage_e2b_harness_freeze.json (harness v13,
   dd2bcc60...). Do NOT rebuild or edit that manifest. List every test under tests/ and every other
   file that runs the harness preflight or check against the real repo tree or pins v13, so the lead
   knows what the config change will make fail. Also list every freeze manifest (reports/*freeze*.json,
   reports/*.sha256) that pins data/config.py.
5. Anything you could not finish.

## Boundaries

No network, no Databento calls, no .env reads, never print or log a key (tests use obvious fakes such as
"db-FAKE-KEY3"). Do not touch live/, ops/, data files, or any freeze. Do not commit. Do not spawn workers.
Return: the two output paths, a summary of at most 200 words, and anything unfinished.
