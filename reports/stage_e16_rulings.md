# Stage E.16 rulings (user-side rulings of 2026-10-09 and the lead's rulings)

All times PDT. The user-side rulings were relayed from the planning chat at about 00:10 on 2026-10-09, after the
lead raised three points at about 23:45 on 2026-10-08 (the E.17 harness sequence, the window starts, and two
pre-registration choices); the lead wrote them into the spec before any worker was spawned.

## User-side rulings (2026-10-09)

- U1 E.17 harness: not caps-only for the whole stage. C1 first under a harness whose only diff from v10 is the
  acct-2 cap and the session caps (C1 freeze section 11); C1's evaluation completes; only then a further harness
  adds the purchase plan for the remaining extension roots. (Hand-off steps 6 to 8.)
- U2 Windows: each product's window starts at the first priced month after its last unpriced gap before 2019-05
  in reports/stage_e12_quotes_ext2010.json, plus warm-up, recorded per product in the freeze before any bar exists.
  Applied literally (reports/stage_e16_windows.json): 24 products 2010-07, TN 2016-01, RTY 2017-06, and HE 2017-07
  (its last unpriced month is 2017-06; the planning chat's message named the other three; the literal rule gives
  HE's start, which the lead records here).
- U3a Costs: base = frozen D8 with no extra tick; stress = D8 plus one tick per side, reported for every test and a
  must-survive condition for any later holdout-2 registration.
- U3b H2 year stability: years with at least 6 monthly units; 10 for the other tests.

## Lead rulings on Task 1, the settlement table (lead_grade written to the JSON at about 00:40; this text 00:45)

- R-S1 A period whose minute is stated by a primary filing dated inside it, or attested as the then-current
  procedure by a primary filing at its end with no change found, keeps the worker's grade.
- R-S2 A period inferred across its span from a primary filing at its boundary that describes settlement at the
  session or pit close, with a source covering the span that states that close or the settlement time, is capped
  at "secondary" (meets the H1/H4 bar): NQ and YM 2010-06-07..2012-11-18; 6E, 6A, 6B, 6C, 6J, 6S 2010-06-07..
  2024-02-29 (CME 08-96 of 2008 plus Baltussen et al. 2021's sample to 2020-05); HG 2010-06-07..2017-09-25.
- R-S3 LE and HE 2010-06-07..2014-12-14: 13:00 CT was assumed and no saved source covering the span states the
  settlement time or the pit close (the 2014 Reuters reprints are unverified and on hosts whose terms forbid
  robots); "weak": no H1 or H4 unit for LE there (HE's window starts 2017-07 and is not affected).
- R-S4 No unit of any test before a product's sourced listing (minute null in the table): RTY before 2017-07-10, TN
  before 2016-01-11.
- R-S5 Livestock's day open 2014-10-27..2016-02-28: 08:00 CT (the Globex restart), 09:05 CT on the first trade date
  of its week, as the worker's sources state (the futures pit opened 09:05 until its 2015-07 closure; H4 uses the
  electronic day open, which is when the bars resume). Task 3b's livestock calendar is cross-checked against it.
- R-S6 Equity settlement at 15:15 CT until 2020-10-23 (CME/CBOT 20-018, effective trade date 2020-10-26: 15:00):
  every test follows S_p as it was. H1's equity window before 2020-10-26 is 14:45-15:15, after Topstep's 15:08
  flatten; the hypothesis concerns the settlement window and today's S_p (15:00) lies inside the flatten, so a pass
  would be tradeable now. The count of product-dates with S_p > 15:08 is reported with each H1 result. H2's decision
  minute is NQ's S on d5 (15:15 before 2020-10-26).
- The worker's disagreements with the frozen calendars' day-session close C (equity 15:00 vs a 15:15 settlement
  before 2020-10-26; grains hist2010 C 14:00 in 2012-05-21..06-24 and 13:20 from 2015-07-06) are recorded and not
  acted on: H tests use S_p from this table, never C, and the calendars stay frozen.
- The raw pages (CME-authored rule filings hosted by cftc.gov, and Baltussen et al.) stay on disk and are not
  committed, as E.13's and E.14's page folders; their sha256s are in the table's sources block.

## Lead rulings on Task 2, the overlap audit (written 00:45; the audit returned 00:28)

- R-O1 None of H1 to H5 is identical (same signal, window and products) to a tested member: all five are KEPT, each
  with the audit's relation text quoted verbatim in its pre-registration section 4.
- R-O2 D4's start rule S_X (E.12: ZF 2020-10-01, ZT 2021-10-01) does not apply: the prompt and U2 fix the windows,
  and E.12's stores hold all trade dates from 2019-05-06; the common file discloses that Gate 0 did not read ZF and
  ZT before those dates.
- R-O3 V24's wording on reusing the 2019-2024 stores is quoted in the common file (section 7) beside V28 and V29,
  with the reads the audit lists, and E.17's order (C1 reads NG, NQ, ZN, 6E, GC, ZC 2010-2019 before H1 to H5 run)
  is disclosed; the freeze precedes those bytes.

## Lead rulings on Task 3b, the calendars (written 01:08; the builder returned about 01:07)

- R-C1 CME holiday-schedule PDFs re-hosted on Dorman Trading's own site (robots.txt allows all; no terms page; not
  cmegroup.com and not an archive of it) are accepted at "secondary": the prompt permits exchange text quoted by
  permitted sources. Without them 30.7% of livestock weekdays would be unsourced and the 2% check would fail.
- R-C2 Cannon Trading's holiday-schedule images (2016-2019; robots.txt disallows listed paths only; no terms page),
  read visually with the transcription recorded and the image saved with its sha256, are accepted at "secondary".
  Without them 2.6% would be unsourced (fails).
- R-C3 The livestock calendar as built passes: 25 of 2,349 weekdays unsourced (1.06%; 1.08% over 2010-06-07..
  2019-04-30), and its 2019-05 overlap agrees with data/calendars/livestock.py. Its three session eras (open 09:05
  to 2014-10-24; 08:00 from 2014-10-27 with Monday 09:05 late opens; 08:30 from 2016-02-29) agree with the
  settlement table's day opens (R-S5). Unsourced dates are excluded as action dates.
- R-C4 EC-AUC 2010-2019 passes: 684 rows from 862 FiscalData records (metadata only), 0 of 420 tenor-matched records
  in 2010-06..2019-04 dropped, 1 same-day announcement excluded (2019-06-21, as E.0); the 2019-05/06 overlap equals the
  frozen rows (12 ids, every field but "source"). Tenor follows original_security_term (the frozen convention), so
  the original-term label decides the contract in H3 (for example a reopening keeps its original term).
- R-C5 Deviations recorded, no evidence affected: a Farm Media page was fetched before its terms were read (the
  terms forbid automated copying; the file was deleted and not used); fia.org's and ampfutures.com's terms were read
  seconds after their single fetches (both permit the use or have no clause).
- R-C6 For E.17's later harness: data.hist_calendar's HIST_GROUPS must add "livestock" before
  load_hist_group_calendar accepts the file (hand-off step 8).

## Lead rulings on Task 3, the build (sent to the coder 01:15; applied by 01:24)

- R-B1 Settlement minute at a scheduled closure: when a scheduled closure of the group calendar begins at S_p, an
  exit or mark at the settlement minute is the close of bar(p, d, S_p - 1) (the frozen engine's own fill for a
  position at a closure), and an entry there is the open of the first bar of the same trade date after the closure
  (none: excluded, "no entry bar"). Without it, equity's 15:15 settlement (before 2020-10-26) and grains' settlement
  at the session close had no fill bar: H2 kept 5 units and equity and grains lost H1/H4 for years.
- R-B2 A fill in a 30-minute bucket with no frozen D8 calibration pays the product's largest per-side slippage (D8's
  rule for a bucket quoted on fewer than 3 of 5 dates), counted "uncalibrated bucket"; replaces the coder's
  exclusion (204 LE/HE H4 units in the probe).
- R-B3 No data condition raises after the run-once marker (a contract change, a refused store, a missing bar are
  excluded and counted); every input problem is detected before the marker.
- R-B4 Registry label E16, ids E16-H1..E16-H5, hard-coded (no run-time override).
- R-B5 The power table was rerun on the real inputs (reports/stage_e16_power.json/.md, not provisional); the
  full-scale probe was not rerun (its times predate R-B1 to R-B4; the changes do not add bar reads beyond S_p - 1).
- The coder's choices 1 to 12 (base_rules/README.md) are accepted, with choice 10 replaced by R-B3 and choice 11
  by R-B2.

## Lead rulings on the freeze review (reports/stage_e16_review.md: APPROVE WITH FIXES; 1 BLOCKING, 8 SHOULD FIX, 7 NOTE; rulings 01:50)

- F-01 BLOCKING, accepted, fixed in code: plans fixed per root ("ext2010" for NG NQ ZN 6E GC ZC, "ext2010h" for the
  other 21); the run manifest's ext2010 entry carries its plan; the loader checks the file name pattern
  (last 2019-04-30, first at or before the window start), the metadata plan and bookings via an injectable plan
  resolver; hand-off step 8 fixes the plan name, label and file layout.
- F-02 accepted: the registration must carry this freeze's sha256.
- F-03 accepted: verdict's test subset removed (the family is the five); a non-default registry only in test mode;
  the registry path and sha256 recorded in every output.
- F-04 accepted, option (a), a tightening: an auction counts only if announced on or before t-3; announcement dates
  added to the 2010-2019 rows from the saved FiscalData CSV and fetched for the frozen 2019-05..2024-02 rows
  (FiscalData metadata; the prompt allows FiscalData in this stage). Option (b), citing Treasury's tentative
  schedule, would keep the 49 units but rest on a source the freeze never fetched.
- F-05 accepted: hand-off step 8 says label E16, ids E16-H1..E16-H5, plan "ext2010h"; the manifest is written as the
  last act before the commit and the hand-off placeholders are filled from it and the commit.
- F-06 accepted: the manifest now hashes the frozen modules base_rules imports (screening/stage_e_engine.py,
  stage_e_frozen.py, stage_e_rules.py, stage_e_verdict.py, trial_registry.py; rules/products.py,
  rules/price_limits.py; data/stage_e_bars.py, hist_bars.py, group_session.py, session.py;
  strategy/stage_e/interface.py), the four stage_e2a tables, the six hist2010 calendars by name (so v12's livestock
  copy does not trip the check), the seven group calendars used (not crypto); data/hist_calendar.py, pull_hist.py,
  hist_store.py and config.py stay out on purpose (v12 changes them); the hand-off says v12 must not touch a hashed
  file, else Part 2 stops for a re-freeze.
- F-07 accepted: the engine's limit-lock test where a limit table exists (2019-05 on), excluding "limit locked";
  single-price fill bars before 2019-05 reported as a diagnostic; no-new-positions entries counted for a descriptive
  Topstep table.
- F-08 accepted: an engine-match test for the R-B1 close fill.
- F-09 ruled: R-B1(b) is KEPT as a stated departure from the engine's closure-cancel (common file section 6,
  prereg_H2 section 3), with the counter "entry after closure". Reason: the fill is causal and costed; the engine's
  cancel is an intraday safety rule; following it would leave H2 about 15 units. Raised to the user in the return.
- F-10 accepted: release_touch.md, derive_windows.py, make_prereg.py and freeze_manifest.py are hashed; the hand-off
  stays outside the manifest by design (it carries the freeze's own hash).
- F-11, F-15, F-16 recorded in the common file; F-12 resolved by F-04's added fields; F-13 and F-14: descriptive
  tables without the "uncalibrated bucket" units (H4) and without S_p > 15:08 product-dates (H1).

- Recheck (reports/stage_e16_review.md "Recheck (2026-10-09)"): APPROVE; 12 FIXED, 4 ACCEPTED-AS-RULED, 0 NOT FIXED; NOTEs R-1 (manifest written last: done), R-2 (E.17 Fable recomputation asserts the registry path recorded in every output), R-3 (the runtime probe predates the fixes; expect a higher RSS than 1.2 GB) are carried into the hand-off.
