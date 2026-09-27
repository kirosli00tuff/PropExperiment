# Stage E.2b: rules common to every worker (read this first, then your own brief)

You are a worker in Stage E.2b of PropExperiment (repo /home/kiros-li/Documents/GitHub/PropExperiment).
The lead (Opus 5.5) planned the stage; you own ONE objective, stated in your brief. Read CLAUDE.md's
sections "Invariants", "Compute limits" (including the overnight profile) and "Context hygiene"; they apply to you.

## Hard boundaries (a breach stops the stage)
- Never edit: any file listed in reports/stage_e1_freeze.json or reports/stage_e2a_ml_freeze.json (docs/STAGE_E_DESIGN.md,
  docs/NULL_CRITERIA_E.md, docs/STAGE_E_ML_DESIGN.md, the E.0 catalog and research files, ...); the E.2a hashed tables
  (reports/stage_e2a_costs.json, stage_e2a_vehicle_sizes.json, stage_e2a_vehicles.json, stage_e2a_vehicle_rule_readings.md,
  stage_e2a_epsilon_declaration.md, stage_e2a_epsilon_declaration_addendum.md, stage_e2a_source_window_amendment.md,
  stage_e2a_epsilon.json and reports/stage_e2a_funnel/); docs/NULL_CRITERIA.md; reports/stage_d1f_confirmation_list.md;
  REGISTRATION.md (stays 0 bytes); anything under live/ or ops/; screening/runner.py (lead ruling OC-A: it stays
  byte-identical as the D.1f-frozen MES runner; import from it, never edit it).
- Never touch holdout data: data/sealed/, the sealed chunks, the unlock log; never call data.holdout's unlock path.
  No TopstepX reference of any kind. No purchase: no billable Databento request, no cap change.
- Data you may read: synthetic data you generate. You may read E.2a's recorded row counts and hashes from reports/.
  You may NOT open any Stage E product's bar parquet (data/processed/<ROOT>/ for any root but MES) or any vendor price
  file. Only RunnerCoder's MES regressions read MES's own research bars.
- Git: no commit, no stash, no checkout/restore/reset of files, no branch switch. Other workers' uncommitted work lives in
  the same tree. Do not edit files another worker owns (listed in your brief); if you need a change there, report it.
- Python environment: run everything as `uv run --no-sync ...`. Only MLPipelineCoder adds packages (uv add); nobody else
  runs uv sync/add/lock.

## Compute (overnight profile, stability over speed)
- Any job expected to take over 2 minutes, use over 2 GB of RAM or over 2 threads, and any run of more than your own
  test files, goes through the two-slot gate: `reports/stage_e2b_briefs/heavy.sh <command>` (waits for a free slot,
  runs at nice 10). Cap threads with OMP_NUM_THREADS etc.; at most 6 threads per job unless your brief says otherwise.
- Check `free -m` before anything big. Do not run the whole test suite; run your own test files plus the existing test
  files your brief names. The lead runs the full suite at integration points.
- Keep command output short (pytest -q, tail of logs, summaries not rows). Read files by section (grep, line ranges).

## Code rules
- Match the surrounding code's style (frozen dataclasses, explicit errors naming the case, no silent fallbacks).
- Cross-platform (user decision V10: the harness must also run on native Windows Python): pathlib paths, no os.fork,
  multiprocessing only with the spawn context, no shell=True or shell-specific calls, no fcntl/resource/signal.SIGKILL
  or /proc, /dev/shm, open text files with encoding="utf-8". Use compute.platform.lower_priority() instead of os.nice,
  and compute.platform.apply_thread_limits(n) for thread caps (the file exists; do not edit it).
- Stage E entry points (anything a later session runs on real data: a cluster screening or confirmation run, an ML
  train or test job, a purchase) call screening.harness_freeze.preflight(expected_sha256) before reading any bar, with the expected manifest
  sha256 taken as a required argument (--harness-sha256), and record the returned sha256 in every output (the file
  exists; do not edit it). Tests replace it with monkeypatch; add one test per entry point proving the entry refuses when
  preflight raises. No argument or environment variable may skip it.
- Frozen values (rules, costs, calendars, epsilon, q_c, windows, seeds, thresholds) come from the frozen files or module
  constants, never from arguments or environment variables a session could vary.
- Tests first where practical (the user's rule), known answers, and aim for 80%+ line coverage of your new modules.
- Where a frozen rule cannot be encoded without a new choice: do not guess. Make the code refuse that case by name and
  record the question in your worker report.

## Return (at the end)
- Write your full report to the path your brief names: files created and modified, each test file with its test count
  and what each test proves, commands run with their results, deviations, open questions, anything unfinished.
- Final reply to the lead: the report path, a summary of at most 200 words, and anything you could not finish.
- Times in PDT (TZ=America/Vancouver date).
