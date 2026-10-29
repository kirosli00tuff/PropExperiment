"""Full re-simulation of every configuration from fold<k>.npz (OOF probabilities, mu_k) and the
label store, per P3.5 (decision rule) and P3.8 (one position, 20-entry cap, next decision at the
first grid minute at or after the exit fill), with the readings S03 (a not-made entry is not
counted and the next minute decides) and S04 (first grid minute with t_ns >= exit_ns).

Writes, per configuration, derived/e33/verify_c/resim/<cid>.json (own daily series, counts,
reported-only P6.2 statistics, and the comparison with the pipeline's daily/trades/not_made
parquet files) and <cid>.trades.parquet. Prints counts only.

Usage: resim_all.py --shard k/n [--only CID ...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_common as vc  # noqa: E402

FLAG_ENTRY_FB, FLAG_EXIT_FB, FLAG_LIMIT, FLAG_LAST, FLAG_NM16, FLAG_NM32 = 1, 2, 4, 8, 16, 32


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_folds(cid: str) -> list[dict]:
    """The 6 npz files; rows sorted by (date, i); EVs from the fold's mu_k (classes -1, 0, +1)."""
    folds = []
    for k in range(1, vc.K_FOLDS + 1):
        z = np.load(vc.SEARCH / cid / f"fold{k}.npz", allow_pickle=False)
        m = json.load(open(vc.SEARCH / cid / f"fold{k}.model.json"))
        if tuple(m["classes"]) != vc.CLASSES:
            raise RuntimeError(f"{cid} fold {k}: classes {m['classes']}")
        if not (np.allclose(m["mu_long"], z["mu_long"], rtol=0, atol=0)
                and np.allclose(m["mu_short"], z["mu_short"], rtol=0, atol=0)):
            raise RuntimeError(f"{cid} fold {k}: mu in model.json differs from npz")
        dates, i, t_ns, p = z["date"], z["i"].astype(np.int64), z["t_ns"], z["p"]
        order = np.lexsort((i, dates))
        if not np.array_equal(order, np.arange(len(order))):
            dates, i, t_ns, p = dates[order], i[order], t_ns[order], p[order]
        if not np.all(np.isfinite(p)):
            raise RuntimeError(f"{cid} fold {k}: non-finite probabilities")
        mu_l, mu_s = z["mu_long"].astype(np.float64), z["mu_short"].astype(np.float64)
        ev_l = p[:, 0] * mu_l[0] + p[:, 1] * mu_l[1] + p[:, 2] * mu_l[2]
        ev_s = p[:, 0] * mu_s[0] + p[:, 1] * mu_s[1] + p[:, 2] * mu_s[2]
        folds.append({"k": k, "date": dates, "i": i, "t_ns": t_ns, "ev_l": ev_l, "ev_s": ev_s,
                      "mu_long": mu_l, "mu_short": mu_s})
    return folds


def decisions(ev_l: np.ndarray, ev_s: np.ndarray) -> np.ndarray:
    """P3.5: long if EV_long > max(EV_short, 0); short if EV_short > max(EV_long, 0); else 0."""
    dec = np.zeros(ev_l.shape[0], dtype=np.int8)
    dec[(ev_l > ev_s) & (ev_l > 0)] = 1
    dec[(ev_s > ev_l) & (ev_s > 0)] = -1
    return dec


def simulate_date(lab: dict, dec: np.ndarray, ev_l: np.ndarray, ev_s: np.ndarray):
    """P3.8 on one date. Returns (trades, not_made) as lists of tuples."""
    t_ns = lab["t_ns"]
    cand = np.flatnonzero(lab["entry_ok"] & (dec != 0))
    trades, not_made = [], []
    entries, next_t = 0, -1
    for idx in cand:
        if entries >= vc.ENTRY_CAP:
            break
        if t_ns[idx] < next_t:
            continue
        side = int(dec[idx])
        pre = "long_" if side > 0 else "short_"
        made = bool(lab[pre + "made"][idx])
        flags = int(lab[pre + "flags"][idx])
        if made:
            net = float(lab[pre + "net"][idx])
            en, ex = int(lab[pre + "entry_ns"][idx]), int(lab[pre + "exit_ns"][idx])
            if not math.isfinite(net) or en < 0 or ex < en:
                raise RuntimeError(f"made trade with bad fields at i={idx}")
            trades.append((int(idx), side, net, en, ex, flags, float(ev_l[idx]), float(ev_s[idx])))
            entries += 1
            next_t = ex
        else:
            not_made.append((int(idx), side, flags, float(ev_l[idx]), float(ev_s[idx])))
    return trades, not_made


def pearson(x: np.ndarray, y: np.ndarray) -> float | None:
    if x.size < 2:
        return None
    xm, ym = x - x.mean(), y - y.mean()
    den = math.sqrt(float((xm * xm).sum()) * float((ym * ym).sum()))
    if den == 0:
        return None
    return float((xm * ym).sum() / den)


def reported_only(rows: dict, trades_arr: dict) -> dict:
    """P6.2 reported-only statistics (S07, S08 readings)."""
    ev_l, ev_s, n_l, n_s = rows["ev_l"], rows["ev_s"], rows["n_long"], rows["n_short"]
    side = np.where(ev_l > ev_s, 1, np.where(ev_s > ev_l, -1, 0))
    keep = side != 0
    ev_c = np.where(side > 0, ev_l, ev_s)[keep]
    net_c = np.where(side > 0, n_l, n_s)[keep]
    maxev = np.maximum(ev_l, ev_s)[keep]
    d_k, i_k = rows["date"][keep], rows["i"][keep]
    n = int(keep.sum())
    out = {"n_rows": int(ev_l.size), "n_rows_with_side": n, "n_rows_tied": int((~keep).sum()),
           "rho_chosen_ev_net_rows": pearson(ev_c, net_c)}
    top_n = math.ceil(n / 10)
    order = np.lexsort((i_k, d_k, -maxev))  # primary: -maxev; then date; then i
    top = order[:top_n]
    out["top_decile_n"] = int(top_n)
    out["top_decile_mean_net"] = float(net_c[top].mean()) if top_n else None
    # trades taken
    tev_l, tev_s, tside, tnet, tmm = (trades_arr[k] for k in ("ev_l", "ev_s", "side", "net", "mid_move"))
    tev_c = np.where(tside > 0, tev_l, tev_s)
    out["rho_chosen_ev_net_trades"] = pearson(tev_c, tnet) if tnet.size else None
    nan = np.isnan(tmm)
    zero = (~nan) & (tmm == 0)
    used = (~nan) & (~zero)
    hits = int(((np.sign(tmm[used]) == tside[used])).sum())
    out["mid_sign"] = {"n_trades": int(tnet.size), "n_used": int(used.sum()), "n_nan": int(nan.sum()),
                       "n_zero": int(zero.sum()), "hits": hits}
    out["mid_sign_hit_rate"] = hits / int(used.sum()) if used.sum() else None
    return out


def compare_with_pipeline(cid: str, dates: list[str], x_d: np.ndarray, n_tr: np.ndarray,
                          trades: list[tuple], not_made: list[tuple]) -> dict:
    root = vc.SEARCH / cid
    cmp = {}
    dly = pq.read_table(root / "daily.parquet").to_pandas()
    cmp["daily_rows"] = int(len(dly))
    cmp["daily_dates_equal"] = list(dly["date"]) == dates
    pX = dly["X_D"].to_numpy(dtype=np.float64)
    pn = dly["n_trades"].to_numpy(dtype=np.int64)
    bad_x = [dates[j] for j in range(len(dates)) if not vc.rel_equal(x_d[j], pX[j])]
    bad_n = [dates[j] for j in range(len(dates)) if n_tr[j] != pn[j]]
    cmp["daily_X_D_mismatch_dates"] = bad_x[:20]
    cmp["daily_X_D_mismatch_count"] = len(bad_x)
    cmp["daily_n_trades_mismatch_count"] = len(bad_n)
    cmp["daily_n_trades_mismatch_dates"] = bad_n[:20]
    cmp["pipeline_trade_total"] = int(pn.sum())
    # trades
    pt = pq.read_table(root / "trades.parquet").to_pandas()
    cmp["pipeline_trades_rows"] = int(len(pt))
    own = {(d, i, s): (net, en, ex, fl, el, es) for (d, i, s, net, en, ex, fl, el, es) in trades}
    pipe = {}
    for r in pt.itertuples(index=False):
        pipe[(str(r.date), int(r.i), int(r.side))] = (float(r.net), int(r.entry_ns), int(r.exit_ns),
                                                      int(r.flags), float(r.ev_long), float(r.ev_short))
    only_own = sorted(set(own) - set(pipe))
    only_pipe = sorted(set(pipe) - set(own))
    field_bad = []
    for k in sorted(set(own) & set(pipe)):
        a, b = own[k], pipe[k]
        ok = (vc.rel_equal(a[0], b[0]) and a[1] == b[1] and a[2] == b[2] and a[3] == b[3]
              and vc.rel_equal(a[4], b[4]) and vc.rel_equal(a[5], b[5]))
        if not ok:
            field_bad.append([k[0], k[1], k[2], list(a), list(b)])
    cmp["trades_only_own"] = [list(k) for k in only_own[:20]]
    cmp["trades_only_own_count"] = len(only_own)
    cmp["trades_only_pipeline"] = [list(k) for k in only_pipe[:20]]
    cmp["trades_only_pipeline_count"] = len(only_pipe)
    cmp["trades_field_mismatch"] = field_bad[:20]
    cmp["trades_field_mismatch_count"] = len(field_bad)
    cmp["trades_sides_pipeline"] = sorted(set(int(s) for s in pt["side"])) if len(pt) else []
    # not made
    pnm = pq.read_table(root / "not_made.parquet").to_pandas()
    own_nm = {(d, i, s): (fl, el, es) for (d, i, s, fl, el, es) in not_made}
    pipe_nm = {}
    for r in pnm.itertuples(index=False):
        pipe_nm[(str(r.date), int(r.i), int(r.side))] = (int(r.flags), float(r.ev_long), float(r.ev_short))
    nm_only_own = sorted(set(own_nm) - set(pipe_nm))
    nm_only_pipe = sorted(set(pipe_nm) - set(own_nm))
    nm_bad = [list(k) for k in sorted(set(own_nm) & set(pipe_nm))
              if not (own_nm[k][0] == pipe_nm[k][0] and vc.rel_equal(own_nm[k][1], pipe_nm[k][1])
                      and vc.rel_equal(own_nm[k][2], pipe_nm[k][2]))]
    cmp["not_made_pipeline_rows"] = int(len(pnm))
    cmp["not_made_only_own_count"] = len(nm_only_own)
    cmp["not_made_only_pipeline_count"] = len(nm_only_pipe)
    cmp["not_made_field_mismatch_count"] = len(nm_bad)
    cmp["not_made_mismatch_examples"] = ([list(k) for k in nm_only_own[:5]]
                                        + [list(k) for k in nm_only_pipe[:5]] + nm_bad[:5])
    # DONE marker hashes
    done = json.load(open(root / "DONE"))
    cmp["done_status"] = done.get("status")
    cmp["done_sha_ok"] = {
        "daily": sha256_file(root / "daily.parquet") == done.get("daily_sha256"),
        "trades": sha256_file(root / "trades.parquet") == done.get("trades_sha256"),
        "not_made": sha256_file(root / "not_made.parquet") == done.get("not_made_sha256"),
        "stats": sha256_file(root / "stats.json") == done.get("stats_sha256"),
    }
    fold_sha_ok = []
    for k in range(1, vc.K_FOLDS + 1):
        fd = json.load(open(root / f"fold{k}.DONE"))
        fold_sha_ok.append(sha256_file(root / f"fold{k}.npz") == fd.get("npz_sha256")
                           and sha256_file(root / f"fold{k}.model.json") == fd.get("model_sha256"))
    cmp["fold_sha_ok"] = fold_sha_ok
    cmp["all_equal"] = (cmp["daily_dates_equal"] and not bad_x and not bad_n and not only_own
                        and not only_pipe and not field_bad and not nm_only_own and not nm_only_pipe
                        and not nm_bad)
    return cmp


def run_config(cid: str, dates: list[str], labels: dict, folds_cache: dict) -> dict:
    t0 = time.time()
    info = vc.parse_config(cid)
    lab_tab = labels[info["label"]]
    folds = load_folds(cid)
    # per-date view of the predictions, with grid checks
    per_date = {}
    fold_of_date = {}
    for f in folds:
        u, start = np.unique(f["date"], return_index=True)
        ends = list(start[1:]) + [len(f["date"])]
        for ds, a, b in zip(u, start, ends):
            ds = str(ds)
            vc.check_in_span(ds)
            if ds in per_date:
                raise RuntimeError(f"{cid}: date {ds} in two folds")
            lab = lab_tab[ds]
            if not (np.array_equal(f["i"][a:b], lab["i"].astype(np.int64))
                    and np.array_equal(f["t_ns"][a:b], lab["t_ns"])):
                raise RuntimeError(f"{cid} fold {f['k']} {ds}: grid differs from the label table")
            per_date[ds] = (f["ev_l"][a:b], f["ev_s"][a:b])
            fold_of_date[ds] = f["k"]
    if set(per_date) != set(dates):
        raise RuntimeError(f"{cid}: prediction dates differ from the 796 OOF dates")
    x_d = np.zeros(len(dates))
    n_tr = np.zeros(len(dates), dtype=np.int64)
    trades, not_made = [], []
    row_parts = {"ev_l": [], "ev_s": [], "n_long": [], "n_short": [], "date": [], "i": []}
    tr_parts = {"ev_l": [], "ev_s": [], "side": [], "net": [], "mid_move": []}
    counts = {"entries_not_made": 0, "entry_fallback_fills": 0, "exit_fallback_fills": 0,
              "exit_limit_marks": 0, "exit_last_touch_marks": 0, "not_made_flag16": 0, "not_made_flag32": 0}
    for j, ds in enumerate(dates):
        ev_l, ev_s = per_date[ds]
        lab = lab_tab[ds]
        dec = decisions(ev_l, ev_s)
        tr, nm = simulate_date(lab, dec, ev_l, ev_s)
        x_d[j] = math.fsum(t[2] for t in tr)
        n_tr[j] = len(tr)
        for t in tr:
            trades.append((ds, *t))
            fl = t[5]
            counts["entry_fallback_fills"] += bool(fl & FLAG_ENTRY_FB)
            counts["exit_fallback_fills"] += bool(fl & FLAG_EXIT_FB)
            counts["exit_limit_marks"] += bool(fl & FLAG_LIMIT)
            counts["exit_last_touch_marks"] += bool(fl & FLAG_LAST)
            tr_parts["ev_l"].append(t[6]); tr_parts["ev_s"].append(t[7]); tr_parts["side"].append(t[1])
            tr_parts["net"].append(t[2]); tr_parts["mid_move"].append(float(lab["mid_move"][t[0]]))
        for t in nm:
            not_made.append((ds, *t))
            counts["entries_not_made"] += 1
            counts["not_made_flag16"] += bool(t[2] & FLAG_NM16)
            counts["not_made_flag32"] += bool(t[2] & FLAG_NM32)
        rk = lab["row_ok"]
        row_parts["ev_l"].append(ev_l[rk]); row_parts["ev_s"].append(ev_s[rk])
        row_parts["n_long"].append(lab["n_long"][rk]); row_parts["n_short"].append(lab["n_short"][rk])
        row_parts["date"].append(np.full(int(rk.sum()), j, dtype=np.int64))
        row_parts["i"].append(lab["i"][rk].astype(np.int64))
    rows = {k: np.concatenate(v) for k, v in row_parts.items()}
    tr_arr = {k: np.asarray(v, dtype=np.float64 if k != "side" else np.int64) for k, v in tr_parts.items()}
    rep = reported_only(rows, tr_arr)
    cmp = compare_with_pipeline(cid, dates, x_d, n_tr, trades, not_made)
    # own outputs
    out_dir = vc.OUT / "resim"
    out_dir.mkdir(parents=True, exist_ok=True)
    tbl = pa.table({
        "date": pa.array([t[0] for t in trades], pa.string()),
        "i": pa.array([t[1] for t in trades], pa.int16()),
        "side": pa.array([t[2] for t in trades], pa.int8()),
        "net": pa.array([t[3] for t in trades], pa.float64()),
        "entry_ns": pa.array([t[4] for t in trades], pa.int64()),
        "exit_ns": pa.array([t[5] for t in trades], pa.int64()),
        "flags": pa.array([t[6] for t in trades], pa.int16()),
        "ev_long": pa.array([t[7] for t in trades], pa.float64()),
        "ev_short": pa.array([t[8] for t in trades], pa.float64()),
    })
    pq.write_table(tbl, out_dir / f"{cid}.trades.parquet")
    res = {"config": cid, **info, "n_trades": int(n_tr.sum()), "n_not_made": len(not_made),
           "dates": dates, "X_D": x_d.tolist(), "n_trades_per_date": n_tr.tolist(),
           "fold_of_date": [fold_of_date[d] for d in dates], "counts": counts,
           "mu_long_by_fold": [f["mu_long"].tolist() for f in folds],
           "mu_short_by_fold": [f["mu_short"].tolist() for f in folds],
           "reported_only": rep, "compare": cmp, "seconds": time.time() - t0}
    vc.write_json(out_dir / f"{cid}.json", res)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()
    k, n = (int(x) for x in a.shard.split("/"))
    ids = a.only or vc.all_config_ids()
    ids = [c for j, c in enumerate(ids) if j % n == k]
    dates = vc.oof_dates()
    needed = sorted({vc.parse_config(c)["label"] for c in ids})
    t0 = time.time()
    labels = {lab: vc.load_label_table(lab, dates) for lab in needed}
    vc.log(f"shard {k}/{n}: {len(ids)} configs; labels loaded {needed} in {time.time() - t0:.1f}s")
    n_ok = n_diff = 0
    for j, cid in enumerate(ids):
        out = vc.OUT / "resim" / f"{cid}.json"
        if out.exists():
            res = json.load(open(out))
        else:
            res = run_config(cid, dates, labels, {})
        eq = res["compare"]["all_equal"]
        n_ok += eq
        n_diff += (not eq)
        vc.log(f"[{j + 1}/{len(ids)}] {cid} trades {res['n_trades']} not_made {res['n_not_made']} "
               f"equal={eq} {res['seconds']:.1f}s")
    vc.log(f"shard {k}/{n} done: equal {n_ok}, differ {n_diff}, {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
