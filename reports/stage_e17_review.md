# Stage E.17 reviews

## v11 review (HarnessReviewer-FableXHigh)

Reviewer: HarnessReviewer-FableXHigh (worker-xhigh, fable), brief reports/stage_e17_briefs/brief_v11_review.md.
Review window: 19:10:53 to 19:24 PDT, 2026-10-09 (`date`). Working tree of
/home/kiros-li/Documents/GitHub/PropExperiment against HEAD 8e5707c7917dc6f861accfbc8aa81fda85994119 (`git rev-parse HEAD`).
Every command ran read-only with `uv run --no-sync` (so the lead's background full suite was never disturbed by an
environment sync), at nice 10, with PYTHONPYCACHEPREFIX under the session scratchpad
(`.../scratchpad/review/pyc`). No vendor call, no .env or key read, no ledger write. `git status --porcelain` before
and after the review lists the same six modified tracked files and no new tracked change; the only file this review
wrote is this one. Review scripts: `.../scratchpad/review/{recompute_quote,compare_manifest,ast_diff}.py`.

**Verdict: APPROVE.** No BLOCKING or SHOULD FIX finding. Four NOTEs, three of which ask the lead to record something
in the v11 commit message, the STATE file or the C1 return (no change to v11 itself).

### Binding rules read

- C1 freeze reports/stage_e14_prereg_C1.md section 9 step 6 and section 11 last paragraph item (2): v11 "differs from
  v10 only in data/config.py (ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and the comments beside them) and in the
  test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300;
  tests/test_stage_e_config_v8.py:62-64), nothing else" (sed -n '136,141p' and '155,201p').
- reports/stage_e16_handoff.md section 1 steps 5-6 (sed -n '21,34p'): the guard (fresh total = the run's own new
  ledger lines, one successful quote per chunk of 642, tool JSON never trusted); ACCOUNT_2_CAP_USD = spent (231.599730
  unless the ledger moved) + fresh total x 1.03 rounded up to the cent; E14_EXT2010_SESSION_CAP_USD = fresh total x
  1.03 rounded down to the cent, never above $60.00 (V27).
- docs/prompts/STAGE_E.17.md A1 (lines 51-54, $97.00) as amended by docs/DECISIONS.md V30 amendment (lines 556-561):
  total billed spend at most $124.00; "Every cap the hand-off computes is also bounded by this."
- docs/DECISIONS.md V27 (line 498 ff.): "harness v11 raises ACCOUNT_2_CAP_USD from $249.67 to $291.08 (the minimum
  E.14's quote needs) ... the fresh ext2010 quote x 1.03 on acct-2, never above $60.00".
- reports/E.15_RETURN.md section 6 item 14 (lines 49-59): the freeze's "test_stage_e_config_v8.py:62-64" is off by
  two; the pinning assertions are lines 64 and 65.

### Check 1: changed files and the harness scan. PASS

- `git diff HEAD --numstat`:
  `8 2 data/config.py`, `642 0 ledger/databento_spend.jsonl`, `10 10 reports/stage_e2b_harness_freeze.json`,
  `3 3 tests/test_e14_config_v10.py`, `2 2 tests/test_e14_pull_hist.py`, `2 2 tests/test_stage_e_config_v8.py`.
  The ledger change is purely additive (642 added, 0 deleted) and is the quote run's (check 3); it is not part of
  the harness manifest and the brief says it is committed later with C1's result.
- `git status --porcelain --untracked-files=all | grep -E '^\?\? (rules|sim|screening|funnel|data|ml_route|compute|strategy|tests)/'`
  printed nothing: no untracked file, .py or otherwise, under any HARNESS_DIRS entry (screening/harness_freeze.py:32-33)
  or under tests/. The untracked .py files in the tree are reports/stage_e17_briefs/{a3_select,fresh_quote_guard,
  verify_freeze,write_hash_files}.py, outside the scan. The passing verify in check 5 is the same fact by the module's
  own `unlisted_python_files` scan.

### Check 2: data/config.py changes only the two assignments. PASS

- AST diff against HEAD (ast_diff.py, comments and whitespace ignored): `data/config.py: 4 AST dump lines differ`,
  exactly `Constant(value=249.67) -> Constant(value=291.08)` and `Constant(value=0.0) -> Constant(value=59.47)`;
  statements new to the file: `L89: ACCOUNT_2_CAP_USD = 291.08`, `L195: E14_EXT2010_SESSION_CAP_USD = 59.47`;
  function set unchanged. So the other 6 added lines are comments, and `git diff` shows them directly above the two
  assignments (lines 85-88 and 193-194).
- The comments' facts checked against the sources: "29,040 lines before E.17's quote" (quote_ext2010.log line 3:
  `29040`); "18:54-19:07 PDT" (log: `Fri Oct 9 18:54:57 PDT` start, `19:06:57 PDT` end); "$57.742330 x 1.03 =
  $59.474600", "231.599730", "291.074330, rounded UP" (check 3); "$124.00 budget (V30 as amended)" (DECISIONS.md:558).

### Check 3: the values. PASS

Recomputed by recompute_quote.py from ledger lines 29041-29682 only (strictly after the pre-run count in
quote_ext2010.log line 3; run start 2026-10-10T01:54:50+00:00 from line 4), matched by `data.pull_hist.request_key`
against `plan_chunks(get_plan("ext2010"))`:

```
plan ext2010: 642 chunks, roots ['NG', 'NQ', 'ZN', '6E', 'GC', 'ZC'], 642 distinct keys
ledger lines now 29682; new lines after 29040: 642; pre-cut lines with ts >= run start: 0
problems: 0; duplicate chunks: 0; missing chunks: 0
  NG: 107 chunks, $8.570392   NQ: 107 chunks, $10.625886   ZN: 107 chunks, $10.106134
  6E: 107 chunks, $11.072096  GC: 107 chunks, $11.182294   ZC: 107 chunks, $6.185528
TOTAL (sum of 642 successful quote lines) = $57.742329910
x 1.03 = $59.474599808
acct-2 spend (SpendGate.account_spent_usd, external ledgers 0): $231.599730238
ACCOUNT_2_CAP_USD expected = ceil_cent(291.074330046) = 291.08; config has 291.08; match: True
E14_EXT2010_SESSION_CAP_USD expected = floor_cent(59.474599808) = 59.47; config has 59.47; match: True
session cap <= 60.00: True; <= 124.00: True; account headroom 59.480269761698 <= 124.00: True
buy gate: session stage-E.14-ext2010 cap 59.47 spent 0.000000 -> left 59.470000; account cap 291.08
  spent 231.599730 -> headroom 59.480270; left <= headroom: True; request cap 3.0
```

- Every one of the 642 new lines is a `quote` event of session stage-E.14-2026-10-05 on acct-2 with ts at or after the
  run start, usd 0.0 and a non-null quoted_usd; each of the plan's 642 chunk keys appears exactly once; no line is
  outside the plan. The ledger has not moved since the run (29682 lines now, as the log's closing `wc -l`). The
  pre-cut sanity (0 lines before line 29040 dated after the run start) confirms the 29040 cut is clean.
- The total agrees with the lead's guard output (fresh_quote_c1.json total_usd 57.74232991039197) to 1e-9 and with
  the tool log line `TOTAL QUOTED $57.742330 (x 1.03 = $59.474600)`; the guard output was not relied on.
- acct-2's spend from `SpendGate(session_id="review-readonly", account="acct-2").account_spent_usd()` is
  231.599730238, the hand-off's "231.599730 unless the ledger moved" (the 642 new lines are $0.00, so it did not).
- Rounding: Decimal ROUND_CEILING on 291.074330046 gives 291.08 and ROUND_FLOOR on 59.474599808 gives 59.47; the
  E.14-pattern float form (`math.ceil/floor(round(x*100, 6))/100`) gives the same two values. Neither is within
  0.0001 of a cent boundary, so no float artefact can flip them.
- Bounds: 59.47 <= 60.00 (V27) and <= 124.00; the account headroom the cap creates (59.480270) <= 124.00 (A1 as
  amended). Funds: the user's confirmed balance is $130.23 (V30 amendment, DECISIONS.md:557), above the $59.48 of
  headroom, so the raised cap never exceeds the funds.
- `data.pull_hist.require_buy_ready` (data/pull_hist.py:270-289): both caps > 0 (59.47, 3.0); left under the session
  cap 59.470000 <= account headroom 59.480270, `round(left - headroom, 9) = -0.01027 <= 0`, so the check passes with
  $0.010270 to spare. `data.spend_gate.decide` (spend_gate.py:191-209) refuses any commit with
  `session_spent + quoted > 59.47` and any with `account_spent + quoted > 291.08`, so commits under the ext2010
  session cannot exceed $59.47; the session cap binds before the account cap (59.47 < 59.480270). See NOTE 3 on
  settle deltas, which are pre-existing gate behaviour and not a v11 matter.

### Check 4: the tests. PASS

- AST diff against HEAD (ast_diff.py): only the cited assertions changed, function sets unchanged in all three files:
  - tests/test_e14_config_v10.py: 3 constants, new statements `L20: assert config.E14_EXT2010_SESSION_CAP_USD == 59.47`,
    `L32: assert config.ACCOUNT_2_CAP_USD == 291.08`, `L33: assert config.ACCOUNTS[config.ACCOUNT_2_ID].cap_usd == 291.08`
    (the freeze's 20, 32-33).
  - tests/test_e14_pull_hist.py: 2 constants, `L196: assert (ext.session_id, ext.session_cap_usd) ==
    ('stage-E.14-ext2010', 59.47)` and `L300: assert config.E14_EXT2010_SESSION_CAP_USD == 59.47` (the freeze's 300,
    plus 196: ruling below).
  - tests/test_stage_e_config_v8.py: two assertions rewritten, `L64: assert floored == 249.67` and `L65: assert
    config.ACCOUNT_2_CAP_USD == 291.08`, replacing HEAD's `floored == 249.67 == config.ACCOUNT_2_CAP_USD` and
    `funds >= config.ACCOUNT_2_CAP_USD` (lines 64-65, the E.15 off-by-two reading; the freeze's "62-64" names a
    comment, the v8 arithmetic pin and only the first of the two cap assertions). See NOTE 2.
- Ruling on tests/test_e14_pull_hist.py:196 (the lead's open choice): WITHIN THE FREEZE. `ph.buy_gate(ph.PLAN_EXT2010)`
  builds its gate from `buy_policy(PLAN_EXT2010)`, which returns `(STAGE_E14_EXT2010_SESSION_ID,
  E14_EXT2010_SESSION_CAP_USD, E14_REQUEST_CAP_USD)` read at call time (data/pull_hist.py:240-246), so
  `ext.session_cap_usd` is E14_EXT2010_SESSION_CAP_USD itself and the HEAD assertion `== ("stage-E.14-ext2010", 0.0)`
  pins that value to 0.0. It is therefore one of "the test assertions that pin those two values", the freeze's
  governing words; the parenthetical is a citation list, already shown incomplete by the off-by-two (E.15 item 14),
  and a harness whose own frozen tests fail cannot be what the freeze meant. Changing it to 59.47 is the minimal
  edit. The lead must record this second citation gap wherever the off-by-two is recorded (NOTE 1).
- No other assertion in tests/ pins either value: `grep -rn -E '249\.67|E14_EXT2010_SESSION_CAP_USD|"stage-E\.14-ext2010", 0\.0' tests/`
  finds only test_stage_e_config_v8.py lines 3 (docstring), 62-64 (v8's own arithmetic) and the six edited lines;
  the acct-2 cap is otherwise referenced only symbolically (`== config.ACCOUNT_2_CAP_USD` in test_e2b_pull_step2.py:371,704
  and test_e2b_pull_step2_e12.py:448).
- Run (19:16:33 to 19:21:33 PDT; `nice -n 10 uv run --no-sync python -m pytest -q -p no:cacheprovider` with a fresh
  PYTHONPYCACHEPREFIX; output .../scratchpad/review/pytest_review.out): **299 passed in 298.88s**, 0 failed, 0 errors.
  Per file (`--collect-only`): test_e14_config_v10 6, test_e14_pull_hist 40, test_stage_e_config_v8 10,
  test_spend_gate_accounts 13, test_pull_universe 57, test_e2b_pull_step2 44, test_e2b_pull_step2_e12 54,
  test_c1_context 7, test_c1_evaluate 23, test_c1_exclusions 5, test_c1_loader 1, test_c1_q_m1 19, test_c1_tables 16,
  test_c1_world 4 (sum 299). The full suite was not run here (the lead's background run owns it).

### Check 5: the manifest. PASS

- `sha256sum reports/stage_e2b_harness_freeze.json` = ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292,
  the lead's figure; `git show HEAD:reports/stage_e2b_harness_freeze.json | sha256sum` =
  fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b (v10, as C1 freeze section 11 records).
- `PYTHONPYCACHEPREFIX=<scratch>/pyc nice -n 10 uv run --no-sync python -m screening.harness_freeze verify --expected ba1ce996...`
  printed `preflight OK: ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292`, rc=0 (19:16:27 PDT).
  Negative control with the v10 digest: `Stage E harness preflight refused: reports/stage_e2b_harness_freeze.json
  sha256 ba1ce99672b7... is not the expected fde3a49c8e15...`, rc=1, so the verify does check the digest.
- v10 vs v11 by field (compare_manifest.py): top-level keys equal (categories, created_pdt, entry_modules, files,
  harness_dirs, head_at_creation, notes, stage, what); only `created_pdt` (2026-10-05T03:27:25-07:00 ->
  2026-10-09T19:10:26-07:00) and `head_at_creation` (77be2a90... -> 8e5707c7..., the current HEAD) differ among
  them; `categories` equal (1061 entries); `files` 1061 vs 1061 with the same key set (nothing added or removed);
  every entry has exactly the fields (bytes, sha256); the changed entries are exactly data/config.py,
  tests/test_e14_config_v10.py, tests/test_e14_pull_hist.py, tests/test_stage_e_config_v8.py, each with v11's
  sha256 and bytes equal to the working file and v10's equal to HEAD's blob; `unchanged entries not matching disk: []`.
- The manifest was built at 19:10:26 PDT, after the quote run ended (19:06:57) and after the cap edits it hashes.

### Check 6: the E.16 freeze. PASS

- `nice -n 10 uv run --no-sync python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4`
  printed `E.16 freeze OK: 97 files; manifest sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4`,
  rc=0 (19:16:33 PDT). The script's verify mode reads bytes only (its docstring lines 8-10; `write()` is only reached
  in write mode, lines 171-175).

### Findings

No BLOCKING. No SHOULD FIX.

- **NOTE 1 (record): two citation gaps in the freeze's test list.** (a) tests/test_e14_pull_hist.py:196 pins
  E14_EXT2010_SESSION_CAP_USD through `buy_gate(PLAN_EXT2010).session_cap_usd` and is absent from the freeze's list;
  (b) the freeze's "test_stage_e_config_v8.py:62-64" is lines 64-65 (E.15 item 14). Both edits are within the
  freeze's governing words. The lead should record both deviations from the citation list in the v11 commit message
  and the C1 return, as E.15 planned for (b). Evidence: data/pull_hist.py:240-246 (`buy_policy`), `git diff HEAD --
  tests/test_e14_pull_hist.py` hunk `@@ -193,7`, ast_diff.py output above.
- **NOTE 2 (record): the funds bound is no longer asserted in tests.** HEAD's tests/test_stage_e_config_v8.py:65
  `assert funds >= config.ACCOUNT_2_CAP_USD` (cap never above the funds) was replaced by the value pin `== 291.08`,
  because v8's `funds` (249.673761) is below the new cap and a funds check for v11 would need the $130.23 balance, a
  new constant the freeze does not allow in the test. The invariant holds in fact: headroom 291.08 - 231.599730 =
  $59.480270 against the user's confirmed $130.23 balance (DECISIONS.md:557). The lead should state this arithmetic
  in the commit message or STATE so the dropped assertion is covered by a record. Evidence: ast_diff.py output
  (`-Assert(... GtE ... ACCOUNT_2_CAP_USD)`), recompute_quote.py output.
- **NOTE 3 (informational, pre-existing behaviour): what the caps do and do not bound.** (a) `decide()` refuses
  commits past either cap, but `SpendGate.settle` (data/spend_gate.py) appends `actual - quoted` as a delta with no
  cap check, so the billed ext2010 total can exceed $59.47 by the settle deltas; the hand-off's step 11 "settle
  deltas checked" is the control. (b) Raising the account cap lifts acct-2's headroom from $18.070270 (v10) to
  $59.480270 for every acct-2 session, not only ext2010: read-only ledger sums show stage-E.12-2026-10-03 has
  $30.804031 of room under its $137.73 session cap (spent 106.925969) and stage-E.1-2026-09-24 $10.002806 under
  $113.48 (spent 103.477194). Both need their own `--buy` commands, which E.17 does not run, and C1's buy consumes
  the headroom to about $0.01, so nothing to fix; the lead should know the window exists between the v11 commit
  and C1's buy. Neither point is a v11 defect: the hand-off prescribes both cap formulas.
- **NOTE 4 (informational): stale historical comments and names the freeze does not let v11 touch.**
  data/config.py:172 "ACCOUNT_2_CAP_USD stays 249.67 (V26 ...)" (E.14 block header, not beside either cap);
  tests/test_e14_config_v10.py:3-4 docstring ("ACCOUNT_2_CAP_USD (V26) ... stay as they were") and the test name
  `test_acct2s_cap_and_the_step2_active_policy_are_unchanged` (line 31); tests/test_stage_e_config_v8.py:3 docstring
  ("ACCOUNT_2_CAP_USD = 249.67"); and tests/test_e14_pull_hist.py:297 `test_the_ext2010_buy_stays_refused_at_a_zero_cap_and_without_c1s_registration`,
  whose first `_main_buy` is now refused by the missing C1 registration (`require_registered`, pull_hist.py:283)
  rather than by a zero cap, so the ext2010 zero-cap branch is no longer exercised by that test (the es2011 test at
  line 291 still covers the branch). All are true statements about earlier harness versions; leave them for a later
  harness and mention them in the return.

### What was not done

- The full test suite: owned by the lead's background run (reports/stage_e17_briefs/pytest_v11.out, not read here).
- No vendor call was made; the fresh quote was taken from the ledger lines only, as the brief requires.
