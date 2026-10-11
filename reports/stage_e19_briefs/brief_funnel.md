# Brief: FunnelCoder-OpusXHigh (Stage E.19 Task 2, worker-xhigh on opus)

Objective: implement the funnel simulator in prop_econ/ exactly as reports/stage_e19_briefs/sim_spec.md sections 2
to 5 specify, with tests that pin hand-computed paths to the cent. The lead owns the model; where the spec is
ambiguous or wrong, write the question into your return (and into reports/stage_e19_briefs/funnel_questions.md) and
take the reading the spec's wording favours, flagged in the code; never decide a modelling question silently.

Inputs: sim_spec.md; rules_schema.md; reports/stage_e19_briefs/rules_provisional.json (development and tests only;
the final rules JSON, reports/stage_e19_rules.json, is being written in parallel by another worker in the same
structure); prop_econ/types.py (the lead's interface: ShockSet, ProductSpec; do not change it, ask instead);
ml_route_v2/payout_sim.py and rules/xfa_rules.py for patterns only (read-only; frozen; take no rule values from them).

Files to write:
- prop_econ/rules.py: load and validate a rules JSON (schema version, every leaf has a RULE, readings[0] equals the
  structured value), select a size, and apply alternative readings by dotted path (returns a new object; no mutation).
  A frozen dataclass view of one size's rules for the simulators.
- prop_econ/funnel.py: the scalar reference (run_attempt, run_xfa) for one path from one ShockSet row: sections 2 to 4,
  plain readable code; this is the specification the vectorized code is pinned to.
- prop_econ/vec.py: the same rules vectorized over paths (numpy), chunked over paths to bound memory, identical
  results path for path (to 1e-9 dollars) to the scalar reference.
- prop_econ/assemble.py: section 5 (fees with rebills, reset credits and resets; activation; Back2Funded; cycles with
  the attempt cap; campaigns with 1 or 5 slots and the $5K / $10K targets; P50 / P80). Pure functions on the pools,
  seeded.
- tests/test_prop_econ_funnel.py (and more test files named tests/test_prop_econ_*.py if useful). Hand ShockSets
  only (no store reads). Required: (1) a Combine pass then an XFA payout, amounts to the cent; (2) a fail and reset,
  with the fees (start price, a rebill that adds a credit, a reset paid by the credit, a reset paid in cash); (3) a
  drawdown lock: the XFA floor trails to the lock and stays; the floor after the first payout; (4) a payout under
  each path, and a refusal under each (too few winning days; the 40% consistency breach; the minimum request);
  (5) the five-account cap: never more than max_active_xfas live XFAs in a 5-slot campaign. Also: the DLL stop; an
  intraday MLL breach through w with a positive close; the micro/full vehicle switch; the lot cap from the prior
  close's tier with each scaling_boundary reading; n >= 1; integer mode; the call-up after n payouts; the horizon;
  vectorized equals scalar on random ShockSets over several configurations (both paths, DLL on and off, both modes,
  zero and positive edge); determinism by seed; the loader's validation and reading overrides.
- Performance: 20,000 XFAs x 756 days in about a minute on one core is the target; report the measured time.

Boundaries: write only prop_econ/rules.py, funnel.py, vec.py, assemble.py (more prop_econ/ modules if needed, but not
returns.py, which ReturnsCoder-OpusHigh writes in parallel, and not types.py) and tests/test_prop_econ_*.py except
tests/test_prop_econ_returns.py. No market data reads, no grid runs, no edits anywhere else (ml_route_v2/, rules/,
sim/, screening/, data/ are frozen). Run only your own tests (`uv run pytest -q tests/test_prop_econ_funnel.py ...`),
never the full suite; `uv run ruff check prop_econ tests/test_prop_econ_*.py` clean. Run under `nice -n 10`. Do not
spawn workers. Do not commit.

Return (three things): the paths; a summary of at most 200 words (what is implemented, test count and result,
measured speed); open questions and anything unfinished.
