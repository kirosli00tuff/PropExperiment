# Brief: MLPipelineCoder-OpusXHigh (Stage E.2b Task 2; worker-xhigh on opus)

Objective: build the ML route's pipeline and every M7 leakage test (design D11.7, docs/STAGE_E_ML_DESIGN.md M3 to M8 with
every E.2a ruling in brackets), on synthetic data only, and record timed probes on synthetic data of the real size.

## Read first (by section)
- reports/stage_e2b_briefs/00_common.md (binding). You are the ONLY worker allowed to change the Python environment.
- docs/STAGE_E_ML_DESIGN.md (FROZEN; never edit): M1 (partition), M2 (pooling, the 31 price-path contracts), M3
  (challengers), M4 (features, availability, net target), M5 (distillation, surrogate trees, block-6 pre-test, rulings
  ML-A01 and ML-A02), M6 (trial accounting), M7 items 1 to 9, M8 (compute; the A-1 batch-size rule).
  reports/stage_e2a_ml_changes.md (A-1..A-3) and reports/stage_e2a_ml_freeze_rulings.md.
- docs/STAGE_E_DESIGN.md D8 (the cost model used in the net target); sim/product_costs.py; reports/stage_e2a_costs.json
  (read-only); data/calendars/ and data/cme_calendar.py (M7.3's block cut uses calendars only, no bar data).
- tests/test_leakage_canaries.py and sim/leakage_canaries.py (M7.7), strategy/interface.py (the Strategy protocol).

## Step 1 (do this first, before anything else): dependencies
- Add lightgbm and torch to pyproject.toml and pin them in uv.lock, torch with CUDA support. Check the driver with
  nvidia-smi. The lock must also resolve a CUDA torch wheel for win_amd64 (user decision V10: the Windows PC with an RTX
  2060 Super, Turing sm_75, may run the LSTM): use the PyTorch index for the chosen CUDA version with explicit = true
  and [tool.uv.sources] so both linux x86_64 and win_amd64 get CUDA builds, and confirm sm_75 and sm_86 are in the
  build's arch list (torch.cuda.get_arch_list()).
- No existing package's pinned version may change: diff uv.lock and list every changed existing package; if any changes,
  stop before `uv sync` and report to the lead (MES bit-for-bit results depend on numpy/pandas versions).
- Record versions (lightgbm, torch, CUDA runtime, driver) in your report and in reports/stage_e2b_ml_probes.json.

## Build (a new package, ml_route/, plus tests/test_ml_route_*.py)
- The feature pipeline (M4) with an availability timestamp on every value, and the feature-timestamp validator.
- The net target with the D8 cost model (charged as M4 says).
- The CPCV splitter by trade date (M7.3 as ruled: calendar-only six blocks, blocks 1-5 for CPCV with two test blocks = 10
  splits, purge by target-window overlap, one full trade date embargo on each side of each validation block).
- The LightGBM and PyTorch jobs: fixed seeds, frozen thread counts (a module constant, not an env var; LightGBM with
  deterministic settings), resumable ledgers (JSONL per configuration x fold, skipped on restart), the model hash chain
  (M7.6: every fitted model's sha256 recorded; a test run refuses on a different hash; record which machine ran each
  fit, since hashes need not match across machines).
- The training job's data access: it reads only the training-window store (built by PurchaseCoder2's step 2 store
  builder, same parquet schema as data/build_bars.py's research parquets; synthetic in tests), asserts a path allowlist
  (ML-A23), and refuses any row whose trade date is on or after 2024-03-01 or before the product's S_X. Its entry point
  takes the store root and the output directory as explicit arguments and calls screening.harness_freeze.preflight()
  first (see 00_common.md). A research-window store must sit in a different root that the training job cannot read.
- The surrogate-tree and block-6 pre-test code (M5, with ML-A01 and ML-A02), the rule wrapper (a distilled rule as a
  Strategy the engine runs, M7.7), and the route manifest writer (block boundaries, S_X values, probe figures, batch size,
  model hashes, trial counts per M6).
- Every M7 test with known answers: M7.1 validator + its two canaries (a feature equal to y; one equal to the next bar's
  close) rejected; M7.2 perturbation (single-product and cross-product F16 features); M7.3 fold test; M7.4 window test
  with a planted research-window bar in the store that makes the job refuse, and a planted research-window path; M7.5
  normalization (perturb all rows after the training window, fitted model hash unchanged); M7.6 hash chain; M7.7 the rule
  wrapper through the existing canaries (sim/leakage_canaries.py; do not edit it or its tests; CanaryCoder extends
  canaries later and needs your wrapper's interface documented in its module docstring).

## Probes (synthetic data of the real size: about 450,000 rows, 20 features, 31 products)
- One LightGBM configuration on one CPCV split at 8 threads (this job may use 8 threads; run it through heavy.sh).
- One LSTM configuration for one epoch on the RTX 3050, with the batch size planned by the frozen A-1 rule (M8: the
  largest configuration, 32 hidden units, lookback 72, one forward and backward pass at batch 512; peak =
  torch.cuda.max_memory_reserved() plus the process's CUDA context from nvidia-smi's per-process figure; halve 512 -> 256
  -> 128 -> 64 while less than 0.5 GB of the 4 GB stays free; if 64 fails, stop and report). Check free VRAM with
  nvidia-smi before launch; one GPU job at a time. If torch cannot use the GPU: record why, run the LSTM probe on CPU and
  report the projected time; never change the challenger list.
- Write measured times, peak RAM and peak VRAM, the batch size, and the projected full-run time per challenger (trees:
  24 configurations x 11 fits; LSTM: 12 configurations x 11 fits x 8 epochs, per M8) to reports/stage_e2b_ml_probes.json.
  These are the ThinkPad's figures; E.2c repeats them on the Windows PC.

## Ownership
You own ml_route/, tests/test_ml_route_*.py, pyproject.toml, uv.lock, reports/stage_e2b_ml_probes.json. Others own the
runner files (RunnerCoder, ScreenStatsCoder), data/ (PurchaseCoder2), compute/ and screening/harness_freeze.py (lead).

## Report
reports/stage_e2b_task2_ml_worker.md: interfaces (the job entry, the store reader, the rule wrapper) at the top; each M7
test and what it proves; versions; the probe table; anything you could not finish.
