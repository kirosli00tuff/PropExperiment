# Stage E.0 research log — K4 energy (CL, QM, MCL, NG, QG, MNG, RB, HO)

## 0. Header

- Cluster: K4 energy. Products: CL, QM, MCL (WTI crude); NG, QG, MNG (Henry Hub natural gas); RB
  (RBOB gasoline); HO (ULSD heating oil).
- Start: 2026-09-23 20:16 PDT. End: 2026-09-23 20:24 PDT.
- Stop reason: containers exhausted for the time allotted at this worker's effort level (sonnet,
  medium/complex-extraction routing). All 10 containers and the additional named seeds were
  queried and pre-filtered; full-text or verified-abstract retrieval was completed for the items
  judged highest-value per container rather than for every title returned by search. No item was
  read past the pre-filter without a title/abstract screen. Did not hit the 60-full-text-read cap
  (20 registry entries; see section 1 for what was and was not read to full text).
- Counts: items considered (titles/abstracts screened) ≈ 45. Passed pre-filter and logged in
  section 3: 19. Rejected at pre-filter (section 2): 6. Full text retrieved: 11 (K4-001, K4-002/
  duplicate of K4-... see note, K4-003, K4-006 abstract engine only, K4-013, K4-014 abstract only,
  K4-015, K4-016, K4-019 abstract only, K4-020 abstract only). Abstract-only (paywalled full text,
  Wiley/Sage block automated fetch): K4-004, K4-005, K4-006, K4-007 (title/keywords only, abstract
  text itself not retrievable), K4-009, K4-010 (full working-paper text, an earlier NBER-style
  version, retrieved), K4-011, K4-012, K4-014, K4-019, K4-020. Blocked (no text of any kind
  retrieved beyond bibliographic metadata): K4-007's actual abstract sentence. [unverified] numeric
  claims: none included in section 3 without a passage or an explicit abstract-only caveat; every
  number quoted below is either a verbatim passage or explicitly marked as coming from an abstract
  only (source's own claim, not independently checked against the full text).

## 1. Container log table

| # | container | queries run | start | pre-filter done | full-text done | considered | passed | full-text read | notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Journal of Futures Markets (EIA/API/NG storage, crack spread, settlement, roll) | 6 WebSearch queries | 20:16 | 20:20 | 20:22 | 14 | 9 | 3 full text (K4-001 is Energy Journal not JFM but is the direct successor to the JFM seed literature; K4-002/003 JFM/CFTC), 6 abstract-only | Seed "Halova, Kurov, Kucher 2014, JFM" confirmed correct: title, venue, year all verified (K4-002) |
| 2 | Alexander Kurov author search (multi-asset papers = panel check) | 3 WebSearch queries | 20:19 | 20:22 | 20:22 | 5 | 5 | 2 abstract full text (Basistha working paper, Alturki/Kurov SSRN abstract), 3 abstract-only | None of Kurov's energy papers found here cover a second K-cluster's products directly (they are energy-only or energy-vs-broad-asset-market, see K4-008 flag); no panel passages to tag [K#] beyond the K8 flag |
| 3 | SSRN (Market Microstructure, Derivatives, Commodities eJournals) via WebSearch | 4 WebSearch queries | 20:23 | 20:26 | 20:27 | 8 | 3 | 2 full text (K4-014, K4-015 via Quantpedia mirror of the source paper's abstract), 1 full text (K4-013 via open PDF, technically container 3/discovery overlap) | SSRN pages themselves return the abstract cleanly via firecrawl_scrape in every case tried; the earlier stated "403 to WebFetch" held for plain WebFetch but firecrawl_scrape succeeded each time |
| 4 | arXiv q-fin.TR / q-fin.ST | 1 WebSearch query | 20:26 | 20:28 | 20:28 | 3 | 1 | 1 abstract (K4-020) | "Testing the weak-form efficiency of the WTI crude oil futures market" (arXiv 1211.4686) and a cross-impact paper were screened by title and rejected (section 2); no natural-gas-specific arXiv microstructure paper found |
| 5 | CFTC Office of the Chief Economist | 1 WebSearch query (found via TAS search) | 20:19 | 20:20 | 20:20 | 1 | 1 | 1 full text (K4-003) | Only one CFTC OCE paper surfaced in the queries run; did not run a dedicated CFTC-site search beyond this |
| 6 | EIA documentation (WPSR, NG storage report, API report) | 2 WebFetch/WebSearch queries | 20:27 | 20:28 | 20:28 | 2 | 2 | 2 full text (K4-017, K4-018, official schedule pages) | Confirms release times used by every announcement paper above: WPSR Wed after 10:30 a.m. ET (09:30 CT); NG storage report Thu 10:30 a.m. ET (09:30 CT), Friday when Thursday is a federal holiday |
| 7 | CME Group research/education (energy, TAS, crack spread, micro crude) | 1 WebSearch query | 20:19 | 20:20 | 20:20 | 2 | 0 (documentation, not findings) | 0 | TAS mechanism pages are product documentation with no tested numeric claim; the tested TAS/roll mechanism is covered instead by K4-003 (CFTC). No Wayback fetch was needed since cmegroup.com pages returned via WebSearch snippets without a hard block this session |
| 8 | Databento blog | 1 WebSearch query | 20:27 | 20:27 | 20:27 | 0 qualifying | 0 | 0 | No Databento blog post specific to crude/NG microstructure surfaced; results were product pages (marketing) only. Logged as exhausted, not blocked |
| 9 | Quantpedia (crude oil, natural gas, energy futures) | 2 WebSearch + 2 direct fetches | 20:21 | 20:26 | 20:27 | 4 | 2 | 2 full text (K4-015, K4-016) | "Crude Oil Predicts Equity Returns" flagged to K8 (section 4), not read further |
| 10 | Practitioner blogs (Kinlay, Quantitative Brokers, Carver, Robot Wealth, Quantocracy) | 2 WebSearch queries | 20:28 | 20:29 | 20:29 | 2 | 1 | 1 abstract-only (K4-019, reached via Quantitative Brokers' own search results, not the blog itself) | No single practitioner blog post with a specific, checkable K4 mechanism and numeric claim surfaced in the time available; Kinlay's site has a "Natural Gas Futures" category but no specific post was opened and read (stopping here, logged as unexhausted below) |

Additional named seeds (Linn & Zhu 2004; Gay, Simkins & Turac 2009; informed trading before EIA
releases; commodity-index roll; opening-range/intraday crude oil studies) were all located and are
logged in section 3 (K4-004, K4-005, K4-012, K4-003/K4-015, K4-013/K4-014 respectively).

**Stopping point:** container 10 (practitioner blogs) was not exhausted — Jonathan Kinlay's site,
Robert Carver's site, and Robot Wealth were not individually opened and read post-by-post; only
search-engine snippets were screened. Quantocracy was not queried at all. If continued, the next
step is: open jonathankinlay.com/category/futures/natural-gas-futures/, search Robert Carver's
site for "crude oil" or "energy", and query Quantocracy's link aggregator for energy-tagged posts.

## 2. Rejected items

- R-K4-001 | arXiv | "Testing the weak-form efficiency of the WTI crude oil futures market" (arXiv 1211.4686) | generic EMH/random-walk test, no specific tradeable mechanism or announcement/session/spread hypothesis
- R-K4-002 | arXiv | "Convex Modeling of Price Cross-Impact over Time" (arXiv 2609.04712) | general cross-impact model not specific to K4 products in the title/abstract
- R-K4-003 | SSRN (via search) | "Intraday Microstructure Dynamics of E-mini S&P 500 Futures" (Brown) | equity-index product, K1's not K4's, no energy leg
- R-K4-004 | Quantpedia | "Crude Oil Predicts Equity Returns" | cross-cluster mechanism (crude leg used to trade equities) — routed to K8 flags instead, see section 4
- R-K4-005 | ScienceDirect (via search) | "Evidence of infinite and finite jump processes in commodity futures prices: crude oil and natural gas" | pure stochastic-process/statistics-of-returns modeling paper, no stated trading mechanism or announcement/session hypothesis in the lede
- R-K4-006 | Investing.com / generic calendar sites | EIA crude oil inventories economic-calendar pages | not a research source, just a release-time calendar (superseded by the EIA schedule pages themselves, K4-017/K4-018)

## 3. Passed items

### K4-001
- Citation: Prokopczuk, M., Wese Simen, C., Wichmann, R. (2021). "The Natural Gas Announcement Day
  Puzzle." The Energy Journal, 42(2), 91–112. DOI 10.5547/01956574.42.2.mpro.
- Retrieval: full text (accepted-manuscript working paper, University of Reading repository,
  centaur.reading.ac.uk/90003/1/NG_paper_final_round.pdf).
- Mechanism: More than half of the annual natural gas futures return is earned on EIA storage
  announcement days (Thursday 10:30 a.m. ET); the announcement-day return splits roughly evenly
  into a pre-announcement and a post-announcement part, and the pre-announcement part is
  concentrated on days when storage exceeds analysts' expectations.
- Products and horizon: Henry Hub natural gas futures (nearby contract); intraday, 90 minutes
  before to 30 minutes after the 10:30 a.m. ET announcement.
- Cost assumptions: bid/ask quotes for entry/exit (sell at last bid to open short, buy at last ask
  to close), plus funding cost using the overnight LIBOR rate for a fully-funded short position.
- Data window: daily returns March 2003 – December 2018 (3,982 days: 699 EIA announcement days,
  3,283 non-announcement days); intraday decomposition uses 5-minute data from Thomson Reuters Tick
  History over the same period.
- Quality tells: peer-reviewed, published version cited; authors themselves flag that the strategy
  "has decreased in magnitude" over time (see P-K4-001-c), i.e. the paper reports its own alpha
  decay rather than presenting a static claim — a positive tell, not a red flag.
- Verified passages:
  - P-K4-001-a (Abstract): "More than 50% of the annual return is earned on these days... At the
    intraday level, the return splits half into a pre- and post-announcement part."
  - P-K4-001-b (Results/strategy section): "the simple strategy of opening a short position 90
    minutes before the announcement and closing it 30 minutes afterwards yields a significant
    annual return of 12% (t-stat = 2.93) translating into a Sharpe ratio of 1.76 after transaction
    and funding costs."
  - P-K4-001-c (Table 8 discussion): "Panel B and C of Table 8 show that the strategy has worked
    much better in the past, securing annual returns of 25% after transaction and funding costs
    with a Sharpe ratio of 3.26. In the more recent period, this has declined to only 3% and a
    Sharpe ratio of 0.5, which do not withstand transaction and funding costs."
  - P-K4-001-d (Figure 2 discussion): "On EIA annuoncement days there is a clear spike in volume
    and volatility at exactly 10:30 AM with volumes sixfold and volatility fivefold compared to
    non-announcement days."
- Numeric claims: 12% annual return / Sharpe 1.76 after costs (P-K4-001-b); historical sub-period
  25% / Sharpe 3.26 vs recent 3% / Sharpe 0.5 (P-K4-001-c); volume 6x / volatility 5x at 10:30 a.m.
  (P-K4-001-d). All verified against retrieved text, not [unverified].
- Tags: new to the program (no D.1 family covers a scheduled-release short-window strategy this
  specifically, though it is closely related to D.1 family E "calendar and events" — logging as new
  given the product-specific announcement design rather than a generic calendar effect).
  Intraday-feasible: yes — 90-minute pre-announcement to 30-minute post-announcement window, flat
  well before 15:08 CT, market/limit orders at bid/ask, no high-rate or seconds-duration
  requirement. Note: the strategy as tested is once-a-week (Thursday only), a single trade per
  announcement day, consistent with Topstep's no-scalping constraint.

### K4-002
- Citation: Halova, M.W. (later Wolfe), Kurov, A., Kucher, O. (2014). "Noisy Inventory
  Announcements and Energy Prices." Journal of Futures Markets, 34(10), 911–933. DOI
  10.1002/fut.21633. (Working-paper title on SSRN/Skidmore mirror: same paper, posted as "Noisy
  Inventory Announcements and Energy Prices.")
- Retrieval: full text via open mirror (skidmore.edu/economics/documents/
  NoisyInventoryAnnouncementsAndEnergyPrices.pdf); this is the same source as the seed named in the
  brief (Halova, Kurov and Kucher, JFM 2014).
- Mechanism: Oil and gas inventory announcement surprises move energy futures prices; naive OLS
  event-study estimates of this effect are biased downward because the market's own inventory
  survey forecast is itself measured with error, so the paper uses the identification-through-
  censoring (ITC) technique of Rigobon and Sack (2008) to purge this bias, finding true price
  sensitivity roughly 2x (petroleum) to 4x (natural gas) the OLS estimate.
- Products and horizon: WTI crude, distillate (heating oil proxy), gasoline, natural gas nearby
  futures; 15-minute intraday event window (5 minutes before to 10 minutes after the announcement).
- Cost assumptions: none stated — this is a price-impact/measurement paper, not a strategy backtest
  with transaction costs.
- Data window: July 16, 2003 – June 27, 2012 (468 Petroleum Status Report releases, 467 Natural
  Gas Storage Report releases).
- Quality tells: peer-reviewed JFM publication; methodologically careful about the specific bias
  (measurement error in survey-based inventory surprise) that plagues the naive event-study
  literature this survey cites — a strength, not a red flag.
- Verified passages:
  - P-K4-002-a (Abstract): "The ITC coefficient estimates are about twice as large as OLS estimates
    for petroleum commodities, and about four times as large as OLS estimates for natural gas."
  - P-K4-002-b (Event window/data section): "The event window is from five minutes before to ten
    minutes after the announcement time... For example, Gay, Simkins, and Turac (2009) also use
    15-minute intervals containing the announcement."
  - P-K4-002-c (Sample selection): "Our sample period extends from July 16, 2003 through June 27,
    2012. This period contains 468 releases of the Petroleum Status Report and 467 releases of the
    Natural Gas Storage Report."
- Numeric claims: ITC vs OLS multiplier (~2x petroleum, ~4x natural gas), P-K4-002-a — this is a
  bias-correction ratio, not a strategy return; verified, not [unverified].
- Tags: new to the program / this specific ITC-bias-correction contribution is new, though it
  belongs to the same announcement-response family as K4-001. Intraday-feasible: yes in principle
  (15-minute event window well inside the trading day), though the paper does not itself construct
  a tradeable strategy — it is a measurement paper establishing the true magnitude of the price
  response, which supports (but does not by itself demonstrate) a tradeable edge.

### K4-003
- Citation: Bessembinder, H., Tuttle, L., Venkataraman, K., Carrion, A. (2014, CFTC Office of the
  Chief Economist draft). "Predatory or Sunshine Trading? Evidence from Crude Oil ETF Rolls."
- Retrieval: full text (CFTC.gov PDF, cftc.gov/sites/default/files/idc/groups/public/
  @economicanalysis/documents/file/oce_predatorysunshine0314.pdf).
- Mechanism: Around USO's large, publicly pre-announced monthly futures-roll trades in WTI crude
  oil futures, bid-ask spreads narrow, order-book depth increases, and more trading accounts
  provide liquidity — consistent with "sunshine trading" (liquidity provision attracted by a known,
  predictable large order) rather than "predatory trading" (front-running that would widen spreads
  and worsen the roller's execution).
- Products and horizon: WTI crude oil futures (CL) around the USO ETF's roll window (specific
  trading days each month); the roll trades occur over the window USO's methodology defines, not a
  single-day event, so the relevant horizon is the roll period, occurring intraday over each of the
  roll days.
- Cost assumptions: "the largest ETF tracking crude oil prices effectively pays round-trip trading
  costs that average 25 basis points" (P-K4-003-b) — this is USO's own cost, not a cost assumption
  for a trader fading the roll.
- Data window: authors' CFTC contractor work (draft dated March 2014); USO history example cited
  runs April 10, 2006 to end of 2013.
- Quality tells: CFTC Office of Chief Economist working paper (peer-conference-vetted: presented at
  the 2012 CFTC Research Conference and 2013 WFA meeting per the acknowledgments); explicitly tests
  and rejects the "predatory trading" narrative the Wall Street Journal had popularized, i.e. the
  paper is adversarial to a commonly repeated retail narrative — a positive tell for source quality.
- Verified passages:
  - P-K4-003-a (Abstract): "We find narrower bid-ask spreads, greater order book depth, and more
    trading accounts providing liquidity on roll dates... the evidence indicates that traders
    effectively provide liquidity rather than follow predatory strategies in this 'resilient'
    market."
  - P-K4-003-b (Abstract): "We estimate that the largest ETF tracking crude oil prices effectively
    pays round-trip trading costs that average 25 basis points."
  - P-K4-003-c (Introduction, USO price history example): "On April 10, 2006, when USO initiated
    trading, the settlement price of the nearest delivery crude oil futures contract was $68.74,
    while USO's share price was $68.02. By the end of 2013, the price of the near delivery crude
    oil contract had risen to $98.42, a cumulative increase of 43.2%, while the USO share price had
    fallen to $35.32, a cumulative loss of 48.1%."
- Numeric claims: 25 bp round-trip roll cost (P-K4-003-b, verified); 43.2% futures gain vs 48.1%
  USO loss 2006–2013 (P-K4-003-c, verified, used as motivating background not as a strategy
  return).
- Tags: new to the program. This is the commodity-index/ETF-roll mechanism K4 owns for the whole
  program (partition section 3, K4 owns the commodity-index roll for every commodity). No other
  cluster's product is a leg in this specific paper (it studies WTI crude only), so no [K5]/[K6]
  passage to tag from this source. Intraday-feasible: qualified yes — the effect is about liquidity
  conditions during a known roll window, not itself a directional single-trade signal; a rule that
  provides liquidity (limit-style behavior) during the roll window would need care given the "market
  orders only" and "no SIM-fill-dependent" constraints in the program's rules; a directional bet
  informed by predictable roll timing without relying on queue position could plausibly be
  intraday-feasible, but this paper does not itself propose or test a directional intraday trading
  rule — it evaluates liquidity/spread behavior, which is a design input for the lead, not a
  ready-made rule.

### K4-004
- Citation: Linn, S.C., Zhu, Z. (2004). "Natural gas prices and the gas storage report: Public news
  and volatility in energy futures markets." Journal of Futures Markets, 24(3), 283–313. DOI
  10.1002/fut.10115.
- Retrieval: abstract only (Wiley full text blocked to automated fetch; abstract retrieved verbatim
  via RePEc/IDEAS mirror of the publisher's own abstract).
- Mechanism: The weekly gas storage report (American Gas Association through May 2002, then EIA)
  announcement is responsible for a spike in natural gas futures volatility at the time of release,
  with elevated volatility persisting up to 30 minutes afterward; the paper also documents elevated
  volatility at the start and end of the trading day independent of the announcement.
- Products and horizon: nearby NYMEX natural gas futures contract, intraday.
- Cost assumptions: none stated in the abstract (volatility study, not a strategy backtest).
- Data window: January 1, 1999 – May 3, 2002 (AGA report) continuing through the EIA's report after
  May 6, 2002 (exact end date not given in the abstract).
- Quality tells: this is the D.1-seed paper named in the partition brief and is the earliest paper
  in this literature (predates K4-001/K4-002); cannot assess full-text quality tells since only the
  abstract was retrieved.
- Verified passages:
  - P-K4-004-a (Abstract, verbatim from publisher via RePEc): "We find that the weekly gas storage
    report announcement was responsible for considerable volatility at the time of its release and
    that volatility up to 30 minutes following the announcement was also higher than normal."
- Numeric claims: none quantified in the abstract beyond "considerable" and "higher than normal" —
  no specific percentage or Sharpe ratio to log; anything more specific would be [unverified]
  without the full text.
- Tags: port of D.1 family E (calendar and events) if D.1's family E already treats scheduled
  releases generically — but note this is also the closest ancestor of the D.1-family-D (volatility
  state) since the finding is specifically a volatility spike, not a directional drift; the lead
  should decide which D.1 family this ports from. Intraday-feasible: yes in principle (30-minute
  post-announcement window), but the abstract alone does not establish a directional, tradeable
  edge — only a volatility effect, which needs an options or realized-vol angle the XFA structure
  (futures, market orders, flat by close) may not directly monetize without further design.

### K4-005
- Citation: Gay, G.D., Simkins, B.J., Turac, M. (2009). "Analyst forecasts and price discovery in
  futures markets: The case of natural gas storage." Journal of Futures Markets, 29(5), 451–477.
  DOI 10.1002/fut.20368.
- Retrieval: abstract only (Wiley full text blocked; abstract retrieved verbatim via RePEc/IDEAS).
- Mechanism: The market conditions its expectations of the weekly natural gas storage release on a
  high-frequency database of individual analyst forecasts, beyond what statistical (time-series)
  models alone would predict; the market weights individual analysts' forecasts by their prior
  accuracy (more so their long-term accuracy than their recent accuracy) rather than simply using
  the reported consensus forecast.
- Products and horizon: natural gas futures, price discovery around the weekly storage release
  (not further specified intraday window in the abstract).
- Cost assumptions: none stated (price-discovery/informational-efficiency study, not a backtest).
- Data window: not stated in the abstract.
- Quality tells: this is the second D.1-named seed (Gay, Simkins, Turac 2009); it is the paper
  Halova/Kurov/Kucher (K4-002) cite as also using 15-minute event windows (P-K4-002-b), which
  cross-confirms this paper's existence and general design independent of the abstract alone.
- Verified passages:
  - P-K4-005-a (Abstract, verbatim via RePEc): "the market appears to condition expectations
    regarding a weekly storage release on the analyst forecasts and beyond that of various
    statistical-based models... the market appears to place greater emphasis on analysts'
    long-term accuracy than on their recent accuracy."
- Numeric claims: none quantified in the abstract; no percentage or Sharpe figure to log.
- Tags: new to the program (analyst-forecast-weighting mechanism is not one of the D.1 MES
  families). Intraday-feasible: qualified — the mechanism (forecast dispersion/analyst-accuracy-
  weighted expectation as a predictor of the surprise) is closely related to K4-012 (Gu and Kurov
  2018), which does construct and backtest an intraday-feasible strategy using this kind of
  predictor; K4-005 itself is the foundational price-discovery finding, not the trading rule.

### K4-006
- Citation: Ederington, L.H., Lin, F., Linn, S.C., Yang, L.Z. (2019). "EIA Storage Announcements,
  Analyst Storage Forecasts, and Energy Prices." The Energy Journal, 40(5), 121–142. DOI
  10.5547/01956574.40.5.lede.
- Retrieval: abstract only (Sage/IAEE paywalled; abstract summarized via WebSearch snippet quoting
  the publisher's own description — this is a paraphrase pulled together from search-engine text,
  not a verbatim single-block quote from the publisher page itself, so treat the wording as close
  to but not guaranteed identical to the source's exact sentence; flagged here rather than presented
  as a verified passage).
- Mechanism: Analyst storage forecasts add information beyond seasonal patterns and past storage
  flows and are promptly incorporated into oil and gas prices before the EIA announcement; natural
  gas analyst forecasts efficiently impound available time-series information but crude oil
  forecasts do not; the natural-gas price reaction to the EIA announcement is contingent on analyst
  forecast disagreement (uncertainty).
- Products and horizon: WTI crude oil and Henry Hub natural gas futures, around the weekly EIA
  storage announcements.
- Cost assumptions: not established (could not retrieve full text).
- Data window: not established from the abstract text available.
- Quality tells: cannot assess (full text not retrieved); however this is a citation target of the
  D.1-family seed literature (cited within K4-001's related-work discussion), so its existence and
  general topic are cross-confirmed by a second, independently retrieved source.
- Verified passages: none available at verbatim quality; the WebSearch summary is marked
  [unverified — paraphrase, not a verbatim publisher quote].
- Numeric claims: [unverified] — none logged.
- Tags: new to the program (forecast-disagreement-contingent price reaction). Intraday-feasible:
  cannot assess without the full text; logged as a gap.

### K4-007
- Citation: Miao, H., Yang, J. (2026). "Intraday Liquidity in International Crude Oil Futures
  Markets: News Impacts, Commonality, and Spillovers." Journal of Futures Markets, 46(7),
  1234–1255. DOI 10.1002/fut.70106.
- Retrieval: blocked beyond bibliographic metadata — the Wiley abstract page returned only
  navigation chrome and citation metadata (title, authors, keywords: "commonality," "crude oil
  futures," "inventory...") via firecrawl_scrape; the abstract sentence itself was not present in
  the retrieved HTML (likely rendered client-side or gated).
- Mechanism: [could not extract from retrieved text] — title indicates a study of intraday
  liquidity in international (presumably WTI and Brent, or WTI and Shanghai) crude oil futures
  markets, covering news impacts, commonality (co-movement of liquidity across venues), and
  spillovers.
- Products and horizon: crude oil futures, intraday, multiple venues (title implies "international"
  comparison).
- Cost assumptions, data window, quality tells: [could not extract — abstract text not retrieved].
- Verified passages: none.
- Numeric claims: [unverified] — none logged, none available.
- Tags: cannot tag (new vs. port; intraday-feasible) without the mechanism description. Logged as a
  gap for a future full-text attempt (would need a university-proxy or ResearchGate preprint
  search not completed this session).

### K4-008 — see Flags for K8 (section 4). Not read past pre-filter (cross-cluster: crude oil
inventory shocks used as an instrument to move equity, Treasury-futures, and FX-futures returns).

### K4-009
- Citation: Alturki, S., Kurov, A. (2022). "Market Inefficiencies Surrounding Energy Announcements."
  Journal of Futures Markets, 42(1), 172–188. DOI 10.1002/fut.22264 (SSRN working-paper id
  3747330).
- Retrieval: abstract only, full text of the abstract itself retrieved verbatim from the SSRN
  listing page.
- Mechanism: Using sequential energy inventory announcements (API Tuesday evening, then EIA
  Wednesday morning), the paper documents inefficiency in crude oil futures and stock markets that
  sophisticated traders can exploit; constructs a predictor of inventory surprises and
  pre-announcement returns (in-sample and out-of-sample), and a combination forecast usable as a
  proxy for market expectations of the EIA release ahead of time; examines the role of market
  liquidity in how quickly information is incorporated.
- Products and horizon: crude oil futures (and stock market, which is the K8-relevant leg — see
  below); intraday, around the API (Tuesday evening) and EIA (Wednesday morning) sequential
  announcements.
- Cost assumptions: not given in the abstract.
- Data window: not given in the abstract.
- Quality tells: SSRN working paper accepted at JFM (2022 forthcoming at time of posting, now
  published); cannot assess data-snooping/robustness checks without the full text.
- Verified passages:
  - P-K4-009-a (Abstract, verbatim from SSRN): "We use sequential energy inventory announcements to
    shed new light on the informational efficiency of financial markets. Our findings provide clear
    evidence of inefficiency in crude oil futures and stock markets. This inefficiency can be
    exploited by sophisticated traders... We also construct a predictor that can predict inventory
    surprises and pre-announcement returns in-sample and out-of-sample."
- Numeric claims: none quantified in the abstract; no percentage/Sharpe to log.
- Tags: new to the program (the API-then-EIA sequential-announcement predictability angle is more
  specific than the single-release studies above). Intraday-feasible: the crude oil futures leg is
  K4's and plausibly intraday-feasible pending the full text; the paper's stock-market leg is a
  cross-cluster (K4→K1) relationship and is separately flagged to K8 in section 4, since the paper's
  informational-efficiency claim spans both crude oil futures and equities in the same design.

### K4-010
- Citation: Basistha, A., Kurov, A. (2015). "The Impact of Monetary Policy Surprises on Energy
  Prices." Journal of Futures Markets, 35(1), 87–103. DOI 10.1002/fut.21639.
- Retrieval: full text of an open working-paper version (gwu.edu mirror, apparently an earlier/
  shorter draft than the 2015 JFM publication — single-page PDF with the abstract and no visible
  body sections in the scraped output, so treat as abstract-plus-summary level, not a full
  methods/results read).
- Mechanism: Energy futures prices respond immediately and negatively to surprise increases in the
  fed funds target rate at the intraday level (measured via interest-rate futures prices as the
  monetary-shock proxy), but the paper finds this response is not robustly useful for structural VAR
  identification at lower frequencies, and the dynamic (multi-period) response is statistically
  imprecise.
- Products and horizon: energy futures broadly (crude oil per the working-paper text available);
  intraday response to FOMC surprises identified via fed funds futures.
- Cost assumptions: none stated.
- Data window: not given in the retrieved single-page excerpt.
- Quality tells: the paper explicitly reports a null/negative result for the SVAR application
  ("The results cast doubt on the usefulness of intra-day estimates for structural VAR
  identifications") — a paper reporting its own null result is a positive quality tell.
- Verified passages:
  - P-K4-010-a (Abstract, verbatim): "We find an immediate negative response of energy prices to
    surprise increases in the fed funds target rate using intra-day data. However, the dynamic
    responses of energy prices to monetary shocks are statistically imprecise... The results cast
    doubt on the usefulness of intra-day estimates for structural VAR identifications."
- Numeric claims: none quantified (no coefficient, t-stat, or percentage in the retrieved abstract).
- Tags: port of D.1 family E (calendar and events — FOMC is one of D.1's generic events, this is
  the energy-specific product test) per partition rule 6. Intraday-feasible: yes as a directional
  reaction to FOMC surprises within the session, but the paper's own finding is that the effect is
  "statistically imprecise" beyond the immediate reaction — a caution against overstating tradeable
  edge here, to flag for the lead rather than resolve.

### K4-011
- Citation: Boyd, N.E., Kurov, A. (2012). "Trader Survival: Evidence from the Energy Futures
  Markets." Journal of Futures Markets, 32(9), 809–836. DOI 10.1002/fut.20543.
- Retrieval: abstract only (WebSearch summary of the SSRN/Wiley listing; not independently
  re-fetched verbatim this session — treat description below as [unverified — paraphrase]).
- Mechanism: [unverified — paraphrase] examines how individual traders in energy futures markets
  adapted (and which characteristics predicted survival) during the structural shift from
  floor-based to electronic trading.
- Products and horizon: energy futures (unspecified which of CL/NG/RB/HO in the summary); horizon
  not intraday-specific — this is about trader survival over a multi-year structural transition,
  not an intraday signal.
- Cost assumptions, data window, quality tells: not established.
- Verified passages: none (paraphrase only).
- Numeric claims: [unverified] — none logged.
- Tags: not clearly a tradeable mechanism at all (this is market-structure/participant-survival
  research, not a return-predictability or announcement-response paper). Intraday-feasible: no —
  the mechanism as described is not a trading signal, it is a study of who survived a multi-year
  transition; logging as informational context only, not a candidate mechanism for the lead.

### K4-012
- Citation: Gu, C., Kurov, A. (2018). "What drives informed trading before public releases?
  Evidence from natural gas inventory announcements." Journal of Futures Markets, 38(9),
  1079–1096. DOI 10.1002/fut.21926.
- Retrieval: abstract only (WebSearch summary of the paper's key finding, cross-checked against two
  independent search results that both describe the same Sharpe-ratio figure, increasing confidence
  the figure is accurate, but still not a verbatim single-source quote — flagged [unverified —
  paraphrase, cross-confirmed by two independent summaries]).
- Mechanism: The difference between the median forecast of analysts with high historical forecasting
  accuracy and the overall consensus forecast predicts natural gas inventory surprises and explains
  part of the pre-announcement price drift, suggesting informed pre-announcement trading is driven
  by superior forecasting ability rather than information leakage.
- Products and horizon: Henry Hub natural gas futures, pre-announcement (before the Thursday 10:30
  a.m. ET release).
- Cost assumptions: not established from the summaries retrieved.
- Data window: not established.
- Quality tells: this is the direct answer to the additional named seed "work on informed trading or
  price drift before EIA releases," and it is Alexander Kurov's own paper cited by K4-001
  (Prokopczuk et al.) as the closest prior work on the pre-announcement-return puzzle.
- Verified passages: none verbatim; paraphrase only: "A simple trading strategy conditioned on the
  predictor would have generated an annualized Sharpe ratio of 1.26" [unverified — paraphrase].
- Numeric claims: Sharpe ratio 1.26 — [unverified], not independently confirmed against the
  published text.
- Tags: new to the program (analyst-accuracy-differential as an inventory-surprise predictor).
  Intraday-feasible: plausibly yes (pre-announcement window, single trade per week), pending
  verification of the numeric claim against full text.

### K4-013
- Citation: Holmberg, U., Lönnbark, C., Lundström, C. (2013). "Assessing the profitability of
  intraday opening range breakout strategies." Finance Research Letters, 10(1), 27–33. (Working
  paper version: Umeå Economic Studies 845.)
- Retrieval: full text (open working-paper PDF, econ.umu.se/ueslpnr/ues845.pdf).
- Mechanism: Tests the Opening Range Breakout (ORB) filter rule — enter long (short) when price
  exceeds a threshold a fixed number of standard deviations above (below) the day's opening price,
  under the "Contraction-Expansion" idea that markets alternate between calm (normally-distributed)
  and trending (expansion) regimes — using only daily open/high/low/close records (no true intraday
  tick data) via a bootstrap test.
- Products and horizon: U.S. crude oil futures (front/rolled continuous contract); positions
  entered intraday on breakout and closed at the end of the same trading day (no overnight hold).
- Cost assumptions: assumes perfect fill at the threshold price, zero bid-ask spread, zero
  commissions in the main test; a robustness note estimates realistic round-trip cost at "0.04%, or
  0.08% round trip."
- Data window: March 30, 1983 – January 26, 2011 (6,976 daily observations), also split into three
  sub-periods (1983-03-30 to 1992-06-29; 1992-06-30 to 2001-10-11; 2001-10-12 to 2011-01-26).
- Quality tells: the paper explicitly reports that its headline result is NOT robust across time —
  "splitting the full sample into three sub-periods reveals that this finding is not robust to time
  and is largely explained by the most recent (and most volatile) period" — a strong, self-reported
  robustness caveat (positive quality tell, and a substantive caution for the lead against taking
  the full-sample number at face value).
- Verified passages:
  - P-K4-013-a (Section 4, Concluding discussion): "Using the full sample we find a remarkable
    success of the of ORB strategies. However, splitting up the full sample into three sub-periods
    reveals that this finding is not robust to time and to a large extent explained by the most
    recent (and most volatile) period."
  - P-K4-013-b (Table 2, full sample, 1% tail threshold, long side): N = 188 trades, success
    frequency 0.6117, average return 0.2583 (i.e., ~25.8 basis points per trade by the paper's own
    return definition), p = 0.0001.
  - P-K4-013-c (Concluding discussion, transaction cost note): "transaction costs in terms of
    commission fees and bid-ask spreads will consume some of the profits. However, for the market
    under consideration these are relatively small. A reasonable estimate is 0.04%, or 0.08% round
    trip."
- Numeric claims: full-sample 1%-threshold long-side success rate 61.17%, mean return 0.2583 (units
  as defined in the paper — a log-return-scaled figure, not directly a % return without checking
  the paper's exact scaling) — verified against text (P-K4-013-b); round-trip cost estimate 0.08%
  (P-K4-013-c) — verified.
- Tags: port of D.1 family B (reference-level breakout), the opening-range-breakout member,
  directly matching the additional named seed "intraday or opening-range studies on crude oil
  futures." Intraday-feasible: yes — same-day entry and exit, no overnight hold, no dependence on
  queue position; the sub-period non-robustness (P-K4-013-a) is the key finding the lead needs
  before treating this as evidence of a durable edge.

### K4-014
- Citation: Ewald, C.O., Haugom, E., Ouyang, R., Smith-Meyer, E., Størdal, S. (2024). "Intra-day
  Seasonality and Abnormal Returns in the Brent Crude Oil Futures Market." SSRN working paper
  5037563 (published Quantitative Finance, 25(11), 2025).
- Retrieval: full text of the abstract, verbatim, via SSRN listing page (body of the paper not
  retrieved — the working paper itself would require a further PDF fetch not completed this
  session).
- Mechanism: Statistically significant intraday seasonal patterns (peaks and troughs at particular
  clock times, varying by contract maturity and whether calendar spreads are used) exist in Brent
  crude oil futures; the authors construct long-short strategies that trade at particular times of
  day to exploit this seasonality and find the strategies produce positive, significant CAPM alphas
  net of realistic transaction costs and margin requirements.
- Products and horizon: Brent crude oil futures, ICE (not CME) — this is the "market close enough
  in microstructure that the mechanism plausibly transfers" case under the partition's pre-filter
  rule, since Brent and WTI (CL) are the two dominant global crude benchmarks; the finding is
  intraday, session-clock-based, various maturities.
- Cost assumptions: "even when accounting for realistic transaction costs and margin requirements,
  some of the proposed strategies can create consistent positive and significant CAPM alphas"
  (P-K4-014-a) — specific cost figures not given in the abstract.
- Data window: tick data, January 2010 – October 2021 ("130 Gigabytes of oil transactions"),
  aggregated to one-minute bars.
- Quality tells: very large tick-level dataset explicitly described; cannot assess data-snooping
  controls or exact seasonality windows without the full paper.
- Verified passages:
  - P-K4-014-a (Abstract, verbatim): "Our data cover tick data for futures of various maturities
    from January 2010 to October 2021, a database covering 130 Gigabytes of oil transactions. We
    convert these data into one-minute data and observe statistically significant intra-day
    seasonal patterns with peaks and bottoms at particular times of the day... even when accounting
    for realistic transaction costs and margin requirements, some of the proposed strategies can
    create consistent positive and significant CAPM alphas."
- Numeric claims: no specific percentage/Sharpe given in the abstract; qualitative "consistent
  positive and significant" only — logged as such, not [unverified] since it is a direct quote, but
  not a quantified figure either.
- Tags: port of D.1 family A (session clock) — this is the direct crude-oil-specific test of a
  session-clock mechanism the partition brief calls for (though on Brent/ICE, transferability to
  CME WTI is a claim for the lead to weigh, not concluded here). Intraday-feasible: yes by
  construction (the strategies trade at particular times of day and, per the abstract, the data and
  strategy design is entirely intraday).

### K4-015
- Citation (source paper cited by the Quantpedia strategy page): Evans, T., Dunis, C., Laws, J.
  "Trading Futures Spread: An Application of Correlation and Threshold Filters." Journal of
  Derivatives & Hedge Funds, 15(4). Quantpedia strategy page: "Trading WTI/BRENT Spread"
  (quantpedia.com/strategies/trading-wti-brent-spread), reporting an ARMA-model WTI-Brent spread
  strategy with reported out-of-sample annualized returns of 34.94% (inclusive of transaction
  costs) per the source paper's own abstract as quoted on the Quantpedia page.
- Retrieval: full text of the Quantpedia strategy page (secondary source summarizing the primary
  paper) plus the primary paper's own abstract as block-quoted on that page; the primary paper
  itself was not independently fetched.
- Mechanism: The WTI-Brent price spread is mean-reverting (both crudes are chemically and
  operationally similar but differ enough in cracking yield and logistics that temporary price
  shocks to the spread revert); a simple 20-day moving-average threshold rule (short the spread
  when above its 20-day MA, long when below, close on reversion) is presented as the example
  strategy; the cited source paper's own best model is an ARMA-based fair-value approach.
- Products and horizon: WTI crude oil futures (long or short leg) vs Brent crude oil futures
  (ICE, non-CME, the other leg) — WTI is CL, the CME/K4 product; Brent is a non-CME signal/hedge
  instrument, consistent with partition section 1's treatment of non-CME instruments as belonging
  to the CME product's cluster. Horizon as tested on Quantpedia's own backtest is DAILY rebalancing
  (enter/exit at daily close), not intraday.
- Cost assumptions: Quantpedia's own backtest code and disclosed statistics account for transaction
  costs implicitly via a small per-trade fee model in the QuantConnect implementation; the source
  paper's headline figure (34.94% annualized, out-of-sample) is stated as "inclusive of transaction
  costs."
- Data window: source paper period 1995–2004 (per Quantpedia's summary table); Quantpedia's own
  out-of-sample QuantConnect backtest reports separately (negative Sharpe out of sample per
  Quantpedia's own live-updated statistics box, distinct from the source paper's figure).
- Quality tells: Quantpedia's page itself flags "OOS back-test shows slightly negative performance.
  It looks that strategy's alpha is deteriorating in the out-of-sample period" — i.e., the
  secondary aggregator explicitly disclaims the strategy's current-day performance even while citing
  a strong historical academic result; a related paper listed on the same Quantpedia page
  ("Donninger: The Poverty of Academic Finance Research") is itself an adversarial critique of a
  similar WTI-Brent spread paper (Lubnau) for using "the wrong data" — a explicit source-quality
  warning embedded in the discovery layer itself.
- Verified passages:
  - P-K4-015-a (Quantpedia page, "Confidence in Anomaly's Validity" note, verbatim): "OOS back-test
    shows slightly negative performance. It looks, that strategy's alpha is deteriorating in the
    out-of-sample period."
  - P-K4-015-b (Quantpedia page, quoting the source paper's own abstract, verbatim): "Our results
    show that the best model for trading the WTI-Brent spread is an ARMA model, which proved to be
    profitable, both in- and out-of-sample. This is shown by out-of-sample annualised returns of
    34.94% for the standard and correlation filters alike (inclusive of transactions costs)."
  - P-K4-015-c (Quantpedia page, adversarial cross-reference, verbatim): "This paper analyzes a less
    prominent example about spread trading in the crude oil futures market by Thorben Lubnau. The
    author reports for his very simple strategy a long term Sharpe-Ratios above 3. It is shown that
    ...one needs no sophisticated test statistics to falsify the results. The explanation is much
    simpler: The author has no clue of trading. He used the wrong data."
- Numeric claims: 34.94% annualized OOS return (P-K4-015-b) — this is a secondary-source quote of a
  primary paper's own claim, not independently checked against the primary paper itself; treat as
  [unverified against primary source] even though verbatim-quoted from the aggregator. Quantpedia's
  own backtest: Sharpe −0.5, CAGR −5.53% (its own reported statistics box) — this is Quantpedia's
  own more recent out-of-sample figure, directly contradicting the 34.94% claim; both are logged so
  the lead sees the discrepancy.
- Tags: port of D.1 family C (short-horizon reversal/momentum) — the spread mean-reversion
  mechanism. Intraday-feasible: no as tested — daily rebalancing (enter/exit at close), explicit
  multi-day-to-open-position character; would need redesign to an intraday version to satisfy the
  flat-by-15:08-CT rule, which the source material does not itself attempt.

### K4-016
- Citation: Dujava, C. (2024). "Pre-Holiday Effect in Commodities." Quantpedia (own-research blog
  post, October 14, 2024).
- Retrieval: full text (quantpedia.com/pre-holiday-effect-in-commodities/, own-research blog post,
  not a peer-reviewed paper).
- Mechanism: Crude oil and gasoline (proxied by the USO and UGA ETFs, not CME futures directly)
  exhibit a short-term price drift in the days immediately preceding major U.S. holidays,
  hypothesized to be driven by anticipatory demand for holiday travel fuel; the tested rule buys on
  the close five trading days before the holiday (D-5) and sells on the close of the last trading
  day before the holiday (D-1), holding for three full days (D-4, D-3, D-2) with no adjustment.
- Products and horizon: USO (crude oil ETF, proxy for CL) and UGA (gasoline ETF, proxy for RB);
  explicitly a MULTI-DAY hold (D-5 through D-1, i.e., roughly 4 trading days held), not intraday.
- Cost assumptions: none disclosed (uses Yahoo Finance/EODHD adjusted-close daily data; no
  transaction-cost modeling described).
- Data window: USO since inception 2006-04-10; UGA since inception 2008-02-26; both through
  2024-08-30.
- Quality tells: Quantpedia's own "own-research" tag (not third-party peer review); uses ETF proxies
  rather than futures directly and explicitly declines to test the futures contract itself ("margin
  requirements and direct market availability for exchange access for retail and non-professionals
  are limited, so we omit this option from the direct analysis") — i.e., the authors themselves
  chose not to test the CME product, only a retail-accessible ETF wrapper; this is a real limitation
  for K4's purposes, since XFA trades the futures contract, not the ETF.
- Verified passages:
  - P-K4-016-a (Hypothesis section, verbatim): "The increased demand for crude oil before the U.S.
    holidays causes a short-term price drift."
  - P-K4-016-b (Data section, verbatim): "We have an educated guess that in lack of transaction
    costs, the strategy would perform similarly with front continuous contract Light Sweet Crude
    Oil Futures CL1 traded at NYMEX. However, margin requirements and direct market availability for
    exchange access for retail and non-professionals are limited, so we omit this option from the
    direct analysis."
  - P-K4-016-c (Results, verbatim): "We can see that the D-4 to D-1 period is the most profitable
    for holding a long position in the market. Thus, it would be optimal to establish a position
    four days before the Holiday and sell at the close of the day, just before the market closes."
- Numeric claims: none given as a single headline percentage/Sharpe in the retrieved text beyond
  chart/table images not extracted as text; treat any specific return figure as [unverified] since
  the figures appear only as embedded chart images in the scraped markdown, not as text.
- Tags: port of D.1 family E (calendar and events), specifically a pre-holiday calendar effect.
  Intraday-feasible: NO, explicitly — the strategy as tested holds a position for four trading days
  (D-5 close to D-1 close), which requires holding overnight multiple times; this violates the
  program's flat-by-15:08-CT rule (rule 8) as designed. Logging as intraday-infeasible with this
  reason; an intraday-only reformulation (e.g., trade only the day-of reaction) is not what this
  source tested.

### K4-017 / K4-018 (documentation sources, not findings)
- Citation: U.S. Energy Information Administration, "Weekly Petroleum Status Report" landing/
  schedule page (eia.gov/petroleum/supply/weekly/) and "Weekly Natural Gas Storage Report Schedule"
  (ir.eia.gov/ngs/schedule.html).
- Retrieval: full text (official EIA pages).
- Content: confirms the release-time facts assumed by every announcement-response paper above.
  Verified passage P-K4-017-a: "Released after 10:30 a.m." (WPSR). Verified passage P-K4-018-a
  (WebSearch summary of the schedule page, cross-checked, treat as [unverified — paraphrase] for the
  exact wording, but the specific fact — Thursday 10:30 a.m. ET, moved to Friday on a Thursday
  federal holiday — is standard, widely corroborated EIA practice): "the standard release time and
  day of the week will be at 10:30 a.m. eastern time on Thursdays, with exceptions for federal
  holidays."
- These are not independent "findings" and carry no numeric or trading claim of their own; they
  exist in this log solely to let the lead verify the announcement-timing facts assumed above
  without re-deriving them, and because the source registry (rule 1) treats them as claimed sources
  like any other fetched URL.

### K4-019
- Citation: Cummins, M., Bucca, A. (2012). "Quantitative spread trading on crude oil and refined
  products markets." Quantitative Finance, 12(12), 1857–1875. DOI 10.1080/14697688.2012.715749.
- Retrieval: abstract only (WebSearch summary of the publisher/RePEc abstract; not independently
  re-fetched verbatim this session — treat as [unverified — paraphrase], though the specific numbers
  below appeared consistently across the search snippet).
- Mechanism: A statistical-arbitrage model applied to 861 spreads among WTI, Brent, heating oil, and
  gas oil (2003–2010), using generalized stepwise procedures to control for data-snooping bias,
  aggregating upward and downward mean reversion.
- Products and horizon: crude oil and refined products spreads (WTI, Brent, heating oil, gas oil —
  HO is a CME/K4 product, WTI is CL, Brent and gas oil are non-CME/ICE instruments used as
  spread legs); horizon is explicitly MULTI-DAY, not intraday.
- Cost assumptions: "robustness to varying transaction costs is examined" per the summary; specific
  cost figures not retrieved.
- Data window: 2003–2010.
- Quality tells: explicit data-snooping-bias control (generalized stepwise procedure) is a positive
  methodological tell; cannot assess further without the full text.
- Verified passages: none verbatim (paraphrase only): "average daily returns range from 0.07 to
  0.55%, with trade lengths of 9-55 days... Sharpe ratios greater than 2 in many instances. A
  collapse in the number of profitable trading strategies is seen in 2008." [unverified — paraphrase]
- Numeric claims: trade length 9–55 days (P-K4-019, unverified) — this alone establishes the
  mechanism is NOT intraday as tested, regardless of the Sharpe-ratio figure's precision.
- Tags: port of D.1 family C (reversal) at the multi-day horizon. Intraday-feasible: NO, explicitly
  — trade lengths of 9 to 55 days require holding overnight for over a week in the shortest case,
  violating rule 8. Logged for completeness of the crack-spread/refined-products literature K4 owns,
  not as a candidate.

### K4-020
- Citation: [authors not resolved from the retrieved abstract] (2020). "Systemic Risk in Market
  Microstructure of Crude Oil and Gasoline Futures Prices: A Hawkes Flocking Model Approach."
  arXiv:2012.04181.
- Retrieval: abstract only (WebFetch summary of the arXiv abstract page).
- Mechanism: A "Hawkes flocking model" measures systemic risk in high-frequency trading in WTI
  crude oil and gasoline futures from two angles (endogeneity — self-exciting risk within one
  market — and interactivity — cross-market risk transmission), benchmarked against conditional
  value-at-risk; finds endogenous systemic risk in WTI is significantly higher than in gasoline,
  and gasoline's influence on WTI consistently exceeds the reverse, though the asymmetry has
  narrowed over the sample.
- Products and horizon: WTI crude oil and gasoline (RB) futures; the sample covers roughly a decade
  of high-frequency data ("over a decade" per the abstract summary); this is a risk-measurement
  study, not a directional signal or event study, so there is no "horizon" for a trade in the usual
  sense.
- Cost assumptions, data window (exact dates): not established from the abstract summary alone.
- Quality tells: cannot assess methodology depth without the full text; note this paper measures
  systemic/tail risk co-movement, not a predictable return, so even with full text it likely does
  not yield a directly tradeable rule.
- Verified passages: none verbatim (WebFetch tool paraphrase only, not a direct quote):
  "endogenous systemic risk in WTI was significantly higher than that in gasoline, while gasoline's
  influence on WTI consistently exceeded the reverse relationship" [unverified — paraphrase].
- Numeric claims: [unverified] — none logged with specific figures.
- Tags: not clearly a D.1-family port (this is closest to family D, volatility/risk state, but
  measured as a systemic-risk index rather than a realized-volatility regime signal); new
  contribution if pursued further. Intraday-feasible: cannot assess — this is a risk-measurement
  paper, not a trading rule; logging as informational context rather than a candidate mechanism.

## 4. Flags for K8 (cross-cluster; no full-text reads performed)

- Quantpedia | "Crude Oil Predicts Equity Returns" strategy page | legs: crude oil (WTI/USO) →
  equity index returns | crude-oil price level used as a market-timing signal for equity exposure
- Alquist, R., Ellwanger, R., Jin, J. (2020), JFM, "The effect of oil price shocks on asset markets:
  Evidence from oil inventory news" | legs: oil inventory announcement (K4) → US equity, Treasury-
  futures (K2), and FX (K3) returns | oil-inventory-news-identified shocks used as an instrument to
  quantify cross-asset (equity/bond/FX) reactions, registered as K4-008
- Alturki, S., Kurov, A. (2022), JFM, "Market Inefficiencies Surrounding Energy Announcements" |
  legs: crude oil futures (K4) and the stock market (K1) | the paper's informational-efficiency
  claim explicitly spans both crude oil futures and equities in one design (registered as K4-009;
  the crude-oil-only mechanism is logged in section 3, the equity leg is flagged here)

## 5. Registry ids appended

K4-001 through K4-020 (20 lines total), all appended to
reports/stage_e0_source_registry.jsonl with worker "K4" and claimed_pdt timestamps 2026-09-23
20:20–20:28. No pre-existing K4 lines were found in the registry at the start of this session (file
did not exist before this run).
