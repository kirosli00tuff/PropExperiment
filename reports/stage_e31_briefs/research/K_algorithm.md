# CME Globex match algorithm K (Configurable) for CBOT soybean meal (ZM) outrights, 2023-11 to 2024-02

Stage E.31, KResearch-OpusHigh (opus, high). Research only. Every quote below was taken from a page
saved under reports/stage_e31_briefs/research/pages/K/ and checked by grep against that file. URLs, UTC fetch
times and sha256 values are in K_fetch_log.md. Anything not from fetched full text is marked [unverified]
or [inferred].

## Sources

| ID | Source | Date of content | File (pages/K/) | sha256 (raw) |
|---|---|---|---|---|
| S1 | CME Globex Product Reference Sheet, Wayback 2023-06-22 (reused from E.28) | sheet date cell 2023-06-21 | globex_product_reference_sheet_20230622.xls | 6f72263dc1d9f53de8abc161e13ed66e48dbcf573bc40abf9f9e30d8fceebb25 |
| S2 | CME Globex Product Reference Sheet, Wayback 2024-02-26 (reused from E.28) | sheet date cell 2024-02-26 (inside the window) | globex_product_reference_sheet_20240226.xls | f9efaa713452fa1416a21feab03762950fa590e032f07afc5dca3c4db71f3018 |
| S3 | CME Client Systems Wiki (old cmegroup.com Confluence), "CME Globex Matching Algorithm Steps", Wayback capture 2023-06-20 | "last modified on Jan 26, 2023" | wayback_steps_near20231201.html (gzip; .decoded is the unzipped copy) | 0ae6cb4b8a5516d0b5955e780906d91a18f9ba2d85dd22fb7c3d284638d1d52b |
| S4 | Same page, current Atlassian wiki (cmegroupclientsite.atlassian.net, page 457218521) | moved to Atlassian 2024-12-21; header says "Updated Jun 02" | wiki_matching_algorithm_steps_current.html | fc7b04730539ca5cb278b7af48873133a339cde0ff28e1989ba7e833a00436f0 |
| S5 | Old wiki, "Supported Matching Algorithms", Wayback capture 2023-12-10 (inside the window) | "last modified on Sep 11, 2023" | wayback_supported_matching_algorithms_near20231201.html | 5e1e4575d6b5388f1ae24a13e2084711825a1f83508d16c7e0ba70747bdc884c |
| S6 | Old wiki, "CME Globex Matching Algorithms" (implied / predetermination rules), Wayback capture 2023-10-02 | "last modified on May 04, 2023" | wayback_algorithms_near20231201.html | 1f655eaed2f8fa4d0136f2ca484df5f74172dc23f7c04735bc2157fc568bd3d2 |
| S7 | CME Globex Notices 2023-09-18 (Wayback), "TOP Order Allocation Maximum Quantity Enhancement - October 1" (same text in the 2023-09-25 notice, globex_notice_20230925.html) | 2023-09-18 | globex_notice_20230918.html | 74cf66326e9075e944d62529cf940ad656595c909d7a51f95179f035fdb281f1 |
| S8 | CME Group presentation to the CFTC Agricultural Advisory Committee, 2019-04-11 (cftc.gov) | 2019 | cftc_aac041119_cmegroup.pdf | e4bac443ce36269a939b5c1c6ee1ae125cbdd04c9bf0e2efb8403f478847867c |
| S9 | CME SER-7180 (KC HRW wheat algorithm change), Wayback | 2014-08-29 | ser7180.pdf | e3cee03fd3e4ac05e4ecf23a32bd6df4fdd88a1400ff015724f475dbdb673ce0 |
| S10 | Wiki "Complex Match Example": current (Atlassian) and Wayback capture 2022-11-29 | old copy "last modified on Aug 11, 2020" | wiki_complex_match_example_current.html; wayback_complex_near20231201.html | ad282afb60df43daf398d9e77c3d74c850a9a1562a6cc7afbb8535885634c696; 659250e3347c64305b35fd34406f2d97e76fd3bffaa0190f783f3ca133c8c1ac |
| S11 | Older captures of the Steps page, used only to date changes: 2021-09-20 and 2022-05-03 (both "last modified on Aug 04, 2021") | 2021 | wayback_20210920_matching_algorithm_steps.html; wayback_20220503_matching_algorithm_steps.html | ba6254df18c9f496f8ceb6b8b2b0f5264051fd3ecdecd041b7de28afa0065318; a5d25e398d776741a645db95fc2b4759d00eaffa6723f56826cd40caba619e87 |

Which version applies to the window. No capture of the Steps page exists between 2023-06-20 (S3) and the
Atlassian move (S4). A text diff of S3 against S4 shows that the Split, FIFO, Pro Rata, PR Min, Leveling, LMM
and FIFO-exception sections are word-for-word the same in both (and in the 2021 copy, S11). Only the TOP
section differs. One TOP difference, how TOP Max is counted, is dated by the notice S7 to 2023-10-01,
before the window, so S4's TOP Max text applies to the window. The other TOP difference, the rules on
modifications, cannot be dated (see section (d)). The K section of S5 (captured 2023-12-10, inside the window)
is the same text as the current Supported Matching Algorithms page.

## (a) Parameter table

The product sheet's ZM row is the same in S1 (2023-06-21) and S2 (2024-02-26); row 33 of "All Futures and
Options". The header names (sheet row 2) are quoted as printed. ZS (row 23), ZL (row 39), ZC (row 5) and ZW
(row 45) outrights carry the same values.

| Parameter | Value | Applies to ZM? | Source | Verbatim quote |
|---|---|---|---|---|
| Match algorithm (tag 1142) | K | Yes (ZM outright) | S1, S2 row 33 | Header "Algorithm*" = "K"; LEGEND sheet: "K: Configurable". Wiki S5 table: "Configurable \| K" |
| Implied eligible | Yes, all contracts | Yes | S1, S2 row 33 | Header "Implied Eligible*" = "Yes, Note 1"; LEGEND: "Note 1: All Contracts" |
| TOP order percent allocation | 1.0 (100%) | Yes | S1, S2 | Header "Top Order Percent Allocation" = "1.0" |
| TOP Min | 1 lot | Yes | S1, S2 | Header "Top Order Allocation Minimum" = "1.0" |
| TOP Max | 100 lots | Yes (outright). The ZM-ZM calendar spread row also shows 100 | S1, S2; S8 | Header "Top Order Allocation Maximum" = "100.0". S8: "TOP MAX in grain outrights is 100 contracts and 1000 contracts in grain spreads." |
| What counts against TOP Max | Only fills after the order rests; the initial aggressed quantity does not count. Effective 2023-10-01 | Yes ("all futures") | S7; S4 | S7: "Starting Sunday, October 1 (trade date Monday, October 2), CME Group will implement an enhancement to the TOP order allocation maximum quantity for all futures and options on futures products." / "With this change, CME Globex will no longer count initial aggressed quantity, and only count fills after the order rests in the market against the TOP MAX quantity. Currently, TOP Max includes initial aggressed quantity as well." S4: "Only lots filled after the order rests in the market count against the running total compared to TOP Max (this excludes initial aggressed quantity)." |
| FIFO percent | 40% | Yes | S1, S2; S8; S9 | Header "FIFO Percent Allocation" = "0.4". S8: "40% of the incoming aggressing order is allocated by timestamp." S9: "the CME Globex match algorithm for all other CBOT grain and oilseed futures contract outright trades and futures spreads, except for KC HRW Wheat, is 40/60 FIFO Pro-Rata." |
| Pro-rata percent | 60% | Yes | S1, S2; S8 | Header "Pro-rata Percent Allocation" = "0.6". S8: "60% of the incoming aggressing order is allocated based on the size of the resting orders." |
| Pro-rata minimum allocation (PR Min) | 1 lot | Yes | S1, S2; S3/S4 | Header "Pro-rata Minimum Allocation" = "1.0". S3/S4: "Any orders that would execute less quantity than the PR Min will not get any fills in the Pro Rata step." |
| Residual allocation | Leveling (outright). Calendar spread ZM-ZM: FIFO | Yes (Leveling on) | S1, S2; S8 | Header "Residual Allocation - Pro Rata Leveling/FIFO" = "Leveling" for ZM; "FIFO" for row 34 ZM-ZM SP. S8: "Leveling (outrights/inter-commodity spreads)". S3/S4: "Leveling can be optionally on or off for K." |
| LMM | None | Yes (no LMM in futures) | S3, S4 | "LMMs do not exist in futures products at CME Group." |
| Split rounding | FIFO share rounded up to a whole lot; the rest goes to Pro Rata | Yes | S3, S4 | "Lots designated to FIFO will be at least the percentage expressed for FIFO, with the remainder designated to be distributed via Pro Rata." / "In both cases, FIFO is rounded up to the whole lot just above the designated percentage for FIFO." |
| Pro-rata rounding | Round down (floor) | Yes | S3, S4, S5 | S3/S4: "Fractional lots received are rounded down prior to allocation." S5: "All fills are rounded down to the nearest integer (which may be zero)." |
| Pro-rata base | Displayed working quantity | Yes | S3, S4 | "{Displayed working quantity of an order} / {Total working lots present} * {Match quantity} ≥ PR Min = allocation" / "Display Quantity orders only participate in Pro Rata based on their working displayed quantity." |
| Leveling: who qualifies | Orders that took part in the Pro Rata step but got 0 lots from it | Yes | S3, S4 | "The order must have participated in the preceding Pro Rata step. This means: The order had working quantity at the time of the match. A calculation was made to determine what quantity it would receive via Pro Rata. The result of this calculation from 1b above caused the order to not receive any lots." |
| Leveling: lots per order | At most 1 | Yes | S3, S4, S5 | "Assuming an order qualifies, it will receive at most one lot during the Leveling step." |
| Leveling: order of distribution | Larger working quantity first, then earlier timestamp | Yes | S3, S4 | "Tiebreaks for Leveling are, in order: Working quantity of the order at the time of distribution. Earliest Timestamp." |
| Residual after Leveling | FIFO | Yes | S5; S8 | S5: "FIFO – Any remaining quantity is distributed to resting orders on a first in, first out basis (earlier timestamped orders receive fills before later timestamped orders)." S8: "Any residual quantity remaining is filled FIFO." |
| FIFO exception (sweep) | If the aggressor is at least as large as the displayed quantity at the price level, the whole level is filled FIFO, hidden quantity included | Yes (all algorithms) | S3, S4; S6 | S3/S4: "In the scenario where an aggressing order quantity is greater than or equal to the displayed quantity in an instrument at a given price level, for matching efficiency, CME Globex applies FIFO in lieu of the designated product algorithm. Quantity is allocated to resting orders according to best price and earliest timestamp." / "This exception applies during the actual match in an instrument, not during predetermination." |
| TOP eligibility | Betters the market (or sweeps the book and rests the remainder), displayed qty ≥ TOP Min | Yes | S3, S4 | "An order becomes TOP in one of the following ways: The order buys or sells out all resting quantity in the book and has a remainder left over that will rest on the book at a new bid or offer price. An order enters the market and improves the market (tightens the bid ask spread). The displayed quantity of the order must be greater than or equal to the TOP Min." |
| TOP: one per side | Yes | Yes | S5 | "Only a single buy order and a single sell order can have TOP priority at any given time. Orders having TOP priority match first regardless of size." |
| FIFO timestamp-priority loss | Quantity increase, price change, account change | Yes | S3, S4 | "A modified order loses its timestamp priority when any of these values are modified: Increase of working quantity of the order. Change of price. Change of account number." |

## (b) Step order as the sources state it

Matrix row for K (S3 and S4, "Algorithm Matrix"): "K | Configurable (Split FIFO/Pro Rata with LMM) | TOP | LMM |
Split | FIFO* | Pro Rata* | Leveling* | FIFO |" with the footnote "*FIFO and Pro Rata percentages are determined
by CMEG and calculated during Split. Leveling can be optionally on or off for K."

S5 (2023-12-10 capture): "Steps proceed in the same sequence regardless of which steps are configured on/off."

General step rules (S6, "Algorithmic Matching Process"): "Apply incoming match quantity to the first step of the
algorithm. Follow the rules of that step to distribute quantity to one or more orders. If any aggressing quantity
remains unmatched, proceed to the next step of the algorithm. Apply remaining unmatched quantity to this next step
of the algorithm." S4/S3 add: "Pro Rata is never the last step of an algorithm due to the required rounding; the
Pro Rata step will always be followed by either a FIFO step or Leveling and FIFO steps."

The sequence for one ZM outright match at one price level, as stated:

0. Pre-check, FIFO exception (S3/S4): if the aggressing quantity is at least the displayed quantity at the
   price level, skip the algorithm and fill FIFO. "Display Quantity orders are treated as their full remaining
   quantity (working displayed plus hidden)." "The FIFO exception can match through multiple price levels." The
   check repeats at each price level until "Aggressing quantity is less than resting quantity at a price level
   (in which case the designated algorithm is used), or The last price level on the aggressing order is
   reached." S6 states the same check as: "Q: Does the aggressing quantity fully satisfy all available quantity
   at the relevant price level(s)? If YES, there is no need to use an algorithm since all orders will be filled.
   Distribute quantity to all orders in TIME priority basis." and "This check only includes displayed quantity
   of resting orders."
1. TOP (S3/S4): "The TOP step entitles one order to all fills up to its Top MAX parameter provided the order
   maintains its TOP status at the time of each match." For ZM, TOP % = 100%, so the TOP order takes
   min(remaining aggressor, its displayed quantity, TOP Max minus lots already counted) [inferred from S1/S2
   values and the S4 TOP % definition: "Aggressing quantity is multiplied by this parameter, and the result
   (rounded down) is allocated to a TOP order."].
2. LMM: no LMMs in futures (S3/S4), so this step allocates nothing for ZM.
3. Split (S3/S4): "There are no lots distributed to orders during this step." The remaining quantity Q is split
   FIFO = Q x 40% rounded up to a whole lot, Pro Rata = the rest. Examples given: "A one lot will be Split to
   FIFO. A two lot will be Split one lot to FIFO, and one lot to Pro Rata. A three lot will be Split two lots to
   FIFO, and one lot to Pro Rata." "The results of this calculation instruct CME Globex to distribute lots via the
   next two steps in the K algo, those two steps being FIFO and Pro Rata in that order."
4. FIFO on the FIFO lots: "resting orders are matched in timestamp order only" (S3/S4).
5. Pro Rata on the Pro Rata lots: each order gets floor(displayed working qty / total working lots x PR lots);
   allocations below PR Min (1 for ZM) are zero (S3/S4 formula above).
6. Leveling: the lots left by rounding in step 5 go one lot each to orders that took part in step 5 but got
   0 lots, largest working quantity first, then earliest timestamp (S3/S4).
7. FIFO on anything still left (S5, S8).

TOP status rules for the simulator (S3/S4, with the version caveat in section (d)):
- Becoming TOP: see the parameter table. Also (S3/S4): "An order entered after a price level is established
  without a TOP order can be assigned TOP status if: Its displayed quantity is ≥ TOP Min for the product, and
  There has not been a TOP order at that price level since it was established."
- Losing TOP (text in both S3 and S4): "Cancelling an order does not convey TOP status to the next eligible
  order." "Likewise, an order loses TOP by being canceled or by having a new TOP order enter the market on the
  same side as it is. An order can also lose TOP status by having its TOP Max satisfied." "An order that loses
  TOP status as a result of TOP Max being equaled or exceeded still maintains its timestamp." "GTC orders do not
  maintain TOP over a weekend." "All refreshes of the Display Quantity order will not have TOP status."
- "It is possible for an aggressing order to match enough quantity on entry (match qty ≥ TOP Max) to not be
  granted TOP status." (S3 and S4; S4's examples show the post-2023-10-01 counting, under which the resting
  remainder becomes TOP.)

Implied orders (S6, captured 2023-10-02, same text in the current page):
- "In the steps below, Price and Quantity (PQ) sources can be either resting quantity in the aggressed
  instrument, or implied quantity from a combination of orders in other instruments."
- "Implied quantity will never match with implied quantity." "No algorithm is applied more than once per
  instrument."
- "Q: Does the required algorithm include a Pro Rata component? If YES, a predetermination step is required."
  K has a Pro Rata step, so this applies to ZM.
- Predetermination: "Determine all PQ sources potentially eligible for aggressing quantity. Include the
  aggressed instrument as a PQ source. Treat each source as one large order quantity. Run the aggressing
  quantity against all steps of the relevant algorithm. Do not go to steps beyond a Pro Rata step." /
  "Generally, the quantity to be allocated is rounded down. Any remainders are added to sources on a FIFO
  basis." / "There is an exception during Predetermination with ICS ratio spreads. Examples include Treasury
  ICS and Soybean Crush spreads." / "Now run the full algorithm (all steps, in order) once per instrument using
  the values calculated in step 5 through 8 as aggressing orders for the relative instruments."
- On visibility: "these implieds will not be visible via market data" is said of ratio-spread implieds
  (TUF example) in S6. The brief's general statement that implied orders "are not disseminated" was not found
  in these pages as a general rule [unverified as a general rule].
- ZM's product rows (S1/S2): ZM-ZM calendar spreads (SP) and ZM butterflies (BF) are implied-eligible
  ("Yes, Note 1"), condors (CF) are not; the soybean crush (Globex symbol SOM, strategy type "SI: Soy Crush")
  is implied-eligible.
- How implied sources share the FIFO step of K in predetermination is not stated (see (d)).

## (c) Worked examples, transcribed

No CME worked example runs the full K sequence (TOP, Split, FIFO, Pro Rata, Leveling, FIFO) end to end. The
examples below are per-step examples from the Steps page; the text is the same in S3 (2023-06-20) and S4 unless
noted. In every example: "Orders in the below table are at the same price on the buy side. Earliest timestamp
is Order 1, then order 2, etc. The sell aggressor is at the same price as the buy orders."

E1. FIFO Example 1 (S3, S4). Sell aggressor 50 lots.

| Order | Working qty before step | Remaining after step |
|---|---|---|
| 1 | 5 | 0 |
| 2 | 9 | 0 |
| 3 | 57 | 21 |
| 4 | 4 | 4 |
| 5 | 28 | 28 |
| 6 | 300 | 300 |

Text: "The aggressing quantity is allocated to orders 1 + 2 (filling them). Order 3 receives a partial fill and
will have 21 lots remaining after the match."

E2. FIFO Example 2, display quantity (S4 table; the S3 table has the same numbers but its cells are garbled).
Sell aggressor 50 lots. "Order 2 is a Display Quantity order with 90 additional unfilled lots displaying 10 at a
time."

| Order | Working qty before | Remaining after | Priority after match | Qty after match |
|---|---|---|---|---|
| 1 | 5 | 0 | n/a | n/a |
| 2 | 10 | 0 | n/a | n/a (90 hidden quantity) |
| 3 | 57 | 22 | 1 | 22 |
| 4 | 4 | 4 | 2 | 4 |
| 5 | 28 | 28 | 3 | 28 |
| 6 | 300 | 300 | 4 | 300 |
| 2 (refreshed) | 10 | 10 | 5 | 10 (80 hidden quantity) |

Text: "After the match, order 2 would be refreshed to its display quantity of 10 at the lowest priority." (The
text also says order 3 has "21 lots remaining", which contradicts the table's 22; see (d).)

E3. Pro Rata Example (S3, S4). Sell aggressor 50 lots. "The Pro Rata Minimum for this contract is 2." Total 403.

| Order | Working qty before | Formula | Result | Rounded down | Allocated | Remaining after |
|---|---|---|---|---|---|---|
| 1 | 5 | 5/403*50 | 0.62 | 0 | 0 | 5 |
| 2 | 9 | 9/403*50 | 1.11 | 1 | 0 | 9 |
| 3 | 57 | 57/403*50 | 7.07 | 7 | 7 | 50 |
| 4 | 4 | 4/403*50 | 0.49 | 0 | 0 | 4 |
| 5 | 28 | 28/403*50 | 3.47 | 3 | 3 | 25 |
| 6 | 300 | 300/403*50 | 37.22 | 37 | 37 | 263 |

Order 2's rounded 1 is below PR Min 2, so it gets 0. (Under ZM's PR Min of 1, order 2 would get 1 [inferred].)

E4. Leveling Example (S3, S4), continuing E3 (PR Min 2). "Of the 50 lots originally designated for Pro Rata,
the PR step only distributed 47 (this is the total number of lots from the "Allocated Lots" column, 7+3+37).
This leaves 3 lots left to distribute." "The order of distribution for these would be order 2, then order 1,
and then order 4, due to their working quantity sizes at the time. As a result, if there had only been two lots
to allocate, order 4 would not have received any allocation (as the smallest order)."

| Order | Allocated from PR | Remaining after PR | Lots via Leveling | Remaining after Leveling |
|---|---|---|---|---|
| 1 | 0 | 5 | 1 | 4 |
| 2 | 0 | 9 | 1 | 8 |
| 3 | 7 | 50 | | 50 |
| 4 | 0 | 4 | 1 | 3 |
| 5 | 3 | 25 | | 25 |
| 6 | 37 | 263 | | 236 (as printed; 263 is consistent, see (d)) |

E5. Split Example (S3, S4). "In all cases 49 lots need to be designated for FIFO and Pro Rata by the Split step."

| Scenario | Split % | Lots to FIFO | Lots to PR |
|---|---|---|---|
| 1 | 100/0 | 49 | 0 |
| 2 | 20/80 | 10 | 39 |
| 3 | 40/60 | 20 | 29 |
| 4 | 0/100 | 0 | 49 |

Plus the three cases in the text at 40/60: 1 lot gives 1 FIFO / 0 PR; 2 lots give 1/1; 3 lots give 2/1.

E6. TOP Max Example 1 (S4 only; added after the 2023-10-01 change). "Top Min =3", "Top Max =40". Book: bid 45 @
100. "Aggressing Offer 50@100 matched resting bid at limit price 100 – Match 45@100, Aggressor Offer will be get
TOP status for the remaining 5 contracts. TOP Max quantity should be counted only after the order has rested in
the market". Result: offer 5 @ 100 (TOP Order).

E7. TOP Max Example 2 (S4 only). Same parameters. Book: bid 45 @ 100; offer 25 @ 102 (TOP order). "Aggressing
Offer 200@100 matched resting bid at limit price 100 – Match 45@100, Aggressor Offer will get TOP status for the
first 40 lot fills against the remaining 155@100. Resting Offer (25@102) will lose TOP status." Result: offer
155 @ 100 (TOP Order); offer 25 @ 102 (no TOP).

E8. LMM Examples 1 and 2 (S3, S4). They do not apply to ZM (no LMMs in futures) and are listed for completeness.
Ex 1, aggressor 50: "Order 2 is placed by LMM A whose percentage is 5%. Order 3 is placed by LMM B whose percentage
is 6%." Rows: 2A 9, 50*.05 = 2.5, gets 2, 7 left; 3B 57, 50*.06 = 3, gets 3, 54 left; orders 1, 4, 5, 6 unchanged
(5, 4, 28, 300). Ex 2, "The sell aggressor is a 1 lot.": 2A .05 rounds to 1 and gets 1 (8 left); 3B .06 rounds to 1
and gets 0 (57 left); "Since there is a tie, the allocated lot goes to the earlier timestamped order."

E9. CFTC AAC 2019 slide (S8), simplified Pro Rata illustration (pure pro rata, no Split): offer 60 total, six
orders A to F of 10 each (16.7% each). "6 Lot Aggressing Order": each gets 1. "5 Lot Aggressing Order": each gets
0, "resulting in no Pro-Rata allocation and this 5 lot moves to either Leveling or FIFO." The same deck's
"Realized Allocations" slide gives "~7% TOP", "~56% FIFO", "~23% Pro-Rata", "~14% Leveling". The text layer does
not name the product or the period.

E10. Complex Match Example (S10). This is algorithm A (SOFR, PR Min 2; GE Eurodollar in the 2020 copy), not K,
but it is CME's only worked example of predetermination with implied sources. The aggressor is 501 into SR1U3.
The book has 2000 bid: 1000 resting outright and 1000 implied from 4 sources (200/300/400/100). There are TOP
orders in SR1U3, SR1H4 and SR1U3-SR1N4. Predetermination: the TOP gets 100 to source #1 (401 left); then Pro
Rata over 1900: source #1 900/1900*401 = 189, #2 42, #3 63, #4 84, #5 21 (total 399); "There are two lots left
over due to rounding. These are distributed to the aggressed instrument." Final sources: #1 291, #2 42, #3 63,
#4 84, #5 21, and each two-instrument source gives like quantities to both instruments. Per-instrument run,
SR1U3 291: "TOP order gets 100 and is filled. 191 left to match." Orders 2/3/4 (200/300/400 of 900) get 42, 63,
84 = 189; "2 lots left for next step which is FIFO. This goes to Order 2." Final book: order 2 156, order 3 237,
order 4 316. The per-instrument tables for the other eight instruments are in
wiki_complex_match_example_current.txt. Algorithm A has no Split or Leveling, so these numbers are not K
allocations.

## (d) Not found / conflicting

Not found:
1. A CME worked example of the full K sequence (TOP, Split 40/60, FIFO, Pro Rata, Leveling, FIFO) on one book.
   Only per-step examples exist (section c).
2. Which quantities the Pro Rata step's denominator uses inside K: the working quantities after the FIFO step
   has filled orders, or before it. S3/S4 say "Total working lots present" and "at the time of a match", and
   the example tables say "Working Quantity Before step". These suggest post-FIFO quantities [inferred, not
   stated].
3. Whether the TOP order, after taking its TOP fill, also takes part in the FIFO and Pro Rata steps with its
   remaining quantity in the same match. S3/S4 say only that an order that loses TOP through TOP Max "still
   maintains its timestamp". S10 (algorithm A) shows the TOP order being filled completely. [not stated for K]
4. Split rounding when 40% of Q is a whole number (for example Q = 5 gives exactly 2.0). The text says "at least
   the percentage" and "rounded up to the whole lot just above". Reading this as ceil(0.4 x Q) gives 2 [inferred].
   The examples given (Q = 1, 2, 3, 49) never land on a whole number.
5. How predetermination handles K's FIFO step across implied sources. S6 describes TOP and Pro Rata at the
   source level ("Do not go to steps beyond a Pro Rata step"), but not how the FIFO lots from Split are
   given to sources, or whether a source's timestamp is defined. Leveling at source level is not covered
   either, since predetermination stops at Pro Rata and "Any remainders are added to sources on a FIFO basis".
6. A general statement that implied quantity is not disseminated. Found only for ratio-spread implieds (S6).
   Implied participation in the opening (pre-open / IOP) match for K: S5 says implied orders are not
   considered at the open only within its SOFR Allocation section ("Implied orders are not taken into
   consideration, because these orders are only active during the continuous trading session."). It also says
   there, "Orders placed during the "pre-opening" or at the Indicative Opening Price will be matched on a price
   and time priority basis". Neither is stated for K.
7. The date of the change to the TOP modification rules. S3 (2023-06-20 capture, last modified 2023-01-26)
   says: "An order loses TOP status by being modified in any of the following ways: Increasing the working
   quantity. Changing the price. Changing the account number." and "The TOP check is made on order entry
   only." S4 (current) says: "Any increase in the working quantity. Modifying the price to a level that does
   not improve the market. Any change to the account number. A decrease in the working quantity does not cause
   the order to lose it's TOP status." and "The TOP check is made on order entry or upon any modification that
   affects eligibility." Which text held in 2023-11 to 2024-02 is unknown: there is no capture in between,
   and two searches found no notice. This matters only for TOP orders that change price.
8. Independent confirmation that the TOP Max change went live on 2023-10-01. S7 is the pre-announcement ("This
   change is currently available in the New Release for customer testing."). The current wiki (S4) shows the
   new rule, but no go-live notice was fetched. The wiki page the notice linked
   (confluence/display/EPICSANDBOX/TOP+Order+Allocation) has no Wayback capture.
9. Peng (J. Futures Markets 2024): no openly reachable full text found in one search; not pursued.
10. The date grain/oilseed futures first moved to K. S9 (2014) says they were already "40/60 FIFO Pro-Rata" then.
    This does not affect the window.

Conflicting or erroneous in the sources:
1. TOP Max for grain spreads. S8 (2019) says "1000 contracts in grain spreads". In S1/S2 the ZS-ZS spread row
   shows 1000, but ZM-ZM and ZL-ZL show 100. Outrights agree at 100.
2. Leveling eligibility wording. S8 says "Any order that did not participate in the Pro-Rata pass is eligible".
   S3/S4 say the order "must have participated in the preceding Pro Rata step" and received 0 lots from it. The
   wiki is more detailed and has a worked example (E4); S8 reads as a loose paraphrase.
3. FIFO-exception threshold. S3/S4 say "greater than or equal to the displayed quantity". The S6 summary
   line says "When the aggressing order quantity is greater than the entire resting quantity at a price level,
   a simplified algorithm is used", while its predetermination check says "fully satisfy all available
   quantity". Equality is covered explicitly only by S3/S4.
4. Typo in E4: order 6 has no Leveling lot, yet its "Remaining Quantity after Leveling step" is printed as 236.
   It should be 263. The same typo appears in all copies (2021, 2023, current).
5. Typo in E2: the text says order 3 "will have 21 lots remaining" (copied from E1), but the table shows 22,
   which matches the arithmetic 5 + 10 + 35 = 50.
6. E10 arithmetic: for SR1N4 the page sums "4+2+1+13=20" while saying order 3's 1 "becomes 0 due to the Pro Rata
   Min", which would make the total 19. It is algorithm A, so this does not affect K.
7. TOP Max counting changed on 2023-10-01 (S7). S3, the latest pre-window capture of the Steps page, still has
   the old rule: "All lots filled on that order, regardless of step (this includes initial aggressed quantity as
   well) count against the running total compared to TOP Max." S4's rule applies to the window.
8. S3 says "TOP Percentage (TOP %) – This parameter is a limiter to quantity being matched against a TOP order."
   The 2021/2022 copies (S11) added "This parameter is not currently used by CME Globex." For ZM the sheet value
   is 1.0, so either reading gives the same allocation.
