# Stage E.16 pre-registration, common part: H1 to H5 (base-rule batch, Part A)

Status: FROZEN by the Stage E.16 freeze (reports/stage_e16_freeze.json, commit "E.16 base-rule freeze"); NOT
REGISTERED. This file and reports/stage_e16_prereg_H1.md to _H5.md together are the pre-registration. Written
2026-10-09 before any 2010-2019 byte of any of the 27 products exists on the machine and before Stage E.17's C1
reads any; no market-data bar was read to write it (Stage E.16 read none). Stage E.17 registers H1 to H5 together
(N + 5) and runs each once, in the order of reports/stage_e16_handoff.md.

## 1. Sources of the definitions (each hashed in the freeze manifest)

- The stage prompt docs/prompts/STAGE_E.16.md ("THE FIVE HYPOTHESES", "Windows", "Pass bar", "Trial count",
  "Priors"), which fixes the five rules; the freeze may only tighten them, except where a user ruling says so.
- The lead's operational spec reports/stage_e16_briefs/lead_spec.md (sections U and 0 to 6), which IS the common
  definition of prices and clock (section 0), costs (1), exclusions and references, rolls, the store boundary and
  windows (2), risk scaling (3), the five tests (4), statistics and the pass bar (5) and run discipline (6). It is
  quoted per test in each H file and incorporated here whole.
- The lead's rulings reports/stage_e16_rulings.md (settlement grades R-S1 to R-S6, the overlap rulings, the review
  rulings) and the settlement table's lead_grade fields.

## 2. User-side rulings, 2026-10-09 (relayed from the planning chat; binding)

- U1: E.17's harness is not caps-only for the whole stage. E.17 does C1 first under a harness whose only diff
  from v10 is the acct-2 cap and the session caps (C1 freeze section 11), completes C1's evaluation, and only then
  writes a further harness adding the purchase plan for the remaining extension roots.
- U2: each product's window starts at the first priced month after its last unpriced gap before 2019-05 in
  reports/stage_e12_quotes_ext2010.json, plus warm-up; each product's start is recorded here, before any bar exists.
- U3a: the base case is the frozen D8 cost with no extra tick (D8 is a measured round trip); D8 plus one extra tick
  per side is the stress case, reported for every test and a must-survive condition for any later holdout-2
  registration.
- U3b: H2's year stability counts years with at least 6 monthly units; 10 units for the other tests.

## 3. Windows per product (U2; reports/stage_e16_windows.json, script reports/stage_e16_briefs/derive_windows.py)

| Products | First priced month after the last unpriced gap | Window (first trade date on or after) | Listing rule R-S4 |
|---|---|---|---|
| NQ YM ZT ZF ZN ZB UB 6E 6A 6B 6C 6J 6S 6N CL NG GC HG ZC ZW ZS ZM ZL LE (24) | 2010-07 | 2010-07-01..2024-02-29 | listed throughout |
| RTY | 2017-06 | 2017-06-01..2024-02-29 | no unit before listing 2017-07-10 |
| TN | 2016-01 (2012-06..2015-12 unpriced) | 2016-01-04..2024-02-29 | no unit before listing 2016-01-11 |
| HE | 2017-07 (2017-06 unpriced) | 2017-07-03..2024-02-29 | listed throughout |

Each test's warm-up (20 units per product; H5 60 grid dates) runs inside the window. For H2 the 20-unit warm-up is 20
monthly units per leg, about three years (review F-15): no H2 unit is traded before 2016 and the full window holds
about 60 units; this is the prompt's rule, read literally. The prompt's 2010-06-07
start does not bind: E.12 quoted whole months and the dataset begins 2010-06-06, so 2010-06 is unpriced for every
product (U2). Never read: holdout-2 (2024-03..2025-03, trade dates 2024-04-01..2025-03-31 and the March 2024
embargo), MES's stores, the research window 2025-04..2026-06, anything from 2026-06-21.

Fallback (prompt, fixed): if E.17 cannot buy a product's extension, that product's window is 2019-05-06..2024-02-29,
recorded per product at E.17's registration from the fresh quote and the funds, before any purchase; a product
whose purchase or store build then fails is added, with the reason, before any test bar is read. A test whose
products all fall back runs on the short window with the lower power stated in section 8. The C1 roots (NG, NQ,
ZN, 6E, GC, ZC) come from C1's ext2010 plan; if C1's purchase does not happen, they fall back the same way.

D4's start rule S_X (E.12: ZF from 2020-10-01, ZT from 2021-10-01) does NOT apply to these tests: the prompt and
U2 fix the windows, and E.12's stores hold every product's trade dates 2019-05-06..2024-02-29 (S_X is applied by the
caller, not in the store). Gate 0 did not read ZF before 2020-10-01 or ZT before 2021-10-01; these tests do.

## 4. The 2010-2024 splice rule (decidable before any bar is read)

- Stores: 2010 to 2019-04-30 from the hist stores (plan "ext2010" for the C1 roots, E.17's 21-root plan for the
  others; trade dates up to 2019-04-30); 2019-05-06 to 2024-02-29 from E.12's phase-1 step-2 stores (data.step2_store,
  read through data.stage_e_bars' confirmation loader with its trade-date refusals). Each file's sha256 is checked
  against E.17's run manifest before any row is returned.
- Boundary: 2019-05-01, 05-02 and 05-03 are in neither store. A trade date in both stores is refused (no date is
  double-counted). A multi-day unit whose holding period spans the boundary is excluded ("store boundary"); a
  reference price across the boundary follows lead_spec section 2 (immediately preceding trade date only, so
  2019-05-06 has no H1 or H4 signal).
- Rolls: each store is a spliced front-contract path (Databento's `<ROOT>.v.0` symbology, fetched with the
  purchase; metadata, not prices). Roll blackouts as data.stage_e_bars L-8. Multi-day positions roll at the splice
  (lead_spec section 2); signals chain across splices; a reference and its trade must be the same contract.
- Calendars: 2019-05-06 on, the frozen group calendars (data/calendars/<group>.py); 2010-2019, the frozen hist2010
  calendars (data/calendars/hist2010/<group>.json, E.14) and, for livestock, reports/stage_e16_calendars/
  hist2010_livestock.json (Task 3b); unsourced calendar dates are excluded as action dates.
- Task 3b's files (reports/stage_e16_calendars.md; rulings R-C1 to R-C6): hist2010_livestock.json (sha256
  802a4dd98a71776af58748c43c2a70772a966a2e37dd08e32fef1ebfe023ba5d; trade dates 2010-06-01..2019-05-31 in E.14's
  hist2010 format; 2,274 trade dates, 75 closures, 26 early halts, 295 late opens; 25 of 2,349 weekdays unsourced,
  1.06%, under the 2% bar; session eras 09:05, 08:00 with Monday 09:05 late opens, 08:30 from 2016-02-29) and
  ec_auc_2010_2019.json (sha256 0c21ce8554698c51868451ca596549bc2940e3271dca47b2f5802ba5e54a7047; 684 rows from
  FiscalData auctions_query, metadata fields only, E.0's filter and announcement rule; equal to the frozen rows on
  the 2019-05/06 overlap). H3's auctions are these rows to 2019-04 and the frozen EC-AUC rows of
  reports/stage_e2b_release_calendar.json from 2019-05. H3 is tightened (review F-04, lead ruling): an
  auction counts only if its announcemt_date is on or before t-3 (Treasury announces at 11:00 ET, before the 14:00 CT
  short entry); else "announced after entry"; no date on file, "no announcement date". The dates come from the
  rows' own fields (2010-2019, added from the saved FiscalData CSV) and from reports/stage_e16_calendars/
  ec_auc_announcements_2019_2024.json for the frozen 2019-05..2024-02 rows (FiscalData metadata, fetched in Stage
  E.16). Announced after t-3 and excluded: 49 of 420 in 2010-06..2019-04 (11.7%) and 46 of 231 in 2019-05..2024-02
  (19.9%), mostly 2-year notes auctioned on a Monday and announced the Thursday before
  (reports/stage_e16_calendars/f04_t3_counts.json).

## 5. Settlement minutes and day-session opens (reports/stage_e16_settlement.json; lead_grade governs)

| Product | S_p periods (CT; lead_grade) | O_p periods (CT) |
|---|---|---|
| NQ | 2010-06-07..2012-11-18 15:15 (secondary); 2012-11-19..2020-10-25 15:15 (primary); 2020-10-26..2024-02-29 15:00 (primary) | 2010-06-07..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |
| YM | 2010-06-07..2012-11-18 15:15 (secondary); 2012-11-19..2020-10-25 15:15 (primary); 2020-10-26..2024-02-29 15:00 (primary) | 2010-06-07..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |
| RTY | 2010-06-07..2017-07-09 not listed (none); 2017-07-10..2020-10-25 15:15 (primary); 2020-10-26..2024-02-29 15:00 (primary) | 2010-06-07..2017-07-09 not listed; 2017-07-10..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |
| ZT | 2010-06-07..2014-02-24 14:00 (primary); 2014-02-25..2024-02-29 14:00 (primary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| ZF | 2010-06-07..2014-02-24 14:00 (primary); 2014-02-25..2024-02-29 14:00 (primary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| ZN | 2010-06-07..2014-02-24 14:00 (primary); 2014-02-25..2024-02-29 14:00 (primary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| TN | 2010-06-07..2016-01-10 not listed (none); 2016-01-11..2024-02-29 14:00 (primary) | 2010-06-07..2016-01-10 not listed; 2016-01-11..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| ZB | 2010-06-07..2014-02-24 14:00 (primary); 2014-02-25..2024-02-29 14:00 (primary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| UB | 2010-06-07..2014-02-24 14:00 (primary); 2014-02-25..2024-02-29 14:00 (primary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| 6E | 2010-06-07..2024-02-29 14:00 (secondary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| 6A | 2010-06-07..2024-02-29 14:00 (secondary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| 6B | 2010-06-07..2024-02-29 14:00 (secondary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| 6C | 2010-06-07..2024-02-29 14:00 (secondary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| 6J | 2010-06-07..2024-02-29 14:00 (secondary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| 6S | 2010-06-07..2024-02-29 14:00 (secondary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| 6N | 2010-06-07..2024-02-29 14:00 (secondary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| CL | 2010-06-07..2015-07-05 13:30 (primary); 2015-07-06..2024-02-29 13:30 (primary) | 2010-06-07..2019-04-30 08:00; 2019-05-01..2024-02-29 08:00 |
| NG | 2010-06-07..2015-07-05 13:30 (primary); 2015-07-06..2024-02-29 13:30 (primary) | 2010-06-07..2019-04-30 08:00; 2019-05-01..2024-02-29 08:00 |
| GC | 2010-06-07..2024-02-29 12:30 (primary) | 2010-06-07..2019-04-30 07:20; 2019-05-01..2024-02-29 07:20 |
| HG | 2010-06-07..2017-09-25 12:00 (secondary); 2017-09-26..2024-02-29 12:00 (primary) | 2010-06-07..2019-04-30 07:10; 2019-05-01..2024-02-29 07:10 |
| ZC | 2010-06-07..2012-06-24 13:15 (primary); 2012-06-25..2013-04-07 14:00 (primary); 2013-04-08..2015-07-05 13:15 (primary); 2015-07-06..2024-02-29 13:15 (primary) | 2010-06-07..2013-04-07 09:30; 2013-04-08..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |
| ZW | 2010-06-07..2012-06-24 13:15 (primary); 2012-06-25..2013-04-07 14:00 (primary); 2013-04-08..2015-07-05 13:15 (primary); 2015-07-06..2024-02-29 13:15 (primary) | 2010-06-07..2013-04-07 09:30; 2013-04-08..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |
| ZS | 2010-06-07..2012-06-24 13:15 (primary); 2012-06-25..2013-04-07 14:00 (primary); 2013-04-08..2015-07-05 13:15 (primary); 2015-07-06..2024-02-29 13:15 (primary) | 2010-06-07..2013-04-07 09:30; 2013-04-08..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |
| ZM | 2010-06-07..2012-06-24 13:15 (primary); 2012-06-25..2013-04-07 14:00 (primary); 2013-04-08..2015-07-05 13:15 (primary); 2015-07-06..2024-02-29 13:15 (primary) | 2010-06-07..2013-04-07 09:30; 2013-04-08..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |
| ZL | 2010-06-07..2012-06-24 13:15 (primary); 2012-06-25..2013-04-07 14:00 (primary); 2013-04-08..2015-07-05 13:15 (primary); 2015-07-06..2024-02-29 13:15 (primary) | 2010-06-07..2013-04-07 09:30; 2013-04-08..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |
| LE | 2010-06-07..2014-12-14 13:00 (weak); 2014-12-15..2024-02-29 13:00 (primary) | 2010-06-07..2014-10-26 09:05; 2014-10-27..2016-02-28 08:00 (09:05 first trade date of the week); 2016-02-29..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |
| HE | 2010-06-07..2014-12-14 13:00 (weak); 2014-12-15..2024-02-29 13:00 (primary) | 2010-06-07..2014-10-26 09:05; 2014-10-27..2016-02-28 08:00 (09:05 first trade date of the week); 2016-02-29..2019-04-30 08:30; 2019-05-01..2024-02-29 08:30 |

Sources: 33 (reports/stage_e16_settlement.md; raw pages under reports/stage_e16_briefs/pages/settlement/, kept on disk and not committed: CME-authored filings hosted by cftc.gov). Grades: the worker's grade and the lead's lead_grade are both in the JSON.

Lead rulings on the table (reports/stage_e16_rulings.md): R-S1 periods stated or attested as the then-current
procedure by a primary filing keep their grade; R-S2 periods inferred across their span (NQ and YM 2010-06-07..
2012-11-18, the six FX majors 2010-2024, HG 2010-06-07..2017-09-25) are capped at secondary, which meets the H1/H4
bar; R-S3 LE 2010-06-07..2014-12-14 is weak (13:00 assumed, no saved source): no H1 or H4 unit there; R-S4 no unit
before listing; R-S5 livestock's day open 2014-10-27..2016-02-28 is 08:00 CT, 09:05 CT on the first trade date of
its week; R-S6 the equity settlement at 15:15 CT before 2020-10-26 is followed as it is (H1's window 14:45-15:15,
past Topstep's 15:08 flatten in that regime; from 2020-10-26 it is 15:00, inside the flatten); the count of
product-dates with S_p > 15:08 is reported with each H1 result. H1's result also shows its pooled statistics without those
product-dates (descriptive; review F-14), and H4's without its "uncalibrated bucket" units (descriptive; F-13).
Grains' O_p 09:30 in 2012-05-21..2013-04-07 is the floor open inside a continuous Globex session (the frozen hist
calendar's day session), not an electronic open (review F-16).

## 6. Costs (lead_spec section 1; U3a)

Base: frozen D8 at size one per side (Topstep's round-turn commission, the 2025-26 mbp-1 bucket slippage of the fill
minute, D8's event-window rule); stress: base plus one tick per side; 1.5 x slippage: reported. D8 is calibrated on
2025-26 books and understates earlier costs (D8 "early-era bias"); the stress case is the guard. Release calendars
for the event-window rule and the fill guard:
From the frozen 2019-05..2024-02 release calendar alone (reports/stage_e16_briefs/release_touch.md), FOMC
(13:00 CT) is the only release type that touches an H fill minute (H1's energy entries at 13:00 fall in the D9.5a
fill guard and are excluded on FOMC days; H4's rates, FX and other exits at S_p - 31 = 13:29 and grains' 13:15
exits pay the event-window cost); E.14's FOMC 2010-2019 rows (reports/stage_e14_cal_releases.json) cover the early
years, so lead_spec section 1's conservative fallback is not needed. Every other type never touches an H fill
minute. A fill in a 30-minute bucket with no frozen D8 calibration (LE and HE at 08:01 in 2014-10-27..2016-02-28)
pays the product's largest per-side slippage (D8's rule for a bucket quoted on fewer than 3 of 5 dates; ruling
R-B2).

Settlement-minute fills at a scheduled closure (ruling R-B1): when a scheduled closure of the group calendar begins
at S_p (equity's 15:15 halt before 2020-10-26; grains' session close at 13:15 or 14:00 in the years it closed
there), an exit or mark "at the settlement minute" is the close of bar(p, d, S_p - 1), the frozen engine's own fill
for a position at a closure, and an entry at that minute is the open of the first bar of the same trade date after
the closure (none: the unit is excluded, "no entry bar"; equity before 2012-11-19, when the session after 15:15
belonged to the next trade date).

Stated departure from the engine (review F-09, lead ruling): the frozen engine cancels an OPENING order pending at a
closure print (an intraday safety rule); R-B1(b) instead opens at the first bar after the closure on the same trade
date. It applies to H2's NQ entries 2012-11-19..2020-10-23 (decision at the 15:15 settlement, entry at the 15:30
reopen) and to any H3 entry at such a minute; the fill is causal (after the decision) and pays its own bucket's cost;
the count is reported ("entry after closure"). Following the engine there would leave H2 about 15 units.

Release-touch check beyond 2019-2024 (review F-11): minutes that exist only in 2010-2019 (equity 14:45 entries,
grains 09:31 entries, livestock 08:01 and 09:06 entries, HG 11:30 under the 2011-2012 FOMC times) were checked against
every release type's product list in the frozen calendar: no type without 2010-2019 rows concerns a product at such
a minute, and E.14's FOMC rows carry the real 2010-2013 instants (13:15, 11:20-11:35, 13:00). E.17 need not repeat it.

Fills the engine would not make, handled conservatively (review F-07): where rules/price_limits.py has a limit
period (2019-05-01 on), every fill is tested with the engine's limit-lock rule and a locked fill excludes the unit
("limit locked"); before 2019-05 no limit table exists and the count of single-price fill bars (high = low) is
reported per test and product as a diagnostic. Entries inside Topstep's no-new-positions window are counted ("no new
positions (Topstep)") and excluded from a descriptive Topstep-venue table only (none is expected: H1's entries are at
S_p - 30 and early-halt dates are excluded).

## 7. Data reuse and order disclosure (V24, V28, V29)

V24 (docs/DECISIONS.md): "The phase-1 stores stay on disk; any reuse needs a new pre-registration that counts
N = 471", and for E.13 "Re-running Gate 0, relaxing its bar, or re-mining the 2019-2024 stores is ruled out". V28
and V29 direct H1 to H5 onto data already owned plus the 2010 extension. This pre-registration is that new one: it
counts the program's N (471, plus C1's 2 if C1 registers first, plus these 5). Every H test's 2019-05-06..2024-02-29
segment is the same E.12 bytes Gate 0 read (all 27 products; Gate 0 tested CP1, CP3, prior-day-return, month-end
and auction-clock features there, none rejected; reports/stage_e16_overlap.md section 7 lists every read, and each
H file's section 4 quotes its relation). In E.17, C1 runs before H1 to H5 (U1) and reads NG, NQ, ZN, 6E, GC and ZC
2010-2019, including NG's and GC's H1 windows and part of ZC's; this freeze precedes any of those bytes.

## 8. Power (lead_spec section 5)

Method (base_rules/power.py; reports/stage_e16_power.json and .md, seed 20261009, 4000 simulations per
cell): unit counts per test and year from the calendars alone (base_rules.report counts: windows, listing, trade
dates, early halts, unsourced dates, estimated roll blackouts of 3 dates per splice from each product's listed
contract cycle, settlement grades, the R-B1 closure rule; missing bars inside a session and zero signals assumed 0);
per-unit net returns i.i.d. normal at the prior's annual net Sharpe scaled to the unit; a pass requires p (the
larger of the plain-t and Newey-West p) at or below the threshold, mean > 0, n >= 30 and year stability with the
test's unit threshold. Two thresholds bracket Holm: 0.01 (its first step, 0.05/5) and 0.05 (its last). The analytic
one-sided t power is beside it. Each H file's section 5 gives its rows; summary (P(pass all bars) at 0.01 / 0.05):

| Test | Prior Sharpe | Full window: units, pass | Fallback window: units, pass |
|---|---|---|---|
| H1 | 0.3 | 3385, 0.110 / 0.247 | 1193, 0.037 / 0.146 |
| H1 | 0.8 | 3385, 0.707 / 0.853 | 1193, 0.265 / 0.521 |
| H2 | 0.4 | 60, 0.105 / 0.258 | 15, 0.000 / 0.000 |
| H2 | 0.9 | 60, 0.534 / 0.750 | 15, 0.000 / 0.000 |
| H3 | 0.3 | 354, 0.089 / 0.242 | 69, 0.036 / 0.121 |
| H3 | 0.7 | 354, 0.498 / 0.703 | 69, 0.116 / 0.303 |
| H4 | 0.2 | 3385, 0.056 / 0.156 | 1193, 0.024 / 0.098 |
| H4 | 0.6 | 3385, 0.432 / 0.640 | 1193, 0.141 / 0.354 |
| H5 | 0.8 | 3370, 0.703 / 0.841 | 1154, 0.250 / 0.503 |
| H5 | 1.5 | 3370, 0.999 / 1.000 | 1154, 0.802 / 0.930 |

H2 cannot pass on the fallback window (2 qualifying years with at least 6 units, below the 3 the bar needs); on the
full window it has about 60 units after its 20-unit warm-up. The low priors give little power for H1, H3 and H4; the
high priors and H5 give useful power on the full window only. H3's units reflect review F-04's
announcement rule (95 auctions announced after t-3 excluded). These are planning numbers, never part of a verdict.

## 9. Code and commands

base_rules/ (27 files) and its tests tests/test_base_rules_*.py with tests/_base_rules_fixtures.py, every file
hashed in the freeze manifest; base_rules/README.md gives the modules, the rulings applied (R-B1 to R-B4), the
coder's choices and the E.17 commands. The runner checks every input (the freeze manifest and every file it lists,
the registration under label E16 with ids E16-H1..E16-H5, a free output path, the run manifest and a row-free
preflight of every store) BEFORE it writes the run-once marker; after the marker no data condition stops a run (it is
excluded and counted). Commands (E.17, after registration and the store builds):

    uv run python -m base_rules.run run --test H1 --freeze reports/stage_e16_freeze.json --freeze-sha256 <sha> \
        --manifest <run manifest> --manifest-sha256 <sha>          # then H2, H3, H4 the same
    uv run python -m base_rules.run run --test H5 --freeze reports/stage_e16_freeze.json --freeze-sha256 <sha>
    uv run python -m base_rules.run verdict --freeze reports/stage_e16_freeze.json --freeze-sha256 <sha>

Runtime (synthetic probe at full 2010-2024 scale, 27 products, before rulings R-B1 to R-B4; reports/stage_e16_briefs/
runtime_probe.md): H1 4:32 and H4 4:25 wall, peak RSS 1.2 GB; H2 0:23; H3 0:45; H5 0:01.

## 10. Trial count and family

N rises by 5 at E.17's registration whatever the outcomes (expected 473 -> 478 after C1's 471 -> 473). Holm at
family-wise 0.05 across the five registered tests, on the base case. A pass is evidence, not a deployment verdict:
the next step for a pass is a holdout-2 registered read (where the stress case must survive, U3a) and only then a
meta-labeling design (V28).
