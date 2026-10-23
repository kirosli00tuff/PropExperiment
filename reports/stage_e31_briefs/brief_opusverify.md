# Brief: OpusVerifier-OpusXHigh (worker-xhigh, model opus, fresh context: the V46 item 5 Pro substitute) - independent check of the E.31 kill-rule numbers

Objective (one): independently verify every number that enters the ZM pilot verdict (spec v2 section 7: K1 under the
dropping and the no-drop variant, K2, K3) and the gate model's fills, without using the producers' statistics code.
Inputs: reports/stage_e31_pilot_spec.md (v2, sha256 31d33e68...; erratum: section 7 governs the gate),
reports/stage_e31_briefs/work/pilot/TABLES31.md, the per-day tables under reports/stage_e31_briefs/work/pilot/runs/measure31/
(<date>/placements.parquet, loop.parquet, days.parquet, DONE), runs/expected31.txt, the manifest runs/manifest31.json
(purchased files with sha256), the grain calendar data.calendars.grains, and the producer's outputs
runs/stats31.json / runs/stats31.md (open these only AFTER your own numbers are written).
Work, in this order:
1. With your own script (in reports/stage_e31_briefs/work/verify_pilot_opus/), from placements.parquet and loop.parquet only:
   the primary population (ZM.v.0, DAY, model c, both sides); K2 = fills; mean N_10 = E_10 - 0.264 (E_10 = mo_10 +
   c_half) for the dropping variant (mo_10) and the no-drop variant (mo_nd_10), as a pooled mean over fills with a valid
   value; 95% two-sided percentile day-block bootstrap (trade dates resampled with replacement, 2,000 replicates; use
   numpy default_rng(31) and also report your own seed-free check that the bound is stable within 0.01 tick across 3
   other seeds); K3 = mean round trips per DAY date (model c); the 0.528 bounds; the verdict.
2. Independent engine check of model (c) on a sample: pick 3 trade dates (one per year 2021, 2022, 2023, chosen by a
   rule you state before looking at any result, e.g. the 10th included DAY date of each year), and for each rebuild the
   ZM.v.0 best bid/ask and trades directly from the raw Z1 MBO file (databento DBNStore; your own minimal book: you
   need only the best levels after F_LAST records and the trade prints) and recompute, for every DAY placement
   (grid 08:35..13:10 CT, both sides, join at g + 50 ms at the best bid/ask, cancel at j + 60 s + 50 ms), whether model
   (c) fills (first A/B-aggressor trade strictly through the price) and its E_10 (mid at t_f + 10 s minus price, times
   side, in ticks). Compare row by row with placements.parquet (model c): counts of matches, mismatches with examples.
3. Only then open runs/stats31.json / stats31.md and compare every verdict number.
Output: reports/stage_e31_briefs/work/verify_pilot_opus/VERIFY_pilot_opus.md: your numbers, the producer's, CONFIRMED or
DISCREPANCY per number, the engine sample's match table, and any defect.
Boundaries: read-only on all data and producer files; no Databento call; no network; no edits outside your folder; no
commits; never read any ZM/ZS/ZL record dated on or after 2024-03-01 (there are none in the files; do not request any).
Keep command output short; memory: at most one heavy process, check free -m first.
Return: the path, CONFIRMED or DISCREPANCY for K1 (both variants), K2, K3 and the verdict, a summary of at most 200
words, and anything unfinished.

Additions for this run (lead, 2026-10-23 13:2x):
- Independence: do not open reports/stage_e31_briefs/work/verify_pilot/ (an earlier verifier's work) until your own
  numbers, your raw-data sample and your comparison with stats31 are written; then compare with it too and say where you differ.
- Pick your raw-data sample dates by your own rule stated before looking at any result; prefer dates not in
  work/verify_pilot/ (you may list its folder names only, not open its files, to avoid them).
- Heavy work: a full pytest run of the repo may be in progress. Do step 1 (tables) first; start step 2 (raw MBO) only when
  `pgrep -f "pytest -q"` returns nothing, and check free -m (keep at least 4 GB free).
