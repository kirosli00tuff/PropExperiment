#!/usr/bin/env python3
"""Stage E.32 Part F: aggregate F_scan_out/*.json (counts, sizes, timings only) into markdown
fragments under F_agg_out/ and F_agg_summary.json. Reads also the four manifest.json headers
(mappings, metadata) and E.31's split markers (per-day counts) for cross-checks."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
W = REPO / "reports/stage_e32_briefs/work/F_data_facts"
SCAN = W / "F_scan_out"
OUTD = W / "F_agg_out"
MAN = REPO / "data/vendor/databento/GLBX.MDP3/mbo/Z1_ZM_v_0-ZM_v_1/manifest.json"
SPLIT = Path("/mnt/large-storage/market_data/PropExperiment/derived/e31")
SERIES = ("Z1", "Z2", "Z3", "Z4")
NAMES = {"Z1": "ZM MBO", "Z2": "ZS MBP-1", "Z3": "ZL MBP-1", "Z4": "definitions"}


def load(series: str) -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(SCAN.glob(f"{series}_*.json"))]


def fmt(n: float) -> str:
    return f"{n:,.0f}"


def gb(n: float) -> str:
    return f"{n / 1e9:,.3f}"


def order_stats(rows: list[tuple[str, int]]) -> dict:
    """rows: (day, count). Lower median at index (N-1)//2 and nearest-rank p90 at
    ceil(0.9 N) - 1 of the ascending sort by (count, day); ties go to the earlier date."""
    s = sorted(rows, key=lambda r: (r[1], r[0]))
    n = len(s)
    pick = {"min": s[0], "median": s[(n - 1) // 2], "p90": s[math.ceil(0.9 * n) - 1],
            "max": s[-1]}
    return {"n_days": n, **{k: {"day": v[0], "count": v[1]} for k, v in pick.items()}}


CONFLICTS: dict[str, list] = defaultdict(list)


def merged_mappings(man: dict) -> dict[str, list[list]]:
    """Per UTC date, the instrument id each monthly header maps the symbol to; dates where two
    headers disagree are recorded in CONFLICTS (the later file's id is kept); then runs."""
    from datetime import timedelta
    per: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    for f in sorted(man["files"], key=lambda f: (f["series"], f["month"])):
        if f["series"] == "Z4":
            continue
        for sym, ents in (f["header"].get("mappings") or {}).items():
            for e in ents:
                d = date.fromisoformat(e["start_date"][:10])
                end = date.fromisoformat(e["end_date"][:10])
                while d < end:
                    per[sym][d.isoformat()].add((f["month"], str(e["symbol"])))
                    d += timedelta(days=1)
    out: dict[str, list[list]] = {}
    for sym, days in per.items():
        runs: list[list] = []
        for d in sorted(days):
            ids = {i for _, i in days[d]}
            if len(ids) > 1:
                CONFLICTS[sym].append((d, sorted(days[d])))
            iid = max(days[d])[1]  # the latest month's header
            nxt = (date.fromisoformat(d) + timedelta(days=1)).isoformat()
            if runs and runs[-1][2] == iid and runs[-1][1] == d:
                runs[-1][1] = nxt
            else:
                runs.append([d, nxt, iid])
        out[sym] = runs
    return out


def main() -> int:
    OUTD.mkdir(exist_ok=True)
    data = {s: load(s) for s in SERIES}
    man = json.loads(MAN.read_text())
    summ: dict = {}
    # ---- definitions: instrument id -> raw symbol (outrights) ----
    raw: dict[str, dict] = {}
    for f in data["Z4"]:
        for iid, e in f["outrights"].items():
            r = raw.setdefault(iid, {"raw_symbol": e["raw_symbol"], "months": [],
                                     "expiration": e.get("expiration"),
                                     "match_algorithm": e.get("match_algorithm"),
                                     "symbols_seen": set()})
            r["months"].append(f["month"])
            r["symbols_seen"].update(e.get("symbols_seen", []))
            if e["raw_symbol"] != r["raw_symbol"]:
                r["symbols_seen"].add(e["raw_symbol"])
    maps = merged_mappings(man)
    lines = ["| Continuous symbol | instrument_id | raw_symbol (Z4) | Mapped from (UTC date) | to (exclusive) | Expiration (Z4, UTC date) |",
             "|---|---|---|---|---|---|"]
    map_rows = []
    for sym in ("ZM.v.0", "ZM.v.1", "ZS.v.0", "ZL.v.0"):
        for a, b, iid in maps.get(sym, []):
            r = raw.get(iid, {})
            exp = r.get("expiration")
            exp_d = datetime.fromtimestamp(exp / 1e9, timezone.utc).date().isoformat() if exp else "?"
            lines.append(f"| {sym} | {iid} | {r.get('raw_symbol', 'NOT IN Z4')} | {a} | {b} | {exp_d} |")
            map_rows.append({"symbol": sym, "iid": iid, "raw": r.get("raw_symbol"), "from": a,
                             "to": b, "expiration": exp_d})
    (OUTD / "mappings.md").write_text("\n".join(lines) + "\n")
    summ["mappings"] = map_rows
    summ["mapping_conflicts"] = {k: v for k, v in CONFLICTS.items()}
    summ["mapping_runs_per_symbol"] = {k: len(v) for k, v in maps.items()}
    summ["mapping_distinct_ids"] = {k: len({r[2] for r in v}) for k, v in maps.items()}
    summ["mapping_returns"] = {k: sum(1 for j in range(len(v)) if v[j][2] in {r[2] for r in v[:j]})
                               for k, v in maps.items()}
    summ["raw_symbol_changes"] = {k: sorted(v["symbols_seen"]) for k, v in raw.items()
                                  if v["symbols_seen"]}
    algo = defaultdict(set)
    for k, v in raw.items():
        algo[v["raw_symbol"][:2]].add(v["match_algorithm"])
    summ["match_algorithm_by_root"] = {k: sorted(v) for k, v in algo.items()}
    summ["z4_instrument_class_totals"] = {}
    for f in data["Z4"]:
        for c, n in f["instrument_class_counts"].items():
            summ["z4_instrument_class_totals"][c] = summ["z4_instrument_class_totals"].get(c, 0) + n
    summ["z4_outright_ids_total"] = len(raw)
    summ["z4_outrights_by_root"] = {r: sum(1 for v in raw.values() if v["raw_symbol"][:2] == r)
                                    for r in ("ZM", "ZS", "ZL")}
    # ---- sizes per month ----
    size_lines = ["| Month | " + " | ".join(f"{NAMES[s]} compressed GB | {NAMES[s]} decompressed GB"
                                         for s in SERIES) + " |",
                  "|---|" + "---|---|" * len(SERIES)]
    tot = {s: [0, 0, 0, 0] for s in SERIES}
    months = sorted({f["month"] for f in data["Z1"]})
    for m in months:
        cells = []
        for s in SERIES:
            f = next(x for x in data[s] if x["month"] == m)
            cells += [gb(f["bytes_compressed"]), gb(f["bytes_decompressed_dbn"])]
            tot[s][0] += f["bytes_compressed"]
            tot[s][1] += f["bytes_decompressed_dbn"]
            tot[s][2] += f["counts"]["records"]
            tot[s][3] += f["manifest_records"]
        size_lines.append(f"| {m} | " + " | ".join(cells) + " |")
    size_lines.append("| **Total** | " + " | ".join(f"**{gb(tot[s][0])}** | **{gb(tot[s][1])}**"
                                                   for s in SERIES) + " |")
    (OUTD / "sizes.md").write_text("\n".join(size_lines) + "\n")
    summ["size_totals"] = {s: {"compressed": tot[s][0], "decompressed": tot[s][1],
                               "records_scanned": tot[s][2], "records_manifest": tot[s][3]}
                           for s in SERIES}
    summ["record_size_bytes"] = {s: data[s][0]["manifest_delivered_record_bytes"]
                                 // data[s][0]["manifest_records"] for s in SERIES}
    summ["ndarray_itemsize"] = {s: data[s][0]["ndarray_itemsize"] for s in SERIES}
    summ["fields"] = {s: data[s][0]["ndarray_fields"] for s in SERIES}
    summ["metadata_versions"] = {s: sorted({f["metadata"]["version"] for f in data[s]}) for s in SERIES}
    summ["timings"] = {s: {"decode_wall_s": round(sum(f["decode_wall_s"] for f in data[s]), 1),
                           "decode_cpu_s": round(sum(f["decode_cpu_s"] for f in data[s]), 1),
                           "decompress_wall_s": round(sum(f["decompress_wall_s"] for f in data[s]), 1),
                           "file_wall_s": round(sum(f["file_wall_s"] for f in data[s]), 1),
                           "max_peak_rss_mb": max(f["peak_rss_mb_process_so_far"] for f in data[s])}
                       for s in SERIES}
    # ---- records series: anomalies, flags, actions, per-day ----
    for s in ("Z1", "Z2", "Z3"):
        c = defaultdict(int)
        fl = defaultdict(int)
        lat = defaultdict(int)
        act = defaultdict(int)
        act_side = defaultdict(int)
        days_reg, days_other = [], defaultdict(int)
        front_rows = []
        for f in data[s]:
            for k, v in f["counts"].items():
                c[k] += v
            for k, v in f["flags"].items():
                fl[k] += v
            for k, v in f["latency_hist_recv_minus_event_nonsnapshot"].items():
                lat[k] += v
            for k, v in f["action_side_counts"].items():
                act_side[k] += v
                act[k.split(":")[0]] += v
            for r in f["per_day"]:
                if r["regular_trade_date"] and r["in_file_month"]:
                    days_reg.append((r["day"], r["records"], r["events_F_LAST"], r["actions"]))
                else:
                    key = ("non_trade_date" if not r["regular_trade_date"] else "other_month")
                    days_other[key] += r["records"]
                    days_other[key + "_days"] += 1
        sym0 = {"Z1": "ZM.v.0", "Z2": "ZS.v.0", "Z3": "ZL.v.0"}[s]
        for f in data[s]:
            for iid, dd in f["per_day_instrument_counts"].items():
                for d, n in dd.items():
                    for a, b, i2 in maps.get(sym0, []):
                        if i2 == iid and a <= d < b:
                            front_rows.append((d, n))
        reg_days = {d for d, *_ in days_reg}
        front_rows = [r for r in front_rows if r[0] in reg_days]
        summ[s] = {"counts": dict(c), "flags": dict(fl), "latency_hist": dict(lat),
                   "actions": dict(act), "action_side": dict(act_side),
                   "days_regular": len(days_reg), "outside_regular": dict(days_other),
                   "records_on_regular_days": sum(r[1] for r in days_reg),
                   "stats_records": order_stats([(d, n) for d, n, *_ in days_reg]),
                   "stats_events": order_stats([(d, e) for d, _, e, _ in days_reg]),
                   "stats_front_records": order_stats(front_rows) if front_rows else None}
        if s == "Z1":
            summ[s]["per_day_rows"] = [(d, n, e) for d, n, e, _ in sorted(days_reg)]
            # cross-check with E.31's split markers (per trade date counts)
            diff, n_cmp, missing = 0, 0, 0
            ours = {d: n for d, n, *_ in days_reg}
            for mk in sorted((SPLIT / "Z1").glob("*.split.json")):
                j = json.loads(mk.read_text())
                for d, n in j.get("dates", {}).items():
                    if d in ours:
                        n_cmp += 1
                        diff += int(ours[d] != n)
                    else:
                        missing += 1
            summ[s]["split_marker_check"] = {"dates_compared": n_cmp, "dates_differing": diff,
                                             "marker_dates_not_in_scan": missing}
    (W / "F_agg_summary.json").write_text(json.dumps(summ, indent=1, default=str))
    for s in ("Z1", "Z2", "Z3"):
        print(s, "days", summ[s]["days_regular"], "rec", fmt(summ[s]["records_on_regular_days"]),
              "outside", summ[s]["outside_regular"])
    print("split check", summ["Z1"].get("split_marker_check"))
    print("totals ok", {s: summ["size_totals"][s]["records_scanned"] == summ["size_totals"][s]["records_manifest"] for s in SERIES})
    return 0


if __name__ == "__main__":
    sys.exit(main())
