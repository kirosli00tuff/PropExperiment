# Stage E.11: Databento key selected by account (data/config.py), harness manifest v7

Worker KeyFix-OpusXHigh, 2026-10-03, finished 01:35 PDT. Not committed: the lead makes the
commit.

## Result

- `data.config.require_databento_key(env_file=ENV_FILE, account=None)` now reads
  `DATABENTO_API_KEY1` for acct-1 and `DATABENTO_API_KEY2` for acct-2. When `account` is None it
  uses `ACTIVE_ACCOUNT`, read at call time. The old single `DATABENTO_API_KEY` is not read at
  all, not even as a fallback.
- Harness manifest v7 sha256:
  **`eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4`**
  (v6 was `9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87`).
- The v6 to v7 manifest diff holds exactly the two allowed file entries: data/config.py
  changed, tests/test_stage_e_config_keys.py added.
- `verify` against v7 prints `preflight OK`. `verify` against v6 now refuses, as expected.
- Targeted tests: `294 passed in 201.37s`, exit 0.

## What changed in data/config.py

Three parts of the file changed, and nothing else (caps, session ids, accounts, paths and
`_read_env_file` are byte-identical):

1. The module docstring sentence about the key now names both variables and the account rule.
2. `DATABENTO_KEY_ENV = "DATABENTO_API_KEY"` is replaced by a read-only mapping
   `DATABENTO_KEY_ENV_BY_ACCOUNT`, built from `ACCOUNT_1_ID` and `ACCOUNT_2_ID`. No Python file
   in the repo imported `DATABENTO_KEY_ENV`; only data/config.py used it. The two old E.5
   reports that mention it, reports/stage_e5_harness_review.md and
   reports/stage_e5_harness_change.md, are history and were not edited.
3. `require_databento_key` takes the new keyword-compatible `account` parameter:
   - An account id that is not in the mapping raises `MissingSecretError`, naming the account
     (repr) and the known accounts. This fails closed.
   - Otherwise the function reads the account's variable from the environment, and falls back to
     the `.env` file when the environment value is absent or blank.
   - If the value is still missing, empty or whitespace-only, it raises `MissingSecretError`,
     naming the variable and the account. No message ever contains a value.
   - A usable key is returned unstripped, exactly as before.

Choices made inside the brief, for the lead to check:

- **Unknown account raises `MissingSecretError`, not `data.spend_gate.UnknownAccountError`.**
  data.spend_gate imports data.config, so importing it back would be circular. Every existing
  caller already catches `MissingSecretError`: compute/remote.py turns it into `SendRefused`,
  and data/pull_step2.py, data/pull_universe.py and data/quote_universe.py list it in their
  refusal handlers. An unknown account is therefore refused cleanly everywhere, never as an
  uncaught crash.
- **A blank environment value does not shadow `.env`.** Before this change, an empty environment
  value already fell through to the file. Whitespace-only values now get the same treatment
  instead of being returned as a key. Blank in both places raises.

Unified diff (`git diff -- data/config.py`; variable names only, no key value anywhere):

```diff
diff --git a/data/config.py b/data/config.py
index ab05179..3cba71c 100644
--- a/data/config.py
+++ b/data/config.py
@@ -1,8 +1,10 @@
 """Paths, spend caps, and credential loading for the offline data lane.
 
-The Databento key is read from the environment or from this repo's ``.env``
-(``DATABENTO_API_KEY``), mirroring MLCryptoEngine's pattern of a
-git-ignored ``.env`` read through one config function. It is never
+Each Databento account has its own key, read from the environment or from this repo's
+``.env``: ``DATABENTO_API_KEY1`` for acct-1, ``DATABENTO_API_KEY2`` for acct-2, chosen by
+``ACTIVE_ACCOUNT`` unless the caller names the account (Stage E.11, V19; the old single
+``DATABENTO_API_KEY`` is no longer read). This mirrors MLCryptoEngine's pattern of a
+git-ignored ``.env`` read through one config function. A key is never
 hardcoded, logged, or written anywhere. This module holds NO TopstepX
 credential of any kind and must never grow one in Stage A.1.
 """
@@ -131,7 +133,14 @@ STEP2_PURCHASE_SESSION_ID = STAGE_E5_SESSION_ID
 STEP2_SESSION_CAP_USD = E5_SESSION_CAP_USD
 STEP2_REQUEST_CAP_USD = E5_REQUEST_CAP_USD
 
-DATABENTO_KEY_ENV = "DATABENTO_API_KEY"
+# One Databento key per account (Stage E.11, V19): .env holds DATABENTO_API_KEY1 and
+# DATABENTO_API_KEY2 only. require_databento_key reads the variable of the account it is asked
+# for (ACTIVE_ACCOUNT by default). The old single DATABENTO_API_KEY is not read, not even as a
+# fallback. Every account in ACCOUNTS has exactly one entry here.
+DATABENTO_KEY_ENV_BY_ACCOUNT: MappingProxyType[str, str] = MappingProxyType({
+    ACCOUNT_1_ID: "DATABENTO_API_KEY1",
+    ACCOUNT_2_ID: "DATABENTO_API_KEY2",
+})
 DATASET = "GLBX.MDP3"
 
 
@@ -152,11 +161,27 @@ def _read_env_file(path: Path) -> dict[str, str]:
     return out
 
 
-def require_databento_key(env_file: Path = ENV_FILE) -> str:
-    """The Databento key, or a clear failure naming the variable."""
-    key = os.environ.get(DATABENTO_KEY_ENV) or _read_env_file(env_file).get(DATABENTO_KEY_ENV)
-    if not key:
+def require_databento_key(env_file: Path = ENV_FILE, account: str | None = None) -> str:
+    """The Databento key of ``account`` (``ACTIVE_ACCOUNT`` when None), or a clear failure.
+
+    The account's variable is read from the environment, else from ``env_file``; a blank
+    environment value does not shadow the file. An account with no registered variable, and a
+    variable that is missing, empty or whitespace-only, raise MissingSecretError naming the
+    account and the variable, never a value.
+    """
+    account_id = ACTIVE_ACCOUNT if account is None else account
+    name = DATABENTO_KEY_ENV_BY_ACCOUNT.get(account_id)
+    if name is None:
+        raise MissingSecretError(
+            f"no Databento key variable is registered for account {account_id!r} "
+            f"(known accounts: {', '.join(DATABENTO_KEY_ENV_BY_ACCOUNT)})"
+        )
+    key = os.environ.get(name, "")
+    if not key.strip():
+        key = _read_env_file(env_file).get(name, "")
+    if not key.strip():
         raise MissingSecretError(
-            f"{DATABENTO_KEY_ENV} is not set in the environment or {env_file.name}"
+            f"{name} (the Databento key of account {account_id}) is not set, or is empty, "
+            f"in the environment or {env_file.name}"
         )
     return key
```

Callers were not edited. All nine call with zero arguments, so they still work:

- Zero-argument `key_loader` defaults: compute/remote.py:125, data/pull_step2.py:758,
  data/quote_universe.py:745, data/pull_universe.py:753.
- Direct zero-argument calls: data/step2_store.py:429, data/build_bars_run.py:135,
  data/build_mes_bars.py:82 and :334, data/pull_mes.py:104, and
  strategy/research/_d1e_quotes.py:979. data/pull_mes.py is not in the brief's caller list.

## Tests

New file tests/test_stage_e_config_keys.py: 34 test items, AAA layout.

- **Isolation.** An autouse fixture deletes `DATABENTO_API_KEY`, `DATABENTO_API_KEY1` and
  `DATABENTO_API_KEY2` from the environment before every test. Every call passes
  `env_file=tmp_path/".env"`, except the two zero-argument tests. One of those only inspects the
  signature. The other patches `config._read_env_file` to fail the test if it is ever called, so
  the repo's `.env` cannot be opened.
- **Values.** All values are obvious fakes, such as `fake-key-1-not-real`. Nothing is printed;
  one test asserts empty stdout and stderr through capsys.

```
test_each_account_maps_to_its_numbered_variable
test_every_registered_account_has_a_key_variable
test_the_mapping_is_read_only
test_acct_1_reads_key1_from_the_environment
test_acct_2_reads_key2_from_the_environment
test_acct_1_and_acct_2_read_their_own_lines_of_the_env_file
test_default_account_is_the_active_account
test_default_follows_active_account_when_it_is_repointed
test_environment_variable_wins_over_the_env_file
test_env_file_is_read_when_the_variable_is_absent_from_the_environment
test_blank_environment_variable_does_not_shadow_the_env_file[ "" | "   " | "\t" ]
test_env_file_is_not_opened_when_the_environment_holds_the_key
test_missing_variable_raises_naming_the_variable_and_the_account
test_missing_env_file_and_environment_raises
test_empty_or_whitespace_only_value_in_the_env_file_raises[ 5 variants ]
test_empty_or_whitespace_only_environment_value_raises_without_a_file_fallback[ 3 variants ]
test_unknown_account_raises_naming_the_account[ acct-3 | "" | ACCT-1 | acct_1 ]
test_legacy_single_variable_alone_is_not_accepted
test_one_accounts_key_never_stands_in_for_the_other
test_refusal_messages_never_contain_a_key_value_and_nothing_is_printed
test_signature_still_binds_with_no_arguments_for_key_loader_callers
test_zero_argument_call_returns_the_active_accounts_environment_key
test_missing_secret_error_is_still_a_runtime_error
```

TDD record:

- **RED.** Before the edit, collection failed with `ImportError: cannot import name
  'DATABENTO_KEY_ENV_BY_ACCOUNT'`.
- **GREEN.** After the edit: `34 passed in 0.09s`.
- **Lint.** `ruff check` on the new test file is clean. data/config.py still has its 3
  pre-existing E501 errors, at current lines 100, 120 and 123, in the E.1 and E.5 cap comments.
  They are identical in the saved original and were left alone, because those lines must stay
  byte-identical.

Targeted run (the brief's command):

```
uv run pytest -q tests/test_stage_e_config_keys.py tests/test_spend_gate_accounts.py
  tests/test_quote_universe.py tests/test_compute_units.py tests/test_harness_freeze.py
  tests/test_e2b_pull_step2.py tests/test_d1f_holdout2.py
-> 294 passed in 201.37s (0:03:21), exit 0
```

The log is reports/stage_e11_briefs/keyfix_pytest.out. The full suite was not run (the lead
runs it).

An earlier run, made before v7 existed and with `PYTHONPYCACHEPREFIX` set, gave
`4 failed, 290 passed` (log: reports/stage_e11_briefs/keyfix_pytest_run1_pycacheprefix.out).
None of the four is a code fault:

- `test_the_real_tree_matches_the_committed_manifest_when_it_exists` failed because the
  manifest was still v6 while data/config.py had changed. This failure was expected, and the
  test passes once v7 exists.
- The three bytecode tests (`test_an_unchecked_hash_pyc_beside_an_unchanged_source_is_refused`,
  `test_a_timestamp_pyc_forged_to_match_its_source_is_refused`,
  `test_honest_and_stale_bytecode_pass`) failed with `FileNotFoundError`. They compile into temp
  folders and expect `__pycache__` beside the source, which the prefix moves elsewhere. Rerun
  without the prefix, all three pass (`3 passed`). **Run test_harness_freeze.py without
  `PYTHONPYCACHEPREFIX`.**

## Manifest v6 to v7

Built with `PYTHONPYCACHEPREFIX=<scratch>/pyc_build uv run python -m screening.harness_freeze
build`:

```
wrote reports/stage_e2b_harness_freeze.json: 1038 files {'harness_code': 136, 'frozen_input': 808,
  'earlier_freeze': 38, 'import_closure': 11, 'stage_e_test': 45}
sha256 eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4
```

Diff of v6 (the copy saved before any edit) against v7, every key under "files" and
"categories", plus the top-level fields:

```
top-level keys equal: True
TOP created_pdt: '2026-09-27T18:10:54-07:00' -> '2026-10-03T01:30:24-07:00'
TOP head_at_creation: '2c0bfe0f23f2bd3c656d782df126b0d688d88ed5' -> '5c28a92e572d081cca70a2fb897a3bff9e7e8acb'
files: v6 1037 v7 1038 | added 1 removed 0 changed 1
  ADDED   tests/test_stage_e_config_keys.py: {'sha256': 'b919ff500d5fc0929f2152fe0383a1ecfe89650ca2c61c0f19f574275ee5eb93', 'bytes': 11441}
  CHANGED data/config.py: {'sha256': 'bba0c1f00189bfa1cdaae3ee0312a9430327f3ddd67fd9629270de98b9830e9d', 'bytes': 7791} -> {'sha256': 'b1a7c7b120b32dfc46ffd2ef30619568a4cf73b0aeb083bb32d9da91b9b50592', 'bytes': 9273}
categories: v6 1037 v7 1038 | added 1 removed 0 changed 0
  ADDED   tests/test_stage_e_config_keys.py: stage_e_test
```

The other top-level fields (stage, what, harness_dirs, entry_modules, notes) are unchanged. No
other file differs. At build time three untracked files belonged to other workers:
`ml_route_v2/__init__.py`, `ml_route_v2/constants.py` and `reports/stage_e11_interfaces.md`.
None of them is in the manifest: `ml_route_v2` is not in HARNESS_DIRS, and the report matches no
pattern. The baseline check before any edit gave `preflight OK: 9a8ebe73...` against v6.

## Verify outputs

```
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify \
    --expected eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4
preflight OK: eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4      (exit 0)

$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify \
    --expected 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
Stage E harness preflight refused: reports/stage_e2b_harness_freeze.json sha256 eee8a8b92a02...
  is not the expected 9a8ebe7364be...                                               (exit 1)
```

v7 still printed `preflight OK` when verified again after the second targeted run, with no
prefix, so the normal `__pycache__` files that pytest writes do not disturb it.

## For the lead (observed, not acted on)

1. **compute/remote.py's outbound key scan now covers only the active account's key.**
   `RemoteRunner._key()` uses `key_loader=require_databento_key`, so it scans uploads for the
   ACTIVE_ACCOUNT key (acct-2, `DATABENTO_API_KEY2`) and not for `DATABENTO_API_KEY1`. Before
   this change, V19 had already removed `DATABENTO_API_KEY` from .env, so `_key()` refused every
   send. Whether the scan should cover both keys is your decision; the brief forbids editing
   callers.
2. **Later files can change or break the freeze.**
   - A new `*.py` under a harness directory (rules, sim, screening, funnel, data, ml_route,
     compute, strategy/stage_e) makes v7's verify fail as "not listed".
   - A new tests/ file matching `test_stage_e_*.py` or `test_ml_route_*.py` does not fail
     verify, but it would enter the next build. That pattern includes any
     `test_ml_route_v2_*.py` an ml_route_v2 worker might write.
3. **ACCOUNT_2_CAP_USD is unchanged at 125.00**, as the brief says. V19 says the next purchasing
   session raises it (about $249.67); that edit would need another manifest rebuild.

## Secret hygiene

- I never opened, read, cat'ed or grepped `.env`, and never printed or echoed any environment
  variable's value.
- No Databento call, quote, purchase or network access was made.
- A scan of every output this worker produced for the Databento key shape
  (`grep -cE 'db-[A-Za-z0-9]{8,}'`) returns 0 for each file:
  - data/config.py
  - tests/test_stage_e_config_keys.py
  - both pytest logs
  - the config diff
  - the manifest diff
  - both verify outputs
- The tests use only fake values and never read the repo's `.env`.
