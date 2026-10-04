## 3. Results per task

### Task 0: startup
All start checks passed (section 2). HEAD 5d85924 (the prompt commit); the tree was clean except for the expected
untracked reports/stage_e12_briefs/margin_pages/.

### Task 1: venues (reports/stage_e13_venues.md; parts _part1, _part2, _part3_brokers; questions in reports/stage_e13_phidias_question.md)
- Prop firms: 18 firms checked from their own help-centre and terms pages (all fetched 2026-10-03). Topstep, Apex,
  Tradeify, Take Profit Trader, MyFundedFutures, Bulenox, Alpha, Lucid, TradeDay, Earn2Trade, FundedNext, Top One,
  Funded Futures Family and The Trading Pit Prime are flat every session: NOT PERMITTED. Topstep requires flat by
  3:10 PM CT (P1-01).
- PERMITTED, unambiguous: The Trading Pit Classic (overnight Monday-Thursday, flat by the Friday close, own EAs
  allowed; not on the current sales page, so possibly not sold) and, for a personal account, IBKR Canada (CIRO
  dealer, TWS/REST API, USD 0 minimum, MES about USD 0.61 a side all-in, MES overnight initial margin USD 3,704.55).
- HUMAN-IN-THE-LOOP ONLY: Phidias Premium 50K/100K/150K (EOD trailing $2,500/$3,000/$4,500; the TOU's
  semi-automated clause is word-for-word unchanged since the 2026-09-28 entry, still undefined, and no API is
  documented); Leeloo's Investor account (being phased out); Wealthsimple (futures, no API).
- UNCLEAR: Elite Trader Funding Direct To Funded and Diamond Hands (multi-day holds allowed; AI and automation need
  written authorization); brokers AMP, Optimus, Ironbeam, EdgeClear, TradeStation, GFF and Jitneytrade (BC
  eligibility; the BCSC exemption limits unregistered foreign dealers to "eligible derivatives parties").
- NOT PERMITTED for automation despite overnight holds: PropEd Capital. NinjaTrader and Tradovate exclude BC. The
  bank-owned brokers, Questrade and Qtrade offer no futures.
- Support questions drafted for the user (never sent): Phidias (A: alert plus manual order; B: tap to confirm, then
  software submits; C: software-managed exits), PropEd, Leeloo, Elite Trader Funding.

### Task 2: trend and carry (reports/stage_e13_trend_carry.md)
- After publication: SG Trend Index (net) Sharpe 0.24 over 2010-2025 and 0.30 over 2013-2025, worst drawdown -20.6%;
  AQR's updated TSMOM factor (gross) 0.31 over 2012-2025 (t 1.18), against 1.41 over 1985-2009; AQR cross-sectional
  carry (gross) -0.19 over 2013-2025, against 0.92 over 1972-2012.
- Carver (quoted from his code and blog): a 4-contract minimum, a 25% risk target, IDM up to 2.5, a cost ceiling of
  0.01 Sharpe per trade.
- Sizing from published volatilities, 25% target, mid case: $40 / $89 / $189 / $428 a month at $10K / $25K / $50K /
  $100K. The books fill with FX, yield and grain micros. Expected 10-year maximum drawdown 76-103% (46-56% at 15%).
  Confirming the edge from its own record takes 44-100+ years.
- Prop fit: a 10% one-year trailing-ruin bound allows a daily sigma of about D/27; one micro per exposure runs
  $169-$2,432 a day. It fails at every drawdown size on the grid ($2,000-$7,500).

### Task 3: information sources (reports/stage_e13_info_sources.md)
- Best: (1) dealer gamma exposure conditioning late-session momentum (Baltussen et al. JFE 2021; free SqueezeMetrics
  GEX from 2011-05-02; the paper's negative-gamma share is 48%); (2) NOAA GFS forecast revisions for NG (one 2025
  daily paper; no forecast-vintage archive found before 2021). No third source meets the bar.
- Every surprise-against-consensus source (EIA storage and WPSR, USDA, economic-surprise indices) needs proprietary
  consensus history. COT, put/call, SKEW, auctions and Fed text have weekly-or-longer or null evidence.

### Task 4: NG replication draft (reports/stage_e13_ng_replication_draft.md, with the lead's rulings C1-C21)
- Model M1 (the frozen Gate 0 ridge fitted once on the E.12 panel): neither fallback condition holds. 29 of 64
  features are live on NG rows, reading NG, five legs (NQ, ZN, 6E, GC, ZC) and official calendars. E.12 persisted
  the out-of-fold predictions, so q is reproduced, not refitted.
- Databento's GLBX.MDP3 starts on 2010-06-06. The window is 2010-06-07..2019-04-30 (lead rulings C5 and C6: a fixed
  start with no volume read, and no May-2019 splice).
- Cost: $57.31 quoted for NG and the five legs ($59.03 with the 3% margin), plus the June-2010 chunks (unquoted);
  acct-2 top-up about $40.96. Build: 3.5-4 sessions, mostly sourced 2010-2019 calendars. No Databento call was
  made: E.12's record covers every item.
- Prior: P(the best of 81 reaches t >= 2.51 under the global null) = 0.396 (Bonferroni 0.502). Power 0.93 / 0.40 /
  0.13 at 1 / 1/2 / 1/4 of the observed effect. Odds 12% (7-35%).
- Designer's recommendation: run later, after a one-year calendar probe.

### Task 5: ranking (reports/stage_e13_ranking.md v3) and pre-registration drafts
- The ranking table has candidates in columns, with the AiTrader readout as a column. Its rule: deployment odds
  first; then published evidence, test independence and fit; cost and effort never decide.
- Final order: **C1 NG replication > C2 GEX momentum > C3 trend+carry personal > C4 GFS revisions > C5 trend+carry
  swing prop.** C0 (pause) is a reasonable alternative.
- The order went through three versions; the review's R-01 settled it (section 5).
- Drafts (nothing frozen):
  - reports/stage_e13_prereg_ngrepl.md (C1);
  - reports/stage_e13_prereg_gexmom.md (C2: GEX < 0 days, trade 14:30-15:00 CT in the sign of the rest-of-day
    return, MES vehicle, c 2.038 ticks, 1.5c and p <= 0.025 per test, two tests).

## 7. Decisions for the user (the lead's recommendation first)

1. **Which candidate next.** Recommendation: either pause until the AiTrader readout (it costs nothing, and none of
   C1-C5 offers better than about 7% central odds of income-bearing deployment), or, if you keep searching, run C1:
   - E.14: a one-session calendar probe (2012's energy calendar and the NGS table at evidence grade), then the
     freeze and harness v10, at $0;
   - E.15: the purchase and one evaluation.
   Add C2 only if you also want the published-evidence test (it shares the equity calendar and the harness change).
2. **Purchase and top-up.** None now. If C1 runs: an acct-2 cap raise of about $41-$50 after the probe ($59.03 with
   the margin, plus the June-2010 chunks, quoted fresh then). C2 alone (about $10.58 with the margin, an estimate)
   fits today's $18.07. Both together: about $50.
3. **V24 question (needed for C1).** Allow two computations on the already-bought 2019-2024 panel: reloading E.12's
   persisted out-of-fold predictions to reproduce the threshold q to 1e-9, and one full-panel fit of the frozen
   ridge M1. Neither reruns Gate 0's decision. Recommendation: allow both, if C1 runs.
4. **Reopen the S&P exposure (needed for C2).** Stage E closed it (docs/STAGE_E_DESIGN.md D1 rule 5). C2 reads ES
   bars never read and trades MES; MES's sealed holdouts stay sealed. Recommendation: decide only if you choose C2.
5. **Support questions.** Drafted for Phidias, Elite Trader Funding, PropEd and Leeloo, never sent.
   Recommendation: hold them. No multi-day strategy on the list fits a prop firm's trailing drawdown (Task 2,
   Part D), so the answers would not change a decision now. Send the Phidias one if a multi-day system becomes a
   candidate.
6. **Personal account.** Recommendation: not now. IBKR Canada is the venue when there is an edge to move or capital
   to deploy (V22). Trend and carry at $10K-$100K earns about $40-$430 a month in the mid case, with deep drawdowns.
7. **Keep ~/.cache/propexp_e12_phase1** (107 MB, outside the repository). It is the only source of C1's threshold
   until a freeze hashes and copies it.
