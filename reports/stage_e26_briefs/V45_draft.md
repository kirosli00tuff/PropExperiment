- 2026-10-21 (Stage E.26, recording V44's instructions and E.25's
  corrections): V45. Four records.
  1. Data move (V44, done in E.26): {{MOVE}}
  2. ACCOUNT_3 (V44): data/config.py registers acct-3 (ACCOUNT_3_ID,
     key variable DATABENTO_API_KEY3, cap {{CAP}}, no external ledger),
     selectable the way acct-1 and acct-2 are (require_databento_key,
     SpendGate and its ledger lines, the quote tool); acct-1, acct-2 and
     ACTIVE_ACCOUNT (acct-2) are unchanged. It is a temporary account for
     the E.28 order-book pilot purchase only (one contract, one schema,
     2023-11..2024-02 extended backwards, never 2024-03 or later); the
     user wipes it after E.28 writes "ACCOUNT_3 SAFE TO WIPE". The key
     was given to the planner as a one-time exception the user chose for
     this throwaway account; it is checked by variable name only and never
     printed, copied or logged. {{HARNESS}}
  3. V34 corrected (E.25 R10, DF1): V34's reason for dropping
     noise-area momentum (Zarattini, Aziz and Barbon, "Beat the Market",
     WP 2024, v2025-09) was "unsized"; the authors' FAQ sizes it ($0.09 a
     share net per trade at a $247 average SPY price, about 3.6 bp; futures
     Sharpe S&P 1.32, Nasdaq 1.23, cost unstated). The drop stands on the
     post-publication evidence instead: no independent S&P test after
     publication (2024-05) is distinguishable from zero and the latest are
     negative (Brusco ES, the paper's rule: -0.61 bp a trade net, Sharpe
     -0.07; Paz SPY out of sample: Sharpe 0.39, t 0.54; Delgado
     2025-09..2026-08: Sharpe -0.46); the one positive Nasdaq test is a
     pointer (VigorTas NQ after publication, t 1.37 over 585 days).
  4. V38 amended (E.25 RD2, DF2, DF3, RD4): V38's sentence "no published
     post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round
     trip" now reads: no published post-2015 intraday effect on the 17
     roots exceeds 1.5 x the D8 round trip, except three working-paper
     effects whose samples run past 2015, none with a significant
     post-2015 estimate: the pre-refunding-announcement ZN gain (Wang and
     Zhao 2025, cash, +12.62 bp, t 3.32), the pre-FOMC ZN drift (Pan and
     Peng 2026, futures, +7.26 bp, t 2.82, 2004-01..2025-06) and the ES
     3rd-Friday reversal (Baltussen, Terstegge and Whelan, -12.89 bp, t
     -2.40, 2003-2021; 2015-23 not significant alone). Each gives 3 to 15
     events in the research window (power 0.11 to 0.22 at the published
     sizes), so none can be tested with adequate power on owned data. The
     closure of the intraday program (V38) stays in place. N stays 538.
