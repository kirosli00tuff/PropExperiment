# Stage E.20 Part A: product file for TN (Ultra 10-Year U.S. Treasury Note futures; vehicle TN)

Reader: ProductReader-TN-OpusHigh (opus, worker-high). Brief: reports/stage_e20_briefs/brief_partA_shared.md.
Work ran 2026-10-11 17:33-17:45 UTC (10:33-10:45 PDT). No data store opened, no bar read, no result file of
E.15/E.17/E.18 or Gate 0 read, no cmegroup.com page fetched (live or archived), no commit.

Root facts used (reports/stage_e20_briefs/root_table.md): tick $15.625 (1/2 of 1/32), D8 RT wall 1.235 ticks =
$19.30, day-session RT mean 1.174 ticks, group rates, O 07:20, C 14:00, F 15:08 CT, backward window
2016-01-01..2019-05-05 (no unit before 2016-01-11, R-S4), search window 2019-05-06..2024-02-29.

Conversion used throughout: TN notional = P x $1,000, so 1 tick = 156.25 / P bp of notional. No public TN price
level was retrieved from a permitted source in this task, so every bp figure is given over the band P = 100..150
(1 tick = 1.56..1.04 bp; D8 RT = 193.0 / P bp = 1.93..1.29 bp; the 1.5x hurdle 1.853 ticks = $28.95 =
289.5 / P bp = 2.90..1.93 bp). The band is illustrative and marked [unverified] as a price level.

## 1. Evidence

**Root-specific finding: no published intraday return study of the Ultra 10-Year contract (TN) since 2015 was
found.** 18 WebSearch queries (TN, "Ultra 10", "Ultra 10-Year", Bloomberg ticker UXY, with intraday, momentum,
reversal, announcement, auction, lead-lag, settlement, time-of-day) and one paper-index search (Firecrawl
research, 2015 onward) returned only product pages, vendor pages, regulator filings, a liquidity note, and
pricing-model papers (pages/TN/search_log.md). This is a gap in what could be found, not evidence that no
effect exists. TN is also absent from Baltussen et al. (2021): their US bond sample is TU, FV, TY, US and UB.

| ID | Effect | Rule | Hold | Gross per trade (bp; TN ticks) | Gross/net | Sample | Decay evidence | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | (absence) TN not in the Baltussen et al. ROD->LH sample | n/a for TN; class rule (ROD -> last half hour) is H6's | last 30 min | none for TN; bond class rows [shared, see shared/baltussen_notes.md] | gross | 16 developed bond futures; US: TU, FV, TY, US, UB; 1974-2020 | class decay [shared, see shared/baltussen_notes.md, shared/aalto_thesis_notes.md] | Baltussen, Da, Lammers, Martens, JFE 142 (2021) 377-403; on-disk copy reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md | primary (absence fact only) |
| E2 | (context, no return effect) TN is one of six CBOT futures buckets in a DV01-volume liquidity study by trading hours | none (volume shares, no return test) | n/a | none | n/a | CBOT futures and TRACE, 2017-07-10..2018-06-01 (229 days) | n/a | Baker, McPhail, Tuckman (CFTC staff note, 2018-12-03), "The Liquidity Hierarchy in the U.S. Treasury Market" | primary (context) |
| E3 | (class pointer, not TN) minute-scale reversion, hours-scale weak trending, pooled over 16 futures including "US 10-year" | trend strength over 2^k minutes predicts the next-minute return | 1 minute (k <= 6: up to ~1 h of lookback) | not reported per trade; minute-scale, below any 60-min hold of the V2.2 clock | gross | TickData end-of-minute, 2010-2023, 16 futures (rates: US, CA, DE, UK 10-year) | none reported per market | Safari, Schmidhuber, arXiv 2501.16772v2 (2025) | primary for what it states; not TN |
| E4 | (class pointer) rates-class ROD->LH and other Treasury-futures intraday effects | see ZN reader | - | planning brief's derived bond figure ~0.9 bp per trade = 0.58..0.86 TN ticks at P 100..150 [unverified: a planning-run derivation, not a quote] | gross | - | - | [shared, see shared/rates_class_notes.md] | unverified here |
| E5 | (class pointer) 10-year auction-day intraday price pressure (prices fall into the auction, recover after) | short before / long after the 10Y auction (K2-aucpre/aucpost already encode the event) | hours | Robeco snippet: "futures prices decline by 6 basis points" before the auction (search snippet only; unit not checked) | gross | 10Y T-note futures 1983-2024 (Robeco); intraday cash/futures 33 years (NY Fed SR1188) | SR1188 snippet: pressure "has not risen in recent years" | Robeco (2025-03 quant chart); Fleming, Liu, Nguyen, NY Fed Staff Report 1188 (2026) | secondary-only (search snippets; not fetched: rates class is ZN's) |
| E6 | (class pointer) post-FOMC drift in long-term US bond futures | multi-day drift after FOMC | ~15 days (not intraday) | n/a | gross | - | - | Indriawan, Jiao, Tse, J. Banking and Finance (2021) | secondary-only (snippet; out of scope: multi-day) |

Verbatim quotes (location; file under reports/stage_e20_briefs/pages/TN/ unless stated):
- E1, Baltussen et al. Table 1 (on-disk copy, lines 913-917): "| US 2-year T-note futures | TU | 8:20 - 15:00 |",
  "| US 10-year T-note futures | TY | 8:20 - 15:00 |", "| Ultra T-bond futures | UB | 8:20 - 15:00 |". A grep of
  the whole copy for "Ultra" finds only the UB row; there is no Ultra 10-Year row.
- E2, cftc_liquidity_hierarchy_2018.pdf.txt lines 113-115: "The 6 buckets correspond to the following contracts,
  which are all listed on the CBOT (Chicago Board of Trade): 2-year T-Note; 5-year T-Note; 10-Year T-Note; Ultra
  10-Year T-Note; T-Bond or 30-Year T-Bond; and Ultra T-Bond or Ultra 30-Year T-Bond." Figure 3 (volume by US,
  Asian, European hours) is an image; no number was extracted.
- E3, arxiv_2501.16772.txt lines 27-29: "Across asset classes, we find that markets are in a trending regime on
  time scales that range from a few hours to a few years, while they are in a reversion regime on shorter and
  longer time scales." Lines 480-481: "The average next-minute return is mostly positive for negative trend
  strength and negative for positive trend strength, so futures prices tend to revert at minute-scales." Sample,
  lines 415-420: "cover the 14-year period 2010-2023" and Table 4 "Interest rates US 10-year Can. 10-year Ger.
  10-year UK 10-year".

Reading of decay and costs. Nothing root-specific exists to show decay. On costs, TN's D8 RT ($19.30; 1.235 ticks)
is above ZN's ($18.28), ZT's and ZF's and below ZB's and UB's, and a tick is 1.0-1.6 bp, so a
class effect must deliver about 1.9-2.9 bp gross per trade to clear 1.5x on TN. The only sized class figure in
hand, the planning brief's ~0.9 bp per trade for bond ROD->LH [unverified derivation], is 0.47-0.70x of TN's D8
round trip: a non-survivor on TN even before decay. The auction-pressure figure (E5) is the one class lead whose
snippet size (6 bp, unit unverified) would exceed the hurdle if it is 6 bp of price; it is already encoded as an
event in the library (k2_auction_*), and its verification belongs to the ZN reader.

Listing (R-S4) verified from a permitted primary source: CBOT Submission No. 15-572, hosted by the CFTC,
fetched afresh 2026-10-11T17:37:09Z (sha256 85201ffd...0bde6, identical to E.16's copy
reports/stage_e16_briefs/pages/settlement/cftc_ptc122315cbotdcm001.pdf):
- lines 68-70: "self-certifying the initial listing of the 10-Year U.S. Treasury Note futures and options
  contracts ("the Contracts"), effective on Sunday, January 10, 2016 for trade date Monday, January 11, 2016 for
  trading on the CME Globex Electronic Trading Platform";
- lines 108-110: "at the introduction of these contracts on January 11, 2016, quarterly delivery months listed for
  trading shall be March 2016, June 2016, and September 2016";
- lines 79-80: "a minimum tick size of one half of one thirty-second of one price point ($15.625)";
- lines 88-89: deliverable notes with "remaining term to maturity of not less than 9 years and 5 months from the
  first day of the contract delivery month, and not greater than 10 years".
Vendor corroboration (secondary): FirstRate Data's TN page (firstratedata_TN.txt) says "Continuous data is from
10-Jan-2016" (the Sunday-evening Globex open of trade date 2016-01-11) and "Individual contracts start with TNZ16".
Result: first trade date 2016-01-11, as R-S4 states. The U2 window start (2016-01-01/04) includes
2016-01-04..2016-01-08, which precede the listing (E.16 already notes that "TN" quotes in 2010-01..2012-05 are not
this contract).

## 2. Feature availability (TN rows; backward window 2016-01-11..2019-05-05, search window 2019-05-06..2024-02-29)

Calendar files read (date ranges and source notes only):
- C-R10: data/calendars/hist2010/rates.json (sha256 099ac84e...382a4), schema e14_hist_calendar/1, products
  include TN, coverage 2010-06-01..2019-05-31, every status graded "cme", 0 unsourced trade dates; sessions
  2011-10-03..2019-05-31 Globex 17:00 (d-1)..16:00 CT, TN day session 07:20-14:00.
- C-R19: data/calendars/rates.py (sha256 449c1529...df23), 2019-05-01..2026-06-19, CME sources.
- C-AUC10: reports/stage_e16_calendars/ec_auc_2010_2019.json (sha256 e3b5f452...b9e5, the F-04 rebuild documented in
  reports/stage_e16_calendars.md), FiscalData auctions_query, 2010-01-01..2019-06-30, 684 coupon rows, 2%-check
  share 0.0%, exact match with the frozen calendar on the 2019-05/06 overlap. Every row is tagged TN. In TN's
  window 2016-01-11..2019-05-05: 240 rows (2Y 35, 3Y 40, 5Y 39, 7Y 46, 10Y 40, 30Y 40); all 40 10Y rows at
  13:00 ET (12:00 CT).
- C-FOMC10: reports/stage_e14_cal_releases.json (sha256 9a051211...a080a7), FOMC 2010-06-23..2019-05-01, 72 rows,
  all tagged TN; in TN's window 27 rows, all "14:00 America/New_York", evidence and time_evidence "official".
- C-REL19: reports/stage_e2b_release_calendar.json (sha256 839f2437...7bcb8), 2019-05-01..2026-06-21. TN's D8
  list in the search window: TREASURY_AUCTION 394 (2Y 58, 3Y 57, 5Y 56, 7Y 60, 10Y 59 all 13:00 ET, 20Y 46,
  30Y 58), NFP 57, FOMC 37 = 488.
- Member literal tables: strategy/members/k2/_releases.py TREASURY_AUCTIONS 2019-05-08..2026-06-11,
  FOMC_STATEMENT_DATES 2019-05-01..; strategy/members/k2/_month_end.py MONTH_END 2019-05..2026-05 (from C-R19).
  No 2010-2019 literal table exists for either; the inputs to rebuild them by the same rules are C-AUC10,
  C-FOMC10 and C-R10.

| Feature | Legs | Calendars | 2016-01-11..2019-05-05 | 2019-05-06..2024-02-29 | Dates and basis |
|---|---|---|---|---|---|
| cp1_ret | TN | C-R10 / C-R19 (17:00 CT first bar of d-1, O 07:20) | yes | yes | from 2016-01-11 (first trade date opens Sunday 2016-01-10 17:00 CT, filing lines 68-70); C-R10 covers to 2019-05-31 |
| cp2_range | TN | C-R10 / C-R19 (O 07:20, [O, O+15)) | yes | yes | from 2016-01-11 |
| cp2_brk | TN | C-R10 / C-R19 (O+15..C 14:00) | yes | yes | from 2016-01-11 |
| cp3_clv | TN | C-R10 / C-R19 (prior complete day) | yes | yes | from 2016-01-12 (first prior complete day) |
| k2_auction_mto | TN | 10Y auctions (AUCTION_TENOR TN = 10Y): C-AUC10 / C-REL19 | yes (inputs exist; 2010-2019 literal table not generated) | yes | 40 10Y auctions in the window, all T_a 12:00 CT, so t1 07:50 and t2 10:20 are "to" rows, t3 12:50 a "since" row |
| k2_auction_msince | TN | same | yes (same note) | yes | applies at t3 12:50 (and at E.20's t4 14:08) |
| k2_fomc_mto | TN | FOMC statement dates at 13:00 CT: C-FOMC10 / C-REL19 | yes (inputs exist; table not generated) | yes | all 27 window statements at 14:00 ET = 13:00 CT, so all meet the FOMC_STATEMENT_DATES rule |
| k2_monthend_msince | TN | N-1, N from the rates group calendar: C-R10 / C-R19 | yes (derivable from C-R10, 0 unsourced; table not generated) | yes | months 2016-01..2019-04 (N of 2019-05 is 05-31, after the window) |
| k2_predrift_move | ZN, ZB only | ISM services | not applicable on TN rows | not applicable on TN rows | own_path_only on ZN, ZB (ml_route_v2/signals/k2.py); no 2010-2019 ISM-services calendar is on disk (a ZN/ZB fact) |
| k2_fomc_msince (excluded at V2.2's clock) | TN | C-FOMC10 / C-REL19 | inputs yes | inputs yes | excluded because 13:00 CT is after 12:50 (signal_coverage section 3); E.20's t4 = 14:08 reaches it. Fact for the lead, not a ruling |
| g01_ret30, g02_ret60, g03_ret120 | TN | open session intervals (SG-3): C-R10 / C-R19 | yes | yes | from 2016-01-11 |
| g04_ret_day | TN | C-R10 / C-R19 (first bar of trade date) | yes | yes | from 2016-01-11 |
| g05_gap | TN | C-R10 / C-R19 (prior C_X close; early-halt rule SG-4) | yes | yes | from 2016-01-12; n/a after early-halt dates (C-R10 lists them) |
| g06_rv60 | TN | C-R10 / C-R19 | partial (warm-up) | yes | needs 20 previous row dates: first possible row about 2016-02-08 by C-R10 trade dates |
| g07_range | TN | C-R10 / C-R19 | yes | yes | needs sigma_X,d (20 dates): about 2016-02-08 |
| g08_prev_ret | TN | C-R10 / C-R19 | yes | yes | from 2016-01-12; scaled by sigma_X,d (about 2016-02-08) |
| g09_vol_state | TN | C-R10 / C-R19 | partial (warm-up) | yes | sigma 20 + 120-date median: first possible row about 2016-07-26 by C-R10 trade dates |
| g10_logvol30 | TN | C-R10 / C-R19 | partial (warm-up) | yes | 20 previous row dates: about 2016-02-08 |
| g11_t_index, g12_dow | none | V2.2 clock | yes | yes | from 2016-01-11 |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | none (calendar only) | TN's D8 list: TREASURY_AUCTION (all coupon tenors), NFP, FOMC | partial / undetermined | yes (C-REL19) | auctions: C-AUC10 yes; FOMC: C-FOMC10 yes; NFP 2010-2019: [shared, see shared/macro_calendars.md] (RTY reader). No single 2010-2019 release file for TN exists; the code's coverage check (`_covered`) reads one coverage range, so a combined file would be needed. The tenor mix differs by window (20Y auctions only from 2020); causal either way |
| g16_month_end | none | C-R10 / C-R19 trade dates | yes | yes | months 2016-01..2019-04 |
| g17_nq, g17_6e, g17_cl, g17_gc, g17_zc | NQ, 6E, CL, GC, ZC | leg listings | [shared] | [shared] | apply on TN rows; listings audited by each lead's reader (product_NQ, _6E, _CL, _GC, _ZC) |
| g17_zn | ZN | - | not applicable on TN rows | not applicable on TN rows | TN is cluster K2, whose lead is ZN (SG-2: the row's own cluster lead is n/a) |
| g17_mbt | MBT (not one of the 17) | - | no (MBT listed 2021, per brief section 7) | partial (from listing) | leg outside the 17 roots |
| g17_mes | MES (not one of the 17) | - | no (MES listed 2019, per brief section 7) | yes/partial | leg outside the 17 roots; MES is also "uncovered" in reports/stage_e12_gate0_list.json |
| k9_anncday | MNQ, M2K, MYM rows only | EC-K9 | not applicable on TN rows | not applicable on TN rows | V2.3 K9 applies only on equity vehicles |

Further facts for the lead (no ruling):
- Row count implication of R-S4 plus V2.4 warm-up: the C-R10 calendar has 854 trade dates in 2016-01-11..
  2019-05-05. With sigma 20 plus the z-score minimum of 60 dates computed from TN's own bars, the first possible
  TN row is about 2016-05-03 (index 80); with G9's 120-date median, about 2016-07-26 (index 140). Actual rows
  also drop roll-blackout and early-halt dates; the roll blackout comes from the store's splice dates, which this
  reader did not open.
- At E.20's t4 = 14:08 CT on rates, h60 ends at 15:08 = F_X, so t4's h60 and F exits coincide on TN. t4 is after
  TN's 14:00 settlement (E.16 settlement table, TN 2016-01-11..2024-02-29, primary).
- TN's AUCTION_TENOR is 10Y (strategy/members/k2/_event_common.py line 43), shared with ZN.

## 3. Proposed features

None. Reasons:
1. No published TN-specific intraday rule since 2015 was found (section 1), so nothing root-specific can be
   turned into a feature with a verbatim sized quote.
2. The class effects that touch TN (ROD->LH for bonds, the 10-year auction cycle, FOMC and release windows) are
   rates-wide. They belong to the ZN reader, and a rates-wide feature proposed there covers TN's rows; a TN copy
   would duplicate it. The auction event is already in the library (k2_auction_mto / _msince).
3. The one sized class figure in hand fails on TN: bond ROD->LH at ~0.9 bp per trade [unverified planning-run
   derivation] = 0.58-0.86 TN ticks at P 100..150, ratio 0.47-0.70 to the D8 RT of 1.235 ticks, below 1.5x.

## 4. NQ only

n/a.

## 5. Fetch log, terms read, budget notices

Raw pages: reports/stage_e20_briefs/pages/TN/.

| URL | UTC | sha256 | Path | Status |
|---|---|---|---|---|
| https://www.cftc.gov/robots.txt | 2026-10-11T17:37:01Z | 1d500ec03ef610b457287a8e55e6ad2f83a7bb888a630325c23573dccdcd81bb | cftc_robots.txt | ok |
| https://www.cftc.gov/filings/ptc/ptc122315cbotdcm001.pdf | 2026-10-11T17:37:09Z | 85201ffd2b3c828f62f9d11175acc2ee96d2fc74ed773a0260d782dc6460bde6 | cftc_cbot15-572_tn_listing.pdf (+ .txt, pdftotext) | ok |
| https://cftc.gov/sites/default/files/2018-11/Liquidity%20Hierarchy%20in%20Tsy%20Mkt%20v4_ada.pdf | 2026-10-11T17:37:13Z | 1c36ae6de56d2662ed796739a36c1c15806fdc54af1dec47a0b6dc8b6d8483b6 | cftc_liquidity_hierarchy_2018.pdf (+ .txt) | ok |
| https://firstratedata.com/robots.txt | 2026-10-11T17:38:42Z | dc1d54dab6ec8c00f70137927504e4f222c8395f10760b6beecfcfa94e08249f | firstratedata_robots.txt | 404 (no robots file; saved error page) |
| https://firstratedata.com/i/futures/TN | 2026-10-11T17:38:55Z | 6e2b3c479e54eea98aa99bf9a19b960659cd6567aef0fc91ccc10a8758fd7b75 | firstratedata_TN.html (+ .txt) | ok |
| https://arxiv.org/robots.txt | 2026-10-11T17:39:20Z (mtime) | eda2bc852443f3f29d31eb04d37b26476654dc33b29256fb882819da23d189a5 | arxiv_robots.txt | ok |
| https://arxiv.org/pdf/2501.16772 | 2026-10-11T17:39:24Z | 9b40ea4bd1605b484d1265e07e3bf03438910be7595444179369903790ba3a2e | arxiv_2501.16772.pdf (+ .txt) | ok |

Read from disk, not fetched: Baltussen et al. copy (reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md);
E.16's copy of CBOT 15-572 (same sha256 as the fresh fetch); CFTC web policy as saved by E.13
(reports/stage_e13_briefs/pages/InfoSource/cftc_webpolicy.html).

Terms read:
- cftc.gov: robots.txt read 17:37:01Z: "User-agent: * / Content-Signal: search=yes,ai-train=no,use=reference";
  named AI training crawlers (ClaudeBot, anthropic-ai, Claude-Web, GPTBot ...) "Disallow: /". Web policy (E.13's
  saved copy): "Government information at the CFTC website is in the public domain." Ruling: single-page,
  user-initiated fetches for reference are allowed (E.13's reading, section 2.1); no crawling.
- firstratedata.com: no robots.txt (404). Product page is public marketing text; one fetch; used only as
  secondary corroboration of the listing date. Ruling: one reference fetch acceptable; no data downloaded.
- arxiv.org: robots.txt "User-agent: * / Crawl-delay: 15"; one PDF fetch, 4 s after robots. arXiv distributes
  papers for reading. Ruling: allowed.

Budget notices: none. WebSearch calls used: 18 of ~50 (log: pages/TN/search_log.md). One Firecrawl
research_search_papers call; no credit notice.

## 6. Unfinished and unverified items

- No TN-specific intraday study found. It may exist behind blocked or paid sources (SSRN, Wiley, ScienceDirect
  full texts were not queried directly); a gap in the record, not evidence of absence.
- Public TN price level not retrieved from a permitted source; bp conversions are given over P = 100..150
  [unverified band].
- Class items for the ZN reader / lead, not fetched by me under the assignment (section 7): NY Fed Staff Report
  1188 (Fleming, Liu, Nguyen 2026) and Robeco (2025-03) on 10-year auction-day price pressure (the "6 basis
  points" figure is a search snippet; unit unverified); Indriawan, Jiao, Tse (JBF 2021) post-FOMC drift
  (multi-day); Safari and Schmidhuber (arXiv 2501.16772, saved here) as a pooled minute-scale result.
- Shared files cited but not yet on disk when this file was written: shared/baltussen_notes.md,
  shared/rates_class_notes.md, shared/aalto_thesis_notes.md (Aalto thesis: whether its 20 futures include TN is
  unknown to me), shared/macro_calendars.md (NFP 2010-2019 coverage decides g13-g15 in the backward window).
- 2010-2019 literal tables for k2_auction_*, k2_fomc_mto and k2_monthend_msince do not exist yet; the inputs exist
  (C-AUC10, C-FOMC10, C-R10). Generating them is a build step, not done here.
