# R18 Queue and fill models for passive limit orders (Stage E.25)

Reader: R18-QueueFill-OpusHigh. Started 2026-10-18 01:56 PDT; cut by the usage limit about 02:00 PDT; resumed 06:12 PDT under a 06:33 PDT hard deadline. Written 06:14-06:17 PDT. This is a PARTIAL return: see section 10.

## 1. Answer (at most 250 words)

Verified in this session: one primary source with fill-probability and post-fill markout numbers (Albers et al. 2025, arXiv:2502.18625, a live maker-order experiment on the Binance Bitcoin perpetual, not CME). Its findings point one way: fill likelihood and post-fill return are negatively correlated; back-of-queue fills mark out at an average of -0.775 bp one second after the fill and front-of-queue fills at -0.058 bp (both before rebate); the naive join-the-touch maker strategy "is in fact highly unprofitable" even with a maker rebate. It also reports that >95% of submitted maker orders are cancelled, which biases fill probabilities estimated from other traders' orders (Lokin and Yu: under 2% vs 50% for the same book state). A second source is on CME futures (Lalor and Swishchuk, arXiv:2409.12721v3, 2026): a 1-lot static posting strategy in the Trading Technologies simulator (queue position assigned, filled only once real volume trades through it) had the first post-fill mark-to-market move go against the order on 767 of 941 ES fills (81.5%), 1269 of 1929 NQ (65.8%), 518 of 625 CL (82.9%) and 199 of 224 ZN (88.8%), one day each in April 2024; ignoring adverse fills and realistic fill probabilities 'substantially inflates trading performance'. No published markout size in ticks for CME futures was verified. The papers named in the brief (Moallemi-Yuan, Cont-Stoikov-Talreja, Cont-de Larrard, Huang-Lehalle-Rosenbaum, Lo-MacKinlay-Zhang) were NOT fetched.
For the lead's passive-saving estimate the program's own sourced facts weigh most: TopstepX fills a limit only on trade-through (DECISIONS C6), and D.1f's trade-through fill model on C-H4 gave UCB95 -177.18 net ticks per micro per day. A worked implication (my arithmetic, not a published number) is in section 5. Prop rules: R9_prop_rules.md already covers HFT, latency-abuse, sim-fill and hold-time clauses for 15+ firms; R18 adds no new firm quote (terms of Tradeify, Bulenox, TPT, ETF, Trading Pit, Earn2Trade forbid automated fetches; Apex and Lucid were unread). Candidates: zero (the passive route is closed by C6; nothing here reopens it).

## 2. Candidate hypotheses

None. Reason: the evidence found says passive fills at the touch carry adverse selection that eats the half-spread, and the venue of record fills only on trade-through, which by construction selects the adverse fills (section 5). Group A and Group B maker-native designs belong to R17 and the lead.

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| Fill likelihood and post-fill return are negatively correlated for maker orders | qualitative | "We document a fundamental trade-off: a negative correlation between maker fill likelihood and post-fill returns." | Abstract, p.1 | Albers, Cucuringu, Howison, Shestopaloff (2025), "The Market Maker's Dilemma", arXiv:2502.18625, https://arxiv.org/abs/2502.18625 | working-paper | pages/R18/arxiv_2502.18625.pdf |
| Naive join-the-touch market making is unprofitable even with rebate | qualitative | "The naive strategy, which is prima facie appealing because it receives the rebate and benefits from the spread, is in fact highly unprofitable." | Sec. 6 (text line ~1012) | same | working-paper | same |
| Post-fill markout (1 s after fill, ex rebate) by queue position | front of queue -0.058 bp; back of queue -0.775 bp | "the average value of -0.058 bp. Conversely, fills from maker orders at the back of the queue predominantly result in negative outcomes, with the majority of the distribution's mass being at negative values, and an average return of -0.775 bp" | Sec. 5, p.16-17 (Table 1 has the full stats) | same | working-paper | same |
| Markout definition | 1 s horizon vs mid | "in basis points by comparing the limit price of the filled order with the midprice one second after the fill occurs—note that these returns do not include the maker rebate" | p.16 | same | working-paper | same |
| Adverse-fill share for passive 1-lot quotes on CME futures (TT simulator, queue-position fills) | ES 767/941 (81.5%); NQ 1269/1929 (65.8%); CL 518/625 (82.9%); ZN 199/224 (88.8%); one day each, 2024-04-23..25, 08:30-16:00 EST | "2024/04/24 ES Jun24 941 767 174 / 2024/04/25 NQ Jun24 1929 1269 660 / 2024/04/23 CL Jun24 625 518 107 / 2024/04/24 ZN Jun24 224 199 25"; definition: "when an LO is filled on the bid (ask) and the next new bid (ask) price is lower (higher), we consider this fill to be adverse" | Table 2, p.6-7 | Lalor and Swishchuk (2024, v3 2026-06-02), "Market Simulation under Adverse Selection", arXiv:2409.12721, https://arxiv.org/abs/2409.12721 | working-paper | pages/R18/arxiv_2409.12721.pdf |
| TT simulator fill model is queue position plus trade-through volume | rule | "TT models LO executions by assigning orders an imaginary queue position in the LOB, which is filled once sufficient real market volume trades through that position" | Sec. 2, p.6 | same | working-paper | same |
| Second sample (330 simulation runs, 2025-04-24): adverse fills dominate | ask 3950 adverse vs 825 non-adverse; bid 3943 vs 813 (about 83%) | "AFA 3950 / NFA 825 / AFB 3943 / NFB 813" ; "Number of trade order fills that were adverse and non-adverse over 330 simulations throughout the trading on April 24th, 2025." | Table 4, p.14 | same | working-paper | same |
| Naive limit backtests overstate | qualitative | "excluding adverse fills and realistic non-adverse fill probabilities substantially inflates trading performance" ; "Adverse fills are unavoidable in LO posting strategies, especially in short-term trading environments." | Sec. 6 Conclusion | same | working-paper | same |
| Fill probability depends on near and far queue sizes | 30% to >90% | "submitted when the near-side queue is large and the opposite-side queue is small have a low fill probability, as low as 30%. Conversely, the fill probability exceeds 90% when the near-side queue is very small and the opposite-side queue is very large." | p.14 | same | working-paper | same |
| Highest fill probability coincides with adverse imbalance | qualitative | "The highest fill probabilities occur when there is a large opposite-side queue and a nearly empty near-side queue, implying an adverse order book imbalance" | p.14 | same | working-paper | same |
| Fill probabilities estimated from others' orders are biased by cancellations | >95% cancelled | "the importance of this can hardly be overstated given that >95% of submitted maker orders are cancelled; see Gould et al. [2010] and Brogaard et al. [2014]" | Sec. 1.1, p.3 | same | working-paper | same |
| Historical vs experimental fill probability for the same book state | <2% vs 50% | "Lokin and Yu [2024] reports a fill probability of less than 2% for orders placed by other market participants when the spread is one tick wide and bid and ask queues are balanced, compared to the 50% fill probability we find in the same situation. This is largely a cancellation" | Sec. 1.1, p.3 | same (citing Lokin and Yu 2024) | working-paper [secondary-only for Lokin-Yu] | same |
| Tick size of the experiment's market (relative tick far smaller than MNQ/MES) | 0.1 USD = ~0.03 bp | "The tick size is 0.1 USD, or approximately 0.03 bp at the time of the experiment" | p.10 | same | working-paper | same |
| Deep-learning fill-time model exists (Nasdaq stocks); no futures numbers extracted | n/a | "This paper proposes a deep learning method to estimate the filltimes of limit orders posted in different levels" | Abstract | Arroyo, Cartea, Moreno-Pino, Zohren (2023), arXiv:2306.05479 | working-paper | pages/R18/arxiv_2306.05479.pdf |
| TopstepX fills a limit only on trade-through | rule | "the market has to trade through your price - not just touch it" | DECISIONS.md C6 (help.topstep.com/en/articles/8765442, fetched 2026-09-23) | Topstep help centre via reports/stage_e0_topstep_facts.md | firm-page | (program file) |
| D.1f trade-through fill model on C-H4 resting limits | UCB95 -177.18 net ticks per micro per day (mean -186.63) | "That is the fill model D.1f already applied to C-H4: UCB95 -177.18 net ticks per micro per day (mean -186.63)" | docs/DECISIONS.md line 39-40 | program record | program-internal | (program file) |
| Latency erodes liquidity-imbalance value; CME latency 100 us-1 ms | see R3 | R3 rows 33 and 96 | R3_orderflow.md | Lehalle-Mounjid 2017; Dixon 2018 (R3's fetches) | working-paper | pages/R3/ |

## 4. Negative evidence

- CME futures (ES, NQ, CL, ZN): 65.8% to 88.8% of passive 1-lot fills were adverse at the next price change (Lalor-Swishchuk Table 2); simulation ignoring this "substantially inflates trading performance" (Sec. 6). Caveat: one day per contract, simulator fills, author-chosen 4/16/1-tick quote spacing, no tick markout size published in the parts read.

- The naive maker strategy loses money even with a rebate (quote above, arXiv:2502.18625 Sec. 6).
- Back-of-queue fills mark out at -0.775 bp after one second (quote above). A retail API trader with no VPS joins at the back of the queue by default.
- Fill-probability estimates from historical order data are biased by cancellations (>95% of maker orders cancelled), so any published fill rate measured on other traders' orders cannot be used as the program's own fill rate.
- Program record: D.1f trade-through fills on C-H4 resting limits gave UCB95 -177.18 net ticks per micro per day (DECISIONS C6).

## 5. Data and cost; honest limit-order backtest method

Worked implication for the lead (my arithmetic from the rule, not a published number; the lead decides whether to use it): on a one-tick-wide MES or MNQ book, a resting buy at the bid saves +0.5 tick against the mid at entry versus a market order. Under a trade-through-only rule the order fills only when a trade prints at least one tick below the limit, so at the fill the market has already traded through the price: the touch fill (the share that a touch-fill backtest counts, where the price stops at the limit and turns) never fills, and the fills that remain are the ones where the price kept going. On those fills the half-spread saved is offset immediately by about one tick of adverse move. The realistic passive saving per side under trade-through is therefore at or below zero before any markout beyond the trade-through tick, and the missed fills (price touches and turns) are lost opportunities that a touch backtest books as wins. This matches the direction of D.1f's -177 ticks per micro per day.
Honest-backtest elements the literature and program use: (a) trade-through rather than touch fills (C6); (b) queue simulation from MBO (D.1g plan, closed); (c) latency injection (R3: 100 us-1 ms CME latency in Dixon 2018 versus retail tens to hundreds of ms); (d) markout accounting at fixed horizons (arXiv:2502.18625 uses 1 s mid markout); (e) missed-fill opportunity cost (a missed entry is replaced by a market order or a skipped trade, both booked); (f) do not estimate fill probability from other traders' orders without a cancellation correction (>95% cancelled).
Data: queue-position models need MBO (Databento `mbo`); fill-at-touch versus trade-through tests need trades plus MBP-1 (`trades`, `tbbo` or `mbp-1`); depth-based fill probability needs MBP-10. Owned: no (brief section 4: five MNQ mbp-1 days and two MES mbp-10 days only). Prices: cite R3 (R3_orderflow.md lines 72-73: Databento Standard "$199 per month" with "1 month of L2 and L3 history"; program-internal D.1e quotes MES mbo RTH $0.7836 per day, mbp-10 RTH $1.2088 per day; quotes, not published prices). R18 fetched no Databento page.

## 6. Prop compatibility

From R9_prop_rules.md (not refetched; quote IDs are R9's): FundedNext terms 2.2.7 "Entering and exiting trades within 5 ticks or without reasonable holding (15-20 seconds) repeatedly is against trading guidelines" (E13) and HC 14298560 bans "latency abuse or order flooding" (E12); MyFundedFutures "High-frequency Trading is not allowed ... so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment" (E29); DayTraders HFT defined as trading "at extremely high speeds, especially in milliseconds" (E17); Alpha Futures >100 trades/day (E25), TradeDay >200 trades/day, AquaFutures >=100 trades/day [secondary-only]; Topstep "no HFT", no VPS, no scalping that exploits SIM fills (E.19). Topstep fills limits on trade-through only (C6). Tradeify, Bulenox, Apex, Lucid, Phidias, Take Profit Trader: HFT banned per R9's table; several only [secondary-only]. No firm page read here states an order-to-trade, cancel-ratio or message-rate number. CME messaging-efficiency rules: not found through a permitted source in the time available.

## 7. Overlap with tested mechanisms

D.1g C6 passive-execution queue model (closed, not run); C-H4 reversal with passive fills (D.1f, trade-through, failed). Nothing here differs from them in a way that reopens them.

## 8. Re-dig: not a re-dig reader. Verdict check reported: C6 closure SUPPORTED (adverse selection of maker fills; naive maker strategy unprofitable; trade-through selects adverse fills).

## 9. Fetch log

| url | UTC | sha256 (16) | saved path | status | tool |
|---|---|---|---|---|---|
| https://arxiv.org/pdf/2502.18625 | 2026-10-18T13:13:02Z | 0d632558381334e1 | pages/R18/arxiv_2502.18625.pdf (+ .txt) | ok | curl |
| https://arxiv.org/pdf/2409.12721 | 2026-10-18T13:15:28Z | 09d9d43308f08e79 | pages/R18/arxiv_2409.12721.pdf (+ .txt) | ok | curl |
| https://export.arxiv.org/api/query (3 searches: limit order/fill/futures; queue/fill/futures; E-mini/queue) | 2026-10-18T13:15:04Z..13:15:23Z | n/a | scratch R18/q1-q3.xml (q1 empty over http) | ok | curl |
| https://arxiv.org/pdf/2306.05479 | 2026-10-18T13:13:18Z | e0e41b8659db7136 | pages/R18/arxiv_2306.05479.pdf (+ .txt) | ok | curl |

Terms: arxiv.org per terms_log.md (allowed; crawl-delay 15 respected). Budget notices: none seen (0 WebSearch calls used). OpenAlex not called (exhausted until 17:00 PDT per lead); Firecrawl not used (no credits per lead); Playwright not used.

## 10. Unfinished and unverified

- Lalor-Swishchuk: Table 1 (trade sizes) and Sections 3-5 (SOC strategy PnL under benchmark vs improved fills, Table 5) not read; the PnL gap between naive and prudent simulation is therefore not quoted.
- Not fetched: Moallemi and Yuan (queue value), Cont-Stoikov-Talreja (2010), Cont-de Larrard (2013), Huang-Lehalle-Rosenbaum (2015 queue-reactive), Lo-MacKinlay-Zhang (2002), Lokin-Yu (2024) primary text, CME iceberg and queue-priority studies, any E-mini or Treasury futures markout study. No published CME fill rate or markout in ticks is verified here: the passive-saving estimate for MNQ/MES rests on the program's C6 rule and D.1f result plus the section 5 arithmetic.
- Arroyo et al. (2023) downloaded but no numbers extracted.
- Databento schema prices not refetched (cite R3). CME messaging-efficiency rules not found.
- No new prop-firm page fetched; R9 covers the domain; order-to-trade and cancel-ratio numbers not found anywhere.
- The bp markouts in arXiv:2502.18625 are from a market with a 0.03 bp tick; they do not convert to MES/MNQ ticks without a volatility and tick-size adjustment, so no tick conversion is given.
