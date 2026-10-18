# Stage E.24 lead rulings on the Fable reviews (lead, Opus 5.5 xhigh; 2026-10-18 11:5x PDT)

Rule: every BLOCKING and SHOULD FIX is fixed before any freeze (prompt A2, C4); NOTEs are fixed when cheap and safe or
listed. Text changes to reports/stage_e24_prereg_F2.md are the lead's; code changes go to the wave 3 fixers.

## A2 loader (loader_review.md; recheck loader_recheck.md: APPROVE, 0 B, 0 SF, 3 N)
- SF-1 null trade_date refused as the frozen path does: FIXED (LoaderFixer, wave 2); recheck OK.
- SF-2 bound mandatory in read_root_books: FIXED (wave 2); recheck OK.
- NOTE-4..11 and the recheck's 3 NOTEs: listed, not changed (the recheck's wiring note: a future multi-day runner
  must build its context with mdio.bounded.bound_context, not only call check_bounded; carried to the return).

## C4b registration (reg_review.md: BLOCK, 2 B, 8 SF, 14 N) -- text revised 11:50-11:55 PDT
- B1 silent share drift when the source's previous close differs: text: prev = the last recorded session,
  rawclose(prev) = the recorded close; flag prev_close_mismatch:SYM above 1e-6 relative; code: runner computes r and
  the share factor from the recorded close and the session's actions (F2Fixer2).
- B2 late-action key collision: text: key = symbol, type, ex_date and amount or ratio (or the source's id); same
  symbol/type/ex_date with different amounts are two actions; code (F2Fixer2).
- S1 step 5 and shorts: text: step 5 scales every new-target position, longs and shorts, by max(0, B - C)/gross,
  longs floored to 0.001, shorts toward zero to whole shares; gross <= B unless carried positions alone exceed it.
- S2 (Q24) late distribution on a split session: text: q_ex x k x amount, k = that session's split ratios.
- S3 cash term of an ETF without a bar: text reworded (N_i r_i on return; -N_i r_c each session BIL has a bar).
- S4 carried positions in step 2: text: C (carried notional) held fixed in step 2, new targets scaled by
  max(0, B - C)/G.
- S5 expected behaviour: text: financing drag (about 0.2-0.35 Sharpe) and dividend-timing noise stated.
- S6 late split exposure: text: suspect-split guard (|ln move| > ln 1.5 with no split: no bar for up to 10 sessions).
- S7 delisting, liquidation, ticker change: text: 10 consecutive sessions without a bar -> closed at the last
  recorded close with costs, dropped, never re-entered; BIL replaced by SGOV after 10 sessions.
- S8 missing tests: all cases above plus a reverse split, a late distribution on a short, shorts above the cap
  (F2Fixer2).
- NOTEs N1-N14: F2Fixer2 fixes the cheap and safe ones and lists the rest.

## B5 IBKR adapter (adapter_review.md: BLOCK, 1 B, 5 SF, 8 N)
- B1 partial bar list on timeout accepted: fix: a timeout or incomplete request raises SourceUnavailable; mock fault
  mode; tests (IBKRFixer).
- S1 no-data answer inside the 2-year depth accepted silently: fix: raise or report as the report claims (IBKRFixer).
- S2 missing-day confirmation leaning on the open session's partial bar: fix, and the not-ready test must not edit the
  mock to pass (IBKRFixer).
- S3 unattended date on an exchange holiday: ruling: `run` requires an explicit --date unless --holidays FILE (the
  operator's copy of the published CME holiday calendar) is given, and refuses a day on which every contract of one
  exchange is affirmed missing while other exchanges are priced unless --accept-exchange-gap is passed (IBKRFixer).
- S4 warm-up vs live price definition: user decision (return section 7, decision 1); code: the probe subcommand logs
  the same bar fetched at different ages so the decision can rest on evidence (IBKRFixer).
- S5 shadow late fills lost: fix (executions/completed orders over a window; mock models retention) (IBKRFixer).
- NOTEs N1-N8: fix the cheap and safe ones, list the rest.

## C4a Alpaca adapter (alpaca/adapter_review.md: APPROVE WITH FIXES, 0 B, 3 SF, 9 N)
- S1 gap-spanning return when the previous bar is older than the request window: the runner now computes r from the
  recorded close (C4b B1); the source must return corporate actions over any span (prev, t] the runner asks for,
  however long, and today's raw close regardless of the window (AlpacaFixer).
- S2 shadow get_orders bounded from the first shadow record (fails after 500 orders): fix (AlpacaFixer).
- S3 an all-empty response becoming a missing day: raise SourceUnavailable instead (AlpacaFixer).
- NOTEs: stale "all" docstrings fixed; the rest listed.
