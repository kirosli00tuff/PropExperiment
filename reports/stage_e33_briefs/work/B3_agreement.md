# B3 agreement summary (TestCoder-OpusXHigh; INTERIM, updated as comparisons run)

Last update: 2026-10-28 07:05 PDT (FINAL for this session: run full_r2 on the fixed builds; see the first section). Harness: reports/stage_e33_briefs/work/pipeline/tests_b3/compare_b3.py (per-run
tables in reports/stage_e33_briefs/work/b3_runs/<run>.md; mismatching cells with both values in
DERIVED/b3/mismatches_<run>.parquet, never printed). INTERFACE rule 1: counts and mismatch locations only.

Dates: the 20 B3 dates (STATE 14:45 rule, recomputed here: OOF sorted, default_rng(20261028).choice(796, 20,
replace=False), sorted), identical to implB/labels/manifest.json: 2021-01-19, 2021-01-25, 2021-03-11, 2021-03-16,
2021-04-01, 2021-05-04, 2021-07-06 (excluded, late open), 2021-07-09, 2021-07-29, 2021-08-16, 2022-06-03,
2022-09-01, 2022-09-29, 2022-12-13 (excluded, after roll), 2022-12-22, 2023-01-11, 2023-02-16, 2023-04-10,
2023-08-11, 2024-02-15.

Tolerances (stated): labels, classes (y), entry_ok, row_ok, span_end_ns, n_long, n_short and every per-side field
(made, net, entry_ns, exit_ns, flags) exactly (a == b; NaN == NaN for floats); w within 1e-12 relative
(|a - b| <= 1e-12 max(|a|, |b|); a float mean of 1/c_m, summation order may differ); features
|a - b| <= max(1e-9 max(|a|, |b|), 1e-12) (G7), NaN == NaN counted separately; rows joined on i (a row on one side
only is a mismatch of column `__row__`). Coder-A's `mid_move` column (reported-only, lab33 17934b7b23b1) has no
Coder-B counterpart and is not compared.

## FINAL rerun on the fixed builds (run full_r2, 07:02 PDT)

Inputs: labels A = DERIVED/labels/ff0181fc391c (lab33 after R-B3-D1/D2; TB sigma from features/c22b0a50f4cd/_day)
against implB/labels (efdde5c74ee1); features A = DERIVED/features/6873427a6150 (the newest Coder-A folder: its
manifest lists the current feat33.py, sha256 66b4e251dce9...; 21c501f2e3e2 lists the same feat33.py but holds only 9
of 20 tables and an older build_features33.py) against features B = implB/features/fb69badd4bb9 (20 tables).
Per-run tables: b3_runs/full_r2.md; cells: DERIVED/b3/mismatches_full_r2.parquet.

| Family | Rows joined | Disagreeing cells |
|---|---|---|
| Labels F05 / F15 / F30 / F60 / T15 / T30 | 5,460 / 5,260 / 4,960 / 4,360 / 5,260 / 4,960 | 0 in all 19 compared columns, every date |
| sigma_ZM, sigma_ZS, sigma_ZL | 20 dates x 3 | 0 (A = B within G7 on all 20) |
| Features, 59 columns | 5,460 | 5,395 cells in 2 columns: F3_11 5,385 (every date, 263-273 rows each); F3_9 10 (2022-09-01 only, i 113-117 and 211-215). The other 57 columns agree on every row; NaN cells 0 |

Remaining diagnoses:
- FD6 (F3_11, refill depletion by a mixed record; diagnosed at 03:20 on the interim run, unchanged): Coder-A counts a
  depletion only when the emptying record's reduction is all fill lots (feat33._removal returns the level only when
  rest == 0); Coder-B when the reduction has any fill part (replayB.reduce, fill > 0). About 1 refill event a day
  differs (2021-01-19: 4,013 vs 4,014 refills; per-mark counts over 195 dates: A < B at 3% of marks, never A > B),
  which moves rbar_15 on every date, so almost every F3_11 row differs at 1e-9. Ambiguous ("reached 0 displayed
  quantity through trades"); the literal reading is Coder-A's (every lot that left with the record was filled). Lead
  rules; one condition changes on one side.
- FD7 (F3_9, new): on 2022-09-01 at 10:27:10 and 12:05:46 CT an F record names an order id that is not yet in the
  book, and the same event batch then adds and cancels that order (17 lots and 1 lot). Coder-A records fill lots only
  for orders already in the book (feat33: `if oid in orders` on F records), so it counts the cancel as a removal;
  Coder-B attributes the fill lots by order id within the batch, so the cancel is a fill, not a removal. Each event
  changes one 5-minute window (5 rows). Reading: F3.9 "fills are not removals" and R-B3-FD5 (fill lots are
  attributed within their event batch) favour Coder-B; fix in Coder-A (drop the book-membership gate on F records,
  keep the per-batch clear). Counts only; no outcome involved.

Record-level synthetic streams on the same code (Coder-A feat33 66b4e251dce9 / build_features33 2784e6b9ef85 = the
6873427a6150 code; Coder-B featB 33269b3a4b4e, dayB 150d3c6c8dee, replayB c20eab0a2df6, pinned at 03:14): 30 OOF dates
up to 2024-01-10 incl. the early close and two late opens: 8,190 rows, 0 disagreeing cells in all 59 columns, sigma
equal, independent oracle (C.1-C.4, C.15, F4.1, F4.6) 0 mismatches on both sides (DERIVED/b4/synthfeat/9/). The
synthetic streams contain neither mixed fill-and-cancel records nor fills of not-yet-booked orders, so FD6 and FD7
do not appear there.

## Status by family

| Family | A source | B source | Rows joined | Disagreeing cells | Run |
|---|---|---|---|---|---|
| Labels F05, F15, F30, F60, T15, T30 (production: A's TB uses sigma_ZM from A's features _day c22b0a50f4cd) | DERIVED/labels/17934b7b23b1 (built by TestCoder 02:20 PDT, 20 dates) | implB/labels efdde5c74ee1 | 5,460 / 5,260 / 4,960 / 4,360 / 5,260 / 4,960 | 0 in every one of the 19 compared columns, every label, every date | b3_runs/full_r1.md |
| Labels, after the D1/D2 rulings (lab33 ff0181fc391c, TB sigma from features/c22b0a50f4cd/_day) | DERIVED/labels/ff0181fc391c | implB/labels efdde5c74ee1 | as above | 0 in every column, label and date (run lab_r3, 03:01); LT2_r3: 46,886 rows, 0 violations | b3_runs/lab_r3.md |
| sigma_ZM(D), sigma_ZS(D), sigma_ZL(D) | features/c22b0a50f4cd/_day | implB/features/345ba20d4f97/_day and B's label-builder sigma | 20 dates x 3 | 0 (all agree within G7; A = B feature = B label sigma_ZM on all 20) | b3_runs/full_r1.md |
| Features (59 columns) | features/c22b0a50f4cd | implB/features/345ba20d4f97 | 5,460 rows | 35,473 cells in 34 columns; every row has at least one (F2.9, F2.11, F3.2, F3.3, F3.11 differ on almost every row) | b3_runs/full_r1.md; cells DERIVED/b3/mismatches_full_r1.parquet |

Feature mismatch counts by column (disagree of 5,460; columns not listed agree everywhere): C_5 298, C_12 11,
C_13 26, C_14 25, F1_1 26, F1_2 116, F1_4 31, F1_5 10, F1_6 26, F2_2 1, F2_3 11, F2_5 1, F2_6 11, F2_7 1,
F2_8 1,341, F2_9 5,415, F2_10 2,123, F2_11 5,398, F3_1 1,077, F3_2 5,140, F3_3 5,390, F3_4 4, F3_6 10, F3_9 725,
F3_10 1,022, F3_11 5,426, F3_12 1,694, F4_2 1, F4_3 8, F4_4 16, F4_5 56, F4_10 11, F4_11 11, F4_12 11.
Diagnoses: section "Feature diagnoses" below (FD1-FD5 explain every mismatching column).

The earlier A build (c0271f430413, before mid_move) also agreed 0 / 0 on FH and on TB with common sigma
(runs lab_fh_r1, tb_common_sigma_r1, superseded).

## Diagnoses

No disagreement on real data so far, so no fix to route. Latent differences found by reading both codes (not
exercised on the 20 dates: the counts that would trigger them are 0 there; the record-level synthetic streams of
B4 exercise them on purpose):

- D1 (book driver, R record carrying F_MAYBE_BAD_BOOK): lab33._drive_book marks the book bad and then clears it on
  the R (mbo_book31.Book.clear resets bad), so the book after that R is GOOD; implB/labB_book.front_updates clears
  first and then marks bad, so the book stays BAD until the next R (READING LB-12). Protocol 0.3 says only "not
  marked bad (F_MAYBE_BAD_BOOK)"; mbo_book31's docstring: the flag marks the book bad "until the next R". Ambiguous
  for a flag on the R itself; the conservative reading is B's (the snapshot that carries the flag is not trusted).
  0 bad-flag records on the 20 dates (both sides' counts); the data facts count 7,630 F_MAYBE_BAD_BOOK records in Z1 over 39 months, but tests_b3/count_d1.py (02:56-02:58, all 816 dates, ZM front) finds 5,417 such records on 58 dates, 0 of them R records, 0 inside 08:35-13:20, and all 5,417 before the date's first R (the evening snapshot), so they never touch a started book: D1 cannot arise and no bad-book period reaches a label or a feature on the discovery dates (b4_runs/D1_counts.json, D1_counts_after_R.json). Ruled R-B3-D1 (B's reading) all the same.
- D2 (entry rule with a locked or crossed book at t on a date with no limit prices): lab33 R5-CROSSED fails the
  limit part only when limits exist, so with limits None an entry at a locked/crossed t is entry_ok (the row is
  still removed by p37_mid_t); implB LB-3 requires M_ZM(t) defined for entry_ok on every date. P3.6 entry text
  ("the ZM book at t has both sides and is not marked bad") is met by a locked book; P3.5/P3.8 then trade it.
  Conservative reading: B's (never enter on a book state 0.3 calls invalid). 0 such minutes on the 20 dates, and it cannot arise on real data: cal33 finds limit prices on all 816 dates (STATE 15:06, "limits None 0"), and with limits A fails the limit part on a locked/crossed book (R5-CROSSED), exactly as B does.
- D3 (F_TOB / F_MBP on MBO records): A marks the book bad (E.31 convention), B does not (LB-13). 0 such records in
  Z1 (data facts 1.5), so no effect on any date.
- D4 (records before the first R that carry F_LAST): A emits no update for them, B emits an invalid update ("not
  started"). Only the update count differs (2021-01-19: A 401,300 updates, B 401,355 F_LAST records, 58 records
  before the start on both); no as-of state inside 08:35-13:20 can differ because both books start at the evening
  snapshot.

## Feature diagnoses (run full_r1; every mismatching column is explained by FD1-FD5)

Method: the mismatch cells located by date and i (b3_runs/full_r1.md), then the two builders' per-mark raw
quantities compared directly over all 328 dates that both have built (A: features/c22b0a50f4cd/_p1/<D>.npz
reference arrays and cumulative counters; B: implB/dayraw/345ba20d4f97/<D>.npz), at the 279 marks 08:35-13:13.
Book and flow counts only (no outcome). Raw agreement over 328 dates x 279 marks = 91,512 marks: 15-minute ZM volume,
5- and 15-minute aggressor buy/sell volume and 5-minute sweeps differ only at 156 / 136 / 156 / 136 marks, all on the
early-close and late-open dates (FD1, FD2); sigma_ZM, ZS, ZL agree on all 20 dates.

| ID | Columns (cells) | Cause | Which side departs from the protocol | Fix owner |
|---|---|---|---|---|
| FD1 early closes | C_5 i >= 211 on 2021-01-19, 2021-01-25, 2022-12-13, 2022-12-22; the per-date normaliser (ratio constant within the date) of F2_8, F2_10, F3_1, F3_10, F3_12 and part of F2_9, F2_11, F3_2, F3_3 on the same 4 dates | A's open-time axis (feat33.axis; FA-1, FA-2) is the regular schedule on every date, so on the 4 early-close dates (2020-12-24, 2021-11-26, 2022-11-25, 2023-11-24; halt 12:05 CT) it treats 12:05-13:20 as open: windows ending after the halt are empty (V = 0, OFI = 0, no sweep, no trade interval). B (B-EARLY-1) maps a closed t to the last open minute before the halt. Raw evidence: V15, abs OFI_1, sweeps differ only on 2020-12-24 and 2022-11-25, at marks 211-278 (12:06-13:13). These marks enter the trailing 20-date references (Vbar per minute, Obar, sbar, rbar, lam60 median) of the 20 dates after each early close | A. P0.3 line 63: "the last k minutes of time during which X was open, ending at t" (X is not open after the halt; the parenthesis lists the regular closures only). B's reading is the literal one | Coder-A (FeatureCoder): build the axis per date from the actual session (data.group_session / the grains calendar), as B does |
| FD2 scheduled late opens | 2021-07-06 (itself, excluded date) i < k: C_12, C_13, C_14, F1_1, F1_2, F1_4, F1_5, F1_6, F2_2, F2_3, F2_5, F2_6, F2_7, F3_6, F4_2-F4_5, F4_10-F4_12, F3_12 (i 0-55); C_5 i 0-9 and the F2_10, F2_11, F3_12 normalisers on 2021-07-09 and 2021-07-29 | The same fixed axis: on a scheduled late open (2021-07-06, 2022-07-05, 2023-07-05, 2023-12-26, 2024-01-02: no overnight session) A's overnight marks are empty, so windows reaching before 08:30 are invalid (A = 0, flags 0); B (B-LATE-1) reaches the previous trade date's day session. Raw evidence: V15 differs at marks 0-9 and lam60 at marks 0-59 only on 2021-07-06. D itself is excluded (no row, no trade), but its marks enter the references of the next 20 dates | A, same line 63 (the last minutes during which X was open are the previous trade date's day session). F1 samples on the previous date still need D's segment (G2), which B applies | Coder-A, with FD1 |
| FD3 OFI terms at the pause junction and at invalid book states | F2_9, F2_11, F3_2, F3_3 on almost every row of every date (normaliser 1e-5 to 1e-2 relative, plus numerators at i < k); F3_4 at i = 0 on 4 dates; F2_8, F2_10 normaliser on 2022-09-01 | Two reading differences in the OFI terms e_n (F2.8, F3.1-F3.4). (a) The term of the first update after 08:30, whose predecessor is the last update of the 07:45-08:30 pause (the pre-open book, crossed or locked on the dates A measured): A (FA-6) computes it whenever both states are two-sided and not bad (crossed/locked allowed); B (B-OFI-1) sets it to 0 unless both states are valid books with bid < ask. Raw evidence: abs OFI_5 differs at mark 08:35 on 283 of 328 dates and abs OFI_15 at marks 08:35-08:45 on 283; abs OFI_1 never (no 1-minute window ending at or after 08:35 straddles the pause). (b) A term that cannot be computed (a side missing or a bad book): A makes the whole window invalid (no partial sums); B sets the term to 0 and keeps the window. Raw evidence: ZS abs OFI_1 differs at 10:58 and 11:01 on 2021-01-05, 2021-01-12 and 2022-08-12 (release days), which moves the k = 1 normalisers of the 20 dates after 2022-08-12 (2022-09-01 among the B3 dates) | Ambiguous; neither matches the most conservative reading. G3: "a feature that cannot be computed (... empty book side ...) takes the value 0" supports A's no-partial-sum rule (b) and is B's departure (a 0 term is an imputation). For (a), 0.3 skips the pause, so a term that compares the open book with a pause state carries pause information into the window (A), and B's 0 is an imputation. Most conservative reading: a term whose predecessor lies in skipped time, or either state not two-sided or bad, is not computable, and a window holding one is invalid (G3); the mark then leaves the trailing reference. Crossed or locked but two-sided states: the formula is defined (A literal); B's exclusion is the stricter reading | Lead decides (a) and (b) and whether crossed or locked states count; then Coder-A or Coder-B (or both) change |
| FD4 refills F3.11 | F3_11 on almost every row of every date (numerator and rbar) | A (FA-23) opens the 100 ms window at the book update (F_LAST) where an F3.10 sweep set leaves the PRE-TRADE touch level at 0 (one level per side per set; the emptying may include cancels in the batch). B (B-REFILL-1) opens it at the record whose fill-attributed reduction empties the CURRENT touch level (deeper levels that become the touch inside a sweep count; adds later in the same batch count; a level whose last lots are cancelled does not). Raw evidence: 15-minute refill counts differ at 42% (A < B) and 10% (A > B) of the 91,512 marks; window-sum totals bid A 8.56 M vs B 9.10 M, ask 7.89 M vs 8.39 M | A. F3.11: "an add at the same price and side within 100 ms (ts_recv) after that price level, while it was the touch, reached 0 displayed quantity through trades": the moment is the record at which the level reached 0, the level is the touch at that moment, the cause is fills. 0.3 makes only first-touch tests, locked-book checks and OFI sums step through book updates; F3.11 is not among them, and tying refills to F3.10's sweep sets is A's narrowing | Coder-A, or the lead rules |
| FD5 removals F3.9 | F3_9: 725 cells on all 20 dates, scattered rows | A (FA-11) keeps an order's unconsumed fill lots across event batches; B (B-FILL-1) clears the fill accumulator at every F_LAST. When a fill is followed by a modify that does not reduce the displayed size (an iceberg-style refresh: 1,472 cases on 2021-01-19), A keeps the lots pending and later uses them to absorb that order's voluntary cancels, which then do not count as removals. Raw evidence: A's 5-minute touch removals are lower at 8% of marks (Ca 6,963 marks, Cb 7,594) and higher at only 7 | A. F3.9: "fills are not removals (ProtocolReview DO-16)": a cancel in a later batch is not a fill. A's own measurement (every fill's book reduction comes in the fill's batch) supports clearing at the batch end | Coder-A |

Columns not listed agree on every row of every date: C_1-C_4, C_6-C_11, C_15, F1_3, F1_7, F1_8, F2_1, F2_4, F3_5,
F3_7, F3_8, F4_1, F4_6-F4_9, F4_13. NaN cells: 0 on both sides.

Labels and sigma need no fix. The open label readings are D1 (an R record carrying F_MAYBE_BAD_BOOK) and D2 (a locked
book at t on a date with no limits), both untriggered on real data, plus D5 (sigma undefined on a date that is not
excluded: A stops with LabelError, B skips TB on that date; on OOF dates it does not arise). The lead decides these
before the freeze. pipeline/tests_b4/test_lt4_labels_handbuilt.py holds xfail tests for D1 and D2 that pass once the
two readings agree.

## Rerun after the B3 rulings (INTERIM, 03:20 PDT)

Run feat_r2_partial (03:18): Coder-A features 6873427a6150 (FD1, FD2, FD3a, FD4, FD5, D1 applied; 10 of the 20 dates
built at 03:18: 2021-01-19 .. 2021-08-16) against Coder-B 7d28f22509b4 (FD3 (a)-(c) applied; 20 dates). 2,730 rows:
58 of 59 columns agree on every row (the OFI family, C_5, F1, F2, F3.9, F3.10, F3.12, F4 and the flags, including
2021-07-06 and the dates whose history holds 2020-12-24). Only F3_11 differs: 2,690 of 2,730 rows. sigma_ZM, ZS, ZL
agree. Labels against ff0181fc391c: 0 cells (run lab_r3).

| ID | Columns | Cause | Reading | Owner |
|---|---|---|---|---|
| FD6 refill depletion by a mixed record | F3_11 (normaliser rbar on every date, so almost every row; numerators at a few marks) | After the FD4 fix both sides open the 100 ms refill window at the record that empties the touch level through fills, but they differ when that one record removes fill lots AND a voluntary remainder (e.g. a cancel of an order whose filled part is still pending): Coder-A (feat33._removal) counts a depletion only when the record's whole reduction is fill lots (rest == 0); Coder-B (replayB.reduce) counts it when the reduction has any fill part (fill > 0). Measured: per-mark 15-minute refill counts over 195 dates x 279 marks: removals equal at every mark; refills A < B at 1,667 (bid) and 1,662 (ask) of 54,405 marks, never A > B; totals 4,846,824 vs 4,855,668 (bid). A direct replay of both rules on 2021-01-19: 8,636 vs 8,638 depletions, 2 of them B-only mixed records, 4,013 vs 4,014 refills | Ambiguous: F3.11 "reached 0 displayed quantity through trades"; R-B3-FD4 excludes "a level emptied by a cancel" but does not settle a single record that is part fill and part cancel. Literal reading: the level reached 0 through trades only if every lot that left with that record was filled (Coder-A's rest == 0); B's any-fill reading counts a level partly emptied by a cancel | Lead rules; then one side changes (a one-line condition: B `fill > 0` vs A `rest == 0`) |
