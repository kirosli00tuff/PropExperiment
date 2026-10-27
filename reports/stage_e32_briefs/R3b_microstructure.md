# R3b: soybean-complex market microstructure for minutes-to-hours directional trading in ZM

Stage E.32, worker SoyMicrostructure-OpusHigh (opus, high). ROOT R3b_microstructure. Started 2026-10-27 00:33 PDT.
Research only: no market data read, no statistic derived from data. Evidence pages and log.tsv:
reports/stage_e32_briefs/pages/R3b_microstructure/. Source labels: academic, practitioner, regulator, exchange, firm.
CME material comes only from CFTC-hosted copies, papers or other secondary sources (E.32 rule); cmegroup.com and its
archives were not fetched. Where a fact rests only on a cmegroup.com-origin file that Stage E.31 saved earlier
(reports/stage_e31_briefs/research/pages/K/), it is marked [E.31 cmegroup-origin, not re-fetched].

Status: complete (finished 2026-10-27 00:49 PDT; see the last section for gaps).

## (a) The K matching algorithm on CBOT grains and oilseeds, and what it means for an aggressor versus a resting order

### a.1 Facts

- ZM outrights use match algorithm K. Owned data: E.31 checked the definitions files of the owned data and found
  "all outrights K" (reports/E.31_RETURN.md line 168, quoted: "structure checked (every weekday snapshot present,
  all outrights K, ticks 10.00/12.50/6.00 USD ..."). This is a recorded E.31 fact, not a new read of data.
- CME's own description, as presented to the CFTC Agricultural Advisory Committee on 2019-04-11 and hosted on
  cftc.gov [exchange material, regulator-hosted] (R3b_cftc_aac041119_cmegroup.pdf, page 3, "K Matching Algorithm in
  Grain Futures"):
  - TOP: "The first order to "better the market" is eligible for TOP allocation. The most any order can be allocated
    is controlled by TOP MAX. TOP MAX in grain outrights is 100 contracts and 1000 contracts in grain spreads."
  - FIFO: "40% of the incoming aggressing order is allocated by timestamp. The order with the oldest timestamp at
    that price level is first in the queue."
  - Pro rata: "60% of the incoming aggressing order is allocated based on the size of the resting orders. The largest
    order receives the largest allocation, followed by the second largest order, etc."
  - Levelling: "A means by which residual quantity from rounding during the Pro-Rata step are distributed. Any order
    that did not participate in the Pro-Rata pass is eligible for rounding with a maximum of 1 contract allocated per
    order."
  - Residual: "Any residual quantity remaining is filled FIFO."
  - Page 4 (pro-rata rounding): with six resting 10-lots, a 6-lot aggressor gives each 1 lot, but "changing the
    incoming order to a 5 lot completely changes the allocation. 5 cannot be equally split amongst 6 equal shares
    resulting in no Pro-Rata allocation and this 5 lot moves to either Leveling or FIFO."
  - Page 5, "Realized Allocations": "~7% TOP", "~56% FIFO", "~23% Pro-Rata", "~14% Leveling". The slide does not say
    which products, period or unit (lots or fills) these shares cover [the scope is not stated in the source].
- Finer parameters for ZM (Stage E.31's parameter table, reports/stage_e31_briefs/research/K_algorithm.md section
  (a), from the CME Globex product reference sheet and the CME client wiki) [E.31 cmegroup-origin, not re-fetched]:
  TOP Min 1, TOP Max 100 (outright), FIFO 0.4, pro rata 0.6, PR Min 1, residual "Leveling" for the ZM outright and
  "FIFO" for the ZM-ZM calendar spread, no LMM in futures, FIFO share rounded up to a whole lot, pro-rata shares
  rounded down, levelling at most 1 lot per order to orders that took part in the pro-rata step and got 0, ties by
  larger working quantity then earlier time; since 2023-10-01 only fills after an order rests count against TOP Max.
  E.31 also recorded a conflict: the CFTC slide says any order "that did not participate in the Pro-Rata pass" is
  eligible for levelling; the wiki says the order "must have participated in the preceding Pro Rata step" and
  received 0 lots. The wiki is the more detailed text.
- FIFO exception for sweeps [E.31 cmegroup-origin, not re-fetched; K_algorithm.md (a), sources S3/S4]: "In the
  scenario where an aggressing order quantity is greater than or equal to the displayed quantity in an instrument at
  a given price level, for matching efficiency, CME Globex applies FIFO in lieu of the designated product
  algorithm." No CFTC-hosted or academic copy of this rule was found in this stage (one search).
- Academic context on pro-rata books [academic]: Field and Large (CFS Working Paper 2008/40,
  R3b_field_large_2008_prorata.pdf, abstract): in four one-tick short-rate futures markets with pro-rata matching
  "offered depths at the quotes on average exceed mean market order size by two orders of magnitude, and their order
  cancellation rates ... are significantly over 96 per cent", and "strategic complementarities in the choice of limit
  order size cause traders to risk overtrading by submitting over-sized limit orders, most of which they expect to
  cancel." ZM is not a one-tick market (median daily range 96 ticks, E.28 A0) and is 60% pro rata, not 100%, so this
  is an analogy, not a ZM result.
- Grain order life [academic]: Ma and Serra's working version (R3b_afajof_63476_ma_serra.pdf, abstract), CME corn,
  soybean and wheat MBO, 2019-01 to 2020-06: "25%-28% of limit orders submitted are executed, while around 75-79% are
  deleted and 7%-8% revised. Latency of limit orders is low, with half of the limit orders being deleted within 2-5
  seconds after their placement."

### a.2 Worked example (a resting 1-lot versus an aggressor; arithmetic only, rules as stated above)

Book: ZM best bid, four resting orders in time order A = 50 lots (oldest), B = 30, D = 19, C = 1 (ours, newest);
displayed total 100 lots; no TOP order left at this price (assumption). A sell market order of q = 10 lots arrives.

1. FIFO exception? q = 10 < 100 displayed, so K applies.
2. Split: FIFO lots = ceil(0.4 x 10) = ceil(4.0) = 4 (E.31 (d)4 reads "rounded up to the whole lot just above" as
   ceil, [inferred]); pro-rata lots = 10 - 4 = 6.
3. FIFO: A (oldest) takes 4. A has 46 left.
4. Pro rata on working quantities after FIFO (E.31 (d)2: post-FIFO denominator [inferred]): total 46 + 30 + 19 + 1 =
   96. A: floor(46/96 x 6) = floor(2.875) = 2; B: floor(30/96 x 6) = floor(1.875) = 1; D: floor(19/96 x 6) =
   floor(1.1875) = 1; C: floor(1/96 x 6) = floor(0.0625) = 0. Allocated 2 + 1 + 1 + 0 = 4; residual 6 - 4 = 2.
5. Levelling: only C took part and got 0, so C gets 1 lot. Residual 2 - 1 = 1.
6. FIFO residual: A takes 1.
7. Totals: A 4 + 2 + 1 = 7, B 1, D 1, C 1; sum 10 = q. Check: equals the aggressor's size, and C's fill (1 lot)
   came from levelling although C was last in time; under pure FIFO C would fill only after 99 lots traded.
8. The aggressor's price is the bid in every case: for q at or below the visible plus implied quantity at the touch,
   the algorithm decides WHO is filled among resting orders, never the aggressor's price. If q = 100 or more, the
   FIFO exception fills the level in time order, and any remainder walks to the next price.

Variant: q = 5 with the same book. FIFO = ceil(2.0) = 2 to A (48 left); pro rata 3 on 48 + 30 + 19 + 1 = 98: A
floor(1.469) = 1, B floor(0.918) = 0, D floor(0.582) = 0, C floor(0.031) = 0; residual 2; levelling by larger working
quantity first: B 1, D 1 (residual 0), C gets nothing. Totals A 3, B 1, D 1, C 0 = 5. So a small aggressor can skip the
1-lot entirely; whether C fills depends on the aggressor size and the other orders, not on C's time priority.

### a.3 What this means for a ZM directional search

- A minutes-scale directional strategy that enters and exits with market (marketable) orders of 1-3 lots is almost
  untouched by K: the fill price is the touch whenever the size is below displayed plus implied quantity. No recorded
  E.28 or E.31 statistic gives ZM touch depth (searched A0_contract_stats.md and E.31_RETURN.md), so "1-3 lots fit at
  the touch" is an assumption for E.33 to check on discovery data. E.31 measured that 11.8% of aggressor PRINTS (26.0%
  of their volume) found less than their size displayed, but those are other traders' sizes, not a 1-lot.
- K matters for (i) any limit-order entry (fills arrive by levelling or FIFO lottery, decoupled from queue position,
  so a resting 1-lot is filled more often when a large aggressor sweeps through, which is the adverse-selection case
  E.31 measured at -0.970 ticks per fill gross at 10 s) and (ii) the meaning of displayed depth. With 60% pro rata,
  resting size buys allocation, so displayed depth includes size that its owners do not expect to trade (the Field
  and Large mechanism, and Ma and Serra's 75-79% deletion share). Depth-imbalance features are therefore noisier
  signals of intent than in a FIFO market, and the sign of a "large bid" is ambiguous. Treat depth and queue features
  as conditioners (planner family 7), with the over-sizing confound written into the feature definition.
- Mechanism to drop: queue-position modelling for a 1-lot. Under K it does not buy priority the way it does under
  FIFO, and V50's trade-through rule decides the simulated fill anyway.
- Test, not assume: whether cancellations at the touch (not additions) carry the information (Ma and Serra's
  information shares, section (e) below, give cancellations at the BBO a large share in grains).

## (b) Implied spreads (calendar and board crush), implied in and implied out, and what an aggressor sees versus the feed

### b.1 Facts

- Mechanism [academic]: Ma, Serra, Peterson and Irwin (NCCC-134 2026, R3b_richie_ma_serra_2026_calendar_spreads.pdf,
  lines 88-95 of the text file): "A key feature of CME's electronic trading design is its implied functionality, an
  automated quoting system that tightly integrates liquidity between calendar spreads and outrights. Through this
  system, liquidity in calendar spreads generates synthetic and contingent quotes in outrights ... For example, a
  $0.25 bid quote of the May-July calendar spread and an ask quote of $4.25 of the May outright can generate an
  implied $4 bid quote of the July outright."
- Implied in and implied out [academic]: Peng, Hu, Robe and Adjemian (NCCC-134 2021,
  R3b_peng_hu_robe_adjemian_2021.pdf, lines 266-270): "A trade can be initiated by either a buyer or a seller as well
  as classified as an implied trade when matching with implied order(s)." and "updates in the LOB also reflect
  changes to implied orders that can be either (i) orders in the outright book created based on orders in the spread
  market ("implied-out") or (ii) orders in the calendar spread book created based on orders in the outright market
  ("implied-in")."
- Size of calendar-implied liquidity at the outright touch, corn and soybeans, CME Market Depth data 2015-01-05 to
  2024-12-27, day session [academic] (Ma et al. 2026, lines 636-641): "For the first-nearby futures, implied liquidity
  contributes 16.00%-17.97% to consolidated liquidity, rising to 50.97%-52.48% for second-nearby futures. For more
  deferred contracts, implied liquidity constitutes about 68.92%-72.09% of consolidated depth in grain markets". The
  measure counts implied depth only when its price equals the consolidated best price (lines 631-635). ZM is not in
  their sample (corn and soybeans only, lines 212-215).
- The exchange's public feed carries the calendar-implied book separately and only two levels deep [firm, data
  vendor] (Databento GLBX.MDP3 docs, R3b_databento_glbx_mdp3.md, line 112): "CME's MDP3 feed has support for implied
  orders over their MBP feed. The MBP feed provides up to 10 levels of real liquidity and 2 levels of implied
  liquidity." Ma et al. 2026 (lines 632-633): "Because implied and outright order books are disseminated separately,
  we count implied depth only when its quote matches the consolidated best price."
- What the owned data contain: the owned ZM MBO is an outright order-by-order feed. Databento (line 47): MBO "Add,
  Modify, and Cancel actions are normalized from [Market Data Incremental Refresh - MBOFD]", and line 113: "Databento
  combines the real and implied books, publishing the merged top-of-book on the [CMBP-1] schema." The owned ZS and ZL
  files are MBP-1, not CMBP-1 (READER_BRIEF owned-data list), so neither the owned ZM MBO nor the owned ZS/ZL MBP-1
  shows implied quantity [inferred from the schema names; confirm with the DataFacts worker].
- Trades against implied quantity lose their aggressor side and order detail:
  - Databento (lines 70-71) [firm]: "Implied trades ... may not have an aggressing side set. These trades will be
    normalized with side set to None."
  - Ma and Serra working version (R3b_afajof_63476_ma_serra.pdf, footnotes 2 and 5) [academic]: "Order details (e.g.,
    order ID, matched quantity, aggressor) are not provided for those market orders that are executed against implied
    order(s). If a market order is executed against both outright and implied limit order(s), only matched outright
    order details are recorded." and "the trade summary message that aggregates the matched limit orders does not
    provide the aggressor indicator if implied liquidity is involved in the match." Their fix: assign the aggressor
    as the side opposite the matched outright orders, and delete trades executed entirely against implied liquidity,
    which were "0.03%, 0.01%, and 0.01%, of total number of trades ... in the corn, soybean, and wheat markets,
    respectively, in each trading day."
- Ratio (intercommodity) spreads such as the soybean crush imply into the legs, and those implieds are not shown in
  market data [exchange; E.31 cmegroup-origin, not re-fetched] (reports/stage_e31_briefs/research/pages/K/
  wayback_algorithms_near20231201.txt, CME Globex Matching Algorithms, capture 2023-10-02): "There is an exception
  during Predetermination with ICS ratio spreads. Examples include Treasury ICS and Soybean Crush spreads." and, in the
  ratio-spread example on the same page, "(these implieds will not be visible via market data)". Also: "Implied
  quantity will never match with implied quantity." The planner's exact phrase "not disseminated in market data" (from
  the wiki page "Implied Intercommodity Ratio Spreads") was not found in any file this stage may read; the E.31 page
  says the same thing in other words.
- The crush spread's legs and price formula are R3a's topic (reports/stage_e32_briefs/R3a_crush.md section 1: board
  crush in cents/bu = 2.2 x M + 11 x O - S, the 10:11:9 ratio). A search snippet of a 2009 CME notice gives the SOM
  legs as "Eleven (11) Soybean Meal futures contracts; ... Nine (9) Soybean Oil ...; ... Ten (10) Soybean" [unverified:
  search snippet of a cmegroup.com page, not fetched under the stage rule].
- Exchange history [practitioner, sponsored by the FIA Principal Traders Group] (Overdahl, Futures Industry, Nov 2011,
  R3b_nera_overdahl_2011.pdf): "On Jan. 31, 2011, the CME turned on implied matching functionality for corn futures
  after turning off this functionality in August 2010." and "in these two instances, market quality improved when the
  exchanges turned off their implied matching functionalities." Interested-party research; context only.
- Priority between outright and implied quantity: Ma et al. 2026 (line 764) state "outright quotes have matching
  priority over implied quotes (CME 2007)", while the E.31-saved CME page describes predetermination in which each
  implied "source" is treated "as one large order quantity" and run through the algorithm's steps with the outright
  book. These two descriptions are not obviously the same; the order of priority inside K for ZM is unresolved here.
- Stage E.31's own measurement (reports/E.31_RETURN.md line 204, front month, day session): "5.5% of aggressor prints
  (3.6% of their volume) found no displayed resting quantity at their price, 11.8% (26.0% of volume) found less than
  their size, and 9.1% of prints carry no aggressor side."

### b.2 Worked example: an implied-out ZM bid from the board crush (units and lot blocks; price convention not checked)

Using R3a's formula per bushel, C [c/bu] = 2.2 x M + 11 x O - S (M in USD/short ton, O in c/lb, S in c/bu).
Suppose a resting crush BUY (buy meal and oil, sell beans) at C* = 150 c/bu, a resting ZL offer at O = 50.00 c/lb and
a resting ZS bid at S = 1300.00 c/bu. A ZM seller can be matched against the crush buyer, with the engine buying ZL
from the ZL offer and selling ZS to the ZS bid. The ZM price that makes the package equal C*:
M = (C* - 11 x O + S) / 2.2 = (150 - 550 + 1300) / 2.2 = 900 / 2.2 = 409.0909 USD/short ton.
That is not on the 0.10 USD tick; how CME rounds or prices SOM legs is not known here [unverified], so this shows the
units only. Lot blocks: one SOM spread is 11 ZM + 9 ZL + 10 ZS (ratio per R3a), so implied ZM quantity from one SOM lot
is 11 ZM lots. The E.31-saved CME page's ratio-spread rule rounds a source's allocation to zero when it is too small to
form whole legs ("If the ZT source ... was allocated 2 lots, round this quantity to zero and work on the other
sources"), so a 1-3 lot ZM aggressor probably does not match crush-implied quantity at all [inferred from a Treasury
example; not stated for the crush]. Check: 2.2 x 409.0909 + 11 x 50 - 1300 = 900.0 + 550 - 1300 = 150.0 c/bu = C*.

### b.3 What this means for a ZM directional search

- For a 1-lot aggressor at the ZM front month, implied quantity is extra liquidity: it can only fill at the same or a
  better price than the outright book, never worse. It does not hurt a market-order entry.
- It does hurt measurement. In the owned data, a trade print with no visible resting quantity at its price, or with
  side None, is most likely an implied match (E.31: 5.5% and 9.1% of front-month day prints). Any order-flow
  imbalance or trade-sign feature must state how it treats side None prints (drop, or sign by the matched outright
  side as Ma and Serra do) and freeze that choice before the search; E.33 should report the share dropped.
- Depth, spread and touch features built from the owned MBO and MBP-1 are outright-only. The true executable touch is
  at least as good as the outright touch, so a cost model built on outright spreads is conservative for the touch
  price. For the second contract (ZM.v.1) the gap is likely much larger: Ma et al. put implied liquidity at about half
  of consolidated touch depth for the second nearby corn and soybean contract.
- Crush-implied liquidity is invisible in every feed. A ZM move caused by a crush-spread order trading through implied
  quantity looks, in ZM's own book, like an aggressor hitting nothing. That makes "sweeps of empty levels" a candidate
  sign of cross-product (crush) flow, not a ZM-only event; a family built on ZM-only book events should carry ZS and
  ZL trade timing as a control.
- Mechanism to drop: any feature that needs implied depth (the owned data cannot rebuild it). Mechanism worth a test:
  side-None or no-resting-quantity prints as a crush-flow flag, measured in discovery data only.

## (c) Roll and delivery effects: delivery months, first notice day, index rolls, spot-month limits, volume migration

### c.1 Facts

- Delivery months and last trading day [exchange; E.28 cmegroup-origin, not re-fetched]
  (reports/stage_e28_briefs/pages/A1_grains/cbot_rulebook_ch13.txt, CBOT Rulebook chapter 13, Wayback 2025):
  "Trading in soybean meal futures is regularly conducted in eight months - September, October, December, January,
  March, May, July, and August." Termination: "No trades in Soybean Meal futures deliverable in the current month
  shall be made after the business day preceding the 15th calendar day of that month." Close on the last day: "the
  close of the expiring future shall begin at 12 o'clock noon and trading shall be permitted thereafter for a period
  not to exceed one minute." Price limits: "There shall be no price limits on the current month contract on or after
  the second business day preceding the first day of the delivery month."
- Stage E.0 recorded a CME statement [exchange, cmegroup-origin, E.0 K6 P-K6-048-d, reports/stage_e0_research_K6.md
  line 672]: "Spot month contracts are not subject to price limits. In Grain and Oilseed contracts, price limits are
  removed on the business day prior to first notice day of an expiring contract month."
- First notice day: no CFTC-hosted or academic text defining it for CBOT grains was found in this stage (two
  searches). A search snippet of a 2017 broker notice says first notice for December CBOT grains "fell on the last
  business day of November" [unverified: search snippet, broker page not fetched]. The two price-limit rules above
  give the same day only if first notice day is the last business day of the month before delivery (worked example
  c.2), which supports that reading [inferred].
- Federal speculative position limits for soybean meal [regulator] (CFTC, "Speculative Limits" page,
  R3b_cftc_speculative_limits.html): "2020 Final Rulemaking Federal Spot Month Limit Level | ... | CBOT Soybean Meal
  (SM) | 1,500" and "Federal Single Month and All-Months-Combined Limit Levels | ... | CBOT Soybean Meal (SM) |
  16,900". The same page: "Exchanges must implement § 150.5 by the 2020 Final Rulemaking's general compliance date of
  January 1, 2022." The pre-2021 legacy levels (relevant to the sealed 2017-2020 test window) were not retrieved
  [unverified]; the GPO appendix table (R3b_govinfo_cfr2025_17_150_appE.pdf) is an image and did not extract.
  The federal definition of the legacy-agricultural spot month was not retrieved [unverified].
- Index rolls:
  - Bloomberg Commodity Index (BCOM) holds soybean meal directly [firm, index provider] (R3b_bcom_methodology.pdf,
    version with January 2023 target weights): soybean meal is an index commodity ("Soybean Meal | CBOT | 100 short
    tons | USD/short ton"), with a 2023 CIP of "3.53%". Roll: "The "Roll Period" is used in this Methodology to refer
    to the sixth through tenth Business Days of the month, during which time the value of BCOM is gradually shifted
    from the utilization of WAV1 for Index calculation to the utilization of WAV2, at the rate of 20% per Business
    Day." Table 9 (contract calendar, Jan to Dec): "Soybean Meal Mar Mar May May Jul Jul Dec Dec Dec Dec Jan Jan".
    Reading the table with the text ("in February the Lead Future is March and the Next Future is May"), BCOM rolls
    its ZM position in February (Mar to May), April (May to Jul), June (Jul to Dec), October (Dec to Jan) and
    December (Jan to Mar) [inferred from Table 9 and the quoted rule]. It never holds the Aug, Sep or Oct ZM contracts.
  - S&P GSCI ("Goldman roll") [academic] (Hu and Peterson, NCCC-134 2014, R3b_nccc_gsci_roll_returns.pdf): "20% of
    the total number of contracts of a sooner-to-expire commodity futures contract will be sold and the same number of
    contracts of a later-to-expire contract will be bought each day from the 5th business day to the 9th business day
    of the month." Its 24 constituents for 2007-2013 include "Corn, Chicago Wheat, and Soybeans" from CBOT, and not
    soybean meal or soybean oil. So the Goldman roll touches ZM only through ZS and the crush. Whether S&P added soy
    products after 2013 was not checked (the S&P methodology PDF returned 403) [unverified].
  - Price impact of index rolls: Mou (2010/2011, SSRN 1716841 and Columbia thesis) reports that front-running the
    GSCI roll earned high Sharpe ratios in 2000-2010 [unverified: search snippet of the abstract; Columbia's copy sits
    behind a bot wall and SSRN is blocked].
- Volume migration before notice [academic]:
  - Arzandeh and Frank (R3b_arzandeh_frank_caes2017.pdf), roll date defined as the day "when its aggregate volume
    traded for two consecutive days falls below that of the second nearest contract": "traders of grains, on average,
    roll their position over three weeks before the expiration date of their contract." Their Table 1 (ZS): January
    2016 contract (expiring 14 Jan 2016) nearby until "20 Dec. 2015"; March 2016 (expiring 14 Mar 2016) nearby "21 Dec.
    2015 - 21 Feb. 2016"; May 2016 from "22 Feb. 2016".
  - Ma and Serra (R3b_afajof_63476_ma_serra.pdf) and Ma et al. 2026 use the same two-day volume rule; E.0 K6-031
    recorded Hu, Mallory, Serra and Garcia (NCCC-134 2017): in corn "the nearby contract loses dominance" in price
    discovery when its volume share falls below 50%, "about 2-3 weeks before expiry" (E.0's summary, abstract quote
    truncated in E.0's file).
  - Ma et al. 2026: implied liquidity is 16-18% of touch depth in the first nearby but about 51-52% in the second
    nearby (section b), so the second contract's displayed outright book understates its liquidity most in the weeks
    before the roll, when it is about to become the front.
- COT [regulator] (CFTC, R3b_cftc_cot_index.html): "The COT Report is generally published each Friday at 3:30 pm
  Eastern Time (US), using the data from the immediately preceding Tuesday of that week." and "Note that holidays can
  change the COT release schedule."

### c.2 Worked example: one ZM contract's calendar (ZMH3, March 2023), dates only

- Last trading day: business day preceding 15 March 2023 (a Wednesday) = Tuesday 14 March 2023.
- Assumed first notice day (last business day of February 2023) = Tuesday 28 February 2023 [inferred rule].
- Limits removed under chapter 13: "second business day preceding the first day of the delivery month"; 1 March 2023
  is a Wednesday, so the business days before it are 28 Feb (1st) and 27 Feb (2nd): Monday 27 February 2023.
- Limits removed under the E.0 CME text: "business day prior to first notice day" = business day before 28 Feb =
  Monday 27 February 2023. Check: both rules give 27 February, consistent with the assumed first notice day.
- BCOM roll from ZMH3 to ZMK3: business days 6-10 of February 2023. Weekdays from 1 Feb: 1, 2, 3, 6, 7, 8 (6th), 9,
  10, 13, 14 (10th); no US holiday falls before 20 Feb. Roll window 8-14 February 2023, 20% a day.
- Ordering: BCOM roll (8-14 Feb) comes about two weeks before first notice (28 Feb). For ZS in early 2016, Arzandeh and
  Frank's volume crossover for the March contract fell on 22 Feb 2016 (first notice 29 Feb 2016 under the same
  rule, a Monday), while BCOM's 6th-10th business days of February 2016 were 8-12 February (weekdays 1-5, 8, 9, 10,
  11, 12). So, in that one ZS case, the index roll came about ten days before the volume crossover, which came
  about one week before first notice [inferred; one contract, ZS not ZM].

### c.3 What this means for a ZM directional search

- The front-month label matters: the owned ZM.v.0 is a volume-ranked continuous series, so its switch date moves with
  traders (about 1-2 weeks before first notice in the ZS example), not with the calendar. Every label horizon must be
  computed within one contract (never across a v.0 switch), and the switch day itself should be excluded or flagged.
- Planner family 8 (index roll, first notice, COT) as flags or exclusions, not as alpha families:
  - roll flag: BCOM business days 6-10 in Feb, Apr, Jun, Oct and Dec for ZM; GSCI business days 5-9 in ZS roll
    months (ZS schedule not retrieved here) as a ZS-side flag;
  - notice flag: from the business day before first notice to last trade of the expiring contract (the spot month
    has no price limits and a 1,500-lot federal spot limit, so large speculators exit before it);
  - COT flag: Friday 14:30 CT release (15:30 ET) falls after the 13:20 CT day close, so the first ZM session that can
    react is Sunday 19:00 CT. Any COT-based feature must be stamped no earlier than that release, never at the Tuesday
    as-of date.
- A directional "front-run the index roll" family for ZM is weak: BCOM's ZM weight is about 3.5%, the published
  evidence is for GSCI (which, at least to 2013, did not hold ZM), the Mou result is unverified here, and the
  Dubois-Marechal counterpoint (search snippet only) says the edge vanished after costs. Keep it as a flag.
- Regime break to state in the protocol: federal limits changed with the 2020 final rule (compliance 2022 for
  exchanges), between the sealed test window (2017-2020) and discovery (2020-12 to 2024-02).

## (d) Seasonality of liquidity: intraday pattern, day versus overnight, growing season, report days

### d.1 Facts

- Intraday U shape in CBOT grains [academic]:
  - Ma and Serra working version (R3b_afajof_63476_ma_serra.pdf, CME corn, soybean and wheat MBO 2019-01 to 2020-06):
    "the intra-session distribution of market activity is specially concentrated at the market open and close for
    both the day and night trading sessions, leading to the well-known 'U' shape activity pattern" and "the night
    session activity reaches a minimum at around 12 a.m., and subsequently increases reaching peaks at around 7:30 a.m.,
    i.e., 15 minutes before the night session closes." They tie the day-session U to liquidity providers "who do not
    hold significant overnight positions and thus unwind their positions before the end of day".
  - Wang (NCCC-134 2019, R3b_wang_nccc2019_invariance.pdf, corn, soybeans, wheat nearby, 2008-01 to 2015-05, 1-minute
    averages over the day session): "all other metrics of trading activity show the well-known U-shape of intraday
    seasonality, namely higher activity at the beginning and the end of the trading day."
- Day versus overnight:
  - ZM's day session carried 0.83 of front-contract volume in E.28's standard window (READER_BRIEF table, from
    reports/stage_e28_briefs/A0_contract_stats.md Table 1; ZS 0.78, ZL 0.82).
  - Ma and Serra: "most trades occur during the day trading session (e.g., Lehecka, Wang, and Garcia 2014)" and the
    same holds for limit-order submission, execution, deletion and revision (their Figure D1).
  - Peng, Hu, Robe and Adjemian (R3b_peng_hu_robe_adjemian_2021.pdf) analyse day and overnight sessions separately and
    find the 2020 soybean depth collapse "in both the outright and calendar spread markets, and in the daytime and
    overnight sessions" [academic].
  - Overnight market-maker incentives existed for corn, wheat and soybeans from 2009 [regulator-hosted CBOT filing,
    R3b_cftc_rul100909cbot001.pdf]: "Limited to Extended Trading Hours (ETH) from 6PM -7:15AM Chicago time"; soybean
    meal is not named in that program. Whether a ZM program ran in 2017-2024 was not found.
  - A CME 2022 article ranks Asia-hours spreads "corn ... followed by Soybean, Soybean Meal, Wheat, and Soybean Oil"
    [unverified: search snippet of a cmegroup.com page, not fetched under the stage rule].
- Growing season and contract cycle [academic] (Wang, Garcia and Irwin, corn BBO 2008-2010, E.28-saved
  reports/stage_e28_briefs/pages/A1_grains/agecon_wang_garcia_irwin_confp04-12.txt, abstract): "Over the extended
  horizon that a contract is traded there exist a pronounced non-linear U-shaped maturity pattern, and a strong
  seasonality consistent with the term structure of implied volatilities." "the BAS is generally small (well below two
  ticks)". "USDA Grain Stock and Production-WASDE announcements significantly widen the BAS, as do short-term price
  trends. The index fund roll has little impact on the BAS, but contract specific effects are present reflecting a
  seasonal pattern where the BAS is lowest in December, and highest in September." No ZM-specific seasonal liquidity
  study was found (stopping rule: three discovery searches on ZM liquidity seasonality surfaced only ZS, corn or CME
  marketing material).
- Report days [academic]: Ma and Serra study "90 minutes before, during and after the WASDE announcements" (released
  "monthly at 11:00 Central Time"; 17 announcement days in their sample): "the uncertainty prior to the announcement
  causes a change in trading strategy, with the most aggressive limit orders, especially aggressive cancellations, and
  aggressive trades triggering larger price impacts (up to 2 bps) than on non-announcement days." Arzandeh and Frank
  (footnote 9) cite Lehecka et al. (2014): "announcement effects of major USDA reports on corn futures prices and volume
  disappear in ten minutes" [secondary citation; Lehecka et al. not read here; R4_events owns report effects].
- Stress regime inside the sealed test window [academic] (Peng et al. 2021, abstract lines 59-68): "soybean
  futures-market depth collapses weeks before" the March 2020 crash; "Soybean depth drops by half for outright futures
  and by over 90 percent for calendar spreads"; the pullback "coincides with overnight news of bleak COVID-19
  developments in China".
- E.31 (reports/E.31_RETURN.md line 202): passive ZM fills "0-5 minutes after a USDA release -8.98 (68 fills)" ticks
  gross at 10 s, the worst bucket measured.

### d.2 Worked example: what a one-tick spread costs in basis points at ZM prices, and how volatility scales by session

- One ZM tick is 0.10 USD/short ton. At a price of 400 USD/short ton: 0.10 / 400 = 0.00025 = 2.5 bp. At 300 USD/ton:
  0.10 / 300 = 0.000333 = 3.33 bp. Check: 2.5 bp x 400 / 300 = 3.33 bp.
- A 1-lot round trip by market orders against a one-tick spread pays one tick (half a tick each way) plus fees:
  1 tick + 0.528 ticks (Topstep 5.28 USD / 10.00 USD per tick) = 1.528 ticks, about 1.53 x 2.5 = 3.8 bp at 400 USD/ton.
  This sits just under E.28's market-order break-even for Topstep ZM, reports/stage_e28_ranking.md line 130:
  "| 6 | topstep | ZM | 2.69 | 2 | 4 | 2 | 1 | 2 | 3 | 2.475 | 2.150 | 2.312 | 0.59 | 1.59 | ..." (header line 123:
  "... | mu*_lim | mu*_mkt | ..."), so mu*_mkt = 1.59 ticks. Check: 1.59 - 1.528 = 0.06 ticks, which E.28's model
  attributes to more than a pure one-tick spread [E.28's cost model not re-derived here].
- Volatility per horizon under a random-walk assumption (stated): sigma_h = sigma_1m x sqrt(h), sigma_1m = 3.15 ticks
  (E.28 A0, regular dates). 5 min: 3.15 x 2.236 = 7.04 ticks; 15 min: 3.15 x 3.873 = 12.20; 60 min: 3.15 x 7.746 =
  24.40. Check: 24.40 / 7.04 = 3.47, and sqrt(60/5) = sqrt(12) = 3.46. The 3.15 figure is an all-session regular-date
  average; the U shape means the open, the close and report minutes carry more of it, and the overnight hours less.
  How much less is not recorded in E.28 A0 [no figure available; E.33 must measure it on discovery data].

### d.3 What this means for a ZM directional search

- Time of day is a first-order conditioner: costs (spread, depth) and volatility both follow the U, so any label or
  feature must be stratified by session and hour (the planner's mandatory strata). A rule that trades evenly through
  the overnight will pay the same 1.53 ticks against much smaller expected moves.
- The overnight minimum near midnight CT and the peak near 07:30 CT (Ma and Serra, grains) suggest the overnight-to-day handover
  (planner family 4, gap at the 08:30 open) sits in the liquid part of the cycle; the 00:00-06:00 CT stretch is the
  thin part, where a market order's cost relative to the move is worst.
- Report windows: exclude a fixed window around 11:00 CT WASDE (and other USDA releases R4 lists) from any
  non-event family; E.31's -8.98 ticks for passive fills 0-5 minutes after releases shows how toxic those minutes are.
- Seasonality by contract month and growing season is documented for corn spreads, not ZM; leave it as a stratum to
  report, not a family.
- The February-April 2020 soybean liquidity collapse sits inside the sealed test window (2017-05 to 2020-11). A model
  selected on 2020-12 to 2024-02 meets a stress regime in the test that discovery never saw; the protocol should say so
  in advance.

## (e) Liquidity costs and spillovers across the soybean complex

### e.1 Facts

- de Boer, Gardebroek, Pennings and Trujillo-Barrera, "Intraday liquidity in soybean complex futures markets", J.
  Futures Markets 42(7) 1189-1211, 2022 [academic]. Abstract only (WUR research portal, R3b_wur_deboer2022.html;
  full text not reachable: Wiley pdfdirect 403 (R3b_wiley_deboer2022.pdf, a 5.8 kB block page), no repository file at
  WUR or Maastricht; OpenAlex lists it as "green" but the only OA location is the WUR landing page without a file):
  "A multidimensional liquidity measure is derived from the limit-order-book, and a Vector Heterogeneous Autoregressive
  model estimates high-resoluted liquidity from 30 s to one trading day. We find traders' order placement influenced by
  the liquidity of related markets. Liquidity persistence and positive liquidity spillovers mainly occur within 30 s,
  whereas spillovers for longer horizons are mostly negative." The round-trip costs the planner quotes (9.2 bp ZS,
  12.5 bp ZL, 13.6 bp ZM) and the 2015 sample year are not in the abstract [unverified].
- A liquidity measure of that kind, from the same research group [academic] (Zhou, Bagnarosa, Gohin, Pennings and
  Debie, J. Commodity Markets 30 (2023) 100314, saved by R3a: reports/stage_e32_briefs/pages/R3a_crush/
  zhou_jcm2023_wur.pdf.txt lines 619-633), the Exchange Liquidity Measure:
  "The XLM (Exchange Liquidity Measure) calculates the round-trip liquidity premium for buying and selling a chosen
  volume, i.e., how much the average transaction price deviates from the mid-price."
  Equations (their (17)-(19)):
      XLM_B,t(V) = 10,000 x (P_B,t(V) - MP_t) / MP_t
      XLM_S,t(V) = 10,000 x (MP_t - P_S,t(V)) / MP_t
      XLM_t(V)   = XLM_B,t(V) + XLM_S,t(V)
  "where, MP_t is the mid-price at time t, P_B,t(V) is the average transaction price of a buy-initiated market order
  with dollar value V at time t, P_S,t(V) is the average transaction price of a sell-initiated market order with dollar
  value V at time t". In Zhou et al. "the dollar value is set to be the median dollar value of the order book spanning
  the full year." Whether de Boer et al. use XLM and which V is not verified [inferred: same group, "multidimensional
  liquidity measure ... derived from the limit-order-book"].
  Zhou et al. (line 125): "volume is significantly related to crush-spread cointegration in certain markets,
  particularly soymeal."
- Information beyond the touch, soybeans (ZS) [academic] (Arzandeh and Frank, CAES 2017 working version of the AJAE
  2019 paper, R3b_arzandeh_frank_caes2017.pdf; CME market-depth data 23 Nov 2015 to 31 Mar 2016, ten-level book):
  abstract: "the steps of the LOB beyond the BAS contribute by over 27% to price discovery of futures contracts" (all
  six contracts); soybeans: midpoint IS "30.16% for soybeans", PT "soybeans (43.72%)", MIS "40.66% for soybeans";
  sampling interval = average price duration: "average price duration is 7.60 seconds for soybeans, lower than that
  for corn, 8.63 seconds". Soybean meal is not in their sample.
- What carries price discovery in the soybean book (ZS, corn, wheat) [academic] (Ma and Serra working version,
  R3b_afajof_63476_ma_serra.pdf, MBO 2019-01-07 to 2020-06-26, day session, daily SVAR information shares, medians):
  "while trades moving the BBO contribute by about 27%-30% to corn and soybean price discovery, they represent around
  42% of the wheat price discovery. Limit order submissions or cancellations moving the BBO jointly represent around
  56% of the corn and soybean price discovery". The SVAR "is estimated daily for each market and each trading
  session" in event time; information shares are variance shares of the efficient-price innovation (a contemporaneous
  and short-lag attribution, not a forecast of future returns). Their method: "We consider both implied and outright liquidity in
  our analyses." The published AJAE 2025 version (doi 10.1111/ajae.12479, cc-by-nc-nd per OpenAlex) was not read; its
  IDEAS abstract (saved by M1) gives the deletion share as "Between 75% and 79%".
- Cross-product lead-lag in seconds is M2's topic (reports/stage_e32_briefs/M2_lead_lag.md); not repeated here.

### e.2 Worked example: converting a basis-point round-trip cost into ZM ticks

- A 1-lot at a one-tick ZM spread, mid 400.00 USD/ton: P_B = 400.05, P_S = 399.95. XLM_B = 10,000 x 0.05 / 400 =
  1.25 bp; XLM_S = 10,000 x 0.05 / 400 = 1.25 bp; XLM = 2.50 bp = 1 tick. Check: 1 tick / 400 x 10,000 = 2.5 bp.
- The planner's 13.6 bp for ZM, IF it is an XLM round trip: at 400 USD/ton, 13.6 / 10,000 x 400 = 0.544 USD/ton =
  5.44 ticks; at 300 USD/ton, 13.6 / 10,000 x 300 = 0.408 USD/ton = 4.08 ticks. Both are several times a one-tick
  spread, so the figure must refer to an order far larger than 1 lot (a median-book dollar value in Zhou et al.'s
  definition), not to a 1-lot trader's cost. Check: 5.44 / 4.08 = 1.333 = 400 / 300.
- Ratios between legs (if the planner's numbers are right): ZM / ZS = 13.6 / 9.2 = 1.48; ZL / ZS = 12.5 / 9.2 = 1.36.
  Cross-leg bp ratios say nothing about ticks per leg without each leg's price and V.

### e.3 What this means for a ZM directional search

- "ZM is the least liquid leg" is plausible but unverified here; what matters to a 1-lot is the touch spread and depth,
  which the owned ZM MBO measures directly. E.33 should report ZM's spread distribution by session and hour from
  discovery data before any cost assumption is frozen; a bp figure for a large V must not be used as a 1-lot cost.
- Spillovers "within 30 s" and negative beyond: the cross-product liquidity link is a seconds-scale effect. At minutes
  scale, use ZS/ZL liquidity state (spread, depth, recent sweep) only as a conditioner of ZM features; do not build a
  family on "liquidity spills into ZM later" (the abstract says longer-horizon spillovers are mostly negative).
- Information is in the book, not only in trades: in ZS, cancellations and submissions that move the BBO carry about
  56% of price discovery and trades that move it about 27-30%; levels beyond the touch carry 30-44% by the various
  measures in late 2015-early 2016. For ZM this supports MBO-based features (BBO-moving cancellations, depth beyond
  the touch) as conditioners, with two caveats: these are contemporaneous attributions, not forecasts (the planner's
  note says the same), and ZM was in neither sample.
- Mechanism to drop: any claim that a single "leader" leg sets the price for minutes; nothing read here supports a
  minutes-scale liquidity lead from ZS or ZL into ZM.

## Summary: what this means for a ZM directional search (all sections)

Worth testing (as conditioners or flags, frozen before E.33 looks at returns):
1. Session and hour strata, report-window exclusions (11:00 CT WASDE and R4's list), notice and roll flags (sections c
   and d). These change cost and volatility more than any book feature.
2. MBO book features at and beyond the touch (BBO-moving cancellations and submissions, depth at levels 2+) as
   conditioners, with the pro-rata over-sizing confound written into their definitions (sections a and e).
3. Side-None or no-resting-quantity prints as a candidate flag for implied (calendar or crush) flow, with the share of
   such prints reported (section b).
4. ZS/ZL liquidity state (spread, depth, sweeps) as a conditioner of ZM, not as a lead signal (section e).

Drop:
- queue-position modelling for a 1-lot under K (section a);
- any feature that needs implied depth (the owned data cannot rebuild it; section b);
- a "front-run the index roll" alpha family for ZM (section c; BCOM weight about 3.5%, GSCI did not hold ZM through
  2013, Wang-Garcia-Irwin find the roll has "little impact on the BAS" in corn, Mou unverified);
- minutes-scale cross-product liquidity spillover as a signal (section e; the abstract puts positive spillovers within
  30 s).

Data-handling rules for E.33 that follow from these facts (proposals for the lead; not decisions):
- labels never cross a ZM.v.0 contract switch; the switch day is flagged;
- COT features time-stamped at Friday 14:30 CT, usable from the Sunday 19:00 CT open;
- costs from the owned outright touch (conservative), never from a bp figure measured for a large order;
- the 2020 COVID liquidity collapse and the 2021-2022 change in federal position limits are named in advance as
  regime differences between the sealed test window and discovery.

## Planner pointers: verification table

| Planner claim | Status | Evidence (file) | What differs or why |
|---|---|---|---|
| de Boer et al. JFM 2022: liquidity spillovers mostly within 30 s | VERIFIED (abstract) | R3b_wur_deboer2022.html: "Liquidity persistence and positive liquidity spillovers mainly occur within 30 s, whereas spillovers for longer horizons are mostly negative." | Abstract only; full text not reachable (Wiley 403, no repository file). The abstract says POSITIVE spillovers within 30 s and mostly negative beyond. |
| de Boer et al.: round-trip liquidity cost 9.2 bp ZS, 12.5 bp ZL, 13.6 bp ZM; ZM least liquid; 2015 data | UNVERIFIED | none | Not in the abstract; full text unread. If the measure is XLM at a median-book dollar value (as in Zhou et al. 2023, same group), 13.6 bp is 4-5.4 ZM ticks for a large order, not a 1-lot cost (section e.2). |
| Arzandeh and Frank AJAE 2019: soybean price duration about 7.6 s | VERIFIED (working-paper version) | R3b_arzandeh_frank_caes2017.pdf: "average price duration is 7.60 seconds for soybeans" | From the CAES 2017 version of the same study (Nov 2015-Mar 2016 data); the AJAE 2019 text was not read. ZS, not ZM. |
| Arzandeh and Frank: book levels beyond the best quote carry more than 27% of price discovery | VERIFIED (working-paper version), with a nuance | same file: "the steps of the LOB beyond the BAS contribute by over 27% to price discovery of futures contracts" | "Over 27%" is the floor across all six contracts; for soybeans the shares are 30.16% (ISM), 43.72% (PT), 40.66% (MIS). |
| Ma and Serra AJAE 2025: trades moving the best quote 27-30% of discovery | VERIFIED (working-paper version) | R3b_afajof_63476_ma_serra.pdf: "trades moving the BBO contribute by about 27%-30% to corn and soybean price discovery" | Working version (AFA listing), not the AJAE text. Corn and soybeans (ZS); wheat about 42%. Day session, median daily IS. |
| Ma and Serra: limit submissions and cancellations at the touch about 56% | PARTLY VERIFIED | same file: "Limit order submissions or cancellations moving the BBO jointly represent around 56% of the corn and soybean price discovery" | The paper says "moving the BBO" (improving submissions and worsening cancellations), not "at the touch"; submissions and cancellations AT the BBO that do not move it are a separate, marginal category. |
| Ma and Serra: contemporaneous; no forward-looking OFI evidence for grains | PARTLY VERIFIED | same file: SVAR "estimated daily for each market and each trading session"; IS as variance decomposition | The method is a contemporaneous/short-lag attribution; "no forward-looking OFI evidence exists for grains" is a literature claim this worker did not search exhaustively (M1 owns OFI). |
| K algorithm: TOP priority capped at 100 contracts on grain outrights | VERIFIED | R3b_cftc_aac041119_cmegroup.pdf (CFTC-hosted CME slide): "TOP MAX in grain outrights is 100 contracts and 1000 contracts in grain spreads." | E.31 found ZM-ZM spread rows showing 100, not 1000, in the product sheet [E.31 cmegroup-origin]. |
| K algorithm: then 40% FIFO, then 60% pro rata with levelling, then FIFO residual | VERIFIED | same file: "40% of the incoming aggressing order is allocated by timestamp"; "60% ... based on the size of the resting orders"; levelling "maximum of 1 contract allocated per order"; "Any residual quantity remaining is filled FIFO." | Levelling eligibility wording differs between the CFTC slide and the CME wiki (section a.1). |
| K algorithm applies to ZM | VERIFIED (owned data, via E.31) | reports/E.31_RETURN.md line 168: "all outrights K" | The CFTC slide says "Grain Futures" without listing products. |
| Globex uses FIFO when the aggressor's size is at least all displayed quantity at the price | PARTLY VERIFIED | E.31-saved CME wiki (cmegroup-origin, not re-fetched): "greater than or equal to the displayed quantity ... CME Globex applies FIFO in lieu of the designated product algorithm" | No CFTC-hosted or academic copy found; rests on a cmegroup-origin file, which the E.32 stage rule does not allow this worker to fetch. |
| Sources named: CME filing 14-270; Peng JFM 2024 | NOT FOUND / NOT A K SOURCE | R3b_ideas_peng_hu_robe_2024.html | Filing 14-270 was not located on cftc.gov (one search). "Peng JFM 2024" is Peng, Hu and Robe, "Maximum order size and market quality", JFM 44(5) 803-825: its abstract is about the 2018 maximum-order-size increase (2,500 to 10,000) in calendar spreads, not about K; full text 403 (Wiley). |
| Implied intercommodity spreads (board crush SOM 10 ZS:11 ZM:9 ZL; calendars; butterflies; ZM-MZM) feed the outright book | PARTLY VERIFIED | Ma et al. 2026 (calendar implieds feed outrights); Peng et al. 2021 (implied-out/implied-in); E.31-saved CME page ("Soybean Crush spreads" are ICS ratio spreads in predetermination) | SOM legs 10:11:9 from R3a and a search snippet only; butterflies and ZM-MZM implieds not checked. |
| Implied bids and offers are eligible but "not disseminated in market data" | PARTLY VERIFIED | E.31-saved CME page: "(these implieds will not be visible via market data)" in the ratio-spread (ICS) context; Databento docs: CME's MBP feed carries "2 levels of implied liquidity" | True for ratio-spread (crush) implieds; FALSE as a general statement: calendar-spread implieds ARE disseminated, on the MBP feed's implied book (2 levels), though not in MBO (and so not in the owned ZM MBO or the owned MBP-1). The exact phrase was not found in any file this stage may read. |
| Ranked family 8: index roll, first notice day and COT as regime flags or exclusions | SUPPORTED as flags | BCOM methodology (ZM roll BD 6-10 in Feb/Apr/Jun/Oct/Dec); Hu-Peterson (GSCI BD 5-9, no ZM to 2013); CBOT ch. 13 (E.28 file); CFTC COT page (Fri 15:30 ET, Tuesday data); Wang-Garcia-Irwin (roll has "little impact on the BAS", corn) | Not supported as an alpha family (section c.3). First notice day definition rests on an inference from two price-limit rules plus a search snippet. |

## Evidence table

| # | Claim | Source (label) | Verbatim quote | Saved file |
|---|---|---|---|---|
| 1 | K in grain futures: TOP cap 100 outrights | CME slide to CFTC AAC 2019-04-11 (exchange, regulator-hosted) | "TOP MAX in grain outrights is 100 contracts and 1000 contracts in grain spreads." | pages/R3b_microstructure/R3b_cftc_aac041119_cmegroup.pdf |
| 2 | K FIFO 40% | same | "40% of the incoming aggressing order is allocated by timestamp." | same |
| 3 | K pro rata 60% | same | "60% of the incoming aggressing order is allocated based on the size of the resting orders." | same |
| 4 | Levelling 1 lot max | same | "Any order that did not participate in the Pro-Rata pass is eligible for rounding with a maximum of 1 contract allocated per order." | same |
| 5 | Realized allocation shares | same | "~7% TOP", "~56% FIFO", "~23% Pro-Rata", "~14% Leveling" | same |
| 6 | ZM outrights are K (owned data) | E.31 return (program record) | "all outrights K" | reports/E.31_RETURN.md line 168 |
| 7 | FIFO exception for sweeps | CME client wiki (exchange) [E.31 cmegroup-origin, not re-fetched] | "greater than or equal to the displayed quantity ... CME Globex applies FIFO in lieu of the designated product algorithm" | reports/stage_e31_briefs/research/K_algorithm.md (a) |
| 8 | Pro-rata markets oversize and cancel | Field and Large 2008 (academic) | "strategic complementarities in the choice of limit order size cause traders to risk overtrading by submitting over-sized limit orders, most of which they expect to cancel." | R3b_field_large_2008_prorata.pdf |
| 9 | Grain limit-order life | Ma and Serra WP (academic) | "around 75-79% are deleted and 7%-8% revised" / "half of the limit orders being deleted within 2-5 seconds" | R3b_afajof_63476_ma_serra.pdf |
| 10 | Implied functionality mechanism | Ma, Serra, Peterson, Irwin 2026 (academic) | "liquidity in calendar spreads generates synthetic and contingent quotes in outrights" | R3b_richie_ma_serra_2026_calendar_spreads.pdf |
| 11 | Implied share of touch depth, corn/soy | same | "For the first-nearby futures, implied liquidity contributes 16.00%-17.97% to consolidated liquidity, rising to 50.97%-52.48% for second-nearby futures." | same |
| 12 | Outright priority over implied | same (citing CME 2007) | "outright quotes have matching priority over implied quotes (CME 2007)" | same |
| 13 | Implied-out / implied-in definitions | Peng, Hu, Robe, Adjemian 2021 (academic) | "orders in the outright book created based on orders in the spread market ("implied-out") or ... orders in the calendar spread book created based on orders in the outright market ("implied-in")" | R3b_peng_hu_robe_adjemian_2021.pdf |
| 14 | MBP feed: 2 implied levels | Databento GLBX.MDP3 docs (firm) | "The MBP feed provides up to 10 levels of real liquidity and 2 levels of implied liquidity." | R3b_databento_glbx_mdp3.md |
| 15 | Merged book only in CMBP-1 | same | "Databento combines the real and implied books, publishing the merged top-of-book on the [CMBP-1] schema." | same |
| 16 | Implied trades lack aggressor side | same | "Implied trades ... may not have an aggressing side set. These trades will be normalized with side set to None." | same |
| 17 | Implied matches lose order details | Ma and Serra WP (academic) | "Order details (e.g., order ID, matched quantity, aggressor) are not provided for those market orders that are executed against implied order(s)." | R3b_afajof_63476_ma_serra.pdf |
| 18 | Crush is an ICS ratio spread; ratio implieds not visible | CME wiki (exchange) [E.31 cmegroup-origin, not re-fetched] | "Examples include Treasury ICS and Soybean Crush spreads." / "(these implieds will not be visible via market data)" | reports/stage_e31_briefs/research/pages/K/wayback_algorithms_near20231201.txt |
| 19 | Implied never matches implied | same | "Implied quantity will never match with implied quantity." | same |
| 20 | CME switched corn implieds off in 2010 | Overdahl 2011, FIA-PTG sponsored (practitioner) | "On Jan. 31, 2011, the CME turned on implied matching functionality for corn futures after turning off this functionality in August 2010." | R3b_nera_overdahl_2011.pdf |
| 21 | ZM months | CBOT Rulebook ch. 13 (exchange) [E.28 cmegroup-origin, not re-fetched] | "eight months - September, October, December, January, March, May, July, and August" | reports/stage_e28_briefs/pages/A1_grains/cbot_rulebook_ch13.txt |
| 22 | ZM last trading day | same | "after the business day preceding the 15th calendar day of that month" | same |
| 23 | Limits off before delivery month | same | "no price limits on the current month contract on or after the second business day preceding the first day of the delivery month" | same |
| 24 | Limits off before FND | CME (exchange) [E.0 cmegroup-origin] | "price limits are removed on the business day prior to first notice day of an expiring contract month" | reports/stage_e0_research_K6.md line 672 |
| 25 | Federal ZM spot limit | CFTC speculative limits page (regulator) | "CBOT Soybean Meal (SM) | 1,500" (spot month, 2020 final rule) | R3b_cftc_speculative_limits.html |
| 26 | Federal ZM single/all-months limit | same | "CBOT Soybean Meal (SM) | 16,900" | same |
| 27 | BCOM roll window | BCOM methodology (firm) | "the sixth through tenth Business Days of the month ... at the rate of 20% per Business Day" | R3b_bcom_methodology.pdf |
| 28 | BCOM ZM contract calendar | same | "Soybean Meal Mar Mar May May Jul Jul Dec Dec Dec Dec Jan Jan" | same |
| 29 | GSCI roll window | Hu and Peterson NCCC-134 2014 (academic) | "each day from the 5th business day to the 9th business day of the month" | R3b_nccc_gsci_roll_returns.pdf |
| 30 | GSCI CBOT constituents 2007-13 | same | "Corn, Chicago Wheat, and Soybeans, all traded at Chicago Board of Trade (CBOT)" | same |
| 31 | Grain roll timing | Arzandeh and Frank WP (academic) | "traders of grains, on average, roll their position over three weeks before the expiration date of their contract." | R3b_arzandeh_frank_caes2017.pdf |
| 32 | COT timing | CFTC COT page (regulator) | "generally published each Friday at 3:30 pm Eastern Time (US), using the data from the immediately preceding Tuesday" | R3b_cftc_cot_index.html |
| 33 | Intraday U, day and night | Ma and Serra WP (academic) | "concentrated at the market open and close for both the day and night trading sessions, leading to the well-known 'U' shape" | R3b_afajof_63476_ma_serra.pdf |
| 34 | Night minimum and 07:30 peak | same | "the night session activity reaches a minimum at around 12 a.m., and subsequently increases reaching peaks at around 7:30 a.m." | same |
| 35 | U shape 2008-2015 grains | Wang NCCC-134 2019 (academic) | "all other metrics of trading activity show the well-known U-shape of intraday seasonality" | R3b_wang_nccc2019_invariance.pdf |
| 36 | Corn BAS: reports widen, roll little impact, seasonal | Wang, Garcia, Irwin (academic) [E.28-saved] | "The index fund roll has little impact on the BAS, but contract specific effects are present reflecting a seasonal pattern where the BAS is lowest in December, and highest in September." | reports/stage_e28_briefs/pages/A1_grains/agecon_wang_garcia_irwin_confp04-12.txt |
| 37 | WASDE window price impacts | Ma and Serra WP (academic) | "aggressive trades triggering larger price impacts (up to 2 bps) than on non-announcement days" | R3b_afajof_63476_ma_serra.pdf |
| 38 | 2020 soybean depth collapse | Peng et al. 2021 (academic) | "Soybean depth drops by half for outright futures and by over 90 percent for calendar spreads" | R3b_peng_hu_robe_adjemian_2021.pdf |
| 39 | Overnight MM program (corn, wheat, soybeans, 2009) | CBOT filing (exchange, regulator-hosted) | "Limited to Extended Trading Hours (ETH) from 6PM -7:15AM Chicago time" | R3b_cftc_rul100909cbot001.pdf |
| 40 | Soy-complex spillovers within 30 s | de Boer et al. 2022 abstract (academic) | "Liquidity persistence and positive liquidity spillovers mainly occur within 30 s, whereas spillovers for longer horizons are mostly negative." | R3b_wur_deboer2022.html |
| 41 | XLM definition | Zhou et al. JCM 2023 (academic) [R3a-saved] | "The XLM (Exchange Liquidity Measure) calculates the round-trip liquidity premium for buying and selling a chosen volume" | reports/stage_e32_briefs/pages/R3a_crush/zhou_jcm2023_wur.pdf.txt |
| 42 | Beyond-BBO information share | Arzandeh and Frank WP (academic) | "the steps of the LOB beyond the BAS contribute by over 27% to price discovery of futures contracts" | R3b_arzandeh_frank_caes2017.pdf |
| 43 | Soybean price duration | same | "average price duration is 7.60 seconds for soybeans" | same |
| 44 | BBO-moving trades and orders, ZS | Ma and Serra WP (academic) | "trades moving the BBO contribute by about 27%-30% to corn and soybean price discovery" / "Limit order submissions or cancellations moving the BBO jointly represent around 56%" | R3b_afajof_63476_ma_serra.pdf |
| 45 | Index-roll front-running profits | Mou 2010/2011 | Sharpe ratios "as high as 4.4" (abstract wording via search snippet) | none [unverified] |
| 46 | SOM legs 11 ZM, 9 ZL, 10 ZS | CME 2009 notice | "Eleven (11) Soybean Meal futures contracts" (search snippet) | none [unverified] |
| 47 | Planner round-trip bp costs | de Boer et al. 2022 | none | none [unverified] |

## Search log and stopping

- WebSearch calls used: 18 of 80. No budget notice was seen.
- Topics closed by the stopping rule: (a) K: CFTC slide plus E.31's record; two further searches for CFTC-hosted grain
  K filings surfaced only Treasury and swap filings. (b) implied: three full-text sources (Ma et al. 2026, Peng et al.
  2021, Databento docs) plus E.31's CME page; Arzandeh et al. 2025 (SSRN only) and CME 2007 not reachable.
  (c) roll and delivery: BCOM, Hu-Peterson, CBOT ch. 13, CFTC limits and COT pages; FND definition not found in an
  allowed full text after two searches. (d) seasonality: Ma-Serra, Wang 2019, Wang-Garcia-Irwin, Peng et al. 2021;
  three searches for ZM-specific liquidity seasonality found nothing new. (e) costs and spillovers: de Boer full text
  unreachable after five routes (Wiley, WUR, Maastricht, NCCC archive, OpenAlex OA lookup).

## Not finished, null results and blocks

- de Boer et al. 2022 full text: not reached (Wiley 403; no repository PDF; the 2019 IATRC and 2020 NCCC versions
  are not in the NCCC archive). Its bp costs stay UNVERIFIED.
- AJAE published versions of Arzandeh-Frank (2019) and Ma-Serra (2025) not read (Wiley); working versions used.
- Peng, Hu and Robe JFM 2024 full text 403; SSRN copy not tried (SSRN blocked). IDEALS (Peng thesis) returns 403.
- S&P GSCI methodology PDF: 403; post-2013 GSCI composition unverified. Mou thesis: Columbia bot wall.
- eCFR: the API renderer is disallowed by robots.txt, so that file was deleted unused; the public page is JavaScript;
  the GPO appendix table is an image. Federal limits came from the CFTC page instead; pre-2021 legacy levels and the
  spot-month definition are unverified.
- CME pages (contract specs, SOM notice, Asia-hours article, client wiki "Implied Intercommodity Ratio Spreads") were
  not fetched under the stage rule; facts that rest on earlier stages' cmegroup-origin files are marked.
- Unresolved: how K orders outright versus implied quantity at one price for ZM (Ma et al.'s "outright priority"
  versus the wiki's source-level predetermination).
