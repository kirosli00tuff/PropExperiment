
## 2026-10-16 — Stage E.22: the five Tier A members confirmed (no edge), the micro trend book designed, E22-F1 registered; N = 533

Prompt docs/prompts/STAGE_E.22.md (V39). Lead Opus 5.5 xhigh, ultracode on, session 1414530f, unattended; paused 02:43-18:26
PDT (usage limit, the user's pause at 07:57, a laptop restart) and resumed under a user-approved window (no confirmation read
after 02:00 PDT 2026-10-17). Return: reports/E.22_RETURN.md.

- **Harness v13** (e40ca85, dd2bcc60...): GC bars as MGC's price path (U8, V39), MNQ on NQ declared (unused), MES as a
  confirmation leg (three enumerated closure prints), not-run trials, Holm K from the list, a run-once marker with list and
  out-dir checks, a dry run. HarnessReviewer-FableXHigh: 0 blocking, 2 should-fix (fixed in code), 14 notes.
- **Lists** (ccd7fa7; K = 5, N = 533): ListReviewer-FableXHigh 0 blocking, 5 should-fix (fixed), recheck clean. Power: all
  sufficient except K6-limitcont-01 LE (undefined) and K8-wkndbtc-01 (34 < 43, by design, not run).
- **Confirmations, once each** (K5 18:28, K8 18:32, K3 18:36, K6 18:50; one at a time, setsid):
  - K5-fomc-01 MGC null (UCB95 +0.09 vs 71; Holm p 0.894); K5 no statement (MHG coverage 0.77 at confirmation).
  - K8-flight-01 HEOD null (UCB95 +2.25 vs 71; p 0.574); **K8 null**; wkndbtc inconclusive by design.
  - K3-ldnrev-01 6E null (UCB95 +0.10 vs 12; p 0.797); K3 no statement (6S, 6N coverage 0.93-0.94).
  - K6-limitcont-01 HE null by inactivity (10 trips; p 0.409); K6 no statement (limitcont LE 0 trips, R-E22-A16).
  - No Holm rejection anywhere; no edge candidate. VerdictVerifier-FableXHigh (one per cluster): no discrepancy.
- **Micro book** (design study on data E.21 read; not evidence): net Sharpe unrounded / simple / greedy $10K 0.47/0.47/0.07,
  $25K 0.47/0.41/0.29, $50K 0.47/0.46/0.31. At $25K simple: cost $572/yr, realized max drawdown 63.5%, IBKR margin p95 104%
  of capital. 12 of 21 micros modelled.
- **E22-F1** (2a2bdd8; r007-E22, N 532 -> 533): $25K simple-rounded paper book, 36 months from the first ledger record after
  the user approves a daily settlement source; PASS iff p <= 0.05 one-sided (NW lag 10) and net Sharpe >= 0.3. RegReviewer-
  FableXHigh: 2 blocking, 8 should-fix, all fixed; the rounding change from the greedy (R-B7) judged legitimate.
- **Guardrails:** holdout all_ok, 0 unlocks, at start, resume and end; REGISTRATION.md 0 bytes; spend ledger unchanged
  (36,402 lines, 034a454b...); nothing dated 2024-03-01 or later read; no purchase, no Databento or TopstepX call, no push.
  The E.16, E.18, E.20 H6 and E.20 search freezes no longer verify (they pinned v12 files that v13 rewrote; not edited); the
  end suite's one failure (tests/test_h6_rod_run.py) is the same cause.
- **For the user:** approve a daily settlement source for E22-F1 (recommend a fresh Databento statistics-schema quote); do not
  trade the book live at $25K at a 20% target; close Stage E's intraday clusters; push the E.22 commits.

### Session cost

{{COST}}
