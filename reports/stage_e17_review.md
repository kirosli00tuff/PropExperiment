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

## C1 STOPPED verdict verification (VerdictVerifier-FableXHigh)

Worker: worker-xhigh, model fable (Fable 5.1). Brief: reports/stage_e17_briefs/brief_c1_verify.md. Started 22:51 PDT,
written 23:08 PDT, 2026-10-09 (times from `date`). Scripts and counts: reports/stage_e17_c1_verify/ (verify_reference.py
-> reference_recount.json; verify_run_counts.py -> run_recount.json; verify_hashes.py -> hashes.json;
verify_order_leakage.py -> order_leakage.json; verdict.json ties them together). Nothing under ledger/, data/, the
marker, the result or any frozen file was written (git status on those paths: clean); c1_replication.evaluate was not
run; no vendor call, no key read. The rebuild ran at nice 10 with a fresh PYTHONPYCACHEPREFIX: 27.9 s wall, 2.02 GB
peak RSS, MemAvailable 8.9 GB before launch.

**Verdict: VERIFIED WITH NOTES.** The STOPPED verdict is the freeze's C10 rule (section 3) applied as written by the
frozen code (c1_replication/evaluate.py:376-384, 520-523) on counts I reproduced exactly from the frozen inputs. No
code or input error caused the stop. The notes concern the freeze text (its sections 2 and 3 are inconsistent for
g17_mbt) and the fact that the stop was fully decidable from frozen artefacts on 2026-10-05, before registration and
purchase.

### Check 1: the reference (E.12's applicable-row counts)

- Source: reports/stage_e14_c1_model.json "c10_reference" is written by c1_replication/q_m1.py:318
  (`c10_reference(build.panel)`, defined q_m1.py:237-247) from E.12's persisted panel, loaded with
  ml_route_v2.phase1.build.load_build from the read-only state copy. The model JSON was created 2026-10-05 03:29:57,
  15 s after the freeze commit 1680982 (03:29:42).
- Recount (verify_reference.py: my own pandas count, and the frozen function beside it): state copy verified against
  the manifest sha256 8a38eeb1... (51 files); E.12 panel 68,138 rows, 27 roots, 64 signals; NG ok rows h60 2,590, hF
  2,473; g17 counts h60 nq 2453, zn 2457, 6e 2450, cl 0, gc 2423, zc 2468, **mbt 87**; hF nq 2345, zn 2341, 6e 2354,
  cl 0, gc 2311, zc 2351, **mbt 84**. All 64 x 2 counts equal the model JSON's; the frozen function gives the same.
  34 signals have a zero reference count in both horizons (g17_cl and the 33 K1-K3/K5-K9 and MCL/6C/MNQ/MBT-vehicle
  members); 30 are live by count, not the 29 the annex's section 3 table states.
- Where E.12's g17_mbt applied: 87 of NG's 2,594 panel rows, on 29 trade dates 2024-01-04..2024-02-29, inside the
  E.12 training window 2019-11-19..2024-02-29, consistent with annex row 96 ("in E.12, live only from MBT's S_X
  2024-01-02").
- Result: 87 and 84 confirmed. See NOTE N-1.

### Check 2: the window and the run's counts

- verify_run_counts.py rebuilds the run's world and panel with the frozen building blocks the run used
  (load_calendars, c12_exclusions, hist_tables, build_world, replication_panel), never evaluate.run or
  evaluate.evaluate. World roots: NG, NQ, ZN, 6E, GC, ZC plus the C7 frames CL and MBT. The MBT frame holds 1 bar,
  trade date 2019-05-31; 0 bars with a trade date in 2010-06-07..2019-04-30; 0 bars at or before the last NG decision
  time in the panel. The CL frame: the same.
- Why no NG row can carry the MBT lead: ml_route_v2/signals/generic.py:339-357 `_lead` marks a row applicable only
  where `j = b.last_closed(view.t) >= 0` and `b.on_day(j, view.day)`; with every MBT bar after every decision time,
  j = -1 on every row, so app_g17_mbt = 0 by construction. Confirmed numerically: app_g17_mbt > 0 on 0 of the
  panel's 5,137 NG rows (not only the ok rows). The frozen test tests/test_c1_world.py:78-97 asserts the same
  (`(a.frame["app_g17_mbt"] == 0).all()`, line 96) and passes (3 frozen tests run, 3 passed, 5.25 s).
- Run counts reproduced exactly: NG ok rows h60 5,120, hF 4,538; g17 h60 nq 4836, zn 4858, 6e 4836, cl 0, gc 4778,
  zc 4806, mbt 0; hF nq 4297, zn 4307, 6e 4288, cl 0, gc 4231, zc 4270, mbt 0; all 64 x 2 counts equal the result's
  guards.C10; panel_counts (rows_in 5,751, rows_out 5,137 and every other count) and the six leg records equal the
  result's; feature_cols equal the model's (C11).
- Zero now but live in the reference: {g17_mbt} for h60 and for hF. Zero in the reference but live now: none. Every
  other zero-count feature now (g17_cl and the 33 members) was zero in E.12. My own rule gives dead = ['g17_mbt
  (h60)', 'g17_mbt (hF)'], identical to the frozen c10_check on my counts and to the result's stop_reason. g17_mbt is
  the only trigger.

### Check 3: code versus the freeze text

- Freeze section 3 (lines 64-66): "The run stops if any feature live in E.12 has 0 applicable rows (ruling C10) ...
  A C10 stop therefore CLOSES this registered attempt." Annex ruling table row C10: "stop if a feature live in E.12
  has 0 applicable rows"; annex build assertion (lines 113-116): "stop if any feature that was applicable on NG rows
  in E.12 has zero applicable rows in the replication".
- Code: evaluate.py:376-384 `c10_check` returns, per horizon, every signal whose reference count is > 0 and whose run
  count is 0; evaluate.py:520-523 raises C1GuardStop on a non-empty list; both sides use the same count definition
  (q_m1.c10_reference). The order inside evaluate() is build_world -> replication_panel -> C11 -> c10_counts ->
  c10_check -> trades (evaluate.py:501-526); the marker precedes evaluate() (run(), evaluate.py:553-559).
- The code implements the rule as written, with "live in E.12" = "applicable on at least one NG ok row in E.12's
  panel", which is the annex's own phrasing. The freeze contains no exemption: it never uses the word "exempt";
  "live" occurs only at lines 28-29 (the five legs to buy, "CL is never live on NG rows. MBT is not listed (n/a by
  design)") and 64-65 (the rule); "n/a" at lines 29, 48 and 64. Line 48 ("Unlisted legs get 'not applicable' (0 plus
  its flag) as in training") says how the feature is computed, not that it is excused from C10. Lines 15-16: where
  the freeze and the annex differ, the freeze rules, and its C10 sentence is unconditional.
- Result: no deviation from the freeze, so not a code error. The stop follows from the freeze's own text being
  inconsistent: section 2 calls MBT n/a by design while section 3 stops on any feature with a non-zero E.12 count,
  and g17_mbt's E.12 count is non-zero. See F-1.

### Check 4: order and leakage

- Log (reports/stage_e17_briefs/c1_evaluate.log): line 0 the date, line 1 the command, line 2 "C1 marker written at
  2026-10-09T22:47:44-07:00"; the two C10 count lines and the verdict line follow. The only numbers before the
  marker line are the date and the command's hashes. Every token after a signal name in the C10 lines is an integer.
  mtimes (PDT): marker 22:47:44.684, result 22:48:44.632, log 22:48:44.784.
- Marker: keys schema, test, started_local, out, inputs; no guards, world, panel or tests block; its inputs block is
  equal to the result's inputs block, so every record in it predates the first bar read.
- Result: every numeric leaf outside `inputs` is an integer count (0 non-integer leaves); the 24 float leaves inside
  `inputs` are all shares (max_share, share, unsourced_share_in_window, unsourced_share_of_trade_dates: C12 and
  calendar coverage), none bar-derived. Keys mean, mean_gross_ticks, t_B, p_one_sided, trades_sha256, tests,
  descriptive, n_trades, r_hat, bar_ticks, decision, c14_slippage_1_5x, c15, trades: 0 hits; the words mean, t_B,
  p_one_sided, trades_sha256, n_trades, r_hat, PASS, FAIL: 0 hits in the result text and 0 in the log. `guards`
  holds only C10. 11 of 11 checks pass.

### Check 5: registration and inputs

- ledger/trial_registrations.jsonl: 2 lines (baseline N 471, 2026-10-05 01:02:35; r001-C1, 2026-10-09 19:29:06:
  test C1, test_ids [C1-T1, C1-T2], freeze sha256 afc5c10f..., harness ba1ce996..., n_before 471, n_after 473). The
  result's registry record matches.
- Freeze file on disk: sha256 afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b (equal), tracked and
  unchanged in git (ls-files rc 0, diff --quiet rc 0). Harness: screening.harness_freeze.check gives manifest sha256
  ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292 with 0 problems. Model JSON sha256 c6075306...
  equal; both M1 payload sha256s equal the model JSON and the result; feature_cols sha256 and the q reprs equal.
  Store-hashes file sha256 b77bfc18... equal; the six ext2010 stores on disk hash to the file, the result's inputs
  and the result's world records. Calendar-hashes file sha256 d5e48579... equal; the six hist calendars, the release
  file (9a051211...) and the energy full sessions (3f2a273a...) hash as listed. c1_replication/*.py hash as in the
  result's code_sha256 and the model JSON's (unchanged since 2026-10-05). v2 freeze (a647cd06...) and Gate 0 list
  (53e7ef57...) equal. 12 of 12 checks pass.

### Findings

- BLOCKING: none.
- SHOULD FIX F-1 (for any new registration; the decision is the user's and the lead's, not mine): the freeze's C10
  rule and its section 2 are inconsistent for g17_mbt, and the inconsistency was decidable from frozen artefacts at
  2026-10-05 03:29:57: the frozen test asserts app_g17_mbt == 0 on every replication NG row
  (tests/test_c1_world.py:96), the frozen model JSON records g17_mbt 87/84 > 0, and c10_check stops on exactly that
  combination. From that moment C1 could only return STOPPED; registration (2026-10-09 19:29:06, N 471 -> 473) and
  the purchase (ruling C1-R3) followed 4 days 16 h later. Any future freeze should define "live in E.12" (or name the
  exempt n/a-by-design legs) in the same sentence as the stop rule, and run c10_check on the real reference against
  the sentinel-frame applicability before registering.
- NOTE N-1: annex row 99 (reports/stage_e13_ng_replication_draft.md:99) lists g17_mbt among the 35 signals that are
  "0 and flag 0 on NG rows" in E.12 and the annex counts 29 live signals; E.12's panel has g17_mbt applicable on
  87/84 NG ok rows (29 trade dates, 2024-01-04..2024-02-29), so 30 are live by count. Row 96 of the same table
  states the 2024 liveness correctly. The freeze rules over the annex (freeze lines 15-16) and its C10 sentence has
  no exemption.
- NOTE N-2: the unit test for the C10 stop (tests/test_c1_evaluate.py:253-259) uses a synthetic reference
  (k1_vwap_dist 12), so the suite never exercised the frozen c10_reference against the frozen sentinel frames; the
  one frozen test that touches g17_mbt (test_c1_world.py:96) asserts the very condition that, with the reference,
  guarantees the stop.
- NOTE N-3: c10_check (evaluate.py:383) treats a signal missing from the run's counts as 0 (`got.get(s, 0)`); not
  exercised here, both sides hold the same 64 signals.
- NOTE N-4: preconditions() hashes the six store files before the marker (check_stores, evaluate.py:219-232); that
  reads file bytes for sha256, not bars, and no bar-derived number exists before the marker. No finding.

Not done: nothing the brief asked for was left undone. M1 was not re-fitted and q not re-derived (outside the brief;
their hashes were checked).

## v12 review (HarnessReviewer-FableXHigh)

Worker: worker-xhigh, model fable. Brief: reports/stage_e17_briefs/brief_v12_review.md. Worked 23:18-23:34 PDT
2026-10-09 (times from `date`). Reviewed: the uncommitted working tree against HEAD 558a7ce (v11 + C1), the coder's
diff reports/stage_e17_briefs/v12.diff (sha256 5f68cc84a9ea0e7453c3f68d0ee756c08716c04bb7db08b1b38b07125088b4de, 9 file
sections; `git apply -R --check --binary` passes, so the tree equals HEAD + diff for those files) and the coder's
report (its claims re-derived below). No vendor call, no key or .env read, no write to ledger/ or data/, no commit.
Scripts under the session scratchpad (plan_check.py, base_rules_check.py, head_compare.py, probe2.py); every test run
at nice 10 with -p no:cacheprovider and a fresh PYTHONPYCACHEPREFIX outside the repo.

**Verdict: APPROVE WITH FIXES** (no BLOCKING finding; two SHOULD FIX items, F-1 and F-2, both before the first buy;
F-2 can be folded into the lead's cap-setting delta).

### Check 1. Scope: PASS

- `git diff HEAD --stat`: data/config.py (+12), data/hist_calendar.py (+6/-1), data/hist_store.py (+11/-1),
  data/pull_hist.py (+169/-18), tests/test_e14_hist_calendar.py (1 line), reports/stage_e2b_harness_freeze.json (the
  provisional manifest), plus the lead's own reports/stage_e17_{STATE,review,rulings}.md (not harness files, hashed by
  no freeze). Untracked under data/, tests/, base_rules/, screening/, sim/, rules/: exactly
  data/calendars/hist2010/livestock.json and tests/test_e17_v12_{pull_hist,hist_calendar,hist_store}.py. No stray .py
  under a harness dir (the manifest diff in check 6 shows no other entry).
- livestock.json: sha256 802a4dd98a71776af58748c43c2a70772a966a2e37dd08e32fef1ebfe023ba5d, 364,732 bytes, equal to
  reports/stage_e16_calendars/hist2010_livestock.json (`sha256sum` of both); the E.16 freeze records that sha and the
  coder's test test_the_copy_is_byte_identical_to_the_frozen_file_and_its_recorded_sha256 pins it.
- data/config.py: the only change is the new block at lines 203-214 (STAGE_E17_EXT2010H_SESSION_ID =
  "stage-E.17-ext2010h", E17_EXT2010H_SESSION_CAP_USD = 0.00, comments); ACCOUNT_2_CAP_USD unchanged (291.08).
  data/hist_calendar.py: HIST_GROUPS gains "livestock" plus docstring/comment. data/hist_store.py: the CLI `--plan`
  choices gain "ext2010h" plus docstring; no logic change (confirmed by reading expected_names, input_files,
  refuse_inputs, hist_spec, drop_outside_window, run_product: all go through plan_chunks/get_plan).
- E.16 freeze: `uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97...` ->
  "E.16 freeze OK: 97 files". screening/harness_freeze.py is NOT among its 97 files (only stage_e_engine, stage_e_frozen,
  stage_e_rules, stage_e_verdict, trial_registry under screening/); its `pins` hold the v10 manifest sha and the C1
  freeze file only, so v12's manifest change does not touch them.
- C1 freeze inputs (reports/stage_e14_c1_freeze_inputs.json, 43 files re-hashed by script): only
  reports/stage_e2b_harness_freeze.json changed (838201c4... vs the recorded fde3a49c... v10), as expected.
- tests/test_e14_hist_calendar.py:164 ("livestock" -> "crypto" as the unknown-group example): ruled WITHIN the coder's
  brief's exception ("an assertion that pins a value this diff must change"). The test's intent (an unknown hist group
  is refused) holds: "crypto" is in data.calendars.GROUPS (data/calendars/__init__.py:18) and not in HIST_GROUPS, so
  the loader still raises "unknown hist calendar group". The file is hashed by the harness manifest (pattern
  test_e14_*.py), not by the E.16 freeze. No finding.

### Check 2. Plan ext2010h: PASS

By my own script (plan_check.py), independent of the coder's tests:
- `root order equals windows purchase_21_roots: True`; `roots 21 total chunks 1993 every root list ==
  monthly(start_month..2019-05-01): True` (each root's `chunks_of` equals the months from
  products.<ROOT>.start_month through 2019-04, end exclusive 2019-05-01, and its length equals
  chunks_2010_to_2019_04: 18 x 106, TN 40, RTY 23, HE 22); `plan_chunks 1993 distinct keys 1993`.
- `trade 2010-07-01 2019-04-30 data 2010-07-01 2019-05-01 test E16 ('E16-H1', ..., 'E16-H5')`; HIST_PLAN_NAMES
  ('es2011', 'ext2010', 'ext2010h'); the union `chunks` is the 106 months 2010-07..2019-04.
- check_hist_chunk refusals (all HistPlanError): 6A 2010-06-06..07-01 and 2010-06-01..07-01 ("not one of plan
  ext2010h's 106 6A chunks 2010-07-01..2019-05-01"), TN 2015-12 ("40 TN chunks 2016-01-01..2019-05-01"), HE 2017-06,
  RTY 2017-05, 6A 2019-05, 6A 2019-04-01..2019-06-01, 6A 2010-07-01..2010-09-01 (a two-month span), NG 2010-07 ("'NG'
  is not a root of plan ext2010h"), an ext2010 NG chunk and an es2011 ES chunk ("a chunk of plan 'ext2010', not
  'ext2010h'"). TN 2016-01-01..2016-02-01 accepted.
- base_rules (base_rules_check.py): for all 21 roots a file at hist_store.hist_parquet_path(root, "ext2010h") has the
  name hist_plan.expected_name gives, passes check_name (2010-06-06 <= 2010-07-01 <= WINDOW_START[root]; TN 2016-01-01,
  RTY 2017-06-01, HE 2017-07-01) and check_plan with default_resolver (window 2010-07-01..2019-04-30 from
  get_plan("ext2010h"), metadata plan "ext2010h", trade_date_range [max(first, window start), 2019-04-30]):
  `21 of 21`. fixed_plan refuses NG under ext2010h and 6A under ext2010.
- es2011 and ext2010 versus HEAD (head_compare.py loads HEAD's data/pull_hist.py beside the working one): ES2011 and
  EXT2010 equal field by field (root_chunks () in v12), plan_chunks keys equal (96; 642), buy_policy equal
  (('stage-E.14-2026-10-05', 0.0, 3.0); ('stage-E.14-ext2010', 59.47, 3.0)), the check_hist_chunk refusal message for
  an out-of-plan chunk byte-identical, the sources of buy_gate, require_buy_ready, run_hist_buy, run_hist_quotes and
  _check_args identical; quote_gate differs only in its docstring (the diff shows the one added sentence). The quote
  session of both v10 plans is still STAGE_E14_SESSION_ID. CLI: `--roots` with es2011 or ext2010 (quote or buy) returns
  RC_REFUSED from select_roots before any gate is built (no banner logged) and before the key loader.

### Check 3. Spend safety: PASS, with F-1 (SHOULD FIX) and N-1 (NOTE)

- Own session: quote_session_id("ext2010h") and buy_policy("ext2010h") both give "stage-E.17-ext2010h" (cap 0.0,
  request cap 3.0); _plan_quote_gate refuses an ext2010h quote through a gate of another session (the coder's test
  test_an_ext2010h_quote_through_a_gate_of_another_session_is_refused, passing). The ledger holds 0 lines of that
  session today, so quotes_from_ledger's fallback cannot return an older session's line for this plan.
- Refusal at the 0.00 cap on the REAL tree (probe2.py, key loader and client factory replaced by canaries that raise):
  `--buy --plan ext2010h --account acct-2 --roots ZT ZF --harness-sha256 838201c4...` -> banner
  "stage-E.17-ext2010h: account acct-2 (cap $291.08, spent $289.417062) · session cap $0.00 (spent $0.000000) ·
  request cap $3.00", "plan ext2010h (test E16): 212 chunks over 2 root(s) ZT, ZF", "harness preflight passed:
  838201c4...", then "REFUSED before any vendor call (HistPlanError): ext2010h buy refused: session cap $0.00, request
  cap $3.00 (stage-E.17-ext2010h)"; rc 2; the key loader was never reached. require_buy_ready checks the cap before the
  registration, so the real registry (E16-H1..H5 not yet registered) was not the refusing check; the registration
  refusal (ids missing, H5 missing, ids under another label) is covered by the coder's three parametrized cases, and
  trial_registry.require_registered does enforce the label (`entry["test"] != test` raises, trial_registry.py:155).
- `--roots`: restricts plan_chunks to the named roots in the order given (ZT, ZF, ZB -> 318 chunks); refuses an empty
  list, a repeat (`--roots names ['ZT'] more than once`), a non-plan root (`--roots ['NG']: not root(s) of plan
  ext2010h`), and any use with es2011/ext2010; all before the gate. The fake buy of HE+RTY touches exactly 45 chunks,
  two purchase manifests, two raw dirs, two symbology files (coder's test, passing).
- **F-1 (SHOULD FIX, lead's design call): refuse `--buy --plan ext2010h` WITHOUT `--roots`.** Today a buy without the
  option covers all 21 roots in the windows file's order (6A, 6B, 6C, 6J, 6N, 6S, CL, HE, HG, LE, RTY, TN, UB, YM, ZB,
  ZF, ZL, ZM, ZS, ZT, ZW) until the session cap stops it: ZT, ZF, ZB (A3's first priority) come 20th, 16th and 15th, so
  an invocation that forgets the option spends the Part 2 budget on the wrong roots, irreversibly, while every gate
  passes. A4 says the purchase IS restricted to the A3 selection by the roots option; the harness enforces that only
  through the command line. The fix is one check in main after select_roots (if args.buy and plan.name in
  ROOTS_OPTION_PLANS and roots is None: raise HistPlanError), RC_REFUSED before any gate; `--quote-only` stays
  whole-plan (step 9 needs the 1,993). The coder's test test_the_ext2010h_buy_refuses_at_a_zero_cap_even_when_registered
  calls buy_argv() without roots and expects RC_REFUSED, which still holds; add one asserting the new reason. Not
  BLOCKING because the lead controls the command line and the cap bounds the loss, but it is the one failure mode
  the caps do not catch.
- **N-1 (NOTE, ruling on 4 concurrent buy processes over disjoint `--roots` sets, one session cap).** Mechanics read
  from data/spend_gate.py and data/quote_universe.py: every authorize re-reads the whole ledger
  (session_spent_usd/shared_spent_usd -> read_entries(ledger) each call), so the caps are global across processes,
  not cached per process; the commit line is appended right after authorize (quote -> authorize -> commit -> download;
  no vendor call between authorize and commit); LockedQuoteGate's lock is a threading.Lock (in-process only), there
  is no cross-process lock; appends are one buffered write per line to an O_APPEND handle. Consequences: (a) the race
  window is one process's authorize-read to its commit-append (one ledger parse, ~31,600 lines today, plus a dump),
  during which up to 3 other processes can authorize against the same stale total; worst-case overshoot of EITHER cap =
  3 x E14_REQUEST_CAP_USD = $9.00, realistic bound 3 x the largest chunk quote of the selection (E.12 averaged ~$0.08
  per chunk). The caps only bind when spend approaches them, so with the session cap set to the selection's total x
  1.03 and the buy restricted to that selection, the race matters only through settle deltas (billed over quote, up to
  3% per chunk, settled without a cap check, as in v10). Margin to require: session cap + $9.00 <= A1's remaining
  budget ($124.00 minus everything billed; C1's ext2010 session shows $57.817332 billed), else run serially. (b) A
  torn read of a line being appended would raise JSONDecodeError (a ValueError) and stop the process (both except
  lists include ValueError): fails closed; if it hits inside _settle's append the chunk is downloaded but unsettled and
  the rerun's preflight_targets refuses ("a file without a settled ledger line"), for the lead to resolve. Rare (needs
  a line straddling a page boundary during another process's read). (c) The condition file
  (VENDOR_ROOT/condition/GLBX.MDP3_2010-07-01_2019-05-01.json) is per plan, written once with open("x"): two processes
  finishing within the same instant -> one raises FileExistsError -> "every chunk is bought, but the free metadata
  fetch failed" -> RC_STOPPED after its chunks are bought and settled; a rerun skips them and finds the file. Safe,
  but expect a possible rerun; staggering the starts avoids it. Symbology files and purchase manifests are per root
  (disjoint), record_file writes tmp-then-replace per root. (d) The ledger's session_cumulative_usd and
  shared_cumulative_usd audit fields can repeat or step out of order under concurrency; the `usd` sums the gate uses
  stay exact. (e) Run every process with a fresh PYTHONPYCACHEPREFIX so no process writes .pyc files under harness
  dirs while another runs preflight. Verdict on the question asked: the gate's cap checks stay safe under this
  concurrency up to the $9.00 worst-case bound above; keep that margin or run one process.

### Check 4. Store builder for ext2010h: PASS, with N-2 and N-3 (NOTE)

- Inputs: expected_names(root, plan) = plan_chunks(plan, (root,)) -> chunks_of(root), the root's own list;
  refuse_inputs requires the manifest's names to equal it in order, in the root's own directory, none sealed (test
  test_the_inputs_are_exactly_the_roots_own_chunk_list and test_an_input_list_other_than_the_roots_own_chunks_is_refused_unopened,
  passing). Layout hist_parquet_path = <base>/ext2010h/<ROOT>/ohlcv-1m_<ROOT>_v_0_2010-07-01_2019-04-30_ext2010h.parquet
  (equal to hist_plan.expected_name for all 21, check 2). Metadata "plan": plan.name and trade_date_range from the
  written frame's first/last trade date (hist_store._metadata:410), inside the window by construction. Group:
  group_of(HE) = group_of(LE) = "livestock" (data/calendars/__init__.py:28), STAGE_E_POLICIES["livestock"] exists
  (data/group_session.py:521), load_hist_group_calendar("livestock") reads the copy; the coder's calendar tests show
  the copy and the frozen file give identical trade dates, early halts, 25 unsourced dates, holidays, late opens and
  sessions, and that base_rules reads the frozen original (K.LIVESTOCK_HIST_PATH).
- **N-2 (NOTE): the partial first trade date is accepted, nothing invented.** drop_outside_window drops only rows whose
  booked trade date is < 2010-07-01; the first bought minute (2010-07-01 00:00 UTC = 2010-06-30 19:00 CT) books to
  2010-07-01 and is kept (test test_the_partial_first_trade_date_is_kept_and_rows_outside_are_dropped_unread:
  before_first_trade_date == {}, the 19:00 CT bar is the first row of 07-01). So for the 18 roots starting 2010-07 the
  first session is missing its opening: 17:00-19:00 CT for fx/rates/metals/energy, 18:00-19:00 for grains, from
  15:30 CT for equity (YM). The E.16 freeze set DEFAULT_START = 2010-07-01 knowing 2010-06 is unbought (constants.py:
  "2010-01..2010-06 unpriced"), so this is a consequence of the frozen windows, not of v12; base_rules computes its
  first WARMUP_UNITS = 20 units without trading. The store summary's gap fields will show the missing opening;
  nothing refuses it. No action; record it beside the stores.
- **N-3 (NOTE): vendor symbology for TN, RTY and HE before listing is untestable here.** fetch_symbology stores the
  raw symbology.resolve responses over [2010-07-01, 2019-05-01) and reads `result[sym]` only; rows with no mapping are
  dropped and counted (hist_store._flag), not refused. If the vendor returns no mapping at all, the second resolve is
  called with an empty id list and any error becomes the named "free metadata fetch failed" HistPlanError AFTER the
  chunks are bought (RC_STOPPED; rerun skips bought chunks). The file is written once, read-only; a wrong one needs
  the lead's manual removal before a rerun. The coder's TN case (symbology from 2016-01-10) shows the builder accepts
  a late start. Reasonable; no change asked.

### Check 5. Tests: PASS

`nice -n 10 uv run python -m pytest -q -p no:cacheprovider` over tests/test_e17_v12_*.py, tests/test_e14_*.py (6
files), tests/test_base_rules_store.py, tests/test_base_rules_review.py: **282 passed in 29.05 s** (finished 23:22
PDT). Collected per file: test_e17_v12_pull_hist 69, test_e17_v12_hist_calendar 5, test_e17_v12_hist_store 27,
test_e14_* 160, test_base_rules_store 18, test_base_rules_review 3 (sum 282). Not run: the full suite (the lead's).
The coder's two reported full-suite failures (the committed-manifest test, the holdout-2 seal test in the worktree)
are environmental as described; the first clears when the manifest is committed.

### Check 6. Provisional manifest: PASS, with F-2 (SHOULD FIX)

- `uv run python -m screening.harness_freeze verify --expected 838201c4bf11b5e407b530c847472894aea8fa24204eabeb014d4077f4d4a56c`
  -> "preflight OK: 838201c4..." (also passed inside the real-tree buy probe above).
- v11 (HEAD, ba1ce996...) vs v12 entry by entry (script): 1,061 -> 1,062 files; changed entries exactly data/config.py,
  data/hist_calendar.py, data/hist_store.py, data/pull_hist.py, tests/test_e14_hist_calendar.py (bytes and sha256
  only); added data/calendars/hist2010/livestock.json (sha 802a4dd9..., 364,732 bytes, category "harness_code" like
  the other six hist2010 calendars); nothing removed; entry_modules, harness_dirs, notes, stage, what equal;
  created_pdt and head_at_creation differ as they must.
- **F-2 (SHOULD FIX, fold into the cap delta): the new cap and session id are pinned only in an unhashed test.**
  TEST_PATTERNS (screening/harness_freeze.py:270-273) lists test_e14_*.py but no test_e17_*.py, so
  tests/test_e17_v12_*.py are outside the manifest (confirmed: no "e17" path in it). In v11 every cap pin sat in a
  hashed file (test_e14_config_v10.py, test_e14_pull_hist.py, test_stage_e_config_v8.py); here
  E17_EXT2010H_SESSION_CAP_USD (0.00) and STAGE_E17_EXT2010H_SESSION_ID are pinned at test_e17_v12_pull_hist.py:204
  only, and test_the_ext2010h_buy_refuses_at_the_configured_placeholder_cap skips once the cap is nonzero. When the
  lead sets the caps (hand-off step 8: "tests pinning these values"), add the two pins to tests/test_e14_config_v10.py
  (hashed by test_e14_*.py; it already pins ACCOUNT_2_CAP_USD and E14_EXT2010_SESSION_CAP_USD) and update the 0.00
  pin in test_e17_v12_pull_hist.py. Extending TEST_PATTERNS instead is not blocked by the E.16 freeze (harness_freeze.py
  is not among its files) but is a screening/ edit outside the hand-off's "nothing else" list: the lead rules; the
  test_e14_config_v10.py pin needs no ruling. It does not affect spend safety (preflight hashes the code the buy runs),
  which is why it is not BLOCKING.

### Other notes (NOTE)

- N-4 cosmetic, unchanged on purpose by the coder: ledger notes read "Stage E.14 hist purchase (ext2010h, test E16)"
  (HIST_NOTE) and the store metadata's stage/source strings say E.14/v10; the quote summary's chunk_range and the
  plan log line use the union span 2010-07-01..2019-05-01 even for a `--roots TN` subset (the chunk COUNT is the
  subset's). The session id and the manifest sha beside them disambiguate. Acceptable; mention in the STATE.
- N-5 command path: data.pull_step2 keeps `--plan` choices ("es2011", "ext2010") and treats `--roots` as a step-2
  option it refuses with `--plan` (pull_step2.py:1190-1197), so `python -m data.pull_step2 --plan ext2010h` is refused
  by argparse; step 9's quote and step 11's buys run as `uv run python -m data.pull_hist ...`. Equivalent: pull_step2's
  hist path only hands the same argv to pull_hist.main with the same key loader and client factory.
- N-6 for the lead's cap delta (read-only gate, 23:28 PDT): acct-2 spent $289.417062, ACCOUNT_2_CAP_USD $291.08,
  headroom $1.662938; session stage-E.14-ext2010 (C1's buy) $57.817332 over 1,928 lines; stage-E.17-ext2010h 0 lines.
  require_buy_ready refuses when (session cap - 0) > headroom, so any session cap above $1.66 is refused until
  ACCOUNT_2_CAP_USD is raised per step 8 (spent + fresh total x 1.03, ceil to the cent). The step-9 guard must be run
  with `--plan ext2010h --session stage-E.17-ext2010h` and the quote without `--roots` (1,993 chunks).
- N-7 three agent worktrees remain under .claude/worktrees (a463ba71... is the v12 coder's at 558a7ce; two older).
  They lie outside HARNESS_DIRS, so the manifest ignores them; prune after the commit.

### Not done / could not verify

- Vendor behaviour (symbology.resolve for TN, RTY, HE over 2010-2019; Databento's handling of an empty id list):
  N-3 states the fail-closed path; not exercisable without a vendor call.
- The full test suite and ruff were not run (outside the brief; the coder reports them).
- The final cap values: not yet set; the lead's follow-up delta is awaited (this worker stays available).

### v12 caps follow-up

Follow-up on the lead's message (00:08-00:12 PDT 2026-10-10, times from `date`). Everything below is recomputed from
ledger/databento_spend.jsonl lines 31,611-33,603 by script (ledger_a3.py in the session scratchpad), from
reports/stage_e12_ranking.json and from the working tree; none of the lead's JSONs (fresh_quote_ext2010h.json,
stage_e17_a3_selection.json, stage_e17_fallback.json) was used as an input. No vendor call, no key or .env read, no
write except this subsection.

**Verdict: APPROVE.** The caps, the selection, the F-1 fix and the manifest check out; one NOTE (N-8) on the tightened
session cap's consequence, nothing to fix.

1. The fresh quote (ledger lines 31,611-33,603; the ledger holds 33,603 lines): 1,993 rows, every one a `quote` event of
   session stage-E.17-ext2010h on acct-2 with ts inside 06:36:08-07:01:54 UTC (23:36:08-00:01:54 PDT), usd 0.0,
   quoted_usd set (0 failed), each of plan ext2010h's 1,993 chunk keys exactly once (0 duplicates, 0 missing, 0 lines
   outside the plan); no other line of that session anywhere in the ledger. TOTAL $153.965349 (153.965348526836),
   x 1.03 $158.584309: equal to the lead's guard total and to E.12's record. Per-root sums (chunks, usd, largest chunk):
   6A 106 10.682692 0.112747; 6B 106 10.170910 0.108640; 6C 106 9.812140 0.106687; 6J 106 10.859810 0.114609;
   6N 106 7.598356 0.097947; 6S 106 8.668967 0.099590; CL 106 11.023248 0.115211; HE 22 0.454877 0.022934;
   HG 106 10.084233 0.112389; LE 106 3.127273 0.045109; RTY 23 1.902238 0.109589; TN 40 2.791587 0.085009;
   UB 106 7.218561 0.093179; YM 106 10.502610 0.114481; ZB 106 9.232754 0.100272; ZF 106 9.091797 0.101667;
   ZL 106 6.223149 0.081453; ZM 106 5.659884 0.074943; ZS 106 6.931452 0.094924; ZT 106 6.041231 0.073899;
   ZW 106 5.887580 0.074129.
2. A3 greedy, recomputed: B = 124.00 - (289.417062 - 231.599730) = 66.182668. Order ZT, ZF, ZB, then
   stage_e12_ranking.json's 28 entries by rank with vehicles mapped through base_rules.constants.VEHICLE_OF inverted
   (MNQ->NQ, MGC->GC, MCL->CL, MYM->YM, M2K->RTY, MHG->HG), C1's six skipped (NQ, GC, NG, 6E, ZN, ZC), MBT skipped
   (outside the 21); every one of the 21 roots is reached. Take/skip with the budget left after each take:
   TAKE ZT 6.222467 (59.960201), ZF 9.364551 (50.595650), ZB 9.509736 (41.085913), CL 11.353946 (29.731968),
   ZL 6.409844 (23.322124), ZS 7.139396 (16.182728), UB 7.435118 (8.747610), TN 2.875335 (5.872276);
   SKIP YM 10.817688; TAKE RTY 1.959305 (3.912971), LE 3.221091 (0.691880); SKIP HG 10.386760, 6S 8.929036;
   TAKE HE 0.468523 (0.223357); SKIP 6J, 6A, 6B, 6N, ZM, ZW, 6C (each > 0.223357). Selected
   ZT ZF ZB CL ZL ZS UB TN RTY LE HE: 933 chunks, quote $64.038166 (64.038166180249), x 1.03 $65.959311; not funded:
   YM, HG, 6S, 6J, 6A, 6B, 6N, ZM, ZW, 6C (10). Equal to the lead's selection, counts and totals. Largest chunk quote
   of the selection: $0.115211 (CL; 0.115211457014).
3. Caps and bounds: ACCOUNT_2_CAP_USD = ceil_cent(289.417062 + 65.959311 = 355.376373) = 355.38, <= A1's absolute
   bound 231.599730 + 124.00 = 355.599730 (PASS). E17_EXT2010H_SESSION_CAP_USD: the hand-off formula gives
   floor_cent(65.959311) = 65.95; the lead set 65.82 = floor_cent(66.182668 - 3 x 0.115211 x 1.03 = 65.826666), a
   tightening (never looser) recorded in rulings V12-R3. Checks: 65.82 + 3 x 0.115211 x 1.03 = 66.176003 <= B 66.182668
   (PASS: four concurrent processes' worst-case race, N-1, stays inside A1); worst-case stage total 57.817332 + 66.176003
   = 123.993335 <= 124.00 (PASS); require_buy_ready: left 65.82 <= headroom 355.38 - 289.417062 = 65.962938 (PASS); the
   session cap binds before the account cap (289.417062 + 65.82 = 355.237 < 355.38), and the worst-case race may pass the
   account cap by up to $0.21 (355.593) while staying under A1's 355.599730. Values in data/config.py:93 and :219 read
   355.38 and 65.82; the comment's 0.118667 is 0.115211 x 1.03.
   **N-8 (NOTE):** 65.82 is $0.139311 below the selection's x 1.03 total (65.959311). Commits sum to $64.038166, so
   the buy completes unless settle deltas (billed over quote, up to 3% per chunk, as in v10) add more than $1.78 across
   the 933 chunks; at C1's observed overage (57.817332 billed against a ~57.74 quote, +0.14%) the selection settles near
   $64.13. If every chunk billed +3%, the cap would refuse the last commits and stop the buy short of the selection
   (RC_STOPPED, fail-closed), never overspend. Acceptable; the lead should know the selection is not guaranteed complete
   under that extreme.
4. F-1 fix, correct: data/pull_hist.py _check_args, inside `if args.buy:`, `if args.plan in ROOTS_OPTION_PLANS and not
   args.roots: raise HistPlanError("--buy --plan ext2010h requires --roots ...")`. _check_args runs before get_plan,
   select_roots, the gate, the preflight and the key loader, so the refusal is RC_REFUSED with nothing built; es2011 and
   ext2010 are untouched (not in ROOTS_OPTION_PLANS); `--quote-only` stays whole-plan. New test
   test_an_ext2010h_buy_without_roots_is_refused_before_the_preflight (cap 10.0, registered, preflight_ok == []); the
   zero-cap test lost its roots-less assertion and now expects one preflight call.
5. Changed since my review (working tree against HEAD + v12.diff rebuilt in the scratchpad, `cmp` per file): exactly
   data/config.py (the two caps and their comments; nothing else), data/pull_hist.py (the three F-1 lines),
   tests/test_e17_v12_pull_hist.py (pin 0.00 -> 65.82, the F-1 test, the roots-less assertion removed),
   tests/test_e14_config_v10.py (291.08 -> 355.38 twice, plus the two F-2 pins of the session id and 65.82),
   tests/test_stage_e_config_v8.py (291.08 -> 355.38). data/hist_calendar.py, data/hist_store.py, livestock.json,
   tests/test_e14_hist_calendar.py and the other two new test files are byte-identical to the reviewed tree; `git
   status` shows no other change under data/, tests/, screening/, sim/, rules/, base_rules/.
6. Manifest: `uv run python -m screening.harness_freeze verify --expected ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32`
   -> "preflight OK: ece91ae8..." (file sha256 equal). Against v11: 1,061 -> 1,062 entries; changed exactly
   data/config.py, data/hist_calendar.py, data/hist_store.py, data/pull_hist.py, tests/test_e14_config_v10.py,
   tests/test_e14_hist_calendar.py, tests/test_stage_e_config_v8.py; added data/calendars/hist2010/livestock.json;
   head_at_creation 558a7ce, created 2026-10-10T00:04:06-07:00. F-2 is closed: both new pins sit in a hashed file.
7. Tests (nice 10, -p no:cacheprovider, fresh PYTHONPYCACHEPREFIX), tests/test_e17_v12_pull_hist.py (70 collected) and
   tests/test_e14_config_v10.py (6): **75 passed, 1 skipped in 24.86 s** (00:08:48-00:09:14 PDT); the skip is
   test_the_ext2010h_buy_refuses_at_the_configured_placeholder_cap, by design once the cap is nonzero. The full suite
   was not run (the lead's).

Not done: nothing asked was left undone.

## H1-H5 verdict recomputation (VerdictVerifier-FableXHigh)

Brief reports/stage_e17_briefs/brief_h_verify.md; worker-xhigh, model fable. Started 01:40, written 02:03 PDT
(2026-10-10). Scripts and artifacts under reports/stage_e17_h_verify/ (vv_common.py, recompute_series.py,
recompute_h5.py, recompute_stats.py, checks_windows.py, spot_check.py, h2_signal_check.py, compare.py;
recompute.json sha256 d8656790..., comparison.json b96403cd..., spot_check.json e5aa6a62..., series_H1..H5.json,
h5_build.json, checks_windows.json, flags_and_cost_decomposition.json, h2_signal_check.json). Every number below was
computed by these scripts from the units files and the stores and written to disk (recompute.json, 01:52) BEFORE
compare.py opened any result's `stats` or verdict.json (01:57). base_rules was never imported or run; the frozen
modules screening/stage_e_frozen.py (D8 tables) and rules/products.py were used for the cost arithmetic, as the brief
allows. Holdout: `data.holdout status` all_ok, unlocks_logged 0 at start (01:40) and end (01:59). No ledger, data,
run or frozen file was written. nice 10, fresh PYTHONPYCACHEPREFIX, one store in memory at a time, no price printed.

### 1. Series rebuilt from the units files (recompute_series.py, recompute_h5.py)

- Units files hold only warm-up and traded rows (H1 540 + 55,070; H2 40 + 112 legs; H3 80 + 405; H4 540 + 51,919);
  excluded candidates are not written, so exclusions by reason other than traded/warm-up are not checkable from them.
- Every traded row's sigma reproduces EXACTLY (max relative deviation 0.0 on 55,070 + 112 + 405 + 51,919 rows) as
  the sample std (ddof 1) of the last 20 g values (g = gross_cents / 100, dollars) of the same key whose exit date is
  strictly before the row's entry date; every window held exactly 20 values. Every net_ru reproduces as
  (gross_cents - costs_cents[case]) / 100 / sigma (0 mismatches, all cases). The x100 in the lead's note is cents vs
  dollars: gross and costs are exact cents (6,020 H1 rows are Fraction strings, ZT/ZF ticks of 781.25 cents), sigma is
  dollars.
- H1/H4 series: the equal-weight mean of net_ru over products traded on each date (3,380 / 3,381 dates, 1 to 27
  products per date). H2: the pair = sum of the two legs' net_ru per month (56 months, always 2 legs). H3: one entry
  per auction (405; two tenors share 2012-04-10's... one date holds two auctions, kept apart as units).
- H5: grid = union of the H1 and H4 results' grid_dates (3,401 each; eligible dates with any signal, not
  reconstructible from units) and the open dates of traded H2/H3 units = 3,460 dates (2010-07-02..2024-02-29), equal
  to the H5 result's grid. x_H1, x_H4 from my series (0 when no trade); x_H2, x_H3 = the H2/H3 results' daily
  mark-to-settlement `component` series, accepted only after a telescoping check: the sum over a unit's open dates
  equals the unit's net_ru per H2 month (worst 8.9e-16) and in total for H3 (2.7e-15; tenors overlap); then verified
  against the stores in section 3. Trailing-60 sigma (ddof 1) over the 60 grid dates strictly before d, mean over
  components with sigma > 0, first 60 dates warm-up: n = 3,400 per case.

### 2. Statistics, Holm, pass bar, DSR (recompute_stats.py; frozen NW lags 5/1/3/5/5; one-sided p_t Student n-1,
p_nw normal with a Bartlett HAC; year thresholds 10, H2 6; fewer than 3 qualifying years fails)

| Test | case | n | mean | sd | t | t_NW | p_t | p_NW | p = max | years q/pos | year stab. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | base | 3380 | -0.16132 | 0.46861 | -20.014 | -19.018 | 1.0 | 1.0 | 1.0 | 15/0 | FAIL |
| H1 | stress | 3380 | -0.42396 | 0.48472 | -50.851 | -43.088 | 1.0 | 1.0 | 1.0 | 15/0 | FAIL |
| H1 | slip150 | 3380 | -0.23583 | 0.47159 | -29.073 | -26.908 | 1.0 | 1.0 | 1.0 | 15/0 | FAIL |
| H2 | base | 56 | 0.34402 | 1.69893 | 1.515 | 1.611 | 0.0677 | 0.0536 | 0.0677 | 6/5 | pass |
| H2 | stress | 56 | 0.28679 | 1.69411 | 1.267 | 1.347 | 0.105 | 0.089 | 0.105 | 6/5 | pass |
| H2 | slip150 | 56 | 0.32898 | 1.69768 | 1.450 | 1.542 | 0.0764 | 0.0616 | 0.0764 | 6/5 | pass |
| H3 | base | 405 | -0.01533 | 1.16883 | -0.264 | -0.226 | 0.604 | 0.589 | 0.604 | 12/5 | FAIL |
| H3 | stress | 405 | -0.08433 | 1.17032 | -1.450 | -1.243 | 0.926 | 0.893 | 0.926 | 12/5 | FAIL |
| H3 | slip150 | 405 | -0.03258 | 1.16912 | -0.561 | -0.481 | 0.712 | 0.685 | 0.712 | 12/5 | FAIL |
| H4 | base | 3381 | -0.04801 | 0.41571 | -6.715 | -6.448 | 1.0 | 1.0 | 1.0 | 15/0 | FAIL |
| H4 | stress | 3381 | -0.11195 | 0.41624 | -15.639 | -14.995 | 1.0 | 1.0 | 1.0 | 15/0 | FAIL |
| H4 | slip150 | 3381 | -0.06661 | 0.41577 | -9.316 | -8.948 | 1.0 | 1.0 | 1.0 | 15/0 | FAIL |
| H5 | base | 3400 | -0.14918 | 5.96940 | -1.457 | -1.468 | 0.927 | 0.929 | 0.929 | 15/2 | FAIL |
| H5 | stress | 3400 | -0.37254 | 2.54119 | -8.548 | -8.654 | 1.0 | 1.0 | 1.0 | 15/0 | FAIL |
| H5 | slip150 | 3400 | -0.21299 | 4.34858 | -2.856 | -2.883 | 0.998 | 0.998 | 0.998 | 15/2 | FAIL |

- Holm at 0.05, m = 5, base case: H2 p 0.0677 vs 0.0100 (no), H3 0.604 vs 0.0125, H5 0.929 vs 0.0167, H4 1.0 vs
  0.025, H1 1.0 vs 0.05: no rejection. Pass bar: H1 FAIL (Holm, mean, years), H2 FAIL (Holm only; mean > 0, n 56,
  years 5/6 pass), H3 FAIL (Holm, mean, years), H4 FAIL (Holm, mean, years), H5 FAIL (Holm, mean, years).
- N = 478 from ledger/trial_registrations.jsonl (baseline 471 + C1 2 + E16 5; last n_after 478; file sha256
  851f1821...). DSR at N = 478 (stage_e_verdict.dsr_table re-implemented: population moments, Sharpe variance =
  population variance of the five base-case per-unit Sharpes = 0.0314383, E[max SR] 0.538836): H1 0.0, H2 0.00639,
  H3 8e-29, H4 0.0, H5 1e-233.
- Comparison with the result files (compare.py): all five tests' series match mine to <= 2.8e-14 (H1 8.9e-16, H2 0,
  H3 0, H4 6.7e-16, H5 2.8e-14) with identical dates; every stats field (n, mean, sd, t, t_nw, nw_lags, p_t, p_nw, p,
  year_stability min_units/qualifying/positive/passes) matches to <= 2.1e-16 relative. verdict.json (01:39:53):
  n_trials_at_verdict 478, registry path and sha256 851f1821..., holm_alpha 0.05, every test pass false with the same
  four checks as mine, reported stress and slip150 cases equal to mine, result_sha256 of H1..H5 equal to the files'
  sha256s (H5 6cf50148...), DSR block: variance 0.031438313313327575, E[max] 0.5388361054322071, DSR H1 0, H2
  0.006393990964780438, H3 0, H4 0, H5 0 (mine differ at 1e-11 from scipy's normal CDF/PPF against funnel's erf and
  Acklam approximations; H3/H5 underflow to 0 there).

### 3. Spot checks against the stores (spot_check.py, h2_signal_check.py; 44 store files, each sha256 equal to the
run manifest before any row was read; bars read by trade-date filter, one store at a time)

- Units checked: H1 100 (all 27 products x era x direction strata, 1 per stratum, plus 3 units each with
  exit_at_close, entry_no_new, event-window and uncalibrated fills), H4 97 (same design), H2 all 56 months (112 legs),
  H3 all 405 auctions. For each: the fill instants and prices at the frozen minutes (H1 S-30 open and S open, or the
  close of bar S-1 when bar S is absent/in a scheduled closure, R-B1; H4 O_p+1 and S-31 with the first-trade-date-of-
  week livestock open; H2 the decision minute max(S_NQ, S_ZN) and the first usable bar after the 15:15 closure for
  NQ before 2020-10-26; H3 14:00 on t-3, t (flip, 2 contracts) and t+5; rolls at the last bar before and the first
  bar at or after each raw_symbol change), the signal and direction (H1 sign of close(S-31) minus the prior trade
  date's close(S-1); H4 minus sign of d-1's window move with its own R-B1 close point), S-30 > O_p, settle_ct,
  after_1508, exit_at_close, entry_no_new, event and uncalibrated flags, gross in exact cents (price-path ticks x the
  vehicle's tick value: MNQ, MYM, M2K, MCL, MGC, MHG, else the root), and the three cost totals per fill from the
  frozen D8 tables (commission per side + ceil(side slippage ticks x tick value), event window = any release of the
  root or vehicle in the frozen 2019-24 calendar or E.14's 2010-19 rows within 30 min before the fill, R-B2 largest
  per-side slippage where no bucket exists; stress + one vehicle tick per side; slip150 1.5 x the slippage ticks).
  Result: **0 mismatches in 714 units** (one fill of one unit never inside the D9.5a 2-minute guard).
- H2 signal: for all 56 months, d5 and dL (the fifth-last and last joint NQ-and-ZN trade date of the month from the
  stores), each leg's month-to-date return from PS(prior month's last joint day) to PS(d5) chained across the splice
  (43 legs crossed one), the rows' mtd fields (to 1e-9) and both directions reproduce: 0 mismatches.
- Daily mark series: H2's component series equals my bar-derived daily values on all 280 dates (max diff 0.0, all
  cases; entry-date value = minus the entry cost, marks at S or the R-B1 close point, exit against the prior mark).
  H3: my sum of open units' daily values agrees on 2,227 dates to <= 6.4e-5 risk units; the residual sits on exactly
  the 317 (base/stress) and 88 (slip150) units whose flip is costed with a per-contract ceil (NOTE 2). The 44 open
  dates without a 14:00 bar carry no value in either implementation ("a missing MK carries the P&L to the next mark").
- Lead focus 1 (H1 costs): verified in cents on 100 units. Decomposition over all 55,070 traded H1 units: mean
  gross/sigma +0.0522, mean base cost/sigma 0.2083 (rates 0.094 vs 0.300, FX 0.078 vs 0.181, equity 0.016 vs 0.101,
  energy 0.039 vs 0.114, metals 0.017 vs 0.265, grains 0.019 vs 0.190, livestock 0.019 vs 0.168); H4: +0.0057 vs
  0.0516. The negative means are the D8 round trip against a 30-minute (H1) or a part-day (H4) sigma, not a unit or
  arithmetic error (flags_and_cost_decomposition.json).

### 4. Exclusions, windows, headers (checks_windows.py)

- Units files vs results: traded 55,070 / 112 legs (= 56 units) / 405 / 51,919 and warm-up 540 / 40 / 80 / 540 equal
  the results' counters. Across all 108,706 rows: no date after 2024-02-29, none in 2024-03-01..2025-03-31 (embargo
  and holdout-2), none from 2025-04-01 (research window) or 2026-06-21, none in the store gap 2019-05-01..03, no
  multi-day unit spanning 2019-04-30/2019-05-06, no unit of a fallback root (6A 6B 6C 6J 6N 6S HG YM ZM ZW) before
  2019-05-06, none before 2010-07-01 for the 17 extended roots, RTY >= 2017-07-10, TN >= 2016-01-11, HE >= 2017-07-03
  (listing, R-S4), no LE H1/H4 unit on or before 2014-12-14 (R-S3), no H2 unit traded before 2016 (F-15).
- Every RUN_ONCE marker and every result header records registry path ledger/trial_registrations.jsonl with sha256
  851f1821... (equal to the file), the freeze sha256 5274aa97... (equal to reports/stage_e16_freeze.json), the run
  manifest sha256 256a5410... for H1-H4 (equal to the file; null for H5) and, for H5, the four component results'
  paths and sha256s (equal to the files: H1 43e6a570..., H2 a661cebc..., H3 a039a75c..., H4 76d34ed6...);
  registration r002-E16, ids E16-H1..H5, status complete. Fallback list sha256 1acf1d96... equals the registry note.

### 5. Findings

- BLOCKING: none.
- NOTE 1 (lead focus 2; for the lead's judgment in the synthesis, no effect on this verdict): H5's sd is carried by
  four grid dates: 2016-06-27 (H5 -224.5; x_H2 / sigma_60 = -899), 2020-09-25 (+183.3; H2 +734), 2021-07-27 (+143.0;
  H2 +573), 2012-04-10 (-123.6; x_H3 / sigma_60 = -370). Each is the first mark date after a sparse component
  switches on (H2's first unit 2016-06-24/30 and its returns after gaps of more than 60 grid dates; H3's first unit
  2012-04-09), when the trailing-60 window holds 59 zeros and one entry-cost value, so sigma_60 is near zero; the
  stress case's larger entry cost gives a larger sigma and a smaller spike (stress H2 -400, H3 -130), which is why
  the base sd 5.97 exceeds slip150 4.35 and stress 2.54. Descriptive (recompute.json h5_descriptive): without the
  top 1 / 5 / 10 / 30 |H5_d| dates the base sd is 4.56 / 0.63 / 0.61 / 0.57 and t is -1.06 / -13.1 / -13.7 / -14.6;
  H5's mean stays negative in every variant. This is the pre-registration's wording applied literally ("sample std
  over the 60 grid dates strictly before d", "0 when flat"), reproduced by my own code to 2.8e-14; the frozen
  definition, not the run, is fragile for sparse components, and any future reuse of the H5 form should guard it.
- NOTE 2: H3's flip (cover + long, 2 contracts in one fill) is costed as 2 x ceil(slippage x tick value), not
  ceil(2 x slippage x tick value); the spec's "per side, the frozen D8 one-side cost at size one" supports the
  per-contract reading. At most 1 cent per unit on 317 units (88 in slip150); no effect on any statistic shown.
- NOTE 3: "uncalibrated bucket" H1 544 = ZC/ZS/ZL 2012-05-21..2013-04-07 (S_p 14:00: the 13:30 entry and 13:59
  close-exit fall in a 30-minute bucket outside grains' 2025-26 day session), the same 544 units as "no new positions
  (Topstep)"; H4 710 = ZC/ZS/ZL 2012-13 (13:29 exits) + LE 165 (08:01 entries 2015-16). The R-B2 cost reproduced on
  the sampled ones. Event-window fills: H1 420 units (grains' 13:15 exits and 2010-12 FOMC 13:15 CT statements
  touching 13:30 fills), H4 730; all sampled flags agreed with my release lookup.
- NOTE 4: not verifiable from the outputs: the exclusion counters other than traded/warm-up (no excluded candidate is
  written to the units files), and the calendars themselves (I used the stores' trade dates and in_scheduled_closure
  flags for the prior trade date, the joint H2 calendar and the R-B1 closure test; every traded unit agreed).

Verdicts: H1 VERIFIED, H2 VERIFIED, H3 VERIFIED, H4 VERIFIED, H5 VERIFIED WITH NOTES (NOTE 1). All five FAIL the
registered pass bar as verdict.json states; N = 478 at the verdict.
