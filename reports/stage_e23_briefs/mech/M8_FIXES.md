# Stage E.23 P1.2 mechanism memo: M8_FIXES (FX and gold fixing flows)

Worker: MechanismReaderM8_FIXES-OpusHigh. Written 2026-10-17, 02:16 to about 02:30 PDT (-07:00). Brief:
reports/stage_e23_briefs/brief_mechanism.md. Pages and logs: reports/stage_e23_briefs/mech_pages/M8_FIXES/
(fetch_log.md, query_log.md). Full texts that E.20 had already saved were reused in place, not refetched. Their
sha256 values were checked again at 02:23 PDT and match the E.20 fetch logs.

The question for every member: does the published literature give a reason why the trigger-day event predicts the
instrument's return over the 5 or 20 trading days after the trigger day's settlement, and in which direction? Bottom
line: every paper in this family measures effects in minutes or hours. The only within-family evidence that goes past
the fix day reaches noon of the next London day (Melvin and Prins). No paper found tests 5 or 20 trading days after
any fixing event. Two FX flow papers (Froot and Ramadorai; Camanho, Hau and Rey) give an analog multi-day mechanism,
and it applies only to the month-end member.

## 1. Evidence table

Paths are relative to the repo root. Text was read by grep and line range from the `.txt` conversion that sits next
to each saved file. Page numbers are the printed page numbers of the saved version.

| Key | Full citation | URL | Saved path | sha256 (saved original) | Verbatim quote (page or section) | Claim supported: horizon / direction / magnitude / sample / instrument |
|---|---|---|---|---|---|---|
| KMW2024 | Krohn, I., Mueller, P., Whelan, P., "Foreign Exchange Fixings and Returns Around the Clock", Journal of Finance (2024); author's accepted manuscript, WRAP 177333 (saved copy reads "Journal of Finance forthcoming") | https://wrap.warwick.ac.uk/177333/1/WRAP-foreign-exchange-fixings-returns-around-clock-Mueller-2023.pdf | reports/stage_e20_briefs/pages/6E/krohn_mueller_whelan_2024_jf_wrap.pdf | a7975f26f9b42b837a0b2a6c1474a63e448fff5a0fa7957bc2233b1c0302e6a3 | p.10: "The last column in Table I makes clear that the pattern we document is an intraday seasonality (i.e., a predictable component) that does not carry over to close-to-close returns. In fact, none of the currencies in our sample move by more than 1 bps per day over our sample period and none of the close-to-close returns are statistically significant." p.11: "pre- and post-fix returns are very robust over time and consistent with the notion of a reversal that nets out to zero on average" | Horizon: intraday only. Effect around the fixes nets to zero over the day. Direction: dollar up before the Tokyo and ECB fixes, down after. Magnitude: p.10, yen post-Tokyo-fix reversal "3.0 ... bps per day"; p.10, euro pre-ECB-fix "-3.5 ... basis points per day"; p.10, after the London fix "2.7 bps for the euro", yen "depreciates by 1.2 bps". Sample 1999-2019, G9 spot. p.11: the 2014-2019 Tokyo reversal is "notably smaller but remains statistically significant". |
| KMW2024 (b) | as above | as above | as above | as above | p.9: "the consistent depreciation of foreign currencies before the Tokyo fix and after European markets open combined with the depreciation of the U.S. dollar during the intraday period leads to a distinctive W -shaped pattern of the cumulative returns measured over a full day." | The daily shape is a within-day W. Nothing in it carries across days. |
| MP2013 | Melvin, M., Prins, J., "Equity hedging and exchange rates at the London 4pm Fix", ECB Third FX Workshop version, Nov 2013 (published in Journal of Financial Markets 2015 [published version not fetched]) | https://www.ecb.europa.eu/events/pdf/conferences/131216/Third_FX_Workshop_MELVIN_PRINS_Equity%20hedging%20and%20exchange%20rates%20Nov%202013.pdf | reports/stage_e20_briefs/pages/6E/melvin_prins_2013_ecb_wp.pdf | 606a6c402741982f4f81423f6df3ca055348156fe728d54976807579168d587c | p.16: "the dependent variable is the exchange rate return from 16:00 GMT on day t to noon the next day t+1, and the independent variable is the same return from 15:00 to 16:00 GMT on day t ... plus this same independent variable interacted with a dummy variable equal to 1 on the last day of each month. The sample period is ... 20040428-20121231." Equation (5), p.16: slope -0.339 on all days, -0.387 extra on end-of-month, both p-values (0.00), R2 1.9%. p.17: "on end of month days, the sum of the two coefficients tell us that 72% of the price movement in the hour leading up to the fix has been reversed before noon of the next day." | Horizon: about 20 hours (16:00 London to noon London the next day). Direction: reversal of the pre-fix hour's move, twice as strong at month-end. Magnitude: 72% of the pre-fix-hour move. Pooled currencies, 2004-2012, spot. |
| MP2013 (b) | as above | as above | as above | as above | p.16: "it is reasonable to expect that the price impact of their trades, if there is any, is temporary as those supplying liquidity absorb the trades for a premium and then lay them off over time." p.1 abstract: "Equity market appreciation over the month predicts currency depreci[ation]" (line break in the saved text) | Mechanism: hedging flows carry no information, so their price impact is temporary. Pre-fix size (E.20, product_6E.md E6): 14 bp of currency depreciation per 10% relative equity appreciation, over the 15:00-16:00 London hour. |
| EV2018 | Evans, M.D.D., "Forex Trading and the WMR Fix", Journal of Banking and Finance (forthcoming at MPRA posting), MPRA Paper 81583, 25 Sep 2017 | https://mpra.ub.uni-muenchen.de/81583/1/MPRA_paper_81583.pdf | reports/stage_e20_briefs/pages/6E/evans_2018_jbf_wmrfix_mpra81583.pdf | f34bf1d22e364cf47be579197f395039ffd1f90e577ce2833bb510c69a77898b | p.31: "These patterns imply that all the relevant trade-based information is fully assimilated into prices by the end of the Fix window, so there is no systematic tendency for rates to rise or fall after that. In this sense, it appears that post-Fix equilibrium prices are quickly established on intra-month trading days." p.32: "both positive and negative pre-Fix price changes are followed by a sizable reversal in prices in the first few minutes" | Horizon: minutes. Direction: no drift after the fix on days within the month. At month-end, a reversal over the first few minutes. Sample 2004-2013 (p.7: "My empirical analysis covers forex trading from the start of 2004 until the end of 2013"), 21 currency pairs. |
| MPP2017 | Marsh, I.W., Panagiotou, P., Payne, R., "The WMR Fix and its Impact on Currency Markets", draft dated 29 Sep 2017 (Norges Bank-hosted) | https://www.norges-bank.no/contentassets/619c8b75e1ed4ba691e8ad6a006855e6/39-panagiotou---the-wmr-fix-and-its-impact-on-currency-markets-.pdf | reports/stage_e23_briefs/mech_pages/M8_FIXES/marsh_panagiotou_payne_norgesbank.pdf | ff31920e9a7b5af885c6ef2c83a2b64c617437e1c348d9d2b0c97fd8ae2f0282 | p.3: "There is a small price reversal in the one minute after the 4pm Fix for both markets that is not observed at other fixing points." p.3: "Positions accumulated in the futures market during the pre-Fix are also reversed, though over a significantly longer time interval than in the spot market" | Horizon: minutes, somewhat longer in futures. Direction: reversal. Spot and futures, "four years of high-frequency data" (abstract). |
| IY2017 | Ito, T., Yamada, M., "Puzzles in the Forex Tokyo 'Fixing': Order Imbalances and Biased Pricing by Banks", NBER WP 22820 (2016); Journal of International Economics 109 (2017) 214-234 per RePEc record [published version not fetched] | https://www.nber.org/system/files/working_papers/w22820/w22820.pdf | reports/stage_e23_briefs/mech_pages/M8_FIXES/ito_yamada_2016_nber_w22820.pdf | 5e86cba5b82f18d2881e5a6cabf7bb4a85be007dcb6f59e7b191e59b70d6cdb2 | p.4: "Because these peculiar order imbalances reflect nothing more than the temporal imbalances of demand/supply of currency, the appreciated price reverses after the fixing time." p.17: "The transactions and price movements at the time of the fixing window is less likely to induce a permanent change in the foreign exchange rate, unlike a macroeconomic announcement. Prices and volumes during the fixing window only represents the temporary imbalance of liquidity." | Horizon: intraday, around 9:55 Tokyo. Direction: USD/JPY up into the fix, reversal after it. Mechanism stronger on the 5th and 10th days (gotobi) and month-end (p.10). Sample: p.22, "January 5, 2006 to December 31, 2013". |
| BSS2023 | Bessho, H., Sugimoto, T., Suzuki, T., "Forex Trading Strategy That Might Be Executed Due to the Popularity of Gotobi Anomaly", arXiv:2301.13204v1 (29 Jan 2023), preprint | https://arxiv.org/pdf/2301.13204 | reports/stage_e23_briefs/mech_pages/M8_FIXES/bessho_etal_2023_arxiv2301.13204.pdf | 07be82468c1c6d175ee5ca77264c8fa4bf632f2bb0f3f98a395c32e019ceb113 | Section 2: "the USD/JPY rate is suddenly decreased just after 9:55 a.m. that is the decision and announcement time of TTM." "Hypothesis 2 The mispricing caused by the Gotobi anomaly is immediately corrected" | Horizon: minutes after 9:55 JST. Direction: on gotobi days, USD/JPY up into the fix and down right after it. Sample 2018-2020 (Section 1), EBS USD/JPY. Not peer reviewed. |
| FR2005 | Froot, K.A., Ramadorai, T., "Currency Returns, Intrinsic Value, and Institutional-Investor Flows", Journal of Finance 60(3), June 2005, 1535-1566 | https://www.johnhcochrane.com/s/froot_currency_jf.pdf | reports/stage_e23_briefs/mech_pages/M8_FIXES/froot_ramadorai_2005_jf.pdf | aecb39721ab66b040fd4788038bed4f36621a22ea512852250a4e7fa052dfc76 | p.1539: "In our data, flow surprises positively forecast excess returns over relatively short horizons (up to 30 trading days). However, flow surprises negatively forecast excess returns at longer horizons (i.e., between 30 trading days and an infinite horizon). This too suggests momentum and reversal" | Analog only: institutional-investor (State Street custodial) currency flows, not fixing flows. Horizon: up to 30 trading days, which covers both 5 and 20. Direction: continuation in the flow's direction. Sample: "June 20, 1994 to February 9, 2001" (p.1545). No per-event bp figure is given in the passage read. |
| CHR2022 | Camanho, N., Hau, H., Rey, H., "Global Portfolio Rebalancing and Exchange Rates", NBER WP 24320 (Feb 2018, revised Dec 2020); Review of Financial Studies 35(11) 2022 per search result [published version not fetched] | https://www.nber.org/system/files/working_papers/w24320/revisions/w24320.rev1.pdf | reports/stage_e23_briefs/mech_pages/M8_FIXES/camanho_hau_rey_nber_w24320_rev1.pdf | 7a7f011f2ccc6efc1f09c1c70ce19be3540a73a45162074db56eb6aee4890f0a | p.5: "net portfolio equity flows in response to differential equity returns are associated with an appreciation (a depreciation) of the domestic currency for net inflows (net outflows)." p.25: "captures delayed portfolio reallocations with a time lag of l quarters." p.19 fn: "Our study focuses on a different time scale (quarterly instead of daily)" | Analog only. Horizon: quarters, neither 5 nor 20 days. Direction: rebalancing after foreign equity outperformance sells the foreign currency, with lags of one to two quarters, so continuation in the rebalancing direction. Sample 1999-2015 (p.4), fund holdings. |
| CH2014 | Caminschi, A., Heaney, R., "Fixing a Leaky Fixing: Short-term market reactions to the London PM gold price fixing", Journal of Futures Markets 34(11), 2014 (UWA accepted manuscript) | https://api.research-repository.uwa.edu.au/ws/files/4725264/A0205_use_this.pdf | reports/stage_e20_briefs/pages/GC/caminschi_heaney_2014_uwa_aam.pdf | 76ff3e190c179ff3eb80105ddeeeca6c8b8ebf605a5eb83387e17c5471218556 | Abstract: "we find statistically significant return advantages in the four minutes following the start of the fixing for informed traders. We find no significant impacts or returns following the publication of the fixing results." Results section: elevated volumes "persist for thirteen minutes for GC" | Horizon: 4 to 13 minutes. Direction: continuation within minutes of the fixing's start, nothing after publication. Sample 2007-2012, GC and GLD, from before the 2015 auction. |
| AFGO2017 | Aspris, A., Foley, S., Gratton, F., O'Neill, P., "Transparency in Commodities Markets", EFMA 2017 Athens paper 0580 | http://efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2017-Athens/papers/EFMA2017_0580_fullpaper.pdf | reports/stage_e20_briefs/pages/GC/aspris_etal_2017_efma.pdf | 81c77b19eac1a4c4c89f421f3e0e0933af6f134bfd926ca8549db2d69934db1f | Abstract: "We observe a decline in the length of time required to reach the final benchmark price, and also show a reduction in the adjusted returns, volatility, and return predictability of the associated futures contract." | Decay: after the electronic LBMA auctions replaced the fix in 2015, the futures' return predictability around the benchmark fell. Intraday only. |
| BGK2018 | Blose, L.E., Gondhalekar, V., Kort, ?, "Overnight and day returns in gold" (title per RePEc record), Journal of Economics and Finance 42(3), 2018 | https://ideas.repec.org/a/spr/jecfin/v42y2018i3d10.1007_s12197-017-9403-0.html | reports/stage_e20_briefs/pages/GC/repec_blose_etal_2018.html | 7300985d5df69900f0cce7dc0816b7566c6daa0175b7b2dd60a9ec90166e5781 | ABSTRACT ONLY: "Overnight returns are significantly positive while day returns are significantly negative in the COMEX gold front futures contract, the gold spot market (London Fix) ... The findings are consistent with gold price being (too) high at the opening of the various markets." | Horizon: the day versus overnight split within each 24 hours. Direction: gold falls in the day session and rises overnight. Says nothing about 5 to 20 days. Abstract only: the title and the third author's first name were not verified. |

## 2. Member paragraphs

### K3-ldnrev-01 (6E, 6J, 6S): month-end London 4 p.m. fix, contrarian to the 10-minute pre-fix move
- Strength: weak.
- Direction: the literature disagrees, and no study measures 5 to 20 days after this event. Hedging-flow papers
  (MP2013, EV2018, MPP2017) predict reversal of the pre-fix move, which is the member's own side, but within minutes to
  about 20 hours. Flow and rebalancing papers (FR2005, CHR2022), used as analogs, predict continuation of the
  flow-driven move (opposite the member's side) over up to 30 trading days or over quarters.
- Horizon: neither 5 nor 20 directly. FR2005 (up to 30 trading days) is the only analog that covers both. MP2013
  stops at noon on day t+1.
- Magnitude: no published per-event figure for 5 or 20 days. Within the day, MP2013 reports 72% of the pre-fix hour's
  move reversed by noon the next day on month-end days (2004-2012, pooled spot, p-values 0.00). The pre-fix hour itself
  moves about 14 bp per 10% of relative month-to-date equity return (MP2013; E.20 product_6E.md, row E6). After the
  2015 change of the WMR fix window to five minutes, no sized study of the reversal was found (E.20 product_6E.md
  notes the same gap).
- Reason: month-end equity-hedge rebalancing by global portfolio managers runs through the 4 p.m. fix. The pre-fix
  move partly reflects that flow. Its price impact is temporary because liquidity suppliers "absorb the trades for a
  premium and then lay them off over time" (MP2013 p.16), and most of it is gone before noon the next day (MP2013
  p.17). EV2018 (p.32) and MPP2017 (p.3) place the month-end reversal in the first minutes after the fix. An entry at
  the trigger day's settlement comes hours after the fix, so most of the documented reversal has already happened. Only
  the part that falls between settlement and noon London of day t+1 can land inside the hold, and no paper sizes that
  part. Against this, FR2005 (p.1539) finds that currency flow surprises forecast returns in the flow's direction for up
  to 30 trading days, and CHR2022 (pp.5, 25) finds that equity-return-driven rebalancing moves currencies with lags of
  one to two quarters. These are analogs (custodial flows, quarterly fund holdings), not fixing events. A 10-minute
  pre-fix move is a noisy proxy for either flow. This member is the only one in the family with any multi-day analog.

### K3-ldnmom-01 (6E, 6J): daily front-running into the London 4 p.m. fix (3-minute trend at 15:45-15:47 London)
- Strength: none (intraday-only).
- Direction: none predicted.
- Horizon: neither.
- Magnitude: none past the fix. KMW2024 (p.10) finds close-to-close returns of at most 1 bp per day, none of them
  significant (1999-2019).
- Reason: the only mechanism is order-flow pressure in the minutes before the fix, which is spent at the fix. EV2018
  (p.31): on days within the month, "all the relevant trade-based information is fully assimilated into prices by the
  end of the Fix window, so there is no systematic tendency for rates to rise or fall after that". KMW2024 (p.10)
  finds that the fix seasonality "does not carry over to close-to-close returns". No source links a 3-minute pre-fix
  trend to returns over the following 5 to 20 days. Drop as intraday-only.

### K3-ecbfix-01 (6E): dollar strength into the ECB fix (short EUR 01:00 to 07:15 CT), dollar weakness after it (long EUR to 15:05 CT)
- Strength: none (intraday-only).
- Direction: none predicted, either for the leg-1 side (short 6E) or for the leg-2 side (long 6E).
- Horizon: neither.
- Magnitude: within the day, KMW2024 (p.10) puts the euro's pre-ECB-fix move at -3.5 bp per day (1999-2019). The
  pattern is a reversal that "nets out to zero on average" (p.11), and close-to-close returns are not significant
  (p.10).
- Reason: this is a within-day seasonality caused by fix-related dollar demand and dealer intermediation, with
  opposite signs on the two sides of the fix. KMW2024 states that it does not carry into daily returns. No source
  connects the ECB fix to the following 5 to 20 days. The member also has two opposite legs, so it has no single
  trigger-day side to extend. Drop as intraday-only.

### K3-tkypre-01 (6J): gotobi and Tokyo month-end days, short 6J (long USD) into the Tokyo 9:55 fix
- Strength: none (intraday-only).
- Direction: none predicted for 5 to 20 days. The documented after-effect is an immediate reversal, which is the
  opposite side (6J up), but it lasts minutes to hours and ends before the trade date's settlement entry.
- Horizon: neither.
- Magnitude: within the day, the yen's post-Tokyo-fix reversal is 3.0 bp per day (KMW2024 p.10, 1999-2019, all days,
  not gotobi only). For 2014-2019 the Tokyo reversal is "notably smaller but remains statistically significant"
  (KMW2024 p.11). No multi-day figure.
- Reason: Japanese importers settle in dollars at the Tokyo TTM fix, concentrated on the 5th, 10th, ... days and at
  month-end. Banks pre-hedge, and USD/JPY rises into 9:55 JST. IY2017 (pp.4, 17) describes these as "temporal
  imbalances", "less likely to induce a permanent change", that reverse after the fix. BSS2023 (Section 2) finds the
  mispricing "immediately corrected" just after 9:55 (2018-2020). The Tokyo fix falls on the evening of calendar day
  d-1 in CT, so by the settlement entry on trade date d the event and its reversal are many hours old. No source finds
  a multi-day yen effect from gotobi demand. Drop as intraday-only.

### K3-tkypost-01 (6J): long 6J (dollar weakness) after the Tokyo 9:55 fix, every Tokyo business day
- Strength: none (intraday-only).
- Direction: none predicted.
- Horizon: neither.
- Magnitude: within the day, 3.0 bp per day for the yen after the Tokyo fix (KMW2024 p.10). Close-to-close returns are
  not significant (KMW2024 p.10).
- Reason: this member trades the second half of the same temporary imbalance as K3-tkypre (IY2017 p.4; KMW2024
  pp.9-11). The post-fix reversal unwinds the pre-fix dollar demand within the Asian session, and the two halves "net
  out to zero on average". Nothing carries past the day. It also fires on almost every trade date, so a 5- or 20-day
  hold from each event day amounts to an almost always long 6J position, and no fix mechanism supports that. Drop as
  intraday-only.

### K5-pmfix-01 (MGC): gold PM auction, continuation of the move from T_P - 1 to T_P + 1 (the first minutes of the auction)
- Strength: none (intraday-only).
- Direction: none predicted for 5 to 20 days. The published continuation lasts 4 minutes.
- Horizon: neither.
- Magnitude: no multi-day figure. CH2014 (2007-2012, GC): return advantages "in the four minutes following the start
  of the fixing" and "no significant impacts or returns following the publication of the fixing results".
- Reason: the mechanism is information leakage from the auction's order flow into futures during the auction itself
  (CH2014 abstract). After the 2015 move to the electronic LBMA auction, the futures' return predictability around the
  benchmark fell (AFGO2017 abstract), so even the intraday effect has decayed. No source finds that the sign of the
  first auction minutes predicts gold over the following days. Drop as intraday-only.

### K5-preauc-01 (MGC): short gold into the AM auction (04:00 to 04:29 CT), unconditional
- Strength: none (intraday-only).
- Direction: none predicted for 5 to 20 days. BGK2018 (abstract only) finds negative day-session and positive overnight
  gold returns, a split within each 24 hours that does not point either way over several days.
- Horizon: neither.
- Magnitude: none published for 5 or 20 days. BGK2018 gives no figure in its abstract.
- Reason: a short into the AM auction trades the pre-auction part of a day/night return pattern (BGK2018, abstract
  only: "consistent with gold price being (too) high at the opening of the various markets"). A 5- or 20-day hold
  spans many nights and days, and BGK2018 reports positive overnight returns that offset the daytime ones, so the
  pattern gives no reason for a multi-day short. The member fires on every auction day, so the multi-day version would
  be an almost always short gold position. No fix mechanism supports that. Drop as intraday-only.

## 3. Query log

The same log, with the same text, is at reports/stage_e23_briefs/mech_pages/M8_FIXES/query_log.md. Each time is the
interval between the logged clock readings that bracket the call. 10 WebSearch calls in total (budget 60). Before
searching, the worker grepped the saved repo pages: reports/stage_e20_briefs/pages/6E and GC (product_6E.md and
product_GC.md), reports/stage_e2*_briefs, reports/stage_e13_briefs/pages and docs/.

| Time (PDT, -07:00) | Tool | Query | Results kept |
|---|---|---|---|
| 02:16:35-02:18:28 | grep (local) | WM/Reuters, london fix, 4pm fix, Melvin, gold fix, LBMA, Tokyo fix, gotobi, ECB fix over the saved briefs and docs | KMW2024, MP2013, EV2018, CH2014, AFGO2017, BGK2018 (abstract) reused from E.20 |
| 02:18:28-02:18:48 | WebSearch | gotobi anomaly yen Tokyo fixing daily returns USD/JPY paper | BSS2023 |
| 02:18:28-02:18:48 | WebSearch | month-end currency returns rebalancing dollar turn of the month exchange rate days after fix | none (bank flow notes and news) |
| 02:18:48-02:19:12 | WebSearch | Ito Yamada "Puzzles in the Tokyo fixing in the forex market" order imbalances biased pricing | IY2017 |
| 02:18:48-02:19:12 | WebSearch | turn-of-the-month effect foreign exchange returns US dollar academic paper | none fetched (Kumar 2015 on INR pairs and Villarreal-Samaniego 2024, abstracts only, paywalled) |
| 02:19:12-02:19:50 | WebSearch | LBMA gold auction AM PM fix returns subsequent days gold price anomaly London fix overnight return | BGK2018 (abstract already saved) |
| 02:19:12-02:19:50 | WebSearch | Camanho Hau Rey global portfolio rebalancing and exchange rates equity returns currency depreciation monthly | CHR2022 |
| 02:20:00-02:20:50 | WebSearch | Froot Ramadorai currency returns intrinsic value institutional investor flows transitory persistent horizon | FR2005 |
| 02:20:00-02:20:50 | WebSearch | Evans O'Neill Rime Saakvitne "Fixing the fix" WMR five-minute window price impact | MPP2017 |
| 02:20:52-02:21:43 | WebSearch | London gold fixing price discovery returns "next day" OR "following days" gold futures after fix study Lucey | none new |
| 02:20:52-02:21:43 | WebSearch | intraday dollar seasonality FX fixing "close-to-close" returns not predictable multi-day reversal currency fix flows | none new |
| 02:21:43-02:23:11 | WebSearch | gotobi days yen depreciation daily exchange rate effect Japanese importers settlement 5th 10th day of month study | none new |
| 02:21:43-02:23:11 | WebSearch | gold futures overnight positive daytime negative returns Blose Gondhalekar Kort London fix pattern | none new |

Stopping rule: (a) all seven members have paragraphs. (b) 12 distinct queries, the last four adding no new relevant
source. (c) The key papers (KMW2024, MP2013, EV2018, IY2017, CH2014) were read in full text by grep and line range.

## 4. Not verified or not reached
- No study measures returns 5 to 20 trading days after any FX or gold fixing event. This is a search result, not a
  finding that no such effect exists.
- MP2013, IY2017 and CHR2022: the published journal versions were not fetched. The quotes come from the saved
  workshop or working-paper versions.
- BGK2018: abstract only (RePEc page). The full text was not fetched; the title and the third author's first name are
  unverified.
- CEPR DP15617 (CHR2022) returned a Cloudflare challenge (02:19:50 PDT; saved as
  camanho_hau_rey_cepr_dp15617_blocked.html). The NBER version was used instead, and Scrapling was not tried.
- New pages were fetched with curl as direct PDF downloads, not with WebFetch. The tool and time of each fetch are in
  fetch_log.md.
- Not fetched: FCA Occasional Paper 46 (Evans, O'Neill, Rime, Saakvitne, "Fixing the Fix?"), which covers the effect
  of the five-minute window and is intraday. Hauptfleisch, Putnins and Lucey on London versus New York gold price
  discovery. Abrantes-Metz and Metz on the gold fix. Bell 2019 (MPRA) on holding gold between fixes. None of their
  abstracts or search snippets suggests a 5 to 20 day horizon.
- MP2013's 72% figure combines the two pooled coefficients. The paper gives p-values, not t statistics, and its
  sample ends in 2012, before the 2015 WMR window change. No post-2015 study of the next-day reversal was found.
- The settlement time used for E.23 entries was not checked against the fix times here. The statement that "most of
  the reversal precedes the settlement entry" (K3-ldnrev, K3-tkypre) rests on the fix clocks in the member docstrings
  and on the reversal horizons quoted above.
