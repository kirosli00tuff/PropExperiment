# F2_natgas: family facts for MNG, QG, NG (Stage E.32b, step F2)

Worker: NatgasReader-OpusHigh. Started 2026-10-28 22:48 PDT. Facts only: nothing here is scored or ranked.
Machine-readable version: reports/stage_e32b_briefs/F2_natgas.json (56 items). It is built by
work/NATGAS/NATGAS_build.py, which checks every quote against its saved source file (0 mismatches).
New pages are in pages/NATGAS/ and logged in pages/NATGAS/log.tsv (URL, UTC and PDT fetch time, method, sha256). Reused
facts cite reports/stage_e28_briefs/A1_natgas.* (E.28), reports/stage_e20_briefs/product_NG.md (E.20),
reports/stage_e2a_costs.md/.json (E.2a program cost model) and reports/stage_e16_settlement.json (E.16).

Leader: NG for all three codes (same underlying; NG ADV is roughly 40 to 190 times that of MNG or QG, per E.28 F9).

## Underlying-wide facts (Henry Hub natural gas; apply to MNG, QG, NG)

### T2b Market-maker and incentive programs (NG's apply to QG and MNG as their leader's)
- NATGAS-10, -11 (new, full text). The NYMEX Financial Natural Gas Market Maker Program covers HH and NG on CME Globex.
  Its scope text does not limit NG to spreads. Hours 7:00-15:00 CT. Participants must quote two-sided markets at set
  spreads and sizes. Term: "Start date is January 1, 2017. End date is July 31, 2026 July 31, 2027" (Submission
  26-350, filed 2026-07-14). It was in force throughout 2021-2026.
- NATGAS-12 (new). The Henry Hub Strips Liquidity Provider Program covers HH and NG on Globex, 2019-10-01 to
  2024-07-31 (Submission 23-316).
- NATGAS-13 (E.28). The Physical Henry Hub (NG) Market Maker Program covers deferred spreads and strips, 2017-07-01 to
  2024-07-31.
- NATGAS-14, -15 (new; MNG only). The Micro Natural Gas Futures Market Development Program was a volume incentive for
  proprietary trading firms, 2023-11-06 to 2024-01-31 (Submission 23-420).
- QG: no program of its own found.

### T2a Automation; T2c Retail share
- NATGAS-8: the CFTC series gives an NG ATS share of 69.9% (2016-11 to 2018-10) and 63.3% (2014-2016). This is the
  shared source: use F2_shared_cftc_automation.json (RatesReader). No QG or MNG figure exists.
- NATGAS-9: the only other figure found is a generic "about 2/3 of volume is HFT" in an abstract. It is not specific
  to NG and gives no source.
- NATGAS-16: no published retail share. Proxy only: COT nonreportables held 4.7% of NG open interest (2022-11 to
  2023-10).

### T3 Structural relationships
| id | members | type | horizon / evidence |
|---|---|---|---|
| 17 | NG:QG 1:4 spread on Globex since 2024-01-22 | mechanical (mini/full) | listing only; no study |
| 18 | MNG fungible with QG and the penultimate financial contracts | mechanical | clearing only |
| 19, 56 | NG calendar spreads and strips; April/May is the highest-volume NG calendar spread | calendar | spread books with MM programs; daily liquidity paper (CFTC OCE); no intraday study |
| 20 | NG inter-contract statistical arbitrage at HFT speed (Driaunys et al. 2014; Masteika and Vaitonis 2015) | calendar or inter-contract | abstract only; horizon, costs and sample not given |
| 21 | NG and CL | economic | VOLATILITY-only bidirectional causality, 10-minute data from 2003-06 (Rosenman and Wolfe 2014, full text) |
| 22 | NG returns respond to the crude inventory surprise (-0.112) at the release | economic | (-5,+10) minute window, 2003-2017 (Linn et al. 2017, EIA slides) |
| 23 | HH leads TTF | economic, other venue | DAILY Granger causality, 2019-2024 (MDPI Gases) |
| 55 | S&P 500 and NG (plus CL and ethanol) | cross-asset | intraday 2010-2013; linkages "vary"; no NG lead-lag result extracted (Tinbergen DP) |

No minute-level cointegration, mean-reversion or return lead-lag study involving NG was found.

### T4 Scheduled events and how fast prices absorb them
- NATGAS-24: the EIA Weekly Natural Gas Storage Report (WNGSR) is released Thursdays at 10:30 ET (09:30 CT), weekly.
- Absorption evidence: all of it says minutes or less. None documents the mean still moving 5 minutes or more after
  the release.
  - NATGAS-25 (full text). Halova, Kurov and Kucher (2014, JFM), 2003-07 to 2012-06, event window (-5,+10) minutes:
    "The results with longer event windows are similar."
  - NATGAS-26 (full text, EIA workshop slides). Linn et al. (2017), 2003-2017: the "5 to 7 minute response relative to
    level at 100 minutes" is "Similar for Gasoline, Distillate and Natural Gas".
  - NATGAS-27 (abstract only). Brigida and Pratt (2019): traders within the first 50 ms incorporate the report, and
    there is no pre-release informed trading.
  - NATGAS-31 (full text). Farhangdoost and Etienne (2020, AAEA): the 15-minute impact has diminished over time.
- NATGAS-28: volatility stays elevated for up to 30 minutes after the release (Linn and Zhu 2004, pit era).
  VOLATILITY-only.
- NATGAS-29 (E.20 full text). Prokopczuk et al. (2021): the mean return over (-90,+30) minutes on announcement days is
  -0.37%, split pre (-90,-5) -0.18% and post (-5,+30) -0.19%. This is an unconditional sign pattern. The post part
  includes the release itself. After 2011 it is not significant (see T6).
- NATGAS-30 (full text of the executive summary). Ederington et al. (2019): analyst forecasts are priced before the
  release, and storage surprises partly reverse the next week. Daily and weekly horizon. This verifies E.20's E6
  quote, which E.20 had only at secondary level.
- NATGAS-32 (abstract only). Boucher, Gagnon and Power (2025, Energy Journal): 26 US macro releases move NG futures
  ("price drift, volatility, and bid-ask spreads"). The horizon is unknown.
- NATGAS-33 (POINTER): weather-model runs move prices, per trade press. No study exists.

### T6 Intraday directional evidence (5 minutes to the session)
| id | study | venue | product | horizon | data | OOS / costs | finding | level |
|---|---|---|---|---|---|---|---|---|
| 39 | Prokopczuk, Wese Simen, Wichmann 2021 | Energy J. (peer-reviewed) | NG | 120 min around WNGSR | 2003-03..2018-12 | in sample; gross and net | full sample significant; **after 2011 raw 2.91%/yr (p 0.558), net -0.90%**: "do not withstand transaction and funding costs" (NEGATIVE after 2010) | full text (E.20) |
| 40 | Gu and Kurov 2018 | JFM (read in Gu's dissertation) | NG | 85 min before WNGSR | 2008-07..2016-01 | in sample; costs not stated | Sharpe 0.84 (1.26 when the predictor is large); needs analyst forecasts | full text (E.20) |
| 41 | Baltussen et al. 2021 (shared source) | JFE | NG | ROD -> last half-hour (14:00-14:30 ET) | 1993-01..2020-05 | R2OOS 0.92% (positive); gross | beta 3.02 (t 6.15) | full text (E.20; owned by EquityReader) |
| 42 | Lammers 2019 | MSc thesis | >60 futures | ROD -> last 30 min | ~45 years | in sample | positive "everywhere" | abstract |
| 43 | Driaunys et al. 2014; Masteika and Vaitonis 2015 | TBE; LNBIP | NG | HFT stat-arb | n/a | unknown | outperforms (claim) | abstract; probably under 5 minutes |
| 44 | Kamali 2016 | PhD dissertation | NG | spread crossings | n/a | n/a | excluded: order-book horizon | abstract |
| 45 | Jin, Kearney, Li, Yang 2020 | JFM | Chinese commodity futures (not energy) | first -> last half-hour | n/a | strategy beats benchmarks | positive | abstract |
| 46 | Program E.12 / E.18 (unpublished) | program records | NG | h60 bar features | 2010-2019 | n/a | not evidence after Holm; backward replication failed | reused (E.28 F14) |

No NG-specific study after 2010 that is both out of sample and net of costs and positive was found. The one NG-specific
sized result net of costs (39) is negative after 2011.

### T7 Session structure
- NATGAS-47: Globex runs Sun-Fri 17:00-16:00 CT with a daily halt from 16:00 to 17:00 CT. Day session in program use:
  08:00-13:30 CT.
- NATGAS-48: NG settles on Globex from 14:28:00 to 14:30:00 ET (13:28-13:30 CT), first six months (NYMEX 19-198, via
  E.16). No study of returns around this window was found.
- NATGAS-49: documented handoff effect: the last half-hour before the 14:30 ET close is predicted by the rest-of-day
  return (Baltussen et al., the same row as T6 item 41).
- NATGAS-50: U-shaped intraday volatility, high at the open (Linn and Zhu 2004, pit era). VOLATILITY-only.
- NATGAS-51: news during non-trading periods produces overnight returns (Borovkova and Mahakena 2015, abstract).

## Per code

### NG (leader)
- T1 spread: no sourced median. The program-measured time-weighted MEAN quoted spread is 1.25 ticks in the day
  session (08:00-13:30 CT, 5 Wednesdays 2025-05 to 2026-04, E.2a; NATGAS-1); across all hours it is 1.45 ticks. The
  CME figure is "below 1.5 ticks on average" in non-US hours, Q2 2020 (NATGAS-7).
- T1 touch: median displayed size 5 contracts at the bid and the ask in the day session (4-6 by bucket) (NATGAS-4).
- T5: physically delivered at Henry Hub (NATGAS-34). Price discovery evidence:
  - NYMEX led the ICE look-alike on 63% of contract days, against 20% for ICE (2006; CFTC; NATGAS-37).
  - Futures lead spot at the daily horizon (2002-2011; NATGAS-38).
- T2b: has its own programs (NATGAS-10 to -13).

### QG
- T1: mean spread 1.22 QG ticks (QG's tick is $0.005, 5 times NG's in price) (NATGAS-2). Median touch 10 contracts
  (NATGAS-5).
- T5: financially settled. Its Floating Price is NG's final settlement price on QG's last trading day, so it settles
  off a sibling's settlement price (NATGAS-35). No price-discovery study of QG was found.
- T2a and T2b: none of its own. Its leader is NG.

### MNG
- T1: mean spread 2.41 ticks, $1 each (NATGAS-3). Median touch 3 contracts (bid 2 in the 13:00-13:30 CT bucket)
  (NATGAS-6).
- T5: financially settled. Its Floating Price is NG's final settlement price, so it settles off a sibling's settlement
  price (NATGAS-36). No price-discovery study of MNG was found.
- T2b: its own volume incentive program ran 2023-11-06 to 2024-01-31 (NATGAS-14). Its leader NG has the programs
  above.

## F1 changes against E.28 (A1_natgas.json)
- NATGAS-52, MNG `market_maker_or_incentive_programs`: E.28 had "none found". New: the MNG Market Development Program,
  2023-11-06 to 2024-01-31.
- NATGAS-53, NG `market_maker_or_incentive_programs`: E.28 had only the Physical HH program (deferred spreads and
  strips). Added: the Financial NG MM Program (NG on Globex, 2017-01-01 to 2027-07-31) and the HH Strips LPP
  (2019-10-01 to 2024-07-31).
- NATGAS-54, `spread_median_ticks_by_session` and `touch_queue_size`: E.28 had these as u. The program's E.2a
  measurement (which E.28 did not cite) gives mean spreads and median touch sizes.

## Searched, not found (details and queries in the JSON `searched_not_found`)
- A median spread for any code. Newer CME spread or depth figures (the 2026 CME Henry Hub liquidity article has none).
- A post-2018 NG automation share, and any figure for QG or MNG.
- A QG program. A 2024-2026 renewal of the Physical HH program. An MNG program after 2024-01. Asia- or Europe-hours
  energy incentive programs covering NG.
- A retail share.
- Minute-level relationship studies (NG-CL, NG-TTF, calendars, NG:QG).
- Evidence of a WNGSR drift of 5 minutes or more. Gay, Simkins and Turac (2009) was not located.
- Information-share studies for QG or MNG.
- A post-2010 NG intraday directional study that is out of sample and net of costs.
- Returns around the settlement window.

## Gaps and failures
- Means, not medians: the lead decides whether E.2a's mean spread can stand in for S. E.2a's five dates are all EIA
  crude Wednesdays.
- Abstract-only items: Brigida and Pratt (2019), Boucher et al. (2025), Driaunys et al. (2014), Lammers (2019), Jin
  et al. (2020), Kamali (2016). Bjursell et al. (2015) was seen as a title only.
- Blocked or unreachable:
  - hull-repository item 3303156 (Cloudflare 403; content unknown).
  - imf.org (403; a Wayback copy was used).
  - eprints.ucm.es (no response; the Tinbergen copy was used).
  - ageconsearch (202 challenge; a Wayback copy was used).
  - skidmore.edu and iaee.org PDFs (404 live; Wayback copies used).
  - Scrapling refused to save PDF output (it needs .md/.html/.txt names), so it was not used.
- Terms: thesis.eur.nl prohibits text and data mining. Its footer was read after one landing page had been fetched;
  nothing further was fetched from that site. All decisions are in log.tsv.
- Author list: the brief names Baltussen et al. (2021) as "Baltussen, van Bekkum and Da". E.20's on-disk copy reads
  "Baltussen, Da, Lammers, Martens". This is for the lead and EquityReader to reconcile.
- Budget: 23 WebSearch calls of 60. No over-budget notice. OpenAlex: 3 calls.
