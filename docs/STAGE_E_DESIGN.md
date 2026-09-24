# Stage E program design

**DRAFT. Nothing in this file is frozen, hashed or registered.** Written by the Stage E.0 lead
(Opus 5.5, max effort) on 2026-09-23 for the user's review. Stage E.1 freezes it (with whatever
the user changes) and buys the data. Every answer below is a proposal: the rule, the reasoning,
the alternatives considered, and what the user must decide.

Written before any price, volume-by-minute or order-book data for any Stage E product existed on
this machine. The only product data used anywhere in this file are public aggregates (contract
specifications, published average daily volume and open interest) and Databento quote metadata
(cost and billable size, which carry no prices).

Order of writing, for the record: D1's rule was fixed at 20:10 PDT (reports/stage_e0_STATE.md)
before any census or quote output existed; D15, D6, D2 to D5 were written next, before any
CatalogWriter started; the rest was filled as the Task 1 and Task 2 artifacts arrived.

Standing inputs from Stage D (MES): ε = 34 net ticks per micro per day, $85.00 a day at 2 micros
(docs/NULL_CRITERIA.md 2.2; the consistency path, T = 2, p = 0.60, R = 1.00 cell of the Stage B
power gate); the MES reference risk E|m_1| = 144.27 ticks, the mean absolute RTH move at T = 1 on
the research bars, $360.68 at 2 micros (NULL_CRITERIA.md 2.1); cumulative N = 58 after D.1f.

---

## D1. Universe and liquidity floor

**Rule (fixed 20:10 PDT, before any census or quote output; copied verbatim from the STATE file).**

1. Exposure = the Topstep-permitted contracts on one underlying whose prices are tied by exchange
   arbitrage (reports/stage_e0_partition.md section 1).
2. An exposure is IN if its most active permitted contract (highest public ADV) meets both:
   (a) public average daily volume >= 10,000 contracts per day, from the most recent CME-published
       full-year or trailing-12-month figure the census finds; no figure found = fails (a), flagged;
   (b) day-session coverage >= 0.95: over the five calibration dates, the mean of
       (ohlcv-1m records in the product's declared day-session window / minutes in that window),
       records = quoted billable bytes / 56 (the ohlcv-1m record size).
3. A contract of an IN exposure is an admissible vehicle if its public ADV >= 1,000 contracts per
   day or it is the exposure's most active contract. Choosing among admissible vehicles is D2's job.
4. History length is not part of D1 (short histories are D4's per-product start rule and power check).
5. The S&P 500 exposure (ES, MES) is not a traded exposure in Stage E: MES is closed and ES is the
   same exposure; it enters only as a leg, on non-holdout dates.
6. Applied mechanically to the Task 1b and Task 2 figures; the kept and dropped lists follow from it.

Declared day-session windows (CT) for the coverage proxy: equity index and crypto 08:30-15:00;
rates and FX 07:20-14:00; energy 08:00-13:30; metals 07:20-12:30; grains 08:30-13:20; livestock
08:30-13:05.

**Reasoning.** The harness fills market orders at the next one-minute bar's open with a
calibrated slippage table. That model is only as good as the bar stream: where minutes go without
a trade, a "next open" can be minutes stale. (b) measures exactly that, from quote metadata alone,
in the part of the day where nearly every member trades. (a) is a coarse sanity floor: a product
with fewer than 10,000 contracts a day on its most active contract is thin enough that one- to
five-lot market orders are no longer small against the flow, and the cost model's assumptions
(top-of-book fills) weaken. The floor is applied to the exposure's most active contract because
the price path is shared across the exposure's contracts; the vehicle floor (3) is looser because
a micro is quoted by market makers against its full-size contract even when it trades less.

**Alternatives considered.** A cost-to-range floor (spread in ticks against typical range): the
better economic criterion, but it needs price data, so it moves to E.2 as a vehicle check (D2).
A whole-session coverage floor: rejected as a product criterion because overnight thinness matters
only to members that trade overnight; it becomes a member-level check instead (D9: every member's
own window must show coverage >= 0.95 on the research window before it is screened). An
open-interest floor: OI measures positions held across days, which this program never holds.

**Input change, logged before any ADV value was read (21:02 PDT, reports/stage_e0_STATE.md).** The
census (reports/stage_e0_liquidity.json, LiquidityCensus2-OpusHigh) found a 2025 full-year ADV for
only 11 of 50 products and CME's 2026 year-to-date ADV (January to August, from CME's August 2026
monthly ADV report) for all 50. Read literally, "full-year or trailing-12-month" would have failed 39
products for lack of such a figure, an availability artifact the rule's intent (a recent annual-scale
activity level) does not require. D1(a) is applied to the 2026 January-August ADV for every product,
one common CME-published period; the 2025 figure is shown where it exists. The threshold is unchanged.

**Applied mechanically (21:25 PDT).** Coverage = mean over the five dates of ohlcv-1m records per
minute of the declared window (reports/stage_e0_quotes.json, set C).

| Cluster | Exposure | Most active contract, 2026 Jan-Aug ADV | (a) >= 10,000 | (b) coverage | (b) >= 0.95 | D1 | Admissible vehicles (2026 Jan-Aug ADV) |
|---|---|---|---|---|---|---|---|
| K1 | Nasdaq-100 | MNQ 2,363,465 | yes | 1.000 | yes | IN | MNQ, NQ (593,595) |
| K1 | Russell 2000 | RTY 209,871 | yes | 1.000 | yes | IN | RTY, M2K (115,832) |
| K1 | Dow | MYM 152,686 | yes | 1.000 | yes | IN | MYM, YM (108,142) |
| K1 | Nikkei 225 USD | NKD 7,969 | NO | 0.621 | NO | **OUT** | — |
| K1 | S&P 500 | ES 1,615,122 | yes | 1.000 | yes | leg only (D1.5) | MES bars (owned) serve as the leg |
| K2 | 2-year | ZT 1,325,938 | yes | 0.981 | yes | IN | ZT |
| K2 | 5-year | ZF 1,941,530 | yes | 0.997 | yes | IN | ZF |
| K2 | 10-year | ZN 2,589,058 | yes | 0.999 | yes | IN | ZN |
| K2 | Ultra 10-year | TN 819,357 | yes | 0.972 | yes | IN | TN |
| K2 | Bond | ZB 609,604 | yes | 0.985 | yes | IN | ZB |
| K2 | Ultra bond | UB 505,131 | yes | 0.982 | yes | IN | UB |
| K3 | EUR | 6E 216,466 | yes | 0.998 | yes | IN | 6E, M6E (24,552), E7 (4,018) |
| K3 | AUD | 6A 119,206 | yes | 0.999 | yes | IN | 6A, M6A (7,765) |
| K3 | GBP | 6B 103,657 | yes | 0.987 | yes | IN | 6B, M6B (4,290) |
| K3 | CAD | 6C 81,946 | yes | 0.985 | yes | IN | 6C |
| K3 | JPY | 6J 180,897 | yes | 0.996 | yes | IN | 6J |
| K3 | CHF | 6S 30,520 | yes | 0.970 | yes | IN | 6S |
| K3 | MXN | 6M 69,001 | yes | 0.903 | NO | **OUT** | — |
| K3 | NZD | 6N 40,801 | yes | 0.957 | yes | IN | 6N |
| K4 | WTI crude | CL 1,079,857 | yes | 1.000 | yes | IN | CL, MCL (252,100), QM (9,446) |
| K4 | Henry Hub gas | NG 521,792 | yes | 1.000 | yes | IN | NG, MNG (14,942), QG (4,060) |
| K4 | RBOB | RB 206,850 | yes | 1.000 | yes | IN | RB |
| K4 | ULSD | HO 187,479 | yes | 1.000 | yes | IN | HO |
| K5 | gold | MGC 429,702 | yes | 1.000 | yes | IN | MGC, GC (212,764) |
| K5 | silver | SIL 134,882 | yes | 0.990 | yes | IN | SIL, SI (83,587) |
| K5 | copper | HG 77,679 | yes | 0.997 | yes | IN | HG, MHG (21,803) |
| K5 | platinum | PL 22,360 | yes | 0.991 | yes | IN | PL |
| K6 | corn | ZC 505,663 | yes | 1.000 | yes | IN | ZC |
| K6 | wheat | ZW 180,405 | yes | 0.990 | yes | IN | ZW |
| K6 | soybeans | ZS 302,997 | yes | 1.000 | yes | IN | ZS |
| K6 | soybean meal | ZM 181,637 | yes | 1.000 | yes | IN | ZM |
| K6 | soybean oil | ZL 232,819 | yes | 1.000 | yes | IN | ZL |
| K6 | lean hogs | HE 67,267 | yes | 0.998 | yes | IN | HE |
| K6 | live cattle | LE 68,652 | yes | 0.999 | yes | IN | LE |
| K7 | bitcoin | MBT 69,615 | yes | 0.996 | yes | IN | MBT |
| K7 | ether | MET 61,082 | yes | 0.947 | NO | **OUT** (borderline) | — |

**Result: 31 traded exposures, S&P 500 as a leg only, 3 exposures out (NKD, 6M, MET).** Every
contract of an IN exposure clears the 1,000-contract vehicle floor. Dropped exposures are not traded;
one may serve as a signal leg only if the member-level coverage check (D9) passes for that leg in
the member's own window. K7 is left with one traded exposure (bitcoin).

Two results the user should look at: MET misses (b) by 0.003 (0.947); NKD fails both parts (ADV
7,969; coverage 0.621 in the 08:30-15:00 CT window, which is not NKD's most active window, since
Nikkei trading concentrates in Tokyo hours). The rule was fixed before these figures existed and is
applied as written; the user may re-admit either.

**User decides:** the two thresholds (10,000 contracts a day; 0.95 coverage); whether an exposure
dropped by (a) only because no public figure was found should be re-checked by hand.

---

## D2. Trading vehicle per exposure, and the sizing rule

**Rule (proposed).**
- Risk target: MES at 2 micros, R* = $360.68, the mean absolute RTH open-to-close move of MES at
  2 micros on the research window (D.1e's E|m_1| = 144.27 ticks x $1.25 x 2).
- Per-contract risk of contract c on exposure X: r_c = the mean over research-window trade dates
  (2025-04-01..2026-06-19, roll-blackout and vendor-degraded dates excluded) of
  |close(C_X - 1 min) - open(O_X)| in USD per contract, where O_X and C_X are the exposure's
  day-session open and close (D6 table). Measured in E.2 on research-window bars only.
- Size: q_c = min(cap_c, max(1, round(R* / r_c))), where cap_c is the number of contracts of c that
  make 1 lot-equivalent (D9.5: minis 1, micros 10, SIL 5, MBT 1, MET 1); risk ratio
  rho_c = q_c r_c / R*.
- A candidate vehicle is an admissible contract (D1.3) with rho_c <= 2.0. Among candidates, those
  with rho_c >= 0.5 are preferred; the vehicle is the preferred candidate with the lowest modelled
  round-turn cost per dollar of risk, (commission_c + 2 x one-side slippage_c) / (q_c r_c) at size
  q_c, from the D8 cost model; ties go to the higher public ADV. If every candidate has
  rho_c < 0.5 (possible for a full-size-only exposure whose one contract moves less than MES at
  2 micros, since the cap fixes q = 1), the exposure is traded at the cap and flagged "undersized";
  its funnel-derived ε (D3) then governs. Chosen in E.2, before any member is run, and frozen.
  (Amended 21:12 PDT after CatalogWriter-K2's note: the 1-lot cap of D9.5 fixes q = 1 for every
  full-size-only exposure, so the lower band could not be met by sizing up.)
- An exposure with no candidate (rho_c > 2.0 at q = 1 on every admissible contract) is not traded
  in Stage E. It may still serve as a leg. Expected cases are the long-bond contracts, to be seen.
- Every member on exposure X trades q_c of the chosen vehicle (a member whose rule sizes by
  signal scales from q_c downward, never above it). Two-leg members size each leg to r_c parity
  (q_1 r_1 as close as integers allow to q_2 r_2) and scale the pair so the spread's measured
  E|m_1| is nearest R*; the sum of legs respects the position limit.
- Price path and history: a member's signals and fills use the vehicle's own bars. Where the
  vehicle is a micro whose own history is too short for D4's power check, E.2 may use the
  exposure's full-size contract bars as the price path with the micro's cost model and tick
  value (same underlying, same quotes up to the multiplier), declared per exposure before any
  confirmation read (D4).

**Reasoning.** The funnel's economics (ε, the MLL and payout dynamics) were derived for a daily
P&L distribution at MES's 2-micro scale. Matching each vehicle's typical day-session move in
dollars to that scale keeps every member inside the regime where ε was measured, so the dollar
bar transfers (D3) and the account rules bite the same way. The band 0.5 to 2.0 allows the integer
size to miss by a factor of two either way; outside it the funnel is being run at a different
scale and the $85 bar would no longer be the funnel's own number. Cost per unit of risk picks
between the micro and the full-size contract of an exposure, since micros are cheaper to size
finely and usually dearer to trade per unit of notional.

**Alternatives considered.** Fixed one contract per product (simple, but risk would vary by a
factor of about 20 across the universe, and ε would mean something different on every product);
volatility-scaled size per member per day (D-H2's idea; it makes size a signal, which is a
hypothesis, not a sizing rule); risk from the standard deviation instead of the mean absolute move
(more sensitive to the tails of a 15-month window; the mean absolute move is what ε was derived
from).

**User decides:** the risk target (MES 2 micros); the band [0.5, 2.0]; whether exposures above the
band (probably ZB and UB) are dropped or traded at 1 contract with their own funnel-derived ε.

---

## D3. Epsilon per product

**Rule (proposed).**
- Translated bar: eps_X = floor( $85.00 / (q_c x tick value_c) ) net ticks per contract per day
  of the chosen vehicle c at size q_c. Example with made-up numbers: a vehicle with a $1.00 tick
  traded at 4 contracts gives floor(85 / 4) = 21 ticks per contract per day.
- Funnel re-derivation (E.2, compute only): the Stage B power gate (funnel/power_gate.py, 8,000
  careers per cell, robust verdict, both payout paths) re-run per traded exposure with the
  exposure's own segment moves E|m_T| (T = 1, 2, 4, 8) measured on the research window at q_c, and
  its own modelled round-turn cost; eps_X,funnel = floor(min over passing cells of net $/day /
  (q_c x tick value_c)), by D.1e's rule exactly (docs/NULL_CRITERIA.md 2.2), with the cell set
  fixed in advance (the 120 grid cells plus D.1e's 100 extension points, re-evaluated).
- Operative eps_X = min(translated, funnel-derived). Both are reported. If no cell of the pre-declared set passes for an exposure, the funnel
  figure is undefined: the translated bar is used and the exposure is flagged (review R-12). The smaller is used because
  a smaller ε makes a null harder to claim; an edge claim does not use ε (it uses the funnel gate
  inside the composite verdict, D5).

**Reasoning.** ε is a daily dollar figure because the funnel acts on daily P&L (D.1e). Under D2's
risk matching, $85 a day is the natural first translation. It is not exact: a product whose daily
moves are fatter-tailed than MES's at the same mean absolute move breaches the MLL more often, and
its own funnel bar would differ. The re-derivation measures that with the program's own simulator
instead of assuming it away, and taking the minimum keeps every null claim conservative.

**Alternatives considered.** A single dollar ε for every product without re-derivation (simpler,
unverified for non-MES distributions); a per-product ε at a fixed contract count instead of the
risk-matched size (would make ε unreadable across products).

**Compute note.** D.1e's 100-cell extension took minutes per cell at 8 processes. At 220 cells per
exposure and roughly 30 traded exposures this is several hours of compute; E.2 runs it resumably at
<= 8 processes, nice 10, one exposure at a time, or on the bracketing subset only (the cells whose
per-day figure lies within +-30% of the translated bar), declared before the run.

**User decides:** whether to accept min(translated, funnel) or the funnel figure alone.

---

## D4. Windows and holdouts, per product

**Rule (proposed): MES's calendar for every product, so that cross-product members see aligned
windows.**
- Research window (screening, sizing inputs, cost calibration, ML tuning): trade dates
  2025-04-01..2026-06-19 (the data end is 2026-06-21 00:00 UTC; holdout-1's first bar is
  2026-06-21 22:00 UTC).
- Confirmation window: S_X..2024-02-29, S_X from the start rule below.
- Embargo: March 2024 trade dates (inside the first sealed chunk, never built into bars).
- Holdout-2: trade dates 2024-04-01..2025-03-31, bought in E.1 and sealed on arrival exactly as
  MES's was (the raw monthly chunks range=2024-03-01_2024-04-01 through
  range=2025-03-01_2025-04-01, each sealed in the download call after its byte check, oldest
  first), one sealed store per product, the same unlock log, the same REGISTRATION.md requirement.
- Holdout-1 (from trade date 2026-06-22): NOT bought in E.1 for any new product. Data that does not
  exist on the machine cannot leak; a registered final-read stage buys it later.
- Start rule per product (NULL_CRITERIA.md 4.1 generalized): V_ref,X = the median of the 14
  monthly medians (2025-04..2026-05) of the day-session one-minute volume of the vehicle's bars
  present; S_X = the first trade date of the earliest month M* from which every month through
  2024-02 has median day-session one-minute volume >= 0.25 V_ref,X; 0.15 and 0.40 descriptive; the
  earliest possible S_X is the first trade date with bars on or after 2019-05-06.
- Short histories (micros listed after 2019-05): the power check below decides. If the vehicle's
  own confirmation window is too short, E.2 may declare the full-size contract's bars as the price
  path (D2), and the start rule then runs on the full-size contract. Declared per exposure in E.2,
  before any confirmation read.
- Power check per member (D.1e Task 3 method, at eps_X): n_b from the member's research-window
  daily series (analytic, and the block-bootstrap simulation where they differ by more than 15%,
  the larger); a member whose n_b exceeds the days its window supplies is labelled
  "inconclusive by design" before confirmation (as C6 was), never tested for a null it cannot reach.
- Cross-product members: the confirmation window is the intersection of the legs' windows, where
  every leg, signal legs included, starts at its own S from the start rule (so MES as a leg starts
  2020-02-03). A trade date is excluded if it is a roll-blackout date of ANY leg the member reads
  (the union), and every leg a member reads must pass the member-level coverage check (D9). A short-
  history signal leg (MBT from 2021-05) may use the full-size contract's bars (BTC, not permitted,
  never traded) only if the power check fails and the user agrees; BTC is quoted free in E.1.
  (Rulings 02:22 PDT on CatalogWriter-K8's questions 1 to 4.)

**Reasoning.** Aligned windows make every cross-product member possible and make the program's
null statements comparable across products. The mined window stays the most recent, the
confirmation window the older history, as in D.1f. Not buying holdout-1 is strictly stronger than
buying and sealing it.

**Alternatives considered.** Product-specific windows (maximizes each product's history; breaks
cross-product alignment and the shared holdouts); a rolling walk-forward instead of one
confirmation block (more reuse of data, but every re-fit is a new look).

**User decides:** whether holdout-1 for new products is left unbought (proposed) or bought and
sealed like MES's; whether full-size bars may stand in for a short-history micro.

---

## D5. Multiple testing

**Rule (proposed).**
- Per cluster, two tiers, as in D.1f. Tier A (edge-eligible, the Holm family): every member that
  passes the cluster's screening session's pre-declared screen on the research window. The ML member
  takes the same screen, on its nested outer-fold estimate (D15.5), and joins Tier A only if it passes
  (ruling on review R-01, 2026-09-24: one reading, D15.10's). The screen: research-window mean net P&L > 0 and daily t >= 1.0 (per micro
  or per contract, zeros on no-trade days). Tier B (null side only): every other member.
- Holm within each cluster's Tier A at family-wise alpha_k = 0.05 / K, where K = the number of
  clusters with a non-empty Tier A in the program (at most 8). A Bonferroni split across clusters,
  Holm inside each, so the program-level family-wise error is at most 5% and each cluster session
  can reach its verdict on its own.
- Edge exists (unchanged from D.1f 3.2, per member): Holm rejection, then the composite screening
  verdict on the confirmation window (robust zero-edge gate plus both drift sub-checks), then
  DSR > 0.95 at the cumulative program N with the Sharpe variance over the cluster's Tier A
  confirmation-window daily Sharpes, daily t > 3.0 one-sided, CSCV PBO < 0.5 on 8 contiguous
  blocks. A passing member becomes a discussion item for a registered final read; nothing is
  registered by a cluster session.
- Program accounting beside every result: cumulative N (58 before Stage E; every screened member
  and grid point adds to it, section D15 for the ML members), DSR at N, PBO, and the per-cluster
  and program totals.

**Reasoning.** Eight cluster sessions will run at different times. A program-wide Holm could only
be applied after the last one, and one cluster's p-values would change another's verdict. Splitting
alpha equally across the clusters that have anything to test keeps the program-level promise and
lets each session finish. The screen is deliberately weak (an edge at ε would show t of roughly 5
or more on 300 research days, so it passes with near certainty) and exists only to keep noise out
of the Holm family; nothing is dropped from the null side.

**Alternatives considered.** Holm at 5% per cluster (program-level error near 34% with eight
clusters; a program claim from any cluster would be overstated); one program-wide Holm (couples
sessions); weighting alpha by cluster prior (defensible, but the weights would be judgments made
now with nothing to base them on); all members in Tier A as in D.1f (with about 120 trials the Holm
thresholds would bury a genuine edge; the screen costs nothing on the null side).

**User decides:** the alpha split (equal over active clusters); the screen (t >= 1.0 on the
research window).

---

## D6. The core port set of MES families

**Rule (proposed): three MES families, ported to every traded exposure, each one trial per
exposure, counted in N.**

Selection criteria, fixed before any Stage E data and without ranking MES members by their D.1f
results: (1) the family is defined only by the product's own session clock and own bars, so it
ports by substituting the product's day-session open O, close C and flat time F and its tick; (2)
at most one entry per product per day, so a larger tick relative to the product's moves does not
decide the result through cost alone (MES's high-frequency C3 and C6 trials were the most negative
members, -276 and -187 net ticks per micro per day); (3) market orders, no stops or targets; (4)
the three cover three different MES classes; (5) the mechanism has a published cross-asset or
generic basis in the program's logs.

| Port | MES family ported (class) | The rule on product P (O, C, F from the table below) | Why this family |
|---|---|---|---|
| CP1 intraday momentum | F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (C3; D.1 log A10 and A28) | Signal: sign of (close of the bar at O+29 min minus open of the trade date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in the signal's direction; zero signal, no trade. Exit: market intent on the first bar at or after C-2 min (fills at the next open). Both signal bars must exist with one instrument_id, else no trade. | the most replicated intraday mechanism across futures; the (a) form (overnight plus first half hour) is the literature's definition, chosen on that ground; (b) is not ported as a separate member. On a product with no overnight session (livestock) the trade date's first bar is the day open, so the signal becomes the first 30 minutes of the day session, which is the (b) form, by the same rule text (review R-03). MES record, corrected on review R-02: MES's confirmation tested the REVERSAL-signed F3.3 statistics (s = -1) and found them null; the momentum form ported here was negative on MES's mined window and is untested on MES's confirmation |
| CP2 opening-range breakout | B-H1 hold 75 (C2) | OR = high and low of the bars in [O, O+15 min). Entry: the first bar opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P; market intent in the break direction; one entry per trade date; no entry from C on. Exit: 75 minutes after the fill, or the engine's forced flatten at F if earlier. | the canonical unconditional breakout; a literal port (15-minute range, 4-tick buffer, 75-minute hold), only the clock and the tick change. Entry window amended 21:12 PDT (after CatalogWriter-K2's note): MES's rule had no latest entry but its day session ended 8 minutes before F; on products whose C falls an hour or more before F an unbounded window would admit post-settlement breaks the family never meant, so entries stop at C |
| CP3 prior-close location | H6 (C7) | Daily bar of day d from [O, C): O_d = open of the O bar, H and L over [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as Family H. CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, market intent on the O bar of day d. Exit: first bar at or after C-2 min. | a once-a-day daily-bar construction, fully specified in the frozen MES list, portable without any MES constant |

Every port trades q_c of the exposure's D2 vehicle and follows D9 (flat by F, trade-through for
any limit order, which none of the three uses). "4 ticks of P" in CP2 means 4 minimum price
increments of the exposure's most active contract (D1 table), in price units, fixed whatever
vehicle D2 chooses (ruling 21:52 PDT on CatalogWriter-K4's question: QM, QG, E7 and M6E have coarser
ticks than their full-size or micro siblings, and the rule must not change with the vehicle).
D6's text governs every port entry: a catalog entry that copied an earlier wording is read as the
current D6 text. A port is NOT re-written as a "new" member by any
cluster: a cluster mechanism that is the same as a port is logged as covered by it.

Families not ported, and why: A session clock (A-H1 to A-H4 are drift bets on the clock; on a
product without a documented drift they measure the research window's trend, which D.1 showed is
what their MES results were); C-H1 to C-H3 and C-H4 (high frequency; cost-dominated on thinner
products; C6 closed); D volatility-state gates (they condition a base strategy; the base strategies
are the ports and the cluster members); E calendar and events (each cluster writes its own
announcement members from its own literature, which is more specific than MES's E-H1); Family H
beyond H6 (five variations of one breakout; CP2 carries the unconditional breakout).

**Session table for the ports (CT; conventional CME day-session open and daily settlement time;
TO BE CONFIRMED against CME's published settlement procedures in E.2 before any bar is read, any
correction logged; F from D9):**

| Group | O | C | F |
|---|---|---|---|
| equity index (MNQ, M2K, MYM, NQ, RTY, YM) | 08:30 | 15:00 | 15:08 |
| NKD | 08:30 | 15:00 (to confirm; NKD's own settlement time may differ) | 15:08 |
| rates (ZT, ZF, ZN, TN, ZB, UB) | 07:20 | 14:00 | 15:08 |
| FX (all) | 07:20 | 14:00 | 15:08 |
| energy (CL, QM, MCL, NG, QG, MNG, RB, HO) | 08:00 | 13:30 | 15:08 |
| gold (GC, MGC) | 07:20 | 12:30 | 15:08 |
| silver (SI, SIL) | 07:20 | 12:25 | 15:08 |
| copper (HG, MHG) | 07:10 | 12:00 | 15:08 |
| platinum (PL) | 07:20 | 12:05 | 15:08 |
| grains (ZC, ZW, ZS, ZM, ZL) | 08:30 | 13:15 | 13:18 (session close 13:20) |
| livestock (HE, LE) | 08:30 | 13:00 | 13:03 (session close 13:05) |
| crypto (MBT, MET) | 08:30 | 15:00 | 15:08 |

**Count.** Three trials per traded exposure. With about 30 traded exposures, about 90 port trials.

**User decides:** the three families; whether CP1 should also carry the (b) form.

---

## D7. Stage E null criteria

**Proposed: docs/NULL_CRITERIA_E.md (draft, written 2026-09-23 20:55 PDT).** It generalizes
docs/NULL_CRITERIA.md, which stays frozen as the MES record. What changes and why:
- The statement unit is the cluster, with a per-exposure resolution table, instead of MES's class.
  Classes still appear as member labels; clusters are what the sessions run and what Holm spans.
- eps is per exposure (D3), and the daily series is in ticks per contract of the vehicle at the
  risk-matched size, keeping D.1e's R-1 lesson (each trip divided by its own quantity).
- A member declared "inconclusive by design" in the hashed list before the run (power, D4) is named
  as not covered and does not block the cluster's statement. Under MES rules one such member blocked
  its class; the exception is allowed only for a pre-run declaration, never after results.
- Tier A and Tier B (D5) replace MES's fixed 58-member Holm family; the edge conditions are
  otherwise unchanged (Holm, composite, DSR at cumulative N, t > 3.0, PBO < 0.5).
- The forbidden claims grow with the scope: no statement for any asset class, "CME futures", other
  sizes, accounts or firms.

**User decides:** the pre-declared "inconclusive by design" exception; the per-cluster unit.

## D8. Cost model per product

**Rule (proposed). The calibration rule is stated here, before any sample is bought.**
- Commission: Topstep's published round-turn total for the product (commission, exchange and NFA
  fees; reports/stage_e0_topstep_facts.json F3.7), for example MNQ $1.22, MCL $1.52, ZN $2.62,
  6E $4.22, GC $4.32, ZC $5.28. The CME increase effective the 2026-10-01 trading day (F3.6: MCL and
  MNG +$0.10 per side) is applied now, since any forward test starts after it: MCL $1.72, MNG $1.92.
- Slippage, one side, per contract, in ticks, per product and per 30-minute CT bucket of its
  trading hours, from the Databento mbp-1 sample on the five dates fixed at 20:10 PDT
  (2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11, 2026-04-15; full trade dates):
  s_b = the time-weighted mean, over the five dates, of the quoted half-spread (ask - bid) / 2 in
  ticks during bucket b; plus a depth term when the time-weighted median top-of-book size on the
  side a market order hits is below q_c: add (q_c - size) / q_c ticks (one extra tick for the part
  of the order beyond the top level). A bucket with quotes on fewer than 3 of the 5 dates takes the
  largest s_b of the product's other buckets. Nothing is smoothed or fitted.
- Round-turn cost at bucket b, in ticks: commission / tick value + s_entry + s_exit.
- tbbo is quoted as well; its trade-weighted effective half-spread per bucket is reported beside
  s_b as a check and is not used.
- Event-window cost (added 21:52 PDT after CatalogWriter-K4's questions): any fill in the half-open
  window [release, release + 30 min) after a scheduled major release that concerns the product (Topstep's release table, F6.4, plus the
  releases the product's catalog members name) pays, per side, the largest s_b of the product's
  buckets instead of its own bucket's. The five sample dates cannot calibrate release minutes for
  every product (none is an FOMC or USDA report day), so the rule is deliberately conservative there
  rather than extended with extra sample days.
- Early-era bias, as docs/NULL_CRITERIA.md 4.3: calibrated on 2025-26 books, the model understates
  costs in thinner earlier years. That is conservative for a null claim and not for an edge: any
  member that passes confirmation gets a period-appropriate cost re-check before discussion.

**Reasoning.** MES's model (commission plus a time-of-day half-spread table from two days of ticks,
about 2.11 ticks a round turn) is the template. At the program's sizes (one to a few contracts,
D2) the top of the book is the relevant depth, and the depth term covers the cases where it is not.
Five dates spread over a year give each bucket five observations of a quantity that is stable day
to day on liquid products; the rule has no free parameter to tune after the sample arrives.

**Known limitations.** Five dates is thin for a time-of-day table. All five are Wednesdays, EIA
crude release days, so energy's 09:30 CT bucket includes the release every time (conservative for
energy members, since spreads widen around it). No latency or adverse-selection model, as for MES.

**Alternatives considered.** mbp-10 (depth beyond the top level; several times the cost per day,
D.1e, and not needed at these sizes); an estimator from one-minute bar ranges (no book data needed,
but noisy and biased); a flat per-product cost (loses the time-of-day structure that matters most
for overnight and event-time members); more sample dates (the user may buy more; the quote is in
Task 2).

**User decides:** mbp-1 alone or mbp-1 plus tbbo; five dates or more.

## D9. The Topstep constraint set

**Confirmed from Topstep's pages on 2026-09-23 (reports/stage_e0_topstep_facts.md; quote ids in
brackets), and how the harness will encode each.**

1. **Flatten.** "All open positions and pending orders begin to automatically cancel at 3:10 PM CST.
   Avoid opening new positions after 3:08 PM CT — Risk Managers begin flattening at that time. It's
   still your responsibility to be flat by 3:10 PM CT." [F4.2] Encoded as F = 15:08 CT for every
   product that trades through 15:10 CT: no new position after F, every position closed by F.
   Grains trade "Monday-Friday: 8:30 AM - 1:20 PM CT" with an overnight session "7:00 PM - 7:45 AM
   CT" and a "CBOT Commodity Market Pause (Mon-Fri): 7:45 AM - 8:30 AM CT. No orders accepted during
   this window. TopstepX manual lockout is not available for CBOT positions held during this time"
   [F4.3, F4.5]: F = 13:18 CT, and no grain position may be held into the 07:45 pause (an overnight
   grain member exits by 07:43 CT). Livestock: "Monday-Friday: 8:30 AM - 1:05 PM CT" [F4.4]: F =
   13:03 CT. CME early-close days: F = 15 minutes before the early close (the rules engine's
   existing convention, from Topstep's Holiday Hours article as read in Stage A.1; the E.0 fetch did
   not find a holiday rule on the hours page, so E.2 re-reads the article and quotes it).
2. **Orders.** Market orders. "the market has to trade through your price - not just touch it"
   [F8.1]: any limit order is filled only when a later bar trades through its price.
3. **Trade rate and holding time** (program floor, fixed before the catalog): at most 20 entries per
   product per trade date; every position held at least 2 full minutes (no exit before the third bar
   after the entry fill); mean holding time over the research window at least 10 minutes, checked
   at screening. An entry whose earliest exit (the member's own exit or F) would come less than 2 full
   minutes after its fill, for example because the fill guard (5a) pushed the fill late, is skipped
   for that day (ruling 01:52 PDT on CatalogWriter-K6's question 5). Topstep's prohibited pattern is "usually hundreds or thousands of trades per day,
   with average durations measured in seconds, not minutes" [F7.3].
4. **Prohibited patterns** [F7.2]: "Running scalping algorithms designed to exploit unrealistic SIM
   fills; Making hundreds of rapid trades to take advantage of preferential queue position in SIM;
   Initiating reckless trades in gapped markets to profit from stray fills", exploiting the lack of
   SIM slippage on stops, tight brackets or auto-breakeven for favourable SIM fills. A member whose
   edge depends on any of these is excluded at design with the reason logged. The harness charges
   slippage on every exit, and no member uses stops or brackets.
5. **News.** "Topstep doesn't require you to flatten positions during economic releases - in SIM or
   Funded Accounts" [F6.1]; prohibited: "Purposefully trading your full Maximum Position Size
   directly into a scheduled major news event" [F6.3]. One rule covers the Combine and the XFA; no
   separate XFA rule is published. Encoded: every member's size is at most 1 lot-equivalent, half
   the XFA's starting 2-lot maximum, so no member ever trades full maximum position size, into news
   or otherwise. D2's size cap therefore tightens from 2 lots to 1 lot-equivalent.
5a. **Event-minute fill guard (harness rule, added 21:52 PDT).** No fill is simulated in the first two
   minutes after a scheduled major release that concerns the product: an intent whose fill would land
   in [release, release + 2 min) is filled at the open of the first bar at or after release + 2 min.
   A bar simulator cannot represent a market order filled in the release minute, and the guard keeps
   every member (ports included, for example CP1 on energy, whose entry at C-30 = 13:00 CT meets the
   FOMC statement) out of fills the model would get wrong. Holding a position through a release is
   unaffected (point 5 governs size).
6. **Position limits and weightings.** "$50K XFA, 2-lot Scaling Plan: 2 Minis, OR 20 Micros, OR any
   combo equal to 2 Minis" [F5.2]; "Micro Silver (SIL): 5:1 ratio vs. Silver (SI); counts as 2 of
   any other micro. Micro Bitcoin (MBT): Capped at mini-equivalent lot sizes, not standard micro
   scaling. Micro Ether (MET): Capped at mini-equivalent lot sizes" [F5.4]; "Your max contracts do
   not increase mid-session" [F5.5]. Encoded as lot-equivalents per contract: minis 1, micros 0.1,
   SIL 0.2, MBT 1, MET 1. The full XFA tier table is an image on Topstep's page (not published as
   text); the rules engine's tiers (2 lots, 3 at $1,500, 5 above $2,000) stay as encoded and
   unchanged, and point 5's cap keeps every member inside the first tier.
7. **Price-limit proximity.** Prohibited Conduct lists "Holding a position within 2% of a product's
   price lock limit" [F2.1]. Topstep's own definition (help.topstep.com/en/articles/8284225, "Staying
   Outside the 2% Price Limit Zone", May 29, 2026, fetched by the lead 2026-09-24 01:46 PDT): "Price
   limits are calculated from the previous day's settlement price"; "Stop trading when % Net Change
   approaches the limit minus 2%"; "Stop trading above: Settlement × (1 + Price Limit% − 2%)"; "Stop
   trading below: Settlement × (1 − Price Limit% + 2%)". So "within 2%" is 2 percentage points of
   price inside the limit, measured from the prior settlement (for a limit set in price units, such as
   grains, Price Limit% = limit amount / prior settlement). Encoded: no entry, and an immediate exit,
   while the price is beyond either stop level. The exit this forces is EXEMPT from the event-minute
   fill guard (5a) and fills at the next bar's open with the event-window cost: the conduct rule
   outranks the fidelity rule (ruling 01:52 PDT on CatalogWriter-K6's question 3). Inputs: prior
   settlements per contract (Databento's statistics schema, to be quoted in E.1; if not bought, the
   volume-weighted price of the one-minute bars in the product's settlement window as the proxy) and
   CME's limit tables by product and period (grain limits are reset periodically), built in E.2.
   Equity-index limits (7% overnight, per the same page) bite on days like March 2020.
   Locked markets (review R-08): when the bars show the market locked at the limit on the side an exit
   must trade (a long exiting at limit-down, a short at limit-up), the D9.7 exit, or any other exit
   including the forced flatten, is NOT filled until a later bar trades through the limit price; the trip
   is flagged, and the count of flagged trips is reported per member. A next-open fill against a lock
   would be a fill "improbable in live markets" (F7.2) and would truncate losses.
8. **Starred products.** The permitted-products page marks MES, MNQ, M2K, MYM, M6E, M6A, 6M, MBT,
   MET, MCL, MGC and SIL with "*" and says "See Prohibited Conduct for restrictions on specific
   products marked with an asterisk (*)" [F1.9]. The follow-up (F12) found the nearest referent in
   Topstep's "Risk Adjustments: High Risk/High Volatility" article, which names MES, M2K, MYM, MNQ,
   MGC, SIL, MCL, MHG, MBT and MET (points 11 and 12 below encode it). M6E, M6A and 6M are starred but
   named on no page found: their restriction stays unresolved, flagged for the user (6M is out by D1).
   Ruling (01:40 PDT, on CatalogWriter-K3's question): a starred contract whose restriction is still
   unresolved at E.1 is NOT a D2 candidate unless the user clears it; EUR and AUD then trade 6E and 6A
   at one contract.
11. **Volatility position caps** [F12.1c]: "During extreme volatility, we may temporarily tighten
   position limits on affected products. ... Energies Restriction - RBOB Gasoline (RB) = 3/6/9;
   Heating Oil (HO) = 3/6/9; Crude Oil (CL) = 3/6/9; Micro Crude Oil (MCL) = 30/60/90; E-Mini Crude
   Oil (QM) = 3/6/9. Metals Restriction - Gold (GC) = 3/6/9; Micro Gold (MGC) = 30/60/90; Silver (SI)
   = 0; Micro Silver (SIL) = 2/4/6; Copper (HG) = 0; Micro Copper (MHG) = 2/4/6; Platinum (PL) = 0"
   (50K/100K/150K). Encoded: every size stays within the 50K figure at all times (so the member is
   deployable whether or not a restriction is in force): SIL and MHG at most 2 contracts, MCL and MGC
   at most 10 (the 1-lot cap binds first), CL, QM, RB, HO and GC at most 1 (point 5 binds first).
   SI, HG and PL can be set to 0 at Topstep's discretion: D2 prefers SIL and MHG for silver and copper
   whenever they are candidates, and platinum (no micro) is flagged "may be suspended in volatile
   periods" for the user.
12. **CPI window** [F12.1e]: "Ahead of Consumer Price Index (CPI) releases ... Minis (ES, RTY, YM, NQ,
   NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute window
   surrounding the release (5 minutes before, 5 minutes after). Micros (MES, M2K, MYM, MNQ, MGC, SIL,
   MHG): Opening transactions limited to 1, 3, 6, 9, and 15 contracts for the $25K, $50K, $100K,
   $150K, and $250K account sizes, respectively, during the window." Encoded: no member opens a
   position in [CPI - 5 min, CPI + 5 min] on NQ, RTY, YM, GC, SI, HG or PL (an entry whose fill would
   land there is skipped for the day, not deferred); on MNQ, M2K, MYM, MGC, SIL and MHG an opening
   fill in the window is at most 3 contracts. The CPI release calendar (BLS, public, with history) is a
   harness input. The restriction is stated as SIM-wide; it applies to the Combine and the XFA.
13. **Holidays** [F12.3a]: "All account types must close positions 15 minutes before any early
   close" (confirms point 1's early-close rule).
9. **"Unfair technology - using software, AI, ultra-high speed systems, or mass data entry to gain
   an unfair advantage"** [F11.4]. The program's bot is ordinary automated trading through the API,
   which Topstep allows ("Custom automated strategies and bots are allowed via the TopstepX /
   ProjectX API, subject to standard platform rules" [F10.4]); the ML members are frozen models
   making at most 20 decisions a day. Flagged for the user in case Topstep reads "AI" more broadly.
10. **Deployment notes** (no effect on E.0's work): trading must originate from a personal device,
    no VPS, VPN or remote server [F10.1, verbatim in F12.2e: "The line is order transmission: your
    server can watch and record, but it cannot trade."]; no sandbox, test on a Practice account
    [F12.2f]; bots are subject to "our prohibition on highfrequency trading (HFT)" [F12.2f]. New and
    material for the program's end state: "Live funded accounts are not allowed to trade through the
    ProjectX API. The API Gateway is built for the simulated environment and isn't available on Live."
    [F12.2g] The bot can run on the Combine and the XFA only; a call-up to the Live Funded Account
    ends automated trading on that account (the program already models LFA call-up as terminal,
    docs/DECISIONS.md).

**Program-wide trade-rate and holding-time floor (proposed).** Every member, on every product:
(a) at most 20 entries per product per trade date; (b) every position is held for at least 2 full
minutes (no exit order before the third bar after the entry fill); (c) mean holding time over the
research window of at least 10 minutes. A member whose rule can breach (a) or (b) is re-written or
excluded at design; (c) is checked at screening, and a member failing it is excluded before
confirmation with the reason logged. Reasoning: Topstep's prohibited pattern is "hundreds or
thousands of trades per day, with average durations measured in seconds, not minutes"; 20 a day
held for minutes is an order of magnitude and more away from it, and every D.1 family except the
C3 and C6 high-frequency trials fits inside it.

**Member-level coverage check.** Each member's own trading window must show ohlcv-1m coverage of
at least 0.95 on the research window for its vehicle before it is screened (E.2 computes it);
otherwise it is excluded before screening with the reason logged.

## D10. The calendar

**Rule (proposed).**
- One calendar per product group, not per product: equity index and crypto; interest rates; FX;
  energy; metals; grains; livestock. Each covers every CME trade date from 2019-05-01 to 2026-06-19
  with holidays, full closures, early halts and early closes, and each entry cites CME's own
  published Globex holiday schedule for that group and year (the D.1f CalendarChecker route:
  cmegroup.com through Wayback or Firecrawl, every quote checked by script as a verbatim substring),
  graded as data/cme_calendar.py grades its entries.
- The equity group reuses data/cme_calendar.py after the carried fix below; the other groups are
  new modules with the same interface and the same completeness assertion in the bar builder.
- Session tables per group, including the grain session (19:00-07:45 and 08:30-13:20 CT on
  TopstepX) and livestock (08:30-13:05 CT), with any change of CME session hours during 2019-2026
  found from CME notices and dated.
- Validation (D.1f step 4b, per group): the observed-holiday check against the bars, on research
  and confirmation dates only. Holdout-2 dates (2024-04-01..2025-03-31) cannot be checked against
  bars; their entries rest on CME's schedules alone and say so.
- Early-close days: F = the early close minus 15 minutes (D9.1), per group.

**Carried from D.1f (must be fixed in E.2, before any holdout-2 chunk is sealed for any product):**
data/cme_calendar.py lists 2024-07-04 as a full closure, while CME's trading-hours capture for ES
gives a 12:00 CT halt (reports/stage_d1f_calendar_check.md), the same error D.1f corrected for
2019-2023. No 2024 entry after 2024-02-29 has ever been checked against bars. With the fix,
MES's holdout-2 has 259 calendar trade dates, not 258.

**Crypto regime change (verified by CatalogWriter-K7 from CME's own release of 2026-06-01, K7-036):**
CME's bitcoin and ether futures have traded 24/7 since 2026-05-29. The crypto calendar therefore
splits at that date: before it, the equity-style week (Sunday 17:00 CT open, Friday 16:00 CT close);
from it, continuous trading, with weekend trading assigned by CME to the next business day, which
the bar builder follows (ruling 02:10 PDT). TopstepX's own session is unchanged (weekday close 15:10
CT, closed Friday 15:10 to Sunday 17:00 CT), so the program still cannot hold or trade over the
weekend. The research window's last three weeks fall in the new regime; the confirmation window
(MBT from 2021-05) lies wholly in the old one, and a K7 statement must say it describes that regime.

**Why per group.** CME's holiday schedules differ by asset class (for example interest-rate and
equity products can halt at different times on the same holiday, and grains close fully on days
when equities trade a short session); one calendar for every product would misplace sessions for
whole groups, and the D.1f failure shows a wrong entry silently shifts roll blackouts, flatten
times and daily-bar completeness.

## D11. What Stage E.2 must build

Before any Stage E data is read, each with known-answer tests, under the same freeze discipline as
D.1f (a manifest committed before the purchase of the confirmation history):
1. **Rules engine, per product** (rules/ is read-only for E.0; this is E.2's list): tick size and
   tick value per product; lot-equivalent weights (minis 1, micros 0.1, SIL 0.2, MBT 1, MET 1);
   the 1-lot-equivalent member cap (D9.5); per-group flatten times (15:08 CT; grains 13:18 with the
   07:45-08:30 pause; livestock 13:03; early closes minus 15 minutes); the price-limit proximity
   rule (D9.7) with per-product limit tables; the per-product commission table (D8). The 50K XFA
   only: 100K, 150K and the Daily Loss Limit option stay out of scope until an edge exists.
2. **Cost models per product** (D8): the calibration code, run once on the sample, frozen.
3. **Calendars per group** (D10), with the 2024-07-04 fix.
4. **Multi-product data pipeline**: the purchase path generalizing data/pull_mes.py (monthly chunks,
   gate, ledger, oldest first, holdout-2 chunks sealed in the download call, one sealed store per
   product, the same unlock log); symbology and roll boundaries per product (monthly-expiry products
   such as CL roll twelve times a year, so the roll blackout removes about three times as many dates
   as MES's); vendor-degraded dates per product; bar builds per product with the start rule (D4).
5. **Cross-product alignment**: a shared minute grid in UTC with explicit missing-bar handling (no
   forward fill into a signal; a member whose leg has no bar at a decision time does not trade).
6. **The screening runner, per product**: screen_candidate generalized to take the product's rules,
   costs, calendar and ε; the member-level coverage check and trade-rate floor (D9); the power
   check (D4).
7. **The ML pipeline** (D15), with its leakage tests, before any fit.
8. **The funnel re-derivation per exposure** (D3), compute only.
9. **Leakage canaries per product**, extended to cross-product members (a planted future bar in one
   leg must not change the other leg's decisions).
10. **The vehicle choice** (D2): risk and cost per admissible contract on the research window,
    frozen before any member runs.
11. **The two carried test fixes** (D14).

## D12. Session plan

**Proposed sequence.** ETAs are from this program's own sessions (D.1f run: 1.5 h for a 58-member
confirmation; D.1f build: one long session for one product's harness; E.0 itself); usage is the
rough token scale of comparable sessions (D.1f run 75M, mostly the lead), stated as a range.

| # | Session | What | ETA | Usage (tokens, rough) |
|---|---|---|---|---|
| 1 | E.1 freeze and first purchase | apply the user's changes; hash the catalog, this design and docs/NULL_CRITERIA_E.md; buy the research window of every admissible contract and the mbp-1 sample (D13 step 1) | 3-4 h | 30-50M |
| 2 | E.2a build | per-product rules (D11.1), group calendars with CME citations (D10, the largest single job: 7 groups x 7 years), cost calibration (D8), data pipeline and bar builds, vehicle choice (D2), funnel re-derivation (D3, compute) | 8-12 h | 80-120M |
| 3 | E.2b build and second purchase | generalized screening runner, ML pipeline and its leakage tests (D15), canaries, freeze manifest; buy the confirmation and holdout-2 history of the chosen vehicles, sealing holdout-2 on arrival (D13 step 2) | 8-12 h | 80-120M |
| 4-17 | one screening and one confirmation session per cluster | screening: members through screen_candidate on the research window, ML tuning, Tier A/B, power check, list hashed. Confirmation: the list on the confirmation window, independent Fable check, statements | screening 3-5 h, confirmation 2-3 h | 40-80M each |

**Cluster order, by distance from MES's drivers:** K4 energy and K5 metals first, then K2 rates, K3 FX
and K6 agriculture, then K7 crypto, then K1 equity-index siblings last (closest to the closed MES
exposure); K8 after the clusters whose products its members use. About 20 sessions in total. Each
cluster's two sessions are independent of the others' results (D5's alpha split), so the order can
change without re-planning. Two clusters are thin after the catalog: K1 has only 2 new members beside
its 9 port trials, which sit close to the closed MES record, and K7 trades one exposure (MBT) in a
regime that changed on 2026-05-29. The user may merge or drop their sessions; nothing else depends on
them except K8 members that read their bars (bought anyway as legs).

## D13. Spend plan

**Quotes (Task 2, all free, 5,050 quote events at $0.00 in ledger/databento_spend.jsonl under
stage-E.0-2026-09-23; reports/stage_e0_quotes.{md,json}).** ohlcv-1m, 2019-05-01 to 2026-06-21, all 50
products: **$351.10** (K1 $69.13, K2 $48.56, K3 $90.41, K4 $50.15, K5 $53.71, K6 $31.85, K7 $7.28).
Calibration sample, 5 full trade dates: mbp-1 **$52.56**, tbbo **$32.19**. 158 quotes failed, all for
months before a micro existed (MCL before 2021-06, MNG before 2023-10, MHG before 2022-04, MBT before
2021-04, MET before 2021-11: "None of the symbols could be resolved"); they cost nothing and no data
exists for them.

**Proposed: buy in two steps, only what the design uses.** For the 31 traded exposures (D1), leaving
out NKD, 6M, MET and ES (MES bars, already owned, serve as the S&P leg on non-holdout dates):

| Step | Session | What | Quoted |
|---|---|---|---|
| 1 | E.1 | research window 2025-04-01..2026-06-21 of every admissible contract (needed for D2's vehicle choice) | $58.42 |
| 1 | E.1 | mbp-1 calibration sample, 5 dates, every admissible contract (D8) | $46.35 |
| 1 (optional) | E.1 | tbbo sample, the cross-check | $27.58 |
| 2 | E.2b | 2019-05..2025-03 history (confirmation window plus the 13 holdout-2 chunks, sealed on arrival) of the ONE chosen vehicle per exposure (range: cheapest to dearest contract per exposure) | $170.39-195.55 |
| | | **Total without tbbo** | **$275.16-300.32** |

Per cluster (step 1 research + step 2 range + mbp-1): K1 $9.31 + $22.11-22.53 + $26.59; K2 $8.06 +
$40.50 + $5.26; K3 $14.24 + $41.25-49.34 + $4.18; K4 $9.61 + $15.65-25.21 + $2.86; K5 $10.37 +
$21.24-28.34 + $5.49; K6 $5.32 + $26.52 + $0.77; K7 $1.49 + $3.11 + $1.20. Buying everything for every
admissible contract instead would be $326.74 plus samples.

**Caps (proposed).** Per session: the quote of that session's request set plus 10%, fixed in the
prompt before any purchase (E.1: about $115, or $146 with tbbo; E.2b: the chosen vehicles' quote plus
10%). Per request: $3.00 (the largest single request is one mbp-1 day of MNQ, about $2.7; the largest
monthly ohlcv-1m chunk is about $0.12). The gate refuses anything above either cap, as for D.1f.

**The user must act before E.1 can buy anything.** data/config.py's SHARED_ACCOUNT_CAP_USD is
$120.00 with $91.592247 already spent, so $28.41 of headroom remains; step 1 alone is $104.77. The cap
has to rise to at least about $400 for the whole plan (spent $91.59 + up to $300.32 + margin), and the
Databento account (about $33 of credit left) needs funding. E.0 did not change any cap.

**Cheaper alternatives the user can choose.** (a) Skip tbbo (already the proposal). (b) Buy each
cluster's step-2 history just before its confirmation session instead of all in E.2b: same total,
spread over time, and nothing is bought for a cluster the program never reaches. (c) Reduce the mbp-1
sample for the equity-index micros (MNQ's five days cost $13.46), at the price of a thinner cost model
for the product most likely to be traded.

## D14. Carried items from D.1f

| Item | What | Fixed in |
|---|---|---|
| tests/test_d1f_calendar_build.py::test_2019_2024_quotes_are_verbatim_from_the_extraction | fails since commit 14c1007: the five corrected Independence Day entries quote CME's time schedules from reports/stage_d1f_calendar_check.json, while the test pins every citation to the build's extraction file | E.2: point the test at both extraction files (test edit only) |
| tests/test_d1f_calendar_build.py::test_confirmation_build_end_to_end | fails in every session after the D.1f build, because it asserts that the real confirmation parquet does not exist | E.2: skip when the real parquet exists (test edit only) |
| 2024-07-04 in data/cme_calendar.py | listed as a full closure; CME gives a 12:00 CT halt | E.2, calendar work (D10), before any holdout-2 read |
| 2019-07-03 and 2023-07-03 grades | CME-confirmed 12:15 CT closes still graded "inferred" | E.2 calendar review |
| D.1f harness-freeze manifest | E.0 appended the E.0 session constants to data/config.py, so `d1f_freeze_check()` now reports config.py changed and data/quote_universe.py unlisted. D.1f is complete and D.1g will not run, so nothing depends on that manifest | E.1 writes Stage E's own manifest; the D.1f one stays as the record of D.1f |

Both failing tests were confirmed again in E.0 (full suite: 940 passed, 1 xfailed, exactly these
2 failed; QuoteCoder-OpusHigh, 2026-09-23).

---

## D15. The machine-learning member protocol (common to all eight clusters)

Written first, before any CatalogWriter wrote an ML entry. The CatalogWriter of each cluster fills
in only: the traded vehicle, the products the features read, the cluster features (with their
research-log references and availability timestamps), the decision window and the horizon h from
the menu below. Everything else here is common and fixed.

**Purpose.** Test whether a flexible model finds an edge the hand-written members miss, without
turning the program into an unaccountable search: one model per cluster, a grid listed in full, a
fixed selection rule, one refit, then frozen before the confirmation window is touched.

**D15.1 Model type.** Gradient-boosted decision trees, LightGBM (not in uv.lock today; E.2 adds
lightgbm and its scipy dependency, pinned), regression objective (L2). Why trees and not deep
networks: the training data is the research window only, about 300 trade dates; at one decision
every h minutes in a session window that is a few thousand noisy, weakly dependent rows. Shallow,
heavily regularized trees are the flexible model that sample can support; a neural network would
have more parameters than the data has independent observations.

**D15.2 One traded vehicle, one position at a time.** The ML member trades ONE vehicle (chosen by
the CatalogWriter with a reason: normally the cluster's exposure most supported by its research
log, subject to D1 and D2). Its features may read any product of its own cluster (K8: the products
its logged mechanisms name). Size q_c from D2. At most one open position. This keeps it one trial,
one daily P&L series, one position inside the XFA limit.

**D15.3 Decision times, horizon and target.**
- The CatalogWriter picks one horizon h per cluster from the menu {15, 30, 60, 120} minutes, with
  a reason traced to the cluster's research log (for example the horizon over which a logged
  announcement response or fix effect plays out). No grid over h.
- The CatalogWriter picks one decision window [W0, W1] inside the vehicle's trading hours, with
  W1 + h <= F (the flat time). Decision times: t_j = W0, W0 + h, W0 + 2h, ..., while t_j + h <= W1 + h.
  Positions therefore never overlap.
- Target: y_j = open of the bar at t_j + h minus open of the bar at t_j + 1 min, in ticks of the
  vehicle: the gross move of a long entered at the first bar after the decision (the engine's
  next-open fill) and exited h minutes later. The program's cost enters through the trade rule
  (D15.6) and every evaluation is on net P&L after the full cost model (commission plus the
  calibrated slippage table at q_c), so what is predicted and scored is the forward return net of
  cost at the fill convention the engine uses.
- Rows: every decision time in the research window, excluding roll-blackout dates,
  vendor-degraded dates, early-halt dates, and any t_j whose target window would pass F or lacks a
  bar at either end.

**D15.4 Feature rules.**
- At most 12 features per cluster: the 5 common base features below plus at most 7 cluster
  features.
- Every cluster feature is traced to a logged mechanism in the cluster's research log (registry id
  and passage number), states its exact formula, and states its availability timestamp. A
  feature is computed only from bars whose close time is <= t_j, from calendars known in advance,
  or from released data after the release's published timestamp (never a settlement or report
  published after t_j).
- No feature, scaling constant, bucket edge or normalization is estimated on the confirmation or
  holdout windows. Any constant is either a fixed literal written in the catalog or estimated on
  the research window's training rows only (inside each fold, on that fold's training rows); any
  rolling quantity uses the product's own trailing bars ending at or before t_j.
- Missing input at t_j (no bar in a lookback, instrument change inside a lookback) means no trade
  at t_j; there is no imputation.
- Common base features (the core port mechanisms, D6, and D.1's logged families):
  B1 return over the 30 minutes ending at t_j, in ticks (D.1 family C);
  B2 return from the trade date's first bar to t_j, in ticks (D.1 A10 / A28, intraday momentum);
  B3 minutes since the vehicle's day-session open O (D.1 family A, session clock);
  B4 mean absolute day-session move over the 20 complete trade dates before the current one,
     in ticks (D.1 family D, volatility state);
  B5 close-location value of the prior complete trade date (D.1 Family H, H6).

**D15.5 Tuning: nested walk-forward inside the research window only.**
- Blocks: the research window's eligible trade dates split into 6 contiguous blocks of equal
  size (the last block takes the remainder).
- Inner walk-forward (selection): for k = 3..6 train on blocks 1..k-1, validate on block k.
  Purge every training row whose target window overlaps a validation row; embargo one full trade
  date before and after each validation block (at least h, and at least the longest lookback of
  any intraday feature). Selection metric: mean over the validation folds of net P&L per trade
  date, in ticks per contract per day with zeros on no-trade days, under the D15.6 trade rule.
  Eligibility: at least 30 validation trades in total. Tie-break: fewer trades per day, then
  smaller num_leaves, then fewer boosting rounds.
- Outer loop (reporting only): for k = 4..6, run the inner selection on blocks 1..k-1 alone (its
  own inner folds), refit the selected configuration on blocks 1..k-1, score block k. The three
  outer scores are the member's honest research-window estimate, the figure its screen uses (D5).
- Final: run the inner selection on all six blocks, refit the selected configuration ONCE on all
  eligible research-window rows, save the model file with its sha256, and freeze it. Nothing is
  re-fit after this.
- The grid, listed in full (48 configurations): num_leaves in {4, 8}; boosting rounds in
  {100, 300}; min_data_in_leaf in {50, 200}; lambda_l2 in {1.0, 10.0}; trade-threshold multiple m
  in {1.0, 1.5, 2.0}. Fixed: learning_rate 0.05, feature_fraction 0.8, bagging_fraction 0.8,
  bagging_freq 1, max_depth -1, objective regression, deterministic true, num_threads 4,
  seed = bagging_seed = feature_fraction_seed = data_random_seed = 20260923. No early stopping.
- The whole grid's fold results are written to disk and reported beside the member.

**D15.6 Trade rule.** At t_j compute the features; y_hat = model(features). c = the vehicle's
modelled round-turn cost in ticks at q_c for t_j's time-of-day bucket (D8). If y_hat >= m c: BUY
q_c with a market intent (fills at the next bar's open); if y_hat <= -m c: SELL q_c; otherwise flat.
Exit with a market intent on the bar at t_j + h - 1 min (fills at the open of t_j + h), or the
engine's forced flatten at F if earlier. No stops, no targets, no pyramiding, at most one position,
inside D9's floor by construction (h >= 15 minutes; at most (W1 - W0)/h + 1 entries a day, which
the CatalogWriter keeps <= 20).

**D15.7 Leakage controls (E.2 builds and tests them before any fit).**
- Feature-timestamp validator: each feature value carries its availability time; any value
  available after t_j raises. A planted-future canary (a feature equal to y_j, and one equal to the
  next bar's close) must be rejected by the validator.
- Perturbation test: replacing every bar after t_j by random values leaves t_j's features and
  y_hat unchanged.
- Fold test: no training row's target window overlaps any validation row; embargo respected;
  training rows never include a date outside the research window.
- Window test: the frozen model's training set contains no trade date before 2025-04-01, none in
  2024-03-01..2025-03-31, none on or after 2026-06-22 (asserted on the saved row index).
- The existing leakage canaries (tests/test_leakage_canaries.py) are extended to run the ML
  member's strategy wrapper through the engine.
- Seeds fixed as in D15.5; the model file's sha256 is recorded before the confirmation window is
  read, and the confirmation run refuses on a different hash.

**D15.8 How it counts in N.** At confirmation the ML member is ONE trial per cluster (one frozen
model, one daily P&L series). The 48-configuration grid was searched on research data the
confirmation window never saw, so it does not inflate the confirmation test; it is reported beside
the member, and in the screening session's own research-window accounting the grid counts as 48
(so a research-window DSR for the ML member is computed at N_screen + 48, not at + 1). Program N
at confirmation: +1 per ML member, 8 at most.

**D15.9 Compute.** Per cluster about 48 x 4 inner fits plus 3 x 48 x 3 outer-loop fits, about 600
fits of a few thousand rows and at most 12 features: a few seconds each, about 15 to 30 minutes per
cluster including feature building, one process, nice 10, under 2 GB, resumable (every
configuration's fold results appended to a JSONL and skipped on restart). One cluster at a time,
never alongside another heavy job.

**D15.10 What the CatalogWriter must write in the ML entry.** ID K#-ml-01; traded vehicle and
reason; products read; the cluster features (up to 7): name, exact formula, source (registry id,
passage), availability timestamp; decision window [W0, W1] and h with reasons; expected rows in the
research window and expected entries per day (<= 20); the falsification condition (the standard
one: UCB95 of mean net daily P&L per contract below eps at >= 80% achieved null power on the
confirmation window counts against it; failing the screen puts it in Tier B); the Topstep check.
It does not choose the model type, the grid, the selection rule or the trade rule.

**User decides:** trees versus another model type; the grid; counting the ML member as one trial.
