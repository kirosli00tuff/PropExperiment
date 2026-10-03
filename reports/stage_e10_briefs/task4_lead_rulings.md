# Stage E.10 Task 4: the lead's rulings on the research logs (input to CatalogWriter-OpusXHigh)

Lead, 2026-10-02 23:00 PDT. Inputs: the four research logs (88 sources; every topic stopped on
saturation; Semantic Scholar was unusable because the .env key holds one character, so OpenAlex and
the web carried the search), reports/stage_e10_design_target.md (sha256 ce798814..., fixed before
any source was read) and reports/stage_e10_search_plan.md. No Stage E result was read for any ruling
below.

Duplicate resolved: K9C-006 and K9R-001 are the same paper (Hu, Pan, Wang, Zhu, JFE 2022 / NBER
w25817). The catalog cites it as K9R-001 with K9C-006 noted.

## Admitted members (three; equity index only; 9 trials)

### M1. K9-vixspike-01: uncertainty premium after an unscheduled VIX spike (long equity index next trade date)
- Source: K9R-001 (P-K9R-001-b, -c, -d, -e, -f, -h); context K9R-002, K9R-003. Conflicts to quote:
  P-K9R-001-f (weaker 1986-2018), K9R-008, K9R-014.
- Condition: the source's heightened-VIX definition on a non-announcement day (writer: extract the exact
  definition from the saved paper: the ΔVIX measure, the role of η, the cutoff unit (VIX points), and how
  "non-announcement day" is defined, i.e. which releases). **Cutoff = 1.0 VIX points (η = 0)** by design
  rule (b)1: the source's 1.0 cutoff gives 39.7 days a year (about 47 in 299 dates), and its 1.5 cutoff
  gives 24.6 (about 29, below the 40-trip expectation). The choice follows the frequency rule, not a result.
- Decision: VIX official close of day t (CBOE daily close). Entry: the first bar of trade date t+1 (17:00 CT
  reopen), market BUY q_c. Exit: market intent on the first bar at or after C_X - 2 min (14:58 CT), D-exit
  (the source measures close to close). Hold about 22 h. Weekly cap D-wk applies.
- Exposures: Nasdaq-100 (MNQ), Russell 2000 (M2K), Dow (MYM). S&P 500 evidence transferred; the S&P is not
  a traded exposure (D1.5). Signal variable: VIX for all three (the source's variable; VXN/RVX/VXD are an
  untested transfer and are not used).
- Rulings on exclusions: **X10, admissible.** The condition reads an implied-volatility change, not the
  sign or size of the price move. The mechanism is the source's model prediction (P-K9R-001-h: uncertainty
  resolves and earns a premium), not overreaction. The risk that the gain is a reversal of the spike-day
  fall is stated in the entry's falsification section (K9R-014, K9R-012). **X14, admissible.** VIX
  measures the uncertainty state of the US equity market whose premium the member collects. It is not a
  price lead from another market. Precedent: K1-vxnband-01 conditioned an equity member on VXN inside K1.
  The reviewer may challenge both.
- Data item: CBOE VIX daily close history (free; availability at the official close, after 15:15 CT).
- Source window 1994-09..2018-05 (and 1986-2018): no overlap with the confirmation window (S_X..2024-02-29),
  holdout-2 or the research window. Label: not source-overlap (writer verifies the dates).

### M2. K9-vixback-01: VIX-futures backwardation state (long equity index next trade date)
- Source: K9R-004 (P-K9R-004-a, -b, -c, -d). Conflict: K9R-005 (calm-after-the-storm, low-vol emphasis).
- Condition: VIX futures term-structure slope (writer: extract the paper's exact slope definition and the
  contracts it uses) at or below the 20th percentile of the trailing 250 completed trade dates (D-pct). The
  source puts the signal in "D1-D4, which correspond to 5-20 percentiles" (P-K9R-004-d), so the bottom-20%
  cut is sourced, and the trailing window is the D-pct design rule. About 20% of dates by construction,
  about 60 in 299 before the weekly cap.
- Decision: slope from day t's settlement values. Entry: first bar of trade date t+1, BUY q_c. Exit: C_X -
  2 min (the source's K = 1 day is close to close). Weekly cap applies.
- Exposures: MNQ, M2K, MYM (S&P evidence transferred).
- Rulings: same X10 and X14 readings as M1. Distinct from M1: a curve-shape state (persistent fear priced at
  the front), not a one-day spike. The two conditions overlap on some dates; the overlap is reported, not
  removed (separate trials, separate sources).
- Data item: CBOE CFE VX futures daily settlements, front and second month (free history; a new external
  series for the program, flagged for E.11/E.12).
- Source window 2010-01-04..2017-12-29: not source-overlap.

### M3. K9-anncday-01: macro-announcement-day premium (long equity index over the announcement trade date)
- Sources: K9C-003 (Ai, Bansal, Guo 2023; P-K9C-003-a, -b, -c, -d, -e) for the date set and the recent
  evidence; K9C-001 (Savor-Wilson) and K9C-002 as support. Conflicts to quote: K9C-004 (day-of-month
  confound, P-K9C-004-b, -c), K9C-007 (pre-FOMC drift gone after 2015), P-K9C-003-e (FOMC premium low
  2016-2019).
- Date set: K9C-003's union (FOMC, nonfarm payroll, GDP first and last estimates, ISM manufacturing, the
  combined inflation announcement as the source defines it: writer extracts the exact list and the
  "earlier of CPI/PPI" rule). About 44 a year, about 52 in 299 dates (writer: show the calendar arithmetic
  from public release calendars, and mark counts not fetched from an official calendar as [unverified]).
- Entry: first bar of the announcement trade date (17:00 CT the prior evening), BUY q_c. Exit: C_X - 2 min.
  The source measures close to close. The full-session hold contains the release.
- Exposures: MNQ, M2K, MYM.
- Rulings: **X4, admissible.** No pre-release move is read; the trade is unconditional on price.
  **X6, admissible.** No post-FOMC move is read, and FOMC is one date type among six. **X12, admissible
  with a flag.** The date set is keyed to release calendars, not the day of the month. K9C-004's
  day-of-month confound is the main falsification risk and is quoted in the entry. D9.12 (CPI window)
  does not bite, because the entry fill is at 17:00 CT the evening before.
- Source window: K9C-003 runs to 2023-08, which overlaps the confirmation window. **Label:
  source-overlap.** An edge cannot be claimed without a registered holdout read (NULL_CRITERIA_E
  section 3).

## Excluded (each goes in the catalog's "Excluded members" table with its reason)

| Candidate | Sources | Reason (check failed) |
|---|---|---|
| Pre-announcement overnight long (reopen to release - 5 min, NFP/ISM/GDP) | K9R-001 / K9C-006 | Variant of M3: same mechanism, a subset of the same dates, the hold window as a parameter (no-grids rule). The 2012-2018 row is weak (P-K9C-006-f). Offered to the user as M3's alternative window. |
| Long equity after a large prior-day shock (moderate shocks) | K9R-019 | Rule 1: abstract only, threshold and sample unknown. Conflict K9R-014 (ES daily autocorrelation about zero). |
| Continue the prior day in calm volatility states | K9R-012, K9R-013 | Evidence: older cash-index data, contradicted in S&P futures after 1993 (K9R-014). Also X3-adjacent. |
| MCL continuation after a 2-SD day | K9R-017 | Frequency: about 15 a year, under the 10% floor. Data from a non-exchange feed, exits fitted. |
| Range compression or inside-day direction | R3 | No academic source gives a direction (R3 saturation). A compression-gated breakout is X2. |
| European-open overnight drift (closing-flow or late-VIX conditioned) | K9O-001, K9O-003 | Non-survivor: the authors report it near zero since 2021 in ES, NQ and YM (K9O-002). The flow version needs signed volume, which the bars lack. |
| 12-month TSMOM held overnight only, in a trend state | K9O-004, K9O-005, K9O-009 | Shape: the trend state persists for weeks, so the weekly cap would pick days arbitrarily, and the Bear state yields about 20 capped trips. Kept for V20's ML route v2 as a feature. |
| 6E time-of-day pattern; MGC Asian-session premium | K9O-010/011; K9O-013/014 | Shape: no sourced condition (every day); X9-adjacent (fix-driven). |
| Bitcoin Monday long | K9C-014, K9C-015 | Evidence: 2013-2017 only, with per-year sign reversals (P-K9C-014-c). No later evidence. |
| Futures weekend effect | K9C-016 | Rule 1: abstract only, products unknown. Equity weekend effect gone (K9C-017, K9C-018). |
| Pre-FOMC drift; FOMC-day FX; FOMC-cycle weeks; pre-holiday; options-expiration week; Halloween | K9C-005/007/010/008/009/020/021/022 | Frequency below the floor and/or non-survivor; option expiry is X13-adjacent. |
| Treasury announcement-day premium | K9C-001 (bonds), K9C-011 | Cost wall: per-day premium below M_X; insignificant after 2008. |
| Scarcity-state carry (storage, basis) | K9M-001/002/004/005/007/008 | Cost wall: about 2-8 bp per trade date, below M_X on every commodity exposure. Faster rebalancing lowers returns (P-K9M-003-c). Needs deferred-contract bars. |
| FX carry earned in the US session | K9M-010, K9M-011 | Cost wall (about 1-2.4 bp a day); no rarity condition; X9-adjacent. |
| NG long after an extreme cold forecast | K9M-017 | Evidence is a 5-day NG1/NG2 spread, not an outright session hold. Needs NOAA GEFS forecast history. |
| New-crop corn weather-premium short | K9M-019/021/022 | Cost wall (about 10 bp, about 1.8 ZC ticks vs M_X 4.5). Passive short not attractive (P-K9M-021-c). X8 risk. |
| Calendar-month commodity seasonality | K9M-013, K9M-014 | Evidence: no out-of-sample gain (K9M-014). |

## Instructions for the cost-wall comparison in each entry

Compare the source's documented mean move per trade with M_X and G(f) **without a price level the program
has not frozen**. Use the ratio route: M_X / E|m_1| and G(f) / E|m_1| from reports/stage_e10_design_target.md
(a), against the source's mean move divided by the source's own mean absolute daily move (or 0.798 x its
daily standard deviation when only that is reported). If the source reports neither, state the source's
figure in its own units and mark the comparison [no conversion available]. A reader's round-price
conversion is never used as evidence.

## Totals

3 members, 9 trials (3 exposures each), against the 40-trial budget. Projected program N = 198 + 9 = 207.

---

## Round 2: rulings on CatalogWriter's section 7 (lead, 2026-10-02 23:25 PDT; no Stage E result read)

1. **K9-vixspike-01 filter: keep it.** The paper states its focus on non-announcement days (P-K9R-001-b, -c)
   and titles Table 9 "Predicting Non-Announcement Day Return". That statement outranks the writer's arithmetic
   inference that Table 7's counts are all-day figures. The member therefore expects about 37.8-39.7 trips
   before the cap and 36.7-38.4 after: **below the (b)1 margin of 40 and above the 30-trip floor.** The lead
   does not relax (b)1 after reading the source. The shortfall goes to the user as a decision: keep the member
   with the margin waived (recommended: about 25% above the floor), or cut it. The no-filter reading (47.1 /
   45.1 trips) is recorded as the alternative, and not chosen because it rests on an inference.
2. Cutoff unit: noted, no change.
3. Longer sample below M_X on M2K and MYM: stated in the entry's cost-wall section as a weakness. No change.
4. **Decision time:** CBOE's official VIX close for day t (the 15:15 CT value). Its publication before the
   entry is [unverified] and is verified in E.12. If it is not reliably available before the entry intent
   (17:59 CT, ruling 5), the sourced fallback is the 3:45 pm ET VIX value (C-K9R-001-13). Write both in
   order.
5. **Reopen entries: every K9 entry at a reopen is market intent on the 17:59 CT bar, filling at the 18:00
   CT open**, on weekdays and Sundays alike. This amends D-entry for D9.4 ("reckless trades in gapped
   markets"), following the K8-wkndbtc-01 judgment that the reopen's first minutes are the gapped market
   of D9.4. The reason is a frozen constraint and precedent, not a source or a result. Holds stay above two
   hours (about 21 h).
6.-10. **K9-vixback-01: excluded.** Two reasons. (a) Shape, consistent with the TSMOM ruling: backwardation
   states persist for days or weeks, so the weekly cap picks days arbitrarily, and the capped count is
   anywhere from about 24 to 56. (b) Evidence at the member's horizon: at K = 1 day only D1-D2 (bottom 10%)
   are significant (writer's item 8), and a 10% cut gives about 30 trips before the cap, below the 40-trip
   expectation. Move it to the Excluded table with both reasons and the passage ids. Keep its full
   specification in an appendix ("withdrawn draft") so the user can reinstate it. Note it as a candidate
   feature for V20's ML route v2. Data item notes (seven VX closes plus spot) stay in the appendix.
11. **K9-anncday-01 mapping:** (a) inflation pairing by **reference month** (CPI and PPI for the same reference
    month; the earlier release date of the pair). That gives 14 inflation dates. (b) 2025Q3 GDP: Initial and
    Updated map to first and last, as the writer did. (c) ISM: scheduled dates, [unverified] as actual.
12. Count: 60 dates in the window, 58 after the cap (scaled to 299: 56.8 / 54.9). Replace "about 52".
13. Ratio route: use Savor-Wilson's 0.145, labelled as the support source's own date set; K9C-003's figure
    is [no conversion available].
14. **Early-close dates:** on a CME early-close date the exit is the forced flatten at F (D9.1: 15 minutes
    before the early close), as for the ports. The entry states it. Early-close dates are not excluded.
15. Treasury row: keep the exclusion. State the reasons in order: the bond premium's only full-text
    evidence ends before 2010 (K9C-001's sample); "insignificant after 2008" is abstract only (K9C-011); the
    cost wall is [conversion unverified]. The other three weakened rows keep their independent reasons.
16. HPWZ label: keep "not source-overlap" on the NBER w25817 sample (to May 2018). State that the JFE 2022
    version was not read, and that the label must be re-checked against it in E.11. If its sample runs past
    2019-05-06 the label becomes source-overlap.
17. K9R-006 and K9R-007: read their log entries (grep the regime log) and add them to K9-vixspike-01's
    support or conflicting evidence if they bear on it, with passage ids verified in the saved files. If they
    do not bear on it, say so in one line.

**Totals after round 2: 2 members (K9-vixspike-01, K9-anncday-01), 6 trials, projected N = 204.**
