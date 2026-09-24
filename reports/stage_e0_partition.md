# Stage E.0 research partition (Task 3)

Written by the lead before any ClusterReader was dispatched (2026-09-23, 20:15 PDT). Each
ClusterReader reads only its own region. The regions are drawn so that two workers cannot read the
same mechanism from different angles. An overlap found afterwards is reported as a partitioning
failure, never as convergence.

## 1. Product ownership: every product belongs to exactly one cluster

| Cluster | Products (Topstep permitted list as read by the planning chat, 2026-09-23) | Exposures (contracts on one underlying, prices tied by arbitrage) |
|---|---|---|
| K1 equity index | MNQ, M2K, MYM, NKD; full-size ES, NQ, RTY, YM | Nasdaq-100 {NQ, MNQ}; Russell 2000 {RTY, M2K}; Dow {YM, MYM}; Nikkei 225 in USD {NKD}; S&P 500 {ES, MES}: leg only, never traded in Stage E |
| K2 rates | ZT, ZF, ZN, TN, ZB, UB | one exposure per tenor |
| K3 FX | 6A, 6B, 6C, 6E, 6J, 6S, 6M, 6N, E7, M6E, M6A, M6B | EUR {6E, E7, M6E}; AUD {6A, M6A}; GBP {6B, M6B}; CAD {6C}; JPY {6J}; CHF {6S}; MXN {6M}; NZD {6N} |
| K4 energy | CL, QM, MCL, NG, QG, MNG, RB, HO | WTI crude {CL, QM, MCL}; Henry Hub gas {NG, QG, MNG}; RBOB {RB}; ULSD {HO} |
| K5 metals | GC, MGC, SI, SIL, HG, MHG, PL | gold {GC, MGC}; silver {SI, SIL}; copper {HG, MHG}; platinum {PL} |
| K6 agriculture and livestock | ZC, ZW, ZS, ZM, ZL, HE, LE | one exposure per product |
| K7 crypto | MBT, MET | bitcoin {MBT}; ether {MET} |
| K8 cross-cluster | none of its own | relationships whose legs sit in two or more of K1 to K7 |

MES is closed. It appears only as a leg of a cross-product member (K1 inside the equity-index
complex, K8 across clusters), on non-holdout dates.

**Non-CME signal instruments** (cash indices, spot FX, spot crypto, LME or SHFE metals, the Osaka
Nikkei contract, cash Treasuries, the VIX index) belong to the cluster of the CME product being
traded. Examples: spot bitcoin leading MBT is K7; Osaka Nikkei leading NKD is K1; spot EUR/USD
leading 6E is K3; LME or SHFE copper leading HG is K5; the cash Treasury auction and ZN is K2; the VIX
index and NQ is K1.

## 2. Rules that bind every reader

1. **Source registry.** `reports/stage_e0_source_registry.jsonl`, one JSON object per line. Before
   fetching any full text, search the registry for the item's DOI, URL and title. If it is there, do not
   read it again: log one line "see <id>" and move on. If it is not, append your claim line FIRST
   (one `echo '<json>' >> reports/stage_e0_source_registry.jsonl`, a single line), then read. Fields:
   `{"id": "K4-017", "worker": "K4", "title": "...", "authors": "...", "year": 2014,
   "doi_or_url": "...", "claimed_pdt": "2026-09-23 21:04", "clusters_tagged": ["K4", "K5"]}`.
   Ids are your cluster label plus a running three-digit number.
2. **Stage D.1's literature log is already read.** 183 MES/ES/NQ items:
   `/home/kiros-li/.claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment/432f46d4-3795-43eb-a44b-a7f14d582823/d1/task1_log.md`
   (read-only, outside the repo). Do not re-read any source it lists; cite its row (for example
   "D.1 A10") where it matters to your cluster.
3. **Panel sources** (one mechanism tested separately on products from several clusters, with no
   cross-product signal: for example intraday momentum across 60 futures, or one announcement study
   covering bonds, currencies and commodities). The first reader to meet one claims it and logs the
   verified passages for EVERY cluster it covers, each passage tagged `[K#]`. The other clusters'
   CatalogWriters read those tagged passages from the claimant's log. A reader who meets an already
   claimed panel source writes one line "see <id>" and moves on.
4. **Cross-cluster items go to K8 only.** An item whose mechanism uses a leg from another cluster (a
   signal in one cluster's product predicting another cluster's product, or a spread across
   clusters) is not read by K1 to K7. Log it in one line under "Flags for K8" (source, item, the two
   legs, one phrase) with no full-text fetch. The lead routes the flags to K8.
5. **Announcements.** The effect of a scheduled release on product P belongs to P's cluster (a CPI
   study of Treasury futures is K2's; the same study's gold results are tagged [K5] by whoever claims
   it under rule 3). One cluster's response used to trade another cluster's product is K8's.
6. **Generic MES families.** The D.1 families (A session clock, B reference-level breakout, C
   short-horizon reversal and momentum, D volatility state, E calendar and events, F data-native
   statistics, G coarser-bar timeframes, H daily-bar constructions) are handled by a small core port
   set the lead fixes in design D6 for every product. Do not hunt for generic literature on them;
   D.1 did that. Log a source about a D.1 family only when it tests that family specifically on your
   cluster's products (for example an opening-range breakout on crude oil futures), tagged
   "port of D.1 family X".
7. **Sentiment and social media are shelved.** Log such an item in one line as "sentiment, shelved"
   and read no further.
8. **Horizon.** The XFA flattens every day by 15:08 CT (earlier for products that close earlier:
   grains 13:20 CT, livestock 13:05 CT). A mechanism that needs a position held past that point is
   logged as intraday-infeasible with the reason. Rules may READ overnight or earlier-day information;
   they may not HOLD overnight.
9. **No price data.** Read papers, articles and public pages only. Never download, open, chart or
   summarize bar, tick or order-book data for any product, and never call Databento.

## 3. The regions

### K1 equity index (MNQ, M2K, MYM, NKD; ES, NQ, RTY, YM as vehicles; MES and ES as legs)
Reads:
- lead-lag, relative value and spread behaviour INSIDE the US equity-index futures complex (ES, NQ,
  RTY, YM and their micros): which leads at minute horizons, NQ/RTY or ES/RTY spread reversion,
  dispersion between the indices;
- NKD: the Nikkei contract's behaviour around Tokyo cash hours and the Osaka contract's hours, the
  overlap of the CME, Osaka and Singapore sessions, the Tokyo open and close in CME time, Japanese
  releases and Bank of Japan decisions as they move NKD;
- index rebalance and reconstitution days (S&P quarterly rebalances, the Russell annual
  reconstitution, Nasdaq-100 reconstitution and special rebalances) and their intraday effect on
  the futures;
- evidence on a D.1 family tested specifically on NQ, RTY, YM or NKD (rule 6);
- signals from non-CME equity instruments (cash indices, VIX index) used to trade K1 products.
Does not read: generic S&P 500 or E-mini mechanisms (D.1's log covers them); anything with a rates,
FX, energy, metals, ags or crypto leg (K8); the S&P 500 exposure as a traded product.

### K2 rates (ZT, ZF, ZN, TN, ZB, UB)
Reads:
- the Treasury auction cycle (seed: Lou, Yan and Zhang 2013, RFS): pre-auction concession and
  post-auction recovery, and the intraday path around the 12:00 CT auction results for 2-, 5-, 7-,
  10-, 20- and 30-year and TIPS auctions; the quarterly refunding announcement;
- FOMC, CPI, NFP and other scheduled macro releases as they move Treasury futures: pre-announcement
  drift, the announcement-minute response, post-announcement drift or reversal; Fed communication
  (minutes, press conferences, speeches);
- Federal Reserve Board and New York Fed staff reports on Treasury-market microstructure;
- month-end and quarter-end index-extension flows; the quarterly Treasury-futures roll, delivery and
  cheapest-to-deliver effects; the 14:00 ET settlement window if a source studies it;
- INSIDE the curve: tenor lead-lag (ZN vs ZB, TN vs ZN), curve spreads and butterflies;
- evidence on a D.1 family tested specifically on Treasury futures (rule 6).
Does not read: rates with an equity, FX, gold, energy or crypto leg (K8).

### K3 FX (6A, 6B, 6C, 6E, 6J, 6S, 6M, 6N, E7, M6E, M6A, M6B)
Reads:
- the WM/Reuters 4 p.m. London fix (seed: Melvin and Prins 2015, JFM): pre-fix trend, post-fix
  reversal, month-end fix flows and equity-hedging rebalancing; the Tokyo 9:55 JST fix and gotobi
  days; the ECB reference rate;
- CME FX futures against spot FX: lead-lag, the CME session against the London and Tokyo sessions,
  time-of-day liquidity; the quarterly IMM roll;
- scheduled releases and central-bank decisions as they move FX futures (FOMC, NFP, CPI; ECB, BoJ,
  BoE, RBA, RBNZ, BoC, SNB, Banxico; local data such as Canadian employment for 6C);
- INSIDE FX: cross rates built from two CME FX futures (EUR/GBP from 6E and 6B, AUD/NZD from 6A and
  6N, EUR/CHF from 6E and 6S), triangular relationships;
- evidence on a D.1 family tested specifically on FX futures (rule 6).
Does not read: the dollar against gold, equities, rates, crude or crypto (K8); carry held overnight
(infeasible, rule 8).

### K4 energy (CL, QM, MCL, NG, QG, MNG, RB, HO)
Reads:
- the EIA Weekly Petroleum Status Report (Wednesday 09:30 CT), the API report the evening before
  (Tuesday 15:30 CT), the EIA weekly natural gas storage report (Thursday 09:30 CT) (seed: Halova,
  Kurov and Kucher 2014, JFM; named author Alexander Kurov): surprise responses, pre-release drift,
  informed trading, post-release drift;
- the Baker Hughes rig count, OPEC and OPEC+ meetings, weather-model update times for natural gas;
- INSIDE energy: crack spreads (CL, RB, HO), crude against natural gas, the RB and HO relationship;
- the NYMEX settlement window and trade-at-settlement flows; expiry and roll behaviour; the
  commodity-index roll (GSCI and BCOM roll period). K4 OWNS the commodity-index roll mechanism for
  every commodity: when a source covers metals or ags too, log those passages tagged [K5] or [K6];
- evidence on a D.1 family tested specifically on energy futures (rule 6).
Does not read: crude against CAD, crude against equities or rates, ethanol and corn (K8).

### K5 metals (GC, MGC, SI, SIL, HG, MHG, PL)
Reads:
- the LBMA gold price auctions (10:30 and 15:00 London) and the LBMA silver price (12:00 London),
  and their effect on COMEX futures (seed: Caminschi and Heaney 2014, JFM): pre-fix drift, post-fix
  reversal, the legacy London PM fix literature;
- INSIDE metals: gold and silver (ratio, lead-lag, spread), platinum and gold, copper against the
  precious metals;
- copper and the Asian session: SHFE and LME hours against the Globex overnight session, Chinese
  releases as they move copper;
- scheduled US releases as they move gold and silver (FOMC, CPI, NFP); the COMEX settlement window,
  options expiry, the roll and delivery period;
- evidence on a D.1 family tested specifically on metals futures (rule 6).
Does not read: the dollar or real rates against gold, equities against copper (K8); the
commodity-index roll (K4 owns it; K5's CatalogWriter reads K4's [K5] passages).

### K6 agriculture and livestock (ZC, ZW, ZS, ZM, ZL, HE, LE)
Reads:
- USDA reports and the market's reaction (seed: Scott Irwin and colleagues, farmdoc,
  farmdocdaily.illinois.edu): WASDE, Crop Progress, Grain Stocks, Acreage and Prospective Plantings,
  Export Sales, Hogs and Pigs, Cattle on Feed, Cold Storage; pre-release drift, the release-minute
  response, post-release drift, limit moves, release timing within or outside the session;
- INSIDE ags: the soybean crush (ZS, ZM, ZL), wheat and corn, hogs and cattle;
- the overnight session against the day session and the gap at the 08:30 CT day open; weather
  forecast updates during the growing season;
- the CBOT settlement window, first notice day and delivery, daily price limits;
- evidence on a D.1 family tested specifically on grain or livestock futures (rule 6).
Does not read: ags against energy (ethanol, corn and crude), ags against the dollar (K8); the
commodity-index roll (K4 owns it; K6's CatalogWriter reads K4's [K6] passages).

### K7 crypto (MBT, MET)
Reads:
- CME bitcoin and ether futures against spot: basis, lead-lag between CME and spot exchanges;
- the weekend gap between the CME Friday close and the Sunday open; the CME CF reference-rate window
  and settlement effects; monthly and quarterly expiry;
- INSIDE crypto: bitcoin and ether;
- scheduled US releases as they move CME crypto futures;
- evidence on a D.1 family tested specifically on crypto futures (rule 6).
Does not read: crypto against equities or the dollar (K8); anything from perpetual swaps or crypto
exchanges that has no CME angle, unless the mechanism is argued to transfer to CME futures;
sentiment (rule 7).

### K8 cross-cluster relationships (dispatched last)
Reads only relationships whose legs sit in different clusters:
- rates and equity index (for example Treasury futures leading equity-index futures at minute
  horizons, or the reverse);
- the dollar and gold; the dollar and commodities;
- crude and CAD; crude and equities; energy and rates (inflation expectations);
- one cluster's announcement response used to trade another cluster's product;
- every flag the lead routes to it from K1 to K7 (listed in its brief).
Does not read: any relationship whose legs sit inside one cluster (the cluster owns it: gold and
silver K5, crack spread K4, soybean crush K6, MNQ and M2K K1, the Treasury curve K2, cross rates K3,
bitcoin and ether K7); single-product mechanisms.

## 4. Where a mechanism could land twice, and who owns it

| Mechanism | Owner | Why |
|---|---|---|
| FOMC, CPI or NFP effect on one product | that product's cluster | rule 5 |
| the same release study covering several clusters | first claimant, passages tagged per cluster | rule 3 |
| one cluster's announcement response trading another's product | K8 | rule 4 |
| commodity-index roll (GSCI, BCOM) | K4 for every commodity, passages tagged [K5] [K6] | one mechanism, one reader |
| a D.1 family on a new product | that product's cluster, only if the source is product-specific | rule 6; the generic version is D6's |
| intraday momentum or any panel of many futures | first claimant, tagged per cluster | rule 3 |
| non-CME signal instrument for a CME product | the traded product's cluster | section 1 |
| settlement-window and expiry effects | the product's cluster | product-specific |
