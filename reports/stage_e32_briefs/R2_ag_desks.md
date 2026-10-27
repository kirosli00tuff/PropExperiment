# E.32 Part R2: how commodity and agricultural desks trade the soybean complex at short horizons

Worker: AgDesks-OpusHigh (ROOT R2_ag_desks), started 2026-10-27 00:40 PDT.
Evidence pages and log: reports/stage_e32_briefs/pages/R2_ag_desks/ (log.tsv). Helper: work/R2_ag_desks/R2_fetch.sh.
Source labels: [academic], [regulator], [exchange], [firm], [practitioner]. Every quote below is verbatim from the
saved file named next to it; [unverified] marks claims not read in full text.
No market data was read; no statistic was derived from data.

Status: complete (re-spawn finished 2026-10-27 02:42 PDT). Written section by section.

---

## P0. Planner pointer: Li, Wang and Diersen (NCCC-134 2024)

Source [academic, conference paper]: Li, Z., Z. Wang and M. Diersen (2024), "Do Agricultural Commodity Price
Spikes Always Stem from News?", NCCC-134 proceedings. File: LiWangDiersen_NCCC134_2024.pdf (.txt).

What it studies (verbatim):
- Scope: "We aim to identify and categorize both types of price spikes in corn, soybean, and wheat futures markets."
  (abstract) But the empirical work is corn only: "The analysis of price spikes is based on corn futures trading
  data. The end-of-5-minute intraday original data of prices for agricultural commodity futures were collected from
  the Chicago Mercantile Exchange Group (CME Group) from 01/01/2013 to 12/31/2022." and "only the normal daytime
  trading hours, from Monday to Friday between 8:30 a.m. and 1:20 p.m. CT, have been chosen." Soybeans are future
  work: "In addition, we plan to explore a wide range of agricultural futures, such as soybeans and wheat."
- Counts: "Over 2,403 trading days, we recorded a total of 3,419 jumps. The daily average number of jumps is 1.42."
  "we record 3,094 clusters of jumps ... Of these, there are 994 news-related clusters of jumps on 494 days, which
  occupy 32.13% of all clusters. The non-news-related clusters account for 67.87%."
- News timing is daily, not intraday: "we could not match the daily news precisely to the ... timestamp of our
  intraday trading data" (lines 140-144, paraphrase of a broken line; see file).
- Result on dynamics: "exogenous events exhibit a faster decay in their relaxation exponent, indicating a shorter
  memory span, in contrast to the more prolonged impact of endogenous events." (Conclusions). This is about the
  decay of volatility (jump intensity) after a shock, not about the sign of later returns.
- Jumps in the first and last 15 minutes of the day are dropped: "we exclude jumps occurring in the first and last
  15 minutes of the trading day."

Does it bear on desks or flows? No. It has no trader, position, order-flow or COT data; "endogenous" means only
"no dated news item that day", not "caused by a flow". It bears weakly on idea family 5 (non-news jumps): in corn,
about two-thirds of 5-minute jump clusters have no news that day, and their volatility relaxes more slowly than
USDA-day jumps. It says nothing about direction after a jump, and nothing about ZM. Use: a pointer that non-news
jumps are common and should be a stratum, not evidence of a tradable effect.

---

## A. Merchants and processors (ADM, Bunge, Cargill, Louis Dreyfus type): hedging and crush flows

### A.1 Facts

1. Merchants run a net commodity position, hedged with exchange futures, with daily volume limits and weekly VaR.
   [firm, 10-K] ADM Form 10-K FY2023, Item 7A (ADM_10K_FY2023_Item7A_quotes.txt; Firecrawl direct-quote, raw page
   not saved because sec.gov refuses an undeclared User-Agent):
   - "The Company manages its exposure to adverse price movements of agricultural commodities used for, and produced
     in, its business operations, by entering into derivative and non-derivative contracts which reduce the
     Company's overall short or long commodity position. Additionally, the Company uses exchange-traded futures and
     exchange-traded and over-the-counter option contracts as components of merchandising strategies designed to
     enhance margins."
   - "In addition, the Company, from time-to-time, enters into derivative contracts which are designated as hedges
     of specific volumes of commodities that will be purchased and processed, or sold, in a future month."
   - "Volumetric limits are monitored daily and VaR calculations and sensitivity analysis are monitored weekly."
   - Item 1A (WebFetch, cut to 125 characters by the tool): "to continually assess price and basis opportunities."
2. Processors hedge a few months of crush capacity with exchange futures.
   [firm, 10-K] Bunge 10-K FY2007, Note 1 (Bunge_10K_FY2007_hedge_quotes.txt; same route): "Bunge hedges portions
   of its forecasted U.S. oilseed processing production requirements, including forecasted purchases of soybeans and
   sales of soy commodity products, for quantities that usually do not exceed three months of processing capacity.
   The instruments used are exchange-traded futures contracts, which are designated as cash flow hedges."
   Later filings (FY2019, search snippet only) say most commodity contracts are economic hedges not designated for
   hedge accounting [unverified: search snippet].
3. The textbook processor hedge is a three-step crush: long soybeans, short meal and oil, unwound in steps.
   [academic] Dahlgran (2005), JARE 30(3) (Dahlgran_JARE2005.pdf): "Tzang and Leuthold (1990) describe a
   three-step soybean-crushing hedge: (a) at the beginning of the planning horizon, buy soybean futures and sell
   soybean meal and soybean oil futures; (b) when processing is initiated, buy soybeans and sell the soybean futures
   contracts; and (c) when processing is complete, sell soybean oil and meal and buy soybean oil and meal futures.
   These steps are respectively denoted as anticipatory hedging, transformation hedging, and hedge closure."
   And: "The crush spread involves a long soybean futures position and short soybean meal and soybean oil futures
   positions in the ratios of 47 pounds of meal and 11 pounds of oil for each bushel of soybean futures."
   Abstract: "(b) anticipatory hedging provides less risk protection than product-transformation hedging".
   The model allows "up to 52 transactions per year" (weekly), i.e. the academic frame is weekly-to-quarterly
   rebalancing, not intraday.
4. Physical-commodity futures are traded more by end users and manual traders than financial futures.
   [regulator] CFTC OCE, Haynes and Roberts (2015), "Automated Trading in Futures Markets"
   (CFTC_oce_automatedtrading.pdf): "the products with the lowest level of automated participation are the physical
   commodity classes, encompassing energy, metals and agricultural products like oil, copper and wheat. Physical
   commodity futures trading often has a higher level of both buy- and sell-side end users who consume and produce
   these goods, and often trade on a manual basis."
   [regulator] CFTC OCE, Fett and Haynes (2017), "The Futures Trading Landscape" (CFTC_oce_futureslandscape.pdf):
   "Trading in physical futures contracts is more concentrated among the individuals and corporations who are part
   of the manufacturing process." and "Because producers and consumers are exposed to the price fluctuations of a
   physical commodity over extended periods of time, this can often require multi-leg hedges across multiple
   contracts or trading in the relative value of a long-dated versus a shorter-dated contract."
   And: "For the products where they are the most active, Corporations participate, relatively equally, in both
   outright and spread trading."

### A.2 When do merchant and processor flows hit ZM, and are they predictable intraday?

What the sources support:
- Merchant hedges are tied to cash transactions (purchases from elevators and farmers, product sales to feed
  mills and exporters) and to a crush plan that runs weeks to months ahead (Bunge: up to three months of capacity).
  Their futures orders are therefore triggered by cash deals and by risk limits checked daily (ADM), which are not
  observable to us. No source read gives an intraday timetable for merchant hedging.
- Hedges go on as spreads or multi-leg packages (Fett and Haynes; Dahlgran's crush), so a large share of commercial
  ZM volume plausibly trades in the crush or calendar spread books rather than as outright ZM aggression. R3b
  section (b) covers implied spreads; whether commercial crush orders reach the ZM outright book only through
  implied prices is a microstructure question for R3b, not evidenced here.
- Nothing read supports "merchant flow is predictable intraday". The only predictable commercial behaviour in the
  evidence is weekly and contrarian (Kang, Rouwenhorst and Tang, section C), and it is visible only with a
  three-day lag in the COT.
- What we cannot see: merchants' cash-basis bids (not in our data), customer sales, and the actual times of their
  futures orders. The owned ZM MBO feed is anonymous (no account or firm identifier; per the program's earlier data
  notes, not re-read here), so merchant flow can only be inferred from order size and spread trading.

Null result: three discovery queries (merchant 10-K hedging, Bunge crush margin hedging, processor hedging
transaction frequency) found no study that times processor futures orders within the day.

---

## B. Proprietary trading shops and market makers in grains

### B.1 Facts

1. [regulator] CFTC OCE, Haynes and Roberts (2017), "Automated Trading in Futures Markets - Update"
   (CFTC_oce_automatedtrading_update.pdf), Table 3, soybean futures (ZS, not ZM), share of volume by counterparty
   type, first sample Nov 12 2012 - Oct 31 2014, then Nov 1 2014 - Oct 31 2016: "Agriculture - Grain and Oilseed
   Soybean 93 115 15.2 25.1 42.5 45.6 36.3 24.1" (columns: total volume mm; ATS-ATS %; ATS-MAN %; MAN-MAN %, each
   for the two periods). So in 2014-16 about 25% of ZS volume was automated-vs-automated and 24% manual-vs-manual.
2. Same source, Table 1, product group: "Agriculture - Grain and Oilseed 16 13 5.6 (0.4) 4.1 (0.3) 39.0 (2.7)
   49.0 (3.9) 55.4 (3.8) 46.9 (3.8)" (non-electronic %, ATS %, manual %): manual trading still about 47% of grain
   and oilseed volume in 2014-16, against e.g. 15.6% in G10 FX ("FX - G10 ... 16.4 (1.1) 15.6 (1.0)").
3. Small accounts dominate soybean volume. [regulator] Haynes and Roberts (2015), Table (small vs large volume
   traders, 2012-14): "Soybean 59,739 19.2 42.2 815 17.2 15.4" (small traders: N, ATS %, MAN %; large: N, ATS %,
   MAN %), with the text: "for individual products like corn and soybeans, small traders contribute the majority
   share of volume; these contracts have a wide set of participants who, individually, execute small quantities,
   but are significant in aggregate." "Large" is defined there as "an account which contributes at least 0.5
   percent to a given day's volume".
4. Spread trading is a large share of soybean volume. Same 2015 table by order type, soybean row: "Soybean 9.1 2.6
   3.5 17.9 9.0 15.6 9.8 8.1 18.4" (ATS-ATS RO-RO, RO-SP, SP-SP; ATS-MAN RO-RO, RO-SP, SP-SP; MAN-MAN RO-RO, RO-SP,
   SP-SP; RO = regular outright, SP = spread). Summing the SP-SP columns: 3.5 + 15.6 + 18.4 = 37.5% of ZS volume was
   spread-against-spread, and outright-against-outright 9.1 + 17.9 + 9.8 = 36.8% (my arithmetic on the quoted
   row; the row omits non-electronic volume).
5. [regulator] Fett and Haynes (2017): "PTFs, and to a lesser extent banks, are usually active throughout the
   trading day, often trading in smaller sizes and with shorter holding periods. Others, like asset managers, trade
   only a handful of times on an average trading day, with activity often concentrated near the settlement period.
   These traders are usually more tilted to spread trading, where they roll large positions out of an expiring
   contract, usually using a relatively small number of large volume trades."

6. HFT share of soybean volume, account-level. [regulator WP, academic] Coughlan and Orlov (CFTC, July 2022 draft),
   "High-Frequency Trading and Market Quality: Evidence from Account-Level Futures Data"
   (CoughlanOrlov_CFTC_2022_HFT.pdf), trade capture data 2012-2021, nine contracts incl. corn, soybeans, wheat:
   - Table 1: "Agriculture   Soybeans         13.1%    36.0%     175.8%       24.8%" (HFT market share 2012, 2020,
     percent change, average over the sample). Against "Energy        WTI crude oil    29.1%    53.9%" and
     "Financials    E-mini S&P500    31.8%    49.7%".
   - HFT is defined by behaviour, not by firm type: "Accounts are classified as HFTs if they trade more than 0.25% of
     total volume in a calendar year, have an end-of-day inventory less than 20% of their trading volume, and never
     hold more than 30% of their daily trading volume at any point in time within the trading day."
   - Abstract: "greater participation by HFTs is strongly associated with improvements in market quality ...
     although higher rates of aggressive trading, such as those observed when HFTs trade directionally to reduce
     their positions, produce an adverse effect on market quality."
   - Why grain HFT share was low until 2015 (settlement mechanics): "the HFT speed advantage was somewhat hindered
     during the settlement period when pit trades were included in the daily settlement calculations" and "during
     the settlement period a large percentage of daily volume is traded, on average, and large price movements are
     common. The settlement period also happens to be the end of the trading day when HFTs need to close out their
     positions". The blended settlement "was abandoned in 2015 when CME closed its agricultural futures pits."
   - ZM is not in the sample; the soybean row is a proxy only.
7. A market-quality view from an ag economist (extension talk, practitioner/academic; pointer-grade but full text
   read). Janzen (2018), "High Frequency Trading in Agricultural Futures Markets: What Low Frequency Traders Should
   Know" (Janzen_KSU_HFT_ag.pdf): "HFT is prevalent, but not dominant in major ag futures markets." On USDA releases:
   "July 2018, USDA announced end of "lock-up" procedure for major report releases; news organizations no longer
   have early access to WASDE, Grain Stocks, and other reports" and "Some news organizations may have been able to
   send out report up to 2 seconds before USDA posted report".
8. Minute-scale reversal in corn, attributed by the speaker to tick size (academic talk). Jones (2018),
   "High-frequency trading and changes in futures price behavior" (Jones_KSU_HFT_presentation.pdf), on nearby corn
   1-minute returns from RTH transaction prices: "In recent data, almost 30% of the one-minute price change is
   reversed in the next minute"; "Evidence for soybeans is similar"; "Most likely explanation in this case: the
   minimum tick is too big, at least for right now". The benchmark slide says "Bid-ask bounce and temporary moves in
   prices would lead to [rho] < 0." Caution for us: a negative 1-minute autocorrelation measured on LAST-TRADE
   prices is largely bid-ask bounce, which a 1-lot paying the spread cannot harvest (it is the spread). Any ZM
   reversal feature must be measured on mid-quotes (ZM MBO lets us), not on trades. The corn table of big moves
   (0.5% or more) shows the "fraction of big moves that are at least half reversed 1 min. later" at 15%-24% in 2007-2014
   and 37%, 22%, 38% in 2015, 2016, 2017 ("2015 65 -0.15 37%", "2017 34 -0.19 38%"); even in the latest years most
   big 1-minute corn moves are NOT half reversed a minute later, and the counts are small (34-65 a year).
9. Prop-firm behaviour visible through enforcement (regulator). CFTC Press Release 7865-19
   (CFTC_PR_7865-19_soybean_spoofing.html/.txt): "a trader at a proprietary trading firm" who "between August 2013
   and June 2016 ... placed orders to buy or sell futures contracts on soybeans, soybean meal, and soybean oil with
   the intent to cancel the orders before execution", using "an automated tool to place relatively small bids or
   offers on one side of the market (Genuine Orders)" and "manually placed relatively large bids or offers on the
   opposite side of the market (Spoof Orders)". Consequence for an order-book-imbalance feature on ZM MBO: large
   resting size on one side is, at least sometimes, placed to be cancelled; imbalance features should be tested
   with and without large, short-lived orders, and cancellation-adjusted variants (R3b/M1 own the feature design).
10. Formal liquidity provision in grain OPTIONS, not futures (exchange filing hosted by the CFTC). CBOT Submission
    No. 11-489 (CFTC_CBOT_rul120811_options_MM_program.pdf): "a market making program in support of certain CBOT
    grain and oilseed options that are traded on the Globex platform", effective "January 01, 2012", product scope
    including "Soybean Meal options"; "All Product activity shall be conducted through a proprietary account of the
    market maker"; "Up to fifteen (15) participants may be selected"; ranking on "Time in the market", "Bid-Ask
    Spread; Book Size and Responses to requests-for-quotes"; incentives include "mass quote functionality" and fee
    waivers. That option market makers delta-hedge in ZM futures (a flow into the futures book) is the standard
    mechanism but is [unverified] in any source read; no ZM-futures market maker program was found.
11. Pit closure and crush packages (regulator WP). Gousgounis and Onur (CFTC OCE, 2016)
    (CFTC_oce_effectofpitclosure.pdf): "Similar concerns have also been raised by soybean brokers, who argue that
    CME's trading platforms do not allow trading in soy crush spreads with non-standard ratios." And: "although
    futures pit trading has been diminished to very low levels, it has not completely disappeared" (special
    strategy trades with an options leg). This supports A.2: some commercial crush hedging is executed as packages
    that never appear as outright ZM aggression on Globex.
12. Speed of automated versus manual traders (regulator, NOT grains: E-mini). Fishe, Haynes and Onur (CFTC OCE,
    "Speed and Latency in Treasury and e-Mini Futures Contracts - Part 2") (CFTC_oce_speedandlatency2.pdf):
    "algorithmic proprietary traders are the quickest group with 50% of the observations responding with new orders
    in less than 200 milliseconds. In contrast it takes manual proprietary traders over 9 seconds on average for
    one-half of the observations to respond." Equal-weighting participants: "the new cutoff for the algorithmic
    proprietary group increases latency time by a factor of 25 to just over 5 seconds". So the median algorithmic
    participant (not the median message) re-quotes in seconds, not microseconds; a 300-1,000 ms bot is slower than
    the fastest accounts but not out of the population.

### B.2 Prop shops and market makers: what the public record supports

- Who provides grain liquidity: account-level CFTC data show HFT-type accounts at about a quarter of soybean volume
  on average over 2012-2021 and 36% in 2020 (Coughlan and Orlov), with manual trading still about 47% of grain and
  oilseed volume in 2014-16 (Haynes and Roberts 2017), and small accounts the majority of soybean volume (Haynes and
  Roberts 2015). Grains are therefore less dominated by fast liquidity providers than crude, gold or the E-mini.
- Named firms and their strategies: no filing, paper or regulator document read names a grain prop shop's strategy.
  Public pointers only: a CTA-database page describes a discretionary program trading "mainly ... the soybean
  crush" (County Cork LLC, ctadatabase.fundpeak.com, search snippet; pointer, not evidence); a 2006 CBOT release
  names a Chicago firm as market maker for crush-spread options (cmegroup.com, not fetched under the stage CME rule;
  pointer). One WebSearch for grain prop job descriptions returned none.
- What prop firms are documented doing in the soybean complex: market making (CBOT options program), and one
  enforcement case of spoofing across ZS, ZM and ZL with automated small orders against manual large ones.
- Null result: two discovery queries (grain prop job descriptions and crush market makers; CFTC-hosted CBOT market
  maker filings for grain futures) found no ZM-futures market maker program and no public description of a grain
  prop shop's short-horizon edge. Stopping rule met for (b): full text read from 5 regulator/academic sources
  (Haynes and Roberts 2015, 2017; Fett and Haynes 2017; Coughlan and Orlov 2022; Gousgounis and Onur 2016) plus the
  CBOT filing and the enforcement release; the last 3 queries surfaced nothing new on named shops.

---

## C. CTAs, index funds and COT positioning

### C.1 Who the COT categories are, and when the COT is public

[regulator] CFTC Disaggregated COT explanatory notes (CFTC_disagg_explanatory_notes.html/.txt):
- "A "producer/merchant/processor/user" is an entity that predominantly engages in the production, processing,
  packing or handling of a physical commodity and uses the futures markets to manage or hedge risks associated
  with those activities."
- "A "swap dealer" is an entity that deals primarily in swaps for a commodity and uses the futures markets to manage
  or hedge the risk associated with those swaps transactions."
- "A "money manager," for the purpose of this report, is a registered commodity trading advisor (CTA); a registered
  commodity pool operator (CPO); or an unregistered fund identified by CFTC."
- Classification is a judgment call: "the actual placement of a trader in a particular classification based upon
  their predominant business activity may involve some exercise of judgment on the part of Commission staff".
[regulator] CFTC COT page (CFTC_COT_index.html/.txt): "The COT Report is generally published each Friday at
3:30 pm Eastern Time (US), using the data from the immediately preceding Tuesday of that week." and "The CFTC
receives the data from the reporting firms on Wednesday morning and then corrects and verifies the data for release
by Friday afternoon."
- Timing consequence (my arithmetic): 15:30 ET = 14:30 CT, after the 13:20 CT grain close, so the first ZM session
  that can react to a COT release is the Sunday 19:00 CT overnight open (R4 section 1.1 has the session grid). The
  positions are 3 trading days stale by then.
[regulator] Legacy COT notes (CFTC_COT_explanatory_notes.txt) on index traders: "All of these traders ... are
generally replicating a commodity index by establishing long futures positions in the component markets and then
rolling those positions forward from future to future using a fixed methodology."

### C.2 Does COT positioning predict returns? (academic)

1. Sanders, Irwin and Merrin (2009), JARE 34(2) (SandersIrwinMerrin_JARE2009.pdf) [academic], weekly 1995-2006,
   10 markets including soybean meal: "Bivariate Granger causality tests show very little evidence that traders'
   positions are useful in forecasting (leading) returns in 10 agricultural futures markets. However, there is
   substantial evidence that traders respond to price changes. In particular, noncommercial traders display a
   tendency for trend following." and "The results generally do not support use of the COT data in predicting price
   movements in agricultural futures markets." Table 1 (noncommercial positions lead returns, p-value of
   beta_j = 0 for all j), soybean meal row: "Soybean Meal 1, 1 0.929 0.929 0.687 0.921 0.000". Text: "the null
   hypothesis that noncommercial positions (PNL) lead or forecast market returns is rejected at the 5% level only in
   soybeans (p-value = 0.047)."
2. Kang, Rouwenhorst and Tang (JF 2020; read as the 2016 draft, KangRouwenhorstTang_2016draft.pdf, and NBER
   w19670) [academic], 26 commodities, weekly, 1994-2014:
   - "Short-term position changes are mainly driven by the trading demands of impatient speculators, while
     long-term variation is primarily driven by the hedging demands from commercial hedgers."
   - "speculators are momentum traders and hedgers are contrarians."
   - "during the weeks following a position change, commodities that are most heavily bought by speculators earn
     significantly lower returns than commodities that are sold by them."
   - Size: "the return impact of an average position change by hedgers, which is equal to 3.5% of total open
     interest ... changes the expected return in the subsequent week by 4.77%*3.5% = 0.168%, or by 9.1%
     annualized."
   - Post-publication part (the tradable part): "a positive excess return spread persists during days 5-20
     following the release of the CFTC report: 0.30% during days 5-10 (t = 3.62) and 0.15% (t = 1.23) during days
     11-20." Days 1-4 are before the report is public: "we separately report the excess returns during days 1-4
     when the report is not yet released and days 5-40 when the information contained in the report is in the
     public domain."
   - This is a cross-sectional, weekly, multi-commodity sort. It is not a ZM time-series signal and not intraday.
   Worked scale check (my arithmetic, assumption: ZM at an illustrative 400 USD/short ton, 0.10 USD tick): a 0.30%
   move over days 5-10 is 0.0030 x 400 = 1.2 USD/ton = 12 ticks spread over about 6 trading days, i.e. about 2
   ticks a day, against a daily range median of 96 ticks (E.28 Table 1). As a minutes-scale feature this is noise;
   at most it is a weekly regime tag.

### C.3 Index funds and their rolls

1. ZM is in the Bloomberg Commodity Index, which rolls on business days 6-10 at settlement prices.
   [firm, index provider] BCOM Methodology, February 2026 (BCOM_Methodology_FEB2026.pdf): the 2026 list includes
   "17. Soybean Meal"; "The "Roll Period" is used in this Methodology to refer to the sixth through tenth Business
   Days of the month"; "On each day of the Roll Period, the dependence of BCOM is shifted, at the rate of 20% per
   day, from WAV1 to WAV2". Contract calendar row (Jan..Dec lead future): "Soybean Meal Mar Mar May May Jul Jul Dec
   Dec Dec Dec Jan Jan". Reading the row (my reading, consistent with R3b c.1): BCOM rolls ZM in February (H to K),
   April (K to N), June (N to Z), October (Z to F) and December (F to H): five roll months a year; it never holds
   the Aug, Sep or Oct ZM contracts.
   - "Hedge Roll Period" means "the period of five Business Days, beginning with the fifth Business Day through and
     including the ninth Business Day of each month" (used for market-disruption handling).
   - Index value is computed at settlement prices (methodology section on daily calculation; "the CIPs are combined
     with the Settlement Prices of all Designated Contracts for such day"), so replicating swap dealers have a
     reason to trade at or near the 13:15 CT settlement (TAS or the closing range). That replicators actually use TAS
     for the BCOM ZM roll is [unverified]; R4 section 5.1 covers TAS.
2. Before BCOM added meal, soybean meal was not in the CFTC's index-trader (CIT) market set.
   [academic] Aulerich, Irwin and Garcia (NBER w19065, 2013) (AulerichIrwinGarcia_NBERw19065.pdf), CFTC
   non-public daily large-trader data: "CITs in 12 agricultural futures markets: CBOT corn, soybeans, soybean oil,
   and wheat; KCBOT wheat; CME feeder cattle, lean hogs, and live cattle; and ICE cocoa, cotton, coffee, and sugar."
   No soybean meal. When BCOM added meal is [unverified] here (R3b reports the current membership only).
3. Roll activity is spread wider than the Goldman window, and its price impact in grains is small and of the wrong
   sign for a pressure story. Same source:
   - "roll #1 and #2 contain about 90% of total rolling activity ... Roll #4 (the Goldman roll) contains
     approximately 65% of roll activity in 2004 but decreases to only about 50% in 2009".
   - "Point estimates of the cumulative impact of a one standard deviation increase in CIT positions on daily
     returns are negative and very small, averaging only about two basis points. The null hypothesis that CIT
     positions do not impact daily returns in a data-defined roll period is rejected in 5 of the 12 markets and
     estimated cumulative impacts are negative in all 12 markets; the opposite of the expected outcome if CIT rolling
     activity simultaneously pressures nearby prices downward and first deferred prices upward."
   - Same paper, literature review: spreads (calendar spreads) "increase during the narrow window when existing
     index positions are rolled from one nearby contract to the next, but the increase is temporary as spreads
     quickly return to the level prevailing before the roll window."
4. Predictable roll trades attract liquidity rather than predators, in a resilient market (crude oil evidence).
   [academic] Bessembinder, Carrion, Tuttle and Venkataraman (2015 draft of JFE 2016)
   (Bessembinder_etal_predictable_trades_2015draft.pdf), USO crude-oil ETF rolls: "The evidence indicates narrower
   bid-ask spreads, greater order book depth and improved resiliency on roll dates. We find that a larger number of
   individual trading accounts provide liquidity on roll dates, and do not find evidence of the systematic use of
   predatory strategies." Not grains; an analogy only.
5. Mou (2010/2011) on front-running the Goldman roll: full text not read (Columbia Academic Commons served a bot
   check page, saved as Mou_ColumbiaThesis.pdf which is HTML; SSRN is blocked). [unverified]. R3b c.1 cites it as
   unverified too.

### C.4 CTAs and trend followers

- The evidence read says large speculators (noncommercial / managed money) are trend followers at weekly horizons
  (Sanders, Irwin and Merrin: "noncommercial traders display a tendency for trend following"; Kang, Rouwenhorst and
  Tang: "speculators are momentum traders"). Kang et al. read that trend following as liquidity DEMAND that
  commercials supply, with short-run reversal of speculator-driven moves at the weekly horizon.
- Intraday CTA execution (what time of day trend followers trade ZM, how much at the settlement) is not in any
  source read. Fett and Haynes's statement that asset managers' "activity [is] often concentrated near the
  settlement period" is the only regulator evidence on time of day, and it is for asset managers across futures, not
  CTAs in ZM.


### C.5 Index rolls and calendar spreads (regulator WP), and two abstract-only pointers

1. [regulator WP] Brunetti and Reiffen, "Commodity index trading and hedging costs" (CFTC OCE)
   (CFTC_OCE_commodityindextrading.pdf), non-public daily LTRS positions in corn, soybeans and wheat:
   "We find evidence, consistent with the model, that index traders have become an important supply of price risk
   insurance." On the roll: "One of our key findings is that the inter-maturity spread increases with the percentage
   of CIT holdings in the first deferred contract. This is consistent with the finding elsewhere (e.g., Mou, 2010)
   that the CIT roll is associated with predictable changes in futures prices." Model comparative static: "the larger
   the size of the position being rolled, the more rapidly the spread increases with the percentage of their
   holdings in the first deferred contract." And: "the timing of the roll by major CITs is announced". The effect is
   on the CALENDAR SPREAD (front minus first deferred), at daily settlement frequency, not on the outright ZM
   direction, and soybean meal is not in their sample.
2. [academic, abstract only: unverified in full text] Frino et al. (author list not checked), "Are Hedgers Informed? An
   Examination of the Price Impact of Large Trades in Illiquid Agricultural Futures Markets", Journal of Futures
   Markets 2016, doi 10.1002/fut.21774 (OpenAlex abstract): "in a relatively
   illiquid deliverable agricultural (grain) futures market where most transactions are executed by hedgers ... the
   price impact of large buyer-initiated transactions is permanent, consistent with the proposition that they are
   executed by traders perceived to be informed." Market not named in the abstract (likely not CBOT) [unverified].
   Pointer: if it holds for ZM, large aggressive ZM trades carry information, which is a testable MBO feature (signed
   large-trade flow), owned by M1.
3. [academic, abstract only: unverified in full text] Cheng, Kirilenko and Xiong, "Convective Risk Flows in Commodity
   Futures Markets", Review of Finance 2015 (doi 10.1093/rof/rfu043; NBER w17921): "while financial traders
   accommodate the needs of commercial hedgers in normal times, in times of distress, financial traders reduce their
   net long positions in response to an increase in the VIX causing the risk to flow to commercial hedgers." Weekly
   positions; a regime pointer (VIX spikes) only.
4. Not found in full text: Brunetti, Buyuksahin and Harris (daily LTRS positions and prices; a Bank of Canada copy
   URL guessed from memory returned 404 and was deleted; the BoC author page had no PDF link). [unverified]

Stopping rule for (c): full text read for 6 sources (Sanders, Irwin and Merrin 2009; Kang, Rouwenhorst and Tang;
Aulerich, Irwin and Garcia; Brunetti and Reiffen; BCOM methodology; CFTC COT notes) plus Bessembinder et al.; the
last 3 discovery queries (daily positions and prices; hedger price impact; index roll front-running) surfaced only
the abstract-only items above.

---

## D. The information desks use, and what of it we can see

Cross-references, not re-verified here: release times against the CBOT session grid are R4 section 1.2 (Export Sales
Thursday 8:30 a.m. ET = 07:30 CT, inside the overnight session; NOPA monthly crush 12:00 noon ET = 11:00 CT for 2026;
WASDE and other USDA reports); board-crush arithmetic and the oil-share regime are R3a sections 1-2 and 8.

### D.1 Facts

1. Board crush and processing margin [academic]. Dahlgran (2005) gives the futures crush as "a long soybean futures
   position and short soybean meal and soybean oil futures positions in the ratios of 47 pounds of meal and 11 pounds
   of oil for each bushel of soybean futures" and the processor's anticipatory hedge as "buy soybean futures and sell
   soybean meal and soybean oil futures" (Dahlgran_JARE2005.pdf). Bunge hedges "quantities that usually do not exceed
   three months of processing capacity" (Bunge_10K_FY2007_hedge_quotes.txt). Soybean brokers told CME that its
   platforms "do not allow trading in soy crush spreads with non-standard ratios" (CFTC_oce_effectofpitclosure.pdf),
   so a processor's real hedge ratio often differs from the listed crush and is worked as separate legs or packages.
   Mechanism (not evidenced intraday in any source read): a widening board crush invites processors to sell the
   crush (sell ZM and ZL, buy ZS), which pushes ZM down relative to ZS; a narrowing one invites the reverse. This is
   the fundamental anchor behind the crush mean reversion R3a reviews; it works over days to weeks.
2. Cash basis [firm]. ADM states it seeks "to continually assess price and basis opportunities"
   (ADM_10K_FY2023_Item7A_quotes.txt; Item 1A, WebFetch excerpt). Basis bids are set by merchants in the cash market
   and are not in our data. No source read links intraday ZM futures moves to basis changes. Null result.
3. Export inspections [government]. USDA AMS WA_GR101 "Grains Inspected and/or Weighed for Export", dated "Mon
   October 26, 2026" for the "WEEK ENDING OCT 22, 2026" (USDA_AMS_wa_gr101_export_inspections.txt): a Monday report
   on the prior Thursday-ending week. It lists whole grains and soybeans (grade code "YSB"); the word "meal" does not
   occur in the report (grep count 0). So inspections bear on ZS, and on ZM only through the crush. The release
   clock time is not printed in the file [unverified].
4. Export sales and NOPA crush: release times per R4. The NOPA data page (NOPA_datastatistics.html) lists "NOPA
   Monthly Crush Report" next to "Members Only"; R4 records distribution through a data vendor to subscribers.
   The weekly FAS export sales page could not be fetched (FAS 403 to curl and WebFetch; the earlier saved file
   USDA_FAS_export_sales_about.html is 0 bytes). NOPA is the one release that is about meal directly (crush volume,
   meal and oil stocks).
5. USDA reports and how fast they are absorbed [academic, conference paper; found by R2, R4 does not cite it].
   Anderson, McKenzie and Noyes (2024), "The Information Content of The WASDE Report and Intra-Day Price Reactions",
   NCCC-134 (AndersonMcKenzieNoyes_NCCC134_2024.pdf), corn and soybean nearby futures, 2010-2021, N = 122 reports:
   "We do not find a significant market reaction within the first ten minutes after the report" (line 102) and
   "the price reaction continues to grow for soybeans between 30 minutes" [and the close] (line 104; the line breaks
   there); Results: "Neither corn nor soybeans have significant price reaction within 10 minutes of the report
   release. However, both have significant price reactions after 30 minutes of the release." The equations print in
   a broken font; from the text definitions: News_it = (1/n) sum_j ln(WASDE_it / Forecast_ijt), the mean log
   surprise of USDA world ending stocks against analyst j's forecast (eq. 1), and PriceChange_wit =
   ln(Close_wit / Open_wit) over window w in {10 min, 30 min, day close} (eq. 2), regressed by SUR on News with an
   early-release dummy. Window start: "began when the WASDE report was released or the opening price if the report
   was released before the market opened". The authors themselves cite Lehecka, Wang and Garcia (2014) for the
   opposite view ("market reactions happen quickly and are completed within about 10 minutes", line 84). This is a
   regression of the post-release return on the KNOWN surprise; it needs the analyst survey (Bloomberg), which the
   program does not own, and 122 events is small. Soybeans only, not meal. Flag to the lead and R4.
6. Weather and South American crops: no academic study of intraday reaction to weather-model runs or to CONAB
   (Brazil) crop reports was found. Two WebSearch queries returned only trade press (StoneX insights, Reuters columns,
   MarketsFarm; pointers only) and one Crossref query returned Stevens (1991), "Evidence for a weather persistence
   effect on the corn, wheat, and soybean growing season price dynamics", J. Futures Markets, doi
   10.1002/fut.3990110108 (title only, [unverified]). R4 section 4 covers weekend weather and the Sunday open. Null
   result for intraday evidence.
7. COT: section C (public Friday 14:30 CT, Tuesday positions; weak or no forecasting power at the weekly horizon
   in soybean meal; cross-sectional weekly hedging-pressure premium of Kang, Rouwenhorst and Tang).
8. Speed of public information: Janzen (2018) on the end of the USDA lock-up in July 2018: "Some news organizations
   may have been able to send out report up to 2 seconds before USDA posted report" (Janzen_KSU_HFT_ag.pdf).

### D.2 What this means for which information a 1-lot bot could use

| Information | Desk access | Our access (owned data, no paid feeds) | Horizon at which it matters (sources) |
|---|---|---|---|
| Cash basis, customer flow, crush plans | private, real time | none | days to months (ADM, Bunge, Dahlgran) |
| Board crush (ZS, ZM, ZL futures) | real time | yes, from ZM MBO and ZS/ZL MBP-1 | days to weeks for the margin anchor (R3a); intraday lead-lag is R3a/M2 |
| USDA reports (WASDE etc.) | public, same second | release times yes; surprise needs analyst surveys we do not own | minutes: absorbed in under 10 minutes (Lehecka et al., via Anderson et al.) or still moving after 30 minutes in soybeans (Anderson et al.); R4 owns the event design |
| NOPA crush | subscribers at release | release date yes; numbers not owned | monthly; no intraday study found (R4) |
| Export sales / inspections | public | release times yes; numbers not owned | weekly; inspections exclude meal |
| COT | public, 3 days stale | could be downloaded free (not owned now) | weekly or longer; no evidence at minutes |
| Weather, South America | paid weather services, local agents | none | overnight and weekend gaps (R4 section 4); no intraday study found |

---

## E. Which edges desks describe as structural, and which a 1-lot retail trader could share

### E.1 The edges in the evidence, by type

1. Liquidity provision (market making). HFT-type accounts trade about 25% of soybean volume on average and 36% in
   2020 (Coughlan and Orlov), earn the spread, and are hurt when they must trade aggressively to cut inventory
   (same source: "aggressive trading, such as those observed when HFTs trade directionally to reduce their
   positions"). The edge rests on speed and queue position. E.31 measured the outcome for us directly: a resting
   1-lot at the ZM touch under the trade-through rule had a gross 10 s edge of -0.970 ticks per fill (reports/
   E.31_RETURN.md section 3.5; V50 closed passive spread capture). NOT shareable.
2. Hedging-pressure (risk-transfer) premium. Speculators supply insurance to commercial hedgers and earn a premium;
   hedgers are contrarian and speculators are momentum traders (Kang, Rouwenhorst and Tang); index traders now also
   supply insurance (Brunetti and Reiffen). Horizon: weeks; size about 0.30% over days 5-10 after the COT release,
   cross-sectional. Shareable in principle by anyone holding positions for weeks; NOT at minutes (C.2 scale check:
   about 12 ZM ticks over 6 days).
3. Predictable flow (index rolls, settlement-period trading). BCOM rolls ZM on business days 6-10 of five months a
   year at settlement prices; asset managers trade "near the settlement period" (Fett and Haynes); the calendar spread
   moves with CIT roll progress (Brunetti and Reiffen) but the price impact on outrights in grains is "negative and
   very small, averaging only about two basis points" (Aulerich, Irwin and Garcia), and predictable roll days bring
   MORE liquidity, not predators (Bessembinder et al., crude oil). For a 1-lot on the outright: the flow is mostly in
   the spread book and at settlement, and the outright effect is about 2 basis points, i.e. at an illustrative
   400 USD/short ton, 0.0002 x 400 = 0.08 USD = 0.8 tick a day (my arithmetic; assumption stated), below the 1.59
   tick market-order break-even at Topstep (reports/stage_e28_ranking.md, rank 6 row "topstep | ZM", mu*_mkt 1.59).
   Weakly shareable, as a stratum (roll days versus others), not as a signal.
4. Information (fundamental). Merchants see cash basis, customer orders and crush plans; weather desks buy forecasts.
   That edge is private and slow (days). Public-release information is incorporated in seconds to tens of minutes
   (D.1 item 5). NOT shareable for the private part; the public-release part is R4's family 2.
5. Order-book information at the millisecond scale. Algorithmic proprietary traders respond to executions in under
   200 ms for half of messages in the E-mini (Fishe, Haynes and Onur); a 300-1,000 ms bot loses any race. Spoofing
   enforcement (CFTC 7865-19) shows large resting orders on the ZS/ZM/ZL books can be placed to be cancelled, so naive
   book imbalance can be gamed. NOT shareable at the race level.

### E.2 Latency arithmetic for a minutes-scale signal (standard ZM numbers, random-walk assumption)

Assumption: random-walk scaling sigma_h = sigma_1m x sqrt(h / 1 minute), with sigma_1m = 3.15 ticks (E.28 A0
Table 1, ZM standard window). Then:
- h = 1 s = 1/60 min: sigma = 3.15 x sqrt(1/60) = 3.15 x 0.1291 = 0.407 ticks.
- h = 300 ms = 0.005 min: sigma = 3.15 x sqrt(0.005) = 3.15 x 0.0707 = 0.223 ticks.
- Check: 0.407 / 0.223 = 1.83, and sqrt(1000/300) = sqrt(3.33) = 1.83. Consistent.
So the price noise added by a 300-1,000 ms delay is 0.2-0.4 ticks (one standard deviation), small next to the 1.59
tick break-even, provided the signal itself decays over minutes. A signal that decays within a second (book races,
release-second trading) is out of reach regardless. The latency question is therefore "how fast does the signal
decay", and only signals whose information half-life is well beyond one second qualify. This is an argument, not a
measurement; E.33 can check it by delaying entries by 1 s in the frozen pipeline (a design item for the lead).

### E.3 What a 1-lot at 300-1,000 ms could plausibly share (sources' mechanisms only; no data looked at)

- Plausible, testable at minutes: (i) the slow part of the reaction to public releases (soybeans still moving after
  30 minutes per Anderson et al.; contested by Lehecka et al.); (ii) commercial or index flow concentrated at known
  times (settlement window, BCOM roll days) as a STRATUM or regime feature; (iii) signed large-trade flow in the ZM
  MBO feed if large aggressive trades are informed (Frino et al., abstract only); (iv) crush-relative moves, where a
  merchant's hedge in one leg moves ZM before ZS/ZL catch up (R3a, M2).
- Implausible: spread capture (E.31), latency races, private information, COT at minutes, trading weather or South
  American news ahead of desks with paid feeds.

---

## F. What this means for a ZM directional search

Mechanisms worth testing (for the lead to weigh; no decision taken here):
1. Time-of-day and calendar strata from documented flows: the 13:14-13:15 CT closing range and settlement window
   (asset managers, index replication, HFT inventory flattening per Coughlan and Orlov), BCOM roll days 6-10 in
   Feb/Apr/Jun/Oct/Dec, COT Friday afternoon to Sunday open, Thursday export-sales overnight, NOPA days. Use them
   as strata or interaction features, not as stand-alone signals: the documented outright effects are about 2 basis
   points a day or less.
2. Signed aggressive volume by trade size on ZM MBO (large trades as a proxy for informed or commercial flow; Frino
   et al. abstract; Fett and Haynes on large, infrequent asset-manager trades). M1 owns the feature definition.
3. Reversal versus continuation after large 1-minute moves, measured on MID-quotes. Jones's corn evidence shows that
   most big 1-minute moves are not half reversed, and that trade-price autocorrelation is mostly bid-ask bounce.
4. Post-release drift (soybeans after WASDE, Anderson et al.), only if R4 recommends it and a surprise proxy can be
   built from owned data (for example, the first 5-minute return as the market's reading of the surprise; a design
   choice for the lead).
5. Book imbalance with a spoofing guard: test variants that drop large orders cancelled within a short time
   (CFTC 7865-19 pattern).

Mechanisms to drop, and why:
- COT positioning as a minutes-scale signal: no forecasting power at weekly horizons in soybean meal (Sanders, Irwin
  and Merrin, Table 1, noncommercials, soybean meal: p-values 0.929, 0.929, 0.687, 0.921; the last entry, 0.000,
  is the "Direction (sum of beta_j x 10^2)" column, not a p-value) and the only robust effect is a cross-sectional weekly
  premium of about 12 ZM ticks over 6 days.
- Front-running index rolls on the outright: outright impact negative and about 2 basis points (Aulerich et al.),
  liquidity improves on predictable roll days (Bessembinder et al.); the roll effect lives in the calendar spread.
- Merchant hedge timing: no source gives an intraday timetable; merchant orders follow private cash deals and are
  partly executed as packages off the outright book.
- Spread capture or queue-race strategies: closed by E.31 and V50; HFT-type accounts own this edge.

---

## P. Planner pointer verification (owned by R2)

| Pointer | Status | Evidence |
|---|---|---|
| Li, Wang and Diersen (NCCC-134 2024): what it studies, does it bear on desks or flows | VERIFIED as to content; it does NOT bear on desks or flows | Full text read (LiWangDiersen_NCCC134_2024.pdf). Title "Do Agricultural Commodity Price Spikes Always Stem from News?"; corn futures only ("The analysis of price spikes is based on corn futures trading data"), 5-minute prices 2013-2022, day session; "a total of 3,419 jumps"; "994 news-related clusters ... 32.13% of all clusters. The non-news-related clusters account for 67.87%"; news matched by day, not by minute. No trader, position or flow data. Relevant only as a pointer that non-news jumps are common (a stratum for idea family 5). See P0. |

---

## G. Evidence index (files in pages/R2_ag_desks/, every row in log.tsv)

| Source | Label | File | Used in |
|---|---|---|---|
| ADM 10-K FY2023 Item 7A / 1A | firm | ADM_10K_FY2023_Item7A_quotes.txt (quotes only; SEC 403) | A.1, D.1 |
| Bunge 10-K FY2007 Note 1 | firm | Bunge_10K_FY2007_hedge_quotes.txt (quotes only) | A.1, D.1 |
| Dahlgran 2005 JARE | academic | Dahlgran_JARE2005.pdf | A.1, D.1 |
| Haynes and Roberts 2015, 2017 (CFTC OCE) | regulator | CFTC_oce_automatedtrading.pdf, _update.pdf | A.1, B.1 |
| Fett and Haynes 2017 (CFTC OCE) | regulator | CFTC_oce_futureslandscape.pdf | A.1, B.1, E |
| Coughlan and Orlov 2022 (CFTC) | regulator WP | CoughlanOrlov_CFTC_2022_HFT.pdf | B.1, E |
| Janzen 2018 (K-State talk) | academic/extension | Janzen_KSU_HFT_ag.pdf | B.1, D.1 |
| Jones 2018 (K-State talk) | academic talk | Jones_KSU_HFT_presentation.pdf | B.1, F |
| CFTC PR 7865-19 | regulator | CFTC_PR_7865-19_soybean_spoofing.html/.txt | B.1, E, F |
| CBOT Submission 11-489 (CFTC-hosted) | exchange filing | CFTC_CBOT_rul120811_options_MM_program.pdf | B.1 |
| Gousgounis and Onur 2016 (CFTC OCE) | regulator WP | CFTC_oce_effectofpitclosure.pdf | B.1, D.1 |
| Fishe, Haynes and Onur, Speed and Latency Part 2 (CFTC OCE) | regulator WP | CFTC_oce_speedandlatency2.pdf | B.1, E (Part 1 saved, not cited) |
| CFTC COT pages and notes | regulator | CFTC_COT_index, CFTC_COT_explanatory_notes, CFTC_disagg_* | C.1 |
| Sanders, Irwin and Merrin 2009 JARE | academic | SandersIrwinMerrin_JARE2009.pdf | C.2, F |
| Kang, Rouwenhorst and Tang (JF 2020 draft; NBER w19670) | academic | KangRouwenhorstTang_2016draft.pdf, _NBERw19670.pdf | C.2, E |
| BCOM Methodology Feb 2026 | firm (index provider) | BCOM_Methodology_FEB2026.pdf | C.3 |
| Aulerich, Irwin and Garcia (NBER w19065) | academic | AulerichIrwinGarcia_NBERw19065.pdf | C.3, E, F |
| Bessembinder et al. 2015 draft | academic | Bessembinder_etal_predictable_trades_2015draft.pdf | C.3, E |
| Brunetti and Reiffen (CFTC OCE) | regulator WP | CFTC_OCE_commodityindextrading.pdf | C.5, E |
| Anderson, McKenzie and Noyes 2024 | academic (conference) | AndersonMcKenzieNoyes_NCCC134_2024.pdf | D.1, E, F |
| Li, Wang and Diersen 2024 | academic (conference) | LiWangDiersen_NCCC134_2024.pdf | P0, P |
| USDA AMS WA_GR101 | government | USDA_AMS_wa_gr101_export_inspections.txt | D.1 |
| NOPA data page | industry association | NOPA_datastatistics.html | D.1 |
| Frino et al. 2016 JFM; Cheng, Kirilenko and Xiong 2015 | academic | none (OpenAlex abstracts only) [unverified] | C.5 |
| Mou thesis | academic | Mou_ColumbiaThesis.pdf is a bot-check HTML page [unverified] | C.3 |

Saved but not used: CFTC_oce_liquidityfuturesmarkets.pdf (no grain content found by grep), CFTC_oce_speedlatency.pdf
(Part 1, Treasuries/E-mini), CFTC_OCE_whitepapers_index.html (discovery), BoC_Brunetti_authorpage.html (discovery),
USDA_FAS_export_sales_about.html (0 bytes), USDA_FAS_ESR_program.html (403 page), NOPA_monthly_crush.html (404 page).

## H. Search log, stopping and gaps

- Re-spawned at 02:34 PDT 2026-10-27 after the first run stopped at 00:51; sections P0, A, B.1 (items 1-5), C.1-C.4
  were on disk and kept; this run added B.1 items 6-12, B.2, C.5, D, E, F, P, G, H.
- WebSearch calls in this run: 4 (CONAB reaction; weather-model intraday; CFTC-hosted CBOT market maker filings; grain
  prop job descriptions). The first run's count is not recorded in the log [gap]. Crossref: 3 queries; OpenAlex: 2.
- Blocks: sec.gov 403 to undeclared User-Agent (quotes via Firecrawl directQuote only); fas.usda.gov 403 to curl and
  WebFetch (Scrapling not tried: the terms check was not done, so the route was not used); Columbia Academic Commons
  bot check; a guessed Bank of Canada URL 404. No cmegroup.com fetch (stage rule).
- Stopping: (a) merchants: 4 full-text sources plus the pit-closure WP, last 3 queries nothing new on intraday timing;
  (b) prop shops: met (see B.2); (c) met (see C.5); (d) release timing deferred to R4; weather and South America:
  null after 3 queries; (e) synthesis from the above.
