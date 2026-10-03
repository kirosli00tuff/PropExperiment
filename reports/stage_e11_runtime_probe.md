# Stage E.11 runtime probe: ML route v2 on synthetic data (Task 5)

Written by CanaryCoder-OpusXHigh, 2026-10-03 (times PDT). Design: docs/STAGE_E_ML_V2_DESIGN.md
V2.11 and V12. Code: ml_route_v2/probe.py, ml_route_v2/pipeline.py, ml_route_v2/synthetic.py.
Raw figures: the probe's own JSON, `<state-dir>/probe.json`. The state dirs are
/home/kiros-li/.cache/propexp_e11_probe/A and /B. They sit on the real disk because /tmp is a
RAM-backed tmpfs, and they are outside the repo. Logs:
reports/stage_e11_briefs/t5_probe_A.log, t5_probe_B.log and t5_probe_B_full.log.

Synthetic data only: no market data was opened. All figures are wall-clock times on synthetic bars,
not results.

**Update 2026-10-03, 04:30 PDT (FixCoder-OpusXHigh, lead ruling FIX 3, V2.11).** The engine stages
now free the world's bars and the panel before the engine starts and checkpoint every path. The
size-A simulate stage was re-measured for one path: it peaks at **4,778 MB (49% of the memory
available at launch), down from 7,198 MB (73%)**, and takes 310.6 s. See "FIX 3: memory and
per-path checkpoints" below. The size-A and size-B rows further down are the first pass's figures
and are kept as measured then.

## Machine and run conditions

- ThinkPad: 20 logical CPUs, 15,118 MB RAM (14 GiB), NVIDIA RTX 3050 Laptop 4 GB. The GPU was
  unused: ridge and LightGBM run on the CPU.
- Overnight profile. Every run used `nice -n 10` and `OPENBLAS_NUM_THREADS=1`. LightGBM used
  `num_threads` 8 (constants.LGBM_FIXED), so at most 8 threads ran at a time. Each size ran as the
  only heavy job, with one exception noted under size B. Nothing ran in the 15:30-16:00 PT window,
  and probe.py waits out that window before every timed step.
- MemAvailable at launch: size B 9,588 MB (02:53), size A 9,874 MB (03:06). The overnight
  profile's 70% limit is therefore about 6.7 to 6.9 GB.

## The synthetic world (what was timed)

- The training window: EARLIEST_S_X..TRAIN_LAST (2019-05-06..2024-02-29), 1,248 union trade dates
  of the real frozen group calendars.
- Bars: synthetic one-minute bars on every open interval of each root's group calendar. They cover
  each vehicle's price path, the 7 cluster leads, MES, and the member-signal legs of the vehicles'
  clusters.
- No warm-up history before S_X, as in the real run, so the first ~140 dates drop out to warm-up.
- 3 decision times, the 66-signal library, 154 model features, and the full grid of 45
  configurations with nested CPCV as designed.
- A sign edge of 3 round trips is planted on every product, so the cost gate trades at a busy,
  conservative rate.

| | size A | size B |
|---|---|---|
| products | all 28 of constants.UNIVERSE | 8: MNQ, ZN, 6E, MCL, MGC, MHG, ZC, MBT (a stand-in for the phase-1 subset, which the freeze picks; V2.1) |
| bar roots / bars | 29 / 44.7 M | 18 / 26.3 M |
| panel rows per horizon | 86,840 | 24,824 |
| admissible (root, h) pairs | 84 | 24 |
| Gate 0 tests (A + B) | 282 (198 + 84) | 222 (198 + 24) |

## Method

1. The pipeline's panel, filter and Gate 0 stages run first, with `force_after_gate0_fail` so
   that every stage runs.
2. ONE complete outer split is timed: all 45 configurations over its 4 inner folds plus the outer
   refit. That is 75 fits and 225 selection-metric scores. The probe calls cpcv's `_prepare` and
   `_compute_units` on split 0; the units land in the run's own store, and the full run resumes
   them.
3. Pieces for the extrapolation:
   - the frozen refit's largest fit, LightGBM depth 3 on every h60 row;
   - PBO (C(16,8) = 12,870 combinations) and DSR on a 1,248 x 45 matrix.
4. Simulate and payouts are measured on ONE path. The schedule is a stand-in: ridge lambda 0.1
   refit on every h60 row, with the cost gate at k = 1.5. It serves timing only.
   - The simulate step is a full engine run over the 1,248 dates at 50K.
   - The payout step is 8 calls of simulate_payouts_pair at 10,000 paths x 252 dates: 50K and
     150K, Standard and Consistency, DLL off and on, with kill switches on and off in one draw.
5. Extrapolated full run = world + panel + filter + Gate 0 + 15 x split + final refit + PBO/DSR
   + 15 schedule refits + 5 x (simulate + payouts) of one path.
6. If the extrapolated size B total is under 90 minutes, size B then runs fully end to end
   (`--full`, resumable), and the measured figures replace the estimate.

Peak RSS per stage is VmHWM from /proc/self/status, reset before each stage through
/proc/self/clear_refs. It includes whatever the process already held, such as the bars. Disk is
the state directory's size after the stage.

## Size A (28 products): measured stages and extrapolated full run

| stage | wall | peak RSS | disk after | basis |
|---|---|---|---|---|
| world build (bars, releases, costs) | 7.9 s | 2,439 MB | - | measured |
| panel (rows, sigma, targets, 66 signals, z-scores) | 28.7 s | 3,156 MB | 128 MB | measured |
| filter (c/sigma, risk table) | 0.2 s | 2,763 MB | 128 MB | measured |
| Gate 0 (A: 198 tests; B: ridge CPCV OOF, 84 pairs) | 12.9 s | 3,179 MB | 138 MB | measured |
| one outer split (45 configs x 4 inner + refit) | 48.1 s | 3,295 MB | 139 MB | measured |
| nested CPCV, 15 outer splits | 722 s (12.0 min) | ~3.3 GB | ~150 MB | extrapolated (15 x split) |
| stats (PBO and DSR) | 0.7 s | - | - | measured on a matrix of the full shape |
| final selection and frozen refit | 1.0 s | - | - | measured (LightGBM d3, every h60 row) |
| schedule (15 refits of the selected configs) | 16 s | - | - | extrapolated (15 x refit) |
| simulate, one path (engine, 50K) | 341 s | **7,198 MB** (sampled 7,372 MB) | - | measured before FIX 3 (22,084 candidates, 6,597 trips) |
| simulate, 5 paths | 1,707 s (28.4 min) | 7.2 GB | - | extrapolated before FIX 3 (5 x one path) |
| payouts, one path (8 calls x 10,000 paths) | 54.3 s | 4,630 MB | - | measured before FIX 3 |
| payouts, 5 paths | 271 s (4.5 min) | 4.6 GB | - | extrapolated before FIX 3 |
| **total, full grid** | **46.1 min** | **7.2 GB** | ~200 MB | extrapolated before FIX 3 (disk scaled from size B's 59.5 MB by rows) |
| *after FIX 3:* engine frames to disk (28 vehicles, once) | 32.2 s | 2,734 MB | +1,841 MB | measured 2026-10-03 |
| *after FIX 3:* simulate, one path, inline (the default) | 310.6 s | **4,778 MB** | - | measured 2026-10-03 (same 22,084 candidates, 6,597 trips) |
| *after FIX 3:* simulate, one path, isolated | 311.4 s | 802 MB parent + 4,669 MB child | - | measured 2026-10-03 |
| *after FIX 3:* payouts, one path | 51.7 s | 2,414 MB (inline) / 802 MB (isolated) | - | measured 2026-10-03 |
| ***total, full grid, after FIX 3*** | ***43.9 min*** | ***4.8 GB*** | ~2.0 GB | extrapolated: the rows above with simulate and payouts replaced (frames 32 s + 5 x 310.6 s; 5 x 51.7 s) |

## Size B (8 products): extrapolation, then a full measured run

First pass, with the extrapolation:

| stage | wall | peak RSS | disk after | basis |
|---|---|---|---|---|
| world build | 3.4 s | 1,512 MB | - | measured |
| panel | 12.4 s | 1,733 MB | 36.7 MB | measured |
| filter | 0.1 s | 1,560 MB | 36.7 MB | measured |
| Gate 0 (222 tests; passed on the planted edge) | 4.1 s | 1,698 MB | 39.6 MB | measured |
| one outer split | 49.9 s | 1,759 MB | 40.0 MB | measured, contended (note 1) |
| simulate, one path | 115.2 s | 3,003 MB | - | measured (7,027 candidates, 4,824 trips) |
| payouts, one path | 56.5 s | 2,263 MB | - | measured |
| **extrapolated total** | **27.3 min** | 3.0 GB | | CPCV 749 s, simulate 576 s, payouts 283 s, rest 32 s |

Because 27.3 minutes is under the 90-minute limit, size B then ran fully end to end
(03:14:38-03:33:56; the pipeline's stage records):

| stage | wall | peak RSS | disk after | basis |
|---|---|---|---|---|
| panel, filter, Gate 0 | (first pass above: 16.6 s) | | 40.0 MB | measured |
| nested CPCV, all 15 splits | 49.9 s (split 0) + 288.7 s (splits 1-14) = **338.6 s (5.6 min)** | 1,738 MB | 47.8 MB | measured |
| stats (PBO, DSR at N_total) | 0.7 s | 1,653 MB | 47.8 MB | measured |
| final selection and refit | 2.2 s | 1,709 MB | 47.9 MB | measured |
| schedule (nested OOS, 5 paths) | 4.4 s | 1,694 MB | 53.6 MB | measured |
| simulate, 5 paths | 576.8 s (9.6 min) | 3,088 MB | 59.5 MB | measured |
| payouts, 5 paths x 8 calls x 10,000 | 281.2 s (4.7 min) | 2,272 MB | 59.5 MB | measured |
| **measured total** | **1,224 s (20.4 min)** | **3.1 GB** | **59.5 MB** | measured, excluding the stand-in timing steps |

Measured against extrapolated (size B):
- Simulate (576.8 s against 575.8 s) and payouts (281.2 s against 282.7 s) matched the
  one-path extrapolation within 1%.
- The CPCV ran at 20.6 s per split in the full run, against 49.9 s for the timed split. The timed
  split overstated the CPCV by 2.2x. The likely causes are note 1 and one-time warm-up in the
  first split.
- The size A CPCV figure (48.1 s per split, timed alone) is therefore probably conservative too.
  The other size A rows should be close.

Notes:
1. Size B's first ~2 minutes (world, panel, Gate 0 and the timed split) overlapped a light second
   job of mine, the canary-figure script (one thread, under 1 GB). Everything else ran alone.
2. probe.json for B: the `--full` restart overwrote the first pass's `stages` entry with the
   restart's "loaded" timings, so its `extrapolated` entry shows a 3.4 s fixed-stage sum. The
   first-pass figures above come from the probe output read before the restart (t5_probe_B.log,
   02:57). probe.py now keeps a first pass's figures and writes a restart's under
   `stages_restart`.
3. The synthetic selection on B (lgbm_d2 and lgbm_d3 at k 1.5 h60, median-path t 8.2) reflects the
   planted edge. It is not a result.

## Full grid on the ThinkPad under the overnight profile

- **Size A (28 products): about 46 minutes (about 44 after FIX 3), extrapolated and
  conservative. Size B (8 products): about 20 minutes, measured.** The time divides into three
  parts:
  - the engine: 5 paths x 5.7 minutes at 28 products (5.2 after FIX 3), 61% of size A;
  - the nested CPCV: about 26%, or less given the B correction;
  - the payout simulation: about 10%.
- **Memory is the binding limit, as CLAUDE.md says.**
  - Before FIX 3, size A's simulate stage peaked at 7.2 GB, 73% of the 9.87 GB available at
    launch. That is above the profile's 70% rule.
  - The cause: the probe process still holds the 29 roots' bars (about 2.4 GB) while the engine
    builds and walks the 28 engine frames.
  - Fixed 2026-10-03 (FIX 3): the engine now runs with neither the bars nor the panel held.
    - One size-A path peaks at 4,778 MB, 49% of the 9,737 MB available at launch.
    - Size A's highest stage is now the simulate stage at 4.8 GB. Before the engine the highest
      was 3.3 GB (the CPCV split).
  - Size B peaked at 3.1 GB before FIX 3. It was not re-measured; the same freeing applies.
- Disk is small: 60 MB measured for B and about 200 MB estimated for A. The largest file is the
  panel pickle, 38 MB for B and about 130 MB for A.
- Threads stay at 8 at most (LightGBM), within the profile's 14. The GPU is not needed.

## 8-to-10-hour windows and checkpoints (V12)

- The whole grid fits one window with a wide margin. Size A needs about 44 minutes (46 before
  FIX 3), so even a real-data run 5 to 10 times slower would still fit in one 8-hour window.
- If a run must pause anyway, a kill at any moment loses at most the unit in progress (since
  FIX 3 that includes one engine or payout path), and a restart with the same state dir resumes.
  The checkpoints are below.

| checkpoint | what is saved | what a restart does |
|---|---|---|
| `stages/panel.pkl` | the training panel | loads it; no bars needed until simulate |
| `stages/filter.pkl` | c/sigma table, risk table, admissible pairs | loads |
| `gate0/` | Gate 0 B's OOF predictions per (horizon, split), and a meta file pinning the inputs | recomputes only the missing splits; a changed input raises StateMismatchError |
| `stages/gate0.pkl` | the Gate 0 tests and verdict | loads; a failed verdict stops the run (V2.2b) |
| `ledger.jsonl` | every configuration and Gate 0 test, append-only | re-registering is a no-op, so N is stable across restarts |
| `cpcv/cpcv_units.jsonl` | one line per finished (config, split, fold) unit: 3,375 units (45 x 15 x 5) plus the meta line | skips the finished units; a fingerprint guards the inputs |
| `stages/cpcv.pkl`, `stats.pkl`, `final.pkl`, `schedule.pkl` | NestedResult; PBO, DSR, path t; frozen config and sha256; nested OOS schedule per path | load (seconds to recompute) |
| `engine/frames/<root>.pkl`, `engine/frames/meta.pkl` (FIX 3) | the engine frame of each traded vehicle, cut to the training calendar (1.84 GB for 28 at size A); the meta pins the world | missing roots are built, present ones reused; another world's meta raises PipelineError |
| `engine/path_<j>.pkl` (FIX 3) | one file per path, written when the path finishes: DayRecords, daily P&L, trips, MLL audit, plus a fingerprint of the schedule, the risk table and the engine inputs | **finished paths are loaded, only the rest run**: a kill mid-stage loses at most the path in progress (5.2 minutes at size A); a file written for other inputs raises PipelineError |
| `stages/simulate.pkl` | per path: the same summaries | written at the end of the stage; when present the stage is loaded |
| `payouts/path_<j>.pkl` (FIX 3) | one file per path: that path's payout rows (account x path type x DLL x ks), with a fingerprint of the path's day records and the draw count | finished paths are loaded (52 s each at size A); a mismatch raises PipelineError |
| `stages/payouts.pkl` | the payout table (path x account x path type x DLL x ks) | written at the end; when present the stage is loaded |

Window boundaries: window 1 runs world through the CPCV and schedule, about 13 minutes at size A.
Window 2 runs simulate and payouts, about 31 minutes. Since FIX 3, a stop anywhere in window 2
loses at most one path (5.2 minutes of engine time or 52 s of payouts).

## FIX 3: memory and per-path checkpoints (2026-10-03)

What changed (lead ruling, Stage E.11 FIX 3; code: ml_route_v2/engine_stage.py,
ml_route_v2/pipeline.py, ml_route_v2/probe.py):
- **Freeing before the engine.**
  - run_pipeline holds the world in one place.
  - Before the engine starts, it drops the panel (also from the report's results) and,
    once the engine frames are on disk, the world (its bars).
  - The bars are freed only when the caller keeps no other reference. probe.py now passes the
    full run a fresh world it does not keep.
- **Only the needed frames.**
  - The engine frames of the traded vehicles are written once to engine/frames, one vehicle at a
    time.
  - Each path then loads only its own traded vehicles' frames from disk.
- **Per-path checkpoints** for simulate and payouts (table above). The restart is tested:
  - tests/test_ml_v2_engine_stage.py: a run killed in path 1 keeps path 0, the restart computes
    only path 1, and a stale file raises;
  - tests/test_ml_v2_e2e.py: a pipeline restart with the stage files removed reuses every path
    file.
- **Optional process isolation.** `run_pipeline(isolate_paths=True)` (probe: `--isolate-paths`)
  runs each path in its own spawned process, one at a time. The default stays inline
  (`pipeline.ISOLATE_ENGINE_PATHS = False`): one inline path peaks at 49% of the memory available
  at launch, not above the brief's "about 50%" trigger. An isolated path costs about 0.7 GB more
  at the peak (the parent plus the child's own interpreter), though it returns all of its memory
  after each path.

Measurement (one size-A path, nice 10, OPENBLAS_NUM_THREADS=1, alone on the machine; the
stage figures as printed: reports/stage_e11_briefs/fix3_measure_A_inline.log and _isolate.log). The schedule is the first pass's stand-in: probe
A's panel.pkl and filter.pkl, ridge lambda 0.1, k = 1.5, 22,084 candidates. The engine frames and
checkpoints went to /home/kiros-li/.cache/propexp_e11_probe/A_fix3.

| | inline (04:13-04:20) | isolated (04:20-04:27) |
|---|---|---|
| MemAvailable at launch | 9,737 MB | 9,773 MB |
| world build (bars held) | 8.0 s, 2,446 MB | 7.9 s, 2,414 MB |
| engine frames to disk (28 vehicles) | 32.2 s, 2,734 MB, 1,841 MB on disk | reused |
| process RSS after freeing the world and the panel | 859 MB | 798 MB |
| **simulate, one path: wall** | **310.6 s** (341 s before) | 311.4 s |
| **simulate, one path: peak RSS** | **4,778 MB, 49% of launch** (7,198 MB, 73% before) | parent 802 MB + child 4,669 MB = 5,471 MB, 56% |
| lowest MemAvailable during the engine | 4,964 MB | 4,525 MB |
| trips | 6,597 (as before) | 6,597; daily P&L identical to inline |
| payouts, one path | 51.7 s, 2,414 MB | 51.6 s, 802 MB |

Notes:
1. The inline process kept about 1.6 GB after the engine path. RSS in the payout step was
   2.4 GB, against 0.86 GB before the engine. Size B's measured 5-path run grew only 85 MB from
   its one-path peak, so the allocator should reuse that memory for the next path rather than
   add to the peak. A 5-path inline run at size A was not measured. If one exceeds about 50%,
   `isolate_paths=True` caps every path at the measured 56%.
2. The size-A panel used here predates FIX 2 (the V2.2 leg roll-blackout rule). On the synthetic
   world FIX 2 changes no row: every synthetic root rolls on the same quarterly rule, so D4's
   union and the own-date exclusion give the same 98,133 size-A decision rows. The schedule and
   the timing are therefore the same under the new rule. Real data will differ: CL and MBT roll
   monthly, so the new rule keeps rows that D4's union dropped.

## Caveats

- Synthetic bars make the panel size realistic (rows, features, admissible pairs), but three
  things will differ on real data:
  - LightGBM's tree growth (min_data_in_leaf 2000 caps it);
  - the number of candidates;
  - so the score and engine time.
- The planted 3c edge gives a busy schedule: 22,084 stand-in candidates at size A, about 25% of
  rows. A real, weaker edge trades less, so the engine and selection-metric figures here lean
  high.
- Real bar loading from the step 2 stores (parquet I/O) is not timed; the panel stage here
  generates bars in memory. The timed size A world build took 7.9 s.
- The timed split includes one-time warm-up; see the size B comparison above.
