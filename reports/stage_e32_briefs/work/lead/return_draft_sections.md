## 2. Guardrail evidence (start checks, quoted from reports/stage_e32_briefs/checks_start.txt, 2026-10-26 22:41:26 PDT)

```
$ git status --short | wc -l
1457
$ git log --oneline -3
baf24eb docs: V51 (ZM directional signal program) and the Stage E.32 prompt
a6e5582 docs: V50 (E.31 accepted: passive spread capture closed; acct-3 safe to wipe; reviewer model check)
97ce7f0 Stage E.31 volume check and ZM pilot
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m screening.harness_freeze verify --expected 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
preflight OK: 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
$ ledger
37290 ledger/databento_spend.jsonl
42589d7bc02696383cbf5d800ceb922491a4dea90fb2c3d3e2f82da36834c9bb
$ uv run python -m screening.trial_registry status (N)
r008-E23: E23 [...] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY: absent
.env DATABENTO_API_KEY2: absent
.env DATABENTO_API_KEY3: non-empty
```
(The git status list itself, 1,457 untracked lines, is in the start file. Keys were checked by name only.)

Holdout before and after Part 0 (the seal): reports/stage_e32_briefs/seal/holdout_status_before.json and _after.json
are identical; the soy test seal's own status before and after is in soy_status_before.json and soy_status_after.json
(after: all_ok, unlocks 0). Session checks: 02:32 PDT and 07:31 PDT, data.holdout state sealed, unlocks_logged 0.

## 6. Open choices (every choice the lead made where the prompt left room)

Part 0 (seal)
1. Whole files are sealed: stores that span the window boundary are sealed whole; no script reads in-window rows to
   split them.
2. Window rule: raw files by UTC span [2017-04-30T21:00Z, 2020-11-30T22:00Z) (the pre-open hours of 2017-05-01 pull
   in the April 2017 ZS/ZL chunks); stores by inclusive trade dates.
3. The soy seal has its own unlock log and phrase (docs/SOY_TEST_UNLOCK_LOG.md), so a soy unlock never counts as
   holdout 1's.
4. rolls/ symbology JSONs (date to instrument id, no prices) are not sealed; named in the seal document.
5. 206 derived files (95 git-tracked reports, 111 ~/.cache ML caches; seal/derived_unsealed_files.tsv) are not
   sealed: git history keeps the tracked ones readable and both are audit state of registered trials; the guard is
   the protocol's data allowlist (P1.2).
6. The seal stays on 2017-05-01..2020-11-30 although MBO exists only from 2017-05-21: sealing three extra weeks costs
   nothing; the protocol tests 2017-05-22..2020-11-30.
Parts R, M, F (workers)
7. R3 split into R3a (economics) and R3b (microstructure), M5 into M5a (validation) and M5b (power, stability), and
   a follow-up reader R5 (ML evidence and the honest odds): 3 of the prompt's 4 follow-up slots.
8. X1 (the exposure inventory) ran on Sonnet medium before the user's never-Sonnet rule reached the run; it was
   re-verified row by row by X1Verifier-OpusHigh inside the workflow pool (to hold concurrency at 6), and the seal
   document's section 4 was corrected from that verification.
9. The first session's workflow journal could not be resumed in the new session; the three unfinished readers ran
   from a continuation script whose item prompts are byte-identical to the original's.
10. MathReviewer fixes are bracketed notes in the reader files; no reader text was deleted (E.28's practice).
11. The cftc.gov terms check came after 18 reference fetches by R3a, R3b and R4 (the terms allow reference use);
    stated in Part V.5, not hidden.
Part P (protocol)
12. Test bar: the program verdict as coded plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (an
    addition, never a relaxation; dropping it is decision D1 in section 7).
13. Effective test span 2017-05-22..2020-11-30 (890 dates), a 20-date feature burn-in in both windows (T_disc 796,
    T_test 870).
14. The overnight session: no labels or trades in E.33; overnight records enter features only.
15. Four idea families plus a context block; post-USDA drift, the overnight handoff, liquidity regimes, index rolls,
    COT and late-session momentum are not families (power or evidence); their signals survive as exclusions, flags
    or features.
16. Five feature sets (each family with C, and all pooled) x 6 executable labels x 10 grid points = 300.
17. Two model families (regularised logistic primary, LightGBM depth <= 3 secondary); the online wrapper (M4 d
    "maybe") is dropped to keep the grid small and the CV analogue exact.
18. The trade rule is the EV rule with class-conditional training means (no tuned probability threshold).
19. Selection on Topstep market orders, L = 1.0 s; other firms, limit variants and L = 0.3 s are reported for the
    finalists only; a finalist is meant for Topstep (lowest ZM fee, API automation admitted).
20. The program runner's 20-entries-a-date cap is adopted; its 10-minute mean-holding floor is not.
21. Embargo of 20 dates after each evaluation block only (labels end inside their session; features use the past).
22. The power gate uses the one-standard-error lower bound of the discovery Sharpe against the binding test bar,
    at power 0.5.
23. Tier B (for the program verdict's variance and PBO when Tier A has one member) is the two runners-up by Sharpe,
    whatever their gates.
24. The model taken to the test is the 6-fold ensemble (no refit, no new hyperparameter).
25. The release calendar is E.31's sourced CSVs (hashed); a NOPA month without a row gets its rule date.
26. Queue-imbalance features use seasoned depth (orders resting at least 1 s), as a spoofing guard (R2).
27. All thresholds use the literal N (838 if no other stage registers first), recomputed at the registered N.
