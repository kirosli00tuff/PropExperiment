# Stage E.23 P1.2 mechanism memo: M10_USDA (WASDE drift; soybean crush spread)

Worker: MechanismReaderM10_USDA-OpusHigh. Brief: reports/stage_e23_briefs/brief_mechanism.md. Written 2026-10-17,
started 02:16 PDT (from `date`), memo finished 02:32 PDT (`date`).
Pages and fetch log: reports/stage_e23_briefs/mech_pages/M10_USDA/ (fetch_log.md has the URL, PDT time, sha256 and tool
for each fetch). Paths in the table below are relative to that folder unless they start with `reports/`.
Members (docstrings read, no data or outcomes opened):
- K6-wasdepre-01 (ZC, ZS): on a WASDE day, side = sign(close 10:29 - open 08:30), the drift before the 11:00 CT release.
- K6-wasdepost-01 (ZC): on a WASDE day, side = sign(close 11:14 - close 10:59), the first 15 minutes of the release
  response.
- K6-crushgap-01 (ZS only): G = GPM_open(d) - GPM_close(d-1), with GPM = 0.022 P_ZM + 11 P_ZL - P_ZS; G <= -2c sells
  ZS, G >= +2c buys ZS. This bets that the overnight gap in the processing margin reverses during the day session, and
  only the bean leg is traded.

E.23 enters at the trigger day's settlement and holds 5 or 20 trading days. A 20-day hold from a WASDE day usually ends
near the next monthly WASDE. That is my inference from the monthly schedule. I did not count it from the calendar.

## 1. Evidence table

| Key | Citation | URL | Saved path | sha256 (first 16) | Verbatim quote (location) | What it supports (horizon, direction, magnitude, sample, instrument) |
|---|---|---|---|---|---|---|
| ADJ19 | Adjemian, M., S. Arita, V. Breneman, A. Hungerford, R. Johansson (2019). "Market Reaction to USDA's August Corn Crop Reports." farmdoc daily (9):186, Oct 4, 2019 | https://farmdocdaily.illinois.edu/2019/10/market-reaction-to-usda-august-corn-crop-reports.html | farmdoc_2019-10_august_reports.md (line 515) | 5a20e11ec3ee0c30 | "The blue and yellow series in Figure 6 indicate that, on average, corn market prices respond to USDA news and those prices tend to remain at about the level of the initial response over the next two trading weeks." (text above Fig. 6). Sample (line 501): "the blue line is the average value observed from 2015-2018; the yellow line is the average observed from 2009-2018". Method (line 515): "if the announcement day price change was originally positive, we reverse signs of price changes over the following ten trading days" | Horizon 10 trading days. Direction: neither continuation nor reversal on average; the price holds the announcement-day level. 2019 was an exception that continued. No t-stat (read off a figure). August reports only, 2009-2018, Dec corn. |
| AHE21 | Arnade, C., L. Hoffman, A. Effland (2021). The Impact of Public Information on Commodity Market Performance: The Response of Corn Futures to USDA Corn Production Forecasts. USDA ERS, ERR-293 | https://www.ers.usda.gov/media/8964/err-293.pdf?v=63286 | arnade_hoffman_effland_2021_err293.pdf (+ .txt) | 2c6216d1900c6294 | "this study shows the USDA's influence on corn prices remains embodied in corn futures for several days after the release of USDA's WASDE report" (Summary, front matter before p. 1). "All lags of the USDA forecast were jointly tested. For most months, the USDA announcement was significant up to 3 days (equal to three lags) after the announcement." (fn. 24, p. 12). "Preliminary model results reveal that lags beyond 3 days were not statistically significant" (Model section, p. 6). "For the model covering the 2013-17 subperiod—when USDA WASDE reports were released at noon—USDA's forecast variable was only significant in June and October." (p. 12). Table 3, after 2012, close-price long-run elasticities: "August ... 0.042", "September ... 0.187" (positive, the wrong sign), "October ... -1.019" | Horizon: the release day plus up to 3 more days, inside the 5-day window; nothing at 20 days. Direction: the cumulative effect is in the release direction (continuation over days 1-3), but signs are unstable after 2012. Magnitude is given only as elasticities ("Long-run impact elasticities tend to be in the range of -0.02 to -0.04", Conclusion). There is no per-event return in bp. Daily OHLC regressions in levels with a lagged dependent variable; joint chi-square tests at 1%; 1999-2017; corn futures. |
| IKI24 | Isengildina-Massa, O., B. Karali, S. H. Irwin (2024). "What do we know about the value and market impact of the US Department of Agriculture reports?" Applied Economic Perspectives and Policy, doi 10.1002/aepp.13409 (open access) | https://onlinelibrary.wiley.com/doi/full/10.1002/aepp.13409 | isengildina_karali_irwin_2024_aepp.md (lines 409, 476, 593) | cf4aef28e9bbcbcc | Line 409: "Lehecka et al. (2014) examined the corn market reaction to USDA reports over 2009–2012 ... the strongest price reaction to report releases was found immediately after markets opened and persisted for about 10 min. They did not find evidence of systematic under- or over-reaction in prices." Line 476: "Cao and Robe (2022) extended these findings to demonstrate that market uncertainty in corn and soybean markets decreased not only immediately following the report release but remained low for up to 5 days after the release of WASDE". Line 593: "This paper reviewed and analyzed 74 studies of the value and impact of USDA reports" | A 74-study survey. A grep of the full text for "drift", "underreact", "reversal", "several days", "following days" and "subsequent days" returns no hits. The only "days after" hit is about implied volatility (Cao and Robe). So the survey reports no study with multi-day directional drift after USDA reports. Lehecka et al.: no under- or over-reaction (corn, 2009-2012, intraday). Cao and Robe: uncertainty stays lower for up to 5 days, a volatility effect with no direction. |
| AMN24 | Anderson, J., A. McKenzie, M. Noyes (2024). NCCC-134 paper on intraday corn and soybean WASDE reactions (saved by E.20) | https://farmdoc.illinois.edu/assets/meetings/nccc134/conf_2024/pdf/Anderson_McKenzie_Noyes_NCCC-134_2024.pdf | reports/stage_e20_briefs/pages/ZC/anderson_mckenzie_noyes_2024.pdf.txt (lines 64, 104, 149, 202) | 975651b9b93e8439 (txt; pdf e9df84b1f3fdad98) | "corn adjusts very little past the initial 30-minute time window. However, soybeans see significant adjustment after the initial 30-minute window." (l. 201-202). "the price reaction continues to grow for soybeans between 30 minutes and the daily close" (l. 104). "The data in out study spans from 2010 to 2021." (l. 149) | Horizon ends at the report-day close; nothing beyond it. Direction: continuation within the day for soybeans; corn is done after 30 minutes. 122 WASDE releases, 2010-2021. Soy coefficients by window (from E.20 product_ZS.md E2): 10 min -0.028, 30 min -0.061, day -0.124. |
| ZABG26 | Zhu, Adjemian, Bagnarosa, Gohin (2026). "Do USDA Reports Align Trader Expectations?" AAEA 2026 selected paper | https://ideas.repec.org/p/ags/aaea26/404355.html | ideas_zhu_adjemian_bagnarosa_gohin_2026.html (abstract) | 5e43a03debbf5a8f | Abstract only: "we estimate unconditional elasticities that are persistently below unity, consistent with incomplete post-report alignment of trader expectations" ... "using high-frequency data from 2013 to 2020" | Intraday volume-volatility evidence that disagreement persists after reports. No direction and no multi-day return. Theory-level support for slow digestion at most. |
| GA23 | Goyal, R., M. K. Adjemian (2023). "Information rigidities in USDA crop production forecasts." AJAE, doi 10.1111/ajae.12373 | https://api.openalex.org/works/doi:10.1111/ajae.12373 | openalex_oa_10_1111_ajae_12373.json (abstract) | a0107a0b03f02e44 | Abstract only: "Several previous studies find that revisions to the department's production and yield forecasts for major agricultural commodities are positively correlated" ... "information rigidities are the more likely culprit" | USDA revisions are positively autocorrelated from month to month. That would predict a next-month revision in the same direction, which matters only for holds that reach the next WASDE (about 20 days). The paper tests no price returns. Weak (theory). |
| SSMC25 | Silveira, Silva, Mattos, Cruz Junior (2025). "The Reaction of Corn Futures Markets to US and Brazilian Crop Reports." JFM, doi 10.1002/fut.22601 | https://api.openalex.org/works/doi:10.1002/fut.22601 | openalex_oa_10_1002_fut_22601.json (abstract) | 03fecd5e83fca52c | Abstract only: "we compare prices and volume behavior on report days with the 5 days preceding and following the announcements" | ±5-day window, but the abstract reports only return volatility and volume. Full text not reached (Wiley PDF blocked). |
| RP93 | Rechner, D., G. Poitras (1993). "Putting on the crush: Day trading the soybean complex spread." J. Futures Markets 13(1), 61-75 (authors' copy) | https://www.sfu.ca/~poitras/soy.pdf | poitras_sfu_soy.pdf (+ .txt, p. 67) | 99127afdd79c9336 | "the largest in absolute magnitude is the correlation between close-to-open and open-to-close GPM. This is important for present purposes, because it provides indirect support for the possibility of 'opening reversals'" (p. 67). "given the size and behavior of these correlation coefficients, it would appear that naive, trend-based, trading strategies for the individual commodities would almost surely not be highly profitable." (p. 67). "the statistical results for the earlier subsample are consistent with the longer term evidence provided by Johnson et al., which suggested a mean-reverting process for the GPM ... this is arguably not the case with the latter subsample." (p. 67) | The K6-crushgap source. Horizon: within the day. The single-leg serial correlations are insignificant, which argues against a ZS-only signal. Multi-day GPM mean reversion holds in 1978-1987 but is doubtful in 1987-1991. Pit era. |
| MIT10 | Mitchell, J. B. (2010). "Soybean Futures Crush Spread Arbitrage: Trading Strategies and Market Efficiency." J. Risk Financial Management 3, 63-96 | https://www.mdpi.com/1911-8074/3/1/63/pdf | mitchell_2010_jrfm.pdf (+ .txt) | 68382bf17eace4ad | Simon (1999), secondary (p. 65): "He finds that the crush spread tends to revert toward its 5-day moving average with a half-life of deviations of about 3 days." Own results: "Trades are opened when the crush spread deviates from its most recent 5-day moving average by amounts ranging from $200 to $400" (s. 5). "The average trade length, Table 6, ranges from 1.79 days at 220/200 to 4.34 days at 200/0." (s. 6.1). "Average profit, Table 2, ranges from a low of -$41.88 at limits of 100/80 to $122.17 at 400/80." (s. 6.1.2, net of "$103.50 transaction costs"). "In general, the fourth time segment gives negative average profit results" (s. 6.2.2). "Even the maximum number of 994 trades amounts to no more than one trade every 7 days" (s. 6.1.1). Sample: "the period from June 4, 1984 through April 7, 2006" (s. 4) | Horizon 1-5 days: mean reversion of the 3-leg spread toward its 5-day mean, half-life about 3 days. Maximum profitable trade length "5 days ... to 9 days". Magnitude, my arithmetic: one 1:1:1 spread is 5,000 bu of beans, so net -$42 to +$122 per trade is -0.8 to +2.4 c/bu, and gross (adding back $103.50) is about 1.2 to 4.5 c/bu. Per-trade SD $219 to $595; CV at least 4.28. Unstable: the last quarter of 1984-2006 lost money. Spread, not a single leg. Johnson et al. (1990/91) are cited here only second-hand (p. 66). |
| LS16 | Liu, Q. W., H. H. Sono (2016). "Empirical Properties, Information Flow, and Trading Strategies of China's Soybean Crush Spread." JFM 36, 1057-1075 | https://api.openalex.org/works/doi:10.1002/fut.21777 | openalex_oa_10_1002_fut_21777.json (abstract) | 78f3a2b6054dd850 | Abstract only: "we find evidence of one-way information flow from the soymeal and soyoil markets to the soybean market" ... "Trading simulations based on the mean-reverting tendencies of the cointegration relationship and 5-day averages of the commonly-used spread both generate positive returns." | Dalian analog. The bean leg is the one that adjusts, which is relevant to a ZS-only member. 5-day-average reversion is profitable. Magnitude and horizon not in the abstract. |
| AC25 | Abdoh, H., M. Chitavi (2025). "Mean reversion of the soybean crush spread: A new model and trading strategies." Int. Rev. Econ. Finance 101, 104186 | https://ideas.repec.org/a/eee/reveco/v101y2025ics1059056025003491.html | reports/stage_e20_briefs/pages/ZL/ideas_abdoh_chitavi_2025.html (abstract; sha 9204c6f2e28a4119); also openalex_oa_10_1016_j_iref_2025_104186.json | 9204c6f2e28a4119 | Abstract only: "Our simulations demonstrate that trading strategies based on these findings would have been profitable, even after accounting for transaction costs. This analysis is based on 8650 trading days from September 1990 to May 2021." | The only crush-reversion study whose sample overlaps 2010-2021. Horizon, per-trade magnitude and which leg moves are all unknown. ScienceDirect full text not reached (captcha; tdm-reservation=1). |
| LH18 | Li, Z., D. Hayes (2018). "The Reverse Soybean Crush Spread: Evidence of the Hedging Pressure Hypothesis." AAEA 2018 selected paper | https://ageconsearch.umn.edu/record/274465/files/Abstracts_18_05_23_20_18_13_46__171_221_3_96_0.pdf | li_hayes_2018_reverse_crush_firecrawl_p1-2.md (Introduction, p. 1) | c6c68b5da19e195f | "we analyze the monthly return of the reverse crush spread, an effective sale of soybean futures contracts and offsetting purchase of soybean meal and oil futures contracts, by contract maturity from 1962 to 2016" ... "The existence of hedging pressure in the soybean complex is consistent with the positive and predictable return on this reverse crush." (p. 1; only pages 1-2 of 12 read) | Monthly horizon. Short beans against long products earns a premium regardless of the gap. That favors only the member's sell-ZS side. Magnitude not read. |

## 2. Member paragraphs

### K6-wasdepost-01 (ZC; side = sign of the 11:00-11:15 CT WASDE release response)
- Strength: weak.
- Direction: the literature disagrees, mildly.
  - Short continuation over days 1-3 in the release direction: AHE21, 1999-2017, joint-significant lags up to 3 days.
  - Neither continuation nor reversal at 10 trading days: ADJ19, August reports 2009-2018, "remain at about the level of the
    initial response over the next two trading weeks".
  - No source documents a reversal.
- Horizon: 5 days (AHE21 days 1-3; ADJ19 10 days). 20 days: no evidence.
- Reason. The only multi-day mechanism is incomplete absorption of the WASDE news:
  - Traders still disagree after the report (ZABG26, abstract only, theory-level).
  - USDA revisions are serially correlated (GA23, abstract only), which could carry into the next month's report, near the
    end of a 20-day hold.
  - The direct evidence goes against a drift. Corn's reaction ends within 30 minutes (AMN24, 2010-2021; Lehecka et al. via
    IKI24 line 409: "no evidence of systematic under- or over-reaction").
  - The one multi-day directional study (AHE21) is a levels regression. Its lags matter for at most 3 days, and after 2012
    its forecast variable is significant only in June and October, with wrong-signed long-run elasticities in August and
    September.
  - The 74-study survey (IKI24) reports no multi-day drift study.
- Magnitude: no per-event post-settlement return in bp or ticks is published. ADJ19 is about 0 over 10 days (read from a
  figure, no t-stat). AHE21 gives only elasticities (-0.02 to -0.04 long run). Post-publication decay: AHE21's 2013-17
  subperiod is weaker than 1999-2012.
- Why the grade is weak: published multi-day work on this event and instrument exists, but it shows a null by about 10
  days. The only directional piece is limited to 3 days, unstable after 2012, and has no return-level t >= 2.

### K6-wasdepre-01 (ZC, ZS; side = sign of the 08:30-10:29 drift on the WASDE day)
- Strength: weak. The trigger's own mechanism is intraday-only.
- Direction: the trigger's mechanism makes no multi-day prediction. The only multi-day channel is generic post-WASDE drift,
  and it predicts at most a short continuation of the release-day move (AHE21), or a null (ADJ19), as for wasdepost.
- Horizon: neither, as far as this trigger is concerned. The post-WASDE evidence above covers 5 days at most.
- Reason:
  - The catalog's mechanism (reports/stage_e0_catalog_K6.md, K6-wasdepre-01) is informed trading before the 11:00 release.
    Its sources (Aitkulova et al. 2026; Zhang 2024) are abstract-only in the catalog and were not reached here [unverified].
  - That mechanism resolves at 11:00, when the number is public. By the settlement entry there is nothing left to
    anticipate.
  - A multi-day effect would need the release-day move to keep drifting. That requires the pre-release drift sign to match
    the release-response sign, which no source measures, and a post-WASDE drift, which the evidence does not show (see
    wasdepost).
  - For ZS, AMN24 shows soybean adjustment continuing to the report-day close ("continues to grow for soybeans between 30
    minutes and the daily close"). That supports slower digestion in beans, but the published evidence stops at the close.
    Extending it beyond the close is my inference, not a finding.
- Magnitude: none published for days after the WASDE day. AMN24's within-day soybean coefficient is -0.124 at the day
  close (the response to ending-stocks news, 2010-2021). It does not apply after settlement.

### K6-crushgap-01 (ZS only; sells ZS when the overnight GPM gap G <= -2c, buys when G >= +2c)
- Strength: weak for the member as traded (the ZS leg alone). The three-leg spread analog is moderate: old samples,
  unstable, abstract-only modern overlap.
- Direction: same side as the member, but only to the extent that a margin deviation is still open at settlement.
  - The spread literature says GPM deviations from the recent 5-day mean revert: RP93 for the pit era; MIT10 for
    1984-2006; Simon 1999 via MIT10; LS16 Dalian (abstract); AC25 1990-2021 (abstract).
  - No source says a margin deviation keeps widening over days.
  - LH18 adds an unconditional monthly premium to short beans against long products. That favors only the member's sell-ZS
    trades and is not tied to the gap.
- Horizon: 5 days. The half-life is about 3 days (Simon via MIT10); average trades last 1.79-4.34 days and profitable ones
  5-9 days at most (MIT10). 20 days: no evidence on this signal. Johnson et al.'s 1.5-9.5-month trades use a 60-day-mean
  deviation and are second-hand.
- Reason: the processing margin is anchored by crushers' arbitrage, so the margin reverts after a dislocation. The member
  reads that dislocation as the overnight gap.
- Three gaps between that evidence and the member:
  1. The member's own source puts most of the reversal inside the day session: close-to-open vs open-to-close GPM
     correlation of -0.49 and -0.43 (catalog P-K6-001-d). A settlement entry may find the gap already closed. No source
     measures whether an overnight gap still predicts the margin over the next 5 days.
  2. The reversion is a spread property. RP93 finds the single-leg serial correlations insignificant ("naive, trend-based,
     trading strategies for the individual commodities would almost surely not be highly profitable").
     - The Dalian information-flow result says the bean leg is the one that adjusts (LS16, abstract), which would favor ZS.
     - No CBOT study says which leg moves.
  3. Stability: MIT10's last quarter of 1984-2006 lost money, and RP93 doubts mean reversion in 1987-1991.
- Magnitude: spread, not the ZS leg. MIT10 nets -$41.88 to +$122.17 per 1:1:1 spread trade after $103.50 costs. By my
  arithmetic (5,000 bu per spread) that is about -0.8 to +2.4 c/bu net and 1.2 to 4.5 c/bu gross. Per-trade SD is
  $219-$595 (CV at least 4.28), with at most one trade every 7 days; sample 1984-2006. The ZS-leg share is unpublished.
  AC25 (1990-2021) claims profits after costs; size unknown (abstract only).

## 3. Query log

Times are PDT on 2026-10-17. Each is bracketed by logged fetch timestamps or file mtimes; I did not record per-query clock
times.

| # | Query | Tool | Time (bracket) | Results kept |
|---|---|---|---|---|
| 0 | grep of reports/stage_e20_briefs, stage_e13_briefs/pages, stage_e2*_briefs, docs, stage_e0 catalog and registry for WASDE/crush | grep | 02:16-02:18 | AMN24 (E.20), AC25 abstract (E.20), Ying-Chen-Dorfman 2017 (E.20; volatility only, not used), catalog K6 source keys |
| 1 | post-announcement drift USDA WASDE reports corn soybean futures returns following days underreaction | WebSearch | 02:18:40-02:19:12 | ERR-293 lead (AHE21), ZABG26 |
| 2 | soybean crush spread mean reversion trading strategy Simon 1999 Journal of Futures Markets holding period days | WebSearch | 02:18:40-02:19:12 | MIT10 (MDPI), AC25, LS16 lead |
| 3 | "err-293" ers.usda.gov pdf Arnade Hoffman Effland ... | WebSearch | 02:20:30-02:22:34 | ERS chart page, which led to the publication page and PDF |
| 4 | Garcia Irwin Leuthold Yang 1997 value of public information ... subsequent days returns | WebSearch | 02:22:48-02:23:32 | none new (bibliographic only) |
| 5 | USDA report announcement risk premium commodity futures returns announcement days corn soybeans | WebSearch | 02:22:48-02:23:32 | none for direction (He-Bian 2025 is an options volatility premium) |
| 6 | crop report futures price reaction overreaction reversal following trading days ... | WebSearch | 02:22:48-02:23:32 | none new (AMN24 already held) |
| 7-10 | OpenAlex search: "USDA reports futures drift days after"; "crop report futures underreaction"; "WASDE futures price adjustment days"; "soybean crush spread trading" | OpenAlex API (curl) | 02:23:32-02:23:40 (file mtimes) | Cao-Robe 2020, SSMC25, GA23, LS16, AC25 OA status, LH18 |
| 11 | Aitkulova Balsamo Seamon "WASDE Surprises and Futures Prices" drift prior to release | WebSearch | 02:25:19-02:25:55 | none (paper not found) |
| 12 | Milonas 1987 "effects of USDA crop announcements on commodity prices" ... | WebSearch | 02:25:19-02:25:55 | none (bibliographic only) |
| 13 | soybean crush spread cointegration half-life days CBOT meal oil daily data 2010 2020 mean reversion | WebSearch | 02:25:19-02:25:55 | Marowka et al. 2020 (JRSS-C; not read, no trading horizon in snippet) |
| 14 | Isengildina-Massa Karali Irwin review market impact USDA reports survey ... duration | WebSearch | 02:25:19-02:25:55 | IKI24 (via Irwin blog, then OpenAlex OA link 02:26:08) |
| 15 | corn soybean futures prices continue to move days after USDA report WASDE momentum ... 5 days 10 days | WebSearch | 02:26:51-02:27:36 | none (trade press only) |
| 16 | "Grain Stocks" OR "Crop Production" report surprise futures "subsequent" returns predictability ... | WebSearch | 02:26:51-02:27:36 | none (trade press only) |
| 17 | soybean crush spread pairs trading profitability recent CBOT data out-of-sample ... | WebSearch | 02:27:36-02:27:44 | RP93 authors' copy (sfu.ca) |
| 18 | Johnson Zulauf Irwin Gerlow 1991 soybean complex spread market efficiency production process pdf | WebSearch | 02:27:44-02:28:59 | Johnson et al. 1990 NCCC-134 PDF (scanned, no text; not used) |
| 19 | soybean board crush margin overnight gap reversal intraday electronic trading day session spread trading rule | WebSearch | 02:27:44-02:28:59 | LH18 (AgEcon abstract, read via Firecrawl) |

Stopping rule:
- WASDE side: queries 15 and 16 added no new relevant source.
- Crush side: queries 18 and 19 added one scanned PDF with no text and one abstract-level unconditional premium (LH18).
  Neither gives a new conditional multi-day result.
- WebSearch calls used: 17 of 60. No over-budget notice was seen.

## 4. Not verified or not reached
- Simon (1999, JFM 19:271-289), the main multi-day crush paper: Wiley paywall. Its half-life (about 3 days) and per-trade
  profits are cited only second-hand from MIT10.
- Johnson, Zulauf, Irwin, Gerlow (1990/1991): the PDF is a scan with no text layer. Cited only second-hand (MIT10, RP93).
- Abdoh and Chitavi (2025): abstract only. ScienceDirect returned a captcha to Scrapling get and fetch, the page carries
  tdm-reservation=1, and Firecrawl query mode failed. Its horizon, magnitude and leg are unknown.
- Liu and Sono (2016), Silveira et al. (2025), Cao and Robe (2020/2022), Goyal and Adjemian (2023), Zhu et al. (2026):
  abstracts only. Wiley pdfdirect is Cloudflare-blocked for curl; Scrapling fetch worked only for the AEPP HTML.
- Aitkulova, Balsamo, Seamon (2026) and Zhang (2024): the pre-release informed-trading sources of K6-wasdepre. Not found
  by search (AgEcon blocks automation; SSRN gives 403). [unverified] beyond the catalog's abstract quotes.
- Milonas (1987), Garcia et al. (1997), Fortenbery and Sumner (1993), Sumner and Mueller (1989): not read; bibliographic
  hits only.
- The Catolica 2014 thesis "The value of fundamentals in agricultural futures markets: an event study approach using WASDE
  reports" (hdl 10400.14/16927) may hold multi-day CARs, but repositorio.ucp.pt refused the connection.
- Li and Hayes (2018): only pages 1-2 of 12 read, so no magnitude.
- AgEcon Search blocks curl and Scrapling with a bot check. That is the access route for most of this literature, so it
  is the main gap.
- Firecrawl credits used: 1 (record links) + 35 (ERR-293 query, failed) + 5 (ScienceDirect query, failed) + 2 (LH18).
