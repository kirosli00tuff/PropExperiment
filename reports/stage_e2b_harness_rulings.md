# Stage E.2b Task 8: the lead's rulings on the harness review

Review: reports/stage_e2b_harness_review.md (HarnessAuditor-FableMax, worker-max on fable, 17:58-18:26 PDT
2026-09-26), against manifest v1 (sha256 eb78185a36e4c5a31e864aa4bdc2eb4d425e5705b67029af4ceb6a438de44662).
Counts: BLOCKING 1, SHOULD FIX 3, NOTE 11. The review was not re-run. Every fix changes a hashed file, so
manifest v1 is superseded by v2 (below); the files that changed after the audit are listed at the end.

## Findings, rulings and fixes

| Id | Grade | Ruling | Fix and owner | Proof |
|---|---|---|---|---|
| F-1 | BLOCKING | Fix. The package init the template asks for ran unhashed on every screening run; the gap D.1f's F3 closed, one directory over. | (a) strategy/members/__init__.py is created empty by the lead and frozen in the harness manifest; the cluster freeze hashes it and refuses unless it is empty (RunnerCoder, screening/stage_e_freeze.py). (b) The preflight scans strategy/members/ and refuses any *.py outside the frozen init and the per-cluster packages k1..k8 (lead, screening/harness_freeze.py). (c) A static allowlist of imports, banned builtins and no assignment to an imported module's attributes, checked for every member module at freeze time and at run time (RunnerCoder); the template states it. RunnerCoder's additions, accepted: star imports, getattr/vars/__builtins__, dunder attributes, mutating calls on imported objects and file I/O are refused too, and resolve_member checks that Python would load the checked files. | tests/test_harness_freeze.py::test_member_code_outside_the_cluster_packages_is_refused; tests/test_stage_e_freeze.py (the review's E2 exploit refused at freeze time and when planted afterwards) |
| F-2 | SHOULD FIX | Fix. | The preflight refuses (1) any unlisted extension module or loose .pyc under the harness directories and strategy/members/, (2) any unchecked hash-based .pyc for a harness source, and, beyond the review's text, (3) any timestamp-based .pyc that Python would trust (its recorded mtime and size match the source) whose code object differs from a fresh compile of the source (lead). The review's third suggestion (launch every entry point with a fresh PYTHONPYCACHEPREFIX) becomes an instruction for the Stage E session prompts, not code: (2) and (3) already refuse every pyc Python would load in place of its source. | tests/test_harness_freeze.py: unchecked-hash (the review's E3), forged timestamp, honest and stale, binary and loose pyc |
| F-3 | SHOULD FIX | Fix. | The start-rule loader re-runs start_rule on each entry's recorded monthly medians and first trade dates and refuses when s_x, v_ref, the sensitivity dates or m_star differ; each entry pins the step 2 parquet's sha256 it was computed from, and confirmation reads refuse a store that hashes differently (InputsCoder; StartRuleInconsistent); the ML route's store reads are pinned the same way (MLTestCoder). MES, a signal leg only, keeps D.1f's confirmation parquet as its S_X source and confirmation store (no MES step 2 store is bought). The cluster prompts state the start-rule files' sha256 (instruction). | tests/test_stage_e_start_dates.py (the review's E1 contradictory s_x refused), tests/test_stage_e_loader.py and tests/test_stage_e_runner.py (a doctored step 2 store refused), tests/test_ml_route_review_fixes.py (the ML store pinned) |
| F-4 | SHOULD FIX | Fix: V6 (docs/DECISIONS.md, audit ML-A14) makes the route a ninth Holm family. | MAX_FAMILIES = 9; holm_alpha_k validates K in 1..9; k_from_tiers(tiers, route_tested=...) with the keyword required (ScreenStatsCoder); E.ML-test's Holm entry names it and 0.05 / (K + 1) (MLTestCoder). | tests/test_stage_e_stats.py (K = 9; the route adds one; 0.05/3 and 0.05/9 by hand) |
| NOTE-1 | NOTE | Accepted: closure-gap and session-end exits fill at the decision bar's close, flagged and counted (ruling OC-T); no future information. | none | - |
| NOTE-2 | NOTE | Accepted: the locked-market test reads the fill bar's range, conservative direction only. | none | - |
| NOTE-3 | NOTE | Accepted, with an instruction: published instants stand in for scheduled ones (15 moves, 14 cancellations); cluster and route run summaries say so. | instruction | - |
| NOTE-4 | NOTE | Fix (cheap, hardens M7.4): the training store books every row by the group calendar (check_bookings) and refuses unbookable, mislabelled and on-or-after-2024-03-01 rows by name. | MLTestCoder | tests/test_ml_route_review_fixes.py (bookings: a March 2024 bar labelled February, a research bar relabelled 2023, a mislabelled row) |
| NOTE-5 | NOTE | Fix: V7 plans no CPU fallback, so a training fit refuses by name without CUDA and records its device; only the probes may run on CPU. The LSTM end-to-end test skips on a machine without CUDA (lead). | MLTestCoder | tests/test_ml_route_review_fixes.py (no CUDA refused before any read; device in every fit record), tests/test_ml_route_e2e.py |
| NOTE-6 | NOTE | Accepted, with an instruction: cluster prompts state the cluster freeze file's sha256 and the start-rule files' sha256; each record already carries cluster_freeze_sha256 and the lead's end check compares git status. | instruction | - |
| NOTE-7 | NOTE | Accepted: the embargo's first hour in the unsealed February 2024 chunk is dropped unread by trade date, as for MES. | none | - |
| NOTE-8 | NOTE | Accepted: a seal failure on resume purges a paid chunk (cost, not integrity). | none | - |
| NOTE-9 | NOTE | Accepted: V10-5's separate roots are sibling directories on the PC, isolated by the allowlist and the agent's checks. | none | - |
| NOTE-10 | NOTE | Accepted: .claude/settings.json, .claude/agents/*.md, docs/ACCESS.md and docs/HOLDOUT_UNLOCK_LOG.md travel in the export; no secret in them. | none | - |
| NOTE-11 | NOTE | Fix (V10-2's letter): lstm_machine.json, written before the first LSTM fit, names the host, GPU, VRAM and the A-1 batch size; later fits refuse another batch size or a card without 0.5 GB free by the A-1 measure. | MLTestCoder | tests/test_ml_route_review_fixes.py (record written, kept and checked; another batch or the CPU refused; one test on the real RTX 3050) |

## Files changed after the audit, and the new manifest

Every fix above changed hashed files, so manifest v1 (eb78185a36e4c5a31e864aa4bdc2eb4d425e5705b67029af4ceb6a438de44662,
1,028 files, 17:56) is superseded by **manifest v2: sha256 ef2074f76d0dcdec91ed359333cff379cad0e9c211da052fcf34aae50ba414b0,
1,031 files** (harness_code 135, frozen_input 808, earlier_freeze 38, import_closure 11, stage_e_test 39), built
18:59:46 PDT at HEAD 2634b65 by `python -m screening.harness_freeze build`, verified by `verify --expected` (v1's hash is
now refused). Changed after the audit (26): data/stage_e_bars.py, ml_route/{adapters, dataset, features, freeze_scope,
inputs, manifest, probes, store, test, train}.py, screening/{harness_freeze, stage_e_freeze, stage_e_runner,
stage_e_start_dates, stage_e_stats}.py, strategy/stage_e/_template.py, tests/{_stage_e_synthetic, test_harness_freeze,
test_ml_route_e2e, test_ml_route_stage_e_inputs, test_stage_e_freeze, test_stage_e_loader, test_stage_e_runner,
test_stage_e_start_dates, test_stage_e_stats}.py. Added (3): ml_route/lstm_machine.py, strategy/members/__init__.py
(empty), tests/test_ml_route_review_fixes.py. Removed: none. Nothing outside the review's findings changed after the
audit except the lead's skipif on the LSTM end-to-end test (NOTE-5).

**Manifest v3 (the committed one): sha256 cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45, 1,032 files**
(stage_e_test 40), built 19:14 PDT. At staging the lead found tests/_compute_fixtures.py (the helper the compute tests
import) outside the manifest's test patterns and outside the commit; screening/harness_freeze.py's TEST_PATTERNS gained
it, which changed that file and the manifest. Nothing else changed between v2 and v3. After v2 the full suite ran clean
(19:00-19:14: 2863 passed, 2 skipped, 1 xfailed, 0 failed); after v3, tests/test_harness_freeze.py, the static check and
the three compute test files: 143 passed. v1 and v2 are refused by the preflight.
