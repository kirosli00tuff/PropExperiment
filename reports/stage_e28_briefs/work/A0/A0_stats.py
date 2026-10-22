"""Stage E.28 A0: owned-data magnitude statistics per owned ohlcv-1m root.

Definitions follow reports/stage_e28_ranking_spec.md section 1. Run from the repo root:
    nice -n 10 uv run python reports/stage_e28_briefs/work/A0/A0_stats.py
Per-root results go to work/A0/A0_roots/<ROOT>.json (a restart skips finished roots); the
assembled file is reports/stage_e28_briefs/A0_contract_stats.json.

DATA RULE (binding, enforced in open_store): only files whose range ends on or before
2023-11-01 are opened; mbp-1 is never touched; file names alone are used for the pilot window.
"""
from __future__ import annotations

import importlib
import json
import os
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

os.nice(10)
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

import databento  # noqa: E402

from data.calendars import GROUP_OF_PRODUCT  # noqa: E402
from rules.products import PRODUCTS  # noqa: E402

OHLCV = REPO / "data/vendor/databento/GLBX.MDP3/ohlcv-1m"
OUT_DIR = REPO / "reports/stage_e28_briefs/work/A0/A0_roots"
OUT_JSON = REPO / "reports/stage_e28_briefs/A0_contract_stats.json"
LAST_ALLOWED_END = "2023-11-01"  # range=2023-10-01_2023-11-01 is the last file that may be opened
WIN_START, WIN_END = date(2022, 11, 1), date(2023, 10, 31)  # standard window, trade dates
C4_END = date(2023, 10, 31)
PILOT_START, PILOT_END_EXCL = "2023-11-01", "2024-03-01"
MAIN_PT = (6 * 60 + 30, 13 * 60)  # 06:30-13:00 America/Vancouver, minutes after midnight
BIG_MOVE_K = 4.0
NS_MIN = 60_000_000_000
PRICE_SCALE = 1e9
EMPTY_FILES: dict[str, list[str]] = {}
RANGE_RE = re.compile(r"^range=(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.dbn\.zst$")


def products_line(root: str) -> int | None:
    for i, line in enumerate((REPO / "rules/products.py").read_text().splitlines(), 1):
        if re.search(rf'_p\("{re.escape(root)}",', line):
            return i
    return None


def list_files(root: str) -> list[tuple[str, str, str]]:
    d = OHLCV / f"{root}_v_0"
    out = []
    for name in sorted(os.listdir(d)):
        m = RANGE_RE.match(name)
        if m:
            out.append((m.group(1), m.group(2), name))
    return out


def open_store(root: str, name: str) -> np.ndarray:
    m = RANGE_RE.match(name)
    if m is None or m.group(2) > LAST_ALLOWED_END:
        raise RuntimeError(f"DATA RULE: refusing to open {root}/{name}")
    rel = OHLCV / f"{root}_v_0" / name
    for attempt in (0, 1):
        path = os.path.realpath(rel)  # resolve at open (E.26 may move data/vendor)
        if "mbp-1" in path:
            raise RuntimeError(f"DATA RULE: refusing mbp-1 path {path}")
        try:
            arr = databento.DBNStore.from_file(path).to_ndarray()
            return arr[["instrument_id", "ts_event", "high", "low", "close", "volume"]].copy()
        except FileNotFoundError:
            if attempt == 0:
                print(f"  {root}/{name} missing at {path}; retry in 60 s", flush=True)
                time.sleep(60)
                continue
            raise
    raise AssertionError


def trade_dates(ts: np.ndarray) -> np.ndarray:
    """CME trade date: CT time >= 17:00 belongs to the next day; Sat/Sun roll to Monday."""
    ct = pd.to_datetime(ts.astype("int64"), utc=True).tz_convert("America/Chicago")
    days = ct.tz_localize(None).normalize().values.astype("datetime64[D]")
    days = days + (ct.hour.values >= 17).astype("int64")
    wd = (days.astype("int64") + 3) % 7  # Monday = 0
    days = days + np.where(wd == 5, 2, np.where(wd == 6, 1, 0))
    return days


def session_spec(group: str, day: date):
    mod = importlib.import_module(f"data.calendars.{group}")
    for s in mod.SESSIONS:
        if s.valid_from <= day and (s.valid_to is None or day <= s.valid_to):
            return s, mod.__file__
    raise LookupError(f"no session spec for {group} {day}")


def scheduled_minutes(group: str, day: date) -> np.ndarray:
    """UTC ns of every scheduled minute start of trade date ``day`` (CT segments)."""
    spec, _ = session_spec(group, day)
    out = []
    for seg in spec.segments:
        s = pd.Timestamp.combine(day + timedelta(days=seg.start_offset_days), seg.start_ct)
        e = pd.Timestamp.combine(day + timedelta(days=seg.end_offset_days), seg.end_ct)
        s = s.tz_localize("America/Chicago").tz_convert("UTC").value
        e = e.tz_localize("America/Chicago").tz_convert("UTC").value
        out.append(np.arange(s, e, NS_MIN, dtype="int64"))
    return np.concatenate(out)


def pt_minutes(ns: np.ndarray) -> np.ndarray:
    pt = pd.to_datetime(ns, utc=True).tz_convert("America/Vancouver")
    return pt.hour.values * 60 + pt.minute.values


def early_halt_days(group: str) -> tuple[set, str]:
    """EARLY_HALT dates of the group's calendar (holiday sessions and business early closes)."""
    name = "data.cme_calendar" if group == "equity" else f"data.calendars.{group}"
    mod = importlib.import_module(name)
    days = {d for d, h in mod.HOLIDAYS.items() if h.kind.name == "EARLY_HALT"}
    return days, name


def day_record(group, d, idx, ts, close, hi, lo, vol, inst, tick) -> dict:
    last_inst = inst[idx[-1]]
    dom = idx[inst[idx] == last_inst]
    rec = {"mixed": len(np.unique(inst[idx])) > 1, "rng": (hi[dom].max() - lo[dom].min()) / tick,
           "vol": vol[idx].sum(), "md": np.array([]), "ad": np.array([]), "mv": np.array([]),
           "ov": np.array([]), "cov": None}
    grid = scheduled_minutes(group, pd.Timestamp(d).date())
    grid = grid[(grid >= ts[idx[0]]) & (grid <= ts[idx[-1]])]
    if grid.size == 0:
        return rec
    tsd, cl, vo, ins = ts[idx], close[idx], vol[idx], inst[idx]
    pos = np.searchsorted(tsd, grid, side="right") - 1  # last bar at or before the minute
    has = pos >= 0
    p0 = np.maximum(pos, 0)
    gclose = np.where(has, cl[p0], np.nan)
    ginst = np.where(has, ins[p0], -1)
    exact = has & (tsd[p0] == grid)
    gvol = np.where(exact, vo[p0], 0.0)
    ptm = pt_minutes(grid)
    is_main = (ptm >= MAIN_PT[0]) & (ptm < MAIN_PT[1])
    rec["mv"], rec["ov"] = gvol[is_main], gvol[~is_main]
    rec["cov"] = float(exact[is_main].mean()) if is_main.any() else None
    step = np.diff(grid) == NS_MIN
    same = (ginst[1:] == ginst[:-1]) & (ginst[1:] >= 0)
    ok = step & same & is_main[1:] & ~np.isnan(gclose[:-1])
    dif = (gclose[1:] - gclose[:-1]) / tick
    rec["md"] = dif[ok]
    rec["ad"] = dif[ok & exact[1:] & exact[:-1]]
    return rec


def aggregate(recs: list[dict]) -> dict:
    cat = lambda k: np.concatenate([r[k] for r in recs]) if recs else np.array([])  # noqa: E731
    md, ad, mv, ov = cat("md"), cat("ad"), cat("mv"), cat("ov")
    rng = np.array([r["rng"] for r in recs])
    dvol = np.array([r["vol"] for r in recs])
    cov = [r["cov"] for r in recs if r["cov"] is not None]
    mt, ot = mv.sum(), ov.sum()
    return {
        "n_trade_dates": len(recs),
        "sigma_1m_ticks": float(np.std(md, ddof=1)) if md.size > 1 else None,
        "sigma_1m_n_changes": int(md.size),
        "sigma_1m_share_zero_changes": float(np.mean(md == 0)) if md.size else None,
        "sigma_1m_consecutive_bars_only_ticks": float(np.std(ad, ddof=1)) if ad.size > 1 else None,
        "sigma_1m_consecutive_bars_only_n": int(ad.size),
        "main_minutes_with_bar_share_median_day": float(np.median(cov)) if cov else None,
        "R_d_median_ticks": float(np.median(rng)),
        "R_d_p25_p75_ticks": [float(np.percentile(rng, 25)), float(np.percentile(rng, 75))],
        "ADV_median_contracts_v0_front": float(np.median(dvol)),
        "ADV_mean_contracts_v0_front": float(np.mean(dvol)),
        "vol_per_min_main_median": float(np.median(mv)) if mv.size else None,
        "vol_per_min_main_mean": float(np.mean(mv)) if mv.size else None,
        "main_grid_minutes": int(mv.size),
        "vol_per_min_overnight_median": float(np.median(ov)) if ov.size else None,
        "vol_per_min_overnight_mean": float(np.mean(ov)) if ov.size else None,
        "overnight_grid_minutes": int(ov.size),
        "main_session_volume_share": float(mt / (mt + ot)) if mt + ot else None,
    }


def window_stats(root: str, files: list[tuple[str, str, str]]) -> dict:
    p = PRODUCTS[root]
    tick = float(p.vendor_tick)
    group = GROUP_OF_PRODUCT[root]
    use = [f for f in files if f[0] >= "2022-10-01" and f[1] <= LAST_ALLOWED_END]
    if not use:
        return {"window_files": 0}
    arr = np.concatenate([open_store(root, f[2]) for f in use])
    arr = arr[np.argsort(arr["ts_event"], kind="stable")]
    td = trade_dates(arr["ts_event"])
    keep = (td >= np.datetime64(WIN_START)) & (td <= np.datetime64(WIN_END))
    arr, td = arr[keep], td[keep]
    ts = arr["ts_event"].astype("int64")
    close = arr["close"].astype("float64") / PRICE_SCALE
    hi = arr["high"].astype("float64") / PRICE_SCALE
    lo = arr["low"].astype("float64") / PRICE_SCALE
    vol = arr["volume"].astype("float64")
    inst = arr["instrument_id"].astype("int64")
    halts, cal_name = early_halt_days(group)
    days = np.unique(td)
    recs, regular = [], []
    for d in days:
        idx = np.nonzero(td == d)[0]
        rec = day_record(group, d, idx, ts, close, hi, lo, vol, inst, tick)
        recs.append(rec)
        regular.append(pd.Timestamp(d).date() not in halts)
    reg = [r for r, ok in zip(recs, regular) if ok]
    excluded = [str(d) for d, ok in zip(days, regular) if not ok]
    out = {
        "window_files": len(use),
        "window_file_names": [f[2] for f in use],
        "window_trade_dates_all": int(days.size),
        "window_first_trade_date": str(days[0]) if days.size else None,
        "window_last_trade_date": str(days[-1]) if days.size else None,
        "window_bars": int(arr.size),
        "days_with_two_instruments": int(sum(r["mixed"] for r in recs)),
        "early_halt_dates_excluded": excluded,
        "early_halt_calendar": cal_name,
    }
    out.update(aggregate(reg))  # primary: regular trade dates only
    out["all_trade_dates_variant"] = {k: v for k, v in aggregate(recs).items() if k in (
        "n_trade_dates", "sigma_1m_ticks", "R_d_median_ticks", "ADV_median_contracts_v0_front",
        "vol_per_min_main_median", "vol_per_min_overnight_median")}
    return out


def daily_closes(root: str, files: list[tuple[str, str, str]]) -> pd.DataFrame:
    """Per trade date: close and instrument of the last bar, streaming file by file."""
    parts = []
    for f in files:
        if f[1] > LAST_ALLOWED_END:
            continue
        a = open_store(root, f[2])
        if len(a) == 0:
            EMPTY_FILES.setdefault(root, []).append(f[2])
            continue
        a = a[np.argsort(a["ts_event"], kind="stable")]
        df = pd.DataFrame({"td": trade_dates(a["ts_event"]), "ts": a["ts_event"].astype("int64"),
                           "close": a["close"].astype("float64") / PRICE_SCALE,
                           "inst": a["instrument_id"].astype("int64")})
        parts.append(df.groupby("td", sort=True).tail(1))
        del a
    allp = pd.concat(parts).sort_values("ts")
    last = allp.groupby("td", sort=True).tail(1).set_index("td").sort_index()
    return last[last.index <= np.datetime64(C4_END)]


def c4_stats(daily: pd.DataFrame) -> dict:
    c = daily["close"].values
    inst = daily["inst"].values
    same = inst[1:] == inst[:-1]
    pos = (c[1:] > 0) & (c[:-1] > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.log(c[1:] / c[:-1])
    years = pd.DatetimeIndex(daily.index[1:]).year.values
    nonpos = int((~pos & same).sum())
    per_year = {}
    for y in np.unique(years):
        sel = (years == y) & same & pos
        ry = r[sel]
        sd = float(np.std(ry, ddof=1)) if ry.size > 1 else None
        big = int((np.abs(ry) > BIG_MOVE_K * sd).sum()) if sd else 0
        big += int(((years == y) & same & ~pos).sum())  # non-positive price days counted as big
        per_year[int(y)] = {"n_returns": int(ry.size), "daily_sd_log": sd, "big_moves": big,
                            "roll_returns_skipped": int(((years == y) & ~same).sum()),
                            "n_trade_dates": int((pd.DatetimeIndex(daily.index).year == y).sum())}
    n_ret = sum(v["n_returns"] for v in per_year.values())
    n_big = sum(v["big_moves"] for v in per_year.values())
    full = [v for y, v in per_year.items() if v["n_trade_dates"] >= 240]
    s19 = {y: v for y, v in per_year.items() if 2019 <= y <= 2023}
    n19 = sum(v["n_returns"] for v in s19.values())
    b19 = sum(v["big_moves"] for v in s19.values())
    return {
        "c4_per_year": per_year,
        "c4_mean_per_full_year": (sum(v["big_moves"] for v in full) / len(full)) if full else None,
        "c4_full_years": [y for y, v in per_year.items() if v["n_trade_dates"] >= 240],
        "c4_rate_per_252d_owned_span": (n_big / n_ret * 252) if n_ret else None,
        "c4_rate_per_252d_2019_to_2023_10_31": (b19 / n19 * 252) if n19 else None,
        "c4_nonpositive_price_returns": nonpos,
        "c4_daily_closes": int(len(daily)),
        "c4_first_trade_date": str(daily.index[0].date()) if len(daily) else None,
        "c4_last_trade_date": str(daily.index[-1].date()) if len(daily) else None,
    }


def root_stats(root: str) -> dict:
    p = PRODUCTS[root]
    files = list_files(root)
    allowed = [f for f in files if f[1] <= LAST_ALLOWED_END]
    pilot = [f[2] for f in files if f[0] < PILOT_END_EXCL and f[1] > PILOT_START]
    cov = sorted((f[0], f[1]) for f in files if f[0] < PILOT_END_EXCL and f[1] > PILOT_START)
    contiguous = bool(cov) and cov[0][0] <= PILOT_START and cov[-1][1] >= PILOT_END_EXCL and all(
        a[1] == b[0] for a, b in zip(cov, cov[1:]))
    line = products_line(root)
    out = {
        "root": root,
        "group": GROUP_OF_PRODUCT[root],
        "tick_size_exchange_units": str(p.tick_size),
        "tick_value_usd": str(p.tick_value_usd),
        "vendor_price_factor": p.vendor_price_factor,
        "vendor_tick": str(p.vendor_tick),
        "tick_source": f"rules/products.py:{line} ({p.tick_source})",
        "first_file": files[0][2] if files else None,
        "last_file": files[-1][2] if files else None,
        "first_owned_file_start_date": files[0][0] if files else None,
        "last_owned_file_end_date_exclusive": files[-1][1] if files else None,
        "n_files": len(files),
        "n_files_opened_allowed": len(allowed),
        "file_gaps": [(a[1], b[0]) for a, b in zip(files, files[1:]) if a[1] != b[0]],
        "pilot_window_files_by_name": pilot,
        "pilot_window_covered_by_names": contiguous,
    }
    if not allowed:
        out["note"] = "no owned file ends on or before 2023-11-01; no statistics computed"
        return out
    out.update(window_stats(root, files))
    out.update(c4_stats(daily_closes(root, allowed)))
    out["empty_files_opened"] = EMPTY_FILES.get(root, [])
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    roots = sorted(d[:-4] for d in os.listdir(OHLCV) if d.endswith("_v_0"))
    only = sys.argv[1:]
    for root in roots:
        if only and root not in only:
            continue
        path = OUT_DIR / f"{root}.json"
        if path.exists():
            continue
        t0 = time.time()
        res = root_stats(root)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(res, indent=1, default=str))
        tmp.rename(path)
        print(f"{root} done in {time.time() - t0:.0f}s", flush=True)
    if not only:
        allres = [json.loads((OUT_DIR / f"{r}.json").read_text()) for r in roots]
        OUT_JSON.write_text(json.dumps({"generated_by": "reports/stage_e28_briefs/work/A0/A0_stats.py",
                                        "roots": allres}, indent=1, default=str))
        print(f"wrote {OUT_JSON} with {len(allres)} roots")


if __name__ == "__main__":
    main()
