# RD8: re-dig of the E.20 planning brief's literature leads (Stage E.25)

Reader: RD8-RedigE20Planning-OpusHigh. Started 06:21 PDT 2026-10-18 (`TZ=America/Vancouver date`).
Input: reports/stage_e20_briefs/literature_planning_2026-10-10.md (findings 1-9, shortlist 1-5, 17 source URLs).
No market data read; no outcome computed. Ratios against the hurdle are the lead's.

## 0. Lead triage (which leads RD8 re-dug, which are owned elsewhere)

| Planning-brief lead | Status before RD8 | RD8 action |
|---|---|---|
| F1 Baltussen et al. ROD->LH; Adams et al. 2026; firmtape; Aalto thesis; Rosa 2022 | re-read by RD1 (equity), RD2 (rates), RD4 (FX/ags), RD5 (gamma), R1, R12 | skipped; cite those files |
| F2 Overnight drift (Boyarchenko-Larsen-Whelan; Liberty Street 2026-07) | full text + decay read by R12 and R13 (pages/R12, pages/R13) | skipped; verdict check cites R12/R13 |
| F3 Closing-auction distortions (Bogousslavsky-Muravyev, JFM 2023) | not read by any E.20 or E.25 reader (no row in r0_e20_evidence_index, r0_prior_sources) | RE-DUG: full text (AEA 2021 conference draft, Dec 2020), forward citations |
| F4 Pre-announcement drift (Kurov-Sancetta-Strasser-Wolfe, JFQA 2019; "Drift Begone" 2022) | E.20 ZN/CL readers had the ECB WP 1901 full text; R6 quoted Table 3; "Drift Begone" unread; no forward-citation pass | RE-DUG: Tables 4-5 and profit section re-read, JFQA abstract, Drift Begone abstract, 73 forward citations (OpenCitations) |
| F5 lunchtime reversal, settlement windows, ES->ZN, CL->CAD lead-lag | R13 (lead-lag) and E16-H1 (settlement) | skipped |
| F6 Noise-area momentum (Zarattini-Aziz-Barbon 2024) | R10 owns all Zarattini papers (full text, FAQ, decay) | skipped; verdict check cites R10 |
| F7 Base rates (Chague et al.; Topstep 2025 stats) | R8 owns prop outcomes (its file is a cut stub) | not re-dug (SSRN not fetchable by automation) |
| F8 ML intraday (Aleti et al.; Huddleston et al.; Frontiers 2026) | Aleti/Huddleston in RD1 | Frontiers terms unreadable (JS shell): not fetched |
| F9 Passive execution (Kurov-Zabotina 2005; Lalor-Swishchuk; DeLise 2024) | Lalor-Swishchuk in R18; DeLise and Kurov-Zabotina unread | RE-DUG: DeLise full text (arXiv), Kurov-Zabotina abstract, forward citations count |

## 1. Answer (at most 250 words)

Three leads in the planning brief had never been read past a summary: closing-auction distortions,
pre-announcement drift (sized only conditionally), and the passive-fill proofs. None of them yields a
prop-compatible, ex-ante tradable intraday effect above 1.5 x the D8 round trip on a micro or ZN.

- Closing auction (Bogousslavsky-Muravyev): the distortion is in cash-equity closing prints, not in
  futures. The index-level (cap-weighted) deviation averages 0.93 bp in absolute value, about 0.56 ES
  points or 2.2 MES ticks at ES 6,000, below the MES hurdle of about 3.0 ticks even with perfect foresight
  of its sign. It reverses after 16:00 ET (half within 20 minutes, the rest overnight), after the Topstep
  15:10 CT flatten. V34's drop is supported.
- Pre-announcement drift (Kurov et al.): the large numbers (ES 0.139% per 1-sd surprise for ISM
  Non-manufacturing, about 33 MES ticks at ES 6,000) are sign-adjusted by the surprise, which is unknown
  before the release. The paper gives no ex-ante rule; its order-flow proxy earned "one order of
  magnitude lower". The sample ends 2014-03; drift was negligible before 2008; 73 forward citations
  contain no post-2015 US replication on ES/ZN; the only follow-up by the authors (UK, 2022) shows the
  drift dies when release security tightens. The program's ZN version (K2-predrift-01) was Tier B. V34's
  drop is supported. The equity version (K1-predrift-01) was never screened (excluded at E.0).
- DeLise: on ZN a resting fill is followed by a -0.45 tick mid move, cancelling most of the half-tick
  saving.
V38 is supported by every source RD8 read.

## 2. Candidate hypotheses

Zero proposable candidates. One unsized lead is recorded for completeness (RD8-L1). It is not a
candidate under V31/V38 because no source sizes an ex-ante rule.

| id | hypothesis | instruments | entry window CT | hold | published effect | gross per trade | grade | owned | overlap |
|---|---|---|---|---|---|---|---|---|---|
| RD8-L1 (unsized, not proposable) | pre-release sign momentum on the KSSW "strong drift" 09:00 CT releases: sign of the [t-30, t-x] return, hold through t+5 min | MES (ES path), ZN | 08:30-09:00 CT on ISM Mfg/Non-mfg, pending/existing home sales, CB confidence (09:00 CT); IP 08:15 CT; GDP prelim 07:30 CT | about 15-35 min | only ex-post, surprise-signed coefficients (ES 0.139% / ZN -0.042% per 1-sd surprise, ISM NM, 2008-01..2014-03) | unknown ex ante | working-paper (ECB WP 1901) / peer-reviewed (JFQA 2019, abstract only) | yes (1-min bars, release calendars incl. ISM) | ZN version = K2-predrift-01 (ISM Services, Tier B); ES version = K1-predrift-01 (excluded at E.0, 0 trials); E-H1/E-H2 differ (overnight hold; post-release) |

## 3. Evidence table

| # | claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|---|
| E1 | Closing-auction share of US equity volume | 7.5% (2018) vs 3.1% (2010) | "The closing auction accounts for a striking 7.5% of daily volume in 2018, up from 3.1% in 2010." | Abstract, p. 1 | Bogousslavsky and Muravyev, "Who Trades at the Close?", AEA 2021 conference draft dated 2020-12-03, https://www.aeaweb.org/conference/2021/preliminary/paper/H9T4hef7 ; published J. Financial Markets 66 (2023), doi 10.1016/j.finmar.2023.100852 | working-paper (published version peer-reviewed, not read) | pages/RD8/bogousslavsky_muravyev_aea2021.pdf (.txt) |
| E2 | Closing prices deviate and revert | half shortly, fully overnight | "they often deviate from closing quote midpoints, but the deviations revert by half shortly after the close and fully overnight" | Abstract, p. 1 | same | working-paper | same |
| E3 | Average stock-level deviation | 8.12 bp (20.6 small, 2.66 large) | "Auction price deviations are 8.12 bps on average and range from 20.6 bps for small stocks to 2.66 bps for large stocks." | Sec. 3.2, p. 13 | same | working-paper | same |
| E4 | Large ETFs (SPY, QQQ) | 3.63 bp mean, 16.32 bp 99th pct | "We also study price deviations for large ETFs (SPY, QQQ, and S&P sectors) and find that they behave similar to large stocks with average deviation of 3.63 bps, and 99th percentile of 16.32 bps" | fn. 14, p. 13 | same | working-paper | same |
| E5 | Index-level (cap-weighted, absolute) deviation | 0.93 bp; max 12 bp (2011-08-11) | "Aggregate price deviation is 0.93 bps on average, or about three billion dollars per day in aggregate." ... "the largest aggregate deviation was 12 bps on August 11, 2011" | Sec. 3.2, p. 15 | same | working-paper | same |
| E6 | Reversal share by next morning | 85% (110% large stocks) | "the coefficient is -0.85, or 85% of the deviation is reversed by the next morning. For large and small stocks, 110% and 85% of the price deviation is reversed." | Sec. 3.3, p. 16 | same | working-paper | same |
| E7 | Reversal timing: after the close | half within 20 min after 16:00 ET | "the price reverts half-way to the pre-close midquote in just twenty minutes after the close" | Sec. 3.4, p. 19 | same | working-paper | same |
| E8 | Pre-announcement drift exists for some releases (JFQA) | 9 of 20; about 40% of the move; starts about 30 min early | "Nine of the 20 announcements that move markets show evidence of substantial informed trading before the official release time. Prices begin to move in the 'correct' direction approximately 30 minutes before the release time. The preannouncement price drift accounts on average for approximately 40% of the total price adjustment." | Abstract | Kurov, Sancetta, Strasser, Wolfe, JFQA 54(1) 2019 449-479, doi 10.1017/S0022109018000625 (RePEc abstract page) | peer-reviewed [secondary-only: abstract] | pages/RD8/repec_kssw_jfqa.html |
| E9 | Sample is 2008-01..2014-03, ES and ZN | n/a | "We study the impact of announcements on second-by-second E-mini S&P 500 stock index and 10-year Treasury note futures from January 2008 to March 2014." | Non-technical summary | Kurov et al., ECB WP 1901 (May 2016), E.20 copy | working-paper | reports/stage_e20_briefs/pages/CL/kurov_etal_ecbwp1901.pdf (sha256 6bec58a8...; .txt) |
| E10 | Size of drift, ES, ISM Non-mfg (largest ES coefficient) | 0.139% per 1-sd surprise, [t-30 min, t-5 s]; R2 0.12 | "ISM Non-manufacturing index 0.139 (0.033)*** 0.12 -0.042 (0.009)*** 0.15" | Table 4, p. 16 | same | working-paper | same |
| E11 | Size of drift, other ES strong-drift releases | 0.023-0.091% per 1-sd | "CB Consumer confidence index 0.023 (0.035) 0.01 -0.036 (0.009)***" ... "Pending home sales 0.087 (0.031)*** 0.09 -0.028 (0.007)***" | Table 4, p. 16 | same | working-paper | same |
| E12 | Pre-drift share of total move | ES mean 49%, ZN mean 39% | "Mean 49% 39%" (rows ISM Non-manufacturing 69%/59% ... CB Consumer confidence 15%/37%) | Table 5, p. 17 | same | working-paper | same |
| E13 | The coefficient needs the surprise (ex-post sign) | n/a | "Following Bernile et al. (in press), we invert the sign of returns for negative surprises." | Sec. 4.2, p. 17 | same | working-paper | same |
| E14 | Earlier-window bond drift is tiny | about 1 bp | "Panels a) and b) for the bond market appear to show some drift (only about one basis point) starting about 60 minutes prior to the announcement." | fn. 16, p. 19 | same | working-paper | same |
| E15 | Profit estimate is aggregate and surprise-conditioned | about $262,000 per release, market-wide | "the average profit per announcement release in the E-mini S&P 500 futures market is about $262,000" ... "we compute the order flow over the [t - 30min, t - 5sec] window and multiply it by the sign of the surprise" | Sec. 4.3, p. 23 | same | working-paper | same |
| E16 | Ex-ante proxy (order flow without surprise) is far weaker | "one order of magnitude lower" | "simply trading in the direction of the order flow produces profits that are one order of magnitude lower than trading the pre-announcement price drift with information on the surprise" | Sec. 4.3, p. 24 | same | working-paper | same |
| E17 | Spread in the sample era | ES 0.020%, ZN 0.013% median | "The median bid-ask spread is 0.020% for the E-mini S&P 500 futures and 0.013% for 10-year Treasury notes futures." | Sec. 4.3, p. 23 | same | working-paper | same |
| E18 | Drift was negligible before 2008 | 3 releases pre-2008 | "the pre-announcement drift before 2007 is negligible. Only three announcements exhibit a pre-announcement price drift during the pre-2008 period" | Sec. 4.4, p. 24 | same | working-paper | same |
| E19 | Authors' follow-up: drift dies when release security tightens (UK) | n/a | "This preannouncement price drift weakens with the end of the prerelease access." | Abstract | Kurov, Sancetta, Wolfe, "Drift Begone!", J. Int. Money and Finance 128 (2022) 102718 (RePEc abstract) | peer-reviewed [secondary-only: abstract] | pages/RD8/repec_drift_begone.html |
| E20 | Forward citations of KSSW | 73 citing works (OpenCitations, 2026-10-18) | (count of rows in the API response) | n/a | api.opencitations.net/index/v2/citations/doi:10.1017/s0022109018000625; titles via Crossref | exchange-regulator n/a; metadata | pages/RD8/oc_citations_10.1017_s0022109018000625.json; oc_kssw_citing_titles.json |
| E21 | Treasury market less efficient in the 5 min before news (forward citation) | n/a | "We find that the U.S. Treasury market is less efficient in the five-minute interval before news arrival." | Abstract | Lin, Lo, Qiao, J. Banking and Finance 133 (2021) 106252 (RePEc) | peer-reviewed [secondary-only] | pages/RD8/repec_lin_lo_qiao.html |
| E22 | Limit fills on ZN are followed by an adverse mid move | -0.45 ticks empirical (-0.48 model) | "Et [dt |f ] -0.48 ticks" / "Êt [dt |f ] -0.45 ticks" ... "Table 2: Theoretical and empirical drift following order fills. Numbers presented in number of ticks." | Table 2, p. 20 | DeLise, "The Negative Drift of a Limit Order Fill", arXiv 2407.16527 (TT simulator, 10-year note futures) | working-paper | pages/RD8/delise_2407.16527.pdf (.txt) |
| E23 | The fill probability given an adverse move | 0.99 | "P (f |D) 0.99" | Table 1, p. 20 | same | working-paper | same |
| E24 | E-mini tick is binding (2005) | n/a | "the current minimum tick sizes of the E-mini S&P 500 and E-mini Nasdaq-100 futures contracts act as binding constraints on the bid-ask spreads" | Abstract | Kurov and Zabotina, J. Futures Markets 25 (2005) 79-104 (RePEc) | peer-reviewed [secondary-only] | pages/RD8/repec_kurov_zabotina.html |

Conversions (inputs for the lead; price levels stated):
- E10 ES ISM NM 0.139% at ES 6,000 = 8.34 points = 33.4 MES ticks (0.25). Conditional on the surprise
  sign (E13); the ex-ante equivalent is not published (E16 says the order-flow proxy earned about a tenth).
- E10 ZN ISM NM -0.042% at ZN 110 = 0.0462 points = 2.96 ZN ticks (1/64), conditional on the surprise;
  hurdle 1.75 ticks. Table 5's ZN figure for the same release, -0.058%, = 4.08 ticks (conditional).
- E14 bond drift about 1 bp at ZN 110 = 0.70 ZN ticks (below the 1.75-tick hurdle, and conditional).
- E5 index-level auction deviation 0.93 bp at ES 6,000 = 0.56 points = 2.2 MES ticks (MES hurdle about
  3.0 ticks; absolute value: direction is not known before the auction). E4 SPY 3.63 bp = 2.18 points =
  8.7 ticks, but in the ETF, and it reverts after 16:00 ET.
- E22 versus the nominal half-tick saving of a passive fill: +0.5 - 0.45 = about +0.05 ZN tick per fill
  (DeLise's own framing; the lead computes any saving).

## 4. Negative evidence (nulls, decay, after-cost)

- Pre-announcement drift is pre-2015 only: sample 2008-01..2014-03 (E9), negligible before 2008 (E18).
  None of the 73 works that cite the JFQA paper (titles read, pages/RD8/oc_kssw_citing_titles.json) is
  a post-2015 US replication on ES or ZN. The relevant follow-ups found: the pre-FOMC drift "essentially
  disappeared after 2015" (Kurov-Wolfe-Gilbert 2021, quoted by R6), and the UK release-policy drift
  "weakens with the end of the prerelease access" (E19). The authors' own later papers (Crossref
  author search, 2020-2026) do not revisit US macro pre-drift.
- The headline sizes are not tradable as published: surprise-signed (E13, E15); the ex-ante order-flow
  version earned "one order of magnitude lower" (E16).
- The program's direct ZN test of the mechanism, K2-predrift-01 (ISM Services, sign of the 08:30-08:49
  move, 15-min hold), was Tier B.
- Closing auction: the stock-level numbers (E3) shrink to 0.93 bp at index level (E5); the reversal
  happens after the cash close (E7) and overnight (E6).
- Passive fills: DeLise's ZN result (E22, E23) matches Lalor-Swishchuk's 88.8% adverse share on ZN (R18):
  fills arrive almost only on adverse moves.

## 5. Data and cost

- RD8-L1 needs 1-minute bars (owned: ES 2010-2024, MES, ZN; research window owned) and the release
  calendar. The program owns FOMC, CPI, NFP, PPI, GDP and ISM calendars (section 4 of the brief). Pending
  home sales, existing home sales, CB consumer confidence and industrial production times are not listed
  as owned (partial).
- Closing auction: would need NYSE/Nasdaq closing imbalance feeds and stock prints: not owned, not priced.
- No Databento price page was read (none needed).

## 6. Prop compatibility

- RD8-L1: entries 07:30-09:00 CT, flat by 09:05 CT: inside the Topstep day. P06: a full-size position into
  a scheduled major release is not allowed; ISM, housing and confidence releases may fall under it; the
  lead must check the P06 release list (R9). Automation allowed via TopstepX API; not HFT.
- Closing auction: incompatible (the reversal starts after 16:00 ET = 15:00 CT and runs overnight; flat by
  15:10 CT).
- Passive fills: TopstepX fills a limit only on trade-through (DECISIONS C6, via R18), which is worse than
  the queue model DeLise used.

## 7. Overlap with tested mechanisms

- RD8-L1 vs K2-predrift-01 (ZN/ZB, ISM Services, sign of 08:30-08:49 move, 15-min hold, Tier B): same
  mechanism on ZN; RD8-L1 adds six more releases and the ES path. vs K1-predrift-01: excluded at E.0
  with 0 trials as an MES E-family re-run (stage_e10_catalog_rulings.md line 51). vs E-H1 (overnight
  hold into FOMC/CPI/NFP) and E-H2 (post-release momentum): different window and releases. Kurov et al.
  find no NFP pre-drift ("Non-farm employment 0.018 (0.016) 0.00 0.000 (0.009)", Table 4) and only
  "some evidence" for CPI in ES ("Consumer price index -0.051 (0.013)*** 0.08 0.001 (0.009)").
- Closing auction vs E16-H1 (settlement-window momentum) and K1 closing windows: those are futures
  windows before 15:00 CT; the auction effect is after it.

## 8. Earlier verdicts the deeper reading supports, weakens or overturns

- V38 ("no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip"):
  SUPPORTS. No RD8 source gives a post-2015 ex-ante intraday effect on any of the 17 roots. Kurov et al.'s
  sample ends 2014-03 ("from January 2008 to March 2014") and its sizes are surprise-conditioned ("we
  invert the sign of returns for negative surprises"). Closing-auction deviations are in stock prints, at
  0.93 bp at index level.
- V34 drop, closing-auction distortions: SUPPORTS. "the price reverts half-way to the pre-close midquote
  in just twenty minutes after the close"; "85% of the deviation is reversed by the next morning". Both
  happen after the 15:10 CT flatten, and the index-level size (0.93 bp, about 2.2 MES ticks) is under the
  MES hurdle even with the sign known.
- V34 drop, pre-announcement drift ("unsized"): SUPPORTS, and the gap is wider than "unsized". The paper
  sizes only the surprise-signed drift. Its ex-ante proxy: "simply trading in the direction of the order
  flow produces profits that are one order of magnitude lower". Decay: "the pre-announcement drift before
  2007 is negligible", and the authors' UK follow-up says the drift "weakens with the end of the
  prerelease access". Note for the lead: the equity-index version (K1-predrift-01) has never been
  screened.
- V34 drop, overnight drift: SUPPORTS (not re-read by RD8). Cited from R12/R13: "Five additional years
  of data later, that pattern appears to have faded" (Liberty Street 2026-07; R13 E18, R12 line 67).
- V34 drop, noise-area momentum: not re-read (R10 owns it). See R10's verdict section.
- K2-predrift-01 Tier B (E.4 K2): SUPPORTS. The bond pre-drift in Kurov et al. is small outside the last
  30 minutes ("only about one basis point"). ISM Services has the largest ZN coefficient among the
  strong-drift releases (-0.042%, surprise-signed; GDP advance, in the "some evidence" group, is -0.067%). An ex-ante sign rule captures only part of it.
- Passive-execution closures (D.1f C-H4 trade-through fill model; planning-brief finding 9): SUPPORTS.
  DeLise: "Êt [dt |f ] -0.45 ticks" on 10-year note futures, with fills on 99% of adverse moves.

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://api.crossref.org/works?query.bibliographic=... (3 DOI lookups) | about 2026-10-18T13:23:50Z | - | not saved (metadata printed) | ok | curl |
| https://api.opencitations.net/index/v2/citations/doi:10.1017/s0022109018000625 | 2026-10-18T13:24:06Z | 4f5328353f78862b3a47de449f66ac3343aee44d32aa9c1ef6b3b62a743fd110 | pages/RD8/oc_citations_10.1017_s0022109018000625.json | ok (73 rows) | curl |
| https://api.opencitations.net/index/v2/citations/doi:10.1016/j.finmar.2023.100852 | 2026-10-18T13:24:13Z | 665fdece07a0edb7cbb4edddea4f85a432798126b4b0bc0bcfd3cdbab0ef67ab | pages/RD8/oc_citations_10.1016_j.finmar.2023.100852.json | ok (21 rows) | curl |
| https://api.opencitations.net/index/v2/citations/doi:10.1002/fut.20119 | 2026-10-18T13:24:20Z | c96a79e7b29a7c57469b955d2b7ab3c1e5f5e96fc4aaea5e0163487b59c24d77 | pages/RD8/oc_citations_10.1002_fut.20119.json | ok (15 rows) | curl |
| https://api.crossref.org/works?filter=doi:... (citing-work titles, 5 batches) | about 2026-10-18T13:24:30Z | 6b404830be015c4a2c0982bc428378f0d7471741c65b034af76bbd4541bad0a0 / e2c2ea5a2985282e1f3d24a6a3660310e869b3520d8e87297ff0ac7d22b05fe6 | pages/RD8/oc_kssw_citing_titles.json / oc_bm_citing_titles.json | ok | python urllib |
| https://api.crossref.org/works/<doi> x 8 (abstract metadata) | about 2026-10-18T13:25:00Z | see pages/RD8/crossref_*.json | pages/RD8/crossref_*.json | ok | curl |
| https://pure.royalholloway.ac.uk/en/ (terms search) | about 2026-10-18T13:25Z | - | scratch only | blocked (Cloudflare challenge) | curl |
| https://www.aeaweb.org/conference/2021/preliminary/paper/H9T4hef7 | 2026-10-18T13:26:01Z | 3ee17253b0d98a660489c0934ac3f674cd01b483e9f55f62f3edb987ced8b5da | pages/RD8/bogousslavsky_muravyev_aea2021.pdf | ok (the URL serves the PDF) | curl |
| https://ideas.repec.org/a/eee/jimfin/v128y2022ics0261560622001218.html | 2026-10-18T13:26:35Z | 153a87d4ca3d43906f52257fbe29015dd8d5ae123f6013c579dc6e524619c480 | pages/RD8/repec_drift_begone.html | ok | curl |
| https://ideas.repec.org/a/cup/jfinqa/v54y2019i01p449-479_00.html | 2026-10-18T13:26:41Z | f5d28dcebf49e2fcb1c1a66050a31741c01d68d865afe70516020f5b46306a18 | pages/RD8/repec_kssw_jfqa.html | ok | curl |
| https://ideas.repec.org/a/wly/jfutmk/v25y2005i1p79-104.html | 2026-10-18T13:26:47Z | 271d6a1737de9168e1fce1c8d55b3845b32ff8ac54336785fa966fa00ee4011a | pages/RD8/repec_kurov_zabotina.html | ok | curl |
| https://arxiv.org/abs/2407.16527 | 2026-10-18T13:26:51Z | 3e651a10e7a7f81f8511d25dc26e2a66b97494b7bf622d706a0cd8bcf7608c55 | pages/RD8/arxiv_delise_abs.html | ok | curl |
| https://arxiv.org/pdf/2407.16527 | 2026-10-18T13:27:12Z | 86bdcfe2ae09ea0eefa61b4df434d250d893214d40e4e545ab0eba87069f7aaa | pages/RD8/delise_2407.16527.pdf | ok | curl |
| https://www.frontiersin.org/legal/terms-and-conditions | 2026-10-18T13:27:27Z | 46131dbefe25e574d057f5a34ccbe573174509184a814c03f40cabccbdb7f5a1 | terms/www.frontiersin.org_terms.html | JS shell; terms unread (curl and WebFetch) | curl, WebFetch |
| https://www.skidmore.edu/economics/documents/KSSW2017-PriceDriftBeforeUSMacroeconomicNews.pdf | 2026-10-18T13:28:06Z | b13d13db3883e98fdda647d7f62a184ca81ac03e798d1fcda77a8ebe45ee86c7 | discarded (404 HTML) | blocked (404) | curl |
| https://ideas.repec.org/a/eee/jbfina/v133y2021ics0378426621002119.html | 2026-10-18T13:28:15Z | c952c266f1e12a509a5b3479734f9361bf541dc4eecd19f9c14a4c9484c309ca | pages/RD8/repec_lin_lo_qiao.html | ok | curl |
| https://ideas.repec.org/a/eee/jbfina/v135y2022ics037842662100323x.html | 2026-10-18T13:28:21Z | c17972065df52eedeee6d28444b4c8f1a0fa0ee699964ba9acdcac26bd0d36ae | pages/RD8/repec_park_payroll.html | ok | curl |
| https://api.crossref.org/works?query.author=Alexander+Kurov... (authors' later work) | about 2026-10-18T13:31Z | - | not saved | ok | curl |

Terms: lines appended to terms/terms_log.md for api.crossref.org, api.opencitations.net, www.skidmore.edu,
pure.royalholloway.ac.uk, www.frontiersin.org, and citing the existing aeaweb.org, ideas.repec.org and arxiv.org lines.
Deviation: RD8 overwrote RD3's saved terms/api.opencitations.net_terms.html (13:29:50Z) and restored it
from https://opencitations.net/about at 13:30:10Z. The restored sha256 2ac14be2... differs from RD3's
logged b8b95f52... because the page is dynamic, but the CC0 sentence is present. The Crossref terms
copy was re-saved byte-identical (sha256 7bccbaff..., as logged).
Budget: 6 WebSearch calls (cap 25 for this reader), with no over-budget notice. OpenAlex and Firecrawl
were not called (per spawn message). No Semantic Scholar calls.

## 10. Unfinished and unverified

- JFQA 2019 published tables were not read (Cambridge Core not tried; the Skidmore 2017 draft returned a
  404). The ES/ZN coefficients quoted are from the 2016 ECB WP (7 strong-drift releases of 21). The JFQA
  version's 9 of 20 releases are known from the abstract only.
- The "Drift Begone" full text (Royal Holloway Pure behind Cloudflare; Elsevier paywall) is abstract only.
- Published JFM 2023 version of Bogousslavsky-Muravyev not read; the numbers above come from the Dec 2020
  draft, sample 2010-2018.
- Frontiers 2026 ML study: not fetched (terms unread). Chague et al. and Topstep stats: R8 owns; not
  re-dug.
- Forward citations of Bogousslavsky-Muravyev (21) and Kurov-Zabotina (15) were screened by title only.
  "End-of-Day Reversal" (Baltussen-Da-Soebhag) is covered by RD1/RD5.
- Lin-Lo-Qiao (2021) and Park (2022) are abstract only. Park uses CFTC positions (multi-day), not intraday.
- The Alturki-Kurov (JFM 2021) oil-inventory pre-announcement predictor is a forward citation of KSSW
  but is RD3's source (RD3_redig_energy_metals.md line 8); not re-read here.
