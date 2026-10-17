# Stage E.23 P1.2 mechanism memo: M3_FLIGHT (flight to safety and cross-asset lead-lag)

Worker: MechanismReaderM3_FLIGHT-OpusHigh. Brief: reports/stage_e23_briefs/brief_mechanism.md.
Written 2026-10-17, started 02:16 PDT (from `date`), finished 02:26 PDT.
Pages and the fetch log are in reports/stage_e23_briefs/mech_pages/M3_FLIGHT/ (fetch_log.md has the URL, PDT time,
sha256 and tool for every page). Saved pages were read only by grep and line ranges. No market data was opened and no
test outcomes were read (the E.9 and E.22 K8 outcome JSONs were deliberately left unopened).

Members: K8-flight-01 H30 MGC, K8-flight-01 HEOD MGC (strategy/members/k8/flight.py), K8-oilcad-01 6C (k8/oilcad.py),
K8-wkndbtc-01 MNQ (k8/wkndbtc.py). Trigger definitions were taken from the module docstrings only.

The E.23 question, as it applies to these members: enter at the trigger day's settlement and hold 5 or 20 trading days.
- Flight: trigger day = a day with a 5-minute MES return at or below the trailing 0.5% quantile; fixed side BUY gold.
- Oilcad: trigger day = a day with a |z| >= 2 five-minute MCL move; side = sign of the crude move (BUY CAD when crude
  rises).
- Wkndbtc: trigger day = a Monday; side = sign of the Friday 14:59 to Sunday 17:59 MBT move.

## 1. Evidence table

| Key | Full citation | URL | Saved path (under mech_pages/M3_FLIGHT/ unless noted) | sha256 | Verbatim quote (page / section) | Claim supported: horizon, direction, magnitude, sample, instrument |
|---|---|---|---|---|---|---|
| BL06a | Baur, D.G. and Lucey, B.M., "Is Gold a Hedge or a Safe Haven? An Analysis of Stocks, Bonds and Gold", IIIS Discussion Paper No. 198 (Dec 2006); published Financial Review 45 (2010) 217-229 | https://www.tcd.ie/triss/assets/PDFs/iiis/iiisdp198.pdf | baur_lucey_2006_iiisdp198.pdf (.txt) | b1936662953977621345594cc98261103063f76f44723011b7bb7607feee559a | "Gold is a safe haven for stocks only for 15 trading days after an extreme shock occurred." (abstract, pdf p.3) | Horizon about 15 trading days. After that the safe-haven gain is gone. |
| BL06b | same | same | same | same | "The cumulated gold returns turn negative about 15 trading days after the initial shock in the US and in the UK and about 20 trading days in Germany. The plot also shows that the price of gold slightly increases after the initial shock for one period while it is falling in the UK and in Germany. Furthermore, the clear positive trend of cumulated stock returns in the US and in the UK shows that extreme negative stock returns are followed by positive stock returns." (Section 2, Figure 7 text, printed p.23, pdf p.25) | Event = daily stock return below its 5% quantile. Gold, cumulated from the shock day: positive at first, negative by day about 15 (US) or about 20 (Germany). Stocks rebound afterwards. Sample 30 Nov 1995 to 30 Nov 2005; spot gold against MSCI indices. Magnitude only in figures, with no numbers and no t-statistics in the text. |
| BL06c | same | same | same | same | "In the US, the gold price turns negative about 10 days and in Germany about 15 days after the extreme negative shock. These results show that gold is only a safe haven contemporaneously, that is, in the short-run. In the long-run gold loses value and is therefore not a safe haven. Moreover, investors that do not already hold gold and only purchase gold the day after an extreme shock either lose money directly due to a falling stock price or lose money relatively due to increasing stock prices right the day after the extreme negative shock." (1% quantile, Figure 9 text, printed p.23-24, pdf p.25-26) | 1% quantile shocks: US gold cumulative return negative by about day 10. Buying gold after the shock day (the E.23 entry timing) loses money. Direction: reversal of the flight-to-gold move. |
| BL06d | same | same | same | same | "investors that hold gold more than 15 trading days after an extreme negative shock loose money. The results also show that there is a large difference as to whether investors hold gold or purchase gold after an extreme negative shock occurred." (Conclusions, printed p.25, pdf p.27) | Horizon: the 20-day hold falls past the 15-day turn. |
| BL06e | same | same | same | same | Table 4 (5% quantile, Newey-West t with 5 lags), US: "s(t-1) 0.0200 1.1573"; "s(t-1,q) -0.0385 -1.2666"; and the text "purchasing gold after an extreme stock market shock is consistent with the safe haven hypothesis for the US market but not for the UK and for Germany" (pdf p.16) | One-day-ahead gold response to an extreme stock shock is not significant (US t = -1.27). No significant t+1 continuation. |
| BL06f | same | same | same | same | "since gold is a hedge against stocks, gold cannot be a safe haven in the long run since rising stock prices are associated with lower gold prices on average." (pdf p.20) | Mechanism for the reversal: gold's negative beta combined with the post-crash equity rebound. |
| BK20 | Baur, D.G. and Kuck, K., "The timing of the flight to gold: An intra-day analysis of gold and the S&P500", Finance Research Letters 33 (2020) 101187, doi 10.1016/j.frl.2019.05.005 (the member's source, K8-003) | https://ideas.repec.org/a/eee/finlet/v33y2020ics1544612319301448.html | reports/stage_e20_briefs/pages/GC/repec_baur_kuck_2020.html (E.20, reused, not refetched) | E.20 log: 8c876d9b7c74790d (prefix) | ABSTRACT ONLY: "extreme negative 5-min S&P500 returns lead to a positive reaction of the gold price. Second, on days with extreme price declines in the stock market, gold continues to increase post US stock trading hours." | Hours, not days: gold rises after the US close on extreme days. That is same-side continuation into the evening after the trigger day. The size of the move, how long it lasts, and whether the series is spot or futures are [unverified] (abstract only). Sample 2007-2018. |
| BBIW19a | Baele, L., Bekaert, G., Inghelbrecht, K. and Wei, M., "Flights to Safety", NBER WP 19095 (rev. May 2019); Review of Financial Studies 33 (2020) 689-746 | https://nber.org/system/files/working_papers/w19095/w19095.pdf | baele_etal_2019_nber_w19095.pdf (.txt) | 3bc36d2dc91c104b41a2f08ccf713c69ee0515a1f7b0df02c49e74bfb9a1b1df | "Intuitively, FTS spells are mostly short-lived. Expressed in fractions over all countries, we find that 62% of the spells last 1 day, 23% last two days, 9% last three days, and 6% last longer than 4 days, but none last longer than 10 days." (Section 4.1, printed p.22, pdf p.24) | The flight-to-safety flow is mostly a 1 to 3 day event and never lasts longer than 10 days. This argues against persistent 5 to 20 day flows. Sample Jan 1980 to Jun 2015, 23 countries, bonds against equities. |
| BBIW19b | same | same | same | same | "The average daily return on a FTS day is only 3 bps and almost never significant. However, the FTS beta of gold returns becomes positive and statistically significant for half the countries, averaging 0.20% per day, once we control for global equity market exposure." (Section 4.2, pdf p.26) | Gold on flight-to-safety days: +3 bp raw, not significant; +0.20%/day after removing equity beta. Same day only, nothing after the event. Instrument: S&P GSCI gold index. |
| FRR15a | Ferraro, D., Rogoff, K. and Rossi, B., "Can oil prices forecast exchange rates? An empirical analysis of the relationship between commodity prices and exchange rates", Journal of International Money and Finance 54 (2015) 116-141 | https://crei.cat/wp-content/uploads/2016/07/COPF_pub.pdf | ferraro_rogoff_rossi_2015_jimf.pdf (.txt) | 81ba0b97be693cbdf7b1a3c58f897d4c2d04c4127017a4101b073f57ead0f987 | "However, when we use lagged commodity price changes, the predictive ability is ephemeral, mostly appearing after instabilities have been appropriately taken into account." (abstract, p.116) | Lagged daily oil does not reliably predict CAD/USD. |
| FRR15b | same | same | same | same | Table 1, "B. Lagged Oil P. Model", Daily column, Clark-West p-values by window size 1/2 to 1/10: "0.096 ... 0.064 ... 0.121 ... 0.158 ... 0.148 ... 0.165 ... 0.304 ... 0.310 ... 0.304"; monthly 0.140 to 0.332 (p.123) | One-day-ahead (lagged oil) out-of-sample predictability of CAD/USD is not significant at 5% for any window. Monthly: none. Sample 14 Dec 1984 to 5 Nov 2010 (6,756 daily observations, p.120). |
| FRR15c | same | same | same | same | "the model with lagged oil prices forecasts significantly better than the random walk benchmark around 2006-2007 at the daily frequency. On the other hand, the same model at the monthly and quarterly frequencies never forecasts significantly better" (Section 3.2, p.126) | Any lead lasts one day and only in one sub-period. Nothing at multi-week horizons. |
| ZDG16a | Zhang, H.J., Dufour, J.-M. and Galbraith, J.W., "Exchange rates and commodity prices: Measuring causality at multiple horizons", Journal of Empirical Finance 36 (2016) 100-120, doi 10.1016/j.jempfin.2015.10.005 (WP version Sept 2015; the member's source, K8-006) | https://jeanmariedufour.research.mcgill.ca/Zhang_Dufour_Galbraith_2014_CommoditypriceXRateCausality_W.pdf | zhang_dufour_galbraith_2014_wp.pdf (.txt) | 363467fcbd3c12363b8f8888ef1fb3dc69c13e2b5c904a7ba7e836e6c78043b9 | "(2) causality is stronger at short horizons, and becomes weaker as the horizon increases" (abstract, p.2); Table 2: "WTI oil 9 CAD/USD 0.000" (Canada 03/01/1986 to 31/07/2015, p.15) | Daily: WTI Granger-causes CAD/USD at a horizon of one day (p = 0.000) and weakens out to day 10. The caveat in reports/stage_e0_catalog_K8.md X-05 applies: the CAD series is Statistics Canada and WTI is EIA, so a one-day "lead" can come from different fixing times alone. No magnitude in bp. |
| ZDG16b | same | same | same | same | "This sample extends from 03/01/2005 to 31/12/2009. ... There is weak evidence of Granger-causality in both directions, but it is stronger in the direction of commodity price to exchange rate, at horizon one. The measures drop quickly after horizon one" (Section 3.3, p.19) | 5-minute data: the lead lasts one 5-minute step. This is the member's own mechanism, and it is intraday. |
| MSS25a | Mourey, M., Shahrour, M.H. and Soiman, F., "A crypto-stock weekend effect: Predicting Monday stock returns using weekend cryptocurrency returns", Finance Research Letters 86 (2025) 108661, doi 10.1016/j.frl.2025.108661, CC-BY (the member's source, K8-004) | https://www.sciencedirect.com/science/article/pii/S1544612325019154 | mourey_etal_2025_frl_firecrawl.md | e62e50db33775a25a2dca2674eb119bd114ed6b01379fe708d5ae5f04ca71a9b | "Our results show a strong asymmetry: negative weekend returns significantly predict Monday equity declines, while positive returns have no effect. This pattern remains robust across benchmarks, including the Nasdaq ... The transmission mechanism strengthens markedly after the May 2022 LUNA collapse" (Abstract); "The sample period spans from 1 January 2021 to 1 June 2025" (Section 3) | Horizon: Monday only (one day). Direction: same side as the weekend move, and only for negative weekends. Sample 2021-2025, S&P 500 (Nasdaq as a robustness check). |
| MSS25b | same | https://ars.els-cdn.com/content/image/1-s2.0-S1544612325019154-fx1002.jpg | mourey_2025_table3.jpg (Table 3 image, read visually) | 843cc1c9cc6c3e41c55105ca18ab43d1bf9de5856b342451c9c348177d62ab65 | Table 3 (negative weekend returns), row BTC-USD: R_WE coefficient "0.1924", posterior P(beta>0) "(0.999)", R2 "0.089 [0.027, 0.175]"; note: "The dependent variable is Monday S&P500 returns." | Monday S&P 500 beta of 0.19 on negative weekend BTC returns: a -5% weekend gives about -0.96% on Monday. Bayesian, so there is no t-statistic. The Monday return definition (close-to-close or including the Sunday gap) is [unverified]. |
| MSS25c | same | same as MSS25a | mourey_etal_2025_frl_firecrawl.md | e62e50db... | "Future research could extend the analysis to assess the persistence of the post-2022 regime, study intraday adjustment once equity markets reopen" (Section 5, Conclusion) | The source tests no multi-day horizon and no intraday split. |
| LT18 | Liu, Y. and Tsyvinski, A., "Risks and Returns of Cryptocurrency", NBER WP 24877 (Aug 2018); Review of Financial Studies 34 (2021) 2689-2727 | https://www.nber.org/system/files/working_papers/w24877/w24877.pdf | liu_tsyvinski_2018_nber_w24877.pdf (.txt) | c59ede546d32c6c2d5215cf7600c6f8642406083fc37952b27d6ee5fa9f364f2 | "Cryptocurrencies have no exposure to most common stock market and macroeconomic factors. They also have no exposure to the returns of currencies and commodities." (abstract, p.2); "For Bitcoin, we use data from 01/01/2011 to 05/31/2018" (p.5) | Before 2018, crypto and equities were segmented. The paper offers no channel by which crypto moves predict multi-day equity returns. Sample 2011-2018 (it predates MSS25's regime). |

Read but not used for a claim: Baur and McDermott, "Is Gold a Safe Haven? International Evidence", IIIS DP 310 (2009)
(baur_mcdermott_iiisdp310.pdf, sha256 591dc6e85a83ccadc72f0cf15f1abae125b2968d63f8692512214ee51bd0ccd1). It has
daily, weekly and monthly contemporaneous safe-haven regressions for 1979-2009, but no post-event path at 5 to 20 days in
the passages grepped.

## 2. Per-member paragraphs

### K8-flight-01 H30 MGC and K8-flight-01 HEOD MGC (one paragraph: in E.23 the two trials share the trigger day and the settlement entry, and differ only in an intraday exit that E.23 does not use)
- Strength: moderate. The evidence is a close analog: daily extreme negative stock shocks and the gold path after them
  over 1 to 20 trading days (BL06b, BL06c). But the sample is 1995-2005, so it does not overlap 2010-2024. The path is
  shown only in figures, with no reported post-event return or t-statistic, and the one-day lag coefficient is not
  significant (BL06e).
- Direction: reversal, which is the opposite side to the member's long gold, at 20 days. At 5 days the evidence is
  neither, and leans flat. The member's own source points the same side only for the hours after the US close (BK20,
  abstract only). The sources do not truly disagree, because they speak to different horizons. They are listed under
  Horizon.
- Reason: on an extreme equity down day, investors move into gold (the flight-to-gold flow; BK20 dates the reaction to
  minutes, with a continuation "post US stock trading hours" on extreme days). Flight-to-safety flows are short-lived: 62%
  of spells last one day and none lasts more than 10 days (BBIW19a). Gold's flight-to-safety-day return is a
  non-significant 3 bp before adjusting for equity exposure (BBIW19b). After the shock, equities on average rebound
  (BL06b). Gold is a hedge with a negative stock beta, so the rebound pulls gold down: "gold cannot be a safe haven in the
  long run since rising stock prices are associated with lower gold prices on average" (BL06f). The cumulative gold
  return from the shock day turns negative about 15 trading days later in the US at the 5% quantile, and about 10 days
  later at the 1% quantile (BL06b, BL06c). BL06c also says investors who "only purchase gold the day after an extreme
  shock ... lose money", which is the timing of the E.23 entry. The trigger is a 0.5% 5-minute quantile, not a daily
  quantile. Many trigger days will therefore not be extreme daily down days, which dilutes any daily-shock mechanism.
  That point is my reading, not a source's.
- Horizon:
  - 20 days: yes, opposite side (BL06b-d).
  - 5 days: weak at most. The US path is slightly positive for one day and then flat (BL06b). The one-day-ahead
    coefficient is not significant (BL06e).
  - The only same-side evidence is post-close hours on the trigger day (BK20). A settlement entry may capture part of
    it, but that is a horizon of hours, not 5 days.
- Magnitude: not reported in any fetched text. BL06 gives figures only. BBIW19b gives same-day gold returns: +3 bp raw,
  and a beta of +0.20%/day after controlling for equities. No post-event bp per event and no t-statistic is available,
  and no post-publication decay is documented. For V31 the lead has no published expected gross per trade at 5 or 20
  days.

### K8-oilcad-01 6C
- Strength: none: intraday-only. The member's own source finds the 5-minute crude-to-CAD lead "drop[s] quickly after
  horizon one" (ZDG16b). The daily-frequency evidence for one day ahead is mixed (ZDG16a significant; FRR15b not
  significant), and there is no evidence at 5 or 20 days. If the lead counts the one-day daily lead in ZDG16a, the label
  could be raised to weak. Even then it does not cover the 5 to 20 day window.
- Direction: continuation (CAD follows the sign of the crude move), and only at horizon one. At 5 and 20 days no fetched
  source gives a direction.
- Reason: the terms-of-trade channel. Higher oil prices raise Canada's export revenue and demand for CAD. This shows up
  mainly as a contemporaneous daily relationship (FRR15a) and a lead of one 5-minute step (ZDG16b). When the lead is
  lagged, it is "ephemeral": the daily lagged-oil model's Clark-West p-values are 0.064 to 0.310 across windows (FRR15b),
  and it was significant only around 2006-2007 (FRR15c). Daily Granger causality from WTI to CAD/USD at a horizon of one
  day (p = 0.000) weakens as the horizon grows (ZDG16a). That result may partly come from the CAD fixing and the WTI
  close being taken at different times (catalog X-05). No source reports a post-shock drift in CAD over days. Over 5 to
  20 days, CAD would follow crude's own return over that window, so any multi-day edge would need crude itself to drift
  or reverse after a 5-minute shock. This family's literature does not cover that, and it was not researched here.
- Horizon: neither 5 nor 20 days. The evidence covers one 5-minute step (ZDG16b) and one day (ZDG16a, FRR15b).
- Magnitude: no bp size is published for the lagged effect. ZDG reports causality measures only. Their intensities are
  tiny: the catalog notes a 5-minute chart axis topping at 0.0024, values [unverified]. FRR15 reports p-values only.
  Sample 1984-2010 (FRR15) and 1986-2015 daily / 2005-2009 five-minute (ZDG16). Decay: FRR15c notes that the significance
  depends on the sub-period.

### K8-wkndbtc-01 MNQ
- Strength: none: intraday-only, or more precisely one day only. The source's effect is the Monday return itself
  (MSS25a). No fetched source tests days after Monday (MSS25c lists persistence as future research), and no source gives
  multi-day evidence for this event.
- Direction: none established at 5 or 20 days. On Monday the direction is continuation, the same side as the weekend
  bitcoin move, and only for negative weekends. Positive weekends "have no effect" (MSS25a). The member trades both
  signs, so the long side has no supporting evidence even for Monday.
- Reason: crypto trades through the weekend while equities are closed. Weekend crypto losses act as a risk signal that
  spills into Monday equities, and the spillover strengthened after the May 2022 LUNA collapse (MSS25a). The source
  frames this as negative-news asymmetry and stress-period transmission. That suggests a fast repricing at the reopen,
  not slow-moving capital. Pre-2018 evidence shows crypto had no exposure to equity factors (LT18), so the channel is
  recent and depends on the regime. No mechanism in the fetched literature carries the effect past Monday's settlement.
  The E.23 entry comes after the Sunday-open gap and the Monday session, which is where the documented effect sits.
- Horizon: neither 5 nor 20 days.
- Magnitude (Monday only, not the E.23 window): BTC Monday S&P 500 beta 0.1924 on negative weekend returns, posterior
  P(beta>0) = 0.999, R2 0.089 (MSS25b). A -5% weekend gives about -96 bp on the Monday S&P 500, and part of that is
  probably the Sunday gap (Monday return definition [unverified]). Sample Jan 2021 to Jun 2025, about 230 Mondays
  (count [unverified]). The source documents the regime break as a stability warning. No post-publication data exists,
  since the paper is from 2025.

## 3. Query log

Times are PDT and are bracketed by the `date` call (02:16:32) and the fetch-log timestamps around each batch. Tools:
WS = WebSearch (standard); OA = OpenAlex API by curl. 18 WebSearch calls in total, within the cap of 60.

| # | Query | Tool | Time (PDT) | Results kept |
|---|---|---|---|---|
| 1 | Baur Lucey 2010 "Is gold a hedge or a safe haven" 15 trading days pdf | WS | 02:16:33-02:18:12 | tcd.ie IIIS DP 198 (BL06), fetched |
| 2 | Ferraro Rogoff Rossi "Can oil prices forecast exchange rates" daily Canadian dollar pdf | WS | 02:16:33-02:18:12 | crei.cat JIMF PDF (FRR15), fetched |
| 3 | weekend bitcoin returns predict Monday stock returns Nasdaq paper | WS | 02:16:33-02:18:12 | none (bitcoin's own Monday effect, off-topic) |
| 4 | "The timing of the flight to gold" Baur Kuck intra-day S&P500 pdf | WS | 02:18:16-02:19:40 | none |
| 5 | Baele Bekaert Inghelbrecht Wei "Flights to Safety" NBER working paper pdf gold | WS | 02:18:16-02:19:40 | NBER w19095 (BBIW19), fetched |
| 6 | Mourey "Crypto-Stock Weekend Effect" Monday stock returns weekend cryptocurrency returns | WS | 02:18:16-02:19:40 | none |
| 6a | search "timing of the flight to gold"; search "crypto-stock weekend effect"; works/doi:10.1016/j.frl.2025.108661 | OA | 02:19:41 | Baur-Kuck has no open-access copy (SSRN only); Mourey is CC-BY with a HAL copy (MSS25) |
| 7 | bitcoin returns predict future stock market returns lead-lag days weeks Granger causality S&P 500 Nasdaq 2018-2023 study | WS | 02:20:48-02:21:25 | none kept (Ahmed et al. Heliyon 2023 noted: bidirectional daily VAR, no multi-day direction; not fetched) |
| 8 | Baur McDermott "Why is gold a safe haven" flight to quality duration days after crash gold returns | WS | 02:20:48-02:21:25 | IIIS DP 310, fetched (read, not used) |
| 9 | oil price shock Canadian dollar delayed response days post-shock drift exchange rate underreaction commodity currency | WS | 02:20:48-02:21:25 | none (bank commentary only) |
| 10 | gold safe haven short-lived event study cumulative gold returns days after extreme negative stock market days post-2010 sample | WS | 02:21:25-02:21:57 | none new (BL06 again) |
| 11 | Akhtaruzzaman Boubaker Lucey Sensoy "Is gold a hedge or a safe-haven asset in the COVID-19 crisis" phase | WS | 02:21:25-02:21:57 | abstract only (see section 4) |
| 12 | gold futures returns after large S&P 500 declines next 5 to 20 days persistence flight to safety reversal gold "trading days" study 2008-2020 | WS | 02:21:57-02:22:29 | none (blogs; Ryan, Corbet and Oxley FRL 2024 snippet only) |
| 13 | Baur Kuck "flight to gold" SSRN 3243111 gold reaction extreme negative equity returns hours | WS | 02:21:57-02:22:29 | sbfc P076 (Baur, Prange, Schweikert): 404 |
| 14 | crude oil returns predict Canadian dollar next week lagged oil weekly forecast exchange rate out-of-sample Kohlscheen Avalos commodity currencies | WS | 02:21:57-02:22:29 | none new (FRR15 again; NHH master's thesis snippet only) |
| 15 | IMF "Cryptic Connections" spillovers between crypto and equity markets bitcoin S&P 500 | WS | 02:22:29-02:22:52 | IMF note: PDF 403, landing page had no text |
| 16 | weekend cryptocurrency returns predict stock returns following week Tuesday persistence crypto equity information transmission weekend closure | WS | 02:22:29-02:22:52 | NBER w24877 (LT18), fetched |
| 17 | "flight to gold" OR "flight-to-safety" gold persistence weeks after equity crash event study intraday high-frequency gold S&P futures continuation next days | WS | 02:23:52-02:24:34 | no new relevant source (Dungey et al. co-jump study: flight frequency, not post-event horizon) |
| 18 | high-frequency crude oil shocks Canadian dollar futures response multi-day drift after large oil price moves intraday 5-minute evidence | WS | 02:23:52-02:24:34 | no new relevant source (BoC workshop slide repeating FRR "short-lived") |

Stopping rule: every member has its paragraph; 18 queries are logged and the last two added no new relevant source; the
key papers BL06, FRR15, ZDG16, BBIW19 and MSS25 were read in full text (MSS25 through Firecrawl, plus the Table 3 image).
The exception is BK20, which is not reachable (section 4).

## 4. Not verified or not reached
- BK20 (Baur and Kuck 2020, the flight member's own source): abstract only. The full text is on SSRN (which answers
  403) and Elsevier, with no open-access copy (OpenAlex). Unverified: the size and duration of the post-close gold
  continuation, the definition of "extreme", and whether the gold series is spot or futures.
- BL06 numbers come from the 2006 working paper. The 2010 Financial Review version may differ: its abstract says
  "approximately 15 trading days" [unverified against the journal text]. The post-event gold path appears only in
  figures (images, not read), so no bp magnitudes exist.
- Akhtaruzzaman, Boubaker, Lucey and Sensoy (Economic Modelling 102, 2021): search snippet only. Gold was a safe haven
  in Phase I of COVID (to 16 Mar 2020) and lost that role in Phase II. [unverified]; not fetched. It would be a post-2010
  analog for the short life of the gold haven.
- Ryan, Corbet and Oxley (Finance Research Letters 64, 2024), on gold's safe-haven effect depending on the shock type:
  snippet only, [unverified].
- Baur, Prange and Schweikert (2019, "Flight to Quality - Gold Mining Shares versus Gold Bullion"): sbfc.sydney.edu.au
  returned 404.
- IMF GFS Note 2022/01 (Iyer, "Cryptic Connections"): PDF 403 by curl. The Scrapling copy of the landing page held only
  navigation. Not used.
- MSS25: the HAL copy (hal-05415054) sits behind an Anubis anti-bot wall that explicitly targets automated scraping. It
  was not bypassed. The ScienceDirect page gave 403 to WebFetch, Scrapling get and Scrapling fetch. Firecrawl retrieved
  the CC-BY article. The Monday return definition and the exact number of Mondays were not found in the grepped text.
- Not researched (outside this family): whether crude oil itself drifts or reverses over 5 to 20 days after a large
  5-minute move. That question decides any multi-day 6C outcome, because CAD tracks crude contemporaneously.
- No over-budget WebSearch notice was seen. No throttling apart from the 403s and the anti-bot page logged above.
