"""E.32b economics: binds econ32b_core to E.28's simulator (A3_funnel.py, A3_models.py and A3_run.build_state,
copied unchanged from reports/stage_e28_briefs/work/A3_econ/; see COPY_MANIFEST.json).

The only generalisation of E.28's per-trade layer: T round trips a day and per-trade SD sigma_T are parameters
(E.28: T = 20, sigma_T = sigma_1m). Daily P&L in USD is normal with mean m = T d v and SD s = sqrt(T) sigma_T v,
d = mu - c, exactly E.28's DayLaw (with T = 20 the expressions are E.28's, operation for operation).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

WORK = Path(__file__).resolve().parent
if str(WORK) not in sys.path:
    sys.path.insert(0, str(WORK))

import A3_funnel as F  # noqa: E402
import A3_run as R  # noqa: E402

from econ32b_core import Evaluator  # noqa: E402

MODEL_CONSTANTS = {"paths_per_pool": F.N_PATHS, "cycles": F.N_CYCLES, "campaign_replications": F.N_REPS,
                   "horizon_trading_days": F.HORIZON, "attempt_cap": F.ATTEMPT_CAP,
                   "campaign_days": F.CAMPAIGN_DAYS, "campaign_target_usd": F.CAMPAIGN_TARGET,
                   "base_seed": F.BASE_SEED, "size": 1}


def build_state(firms: list[str]) -> dict[str, Any]:
    """E.28's models, common random numbers and cycle index draws, built once in the parent (forked workers
    share the read-only arrays)."""
    R.build_state(firms)
    return R._STATE


def make_evaluator(state: dict[str, Any], firm: str, t_rt: int, sigma_t: float, v: float) -> Evaluator:
    if t_rt < 1:
        raise ValueError(f"T must be >= 1 round trip a day, got {t_rt}")
    if not (sigma_t > 0 and v > 0):
        raise ValueError(f"sigma_T and v must be positive, got {sigma_t}, {v}")
    model = state["models"][firm]
    d_att, d_xfa = state["draws"][firm]
    att, xfa = state["idx"]
    s = math.sqrt(t_rt) * sigma_t * v

    def evaluate(d: float) -> dict[str, Any]:
        law = F.DayLaw(m=t_rt * d * v, s=s)
        pools = F.simulate_pools(model, law, d_att, d_xfa)
        st = F.cycle_stats(model, pools, att, xfa)
        p = F.campaign_p_reach(model, pools)
        return {"ev": st.ev, "se": st.se, "ev_ex_api": st.ev_ex_api, "p10k": p, "stats": dict(st.__dict__)}

    return evaluate


def model_limits() -> dict[str, dict[str, Any]]:
    """Each firm model's 50K plan, MLL and DLL (USD), for the check against F4's firm facts."""
    import A3_models as M

    return {f: {"plan": m.plan, "mll_usd": m.mll_usd, "dll_usd": m.dll_usd}
            for f, m in M.firm_models().items()}
