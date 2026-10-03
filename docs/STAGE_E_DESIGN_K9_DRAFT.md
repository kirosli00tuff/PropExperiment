# Stage E design amendment for K9 (DRAFT, proposals for the user)

Status: **draft, not in force.** Written in Stage E.10 (2026-10-02/03) by the lead. docs/STAGE_E_DESIGN.md
stays frozen and unedited. If the user accepts these proposals, Stage E.11 writes them into an
amendment, logs the decision in docs/DECISIONS.md, and freezes the K9 catalog with them. Nothing here
was chosen from Stage E results: every figure traces to reports/stage_e10_design_target.md (fixed
2026-10-02 22:29 PDT, before any source was read), the frozen D-sections, or the draft K9 catalog.

---

## K9-A. K9 is its own cluster and its own Holm family

**Proposal.** K9 (low-frequency, full-session holds) is a ninth cluster with its own Tier A and Tier B
(D5) and its own Holm run. V14(b)'s maximum K rises from 9 (eight clusters plus the ML route) to 10
(eight clusters, the ML route, K9). Holm runs from K9 on use alpha_k = 0.05 / 10.

**Arithmetic the user should see.**
- K1 to K8 ran Holm at 0.05 / 9 = 0.005556 (V14(b)). If all eight had a non-empty Tier A and K9 and the
  ML route each ran at 0.05 / 10, the program-level Bonferroni bound would be 8 x 0.005556 + 2 x 0.005 =
  0.0544, slightly above 0.05. With seven or fewer of K1-K8 non-empty it is at most 0.0489. The exact
  count is in the program accounting (each cluster's return). It is not re-read here, because E.10
  reads no Stage E result.
- **It changes no verdict.** The edge chain requires daily t > 3.0 one-sided, which is p < 0.00135.
  That is stricter than 0.05 / 37, so any K up to 37 is non-binding, as V14(b) already noted for K = 9.
  The strictly clean alternative is to give K9 and the ML route together what K1-K8 left unspent: at
  worst 0.05 / 18 = 0.00278 each. That is also above 0.00135, so it binds nothing either.
- **Recommendation:** K = 10 for K9 and the ML route, with the bound arithmetic recorded beside each Holm
  run. The t > 3.0 gate makes the choice immaterial. If the user wants the bound at or below 0.05 in
  every case, use 0.05 / 18 for K9 and the ML route instead. Nothing else changes.

## K9-B. The K9 screen: D5 plus a minimum trade count (V18)

**Proposal.** Tier A for K9 = D5's screen (research-window mean net P&L > 0 and daily t >= 1.0, per
contract, zeros on no-trade dates) **and** at least 30 completed round trips per trial in the research
window, counted after roll-blackout and data-quality exclusions. A trial with fewer trips is "insufficient
trades", goes to Tier B, and supports no edge statement.

**Arithmetic (299 research dates, 2025-04-01..2026-06-19 less 15 roll-blackout and 2 UR-1 dates).** 30
trips is a trade on 10% of dates. The K9 cap of two entries a week gives at most about 120. D5's t >= 1.0
then needs a per-trip mean/sd of about 1/sqrt(k): 0.18 at 30 trips, 0.09 at 120. A pass on one or two lucky
trades (V18's failure, t = sqrt(n/(n-1)) for one positive day) needs those trades to outweigh 28 or more
others.

**Alternatives:** 20 (admits rarer conditions, weaker protection) or 50 (stronger, and excludes
conditions rarer than about one a week).

**Recommendation:** 30. The design target asks every member for at least 40 expected trips (a one-third
margin), so the floor rejects only a condition far rarer in the window than its construction implies.
The one active member, K9-anncday-01, meets the margin (the catalog's recount after the review is in
section K9-F). The withdrawn K9-vixspike-01 (catalog Appendix B) would expect about 37-40 trips at its
1.0-point cutoff, short of the margin. At the source's 0.5-point cutoff it would expect about 62 (decision
K9-G.3).

## K9-C. The trial budget and N

**Proposal.** At most 40 K9 trials (one trial = one member on one exposure; no parameter grids). Program
N rises from 198 to at most 238 when K9 is screened. The DSR hurdle at N grows with the expected maximum
Sharpe of N trials (about sqrt(2 ln N)): from about 3.25 at N = 198 to about 3.31 at N = 238 in units of the
trials' Sharpe standard deviation. That is a small increase, and it is why the budget is capped.

The draft catalog's count against the budget is in section K9-F.

## K9-D. eps for K9 trials: what a K9 pass can and cannot mean

The design target's cost wall shows that **a single low-frequency trial almost cannot reach eps_X**. At two
trades a week, a trial needs a mean gross gain per trade of 0.32 to 1.03 times the vehicle's mean absolute
day-session move. At one a week, 0.60 to 1.96 times (reports/stage_e10_design_target.md, (a)).

**Proposal (for the user to rule on):** K9 keeps D7's per-trial null exactly as frozen (UCB95 < eps_X with
power >= 0.80), and its edge chain is unchanged (Holm, composite verdict, DSR, t > 3.0, PBO). The return
of the K9 screening session must state, beside every Tier A trial, the fraction of eps_X its research-window
mean represents. A K9 edge below eps_X is then reported as a **component edge**: a candidate input for
V20's ML route v2 (portfolio construction across products), not a stand-alone funnel pass. No eps is
changed and no new threshold is introduced.

## K9-E. Confirmation and holdout-2 purchases per exposure (the step 2 path; no quote run in E.10)

- **As frozen (D13, U4):** each cluster's 2019-05..2025-03 history of its chosen vehicles (the confirmation
  window plus the 13 holdout-2 chunks, sealed on arrival, oldest first) is bought just before that
  cluster's confirmation session. It is bought only for exposures with a Tier A trial after the Holm-entry
  screen.
- **Already owned, nothing to buy:** MCL, NG (K4), MGC and MHG (K5). Their confirmation windows are on
  disk and their holdout-2 chunks are sealed (holdout status at E.10 start: holdout_2 MCL, MGC, MHG, NG
  all_ok, 0 unlocks). Those confirmation windows were already read for K4's and K5's confirmations.
  K9's catalog was written without reading them, but a K9 trial on those exposures is confirmed on a
  window the program has seen before. V20 records the same overlap for the ML route. The K9 return must
  flag it.
- **The draft catalog's exposures (K9-F) are all equity index: MNQ, M2K and MYM.** None has its step 2
  history on disk. The holdout-2 stores at E.10 start hold only MCL, MGC, MHG and NG. A K9 confirmation would
  therefore buy the 2019-05..2025-03 history of the equity vehicles with a Tier A trial. E.0's quote for
  K1's three vehicles was $22.11-22.53 (D13), with the holdout-2 chunks sealed on arrival.
- **Everything else:** quoted in the K9 confirmation session's prompt (E.0's per-cluster quotes in D13 are
  the order of magnitude: about $3-$49 per cluster's vehicles), bought on acct-2 within the session cap
  (quote plus 10%) after the user's explicit approval. Before any purchase: V19's preconditions,
  ACCOUNT_2_CAP_USD raised to about $249.67 and data/config.py taught to select DATABENTO_API_KEY1 or
  DATABENTO_API_KEY2 by account. Until then every Databento call is refused.
- **New data K9 may need beyond step 2:** any member that reads deferred-contract (curve) prices, or an
  external public series, names it in its catalog entry. Curve bars are a new ohlcv-1m purchase (second
  and later contract months), quoted and approved separately in E.11 or E.12. A public series (for
  example EIA storage levels or CBOE index closes) is fetched free, with its publication time encoded as
  the availability time.
- **Holdout-2** is read only in a registered Stage D.2-type final read. REGISTRATION.md stays 0 bytes
  until then.

## K9-F. The draft catalog in one table

From reports/stage_e10_catalog_K9.md, after two rounds of lead rulings (reports/stage_e10_briefs/task4_lead_rulings.md),
the Fable review (reports/stage_e10_catalog_review.md: 0 BLOCKING, 8 SHOULD FIX, 8 NOTE) and the lead's rulings
on it (reports/stage_e10_catalog_rulings.md).

| Member | Mechanism | Condition (decision) | Hold (CT) | Exposures (vehicle, q_c) | Expected trips | Label | Trials |
|---|---|---|---|---|---|---|---|
| K9-anncday-01 | Macro-announcement-day premium earned over the announcement day (Ai, Bansal, Guo; Savor and Wilson) | The trade date carries FOMC, payroll, GDP (first or last estimate), ISM manufacturing, or the earlier of CPI/PPI for a reference month (official calendars). Early-close, early-halt and closure dates excluded | Intent 17:59 CT on the prior evening, fill 18:00 CT; exit intent 14:58, fill 14:59 (C_X - 2 min); about 21 h; long | Nasdaq-100 (MNQ, 1), Russell 2000 (M2K, 3), Dow (MYM, 3) | 58 dates in the window before the cap, 56 after; 54.9 / 53.0 scaled to 299 screened dates (worst case with every rescheduled BLS and BEA date dropped: 46.4 / 44.5) | source-overlap (K9C-003 sample to 2023-08) | 3 |
| **Total** | | | | | | | **3 of 40** |

Projected program N after K9: 198 + 3 = 201.

Withdrawn, with full specifications kept in the catalog for the user:
- **Appendix A, K9-vixback-01** (VIX-futures backwardation; Fassas-Hourvouliades). The state persists for days
  or weeks, so the weekly cap would pick days arbitrarily (the same ground as the excluded TSMOM candidate).
  At the 1-day horizon only the bottom 10% of slopes is significant, which gives about 30 trips.
- **Appendix B, K9-vixspike-01** (premium for heightened uncertainty after a VIX spike; Hu, Pan, Wang, Zhu;
  not source-overlap). It fails the borderline test fixed before any source was read. The test requires the
  condition to read a volatility level; this one reads a one-day change in VIX, which the source correlates
  at -70% with the day's return. The source's own Table 8 shows a comparable next-day return after large
  price drops alone, so the source does not separate the premium from X10's reversal.

Every other candidate in the four research logs is in the catalog's Excluded table with its reason. The
literature found supplies no K9 member for rates, FX, energy, metals, grains, livestock or bitcoin. The
session-scale evidence for those markets either trades every day with no sourced condition, documents moves
below the cost wall in the source's own units, is monthly, or is a non-survivor.

## K9-G. Decisions for the user, and what E.11 and E.12 need

Decisions before E.11 freezes K9 (the lead's recommendation first):
1. **Keep K9-anncday-01 despite D.1's E-H1** (recommended). The other choice is to cut it for consistency with
   E.0's exclusion of K1-predrift-01; K9 is then empty. The lead's grounds are in reports/stage_e10_catalog_rulings.md,
   R-02. E-H1 was a non-resolution on MES, not a null. D6 leaves announcement members to each cluster's
   literature. The date set, hold and exposures differ.
2. **K9-anncday-01's hold window.** The full announcement day (recommended: the full-session form K9 tests) or
   the excluded pre-announcement variant: the prior evening to five minutes before the NFP, ISM or GDP release
   (Hu, Pan, Wang, Zhu). The variant is not source-overlap, so an edge on it could be claimed without a
   registered holdout read. Its source finds the post-release segment small, insignificant and high-variance.
   Its window coincides with E-H1's on the same research window as MES.
3. **Reinstating K9-vixspike-01** (Appendix B): not recommended. It needs the borderline test widened from a
   volatility level to a one-day change, by the user. If reinstated, choose one cutoff: 0.5 VIX points (about
   62 capped trips, meets the 40-trip margin, 7.87 bps per trade in the source) or 1.0 (about 37-38, needs the
   margin waived, 10.34 bps). Also add the pre-stated descriptive reversal diagnostic. It would add 3 trials.
4. **Reinstating K9-vixback-01** (Appendix A): not recommended.
5. **The reopen entry time** (K9-H): 18:00 CT fill (recommended) or the 17:00 CT first bar as D-entry was fixed.
6. **The minimum trade count** (K9-B): 30 (recommended), 20 or 50.
7. **Holm K** (K9-A): 10 (recommended), or 0.05/18 for K9 and the ML route.
8. **The trial budget** (K9-C): the cap of 40 stands; the draft uses 3.
9. **The eps reading** (K9-D): report each Tier A trial's mean as a fraction of eps_X and call a sub-eps edge a
   component edge (recommended), with D7's null unchanged.
10. **Exposures.** The three equity-index exposures carry the same evidence by transfer. Keep all three
    (recommended: the check spreads over large-cap, small-cap and price-weighted indices), or the Nasdaq-100
    only (1 trial).
11. **Whether K9 is worth E.11 and E.12 at all** with one member on three correlated indices. The lead
    recommends going ahead: the cost is 3 trials and no purchase. The alternative is to fold K9-anncday-01 into
    V20's ML route v2 as a feature, with no separate screen.

E.11 (freeze) needs:
- The user's decisions above, written into a design amendment and docs/DECISIONS.md.
- Re-checks the draft flagged. BLS's revised-schedule notice for the dates moved by the 2025 lapse in
  appropriations, and BEA's revised GDP schedule (Q21): keep a date only if it was announced before the entry
  intent (R-07). Worst case with every flagged date dropped: about 46 trips before the cap on the 299 screened
  dates, 44.5 after. ISM's actual release
  dates. The CME early-close and holiday sessions in the window (R-12). The JFE sample check (R-11) is closed.
- The member text hashed into a K9 freeze manifest, as for K1-K8.

E.12 (code and screen) needs:
- The member coded against the frozen text. The harness's calendars gain the K9 announcement calendar (FOMC,
  BLS Employment Situation, CPI, PPI, BEA GDP, ISM manufacturing), built from official pages with citations,
  as in E.2a's D10 calendars, and holding the dates as known at each entry intent.
- No external series and no purchase: MNQ, M2K and MYM research-window bars are already owned (E.1 step 1). If
  K9-vixspike-01 is reinstated, CBOE's daily VIX close history (free) is added, with its availability time
  encoded.
- The screen: D5 plus the minimum trade count, the Holm run at the agreed K, the per-trial eps fraction, and
  the D9.7 exit count per member.
- A Fable audit of the member code and the screen figures before any verdict, as in E.3-E.9.

## K9-H. The reopen entry time (amends the design target's D-entry default; for the user)

**Proposal.** A K9 entry at a reopen is market intent on the 17:59 CT bar, filling at the 18:00 CT open, on
weekdays (after the 16:00-17:00 CT halt) and on Sundays alike. The design target's D-entry, fixed before any
source was read, said "the first bar at or after 17:00 CT". The lead changed it in round 2, after the sources
were read, on a non-result ground.

**Reasoning.** D9.4 prohibits "Initiating reckless trades in gapped markets to profit from stray fills".
K8-wkndbtc-01 moved its Sunday entry to 18:00 CT because the reopen's first minutes "are the gapped market of
D9.4" (reports/stage_e0_catalog_K8.md, its entry rule). The D8 cost table's 17:00 CT bucket is among the widest
on the equity vehicles. Extending the Sunday precedent to the weekday reopen after a one-hour halt is a
judgment, not a frozen rule. The Fable review (R-06) noted that one market order a day at q_c is not a
stray-fill pattern and that the harness charges slippage on every fill.

**Cost.** The member does not hold the 15:00-18:00 CT part of its source's close-to-close return (the hour after
the cash close, the halt and the reopen hour).

**Alternative.** The 17:00 CT first bar, as D-entry was fixed. **Recommendation:** 18:00 CT. It costs one hour
of a 21-hour hold and keeps every K9 fill away from the reopen minutes the K8 precedent treats as gapped.
