"""Stage E.29 reference correlations (reports/stage_e29_model.md section 8; brief_corr.md).

Front contracts of CL, ZM, GC, NQ from owned ohlcv-1m v_0 bars, trade dates 2022-11-01..2023-10-31.
Reference only, never a model input. Run from the repo root:
    nice -n 10 uv run python reports/stage_e29_briefs/work/corr/corr_stats.py

DATA RULE (binding, enforced in open_store before any open): only
data/vendor/databento/GLBX.MDP3/ohlcv-1m/<ROOT>_v_0/range=<a>_<b>.dbn.zst with a >= 2022-10-01 and
b <= 2023-11-01; never mbp-1, data/sealed, data/processed*, MES, holdout, embargo or research-window
paths. The decision is taken from the file name and the resolved path before the file is opened.
Trade-date and calendar conventions are copied from reports/stage_e28_briefs/work/A0/A0_stats.py.
"""
from __future__ import annotations

import importlib
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

os.nice(10)
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

import databento  # noqa: E402

from data.calendars import GROUP_OF_PRODUCT  # noqa: E402

ROOTS = ("CL", "ZM", "GC", "NQ")
OHLCV = REPO / "data/vendor/databento/GLBX.MDP3/ohlcv-1m"
WORK = REPO / "reports/stage_e29_briefs/work/corr"
OUT_JSON = REPO / "reports/stage_e29_briefs/E29_correlations.json"
FIRST_ALLOWED_START = "2022-10-01"  # the month before the window, for the 2022-11-01 prior close
LAST_ALLOWED_END = "2023-11-01"  # A0 rule: range=2023-10-01_2023-11-01 is the last file that may be opened
WIN_START, WIN_END = date(2022, 11, 1), date(2023, 10, 31)
MAIN_PT = (6 * 60 + 30, 13 * 60)  # [06:30, 13:00) America/Vancouver, minutes after midnight
PRICE_SCALE = 1e9
RANGE_RE = re.compile(r"^range=(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.dbn\.zst$")
FORBIDDEN = ("mbp-1", "sealed", "processed", "holdout", "embargo", "research", "/MES")
OPENED: list[dict] = []


def list_window_files(root: str) -> list[str]:
    """Pick files by name only: start >= 2022-10-01 and end <= 2023-11-01."""
    out = []
    for name in sorted(os.listdir(OHLCV / f"{root}_v_0")):
        m = RANGE_RE.match(name)
        if m and m.group(1) >= FIRST_ALLOWED_START and m.group(2) <= LAST_ALLOWED_END:
            out.append(name)
    return out


def open_store(root: str, name: str) -> np.ndarray:
    m = RANGE_RE.match(name)
    if m is None or m.group(2) > LAST_ALLOWED_END or m.group(1) < FIRST_ALLOWED_START:
        raise RuntimeError(f"DATA RULE: refusing to open {root}/{name}")
    if root == "MES" or root not in ROOTS:
        raise RuntimeError(f"DATA RULE: refusing root {root}")
    rel = OHLCV / f"{root}_v_0" / name
    for attempt in (0, 1):
        path = os.path.realpath(rel)  # resolve at open (data/vendor may be a symlink)
        low = path.lower()
        bad = [f for f in FORBIDDEN if f.lower() in low]
        if bad or "/ohlcv-1m/" not in path:
            raise RuntimeError(f"DATA RULE: refusing path {path} ({bad})")
        try:
            arr = databento.DBNStore.from_file(path).to_ndarray()
            OPENED.append({"root": root, "file": name, "range_start": m.group(1), "range_end": m.group(2),
                           "resolved_path": path, "rows": int(len(arr))})
            return arr[["instrument_id", "ts_event", "open", "high", "low", "close", "volume"]].copy()
        except FileNotFoundError:
            if attempt == 0:
                print(f"  {root}/{name} missing at {path}; retry in 60 s", flush=True)
                time.sleep(60)
                continue
            raise
    raise AssertionError


def trade_dates(ts: np.ndarray) -> np.ndarray:
    """A0 copy. CME trade date: CT time >= 17:00 belongs to the next day; Sat/Sun roll to Monday."""
    ct = pd.to_datetime(ts.astype("int64"), utc=True).tz_convert("America/Chicago")
    days = ct.tz_localize(None).normalize().values.astype("datetime64[D]")
    days = days + (ct.hour.values >= 17).astype("int64")
    wd = (days.astype("int64") + 3) % 7  # Monday = 0
    days = days + np.where(wd == 5, 2, np.where(wd == 6, 1, 0))
    return days


def pt_minutes(ns: np.ndarray) -> np.ndarray:
    pt = pd.to_datetime(ns, utc=True).tz_convert("America/Vancouver")
    return pt.hour.values * 60 + pt.minute.values


def early_halt_days(group: str) -> tuple[set, str]:
    """A0 copy: EARLY_HALT dates of the group's calendar."""
    name = "data.cme_calendar" if group == "equity" else f"data.calendars.{group}"
    mod = importlib.import_module(name)
    days = {d for d, h in mod.HOLIDAYS.items() if h.kind.name == "EARLY_HALT"}
    return days, name


def load_bars(root: str) -> pd.DataFrame:
    parts = []
    for name in list_window_files(root):
        a = open_store(root, name)
        parts.append(pd.DataFrame({
            "ts": a["ts_event"].astype("int64"), "inst": a["instrument_id"].astype("int64"),
            "open": a["open"].astype("float64") / PRICE_SCALE, "high": a["high"].astype("float64") / PRICE_SCALE,
            "low": a["low"].astype("float64") / PRICE_SCALE, "close": a["close"].astype("float64") / PRICE_SCALE,
            "volume": a["volume"].astype("float64")}))
        del a
    df = pd.concat(parts, ignore_index=True).sort_values("ts", kind="stable").reset_index(drop=True)
    df["td"] = trade_dates(df["ts"].values)
    df["ptm"] = pt_minutes(df["ts"].values)
    return df


def daily_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per trade date, built from the front contract's bars only.

    Front contract = the instrument_id with the largest summed volume on that trade date within the v_0 series.
    """
    vol = df.groupby(["td", "inst"], sort=True)["volume"].sum().reset_index()
    ninst = vol.groupby("td")["inst"].nunique()
    front = vol.sort_values(["td", "volume", "inst"], ascending=[True, False, True]).groupby("td").head(1)
    front = front.set_index("td")["inst"]
    f = df[df["inst"].values == front.reindex(df["td"]).values]
    g = f.groupby("td", sort=True)
    out = pd.DataFrame({"inst": front, "n_inst": ninst, "close": g["close"].last(), "high": g["high"].max(),
                        "low": g["low"].min(), "bars": g.size()})
    m = f[(f["ptm"] >= MAIN_PT[0]) & (f["ptm"] < MAIN_PT[1])]
    gm = m.groupby("td", sort=True)
    out["main_open"] = gm["open"].first()
    out["main_close"] = gm["close"].last()
    out["main_bars"] = gm.size()
    out.index = pd.to_datetime(out.index)
    out["roll"] = out["inst"].ne(out["inst"].shift(1)) & out["inst"].shift(1).notna()
    return out


def series(day: pd.DataFrame, drop_dates: set) -> pd.DataFrame:
    """Returns and ranges on the kept dates (roll dates dropped; returns only within one instrument)."""
    d = day[~day.index.map(lambda x: x.date() in drop_dates)].copy()
    prev_inst, prev_close = d["inst"].shift(1), d["close"].shift(1)
    ok = (d["inst"] == prev_inst) & ~d["roll"]
    d["ret"] = np.where(ok, np.log(d["close"] / prev_close), np.nan)
    d["range_pct"] = np.where(~d["roll"], (d["high"] - d["low"]) / d["close"] * 100.0, np.nan)
    d["ret_main"] = np.where(~d["roll"] & d["main_open"].notna(), np.log(d["main_close"] / d["main_open"]),
                             np.nan)
    win = (d.index >= pd.Timestamp(WIN_START)) & (d.index <= pd.Timestamp(WIN_END))
    return d[win]


def pair_stats(a: pd.Series, b: pd.Series) -> dict:
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    n = len(j)
    if n < 4:
        return {"n_days": n}
    r = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
    rs = float(j.iloc[:, 0].rank().corr(j.iloc[:, 1].rank()))
    z, se = np.arctanh(r), 1.0 / np.sqrt(n - 3)
    return {"n_days": n, "pearson": round(r, 4), "pearson_ci95_fisher": [round(float(np.tanh(z - 1.96 * se)), 4),
            round(float(np.tanh(z + 1.96 * se)), 4)], "spearman": round(rs, 4)}


def correlations(sers: dict[str, pd.DataFrame]) -> dict:
    out = {}
    for col in ("ret", "range_pct", "ret_main"):
        tab = {}
        for i, a in enumerate(ROOTS):
            for b in ROOTS[i + 1:]:
                tab[f"{a}-{b}"] = pair_stats(sers[a][col].rename(a), sers[b][col].rename(b))
        out[col] = tab
    return out


def root_summary(root: str, day: pd.DataFrame, s: pd.DataFrame, halts_in: list[str], cal: str) -> dict:
    w = day[(day.index >= pd.Timestamp(WIN_START)) & (day.index <= pd.Timestamp(WIN_END))]
    return {
        "group": GROUP_OF_PRODUCT[root], "early_halt_calendar": cal,
        "trade_dates_in_window": int(len(w)), "first_trade_date": str(w.index[0].date()),
        "last_trade_date": str(w.index[-1].date()),
        "roll_dates_in_window": [str(x.date()) for x in w.index[w["roll"].values]],
        "front_instrument_ids_in_window": sorted({int(x) for x in w["inst"]}),
        "dates_with_two_or_more_instruments": int((w["n_inst"] > 1).sum()),
        "early_halt_dates_in_window_excluded": halts_in,
        "n_ret": int(s["ret"].notna().sum()), "n_range": int(s["range_pct"].notna().sum()),
        "n_ret_main": int(s["ret_main"].notna().sum()),
        "ret_sd_daily": round(float(s["ret"].std(ddof=1)), 6),
        "range_pct_median": round(float(s["range_pct"].median()), 4),
        "main_bars_median": float(s["main_bars"].median()),
    }


def main() -> None:
    t0 = time.time()
    days, sers_p, sers_a, summ_p, summ_a = {}, {}, {}, {}, {}
    for root in ROOTS:
        day = daily_table(load_bars(root))
        day.to_csv(WORK / f"daily_{root}.csv")
        days[root] = day
        halts, cal = early_halt_days(GROUP_OF_PRODUCT[root])
        halts_in = sorted(str(d) for d in halts if WIN_START <= d <= WIN_END
                          and pd.Timestamp(d) in day.index)
        sers_p[root] = series(day, halts)
        sers_a[root] = series(day, set())
        summ_p[root] = root_summary(root, day, sers_p[root], halts_in, cal)
        summ_a[root] = root_summary(root, day, sers_a[root], [], cal)
        print(f"{root}: {summ_p[root]['trade_dates_in_window']} dates, rolls {len(summ_p[root]['roll_dates_in_window'])},"
              f" n_ret {summ_p[root]['n_ret']}", flush=True)
    res = {
        "stage": "E.29", "purpose": "reference price correlations, never a model input (stage_e29_model.md s8)",
        "window_trade_dates": [str(WIN_START), str(WIN_END)],
        "zm_substitute": None,
        "files_opened": OPENED,
        "per_root_primary": summ_p,
        "per_root_all_dates": {r: {k: summ_a[r][k] for k in ("n_ret", "n_range", "n_ret_main")} for r in ROOTS},
        "correlations_primary_early_halt_dates_excluded": correlations(sers_p),
        "correlations_all_trade_dates": correlations(sers_a),
        "runtime_s": round(time.time() - t0, 1),
    }
    OUT_JSON.write_text(json.dumps(res, indent=1))
    print(f"wrote {OUT_JSON.relative_to(REPO)}; files opened {len(OPENED)}; {res['runtime_s']} s")


if __name__ == "__main__":
    main()
