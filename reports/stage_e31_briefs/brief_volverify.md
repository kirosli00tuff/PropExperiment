# Brief: VolumeVerifier-FableXHigh (worker-xhigh, model fable) - independent check of the Part 1 verdicts

Objective (one): independently recompute the Part 1 volume verdict numbers from the purchased DBN file, then
compare with the producer's results, and report every difference.
Order of work (independence): FIRST write your own short script (in your own scratch dir, e.g.
reports/stage_e31_briefs/work/verify_vol/) from the definitions in reports/stage_e31_volume_request.md ONLY
(frozen; sha256 09d83f433f2869aab4e26670c455266dd597a6a32673a9c367a846bdf5939b9e: check it), run it, record your
numbers; only THEN open the producer's outputs reports/stage_e31_briefs/work/pilot/runs/vol_measures.json and
reports/stage_e31_volume.md and code reports/stage_e31_briefs/work/pilot/vol_measure.py, and compare.
Input: the DBN file named in reports/stage_e31_briefs/work/pilot/runs/vol_purchase_manifest.json (check sha256).
Numbers to recompute: the window (last 12 full months before the exclusive end) and its day counts; QM and ZM
median daily volume on the primary universe and on each root's own universe; the two verdicts; per root and
quarter: days, median, p10, front-month share; the hyphen-dropped counts; weekend bars; instrument-id to symbol
resolution (note: some ids are reused across symbols over time, so resolve by date interval).
Also audit: that only ts_event, instrument_id, volume (and mappings) are used; no price is used or reported.
Output: reports/stage_e31_briefs/work/verify_vol/VERIFY_volume.md: your numbers, the producer's, the match or
difference for each, a verdict CONFIRMED / DISCREPANCY per verdict number, and any defect in the code.
Boundaries: no network or Databento call, no other data file, no edits to the producer's files. No commits.
Keep command output short. Return the path, a summary of at most 200 words, and anything unfinished.
