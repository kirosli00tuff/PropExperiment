# Brief: InputsCoder-OpusXHigh (worker-xhigh on opus) - start dates (S_X) and runner follow-ups (lead ruling OC-K)

Objective: build the frozen start-date (S_X) builder and the ONE shared S_X loader used by both the Stage E runner and the
ML route, wire the runner to it, and apply the lead's ruling on zero-variance members.

Read: reports/stage_e2b_briefs/00_common.md (binding); docs/STAGE_E_DESIGN.md D1 (declared day-session windows), D4 (the
start rule, "day-session one-minute volume of the vehicle's bars present", the full-size fallback, cross-product windows),
D6 (session table); NULL_CRITERIA.md 4.1 (read-only); strategy/research/_d1f_start_rule.py (how D.1f computed MES's monthly
medians); screening/stage_e_stats_start.py (ScreenStatsCoder's start_rule function; import it, do not edit it); the runner
report reports/stage_e2b_task1_runner_worker.md sections 0, 6, 7 (StartRuleMissing, START_RULE_PATH, Q2, Q10);
data/step2_store.py (STEP2_ROOT, step2_parquet_path) and data/stage_e_bars.py.

Build:
1. screening/stage_e_start_dates.py:
   - a builder for one SET (a cluster id K1..K8, or "ML" for the ML route's 31 price-path contracts; the set's roots come
     from the frozen files: a cluster's traded vehicles and every leg its members read; ML's list from ml_route's frozen
     inputs): monthly medians of day-session one-minute volume per root, V_ref months 2025-04..2026-05 from the research
     store, confirmation months 2019-05..2024-02 from the step 2 store; S_X via start_rule (0.25, with 0.15 and 0.40
     descriptive). "Day session" as D4 and D.1f define it; if the frozen text leaves the window for a product open, refuse
     that product by name and record the question. Reads volume and timestamps only, never prices (select columns).
   - writes reports/stage_e_start_rule_<SET>.json (schema "stage_e_start_rule/2": {"set", "products": {ROOT: {"s_x",
     "s_x_015", "s_x_040", "v_ref", "monthly_medians"}}, "inputs": [{path, sha256}], "harness_sha256", "created_pdt"}),
     read-only, refusing to overwrite; its CLI entry takes --harness-sha256 and calls preflight first.
   - the shared loader: load_start_dates(root=REPO_ROOT) -> Mapping[str, date] over every reports/stage_e_start_rule_*.json,
     refusing if two files give one root different S_X; start_date(root_symbol, root=REPO_ROOT) -> date raising the
     runner's StartRuleMissing (or a subclass) when absent.
   Nothing to read yet (no step 2 data): test on synthetic stores, including D.1f's MES medians reproduced if recorded.
2. Runner wiring (RunnerCoder has finished; you now own screening/stage_e_runner.py, stage_e_align.py and their tests for
   these edits only): replace the single START_RULE_PATH with the shared loader; keep every existing test passing (update
   only tests that asserted the old single path, and say which).
3. Lead ruling on runner Q10 (zero variance): D5's screen is "mean net P&L > 0 and daily t >= 1.0", so a member whose
   research series has mean <= 0 fails the screen whatever its variance and is Tier B (screen.passes False, t None is
   fine); only its power check is undefined (PowerCheckUndefined, recorded by name as a question for the user). Make the
   runner tier it B instead of leaving it untiered; test it.
4. The ML route (MLPipelineCoder has finished; MLTestCoder is working in ml_route/ now): do NOT edit ml_route/;
   MLTestCoder wires ml_route.inputs.load_start_dates to your loader by the names above.
Ownership: screening/stage_e_start_dates.py, tests/test_stage_e_start_dates.py, and the runner edits above.
Report: reports/stage_e2b_g2a_inputs_worker.md. Reply with path, summary <= 200 words, anything unfinished.
