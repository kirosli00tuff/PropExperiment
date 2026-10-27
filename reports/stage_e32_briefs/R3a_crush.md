# R3a_crush: soybean-complex economics for a minutes-to-hours ZM directional search

Stage E.32, Part R3 (first half). Worker CrushEconomics-OpusHigh. Started 2026-10-26 23:03 PDT.
Evidence pages and log: reports/stage_e32_briefs/pages/R3a_crush/ (log.tsv). Scratch: reports/stage_e32_briefs/work/R3a_crush/.
No market data was read and no statistic was derived from data. Every number below is either quoted from a saved
full text (file named) or is arithmetic on contract specifications and quoted numbers, shown step by step.
Source labels: [academic], [practitioner], [regulator], [exchange], [firm], [extension] (university extension
service, e.g. farmdoc daily, Southern Ag Today; written by academics but not peer reviewed).

Status of sections: 1-11 done (sections 7-11 written after a re-spawn, 2026-10-27 00:16-00:22 PDT).

---

## 1. Contract arithmetic: the board crush, its units, the 10:11:9 and 10:12:9 ratios, and tick conversions

### 1.1 Facts

- Contract units and ticks used here (E.28 owned-data table, reports/stage_e28_briefs/A0_contract_stats.md lines
  114-117, quoted: `| ZM | yes | 0.10 | 10.00 | 3.15 |`, `| ZS | yes | 0.0025 | 12.50 | 3.11 |`,
  `| ZL | yes | 0.0001 | 6.00 | 5.52 |`): ZM tick 0.10 USD per short ton, 10.00 USD; ZS tick 0.0025 USD/bu
  (0.25 cents/bu), 12.50 USD; ZL tick 0.0001 USD/lb (0.01 cents/lb), 6.00 USD. Contract sizes follow: ZM
  10.00/0.10 = 100 short tons; ZS 12.50/0.0025 = 5,000 bu; ZL 6.00/0.0001 = 60,000 lb. Poitras's course note
  states the same sizes [academic teaching note]: "Weight of one CME soybean contract: (5000 bu.)(60 lbs) =
  300,000 lbs. / Weight of one CME soy meal contract: (100 tons)(2000 lbs.) = 200,000 lbs. / Weight of one CME soy
  oil contract: 60,000 lbs." (poitras_soycrush_wpd.pdf.txt). CME's own pages were not fetched (stage rule).
- The CME "board crush" yield, quoted second-hand from CME by farmdoc daily [extension]: a bushel of soybeans
  yields "11 pounds of soybean oil, 44 pounds of 48 percent protein soybean meal, 4 pounds of hulls and 1 pound of
  waste" (CME Group)" (Janzen and Wang 2025, farmdoc_fdd101325_oilshare.pdf.txt, Appendix).
- The older USDA convention is 48 lb of meal. Rechner and Poitras (1993) [academic]: "a (60 lbs.) bushel of
  soybeans yields 11 lbs. of oil and 48 lbs. of meal [USDA (1988)]" and "Given the CBOT contract specifications,
  this translates into 10 soybeans, 12 meal, and 9 oil contracts for a balanced position."
  (rechner_poitras_1993.pdf.txt lines 105-116). Smith (2021) [extension] explains the two conventions: "There are
  two common approaches to estimating the quantity of soybean meal: (1) the one depicted above, 48 lbs of soybean
  meal at (44% protein) or (2) 44 lbs of soybean meal (48% protein), which is used by CME group."
  (tamu_meal_or_oil.txt).
- Poitras's note [academic teaching note] names both ratios: "The CME Soybean Crush Guide (p.7) (see BUS 419
  webpage) uses 10 Soybean, 11 Soy Meal and 9 Soy Oil" (poitras_soycrush_wpd.pdf.txt). So 10:11:9 is the CME
  (44 lb) ratio and 10:12:9 the USDA-1988 (48 lb) ratio used by Rechner and Poitras.
- Actual yields drift: farmdoc [extension] reports "the standard board crush margin calculation assumes 11 pounds of
  each 60-pound bushel of soybeans, or 18.3%, is oil" while "Oil extraction rates have increased and now are
  routinely around 20% of output" (farmdoc_fdd091025_extraction.pdf.txt lines 57-60); and NOPA data put oil "from
  just more than 11 pounds to about 12 pounds per bushel" and meal "consistently between 47 to 48 pound per
  bushel. USDA crush data indicate a meal share closer to 44 pounds." (farmdoc_fdd101325_oilshare.pdf.txt,
  Appendix). The board formula's weights are a convention, not the physical yield.

### 1.2 Equations

Board crush margin per bushel (CME 44-lb convention):

    C_44 [USD/bu] = (44/2000) * M + (11/100) * O - S/100
                  = 0.022 * M + 0.11 * O - S/100

    M = ZM price, USD per short ton; O = ZL price, cents per lb; S = ZS price, cents per bu.
    44/2000 = 0.022 short tons of meal per bushel; 11 lb oil per bushel times O/100 USD/lb = 0.11 * O USD/bu.

USDA-1988 (48-lb) convention: C_48 = 0.024 * M + 0.11 * O - S/100.

In cents per bushel: C_44 [c/bu] = 2.2 * M + 11 * O - S.

Oil share of crush output value (the "oil share"): OS = 0.11 * O / (0.022 * M + 0.11 * O) under 44 lb, or
0.11 * O / (0.024 * M + 0.11 * O) under 48 lb (farmdoc's definition: "The share of crush value for each component
is the revenue for each component as a percentage of total revenue", farmdoc_fdd101325_oilshare.pdf.txt).

Leg sensitivities of C_44 (cents/bu per one tick of each leg), from the partial derivatives:
- dC/dM = 2.2 c/bu per USD/ton; one ZM tick (0.10 USD/ton) = 2.2 * 0.10 = 0.22 c/bu.
- dC/dO = 11 c/bu per c/lb; one ZL tick (0.01 c/lb) = 11 * 0.01 = 0.11 c/bu.
- dC/dS = -1; one ZS tick = 0.25 c/bu.

### 1.3 Worked arithmetic

(a) Ratios. 10 ZS = 10 * 5,000 bu = 50,000 bu.
- Meal at 44 lb/bu: 50,000 * 44 = 2,200,000 lb = 2,200,000/2,000 = 1,100 short tons = 1,100/100 = 11 ZM.
- Meal at 48 lb/bu: 50,000 * 48 = 2,400,000 lb = 1,200 short tons = 12 ZM.
- Oil at 11 lb/bu: 50,000 * 11 = 550,000 lb = 550,000/60,000 = 9.17 ZL, rounded to 9 (540,000 lb, i.e. 10.8 lb/bu).
- Check against Poitras's husk arithmetic: 10:11:9 leaves 3,000,000 - 2,200,000 - 540,000 = 260,000 lb; the note
  says "(300,000)(10) - (200,000)(11) - (60,000)(9) = 260,000 lbs. of husks". 10:12:9 leaves 60,000 lb; the note
  says "= 60,000 lbs. of husks". Both match.

(b) Dollar value of 1 cent/bu of crush on the 10-lot position: 50,000 bu * 0.01 USD/bu = 500 USD. Rechner and
Poitras: "when trading 10 soybean, 12 meal, and 9 oil contracts, a 1-cent per bushel change in the GPM represents a
$500.00 change in the value of the position" (rechner_poitras_1993.pdf.txt line 133). Match.

(c) One ZM tick in crush units. 0.022 ton/bu * 0.10 USD/ton = 0.0022 USD/bu = 0.22 c/bu. Check by dollars: 11 ZM *
10 USD = 110 USD per tick on all 11 lots; 110 USD / 50,000 bu = 0.0022 USD/bu = 0.22 c/bu. Match.
Inverse: 1 c/bu / 0.22 c/bu per tick = 4.545 ZM ticks. So a 1 c/bu crush dislocation closed entirely by ZM is
about 4.5 ZM ticks (45.45 USD per ZM lot). Under 48 lb the factor is 0.24 c/bu per tick and 1/0.24 = 4.17 ticks.

(d) Rechner and Poitras's execution-cost arithmetic as an independent check of the leg conversions on 10:12:9
(two ticks per leg per round trip): "0.5 + 0.48 + 0.216 = 1.196 cents per bushel" (line 142). Recompute: beans
2 * 0.25 = 0.50 c/bu; meal 2 ticks * 0.10 USD/ton * 0.024 ton/bu = 0.0048 USD/bu = 0.48 c/bu; oil 2 ticks * 0.01
c/lb * 10.8 lb/bu = 0.216 c/bu (9 lots * 60,000 lb / 50,000 bu = 10.8 lb/bu). Sum 1.196 c/bu. Match.

(e) One-minute volatility of each leg in crush units on the E.28 standard numbers (2022-11-01..2023-10-31, front
contract): ZM 3.15 ticks * 0.22 = 0.693 c/bu; ZS 3.11 ticks * 0.25 = 0.778 c/bu; ZL 5.52 ticks * 0.11 = 0.607 c/bu.
The three legs move the crush by similar amounts per minute, so none is negligible. An upper bound on the crush's
one-minute SD (legs perfectly anti-aligned in their crush contribution) is 0.693 + 0.778 + 0.607 = 2.08 c/bu; the
legs are positively correlated in price and beans enter with the opposite sign, so the true SD is far lower. No
correlation is computed here (no new statistic from data).

(f) Oil share, worked on quoted futures prices. Smith (2021) [extension] quotes futures moving "from $417.60/ton in
January 2021 to $312.90/ton in October 2021", oil "from 44.62 cents/lb to 58.62 cents/lb", beans "from $13.70/bu
to $11.88/bu" (tamu_meal_or_oil.txt). October 2021 under 48 lb: meal 0.024 * 312.90 = 7.510 USD/bu; oil 0.11 *
58.62 = 6.448 USD/bu; OS = 6.448/(7.510 + 6.448) = 6.448/13.958 = 46.2%; margin = 13.958 - 11.88 = 2.078 USD/bu.
Smith reports "54% of soybean value attributed to meal and 46% to oil" and "the crush margin was $2.08" (as of
October 13, 2021). Match. Under 44 lb: meal 0.022 * 312.90 = 6.884; OS = 6.448/13.332 = 48.4%; C_44 = 13.332 -
11.88 = 1.452 USD/bu. The convention moves the oil share by about 2 points and the margin by 0.6 USD/bu at these
prices, so any oil-share feature must name its convention. January 2021 under 48 lb: 0.024 * 417.60 = 10.022;
0.11 * 44.62 = 4.908; OS = 4.908/14.930 = 32.9% (Smith: meal "65%" of value for "the first three months of 2021",
i.e. oil about 35%, a three-month average, so a rough rather than exact match).

### 1.4 What this means

- A 1 c/bu crush residual is 4.5 ZM ticks if ZM alone closes it. E.28's Topstep ZM market-order break-even is 1.59
  ticks (reports/stage_e28_ranking.md line 130, row `| 6 | topstep | ZM | ... | 0.59 | 1.59 | ...`, column
  mu*_mkt). So a residual of 1.59/4.545 = 0.35 c/bu closed fully by ZM pays one break-even. Whether ZM is the leg
  that closes it is an empirical question (Section 5).
- The weights are conventions. A residual built on 0.022/0.11 will carry a slow drift as true yields move (oil
  18.3% to about 20% since 2020). For minutes-to-hours horizons this drift is negligible within a day but matters
  for any level-based (not change-based) residual estimated over months.

---

## 2. The oil-share regime change (renewable diesel) and the discovery/test split

### 2.1 Facts

- Janzen and Wang (farmdoc daily, 2025-10-13) [extension], weekly Illinois processor prices, 2007-2025: "Between 2013
  and 2020, the oil value share ranged between 25 to 35 percent. Since 2020, it has only rarely been below 35
  percent. In both 2021 and 2025, it briefly reached 50 percent." and "there is a stark jump in the oil value share
  in late 2020 that has persisted to the present" (farmdoc_fdd101325_oilshare.pdf.txt).
- Same source on margins: "Since late 2020, crush margins have periodically increased and become considerably more
  volatile. Changes in crush margins are much larger now than they were before 2020."
- Same source, the key regime statistic. Weekly first-difference regressions of soybean price changes on meal and
  oil price changes: May 2007-September 2020 "dSB(t) = 0.000 + 0.511 dSBM(t) + 0.232 dSO(t), R2 = 0.791", and "The
  results are similar for the 2017 to 2020 period after Irwin concluded his analysis but before the renewable
  diesel boom period." For October 2020-September 2025: "dSB(t) = 0.000 + 0.451 dSBM(t) + 0.070 dSO(t), R2 = 0.322"
  and "It appears a previously stable relationship among soybean crush components has broken down." Also: "the
  correlation between these price changes has broken down." Units there are USD per pound for all three (they
  "convert all prices to dollars per pound"); the regression is weekly cash prices, not futures, not intraday.
- Price levels: "The soybean oil price nearly tripled from $0.26 per pound to $0.94 per pound" between late 2020
  and early 2022, while "Soybean prices roughly doubled and soybean meal prices increased by roughly 60%."
- Physical yields shifted at the same time: "the realized US soybean oil extraction rate jumped to 19.7% in late
  2020 and then continued to increase to around 20.0% for much of 2025. (November and December in both 2022 and
  2023 were short-lived exceptions to this otherwise persistent shift.)" (farmdoc_fdd091025_extraction.pdf.txt
  lines 112-114).
- Smith (Southern Ag Today, 2021-10-25) [extension]: "the percent of value derived from meal and oil changed in April
  2021. For the first three months of 2021, soybean meal was 65% of the soybean value, the same as the January 2006
  to October 2021 average." Drivers named: vegetable-oil stocks ("days-on-hand ... to drop from 41.7 days ... to
  38.5 days") and "current and potential demand for biodiesel derived from soybean oil" (tamu_meal_or_oil.txt).

### 2.2 Mapping onto E.32's windows

- Sealed test window 2017-05..2020-11: falls inside the pre-boom regime (oil share 25-35%, weekly R2 about 0.79,
  stable leg relations), apart from its last months (the "stark jump" is dated "late 2020"; Janzen and Wang's
  second regression starts October 2020). Other events inside it (US-China trade war 2018-19, Covid 2020) are not
  covered by these sources; the planner's mention of them is [unverified] here.
- Discovery window 2020-12..2024-02: entirely inside the renewable-diesel regime (oil share mostly above 35%, peak
  near 50% in 2021, weekly R2 about 0.32, more volatile margins, the oil price peak of early 2022).
- Therefore the discovery data contain a crush whose legs co-move LESS tightly (at the weekly horizon) than in the
  test window. Two opposite risks follow: (i) a crush-residual signal tuned on discovery could find wider, noisier
  residuals and fewer clean reversions, then meet a test window where reversion is tighter but residuals smaller
  (fewer triggers at a fixed threshold, smaller gross per trade); (ii) fixed ZM/ZS/ZL betas fitted on 2020-24 will
  be wrong in 2017-20 (the oil coefficient fell from 0.232 to 0.070 in the weekly regression). This supports the
  planner's suggestion of adaptive (causal rolling) betas and thresholds in units of a rolling residual SD rather
  than fixed cents.
- No source found measures the regime change at intraday horizons. The weekly evidence does not say whether
  minute-scale leg co-movement changed. [gap, stated as such]

### 2.3 Worked example: what the regime shift does to ZM's weight in the crush

Using the weekly coefficients as given (USD/lb units, so they are value-per-pound sensitivities, not contract
hedge ratios): the share of a soybean price change "explained" per unit oil change fell by 0.232 - 0.070 = 0.162,
i.e. to 0.070/0.232 = 30% of its earlier size, while the meal coefficient changed by 0.511 - 0.451 = 0.060, i.e. to
0.451/0.511 = 88%. Check: 0.070/0.232 = 0.3017; 0.451/0.511 = 0.8826. Reading: soybean price changes became much
less tied to oil and only slightly less tied to meal. For a ZM-centred residual this is mildly reassuring (the
beans-meal link held better than the beans-oil link), but it is weekly cash-price evidence.

---

## 3. Intraday cointegration of ZS, ZM and ZL: Zhou, Bagnarosa, Gohin, Pennings and Debie

The only study found that tests crush cointegration inside the trading day on CME data. Two versions read in full:
the journal article (J. Commodity Markets 30 (2023) 100314, open access CC BY, zhou_jcm2023_wur.pdf.txt) and the
NCCC-134 2022 conference version with the supplementary tables (zhou_nccc134_2022.pdf.txt). [academic]

### 3.1 Facts (verbatim)

- Data: "The high-frequency data used in this study covers the total trading activity of 2015, amounting to 243
  trading days." (JCM line 587). One-minute snapshots, chosen "to limit the Epps effect" (NCCC lines 890-892).
- Sessions: "the electronic trading session from 7PM to 7.45AM (session 1) and the market trading session from
  8.30AM to 1.20PM (session 2), during which most of the trades take place." (NCCC lines 893-895). Note: in 2015
  the day session closed 13:20 CT; E.32 uses 08:30-13:20 for the day session too.
- Model (JCM Eq. (10)): "dP_t = c_0 + Pi P_{t-1} + sum_{j=1}^{p-1} Gamma_j dP_{t-j} + e_t ... where the low-rank
  matrix Pi = kappa beta' can be decomposed into two rank h-matrices kappa and beta of dimensions (n x h) and
  e_t ~ N(0, Sigma)." It is cast in state-space form (Eq. (12), x_t = F x_{t-1} + G e_t) with idle (untraded)
  prices treated as missing and estimated by EM.
- Plain Johansen on raw one-minute prices finds little: "Hardly any cointegration was detected using Johansen's
  approach, regardless of the matching method applied." Table 2 (JCM): Johansen "all price" 64 cointegrated days,
  ZSmatch 69, ZLmatch 70, ZMmatch 68; the missing-data-filtered state-space test 180 days, 11 months, 3 quarters.
- Session effect, NCCC supplementary Tables 7-9 (ZS open-interest rollover row): session 1 (overnight) "52 / 2 / 1"
  (day/month/quarter); session 2 (day) "180 / 11 / 3"; session 1 + session 2 together "52 / 2 / 1". Text: "prices
  in session 1 are so greatly affected by market noise that even the combining of both sessions yields no
  additional information about the joint dynamics of asset prices and, even worse, prevents identification of
  the cointegrated days." (NCCC lines 2649-2653). JCM text: "A high level of cointegration is indeed observed during
  session 2 trading hours, which fades away during session 1." (JCM lines 745-746).
- Sampling frequency: "The two-minute daily data set allows us to detect 229 days of cointegration (versus 180
  using the 1-minute daily data set)" (NCCC line 2756).
- USDA days: "the stronger intraday cointegration observed on average on USDA announcement days, although the
  number of observations available is limited." (JCM lines 746-747).
- Cointegrating vector (JCM Table 4, cointegrated days only, normalised ZS = 1, missing-data filter): Median ZL
  -0.11, ZM -0.19; Average -0.09, -0.21; quartiles 25% -0.17, -0.24 and 75% -0.06, -0.14; StDev 0.28, 0.28; "CME
  (physical)" -0.11, -0.22. Johansen: median -0.13, -0.17, StDev 0.5, 0.47.
- Speed of adjustment, not vector, depends on volume: "traded volumes, epitomizing disagreement on market
  expectations, mainly influence the speed of convergence towards the stationary cointegrated joint process,
  rather than the cointegrating vector itself." (JCM conclusion, line ~984).
- Leadership: "If the traded volumes of soyoil relative to soybean increase, we can expect soymeal to even more
  significantly Granger cause the soyoil dynamics ... Nevertheless, the lower the traded volumes of soymeal
  relative to soyoil, the less soymeal prices will Granger cause soybean prices" (JCM lines 814-820). And:
  "important potential trading volumes in the main market, the soybean market in our case, or a lack of liquidity
  in the secondary markets, i.e., soybean meal and oil, act as a counterbalance and may discourage the fully
  informed traders from building correcting trades to enforce the cointegration relationship." (JCM conclusion).
- Rollover: "some intermediary contract maturities are not considered by informed traders throughout the year,
  thus leaving unused their capacity to counterbalance on an intraday basis" (JCM conclusion); the ZS
  open-interest rollover gave the most cointegrated days (NCCC Table 8: 180 vs monthly rollover 132).
- No half-life, no loading (kappa) magnitudes in time units, and no trading rule are reported. A grep of both
  full texts for "half" finds no half-life. The kappa results are reported only as regression coefficients of
  kappa ratios on volume ratios (JCM Table 3).

### 3.2 Worked arithmetic

- Share of days cointegrated, day session, 1-minute: 180/243 = 0.741 (74%). At 2-minute: 229/243 = 0.942 (94%).
  Overnight session: 52/243 = 0.214 (21%). Plain Johansen, day session: 64/243 = 0.263 to 70/243 = 0.288.
- The ZM weight: median -0.19 against physical -0.22, a gap of 0.03, i.e. 0.03/0.22 = 13.6% smaller in magnitude.
  Daily SD 0.28 is larger than the median magnitude itself (0.28/0.19 = 1.47), and the interquartile range is
  -0.24 to -0.14 (width 0.10). So a single day's estimated vector is a noisy estimate of the physical weights; a
  fixed physical vector or a long-window estimate is the sensible residual for a trading signal.
- Units caveat [unverified, needs reviewer]: with prices in CBOT quote units (ZS cents/bu, ZL cents/lb, ZM USD per
  short ton) the board crush is S - 11 O - 2.2 M; Marowka et al. [academic] write "the Chicago Board of Trade
  (CBOT) quotes the crush spread as yt(1) - 11yt(2) - 2.2yt(3)" (marowka_spiral_b.pdf.txt lines 67-68). Normalised
  to ZS = 1 that is (1, -11, -2.2). Zhou's "CME (physical)" row (1, -0.11, -0.22) is reproduced only if ZS is in
  USD/bu and both ZL and ZM are in units 100 times smaller than cents/lb and 10 times smaller than USD/ton
  respectively, or under some other price scaling the paper does not state. The ratio of the meal to the oil
  weight is 2.2/11 = 0.2 in quote units but 0.22/0.11 = 2.0 in Zhou's table. The paper does not give its price
  units; the comparison "-0.19 vs -0.22" is internally consistent within the paper, but the vector cannot be
  applied to quote-unit prices without knowing the scaling.
[MathReview A-12 (lead: accepted): the stated scaling does not reproduce the row (ZS in USD/bu, ZL in 0.01 c/lb units and ZM in 0.10 USD/ton units give (1, -0.0011, -0.0022)); two scalings reproduce (1, -0.11, -0.22): (A) ZS in c/bu, ZL in ticks of 0.01 c/lb, ZM in ticks of 0.10 USD/ton (11 x 0.01 = 0.11; 2.2 x 0.10 = 0.22), M2's reading in M2 (c) (M2:318-319), or (B) ZS in USD/bu, ZL in c/lb, ZM in units of 10 USD/ton (0.11; 0.022 x 10 = 0.22), while quote units give (1, -11, -2.2). Zhou's text states no units and uses "the last trading price" (zhou_etal_nccc134_2022.pdf.txt line 1019); the internal evidence favours a tick-like scaling, and the conclusion of this section (compare -0.19 with -0.22 only as a ratio inside the paper; use a fixed physical vector or a long-window estimate for the signal) stands.]

### 3.3 What it implies for a ZM search

- Day-session (08:30-13:20) crush residuals are mostly stationary within the day at 1-2 minute sampling (in 2015);
  overnight residuals mostly are not. This is direct support for computing any crush residual on day-session data
  and for treating overnight crush moves as weakly anchored.
- Who adjusts depends on relative volumes (the volume ratios move the kappa ratios), so "which leg adjusts" is a
  state variable, not a constant. A ZM-only trade on a crush residual should be conditioned on relative volume
  (ZM vs ZS vs ZL) and, per the theory, it works best when the byproduct markets are liquid relative to beans.
- The study is 2015 only, one year, a different regime (pre-renewable-diesel) from both E.32 windows, and reports
  no speed in minutes, so it cannot size the signal.

---

## 4. Crush-spread trading rules: profitability and decay

### 4.1 Facts, in date order of the samples

- Johnson, Zulauf, Irwin and Gerlow (JFM 1991, 11(1) 25-37) [academic; full text not read: the NCR-134 1990
  precursor johnson_etal_nccc1990.pdf is a scanned image (pdftotext returns 81 words, no OCR tool on this
  machine); evidence is second-hand, marked]. Per Rechner and Poitras: "Five trades are initiated at the closing
  price on the 15th of every month and then lifted at preset intervals: 1.5, 3.5, 5.5, 7.5, and 9.5 months" and
  quoting Johnson et al.: "Significant profits above transactions costs are not found at trade lengths of 1.5 and
  3.5 months, but are found at trade lengths of 5.5 months or longer" (rechner_poitras_1993.pdf.txt lines 69-78).
  Per Mitchell: sample "1966-1988"; "While 1.5 month trades result in an average loss of $156, profit increases to
  $3, $241, $235, and $418 as the trade length increases." (mitchell_jrfm2010_firecrawl.md line 101).
  [secondary, unverified against Johnson et al.'s own text]
- Rechner and Poitras (JFM 1993, 13(1) 61-75) [academic, full text read]: rule "If the GPM on the open is less
  (greater) than the previous day's close, a reverse crush (normal crush) spread is placed. In all cases, the
  position is liquidated on the close of the same day." Costs "1.5 cents per bushel" round trip. Daily open/close
  data, "February 1, 1978 to July 31, 1991", pit era. Aggregate table (OCR heading "Table IV", text calls it Table
  II), net of costs, filters 0 / 1 / 2 / 3 cents: mean profit per trade -0.36 / 0.35 / 1.02 / 1.74 c/bu; trades
  3352 / 1861 / 922 / 457; t-values -7.69 / 5.08 / 9.10 / 9.30; percent profitable 39.6 / 52.3 / 62.3 / 69.0.
  Key correlation, Table IA (1978-87): "(Close, - Open,) and (Open, - Close,-1) -0.49 (-23.7)"; Table IB
  (1987-91): "-0.43 (-14.2)". The single legs show no such effect: meal "-0.019 (-0.92)" in 1978-87 and "-0.067
  (-2.22)" in 1987-91. Authors: "it provides indirect support for the possibility of 'opening reversals'; or, in
  other words, the tendency of GPM to change direction at the open." Decay warning: "the small number of trades
  in 1990 combined with the poor performance of 1991 does raise concern ... a substantial upward shift in the GPM
  starting with the June 1, 1989 rollover date." Their explanation: "While the public is in on the close only
  the trading floor is in on the open."
- Simon (JFM 1999, 19(3) 271-289) [academic; full text not obtained (Wiley paywall; no author copy found);
  abstract from IDEAS, simon1999_ideas.html]: "deviations of the soybean crush spread from its long-run
  equilibrium were transitory during the sample period from January 1985 through February 1995. This equilibrium
  is characterized by strong seasonality and by a persistent uptrend in soymeal and soyoil prices relative to
  soybean prices. A tendency also exists for the crush spread to revert toward its most recent 5-day average.
  Simulations demonstrate that trading rules based on these results would have been profitable." Mitchell's
  summary of Simon: "the crush spread tends to revert toward its 5-day moving average with a half-life of
  deviations of about 3 days" and "Trades prove profitable after adjustment for transaction costs ($103.50 per
  round-trip trade)". [half-life is secondary via Mitchell; not seen in Simon's text]
- Liu (JFM 2005, 25(5) 491-514), hog-corn-meal analogue [academic, abstract only]: three series "cointegrated with
  one single cointegrating vector, whose coefficients are comparable to the ratios used by the United States
  Department of Agriculture"; "Ex-post trading simulations that utilize the cointegration results generate
  significant profits" (liu2005_ideas.html). Daily-to-longer horizon; included because the brief names it.
- Mitchell (JRFM 2010, 3(1) 63-96) [academic, full text read via Firecrawl, mitchell_jrfm2010_firecrawl.md]: data
  "June 4, 1984 through April 7, 2006", daily closes, "a naive 1:1:1 relationship". Entry when the spread deviates
  from its 5-day moving average by 200-400 USD, exit at 0-200 USD; costs 103.50 USD per round trip. Results:
  "Average profit ... ranges from a low of -$41.88 at limits of 100/80 to $122.17 at 400/80." The fourth (latest)
  time segment "gives negative average profit results, a higher standard deviation of profit, a lower percentage
  of profitable trades, and longer trade length." Replication of Simon: "A trader who bases their trading
  practices on the results for $200 limits reported by Simon would experience, over the 20-year period, average
  losses of $20 per trade rather than an approximate $200 average profit per trade as reported by Simon."
  Conclusion: "Unless further research demonstrates arbitrage limits (filters) with more appealing risk-return
  characteristics, the soybean crush spread should be considered an efficient market." Trade length: "profitable
  trades are significantly shorter than losing trades"; "no trade at any set of limits up to 400/200 produces a
  profitable trade in excess of 9 days". Also: "In October, 1992 the CBOT changed the soymeal contract
  specifications from 44% protein to 48% protein."
- Liu and Sono (JFM 2016, 36(11) 1057-1075), Dalian [academic, abstract only, jfm2016_v36i11_ideas.html]:
  cointegrated with "significant seasonality and consistent time trends"; "evidence of one-way information flow
  from the soymeal and soyoil markets to the soybean market"; "Trading simulations based on the mean-reverting
  tendencies of the cointegration relationship and 5-day averages of the commonly-used spread both generate
  positive returns."
- Dunis, Laws and Evans (book chapter, 2009) [academic; pointer only, purchase-only, not read]: per the search
  snippet, for "most of the models, trading costs all but eliminate any profit potential". [unverified: search
  snippet only]
- Gu and Lei (ICMMCT 2018, Atlantis) [academic, conference; read]: Dalian/Zhengzhou crush, daily, 2013-2016
  ("from January 4, 2013 to December 2016. The daily", atlantis_25900046.pdf.txt line 106). Low-tier venue; not
  used further.
- Abdoh and Chitavi (IREF 2025, vol. 101, 104186) "Mean reversion of the soybean crush spread: A new model and
  trading strategies" [academic]. Retrieval: ScienceDirect returns 403 to curl; no author or SSRN copy found in two
  searches; Scrapling not used (the page declares Elsevier "tdm-reservation" = 1); Firecrawl (route 4) in
  directQuote mode returned verbatim passages but not the raw page. Those passages are saved in
  abdoh_chitavi_firecrawl_directquote.txt; treat them as PARTIAL full text (the extractor chose the passages; table
  layouts are fragmentary). Abstract (IDEAS, abdoh_chitavi_ideas.html): "no study has examined how intraday
  deviations of soybean products from the processing relationship reflected in USDA estimates affect the soybean
  crush spread. We introduce a new market-based measure that captures these deviations in the short term ...
  trading strategies based on these findings would have been profitable, even after accounting for transaction
  costs. This analysis is based on 8650 trading days from September 1990 to May 2021."
  From the extracted passages:
  - Data: "futures prices captured at 10-min intervals" from tickdata.com; "We use non-missing intraday price data
    of beans and their products, which cover 8650 trading days."
  - The measure: a regression run "each day" of the intraday bean price on meal and oil prices, "Bean_t = a0 + a1
    Meal_t + a2 Oil_t + mu_t" (their Eq. (2)), whose coefficients "can be interpreted as the magnitudes of meal and
    oil inferred by market prices"; means "0.02 and 0.117, which are equivalent to 40 and 11.7 pounds". DEV-GCM
    (their Eq. (3)) values the gap between these market-implied yields and USDA yields at that day's prices.
  - Speed: "the transitory movements from the long-run equilibrium, which lasts 10.4 days on average"; half-life
    "in terms of days as (ln(0.5)/ln(1+b1))"; Table 4 half-lives "38.81 days" (seasonal-dummy-and-trend residual)
    and "28.41 days" (adding lagged DEV-GCM); with 30- and 60-day moving averages of DEV-GCM, b1 "-0.0256" and
    "-0.0251", half-lives "26.72 days" and "27.26 days".
  - Trading: daily rules, entry when the residual exceeds X times its SD with X in {0, 0.05, 0.10, 0.15, 0.20},
    exit "when the residual reverts to zero"; one panel shows "Number of trades | 406 | Average duration (days) |
    6.09 | ... Winning trade percentage | 66.01 % | Average profit (per pound) | 0.0018 | ... t-statistics | 5.137".
    Costs "$75 per contract per round-trip" on "two contracts of soybean, three contracts of soymeal, and ten
    contracts of soyoil" (15 * 75 = 1,125 USD); "if traded applying e1, the average profits become equal to $1,080,
    $1,380, $1,500, $1,800, and $2040 using the thresholds of 0,0.05,0.1,0.15, and 0.2 respectively. However,
    after accounting for transaction costs when applying e2, trading is not profitable."
  This is a DAILY trading rule whose signal uses intraday (10-minute) prices to estimate the day's implied yields.
  It is not a minutes-scale rule.

### 4.2 Worked arithmetic

(a) Rechner and Poitras gross edge. Net mean at zero filter -0.36 c/bu after 1.5 c/bu costs, so gross = -0.36 +
1.50 = +1.14 c/bu per trade on the 10:12:9 (or 20:24:18) spread. At 3-cent filter gross = 1.74 + 1.50 = 3.24
c/bu. Check: Mitchell's restatement "from a loss of .35 cents per bushel with no filter to +.35, 1.02, and 1.74"
(he writes .35 where the table says -0.36; a one-cent rounding difference in the second decimal, noted).

(b) Implied overnight-to-day reversal fraction. For a regression of the day change y = Close_t - Open_t on the
overnight change x = Open_t - Close_{t-1}, the slope b = rho * sd(y)/sd(x) (standard OLS identity). 1978-87:
b = -0.49 * 2.837/2.727 = -0.49 * 1.0403 = -0.510. 1987-91: b = -0.43 * 3.133/3.241 = -0.43 * 0.9667 = -0.416.
So in the pit era about 42-51% of a GPM overnight change was given back during the next day session, on average.
Check: |b| < 1 and of the same order as |rho|, since the two SDs are within 5% of each other. (Std. devs. from
Tables IA/IB, cents/bu: "Open, - Close,-1 ... 2.727", "Close, - Open, ... 2.837"; "3.241", "3.133".)

(c) What a 3-day half-life means at minutes. Assume (assumption, not from a source) that the deviation from the
5-day mean decays as an Ornstein-Uhlenbeck process, d(z) = -theta z dt, so half-life H = ln 2 / theta.
H = 3 trading days gives theta = 0.6931/3 = 0.2310 per day. If all reversion happens in the 290 day-session
minutes (08:30-13:20 = 4 h 50 min = 290 min; Zhou: "290 data points per trading day using the 1-minute data
set"), theta = 0.2310/290 = 7.97e-4 per minute. Expected fraction of a deviation closed in 60 minutes:
1 - exp(-60 * 7.97e-4) = 1 - exp(-0.0478) = 0.0467 (4.7%). A 1 c/bu deviation would close by 0.047 c/bu in an hour;
if ZM alone closed it, 0.047/0.22 = 0.21 ZM ticks, against the 1.59-tick break-even. Check: 60/290 of a day is
0.207 day; 0.207 * 0.231 = 0.0478, same exponent. Conclusion: the daily-scale reversion documented by Simon and
Mitchell is far too slow to pay at hours horizons by itself; an hours-scale ZM signal needs a fast intraday
component (Zhou's within-day cointegration) or the open-reversal component (Rechner and Poitras), not the 5-day
mean.

(d) Abdoh and Chitavi checks. Half-life formula H = ln(0.5)/ln(1 + b1): b1 = -0.0256 gives ln(0.9744) = -0.025933,
H = -0.693147/-0.025933 = 26.73 days (paper: 26.72); b1 = -0.0251 gives ln(0.9749) = -0.025420, H = 27.27 days
(paper: 27.26). Both match to rounding. Profit per trade: 0.0018 USD/lb * 600,000 lb = 1,080 USD, the paper's
first e1 figure (threshold 0), so the 406-trade panel is e1 at X = 0. Net of the 1,125 USD cost: 1,080 - 1,125 =
-45 USD at X = 0; 1,380 - 1,125 = +255 USD at X = 0.05; 2,040 - 1,125 = +915 USD at X = 0.20. e2's best, 865 USD, is
below cost (865 - 1,125 = -260 USD), as the paper says. Position check: 2 ZS = 2 * 300,000 = 600,000 lb; 3 ZM = 3 *
200,000 = 600,000 lb; 10 ZL = 10 * 60,000 = 600,000 lb. So the traded position is equal POUNDS of each leg (2:3:10),
not the board ratio 10:11:9; per-contract cost share 75 USD on a 6-day hold. In ZM terms per ZM lot: the trade's
average gross 1,080 USD over 15 lots is 72 USD per lot, i.e. 7.2 ZM-tick-equivalents per lot per trade over about
6 days, against Topstep's 5.28 USD round-trip fee plus spread per lot. These are daily-close executions.

### 4.3 Reading

- Every daily crush-rule study that has an out-of-sample or later-period look shows decay: Rechner and Poitras's
  1990-91 weakness after the 1989 GPM shift; Mitchell's negative fourth segment and his failed replication of
  Simon's 200-USD rule; Janzen and Wang's post-2020 breakdown of the leg relations (Section 2). The gross edges are
  of the size of costs (Rechner and Poitras zero filter: gross 1.14 c/bu vs costs 1.5 c/bu).
- The one positive recent claim (Abdoh and Chitavi 2025) is a daily rule with multi-day holds (about 6 days) and
  a 27-39 day half-life to the long-run equilibrium; at threshold 0 its gross (1,080 USD) is below its own cost
  (1,125 USD), and only its USDA-yield-adjusted residual clears costs. Its novelty for E.32 is the measure, not
  the horizon: market-implied meal and oil yields estimated from the day's intraday bean-on-products regression.
  Read from partial full text only.

---

## 5. Mean-reversion speed and half-life: what is published

| Horizon | Source | What is published | Status |
|---|---|---|---|
| Daily, 1985-1995 | Simon 1999 via Mitchell 2010 | "half-life of deviations of about 3 days" toward the 5-day MA | secondary (Simon not read) |
| Daily, 1984-2006 | Mitchell 2010 | average length of profitable trades "1.27 days at 220/200 to 2.63 days at 220/0"; unprofitable "2.16 days ... to 7.74 days" | read (line 205, 214) |
| Open-to-close, 1978-91 | Rechner and Poitras 1993 | corr(overnight GPM change, next day-session change) -0.49 and -0.43 | read |
| Daily rule, 10-min inputs, 1990-2021 | Abdoh and Chitavi 2025 | half-life of shocks "38.81 days" / "28.41 days" / "26.72 days" / "27.26 days"; transitory movements "lasts 10.4 days on average"; trades average "6.09" days | partial full text (Firecrawl directQuote) |
| Intraday 1-2 min, 2015 | Zhou et al. 2023 | cointegration on 74% (1-min) / 94% (2-min) of day sessions; no speed in time units | read |
| Daily, 2001-2015 (yearly fits) | Marowka et al. (JRSS-C 2020) | alpha "can be interpreted as the speed of the mean reversion of zt"; the vector varies by year (2014 "considerably higher variability") | read (no time-unit half-life found by grep) |

- No intraday half-life of the crush residual is published in any source found. Three discovery queries aimed at
  it ("crush spread" "half-life"; "crush spread" high-frequency/intraday/5-minute cointegration; intraday soybean
  complex lead-lag price discovery) surfaced only the sources above. The planner's statement "No intraday
  half-life is published" stands as VERIFIED-BY-ABSENCE (absence in what was searched, not proof).

---

## 6. Which leg adjusts

### 6.1 Facts

- Zhou et al. 2023 (intraday, 2015) [academic, read]: leadership varies with relative volumes (Section 3.1
  quotes). No fixed leader. Meal "Granger causes" more when byproduct volume is high relative to beans.
- Adrangi (J. Business & Economics Research, 2006, Clute) [academic; abstract only, clute_jber_2679_view.html; the
  full-text PDF link returns a JavaScript viewer page]: daily nearby futures; "Our VAR and bivariate GARCH model
  estimates suggest a strong bi-directional causality in Crush futures prices. We also find that while soybean
  contracts bear the burden of convergence when the spread between soybean and soy meal contract prices widens,
  this is not true of soybean and soy oil contracts." [abstract only]
- Liu and Sono 2016 (Dalian, daily) [abstract only]: "one-way information flow from the soymeal and soyoil markets
  to the soybean market".
- Avileis and Swanson (NCCC-134 2025) [academic, conference, read]: daily Bloomberg futures 2019-February 2025
  ("Daily commodity futures data for the nearby and first deferred contracts were downloaded from Bloomberg from
  2019 until February 2025", lines 345-346); 36 biofuel-policy events 2021-2025. "a 1% biofuel-induced price
  increase in soybean oil leads to a 0.19% rise in soybean prices and a 0.30% drop in soybean meal prices" and
  "meal prices serve as a price anchor when it comes to biofuels." Also "soybean oil futures returns increase
  significantly on announcement days (0.59%) and continue rising the following day (0.62%), exhibiting what we
  term Post-Announcement-Leak Drift (PALD)."
- Janzen and Wang 2025 (weekly cash) [extension]: the oil coefficient in the beans regression fell from 0.232 to
  0.070 after 2020 while meal's moved from 0.511 to 0.451 (Section 2).

### 6.2 Worked example: a biofuel shock in ZM ticks

Take ZM at 300 USD/ton (an illustrative level; the October 2021 futures price quoted in Section 1 was 312.90). A
biofuel-induced +3% ZL move implies, per Avileis and Swanson's daily causal estimate, a ZM move of 3 * (-0.30%) =
-0.90%; 0.009 * 300 = -2.70 USD/ton = -27 ZM ticks (at 0.10 USD/tick). Check: 27 ticks * 10 USD = 270 USD per ZM
lot; 300 USD/ton * 100 tons * 0.009 = 270 USD. This is a daily (close-to-close) relation, not a minutes one; it
says the sign of ZM's response to an oil-demand shock is negative, which a ZM directional model could use as a
conditioning feature on policy-event days (EPA RVO, CARB, leaks), most of which the paper dates within 2021-2025,
i.e. inside the discovery window and absent from the 2017-20 test window except for the earlier RFS cycle.

### 6.3 Reading

- Daily evidence (Adrangi; Liu and Sono for Dalian) leans toward beans adjusting to products, especially for the
  beans-meal spread; the intraday evidence (Zhou) says the adjusting leg depends on relative volume. Neither says
  ZM is the leg that closes crush residuals. The planner's test ("test early which leg adjusts: if ZM is not the
  adjusting leg, family 1 dies") is the right gate. Prior from the literature: ZM is NOT the default adjusting
  leg; it leads beans in daily data. That makes a ZM-leg reversion signal less likely than a ZM-leads signal
  (ZM moves first, ZS follows), which E.32 cannot trade on ZM itself.


---

## 7. The overnight session and the "repaired after the 08:30 open" hypothesis

(Section written after a re-spawn, 2026-10-27 00:16-00:22 PDT; sources fetched in both spawns, all in log.tsv.)

### 7.1 Facts

- Zhou et al. (NCCC-134 2022 version, supplementary Section E.1) [academic, read]: sessions "the electronic
  trading session from 7PM to 7.45AM (session 1) and the market trading session from 8.30AM to 1.20PM (session 2)"
  (zhou_nccc134_2022.pdf.txt lines 893-894). Counts of cointegrated days, ZS open-interest rollover, 1-minute
  data: session 1 "52", session 2 "180", session 1 + session 2 "52" (Tables 7, 8, 9, lines 2681-2733). Their
  explanation: "The fact that only the official trading hours are informative about the joint dynamics of
  financial assets might be explained by the absence of manufacturers outside of the official trading hours and
  the prevalence of traders during electronic sessions." (lines 2654-2657). And: "the role of traded volumes in
  the market's capacity to revert to equilibrium, and thus enforce the cointegration of asset prices, shrinks
  during electronic trading sessions" (lines 1533-1535).
- What Zhou did NOT test: every test is WITHIN a session (or on the two sessions pooled). No test asks whether a
  residual that opens up during session 1 is closed during the following session 2. The planner's "repaired
  after the 08:30 open" is therefore not addressed by Zhou in either direction.
- Rechner and Poitras (JFM 1993) [academic, read] is the closest published analogue, in the pit era (1978-91, no
  overnight electronic session; "overnight" there means close-to-open). Aggregate GPM: corr(Open_t - Close_{t-1},
  Close_t - Open_t) = -0.49 (1978-87) and -0.43 (1987-91) (Section 4). But the single legs did not reverse: meal
  -0.019 (t -0.92) in 1978-87 and -0.067 (t -2.22) in 1987-91 (Section 4.1 quotes). Their mechanism: "While the
  public is in on the close only the trading floor is in on the open." So in the only data that exist, the
  open-reversal lived in the SPREAD, not in the meal leg.
- Helms, Kaen and Rosenman (1984), via Rechner and Poitras [secondary pointer, not read]: minute-by-minute CBOT
  soybean prices on "a number of days in 1977 and 1978" showed "non-periodic cycles (persistent dependence) in
  both daily and intraday futures prices" (rechner_poitras_1993.pdf.txt lines 56-59). [unverified against the
  original]
- Session history [regulator-hosted exchange filing, read]: CBOT's 2012 self-certification to the CFTC: "Current
  electronic trading hours for these products are Sunday to Friday, 6:00 p.m. to 7:15 a.m. CT and 9:30 a.m. to
  1:15 p.m. CT", proposing "Sunday to Friday, 5:00 p.m. to 2:00 p.m. CT" effective "June 3, 2012"
  (cftc_cbot_rul051612.pdf.txt lines 29-37). By 2015 the sessions were 19:00-07:45 and 08:30-13:20 (Zhou, above).
  Whether the session times were identical across all of 2017-05..2024-02 was not verified here (no CME page may be
  fetched; the DataFacts worker owns session facts). [gap]
- Joseph and Garcia (AAEA 2016) [academic, conference paper, read]: CBOT electronic soybean futures, 15-second
  returns, "WASDE, CP, GS, AC, and PP reports from June 2010-May 2014", 30 reports released outside trading hours
  and 29 inside (joseph_garcia_aaea2016.pdf.txt lines 120-123). Abstract: "report releases during non-trading
  hours cause a large spike in volatility at the onset of trading which subsides quickly ... Return correlations
  provide little evidence to support systematic under- or overreaction in prices regardless of when the report is
  released". Body: "major market reactions persist for about 10 to 15 minutes" (line 317). Relevance: news that
  arrives while a market is shut is absorbed in the first minutes of the next session, with no measured
  continuation or reversal (outright soybeans, not the crush, not ZM).
- Ulibarri (J. Futures Markets 1998, MPRA copy) [academic, read; NYMEX crude, 1993, analogue only]: "ACCESS
  variables are informative in predicting daytime volume but not daytime prices" (ulibarri_mpra14818.pdf.txt,
  conclusions). Different market and era; listed as a weak analogue, not evidence about ZM.

### 7.2 Worked arithmetic

(a) How thin is the ZM overnight book relative to the day session? From the standard numbers (E.28 Table 1):
ZM day-session volume share 0.83, so the overnight share is 1 - 0.83 = 0.17 (assumption: the 07:45-08:30 gap is
closed, so all non-day volume is overnight). Session lengths: overnight 19:00 to 07:45 = 12 h 45 min = 765 min;
day 08:30 to 13:20 = 290 min. With ADV 36,690 contracts:
  day: 0.83 * 36,690 = 30,452.7 contracts / 290 min = 105.0 contracts per minute;
  overnight: 0.17 * 36,690 = 6,237.3 contracts / 765 min = 8.15 contracts per minute;
  ratio 105.0 / 8.15 = 12.9.
Check: (0.83/0.17) * (765/290) = 4.882 * 2.638 = 12.88. Same calculation for ZS (0.78): (0.78/0.22) * 2.638 =
3.545 * 2.638 = 9.35; ZL (0.82): (0.82/0.18) * 2.638 = 4.556 * 2.638 = 12.02. ZM is the thinnest of the three
overnight per minute relative to its own day session, consistent with Zhou's account that crush-enforcing traders
are absent overnight.

(b) Sizing the repair hypothesis with the only published magnitude (pit era, illustrative, NOT a forecast).
Rechner and Poitras 1978-87: SD of the close-to-open GPM change 2.727 c/bu and implied give-back slope b = -0.510
(Section 4.2 b). A one-SD overnight crush move would on average give back 0.510 * 2.727 = 1.391 c/bu by the day
close. If ZM alone carried the give-back: 1.391 / 0.22 = 6.32 ZM ticks, against the 1.59-tick break-even
(Section 1.4). Check: 1.391 c/bu * 4.545 ticks per c/bu = 6.32. Three reasons this does not transfer: (i) it is
1978-87 pit data; (ii) it is open-to-CLOSE, not minutes after the open; (iii) in the same data the meal leg's own
open reversal was -0.019, i.e. the reversal was not carried by meal. Under (iii) the ZM share of the give-back
could be near zero.

(c) Zhou's session counts as shares: overnight 52/243 = 21.4%; day 180/243 = 74.1%; pooled 52/243 = 21.4%
(pooling the noisy overnight data destroyed day-session detection). Check: 52 + 191 = 243; 180 + 63 = 243.

### 7.3 Test that E.33 could run (described for the lead; no decision taken here)

Quantities (all from owned schemas: ZM MBO mid, ZS and ZL MBP-1 mids):
  r(t) = 0.022 * M(t) + 0.11 * O(t) - S(t)/100, USD/bu (Section 1.2), at fixed board weights.
  D_on(d) = r(07:45 last mid of the overnight session, day d) - r(13:20 last mid, day d-1): the overnight residual
  change. Its ZM component: 0.022 * (M(07:45) - M(13:20 prior)).
  Label: ZM mid return from 08:30 + L (L = first post-open quote plus latency) to 08:30 + h, h in {15, 30, 60, 120}
  minutes, in ZM ticks, net of 1.59 ticks.
  Test: sign(-D_on) as the trade direction for ZM (ZM long when the crush is too low because meal is cheap
  relative to beans and oil), and, separately, the decomposition: does the day-session change in r come from ZM,
  ZS or ZL? If ZS or ZL closes the gap, the hypothesis is dead for a ZM-only trade (the planner's gate).
Leakage and look-ahead traps, each with a catching test:
  1. Settlement vs last mid: settlement is set in the 13:14-13:15 closing range and published after; using it as
     the 13:20 reference is fine only if it is the published value for that date. Test: recompute with the 13:20
     last mid; the signal's sign agreement should exceed 95% of days.
  2. Cross-schema timestamps: ZM MBO and ZS/ZL MBP-1 must be joined on the same clock (ts_recv or ts_event, one
     of them) with strictly backward as-of joins. Test: shift ZS/ZL by +1 s; a real signal changes little, a leak
     collapses.
  3. Opening match: the 08:30 open prints from an opening auction; a market order sent after it cannot get that
     price. Test: start labels at the first ZM quote after 08:30 plus 300-1,000 ms and compare with labels started
     at the open print; a large gap flags an untradeable edge.
  4. Daily-estimated cointegrating vectors (Zhou fits one per day using the whole day) are look-ahead inside the
     day. Test: use fixed board weights or weights fitted on prior sessions only, and assert in code that no
     weight uses data stamped after the decision time.
  5. Weekend and holiday opens: the Sunday 19:00 session carries weekend news; Mondays and post-holiday opens form
     their own stratum. Test: report results with and without them.
  6. Rolls: the three roots roll on different calendars; a v0 roll in one leg creates a fake residual jump. Test:
     drop days within the roll window of any leg and check the result is stable. (Listed months for each root
     come from the definitions schema; not verified here.)
  7. USDA release days: Joseph and Garcia show 10-15 minutes of report-driven volatility at the open on
     non-trading-hour releases (pre-2012) and Zhou finds stronger cointegration on USDA days. Test: stratify;
     exclude the first 15 minutes after any release.

### 7.4 Status of the planner's two overnight claims

- "Crush cointegration mostly breaks down overnight": VERIFIED for 2015 (52 vs 180 of 243 days).
- "Overnight ZM dislocations get repaired after the 08:30 open": UNTESTED in any source found, as the planner said.
  The only related evidence (pit era) puts the repair in the spread and NOT in the meal leg (-0.019). Prior: weak.

---

## 8. Fundamental drivers at short horizons: NOPA crush, biofuel policy, USDA reports, processing margins

### 8.1 Facts

- NOPA monthly crush report [industry association, read]: "The NOPA Crush Report contains data from 20 member
  companies that account for 99% of the US soybean crush." Contents: "Soybean crush and oils stocks for the
  current month, previous month, and comparable month a year ago", "Soybean meal: tons produced, yield, and
  exports", "Soybean oil pounds produced and yield" (nopa_monthly_crush.html). Timing: "For 2026, the report will
  be published at 12:00 noon (EST) on the dates listed" (same file); the 2025 schedule: "LSEG Release Dates (at
  Noon Eastern)", Wednesday January 15, Tuesday February 18, Monday March 17, ... Monday December 15
  (nopa_release_dates_2025.pdf.txt). Noon Eastern = 11:00 Central, inside the day session. Release times for
  2017-2024 were NOT verified from a primary page (the LSEG product page fetched in the first spawn is a generic
  shell; a search snippet says "within seconds of 11:00AM CT", [unverified: search snippet only]). E.33 needs a
  dated release calendar; that belongs to the lead or DataFacts, not here.
- No academic intraday event study of the NOPA release was found (three queries: "NOPA monthly crush report
  soybean futures price reaction announcement effect"; "NOPA crush report released 11:00 Central time 15th of
  month schedule"; the NOPA-site search). Trade press (agricensus, barchart, S&P Global) describes single-day
  reactions; pointers only, never evidence.
- Biofuel policy (Avileis and Swanson, NCCC-134 2025) [academic, read; full quotes in Section 6]: 36 events
  2021-2025 (EPA, CARB, media "leaks"), DAILY returns; ZL "+0.59%" on the announcement day and "+0.62%" the next
  (their PALD); a 1% biofuel-induced ZL rise moves ZM -0.30%. No intraday timing is reported. Trade-press reports
  of limit moves on EPA days (for example 2022-12-01) are pointers only [unverified].
- USDA reports in soybeans (Joseph and Garcia 2016) [academic, read]: reactions "persist for about 10 to 15
  minutes"; "little evidence to support systematic under- or overreaction" (Section 7.1). Zhou: "stronger
  intraday cointegration observed on average on USDA announcement days" (Section 3.1). The direction of the
  15-90 minute path after USDA releases belongs to another worker's root; not pursued here.
- Processing margins: Janzen and Wang (farmdoc daily 2025) [extension]: "Since late 2020, crush margins have
  periodically increased and become considerably more volatile" (Section 2.1). Kang and Lee (NCCC-134 2026,
  "Preliminary and incomplete") [academic, conference, read abstract in full text]: the renewable-diesel crush
  expansion changed inland spot prices but "The resilience effect appears in spot prices and convenience yields,
  but not in futures prices" (kang_lee_nccc2026.pdf.txt abstract). A basis-level effect, not a futures signal.
- Export demand (weekly export sales, flash sales): NOT researched to full text in this root. [gap, stated]

### 8.2 Worked arithmetic: can a NOPA-day ZM directional rule be tested on 39 months?

- Events: one release per month; the discovery window 2020-12-01..2024-02-29 holds 39 calendar months, so at most
  39 releases (December 2020 through February 2024, each dated on or after the 15th). Check: 2020-12 (1) + 2021
  (12) + 2022 (12) + 2023 (12) + 2024-01..02 (2) = 39.
- Position in the session: 11:00 CT is 150 minutes after 08:30 (11:00 - 08:30 = 2 h 30 min) and 140 minutes
  before 13:20 (13:20 - 11:00 = 2 h 20 min). A 240-minute label cannot fit inside the session; 60 and 120 can.
- Noise at 60 minutes (random-walk scaling assumed, stated): sigma_60 = 3.15 * sqrt(60) = 3.15 * 7.746 = 24.40
  ZM ticks. Standard error of a mean over n = 39 events: 24.40 / sqrt(39) = 24.40 / 6.245 = 3.91 ticks. To reach
  t = 2 on a true mean edge equal to the 1.59-tick break-even: n = (2 * 24.40 / 1.59)^2 = (30.69)^2 = 942 events.
  Check: 942 / 12 = 78.5 years of monthly releases. Conclusion: a NOPA-day directional rule is not testable on the
  owned data; at best NOPA days are a stratum or an exclusion window. The same arithmetic applies to the 36
  biofuel events of Avileis and Swanson (fewer of them fall inside 2020-12..2024-02).
- Event-day volatility will be higher than sigma_1m on normal days (Joseph and Garcia's report-day volatility
  peaks), which makes n larger still; the 942 is a lower bound under the stated assumption.

### 8.3 Reading

The fundamental drivers named in the topic list either arrive monthly (NOPA, about 39 events), irregularly (biofuel
policy, tens of events over five years), or are measured at daily or weekly horizons. None gives a sample large
enough for a minutes-scale directional rule on its own. They are useful as STRATA (days on which the crush
relation is stressed or reinforced), as EXCLUSION windows (the first 10-15 minutes after a release), and, for
biofuel events, as a sign prior (an oil-demand shock lowers ZM).

---

## 9. What this means for a ZM directional search

Mechanisms worth testing (in order of prior strength, all weak):
1. Day-session crush residual -> ZM, conditioned on relative volume. Zhou: day-session residuals are mostly
   stationary at 1-2 minute sampling (74-94% of 2015 days), and the speed of adjustment depends on relative
   volumes. The first gate is the planner's: does ZM, rather than ZS or ZL, close the residual? The literature's
   prior is that ZM is NOT the default adjusting leg (Adrangi daily; Zhou volume-dependent; Rechner and Poitras
   meal leg -0.019). Published reversion speeds are all daily (half-life about 3 days via Mitchell's summary of
   Simon; 27-39 days in Abdoh and Chitavi), which at hours horizons close only about 5% of a deviation per hour
   (Section 4.2 c); a payable signal needs a fast intraday component that no paper measures.
2. Overnight-to-open repair (Section 7.3). Untested anywhere; the pit-era analogue puts the reversal in the
   spread, not the meal leg. Cheap to test once family 1's data are built (same residual, one decision per day,
   about 800 trading days in 39 months).
3. Biofuel event days as a conditioning flag (negative ZM response to oil shocks, Avileis and Swanson), not as a
   standalone rule.

Mechanisms to drop or demote:
- Daily crush rules toward a 5-day mean (Simon) or long-run equilibrium (Mitchell, Abdoh and Chitavi): too slow
  for minutes-to-hours, decayed out of sample (Mitchell's failed replication of Simon), and gross edges of the size
  of costs (Rechner and Poitras zero filter: gross 1.14 c/bu against 1.5 c/bu costs).
- NOPA-day or biofuel-day directional event rules: about 39 events against about 942 needed (Section 8.2).
- Per-day cointegrating vectors (Zhou's daily fits): SD 0.28 around a median of -0.19 for ZM, and look-ahead
  within the day. Use fixed board weights or prior-session rolling weights.
- Fixed betas fitted on 2020-24 and applied to 2017-20: the weekly oil coefficient fell from 0.232 to 0.070 at the
  regime change (Janzen and Wang). Thresholds should be in units of a causal rolling residual SD, not fixed cents.

Regime: the discovery window lies wholly inside the renewable-diesel regime (oil share mostly above 35%, weekly
co-movement R2 0.32); the sealed test window lies wholly before it (oil share 25-35%, R2 about 0.79), apart from
its last weeks. Any crush-based ZM signal selected on discovery data meets a different crush in the test window.
No source measures this break at intraday horizons. [gap]

---

## 10. Planner pointers I own: verification table

| # | Planner claim | Status | Evidence (file) |
|---|---|---|---|
| 1 | ZM tick 10 USD, ZS 12.50, ZL 6 | VERIFIED (owned-data definitions table via E.28; not from a CME page, stage rule) | A0_contract_stats.md lines 114-117 |
| 2 | Board crush = 0.022 x meal (USD/ton) + 0.11 x oil (c/lb) - beans (USD/bu) | VERIFIED as arithmetic of 44 lb meal and 11 lb oil per 60 lb bushel; CME's yields quoted second-hand by farmdoc; Marowka quote "yt(1) - 11yt(2) - 2.2yt(3)" in cents | farmdoc_fdd101325_oilshare.pdf.txt; marowka_spiral_b.pdf.txt lines 67-68 |
| 3 | Ratio 10 ZS : 11 ZM : 9 ZL; Rechner and Poitras used 10:12:9 | VERIFIED | poitras_soycrush_wpd.pdf.txt; rechner_poitras_1993.pdf.txt lines 105-116 |
| 4 | One ZM tick = 0.22 c/bu of crush; 1 c/bu = about 4.5 ZM ticks | VERIFIED (arithmetic: 0.022 x 0.10 USD = 0.0022 USD/bu = 0.22 c/bu; 1/0.22 = 4.545) | Section 1.2 |
| 5 | Zhou et al.: 180 of 243 day sessions cointegrated (229 at 2-min) | VERIFIED | zhou_jcm2023_wur.pdf.txt; zhou_nccc134_2022.pdf.txt line 2756, Table 8 |
| 6 | Overnight session cointegrated on only 52 | VERIFIED (ZS open-interest rollover; 53/49/33 under other rollovers) | zhou_nccc134_2022.pdf.txt Table 7 |
| 7 | Median vector ZL -0.11, ZM -0.19 vs physical -0.11, -0.22; daily SD 0.28 | VERIFIED (SD 0.28 for both legs); price units of the vector not stated by the paper, see Section 3.2 caveat | zhou_jcm2023_wur.pdf.txt Table 4 |
| 8 | Leadership depends on relative volume; no fixed leader | VERIFIED | zhou_jcm2023_wur.pdf.txt lines 814-820 |
| 9 | No half-life or information-share levels reported (Zhou) | VERIFIED (grep for "half" finds none; kappa reported only as ratios regressed on volume ratios) | both Zhou files |
| 10 | Simon (JFM 1999): crush rules profitable 1985-1995 | PARTLY VERIFIED: abstract only ("January 1985 through February 1995", "would have been profitable"); full text not obtained; the 3-day half-life is Mitchell's summary | simon1999_ideas.html; mitchell_jrfm2010_firecrawl.md |
| 11 | Mitchell (JRFM 2010): unstable | VERIFIED (negative later segment; Simon replication loses 20 USD per trade) | mitchell_jrfm2010_firecrawl.md |
| 12 | Abdoh and Chitavi (IREF 2025): deviations of meal and oil from USDA crushing yields explain transitory crush moves; three-leg daily rules profitable after costs | PARTLY VERIFIED: partial full text (Firecrawl directQuote). Profitable after costs only under cost assumption e1 and thresholds above 0; under e2 "trading is not profitable"; at threshold 0 gross 1,080 USD < 1,125 USD cost; signal uses 10-minute intraday prices but the rule is daily with about 6-day holds | abdoh_chitavi_firecrawl_directquote.txt; abdoh_chitavi_ideas.html |
| 13 | Rechner and Poitras (1993) | VERIFIED (10:12:9; open-to-close rule; costs 1.5 c/bu; opening-reversal correlations -0.49/-0.43; decay after 1989) | rechner_poitras_1993.pdf.txt |
| 14 | "No intraday half-life is published" | VERIFIED BY ABSENCE (not found in any source read or in the targeted queries of both spawns (3 in the first, 2 in this one); absence, not proof) | Section 5, Section 11 |
| 15 | "Crush cointegration mostly breaks down overnight" | VERIFIED for 2015 only | Section 7.1 |
| 16 | Overnight ZM dislocations repaired after the 08:30 open (hypothesis) | UNVERIFIED (untested anywhere; pit-era analogue shows the reversal in the spread, meal leg -0.019) | rechner_poitras_1993.pdf.txt; Section 7 |
| 17 | Expected regime break between discovery (RD oil share) and test (2017-20, trade war and Covid) | PARTLY VERIFIED: the oil-share and co-movement break is verified at weekly cash horizons (Janzen and Wang); the trade-war and Covid parts are not covered by any source read here; no intraday evidence | farmdoc_fdd101325_oilshare.pdf.txt; farmdoc_fdd091025_extraction.pdf.txt |

---

## 11. Search log, stopping rule and non-survivors

Stopping rule (brief rule 6) by topic:
- Contract arithmetic and ratios: 4 full texts (Rechner and Poitras; Poitras note; farmdoc x2; Smith). Stopped.
- Daily and intraday cointegration: full texts Zhou (two versions), Marowka et al., Mitchell, Rechner and Poitras;
  last three queries (this spawn: "crush spread" high-frequency intraday cointegration 2020-2023; soybean crush
  overnight/day-session price discovery; overnight-vs-intraday returns in grain futures) surfaced nothing new
  except a hedging thesis (below). Stopped.
- Crush trading-rule profitability and decay: full texts Rechner and Poitras, Mitchell, Abdoh and Chitavi
  (partial); Johnson et al. 1991 and Simon 1999 not obtainable as text (scanned precursor; paywall). Stopped.
- Half-life at any horizon: covered by the above; no intraday figure exists in what was searched. Stopped.
- Regime change: farmdoc x2 (Janzen and Wang; extraction rates), Smith 2021, Kang and Lee 2026; last query
  (oil share / structural break / meal price discovery) found only Kang and Lee (spot, not futures). Stopped.
- Which leg adjusts: Zhou, Avileis and Swanson (full); Adrangi and Liu-Sono (abstract only). Stopped.
- Fundamental drivers at short horizons: NOPA pages, Joseph and Garcia, Avileis and Swanson; three NOPA queries
  found no academic intraday study. Stopped. Export sales not researched (gap).

Non-survivors and items read but not used as evidence:
- Emery and Liu (JFM 2002) [academic, abstract only, emery_liu2002_ideas.html]: electricity vs natural gas, daily
  settlements; "statistically significant mean reversion ... also is economically significant in both in-sample
  and out-of-sample tests." An energy analogue of a cointegrated-spread rule at DAILY horizon; no bearing on ZM
  minutes.
- Kanamura, Rachev and Fabozzi (KIT WP 27, 2011) [academic, read title page]: spread-trading profit model for
  energy futures; not soybean. Not used.
- Wu (Illinois MS thesis 2022, ideals_126677_intraday_hedging.html) [academic, abstract read]: intraday data
  improve minimum-variance HEDGING in the soybean crush complex ("there is at least one intraday data-based hedging
  strategy that outperforms the Naive in the soybean crush complex"); covariance forecasting, not direction.
- Ulibarri (1998): NYMEX crude, after-hours session; analogue only (Section 7.1).
- Gu and Lei (Atlantis 2018), atlantis_25886066: Dalian crush stat-arb, low-tier venue; not used.
- shs_gap_soyoil.html: a captcha page (no content); lseg_nopa.html/.txt: a generic product shell with no release
  facts; clute_jber_2679.pdf and adrangi_jber2006.pdf: both are HTML viewer pages, not the PDF (so Adrangi stays
  abstract only); johnson_etal_nccc1990.pdf: a scanned image with no text layer (no OCR tool on the machine).

Budget: WebSearch calls in this spawn: 10 (00:16-00:22 PDT). The first spawn's count was not logged; its
log.tsv shows 36 fetches between 23:03 and 23:15 PDT. Total stays well under the 80-call cap on any reading.
No "budget used up" notice was received. Firecrawl was used twice in the first spawn (mdpi.com, which blocks curl
and whose terms could not be read, so no Scrapling; ScienceDirect, whose page declares a TDM reservation).
Scrapling was not used in either spawn.

Status: all sections 1-11 written. Finished 2026-10-27 00:23 PDT.
