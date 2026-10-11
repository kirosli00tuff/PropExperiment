# Stage E.20 Part A: product reader ZN (vehicle ZN)

Reader: ProductReader-ZN-OpusHigh. Started about 2026-10-11 10:32 PDT; finished about 11:00 PDT.
Shared notes written: `shared/aalto_thesis_notes.md` and `shared/rates_class_notes.md`. The rates class
evidence is in full there. Below are the rows for ZN, sized in ZN ticks.

Conversions (from `shared/rates_class_notes.md` section 0):
- One ZN tick (1/64 point) is 1.42 bp of price at a price of 110 [assumption; ZN traded at about 110-135
  over 2010-2024, which gives 1.16-1.42 bp per tick].
- One bp of yield is about 6 bp of ZN price. Hartley and Schwarz: "So a 10-year futures contract has a
  duration of about 6 years."
- A 10-year cash price change maps to ZN at about x0.69 (cash duration 8.7 [assumption]).
- ZN D8 round trip: 1.17 ticks ($18.28). The 1.5x hurdle is 1.755 ticks.

## 1. Evidence

| ID | Effect | Rule | Hold | Gross / trade (bp; ZN ticks) | Gross/net | Sample | Decay | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD to LH momentum, bond futures | at 13:30 CT long if P(13:30)/P(prior 14:00 settle) - 1 > 0, else short; exit at 14:00 CT (end of settlement) | 30 min | 0.86 bp; 0.60 ticks (2.16%/yr / 252, 1/N of 16 bond futures). TY: β_ROD 2.53 (t 6.96), R2_OOS 0.86% | gross | 16 bond futures (TY from 1983-01-05), 1974-12..2020-05, 1-min | bonds β_ROD 3.19 (1974-99) to 1.53 (2000-20); LETF channel insignificant for bonds | Baltussen, Da, Lammers, Martens, JFE 2021 (on-disk copy) | primary |
| E2 | Same family, 2008-2024 | ROD/last-half-hour momentum and reversal | 30 min | none given | net "may not be feasible ... especially in bond and currency futures" | 20 equity, bond, FX futures, 2008-01..2024-10 | persists 2008-2024, per the abstract | Majorin, Aalto MSc thesis 2025 | abstract primary; figures [unverified] (full text restricted) |
| E3 | 10-year auction, pre leg | short at T_a - 180 (09:00 CT), cover at the auction close 12:00 CT on 10Y auction days | 180 min | cash 10Y -3.822 bp, x0.69 = 2.64 bp; **1.86 ticks** (ratio 1.59) | gross | on-the-run cash, GovPX/BrokerTec, 1991-06..2024-07, 1-min | 10Y yield pressure 1.491 (91-06), 1.732 (07-14), **0.593* (15-24)**; "less than half the earlier magnitudes" | Fleming, Liu, Nguyen, NY Fed SR 1188 (2026) | primary (WP) |
| E4 | 10-year auction, post leg | long from the results release (about 12:02 CT) to +180 min (about 15:02 CT) | 180 min | cash 10Y +6.084 bp, x0.69 = 4.20 bp; **2.96 ticks** (ratio 2.53) | gross | as E3 | 2015-24 total (both legs) 5.165 bp of cash price, about 2.51 ZN ticks for two trades, about 1.25 per leg (even split assumed; ratio about 1.07) | SR 1188 Tables 2, 3 | primary (WP) |
| E5 | Cross-tenor auction spillover to the 10-year | E3/E4 rule around 5Y and 7Y auctions | 2 x 180 min | 10y yield pressure 0.736 bp (5Y), 0.490 bp (7Y), both legs; x6 = 3.11 and 2.07 ticks in total; about 1.55 and 1.04 per leg (ratios 1.33, 0.89) | gross | as E3, full sample only | no subsample given; own-tenor effects fell by more than half after 2014 | SR 1188 Table 4 | primary (WP) |
| E6 | 10-year auction, ZN futures directly | ZN on 10Y auction days vs regular days, "ahead of the auction" | unstated | 6 bp; **4.2 ticks** (pre leg) | gross; costs "taken into account", no figures | ZN futures, Tickdata, 1983-01..2024-08 | none reported | Houweling, Penninga, Martinetti, Robeco quant chart, 2025-03-27 | primary, practitioner |
| E7 | Pre-announcement drift | trade 30 min before a release in the surprise's direction | 30 min | not causal (needs the surprise sign); bond pre-drift "only about one basis point"; ZN drift 39% of the total move | gross | ZN and ES 1-sec, 2008-01..2014-03 | JFQA version: 9 of 20 announcements [secondary-only]; post-2015 unknown | Kurov, Sancetta, Strasser, Wolfe, ECB WP 1901 (2016) | primary (WP) |
| E8 | Pre-FOMC drift | long into the FOMC | 24 h | null: "no such effect in U.S. Treasury securities" | gross | 1994-2011 (1980-2011) | n/a | Lucca and Moench, NY Fed SR 512 (rev. 2013; JF 2015) | primary (shared copy) |
| E9 | Post-FOMC drift | trade in the shock's sign after the statement | up to 15 days | no figure ("up to four times the Sharpe ratio of buy-and-hold") | gross | post-GFC, US and German long bond futures | "absence of pre-FOMC announcement drift" | Indriawan, Jiao, Tse, JBF 2021 | [secondary-only] (abstract) |
| E10 | End-of-month | long 10Y futures over the last day of the month | close to close (overnight) | 9 bp; about 6.3 ticks (last day); 22 bp over the last 5 days | gross | 1990-2018, daily | not reported | Hartley and Schwarz, Wharton WP 2019 | primary (WP); not intraday |
| E11 | Month-end strike time | index rebalancing trades concentrate at the index strike time | n/a | no return figure | n/a | Treasury cash activity | strike moved from 3 to 4 pm ET (14:00 to 15:00 CT), January 2021 | Dyer, Fleming, Shachar, Liberty Street 2026-09-22 | primary, activity only |
| E12 | First-15 to last-15 min momentum, China T-bond futures | sign of the first 15 min return predicts the last 15 min | 15 min | none given | unknown | CFFEX, years not seen | n/a | Zhang, Wang, Li, JBEF 2021 | [secondary-only] (abstract) |
| E13 | Intraday trend (1 h or more) and reversion (16 min or less), pooled incl. US 10Y | regression on trend strength | 1 h+ | R2_OOS 0.020 bp (1 h+); not tradable size | gross | 24-market pool, 2010-2023, 1-min | n/a | Safari and Schmidhuber, arXiv 2501.16772v2 | primary |

Verbatim quotes and locations are in `product_ZN.json` (field `quote`) and in `shared/rates_class_notes.md`.

**Decay and costs.** Two rates effects have published sizes near ZN's cost wall:
- The auction-day V (E3, E4, E6) is the only one whose full-sample average clears 1.5x per leg: about 1.9
  ticks before the auction and about 3.0 ticks after it, 1991-2024.
- Its post-2014 size is less than half that. Over 2015-2024 the 10-year yield pressure is 0.593 bp, with
  p < 0.1. That is about 1.25 ticks a leg if split evenly, below the 1.755-tick hurdle.
- It is already in the program as K2-aucpre-01 and K2-aucpost-01, and enters v2 as `k2_auction_mto` and
  `k2_auction_msince`.
- E.20's rates clock reaches only part of each leg. t2 = 10:20 CT with h60 sits inside the pre window
  (09:00-12:00). t3 = 12:50 CT misses the first 48 minutes of the post window.

ROD to LH momentum (E1) is about 0.6 ticks a trade gross, half of one round trip:
- It halved after 2000.
- It sits at 13:30-14:00 CT, which no rates decision time reaches.
- The Aalto abstract (E2) says such strategies are "especially" infeasible after costs in bond futures.

FOMC shows no pre-drift (E8, E9). The post-FOMC drift (E9) is multi-day and unsized intraday.
End-of-month (E10) is a close-to-close effect. Its intraday share is unknown.

## 2. Feature availability (ZN rows, and ZN as a G17 lead leg)

Calendar files used:
- EC-AUC 2010-2019: `reports/stage_e16_calendars/ec_auc_2010_2019.json` (sha256 e3b5f452..., FiscalData,
  official).
- E.14 releases: `reports/stage_e14_cal_releases.json` (sha256 9a051211...).
- Frozen release calendar: `reports/stage_e2b_release_calendar.json` (sha256 839f2437...).
- Rates hist2010 group calendar: `data/calendars/hist2010/rates.json` (sha256 099ac84e..., 2010-06-01..2019-05-31,
  CME-sourced, 0 unsourced).
- 2019-2024 group calendar: `data/calendars/rates.py`.

Windows:
- Backward window: 2010-07-01..2019-05-05.
- Search window: 2019-05-06..2024-02-29.

| Feature | Legs | Calendars | 2010-2019 | 2019-2024 | Dates and basis |
|---|---|---|---|---|---|
| cp1_ret | ZN | rates group calendar (Globex open 17:00 CT) | **partial** | yes | `ports._first_bar` needs a bar at exactly 17:00 CT on d-1. hist2010/rates.json sessions: 2010-06-01..2011-09-30 open 17:30 CT (`zn_specs_2010`); 2011-10-03 on, 17:00 (`globex_20110919`). Missing on 2010-07-01..2011-09-30 (value NaN, row excluded); yes from trade date 2011-10-03 |
| cp2_range, cp2_brk | ZN | rates calendar (O 07:20) | yes | yes | Range from O = 07:20 CT, both eras (day_session_ct 07:20-14:00 in both hist2010 eras) |
| cp3_clv | ZN | rates calendar (O, C) | yes | yes | Prior complete day session 07:20-14:00 |
| k2_auction_mto, k2_auction_msince | ZN | 10Y auctions (AUCTION_TENOR ZN to "10Y") | yes (calendar exists; no literal table generated) | yes | 2010-2019: EC-AUC 106 10Y rows in window, 2010-07-13..2019-04-10, every month; 105 at 13:00 ET, 1 at 11:30 ET (2012-12-12). 2019-2024: frozen 59 rows, 2019-05-08..2024-02-07, all 13:00 ET. `k2/_releases.py` covers 2019-05 on only |
| k2_fomc_mto | ZN | FOMC statement dates; anchor fixed at 13:00 CT (`ml_route_v2/signals/k2.py` FOMC_MIN) | **partial** | yes | E.14: 71 statements in window. 50 at 14:00 ET (13:00 CT) from 2013-03-20; 21 earlier at other times (14:15 x13, 12:30 x4, 12:35 x3, 12:20 x1; last 2013-01-30). On the 8 statements at 12:20-12:35 ET (11:20-11:35 CT), the fixed 13:00 CT anchor would place the event after t3 although it was already public. 2019-2024: frozen 37 in window |
| k2_monthend_msince | ZN | month-end dates (EC-CAL rates: N-1, N) | yes (derivable) | yes | 2010-2019: no literal table. Derivable from hist2010/rates.json trade dates by the member's rule. 2019-2024: `k2/_month_end.py` 2019-05-30..2026-05-28 |
| k2_predrift_move | ZN (and ZB) | ISM Services release dates | **no** | yes | No 2010-2019 ISM Services calendar found on disk: the E.14 release calendar holds NGS, WPSR and FOMC only; searched reports/*.json and data/calendars. 2019-2024: frozen 57 ISM_SERVICES dates in window |
| g01-g04, g06, g07, g10 | ZN | none (g04: first bar of the trade date) | yes | yes | Own path; g04 uses the actual first bar (`generic._own`), valid in both Globex eras |
| g05_gap, g08_prev_ret, g09_vol_state | ZN | rates calendar | yes | yes | O/C day session in both eras; g09 needs a 120-date warm-up; early-halt rule SG-4 |
| g11_t_index, g12_dow, g16_month_end | none / calendar | rates calendar | yes | yes | Flags from the group calendar |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | ZN | ZN's D8 list: TREASURY_AUCTION (all tenors), NFP, FOMC, ISM_SERVICES | **partial** | yes | 2019-2024: frozen 545 ZN rows in window (auctions 394, ISM_SERVICES 57, NFP 57, FOMC 37). 2010-2019: auctions yes (EC-AUC 636 rows in window: 2Y 97, 3Y 106, 5Y 107, 7Y 114, 10Y 106, 30Y 106; 20Y not issued until 2020); FOMC yes (E.14, times as above); NFP [shared, see shared/macro_calendars.md (RTY reader)]; ISM Services **none** |
| g17_nq, g17_6e, g17_cl, g17_gc, g17_zc (read on ZN rows) | NQ, 6E, CL, GC, ZC | none | yes | yes | Leads listed before 2010; listing facts in those readers' files |
| g17_zn on ZN rows | ZN | none | n/a by design | n/a by design | Own cluster K2: "the row's own cluster lead is not applicable" (`generic.py` docstring; `_lead`, `view.cluster != own_cluster`) |
| **g17_zn as a lead leg (read by K1, K3-K7 rows)** | ZN | none (ZN roll dates make it n/a per V2.2) | yes | yes | ZN listed well before 2010. Baltussen et al. Table A: "US 10-year T-note futures \| TY \| 1983-01-05 \| 2020-05-01". E.16 R-S4 names only RTY (2017-07-10) and TN (2016-01-11) as late listings. `stage_e16_windows.json` ZN window_start 2010-07-01. Rates Globex session covers every group's t1-t4 in both eras (17:30 or 17:00 to 16:00 CT) |
| g17_mbt | MBT | none | no | partial | MBT listed 2021 (brief section 7); outside the 17 roots |
| g17_mes | MES | none | no | partial | MES listed 2019-05; uncovered in `stage_e12_gate0_list.json` |
| k9_anncday | none on ZN rows | EC-K9 | n/a | n/a | Applies on MNQ, M2K and MYM rows only (V2.3) |
| r_ROD, abs r_ROD vs median (prompt-added) | ZN | rates calendar, C = 14:00 CT | yes | yes | Own path and group calendar in both eras. Listed for completeness, not proposed |

Facts for the lead's F6 cut, without a ruling:
- cp1_ret is missing on ZN for the first 15 months of the backward window.
- k2_predrift_move and the ISM part of g13-g15 have no 2010-2019 calendar.
- k2_fomc_mto's fixed 13:00 CT anchor is correct only from 2013-03-20.

## 3. Proposed features

**None.** Reasons, with the candidates that were sized:
1. **Cross-tenor auction flags on ZN rows**: minutes to and since the 5Y and 7Y auctions (SR 1188
   Table 4).
   - Causal, legs ZN only; EC-AUC covers both windows.
   - Published size, full sample, both legs together: 0.736 bp of 10y yield (5Y) and 0.490 bp (7Y), that
     is 3.11 and 2.07 ZN ticks for two trades. That is about 1.55 and 1.04 ticks a leg, ratios 1.33 and
     0.89 against 1.17. **Neither clears 1.5x.** The own-tenor effect fell by more than half after 2014,
     so the post-2014 spillover is likely smaller still.
   - E.20's clock captures only part of each leg.
   - Rejected.
2. **Post-FOMC continuation at t4 (14:08 CT)**: the sign of ZN's 12:59-14:07 move on FOMC days, hold h60
   or to F.
   - E9's evidence is multi-day, abstract-only and unsized intraday. No verbatim per-trade figure exists.
   - Rejected: no published size.
3. **Last-10-minute momentum** (E2).
   - Its window (13:50-14:00 CT) has no E.20 rates decision time.
   - The thesis's figures are unreadable (restricted full text).
   - Rejected.
4. **Own-tenor auction V.** Already in the library (`k2_auction_mto`, `k2_auction_msince`); not
   re-proposed.

## 4. NQ only

n/a

## 5. Fetch log, terms read, budget notices

Fetch log. All UTC 2026-10-11. Paths under `reports/stage_e20_briefs/`.

| URL | UTC | sha256 | Path | Status |
|---|---|---|---|---|
| https://aaltodoc.aalto.fi/robots.txt | 17:34:03Z, 17:35Z, 17:37Z | - | (502 page discarded) | blocked (502 x2, timeout) |
| https://aaltodoc.aalto.fi/items/1011f043-edd1-4cb2-9694-b1216d77561f | 17:35Z (curl), 17:36Z (WebFetch) | - | - | blocked (502 x2; WebFetch 403) |
| https://aaltodoc.aalto.fi/server/api/core/items/1011f043-edd1-4cb2-9694-b1216d77561f | 17:36Z | 0d301069918a97651b2a53431dce0b924450b65f42bdf550a94158cdcae9ac46 | shared/aalto_thesis_item_api.json | ok |
| .../items/1011f043-.../bundles | 17:37Z | 5ab2d147bb5afb7d225d55eadda150548477e79fc341c5009fa9b50371158950 | shared/aalto_thesis_bundles_api.json | ok (no files) |
| .../items/1011f043-.../accessStatus | 17:37:19Z | c1e2559dd40aae2d6ed5a29fa6c17663f72f6804a4ea5be42537d0086d6214bd | shared/aalto_thesis_accessstatus_api.json | ok (metadata.only) |
| https://aaltodoc.aalto.fi/info/end-user-agreement | 17:38Z | - | - | blocked (timeout) |
| https://www.aalto.fi/en/news/aalto-thesis-database-now-available-from-outside-the-learning-centre | 17:39:39Z | 112721737613c5f2931bd3d91a253156d89066bd79fbcb3a0c7a9434f5880f38 | shared/aalto_thesis_database_news.html | ok |
| https://www.skidmore.edu/economics/documents/KSSW2017-PriceDriftBeforeUSMacroeconomicNews.pdf | 17:42:32Z | - | (404 page discarded) | blocked (404) |
| https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp1901.en.pdf | 17:42:45Z | 6bec58a8c4c296fc29ac49998ae1c3aa373b38701b5ad901b6ce948355887d67 | pages/ZN/kssw_ecbwp1901.pdf | ok |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188.pdf | 17:43:34Z | 93f9b196946d3c41e9670052eb3d8d0fce30fb892f8f1553c1b469c05193095b | pages/ZN/nyfed_sr1188.pdf | ok |
| https://www.robeco.com/en-au/insights/2025/03/quant-chart-us-treasuries-up-for-auction | 17:44:13Z | e859ba7cf3ff808d7b9b2e5172808c865510e93080568c6ab32b28deaf4535aa | pages/ZN/robeco_quant_chart_auctions.html | ok |
| https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2019/12/17-19.Schwarz.pdf | 17:44:41Z | 56403762378f606f595dcce11afcf1f1eaccf8810237c58999f653a230a32809 | pages/ZN/hartley_schwarz_2019.pdf | ok |
| https://arxiv.org/pdf/2501.16772 | 17:45:10Z | 9b40ea4bd1605b484d1265e07e3bf03438910be7595444179369903790ba3a2e | pages/ZN/arxiv_2501.16772.pdf | ok |
| https://ideas.repec.org/a/eee/beexfi/v31y2021ics2214635021000599.html | 17:45:49Z | 449b680f2a3d29e89e82027b2be95de5b83d3d3ca72ddfb41941c5b400d20b19 | pages/ZN/ideas_zhang_wang_li_2021_bond_intraday_momentum.html | ok (abstract) |
| https://www.sciencedirect.com/science/article/pii/S2214635021000599 (+ robots.txt) | 17:46Z | - | pages/ZN/sciencedirect_robots_403_blockpage.html | blocked (403) |
| https://arxiv.org/pdf/2508.06788 | 17:49:20Z | 79bb14f8e7d8d859e971187825433511c6d0ce00f1ff267be24887a48bbb95b2 | pages/ZN/arxiv_2508.06788.pdf | ok, not relevant (ES only), not used |
| https://works.bepress.com/yiuman-tse/141 | 17:49:37Z | 3b0fb000db6867bd363d27f5dd76a894feb56d93978bfc11ed4e6e9440384d9d | pages/ZN/bepress_tse_141.html | ok, service discontinued, no paper |
| https://ideas.repec.org/a/eee/jbfina/v123y2021ics0378426620302880.html | 17:49:52Z | b931c295046bd2d6db662a01abe93e81402f88988ae224d86f5d16095bd1d768 | pages/ZN/ideas_indriawan_jiao_tse_2021.html | ok (abstract) |
| https://libertystreeteconomics.newyorkfed.org/?p=45552 (to /2026/09/treasury-trading-at-the-close/) | 17:51:10Z | 2036a2f067b9c0639d01ede8cb3dd0991f57dd0dea5874cdd06819c6c2336553 | pages/ZN/lse_index_strike.html | ok |

On-disk sources grepped, not fetched by me:
- `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md`;
- `shared/lucca_moench_sr512.pdf.txt`, fetched by another reader.

Terms and robots read. Each robots.txt is saved in `pages/ZN/`, read before the first page fetch from
that site:

| Site | Read | Ruling |
|---|---|---|
| aaltodoc.aalto.fi | unreachable (502/timeout) | robots and end-user agreement unread. Only 3 public metadata GETs were made; no full text exists to download (metadata.only) |
| aalto.fi | not read (single news page) | public news page, one GET |
| skidmore.edu | robots ok, crawl-delay 5 | /economics/documents not disallowed |
| ecb.europa.eu | robots ok | /pub/pdf not disallowed |
| newyorkfed.org | robots ok | medialibrary not disallowed |
| robeco.com | robots ok | insights pages not disallowed |
| rodneywhitecenter.wharton.upenn.edu | robots ok | nothing disallowed |
| arxiv.org | robots ok, crawl-delay 15 | /pdf allowed; 2 fetches 4 min apart |
| ideas.repec.org | robots ok | only /cgi-bin/ disallowed |
| sciencedirect.com | robots returned 403 | blocked; not retried |
| works.bepress.com | robots 302 | one page; service retired |

Budget:
- WebSearch: 18 calls, no over-budget notice.
- Firecrawl: 1 search (4 credits; output too large, not used again). No credit notice.
- WebFetch: 1 (403).
- A tool cost notice appeared ("COST CRITICAL ... Informational only"). Treated as informational, per
  section 8.

## 6. Unfinished and unverified items

- **Aalto thesis full text is not retrievable.** Aaltodoc reports "metadata.only". No per-class or
  per-market numbers exist in this record. See `shared/aalto_thesis_notes.md`. The planning brief's
  "every asset class" is wrong: the sample is equity, bond and FX only.
- Aaltodoc terms and robots.txt were not readable (site errors). This is recorded as a gap.
- Conversions:
  - the cash 10-year duration of 8.7 is an assumption;
  - the ZN price level of 110 is an assumption;
  - mapping 10-year yield changes onto ZN's cheapest-to-deliver is approximate.
  Ticks may be off by about ±20%.
- SR 1188's 2015-2024 pre/post split by leg is not published. The "1.25 ticks per leg" assumes an even
  split.
- Abstract only [secondary-only]: Zhang, Wang, Li 2021 (ScienceDirect 403) and Indriawan, Jiao, Tse 2021.
- Not found: "Drift Begone"; US Treasury futures intraday momentum papers since 2015 beyond Baltussen;
  settlement-window effects; ES to ZN lead-lag at retail latency.
- NFP 2010-2019 coverage (for g13-g15) is left to the RTY reader's `shared/macro_calendars.md`, which was
  not on disk when this file was written.
