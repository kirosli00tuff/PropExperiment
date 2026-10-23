# Stage E.31 Part 1: independent verification of the QM and ZM volume verdicts

Verifier: VolumeVerifier-FableXHigh (worker-xhigh, fable). Run 2026-10-22; first calculation saved 08:09:15 PDT, report written about 08:13 PDT (file mtimes and date).
Brief: reports/stage_e31_briefs/brief_volverify.md. No network, no Databento call, no key, no commit, no edit to any producer file.

## Overall result

**CONFIRMED for every verdict number.** My independent recomputation (written from the frozen request alone, run, saved to
verify_numbers.json at 08:09:15 PDT, before I opened any producer output) agrees exactly with the producer on all
442 compared quantities in vol_measures.json (442 match, 0 differ), and on all 64 rows of the four quarter tables in
reports/stage_e31_volume.md. No numeric discrepancy. Two definitional notes, no defect that changes a number (see the code audit).

## Order of work and inputs checked

1. Read reports/stage_e31_volume_request.md only. sha256 = 09d83f433f2869aab4e26670c455266dd597a6a32673a9c367a846bdf5939b9e: matches the frozen value.
2. DBN file named in vol_purchase_manifest.json (fields path and sha256 only): sha256sum = 9dbd86f5375e8461c153fe0d0d85e7469b18f71e8e87ab3e8501f7060cf77fef,
   equal to the manifest value. File read-only, mtime 08:00:05 PDT, unchanged at the end.
3. Wrote verify_vol_calc.py (main) and xcheck_pandas.py (second implementation of the headline medians), ran both. The two agree with each other.
4. Only then opened vol_measures.json, stage_e31_volume.md and vol_measure.py. compare.py and compare_md.py do the comparison.

Data facts (mine): 73,166 bars; dataset GLBX.MDP3, schema ohlcv-1d; metadata start 2023-01-01, end 2026-10-22T00:00:00Z (exclusive,
no time part); first bar 2023-01-02, last bar 2026-10-21; every ts_event is exactly 00:00:00 UTC (so the UTC date is the bar date);
no duplicate (instrument, day) bars; no zero or negative volume; no bar with a root other than QM or ZM.

## Verdict numbers: mine vs producer

| Quantity | Mine | Producer | Status |
|---|---:|---:|---|
| Window (last 12 full months before exclusive end 2026-10-22) | 2025-10-01 to 2026-09-30 | 2025-10-01 to 2026-09-30 | CONFIRMED |
| Window universe days, primary | 260 | 260 | CONFIRMED |
| Window own days, QM / ZM | 260 / 251 | 260 / 251 | CONFIRMED |
| Weekdays in window / weekday not in universe | 261 / ['2026-04-03'] | (not reported by producer) | not reported by producer |
| Zero-filled days, QM / ZM | 0 / 9 | 0 / 9 | CONFIRMED |
| QM median, primary universe | 4,480.5 | 4,480.5 | CONFIRMED |
| QM verdict (below 1,000 = FAIL), primary | PASS | PASS | CONFIRMED |
| QM median, own universe | 4,480.5 | 4,480.5 | CONFIRMED |
| QM verdict, own | PASS | PASS | CONFIRMED |
| ZM median, primary universe | 78,281.5 | 78,281.5 | CONFIRMED |
| ZM verdict (below 5,000 = FAIL), primary | PASS | PASS | CONFIRMED |
| ZM median, own universe | 79,512.0 | 79,512.0 | CONFIRMED |
| ZM verdict, own | PASS | PASS | CONFIRMED |
| Primary vs own verdicts differ? | no / no | False / False | CONFIRMED |
| Window P10, QM / ZM (primary) | 2,105.5 / 53,514.2 | 2,105.5 / 53,514.2 | CONFIRMED |
| Window volume, QM / ZM | 1,849,614 / 20,846,749 | 1,849,614 / 20,846,749 | CONFIRMED |

The weekday-count row is a quantity the producer does not report (Good Friday 2026-04-03 is the one weekday with no QM or ZM bar); it is not a discrepancy.
Margins: QM median is 4.5 times its 1,000 threshold, ZM median 15.7 times its 5,000 threshold.

Verdict conclusions: QM = PASS (the frozen E.28 QM pilot is not closed by the volume rule); ZM = PASS (Part 4 is not stopped by the volume rule).
Both verdicts CONFIRMED.

## Universe, filters and counts: mine vs producer

| Quantity | Mine | Producer | Status |
|---|---:|---:|---|
| Universe days whole span: primary / QM own / ZM own | 989 / 989 / 955 | 989 / 989 / 955 | CONFIRMED |
| Instruments with bars, QM / ZM | 434 / 491 | 434 / 491 | CONFIRMED |
| Outrights kept, QM / ZM | 58 / 56 | 58 / 56 | CONFIRMED |
| Hyphen-dropped symbols, QM / ZM | 376 / 435 | 376 / 435 | CONFIRMED |
| Hyphen-dropped bars, QM / ZM | 6,759 / 45,819 | 6,759 / 45,819 | CONFIRMED |
| Hyphen-dropped volume, QM / ZM | 239,698 / 47,168,442 | 239,698 / 47,168,442 | CONFIRMED |
| Weekend outright bars, QM / ZM (Sat / Sun split mine: QM 0 / 826, ZM 0 / 0) | 826 / 0 | 826 / 0 | CONFIRMED |
| Weekend outright volume, QM / ZM | 78,857 / 0 | 78,857 / 0 | CONFIRMED |
| Bars with neither root | 0 | 0 | CONFIRMED |
| Check line (regex non-matching outrights): bars QM / ZM | 0 / 28 | 0 / 28 | CONFIRMED |
| Check line volume QM / ZM | 0 / 424 | 0 / 424 | CONFIRMED |
| Check line ZM symbols (8, all 'ZM:CF ...') | 8 | 8 | CONFIRMED |
| Check line ZM share of root weekday outright volume | 5.573e-06 | 5.573e-06 | CONFIRMED |
| Above 1% for either root? | no / no | False / False | CONFIRMED |
| Last quarter partial (days), primary | 2026Q4, 15 days | ('2026Q4', 15) | CONFIRMED |

Definitional note 1 (not a difference in any verdict figure): the producer's check-line `root_volume` for QM is 8,844,728, mine is 8,923,585.
The gap is exactly the 78,857 contracts of QM Sunday-dated outright bars (8,923,585 - 78,857 = 8,844,728). The producer's denominator is weekday outright volume,
mine is all outright volume; for ZM both are 76,082,523. The share stays 0.000% for QM and 0.0006% for ZM; neither is near the 1% trigger.
Definitional note 2: the producer applies the hyphen filter before the weekend drop, so its 'weekend bars' are outright-only (QM 826). Counting spreads too,
QM Sunday-dated bars would be 1,337 (volume 85,849); ZM has none either way. The producer's label says 'outright', so this is consistent with its own wording and with the request.

## Per-quarter tables: mine

Compared with the producer's quarters_primary and quarters_own (both roots, 16 quarters each): days, median, P10, total volume, front-month share and
top-volume share all match to the stored float precision (relative tolerance 1e-12 on P10 and the shares, exact on integers and medians); the rendered
tables in stage_e31_volume.md match my numbers at the printed precision on all 64 rows (compare_md.py).

### QM (primary-universe columns first, own-universe columns beside)

| Quarter | Days (primary) | Median | P10 | Days (own) | Median (own) | P10 (own) | Front-month share | Top-volume share (info) | Volume |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023Q1 | 65 | 14,632.0 | 11,947.0 | 65 | 14,632.0 | 11,947.0 | 0.845 | 0.923 | 991,036 |
| 2023Q2 | 64 | 15,008.5 | 11,813.8 | 64 | 15,008.5 | 11,813.8 | 0.845 | 0.912 | 983,679 |
| 2023Q3 | 65 | 11,823.0 | 8,835.6 | 65 | 11,823.0 | 8,835.6 | 0.795 | 0.881 | 772,064 |
| 2023Q4 | 65 | 12,862.0 | 9,247.0 | 65 | 12,862.0 | 9,247.0 | 0.805 | 0.891 | 820,729 |
| 2024Q1 | 64 | 9,968.0 | 7,880.2 | 64 | 9,968.0 | 7,880.2 | 0.814 | 0.890 | 650,616 |
| 2024Q2 | 65 | 9,804.0 | 6,677.8 | 65 | 9,804.0 | 6,677.8 | 0.784 | 0.869 | 614,344 |
| 2024Q3 | 66 | 8,079.0 | 6,105.5 | 66 | 8,079.0 | 6,105.5 | 0.767 | 0.850 | 546,918 |
| 2024Q4 | 66 | 6,899.5 | 4,362.0 | 66 | 6,899.5 | 4,362.0 | 0.784 | 0.846 | 495,020 |
| 2025Q1 | 64 | 5,174.0 | 3,656.6 | 64 | 5,174.0 | 3,656.6 | 0.790 | 0.873 | 360,921 |
| 2025Q2 | 64 | 4,563.5 | 3,505.2 | 64 | 4,563.5 | 3,505.2 | 0.742 | 0.809 | 447,017 |
| 2025Q3 | 66 | 3,180.5 | 2,332.5 | 66 | 3,180.5 | 2,332.5 | 0.808 | 0.879 | 218,558 |
| 2025Q4 | 66 | 2,859.0 | 1,604.5 | 66 | 2,859.0 | 1,604.5 | 0.823 | 0.899 | 195,933 |
| 2026Q1 | 64 | 4,285.5 | 2,650.0 | 64 | 4,285.5 | 2,650.0 | 0.818 | 0.913 | 749,134 |
| 2026Q2 | 64 | 7,414.5 | 3,817.9 | 64 | 7,414.5 | 3,817.9 | 0.857 | 0.925 | 563,066 |
| 2026Q3 | 66 | 4,804.0 | 2,862.5 | 66 | 4,804.0 | 2,862.5 | 0.832 | 0.892 | 341,481 |
| 2026Q4 (partial) | 15 | 5,838.0 | 5,024.6 | 15 | 5,838.0 | 5,024.6 | 0.796 | 0.889 | 94,212 |

### ZM

| Quarter | Days (primary) | Median | P10 | Days (own) | Median (own) | P10 (own) | Front-month share | Top-volume share (info) | Volume |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023Q1 | 65 | 60,401.0 | 48,366.0 | 62 | 60,994.5 | 49,028.2 | 0.381 | 0.624 | 3,922,860 |
| 2023Q2 | 64 | 72,274.0 | 54,516.9 | 62 | 74,200.0 | 57,686.6 | 0.343 | 0.550 | 4,707,218 |
| 2023Q3 | 65 | 61,824.0 | 50,093.0 | 63 | 61,981.0 | 51,548.2 | 0.077 | 0.564 | 3,979,415 |
| 2023Q4 | 65 | 83,427.0 | 56,229.4 | 63 | 84,120.0 | 58,648.0 | 0.301 | 0.514 | 5,164,885 |
| 2024Q1 | 64 | 76,823.5 | 61,627.7 | 61 | 78,401.0 | 63,151.0 | 0.336 | 0.565 | 4,956,465 |
| 2024Q2 | 65 | 88,178.0 | 67,196.8 | 63 | 89,032.0 | 69,046.8 | 0.349 | 0.571 | 5,777,626 |
| 2024Q3 | 66 | 78,209.0 | 57,847.0 | 64 | 79,036.5 | 58,709.1 | 0.071 | 0.545 | 5,241,094 |
| 2024Q4 | 66 | 79,963.5 | 56,002.0 | 64 | 80,653.0 | 60,660.2 | 0.260 | 0.515 | 5,268,148 |
| 2025Q1 | 64 | 76,056.0 | 53,122.8 | 61 | 76,806.0 | 60,584.0 | 0.369 | 0.600 | 4,710,546 |
| 2025Q2 | 64 | 74,492.5 | 57,768.0 | 62 | 75,179.0 | 59,637.7 | 0.382 | 0.526 | 4,971,077 |
| 2025Q3 | 66 | 74,914.5 | 55,142.0 | 64 | 75,646.5 | 57,230.7 | 0.104 | 0.509 | 5,067,838 |
| 2025Q4 | 66 | 74,468.5 | 46,327.0 | 64 | 74,802.0 | 50,284.5 | 0.341 | 0.548 | 5,182,639 |
| 2026Q1 | 64 | 83,222.0 | 60,626.7 | 61 | 83,305.0 | 62,928.0 | 0.375 | 0.601 | 5,376,718 |
| 2026Q2 | 64 | 76,517.0 | 58,517.6 | 62 | 77,152.0 | 59,966.0 | 0.367 | 0.530 | 5,072,277 |
| 2026Q3 | 66 | 78,281.5 | 54,515.5 | 64 | 78,379.0 | 56,667.9 | 0.080 | 0.538 | 5,215,115 |
| 2026Q4 (partial) | 15 | 96,021.0 | 80,556.0 | 15 | 96,021.0 | 80,556.0 | 0.240 | 0.644 | 1,468,602 |

## Instrument-id to symbol resolution

- DBN mappings: 5994 raw symbols, 5994 distinct instrument ids; 925 ids carry bars in this file.
- 4 ids are reused across different raw symbols over time (42014428, 42020970, 42067754, 42068559; each has two non-overlapping intervals).
  **None of the four has a bar in the file** (records of reused ids: 0), so id reuse cannot affect any figure here. A naive last-symbol map would also misname 0 records.
- I resolved every bar by date interval [start_date, end_date) (Databento's end is exclusive): 73,166 of 73,166 bars resolve to exactly one symbol; 0 unresolved, 0 ambiguous.
  The closed-interval variant gives the same names on every bar (0 differences).
- Direct check of the producer's `symbol_for` (imported read-only, xcheck_symbols.py): 0 differences from my resolution on all 73,166 bars.

## Price-use audit

- My scripts: `ts_event`, `instrument_id`, `volume` and `metadata.mappings` only; a grep for open/high/low/close/price finds only the builtin `open`, the word 'closed' in interval-variant names, and one comment saying no price is used.
- Producer `vol_measure.py`: `load_dbn` takes the three columns from `to_ndarray()` and deletes the array at once; no other column is referenced anywhere (grep of the file for
  `["open"|"high"|"low"|"close"]` and `.open/.high/.low/.close` finds nothing). `to_ndarray()` does load the price columns into memory briefly, as mine does; they are never read.
- `vol_measures.json`: recursive key scan shows no price key. `stage_e31_volume.md`: the only word match is the sentence 'no prices'. **Audit passed.**

## Code audit of vol_measure.py (defects and risks)

No defect that changes a number. Items, most relevant first:

1. `symbol_for` returns `entries[0][2]` without any date check whenever an instrument id has only one raw name (lines 100-102). A bar dated outside that id's mapping interval would be named silently.
   Effect here: none. My strict half-open check finds 0 bars outside their interval. Risk class: silent, low.
2. `symbol_for` falls back from the half-open to the closed interval (lines 106-108). For a reused id on the exclusive-end day it returns the old symbol (shown: id 42014428 on 2024-02-25 returns QMH4-QMH9, where the half-open rule finds no symbol).
   In a gap day it raises MeasureError, which is the right stop. Effect here: none, because no reused id has a bar.
3. The 28 ZM bars with symbols like 'ZM:CF F5H5K5N5' (colon-notation condor spreads, 424 contracts in total) are not hyphen symbols, so the request keeps them in the ZM daily volume (the check line is a check, not a filter).
   The producer does exactly this; they cannot enter the front-month pick (no regex match) but can enter the top-volume maximum. Effect: ZM window median is 78,281.5 with or without them (my sensitivity run).
4. `verdict()` returns FAIL for a None median (empty window): conservative, correct.
5. `window_from_end` is equivalent to my month-walk for every exclusive end; tested against mine on every midnight-UTC end date from 2024-01-01 to 2027-12-31 (1,461 dates, 0 differences; xcheck_window.py).
6. The `partial` flag marks the last quarter of every table unconditionally; correct here (2026Q4 has 15 days), would mislabel a full last quarter.
7. Front-month ties (two symbols with the same delivery key on a date) would be resolved by `min` order; there are 0 tie days in this data (mine).

## Sensitivity of the verdicts (extra, not requested; sens.py)

| Variant | QM median | ZM median |
|---|---:|---:|
| Rule as frozen (primary universe) | 4,480.5 | 78,281.5 |
| Without ZM colon spreads | 4,480.5 | 78,281.5 |
| Sunday bars folded into the next Monday | 4,518.5 | 78,281.5 |
| Hyphen spreads included (not the rule) | 4,689.5 | 127,148.0 |

Lowest single-quarter median in 2023-2026: QM 2,859.0 (2025Q4), ZM 60,401.0 (2023Q1). Lowest month-of-window median: QM 1,809.0, ZM 64,842.0.
Every variant is above both thresholds, so the verdicts do not depend on a definitional choice.

## Invariants

- Holdout: `unlocks_logged` 0 at start and 0 at end; all_ok true both times.
- No network or Databento call, no key read, no TopstepX call; no other data file opened; no commit. REGISTRATION.md not touched.
- Producer files unchanged (mtimes 08:05 and 08:06 PDT, before my first run). Importing vol_measure.py left its existing __pycache__ entry (08:06:07) as it was.
- Files I wrote, all in reports/stage_e31_briefs/work/verify_vol/: verify_vol_calc.py, verify_numbers.json, xcheck_pandas.py, probe_meta.py, compare.py, compare_rows.json,
  compare_md.py, xcheck_symbols.py, xcheck_window.py, sens.py, make_report.py, VERIFY_volume.md.
