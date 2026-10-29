# F2_metals: family reader facts, COMEX metals (MGC, GC, SIL, SI, MHG, HG)

Worker: MetalsReader-OpusHigh (Stage E.32b, step F2). Started 2026-10-28 22:48 PDT, finished 2026-10-28 23:01 PDT
(fetch times in pages/METALS/log.tsv run 05:49Z to 06:01Z). WebSearch: 32 of 70; no budget notice seen. Full-text
T6 reads: 2 new (plus reused E.20 and E.28 files). Facts only: nothing here is scored or ranked.

JSON twin: reports/stage_e32b_briefs/F2_metals.json (58 items). Every quote was checked against its saved file by
work/METALS/METALS_build.py (0 misses; "..." joins separate passages). Pages: pages/METALS/ (log.tsv lists URL,
UTC and PDT times, method, sha256 and note; rows marked NOT USED or FAILED are not evidence). Reused facts cite
reports/stage_e28_briefs/A1_metals.* and reports/stage_e20_briefs/product_GC.json by file and field.
Shared sources were not re-read: CFTC automated-trading reports (RatesReader) and Baltussen et al. 2021 (EquityReader).

## Family-wide facts

- Sessions (T7): Globex Sunday 17:00 CT to Friday 16:00 CT, with a daily 60-minute break 16:00-17:00 CT (METALS-14,
  reused E.28). Settlement windows: GC 13:29-13:30 ET, SI 13:24-13:25 ET, HG 12:59-13:00 ET, each a one-minute VWAP
  (METALS-11, -12, -13; COMEX filing rules0815235374). These are structure only. No study of a price effect at the
  settlement window or at the 17:00 CT reopen was found.
- Macro releases (T4): US 08:30 ET releases (payrolls and durable goods have the largest effect), plus releases at
  09:15 and 10:00 ET. Elder, Miao and Ramchander (JBF 2012), 2002-2008, 5-minute data. Gold and silver respond mostly
  in 08:30-08:35. Copper "exhibits a somewhat delayed response to the 8:30 announcement". After the 09:15 releases
  the peak R-square for gold and silver comes "about a 30-minute delay" later, and silver lags 5-10 minutes after the
  10:00 releases. The response "tends to dissipate in less than an hour" (METALS-23). The volatility effect decays
  within about 10 minutes (METALS-24, volatility-only). Gold and FOMC: Awartani et al. (IRFA 2024), GC 2007-2020. The
  adjustment 10 minutes after the shock is "significantly threefold higher than after 5 minutes" (METALS-25). Smales
  and Yang 2015 put the gold reaction mostly within 90 seconds (METALS-26), but that item is secondary-only (snippet
  level, from E.20).
- No weekly product-specific report exists for the metals (E.28 F10). Copper's response to China data: no study found.

## GC (leader of gold) and MGC (satellite)

- T1 spread. GC averaged 1.39 ticks top-of-book across all hours in Q1 2023 (most active month; CME whitepaper
  Table 3). Over SGT 21:00-01:00 (ET 08:00-13:00) the hourly averages were 1.31-1.35 (METALS-49). An older CME
  article (2017-Q1 2018) says "one tick during almost all trading hours" (METALS-1). Both figures are averages or
  descriptions, not medians. MGC: none published.
- T1 touch size. GC averaged 6.76 lots at the best bid/ask in Q1 2023, with US-hours hourly averages of 6.8-8.4
  (METALS-51). Earlier figures: 15-24 lots in Asia hours (2017-18) and a 2010 level-1 median of 4.62 (METALS-3).
  MGC: none published.
- T2b programs. GC and SI are covered by the Globex Precious Metals Volume Incentive Program, 2018-02-01 to
  2026-01-31 (METALS-15, -16). The Sovereign Wealth Fund Incentive Program gives a 20% fee discount on Gold Futures
  and Copper Futures from 2026-08-17 (METALS-17). MGC has only a futures market-maker program from 2010-2012 and an
  options market-maker program from 2023 (METALS-20). This is an F1 change: E.28 had no program for GC (METALS-54).
- T2c retail. No share of volume is published, only "+17% YoY" retail participation in GC in 2023 (METALS-45).
- T3. MGC and GC form a mechanical pair: MGC settles to GC's price (METALS-38). Calendar spreads exist (METALS-41).
  Gold-silver: silver leads gold at 1-minute frequency in CME futures, 2007-2012, in a master's thesis, in sample
  (METALS-37).
- T5. GC is physically delivered. MGC is also physically delivered (ACE certificates), but its daily and final
  settlement prices come from GC's (METALS-5, -6). Price discovery: COMEX futures lead London spot. The ILS is about
  66% after 2007, and after Globex the "US futures [take] a consistent lead irrespective of market hours" (Hauptfleisch,
  Putnins and Lucey, JFM 2016, 1997-2014; METALS-21).
- T6 directional evidence:
  - METALS-27: Baltussen et al. JFE 2021 GC row, from E.20's extract. Rest-of-day return predicts the last half hour
    (12:00-12:30 CT), beta 1.09 (t 2.95), R2_OOS 0.08%, significant at 5%. Data 1984-2020, gross. Peer-reviewed, out
    of sample, same product. The shared reader owns the full reading.
  - METALS-28 (negative/decay): the PM-fix drop and hat-shaped pattern are significant only in 2007-2011. CBS thesis.
  - METALS-29 (negative): broker gold data, contrarian rule not significant, gross. Other venue.
  - METALS-30: overreaction contrarian on GC, SI and HG, 2019-2020. Turning points are defined ex post.
  - METALS-31 (abstract): COMEX gold day returns are negative and overnight returns positive, 1985-2012. The authors
    say "economically important even with transaction costs".
  - METALS-32 (abstract): gold rises after extreme negative 5-minute S&P 500 moves.
  - Excluded: METALS-57 (1-minute variance ratio) and METALS-58 (daily horizon).
- T7. The LBMA gold auction runs at 10:30 and 15:00 London. Since the 2015 reform there is no significant leakage
  before the fix, and price discovery finishes within minutes (METALS-35). The hat-shaped 24-hour pattern, rising in
  Asia and falling in the West, is documented in METALS-36 (thesis; significant mainly 2007-2011).

## SI (leader of silver) and SIL (satellite)

- T1. SI spread: "one tick wide most of the hours" (2017-18). Touch size: 22-27 lots in Asia hours, and a 2010
  level-1 median of 6.56 (METALS-2, -4). SI is not in the 2023 whitepaper. SIL: none published.
- T2b. SI has the Precious Metals Volume Incentive Program (METALS-15). SIL has the Korea Retail FCM rebate,
  2022-11-01 to 2028-07-31, a volume rebate rather than quoting (METALS-19). No SIL futures quoting program was found.
- T3. SIL and SI form a mechanical pair (METALS-39). Silver leads gold at 1-minute frequency (thesis, METALS-37).
- T5. SI is physically delivered. SIL is delivered through ACE certificates, and its daily settlement is derived
  from SI's (METALS-7).
- T6 and T7. Before 2014, COMEX silver futures and spot showed a 10-12 bp downward bias around the noon London silver
  fixing, with prices suppressed about 10 minutes either side of the fix start, over 2000-2013 (Caminschi, UWA working
  paper 2014, marked "do not cite without permission"; METALS-43, -44). The fixing was replaced by an auction in 2014.
  A later study reports lower futures predictability after the reform, but that is snippet only. SHFE gold and silver
  (other venue): first-half-hour predictability moved from the day session to the night session (GFJ 2025, abstract;
  METALS-46, -34).

## HG (leader of copper) and MHG (satellite)

- T1. HG averaged 1.55 ticks across all hours in Q1 2023. US-hours hourly averages were 1.38-1.45 (median 1.44)
  (METALS-50). Touch size averaged 5.35 lots, with US-hours hourly averages of 6.4-7.1 (METALS-52). This is an F1 change:
  E.28 had null (METALS-56). MHG: none published.
- T2b. HG has the Globex Base Metals Volume Incentive Program, 2018-02-01 to 2026-01-31 (METALS-47, -48; F1 change
  METALS-55), and the SWF incentive from 2026-08 (METALS-17). MHG had the Micro Copper Market Development Program with
  quoting obligations, 2022-05-01 to 2025-01-31 (METALS-18).
- T3. MHG and HG form a mechanical pair; MHG is aggregated with QC for position limits (METALS-40). COMEX, LME and
  SHFE are a cross-venue relation documented at daily horizons only (METALS-42).
- T5. HG is physically delivered (METALS-10). MHG is financially settled: its final settlement price is HG's
  settlement price on the 3rd last business day of the prior month, and its daily settlement equals HG's (METALS-8,
  -9). Price discovery: "Comex, followed by the SHFE, not the LME" leads copper (2001-2013, daily data;
  Figuerola-Ferretti, Gilbert and Yan 2014; METALS-22).
- T6. SHFE copper (other venue): the first half-hour predicts the last half-hour, 2002-2013, gross, in sample (Jin
  et al. JFM 2020, read from the MPRA working-paper version; METALS-33). No COMEX copper intraday directional study
  was found.

## Searched, not found (details and queries in the JSON)

- T1: no spread or touch size for MGC, SIL or MHG. No SI figure newer than 2017-18. The RFS 2012 commodity
  liquidity paper's full text was not reachable.
- T2a: no non-CFTC automated or HFT share for any metals code (CFTC figures are the shared file's).
- T2b: no MGC or SIL outright-futures quoting program in 2021-2026. Copper results were options programs (not in
  scope). The 2026 weekend programs cover 1OZ and SIC only (snippet).
- T2c: no retail share of volume.
- T3: no peer-reviewed intraday gold-silver or gold-copper study; no calendar-spread mean-reversion study.
- T4: no study of copper and China data. Kurov et al. pre-announcement drift does not include gold (snippet).
- T6: no COMEX silver or copper study at 5 minutes or more apart from the multi-asset shared source.
- T7: no study of a settlement-window or Globex-reopen effect.

## Gaps and route failures

- The GC and HG spreads are hourly averages, not medians (the spec asks for a median). The 2017-18 GC and SI
  figure ("one tick") is descriptive.
- Cloudflare challenges blocked acfr.aut.ac.nz (Zhou et al.; Aspris et al. silver reform) and
  hull-repository.worktribe.com (published Jin et al.). The curl results were deleted and logged as FAILED.
  Scrapling fetch on Hull also failed; it was tried after a robots/Content-Signal check, logged. Firecrawl was not
  used.
- The Smales and Yang 2015 90-second figure remains secondary-only.
