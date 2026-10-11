# Stage E.20 Part A: product report, RTY (vehicle M2K)

Reader: ProductReader-RTY-OpusHigh (opus, high). Worked 2026-10-11 10:32-10:56 PDT
(17:32-17:56 UTC). JSON: `reports/stage_e20_briefs/product_RTY.json`.
Shared notes written: `shared/equity_class_notes.md` (equity-class literature) and
`shared/macro_calendars.md` (FOMC, CPI, NFP, PPI, GDP, ISM; EC-K9). No data store opened, no E.15,
E.17, E.18 or Gate 0 result read, no bar value read.

Root facts (root table): M2K tick $0.50 (0.10 index point, $5 x index); D8 round-trip wall 6.346
ticks = $3.17; equity group O 08:30, C 15:00, F 15:08 CT; backward window 2017-06-01..2019-05-05
(no CME unit before 2017-07-10, R-S4); search window 2019-05-06..2024-02-29.
Conversion used throughout: 1 bp of notional = L/1000 M2K ticks at index level L. At L = 2,000 that
is 2 ticks = $1 per bp, so the D8 wall is about 3.2 bp (4.2 bp at L = 1,500; 2.6 bp at 2,400).
Level source: Wikipedia, "Russell 2000 Index": "The index first traded above ... the 2,000 level on
December 23, 2020" (`pages/RTY/wikipedia_russell2000.html`). The 1,500-2,400 range for the search
window is this reader's approximation [unverified beyond that one level].

**Listing check (assignment).** Verified. CFTC-hosted Nadex rule certification of 2017-06-22
(`pages/RTY/cftc_ptc062517nadexdcm001.pdf`, sha256 802b02d2...): "On April 12, 2017, CME announced
that beginning on July 10, 2017, it would list futures (and options) contracts based on the Russell
2000 Index, including the E-mini® Russell 2000® Index Futures. The E-mini Russell 2000 Index Futures
currently serves as the underlying asset class for the Nadex US SmallCap 2000 contracts, and is
traded on ICE." This agrees with E.16's S04 (CME 17-110, its copy line 76: "for trade date of
Monday, July 10, 2017"). Before that date the Russell futures traded on ICE, so no GLBX bars exist.
M2K itself: first trade date 2019-05-06 (CME/CBOT filing, CFTC `ptc041519cmedcm003.pdf` line 77:
"effective on Sunday, May 5, 2019, for trade date Monday, May 6, 2019"), the first day of the search
window; MES has the same date.

## 1. Evidence

Full notes, quotes and locations: `shared/equity_class_notes.md`. "Derived" = this reader's
arithmetic (annualized / 252, the papers' annualization of one trade a day). Ticks at L = 2,000.

| ID | Effect | Rule | Hold | Gross per trade | Gross/net | Sample | Decay evidence | Source (grade) |
|---|---|---|---|---|---|---|---|---|
| E1 | ROD -> LH, Russell futures (ER) | sign of r_ROD = P(15:30 ET)/P(prior 16:00 close) - 1; hold to 16:00 ET | 30 min (14:30-15:00 CT) | beta 6.00 (x100, t 5.86): about 6 bp per 1 % of r_ROD = 12 ticks per 1 %; mean per trade not derivable (mean abs r_ROD for ER not reported) | gross | ER 1993-02-08..2020-05-01, 1-min, R2 3.35 %, R2_OOS 3.15 % | none post-2020 for ER; see E8, E9 | Baltussen et al. JFE 2021, Table B1 (primary, on-disk copy) |
| E2 | ONFH -> LH, ER | r_ONFH = P(10:00 ET)/P(prior close) - 1 | 30 min | beta 8.17 (t 4.62), R2_OOS 2.21 % | gross | as E1 | ES ONFH R2_OOS -1.68 % in the same table; program's CP1 (this form) already failed | same table (primary) |
| E3 | First half-hour sign -> LH, SPY | long if r1 > 0 else short at 15:30 ET, r1 from previous close to 10:00 ET | 30 min | 6.67 %/yr, Sharpe 1.08; derived 2.65 bp = 5.3 ticks | gross | SPY 1993-2013 | none post-2013 in paper | Gao, Han, Li, Zhou JFE 2018 (Dec 2015 WP; primary, WP version) |
| E4 | E3 after spread | ask/bid at 15:30, close at 16:00 | 30 min | 2005-2013: 7.96 %/yr gross -> 6.52 %/yr net (derived 3.16 -> 2.59 bp) | net (spread only) | SPY 2005-2013 | spread about 1.2 bp after 2005 | Gao et al. Table 10 (primary) |
| E5 | First half-hour -> LH, IWM (Russell ETF) | mean-variance weights in [-0.5, 1.5] | 30 min | 11.72 %/yr (t 5.18), OOS R2 2.43 %; not convertible per trade (SPY same method 6.85 %/yr) | gross | IWM 2000-05-26..2013-12-31 | none post-2013 | Gao et al. Table 12 (primary) |
| E6 | E3 on FOMC statement days | E3's rule on FOMC days only | 30 min | 20.04 %/yr (t 2.46) vs 6.24 on other days; derived 7.95 bp = 15.9 ticks | gross | SPY 1993-2013, about 165 events | none post-2013; related pre-FOMC drift gone after 2015 (E11) | Gao et al. Table 8 (primary) |
| E7 | First half-hour sign -> LH, S&P 500 cash index | as E3 | 30 min | 6.567 %/yr, Sharpe 1.115; derived 2.61 bp = 5.2 ticks | gross | .SPX 2005-10..2017-12 | none post-2017 | Li, Sakkas, Urquhart JFM 2022 (primary, accepted MS) |
| E8 | Hourly momentum by dealer net gamma, ES | momentum return by gamma quartile | 10-120 min | 60 min: Q1 +0.633 bp, Q4 -1.144 bp, Q4-Q1 -1.777 bp (t -3.93) | gross | ES 2018-01..2024-12 | itself post-2018: reversal when gamma high | Adams et al. draft 2026-07-15 (primary, unpublished) |
| E9 | ROD -> LH retest, SPX | r_ROD from the open | 30 min | slope +0.006 (t 0.6); +0.055 (t 3.1) on short-gamma closes | gross | SPX 2022-04..2026-08, 1,085 days | flat every year | firmtape, dev.to 2026-08-27 (UNREVIEWED; graded unverified) |
| E10 | Pre-FOMC drift, SPX | long into scheduled FOMC statement | 24 h incl. overnight | 49 bp per event over 24 h; the FOMC-morning share is shown only in a figure (unsized) | gross | SPX 1994-09..2011-03 | E11 | Lucca and Moench NY Fed SR 512 / JF 2015 (primary) |
| E11 | Pre-FOMC drift after 2015 | as E10, to 2019-12 | 24 h | "essentially disappeared after 2015" (unsized) | unknown | US equities 1994-2019 | the finding is decay | Kurov, Wolfe, Gilbert FRL 2021 ([secondary-only], abstract) |
| E12 | End-of-day momentum from LETF and gamma imbalance, single stocks | cross-section | to close | not converted (stocks) | gross | US stocks 2005-05..2020-07 | significant in all 2012-2019 subsamples; LETF effect constant | Barbon, Beckmeyer, Buraschi, Moerke WP 2021 (primary, WP) |
| E13 | Noise-area momentum, SPY (V34 drop) | bands from open +/- 14-day mean abs move | intraday | no per-trade figure; unlevered 6.2 %/yr net, Sharpe 0.61 | net | SPY 2007-2024 | n/a | Zarattini, Aziz, Barbon WP 2025 (primary) |
| E14 | Overnight -> LH; first half-hour not predictive | n/a | 30 min | n/a | unknown | 1999-2014 | n/a | Liu and Tse IREF 2017 ([unverified], not retrieved) |
| E15 | 20 equity, bond, FX futures 2008-2024 | n/a | n/a | no figures | unknown | 2008-01..2024-10 | patterns persist; may not survive costs | Aalto thesis ([shared, see shared/aalto_thesis_notes.md], metadata only) |

Reading of decay and costs.
- Russell-specific evidence is old: E1 and E2 end in 2020-05 and E5 in 2013. On the same methods,
  Russell's momentum is at least as strong as the large-cap indices': ER's ROD R2_OOS 3.15 % vs ES
  2.29 %, NQ 3.76 %; IWM's mean-variance gain 11.72 %/yr vs SPY's 6.85 %/yr. Russell also has the
  largest leveraged-ETF exposure in Baltussen's equity list (X^2 - X share 0.0085 vs ES 0.0034),
  the channel Baltussen and Barbon et al. tie to end-of-day momentum.
- Per-trade sizes for the first half-hour form are about 2.6 bp gross (E3, E7), close to M2K's wall
  of about 3.2 bp at L = 2,000: ratio near 0.8 before any decay, so it fails the 1.5x hurdle
  unconditionally. Only the FOMC-day interaction (E6, about 7.95 bp) clears it, on 1993-2013 data.
- Post-2018 evidence (E8 primary draft, E9 unreviewed, E11 abstract) all points the same way:
  weaker or reversed equity intraday momentum since 2018, and no pre-FOMC drift since 2015. None of
  it is on Russell. E.20's H6 tests ROD -> LH directly on NQ after the paper's sample.
- Gamma-conditioned results (E8, E9's conditional, Baltussen Table 7, E12) need option-position
  data, not bars of the 17 roots: none can be a feature under section 6's rule.

## 2. Feature availability

Basis: listing dates and calendar files only. RTY's backward window has bars only from 2017-07-10.
Warm-up milestones count trade dates from `data/calendars/hist2010/equity.json` (weekdays minus full
closures; 469 trade dates 2017-07-10..2019-05-05, 15 of them early-halt dates without rows, so each
milestone moves a few days later). Equity calendars: hist2010 2010-06-01..2019-05-31 (0 unsourced,
sha256 b12aee43...); `data/calendars/equity.py` 2019-05-01..2026-06-19 (sha256 3315e812...).

| Feature | Legs | Calendars / tables | 2010-2019 (RTY window) | 2019-2024 | Dates and basis |
|---|---|---|---|---|---|
| cp1_ret, cp2_range, cp2_brk | RTY | equity group calendar | partial | yes | from 2017-07-10 (first CME date); none 2017-06-01..07-09 |
| cp3_clv | RTY | equity group calendar | partial | yes | from 2017-07-11 (needs a prior complete date) |
| g01_ret30, g02_ret60, g03_ret120, g04_ret_day | RTY | calendar; sigma_X,d (20 dates) | partial | yes | from about 2017-08-07 (21st trade date) |
| g05_gap | RTY | calendar (previous date, C_X); sigma | partial | yes | from about 2017-08-07; not applicable after early-halt dates (SG-4) |
| g06_rv60, g07_range, g08_prev_ret, g10_logvol30 | RTY | calendar; 20-date bases | partial | yes | from about 2017-08-07 |
| g09_vol_state | RTY | calendar; sigma; 120-date median | partial | yes | from about 2018-01-24 (141st trade date) |
| g11_t_index, g12_dow, g16_month_end | rows only | equity group calendar | partial | yes | calendar covers 2010-06..2019-05, rows exist from 2017-07-10 |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | rows only | frozen release calendar, M2K D8 list = NFP, FOMC, ISM_SERVICES | partial | yes | 2010-2019: FOMC only on file (E.14; 15 statements 2017-07-26..2019-05-01, all 14:00 ET official); NFP and ISM services: no file. 2019-2024: 151 releases (NFP 57, FOMC 37, ISM 57). [shared, see shared/macro_calendars.md] |
| k9_anncday | M2K rows | EC-K9 (FOMC, NFP, GDP, ISM mfg, CPI/PPI) | no | yes | 2019-05-01..2024-02-29, 240 dates, no uncovered span; no 2010-2019 file. [shared, see shared/macro_calendars.md] |
| g17_nq | NQ | none | no (by design) | no (by design) | not applicable on RTY rows: the code drops the lead of the row's own cluster (`generic.py` _lead: `ok &= view.cluster != own_cluster`; K1 lead = NQ) |
| g17_zn, g17_6e, g17_cl, g17_gc, g17_zc | ZN, 6E, CL, GC, ZC | lead listing | undetermined here | undetermined here | apply on RTY rows; each lead's listing is audited by that root's reader (product_ZN/6E/CL/GC/ZC) |
| g17_mes | MES (not a 17 root) | listing | no | yes | MES first trade date 2019-05-06 (CFTC ptc041519cmedcm003); leg outside the 17 roots |
| g17_mbt | MBT (not a 17 root) | listing | no | partial | listed 2021 per the brief (not re-verified); leg outside the 17 roots |
| r_rod, abs r_rod ratio (prompt-added; context) | RTY | C = 15:00 CT; 60 prior dates | partial | yes | r_rod from 2017-07-11; ratio from about 2017-10-02 (61st date) |
| k1_vwap_dist, k1_vxn_regime, k1_vxn_band, k8_wkndbtc_move | NQ, MBT | - | n/a | n/a | apply on MNQ rows only, not RTY rows (E.11 coverage section 2) |

Every RTY-row feature is at most "partial" over 2010-2019 because RTY's GLBX history starts
2017-07-10, inside the E.16 window that starts 2017-06-01. Whether that counts as "exists causally
over both windows" under F6 is the lead's ruling.

## 3. Proposed features

One proposal. Considered and not proposed: a pre-FOMC drift flag (Lucca and Moench), because the
morning-only part of the drift is not sized in the paper and the drift "essentially disappeared after
2015" (E11, abstract only); the r12 (second-to-last half hour) joint signal of Gao et al., because
r12 ends at 14:30 CT, after t4 (14:08 CT); every gamma or LETF-flow conditioner (needs non-bar data).

**P1. `fomc_r1`: first-half-hour return on FOMC statement days (Gao et al., Table 8).**
- Source quote: "Release FOMC 20.04** 5.84 3.43" (Table 8 Panel B: Avg Ret %/yr, Std Dev, Sharpe);
  rule (Sec. 3.1): "we will take a long position in the market at the beginning of the last half-hour
  if the timing signal is positive, and take a short position otherwise ... the position (long or
  short) is closed at the market close"; r1 (Sec. 2): "we calculate the first half-hour return using
  previous day's close price and the price at 10:00am Eastern time".
- Formula: on RTY rows of trade date d, if d is a scheduled FOMC statement date, value =
  close(b_{08:59}, the bar closing 09:00 CT on d) / close(b_{C-1}, the bar closing at C_X = 15:00 CT on
  the equity calendar's previous trade date) - 1, flag 1; else 0 and flag 0. Direction: sign(value).
  Not applicable after an early-halt date (no C_X close), as G5. Missing bar: row excluded.
- Decision time and horizons: t4 (14:08 CT) with h60 and F (both exit at 15:08 CT). Legs: RTY.
  Calendars: FOMC statements, `reports/stage_e14_cal_releases.json` (2010-06-01..2019-05-31) and
  `reports/stage_e2b_release_calendar.json` (2019-05-01..2026-06-21); equity group calendars.
- Availability: both windows on the calendar side (FOMC is the one macro calendar on file for both);
  RTY rows only from 2017-07-11, so 15 FOMC dates in the backward window and 37 in the search window.
- Expected gross: 20.04 / 252 = 7.95 bp per trade (SPY, 15:30-16:00 ET, 1993-2013, t 2.46, about 165
  events). At L = 1,500 / 2,000 / 2,400: 11.9 / 15.9 / 19.1 ticks against the D8 wall of 6.346 ticks
  ($3.17): ratio 1.88 / 2.51 / 3.01. Clears 1.5x on the published figure.
- What lowers that expectation (the lead should weigh it): SPY not Russell; t4's 59-minute hold
  (14:09-15:08 CT) is not the paper's 14:30-15:00 CT and includes 15:00-15:08 after the cash close;
  no post-2013 test of the FOMC interaction; the ONFH signal weakens out of sample in later work
  (Baltussen ES R2_OOS -1.68 %; Rosa 2022, NQ reader); the related pre-FOMC drift is gone after 2015
  (abstract only); the paper labels the dates "FOMC minutes" while giving statement timing; it is a
  conditional of the CP1 (ONFH) family the program already screened. Few events: 52 in total.
- Not a data-driven choice: it comes from the paper's Table 8 only; no program data or result was read.

## 4. NQ only

n/a.

## 5. Fetch log, terms read, budget notices

Full log with sha256: `reports/stage_e20_briefs/pages/RTY/fetch_log.tsv` (41 lines) and the JSON
`fetch_log`. Pages used as evidence (UTC):

| URL | UTC | sha256 (prefix) | Saved | Status |
|---|---|---|---|---|
| https://www.cftc.gov/IndustryOversight/IndustryFilings/PTCDCMRules/36900 | 17:37:37 | d2a57ce085d1a578 | pages/RTY/cftc_ptcdcm_36900.html | ok |
| https://www.cftc.gov/filings/ptc/ptc062517nadexdcm001.pdf | 17:37:57 | 802b02d2d46dc098 | pages/RTY/ | ok |
| https://www.jean-sebastienfontaine.com/papers/0dte-options-volatility.pdf | 17:38:22 | 6b256ade06bd6428 | shared/adams_etal_0dte_fontaine.pdf | ok |
| https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf | 17:39:35 | 050d5680d1424a5f | shared/gao_han_li_zhou_wp2015_mql5.pdf | ok |
| https://dev.to/firmtape/intraday-momentum-is-dead-in-the-0dte-era-we-measured-it-on-1085-spx-sessions-43g0 | 17:40:09 | 7b66ef35a5dbd9b1 | shared/devto_firmtape_spx_retest.html | ok |
| https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf | 17:41:00 | 39add97e355b49c0 | shared/li_sakkas_urquhart_2022_accepted.pdf | ok |
| https://ideas.repec.org/a/eee/finlet/v40y2021ics1544612320315956.html | 17:42:06 | a55f8ef6bd4fd27a | shared/ideas_kurov_wolfe_gilbert_2021.html | ok |
| https://alexandria.unisg.ch/server/api/core/bitstreams/a99aba00-.../content | 17:43:49 | 41d635d162551c4a | shared/zarattini_aziz_barbon_beat_the_market.pdf | ok |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf | 17:44:55 | c7cb0f335c60cb9f | shared/lucca_moench_sr512.pdf | ok |
| https://www.cftc.gov/IndustryOversight/IndustryFilings/TradingOrganizationProducts/41359 | 17:45:53 | 9fc0fc648baf662b | pages/RTY/cftc_products_41359.html | ok |
| https://www.cftc.gov/filings/ptc/ptc041519cmedcm003.pdf | 17:46:01 | 224f824a95bad7f7 | pages/RTY/ | ok |
| https://en.wikipedia.org/wiki/Russell_2000_Index | 17:47:15 | 05305db4cdeee4ae | pages/RTY/wikipedia_russell2000.html | ok |
| https://www.alexandria.unisg.ch/server/api/core/bitstreams/5a99db31-.../content | 17:48:06 | 4c2cbcd35d990144 | shared/barbon_beckmeyer_buraschi_moerke_letf.pdf | ok |

Failed or withdrawn: Skidmore copies of Kurov-Wolfe-Gilbert and KSSW 2017 (404, curl and scrapling
get); efmaefm.org (TLS chain error, curl and scrapling); reading-9.eprints-hosting.org (DNS);
SelectedWorks (retired page); olin.wustl.edu Zhou page (404); eprints.soton.ac.uk (401 security
page; irrelevant record); an MPRA record (irrelevant; deleted). Wikipedia `/w/index.php?action=raw`
was fetched before reading its robots line `Disallow: /w/`; the copy was deleted, the row is logged
"terms-forbid", and the allowed `/wiki/` page was used instead.

Terms read (robots.txt; JSON `terms_read` has each ruling): cftc.gov (Content-Signal
`use=reference`, `ai-train=no`: reference reading allowed), nadex.com, jean-sebastienfontaine.com
(none, 404), c.mql5.com, dev.to, centaur.reading.ac.uk (CC BY-NC-ND), skidmore.edu, ideas.repec.org,
alexandria.unisg.ch, newyorkfed.org, en.wikipedia.org; efmaefm.org unreadable (nothing fetched).
No cmegroup.com page fetched, live or archived; CME text comes only from CFTC-hosted filings.

Budget: 20 WebSearch calls of about 90; no over-budget notice. Firecrawl not used.

Incident: the session scratchpad is shared by all readers; another reader's `fetch.sh` overwrote
mine at the same path, so my first four fetches (17:37 UTC) saved nothing and wrote four rows into
`pages/LE/fetch_log.tsv`. I removed exactly those four rows (all containing
`pages/LE/reports/stage_e20_briefs/pages/RTY`) from the LE log and refetched under a private
script. No LE file other than that log was touched.

## 6. Unfinished and unverified

- Gao et al.: the published JFE 2018 version was not retrieved; all Gao numbers are from the
  December 2015 working paper on a third-party host and may differ from the journal version.
- Kurov, Wolfe, Gilbert (2021): abstract only [secondary-only]. Liu and Tse (2017): [unverified].
- No per-trade ROD -> LH figure for Russell: Baltussen does not report the mean abs r_ROD per market.
- No post-2015 Russell-specific intraday study found (three searches); a gap, not evidence of absence.
- g17 leads ZN, 6E, CL, GC, ZC: left to their readers. MBT's 2021 listing not re-verified.
- Russell index levels 1,500-2,400 for the search window: approximate; only the 2,000 crossing on
  2020-12-23 is quoted.
- 2010-2019 NFP, ISM services, ISM manufacturing, CPI, PPI, GDP calendars do not exist on disk;
  building them is outside this brief (see `shared/macro_calendars.md` section 5).
