"""E.31 stats layer, markdown report: the verdict line first (with the spec 7 v2 "fragile" label),
then the three models side by side for the primary population, the five firms, all cells, the
model (a) block from 2023-11-01, the splits, the loop, implied liquidity, the exclusion counts of
days.parquet and the consistency checks. Input: the JSON-ready results of stats31.compute_all.
"""

from __future__ import annotations

from typing import Any

from stats31_core import FEE_PER_FILL_TICKS, FIRMS, HORIZONS_S, KM_POINTS_S, PRIMARY_FIRM

MODEL_NAMES = {"a": "(a) K", "b": "(b) FIFO back of queue", "c": "(c) trade-through (gate)"}
SIDES = ("pooled", "buy", "sell")
SPLIT_H = 10  # the column with an interval in the split tables (the gate's horizon)


def fmt(stat: dict[str, Any] | None, digits: int = 4) -> str:
    if stat is None or stat.get("value") is None:
        return "n/a"
    lo, hi = stat["ci95"]
    ci = "" if lo is None else f" [{lo:.{digits}f}, {hi:.{digits}f}]"
    tag = f" {stat['label']}" if stat.get("label") else ""
    return f"{stat['value']:.{digits}f}{ci}{tag}"


def num(x: float | None, digits: int = 4) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out.extend("| " + " | ".join(r) + " |" for r in rows)
    return [*out, ""]


# ------------------------------------------------------------------ cell rows ----
def _horizon_rows(cells: list[dict[str, Any]]) -> list[list[str]]:
    rows: list[list[str]] = []
    for h in map(str, HORIZONS_S):
        hb = [c["horizons"]["drop"][h] for c in cells]
        nd = [c["horizons"]["nodrop"][h] for c in cells]
        rows += [
            [f"{h} s: fills with E_h (dropped)", *[f"{x['n']} ({x['dropped']})" for x in hb]],
            [f"{h} s: mean markout (ticks)", *[fmt(x["markout_mean"]) for x in hb]],
            [f"{h} s: median markout", *[num(x["markout_median"]) for x in hb]],
            [f"{h} s: mean c_half on these fills", *[fmt(x["c_half_mean"]) for x in hb]],
            [f"{h} s: mean E_h", *[fmt(x["edge_mean"]) for x in hb]],
            [f"{h} s: median E_h", *[num(x["edge_median"]) for x in hb]],
            [f"{h} s: share E_h > 0", *[fmt(x["edge_share_positive"]) for x in hb]],
            [f"{h} s: mean N_h({PRIMARY_FIRM})",
             *[fmt(x["net"][PRIMARY_FIRM]["mean"]) for x in hb]],
            [f"{h} s: median N_h({PRIMARY_FIRM})",
             *[num(x["net"][PRIMARY_FIRM]["median"]) for x in hb]],
            [f"{h} s: VPO_h({PRIMARY_FIRM}) per resting order",
             *[fmt(x["net"][PRIMARY_FIRM]["vpo"]) for x in hb]],
            [f"{h} s no-drop: fills with E_h (dropped)",
             *[f"{x['n']} ({x['dropped']})" for x in nd]],
            [f"{h} s no-drop: mean E_h", *[fmt(x["edge_mean"]) for x in nd]],
            [f"{h} s no-drop: mean N_h({PRIMARY_FIRM})",
             *[fmt(x["net"][PRIMARY_FIRM]["mean"]) for x in nd]],
            [f"{h} s no-drop: VPO_h({PRIMARY_FIRM})",
             *[fmt(x["net"][PRIMARY_FIRM]["vpo"]) for x in nd]]]
    return rows


def cell_rows(cells: list[dict[str, Any]]) -> list[list[str]]:
    rows = [
        ["placements", *[str(c["placements"]) for c in cells]],
        ["fills (of which in the 50 ms cancel latency)",
         *[f"{c['fills']} ({c['fills_in_cancel_latency']})" for c in cells]],
        ["fills by trigger", *[", ".join(f"{k} {v}" for k, v in c["fills_by_trigger"].items())
                               for c in cells]],
        ["fill rate", *[fmt(c["fill_rate"]) for c in cells]],
        ["touch rate", *[fmt(c["touch_rate"]) for c in cells]],
        ["stale share (best price at g differs from j)", *[fmt(c["stale_share"]) for c in cells]]]
    for t in KM_POINTS_S:
        rows.append([f"KM P(fill by {t} s)", *[fmt(c["km"][f"p_fill_by_{t}s"]) for c in cells]])
    rows += [
        ["KM median time to fill (s)", *["not reached" if c["km"]["median_s"] is None
                                         else f"{c['km']['median_s']:.3f}" for c in cells]],
        ["KM censored before 60 s", *[str(c["km"]["censored_before_60s"]) for c in cells]],
        ["mean c_half, all fills (ticks)", *[fmt(c["c_half"]["mean"]) for c in cells]],
        ["median c_half, all fills", *[num(c["c_half"]["median"]) for c in cells]]]
    return rows + _horizon_rows(cells)


# ------------------------------------------------------------------ sections ----
def _title(res: dict[str, Any]) -> list[str]:
    m = res["meta"]
    exp = m.get("expected_dates") or {}
    return [
        "# Stage E.31 ZM pilot: statistics and kill rule", "",
        f"Generated {m['generated_pt']} by stats31.py from {m['runs_dir']}: {m['dates_done']} "
        f"trade dates with a done marker ({m['first_date']} to {m['last_date']}); expected "
        f"dates {exp.get('count', 'n/a')} (sha256 {str(exp.get('sha256', 'n/a'))[:16]}...); "
        f"folders without a marker: {len(m['folders_skipped_no_marker'])}. Inputs sha256 "
        f"{m['inputs_sha256'][:16]}... over {m['input_files']} files. Bootstrap: "
        f"{m['bootstrap']['replicates']} replicates, seed {m['bootstrap']['seed']}, unit "
        f"{m['bootstrap']['unit']} ({m['bootstrap']['pool']}). Intervals are 95% two-sided "
        "percentile intervals; labels: positive (lower bound > 0), negative (upper bound < 0), "
        "not distinguishable from 0. Units: ticks of 0.10 USD/short ton (10.00 USD).", ""]


def _verdict(res: dict[str, Any]) -> list[str]:
    kr = res["kill_rule"]
    k1, k3 = kr["K1"], kr["K3"]["interval"]
    yes = {True: "**holds**", False: "does not hold"}
    names = {"drop": "dropping markout", "nodrop": "no-drop markout"}
    rows = [[f"K1 ({names[v]})", "lower 95% bound of mean N_10(Topstep) = E_10 - 0.264",
             f"lower bound {num(k1[f'lower_{v}'])}; mean {fmt(k1[f'interval_{v}'])} over "
             f"{k1[f'interval_{v}']['n']} fills with a valid 10 s markout "
             f"({k1[f'interval_{v}']['dropped']} without)", "holds if not above 0",
             yes[k1[f"holds_{v}"]]] for v in ("drop", "nodrop")]
    rows += [
        ["K2", kr["K2"]["statistic"], str(kr["K2"]["value"]), kr["K2"]["rule"],
         yes[kr["K2"]["holds"]]],
        ["K3", kr["K3"]["statistic"], f"{num(kr['K3']['value'])}; interval {fmt(k3)} over "
         f"{kr['K3']['dates']} DAY trade dates", kr["K3"]["rule"], yes[kr["K3"]["holds"]]]]
    info = kr["information_only"]
    out = [f"## Verdict: {kr['verdict_line']}", "",
           f"Primary population (spec 7, v2): {kr['primary']['symbol']}, "
           f"{kr['primary']['session']} session, model ({kr['primary']['model']}), "
           f"{kr['primary']['sides']}, after all exclusions. ZM fails if any test holds; K1 holds "
           "if either variant's bound is not above 0. Nothing else decides.", "",
           *_table(["test", "statistic", "value", "rule", "result"], rows),
           "Information only (decides nothing; a PASS whose K1 would hold here is labelled "
           "\"PASS, fragile (fee reading)\"):", ""]
    for v in ("drop", "nodrop"):
        b = info[f"K1_bound_0.528_{v}"]
        out.append(f"- K1 ({names[v]}) with the full round-trip fee on every fill "
                   f"(E_10 - 0.528): lower bound {num(b['ci95'][0])}; mean {fmt(b)}.")
    out.append("")
    warn = _check_warnings(res["checks"])
    if warn:
        out += ["Consistency warnings (see the checks section):", "", *[f"- {w}" for w in warn],
                ""]
    return out


def _side_by_side(res: dict[str, Any]) -> list[str]:
    cells = [res["cells"][m]["ZM.v.0"]["DAY"]["pooled"] for m in MODEL_NAMES]
    return ["## Primary population, the three models side by side (ZM.v.0, DAY, sides pooled)",
            "", *_table(["statistic", *MODEL_NAMES.values()], cell_rows(cells))]


def _firms(res: dict[str, Any]) -> list[str]:
    cells = [res["cells"][m]["ZM.v.0"]["DAY"]["pooled"] for m in MODEL_NAMES]
    rows = []
    for h in map(str, HORIZONS_S):
        for firm in FIRMS:
            nets = [c["horizons"]["drop"][h]["net"][firm] for c in cells]
            rows.append([f"{h} s", f"{firm} ({FEE_PER_FILL_TICKS[firm]:.3f})",
                         *[f"{fmt(n['mean'])}; VPO {fmt(n['vpo'])}" for n in nets]])
    return ["## Net results for the five firms (ZM.v.0, DAY, sides pooled)", "",
            "Mean N_h(firm) = E_h - fee per fill over fills, and VPO_h = fill rate x mean N_h.", "",
            *_table(["h", "firm (fee per fill, ticks)", *MODEL_NAMES.values()], rows)]


def _all_cells(res: dict[str, Any]) -> list[str]:
    out = ["## All cells (model x symbol x session; pooled, buy, sell)", ""]
    for model, by_symbol in res["cells"].items():
        for symbol, by_session in by_symbol.items():
            for session, cell in by_session.items():
                out += [f"### {MODEL_NAMES[model]}, {symbol}, {session}", "",
                        *_table(["statistic", *SIDES], cell_rows([cell[s] for s in SIDES]))]
    return out


def _model_a_block(res: dict[str, Any]) -> list[str]:
    blk = res["model_a_from_2023_11_01"]
    out = [f"## Model (a), trade dates from {blk['first_date']} alone (spec 3.1; decides nothing)",
           "", f"{blk['dates']} trade dates; intervals resample {blk['bootstrap']['pool']}.", ""]
    if "cells" not in blk:
        return [*out, blk["note"], ""]
    for symbol, by_session in blk["cells"]["a"].items():
        for session, cell in by_session.items():
            out += [f"### {MODEL_NAMES['a']} from {blk['first_date']}, {symbol}, {session}", "",
                    *_table(["statistic", *SIDES], cell_rows([cell[s] for s in SIDES]))]
    lp = blk["loop"]["ZM.v.0"]["a"]
    out += [f"Loop (ZM.v.0, DAY, model (a)) from {blk['first_date']}: {lp['dates']} dates, mean "
            f"{fmt(lp['mean'], 3)} round trips per date, median {num(lp['median'], 1)}.", ""]
    return out


def _split_row(family: str, bucket: str, blk: dict[str, Any]) -> list[str]:
    hz = blk["horizons"]
    place = (f"{blk['placements']} ({fmt(blk['fill_rate'])})" if "placements" in blk else "-")
    hk = str(SPLIT_H)
    means = [hz[str(h)]["edge_mean"] for h in HORIZONS_S]
    return [family, bucket, place, str(blk["fills"]),
            *[fmt(m) if h == SPLIT_H else num(m["value"]) for h, m in zip(HORIZONS_S, means,
                                                                        strict=True)],
            num(hz[hk]["edge_median"]), fmt(hz[hk]["edge_share_positive"]),
            fmt(hz[hk]["net"][PRIMARY_FIRM]["mean"])]


def _splits(res: dict[str, Any]) -> list[str]:
    header = ["family", "bucket", "placements (fill rate)", "fills",
              *[f"mean E_{h}" for h in HORIZONS_S], f"median E_{SPLIT_H}",
              f"share E_{SPLIT_H} > 0", f"mean N_{SPLIT_H}({PRIMARY_FIRM})"]
    out = ["## Splits (spec 5; reported for every model, they decide nothing)", "",
           "ZS / ZL moves: sign of s x d, d = mid(t_f) - mid(t_f - L) in that contract's ticks; "
           "joint: both against, both with, other, missing if either mid is missing. USDA: signed "
           "minutes from the nearest release on the trade date (no release: other). These are "
           "fill-time conditions, so only statistics among fills are shown. Queue imbalance s x I "
           "at j is an entry-time quantity, so its buckets also show placements and fill rate. "
           "Headline (dropping) markouts; sides pooled. JSON: every firm and horizon.", ""]
    for model, by_symbol in res["splits"].items():
        for symbol, by_session in by_symbol.items():
            for session, fams in by_session.items():
                rows = [_split_row(fam, b, blk) for fam, buckets in fams.items()
                        for b, blk in buckets.items()]
                out += [f"### Splits: {MODEL_NAMES[model]}, {symbol}, {session}", "",
                        *_table(header, rows)]
    return out


def _loop(res: dict[str, Any]) -> list[str]:
    rows = []
    for symbol, by_model in res["loop"].items():
        for model, b in by_model.items():
            q = b["quantiles"]
            rows.append([symbol, MODEL_NAMES[model], str(b["dates"]), str(b["round_trips_total"]),
                         fmt(b["mean"], 3), num(b["median"], 1),
                         f"{num(b['min'], 0)} / {num(q['p10'], 1)} / {num(q['p25'], 1)} / "
                         f"{num(q['p75'], 1)} / {num(q['p90'], 1)} / {num(b['max'], 0)}",
                         ", ".join(f"{k}: {v}" for k, v in b["histogram"].items()),
                         num(b["mean_rt_s"], 2),
                         f"{b['entries_filled_total']} / {b['orders_placed_total']}"])
    return ["## Feasible round trips: the loop (spec 6; DAY session)", "",
            "Completed round trips per DAY trade date; no P&L of the loop is computed.", "",
            *_table(["symbol", "model", "dates", "round trips", "mean per date [CI]", "median",
                     "min / p10 / p25 / p75 / p90 / max", "dates by count", "mean RT duration (s)",
                     "entries filled / orders placed"], rows)]


def _implied(res: dict[str, Any]) -> list[str]:
    rows = []
    for symbol, by_session in res["implied"].items():
        for session, b in by_session.items():
            t = b["totals"]
            rows.append([symbol, session, str(b["dates"]), f"{t['n_ab']} / {t['vol_ab']}",
                         fmt(b["share_prints_no_resting"]), fmt(b["share_volume_no_resting"]),
                         fmt(b["share_prints_short"]), fmt(b["share_volume_short"]),
                         f"{t['n_n']} / {t['vol_n']}", fmt(b["share_prints_side_n_of_all"])])
    return ["## Implied-liquidity check (spec 8)", "",
            "Among trades with aggressor A or B: (i) no displayed resting quantity on the passive "
            "side at the price just before the trade; (ii) displayed resting quantity below the "
            "trade's size (as the engine's n_short / vol_short define it). Side N beside.", "",
            *_table(["symbol", "session", "dates", "A/B prints / volume", "(i) share of prints",
                     "(i) share of volume", "(ii) share of prints", "(ii) share of volume",
                     "side N prints / volume", "side N share of all prints"], rows)]


def _days(res: dict[str, Any]) -> list[str]:
    rows = []
    for symbol, b in res["days"].items():
        reasons = "; ".join(f"{k or '(blank)'}: {v}" for k, v in b["excluded_by_reason"].items())
        rows.append([symbol, str(b["dates"]), str(b["included"]), str(b["excluded"]),
                     reasons or "none", str(b["n_records"]), str(b["inversions"]),
                     str(b["bad_flag_records"]), str(b["crossed_moments"]),
                     f"{num(b['max_gap_day_s_max'], 1)} ({b['dates_gap_over_60s']} dates > 60 s)",
                     f"{b['placements_day']} / {b['placements_on']}",
                     ", ".join(b["instruments"])])
    return ["## Exclusions (days.parquet, spec 2)", "",
            *_table(["symbol", "dates", "included", "excluded", "excluded by reason", "records",
                     "ts_event inversions", "bad-book flag records", "crossed/locked/empty moments",
                     "max DAY gap (s)", "placements DAY / overnight", "instruments"], rows)]


def _check_warnings(checks: dict[str, Any]) -> list[str]:
    warn = []
    for key, value in checks.items():
        if isinstance(value, dict):
            bad = {k: v for k, v in value.items() if v}
            if bad:
                warn.append(f"{key}: {bad}")
        elif value:
            warn.append(f"{key}: {value}")
    return warn


def _checks(res: dict[str, Any]) -> list[str]:
    rows = [[k, str(v)] for k, v in res["checks"].items()]
    return ["## Consistency checks (each should be 0 or empty)", "",
            *_table(["check", "value"], rows)]


def render(res: dict[str, Any]) -> str:
    lines = [*_title(res), *_verdict(res), *_side_by_side(res), *_firms(res), *_all_cells(res),
             *_model_a_block(res), *_splits(res), *_loop(res), *_implied(res), *_days(res),
             *_checks(res)]
    return "\n".join(lines) + "\n"
