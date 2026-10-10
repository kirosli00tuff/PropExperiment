"""Independent check of H2's signal for every traded month: d5 and dL from the joint trade dates
(NQ store AND ZN store), PS(X, d) = close of bar(d, S_X - 1), MTD_X chained across a contract
splice (old segment to the close of the last old-contract bar, new segment from the open of the
first new-contract bar), direction: MTD_NQ > MTD_ZN -> short NQ, long ZN; else the reverse.
Compares d5, dL, each leg's mtd field and direction with the units rows. Prints counts only."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo

import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from vv_common import OUT, REPO, iter_units, write_json  # noqa: E402

CT = ZoneInfo("America/Chicago")
HIST_LAST = "2019-04-30"


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def settle_minutes() -> dict:
    with open(REPO / "reports/stage_e16_settlement.json", encoding="utf-8") as handle:
        prods = json.load(handle)["products"]

    def lookup(root: str, day: str) -> int:
        for p in prods[root]["settle"]:
            if p["from"] <= day <= p["to"]:
                h, m = p["minute_ct"].split(":")
                return int(h) * 60 + int(m)
        raise KeyError((root, day))
    return lookup


def load_store(path: str, expected: str) -> pd.DataFrame:
    full = REPO / path
    if sha256(full) != expected:
        raise RuntimeError(f"{path}: sha256 differs from the manifest")
    df = pq.read_table(full, columns=["ts_event", "open", "close", "raw_symbol", "trade_date",
                                      "in_scheduled_closure"]).to_pandas()
    local = pd.to_datetime(df["ts_event"], utc=True).dt.tz_convert(CT)
    df["minute"] = (local.dt.hour * 60 + local.dt.minute).astype(int)
    return df.sort_values("ts_event").reset_index(drop=True)


def ps_row(df: pd.DataFrame, day: str, s_minute: int):
    rows = df[(df["trade_date"] == day) & (df["minute"] == s_minute - 1) & (~df["in_scheduled_closure"])]
    return None if rows.empty else rows.iloc[0]


def chained_return(df: pd.DataFrame, a, b) -> float:
    """PS a -> PS b, the product of same-contract segment returns split at each splice."""
    seg = df[(df["ts_event"] > a["ts_event"]) & (df["ts_event"] <= b["ts_event"])]
    ret, last_price = 1.0, float(a["close"])
    symbol = a["raw_symbol"]
    for _, bar in seg[seg["raw_symbol"] != symbol].head(1).iterrows():
        pass
    changes = seg.index[seg["raw_symbol"].values != symbol]
    while len(changes):
        i = changes[0]
        before = df.loc[i - 1]
        ret *= float(before["close"]) / last_price
        after = df.loc[i]
        last_price, symbol = float(after["open"]), after["raw_symbol"]
        rest = seg.loc[i:]
        changes = rest.index[rest["raw_symbol"].values != symbol]
    ret *= float(b["close"]) / last_price
    return ret - 1.0


def main() -> None:
    with open(REPO / "reports/stage_e17_run_manifest.json", encoding="utf-8") as handle:
        manifest = json.load(handle)["stores"]
    s_of = settle_minutes()
    units = defaultdict(dict)
    for row in iter_units("H2"):
        units[row["date"]][row["key"]] = row
    out = {"months": len(units), "mismatches": [], "checked": 0, "splices_chained": 0}
    for era in ("hist", "step2"):
        months = {d: legs for d, legs in units.items() if (d <= HIST_LAST) == (era == "hist")}
        if not months:
            continue
        key = "ext2010" if era == "hist" else "step2"
        nq = load_store(manifest["NQ"][key]["path"], manifest["NQ"][key]["sha256"])
        zn = load_store(manifest["ZN"][key]["path"], manifest["ZN"][key]["sha256"])
        joint = sorted(set(nq["trade_date"]) & set(zn["trade_date"]))
        by_month = defaultdict(list)
        for d in joint:
            by_month[d[:7]].append(d)
        for dL, legs in sorted(months.items()):
            month = dL[:7]
            days = by_month[month]
            prior = by_month.get(f"{int(month[:4]) - 1}-12" if month[5:] == "01"
                                 else f"{month[:4]}-{int(month[5:]) - 1:02d}", [])
            rec = {"month": month}
            if len(days) < 5 or not prior:
                rec["note"] = "calendar incomplete in the stores"
                out["mismatches"].append(rec)
                continue
            d5, prior_end = days[-5], prior[-1]
            if d5 != legs["NQ"]["d5"] or dL != days[-1]:
                rec["d5_dL"] = f"mine {d5}/{days[-1]} theirs {legs['NQ']['d5']}/{dL}"
            mtd = {}
            for root, df in (("NQ", nq), ("ZN", zn)):
                a = ps_row(df, prior_end, s_of(root, prior_end))
                b = ps_row(df, d5, s_of(root, d5))
                if a is None or b is None:
                    rec[f"{root}_ps_missing"] = True
                    continue
                if a["raw_symbol"] != b["raw_symbol"]:
                    out["splices_chained"] += 1
                mtd[root] = chained_return(df, a, b)
                theirs = float(legs[root]["mtd"])
                if abs(mtd[root] - theirs) > 1e-9:
                    rec[f"{root}_mtd"] = f"differs by {mtd[root] - theirs:.3e}"
            if len(mtd) == 2:
                nq_dir = -1 if mtd["NQ"] > mtd["ZN"] else 1
                if int(legs["NQ"]["direction"]) != nq_dir or int(legs["ZN"]["direction"]) != -nq_dir:
                    rec["direction"] = "differs"
            out["checked"] += 1
            if len(rec) > 1:
                out["mismatches"].append(rec)
        del nq, zn
    out["months_with_mismatch"] = len(out["mismatches"])
    write_json(OUT / "h2_signal_check.json", out)
    print({k: v for k, v in out.items() if k != "mismatches"})
    for rec in out["mismatches"][:20]:
        print("  ", rec)


if __name__ == "__main__":
    main()
