# Stage E.14 Task 5: test C1's M1 fit and q reproduction; C1 FROZEN, AWAITING FUNDS

Lead: Opus 5.5 xhigh, 2026-10-05. Run 03:29:54-03:29:57 PDT, after the freeze commit 1680982 (03:29:42 PDT) and
before any 2010-2019 byte exists (none was bought). Command (c1_replication/README.md):

```
uv run python -m c1_replication.q_m1 --state ~/.cache/propexp_e14_c1/e12_state_copy \
  --state-manifest reports/stage_e14_c1_e12_state_manifest.json \
  --state-manifest-sha256 8a38eeb150ba7c063e1f7b4292b00efb0bd10549c61e8202fcb926bc8dab1ad9 \
  --out reports/stage_e14_c1_model.json --model-dir ~/.cache/propexp_e14_c1/m1
```
Exit 0; peak memory 641 MB; log reports/stage_e14_briefs/q_m1.log. Output reports/stage_e14_c1_model.json, sha256
**c6075306ddfd70cb22a2b32f8017ae41ba6050778e6cb66568d00b94585421e6**.

## 1. The q reproduction (ruling C4): exact

The persisted out-of-fold splits were reloaded with no fit (a guard refuses any fit call), and E.12's NG family B
rows were rebuilt with Gate 0's own trade rule and statistic. Absolute differences against reports/stage_e12_gate0.json
are 0.0 for every float; counts are equal.

| Pair | Trades | Dates | Rows | Mean gross (ticks) | t_B | p | Mean cost (ticks) | Match |
|---|---|---|---|---|---|---|---|---|
| NG h60 | 518 | 330 | 2,590 | 5.5694980694980805 | 2.5143449337178385 | 0.00620103578191354 | 1.7128756307018143 | exact |
| NG hF | 494 | 283 | 2,473 | 13.92105263157894 | 2.329878707167312 | 0.010259209950479303 | 1.766139250550433 | exact |

## 2. q per horizon (ruling C3: the smallest |r_hat| among NG's Gate 0 trades)

| Horizon | q (repr) | OOF rows at or above q |
|---|---|---|
| h60 | **0.033735277284776724** | 518 (= the trades) |
| hF | **0.0831931045522869** | 494 (= the trades) |

## 3. M1 (rulings C1, C2): one ridge per horizon, lambda 0.1, on E.12's whole training panel

| Horizon | Training rows (81 admissible pairs, pooled) | Features | Payload sha256 (the coefficient hash) | Refit equal |
|---|---|---|---|---|
| h60 | 67,797 | 150 | **9c2d9986ec788a0abcd08186cf249061f91ed0794d3519532ef779de4ccfb9d8** | yes |
| hF | 64,695 | 150 | **153c2bdc25087e0b2f2f236d46fa186e78bb85fa2d50d8702d4c7e5ac4dfbe99** | yes |

Payloads: ~/.cache/propexp_e14_c1/m1/c1_m1_h60.ridge and c1_m1_hF.ridge (1,216 bytes each, mode 0444). Each fit
ran twice with the same payload sha256. feature_cols: 150 names, sha256
af7d43d63b1af935559a745d9708e4657486ef01bc9100e3ddea37aa934ffd1b (E.12's order; ruling C11). ml_route_v2/constants.py
byte-identical (constants fingerprint 013fa5a4...; E.12's v2 freeze verified, 91 files, a647cd06...). The ML
config ledger was read through a temporary copy; the real file's sha256 is unchanged (aacca512...). The E.12
state copy was re-verified after the run (51 files). C10 reference counts (per feature, NG rows applicable in
E.12; counts only) are in the JSON.

## 4. Status: FROZEN, AWAITING FUNDS

C1 is not registered in Stage E.14, so N stays 471 for it. The later session (after the user's acct-2 top-up)
does exactly this, in order, under reports/stage_e14_prereg_C1.md section 11:

1. Verify, by script, before anything else, and record the results in its STATE:
   - every entry of reports/stage_e14_c1_freeze_inputs.json (43 files; the list's sha256
     3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e);
   - the freeze file reports/stage_e14_prereg_C1.md: sha256
     afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b, committed in 1680982 and unchanged in git;
   - the E.12 state copy against reports/stage_e14_c1_e12_state_manifest.json (sha256 8a38eeb1...);
   - reports/stage_e14_c1_model.json (sha256 c6075306...) and both M1 payloads (9c2d9986... and 153c2bdc...);
   - its harness: v10 (fde3a49c...) or a later manifest that differs only in data/config.py's ACCOUNT_2_CAP_USD,
     E14_EXT2010_SESSION_CAP_USD and their comments, and the test assertions that pin those two values
     (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64).
2. Quote fresh: `uv run python -m data.pull_step2 --quote-only --plan ext2010 --account acct-2 --quotes-out <json>`
   ($0.00 lines). Stop if the quote x 1.03 exceeds acct-2's headroom under the raised cap. At Stage E.14's quote
   ($57.742330, x 1.03 = $59.474600; acct-2 spent $231.599730) the cap must be at least $291.074330, so
   ACCOUNT_2_CAP_USD = $291.08 or more (a raise of at least $41.41 on today's $249.67), with
   E14_EXT2010_SESSION_CAP_USD set from the new quote x 1.03 in whole cents.
3. Register: `uv run python -m screening.trial_registry register --test C1 --ids C1-T1 C1-T2 --freeze
   reports/stage_e14_prereg_C1.md --freeze-sha256 afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
   --harness-sha256 <its harness>` (N 471 -> 473 if nothing else registered first).
4. Buy: `uv run python -m data.pull_step2 --buy --plan ext2010 --account acct-2 --harness-sha256 <sha>`; holdout
   status after.
5. Build the six stores (`uv run python -m data.hist_store --plan ext2010 --harness-sha256 <sha>`; counts only),
   write the store-hash and calendar-hash files (c1_replication/README.md step 3).
6. Evaluate once: `uv run python -m c1_replication.evaluate ...` (README step 4), behind its run-once marker
   reports/stage_e14_c1_RUN_ONCE.json; the verdict per the freeze's section 5; then a Fable recomputation.
