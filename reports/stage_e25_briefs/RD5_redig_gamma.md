# RD5: re-dig of the pre-2022 dealer-gamma and GEX sources (RedigReader-DealerGamma-OpusHigh)

Stage E.25, research only. Written 2026-10-18 01:38-01:52 PDT. Scope: the gamma/GEX sources E.13 cited (INF section 2.7(a),
I-37b, I-39, I-40, I-47, I-48), the C2 pre-registration draft (reports/stage_e13_prereg_gexmom.md), the E.20 GEX ruling
(reports/stage_e20_briefs/product_NQ.md section 4), Baltussen et al. (2021) Tables 7-8 (on disk), and the pre-2022 gamma
literature: Ni, Pearson, Poteshman and White (RFS 2021), Barbon and Buraschi (Gamma Fragility, 2020), Anderegg, Ulmann and
Sornette (JIMF 2022), SqueezeMetrics' GEX white paper (2017), and their forward citations. The 0DTE-era papers (2022-2026)
belong to R1 (reports/stage_e25_briefs/R1_0dte_academic.md; still a skeleton when this file was written); one of them,
Adams et al. (2026), is already on disk from E.20 and is quoted here only for the measure question the spawn message asks.

## 1. Answer (at most 250 words)

The deeper reading supports both gamma verdicts and answers the measure question in the negative.

- **The 135-date stop was not a measure artifact.** SqueezeMetrics' GEX and Baltussen et al.'s NGE are the same
  construction (market makers long every call, short every put; only the scaling differs), and the paper itself checked
  SqueezeMetrics against OptionMetrics, 2002-2017: "virtually identical results". The paper's 48% negative share therefore
  cannot hold in 2011-2019, where E.14 counted 135 negative dates (about 7%). Derived: at least about 2,700 of the paper's
  2,930 negative-NGE days fall before May 2011, so Table 7's conditional slope is identified mainly on 1996-2010 data.
- **A better measure makes the count smaller, not larger.** With signed Cboe Open-Close positions (Adams et al. 2026,
  2018-2024), market makers' net gamma "is positive for 88 percent of all 10-minute trading intervals" and its monthly
  average "is always positive". The sign of the conditional effect matches Baltussen (momentum at low gamma, reversal at
  high gamma), but it is small (about 0.7 bp at 1-2 h in the lowest quartile, not a trade return), and the authors say
  it "does not translate into a feasible trading strategy".
- Barbon and Buraschi: the autocorrelation effect is "limited" (1% of a standard deviation per standard deviation of
  gamma imbalance). Their gamma variable predicts the size of moves, not their direction.
- No forward citation re-tests the S&P gamma-conditioned last-half-hour rule out of sample or after costs.

New candidates: none sized. One unsized pointer (RD5-C1, signed market-maker position change to the SPX futures
end-of-day return) needs paid signed SPX option data.

## 2. Candidate hypotheses

| id | hypothesis | status |
|---|---|---|
| RD5-C1 | Change in option market makers' net SPX option position (from signed high-frequency SPX trades) predicts the end-of-day S&P futures return (Egebjerg and Kokholm, working paper) | UNSIZED: seminar abstract only [secondary-only]; the full text (SSRN 4936978) was not retrieved; data (signed SPX trades by participant type) not owned; listed so the lead can decide whether R1/R2 should pursue it. Not prop-ready. |

No sized candidate. Why zero: every pre-2022 gamma source sizes volatility, autocorrelation or regression slopes, not a
per-trade gross; the one directional, futures-level, gamma-conditioned rule (Baltussen Table 7) is the rule already run as
E20H6-T3 (on NQ) and drafted as C2 (on ES), and the deeper reading below says its post-2011 base is thin.

## 3. Evidence table

| # | claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|---|
| 1 | Baltussen NGE sign convention: MMs long all calls, short all puts | n/a | "we assume option market makers are short allpositions puts and and long precise all calls" (garbled extraction of footnote 8; eq. 14 uses "the adjustment of -100 ... short gamma for option market makers" on puts) | p. 397 area, eq. (14)-(15), footnote 8 (md lines 1942-1990) | Baltussen, Da, Lammers, Martens, JFE 142 (2021) 377-403 | peer-reviewed | reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md |
| 2 | SqueezeMetrics checked against OptionMetrics | 2002-2017 | "We have verified the computations of SqueezeMetrics using OptionMetrics data over the 2002 to 2017 period, yielding virtually identical results." | footnote 7 (md line 1990) | same | peer-reviewed | same |
| 3 | Whole-sample negative share | 2930 neg / 3158 pos | "In the period from 1996 until May 2020 there have been 2930 days with a negative NGE and 3158 with a positive one." | section 4.1 (md 1974-1976) | same | peer-reviewed | same |
| 4 | Table 7 conditional slope | b 6.63 (t 4.78) if NGE<0; 0.82 (t 1.03) if NGE>=0 | "NGEt-1 < 0 \| -0.01 (-0.63) \| 6.63*** (4.78) \| 3.58" | Table 7 (md 2060-2061) | same | peer-reviewed | same |
| 5 | Table 8 continuous form; authors control for a shared time trend | NGE x rROD -123.04 (t -3.42) | "The last two columns confirm that these results are not driven by a time trend shared by intraday momentum and NGE by running a difference-in-difference regression." | section 4.1 and Table 8 | same | peer-reviewed | same |
| 6 | SqueezeMetrics GEX assumptions (same sign convention) | n/a | "2. Call options are sold by investors; bought by market-makers." and "3. Put options are bought by investors; sold by market-makers." | p. 4, "Four Assumptions" | SqueezeMetrics (Prior Analytics LLC), "Gamma Exposure", December 2017, https://squeezemetrics.com/monitor/download/pdf/white_paper.pdf | vendor | pages/RD5/sqzm_gex_white_paper.pdf (DO_NOT_COMMIT) |
| 7 | GEX is sold as a variance forecaster, not a direction signal | 1-day SD 0.55% vs 0.85% (top two GEX quartiles) | "When instead we compare the highest and second-highest** quartiles of GEX to subsequent SPX variance, the 1-day standard deviations are 0.55% and 0.85%, respectively." | p. 2 | same | vendor | same |
| 8 | Gamma Fragility: data, sign proxy | 4 indices + 276 stocks, 1996-2017 | "If dealers are long call options and short put options, the aggregate imbalance is proportional to the difference between the aggregate gamma of the call minus the aggregate gamma of the put options" | section II.B, eq. (3) (txt 556-565) | Barbon and Buraschi, "Gamma Fragility", SoF HSG WP, 5 Nov 2020, https://alexandria.unisg.ch/handle/20.500.14171/111591 | working-paper | pages/RD5/barbon_buraschi_2020_gamma_fragility.pdf |
| 9 | Gamma Fragility: autocorrelation effect small | 1% of SD | "The economic magnitude of the result, however, is limited. A unitary standard deviation increase in the gamma imbalance proxy is associated to a decrease in autocorrelation of about 1% of a standard deviation." | section III, after eq. (6) (txt 846-850) | same | working-paper | same |
| 10 | Gamma Fragility: index volatility effect | > 20 bp of abs daily return per SD | "one standard deviation increase in the gamma imbalance is associated to a decrease in absolute return of the underlying index of more than 20 basis points (about 20% of a standard deviation)" | Table III discussion (txt 751-753) | same | working-paper | same |
| 11 | Better (signed) measure: MM net gamma mostly positive | 88% of 10-min intervals; monthly average always positive | "The market makers' net gamma is positive on average and throughout most of our sample. Figure IA2 shows that Net Γt is positive for 88 percent of all 10-minute trading intervals." ... "Summing 0DTE and non-0DTE exposures, we find that the monthly average is always positive." | section 3 (txt 660-665) | Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov, "Do S&P 500 Options Increase Market Volatility? Evidence from 0DTEs", draft 15 Jul 2026 (R1 owns) | working-paper | reports/stage_e20_briefs/shared/adams_etal_0dte_fontaine.pdf.txt |
| 12 | Signed-measure conditional momentum small, not tradable | low quartile about 0.7 bp at 1-2 h; Q1-Q4 -1 to -3 bp | "they increase monotonically from almost zero in the next 10-minute interval to around 0.7 bps at the 1- and 2-hour horizons." ... "this result does not translate into a feasible trading strategy since the market makers' net gamma is not observable to other investors." | section 4.4, Table 7 (txt 1130-1152) | same | working-paper | same |
| 13 | Authors' later work: NGE assumption admitted as measurement error | n/a | "The above N GE measure relies on the assumption that market makers are short the entire put and long the entire call open interest at each point in time (see Baltussen et al. (2021)), which introduces measurement errors." | section 4/5, p. 20-21 (txt ~1298) | Baltussen, Da, Soebhag, "End-of-Day Reversal", WP April 2025, https://www3.nd.edu/~zda/EOD.pdf | working-paper | pages/RD5/baltussen_da_soebhag_eod.pdf |
| 14 | Later work: market-level TS momentum in a stock-level decomposition | 2.79 bp/day, 1993-2019, gross | "Further, we show the expected profit of the TS strategy, which is 2.79 basis points per day, in line with intraday momentum at the market-level." | section 4, Table 5 (txt 1097-1099) | same | working-paper | same |
| 15 | Later work: stock-level gamma interaction holds but does not explain EOD reversal | t -4.76 on ROD3 after gamma control | "Interestingly, the coefficient on ROD3 remains highly significant (t-statistic = -4.76) after controlling for gamma hedging demand from individual stock options." | section 5, Table 7 (txt ~1262) | same | working-paper | same |
| 16 | Barbon et al. (2021) use signed open-close data (better measure) for stocks | 2012-2019 (TAQ), May 2005-Jul 2020 (options) | "The dataset includes information on signed trading volume, the identity of the coun-" [terparty] | data section (txt 393) | Barbon, Beckmeyer, Buraschi, Moerke, S/BF-HSG WP 2021/14 (E.20 RTY E12) | working-paper | reports/stage_e20_briefs/shared/barbon_beckmeyer_buraschi_moerke_letf.pdf.txt |
| 17 | Anderegg et al.: reconstructed dealer gamma (trade-repository data, FX) is negative; volatility effect only | EURUSD +0.7%, USDJPY +0.9% vol at about -1000 bn USD gamma | "we first reconstruct the aggregated OMM's gamma exposure by using trade repository data and find that it is negative" | abstract (OpenAlex abstract index; full text not fetched) | Anderegg, Ulmann, Sornette, J. Int. Money and Finance (2022) 102627 | peer-reviewed [secondary-only] | none (OpenAlex record W4213420418, scratch) |
| 18 | Egebjerg and Kokholm: signed MM position change predicts SPX futures end-of-day return (unsized) | none | "we estimate changes to the net option position of OMMs over an extended period and find that the change is a strong predictor of the end-of-day return on SPX futures" | seminar abstract | Egebjerg and Kokholm, "A Model for the Hedging Impact of Option Market Makers", SSRN 4936978 (2024); Aarhus seminar page | working-paper [secondary-only] | pages/RD5/au_egebjerg_seminar.html |
| 19 | Maurer (2026): dealer gamma adds to overnight-gap size forecasts only when VIX is low | none quoted (WebFetch summary only) | (no verbatim quote; WebFetch returned a summary) | OptionMetrics research page | M. Maurer, SSRN 6650858 (2026) | working-paper [secondary-only] [unverified] | pages/RD5/om_maurer_2026.html (Cloudflare block page only) |

## 4. Negative evidence

- **No out-of-sample, post-2020 or after-cost re-test of the S&P gamma-conditioned last-half-hour rule exists among the
  forward citations.** OpenAlex lists 94 works citing Baltussen et al. (W3106590193, 2026-10-18 08:42Z). The gamma-related
  ones are stock cross-sections (Barbon et al. 2021; Soebhag 2023; Baltussen-Da-Soebhag 2025), simulations (Buis et al.,
  JEDC 2024: "we study the effect of the gamma positioning of dynamic hedgers on market quality through simulations"),
  option-return papers (Willeboordse, FRL 2026), China (Yuan and Li 2022; Zheng and Luo 2024), bitcoin (Weiss et al. 2026;
  crypto closed, V39-V41), or 0DTE (Dim-Eraker-Vilkov, Adams et al., Vasquez et al.: R1's). Gamma Fragility has 4 citing
  works; Ni et al. (W3122647810) 95, none an index-futures intraday direction test outside R1's set.
- Gamma Fragility (row 9): autocorrelation effect "limited". Its strong results are about volatility, range and flash
  crashes (rows 10; "a one standard deviation decrease in gamma imbalance is associated to an increase of roughly 15 basis
  points in the daily spread", txt 914-916), i.e. size, not sign.
- SqueezeMetrics' own white paper (row 7) presents GEX as a variance forecaster; it makes no claim about the sign of the
  next move, and its only return claim is a cross-sectional stock screen ("screening for a GEX near zero yielded excess
  returns", unsized, p. 7).
- Adams et al. (row 12): with the better measure, conditional momentum is about 0.7 bp at best and "not observable to
  other investors" in real time.
- Baltussen-Da-Soebhag (row 15): gamma hedging "contribute[s] to the end-of-day reversal, they do not fully explain it";
  Barbon et al. (2021) report the end-of-day effects "quickly revert at the next day's open" (abstract).
- Period concentration (derived, not published): E.14 counted 135 calendar-eligible GEX < 0 dates in 2011-05-03..2019-04-30
  (calendar-free bound 146; reports/E.14_RETURN.md line 317) and E.20's T3 had 39 GEX < 0 trades in 2019-05-06..2020-05-29
  (reports/E.20_RETURN.md line 290). Since GEX and NGE share a sign (rows 1, 2, 6), at most about 146 + 50 of the paper's
  2,930 negative days fall after April 2011, so at least about 2,700 fall in 1996-01..2011-04 (about 3,800 trading days,
  roughly 70% negative). The paper's Table 7 is therefore identified mostly on pre-2011 data, a regime that has not
  recurred. The lead should check this arithmetic; it uses only counts already on record.
- Illustrative only, [derived; scale unverified]: Table 8 column (3) gives r_LH slope = 2.58 - 123.04 x NGE (x100 units).
  The Fig. 3 extraction shows axis values 0.02 (2012, 2016) and 0.06 (2020), which would put the slope near 0.1 and -4.8,
  i.e. no momentum or reversal at typical post-2011 positive NGE. The figure's numbers may be axis ticks, not data; do not
  use without the figure itself.

## 5. Data and cost

- RD5-C1 needs signed SPX option trades by participant type (Cboe Open-Close Volume Summary, intraday or daily, or a
  LiveVol/DataShop equivalent). Not owned (brief section 4: no options data). Price not read here (R2 owns cboe.com and
  OPRA/Databento pricing; cite R2). Adams et al. list their source: "Cboe Open-Close Volume: Intraday open-close volumes at
  10-minute frequency from 01/2018 to 12/2024" (txt 1641-1642).
- A better daily sign than SqueezeMetrics' GEX (signed end-of-day open-close positions) is the same paid Cboe product; the
  evidence above says it would label fewer days "dealers short gamma", not more.
- SqueezeMetrics: the white paper's disclaimer says it "may not be used, published, or redistributed without the prior
  written consent of Prior Analytics LLC" (p. 1); the RD5 copy is listed in DO_NOT_COMMIT.txt. The DIX/GEX CSV terms ruling
  stands as in E.20 product_NQ.md section 4c.

## 6. Prop compatibility

RD5-C1 (if ever sized): an end-of-day S&P futures trade ends by the 15:00 CT cash close, before the 15:10 CT flatten;
one trade a day; no HFT; automatable on a daily signal if the data arrive intraday (10-minute Open-Close data would be
needed in real time, which Adams et al. say other investors do not observe). The P06 news rule binds only on release days.

## 7. Overlap with tested mechanisms

- RD5-C1 overlaps E20H6-T1..T3 (last-half-hour window on NQ) and C2 (S&P late session, GEX-conditioned) in timing; it
  differs in the signal (change in signed market-maker positions, not price momentum and not the GEX sign). Index ids:
  r0_mechanism_index.md lines 204, 231-233, 274 ("gamma/GEX: E20H6-T3; C2 (stopped)").
- Barbon et al. (2021) LETF rebalancing: E.20 RTY E12 (sources only, never a trial).

## 8. Verdict checks (re-dig)

| verdict | effect | quote | source |
|---|---|---|---|
| E.14 C2 stopped at its power rule (135 < 200 GEX < 0 dates, 2011-05..2019-04) | SUPPORTS | "We have verified the computations of SqueezeMetrics using OptionMetrics data over the 2002 to 2017 period, yielding virtually identical results." (with the shared sign convention, white paper assumptions 2-3). The low count is a property of 2011-2019, not of SqueezeMetrics' construction. | Baltussen et al. 2021 fn 7; SqueezeMetrics 2017 p. 4 |
| E.13 prereg C2 section 7 power assumption (48% share, about 920 trades) and E.13 lead note ("SqueezeMetrics' GEX column is a different construction") | WEAKENS | Same quote as above, plus "In the period from 1996 until May 2020 there have been 2930 days with a negative NGE": the 48% is a whole-sample share dominated (derived) by 1996-2010; the construction differs only in scaling (dollars per 1% move versus division by market value), not in sign. | Baltussen et al. 2021 section 4.1 and fn 7 |
| E20H6-T3 FAIL (134 trades, gross -3.52 ticks) | SUPPORTS | "this result does not translate into a feasible trading strategy since the market makers' net gamma is not observable to other investors" and the low-gamma momentum is "around 0.7 bps at the 1- and 2-hour horizons" (S&P, 2018-2024, signed measure). No forward citation re-tests the rule on NQ or after costs. | Adams et al. 2026 section 4.4 |
| Spawn question: does net dealer gamma from open interest or signed positions change the count or the sign? | SUPPORTS the existing verdicts (count falls, sign unchanged) | "Net Γt is positive for 88 percent of all 10-minute trading intervals." / "the monthly average is always positive." | Adams et al. 2026 section 3 |
| E.13 INF 2.7(a) verdict "evidence moderate" for gamma conditioning | WEAKENS | "The economic magnitude of the result, however, is limited. A unitary standard deviation increase in the gamma imbalance proxy is associated to a decrease in autocorrelation of about 1% of a standard deviation." | Barbon and Buraschi 2020, section III |
| E.13 INF 2.7(a): GEX as a conditioning variable rather than a stand-alone signal (and R12's volatility-filter question) | SUPPORTS (as a size or range filter only) | "one standard deviation increase in the gamma imbalance is associated to a decrease in absolute return of the underlying index of more than 20 basis points" | Barbon and Buraschi 2020, Table III discussion |

## 9. Fetch log, terms, budget notices

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://api.openalex.org/works?search=... and filter=cites:W3106590193, W3122647810, W4244722880, W4213420418; author.id filters (Baltussen A5067518819, Da A5055383535, Pearson A5049465404) | 2026-10-18T08:40Z-08:45Z | n/a (JSON in scratch) | scratchpad/RD5/*.json | ok | curl (OpenAlex polite pool) |
| https://api.openalex.org/works?filter=openalex:... (abstract batch 2) | 2026-10-18T08:46:21Z | n/a | none | throttled ("Rate limit exceeded ... free daily budget ... used up") | curl |
| https://alexandria.unisg.ch/server/api/pid/find?id=20.500.14171/110335 and /111591; items/.../bundles | 2026-10-18T08:42Z | n/a | scratchpad/RD5/unisg_*.json, b_*.json | ok | curl |
| https://alexandria.unisg.ch/server/api/core/bitstreams/25fec636-90a2-4735-a3a4-dfc0b68d3feb/content | 2026-10-18T08:42:51Z | eda0e49bd09bec9cc13b18e2991b37535e74de5e42a0a1ee1a057982d3fc036c | pages/RD5/barbon_buraschi_2020_gamma_fragility.pdf | ok | curl |
| https://squeezemetrics.com/monitor/download/pdf/white_paper.pdf | 2026-10-18T08:43:40Z | 23eaf3fa1bbb765dc9b4a9077d64a784d930662bbf329a9872d4da7c9a60a8c1 | pages/RD5/sqzm_gex_white_paper.pdf | ok (DO_NOT_COMMIT) | curl |
| https://www3.nd.edu/~zda/EOD.pdf | 2026-10-18T08:45:27Z | faa9de99da6579a94e499b4ee5bac061861ed7b3c02edcc932dd00e87c60460d | pages/RD5/baltussen_da_soebhag_eod.pdf | ok | curl |
| https://www3.nd.edu/robots.txt | 2026-10-18T08:45:34Z | 9448f8a1159c9b14e3e1b9d8eab1a6ddf88d26e1f888a34cef430c756e4e6e1e | pages/RD5/nd_robots.txt | ok (404, no directives) | curl |
| https://api.semanticscholar.org/graph/v1/paper/batch (14 DOIs, keyless) | 2026-10-18T08:46:40Z | n/a | scratchpad/RD5/s2a.json | ok (titles only, abstracts empty) | curl |
| https://econ.au.dk/robots.txt | 2026-10-18T08:47:04Z | ba17b40252229022d43a063b14e724dd15ace8411fb8298068cfd0c075d7f089 | pages/RD5/econ.au.dk_robots.txt | ok | curl |
| https://econ.au.dk/research/finance/seminars/vis/artikel/finance-internal-seminar-phd-seminar-sebastian-egebjerg-au-and-tobias-skipper-soussi-au | 2026-10-18T08:47:12Z | 5f04c64b397aee41ffb44fc639e77385f57f63828d06d6b6955db5d41cd3157a | pages/RD5/au_egebjerg_seminar.html | ok | curl |
| https://www.merlin.uzh.ch/publication/show/21160 | 2026-10-18T08:47:31Z | 87771701397a031a2247aa6251330366a38462143961133e5347e3a514625c60 | pages/RD5/uzh_ekblom_thesis.html | moved (page says publications moved to ZORA; no content) | curl |
| https://optionmetrics.com/robots.txt | 2026-10-18T08:47:34Z | 4a75222a2cb5dba18a24ae1aa58658b4b80cded1ae72ea127d796d15d660987f | pages/RD5/optionmetrics_robots.txt | ok | curl |
| https://optionmetrics.com/research/dealer-gamma-exposure-and-overnight-gap-risk-incremental-information-in-low-volatility-regimes/ | 2026-10-18T08:47:40Z | 98f6617703c06e096fb4e3c8812b0a716794ffdb51cfdbeed03c693e37e34775 | pages/RD5/om_maurer_2026.html | blocked (Cloudflare); then WebFetch summary only (not saved, no verbatim) | curl, WebFetch |

Terms: appended to terms/terms_log.md for alexandria.unisg.ch, www3.nd.edu, econ.au.dk, optionmetrics.com, squeezemetrics.com
(citing R2's line and E.20's clearance). WebSearch calls used: 10 of 45.
Budget notices: 2026-10-18T08:43:21Z Firecrawl firecrawl_search HTTP 402 "out of credits" (3 calls; no Firecrawl paper
tools used after that); 2026-10-18T08:46:21Z OpenAlex keyless daily IP budget exhausted ("Rate limit exceeded"; shared by
all readers on this IP; resets at midnight UTC).

## 10. Unfinished and unverified items

- Ni, Pearson, Poteshman and White (RFS 2021): published full text not retrieved (Oxford paywall; SSRN blocked); only a
  2006 draft exists on ou.edu (not fetched). No number from it is used. It is a daily, single-stock volatility paper.
- Anderegg et al. (2022): full text (ETH repository hdl 20.500.11850/536212) not fetched; abstract via OpenAlex only.
- Egebjerg and Kokholm (SSRN 4936978), Hu-Kirilova-Muravyev "Options Market Makers" (SSRN 4633451), Chilingarian "The
  Sign of Dealer Gamma" (SSRN 7131778, 2026), Gayda et al. "Option Liquidity and Gamma Imbalances" (SSRN 4138512), Maurer
  (SSRN 6650858): SSRN-only, not retrieved; Chilingarian's and Hu et al.'s papers bear directly on the sign question and
  are worth a follow-up if the lead finds a non-SSRN copy.
- Forward citations of Gamma Fragility and Anderegg were listed (4 and 13 works); abstracts for the second batch of
  Baltussen forward cites could not be read after the OpenAlex budget ran out.
- Rosa (JFM 2022) threshold form: still [unverified] (Wiley), as in E.20.
- The period-concentration arithmetic in section 4 is derived from counts on record; the lead or a verifier should check it.
