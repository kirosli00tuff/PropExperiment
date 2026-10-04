# Stage E.13 Task 5: ranking of what is left to search (lead)

Written by the lead (Opus 5.5) on 2026-10-03, against docs/prompts/STAGE_E.13.md Task 5. No market data of any
window was read for it. Every fact below cites a line, section or source key in one of the four task files:

- VEN = reports/stage_e13_venues.md (Task 1; keys P1-xx, P2-xx, B-xx)
- TC = reports/stage_e13_trend_carry.md (Task 2; keys T-xx)
- INF = reports/stage_e13_info_sources.md (Task 3; keys I-xx, P-xx)
- NGR = reports/stage_e13_ng_replication_draft.md (Task 4; keys R-xx, code file:line)

The program's own records are cited by path. Lead arithmetic is shown in section 4. Where a figure rests on an
assumption, the assumption is named. "UNSOURCED" marks anything with no source; no ranking step rests on one.

## 1. The ranking rule (fixed before the candidates were scored)

1. Primary key: the lead's odds that the candidate's next stage moves the program toward an income-bearing
   deployment. The odds combine the evidence read at its post-publication strength, whether a clean test with
   adequate power exists, and the venue fit.
2. Tie-break, in order: the strength of the published evidence; then whether the test is independent of data
   the evidence or the program has already used; then venue fit.
3. Data cost and build effort are reported but never move a candidate above one with better odds or better
   evidence. Section 3 checks this.

## 2. Candidates

- **C1 NG backward replication** (Task 4): does E.12's Gate 0 family B result for NG (h60 t_B 2.51; hF 2.33) hold
  on 2010-06-07..2019-04-30 data that no part of the program has read? The model is the frozen pooled ridge M1,
  and the threshold is reproduced from E.12's persisted out-of-fold predictions. Two tests. NGR sections 1-11,
  lead rulings C1-C21.
- **C2 Dealer-gamma-conditioned late-session momentum** (Task 3's first source): on days when the prior day's S&P
  dealer gamma exposure (GEX) is negative, trade the S&P's last half hour (14:30-15:00 CT) in the sign of its
  rest-of-day return. The data is ES as the price path for 2011-05-02..2019-04-30 (never read by the program), and
  MES is the vehicle. INF section 2.7(a) and section 5 item 1.
- **C3 Trend and carry, personal micro account at IBKR Canada** (Tasks 1 and 2): a diversified Carver-style
  portfolio of micros, held for days to weeks. TC Parts A-C; VEN part 3.
- **C4 NOAA GFS forecast revisions for NG** (Task 3's second source): the change in forecast heating/cooling degree
  days between model runs, traded intraday on NG. INF section 2.3 and section 5 item 2.
- **C5 Trend and carry on a swing prop firm** (Tasks 1 and 2): Phidias Premium (human in the loop), Elite Trader
  Funding Direct To Funded (unclear), or The Trading Pit Classic (permitted, flat by the Friday close, possibly no
  longer sold). TC Part D; VEN lead summary.
- **AIT, the AiTrader readout** (the sibling project, shown as a column for timing; its results were not read):
  AiTrader Stage C, a one-shot, pre-registered evaluation of whether its pipeline's LLM judgment of news predicts
  next-session excess returns of US equities, gross, against an equal-weighted band benchmark. It starts once
  the Stage B exit gate is met: 60 day-clusters, at least 1,000 scorable observations and adequate realized power
  (../AiTrader/docs/STAGES.md lines 19-57). The last recorded count is 45 clusters on 2026-10-02 (AiTrader commit
  0eda3cd). At one cluster per trading day, 60 clusters arrive on about 2026-10-23 at the earliest. The hard stop
  of 120 trading days from 2026-07-28 falls on about 2027-01-15 (lead calendar arithmetic, section 4).
- **C0 Pause**: open no new PropExperiment search until the AiTrader readout.
- Considered and not carried as candidates: every surprise-against-consensus source (EIA storage, WPSR, USDA,
  economic-surprise indices), because the consensus history is proprietary (Bloomberg, Dow Jones, Reuters) and no
  free history was found (INF section 1, rows 2a, 2b, 4 and 6). Also COT, put/call, SKEW, Treasury auctions and
  Fed text, whose evidence is weekly or longer, or null (INF section 1, rows 1, 7 and 8a-8b).

## 3. The ranking table (criteria in rows, candidates in columns; AiTrader as a column)

| Criterion | C1 NG replication | C2 GEX late-session momentum | C3 Trend+carry, personal IBKR | C4 GFS revisions, NG | C5 Trend+carry, swing prop | AIT AiTrader readout |
|---|---|---|---|---|---|---|
| What it tests | Whether the frozen v2 ridge's NG edge (E.12 t_B 2.51, the best of 81) holds in a decade the program never read (NGR section 1) | Whether S&P intraday momentum is present on negative-gamma days in 2011-2019 under the program's costs and timing (INF 2.7(a)) | Not a test: implementing a published premium; its own record cannot confirm an edge (TC C4) | Whether model-run revisions in gas-weighted HDD/CDD predict NG's intraday move (INF 2.3) | As C3, under a trailing drawdown (TC Part D) | LLM news judgment on next-session US equity returns, gross (AiTrader STAGES.md lines 8-17) |
| Evidence and strength | Weak: the program's own in-sample, selected result. P(best of 81 >= 2.51 under the global null) = 0.396 independent, Bonferroni 0.502 (NGR section 9) | Moderate: Baltussen et al. (JFE 2021), 60+ futures, 1974-2020, timing Sharpe 0.87-1.73 by asset class, stronger when gamma is negative; costs not tested (INF I-37b) | Strong long run, weak since 2010: MOP TSMOM above 1 gross, 1985-2009; SG Trend 0.24 net 2010-2025 (TC evidence table, T-05) | Weak: one 2025 paper on a 5-day NG1/NG2 spread from daily data; no intraday study (INF 2.3, P-05) | As C3 | Not assessed here: pre-registered elsewhere, results not read |
| Post-publication record | n/a (unpublished). The 2010-2019 regime differs: pre-LNG exports, calmer volatility (NGR section 9, R04-R20) | Decline reported after 2013 (Rosa, cited second-hand, INF I-39). The program's unconditional relative (CP1) was null on MES 2020-2024 (INF P-07, P-08). The 0DTE regime since 2022 is untested | SG Trend 0.30 net 2013-2025; AQR TSMOM 0.31 gross 2012-2025 (t 1.18); cross-sectional carry -0.19 gross 2013-2025 (TC summary, T-09, T-11) | None (published 2025) | As C3 | n/a |
| Venue fit | Topstep 150K XFA only, 1 NG contract, h60 only; does not fit a 50K (NGR section 6) | Topstep, intraday, flat by 15:08 CT; MES fits a 50K. But the S&P exposure is closed in Stage E: docs/STAGE_E_DESIGN.md D1 rule 5 | IBKR Canada PERMITTED: CIRO dealer, API, USD 0 minimum (VEN lead summary, B-02, B-06). Margins (B-06): FX, yield and grain micros $136-$919; MES $3,705, MNQ $7,359, MGC $3,788 | Topstep, NG on a 150K only (sizing as C1, NGR section 6) | Fails: at 1 micro per instrument a diversified book runs $169-$2,432 a day of sigma, against about D/27 allowed for 10% one-year ruin ($93-$167 at D = $2,500-$4,500). Phidias human-in-the-loop only; ETF unclear; TTP Classic flat on Fridays and maybe not sold (TC Part D; VEN) | US equities, not CME futures; not a Topstep vehicle |
| Data cost and top-up | NG and 5 legs: $57.31 quoted for 106 chunks ($59.03 x 1.03), plus the June-2010 chunks (unquoted); acct-2 top-up about $40.96 (NGR section 8) | ES 2011-05..2019-04: not quoted; ESTIMATE about $10.27 (E.0's ES quote, $9.197823 for 86 months, scaled to 96 months; reports/stage_e0_quotes.json). Fits acct-2's $18.07 alone. GEX: SqueezeMetrics CSV, free, from 2011-05-02; the CSV's terms not found (INF I-47, I-48) | Daily data for the build: not quoted (the next stage quotes it). Capital: the user's own (V22) | No pre-2021 forecast-vintage archive found (INF 2.3, I-30) | As C3, plus evaluation fees ($149-$169 Phidias Premium, P2-01/P2-02) | $0 to this program |
| Build effort (sessions) | 3.5-4: calendars 1.5-2, harness v10 1, quote/buy/evaluate 1 (NGR section 8, an estimate) | About 2.5-3 alone (the 2011-2019 equity calendar, an ES ext store, the GEX load, a simple rule); about 1-1.5 more if run with C1, which already builds the equity group calendar (NGR section 5, C-2). Lead estimate | 3-5 for a build and paper period (lead estimate; no test) | 3-5 (GRIB processing, gas weighting) plus a vintage archive that may not exist (lead estimate) | As C3, plus a written answer from the firm first | 0 (runs in its own repository) |
| Power, t ~ S x sqrt(years) | Expected t 3.41 (h60) and 3.17 (hF) at the observed effect over 8.90 years; power 0.93 / 0.40 / 0.13 / 0.025 at 1 / 1/2 / 1/4 / 0 of it (NGR section 9) | About 1,913 test dates. Power depends on the GEX<0 share (UNSOURCED; 10-30% assumed): 0.28-0.67 at a net per-trade Sharpe of 0.10, 0.55-0.95 at 0.15 (section 4). The 1.5c bar is about 0.17 sigma per trade at 2011-2019 index levels, which lowers power further | Years to t = 3 at S = 0.24 / 0.30 / 0.50: 156 / 100 / 36 (TC C4). Not testable in useful time | t = 3 needs 6 years at 150 events a year and a per-event Sharpe of 0.1 (INF 2.3), but there is no clean archive before 2021 | As C3 | Its own gate: realized power recomputed at C.2 |
| Income at the user's scale, if real (V22) | Per 150K XFA, 1 NG at h60: $345/month at the observed effect, $96 at half, negative at a quarter (section 4). Five copied accounts are one bet: up to about 5x, before the 90/10 split | Today's MES, 2 contracts on a 50K / 4 on a 150K: about $55-$131 / $109-$261 a month at a gross per-trade Sharpe of 0.10-0.20 and 50 trades a year (section 4; assumptions named) | Mid case at a 25% target: $40 / $89 / $189 / $428 a month at $10K / $25K / $50K / $100K; expected 10-year max drawdown 76-103% of capital (46-56% at 15%) (TC C3) | Not estimable (no effect size) | About $0: the book does not fit | n/a to this program |
| Lead's odds: (a) the next stage's test passes | 12% (7-35%) (NGR section 9; lead note on its central figure) | About 10% (5-20%): moderate evidence, but a decline after 2013 inside the window, the program's null relative, and a strict cost bar at 2011-2019 levels | n/a (no test). P(positive net return over 5 years) about 60% | About 3% (no clean window) | n/a | Not assessed |
| (b) Income-bearing deployment within 12 months | About 4%: P(real given a pass) 0.5-0.8 (NGR section 9) x about 0.5 for a net forward test, a 150K-only vehicle | About 3%: post-publication decay and the 0DTE regime between the 2011-2019 test and 2026+ trading; needs the S&P exposure reopened | Under 2%, if income is taken as $500/month or more at $100K or less (TC C3) | About 1% | About 1% | Not assessed |
| Main risks | V24 question on reloading E.12's persisted OOF predictions; ~/.cache/propexp_e12_phase1 (107 MB, outside the repo) is the only source of q; 2010s calendars at evidence grade; D8 calibrated on 2025-26 costs; regime | GEX data terms and construction (SqueezeMetrics vs OptionMetrics); the GEX<0 share unknown; in-sample for the published paper; MES closed by D1.5; D8 understates early-era costs (reports/stage_e2a_costs.md line 100) | Deep drawdowns; the user's own capital; CAD/USD; post-2012 carry gone (T-11) | No archive; weak evidence | Terms (written answers pending); granularity | Separate project |
| Timing | Probe 1 session, then 3-4 sessions | 2.5-3 sessions (or +1-1.5 with C1) | Only after capital exists (V22: XFA payouts first) | n/a | After a written answer | Exit gate about 2026-10-23 at the earliest; hard stop about 2027-01-15 |

## 4. Lead arithmetic (shown)

- **C1 income if real.** E.12's NG h60 trade set: 518 trades in 4.82 years = 107.5 a year (E.12_RETURN.md
  lines 10-11; NGR section 9). Net per trade = (5.569 x f - 1.713) ticks x $10, with f the share of the observed
  gross effect. f = 1 gives $38.56, or $345/month. f = 1/2 gives $10.71, or $96/month. f = 1/4 gives -$3.21. One
  contract on one 150K XFA (NGR section 6), before the 90/10 split, payout caps and the MLL path.
- **C2 power.** Test dates = 252 x 7.99 years (2011-05-02..2019-04-30) x 0.95 (early closes and roll blackouts,
  an assumption) = 1,913. Trades = share x 1,913, where the share is the fraction of GEX<0 days (UNSOURCED; 0.10,
  0.20 and 0.30 shown). E[t] = s x sqrt(trades), where s is the per-trade Sharpe. Power = 1 - Phi(1.96 - E[t]).
  - share 0.20: s 0.05 / 0.10 / 0.15 gives power 0.16 / 0.50 / 0.83;
  - share 0.10: 0.10 / 0.28 / 0.55;
  - share 0.30: 0.22 / 0.67 / 0.95.
- **C2 cost bar.** MES D8 round trip with a 14:30 CT entry and a 15:00 CT exit: commission 0.976 ticks + 0.5191 +
  0.5428 = 2.04 ticks = $2.55 (reports/stage_e2a_costs.md, MES check rows 14:30 and 15:00). At today's MES (index
  7,775.5, 10.7% annual volatility, $263 of daily sigma; TC C2, T-22), a last-half-hour sigma of about $91 (12% of
  the daily variance, an assumption) makes the cost 0.028 sigma. At 2011-2019 index levels near a third of
  today's, the same 2.04 ticks is about 0.11 sigma, so the 1.5c bar is about 0.17 sigma per trade. This is a lead
  approximation; the next stage computes c from D8 on the test rows.
- **C2 income if real.** Gross per-trade Sharpe 0.10-0.20 on today's $91 sigma, less $2.55 of cost: $13-$31 net per
  MES per trade. Two MES on a 50K (daily sigma target $200) and four on a 150K ($450; V2.0), at 50 trades a year
  (share 0.20): $55-$131 and $109-$261 a month.
- **AIT dates.** 15 trading days after 2026-10-02 with no exchange holiday between is 2026-10-23. The 120th NYSE
  trading day from 2026-07-28 (excluding the Labor Day, Thanksgiving, Christmas, New Year and MLK holidays) is
  2027-01-15.
- **Combined pass odds** if C1 and C2 run together and are treated as independent: 1 - (1 - 0.12)(1 - 0.10) = 0.21.

## 5. The ranked order and why

1. **C1 NG backward replication.** It ranks first on odds that are about equal to C2's ((a) 12% against about 10%;
   (b) about 4% against about 3%), and on the second tie-break: its test is the only fully independent one on the
   list. The window was read by neither the program nor any published study. The model and threshold come from
   frozen code with no free parameter (NGR sections 2-4, C1-C21). Its power is known: 0.93 at the observed effect.
   Under the global null, the chance of the selected near-miss also passing is about 0.018 (NGR section 7), so a
   pass would be informative. Against it: its evidence is weak (a selected t of 2.51), its upside is narrow (one
   NG contract on a 150K), and a fail mostly confirms the prior.
2. **C2 GEX-conditioned late-session momentum.** It has the best published evidence on the list (peer-reviewed,
   intraday, on-instrument, 45 years). It ranks second because:
   - its clean window (2011-2019) lies inside the paper's own sample, so it cannot test the reported decline after
     publication or the 0DTE regime;
   - its power rests on an unsourced share of negative-gamma days;
   - the program's closest relative (CP1) was null on MES in 2020-2024;
   - it needs the closed S&P exposure reopened (D1 rule 5).
   The margin over C1 is small. Under a pure evidence-first rule C2 would rank first. The lead's tie-break puts
   test independence above published strength, because a third v2-style near-miss is the failure the program
   most needs to avoid.
3. **C3 Trend and carry, personal account.** It has the strongest long-run evidence, and IBKR Canada permits it
   without ambiguity. But since 2010 its Sharpe is about 0.25-0.35, carry is gone since 2013, and the income at the
   user's capital is $40-$430 a month with expected 10-year drawdowns of 76-103% at a 25% target (TC C3). It
   cannot be confirmed from its own record in useful time (TC C4). It is a later diversifier for capital the user
   already has, not an income path now. It ranks third on income odds; ease plays no part.
4. **C4 GFS revisions, NG.** Weak evidence, and no forecast-vintage archive before 2021 was found. A 2021+ window
   overlaps the 2019-2024 stores (V24) and the read research window, so no clean test exists today.
5. **C5 Trend and carry, swing prop.** The drawdown arithmetic fails at minimum micro size (TC Part D), and the
   venues need written answers first (VEN).

The AiTrader readout runs on its own clock in late October 2026 at the earliest. It tests a different
information source on a different asset class, so none of C1-C5 predicts it, and it predicts none of them.

**Ease check.** C1 costs about $41 of top-up and 3.5-4 sessions. C2 costs about $10 and 2.5-3 sessions, so C2 is
the cheaper and easier of the two. C1 is ranked above it anyway, so cost did not decide the top. C3 has the best
evidence and ranks third on income at the user's scale, not on effort. No candidate was moved up because it is
cheap.

**What the whole list says.** No candidate offers better than about 4% odds of income-bearing deployment within
12 months. The best test on the list passes about one time in eight. Pausing (C0) until the AiTrader readout is a
reasonable choice that costs nothing. If the user keeps searching (V24), the cleanest next step is C1, with C2 as
an optional companion that shares C1's equity-calendar work. Run both, and the combined chance of at least one
pass is about 21%.

## 6. Pre-registration drafts (drafts only: nothing frozen, nothing run)

- reports/stage_e13_prereg_ngrepl.md (C1): the Task 4 draft and the lead's rulings, consolidated into the
  pre-registration template.
- reports/stage_e13_prereg_gexmom.md (C2): written by the lead.

Both need user decisions before any freeze (the V24 reload question for C1; reopening the S&P exposure for C2;
the top-up), and a one-session calendar probe first (NGR section 11).
