"""Stage E.33c Part D: input loading and integrity checks (read only).

Reads the search root (INTERFACE.md 4.3), the feature store's _day files (4.1, sigma_zm), the null proof seeds and
the selection JSON written by the frozen select33.py. Refuses on a protocol or selection hash mismatch and on any
date outside the discovery window (no test-window date, nothing dated 2024-03-01 or later).
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
DERIVED = Path("/mnt/large-storage/market_data/PropExperiment/derived/e33")
SEARCH = DERIVED / "search"
FEAT_SHA, LABEL_SHA = "2b30cb0e953b", "b15c4ca10d68"
FEAT_DAY = DERIVED / "features" / FEAT_SHA / "_day"
PROOFS = DERIVED / "proofs"
STATS_C = DERIVED / "stats_c"
WORK = REPO / "reports" / "stage_e33c_briefs" / "work"
PROTOCOL = REPO / "reports" / "stage_e32_discovery_protocol_v0.3.md"
PROTOCOL_SHA = "a2a2856f49723f97319a4db2819ba4d1b5c4b8a1dc86a596e7c48110dbb48246"
SELECT_JSON = REPO / "reports" / "stage_e33c_briefs" / "select" / "P8_select33.json"
SELECT_SHA_PREFIX = "ee506884263d712e"
B5_MD = REPO / "reports" / "stage_e33_briefs" / "work" / "B5_proofs.md"
NULL_CRITERIA = REPO / "docs" / "NULL_CRITERIA_E.md"
K6_LIST = REPO / "reports" / "stage_e22_k6_confirmation_list.json"
DISC_FIRST, DISC_LAST = "2020-12-01", "2024-02-29"
TEST_FIRST, TEST_LAST = "2017-05-01", "2020-11-30"
NULL_SEEDS = tuple(range(1, 21))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_hashes() -> dict:
    p = sha256(PROTOCOL)
    if p != PROTOCOL_SHA:
        raise SystemExit(f"REFUSE: protocol sha256 {p} != {PROTOCOL_SHA}")
    s = sha256(SELECT_JSON)
    if not s.startswith(SELECT_SHA_PREFIX):
        raise SystemExit(f"REFUSE: selection JSON sha256 {s} does not start {SELECT_SHA_PREFIX}")
    return {"protocol_sha256": p, "select_json_sha256": s}


def check_dates(dates: list) -> None:
    """Every date inside the discovery window; none in the test window; none on or after 2024-03-01."""
    bad = [d for d in dates if not (DISC_FIRST <= d <= DISC_LAST) or (TEST_FIRST <= d <= TEST_LAST)]
    if bad:
        raise SystemExit(f"REFUSE: {len(bad)} dates outside the discovery window, first {bad[0]}")


def load_selection_fields() -> dict:
    """Only the fields D1 needs from the 505 KB selection JSON (never printed whole)."""
    d = json.loads(SELECT_JSON.read_text())
    keep = ("config", "constant", "dates_with_trade", "defined", "dsr", "failed", "gates", "mean_net_per_trade",
            "passes_all", "se", "share_dates_with_trade", "sharpe", "sr_lower", "t", "total_net", "trade_count",
            "trades_per_date")
    configs = {}
    for c in d["configs"]:
        row = {k: c.get(k) for k in keep}
        g5 = c.get("g5") or {}
        row["g5"] = {k: g5.get(k) for k in ("a", "quarters_positive", "n_quarters", "b", "total", "max_month_sum",
                                             "max_month_share", "c", "min_lomo_t", "lomo_undefined", "d",
                                             "tercile_means")}
        configs[c["config"]] = row
    bh = d["reports"]["bh_holm"]
    return {"n_trials": d["n_trials"], "b_test": d["b_test"], "t_disc": d["t_disc"], "funnel": d["funnel"],
            "ranking_all": d["ranking_all"], "ranking_pass": d["ranking_pass"], "tier_a": d["tier_a"],
            "tier_b": d["tier_b"], "tier_b_reading": d["tier_b_reading"], "best_config": d["best_config"],
            "best_sharpe": d["best_sharpe"], "pbo": d["reports"]["pbo"],
            "bh": {"m": bh["m"], "n_bh": len(bh["bh_rejected"]), "n_holm": len(bh["holm_rejected"]),
                   "min_p": bh["min_p"], "p_values": bh["p_values"]},
            "reference_thresholds": d["reports"]["reference_thresholds"], "configs": configs}


def load_config(base: Path) -> dict:
    """One configuration's stats.json, daily series and trade nets (INTERFACE 4.3)."""
    if not (base / "DONE").exists():
        raise SystemExit(f"REFUSE: no DONE marker in {base}")
    stats = json.loads((base / "stats.json").read_text())
    daily = pd.read_parquet(base / "daily.parquet")
    trades = pd.read_parquet(base / "trades.parquet", columns=["date", "net"])
    dates = [str(v) for v in daily["date"]]
    tdates = sorted({str(v) for v in trades["date"]})
    return {"stats": stats, "dates": dates, "x": daily["X_D"].to_numpy(dtype=np.float64).tolist(),
            "nt": daily["n_trades"].to_numpy(dtype=np.int64).tolist(),
            "trade_net": trades["net"].to_numpy(dtype=np.float64), "trade_dates": tdates}


def load_real(cids: list) -> tuple:
    configs, dates = {}, None
    for cid in cids:
        c = load_config(SEARCH / cid)
        if dates is None:
            dates = c["dates"]
        elif c["dates"] != dates:
            raise SystemExit(f"REFUSE: {cid} daily dates differ")
        configs[cid] = c
    check_dates(dates)
    for c in configs.values():
        check_dates(c["trade_dates"])
    return dates, configs


def load_sigma(dates: list) -> list:
    out = []
    for d in dates:
        v = json.loads((FEAT_DAY / f"{d}.json").read_text()).get("sigma_zm")
        if v is None or not math.isfinite(float(v)) or float(v) <= 0:
            raise SystemExit(f"REFUSE: sigma_zm {v!r} on {d}")
        out.append(float(v))
    return out


def load_null(dates: list) -> dict:
    """The 20 null seeds x 20 configurations of B5 (derived/e33/proofs/seed<s>/search/<cid>/)."""
    out = {}
    for s in NULL_SEEDS:
        root = PROOFS / f"seed{s}"
        ids = [ln.strip() for ln in (root / "ids.txt").read_text().splitlines() if ln.strip()]
        if len(ids) != 20:
            raise SystemExit(f"REFUSE: seed {s} has {len(ids)} ids")
        seed = {}
        for cid in ids:
            c = load_config(root / "search" / cid)
            if c["dates"] != dates:
                raise SystemExit(f"REFUSE: null seed {s} {cid} dates differ from the real OOF dates")
            seed[cid] = c
        out[s] = seed
    return out


B5_ROW = re.compile(r"^\| (\d+) \| [^|]* \| failed fits: (\d+) \| (\S+) \| (-?\d+\.\d+) \|")


def b5_null_best() -> dict:
    """Seed -> (best configuration, best SR_d to 4 decimals) from the null table of B5_proofs.md."""
    out, in_null = {}, False
    for ln in B5_MD.read_text().splitlines():
        if ln.startswith("## Null seeds"):
            in_null = True
        elif ln.startswith("## Planted seeds"):
            break
        elif in_null:
            m = B5_ROW.match(ln)
            if m:
                out[int(m.group(1))] = (m.group(3), float(m.group(4)), int(m.group(2)))
    return out


def k6_zm_members() -> dict:
    d = json.loads(K6_LIST.read_text())
    zm = [{"member": t["member"], "eps_ticks": t["eps_ticks"], "eps_usd_per_day_at_q": t["eps_usd_per_day_at_q"],
           "q": t["q_c"], "tier": t["tier"], "labels": t["labels"]} for t in d["trials"] if t["vehicle"] == "ZM"]
    return {"path": str(K6_LIST.relative_to(REPO)), "sha256": sha256(K6_LIST), "cluster": d["cluster"],
            "zm_window": d["confirmation_window"]["ZM"], "n_members": len(d["trials"]), "zm_members": zm}
