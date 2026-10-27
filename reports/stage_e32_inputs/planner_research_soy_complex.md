# Planner research: short-horizon directional predictability in the soybean complex (2026-10-26)

This is an external web research run from the planning chat. Treat it as
pointers to verify, not as evidence to cite unchecked. Several 2025 papers
were read from abstracts only, and the core order-book studies use 2015
data. CME pages were not fetched. The probability judgements are the
research run's opinion.

## Bottom line (as reported)

No published study shows a directional ZM edge at seconds-to-hours
horizons that clears about 1.6 ticks at retail latency. The research
run's prior for any single family clearing it out of sample is under 20%.

## Contract arithmetic

- ZM tick is 10 USD, ZS tick 12.50 USD, ZL tick 6 USD.
- Board crush per bushel = 0.022 x meal ($/ton) + 0.11 x oil (cents/lb)
  - beans ($/bu). The ratio is 10 ZS : 11 ZM : 9 ZL; Rechner and Poitras
  used 10:12:9.
- One ZM tick moves the crush by 0.22 cents/bu, so a 1 cent/bu crush
  dislocation is about 4.5 ZM ticks if ZM alone adjusts.

## Key evidence

- Zhou, Bagnarosa, Gohin, Pennings and Debie, J. Commodity Markets 2023
  (NCCC-134 2022 version), CME LOB 2015, 1-minute sampling, daily
  state-space VECM:
  - the day session was cointegrated on 180 of 243 days (229 at
    2-minute sampling); the overnight session on only 52;
  - the median vector, normalised to ZS = 1, was ZL -0.11 and ZM -0.19,
    against physical weights of -0.11 and -0.22, each with a daily SD of
    0.28;
  - leadership depends on relative volume, with no fixed leader;
  - no half-life or information-share levels are reported.
- de Boer, Gardebroek, Pennings and Trujillo-Barrera, JFM 2022, 2015
  data:
  - liquidity spillovers occur mostly within 30 seconds;
  - round-trip liquidity cost is 9.2 bp for ZS, 12.5 bp for ZL and
    13.6 bp for ZM, so ZM is the least liquid leg.
- Arzandeh and Frank, AJAE 2019: soybean price duration is about 7.6
  seconds; book levels beyond the best quote carry more than 27% of
  price discovery.
- Ma and Serra, AJAE 2025, corn, soybeans and wheat MBO, 2019-01 to
  2020-06:
  - trades that move the best quote carry 27-30% of price discovery;
  - limit submissions and cancellations at the touch carry about 56%.
  This is contemporaneous; no forward-looking OFI evidence exists for
  grains.
- Crush profitability at daily horizons:
  - Simon, JFM 1999: profitable in 1985-1995.
  - Mitchell, JRFM 2010: unstable.
  - Abdoh and Chitavi, IREF 2025, 1990-2021: deviations of meal and oil
    from USDA crushing yields explain transitory crush moves; three-leg
    daily rules were profitable after costs (abstract only).
  - No intraday half-life is published. That is a gap the discovery data
    can fill.
- USDA reports:
  - the price and volatility effect is gone within minutes (Lehecka,
    Wang and Garcia 2014; Adjemian and Irwin 2018);
  - volatility stays elevated for up to about 60 minutes (Kauffman
    2013);
  - 11:00 CT releases have been made into live trading since 2012;
  - the DIRECTION of the 15-90 minute path after the jump is untested.
    One farmdoc anecdote (2025-09-12 WASDE) shows a full reversal.
- Settlement:
  - the closing range is 13:14 to 13:15 CT, and TAS has existed since
    2015-06-15;
  - after the 2012 move to electronic settlement, pre-close to
    settlement reversals declined (Onur and Reiffen, CFTC 2018).
- Intraday momentum, where the first half-hour predicts the last
  half-hour:
  - US ETFs (Gao, Han, Li and Zhou), R2 about 1.2-1.7% out of sample;
  - Chinese commodities including Dalian soybean meal (t about 3.07).
  - It has not been tested on CBOT ZM.
- Overnight: crush cointegration mostly breaks down overnight. A
  hypothesis: ZM dislocations built overnight get repaired after the
  08:30 open. This is untested.
- ML: no credible grain LOB ML study exists. Briola et al. (QF 2025)
  found deep LOB models help only for very active stocks. ZM is in the
  sparse regime, so deep models are not recommended at hours-scale
  labels.

## The research run's ranked idea families

1. ZM-leg crush-residual reversion at 15-240 minutes, conditioned on
   session and hour, z-score and liquidity state, including overnight
   build-up repaired after 08:30. Under-studied intraday.
2. The direction of the path 15-90 minutes after USDA releases (WASDE,
   Grain Stocks, Acreage, NOPA), entering 5-15 minutes after the release,
   conditioned on the initial jump and early order flow. There are only
   about 40 major events in the discovery window. Largely unpublished.
3. Late-session momentum or reversal into the 13:15 settlement (the first
   30 minutes or the overnight return predicting the last 30-45 minutes).
   Unpublished for ZM, but the idea is well known.
4. Overnight-gap continuation or reversal at the 08:30 open.
5. The aftermath of non-news jumps and liquidity shocks (sweep and
   refill) at 1-30 minutes.
6. ZS/ZL to ZM lead-lag in seconds: a feature only (under 1 tick, and
   HFT takes it).
7. MBO order-flow imbalance, aggressive cancellations and queue features:
   conditioners only.
8. Index roll, first notice day and COT: regime flags or exclusions.
9. End-to-end deep LOB ML: do not pre-register.

## Its protocol suggestions (for the lead to weigh, not binding)

- At most 4-5 families, with Holm or Bonferroni across families and a
  deflated Sharpe or White's reality check within each.
- Labels at 5, 15, 30, 60, 120 and 240 minutes and to the session close,
  net of 1.6 ticks, plus a triple-barrier label at about +-4-6 ticks.
- A crush residual from both the 10:11:9 weights and a causal rolling
  beta over 5-20 sessions. Estimate the half-life by session and hour,
  and test early which leg adjusts: if ZM is not the adjusting leg,
  family 1 dies.
- Mandatory strata: day and overnight sessions, report days, and roll
  and notice windows. Expect a regime break between discovery (2020-24,
  renewable-diesel oil share) and test (2017-20, trade war and Covid).
  Prefer adaptive betas and frozen hyperparameters.
- Walk-forward validation with purge and embargo of at least the label
  horizon plus one session, block bootstrap by day, and positive results
  in at least two-thirds of quarters.
- Market-order execution with depth-conditioned slippage and 300-1,000
  ms latency, excluding the first 1-2 minutes after releases. Prop-firm
  rules belong in the objective.
- Models: regularised linear or logistic, and shallow GBM (depth up to 3,
  monotone constraints where the sign is economically fixed). No deep
  LOB models.

## Main sources (URLs as given by the research run)

- Zhou et al. NCCC-134 2022: https://farmdoc.illinois.edu/assets/meetings/nccc134/conf_2022/pdf/Zhou_Bagnarosa_Gohin_Pennings_Debie_NCCC-134_2022.pdf ; https://edepot.wur.nl/629433
- de Boer et al. JFM 2022: https://onlinelibrary.wiley.com/doi/10.1002/fut.22325
- Arzandeh and Frank AJAE 2019: https://onlinelibrary.wiley.com/doi/10.1111/ajae.12479
- Ma and Serra AJAE 2025: https://ideas.repec.org/a/wly/ajagec/v107y2025i1p125-151.html
- Simon JFM 1999: https://ideas.repec.org/a/wly/jfutmk/v19y1999i3p271-289.html
- Mitchell JRFM 2010: https://ideas.repec.org/a/gam/jjrfmx/v3y2010i1p63-96d28369.html
- Abdoh and Chitavi IREF 2025: https://www.sciencedirect.com/science/article/pii/S1059056025003491
- Rechner and Poitras 1993: https://www.sfu.ca/~poitras/soy.pdf
- Lehecka et al. corn: https://www.researchgate.net/publication/278398012
- Adjemian and Irwin AJAE 2018: https://onlinelibrary.wiley.com/doi/abs/10.1093/ajae/aay018
- Couleau, Serra and Garcia NCCC-134 2018: https://farmdoc.illinois.edu/assets/meetings/nccc134/conf_2018/pdf/Couleau_Serra_Garcia_NCCC-134_2018.pdf
- Onur and Reiffen CFTC: https://www.cftc.gov/sites/default/files/2019-05/onur_reiffen_Manuscript_ada.pdf
- Gao, Han, Li and Zhou: https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf
- Li, Wang and Diersen NCCC-134 2024: https://farmdoc.illinois.edu/assets/meetings/nccc134/conf_2024/pdf/Li_Wang_Diersen_NCCC-134_2024.pdf
- Briola et al. QF 2025: https://www.tandfonline.com/doi/full/10.1080/14697688.2025.2522911
- farmdoc daily 2025-09 WASDE: https://farmdocdaily.illinois.edu/2025/09/corn-and-soybean-markets-shrug-off-bearish-usda-figures.html
