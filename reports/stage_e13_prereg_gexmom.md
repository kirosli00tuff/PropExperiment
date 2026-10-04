# Pre-registration DRAFT: dealer-gamma-conditioned late-session momentum in S&P futures (C2)

Status: DRAFT for the user, written by the lead in Stage E.13 on 2026-10-03, revised 2026-10-04 after the Fable review
(reports/stage_e13_rulings.md). Ranked second in reports/stage_e13_ranking.md (v3). Nothing here is frozen, run, fetched
or bought. Neither the GEX file nor any price was opened to write it. A later stage freezes it only after the
user's decisions in section 10, writing its sha256 into that stage's STATE file before any computation.

Sources: reports/stage_e13_info_sources.md (INF) section 2.7(a) and section 5 item 1, with keys I-37b (Baltussen,
Da, Lammers and Martens, "Hedging demand and market intraday momentum", JFE 2021), I-39 (the post-2013 decline
reported by Rosa, cited second-hand), I-40, I-47 and I-48 (SqueezeMetrics GEX: the definition, the CSV and the
platform terms), and P-07, P-08 (the program's CP1 port and D.1's MES null). Ranking: reports/stage_e13_ranking.md,
candidate C2.

## 1. Hypothesis (one, with a stated sign)

On trade dates whose prior trading day's S&P 500 dealer gamma exposure is negative, the S&P 500 futures return
over the last half hour of the cash session (14:30-15:00 CT) has the same sign as that day's rest-of-day return
(the prior trade date's 15:00 CT price to today's 14:30 CT price). Baltussen et al. report that "market intraday
momentum is present for the index when NGE is negative and becomes stronger when NGE becomes more negative"
(INF I-37b). The test asks whether this holds in 2011-2019 under the program's timing, vehicle and costs.

## 2. Data and windows

- Price path: ES.v.0, Databento GLBX.MDP3, ohlcv-1m (volume-ranked continuous, splices from Databento's symbology,
  as the step 2 builder does). Trade dates 2011-05-03..2019-04-30. The first date needs the prior day's GEX, which
  starts 2011-05-02. The end is the day before the program's earliest read data (2019-05). No program file has
  read any bar before 2019-05 (NGR section 5, evidence list).
- Vehicle (costs, sizing, any later deployment): MES, tick 0.25 index points = $1.25 (rules/products.py:154).
  ES and MES track the same index, so index-point moves convert to MES ticks one for one per 0.25 points.
- Conditioning data: SqueezeMetrics' daily DIX/GEX CSV (date, price, DIX, GEX), from 2011-05-02 (INF I-47); GEX
  is "a dollar-denominated measure of option market-makers' hedging obligations" (INF I-40). Before use, the next
  stage records the CSV's URL, UTC fetch time and sha256, and reads the CSV's terms. The platform terms bar
  "creating user accounts by automated means" (I-48), and no clause on the public CSV was found. If its terms
  forbid this use, C2 stops (no substitute series without a new pre-registration).
- Information timing: for trade date d, use the GEX row dated on the latest trading day strictly before d. If
  SqueezeMetrics documents that a row dated d-1 can be published after 14:30 CT on d, use the row two trading days
  back. The next stage records which applies before any price is read.
- Never read before the test: the 2011-2019 ES bars and the CSV's GEX values. The only read before the
  evaluation is section 9 step 3, a COUNT of GEX < 0 days in the window, with no prices and no returns.

## 3. Rule (every parameter fixed)

- Eligible date d: a normal ES day session (CME equity early-close dates excluded, from the 2011-2019 equity
  calendar built from official pages); not an ES roll-blackout date (the splice date and the two group trade
  dates before it, data/stage_e_bars.py:30-33); every bar the rule reads present; a GEX row available per
  section 2. A date that fails any condition is excluded and counted. No other exclusion: FOMC, CPI and option
  expiry dates stay in.
- Unsourced calendar dates (as C1's ruling C12; Fable R-07): a date whose holiday or early-close status cannot be
  sourced at "cme" or "secondary" grade is excluded and counted. The run stops before the purchase if more than 2%
  of the window's dates are excluded this way. The calendar is built and this check made before any price is
  bought.
- Signal: R_rod(d) = close(b_14:29 on d) / close(b_14:59 on the prior trade date) - 1, where b_s is the one-minute
  bar starting at s CT and its close is known at s + 1 minute. The prior trade date's 15:00 CT price is the cash
  close.
- Entry and exit (the frozen engine's clock: decide at a bar's close, fill at a later bar's open):
  - side = +1 if R_rod > 0, -1 if R_rod < 0, no trade if R_rod = 0;
  - entry at the open of b_14:30, exit at the open of b_15:00, as a market order; one MES per trade;
  - flat well before Topstep's 15:10 CT flatten (VEN P1-01).
- Gross P&L per trade: g = side x (open(b_15:00) - open(b_14:30)) / 0.25, in MES ticks.
- T1 (the hypothesis): the trades on eligible dates with GEX < 0.
- T2 (the comparator): the trades on every eligible date, whatever GEX is.
- Nothing is fitted or tuned. There are no windows, thresholds or lookbacks other than those above.

## 4. Costs

c = the D8 MES round trip for a 14:30 entry and a 15:00 exit: commission 0.976 ticks ($1.22 / $1.25) + s_b(14:30)
0.5191 + s_b(15:00) 0.5428 = 2.038 ticks ($2.55) (reports/stage_e2a_costs.md, MES check, rows 14:30 and 15:00). It
is fixed for every trade, with no event-window change. This section is the only statement of c (Fable R-07). D8 was calibrated on 2025-26 books and understates thinner
early-era costs (same file, line 100). At 2011-2019 index levels this cost is a larger share of the move than
today (ranking section 4), so the bar is conservative for deployment at today's prices.

## 5. Pass bar (fixed)

Each test Tk passes iff all of:
1. mean g >= 1.5 x c = 3.057 MES ticks (0.764 index points) per trade;
2. one-sided t on the per-trade g (one trade per date, so date clustering is the identity) with p <= 0.025
   (Bonferroni 0.05 / 2), in the direction mean g > 0;
3. at least 30 trades.

The GEX hypothesis passes iff T1 passes AND T1's mean g exceeds T2's (a point comparison: the conditioning adds
information). T2 passing alone reads "unconditional late-session momentum in 2011-2019; no evidence that GEX adds
information". That is not a pass for C2.

## 6. Trial count

+2 (T1 and T2) at registration, whatever the outcome. N 471 -> 473 if C2 runs alone; 473 -> 475 if it is
registered after C1. The count in section 9 step 3 is not a test.

## 7. Power and prior

- Test dates: about 1,913 (252 x 7.99 years x 0.95 for exclusions, an assumption). T1's trade count is the GEX < 0
  share of them. The paper's own NGE has a 48% share: "In the period from 1996 until May 2020 there have been 2930
  days with a negative NGE and 3158 with a positive one" (I-37b; reports/stage_e13_briefs/pages/InfoSource/
  baltussen_etal_2021_jfe.md; Fable R-02). SqueezeMetrics' GEX column is a different construction, so its share
  may differ. Section 9 step 3 counts it before any price is read.
- Power of T1 at the 0.025 t bar: at the paper's share of 0.48 (about 920 trades), 0.33 / 0.86 / 0.995 for a
  per-trade Sharpe of 0.05 / 0.10 / 0.15. At a share of 0.20, 0.16 / 0.50 / 0.83. At 0.10: 0.10 / 0.28 / 0.55. At 0.30: 0.22 / 0.67 / 0.95 (ranking section 4). The 1.5c bar is about
  0.13-0.17 sigma per trade at 2011-2019 index levels (a lead approximation; ranking section 4, Fable R-09). It
  binds before the t bar at every share of 0.10 or more, so the effect must be strong to pass.
- The paper's timing-strategy Sharpe is 0.87-1.73 a year at the asset-class level, before costs (INF I-37b), or
  0.055-0.11 per day unconditionally (INF 2.7(a) fit line). The conditional effect is larger by the paper's
  account; its size is not quoted in INF.
- Prior against: a decline after 2013 was reported (I-39, second-hand). The program's unconditional relative, the
  CP1 port, was null on MES in 2020-2024 (P-07, P-08), though the rest-of-day form and the gamma conditioning were
  never screened (INF 2.7(a)). The window lies inside the paper's sample, so a pass shows a 2011-2019 effect under
  the program's costs, not a post-publication one.
- The lead's odds of a C2 pass, derived in ranking section 4 (reports/stage_e13_briefs/c2_odds.py): central 18.0%,
  skeptical 3.9%, optimistic 38%. Odds of income-bearing deployment: 5.0% / 0.8% / 15.4%.
- Minimum-power stop (section 9 step 3): if fewer than 200 eligible GEX < 0 dates exist, power is below about 0.5
  even at a per-trade Sharpe of 0.14. The stage then stops before the purchase and reports, and the user decides.
  At the paper's 48% share (about 920 dates) the stop is far from binding. It guards only against a very different
  sign distribution in SqueezeMetrics' series.

## 8. What each outcome means

- **Pass:** on negative-gamma days the S&P's last half hour followed the rest of the day's direction, by at least
  1.5x the program's cost, at p <= 0.025, in 2011-2019, and more than on all days. This supports the gamma-hedging
  channel under the program's costs. It is not a deployment verdict: the evidence is pre-publication, the 0DTE
  options regime since 2022 is untested, and at about 50 trades a year a forward test needs years to reach t = 3.
  The next step would be a pre-registered forward paper test on MES with the rule unchanged. MES's sealed
  holdouts stay sealed (CLAUDE.md: Stage D.2 only).
- **Fail:** the gamma-conditioned form does not clear the program's costs even inside the published sample. The
  GEX source is closed for this program.
- **T2 alone passes:** recorded as an unconditional pre-publication effect. It opens nothing on its own, because
  the program's related price-only tests were null after 2019.

## 9. Order of events

1. The user's decisions (section 10). Freeze this pre-registration and the harness change: an ES store for
   2011-05..2019-04, alongside C1's "ext2010" type if both run. The Fable review comes before the freeze.
2. Fetch the GEX CSV once: terms check, sha256, the timing rule of section 2. Record all three before step 3.
3. Count the eligible GEX < 0 dates (a count only; no price or return is read). If the count is under 200, stop
   and report (section 7).
4. Build the 2011-2019 equity group calendar from official pages (shared with C1's C-2).
5. Quote fresh (logged first), then buy ES 2011-05..2019-04. The store build prints counts only.
6. Run T1 and T2 once, behind a run-once marker, and report the verdict.

## 10. Decisions the user must make before any freeze

1. **Reopen the S&P exposure for this one test.** Stage E closed it: "The S&P 500 exposure (ES, MES) is not a
   traded exposure in Stage E: MES is closed" (docs/STAGE_E_DESIGN.md D1 rule 5). C2 trades MES and reads ES
   bars of a period never read. MES's sealed holdouts are untouched.
2. **The purchase:** ES 2011-05..2019-04, not yet quoted; ESTIMATE about $10.27 by scaling E.0's ES quote ($9.197823
   for 86 months, reports/stage_e0_quotes.json) to 96 months. It fits acct-2's $18.07 headroom alone (with the
   3% margin, about $10.58). Run together with C1, the combined top-up is about $50.
3. **The GEX source:** accept SqueezeMetrics' free CSV, subject to the terms check in section 9 step 2.
