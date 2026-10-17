**Window (user-approved, not the lead's).** The user paused the stage at 07:57 PDT and approved a new window (planner
message 2026-10-16 18:27 PDT): no confirmation read after 02:00 PDT on 2026-10-17, the return by 03:00 PDT; this replaced the
prompt's 06:30/07:30 times and nothing else. Logged here as a user-approved window change. The stage itself stopped at 02:43
PDT on a usage limit with no confirmation read started; after the laptop restart every earlier worker was treated as gone and
the disk state re-verified (section 2).

**Part A (reports/stage_e22_briefs/partA_rulings.md, written and hashed into the lists before any read):**
1. R-E22-A1: each cluster's single run covers every runnable frozen trial, Tier A and Tier B (E.5's K4 precedent), so V14 (c)
   and L-E5-3 have their series; OC-H-excluded trials listed, not run, not covered. `--all` still executes them (pmfix MGC,
   K3's three coverage exclusions); their records are present and not used (VerdictVerifier-K5 note).
2. R-E22-A2: K6 confirmed despite V18 ("not planned"), since V39 and the prompt name K6-limitcont-01.
3. R-E22-A3: owned data only (step 2 stores of E.5 and E.12; MES's Stage D store); MNQ step 2 and BTC not owned.
4. R-E22-A4: GC bars as MGC's price path for every MGC-vehicle trial (K5's six, K8's flight H30 and HEOD), MGC's costs, tick
   value and q_c: MGC's own window is empty, so D4's power check fails; U8 met by V39's delegation; declared before any read
   (reports/stage_e22_price_paths.json, pinned in v13).
5. R-E22-A5: NQ bars as MNQ's price path (MNQ's history not owned, so its owned supply is 0). Declared, but not exercised: the
   only MNQ trial (wkndbtc) is not run. ListReviewer preferred the strict reading (no NQ path; wkndbtc "untestable on owned
   data, missing MNQ"); verdict-neutral either way. Left in v13's declaration (see decision 6).
6. R-E22-A6 (revised after the list review): wkndbtc "inconclusive by design" only (MBT window 34 days < n_b 43; BTC not
   owned, not bought), declared not run by a reason-only entry; an earlier "untestable (missing MBT)" declaration was withdrawn
   before any commit.
7. R-E22-A7, A8: MES from its Stage D store at S = 2020-02-03; D4's start rule for every other root, run on its owned store
   (GC and NQ on their own research volumes).
8. R-E22-A9: by-design trials are never run (applied in the list builder after list-review N-1).
9. R-E22-A10: Holm K = 5 (K3, K4, K5, K6, K8), not V14 (b)'s 9, since every cluster and the ML route have now been screened;
   the K = 9 Holm reported descriptively; family-wise error with K4 at 0.0056 is at most 0.0456.
10. R-E22-A11: N = 533 for DSR (532 + E22-F1, registered at 02:12 before the lists at 02:20), the conservative value.
11. R-E22-A12: operative eps_X (min of translated and funnel), as E.5.
12. R-E22-A13: a Tier A trial with no record enters Holm at p = 1 with the screened family size.
13. R-E22-A14: K8's DSR variance over Tier A when two series exist, else every run trial (here the three run trials).
14. R-E22-A15: open issues carried as frozen (K3's 14 FX dates, July 3 dates, K6 limit tables and D9.7 proxy, wkndbtc regime);
    tick history over the confirmation window taken from the step 2 bar reports (off_tick_prices 0).
15. R-E22-A16: K6-limitcont-01 LE (power undefined, 0 research trips) run and covered; a zero-trip confirmation outcome reads
    inconclusive and costs K6 its statement; accepted before the read (and it happened).

**Harness and process:**
16. Harness v13 built rather than an E.5-style stop: the prompt's guardrail anticipated it; Fable-reviewed and committed
    (e40ca85) before any read. Review SHOULD FIX items fixed in code (not procedure); residual R-1 covered by a pre-run script.
17. A speculative working-tree manifest (W1, 8cd39432) was used to build K8's start rule and a first power run during the
    review; the power was re-run under committed v13 (identical); K8's start-rule file was kept (W1 -> v13 changed only the
    runner and verdict modules and tests; list-review N-2).
18. K3 and K6 start rules built under v12 before any harness edit (the loader does not check a file's harness).
19. The four earlier freezes broken by v13 (E.16, E.18, E.20 H6, E.20 search) and the h6 test were left as they are
    (frozen records of completed stages).
20. One Fable verifier per cluster, started as each verdict landed (the prompt planned one VerdictVerifier).
21. Confirmation order K5, K8, K3, K6, one at a time, detached with setsid so a dropped shell could not consume a marker.
22. The end suite ran at 02:20 on the final code and is the one quoted; a second run after the confirmations (18:59:54) was
    stopped at 81% (19:14:51) because free memory fell to 1.5 GB (stability over speed); no tested code changed after 2a2bdd8.

**Part B (reports/stage_e22_briefs/lead_spec_B.md S1-S8):**
23. Universe: 12 micros on E.21's owned paths; SIL (no owned path), MES (no 2010-2024 path) and MHG, M6A, M6B, MCD, MJY, MZW,
    MZM (their only owned paths are Part A confirmation-window data E.21 never read) not modelled.
24. Yield micros in the study: a proxy from ZT/ZN/ZB with declared modified durations 1.9/6.5/15.0 (UNSOURCED); in the
    forward test they trade their own yield-quoted contracts.
25. Sizing vol as price-difference vol (sigma(dP)/P), so the yield instruments are well defined.
26. B-R1: Carver's production forecast scalars (5.95/4.10/2.79/1.91), not the book set (shown as a sensitivity).
27. B-R2 to B-R5: the blended vol as the EWMAC denominator; the rounded-and-buffered baseline as "simple"; the November 2021
    post's greedy parameters unchanged (250, 0.0125, not rescaled to 20%); no end-of-sample look-ahead.
28. B-R6: the 0.5 correlation shrink in the main greedy rows (the post states shrinking without a value).
29. B-R7: E22-F1's rounding changed from the greedy (draft 1) to simple rounding after the design study, before the freeze.
30. D8 extension costs for MNG, M6E, 2YY, 10Y, 30Y, MZC, MZS, MZL (commission plus one tick; the $1.92 round-turn commission for
    yields and grains UNSOURCED); 2026 IBKR margins applied to historical positions.
31. E22-F1: frozen by a separate freeze commit (2a2bdd8, E.21's precedent) before registration; registered under test group
    "E22" with id E22-F1 because the registry refuses the "E22F1" group form the frozen text's example command used.
32. E22-F1 text decisions: start = the first ledger record; warm-up = the source's own back history (no splice); a missing
    weekday counts as 0; pre-clock roll correction allowed; stuck roll -> abandoned; abandonment reported, never restarted
    under the same ID.
33. The study's cache (daily price series) and per-book series are not committed (derived market data; size).
