# Stage E.20 Part A: product reader, ZT (2-year Treasury note futures; vehicle ZT)

Reader: ProductReader-ZT-OpusHigh (opus, high). Work: 2026-10-11 10:32-10:47 PDT. JSON twin:
`reports/stage_e20_briefs/product_ZT.json`. Raw pages: `reports/stage_e20_briefs/pages/ZT/`.
No data store opened, no E.15/E.17/E.18 or Gate 0 results read, nothing edited outside these outputs.

Conversion used throughout. ZT point value is $2,000 (rules/products.py:156: tick 0.00390625 pt =
$7.8125). One bp of notional at price P is P/39.0625 ticks. P = 105 is assumed (2.69 ticks per bp).
Over P = 101.5-110.5 the tick figures scale by 0.967-1.052. The price level comes from search
snippets only (Barchart ZTU23 101-155 on 2023-09-29, 110-13 near 2020-10-05), so it is
[unverified]. Returns on the cash on-the-run 2Y are taken as equal to ZT returns. This is an
approximation: the CTD's duration is close to the on-the-run 2Y's. Yield-to-price conversion uses
the paper's own 2Y ratio, Table 3 price pressure / Table 2 yield pressure = 1.336/0.712 = 1.876.
D8 round trip for ZT: 1.323 ticks ($10.34) (root table).

## 1. Evidence

| ID | Effect | Rule | Hold | Gross per trade | Gross/net | Sample | Decay evidence | Source |
|---|---|---|---|---|---|---|---|---|
| E1 | 2Y auction: price falls before the auction (own tenor) | Short the 2Y from close-180 to close-1 min on 2Y auction dates (close 13:00 ET = 12:00 CT) | 180 min | 0.733 bp = 1.97 ticks | gross | On-the-run cash 2Y mids, GovPX 1991-2000, BrokerTec 2001-2024, 1-min; auctions 1991-06-25..2024-07-24 | Pre leg not split by period. Both legs together: 1.348 bp (1991-2006), 1.852 (2007-2014), 0.887 (2015-2024). 2Y F-test S3=S2 1.867, not significant | Fleming, Liu, Nguyen (2026), FRBNY SR 1188, Table 3. [primary] |
| E2 | 2Y auction: price recovers after the auction (own tenor) | Long from the minute after results (0+) for 180 min | 180 min | 0.603 bp = 1.62 ticks | gross | as E1 | 2015-2024 both legs 0.887 bp, about 0.44 bp (1.19 ticks) per leg if split equally (split not reported) | SR 1188, Table 3. [primary] |
| E3 | Spillover of auction pressure onto the 2Y from 3Y, 5Y, 10Y auctions | Same two legs as E1/E2, in the 2Y note, on 3Y, 5Y or 10Y auction dates | 2 x 180 min | Two-leg yield pressure 0.677 (3Y), 0.966 (5Y), 1.013 bp (10Y) = 1.27/1.81/1.90 bp price. Per leg (equal split assumed) 1.71/2.43/2.56 ticks | gross | as E1, full sample only | No period split for spillovers. 2Y own-tenor yield pressure 0.712 -> 0.419 in 2015-2024 (x0.59) | SR 1188, Table 4. [primary; per-leg split is a derivation] |
| E4 | ROD -> last half hour, TU futures | sign(r_ROD), with r_ROD = prior close 15:00 ET to 14:30 ET, predicts 14:30-15:00 ET (13:30-14:00 CT) | 30 min | Derived: 0.0207 x E\|r_ROD\| (about 6.5 bp) = 0.135 bp = 0.36 ticks | gross | TU 1991-01-04..2020-05-01, 7,153 days, 08:20-15:00 ET, 1-min | Full-sample row only; class decay: see NQ and ZN shared notes | Baltussen, Da, Lammers, Martens (JFE 2021), Table B2 Panel B (disk copy). [primary row; derivation mine] |
| E5 | End of month, 2Y (last trading days) | Hold the 2Y zero over the last t trading days (t=2: N-1 and N), financed at GC repo | daily close-to-close (includes overnight; not intraday) | 5 bp over 2 days (2.5 bp/day = 6.7 ticks/day), 1990-2018; 2015-2019: 1 bp over 2 days, n.s. | gross | GSW zero-coupon 2Y/5Y/10Y, daily, 1990-2018 | 2Y last 2 days: 0.05*** in 2010-2014, 0.01 (n.s.) in 2015-2019 | Hartley and Schwarz (2019), Rodney White Center WP 17-19, Tables 1, 3, 4. [primary] |
| E6 | Pre-FOMC day (-1) at the short end: null | 2Y yield change on the day before scheduled FOMC days | daily | -0.25 bp yield (n.s.), about 0.47 bp price = 1.26 ticks | gross | ACM zero-coupon yields, 1994-09..2025-12 | n/a (null) | Pan and Peng (2026 draft), SAIF. [primary] |
| E7 | Pre-FOMC 2pm-to-2pm window, 2Y: null | 2Y benchmark yield change from 14:00 ET on t-1 to 14:00 ET on FOMC day | 24 h | 0.006 pp = 0.6 bp yield (s.e. 0.4), n.s. | gross | 1994-09..2011-03 (pre-2015 sample, published 2015) | n/a (null) | Lucca and Moench, FRBNY SR 512, Table 8. [primary] |

Verbatim quotes (location; file under pages/ZT/ unless noted):
- E1/E2, SR 1188 Table 3 (PDF p. 48), 2-Year column: "Price Pressure (bps)         1.336∗∗∗" / "Pre-auction Return (bps)    −0.733∗∗∗" / "Post-auction Return (bps)    0.603∗∗" / Panel B "S3: 2015-2024              0.887∗∗∗". Window definition (p. 21): pre-auction return "P(−1) −P(−181) / P(−181)" and post-auction "P(+180) −P(0+ ) / P(0+ )". Table 2 Panel B: "S3: 2015-2024                       0.419∗∗∗". Text p. 20: "the post-2015 period displays markedly weaker yield pressure—less than half the earlier magnitudes."
- E3, SR 1188 Table 4 (PDF p. 49), 2-Year secondary column: "2-Year        0.712∗∗∗", "3-Year        0.677∗∗∗", "5-Year        0.966∗∗∗", "7-Year        0.297∗", "10-Year       1.013∗∗∗", "30-Year      −0.073". Text p. 23: "around 3-year auctions, we observe significant yield pressure in the 2-year (0.68 bps) and 3-year (0.75 bps) notes".
- E4, Baltussen disk copy (reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md), line 3612: "| TU | 1.37** (2.11) | 0.17 | 0.09* | 1.56** (2.44) | 2.34*** (3.41) | 4.83 (1.52) | 0.80 | 0.26** | 2.07*** (4.45) | 0.71 | 0.70*** |". The last three columns are beta_ROD, R2 and R2OOS. Caption: "Adjusted R2, R2OOS, and slope coefficients are multiplied by 100." Sample row, line 3262: "| US 2-year T-note futures | TU | 1991-01-04 | 2020-05-01 | 7153 | 08:20-15:00 | USA |". Hours are "denoted in Eastern Standard Time (EST)". The volatility input comes from SR 1188, p. 17: "Annualized realized volatility scales with duration from 1.3% (2-year)".
- E5, Hartley-Schwarz Table 1: "2-Year        0.03*** 0.05*** 0.06***" (note: "100 times the average excess returns"). Table 4, 2015-2019: "2-Year         0.01*        0.01   0.04***". Table 3: "2-Year         0.97      1.11     1.10". Text: "The estimates in the final period, from 2015-2018 are smaller than most of the other periods, but they remain significant." Table 4's note does not restate the x100 scaling. Its 2010-2014 2Y values equal Table 1's, so the same units are assumed.
- E6, Pan-Peng: "The 10-year yield declines by an average of 0.79 basis points, while the 2-year yield drops insignificantly by only 0.25 basis points."
- E7, SR 512 Table 8: "Instrument: FF ED-4 TREAS-3M TREAS-2Y TREAS-5Y TREAS-10Y", post-1994 "pre-FOMC dummy 0.001 0.007 0.001 0.006 0.001 −0.002", s.e. "[0.001] [0.006] [0.004] [0.004]".

Reading of decay and costs.
- The only intraday, ZT-relevant effect with a sized primary figure is the auction inverted V (E1-E3).
  - Full sample: one leg on the own tenor is 1.6-2.0 ticks gross, against a D8 round trip of 1.32 ticks (ratio 1.2-1.5). The pre-auction leg is just under 1.5x.
  - 2015-2024: own-tenor pressure roughly halved. About 1.2 ticks per leg, a ratio of about 0.9.
- At the V2.2 clock no rates decision time spans a full 180-minute leg:
  - t2 = 10:20 h60 covers 60 of the 180 pre-auction minutes before the 12:00 CT close;
  - t3 = 12:50 h120 covers the post window from about 48 minutes after results.
  - So the capturable gross is lower still.
- The frozen K2-aucpre/aucpost members already implement the E1/E2 rule on the own tenor (aucpre: SELL T_a-180 to T_a-1; aucpost: BUY T_a+5 for 180 min). This is not new evidence for a new rule.
- The month-end effect (E5) is daily, includes overnight, and is not significant for the 2Y in 2015-2019.
- Pre-FOMC drift at the short end is null in two sources (E6, E7).
- ROD -> LH on TU is significant in-sample (t 4.45, R2OOS 0.70%), but its implied per-trade size (about 0.36 ticks) is about a quarter of the D8 round trip.
- The practitioner auction note from Robeco (10Y futures, 1983-2024, "futures prices decline by 6 basis points" before the auction) is 10Y-only: rates class, not cited as a ZT row.
- Class evidence: cite `reports/stage_e20_briefs/shared/rates_class_notes.md` and `shared/aalto_thesis_notes.md` (ZN reader); Baltussen class rows: `shared/baltussen_notes.md` (NQ reader). [shared, see those paths]

## 2. Feature availability (V2.3 features that read ZT bars or apply on ZT rows)

Calendar files: hist2010 rates = `data/calendars/hist2010/rates.json` (2010-06-01..2019-05-31, 2,324 trade dates, 0 unsourced, 25 full closures, 97 early halts, sha256 099ac84e...); rates.py = `data/calendars/rates.py` (2019-05-01..2026-06-19, sha256 449c1529...); EC-AUC 2010-2019 = `reports/stage_e16_calendars/ec_auc_2010_2019.json` (FiscalData, 2010-01-01..2019-06-30, verified, sha256 e3b5f452...); frozen = `reports/stage_e2b_release_calendar.json` (2019-05-01..2026-06-21, sha256 839f2437...) through `strategy/members/k2/_releases.py`; E.14 FOMC = `reports/stage_e14_cal_releases.json` (2010-06..2019-05, sha256 9a051211...).

| Feature | Legs | Calendars | 2010-2019 (backward, 2010-07-01..2019-05-05) | 2019-2024 | Basis / dates |
|---|---|---|---|---|---|
| cp1_ret, cp2_range, cp2_brk, cp3_clv | ZT | rates group calendar | yes | yes | ZT listed throughout: Baltussen sample row TU 1991-01-04..2020-05-01; E.16 windows start 2010-07; no R-S4 restriction. Day session 07:20-14:00 CT in both eras. Globex opened at 17:30 CT d-1 until 2011-09-30 (17:00 CT from 2011-10-03), so CP1's "first bar" is the 17:30 bar before 2011-10-03. |
| k2_auction_mto, k2_auction_msince | none (fixed clock; ZT rows) | TREASURY_AUCTIONS, tenor 2Y (AUCTION_TENOR ZT=2Y) | partial | yes | 2019-2024: 58 2Y rows in 2019-05..2024-02, one every month; the E.16 announcements file has 0 tenor mismatches. 2010-2019: 97 2Y rows (2010-07-27..2019-02-25); 9 months have no 2Y event. See the note below the table. 2Y times 2010-2019: 13:00 ET x92, 11:30 ET x5. All rows announced before the auction date. The 2010-2019 rows are not yet transcribed into k2/_releases.py. |
| k2_fomc_mto | none | FOMC_STATEMENT_DATES (instant 13:00 CT only, L-15) | partial | yes | 2019-2024: frozen, 37 in window. 2010-2019: E.14 has 71 statements in the window. 50 are at 14:00 ET = 13:00 CT, from 2013-03-20. 21 earlier ones are at 14:15 ET (13:15 CT, 14 with inferred times) or 12:20-12:35 ET. The member's 13:00 CT filter admits no date in 2010-07-01..2013-03-19. Extending it is the lead's call. FOMC calendar also audited in shared/macro_calendars.md. |
| k2_monthend_msince | none | K2 MONTH_END (N-1, N of the rates calendar) | yes | yes | k2/_month_end.py covers 2019-05-30..2026-05-28. For 2010-2019 it follows mechanically from hist2010 rates (complete, fully sourced); the table is not yet generated. |
| k2_predrift_move | ZN, ZB | ISM_SERVICES_DATES | n/a on ZT rows | n/a on ZT rows | Applies only on ZN and ZB rows (k2/predrift.py:46). |
| g01_ret30, g02_ret60, g03_ret120, g04_ret_day, g06_rv60, g07_range, g09_vol_state, g10_logvol30 | ZT | rates calendar (session intervals) | yes | yes | Own bars; hist2010 rates and rates.py. |
| g05_gap, g08_prev_ret | ZT | rates calendar (C = 14:00, early-halt flags) | yes | yes | hist2010 has early-halt flags (97); settlement 14:00 CT throughout (reports/stage_e16_settlement.md rows 38-39). |
| g11_t_index, g12_dow | none | none | yes | yes | Clock only. |
| g16_month_end | none | rates calendar trade dates | yes | yes | hist2010 rates and rates.py. |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | none | D8 list for ZT: TREASURY_AUCTION (all coupon tenors), NFP, FOMC | partial | yes | 2019-2024: 488 ZT rows in window (auctions 394: 2Y 58, 3Y 57, 5Y 56, 7Y 60, 10Y 59, 20Y 46, 30Y 58; NFP 57; FOMC 37). 2010-2019: auctions 636 rows (2Y 97, 3Y 106, 5Y 107, 7Y 114, 10Y 106, 30Y 106; no 20Y issued before 2020; products include ZT) and FOMC 71 are on disk. I found no 2010-2019 NFP calendar on disk; see shared/macro_calendars.md (RTY reader). The 2010-2019 list is not yet assembled in the release-calendar format. |
| g17_nq, g17_6e, g17_cl, g17_gc, g17_zc | lead leg | none | yes (listing per lead reader) | yes | Lead roots among the 17 with a 2010-07 window start; listing audited by each lead's reader (product_<LEAD>.md). |
| g17_zn | ZN | none | not applicable on ZT rows | not applicable on ZT rows | SG-2: ZN is K2's own cluster lead (ml_route_v2/constants.py CLUSTER_LEADS). The feature is constant 0 plus its flag on every ZT row. |
| g17_mbt | MBT | none | no | partial (MBT listed 2021) | Leg outside the 17 roots. |
| g17_mes | MES | none | no | partial (MES listed 2019) | Leg outside the 17 roots; uncovered in stage_e12_gate0_list.json. |

Not on ZT rows: k9_anncday (MNQ, M2K, MYM only) and every K1, K3-K8 member.

Note on k2_auction in 2010-2019 (lead to note, not a calendar defect; E.16 flagged the same).
- Nine 2-year-maturity sales were reopenings of older notes, and their original_security_term is not 2-Year:
  - keyed 5Y, so mapped to ZF: 2015-05-26, 2015-08-25, 2015-09-22, 2015-11-04, 2016-02-23, 2017-10-24;
  - keyed 7Y, so mapped to no vehicle: 2017-04-25, 2019-03-26, 2019-04-23.
- Under the frozen convention, ZT has no auction event in 2015-05, 2015-08, 2015-09, 2015-10, 2016-02, 2017-04, 2017-10, 2019-03 and 2019-04.
- Keying on security_term would restore them. That is a definition choice for the lead.

## 3. Proposed features

One documented candidate. It does not clear 1.5x at the V2.2 clock.

**zt_cpnauc_mto / zt_cpnauc_msince**: a clock of 2Y-note auction pressure on 2Y, 3Y, 5Y and 10Y auction dates.
- Source: SR 1188, Table 4 (2-Year column: 3Y 0.677***, 5Y 0.966***, 10Y 1.013***, own 0.712***) and p. 4: "Yields rise steadily in the hours leading up to the auction and reverse in the hours following the release of auction results".
- Formula, for a ZT row (d, t):
  - A_d = the CT instants T_a of TREASURY_AUCTION rows dated d with original tenor in {2Y, 3Y, 5Y, 10Y}. T_a uses the same frozen conversion as k2_auction: closing_time_comp ET expressed in CT.
  - mto = min(T_a - t) over T_a >= t, in minutes, with flag 1; otherwise 0 with flag 0.
  - msince = t - max(T_a) over T_a with T_a + 4 <= t (the offset K2-aucpost uses, aucpost.py:34), with flag 1; otherwise 0 with flag 0.
  - No bar is read.
  - It differs from k2_auction_* only in adding the 3Y, 5Y and 10Y instants on ZT rows. The 7Y (0.297*, 10% level) and the 30Y (n.s.) are left out.
- Decision times and horizons: t2 (10:20 CT, short side, h60) and t3 (12:50 CT, long side, h60/h120). F from t2 would span the auction.
- Legs: ZT only.
- Calendars: EC-AUC 2010-2019 and the frozen TREASURY_AUCTION rows 2019-2024. Both list every coupon tenor, and every row was announced before its auction date. Available in both windows: yes.
- Expected gross per trade:
  - Full sample on a 5Y or 10Y day: about 0.93 bp price per 180-minute leg, about 2.5 ticks.
  - The clock captures about 1/3 of the pre leg (t2 h60) and about 2/3 of the post leg (t3 h120), assuming linear accrual (not read numerically from Figure 2). That gives about 0.8 and 1.7 ticks.
  - With the 2Y own-tenor post-2015 ratio 0.59 applied, about 0.5 and 1.0 ticks. The spillover decay itself is unreported.
  - Best case post-2015, t3 h120: about 1.0 tick against the D8 1.323 ticks ($10.34), ratio about 0.75. Full-sample best case: about 1.28.
- Clears 1.5x: no.
- Why list it anyway: the spillover rows are the paper's largest 2Y numbers (5Y and 10Y auctions move the 2Y more than its own auction does), and the feature costs no new data. The lead decides.

No second proposal. The other ZT-specific effects found are daily or overnight (E5), null (E6, E7), already a frozen member (E1/E2 = K2-aucpre/aucpost; E5 underlies K2-monthend), or already added by the prompt (E4 = r_ROD).

## 4. NQ only

n/a

## 5. Fetch log, terms read, budget notices

| URL | UTC | sha256 | Path (pages/ZT/) | Status |
|---|---|---|---|---|
| https://www.newyorkfed.org/robots.txt | 2026-10-11T17:36:26Z | 0102c8c4...51cb5551e | nyfed_robots.txt | ok |
| https://www.newyorkfed.org/privacy/termsofuse | 2026-10-11T17:36:30Z | 9173e70b...6af680f | nyfed_terms.html (+ .txt) | ok |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188.pdf | 2026-10-11T17:36:42Z | 93f9b196946d3c41e9670052eb3d8d0fce30fb892f8f1553c1b469c05193095b | nyfed_sr1188.pdf (+ .txt) | ok |
| https://rodneywhitecenter.wharton.upenn.edu/robots.txt | 2026-10-11T17:38:05Z | 975ced5a...b20865 | wharton_rwc_robots.txt | ok |
| https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2019/12/17-19.Schwarz.pdf | 2026-10-11T17:38:13Z | 56403762378f606f595dcce11afcf1f1eaccf8810237c58999f653a230a32809 | hartley_schwarz_2019.pdf (+ .txt) | ok |
| https://en.saif.sjtu.edu.cn/robots.txt | 2026-10-11T17:38:05Z | (404, not kept) | - | ok |
| https://en.saif.sjtu.edu.cn/junpan/FOMC_new.pdf | 2026-10-11T17:38:16Z | 06a73bf324594a0c01693c89c8b84e87724ad837f83607fd2ff3c4816f16326d | pan_peng_fomc_2026.pdf (+ .txt) | ok |
| https://arxiv.org/robots.txt | 2026-10-11T17:39:07Z | eda2bc85...189a5 | arxiv_robots.txt | ok |
| https://arxiv.org/abs/2508.06788 | 2026-10-11T17:39:10Z | dfd12654...75330d | arxiv_2508.06788_abs.html | ok (not relevant: E-mini only) |
| https://www.robeco.com/robots.txt | 2026-10-11T17:39:29Z | 711fcd7c...f81e | robeco_robots.txt | ok |
| https://www.robeco.com/en-hk/insights/2025/03/quant-chart-us-treasuries-up-for-auction | 2026-10-11T17:39:34Z | 98c11fdf...0ef4 | robeco_quant_chart_auctions.html (+ .txt) | ok (10Y only) |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf | 2026-10-11T17:40:59Z | c7cb0f335c60cb9fc305189935fb7c51e98fa8461c2b33efd51eb5a5c3f2e34b | nyfed_sr512_lucca_moench.pdf (+ .txt) | ok |
| https://ideas.repec.org/robots.txt | 2026-10-11T17:41:33Z | 4620fbdb...1702d46 | repec_robots.txt | ok |
| https://ideas.repec.org/p/osf/socarx/xucf8.html | 2026-10-11T17:41:37Z | 56a85b62...957722a | repec_prerefunding.html | ok (long end, daily; out of scope) |

Full sha256 values are in the JSON fetch_log. All fetches used plain curl with a browser user agent, one request per page, with seconds between requests to the same domain. No Scrapling or Firecrawl was needed.

Terms read:
- newyorkfed.org terms of use (2026-10-11T17:36:30Z): "You may: Access the Content, manually or through an automated process or device, provided your access does not have the effect of disabling, damaging, or interfering with the function of the Website". robots.txt disallows only /PrincipleInterest/ and two calendar PDFs. Allowed.
- rodneywhitecenter.wharton.upenn.edu: robots.txt "User-agent: * / Disallow:" (empty). Allowed; no terms page read.
- en.saif.sjtu.edu.cn: robots.txt 404 and no terms page found. One fetch of the author's own posted draft.
- arxiv.org (/abs/ allowed, crawl delay honoured), robeco.com (insights pages not disallowed) and ideas.repec.org (paper pages not disallowed): one fetch each.
- No cmegroup.com page and no archive of it was fetched. Barchart was seen only in search snippets and never fetched.

Budget notices: none. WebSearch calls: 14 of about 50. No Firecrawl calls.

## 6. Unfinished and unverified items

- [unverified] The ZT price level (P = 105, range 101.5-110.5) used for the bp-to-tick conversion rests on search snippets only. Tick figures scale by 0.967-1.052 across that range.
- Derived by this reader, not published:
  - the per-leg and post-2015 spillover figures (E3 and the proposal);
  - the clock-capture fractions (linear accrual assumed; SR 1188 Figure 2 was not read numerically);
  - the E4 per-trade size (0.8 x daily sigma from SR 1188's 1.3% annual vol).
- SR 1188 is a staff report (March 2026, revised July 2026), not peer reviewed. Its spillover table has no period split.
- g13-g15 for 2010-2019: NFP coverage is not decided here. It rests on the RTY reader's shared/macro_calendars.md, which did not exist when this file was finished.
- ZN's shared/rates_class_notes.md and shared/aalto_thesis_notes.md did not exist when this file was finished. Bond-class evidence is cited by path only.
- Not fetched, out of scope:
  - Brooks, Katz and Lustig post-FOMC drift (multi-day);
  - pre-refunding-announcement gains (long end, daily; abstract only on RePEc);
  - Kurov et al. pre-announcement drift (10Y; ZN reader).
- Searches for minute-level 2Y-futures studies of momentum or reversal, post-release continuation, short-end lead-lag and FOMC-day drift found no primary post-2015 study (4 searches). This is a gap in what was found, not evidence that no effect exists.
