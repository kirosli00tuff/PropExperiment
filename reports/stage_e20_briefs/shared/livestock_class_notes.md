# Livestock class notes (LE, HE): intraday evidence since 2015

Written by ProductReader-LE-OpusHigh (Stage E.20 Part A), 2026-10-11, 17:36-17:58Z. These notes are for the HE
reader and the lead. Full rows, conversions and fetch log: `reports/stage_e20_briefs/product_LE.md` section 1.
Raw pages and quote files: `reports/stage_e20_briefs/pages/LE/`. The HE reader converts with HE's own price level and tick.

## Bottom line

No post-2015 primary source sizes an intraday (within the 08:30-13:05 CT day session) return effect for live cattle or
lean hogs. The livestock-specific rows that exist are:

1. **Baltussen, Da, Lammers, Martens (JFE 2021), Table B3 Panel B** (on-disk copy
   `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md`, lines 3782-3784). Columns: βONFH, R2, R2OOS,
   βONFH (joint), βM, βSLH, R2, R2OOS, βROD, R2, R2OOS (x100; Newey-West t in parentheses).
   - FC: "| FC | 0.06(0.08) | -0.01 | -0.06 | 0.01(0.02) | -1.04(-1.22) | 1.99(0.83) | 0.03 | -0.19 | -0.34(-0.72) | -0.00 | -0.04 |"
   - LC: "| LC | -0.01(-0.01) | -0.01 | -0.05 | -0.03(-0.04) | 0.01(0.01) | 6.14***(2.77) | 0.19 | 0.01** | 0.42(1.03) | 0.00 | -0.05 |"
   - LH: "| LH | 0.56(0.87) | 0.00 | -0.04 | 0.58(0.89) | -0.98(-1.18) | 3.30*(1.76) | 0.08 | -0.06 | 0.03(0.06) | -0.01 | -0.06 |"
   - Reading: rest-of-day to last half-hour momentum is **null for LC, LH and FC**. LC's second-to-last half hour (SLH) is
     significant (t 2.77) and LH's is marginal (t 1.76), with tiny out-of-sample R2.
   - Sample hours (Table A3): "| Live cattle futures | LC | 1984-08-14 | 2020-05-01 | 8797 | 08:30-13:05 | Softs |" and
     "| Lean hogs futures | LH | 1981-04-03 | 2020-05-01 | 9499 | 08:30-13:05 | Softs |".
   - Fig. 4(c) (2006-06..2020-05, NW t of r_LH on r_ROD, as transcribed in the copy): "| LC | 3.0 | 0.3 |",
     "| LH | 7.2 | -0.6 |", "| FC | 1.6 | -1.6 |".
   - Class rows (commodities, which include the livestock): Table 6 η(rROD) 4.34%/yr, SR 1.42 (line 1742). Table 5
     2000-2020 slope 1.04 (t 2.86) (line 1668). Softs group βROD 0.65 (t 2.16), R2OOS -0.01 (line 3715).
2. **Janardanan, Qiao, Rouwenhorst**: working paper (Feb 2017, `pages/LE/janardanan_etal_2017_wp_ou.pdf.txt`) and JFM 39(8)
   2019. Next-day close-to-close return after limit days, Bloomberg daily, 1991-01-07..2016-05-23 (WP Table 2, p. 13,
   regression with contract fixed effects, t clustered by time):
   - All limit days, bup: "LC 0.57% (4.07)  LH 0.44% (2.53)"; bdown: "LC -0.41% (-1.99)  LH -0.88% (-4.24)".
   - No consecutive limit days, bup: "LC 0.36% (2.41)  LH 0.20% (1.23)"; bdown: "LC -0.08% (-0.50)  LH -0.53% (-3.23)".
   - 90% limit moves, bup: "LC 0.20% (2.23)  LH -0.03% (-0.12)".
   - WP Table 3 (p. 16), the options-implied limit-day price forecasting the next day:
     - close-to-open b: LC 0.39, LH 0.96; R2: LC 49.2%, LH 94.1%;
     - close-to-close b: LC 0.34, LH 0.01; R2: LC 19.9%, LH 0.0%.
     - Reading (mine): for both, the forecastable part is in the price by the next open, and the open-to-close remainder
       is not shown to continue. The papers report no open-to-close split.
   - JFM 2019 (Firecrawl quotes, `pages/LE/janardanan_qiao_rouwenhorst_2019_jfm_quotes.md`), pooled over 12 commodities:
     "the next‐day return (t = 1) is on average 56 basis points"; "29 basis points" without consecutive limits; "−53 basis
     points" and "−27 basis points" after limit down; "Cumulative returns show no reversal over the next 2 weeks". LH
     limit share of days: "| LH | 1.96 | 1.78 |"; LC "| LC | 1.76 | 1.60 |" (up %, down %).
3. **USDA livestock reports are daily or overnight events, and their effect has decayed.**
   - Karali, Isengildina-Massa, Irwin, JARE 2019 (`pages/LE/karali_isengildina_irwin_2019_jare_quotes.md`): after-hours
     reports are dated to the next trading day. Cattle report-day variance ratio 2000-2016 is "1.08 | 0.43" (p).
     Live-cattle marketings surprise +0.102 pp per 1%, post-2000. Hogs: "MarketingPost-2000 | -0.754*** (0.182)" and
     "BreedingPost-2000 | -0.060 (0.206)".
   - Isengildina-Massa et al., NCCC-134 2016 (`pages/LE/isengildina_karali_irwin_adjemian_2016_nccc134_quotes.md`): Hogs
     and Pigs reaction "during the most recent 2007-2016 sub-period was not significantly different from zero" (their Table 13; the passage
     returned does not name the market). For lean hogs, Hogs and Pigs impact fell from 0.797 to 0.649.
   - These need analyst-survey surprise data and are close to close, so they are not intraday features.
4. **He and Serra (AJAE 2022)**: intraday LE and HE limit-move study, 2014-2019. Abstract only (OpenAlex): "price limits
   neither reduce volatility nor improve liquidity ... significantly higher volatility and lower liquidity when trading
   resumes". No return sizing. [secondary-only]

Checked and empty for livestock:
- Aalto thesis: no commodities (`shared/aalto_thesis_notes.md`).
- Borgards et al. 2021: 20 commodities, no livestock.
- Joseph 2015 dissertation: the intraday essay is soybeans.
- He, Serra, Garcia 2021 (flash events): liquidity only.
- Couleau et al. 2017/2018: volatility only.
- Gousgounis and Onur: pit closure, liquidity.
- E.0's K6 log (`reports/stage_e0_research_K6.md`) found nothing intraday for livestock either.

## Exchange facts useful to both readers (CFTC-hosted CME filings, `pages/LE/cftc_*.pdf.txt`)

- Live cattle:
  - initial limit $0.030/lb at least from 2014-12 (CME 14-575, filed 12/18/14) to trade date 2020-10-04;
  - CME 20-352: "adjust the current, initial daily price limit for Live Cattle futures from $0.03 to $0.04 per pound",
    effective trade date 2020-10-05;
  - expanded limit 150% ($0.045, then $0.06);
  - expiring month's last two days $0.050 from 2014-09-08 (CME 14-109).
  - Not verified: no 2015-2019 LE limit filing was read.
- HE limits are not covered here (HE's backward window is 2017-07..2019-05; the 2019+ HE table is in rules/price_limits.py).
- CME 20-352 Exhibit 4: average June LE settle "ALL $117.08" (2015-2020) per cwt. Its narrative says "Live Cattle settled
  at limit on seven straight days" (2020-03-31..04-08).
- Livestock session eras (calendar `data/calendars/hist2010/livestock.json`, E.16 R-C3/R-S5):

| Dates | Session (CT) |
|---|---|
| to 2014-10-24 | 17:00-16:00 Globex, Monday 09:05 |
| 2014-10-27..2016-02-26 | 08:00-16:00 (Fri 13:55), Monday 09:05 |
| from 2016-02-29 | 08:30-13:05 |

  Settlement 13:00, with window 12:59:30-13:00 from 2014-12-15 (E.16 S27). HE's backward window (from 2017-07) lies
  wholly in the third era.
