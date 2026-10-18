## 7. Decisions for the user (each with a recommendation)

1. **Whether to test C1 (noise-area intraday momentum on MNQ), and how.** It is the only frequent candidate that
   clears the hurdle on published numbers and duplicates no trial, but no independent S&P test after
   publication is distinguishable from zero (the latest are negative), the one positive Nasdaq test is a pointer
   (t 1.37), its power on the window is 0.35 at the published size, third-party results already
   cover the research window (so a read of it would not be blind), and its drawdown at 1 MNQ exceeds the 50K and
   100K trailing limits. **Recommendation:** do not register a research-window read. If the user wants one more
   test, register a frozen FORWARD paper record on MNQ (a new registration, N + 1, using the forward plumbing E.24
   builds), with its length and bar fixed from the published Sharpe before day one, and expect it to fail. No
   Combine purchase follows from it unless it passes (V33 stands).
2. **The 3rd-Friday spike (C2/C3) and the Treasury drifts (C4/C5).** Each clears the hurdle on published numbers
   but gives 3-15 events in the research window (power 0.11-0.22 at the published sizes, 0.06-0.17 at the post-2015
   sizes), two shrank after 2015 or between drafts, and
   C4's effect is conditional on a nearby FOMC. **Recommendation:** register nothing now. If the user wants one of
   them kept alive, the cheapest honest option is a forward event log (a few events a year) rather than a test
   that cannot reach power; adding W_cf's post-sample events (V41) lifts C2 only to about 0.25.
3. **Passive execution (Groups A and B).** Group A is empty; B1 would need a Databento purchase (trades and mbp-1)
   and its price saving is under 1% of the published move, with trade-through fills selecting adverse days.
   **Recommendation:** buy nothing; keep the C6 closure; request no quote.
4. **V38's wording.** The re-dig found three working-paper effects above 1.5 x the D8 round trip on the program's
   roots whose samples run past 2015 (pre-refunding ZN, cash returns; pre-FOMC ZN, futures; the ES 3rd-Friday
   reversal), none with a significant post-2015 estimate, each rare and low-powered.
   **Recommendation:** amend V38's sentence to name them as exceptions that cannot be tested with adequate power on
   owned data, leaving the closure of the intraday program in place.
5. **V34's reason for dropping noise-area momentum.** The "unsized" basis is weakened (the authors' FAQ sizes it);
   the post-publication evidence now closes it on the S&P side on other grounds. **Recommendation:** record the
   correction in docs/DECISIONS.md with the post-publication evidence.
6. **Topstep's rules record.** Topstep's Tier 1 news window (2026-10-10..16) overturns E.19's R040 ("news flatten
   not required"). **Recommendation:** refresh reports/stage_e19_rules.json at the next prop-economics stage, before
   any Combine modelling.
7. **Direction.** **Recommendation:** keep the intraday prop program closed (V38); the AiTrader readout
   (2026-10-23) and E.24's forward plumbing remain the next decision points. Prop outcome data (Topstep's 2025
   funnel: about a third of funded individuals paid at least once) and the evidence above give no reason to buy a
   Combine.
