Three worker spawns, all on Opus 5.5 (Fable is not on the Pro plan); at most two ran at once. Times are PDT from
the transcripts and log files; tokens are each transcript's usage sums (input + output + cache read + cache
creation), from reports/stage_e10_briefs/cost.py.

| step | owner | agent file / model / effort | start to end | tokens | status |
|---|---|---|---|---|---|
| Plan, briefs (coder, correlations, review), Z3 declaration | lead | - / Opus 5.5 / high | 10-21 19:19 to 19:26 (declaration mtime 19:24:16) | in lead total | done |
| Measured correlations (reference) | CorrMeasurer-OpusHigh | worker-high / opus / high | 19:25:55 to 19:28:58 | 1,514,154 | done: E29_correlations.md/.json |
| Basket module, runner, tests, tables script | BasketCoder-OpusXHigh | worker-xhigh / opus / xhigh | 19:25:51 to 19:37:04; resumed by SendMessage 21:54:37 to 22:02:15 (last record 22:12:15) | 8,094,423 | partial: cut twice by usage limits. On disk: e29_basket.py, e29_run.py, e29_tables.py, 9 tests passing (21:57), LOG.md C1 to C9 |
| Grid run, first launch (coder) | detached, 6 processes, nice 10 | - | 21:59:32 to 22:21 (killed by reboot at 139 records) | - | resumed below |
| Grid run, restart (OC-12) | lead, one detached command | - | 10-22 02:41 to 02:51:55 (rc 0; 96 run, 139 kept) | - | done: 228 cells + 7 alone, 0 missing |
| Collect, tables, final tests | lead | - | 02:51 to 02:53 | - | done: E29_cells.json, E29_tables.md, 11 passed |
| Independent review (Z5) | BasketReviewer-OpusXHigh | worker-xhigh / opus / xhigh, fresh context | 02:53:26 to 03:13:06 | 8,589,743 | done: R_review.md, GO WITH FIXES |
| Synthesis drafts (answers, compact tables, OC, decisions) | lead | - / Opus 5.5 / high | 02:54 to 03:15 | in lead total | done |
| Grid confirmation of the other 211 records (SHOULD FIX 7) | lead, one detached command, 6 processes (OC-17) | - | 03:13 to 04:19 (rc 0) | - | done: 0 of 470 moved |
| Vanish table (SHOULD FIX 8), return, end checks, suite, commit | lead | - / Opus 5.5 / high | 04:19 to end (section 8) | in lead total | done |

The lead kept the declaration, the reading of the results (sections 3.3 to 3.5), the open choices and the decisions
for itself. The grid restart and the confirmation pass were single mechanical commands. The lead ran them itself
instead of spawning a worker (25k to 35k tokens of setup each), and the coder was still blocked by the usage limit
at the time of the restart.
