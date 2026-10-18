# RD2 re-dig: rates sources (Treasury futures), Stage E.25

Reader: RedigReader-Rates-OpusHigh (RD2). Started 2026-10-18 01:38 PDT; this version 02:05 PDT.
Scope: every source cited in reports/stage_e20_briefs/product_{ZN,ZT,ZF,ZB,UB,TN}.{json,md},
shared/rates_class_notes.md and shared/aalto_thesis_notes.md, plus the sources behind E16-H2
(Harvey, Mazzoleni, Melone 2025) and E16-H3 (Lou, Yan, Zhang 2013), with their forward citations.
Conversions follow rates_class_notes.md section 0: ZN tick 1/64 = 0.015625 pt = 1.42 bp of price at
110; ZN price change about 0.69 x the on-the-run 10-year cash price change (E.20 assumption,
duration about 6 vs 8.7, not sourced); ZN D8 RT 1.168 ticks, hurdle 1.75 ticks (brief section 2).

## 1. Answer (at most 250 words)

Deeper reading mostly SUPPORTS the rates closures, with two exceptions that came from sources the
E.20 readers had on disk or saw only as abstracts.

Supports: the auction cycle (E16-H3, K2-aucpre/aucpost). SR 1188 states that Lou, Yan and Zhang's
multi-day effect "do[es] not persist at the same magnitude" through 2024. Lou, Yan and Zhang's own cost
table says short holds (t <= 6 days) are unprofitable after costs; H3 used 3 and 5 days. Fleming,
Nguyen and Rosenberg (JFE 2024) find dealers' post-auction compensation "has also declined".
Bond intraday momentum (K2-cp1, E20H6 class): the Baltussen bond rows were checked against the full
text, and their decay holds. The Aalto thesis is still metadata-only.

Weakens V38's sentence "no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8
round trip":
- Wang and Zhao (2025 draft, OFR/Notre Dame). E.20 logged it as "long end, daily; out of scope" from
  the abstract. The full text shows an intraday gain in New York hours on the day before the quarterly
  refunding announcement: 10-year cash +12.62 bp (t 3.32, 1991-2023), about 6.1 ZN ticks gross.
  It strengthened after 2002. Only 4 events a year.
- Pan and Peng (June 2026 draft; the copy was on disk in E.20's ZT folder, but E.20 used only its 2-year
  null). A pre-FOMC Treasury drift realized 19:00 ET day -2 to 12:00 ET day -1: +7.26 bp (t 2.82,
  2004-2025), about 5.1 ZN ticks if the figure is a futures return. That window fits one Topstep trading
  day. It contradicts E.20's "FOMC: no pre-drift" row.

The 5-year auction effect, not decayed after 2015, was already noted by E.20 and tested in K2.

## 2. Candidate hypotheses

| id | hypothesis | instruments | entry window CT | hold | trades/yr | published effect | gross per trade (ZN ticks) | grade | overlap |
|---|---|---|---|---|---|---|---|---|---|
| RD2-C1 | Pre-refunding-announcement (pre-TRA) day long: buy long-dated Treasury futures at the start of the New York session on the trading day before the Treasury's quarterly Primary Release (Monday 15:00 ET), exit by 15:05 CT the same day | ZN (also ZB, UB, ZF) | 06:30 CT (07:30 ET) or the 17:00 CT session open, exit <= 15:05 CT | about 8.5 h (or one trading day) | 4 | 10-year cash +12.62 bp/day (daily CRSP, N 129, sd 43.15, t 3.32, 1991Q4-2023); intraday Tradeweb 2006-2023: "10-year Treasury rising by over 10 bps" in the morning of Day -1 | 6.13 (daily mean x 0.69), 4.86 (intraday ">10 bp" lower bound), 4.19 (non-ZLB subsample 8.62 bp) | working-paper | K2-monthend-01 (pre-TRA Fridays often fall in the last 5 days of the month); E16-H3 (refunding auctions follow); none tests TRA dates |
| RD2-C2 | Pre-FOMC Treasury drift, overnight leg: long ZN from 19:00 ET (18:00 CT) on day -2 (the evening before the meeting's first day) to 12:00 ET (11:00 CT) on day -1 | ZN (UB, ZB plausible; 10-year only reported intraday) | 18:00 CT entry (overnight session), 11:00 CT exit | 17 h, inside one Topstep trading day (17:00-15:10 CT) | 8 | "approximately 7.26 basis points, with a statistically significant t-statistic of 2.82" (10-year, 2004-01..2025-06); remainder of day -1 (12:00-17:00 ET) -2.05 bp (t -1.76) | 5.11 if 7.26 bp is a ZN futures return (Figure 2 plots "10-year Treasury note futures"); 3.53 if it is a cash 10-year return (x 0.69) | working-paper | K2-fomcpost-01 (post-statement, day 0); E-H1 (MES, day 0, overnight-through-day); K5-fomc-01 (gold, day 0); no member trades day -1 on rates |

Details per candidate (JSON has every field):
- RD2-C1. The window and subsamples come from many splits (pre/post 2002, surplus, debt ceiling, ZLB,
  recession, slope, quarter). The two splits that matter now cut against it: "Downward-sloping 10 ...
  4.71 [0.36]" (the curve was inverted for much of 2022-2024) and "Q2 32 ... -2.81 [-0.36]". The
  research window 2025-04..2026-06 holds about 5 pre-TRA days; the paper's first version was March
  2024, so those days are post-publication. The paper's own cost remark borrows Lou, Yan and Zhang's
  4 bp: "even with a 4 bps transaction cost, the equally weighted pre-TRA strategy would sustain an
  annualized Sharpe ratio close to 4". No replication was found (one WebSearch, OpenAlex citing list:
  none; OpenAlex then ran out of budget).
- RD2-C2. The window was chosen by the authors from the intraday figure (19:00 ET Tokyo open to
  12:00 ET London close). It is a post-hoc window and needs a pre-registered fixed window. The daily
  drift depends on regime: "Panel B: QE and QT ... QE3 0.84 1.92** 1.79***" and the authors link it to
  "the post-2008 QE environment". The entry is in the overnight session, where D8's day-session cost
  does not apply (no published overnight ZN spread found; unverified).

Not proposed (and why): the 5-year auction legs (SR 1188 S3 5-year price pressure 4.482 bp,
significant at 1%). They are K2-aucpre-01 and K2-aucpost-01 on ZF, already screened (E.3, Tier B).
E.20's ZF reader already flagged them as undecayed. Smales (2021) post-auction 15-minute futures
reaction to the bid-to-cover: abstract only, and it is the excluded K2-surprise-01 (X-08) shape.

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| Pre-TRA 10-year daily return | 12.62 bp, sd 43.15, N 129 | "10Y 129        12.62       43.15      -97.92     121.41     7,933      1.82" | Table 2 Panel A, PDF p. ~43 (txt l.1489) | Wang, Zhao, "Pre-Refunding Announcement Gains in U.S. Treasurys", July 16 2025 draft (first version March 18 2024), OSF preprint xucf8, https://osf.io/xucf8/download | working-paper | pages/RD2/wang_zhao_2024_prerefunding.pdf (.txt) |
| Pre-TRA t-stats and post-2002 | 12.62 (t 3.32); post-2002 15.48 (t 3.27); pre-2002 6.48 (t 1.03) | "Full                     129      0.66          [0.86]    8.25∗∗∗      [3.62]    12.62∗∗∗    [3.32]"; "Post-2002                 88      0.57          [0.53]    9.97∗∗∗      [3.66]    15.48∗∗∗    [3.27]" | Table 6 Panels A-B | same | working-paper | same |
| Pre-TRA intraday timing | >10 bp in the NY morning | "A significant upward price movement in Treasurys begins early in the New York trading session on the day preceding the TRA (Day −1). Prices increase notably in the morning, with the 10-year Treasury rising by over 10 bps, and then continue to increase marginally for the remainder of New York trading hours." | Section 4.3, p. 19 | same | working-paper | same |
| Pre-TRA intraday data | Tradeweb, 07:30-17:00 ET, 2006-2023 | "average cumulative intraday returns for 10-year Treasury notes during New York trading hours (07:30-17:00 ET) ... The sample period is from 2006 to 2023." | Figure 1 note, p. 2 | same | working-paper | same |
| Pre-TRA day is usually a Friday; EOM control | attenuated, still significant | "since most TRAs occur on Mondays, the pre-TRA day is typically a Friday"; "while the magnitude of the pre-TRA coefficient is slightly attenuated, it remains positive and statistically significant for all maturities" | Section 4.1, p. 14-15 | same | working-paper | same |
| Pre-TRA weak regimes | downward slope 4.71 (t 0.36, N 10); Q2 -2.81; non-ZLB 8.62 (t 2.19) | "Downward-sloping        10        -0.43         [-0.38]    2.04        [0.22]      4.71      [0.36]"; "Non-ZLB                  101      1.39          [1.43]     5.69∗∗      [2.30]     8.62∗∗     [2.19]" | Table 6 Panels E, G, H | same | working-paper | same |
| Pre-FOMC Treasury drift, overnight window | 7.26 bp, t 2.82 | "The average cumulative return on U.S. Treasury futures begins to rise at 19:00 ET on day -2, coinciding with the start of the Tokyo market, and peaks at 12:00 ET on day -1, aligning with the closing of the London market. The average 10-year Treasury return over this non-U.S. trading window is approximately 7.26 basis points, with a statistically significant t-statistic of 2.82. In contrast, during the remainder of the day (12:00 ET–17:00 ET) leading up to the FOMC meeting, the return is around -2.05 basis points, with a t-statistic of -1.76." | Section 3.1, pp. 12-13 | Pan, Peng, "The Pre-FOMC Drift in Long-Term Treasury Bonds", SAIF draft June 2 2026 (first draft May 31 2023) | working-paper | reports/stage_e20_briefs/pages/ZT/pan_peng_fomc_2026.pdf (.txt), sha256 06a73bf3...6326d (E.20 copy, re-read) |
| Pre-FOMC Treasury drift, daily | 10-year zero yield -0.79 bp | "Over the 24-hour window that ends at the market close of the day before the FOMC announcement, the 10-year zero-coupon bond yield drops by a significant 0.79 basis points, compared with a full-sample average of -0.04 basis points." | Introduction, p. 2 | same | working-paper | same |
| Pre-FOMC drift sample, futures | E-mini Treasury futures 2004-01..2025-06; 250 meetings 1994-2025 | "on E-mini Treasury futures from January 2004 to June 2025 from the Chicago Mercantile Exchange (CME)"; "During this period, we have 250 scheduled FOMC announcements." | Section 2 | same | working-paper | same |
| Auction cycle does not persist | qualitative | "the strong auction-cycle effects documented by Lou et al. (2013), whose sample ends in 2008, do not persist at the same magnitude when the sample is extended through 2024" | Section 4.1, pp. 20-21 | Fleming, Liu, Nguyen, NY Fed SR 1188 (2026) | working-paper | reports/stage_e20_briefs/pages/ZN/nyfed_sr1188.pdf (.txt l.719-721), sha256 93f9b196...095b |
| 10-day auction window weakens after 2014 | qualitative | "While yield pressure is significant over the full sample, the effect is most pronounced during 2007–2014 and weakens markedly in 2015–2024." | footnote 14, p. 21 | same | working-paper | same |
| 6-hour window share of 10-day effect | about 25% | "the six-hour window we study accounts for approximately 25% of the total 10-day effect" | p. 19 | same | working-paper | same |
| SR 1188 Table 2/3 numbers re-checked | all E.20 figures match | "10-Year ... 1.192∗∗∗"; "S3: 2015-2024 ... 0.593∗"; "Price Pressure (bps) ... 9.905∗∗∗"; "S3: 2015-2024 ... 4.482∗∗∗ ... 5.165∗ ... 14.224∗" | Tables 2-3, pp. 47-48 | same | working-paper | same |
| LYZ costs kill short holds | t <= 6 days unprofitable | "Panel C shows that repo funding costs and bid-ask spreads significantly reduce the profitability of the strategy. In particular, for t ≤ 6, trading costs render the strategy unprofitable. For longer holding periods (t ≥ 7), the strategy is still profitable, with an annualized Sharpe ratio of 0.84 for t = 10." | Section III, p. 16 | Lou, Yan, Zhang (2013), RFS 26(8), author copy https://personal.lse.ac.uk/loud/Shocks.pdf | peer-reviewed | pages/RD2/lou_yan_zhang_2013_shocks.pdf (.txt) |
| LYZ sample ends 2008 | 1980-2008 | "Our sample spans from January 1980 to June 2008" | Section II.B | same | peer-reviewed | same |
| LYZ 10-year 5-day differential weak | 23.84 bp, t 1.78 | "This 5-day return differential is 23.84 (t = 1.78) basis points for 10-year notes." | p. 10 | same | peer-reviewed | same |
| Dealer auction compensation declined | qualitative | "Surprisingly, compensation for taking on inventory risk at auctions has also declined. We show that the diminished post-auction price appreciation is related to the increasing participation of investment funds in the primary market in the post-crisis period." | Introduction | Fleming, Nguyen, Rosenberg, "How do Treasury dealers manage their positions?", NY Fed SR 299 (rev. 2024); JFE 158 (2024) | peer-reviewed (SR version read) | pages/RD2/nyfed_sr299_fleming_nguyen_rosenberg.pdf (.txt l.209-211) |
| Auctions move ZN futures (15-min) | direction only | "Using 15‐min intervals over the period 2000–2017, it is shown that auctions of US Treasury securities have an economic and statistically significant impact on the 10‐year Treasury note futures market. Prices move higher, volatility increases and there is an upturn in trading volume in the interval immediately following an auction." | abstract | Smales, "The effect of treasury auctions on 10-year Treasury note futures", Accounting & Finance 61(S1) 2021, 1517-1555 | peer-reviewed [secondary-only] | pages/RD2/ideas_smales_2021_acfi.html |
| Month-end Treasury effect persisted in 2015-2019 | 10-year zero, last day 0.13*** | "2015-2019 ... 10-Year        0.13***       0.08   0.27*** 0.24**    0.28**" | subperiod table, p. 27 | Hartley, Schwarz (2019), Rodney White Center WP 17-19 | working-paper | reports/stage_e20_briefs/pages/ZN/hartley_schwarz_2019.pdf (.txt l.1360-1362), sha256 56403762...a32809 |
| Month-end in futures | 10-year futures last day 0.09*** (%/month units) | "10-Year        0.09*** 0.14*** 0.17*** 0.18*** 0.22*** 0.20***" | Table 8 | same | working-paper | same (l.1520) |
| HS on costs | spread 2-3 bp vs EOM returns | "the typical off-the-run bid-ask spread is only 2 to 3 basis points ... This is an order of magnitude lower than the average excess returns for the end-of-month trading strategy at the 10-year maturity." | Section 2.2, p. 7 | same | working-paper | same |
| Rebalancing pair bond leg (E16-H2 source) | bonds +2 bp next day per 1 sd calendar signal | search-engine summary only (EDHEC copy terms forbid reproduction; NBER terms forbid automation) | abstract via search results | Harvey, Mazzoleni, Melone, NBER w33554 (2025) | working-paper [secondary-only] | none |
| Baltussen bond rows re-checked | TY beta_ROD 2.53 (6.96), R2 1.06, R2_OOS 0.86 | "TY | 1.68*** (3.41) | 0.24 | 0.16*** | ... | 2.53*** (6.96) | 1.06 | 0.86***"; bonds 2000-2020 "1.53*** (3.61) | 0.47"; "the bond market results remain positive but insignificantly so" | Table B2, Table 5, Section 4.2 | Baltussen, Da, Lammers, Martens, JFE 142 (2021) | peer-reviewed | reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md (l.3614, 1667, 2395) |
| Herb (2025) auction underpricing | risk premium, 2000-2016 | "underpricing of U.S. Treasury securities is explained by risk premia that compensate dealers for bearing price risk" | abstract | Herb, JBF 170 (2025) 107316 | peer-reviewed [secondary-only] | pages/RD2/ideas_herb_2025_jbf.html |

## 4. Negative evidence

- Auction cycle decay. SR 1188 says Lou et al.'s effect does not persist through 2024 and the 10-day
  window "weakens markedly in 2015–2024". Fleming, Nguyen and Rosenberg say auction compensation
  "has also declined". Lou, Yan and Zhang's own Panel C: "for t ≤ 6, trading costs render the strategy
  unprofitable". The 10-year 5-day differential was already weak in their sample (t 1.78).
- Bond intraday momentum: bonds 2000-2020 slope 1.53 with R2 0.47, against 3.19 and 1.28 in
  1974-1999. Mechanism test: "the bond market results remain positive but insignificantly so". The
  Aalto thesis access status on 2026-10-18 is still `"status" : "metadata.only"`
  (pages/RD2/aalto_thesis_accessstatus_2026-10-18.json).
- Pre-TRA (C1): weak or negative in some regimes: downward-sloping curve 4.71 bp (t 0.36), Q2 -2.81 bp,
  recession -2.18. No out-of-sample or post-2023 replication found.
- Pre-FOMC (C2): the 2-year shows no drift ("the 2-year bond yield drops by an insignificant 0.25 basis
  points"). The rest of day -1 gives back -2.05 bp. Lucca and Moench's 2pm-to-2pm window finds
  nothing, so the effect depends on the window. The drift depends on QE regime (Table A-robustness
  Panel B).

## 5. Data and cost

- C1: ZN/ZB/UB/ZF 1-minute bars are owned (2010-07..2024-02; research window 2025-04..2026-06). The TRA
  dates are not in the owned calendars (FOMC, CPI, NFP, PPI, GDP, ISM, EIA/WASDE, FiscalData auctions).
  They are public on Treasury press releases (home.treasury.gov; quarterly refunding statements), free.
  Not fetched here, and the program's terms check for home.treasury.gov is not done (E.16 used
  FiscalData for auctions). owned: partial. The paper's own dates are in its Table 1 (pages/RD2 copy,
  l.1425).
- C2: ZN bars owned. FOMC statement dates owned. Day -2 19:00 ET to day -1 12:00 ET needs overnight
  bars, which ohlcv-1m covers (Globex). owned: yes. Cost: D8 is day-session only. No published
  overnight ZN cost found [unverified].

## 6. Prop compatibility

- C1: entry 06:30 CT or at the 17:00 CT open, exit by 15:05 CT, flat before 15:10. Pre-TRA Fridays can
  fall on an NFP Friday or a month-end day. P06 bars full size into a scheduled major release, so the
  size must be capped on NFP-coincident dates (or the entry moved after 07:30 CT; the lead decides). No HFT.
  Automation or manual both workable (4 trades a year).
- C2: entry 18:00 CT on day -2's evening, which is the start of Topstep's trading day for day -1
  (17:00-15:10 CT), exit 11:00 CT. That is no overnight hold in Topstep's sense. Day -1 (Tuesday of a
  two-day meeting) can coincide with CPI or other 07:30 CT releases (P06). Low overnight liquidity.
  Topstep lists ZN; no micro 10-year note exists (CME's 10-year micro yield futures are a different
  contract), so 1 ZN is the minimum, at $15.625 a tick.

## 7. Overlap with tested mechanisms

- C1: no member uses TRA dates. Partial date overlap with K2-monthend-01 (N-1, N day session) and
  E23-MEZNh5. Wang-Zhao control for EOM ("last five trading days") and the effect survives. E16-H3 holds
  around auctions, which follow the TRA by about a week.
- C2: K2-fomcpost-01 (day 0, 13:29-15:04 CT, Tier B), E-H1 (MES day 0 overnight-through-day),
  K5-fomc-01 (MGC day 0). No member holds rates futures on day -1. Gate 0's release-clock features
  (g13-g15) cover FOMC on ZF only as minutes-to/since release at fixed decision times (overlap
  unchecked beyond the index).

## 8. Verdict checks (re-dig)

| verdict | effect | quote | source |
|---|---|---|---|
| E16-H3 (Treasury auction cycle, multi-day) FAIL, E.17/V31 | SUPPORTS | "the strong auction-cycle effects documented by Lou et al. (2013), whose sample ends in 2008, do not persist at the same magnitude when the sample is extended through 2024" | SR 1188 p. 20-21 |
| E16-H3 FAIL (hold lengths 3 and 5 days) | SUPPORTS | "for t ≤ 6, trading costs render the strategy unprofitable" | Lou, Yan, Zhang 2013, p. 16 |
| E16-H3 and K2-aucpre/aucpost (E.3 Tier B) | SUPPORTS | "compensation for taking on inventory risk at auctions has also declined ... related to the increasing participation of investment funds in the primary market in the post-crisis period" | Fleming, Nguyen, Rosenberg, SR 299 / JFE 2024 |
| K2-aucpre-01 / K2-aucpost-01 on ZN, ZB, ZT (E.3) | SUPPORTS | "S3: 2015-2024 ... 0.593∗" (10-year yield pressure, about half the full sample); "Formal F-tests confirm that yield pressure declines significantly after 2014 for the 3- and 10-year notes." | SR 1188 Table 2, p. 20 |
| K2-aucpre-01 / K2-aucpost-01 on ZF (E.3) | WEAKENS (power, not sign) | "S3: 2015-2024 ... 4.482∗∗∗" (5-year price pressure, both legs, cash): about 3.4 ZF ticks per leg if split evenly (0.663 bp/tick), above ZF's 1.97-tick hurdle. The E.3 screen saw about 15 five-year auctions in 299 dates. A Tier B there is weak evidence against it. Already noted by E.20's ZF reader; no new candidate. | SR 1188 Table 3 |
| K2-cp1-01 and the bond leg of E20H6 (ROD momentum) | SUPPORTS | "the bond market results remain positive but insignificantly so"; bonds 2000-2020 "1.53*** (3.61) | 0.47" vs 1974-1999 "3.19*** (8.38) | 1.28" | Baltussen et al. 2021 |
| K2-monthend-01 (E.3) and E23-MEZNh5 NULL | WEAKENS (mildly) | "2015-2019 ... 10-Year 0.13***" (last day, 10-year zero, close-to-close): the published month-end effect was still present in 2015-2019, so the intraday screen's failure may be about timing or window (overnight share unknown), not absence | Hartley, Schwarz 2019 subperiod table |
| E16-H2 (month-end NQ/ZN pair) FAIL | SUPPORTS [secondary-only] | search summary of the abstract: calendar signal moves bonds "about 2 bps over the next trading day", too small for ZN's leg to matter | Harvey, Mazzoleni, Melone 2025 (full text not fetched: terms) |
| V38 "no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip" | WEAKENS | "Prices increase notably in the morning, with the 10-year Treasury rising by over 10 bps" (pre-TRA day; 2006-2023 Tradeweb); post-2002 10-year 15.48 bp (t 3.27) | Wang, Zhao 2025 draft |
| V38 (same sentence); E.20 rates_class_notes R6/R7 "FOMC: no pre-drift" | WEAKENS (rates_class_notes R6 reading is OVERTURNED for the long end) | "contrary to the conclusion of Lucca and Moench (2015), we find positive and significant returns (i.e., negative yield changes) on long-term Treasury bonds before the FOMC announcement"; overnight window "approximately 7.26 basis points ... t-statistic of 2.82" | Pan, Peng 2026 draft |
| E.20 ZT reader's classification of the pre-refunding paper ("long end, daily; out of scope") | OVERTURNS (classification, not a trial) | "we analyze intraday price dynamics using high-frequency data ... Prices increase notably in the morning" | Wang, Zhao 2025 draft |

## 9. Fetch log, terms, budget notices

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://personal.lse.ac.uk/loud/Shocks.pdf | 2026-10-18T08:44:20Z | 98ad8352790d1c628cc7941a088680dbfeb2aa7ea9283b883a8606f0fd6e011d | pages/RD2/lou_yan_zhang_2013_shocks.pdf | ok | curl |
| https://ideas.repec.org/a/bla/acctfi/v61y2021is1p1517-1555.html | 2026-10-18T08:44:43Z | 8063b8a8fa43898d6c4f35a524478be1e804a76697ea2ab15ee530e299195fd1 | pages/RD2/ideas_smales_2021_acfi.html | ok (abstract) | curl |
| https://ideas.repec.org/a/eee/jbfina/v170y2025ics0378426624002309.html | 2026-10-18T08:44:50Z | 3c892955e4c96cec6eaba46d28f220dd3c11d83dfe9c0755a5ff1cf9727d6ff8 | pages/RD2/ideas_herb_2025_jbf.html | ok (abstract) | curl |
| https://research-repository.uwa.edu.au/en/publications/05f664a3-3805-4637-ae3c-cb70b0412f65 | 2026-10-18T08:45:08Z | 299475e44d77b637a6e6ef41504e476d8c70b57dff87e134eae68c291bf17cc5 | pages/RD2/uwa_smales_2021_landing.html | ok (no full text deposited) | curl |
| https://osf.io/xucf8/download | 2026-10-18T08:45:47Z | 3fc6bc4f466de4a2a49d11d4598b796a2761119499f2ba5abfdf6cf01476a855 | pages/RD2/wang_zhao_2024_prerefunding.pdf | ok | curl |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188_appendix.pdf | 2026-10-18T08:47:39Z | 666647ed0c36d0e7c95326c988068cd4764099bd92345c342cb3b1dfc53d8298 | (deleted: HTML not-found page) | ok (wrong URL; appendix not public) | curl |
| https://www.newyorkfed.org/research/staff_reports/sr1188.html | 2026-10-18T08:47:51Z | 1d0daa6dc947414e028b261d73f8acacb5df156b0038ee58a4256c72dc318659 | pages/RD2/nyfed_sr1188_landing.html | ok (links only the main PDF) | curl |
| https://research.aalto.fi/en/publications/675214fe-ee5b-4cf6-b1a3-6e72f6ebaac5 | 2026-10-18T08:48:12Z | 4785cfcd6e13b4eb80fe0b1bc9fdc92dbe45e697d31ad74e0d8312e7e819801a | pages/RD2/aalto_etula_dashforcash_landing.html | ok | curl |
| https://research.aalto.fi/files/40965155/hhz054.pdf | 2026-10-18T08:48:29Z / 08:48:41Z | - | none | blocked (403; scrapling get: Cloudflare stub) | curl, scrapling get |
| https://aaltodoc.aalto.fi/server/api/core/items/1011f043-edd1-4cb2-9694-b1216d77561f/accessStatus | 2026-10-18T08:49:58Z | c1e2559dd40aae2d6ed5a29fa6c17663f72f6804a4ea5be42537d0086d6214bd | pages/RD2/aalto_thesis_accessstatus_2026-10-18.json | ok (metadata.only) | curl |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr299.pdf | 2026-10-18T08:55:44Z | 49511bc1e73d45af3973b4ed264093dc707517d5360a433dcd4620afac5b3ee6 | pages/RD2/nyfed_sr299_fleming_nguyen_rosenberg.pdf | ok | curl |

Re-read from disk (no refetch): SR 1188, Hartley-Schwarz, Liberty Street close post (ZN folder),
Pan-Peng (ZT folder), Baltussen (E.13 InfoSource), E.0 K2 research log.

Terms lines appended to terms/terms_log.md by RD2: osf.io (allowed one at a time),
ideas.repec.org (allowed, abstract pages), research-repository.uwa.edu.au (allowed one at a time),
research.aalto.fi (allowed one at a time; PDF blocked by Cloudflare), www.edhec.edu (forbidden:
reproduction of downloadable documents without authorization; nothing fetched), www.newyorkfed.org
(cites E.20's reading). LSE (personal.lse.ac.uk) and NBER (forbidden) already logged by other readers.

Budget notices:
- 2026-10-18T08:43:38Z (01:43 PDT): Firecrawl firecrawl_search returned "Insufficient credits to perform
  this request" (3 calls). Firecrawl unused afterwards. Firecrawl credits ran out; adding credits or
  upgrading at https://www.firecrawl.dev/billing/bw5epbcjrpzvwg0ds2wf0wh7xf408gb7 restores it.
- 2026-10-18T08:50:13Z: OpenAlex HTTP 429 with "retry-after: 54449", "x-ratelimit-remaining-usd: 0"
  (the daily budget of the shared IP/email is exhausted). OpenAlex calls made before it: 4 batches
  (searches and cites lists, scratch RD2/oa/).
- 2026-10-18T08:53Z: Semantic Scholar keyless: 429 three times (60 s waits): throttled.
- WebSearch calls by RD2: 10 of 45.

## 10. Unfinished and unverified

- Forward citations of Pan-Peng, Wang-Zhao, SR 1188 and Hartley-Schwarz after 08:50Z: not listed
  (OpenAlex budget gone, S2 throttled, Firecrawl out of credits). Before that, OpenAlex showed SR 1188
  0 citers, Hartley-Schwarz 3 (Hartley 2020, Wang-Zhao x2) and Herb 2025 1 (unrelated).
- Smales 2021 (A&F) full text: SSRN only; abstract only [secondary-only]. Smales 2020 GFJ: as E.0.
- Herb 2025, Sigaux 2024, Amin-Tedongap 2023, Krohn-Vala 2025 (SSRN 5207418): abstracts or citations
  only, no full text (SSRN blocks automation; not found elsewhere).
- Etula et al. 2020 (Dash for Cash): blocked (Cloudflare); its Treasury month-end claim is cited only
  through Wang-Zhao.
- Harvey-Mazzoleni-Melone full text: terms forbid (EDHEC, NBER); [secondary-only].
- KSSW 2019, Lucca-Moench, Indriawan-Jiao-Tse, Zhang-Wang-Li, Safari-Schmidhuber, CFTC TN note and
  Robeco: no deeper read beyond E.20's notes (lower relevance: unsized, not causal, or not rates-specific).
- Whether Pan-Peng's 7.26 bp is a ZN futures return or a cash 10-year return: the text says "10-year
  Treasury return" while Figure 2 plots futures; both conversions given.
- TRA dates for 2025-2026 not fetched; Treasury press-release terms not checked.
