# Brief: FoldTimes-HaikuMed (Stage E.33c, S2 input; pure extraction)

Objective (one): parse the search log reports/stage_e33_briefs/work/logs/search_real.log (965 lines) into a
per-fold timing table. Pure extraction: no interpretation, no projection, no conclusion.

Input (the only file you may read): /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e33_briefs/work/logs/search_real.log

Line formats (timestamp prefix `YYYY-MM-DD HH:MM:SS,mmm LEVEL `):
- `start E33-S5F15L001A fold 1 (1 thr; pid 2625975; 12034 MB available)`
- `E33-S5F15L001A fold 4 done 17.6 s`
- `E33-S5F15L001A finalized (ok) in 13.9 s`
- `collector window 15:30-16:00 PT: pausing submissions` and `collector window over: resuming`
- a few header lines (registration checked, manifest, fold tasks to run).
Config id grammar: `E33-<set><label><grid>`: set S1..S5; label F05, F15, F30, F60, T15 or T30; grid L001A, L001E,
L010A, L010E, L100A, L100E (model LOGIT) or G2050, G2200, G3050, G3200 (model LGBM).

Outputs (create the folder reports/stage_e33c_briefs/fold_times/):
1. parse_fold_times.py: stdlib-only Python, run as `python3 -I parse_fold_times.py <log> <outdir>`; it writes 2 and 3.
2. fold_times_real.csv, one row per (config, fold) with at least one start line, sorted by first start time. Columns:
   config_id, set, label, model (LOGIT or LGBM), grid, fold, n_starts, first_start, last_start, start_line (log line
   number of the last start), done_time, done_line, seconds (the number on the done line), status (`done` if a done
   line exists, else `cut`). Empty cells for missing values. Times exactly as in the log.
3. fold_times_summary.md: total rows; rows by status; per (set, model): count done, sum, mean, min, max of seconds
   (1 decimal); the count of `finalized (ok)` and `finalized (failed)` lines; the two collector-window lines with their
   timestamps and line numbers; the first start line's timestamp; the last line's timestamp and text; every line that
   matches none of the formats above (line number and its first 100 characters). Report the counts you find; do not
   adjust anything to match an expectation.

Boundaries:
- Read only the log above. Do not open, list or stat anything under /mnt/large-storage/market_data/PropExperiment/
  derived/e33/ (outcome seal). Edit no other file. No web, no agents, no git.
- Do not end your turn while a job of yours is still running.
- Return: the three paths, the row counts by status, and at most 150 words. Say plainly anything you could not do.
