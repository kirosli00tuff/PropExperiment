## 6. Open choices (every decision the lead made on its own, with the reason)

Rulings are in reports/stage_e21_briefs/lead_spec.md ([LEAD] items, section A, section B) and
multiday/README.md (Coder choices, Lead rulings, Freeze review fixes). All were made before any bar
was read (the marker is dated 04:12:28 PDT).

1. **MultidayCoder started in parallel with Step 1**, not after it as the delegation table says (03:18
   vs the readers' 03:33 return). Reason: the five-hour window, and the build reads no data. Reader
   amendments were to go by SendMessage; none changed the code-level spec (A1-A11). A12 came later,
   from the calendar counts.
2. **LE's 2010-06-07..2014-12-14 span (R-S3) is excluded for every test.** LE's first mark is on or
   after 2014-12-15. Reason: the prompt's F1 exclusion, applied to marks, references and S_M alike.
3. **Volatility warm-up: 60 defined daily returns (A3).** MOP gives no rule. T3 needs a defined sigma
   without a 12-month lookback. For T1 and T2 the 12-month lookback binds first.
4. **Daily returns for sigma are undefined across store eras and across a missing previous mark**
   (skipped by the EWMA, counted; FR-6). Reason: same-contract, one-day returns only. This gives no
   look-ahead.
5. **Lookbacks across the 2019-04-30/2019-05-06 store boundary.** They are split as at a splice only
   when the two contracts differ; with the same contract the chain runs through. Reason: never chain
   across two contracts, and never lose a year of signals to the boundary.
6. **The store boundary is a flat month for T1/T2.** The April 2019 rebalance closes everything and the
   May 2019 rebalance reopens. T3's April/May 2019 unit is excluded. Reason: lead_spec section 2 says a
   multi-day hold spanning the boundary is excluded.
7. **Rebalance date.** It is the latest eligible date among the month's last six trade dates. If none
   exists, the position is closed at the first eligible date after month end. Reference dates follow
   the same six-date rule, and roll-blackout dates are allowed for references. Reason: month-end
   semantics under roll blackouts, with calendar-known eligibility.
8. **S_M is calendar-defined:** the roots whose month M-12 lies in the window. A root whose signal or
   sigma is undefined still counts and holds zero. After Q1, the window is the latest of the
   windows-file date, R-S4 and R-S3. Reason: roots rebalance on different dates, so an S_M built from
   realized signals would use other roots' later information.
9. **Holdings are fixed contracts between fills:** n = w / (S_M x V). Reason: this reproduces MOP's
   monthly return exactly between rolls (A5), as a real monthly-rebalanced book would.
10. **The February 2024 rebalance closes every position.** Reason: the next month lies outside the
    window.
11. **T3 sizing.** "Scaled to the hold" is read as a constant 0.40/sigma weight over the hold. S_u
    counts eligible units, and eligibility includes a defined sigma (Q2). Reason: the prompt's
    wording, with verdict invariance shown in FR-5. Both roots enter at the same settlement, so this
    is not look-ahead.
12. **Fill guard.** Rebalance, entry and exit dates must have a fill point outside D9.5a guard
    windows (calendar data). Roll legs move to the nearest usable bar outside them. Reason: release
    times are known in advance.
13. **Limit locks are a counted diagnostic only.** Reason: moving or excluding on the fill bar's own
    high and low would use that bar's prices.
14. **Series dates are calendar-defined, with zeros on flat days.** Reason: no data-dependent series
    length.
15. **The bootstrap uses a fresh default_rng(20261014) per test and circular blocks of 21.** Reason:
    test order cannot change any interval.
16. **HOP's 10% portfolio scaling is not adopted for T2 (A6, a declared deviation).** Reasons: the
    prompt's T2 formula is binding first; the 36-month covariance warm-up costs about two years and
    four roots; a book-level scaler at per-root rebalance dates would need other roots' unknown
    same-month signals.
17. **The T3 parenthetical is corrected (A8):** day -2 is the second-to-last trade date. Reason: the
    papers' four-day window.
18. **T3 days are numbered on NYSE trading days (A12)**, by rule-based NYSE closures plus three
    special closures. Reason: the equity futures calendar books US holidays as early-halt trade dates,
    while the papers count NYSE days. This was found in the calendar-only counts, before any bar.
19. **The trend reader's chained_return "MISMATCH risk" is rejected (A1).** Reason: the function
    splits at every recorded splice (h2.py lines 65-72).
20. **A non-positive price makes a return, lookback or notional undefined, counted (Q3).** Reason:
    CL's April 2020 prices. Fixed-contract P&L is unaffected.
21. **Forced close at an era's last mark (Q4).** The end-of-book check is a counted, non-fatal
    backstop (FR-1), and backstop fill dates are precomputed (FR-9). Reason: no unforeseen data
    condition may STOP the single attempt after its marker (R-B3).
22. **A failed hold (a contract change with no splice, or a missing roll bar) zeroes the order that
    opened it, counted.** Reason: base_rules' unit-exclusion convention. This is a data-presence
    effect, reported (FR-3).
23. **PropEd's F8 table covers every plan allowing overnight holds, each flagged "automation
    UNCONFIRMED" (A11).** Reason: no public page grants automation, and the FAQ marks it not allowed.
24. **F8 method (brief_economics.md):** K_min is the smallest capital at which every root's
    full-signal position is at least one contract, from E.13's C2 per-contract dollar risk. The
    "smallest integer size" is the scale at which the binding root holds one contract. Breaches are
    measured over rolling 21-trade-day EOD windows. In the no-weekend variant, P&L after weekend gaps
    is zeroed and two extra fills are charged per weekend. Reason: the prompt fixes the outputs but
    not the method.
25. **Evidence pages committed:** text, HTML and markdown pages and the fetch logs. Left out: every
    DO_NOT_COMMIT entry (all PropEd pages, whose terms forbid scraping without permission; 10 TOM
    pages) and third-party PDFs and images, whose .txt extractions stay. Reason: site terms and
    copyright; E.13 and E.20 also committed selectively.
26. **The E.21 checks script is E.20's** with this session's scratchpad and an E.21 freeze check
    added.
27. **Commits carry the Co-Authored-By and Claude-Session lines.** Reason: this repository's
    precedent (E.20's commits).
28. **T4 kept H5's trailing-60-grid-date scaling (FR-4, no change at the freeze).** Reason: the prompt
    says "as H5 combines". Consequence, seen after the run (F8): T4's series is dominated by three days
    where H2's first hold dates meet a near-zero trailing sd. T4 is therefore not an informative test
    of the combined book (section 7, item 3).
29. **The verifier was told of the lookback "missing bar" concentration after its own computation**
    (ZC, ZL, ZS, LE, HE runs of about 12 months). Reason: a post-run diagnostic. It changes no rule
    or number; finding in section 5.
