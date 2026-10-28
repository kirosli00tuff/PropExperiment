"""B4 LT2 span check (protocol P4.1 LT2) on real label tables: for every kept row (row_ok) of every label type and
every built date, the span lies in [08:35, 13:13] on D, on one ZM front, clear of P3.6 (rules 1-5: open, close,
releases, P1.4 exclusions, the book in the span has both sides and is not bad, the limit band at t), and M_ZM(t) is
valid (P3.7). The span checked is the row's whole possible span (R-L10): [t, t + L + h] for FH, [t, t + 2L + h] for
TB (span_hi). Each implementation's rows are checked against the OTHER implementation's book replay (A's tables
against implB/labB_book.front_updates, B's against pipeline/lab33.replay) and against cal33's calendar, so no
check reuses the code it checks. The feature part: every feature row's t_ns is the decision time 08:35 + i min CT
on D (the cut-off; LT1 checks that nothing after it enters).

Counts only (INTERFACE rule 1): violations per rule, rows checked; no label value is read except row_ok, t_ns and
span_end_ns (span times). Output: JSON summary and a markdown block appended to the B4 report by the caller.

Usage: uv run python .../tests_b4/lt2_span.py --a-labels DIR --b-labels DIR [--features-a DIR] [--features-b DIR]
       [--dates b3] [--out JSON]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
IMPLB = PIPE.parent / "implB"
for _p in (str(PIPE), str(IMPLB), str(PIPE / "tests_b3")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cal33  # noqa: E402
import data33  # noqa: E402
import guard33 as g  # noqa: E402
import lab33  # noqa: E402
import labB_book  # noqa: E402
import compare_b3 as cb  # noqa: E402

NS = 1_000_000_000
MIN = 60 * NS
L = NS
H = {"F05": 5, "F15": 15, "F30": 30, "F60": 60, "T15": 15, "T30": 30}
RULES = ("grid_time", "open_0835", "close_1313", "span_nonempty", "fh_end_exact", "tb_end_range",
         "release_window", "excluded_date", "book_side_or_bad_in_span", "mid_invalid_at_t", "limit_band_at_t",
         "front_undefined")


def _bad_prefix(t: np.ndarray, ok: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return t, np.concatenate([[0], np.cumsum(~ok)])


def _any_bad(tpre: tuple[np.ndarray, np.ndarray], lo: int, hi: int) -> bool:
    t, cum = tpre
    a, b = np.searchsorted(t, lo, side="left"), np.searchsorted(t, hi, side="right")
    return bool(cum[b] - cum[a] > 0)


def _asof(t: np.ndarray, u: int) -> int:
    return int(np.searchsorted(t, u, side="right")) - 1


def books(d: str) -> dict:
    """Both implementations' books of D's ZM front (records with ts_recv < 13:20:00 CT)."""
    front = int(cal33.fronts(d)["ZM"])
    stop = cal33.ct_ns(d, "13:20:00")
    rec = data33.load_zm(d, cutoff_ns=stop - 1)
    tick = cal33.tick("ZM")
    ha = lab33.replay(rec, front, tick, end_ns=stop - 1)
    ub, _ = labB_book.front_updates(rec, front, tick)
    a_ok = (ha.bid != lab33.NO_PX) & (ha.ask != lab33.NO_PX) & ha.good
    b_ok = ub.has_bid & ub.has_ask & ~ub.bad
    return {
        "front": front,
        "A": {"pre": _bad_prefix(ha.t, a_ok), "t": ha.t, "bid": ha.bid, "ask": ha.ask, "ok": a_ok},
        "B": {"pre": _bad_prefix(ub.t, b_ok), "t": ub.t, "bid": ub.bid, "ask": ub.ask, "ok": b_ok},
    }


def span_hi(label: str, t: int, end: int) -> int:
    """End of the span a kept row is checked over. READING T-6 as ruled by R-L10 (lead E.33b, 2026-10-28 09:41):
    FH: the possible span [t, t + L + h]; TB: every span the label can have, [t, t + 2L + h] (tau <= t + L + h, so
    tau + L <= t + 2L + h), independent of the realised tau. max(., end) keeps a malformed realised end beyond it
    inside the checks (tb_end_range / fh_end_exact count it as well)."""
    h = H[label]
    poss = t + L + h * MIN if label.startswith("F") else t + 2 * L + h * MIN
    return max(poss, end)


def check_table(df: pd.DataFrame, label: str, d: str, bk: dict | None, book_side: str) -> dict[str, int]:
    v = {r: 0 for r in RULES}
    h = H[label]
    t0, close = cal33.ct_ns(d, "08:35:00"), cal33.ct_ns(d, "13:13:00")
    excl, _ = cal33.excluded(d)
    rel = [int(r) for r in cal33.releases(d)]
    lim = cal33.limits(d)
    tick = cal33.tick("ZM")
    rows = df[df["row_ok"]]
    for i, t, end in zip(rows["i"].tolist(), rows["t_ns"].tolist(), rows["span_end_ns"].tolist(), strict=True):
        poss = t + L + h * MIN  # FH end; the TB realised end lies in (t + L, poss + L]
        hi = span_hi(label, t, end)
        v["grid_time"] += int(t != t0 + i * MIN)
        v["open_0835"] += int(t < t0)
        v["close_1313"] += int(hi > close)
        v["span_nonempty"] += int(end <= t)
        if label.startswith("F"):
            v["fh_end_exact"] += int(end != poss)
        else:
            v["tb_end_range"] += int(not (t + L < end <= poss + L))
        v["release_window"] += int(any(t <= r + 30 * MIN and hi >= r - 2 * MIN for r in rel))
        v["excluded_date"] += int(bool(excl))
        if bk is None:
            v["front_undefined"] += 1
            continue
        b = bk[book_side]
        v["book_side_or_bad_in_span"] += int(_any_bad(b["pre"], t, hi))
        k = _asof(b["t"], t)
        mid_ok = k >= 0 and bool(b["ok"][k]) and int(b["bid"][k]) < int(b["ask"][k])
        v["mid_invalid_at_t"] += int(not mid_ok)
        if lim is not None and mid_ok:
            hl, ll = lim[0] // tick, lim[1] // tick
            s2 = int(b["bid"][k]) + int(b["ask"][k])  # 2 M in ticks; 2% band: M >= HL - 0.02 c, c = (HL+LL)/2
            v["limit_band_at_t"] += int(50 * s2 >= 99 * hl - ll or 50 * s2 <= 101 * ll + hl)
    return v


def run(a_root: Path | None, b_root: Path | None, dates: list[str], labels: list[str]) -> dict:
    out: dict = {"rows": {}, "violations": {}, "dates": dates, "fronts": {}}
    for d in dates:
        excl, _ = cal33.excluded(d)
        bk = None
        try:
            bk = None if excl else books(d)
        except Exception as exc:  # noqa: BLE001  a front or load failure is counted, never hidden
            out.setdefault("errors", []).append(f"{d}: {exc!r}")
        if bk is not None:
            out["fronts"][d] = bk["front"]
        for side_name, root, other in (("A", a_root, "B"), ("B", b_root, "A")):
            if root is None:
                continue
            for lab in labels:
                p = root / lab / f"{d}.parquet"
                if not p.exists():
                    continue
                df = pd.read_parquet(g.check_path(p), columns=["i", "t_ns", "row_ok", "span_end_ns"])
                key = f"{side_name} {lab}"
                out["rows"][key] = out["rows"].get(key, 0) + int(df["row_ok"].sum())
                v = check_table(df, lab, d, bk, other)
                agg = out["violations"].setdefault(key, {r: 0 for r in RULES})
                for r, n in v.items():
                    agg[r] += n
    return out


def feature_times(root: Path, dates: list[str]) -> dict:
    res = {"rows": 0, "bad_t_ns": 0, "dates": 0}
    for d in dates:
        p = root / f"{d}.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(g.check_path(p), columns=["date", "i", "t_ns"])
        t0 = cal33.ct_ns(d, "08:35:00")
        res["rows"] += len(df)
        res["dates"] += 1
        res["bad_t_ns"] += int(((df["t_ns"] != t0 + df["i"].astype(np.int64) * MIN) | (df["date"] != d)).sum())
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a-labels", default=None)
    ap.add_argument("--b-labels", default=None)
    ap.add_argument("--features-a", default=None)
    ap.add_argument("--features-b", default=None)
    ap.add_argument("--dates", default="b3")
    ap.add_argument("--labels", default=",".join(H))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    os.nice(10)
    t0 = time.time()
    dates = cb.b3_dates() if args.dates == "b3" else [x for x in args.dates.split(",") if x]
    labels = [x for x in args.labels.split(",") if x]
    res = run(Path(args.a_labels) if args.a_labels else None, Path(args.b_labels) if args.b_labels else None,
              dates, labels)
    for name, root in (("features_A", args.features_a), ("features_B", args.features_b)):
        if root:
            res[name] = feature_times(Path(root), dates)
    res["seconds"] = round(time.time() - t0, 1)
    Path(args.out).write_text(json.dumps(res, indent=1))
    tot = sum(sum(v.values()) for v in res["violations"].values())
    print(f"LT2 rows {sum(res['rows'].values())} violations {tot} errors {len(res.get('errors', []))} "
          f"seconds {res['seconds']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
