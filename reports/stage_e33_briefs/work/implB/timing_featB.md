# Implementation B feature builder: timing (FeatureCoder2, 2026-10-27)

All times PDT from `date` and the builder manifests (UTC ISO stamps converted). Machine: ThinkPad, 20 logical CPUs,
14 GB RAM; every run at nice 10, at most 3 worker processes, `free -m` checked before each run (available 8.8-10.4
GB).

## Measured

| Run | Code | Dates | Workers | Wall | Per day raw (s) | Features |
|---|---|---|---|---|---|---|
| Single day, profiled (2022-02-15) | dev | 1 raw | 1 | 11.0 s (of which ~8.5 s one-off manifest and sha checks in data33/guard33, once per process) | replay ~3-6 s | - |
| B3 dev build (old junction reading, superseded; outputs deleted 02:15 on 10-28) | c1faea3006da | 20 targets, 306 new raws (+22 cached) | 3 | 15:13:42-15:21:16 (7.6 min) | median 3.87, p90 6.88, max 12.47 (sum 1,328 s) | 8.6 s for 20 dates |
| One-date build (2023-04-10 + 21 history raws) | 345ba20d4f97 | 1 target, 22 raws | 3 | 45 s | - | <1 s |
| LT1-style truncation self-check, 4 times on 2023-04-10 | 345ba20d4f97 | 4 cutoff rebuilds | 1 | 35 s | ~6 s each (incl. process start) | 59/59 equal at each time |

| **Final B3 build** (DERIVED/implB, code 345ba20d4f97) | 345ba20d4f97 | 20 targets, 306 new raws (+22 cached) | 3 | 2026-10-28 02:02:09-02:12:45 (10.6 min) | median 5.38, p90 9.72, max 24.45 (sum 1,878 s) | 8.05 s for 20 dates |
| LT1-style truncation self-check, 5 more times (2021-07-06 i 0 and 150, 2021-01-19 i 3, 2022-12-22 i 272, 2024-02-15 i 61) | 345ba20d4f97 | 5 cutoff rebuilds | 1 | about 60 s | - | 59/59 equal at each time |

| FD3 rebuild (lead ruling FD3) | 7d28f22509b4 (superseded: cutoff-cache fix) | 20 targets, 328 raws | 2 | 02:46:52-03:06:18 (19.4 min) | median 6.1 | 26.2 s |
| FD3 rebuild, final | fb69badd4bb9 | 20 targets, 328 raws | 2 | 03:07:48-03:28:27 (20.7 min) | median 6.9 | 20.5 s |

The 2026-10-27 run was cut at about 15:27 PDT by the usage limit (no background job was running then); work resumed
02:02 PDT on 2026-10-28. The final build's per-raw times are about 40% above the dev build's on the same kind of
dates (load from other jobs is the likely cause; not examined).

## Where the time goes (one day raw)

- data33/guard33 one-off checks per process: discovery manifest sha256, E.31 Z1 marker sha256 (about 8.5 s, then
  cached for the process; the pool reuses each worker for many dates).
- ZM book replay (mbo_book31.Book in pure Python plus the F3 record-level bookkeeping and the 5-level state per
  F_LAST update): about 2-4 s for a median day (400-900k front records).
- Everything else (ZS/ZL MBP-1, as-of lookups, windows by cumulative sums, lam60's 279 lstsq fits, seasoned depth
  at 279 times): under 1 s.
- Features from 22 day raws (D and 21 history dates): about 0.4 s per date.

## Projection for the full build (lead's run)

816 day raws x 4.3-6.1 s mean / 3 workers = about 20-28 min, plus about 6 min of features (816 x 0.43 s, one
process), so about 26-35 min at 3 workers; peak memory about 0.5 GB per worker (day arrays plus the replay's
Python objects). Disk: about 190 KB per day raw (155 MB for 816) plus about 130 KB per feature parquet.
