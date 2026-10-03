"""ML route v2 phase 1 on real data (Stage E.12 Task 1b; lead rules P-1, P-1a, P-2, P-3; freeze
review F-2, F-3).

``python -m ml_route_v2.phase1 build|register|run --harness-sha256 SHA --freeze-sha256 SHA``
(run also ``--expected-list-sha256 SHA``). No flag names a path or a vehicle: the manifest is
reports/stage_e12_ml_v2_freeze.json, the reports go to reports/, the tests to
ledger/ml_v2_config_ledger.jsonl, the state to ~/.cache/propexp_e12_phase1, and the vehicles are
the ranking's subset (reports/stage_e12_ranking.json) whose step 2 stores exist.

- world.py: the phase-1 vehicles from the ranking (F-3), the world from the frozen stores (P-1
  coverage, P-1a MES contingency, P-3 start dates and bars);
- build.py: the build step (panel, c/sigma filter, risk table, reports, saved state);
- gate0_stage.py: the P-2 Gate 0 list, its registration and the one run;
- freeze.py: the v2 freeze manifest check every step runs first;
- cli.py: the command line and the canonical paths.
"""

from ml_route_v2.phase1.freeze import FreezeError, verify_v2_freeze
from ml_route_v2.phase1.world import (
    Coverage,
    Phase1Error,
    Phase1Subset,
    Phase1WindowError,
    Phase1World,
    phase1_subset,
    phase1_world,
    signal_coverage,
)

__all__ = ["Coverage", "FreezeError", "Phase1Error", "Phase1Subset", "Phase1WindowError",
           "Phase1World", "phase1_subset", "phase1_world", "signal_coverage", "verify_v2_freeze"]
