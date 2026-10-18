# R6: scheduled-event microstructure not yet tested (Stage E.25, research only)

Reader: R6-SchedEvents-OpusHigh. Started 2026-10-18 01:38 PDT; cut by the usage limit at about 01:59 PDT; resumed 06:21 PDT (planner window
change: work to 09:00 PDT). Status: FINAL (finished about 07:00 PDT). Times PDT; fetch-log times UTC.

## 0. What is already a trial (index check, done first)

Sources grepped: reports/stage_e25_briefs/r0_mechanism_index.md (keywords "release-minute momentum",
section 1, 3, 5, 6, 17), reports/stage_e23_briefs/inventory/{K1,K2,K4,K5,CDE}.md.

| id | what it tested | instrument | window (CT) |
|---|---|---|---|
| E-H1 | pre-release overnight drift on FOMC / CPI / NFP dates (first bar to release) | MES | ~17:00 d-1 to 07:30 (CPI/NFP) or 13:00 (FOMC) |
| E-H2 | post-release momentum: 5-min reaction range > 2.0x baseline, follow for 10 min (CPI, NFP, FOMC statement) | MES | 07:35-07:45; 13:05-13:15 |
| K5-fomc-01 | FOMC statement: sign of close(13:04)-close(12:59), momentum 13:05-13:15 | MGC (GC) | 13:05-13:15 |
| K2-fomcpost-01 | FOMC statement date: unconditional BUY 13:29-15:04 | ZT ZF ZN TN ZB UB | 13:29-15:04 |
| K2-predrift-01 | ISM Services (09:00 CT): sign 08:30-08:49, momentum to 09:04 | ZN, ZB | 08:49-09:04 |
| K4 WPSR / NGS members | EIA crude and gas inventory releases (pre, fade, momentum) | MCL, NG | various |
| Gate 0 g13-g15, k9_anncday | ML features minutes-to-release, minutes-since-release, release-day dummy at fixed decision times | all K roots | t1/t2/t3 |
| K9-anncday-01 | announcement-day premium, long MNQ/M2K/MYM: draft only, NOT a trial | - | - |

Engine-side only (not members): K1 members read FOMC/ISM/NFP/CPI instants only for fill guards and event-window cost
(K1.md: "No member reads a release").

So NOT yet tested: (a) any NQ/MNQ, ES-full, ZN, CL or GC member keyed to CPI, NFP, retail sales, PCE, GDP, ISM
Manufacturing, jobless claims or Treasury refunding; (b) the FOMC press-conference window (14:30 ET onward)
on equity index; (c) post-release horizons beyond 10 minutes on equity index and any post-release reversal
(5-30 min fade) on any root other than MCL WPSR (K4-eiafade-01); (d) pre-release positioning before 10:00 ET
releases on equity index (K2-predrift-01 covered ISM Services on ZN/ZB only).

Topstep Tier 1 window (R9 E01-E03, help article 13613539, dateModified 2026-10-16; read from
pages/R9/ts_13613539.html, sha256 c3968edb2ef9d18f): "Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening
transactions permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after).
Micros (MES, M2K, MYM, MNQ, MGC): Opening transactions limited to 1, 3, 6, 9, and 15 contracts for the $25K, $50K,
$100K, $150K, and $250K account sizes"; "Other products (energies, rates, FX, etc.) are unaffected."; "Pending orders
... will not fill during the 10-minute window, and new pending orders intended to execute during this timeframe
cannot be placed. TP/SL brackets that are reducing/closing positions will be accepted during the window." Windows
(CT): "CPI 7:30 AM 7:25 to 7:35 AM FOMC rate decision 1:00 PM 12:55 to 1:05 PM FOMC press conference 1:30 PM 1:25 to
1:35 PM Non Farm Payroll (NFP/Unemployment Rate) 7:30 AM 7:25 to 7:35 AM". The list says "for example, CPI, FOMC,
NFP"; retail sales, PCE, GDP, ISM, claims and refunding are not named. Applied per candidate below and in section 6.

## 1. Answer (at most 250 words)

The index check (section 0) leaves untested: FOMC press-conference and post-statement windows on equity index,
any NQ/ES/ZN/CL/GC member keyed to CPI, NFP, retail sales, PCE, GDP, ISM Manufacturing, claims or refunding,
and post-release fades except MCL WPSR. Six candidates, all on owned data plus free calendars; all are
pointers, not strong evidence. The best-documented are three FOMC-day equity-index
choices on the same about 8 events a year. C3, the Baglioni-Ribeiro pre-announcement reversal (thesis), reports
23.34 bp per event net of spread on 71 events from 2011 to 2020, but nothing after January 2020 has tested it.
C1 fades the statement move during the Chair press conference. Its sign is regime-dependent: it reinforced
the statement move from 2011 to 2020 and reversed it only after COVID (Narain-Sangani, IJCB 2026, n of about 16).
C2, the Boguth et al. post-statement reversal, has no published same-day share. C4-C6 are weak (RV-inferred CL fade;
release-day filter on a failed mechanism; pre-release drift ending 2014). The 08:30 ET releases leave nothing to trade after about 5 minutes. CEA (2021-2023) finds ES and
ZN responses "very close to zero" after the first 5-minute interval. Boguth et al. (2023) find "Significant price
reversals are a unique feature of equity returns on FOMC announcement dates". Topstep's Tier 1 window (minis
blocked, micros capped, pending orders unfilled, 5 min either side of CPI, NFP, FOMC decision and press
conference) moves C1's entry to 13:36 CT. It does not touch C2-C6 entries or CL/ZN.

## 2. Candidate hypotheses

### R6-C1 FOMC press-conference fade on equity index (NQ/MNQ, ES/MES)

- Hypothesis: on FOMC statement days with a Chair press conference, take the side opposite to the
  index move over the statement window (13:00-13:30 CT, i.e. 14:00-14:30 ET), enter at the press-conference
  start (13:30 CT) and exit at its end (about 14:15-14:30 CT). Mechanism (Narain and Sangani, IJCB 2026):
  since COVID, and more so since the March 2022 tightening cycle, Powell's Q&A has moved markets opposite
  to the statement reaction; under Bernanke and Yellen the press conference reinforced it.
- Published effect: SPY return over press conference regressed on SPY return in the 30-min statement window:
  Powell post-COVID slope -0.694 (s.e. 0.253); Powell post-COVID tightening slope -0.752 (s.e. 0.282);
  N = 73 press conferences (Apr 2011 - Mar 2024), R2 0.16 (Table A.6). Correlation 0.45 (pre-COVID)
  -> -0.07 (post-COVID pre-tightening) -> -0.48 (after March 2022). Statement-window squared SPY return,
  Powell: 0.220 + 0.048 = 0.268 (%^2), i.e. RMS about 0.52% (Table 1); press-conference SPY return sd 0.723%,
  min -2.583%, max 1.782% (summary statistics table).
- Conversion (inputs for the lead, not a ratio): an expected fade of |beta| x |statement move|. With
  beta = -0.752 and a typical |statement move| of about 0.4% (mean absolute value of a normal with RMS 0.52%
  is about 0.8 x 0.52% = 0.41%; my approximation, not a published number; the published statement-window
  SPY sd over all 73 press conferences is 0.511%, mean 0.085% (Table A.2: "SPY Return: Statement Release (%) NYSE
  TAQ 0.085 0.511 -1.421 1.192"), consistent with it): 0.752 x 0.41% = 0.31% of the index.
  NQ at 21,000: 0.31% x 21,000 = 65 NQ points = 260 MNQ ticks. ES at 6,000: 0.31% x 6,000 = 18.6 ES points
  = 74 MES ticks. Per-trade sd is of the same order (0.72% of SPY), N post-2022 about 16 conferences.
- Contrary evidence on the SAME mechanism: Gomez-Cram and Grotteria (JFE 2022), 2011-2020: "Strong positive
  correlation between price changes around the statement release and the subsequent press conference ...
  44% for SPY". The sign flipped across regimes; this is a regime-dependent, low-n effect.
- Prop: press conference ends before 15:10 CT (2023-2024 conferences ended 15:14-15:23 ET = 14:14-14:23 CT,
  IJCB Table A.1, e.g. "Mar. 20, 2024 Jerome Powell ... 14:00 14:30 15:17"); about 8 events a year. TIER 1
  WINDOW BINDS: 13:30 CT entry is inside the press-conference window 13:25-13:35 CT, so NQ/ES cannot be opened
  and MNQ/MES opening is capped at 1/3/6/9/15 contracts (25K-250K); a resting order placed for 13:30 will not fill.
  Prop-compatible form: market entry on MNQ/MES at 13:36 CT (first minute after the window), losing the first
  6 minutes of the published press-conference window (the published return is start-to-end; the share in the
  first 6 minutes is not published). P06 still applies on top. No HFT; 1-minute decision.
- Data: owned (1-minute NQ/ES/MES bars, FOMC calendar incl. 2025-04..2026-06, about 11 meetings in the
  research window; press-conference start 14:30 ET is fixed; end time varies 40-60 min, a fixed exit such
  as 14:20 CT avoids needing transcripts).
- Overlap: E-H2 (MES, momentum 13:05-13:15 after the statement, opposite sign and different window);
  K5-fomc-01 (MGC momentum 13:05-13:15); K2-fomcpost-01 (rates, unconditional buy 13:29-15:04). No member
  conditions the 13:30-14:30 CT window on the statement-window move.

### R6-C2 FOMC post-statement price-pressure reversal (fade the 13:10-13:50 CT move, exit 15:05 CT)

- Hypothesis: on FOMC days with a press conference, the E-mini move from 10 to 50 minutes after the
  14:00 ET statement reverses; fade it from 13:50 CT to the 15:05 CT flatten.
- Source: Boguth, Gregoire, Martineau, "Price Pressure and Efficiency on FOMC Announcements" (draft 28 Jun
  2019; later "Noisy FOMC Returns? Information, Price Pressure, and Post-Announcement Reversals", with
  A. Fisher, NFA 2022 best asset-pricing paper, R&R RFS per search results [secondary-only for status]).
  E-mini 1997-2017; reversal regression for press-conference meetings (Table 1 note: sample from April 2011).
- Quotes: "returns from the 10th to the 60th minute following announcements predicts a substantial price
  reversal of about 60 basis points that can last several hours until the next trading day. For
  announcements with no press conferences, we find no price reversal." (p. 3-4). "The coefficient exceeds
  -2 ... The mean absolute returns during this period in our sample is 28 basis points. Therefore, our model
  predicts a reversal of over 56 basis points between between 50 minutes after the announcement and the
  end of the next trading day. The R2 t at t = 50 indicates that 40% of the variation in future returns is
  related to temporary deviation from efficient pricing." (p. 19).
- Conversion: 56 bp is to the NEXT-DAY settlement (includes overnight, not prop-compatible as published).
  Upper bound for the intraday part: 56 bp x 6,000 / 10,000 = 33.6 ES points = 134 MES ticks; on NQ (if the
  same % held; NQ not studied) 56 bp x 21,000 / 10,000 = 117.6 NQ points = 470 MNQ ticks. The same-day
  share (13:50-15:05 CT) is NOT published; the lead should treat the intraday gross as unknown.
- 2025 abstract (vincentgregoire.com): "Standard predictive regressions confirm significant reversal of
  event-window returns by announcement-cycle end" -- the published horizon moved to the announcement
  cycle (weeks), which weakens the intraday reading.
- Prop: exit 15:05 CT < 15:10 CT; entry 50 min after the statement (13:50 CT), outside both Tier 1 windows
  (12:55-13:05 and 13:25-13:35 CT), so minis and micros are unrestricted at entry; during the press conference
  (P06: scheduled major event in progress; keep below plan maximum). 8 events a year.
- Later version (Boguth, Fisher, Gregoire, Martineau, "Price Informativeness and FOMC Return Reversals", 5 Mar
  2023, OSF): the reversal tested there is daily, days [0,3] to [4,20]: "Column (4) and (6) report a price reversal
  of 80 and 85 bps for FOMC announcements with press conference and with large monetary policy surprises" (s. 4,
  p. 25); the intraday result kept is only "the raw dR2 are negative, ranging from -0.003 to -0.012, implying
  that stock market returns in the intraday pre-announcement and announcement windows are reversed by later
  returns" (p. 14). So the 2019 intraday 56 bp figure is not carried into the later versions as an intraday number.
- Data: owned (1-minute ES/MES/NQ bars, FOMC calendar). Research window holds about 10 FOMC meetings.
- Overlap: E-H2 (MES momentum 13:05-13:15), K5-fomc-01 (MGC momentum 13:05-13:15), K2-fomcpost-01 (rates
  unconditional buy 13:29-15:04). None fades the 13:10-13:50 move. Shares FOMC dates with R6-C1 and R6-C3:
  C1, C2, C3 are three conditioning choices on the same ~8 events a year, not independent hypotheses.

### R6-C3 FOMC pre-announcement reversal (Baglioni and Ribeiro): fade the prior-24h return, 12:50-14:50 CT

- Hypothesis: if the E-mini return over the 24 hours to 13:50 ET (12:50 CT) on an FOMC day is negative
  (positive), buy (sell) at 12:50 CT and close at 14:50 CT (15:50 ET).
- Source: Baglioni, T. (2023), Essays in Financial Economics, PhD thesis, Insper, ch. 1 "The FOMC
  Announcement Reversal" (with R. M. Ribeiro). E.13 read only the abstract (I-56b); this is the full text.
- Quotes: Table 1.2 Panel A, 09/1997-01/2020: "Reversal From 1:50 p.m. FOMCt to 3:50 p.m. FOMCt 180 17.86***
  1.02" (events, return in bp per event, annualized Sharpe). Table 1.9 Panel A, post-Lucca-Moench
  04/2011-01/2020: "Reversal From 1:50 p.m. FOMCt to 3:50 p.m. FOMCt 71 23.34*** 1.60". Note: "Each strategy
  is implemented buying at the ask price and selling at the bid price" (net of the spread, no commission).
  Regression: "A 1% return in the pre-announcement interval implies 23 basis points (bps) of negative return
  in the post-announcement interval." (p. 9).
- Conversion: 23.34 bp x 6,000 / 10,000 = 14.0 ES points = 56 MES ticks (net of spread); on NQ (not studied)
  23.34 bp x 21,000 / 10,000 = 49.0 NQ points = 196 MNQ ticks. Sharpe convention (footnote 11, p. 13; the
  square-root signs are displaced in the PDF text layer): "Daily Sharpe ratios are computed standardizing the
  [sqrt] Sharpe ratio of the intraday trading strategies to reflect one trading day (6.5 hours of trading) by
  multiplying it by [sqrt] 6.5, and dividing it by the square root of the number of hours in which the position is
  open in the trading strategy (2 hours for the case of Reversal ...). Annualized Sharpe ratios are computed
  multipliyng the daily Sharpe ratio by [sqrt] 8 (the number of FOMC meetings per year)." My derivation (lead to
  verify): raw per-event Sharpe = 1.60 / sqrt(8) / sqrt(6.5/2) = 0.31 (post-2011; implied per-event sd about
  23.34 / 0.31 = 74 bp); full sample 1.02 / sqrt(8) / sqrt(3.25) = 0.20 (sd about 89 bp).
- Decay: sample ends January 2020; no post-2020 test found. Lucca-Moench drift itself disappeared after
  2015 (Kurov, Wolfe, Gilbert 2021), while this reversal strengthened post-2011 in the thesis.
- Prop: flat 14:50 CT; P06 binds HARD: the entry is 10 minutes BEFORE the 14:00 ET statement, i.e. a
  position held into a scheduled major release, which Topstep forbids at full maximum position size.
  Must run at reduced size. Tier 1: entry 12:50 CT is 5 minutes before the 12:55-13:05 CT window, so the
  position is opened outside it; holding an existing position through the window is not restricted for equity
  index in the article (its "Existing Positions" sentence names energies and metals only; the lead should treat
  equity-index holds through the window as allowed but unconfirmed). The exit 14:50 CT is outside all windows.
  8 events a year.
- Data: owned. Signal needs the 24-hour return to 12:50 CT (overnight bars, owned).
- Overlap: E-H1 (MES, long from ~17:00 CT into the 13:00 CT FOMC release: the drift leg, opposite
  logic and before the release); K9 pre-FOMC drift (excluded on frequency, P-04, never a trial). The
  reversal leg itself was never a trial.

### R6-C4 Crude oil fade of the first 5-minute move after 08:30 ET NFP / retail sales (weak evidence)

- Hypothesis: on NFP and advance retail sales days, fade the CL move over 07:30-07:35 CT, hold to 08:00 CT.
- Source: Chatrath, Miao, Ramchander (and co-author), "Does the price of crude oil respond to macroeconomic
  news?", J. Futures Markets 32(6) 2012, 536-559 (author manuscript, Colorado State repository). NYMEX CL
  5-minute returns 2005-2009, about 60 events per announcement.
- Quotes: Table 5, "Change in Nonfarm Payrolls 0.2852a ( 5.01) ... 59"; "Advanced Retail Sales 0.1433a ( 4.44)
  ... 60" (5-minute response, percent per one-sd surprise). Text p. 22-23: "It appears that the majority of
  the response is reversed for most of the macro indicators within just 10 minutes of the announcements ...
  It appears that all of the price response for all the announcements is reversed within thirty minutes."
  Abstract: "The initial (intraday) response in energy prices to macro news appears to be the result of
  noise trading."
- CAUTION: the "reversal" is inferred from realized volatility over 0-10 and 0-30 minutes no longer
  differing from control days (Table 6), not from a signed return regression; a diluted RV test cannot
  show reversal. Treat as a pointer to a testable fade, not as a measured fade return.
- Conversion (upper bound if the 5-minute response fully reversed): 0.2852% x $65 = $0.185/bbl = 18.5 MCL
  ticks (MCL tick $0.01) per one-sd surprise; mean |surprise| is about 0.8 sd, so about 15 MCL ticks.
  Gross unknown; dispersion not published for the fade.
- Prop: 07:35-08:00 CT entry after the release (P06: the position is opened after the release, not held
  into it; allowed). Tier 1: CL/MCL are energies, "unaffected"; the NFP window 07:25-07:35 CT would not bind CL
  anyway, and retail sales is not a named Tier 1 event. Flat long before 15:10 CT. About 24 events a year.
- Data: owned (CL/MCL 1-minute bars; NFP calendar; retail sales calendar NOT in the owned list in brief
  section 4: needs a free BLS/Census schedule build).
- Overlap: K4-eiafade-01 (MCL fade after WPSR, an EIA release, 14-min move): same fade logic, different
  release family. No member trades CL on BLS/Census releases.

### R6-C5 Equity first-half-hour -> last-half-hour momentum on CPI / GDP release days (NQ)

- Source: Gao, Han, Li, Zhou (JFE 2018; WP 2015 on disk, E.20 shared), Table 8 Panel B, SPY 1993-2013:
  "Release CPI 18.03*** 5.80 3.11" vs "Non-Release CPI 6.10*** 6.21 0.98"; "Release GDP 14.40** 6.14 2.35";
  "Release MCSI 19.09*** 4.94 3.86" (annualized % = per-trade x 252, as stated: "we still annualize the
  returns multiplying by a factor of 252 because we only trade once per day").
- Conversion: CPI days 18.03 / 252 = 0.0716% per trade; NQ at 21,000: 15.0 NQ points = 60 MNQ ticks; ES at
  6,000: 4.3 ES points = 17 MES ticks. GDP 14.40 / 252 = 0.057% -> 12.0 NQ points = 48 MNQ ticks.
- Strongest negative: the program's own E20H6-T1 (rest-of-day -> last half-hour, NQ, unconditional) realized
  gross 1.25 MNQ ticks vs 4.08 cost although the same paper family published about 2.5 bp unconditional
  (6.24%/252); the release-day split is about 12 events a year per release and was never run.
- Prop: 14:30-15:00 CT position, flat by 15:00 CT; the release is at 07:30 CT, so nothing is held into it
  (P06 not triggered); Tier 1 not triggered (14:30 CT is outside every window). The signal reads the 08:30-09:00
  ET first half-hour (07:30-08:00 CT), which overlaps the CPI window, but no position is opened then.
  Data owned (NQ bars, CPI/GDP calendars).
- Overlap: E20H6-T1..T3 (same mechanism, all days), K1-cp1-01 (morning-sign -> last half-hour, MNQ/M2K/MYM,
  all days). The only new element is the release-day conditioning; the lead may judge it a filter on a failed
  mechanism (E20H6-T2 already tried a large-move filter).

### R6-C6 Pre-release drift into 10:00 ET releases on ES/NQ (ISM Manufacturing, home sales, consumer confidence)

- Source: Kurov, Sancetta, Strasser, Wolfe, ECB WP 1901 (2016) / JFQA 54 (2019), on disk from E.20
  (reports/stage_e20_briefs/pages/ZN/kssw_ecbwp1901.pdf.txt, re-used, not refetched). ES and ZN second data
  2008-01..2014-03.
- Quotes: Table 3 [t-30min, t-5sec], ES gamma (percent per one-sd surprise): "ISM Non-manufacturing 0.139
  (0.030)***", "Pending home sales 0.154 (0.083)*", "ISM Manufacturing 0.091 (0.036)**", "Existing home sales
  0.113 (0.040)***", "GDP preliminary 0.146 (0.068)**"; "The ratio Gamma m ranges from 15 percent in the CB
  Consumer Confidence Index up to 69 percent in the ISM Non-Manufacturing Index ... The mean ratio across all
  seven announcements and both markets is 44 percent." Profits in the paper require the surprise sign: "the
  average profit per announcement release in the E-mini S&P 500 futures market is about $262,000".
- Tradable form (proposal): sign of the T-30 to T-5 move, held to T+5. Not published as such; the paper's
  profits condition on the realized surprise (ex post), so the tradable gross is unknown.
- Conversion of the drift size: ISM Mfg 0.091% per one-sd surprise x 6,000 = 5.5 ES points (22 MES ticks);
  NQ (not studied) 0.091% x 21,000 = 19 NQ points (76 MNQ ticks). Only the share of days on which the
  pre-move has the right sign earns this.
- Decay: sample ends 2014; information leakage channels (early data access) were the paper's mechanism and
  were partly closed since (paper discusses Reuters/ISM early releases); no post-2014 test found.
- Prop: P06 binds: holding into the 09:00 CT release at full size is barred; reduced size. Tier 1: ISM
  Manufacturing, home sales and consumer confidence are not named Tier 1 events (the list says "for example,
  CPI, FOMC, NFP"; whether Topstep adds others by email/banner is not stated as a fixed list).
- Overlap: K2-predrift-01 (ISM Services, ZN/ZB, same tradable form): Tier B with E.3 t -0.429 (ZN) and
  -1.241 (ZB) in the research window, i.e. the same mechanism on rates did not show. ES/NQ and the other
  10:00 ET releases were never members.

### Considered and NOT proposed (zero candidates, with the reason)

- CPI / NFP / retail sales / jobless claims post-release continuation (5-60 min) on NQ, ES, ZN: the
  evidence says adjustment is complete within about a minute and the price then stays put (Pinchuk 2022;
  Winkelmann-Yao 2026; Chordia-Green-Kottimukkalur 2018 [secondary-only]); E-H2 (MES 10-min momentum) already
  failed. No published post-release drift at 5-60 min on these releases was found.
- CPI / NFP reversal at 5-30 min on equity index: Winkelmann-Yao find overshooting on circuit-breaker CPI
  days, but only inside the first minute (rejections fall to zero for windows of 2 minutes or more); Kroner
  (FEDS 2025-022) finds overreaction only "in the first days following CPI releases" (multi-day, not
  prop-compatible). Pinchuk notes partial reversal only after the most positive surprises (figure only, no
  number). Nothing sized at an intraday horizon.
- Pre-release positioning before CPI / NFP / retail sales / claims: Kurov et al. Table 3 shows no
  surprise-signed drift (CPI gamma -0.005, NFP 0.040*, retail sales 0.009, claims -0.009 for ES). An
  unconditional pre-release intercept is "significant only for ... Initial Claims ... in the stock market, CPI
  announcement in the bond market, and Non-Farm Employment announcement in both markets", but its size and
  sign are not printed; E-H1 tested pre-release drift on MES for CPI/NFP dates (overnight). Pointer only.
- GC (gold) on macro releases: Elder-Miao-Ramchander (JBF 2012): "the response tends to dissipate in less
  than an hour", efficient at 5 minutes; K5-fomc-01 (FOMC gold momentum) null. No candidate.
- Treasury quarterly refunding (QRA, 08:30 ET Wednesdays, 4 a year): Hartley-Rigon (Hoover WP 26112, 2026)
  measure yield effects of supply SURPRISES against primary-dealer expectations in "a tight intraday window";
  the sign needs the dealer-survey expectation (not owned) and n = 4/year. No candidate.
- FOMC minutes (14:00 ET, 3 weeks after): Narain-Sangani Table A.3 squared 10-min SPY return 0.040 (vs 0.278
  CPI); small. PCE, GDP, ISM: no sized intraday drift or reversal found beyond C5/C6.
- Volatility-scaled breakouts after releases: no academic or audited source found; practitioner material is
  R10's (Zarattini / Concretum) and R11's (communities) remit.
- ZN (and ES) after 08:30 ET releases, 2021-2023: rates are outside Topstep's Tier 1 restriction, so a ZN
  release-minute member would be prop-feasible; but the newest sized evidence found (CEA for OMB, Feb 2024,
  ZT/ZN/ES futures, Jan 2021-Nov 2023, 5-min intervals to 60 min) says "after the first five-minute interval, the
  estimates are very close to zero and not significantly different from zero". The first-5-min response (4-5 bp
  per unit surprise for ES and ZN) needs consensus data (not owned) and is earned in seconds ("the primary response
  ... occurs within the first 3-4 seconds", citing earlier studies), i.e. HFT territory. No candidate.
- CPI / NFP / GDP reversal at daily horizons on equity: Boguth-Fisher-Gregoire-Martineau (2023): "For all three
  announcement types the excess dR2 are positive on the announcement date, indicating heightened price
  informativeness ... Significant price reversals are a unique feature of equity returns on FOMC announcement
  dates" (p. 19); on FOMC dates "the prices of two year Treasuries, Fed funds futures, and Eurodollar
  futures do not show reversals" (p. 4). No candidate.
- CL on BLS releases after 2012: one more search (2026-10-18 06:25 PDT) found only volatility rankings (Faseli
  2019/2020, WTI 2012-2018, TU Wien repository) and jump studies (Luo and Kang, NFP triggers CL jumps), no signed
  post-release return. Search-result pointers only, not fetched; nothing sized. R6-C4 stays the only CL item.

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| Powell post-COVID press conference reverses statement move | slope -0.694 (0.253); tightening -0.752 (0.282); N 73 | "Powell (Post-COVID, Tightening) x Returns around Statement -0.752** (0.282)" | Table A.6 | Narain, Sangani, The Market Impact of Fed Communications: The Role of the Press Conference, IJCB (forthcoming; v22n1 Jan 2026), https://www.ijcb.org/sites/default/files/ijcb-vn-market-impact-fed-communications-role-press-conference.pdf | peer-reviewed | pages/R6/ijcb_market_impact_fed_press_conf.pdf |
| correlation statement vs press-conference move by subperiod | 0.45 -> -0.07 -> -0.48 | "the correlation between market reactions to the FOMC statement and to the press conference falls from 0.45 to -0.07 after March 2020 ... (yielding a correlation of -0.48 during the subperiod of Chair Powell's term after March 2022)" | s. 4.2, p. 22 | same | peer-reviewed | same |
| press-conference SPY return dispersion | sd 0.723%, min -2.583, max 1.782 | "SPY Return: Press Conference (%) NYSE TAQ 0.091 0.723 -2.583 1.782" | summary statistics table (appendix) | same | peer-reviewed | same |
| statement-window squared return (Powell) | 0.220 + 0.048 | "FOMC Statement Release (30-Min. Window) 0.220** (0.065) 0.048 (0.096)" | Table 1 | same | peer-reviewed | same |
| 2011-2020 press conference REINFORCED the statement | 44% (SPY) | "Strong positive correlation between price changes around the statement release and the subsequent press conference ... 44% for SPY" | slides p. "Empirical contribution" | Gomez-Cram, Grotteria, Real-time price discovery via verbal communication, JFE 143(3) 2022; CEMLA slides Oct 2020 | working-paper (slides of a peer-reviewed paper) [secondary-only for the JFE text] | pages/R6/cemla_gomezcram_grotteria_slides.pdf |
| post-FOMC price-pressure reversal (press-conference meetings) | about 60 bp; 56 bp to next-day settle; R2 40% at t=50 | "returns from the 10th to the 60th minute following announcements predicts a substantial price reversal of about 60 basis points that can last several hours until the next trading day. For announcements with no press conferences, we find no price reversal." | p. 3-4; p. 19 | Boguth, Gregoire, Martineau, Price Pressure and Efficiency on FOMC Announcements, draft 28 Jun 2019, https://ies.keio.ac.jp/upload/20190716macro_Martineau_abstract-1.pdf | working-paper | pages/R6/keio_martineau_2019_abstract.pdf |
| later version: reversal by announcement-cycle end | n/a | "Standard predictive regressions confirm significant reversal of event-window returns by announcement-cycle end." | 2025 abstract | Boguth, Fisher, Gregoire, Martineau, Noisy FOMC Returns? (2025), https://www.vincentgregoire.com/ | working-paper [abstract only] | pages/R6/vincentgregoire_home.html |
| FOMC pre-announcement reversal, post-2011 | 23.34 bp per event net of spread, 71 events, annualized SR 1.60 | "Reversal From 1:50 p.m. FOMCt to 3:50 p.m. FOMCt 71 23.34*** 1.60" | Table 1.9 Panel A, p. 26 | Baglioni (2023), Essays in Financial Economics, PhD thesis, Insper, ch. 1 with R. M. Ribeiro, https://repositorio.insper.edu.br/handle/11224/7532 | thesis | pages/R6/baglioni_2023_insper_thesis.pdf |
| same, 1997-2020 | 17.86 bp, 180 events, SR 1.02 | "Reversal From 1:50 p.m. FOMCt to 3:50 p.m. FOMCt 180 17.86*** 1.02" | Table 1.2 Panel A, p. 14 | same | thesis | same |
| same, regression slope | -23 bp per 1% pre-return | "A 1% return in the pre-announcement interval implies 23 basis points (bps) of negative return in the post-announcement interval." | p. 9 | same | thesis | same |
| pre-FOMC drift gone after 2015 | n/a | "the pre-FOMC drift essentially disappeared after 2015 in both announcements accompanied by press conferences and announcements not accompanied by press conferences" | abstract | Kurov, Wolfe, Gilbert, The Disappearing Pre-FOMC Announcement Drift, FRL 40 (2021) (E.10 copy, re-used) | peer-reviewed | reports/stage_e10_research/calendar/kurov_wolfe_gilbert_2020.txt |
| CPI-day / GDP-day first-half-hour -> last-half-hour momentum | 18.03 / 14.40 %/yr (x252) | "Release CPI 18.03*** 5.80 3.11"; "Release GDP 14.40** 6.14 2.35" | Table 8 Panel B | Gao, Han, Li, Zhou, Market intraday momentum, WP Dec 2015 (JFE 129, 2018) (E.20 copy, re-used) | working-paper (peer-reviewed version exists) | reports/stage_e20_briefs/shared/gao_han_li_zhou_wp2015_mql5.pdf.txt |
| pre-release drift in ES before 10:00 ET releases | ISM Mfg 0.091%, ISM NM 0.139%, existing home 0.113% per 1-sd surprise | "ISM Manufacturing 0.091 (0.036)** 0.06 -0.027 (0.009)***" | Table 3 | Kurov, Sancetta, Strasser, Wolfe, ECB WP 1901 (2016) (E.20 copy, re-used) | working-paper (JFQA 2019) | reports/stage_e20_briefs/pages/ZN/kssw_ecbwp1901.pdf.txt |
| no pre-release drift for CPI / NFP / retail / claims | CPI -0.005 (0.035) | "Consumer price index -0.005 (0.035) 0.00 -0.001 (0.011) 0.00 0.981" | Table 3 | same | working-paper | same |
| ES response 90% in first minute, flat after 5 min | 90% | "Around 90% of the response happens during the first minute. After the first 5 minutes upon the announcement, the price seems to stay at a post-announcement level." | s. 4, p. 16 | Pinchuk, Monetary Uncertainty as a Determinant of the Response of Stock Market to Macroeconomic News, arXiv 2212.04525 (2022); E-mini 1-min, 1997-2019 | working-paper | pages/R6/arxiv_2212.04525_monetary_uncertainty.pdf |
| overreaction only after most positive surprises | > half retraced (figure) | "prices seem to drift back more than halfway toward their pre-announcement level. I observe this pattern only for the most positive news surprises." | p. 16-17 | same | working-paper | same |
| CPI overshoot on circuit-breaker days is sub-minute | rejections 50% (20-30 s) -> 0% (600 s) | "When we use longer windows of at least one minute for the event-return estimation, results in Table 5 show that the rejection frequencies fall rapidly to zero." | s. 5.3, Table 5 | Winkelmann, Yao, Breaking news, arXiv 2603.22835 (2026); ES CPI 2020-01..2025-10, 69 releases | working-paper | pages/R6/arxiv_2603.22835_breaking_news.pdf |
| CPI 1-min ES move size 2020-2025 | median abs 0.19% (regular), 0.82% (breaking) | "The median 1-minute absolute event return quadruples from 0.2% to 0.8%." | s. 5.1, Table 3 | same | working-paper | same |
| ES reaction to CPI larger in 2021-2023 regime | -66.09 bp vs -4.98 bp per 1-sd surprise (60-min) | "News -4.98* -66.09***" (S&P 500 low vs high inflation) | Table 3, p. 24 | Kroner, How Markets Process Macro News: The Importance of Investor Attention, FEDS 2025-022 | working-paper | pages/R6/kroner_feds2025022.pdf |
| overreaction is multi-day | n/a | "both interest rates and inflation swap rates tend to overreact in the first days following CPI releases when levels of attention are high" | p. 3 | same | working-paper | same |
| CL 5-min response to NFP / retail sales | 0.2852% / 0.1433% per sd | "Change in Nonfarm Payrolls 0.2852a ( 5.01) 0.00 30.57 59" | Table 5 | Chatrath, Miao, Ramchander et al., Does the price of crude oil respond to macroeconomic news?, JFM 32(6) 2012 (author manuscript), https://hdl.handle.net/10217/206897 | peer-reviewed (manuscript) | pages/R6/crude_macro_jfm2012.pdf |
| CL "reversal" within 30 min (RV-based) | n/a | "It appears that all of the price response for all the announcements is reversed within thirty minutes." | p. 23, Table 6 | same | peer-reviewed (manuscript) | same |
| gold response efficient, gone within an hour | durable goods 0.06% per sd in 5 min | "the metal prices are efficient in incorporating new economic information and the response tends to dissipate in less than an hour after the release of the announcement" | s. 5.4, p. 22-23 | Elder, Miao, Ramchander, Impact of macroeconomic news on metal futures, JBF 36(1) 2012 (manuscript) | peer-reviewed (manuscript) | pages/R6/elder_miao_ramchander_2012_metals.pdf |
| ES and ZN futures absorb 08:30 ET news within 5 min, 2021-2023 | 4-5 bp per unit surprise in first 5 min; about 0 after | "after the first five-minute interval, the estimates are very close to zero and not significantly different from zero" | p. 5, text on Figures 1-2 | Council of Economic Advisers, The Timing of Market Reactions to Data Releases (for OMB), 14 Feb 2024, https://bidenwhitehouse.archives.gov/wp-content/uploads/2024/02/CEA-PFEI-Analysis.pdf | exchange-regulator (US government analysis; not peer-reviewed) | pages/R6/cea_pfei_analysis_2024.pdf |
| primary response within seconds | 3-4 s; nothing after about 9 s | "the primary response to economic data releases occurs within the first 3-4 seconds after the news announcement is made, and that after approximately 9 seconds, asset price movements can no longer be related to the announcement" | p. 2 (summary of Brogaard et al. 2014 and Hu et al. 2017) | same | exchange-regulator [secondary for the cited studies] | same |
| FOMC reversals are daily-horizon in the later version | 80 bp (press-conference meetings), days [0,3] -> [4,20] | "Column (4) and (6) report a price reversal of 80 and 85 bps for FOMC announcements with press conference and with large monetary policy surprises, respectively." | s. 4, p. 25 | Boguth, Fisher, Gregoire, Martineau, Price Informativeness and FOMC Return Reversals, 5 Mar 2023 (SocArXiv/OSF zurfk; later "Noisy FOMC Returns?", R&R RFS per CV [secondary-only for status]), https://osf.io/download/62a74fca2631491f71a3175f/ | working-paper | pages/R6/osf_zurfk_boguth_gregoire_martineau_2022.pdf |
| intraday FOMC windows reversed later | raw dR2 -0.003 to -0.012 | "the raw dR2 are negative, ranging from -0.003 to -0.012, implying that stock market returns in the intraday pre-announcement and announcement windows are reversed by later returns" | s. 3, p. 14 | same | working-paper | same |
| CPI/NFP/GDP days: no equity reversal | excess dR2 > 0 | "Significant price reversals are a unique feature of equity returns on FOMC announcement dates." | s. 3, p. 19 (Table 5) | same | working-paper | same |
| statement-window SPY move size, 73 press conferences | mean 0.085%, sd 0.511% | "SPY Return: Statement Release (%) NYSE TAQ 0.085 0.511 -1.421 1.192" | Table A.2 | Narain, Sangani (IJCB 2026) | peer-reviewed | pages/R6/ijcb_market_impact_fed_press_conf.pdf |
| press-conference end times 2023-2024 | 15:14-15:23 ET | "Mar. 20, 2024 Jerome Powell 5-1/4 to 5-1/2 Percent Yes 14:00 14:30 15:17" | Table A.1 | same | peer-reviewed | same |
| early press-conference era had different clock times | statements 12:30 ET, PC 14:15 ET (2011-2012) | "04/27/2011 12:30 12:32 14:15" | Internet Appendix table of announcement times | Boguth, Gregoire, Martineau, Internet Appendix to "Shaping Expectations and Coordinating Attention" (JFQA), 5 Sep 2018, https://www.vincentgregoire.com/files/appendices/FOMC_PC_InternetAppendix.pdf | working-paper (appendix of a peer-reviewed paper) | pages/R6/gregoire_FOMC_PC_InternetAppendix.pdf |
| Topstep Tier 1 window (constraint, not evidence of an effect) | 5 min either side; minis 0; micros 1/3/6/9/15 | "Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after)." | Tier 1 News Events Restrictions | Topstep help 13613539 (dateModified 2026-10-16), read from R9's copy | firm-page | pages/R9/ts_13613539.html |
| QRA supply surprises move term spread | 0.07%-0.20% per 1% GDP surprise | "a tight intraday window around the announcement, to precisely identify the causal effect of supply surprises on yields" | abstract page | Hartley, Rigon, Hoover Economics WP 26112 (2026) | working-paper [abstract only] | pages/R6/hoover_hartley_rigon_2026_qra.html |

## 4. Negative evidence

- Regime instability of the FOMC press-conference sign: positive (reinforcing) 2011-2020 (Gomez-Cram and
  Grotteria: 44% for SPY; Narain-Sangani: Bernanke 0.367, Yellen 0.267, Powell pre-COVID 0.526, all not
  significant) and negative only post-COVID; N 73 in all, about 16 after March 2022; nothing after March
  2024 was found.
- Boguth et al.: "For announcements with no press conferences, we find no price reversal." (all FOMC
  meetings have had press conferences since 2019, so this matters for history only); the 2025 version moved
  the headline horizon to the whole announcement cycle.
- Baglioni sample ends January 2020; the drift leg (Lucca-Moench) that motivated it disappeared after 2015
  (Kurov-Wolfe-Gilbert). No replication found (OpenAlex budget exhausted, Semantic Scholar throttled).
- Price discovery on 08:30 releases is near-instant (90% in the first minute, flat after 5 min); overshoots
  are sub-minute; Chordia, Green, Kottimukkalur (RFS 2018) report price response within milliseconds and
  that low-latency profits did not rise [secondary-only: search-result abstract, PDF not fetched].
- CL "reversal within 30 min" rests on a realized-volatility comparison, not on signed returns.
- Pre-release drift (Kurov et al.) exists only for some 10:00 ET releases, ends in 2014, and its profits are
  computed with the surprise known; the same tradable form on ZN/ZB before ISM Services (K2-predrift-01)
  did not show in the research window.
- Gao et al. release-day momentum: the program's E20H6-T1 measured 1.25 MNQ ticks gross on the
  unconditional mechanism, far below the published unconditional 2.5 bp.
- CEA (2021-2023 sample, the most recent found): ES and ZN surprise responses are "very close to zero" after
  the first 5-minute interval, out to 60 minutes: no post-release drift and no measurable reversal in later
  intervals on the 08:30 ET releases.
- Boguth et al. (2023): the FOMC reversal survives in the later version only at daily horizons ([0,3] -> [4,20]
  trading days, not prop-compatible); equity returns on GDP, inflation and unemployment days are not reversed.
- Kroner: CPI sensitivity was a 2021-2023 attention regime; low-inflation coefficient -4.98 bp per sd is
  13x smaller, so CPI-keyed effects should be expected to have shrunk after 2023.

## 5. Data and cost

All six candidates use only owned data: 1-minute bars (NQ, ES, MES, CL/MCL; brief section 4) and the owned
release calendars (FOMC, CPI, NFP, GDP, ISM). Gaps: R6-C4 needs an advance retail sales calendar and
R6-C6 needs ISM Manufacturing / existing and pending home sales / Conference Board calendars (free
official schedules: BLS, Census, NAR, Conference Board; not fetched here); R6-C1 needs press-conference end
times only if a variable exit is used (a fixed exit avoids it). No surprise (consensus) data is owned:
none of the six candidates needs it. Surprise-signed variants (Kurov profits, Elder/Chatrath coefficients,
Hartley-Rigon QRA) would need Bloomberg/consensus data (not priced here; no purchase). Research-window
event counts (2025-04-01..2026-06-19): FOMC about 10 meetings (C1-C3), CPI about 14 and GDP about 14 (C5),
NFP and retail sales about 14 each (C4), 10:00 ET releases about 14 each (C6) -- counts are calendar
arithmetic, not read from data.

## 6. Prop compatibility (Topstep rules as in brief section 3)

| id | flat by 15:10 CT | P06 (no full max size into a scheduled major release) | Topstep Tier 1 window (CT) | HFT / automation | events/yr |
|---|---|---|---|---|---|
| R6-C1 | yes (exit about 14:20 CT) | entry during the Chair press conference: scheduled event in progress; below max size | BINDS: 13:30 entry is inside 13:25-13:35; NQ/ES blocked, MNQ/MES capped (3 on 50K), pending orders do not fill; move entry to 13:36 CT on micros | 1-min decision, no HFT | 8 |
| R6-C2 | yes (exit 15:05 CT) | entry 50 min after the statement, inside the press conference; below max size | not binding (13:50 entry) | 1-min | 8 |
| R6-C3 | yes (exit 14:50 CT) | BINDS: opened 10 min before the 13:00 CT statement and held through it; below max size | entry 12:50 is outside 12:55-13:05; hold through the window allowed for open positions (equity-index hold not stated explicitly) | 1-min | 8 |
| R6-C4 | yes (exit 08:00 CT) | entry 5 min after the release, not held into it | not binding: energies unaffected; retail sales not a named Tier 1 event | 1-min | about 24 |
| R6-C5 | yes (14:30-15:00 CT) | not triggered | not binding (14:30 entry) | 1-min | about 12 per release type |
| R6-C6 | yes (exit about 09:05 CT) | BINDS: held through the 09:00 CT release; below max size | not binding on named events (ISM etc. not listed) | 1-min | about 12 per release type |

DLL: C1-C3 per-trade sd is of order 0.7-0.9% of the index (Narain-Sangani SPY sd 0.723%; Baglioni implied sd
74-89 bp): on 1 MNQ at NQ 21,000 that is about 150-190 NQ points x $2 = $300-$380 per contract-sd, inside
a $1,000 DLL at 1-2 MNQ; the lead sizes. Other firms: not assessed here (R9).

## 7. Overlap with tested mechanisms

| candidate | overlap ids | how it differs |
|---|---|---|
| R6-C1 | E-H2, K5-fomc-01, K2-fomcpost-01 | fades the statement-window move during 13:30-14:20 CT; tested members trade momentum 13:05-13:15 (MES, MGC) or an unconditional rates buy |
| R6-C2 | E-H2, K5-fomc-01, K2-fomcpost-01 | fades the 13:10-13:50 CT move to 15:05 CT; no tested member conditions on it |
| R6-C3 | E-H1 (drift leg), K9 pre-FOMC drift (not a trial, P-04) | the reversal leg (prior-24h sign faded through the release) was never a trial |
| R6-C4 | K4-eiafade-01 | same fade logic on BLS/Census 08:30 ET releases instead of EIA WPSR |
| R6-C5 | E20H6-T1..T3, K1-cp1-01 | release-day conditioning of a mechanism that failed unconditionally |
| R6-C6 | K2-predrift-01 | same tradable form on ES/NQ and on 10:00 ET releases other than ISM Services |

## 8. Verdicts touched by the deeper reading (R6 is not a re-dig reader; listed because the full texts bear on them)

- E.13 I-56b and the K9 exclusion of pre-FOMC drift on frequency (P-04): WEAKENS the closure as applied to the
  reversal leg. E.13 read only the abstract; the full thesis gives 23.34 bp per event net of spread on 71
  post-2011 events (Table 1.9), larger than the drift it was compared with, while the drift itself is dead
  post-2015 (supports the E-H1 drift fail).
- E-H1 (MES pre-release drift on FOMC/CPI/NFP): SUPPORTS the fail: Kurov-Wolfe-Gilbert "the pre-FOMC drift
  essentially disappeared after 2015"; Kurov et al. Table 3 shows no CPI/NFP pre-release drift.
- E-H2 (MES 10-min post-release momentum): SUPPORTS the fail: "After the first 5 minutes upon the
  announcement, the price seems to stay at a post-announcement level" (Pinchuk); for FOMC, Boguth et al.
  find reversal, not momentum, from minute 10 on.
- K5-fomc-01 (MGC FOMC momentum, E.22 null): SUPPORTS: metals "efficient in incorporating new economic
  information" (Elder et al.); no source found for gold momentum after FOMC at 5-15 min.
- K2-predrift-01 (ZN/ZB pre-ISM drift, Tier B): consistent with Kurov et al. (drift sample ends 2014); no
  newer evidence found either way.

## 9. Fetch log, terms, budget notices

| url | UTC | sha256 (first 16) | saved path | status | tool |
|---|---|---|---|---|---|
| https://arxiv.org/pdf/2603.22835 | 2026-10-18T08:41:43Z | 12019def00fe0d3a | pages/R6/arxiv_2603.22835_breaking_news.pdf | ok | curl |
| https://arxiv.org/pdf/2212.04525 | 2026-10-18T08:42:14Z | bb1fc3fac41638c5 | pages/R6/arxiv_2212.04525_monetary_uncertainty.pdf | ok | curl |
| https://ndownloader.figshare.com/files/34909368 | 2026-10-18T08:43:44Z | e5decd50971051dc | (deleted: 2 KB HTML, HTTP 202, no PDF) | blocked (no file served; Lin-Lo-Qiao 2021 not read) | curl |
| https://www.ijcb.org/sites/default/files/ijcb-vn-market-impact-fed-communications-role-press-conference.pdf | 2026-10-18T08:45:11Z | 78b6a436c038d4bf | pages/R6/ijcb_market_impact_fed_press_conf.pdf | ok | curl |
| https://clon.cemla.org/actividades/2020-final/2020-10-xxv-meeting-cbrn/Session%205/1.%20SLIDES%20Real-time%20Price%20DIscovery.pdf | 2026-10-18T08:48:27Z | 1f10e494e32944ea | pages/R6/cemla_gomezcram_grotteria_slides.pdf | ok | curl |
| https://mountainscholar.org/bitstreams/21623442-a01d-45a6-879d-d645e781e52a/download | 2026-10-18T08:49:56Z | 80b8073e34ffddd5 | pages/R6/elder_miao_ramchander_2012_metals.pdf | ok | curl |
| https://repositorio.insper.edu.br/bitstreams/fb55a5bb-06c8-4ed4-aa81-054742c3b42d/download | 2026-10-18T08:52:20Z | 865a0c404e05013a | pages/R6/baglioni_2023_insper_thesis.pdf | ok (curl 403 Akamai; scrapling get) | scrapling get |
| https://www.vincentgregoire.com/ | 2026-10-18T08:53:51Z | 9907ab77664e5c34 | pages/R6/vincentgregoire_home.html | ok | curl |
| https://ies.keio.ac.jp/upload/20190716macro_Martineau_abstract-1.pdf | 2026-10-18T08:53:59Z | 40e14f7715f413c9 | pages/R6/keio_martineau_2019_abstract.pdf | ok | curl |
| https://www.hoover.org/research/does-government-debt-management-matter-high-frequency-identification-us-treasury-quarterly | 2026-10-18T08:55:40Z | 2492ce075b5999d4 | pages/R6/hoover_hartley_rigon_2026_qra.html | ok (abstract page only) | curl |
| https://mountainscholar.org/handle/10217/206897?show=full | 2026-10-18T08:56:08Z | d59963a6e45967ac | pages/R6/mountainscholar_206897_crude_macro.html | ok | curl |
| https://mountainscholar.org/bitstreams/4a089604-914e-4497-bf2e-25fa9408b9a3/download | 2026-10-18T08:56:14Z | 7cee58203d1d6db0 | pages/R6/crude_macro_jfm2012.pdf | ok | curl |
| https://www.federalreserve.gov/econres/feds/files/2025022pap.pdf | 2026-10-18T08:57:03Z | 25de8e1d91475e5f | pages/R6/kroner_feds2025022.pdf | ok | curl |
| https://www.vincentgregoire.com/files/appendices/FOMC_PC_InternetAppendix.pdf | 2026-10-18T13:22:57Z | 8d36fef667db36cf | pages/R6/gregoire_FOMC_PC_InternetAppendix.pdf | ok | curl |
| https://www.charlesmartineau.com/research | 2026-10-18T13:23:20Z | n/a | scratch only (no "Noisy FOMC Returns" PDF linked) | ok, nothing found | curl |
| https://osf.io/download/62a74fca2631491f71a3175f/ | 2026-10-18T13:23:45Z | 31f75c3a7b2ff9be | pages/R6/osf_zurfk_boguth_gregoire_martineau_2022.pdf | ok | curl |
| https://www.whitehouse.gov/wp-content/uploads/2024/02/CEA-PFEI-Analysis.pdf | 2026-10-18T13:24:47Z | n/a | none | not found (404; removed from current site) | curl |
| https://bidenwhitehouse.archives.gov/wp-content/uploads/2024/02/CEA-PFEI-Analysis.pdf | 2026-10-18T13:24:58Z | 156385bbd8446b73 | pages/R6/cea_pfei_analysis_2024.pdf | ok | curl |

Re-used from disk (not refetched): Gao-Han-Li-Zhou WP (reports/stage_e20_briefs/shared/), Kurov-Sancetta-Strasser-Wolfe
ECB WP 1901 (reports/stage_e20_briefs/pages/ZN/), Kurov-Wolfe-Gilbert (reports/stage_e10_research/calendar/), Topstep
help 13613539 (pages/R9/ts_13613539.html, R9's fetch 2026-10-18T08:47:24Z).

Terms read (lines in terms/terms_log.md, reader R6): figshare.com, www.ijcb.org, lbsresearch.london.edu (robots
blocks Claude agents: forbidden, nothing fetched), clon.cemla.org, mountainscholar.org, repositorio.insper.edu.br,
www.vincentgregoire.com, ies.keio.ac.jp, www.hoover.org, www.cambridge.org (forbidden by caution, nothing fetched),
www.whitehouse.gov and bidenwhitehouse.archives.gov (US-government material, not copyright protected), www.cxoadvisory.com
(copying prohibited: forbidden, nothing fetched; it reviews Baglioni-Ribeiro, pointer only). Cited other readers'
lines: arxiv.org, osf.io (line 54), www.federalreserve.gov. www.charlesmartineau.com: robots.txt "User-Agent: *" with
no Disallow and content-signal comments that set no signal; one page read, nothing saved to pages/.

Budget notices: OpenAlex 2026-10-18T08:46:35Z "Rate limit exceeded ... Insufficient budget ... ($0 remaining; resets at
midnight UTC)"; not called again. Firecrawl 2026-10-18T08:47:26Z "Request failed with status code 402 ... out of
credits"; not called again. Semantic Scholar keyless: 429 three times each on four lookups 08:48-08:59Z (Narain-Sangani,
Gomez-Cram-Grotteria, Hartley-Rigon QRA, Baglioni) then logged "throttled"; not retried in the second pass.
WebSearch: second pass used 5 calls (13:22-13:26Z), no over-budget notice. First-pass count not recorded on disk.

## 10. Unfinished and unverified items

- No post-January-2020 test of R6-C3 (Baglioni-Ribeiro reversal) and no post-March-2024 test of R6-C1 were found;
  forward-citation searches were blocked (OpenAlex budget, S2 throttled). CXO Advisory reviews the paper but its
  terms forbid copying, so it was not read.
- "Noisy FOMC Returns?" (2025, SSRN 4131740) full text not read: SSRN is off limits by automation and no author
  page links a PDF; the 2023 OSF version was read instead. Whether the 2025 version restores an intraday reversal
  number is unknown.
- Gomez-Cram and Grotteria JFE 2022 text: slides only [secondary-only]. Chordia-Green-Kottimukkalur RFS 2018:
  abstract only [secondary-only]. Lin-Lo-Qiao (2021, JBF) figshare file not served: not read.
- R6-C1 conversion uses my approximation of the mean absolute statement move (0.8 x sd); Narain-Sangani do not
  print it. The published press-conference fade is start-to-end; the share lost by moving entry to 13:36 CT is
  not published.
- Same-day share of the Boguth et al. 2019 post-statement reversal (R6-C2) is not published.
- Release calendars for advance retail sales, existing/pending home sales and Conference Board confidence are not
  owned; official schedules not fetched (C4, C6).
- Topstep: whether holding an existing equity-index position through a Tier 1 window is allowed is implied, not
  stated (the "Existing Positions" sentence names energies and metals); whether Topstep adds events beyond CPI,
  FOMC and NFP ("for example") is not stated as a fixed list.
- The lead verifies all conversions (bp to points to micro ticks) and the Baglioni Sharpe-to-per-event derivation.
