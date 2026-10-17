# Stage E.23 rulings on the registration reviews (lead, 2026-10-17 03:32 PDT, before registration and any outcome read)

Reviews: reports/stage_e23_briefs/reg_review.md (RegReviewer-FableXHigh, design and registration: APPROVE WITH FIXES, 0
BLOCKING) and reports/stage_e23_briefs/code_review.md (CodeReviewer-FableXHigh, code: APPROVE WITH FIXES, 0 BLOCKING).
Both reviewed freeze 3fdd98d7...; every fix below went into the rebuilt freeze e0d20d0f... .

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| R-01 future confirmation windows | SHOULD FIX | accepted | prereg section 4: K2-monthend-01's research window SELECTED it, so a later confirmation is W_cf + holdout-2 (about 5.8 y, power about 0.21); H6: W_cf + holdout-2 + research window (about 7.0 y, 0.25) |
| R-02 regressors before 2011-07-29 | SHOULD FIX | accepted | lead_spec section 1: an absent regressor value is zero (E.21's zero-when-flat); the code already did this |
| R-03 which confirmation hurdle | SHOULD FIX | accepted | prereg section 3 and lead_spec section 5: the gate uses b = max(2.0, z(1 - 0.05/S)); power_gate is its S = 1 value; both gate every W_cf row |
| R-04 ZF's ML-panel S_X | NOTE | accepted | lead_spec section R wording |
| R-05 the lenient power gate | NOTE | recorded as an Open choice | none |
| R-06 H6 20-day direction | NOTE | recorded as an Open choice | prereg section 1 sentence |
| R-07 H6 cost margin thin at beta 0.1 | NOTE | recorded | none |
| R-08 exit-side counters on disk 02:46-02:58 | NOTE | no leak relevant to multi-day outcomes; disclosed in the return | none |
| R-09 p_alpha stricter than the prompt | NOTE | kept (conservative, pre-registered) | none |
| C-01 test mode reaches the real stores | SHOULD FIX | accepted | trigger_hold/run.py preconditions refuses the test mode with the real run manifest; test added (tests/test_trigger_hold_run.py) |
| C-04 power table not cross-checked | NOTE | adopted | preconditions checks the power table's events and config sha256 against the frozen files (outside the test mode); dry-checked on the real files: 0 mismatches |
| C-02, C-03, C-05 to C-09 | NOTE | recorded; no change | none |

Checks after the fixes: 94 trigger_hold tests pass; ruff clean; freeze rebuilt e0d20d0fcac4c9861a2c90ff83190b806b1fe945bb36420dcefc1625ecb3c183
(20 inputs, 5 ids, verified); a dry run of the real discovery preconditions with registration stubbed in memory passed
(freeze, config, power hashes, manifest, 8 store preflights; no marker, no output, registry unchanged).
| registry ids | n/a | the registry refused E23-MEZF-h5 (one hyphen only, screening/trial_registry.py _ID); renamed E23-MEZFh5, E23-MEZNh5, E23-MEZBh5, E23-H6NQh5, E23-H6NQh20 at 03:33 PDT (config, prereg, shortlist); power rerun (identical rows), freeze rebuilt 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5, dry run passed | none |
