# R10 Practitioner books and authors (SourceReader-Practitioner-OpusHigh)

Stage E.25, reader R10. Started 2026-10-18 01:38 PDT; finished 01:55 PDT (`date`).
Overlap files read: r0_mechanism_index.md (present at start), r0_e20_evidence_index.md, r0_prior_sources.md.
Re-used: reports/stage_e20_briefs/shared/zarattini_aziz_barbon_beat_the_market.pdf.txt (E.20 copy, the
2025-02-03 version). R10 also fetched the newer 2025-09-22 version from concretumgroup.com (the texts
differ: the newer one extends the post-publication table to August 2025). All Concretum PDFs are kept
local only (site terms: personal, non-commercial use, no republishing; listed in DO_NOT_COMMIT.txt).

All conversions below are R10 arithmetic on published figures and are shown in full. Hurdle ratios,
ranking and test design belong to the lead.

## 1. Answer (at most 250 words)

Of the practitioner sources, only Concretum's (Zarattini, Aziz, Barbon) are written up as papers with
full rules, cost assumptions and post-publication updates. None of the books (Crabel 1990, Raschke and
Connors 1995, Williams 1999, Chan 2013, Davey 2014) could be read in full text (copyright); every
figure from them below is [secondary-only] or [unverified], and none publishes a true out-of-sample test.

Strongest candidate: noise-area intraday momentum ("Beat the Market"). On SPY, 2007-2024, the
published average profit is $0.09 per share per trade, net, at an average SPY price of $247: 3.64 bp
net, about 4.0 bp gross. At ES 6,000 that is about 2.4 ES points, about 9.6 MES ticks gross, against an
MES hurdle of about 3.0 ticks. The authors also report the same rules on 33 futures from 2007 to
2024-09 (S&P 500 Sharpe 1.32, Nasdaq 1.23, Russell 0.45), but the futures cost assumption is not
stated. The program never screened this rule: V34 dropped it as "unsized", yet the FAQ does size it.
Post-publication returns were +17% (May-Dec 2024) and about +1% (Jan-Aug 2025), with five losing
months out of six from March to August 2025.

Strongest negative: Mesfin (arXiv 2605.04004, 2026). A walk-forward test of opening-range breakout on
MNQ, 2021-2025, found "T = 0.88" with year-unstable results. Also, Holmberg et al. (2013) find that ORB
profits on crude oil come "only in the last time period" (2001-2011). The VWAP trend rule
(Zarattini-Aziz 2023) is the program's K1-vwap-01 (Tier B, failed), and Raschke's 80-20 is
K1-cp3-01/H6 (failed).

## 2. Candidate hypotheses

| id | hypothesis | instruments | entry window CT | hold | trades/yr | best source (grade) | sample / OOS | published effect | price used | gross pts | gross micro ticks | gross/net | overlap | owned / testable |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R10-C1 | Noise-area intraday momentum: bands = max/min(open, prior close) x (1 +/- 14-day mean abs move from open to HH:MM); enter at HH:00/HH:30 checks on a band break; trailing stop = current band or VWAP; flat at close | MES (also MNQ, M2K; paper ran ES/NQ/RTY futures) | 09:00-14:30 at half-hour marks (SPY 10:00-15:30 ET) | intraday, to 15:00 at latest | about 450 on SPY (7,668 trades / 2007-2024) | Zarattini, Aziz, Barbon 2024/2025 WP (working-paper) | SPY 2007-05..2024-04; post-publication 2024-05..2025-08 (authors' own update); futures table 2007..2024-09 | $0.09/share net per trade at average SPY $247 = 3.64 bp net; costs $0.0035/share commission + $0.001 slippage per side -> gross about $0.099 = 4.0 bp | ES 6,000 (5,500 low) | 2.41 (2.21) | 9.6 MES (8.8) | net published; gross R10-derived | none exact; near K1-vwap-01 (stop component), K1-cp2-01 / B-H1 / H1-H5 (opening-range breaks); V34 dropped unscreened | yes (1-min bars; open, prior close, VWAP from own bars) / yes |
| R10-C2 | ATR-band volatility breakout from the open (Crabel "stretch" / Williams volatility breakout, modern form): long on a 15-min close above open + 0.5 x ATR(14), short below open - 0.5 x ATR(14); stop when price returns to the open; exit EOD; optional 5-min counter-move entry overlay | MES, MNQ; crude-oil variant MCL | 08:45-14:45 at 15-min marks | intraday to close | not published | Zarattini & Pagani 2026, QuanTips #2 (vendor research note) + Concretum article 2026 (vendor) | SPY 2007-01..2026-01 (note); 2006-01..2026-01 gross (article) | no per-trade figure; net CAGR "above 13%", Sharpe "approximately 0.87"; gross CAGR 14.1%, Sharpe 0.88; overlay adds about 200 bp CAGR, Sharpe 0.87 -> 0.99 | n/a | null | null | net (note) and gross (article) | none exact; D-H3 (range compression then breakout) and B-H4 differ (opening range, not ATR band from open) | yes / yes |
| R10-C3 | 5-minute ORB in the direction of the first 5-min candle: enter at the second candle's open, stop at the first candle's extreme, target 10R or EOD | MNQ (paper: QQQ) | 08:35 | to 15:00 or stop | about 250 (1,795 trades 2016-01..2023-02) | Zarattini & Aziz 2023/2025 WP (working-paper) | QQQ 2016-2023, in-sample; no OOS; zero slippage assumed | 0.13R per trade net of $0.0005/share; 31% annual at up to 4x leverage. R10-derived lower bound per notional: ln(1.31)/252 = 0.107% of account per trade, /4x = at least 2.7 bp | NQ 22,000 | at least 5.9 (bound) | at least 23.8 MNQ (bound) | net, zero slippage | closest B-H1, K1-cp2-01 (15-min OR, 4-tick break), F3_3 (opening 30 min to last 30 min), H1-H5 (OR30 to 14:58); first-5-min-candle direction with a stop at its extreme and an EOD hold not tested | yes / yes |
| R10-C4 | Fixed-percent ORB from the open, hold to close (Crabel / Williams / Fisher form; HLL 2013, Lundström): buy stop at open x (1 + rho), sell stop at open x (1 - rho), exit at close | MCL (crude), MES | from 08:00 (CL) / 08:30 (ES) | to close | CL rho 1.0%: 1,044 trades over 1991-2011, about 52/yr | Lundström, Umeå WP 861 (2013, rev. 2017) (working-paper); Holmberg, Lönnbark, Lundström FRL 2013 (peer-reviewed; WP version read) | CL 1991-2011, S&P 1991-2010; fixed rho; no costs | CL rho 1.0%: A = 0.0020 (20 bp) per trade; S&P rho 0.5%: A = 0.0004 (4 bp) | CL $65; ES 6,000 | CL 0.13 $/bbl; ES 2.4 | 13 MCL; 9.6 MES | gross (no costs, threshold fills assumed) | K4-cp2-01 (MCL 15-min OR, 4 ticks, 75 bars) and B-H1 differ; open +/- fixed % to close not tested | yes / yes |

Candidates considered and not proposed (with reason):
- VWAP trend trading (Zarattini & Aziz 2023, QQQ). This is K1-vwap-01, already tested on MNQ (Tier B,
  failed). R10's derived estimate is about 0.9 bp per trade net, with zero slippage and $0.0005/share,
  over about 22,000 trades (ln(7.71)/22,000). So it sits at or below the MNQ hurdle once realistic fills
  are applied.
- ORB on Stocks in Play (Zarattini, Barbon, Aziz 2024). It is a cross-section of single stocks
  ranked by relative volume, with no futures analogue in owned data.
- Raschke 80-20 (prior day opens in the bottom 20% and closes in the top 20%, then follow-through the
  next morning). This is K1-cp3-01 and D.1 H6 (prior-close location follow-through): tested, failed.
- Raschke Holy Grail (ADX > 30, first pullback to the 20 EMA) and Turtle Soup. These are daily-bar
  multi-day setups, not intraday; no published OOS; outside the intraday prop scope; E.23 closed the
  program's own triggers at multi-day holds.
- Chan's opening-gap momentum on FSTX (2013 book, about 13% APR, Sharpe 1.4, 2004-2012). These figures
  are [secondary-only] (a forum post) and could not be verified. The same post reports a failed
  replication for 2008-2013 ("barely broke even ... Sharpe of 0 or less"). The nearest test is D-H4
  (gap fade, the opposite sign). Gap continuation on MNQ: Mesfin 2026 reports gross +16.53 points,
  T = 1.46, N = 35 OOS trades (failed).
- Davey and Williams: their evidence is contest records (World Cup Championship of Futures Trading),
  which R7 owns. Davey's bio claims 148%, 107% and 112% in three consecutive contests, 2005-2007
  [secondary-only]. Their published strategies are mostly multi-day.
- Concretum Bitcoin intraday papers: a closed direction (crypto, V39-V41).

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| C1 per-trade profit | $0.09/share, avg SPY $247 | "the average profit per trade is $0.09 per share ... From 2007 to 2024, the average SPY price was $247" | FAQ Q23, p. 40 (2025-02 version) | Zarattini, Aziz, Barbon, "Beat the Market", WP, first version 2024-05-10, https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf | working-paper | pages/R10/concretum_Beat-the-Market.txt (also E.20 shared copy) |
| C1 recent per-trade profit | $0.18/share | "Over the last seven years, the average profit per share has been a robust $0.18." | FAQ Q23 | same | working-paper | same |
| C1 costs | $0.0035 + $0.001 per share | "commission fee of $0.0035 per share ... Additionally, we account for a slippage of $0.001 per share" | section 3, p. 10-11 | same | working-paper | same |
| C1 measured slippage | about $0.001 | "After executing over 1,000 trades, involving more than $50 million in notional value, the average slippage recorded is approximately $0.001, with a median value even lower at $0.0005." | section 4.6 | same | working-paper (authors' own live fills, unaudited) | same |
| C1 headline | Sharpe 1.33, 19.6%/yr net | "achieved a total return of 1,985% (net of costs), an annualized return of 19.6%, and a Sharpe Ratio of 1.33" | abstract | same | working-paper | same |
| C1 unlevered | Sharpe 1.24, 9.7%/yr | "Momentum Curr.Band + VWAP 100% 380% 9.7% 7.7% 1.24 43%" | Table A1 | same | working-paper | same |
| C1 trade counts | 7,668 trades, 1.8/day | "Intra Mom. Curr.Band + VWAP Dyn. 7,668 1.8 37% 0.09" | Table 4 | same | working-paper | same |
| C1 on futures | S&P SR 1.32, Nasdaq 1.23, Russell 0.45 | "We applied the same rules to 33 different futures markets globally, covering 21 commodities and 12 equity indices, between January 2007 and September 2024. Of these, only 2 instruments produced a negative total return. The average Sharpe Ratio across all instruments was 0.60"; rows "Nasdaq Equity 1,533 16.8 13.6 1.23", "Russell Equity 181 6.1 13.6 0.45", "S&P500 Equity 2,501 19.8 14.9 1.32" | FAQ Q13, p. 35 | same | working-paper; futures cost assumption not stated | same |
| C1 parameter sensitivity | optimum lookback 90, VM 1.5 | "The optimal lookback period is 90 days (versus 14 days), which increases the Sharpe Ratio from 1.35 to 1.50." | FAQ Q14 | same | working-paper | same |
| C1 impact-model rerun | Sharpe 1.17 | "The Sharpe Ratio stands at 1.17 (versus 1.33)" | FAQ Q15 | same | working-paper | same |
| C1 NR4 conditioning | 22 bp/day, t 5.14 | "NR4 660 22 5.14 45% 3.2"; "Unconditional 2620 12 5.34 43% 1.7" | Table 5 | same | working-paper | same |
| C1 post-publication | 2024 +32.2%, 2025 (Jan-Aug) +1.0% | rows "2024 8.8 -1.5 -0.4 5.8 -4.3 1.6 8.2 -2.8 4.1 6.7 -2.6 5.7 32.2" and "2025 -1.2 7.6 -0.2 4.3 -2.1 -2 -2 -2.9 1.0" | FAQ Q24 table (2025-09-22 version) | same, newer version | working-paper (authors' own update, not independent) | pages/R10/concretum_Beat-the-Market.txt |
| C1 decay before publication | 2016 -12.8%, 2017 -6.9% | "2016 ... -12.8"; "2017 ... -6.9" | FAQ Q4 table | same | working-paper | same |
| C2 rule | open +/- 0.5 ATR(14) | "The upper band is defined as the session opening price plus one-half of the 14-period ATR" ; "it is closed if the price returns to the session's opening level" | section 3 | Zarattini & Pagani, "Improving Performance with Fast Alphas", QuanTips #2, Feb 2026, https://concretumgroup.com/wp-content/uploads/2026/02/Improving-Performance-with-Fast-Alphas-A-Tactical-Overlay-for-Intraday-Trend-Trading.pdf | vendor | pages/R10/concretum_Improving-Performance-...txt (and _flow.txt) |
| C2 result | CAGR > 13%, SR 0.87 net | "the strategy delivers a double-digit CAGR (Compound Annual Growth Rate) above 13% and a Sharpe ratio of approximately 0.87" | section 3 | same | vendor | same |
| C2 overlay | +200 bp CAGR, SR 0.99 | "The enhanced strategy increases net-of-fee CAGR (Compound Annual Growth Rate) by approximately 200 basis ... points and improves the Sharpe ratio from 0.87 to 0.99." | section 4 | same | vendor | same |
| C2 gross, 2006-2026 | 14.1% CAGR, SR 0.88 | "End-of-day liquidation delivers a 14.1% CAGR, a Sharpe ratio of 0.88, and a maximum drawdown" ; "(gross-of-cost 1 ) intraday-trend framework on SPY, tested from January 2006 to January 2026" | article body | Concretum, "Breaking the Rules of Intraday Trading", https://concretumgroup.com/breaking-the-rules-of-intraday-trading/ | vendor | pages/R10/concretum_breaking-the-rules-of-intraday-trading.html |
| fast alpha fails after costs | 5-min streak reversal | "once standard IBKR commissions are applied ... the strategy's net performance becomes negative" | section 2 / Fig. 2 | Zarattini & Pagani 2026 | vendor | as C2 |
| C3 rule and result | 0.13R, 1,795 trades, 31%/yr | "The Win Rate of the strategy was 24%, which made the average PnL per trade equal to 0.13R." ; "out of 1,795 trades, 51% were long ... The annualized Sharpe Ratio was 1.12 while the annualized rate of return was 31%." | section 3, p. 9-10 | Zarattini & Aziz, "Can Day Trading Really Be Profitable?", WP, first version 2023-04-24, this version 2025-09-22, https://concretumgroup.com/wp-content/uploads/2026/02/Can-Day-Trading-Really-Be-Profitable.pdf | working-paper | pages/R10/concretum_Can-Day-Trading-Really-Be-Profitable.txt |
| C3 fills | zero slippage | "Entry Open of the second 5-minute ... We assumed no slippage in fills." ; "a maximum leverage of 4x, and a commission of $0.0005/share traded" | Table 2; section 3 | same | working-paper | same |
| C3 ATR-stop sweep (in-sample selection) | stop 5% of ATR, TQQQ +9,350% | "the best results were achieved ... with tight stop losses (5% of the 14-day ATR)" ; "this result can under certain circumstances be considered unrealistic as our model assumed no slippage" | section 4 | same | working-paper | same |
| C4 fixed-rho ORB, OOS | CL rho 1.0%: 0.0020; S&P rho 0.5%: 0.0004 | "crude oil 1.0 1044 0.58 0.0020 0.0000"; "S&P 500 ... 0.5 3314 0.49 0.0004 0.0057"; "No trading costs are included." | Table 2, p. 18 | Lundström, "Day trading returns across volatility states", Umeå Economic Studies 861 (2013, rev. 2017), http://www.usbe.umu.se/digitalAssets/194/194520_ues861.pdf | working-paper | pages/R10/umu_ues861.pdf/.txt |
| C4 samples | CL 1991-2011, S&P 1991-2010 | "The crude oil price series covers the period January 2, 1991 to January 26, 2011 and the S&P 500 price series covers the period January 2, 1991 to November 29, 2010." | section 4 | same | working-paper | same |
| C4 in-sample ORB on CL | about 0.20% per trade | "full sample 1% 1.6889 188 0.6117 0.2583 0.0001" (long, alpha 1%); the rho values "are derived from the sample" | Table 2 | Holmberg, Lönnbark, Lundström, Umeå WP 845 = FRL 10(1) 2013, 27-33 | peer-reviewed (WP version read) | pages/R10/umu_ues845.pdf/.txt |
| C4 fills | perfect fill | "we assume a perfect order fill at the threshold price, a zero bid ask spread, as well as zero commissions" | section 3 | same | peer-reviewed (WP version) | same |
| VWAP trend (K1-vwap) | 671% on QQQ, about 22,000 trades | "an initial investment of $25,000 in the VWAP Trend Trading strategy with QQQ would have grown to $192,656, net of commissions" ; "The active VWAP strategies incurred about 22,000 trades." ; "we assumed no slippage in our order fills" | abstract; section 4; section 3.4 | Zarattini & Aziz, "VWAP: The Holy Grail for Day Trading Systems", WP 2023-11-13 | working-paper | pages/R10/concretum_Volume-Weighted-Average-Price.txt |
| Crabel ORB origin | n/a | "Toby Crabel is often credited with first introducing the ORB (back in 1990)" ; "Raschke and Connors [10] introduced the Momentum Pinball strategy ... combining a 60-minute ORB with a 3-day Relative Strength Index" | section 1 | Zarattini, Barbon, Aziz 2024 (citing books) | working-paper citing practitioner-book [secondary-only] | pages/R10/concretum_A-Profitable-Day-Trading-...txt |
| Chan FSTX gap strategy | APR about 13%, Sharpe 1.4, 2004-2012 | (search-result summary of a futures.io post; not retrieved) | n/a | Chan 2013, Algorithmic Trading, ch. 7 | practitioner-book [secondary-only][unverified] | not saved (forum; pointer) |
| Davey contest returns | 148%, 107%, 112% | (search-result summary of the publisher's author bio; not retrieved) | n/a | Davey 2014, Wiley bio | practitioner-book [secondary-only][unverified]; R7 owns WCC | not saved |

## 4. Negative evidence

- ORB on MNQ, walk-forward 2021-2025 (Mesfin, arXiv 2605.04004, May 2026, an independent single-author
  preprint): "the Opening Range Breakout long at a 15-bar hold (net +2.82 points, T = 0.88 on net
  returns)"; OR = "09:30-09:55 ET"; friction "For MNQ: 2.0 points ($4.00 per micro contract)"; "Eleven
  families fail because gross return before friction is 0.07-1.50 points, below the 2.0-point friction
  floor." Gap continuation short: "gross +16.53 points, net +14.52 points, T = 1.46 ... fails year
  stability and the per-fold trade count minimum."
- Crude-oil ORB is time-unstable (Lundström 2017, on HLL 2013): "HLL (2013) find significantly positive
  returns only in the last time period, ranging from 2001-10-12 to 2011-01-26, which are thus not robust
  to time." HLL Table 2, 1992-06-30..2001-10-11, short side at alpha 1%: "-0.0258 0.6814".
- S&P fixed-rho ORB fades at wider thresholds (Lundström Table 2): "For ranges larger than rho = 1.0,
  e.g., rho = 1.5 and rho = 2.0, we cannot reject the null hypothesis of zero returns on average."
  Expansion days are not predictable: "We tried various ARCH and GARCH specifications to predict the
  volatility state, but without improving the results in any significant way."
- Noise-area momentum, decay pattern: the strategy lost money in 2016 (-12.8%) and 2017 (-6.9%). The
  authors' own citation: "Rosa [7] analyzes additional data post-2013, noting a decline in
  predictability". The 2025 post-publication months from March to August were -0.2, 4.3, -2.1, -2,
  -2, -2.9 (five losing months of six), giving +1.0% for Jan-Aug 2025.
- No independent academic replication: OpenAlex lists 0 citing works for "Beat the Market" (W4396887499,
  W7208629361) and only the authors' own papers citing the ORB and VWAP papers (W4366957240: 4 citers,
  all Zarattini; W4389319238: 3 Zarattini plus 1 unrelated review). A TradingView user's implementation
  (pointer only, via search results) reported smaller returns and a "very low" Sharpe.
- Zero-slippage assumptions: C3 ("We assumed no slippage in fills") and VWAP ("we assumed no slippage
  in our order fills") are both sensitive to stop slippage. For TQQQ, the authors write that a 5%-ATR stop
  "implies a stop width of $0.08 ... the stop will likely be exceeded".
- Fast alphas (5-minute streak reversal on SPY): "once standard IBKR commissions are applied ... net
  performance becomes negative" (the authors' own negative result).
- Chan's FSTX gap strategy: a third-party replication reportedly "barely broke even" from 2008 to 2013
  [secondary-only].
- Selection bias: the Concretum authors run a research firm, and Aziz runs a trading community (Bear
  Bull Traders), so the papers double as marketing. The post-publication tables are the authors' own
  (unaudited). The futures table hides 29 of 33 instrument names, its cost assumption is not stated,
  and it was published after the SPY result was known.

## 5. Data and cost

- R10-C1, C2, C3 and C4 need only 1-minute OHLCV for MES/MNQ/M2K/MCL plus session open, prior close and
  session VWAP (VWAP from 1-minute bars as in K1-vwap-01). The program owns these (section 4 of the
  brief): research window 2025-04-01..2026-06-19, plus MES 2019-05..2025-03 (holdout-2 sealed) and 17
  roots 2010-2024 (NQ, CL, RTY). No purchase is needed. C1's 14-day lookback and C2's ATR(14) need
  15 prior sessions. C2's "14-period ATR" bar length is not stated explicitly. R10 reads it as daily
  because the bands are fixed "At the beginning of each trading session" (unverified; ask the authors or
  test both readings in the design).
- The VIX filter (C1 FAQ Q20) would use Cboe VIX daily history, which is owned.
- Concretum code: FAQ Q1 offers code ("Can you share the code used to backtest the strategy?"). R10
  did not open any download or sign-up. Site terms: personal, non-commercial use only.

## 6. Prop compatibility

- C1: SPY trades are inside the RTH session and flat at the close (16:00 ET = 15:00 CT), before Topstep's
  15:10 CT flatten. About 1.8 trades a day, so no HFT. Entries are at half-hour marks only, so
  semi-manual execution is possible (V39). Volatility-targeted sizing up to 4x maps to 1 to a few MES.
  On the P06 rule, entries at 09:00 CT checks can fall near 09:00 ET-scheduled releases; the 08:30 CT
  releases come before the first check (10:00 ET). The daily loss limit (DLL) binds on gap days. The
  consistency rule: the hit ratio is 37-43% with right-skewed days (best day +9.1%), which may strain
  "best day below 55% / at most 40%".
- C2: flat EOD, 15-minute decisions, stop at the open. Compatible on the same terms as C1.
- C3: one trade a day at 08:35 CT with a stop at the first candle's extreme. Compatible. It is
  stop-slippage sensitive, and P06 matters on 08:30 CT release days (the first 5-minute candle IS the
  release reaction).
- C4: one trade a day, flat at the close. Compatible. CL entries near the 09:30 CT Wednesday EIA release
  fall under P06.
- No firm-specific data in these sources. R9 owns firm rules.

## 7. Overlap with tested mechanisms

- C1: no exact match. K1-vwap-01 (MNQ, sign versus VWAP, stop-and-reverse) is C1's trailing-stop
  component only. B-H1/B-H3/H1-H5 (MES), K1-cp2-01 (MNQ) and RT1-RT4 are fixed opening-range breaks with
  4-tick thresholds and fixed holds, whereas C1 uses a time-of-day-varying band from 14-day mean
  absolute moves, gap-adjusted, checked every 30 minutes, with a trailing stop and an EOD exit. V34
  dropped it unscreened ("unsized; ... close to the failed opening-range family"). Gate 0 features
  g07_range and g05_gap are not this rule.
- C2: no exact match. D-H3 (20-bar range compression then breakout) and B-H4 (narrow OR15 breakout)
  measure the range differently. The C2 trigger is the distance from the session open in daily-ATR units.
- C3: closest are B-H1 (15-min OR, 4-tick break, 5/75-minute hold), K1-cp2-01 (MNQ, 15-min OR, 75 bars),
  F3_3 opening_30min_to_close_momentum (signal at 09:00, trade 14:30-15:00) and H family OR30 to 14:58.
  C3's own setup (direction of the first 5-minute candle, stop at its extreme, EOD hold) was not tested.
- C4: K4-cp2-01 (MCL/NG, 15-min OR, 75 bars) and B-H1 (MES). Open +/- fixed % to close was not tested.
- VWAP trend = K1-vwap-01 (tested, Tier B). 80-20 = K1-cp3-01 and D.1 H6 (tested). NR4/NR7 = D.1 H1/H2
  (tested as OR30 breakouts on MES). Note that BtM Table 5 conditions the noise-area rule (not an ORB)
  on NR4: 22 bp/day, t 5.14.

## 8. Verdict checks (R10 is not a re-dig reader; listed because the objective asks what was tested)

- V34 (2026-10-10), "noise-area momentum (unsized; the latter close to the failed opening-range
  family)": WEAKENS the "unsized" basis. The FAQ (Q23, in the version E.20 already held) sizes it:
  "the average profit per trade is $0.09 per share ... the average SPY price was $247" (3.64 bp net,
  about 9.6 MES ticks gross at ES 6,000). E.20's product_RTY row recorded "no per-trade figure". The
  FAQ Q13 futures table (S&P 500 Sharpe 1.32, Nasdaq 1.23 over 2007..2024-09) also bears on
  transferability. The "close to opening-range family" reasoning is a judgment for the lead; the rule
  differs as described in section 7.
- K1-vwap-01 / E.7 Tier B: SUPPORTS. The source paper assumed "no slippage in our order fills" over about
  22,000 trades, and its own footnote warns "significantly higher commission rates can affect the
  strategy's effectiveness".
- D.1 B/H families and K1-cp2-01 (ORB failures): SUPPORTED by Mesfin 2026 (MNQ ORB "T = 0.88").
  Lundström's "not robust to time" points the same way.

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://concretumgroup.com/robots.txt | 2026-10-18T08:40Z | n/a (read inline) | not saved | ok | curl |
| https://concretumgroup.com/terms-of-use/ | 2026-10-18T08:41:13Z | 2cd37b3ba39ff0474c7f6e9ef32ebcbbf18eb69d80a40d0058dca7f589ae4d3e | terms/concretumgroup.com_terms.html | ok | curl |
| https://concretumgroup.com/papers/ | 2026-10-18T08:41:36Z | 179ab163bec57e24e263dbe8ed380ccae26c5b08cfba0cbaad994279e24f27ba | pages/R10/concretum_papers.html | ok | curl |
| https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf | 2026-10-18T08:41:49Z | 865010dfd938d513c1cd22a7be5932bc232afe498c3cf493d6d8bd4b0de86ebb | pages/R10/concretum_Beat-the-Market.pdf | ok | curl |
| .../2026/02/Can-Day-Trading-Really-Be-Profitable.pdf | 2026-10-18T08:41:55Z | bb800b06ee8e28c9fb40826a4b086f03e7268eec351152e8b970838f76e51fc8 | pages/R10/concretum_Can-Day-Trading-Really-Be-Profitable.pdf | ok | curl |
| .../2026/02/A-Profitable-Day-Trading-Strategy-For-The-U.S.-Equity-Market.pdf | 2026-10-18T08:42:02Z | 9423012e9f0199e3f6925c500725815c236d7ddbdd7500d50d10bac2be745e91 | pages/R10/concretum_A-Profitable-Day-Trading-Strategy-For-The-U.S.-Equity-Market.pdf | ok | curl |
| .../2026/02/Volume-Weighted-Average-Price.pdf | 2026-10-18T08:42:09Z | 47137abd00730dd6970d5d6409b3908342d63d75ecfc9cf2badc7d206f6905c8 | pages/R10/concretum_Volume-Weighted-Average-Price.pdf | ok | curl |
| .../2026/02/The-Power-Of-Price-Action-Reading.pdf | 2026-10-18T08:42:15Z | 754a770d6e9c667ce482608c75eb064c398b85bc8744d017dff33e9dab5a65cf | pages/R10/concretum_The-Power-Of-Price-Action-Reading.pdf | ok | curl |
| .../2026/02/Improving-Performance-with-Fast-Alphas-A-Tactical-Overlay-for-Intraday-Trend-Trading.pdf | 2026-10-18T08:42:22Z | 4904a802a0aefb133d356330d7156270c6249e5eccac006cae9206b674501c47 | pages/R10/concretum_Improving-Performance-with-Fast-Alphas-A-Tactical-Overlay-for-Intraday-Trend-Trading.pdf | ok | curl |
| https://concretumgroup.com/research/ | 2026-10-18T08:45:05Z | 01701bfdc63dc11deb93f201cca3042d3034c8e94ee56ac90f7ca10af1753383 | pages/R10/concretum_research.html | ok | curl |
| https://concretumgroup.com/articles/ | 2026-10-18T08:45:17Z | dd853909806d781737efabd6ec8a896cc389a37be0692674ede760f212f0a152 | pages/R10/concretum_articles.html | ok | curl |
| https://concretumgroup.com/trading/ | 2026-10-18T08:45:25Z | cff1bd668d9244188608b0b2437fdc80ec4bda8d2d46a9252d78ad164e393293 | pages/R10/concretum_trading.html | ok | curl |
| https://concretumgroup.com/breaking-the-rules-of-intraday-trading/ | 2026-10-18T08:45:41Z | 35177ad115e8f36e61666b87c0462075c5b22005c3d2d0448fe5a33e36b9ee9c | pages/R10/concretum_breaking-the-rules-of-intraday-trading.html | ok | curl |
| https://concretumgroup.com/when-execution-delays-erode-short-term-alpha/ | 2026-10-18T08:45:49Z | 0c0c9bb3087c5f0b453003c2a51b25ef1072bdea2f5b8b39713bf98ea1afeb51 | pages/R10/concretum_when-execution-delays-erode-short-term-alpha.html | ok | curl |
| https://concretumgroup.com/automating-intraday-strategies-from-manual-complexity-to-algorithmic-precision/ | 2026-10-18T08:45:56Z | d8c1e111c737bba9367b2651e75356b866242686c91faf59bce56031f7feccf7 | pages/R10/concretum_automating-intraday-strategies-from-manual-complexity-to-algorithmic-precision.html | ok | curl |
| https://arxiv.org/pdf/2605.04004 | 2026-10-18T08:47:18Z | d0bd26e424a0c81bbca149e35566a3b9929a3cd207934e07638a99e78ca4ca80 | pages/R10/arxiv_2605.04004.pdf | ok (arxiv terms: existing terms_log line) | curl |
| https://swopec.hhs.se/umnees/abs/umnees0845.htm, ...0861.htm, ...0948.htm | 2026-10-18T08:48Z | not kept (scratch) | scratch only | ok (robots.txt read: disallows /scripts/ /test/ /RePEc/ only) | curl |
| https://ideas.repec.org/p/hhs/umnees/0861.html, .../0845.html | 2026-10-18T08:49Z | not kept (scratch) | scratch only | ok (terms_log line ideas.repec.org) | curl |
| http://www.usbe.umu.se/digitalAssets/194/194520_ues861.pdf | 2026-10-18T08:49:32Z | 7c71f315bd897780eda0c35328eb1cb966974bc929df240b7fb85fd7d7bf631d | pages/R10/umu_ues861.pdf | ok (no robots.txt served; university working-paper series, single named PDF) | curl |
| http://www.econ.umu.se/DownloadAsset.action?contentId=196616&languageId=3&assetKey=ues845 | 2026-10-18T08:49:40Z | 3bbf81e2f9bfb11f1e2622077b3c064ffc541e697fa57729ba55767b375cbeee | pages/R10/umu_ues845.pdf | ok (as above) | curl |
| WebSearch x 8 (noise-area replication; Holmberg; Lundström; Chan x2; Crabel; Davey x2; Raschke) | 08:43-08:53Z | n/a | n/a | ok; results used as pointers only | WebSearch |
| firecrawl_research_search_papers x 2 | 08:47Z, 08:52Z | n/a | n/a | ok | Firecrawl research |

Terms read: concretumgroup.com (new terms_log line); arxiv.org and ideas.repec.org (existing lines).
swopec.hhs.se and umu.se: robots.txt only; no terms page located (gap; single named PDFs only).
Not fetched: futures.io / NexusFi (forum, pointer only), pirate PDF mirrors of Chan's book (never), SSRN
(blocks automation; the Concretum site hosts the same papers), oxfordstrat.com (vendor blog, pointer).

Budget notices:
- 2026-10-18T08:44Z: Semantic Scholar keyless search: "Too Many Requests" (1 call); logged throttled, not retried.
- 2026-10-18T08:47:02Z (01:47 PDT): OpenAlex: "Rate limit exceeded ... Insufficient budget. This request
  has no API key, so it counts against the free daily budget shared by everyone on your network's IP
  address, and that budget is used up ($0 remaining; resets at midnight UTC)". .env has OPENALEX_EMAIL
  only. Six forward-citation calls before this time succeeded.
- 2026-10-18T08:48Z: Firecrawl firecrawl_search: "Insufficient credits to perform this request." Web search
  fell back to WebSearch (8 calls used of 45). firecrawl_research_search_papers still worked at 08:52Z.

## 10. Unfinished and unverified

- Book full texts (Crabel 1990, Raschke and Connors 1995, Williams 1999, Chan 2013, Davey 2014/2019)
  were not read. Every figure from them is [secondary-only] or [unverified]. Davey and Williams contest
  records belong to R7.
- Forward citations after 08:47Z could not be checked (OpenAlex budget gone, Semantic Scholar
  throttled). Concretum, HLL 2013 and Lundström forward-citation sweeps are incomplete.
- C1 futures (FAQ Q13): cost assumption and per-trade figures not published. 29 of 33 instrument names
  masked. Authors offer details by email (not contacted).
- C1 gross: R10 adds the paper's own costs ($0.009/share round trip) to the net $0.09. The $247 is a
  time-average SPY price, not trade-weighted. The $0.18/share "last seven years" figure was not converted
  (the paper gives no average price for that window).
- C3 per-trade size is an R10-derived lower bound (account return / 4x leverage cap), not published.
- Pointer for the lead, outside R10's objective: Mesfin 2026's two "positive controls" on MNQ (GMM
  regime signals; "RTH Confluence ... mean net +11.82 points, N = 196"; the author notes the GMM fit
  "contaminates the W1 OOS fold") were not assessed.
