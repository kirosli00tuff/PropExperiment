# Brief: MLTestCoder-OpusXHigh (worker-xhigh on opus) - the ML route's test side and M7.8 completeness (lead ruling OC-L)

Objective: complete the ML route so that everything M7.8 names is built and tested before the harness freeze: the Stage E
engine adapter for the distilled-rule wrapper, the E.ML-test entry, the training-window DSR and PBO (M6), the wiring of
the shared S_X and release-calendar loaders, and the lead's ruling on targets inside the fill guard.

Read: reports/stage_e2b_briefs/00_common.md (binding); reports/stage_e2b_task2_ml_worker.md (the pipeline as built,
sections 1, 4, 7, 8); docs/STAGE_E_ML_DESIGN.md (FROZEN) M4, M5, M6, M7 (esp. item 8: "E.2b's harness manifest hashes the
route's whole pipeline (the feature and target builders, the block cut, the CPCV splitter, the selection, surrogate,
pre-test, ranking and write-up code, and every M7 test) before E.ML-buy; ... E.ML-train and E.ML-test refuse to run when
any hashed file differs"), M9; the Stage E runner's member protocol strategy/stage_e/interface.py (StageEMember.on_minute)
and screening/stage_e_runner.py / stage_e_engine.py interfaces (reports/stage_e2b_task1_runner_worker.md section 0);
funnel/multiple_comparisons.py and strategy/research/_d1f_statistics.py (existing DSR/PBO code; reuse, do not edit).

Build (you own ml_route/ now; MLPipelineCoder has finished):
1. ml_route/stage_e_adapter.py: a multi-leg adapter holding one DistilledRuleStrategy per traded exposure of the cluster
   (ML-A15), with the lead's bars fed through observe_lead, implementing StageEMember so the Stage E runner/engine runs a
   distilled rule with D8 costs and the D9 constraint set. Document it in the module docstring (CanaryCoder uses it).
2. The E.ML-test entry (M5, M6, M9): python -m ml_route.test ... --harness-sha256 SHA: preflight first; loads the frozen
   rules and verifies the hash chain (verify_model_file, verify_chain, rule_spec_from_json's hash check); refuses on any
   difference; runs each frozen rule on the research window through the Stage E runner's path with explicit data roots;
   writes the results and the trial accounting M6 requires. Everything the frozen text leaves open: refuse by name and
   record the question.
3. The training-window DSR and PBO that M6 reports, from the ledger's validation daily P&L series, reusing the existing
   statistics code.
4. Wire ml_route.inputs.load_start_dates to screening.stage_e_start_dates.load_start_dates (InputsCoder is writing it now
   with exactly that name and start_date(root_symbol) raising StartRuleMissing; import lazily or test with monkeypatch
   until it lands) and ml_route.inputs.load_event_calendar to screening.stage_e_rules.load_release_calendar (the runner's
   schema, reports/stage_e2b_release_calendar.json, being assembled now). F13-F15 read that calendar.
5. Lead ruling OC-M on MLPipelineCoder's Q3: D9.5a governs every simulated fill, so a target's entry or exit fill that
   would land in [release, release + 2 min) is deferred to the open of the first bar at or after release + 2 min, and the
   D8 event-window cost applies to fills in [release, release + 30 min), exactly as the engine does; the target is not
   set missing for this reason. Keep a count of deferred fills in the dataset summary.
6. M7.8 completeness: list every item M7.8 names and where it lives (file, function, test); build anything missing.
Tests: known answers, the adapter through the Stage E engine on synthetic bars, the test entry refusing on a changed rule
or model hash, DSR/PBO known answers, every existing ml_route and canary test still passing (run them).
Report: reports/stage_e2b_g4_mltest_worker.md. Reply with path, summary <= 200 words, anything unfinished.
