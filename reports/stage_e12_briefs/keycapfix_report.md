# KeyCapFix-OpusXHigh: harness v8 code changes (Stage E.12 Task 4)

Worker: worker-xhigh, opus. Worktree /home/kiros-li/Documents/GitHub/PropExperiment-e12-v8
(branch e12-v8, base 8b93e98). No commit, no manifest written, no Databento call, no key read or
printed, no network. The only file written in the main tree is this report. Times PDT, 2026-10-03.

## 1. The cap arithmetic (recomputed)

- Ledger: ledger/databento_spend.jsonl in the worktree = HEAD = the main tree's file at 08:5x PDT:
  17,400 lines, sha256 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957.
- `data.spend_gate.account_committed_usd(read_entries(LEDGER_PATH), "acct-2")` =
  **124.673761487003** (124.673761 to 6 dp, matches the brief). (acct-1, this repo's lines only:
  9.474373534322; its external ledger is not included in that figure.)
- 124.673761 + 125.00 (V19 top-up) = 249.673761, rounded down to the cent: **249.67**.

## 2. Changes, by file

### data/config.py (harness_code)
- :78-85 `ACCOUNT_2_CAP_USD = 249.67` with the arithmetic, the ledger line count and sha256 in a
  comment (was 125.00). ACCOUNTS["acct-2"] picks it up.
- :136-151 the Stage E.12 block after the E.5 block: `STAGE_E12_SESSION_ID =
  "stage-E.12-2026-10-03"`, `E12_SESSION_CAP_USD = 0.00` (comment: the lead sets it from the fresh
  quote, the selected subset's total x 1.03, never above the two accounts' combined headroom,
  before the v8 manifest), `E12_REQUEST_CAP_USD = 3.00` (D13), `STEP2_TRAINING_WINDOW_ONLY = True`.
- :153-159 `STEP2_PURCHASE_SESSION_ID`, `STEP2_SESSION_CAP_USD`, `STEP2_REQUEST_CAP_USD` repointed
  to the E.12 block. Earlier blocks (A.1, D.1f, E.0, E.1, E.2b, E.5) unchanged.
- :213 C-10(b): `require_databento_key` returns `key.strip()` (docstring updated).

### docs/ACCESS.md (not in the manifest)
- :9 only. C-10(a): the credential line now names `DATABENTO_API_KEY1` (acct-1) and
  `DATABENTO_API_KEY2` (acct-2). The MLCryptoEngine key-match sentence now says acct-1, since the
  old DATABENTO_API_KEY was acct-1's key.

### data/pull_step2.py (harness_code). Every existing guard is kept.
- :70-89 docstring: an E.12 section; :6-11 usage lines; the buy-flow paragraph names --account.
- :207-216 `ML_V2_PRICE_PATHS`, a 28-root literal, with an import-time check that it equals
  ML_ROUTE_ROOTS minus RB, HO, SI. No ml_route_v2 import. `ML_V2_CONTRACTS` gives set "ml-v2".
- :218-224 `TRAINING_WINDOW_END = "2024-03-01"`, `LAST_TRAINING_CHUNK`, import-time checks.
  :229-236 `EXTENSION_2010_CHUNKS` (112 months, 2010-01-01..2019-05-01 exclusive, checked) and
  `EXTENSION_2010_SKIPPED = {"MBT": ...}`.
- :262-266 `QUOTES_OUT_DEFAULT = reports/stage_e12_quotes.json`, `SET_ML_V2`, `QUOTE_SETS`.
- :297-308 new errors: `Step2AfterTrainingWindow(Step2ChunkError)` (names `range=<start>_<end>`),
  `Step2QuoteOnlyChunk(Step2ChunkError)`, `Step2TrainingWindowRequired(Step2Error)`.
- :353 `training_window_chunks`. :374 `plan_step2(roots, *, training_window=False)`.
  :390 `check_chunk(chunk, *, training_window=False)` refuses any non-`Chunk` first and, under
  the option, any chunk starting on or after 2024-03-01. :419 `validate_plan` passes the flag on.
- :426 `QuoteOnlyChunk` (a separate type, not a Chunk subclass). :447
  `check_quote_only_chunk` (root, request shape, the kind's own chunk set, OC-R, MBT).
  :472 `plan_quote_only(roots, kind)` returns (plan, skipped). :494 `check_for_quote`.
- :503 `parse_roots` (distinct, non-empty items, each in ML_V2_PRICE_PATHS, then check_root).
  :518 `groups_by_cluster`.
- :599 `require_account`, :606 `require_buy_caps(gate, account=None)` (any registered account
  passed explicitly; None keeps ACTIVE_ACCOUNT). :617 `require_training_window` (the interlock).
- :653 `run_quote_only(..., training_window=False)` checks each item with check_for_quote, then
  `install_forbidden_guards`, then `gate.quote` only (as before).
- :697 `account_position` (see open item 1), :712 `accounts_summary` (both accounts, combined
  headroom), :729 `_usd_bucket` (adds `usd_extension_2010_01_2019_04` for extension quotes).
- :933 `run_buy(..., account=None, training_window=False)`: preflight, then
  `require_buy_caps(gate, account)`, then the interlock, then `validate_plan`, and `check_chunk`
  again per chunk, all with the flag.
- CLI: :987 `_parser` (--account with choices = ACCOUNTS; --roots in the --ml-route/--cluster
  group; --training-window, --holdout2-only and --extension-2010 mutually exclusive;
  --quotes-out). :1016 `quote_groups` (ml-v2). :1026 `quote_paths` (.json only, .md beside it,
  E.2b's json and md refused). :1065 `_quote_roots` (exactly one of --set/--roots; section
  name = set or `roots:<list>`, plus `+<window>`). :1086 `_check_buy_args`. Before any gate or
  vendor call it refuses: missing sha256, --set, the quote-only plans, --quotes-out, missing
  --account, and the interlock. :1102 `_gate_on` refuses a gate on the wrong account. :1108
  `main`: `gate_factory(account=...)`, `key_loader(account=...)`. Quote-only builds every
  account's gate and logs and records their positions before any vendor call. :1175
  `render_quotes_markdown`. :1199 `_quote_main` writes `accounts`, a per-section `plan` and
  `skipped_roots`.

### Tests
- New, frozen by TEST_PATTERNS (checked with `manifest_categories`: both `stage_e_test`):
  - tests/test_stage_e_config_v8.py (10 tests). The cap arithmetic (124.673761 + 125.00 ->
    249.67, never above the funds). acct-2's spend recomputed from the ledger's first 17,400
    lines, sha256-pinned, so later appends do not break it. Stripped key from env and from .env,
    with capsys showing no value. The E.12 block, the repointing, and its position in the
    file. Earlier blocks unchanged. ACCESS.md's credential line.
  - tests/test_e2b_pull_step2_e12.py (54 tests). The 28 price paths, cross-checked against
    `ml_route_v2.constants.UNIVERSE` in the test only. --roots validation (9 bad inputs; main
    refuses before any call). Training-window plans: ZN 58 chunks ending 2024-02, MBT 35 from
    2021-04, each of the 13 chunks from 2024-03 refused by name. run_buy and run_quote_only
    refuse a 2024-03 chunk with no vendor call. Interlock on: main and run_buy refuse without the
    option, with no gate, preflight, key or client. --account: required for --buy, an unknown
    one is refused by the parser, require_buy_caps accepts acct-1 when named, a factory
    returning the wrong account is refused. An end-to-end acct-1 buy with fakes checks the gate
    on acct-1, the key loader called with account="acct-1", ledger lines on acct-1 under E.12,
    the banner naming acct-1, and no key in any output. main hands run_buy the account and the
    window plan. Holdout-2-only and extension plans: never accepted by check_chunk, validate_plan,
    run_buy or main --buy. Their quotes go through gate.quote only, under the forbidden guards.
    Both accounts' positions and the combined headroom are reported. MBT is skipped and an
    unpriceable root fails its quotes. Set ml-v2 with the training window. --quotes-out: the
    default, the .md beside it, E.2b's files refused (mtimes unchanged), .json only, --buy
    refused.
- Updated to read the constants; no check is weakened:
  - tests/test_e2b_pull_step2.py (frozen). :94 an autouse fixture holds
    `ps.STEP2_TRAINING_WINDOW_ONLY` False for these full-71-chunk tests (sealing and resume
    paths stay in the code for later phases). The interlock is tested at the config's value in
    the new file. :102 `gates_for` is main's two-account gate factory, with acct-1's external
    ledger a tmp file. main() calls take `**kw` / account= and `--account acct-2`. :291 the
    headroom reads ACCOUNT_2_CAP_USD. :493 "one cent under the cap" reads the constant (it pinned
    124.99 of 125.00). :551 the fixture's patch is re-applied after a mid-test
    `monkeypatch.undo()`. :675-760 the active-policy tests: ACTIVE_SESSION =
    config.STEP2_PURCHASE_SESSION_ID == STAGE_E12_SESSION_ID, the E.12 caps are active, and the
    E.5 block is pinned as kept (stage-E.5-2026-09-27, 21.52, 3.00).
  - tests/test_spend_gate_accounts.py (not frozen) :78, :144-152, :179: 125.00 replaced by
    config.ACCOUNT_2_CAP_USD.
  - tests/test_pull_universe.py (not frozen) :393, :441: "cap $125.00" and 125.00 replaced by the
    constant.

## 3. `git -C /home/kiros-li/Documents/GitHub/PropExperiment-e12-v8 diff --stat`

```
 data/config.py                    |  40 ++-
 data/pull_step2.py                | 557 ++++++++++++++++++++++++++++++++------
 docs/ACCESS.md                    |   2 +-
 tests/test_e2b_pull_step2.py      | 106 +++++---
 tests/test_pull_universe.py       |   5 +-
 tests/test_spend_gate_accounts.py |  14 +-
 6 files changed, 586 insertions(+), 138 deletions(-)
```
Untracked (new): tests/test_e2b_pull_step2_e12.py (552 lines), tests/test_stage_e_config_v8.py
(170 lines). In the main tree all eight paths are clean at 8b93e98, so the changes apply as they
are. The main tree passed the v7 manifest check with 0 problems at 09:1x PDT, so v8 differs from
v7 only by these files plus the lead's E12_SESSION_CAP_USD edit.

## 4. Test summary lines (worktree, main tree's venv, nice 10)

- The brief's list: tests/test_e2b_pull_step2.py, test_spend_gate.py,
  test_spend_gate_accounts.py, test_stage_e_config_keys.py, test_harness_freeze.py and the two
  new files, with a fresh PYTHONPYCACHEPREFIX: `4 failed, 180 passed in 154.28s (0:02:34)`.
  - `test_the_real_tree_matches_the_committed_manifest_when_it_exists`: expected. The v7
    manifest does not match the changed data/config.py, data/pull_step2.py and
    tests/test_e2b_pull_step2.py, and it passes once the lead builds v8.
  - `test_an_unchecked_hash_pyc_...`, `test_a_timestamp_pyc_forged_...`,
    `test_honest_and_stale_bytecode_pass`: caused by PYTHONPYCACHEPREFIX (FileNotFoundError on
    the tmp tree's `screening` __pycache__). They fail the same way at HEAD: the baseline run
    with the prefix gave `3 failed, 224 passed`.
- tests/test_harness_freeze.py with PYTHONDONTWRITEBYTECODE=1 and no prefix:
  `1 failed, 16 passed in 1.30s` (only the manifest test; HEAD gave `17 passed`).
- tests/test_pull_universe.py: `57 passed in 6.00s`.
- Other tests that touch the changed symbols: test_quote_universe, test_cross_platform_static,
  test_e2b_step2_store, test_stage_e_loader, test_stage_e_runner, test_stage_e_start_dates,
  test_compute_datarules, test_ml_route_store, test_ml_route_review_fixes, test_d1f_holdout2 and
  test_ml_route_e2e, plus test_pull_universe: `1 failed, 390 passed, 1 warning in 119.05s`. The
  failure, `test_d1f_holdout2.py::TestRealStores::test_real_holdout2_is_not_yet_sealed_or_verifies`,
  comes from the environment: the worktree has no git-ignored sealed holdout files. The same test
  in the main tree: `1 passed in 1.96s`.
- The full suite was NOT run: another worker's ml_v2 pytest job was running, and CLAUDE.md
  allows one heavy job at a time. The lead's end check (`uv run pytest -q -p no:cacheprovider`)
  covers it.
- ruff on data/pull_step2.py and the new or changed tests: clean. data/config.py and the two
  unfrozen tests keep their earlier E501 lines, which exist at HEAD.

## 5. Manifest build and verify (lead, main tree, after applying the changes and setting
E12_SESSION_CAP_USD)

```
cd /home/kiros-li/Documents/GitHub/PropExperiment
PYTHONPYCACHEPREFIX=/tmp/claude-1000/<fresh> uv run python -m screening.harness_freeze build
PYTHONPYCACHEPREFIX=/tmp/claude-1000/<fresh> uv run python -m screening.harness_freeze verify --expected <sha256 printed by build>
PYTHONDONTWRITEBYTECODE=1 uv run pytest -q -p no:cacheprovider tests/test_harness_freeze.py tests/test_stage_e_config_v8.py tests/test_e2b_pull_step2_e12.py tests/test_e2b_pull_step2.py
git diff --stat reports/stage_e2b_harness_freeze.json   # the v7 -> v8 diff
```
Harness files changed (in the manifest): data/config.py, data/pull_step2.py,
tests/test_e2b_pull_step2.py; new: tests/test_e2b_pull_step2_e12.py,
tests/test_stage_e_config_v8.py. Changed but not in the manifest: docs/ACCESS.md,
tests/test_spend_gate_accounts.py, tests/test_pull_universe.py. No other harness file was
touched; data/pull_step2_report.py is unchanged, and its `_set_lines` is imported read-only.

## 6. Open items and judgment calls for the lead

1. Credit and top-up fields. `account_position` now sets `credit_left_usd` to the cap headroom
   for both accounts. Before, it was 125.00 - spent for acct-2, which would show $0.33 left and
   a top-up for nearly any quote after the raise. `account_credit_usd` stays U5's $125.00 for
   acct-2 and is the cap for acct-1. The top-up fields therefore count against cap headroom.
   The reasons: V19 says the cap was "raised to match" the funds, and V23 calls acct-1's
   headroom its funds. Overrule if wrong.
2. The interlock is enforced in both `main` and `run_buy`, as defense in depth. The legacy test
   file holds the flag off with an autouse fixture, documented.
3. Quote-only plans skip the trade-date guard, since no minute is downloaded. Each kind is checked
   against its own explicit chunk set instead.
4. A quote-only run now reads acct-1's external ledger
   (/mnt/large-storage/.../spend_ledger.jsonl) to report both positions. If the archive drive is
   not mounted, it refuses before any vendor call (fail closed).
5. Quotes-file layout: one section per set or roots list plus window, for example
   `ml-v2+training-window` or `roots:ZN,MBT+extension-2010`. The header fields `range` and
   `account` are the last run's values; use each section's `plan`. In the .md, the
   extension's money appears only in the total (the JSON has `usd_extension_2010_01_2019_04`),
   and `_set_lines` still labels top-ups "acct-2 ... ACCOUNT_2_CAP_USD" whichever account
   quoted.
6. MBT is the only root skipped by name for the 2010 extension, as the brief says. MCL and MHG are
   not price paths, but if quoted through another set they would fail their quotes.
   --holdout2-only and --extension-2010 are not limited to the price paths.
7. `--buy --ml-route/--cluster` still work. They now also need --account and, while the flag is
   on, --training-window.
8. `main()`'s injected `key_loader` and `gate_factory` are now called with `account=`, which
   changes the signature for any external caller that injects fakes. There are none outside
   tests.
9. E12_SESSION_CAP_USD = 0.00 until the lead sets it. data/pull_step2.py is now about 1,215
   lines (it was 836). I did not split it, because that would create a new harness file.
10. Not done (outside the brief): the holdout status check, which is the lead's start and end
    check (nothing here touched data/ or the holdout), and the full suite (see §4).
