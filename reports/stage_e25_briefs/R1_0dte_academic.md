# R1: 0DTE and dealer gamma, academic work 2022-2026 (SourceReader-0DTEAcademic-OpusHigh, rerun)

Status: DONE under a hard deadline (rerun started 06:13 PDT, first write 06:15 PDT 2026-10-18). The first
R1 run was cut by a usage limit about 01:58 PDT; its pages under pages/R1/ were reused. Two of the five
priority papers (Dim-Eraker-Vilkov; Brogaard-Han-Won) and Beckmeyer-Branger-Gayda were NOT read in full
text (see section 10).

## 1. Answer (at most 250 words)

The strongest sized evidence read is Adams, Dim, Eraker, Fontaine, Ornthanalai and Vilkov (draft 15 Jul
2026, S&P 500 / E-mini, 2018-2024, signed Cboe Open-Close positions). Market makers' net gamma is
positive most of the time and dampens: one sd more 0DTE net gamma lowers next-10-minute realized vol by
about 23 annualized bp; expiry days have 7% lower 10-minute RV. For
returns, momentum from one hour to the next is about +0.7 bp at 1-2 h in the lowest gamma quartile and
about -1 to -2 bp (reversal) in the highest; Q1-Q4 spread -1 to -3 bp at 30 min to 2 h. At ES 6,000
that is 0.42 pt (1.7 MES ticks) for Q1 momentum and 0.6-1.2 pt (2.4-4.8 MES ticks) for the Q4
reversal, around the about 3.0-tick MES hurdle; the authors state it "does not translate into a feasible
trading strategy" because net gamma is not observable. Amaya, Garcia-Ares, Pearson and Vasquez (Jan
2025, Cboe proprietary trades) bound the gamma effect on volatility at +3.3 pp (daily) and +6.4 pp
(30-minute) at most (sd 0.9 pp vs 4.6 pp from all causes).
Dim, Eraker and Vilkov (2024 WFA version) find open-interest 0DTE gamma does not propagate volatility and volume shocks do not amplify returns (a null). Vilkov's 0DTE trading-rules replication package (Aug 2026 correction) states no 0DTE
option strategy keeps a positive net Sharpe. One candidate (R1-C1, high-gamma hourly ES reversal),
low confidence: unowned data, unobservable in real time per the authors; overlaps C2, E20H6-T3.

## 2. Candidate hypotheses

| id | hypothesis | instruments | window / hold | published effect | price used | gross pts | MES ticks | gross/net | dispersion | data | owned | testable | overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1-C1 | When market makers' net gamma (signed 0DTE + non-0DTE) is in its top quartile, fade the previous hour's ES return over the next 1-2 h | MES (ES); MNQ transfer unverified | any 10-min mark 08:30-15:00 CT (paper: RTH), hold 1-2 h | Q4 "negative momentum returns ... of around 1-2 bps"; Q1-Q4 spread -1 to -3 bp (30 min-2 h) | ES 6,000 (2025-26 level; sample 2018-2024 averaged lower, about 3,500-5,000, which makes the point value smaller) | 1 bp = 0.60 pt; 2 bp = 1.20 pt | 1 bp: 0.60/0.25 = 2.4 ticks; 2 bp: 4.8 ticks (hurdle about 3.0) | gross, before costs | "statistically significant at the 1- and 2-hour horizons" (Q4); no per-trade sd quoted | Cboe Open-Close Volume intraday 10-min, SPX/SPXW, by participant type | no | no (data not owned; authors say not observable in real time) | E13/E14-C2, E20H6-T3 |

Conversion: points = bp x price / 10,000 = 1 x 6,000 / 10,000 = 0.60 ES pt; ticks = 0.60 / 0.25 = 2.4 MES
ticks. Note the paper's "momentum return" is a first difference of buy-and-hold returns
(R_{t,t+n} - R_{t-n-1,t-1}), not the P&L of a position signed by the past return; the per-trade gross of an
actual fade rule is therefore not directly published (the lead should treat 1-2 bp as an upper-order
indication, not a per-trade figure).

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| Low-gamma momentum size | about 0.7 bp at 1-2 h | "for the low net gamma quartile, the average return estimates are positive across all investment horizons, and they increase monotonically from almost zero in the next 10-minute interval to around 0.7 bps at the 1- and 2-hour horizons." | section 4.4, pp. 32-33 (txt lines 1133-1137) | Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov, "Do S&P 500 Options Increase Market Volatility? Evidence from 0DTEs", draft 15 Jul 2026 | working-paper | reports/stage_e20_briefs/shared/adams_etal_0dte_fontaine.pdf.txt (E.20 copy, not refetched; sha256 074f8ca85a868bda...) |
| High-gamma reversal size | about 1-2 bp; Q1-Q4 -1 to -3 bp | "negative momentum returns (or positive reversal returns) of around 1 - 2 bps across the investment horizons for the higher level of net gamma. The difference between the first and fourth quartile ranges between -1 and -3 bps across investment horizons between 30 minutes and 2 hours, and it is statistically significant." | section 4.4, p. 33 (txt 1141-1144) | same | working-paper | same |
| Not tradable per authors | - | "this result does not translate into a feasible trading strategy since the market makers' net gamma is not observable to other investors." | section 4.4, p. 33 (txt 1151-1152) | same | working-paper | same |
| Gamma lowers next-interval vol | 23 annualized bp per sd | "Shifting 0DTE net gamma in a 10-minute interval by one standard deviation reduces predicted S&P 500 realized volatility by about 23 basis points (annualized) in the next 10-minute interval. The effect on volatility persists for the next hour" | Introduction (txt 122-125) | same | working-paper | same |
| 0DTE expiry days calmer | -61 annualized bp, about 7% | "on days when 0DTE contracts expire, the 10-minute realized volatility of S&P 500 index returns is lower by 61 annualized basis points (bps) on average—which is about 7% of the average realized volatility in our sample." | Introduction (txt 66-69) | same | working-paper | same |
| Order-flow reversal decays within the hour | about 30 min | "This predictability remains statistically significant for about 30 minutes and decays toward zero within the hour" | Introduction (txt 132-133) | same | working-paper | same |
| Data used | - | "Cboe Open-Close Volume: Intraday open-close volumes at 10-minute frequency" | data appendix (txt 1641) | same | working-paper | same |
| Max gamma effect on vol is bounded | +3.3 pp daily, +6.4 pp 30-min | "We find that the maximum impact of OMM gamma on annualized volatility is to increase annualized daily volatility by 3.3 percentage points. The maximum impact of OMM gamma on annualized 30-minute volatility is to increase it by 6.4 percentage points." | Introduction p. 4-5 (txt 212-216) | Amaya, Garcia-Ares, Pearson, Vasquez, "0DTE Index Options and Market Volatility: How Large is Their Impact?", 25 Jan 2025 | working-paper | reports/stage_e25_briefs/pages/R1/vasquez_amaya_pearson_garciaares_cboe.pdf.txt (sha256 385ad5fddfe706d5...) |
| Gamma-induced vol changes are small vs total | sd 0.9 pp vs 4.6 pp | "the standard deviation of the gamma-induced change in 30-minute realized volatility is 0.9 percentage points. This is smaller than the standard deviation of changes in annualized 30-minute realized volatility due to all causes, which is 4.6 percentage points." | Introduction (txt 227-230) | same | working-paper | same |
| Vol elevated only when OMM gamma negative (rare) | - | "But OMM gamma is sometimes negative, and at these times volatility is elevated." | Introduction (txt 211-212) | same | working-paper | same |
| 0DTE OI gamma does not propagate volatility; volume shocks do not amplify returns | - | "high open interest gamma in 0DTEs does not propagate past volatility. ... intraday 0DTE trading volume shocks do not amplify recent past index returns, inconsistent with the view that 0DTEs market growth intensifies market fragility." | Abstract (txt 7-15) | Dim, Eraker, Vilkov, '0DTEs: Trading, Gamma Risk and Volatility Propagation', WFA version 14 May 2024 (SSRN 4692190) | working-paper | pages/R1/dim_eraker_vilkov_wfa.pdf(.txt) (sha256 2064cff3cd3b2de2681f03eb99630ab8b5f8683d39142593d20b0f5bb8ea8d43) |
| Early vs late sample difference negligible | 0.15 sd of return vol | "the difference in the magnitude of the average volatility response to 0DTE trading across the early and later sample period amounts to only 0.15 standard deviations of the return volatility, which is economically negligible." | Introduction (txt 129-131) | same (sample 01/2012 to 14/06/2023) | working-paper | same |

## 4. Negative evidence

- Dim, Eraker and Vilkov (WFA 14 May 2024 version, sample 2012 to mid-2023): null on propagation; abstract and intro quotes in section 3. "The average daily open interest gamma did not grow after 2016, neither for 0DTEs nor for the other maturities" (intro, txt 156-158). No sized ES/SPX return effect usable as a trade.
- Authors' own feasibility denial (Adams et al. 2026, section 4.4): "this result does not translate into a
  feasible trading strategy since the market makers' net gamma is not observable to other investors."
- Effect decays fast: order-flow predictability "decays toward zero within the hour" (Adams et al., intro).
- Net gamma is mostly positive (RD5 row 11, from the same paper): "Net Γt is positive for 88 percent of all
  10-minute trading intervals", so the vol-amplifying (negative gamma) state is rare.
- Amaya et al. (2025): the gamma channel is economically small relative to all causes of volatility
  (quotes in section 3).
- Vilkov, "0DTE Trading Rules: Tail Risk, Implementation, and Tactical Timing" (SSRN 4641356), replication
  package README (fetched from GitHub raw, last updated Aug 2026): "Correction, August 2026. A
  transaction-cost unit-scale error caused the bid-ask half-spread to be charged at 1/100 of its true size
  (about 0.022 bp instead of 2.2 bp). ... the correction reverses the sign of the net-of-cost conclusions: no
  strategy or basket retains a positive net Sharpe ratio." KNOWN-ISSUES.md: "No structure retains a
  materially positive net Sharpe ratio." and "on the paper's full sample the put-ratio conditional net Sharpe
  goes from +0.93 to -0.75 and the top-three basket from +0.82 to -0.82." (These are SPXW option
  strategies, not futures; grade working-paper/replication-package; the paper PDF itself is
  "still being revised" per the README and was not read.)

## 5. Data and cost

- R1-C1 needs Cboe Open-Close Volume Summary (SPX/SPXW, intraday 10-minute, open/close by participant
  class) for signed market-maker positions, plus ES 1-min bars (owned). The program does not own the
  Cboe data. Published price: not fetched by R1 (R2 owns vendor/data pricing; cite R2). Terms on use:
  unread by R1.
- Public GEX proxies (SqueezeMetrics, open-interest based) are what C2/E20H6-T3 used; Adams et al.'s point
  is that the signed measure differs (RD5 rows 11-12).

## 6. Prop compatibility

R1-C1: intraday, 1-2 h hold, entries at 10-minute marks in RTH, flat by 15:10 CT feasible if entries stop by
about 13:10 CT; low frequency (not HFT); automation permitted per R9; P06 news rule binds on release days
only. Real-time signal availability is the blocking issue, not prop rules.

## 7. Overlap with tested mechanisms

- E13/E14-C2 (GEX-conditioned S&P late-session momentum, stopped at power rule): same family (dealer
  gamma conditioning of momentum); R1-C1 differs by using signed Cboe positions and hourly reversal across
  the whole session rather than open-interest GEX and the last half-hour.
- E20H6-T3 (previous-day GEX < 0 conditioning of last-half-hour NQ momentum, FAIL): same idea, opposite
  regime (negative gamma amplifies momentum); R1-C1 uses the high positive gamma state and ES, intraday.
  r0_mechanism_index.md not re-grepped in this rerun: overlap ids above are from the spawn message; lead to check.

## 8. Re-dig (not a re-dig reader; verdict notes only)

- E20H6-T3 FAIL: SUPPORTED (low-gamma momentum is about 0.7 bp, below the MNQ/MES hurdle; RD5 row 127
  says the same).

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://www.vilkov.net/ | 2026-10-18T13:13Z | 3130f92565b301aa5c05c0b157f3e723ddc9b5bf1d58a0580328dea7407bb3e2 | pages/R1/vilkov_home.html | ok (no paper PDFs linked) | curl |
| https://www.vilkov.net/robots.txt | 2026-10-18T13:13Z | - | pages/R1/vilkov_robots.txt | ok (sitemap line only, no disallow) | curl |
| https://raw.githubusercontent.com/vilkovgr/0dte-strategies/main/README.md | 2026-10-18T13:13:48Z | bdfbd7973191e83cff9127d905d93ca983a4cbddb789a05db534524c6b68122a | pages/R1/vilkov_0dte_strategies_README.md | ok | curl |
| https://raw.githubusercontent.com/vilkovgr/0dte-strategies/main/KNOWN-ISSUES.md | 2026-10-18T13:14Z | e1141b5b9aec78ca27c7106fb46351b847c14c612a72ffab21e6386ff79b96d8 | pages/R1/vilkov_0dte_KNOWN-ISSUES.md | ok | curl |
| https://westernfinance-portal.org/viewpaper?n=950096 | 2026-10-18T13:15:52Z | 2064cff3cd3b2de2681f03eb99630ab8b5f8683d39142593d20b0f5bb8ea8d43 | pages/R1/dim_eraker_vilkov_wfa.pdf (+ .txt) | ok (terms not read: gap) | curl |
| (first run) Amaya et al. Cboe PDF, Bandi-Fusari-Reno PDF, Baltussen-Terstegge-Whelan PDFs, Ladia 2026 | 2026-10-18 ~08:42-08:51Z | see files | pages/R1/*.pdf(.txt) | ok (first run; URLs not logged by it) | first-run worker |
| Adams et al. 2026 | - | 074f8ca85a868bda (prefix) | reports/stage_e20_briefs/shared/adams_etal_0dte_fontaine.pdf.txt | reused from E.20, not refetched | - |

Terms: vilkov.net robots.txt read (no disallow); terms page not found on the homepage, not logged to
terms_log.md (gap). GitHub raw: public repository files, one request each.
Budget notices (first run): 2026-10-18T08:43:08Z Firecrawl search per-minute limit; 2026-10-18T08:46:56Z
OpenAlex HTTP 429 (daily credit exhausted). Rerun: 2 WebSearch calls, no budget notice. westernfinance-portal.org terms not read (gap; one PDF fetched).

## 10. Unfinished and unverified items

- Dim, Eraker and Vilkov: the May 2024 WFA version was read by grep (abstract, intro); the SSRN revision of 6 Jun 2025 was not; tables not mined for bp effects.
- Brogaard, Han and Won (one WebSearch at 06:16 PDT found no open copy), "How Does Zero-Day-To-Expiry Options Trading Affect the Volatility of Underlying
  Assets?" (SSRN 4426358): NOT read. [unverified].
- Beckmeyer, Branger and Gayda (0DTE retail trading): NOT searched or read.
- Bandi, Fusari and Reno, "0DTE option pricing" (Mar 2024 draft, on disk): read only its front matter; it is a
  pricing paper with no sized ES/SPX return effect found by grep; not mined further.
- Vilkov "0DTE Trading Rules" paper PDF itself not read; only the replication README and KNOWN-ISSUES.
- Baltussen-Terstegge-Whelan and Ladia 2026 PDFs (first run) not read in this rerun.
- No per-trade sd for R1-C1; overlap ids not re-checked against r0_mechanism_index.md; terms page for
  vilkov.net not saved.
