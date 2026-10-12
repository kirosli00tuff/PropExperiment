## 5. Verification (each Fable finding, the ruling and the fix; full text in the review files, rulings in reports/stage_e20_rulings.md)

| Review | Verdict | Findings | Rulings (section) |
|---|---|---|---|
| H6Reviewer-FableXHigh (reports/stage_e20_review_h6.md) | APPROVE WITH FIXES | 0 BLOCKING, 3 SHOULD FIX, 7 NOTE | 2 |
| VerdictVerifier-FableXHigh, H6 (reports/stage_e20_review.md "H6 verification") | VERIFIED WITH NOTES | 0 BLOCKING, 1 SHOULD FIX, 5 NOTE | 3 |
| PlanReviewer-FableXHigh (reports/stage_e20_review_plan.md) | BLOCK, then APPROVE WITH FIXES on recheck | 1 BLOCKING, 6 SHOULD FIX, 8 NOTE; recheck +1 SHOULD FIX, 2 NOTE | 4, 4b |
| SearchReviewer-FableXHigh (reports/stage_e20_review_search_code.md) | APPROVE WITH FIXES | 0 BLOCKING, 1 SHOULD FIX, 8 NOTE | 6 |
| ScreenVerifier-FableXHigh (reports/stage_e20_review.md "Search screen verification") | VERIFIED | 0 BLOCKING, 0 SHOULD FIX, 3 NOTE | 8 |

Every BLOCKING and SHOULD FIX finding, with its fix:
- H6R-1 (code): a post-marker catch-all writes every test STOPPED with the traceback and the result file; test added.
- H6R-2 (text): the prereg header discloses the GEX sign count; section 6 records who, when and what was read.
- H6R-3 (text): section 7a adds the prior close after an early-close day, the roll difference, shortened days in T2.
- H6V-2 (descriptive): breach dates are the result's mll_liquidation_fill_dates (T1 2023-11-30, T2 2021-10-07); reading note.
- PR-1 (BLOCKING): the 2010-2019 swap table (backward_swap_table.md; plan 10.1) and the Step 6 sentinel dry check before the
  freeze; no feature NO-SOURCE; the dry check passed with no feature dropped.
- PR-2: k2_fomc_mto dropped (13:00 CT event minute wrong before 2013-03-20).
- PR-3: above-4.0 Sharpe fails the screen (reading (a)), fixed before the fit.
- PR-4: the composed builder re-applies the frozen checks by name (the grid assertion later limited to synthetic worlds per
  V2.2b, rulings 7).
- PR-5: B1's fixed-D construction declared, with E.16 F-07's single-price-bar diagnostic.
- PR-6: ruin not computed on a fail; on a pass, an engine adapter hashed before B1's registration.
- PR-7: acceptance rule (c) written as applied; RTY's ground (d) withdrawn.
- PR-16: the daily cost fallback's reach quantified (25.0% of entries for 15 vehicles; grains and livestock exits 13-18%).
- SC-1: check --world before the registration.
The verifier of H6 reproduced every verdict number independently (bar-level reconstruction, no h6_rod import): all
trades matched to the cent except the two MLL liquidations, which explain the small t differences.
