# B4 leakage and pipeline tests (protocol P4.1) and record-level synthetic streams (P4.2 first bullet)

TestCoder-OpusXHigh, Stage E.33. FINAL for this session (07:06 PDT 2026-10-28). Times PDT from `date`. Tests live in
reports/stage_e33_briefs/work/pipeline/tests_b4/; run results in reports/stage_e33_briefs/work/b4_runs/.
INTERFACE rule 1: real-data results below are counts only.

| LT | What ran | Counts | Status |
|---|---|---|---|
| LT1 truncation | Draw fixed and written (reports/stage_e33_briefs/work/LT1_draw.json): idx = default_rng(20261027).choice(796 x 273, 200, replace=False) over the (OOF date, i) grid, date = OOF[idx // 273], i = idx % 273, t = 08:35 CT + i min; 200 times on 178 dates (11 on excluded dates). Script tests_b4/lt1_truncation.py (build_features33.build_cutoff: all four inputs truncated at ts_recv <= t; G7 comparison with the production row; no row after t). Driver tests_b4/run_lt1_lt7.py (production store of the 178 dates under DERIVED/b4/lt_features, all 200 draws with prior=production, 20 with prior=recompute, then LT7) written but NOT launched: the session was cut by a usage limit at about 03:15 | Timing probe only (5 draws, Coder-A code c22b0a50f4cd, now superseded): 0 columns outside G7, 0 rows after t; recompute 66 s a draw, production prior 1.3-2.7 s | NOT RUN on the frozen code (5 of 200 draws on a superseded code). Needs the frozen Coder-A feature code (currently 6873427a6150 plus the FD6/FD7 rulings) and about 50 min at 3 processes with run_lt1_lt7.py |
| LT2 span | tests_b4/lt2_span.py on the 20 B3 dates: every kept row of A and B (all six labels) checked against the OTHER implementation's book replay and cal33's calendar: grid time, 08:35 open, 13:13 close (possible span and realised end), FH end exact, TB end in (t + L, t + 2L + h], release windows (closed), excluded dates, every book update in [t, max(t + L + h, end)] two-sided and not bad, valid M_ZM(t), limit band at t (exact integer test); feature part: every feature row's t_ns is 08:35 CT + i min on its date (the cut-off; LT1 tests what enters before it) | Final run LT2_r4 (07:03; labels A ff0181fc391c and B efdde5c74ee1, features A 6873427a6150 and B fb69badd4bb9): 46,886 kept rows (each side F05 4,303, F15 4,113, F30 3,828, F60 3,258, T15 4,113, T30 3,828), 0 violations on every rule, 0 errors; features 5,460 rows each side, 0 bad t_ns. Earlier runs r1-r3 also 0. Sensitivity: rows forced to row_ok with FH spans on 2021-07-09, 2022-06-03, 2021-04-01 give 273, 142, 82 violations, exactly the rows production removed | PASSED on the 20 B3 dates (the brief's 'any dates built so far'); not run on the full store, which did not exist |
| LT3 fold hygiene | SearchCoder's pipeline/tests/test_search33.py (35 tests: folds, embargo, inner split, training rows only, scaler, calibrator, mu_k, LightGBM bins from inner-train, early stopping on the inner block) + tests_b4/test_lt3_embargo.py (3 tests): OOF = universe[20:]; declared look-back table from P0.3/P4 (20 dates for sigma and the trailing references, 10 for F1.3, 21 for F1.7/F4.7, 1 for minute windows on late opens, 0 for calendar/definitions; labels 0 dates after D); for every fold the first training date after the block minus 21 lies after the block, the last training date before it ends before the block; both builders load at most 21 history dates | 35 passed (35.0 s); 3 passed | PASS. Note: the embargo (21) equals the longest look-back (21), not strictly more; equality is sufficient because the first post-embargo training date's earliest look-back date is the first embargo date. Weights per date: both label builders compute w inside one date's call (no cross-date input); B3 shows A and B weights equal |
| LT4 clock | tests_b4/test_lt4_labels_handbuilt.py (both implementations): a record with ts_recv <= t + L but ts_event after it is used, one with ts_recv 1 ns after t + L but ts_event before it is not; an update stamped exactly at t + h + L is used, 1 ns later is not; label starts are 08:35 CT + i min on CST, CDT and DST-change dates; A's replay and data33 order by ts_recv (stable) when handed ts_event order; data33.truncate keeps ts_recv <= cutoff (a ts_recv < ts_event record kept); D1 and D2 now tested as the lead ruled them (R-B3-D1, R-B3-D2) on both sides | Last full tests_b4 run 03:00: 53 passed (this file 31 incl. the ruled D1/D2 tests on lab33 ff0181fc391c and labB efdde5c74ee1) | PASSED (labels and data33.truncate). Feature cut-offs: by LT1, not run |
| LT5 leak canary | tests_b4/test_lt5_canary.py: LEAK(t) = y(t - 1 min) (FH15) on a record-level synthetic day; LT1-style truncation at 40 random t; LT2 window reach; then the canary as column F3_1 of synthetic INTERFACE tables (60 dates, FH15 labels from one random-walk mid path per date) through search33.run_fold / finalize_config (E33-S5F15L010A), against the same tables without it. Removed: exists only in pytest tmp folders | LT1: 25 of 40 truncation times change the canary, 0 change the honest control (5-minute mid return); LT2: 263 of 263 defined canary rows reach past t, control 0; CV: clean t = -2.18 (daily Sharpe -0.28, 387 trades), leaked t = 28.8 (daily Sharpe 3.72, 1,018 trades) | PASS (3 tests) |
| LT6 data guard | DataCoder's pipeline/tests/test_guard33.py + tests_b4/test_lt6_guard_classes.py | 44 passed; 10 passed. One test per P1.2 Refused class: sealed SOY_test_v1 folder (test_refuses_sealed_soy_test_folder, symlink, original location); ZM/ZS/ZL dated 2017-05-01..2020-11-30 (test_refuses_test_window_dates, spans from file and folder names, check_request, check_records); on or after 2024-03-01 (test_refuses_dates_on_or_after_2024_03_01, post-cutoff spans); derived_unsealed_files.tsv (test_refuses_files_listed_in_derived_unsealed_tsv, incl. a folder holding a listed file); other roots' market data (test_refuses_other_market_data_and_unlisted_files); E.31 measured outputs (test_refuses_e31_runs; the supplement adds stats31.md and the runs/ folder itself) | PASS |
| LT7 simulator causality | tests_b4/lt7_causality.py: at the LT1 times within each configuration's grid, the seed-1 null proof fold model of t's fold (DERIVED/proofs/seed1/search/<cid>/fold<k>.model.json, read only; search33.load_fold_model / predict_proba / decide); production decision = label table entry_ok and decide() on the production feature row; recomputed = lab33 entry rules on ZM records truncated at t and decide() on the LT1 rebuilt row; entry fills (decided side, and both sides) from lab33.entry_fill vs entry_fill_from_records truncated at the production fill time; production fill time vs the label table's <side>_entry_ns. Counts only | Partial run 03:12 (b4_runs/LT7_c22b_r1.json): the 20 seed-1 configurations at the 5 draws that had production features AND an LT1 rebuild (Coder-A c22b0a50f4cd, superseded), labels ff0181fc391c; 3 of them on dates with label tables: 50 decisions, 50 equal; 11 decided trades, 11 fills equal; 10 both-side fills equal of 10; 5 entry_ok equal of 5; 0 fill-time vs table mismatches; 10 skipped (i outside G_30); 199 inputs missing (draws without production features, rebuilds or labels). Mechanics dry run on synthetic-table models (b4_runs/LT7_dryrun.json) also all equal | NOT RUN at the declared scale (200 times; 3 usable draws on a superseded feature code). Needs LT1's rebuilds and production labels on the 178 draw dates: run_lt1_lt7.py step 4 |

## Record-level synthetic streams (P4.2 first bullet)

Generator tests_b4/synth_streams.py: ZM MBO (MBO_COMPACT) and ZS / ZL MBP-1 (data33.MBP1_SPLIT) for 30 trade dates
(2023-02-27..2023-04-07, across the DST change), at the data facts' rates: ZM about 580k records and 380k events a
date (data facts 3.1 median 491k ZM.v.0 records, 400k events), 14 events/s in the day session and 3/s overnight, an
evening R snapshot, adds / cancels / size and price modifies / trades (T, F, then C or M) / refills within 100 ms,
1-minute mid SD 3.26 ticks (P0.4: 3.15), spread one tick on 99.4% of updates; ZS 9 and 2.5 events/s, ZL 6 and 1.5;
0.14-0.15% of records with ts_recv < ts_event (F 1.4), 2% of events sharing a ts_recv, ZM.v.1 records interleaved,
side-N adds, a front roll at date 15. Episodes: empty ask side (dates 3, 19 past 13:20), a bad book ended by an R
(7), an R carrying F_MAYBE_BAD_BOOK (11, latent D1), a locked book at a decision minute on dates without limits (15,
23, latent D2), limit bands near the price (5, 6), releases (2, 9, 13), an excluded date (27).

Labels through BOTH implementations (run_synth_b4.py, seed 4242; DERIVED/b4/synth/4242/): 45,390 rows over six
labels x 30 dates; 27 of 30 dates agree in every column of every label (0 cells). The 3 others are the planted latent
differences: 2023-03-14 (date 11, D1: after the flagged R, A's book is good, B's stays bad until the next R) from
11:57 on; 2023-03-20 and 2023-03-30 (dates 15 and 23, D2: one minute, i = 40 and 175). Exercised and equal in both:
release windows (38 F05 minutes, 63 T30 minutes), entry fallbacks (flag 1), entries not made (16), TB entries not
made (32), exit fallbacks (2), exit marks at the last valid touch (2|8), the limit band, an excluded date.

Known-answer cases (tests_b4/test_lt4_labels_handbuilt.py, both implementations, values worked by hand): FH nets and
classes with ts_recv/ts_event ordering, TB up barrier with tau and exit at tau + L, entry fallback fill (flag 1),
exit marked at the high limit (2|4, net bid - HL - f) and at the last valid touch with no limits (2|8), release
window edges (F05 i 138-175, F60 i 83-175), limit band (i 26-35), excluded date. All pass on A and B.

Features through both builders (tests_b4/run_synth_features.py): the 30 OOF dates up to 2024-01-10 and every date
the builders ask for (51 dates: 21 history dates each, previous dates of late opens) get synthetic ZM MBO and ZS / ZL
MBP-1 records inside each date's real session intervals (data.group_session: the 2023-11-24 early close, the
2023-12-26 and 2024-01-02 late opens without an overnight session) with the date's real front ids; only
data33.load_zm / load_mbp1 are replaced, so both builders run with the real calendar, fronts, releases and
definitions. Independent oracle (this script's own mbo_book31 replay of the synthetic ZM stream): C.1, C.2, C.3,
C.4, C.15, F4.1 (i >= 1) and F4.6 on all 30 dates x 273 rows: 0 mismatches for A and for B. sigma_ZM: A = B on all 30.
- Run seed 7 (02:31-02:40): per-mark raw comparison of the two builders' intermediate arrays over the 51 dates:
  volume, OFI 1/5/15 (ZM, ZS, ZL), removals, lam60 equal on the 48 regular dates; differences only on 2023-11-24
  (marks 12:06-13:13, FD1) and the two late opens (marks 08:35-08:44 and lam60's 60 intervals, FD2), which
  confirms FD1 and FD2 on data with a known schedule. No pause-junction OFI difference (the synthetic pre-open book is
  never crossed, so A and B compute the same term: FD3a needs an invalid pre-open state, as diagnosed) and no
  removal difference (the generator makes no iceberg refreshes: FD5 needs them, as diagnosed). Refills: A counted 0,
  B 169k: a GENERATOR fault (each record had its own ts_event, so A's ts_event-grouped sweep sets never formed);
  fixed: one ts_event per event (data facts: 0 batches mix ts_events). Superseded.
- Run seed 8 (02:41-02:55, same streams with per-event ts_event): its builders were imported while both coders were
  changing code for the B3 rulings, so the code it ran is not pinned; superseded. The script now imports both
  builders before forking and writes code_used.json with the sha256 of every builder file.
- Final run seed 9 (03:14-03:31, code pinned at 03:14: Coder-A feat33 66b4e251dce9 + build_features33 2784e6b9ef85 = the
  6873427a6150 code; Coder-B featB 33269b3a4b4e, dayB 150d3c6c8dee, replayB c20eab0a2df6, build_featB b9fee7234fcb;
  DERIVED/b4/synthfeat/9/code_used.json): 8,190 rows (30 dates x 273), 0 disagreeing cells in all 59 columns, sigma_ZM
  equal on all 30, oracle 0 mismatches on both sides. PASSED. The synthetic streams hold no mixed fill-and-cancel
  record and no fill of a not-yet-booked order, so the two residual real-data differences (B3 FD6, FD7) do not appear.

## LT1 timing (02:26-02:28 PDT, Coder-A code c22b0a50f4cd, b4_runs/LT1_timing.json)

Five draws whose 21 history dates already had production pass-1 tables (2021-01-19 i 196, 2021-01-20 i 77,
2021-03-12 i 240, 2021-03-16 i 18, 2021-03-16 i 259). prior=recompute (D and all 21 history dates re-streamed from
truncated inputs): 66.4 s for one draw. prior=production (D re-streamed from truncated inputs, history from production
pass 1, whose records all precede D's window): 1.3-2.7 s a draw. All 5: 0 columns outside G7, 0 rows after t.
Production pass 2 was added for 2021-01-20 and 2021-03-12 in features/c22b0a50f4cd (0.2 s each), and the rebuilds
sit under features/c22b0a50f4cd/_lt1/<t>/.

Projection for 200 draws: recompute 200 x 66 s = 3.7 h at 1 process (about 1.3 h at 3); production prior about
200 x 2.5 s = 8 min, but it needs the production store on the 178 drawn dates (pass 1 measured about 3 s a date, so a
full store of 816 pass-1 and 796 pass-2 dates is about 40 min at 1 process, 15 min at 3). Proposal: run LT1 with
prior=recompute on the frozen feature code once the full store exists (a separate 1.3 h job at 3 processes), or
prior=production on all 200 plus recompute on a 20-draw subset (about 25 min at 1 process); the lead chooses.
