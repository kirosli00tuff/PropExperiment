"""Check 1 (VerdictVerifier-FableXHigh, Stage E.18): recompute C1b's verdict numbers independently.

Never calls c1_replication.c1b, c1_replication.evaluate.run/.evaluate or q_m1 (the evaluation runs
once). Rebuilds the world and the panel with the frozen building blocks the run used
(load_calendars, c12_exclusions, hist_tables, build_world through data.hist_bars.load_hist_leg on
the pinned stores, replication_panel), then computes with its own code: the C10 counts and C1b's
amended check, r_hat (own ridge unpack, cross-checked against ml_route_v2.models.predict), the
trades, the statistic (gate0._b_test's conventions: trade-level mean, per-date means, sd ddof=1,
one-sided Student p with n_dates - 1 df), the pass bar, the verdict, the descriptive outputs
(C14, C15) and trades_sha256 in evaluate.trades_sha256's encoding.

Does NOT read the result, the marker or the evaluation log. Prints counts and statistics only;
never a price, a bar row or a feature value. Writes reports/stage_e18_verify/recompute.json.
"""

from __future__ import annotations

import gc
import hashlib
import json
import math
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

os.nice(10)

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import t as student_t  # noqa: E402

OUT = REPO / "reports" / "stage_e18_verify" / "recompute.json"
FREEZE_MANIFEST = REPO / "reports" / "stage_e18_freeze.json"
MODEL = REPO / "reports" / "stage_e14_c1_model.json"
MODEL_DIR = Path.home() / ".cache" / "propexp_e14_c1" / "m1"
STORE_HASHES = REPO / "reports" / "stage_e17_c1_store_hashes.json"
CALENDAR_HASHES = REPO / "reports" / "stage_e17_c1_calendar_hashes.json"
TEST_IDS = ("C1b-T1", "C1b-T2")
HORIZON_OF = {"C1b-T1": "h60", "C1b-T2": "hF"}
VEHICLE = "NG"
C10_EXEMPT = ("g17_mbt", "g17_cl")  # freeze section 3 as amended (V31)
COST_MULTIPLE = 1.5
ALPHA = 0.025
MIN_TRADES = 30
MIN_AVAILABLE_KB = 3_500_000  # E.17's rebuild peaked at about 2.1 GB


def now_date() -> str:
    return subprocess.run(["date"], capture_output=True, text=True, check=True).stdout.strip()


def mem_available_kb() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1])
    raise RuntimeError("MemAvailable not found")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fnum(x: float) -> float | None:
    return None if (x is None or not math.isfinite(x)) else float(x)


def own_unpack(payload: bytes) -> tuple[np.ndarray, float]:
    p = int(np.frombuffer(payload[:8], dtype="<i8")[0])
    assert len(payload) == 8 + 8 * (p + 1), "payload length"
    coef = np.frombuffer(payload[8:8 + 8 * p], dtype="<f8").astype(np.float64)
    intercept = float(np.frombuffer(payload[8 + 8 * p:], dtype="<f8")[0])
    return coef, intercept


def own_stats(days: np.ndarray, g: np.ndarray, cost: np.ndarray, n_rows: int) -> dict:
    n_trades = int(g.size)
    mean_trades = float(g.mean()) if n_trades else float("nan")
    per_date = pd.Series(g).groupby(days).mean().to_numpy(np.float64)
    n_dates = int(per_date.size)
    mean_dates = float(per_date.mean()) if n_dates else float("nan")
    sd_dates = float(per_date.std(ddof=1)) if n_dates >= 2 else float("nan")
    t_b = mean_dates / (sd_dates / math.sqrt(n_dates)) if n_dates >= 2 and sd_dates > 0 \
        else float("nan")
    p = float(student_t.sf(t_b, n_dates - 1)) if math.isfinite(t_b) else 1.0
    c = float(cost.mean()) if n_trades else float("nan")
    bar = COST_MULTIPLE * c
    crit1_trade_mean = bool(math.isfinite(mean_trades) and mean_trades >= bar)
    crit1_date_mean = bool(math.isfinite(mean_dates) and mean_dates >= bar)
    crit2 = bool(math.isfinite(p) and p <= ALPHA)
    crit3 = bool(n_trades >= MIN_TRADES)
    return {
        "n_rows": n_rows, "n_trades": n_trades, "n_dates": n_dates,
        "mean_gross_ticks_trade_level": fnum(mean_trades),
        "mean_of_per_date_means": fnum(mean_dates),
        "sd_per_date_means_ddof1": fnum(sd_dates),
        "t_B": fnum(t_b), "p_one_sided": fnum(p),
        "cost_ticks": fnum(c), "bar_ticks": fnum(bar),
        "criteria": {"mean_ge_1_5c_trade_level": crit1_trade_mean,
                     "mean_ge_1_5c_per_date_mean": crit1_date_mean,
                     "p_le_0_025": crit2, "n_ge_30": crit3},
        "decision_trade_level_mean": "PASS" if (crit1_trade_mean and crit2 and crit3) else "FAIL",
        "decision_per_date_mean": "PASS" if (crit1_date_mean and crit2 and crit3) else "FAIL",
    }


def own_descriptive(g: np.ndarray, cost: np.ndarray, side: np.ndarray, days: np.ndarray,
                    n_rows: int, comm: float) -> dict:
    c15 = comm + COST_MULTIPLE * (cost - comm)
    mean_c15 = float(c15.mean()) if c15.size else float("nan")
    years = Counter(pd.to_datetime(days).year.astype(int).tolist())
    return {
        "c14_slippage_1_5x": {"commission_rt_ticks": comm, "mean_cost_ticks": fnum(mean_c15),
                              "bar_ticks": fnum(COST_MULTIPLE * mean_c15),
                              "mean_ge_bar": bool(g.size and float(g.mean())
                                                  >= COST_MULTIPLE * mean_c15)},
        "c15": {"share_of_rows_at_or_above_q": (g.size / n_rows) if n_rows else None,
                "n_rows": n_rows,
                "long": {"n": int((side > 0).sum()),
                         "mean_gross_ticks": fnum(float(g[side > 0].mean()))
                         if (side > 0).any() else None},
                "short": {"n": int((side < 0).sum()),
                          "mean_gross_ticks": fnum(float(g[side < 0].mean()))
                          if (side < 0).any() else None},
                "trades_per_year": {str(y): n for y, n in sorted(years.items())}}}


def main() -> int:
    started = now_date()
    avail = mem_available_kb()
    print(f"start {started}; MemAvailable {avail // 1024} MB")
    if avail < MIN_AVAILABLE_KB:
        print("refusing: too little memory")
        return 2
    from c1_replication.constants import E12_GATE0_LIST, E12_GATE0_LIST_SHA256, WINDOW_FIRST, WINDOW_LAST
    from c1_replication.context import hist_tables
    from c1_replication.evaluate import default_leg_loader, load_calendars, load_store_hashes
    from c1_replication.exclusions import c12_exclusions
    from c1_replication.guards import pinned_file
    from c1_replication.q_m1 import feature_cols_sha256
    from c1_replication.world import build_world, replication_panel
    from data.group_session import group_of
    from ml_route_v2.configs import ridge_spec
    from ml_route_v2.constants import COST_SENSITIVITY_SLIPPAGE_MULTIPLE, GATE0_RIDGE_LAMBDA
    from ml_route_v2.models import FittedModel, predict
    from ml_route_v2.portfolio import vehicle_facts

    assert COST_SENSITIVITY_SLIPPAGE_MULTIPLE == COST_MULTIPLE
    # Pinned inputs: the freeze manifest's pins for the model, the store and calendar hash files.
    manifest = json.loads(FREEZE_MANIFEST.read_bytes())
    pins = manifest["pins"]
    pin_checks = {}
    for key, path in (("model", MODEL), ("store_hashes", STORE_HASHES),
                      ("calendar_hashes", CALENDAR_HASHES)):
        want = pins[key][1]
        got = sha256_file(path)
        pin_checks[key] = {"path": str(path.relative_to(REPO)), "manifest_path": pins[key][0],
                           "manifest_sha256": want, "sha256_now": got, "equal": want == got}
    model_doc = json.loads(pinned_file(MODEL, pins["model"][1], "model JSON"))
    signals = tuple(json.loads(pinned_file(E12_GATE0_LIST, E12_GATE0_LIST_SHA256,
                                           "E.12 Gate 0 list"))["covered_signals"])
    assert tuple(model_doc["signals"]) == signals, "model signals are not the covered signals"
    cols = tuple(model_doc["feature_cols"])
    assert feature_cols_sha256(cols) == model_doc["feature_cols_sha256"]
    spec = ridge_spec(GATE0_RIDGE_LAMBDA)
    models, coefs, q = {}, {}, {}
    payload_rec = {}
    for h in ("h60", "hF"):
        sha = model_doc["m1"][h]["payload_sha256"]
        assert model_doc["m1"][h]["spec"] == spec.as_dict()
        payload = (MODEL_DIR / f"c1_m1_{h}.ridge").read_bytes()
        got = hashlib.sha256(payload).hexdigest()
        payload_rec[h] = {"sha256_model_json": sha, "sha256_now": got, "equal": sha == got,
                          "bytes": len(payload)}
        assert sha == got, f"M1 {h} payload sha256 mismatch"
        models[h] = FittedModel(spec, got, payload)
        coefs[h] = own_unpack(payload)
        qrec = model_doc["q"][h]
        assert qrec["q_repr"] == repr(qrec["q"]) and qrec["q"] > 0
        q[h] = float(qrec["q"])
        assert coefs[h][0].shape[0] == len(cols), "coef count is not the feature count"
    reference = model_doc["c10_reference"]

    stores = load_store_hashes(STORE_HASHES)
    cal = load_calendars(CALENDAR_HASHES, WINDOW_FIRST, WINDOW_LAST)
    c12 = c12_exclusions(cal["calendars"], tuple(cal["releases"].unsourced),
                         first=WINDOW_FIRST, last=WINDOW_LAST)
    assert not c12.stops, "C12 stops"
    loader = default_leg_loader(None)
    t_world = now_date()
    with hist_tables(cal["tables"]):
        world = build_world(
            lambda r: loader(r, expected_sha256=stores[r], calendar=cal["calendars"][group_of(r)]),
            cal["releases"].calendar, c12.excluded_dates(), first=WINDOW_FIRST, last=WINDOW_LAST)
        world_rec = {"roots": {r: dict(v) for r, v in world.roots.items()},
                     "calendar_dates": len(world.calendar), "excluded_dates": len(world.excluded)}
        panel = replication_panel(world, signals)
        del world
        gc.collect()
    t_panel = now_date()
    frame = panel.frame
    panel_counts = {k: int(v) for k, v in dict(panel.counts).items()}
    is_ng = frame["root"].to_numpy(object) == VEHICLE
    feature_cols_equal = tuple(panel.feature_cols) == cols
    print(f"world {t_world} -> panel {t_panel}; rows {len(frame)}, NG rows {int(is_ng.sum())}, "
          f"feature_cols equal model {feature_cols_equal}")

    # C10 counts (own) and C1b's amended check (own).
    c10_counts, c10_dead_c1_rule, c10_dead_amended = {}, [], []
    for h in ("h60", "hF"):
        sel = is_ng & frame[f"ok_{h}"].to_numpy(bool)
        app = {s: int((frame[f"app_{s}"].to_numpy(np.float64)[sel] > 0).sum()) for s in signals}
        c10_counts[h] = {"ng_ok_rows": int(sel.sum()), "applicable": app}
        for s, n_ref in reference[h]["applicable"].items():
            if n_ref > 0 and app.get(s, 0) == 0:
                c10_dead_c1_rule.append(f"{s} ({h})")
                if s not in C10_EXEMPT:
                    c10_dead_amended.append(f"{s} ({h})")
    exempt_counts = {h: {s: c10_counts[h]["applicable"][s] for s in C10_EXEMPT} for h in c10_counts}
    exempt_ref = {h: {s: reference[h]["applicable"][s] for s in C10_EXEMPT} for h in reference}
    live_in_ref_zero_now = {h: sorted(s for s, n in reference[h]["applicable"].items()
                                      if n > 0 and c10_counts[h]["applicable"][s] == 0)
                            for h in reference}
    print(f"C10 dead by C1's rule {c10_dead_c1_rule}; dead by the amended rule {c10_dead_amended}")

    # Trades and statistics per test (own code).
    comm = float(vehicle_facts(VEHICLE).commission_rt_ticks)
    tests, desc, sha_rows = {}, {}, []
    for tid in TEST_IDS:
        h = HORIZON_OF[tid]
        mask = frame[f"ok_{h}"].to_numpy(bool)  # horizon_data's mask: ok rows, no root filter
        n_non_ng = int((~is_ng & mask).sum())
        rows = frame.loc[mask]
        X = rows[list(cols)].to_numpy(np.float64)
        n_rows = int(X.shape[0])
        coef, intercept = coefs[h]
        r_own = X @ coef + intercept
        r_alt = (X * coef).sum(axis=1) + intercept  # a second summation order
        r_frozen = predict(models[h], X)
        side = np.sign(r_own).astype(np.int8)
        take = (np.abs(r_own) >= q[h]) & (side != 0)
        take_alt = (np.abs(r_alt) >= q[h]) & (np.sign(r_alt) != 0)
        take_frozen = (np.abs(r_frozen) >= q[h]) & (np.sign(r_frozen) != 0)
        idx = np.flatnonzero(take)
        s = side[idx]
        g = s * rows[f"y_gross_{h}"].to_numpy(np.float64)[idx]
        cost = np.where(s > 0, rows[f"cost_long_{h}"].to_numpy(np.float64)[idx],
                        rows[f"cost_short_{h}"].to_numpy(np.float64)[idx])
        days = pd.to_datetime(rows["trade_date"]).to_numpy(dtype="datetime64[D]")[idx]
        ts = rows["decision_ts_ns"].to_numpy(np.int64)[idx]
        assert np.isfinite(g).all() and np.isfinite(cost).all()
        stats = own_stats(days, g, cost, n_rows)
        stats["horizon"] = h
        stats["r_hat_checks"] = {
            "max_abs_diff_own_vs_frozen_predict": float(np.abs(r_own - r_frozen).max()) if n_rows else 0.0,
            "max_abs_diff_own_vs_alt_sum": float(np.abs(r_own - r_alt).max()) if n_rows else 0.0,
            "trade_set_equal_frozen_predict": bool((take == take_frozen).all()),
            "trade_set_equal_alt_sum": bool((take == take_alt).all()),
            "rows_within_1e-9_of_q": int((np.abs(np.abs(r_own) - q[h]) <= 1e-9).sum()),
            "rows_with_r_hat_zero": int((side == 0).sum()),
            "non_ng_ok_rows": n_non_ng, "q": q[h], "q_repr": repr(q[h]),
            "n_rows_equals_ng_ok_rows": n_rows == c10_counts[h]["ng_ok_rows"]}
        stats["first_trade_date"] = str(days.min()) if g.size else None
        stats["last_trade_date"] = str(days.max()) if g.size else None
        tests[tid] = stats
        desc[tid] = own_descriptive(g, cost, s, days, n_rows, comm)
        for d, t_, sd, gg, cc in zip(np.datetime_as_string(days, unit="D"), ts, s, g, cost,
                                     strict=True):
            sha_rows.append([tid, str(d), int(t_), int(sd), repr(float(gg)), repr(float(cc))])
        print(f"{tid} {h}: n_rows {n_rows}, n_trades {stats['n_trades']}, n_dates {stats['n_dates']}, "
              f"mean(trades) {stats['mean_gross_ticks_trade_level']!r}, mean(dates) "
              f"{stats['mean_of_per_date_means']!r}, c {stats['cost_ticks']!r}, bar {stats['bar_ticks']!r}, "
              f"t_B {stats['t_B']!r}, p {stats['p_one_sided']!r}, decision(trade mean) "
              f"{stats['decision_trade_level_mean']}, decision(date mean) {stats['decision_per_date_mean']}")
    trades_sha = hashlib.sha256(json.dumps(sha_rows, separators=(",", ":")).encode()).hexdigest()
    passing_trade = [t for t in TEST_IDS if tests[t]["decision_trade_level_mean"] == "PASS"]
    passing_date = [t for t in TEST_IDS if tests[t]["decision_per_date_mean"] == "PASS"]
    verdict_trade = "PASS" if passing_trade else "FAIL"
    verdict_date = "PASS" if passing_date else "FAIL"
    finished = now_date()
    rec = {
        "schema": "stage_e18_verify/recompute/1",
        "verifier": "VerdictVerifier-FableXHigh",
        "started_local": started, "world_built_local": t_world, "panel_built_local": t_panel,
        "finished_local": finished,
        "mem_available_mb_at_start": avail // 1024,
        "inputs_read": {"freeze_manifest": {"path": str(FREEZE_MANIFEST.relative_to(REPO)),
                                            "sha256": sha256_file(FREEZE_MANIFEST)},
                        "pins": pin_checks, "m1_payloads": payload_rec,
                        "gate0_list_sha256": E12_GATE0_LIST_SHA256,
                        "stores_sha256_expected": stores,
                        "window": [WINDOW_FIRST.isoformat(), WINDOW_LAST.isoformat()],
                        "result_marker_log_read": False},
        "c12": c12.record(),
        "world": world_rec,
        "panel_counts": panel_counts,
        "panel": {"rows": int(len(frame)), "ng_rows": int(is_ng.sum()),
                  "feature_cols_equal_model": feature_cols_equal, "n_feature_cols": len(cols),
                  "n_signals": len(signals)},
        "c10": {"counts": c10_counts, "exempt": list(C10_EXEMPT),
                "exempt_counts_now": exempt_counts, "exempt_reference": exempt_ref,
                "live_in_reference_zero_now": live_in_ref_zero_now,
                "dead_by_c1_rule": c10_dead_c1_rule, "dead_by_amended_rule": c10_dead_amended,
                "amended_check_stops": bool(c10_dead_amended)},
        "statistic_convention": "mean reported = trade-level mean of g; t_B = mean(per-date means)"
                                " / (sd(per-date means, ddof=1) / sqrt(n_dates)); p = scipy "
                                "student_t.sf(t_B, n_dates - 1); c = mean cost over trades",
        "tests": tests,
        "verdict_with_trade_level_mean": verdict_trade, "passing_tests_trade_level_mean": passing_trade,
        "verdict_with_per_date_mean": verdict_date, "passing_tests_per_date_mean": passing_date,
        "verdict_depends_on_which_mean": verdict_trade != verdict_date,
        "descriptive": desc,
        "trades_sha256": trades_sha,
        "n_sha_rows": len(sha_rows),
    }
    OUT.write_text(json.dumps(rec, indent=1, allow_nan=False) + "\n")
    print(f"verdict (trade-level mean, as the code reads criterion 1): {verdict_trade} {passing_trade}; "
          f"verdict (per-date mean): {verdict_date} {passing_date}; trades_sha256 {trades_sha}")
    print(f"written {OUT.relative_to(REPO)} at {finished}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
