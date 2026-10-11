# Stage E.20 Part A: product reader UB (Ultra U.S. Treasury Bond futures; vehicle UB)

Reader: ProductReader-UB-OpusHigh (opus, worker-high). Started 2026-10-11 10:33 PDT, finished 2026-10-11 10:45 PDT (JSON finished_utc 17:45:05Z).
Brief: reports/stage_e20_briefs/brief_partA_shared.md. Assignment (section 7): evidence specific to UB only.
Rates-class evidence is cited from the ZN reader, the Aalto thesis from shared/aalto_thesis_notes.md,
Baltussen et al. by grepping the on-disk copy, and the macro calendars from the RTY reader.
No data store, bar, E.15/E.17/E.18 result or Gate 0 result was opened. No cmegroup.com page was fetched.

Root facts (root_table.md): vehicle UB, tick 1/32 point = $31.25, D8 round-trip wall 1.121 ticks = $35.03,
group rates, O 07:20, C 14:00, F 15:08 CT. Backward window 2010-07-01..2019-05-05, search window
2019-05-06..2024-02-29. Decision times (rates): t1 07:50, t2 10:20, t3 12:50, t4 14:08 CT.

Listing: "the Long-Term U.S. Treasury Bond ("Ultra") futures that the Exchange listed for trading on
January 11, 2010" (CBOT filing to the CFTC, 2010-05-21, p.1; pages/UB/cftc_rul052110cbot001.pdf). UB is
listed throughout both windows.

Tick conversion used below: one UB tick = (1/32)/P of notional, so ticks = bp x P / 312.5, where P is the
futures price in points. **I found no fetchable public source for a UB price level** (one search tried,
nothing usable; cmegroup.com is off limits). Every tick figure is therefore shown at P = 120 / 150 / 180,
a range picked by me as illustrative and marked [unverified].

## 1. Evidence

| id | effect | rule | hold | gross per trade | gross/net | sample | decay evidence | source | grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD -> LH intraday momentum, **UB's own row** | at 14:30 ET (13:30 CT) go long if r_ROD = P(14:30 ET)/P(prior 15:00 ET close) - 1 > 0, short if < 0; exit 15:00 ET (14:00 CT) | 30 min | Paper: beta_ROD = 3.39 (x100), t 4.36 (Newey-West), adj. R2 2.35%, **R2_OOS -3.40%**. Not sized per trade in the paper. My derivation [derived, illustrative]: beta x E\|r_ROD\| = 0.0339 x 0.62% = about 2.1 bp, i.e. 0.81 / 1.01 / 1.21 ticks at P = 120/150/180 (E\|r_ROD\| from sqrt(2/pi) x 12.4%/sqrt(252), the 30-year cash bond's realized volatility in Fleming et al. 2026, Table 1 Panel B: a proxy, not UB's own) | gross | UB, 2010-02-03..2020-05-01, 2,564 days, 1-min bars (Tickdata) | **Out of sample the UB regression loses to the mean: R2_OOS -3.40%** (also -2.24 for r_ONFH and -1.92 for the 3-variable model). UB's in-sample slope is the largest of the US bond futures, but its OOS fit is the worst | Baltussen, Da, Lammers, Martens (JFE 2021) Table B2 Panel B; Table A2 | primary (on-disk copy) |
| E2 | Pre-auction concession, 30-year bond (the tenor UB's K2 auction features use) | short from 180 min before the auction close to 1 min before it (09:00 -> 12:00 CT for a 13:00 ET close) | 180 min | Pre-auction return **-12.075 bp*** (full sample 1991-2024); total V-shape pressure 17.106 bp***; 2015-2024 total pressure 14.224 bp (p<.1), pre/post split not reported per sub-period. -12.075 bp = 4.64 / 5.80 / 6.96 UB ticks at P = 120/150/180 for the full 3-hour window | gross (log midquote changes) | on-the-run **cash** 30-year bond, GovPX/BrokerTec midquotes, 223 30-year auctions, 1991-06-25..2024-07-24 | Weaker after 2014: "the post-2015 period displays markedly weaker yield pressure—less than half the earlier magnitudes"; 30-year yield pressure 2015-2024 is 0.592 bp and **not significant** (Table 2). The 30-year price pressure falls from 25.514*** (2007-2014) to 14.224* (2015-2024); the F-test for S3 = S2 is 1.116 (n.s.) | Fleming, Liu, Nguyen, NY Fed Staff Report 1188 (2026, rev. July 2026), Tables 2, 3, text pp.4, 19-21 | primary (cash bond, not UB futures) |
| E3 | Post-auction reversal, 30-year | long from release+1 min to +180 min (about 12:01 -> 15:01 CT) | 180 min | +5.031 bp, **not significant**; "except for the 30-year bond, where the post-auction adjustment is negligible" | gross | as E2 | n/a (null over the full sample) | same, Table 3, p.19 | primary (null) |
| E4 | FOMC and payroll windows: no auction-style V-shape | same 6-hour window around FOMC and employment releases | - | no V-shape (no size given) | - | as E2 | - | same, p.4 | primary (null, unsized) |
| E5 | Post-FOMC drift in long-term US bond futures | long after expansionary FOMC surprises, short after contractionary ones | days (drift "persists for 15 days") | "up to four times the Sharpe ratio of buy-and-hold"; no per-trade size; the conditioning variable is a policy surprise measure, not a price | unknown | long-term US and German bond futures, transaction data, "post-financial crisis period" (contract and years not visible in the abstract) | none visible | Indriawan, Jiao, Tse (J. Banking & Finance 123, 2021) | **secondary-only** (abstract; full text paywalled) |
| E6 | Leveraged-ETF exposure, the mechanism behind E1 | - | - | UB has the largest LETF market share among the bond futures, 0.028 (X^2 - X), with an ROD -> LH t of 4.4 | - | 2006-06..2020-05 | the bond-market diff-in-diff is "positive but insignificantly so" (Section 4.2) | Baltussen et al. 2021, Fig. 4 panel (b) | primary (mechanism, not a trade) |

Verbatim quotes (location in the saved file):
- E1, Table B2 Panel B (baltussen_etal_2021_jfe.md line 3616): "| UB | 2.46\*\*\* (2.79) | 0.61 | -2.24 | 2.44\*\*\* (2.77) | 3.73\*\*\* (3.30) | 15.06\*\* (2.52) | 3.49 | -1.92\*\* | 3.39\*\*\* (4.36) | 2.35 | -3.40\* |". The caption (line 3537): "Panel B: Newey and West (1986) robust *t*-statistics are in parentheses. Samples range from October 1982 to May 2020. ... Adjusted R<sup>2</sup>, R<sup>2</sup><sub>OOS</sub>, and slope coefficients are multiplied by 100." Table A2 (line 3266): "| Ultra T-bond futures | UB | 2010-02-03 | 2020-05-01 | 2564 | 08:20-15:00 | USA |" (the caption gives U.S. times in Eastern time).
- E2, Table 3 Panel A (nyfed_sr1188.txt, printed p.48): "Pre-auction Return (bps)    −0.733∗∗∗   −1.134∗∗∗      −2.523∗∗∗   −1.204      −3.822∗∗∗    −12.075∗∗∗" (the last column is the 30-year); Panel B: "S3: 2015-2024              0.887∗∗∗    1.216∗∗        4.482∗∗∗    2.509        5.165∗      14.224∗". The window definition (Table 3 caption): "pre-auction (post-auction) returns are computed as the change in the log of the best bid-ask midpoint over the 180-minute window before (after) auction close (release)". Shape (p.4): "Yields rise steadily in the hours leading up to the auction and reverse in the hours following the release of auction results". Decay (p.20): "the post-2015 period displays markedly weaker yield pressure—less than half the earlier magnitudes." Table 2 Panel B (p.47): "S3: 2015-2024                       0.419∗∗∗    0.340∗      0.919∗∗∗    0.417∗       0.593∗       0.592".
- E3 (p.19): "with the two components broadly similar in magnitude except for the 30-year bond, where the post-auction adjustment is negligible." Table 3: "Post-auction Return (bps)    0.603∗∗     1.120∗∗∗       2.107∗∗∗    2.816∗∗∗    6.084∗∗∗      5.031".
- E4 (p.4): "similar analysis of yield movements around Federal Open Market Commit- tee (FOMC) and employment announcements does not produce the same inverted V-shape".
- E5 (IDEAS abstract page): "Using transaction-level data during the post-financial crisis period, we observe a sizable post-announcement drift in government bond markets. A trading strategy of investing in the market after expansionary shocks and shorting the market following contractionary surprises yields up to four times the Sharpe ratio of buy-and-hold investment. ... it persists for 15 days."
- E6 (Fig. 4 panel (b), line 2447): "| UB | 0.028 | 4.4 |"; the caption (line 2477) says the t-statistic is for "regressing its futures' last half-hour return (r<sub>LH</sub>) on the return until 30 minutes before close (r<sub>ROD</sub>)".

Class evidence (cited, not re-read): the bond portfolio's ROD -> LH strategy figures and the rates-class
literature, [shared, see reports/stage_e20_briefs/shared/baltussen_notes.md and shared/rates_class_notes.md];
the Aalto thesis gives pooled bond statements only, no per-market numbers ("especially in bond and currency
futures" not feasible after costs) [shared, see shared/aalto_thesis_notes.md lines 16-20, 67-71].

**What decay and costs say for UB.**
- E1 (ROD -> LH) has the strongest in-sample UB slope among US bond futures but a negative OOS R2 on UB's
  own 10-year sample. The derived gross of about 1 tick is below 1.5 x 1.121 = 1.68 ticks at every price
  in the range.
- E1 also does not fit the E.20 clock for rates. Its signal time is 13:30 CT and its window
  13:30-14:00 CT. t3 = 12:50 (h60 exits at 13:50, h120 at 14:50) and t4 = 14:08 (after C = 14:00) do not
  contain that window. Only the r_ROD feature the prompt already adds would carry it.
- E2 is the one sized effect on UB's tenor. Over its full 3-hour window it is 4.6-7.0 ticks gross, and
  smaller after 2014.
  - On the V2.2 clock the 09:00-12:00 CT window is reachable only in part: t2 = 10:20 with h60 exits at
    11:20, covering 60 of the 180 minutes. If the drift is uniform ("rise steadily"), that is about
    4.0 bp, or 1.55 / 1.93 / 2.32 ticks, which is 1.38 / 1.72 / 2.07 x the D8 wall.
  - With the 2015-2024 total (14.224) split in the full-sample proportion, the hour is about 3.3 bp:
    1.28 / 1.60 / 1.92 ticks, or 1.14 / 1.43 / 1.71 x.
  - t2 with h120 exits at 12:20. That crosses the auction close and the results release, whose jump the
    paper excludes, so the paper's figures do not apply to it.
  - Every figure here comes from cash on-the-run 30-year midquotes, not UB futures. That UB's return in
    bp matches the cash bond's is my assumption [unverified]: UB's cheapest-to-deliver has 25+ years to
    maturity.
  - This effect already enters the library as `k2_auction_mto` / `k2_auction_msince` (K2-aucpre-01,
    K2-aucpost-01).
- E3 (post-auction) is a null for the 30-year bond.
- E5 is unsized, multi-day, and conditioned on a policy-surprise measure that is neither in the 17 roots'
  bars nor in a calendar.

## 2. Feature availability (UB rows)

Calendars and sha256 used:
- 2019-2024 rates group calendar: data/calendars/rates.py, CALENDAR_COVERAGE 2019-05-01..2026-06-19, sha256 449c1529...
- 2010-2019 rates group calendar: data/calendars/hist2010/rates.json, coverage 2010-06-01..2019-05-31. It lists UB, has complete exception lists for every year, 0 unsourced dates, evidence "cme" (CME documents), sha256 099ac84e...
- Frozen release calendar: reports/stage_e2b_release_calendar.json, 2019-05-01..2026-06-21, sha256 839f2437...
- EC-AUC 2010-2019: reports/stage_e16_calendars/ec_auc_2010_2019.json, 2010-01-01..2019-06-30 from FiscalData, sha256 e3b5f452...
- 2019-2024 auction announcement dates: reports/stage_e16_calendars/ec_auc_announcements_2019_2024.json, sha256 78e68a58...
- 2010-2019 FOMC: reports/stage_e14_cal_releases.json, 2010-06-01..2019-05-31, sha256 9a051211...
- K2 member literals: strategy/members/k2/_releases.py and _month_end.py.

| feature | legs | calendars / literals | 2010-2019 (UB window 2010-07-01..2019-05-05) | 2019-2024 | basis |
|---|---|---|---|---|---|
| `cp1_ret` | UB | rates calendar (O 07:20); first bar = the exact 17:00 CT bar of d-1 (ports.py `_first_bar`, k2/cp1.py:47 GLOBEX_OPEN_CT) | **partial: 2011-10-03..2019-05-05 only** | yes | hist2010/rates.json session R1 (2010-06-01..2011-09-30): Globex opened 17:30 CT ("SUN - FRI: 5:30 p.m. - 4:00 p.m."), so no 17:00 CT bar exists and the frozen definition is missing for 2010-07-01..2011-09-30. R2 from 2011-10-03 (CME Globex notice 2011-09-19): 17:00 CT. cp1 is a pooled, always-applicable signal, so "missing for data reasons" would drop those UB rows (V2.3). The same applies to every rates root (ZT, ZF, ZN, ZB) |
| `cp2_range`, `cp2_brk` | UB | rates calendar O 07:20, C 14:00 | yes | yes | day_session_ct 07:20-14:00 in both hist2010 eras and in rates.py |
| `cp3_clv` | UB | rates calendar (prior port-complete day) | yes | yes | same |
| `k2_auction_mto`, `k2_auction_msince` | UB | 30Y TREASURY_AUCTIONS (AUCTION_TENOR UB = "30Y"; T_a = closing_time_comp ET - 1 h in CT) | yes (calendar exists; no member literal table yet) | yes | 2019-2024: k2/_releases.py, 58 30Y auctions 2019-05-09..2024-02-08, all T_a 12:00 CT. 2010-2019: EC-AUC, 106 30Y rows 2010-07-14..2019-04-11 inside UB's window (2010: 6, 2011-2018: 12 each, 2019: 4), 105 at 13:00 ET and 1 at 11:30 ET (2012-09-13). The overlap 2019-05..06 matches the frozen rows exactly except `source` (E.16). Announcement 5-8 days before every 30Y row, so E.16's F-04 rule (announced on or before t-3) holds for all 106. Reopenings carry original term 30Y, as in the frozen convention. With t4, `k2_auction_msince` also applies at 14:08 |
| `k2_fomc_mto` | UB | FOMC_STATEMENT_DATES = FOMC rows whose instant is 13:00 CT; anchor fixed at 13:00 CT (k2.py FOMC_MIN) | **partial: 2013-03-20..2019-05-01 (50 statements at 14:00 ET)** | yes | E.14 FOMC rows in 2010-06..2019-05: 72. At 14:00 ET: 2013 (7), 2014-2018 (8 each), 2019 (3). Not at 13:00 CT: 14 at 14:15 ET (13:15 CT, 2010-06-23..2013-01-30, time inferred from the Fed's 2011-03-24 rule) and 8 press-conference statements at 12:20-12:35 ET (11:20-11:35 CT, 2011-04..2012-12). Under the member's 13:00 CT rule those 22 dates are not events, and on the 8 early ones the statement falls before t3 = 12:50 |
| `k2_fomc_msince` (left out at E.11, reading SC-9) | UB | as above | as `k2_fomc_mto` | yes | **Fact for the lead:** SC-9 left it out because 13:00 CT is after the last decision time, 12:50. E.20's t4 = 14:08 CT is after 13:00, so this side is reachable at t4 |
| `k2_monthend_msince` | UB | N-1 and N of each month from the rates calendar; anchor 07:20 | yes (derivable; the member table covers 2019-05.. only) | yes | 2019-2024: k2/_month_end.py, 58 months 2019-05..2024-02. 2010-2019: hist2010/rates.json gives every trade date (2,324 trade dates, 25 full closures, 97 early halts, 0 unsourced), so N-1 and N follow by the same rule. Early-halt N or N-1 are dropped at run time by the member (C4) |
| `k2_predrift_move` | ZN, ZB | ISM_SERVICES_DATES | n/a on UB rows | n/a on UB rows | k2.py: EXPOSURES = ("ZN", "ZB"); not applicable on UB |
| `g01`-`g03` (30/60/120-min returns), `g04_ret_day`, `g07_range`, `g08_prev_ret` | UB | rates calendar; sigma_X,d | yes | yes | calendars cover both windows. Warm-up for sigma_X,d at the window start depends on the bar start (E.17's ext2010h purchase from 2010-07), so the first rows are a data question, not a calendar one |
| `g05_gap` | UB | rates calendar (prior date's C-1 bar; not applicable after an early-halt date, SG-4) | yes | yes | early halts listed in both calendars |
| `g06_rv60`, `g09_vol_state`, `g10_logvol30` | UB | rates calendar; 20- and 120-date lookbacks | yes (after warm-up) | yes | the 120-date lookback of G9 needs about 6 months of bars before the first row (data, undetermined from calendars) |
| `g11_t_index`, `g12_dow` | none | clock | yes | yes | no input (E.20 adds index 4 for t4) |
| `g13_min_to_rel`, `g14_min_since_rel`, `g15_rel_day` | UB | UB's D8 list = FOMC, NFP, TREASURY_AUCTION (all nominal tenors: 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y) | **partial / undetermined: auctions yes, FOMC yes, NFP see RTY** | yes | Frozen file: UB appears in FOMC (57 rows), NFP (85) and TREASURY_AUCTION (587) only, not CPI or PPI. 2010-2019: auctions in EC-AUC (all nominal tenors, 2010-01..2019-06; no 20Y was auctioned then, E.16); FOMC in E.14 (instants as released, 14 times inferred); NFP [shared, see shared/macro_calendars.md]. The frozen ReleaseCalendar loads only the 2019+ file, so a 2010-2019 merge is engineering work |
| `g16_month_end` | UB | rates group calendar trade dates | yes | yes | hist2010/rates.json and rates.py |
| `g17_nq`, `g17_6e`, `g17_cl`, `g17_gc`, `g17_zc` | NQ, 6E, CL, GC, ZC | none (lead bars) | [shared] | [shared] | lead listings are audited by those roots' readers (product_NQ/6E/CL/GC/ZC.md) |
| `g17_mbt` | MBT | none | no (not listed) | partial (from its 2021 listing) | MBT is outside the 17 roots (brief section 7) |
| `g17_mes` | MES | none | no (listed 2019) | yes | MES is outside the 17 roots (brief section 7) |
| `g17_zn` | ZN | none | n/a on UB rows | n/a on UB rows | generic.py `_lead`: the row's own cluster lead (K2 -> ZN) is not applicable |
| `k9_anncday` | - | EC-K9 | n/a on UB rows | n/a on UB rows | applies on MNQ, M2K, MYM only (V2.3) |

## 3. Proposed features

**None.** Reasons:
- The one sized UB-tenor effect, the 30-year pre-auction concession (E2), is already in the library as
  `k2_auction_mto` / `k2_auction_msince`. Proposing it again would duplicate a member variable.
- ROD -> LH on UB (E1) has negative OOS R2. Its derived gross is under 1.5x the D8 wall, its window
  (13:30-14:00 CT) contains no decision time, and the prompt already adds r_ROD.
- Post-FOMC drift (E5) is secondary-only and unsized, and it needs a policy-surprise input that is not
  available from the 17 roots' bars or a calendar.
- The post-auction reversal (E3) and the FOMC/payroll windows (E4) are nulls for the 30-year bond.

Two facts the lead may want, which are not proposals:
- (a) `k2_fomc_msince`, the FOMC member's "minutes since" side, becomes reachable at t4 = 14:08 CT. The
  same timing argument applies to K5-fomc-01's FOMC 5-minute move (known 13:05 CT), which E.11 excluded
  only because 13:05 was after 12:50. That is a GC-row matter, noted here because the cause is the same.
- (b) On a 30Y auction day, t2 with h120 exits at 12:20 CT, after the 12:00 CT auction close and the
  results release.

## 4. NQ only

n/a.

## 5. Fetch log, terms read, budget notices

| URL | UTC | sha256 | path (reports/stage_e20_briefs/pages/UB/) | status |
|---|---|---|---|---|
| https://www.newyorkfed.org/robots.txt | 2026-10-11T17:37:05Z | 0102c8c4...c51e | newyorkfed_robots.txt | ok |
| https://www.newyorkfed.org/terms-of-use | 2026-10-11T17:37:12Z | - | (deleted: a "Page Not Found" page) | ok (wrong URL) |
| https://www.newyorkfed.org/privacy/termsofuse | 2026-10-11T17:37:28Z | 3196c301...8cc8e | newyorkfed_terms.html (+ .txt a3eca218...030f) | ok |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188.pdf | 2026-10-11T17:37:42Z | 93f9b196...095b | nyfed_sr1188.pdf (+ .txt 0103fe18...a7d7) | ok |
| https://ideas.repec.org/robots.txt | 2026-10-11T17:39:1xZ | 4620fbdb...1d46 | repec_robots.txt | ok |
| https://ideas.repec.org/a/eee/jbfina/v123y2021ics0378426620302880.html | 2026-10-11T17:39:19Z | b931c295...d768 | ideas_indriawan_jiao_tse_2021.html (+ .txt f220394f...3464) | ok (abstract only) |
| https://em.seu.edu.cn/robots.txt | 2026-10-11T17:39:4xZ | - | not kept | 404 (no robots file) |
| https://em.seu.edu.cn/2021/1101/c29365a388728/page.htm | 2026-10-11T17:39:41Z | 0906a81f...10c6 | seu_tse_lecture.html (+ .txt cdb56b3f...e467) | ok (seminar abstract, secondary) |
| https://cftc.gov/stellent/groups/public/@rulesandproducts/documents/ifdocs/rul052110cbot001.pdf | 2026-10-11T17:40:07Z | 980d6205...5b88 | cftc_rul052110cbot001.pdf (+ .txt d891db1a...e6eb) | ok |
| https://faculty.fordham.edu/rchen/JFI-Chen-Leisikow.pdf (and /robots.txt) | 2026-10-11T17:40:20Z | - | not kept | 404 |
| https://works.bepress.com/yiuman-tse/141 (WebFetch) | 2026-10-11T17:38Z | - | - | redirect to digitalcommons.elsevier.com, not followed |
| On-disk files read (no fetch): reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md | - | 18cb436e...0465 | - | grep only |

Full sha256 values are in product_UB.json.

Terms read:
- newyorkfed.org: Terms of Use, last updated 6/9/2023. "The New York Fed grants you a non-exclusive license, subject to the Terms, to use, copy, and distribute Content for your personal or business purposes." Prohibited uses cover illegal use and disrupting the site; there is no ban on automated access. robots.txt disallows only three paths. Ruling: allowed (one PDF fetched).
- ideas.repec.org: robots.txt disallows only /cgi-bin/ for all agents. I did not look for a terms page. One page fetched.
- em.seu.edu.cn: no robots.txt (404) and no terms page found. One page fetched.
- cftc.gov: reused E.14's reading (reports/stage_e14_briefs/pages/terms_checks.md line 8): "Government information at the CFTC website is in the public domain." Allowed for single filings. One filing fetched.
- faculty.fordham.edu: 404, nothing fetched.

Budget: 12 WebSearch calls (cap about 50) and 1 WebFetch. No over-budget notice, no Firecrawl use, no throttling.

## 6. Unfinished and unverified

- **No public UB price level was sourced.** Tick conversions use an illustrative P = 120/150/180 [unverified].
- E1's per-trade gross is my own derivation from the paper's slope and a proxy volatility (the cash 30-year
  bond's 12.4% annualized realized volatility on pre-auction days, SR1188 Table 1). It is not a published
  figure.
- E2 is measured on cash on-the-run 30-year bonds, not UB futures. That UB's return in bp matches the cash
  bond's is my assumption [unverified]. The per-hour share assumes a uniform drift across the 3-hour window
  (the paper's words are "rise steadily"; I did not read Figure 2's values). The 2015-2024 pre/post split
  is not reported in Table 3 and was not looked for in the online appendix.
- E5 (Indriawan, Jiao, Tse 2021): the full text is paywalled; only the abstract and a seminar abstract were
  read. The contract (ZB or UB), the sample years and any intraday component are unknown.
- Leads not fetched because they belong to other readers or are not UB-specific: Robeco's March 2025 quant
  note on 10-year futures around auctions (search snippet: "about 6 bp" before the auction) and Hartley and
  Schwarz, "Predictable End-of-Month Treasury Returns" (2-, 5- and 10-year per a CXO summary, daily data).
  Both are rates-class [shared, see shared/rates_class_notes.md]. Both are [unverified] here.
- `g13`-`g15`: whether NFP 2010-2019 is covered is deferred to the RTY reader (shared/macro_calendars.md).
- `g17_*` lead listings are deferred to the lead roots' readers.
- No UB-specific intraday study since 2015 other than Baltussen et al.'s UB rows was found. The searches
  ("Ultra T-bond" intraday; Ultra price discovery; 30-year futures auction intraday) returned only pricing
  papers on Ultra's delivery option and market-data pages. That is a gap in the search, not evidence that
  no such study exists.
