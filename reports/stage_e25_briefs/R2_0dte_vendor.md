# R2: 0DTE second reader (exchange, vendor, practitioner) - Stage E.25

Reader: R2-0DTEVendor-OpusHigh. Wave 1 ran 01:38-01:58 PDT (cut by the usage limit); resumed 06:21 PDT,
finished 06:32 PDT 2026-10-18. Academic side: R1 (R1_0dte_academic.md) and RD5 (RD5_redig_gamma.md),
cited, not repeated.

## 1. Answer (at most 250 words)

No exchange, vendor or bank source read gives a sized, per-trade, intraday ES/NQ effect that is
prop-compatible and testable on owned data. Cboe's own studies say 0DTE market-maker hedging is small. Net
gamma averages "$170mm to $670mm", or 0.04-0.17% of daily S&P futures liquidity (2023). In the April 2025
turmoil it was "at best, just 0.2%" of futures notional. Cboe also found "no uptick in intraday gap moves",
including the last hour. Bank views come only through press reposts (JPM, BofA, Nomura, 2023). They describe
more intraday reversal in the 0DTE era, without numbers. JPM's $30.5bn figure is a scenario, not a measurement.

Vendor evidence is marketing-grade:
- SpotGamma's own gamma-sign backtest underperforms buy-and-hold and gets "chewed up" by sign flips.
- Its "report card" lists hand-picked calls.
- Its key-level statistics (2019-05-10 to 2024-05-28) give 1-day forward returns after level breaches
  (+14 bp after a Put Wall breach). They have no n and no dispersion, and the hold runs overnight.
- SqueezeMetrics says DIX has "lost a great deal of predictive power" since 2022.
- MenthorQ, HIRO and FlashAlpha publish no aggregate backtests; the only figures found are anecdotes.

Data prices (published):
- Cboe Intraday Open-Close (the only signed-by-capacity source): 10-minute history $1,000 per month of data
  (about $15,000 for the research window); 1-minute history $4,000 per month (about $60,000).
- Unsigned feeds: Databento OPRA $199/month (12 months L1); ORATS 1-minute $199/month plus $1,500 for
  history from August 2020.
- Vendor dashboards: $99 to $720 a month.

Two weak candidates (R2-C1 and R2-C2), both low confidence. R2-C2 is a cross-reference to the shortlisted C1:
the Beat-the-Market paper's 5-day-RSI "gamma proxy" regression, which can be computed from owned bars.

## 2. Candidate hypotheses

| id | hypothesis | instruments | window / hold | published effect | price used | gross pts | MES ticks | gross/net | dispersion | data | owned | testable | overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R2-C1 | After SPX breaks below SpotGamma's daily Put Wall, go long; published 1-day forward return +14 bp (Call Wall breach: -7 bp) | MES (ES) | as published: 1-day forward return (close-to-close by implication; definition not stated); an intraday variant (breach to 15:00 CT) is NOT published | "Following a Put Wall breach, forward returns are noticeably positive: average 1-day return of 14bps" | SPX/ES 6,600 (2025-26); sample 2019-05-10..2024-05-28 averaged about 3,000-5,300 | 14 x 6,600 / 10,000 = 9.24 pt (at 4,000: 5.6 pt) | 9.24 / 0.25 = 37.0 (at 4,000: 22.4) | unknown (vendor; no costs) | none published (no n, no sd, no t) | SpotGamma daily Put/Call Wall history | no | no (no history for sale found; SpotGamma Alpha $299/mo shows current levels) | E-H3/expiry family only loosely; reversal family (K1-vxnband-01, C-H1); multi-day trigger closure (V39-V41, E.23) if held overnight |
| R2-C2 | Conditioning overlay on shortlist C1 (noise-area momentum): skip or downsize on days when the 5-day RSI of the index is high (vendor-style "gamma proxy": high RSI = dealers likely long gamma = more intraday mean reversion) | MNQ/MES (paper: SPY) | C1's own windows; filter set at previous close | "we obtain a value of beta of -3.25 with a p-value of 0.001" (daily momentum-portfolio return in bp per RSI point) | n/a (regression slope, not a trade) | not convertible to a per-trade gross | n/a | gross (cost section 4.6 separate) | p = 0.001; in-sample 2007-2024; no OOS for this regression | 1-min bars (RSI from daily closes) | yes | yes (research window) | C1 (shortlist, R10-C1); C2 and E20H6-T3 (GEX-conditioned momentum, FAIL/stopped) |

Why so few: every exchange study sizes hedging flow or volatility, not direction; bank views come
second-hand and unsized; vendor statistics have no denominators or dispersion and mostly use daily or
multi-day horizons. R1-C1 (Adams et al. 2026, high-gamma hourly reversal 1-2 bp) is the academic sized
analogue; R2 adds its data price (section 5).

R2-C2 caveats for the lead: the slope is in-sample. The paper's own wording is "it is beyond the scope of this
paper to provide a precise estimate of gamma imbalance": RSI is a proxy the authors chose, not a measured
gamma. Adding it to C1 is a new trial on top of C1, and E20H6-T3 already failed with a real (SqueezeMetrics)
GEX filter on a related momentum rule. Owner of the paper: R10 (R10_practitioner.md, shortlist C1). R2 only
points at its section 4.5, which R10 did not cover (no "gamma" hit in R10_practitioner.md).

## 3. Evidence table

| # | claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|---|
| E1 | Cboe: SPX 0DTE market-maker net gamma is small vs S&P futures liquidity | $170mm to $670mm; 0.04% to 0.17% of daily S&P futures liquidity | "On average, market maker positioning is fairly de minimis, with net gamma exposure ranging from $170mm to $670mm throughout the day. To put that number in context, S&P futures trade around $400bn a day, so we're talking about potential hedging flows that make up between 0.04% to 0.17% of the daily S&P futures liquidity." | point 1 under the 30-min box plot (line 334 of saved md) | Mandy Xu, Cboe, "Volatility Insights: Much Ado About 0DTEs", 2023-09-07/08, https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options | exchange-regulator (exchange with commercial interest in 0DTE volume) | pages/R2/cboe_much_ado_0dte_2023.md (PDF copy pages/R2/sg_cboeqqq.pdf) |
| E2 | Cboe: net gamma at 3:30 pm and tails | median +$173mm; IQR -$1.1bn to +$2.4bn; whiskers -$5bn to +$7.7bn = 1.3%-1.9% of futures notional | "The median net gamma at 3:30pm is just +$173mm with the typical range from -$1.1bn to +$2.4bn (25th to 75th percentile readings). Even if we focus on the "whiskers" on the box plot, the range of -$5bn to +$7.7bn represents just 1.3% to 1.9% of the S&P futures daily notional volume." | point 2 (line 336) | same | exchange-regulator | same |
| E3 | Cboe: scope caveat (only SPX 0DTE, not other expiries, ES options or SPY) | - | "It's worth noting that this analysis is only for market maker positioning in SPX 0DTE options. Market makers may have offsetting positions in other expiries, or other equivalent products (e.g. E-mini or SPY 0DTE options)." | line 338 | same | exchange-regulator | same |
| E4 | Cboe: no rise in 1-min 2-sigma jumps, incl. last hour | no uptick | "there has been no uptick in intraday gap moves in the S&P over the past year, either during the trading day or in the last hour going into the close" | section "Assessing S&P Intraday Volatility" (line 353) | same | exchange-regulator | same |
| E5 | Cboe: close-to-close vs intraday realized vol spread unchanged | 2.7 vol pts YTD = 10-year average | "The YTD average spread of 2.7 vol pts is exactly the same as the 10-year average (Exhibit 5)." | line 351 | same | exchange-regulator | same |
| E6 | Cboe 2025: in April 2025 turmoil MM 0DTE gamma hedging at most 0.2% of S&P futures notional | +$2.1B to -$390M (Apr 4), +$300M to +$770M (Apr 9); 0.2% | "SPX futures traded over $850B on April 9th and over $940B on April 4th, so market marker gamma hedging activity in SPX 0DTE options represented, at best, just 0.2% of S&P futures notional volume." | PDF p. 7-8, Exhibits 10-11 (txt lines 395-400) | Cboe, "0DTEs Decoded: Positioning, Trends and Market Impact", 2025-05-02 (PDF via storage.pardot.com) | exchange-regulator | pages/R2/cboe_0dtes_decoded_2025.pdf (+ .txt) |
| E7 | Cboe 2025: retail share of SPX 0DTE | 50-60%; 57% -> 47% in early April 2025 | "We estimate that retail now makes up around 50-60% of SPX 0DTE trading." | landing page bullet 1 (line 278) | Cboe insights post 2025-05-02, https://www.cboe.com/insights/posts/0-dt-es-decoded-positioning-trends-and-market-impact | exchange-regulator | pages/R2/cboe_0dtes_decoded_2025.md |
| E8 | SpotGamma: gamma-sign SPX timing underperforms buy-and-hold; whipsaw; bull-market-only sample | no numbers | "You will underpeform the SPX if you only use "market gamma" as your buy/sell indicator." / "We know from our own testing that you can get "chewed up" at times where the indicator flips back and forth between positive and negative." / "All gamma data we've seen has been collected during a very large bull market." | post body, bullets | SpotGamma, "SPX Long Gamma Backtest", 2019-12-10, https://spotgamma.com/spx-long-gamma-backtest/ | vendor | pages/R2/sg_spx_long_gamma_backtest.md |
| E9 | SpotGamma "Quarterly Report Card" is a list of selected dated calls, no hit rate | none | e.g. "6/5 - Crowded Tech Positioning Breaks - SPX Falls More Than 4% From Its Highs" (no denominator, no misses listed) | page headings | SpotGamma, https://spotgamma.com/spotgamma-quarterly-report-card/ (fetched 2026-10-18) | vendor (marketing; selection bias) | pages/R2/sg_report_card.md |
| E10 | Cboe 2025: 0DTE share and size | over 50% of SPX volume; over $1T notional daily; ADV 388k (Q1 2022) -> 1.98M (Q1 2025) | "0DTE options now make up over 50% of the total SPX volume, with over $1T notional trading daily (Exhibit 2)." | PDF p. 1 (txt line 12) | Cboe, 0DTEs Decoded, 2025-05-02 | exchange-regulator | pages/R2/cboe_0dtes_decoded_2025.txt |
| E11 | Cboe 2025: 0DTE share falls in turmoil | 64% (Apr 1) -> 36% (Apr 7) | "0DTE share of overall SPX option volume fell from a high of 64% on April 1st to a low of 36% on April 7th" | txt line 228 | same | exchange-regulator | same |
| E12 | Cboe 2025: risk format of 0DTE trades | over 95% capped risk; naked short 4% | "with over 95% of all 0DTE trades done in capped risk formats (i.e. either long options outright or short options through spreads). Naked short options, with the potential for massive losses, make up just 4% of SPX" | txt lines 332-333 | same | exchange-regulator | same |
| E13 | Cboe Sep 2026: 0DTE volume at record in the research window's tail | SPX 0DTE record quarterly ADV 3.2M; monthly 3.4M | "SPX zero-days-to-expiry (0DTE) options reached a record quarterly ADV of 3.2 million contracts and record monthly ADV of 3.4 million contracts." | bullet (line 275) | Cboe, "Market Metrics That Matter: Derivatives September 2026 Volume Highlights", 2026-10-12, https://www.cboe.com/insights/posts/market-metrics-that-matter-derivatives-september-2026-volume-highlights | exchange-regulator | pages/R2/cboe_metrics_sep2026.md |
| E14 | Cboe 2026: RUT 0DTE share doubled; retail 60-65% | 13% -> 25% | "The share of 0DTE options in RUT has almost doubled, from 13% to 25% (see Exhibit 2)." | PDF txt line 52 | Cboe, "Small Caps, Big Momentum: The Rise of 0DTE Trading in Russell 2000 Index & ETF Options", 2026-03-13 | exchange-regulator | pages/R2/cboe_rut_0dte_2026.pdf (+ .txt) |
| E15 | JPM, BofA, Nomura (via ZeroHedge repost on SpotGamma): 0DTE era shows more intraday reversal; morning/afternoon same-direction share "plummeted" | none (charts only) | "So, instead of Kolanovic's 'Volmageddon', JPMorgan's quants have observed more intraday reversal behavior (which matches SpotGamma and BofA's findings)." / "the share of sessions during which US equities move in the same direction in morning and afternoon trading has plummeted." | lines 94-96; dated 2023-05-16 (image stamp line 104) | ZeroHedge (Tyler Durden) reposted by SpotGamma, https://spotgamma.com/volmageddon-no-jpm-bofa-say-0-dte-options-are-suppressing-intraday-vol/ | pointer [secondary-only] (bank notes not read; press repost on a vendor site) | pages/R2/sg_volmageddon_jpm_bofa.md |
| E16 | BofA (via press): 0DTE share and trade-side pattern | 40-45% of SPX volume (early 2023); 75% of single-leg auto-ex trades near bid/ask; ask-skew early, bid-skew late | "half of all SPX 0DTE option trades are "single-leg auto-execution", a category for which (i) 75% of trades occur near the bid or the ask – more than for any other tenor, and (ii) volume is uniquely skewed towards the ask early in the day but towards the bid later in the day" | line 63 | ZeroHedge repost on SpotGamma, https://spotgamma.com/no-0dte-will-not-result-in-volmageddon-bofa-derivative-gurus-respond-to-kolanovic/ (2023-02) | pointer [secondary-only] | pages/R2/sg_bofa_respond_kolanovic.md |
| E17 | JPM (via press): 0DTE unwind scenario, not a measurement | 5% drop in 5 min -> $30.5bn flow -> +20 pp further decline | "The analysts expect such a scenario if the S&P 500 declined 5% in five minutes, triggering $30.5 billion in 0DTE option-related trading that would in turn add another 20 percentage points to the index's decline." | line 74 | Benzinga, 2023-03, https://www.benzinga.com/analyst-ratings/analyst-color/23/03/31230564/jpmorgan-analysts-believe-these-options-could-turn-a-5-market-fall-into-a-deadly-di | pointer [secondary-only] | pages/R2/benzinga_jpm_0dte_2023.md |
| E18 | Nomura (via SpotGamma): 0DTE volume mostly MM risk positioning that "nets out" | none | "flow can exacerbate intraday moves, BUT much of the volume likely electronic market makers trading for risk positioning, creating noise that can 'net out'." | line 36 (2023-01-24) | SpotGamma, "Nomura on 0DTE Options Volumes", https://spotgamma.com/nomura-on-0dte-options-volumes/ | pointer [secondary-only] | pages/R2/sg_nomura_0dte.md |
| E19 | SpotGamma key-level statistics (R2-C1 source) | Put Wall breach: +14 bp 1-day, +7 bp 5-day, +39 bp 10-day; Call Wall breach: -7 bp 1-day | "Following a Put Wall breach, forward returns are noticeably positive: average 1-day return of 14bps, average 5-day return of 7bps, and average 10-day return of 39bps." / "Following a Call Wall breach, average forward returns are diminutive: -7bps for 1 day forward return, and 5bps for 5 day forward returns." / sample: "based on data from 10 May 2019 - 28 May 2024" | lines 41, 54, 65 | SpotGamma Support, "SpotGamma SPX Key Levels Statistics", https://support.spotgamma.com/hc/en-us/articles/31209900542867 | vendor (no n, no dispersion, no costs, in-sample; vendor defines its own levels) | pages/R2/sg_support_key_levels.md |
| E20 | SpotGamma: Vol Trigger separates volatility, not direction | 5-day RV 13% above vs 18% below; 1-day sd 0.9% vs 1.3% | "SPX Opens Above Volatility Trigger™ | 13%" / "SPX closes above Vol Trigger | 0.9% | 2.0%" ; "SPX closes below Vol Trigger | 1.3% | 2.7%" | table rows lines 79-88 | same | vendor | same |
| E21 | SqueezeMetrics GEX white paper: GEX predicts variance, not direction | top vs second GEX quartile 1-day sd 0.55% vs 0.85% | "When instead we compare the highest and second-highest** quartiles of GEX to subsequent SPX variance, the 1-day standard deviations are 0.55% and 0.85%, respectively." | p. 2 (txt lines 66-70); paper dated March 2016, revised December 2017 | SqueezeMetrics, "Gamma Exposure (GEX)" white paper, https://squeezemetrics.com/monitor/download/pdf/white_paper.pdf | vendor | pages/R2/sqm_gex_white_paper.pdf (+ .txt; DO_NOT_COMMIT) |
| E22 | SqueezeMetrics: DIX signal decayed since 2022 (decay evidence for a vendor signal) | - | "Ever since 2022, the S&P 500 Dark Index (DIX) has clearly lost a great deal of predictive power. It's become messy. Its signal is degraded." | line 15 | SqueezeMetrics note, 2023-12-17, https://mailer.squeezemetrics.com/w/SIIFYZqc14gv41SmeSjRYw?_2023-12-17 | vendor | pages/R2/sqm_note_2023-12-17_dix_power.md |
| E23 | Beat the Market: RSI as dealer-gamma proxy predicts momentum-strategy returns (R2-C2 source) | beta -3.25 bp per RSI point, p 0.001 | "we obtain a value of beta of -3.25 with a p-value of 0.001. The results indicate that the slope coefficient of the regression is negative and significantly different from zero." / "Although it is beyond the scope of this paper to provide a precise estimate of gamma imbalance, we hypothesize that utilizing a short-term Relative Strength Index (RSI) might allow us to gauge whether the market is near the bulk of call strikes or put strikes." | section 4.5, p. 23 (txt lines 866-878) | Zarattini, Aziz, Barbon, "Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)", WP, version 2025-02-03 (owned by R10; E.20 shared copy) | working-paper | reports/stage_e20_briefs/shared/zarattini_aziz_barbon_beat_the_market.pdf.txt (sha256 5bed406569325f0a...) |
| E24 | FlashAlpha: futures GEX backtests must use cash-index proxy; no backtest result published | - | "research the signal on `historical.flashalpha.com` using **SPY** (for ES) and **QQQ** (for NQ) since January 2017" / "Minute-resolution replay for cash-index and equity symbols goes back to 2017-01-03" | lines 349, 479 | FlashAlpha, "Backtesting Futures Gamma (ES & NQ): Historical GEX Done Right", 2026-06, https://flashalpha.com/articles/backtesting-futures-gamma-es-nq-historical-gex | vendor | pages/R2/fa_backtesting_futures_gamma.md |
| E25 | SpotGamma 2026 0DTE guide: "pin"/"pop" afternoon regimes asserted, not tested | 0DTE about 63% of SPX volume Feb 2026 | "In February 2026, Cboe reported that **0DTE contracts approached 63% of total SPX volume**" ; "If the market has been range-bound all day and GEX is positive, the afternoon will likely see prices tighten further around the highest-gamma strike." | lines 64, 216 | SpotGamma, "0DTE Options Explained", published 2026-06-10, https://spotgamma.com/0dte-options-explained/ | vendor (marketing) | pages/R2/sg_0dte_explained_2026.md |

## 4. Negative evidence

- Exchange (E1-E6): Cboe finds 0DTE market-maker hedging de minimis against S&P futures volume (0.04-0.17%
  on average, at most 0.2% on the April 2025 stress days, 1.3-1.9% at the 2023 whiskers). It finds no rise in
  intraday 1-minute jumps "either during the trading day or in the last hour going into the close". The
  intraday vs close-to-close vol spread "is exactly the same as the 10-year average". The bias runs the other
  way: Cboe sells these products and has an interest in finding no harm. Scope caveat E3: the study covers
  SPX 0DTE only.
- Vendor's own test (E8): SpotGamma states that timing SPX with the gamma sign underperforms buy-and-hold and
  whipsaws, and that its sample was a bull market.
- Vendor signal decay (E22): SqueezeMetrics says DIX "has clearly lost a great deal of predictive power" since
  2022, the start of the daily-expiry era.
- Variance, not direction (E20, E21): both vendors' quantified claims are about volatility (sd 0.55% vs 0.85%;
  RV 13% vs 18%), not signed returns.
- No aggregate vendor backtests: none were found for MenthorQ levels, SpotGamma HIRO or FlashAlpha. Searches
  at 13:21-13:28Z returned only single-trade anecdotes, for example a MenthorQ partner blog's "75 percent win
  rate" from one person's journal. These are search-summary leads only, not retrieved text, so they are not
  evidence and are listed in section 10.
- Bank notes (E15-E18) are unsized press reposts, and the JPM $30.5bn figure is a scenario (E17). JPM's
  "intraday reversal" observation from 2023 is not quantified in anything read.
- Academic cross-check (R1, RD5): Dim-Eraker-Vilkov find a null for gamma propagation. Adams et al. 2026 say
  their effect "does not translate into a feasible trading strategy". RD5 says the Baltussen gamma rule's
  post-2011 base is thin. The vendor side adds nothing that overturns these.

## 5. Data and cost

| data | needed by | owned | published price (quoted) | URL, date read | terms |
|---|---|---|---|---|---|
| Cboe Intraday Open-Close, 10-minute (signed volume by capacity: customer, pro-customer, broker-dealer, firm, MM; SPX trades only on C1, so C1 covers SPX in full) | R1-C1 (Adams et al. use it), RD5-C1 | no | Fees Schedule effective 2026-10-01: Ten-Minute Intraday subscription "$3,000 per month" / "$36,000 per year"; historical ad-hoc "$1,000 per month" [pdftotext layout; that the $1,000 sits in the historical column is inferred from position]. Research window 2025-04..2026-06 = 15 months -> about $15,000. History: "C1 / 10-min interval / 2011-01-03" | https://cdn.cboe.com/resources/membership/Cboe_FeeSchedule.pdf (fetched 13:23Z); product page https://datashop.cboe.com/cboe-options-open-close-volume-summary | academic discount "$3,000 per year for the first year and $250 per month for each additional month"; free sample "Ten-Minute Intraday Open-Close Historical Data for the period July 1, 2022 through December 31, 2022" for first-time non-TPHs (would need a request: not done) |
| Cboe Intraday Open-Close, 1-minute | finer timing of R1-C1 | no | One-Minute subscription "$12,000 per month" / "$144,000 per year"; historical "$4,000 per month" (last four years) and "$2,500 per month" (five or more years) [layout inferred]. Research window about $60,000. History: "C1 / 1-min interval / 2019-10-07" | same | academic "$12,000 per year for the first year and $1,000 per month" |
| Cboe Open-Close EOD | daily signed positions | no | "$600.00*" (one to four years, per month) / "$300.00*" (five or more years) / monthly "$600.00" | same | academic $1,500/yr |
| (history) 2022 Open-Close fees | price trend | - | SR-CBOE-2022-023: Intraday subscription "$2,000 per month"; historical "$1,000 per month" / "$24,000 per year" | pages/R2/cboe_SR-CBOE-2022-023.pdf, p. 35 | the subscription price rose from $2,000 to $3,000 a month between 2022 and 2026 |
| Cboe LiveVol Pro / Core (platform) | discretionary view | no | "LiveVol Pro is available as a web-based platform for $380 per month"; "LiveVol Core platform prices ... will be updated to $105.00 per month or $1,050.00 per year" | https://datashop.cboe.com/livevol-pro | market-data fees extra (CGI feed $14.95/mo; "CME Data Package fee will increase from $119.80 per month to $130.10 per month") |
| Cboe DataShop Option Trades / Quote Intervals | unsigned trades or NBBO | no | price computed in cart (not on the static page); SPX underlying bid/ask needs a CGI license, "fees start at $1k/month" | https://datashop.cboe.com/option-trades | - |
| OPRA via Databento (OPRA.PILLAR: trades, CBBO, TCBBO, CMBP-1, OHLCV) | GEX from OI plus trade-signing assumptions | no | Standard "$199 per month" (L1 trades/CBBO "Last 12 months", OHLCV/definitions/statistics 13+ years); Plus "$1,500 license fees per month" (3 years L1, annual contract); Unlimited "$4,000 license fees per month" (13+ years); usage-based historical "Pay as you go" (per-GB rate shown only in the portal estimator). Dataset "Since 2013-04-01 UTC" | https://databento.com/catalog/opra/OPRA.PILLAR#pricing (fetched 08:50Z) | "A license isn't required to access historical data."; personal use "Up to 2 devices"; no spend in this stage |
| ORATS 1-minute intraday (Greeks/IV from NBBO) | unsigned GEX by minute | no | "For an individual license, recurring delivery is $199 per month and the historical backfill from August 2020 is $1,500 as a one-time purchase"; "S3 storage and transfer fees range from $1-2k" | https://orats.com/one-minute-data | professional licenses priced separately |
| ORATS near-EOD (14 min before close) | daily GEX | no | "recurring delivery is $99 per month and the historical backfill from 2007 is $599" | https://orats.com/near-eod-data | - |
| ThetaData | tick options | no | $40 (Value) / $80 (Standard) / $160 (Pro) per month [secondary-only: from FlashAlpha's June 2026 comparison table, "ThetaData ... $40/mo (Value) ... $160/mo (Pro)"; thetadata.net terms forbid automated access, so its page is not cited] | pages/R2/fa_pricing_comparison.md line 371 | vendor comparison by a competitor |
| Massive (Polygon) options | chains, ticks | no | "$29/mo (Starter, 15-min delayed)" to "$199/mo (Advanced, real-time)" [secondary-only, same FlashAlpha table; massive.com terms forbid scraping] | pages/R2/fa_pricing_comparison.md line 372 | same |
| SpotGamma levels (Call/Put Wall, Vol Trigger, HIRO) | R2-C1 | no | Essential "$99/mo", Alpha "$299/mo" (promo annual "First year $534" / "First year $1,494"); institutional "from $1,999/mo" [secondary-only, FlashAlpha table] | https://spotgamma.com/pricing/ | no level history for sale found; personal-use terms |
| MenthorQ (gamma levels on futures) | none sized | no | Premium "$129 / next months" (first month $39); Pro "$349 / next months" | https://menthorq.com/pricing/ | terms bar copying and bulk download |
| SqueezeMetrics (GEX, DIX) | C2, E20H6-T3 (done) | daily CSV yes (E.14 copy) | "$720 / month"; "Market-structure measurements with history since 2011" | https://squeezemetrics.com/monitor/plans | E.20 clearance |
| FlashAlpha (computed GEX API, minute replay from 2017 on SPY/QQQ) | unsigned GEX backtest | no | Alpha "$1,199/mo annual ($1,499/mo monthly)" with "the Historical API (point-in-time replay since January 2017)" | https://flashalpha.com/articles/options-data-pricing-comparison-flashalpha-thetadata-polygon-spotgamma-squeezemetrics (2026-06-07) | vendor's own pricing |

Point for the lead: only Cboe Open-Close sells trades signed by participant type ("This dataset categorizes
every trade by participant type (customer, professional customer, broker-dealer, market ..."). OPRA, ORATS,
ThetaData, Massive and FlashAlpha give open interest, quotes or trades with no participant, so any GEX built
from them rests on a sign convention. Adams et al. (R1) find the convention is wrong in sign often enough to
matter: market makers' net gamma is positive in 88% of intervals.

## 6. Prop compatibility

- R2-C1: as published, the 1-day forward return is held overnight, which breaks Topstep's flat-by-15:10 CT
  rule. An intraday variant (enter on the breach, exit by 15:00 CT) is unpublished and unsized. A position held
  1-5 days falls under the closed direction "the program's own intraday triggers at multi-day holds"
  (V39-V41, E.23). DLL: one MES, no issue. P06: not news-specific. HFT: no. Automation: needs a live vendor
  level each day, read from a dashboard by hand (V39 allows manual), and SpotGamma's terms are personal use.
- R2-C2: inherits C1's profile (intraday, flat by 15:00 CT, automatable from owned bars). The filter is set at
  the previous close, so there is no extra execution constraint.
- Options-data candidates (R1-C1): the futures leg is Topstep-compatible. The signal needs 10-minute Open-Close
  data in near real time (subscription $3,000/month); delivery is "Minutes after each interval closes", fine
  for a 1-2 h hold.

## 7. Overlap with tested mechanisms

| candidate | overlap ids | how it differs |
|---|---|---|
| R2-C1 | E-H3 (expiry), C-H1/K1-vxnband-01 (reversal family), E23 multi-day closure | conditioned on a vendor's options-derived level, not on price alone; daily horizon |
| R2-C2 | C1 (shortlist; R10-C1), C2 (stopped), E20H6-T3 (FAIL) | uses RSI from owned bars as the gamma proxy, not SqueezeMetrics GEX; applies to C1's noise-area rule, not the last-half-hour rule |
| bank "more intraday reversal" (E15, unsized) | K1-cp1-01, E20H6-T1/T2, E16-H1 | a reversal sign is the opposite trade of the cp1 momentum members. E20H6-T1's gross was +1.25 ticks (momentum), so the opposite trade loses before costs |

## 8. Re-dig (not a re-dig reader)

Not applicable to R2 (first-wave reader). Verdict checks that R2's sources bear on are listed in the JSON
`verdict_checks`: E20H6-T3 and C2 (supported, E1/E6/E8), K1-cp1-01/E20H6-T1 (consistent, E15, pointer
grade).

## 9. Fetch log

Full log, one line per request: url | UTC | sha256 (first 16 hex) | path | status | tool | bytes. Mirrored in
the JSON `fetch_log`; scratch copy at
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/37fc9660-82d1-49fd-be83-50b822ab0a5b/scratchpad/R2/fetchlog.txt.
Summary: 85 log lines: 76 in wave 1 (08:39-08:58Z), 9 in the resume (13:23-13:28Z).

Terms read (terms/terms_log.md, R2 lines): www.cboe.com, spotgamma.com, squeezemetrics.com, menthorq.com,
orats.com, flashalpha.com (allowed one page at a time); thetadata.net, massive.com, tier1alpha.com (forbidden:
copies deleted, search results only); vol.land (no terms found, not fetched); datashop.cboe.com,
cdn.cboe.com/storage.pardot.com and the support/notes/mailer subdomains (cited to their parents, added
13:2xZ); www.numerix.com (terms page 404, not fetched); www.benzinga.com (R5's line). databento.com: line 11.

Deviations (wave 1, logged at the time): thetadata.net /pricing and /subscribe, massive.com /pricing (twice)
and tier1alpha.com home were fetched before their terms were read. The terms forbid automation, all copies
were deleted, and none is cited.

Budget notices: Firecrawl "Insufficient credits to perform this request" at 2026-10-18T08:48:44Z (fell back to
scrapling). WebSearch: 9 calls in the resume (cap 25), no over-budget notice. OpenAlex, Firecrawl and
Semantic Scholar not called in the resume.

Blocked: Benzinga returned 403 to scrapling get at 13:27:01Z and succeeded with scrapling fetch.

## 10. Unfinished and unverified

- The Open-Close fee table was read from pdftotext layout output. Which column the "$1,000 per month" belongs
  to (historical ad hoc, Ten-Minute) and the 1-minute split ($4,000 for the last four years, $2,500 for five
  or more years) are inferred from text position; check against the PDF page ("Livevol Fees", p. 12-13).
- ThetaData, Massive and SpotGamma institutional prices are secondary-only (a competitor's June 2026 table).
- Not read (paywall or no terms): the original JPM, BofA, Nomura and Goldman notes; Risk.net "Bank QIS teams
  take zero-day options plunge" (JPM 0DTE intraday momentum strategy, search result only); the Numerix white
  papers "0DTE Trading Strategies" and "Gamma Hedging of 0DTE Options" (2026-01; terms page not found); and
  Tier1Alpha research (terms forbid automation).
- MenthorQ's "75 percent win rate" (via a Tickblaze blog) and SpotGamma HIRO "+406%" trade examples are search
  summaries only [unverified], anecdotes in any case.
- SpotGamma level history: no purchasable history found; not checked with SpotGamma (no contact allowed).
- Databento's OPRA per-GB rate is not printed on the page (estimator only).
- r0_mechanism_index.md was grepped for overlap ids. Ranking and ratios are for the lead.
