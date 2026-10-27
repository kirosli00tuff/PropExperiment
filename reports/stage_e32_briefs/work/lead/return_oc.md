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
21. Embargo of 21 dates after each evaluation block only (labels end inside their session; features use the past;
    21 covers the 20-date SDs of F1.7 and F4.7, which reach the 13:15 mid of the 21st date back; ProtocolReview
    LE-4, AR-5).
22. The power gate uses the one-standard-error lower bound of the discovery Sharpe against the binding test bar,
    at power 0.5.
23. Tier B (for the program verdict's variance and PBO when Tier A has one member) is the next two configurations
    of the Tier A walk with correlation <= 0.70 to every one taken, gates ignored; failed or constant series are
    skipped (ProtocolReview DO-5, FixVerifier R-W2-1).
24. The model taken to the test is the 6-fold ensemble (no refit, no new hyperparameter).
25. The release calendar is E.31's sourced CSVs (hashed); a NOPA month without a row gets its rule date.
26. Queue-imbalance features use seasoned depth (orders resting at least 1 s), as a spoofing guard (R2).
27. All thresholds use the literal N = trial_registry.current_n() right after E.33's one registration of the 300
    IDs (838 if no other stage registers first), recomputed by p7_final.py at that N (ProtocolReview DO-4, AR-3).
Part P after the ProtocolReviewer (v0.3) and the FixVerifier re-check (v0.4)
28. Entry decisions use only data with ts_recv <= t; the locked-book rule is a row rule; an entry or exit whose side
    is empty at t + L fills at the first later valid book update (the P3.2 fallback), and a TB trade's barrier
    reference is the mid at that fill update (ProtocolReview LE-1, FixVerifier R-W1-2).
29. Definitions (limit prices) are taken as of ts_recv <= 08:30 CT on D; a missing or undefined limit skips the
    limit rule for that date (ProtocolReview LE-2, FE-8; FixVerifier R-W4-8, R-W1-11).
30. The release calendar is parsed by a fixed rule with asserted counts (39 WASDE, 39 Crop Production, 4 Annual, 13
    Grain Stocks, 3 Prospective Plantings, 3 Acreage, 37 NOPA rows plus 2 rule dates); a NOPA month without a row
    gets its rule date (ProtocolReview LE-3, DO-8; FixVerifier R-W1-5). (Replaces 25's wording.)
31. Conservative readings by E.33 go into reports/stage_e33_protocol_readings.md, hashed in the pipeline freeze and
    quoted in the C1 note; none after C1 (ProtocolReview DO-1, FixVerifier R-W2-2).
32. Registry IDs E33-<set><label><grid> (e.g. E33-S5F15L010A) to match trial_registry's pattern; one register call
    (ProtocolReview DO-3, FE-1).
33. Synthetic proofs at a declared subset scale (S5 x {FH15, TB30} x 10 grid points, 20 null and 20 planted seeds,
    4,800 fits) instead of 40 full searches (72,000 fits); the plant is sized at FH15 by the P3.5 oracle with true
    class probabilities (ProtocolReview FE-2, FE-7, DO-21; FixVerifier R-W3-4, lead's choice of FH15).
34. LT7 (simulator causality) runs on the fold models of the seed-1 null proof search, applied to the real streams
    before any real-outcome fit, and again on Tier A and Tier B after the test list is hashed (FixVerifier R-W3-6,
    lead's choice).
35. An interrupted fold is rerun once from the DONE markers; a second interruption fails the configuration
    (FixVerifier R-W3-7, lead's choice over failing at once).
36. Threads: processes x threads <= 8; every long job at nice 10 and resumable (ProtocolReview FE-3, FixVerifier
    R-W4-3, R-W4-4).
37. No package is added after the pipeline freeze; anything needing statsmodels is written in numpy with tests or
    reported as not done; SFI only if time remains (ProtocolReview FE-6).
38. E.33's deadlines are quoted by value from its prompt as amended at 08:16 (search cut 07:00 PDT 2026-10-28, work
    stop 08:00, return 08:45, nothing after 09:00); the prompt's current times govern; the cut unit is a whole
    feature set and the report cut order is declared (ProtocolReview DO-19, FE-11; FixVerifier R-W3-1, R-W4-1).
39. G3 and the protocol-added test DSR use the program's sign "> 0.95"; b_test is the unrounded 0.164882; ranking
    rounds SR_d with Python's round() (FixVerifier R-W1-12, R-W1-4, R-W2-4).
40. The P6.4 (iii) queue-model variant uses a port of E.31's fill logic written by E.33 (F 6.2 classes E.31's code
    as not reusable), reported as not done if not ready; P6.3-P6.5 items are never a stop (FixVerifier FE-6,
    R-W4-2).
41. E.31's measured outputs (pilot/runs/, incl. runs/measure31/) are refused in code; X1_exposure.md, X1_verify.md
    and the Table C appendix are closed to E.33's workers as whole files (ProtocolReview LE-7, FE-5; FixVerifier
    R-W1-8).
Process
42. The fix re-check ran as four split FixVerifier workers (by item and section) instead of one, and the v0.4 diff
    spot-check as two; same model (Fable xhigh) and effort, less context per step.
43. All 25 NOTE items of the re-check were applied with the SHOULD FIX items (the prompt requires only BLOCKING and
    SHOULD FIX).
44. The full pytest ran during the re-check (no code changed after Part 0); its one failure predates E.32 and is not
    fixed here (decision D7).
45. The MathReviewer NOTE items were not applied to the reader files (listed in the review files).
