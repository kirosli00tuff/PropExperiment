"""K3 re-derivation: the section 6 sequential loop under model (c), from raw Z1 records (own engine_check functions)."""
import sys as _s, pathlib as _p; _s.path.insert(0, str(_p.Path(__file__).resolve().parent))
import bisect, json, sys
from datetime import date, datetime, time
import numpy as np, pandas as pd
from engine_check import replay, valid_state, HERE, MEAS, LATENCY_NS, CANCEL_NS, CHI, UTC

def ct_ns(T, hh, mm):
    d = date.fromisoformat(T)
    return int(datetime.combine(d, time(hh, mm), tzinfo=CHI).astimezone(UTC).timestamp()) * 1_000_000_000

def first_through(TR, p, s, lo_t, hi_t):
    lo = bisect.bisect_right(TR["t"], lo_t); hi = bisect.bisect_right(TR["t"], hi_t)
    for q in range(lo, hi):
        if TR["s"][q] in ("A", "B") and ((TR["p"][q] < p) if s == 1 else (TR["p"][q] > p)):
            return int(TR["t"][q])
    return None

def run(T, H, TR, repl_extra_ns, stop_on="decision"):
    t_start = ct_ns(T, 8, 35); t_stop = ct_ns(T, 13, 15)
    d = t_start; entry_side = 1; leg = "entry"; rts = 0; entries = 0; orders = 0; invalid_join = 0
    rt_durs = []; t_entry_decided = None
    while True:
        if (d >= t_stop) if stop_on == "decision" else (d + LATENCY_NS >= t_stop): break
        j = d + LATENCY_NS
        k = bisect.bisect_right(H["t"], j) - 1
        if not valid_state(H, k):
            invalid_join += 1
            d = j + 1_000_000_000; continue   # not specified by the spec; counted
        s = entry_side if leg == "entry" else -entry_side
        p = int(H["bid"][k]) if s == 1 else int(H["ask"][k])
        orders += 1
        if leg == "entry" and t_entry_decided is None: t_entry_decided = d
        tf = first_through(TR, p, s, j, j + CANCEL_NS + LATENCY_NS)
        if tf is None:
            d = j + CANCEL_NS + repl_extra_ns; continue
        if leg == "entry":
            entries += 1; leg = "exit"; d = tf
        else:
            rts += 1; rt_durs.append((tf - t_entry_decided) / 1e9); t_entry_decided = None
            leg = "entry"; entry_side = -entry_side; d = tf
    return dict(round_trips=rts, entries_filled=entries, orders_placed=orders, mean_rt_s=float(np.mean(rt_durs)) if rt_durs else np.nan, invalid_join=invalid_join)

def main(dates):
    res = {}
    for T in dates:
        X = pd.read_parquet(HERE / "raw_extract" / f"{T}.parquet")
        H, TR, anom, n_inv, start = replay(X, T)
        L = pd.read_parquet(MEAS / T / "loop.parquet"); L = L[(L.symbol == "ZM.v.0") & (L.model == "c")].iloc[0]
        prod = dict(round_trips=int(L.round_trips), entries_filled=int(L.entries_filled), orders_placed=int(L.orders_placed), mean_rt_s=float(L.mean_rt_s))
        res[T] = {"prod": prod}
        for name, extra, stop in (("A_repl_at_cancel_decision", 0, "decision"), ("B_repl_at_cancel_effective", LATENCY_NS, "decision"),
                                  ("C_repl_at_cancel_decision_stop_on_join", 0, "join"), ("D_repl_at_cancel_effective_stop_on_join", LATENCY_NS, "join")):
            res[T][name] = run(T, H, TR, extra, stop)
        print(T, "prod", prod)
        for name in list(res[T])[1:]:
            print("   ", name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[T][name].items()})
    (HERE / "loop_check.json").write_text(json.dumps(res, indent=1, default=str))

if __name__ == "__main__":
    main(sys.argv[1:] or list(json.load(open(HERE / "picked_dates.json")).values()) + list(json.load(open(HERE / "picked_extra.json")).values()))
