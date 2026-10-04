# Brief: BrokerVenues-OpusHigh (Stage E.13 Task 1, part 3: a personal futures account for a Canadian resident)

Read reports/stage_e13_briefs/research_rules.md first and follow it. Your pages folder:
reports/stage_e13_briefs/pages/BrokerVenues/.

## Objective (one)
Establish which brokers let a resident of British Columbia, Canada, open a personal account that trades US
(CME Group) futures, including micro contracts, through an API that an automated system can use, holding
positions for days; and record each one's costs, margins and minimums from the broker's own pages.

## Brokers
At least Interactive Brokers Canada (IBKR Canada Inc.). Then check, and include those that accept Canadian
(BC) residents for US futures: AMP Futures, NinjaTrader Brokerage, Tradovate, Optimus Futures, Ironbeam,
EdgeClear, TradeStation, Questrade, Wealthsimple, the Canadian bank-owned brokers (TD Direct Investing,
RBC Direct Investing, BMO InvestorLine, CIBC Investor's Edge, National Bank Direct Brokerage), Qtrade, and any
other you find. A broker that does not accept BC residents for futures gets one row saying so, with the quote.
Also record, from a sourced page, any Canadian regulatory point that decides eligibility (CIRO membership,
provincial derivatives rules, the need for a Canadian-registered dealer).

## Per broker (every cell sourced)
1. Accepts BC residents for US futures? (quote)
2. Account minimum (to open, and for futures/margin permission), currency (CAD/USD), account types.
3. API for automated trading: name (e.g. TWS API, Client Portal Web API, FIX), whether it allows order entry
   for futures, any extra fee, any automation restriction in the terms. Holding positions overnight and for
   days: allowed (normally yes for a retail margin account; source it).
4. Micro futures available. Check each of these (listed at the broker, yes/no, with the source): MES, MNQ, M2K,
   MYM, MCL, MGC, SIL, MHG, MBT, MET, micro FX (M6E, M6A, M6B, MCD, MJY, MSF, if listed), micro treasury yield
   futures (2YY, 5YY, 10Y, 30Y), micro Henry Hub natural gas (if listed; give its symbol), micro grains (if
   listed), and full-size NG, ZT, ZF, ZN for reference.
5. Commissions per contract per side for micros and for the full-size contracts above (broker commission,
   and the exchange, clearing and regulatory fees where the broker publishes them), and any market-data
   subscription needed for CME real-time data, with its monthly cost.
6. Initial and maintenance margin per contract for each micro in item 4 and for NG, ZN, ZF, ZT, from the
   BROKER's margin page (not CME's site, which refuses this machine and forbids automated access): date the
   page shows, intraday vs overnight margin if the broker distinguishes them (overnight is what a multi-day
   system pays).
7. Inactivity or platform fees, and any minimum-activity rule.

## Output
reports/stage_e13_venues_part3_brokers.md:
1. A broker summary table: | Broker | BC residents | Minimum | API (futures orders) | Multi-day holds | Micros listed | Commission (micro, per side, all-in) | Market data cost | Notes | with source keys [B-01]... in every cell (UNSOURCED where needed).
2. A margin table: | Contract | Broker | Initial (overnight) | Maintenance (overnight) | Intraday (if any) | Page date | Source key |, IBKR at least; a second broker where its page is public.
3. A classification line per broker: PERMITTED (multi-day automated via API, unambiguous) / HUMAN-IN-THE-LOOP
   ONLY / NOT PERMITTED / UNCLEAR, with the deciding source keys.
4. A source list: key | URL | fetched | page date | page type | verbatim quote.
5. Gaps and failures.

## Stopping rule
Done when IBKR Canada has every field filled (or UNSOURCED with the reason) and every other broker has at
least fields 1 and 3, plus fields 2, 4, 5 and 6 where it accepts BC residents. Budget: at most 100 WebSearch
calls. Never log in, open an account, or request a quote from a broker.

## Boundaries
Brokers only. Prop firms belong to PropVenues1/2; volatilities, sizing and trend evidence to TrendCarry.
