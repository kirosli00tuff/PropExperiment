# Stage E.29: measured reference correlations, CL / ZM / GC / NQ front contracts

Reference only, never a model input (reports/stage_e29_model.md section 8). Facts only: no placement on the
model's rho grid here (the lead does that). Worker CorrMeasurer-OpusHigh, run 2026-10-21 19:27:49-19:27:53 PDT
(times from `date`). Script: reports/stage_e29_briefs/work/corr/corr_stats.py (nice 10, one process, 1.7 s);
tables rendered from E29_correlations.json by work/corr/write_md.py. Per-date daily series (front id, close,
high, low, main-session open/close, roll flag) are in work/corr/daily_<ROOT>.csv.

ZM is owned (data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0), so no soybean-complex substitute was used.

## Data rule and guards, as applied

- Files chosen by name only: <ROOT>_v_0/range=<a>_<b>.dbn.zst with a >= 2022-10-01 and b <= 2023-11-01
  (A0's rule: range=2023-10-01_2023-11-01 is the last file that may be opened; the 2022-10 file is opened only
  for the 2022-10-31 prior close and for trade date 2022-11-01's Sunday-evening bars). 13 files per root, 52 in
  all. No file dated 2023-11-01 or later was opened (the 2023-11 and 2023-12 files exist on disk and were
  skipped by name; the 2024-03+ gap is absent from the folders).
- open_store (copied from A0, extended) refuses before opening: a name outside that range, a root other than
  CL/ZM/GC/NQ, and any resolved path containing mbp-1, sealed, processed, holdout, embargo, research or /MES, or
  not under /ohlcv-1m/. Paths resolve to /mnt/large-storage/market_data/PropExperiment/... (the E.26 data move).
  None was refused; the 60-second missing-file retry never fired.
- Nothing written under data/. No network, no Databento API, no keys. Holdout status checked immediately before
  and after the run (bottom of this file): all_ok true and unlocks_logged 0 for holdout 1 (printed as `<top>`,
  the report's top-level keys) and for holdout_2 and each of its products, both times.

## Method

- Trade date (A0 copy): bar start in America/Chicago; at or after 17:00 CT it belongs to the next day; Saturday
  and Sunday roll to Monday. Window: trade dates 2022-11-01..2023-10-31.
- Front contract per trade date: within the v_0 series (Databento's volume-ranked continuous front), the
  instrument_id with the largest summed one-minute volume on that trade date (ties broken to the lower id).
  Only that instrument's bars are used for the day. The v_0 file holds one instrument per bar,
  so this is the highest-volume outright among the instruments the v_0 series carried that day, not a scan of
  every listed expiry. A roll date is a trade date whose front id differs from the previous owned trade
  date's; roll dates are dropped from returns, ranges and main-session returns.
- Daily close: close of the front contract's last bar of the trade date (not the CME settlement). Daily return:
  ln(close_t / close_prev) where prev is the previous kept trade date of that root, computed only when both days
  have the same front id (no return across a roll). The day after a roll uses the roll day's close of the same
  new contract. The return on 2022-11-01 uses the 2022-10-31 close.
- Daily range: (high - low) / close x 100 over all front-contract bars of the trade date (Globex day).
- Main-session return: ln(close of the last front bar starting before 13:00 PT / open of the first front bar
  starting at or after 06:30 PT) on the trade date. For ZM the session closes 11:20 PT, so its main session is
  06:30-11:20 PT (median 290 bars vs 390 for CL, GC, NQ).
- Calendars (A0 convention): primary tables exclude each root's EARLY_HALT dates (data/calendars/energy.py,
  grains.py, metals.py; data/cme_calendar.py for NQ) because the trade-date rule books holiday sessions on the
  holiday's own date. With a date excluded, the next day's return runs from the previous kept date. A variant
  with all trade dates kept is also given.
- Pairs: inner join on common trade dates with a value for both roots. Pearson (with a Fisher-z 95% interval,
  descriptive), and Spearman (Pearson of ranks). Six pairs.

## Notes of fact

- ZM's v_0 front id changed three times in December 2022 (2022-12-12, 12-14, 12-19), each dropped as a roll date.
- CL roll dates 2023-02-20 and 2023-06-19 are also early-halt dates (excluded in the primary tables either way).
- Dates with two or more instrument ids in the v_0 bars: CL 7, GC 5, NQ 4, ZM 0; on those days only the
  higher-volume id's bars are used.

## Tables, primary (early-halt dates excluded, A0 convention)

### Daily close-to-close log return (Globex day)

| Pair | Pearson | 95% CI (Fisher z) | Spearman | Days |
|---|---|---|---|---|
| CL-ZM | 0.1067 | -0.0221 to 0.2321 | 0.0940 | 233 |
| CL-GC | 0.1177 | -0.0110 to 0.2425 | 0.1468 | 233 |
| CL-NQ | 0.0883 | -0.0407 to 0.2144 | 0.1001 | 233 |
| ZM-GC | -0.0126 | -0.1395 to 0.1147 | 0.0128 | 238 |
| ZM-NQ | -0.0262 | -0.1526 to 0.1011 | 0.0372 | 239 |
| GC-NQ | 0.1591 | 0.0331 to 0.2801 | 0.0794 | 240 |

### Daily range (high - low) / close, % (Globex day)

| Pair | Pearson | 95% CI (Fisher z) | Spearman | Days |
|---|---|---|---|---|
| CL-ZM | 0.0384 | -0.0903 to 0.1659 | 0.0995 | 234 |
| CL-GC | 0.3954 | 0.2816 to 0.4981 | 0.3340 | 235 |
| CL-NQ | 0.1434 | 0.0157 to 0.2665 | 0.1954 | 235 |
| ZM-GC | 0.0188 | -0.1086 to 0.1456 | 0.0628 | 238 |
| ZM-NQ | 0.0478 | -0.0796 to 0.1736 | 0.0164 | 239 |
| GC-NQ | 0.3780 | 0.2640 to 0.4816 | 0.3194 | 240 |

### Main-session return, log(last close / first open) in 06:30-13:00 PT

| Pair | Pearson | 95% CI (Fisher z) | Spearman | Days |
|---|---|---|---|---|
| CL-ZM | 0.0882 | -0.0405 to 0.2140 | 0.1117 | 234 |
| CL-GC | 0.0919 | -0.0365 to 0.2173 | 0.1357 | 235 |
| CL-NQ | 0.0613 | -0.0672 to 0.1878 | 0.0418 | 235 |
| ZM-GC | -0.0155 | -0.1424 to 0.1119 | 0.0219 | 238 |
| ZM-NQ | 0.0205 | -0.1066 to 0.1471 | 0.0710 | 239 |
| GC-NQ | 0.1695 | 0.0438 to 0.2899 | 0.1762 | 240 |

## Tables, variant (all trade dates kept)

### Daily close-to-close log return (Globex day)

| Pair | Pearson | 95% CI (Fisher z) | Spearman | Days |
|---|---|---|---|---|
| CL-ZM | 0.1134 | -0.0148 to 0.2379 | 0.1036 | 235 |
| CL-GC | 0.1167 | -0.0098 to 0.2395 | 0.1506 | 241 |
| CL-NQ | 0.0949 | -0.0315 to 0.2184 | 0.1072 | 242 |
| ZM-GC | -0.0154 | -0.1421 to 0.1117 | 0.0122 | 239 |
| ZM-NQ | -0.0232 | -0.1491 to 0.1035 | 0.0411 | 241 |
| GC-NQ | 0.1579 | 0.0342 to 0.2768 | 0.0753 | 249 |

### Daily range (high - low) / close, % (Globex day)

| Pair | Pearson | 95% CI (Fisher z) | Spearman | Days |
|---|---|---|---|---|
| CL-ZM | 0.0347 | -0.0937 to 0.1619 | 0.0930 | 235 |
| CL-GC | 0.4081 | 0.2971 to 0.5083 | 0.3578 | 241 |
| CL-NQ | 0.1743 | 0.0493 to 0.2939 | 0.2297 | 242 |
| ZM-GC | 0.0212 | -0.1060 to 0.1477 | 0.0667 | 239 |
| ZM-NQ | 0.0275 | -0.0993 to 0.1533 | 0.0082 | 241 |
| GC-NQ | 0.4109 | 0.3020 to 0.5092 | 0.3679 | 249 |

### Main-session return, log(last close / first open) in 06:30-13:00 PT

| Pair | Pearson | 95% CI (Fisher z) | Spearman | Days |
|---|---|---|---|---|
| CL-ZM | 0.0882 | -0.0403 to 0.2137 | 0.1121 | 235 |
| CL-GC | 0.0857 | -0.0411 to 0.2098 | 0.1262 | 241 |
| CL-NQ | 0.0617 | -0.0649 to 0.1863 | 0.0417 | 242 |
| ZM-GC | -0.0156 | -0.1422 to 0.1115 | 0.0214 | 239 |
| ZM-NQ | 0.0207 | -0.1059 to 0.1467 | 0.0716 | 241 |
| GC-NQ | 0.1693 | 0.0459 to 0.2875 | 0.1707 | 249 |

## Per-root facts (primary)

| Root | Group calendar | Trade dates in window | Roll dates (dropped) | Front ids | Dates with 2+ ids | Early-halt dates excluded | n ret | n range | n main ret | SD daily ret | Median range % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CL | data.calendars.energy | 258 | 2022-11-21, 2022-12-19, 2023-01-20, 2023-02-20, 2023-03-20, 2023-04-19, 2023-05-22, 2023-06-19, 2023-07-19, 2023-08-21, 2023-09-18, 2023-10-19 | 13 | 7 | 2022-11-24, 2022-11-25, 2023-01-16, 2023-02-20, 2023-05-29, 2023-06-19, 2023-07-04, 2023-09-04 | 238 | 240 | 240 | 0.0220 | 3.05 |
| ZM | data.calendars.grains | 251 | 2022-11-23, 2022-12-12, 2022-12-14, 2022-12-19, 2023-02-21, 2023-04-17, 2023-06-22 | 6 | 0 | 2022-11-25 | 243 | 243 | 243 | 0.0159 | 2.18 |
| GC | data.calendars.metals | 258 | 2022-12-01, 2023-02-01, 2023-03-31, 2023-06-01, 2023-07-31 | 6 | 5 | 2022-11-24, 2022-11-25, 2023-01-16, 2023-02-20, 2023-05-29, 2023-06-19, 2023-07-04, 2023-09-04 | 245 | 245 | 245 | 0.0090 | 1.16 |
| NQ | data.cme_calendar | 259 | 2022-12-14, 2023-03-15, 2023-06-14, 2023-09-13 | 5 | 4 | 2022-11-24, 2022-11-25, 2023-01-16, 2023-02-20, 2023-04-07, 2023-05-29, 2023-06-19, 2023-07-03, 2023-07-04, 2023-09-04 | 245 | 245 | 245 | 0.0134 | 1.81 |

All-dates variant counts: CL n ret 246, n range 246, n main 246; ZM n ret 244, n range 244, n main 244; GC n ret 253, n range 253, n main 253; NQ n ret 255, n range 255, n main 254.

## Files opened (52; every one passed open_store's name and resolved-path guard)

| Root | File (range=start_end) | Rows |
|---|---|---|
| CL | 2022-10-01_2022-11-01 | 28929 |
| CL | 2022-11-01_2022-12-01 | 29532 |
| CL | 2022-12-01_2023-01-01 | 28769 |
| CL | 2023-01-01_2023-02-01 | 28278 |
| CL | 2023-02-01_2023-03-01 | 27235 |
| CL | 2023-03-01_2023-04-01 | 31528 |
| CL | 2023-04-01_2023-05-01 | 26017 |
| CL | 2023-05-01_2023-06-01 | 30867 |
| CL | 2023-06-01_2023-07-01 | 29649 |
| CL | 2023-07-01_2023-08-01 | 28591 |
| CL | 2023-08-01_2023-09-01 | 31443 |
| CL | 2023-09-01_2023-10-01 | 28532 |
| CL | 2023-10-01_2023-11-01 | 30130 |
| ZM | 2022-10-01_2022-11-01 | 16769 |
| ZM | 2022-11-01_2022-12-01 | 14984 |
| ZM | 2022-12-01_2023-01-01 | 15532 |
| ZM | 2023-01-01_2023-02-01 | 16110 |
| ZM | 2023-02-01_2023-03-01 | 15595 |
| ZM | 2023-03-01_2023-04-01 | 19839 |
| ZM | 2023-04-01_2023-05-01 | 15511 |
| ZM | 2023-05-01_2023-06-01 | 18817 |
| ZM | 2023-06-01_2023-07-01 | 18069 |
| ZM | 2023-07-01_2023-08-01 | 16808 |
| ZM | 2023-08-01_2023-09-01 | 19339 |
| ZM | 2023-09-01_2023-10-01 | 16150 |
| ZM | 2023-10-01_2023-11-01 | 19038 |
| GC | 2022-10-01_2022-11-01 | 29057 |
| GC | 2022-11-01_2022-12-01 | 28189 |
| GC | 2022-12-01_2023-01-01 | 28871 |
| GC | 2023-01-01_2023-02-01 | 27272 |
| GC | 2023-02-01_2023-03-01 | 27408 |
| GC | 2023-03-01_2023-04-01 | 30775 |
| GC | 2023-04-01_2023-05-01 | 26289 |
| GC | 2023-05-01_2023-06-01 | 29381 |
| GC | 2023-06-01_2023-07-01 | 30008 |
| GC | 2023-07-01_2023-08-01 | 28312 |
| GC | 2023-08-01_2023-09-01 | 31549 |
| GC | 2023-09-01_2023-10-01 | 28481 |
| GC | 2023-10-01_2023-11-01 | 30389 |
| NQ | 2022-10-01_2022-11-01 | 29099 |
| NQ | 2022-11-01_2022-12-01 | 29831 |
| NQ | 2022-12-01_2023-01-01 | 28915 |
| NQ | 2023-01-01_2023-02-01 | 28796 |
| NQ | 2023-02-01_2023-03-01 | 27356 |
| NQ | 2023-03-01_2023-04-01 | 31675 |
| NQ | 2023-04-01_2023-05-01 | 27249 |
| NQ | 2023-05-01_2023-06-01 | 31497 |
| NQ | 2023-06-01_2023-07-01 | 29977 |
| NQ | 2023-07-01_2023-08-01 | 28629 |
| NQ | 2023-08-01_2023-09-01 | 31738 |
| NQ | 2023-09-01_2023-10-01 | 28592 |
| NQ | 2023-10-01_2023-11-01 | 30480 |

Resolved directory for every file: /mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/ohlcv-1m/CL_v_0, /mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/ohlcv-1m/GC_v_0, /mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/ohlcv-1m/NQ_v_0, /mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0.

## Holdout status (`uv run python -m data.holdout status`, keys all_ok and unlocks_logged only)

Before the data read:

```
2026-10-21 19:27:49 PDT
<top>: {"all_ok": true, "unlocks_logged": 0}
holdout_2: {"all_ok": true, "unlocks_logged": 0}
holdout_2.products.MCL: {"all_ok": true, "unlocks_logged": 0}
holdout_2.products.MGC: {"all_ok": true, "unlocks_logged": 0}
holdout_2.products.MHG: {"all_ok": true, "unlocks_logged": 0}
holdout_2.products.NG: {"all_ok": true, "unlocks_logged": 0}
```

After the data read:

```
2026-10-21 19:27:53 PDT
<top>: {"all_ok": true, "unlocks_logged": 0}
holdout_2: {"all_ok": true, "unlocks_logged": 0}
holdout_2.products.MCL: {"all_ok": true, "unlocks_logged": 0}
holdout_2.products.MGC: {"all_ok": true, "unlocks_logged": 0}
holdout_2.products.MHG: {"all_ok": true, "unlocks_logged": 0}
holdout_2.products.NG: {"all_ok": true, "unlocks_logged": 0}
```

