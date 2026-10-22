# Stage E.28 Part B: schema decision (B1) and measurement spec (B2)

Written by the lead (Opus 5.5, xhigh), 2026-10-21: drafted from 15:15 PDT, parameter block filled at 16:10 PDT for Topstep QG
and re-filled at 16:41 PDT for Topstep QM after RankingReviewer's RR-01 and the lead's rulings v2 moved QG below the Layer
1 gate (reports/stage_e28_briefs/A3_ranking_table.md, primary rank 1 = Topstep QM; the QG version is kept as
reports/stage_e28_briefs/B_spec_v1_QG.md).
Reviewed by SpecReviewer-FableXHigh (reports/stage_e28_briefs/R_spec.md, GO WITH FIXES); every required and recommended
fix applied at 16:34 PDT; this version is hashed and frozen before any quote, balance check or download. The analysis runs only this spec.
No rule is tested, nothing is selected, nothing is registered, and N stays 538.

## 0. Parameters (filled from the top pair of reports/stage_e28_ranking.md)

| Parameter | Value |
|---|---|
| Contract (ROOT) | QM (NYMEX E-mini crude oil, 500 barrels; Databento symbol QM.v.0) |
| Firm of the top pair | Topstep (50K Trading Combine, Standard path) |
| Tick size / tick value (USD) | 0.025 USD per barrel / 12.50 |
| Matching algorithm | FIFO (tag 1142 = F) for QM outright futures: CME Globex Product Reference Sheet, Wayback snapshots 2024-02-26 (row 309) and 2023-06-22 (row 315), saved by SpecReviewer (pages/REV_spec/), read by the lead with work/lead/lead_xls_rows.py: "E-mini Crude Oil Futures, QM, CL, Outright, Yes, Note 4, 0.025, 12.5, F". QM is implied-eligible; Databento's mbp-1 is the outright (direct) book, without implied liquidity |
| Fee per side in ticks (FEE_SIDE) | Primary 0.1368 (Topstep's sourced 3.42 USD per round trip for QM / 2 / 12.50). Conflict flagged by EconCoder: a Topstep page gives a 3.70 USD per lot simulated Combine fee (RankingReviewer RR-02: the per-product fee governs); net markouts are also reported at 0.296 tick per side (3.70 / 12.50), the conservative reading |
| sigma_1m in ticks (SIGMA1M) | 2.520 (derived from CL under OC-1: CL's 6.30 ticks x 0.01 / 0.025) |
| Firm's simulated fill rule (SIMRULE) | trade_through_only (TopstepX: "the market has to trade through your price - not just touch it", docs/DECISIONS.md:36-38) |
| Latency (assumption) | 50 ms join and cancel, fixed; a retail path may be 60-120 ms (R_spec.md RS-11); not varied |
| Request end | 2024-02-29T22:00:00Z exclusive (16:00 Central, the end of CME trade date 2024-02-29; no record of trade date 2024-03-01) |

## 1. B1, the schema decision

The pilot measures, for a simulated 1-lot resting limit order: whether it fills under the conservative rule of
section 3, how long it waits, and its markouts at 1, 10 and 60 s against the mid. That needs, at every moment:
the best bid and ask and their displayed sizes (the queue ahead at join; the mid for markouts; the spread for the
one-tick-inside placement), and every trade with its price, size and aggressor side (the volume traded at our price
after we join, and any trade through our price). It does not need individual order identities, because the rule
deliberately ignores cancellations ahead of us (it assumes the whole displayed queue ahead must trade first, which
is conservative).

- mbo: needed only to reconstruct exact queue position order by order. The conservative rule does not use it. Not
  chosen (most expensive).
- mbp-10: the same top-of-book and trade information as mbp-1 plus nine more levels of depth. Depth is not used by
  any measurement here. Not chosen (more expensive than mbp-1; depth features belong to a later, separately
  purchased discovery set).
- tbbo: one record per trade with the book just before it, and nothing between trades. The queue at a join time that
  is not a trade time, and the mid at fixed clock horizons, are not observed. Not sufficient.
- **mbp-1: chosen.** Every top-of-book change and every trade, with exchange timestamps. It supports the fill rule,
  queue times and markouts for orders at the touch and one tick inside. It is the cheapest schema that does.

Minimum span inside 2023-11-01..2024-02-29 (arithmetic in section 6, filled with the contract's numbers).

## 2. Data, sessions and exclusions

- Dataset GLBX.MDP3, schema mbp-1, the contract's volume-based continuous front contract (Databento continuous symbol
  ROOT.v.0, the same convention as the program's ohlcv-1m store). The instrument behind v.0 on each trade date is
  logged. Trade dates on which the v.0 instrument changes, and the trade date after, are excluded (roll days).
- Trade date: the CME Globex trade date (17:00 Central of the previous calendar day to 16:00 Central). CME holidays
  and early-close dates (the repo's CME calendar) are excluded.
- Sessions, by America/Vancouver clock time: MAIN = 06:30-13:00; OVERNIGHT = the rest of the trade date. The first
  and last 5 minutes of each session, and the daily maintenance halt, are excluded from placements.
- The book is the outright book only (mbp-1 excludes implied liquidity); trades with no aggressor side (side N:
  implied-involved or opening trades) are counted per date and never add to V(t) or trigger a fill.
- Data checks before any statistic: records sorted by ts_recv then the exchange sequence, with ts_event (made
  non-decreasing, inversions counted) as the time axis; records with bad-data flags
  dropped (counted); moments with a crossed or locked best bid and ask, or with an empty side, take no placements and
  stop markout clocks (counted); a trade date with a gap above 60 s in MAIN-session records is excluded (counted).

## 3. B2, the measurement spec

Placements. On a clock grid every 5 minutes (xx:00, xx:05, ...) inside each session, two virtual orders are created,
one buy and one sell, each of size 1:
- T (at the touch): buy at the best bid, sell at the best ask;
- I (one tick inside): only when the spread is at least 2 ticks: buy at best bid + 1 tick, sell at best ask - 1 tick.
Virtual orders never interact with each other or with the book (no market impact is simulated).

Latency. An order created at grid time g joins the book at j = g + 50 ms, using the book state at j. A cancel takes
effect 50 ms after it is decided; fills inside that window count.

Fill rule (conservative; never a fill on a touch alone). At join the order goes to the back of the visible queue:
Q_ahead = the displayed size at its price in the book state at j (for T, the size at the best on its side; for I,
0, since the level did not exist). After j, V(t) is the cumulative volume of trades printed at exactly its price
with the aggressor on the other side (sell-aggressor trades for a buy order, buy-aggressor trades for a sell
order). The order fills at the first trade that makes V(t) >= Q_ahead + 1, or at the first trade with a defined aggressor
(side A or B, never N) printed at a price strictly through its price (below a buy's price, above a sell's price),
whichever comes first. Fills are reported by trigger (queue or through) and by side. The fill price is
the order's limit price; the fill time is that trade's timestamp. A quote that moves to or through the order's
price without a trade is not a fill. Cancellations of resting orders ahead in the queue do not reduce Q_ahead.

Stale placements. The share of placements whose best price on the order's side at g differs from that at j is
reported per cell.

Cancellation. An order not filled within 60 s of j is cancelled (decided at j + 60 s, effective 50 ms later). There
is no other cancellation.

Markouts. For a fill at time t_f and price p, with side s = +1 for a buy and -1 for a sell:
markout_h = s x (mid(t_f + h) - p) / tick, for h = 1, 10 and 60 s, where mid = (best bid + best ask) / 2 from the
last valid book state at or before t_f + h. A markout whose horizon crosses a session end, a crossed or empty book,
or an excluded period is dropped (counted). Beside the headline, a no-drop variant uses the last valid mid at or before
t_f + h (dropping only if none exists after t_f), because a sweep that empties one side is an adverse event and
dropping it would flatter the mean. Net markout_h = markout_h - FEE_SIDE.

What counts as a positive markout. For one fill: markout_h > 0. For a cell's mean (section 4): "positive" if the 95%
confidence interval's lower bound is above 0; "negative" if its upper bound is below 0; otherwise "not
distinguishable from 0". The headline economic statement is about the NET mean markout at 60 s.

## 4. Statistics

Cells: placement type (T, I) x session (MAIN, OVERNIGHT), with buy and sell pooled; buy and sell are also shown
separately.
Per cell:
- placements (count), fills within 60 s (count), the fill rate, and the Kaplan-Meier curve of time to fill with
  censoring at 60 s (median time to fill and the fill probability at 1, 10 and 60 s);
- among fills: mean and median markout at 1, 10 and 60 s, the share of positive markouts, and the mean net markout;
- the value per resting order, VPO_h = fill rate x (mean markout_h - FEE_SIDE), the queue-value identity of the
  methods brief (Part 4), at h = 60 s (and 10 s);
- the touch rate: the share of orders whose price was reached by a trade or by the opposite quote within 60 s,
  against the fill rate (the queue effect).
Confidence intervals: 95%, by a day-block bootstrap (trade dates resampled with replacement, 2,000 replicates, seed
28), for every rate and mean above.

Under the firm's simulated rule (B5 re-score). The same placements are re-filled under the top firm's documented
sim rule (SIMRULE; for example, fill only on a trade through the price), and the same statistics are reported, so
the ranking can be re-scored with the measured costs under both rules.

## 5. What this pilot does not do

No condition on any feature, no parameter search, no strategy, no selection among cells (all cells are reported).
The grid, latency, 60 s cap and horizons above are fixed here and are not varied. Any later use of these data for
a hypothesis needs its own pre-registration (methods brief, Part 4).

## 6. Minimum span (B1 arithmetic; filled with the contract's numbers)

Targets: the fill rate in the MAIN T cell to within +-0.03 (95% half-width), the mean 10 s markout to within +-0.10
tick, and the mean 60 s markout to within +-0.20 tick.
- Placements per MAIN day: 78 grid times x 2 sides = 156 (6.5 hours, 5-minute grid, minus the excluded edges).
- Fill rate: n >= deff x (1.96 x 0.5 / 0.03)^2 = 1,067 deff placements; with an assumed within-day design effect
  deff = 3, n >= 3,201, so at least 21 MAIN days.
- Markouts: with sigma_60 the SD of a 60 s mid change in ticks (taken as SIGMA1M) and sigma_10 = sigma_60 / sqrt(6),
  the fills needed are n_10 = deff x (1.96 sigma_10 / 0.10)^2 and n_60 = deff x (1.96 sigma_60 / 0.20)^2, with
  deff = 1.5 for fills. Fills per MAIN day = 156 x p_fill, with p_fill = 0.3 assumed for T orders.
- Minimum days = max(21, n_10 / (156 p_fill), n_60 / (156 p_fill)), rounded up and then raised by 15% for excluded
  days. The design effects and p_fill are assumptions; the pilot reports the realized bootstrap widths.

Filled for QM (sigma_60 = 2.520 ticks, sigma_10 = 1.029): n_10 = 1.5 x (1.96 x 1.029 / 0.10)^2 = 610 fills; n_60 =
1.5 x (1.96 x 2.520 / 0.20)^2 = 915 fills. (The QG version had 151 and 227.) With PilotCoder's grid count of 76 MAIN grid times (152 placements a day
after the 5-minute edge exclusions) and p_fill = 0.3, that is 45.6 fills a day, so 14 and 21 days; the fill-rate target
needs 21 days. Minimum = max(21, 14, 21) = 21, raised 15% = 25 MAIN trade dates. If p_fill is as low as 0.1, n_60 needs
61 days; the full window 2023-11-01..2024-02-29 (about 80 trade dates) covers both. The minimum span is
therefore the last 25 trade dates of the window; the purchase then extends the start backwards as the funds allow
(B3), never past 2024-02-29.

Corrected after review (RS-07): with 152 placements a day the fill-rate target needs ceil(3,201 / 152) = 22 MAIN days,
and 22 x 1.15 = 25.3, so 26 usable trade dates after exclusions. The repo calendar gives 85 trade dates in
2023-11-01..2024-02-29, with 4 holiday or early-close exclusions and about 4 roll-day exclusions. The minimum span is
therefore [2024-01-18, 2024-02-29T22:00Z) for QG. For QM, which rolls every month (about 8 roll-day exclusions in four
months rather than 4), the first trade date is no later than 2024-01-12: the minimum span is [2024-01-12,
2024-02-29T22:00Z). If the fresh quote for that
minimum span exceeds the spend target below, nothing is bought.

Spend target (RS-08). The account's usable balance B is the acct-3 cap of 125.00 USD unless a lower balance is shown at
purchase time. TARGET = B - max(3.00, 0.03 x B), rounded down to the cent (121.25 USD at B = 125.00). The span search
finds the earliest start whose quote is at most TARGET; the buy is approved for exactly that fresh quote; nothing is
bought if the minimum span's quote exceeds TARGET.

Every purchased trade date, after the exclusions of section 2, is measured (RS-10). "ACCOUNT_3 SAFE TO WIPE" is written
to the STATE file only after verify.py exits 0, or 3 for data-quality findings only (RS-09).
