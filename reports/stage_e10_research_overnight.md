# Stage E.10 research log, Reader 2: overnight and session-level trend (topics O1, O2)

- Reader: LitReader-Overnight-OpusHigh. Model: Opus 5.5 (claude-opus-5-5), effort high.
- Start: 2026-10-02 22:32 PDT. End: 2026-10-02 22:53 PDT.
- Inputs read: reports/stage_e10_search_plan.md (common rules, O1-O2), reports/stage_e10_design_target.md
  sections (a)-(c), reports/stage_e10_briefs/e0_logged_sources.txt (grep only).
- Counts: records screened by title or abstract: about 450 (240 unique OpenAlex titles across 31 API
  queries, 20 arXiv API entries, about 210 WebSearch result links over 23 calls, with heavy duplication).
  Sources logged: 19 (K9O-001 to K9O-019). Full text: 11 (K9O-001, -004, -005, -006, -007, -008,
  -009, -010, -011, -012, -014). Abstract only, or abstract plus appendix: 8 (K9O-002 is a full
  blog post, counted here as full text of a non-peer-reviewed note; K9O-003 abstract plus full online
  appendix; K9O-013, -015, -016, -017, -018, -019 abstract only). Blocked or not retrievable: see the
  fetch-failure table (SSRN x4, ScienceDirect x2, Wiley x1, JOIM 404, SMU DNS failure, AUT
  Cloudflare, ZORA).
- WebSearch calls used: 23 of 120. No over-budget notice was seen.
- Semantic Scholar: every request with the .env key returned HTTP 403 "Forbidden" at 22:33 PDT (and
  429 without a key). Scholarly search therefore ran on OpenAlex (and the arXiv API, Crossref once).
  The key was never printed.
- Firecrawl: used twice, both on SSRN abstract pages after Scrapling `get` returned a 59-byte block
  page (logged in the fetch table).
- Stop reason per topic: **O1 saturation** (the last 15+ records screened, OpenAlex queries o1j-o1m,
  the crude-oil and two Treasury WebSearches, added no new mechanism). **O2 saturation** (the last 15+
  records, the OpenAlex o2 queries and the Quantpedia and Concretum WebSearches, added no new
  mechanism). Not budget.
- Quoting convention: passages are copied from the saved file (PDFs via `pdftotext -layout`, HTML via a
  tag-stripping conversion saved beside the raw file as .txt). Line breaks and runs of spaces in the
  layout text are collapsed to one space; end-of-line hyphenation and ligature characters are kept as
  they appear in the file. "[...]" marks an omission inside a passage. Table rows are quoted with
  whitespace collapsed.
- Unit conversions in the reader's notes are the reader's arithmetic, not the source's. Where a
  conversion needs an index or FX level, an illustrative level is named (for example NQ = 20,000);
  it is not program data and no file under data/ was opened.

---

## Sources

### K9O-001 The Overnight Drift (Boyarchenko, Larsen, Whelan)

- Citation: Boyarchenko, N., Larsen, L. C., Whelan, P. (2020, revised August 2022). "The Overnight
  Drift." Federal Reserve Bank of New York Staff Reports no. 917. Published version: Review of
  Financial Studies (2023), DOI 10.1093/rfs/hhad020 (DOI from memory of the journal record, not
  verified in a fetched file: treat as [unverified]). CEPR DP14462 is an earlier version.
- Retrieval: curl of the NY Fed PDF. File reports/stage_e10_research/overnight/boyarchenko_sr917.pdf
  (+ .txt). Full text.
- Mechanism: E-mini S&P 500 returns are concentrated at the European open (02:00-03:00 ET), which the
  authors attribute to dealers offloading inventory taken on at the US close (inventory risk with
  time-varying dealer risk capacity). The reversal is asymmetric: after selling pressure at the US
  close the overnight reversal is strong; after buying pressure it is weak.
- Products and horizon: ES (and SP) front futures; hold windows 02:00-03:00 ET (OD) or 01:30-03:30 ET
  (OD+); the conditional BtD rule holds 01:30-03:30 ET only after a negative closing order imbalance.
- Sample window: 5 January 1998 to 31 December 2020 (main); trading strategies 2004.1 to 2020.12.
- Market and data frequency: CME E-mini S&P 500, mid quotes and best bid/offer, 5-minute and hourly
  returns; signed volume for order imbalance (RSV, 15:15-16:15 ET).
- Cost assumptions: Refinitiv best bid and ask quotes; long entered at the ask, exited at the bid.
- Quality tells: Fed staff report, later RFS; bootstrap and Bonferroni/Benjamini-Yekutieli checks of
  the hour; year-by-year persistence; DST natural experiment (predictability moves with the European
  open). The authors themselves later report the effect has faded (K9O-002).
- Verified passages:
  - P-K9O-001-a (abstract): "This paper documents that U.S. equity returns are large and positive
    during the opening hours of European markets."
  - P-K9O-001-b (abstract): "market selloffs generate robust positive overnight reversals, while
    reversals following market rallies are much more modest."
  - P-K9O-001-c (p. 1): "the largest positive returns are between 2:00 and 3:00 - the opening of
    European markets in U.S. Eastern Time terms (ET) - averaging 3.7% on an annualized basis (1.48 basis
    points per day)."
  - P-K9O-001-d (p. 2): "they are positive in 20 out of 23 years since 1998 and statistically
    significant in 17 of these."
  - P-K9O-001-e (Section II data): "Our sample period spans January 5, 1998 – December 31, 2020 (23
    years)."
  - P-K9O-001-f (p. 5): "Pre- transaction costs, a trading strategy that goes long the S&P 500 futures
    between 2:00 and 3:00 earns a Sharpe ratio of 1.1 and accounting for bid-ask spreads this reduces
    to −0.5."
  - P-K9O-001-g (Section V): "We also consider a conditional trading strategy that ‘buys-the-dip’,
    denoted BtD, which holds the e-mini during the OD+ period but only on trading days following a
    negative order flow at [...] market close (RSVt−1 < 0)."
  - P-K9O-001-h (Section V): "However, the BtD strategy remains highly profitable (Sharpe ratio of 1.1)
    because it only pays the bid-ask spread on half the trading days when returns are higher."
  - P-K9O-001-i (Table IX (a), without costs, columns CTC, CTO, OTC, OD, OD+, BtD): "Mean 8.95 4.62
    4.20 3.75 6.21 6.07"
  - P-K9O-001-j (Table IX (b), with costs, same columns): "Mean 8.95 0.38 −0.05 −0.59 1.91 4.04"
  - P-K9O-001-k (Section III.C): "in the first sample opening hour returns are large, negative and
    significant"
- Numeric claims: 3.7% annualized, 1.48 bp per day in the 02:00-03:00 ET hour (P-K9O-001-c); positive
  in 20 of 23 years (P-K9O-001-d); OD Sharpe 1.1 before costs, -0.5 after (P-K9O-001-f); BtD mean 6.07%
  annualized before costs and 4.04% after, holding on about half of days (P-K9O-001-h, -i, -j).
- Conflicting evidence: K9O-002 (post-2021 disappearance, P-K9O-002-a, -b, -c); K9O-003 (inventory risk
  subsumed by VIX change, P-K9O-003-e).
- Reader's note: Shape: a 2-hour overnight hold (01:30-03:30 ET = 00:30-02:30 CT) inside the trade
  date that starts at the 17:00 CT reopen; long only; meets the two-hour minimum exactly. Condition:
  negative closing order imbalance fires on about 50% of dates (P-K9O-001-h), too often; a stricter cut
  (bottom quintile of closing imbalance) would fire near 20% but that literal is not in the source.
  Inputs: RSV needs aggressor-signed volume, which one-minute OHLCV bars do not carry: a data item for
  E.11/E.12, flagged. Exclusion: the BtD rule buys after net selling at the close, that is, it is
  signed against the closing flow; under the borderline rule "a rule signed against the prior move is
  X10", BtD is X10-adjacent. The unconditional hour (no sign condition) is not X10 but trades every
  day. Products: ES only (not a traded exposure); K9O-002 says the same pattern held in NQ and YM.
  Size versus the cost wall (reader's arithmetic): BtD's 6.07%/yr over ~252 dates is ~2.4 bp per date,
  ~4.8 bp per trade at f = 0.5. At an illustrative NQ level of 20,000, 4.8 bp = 9.6 points = 38 MNQ
  ticks: above M_X (16.2 ticks) but about 1/11 of G(0.4) = 430 ticks. The unconditional OD hour (1.48
  bp) is about 3 points = 12 MNQ ticks, below M_X.

### K9O-002 The Disappearing Overnight Drift (Liberty Street Economics, 2026)

- Citation: Boyarchenko, N., Larsen, L. C., Whelan, P. (1 July 2026). "The Disappearing Overnight
  Drift." Liberty Street Economics (Federal Reserve Bank of New York blog). No DOI.
- Retrieval: curl of https://libertystreeteconomics.newyorkfed.org/?p=43261. File
  reports/stage_e10_research/overnight/lse_blog_43261.html (+ .txt conversion). Full text of the post.
- Mechanism: the authors' own out-of-sample update: the 02:00-03:00 ET drift averaged near zero in
  January 2021 to December 2025, in ES, NQ and YM; they attribute the fade to a compression of
  closing order-imbalance dispersion (the inventory channel), not to a change in variance or dealer
  capacity.
- Products and horizon: ES, NQ, YM; the 02:00-03:00 ET hour and next-day cumulative returns by bin of
  closing signed volume.
- Sample window: January 2021 to December 2025 (1,245 trading days), against 1998-2020 and 2007-2020.
- Market and data frequency: CME E-mini futures, intraday (5-minute bars in the charts).
- Cost assumptions: none stated (returns before costs).
- Quality tells: blog note by the original authors, not peer reviewed; charts with stated samples;
  a stated falsifiable prediction.
- Verified passages:
  - P-K9O-002-a (paragraph 1): "Five additional years of data later, that pattern appears to have faded: the 2:00–3:00
    window that previously generated roughly 3.7 percent per annum has averaged close to zero since
    2021."
  - P-K9O-002-b (after first chart): "The 2:00–3:00 window—previously responsible for more than 60 percent of the contract’s
    5.9 percent annualized close-to-close return—is flat. The same pattern holds in the E-mini
    Nasdaq-100 (NQ) and E-mini Dow Jones (YM) contracts."
  - P-K9O-002-c (closing-imbalance section): "In 2021–25 (bottom panel), the spread is much narrower, consistent with a weaker
    predictive link in the post-publication sample."
  - P-K9O-002-d (conclusion): "Our framework yields a falsifiable prediction: if order-imbalance dispersion widens
    back toward its pre-2020 range, the overnight drift should reappear in the same 2:00–3:00 window,
    with the same cross-contract signature."
  - P-K9O-002-e (chart note): "Sample: S&P 500 E-mini futures, January 2021–December 2025 (1,245 trading
    days)."
- Numeric claims: drift near zero since 2021 (P-K9O-002-a); window was over 60% of a 5.9% annualized
  close-to-close return (P-K9O-002-b).
- Conflicting evidence: this source is itself the main conflict for K9O-001 and K9O-003.
- Reader's note: Strongest evidence against an unconditional or order-flow-conditioned European-open
  hold on MNQ/MYM in a research window after 2021. Its own prediction makes a conditional version
  (trade only when closing-imbalance dispersion is high) testable, but that state variable needs signed
  volume (flagged data item) and was absent in 2021-2025 by the authors' account.

### K9O-003 Market Return Around the Clock: A Puzzle (Bondarenko, Muravyev)

- Citation: Bondarenko, O., Muravyev, D. (2023). "Market Return Around the Clock: A Puzzle." Journal of
  Financial and Quantitative Analysis 58(3), 939-967 [volume and pages from a search-result URL, unverified]. DOI 10.1017/S0022109022000783.
- Retrieval: curl of the Cambridge article page (abstract) and the Cambridge-hosted online appendix PDF.
  Files: bm_cambridge.html (+ bm_cambridge.txt) and bm_jfqa_supp.pdf (+ .txt). Abstract plus full
  online appendix; the main text was not open.
- Mechanism: the E-mini S&P 500 earns its whole average return in the four hours around the European
  open (23:30-03:30 ET); the authors argue for uncertainty resolution (VIX futures rise overnight and
  fall at the European open) rather than inventory risk.
- Products and horizon: ES, VIX futures; 4-hour window 23:30-03:30 ET (= 22:30-02:30 CT), sub-windows.
- Sample window: January 2004 to July 2018 for ES (Table IA.5 statement); VIX futures from 22 June 2014.
- Market and data frequency: CME tick-level data, aggregated to intraday periods.
- Cost assumptions: main text Section V.C (not retrieved) reports profitability after costs (P-K9O-003-c).
- Quality tells: JFQA; appendix includes weekend versus weekday test, pre/post-2011 liquidity test,
  zero-imbalance subsample, horse race against order imbalance.
- Verified passages:
  - P-K9O-003-a (abstract): "Strikingly, 4 hours around European open account for the entire average
    market return. This period’s returns have a 1.6 Sharpe ratio and remain high after transaction
    costs. Average returns are a noisy zero during the remaining 20 hours."
  - P-K9O-003-b (abstract): "High returns are consistent with European investors processing information
    accumulated overnight and thus resolving uncertainty."
  - P-K9O-003-c (Internet Appendix p. 3): "Section V.C shows that this strategy is profitable after
    costs."
  - P-K9O-003-d (Table IA.8, columns Full 11:30-3:30, Middle 1:30-2:30, 1st Part 11:30-1:30, 2d Part
    1:30-3:30): "Return, E-mini S&P 0.0761*** 0.0508*** 0.0169** 0.0591***"
  - P-K9O-003-e (Internet Appendix p. 5): "while VIX change has a t-statistic of 3.1. Overall,
    uncertainty resolution explains return reversal at EU-open better than inventory risk."
  - P-K9O-003-f (Internet Appendix p. 4): "If anything, EU-open returns are lower on weekends than on
    the other days, 4.8% versus 8.2%."
  - P-K9O-003-g (Table IA.5 note): "period from January 2004 to July 2018 for E-mini S&P 500 futures"
- Numeric claims: Sharpe 1.6 for the 4-hour window (P-K9O-003-a); 7.61% annualized full window, 5.91%
  in 01:30-03:30 (P-K9O-003-d, units as annualized fractions per the table); weekend 4.8% vs weekday
  8.2% (P-K9O-003-f).
- Conflicting evidence: K9O-002 (fade after 2021, P-K9O-002-a). Against K9O-001's inventory story:
  P-K9O-003-e.
- Reader's note: Same window family as K9O-001. Condition candidates in the source: a VIX rise during
  the last US hour predicts a higher EU-open return (Table IA.9). A VIX-conditioned rule reads another
  market (VIX index or futures), so it is X14-adjacent under the K8 class unless VIX is treated as a
  public daily series (it is published intraday by Cboe; a close-to-close VIX change would be a public
  daily series with a documented time). Unconditional window trades every day. 7.6% per year over ~252
  dates is ~3.0 bp per date, about 6 MNQ ticks at NQ = 20,000 (illustrative): below M_X 16.2.

### K9O-004 A Tug of War: Overnight versus Intraday Expected Returns (Lou, Polk, Skouras)

- Citation: Lou, D., Polk, C., Skouras, S. (2019). "A tug of war: Overnight versus intraday expected
  returns." Journal of Financial Economics 134, 192-213 [volume and pages unverified]. DOI 10.1016/j.jfineco.2019.03.011 (OpenAlex record).
- Retrieval: LSE Research Online accepted version, curl. Files lps_lse_page.html, lps_tugofwar.pdf (+
  .txt). Full text (accepted manuscript).
- Mechanism: momentum profits (cross-sectional, industry and time-series) accrue overnight while the
  intraday component is flat or negative; the authors link it to clienteles (individuals trade at the
  open, institutions intraday against momentum).
- Products and horizon: Moskowitz-Ooi-Pedersen 12-month TSMOM applied to 22 equity index futures,
  decomposed into close-to-open and open-to-close parts, monthly aggregation.
- Sample window: 1996 to 2016 for the futures test (Table III); start dates per contract in Panel B
  (S&P500 mini from 10 September 1997); US stocks 1993-2013.
- Market and data frequency: Thomson Reuters Tick History; open and close defined as 30-minute VWAPs
  around the busiest minute before and after noon.
- Cost assumptions: none (gross returns).
- Quality tells: JFE; t-statistics with 12-lag correction; robust to 4-factor alphas.
- Verified passages:
  - P-K9O-004-a (Section 3): "As with cross-sectional momentum, time-series momentum occurs entirely
    overnight."
  - P-K9O-004-b (Section 3): "the monthly overnight CAPM alpha associated with time-series momentum is
    1.40% with a t-statistic of 3.24. The corresponding intraday alpha is negative, economically
    negligible, and statistically indistinguishable from zero."
  - P-K9O-004-c (Section 3): "Interestingly, all of this strategy’s negative return skewness comes from
    its intraday component."
  - P-K9O-004-d (Table III caption): "the day vs. at night for the period 1996 to 2016, for 22 equity
    index futures listed in Panel B."
  - P-K9O-004-e (Table III Panel A, columns Raw, CAPM, 3-Factor, 4-Factor, Stdev, Skew): "Overnight
    1.10% 1.40% 1.42% 1.54% 4.24% 0.178" and "Intraday -0.29% -0.10% -0.10% -0.04% 4.85% -2.767"
  - P-K9O-004-f (Section 3): "“intraday” and “overnight” periods are much more well-de…ned for equity
    markets than they are for, say, USD/Yen currency futures."
  - P-K9O-004-g (Conclusion): "This claim seems particularly likely for trend-following strategies we
    have studied that invest in highly liquid equity index futures."
- Numeric claims: TSMOM overnight 1.10% raw per month (t 2.67), intraday -0.29% (t -0.78)
  (P-K9O-004-e); overnight CAPM alpha 1.40% per month, t 3.24 (P-K9O-004-b).
- Conflicting evidence: K9O-006 (TSMOM predictability weak asset by asset, P-K9O-006-a); K9O-008
  (shorter trends decayed, P-K9O-008-b).
- Reader's note: The most direct O2 evidence: the 12-month trend premium in equity index futures is
  earned close-to-open, not open-to-close. K9 shape: hold from the 17:00 CT reopen (or the prior close)
  to the day-session open (08:30 CT for MNQ/MYM/M2K), about 15.5 hours, in the direction of the
  12-month trend. Every date has a trend sign, so a rarity condition is needed, for example the
  K9O-009 Bear or Correction states, or a trailing-percentile cut on trend strength (D-pct). Not X1
  (signal is 12 months, not the overnight plus first half hour) and not X15 (not hourly, not Monday);
  under the borderline rule it is admissible "if sourced at that horizon", which this source is. Size:
  1.10% per month for a diversified, volatility-scaled portfolio of 22 indexes is ~5 bp per trade date
  at portfolio level (reader's arithmetic); per-instrument size at the session level is not reported.
  At NQ = 20,000 (illustrative), 5 bp is 10 points = 40 MNQ ticks, above M_X 16.2 but far below
  G(0.4) 430. Note the LPS "open" is a noon-centred VWAP for foreign indexes, so the US mapping to
  the 08:30 CT open is an assumption.

### K9O-005 Time Series Momentum (Moskowitz, Ooi, Pedersen)

- Citation: Moskowitz, T. J., Ooi, Y. H., Pedersen, L. H. (2012). "Time series momentum." Journal of
  Financial Economics 104, 228-250 (title page of the saved file). DOI 10.1016/j.jfineco.2011.11.003.
- Retrieval: curl of the NYU Stern author copy (pages.stern.nyu.edu/~lpederse). File mop_tsmom.pdf (+
  .txt). Full text.
- Mechanism: an instrument's own past 1-12 month excess return predicts its next-month return
  (under-reaction then delayed over-reaction).
- Products and horizon: 58 futures and forwards (24 commodities, 12 cross-currency pairs, 9 equity
  indexes, 13 government bonds); look-back 12 months, holding 1 month in the base case.
- Sample window: January 1965 to December 2009.
- Market and data frequency: daily futures returns compounded to monthly.
- Cost assumptions: gross of costs in the main tests.
- Quality tells: JFE, the founding TSMOM paper; per-instrument results.
- Verified passages:
  - P-K9O-005-a (abstract): "We document signiﬁcant ‘‘time series momentum’’ in equity index,
    currency, commod- [...] ity, and bond futures for each of the 58 liquid instruments we consider."
  - P-K9O-005-b (abstract): "persistence in returns for one to 12 months that partially reverses over
    longer horizons,"
  - P-K9O-005-c (Section 2): "from January 1965 through December [...] 2009. These instruments are among the most"
- Numeric claims: 58 instruments, January 1965 to December 2009 (P-K9O-005-a, -c).
- Conflicting evidence: K9O-006 (P-K9O-006-a, -b).
- Reader's note: Horizon source for the daily-scale trend members (O2). Gives no session split; K9O-004
  supplies that for equity indexes only. For rates, FX, metals and energy, there is no source in this
  log that splits TSMOM by session, so a session-hold TSMOM member on ZN or 6E would rest on the
  monthly evidence plus an assumption about when it accrues. TSMOM sign alone trades every day: needs
  a rarity condition (K9O-009 states, D-pct on trend strength).

### K9O-006 Time Series Momentum: Is It There? (Huang, Li, Wang, Zhou)

- Citation: Huang, D., Li, J., Wang, L., Zhou, G. (2020). "Time series momentum: Is it there?" Journal of
  Financial Economics 135, 774-794 (title page of the saved file). DOI 10.1016/j.jfineco.2019.08.004.
- Retrieval: curl of the Asian Finance Association working-paper mirror
  (down.aefweb.net/WorkingPapers/w717.pdf), which carries the JFE layout. File hlwz_tsm_isitthere.pdf
  (+ .txt). Full text.
- Mechanism: (against) asset-by-asset regressions show little 12-month-to-1-month predictability; the
  pooled t-statistic fails bootstrap critical values; TSMOM profits match a sample-mean strategy that
  needs no predictability.
- Products and horizon: the 55 MOP instruments; 12-month look-back, 1-month hold.
- Sample window: January 1985 to December 2015.
- Market and data frequency: daily futures/forward returns aggregated monthly.
- Cost assumptions: none.
- Quality tells: JFE; wild and pairs bootstraps; out-of-sample tests.
- Verified passages:
  - P-K9O-006-a (abstract): "per shows that asset-by-asset time series regressions reveal little
    evidence of TSM, both [...] in- and out-of-sample."
  - P-K9O-006-b (abstract): "From an investment perspective, the TSM strategy is proﬁtable, but its
    perfor- [...] mance is virtually the same as that of a similar strategy that is based on historical
    sample [...] mean and does not require predictability. Overall, the evidence on TSM is weak, particu- [...]
    larly for the large cross section of assets."
  - P-K9O-006-c (Section 2): "sample period is from January 1985 to December 2015."
- Numeric claims: none beyond the sample.
- Conflicting evidence: conflicts with K9O-005 and K9O-004.
- Reader's note: Main conflicting evidence for O2. For K9 it implies that a single-product TSMOM
  session member is close to "long the product when its trailing mean is positive", which for equity
  indexes is mostly long. A K9 TSMOM member should therefore be judged against a long-only session
  hold, not against zero.

### K9O-007 Momentum Strategies in Futures Markets and Trend-following Funds (Baltas, Kosowski)

- Citation: Baltas, A.-N., Kosowski, R. (2012 working paper, EFMA 2012 Barcelona; version 11 June
  2012). "Momentum Strategies in Futures Markets and Trend-following Funds." SSRN 1968996. No DOI found.
- Retrieval: plain-http download from efmaefm.org (the https host failed certificate verification in
  curl and Scrapling). File baltas_kosowski_momf.pdf (+ .txt). Full text.
- Mechanism: TSMOM exists at monthly, weekly and daily rebalancing frequencies, with low correlation
  across frequencies; daily and weekly strategies weakened after 1995.
- Products and horizon: 71 futures across asset classes; daily strategies with look-back and holding
  periods J, K in {1, 3, 5, 10, 15, 30, 60} days.
- Sample window: December 1974 to January 2012.
- Market and data frequency: daily futures data.
- Cost assumptions: not in the passages read.
- Quality tells: conference paper (later published, journal version not retrieved); grid of (J, K)
  pairs: multiple testing across 3 frequencies x many pairs.
- Verified passages:
  - P-K9O-007-a (abstract): "We find that monthly, weekly and daily strategies exhibit low
    cross-correlation, which indicates that they capture distinct return continuation phenom- ena."
  - P-K9O-007-b (Introduction): "the monthly strategies have been more profitable while the weekly and
    daily strategies have become less profitable during the second sub-sample period (post-1995)."
  - P-K9O-007-c (Section 4): "in the most recent 8 (or even 16) weeks for the weekly frequency and in
    the period between the past 9 to 15 days for the daily frequency."
  - P-K9O-007-d (Introduction): "Using daily data on 71 futures contracts across assets classes from
    December 1974 to January 2012"
- Numeric claims: daily momentum concentrated in 9-15 day look-backs (P-K9O-007-c).
- Conflicting evidence: its own sub-sample (P-K9O-007-b); K9O-008 (P-K9O-008-b).
- Reader's note: Supports a daily-scale (9-15 day) trend signal as a separate phenomenon, but the
  decay after 1995 weighs against short trends in a 2020s window. No session split. A 9-15 day trend
  signal held for one session is not X1 or X15 by horizon.

### K9O-008 Two Centuries of Trend Following (Lempérière, Deremble, Seager, Potters, Bouchaud)

- Citation: Lempérière, Y., Deremble, C., Seager, P., Potters, M., Bouchaud, J.-P. (2014). "Two
  centuries of trend following." arXiv:1404.3274 (journal publication not verified).
- Retrieval: curl of arxiv.org/pdf/1404.3274. File lemperiere_two_centuries.pdf (+ .txt). Full text.
- Mechanism: trend excess returns exist across commodities, currencies, indexes and bonds since 1800;
  predictability saturates for large signals; long trends stable, short trends decayed.
- Products and horizon: futures since 1960 and spot series since 1800; signal = price minus a 5-month
  EMA, scaled by volatility, monthly.
- Sample window: futures from 1960, spot from 1800, to about 2013 (end date not located by grep).
- Market and data frequency: monthly closes.
- Cost assumptions: none.
- Quality tells: CFM practitioner research, long sample, t-stat about 5 since 1960 and 10 since 1800.
- Verified passages:
  - P-K9O-008-a (abstract): "When analyzing the trend following signal further, we find a clear
    saturation effect for large signals, suggesting that fundamentalist traders do not attempt to
    resist “weak trends”, but step in when their own signal becomes strong enough."
  - P-K9O-008-b (abstract): "We find no sign of a statistical degradation of long trends, whereas
    shorter trends have significantly withered."
  - P-K9O-008-c (Section 4.3): "Much shorter trends (say over three days) have significantly decayed
    since 1990"
  - P-K9O-008-d (Figure 5 note): "The best fit to the data is provided by the hyperbolic tangent, which
    suggests a saturation of the signal for large values."
- Numeric claims: overall t-stat about 5 since 1960 (abstract, not separately quoted).
- Conflicting evidence: P-K9O-008-a/-d conflict with conditioning on very strong trends; P-K9O-008-c
  with K9O-007's daily strategies.
- Reader's note: Design guidance for O2 conditions: a "trade only when trend strength is extreme" rule
  is contradicted by the saturation result: the payoff per unit of signal flattens at extremes, so
  rarity should not come from an extreme-strength cut. Months-long trends are the ones that survive.

### K9O-009 Momentum Turning Points (Garg, Goulding, Harvey, Mazzoleni)

- Citation: Goulding, C. L., Harvey, C. R., Mazzoleni, M. G. (2023). "Momentum turning points." Journal
  of Financial Economics [volume and pages unverified], DOI 10.1016/j.jfineco.2023.05.007 (the JFE byline drops
  Garg). Retrieved version: Garg, Goulding, Harvey, Mazzoleni, AEA 2021 preliminary paper, version 11
  December 2020.
- Retrieval: the ScienceDirect OA article returned a Cloudflare challenge to curl and to Scrapling
  `fetch`; the AEA-hosted preliminary PDF was downloaded with curl. File ghm_aea.pdf (+ .txt). Full
  text of the working version.
- Mechanism: classify each month by the signs of the trailing 12-month (slow) and 1-month (fast)
  returns: Bull (both >= 0), Correction (12m >= 0, 1m < 0), Bear (both < 0), Rebound (12m < 0, 1m >= 0).
  Slow and fast disagree in Corrections and Rebounds (turning points); blending speeds by state
  improves Sharpe ratios.
- Products and horizon: US stock market (Mkt-RF), extended to international equity markets; monthly.
- Sample window: January 1969 to December 2018.
- Market and data frequency: monthly index returns.
- Cost assumptions: an S&P futures cost example (2 bp spread, 0.5 bp roll) in Section 3.
- Quality tells: JFE; out-of-sample dynamic speed selection; equity-only.
- Verified passages:
  - P-K9O-009-a (Figure 2 note): "A month is classified as Correction if rt−12,t ≥ 0 but rt−1,t < 0; as
    Bear if rt−12,t < 0 and rt−1,t < 0; and as Rebound if rt−12,t < 0 but rt−1,t ≥ 0."
  - P-K9O-009-b (Section 2): "Bear months are relatively uncommon—approximately one-sixth of the time
    (16.8%)—"
  - P-K9O-009-c (Section 2): "whereas Correction and Rebound months amount to the remaining 34.8% of
    the months. In other words, about once every three months, on average, SLOW and FAST suggest a
    different position in the stock market."
  - P-K9O-009-d (Figure 1 note): "over the 50-year evaluation period from 1969-01 to 2018-12."
- Numeric claims: Bull 48.3% of months, Bear 16.8%, Correction plus Rebound 34.8% (P-K9O-009-b, -c).
- Conflicting evidence: K9O-006 (TSMOM weak asset by asset).
- Reader's note: Supplies a pre-stated, non-tuned state variable for a TSMOM session member: for
  example, short the overnight session of MNQ/MYM/M2K only in Bear months (both signs negative,
  16.8% of months). Because a monthly state persists for the whole month, the D-wk cap (two entries a
  week) would bind: Bear-month dates x 2/5 is about 7% of dates, near or below the 10% floor. Using the
  daily-updated trailing 12-month and 21-day returns instead of month-end states changes the
  frequency; that is a design choice for the lead. Not X1/X15 by horizon. Equity only.

### K9O-010 Intraday Patterns in FX Returns and Order Flow (Breedon, Ranaldo)

- Citation: Breedon, F., Ranaldo, A. (2013). "Intraday Patterns in FX Returns and Order Flow." Journal
  of Money, Credit and Banking [volume and pages unverified]. DOI 10.1111/jmcb.12032. Retrieved version: preliminary
  draft dated 5 December 2008 (AEA 2009 conference).
- Retrieval: curl of swlb1.aeaweb.org/conference/2009/retrieve.php?pdfid=301. File
  breedon_ranaldo_aea2009.pdf (+ .txt). Full text of the draft.
- Mechanism: currencies depreciate during their own local trading hours and appreciate during foreign
  hours, mirrored in order flow (locals are net buyers of foreign currency in their own hours).
- Products and horizon: EUR/USD, USD/JPY, EUR/JPY, GBP/USD, USD/CHF, AUD/USD on EBS; session holds,
  e.g. EUR/USD short 07:00-13:00 GMT, long 13:00-21:00 GMT.
- Sample window: 2 January 1997 to 1 June 2007.
- Market and data frequency: EBS interdealer transactions, aggregated hourly.
- Cost assumptions: firm EBS bid and ask; long at the ask, unwound at the bid.
- Quality tells: published JMCB; draft is "preliminary and incomplete"; only EUR/USD survives costs.
- Verified passages:
  - P-K9O-010-a (abstract): "We present evidence of time-of-day effects in foreign exchange returns
    through a significant tendency for currencies to depreciate during local trading hours (e.g.
    EUR/USD tends to depreciate in the European morning and then appreciate in US trading hours)."
  - P-K9O-010-b (Table 5, EUR/USD rows): "EUR/USD Short 7.00-13.00 0.06" and "Long 13.00-21.00 0.07"
  - P-K9O-010-c (Section 3): "As might be expected, most of these simple time-of-day trading
    strategies are not profitable when trading costs are included. However, the notable exception is
    EUR/USD where the significant intraday pattern combined with narrow spreads in this cross means
    that this basic strategy has been profitable on average with Sharpe Ratios of 1.3 and 0.9
    respectively for the morning short and afternoon long."
  - P-K9O-010-d (Section 2): "Over the whole sample 2/1/1997 to 1/6/2007"
  - P-K9O-010-e (Section 2.3): "although the returns over each session individually show considerable
    variation, the difference in returns between the two sessions remains remarkably stable."
- Numeric claims: EUR/USD annualised returns after costs 0.06 (morning short) and 0.07 (afternoon long)
  (P-K9O-010-b; the unit, fraction or percent, is not stated in the table row); Sharpe 1.3 and 0.9
  (P-K9O-010-c).
- Conflicting evidence: K9O-012 attributes intraday dollar swings to benchmark fixes (P-K9O-012-a).
  Other pairs unprofitable after costs (P-K9O-010-b context, P-K9O-010-c).
- Reader's note: Mechanism differs from X1-X15 on its face (home-currency bias plus segmentation),
  but the windows bracket the ECB 13:15 CET and London 16:00 fixes, and K9O-012 explains the same
  W-shape by fixes: X9-adjacent, to be ruled by the lead. Unconditional (every day): needs a condition
  from the source family (order flow is the source's state variable; not in OHLCV). Hold: 13:00-21:00
  GMT is 07:00-15:00 CST but 08:00-16:00 CDT in summer, past F = 15:08 CT; the morning short
  07:00-13:00 GMT is 01:00-07:00 CST, inside one trade date. Size: if 0.06 means 6% a year, that is
  ~2.4 bp per date, ~2.8 6E ticks at EUR/USD 1.15 (illustrative), below M_X 6.9.

### K9O-011 Segmentation and Time-of-Day Patterns in Foreign Exchange Markets (Ranaldo)

- Citation: Ranaldo, A. (2009). "Segmentation and time-of-day patterns in foreign exchange markets."
  Journal of Banking and Finance [volume and pages unverified]. DOI 10.1016/j.jbankfin.2009.05.019. Retrieved
  version: Swiss National Bank Working Paper 2007-3 (dated 21 December 2006).
- Retrieval: SNB page (snb_wp2007_03.html) then curl of the SNB PDF. File ranaldo_snb_wp2007_03.pdf (+
  .txt). Full text.
- Mechanism: domestic currencies appreciate in foreign working hours and depreciate in domestic hours;
  explained by domestic-currency bias with segmentation, producing cyclical dealer inventory pressure.
- Products and horizon: CHF/USD, JPY/USD, EUR/USD, JPY/EUR, DEM/USD; working-hour windows.
- Sample window: January 1993 to August 2005 (CHF/USD, JPY/USD); January 1999 to August 2005 (EUR/USD,
  JPY/EUR).
- Market and data frequency: high-frequency spot quotes, hourly.
- Cost assumptions: not in the passages read.
- Quality tells: JBF; persistence across years claimed.
- Verified passages:
  - P-K9O-011-a (abstract): "Domestic currencies appreciate (depreciate) systematically during for-
    eign (domestic) working hours. These time-of-day patterns are statistically and economically highly
    significant."
  - P-K9O-011-b (abstract): "The prevalence of domestic (foreign) traders demanding the counterpart
    currency during domestic (foreign) working hours implies a cyclical net positive (negative)
    imbalance in dealers’ inventory."
  - P-K9O-011-c (Section 3): "from the beginning of January 1993 to the end of August 2005 for the
    CHF/USD and JPY/USD exchange rates, and from Jan- uary 1999 to August 2005 for EUR/USD and JPY/EUR."
- Numeric claims: none quoted.
- Conflicting evidence: K9O-012 (P-K9O-012-a).
- Reader's note: Same family as K9O-010, earlier sample; applies to 6E, 6S, 6J. Same X9 caution and
  same lack of a rarity condition.

### K9O-012 Foreign Exchange Fixings and Returns Around the Clock (Krohn, Mueller, Whelan)

- Citation: Krohn, I., Mueller, P., Whelan, P. (2024). "Foreign Exchange Fixings and Returns around the
  Clock." Journal of Finance (OpenAlex lists 2023; volume unverified). DOI 10.1111/jofi.13306. Retrieved version: Bank of Canada Staff
  Working Paper 2021-48.
- Retrieval: Wiley pdfdirect returned a 5.6 KB challenge page (discarded); Bank of Canada PDF by curl.
  File kmw_boc_swp2021_48.pdf (+ .txt). Full text of the working paper.
- Mechanism: the US dollar appreciates before the major fixes (Tokyo, ECB, London) and depreciates
  after, a W-shape over 24 hours, from dealers hedging an unconditional dollar demand at fixes.
- Products and horizon: major USD crosses, spot and CME FX futures; hours around fixes.
- Sample window: January 1999 to December 2019 (spot); futures data from January 2006.
- Market and data frequency: high-frequency spot and inter-dealer order flow (Refinitiv Matching), CME
  futures.
- Cost assumptions: not in the passages read.
- Quality tells: JF; inter-dealer order flow; CME order flow found uninformative for reversals.
- Verified passages:
  - P-K9O-012-a (abstract): "We document that intraday currency returns display systematic reversals
    around the major benchmark fixings, characterized by an appreciation of the U.S. dollar pre-fix and
    a depreciation post-fix."
  - P-K9O-012-b (Introduction): "to the pre-fix order imbalance results in a post-fix reversal of
    around 2.5 to 3.5 basis points"
  - P-K9O-012-c (Section 2): "Our full sample starts in January 1999 and ends in December 2019"
- Numeric claims: post-fix reversal of 2.5-3.5 bp per one-standard-deviation pre-fix imbalance
  (P-K9O-012-b).
- Conflicting evidence: offers a competing explanation for K9O-010/011.
- Reader's note: Hits X9 (fix-timed). Logged as the main competing explanation for the FX
  time-of-day sessions: a session member whose window brackets a fix inherits X9.

### K9O-013 Overnight versus Day Returns in Gold and Gold Related Assets (Blose, Gondhalekar, Kort)

- Citation: Blose, L. E., Gondhalekar, V., Kort, A. (2018). "Overnight versus day returns in gold and
  gold related assets." Journal of Economics and Finance 42(3), 526-549. DOI 10.1007/s12197-017-9403-0.
- Retrieval: RePEc/IDEAS abstract page by curl. File ideas_blose_gold.html (+ .txt). Abstract only
  (Springer full text not open).
- Mechanism: gold is "too high" at each market's open: overnight returns positive, day returns
  negative, in COMEX front gold futures, London fix spot, miners and funds.
- Products and horizon: COMEX GC front futures and related assets; close-to-open versus open-to-close.
- Sample window: not stated in the abstract.
- Market and data frequency: daily open and close.
- Cost assumptions: abstract says results survive costs.
- Quality tells: lower-tier journal; abstract only.
- Verified passages:
  - P-K9O-013-a (abstract): "Overnight returns are significantly positive while day returns are
    significantly negative in the COMEX gold front futures contract, the gold spot market (London Fix),
    gold mining company stocks, and gold related closed end mutual funds and exchange traded funds."
  - P-K9O-013-b (abstract): "The asymmetry is shown to be present in both up and down markets for gold.
    The results are economically important even with transaction costs."
- Numeric claims: none in the abstract.
- Conflicting evidence: none retrieved; K9O-014 agrees and adds a London-fix manipulation period.
- Reader's note: MGC: long from the 17:00 CT reopen to the COMEX day open (or short the day session).
  Unconditional, so it trades every day: needs a rarity condition, none sourced. Exclusion check: the
  day-session weakness overlaps the London PM fix window (X9) in K9O-014's reading; not a fade (X10)
  and not keyed to a prior move. No size given; cannot compare with M_X 16.8 / G(0.4) 183.1 ticks.

### K9O-014 Gold Price Dynamics Around the Clock (Donati, Jung; CBS master's thesis)

- Citation: Donati, F., Jung, J. A. (2019). "Gold Price Dynamics Around the Clock." MSc thesis,
  Copenhagen Business School (supervisor P. Whelan), 15 May 2019. No DOI.
- Retrieval: curl of research-api.cbs.dk portal PDF. File cbs_gold_thesis.pdf (+ .txt). Full text.
- Mechanism: gold appreciates in eastern (China, India) trading hours and depreciates in western
  hours (a hat shape), linked to eastern import demand; gold falls around London fix times in the
  alleged-manipulation years.
- Products and horizon: COMEX GC futures, 5-minute data around the clock.
- Sample window: 18 years of 5-minute data (exact start and end dates not located by grep).
- Market and data frequency: GC futures, 5-minute.
- Cost assumptions: bid-ask spreads; strategies unprofitable after costs in the first half of the
  sample, profitable but below the market in the second half.
- Quality tells: master's thesis (low weight); supervised by a K9O-001 author.
- Verified passages:
  - P-K9O-014-a (abstract): "We find a hat-shaped intraday seasonality, with gold appreciating during
    eastern trading hours in a robust way and depreciating for the rest of the day."
  - P-K9O-014-b (abstract): "When transaction costs are not taken into account they outperform the
    market, with Sharpe ratios as high as 1.61. When taken into account, trading strategies
    underperform the market, but still show some profitability."
  - P-K9O-014-c (Section 1.4): "Including transaction costs, the four trading strategies perform poorly
    in the first half of the sample due to high bid-ask spreads. In the second half, bid-ask spreads are
    considerably smaller, and three of our four strategies become profitable despite not beating the
    market."
- Numeric claims: Sharpe up to 1.61 before costs (P-K9O-014-b).
- Conflicting evidence: costs (P-K9O-014-b, -c).
- Reader's note: Supports a MGC long in the Asian session (17:00 CT reopen to about 02:00 CT, before
  the London open) as a time-of-day premium. Every-day pattern: no rarity condition. Its condition
  candidates are macro (China GDP, INR) at low frequency, not tested as triggers. X9 overlap for any
  window that spans the London fixes.

### K9O-015 Return Differences between Night and Day: Global Futures Markets (Kallionpää; Aalto thesis)

- Citation: Kallionpää, P. (2013). "Return differences between night and day: Evidence from global
  futures markets." Master's thesis, Aalto University School of Business, Department of Finance. No DOI.
- Retrieval: curl of epub.lib.aalto.fi/en/ethesis/id/13246 (abstract page). File aalto_13246.html (+
  .txt). Abstract only.
- Mechanism: night (close-to-open) versus day (open-to-close) returns for 17 futures: equity index and
  commodity premiums earned at night, day returns negative; interest-rate futures the reverse (day
  positive, night negative).
- Products and horizon: 17 futures (equity index, interest rate, commodity), primary-exchange open and
  close.
- Sample window: 1997 to 2012 (about 4,000 trading days).
- Market and data frequency: Bloomberg daily open and close.
- Cost assumptions: none stated.
- Quality tells: master's thesis, abstract only: low weight.
- Verified passages:
  - P-K9O-015-a (abstract): "I report negative Day returns for equity index and commodity futures during
    the sample period. According to the study the premiums are earned solely during the Night time when
    markets are closed."
  - P-K9O-015-b (abstract): "In consistence, Day time returns for interest rate futures are positive and
    Night returns negative."
  - P-K9O-015-c (abstract): "The sample consists of open and close prices for over 15 years from 1997 to
    2012."
- Numeric claims: none.
- Conflicting evidence: none retrieved.
- Reader's note: The only source found that splits rates futures by session; direction only, weak
  source. A rates day-session premium likely reflects US announcement timing (Calendar reader's
  domain): routed note below. Unconditional.

### K9O-016 Overnight Returns of Stock Indexes: Evidence from ETFs and Futures (Liu, Tse)

- Citation: Liu, Q., Tse, Y. (2017). "Overnight returns of stock indexes: Evidence from ETFs and
  futures." International Review of Economics and Finance 48, 440-451 (pages from memory,
  [unverified]). DOI 10.1016/j.iref.2017.01.005.
- Retrieval: SSRN 2921758 blocked to curl and Scrapling `get` (59-byte page); Firecrawl scrape of the
  abstract page (logged). File liu_tse_ssrn_2921758_firecrawl.md (main-content excerpt). Abstract only.
- Mechanism: overnight returns of US index ETFs and most international index futures are positive and
  day returns negative; the overnight return predicts the first half-hour negatively and the last
  half-hour positively.
- Products and horizon: US index ETFs and international index futures; overnight versus trading
  hours, first and last half-hour.
- Sample window: 1999 to 2014.
- Market and data frequency: intraday.
- Cost assumptions: none in the abstract.
- Quality tells: IREF; abstract only.
- Verified passages:
  - P-K9O-016-a (abstract): "During the period 1999-2014, overnight returns of US exchange-traded index
    funds and most international index futures are significantly positive, while returns during trading
    hours are negative."
  - P-K9O-016-b (abstract): "For US ETF and futures markets, we also show that overnight returns can
    forecast both the in-sample and out-of-sample returns during the first half-hour (with a negative
    relation) and last half-hour (with a positive relation) of trading hours."
- Numeric claims: none.
- Conflicting evidence: none.
- Reader's note: The predictive part is X1 (overnight return predicts the last half-hour) and an
  opening-half-hour reversal (X10-like). The session-split part agrees with K9O-001/-003/-015.

### K9O-017 Market Closure and Short-Term Reversal (Della Corte, Kosowski, Wang)

- Citation: Della Corte, P., Kosowski, R., Wang, T. (2015). "Market Closure and Short-Term Reversal."
  SSRN 2730304, DOI 10.2139/ssrn.2730304. E.0 logged the later version as K3-040 (Kosowski et al.
  2023, "Overnight-Intraday Reversal Everywhere", SSRN 4605208); that SSRN page now returns HTTP 410
  "removed" (Firecrawl, logged), so it could not be re-fetched.
- Retrieval: EPFL seminar page (22 January 2018) carrying the abstract, curl. File
  dellacorte_epfl_memento.html. Abstract only.
- Mechanism: cross-sectional: buy assets with low past overnight returns, sell those with high, hold
  intraday; explained by cross-sectional volatility and limits to arbitrage.
- Products and horizon: international equities and futures on equity indexes, rates, commodities and
  currencies; overnight signal, intraday hold.
- Sample window: not in the abstract.
- Market and data frequency: daily open and close.
- Cost assumptions: not in the abstract.
- Quality tells: working paper, abstract only.
- Verified passages:
  - P-K9O-017-a (abstract): "A strategy that buys securities with low past overnight returns and sell
    securities with high past overnight returns generates sizeable out-of-sample excess returns and
    Sharpe ratios."
  - P-K9O-017-b (abstract): "outperforms the conventional short-term reversal strategy for major
    international equity markets and futures written on equity indices, interest rates, commodities,
    and currencies."
- Numeric claims: none.
- Conflicting evidence: conflicts with any "overnight return continues into the day" rule (O1
  continuation).
- Reader's note: Hits X10 (fade of the overnight move, at the daily frequency) and is cross-sectional
  (needs a basket). Logged as the main O1 evidence for reversal rather than continuation across
  asset classes.

### K9O-018 Hedging Demand and Market Intraday Momentum (Baltussen, Da, Lammers, Martens)

- Citation: Baltussen, G., Da, Z., Lammers, S., Martens, M. (2021). "Hedging demand and market intraday
  momentum." Journal of Financial Economics 142, 377-403 (title page of the saved file). DOI 10.1016/j.jfineco.2021.04.029.
- Retrieval: curl of the author copy www3.nd.edu/~zda/intramom.pdf. File baltussen_intramom.pdf (+
  .txt). Full text available; only the abstract was read (X1 family).
- Mechanism: the return from the previous close to the last 30 minutes predicts the last 30 minutes,
  via gamma hedging; it reverts over the following days.
- Products and horizon: over 60 futures on equities, bonds, commodities and currencies; last 30 minutes.
- Sample window: December 1974 to May 2020 (from the text, line "from December 1974 to May 2020").
- Market and data frequency: intraday.
- Cost assumptions: not read.
- Quality tells: JFE.
- Verified passages:
  - P-K9O-018-a (abstract): "The return during the last 30 minutes before the market [...] close is
    positively predicted by the return during the rest of the day (from previous mar- [...] ket close to the
    last 30 minutes)."
  - P-K9O-018-b (abstract): "The predictive power is economically and statistically [...] highly signiﬁcant,
    and reverts over the next days."
  - P-K9O-018-c (Section 1): "from December 1974 to May 2020."
- Numeric claims: none quoted.
- Conflicting evidence: P-K9O-018-b (reversal over the next days) conflicts with multi-day continuation
  of session moves.
- Reader's note: X1. Logged because the reversion over subsequent days is evidence against a
  "yesterday's session sign continues today" member.

### K9O-019 An Anatomy of Asset Returns (Renò, Shi; seminar abstract)

- Citation: Renò, R., Shi, S. (2026). "An Anatomy of Asset Returns." Seminar paper, Tinbergen Institute
  Econometrics Seminar, 13 March 2026 (also SMU, 13 April 2026). No paper or DOI found.
- Retrieval: curl of the Tinbergen event page. File tinbergen_anatomy.html (+ .txt). Abstract only.
  The SMU page failed (DNS) and no arXiv or SSRN version was found.
- Mechanism: a drift-volatility-jump decomposition from half-power autocovariances, applied to
  overnight/day reversals in US stocks and futures.
- Products and horizon: US stocks and futures; overnight versus day.
- Sample window: not stated.
- Market and data frequency: high-frequency.
- Cost assumptions: none.
- Quality tells: seminar abstract only; very low weight.
- Verified passages:
  - P-K9O-019-a (abstract): "The decomposition allows to uncover new findings on the overnight/day
    return reversals in US stocks and futures."
- Numeric claims: none.
- Conflicting evidence: none.
- Reader's note: Context only. A WebSearch summary attributed a "momentum channel driven by continuous
  returns and a reversal channel driven by jumps" to this work; that wording is NOT in the saved file
  and is not logged as evidence.

---

## Fetch log (evidence files)

All files under reports/stage_e10_research/overnight/. Times are file write times (UTC), equal to the
fetch time. sha256 of the raw file.

| File | URL | UTC fetch time | sha256 | Bytes | Tool |
|---|---|---|---|---|---|
| boyarchenko_sr917.pdf | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf | 2026-10-03T05:34:18Z | 403276b2ea8227c14ccfb854014af1df6a425430e5f622599640d7c0c16e683a | 3881868 | curl |
| lse_blog_43261.html | https://libertystreeteconomics.newyorkfed.org/?p=43261 | 2026-10-03T05:41:19Z | 7cacdb191577c19bc5dacf6f99f6eebc76adc9ff7748bbc325ce6a85adc60740 | 174658 | curl |
| bm_cambridge.html | https://www.cambridge.org/core/product/identifier/S0022109022000783/type/journal_article | 2026-10-03T05:35:53Z | 879cd7109d1e6afe4aa0832975261213ed396bad689e2a22d4f41491fa258159 | 952868 | curl |
| bm_jfqa_supp.pdf | https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S0022109022000783/resource/name/S0022109022000783sup001.pdf | 2026-10-03T05:36:02Z | 27168fdc53c1ad9c1aff1d1467db5a09b6cf5c8adabec7a505996ba3a6f83cd4 | 1002084 | curl |
| lps_lse_page.html | https://researchonline.lse.ac.uk/id/eprint/87481 | 2026-10-03T05:36:53Z | db3a5d15e498a4a183f2f1e8e1a3aa6f72bef97d08087aac85196dd1d2d988d4 | 45544 | curl |
| lps_tugofwar.pdf | https://researchonline.lse.ac.uk/id/eprint/87481/7/Polk_Tug%20of%20War.pdf | 2026-10-03T05:37:00Z | bee535c9079268128a0cda044c8bf4af14f4e9e9638bc0588fa611c33e89e8d3 | 614561 | curl |
| mop_tsmom.pdf | https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf | 2026-10-03T05:36:55Z | 7682f8e97eb4b77591dc85e36731ff51ed031970cdde81678108734db9478379 | 976459 | curl |
| hlwz_tsm_isitthere.pdf | https://down.aefweb.net/WorkingPapers/w717.pdf | 2026-10-03T05:40:31Z | ec8209bd179eaa0f7d5f60d2613b141c2e314c1b688ab7a10739f068cd2365fc | 1350895 | curl |
| baltas_kosowski_momf.pdf | http://efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2012-Barcelona/papers/BK_MOMF_Full.pdf | 2026-10-03T05:43:52Z | f48c15bba94e7105939ddd86c33831078c778c3fb7d77bb2cafa3d8cd0449a5a | 1154861 | curl (http; https failed TLS verification) |
| lemperiere_two_centuries.pdf | https://arxiv.org/pdf/1404.3274 | 2026-10-03T05:45:39Z | b38cf16e2a07a136c727a232acc15c6510170e301d39e89ad4ef18a489635124 | 463000 | curl |
| ghm_aea.pdf | https://benny.aeaweb.org/conference/2021/preliminary/paper/492Ds6fk | 2026-10-03T05:37:59Z | 0c6a9bd9d5fc228dbd5a533fad7f88fc2af6bc8d558ce59ab18effaf5b8ce55e | 921229 | curl |
| breedon_ranaldo_aea2009.pdf | https://swlb1.aeaweb.org/conference/2009/retrieve.php?pdfid=301 | 2026-10-03T05:39:03Z | f0214a8e9ea14a6c070c8b2737d02194a7ebf5e05570f114bb4d581ffdbdd78e | 242167 | curl |
| snb_wp2007_03.html | https://www.snb.ch/en/publications/research/working-papers/2007/working_paper_2007_03 | 2026-10-03T05:39:02Z | 0936cdac436ed8e2152e27015fa2e4f6ee2daea56c51f69b620b9fb3898a75aa | 74931 | curl |
| ranaldo_snb_wp2007_03.pdf | https://www.snb.ch/public/asset/en/www-snb-ch/publications/research/working-papers/2007/working_paper_2007_03/publications0_en/working_paper_2007_03.n.pdf | 2026-10-03T05:39:08Z | 1259f03e3e303a01d896cc0e4ddd6bf81bd6e33b60a821fe6fb6af670a64d27f | 349406 | curl |
| kmw_boc_swp2021_48.pdf | https://www.bankofcanada.ca/wp-content/uploads/2021/10/swp2021-48.pdf | 2026-10-03T05:39:38Z | 807fdb20dac0010b3b41f3f08c17b9bf7a233291fea449cd64cd86ad54fa0f46 | 1468457 | curl |
| ideas_blose_gold.html | https://ideas.repec.org/a/spr/jecfin/v42y2018i3d10.1007_s12197-017-9403-0.html | 2026-10-03T05:44:34Z | 5b3a55689c07b22e5bfc1ee356952845a811ee0d1ff48ab986c913552353fae0 | 49624 | curl |
| cbs_gold_thesis.pdf | https://research-api.cbs.dk/ws/portalfiles/portal/59803241/651553_Thesis_Contract_13383.pdf | 2026-10-03T05:44:44Z | 63858a7564d0a666ceaa9692b2c695f99542f19975790609ad7064a04a3674b5 | 2470014 | curl |
| aalto_13246.html | https://epub.lib.aalto.fi/en/ethesis/id/13246 | 2026-10-03T05:43:11Z | a2bbdbd12344a0f33ff842d9d1cceb29079bd01db025379bbccdcfc7d98425f8 | 6988 | curl |
| liu_tse_ssrn_2921758_firecrawl.md | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2921758 | 2026-10-03T05:42:49Z | 4fd44d2d47cfe3d97b1211320c7413d447cf2b46be040dbf26430278951714e0 | 1791 | Firecrawl scrape (after Scrapling get failed); excerpt saved |
| dellacorte_epfl_memento.html | https://memento.epfl.ch/event/market-closure-and-short-term-reversal | 2026-10-03T05:35:31Z | f33a2ad4a0fd59f80572ed60bc50d0ef579a546d769be96e66b7a9a0186f956f | 20252 | curl |
| baltussen_intramom.pdf | https://www3.nd.edu/~zda/intramom.pdf | 2026-10-03T05:42:02Z | 623ba82490acd01546f568cf582de5a9b45dfbd97731cd548cb119d7a0acec57 | 2397917 | curl |
| tinbergen_anatomy.html | https://tinbergen.nl/event/2026/03/13/13278/an-anatomy-of-asset-returns | 2026-10-03T05:41:29Z | ee407cbf1a264cbee7f0c7be3ba167283c05e16481dc65d1b223cc5ac76cd554 | 168413 | curl |
| qp_update_489.html | https://vvv.quantpedia.com/?p=489 | 2026-10-03T05:43:32Z | 64262c9a36cad11af3dc2080cecdeaf0d890fd24ed2ca0016ee37c6e4be6bbd1 | 117173 | curl (pointer only: identified K9O-007; not evidence) |
| fortuin_eur_thesis.pdf | https://thesis.eur.nl/pub/65764/Second-Draft-Final-Version-Master-Thesis-Daan-Fortuin.pdf | 2026-10-03T05:43:15Z | ff43a65210583fb30af58c66e70604af13dc620fd534cb844aecaa8ad06c5386 | 4868229 | curl (screened and rejected: stocks only) |

Each PDF has a pdftotext .txt beside it; each HTML used for quotes has a tag-stripped .txt beside it.
API search records (not evidence) are under reports/stage_e10_research/overnight/api/ (31 OpenAlex
JSON files, 2 arXiv XML, 1 Crossref JSON).

### Fetch failures

| Target | Route tried | Result |
|---|---|---|
| Semantic Scholar Graph API (all queries) | curl with x-api-key | HTTP 403 Forbidden (key rejected); 429 without key |
| SSRN 4605208 (Kosowski et al. 2023, E.0 K3-040) | curl Delivery.cfm; Scrapling fetch; Firecrawl | HTML block page; 659-byte page; Firecrawl HTTP 410 "removed from SSRN" |
| SSRN 3596245 (Bondarenko-Muravyev WP) | curl Delivery.cfm | HTML block page |
| SSRN 2921758 PDF (Liu-Tse) | curl, Scrapling get | 59-byte page; abstract via Firecrawl (above) |
| ScienceDirect S0304405X23000995 (GHM JFE) | curl pdfft; Scrapling fetch | Cloudflare "Just a moment"; working version used |
| Wiley pdfdirect 10.1111/jofi.13306 (KMW JF) | curl | 5.6 KB challenge page; Bank of Canada version used |
| ZORA (Ranaldo JBF accepted version) | curl | no PDF link; SNB version used |
| JOIM "Nasdaq-100 index futures: intraday momentum or reversal?" | curl | 404 page not found |
| AUT ACFR "Ivy Zhou" gold paper | curl | Cloudflare challenge; not retried (thesis K9O-014 covers the topic) |
| SMU seminar page (Renò-Shi) | curl, Scrapling get, WebFetch | DNS failure (ENOTFOUND) |
| Kim, Tse, Wald (2016) "Time series momentum and volatility scaling" | OpenAlex, Crossref | no abstract in either; SSRN only; not retrieved |
| arXiv API search for "anatomy of asset returns" | http (empty), https | no matching entry |

---

## Rejection table (records screened and rejected)

| Record | Reason |
|---|---|
| Gao, Han, Li, Zhou (2018) "Market intraday momentum" | X1 itself; already the CP1 source |
| Li, Sakkas, Urquhart (2021) "Intraday time series momentum: global evidence" (FinMar) | X1 family (first half-hour predicts last) |
| Jin et al. (2019) "Intraday time-series momentum: evidence from China" | X1 family; Chinese futures not traded |
| "Bitcoin intraday time series momentum" (2021, Financial Review) | X15/X1 family; E.0 covered bitcoin intraday |
| Berkman, Koch, Tuttle, Zhang (2012) "Paying attention: overnight returns and the hidden cost of buying at the open" | individual stocks, attention; no futures |
| Hendershott, Livdan, Rösch (2020) "Asset pricing: a tale of night and day" | stock cross-section (beta priced overnight); no futures session rule |
| Cliff, Cooper, Gulen (2008) "Return differences between trading and non-trading hours" | US stocks/ETFs; SSRN only; equity-index night premium already covered by K9O-001/-003/-016 |
| Kelly, Clark (2011) "Returns in trading versus non-trading hours" (J Asset Mgmt) | ETFs; not open; covered by K9O-016 |
| Akbas et al. (2022) "Overnight returns, daytime reversals, and future stock returns" | stocks only |
| Fortuin (2022) EUR thesis "The structure of overnight versus intraday prices" | stocks only (downloaded, screened, rejected) |
| Hasbrouck (2003) "Intraday price formation in U.S. equity index markets" | price discovery, no return premium |
| "Night trading and market quality: Chinese and US precious metal futures" (2020) | market quality, not returns |
| "Night trading with futures in China: aluminum and copper" (2021) | Chinese venue; not traded |
| "Empirical differences between overnight and day trading hour returns: Chinese commodity futures" (XJTLU) | Chinese venue; not traded |
| "The effect of nighttime trading of futures markets on information flows: China" (2016) | Chinese venue; information flow |
| NYMEX crude after-hours (ACCESS) VAR study (1990s, Emerald CFRI) | price-volume lead-lag, no return premium; pre-Globex era |
| "The overnight return puzzle and the T+1 rule in Chinese stocks" (2020) | Chinese stocks |
| "Overnight momentum, informational shocks, and late informed trading in China" (2019) | Chinese stocks |
| "Statistical arbitrage with mean-reverting overnight price gaps on S&P 500" (2019, JRFM) | stocks; gap fade (X10) |
| Pitkäjärvi, Suominen, Vaittinen (2020) "Cross-asset signals and time series momentum" | signal from another market: X14 class |
| Daniel, Moskowitz (2016) "Momentum crashes" | cross-sectional stock momentum |
| Lim, Zohren, Roberts (2019) "Enhancing TSMOM with deep neural networks" | ML signal, outside a pre-stated condition |
| "Profitability of time series momentum" (JBF 2015) | not retrieved; monthly; no session split (pointer only) |
| Fleming, Lopez (1999) NY Fed SR82 Treasury volatility spillovers | volatility, not returns (Regime topic) |
| Quantified-strategies, Moneymetals, TradingView, NexusFi, LuxAlgo, CXO, Alpha Architect, BSIC, Substack pages | blogs: pointers only, never evidence |
| JOIM "Nasdaq-100 index futures: intraday momentum or reversal?" | page 404; intraday (likely X1) |
| Iwatsubo et al. (2018) platinum and gold futures intraday seasonality (cited in K9O-014) | liquidity and volume seasonality, not read |
| He (2026) "Interpretable Systematic Risk around the Clock", arXiv 2604.13458 (downloaded, read abstract, deleted) | stock-market jump-risk factor from LLM-classified news; no session rule |
| "Does Overnight News Explain Overnight Returns?", arXiv 2507.04481 (downloaded, read abstract, deleted; authors not checked) | US stocks; news-topic NLP signal, not an admissible input |
| AUT ACFR "Trading hours extension and intraday price behavior" (2019 blind draft) | intraday overreaction (X10); not read |
| Dozens of off-topic OpenAlex hits (GARCH comparisons, HFT, algorithmic trading, crypto surveys, non-finance titles) | off topic |

---

## Routed (belongs to other readers; not read further)

- Regime reader: K9O-001's VIX double sorts and "reversals amplified in high volatility"; any
  "overnight drift after a large prior-day decline" rule (large prior-day moves); Kim, Tse, Wald (2016)
  TSMOM and volatility scaling (volatility state); Fleming-Lopez Treasury volatility spillovers.
- Calendar reader: rates day-session premium in K9O-015 (likely US announcement timing); the
  pre-announcement and FOMC drift papers that surfaced in OpenAlex ("Premium for heightened
  uncertainty: explaining pre-announcement market returns", JFE 2021; "The pre-FOMC announcement drift and private information"); day-of-week
  effects of the European-open window (K9O-003 Table IA.7).
- Commodity reader: TSMOM combined with carry or term structure; "Macroeconomic conditions,
  speculation, and commodity futures returns" (2025); "The fundamentals of commodity futures returns"
  (2012); "Factor structure in commodity futures return and volatility" (2018).

---

## Candidate mechanisms (supported by this log; no catalog entries written)

1. **European-open overnight drift, conditioned on closing order flow (or on a late-session VIX
   rise).** Sources K9O-001 (P-K9O-001-a, -b, -g, -h, -i, -j), K9O-003 (P-K9O-003-a, -d, -e).
   Condition: negative closing order imbalance (RSV < 0 over 15:15-16:15 ET; fires on about half of
   dates, so a stricter pre-stated cut is needed) or a VIX rise in the last US hour. Sign: long.
   Hold: 00:30-02:30 CT (OD+) or 22:30-02:30 CT (EU-open). Products: MNQ, MYM (evidence is ES; NQ and
   YM named in P-K9O-002-b), M2K by extension. Closest X: X10 for the order-flow version (signed
   against the closing flow); X14 for the VIX version. Strongest conflict: the effect has averaged
   near zero since 2021 in ES, NQ and YM (P-K9O-002-a, -b, -c). Data flag: signed volume is not in
   one-minute OHLCV.
2. **Daily-scale TSMOM held over the overnight session only, with a trend-state condition.** Sources
   K9O-004 (P-K9O-004-a, -b, -e), K9O-005 (P-K9O-005-a, -b), K9O-009 (P-K9O-009-a, -b, -c).
   Condition: a pre-stated trend state, e.g. GHM Bear (12-month and 1-month returns both negative,
   16.8% of months) for a short, or Bull for a long with a rarity cut; not an extreme-strength cut
   (P-K9O-008-a, -d). Sign: with the 12-month trend. Hold: 17:00 CT reopen to the 08:30 CT day open
   (equity index). Products: MNQ, MYM, M2K (session split sourced only for equity index futures).
   Closest X: X1 by window (overnight) but not by signal (12 months); X15 by family (TSMOM) but not by
   horizon; admissible under the borderline rule if sourced at that horizon. Conflicts:
   P-K9O-006-a, -b; P-K9O-008-b, -c; P-K9O-007-b.
3. **FX home-currency time-of-day pattern (EUR weak in European morning, strong in US hours).** Sources
   K9O-010 (P-K9O-010-a, -b, -c, -e), K9O-011 (P-K9O-011-a, -b). Condition: none sourced (fires every
   day); the source's state variable is order flow. Sign: short 6E 07:00-13:00 GMT (01:00-07:00 CST),
   long 6E 13:00-21:00 GMT (07:00-15:00 CST; violates F in CDT). Products: 6E (6S, 6J weaker). Closest
   X: X9 (KMW explain the intraday dollar W-shape by fixes, P-K9O-012-a). Conflict: P-K9O-012-a; only
   EUR/USD survives costs (P-K9O-010-c).
4. **Gold Asian-session premium (overnight positive, day negative).** Sources K9O-013 (P-K9O-013-a,
   -b), K9O-014 (P-K9O-014-a, -b, -c). Condition: none sourced (every day). Sign: long MGC from the
   17:00 CT reopen into the Asian session (or short the day session). Products: MGC. Closest X: X9
   for any window spanning the London fixes. Conflict: costs erode it in the first half of the CBS
   sample (P-K9O-014-c); evidence is abstract-level or thesis-level.
5. (Weak, context only) **Session split of equity-index and commodity premiums to the night, rates to
   the day.** Source K9O-015 (P-K9O-015-a, -b), K9O-016 (P-K9O-016-a). Unconditional; rates part
   routed to the Calendar reader.

Non-survivors for O1 continuation: no source found that documents "the overnight return signs the full
day session" in futures with a mechanism distinct from X1. The evidence found points the other way:
overnight moves reverse intraday in the cross-section (K9O-017, X10), the overnight return predicts a
first-half-hour reversal (K9O-016), and the rest-of-day move reverts over the next days (K9O-018).
