# Stage E.2a Task 1: every edit applying the user's decisions V1 to V9

Lead: Opus 5.5 (xhigh). Applied 2026-09-25 by one script (exact-string replacements, each checked
to match exactly once in docs/STAGE_E_ML_DESIGN.md before anything was written, and each new text
checked present exactly once after). The decisions are quoted verbatim in docs/DECISIONS.md (entry
of 2026-09-25) and in the stage prompt (docs/prompts/STAGE_E.2a.md, Task 1).

docs/STAGE_E_ML_DESIGN.md sha256 before: 7ae2d3471c2d2d79da2380db0fa74c5ccef1859718002999e605488fc411d6a1
docs/STAGE_E_ML_DESIGN.md sha256 after Task 1: 185e8cd5c908048ff6de3ae63036b31ed7b8badab62c8d4aec2890d58aeba8a0

## Decision coverage

| Decision | Edits | Or: no edit needed, and why |
|---|---|---|
| V1 | ML-00, ML-01, ML-03, ML-04, ML-05, ML-20, ML-35, ML-36 |  |
| V2 | ML-00, ML-06, ML-07, ML-36 |  |
| V3 | ML-00, ML-08, ML-11, ML-36 |  |
| V4 | ML-00, ML-12, ML-14, ML-36 |  |
| V5 | ML-00, ML-15, ML-16, ML-36 |  |
| V6 | ML-00, ML-17, ML-18, ML-36 |  |
| V7 | ML-00, ML-09, ML-10, ML-21, ML-22, ML-23, ML-24, ML-25, ML-26, ML-27, ML-28, ML-36 |  |
| V8 | ML-00, ML-02, ML-13, ML-19, ML-29, ML-30, ML-31, ML-32, ML-33, ML-34, ML-36 |  |
| V9 | ML-00 | No edit to the ML design. F-1: the design already says 31 traded exposures (M1 table, M2) and the frozen D1 says 31; nothing to change. F-5: K2-aucpost-01 is in the frozen catalog; acceptance is recorded in docs/DECISIONS.md, no catalog edit (the catalog is frozen). FA-06 option: carried out by Tasks 2 and 11 as a separate amendment file; the ML design's only source-overlap sentence (M6, route rules are not source-overlap on that ground) is unaffected. |

Every edit maps to a decision (the Decision field of each edit below). ML-00 and ML-36 are the
record notes (header and collected list) that say the decisions were applied.

## Application notes and questions for the user (not applied: no decision covers them)

- Q-1 (V1, cap). M1's "User decides" listed "the cap for that purchase". V1 decides the partition,
  the full step 2 range and that funding is pending, but sets no cap. Left to the user; the design says
  so (ML-05). D13's frozen per-session rule (quote plus 10%) is the precedent, not applied here.
- Q-2 (V8 against the E.2a prompt). V8: "the route's buy and train sessions run after E.2b". The E.2a
  prompt's summary says Stage E.2b "buys the older history once the user funds it", and its scope says the
  older history "is bought in E.2b or later". The design follows V8's text (E.ML-buy after E.2b, ML-31);
  which session makes the purchase has no effect on the partition, the seal-on-arrival rule or any
  statistic. For the planning chat.
- Q-3 (V7, budget). M8's "User decides" listed the compute budget. V7 sets none; the design says E.2b's
  probe re-plans the estimates and reports them (ML-28).
- A-1 (V7, application detail). V7 says "state that E.2b's probe re-plans the LSTM's batch size to leave
  at least 0.5 GB of VRAM free". So that no choice is left to be made after data is seen, ML-24 states
  the re-plan as a mechanical rule on synthetic inputs of the frozen shapes (halve from 512 to 256, 128,
  64 until 0.5 GB stays free; one batch size for all four LSTM configurations; recorded in the route
  manifest before any fit; stop to the user if 64 does not fit). The halving sequence and the single
  batch size are the lead's reading of V7, flagged for the auditor.
- A-2 (V7, the draft's CPU fallback). The draft's fallback (sub-sample or drop the LSTM on the CPU) was
  conditional on the user refusing the Windows PC. V7 moves the LSTM to this machine's GPU, so the
  fallback is struck, and the design says the LSTM's data, decision times and grid are not reduced
  without the user's decision (ML-25). This is the freeze's default, not a new choice.
- A-3 (V8, session names). Where the draft says "E.2" for the freeze it now says E.2a, and for the
  route's build E.2b, the split V8 names (ML-02, ML-13, ML-19, ML-24, ML-27, ML-30, ML-34).

## Edits to docs/STAGE_E_ML_DESIGN.md

### ML-00 (V1-V9 (record))

Old:

```
**DRAFT. Nothing in this file is frozen, hashed or registered.** Written by the Stage E.1 lead
(Opus 5.5, max effort) on 2026-09-24, after the Stage E pre-registration freeze (commit 848f331,
manifest reports/stage_e1_freeze.json), for the user's review. Stage E.2 freezes it, with the user's
changes, before any ML fit and before any research-window bar is read. It replaces design section
D15 (superseded by the user's decision U6, docs/DECISIONS.md, 2026-09-24).
```

New:

```
~~**DRAFT. Nothing in this file is frozen, hashed or registered.**~~ Written by the Stage E.1 lead
(Opus 5.5, max effort) on 2026-09-24, after the Stage E pre-registration freeze (commit 848f331,
manifest reports/stage_e1_freeze.json), for the user's review. ~~Stage E.2 freezes it~~ Stage E.2a
freezes it, with the user's
changes, before any ML fit and before any research-window bar is read. It replaces design section
D15 (superseded by the user's decision U6, docs/DECISIONS.md, 2026-09-24).

**Stage E.2a (2026-09-25) applied the user's decisions V1 to V9 (docs/DECISIONS.md, entry of
2026-09-25) to this draft.** Every edit is logged in reports/stage_e2a_ml_changes.md (old text, new
text, decision). Changed passages carry a bracketed "[V#, 2026-09-25: ...]" note; superseded text
stays visible, struck through, as in Stage E.1. The user accepted every proposed rule below (V1 to
V6, V8) except M8's, which the user amended (V7). Where a bracketed note and the text it annotates
differ, the note governs.
```

### ML-01 (V1)

Old:

```
## M1. Data partition

**Proposed rule.**
```

New:

```
## M1. Data partition

**Proposed rule.** [V1, 2026-09-25: accepted by the user.]
```

### ML-02 (V8)

Old:

```
The ML route design (this file) is frozen in E.2 before any ML fit and before any
  research-window bar is read by anyone.
```

New:

```
The ML route design (this file) is frozen in ~~E.2~~ E.2a [V8, 2026-09-25: Stage E.2 is split
  into E.2a (this freeze and the shared harness) and E.2b (the route's build)] before any ML fit and
  before any research-window bar is read by anyone.
```

### ML-03 (V1)

Old:

```
more in total and avoids a second pass over the same months later; that is the proposal.
```

New:

```
more in total and avoids a second pass over the same months later; that is the proposal [V1,
2026-09-25: accepted: the route buys the full step 2 range, 2019-05..2025-03, of one contract per
exposure, holdout-2 sealed on arrival].
```

### ML-04 (V1)

Old:

```
without new funding and a new session cap.**
```

New:

```
without new funding and a new session cap.** [V1, 2026-09-25: funding is pending: the user will
top up acct-2. Nothing is bought in Stage E.2a.]
```

### ML-05 (V1)

Old:

```
**User decides:** the partition; funding acct-2 (or another account) for the route's history and
the cap for that purchase; whether the route buys the full step 2 range per contract (proposed) or
only 2019-05..2024-02.
```

New:

```
**User decides:** the partition; funding acct-2 (or another account) for the route's history and
the cap for that purchase; whether the route buys the full step 2 range per contract (proposed) or
only 2019-05..2024-02.
[V1, 2026-09-25: decided. The partition as proposed: train, tune, normalize and distil only on
S_X..2024-02-29; March 2024 and holdout-2 are never touched; the frozen distilled rules are tested
once on the research window; holdout-2 stays the final gate. The route buys the full step 2 range
(2019-05..2025-03) of one contract per exposure, holdout-2 sealed on arrival. Funding is pending
(the user will top up acct-2); V1 sets no cap for that purchase, which stays the user's decision.]
```

### ML-06 (V2)

Old:

```
## M2. Pooling

**Proposed rule.**
```

New:

```
## M2. Pooling

**Proposed rule.** [V2, 2026-09-25: accepted by the user.]
```

### ML-07 (V2)

Old:

```
**User decides:** one pooled model versus per-cluster models.
```

New:

```
**User decides:** one pooled model versus per-cluster models.
[V2, 2026-09-25: decided: one pooled model per challenger across the 31 traded exposures, evidence
counted in trade dates.]
```

### ML-08 (V3)

Old:

```
**Proposed rule. Two challengers, 36 configurations in total, listed in full.** The TCN is dropped.
```

New:

```
**Proposed rule. Two challengers, 36 configurations in total, listed in full.** The TCN is dropped.
[V3, 2026-09-25: accepted by the user.]
```

### ML-09 (V7)

Old:

```
num_threads 8 (the
   CLAUDE.md maximum), seed
```

New:

```
num_threads 8 (~~the
   CLAUDE.md maximum~~ [V7, 2026-09-25: inside the overnight profile's 14-thread limit; the value
   stays 8]), seed
```

### ML-10 (V7)

Old:

```
Adam at 1e-3, batch 512, 8 epochs, no
```

New:

```
Adam at 1e-3, batch 512 [V7, 2026-09-25: E.2b's probe may lower
   it, by M8's rule, to leave at least 0.5 GB of VRAM free], 8 epochs, no
```

### ML-11 (V3)

Old:

```
**User decides:** the two challengers (or trees only, which halves the compute and removes the GPU
question in M8); the grids.
```

New:

```
**User decides:** the two challengers (or trees only, which halves the compute and removes the GPU
question in M8); the grids.
[V3, 2026-09-25: decided: LightGBM plus one small LSTM, 36 configurations in total, as listed; the
TCN stays dropped.]
```

### ML-12 (V4)

Old:

```
## M4. Features and targets

**Proposed rule.**
```

New:

```
## M4. Features and targets

**Proposed rule.** [V4, 2026-09-25: accepted by the user.]
```

### ML-13 (V8)

Old:

```
(the bars' volume field; E.2 reads it, this file does not);
```

New:

```
(the bars' volume field; ~~E.2~~ the route's pipeline [V8, 2026-09-25: built in
    E.2b] reads it, this file does not);
```

### ML-14 (V4)

Old:

```
**User decides:** the three horizons; the feature list; the 1.5 x cost stress in selection.
```

New:

```
**User decides:** the three horizons; the feature list; the 1.5 x cost stress in selection.
[V4, 2026-09-25: decided: the three horizons, the feature list and the 1.5 x cost stress, as
written.]
```

### ML-15 (V5)

Old:

```
**Proposed rule. A fixed procedure, no choices after training.**
```

New:

```
**Proposed rule. A fixed procedure, no choices after training.** [V5, 2026-09-25: accepted by the
user.]
```

### ML-16 (V5)

Old:

```
**User decides:** depth 2; at most 2 rules per cluster and 16 in total; the block-6 pre-test.
```

New:

```
**User decides:** depth 2; at most 2 rules per cluster and 16 in total; the block-6 pre-test.
[V5, 2026-09-25: decided: depth-2 surrogate rules, at most 2 per cluster and 16 in total, and the
block-6 pre-test, as written.]
```

### ML-17 (V6)

Old:

```
## M6. Trial accounting

**Proposed rule.**
```

New:

```
## M6. Trial accounting

**Proposed rule.** [V6, 2026-09-25: accepted by the user.]
```

### ML-18 (V6)

Old:

```
**User decides:** one trial per tested rule; the route as its own family in the Bonferroni split.
```

New:

```
**User decides:** one trial per tested rule; the route as its own family in the Bonferroni split.
[V6, 2026-09-25: decided: one trial per tested rule; the route as its own family at alpha
0.05 / (K + 1).]
```

### ML-19 (V8)

Old:

```
**Proposed rule. E.2 builds and tests all of these before any fit**
```

New:

```
**Proposed rule. ~~E.2~~ E.2b [V8, 2026-09-25] builds and tests all of these before any fit**
```

### ML-20 (V1)

Old:

```
**User decides:** nothing new beyond the partition (M1); the list is the minimum.
```

New:

```
**User decides:** nothing new beyond the partition (M1); the list is the minimum.
[V1, 2026-09-25: the partition is decided; this list stands as written.]
```

### ML-21 (V7)

Old:

```
## M8. Compute

**Proposed rule.**
```

New:

```
## M8. Compute

**Proposed rule.** [V7, 2026-09-25: amended by the user: the LSTM trains on this machine's GPU, the
Windows PC is dropped, and both challengers follow the overnight profile of CLAUDE.md. Struck text
is superseded.]
```

### ML-22 (V7)

Old:

```
- **Where:** the gradient-boosted trees on the ThinkPad (CPU). The LSTM on the Windows PC with the
  RTX 2060 Super (8 GB) if the user agrees; otherwise on the ThinkPad CPU with decision times
  sub-sampled to every 60 minutes for the LSTM only, or the LSTM is dropped (M3).
```

New:

```
- **Where:** the gradient-boosted trees on the ThinkPad (CPU). ~~The LSTM on the Windows PC with the
  RTX 2060 Super (8 GB) if the user agrees; otherwise on the ThinkPad CPU with decision times
  sub-sampled to every 60 minutes for the LSTM only, or the LSTM is dropped (M3).~~ [V7, 2026-09-25:
  the LSTM trains on this machine's NVIDIA RTX 3050 Laptop GPU (4 GB of VRAM, found 2026-09-25), on
  the data and decision times of M3 and M4 as written (no sub-sampling). The Windows PC is dropped
  from the route: nothing of the route runs on it and no data is copied to it.]
```

### ML-23 (V7)

Old:

```
- **Limits (CLAUDE.md):** at most 8 threads (half the ThinkPad's cores, capped at 8), one heavy job
  at a time across the lead and all workers, `nice -n 10`
```

New:

```
- **Limits (CLAUDE.md):** ~~at most 8 threads (half the ThinkPad's cores, capped at 8), one heavy job
  at a time across the lead and all workers,~~ [V7, 2026-09-25: the overnight profile of CLAUDE.md
  (added 2026-09-25): at most 14 threads in total across all jobs and at most two heavy jobs at once;
  the combined peak memory estimate of the running jobs under 70% of the memory available just
  before launch, anything larger in chunks; the GPU allowed for model training, one GPU job at a
  time, free VRAM checked with nvidia-smi before launch, batches sized to leave at least 0.5 GB of
  VRAM free;] `nice -n 10`
```

### ML-24 (V7)

Old:

```
- **Time per challenger (guesses; E.2 measures each with a timed probe on one fold before the
  full run and re-plans from the probe):**
```

New:

```
- **LSTM batch size [V7, 2026-09-25].** E.2b's probe re-plans the LSTM's batch size to leave at
  least 0.5 GB of the RTX 3050's VRAM free. The rule is mechanical and reads no market data: the probe
  runs one forward and backward pass of the largest LSTM configuration (32 hidden units, lookback 72)
  on synthetic inputs of the frozen shapes at batch 512, and reads the card's peak memory in use
  (nvidia-smi, CUDA context included); while less than 0.5 GB of the 4 GB stays free, the batch size
  is halved (256, then 128, then 64); if 64 still leaves less than 0.5 GB free, the probe stops and
  the case goes to the user. The result is one batch size for all four LSTM configurations; it and
  the probe's memory figures are recorded in the route manifest before any fit. Every other LSTM
  setting of M3 (learning rate, epochs, seed, grid) stays as written.
- **Time per challenger (guesses; ~~E.2~~ E.2b [V7, V8] measures each with a timed probe on one fold
  before the full run and re-plans from the probe):**
```

### ML-25 (V7)

Old:

```
  - LSTM: 12 configurations x 11 fits x 8 epochs; on the GPU about 1 to 2 minutes per epoch, so
    about 18 to 35 hours; on the ThinkPad CPU several times that, which is why the CPU fallback
    sub-samples or drops it.
```

New:

```
  - LSTM: 12 configurations x 11 fits x 8 epochs; ~~on the GPU about 1 to 2 minutes per epoch, so
    about 18 to 35 hours; on the ThinkPad CPU several times that, which is why the CPU fallback
    sub-samples or drops it.~~ [V7, 2026-09-25: on the RTX 3050 Laptop GPU. The draft's 1 to 2
    minutes per epoch was guessed for the Windows PC's desktop RTX 2060 Super; the laptop card's
    speed on this job is unknown until E.2b's probe, so the 1,056 epochs are taken as about 18 to 35
    hours or more, a guess re-planned from the probe. No CPU fallback is planned: the LSTM's data,
    decision times and grid are not reduced to save time without the user's decision.]
```

### ML-26 (V7)

Old:

```
- **The Windows PC** is outside this repository's machine rules (CLAUDE.md covers the ThinkPad).
  Using it needs the user's setup (environment, copying the training-window bar store, and bringing
  results back with hashes); no research-window data is ever copied to it.
```

New:

```
- ~~**The Windows PC** is outside this repository's machine rules (CLAUDE.md covers the ThinkPad).
  Using it needs the user's setup (environment, copying the training-window bar store, and bringing
  results back with hashes); no research-window data is ever copied to it.~~ [V7, 2026-09-25: the
  Windows PC is dropped from the route.]
```

### ML-27 (V7)

Old:

```
**Reasoning.** The trees fit comfortably on the ThinkPad inside the stability rules; the LSTM does
not at this scale. Every figure here is a guess until E.2's probe.
```

New:

```
**Reasoning.** The trees fit comfortably on the ThinkPad inside the stability rules; the LSTM does
not at this scale [V7, 2026-09-25: on the CPU; it trains on this machine's GPU]. Every figure here is
a guess until ~~E.2's~~ E.2b's [V8] probe.
```

### ML-28 (V7)

Old:

```
**User decides:** whether the Windows PC is used for the LSTM; the compute budget.
```

New:

```
**User decides:** whether the Windows PC is used for the LSTM; the compute budget.
[V7, 2026-09-25: decided: the LSTM trains on this machine's RTX 3050 Laptop GPU and the trees on the
CPU, both under the overnight profile; the Windows PC is dropped. V7 sets no compute budget: E.2b's
probe re-plans the time estimates and reports them to the user.]
```

### ML-29 (V8)

Old:

```
**Proposed sequence.**
```

New:

```
**Proposed sequence.** [V8, 2026-09-25: accepted by the user; Stage E.2 is split into E.2a and E.2b.]
```

### ML-30 (V8)

Old:

```
| 1 | E.2 (build) | the user's review of this draft; **freeze this design** (hash) before any ML fit and before any research-window bar is read; build the route's pipeline and every M7 test with known answers; the training-window bar store; timed probes for M8 | this file reviewed; the harness pieces of D11 the route shares (bars, calendars, costs, rules) |
```

New:

```
| ~~1~~ | ~~E.2 (build)~~ | ~~the user's review of this draft; **freeze this design** (hash) before any ML fit and before any research-window bar is read; build the route's pipeline and every M7 test with known answers; the training-window bar store; timed probes for M8~~ | ~~this file reviewed; the harness pieces of D11 the route shares (bars, calendars, costs, rules)~~ |
| 1a | E.2a [V8] | the user's review of this draft (decisions V1 to V9); **freeze this design** (hash) before any ML fit and before any research-window bar is read | this file reviewed |
| 1b | E.2b (build) [V8] | build the route's pipeline and every M7 test with known answers; the training-window bar store's code (filled once the history is bought); timed probes for M8, including the LSTM batch-size probe | the harness pieces of D11 the route shares (bars, calendars, costs, rules; built in E.2a) |
```

### ML-31 (V8)

Old:

```
| 2 | E.ML-buy (can be inside E.2) | buy the route's history: the full step 2 range 2019-05..2025-03 of one contract per exposure, holdout-2 chunks sealed on arrival (U4) | funding and a session cap: about $165-190 (M1) |
```

New:

```
| 2 | E.ML-buy ~~(can be inside E.2)~~ [V8, 2026-09-25: after E.2b] | buy the route's history: the full step 2 range 2019-05..2025-03 of one contract per exposure, holdout-2 chunks sealed on arrival (U4; V1) | funding and a session cap: about $165-190 (M1) [V1: funding pending] |
```

### ML-32 (V8)

Old:

```
proposal: E.ML-buy and E.ML-train run right after E.2, in parallel with K2's screening session
(different windows, one heavy job at a time on the machine); E.ML-test runs once all rules are
frozen, before K8 (whose members read other clusters' products, and which the route's cross-product
rules may overlap).
```

New:

```
proposal: E.ML-buy and E.ML-train run right after E.2, in parallel with K2's screening session
(different windows, one heavy job at a time on the machine); E.ML-test runs once all rules are
frozen, before K8 (whose members read other clusters' products, and which the route's cross-product
rules may overlap). [V8, 2026-09-25: accepted: E.ML-buy and E.ML-train run after E.2b, beside K2's
screening session; E.ML-test runs once all the route's rules are frozen, before K8. V7: the machine
now runs under the overnight profile (at most two heavy jobs at once), not one heavy job at a time.]
```

### ML-33 (V8)

Old:

```
**User decides:** the place in the order; whether E.ML-buy and E.ML-train may start before K2's
screening session ends.
```

New:

```
**User decides:** the place in the order; whether E.ML-buy and E.ML-train may start before K2's
screening session ends.
[V8, 2026-09-25: decided: after E.2b and beside K2's screening, so they may start before K2's
screening session ends; the test runs once all the route's rules are frozen, before K8.]
```

### ML-34 (V8)

Old:

```
## What E.2 must build for the route, and the data it needs
```

New:

```
## What ~~E.2~~ E.2b [V8] must build for the route, and the data it needs
```

### ML-35 (V1)

Old:

```
  $164.71-189.31 for the full step 2 range, from E.0's quotes); calendars
```

New:

```
  $164.71-189.31 for the full step 2 range, from E.0's quotes [V1, 2026-09-25: the full step 2 range;
  funding pending]); calendars
```

### ML-36 (V1-V8 (record))

Old:

```
8. M9: the route's place in the order.
```

New:

```
8. M9: the route's place in the order.

[2026-09-25: all eight decided by the user (docs/DECISIONS.md, V1 to V8): 1 by V1, 2 by V2, 3 by V3,
4 by V4, 5 by V5, 6 by V6, 7 by V7 (this machine's RTX 3050 Laptop GPU for the LSTM; the Windows PC
dropped), 8 by V8.]
```

