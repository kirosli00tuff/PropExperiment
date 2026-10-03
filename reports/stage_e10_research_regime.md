# Stage E.10 research log, Reader 1: regime (R1 volatility state, R2 large prior-day move, R3 range compression)

- Reader: LitReader-Regime-OpusHigh (model claude-opus-5-5, effort high)
- Start: 2026-10-02 22:32 PDT. End: 2026-10-02 22:52 PDT.
- Inputs read: reports/stage_e10_search_plan.md (common rules, Reader 1 topics, log format),
  reports/stage_e10_design_target.md sections (a), (b), (c), reports/stage_e10_briefs/e0_logged_sources.txt
  (grep only). Nothing under data/, no screen records, no results files.
- Raw pages: reports/stage_e10_research/regime/ (PDF plus pdftotext .txt beside each; HTML and markdown
  pages as saved). API search records: reports/stage_e10_research/regime/api/ (search records, not evidence).

## Counts

| Item | Count |
|---|---|
| Records screened, title level | about 460: 160 OpenAlex records (8 searches x 20) plus about 300 WebSearch result links (38 calls) |
| Items opened or fetched | 52 fetch attempts (fetch log below) |
| Sources logged (K9R ids) | 25 |
| Full text read (grep) | 16 (K9R-001, 002, 004, 008, 009, 010, 011, 014, 015, 016, 017, 018, 020, 022, 024, 025) |
| Abstract only | 8 (K9R-003, 005, 006 via pointer page, 007, 012, 013, 019, 021) |
| Summary page only | 1 (K9R-023, AQR summary of a working paper) |
| Blocked or no text (not logged as sources) | 9 (see rejection table: Wang-Yu 2004, Banerjee-Doran-Peterson 2007, Marshall-Cahan-Cahan 2008, Bansal-Stivers SSRN, Connolly-Stivers-Sun JFQA, CESifo x2, Hull, Wallmeier) |
| WebSearch calls used | 38 tool calls (three of them ran several internal queries in "extended" style; no over-budget notice was received) |
| Firecrawl uses | 0 |

Tool notes (logged as facts, not decisions):
- The Semantic Scholar key in .env has a value of length 1 (effectively empty). Calls with it returned
  `{"message":"Forbidden"}`; keyless calls returned HTTP 429. Semantic Scholar was therefore unusable for
  this reader. OpenAlex was used as the scholarly API; its relevance ranking for these topics was poor
  (R3 queries returned no finance papers), so most discovery came from WebSearch.
- The shared session scratchpad was overwritten by another reader's helper scripts at 22:34 PDT. Three
  OpenAlex search records (oa_r2a/b/c) were briefly written to commodity/api/ and were moved back to
  regime/api/. Private helper copies were used from then on. No evidence file was affected.

## Stop reason per topic

- R1 (volatility state): saturation. The last 15 records screened (OVX, bitcoin volatility, MOVE,
  VIX-spike practitioner notes, Copeland, Lubnau-Todorova, Bansal-Stivers, VRP short-horizon items) added
  no mechanism beyond "a volatility or uncertainty premium earned after implied volatility rises", which
  K9R-001 to K9R-007 already carry.
- R2 (large prior-day move, not a fade): saturation. The last 15 records (margin papers, Cox-Peterson
  pointers, Kudryavtsev, Vaasa thesis, Savor, inside-day pointers) added no new non-fade mechanism; the
  continuation evidence remains the Caporale-Plastun family and Joseph-Mazouz, and the conflicting
  evidence is Janardanan et al., Hua-Wei and Bianco et al.
- R3 (range compression): saturation, with a negative finding. No peer-reviewed or working-paper test of
  narrow-range or inside-day direction in futures was found. Every NR4/NR7/inside-day source located is
  practitioner material (Crabel 1989-1990 articles and book, Bulkowski) available only as pointers. The
  academic evidence found is on volatility persistence (magnitude, not direction) and on candlestick
  patterns (no value).

---

## R1. Session drift conditioned on a volatility state

### K9R-001 Premium for heightened uncertainty (VIX spikes and pre-announcement returns)

- Citation: Hu, Grace Xing; Pan, Jun; Wang, Jiang; Zhu, Haoxiang (2019, revised March 2021). "Premium for
  Heightened Uncertainty: Explaining Pre-Announcement Market Returns." NBER Working Paper 25817.
  Published Journal of Financial Economics (2022), DOI 10.1016/j.jfineco.2021.09.015 (DOI from the OpenAlex
  record oa_r1a.json; journal pages not fetched).
- Retrieval: curl from nber.org; regime/hu_pan_wang_zhu_nber_w25817.pdf (+ .txt). Full text.
- Mechanism: a risk premium for heightened "impact uncertainty". When implied volatility (VIX) builds up
  (before a scheduled release, or in an unscheduled one-day spike), the market falls; the uncertainty then
  resolves and the market earns a positive premium on the next day or in the pre-announcement window.
- Products and horizon: S&P 500 index futures (big contract before Sept 1997, E-mini after) for the
  pre-announcement windows; S&P 500 index daily returns for the unscheduled VIX-spike days (Table 7).
  Horizon: prior close (4 pm ET) to 5 minutes before the release; or one trading day (close to close) after
  a heightened-VIX day.
- Sample window: September 1994 to May 2018 (main); January 1986 to May 2018 (Table 7 bottom panel).
- Market and data frequency: CME transaction-level S&P futures, VIX futures tick data, daily VIX and
  S&P 500 index.
- Cost assumptions: none stated (gross returns).
- Quality tells: peer-reviewed (JFE) with a model making the prediction before the test (Prediction 5);
  out-of-sample (1986 start) results weaker; t-stats in the 2 to 3 range; the 76.6 bps figure in the
  introduction sorts on the *contemporaneous* pre-announcement VIX change (not tradable ex ante); the
  tradable sorts are the accumulation-period ΔVIX (VIX_{t-1} - VIX_{t-7}) and the one-day ΔVIX cutoffs.
- Verified passages:
  - P-K9R-001-a (Intro, p. 2): "From September 1994 to May 2018, the pre-announcement returns for NFP, ISM, and GDP are on average 10.1 bps, 9.1 bps, and 7.5 bps, respectively, and all statistically significant. Using S&P 500 index futures, these pre-announcement re- turns are calculated from the close of the previous trading day at 4 pm to 5 minutes before the respective announcements"
  - P-K9R-001-b (Intro): "Focusing on non-announcement days, we identify days of unanticipated heightened uncertainty using sudden and large increases in VIX. Consistent with our model's prediction, we find that such heightened VIX days are followed by large next-day market returns, with magnitudes comparable to the pre-announcement returns."
  - P-K9R-001-c (Intro): "we find predictability only for those non-announcement days with heightened VIX and the adjusted R-squared of the predictive regression is 2.34%, comparable to that for the scheduled announcements. For all other non-announcement days, changes in VIX cannot predict the next-day returns and the R-squared is essentially zero."
  - P-K9R-001-d (Sec. on unanticipated uncertainty, p. 39): "For the post-1994 sample period, a cutoff value of 2.5% yields an average of 11.1 heightened VIX days per year, comparable to the monthly frequency of NFP, ISM, and GDP, while a higher cutoff value of 3.0% results in an average of 7.7 heightened VIX days per year, comparable to the FOMC frequency. Rather interestingly, the corresponding next-day returns, as reported under Rett+1 in Table 7, are 36.59 and 42.70 basis points, respectively, and both statistically significant."
  - P-K9R-001-e (Table 7, rows, 1994-2018, η = 0): "1.5 24.6 19.63 2.68" and "1.0 39.7 10.34 2.01" (cutoff in VIX points, heightened days per year, next-day return bps, t-stat).
  - P-K9R-001-f (Table 7, rows, 1986-2018, η = 0): "1.5 22.2 14.22 2.07" and "1.0 36.5 6.59 1.41".
  - P-K9R-001-g (Table 5 discussion): "the average pre-announcement return is 20.63 basis points for the high group, statistically significant and twice as large the 9.42 basis points for the low group." (high group = top 30 percentile of accumulation-period ΔVIX, measured "by VIXt−1 -VIXt−7 , using information up to the day before the announcement day t").
  - P-K9R-001-h (Model): "Prediction 5 Unanticipated spikes in VIX will be followed by VIX reversals and high re- turns."
- Numeric claims: unscheduled heightened-VIX day (ΔVIX ≥ 1.0 point): 39.7 days a year, next-day S&P
  return 10.34 bps, t 2.01 (P-K9R-001-e); ΔVIX ≥ 1.5: 24.6 a year, 19.63 bps, t 2.68 (P-K9R-001-e); in the
  1986-2018 sample the same cutoffs give 6.59 bps (t 1.41) and 14.22 bps (t 2.07) (P-K9R-001-f).
  Pre-announcement (NFP/ISM/GDP/FOMC) with high accumulation ΔVIX: 20.63 bps vs 9.42 bps (P-K9R-001-g).
- Conflicting evidence: weaker in the longer sample (P-K9R-001-f); K9R-008 (volatility timing: returns do
  not rise in proportion to volatility); K9R-014 and K9R-012 (high-volatility states carry negative daily
  autocorrelation, so the next-day gain after a VIX spike may be a reversal of the spike-day fall, which is
  X10 in mechanism even if the condition reads VIX).
- Reader's note: Shape: condition = ΔVIX over the prior day (or VIX above its EWMA) at or above a cutoff,
  read at the 15:15 CT VIX close; with the 1.0-point cutoff it fires on about 40 of about 252 days (f about
  0.16), the 1.5-point cutoff about 25 (f about 0.10), both inside the 10% to 40% band. Hold: next trade
  date, 17:00 CT reopen to F (the source measures close to close on the cash index, so the D-exit default
  is "C_X - 2 min"). Sign: long, all equity exposures (MNQ, M2K, MYM inherit S&P evidence; flag S&P/cash).
  Exclusions: X10 is the main risk. The condition reads a volatility change, not the sign of the move, which
  is the borderline rule's test, but VIX spikes coincide with down days, so the trade is long after mostly
  down days; Task 4 must rule. X14 risk: VIX is computed from SPX options, i.e. another market's price
  (V16 class); a variant on the vehicle's own realized volatility is not tested by the source. The
  pre-announcement variant overlaps X4 (scheduled-release window) and the Calendar reader's topic and also
  sits on the CPI window rule (D9.12) for NFP-type days. Cost wall, in the source's units: 10-20 bps per
  trade on an index with a mean absolute daily move of roughly 70-100 bps in this period (my reading, not a
  source number) is about 0.1-0.25 x E|m1|. That clears M_X for MNQ, M2K and MYM (M_X is about 0.02-0.09 x
  E|m1| by the design table's own ratios) but is far below G(0.2) (1.10-1.21 x E|m1|) and G(0.1).

### K9R-002 Implied volatility indices as leading indicators (Giot) [E.0 K1-025]

- Citation: Giot, Pierre (2002 working paper, September 19, 2002). "Implied volatility indices as leading
  indicators of stock index returns?" CORE, Université catholique de Louvain. Journal version: Giot (2005),
  "Relationships between implied volatility indexes and stock index returns", Journal of Portfolio
  Management 31(3), 92-100 [journal DOI unverified]. E.0 id: K1-025.
- Retrieval: curl from research.dial.uclouvain.be bitstream; regime/giot_uclouvain.pdf (+ .txt). Full text
  (working-paper version).
- Mechanism: very high implied-volatility levels mark "oversold" fear states followed on average by
  positive index returns (contrarian, risk premium in fear states); average and moderately high levels are
  followed by poor risk-adjusted returns.
- Products and horizon: S&P 100 (VIX, old VXO definition) and Nasdaq-100 (VXN) cash indices; 1-, 5-, 20-
  and 60-day forward returns.
- Sample window: S&P 100: January 2, 1986 to August 2, 2002 (text) / to May 8, 2002 (table note; the
  paper is inconsistent). Nasdaq-100: January 3, 1995 to March 27, 2000 (bull) and March 13, 2000 to
  August 2, 2002 (bear).
- Market and data frequency: daily closes.
- Cost assumptions: none.
- Quality tells: percentile thresholds are full-sample (look-ahead); overlapping multi-day returns; the
  1-day regression is weak; small N in the top buckets.
- Verified passages:
  - P-K9R-002-a (Abstract): "very high levels of implied volatility can on a statistical basis be viewed as signalling an imminent increase in stock indices, at least on a short term basis. Our analysis also shows that average to moderately high levels of implied volatility lead to unfavorable (from a mean-variance perspective) returns."
  - P-K9R-002-b (Sec. II): "Hence the econometric analysis does not show a strong relationship between VIX or VXN levels and 1-day ahead returns on the S&P100 or NASDAQ100 indices."
  - P-K9R-002-c (Table I, columns 1-, 5-, 20-, 60-day): "VIX larger than its 90% percentile (=28.98, N=413)" / "Mean 0.19 0.96 2.52 5.28" / "Std. 2.31 3.48 5.43 8.24" (1-day mean 0.19%, 1-day std 2.31%; the 20-day figure is also stated in text: "buying the S&P100 index whenever VIX is larger than its 90% percentile and closing the long position after 20 days yield an average return of 2.52% with a standard deviation of 5.43%").
  - P-K9R-002-d (Table II, Nasdaq-100 bull period): "VXN larger than its 90% percentile (=45.83, N=133)" with "Mean. 0.51" and "Std. 2.95" for 1-day returns.
- Numeric claims: S&P 100 after VIX > 90th percentile: 1-day mean 0.19%, std 2.31%, N 413 (P-K9R-002-c),
  i.e. t about 1.7 if the 413 days were independent (my arithmetic). Nasdaq-100 bull period after VXN >
  90th: 1-day mean 0.51%, std 2.95%, N 133 (P-K9R-002-d).
- Conflicting evidence: P-K9R-002-b in the same paper; K9R-005 (low, not high, implied volatility followed
  by positive returns 2000-2013); K9R-008.
- Reader's note: Condition "VIX above its trailing 90th percentile" is too rare and too clustered (fires in
  crises, many consecutive days) for the weekly cap; the D-pct 80th percentile version would fire on about
  20% of dates but is not what the source tested. Hold: 1 day (fits a session hold); evidence at 1 day is
  weak. Sign: long equity index. X10 and X14 risks as for K9R-001. Size: 0.19% vs E|r| about 1.8% in that
  high-vol bucket (std 2.31% x 0.8) is about 0.1 x the bucket's own mean absolute move.

### K9R-003 S&P futures returns and contrary sentiment indicators (Simon and Wiggins)

- Citation: Simon, David P.; Wiggins III, Roy A. (2001). "S&P futures returns and contrary sentiment
  indicators." Journal of Futures Markets 21(5), 447-462 [DOI not captured; IDEAS handle
  RePEc:wly:jfutmk:v:21:y:2001:i:5:p:447-462].
- Retrieval: curl of the IDEAS abstract page; regime/simon_wiggins_2001_ideas.html. Abstract only (Wiley
  full text not attempted beyond IDEAS; no open copy found in the searches).
- Mechanism: fear indicators (VIX, put-call ratio, TRIN) are contrarian: high fear predicts higher
  subsequent S&P futures returns.
- Products and horizon: S&P 500 futures; 10-, 20-, 30-day horizons.
- Sample window: January 1989 to June 1999.
- Market and data frequency: daily.
- Cost assumptions: not stated in the abstract.
- Quality tells: futures (not cash), out-of-sample simulation over the second half; horizons are multi-week.
- Verified passages:
  - P-K9R-003-a (Abstract): "This article investigates the predictive power of popular market‐based sentiment measures for subsequent returns on the Standard & Poor's (S&P) 500 futures contract over 10‐day, 20‐day, and 30‐day horizons from January 1989 through June 1999. These measures include the volatility index, the put–call ratio, and the trading index."
  - P-K9R-003-b (Abstract): "Finally, out‐of‐sample trading simulations performed over the second half of the sample period demonstrate that profits and risk‐adjusted profits would have been enhanced by buying S&P futures when the fear indicators were high rather than low."
- Numeric claims: none in the abstract.
- Conflicting evidence: K9R-005.
- Reader's note: Horizon (10-30 days) is longer than a K9 hold; a session hold would capture only a
  fraction. Supports the sign of K9R-001 (long after fear) in futures. Same X10/X14 notes.

### K9R-004 VIX futures term structure as a contrarian timing indicator (Fassas and Hourvouliades)

- Citation: Fassas, Athanasios P.; Hourvouliades, Nikolas (2019). "VIX Futures as a Market Timing
  Indicator." Journal of Risk and Financial Management 12(3), 113 (MDPI, open access) [DOI not captured;
  IDEAS handle RePEc:gam:jjrfmx:v:12:y:2019:i:3:p:113-:d:244838].
- Retrieval: curl from mdpi-res.com; regime/fassas_hourvouliades_2019_jrfm.pdf (+ .txt). Full text.
- Mechanism: when the VIX futures curve is in backwardation (fear priced at the front), subsequent S&P 500
  returns are positive (contrarian, volatility risk premium); contango carries no signal.
- Products and horizon: S&P 500 index; 1 day, 1 week, 1 month, 1 quarter.
- Sample window: 4 January 2010 to 29 December 2017.
- Market and data frequency: daily closes of spot VIX and the seven nearest VIX futures (CFE website).
- Cost assumptions: none.
- Quality tells: one-regressor dummy design, Newey-West errors, R2 0.009 at 1 day; overlapping returns at
  longer horizons; percentile bins are full-sample; one bull-market sample.
- Verified passages:
  - P-K9R-004-a (Sec. 4): "The coefficient of negative slope (Slope− t ) had a negative sign in all cases, and it was statistically significant in the three out of four time horizons under review (except the monthly horizon). This means that whenever the estimated VIX term structure took negative values (i.e., the VIX futures were in backwardation), the subsequent future return of S&P500 was positive."
  - P-K9R-004-b (Sec. 4): "On the contrary, the coefficient of the positive term structure (Slope+t) was not statistically significant in any instance, suggesting that when the VIX futures term structure was in contango (as it normally is), there was no meaningful market timing signal for S&P500 returns."
  - P-K9R-004-c (Table 2): "K = 1 day" row: "−0.0004 0.0245 −0.1687 *** 0.009 10.59 2.07".
  - P-K9R-004-d (Sec. 4): "the lower percentiles (D1–D4, which correspond to 5–20 percentiles) coefficients were statistically significant in all cases and had statistically higher coefficients compared to the respective higher percentile coefficients".
- Numeric claims: 1-day slope coefficient on backwardation -0.1687 (significant at 1%), adjusted R2
  0.009 (P-K9R-004-c); the bottom 20% of slope days carry the signal (P-K9R-004-d).
- Conflicting evidence: K9R-005 (Lubnau-Todorova report the opposite emphasis: low implied volatility
  followed by positive returns, in non-US markets).
- Reader's note: Condition "VIX curve slope in its bottom 20%" fires on about 20% of dates by construction,
  inside the band, and reads a volatility *state* (curve shape), not the sign of the last move, which is the
  cleaner side of the X10 borderline. Hold: 1 day measured close to close on the cash index (session hold
  fits). Sign: long equity. Data: needs daily VIX futures settlements (public CFE history, not held by the
  program; flag for E.11/E.12) and is a signal from another market's prices (X14 risk). Size: the
  coefficient is in return per unit of slope and is not convertible to ticks from the paper alone.

### K9R-005 The calm after the storm (Lubnau and Todorova)

- Citation: Lubnau, Thorben Manfred; Todorova, Neda (2015). "The calm after the storm: implied volatility
  and future stock index returns." European Journal of Finance 21(15), 1282-1296. DOI
  10.1080/1351847X.2014.935872.
- Retrieval: curl of the IDEAS page; regime/lubnau_todorova_2015_ideas.html. Abstract only.
- Mechanism: very low implied volatility is followed by positive index returns over weeks (contrary to the
  fear-gauge view).
- Products and horizon: five implied-volatility indices and their stock indices; 20, 40, 60 trading days.
- Sample window: January 2000 to October 2013.
- Market and data frequency: daily.
- Cost assumptions: "adjusted excess returns" (details not in abstract).
- Quality tells: bootstrap; significant only for Germany and Japan.
- Verified passages:
  - P-K9R-005-a (Abstract): "Contrary to previous research, very low volatility levels appear to be followed by significantly positive average returns over the next 20, 40 or 60 trading days."
  - P-K9R-005-b (Abstract): "The excess returns measured against a buy and hold benchmark are significant for the German and Japanese market when tested with a bootstrap methodology."
- Numeric claims: none in the abstract.
- Conflicting evidence: this source is itself the main conflict for K9R-002 to K9R-004.
- Reader's note: Context and conflict. Horizon 20-60 days, so not a session hold. Not significant for the
  US (by omission in the abstract). A low-volatility long would also be X-free but the source gives no
  session-scale evidence.

### K9R-006 Time-varying equity premia with a high-VIX threshold (Bansal and Stivers)

- Citation: Bansal, Naresh; Stivers, Chris T. (2023 working paper). "Time-varying Equity Premia with a
  High-VIX Threshold and Sentiment." SSRN 4477652.
- Retrieval: SSRN blocked (scrapling get and fetch returned 59 and 659 bytes). The abstract was read from a
  Quantpedia page that reproduces it: regime/bansal_stivers_quantpedia_pointer.md. Abstract only, via a
  pointer page (pointer quality; the lead should treat it as [abstract via secondary page]).
- Mechanism: equity premium jumps after VIX exceeds a high threshold near its 80th percentile (risk premium
  in stress states).
- Products and horizon: aggregate US stock market excess returns; 1, 3, 6, 12 months.
- Sample window: 1990 to 2022.
- Market and data frequency: monthly forecasting horizons.
- Cost assumptions: none.
- Verified passages:
  - P-K9R-006-a (abstract as reproduced): "Over the 1990 to 2022 period, we show that time-variation in the returns earned from equity-market exposure can be explained well with a simple specification, which predicts: (1) much higher excess returns after the implied volatility from equity-index options exceeds a high threshold at around its 80th percentile"
  - P-K9R-006-b (abstract as reproduced): "Comparatively, we show that the VIX-threshold in our specification outperforms other risk explanatory terms suggested by the literature; including the recent high-frequency realized volatility"
- Numeric claims: predictive R2 about 20% and 30% at 6 and 12 months (stated in the same abstract, not
  verified beyond the pointer page).
- Reader's note: Context only: monthly horizons, not session holds. Notable because the threshold near the
  80th percentile matches D-pct, and because the authors report that VIX beats recent realized volatility
  as the state variable (relevant if a member wanted an own-bar realized-volatility proxy to avoid X14).

### K9R-007 Market timing with daily VIX changes (Copeland and Copeland)

- Citation: Copeland, Maggie M.; Copeland, Thomas E. (1999). "Market Timing: Style and Size Rotation Using
  the VIX." Financial Analysts Journal 55(2), 73-81. DOI 10.2469/faj.v55.n2.2262.
- Retrieval: curl of the IDEAS page; regime/copeland_1999_ideas.html. Abstract only.
- Mechanism: daily VIX changes lead next-day relative returns: after VIX rises, large caps beat small caps
  and value beats growth.
- Products and horizon: style and size portfolios; next day.
- Sample window: not in the abstract.
- Verified passages:
  - P-K9R-007-a (Abstract): "On days that follow increases in the VIX, portfolios of large-capitalization stocks outperform portfolios of small-capitalization stocks and value-based portfolios outperform growth-based portfolios. On days following a decrease in the VIX, the opposites occur."
- Reader's note: Relative (long-short) effect; K9 allows one directional position per member, so it maps at
  most to "M2K weaker than MYM after VIX rises", which is not a single-product directional rule. Context.

### K9R-008 Volatility-managed portfolios (Moreira and Muir) [conflicting]

- Citation: Moreira, Alan; Muir, Tyler (2016). "Volatility Managed Portfolios." NBER Working Paper 22208.
  (Journal of Finance 2017, DOI not captured.)
- Retrieval: curl from nber.org; regime/moreira_muir_nber_w22208.pdf (+ .txt). Full text.
- Mechanism: expected returns do not rise in proportion to volatility, so taking less risk when recent
  realized volatility is high raises Sharpe ratios.
- Products and horizon: equity factors and the currency carry trade; monthly rebalancing on the previous
  month's realized variance.
- Sample window: not extracted (monthly, long US samples).
- Verified passages:
  - P-K9R-008-a (Abstract): "Volatility timing increases Sharpe ratios because changes in factor volatilities are not offset by proportional changes in expected returns."
  - P-K9R-008-b (Intro): "We construct portfolios that scale monthly returns by the inverse of their previous month's"
- Reader's note: Conflicting evidence for any "high realized volatility, so larger expected drift" member at
  the monthly scale: the expected return per unit of risk falls in high-volatility months. It does not test
  a one-day horizon after a spike, so it does not contradict K9R-001 directly, but it warns that the
  per-trade edge relative to the move (the eps arithmetic) does not grow with volatility.

### K9R-009 Evaporating liquidity (Nagel) [X10 context]

- Citation: Nagel, Stefan (2011). "Evaporating Liquidity." NBER Working Paper 17653. Published Review of
  Financial Studies (2012) [DOI not captured].
- Retrieval: curl from nber.org; regime/nagel_nber_w17653.pdf (+ .txt). Full text.
- Mechanism: returns to short-term reversal (liquidity provision) rise with VIX.
- Products and horizon: US stocks, cross-sectional daily reversal portfolios.
- Sample window: January 1998 to December 2010 (text: "The sample period runs from the beginning of 1998 to the end of December 2010.").
- Verified passages:
  - P-K9R-009-a (Abstract): "Analysis of reversal strategies shows that the expected return from liquidity provision is strongly time-varying and highly predictable with the VIX index. Expected returns and conditional Sharpe Ratios increase enormously along with the VIX during times of nancial market turmoil"
- Reader's note: The mechanism is a fade (X10) made stronger in high-VIX states, and cross-sectional.
  Logged because it is the main literature showing that "high-VIX next-day gains" can be liquidity-provision
  reversal rather than a pure uncertainty premium; that is the reading Task 4 must exclude for K9R-001.

### K9R-010 Carry trades and currency crashes (Brunnermeier, Nagel, Pedersen)

- Citation: Brunnermeier, Markus K.; Nagel, Stefan; Pedersen, Lasse H. (2008). "Carry Trades and Currency
  Crashes." NBER Working Paper 14473 (NBER Macroeconomics Annual 2008).
- Retrieval: curl from nber.org; regime/bnp_carry_nber_w14473.pdf (+ .txt). Full text.
- Mechanism: VIX increases coincide with carry unwinds (investment currencies fall, funding currencies
  rise); a high VIX level then predicts higher future carry returns (crash risk premium).
- Products and horizon: G10 currencies vs USD; weekly (1992-2006) and quarterly (1986-2006).
- Verified passages:
  - P-K9R-010-a (Intro): "a higher level of VIX predicts higher returns for investment currencies and lower returns for funding currencies, and controlling for VIX reduces the predictive coefficient for interest-rate differentials"
  - P-K9R-010-b (Intro): "We show that during weeks in which the VIX increases, the carry trade tends to incur losses."
- Reader's note: Directional for 6A, 6N (investment, long after high VIX) and 6J, 6S (funding, short) but
  at weekly and quarterly horizons; no session-scale evidence. X14 (VIX is an equity-option series read for
  FX). Context only.

### K9R-011 Flights to safety (Baele, Bekaert, Inghelbrecht, Wei)

- Citation: Baele, Lieven; Bekaert, Geert; Inghelbrecht, Koen; Wei, Min (2014). "Flights to Safety."
  Finance and Economics Discussion Series 2014-46, Federal Reserve Board.
- Retrieval: curl from federalreserve.gov; regime/feds_2014_46.pdf (+ .txt). Full text.
- Mechanism: flight-to-safety days (bonds up, stocks down) are rare and coincide with VIX increases; just
  after a spell, short-term reversals (stocks up, bonds down) appear.
- Products and horizon: equity and 10-year bond indices, 23 countries; daily.
- Sample window: January 1980 to January 2012 (country samples vary).
- Verified passages:
  - P-K9R-011-a (Abstract): "On average, FTS days comprise less than 3% of the sample, and bond returns exceed equity returns by 2.5 to 4%."
  - P-K9R-011-b (Sec. 3): "Interestingly, one day before and one day after a FTS spell, equity returns are solidly positive and bond returns negative, leading to strong positive return impact just before and after a FTS spell. While this seems puzzling at first, it is entirely driven by FTS events identified by the ordinal method."
  - P-K9R-011-c (Sec. 3): "A plausible hypothesis is that these events reflect reversals during stressful times."
- Reader's note: Contemporaneous classification; the post-spell effect is a reversal (X10) and the authors
  attribute it to the identification method (P-K9R-011-b). FTS days are under 3% of dates (too rare).
  Conflicting/context for any "bonds after an equity-volatility spike" member (ZN, ZB, UB).

### K9R-012 Feedback traders and autocorrelation by volatility state (Sentana and Wadhwani)

- Citation: Sentana, Enrique; Wadhwani, Sushil B. (1992). "Feedback Traders and Stock Return
  Autocorrelations: Evidence from a Century of Daily Data." Economic Journal 102(411), 415-425. DOI
  10.2307/2234525.
- Retrieval: curl of IDEAS page; regime/sentana_wadhwani_1992_ideas.html (also regime/abs_sentana_wadhwani.json
  from OpenAlex, truncated). Abstract only.
- Mechanism: positive feedback trading makes daily index returns positively autocorrelated in calm states
  and negatively autocorrelated in volatile states.
- Products and horizon: US stock index; daily and hourly.
- Sample window: about a century of daily data (exact dates not in the abstract).
- Verified passages:
  - P-K9R-012-a (Abstract): "The authors' results indicate that when volatility is low, daily (and hourly) stock returns exhibit positive autocorrelation, but when it is high, returns exhibit negative serial correlation. They also find an important asymmetry--negative serial correlation is more likely after price declines."
  - P-K9R-012-b (Abstract): "The authors also find no significant relation between margin requirements and the autocorrelation of returns."
- Reader's note: Supplies a state-dependent sign: continuation of the prior day in low-volatility states
  (R3-adjacent, not a fade, and not X3 because the sign comes from the prior return, not the close's place
  in the range), reversal in high-volatility states (X10). Cash index data with nonsynchronous trading;
  see K9R-014 for the futures evidence that the daily effect has nearly gone. P-K9R-012-b is conflicting
  evidence for a margin-driven mechanism in R2.

### K9R-013 Volatility and serial correlation (LeBaron)

- Citation: LeBaron, Blake (1992). "Some Relations Between Volatility and Serial Correlations in Stock
  Market Returns." Journal of Business 65(2), 199-219. DOI 10.1086/296565.
- Retrieval: OpenAlex API record; regime/abs_lebaron1992.json. Abstract only.
- Verified passages:
  - P-K9R-013-a (Abstract): "It is found that serial correlations are changing over time and are related to stock return volatility."
- Reader's note: The founding "LeBaron effect" source (autocorrelation falls as volatility rises); no sign
  or magnitude in the abstract. Context for K9R-012 and K9R-014.

### K9R-014 Intraday LeBaron effects in S&P 500 futures (Bianco, Corsi, Renò) [conflicting]

- Citation: Bianco, Simone; Corsi, Fulvio; Renò, Roberto (2009). "Intraday LeBaron effects." PNAS 106(28),
  11439-11443. DOI 10.1073/pnas.0901165106.
- Retrieval: curl from scholarworks.wm.edu; regime/bianco_corsi_reno_2009_pnas.pdf (+ .txt). Full text.
- Mechanism: serial correlation falls when forecast volatility is high; at the daily level the effect has
  attenuated; intraday it persists.
- Products and horizon: S&P 500 index futures; daily close-to-close and 5-minute returns.
- Sample window: 1993 to 2007, 4,344 days.
- Market and data frequency: futures tick data on a 5-minute grid.
- Verified passages:
  - P-K9R-014-a (Abstract): "After finding a significant attenuation of the original effect over time, we show that a similar but more pronounced effect holds by using intraday measures"
  - P-K9R-014-b (Results): "serial correlation has almost disappeared, the AR(1) coefficient of Rt being just −0.0276, whereas the mean value found by LeBaron in the period 1928–1990 was 0.0618."
  - P-K9R-014-c (Abstract): "We find that intraday serial correlation is negatively correlated to volatility forecasts, whereas it is positively correlated to unexpected volatility."
- Numeric claims: daily AR(1) of ES returns 1993-2007 = -0.0276 vs 0.0618 in LeBaron's 1928-1990 sample
  (P-K9R-014-b).
- Reader's note: Main conflicting evidence for any daily "continuation in calm states" member built on
  K9R-012/013 in equity index futures. Also a caution for K9R-001: in futures the daily-scale
  volatility-autocorrelation link is weak after 1993.

### K9R-015 Trading volume and serial correlation (Campbell, Grossman, Wang)

- Citation: Campbell, John Y.; Grossman, Sanford J.; Wang, Jiang (1993). "Trading Volume and Serial
  Correlation in Stock Returns." Quarterly Journal of Economics 108(4), 905-939.
- Retrieval: curl from dash.harvard.edu; regime/campbell_grossman_wang_1993.pdf (+ .txt). Full text.
- Mechanism: price moves on high volume reflect liquidity demand absorbed by risk-averse market makers and
  tend to reverse; moves on low volume reflect public information and reverse less.
- Products and horizon: CRSP value-weighted NYSE/AMEX index and large stocks; daily.
- Sample window: 7/3/62 to 12/30/88; main sample 7/3/62 to 9/30/87.
- Verified passages:
  - P-K9R-015-a (Abstract): "For both stock indexes and individual large stocks, the first-order daily return autocorrelation tends to decline with volume."
  - P-K9R-015-b (Sec. I): "Thus, the model with heterogeneous investors suggests that price changes accompanied by high volume will tend to be reversed; this will be less true of price changes on days with low volume."
- Reader's note: R2 mechanism split: high-volume large moves reverse (X10); low-volume moves do not reverse,
  which is "less reversal", not demonstrated continuation. Cash-index nonsynchronous trading inflates
  positive autocorrelation (the paper's own caveat area). Context; no session-scale candidate on its own.

---

## R2. Session drift after a large prior-day move (not a fade)

### K9R-016 Momentum after one-day abnormal returns in cryptocurrencies (Caporale and Plastun)

- Citation: Caporale, Guglielmo Maria; Plastun, Alex (2019 working paper; 2020 journal). "Momentum effects
  in the cryptocurrency market after one-day abnormal returns." Brunel Economics and Finance Working Paper
  1917 (October 2019); Financial Markets and Portfolio Management 34, 251-266 (2020), DOI
  10.1007/s11408-020-00357-1 (DOI from the search-result link, journal page not fetched).
- Retrieval: curl from brunel.ac.uk; regime/caporale_plastun_2019_crypto_momentum.pdf (+ .txt). Full text.
- Mechanism: on a day with an abnormal return (beyond mean + k standard deviations) prices keep moving in
  that direction until the close; the next day shows momentum or reversal depending on the coin and sign.
- Products and horizon: BTCUSD, ETHUSD, LTCUSD spot (CoinMarketCap); same day and next day, hourly.
- Sample window: the abstract says 01.01.2017-01.09.2019, the data section says 01.01.2015-01.09.2019
  (internal inconsistency).
- Market and data frequency: daily and hourly spot.
- Cost assumptions: none; the paper says costs are small.
- Quality tells: "Strategy 1" trades on the abnormal day after it is detected intraday but classifies the
  day using its full-day return (selection on the outcome), so its high t-stats are not tradable evidence;
  "Strategy 2" (next day) is the tradable test; k chosen per coin "to generate ... a sufficient number of
  overreactions"; no costs; spot data.
- Verified passages:
  - P-K9R-016-a (Sec. 3): "Concerning price behaviour on the day after overreactions, average hourly BTCUSD returns after a positive overreaction are much lower than on normal days during the first hours of the following day (Figure B.1), and these differences are statistically significant (Table B.1), which implies the existence of a contrarian effect. As for negative overreactions, on the following day prices tend to move in the direction of the overreaction (Figure B.2 and Table B.2), which represents evidence of a momentum effect."
  - P-K9R-016-b (Table 5, Strategy 2): "BTCUSD* 49 29 59.2% 75.3% 15.06% 1.54% 1.75 rejected" with "not" on the line above, i.e. "not rejected" (* = contrarian strategy).
  - P-K9R-016-c (Table 6, Strategy 2): "BTCUSD 46 25 54.3% 52.0% 10.4% 1.13% 1.55" with "not rejected".
  - P-K9R-016-d (Sec. 2): "k=2 for BTCUSD and k=1.5 for ETHUSD and LTCUSD, k being chosen on the basis of the sample size to generate in each case a sufficient number of overreactions"
- Numeric claims: next-day BTC: after positive abnormal days, contrarian 1.54% per trade, t 1.75, null not
  rejected, 49 trades (P-K9R-016-b); after negative abnormal days, momentum 1.13% per trade, t 1.55, null
  not rejected, 46 trades (P-K9R-016-c).
- Conflicting evidence: within the paper, BTC next-day effects split in sign and are insignificant.
- Reader's note: For MBT, the tradable next-day test fails significance in both directions, and the
  positive-side effect is a fade (X10). 95 trades in about 2.7-4.7 years is f about 0.06-0.10 (below or at
  the floor). Non-survivor for K9 purposes.

### K9R-017 Gold and oil after abnormal-return days (Caporale and Plastun) [E.0 K5-028]

- Citation: Caporale, Guglielmo Maria; Plastun, Alex (2021). "Gold and oil prices: abnormal returns,
  momentum and contrarian effects." Financial Markets and Portfolio Management 35, 353-368. DOI
  10.1007/s11408-021-00380-w. E.0 id: K5-028.
- Retrieval: curl from bura.brunel.ac.uk (author accepted version, journal pagination); CESifo copy blocked
  by a client challenge; regime/caporale_plastun_2020_gold_oil_brunel.pdf (+ .txt). Full text.
- Mechanism: abnormal-return days continue intraday; next day oil continues (momentum), gold reverses.
- Products and horizon: gold and oil prices (MetaQuotes data, GMT+3); same day and next day, hourly.
- Sample window: 01.01.2009 to 31.03.2020.
- Cost assumptions: none ("the spread is only 0.02% per trade" for gold).
- Quality tells: CFD-style data, not exchange futures; same Strategy 1 selection problem as K9R-016; k = 2
  standard deviations; Strategy 2 for oil is the only significant next-day result.
- Verified passages:
  - P-K9R-017-a (Abstract): "On the following day two different price patterns are detected: a momentum effect for oil prices and a con- trarian effect for gold prices, respectively."
  - P-K9R-017-b (Table 3, Strategy 2): "Oil 81 50 62 56.42 5.64 0.70 3.89 Rejected" and "Golda 59 35 59 4.26 0.43 0.07 1.36 Not rejected".
  - P-K9R-017-c (Table 4, Strategy 2): "Oil 83 49 59.0 49.9 5.0 0.60 2.12 Rejected" and "Gold* 74 43 58.1 11.3 1.1 0.15 0.73 Not rejected".
  - P-K9R-017-d (Sec. 3): "The CAR analy- sis shows that the momentum effect is temporary (Figs. D.1, D.2): usually it lasts for a few hours ... The biggest momentum effects are observed at 9 a.m. for positive abnormal returns and at 10 a.m. for negative ones (Table D.3)."
  - P-K9R-017-e (Sec. 2): "Our analysis does not incorporate transaction costs (spreads, broker or bank fees, swaps etc.), and therefore it is only a proxy for actual trading."
- Numeric claims: oil, next day in the direction of the abnormal day: 0.70% per trade (81 trades, t 3.89)
  after positive days; 0.60% per trade (83 trades, t 2.12) after negative days (P-K9R-017-b, -c). Gold
  contrarian next day: 0.07% and 0.15% per trade, not significant.
- Conflicting evidence: gold (same paper) reverses; K9R-018 shows the same authors' "inertia" measure is a
  favourable-excursion measure, not a close-to-close return; K9R-020 finds no continuation after large
  non-limit moves in agricultural futures; K9R-021 finds weak reversal after large one-day moves in 26
  commodity futures.
- Reader's note: Candidate for MCL: condition = prior day's return beyond mean + 2 SD (both signs), hold the
  next trade date from the open with exit by the source's timing (peak 9-10 a.m. GMT+3, i.e. early in the
  CT night; the paper's Strategy 2 exit uses its timing parameters), sign = with the prior day. Frequency:
  164 trades in about 11.25 years is about 15 a year (f about 0.06), below the 10% floor at k = 2; the
  D-pct 80/20 definition would fire on about 40% of days but is a different, untested condition (it would
  be a parameter change, not the source's rule). X10 not hit (continuation). Borderline with X11 only if
  keyed to limits (it is not). Size: 0.60-0.70% per trade vs crude's mean absolute daily move (roughly
  1.5-2% in 2009-2020, my reading) is about 0.3-0.45 x E|m1|; MCL G(0.1) is about 2.3 x E|m1| by the
  design table's own ratios, so far short; clears M_X (about 0.14 x E|m1|). Data quality (non-exchange
  feed, GMT+3 day boundary) is a serious caveat.

### K9R-018 Short-term price overreactions: "inertia anomaly" (Caporale, Gil-Alana, Plastun)

- Citation: Caporale, Guglielmo Maria; Gil-Alana, Luis; Plastun, Alex (2014). "Short-Term Price
  Overreactions: Identification, Testing, Exploitation." DIW Berlin Discussion Paper 1423 (October 2014).
  A journal version exists (abstract page saved; venue not verified).
- Retrieval: curl from diw.de (full text) and from mev.biem.sumdu.edu.ua (one-page abstract);
  regime/caporale_gilalana_plastun_diw_dp1423.pdf (+ .txt), regime/caporale_gilalana_plastun_2018_abstract.pdf
  (+ .txt). Full text.
- Mechanism (as claimed): after an "overreaction day", prices keep moving in the same direction the next
  day ("inertia anomaly"); counter-movement strategies fail in FX and commodities.
- Products and horizon: Dow Jones index and stocks, EURUSD, USDJPY, GBPCHF, AUDUSD, gold, oil; next day.
- Sample window: January 2002 to end of September 2014 (trading-robot tests 2012-2014, parameters fitted
  on 2013).
- Quality tells (decisive): the "overreaction" and the "return" are both defined on the daily range, not on
  close-to-close returns, and the next-day "movement in the direction of the overreaction" is the
  favourable excursion (High - Open)/Open. The test therefore measures whether next-day ranges are larger
  after large-range days (volatility clustering), not whether the close moves in the same direction.
  Trading-robot parameters were optimised on 2013 and the authors note in a footnote that changing
  parameters can make a strategy profitable only for the data set used.
- Verified passages:
  - P-K9R-018-a (Sec. 3): "In our opinion the daily return, i.e. the difference between the maximum and minimum prices during the day, is more appropriate. This is calculated as: ( Highi − Lowi ) ... Lowi"
  - P-K9R-018-b (Sec. 3): "In the case of Hypothesis 2 (movement in the direction of the overreaction), either equation (8) or (7) is used depending on whether the price has increased or decreased." (Equation (8) in the extracted text is 100% x ( Highi + 1 − Openi + 1 ) divided by Openi + 1, i.e. the next day's favourable excursion from the open; the layout of the formula is reconstructed, the words are verbatim.)
  - P-K9R-018-c (Table 9): "Number of matches 536 2637 517 2656" and "Mean 0,87% 0,79% 1,57% 1,42%" (gold abnormal/normal, oil abnormal/normal, averaging period 20).
  - P-K9R-018-d (footnote 1): "By changing the values of various parameters of the trading strategy one can make it profitable, but this would work only for the specific data set being used, not in general."
- Numeric claims: abnormal (range) days are 536 of 3,173 gold days and 517 of 3,173 oil days (about 16%)
  (P-K9R-018-c); next-day favourable excursion 0.87% vs 0.79% (gold), 1.57% vs 1.42% (oil).
- Reader's note: Non-survivor as directional evidence. The "inertia" is about range (R3-type expansion
  persistence), measured with an excursion that is always positive by construction, so it carries no
  direction for a market-order, no-target K9 hold. Its value to K9 is negative: it shows that the
  Caporale-Plastun "momentum" family partly rests on favourable-excursion measures. K9R-017 uses
  close-based hourly CAR and trade simulations with timing exits, so it is less affected, but its exits
  are fitted timing parameters.

### K9R-019 Overreaction and continuation in 39 national stock indices (Joseph and Mazouz)

- Citation: Joseph, Nathan Lael; Mazouz, Khelifa (2010). "Testing for Overreaction and Return
  Continuations in Stock Price Index Returns." International Journal of Strategic Decision Sciences 1(2),
  93-112. DOI 10.4018/jsds.2010040105.
- Retrieval: scrapling extract get of the Coventry repository page; regime/joseph_mazouz_2010_coventry.md.
  Abstract only.
- Mechanism: moderate index shocks continue the next day; large negative shocks reverse; large positive
  shocks are followed by nothing.
- Products and horizon: 39 national stock indices; day-one cumulative abnormal return after the shock.
- Sample window: not in the abstract.
- Verified passages:
  - P-K9R-019-a (Abstract): "Whilst the market is efficient when the positive shocks are large, the market also over-reacts when negative shocks are large. To illustrate, for large stock markets that are more liquid, positive shocks of more than 5% generate an insignificant day one CAR of -0.004%, whilst negative shocks of more than 5% generate a positive and significant day one CAR of 0.662%. In contrast, positive (negative) shocks of less than 5% generate a significant one day CAR of 0.119% (-0.174%) for these same (large) stock markets."
- Numeric claims: shocks under 5% in large markets: next-day CAR +0.119% after up shocks and -0.174%
  after down shocks, both significant; down shocks over 5%: +0.662% (reversal) (P-K9R-019-a).
- Reader's note: Supports a with-the-move (continuation) next-day drift for moderate shocks in large, liquid
  index markets: condition "prior day's index move beyond a shock threshold but under 5%", hold next day,
  sign with the shock. The large-negative-shock arm is X10. Shock threshold and sample are not in the
  abstract, so frequency cannot be set from the source (D-pct would be the design default). Weak journal;
  cash indices, nonsynchronous trading may inflate continuation (see K9R-014). Size about 0.12-0.17% vs a
  mean absolute index day of about 0.7-1% is about 0.15-0.25 x E|m1|: clears M_X for MNQ/M2K/MYM, far
  below G(0.2).

### K9R-020 Commodity price limits (Janardanan, Qiao, Rouwenhorst) [X11; conflicting for R2]

- Citation: Janardanan, Rajkumar; Qiao, Xiao; Rouwenhorst, K. Geert (2017). "On Commodity Price Limits."
  Working paper, SummerHaven Investment Management and Yale SOM (February 2017).
- Retrieval: curl from ou.edu (energy finance conference); regime/janardanan_limits.pdf (+ .txt). Full text.
- Mechanism: price limits delay price discovery, so returns continue after limit days; large moves that do
  not hit the limit show no continuation.
- Products and horizon: soybean oil, corn, cotton, feeder cattle, live cattle, lean hogs, soybeans, wheat
  (nine commodities named as such in the text); next day to one week.
- Sample window: 01/07/1991 to 05/23/2016.
- Verified passages:
  - P-K9R-020-a (Abstract): "Consistent with delayed price discovery, returns continue in the same direction after limit days and do not reverse after one week, whereas returns are small after large price moves that do not hit limits."
  - P-K9R-020-b (Intro): "When we compare our findings to the day after large price moves between 90% and 100% of the limit size, we do not find any return continuation. Average returns after 90% limit days are virtually zero for both positive and negative moves. These large average returns after limits are not driven by the large price moves, but rather are associated with limits themselves."
- Numeric claims: next-day return after limit-down days -38 to -63 bps (Intro, lines quoted in file
  "for limit down days, the average return on the following day is -38 to -63 basis points"); after
  90-100%-of-limit moves, virtually zero (P-K9R-020-b).
- Reader's note: The continuation is X11 (limit-keyed, already tested as K6-limitcont). Its control
  (large moves short of the limit) is the strongest direct evidence against a generic "large prior-day move
  continues" member in ZC, ZW, ZS, ZL, HE, LE. Key conflicting source for R2.

### K9R-021 Large one-day commodity futures price changes (Hua and Wei)

- Citation: Hua, Wei; Wei, Peihwang (2014). "Analysing large one-day commodity futures price changes."
  International Journal of Bonds and Derivatives. DOI 10.1504/ijbd.2014.067401.
- Retrieval: OpenAlex API record; regime/abs_large_oneday_commodity.json (Hull repository copy returned
  403). Abstract only.
- Verified passages:
  - P-K9R-021-a (Abstract): "This paper analyses large one-day price changes in 26 US commodity futures"
  - P-K9R-021-b (Abstract): "Subsequent to large price changes, we find a tendency for reversal, but the magnitude of reversal is not strong and can be explained by the market factor."
- Reader's note: Conflicting for R2 continuation in commodity futures (26 contracts); the weak reversal
  would be X10 anyway. No sample window in the abstract.

### K9R-022 Trends, reversion and critical trend strength (Schmidhuber)

- Citation: Schmidhuber, Christof (2020). "Trends, Reversion, and Critical Phenomena in Financial Markets."
  arXiv:2006.07847v4 (11 December 2020).
- Retrieval: curl from arxiv.org; regime/schmidhuber_arxiv2006.07847.pdf (+ .txt). Full text.
- Mechanism: next-day return is a cubic in trend strength: moderate trends persist (linear term), strong
  trends revert (cubic term); the cross-over is below a trend strength (t-stat) of 2.
- Products and horizon: 24 futures (equity indices, rates, currencies, commodities); next day, trend
  horizons from days to years.
- Sample window: 1990 to Dec 31, 2019 (first two years used for warm-up).
- Verified passages:
  - P-K9R-022-a (Abstract): "Our key observation is that tomorrow's expected return follows a cubic polynomial of to- day's trend strength. The positive linear term of this polynomial represents trend persistence, while its negative cubic term represents trend reversal."
  - P-K9R-022-b (Sec. 3): "Our analysis quantifies where exactly this happens: below a critical trend strength of 2, before trends become strongly statistically significant."
  - P-K9R-022-c (Table 3): "b 1.29% ±0.43% 3.0" and "c −0.62% ±0.23% 2.7"; "R2 1.31 bp 4.91 bp".
- Numeric claims: linear coefficient 1.29% (t 3.0), cubic -0.62% (t 2.7), R2 1.31 bp single scale
  (P-K9R-022-c); returns are normalised by volatility, so 1.29% means about 0.013 daily standard
  deviations per unit of trend strength.
- Reader's note: Pooled across 24 futures; the effect per trade is about 1% of a daily standard deviation,
  far below M_X on every exposure. The persistence part is daily-scale TSMOM (routed to the Overnight
  reader); the reversion part is X10. Conflicting for R2: a "large move" in trend terms predicts reversal,
  not continuation.

### K9R-023 Margin changes do not move futures prices (Hedegaard, AQR summary)

- Citation: Hedegaard, Esben (working paper; AQR library page). "Causes and Consequences of Margin Levels
  in Futures Markets." Data: 16 commodity futures, 2000-2011, margins obtained by FOIA request.
- Retrieval: scrapling extract get of aqr.com library page; regime/hedegaard_aqr_margins.md. Summary page
  only (written by AQR, not the paper's abstract).
- Verified passages:
  - P-K9R-023-a (summary page): "Contrary to conventional wisdom and prior research by others, the author failed to find evidence that margin changes affect futures prices, even when controlling for speculator positions."
  - P-K9R-023-b (summary page): "However, margin increases do affect realized volatility, which increases by about 50% on average on the day of a margin increase."
- Reader's note: Conflicting for the "margin-driven deleveraging gives next-day drift" mechanism in R2.

### K9R-024 Determinants of CME margin changes (Abruzzo and Park)

- Citation: Abruzzo, Nicole; Park, Yang-Ho (2014). "An Empirical Analysis of Futures Margin Changes:
  Determinants and Policy Implications." Finance and Economics Discussion Series 2014-86, Federal Reserve
  Board.
- Retrieval: curl from federalreserve.gov (fedinprint copy failed); regime/feds_2014_86_margins.pdf (+ .txt).
  Full text.
- Verified passages:
  - P-K9R-024-a (Abstract): "We first find that CME Group raises margins quickly following volatility spikes but does not immediately lower margins following volatility de- clines, implying that margin-induced procyclicality is more of a concern in recessions than in expansions."
  - P-K9R-024-b (Sec. 5.2): "we find that changes in futures prices have no statistically significant relation to margin changes for many of the futures contracts"
- Reader's note: Context only: establishes that margin increases follow volatility spikes (the
  precondition for deleveraging) with sample ending July 31, 2013; it does not test subsequent returns.
  With K9R-023 and P-K9R-012-b, no source located supports a directional margin-deleveraging drift.

---

## R3. Range compression and expansion

### K9R-025 Candlestick technical trading strategies (Marshall, thesis) [conflicting]

- Citation: Marshall, Benjamin Richard (2005). "Candlestick Technical Trading Strategies: Can They Create
  Value for Investors?" PhD thesis, Massey University (basis of Marshall, Young and Rose 2006, Journal of
  Banking and Finance).
- Retrieval: curl from mro.massey.ac.nz; regime/marshall_young_rose_massey.pdf (+ .txt). Full text of the
  front matter and abstract (the extracted text is 673 lines; pattern-level tables were not in the
  extracted text, so the harami/inside-day rows could not be checked).
- Verified passages:
  - P-K9R-025-a (Abstract): "the tests in this thesis, using Dow Jones Industrial Index (DHA) component stock data for the 1 992 - 2002 period, are clearly out of sample tests."
  - P-K9R-025-b (Abstract): "Using an innovative extension of the bootstrap methodology, which allows the generation of random open, high, low and close prices, to test the profitability of candlestick technical trading strategies showed that candlestick technical analysis does not have value."
- Reader's note: The closest academic test of open-high-low-close bar patterns (which include inside-day
  type patterns) finds no value, in US large stocks, with holds of up to ten days. Conflicting evidence for
  any R3 pattern member. Not futures.

R3 summary: no academic or working-paper source was found that tests the *direction* of the session after
a narrow-range or inside day in futures. Practitioner pointers only (not evidence): Crabel, T. (1989)
"Inside day patterns in the S&P", Technical Analysis of Stocks & Commodities V.7:11 (paywalled store page in
search results); Crabel (1990) book; Bulkowski pattern statistics. The design target's borderline rule
(direction must come from a separate mechanism) cannot be met from this literature. The only
range-related academic evidence found is about magnitude: large-range days are followed by larger next-day
ranges (K9R-018's own data, P-K9R-018-c), i.e. volatility clustering, which gives no sign.

---

## Fetch log

All times UTC. sha256 is of the raw saved file. Rows marked "removed" were fetched, found to be a block page
or off-target, and deleted; they are kept here for the record. Search-record JSON files under api/ are not
listed (they are search records, not evidence).

| File | URL | UTC fetch time | sha256 | bytes | tool | status |
|---|---|---|---|---|---|---|
| caporale_plastun_2019_crypto_momentum.pdf | https://www.brunel.ac.uk/economics-finance-and-accounting/research/pdf/1917-Oct-GMC-Momentum-effect-in-the-Cryptocurrency-Market-after-One-day-Abnormal-Returns.pdf | 2026-10-03T05:34:39Z | 181aac5d468f16b7650a68344a445e96ecfbc52f3a3619a02d72e91012262801 | 1494763 | curl (http=200) | kept |
| efma2009_0102.pdf | https://efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2009-Milan/papers/EFMA2009_0102_fullpaper.pdf | 2026-10-03T05:34:42Z | - | - | curl (http=000) | removed (block page, failure or off-target) |
| caporale_plastun_2020_gold_oil_cesifo8445.pdf | https://cesifo.org/DocDL/cesifo1_wp8445.pdf | 2026-10-03T05:35:02Z | 32ed63159c77e21ee19ca1b9aa3213ccf0218eb59539560b132a8e68ef0e18ea | 3038 | curl (http=200) | removed (block page, failure or off-target) |
| caporale_gilalana_plastun_cesifo5066.pdf | https://cesifo.org/DocDL/cesifo1_wp5066.pdf | 2026-10-03T05:35:02Z | 32ed63159c77e21ee19ca1b9aa3213ccf0218eb59539560b132a8e68ef0e18ea | 3038 | curl (http=200) | removed (block page, failure or off-target) |
| campbell_grossman_wang_1993.pdf | https://dash.harvard.edu/bitstream/1/3128710/2/campbell_trading.pdf | 2026-10-03T05:35:03Z | f2955158df1350db965dafb40cb8a8adda76fba9650083dd931a529655ee215a | 1585781 | curl (http=200) | kept |
| caporale_plastun_2020_gold_oil_brunel.pdf | https://bura.brunel.ac.uk/bitstream/2438/21825/6/FullText.pdf | 2026-10-03T05:35:09Z | 1f5d5cfb56cd1b6d8ece1870ed33b160b26503e24f593a3b791e90435a55427d | 692210 | curl (http=200) | kept |
| hu_pan_wang_zhu_nber_w25817.pdf | http://www.nber.org/papers/w25817.pdf | 2026-10-03T05:35:46Z | 3c66010b1582e55b9f5722f162003baa761e1c872b76cc47ced6f1588c3e3ae4 | 634417 | curl (http=200) | kept |
| simon_wiggins_2001_ideas.html | https://ideas.repec.org/a/wly/jfutmk/v21y2001i5p447-462.html | 2026-10-03T05:35:48Z | 0d119b47c831a530d48b4440d0feb8222ed76de89fee42f67fa15787f0197f4e | 31669 | curl (http=200) | kept |
| wang_yu_2004_ideas.html | https://ideas.repec.org/a/eee/jbfina/v28y2004i6p1337-1361.html | 2026-10-03T05:35:48Z | 6ba604aa20f87e64a8de3a8ea03a537c3a579d9c277a60c5d022d1483e8b0fb8 | 49026 | curl (http=200) | kept |
| fassas_hourvouliades_2019_jrfm.pdf | https://mdpi-res.com/d_attachment/jrfm/jrfm-12-00113/article_deploy/jrfm-12-00113-v2.pdf | 2026-10-03T05:36:25Z | a2f473f420c2a162de1864b5e9ad1ec5d0188610ff1eb3a457cad3c75b61b478 | 454269 | curl (http=200) | kept |
| connolly_stivers_sun_nber2004.pdf | https://users.nber.org/~confer/2004/URCf04subs/connolly.pdf | 2026-10-03T05:36:25Z | c69cd6d967108697f1927a30dfc6133c91a2a584bccef5a0c7379d7c83c28bbe | 917179 | curl (http=200) | kept |
| nagel_nber_w17653.pdf | https://www.nber.org/papers/w17653.pdf | 2026-10-03T05:36:27Z | 88f670eafd30c0396018bca55bf90fc050378d23d4d2518dc57421e7248a5294 | 449659 | curl (http=200) | kept |
| connolly_stivers_sun_atlfed_wp0203a.pdf | https://www.atlantafed.org/-/media/documents/research/publications/wp/2002/wp0203a.pdf | 2026-10-03T05:36:46Z | 4d228b5fc1e5f0e37d5387c3e2d25637c7187c9aa4fb498323224069957958b5 | 48165 | curl (http=200) | removed (block page, failure or off-target) |
| giot_uclouvain.pdf | https://research.dial.uclouvain.be/bitstreams/995d05e0-4d85-40d7-8ea7-3391a0e4365e/download | 2026-10-03T05:37:11Z | 1133a42b811217be07ebfd9d0bf04bd8685bfab556e3600bc604c652493a301f | 5499183 | curl (http=200) | kept |
| wallmeier_efma2008.pdf | https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2008-Athens/papers/Wallmeier.pdf | 2026-10-03T05:37:16Z | - | - | curl (http=000) | removed (block page, failure or off-target) |
| moreira_muir_nber_w22208.pdf | https://www.nber.org/papers/w22208.pdf | 2026-10-03T05:37:45Z | be1ea92102e1394e9ddec9545489902f45e5a07b42bd4c42faf8ee372e99fa7a | 1013730 | curl (http=200) | kept |
| banerjee_doran_peterson_fsu.pdf | https://its.fsu.edu/content/download/41618/268931/file | 2026-10-03T05:37:56Z | 0abe8c116f9ecab9a82ad2dfb9071805875b67058eb803d336a74c255ae3cfa8 | 55212 | curl (http=404) | removed (block page, failure or off-target) |
| bnp_carry_nber_w14473.pdf | https://www.nber.org/papers/w14473.pdf | 2026-10-03T05:37:57Z | f6ca74e323dfe2472857c4cacda49d19caffa7c182695131b7ed6dc1b5eb0942 | 260385 | curl (http=200) | kept |
| wang_yu_2004_jbf.pdf | http://tcnh.ntt.edu.vn/images/futures/6.pdf | 2026-10-03T05:39:10Z | b472fa8f7dd3386c7b9ed7ba8f3d28a1b202048ffb1cad2f8071ba4843197c23 | 60412 | curl (http=200) | removed (block page, failure or off-target) |
| janardanan_limits.pdf | https://www.ou.edu/content/dam/price/Finance/energyfinanceconference/papers/Janardanan-et-al-Limits%20Paper.pdf | 2026-10-03T05:39:12Z | f8a3ed6596667a3d37fd17cc879f7b594bd91242b743a34829f602a3d1ec28fc | 783644 | curl (http=200) | kept |
| hull_371741.pdf | https://hull-repository.worktribe.com/OutputFile/371741 | 2026-10-03T05:39:13Z | ca145b2ab1edeafc166fe23f8fcf1f4c38e494c31a1215984d2452d737c4e12b | 5663 | curl (http=403) | removed (block page, failure or off-target) |
| fed_feds2014_86_margins.pdf | https://fedinprint.org/item/fedgfe/35436/original | 2026-10-03T05:39:13Z | - | - | curl (http=000) | removed (block page, failure or off-target) |
| schmidhuber_arxiv2006.07847.pdf | https://arxiv.org/pdf/2006.07847 | 2026-10-03T05:39:13Z | 9d46b273053d2409cafe9b2a9f7973ae1ab66d25f104c00633aa3161e1dabe9a | 936603 | curl (http=200) | kept |
| abs_wang_yu_2004.json | https://api.openalex.org/works?filter=title.search:Trading%20activity%20and%20price%20reversals%20in%20futures%20markets&per-page=1 | 2026-10-03T05:39:45Z | 873663d82a331a985dc1e0f146ed50c519625035242df891c5459772f7031209 | 14705 | curl(OpenAlex API) (abstract) | kept |
| feds_2014_46.pdf | https://www.federalreserve.gov/pubs/feds/2014/201446/201446pap.pdf | 2026-10-03T05:40:10Z | efa5c3bc700d06adcf466005dfec1c40ca3edfbe9401dffcd1bd52b115c036d3 | 612055 | curl (http=200) | kept |
| farmdoc_confp14-08.pdf | https://farmdoc.illinois.edu/assets/meetings/nccc134/conf_2008/pdf/confp14-08.pdf | 2026-10-03T05:40:35Z | 8e5d8ecc9ab21c2c3907843a5c2dd9107c59579cd6afdffa4e0beb6381a30b45 | 457560 | curl (http=200) | kept |
| marshall_cahan_2008_ideas.html | https://ideas.repec.org/a/eee/jbfina/v32y2008i9p1810-1819.html | 2026-10-03T05:40:35Z | 9e040c335192440bb2464de2f4bfdcf99a49e33fc0c5481795aed5244a80eb13 | 49764 | curl (http=200) | kept |
| abs_marshall_2008.json | https://api.openalex.org/works?filter=title.search:Can%20commodity%20futures%20be%20profitably%20traded%20with%20quantitative%20market%20timing%20strategies&per-page=1 | 2026-10-03T05:40:44Z | 89c4824c6c29ca46f32c48cafad6eff2d37035d983143324ed7eda940368b63b | 13829 | curl(OpenAlex API) (abstract) | kept |
| marshall_young_rose_massey.pdf | https://mro.massey.ac.nz/bitstreams/7afc8049-23a1-4fe9-ac3a-792d6403ef1c/download | 2026-10-03T05:41:21Z | 2e003df6c20fc9b2af4b8b06cb8b4d2a635265d73aa32e50ffa2057fd1cb48e8 | 460880 | curl (http=200) | kept |
| bianco_corsi_reno_2009_pnas.pdf | https://scholarworks.wm.edu/server/api/core/bitstreams/f5cbe32b-44e9-403b-ae61-00de4eb9b239/content | 2026-10-03T05:41:55Z | 73b5d5cc3e8a16f4fd18f207b16eacae3f84a09362a1b981ed92eb349552537c | 1560705 | curl (http=200) | kept |
| cand_ssoar22131.pdf | https://ssoar.info/ssoar/bitstream/document/22131/1/22131_1.pdf | 2026-10-03T05:41:58Z | 880cd9bddd7031942095640f702f4d937556b8b753d7be22104dc5d9c02c9846 | 24773 | curl (http=200) | removed (block page, failure or off-target) |
| cand_durham1414981.pdf | https://durham-repository.worktribe.com/OutputFile/1414981 | 2026-10-03T05:41:59Z | 8bdf3637bc1880f9336ea0d23de4a91310d324bc3a9d76e71c0c9d62dae98cb1 | 5689 | curl (http=403) | removed (block page, failure or off-target) |
| cand_redalyc.pdf | https://www.redalyc.org/pdf/3058/305830999002.pdf | 2026-10-03T05:42:00Z | 314c173a467ed3bb19bdf5700208b464ace4992b9c1fcad97649d3ed3acd6a23 | 282527 | curl (http=200) | removed (block page, failure or off-target) |
| kudryavtsev_2021_econstudies.pdf | https://www.iki.bas.bg/Journals/EconomicStudies/2021/2021-7/3_Andrey-Kudryavtsev_f-F.pdf | 2026-10-03T05:42:34Z | 80f62da465131504cc4c50fa71ba2a559eb0a58ab2692a517f54bf141402e58f | 147506 | curl (http=200) | removed (block page, failure or off-target) |
| cand_atlfed13394.pdf | https://www.fedinprint.org/item/fedawp/13394/original | 2026-10-03T05:42:38Z | - | - | curl (http=000) | removed (block page, failure or off-target) |
| cand_uwasa.pdf | https://osuva.uwasa.fi/bitstreams/dab53ba4-393d-4f3a-bca7-c012f6fcf596/download | 2026-10-03T05:42:38Z | 2820f9f0328efacf0816bd283e96ec3265091325d13aa113f81569135292de62 | 1122495 | curl (http=200) | removed (block page, failure or off-target) |
| joseph_mazouz_2010_coventry.md | https://pureportal.coventry.ac.uk/en/publications/testing-for-overreaction-and-return-continuations-in-stock-price-/ | 2026-10-03T05:42:59Z | ec412274df4629c7a53a2a4d95885866c14cafb293449e7dd641508cea47d3fd | 10752 | scrapling extract get (abstract page) | kept |
| abs_large_oneday_commodity.json | https://api.openalex.org/works?filter=title.search:Analysing%20large%20one-day%20commodity%20futures%20price%20changes&per-page=1 | 2026-10-03T05:43:05Z | 4bab77c5e4d830e584c2f312eab2387c22280230612e87a59527f96edba22191 | 12161 | curl(OpenAlex API) (abstract) | kept |
| abs_sentana_wadhwani.json | https://api.openalex.org/works?filter=title.search:Feedback%20traders%20and%20stock%20return%20autocorrelations%3A%20evidence%20from%20a%20century%20of%20daily%20data&per-page=1 | 2026-10-03T05:43:05Z | a88284b1bb78df12d9c8304fa12fee0098d58fafaf30fffc0f2143faa55fd2d3 | 12706 | curl(OpenAlex API) (abstract) | kept |
| abs_lebaron1992.json | https://api.openalex.org/works?filter=title.search:Some%20relations%20between%20volatility%20and%20serial%20correlations%20in%20stock%20market%20returns&per-page=1 | 2026-10-03T05:43:06Z | c2726971ff26c0aa832bb32baa18f16d4a2ff7c228db103c5b9a884322bd93ab | 12173 | curl(OpenAlex API) (abstract) | kept |
| sentana_wadhwani_1992_ideas.html | https://ideas.repec.org/a/ecj/econjl/v102y1992i411p415-25.html | 2026-10-03T05:43:11Z | 58a5ad82cbf2e0938e0a094b91ef687fb93ef96d9951c14a2a212c096997d62b | 31629 | curl (http=200) | kept |
| feds_2014_86_margins.pdf | https://www.federalreserve.gov/econresdata/feds/2014/files/201486pap.pdf | 2026-10-03T05:43:17Z | 3bb9205526498e387d8efc5d8b851ef188a6a619e7c5b8c440c8104c9201670f | 745546 | curl (http=200) | kept |
| hedegaard_aqr_margins.md | https://www.aqr.com/library/working-papers/causes-and-consequences-of-margin-levels-in-futures-markets | 2026-10-03T05:43:34Z | a38f24eaa7b9416093f125bef693f80dd9bcf86ec7885204cd3cd2847d00721f | 12494 | scrapling extract get (summary page) | kept |
| lubnau_todorova_2015_ideas.html | https://ideas.repec.org/a/taf/eurjfi/v21y2015i15p1282-1296.html | 2026-10-03T05:43:58Z | 8471713c69e0dcb9e23de13d5682522c60661bf48fe62c242f9d36c5da598947 | 35326 | curl (http=200) | kept |
| copeland_1999_ideas.html | https://ideas.repec.org/a/taf/ufajxx/v55y1999i2p73-81.html | 2026-10-03T05:43:58Z | f9005184d18fcc2ecbebd6e37dbe8673a6b2e297d85e9efde0b97bc82b6395f8 | 32424 | curl (http=200) | kept |
| abs_highvix_threshold.json | https://api.openalex.org/works?filter=title.search:Time-varying%20equity%20premia%20with%20a%20high-VIX%20threshold&per-page=1 | 2026-10-03T05:44:16Z | a78e65fee92c78b3739153c8c65d030f7e6e624e4543a74fe278e33bee1d64aa | 523 | curl(OpenAlex API) (abstract) | kept |
| bansal_stivers_quantpedia_pointer.md | https://quantpedia.com/time-varying-equity-premia-with-a-high-vix-threshold/ | 2026-10-03T05:44:47Z | 8e7d9cb194fd59ead795a40593865c58a3ff7a38c3006f408d3c9f1c18563a31 | 22281 | scrapling extract get (pointer page reproducing abstract) | kept |
| (not saved) | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4477652 | 2026-10-03T05:44:47Z | - | - | scrapling get+fetch (blocked (59 and 659 bytes, no content)) | blocked, not saved |
| abs_savor2012.json | https://api.openalex.org/works?filter=title.search:Stock%20returns%20after%20major%20price%20shocks%3A%20The%20impact%20of%20information&per-page=1 | 2026-10-03T05:45:06Z | 1ad6154202a3b66d5db2b9abd5c24b607f4569c4b47716673a58ea7a0a40bdfb | 14815 | curl(OpenAlex API) (abstract) | kept |
| cand_spoudai.pdf | https://spoudai.unipi.gr/index.php/spoudai/article/download/975/1054 | 2026-10-03T05:45:32Z | - | - | curl (http=000) | removed (block page, failure or off-target) |
| caporale_gilalana_plastun_2018_abstract.pdf | https://mev.biem.sumdu.edu.ua/wp-content/uploads/2021/04/Plastun_32.pdf | 2026-10-03T05:45:41Z | 60e87ac46da15df70f6c8df3c404eec58346b4d538ffb63176e41000c9ab8640 | 55211 | curl (http=200) | kept |
| caporale_gilalana_plastun_diw_dp1423.pdf | https://www.diw.de/documents/publikationen/73/diw_01.c.488819.de/dp1423.pdf | 2026-10-03T05:45:54Z | e373e34368bd9b48cb43babdc8b1bf12fce8af80486f8f373e3a1ddc2857613d | 464832 | curl (http=200) | kept |

## Rejection table (records opened or considered and not logged as sources)

| Record | Reason |
|---|---|
| Wang, C.; Yu, M. (2004) "Trading activity and price reversals in futures markets", JBF 28(6) 1337-1361, DOI 10.1016/s0378-4266(03)00120-1 | Blocked: IDEAS has no abstract; OpenAlex has no abstract; the only PDF link (tcnh.ntt.edu.vn) serves a proxy page. Its topic (weekly reversals in 24 futures by volume and open interest) is X10 in any case |
| Banerjee, Doran, Peterson (2007) "Implied volatility and future portfolio returns", JBF 31(10) | Blocked: FSU link 404; no open copy found |
| Marshall, Cahan, Cahan (2008) "Can commodity futures be profitably traded with quantitative market timing strategies?", JBF 32 | No abstract on IDEAS or OpenAlex; no open copy found. Rule families (filters, MA, S&R, channel breakouts, OBV) are X2-type in any case |
| Connolly, Stivers, Sun (2004 NBER conference draft) "Commonality in the time-variation of stock-bond and stock-stock return comovements" | Fetched (regime/connolly_stivers_sun_nber2004.pdf); comovement study, no directional return claim. Their JFQA 2005 paper: Atlanta Fed copy is a block page (removed); contemporaneous relation only per search summaries, not logged |
| Karali, Thurman (2008) "Volatility persistence in commodity futures: inventory and time-to-delivery effects", NCCC-134 | Fetched (regime/farmdoc_confp14-08.pdf); lumber futures only (not a K9 exposure); volatility magnitude, no direction |
| Kudryavtsev (2021) "Stock price dynamics surrounding company-specific shocks" | Individual stocks, company-specific shocks; removed |
| Koski (2026) master's thesis, short-term reversals in S&P 100 stocks (osuva.uwasa.fi) | Individual stocks, reversal (X10), thesis; removed |
| Augusto Ely (2014) LeBaron effect in Brazil (redalyc) | Brazilian cash market; removed |
| Savor (2012) "Stock returns after major price shocks: the impact of information", JFE, DOI 10.1016/j.jfineco.2012.06.011 | Individual stocks; OpenAlex record has no abstract (regime/abs_savor2012.json); not fetched further |
| Bansal-Stivers SSRN page | Blocked (scrapling get and fetch); logged via pointer page as K9R-006 |
| CESifo WP 8445 and WP 5066 | Client-challenge page (3,038 bytes); alternative copies used (K9R-017, K9R-018); removed |
| Hull repository OutputFile/371741 | HTTP 403; abstract used via OpenAlex (K9R-021); removed |
| Durham repository OutputFile/1414981; SSOAR 22131; SPOUDAI (Piraeus); EFMA 2009-0102; Wallmeier EFMA 2008; fedinprint 13394 | 403, HTML, or connection failure; not identified; removed or never saved |
| Chiarella et al. "The return-volatility relation in commodity futures markets" (UTS QFR rp336) | Contemporaneous return-volatility relation, no predictive claim; not fetched |
| Muravyev, Ni (2016) "Why do option returns change sign from day to night?" | Option returns, not futures direction; not fetched |
| "Scale matters" (arXiv 2103.00395, bitcoin/gold/S&P predictability) | Entropy measures, no conditional directional rule; not fetched |
| Practitioner pages (City Index/StoneX OVX and bitcoin notes, T. Rowe Price VIX note, eco3min, TradingView, LuxAlgo, Bulkowski, morpheustrading, cxoadvisory, macrosynergy) | Blogs or vendor pages: pointers only, not evidence |
| Bollerslev, Osterrieder, Sizova, Tauchen (CREATES rp11_51); Bollerslev-Tauchen-Zhou VRP | Monthly to quarterly horizons; not fetched |
| OpenAlex result sets oa_r1a, r1c, r1d, r2a, r2b, r2c, r3a, r3b | About 160 records screened at title level; nearly all off-topic (private equity, IPOs, climate, physics); the on-topic ones are logged above or routed |

## Routed (belong to other readers; not read)

- Overnight reader: Boyarchenko, Larsen, Whelan (2023) "The overnight drift" (overnight return after large
  prior-day declines, dealer inventory; note it is signed against the prior move, so X10 per the borderline
  rule unless the Overnight reader shows otherwise). Lou, Polk, Skouras "A tug of war: overnight versus
  intraday expected returns". Bondarenko, Muravyev "Market return around the clock". Hendershott, Livdan,
  Rösch "Asset pricing: a tale of night and day". Moskowitz, Ooi, Pedersen (2012) "Time series momentum".
  NBIM (2014) discussion note "Momentum in futures markets" (TSMOM weaker in high-volatility regimes).
  Schmidhuber's persistence term (K9R-022) as daily-scale TSMOM.
- Calendar reader: Lucca, Moench (2015) pre-FOMC drift; the scheduled-announcement half of K9R-001
  (pre-NFP/ISM/GDP/FOMC overnight returns conditioned on the six-day VIX build-up) overlaps the Calendar
  topic and X4; the lead resolves the duplicate in Task 4.
- Commodity reader: Karali-Thurman inventory and volatility persistence (rejected here as lumber-only, but
  the inventory channel belongs to the Commodity reader); Janardanan et al.'s inventory/stock-out
  explanation of pre-limit volatility.

## Candidate mechanisms the log supports

1. **Uncertainty premium after an implied-volatility spike (long equity index the next session).**
   Sources: K9R-001 (P-K9R-001-b, -c, -d, -e, -f, -h); supporting sign at longer horizons K9R-002
   (P-K9R-002-a, -c, -d), K9R-003 (P-K9R-003-a, -b). Condition: VIX close up at least 1.0-1.5 points on the
   day (or VIX above its EWMA by that much), known at the 15:15 CT VIX close; about 25-40 days a year.
   Sign: long. Hold: next trade date, 17:00 CT reopen to F (source: close to close, cash S&P 500).
   Products: MNQ, M2K, MYM (S&P evidence, flagged). Closest X: X10 (long after mostly down days; the
   condition reads volatility, not the sign of the move) and X14 (VIX is computed from SPX options).
   Conflicts: K9R-008, K9R-009, K9R-014, P-K9R-001-f. Size about 10-20 bps per trade: clears M_X, far below
   G(f).
2. **VIX-futures backwardation state (long equity index next session).** Source: K9R-004 (P-K9R-004-a,
   -b, -c, -d). Condition: VIX futures curve slope in its bottom 20% (backwardation); about 20% of dates by
   construction. Sign: long. Hold: 1 day close to close (cash S&P). Products: MNQ, M2K, MYM (flag S&P).
   Closest X: X14 (signal from VIX futures, a series the program does not hold; data flag for E.11/E.12);
   X10 is less direct because the condition is a curve state, not a move. Conflict: K9R-005. Size not
   convertible from the source.
3. **With-the-move continuation after a large crude-oil day (MCL).** Source: K9R-017 (P-K9R-017-a, -b,
   -c, -d, -e). Condition: prior day's return beyond its mean + 2 SD, either sign; about 15 a year at the
   source's k (below the 10% floor). Sign: with the prior day. Hold: from the next day's start for a few
   hours (peak 9-10 a.m. GMT+3, i.e. about 1-2 a.m. CT; the source's exits are fitted timing parameters),
   so a session hold to F is untested. Products: MCL only (gold reverses and is insignificant). Closest X:
   none directly (not a fade, not limit-keyed); X1 is not hit because the signal is the whole prior day.
   Conflicts: K9R-018 (the authors' related "inertia" result is a range artifact), K9R-020 (no continuation
   after large non-limit moves in ags/livestock), K9R-021 (weak reversal in 26 commodity futures),
   K9R-022 (strong trends revert). Data caveat: MetaQuotes CFD-type feed, no costs.
4. **Moderate-shock next-day continuation in large index markets.** Source: K9R-019 (P-K9R-019-a),
   abstract only. Condition: prior-day index shock beyond the paper's threshold but under 5%; sign with
   the shock; hold next day; products MNQ, M2K, MYM (cash-index evidence, 39 countries). Closest X: X10
   for the >5% down arm; X3 not hit (sign from the return, not the close location). Conflicts: K9R-014
   (daily autocorrelation of ES near zero, -0.0276, 1993-2007), K9R-012/013 (continuation only in calm
   states, older cash data). Thin: abstract only, threshold and sample unknown.
5. **State-dependent autocorrelation (continue the prior day in calm states).** Sources: K9R-012
   (P-K9R-012-a), K9R-013 (P-K9R-013-a), with K9R-014 (P-K9R-014-a, -b) as the main conflict showing the
   daily effect nearly gone in S&P futures after 1993. Condition: trailing volatility in its bottom 20%
   (D-pct); sign with the prior day's return; hold next session; equity index. Closest X: X3 (both read
   the prior day; X3 uses the close's location, this uses the return's sign) and the R3 borderline
   (low-volatility gate). Weakest of the five; listed because it is the only R3-adjacent mechanism with a
   stated sign.

Non-survivors and negative findings: crypto next-day effects (K9R-016) are insignificant and split in sign;
the "inertia anomaly" (K9R-018) is a favourable-excursion artifact; margin-deleveraging drift has no
supporting source (K9R-012-b, K9R-023, K9R-024); no academic direction test exists for narrow-range or
inside days (R3); candlestick bar patterns show no value (K9R-025); no session-scale volatility-state
evidence was found for rates (ZT-UB), FX (6x, only weekly/quarterly carry in K9R-010), grains, livestock
or gold.

## Footer

- End: 2026-10-02 22:52 PDT (stop reason: saturation on R1, R2 and R3; WebSearch budget not reached, 38 of 120 calls used; no over-budget notice received).
- The 52-row fetch log is also kept as a TSV at reports/stage_e10_research/regime/api/fetchlog.tsv. The fetch time logged for the three scrapling pages is the time the page was copied into regime/ (within two minutes of the scrape).

