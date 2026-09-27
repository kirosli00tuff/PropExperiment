# Stage E.2b V10 amendment: the Windows PC as an optional machine for ML training and backtests

Written by the Stage E.2b lead (Opus 5.5, xhigh) on 2026-09-26, before any Stage E member was coded or run and before any
model was fitted on real data (none has been). Authority: the user's decision V10 of 2026-09-26, as the Stage E.2b prompt
records it: "The user decided on 2026-09-26 that ML training and backtests (screening and confirmation runs) may execute on
the Windows PC when it is available: Ryzen 5, 32 GB of RAM, NVIDIA RTX 2060 Super with 8 GB of VRAM, 2 TB SSD (figures as
the user gave them, measured in E.2c). The PC is shared and not always available, so the ThinkPad stays the default and
every job must also run on it unchanged. The ThinkPad keeps the Claude sessions, purchases, sealing, reviews and commits,
and sends each job over SSH when the PC is used."

This amendment edits no frozen file. docs/STAGE_E_ML_DESIGN.md stays as frozen by reports/stage_e2a_ml_freeze.json
(sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2); its M8 is read together with this file. It is
hashed by the Stage E harness manifest (reports/stage_e2b_harness_freeze.json) and audited in Stage E.2b Task 7.

## What changes

**V10-1. Where jobs run (M8, "Where").** V7 (2026-09-25) dropped the Windows PC: "nothing of the route runs on it and no
data is copied to it". V10 supersedes that sentence and nothing else in M8. The ThinkPad stays the default machine: the
trees on its CPU, the LSTM on its RTX 3050 Laptop GPU, as V7 set. When the Windows PC is available, an ML training job or
a backtest (a cluster's screening or confirmation run) may run there instead, sent from the ThinkPad over SSH by the
Stage E compute backend (compute/). Every job runs unchanged on either machine.

**V10-2. One machine and one batch size per LSTM grid (M8, "LSTM batch size", the frozen A-1 rule).** The A-1 rule gives
one batch size for all four LSTM configurations, recorded in the route manifest before any fit. To keep that a single
value whichever machine runs a fit:
- Before the first LSTM fit, the route manifest records the machine chosen to run the LSTM challenger and the batch size
  that the A-1 rule plans on that machine's card. On the RTX 3050 the rule reads as written (4 GB). On the RTX 2060 Super
  the same rule runs against its memory (8 GB, measured in E.2c): the same largest configuration (32 hidden units,
  lookback 72), the same start at batch 512, the same halving to 256, 128 and 64 while less than 0.5 GB of the card's
  memory stays free, the same peak measure (torch.cuda.max_memory_reserved() plus the process's CUDA context from
  nvidia-smi), and the same stop to the user if 64 still fails.
- Every LSTM fit of the route (12 configurations x 11 fits) uses that recorded batch size. If fits must move to the other
  machine (the PC becomes unavailable, or the reverse), they keep the recorded batch size and run only if that card holds
  it with at least 0.5 GB free by the same measure; otherwise they wait for the recorded machine, or the case goes to the
  user. A batch size is never re-planned after the first fit.

**V10-3. Machine record.** Every job records the machine that ran it (host name, operating system, CPU, GPU, driver and
CUDA versions, and the lightgbm, torch, numpy and pandas versions) in its result record; for ML fits the record sits in the
route's ledger beside each model's sha256 (M7.6). Hashes are recorded as produced: bit-identical fits across the two
machines are not assumed, and the route's test run loads the recorded models and refuses on a different hash, as M7.6
says. The trees' thread count and every seed stay the pipeline's frozen constants on either machine.

**V10-4. What never goes to the PC.** Enforced by the backend's send side and checked again on the PC before a job
starts: no sealed holdout chunk; no plaintext bar booked to a holdout-1 trade date (on or after 2026-06-22), a holdout-2
trade date (2024-04-01..2025-03-31) or the March 2024 embargo; no Databento key or other secret; no ledger. Purchases,
sealing, unlock-log handling, reviews and commits stay on the ThinkPad. The frozen harness commit itself is never sent,
because git history carries the ledger: the ThinkPad exports the frozen commit's tree without ledger/ as a reproducible
single commit (no history), checks the exported tree against the harness preflight before anything leaves, and sends it as
a git bundle over SSH (no repository credential is stored on the PC). A job refuses unless the PC's checkout is that
export commit with every tracked file byte-identical to its blob, the installed numpy, pandas, pyarrow, lightgbm, torch and
scikit-learn versions equal uv.lock's, and the Stage E harness preflight passes there.

**V10-5. M7.4 kept by separate data roots.** An ML training job's data root on the PC holds only the training-window
store (trade dates 2019-05-06..2024-02-29, from each product's S_X); the research-window stores that backtests read go to
a separate root the training job cannot read, and a training job whose root holds anything else is refused. The training
job's path allowlist (ML-A23) and the planted-bar and planted-path canaries (M7.4) apply unchanged on either machine.

**V10-6. Results.** A result is accepted on the ThinkPad only after its sha256 manifest, pulled back with it, verifies
file by file; a missing hash or a mismatch refuses the result and the job is run again.

**V10-7. Limits on the PC.** Jobs there run at below-normal priority (the Windows form of nice 10), one heavy job at a time
(the PC is shared), with the pipeline's frozen thread counts; CLAUDE.md's overnight profile still governs the ThinkPad.
E.2c measures the PC (CPU, memory, GPU, the two probes) before its first real job.

## What does not change

Every statistical choice in the frozen ML design: the partition (M1), pooling (M2), the challenger list and grids (M3),
features, availability and targets (M4), distillation and the pre-test (M5), trial accounting (M6), the leakage controls
(M7, items 1 to 9), and the A-1 rule itself. The screening rules of docs/STAGE_E_DESIGN.md and docs/NULL_CRITERIA_E.md
are untouched: a backtest computes the same thing on either machine. No member, trial, window, threshold or cost changes.
