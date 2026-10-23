"""Independent recomputation of the Stage E.31 Part 1 volume numbers.

Written from reports/stage_e31_volume_request.md only (sha256 09d83f43...).
Reads only ts_event, instrument_id, volume and the DBN symbol mappings.
No price field is referenced anywhere in this file.
Usage: verify_vol_calc.py <dbn.zst> <out.json>
"""
import collections
import datetime as dt
import json
import re
import sys

import databento as db
import numpy as np

EPOCH = dt.date(1970, 1, 1)
NS_DAY = 86_400_000_000_000
MONTH_CODE = {c: i + 1 for i, c in enumerate("FGHJKMNQUVXZ")}
STD_RE = re.compile(r"^(QM|ZM)[FGHJKMNQUVXZ][0-9]{1,2}$")
ROOTS = ("QM", "ZM")


def to_date(day):
    return EPOCH + dt.timedelta(days=int(day))


def day_int(d):
    return (d - EPOCH).days


def last_day_of_month(y, m):
    nxt = dt.date(y + (m // 12), (m % 12) + 1, 1)
    return nxt - dt.timedelta(days=1)


def window_for(end_excl):
    y, m = end_excl.year, end_excl.month
    while last_day_of_month(y, m) >= end_excl:
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    end_y, end_m = y, m
    sy, sm = end_y, end_m - 11
    while sm < 1:
        sm += 12
        sy -= 1
    return dt.date(sy, sm, 1), last_day_of_month(end_y, end_m)


def delivery(sym, year):
    """(year, month) from a standard outright symbol on a date in `year`."""
    mo = MONTH_CODE[sym[2]]
    digits = sym[3:]
    if len(digits) == 1:
        d = int(digits)
        y = year - (year % 10) + d
        if y < year - 1:
            y += 10
    else:
        y = 2000 + int(digits)
    return (y, mo)


def quarter_of(d):
    return (d.year, (d.month - 1) // 3 + 1)


def stats(vec):
    v = np.asarray(vec, dtype=float)
    if len(v) == 0:
        return {"days": 0, "median": None, "p10": None}
    return {"days": int(len(v)), "median": float(np.median(v)),
            "p10": float(np.percentile(v, 10))}


def main(path, out):
    s = db.DBNStore.from_file(path)
    meta = s.metadata
    arr = s.to_ndarray()
    ts = arr["ts_event"].astype("int64")
    iid = arr["instrument_id"].astype("int64")
    vol = arr["volume"].astype("int64")
    del arr
    res = {"n_records": int(len(ts))}
    res["meta"] = {"dataset": meta.dataset, "schema": str(meta.schema),
                   "start_ns": int(meta.start), "end_ns": int(meta.end),
                   "start_utc": str(np.datetime64(int(meta.start), "ns")),
                   "end_utc": str(np.datetime64(int(meta.end), "ns"))}
    res["ts_event_all_midnight_utc"] = bool(np.all(ts % NS_DAY == 0))
    days = ts // NS_DAY
    res["first_bar_date"] = str(to_date(days.min()))
    res["last_bar_date"] = str(to_date(days.max()))
    end_excl = to_date(int(meta.end) // NS_DAY)
    res["end_exclusive_date"] = str(end_excl)
    res["end_has_time_part"] = bool(int(meta.end) % NS_DAY != 0)

    # ---- symbol mapping: instrument_id -> intervals [start, end) of raw symbols
    ivals = collections.defaultdict(list)
    for raw, lst in meta.mappings.items():
        for e in lst:
            ivals[int(e["symbol"])].append(
                (day_int(e["start_date"]), day_int(e["end_date"]), raw))
    reused = {i: v for i, v in ivals.items() if len({r for _, _, r in v}) > 1}
    res["mapping"] = {
        "raw_symbols": len(meta.mappings),
        "distinct_ids": len(ivals),
        "ids_with_multiple_raw": len(reused),
        "reused_detail": {str(i): [[str(to_date(a)), str(to_date(b)), r]
                                   for a, b, r in sorted(v)]
                          for i, v in reused.items()},
    }
    # resolve each record by date interval; test half-open and closed ends
    raw_excl = []
    unresolved_excl = multi_excl = 0
    unresolved_closed = multi_closed = 0
    differ_excl_vs_closed = 0
    for i, d in zip(iid.tolist(), days.tolist()):
        c = [r for a, b, r in ivals.get(i, ()) if a <= d < b]
        k = [r for a, b, r in ivals.get(i, ()) if a <= d <= b]
        if len(c) == 0:
            unresolved_excl += 1
        if len(c) > 1:
            multi_excl += 1
        if len(k) == 0:
            unresolved_closed += 1
        if len(k) > 1:
            multi_closed += 1
        if sorted(set(c)) != sorted(set(k)):
            differ_excl_vs_closed += 1
        raw_excl.append(c[0] if c else None)
    res["mapping"].update({
        "records_unresolved_halfopen": unresolved_excl,
        "records_multi_halfopen": multi_excl,
        "records_unresolved_closed": unresolved_closed,
        "records_multi_closed": multi_closed,
        "records_resolution_differs_halfopen_vs_closed": differ_excl_vs_closed,
    })
    # naive map (id -> a single raw symbol) would misname how many records?
    naive = {}
    for i, v in ivals.items():
        naive[i] = sorted(v)[-1][2]
    res["mapping"]["records_misnamed_by_naive_last_symbol"] = int(sum(
        1 for i, r in zip(iid.tolist(), raw_excl) if r is not None and naive[i] != r))
    # records of reused ids
    res["mapping"]["records_of_reused_ids"] = int(sum(1 for i in iid.tolist() if i in reused))

    # ---- classification
    n = len(ts)
    root = np.array([r[:2] if r else "??" for r in raw_excl])
    hyph = np.array([("-" in r) if r else False for r in raw_excl])
    weekend = ((days + 3) % 7) >= 5
    res["root_not_QM_ZM_records"] = int(np.sum(~np.isin(root, ROOTS)))
    res["duplicate_instrument_day_records"] = int(n - len(set(zip(iid.tolist(), days.tolist()))))
    res["zero_volume_records"] = int(np.sum(vol == 0))
    res["negative_volume_records"] = int(np.sum(vol < 0))

    hy = {}
    for rt in ROOTS:
        m = (root == rt) & hyph
        o = (root == rt) & ~hyph
        hy[rt] = {
            "hyphen_instruments": len({r for r, mm in zip(raw_excl, m) if mm}),
            "hyphen_bars": int(m.sum()), "hyphen_volume": int(vol[m].sum()),
            "outright_instruments": len({r for r, mm in zip(raw_excl, o) if mm}),
            "outright_bars": int(o.sum()), "outright_volume": int(vol[o].sum()),
            "outright_bars_weekend": int((o & weekend).sum()),
            "outright_volume_weekend": int(vol[o & weekend].sum()),
            "outright_bars_saturday": int((o & (((days + 3) % 7) == 5)).sum()),
            "outright_bars_sunday": int((o & (((days + 3) % 7) == 6)).sum()),
            "all_bars_weekend_incl_spreads": int(((root == rt) & weekend).sum()),
            "all_volume_weekend_incl_spreads": int(vol[(root == rt) & weekend].sum()),
        }
    res["hyphen_and_weekend_overall"] = hy

    # ---- outrights, standard-symbol check
    outr = np.isin(root, ROOTS) & ~hyph
    nonstd = {}
    for rt in ROOTS:
        m = outr & (root == rt)
        bad = [(r, int(v)) for r, v, mm in zip(raw_excl, vol.tolist(), m)
               if mm and not STD_RE.match(r)]
        tot = int(vol[m].sum())
        badvol = int(sum(v for _, v in bad))
        nonstd[rt] = {"nonmatching_bars": len(bad),
                      "nonmatching_symbols": sorted({r for r, _ in bad})[:20],
                      "nonmatching_n_symbols": len({r for r, _ in bad}),
                      "nonmatching_volume": badvol, "root_outright_volume": tot,
                      "share": (badvol / tot) if tot else 0.0}
    res["nonstandard_outrights"] = nonstd

    # ---- daily aggregation (weekdays only, outrights only)
    keep = outr & ~weekend
    dayvol = collections.defaultdict(int)          # (root, day) -> volume
    bars = collections.defaultdict(list)           # (root, day) -> [(delivery, vol, raw)]
    for r, d, v, rw, k in zip(root.tolist(), days.tolist(), vol.tolist(),
                              raw_excl, keep.tolist()):
        if not k:
            continue
        dayvol[(r, d)] += v
        yr = to_date(d).year
        dv = delivery(rw, yr) if STD_RE.match(rw) else None
        bars[(r, d)].append((dv, v, rw))

    universe = sorted({d for (_, d) in dayvol})
    own = {rt: sorted({d for (r, d) in dayvol if r == rt}) for rt in ROOTS}
    res["universe_dates_total"] = len(universe)
    res["own_dates_total"] = {rt: len(own[rt]) for rt in ROOTS}

    # front month per (root, day): earliest delivery among standard outrights
    front_vol = {}
    maxvol = {}
    tie_front = 0
    nostd_in_day = 0
    for key, lst in bars.items():
        std = [(dv, v, rw) for dv, v, rw in lst if dv is not None]
        nostd_in_day += len(lst) - len(std)
        if std:
            md = min(dv for dv, _, _ in std)
            cand = [x for x in std if x[0] == md]
            if len(cand) > 1:
                tie_front += 1
            front_vol[key] = sum(v for _, v, _ in cand) if len(cand) == 1 else cand[0][1]
        else:
            front_vol[key] = 0
        maxvol[key] = max(v for _, v, _ in lst)
    res["front_month_tie_days"] = tie_front
    res["nonstandard_bars_in_front_calc"] = nostd_in_day

    # ---- window
    w0, w1 = window_for(end_excl)
    res["window"] = {"start": str(w0), "end": str(w1)}
    wdays = [d for d in universe if w0 <= to_date(d) <= w1]
    n_weekdays = sum(1 for k in range((w1 - w0).days + 1)
                     if (w0 + dt.timedelta(days=k)).weekday() < 5)
    res["window"]["calendar_days"] = (w1 - w0).days + 1
    res["window"]["weekdays"] = n_weekdays
    res["window"]["universe_days"] = len(wdays)
    res["window"]["weekdays_not_in_universe"] = [
        str(w0 + dt.timedelta(days=k)) for k in range((w1 - w0).days + 1)
        if (w0 + dt.timedelta(days=k)).weekday() < 5
        and day_int(w0 + dt.timedelta(days=k)) not in set(universe)]
    res["window"]["own_days"] = {
        rt: sum(1 for d in own[rt] if w0 <= to_date(d) <= w1) for rt in ROOTS}
    res["window"]["zero_fill_days_primary"] = {
        rt: sum(1 for d in wdays if dayvol.get((rt, d), 0) == 0) for rt in ROOTS}
    kill = {"QM": 1000, "ZM": 5000}
    res["window"]["median_primary"] = {}
    res["window"]["median_own"] = {}
    res["window"]["verdict_primary"] = {}
    res["window"]["verdict_own"] = {}
    for rt in ROOTS:
        vp = [dayvol.get((rt, d), 0) for d in wdays]
        vo = [dayvol[(rt, d)] for d in own[rt] if w0 <= to_date(d) <= w1]
        res["window"]["median_primary"][rt] = float(np.median(vp))
        res["window"]["median_own"][rt] = float(np.median(vo))
        res["window"]["verdict_primary"][rt] = "FAIL" if np.median(vp) < kill[rt] else "PASS"
        res["window"]["verdict_own"][rt] = "FAIL" if np.median(vo) < kill[rt] else "PASS"
        res["window"].setdefault("stats_primary", {})[rt] = stats(vp)
        res["window"].setdefault("stats_own", {})[rt] = stats(vo)
        res["window"].setdefault("sum_volume", {})[rt] = int(sum(vp))

    # ---- per root and quarter
    quarters = sorted({quarter_of(to_date(d)) for d in universe})
    qt = {}
    for rt in ROOTS:
        rows = []
        for q in quarters:
            ud = [d for d in universe if quarter_of(to_date(d)) == q]
            od = [d for d in own[rt] if quarter_of(to_date(d)) == q]
            vp = [dayvol.get((rt, d), 0) for d in ud]
            vo = [dayvol[(rt, d)] for d in od]
            tot = sum(vo)
            fm = sum(front_vol.get((rt, d), 0) for d in od)
            hm = sum(maxvol.get((rt, d), 0) for d in od)
            sp, so = stats(vp), stats(vo)
            rows.append({"quarter": f"{q[0]}Q{q[1]}",
                         "days_primary": sp["days"], "median_primary": sp["median"],
                         "p10_primary": sp["p10"],
                         "days_own": so["days"], "median_own": so["median"],
                         "p10_own": so["p10"],
                         "volume": int(tot),
                         "front_share": (fm / tot) if tot else None,
                         "top_share_info": (hm / tot) if tot else None})
        qt[rt] = rows
    res["quarters"] = qt
    res["last_quarter_partial_days"] = qt["QM"][-1]["days_primary"]

    # ---- sensitivity: tables without non-matching symbols if > 1%
    res["nonstd_removed_tables"] = {}
    for rt in ROOTS:
        if nonstd[rt]["share"] > 0.01:
            res["nonstd_removed_tables"][rt] = "NEEDED (not computed here)"

    with open(out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    w = res["window"]
    print("records", res["n_records"], "end_excl", res["end_exclusive_date"],
          "window", w["start"], w["end"], "universe_days", w["universe_days"])
    print("median_primary", w["median_primary"], w["verdict_primary"])
    print("median_own", w["median_own"], w["verdict_own"], "own_days", w["own_days"])
    print("unresolved/multi", res["mapping"]["records_unresolved_halfopen"],
          res["mapping"]["records_multi_halfopen"], "reused ids",
          res["mapping"]["ids_with_multiple_raw"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
