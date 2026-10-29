# F2 crude (MCL, QM, CL): sourced facts for Stage E.32b

Worker: CrudeReader-OpusHigh. Started 2026-10-28 22:46 PDT. Items: 55 (CRUDE-1 to CRUDE-55) in
reports/stage_e32b_briefs/F2_crude.json. WebSearch calls: 27 of 60. Full-text T6 reads: 3 of 12. Pages and log:
reports/stage_e32b_briefs/pages/CRUDE/ (log.tsv). Helpers: reports/stage_e32b_briefs/work/CRUDE/.
Facts only. No scores. Items marked "reused" cite E.28 (A1_crude.json) or E.20 (product_CL.json) and their saved pages.
Shared sources were not fetched: CFTC automated-trading series (RatesReader) and Baltussen et al. (EquityReader). CRUDE-18
only points to E.20's earlier reading of Baltussen.

## Underlying and roles

- Underlying: WTI light sweet crude. Siblings: CL (1,000 bbl, tick 0.01), QM (500 bbl, tick 0.025 = 2.5 CL ticks),
  MCL (100 bbl, tick 0.01). The leader by size and settlement is CL. It is physically delivered at Cushing (CRUDE-11).
- MCL and QM settle in cash at CL's final settlement price. Rulebook ch. 309 and 401: "The Floating Price for each
  contract month will be equal to the Light Sweet Crude Oil Futures contract final settlement price" (CRUDE-9,
  CRUDE-10, CRUDE-36).

## CL (leader)

T1, spread and touch. No time-weighted, session-split median was found.
- CRUDE-1: in 2012-13 the majority of volume traded at a one-tick spread. This is volume-weighted, with no session
  split (Roberts 2018, UMD thesis, reused).
- CRUDE-48: CME whitepaper (Wayback), Q1 2023, most active month, average best bid/ask by hour. In the US day-session
  hours (22:00-03:00 SGT = 09:00-14:00 ET) the hourly values are 1.27 to 1.30 ticks. Over all 24 hours they run from
  1.27 to 1.73, widest at 06:00 SGT, next to the daily pause. These are means of hourly averages, not medians.
- CRUDE-45 [unverified: snippet]: CME 2016 deck, average 1.07 ticks in US hours and 1.18 in Asian hours. The deck is
  only on cmegroup.com and has no Wayback capture.
- Touch: median level-1 bid depth 7 contracts, 2012-13 (CRUDE-2). Mean top-of-book quantity about 8 lots in US
  day-session hours, Q1 2023, ranging 7.6 to 9.1 (CRUDE-49). On average 25 lots executable at the best bid-ask in US
  hours, 2018 (CRUDE-50; the measure is not defined).

T2a, automated share (the CFTC series is excluded and belongs to RatesReader).
- CRUDE-55: CME note, Q1 2010. Algorithmic trading was 35.34% of CL volume and 71.24% of messages, the lowest of the
  five flagship products.
- CRUDE-3: 52 electronic market-maker accounts made about 50% of WTI volume in 2011 (CFTC working paper, reused).
- CRUDE-42 (pointer, snippet): HFT was more than 60% of all US futures volume in 2012 (Tabb Group, via news).
- No post-2016 product-level figure was found outside the CFTC series.

T2b, programs in force 2021-2026 (CFTC self-certifications, full text).
- CRUDE-25: NYMEX Crude and Refined Futures Volume Incentive Program (CL, HO, RB on Globex), 2018-02-01 to
  2025-01-31.
- CRUDE-26: NYMEX Crude Oil Incentive Program (CL, BZ), 2024-02-15 to 2025-01-31.
- CRUDE-46: NYMEX Crude Liquidity Program (CL, BZ), 2024-06-01 to 2025-01-31.
- Negative scope, not CL: the Oil Incentive Program covers third-party-assessment products, extended to 2026-01-31
  (CRUDE-27). The Oil LPP covers HTT and WTT, 2022-10 to 2024-01 (CRUDE-47).
- Not read: the 2025-12-02 Oil LPP modification. The 2013-15 MMP excluded CL (CRUDE-6).

T2c, retail share. None published. Proxies only (CRUDE-8).

T5, price discovery. CRUDE-32 (Elder, Miao, Ramchander 2014; 1-second data, 2007-2012): WTI's mean daily information
share against ICE Brent is 81.6%, and the mean lower bound is 69.3%.

## MCL

- T1: own spread and touch not sourced. Three queries returned nothing (searched_not_found). Leader facts:
  CRUDE-1, 2, 48, 49, 50.
- T2b: NYMEX Micro Crude Oil Liquidity Provider Program, 2021-07-12 to 2026-01-31, with quoting obligations
  (CRUDE-4). The leader's programs are listed under CL.
- T2c: about 109,000 individual traders since launch. No share figure (CRUDE-7).
- T5: cash-settled at CL's final settlement (CRUDE-9). No MCL-CL information-share study was found.

## QM

- T1: not sourced. Leader facts only.
- T2b: only the 2013-15 Crude and Refined MMP (CRUDE-5). No QM program for 2021-2026 was found. The leader's programs
  are listed under CL.
- T5: cash-settled at CL's final settlement (CRUDE-10). Tse and Xiang (2005) study QM against CL, but the result is
  unknown: no abstract on IDEAS, Crossref or OpenAlex (CRUDE-12).
- F1 (CRUDE-24): QM median daily volume was 4,480.5 contracts over 2025-10-01 to 2026-09-30 (E.31_RETURN.md lines
  10-11). The old A1 values ([1].adv_2022_11_2023_10 and adv_published_latest) are null.

## Shared underlying facts (apply to MCL, QM, CL)

T3, relationships.
- CRUDE-33 (economic, WTI-Brent): intraday price discovery on 1-second data, with WTI leading. The authors say oil
  futures fully reflect new information "within minutes". This is a lead-lag measured at seconds, not a minute-level
  predictive lead.
- CRUDE-34 (economic, crack HO-CL and location Brent-WTI): the spreads mean-revert and the legs are cointegrated, on
  daily and monthly data from 1984 to 2005 (Dempster et al. 2006). No intraday crack study was found.
- CRUDE-35 (calendar, mechanical): CL calendar spreads are common. Non-active months settle from the calendar-spread
  VWAP over 2:28-2:30 pm ET.
- CRUDE-36 (mechanical): the micro and mini to full pairs MCL-CL and QM-CL.

T4, scheduled events and how fast they are absorbed.
- Schedule: EIA WPSR on Wednesdays at 10:30 ET (CRUDE-13). API on Tuesdays at 16:30 ET (CRUDE-15). Macro releases
  at 8:30 and 10:00 ET; payrolls are followed by jumps in more than 30% of releases, 2005-2010 (CRUDE-38).
- Fast absorption, or reversal:
  - BoC SWP 2020-8 (2003-2017): estimates over 5, 15 and 30 minutes are "very close" (CRUDE-14).
  - Luo and Kang (5-minute data, about 2003-2010): the shock does not predict returns over 10:35-11:00 or 11:00-15:00
    ET (CRUDE-51, negative). The pre-release predictability they find is leakage.
  - Geman and Li (abstract): effects last about 25 minutes, then the price reverts quickly (CRUDE-30).
  - Rousse and Sevi (2007-2014): the CL price over-reacts, and half of the move is reversed after 4 hours (CRUDE-52).
  - Ye and Karali 2015 poster (2013-14): 15-minute API and EIA effects; the EIA effect is about twice API's
    (CRUDE-28).
- Slow adjustment, on another venue: Wen et al. 2023 (USO ETF, 2006-2019) find that the EIA-day "adjustment process
  is rather slow and is only completed at the end of the trading day". It is in sample, declining, and absent in
  2014-2016 (CRUDE-20).
- Other: pre-EIA order imbalance (CRUDE-16, conditional on the ex-post surprise). A daily announcement-day effect
  (CRUDE-53). OPEC: no intraday study was found.

T6, directional evidence (5 minutes to the session).
- CL itself:
  - Baltussen et al. (JFE 2021, via E.20): CL last-half-hour momentum gives R2_OOS of -1.04%, a null (CRUDE-18,
    negative).
  - Wang and Yang (2010, Energy Economics, abstract): no out-of-sample 30-minute predictability in crude. Only heating
    oil and natural gas show it. The data are from before 2010 (CRUDE-39, negative). A citing paper paraphrases this as
    WTI predictability, which conflicts with the abstract.
  - Geman and Li (abstract): an EIA-day strategy that follows the 10:20-10:25 move (CRUDE-31). Sample and costs are
    not stated.
- Same underlying, another venue (USO):
  - Wen et al. 2023 (CRUDE-19): in sample and gross. The EIA-day third half-hour predicts the last half-hour, and on
    other days the first half-hour does.
  - Wen, Gong, Ma, Xu 2021 (CRUDE-43, snippet only): in and out of sample.
- Other crude benchmarks and venues:
  - ICE Brent time-of-day strategies with alphas after costs (CRUDE-23, abstract).
  - ICE Brent is inefficient under 10 minutes, and efficiency improves at lower frequencies. No costs were included
    (CRUDE-54, full text).
  - INE SC: the night return predicts a day reversal in and out of sample (CRUDE-41, abstract).
- Futures broadly:
  - Safari and Schmidhuber 2025 (Physica A, 16 futures markets including crude, 2010-2023): reversion at 2-16
    minutes, and weak trend persistence at 1 hour or more. The out-of-sample R2 is 0.55 bp and 0.020 bp, gross
    (CRUDE-40, full text).
  - Covid-period overreactions and reversals (CRUDE-22, abstract).
  - Chinese commodities: intraday momentum and reversal do not cover costs (CRUDE-44, abstract, negative).
- Excluded: Lalor and Swishchuk, on passive-fill adverse selection (CRUDE-21).

T7, session structure.
- Globex runs Sunday to Friday, 18:00-17:00 ET, with a 60-minute pause (CRUDE-17).
- Settlement is at 2:30 pm ET, from the 2:28-2:30 window (CRUDE-37).
- Jumps cluster at the former pit open (8:55-9:10 ET, 18 of 133 jumps) and close (14:10-14:40 ET, 13 of 133) and at
  the 18:00 open (8). This is volatility only (CRUDE-29).
- Spreads are widest next to the daily pause (CRUDE-48).
- No study of a directional effect at a handoff was found for CL. On USO (CRUDE-19, CRUDE-43) the first half-hour
  after the overnight break predicts the close.

## Searched, not found (details in JSON searched_not_found)

- MCL and QM spread and touch (3 queries).
- A QM program for 2021-2026.
- A post-2016 product-level HFT share outside the CFTC series.
- Intraday crack-spread cointegration.
- MCL-CL and QM-CL price discovery.
- Halova, Kurov and Kucher (2014) full text.
- Intraday OPEC studies.
- Settlement-window or open-handoff directional studies.
- Any CL-specific study after 2010 that is out of sample or net of costs at 5 minutes to the session.

## Gaps

- MCL and QM spread and touch are not sourced.
- CL spread has no time-weighted median, only a 2012-13 volume-weighted statement and Q1-2023 hourly means. The lead
  decides which, if any, becomes S.
- QM against CL price discovery is unknown.
- Several papers were used at abstract, poster or snippet level because the full text was not obtained: Halova et al.
  2014; Ye and Karali (2016 journal version); Geman and Li; Haugom et al. 2025 (embargoed to 2027-02-06); Wen-Gong-Ma-Xu
  2021.
- The Luo and Kang text is a Firecrawl directQuote extraction, not the raw PDF, which sits behind Cloudflare.
- The 2025-12-02 Oil LPP modification filing was not read.
- Wayback: the archive.org availability API returned 429. Direct web.archive.org id_ URLs worked. The CME 2016 deck
  has no capture.
