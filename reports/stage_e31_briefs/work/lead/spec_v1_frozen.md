# Stage E.31 Part 2: the ZM order-book pilot spec

Written by the E.31 lead (Opus 5.5, xhigh), 2026-10-22, from 08:05 PDT, before any ZM, ZS or ZL order-book
data was quoted or bought. Binding: docs/prompts/STAGE_E.31.md Part 2 and V48. E.28's frozen QM spec
(reports/stage_e28_pilot_spec.md, sha256 8937740338e81103...) stays as the record of that pilot; its rules
are reused here where this file says so and where they apply. This file is hashed and frozen before any ZM
purchase (the hash and time are in reports/stage_e31_STATE.md). It measures fills and markouts of a
simulated passive 1-lot order. It tests no rule, selects nothing, registers nothing, and N stays 538.
No strategy P&L is computed.

## 0. Parameters

| Parameter | Value |
|---|---|
| Contract | ZM, CBOT soybean meal futures, 100 short tons; tick 0.10 USD/short ton = 10.00 USD |
| Front, second month | Databento continuous ZM.v.0 and ZM.v.1 (volume rank 1 and 2 on each day; the program's v.0 convention, E.28 section 2) |
| Conditioning contracts | ZS.v.0 (soybeans, tick 0.0025 USD/bu = 12.50 USD) and ZL.v.0 (soybean oil, tick 0.0001 USD/lb = 6.00 USD), front month |
| Matching algorithm | K (configurable), section 3; confirmed from the definitions (tag 1142 / `match_algorithm`) |
| Fees, USD per round trip (E.28 A2_firm_*.json, checked 07:5x: no difference) | Topstep 5.28, Lucid 5.60, Bulenox 5.72, MFFU 6.12, Tradeify 9.20 |
| Fee per fill (one side), ticks | RT / 2 / 10: Topstep 0.264, Lucid 0.280, Bulenox 0.286, MFFU 0.306, Tradeify 0.460 |
| Latency | 50 ms join and cancel, fixed (E.28 section 0) |
| Request end | 2024-02-29T22:00:00Z exclusive (16:00 CT on 2024-02-29; trade date 2024-03-01 opens 19:00 CT = 01:00Z on 2024-03-01, so none of it is bought) |
| Spend | acct-3 only, SpendGate session `stage-E.31-2026-10-22-pilot`; TARGET = funds left after Part 1 less 2.00 USD = 125.00 - 0.72502180934 - 2.00 = 122.27 USD (rounded down to the cent) |

## 1. Data

Four series, all on GLBX.MDP3, stype_in continuous unless stated, for the same whole months:
- Z1: ZM MBO, symbols ZM.v.0 and ZM.v.1.
- Z2: ZS MBP-1, ZS.v.0.
- Z3: ZL MBP-1, ZL.v.0.
- Z4: instrument definitions, schema `definition`, stype_in parent, ZM.FUT, ZS.FUT and ZL.FUT (outrights and
  spreads, so the implied-spread fields of both can be read).

The definitions are read first, to confirm for the ZM, ZS and ZL outrights the match algorithm (expected K),
the tick size, and the implied fields. If ZM's outright is not K, the measurement still runs (models b and c
do not depend on it) and model (a) is reported with that finding at its head.

Window. Whole calendar months ending with February 2024 and extending backwards: k months means trade dates
in [first day of month m_k, 2024-02-29]. Each month's request runs from 16:00 CT on the last calendar day of
the month before (in UTC; 21:00Z under CDT, 22:00Z under CST) to 16:00 CT on its own last calendar day, the
last month ending exactly at 2024-02-29T22:00:00Z. 16:00 CT falls between the 13:20 CT close and the 19:00 CT
open, so each request holds whole trade dates of its own month only. Requests are one per series per month
(4k requests), so each file is a bounded download and the span search can add months one at a time.

Length rule (span search, section 9): k is the largest number of months for which the sum of the fresh
quotes of all 4k requests is at most TARGET. k >= 2 or nothing is bought. All four series cover the same
months. The window contains a WASDE day in every month (USDA releases WASDE monthly). It contains a
limit-reset month if k reaches back to the latest reset month (section 9 states which and how many months
that needs); if the funds do not reach it, the window cannot include one and the return says so.

## 2. Days, sessions and exclusions

- Trade date: the CBOT trade date (the overnight session from 19:00 CT on the previous evening plus the day
  session). Holidays, early closes and late opens come from data.calendars.grains (HOLIDAYS, LATE_OPENS); every
  closure, early-close and late-open date is excluded.
- Sessions (America/Chicago clock): DAY = 08:30-13:20 CT, primary. OVERNIGHT = 19:00 CT (previous evening) to
  07:45 CT, reported separately. The first and last 5 minutes of each session take no placements.
- Roll days: for each continuous symbol, a trade date on which its instrument changes, and the trade date
  after, are excluded for that symbol (E.28 section 2). The instrument behind each symbol on each date is logged.
- Book validity (Z1): the book of an instrument is valid from its start-of-day snapshot (or clear followed by
  adds) on; a trade date whose book has no valid start, or which carries a record flagged as a possibly bad
  book, is excluded for that instrument from that record until the next valid snapshot (counted). Databento
  streams a synthetic snapshot (a clear, then adds in priority order, flagged F_SNAPSHOT) at 00:00 UTC each
  weekday when the request interval includes that midnight (research/data_facts.md a1). Every month request
  starts at 16:00 CT the evening before its first day, so it includes each weekday midnight of the month; the
  first trade date's book is valid from the first snapshot. Whether a continuous symbol's newly mapped
  instrument starts with a snapshot at a roll is not documented; the roll-day exclusion and the validity rule
  above cover it either way.
- Moments with a crossed or locked book, or an empty side, take no placements and stop markout clocks (counted).
  A trade date with a gap above 60 s between ZM front-month records inside the DAY session is excluded (counted).
- Records are processed in the file order (ts_recv, then sequence); ts_event, made non-decreasing (inversions
  counted), is the time axis (E.28 section 2).
- ZS and ZL days are not excluded separately: if a ZS or ZL mid is missing at a time a condition needs, that
  fill is in the "missing" bucket of that condition (counted).

## 3. The book and the matching rules

Book. The ZM book of each instrument is rebuilt order by order from Z1: add, cancel, modify, clear, trade and
fill records. Priority: an order keeps its place on a size decrease; a price change or a size increase sends it
to the back of its new level (CME rule; section 3.1). Snapshot orders keep their order in the file within each
level. Only the outright, displayed book exists here: implied orders are not in the data.

The virtual order. A 1-lot joins at the back of the queue at its price at join time, behind every order then
resting there. Orders added later at that price are behind it. It never trades with the book and changes
nothing in it (no market impact).

Match events. A match event is one aggressor's execution at one price level: the trade and fill records that
share its ts_event and price in Z1 (the grouping rule the code uses is stated in its README). Its volume v is
the sum of the trade sizes at that price. An aggressor that sweeps several levels makes one event per level.

### 3.1 K algorithm parameters for ZM outrights

Source: reports/stage_e31_briefs/research/K_algorithm.md (KResearch-OpusHigh, verbatim quotes and saved pages;
S1/S2 = CME Globex Product Reference Sheet, Wayback 2023-06-21 and 2024-02-26, ZM row 33, identical in both).
ZM outright: algorithm K; TOP allocation 100%, TOP Min 1, TOP Max 100 (counting only fills after the order
rests, from 2023-10-01, S7); FIFO 40%; pro rata 60%; pro-rata minimum 1; residual Leveling; no LMM in futures;
implied-eligible. ZS and ZL outrights carry the same values (S1/S2 rows 23 and 39).

Allocation of an event's outright volume Q at price p (the K step order, S3/S4 "Algorithm Matrix", S5, S6):
0. FIFO exception: if Q is at least the displayed quantity resting at p (the virtual order included), every
   order at p fills in time order.
1. TOP: the level's TOP order, if any, takes min(Q, its displayed quantity, 100 minus its fills since it
   rested). An order is TOP when it betters the market on its side with displayed quantity >= 1, or enters a
   level that has had no TOP order since it was established; it loses TOP when cancelled, when a new TOP order
   enters on its side, when TOP Max is reached, or when modified by a size increase or a price change to a level
   that does not better the market (S4's current text; S3's older text differs only for price-changing TOP
   orders, research (d) item 7). One TOP order per side. The virtual order is never TOP (it joins an existing
   level).
2. LMM: none.
3. Split of the remaining Q1: FIFO lots = ceil(0.4 x Q1), pro-rata lots = Q1 - FIFO lots (S3/S4: "at least the
   percentage expressed for FIFO"; Q1 = 5 gives 2 and 3, an inference, (d) item 4).
4. FIFO: the FIFO lots go to orders in time priority.
5. Pro rata: each order gets floor(w_i / W x pro-rata lots), with w_i its displayed working quantity after steps
   1 and 4 and W their sum (post-FIFO quantities: inferred from "Total working lots present", (d) item 2); an
   allocation below 1 is 0. The TOP order, after its TOP fill, takes part in steps 4 to 7 with what remains of it
   (it keeps its timestamp; (d) item 3, lead's reading).
6. Leveling: the lots left by rounding go, at most one each, to orders that took part in step 5 and got 0 from
   it, larger working quantity first, then earlier timestamp.
7. FIFO for anything still left.
The virtual 1-lot has working quantity 1 and timestamp j, so it is last in steps 4, 6 and 7 among orders that
were resting before it.

Implied liquidity. Implied orders are not in the data. Q is the event's outright volume: the quantity filled
against displayed outright orders resting at p in that event, as Z1 shows it (fills of resting orders, or the
size decrements of the orders at p in the event); any part of the print beyond it went to implied sources and is
not reallocated. How CME's predetermination splits an aggressor between the outright book and implied sources
is not stated for K's FIFO step ((d) item 5); taking the realized outright share as given avoids needing it.

Tests (Part 3): CME's per-step worked examples E1 to E7 and E9 of the research file, with the two printing
errors corrected as research (d) items 4 and 5 state (E4 order 6: 263, E2 order 3: 22), plus hand-built
full-sequence cases (TOP + Split + FIFO + pro rata + Leveling + FIFO) whose allocations the test states by hand.
CME publishes no full-sequence K example ((d) item 1).

Not found (values used): the pro-rata denominator (post-FIFO, above); the TOP order's part in later steps (it
takes part); split rounding on a whole number (ceil); the K FIFO step across implied sources (not needed, above);
the TOP modification rule in force in the window (S4's text). Opening matches are not used: no placement rests
in the first 5 minutes of a session.

## 4. Placements and fill models

Placements (E.28 section 3, T orders only, because the order rests at the best bid or ask): on a clock grid
every 5 minutes (xx:00, xx:05, ... CT) inside each session after the edge exclusions, two virtual orders, one
buy at the best bid and one sell at the best ask, size 1. An order created at grid time g joins at j = g + 50 ms
using the book at j. It is cancelled if not filled within 60 s of j (decided at j + 60 s, effective 50 ms
later; fills inside that window count). The next grid time places a new order (the replacement). No order is
placed one tick inside. Stale placements (best price at g differs from j) are counted per cell.

Each placement is filled independently under three models; the first event that fills it under a model sets
that model's fill time t_f. The fill price is always the order's limit price p.
- (a) K. At each match event at p while the order rests, the event's volume v is allocated by section 3.1 over
  the queue at p as it stood just before the event, with the virtual order inserted at its place. The order
  fills when its allocation is at least 1. The queue's real state comes from Z1 at every moment (orders ahead
  that cancel or are filled leave it), so the counterfactual is only where the event's volume goes.
- (b) FIFO, back of the visible queue. Q_ahead(t) = the remaining displayed size, as Z1 shows it at t, of the
  orders that were ahead of the virtual order at j and still rest at p. The order fills at the first match
  event at p whose volume v exceeds Q_ahead just before the event.
- (c) Trade-through only (THE GATE). The order fills at the first trade with a defined aggressor (A or B, never
  N) printed at a price strictly through p (below a buy, above a sell) while it rests. A trade at p, or a quote
  that moves to or through p without a trade, is not a fill. This is the Topstep simulator's documented rule
  (docs/DECISIONS.md:36-38).
Under (a) and (b) a trade strictly through p also fills the order (E.28's through trigger), because an aggressor
that clears a level fills everything resting there. Fills are reported by trigger (queue or through).

## 5. Markouts

For a fill at t_f at price p, side s (+1 buy, -1 sell), with mid0 = the ZM mid of the same instrument just
before the fill event and mid(t) the last valid mid at or before t (valid: both sides present, not crossed or
locked):
- markout_h = s x (mid(t_f + h) - mid0) / tick, for h = 1, 10 and 60 s ("against the ZM mid");
- half-spread captured c = s x (mid0 - p) / tick (it can be negative for a through fill);
- edge E_h = markout_h + c = s x (mid(t_f + h) - p) / tick;
- net edge N_h(firm) = E_h - fee per fill (section 0).
A markout whose horizon crosses a session end, an excluded period, or a crossed or empty book is dropped
(counted). Beside it, the no-drop variant of E.28 (the last valid mid at or before t_f + h, dropped only if
none exists after t_f) is reported; the headline and the gate use the dropping version, and the no-drop
version is shown beside the gate as a check.

Conditions and splits (reported for every model; they decide nothing):
- ZS and ZL moves: for L = 1 s and L = 10 s, d = mid(t_f) - mid(t_f - L) of ZS (and of ZL) in that contract's
  ticks, from Z2 and Z3. Bucket by sign of s x d: against (< 0), flat (= 0), with (> 0), missing. Shown for ZS,
  for ZL, and jointly (both against, both with, other).
- Session: DAY, OVERNIGHT.
- USDA releases (reports/stage_e31_briefs/research/usda_releases.csv for 2022-11..2024-02 and
  usda_releases_ext.csv before it; WASDE, Crop Production, Grain Stocks, Crop Progress, Export Sales, Fats & Oils;
  NOPA is not USDA and is not used; converted to CT; a trade date outside both files' range is not measured
  until they cover it): signed minutes from the
  nearest release on the same trade date: pre (-30, 0), post [0, 5), post [5, 30), other (including trade dates
  without a release).
- Queue imbalance at entry: I = (bid size - ask size) / (bid size + ask size) at the best level at j, side
  adjusted s x I, buckets (-1, -0.6], (-0.6, -0.2], (-0.2, 0.2), [0.2, 0.6), [0.6, 1).

## 6. Feasible round trips (the capacity count)

Per DAY session of the front month, a sequential loop with one 1-lot order at a time, under each model:
- from the first placement time, a buy at the best bid (the entry side alternates by round trip within the
  day, starting with buy), joining 50 ms after it is decided, cancelled after 60 s unfilled and replaced at once
  by a new order at the then-best price on the same side (joining 50 ms later, back of the queue);
- when the entry fills, the exit order (the opposite side, at the then-best price) is decided at t_f and joins
  50 ms later, with the same cancel and replace rule;
- when the exit fills, one round trip is complete and the next entry is decided at that moment.
No order is placed in the last 5 minutes of the session; an open position at the session end is not counted.
The loop's count per DAY trade date is the number of completed round trips. Only counts and durations are
reported; no P&L of the loop is computed.

## 7. Kill rule (fixed before any data)

Primary population: ZM front month (ZM.v.0), DAY session, model (c), the section 4 placements, buy and sell
pooled, after all exclusions. ZM FAILS the pilot if any of these holds:
- K1: the mean over fills of the 10 s edge net of Topstep's fee per fill, N_10(Topstep) = E_10 - 0.264, has a
  95% day-block bootstrap interval (section 8) whose lower bound is not above zero;
- K2: there are fewer than 400 fills;
- K3: the loop of section 6 under model (c) completes fewer than 20 round trips per DAY trade date, as the mean
  over measured DAY trade dates.
Otherwise ZM PASSES. Models (a) and (b), the overnight session, the second month and the other firms are
reported in full and decide nothing. Beside K1, for information only: the same bound with the full round-trip
fee charged on every fill (E_10 - 0.528), and the no-drop variant.

Fee reading (lead's choice, logged as an open choice): a passive round trip is two fills and pays one
round-trip fee, and Topstep states "Each side (Buy or Sell) incurs half the total" (E.28 A2_firm_topstep.json),
so the fee per fill is half the round-trip fee, the same convention as E.28's FEE_SIDE.

## 8. Statistics

Cells: model (a, b, c) x session (DAY, OVERNIGHT) x month (front, second), buy and sell pooled and also shown
separately. Per cell, as E.28 section 4: placements, fills within 60 s, the fill rate, the Kaplan-Meier time to
fill censored at 60 s (median, P at 1, 10, 60 s), and among fills the mean and median of markout_h, c, E_h and
N_h(Topstep) at h = 1, 10, 60 s, the share of positive E_h, and the value per resting order VPO_h = fill rate x
mean N_h. Net results for all five firms are shown for the primary cell.
Intervals: 95% two-sided percentile intervals from a day-block bootstrap (trade dates resampled with
replacement, 2,000 replicates, seed 31), for every rate and mean, and for the loop's mean count (K3).

Implied-liquidity check (front month, per session): among ZM trades with a defined aggressor, the share of
prints, and of volume, whose price had (i) no displayed resting quantity on the passive side in the rebuilt
book just before the trade, or (ii) less displayed resting quantity than the trade's size; trades with side N
are counted beside.

## 9. Window arithmetic and purchase

- TARGET = 122.27 USD (section 0). Span search: free, ledgered quotes (session `stage-E.31-2026-10-22-pilot-span`,
  cap 0.00) of the 4 requests of each month, from February 2024 backwards, one month at a time, stopping at the
  first month whose addition makes the cumulative sum exceed TARGET; k is the number of months before it.
  k >= 2, else nothing is bought.
- Limit-reset month: CBOT resets the soybean complex's daily limits semi-annually; ZM's took effect on trade
  date 2023-11-01 (30 to 25 USD/ton, CME SER-9281; research/data_facts.md c), so the window includes a reset
  month when k >= 4 (November 2023), and every earlier May and November it reaches.
- Review in two passes (lead's choice, logged): SpecReviewer-FableXHigh checks this spec, the kill rule, the
  window arithmetic and the purchase and verify code (pull31.py, pilot31_common.py, verify31.py) and gives GO or
  NO GO for the purchase; the engine and stats code (mbo_book31, kalgo31, measure31*, stats31*) get their own
  Fable review before the measurement runs. Every BLOCKING item of either is fixed and re-checked once.
- After the SpecReviewer's GO: a fresh quote of every chosen request; buy only if their sum is at most TARGET;
  then the purchases, ZM MBO first, latest month first, each request committed, downloaded (.partial, link,
  read-only), record-byte checked and settled through SpendGate before the next. Billing more than 3% above a
  quote stops the remaining purchases.
- Verification before any measurement: per file, bytes, sha256, record counts by record type and instrument,
  the ts_event range inside the request, and no record dated on or after 2024-03-01; a manifest JSON holds them.
  "ACCOUNT_3 SAFE TO WIPE" is written to the STATE file with the time and the amount left only after the last
  purchase is verified.
- Arithmetic for the minimum: a DAY session has 57 grid times after the edge exclusions (08:35 to 13:15 CT), so
  114 placements per DAY trade date. K2's 400 fills need 400 / (114 p) DAY trade dates for a model (c) fill rate
  p: 18 dates at p = 0.2, 36 at p = 0.1, 71 at p = 0.05. Two months give about 38 usable DAY trade dates after
  exclusions. If the span is too short for K2, K2 decides (the pilot fails on K2, it is not extended).

- Measurement: every purchased trade date, after the exclusions of section 2, is measured (E.28 RS-10). No
  statistic and no part of the verdict is computed or read until every purchased trade date is done; a partial
  run is never looked at. The run is resumable per trade date, at nice 10 with at most min(8, cores / 2) workers,
  and stays out of the 15:30-16:00 PT collector window.

## 10. What this pilot does not do

No condition is selected, no parameter is searched, no strategy is run, and every cell is reported. The grid,
latency, 60 s cap, horizons, buckets and kill rule are fixed here. No ZM, ZS or ZL record dated on or after
2024-03-01 is quoted, bought or read. Any later use of these data for a hypothesis needs its own
pre-registration.
