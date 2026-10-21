# Stage E.26 Task 2 review: ACCOUNT_3 patch and scripts/set_databento_key3.sh

Reviewer: ConfigReviewer-FableXHigh (Fable 5.1, xhigh), independent of the worker
(ConfigCoder-OpusXHigh). Review window 05:12-05:30 PDT, 2026-10-21.

Inputs, as given: reports/stage_e26_briefs/task2_config.patch (sha256 247651d412b36b8d...; 5 files,
+671 -8), reports/stage_e26_briefs/task2_report.md (with Follow-up and Follow-up 2), the worker's
worktree .claude/worktrees/agent-aeca900d4301d6fb8, scripts/set_databento_key3.sh (untracked, 697
bytes, mode 775), docs/DECISIONS.md V43/V44, docs/prompts/STAGE_E.26.md Task 2, and (follow-up)
the main repo with the patch applied and the v14 manifest. Nothing in the main repo was edited,
applied or committed by me; no .env was read (the worktree has none, the main repo's was not
opened); no network. Line numbers below are post-patch and identical in the worktree and the
main repo (the four applied files are byte-identical, see section C).

What I verified myself (not taken from the report)
- The patch equals `git diff --binary` over the 5 files in the worktree (same sha256 247651d4...).
- `PYTHONPATH=. .venv/bin/python -c "import data.config as c; print(c.__file__)"` from the
  worktree prints the worktree path.
- Targeted run from the worktree: tests/test_e26_account3.py, test_stage_e_config_keys.py,
  test_e2b_pull_step2_e12.py, test_spend_gate_accounts.py, test_spend_gate.py,
  test_e14_pull_hist.py, test_compute_datarules.py: "225 passed in 23.21s". The full suite was
  not run (brief).
- Every repo-wide claim below (who iterates ACCOUNTS, which freezes pin which files, which pins
  carry the v13 sha) comes from my own greps and manifest scans, listed inline.

## A. Findings on the patch

No BLOCKING finding.

### A1. SHOULD FIX: the step 2 quote summary now reports headroom that step 2 may not spend
Evidence: data/pull_step2.py:1165 builds one gate per entry of ACCOUNTS for `--quote-only`
(`for a in ACCOUNTS`), and accounts_summary at :726-731 sums every position into
`combined_headroom_usd`; its docstring (:727-728) says "the E.12 session caps may never exceed
it". Since Follow-up 2, require_buy_caps at :613-629 refuses every step 2 buy on acct-3, so the
combined figure now includes $125.00 (acct-3's full cap, test_e2b_pull_step2_e12.py:457-459
asserts exactly that) that no step 2 purchase can use. The .md (:1230-1231) prints the same
number as "Combined headroom".
Failure scenario: a later lead sizes an E.12-style step 2 session cap from the quotes JSON or .md,
as the docstring invites, and sets it up to $125.00 above what acct-1 and acct-2 can actually
fund. The account caps still bound each account (decide, data/spend_gate.py:174-212), so no
account overspends its own cap; the damage is a session cap documented as a bound that is not
one. Not a spend risk for acct-3 (the guard holds); a documentation and consistency defect.
Fix, one of two, both one line in data/pull_step2.py (either changes data/pull_step2.py's hash,
so apply it before the single v14 rebuild and the commit; see section C):
  (a) keep the lead's ruling (summary covers every registered account) and make the docstring
      true, :727-728: "Every registered account's position (spent, cap, headroom), each from its
      own gate, and their combined headroom. Pilot-only accounts (PILOT_ONLY_ACCOUNTS) are listed
      but may not be spent by step 2, so a step 2 session cap is bounded by the non-pilot
      positions, not by combined_headroom_usd." No test changes.
  (b) exclude pilot-only accounts from the combined figure only, :730:
      `combined = round(sum(p["cap_headroom_usd"] for a, p in positions.items() if a not in
      PILOT_ONLY_ACCOUNTS), 6)`, and change the test's combined assert (:457-459) back to
      acct-1 + acct-2 (keep the three acct-3 position asserts and the `| acct-3 |` row).
I recommend (a): it is docstring-only and keeps the ruling. The lead decides.

### A2. NOTE: acct-1, acct-2, LEGACY_ACCOUNT_ID, ACTIVE_ACCOUNT and every existing path are unchanged
Checked, with evidence:
- data/config.py: ACCOUNT_1/2 entries (:105-112), SHARED_ACCOUNT_CAP_USD, ACCOUNT_2_CAP_USD,
  LEGACY_ACCOUNT_ID (:79), ACTIVE_ACCOUNT (:122, acct-2), E14_BUY_ACCOUNT (:219, acct-2), the key
  map's acct-1/acct-2 lines (:244-245) and require_databento_key (:268-293) have no diff. The
  function reads only the variable of the account asked for; the unknown-account message lists
  ids (`', '.join(DATABENTO_KEY_ENV_BY_ACCOUNT)`), never values. The new test
  test_key3_never_stands_in_for_acct1_acct2_or_the_default proves KEY3 does not leak sideways.
- data/spend_gate.py: untouched. resolve_account (:149-157), entry_account (:161-165) and
  account_committed_usd (:168-171) are per-account, so acct-3 lines never enter acct-1's or
  acct-2's total (tested). SpendGate.__init__ (:250-266) still defaults to acct-1.
- Everything that iterates ACCOUNTS in run code (my grep over the main tree, tests excluded):
  compute/datarules.py:86 (external ledgers only; acct-3 adds none), data/pull_hist.py:742 and
  data/pull_step2.py:1014 (`--account` choices), data/pull_step2.py:1165 (A1), and the message
  texts at data/spend_gate.py:155 and data/pull_step2.py:1113. No test asserts the literal
  "acct-1, acct-2" (grep of tests/: none). Nothing loops over the key map or calls
  require_databento_key per account.
- Start/end checks: reports/stage_e26_briefs/checks.sh's "ledger total per account" block
  (`for a in sorted(ACCOUNTS): SpendGate(session_id="e26-checks-readonly", account=a)`) now
  prints a third line, "acct-3: spent 0.000000 cap 125.00 headroom 125.000000". It reads only the
  repo ledger (no external ledger for acct-3, no key), so it is an output change, not a failure.
  The end block will differ from the start block by exactly that line.
- No existing path reads acct-3's key unexpectedly: key_loader is called once with the selected
  account (pull_step2.py:1170, pull_hist.py:830); every other client builder
  (data/pull_mes.py:104, data/build_mes_bars.py:82 and :334, data/step2_store.py:528,
  data/build_bars_run.py:135, strategy/research/_d1e_quotes.py:979) calls
  require_databento_key() with no account, i.e. acct-2.

### A3. NOTE: acct-3 is selectable exactly as acct-1 and acct-2 are, and E.28 needs no config edit
- require_databento_key(account="acct-3") reads DATABENTO_API_KEY3 (environment, then .env;
  tested in both directions and for blank shadowing).
- SpendGate(session_id, ..., account="acct-3") takes cap 125.00 and no external ledger; every
  ledger line it writes carries "account": "acct-3" (data/spend_gate.py:323; tested for quote,
  commit, settle and refused).
- Quote tools: `data.pull_hist --quote-only --plan es2011 --account acct-3` runs end to end on a
  fake client (96 $0.00 lines on acct-3 under E.14's quote session, key loaded once with
  account="acct-3", fake key in no output). `data.pull_step2 --quote-only --account acct-3`
  parses; the other quote tools have no account option and cannot reach acct-3.
- An E.28 pilot script needs no edit to data/config.py:
  `SpendGate("e28-pilot-<date>", session_cap_usd=X, shared_cap_usd=Y <= 125.00, account="acct-3")`
  for a plain gate, or `data.pull_mes.RequestCappedGate(session_id, request_cap_usd=Z,
  session_cap_usd=X, account="acct-3")` (data/pull_mes.py:163-169; LockedQuoteGate in
  data/quote_universe.py:258-262 is the same constructor) for a per-request cap, plus
  require_databento_key(account="acct-3"). shared_cap_usd may tighten the account cap but a value
  above 125.00 raises (data/spend_gate.py:233-240, tested). PILOT_ONLY_ACCOUNTS is consulted only
  by data.pull_step2.require_buy_caps, so the gate itself does not refuse acct-3: correct for the
  pilot.
- Two traps E.28 must avoid, both pre-existing semantics: (i) SpendGate's default account is
  acct-1 and require_databento_key's default is acct-2, so both calls must name acct-3
  explicitly; (ii) session_spent_usd (data/spend_gate.py:279-281) sums every line of a session id
  whatever its account, and the quote-dedupe readers (pull_hist.py:450, pull_step2.py:661,
  quote_universe.py:423) are keyed by session only, so E.28 must use its own session id, never
  E.12's or E.14's.
- Not enforced by config or the gate, and therefore E.28's own job: the date bound ("never
  2024-03-01 or later"), the one-contract and one-schema rule, and the balance check at purchase.
  decide() is pure cap arithmetic (data/spend_gate.py:174-212). data.trade_date_guard exists for
  the date bound.

### A4. NOTE: ACCOUNT_3_CAP_USD = 125.00 against V43 and V44 (judgment for the lead, in V45)
data/config.py:96-102 sets 125.00 "the credit a new Databento account opens with (U5: acct-2
opened with $125.00), an upper bound only: the balance check at purchase time governs".
V44 (docs/DECISIONS.md:826-835) says "all of its funds go to the one contract and schema" and
names no dollar figure; V43 (docs/DECISIONS.md:806-807) recorded "a Databento pilot cap of USD
100 for order-book data (the user reports about USD 120 on the account)", written when the pilot
was to run on the existing account. 125.00 is consistent with V44 as an account cap: the registry
cap is an upper bound and the gate refuses above it. It is not where V43's USD 100 or V44's
"all of its funds" is enforced; that is the E.28 pilot gate's session cap, which the pilot script
must set (E.28 may not edit config). The lead should state in V45 which figure governs the
pilot's session cap (V44's "all funds" of acct-3, or V43's USD 100), so E.28 does not have to
infer it. The U5 figure is also an assumption about a new account's opening credit; the comment
already says the balance governs, which is right.

### A5. NOTE: the pilot-only guard is complete for every buy path in data/, and refuses before any key or vendor call
Verified against the code, not the report:
- data.pull_step2 --buy: main runs the preflight (:1161), then require_buy_caps (:1163), then
  key_loader (:1170); the guard's Step2Error is in the refusal tuple (:1171-1175, RC_REFUSED).
  run_buy (:939-975) repeats the preflight (:956) and require_buy_caps (:957) before any client
  attribute is touched (:962 onward). The guard checks `{account_id, gate.account_id} &
  PILOT_ONLY_ACCOUNTS`, so a gate on acct-3 is refused whether or not the account is named, and
  an explicit acct-3 with a gate elsewhere is refused too. The only callers of gate.commit in step
  2 are _buy (:846) via _acquire_sealed/_acquire_kept (:869, :911), which only run_buy calls
  (:961, :964). The error text names account ids only. New tests cover the CLI, run_buy with
  account None and acct-3, and the acct-1/acct-2 pass-through; the worker confirmed RED first.
- data.pull_step2 --plan --buy hands off to data.pull_hist.main (:1194-1209), where
  require_buy_ready (pull_hist.py:396-402) refuses any account but E14_BUY_ACCOUNT as its first
  check, before the registry, the key (:830) and the client (:836). Tested directly and through
  the hand-off.
- data/pull_universe.py (gate on ACTIVE_ACCOUNT only, no option), data/pull_mes.py and
  data/adapter.py (acct-1 default gates, default key), data/quote_universe.py (no account
  option), data/step2_store.py:528, data/build_mes_bars.py, data/build_bars_run.py,
  compute/remote.py (default key, no option): none can select acct-3.
- The guard does not block quotes on acct-3 ($0.00 lines), which matches "selectable the same
  way".

### A6. NOTE: stale and misleading text in data/pull_step2.py (optional; same rebuild rule as A1)
- :71 module docstring still says `--account acct-1|acct-2`.
- :1113 `--buy requires --account (acct-1, acct-2, acct-3)` now offers acct-3 as a buy account
  that :613-629 refuses one step later. Fix: `', '.join(a for a in ACCOUNTS if a not in
  PILOT_ONLY_ACCOUNTS)`. Harmless (the refusal follows), so NOTE; if the lead fixes A1 in
  pull_step2.py anyway, fold these two lines into the same edit so the harness is rebuilt once.

### A7. NOTE: tests are fake-key only, isolated, AAA; the two frozen-test edits are minimal and correct
- Keys: "db-FAKE-..." constants; the autouse fixture deletes DATABENTO_API_KEY1/2/3 and the
  legacy variable; every require_databento_key call passes an env_file under tmp_path; the CLI
  tests inject key_loader. The real .env is never opened.
- Ledgers: every writing gate uses tmp_path. Three tests use the default (real) paths read-only:
  test_the_pull_step2_plan_hand_off_on_acct3_is_refused_by_pull_hist (default buy_gate reads
  config.LEDGER_PATH through banner(); the real trial registry is untouched because
  require_buy_ready checks the account before the registry, pull_hist.py:399-401), and the two
  quote-tool parser tests. The module fixture real_files_untouched compares the real ledger and
  docs/ACCESS.md bytes before and after the module, which makes this the seventh real-ledger
  guard the memory rule applies to ("no ledger writes during pytest").
- tests/test_stage_e_config_keys.py:62-63 (map now includes acct-3) and :257-258 ("acct-3" ->
  "acct-9" as the unregistered example) are the minimal correct edits; the test bodies are
  unchanged. tests/test_e2b_pull_step2_e12.py:446-450, :457-459, :463 follow the lead's ruling
  (a); see A1 for the combined-headroom consequence. Both files cite "V45", which Task 3 writes
  in the same commit; the lead should make sure V45 indeed records acct-3 and the guard.
- AAA structure throughout; names say the behaviour; 36 items pass.

### A8. NOTE: harness and other freezes (pre-follow-up view; the v14 verification is section C)
- Harness v13 (reports/stage_e2b_harness_freeze.json before the rebuild) pinned exactly four of
  the five files: data/config.py f0e7381ec117, data/pull_step2.py 6a57461b03ce,
  tests/test_stage_e_config_keys.py b919ff500d5f, tests/test_e2b_pull_step2_e12.py 2a0bcd4b663b
  (all equal to HEAD before the patch, checked). tests/test_e26_account3.py matches none of
  TEST_PATTERNS (screening/harness_freeze.py:274-277: test_stage_e_*, test_e2b_*, test_e14_*,
  ...), so no manifest lists it. If the lead wants it frozen, the no-code option is to name it
  tests/test_stage_e_account3.py; adding "test_e26_*.py" to TEST_PATTERNS edits
  screening/harness_freeze.py, which is itself harness code.
- Non-harness freezes: none pins any of the five files. My scan of every reports/**/*.json for
  the five paths with a nearby sha: only the harness manifest (above) and
  reports/stage_d1f_harness_freeze.json (data/config.py a534698fb244, already stale at HEAD, so
  unchanged in status). reports/stage_e1_freeze.json and reports/stage_e12_ml_v2_freeze.json
  name data/config.py in note text only. reports/stage_e16_briefs/freeze_manifest.py leaves
  data/config.py out on purpose (:77-78). The E.18 C1b freeze, the cluster freezes
  (screening/stage_e_freeze.py) and reports/stage_e2b_briefs/check_frozen.py do not list them.
  So nothing else in the harness needed to change, and the end checks' E.16, E.18 and cluster
  verifications are unaffected.

## B. Findings on scripts/set_databento_key3.sh

I exercised a copy of the script in my scratch directory with fake keys only (never the repo's
.env). Verified behaviour: the key is read with `read -r -s` (:8, no echo, not in shell history);
`printf` is a bash builtin and the key is `unset` at :15, so no process ever gets it as an
argument (strace -f -e execve: 0 lines containing the fake key); nothing logs it; the new .env is
mode 600 (umask 077 at :7, mktemp, chmod at :17); duplicate `DATABENTO_API_KEY3=` lines are
removed (:13); an .env with CRLF lines or without a trailing newline is handled (GNU grep
re-terminates the last line); empty input exits 1 with .env unchanged; EOF on stdin exits 1 via
`set -e` with nothing created; a missing .env is created at 600. `.env` and `.env.*` are ignored
at .gitignore:2-3, identical at HEAD, so neither .env nor a stray temp file can enter a commit
with `git add -A`. The file contains no key. It is safe to commit after B1.

### B1. SHOULD FIX: no cleanup trap, so a failure between mktemp and mv leaves the key on disk
Evidence: :12 `tmp="$(mktemp .env.XXXXXX)"` ... :16 `mv "$tmp" .env`, with `set -euo pipefail`
(:5) and no `trap`. Reproduced on the scratch copy by making the temp file unwritable before :14:
the script exits 1 and `.env.mB0Rxg` (mode 600, holding `DATABENTO_API_KEY3=<key>`) stays in the
repo root. Same outcome for a signal or a full disk in that window. Git-ignored, so not
committable, but a second copy of the key the user does not know about, in the folder the data
move is reorganising.
Fix (validated on the scratch copy; the forced failure then leaves no temp file): add before :12
```
tmp=""
trap '[ -z "$tmp" ] || rm -f "$tmp"' EXIT
```
After a successful `mv` the path no longer exists and `rm -f` is a no-op. Bash runs the EXIT
trap on INT and TERM as well.

### B2. NOTE: dedupe misses `export` and indented forms; a pasted trailing CR is kept; mv into a directory
- :13 `grep -v '^DATABENTO_API_KEY3='` leaves `export DATABENTO_API_KEY3=old` and
  `  DATABENTO_API_KEY3=old2` in place (verified). Harmless for this repo: data/config.py's
  _read_env_file (:255-265) never matches the `export` form, and for the indented form the last
  line wins, which is the appended new key. Still, stale lines with an old key would remain.
  Fix: `grep -Ev '^[[:space:]]*(export[[:space:]]+)?DATABENTO_API_KEY3[[:space:]]*='`.
- A key pasted with a trailing CR is written as `...^M` (verified). config strips it on read
  (`.strip()`), so it works; `KEY=${KEY//$'\r'/}` after :8 removes it anyway.
- If `.env` were a directory, :16 would move the temp file into it and :18 would report success
  (verified; contrived). `mv -T "$tmp" .env` or an `[ -d .env ]` refusal closes it.
A full replacement with B1 and B2 applied, validated on the scratch copy for every case above:
```
#!/usr/bin/env bash
# Adds or replaces DATABENTO_API_KEY3 in .env from hidden input.
# The key is never echoed, printed, logged or passed on the command line.
# Run it yourself in a terminal on this laptop:  bash scripts/set_databento_key3.sh
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
tmp=""
trap '[ -z "$tmp" ] || rm -f "$tmp"' EXIT
read -r -s -p "Paste the new Databento API key (hidden), then press Enter: " KEY
echo
KEY=${KEY//$'\r'/}
if [ -z "${KEY}" ]; then echo "Nothing entered; .env unchanged."; exit 1; fi
if [ -d .env ]; then echo ".env is a directory; refusing."; exit 1; fi
touch .env
tmp="$(mktemp .env.XXXXXX)"
grep -Ev '^[[:space:]]*(export[[:space:]]+)?DATABENTO_API_KEY3[[:space:]]*=' .env > "$tmp" || true
printf 'DATABENTO_API_KEY3=%s\n' "$KEY" >> "$tmp"
unset KEY
mv -T "$tmp" .env
chmod 600 .env
echo "DATABENTO_API_KEY3 set in .env (value not shown)."
```

## C. Lead's follow-up: the v14 manifest, verified independently

The lead applied task2_config.patch to the main repo (05:19 PDT, uncommitted) and rebuilt
reports/stage_e2b_harness_freeze.json; v13 is kept at
reports/stage_e26_briefs/harness_v13_manifest.json. My own comparison (python, both JSONs read
whole, every changed entry rehashed from the main-repo bytes and the worktree bytes):

- sha256 of the files: v14 6dc0eda905b63147..., v13 dd2bcc6025144e0d... (the harness sha is the
  manifest file's bytes, screening/harness_freeze.py:63-70). Both match the lead's figures.
- Top-level keys identical (categories, created_pdt, entry_modules, files, harness_dirs,
  head_at_creation, notes, stage, what). Values differ only in created_pdt
  (2026-10-16T02:08:12-07:00 -> 2026-10-21T05:19:15-07:00) and head_at_creation
  (5a5674b4 -> 71d667f6). notes, stage, what, harness_dirs, entry_modules unchanged.
- files: 1065 in both; added none; removed none; changed exactly data/config.py,
  data/pull_step2.py, tests/test_e2b_pull_step2_e12.py, tests/test_stage_e_config_keys.py. The
  category of every entry is unchanged.
- Each changed entry's sha256 and byte count equal the main-repo file and the worktree file:
  data/config.py 74f509314ced / 17515 (v13 f0e7381ec117), data/pull_step2.py 91f50a84aee0 /
  67729 (v13 6a57461b03ce), tests/test_e2b_pull_step2_e12.py 6292c9d680b7 / 27394 (v13
  2a0bcd4b663b), tests/test_stage_e_config_keys.py e8d9af3c50de / 11651 (v13 b919ff500d5f).
- All 1065 v14 entries match the main tree as it stands (0 mismatches), so hf.check(REPO_ROOT)
  and tests/test_harness_freeze.py's real-tree test pass again under v14.

Acceptable as the minimal consequence of Task 2: yes. The only content change is the four
hashes the patch forces; nothing is added, removed or recategorised, and tests/test_e26_account3.py
is (as expected from TEST_PATTERNS) not pulled in. Two caveats:
1. head_at_creation records 71d667f, the parent of the commit that will carry these files, because
   the build ran on an uncommitted tree. v13 was built the same way (reports/stage_e22_STATE.md:
   manifest 02:08, commit e40ca85 02:10), so this follows precedent; say so in the progress entry.
2. If the lead applies A1 (either option) or A6, data/pull_step2.py changes again and v14 must be
   rebuilt before the commit, giving a different sha. Decide A1/A6 first, then rebuild once, then
   commit the manifest with the code.

What a v14 breaks that v13 passed (the main tree, worktrees and .venv excluded):
- Code pins of dd2bcc60: trigger_hold/events.py:69 `HARNESS_SHA256` (used at :263), imported by
  trigger_hold/events_h6.py:104 and used at :108, and trigger_hold/events_validate.py:64
  (`EV.HARNESS_SHA256`). Each refuses at run time with HarnessFreezeError until bumped to
  6dc0eda9.... trigger_hold/ is outside HARNESS_DIRS (screening/harness_freeze.py:32) and absent
  from the manifest, so bumping the pin does not change the harness sha. The six tests that
  import trigger_hold (tests/test_trigger_hold_*.py, tests/test_mdio_*.py) do not call preflight
  or read the pin, so no test fails either way.
- reports/stage_e26_briefs/before_after.sh:11 `H=dd2bcc60...`: the E.26 end checks must be run
  with the v14 sha, or the harness line will report a mismatch.
- Every `--harness-sha256` caller needs the new sha on its command line from now on (the
  worker's list in task2_report.md section 5 is correct: pull_step2, pull_hist, step2_store,
  hist_store, stage_e_runner, stage_e_start_dates, stage_e_verdict, trial_registry, ml_route
  train/test, ml_route_v2 phase1 cli, compute agent/remote, c1_replication c1b/evaluate).
- Historical scripts under reports/stage_e22_briefs/verify_k3, verify_k8, stage_e23_briefs/verify
  and ret, stage_e24_briefs/loader pin or print v13 as a record of their own runs; leave them.
- Already failing before v14 and unchanged: pattern_search/constants.py:87 and
  h6_rod/constants.py:95 pin v12 (tests/test_h6_rod_run.py fails since v13; the pattern_search
  tests use fake hooks and pass).
- Tests: no test in tests/ contains the v13 literal; the only test that failed because of the
  patch (the real-tree manifest test) passes under v14. The full suite was not run.

Commit hygiene for the Task 3 commit: include the five patched files, reports/stage_e2b_harness_freeze.json
(v14), reports/stage_e26_briefs/harness_v13_manifest.json, scripts/set_databento_key3.sh (after
B1) and the trigger_hold pin bump if the lead chooses it; never .env or any `.env.*`.

## Verdicts

VERDICT: APPROVE AFTER FIXES — A1 (one line in data/pull_step2.py: the docstring at :727-728 made
true, option (a), or the pilot-only exclusion, option (b)); then rebuild v14 once and commit the
manifest with the code. A2-A8 are notes for the lead and E.28; none blocks.

VERDICT (scripts/set_databento_key3.sh): APPROVE AFTER FIXES — B1 (the EXIT trap). B2 is
optional; the full replacement in B2 carries both. The file holds no key and is safe to commit.

## D. Final confirmation (lead's request, 05:30-05:38 PDT; main repo read-only, nothing committed)

(1) The three fixes match the proposals and change no behaviour beyond message text.
- `diff` of data/pull_step2.py, worktree (reviewed patch) against the main tree: exactly three
  hunks. :71 module docstring gains "(acct-3 is pilot-only and refused, Stage E.26)" (A6).
  :727-730 accounts_summary docstring is A1 option (a), with "Stage E.26, V45" added (text only).
  :1115-1116 `buyable = ", ".join(a for a in ACCOUNTS if a not in PILOT_ONLY_ACCOUNTS)` feeds the
  `--buy requires --account (...)` message (A6): a string change inside a branch that already
  raises; no control flow, no gate, no key path touched. data/config.py, tests/test_e26_account3.py,
  tests/test_stage_e_config_keys.py and tests/test_e2b_pull_step2_e12.py are byte-identical to
  the reviewed worktree files (cmp).
- scripts/set_databento_key3.sh is byte-identical (diff) to the B2 replacement I validated on the
  scratch copy (trap, CR strip, directory refusal, wider dedupe, `mv -T`); `bash -n` passes;
  22 lines, 885 bytes, no key material.
- Lint, not behaviour: data/pull_step2.py:71 is now 143 characters, a new E501 (ruff, limit 100).
  HEAD's pull_step2.py had none; config.py's 7 E501 are the pre-existing ones (same count at
  HEAD). Wrapping the line changes data/pull_step2.py's hash and so needs one more v14 rebuild;
  accepting it costs nothing. Lead's choice; it does not block.

(2) The rebuilt v14, verified independently.
- sha256 of reports/stage_e2b_harness_freeze.json: 81121be85ddb7872c3090d9c8c3ce7452204a0307c0c365289e7f7005d6855c2,
  as stated. Top-level differences from v13 (reports/stage_e26_briefs/harness_v13_manifest.json):
  created_pdt (-> 2026-10-21T05:27:35-07:00) and head_at_creation (-> 71d667f6) only; notes,
  stage, what, harness_dirs, entry_modules unchanged.
- files: 1065 in both; added none; removed none; changed exactly data/config.py,
  data/pull_step2.py, tests/test_e2b_pull_step2_e12.py, tests/test_stage_e_config_keys.py;
  categories unchanged.
- Each changed entry's sha256 and byte count equal the main-tree file: data/config.py
  74f509314ced / 17515; data/pull_step2.py 39760ba47346 / 68017 (the A1+A6 text);
  tests/test_e2b_pull_step2_e12.py 6292c9d680b7 / 27394; tests/test_stage_e_config_keys.py
  e8d9af3c50de / 11651. All 1065 entries match the main tree (0 mismatches), and
  `screening.harness_freeze.check(REPO_ROOT)` returns no problems with digest 81121be8....
- Still true from section C: trigger_hold/events.py:69 (used at :263, events_h6.py:108,
  events_validate.py:64) stays pinned to v13 and will refuse to run until the user bumps it (the
  lead's reason, an E.23 freeze member, is sound); reports/stage_e26_briefs/before_after.sh:11
  must be run with 81121be8....

(3) V45 item 2 (docs/DECISIONS.md, last entry, from line 843; the item at its lines 29-53) is
accurate against the code and this review: ACCOUNT_3_ID, DATABENTO_API_KEY3, cap USD 125.00 from
U5 as an upper bound, no external ledger; selectable through require_databento_key, SpendGate and
its ledger lines and the quote tool; acct-1, acct-2, their caps and ACTIVE_ACCOUNT unchanged;
pilot-only scope and span; PILOT_ONLY_ACCOUNTS refusing a step-2 buy before any key is read
(pull_step2.py:1163 precedes :1170) and pull_hist already refusing (pull_hist.py:396-402); the
pilot script passing account="acct-3" to both calls with its own session id and caps; the spend
bound as V44's "all of its funds" (balance less a few dollars of margin, under the USD 125.00 cap)
superseding V43's USD 100 for this account; key by variable name only; harness v14 with the sha
above, "differs from v13 only in those four entries" (true of the file entries; the two
timestamp/HEAD fields differ as on every rebuild). One precision point, optional: the item says
"every Stage E entry point takes the v14 sha from now on" but does not record that
trigger_hold/events.py keeps its v13 pin (E.23 freeze member, left for the user), so trigger_hold
runs refuse until it is bumped; one clause would close that gap.

FINAL: APPROVE (remaining, non-blocking: the E501 at data/pull_step2.py:71, and the optional
trigger_hold clause in V45).
