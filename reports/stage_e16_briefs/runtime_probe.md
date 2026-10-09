# Stage E.16 Task 3: runtime probe (synthetic stores at full 2010-2024 scale)

Synthetic data only: no market data was read. Stores written by `python -m base_rules.probe build` to ~/.cache/propexp_e16_probe/ (on disk, outside the repo; deleted afterwards), in the real ext2010 and step 2 layouts with the frozen read-only writer: 27 products, one-minute bars over every open interval of each product's calendars (the real hist2010 calendars before 2019-05-01, the real 2019-on calendars after; livestock 2010-2019 a PROVISIONAL stand-in, Task 3b's file not yet on disk), trade dates 2010-06-07..2019-04-30 and 2019-05-06..2024-02-29, a tick random walk, rolls at 00:00 UTC of estimated splice dates.

- Bars written: 117,460,015 rows; ext2010 files 887 MiB, step 2 files 483 MiB.
- Build: built in 248 s -> /home/kiros-li/.cache/propexp_e16_probe

Each test ran through the E.17 command line (`python -m base_rules.run run ...`: freeze check on a probe freeze in the lead's format, registration check on a temporary registry, run-once marker, the real settlement table, windows and EC-AUC inputs from the main tree), one process per test under `/usr/bin/time -v`, `nice -n 10`, products loaded one at a time; H5 combines H1..H4's result files.

| test | status | wall clock (time -v) | peak RSS (MiB) | units (base) |
|---|---|---|---|---|
| H1 | complete | 4:31.79 | 1201.4 | 3356 |
| H2 | complete | 0:22.66 | 1200.9 | 5 |
| H3 | complete | 0:44.86 | 1034.5 | 424 |
| H4 | complete | 4:24.67 | 1156.6 | 3354 |
| H5 | complete | 0:01.23 | 182.6 | 3356 |

Exclusions by reason on the synthetic stores (the synthetic random walk has no edge; counts show the calendars, the windows, the settlement table and the store checks at work):

- H1: {'after 15:08': 0, 'early halt': 2268, 'eligible': 67627, 'fill guard': 287, 'missing bar': 11143, 'no reference': 1934, 'not listed': 27, 'outside window': 5461, 'roll blackout': 5685, 'settlement unsourced': 1033, 'traded': 66223, 'warmup': 540, 'zero signal': 577}
- H2: {'early halt': 21, 'eligible': 25, 'leg traded': 10, 'leg warmup': 40, 'missing bar': 105, 'no reference': 2, 'outside window': 1, 'roll blackout': 11, 'traded': 5}
- H3: {'auction not a trade date': 20, 'early halt': 27, 'eligible': 504, 'outside window': 4, 'roll blackout': 105, 'same-tenor overlap': 7, 'store boundary': 2, 'traded': 424, 'warmup': 80, 'window end': 111}
- H4: {'after 15:08': 0, 'early halt': 2268, 'eligible': 67619, 'missing bar': 24, 'no cost bucket': 204, 'no reference': 13061, 'not listed': 27, 'outside window': 5461, 'roll blackout': 5685, 'settlement unsourced': 1033, 'traded': 63553, 'warmup': 540, 'zero signal': 3322}
- H5: {'grid dates': 3416, 'units': 3356, 'warmup': 60}

Memory at the end (free -m, Mem row): `Mem:           15118        7990        1893        1119        6168        7128`.

## Notes

- Totals: about 10 minutes for the four bar-reading tests run one after another (H1 4:32, H4 4:25,
  H3 0:45, H2 0:23) plus 1 s for H5; peak RSS 1.2 GiB per process (one product in memory at a
  time), against about 6-7 GiB available on the ThinkPad during the probe. Store build: 248 s.
  The real E.17 stores carry 16 columns where the loader reads 6; read time should be similar.
- The `verdict` command also ran on the probe results (Holm, pass bar, DSR at N = 476 from the
  temporary registry): every test FAILS on the synthetic random walk, as it must.
- `missing bar` 11,143 (H1) and `no reference` 13,061 (H4): equity S = 15:15 CT before
  2020-10-26 and grains S at the session close fall on the close-minute bar of a halted session,
  absent from the synthetic stores and flagged in_scheduled_closure in the real ones (README,
  open issues). H2 keeps 25 eligible months, 5 after warm-up, for the same reason.
- H4 `no cost bucket` 204: LE and HE O_p = 08:00 CT (2014-10-27..2016-02-28, days other than the
  week's first) puts H4's entry at 08:01, before the first D8 livestock bucket (08:30 CT); the
  unit is excluded (README, coder choice 11). A lead question.
- `fill guard` 287 (H1): FOMC instants (13:00 CT and 2010-2012 times) on livestock exits at
  13:00 and energy entries at 13:00 CT. The release-touch report finds FOMC the only release type
  touching an H fill minute in 2019-05..2024-02; it has 2010-2019 rows (E.14), so no conservative
  fallback minute is in force (`fallback_ct_minutes` empty in the results).
- The probe stores were deleted afterwards (`python -m base_rules.probe clean`).

## After the lead's rulings R-B1..R-B4 (01:2x PDT)

The probe above ran on the code before the rulings and was not rerun (lead instruction). The
rulings change no read path: R-B1 replaces a missing exit bar by the close of bar S-1 and adds
one reopening-bar lookup, R-B2 replaces an exclusion by a cost, R-B3 adds a pre-marker preflight
that hashes every store the test reads once more (the step that was already done per product
during the run) and moves the context build before the marker, R-B4 fixes the label. Expected
effect on wall time: the extra hashing (seconds per GB of store) and more units simulated in H1,
H4 and H2 (equity before 2020-10-26 and grains 2010-2015 now trade). The probe's leftover outputs
in ~/.cache/propexp_e16_probe were deleted.
