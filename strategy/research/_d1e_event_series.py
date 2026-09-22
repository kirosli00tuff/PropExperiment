"""Stage D.1e Task 1c: event-level and per-day series behind the recorded F/G statistics.

Reproduction only. This module defines NO new statistic and changes NO declared
definition. Every series is read straight out of the same ``TestedStat``/``DayObs``
objects Stage D.1b (Family F, ``strategy.research.f_data_native._stylized_facts``) and
Stage D.1d (Family G, ``strategy.research.g_timeframe._stylized_facts``) built, by
calling those modules' own builders on the same 139 EDA dates. Neither module is edited
or monkey-patched.

What an "event value" is, per statistic type -- exactly what the recorded edge averages:

- correlation-type F statistics (keys ``PAIR_KEYS``: F1.1, F2.4, F3.2, F3.3, F5.x, F6.1):
  ``sign(sign_pred) * ticks`` per pooled observation. This is the summand of
  ``_corr_edge_fn``, so its mean is ``implied_edge_ticks``. The recorded ``estimate`` is a
  Pearson correlation and is checked separately through the statistic's own
  ``estimate_fn``.
- F4.1 / F4.2 (keys ``("ticks",)``, ``edge_equals_estimate``): the signed forward 15-min
  move in ticks; mean = estimate = implied_edge_ticks.
- F4.4 (keys ``("round_ticks", "control_ticks")``): the event series is ``round_ticks``,
  the forward 15-min move from the round level L. Its mean is the recorded
  ``implied_edge_ticks``. The recorded ``estimate`` is the DIFFERENCE
  ``mean(round_ticks) - mean(control_ticks)``; the control leg is not an event series of
  the tested edge, so it is reported as scalars (``control_mean_ticks``, ``n_control``)
  and the difference is checked through the statistic's own ``estimate_fn``.
- G statistics (keys ``("x",)``, ``edge_equals_estimate``): the signed next-bar move in
  ticks (G3: the signed move to the RTH segment end); mean = estimate = implied edge.

The bootstrap is deliberately not re-run: the CI and p-value are not reproduced here and
nothing in this file depends on them. Estimates, n, edges and sub-block estimates come
from the same ``estimate_fn``/``edge_fn``/``n_fn``/``pool_days`` calls ``compute_result``
makes, with the same sub-block map, so they reproduce the recorded figures exactly.

    uv run python -m strategy.research._d1e_event_series

Writes ``reports/stage_d1e_members_events.json``.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from data.config import REPO_ROOT
from strategy.research.f_data_native._stylized_facts import (
    DECL_SHA256 as F_DECL_SHA256,
)
from strategy.research.f_data_native._stylized_facts import (
    EMPTY,
    PAIR_KEYS,
    DayObs,
    TestedStat,
    _safe_float,
    _sanitize,
    build_all_day_arrays,
    build_f1,
    build_f2,
    build_f3,
    build_f4,
    build_f5,
    build_f6,
    engineer_bars,
    pearson_r,
    pool_days,
    resolve_eda_dates,
    split_equal,
)
from strategy.research.g_timeframe._stylized_facts import (
    DECL_SHA256 as G_DECL_SHA256,
)
from strategy.research.g_timeframe._stylized_facts import (
    build_days,
    build_statistics,
)
from strategy.research.g_timeframe.resample import TIMEFRAMES, annotate_session, coarse_bars

TOL = 1e-9

F_MODULE_PATH = REPO_ROOT / "strategy" / "research" / "f_data_native" / "_stylized_facts.py"
G_MODULE_PATH = REPO_ROOT / "strategy" / "research" / "g_timeframe" / "_stylized_facts.py"
F_DECLARATION_PATH = REPO_ROOT / "reports" / "stage_d1b_family_f_declaration.md"
G_DECLARATION_PATH = REPO_ROOT / "reports" / "stage_d1d_timeframe_declaration.md"
F_FACTS_PATH = REPO_ROOT / "reports" / "stage_d1b_family_f_facts.json"
G_FACTS_PATH = REPO_ROOT / "reports" / "stage_d1d_family_g_facts.json"
MEMBERS_PATH = REPO_ROOT / "reports" / "stage_d1e_members_recorded.json"
OUTPUT_PATH = REPO_ROOT / "reports" / "stage_d1e_members_events.json"

# The event-series definition per key signature, and the human-readable label recorded
# alongside each statistic so the consumer knows which series it is holding.
SERIES_LABEL = {
    PAIR_KEYS: (
        "sign(sign_pred) * ticks per pooled observation; mean = implied_edge_ticks "
        "(the recorded estimate is the Pearson correlation, checked separately)"
    ),
    ("ticks",): (
        "signed forward 15-min move in ticks per crossing event; "
        "mean = estimate = implied_edge_ticks"
    ),
    ("round_ticks", "control_ticks"): (
        "round_ticks: forward 15-min move from the round level L in ticks; "
        "mean = implied_edge_ticks. The recorded estimate additionally subtracts "
        "mean(control_ticks), reported as control_mean_ticks/n_control."
    ),
    ("x",): (
        "signed next-bar move in ticks per event (G3: signed move to the RTH segment "
        "end); mean = estimate = implied_edge_ticks"
    ),
}


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _event_values(day: DayObs, keys: tuple[str, ...]) -> np.ndarray:
    """The event value array for one day, defined exactly as the recorded edge averages."""
    if keys == PAIR_KEYS:
        sign_pred = day.data.get("sign_pred", EMPTY)
        ticks = day.data.get("ticks", EMPTY)
        return np.sign(sign_pred) * ticks
    if keys == ("ticks",):
        return day.data.get("ticks", EMPTY)
    if keys == ("round_ticks", "control_ticks"):
        return day.data.get("round_ticks", EMPTY)
    if keys == ("x",):
        return day.data.get("x", EMPTY)
    raise ValueError(f"no event-series definition for keys {keys!r}")


def _check(name: str, computed: float | None, recorded: float | None) -> dict:
    if computed is None or recorded is None:
        ok = computed is None and recorded is None
        return {"name": name, "pass": ok, "computed": computed, "recorded": recorded,
                "abs_diff": None}
    diff = abs(float(computed) - float(recorded))
    return {"name": name, "pass": bool(diff <= TOL), "computed": float(computed),
            "recorded": float(recorded), "abs_diff": diff}


def _check_list(name: str, computed: list, recorded: list | None) -> dict:
    if recorded is None:
        return {"name": name, "pass": False, "computed": computed, "recorded": None,
                "max_abs_diff": None, "note": "no recorded sub_block_estimates"}
    if len(computed) != len(recorded):
        return {"name": name, "pass": False, "computed": computed, "recorded": recorded,
                "max_abs_diff": None, "note": "length mismatch"}
    worst = 0.0
    ok = True
    for c, r in zip(computed, recorded, strict=True):
        if c is None or r is None:
            ok = ok and (c is None and r is None)
            continue
        d = abs(float(c) - float(r))
        worst = max(worst, d)
        ok = ok and d <= TOL
    return {"name": name, "pass": bool(ok), "computed": computed, "recorded": recorded,
            "max_abs_diff": worst}


def _lag1_autocorr(sums: np.ndarray) -> float | None:
    if len(sums) < 3:
        return None
    return _safe_float(pearson_r(sums[:-1], sums[1:]))


def build_statistic_record(
    stat: TestedStat,
    source: str,
    recorded: dict,
    eda_dates: list[date],
    index_of: dict[date, int],
    subblock_map: dict[date, int],
    with_events: bool,
) -> dict:
    """Per-event and per-day series for one statistic, plus the reproduction checks."""
    n_days = len(eda_dates)
    daily_sum = np.zeros(n_days, dtype=float)
    daily_count = np.zeros(n_days, dtype=int)
    chunks: list[np.ndarray] = []
    event_dates: list[str] = []
    for day in stat.days:
        vals = np.asarray(_event_values(day, stat.keys), dtype=float)
        i = index_of[day.obs_date]
        daily_sum[i] = float(vals.sum()) if len(vals) else 0.0
        daily_count[i] = int(len(vals))
        if len(vals):
            chunks.append(vals)
            event_dates.extend([day.obs_date.isoformat()] * len(vals))
    events = np.concatenate(chunks) if chunks else EMPTY

    full_pool = pool_days(stat.days, stat.keys)
    estimate = _safe_float(stat.estimate_fn(full_pool))
    n_from_stat = int(stat.n_fn(full_pool))
    if stat.edge_equals_estimate:
        edge = estimate
    elif stat.edge_fn is not None:
        edge = _safe_float(stat.edge_fn(full_pool))
    else:
        edge = None

    sub_computed: list[float | None] = []
    for b in range(4):
        bd = [d for d in stat.days if subblock_map[d.obs_date] == b]
        sub_computed.append(
            _safe_float(stat.estimate_fn(pool_days(bd, stat.keys))) if bd else None
        )

    rec_edge = recorded.get("implied_edge_ticks")
    rec_est = recorded.get("estimate")
    rec_n = recorded.get("n_events", recorded.get("n"))
    event_mean = float(np.mean(events)) if len(events) else None
    event_sd = float(np.std(events, ddof=1)) if len(events) > 1 else None

    checks = {
        "event_mean_equals_recorded_implied_edge": _check(
            "event_mean_equals_recorded_implied_edge", event_mean, rec_edge
        ),
        "estimate_equals_recorded_estimate": _check(
            "estimate_equals_recorded_estimate", estimate, rec_est
        ),
        "n_events_equals_recorded_n": _check(
            "n_events_equals_recorded_n", float(len(events)), None if rec_n is None else float(rec_n)
        ),
        "n_events_equals_stat_n_fn": _check(
            "n_events_equals_stat_n_fn", float(len(events)), float(n_from_stat)
        ),
        "daily_count_sum_equals_n_events": _check(
            "daily_count_sum_equals_n_events", float(daily_count.sum()), float(len(events))
        ),
        "sub_block_estimates_reproduce": _check_list(
            "sub_block_estimates_reproduce", sub_computed, recorded.get("sub_block_estimates")
        ),
    }
    all_pass = all(c["pass"] for c in checks.values())

    out: dict = {
        "source": source,
        "family": stat.family,
        "description": stat.description,
        "event_series_definition": SERIES_LABEL[stat.keys],
        "n_events": int(len(events)),
        "event_mean_ticks": event_mean,
        "event_sd_ticks": event_sd,
        "events_per_eda_day": float(len(events)) / n_days,
        "computed_estimate": estimate,
        "computed_implied_edge_ticks": edge,
        "computed_sub_block_estimates": sub_computed,
        "recorded_implied_edge_ticks": rec_edge,
        "recorded_estimate": rec_est,
        "recorded_n": rec_n,
        "checks": checks,
        "checks_all_pass": all_pass,
        "daily_sum_ticks": [float(v) for v in daily_sum],
        "daily_count": [int(v) for v in daily_count],
        "daily_lag1_autocorr_of_sums": _lag1_autocorr(daily_sum),
        "recorded_direction": (
            None if rec_edge in (None, 0) else (1 if rec_edge > 0 else -1)
        ),
    }
    if stat.keys == ("round_ticks", "control_ticks"):
        ctrl = full_pool["control_ticks"]
        out["control_mean_ticks"] = float(np.mean(ctrl)) if len(ctrl) else None
        out["n_control"] = int(len(ctrl))
    if with_events:
        out["event_values_ticks"] = [float(v) for v in events]
        out["event_dates"] = event_dates
    return out


def collect_f_stats(bars: pd.DataFrame, eda_dates: list[date]) -> list[TestedStat]:
    """Every Family F TestedStat, built by the F module's own builders."""
    f_bars = engineer_bars(bars)
    day_arrays = build_all_day_arrays(f_bars)
    wcache: dict = {}
    stats: list[TestedStat] = []
    stats += build_f1(day_arrays, eda_dates, wcache)
    stats += build_f2(day_arrays, eda_dates, wcache)
    f3_stats, _ = build_f3(day_arrays, eda_dates, wcache)
    stats += f3_stats
    stats += build_f4(f_bars, day_arrays, eda_dates)
    stats += build_f5(day_arrays, eda_dates, wcache)
    stats += build_f6(day_arrays, eda_dates, wcache)
    return stats


def collect_g_stats(bars: pd.DataFrame, eda_dates: list[date]) -> list[TestedStat]:
    """Every Family G TestedStat at every declared timeframe, via the G module's pipeline."""
    g_bars = annotate_session(bars)
    g_bars["trade_date_obj"] = pd.to_datetime(g_bars["trade_date"].astype(str)).dt.date
    stats: list[TestedStat] = []
    for tf in TIMEFRAMES:
        coarse = coarse_bars(g_bars, tf)
        days = build_days(g_bars, coarse, tf, eda_dates)
        tf_stats, _q80s = build_statistics(days, tf)
        stats += tf_stats
    return stats


def main() -> None:
    started = time.time()

    members = json.loads(MEMBERS_PATH.read_text())
    recorded_members = {v["id_in_facts"]: v for v in members["statistics"].values()}
    f_facts = {r["id"]: r for r in json.loads(F_FACTS_PATH.read_text())["tested_statistics"]}
    g_facts = {r["id"]: r for r in json.loads(G_FACTS_PATH.read_text())["tested_statistics"]}

    eda_dates, _excluded, bars = resolve_eda_dates()
    index_of = {d: i for i, d in enumerate(eda_dates)}
    sizes = split_equal(len(eda_dates), 4)
    subblock_map: dict[date, int] = {}
    pos = 0
    for b, size in enumerate(sizes):
        for d in eda_dates[pos : pos + size]:
            subblock_map[d] = b
        pos += size

    f_stats = collect_f_stats(bars, eda_dates)
    g_stats = collect_g_stats(bars, eda_dates)
    by_id: dict[str, tuple[TestedStat, str]] = {}
    for s in f_stats:
        by_id[s.id] = (s, "C")
    for s in g_stats:
        by_id[s.id] = (s, "D")

    member_ids = [v["id_in_facts"] for v in members["statistics"].values()]
    missing = [i for i in member_ids if i not in by_id]
    if missing:
        raise AssertionError(f"recorded member ids not rebuilt: {missing}")

    statistics: dict[str, dict] = {}
    for sid in member_ids:
        stat, source = by_id[sid]
        statistics[sid] = build_statistic_record(
            stat, source, recorded_members[sid], eda_dates, index_of, subblock_map,
            with_events=True,
        )

    # Coverage map: every OTHER directional F statistic and every other G statistic,
    # same fields and same checks, without the per-event arrays.
    coverage: dict[str, dict] = {}
    for s in f_stats:
        if s.id in statistics or not s.directional:
            continue
        rec = f_facts.get(s.id)
        if rec is None:
            raise AssertionError(f"no recorded Family F record for {s.id}")
        coverage[s.id] = build_statistic_record(
            s, "C", rec, eda_dates, index_of, subblock_map, with_events=False
        )
    for s in g_stats:
        if s.id in statistics:
            continue
        rec = g_facts.get(s.id)
        if rec is None:
            raise AssertionError(f"no recorded Family G record for {s.id}")
        coverage[s.id] = build_statistic_record(
            s, "D", rec, eda_dates, index_of, subblock_map, with_events=False
        )

    f_decl_sha = _sha256(F_DECLARATION_PATH)
    g_decl_sha = _sha256(G_DECLARATION_PATH)
    all_pass = all(r["checks_all_pass"] for r in statistics.values()) and all(
        r["checks_all_pass"] for r in coverage.values()
    )
    elapsed = time.time() - started

    out = {
        "meta": {
            "generated_utc": datetime.now(UTC).isoformat(),
            "purpose": (
                "Stage D.1e Task 1c: event-level and per-day series for the recorded "
                "Family F and Family G statistics, for day-block bootstrap power work. "
                "Reproduction only -- no new statistic, no changed definition."
            ),
            "eda_dates": [d.isoformat() for d in eda_dates],
            "n_eda_dates": len(eda_dates),
            "sub_block_sizes": sizes,
            "declaration_sha256_f": f_decl_sha,
            "declaration_sha256_g": g_decl_sha,
            "declaration_sha256_f_matches_module_constant": f_decl_sha == F_DECL_SHA256,
            "declaration_sha256_g_matches_module_constant": g_decl_sha == G_DECL_SHA256,
            "f_module_sha256": _sha256(F_MODULE_PATH),
            "g_module_sha256": _sha256(G_MODULE_PATH),
            "n_statistics": len(statistics),
            "n_coverage_statistics": len(coverage),
            "tolerance": TOL,
            "checks_all_pass": bool(all_pass),
            "runtime_seconds": elapsed,
        },
        "statistics": statistics,
        "coverage_statistics": coverage,
    }
    OUTPUT_PATH.write_text(json.dumps(_sanitize(out), indent=2))

    n_fail = sum(1 for r in statistics.values() if not r["checks_all_pass"])
    n_cov_fail = sum(1 for r in coverage.values() if not r["checks_all_pass"])
    print(
        f"wrote {OUTPUT_PATH} in {elapsed:.1f}s: {len(statistics)} member statistics "
        f"({n_fail} failing), {len(coverage)} coverage statistics ({n_cov_fail} failing)"
    )
    for label, block in (("member", statistics), ("coverage", coverage)):
        for sid, r in block.items():
            if r["checks_all_pass"]:
                continue
            for c in r["checks"].values():
                if not c["pass"]:
                    print(
                        f"  FAIL {label} {sid} {c['name']}: computed={c['computed']!r} "
                        f"recorded={c['recorded']!r}"
                    )
    for sid in ("G2.RTH.30", "F3_2_bucket07_bucket08"):
        r = statistics.get(sid)
        if r:
            print(
                f"  {sid}: n={r['n_events']} sd={r['event_sd_ticks']!r} "
                f"per_day={r['events_per_eda_day']:.4f} "
                f"lag1_autocorr_of_daily_sums={r['daily_lag1_autocorr_of_sums']!r}"
            )


if __name__ == "__main__":
    main()
