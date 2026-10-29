# Fold timing summary (E.33c, FoldTimes-HaikuMed)

Source: reports/stage_e33_briefs/work/logs/search_real.log (965 lines).

- Total rows: 448
- Rows with status `cut`: 8
- Rows with status `done`: 440
- Rows with more than one done line: 0

## Seconds per (set, model), done rows only

| set | model | count done | sum | mean | min | max |
|---|---|---|---|---|---|---|
| S1 | LOGIT | 56 | 2124.0 | 37.9 | 2.2 | 230.0 |
| S1 | LGBM | 24 | 48.9 | 2.0 | 1.3 | 2.7 |
| S5 | LOGIT | 216 | 23602.7 | 109.3 | 6.0 | 654.2 |
| S5 | LGBM | 144 | 721.8 | 5.0 | 1.9 | 14.2 |

## Finalized lines

- `finalized (failed)`: 0
- `finalized (ok)`: 72

## Collector window lines

- line 732 at 2026-10-28 15:34:05,310: `2026-10-28 15:34:05,310 INFO collector window 15:30-16:00 PT: pausing submissions`
- line 733 at 2026-10-28 16:00:05,331: `2026-10-28 16:00:05,331 INFO collector window over: resuming`

## Header lines (matched the brief's header formats)

- line 1: 2026-10-28 14:29:03,603 INFO registration checked for 300 ids
- line 2: 2026-10-28 14:29:04,022 INFO manifest {"argv": ["reports/stage_e33_briefs/work/pipeline/run_search33
- line 3: 2026-10-28 14:29:04,101 INFO 1800 fold tasks to run (300 configs)

## Timing anchors

- First start line timestamp: 2026-10-28 14:29:04,106
- Last non-empty line 965: `2026-10-28 16:08:07,494 INFO start E33-S1F30L100A fold 4 (1 thr; pid 2625976; 7991 MB available)`

## Done lines with no matching start line

- Count: 0

## Unmatched lines (matched no format)

- Count: 0

