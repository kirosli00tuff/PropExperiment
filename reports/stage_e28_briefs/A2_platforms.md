# A2_platforms: Layer 2 platform facts (Stage E.28 Part A), as of 2026-10-21

Worker A2_platforms (opus high). Facts only for criteria F (simulated fill rule for resting limits) and P (API,
OCO/bracket, VPS, rate limit) of reports/stage_e28_ranking_spec.md section 3. No scores are given here; the lead
scores. Every quoted line is from a page saved under reports/stage_e28_briefs/pages/A2_platforms/ (log.tsv there
has URL, UTC and PDT fetch time, method, sha256). Forum posts are pointers only and are labelled so. Machine-readable
copy: A2_platforms.json (fields value, unit, source_file, quote, note).

Status legend: [doc] = vendor documentation; [firm] = firm help page; [pointer] = forum or third-party, not
evidence; [unverified] = not confirmed from full text.

## 1. TopstepX / ProjectX (Topstep; ProjectX Trading LLC is the platform owner)

| Item | Fact | Source file | Verbatim quote |
|---|---|---|---|
| Sim fill rule for resting limits | Trade-through: Topstep's help article on order types says a limit fills only when the market trades through the price, not on a touch, and its FAQ answer to "Why wasn't my order filled?" repeats it. The article does not say "simulated", but it is Topstep's help page for TopstepX accounts, which are simulated except Live. No ProjectX document on the sim matching engine (queue or volume model) was found. | ts_8765442_fills.html.txt L56, L147 | "Price execution over speed. Trade-off: the market has to trade through your price — not just touch it. You might not get filled. Partial fills happen." ; "Limit orders especially — if the market doesn't trade through your price, you don't get filled." |
| Native API | Yes: ProjectX Gateway API (REST + realtime hubs) | px_order_place.html.txt | (endpoint page "order-place"; see order types) |
| Order types on the API | Limit, Market, Stop, TrailingStop, JoinBid, JoinAsk | px_order_place.html.txt L33-39 | "type integer The order type: 1 = Limit 2 = Market 4 = Stop 5 = TrailingStop 6 = JoinBid 7 = JoinAsk" |
| Bracket / OCO on the API | Native stop-loss and take-profit brackets attached to an order, only when the account is in "Auto OCO Brackets" mode; default "Position Brackets" mode rejects bracket objects. No standalone OCO endpoint seen. | px_order_place.html.txt L72-75 | "Auto OCO Brackets . Brackets attach to each order. stopLossBracket and takeProfitBracket are accepted on this endpoint." |
| API rate limit | 200 requests per 60 s for all endpoints except bar history (50 per 30 s); HTTP 429 on excess. 200/60 s = 3.3 requests per second on average. | px_rate_limits.html.txt L23-26 | "POST /api/History/retrieveBars 50 requests / 30 seconds" ; "All other Endpoints 200 requests / 60 seconds" ; "the API will respond with an HTTP 429 Too Many Requests error" |
| Market data behind the sim | TopstepX's own CME feed (May 2025 Wayback copy of the TopstepX FAQ; the line is gone from today's page). Today Topstep says CME requires payment for data on simulated accounts and that it covers Level 1. Search snippets (not fetched: the page now returns 404) say ProjectX is a licensed CME redistributor through Sim2Funded Solutions, LLC with primary market-data servers in Northern Virginia [unverified, snippet only]. If the servers are in Virginia, a Chicago VPS would not sit next to the TopstepX order path; this is not confirmed. | ts_8524249_topstepx_faqs_wb20250515.html.txt L87; ts_8284120_marketdata.html.txt | "Our own dedicated data feed, direct from the Chicago Mercantile Exchange (CME)." ; "The CME requires payment for all market data on simulated accounts. Topstep covers Level 1 for all 4 exchanges at no cost to you." |


## 2. Tradovate (used by MFFU, Tradeify, Lucid; firm workers own which firm uses what)

| Item | Fact | Source file | Verbatim quote |
|---|---|---|---|
| Sim fill rule for resting limits | **Undocumented.** No Tradovate document on its simulation matching logic was found (searches on Tradovate support, partner docs and community). A Tradovate staff account (BWeis, staff flag true) said only that the sim tries to mirror exchange matching. Users in the same thread report sim limits fill only when price breaks through. [pointer: forum] | tv_community_2279.json (post 11 by staff; posts 2 and 7 by users) | staff: "Live orders get filled by the exchange's matching engine. While Tradovate tries to mirror the filling algos as close as we can, reproducing the exchange's matching algorithms with 100% accuracy in a simulation environment would be very difficult for any platform to achieve." ; user (post 2): "It takes price breaking through my limit in order to get filled, even when I've left an order on the books for some time" (sentence continues) ; staff (post 9): "Are you referring to how our simulation engine is filling your trades? It seems the email address associated with this user does not have a live account" |
| Native API | Yes: REST + WebSocket (demo.tradovateapi.com / live), documented in the partner docs. Whether a prop-firm (eval or funded) user may use it is a firm rule (firm workers). | tv_partner_architecture.md L195 | "'https://demo.tradovateapi.com/v1/order/item?id=1000'" |
| Order types on the API | Limit, LimitIfTouched, MIT, Market, QTS, Stop, StopLimit, TrailingStop, TrailingStopLimit; TIF Day, FOK, GTC, GTD, IOC | tv_partner_place_order.md L85, L95 | "`orderType` (enum, required) — Limit, LimitIfTouched, MIT, Market, QTS, Stop, StopLimit, TrailingStop, TrailingStopLimit" ; "`timeInForce` (enum, optional) — Day, FOK, GTC, GTD, IOC" |
| OCO / bracket on the API | Native: order/placeoco (OCO) and order/placeoso (order-sends-order, brackets) | tv_partner_place_oco.md L7, L12; tv_partner_place_oso.md L7-11 | "OCO order strategies link 2 orders together such that if one order is filled, the other order is cancelled." ; "### Place an Order Sends Order order strategy." ; "OSO orders allow for the most complex multi-bracket trading strategies." |
| API rate limit | Two tiers. User level, authenticated: 5,000 per hour, 5,000 per minute, 5,000 per second (as printed; the hourly cap binds, about 1.4 requests per second sustained). Endpoint level per IP, rolling 1 h window, penalty ticket (p-ticket, p-time) on excess; the only order endpoint listed is dryrun (500/h). 429 on user-level excess. Note: these are the partner (prop-firm) docs; a separate end-user limit table was not found. | tv_partner_rate_limits.md L11-24, L30-33, L136-140, L146, L168 | "\| **Authenticated** \| 5,000        \| 5,000          \| 5,000          \|" ; "Endpoint limits use a rolling one-hour window, not a fixed hourly reset." ; "\| `dryrun`     \| 500            \| 1                  \| All                  \|" ; "the server stops handling requests for a period of time and responds to each new request with a 429 status code." |
| Market data behind the sim | Not documented on pages fetched (the Tradovate demo uses Tradovate's own CME feed per its marketing page, not saved). [unverified] | - | - |

## 3. Rithmic (R|Trader Pro, R|API+, R|Protocol API, Paper Trading / Exchange Simulator; used by Bulenox, Tradeify, Lucid and others)

| Item | Fact | Source file | Verbatim quote |
|---|---|---|---|
| Sim fill rule (vendor page) | Rithmic's Exchange Simulator fills against a simulated matching engine on live CME data; the product page does not state the fill rule. | rith_products_exchange-simulator.md L37 | "It connects to live exchange data in real time — the same data that powers live trading accounts. The difference is that orders are filled against a simulated matching engine rather than the actual exchange." |
| Sim fill rule (detail) | Queue model: fill when the market trades through the price AND the estimated queue ahead is depleted and there is quantity or opposite-side activity at the price; each account is simulated separately. Source is a 2019-01-31 post by an account named "Rithmic" on the Optimus Futures forum (forum, so a pointer; not on rithmic.com). [pointer: forum, vendor-attributed] | optimus_rithmic_paper_2413.json (post 3, user "Rithmic", 2019-01-31) | "Our filling algorithm also takes into account when your order was received by the simulator, Rithmic's estimated place of the order in the order queue and the order's attributes (price, size, buy/sell, etc.). We report a fill when the market trades through your price and when the orders ahead of you in the queue, based upon our estimate of your position in the queue and market activity, are depleted and there is quantity or opposite side order activity at your price level. This is not pessimistic. It is somewhat realistic." ; "our filling algorithmic treats each account separately which means that orders from one account in our paper trading system do not affect orders of any other account" |
| Native API | Yes: R\|API+ (C++/.NET), R\|Protocol API (WebSocket + protobuf, any language), R\|Diamond API (Linux, co-location required) | rith_products_api-suite.md L300 | "R \| Protocol API™ (a wire-line spec using WebSockets and Google Protocol Buffers, works in any language), and R \| Diamond API™ (ultra-low latency, Linux only, requires co-location)" |
| Order types / OCO / bracket | Market, limit, stop, bracket, OCO in the simulator; brackets, OCOs and trailing stops held server side | rith_products_exchange-simulator.md; rith_products_api-suite.md | "All order types: market, limit, stop, bracket, OCO" ; "Trailing stops, brackets, and OCOs that execute on Rithmic's servers — fire even when the client connection drops." |
| Sim is the conformance environment | The paper system is where R\|API+ and R\|Protocol API conformance is tested | rith_products_exchange-simulator.md | "The paper trading system is the same environment used for R \| API+™ and R \| Protocol API™ conformance testing." |
| API rate limit | Not published on rithmic.com pages fetched (api-suite, technology, faq). Unknown. | rith_products_api-suite.md; rith_support_faq.md | (no rate figure on the pages) |
| Vendor latency claims | R\|API+ and R\|Protocol API "<1ms" (order handling / order routing, server side, not network); Diamond "<250µs" tick-to-trade | rith_products_api-suite.md | "\| Typical latency \| <1ms \| <1ms \| <250µs \|" ; "\| Latency basis \| Order handling \| Order routing \| Tick-to-trade \|" |
| Connection points | Includes Chicago, Aurora and "USA West" | rith_technology.md L226 | "New YorkChicagoAuroraUSA EastUSA WestSão Paulo" |
| Market data behind the sim | Live CME data, the same feed as live accounts | rith_products_exchange-simulator.md L26 | "Rithmic's paper trading system connects to live exchange data from CME Group and Nasdaq." |

## 4. NinjaTrader simulation engine (Sim101 and NinjaTrader-hosted sim accounts)

| Item | Fact | Source file | Verbatim quote |
|---|---|---|---|
| Sim fill rule | Documented probabilistic queue model: not touch-fill; uses bid/ask volume, trade volume, time to simulate queue position, random state delays. | nt8_simulation.html.txt L12 | "The simulation engine is not a simple algorithm that fills your order once the market trades at your order price. The engine uses a scientific approach to determine fill probability by including a number of variables including: ask/bid volume, trade volume, time (to simulate order queue position), and random time delays for switching between order states." |
| Scope caveat | This engine applies to orders routed to NinjaTrader's own simulator (Sim101 and sim accounts NinjaTrader hosts). When NinjaTrader Desktop is only a front end to a firm's Tradovate or Rithmic account, the fill comes from that back end's sim, not from this engine. [inference from the help page's mixed live/sim description; not stated for prop accounts] | nt8_live_simulation_environment.html.txt | "NinjaTrader is a true mixed live/simulation platform. You can have multiple entry windows open and using the account drop down menu, simultaneously route orders to your live broker in one window while routing orders to the simulator in another." |
| Historical (backtest) fill options | Separate from the live sim; slippage applies only to market-type orders in backtests. Not relevant to F. | nt8_understanding_historical_fill_.html.txt L26 | "Slippage can be added to your order fills to help mimic real market conditions." |

## 5. Other back ends: CQG, Volumetrica/dxFeed, WealthCharts

| Item | Fact | Source file | Verbatim quote |
|---|---|---|---|
| CQG sim fill rule | **Undocumented** after 2 searches (help.cqg.com returned nothing on simulated fills). Lucid labels its Tradovate/NinjaTrader/TradingView path "CQG supported platforms", which suggests CQG connectivity behind Lucid's Tradovate accounts [inference]. | lucid_platforms.html.txt L17-20 | "CQG supported platforms:" followed by "NinjaTrader", "Tradovate", "TradingView" |
| Volumetrica (MFFU third-party platform path) sim fill rule | **Undocumented**: volumetricatrading.com FAQ and MFFU's Volumetrica article give no fill rule; 2 searches found none. | vol_faq.html.txt; mffu_volumetrica.html.txt | (no fill statement on either page) |
| Volumetrica data feed | dxFeed | mffu_volumetrica.html.txt L16 | "Volumetrica Trading Platforms, including desktop applications such as VolSys and VolBook, utilize dxFeed as their primary data source." |
| Volumetrica prop role | Supplies dashboards and platforms to prop firms | vol_faq.html.txt L9 | "Used by over 20 Prop Firms Futures worldwide for operational management and monitoring. Data quality is guaranteed by our partnership with dxFeed for real-time data feeds." |
| WealthCharts (Tradeify broker option) sim fill rule | **Undocumented**: 1 search found nothing first-party. | - | - |

Firm to back-end map (from firm pages fetched here; the firm workers' files are authoritative for each firm):
- Topstep: TopstepX / ProjectX only (A2_firm_topstep.md). Fill rule: trade-through (section 1).
- Lucid: "CQG" path (Tradovate, NinjaTrader, TradingView) and Rithmic path (lucid_platforms.html.txt L17-29).
- MFFU: Tradovate (trader.tradovate.com login, mffu_platforms.html.txt L15) and dxFeed-connected third-party
  platforms incl. Volumetrica (mffu_volumetrica.html.txt).
- Tradeify: Tradovate, Rithmic, WealthCharts (A2_firm_tradeify.md).
- Bulenox: Rithmic (A2_firm_bulenox, if written; Bulenox pages mention Rithmic 29 times, NinjaTrader 16).
Where NinjaTrader Desktop is used as the front end at these firms, the sim fill comes from the back end (Tradovate,
Rithmic, CQG), not from NinjaTrader's own Sim101 engine [inference, section 4 caveat].

## 6. Latency to CME Aurora (published measurements)

No co-location is assumed. CME Globex matches in Aurora, IL; the sources below measure to Chicago (city or
downtown data centres), so Aurora adds the Chicago-Aurora leg.

| Path | Value | Window | Source file | Verbatim quote | Note |
|---|---|---|---|---|---|
| Vancouver to Chicago (WonderNetwork servers) | median of 336 hourly run averages 53.2 ms RTT; range 52.9-60.5 ms | 2026-10-07 11:13 to 2026-10-21 12:13 (site time) | wn_vancouver_chicago.html.txt | "Table generated with the unix command line tool ping , executing 30 pings from Vancouver to Chicago ." ; first row "53.200ms" (avg) | data-centre to data-centre; a home connection adds last-mile latency. Median computed by this worker from the 336 avg cells. |
| Seattle to Chicago (WonderNetwork) | median 44.5 ms RTT; range 44.2-54.1 ms | same | wn_seattle_chicago.html.txt | first row "44.520ms" (avg) | Pacific Northwest alternative route |
| Azure West US 2 (Washington) to North Central US (Illinois) | 51 ms P50 RTT | 30-day window; page ms.date 2026-07-30 | azure_network_latency.html.txt L40, row "West US 2" in the Central US table | "The following tabs show the monthly percentile P50 round-trip times between Azure regions for a 30-day window. Latency values are in milliseconds (ms)." ; row "West US 2" with cells 38, 51, 56 under the columns Central US, North Central US, South Central US (table cells, read by script) | Azure backbone; region-to-region, not retail |
| Chicago (350 E. Cermak) to Aurora | 370 µs RTT rack to rack (microwave, best case) | April 2013 press release | mckay_aurora_cermak_370us_wb.html.txt L45 | "The private line service connects exchange datacenters in Aurora, IL and 350 E. Cermak Rd. in downtown Chicago in 370 microseconds round trip time from rack to rack." | vendor claim, 2013, specialised microwave; retail fibre is slower [unverified figure for fibre] |
| Chicago VPS to CME / platform gateways | 0.52 ms to CME and to Tradovate; <1 ms to Rithmic and CQG | Wayback capture 2026-04-11 | quantvps_chicago_wb.html.txt L50-53 | "CME Latency 0.52ms" ; "Tradovate Latency 0.52ms" ; "Rithmic Latency <1ms" ; "CQG Latency <1ms" | VPS vendor marketing claim, not an independent measurement |
| Rithmic server-side order handling | <1 ms (R\|API+, R\|Protocol API), excluding network | current site | rith_products_api-suite.md | "\| Typical latency \| <1ms \| <1ms \| <250µs \|" | vendor claim; adds to network RTT |

Summary for the lead (facts, no score): Vancouver-to-Chicago network RTT is about 50-55 ms on published
data-centre measurements (two independent sources: WonderNetwork 53 ms, Azure 51 ms from Washington state); from a
Chicago VPS the network leg to CME or the platform gateways is under about 1 ms on vendor claims. Platform-side
processing (sim engine, risk checks) is not published for Tradovate, ProjectX or CQG.

## 7. VPS rules at platform level

| Platform | Fact | Source file | Verbatim quote |
|---|---|---|---|
| Tradovate | No VPS prohibition found in the partner docs. The rate-limit page treats shared hosting and VPNs only as shared-IP cases for endpoint limits. | tv_partner_rate_limits.md L22 | "If you're behind a shared IP (corporate network, VPN, shared hosting), you may share limits with other clients." |
| Rithmic | No VPS prohibition found on rithmic.com. R\|Diamond API needs co-location; R\|API+ and R\|Protocol API do not. Connection points include Chicago, Aurora and USA West. | rith_products_api-suite.md L300; rith_technology.md L226 | "R \| Diamond API™ (ultra-low latency, Linux only, requires co-location)" |
| ProjectX / TopstepX | No ProjectX platform VPS rule found. Topstep's own rule (firm level, in A2_firm_topstep.md) forbids sending orders from a VPS. | (firm worker file) | see A2_firm_topstep.md: "The use of VPS, VPNs, and remote servers is prohibited by Topstep's Terms of Use." |
| NinjaTrader, CQG, Volumetrica, WealthCharts | No platform-level VPS rule found (1 search covered the platform-level question). | - | - |

Conclusion (fact, not score): VPS rules are set by the firms, not by the platforms. The firm workers' files give
each firm's rule (Topstep forbids it for order flow; Tradeify has a conditional VPS clause; Lucid and MFFU had no
statement found).

## 8. Canadian tax treatment of prop-firm payouts (not scored)

One line: no CRA page names prop-firm payouts. On CRA's general definitions, payouts from a firm for trading under
a contractor-style agreement would be business income ("income from any activity you do for profit", reported
with Guide T4002). That reading is this worker's interpretation, not a CRA ruling. For GST/HST, a person stops
being a small supplier above CAD 30,000 of worldwide taxable supplies, zero-rated ones included, over four
consecutive calendar quarters or within one quarter. Whether payouts from a non-resident firm count as taxable
(zero-rated export) supplies is not addressed on the pages fetched [unverified].

Sources: cra_what_a_business.html.txt L39, L51, L63: "A business is an activity that you intend to carry on for
profit and there is evidence to support that intention." ; "Business income includes income from any activity you
do for profit. For example, the income from a service business is business income." ; "Guide T4002 ,
Self-employed Business, Professional, Commission, Farming, and Fishing Income". cra_gsthst_when_register.html.txt
L57-58, L62-63, L285: "You do not exceed the $30,000 threshold Footnote 1 over four consecutive calendar quarters."
; "You are a small supplier." ; "You exceed the $30,000 threshold 1 in a single calendar quarter." ; "Include the
total amount of all revenues (before expenses) from your worldwide taxable supplies (including zero-rated supplies )."

## 9. Gaps, failures and negative results

- Tradovate sim fill rule: not documented by Tradovate (3 searches; the partner-docs sitemap of 468 pages has no
  simulation-fill page; community search). Only forum statements: users report trade-through fills; staff say the
  sim "tries to mirror" exchange matching.
- CQG, Volumetrica and WealthCharts sim fill rules: not documented after 2, 2 and 1 searches.
- Rithmic: the queue-model description comes from a vendor-named forum post (2019), not from rithmic.com. rithmic.com
  says only "simulated matching engine". Rithmic API rate limits are not published (1 search, 3 site pages).
- ProjectX: no sim matching-engine document. The trade-through rule comes from Topstep's help page, which does not
  say "simulated". The data-centre location (Northern Virginia) comes from a search snippet; the page now returns
  HTTP 404 and has no Wayback copy.
- Tradovate rate limits: the user-level table prints 5,000 for hour, minute and second, which reads like a table
  error. Only the hourly figure is a binding constraint at face value. The limits for end-user (non-partner) API
  keys were not found separately.
- Latency: no published measurement from a residential Vancouver line to Aurora was found. The figures are
  data-centre to data-centre (Vancouver/Seattle/Washington to Chicago) plus 2013 microwave Chicago-Aurora and
  2026 vendor VPS claims.
- Failed fetches: mckay-brothers.com live page (HTTP 404, Wayback used); quantvps.com (HTTP 429, Wayback used);
  canada.ca with the full browser header set (HTTP/2 INTERNAL_ERROR; a plain UA worked); help.cqg.com (no
  simulation page found); intercom.help/tradeify-test (404, no Wayback copy).
- WebSearch calls used: 26 of 40. No budget-exhausted notice was received.
