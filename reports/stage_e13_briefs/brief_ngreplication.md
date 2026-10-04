# Brief: ReplicationDesigner-OpusXHigh (Stage E.13 Task 4: the backward NG replication, draft and cost)

Read reports/stage_e13_briefs/research_rules.md first and follow it (its data boundaries bind you most of
all). Your pages folder for the few web lookups you need: reports/stage_e13_briefs/pages/ReplicationDesigner/.

## Objective (one)
Draft, as a pre-registration that the next stage could freeze and run unchanged, a backward replication of
the E.12 Gate 0 family B near-miss for NG, and establish its feasibility, cost, power and honest prior. You
draft; the lead rules on every design choice (provisional rulings below; list every other choice you make in
the choices table for the lead's ruling). Nothing is run, bought or frozen in this stage.

## The hypothesis (fixed by the stage prompt; do not change it)
The Gate 0 family B result for NG at h60 (and hF, as the second of exactly two tests) reflects an edge that
also holds on 2010-01-04..2019-05-03 NG data, a period no part of the program has read.

## Inputs (read by section; code and docs only)
- reports/E.12_RETURN.md: lines 7-32 (verdict), 476-562 (purchase and Gate 0, the family B table), 563-573
  (the 2010 extension quote), 619-700 (open choices, decisions).
- docs/STAGE_E_ML_V2_DESIGN.md: V2.0 (47-131), V2.1 (134-260), V2.2 decision clock (263-334), V2.2b Gate 0
  (336-433), V2.3 signals (435-550), V2.4 normalization (551-583), V2.5 targets (584-599).
- The frozen code: ml_route_v2/ (gate0.py, panel.py, normalize.py, targets.py, cost_filter.py, cpcv.py,
  signals/, phase1/build.py, phase1/gate0_stage.py, phase1/world.py, phase1/_io.py), and what they import
  from screening/, data/, rules/ (sessions, roll blackout, calendars, D8 costs). Read code by grep/sections.
- reports/stage_e12_quotes_ext2010.json and .md (quote records: costs and chunk counts, not market data).
- reports/stage_e12_gate0_list.json (the registered test list) may be read. reports/stage_e12_gate0.json and
  every other result table: you may print its KEY NAMES / schema only (to learn whether per-row OOF
  predictions or per-pair thresholds were persisted), never its values beyond what E.12_RETURN.md prints.
- No bar file, store, cost sample or market-data file of any window may be opened.

## Provisional lead rulings (follow them; if the code shows one cannot work, say so with file:line evidence
## and propose the alternative in the choices table)
- L4-1 Model rule, stated before any 2010-2019 data exists: the model is M1, the frozen Gate 0 family B ridge
  (lambda 0.1, every feature the E.12 build computed, plus product and cluster identifiers, pooled over the
  E.12 phase-1 panel, one model per horizon), fitted ONCE on the whole E.12 training panel, then applied
  unchanged to NG rows of the replication window. Reason: the hypothesis is about that model's result; any
  other model tests a different hypothesis. M2 (an NG-only ridge at lambda 0.1 on NG's own-path features,
  fitted once on NG's E.12 training rows) is the fallback ONLY if (a) the frozen code cannot fit M1 on the
  E.12 stores without modification, or (b) a feature that is live on NG rows cannot be computed for the
  replication window from purchasable data and official calendars. Establish (a) and (b) from the code; say
  which holds; if M2 applies, say plainly that it tests a weaker, different hypothesis.
- L4-2 Trade rule: Gate 0's: on each NG decision row of the replication window, trade sign(r_hat) when
  |r_hat| is at or above the threshold q = the 80th percentile of |r_hat| over NG's training-window OOF
  predictions at that horizon, exactly as Gate 0 formed them. The threshold is never computed from
  replication-window data. Establish from the code whether E.12 persisted the OOF predictions or the
  threshold. If not, the next stage recomputes NG's OOF predictions by re-running the frozen CPCV fit code
  deterministically, must reproduce E.12's NG h60 row (518 trades, t_B 2.51, mean 5.569 ticks) to 1e-9
  before reading q, and computes nothing else; flag this as a V24 question for the user (a reproduction, not a
  new test or a rerun of the gate's decision).
- L4-3 Features: M1 needs every feature live on NG rows. Determine from the code which features are live on
  NG rows, which read other roots (G17 leads; member legs), and which read calendars (release flags G13-G15,
  NG storage-day flag, month-end, CME holidays/early closes, roll blackout). Legs not listed in a period get
  the design's "not applicable" treatment (0 plus its flag), as in training: MBT (in E.12 its lead was
  n/a for nearly all rows, S_X 2024-01-02) and MES (excluded entirely by P-1a: no feature). A leg that WAS
  listed in 2010-2019 is bought, never set to n/a (that would change the model's inputs).
- L4-4 Window: the replication window runs from the first date the data and every feature's warm-up allow
  to 2019-05-03. Databento's GLBX.MDP3 history appears to start in June 2010 (the E.12 quote failed every
  2010-01..2010-06 chunk): confirm from Databento's public dataset page (sourced) and the quote record. State
  the D4 start-rule amendment the purchase and build need, and confirm from the code and records that no
  program file has ever read NG (or any leg) before 2019-05.
- L4-5 Cost: D8 at the vehicle (NG is its own vehicle and price path), the frozen cost table applied
  unchanged; the pass bar is gross, so cost enters as c(NG,h) only. State plainly that D8 was calibrated on
  2025-2026 samples and 2010s costs may differ.
- L4-6 Pass bar: two tests (NG h60, NG hF). A test passes iff mean gross g >= 1.5 x c(NG,h) (c from D8 over
  the test rows), the one-sided date-clustered t_B (Gate 0's statistic) has p <= 0.025 (Bonferroni 0.05 / 2),
  at least 30 trades, and the sign is Gate 0's (trade sign(r_hat); mean g > 0). The replication passes iff at
  least one test passes. N: 471 -> 473.
- L4-7 Order of events for the next stage: freeze the pre-registration (hash in STATE) -> build calendars
  from official pages (no prices) -> buy -> build stores (checks print counts only, never prices or returns)
  -> fit M1 (or reproduce q) -> compute replication features -> one evaluation. Nothing in the 2010-2019 data
  is summarized, plotted or printed before the evaluation.

## What the draft must contain (reports/stage_e13_ng_replication_draft.md)
1. Hypothesis (as above) and the two tests.
2. Model and the stated model rule (L4-1), with which of (a)/(b) holds per the code.
3. Features: a table of every feature live on NG rows: name, what it reads (own path, which leg, which
   calendar), available in 2010-2019 (yes / n/a by design / needs purchase / needs calendar build).
4. Trade rule and threshold (L4-2), with the persisted-or-recompute finding (file:line).
5. Window, warm-up, D4 amendment, roll and calendar sources (L4-4).
6. Cost (L4-5); NG's vehicle and sizing on a 50K and a 150K XFA: contract value, tick value, a published
   NG volatility (sourced; not the program's bars), the dollar size of a typical h60 move per contract, the
   lot limits and MLL, and whether one NG contract fits V2.8's rules (target daily sigma 0.10 x D, max trade
   loss 0.25 x D). Check whether a micro Henry Hub contract exists (sourced) and whether Topstep lists it
   (cite reports/stage_e0_topstep_facts.json by grep, or say not found).
7. Pass bar, trial count (L4-6), and what a pass and a fail each mean for the program (one paragraph each).
8. Feasibility and cost: what must be bought (NG alone, or NG plus each leg), per item from E.12's quote
   record (per_contract in reports/stage_e12_quotes_ext2010.json; NG $8.52 for 106 of 112 chunks), whether
   the funds left (acct-1 $1.609980, acct-2 $18.070270) cover it under the 1.03 margin and the one-account-per-
   item placement rule, and the top-up needed. Also the calendar builds needed and the build effort in
   sessions. No Databento call: if an item is not in E.12's record, say so; do not quote it.
9. Prior, stated honestly:
   - the probability that the best of 81 family B tests reaches t >= 2.51 under the global null: compute
     it under independence (1 - (1 - p)^81 with p = 0.0062) and give the Bonferroni bound, and say how
     positive correlation among the tests moves it; note NG h60 and hF share entries;
   - the winner's-curse shrinkage: power of the replication at a true effect equal to the observed one,
     half of it, a quarter, and zero, using t ~ (observed t / sqrt(4.82 years)) x sqrt(replication years) and
     the expected trade count (E.12: 518 trades in 4.82 years at h60);
   - the NG regime change between 2010-2019 and 2019-2024 (shale supply growth, LNG exports from 2016, price
     level and volatility), from published sources (EIA pages preferred), sourced with quotes;
   - your overall odds that the replication passes, with the reasoning.
10. A design-choices table: choice | options | proposed | rationale | lead ruling (leave the last column
    blank, or "per L4-x" where a provisional ruling covers it).
11. A one-paragraph recommendation: run, run later, or drop, and the reason.

## Stopping rule and budget
Done when sections 1-11 are written and every claim about the code cites file:line. Web lookups only for
items 4 (Databento start date), 6 (micro NG, NG volatility) and 9 (regime): at most 40 WebSearch calls.

## Boundaries
No market data of any window, no result-table values beyond E.12_RETURN.md, no Databento call, no edits
outside your draft and pages folder, no freeze, no commit. Other workers own venues, trend/carry and
information sources.
