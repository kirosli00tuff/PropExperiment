## 6. Open choices (every decision the lead made on its own, with the reason)

1. **A trigger is one frozen member trial** (a member on one root, or one frozen rule test such as E20H6-T1), as the
   program counted trials; the trend regression is then the same root's T1 and T2.
2. **Power convention**: true net Sharpe 0.5 on the book's daily series, zeros on flat days, E[t] = 0.5 x sqrt(years): the
   program's convention (E.21 prereg section 3, E.22 F1). Under it power depends on window length, not on event count.
3. **Power gate at the per-test hurdle alpha t >= 2.0** (the lenient reading of "the power to reach the bar"; R-05).
   Holm's step-1 power at K = 5 (0.17 on W_ext) is reported beside it. Under the strict reading every trigger-hold would be
   inconclusive by design on both windows and nothing would have been read. The discovery read therefore spent W_ext's
   multi-day outcome for these five trigger-holds in a read that could not produce a PASS (every confirmation row was
   gated before the read).
4. **Discovery on W_ext (2011-07-27..2019-04-30), confirmation declared on W_cf (2019-05-06..2024-02-29) and gated.** The
   prompt's ideal discovery window (the data each trigger was screened on) is the research window, which P2.4 bars. W_cf
   (at most 4.82 years) cannot reach power 0.2 in any role; W_ext (7.7 years on the long roots) can. The reverse order
   would have read nothing. This order keeps every trigger's multi-day outcome on 2019-05..2024-02 uncomputed for a
   later registered confirmation (the frozen E.21 loader held the W_cf rows in memory during discovery; nothing was
   computed from them: NOTE-2).
5. **W_ext starts at 2011-07-27**, the first date of the E.21 T1/T2 series, so both regressors are defined; a book's
   series starts at its first unit (amendment 02:36); a regressor value absent on a book date (first per-root values
   2011-07-29) is zero, E.21's own convention (R-02).
6. **Shortlist rule**: moderate or strong stated mechanism; data owned on both windows; multi-day outcome never read; not
   a duplicate of a shortlisted mechanism on the same root; a fixed-side book that would be in the market on almost every
   day is a buy-and-hold, not a trigger test (refined at 03:10 from the power table's calendar facts; H6's books, in the
   market 91-94% of days with a side that follows the trigger, stay trigger tests).
7. **K2-aucpre-01 and K2-aucpost-01 dropped**: their 5-day post-auction long from the auction day's settlement is the long
   leg of E16-H3, already read on 2010-07..2024-02 (E.17, FAIL); the two members are one bet (M6).
8. **K4-ngpre-01 dropped and K2-monthend-01's 20-day hold not registered**: weekly events (ngpre) or N-1 and N each month
   with a 20-day hold keep a fixed-side book in the market on almost every day. "Two holds each" read as the default.
9. **K2-monthend-01 on ZF, ZN and ZB**: one root per futures tenor in Hartley-Schwarz Table 8 (5y, 10y, 30y); ZT has only a
   cash 2y figure; TN and UB have no row (TN is also too short on W_ext).
10. **E20H6-T1 only** (T2 is a magnitude-filtered variant; T3 excluded: GEX from 2011-05 and terms cleared for one test),
    and H6 rather than CP1, E16-H1 or E16-H4 on NQ: the same late-day pressure and reversal mechanism on the same root.
11. **Directions**: K2-monthend-01 m = +1 (the member's long side; M7); E20H6-T1 m = -1 (reversal; M4). The 20-day H6 hold
    keeps the mechanism's direction although the 20-day evidence is disputed (R-06).
12. **FOMC triggers dropped as weak** (M2: K5-fomc-01 and K2-fomcpost-01 weak with disagreement; K2-predrift-01
    intraday-only) although the prompt names post-FOMC drift; **K8-flight-01 (moderate) and K1-vxnband-01 (moderate)
    unreadable** for data (the MES leg and VXN are not owned for 2010-2019; W_cf alone is gated).
13. **TN, RTY, HE and LE excluded** for short W_ext stores (power below 0.2 on both windows), which removed K6-limitcont-01.
14. **Entry rule**: the first settlement mark strictly after the trigger's decision time (the same day for both triggers);
    **position**: clip(sum of units, -1, +1), changing only when that value changes, sized 0.40 / (sigma x notional) at the
    change date and not resized while held.
15. **Descriptive alpha3** (adding the root's own buy-and-hold return) and the in-market fraction, because the month-end
    book is long-only and E.21's regressors are signed trend returns, not the asset's drift.
16. **Two coders** (BookCoder for the engine, TriggerCoder for the event extraction) in parallel instead of one BookCoder
    (V37: independent items); **two Fable reviewers** with distinct lenses (design and registration; code).
17. **BookCoder's thirteen conservative choices accepted** (lead_spec section R): an ineligible exit date excludes the unit
    (E.21 T3's rule; a calendar and bar-existence filter, never a price); the T3 entry eligibility in full, so Treasury
    roll blackouts at quarter month-ends remove about a third of the month-end units; stress = commission + 2 x (base -
    commission); discovery context ends 2019-04-30; Holm counts every registered trigger-hold; ties by id.
18. **TriggerCoder's eight readings accepted** (trigger ids as freeze labels; an event is an accepted entry that filled; D9.7
    price limits not applied on W_ext, where no table exists and W_cf shows no H6 refusal; H6's lead-in clamp not applied
    on W_ext).
19. **s_x null** for every row (W_cf from 2019-05-06); E.12's ML-panel S_X for ZF is not this trigger's (R-04).
20. **Registry ids renamed** E23-MEZFh5 etc. when the registry refused a second hyphen (03:33; nothing written by the
    refusal); power rerun with identical rows; freeze rebuilt.
21. **The confirmation step was run once with zero survivors** (03:35): it wrote its marker and recorded that nothing was
    read, so the order of P2.6 is on record.
22. **C-04 guard added** beyond the SHOULD FIX (the power table's events and config sha256 must equal the frozen files').
23. **Cost feasibility on approximate notionals** (typical prices; the H6 gross is the reader's arithmetic, not a published
    figure; R-07).
24. **Mechanism readers' deadline 03:45 PDT** and 60 searches each; all returned by 02:33.
25. **VerdictVerifier's NOTE-2 (W_cf rows in memory during discovery) was ruled a wording correction**, not a re-read or
    a code change. A second discovery read is barred (run-once), and the frozen loader is not edited after the reads. The
    return says "computed nothing from any bar dated after 2019-04-30"; decision 5 carries the loader bound forward.
26. **The `git status --short` quotes in section 2 omit the untracked (`??`) lines**: 1,029 at the start and 1,288 at the
    end. These are earlier stages' untracked pages plus this stage's new files before the final commit. Every other line is
    verbatim, and the full text is in reports/stage_e23_briefs/start_checks.txt and end_checks.txt.
27. **The end checks are the 05:21:40 run**, taken after both reads and before the end suite. A final rerun just before
    the commit (end_checks_final.txt) is quoted as its difference from the 05:21:40 run.
28. **After the stall, the verifier was resumed by message, not re-spawned.** Its file-based recomputation (343 rows)
    and spot_audit.py were already on disk, and only the run and the verdict line were missing.
