"""Stage E.31 Part 1: QM and ZM daily-volume measures (V3) and kill rules.

Implements the "V3 measures, fixed details" and "Kill rules" sections of
reports/stage_e31_volume_request.md (sha256 09d83f43...). Reads only
ts_event, instrument_id and volume from the purchased ohlcv-1d DBN file plus
its symbol mappings. Prices are never kept, used, stored or reported.
No network call of any kind.

CLI: uv run python vol_measure.py --dbn PATH --out-json PATH --out-md PATH
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REQUEST_PATH = Path("reports/stage_e31_volume_request.md")
REQUEST_SHA256 = "09d83f433f2869aab4e26670c455266dd597a6a32673a9c367a846bdf5939b9e"
DEFAULT_MANIFEST = Path("reports/stage_e31_briefs/work/pilot/runs/vol_purchase_manifest.json")
ROOTS = ("QM", "ZM")
OUTRIGHT_RE = re.compile(r"^(QM|ZM)[FGHJKMNQUVXZ][0-9]{1,2}$")
MONTH_CODES = "FGHJKMNQUVXZ"
NS_PER_DAY = 86_400 * 10**9
WINDOW_MONTHS = 12
KILL_THRESHOLDS = {"QM": 1_000, "ZM": 5_000}
CHECK_SHARE_LIMIT = 0.01
WEEKEND = (5, 6)  # Saturday, Sunday (date.weekday())


class MeasureError(RuntimeError):
    """A stop condition from the brief (missing mapping, sha mismatch...)."""


# ---------------------------------------------------------------- symbols

def root_of(symbol: str) -> str | None:
    """Root by the raw symbol's leading root letters (QM or ZM), else None."""
    for root in ROOTS:
        if symbol.startswith(root):
            return root
    return None


def is_hyphen(symbol: str) -> bool:
    """The prompt's outright filter: any symbol containing a hyphen is dropped."""
    return "-" in symbol


def matches_outright(symbol: str) -> bool:
    return OUTRIGHT_RE.match(symbol) is not None


def decode_delivery_year(digits: str, year: int) -> int:
    """Delivery year from the symbol's digit(s) for a bar dated in `year`.

    One digit d: y = t - (t mod 10) + d, plus 10 if y < t - 1.
    Two digits: 20dd.
    """
    if not digits.isdigit() or len(digits) not in (1, 2):
        raise ValueError(f"bad delivery digits {digits!r}")
    if len(digits) == 2:
        return 2000 + int(digits)
    y = year - (year % 10) + int(digits)
    if y < year - 1:
        y += 10
    return y


def delivery_key(symbol: str, year: int) -> tuple[int, int] | None:
    """(delivery year, month 1..12) for a regex-matching outright, else None."""
    if not matches_outright(symbol):
        return None
    month = MONTH_CODES.index(symbol[2]) + 1
    return decode_delivery_year(symbol[3:], year), month


# ---------------------------------------------------------------- mappings

def invert_mappings(mappings: dict) -> dict[int, list[tuple[dt.date, dt.date, str]]]:
    """raw_symbol -> intervals  ==>  instrument_id -> [(start, end, raw_symbol)]."""
    inv: dict[int, list[tuple[dt.date, dt.date, str]]] = defaultdict(list)
    for raw, intervals in mappings.items():
        for iv in intervals:
            inv[int(iv["symbol"])].append((iv["start_date"], iv["end_date"], raw))
    return dict(inv)


def symbol_for(iid: int, day: dt.date, inv: dict) -> str:
    """Raw symbol of `iid` on `day`. Raises MeasureError if not resolvable."""
    entries = inv.get(iid)
    if not entries:
        raise MeasureError(f"instrument_id {iid} has no raw symbol in the DBN mappings")
    names = {e[2] for e in entries}
    if len(names) == 1:
        return entries[0][2]
    for start, end, raw in entries:  # Databento intervals: end exclusive
        if start <= day < end:
            return raw
    for start, end, raw in entries:
        if start <= day <= end:
            return raw
    raise MeasureError(f"instrument_id {iid} maps to {sorted(names)} but no interval covers {day}")


# ---------------------------------------------------------------- load

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_dbn(path: Path):
    """Return (ts_event ns, instrument_id, volume, mappings, meta) without prices."""
    import databento as db

    store = db.DBNStore.from_file(str(path))
    arr = store.to_ndarray()
    ts = np.asarray(arr["ts_event"], dtype=np.int64).copy()
    iid = np.asarray(arr["instrument_id"], dtype=np.int64).copy()
    vol = np.asarray(arr["volume"], dtype=np.int64).copy()
    del arr  # prices dropped immediately
    meta = store.metadata
    info = {
        "dataset": meta.dataset,
        "schema": str(meta.schema),
        "stype_in": str(meta.stype_in),
        "symbols": list(meta.symbols),
        "start_ns": int(meta.start),
        "end_ns": int(meta.end),
        "mapping_symbols": len(store.mappings),
    }
    return ts, iid, vol, store.mappings, info


# ---------------------------------------------------------------- records

def ns_to_date(ns: int) -> dt.date:
    return dt.date(1970, 1, 1) + dt.timedelta(days=int(ns // NS_PER_DAY))


def build_records(ts, iid, vol, inv) -> list[dict]:
    """One dict per bar: date, symbol, volume (no prices)."""
    return [
        {"date": ns_to_date(t), "symbol": symbol_for(int(i), ns_to_date(t), inv), "volume": int(v)}
        for t, i, v in zip(ts.tolist(), iid.tolist(), vol.tolist())
    ]


def split_records(records: list[dict]) -> dict:
    """Apply root, hyphen filter, weekend drop. Returns outrights and counts."""
    out = {"outright": [], "hyphen": defaultdict(lambda: {"bars": 0, "volume": 0, "symbols": set()}),
           "weekend": defaultdict(lambda: {"bars": 0, "volume": 0}),
           "other_root": {"bars": 0, "volume": 0, "symbols": set()},
           "instruments": defaultdict(set), "outright_symbols": defaultdict(set)}
    for r in records:
        root = root_of(r["symbol"])
        if root is None:
            out["other_root"]["bars"] += 1
            out["other_root"]["volume"] += r["volume"]
            out["other_root"]["symbols"].add(r["symbol"])
            continue
        out["instruments"][root].add(r["symbol"])
        if is_hyphen(r["symbol"]):
            h = out["hyphen"][root]
            h["bars"] += 1
            h["volume"] += r["volume"]
            h["symbols"].add(r["symbol"])
            continue
        if r["date"].weekday() in WEEKEND:
            w = out["weekend"][root]
            w["bars"] += 1
            w["volume"] += r["volume"]
            continue
        out["outright_symbols"][root].add(r["symbol"])
        out["outright"].append({**r, "root": root})
    return out


def check_line(outrights: list[dict]) -> dict:
    """Count and volume of kept non-hyphen symbols not matching OUTRIGHT_RE."""
    res = {}
    for root in ROOTS:
        rows = [r for r in outrights if r["root"] == root]
        total = sum(r["volume"] for r in rows)
        bad = [r for r in rows if not matches_outright(r["symbol"])]
        bad_vol = sum(r["volume"] for r in bad)
        res[root] = {
            "symbols": sorted({r["symbol"] for r in bad}),
            "bars": len(bad),
            "volume": bad_vol,
            "root_volume": total,
            "share": (bad_vol / total) if total else 0.0,
            "above_1pct": bool(total and bad_vol / total > CHECK_SHARE_LIMIT),
        }
    return res


def daily_by_root(outrights: list[dict]) -> dict[str, dict[dt.date, dict]]:
    """root -> date -> {volume, front, top}. Front = earliest delivery among
    that date's outrights with a bar (regex-matching symbols only); top = the
    day's highest-volume outright."""
    grouped: dict[str, dict[dt.date, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in outrights:
        grouped[r["root"]][r["date"]].append(r)
    res: dict[str, dict[dt.date, dict]] = {}
    for root in ROOTS:
        days = {}
        for day, rows in grouped.get(root, {}).items():
            keyed = [(delivery_key(r["symbol"], day.year), r) for r in rows]
            keyed = [(k, r) for k, r in keyed if k is not None]
            front = min(keyed, key=lambda kr: kr[0])[1] if keyed else None
            days[day] = {
                "volume": sum(r["volume"] for r in rows),
                "front": front["volume"] if front else 0,
                "front_symbol": front["symbol"] if front else None,
                "top": max(r["volume"] for r in rows),
            }
        res[root] = days
    return res


def universes(daily: dict) -> dict:
    """Primary: union of Mon-Fri dates with any QM or ZM outright bar.
    Secondary: each root's own dates."""
    union = sorted(set().union(*[set(daily[r]) for r in ROOTS]))
    return {"primary": union, **{r: sorted(daily[r]) for r in ROOTS}}


def series(daily_root: dict, dates: list[dt.date]) -> dict[str, np.ndarray]:
    """Zero-filled arrays of volume/front/top on the given dates."""
    zero = {"volume": 0, "front": 0, "top": 0}
    rows = [daily_root.get(d, zero) for d in dates]
    return {k: np.array([r[k] for r in rows], dtype=np.int64) for k in ("volume", "front", "top")}


# ---------------------------------------------------------------- window, quarters

def add_months(year: int, month: int, n: int) -> tuple[int, int]:
    idx = year * 12 + (month - 1) + n
    return idx // 12, idx % 12 + 1


def window_from_end(end_ns: int) -> tuple[dt.date, dt.date]:
    """Last 12 full calendar months whose last day is before the exclusive end.

    B = the latest first-of-month midnight UTC with B <= end; the last full
    month is the month before B.
    """
    end_day = ns_to_date(end_ns)
    by, bm = end_day.year, end_day.month  # month containing end; its 1st <= end
    ly, lm = add_months(by, bm, -1)
    win_end = dt.date(by, bm, 1) - dt.timedelta(days=1)
    sy, sm = add_months(ly, lm, -(WINDOW_MONTHS - 1))
    return dt.date(sy, sm, 1), win_end


def quarter_of(day: dt.date) -> str:
    return f"{day.year}Q{(day.month - 1) // 3 + 1}"


def stats(arrs: dict[str, np.ndarray]) -> dict:
    vol = arrs["volume"]
    total = int(vol.sum())
    if len(vol) == 0:
        return {"days": 0, "median": None, "p10": None, "front_share": None,
                "top_share": None, "total_volume": 0}
    return {
        "days": int(len(vol)),
        "median": float(np.median(vol)),
        "p10": float(np.percentile(vol, 10)),
        "front_share": (int(arrs["front"].sum()) / total) if total else None,
        "top_share": (int(arrs["top"].sum()) / total) if total else None,
        "total_volume": total,
    }


def quarter_table(daily_root: dict, dates: list[dt.date]) -> list[dict]:
    by_q: dict[str, list[dt.date]] = defaultdict(list)
    for d in dates:
        by_q[quarter_of(d)].append(d)
    quarters = sorted(by_q)
    table = []
    for q in quarters:
        row = {"quarter": q, **stats(series(daily_root, by_q[q]))}
        row["partial"] = q == quarters[-1]
        table.append(row)
    return table


def in_window(dates: list[dt.date], win: tuple[dt.date, dt.date]) -> list[dt.date]:
    return [d for d in dates if win[0] <= d <= win[1]]


def verdict(median: float | None, root: str) -> str:
    if median is None:
        return "FAIL"
    return "FAIL" if median < KILL_THRESHOLDS[root] else "PASS"


# ---------------------------------------------------------------- run

def measure(ts, iid, vol, mappings, meta) -> dict:
    inv = invert_mappings(mappings)
    missing = sorted({int(i) for i in np.unique(iid)} - set(inv))
    if missing:
        raise MeasureError(f"{len(missing)} instrument ids have no raw symbol: {missing[:20]}")
    records = build_records(ts, iid, vol, inv)
    parts = split_records(records)
    outrights = parts["outright"]
    checks = check_line(outrights)
    daily = daily_by_root(outrights)
    unis = universes(daily)
    win = window_from_end(meta["end_ns"])

    def root_block(root: str, d: dict) -> dict:
        own = sorted(d)
        prim = unis["primary"]
        w_prim, w_own = in_window(prim, win), in_window(own, win)
        s_prim, s_own = stats(series(d, w_prim)), stats(series(d, w_own))
        return {
            "quarters_primary": quarter_table(d, prim),
            "quarters_own": quarter_table(d, own),
            "window_primary": s_prim,
            "window_own": s_own,
            "window_zero_days_primary": int(sum(1 for x in w_prim if x not in d)),
        }

    roots = {}
    for root in ROOTS:
        blk = root_block(root, daily[root])
        blk["verdict_primary"] = verdict(blk["window_primary"]["median"], root)
        blk["verdict_own"] = verdict(blk["window_own"]["median"], root)
        blk["verdicts_differ"] = blk["verdict_primary"] != blk["verdict_own"]
        if checks[root]["above_1pct"]:
            clean = [r for r in outrights if matches_outright(r["symbol"]) or r["root"] != root]
            blk["without_nonmatching"] = root_block(root, daily_by_root(clean)[root])
        roots[root] = blk

    return {
        "meta": {**meta, "start": ns_to_date(meta["start_ns"]).isoformat(),
                 "end_exclusive_utc": dt.datetime.fromtimestamp(meta["end_ns"] / 1e9, dt.timezone.utc).isoformat()},
        "records_total": len(records),
        "instruments": {r: {"with_bars": len(parts["instruments"][r]),
                            "outright_with_weekday_bars": len(parts["outright_symbols"][r]),
                            "hyphen_dropped": len(parts["hyphen"][r]["symbols"]) if r in parts["hyphen"] else 0}
                        for r in ROOTS},
        "hyphen_dropped": {r: {"symbols": len(v["symbols"]), "bars": v["bars"], "volume": v["volume"]}
                           for r, v in parts["hyphen"].items()},
        "other_root": {"bars": parts["other_root"]["bars"], "volume": parts["other_root"]["volume"],
                       "symbols": sorted(parts["other_root"]["symbols"])},
        "weekend_bars": {r: dict(parts["weekend"].get(r, {"bars": 0, "volume": 0})) for r in ROOTS},
        "check_line": checks,
        "universe_days": {"primary": len(unis["primary"]), **{r: len(unis[r]) for r in ROOTS}},
        "window": {"start": win[0].isoformat(), "end": win[1].isoformat(),
                   "days_primary": len(in_window(unis["primary"], win)),
                   **{f"days_{r}": len(in_window(unis[r], win)) for r in ROOTS}},
        "roots": roots,
    }


def fmt(x, nd=0) -> str:
    if x is None:
        return "n/a"
    return f"{x:,.{nd}f}"


def qtable_md(rows: list[dict]) -> list[str]:
    out = ["| Quarter | Days | Median | P10 | Front-month share | Top-volume share |",
           "|---|---:|---:|---:|---:|---:|"]
    for r in rows:
        q = r["quarter"] + (f" (partial, {r['days']} days)" if r["partial"] else "")
        out.append(f"| {q} | {r['days']} | {fmt(r['median'], 1)} | {fmt(r['p10'], 1)} | "
                   f"{fmt(r['front_share'], 3) if r['front_share'] is not None else 'n/a'} | "
                   f"{fmt(r['top_share'], 3) if r['top_share'] is not None else 'n/a'} |")
    return out


def render_md(res: dict, prov: dict) -> str:
    w = res["window"]
    L = ["# Stage E.31 Part 1: QM and ZM daily volume (V3 measures and kill rules)", "",
         f"Generated by reports/stage_e31_briefs/work/pilot/vol_measure.py at {prov['generated_utc']} (UTC).",
         f"Request file: {prov['request_path']} (sha256 {prov['request_sha256']}, matches frozen value: {prov['request_sha_ok']}).",
         f"DBN file: {prov['dbn']} (sha256 {prov['dbn_sha256']}, matches manifest: {prov['dbn_sha_ok']}).",
         f"Data span: {res['meta']['start']} to {res['meta']['end_exclusive_utc']} (end exclusive); "
         f"{res['records_total']:,} bars. Only ts_event, instrument_id and volume were read; no prices.", "",
         "## Verdicts (kill rules, primary universe)", ""]
    for root in ROOTS:
        b = res["roots"][root]
        thr = KILL_THRESHOLDS[root]
        L.append(f"- {root}: median daily volume over the window (primary universe) = "
                 f"{fmt(b['window_primary']['median'], 1)} contracts; rule: below {thr:,} contracts = FAIL. "
                 f"Result: {b['verdict_primary']}. Own-universe median {fmt(b['window_own']['median'], 1)} "
                 f"gives {b['verdict_own']}" + (" (DIFFERENT, primary governs)." if b["verdicts_differ"] else " (same)."))
    L += ["", "## Window", "",
          f"- {w['start']} to {w['end']} (last 12 full calendar months before the exclusive end).",
          f"- Universe days in window: primary {w['days_primary']}, QM own {w['days_QM']}, ZM own {w['days_ZM']}.",
          f"- Primary-universe window days with zero-filled volume: QM {res['roots']['QM']['window_zero_days_primary']}, "
          f"ZM {res['roots']['ZM']['window_zero_days_primary']}.",
          "", "## Universes, instruments, filters", "",
          f"- Universe days (whole span): primary {res['universe_days']['primary']}, "
          f"QM own {res['universe_days']['QM']}, ZM own {res['universe_days']['ZM']}."]
    for root in ROOTS:
        i, h = res["instruments"][root], res["hyphen_dropped"].get(root, {"symbols": 0, "bars": 0, "volume": 0})
        L.append(f"- {root}: {i['with_bars']} instruments with bars; {i['outright_with_weekday_bars']} outrights kept "
                 f"(weekday bars); {h['symbols']} hyphen symbols dropped ({h['bars']:,} bars, volume {h['volume']:,}).")
    o = res["other_root"]
    L.append(f"- Bars with neither QM nor ZM root: {o['bars']} (volume {o['volume']:,}).")
    for root in ROOTS:
        wb = res["weekend_bars"][root]
        L.append(f"- Weekend (Sat/Sun UTC) outright bars excluded, {root}: {wb['bars']} bars, volume {wb['volume']:,}.")
    L += ["", "## Check line (non-hyphen symbols not matching ^(QM|ZM)[FGHJKMNQUVXZ][0-9]{1,2}$)", ""]
    for root in ROOTS:
        c = res["check_line"][root]
        L.append(f"- {root}: {len(c['symbols'])} symbols, {c['bars']} bars, volume {c['volume']:,} "
                 f"({c['share'] * 100:.3f}% of root volume); above 1%: {c['above_1pct']}"
                 + (f"; symbols {c['symbols']}" if c["symbols"] else "") + ".")
    for root in ROOTS:
        b = res["roots"][root]
        L += ["", f"## {root} by quarter, primary universe (QM-or-ZM dates, zero-filled)", ""]
        L += qtable_md(b["quarters_primary"])
        L += ["", f"## {root} by quarter, own universe", ""]
        L += qtable_md(b["quarters_own"])
        if "without_nonmatching" in b:
            L += ["", f"## {root} by quarter without non-matching symbols, primary universe", ""]
            L += qtable_md(b["without_nonmatching"]["quarters_primary"])
    L += ["", "Notes: median and P10 via numpy median / percentile (linear). Front-month share = quarter sum of the "
          "earliest-delivery outright's volume / quarter sum of root volume. Top-volume share (information only) = "
          "quarter sum of the day's highest-volume outright / quarter sum of root volume. The last quarter is partial.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dbn", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    a = ap.parse_args(argv)

    manifest = json.loads(a.manifest.read_text())
    dbn_sha = sha256_file(a.dbn)
    if dbn_sha != manifest["sha256"]:
        raise MeasureError(f"DBN sha256 {dbn_sha} != manifest {manifest['sha256']}")
    req_sha = sha256_file(REQUEST_PATH) if REQUEST_PATH.exists() else None
    ts, iid, vol, mappings, meta = load_dbn(a.dbn)
    res = measure(ts, iid, vol, mappings, meta)
    prov = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "dbn": str(a.dbn), "dbn_sha256": dbn_sha, "dbn_sha_ok": dbn_sha == manifest["sha256"],
            "request_path": str(REQUEST_PATH), "request_sha256": req_sha,
            "request_sha_ok": req_sha == REQUEST_SHA256}
    out = {"provenance": prov, **res}
    a.out_json.write_text(json.dumps(out, indent=1, default=str) + "\n")
    a.out_md.write_text(render_md(res, prov))
    for root in ROOTS:
        b = res["roots"][root]
        print(f"{root}: window median primary {b['window_primary']['median']} -> {b['verdict_primary']}; "
              f"own {b['window_own']['median']} -> {b['verdict_own']}")
    print(f"window {res['window']['start']}..{res['window']['end']} days primary {res['window']['days_primary']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except MeasureError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        sys.exit(2)
