# M2. F09 into ZL: soy-complex (and energy) lead-lag and relative value with ZL as the traded leg

Stage E.34, ZL methods addendum, part M2. Worker MathReaderM2-OpusHigh, 2026-10-29 (started 12:10 PDT).
No market data was opened, no price, return, feature or model output was computed, nothing was trained, N stays 838.
Every number below is either quoted (with its source) or hand arithmetic on the shared ZL facts in BRIEFS.md
`## RULES`; the arithmetic is reproduced by work/MathReaderM2-OpusHigh/scripts/m2_examples.py, which writes
work/MathReaderM2-OpusHigh/m2_examples.json (sha256 prefix a426a5eab43aedde). Values from that JSON are named by key.

Files:
- Pages fetched in this stage, with the log: reports/stage_e34_briefs/work/MathReaderM2-OpusHigh/pages/ (log.tsv).
- Reused verified quotes: the E.32 methods brief (reports/stage_e32_methods_brief.md), cited as "E.32 brief
  <section>:<line>", and two E.32 saved pages read by grep for passages the brief did not quote
  (reports/stage_e32_briefs/pages/R3a_crush/zhou_jcm2023_wur.pdf.txt and rechner_poitras_1993.pdf.txt).

Conventions (as E.32 M2 and the E.32 protocol 0.3):
- Prices: S = ZS in cents/bu, O = ZL in cents/lb, M = ZM in USD/short ton; nS, nL, nM = the same prices in ticks
  (0.25 c/bu, 0.01 c/lb, 0.10 USD/ton). ZL tick = USD 6.00.
- Board crush in cents/bu: C = 11 O + 2.2 M - S = 0.11 nL + 0.22 nM - 0.25 nS (E.32 brief M2 c, 4718-4728; E.32
  protocol F1, line 413). One ZL tick moves C by 0.11 c/bu, so a 1 c/bu crush dislocation closed by ZL alone is
  1/0.11 = 9.09 ZL ticks (1/11 c/lb) = USD 54.55 a ZL contract (m2_examples.json zl_ticks_per_cent_crush).
- Cost: Topstep ZL round trip c_f = 2.38 ticks (E.32b holding scope 15). sigma_h (ticks): h1 5.52, h5 12.05, h15
  20.37, h30 28.10, h60 38.21 (E.32b holding scope 15). Band B = 15, 30, 60 minutes.
- [derived] marks my algebra; [unverified] a claim without fetched full text; [u] an assumption.

## Bottom line (for the lead)

1. (a) Crush residual, ZL adjusting. The mechanism is the same residual E.33 used (F1), read for the ZL leg. The
   expected gross per trade is G = s_L x D x (1 - 2^-m) / 0.11 ZL ticks (s_L = ZL's share of the closure, D the
   dislocation in c/bu, m the hold in half-lives). Break-even share s_L* = 2.38 x 0.11 / (D (1 - 2^-m)): 0.52 at
   D = 1 c, m = 1; 0.35 at m = 2; 0.26 even with full reversion. ZL is cheaper per crush cent than ZM was (ZM needed
   0.70 at D = 1, m = 1), but its noise is larger, so cost per sigma is about the same (ZL 0.085, ZM 0.092). The
   published evidence gives no s_L, no intraday half-life, and the one intraday source says leadership moves with
   relative volume. Verdict: USE, as the crush set of F09, with ZL-specific normalisation (a ZL-dependent regression
   residual) and an origin split (did ZL move, or did the others?).
2. (b) ZS and ZM leading ZL. Minute look-backs (1, 5, 15, 30) are allowed; seconds are not (E.32 M2 b). The useful
   form is one "implied-oil gap" (how far ZL lags what the ZS and ZM moves imply through the crush), plus each
   leader's own scaled return. Bars suffice for the leaders at minute look-backs; the leaders' books would make the
   test-window read a new purchase (ZS and ZM book data for 2017-05..2020-11 are not owned; only their ohlcv-1m bars
   are, inside the sealed files). Verdict: USE, bars only for ZS and ZM.
3. (c) CL, HO, RB. HO and RB are not owned for either window (only 2025-04..2026-06, closed): EXCLUDE. RINs have no
   owned or free intraday series: EXCLUDE. CL bars are owned for both windows, but E.12 and E.20 already used CL's
   60-minute return as a lead on ZL (R1-11, R1-15; no pass), and the test window's 2019-05..2020-11 ZL bars were read
   in those trials. The literature found links energy to vegetable oil weekly or daily, through biodiesel pricing,
   with no intraday evidence. Verdict: EXCLUDE CL from F09's registered sets. Fallback if the lead wants it: one
   disclosed context feature (CL scaled return at k = 15), never a set of its own.
4. (d) Which leg adjusts. Use the VECM loadings alpha on (ZS c, ZL ticks, ZM ticks), the adjustment share s_L, the
   weak-exogeneity restriction alpha_L = 0, the bivariate device (oil value against implied oil value) for IS, CS
   and ILS, and the OU half-life hl = -ln 2 / ln phi with phi = 1 + beta'alpha. They must not select anything. Two
   uses are clean: (i) causal features (prior-date estimates of s_L and hl inside each training fold), and (ii) a
   report-only diagnostic computed for every set after the search, whether or not anything passes. (E.33 made the
   VECM a Tier-A-only P6.5 diagnostic, so the program never measured which leg adjusts.) Literature: intraday (Zhou
   et al., 2015 data) both ZS and ZM Granger-cause ZL more as ZL's relative volume rises; daily evidence has beans
   adjusting (Adrangi; Liu and Sono, abstracts) and, in the renewable-diesel regime, biofuel shocks starting in ZL
   (Avileis and Swanson, daily). So ZL is a plausible follower to bean and meal shocks and the origin of biofuel
   shocks.
5. (e) E.33's ZM negative constrains the ZL prior two ways that pull apart. The shares sum to 1, so evidence that
   ZM does not close the residual moves share toward ZS and ZL. But E.33 also failed in a way consistent with a
   common cause: no tradable minutes-scale reversion or propagation in the complex net of costs, at a cost per sigma
   (0.092) that ZL barely improves on (0.085). Net reading: E.33 rules out "ZM adjusts strongly" but not "ZL
   adjusts"; it is weak, mildly negative evidence for F09 on ZL. E.32b's about 2.5% for F09 is not contradicted.
   The prior number is the lead's decision.
6. (f) Protocol inputs. A 17-feature F09 list (crush 8, propagation 9) and a V28 rule variant (4 rules x 3 holds
   = 12). My judgment: F09 built only from bars is not an order-book strategy, so under a literal V43 it must be
   rules (V28). The ML form is admissible only if the lead rules, as E.33's precedent allows, that sets traded and
   labelled on ZL's own book inside the order-book program count as order-book strategies. That ruling is reserved
   for the lead.

## (a) The crush residual with ZL as the adjusting leg

**1. Core idea.**
- E.33 asked whether ZM closes crush dislocations. Here the same relation is read for ZL: when C = 11 O + 2.2 M - S
  is far from its causal mean, does ZL move to close it within 15-60 minutes, and by enough to pay 2.38 ticks?
- Two things change against E.33's F1. First, the residual's normalisation: an Engle-Granger (OLS) residual depends
  on which leg is the dependent variable, so F1.3 (ZM on ZS and ZL) has to be re-fitted with ZL as the dependent
  variable. Second, the dislocation's origin. In the discovery regime the oil leg carries its own biofuel shocks
  (section (d)). A dislocation that ZL itself opened is a margin change ZL caused, not a ZL lag, and fading it fades
  news. So the crush set needs a feature that says which leg opened the gap.

**2. Equations.**
- Crush level and its z-scores are leg-agnostic, so E.32 protocol F1.1, F1.2 and F1.4 (lines 418-421) carry over
  unchanged: zC_k(t) = (C(t) - mean_k)/sd_k over the minute marks t - j, j = 1..k, inside the segment. The sign is
  the one difference: zC > 0 (crush wide: oil plus meal rich against beans) means sell ZL when ZL is the closer.
- ZL-dependent residual (the F1.3 mirror) [derived from protocol line 420 by swapping the roles of ZM and ZL]:
  before D's open, OLS on the clean 1-minute samples 08:35-13:13 of the 10 trade dates before D in the current
  segment (at least 3, or invalid):
      O = a + b_S S + b_M M + eps   (natural units: c/lb on c/bu and USD/ton; centred fit, a from the means)
      e_L(t) = (O(t) - a - b_S S(t) - b_M M(t)) / 0.01   [ZL ticks],   zRL(t) = e_L(t) / sd_e.
  e_L > 0 means ZL is rich against beans and meal: sell ZL.
- Physical hedge ratios, against which the rolling b_S and b_M are read [derived]: from C = const, O = (S - 2.2 M +
  C)/11, so b_S = 1/11 = 0.0909 c/lb per c/bu and b_M = -2.2/11 = -0.200 c/lb per USD/ton. In ticks, a 1-tick ZS
  move implies 0.25/0.11 = 2.273 ZL ticks; a 1-tick ZM move implies -0.22/0.11 = -2.000 ZL ticks
  (m2_examples.json zl_ticks_per_zs_tick, zl_ticks_per_zm_tick). Per ZL contract (60,000 lb of oil = 60,000/11 =
  5,454.5 bu), the crush-neutral position is 5,454.5/5,000 = 1.091 ZS and 5,454.5 x 0.022 = 120.0 tons = 1.200 ZM:
  the board's 9 ZL : 10 ZS : 11 ZM scaled to one ZL lot (9 x 1.091 = 9.82, about 10; 9 x 1.2 = 10.8, about 11). The
  traded position is ZL alone; the ratios only define the residual.
- Why rolling, never fixed physical weights: Janzen and Wang's weekly cash regression of soybean on meal and oil
  changes moved from 0.511 dSBM + 0.232 dSO (2007-2020) to 0.451 dSBM + 0.070 dSO (Oct 2020-Sep 2025), "a
  previously stable relationship among soybean crush components has broken down" (E.32 brief R3a 2.1, 1497-1501; the quote at 1500).
  The oil coefficient is the one that collapsed, so a ZL-dependent residual with fixed weights would be most wrong
  exactly in the leg traded here. The E.32 protocol's rule stands: levels are "normalised by causal rolling
  statistics, never fixed cents" (protocol F1, line 194).
- Origin split [new, derived]: over the last k = 30 minutes the crush change splits into leg contributions
  dC_30 = 11 dO_30 + 2.2 dM_30 - dS_30. ZL's signed share of the absolute contributions:
      oL30 = 11 dO_30 / (|11 dO_30| + |2.2 dM_30| + |dS_30|),   in [-1, 1]; invalid when the denominator is 0.
  |oL30| near 1: ZL opened the dislocation (biofuel-type shock; do not fade). |oL30| near 0: beans or meal opened it
  (ZL lags; the catch-up case of section (b)).
- Trade arithmetic (E.32 M2 f, 5093-5121, rewritten for ZL) [derived]: with ZL's adjustment share s_L (section d), a
  dislocation D = |C - m| c/bu and a hold of m half-lives (m = h / hl),
      expected gross G = s_L x D x (1 - 2^-m) / 0.11 ZL ticks;   break-even share s_L* = 2.38 x 0.11 / (D (1 - 2^-m)).
  Including the test's minimum detectable edge (K2: stop if the best discovery net edge is below e80_test, 1.81
  ticks at h 30), a configuration needs G >= 2.38 + 1.81 = 4.19 ticks at h 30 (E.32b recs 4.5(a), "c_f +
  e80_test 4.19"), i.e. s_L x D x (1 - 2^-m) >= 4.19 x 0.11 = 0.461 c/bu.

**3. Worked ZL example** (illustrative prices, not data).
- Prices: ZS 1,300.00 c/bu, ZL 60.00 c/lb, ZM 380.0 USD/ton: C = 660 + 836 - 1,300 = 196 c/bu.
- ZS rises 4 ticks (1.00 c/bu) in 10 minutes; ZL and ZM do not move. C falls 1.00 c/bu; oL30 = 0 (beans opened it).
  If ZL alone closes it (s_L = 1), ZL rises 1/0.11 = 9.09 ticks = USD 54.55 a contract.
- Against sigma_30 = 28.10 ticks, the full 9.09-tick closure is 0.32 sigma: a 1 c/bu dislocation is small relative
  to ZL's own 30-minute noise. In crush units ZL's 30-minute sigma is 28.10 x 0.11 = 3.09 c/bu.
- Break-even share s_L* (m2_examples.json breakeven_sL; rows D in c/bu, columns m = 1 / 2 / 3 / full reversion):

| D | m = 1 | m = 2 | m = 3 | full |
|---|---|---|---|---|
| 0.5 | 1.047 (impossible) | 0.698 | 0.598 | 0.524 |
| 1 | 0.524 | 0.349 | 0.299 | 0.262 |
| 2 | 0.262 | 0.175 | 0.150 | 0.131 |
| 3 | 0.175 | 0.116 | 0.100 | 0.087 |

  Check of one cell: 2.38 x 0.11 / (1 x 0.5) = 0.2618 / 0.5 = 0.5236. Gross at s_L = 1, D = 1: 4.545 / 6.818 /
  7.955 ticks at m = 1 / 2 / 3 (gross_sL1_D1).
- Against ZM (E.32 M2 f table, 5134-5135): at D = 1, m = 1 ZM needed 0.70, ZL needs 0.52. One crush cent is 9.09 ZL
  ticks against 4.55 ZM ticks, and the cost in ticks is 2.38 against 1.59: 2.38/9.09 = 0.262 c against 1.59/4.545 =
  0.350 c. ZL is about 25% cheaper per crush cent closed.
- Hold against half-life (halflife_vs_hold; D = 1 c): hl 10 min gives s_L* 0.405 / 0.299 / 0.266 at h 15 / 30 / 60;
  hl 20 min 0.646 / 0.405 / 0.299; hl 30 min 0.894 / 0.524 / 0.349; hl 60 min 1.646 / 0.894 / 0.524. A half-life
  near or above the hold makes every D near 1 c unpayable.
- With the K2 edge included (G >= 4.19 at h 30), the D needed is 0.461 / (s_L (1 - 2^-m)): s_L = 1: 0.92 / 0.61 /
  0.53 c at m = 1 / 2 / 3; s_L = 0.5: 1.84 / 1.23 / 1.05 c; s_L = 0.25: 3.69 / 2.46 / 2.11 c.
- With the hypothetical VECM of section (d) (s_L = 0.142, hl 17.6 min), ZL's full eventual move per cent of
  dislocation is 1.29 ticks, below 2.38 even with full reversion. The family is alive only if s_L is well above
  that illustration.
- Spread sensitivity: c_f assumes a 1.0-tick ZL spread [u]. The only published ZL figure is a search snippet, "US
  hours 2.06 ticks" for Q1-Q3 2022 (F2_grains.md line 54, GRAINS-35, unverified). At S = 2.06, c_f = 2.06 + 0.5 +
  0.88 = 3.44 and s_L* at D = 1, m = 1 rises to 0.757 (cf_spread206). DataFacts or the run stage should measure the
  ZL day-session spread on discovery MBP-1 before freezing c_f; that is a count-type fact, not an outcome.

**4. Data.**
- 1-minute prices of ZS, ZM and ZL in the day session (08:30-13:20 CT), on one clock. For ZL, the BBO mid from its
  own book where the program buys or owns it (MBP-1 owned for discovery; F10's book purchase covers the test). For
  ZS and ZM, ohlcv-1m closes in both windows (section (b) for why bars). Bar volumes for the volume-share features.
- Front-month map and segments as E.32 protocol G2 (lines 372-376): ZS has no October or December contract, so
  autumn segments mix months [DataFacts confirms months from the definitions]. ohlcv-1m v.0 bars roll on
  Databento's continuous rule; segment breaks must come from the definitions or the bars' instrument_id.
- Executable prices: ZL ask/bid at decision + 1 s (E.33 P3.2) if the ZL book is used; with bars only, the next bar's
  open plus the full c_f.

**5. Leakage and look-ahead traps** (E.32 M2 c (i)-(v), 4797-4815, all apply; ZL-specific additions):
- (i) Normalisation leak: an OLS residual fitted on the same day it is used is look-ahead (Zhou's per-day smoother
  is description only, E.32 brief M2 bottom line 4, 4459-4461). Test: future-scramble invariance; the
  coefficients for D equal those from a run truncated at D's open.
- (ii) Bounce and staleness in the leg that is also the label. If C(t) uses ZL's last trade and the label starts
  at ZL's next price, bid-ask bounce in ZL makes a spurious "reversion" that the label confirms. Use ZL's BBO mid in
  C when the book exists (MathReview A-3, E.32 brief 4788); with bars, require each leg's last trade within a frozen
  staleness limit (for example 2 minutes) and test with a +1-bar shift of the feature (the edge must not jump).
- (iii) Stale leaders. A minute without a ZS or ZM trade has no bar (ohlcv bars come from trades); forward-filling a
  stale close makes a dislocation that "closes" when the leg next trades. Test: count entries whose leaders' last
  trade is older than the limit; it must be 0.
- (iv) Origin features use dO_30, which overlaps the label only if the label start is inside the 30-minute window;
  it is not (labels start at t + L). Test: oL30 at t is unchanged when all data after t is scrambled.
- (v) Regime: biofuel-policy days (EPA RVO and SRE announcements, mostly unscheduled) give ZL-origin dislocations
  that persist (section (d)). Not a leak; an exclusion by date list would be one, because the dates are known only
  afterwards. Any filter must be causal (for example a 20-date realised-volatility state), or the days stay in.

**6. Compute.** As E.32 M2 c and f (4817-4822, 5180-5183): about 2.6 million rows over the windows, rolling OLS per
date in milliseconds, RAM under 1 GB.

**7. Verdict: USE** as F09's crush set on ZL, with three frozen choices: the ZL-dependent rolling residual zRL (10
dates, in segment), the origin share oL30 and its interaction with zC30, and ZL's volume share. Drop F1.7/F1.8 (the
overnight crush gap): its once-a-day form is K6-crushgap-01 (R1-08), null on 2019-05..2024-02 in E.22, and the test
window's 2019-05..2020-11 bars were read for it (seal section 4). It adds exposure and little that is new.

## (b) ZS and ZM leading ZL at minute look-backs

**1. Core idea.**
- News about bean demand (exports, crush pace, weather) reaches ZS first, the most liquid leg (median v_0 ADV
  77,862 against ZM's 36,690; E.32 protocol F2, line 200). Meal news reaches ZM. The question is whether ZL prices
  the implied change in oil value with a delay of minutes. A delay could come from slower spread and processor flow,
  as the E.32b dossier frames it ("through crush margins that a slower participant set prices with a delay", E.32b
  recs 4.5, 540).
- Seconds are out of reach: in E.32 M2 (b), a pure-shift lead of 1-2 s leaves 0.20-0.53 ticks of predictable move
  after 0.3 s latency on ZM, and "a naive strategy based on market orders cannot make any profit of this effect"
  (Huth and Abergel, E.32 brief 4693). De Boer et al. put soybean-complex liquidity spillovers "mainly within 30 s"
  (F2_grains.md line 80, GRAINS-24, abstract). F09 therefore tests whether a minutes-scale residue exists, at
  look-backs of 5-30 minutes and holds of 15-60.
- The leaders matter only through what they imply for oil. With meal fixed, a bean move implies an oil move of the
  same sign. With beans fixed, a meal move implies an oil move of the opposite sign (oil plus meal value must match
  beans). That is why one implied-oil gap, not separate ZS and ZM returns, is the primary propagation feature.

**2. Equations.**
- Scaled leader returns (E.32 protocol F2.1-F2.6, lines 430-431, with the roles of the legs swapped):
  rX_k(t) = (P_X(t) - P_X(t - k min)) / (tick_X x sigma_X(D) x sqrt(k)), X in {ZS, ZM}, k in {5, 15, 30}; sigma_X(D)
  as protocol 0.3 (lines 60-62: the SD of 1-minute changes over 08:35-13:13 of the 20 prior dates, chained across
  rolls).
- Implied-oil gap with physical weights (the F2.7 mirror) [derived]:
      g_k = [ (dS_k - 2.2 dM_k)/11 - dO_k ] / 0.01 / (sigma_ZL(D) sqrt(k))   (natural units for dS, dM, dO)
  Identity: (dS - 2.2 dM)/11 - dO = -(11 dO + 2.2 dM - dS)/11 = -dC_k/11 c/lb, so g_k = -dC_k / (0.11 sigma_ZL(D)
  sqrt(k)): the k-minute crush change in ZL ticks, sign reversed. g_k > 0: ZL rose less than beans and meal imply;
  buy ZL.
- Regression-weight gap (preferred; uses the zRL fit of (a)): gR_k = [ b_S dS_k + b_M dM_k - dO_k ] / 0.01 /
  (sigma_ZL(D) sqrt(k)), with b_S, b_M frozen for D. The physical weights treat every bean move as an oil move. The
  weekly evidence says that since late 2020 beans move with oil far less (oil coefficient 0.070; E.32 brief 1499).
  So g_k mostly measures crush-margin changes that need not reverse, and gR_k uses the empirical co-movement instead.

**3. Worked example** (m2_examples.json b_example).
- ZS +4 ticks (1.00 c/bu) over 15 minutes; ZM and ZL unchanged. Physical gap: 1/0.11 = 9.09 ZL ticks; g_15 = 9.09 /
  20.37 = 0.446 (sigma_15 20.37 measured, not sqrt-scaled).
- If ZL closes a fraction f of the gap within a 30-minute hold, the gross is 9.09 f; break-even f = 2.38/9.09 =
  0.262. At f = 0.5: gross 4.545, net 2.165 ticks, per-trade Sharpe 2.165/28.10 = 0.0771, and (3/0.0771)^2 = 1,516
  trades for t = 3 before any deflation. That is about 1.9 trades a date over 796 OOF dates, under the 9-a-day cap.
- How big are bean moves in oil terms? ZS's 15-minute sigma under random-walk scaling is 3.11 x sqrt(15) = 12.05 ZS
  ticks = 3.01 c/bu. With meal fixed it implies 27.4 ZL ticks, 1.34 times ZL's own 15-minute sigma
  (zs_1sigma15_implied_over_zl_sigma15). ZL cannot be following the physical identity tick for tick, or its sigma
  would be larger. Most bean moves are absorbed by the margin and by meal. The physical gap is therefore large and
  mostly not a ZL lag, which is the case for gR_k.
- Bounce in bar closes (half a tick per leg, in ZL ticks: ZS 1.136, ZM 1.000, ZL 0.5; combined SD 1.594 ticks,
  bounce_gap_sd_ticks): 13% of sigma_5, 8% of sigma_15, 6% of sigma_30. Bars are adequate at k >= 5; at k = 1 bounce
  is 29% of sigma_1 (1.594/5.52), so k = 1 is dropped.

**4. Data: bars or books.**
- Bars suffice for the leaders. At look-backs of 5-30 minutes the close of an ohlcv-1m bar is a trade price within
  the minute; staleness and bounce are second-order (above) and can be bounded by a staleness rule. The leaders'
  books would add order-flow features (E.32 protocol F2.8-F2.11, ZS and ZL OFI). The only positive forward
  order-flow finding in E.32's sources is cross-asset and lagged (E.32 protocol F2, line 204), but it decays within
  about 30 minutes, and its fast part is what HFT takes.
- Test-window consequence (the decisive point): ZS, ZM and ZL ohlcv-1m for 2017-05..2020-11 are owned inside the
  sealed soy files (E.32b recs 4.5(c), the "test, F09" row, line 644). No ZS or ZM book data for the window was ever
  bought ("No order-book data (MBO, MBP, trades) for the window was ever bought or read", seal section 4,
  reports/stage_e32_test_seal.md 117-119). A frozen model whose leaders use ZS MBP-1 or ZM MBO features would make
  the one test read require buying ZS and ZM book data for 2017-05..2020-11 as well as ZL's. That purchase is not
  priced (E.32b priced only ZL: MBO USD 21.48, MBP-1 USD 23.36) and would need a logged quote and the user's
  approval. Bars-only leaders keep the F09 test inputs at USD 0.
- ZL's own price: its BBO mid from the book when the program has the ZL book (F10); otherwise ZL bars, with the
  entry at the next bar's open plus the full c_f.
- Bar timing [DataFacts to confirm]: Databento ohlcv-1m records are stamped with the bar's open time (ts_event at the
  start of the interval), so the bar stamped u is complete only at u + 60 s. [unverified here: from vendor-format
  knowledge, not a fetched page]

**5. Leakage and look-ahead traps.**
- (i) Bar-open stamps: using the bar stamped t at decision time t is a 1-minute look-ahead. Rule: at decision t,
  the latest usable bar is the one stamped t - 1 min (closing at t). Test: shift every leader bar by +1 minute;
  features at t must change only if they used the bar stamped t.
- (ii) Mixed clocks: the ZL book on ts_recv, bars on ts_event. At minute look-backs the gap is milliseconds (E.33
  measured the largest ZM/ZS/ZL median ts_recv - ts_event gap at 0.252 ms; E.33_RETURN.md line 150), so the rule in (i)
  dominates.
- (iii) Contemporaneous news: a USDA report moves all three legs within the same minute. A gap measured while the
  legs are still repricing is not a lead. Keep E.33's release exclusion (P3.6 rule 3: marks within [R - 2, R + 30]
  minutes of a release are not used; feat33.py 829-830) and add no new event list after the fact.
- (iv) Roll steps: a front change in one leg makes a k-minute "return" across a roll. Returns are invalid when the
  window crosses any leg's front change (protocol G2).
- (v) Selected look-backs: k is frozen at {5, 15, 30} before any outcome. Choosing k after seeing results counts
  each tried k into N.
- (vi) Exposure on the discovery dates: E.33 computed ZS and ZL scaled returns (k 1, 5, 15) and the ZS/ZL OFI as
  features with ZM labels (feat33.py 1032-1051). The reverse direction (ZS and ZM returns with ZL labels) was never
  computed. Disclose this under P1.5.

**6. Compute.** Bars for three roots over 816 dates: seconds per feature pass, RAM well under 1 GB.

**7. Verdict: USE, bars only for ZS and ZM:** rS_k and rM_k at k = 5, 15, 30, and gR_k at k = 5, 15, 30. Leader
books are excluded because they would make the test read a new, unpriced purchase.

## (c) CL, HO and RB as leaders (biofuel and energy linkage)

**1. Data status.**
- CL ohlcv-1m: owned 2010-07..2026-06 (BRIEFS RULES), so both windows are owned. CL is a NYMEX contract and trades
  through the ZL day session.
- HO and RB ohlcv-1m: owned only 2025-04..2026-06, which is closed (2024-03 onward). Neither discovery nor test is
  owned, so using them needs two Databento purchases, each needing a quote and approval. Not free.
- RINs (D4, D6): no exchange futures feed; prices are OTC assessments (OPIS, Argus) [unverified: no page fetched]. No
  owned or free intraday series.

**2. Exposure.**
- E.12 Gate 0 (R1-11) and E.20's search (R1-15) both had G17, "the 60-minute log return (x 1e4) of each other
  cluster's lead price path". On ZL the live leads were NQ, ZN, 6E, CL and GC, at horizons h60, h120 and hF, over
  2019-05-06..2024-02-29, with no pass (E.32b recs L11, 442-449; R1_closed_lines.md lines 84, 112).
- LR-Q3b rated ZL F09 "same family and product at a neighbouring horizon" because of exactly these leads (recs L11,
  452-453).
- The ZL test window's 2019-05..2020-11 bars were read in those trials (E.12 and E.20 rows, seal section 4,
  reports/stage_e32_test_seal.md 123 and 126). A CL-to-ZL lead in the test is therefore not virgin either.

**3. Mechanism and equations.**
- Biodiesel is priced off its feedstock. Irwin and Good (farmdoc daily, 2013-09-18) model a soybean-oil plant with a
  "Conversion factor of 7.55 pounds of soybean oil per gallon of biodiesel". They find "the market has typically
  priced biodiesel based on the cost of soybean oil, a markup for other variable and fixed costs, and zero profits",
  with all other costs "lumped into the constant term of 0.60" (farmdoc_fdd180913_biodiesel_prices.pdf.txt lines
  51, 89-93).
- Zero-profit pricing [derived from that passage]: P_BD (USD/gal) = 0.60 + 7.55 x P_SBO (USD/lb). Revenue also
  includes the RIN, credits and glycerin, so diesel affects ZL only through the margin P_BD + RIN + credit -
  feedstock. The trade calls the oil-to-diesel gap "BOHO" (bean oil minus heating oil). Trade press says RIN values
  rise with it [unverified: Fastmarkets snippet in a search result, not fetched].
- Worked: one ZL tick (0.0001 USD/lb) is 7.55 x 0.0001 = 0.000755 USD of feedstock cost per gallon. If biodiesel
  value tracked heating oil one for one with no RIN absorption, a 1-cent-per-gallon HO move would map to 0.01 /
  7.55 = 0.001325 USD/lb = 13.2 ZL ticks [derived; illustrative upper bound]. The RIN and the margin absorb part of
  any such move, and the literature gives no intraday share.
- Direction in the discovery regime: in the renewable-diesel boom the feedstock led the fuel. "Biodiesel prices
  initially followed the surge upward in soybean oil prices, but lagged in the second half of 2021"
  (farmdoc_fdd111323_biodiesel_squeeze.pdf.txt lines 165-167, Irwin, 2023-11-13; weekly data). Biofuel-policy news
  moves ZL first (Avileis and Swanson, daily 2019-2025: "a 1% biofuel-induced price increase in soybean oil leads to
  a 0.19% rise in soybean prices and a 0.30% drop in soybean meal prices", E.32 brief 1802-1804).
- Weekly and older evidence on energy to vegetable oil: Kristoufek, Janda and Zilberman (weekly 2003-2011) find
  "biodiesel with German diesel" strongly connected at low frequencies, and in crisis periods "biodiesel ... is lead
  by ... (German diesel) even at high frequencies" (kristoufek_2012_timefreq_biofuels.pdf.txt lines 32-39; "high
  frequencies" there means scales of weeks). They report Busse et al. (2010), secondary: "crude oil strongly
  influenced the prices of biodiesel and biodiesel shocks transmitted into rapeseed oil prices. However, the results
  are regime-dependent." (lines 79-81). Tanaka, Guo and Wang (GCB Bioenergy 2023), wholesale prices: crude oil and
  biodiesel are net transmitters and soybeans a net receiver [unverified: abstract via search result only].
- Intraday: three queries for intraday or high-frequency soybean oil and crude oil lead-lag found no study (search
  log). The nearest intraday commodity work is on realised volatility, not return leads [unverified, search results].

**4. Verdict.**
- HO, RB, RINs: EXCLUDE (not owned in either window; RINs not available at all as an intraday series).
- CL: EXCLUDE from F09's registered sets. Reasons:
  - (i) The only CL-to-ZL test the program ran (60-minute CL return as a lead on ZL, h60-hF) found nothing, and a
    15-60 minute version is the same family at a neighbouring horizon (LR-Q3b). It would add trials to N with a
    prior lowered by that null.
  - (ii) The mechanism runs through biodiesel and RIN margins that the literature measures weekly or daily. In the
    discovery regime it ran mostly from ZL to fuel, not the reverse.
  - (iii) Its test-window bars (CL and ZL, 2019-05..2020-11) are already exposed through G17.
  - (iv) CL is the most-watched energy contract. A 15-60 minute lead from it into a liquid CBOT contract would be an
    unusual minutes-scale inefficiency with no published support found.
- Fallback, if the lead decides to include CL: one context feature rCL_15 = (CL(t) - CL(t - 15 min)) / (0.01 x
  sigma_CL(D) x sqrt(15)) from owned CL ohlcv-1m (bar timing as (b)(5)(i)), in the propagation set only. Count it
  and disclose it as a repeat of G17 at a neighbouring horizon. No CL rule.

## (d) Which leg adjusts: loadings, shares, half-life, and how to estimate them without selecting

**1. Core idea.** ZL is tradable on the crush only if it is a closing leg (alpha_L != 0, with the right sign and a
large enough share) and the closure is fast against the hold (hl < h). None of the three numbers is published for
intraday soy, and the program never measured them: E.33 made the VECM loadings a P6.5 diagnostic, run "after the
test list is hashed; Tier A and Tier B only" (E.32 protocol 663, 671-672), and with Tier A empty "none was
computed" (E.33c_RETURN.md 180-183).

**2. Equations** (E.32 M2 c-e, 4744-4760, 4962-5008, re-signed for ZL) [derived where marked]:
- VECM, r = 1, P = (S [c/bu], nL, nM)': dP_t = alpha z_{t-1} + sum_j Gamma_j dP_{t-j} + u_t, z = beta'P with
  physical beta = (-1, 0.11, 0.22) so that z = C (c/bu), or beta from a causal rolling Johansen fit normalised on
  the ZL entry.
- Adjustment share [derived]: s_i = beta_i alpha_i / (beta'alpha), with sum s_i = 1. With short-run terms, replace
  alpha by alpha~ = (I - sum Gamma_j)^-1 alpha (MathReview A-4, E.32 brief 4974). ZL's eventual move per 1 c/bu of
  z is alpha_L / (-beta'alpha) = -s_L / 0.11 ticks: ZL falls 9.09 s_L ticks when the crush is 1 c too wide.
- Weak exogeneity: H0 alpha_L = 0 (ZL does not adjust: F09's crush set is dead); H0 alpha_S = alpha_M = 0 (ZL does
  all the adjusting). "If they are zero then that particular error correction term does not enter that equation"
  (Boero notes, E.32 brief 5071).
- Half-life: phi = 1 + beta'alpha (Gamma = 0) and hl = -ln 2 / ln phi in sampling units (E.32 brief 4764,
  4863). At dt = 1 minute: phi 0.90 -> 6.58 min, 0.95 -> 13.51, 0.97 -> 22.76, 0.99 -> 68.97 (hl_from_phi). OLS
  biases phi down by about (1 + 3 phi)/T (Kiviet and Phillips eq. 3.12, E.32 brief 4866), so hl comes out too
  short. One day session (T 290) at true 0.95 gives about 10.6 min instead of 13.5 (E.32 brief 4891-4893). Correct
  with b_c = (T b_hat + 1)/(T - 3) and report Hansen grid-bootstrap intervals (E.32 brief 4871-4872, 4874-4879).
- Bivariate price-discovery device for ZL [derived, mirroring E.32 brief 5005-5010]: p1 = 0.11 nL (ZL's oil value,
  c/bu); p2 = S - 0.22 nM (implied oil value from beans less meal, c/bu); z = p1 - p2 = C; beta = (1, -1)', one
  common trend. Then CS_1 = alpha_2 / (alpha_2 - alpha_1), Hasbrouck IS_1 with both Cholesky orderings (report both
  bounds), and Putnins' ILS_1 = IL_1/(IL_1 + IL_2). ILS_1 > 0.5 says ZL leads, against the trade; ILS_1 < 0.5 says
  ZL follows. The trivariate IS/CS do not apply (two common trends; E.32 brief 4447-4450).

**3. Worked example (hypothetical alpha, not an estimate;** m2_examples.json vecm_hyp).
- alpha = (+0.02, -0.05, -0.06) per minute on (ZS cents, ZL ticks, ZM ticks), the same magnitudes as E.32 M2 e with
  signs for z = C.
- beta'alpha = -0.02 - 0.0055 - 0.0132 = -0.0387, so phi = 0.9613 and hl = 0.6931/0.03947 = 17.56 min.
- Shares: ZS 0.517, ZL 0.142, ZM 0.341. ZL's move per cent of z is -0.05/0.0387 = -1.292 ticks. Iterating the error
  correction from z0 = +1 c gives ZS +0.517 c, ZL -1.292 ticks, ZM -1.550 ticks and z -> 0, a match.
- Reading: at this alpha ZL cannot pay at D = 1 (1.29 < 2.38 even at full reversion). The kill line is s_L* from
  (a): 0.26 at full reversion, 0.40 at hl 20 and h 30.

**4. Literature on which leg adjusts** (no intraday s_L, hl or alpha_L is published in any source found).
- Intraday, 2015 day sessions (Zhou, Bagnarosa, Gohin, Pennings and Debie, J. Commodity Markets 2023; full text).
  Speeds depend on volume, the vector does not (E.32 brief 1576-1578). The ZL-specific passages, which the E.32 brief
  quoted only in part (zhou_jcm2023_wur.pdf.txt lines 821-822 and 880-882):
  - "the contribution of soybean to the common factor relative to that of soyoil is positively related to the
    ratio of the traded volumes of soyoil and soybean. This means that the higher the volume of soyoil relative to
    soybean, the more soybean will Granger cause soyoil";
  - "If the traded volumes of soyoil relative to soybean increase, we can expect soymeal to even more significantly
    Granger cause the soyoil dynamics".
  - Reading: ZL is the follower of both other legs on days when ZL's relative volume is high. "Which leg adjusts"
    is a state variable, so ZL's volume share and its ratio to ZS enter as features, not as a fixed belief.
- Daily, CBOT (Adrangi 2006, abstract only; full text failed again this stage, log): "soybean contracts bear the
  burden of convergence when the spread between soybean and soy meal contract prices widens, this is not true of
  soybean and soy oil contracts" (E.32 brief 1795-1797). For the bean-oil pair, beans do not carry the adjustment,
  which leaves oil (or neither) to do it: weak, abstract-level support for ZL adjusting daily.
- Daily, Dalian (Liu and Sono 2016, abstract): "one-way information flow from the soymeal and soyoil markets to the
  soybean market" (E.32 brief 1798). Beans adjust there.
- Pit-era open/close (Rechner and Poitras 1993, full text, saved E.32 page rechner_poitras_1993.pdf.txt lines
  267-278 and 343-356). For the oil leg alone the correlation of the overnight change with the next day-session
  change is "-0.035 (-1.70)" in 1978-87 and "-0.08935 (-2.95)" in 1987-91, against -0.49 and -0.43 for the crush
  (E.32 brief 1643-1644). Most of the crush's opening reversal is not a reversal in oil.
- Renewable-diesel regime, daily events (Avileis and Swanson, NCCC-134 2025, full text): biofuel shocks start in ZL,
  and "meal prices serve as a price anchor when it comes to biofuels" (E.32 brief 1802-1805). On those days ZL is the
  origin, not the closer. Weekly cash evidence agrees that beans decoupled from oil after 2020 (Janzen and Wang, E.32
  brief 1497-1501).
- Net: ZL plausibly follows bean and meal shocks (intraday, state-dependent) and leads on biofuel shocks. That is the
  reason for the origin split oL30 in (a) and for gR_k in (b).

**5. Estimating them without turning a diagnostic into a selection.**
- Allowed, causal features (inside the frozen feature set, so no extra trials):
  - for each date D, a VECM on the prior 20 dates' clean day-session minutes inside the segment, giving s_L(D),
    hl(D) and alpha_L(D);
  - these enter the ML set as features, or not at all.
  - Test: the values for D equal those from a run truncated at D's open (future-scramble invariance; E.32 brief
    5044-5046).
- Required, report-only (selects nothing):
  - after the search, on every F09 set whether or not anything passes (unlike E.33's Tier-A-only P6.5), report:
    alpha (trivariate, with Gamma), s_L with a session-block bootstrap CI, phi_hat, the Kendall-corrected phi_c,
    the grid-bootstrap hl CI by hour, and bivariate ILS with both IS bounds;
  - all on OOF dates, with beta frozen from prior dates.
  - A negative then comes with its mechanism: either ZL does not adjust or it adjusts too slowly.
- Not recommended, and if used it must be hashed in the registration: an early kill on the first fold's training
  dates (s_L's CI upper end below s_L* at the frozen D and h). It is a pre-registered selection step on discovery
  prices. It saves compute but steers the search, and its dates must stay training-only. Its use is the lead's
  decision.
- Gate parameters (sampling dt = 1 min, 20-date window, day session only, release minutes excluded, IS ordering
  rule) are frozen before any outcome. Choosing them after seeing results is a selection step (E.32 brief 5047-5049).

**6. Data.** The same 1-minute bars (leaders) and ZL mids or bars as (a); no extra purchase. Compute is milliseconds
per date for the VECM (E.32 brief 5055-5056). Grid bootstraps run minutes on 8 threads.

**7. Verdict: USE** in two roles: causal prior-date estimates as features (optional), and the report-only
diagnostic (required). No gate on outcome-bearing statistics unless it is pre-registered.

## (e) How E.33's ZM negative constrains the prior for ZL as the traded leg

**1. What E.33 showed** (E.33c_RETURN.md 12-35, 207-225; aggregate outcomes only):
- 300 configurations: S1 crush, S2 propagation from ZS and ZL, S3 ZM order flow, S4 own path, S5 pooled; 6 labels;
  10 models.
- Tier A empty. The best G1 configuration loses 1.098 ticks a trade. The best daily Sharpe, 0.0478, sits inside the
  null's per-seed maxima; it is "not a null statement in the program's sense".
- ZL entered only as an input leg (its mids, scaled returns and OFI). ZL labels were never computed.

**2. Two channels that pull in opposite directions.**
- (i) Leg-share channel (raises the ZL prior). The shares of a closure sum to one. E.33's failure is evidence
  against "ZM closes the residual strongly at 5-60 minutes", and that removes probability from a hypothesis that
  competes with "ZL closes it".
  - Illustration, not an estimate: say the prior weights are ZM strong closer 0.10, ZL strong closer 0.10, and
    everything else (no tradable minutes structure, beans close, the structure is seconds-fast) 0.80. Say E.33 had
    power 0.8 against the ZM case.
  - The ZM weight then falls to 0.1 x 0.2 / (0.02 + 0.90) = 0.022, and the ZL weight rises to 0.10/0.92 = 0.109, a
    9% relative gain.
- (ii) Common-cause channel (lowers it):
  - E.33 failed across every set, including ZM's own order flow and the pooled set, at a cost per sigma (ZM 1.59/
    17.25 = 0.092 at 30 minutes under random-walk scaling) that ZL barely improves on (2.38/28.10 = 0.085;
    m2_examples.json cost_per_sigma). It is base-rate evidence that 1-lot market-order signals at minutes in this
    complex do not clear costs.
  - Its S2 also says ZS and ZL moves at 1-15 minute look-backs carried no tradable information for the less liquid
    byproduct. The same slow-participant mechanism is what F09 needs from ZL.
  - In the renewable-diesel regime, ZL is also where the complex's idiosyncratic shocks start (section d). That
    makes "ZL lags" less likely than "ZM lags" was.
- (iii) What E.33 does not constrain:
  - s_L and hl, which were never estimated;
  - the ZS/ZM-to-ZL direction of propagation;
  - the origin-split reading, in which only leader-opened dislocations are traded.
  - Power is limited too: E.33 could miss edges below its minimum detectable 1.41-3.98 ZM ticks a trade
    (E.33c_RETURN.md 194-200). The ZL discovery e80 is 1.08, 2.16 and 4.41 ticks at h 15, 30, 60 (BRIEFS RULES).

**3. Reading.**
- Channel (i) is small, because the ZM-strong-closer weight was already low before E.33 (the literature prior was
  "ZM is NOT the default adjusting leg", E.32 brief 1825-1827).
- Channel (ii) is broad. On balance E.33 is weak, mildly negative evidence for F09 on ZL. E.32b's figure (F09 about
  2.5%, P(edge) 0.05 after lowering for the G17 null, x 0.7 x 0.7; recs 4.5, 545-548) is consistent with this
  reading; nothing here argues for raising it.
- The prior number is the lead's decision.
- One design consequence follows: F09 on ZL should not be a mirror of E.33's S1 and S2 with the leg swapped. It
  should carry the two changes the regime evidence suggests (the ZL-dependent residual with the origin split, and
  the regression-weight gap). Otherwise it inherits E.33's failure mode unchanged.

## (f) Protocol inputs

Proposals for the lead's pre-registration; the lead decides what enters, the model rule (V43/V28) and every count.
Notation and general rules follow the E.32 protocol 0.3 and G1-G4 (lines 46-70, 368-380):
- point in time on ts_recv for book data;
- bars usable only after their close (rule B below);
- level quantities only inside the current segment (all three fronts unchanged);
- scales chained across rolls;
- invalid -> 0 with the family flag set;
- clip to [-5, 5] after normalisation.

**Prices.** O(u): ZL BBO mid as of u if the program holds ZL book data, else the close of ZL's last complete
ohlcv-1m bar. S(u), M(u): the close of ZS's and ZM's last complete ohlcv-1m bar. Rule B: at decision time t the last
usable bar of any root is the one stamped t - 1 min (the bar covering [t - 1 min, t)) [bar-stamp convention for
DataFacts to confirm]. Staleness: a leg whose last trade bar is older than 2 minutes at t makes every F09 feature
invalid at t.

**Scales.** sigma_X(D) for X in {ZS, ZM, ZL} as protocol 0.3 (20 prior dates, 08:35-13:13, 1-minute changes, in
ticks of X). Crush statistics in c/bu. V_X(k): contracts traded in the k minutes ending at t (bar volumes; ZL from
its book trades if held).

**Crush set S_crushL (8 features; each with E.33's context block C if the lead keeps it).**

| ID | Definition | Look-back | Normalisation |
|---|---|---|---|
| L1.1 | zC30 = (C(t) - mean_30)/sd_30, C = 11 O + 2.2 M - S; mean and sd over C(t - j min), j = 1..30 | 30 min, in segment | own rolling z; clip |
| L1.2 | zC120: as L1.1 with j = 1..120 | 120 min, in segment | as L1.1 |
| L1.3 | zRL = e_L(t)/sd_e; before D's open, OLS O = a + b_S S + b_M M on the clean 1-minute samples 08:35-13:13 (release marks [R - 2, R + 30] min excluded) of the 10 trade dates before D in the segment (at least 3 dates or invalid); centred fit, a from the means; e_L = (O - a - b_S S - b_M M)/0.01 in ZL ticks; sd_e = fit residual SD in ZL ticks; coefficients fixed for D | 10 dates | sd_e; clip |
| L1.4 | dzC5 = zC30(t) - zC30(t - 5 min) | 35 min | difference of z |
| L1.5 | oL30 = 11 dO_30 / (\|11 dO_30\| + \|2.2 dM_30\| + \|dS_30\|), dX_30 = X(t) - X(t - 30 min) | 30 min | bounded [-1, 1]; invalid if denominator 0 |
| L1.6 | zC30 x (1 - \|oL30\|) (reversion weighted to leader-opened dislocations) | 30 min | product |
| L1.7 | vrelL15 = V_ZL(15)/(V_ZL(15) + V_ZS(15) + V_ZM(15)) | 15 min | share in [0, 1] |
| L1.8 | zC30 x vrelL15 | 30 min | product |

**Propagation set S_propL (9 features).**

| ID | Definition | Look-back | Normalisation |
|---|---|---|---|
| L2.1-L2.3 | rS_k = (S(t) - S(t - k))/0.25/(sigma_ZS(D) sqrt(k)), k = 5, 15, 30 | k min | sigma_ZS(D); clip |
| L2.4-L2.6 | rM_k = (M(t) - M(t - k))/0.10/(sigma_ZM(D) sqrt(k)), k = 5, 15, 30 | k min | sigma_ZM(D); clip |
| L2.7-L2.9 | gR_k = [b_S dS_k + b_M dM_k - dO_k]/0.01/(sigma_ZL(D) sqrt(k)), b_S, b_M from L1.3's fit for D (invalid when L1.3 is invalid), k = 5, 15, 30 | k min | sigma_ZL(D); clip |

- Not included, with reasons:
  - k = 1 (bounce is 29% of sigma_1, (b)3);
  - the physical-weight gap g_k (equal to a scaled crush change, already carried by L1.4; mostly margin moves,
    (b)3);
  - F1.7/F1.8 overnight crush gap (K6-crushgap-01 exposure, (a)7);
  - leader OFI and any ZS or ZM book feature (test-window purchase, (b)4);
  - CL (see (c); fallback rCL_15 = (CL(t) - CL(t - 15))/0.01/(sigma_CL(D) sqrt(15)) in S_propL only, if the lead
    overrides);
  - HO, RB, RINs (not owned).
- ZL's own scaled returns enter only through the context block C (as E.33 treated the own price path); the gaps
  already net ZL's own move.
- Optional causal mechanism features (d)5, if the lead wants them in S_crushL: s_L(D), hl(D) from a VECM on the 20
  prior dates (day session, dt 1 min, release marks excluded, beta normalised on the ZL entry, lag order fixed at 5).
  They are constant within D. This adds 2 features, not trials.

**Model rule.**
- My judgment: F09 built only from bars is not an order-book strategy, so under a literal V43 (docs/DECISIONS.md
  788-806: "for order-book and limit-order strategies"; "V28 stands unchanged for every other line") it must run as
  rules.
- The ML form (S_crushL and S_propL as E.33-style sets) is admissible only if the lead rules that sets whose labels,
  execution and ZL mid come from ZL's own book inside the one order-book program qualify, as E.33's precedent did
  ("E.33 ran its crush and propagation sets as ML inside an order-book program", BRIEFS RULES).
- This is the lead's decision (reserved); the counts below are for either reading.

**Rule-based variant (V28), 4 rules x h {15, 30, 60} = 12 configurations.**

Common to every rule:
- Decision grid: minute marks 08:35..(13:12 - h) CT, further capped by Topstep's latest entry (h 30: 10:50 PT =
  12:50 CT).
- One position at a time. Enter at the first qualifying mark, by market order: ZL ask/bid at t + 1 s from the book,
  or the next ZL bar's open plus c_f if bars only.
- Exit by market at t + h. Flat by the session end. E.33's P3.6 exclusions (releases, rolls, limits). No re-entry
  until flat.
- Thresholds are fixed here, from E.32b's draft (recs 4.5(b) P4-P5, 616-619), not tuned. Any other value is a new
  configuration counted into N.

| Rule | Entry condition at mark t | Side |
|---|---|---|
| R1 crush reversion (ZL-dependent residual) | \|zRL\| >= 2.0 | sell if zRL > 0, buy if < 0 |
| R2 leader-opened crush reversion | \|zC30\| >= 1.5 and \|oL30\| <= 1/3 | sell if zC30 > 0, buy if < 0 |
| R3 implied-oil catch-up | \|gR_15\| >= 1.5 | buy if gR_15 > 0, sell if < 0 |
| R4 ZS leads | \|rS_15\| >= 1.5 and \|rL_15\| <= 0.5 (rL_15 = ZL's own scaled 15-minute return) | the sign of rS_15 |

**Parameters to freeze (all F09).**
- Segment rule (protocol G2).
- 10-date OLS window, at least 3 dates.
- 20-date scale window.
- Staleness limit 2 min.
- Rule B bar timing.
- Look-backs {5, 15, 30}; z windows {30, 120}; volume window 15.
- The origin window 30 and cut 1/3.
- Thresholds 2.0, 1.5, 1.5, 1.5, 0.5.
- Holds {15, 30, 60}; release exclusion [R - 2, R + 30] min.
- Clip [-5, 5].
- c_f 2.38 (spread assumed 1.0 tick [u]; sensitivity at the measured spread, (a)3).
- The report-only diagnostic list of (d)5.

**Data per window.**
- Discovery 2020-12-01..2024-02-29: ZS, ZM, ZL ohlcv-1m (owned, 39 files each); ZL book (owned MBP-1 front month,
  or the F10 MBO purchase, USD 19.48 estimate); definitions Z4 (owned).
- Test 2017-05..2020-11: ZS, ZM, ZL ohlcv-1m inside the sealed files (USD 0); ZL book only as F10 buys it; no ZS or
  ZM book.
- Exposure to disclose (P1.5 and seal section 4):
  - E.33's ZS/ZL features with ZM labels on the discovery dates;
  - E.31's ZS/ZL 1 s and 10 s splits;
  - E.12/E.20 G17 leads (CL among them) on ZL, 2019-05..2024-02, which covers the test window's 2019-05..2020-11
    bars;
  - E.22's crush gap traded in ZS.

**Trial-count implications (for the lead).** Rules: 12. ML on the two sets: 2 sets x 5 labels x 10 model settings =
100 (E.32b's option A counted 200 for four sets including S_book and S_pool).

## Evidence table

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Biodiesel priced off soybean oil cost; 7.55 lb/gal | Irwin and Good, farmdoc daily 2013-09-18 (extension) | "Conversion factor of 7.55 pounds of soybean oil per gallon of biodiesel"; "the market has typically priced biodiesel based on the cost of soybean oil, a markup for other variable and fixed costs, and zero profits" | pages/farmdoc_fdd180913_biodiesel_prices.pdf(.txt) lines 51, 93-94 |
| In the RD boom, biodiesel lagged soybean oil | Irwin, farmdoc daily 2023-11-13 (extension) | "Biodiesel prices initially followed the surge upward in soybean oil prices, but lagged in the second half of 2021" | pages/farmdoc_fdd111323_biodiesel_squeeze.pdf(.txt) lines 165-167 |
| Conversion 7.50-7.55 lb/gal held throughout | same | "This has been assumed to be between 7.50 and 7.55 pounds per gallon for the entire time we have used the model." | same, lines 78-80 |
| Biodiesel led by diesel at weekly scales in crises | Kristoufek, Janda and Zilberman 2012 (academic; arXiv 1209.0900) | "in the crisis periods, ethanol (biodiesel) is lead by corn (German diesel) even at high frequencies (low scales)" | pages/kristoufek_2012_timefreq_biofuels.pdf(.txt) lines 38-39 |
| Busse et al.: crude oil influences biodiesel, regime-dependent (secondary) | same, citing Busse et al. 2010 | "crude oil strongly influenced the prices of biodiesel and biodiesel shocks transmitted into rapeseed oil prices. However, the results are regime-dependent." | same, lines 80-81 |
| ZL follows ZS more when ZL's relative volume is high | Zhou et al. 2023 JCM (academic, full text, E.32 page) | "the higher the volume of soyoil relative to soybean, the more soybean will Granger cause soyoil" | reports/stage_e32_briefs/pages/R3a_crush/zhou_jcm2023_wur.pdf.txt lines 822, 880 |
| ZL follows ZM more when ZL's relative volume is high | same | "If the traded volumes of soyoil relative to soybean increase, we can expect soymeal to even more significantly Granger cause the soyoil dynamics" | same, lines 881-882 |
| Oil leg alone barely reverses overnight moves | Rechner and Poitras 1993 (academic, full text, E.32 page) | Table IA soybean oil: "(Open, - Close,-]) and (Close, - Open,) -0.035 (-1.70)"; Table IB: "-0.08935 (-2.95)" | reports/stage_e32_briefs/pages/R3a_crush/rechner_poitras_1993.pdf.txt lines 278, 356 |
| Day-session cointegration 180/243; no half-life | Zhou et al. | E.32 brief R3a 3.1 | E.32 brief 1549-1590 |
| Leg relations broke after 2020 (weekly) | Janzen and Wang 2025 | E.32 brief R3a 2.1 | E.32 brief 1497-1501 |
| Biofuel shocks start in ZL; meal anchors | Avileis and Swanson 2025 | E.32 brief R3a 6.1 | E.32 brief 1802-1805 |
| Beans do not carry the bean-oil adjustment (daily) | Adrangi 2006 [abstract only] | E.32 brief R3a 6.1 | E.32 brief 1795-1797 |
| Crude and biodiesel net transmitters (wholesale) | Tanaka, Guo and Wang 2023, GCB Bioenergy | [unverified: abstract via search result] | none |
| BOHO spread and RIN values co-move | Fastmarkets trade press | [unverified: search snippet] | none |
| ZL spread about 2.06 ticks US hours 2022 | GRAINS-35 | [unverified: snippet] | F2_grains.md line 54 |
| VECM shares, weak exogeneity, half-life bias, grid bootstrap, ILS | E.32 M2 (c)-(e) | as cited in (d) | E.32 brief 4699-5080 |

## Search log, stopping rule, failures

- WebSearch: 13 queries (12:11-12:20 PDT). No budget notice. Topics:
  - which leg adjusts in the crush (3 queries);
  - soybean oil and crude, heating oil or diesel transmission (4);
  - intraday soybean oil and energy lead-lag (3);
  - EPA RVO intraday reactions (1; trade press only, events 2025-2026, outside both windows);
  - farmdoc biodiesel and BOHO (2).
- Searched, not found: any intraday estimate of ZL's crush-adjustment share or half-life; any intraday (minutes)
  study of soybean oil against crude oil or heating oil; any academic intraday event study of EPA announcements on
  ZL.
- Fetches (pages/log.tsv). Method: curl with browser headers. WebFetch was not used, because it returns a model
  summary, not the raw bytes rule 9 requires to be saved. Scrapling was used once (`extract get`, then the library
  fetcher).
  - Saved and used: farmdoc fdd180913, farmdoc fdd111323, Kristoufek et al. arXiv 1209.0900.
  - Failed:
    - Adrangi 2006 (three Clute OJS URLs return a viewer page with no PDF);
    - AgEcon Search 15880 and Franken, Irwin and Garcia 2020 (AWS WAF challenge, HTTP 202; Scrapling `extract get`
      returned the PDF once but as decoded text, unreadable; the library fetcher got the 202 page; Firecrawl not
      tried);
    - the IPB journal VECM paper (PDF xref error).
  - These gaps are covered by the E.32 brief's sources or marked [unverified]. None is presented as a finding.
- Stopping rule: each topic (a)-(e) has at least two full-text sources, or an explicit "not found" after at least
  three queries.

## Not finished or not verified

- Not verified here:
  - the ohlcv-1m bar-stamp convention (ts_event at the bar open);
  - the ZS, ZM and ZL contract months;
  - the ZL day-session spread. These are DataFacts or run-stage counts.
- No intraday s_L, hl or ZL-CL lead evidence exists in what was searched. Every such number above is hypothetical
  and labelled so.
- The Franken, Irwin and Garcia (2020) biodiesel hedge paper (soybean oil against heating oil weights) was not
  obtained (WAF). A Firecrawl retry was not attempted.
