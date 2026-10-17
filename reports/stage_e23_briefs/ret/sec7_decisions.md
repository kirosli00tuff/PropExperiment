## 7. Decisions for the user (the lead's recommendation first)

1. **Close "the program's intraday triggers at multi-day holds" as a direction.** Recommendation: yes. The four triggers
   with a moderate or strong multi-day mechanism and owned 2010-2019 data were read once on 7.7 years of data none of them
   had touched, and none came near the bar (largest alpha t 0.55; Holm smallest p 0.31). The month-end book's small raw
   gain is the bonds' own drift (alpha3 about zero). H6's reversal lost money at both holds. No variant (other roots, the
   20-day month-end hold, the opposite H6 direction, T2) should be tested on these windows: any of them would be chosen from
   this read.
2. **What to do with the multi-day data no E.23 computation used (W_cf 2019-05..2024-02, holdout-2).** Recommendation: keep it for a
   hypothesis with a stronger prior than these. A confirmation of E.23's (absent) survivors is moot. Note the structural
   finding: at a true net Sharpe of 0.5, no window the program owns supports a discovery read AND a confirmation read with
   power 0.2 each (W_cf at most 4.8 years gives 0.18; W_ext 7.7 years gives 0.27); W_cf + holdout-2 (about 5.8 years) gives
   about 0.21 and W_cf + holdout-2 + the research window about 0.25. A future multi-day test can confirm on those blocks
   only once, and only for a trigger the research window did not select.
3. **Data for a properly powered multi-day program.** Recommendation: do not buy data for this line now. Pre-2010 CME minute
   data is not on Databento's GLBX.MDP3 (it starts 2010-06), and a daily-settlement source for longer history would be a
   new vendor and a new design question; the trend evidence (E.21) and E22-F1 already cover the multi-day track's best
   candidate.
4. **Carried over:** E22-F1 still waits for the user's choice of a daily settlement source (recommendation from E.22: a
   fresh Databento statistics-schema quote); the AiTrader readout (2026-10-23) remains the next decision point.
5. **Bound the multi-day loader before the next multi-day discovery read** (VerdictVerifier NOTE-2, NOTE-5).
   Recommendation: yes, in the next multi-day stage's prompt. Load the stores only through ctx.last, so a discovery
   read never holds later bars in memory, and have the book write per-unit and per-fill files as E.21 did. This is a
   code change to base_rules/context.py or multiday/, outside any frozen member, so it needs the user's approval in
   that prompt. The E.23 numbers do not depend on it (the spot audit reproduced every value).
