# Brief: SimCoder-OpusXHigh (worker-xhigh, model opus) - Stage E.31 Part 3, the order-book engine

Objective (one): write the engine that rebuilds the ZM book from MBO, simulates the virtual 1-lot under fill models
(a) K, (b) FIFO and (c) trade-through, runs the round-trip loop, and writes the per-day tables. Synthetic tests only.

Binding inputs (read by section):
- reports/stage_e31_pilot_spec.md sections 1 to 6 and 8 (implied check). Section 3.1 is the K algorithm.
- reports/stage_e31_briefs/work/pilot/TABLES31.md: the exact output tables (the stats layer, written by StatsCoder,
  reads them; do not change the interface; if it cannot hold something the spec needs, stop and report).
- reports/stage_e31_briefs/research/K_algorithm.md (parameters; section c's worked examples E1-E7 and E9 become unit
  tests, with the two printing errors corrected as its section d items 4 and 5 state).
- reports/stage_e31_briefs/research/data_facts.md section a (Databento MBO facts: weekday 00:00 UTC snapshots = R then
  A records in priority order with F_SNAPSHOT; trade = one T record with the aggressor side (N on implied trades),
  then one F record per resting order filled; T and F do not change the book; flags; ts_event vs ts_recv; mbp-1).
- Reuse, read-only: E.28's reports/stage_e28_briefs/work/B_pilot/pilot_stream.py (stream one trade date at a time),
  measure_core.py (placements, fills, markouts on mbp-1), pilot_common.py (sessions, grid, exclusions); the repo's
  data.calendars.grains (HOLIDAYS, LATE_OPENS, sessions). Copy what fits into new files.
- Purchased files: their list comes from runs/manifest31.json (written by verify31.py: path, series, month, sha256).
  USDA releases: reports/stage_e31_briefs/research/usda_releases.csv plus usda_releases_ext.csv (same columns; an
  extension being written now). Refuse to measure a trade date outside the USDA files' covered range.
Files (new, in reports/stage_e31_briefs/work/pilot/): mbo_book31.py (book per instrument, priorities, TOP state,
snapshots), kalgo31.py (the allocation function of spec 3.1, pure, no I/O), measure31_core.py (placements, fill
models, markouts, conditions, loop, implied check), measure31.py (CLI: --manifest PATH --out DIR [--workers N]
[--dates FILE] [--write-expected-dates FILE]; per trade date, resumable with a done marker, nice 10, workers at most
min(8, os.cpu_count() // 2); a split step that streams each monthly DBN file once into per-trade-date compact arrays
under /mnt/large-storage/market_data/PropExperiment/derived/e31/ so each worker reads only its date), README_measure31.md
(commands, the match-event grouping rule, every convention the spec leaves to the code), tests/test_kalgo31.py,
tests/test_book31.py, tests/test_measure31.py.
Speed matters: the window may hold 30+ months of ZM MBO (several hundred million records). numba is not installed and
no dependency may be added: use numpy where it fits and lean Python in the book loop. Measure your per-record
throughput on a synthetic day and state the estimated hours for 700 trade dates on 8 workers, and the peak memory
per worker, in your return.
Tests (synthetic only): K allocator on every CME example and on hand-built full-sequence cases (TOP + split + FIFO +
pro rata + leveling + FIFO, stating each order's lots by hand); book rebuild (add, cancel, modify: size decrease keeps
priority, increase or price change loses it; snapshot clear and rebuild; TOP set and lost); each fill model on small
scenarios (queue fill, through fill, no fill on a touch, cancel at 60 s + 50 ms); markouts, half-spread and drops;
session clocks in CST and CDT; roll-day, holiday and gap exclusions; the loop state machine; ZS/ZL condition values;
the table columns match TABLES31.md exactly. Run: uv run pytest -q -p no:cacheprovider on your three test files.
Boundaries: no Databento call, no network, no API key, no real data file opened (none exists yet). Do not edit the
spec, TABLES31.md, or other workers' files (pull31*, pilot31_common.py, verify31*, vol_*, stats31*). No record dated
on or after 2024-03-01 may be read (guard it). If the spec is ambiguous, choose the conservative reading, write it in
README_measure31.md under "Conventions", and list it in your return. No commits. Keep output short (pytest -q).
Return: the paths, a summary of at most 200 words with test counts, the speed and memory estimate, and anything
unfinished.
