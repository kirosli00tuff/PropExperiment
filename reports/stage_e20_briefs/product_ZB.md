# Stage E.20 Part A: product reader ZB (30-year Treasury bond futures; vehicle ZB)

Reader: ProductReader-ZB-OpusHigh. Written 2026-10-11, 10:33 to about 10:55 PDT. JSON: `reports/stage_e20_briefs/product_ZB.json`.
Raw pages: `reports/stage_e20_briefs/pages/ZB/`. No data store opened. No E.15/E.17/E.18 or Gate 0 results read.
WebSearch calls used: 11 of about 50. No budget notice was received.

Shared assignment: root-specific evidence only. Rates-class evidence is cited from the ZN reader
(`shared/rates_class_notes.md`, which did not exist at 17:45Z) and the Aalto thesis from `shared/aalto_thesis_notes.md`.
Baltussen et al.'s US 30-year row was taken from the on-disk copy.

**Conversion used throughout.** One ZB tick is 1/32 point, $31.25 on $100,000 face. Notional is P x $1,000, so
ticks = bp x P / 312.5. **P = 140 is an assumption.** No public ZB price was fetched. Values scale linearly with P:
x0.857 at P = 120, x1.143 at P = 160.

Two of the sources measure yields on cash on-the-run bonds. Converting yield bp to ZB price bp uses an **assumed ZB
(CTD) modified duration D = 12, range 11 to 13 [unverified]**. It is inferred from the 15-to-under-25-year deliverable
grade, with the cheapest-to-deliver at the short end. That grade is quoted from the CBOT filing the UB reader saved
(`pages/UB/cftc_rul052110cbot001.pdf`, sha256 980d6205...): "Treasury bonds eligible for physical delivery shall be
limited to those with remaining terms to maturity of at least 15 years, but less than 25 years". It applies from the
March 2011 contract.

The D8 round trip for ZB is 1.122 ticks ($35.06), so the 1.5x hurdle is 1.683 ticks ($52.59).

## 1. Evidence

| id | Effect | Rule | Hold | Gross per trade (bp; ticks at P=140) | Gross/net | Sample | Decay evidence | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Pre-auction price pressure on the 30Y, from its own auction | Short from T_a-180 to T_a-1 min, where T_a is the competitive close (13:00 ET = 12:00 CT). Post leg: long from T_a+0+ to T_a+180 | 180 min | Pre leg: yield +0.634 bp, so 7.61 bp of ZB notional at D 12 = **3.41 ticks** (3.12 to 3.69 for D 11 to 13). If ZB moved like the on-the-run 30Y (-12.075 bp), 5.41 ticks. Post leg not significant | gross | Cash on-the-run 30Y, GovPX/BrokerTec, 1-min, 1991-06..2024-07 | 30Y yield pressure is not significant in 2015-2024 (0.592, ns). It peaked in 2007-2014 (1.448***). Price pressure in 2015-2024 is 14.224* against 17.106*** over the full sample. The sample overlaps the search window (E.0 ruling R-04, SOURCE-OVERLAP) | Fleming, Liu, Nguyen 2026, FRBNY SR 1188, Tables 2-3 | primary |
| E2 | Cross-tenor spillover: 10Y auctions move the 30Y yield more than 30Y auctions do | On 10Y auction days the 30Y yield rises into the close and reverses after the results. Also significant on 5Y days (0.562***) and 7Y days (0.353*) | 180 min | Total 1.294 bp***. The pre/post split is not published. With a pre share of 0.55 (bracket 0.37 to 0.73): 0.712 bp, or 8.54 bp = **3.83 ticks** (derived) | gross | As E1 | No subsample split. The 10Y own-auction effect halves after 2014 (0.593* against 1.192***) | SR 1188, Table 4, p.23 | primary |
| E3 | Post-FOMC yield decline, unconditional, with nulls | Yields fall for about 3 h after the FOMC statement. No systematic change in the 3 h before FOMC or payrolls, and none after payrolls | up to 180 min | 0.5 to 1.5 bp of yield across maturities, which is 6 to 18 bp at D 12 over 3 h. A t4 (14:08 CT) to F (15:08) slice gets about 1/3 if the drift is linear: 0.9 to 2.7 ticks [derived] | gross | Cash on-the-run, FOMC 1997..2024-07 | Not reported | SR 1188, p.25 | primary (the per-maturity figure was not read) |
| E4 | ROD -> LH intraday momentum, US T-bond row | r_LH (13:30-14:00 CT) regressed on r_ROD | 30 min | Slope 2.11 (x100): **0.95 ticks per 1% ROD move** | gross | US futures, 1-min, 1982-10..2020-05 (panel range) | OOS R2 0.22%. The LH window is unreachable at t1-t4 | Baltussen et al. 2021 JFE, Table B2, row US (on-disk copy) | primary |
| E5 | End-of-month Treasury returns: daily, not intraday | Long Treasury futures held only over the last t days of the month | 1 to 6 days, overnight included | 30Y futures, last day: 0.15 (about %) = 15 bp = 6.72 ticks close-to-close. The intraday share is not reported | gross | Treasury futures, daily, 1990-2018 | "smaller ... but they remain significant" in 2015-2018 | Hartley, Schwarz 2019, Rodney White Center WP 17-19, Table 8 | primary (working paper) |
| E6 | Pre-release drift before ISM Services | Prices drift toward the surprise from about T-30. ZB appears only in a robustness check | ~30 min | none for ZB | unknown | ES, ZN; ZB robustness; 2008-2014 | Pre-2015 sample. V34 dropped this effect as unsized | Kurov, Sancetta, Strasser, Wolfe 2019 JFQA, via E.0 log K2-007 | secondary-only |
| E7 | Post-FOMC drift in long-term US bond futures, signed by the surprise | Long after easing surprises, short after tightening surprises. The drift lasts 15 days. No pre-FOMC drift | multi-day | none (abstract only) | unknown | Post-crisis, transaction level | unknown | Indriawan, Jiao, Tse 2021 JBF (UB reader's IDEAS page) | secondary-only |
| E8 | Intraday momentum and reversal 2008-2024 persist but mostly fail after costs, "especially" in bonds | n/a | intraday | none | net | 20 futures | After-cost failure | Aalto thesis 2025 [shared, see shared/aalto_thesis_notes.md] | secondary-only (abstract) |

Verbatim quotes. Each was re-found by script in the saved text after whitespace normalization.

- E1. SR 1188, Table 2, 30-Year column: "Yield Pressure (bps) ... 0.869∗∗∗", "∆Y (pre) ... 0.634∗∗∗", "∆Y (post) ...
  −0.235", "S3: 2015-2024 0.419∗∗∗ 0.340∗ 0.919∗∗∗ 0.417∗ 0.593∗ 0.592".
- E1. Table 3: "Pre-auction Return (bps) −0.733∗∗∗ −1.134∗∗∗ −2.523∗∗∗ −1.204 −3.822∗∗∗ −12.075∗∗∗" and "S3: 2015-2024
  0.887∗∗∗ 1.216∗∗ 4.482∗∗∗ 2.509 5.165∗ 14.224∗".
- E1. p.19: "with the two components broadly similar in magnitude except for the 30-year bond, where the post-auction
  adjustment is negligible."
- E2. Table 4: "10-Year 1.013∗∗∗ 1.076∗∗∗ 1.259∗∗∗ 0.796∗∗∗ 1.192∗∗∗ 1.294∗∗∗" (the last column is the 30-Year
  yield) and "30-Year −0.073 −0.035 0.182 0.326 0.395 0.869∗∗∗".
- E2. p.23: "Auctions of 5-, 7-, and 10-year notes are associated with significant yield pressure across the entire
  curve." and "30-year auctions generate significant yield pressure primarily in the 30-year bond (0.87 bps), with
  negligible effects at shorter maturities."
- E3. p.25: "In the three hours prior to each announcement, yield changes are not systematically different from zero.
  Following employment report releases, yield changes remain largely insignificant. FOMC announcements are followed by
  a significant and persistent decline in yields—on the order of 0.5–1.5 bps—consistent with the previously documented
  post-FOMC drift in bond markets".
- E4. Table B2, Panel B: "US | 1.77*** (3.62) | 0.21 | 0.09*** | 1.81*** (3.71) | 2.59*** (5.03) | 0.88 (0.15) | 0.65
  | -0.43*** | 2.11*** (3.85) | 0.64 | 0.22***". Table 1: "US 30-Year T-bond futures | US | 8:20 - 15:00".
- E5. Table 8: "30-Year 0.15*** 0.21*** 0.27*** 0.27*** 0.33*** 0.31*** 0.03 0.03 0.02 0.09". Notes: "The units are
  (approximate) percentage points per month (not annualized)." Text: "The estimates in the final period, from
  2015-2018 are smaller than most of the other periods, but they remain significant."

**Reading on decay and costs.**

**The only sized, ZB-relevant intraday effect is auction price pressure (E1, E2).** It is measured on cash on-the-run
bonds, not on the futures. Two facts matter for ZB:

- The own-tenor 30Y effect is the weakest after 2014: 30Y yield pressure is not significant in 2015-2024.
- 30-year auctions move mainly the 30Y itself, while 10Y auctions move the whole curve. ZB's CTD (a 15-to-25-year
  bond) therefore probably gets less from its own tenor's auction than the on-the-run 30Y does, and at least as much
  from 10Y auctions.

**The library's existing auction feature (`k2_auction_mto` on ZB, 30Y only) falls short of the hurdle on the clock.**
At t2 = 10:20 CT, 100 minutes before T_a = 12:00 CT:

| Horizon | Full sample, ticks | x D8 | Scaled to 2015-2024, ticks | x D8 |
|---|---|---|---|---|
| h120 (exit 12:20, crosses the results) | about 1.75 | 1.56 | 1.19 | 1.06 |
| h60 | 1.14 | 1.01 | 0.77 | 0.69 |

**The other effects do not fit the clock or the cost wall:**

- **E4 (ROD -> LH).** About 1 tick per 1% ROD move, and its 13:30-14:00 CT window cannot be reached at t1-t4.
- **E3 (post-FOMC).** The decline is unconditional, and it starts at 13:00 CT, after t3. It can be reached only at t4
  (see section 2, `k2_fomc_msince`).
- **E5 (month-end).** Sizable but daily. It supports the existing `k2_monthend_msince`, but no source splits it
  intraday.

**Nulls.** No pre-FOMC drift (E3, E7). No pre-payroll or post-payroll yield change (E3). No post-auction reversal on
the 30Y (E1). Bonds fail after costs in the Aalto abstract (E8).

## 2. Feature availability (ZB rows; ZB's bars are read only by features on ZB's own rows)

Calendars:

- Rates group calendar, 2010-2019: `data/calendars/hist2010/rates.json`, covering 2010-06-01..2019-05-31 (sha256
  099ac84e..., 0 unsourced, verbatim check 253 with 0 failures). Globex opened at 17:30 CT until 2011-09-30 and at
  17:00 CT from 2011-10-03. ZB's day session is 07:20-14:00 in both eras.
- Rates group calendar, 2019-2024: `data/calendars/rates.py`, covering 2019-05-01..2026-06-19 (sha256 449c1529...).
- EC-AUC 2010-2019: `reports/stage_e16_calendars/ec_auc_2010_2019.json` (sha256 e3b5f452...).
- FOMC 2010-2019: `reports/stage_e14_cal_releases.json` (sha256 9a051211...).
- Frozen release calendar: `reports/stage_e2b_release_calendar.json` (sha256 839f2437...).

| Feature | Legs | Calendars | 2010-2019 | 2019-2024 | Dates / basis |
|---|---|---|---|---|---|
| cp1_ret | ZB | rates calendar | **partial** | yes | No 17:00 CT open bar exists 2010-07-01..2011-09-30, because Globex opened at 17:30 CT. The frozen rule (exact 17:00 bar of d-1) gives "missing", which excludes the row. The lead needs to rule on this. Yes from 2011-10-03 |
| cp2_range, cp2_brk, cp3_clv | ZB | rates calendar | yes | yes | Own bars; O 07:20 and C 14:00 in both eras |
| k2_auction_mto / k2_auction_msince | ZB | TREASURY_AUCTIONS 30Y | yes | yes | EC-AUC: 106 30Y auctions in 2010-07-01..2019-05-05 (105 at 13:00 ET, 1 at 11:30 ET), 0.0% unsourced, exact match on the 2019-05/06 overlap. Frozen table: 58 in the window. The 2010-2019 rows are not yet in the member's literal table |
| k2_fomc_mto | ZB | FOMC statements at 13:00 CT | **partial** | yes | E.14 has 71 statements in the window: 50 at 14:00 ET (from 2013-03-20) and 21 at other instants (13 at 14:15 ET with inferred times, 8 at 12:20-12:35 ET). The member's set is "instant = 13:00 CT" (L-15), so the frozen definition covers 2013-03-20 onward only. 37 dates in 2019-2024 |
| k2_fomc_msince (not in the current library) | ZB | as above | partial | yes | SC-9 excluded it because 13:00 CT is after t3. **E.20's t4 = 14:08 makes it reachable.** This is a fact for the lead, not a proposal. Evidence: E3 |
| k2_monthend_msince | ZB | N-1, N from the rates calendar | yes | yes | Derivable 2010-2019 from hist2010/rates.json by the member's rule. **The 2010-2019 literal table has not been generated.** 58 months in 2019-2024 |
| k2_predrift_move | ZB (and ZN) | ISM_SERVICES_DATES (09:00 CT) | **no** | yes | No ISM Services calendar for 2010-2019 was found on disk. E.16's review (line 232) lists ISM_SERVICES among the types with no 2010-2019 rows. 57 dates in 2019-2024. [shared: RTY's macro_calendars.md, if it covers ISM Services] |
| g01-g04, g06, g07, g10 | ZB | rates calendar (sessions) | yes | yes | Own bars |
| g05_gap | ZB | rates calendar (previous date, C 14:00, early halts) | yes | yes | Not applicable after an early halt. hist2010 lists 97 early halts, all sourced |
| g08_prev_ret, g09_vol_state | ZB | rates calendar | yes | yes | g09 needs 120 dates of warm-up before the first backward row. Whether bars exist before 2010-07 is a data question I did not decide |
| g11_t_index, g12_dow | none | clock | yes | yes | t4 adds a 4th index value |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | none | ZB's D8 list: TREASURY_AUCTION (all nominal tenors), ISM_SERVICES, NFP, FOMC | **partial** | yes | 2019-2024: 545 rows (auctions 394, ISM Services 57, NFP 57, FOMC 37). 2010-2019: auctions yes (EC-AUC: 2Y 97, 3Y 106, 5Y 107, 7Y 114, 10Y 106, 30Y 106; no 20Y existed then); FOMC yes (71); **NFP and ISM Services not found**. CPI is not on ZB's list. [shared, see shared/macro_calendars.md (RTY)] |
| g16_month_end | none | rates calendar | yes | yes | From the calendar |
| g17_nq, g17_6e, g17_cl, g17_gc, g17_zc | lead | lead's calendar | yes | yes | All listed before 2010; each lead's reader audits it [shared, see product_<LEAD>.md] |
| g17_zn | ZN | none | no | no | Own-cluster lead: not applicable on ZB rows by construction (SG-2) |
| g17_mbt | MBT | none | no | partial | Leg outside the 17 roots; listed 2021-05 |
| g17_mes | MES | none | no | partial | Leg outside the 17 roots; listed 2019-05 |

No feature on another root's rows reads ZB. The G17 K2 lead is ZN, and no K8 leg is ZB. `k9_anncday` applies only to
MNQ, M2K and MYM rows.

## 3. Proposed features

**P1 `k2_auc10_mto_zb`: minutes to the 10-year note auction close, on ZB rows (does not clear 1.5x on post-2015
scaling).**

- **Source.** SR 1188, Table 4: "10-Year 1.013∗∗∗ 1.076∗∗∗ 1.259∗∗∗ 0.796∗∗∗ 1.192∗∗∗ 1.294∗∗∗" (the last value is
  the 30Y). p.23: "Auctions of 5-, 7-, and 10-year notes are associated with significant yield pressure across the
  entire curve."
- **Formula.** On a ZB row at time t of date d: if d is a 10Y auction date (tenor "10Y" in TREASURY_AUCTIONS or EC-AUC)
  and t < T_a (CT, normally 12:00), the value is (T_a - t) in minutes with flag 1. Otherwise the value is 0 with
  flag 0. This is the same `fixed_clock` as `k2_auction_mto`, with the tenor set to 10Y for ZB. An msince side for
  t3/t4 is optional.
- **Times, horizons, legs, calendars.** t1 and t2; h60, h120 and F; leg ZB. Calendars: 10Y rows of EC-AUC (106 in the
  backward window) and of the frozen calendar (59 in the search window); the rates calendar.
- **Availability.** Both windows: yes.
- **Expected gross and ratio (derived).** The 1.294 bp total is split with a 0.55 pre share (bracket 0.37 to 0.73),
  giving 0.712 bp over 09:00-12:00 CT.
  - Short at t2 with h120: 100/180 of the pre leg minus 20/180 of the post reversal = 0.331 bp. At D 12 that is
    3.97 bp, or **1.78 ticks** on the 1991-2024 average (bracket 0.94 to 2.61), which is 1.58x D8.
  - Scaled by the 10Y own-auction ratio of 2015-2024 to full sample (0.497): **0.88 ticks = 0.79x D8. Does not clear
    1.5x.**
  - h60: 1.28 ticks full sample, 0.63 post-2015.
- **Caveats.**
  - Duration, price level, pre share and the linear profile within the window are all assumptions.
  - The source sample (1991-2024) overlaps the search window.
  - The source is on cash Treasuries, not futures.
- **Why list it anyway.** The library's only auction feature on ZB keys on 30Y auctions. The paper's spillover table
  says the 10Y auction is the larger driver of the 30Y yield, and the 30Y auction barely moves anything shorter. That
  is a published fact about ZB's own exposure. The lead decides.

No second proposal. Two candidates were considered and set aside:

- A post-FOMC drift signed by ZB's own 13:00-14:07 move. The published rule signs by a policy-surprise measure the 17
  roots cannot supply, and the paper is abstract-only.
- An unconditional post-FOMC long at t4. That is the existing K2-fomcpost family (`k2_fomc_msince`), not a new
  feature.

## 4. NQ only

n/a

## 5. Fetch log, terms read, budget notices

| URL | UTC | sha256 | Path | Status |
|---|---|---|---|---|
| https://www.newyorkfed.org/robots.txt | 2026-10-11T17:36:50Z | 0102c8c4...51cb5551e | pages/ZB/www.newyorkfed.org_robots.txt | ok |
| https://rodneywhitecenter.wharton.upenn.edu/robots.txt | 2026-10-11T17:36:53Z | 975ced5a...d20865 | pages/ZB/rodneywhitecenter.wharton.upenn.edu_robots.txt | ok |
| https://www.newyorkfed.org/privacy/termsofuse | 2026-10-11T17:37:10Z | 8bc87341...b2a8883 | pages/ZB/nyfed_termsofuse.html (.txt) | ok |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188.pdf | 2026-10-11T17:37:21Z | 93f9b196946d3c41e9670052eb3d8d0fce30fb892f8f1553c1b469c05193095b | pages/ZB/nyfed_sr1188.pdf (.txt) | ok |
| https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2019/12/17-19.Schwarz.pdf | 2026-10-11T17:37:24Z | 56403762378f606f595dcce11afcf1f1eaccf8810237c58999f653a230a32809 | pages/ZB/hartley_schwarz_2019_rwc.pdf (.txt) | ok |
| https://www.quantitativebrokers.com/robots.txt | 2026-10-11T17:40:01Z | fd140a31...dc25aa | pages/ZB/quantitativebrokers_robots.txt | ok |
| https://www.quantitativebrokers.com/whitepapers/2024-01 | 2026-10-11T17:40:28Z | c2420714...f680b0 | pages/ZB/qb_2024-01.html (.txt) | gated (summary only; "Request the full whitepaper"); not used |
| https://www.upenn.edu/about/disclaimer | 2026-10-11T17:44:18Z | none | none | 403 (curl) |
| https://www.upenn.edu/about/disclaimer (scrapling get) | 2026-10-11T17:44:24Z | e2e4a4ad...f8b7 | pages/ZB/upenn_disclaimer.md | ok |

Full hashes are in the JSON.

Terms read:

- **newyorkfed.org.** Terms (read 17:37:10Z, before the SR 1188 fetch): "The New York Fed grants you a non-exclusive
  license, subject to the Terms, to use, copy, and distribute Content for your personal or business purposes."
  robots.txt disallows only /PrincipleInterest/ and two seminar-calendar PDFs.
- **rodneywhitecenter.wharton.upenn.edu.** robots.txt is "User-agent: * / Disallow:" (read before the fetch). No terms
  page was located before the fetch. The Penn disclaimer, read after the fetch, states no restriction on access. The
  PDF is a public working paper.
- **quantitativebrokers.com.** robots.txt groups the AI agents with "*", and /whitepapers/ is not disallowed. The full
  text is gated, so the page was not used.

Re-used, not fetched:

- From other readers or earlier stages: the CBOT 2010 filing and the Indriawan et al. IDEAS page (both UB reader,
  pages/UB/), the Baltussen copy (E.13), the Kurov et al. passage (E.0 log), and the Aalto notes (shared/).

Budget notices: none. WebSearch calls: 11. Firecrawl was not used.

## 6. Unfinished and unverified items

- No study on ZB futures (as opposed to cash 30Y) around auctions was found in 11 searches. The sizes in E1 and E2
  carry three assumptions: the duration (D = 12, range 11 to 13), the price (P = 140), and a profile linear within the
  window [unverified].
- I did not read Figure 2 of SR 1188 (minute profile) or Figure A4 (FOMC yields by maturity), because they are figures,
  not text.
- Kurov et al. (2019) and Indriawan, Jiao, Tse (2021) were not fetched in full (a class item, and a paywall). They are
  graded secondary-only.
- 2010-2019 calendars not on disk:
  - NFP and ISM Services. These decide `g13`-`g15` and `k2_predrift_move`. RTY's `shared/macro_calendars.md` was not
    yet written when I checked (about 17:45Z).
  - The month-end literal table and the 30Y/10Y auction literal tables for 2010-2019. These are derivable from files
    already on disk but have not been generated.
- `cp1_ret` 2010-07..2011-09 (17:30 CT Globex open): the frozen rule makes every such row missing. The reading is
  reserved for the lead.
- Rates-class notes (`shared/rates_class_notes.md`) did not exist when I checked, so class-level citations to ZN are by
  path only.
