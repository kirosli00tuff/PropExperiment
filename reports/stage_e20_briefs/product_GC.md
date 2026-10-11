# E.20 Part A: product reader GC (COMEX gold; vehicle MGC, price path GC)

Reader: ProductReader-GC-OpusHigh. Written 2026-10-11, 10:33 to 10:54 PDT. Shared brief:
`reports/stage_e20_briefs/brief_partA_shared.md`. Assignment: the metals class (I am the only metals
reader), London fix and LBMA auction history, a feature audit for GC's rows, and GC's listing as a G17
lead. JSON twin: `reports/stage_e20_briefs/product_GC.json`. Raw pages: `reports/stage_e20_briefs/pages/GC/`.

Unit conversions used throughout. MGC is 10 oz with a $0.10/oz tick, so one tick is $1.00 and one
basis point of notional is (price x 10 x 0.0001) dollars, which equals that many ticks.
- Search window: price $1,800.09/oz, the LBMA 2022 average. Kitco reports: "the LBMA reported that gold prices averaged
  $1,800.09 an ounce last year" (`pages/GC/kitco_lbma_2022_averages.html`). So 1 bp = $1.80 = 1.80 MGC ticks.
- Backward window: price $1,433.61, the mean fix price in Aspris et al.'s 2012-02..2015-03 pre-period
  (Table 2). So 1 bp = 1.43 ticks.
- D8 round trip for GC (root table): 5.597 MGC ticks = $5.60, which is 3.11 bp at $1,800. 1.5x D8 =
  8.40 ticks = 4.66 bp.

## 1. Evidence: published intraday gold evidence since 2015 (plus the pre-2015 fix context)

| Id | Effect | Rule (as published) | Hold | Gross per trade | Gross/net | Sample | Decay evidence | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD -> LH market intraday momentum, GC row | Regress r_LH (last 30 min of GC's 08:20-13:30 ET day, i.e. 12:00-12:30 CT) on r_ROD (prior close to 30 min before close). Strategy: long if r_ROD > 0, else short, for the last half hour | 30 min, ending 13:30 ET = 12:30 CT (COMEX settlement) | GC: beta_ROD = 1.09 (x100), so 1.09 bp of expected r_LH per 1% r_ROD, which is 1.96 MGC ticks at $1,800. The commodity 1/N portfolio returns 4.34%/yr (SR 1.42), about 1.72 bp per trade if annualized over 252 days (derived), which is 3.10 ticks: 0.55x D8 | gross | GC 1984-01-05..2020-05-01, 9,044 obs, 1-min (Tickdata) | Commodity pool: beta_ROD 1.59 (t 3.92) in 1974-1999, 1.04 (t 2.86) in 2000-2020. GC R2_OOS 0.08% (5% level). No post-2020 metals evidence: the Aalto thesis has no commodities (`shared/aalto_thesis_notes.md`) | Baltussen, Da, Lammers, Martens, JFE 142 (2021); on-disk copy (L893, L1668, L1742, L3289, L3764). [shared, see `shared/baltussen_notes.md` L98, L121] | primary |
| E2 | London fix window in GC, before and after the 2015 auction | CAR in GC from fix start, signed by the eventual fix direction ("assuming an informed view"); 90-min window around the fix | 10 / 30 / 60 min | Gold CAR 10 min: 9.41 bp before (13.5 ticks at $1,433.61) vs 5.65 bp after (6.7 ticks at the post mean $1,192.57). Difference -3.76 bp, not significant. Not tradeable: the sign uses foresight of the fix direction | gross, foresight | GC Globex 1-min/5-s, 2012-02-14..2015-04-30 (gold post-period about 6 weeks) | Lower after the reform, but n.s. "A possible cause of this is the small sample of data in the post period." After the reform: "no significant leakage prior to the start of the fix" | Aspris, Foley, Gratton, O'Neill (2017), EFMA Athens WP | primary (WP) |
| E3 | PM fix leakage (pre-2015 regime; context for 2010-2015) | Informed trader signed by fix direction; public predictor = GC direction 15:00-15:06 London | 4 min after the fix start; 2 min before the end | "around 10bps in the four minutes following the start of the fixing, and a possible further 4bps in the two minutes before the end". Foresight-based; "no significant returns following the end of the fixing" | gross, foresight | GC 2007-01-01..2012-12-31, 1,504 days, 1-min | Superseded by the 2015 auction; E2 finds no pre-start leakage afterwards | Caminschi & Heaney, JFM 34(11) 2014 (UWA accepted manuscript). Published before 2015: context only | primary (AAM) |
| E4 | Hat-shaped 24-h gold pattern; drops into the AM and PM fixes | Gold rises in Asian hours and falls in Western hours. 30-min window before each London fix | 30 min (fix), about 21 h (West) | PM fix: -4.2 pp annualized (text, p.37; the intro says -3.9%). That is about -1.7 bp per day if the annualization is x252 (derived, convention [unverified]): about 3 ticks, 0.5x D8. West: -10.0% annualized | gross. Backtests underperform the market after spread costs | GC1/GC2 5-min bid/ask, 2001-2018 | PM fix: "especially between 2007 and 2011 returns are strong ... before and after that time they are small and insignificant". West leg significant only in 2013, 2015, 2017 | Donati & Jung, CBS MSc thesis (2019) | primary (thesis; lower tier) |
| E5 | Abnormal-return day momentum; next-day contrarian (gold) | Strategy 1: once a day's return passes mean + 2 sd at the "timing parameter" hour, trade in its direction to the day end (GMT+3). Strategy 2: next day, contrarian for gold | To the day end (GMT+3 midnight) | S1 0.70% (pos) and 1.05% (neg) per trade; selection uses the day's ex-post abnormal return (look-ahead). S2 gold contrarian 0.07% (t 1.36) and 0.15% (t 0.73), "Not rejected" vs random | gross ("does not incorporate transaction costs") | Broker (MetaQuotes) hourly, 2009-01..2020-03 | None. The fair version (S2) is not significant | Caporale & Plastun, FMPM 35 (2021) 353-368 (on-disk Brunel copy) | primary |
| E6 | FOMC surprise response in gold | 5- and 10-min GC returns after FOMC rate surprises | 5-10 min | 1-sd loosening surprise: about 23 bp; tightening: about 4 bp. "the adjustment 10 minutes after the shock is significantly threefold higher than after 5 minutes". Needs a surprise measure; no rule beyond 10 min | gross (no strategy) | GC 5-min (Olsen), 2007-01-02..2020-12-31 | None reported | Awartani, Hussain, Virk, IRFA (2024), authors' final manuscript (MMU figshare) | primary (AAM) |
| E7 | Intraday overreaction then reversal | Contrarian after decile-1 moves between turning points; earns 20% of the reversal range | Until the next turning point | GC decile 1, short after positive overreaction, pre-Covid: 0.15 (table units, probably %) [unit unverified]. Turning points are ex post, so not causally codable | gross ("transaction costs ... negligible", asserted) | 20 futures, 1-min/15-min/1-h, 2019-11-20..2020-06-03 | Covid-dominated six months; no OOS | Borgards, Czudaj, Hoang, Resources Policy 71 (2021), Europe PMC full text | primary |
| E8 | Day (open-to-close) returns negative in COMEX gold | Day return < 0, overnight > 0 | Day session | Not stated in the abstract | abstract says "economically important even with transaction costs" | COMEX GC front; 1985-2012 (2014 paper) | 2014 abstract: "The asymmetry has weakened substantially over the years, but it is still present" | Blose, Gondhalekar, Kort, J. Econ. Finance 42(3) (2018); Blose & Gondhalekar, AEL (2014) | abstract only |
| E9 | Flight to gold after extreme negative 5-min S&P 500 moves (source of K8-flight-01) | Gold reacts positively after extreme negative 5-min S&P moves; continues after US stock hours on extreme days | Minutes | Not stated | unknown | Intraday gold and S&P 500, 2007-2018 | None in the abstract | Baur & Kuck, Finance Research Letters 33 (2020) | abstract only |
| E10 | Fix reform and daily gold futures | Daily volatility and returns before and after 2015-03-20 | daily (not intraday) | n/a. "returns have been unaffected by the recent changes in the fixing processes" | n/a | CME Globex SI/GC daily, 2008-01..2018-06 | n/a | Crain, Hoelscher, Jones, ACRN JoFRP 9 (2020) | primary |
| E11 | First half-hour momentum, SHFE gold (class, not COMEX) | r_first30 predicts later half hours before night trading; the effect disappears after night trading starts | 30 min | not sized | n/a | SHFE gold 2008-01-10..2021-10-20, 1-min | Predictability "disappears" after the night-session launch | Zhou (Ivy) et al., ACFR conference paper | secondary-only (Firecrawl model answer; not saved raw) |
| E12 | Macro-announcement response in gold futures | 10-s intervals around US releases | 90 s | volume +405%, volatility +220% in the first 10 s; back to normal "within 90 seconds" | n/a | GC TRTH 2006-11-24..2012-12-31 | n/a | Smales & Yang, IRFA 41 (2015) | secondary-only (E.0 log `reports/stage_e0_research_K5.md` K5-004; not re-fetched) |
| E13 | Fix reform: spreads and depth in exchange products | Before vs after the auction reform | n/a | n/a: lower spreads, more depth | n/a | not in abstract | n/a | Aspris, Foley, O'Neill, JFM 40(11) (2020) | abstract only |
| E14 | Settlement-window (12:29-12:30 CT) effects in GC | Searched (2 queries); no study found | | | | | | | null: gap in the record, not evidence of absence |

Reading. No source since 2015 gives a sized, causally codable intraday rule for COMEX gold that
clears the cost wall. The only sized, codable effect is Baltussen's ROD -> LH. For the commodity
portfolio it comes to about 1.7 bp (about 3.1 MGC ticks) per trade, gross, which is 0.55x D8 and below
the 1.5x hurdle. GC's own coefficient is significant (t 2.95) with a small R2_OOS (0.08%). The commodity
coefficient falls by about a third from 1974-1999 to 2000-2020, and nothing covers metals after 2020.

The published GC last half hour is 12:00-12:30 CT and ends at the COMEX settlement. E.20's gold
decision times are t1 07:50, t2 10:20, t3 12:50 and t4 14:08. None is at 12:00, and t3 and t4 come after
that window. Baltussen gives no evidence for gold after the settlement. The prompt's r_ROD features
are not re-proposed here.

The fix-window effects are foresight-signed (E2, E3) or decayed. The PM-fix drop was strong in
2007-2011 and "small and insignificant" outside it (E4). Aspris finds no pre-start leakage after the
2015 auction (E2). Event responses (E6, E12) finish within 90 s to 10 min, far shorter than the 60-minute
minimum hold. Overreaction (E7) and abnormal-day momentum (E5, Strategy 1) depend on ex-post
information. The fair variant of E5 is not significant. Every sized figure is gross.

What existed in 2010-2015 (for features defined on the auction). Until 2015-03-19 the London Gold
Fixing ran twice daily, "an 'AM fixing' commencing at 10:30AM London time and a 'PM fixing' at 3:00 PM
London time", as "a teleconference of five members" (Caminschi & Heaney, AAM p.~3). Deutsche Bank
resigned in May 2014, "leaving the Fix with 4 members only" (Donati & Jung, p.19-20). "The change in
the gold fix occurred on March 20, 2015, when the new auction platform replaced the twice-daily
telephone conference fixing process by five market participants" (Crain et al., p.178). "Like before, the
LBMA Gold Price is fixed twice a day at 10:30 and 15:00" (Donati & Jung). The IBA auction runs in "rounds
that are 45 seconds in duration" (Aspris et al. 2017).

So the event instants (10:30 and 15:00 London) are the same in both regimes. The mechanism (fixing
teleconference vs electronic auction) and the participant count changed. The fix duration (10-15 min
under the old fix; "almost always complete within ten minutes" under the new one) also changed. The
fix-day calendar (London business days less the announced no-PM half days) is not on disk for
2010-2019; see section 2.

## 2. Feature availability (GC's rows, and GC as a leg)

Windows: backward 2010-07-01..2019-05-05; search 2019-05-06..2024-02-29. Basis: listing and calendar
files only, never a bar.

GC listing. COMEX GC trades over both windows. E.16 sets GC's window start to 2010-07-01, with
2010-2019 bars from "C1's ext2010 plan (E.17)" (`reports/stage_e16_windows.json` products.GC). The
E.14 hist metals calendar lists GC among its products for 2010-06-01..2019-05-31
(`data/calendars/hist2010/metals.json`). Baltussen's Table A3 has GC data from 1984-01-05 to
2020-05-01.

Calendars referenced:
- **HIST-MET**: `data/calendars/hist2010/metals.json`. 2010-06-01..2019-05-31; 2,323 trade dates, 26
  closures, 73 early halts, 0 unsourced; CME documents via Wayback.
- **MET19**: `data/calendars/metals.py`. CALENDAR_COVERAGE 2019-05-01..2026-06-19.
- **MFS**: `strategy/members/k5/_calendar.py` METALS_FULL_SESSIONS. 2019-05-01..2026-06-18.
- **GAM / GPM**: `strategy/members/k5/_releases.py` GOLD_AM_AUCTIONS and GOLD_PM_AUCTIONS. TABLE_RANGE
  2019-05-01..2026-06-19; generated from the frozen release calendar and E.4b's release check.
- **FLT**: `strategy/members/k8/_calendar.py` FLIGHT_DATES. TABLE_RANGE 2019-05-01..2026-06-19.
- **REL19**: `reports/stage_e2b_release_calendar.json` (sha 839f2437...). 2019-05-01..2026-06-21. GC/MGC
  rows: FOMC 57, NFP 85, CPI 85, G.17 Industrial Production 85.
- **REL10**: `reports/stage_e14_cal_releases.json`. 2010-06-01..2019-05-31; only NGS, WPSR and FOMC (72
  FOMC rows, 58 time-official and 14 inferred).
- **SETL**: `reports/stage_e16_settlement.md` (GC S = 12:30 CT, window 12:29:00-12:30:00, primary,
  2010-06-07..2024-02-29). O = 07:20, secondary for 2015-09 onward.

| Feature | Legs | Calendars | 2010-2019 | 2019-2024 | Basis / dates | Shared ref |
|---|---|---|---|---|---|---|
| k5_ovr_ret | GC | O_X, C_X, trade dates; early-halt rule (MFS in code) | yes (derivable) | yes | Member clock t = O+60k <= C (08:20..12:20 CT), so it applies at t2 and t3 and carries to t4. HIST-MET gives trade dates and halts for 2010-06-01..2019-05-31, but the member's own table (MFS) starts 2019-05-01. A 2010-2019 MFS equivalent must be derived from HIST-MET; no such table exists yet | |
| k5_ovr_pct | GC | MFS (20 prior full sessions, 80% floor) | yes (derivable) | yes | As above. Warm-up: 20 full sessions after 2010-07-01 | |
| k5_pmfix_move | GC | GPM (PM auction days and instant T_P = 15:00 London in CT) | no | yes | GPM covers 2019-05-01..2026-06-19 only. No gold PM fix or auction calendar for 2010-2019 is on disk (REL10 has none; HIST-MET has sessions only). The instant (15:00 London) is the same before and after 2015-03-20, but the event changes from the fixing teleconference (to 2015-03-19) to the IBA auction (from 2015-03-20). Building it needs E&W bank holidays plus the 2010-2018 no-PM half days, which are not on disk | |
| k5_preauc_msince | none | GAM (AM instant 10:30 London) | no | yes | Same as k5_pmfix: GAM starts 2019-05-01. Old AM fixing at 10:30 London until 2015-03-19 | |
| (K5-fomc-01, excluded in V2.3) | GC | FOMC dates and instants | facts only: FOMC calendar yes (REL10) | yes (REL19 / k5 FOMC table) | Excluded because the move is known at 13:05 CT, after t3 12:50. **E.20's t4 = 14:08 CT is after 13:05**, so the K5-fomc move is known at t4 on FOMC dates. REL10 FOMC instants in CT: 13:15 (2010-2013, 14 dates), 11:20-11:35 (2011-2012, 8), 13:00 (2013-2019, 50). The member's table keeps only 13:00 CT instants. The lead decides whether this re-enters | |
| k8_flight_ret | MES | FLT; release guard (REL19) | no | yes | MES is not one of the 17 roots and was listed 2019-05-06, so it does not exist in the backward window. FLT starts 2019-05-01 | |
| k8_flight_tail | MES | FLT (20 prior dates, n >= 1,200) | no | yes | As above, plus warm-up | |
| cp1_ret | GC | O_X; trade dates (HIST-MET / MET19) | yes | yes | Port CP1: close(O+29) - open(first bar) | |
| cp2_range, cp2_brk | GC | O_X; trade dates | yes | yes | Port CP2 | |
| cp3_clv | GC | O_X, C_X of d-1; trade dates | yes | yes | Port CP3. C = 12:30 CT is primary in both windows (SETL) | |
| g01_ret30, g02_ret60, g03_ret120, g04_ret_day | GC | trade dates; sigma lookback | yes | yes | Own path | |
| g05_gap | GC | C_X of the previous trade date; early halts | yes | yes | HIST-MET early halts make G5 not applicable on those dates (SG-4) | |
| g06_rv60, g07_range, g08_prev_ret, g09_vol_state, g10_logvol30 | GC | trade dates (20 to 120-date lookbacks) | yes | yes | Own path; warm-up after 2010-07-01 | |
| g11_t_index, g12_dow | none | clock | yes | yes | | |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | none | D8 list for MGC/GC: FOMC, NFP, CPI, G.17 | partial | yes | REL19: all four, 2019-05-01..2026-06-21. REL10 2010-2019: FOMC only; NFP, CPI and G.17 have no 2010-2019 rows on disk | [shared, see `shared/macro_calendars.md` (RTY), not yet on disk when I finished; G.17 is not in RTY's list] |
| g16_month_end | none | group trade dates | yes | yes | HIST-MET / MET19 | |
| g17_gc (GC as the K5 lead on other roots' rows) | GC | none beyond the row's trade date | yes | yes | GC is listed over both windows (see above). Not applicable on GC's own rows (own cluster, SG-2) | |
| g17_nq, g17_zn, g17_6e, g17_cl, g17_zc (on GC rows) | NQ, ZN, 6E, CL, ZC | none | see those readers | see those readers | Listings audited by the NQ, ZN, 6E, CL and ZC readers | product_<ROOT>.md |
| g17_mbt, g17_mes (on GC rows) | MBT, MES | none | no | partial (MES from 2019-05-06; MBT from 2021) | Both legs are outside the 17 roots | |
| r_ROD, abs r_ROD over its median (added by the prompt) | GC | group C (12:30) | not audited | not audited | Given by the prompt | |

## 3. Proposed features

None proposed. The reasons:
1. No sized gold rule since 2015 clears 1.5x D8, which is 8.40 MGC ticks or about 4.7 bp at $1,800. ROD -> LH
   is about 3.1 ticks per trade (commodity pool, E1). It is also already in the prompt, and its
   published window (12:00-12:30 CT) is not one of E.20's decision times.
2. The fix-window effects are foresight-signed or decayed after 2011 and after the 2015 reform (E2-E4).
   A fix-based feature would also fail the both-windows calendar test: no 2010-2019 fix calendar is on
   disk (section 2).
3. Event-response studies (E6, E12) end within 10 minutes. At t4 the FOMC move is known, but nothing
   published sizes a 60-minute continuation from 14:08. I give this as an availability fact (section 2),
   not a proposal.
4. Considered and rejected:
   - E5 Strategy 2 (next-day contrarian): not significant, broker data, GMT+3 day; g08_prev_ret already
     carries the prior day's return.
   - E8 (negative day-session drift): no size, abstract only.
   - E9 (flight to gold on an NQ leg instead of MES): only the abstract is available, so it cannot be
     sized, and replacing the S&P 500 with the Nasdaq-100 would be a design choice of mine.

## 4. NQ only

n/a.

## 5. Fetch log, terms read, budget notices

Full rows (URL, UTC, sha256, size, status) are in `reports/stage_e20_briefs/pages/GC/_fetch_log.tsv`
and the JSON. Evidence pages:

| File | URL | UTC | sha256 (first 16) | Status |
|---|---|---|---|---|
| aspris_etal_2017_efma.pdf | http://efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2017-Athens/papers/EFMA2017_0580_fullpaper.pdf | 2026-10-11T17:38:42Z | 81c77b19eac1a4c4 | ok |
| crain_etal_2020_jofrp09m.pdf | http://www.acrn-journals.eu/resources/jofrp09m.pdf | 2026-10-11T17:38:46Z | 5e772b27baf96671 | ok |
| caminschi_heaney_2014_uwa_aam.pdf | https://api.research-repository.uwa.edu.au/ws/files/4725264/A0205_use_this.pdf | 2026-10-11T17:47:51Z | 76ff3e190c179ff3 | ok (research-repository.uwa.edu.au URL: 403 at 17:39:13Z) |
| awartani_etal_2024_irfa_aam.pdf | https://ndownloader.figshare.com/files/65204829 | 2026-10-11T17:40:33Z | 095015c35d6de6ad | ok. Two curl tries returned 202 empty (AWS WAF). `scrapling extract get` resolved the signed S3 redirect, then curl fetched the file. Licence: CC BY-NC-ND 4.0 (figshare API, awartani_figshare_api.json) |
| borgards_etal_2021_pmc9759686.xml | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9759686/fullTextXML | 2026-10-11T17:39:50Z | 98fd726eba6419bc | ok |
| repec_baur_kuck_2020.html | https://ideas.repec.org/a/eee/finlet/v33y2020ics1544612319301448.html | 2026-10-11T17:42:49Z | 8c876d9b7c74790d | ok (abstract) |
| repec_aspris_foley_oneill_2020.html | https://ideas.repec.org/a/wly/jfutmk/v40y2020i11p1691-1710.html | 2026-10-11T17:42:59Z | 5a39de936641ef19 | ok (abstract) |
| repec_sobti_etal_2021.html | https://ideas.repec.org/a/eee/finana/v78y2021ics1057521921002209.html | 2026-10-11T17:43:02Z | e8a59b9b461edbe8 | ok (abstract) |
| repec_blose_gondhalekar_2014.html | https://ideas.repec.org/a/taf/apeclt/v21y2014i18p1269-1272.html | 2026-10-11T17:43:43Z | 8be27e39be3ba45a | ok (abstract) |
| repec_blose_etal_2018.html | https://ideas.repec.org/a/spr/jecfin/v42y2018i3d10.1007_s12197-017-9403-0.html | 2026-10-11T17:43:47Z | 7300985d5df69900 | ok (abstract) |
| kitco_lbma_2022_averages.html | https://www.kitco.com/news/article/2023-01-27/gold-and-palladium-were-winners-2022-silver-and-platinum-lagged-lbma | 2026-10-11T17:48:32Z | 4057c271c459c9b9 | ok |
| hull_3303156.pdf | https://hull-repository.worktribe.com/OutputFile/3303156 | 2026-10-11T17:41:56Z | 88810a826a98bf3a | blocked (Cloudflare 403) |
| sbfc2019_P250.pdf | https://sbfc.sydney.edu.au/2019/papers/P250_Named.pdf | 2026-10-11T17:41:52Z | b9347f234dc3c8d5 | 404 |
| ACFR Zhou 4a PDF | https://acfr.aut.ac.nz/__data/assets/pdf_file/0008/686816/4a-Z-Ivy-Zhou.pdf | 2026-10-11T17:44:16Z | n/a | blocked (curl 403; Scrapling get 403, fetch empty). Read through a Firecrawl query answer only (E11, secondary-only) |

On-disk copies used (fetched by earlier stages; provenance from their logs):
- `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md`, sha 18cb436e...;
  provenance in `reports/stage_e13_info_sources.md` I-37b.
- `reports/stage_e10_research/overnight/cbs_gold_thesis.pdf`, sha 63858a75... (matches the E.10 log
  entry). URL
  https://research-api.cbs.dk/ws/portalfiles/portal/59803241/651553_Thesis_Contract_13383.pdf, fetched
  2026-10-03T05:44:44Z.
- `reports/stage_e10_research/regime/caporale_plastun_2020_gold_oil_brunel.pdf`, sha 1f5d5cfb...
  (matches). URL https://bura.brunel.ac.uk/bitstream/2438/21825/6/FullText.pdf, fetched
  2026-10-03T05:35:09Z. It is the typeset FMPM 35:353-368 text.
- `reports/stage_e20_briefs/shared/aalto_thesis_notes.md` (ZN reader) and `shared/baltussen_notes.md`
  (NQ reader).

Terms and robots read (robots.txt only; no site's full terms page was read, which is a gap):
- efmaefm.org and acrn-journals.eu: no robots.txt (404).
- figshare.com: robots returned 202 empty.
- ebi.ac.uk: Crawl-Delay 10, REST path allowed.
- research-repository.uwa.edu.au: Crawl-Delay 5, files allowed.
- ideas.repec.org: only /cgi-bin/ disallowed.
- kitco.com: Allow /.
- acfr.aut.ac.nz: robots 403.
- thesis.eur.nl: read, not used.
- lbma.org.uk and ice.com: robots read, no page fetched.
- cmegroup.com: never fetched.

Budget notices: none. I used 20 WebSearch calls of the about 90 allowed, and 2 Firecrawl scrapes of
one PDF (49 credits each, reported, no exhaustion).

Note: another worker's fetch helper wrote a row and a file (`terms_ageconsearch_robots.txt`,
ageconsearch.umn.edu robots, 17:39:05Z) into `pages/GC/` and its `_fetch_log.tsv`. It is not mine. I
left it untouched.

## 6. Unfinished and unverified items

- No 2010-2019 gold AM/PM fix (auction) calendar exists on disk. Its absence decides k5_pmfix_move and
  k5_preauc_msince as "no" for the backward window. Building one (London business days, the
  2010-2018 no-PM half days, the 2015-03-20 regime change) was out of scope.
- METALS_FULL_SESSIONS for 2010-2019: I marked k5_ovr "yes (derivable)" from HIST-MET. No derived table
  exists, and the derivation rule (full session = trade date that is not an early halt or late open)
  is my reading of the member's definition, not a verified equivalence.
- Baltussen's annualization convention (x252) behind the 1.72 bp per trade is [unverified]. So is
  the CBS thesis's annualization behind the -1.7 bp per day. Borgards's Table 2 units are
  [unverified] (probably percent).
- Abstract-only: Blose et al. 2018 (no size, no sample in the abstract), Baur & Kuck 2020, Aspris
  et al. 2020, Sobti et al. 2021.
- Secondary-only: Smales & Yang 2015 (E.0 log) and the SHFE Zhou paper (Firecrawl answer).
- Not retrieved: Nilsson (SSRN 2657767, the post-2015 pre-auction price pressure paper; E.0 also failed),
  Abrantes-Metz & Metz (2014 draft), Batten, Lucey & Peat (2016), Sobti (2025), Gu, Kurov & Stan (2023).
- Settlement-window (12:29-12:30 CT) evidence: none found in 2 searches. This is a gap, not a finding.
- `shared/macro_calendars.md` (RTY) was not on disk when I finished, so g13-g15 cite REL19 and REL10
  directly. G.17 (Fed industrial production) is on GC's D8 list but not in RTY's assignment, and it has
  no 2010-2019 rows on disk.
