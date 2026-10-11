
## 2026-10-10 — Stage E.19: prop economics; the Topstep funnel is negative at zero edge; break-even net Sharpe about 0 (50K) to 0.9 (150K)

Prompt docs/prompts/STAGE_E.19.md (V22, V31, V32). Lead Opus 5.5 xhigh, session 087ee4a8. Return: reports/E.19_RETURN.md.

- **Verdict: no, at zero edge.** Inside the policy band (daily risk <= 0.25 of the drawdown distance) all 1,500 zero-edge
  configurations lose money: best 50K Standard -$250 per cycle (-$31 per Combine purchase; -$94 without the $14.50
  API fee), 100K -$1,063, 150K -$2,696. It depends on costs (at a net Sharpe of exactly 0, 50K is about break-even)
  and on sizing beyond the terms (f 0.50 with the DLL reaches about break-even; sign not established).
- **Break-even net Sharpe** (best band f): 50K 0.02 Standard / < 0 Consistency; 100K 0.52 / 0.34; 150K 0.86 / 0.54;
  zero gross edge is about -0.5 net (D8 costs at one round trip a day). Best: 50K, Consistency, DLL, Standard
  pricing, Back2Funded: +$906 per cycle at a net Sharpe of 0.5. $5,000 withdrawn (five 50K accounts): 112 / 164
  purchases and $7.9K / $11.5K of fees at zero edge (50% / 80%), 51 / 76 and $4.1K / $5.9K at 0.5. Cycles with no
  payout at all: 48-74% at zero edge.
- **Rules:** 214 rules (198 SOURCED, 7 UNSOURCED, 3 CONFLICT) and 42 practices from 41 Topstep help-centre and terms
  pages (curl, one page at a time; ToU section 28 crawl ban read as not covering named fetches, upheld by Fable).
  New since E.12: Combine consistency 55% of total profit; call-up discretionary; API $14.50/month; no VPS.
- **Model:** prop_econ/ (rules, scalar reference, vectorized simulator, fees and campaigns, returns, grid,
  aggregator), 148 tests; 780 jobs, 4,464 records (82.7 min on 4 workers). Returns: owned E.12 training stores, NQ,
  CL, GC, ZN, 6E day sessions, demeaned, random direction, 5-day block bootstrap; normal comparison.
- **Review:** RulesReviewer-FableXHigh 1 BLOCKING (RR-1 account stacking: churn metrics and label L-19 added), 4
  SHOULD FIX, 14 NOTE; EconReviewer-FableXHigh 0 BLOCKING, 3 SHOULD FIX (text fixes), 11 NOTE; the headline
  reproduces independently (blind recomputation, Phase C verdict cells). Rulings reports/stage_e19_rulings.md.
- **Guardrails:** holdouts all_ok, 0 unlocks, start and end; REGISTRATION.md 0 bytes; N 480 unchanged; spend ledger
  unchanged (no purchase, no Databento call); harness v12 unchanged; no TopstepX call; no push.
- **For the user:** do not buy a Combine until a registered test shows a net Sharpe of about 0.5 or more; then 50K,
  Consistency path, DLL, Standard pricing, Back2Funded, a fixed fee budget (about $1,000) and a bot that obeys the
  terms list in the return's section 7.
