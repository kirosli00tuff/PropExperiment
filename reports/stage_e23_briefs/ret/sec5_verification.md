## 5. Verification (each Fable finding, the ruling and the fix)

Three Fable xhigh workers checked this stage. None of them produced any of the work it checked.

- **RegReviewer** (design and registration) and **CodeReviewer** (trigger_hold/ line by line) worked before any read, on freeze 3fdd98d7... . Both returned APPROVE WITH FIXES with 0 BLOCKING.
- Every fix went into the rebuilt freeze e0d20d0f... . After the registry id rename it became 24dcf4dd..., which is the freeze the reads ran on (rulings: reports/stage_e23_briefs/review_rulings.md).
- **VerdictVerifier** worked after both reads. It used its own code and imported no project module. Its verdict was **VERIFIED WITH NOTES, no BLOCKING** (reports/stage_e23_briefs/verify/verdict_verify.md, set 07:24 PDT).

### 5.1 Registration review (reports/stage_e23_briefs/reg_review.md)
| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| R-01 the prereg's future confirmation window used the research window, which SELECTED K2-monthend-01 | SHOULD FIX | accepted | prereg section 4. K2: a later confirmation is W_cf + holdout-2 (about 5.8 y, power about 0.21). H6: W_cf + holdout-2 + the research window (about 7.0 y, 0.25) |
| R-02 per-root regressors start 2011-07-29; 1-2 book dates had no value, and the frozen text did not say how they are handled | SHOULD FIX | accepted | lead_spec section 1 and prereg section 3: an absent regressor value is zero (E.21's zero-when-flat). The code already did this |
| R-03 two definitions of the power gate | SHOULD FIX | accepted | prereg section 3: the confirmation gate uses b = max(2.0, z(1 - 0.05/S)); every W_cf row fails it at 2.0 already |
| R-04 E.12's ML-panel S_X for ZF | NOTE | accepted | lead_spec section R wording (a panel start, not this trigger's S_X) |
| R-05 the lenient power gate (t >= 2.0; at the Holm step-1 hurdle W_ext power is 0.17) | NOTE | Open choice 3 | none |
| R-06 the H6 20-day direction is not fixed by the mechanism | NOTE | Open choice 11 | prereg section 1 sentence |
| R-07 the H6 cost margin is thin at beta 0.1 (multiple 1.3-2.9) | NOTE | recorded | none |
| R-08 exit-side counters on disk 02:46-02:58 | NOTE | no leak relevant to multi-day outcomes; residue recorded in section 3.4 | none |
| R-09 p_alpha is stricter than the prompt (max of plain and NW p) | NOTE | kept (conservative, pre-registered) | none |

### 5.2 Code review (reports/stage_e23_briefs/code_review.md)
| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| C-01 the test mode with `--input-paths '{}'` reached the real stores without the real marker | SHOULD FIX | accepted | `preconditions` refuses the test mode with the real run manifest; test added (tests/test_trigger_hold_run.py::test_the_test_mode_refuses_the_real_run_manifest) |
| C-02 window membership is tested on d0, not d_e | NOTE | recorded | none. d_e = d0 for every unit (verified on all 3,846), so no number changes |
| C-03 a PASS is impossible on this freeze (every W_cf row gated) | NOTE | recorded | none. The prereg said so before the discovery read (section 4 power table); Open choice 3 |
| C-04 the power table's events and config hashes were not cross-checked | NOTE | adopted | `preconditions` compares them with the frozen files outside the test mode |
| C-05 regressors are projected on the book's dates (a few roll dates per root) | NOTE | recorded | none. This cannot create alpha |
| C-06 exit eligibility uses calendar and bar existence at d_x | NOTE | recorded | none. It is not a price condition (lead ruling R1, as E.21 T3) |
| C-07 the member code is pinned indirectly through the events files' recorded hashes | NOTE | recorded | none |
| C-08 stress rounding is conservative by at most 1 cent per side | NOTE | recorded | none |
| C-09 the TriggerCoder counters incident | NOTE | as R-08 | none |
| (lead) the registry refused ids with two hyphens | n/a | ids renamed (E23-MEZFh5 etc.), power rerun with identical rows, freeze rebuilt 24dcf4dd..., dry run passed | none |

### 5.3 Verdict verification (reports/stage_e23_briefs/verify/verdict_verify.md, tables.md, recompute_file_based.json, spot_audit.json)

**File-based recomputation: 343 rows compared, 339 within 1e-9 relative, 4 DSR rows at 2-3e-9.** It covered:
- n, mean, sd, net Sharpe, raw t, NW t, and the OLS alpha on v_T1 and v_T2 with its Bartlett HAC t, plain t, p_alpha, R^2, betas and correlations, for all five trigger-holds in both cases;
- alpha3 and the in-market fraction;
- Holm (nothing rejected; smallest p_alpha 0.3095 against 0.01) and the survivor rule (none: largest alpha t_NW 0.552, largest Sharpe 0.207);
- DSR at N 538 (all below 0.001) and CSCV PBO 0.428571 (30/70);
- the W_cf gate (below 0.2 at every S from 1 to 4), N 533 -> 538, the freeze and registry hashes (108 frozen files match), and the marker order (each marker written before its computation).

**Spot audit** (re-simulation from the ext2010 stores, 07:22:25-07:22:35 PDT, nice 10, 2010-07-01..2019-04-30 only):
- Every daily base and stress series value matched (max |diff| 0.0 on 9,668 dates). So did unit counts by reason, fills, roll pairs, gross, costs, net and alpha3.
- Each unit enters at the first mark after its decision (d_e = d0 for all 3,846 units) and exits h marks later.
- Size is 0.40/(sigma x notional), with sigma taken strictly before entry.
- Costs per side are D8 base; stress = commission + 2 x slippage. Round trips are $10.14 / $18.26 / $34.04 / $2.10, equal to the prereg's.
- The entry day carries only the fill cost: no trigger-day intraday P&L.

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| NOTE-1 four DSR values differ at 2-3e-9 relative (the run's Acklam normal quantile) | NOTE | accepted | none (descriptive; every DSR < 0.001) |
| NOTE-2 the frozen E.21 loader (base_rules/context.py -> store.load_product) concatenates both eras, so the step2 store's W_cf rows (2019-05-06..2024-02-29) were in memory during the discovery read. Nothing was computed from them; only the boundary-splice contract comparison and the limit-lock rule construction touch that frame, and neither yields a value in any statistic | NOTE | accepted. The return says "computed nothing from any bar dated after 2019-04-30" (sections 3.4, 3.6, Open choice 4), not "read nothing". The freeze is not changed after the reads | for a later stage: bound the loader by ctx.last before any further discovery on W_ext (decision 5) |
| NOTE-3 the program's CSCV helper drops the last 4 of 1,940 dates (n // 8 blocks); equal blocks give PBO 0.4857 | NOTE | recorded; the program's helper is kept | none (descriptive; both < 0.5) |
| NOTE-4 the calendar-only power table differs from the realized books by up to 6 dates and 2 units | NOTE | recorded | none (realized power 0.2685-0.2694; no gate flag changes) |
| NOTE-5 the discovery output has no per-unit or per-fill records; the audit had to re-simulate | NOTE | accepted for later stages | none now (run-once outputs are not rewritten); later books write unit and fill files, as E.21 did |
| NOTE-6 the prereg says K2 decides "at 07:20 CT"; the events carry 07:21 CT (the 07:20 bar's close) | NOTE | recorded; the frozen prereg is not edited | none (no unit changes) |
| NOTE-7 registry line r008 was in the working copy, not committed | NOTE | accepted | committed in the final commit with the stage's results |
