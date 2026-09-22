# Stage D.1e Task 5d: the lead's adjudication of the adversarial review

Lead: Fable 5.1, xhigh, 2026-09-22 06:55Z. Review: reports/stage_d1e_adversarial_review.md
(fable max, 55 findings: 7 BLOCKER, 23 SHOULD-FIX, 25 NOTE, verdict NOT READY). Every finding
is ruled on below; ACCEPT means the reviewer's fix is written into the document as proposed,
ACCEPT-MOD means written with the stated change, REJECT would mean left as is with the reason.
No finding is rejected. Amendments are applied to reports/stage_d1f_confirmation_list.md
(list) and docs/NULL_CRITERIA.md (criteria) before hashing; the numbers affected by R-1 are
recomputed, re-verified and re-filled; the reviewer re-reads the amended documents before the
hash.

| ID | Sev | Ruling | Amendment (where) and the lead's reasoning |
|---|---|---|---|
| R-1 | B | ACCEPT (option a) | list 3.1, A1; criteria 1, 5; coverage map. The unit is net ticks per micro per day with each round trip divided by its own contract quantity: d_t = sum over trips closing on t of trip_pnl_usd / (1.25 x trip_micros), trip_micros = the maximum absolute position during the trip, recorded by the runner (new additive field `trip_micros`). This is exact for the 29 fixed-size trials and C-H4 (q = 1), for H1-H6 (q = 2) and for D-H2/RT7 (per-trip q in 1..5) alike; it needs no mean-size convention. Scaling a 1-micro P&L to the 2-micro bar assumes per-micro costs do not rise with size; the size-5 slippage bucket a 2-micro order pays is slightly higher, so the assumption overstates the 2-micro edge, which is conservative for a null claim (stated). The 1b re-run, the power run, the coverage-map figures and N_C6 are re-issued at the correct unit and re-verified. Running the trials at 2 micros is forbidden, as the reviewer says. |
| R-2 | B | ACCEPT | list 0: seven hashes added (_lead_accounting.py, _d1d_accounting.py, f_data_native/trials.py, g_timeframe/trials.py, stage_d1d/d1b/d1 accounting JSONs); A1 gets a factory column with each parametrised factory verbatim. |
| R-3 | B | ACCEPT | list 5.4 rewritten: the hashed statistics modules are not edited; a wrapper module calls their builders with the confirmation dates as _d1e_event_series.py does, with the 1e-9 reproduction test. list 5 enumerates every file D.1f may change; everything else is byte-identical to the freeze manifest. |
| R-4 | B | ACCEPT | list 1.5 step 1b: harness-freeze manifest of sha256 over screening/, sim/, funnel/, rules/, data/*.py, strategy/interface.py, the new D.1f modules and the section 0 files, written and printed before any quote; the list runner refuses to run if any hash differs, re-checks at completion, records the manifest hash in every output. |
| N-1 | B | ACCEPT (option a, mechanism pinned) | list 5 and A1: before the purchase D.1f writes a hashed release-table module for 2019-05-01..2024-02-29 (scheduled FOMC statement dates and times from the Federal Reserve's historical calendars; CPI and Employment Situation dates and times from the BLS schedule archives; published dates where a release moved; unscheduled FOMC actions excluded, the module's own convention; each entry cited). E-H1 and E-H2 receive the combined table through their factories if their constructors accept one; if not, the two modules are amended to accept a table with the default unchanged, re-hashed in a declared amendment before the purchase, with a test that the amended modules reproduce the train-union figures to the cent. C5 stays in the list. |
| C-1 | B | ACCEPT (full-session MBO) | list 3.5, criteria 1.1: D.1g buys full trade-date MBO (17:00 CT to 16:00 CT) for the N_C6 dates and simulates every resting order of C-H4 as coded; N_C6 and the budget line are re-issued at the correct unit. Restricting C-H4 to RTH would re-parametrise a frozen member. |
| D-2 | B | ACCEPT | list 5.3 and 1.5 step 4b: CALENDAR_COVERAGE extended to 2019-01-01 and asserted by the bar builder; the observed-holiday validation over the confirmation bars must pass before step 5; the 2025-2026 entries byte-identical to the hashed file; the calendar immutable once step 7 starts. |
| R-5 | S | ACCEPT | list A2: F4.4's event value is the plain round-level forward move with NO control adjustment; -3.3631 is that mean and the control-subtracted -4.5774 is descriptive. _d1e_event_series.py hashed in section 0; the D.1f wrapper reproduces its per-event definitions. Coverage map corrected the same way. |
| R-6 | S | ACCEPT | list A2: sample-derived thresholds (F2.4, F5.1, F5.2 terciles; F5.3 regression; G1/G4 Q80; trailing 20-date baselines) are recomputed on the confirmation window as the hashed code does; not frozen at EDA values. |
| R-7 | S | ACCEPT | list 1.5 and 5.5: H1-H6 exercised before step 7 on synthetic bars only; any run on research bars is logged as a look and counts one screen in N for that member. |
| R-8 | N | ACCEPT | list A3, criteria 4.3: 2-micro orders pay the size-5 slippage bucket; stated. |
| R-9 | N | ACCEPT | list 3.1: the bootstrap pinned by function, per-member rng seed 20260921, np.quantile linear, p = (k + 1)/(B + 1). |
| R-10 | N | ACCEPT | list 3.2 ii: the gate call for a statistic defined (p, R, T as for trips). |
| E-1 | S | ACCEPT | criteria 2.2 rewritten: 220 cells, both files pinned (power_gate.json, extension JSON with its 100 rows including the finished T = 32), "passing" defined as robust_c80_verdict == "pass", marginal excluded, no recomputation or extension changes epsilon for this list; power_gate_cells.json pinned. |
| E-2 | S | ACCEPT-MOD | criteria 7 and list 3.3/3.4: every class statement carries the per-trade epsilon at the confirmation frequency, the least-active member and its count, and the largest per-trade UCB95 in the class. Minimum activity: none is imposed on the null itself, because a member that almost never trades truly cannot fund a Combine, and that is the economic statement; but a member with fewer than 30 closed round trips or events on the window is marked "null by inactivity", and a class statement resting on such a member carries that label in the same sentence. Zero activity is inconclusive (N-2). |
| E-3 | N | ACCEPT | list A2: the cost sentence rewritten as the reviewer proposed; the earlier "overstates cost, conservative" sentence (the lead's own) was wrong in direction and is removed. |
| E-4 | N | ACCEPT | criteria 2.3: column labelled "trial members only". |
| E-5 | N | ACCEPT | list 3.1: r defined for trials and for statistics. |
| H-1 | S | ACCEPT | list A3: instrument guard covers every daily bar entering day d's condition (d-1 and d-2 for H3); the trailing 60 ranges exempt. |
| H-2 | S | ACCEPT | list A3: H4/H5 need 61 complete bars; percentiles over the 60 before d-1. |
| H-3 | S | ACCEPT | list A3: exit on the first bar with CT time >= 14:58 before the no-new-positions time; otherwise the engine's forced flatten, counted and logged. |
| H-4 | S | ACCEPT | list A3: factories take no arguments; the test-only warm-up override is a private constructor argument with the production default. |
| H-5 | S | ACCEPT | coverage map 5: proxies re-read at per-micro scale (B-H1 hold-75 99.5, A-H4 rth 229 per micro): per-trade SD 200 for H1-H5, 230 for H6; re-projected. |
| H-6 | N | ACCEPT | list A3: inequalities exactly as the table writes them. |
| H-7 | N | ACCEPT | list A3: q = 33.33 and 66.67 exactly, np.percentile linear. |
| H-8 | N | ACCEPT | list A3: a bar's CT clock time defined as the America/Chicago minute of its ts_event. |
| H-9 | N | ACCEPT | list A3: OR = 30 named as B-H3's declared OR30 and RT1-RT4's six five-minute bars; the entry window 09:00-14:29 as the OR end and the 14:30 no-new-positions convention. |
| L-1 | S | ACCEPT | list 1.2: each holdout-2 chunk sealed by the same call that downloads it before the next request; oldest-first pull order; the adapter's record-byte check is the only decode and yields a byte count; manifest records bytes and hashes only; the puller refuses to re-buy any chunk in either manifest. |
| L-2 | S | ACCEPT | list 5.2: the five acceptance invariants written in. |
| L-3 | S | ACCEPT | list 1.2: unlock headings name the holdout; per-holdout counting; the stage regex pinned; holdout-2 unreadable in D.1f and D.1g; any unlock before a registered D.2 voids the list. |
| L-4 | N | ACCEPT-MOD | list 1.2: no embargo on the mined side, with the reason written: every member is intraday-only and the mined window's runs started 2025-04-01 with their own warm-up inside the mined window, so no bar and no trailing state crosses the 2025-03-31 boundary in either direction; D.2's read of holdout-2 warms up on the confirmation window's tail, which lies before it. |
| L-5 | N | ACCEPT | list 1.2/4: 259 calendar trade dates before exclusions, about 239 after blackout and degraded dates. |
| L-6 | N | ACCEPT | list 1.2: "every March 2024 trade date". |
| M-1 | S | ACCEPT | list 3.2 iii: DSR, t and PBO pinned to the program's functions, inputs and block count; sensitivities at N = 101 and 186 reported, not criteria. |
| M-2 | S | ACCEPT | list 2.2: anomaly one-sided in direction s with net edge >= +2.11; a significant negative value is a sign reversal; future tests on forward data or a new purchase outside every window, under a new declaration, adding to N. |
| M-3 | S | ACCEPT-MOD | list 3.5: "on or before 2024-02-29"; D.1g's queue-model C-H4 is a new execution hypothesis, N = 59 for D.1g's DSR; its dates were read by D.1f's trade-through run of the same signal, so any C6 edge claim says it is out of sample only in the fill model. |
| M-4 | N | ACCEPT | list 3.6. |
| N-2 | S | ACCEPT | list 3.3/3.4, criteria 6: zero trips or events, or SE_boot = 0, is inconclusive. |
| N-3 | S | ACCEPT | list 1.3: trials trade through degraded days with the flag hidden; statistics exclude flagged dates; the degraded list is fetched once at step 2, frozen, compared with the eight known dates, differences logged before step 5. |
| N-4 | N | ACCEPT | list 3.1: the two denominators stated. |
| N-5 | N | ACCEPT | list 3.3: both constructions used as written, not reconciled after the run. |
| C-2 | S | ACCEPT | list 3.5, criteria 1.1: the fill model specified and hashed before the MBO purchase; any book-derived parameter estimated on declared days outside the evaluation dates. |
| D-1 | S | ACCEPT | criteria 4.1: medians over bars present; all trade dates of the month without exclusions; first month 2019-05 and S = 2019-05-06 if it qualifies; computed on the confirmation parquet after step 4's drop and on the research parquet as it is. |
| D-3 | N | ACCEPT | criteria 4.3: the two mechanical cost facts added. |
| D-4 | N | ACCEPT | list 1.1: a bar whose raw symbol is not an MES outright inside the continuous series is dropped and logged. |
| D-5 | N | ACCEPT | list 3.6, criteria 4.4: the vendor flag removes five 2020 dates from every statistic; stated. |
| V-1 | S | ACCEPT | list 6, criteria 1: hashing order (list first, its section 6 holds only time and chmod; criteria embeds the list's hash and is hashed second; both hashes to reports/stage_d1e_declaration_hashes.json and to progress.md; the user's commit is the anchor). |
| V-2 | S | ACCEPT | list 0: provenance table of the load-bearing inputs, hashes recomputed at hashing time for the files the R-1 fix regenerates. |
| V-3 | N | ACCEPT | list 0: "plus this stage's additive changes" replaced by the commit at declaration plus the freeze manifest. |
| V-4 | N | ACCEPT | criteria 2.2: power_gate_cells.json pinned. |
| V-5 | N | ACCEPT | list 3.5: N_C6 re-filled after R-1. |
| W-1 | S | ACCEPT | criteria 7: the aggregate sentence rewritten in the reviewer's scoped form. |
| W-2 | N | ACCEPT | criteria 1: the null stated as the inference the test supports. |
| W-3 | N | ACCEPT | criteria 1: trials executed through the engine; statistics charged the flat round turn. |
| W-4 | N | ACCEPT | criteria 5: the resolvable-member count recomputed after R-1. |

Also confirmed by the review and kept: the 31 section-0 hashes; the near-miss lists; epsilon = 34
on the pinned files (the reviewer's independent re-derivation on the 100-row extension file);
the holdout-2 bounds and embargo; the start rule reading only unsealed months.

## Re-review (section 15 of the review): 52 resolved, 3 partly, 10 new; all accepted

| ID | Sev | Ruling | Amendment |
|---|---|---|---|
| R-1 (remainder) | S | ACCEPT | criteria 1.1: C-H4 at its coded 1 micro, compared per micro with the 2-micro bar. |
| N-1 (remainder) = NEW-1 | B | ACCEPT | list 0: the two E-H entries annotated as pre-amendment hashes whose post-amendment hashes live in the freeze manifest, which section 0's INVALID rule and 5.6's refusal read for those two files only; "does not retype factories" excepts the two confirmation factories; A1 carries both factories for E-H1 and E-H2 verbatim, and the continuity run uses the no-argument ones. |
| N-3 (remainder) | S | ACCEPT | criteria 4.2 carries the list-1.3 sentence. |
| NEW-2 | N | ACCEPT | list 1.2 (b): holdout-2's size rationale restated at the corrected scale (239 usable days exceed every binding n_b except C3's 566). |
| NEW-3 | N | ACCEPT | criteria 3: N = 59 for D.1g noted. |
| NEW-4 | N | ACCEPT | list 1.5 1b: "asks the user to commit it". |
| NEW-5 | N | ACCEPT | list 1.5 1b: data/config.py's D.1f session id and caps set by the user before the freeze and frozen with it. |
| NEW-6 | S | ACCEPT | list 1.1: the raw symbol is the one mapped on the bar's date; a drop needs no MES outright on that date; drops per month logged, expected zero from 2019-05-06, non-zero stops the run for a lead decision. |
| NEW-7 | N | ACCEPT | list 0 wording; a note added at the head of the verification report pointing to section 11 as the verified state. |
| NEW-8 | N | ACCEPT | criteria 1: C-H4 moved out of the market-order clause. |
| NEW-9 | N | ACCEPT | list A3: H1 and H2's earlier ranges named as exempt. |
| NEW-10 | N | ACCEPT | criteria 2.2: the field named as tabulated for the grid and as stored in the extension file. |

The reviewer's verdict after these: READY TO HASH under the section 6 procedure. Hashed next.
