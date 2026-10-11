# Equity-class intraday literature since 2015 (Stage E.20 Part A, shared source notes)

Reader: ProductReader-RTY-OpusHigh. Written 2026-10-11 (UTC times below; local PDT = UTC - 7 h).
Other readers cite this file as `reports/stage_e20_briefs/shared/equity_class_notes.md`.
Baltussen et al. (JFE 2021) and Rosa (JFM 2022) belong to the NQ reader
(`shared/baltussen_notes.md`, `shared/rosa_2022_notes.md`); only Baltussen's Russell (ER) rows,
grepped from the on-disk copy, are given here. The Aalto thesis belongs to the ZN reader
(`shared/aalto_thesis_notes.md`: metadata only, no figures).

Every number below is quoted from a saved full text, with its location. Per-trade figures marked
"derived" are this reader's arithmetic (annualized figure / 252, the papers' stated annualization of
a once-a-day trade), not the authors'. Fetch log: `reports/stage_e20_briefs/pages/RTY/fetch_log.tsv`
(every URL, UTC time, HTTP code, sha256, path).

## Bottom line for other readers

1. The only Russell-specific primary numbers found are Baltussen's ER row (ROD -> LH, 1993-2020) and
   Gao et al.'s IWM row (first half-hour -> LH, 2000-2013, mean-variance form). No study since 2015
   tests Russell 2000 futures intraday on post-2015 data.
2. Every equity-index intraday momentum figure found is gross and from samples ending 2013-2020.
   The post-2020 evidence is weak in grade and points to decay: the Adams et al. draft (ES,
   2018-2024) finds hourly momentum turns into reversal when dealer net gamma is high; the
   unreviewed SPX retest (2022-04..2026-08) finds a flat unconditional ROD -> LH slope; Kurov,
   Wolfe and Gilbert (abstract only) find the pre-FOMC drift disappeared after 2015.
3. Macro-news days strengthen first-half-hour momentum in SPY 1993-2013 (Gao et al. Table 8:
   FOMC days 20.04 %/yr vs 6.24 %/yr on other days). No post-2013 test of that interaction found.
4. Gamma-conditioned results (Adams et al., Baltussen Table 7, Barbon et al., the SPX retest) need
   option-position data that the 17 roots' bars do not give; none can be a bar-only feature.

## Sources and rows

### S1. Gao, Han, Li, Zhou, "Market intraday momentum", JFE 129 (2018) 394-414
- Copy read: working paper "Intraday Momentum: The First Half-Hour Return Predicts the Last
  Half-Hour Return", "Current Version: December, 2015" (title page), hosted on c.mql5.com (a forum
  file host; robots.txt allows `*`). The published JFE version was not retrieved (no author copy
  found; olin.wustl.edu faculty page 404). Grade: primary text of the authors, working-paper version;
  numbers may differ from the JFE version.
  Saved: `shared/gao_han_li_zhou_wp2015_mql5.pdf` (+ `.txt`), sha256 050d5680d1424a5f...
- Rule (Sec. 3.1, eq. 4): "we will take a long position in the market at the beginning of the last
  half-hour if the timing signal is positive, and take a short position otherwise. It is worth noting
  that the position (long or short) is closed at the market close on each trading day."
  r1 definition (Sec. 2): "we calculate the first half-hour return using previous day's close price
  and the price at 10:00am Eastern time" (so r1 is overnight plus first half-hour, the ONFH form the
  program's CP1 port already tested, V34 item 2).
- SPY, 1993-02-01..2013-12-31, half-hour bars from TAQ: "the average return of the timing strategy
  using the sign of the first half-hour return is 6.67% per annum with a standard deviation of 6.19%.
  The Sharpe ratio is thus 1.08" (Introduction, p. 1). Success rate "54.37%" (Sec. 3.1).
  Derived per trade: 6.67 / 252 = 2.65 bp gross.
- Costs (Sec. 5.2, Table 10, bid-ask at 15:30 ET, closing price at 16:00 ET): after 2001-07-01,
  "the average return reduces to 4.46% per annum, 2.47% lower than the average return before
  transaction costs"; after 2005-01-01, "6.52% after transaction costs compared with 7.96% before".
  Derived per trade after spread, 2005-2013: 2.59 bp (6.52/252).
- IWM (Table 12, Panel A, "same analysis as Table 6", i.e. a constrained mean-variance portfolio,
  weights between -0.5 and 1.5, risk aversion 5, not the sign rule): "IWM 11.72*** 7.70 2.51 2.43
  11.72" = Avg Ret 11.72 %/yr (t 5.18), Std Dev 7.70 %, INS R2 2.51 %, OOS R2 2.43 %, CER 11.72 %.
  Sample "from its inception date [05/26/2000, Table 11] to December 31, 2013". Not convertible to a
  per-trade sign-rule figure (weights vary).
- Macro-news days (Table 8, Panel B, sign rule on r1, SPY 1993-2013): "Non-Release FOMC 6.24***
  6.20 1.01" and "Release FOMC 20.04** 5.84 3.43" (Avg Ret %/yr, Std Dev, Sharpe); MCSI release
  19.09 vs 6.05; GDP release 14.40 vs 6.28; CPI release 18.03 vs 6.10. Panel A: FOMC-day
  beta_r1 14.4 (t 2.35), R2 11.0 % vs 6.68 and 2.5 % on other days. Text: "The greatest economic
  gains are delivered on the release days of the FOMC minutes. The annualized average return reaches
  a high level of 20.04%." Derived per trade on FOMC days: 20.04 / 252 = 7.95 bp gross (about 8
  events a year, so roughly 165 trades in the sample).
  Caveat: the paper calls them "FOMC minutes ... released regularly at 2:15pm about every six weeks"
  (Sec. 4.2); 2:15 pm every six weeks is the pre-2013 statement schedule, while minutes are released
  three weeks after each meeting. Which date set was used is ambiguous in the text.
- Decay: none in the paper beyond its own OOS tests (Table 4 is "Out-of-Sample Market Timing").
  Later evidence on this ONFH form: Baltussen Table B1 (ES ONFH R2_OOS -1.68 %, see S2), Rosa 2022
  (NQ reader), Liu and Tse 2017 (S9, secondary-only).

### S2. Baltussen, Da, Lammers, Martens, JFE 142 (2021): Russell (ER) rows only
- Copy: `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md` (E.13, version of
  record per E.13 I-37b). Full read and portfolio figures: NQ reader, `shared/baltussen_notes.md`.
- Sample row (Table A1, line 3235): "| Russell 2000 ICE/CME* | ER | 1993-02-08 | 2020-05-01 | 6746 |
  09:30-16:00 | USA |"; the asterisk: "the sample period is extended by considering the regular
  future before the mini contract was introduced". Note: before 2017-07-10 the Russell futures
  traded on ICE (S10), so the paper's ER series is not GLBX-only.
- Table B1 Panel B (individual equity index futures; slopes, R2 and R2_OOS "multiplied by 100";
  Newey-West t in parentheses), line 3431: "| ER | 8.17*** (4.62) | 2.38 | 2.21*** | 7.79*** (4.54) |
  3.61*** (3.15) | 12.27** (2.17) | 3.91 | 3.33*** | 6.00*** (5.86) | 3.35 | 3.15*** |".
  Reading: ONFH beta 8.17 (t 4.62), R2 2.38 %, R2_OOS 2.21 %; ROD beta 6.00 (t 5.86), R2 3.35 %,
  R2_OOS 3.15 %. Compare NQ: ROD 6.36 (t 7.97), R2_OOS 3.76 %; ES: ONFH R2_OOS -1.68 %.
  Conversion: beta 0.06 means about 6.0 bp of expected LH return per 1 % of r_ROD. In M2K ticks at an
  index level of 2,000 (1 bp = 0.2 index points = 2 ticks of 0.10): 12 ticks per 1 % of |r_ROD|.
  A per-trade average needs the mean |r_ROD| for ER, which the paper does not report per market
  (not derived; deriving it from program data is not allowed).
- Leveraged-ETF exposure (table at lines 2412-2419, "Average Leveraged ETF Market Share (X^2 - X)"):
  "| ER | 0.0085 | 3.85 |", the largest of the equity markets listed (ES 0.0034).

### S3. Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov, "Do S&P 500 Options Increase Market
Volatility? Evidence from 0DTEs", draft dated "July 15, 2026"
- Saved: `shared/adams_etal_0dte_fontaine.pdf` (+ `.txt`), sha256 6b256ade06bd6428..., from the
  co-author's GitHub Pages site (no robots.txt: 404). Grade: primary, unpublished draft.
- Abstract: "intraday variation in market makers' hedging needs predicts stronger order-flow
  reversals, lower momentum returns, and lower intraday volatility."
- Table 7 (E-mini S&P, 10-minute marks, regular hours 9:30-16:00 ET, "The sample period is from
  01/2018 to 12/2024"); "momentum return" is defined as the first difference R(t,t+n) - R(t-n-1,t-1)
  in bp (Sec. 4.4). Quartiles of market makers' net gamma (180-day backward window):
  "60 0.633* 0.087 -0.271 -1.144** -1.777***" (Q1, Q2, Q3, Q4, Q4-Q1) and
  "120 0.730 0.181 -0.759 -2.158** -2.888***". Text: "small positive momentum returns for lower levels
  of market makers' net gamma, but negative momentum returns (or positive reversal returns) of around
  1-2 bps across the investment horizons for the higher level of net gamma."
- Use: decay or regime evidence for equity momentum in 2018-2024 (ES). Sizes of 1-3 bp are below
  M2K's D8 wall in bp (about 3.2 bp at index 2,000) and need SPX option-position data, which is not
  a bar of any of the 17 roots.

### S4. firmtape, "Intraday momentum is dead in the 0DTE era" (dev.to, posted 2026-08-27)
- UNREVIEWED practitioner blog post, not peer reviewed. Saved: `shared/devto_firmtape_spx_retest.html`
  (+ `.txt` extract), sha256 7b66ef35a5dbd9b1... (dev.to robots.txt allows article pages).
- Design as stated: "1,085 SPX sessions, 2022-04-14 to 2026-08-20, one observation per day: the
  rest-of-day return (open to 30 minutes before the close) against the last-30-minute return."
  (r_ROD from the open, not the prior close as in Baltussen.)
- Result: "all 1,085 +0.006 +/- 0.009 +0.6" (slope, t) and "Flat overall, flat in every single year,
  signs alternating." Conditional: "the slope adds +0.055 (t +3.1) on short-gamma closes ... short
  closes are only 15% of sessions ... Five-for-five on sign is worth reporting; it is not worth a
  position." Grade: unreviewed; usable only as a pointer.

### S5. Li, Sakkas, Urquhart, "Intraday time series momentum: global evidence and links to market
characteristics", J. Financial Markets 57 (2022) 100619
- Saved: `shared/li_sakkas_urquhart_2022_accepted.pdf` (+ `.txt`), accepted manuscript, CentAUR
  (CC BY-NC-ND 4.0), sha256 39add97e355b49c0.... Grade: primary (accepted version).
- Data: 16 developed-market cash indices (US = S&P 500, ".SPX 09:30 - 16:00"), "04 October 2005 to
  29 December 2017"; not futures, not Russell.
- Rule (performance table caption): "ITSM opens a long (short) position at the beginning of the last
  half hour if the return during the first half hour on the same trading day is positive (negative),
  and closes the positions at the market close."
- US row: "US ITSM 6.567 5.892 0.086 3.099 1.115" (Mean %/yr, SD, skew, kurtosis, Sharpe;
  annualized). Derived per trade: 2.61 bp gross, cash index (not tradable as such).

### S6. Lucca and Moench, "The Pre-FOMC Announcement Drift", NY Fed Staff Report 512 (rev. 2013;
published J. Finance 2015)
- Saved: `shared/lucca_moench_sr512.pdf` (+ `.txt`), sha256 c7cb0f335c60cb9f... (newyorkfed.org
  robots.txt allows the path). Grade: primary (staff-report version of the JF 2015 paper).
- "since 1994, the S&P500 index has on average increased 49 basis points in the 24 hours before
  scheduled FOMC announcements. These returns do not revert in subsequent trading days" (abstract
  page). Intraday shape (Sec. 3.1, 131 meetings 1994-09..2011-03): "the SPX rises slightly on the
  afternoon of the day before the FOMC (left panel), and it then drifts sharply higher in the morning
  of scheduled FOMC announcements (middle panel). Right before the time of the announcement ... it
  reaches a level about 50 basis points higher than on the previous day's open. Following the
  announcement at 2:15 pm the SPX is on average flat". The morning-only share is shown in a figure,
  not tabulated: not sized here.
- Size portfolios: daily close-to-close only ("this analysis is based on daily close-to-close
  returns"); no Russell intraday figure.

### S7. Kurov, Wolfe, Gilbert, "The Disappearing Pre-FOMC Announcement Drift", Finance Research
Letters 40 (2021)
- Full text NOT retrieved: the Skidmore author copy returns 404 (curl and scrapling get). Abstract
  read on IDEAS/RePEc (`shared/ideas_kurov_wolfe_gilbert_2021.html`, sha256 a55f8ef6bd4fd27a...).
  Grade: [secondary-only] (abstract).
- Abstract: "We extend the sample to December 2019. We find that after first appearing before FOMC
  announcements accompanied by the Fed Chair press conferences, the pre-FOMC drift essentially
  disappeared after 2015 in both announcements accompanied by press conferences and announcements not
  accompanied by press conferences." Unsized in the abstract.

### S8. Barbon, Beckmeyer, Buraschi, Moerke, "The Role of Leveraged ETFs and Option Market Imbalances
on End-of-Day Price Dynamics", S/BF-HSG WP 2021/14 (September 2021)
- Saved: `shared/barbon_beckmeyer_buraschi_moerke_letf.pdf` (+ `.txt`), sha256 4c2cbcd35d990144...
  (St. Gallen repository). Grade: primary, working paper. Same paper as the EFMA 2021 entry
  ("previously circulated under the title End-of-Day Momentum and Option Hedging"); the EFMA copy
  itself could not be fetched (TLS chain error).
- Single stocks, not index futures (stock sample "May 2005 through July 2020"). Abstract: "a large and
  negative (positive) aggregated gamma imbalance ... gives rise to an economically and statistically
  significant end-of-day momentum (reversal) ... the effect generated by leveraged ETFs is
  economically larger ... the documented effects quickly revert at the next day's open."
  Over time: "the impact of both channels has been both economically and statistically significant in
  all subsamples between 2012 and 2019 ... the impact of delta-hedging has increased over time,
  whereas it remained constant for leveraged ETF rebalancing." (A search summary claiming the LETF
  effect "decreased over time" refers to a later SFI version not read here.)

### S9. Liu and Tse, "Overnight returns of stock indexes: Evidence from ETFs and futures",
Int. Rev. Economics and Finance 48 (2017)
- Full text NOT retrieved (bepress SelectedWorks page retired). Only a search-result summary, which
  cites it as finding, for S&P 500 ETFs and 12 international index futures, no predictive power of the
  first half-hour return and positive prediction of the last half-hour by the overnight return.
  Grade: [unverified]. Not used for any number.

### S10. Zarattini, Aziz, Barbon, "Beat the Market: An Effective Intraday Momentum Strategy for
S&P500 ETF (SPY)", working paper (first version 2024-05-10, this version 2025-02-03)
- Saved: `shared/zarattini_aziz_barbon_beat_the_market.pdf` (+ `.txt`), sha256 41d635d162551c4a....
  Practitioner co-authors. This is the noise-area momentum V34 dropped as unsized.
- Unlevered (Table 1): "Momentum Opp.Band 100% 178% 6.2% 10.9% 0.61 54%" (total return, IRR, vol,
  Sharpe, hit ratio), net of $0.0035/share commission; the abstract's 19.6 %/yr and Sharpe 1.33 use
  volatility-targeted leverage. No per-trade gross in bp is reported; trades per day vary. So no sized
  per-trade figure: the V34 drop stands on this reading.

## Searched, not found (gaps, not evidence of absence)
- No post-2015 study of Russell 2000 futures intraday patterns (three searches).
- No 2019-2021 journal study of half-hour periodicity in equity index futures (one search).
- No 2024-2026 peer-reviewed retest of ROD -> LH on index futures beyond the Adams et al. draft and
  the unreviewed SPX retest (one search).
- Credit Suisse (2015) note on small-cap LETF end-of-day rebalancing share: search-summary only,
  [unverified], not fetched.
