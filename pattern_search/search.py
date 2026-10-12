"""The search and the SCREEN (reports/stage_e20_plan.md sections 7, 8 and 9; F6, F7).

- ``admissibility``: one pass of the frozen c/sigma filter on the whole search panel
  (pipeline._filter: c_sigma, the risk table, the admissible (vehicle, horizon) pairs). An empty
  admissible set refuses (``EmptyAdmissible``): the frozen pipeline would turn it into no filter
  at all (pipeline.py: ``admissible=adm or None``); plan 8 makes it a failed screen.
- ``run_nested`` / ``run_final``: cpcv.nested_cpcv and cpcv.final_selection with the frozen
  arguments of plan 8: the 45 frozen CONFIGS, score_fn_for(the whole-panel risk table) (the
  per-split tables come from risk_fn, which overrides it inside cpcv), the frozen ConfigLedger in
  the state directory (cpcv._prepare registers the 45 config ids before the first fit), the
  admissible pairs, the training calendar and split_risk_fn(panel). Resumable per (config,
  split) unit by the frozen state_dir/cpcv/cpcv_units.jsonl.
- ``screen``: plan 9 items 1-3 and the final-selection condition: median-path daily t
  (pipeline.record_figures, its _daily_t) >= 2.0; PBO (cpcv.pbo_cscv on config_daily) < 0.5,
  counted as not < 0.5 when it raises, returns degenerate or a NaN pbo; annualized net Sharpe of
  the path-averaged record in [0.5, 4.0] (above 4.0 fails item 3 as written and raises the
  leakage alarm flag for the record); final_selection must return a configuration.
- ``reported``: the DSR at N_total = 528 passed explicitly (cpcv.dsr_at_n on the path-averaged
  record, Sharpe variance over the finite config_sharpes, as pipeline._stats), the
  per-configuration table, the final configuration's own CPCV OOS t and Sharpe. The trade-level
  items (per-product round trips, 1.5 x slippage, t4 and r_ROD shares) are pattern_search.oos.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pattern_search import constants as K
from pattern_search import guard  # noqa: F401  (F3)

LEDGER_FILE = "ledger.jsonl"  # the frozen pipeline's name (pipeline.LEDGER_FILE)
CPCV_DIR = "cpcv"


class SearchRefusal(RuntimeError):
    """The search cannot proceed as the plan says."""


class EmptyAdmissible(SearchRefusal):
    """No (vehicle, horizon) pair passes the c/sigma filter: the search has no model."""


def frozen_configs() -> tuple[Any, ...]:
    """The 45 frozen configurations in CONFIGS order (E20S-nn = CONFIGS[nn - 1])."""
    from ml_route_v2.configs import CONFIGS

    if len(CONFIGS) != K.N_CONFIGS:
        raise SearchRefusal(f"the frozen grid has {len(CONFIGS)} configurations, not 45")
    return tuple(CONFIGS)


def admissibility(panel: Any) -> dict[str, Any]:
    from ml_route_v2.pipeline import _filter

    filt = _filter(panel)
    if not filt["admissible"]:
        raise EmptyAdmissible("no (vehicle, horizon) pair passes the c/sigma filter (tau "
                              "0.167): the search has no model and the screen fails (plan 8)")
    return filt


def ledger(state_dir: Path) -> Any:
    from ml_route_v2.configs import ConfigLedger

    return ConfigLedger(Path(state_dir) / LEDGER_FILE)


def _cpcv_kwargs(panel: Any, filt: dict[str, Any], calendar: Sequence[date],
                 state_dir: Path) -> dict[str, Any]:
    from ml_route_v2.pipeline import split_risk_fn

    if not filt["admissible"]:
        raise EmptyAdmissible("refusing a CPCV with an empty admissible set (plan 8)")
    return {"ledger": ledger(state_dir), "state_dir": Path(state_dir) / CPCV_DIR,
            "admissible": tuple(filt["admissible"]), "calendar": tuple(calendar),
            "risk_fn": split_risk_fn(panel)}


def run_nested(panel: Any, filt: dict[str, Any], calendar: Sequence[date], state_dir: Path,
               configs: Sequence[Any] | None = None) -> Any:
    from ml_route_v2.cpcv import nested_cpcv
    from ml_route_v2.pipeline import score_fn_for

    cfgs = tuple(configs) if configs is not None else frozen_configs()
    return nested_cpcv(panel, cfgs, score_fn_for(filt["risk"]),
                       **_cpcv_kwargs(panel, filt, calendar, state_dir))


def run_final(panel: Any, filt: dict[str, Any], calendar: Sequence[date], state_dir: Path,
              configs: Sequence[Any] | None = None) -> Any:
    from ml_route_v2.cpcv import final_selection
    from ml_route_v2.pipeline import score_fn_for

    cfgs = tuple(configs) if configs is not None else frozen_configs()
    return final_selection(panel, cfgs, score_fn_for(filt["risk"]),
                           **_cpcv_kwargs(panel, filt, calendar, state_dir))


# ------------------------------------------------------------------ the screen ----
def _finite(x: Any) -> bool:
    try:
        return x is not None and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def pbo_record(config_daily: pd.DataFrame) -> dict[str, Any]:
    """cpcv.pbo_cscv on the configurations' CPCV OOS daily, with "passes" = (pbo < 0.5, not
    degenerate, finite, no error) (plan 9 item 2, review PR-11)."""
    from ml_route_v2.cpcv import pbo_cscv

    try:
        rec = dict(pbo_cscv(config_daily.to_numpy()))
    except Exception as exc:  # noqa: BLE001 - an error counts as not < 0.5 (plan 9 item 2)
        return {"pbo": float("nan"), "error": f"{type(exc).__name__}: {exc}", "passes": False}
    ok = _finite(rec.get("pbo")) and not bool(rec.get("degenerate")) and \
        float(rec["pbo"]) < K.SCREEN_PBO_MAX
    rec["passes"] = bool(ok)
    return rec


def screen(nested: Any, final: Any) -> dict[str, Any]:
    """Plan 9 items 1-3 and the final-selection condition on the nested OOS record."""
    from ml_route_v2.pipeline import record_figures

    fig = record_figures(nested.path_daily)
    median_t, sharpe = float(fig["median_path_t"]), float(fig["sharpe_annual"])
    pbo = pbo_record(nested.config_daily)
    item1 = _finite(median_t) and median_t >= K.SCREEN_MEDIAN_T_MIN
    item3 = _finite(sharpe) and K.SCREEN_SHARPE_MIN <= sharpe <= K.SCREEN_SHARPE_MAX
    alarm = _finite(sharpe) and sharpe > K.SCREEN_SHARPE_MAX
    has_final = final is not None and final.config is not None
    passed = bool(item1 and pbo["passes"] and item3 and has_final)
    return {
        "verdict": K.PASS if passed else K.FAIL,
        "items": {
            "1_median_path_t": {"value": median_t, "bar": f">= {K.SCREEN_MEDIAN_T_MIN}",
                                "passes": bool(item1), "path_t": list(fig["path_t"])},
            "2_pbo": {"value": pbo.get("pbo"), "bar": f"< {K.SCREEN_PBO_MAX}",
                      "passes": bool(pbo["passes"]), "record": pbo},
            "3_sharpe_annual": {"value": sharpe,
                                "bar": f">= {K.SCREEN_SHARPE_MIN} and <= {K.SCREEN_SHARPE_MAX}",
                                "passes": bool(item3), "leakage_alarm": bool(alarm)},
            "final_selection": {"config_id": final.config.config_id if has_final else None,
                                "passes": bool(has_final)},
        },
        "leakage_alarm": bool(alarm),
        "n_dates": int(len(nested.path_daily)),
        "daily_mean_usd": float(fig["daily_mean"]),
        "selected_per_split": list(nested.selected),
    }


def empty_screen(reason: str) -> dict[str, Any]:
    """The screen when the search has no model (empty admissible set)."""
    return {"verdict": K.FAIL, "reason": reason, "items": {}, "leakage_alarm": False}


# ------------------------------------------------------------------ reported items ----
def dsr_record(nested: Any, n_total: int = K.N_TOTAL_AT_SCREEN) -> dict[str, Any]:
    """cpcv.dsr_at_n(path_daily.mean(axis=1), N_total, sharpe_variance(finite config_sharpes))."""
    from ml_route_v2.cpcv import CPCVError, dsr_at_n, sharpe_variance

    avg = nested.path_daily.mean(axis=1).to_numpy(np.float64)
    sharpes = nested.config_sharpes.to_numpy(np.float64)
    finite = sharpes[np.isfinite(sharpes)]
    if finite.size == 0:
        return {"status": "undefined", "reason": "no finite configuration Sharpe",
                "n_trials": n_total}
    try:
        rec = dict(dsr_at_n(avg, int(n_total), sharpe_variance(finite)))
    except CPCVError as exc:
        rec = {"status": "undefined", "reason": str(exc)}
    rec["n_trials"] = int(n_total)
    rec["n_finite_config_sharpes"] = int(finite.size)
    return rec


def _series_t_sharpe(xs: np.ndarray) -> dict[str, float]:
    from ml_route_v2.pipeline import TRADE_DATES_PER_YEAR, _daily_t, _sharpe_daily

    xs = np.asarray(xs, dtype=np.float64)
    s = _sharpe_daily(xs) if xs.size else float("nan")
    return {"daily_t": _daily_t(xs), "sharpe_daily": s,
            "sharpe_annual": s * float(np.sqrt(TRADE_DATES_PER_YEAR)),
            "total_usd": float(xs.sum()) if xs.size else 0.0}


def config_table(nested: Any, final: Any | None) -> pd.DataFrame:
    """One row per configuration: registry id, inner and outer scores, CPCV OOS daily t and
    Sharpe (its config_daily column), trades, splits selecting it, final-selection score."""
    inner = nested.inner_table
    outer = nested.outer_table
    rid = {cid: r for r, cid in K.config_ids().items()}
    fin = final.table.set_index("config_id") if final is not None and len(final.table) else None
    rows = []
    for cid in nested.config_daily.columns:
        i = inner.loc[inner["config_id"] == cid]
        o = outer.loc[outer["config_id"] == cid]
        stats = _series_t_sharpe(nested.config_daily[cid].to_numpy())
        rows.append({
            "registry_id": rid.get(cid), "config_id": cid,
            "inner_mean_score_mean": float(pd.to_numeric(i["mean_score"]).mean())
            if i["mean_score"].notna().any() else None,
            "inner_eligible_splits": int(i["eligible"].sum()),
            "outer_score_mean": float(pd.to_numeric(o["sharpe"]).mean())
            if o["sharpe"].notna().any() else None,
            "outer_eligible_splits": int(o["eligible"].sum()),
            "outer_trades": int(o["n_trades"].sum()),
            "cpcv_oos_daily_t": stats["daily_t"], "cpcv_oos_sharpe_annual": stats["sharpe_annual"],
            "config_sharpe_population": float(nested.config_sharpes.get(cid, float("nan"))),
            "selected_splits": int(sum(1 for s in nested.selected if s == cid)),
            "final_mean_score": (None if fin is None or cid not in fin.index
                                 or fin.loc[cid, "mean_score"] is None
                                 or not _finite(fin.loc[cid, "mean_score"])
                                 else float(fin.loc[cid, "mean_score"])),
            "final_eligible": (bool(fin.loc[cid, "eligible"]) if fin is not None
                               and cid in fin.index else None),
        })
    return pd.DataFrame(rows)


def final_own_record(nested: Any, final: Any) -> dict[str, Any]:
    """The final configuration's own CPCV OOS t and Sharpe: its config_daily column (each date
    the mean over the 5 splits testing its block) and its 5 path series' median t."""
    from ml_route_v2.pipeline import _daily_t

    if final is None or final.config is None:
        return {"status": "no final configuration"}
    cid = final.config.config_id
    paths = nested.config_path_sharpes.loc[cid].to_list() if cid in \
        nested.config_path_sharpes.index else []
    rec = {"config_id": cid, "config_daily": _series_t_sharpe(nested.config_daily[cid].to_numpy()),
           "path_sharpes_population": paths}
    rec["note"] = ("config_daily averages the 5 splits that test each block; the per-path t of "
                   "the final configuration is in oos.final_paths")
    rec["daily_t_of_config_daily"] = _daily_t(nested.config_daily[cid].to_numpy())
    return rec


__all__ = ["CPCV_DIR", "LEDGER_FILE", "EmptyAdmissible", "SearchRefusal", "admissibility",
           "config_table", "dsr_record", "empty_screen", "final_own_record", "frozen_configs",
           "ledger", "pbo_record", "run_final", "run_nested", "screen"]
