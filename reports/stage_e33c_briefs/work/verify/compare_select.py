"""Compare the own numbers (derived/e33/verify_c/gates_own.json, gates_parquet.json, resim/*.json)
with (1) the pipeline's selection output P8_select33.json, (2) the engine's per-configuration
stats.json, and (3) the StatsCoder's D_stats.json. Tolerance 1e-9 relative, 1e-12 absolute for
floats; integers, flags and memberships exact. Writes derived/e33/verify_c/compare.json and
three_dates.json; prints counts only.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_common as vc  # noqa: E402

SELECT = vc.REPO / "reports" / "stage_e33c_briefs" / "select" / "P8_select33.json"
DSTATS = vc.WORK / "D_stats.json"


class Cmp:
    def __init__(self, name: str):
        self.name, self.n_agree, self.diffs = name, 0, []

    def check(self, where: str, field: str, own, other) -> None:
        if isinstance(own, (list, tuple)) and isinstance(other, (list, tuple)):
            if len(own) != len(other):
                self.diffs.append({"where": where, "field": field, "own": own, "other": other})
                return
            for j, (a, b) in enumerate(zip(own, other)):
                self.check(where, f"{field}[{j}]", a, b)
            return
        ok = (own == other) if (isinstance(own, (bool, str, int)) and not isinstance(own, float)
                                and isinstance(other, (bool, str, int))) else vc.rel_equal(own, other)
        if ok:
            self.n_agree += 1
        else:
            self.diffs.append({"where": where, "field": field, "own": own, "other": other})

    def summary(self) -> dict:
        by_field = Counter(d["field"].split("[")[0] for d in self.diffs)
        return {"n_agree": self.n_agree, "n_differ": len(self.diffs), "differ_by_field": dict(by_field),
                "examples": self.diffs[:40]}


def quarter_counts(dates: list[str]) -> dict[str, int]:
    c = Counter(vc.quarter_key(d) for d in dates)
    return dict(c)


def main() -> int:
    dates = vc.oof_dates()
    own = json.load(open(vc.OUT / "gates_own.json"))
    own_pq = json.load(open(vc.OUT / "gates_parquet.json"))
    S, G, SUM = own["stats"], own["gates"], own["summary"]
    ids = vc.all_config_ids()
    qn = quarter_counts(dates)
    report = {}

    # 0. own-vs-own: the series from the re-simulation and from the pipeline's parquet give the same numbers
    c0 = Cmp("own_resim_vs_own_parquet")
    for cid in ids:
        for f in ("trade_count", "dates_with_trade", "mean_net_per_trade", "hit_rate", "total_net"):
            c0.check(cid, f, S[cid][f], own_pq["stats"][cid][f])
        for f in ("mean", "sd", "skew", "kurtosis", "sharpe"):
            c0.check(cid, "moments." + f, S[cid]["moments"][f], own_pq["stats"][cid]["moments"][f])
        for f in ("G1", "G2", "G3", "G4", "G5", "pass_all"):
            c0.check(cid, f, G[cid][f], own_pq["gates"][cid][f])
    c0.check("summary", "funnel_alone", list(SUM["funnel_alone"].values()), list(own_pq["summary"]["funnel_alone"].values()))
    c0.check("summary", "ranking", SUM["ranking"], own_pq["summary"]["ranking"])
    report[c0.name] = c0.summary()

    # 1. versus the pipeline's selection output
    P = json.load(open(SELECT))
    c1 = Cmp("own_vs_P8_select33")
    bt = SUM["b_test_values"]
    c1.check("top", "b_test (own: program-function bisection)", bt["b_test_program"], P["b_test"])
    c1.check("top", "n_trials", vc.N_TRIALS, P["n_trials"])
    c1.check("top", "t_disc", vc.T_DISC, P["t_disc"])
    for k in ("G1", "G2", "G3", "G4", "G5"):
        c1.check("funnel", f"alone.{k}", SUM["funnel_alone"][k], P["funnel"]["alone"][k])
    for k in ("G1", "G1..G2", "G1..G3", "G1..G4", "G1..G5"):
        c1.check("funnel", f"in_order.{k}", SUM["funnel_in_order"][k], P["funnel"]["in_order"][k])
    c1.check("funnel", "failed_configs", 0, P["funnel"]["failed_configs"])
    c1.check("funnel", "n_configs", 300, P["funnel"]["n_configs"])
    c1.check("top", "best_config", SUM["ranking"][0], P["best_config"])
    c1.check("top", "best_sharpe", S[SUM["ranking"][0]]["moments"]["sharpe"], P["best_sharpe"])
    c1.check("top", "ranking_all", SUM["ranking"], P["ranking_all"])
    c1.check("top", "ranking_pass", SUM["passers"], P["ranking_pass"])
    c1.check("top", "tier_a", SUM["tier_a"], P["tier_a"])
    c1.check("top", "tier_b", SUM["tier_b"], P["tier_b"])
    c1.check("top", "tier_b_detail.continue.tier_b", SUM["tier_b"], P["tier_b_detail"]["continue"]["tier_b"])
    c1.check("top", "tier_b_detail.continue.start_position", 0, P["tier_b_detail"]["continue"]["start_position"])
    pc = {r["config"]: r for r in P["configs"]}
    c1.check("top", "configs_count", 300, len(pc))
    for cid in ids:
        s, g, p = S[cid], G[cid], pc[cid]
        c1.check(cid, "constant", s["constant_series"], p["constant"])
        c1.check(cid, "defined", True, p["defined"])
        c1.check(cid, "failed", False, p["failed"])
        for f in ("set", "label", "grid", "family", "h"):
            c1.check(cid, f, s[f], p[f])
        c1.check(cid, "trade_count", s["trade_count"], p["trade_count"])
        c1.check(cid, "dates_with_trade", s["dates_with_trade"], p["dates_with_trade"])
        c1.check(cid, "trades_per_date", s["trades_per_date"], p["trades_per_date"])
        c1.check(cid, "share_dates_with_trade", s["share_dates_with_trade"], p["share_dates_with_trade"])
        c1.check(cid, "mean_net_per_trade", s["mean_net_per_trade"], p["mean_net_per_trade"])
        c1.check(cid, "total_net", s["total_net"], p["total_net"])
        for f in ("n", "mean", "sd", "skew", "kurtosis", "sharpe"):
            c1.check(cid, "moments." + f, s["moments"][f], p["moments"][f])
        c1.check(cid, "sharpe", s["moments"]["sharpe"], p["sharpe"])
        c1.check(cid, "t", s["t_stat"], p["t"])
        c1.check(cid, "dsr (program function)", g["dsr_program"]["dsr"], p["dsr"])
        c1.check(cid, "dsr (own formula)", g["dsr_own"]["dsr"], p["dsr"])
        c1.check(cid, "se", g["se_sharpe"], p["se"])
        c1.check(cid, "sr_lower", g["sr_minus_se"], p["sr_lower"])
        for k in ("G1", "G2", "G3", "G4", "G5"):
            c1.check(cid, "gates." + k, g[k], p["gates"][k])
        c1.check(cid, "passes_all", g["pass_all"], p["passes_all"])
        g5 = p["g5"]
        c1.check(cid, "g5.a", g["G5a"], g5["a"])
        c1.check(cid, "g5.b", g["G5b"], g5["b"])
        c1.check(cid, "g5.c", g["G5c"], g5["c"])
        c1.check(cid, "g5.d", g["G5d"], g5["d"])
        c1.check(cid, "g5.quarters_positive", g["G5a_quarters_positive"], g5["quarters_positive"])
        c1.check(cid, "g5.n_quarters", 13, g5["n_quarters"])
        c1.check(cid, "g5.total", g["G5b_total"], g5["total"])
        c1.check(cid, "g5.max_month_sum", max(s["per_month"].values()), g5["max_month_sum"])
        c1.check(cid, "g5.max_month_share", g["G5b_max_month_share"], g5["max_month_share"])
        c1.check(cid, "g5.min_lomo_t", g["G5c_min_t"], g5["min_lomo_t"])
        c1.check(cid, "g5.lomo_undefined", sum(1 for t in g["G5c_loo_t"].values() if t is None), g5["lomo_undefined"])
        c1.check(cid, "g5.tercile_means", g["G5d_tercile_means"], g5["tercile_means"])
        for q in sorted(s["per_quarter"]):
            c1.check(cid, "g5.quarter_means", s["per_quarter"][q] / qn[q], g5["quarter_means"].get(q))
    report[c1.name] = c1.summary()

    # 2. versus the engine's stats.json (P6.2 as the pipeline computed it per configuration)
    c2 = Cmp("own_vs_stats_json")
    sigma = vc.load_sigma_zm(dates)
    terc = vc.tercile_of_dates(dates, sigma)
    terc_sig = {k: [sigma[d] for d in dates if terc[d] == k] for k in (1, 2, 3)}
    mcount = Counter(vc.month_key(d) for d in dates)
    for cid in ids:
        s = S[cid]
        r = json.load(open(vc.OUT / "resim" / f"{cid}.json"))
        e = json.load(open(vc.SEARCH / cid / "stats.json"))
        c2.check(cid, "failed", False, e["failed"])
        c2.check(cid, "n_dates", 796, e["n_dates"])
        for f in ("mean", "sd", "skew", "kurtosis", "sharpe", "n"):
            c2.check(cid, "moments." + f, s["moments"][f], e["moments"][f])
        c2.check(cid, "t_stat", s["t_stat"], e["t_stat"])
        for f in ("trade_count", "trades_per_date", "mean_net_per_trade", "hit_rate", "share_dates_with_trade"):
            c2.check(cid, f, s[f], e[f])
        for k in range(1, 7):
            c2.check(cid, "per_fold.sum", s["per_fold"][str(k)], e["per_fold"][str(k)]["sum"])
            c2.check(cid, "per_fold.n_dates", sum(1 for f in r["fold_of_date"] if f == k), e["per_fold"][str(k)]["n_dates"])
        for q in sorted(s["per_quarter"]):
            c2.check(cid, "per_quarter.sum", s["per_quarter"][q], e["per_quarter"].get(q, {}).get("sum"))
            c2.check(cid, "per_quarter.mean", s["per_quarter"][q] / qn[q], e["per_quarter"].get(q, {}).get("mean"))
            c2.check(cid, "per_quarter.n_dates", qn[q], e["per_quarter"].get(q, {}).get("n_dates"))
        c2.check(cid, "per_quarter.keys", sorted(s["per_quarter"]), sorted(e["per_quarter"]))
        for m in sorted(s["per_month"]):
            c2.check(cid, "per_month.sum", s["per_month"][m], e["per_month"].get(m, {}).get("sum"))
            c2.check(cid, "per_month.mean", s["per_month"][m] / mcount[m], e["per_month"].get(m, {}).get("mean"))
            c2.check(cid, "per_month.n_dates", mcount[m], e["per_month"].get(m, {}).get("n_dates"))
        c2.check(cid, "per_month.keys", sorted(s["per_month"]), sorted(e["per_month"]))
        for k in (1, 2, 3):
            v = e["vol_terciles"][str(k)]
            c2.check(cid, "vol_terciles.mean", s["vol_terciles"][str(k)]["mean"], v["mean"])
            c2.check(cid, "vol_terciles.n_dates", s["vol_terciles"][str(k)]["n"], v["n_dates"])
            c2.check(cid, "vol_terciles.sigma_min", min(terc_sig[k]), v["sigma_min"])
            c2.check(cid, "vol_terciles.sigma_max", max(terc_sig[k]), v["sigma_max"])
        for f in r["counts"]:
            c2.check(cid, "counts." + f, r["counts"][f], e["counts"].get(f))
        ro, eo = r["reported_only"], e["reported_only"]
        for f in ("n_rows", "rho_chosen_ev_net_rows", "rho_chosen_ev_net_trades", "top_decile_mean_net",
                  "top_decile_n", "mid_sign_hit_rate"):
            c2.check(cid, "reported_only." + f, ro[f], eo.get(f))
        for f in ("n_used", "n_nan", "n_zero"):
            c2.check(cid, "reported_only.mid_sign." + f, ro["mid_sign"][f], eo["mid_sign"].get(f))
        c2.check(cid, "reported_only.mid_sign.hit_rate", ro["mid_sign_hit_rate"], eo["mid_sign"].get("hit_rate"))
        for k in range(1, 7):
            c2.check(cid, "folds.model_sha256",
                     json.load(open(vc.SEARCH / cid / f"fold{k}.DONE"))["model_sha256"], e["folds"][str(k)]["model_sha256"])
    report[c2.name] = c2.summary()

    # 3. versus the StatsCoder's D_stats.json
    if DSTATS.exists():
        D = json.load(open(DSTATS))
        c3 = Cmp("own_vs_D_stats")
        c3.check("top", "branch", "N (Tier A empty)", D["branch"])
        for k in ("G1", "G2", "G3", "G4", "G5"):
            c3.check("funnel", f"alone.{k}", SUM["funnel_alone"][k], D["funnel"]["alone"][k])
        for k in ("G1", "G1..G2", "G1..G3", "G1..G4", "G1..G5"):
            c3.check("funnel", f"in_order.{k}", SUM["funnel_in_order"][k], D["funnel"]["in_order"][k])
        c3.check("top", "ranking_top10", SUM["top10"], D["ranking_top10"])
        c3.check("top", "top10.keys", sorted(SUM["top10"]), sorted(D["top10"]))
        th = D["thresholds"]
        c3.check("thresholds", "b_test", bt["b_test_program"], th["b_test"])
        c3.check("thresholds", "G3 (normal moments)", bt["g3_sr_threshold_normal_program"], th["G3"])
        c3.check("thresholds", "N", vc.N_TRIALS, th["N"])
        c3.check("thresholds", "T_disc", vc.T_DISC, th["T_disc"])
        c3.check("thresholds", "T_test", vc.T_TEST, th["T_test"])
        c3.check("thresholds", "SR0 (discovery V)", G[ids[0]]["dsr_program"]["sr0"], th["SR0"])
        c3.check("selection_as_written", "tier_a", SUM["tier_a"], D["selection_as_written"]["tier_a"])
        c3.check("selection_as_written", "tier_b", SUM["tier_b"], D["selection_as_written"]["tier_b"])
        dc = D["configs"]
        c3.check("top", "configs_count", 300, len(dc))
        for cid in ids:
            s, g, d = S[cid], G[cid], dc[cid]
            r = json.load(open(vc.OUT / "resim" / f"{cid}.json"))
            c3.check(cid, "constant", s["constant_series"], d["constant"])
            for f in ("trade_count", "dates_with_trade", "trades_per_date", "share_dates_with_trade",
                      "mean_net_per_trade", "total_net", "hit_rate"):
                c3.check(cid, f, s[f], d[f])
            for f in ("n", "mean", "sd", "skew", "kurtosis", "sharpe"):
                c3.check(cid, "moments." + f, s["moments"][f], d["moments"][f])
            c3.check(cid, "sharpe", s["moments"]["sharpe"], d["sharpe"])
            c3.check(cid, "t", s["t_stat"], d["t"])
            c3.check(cid, "dsr", g["dsr_program"]["dsr"], d["dsr"])
            c3.check(cid, "se", g["se_sharpe"], d["se"])
            c3.check(cid, "sr_lower", g["sr_minus_se"], d["sr_lower"])
            for k in ("G1", "G2", "G3", "G4", "G5"):
                c3.check(cid, "gates." + k, g[k], d["gates"][k])
            g5 = d["g5"]
            c3.check(cid, "g5.a", g["G5a"], g5["a"]); c3.check(cid, "g5.b", g["G5b"], g5["b"])
            c3.check(cid, "g5.c", g["G5c"], g5["c"]); c3.check(cid, "g5.d", g["G5d"], g5["d"])
            c3.check(cid, "g5.pass", g["G5"], g5["pass"])
            c3.check(cid, "g5.quarters_positive", g["G5a_quarters_positive"], g5["quarters_positive"])
            c3.check(cid, "g5.total", g["G5b_total"], g5["total"])
            c3.check(cid, "g5.max_month_sum", max(s["per_month"].values()), g5["max_month_sum"])
            c3.check(cid, "g5.max_month_share", g["G5b_max_month_share"], g5["max_month_share"])
            c3.check(cid, "g5.min_lomo_t", g["G5c_min_t"], g5["min_lomo_t"])
            c3.check(cid, "g5.lomo_undefined", sum(1 for t in g["G5c_loo_t"].values() if t is None), g5["lomo_undefined"])
            c3.check(cid, "g5.tercile_means", g["G5d_tercile_means"], g5["tercile_means"])
            for f in r["counts"]:
                c3.check(cid, "counts_p32." + f, r["counts"][f], d["counts_p32"].get(f))
            if cid in D["top10"]:
                t10 = D["top10"][cid]
                c3.check(cid, "top10.rank", SUM["top10"].index(cid) + 1, t10["rank"])
                p62 = t10["p62"]
                c3.check(cid, "top10.p62.hit_rate", s["hit_rate"], p62["hit_rate"])
                c3.check(cid, "top10.p62.mean_net_per_trade_from_trades", s["mean_net_per_trade"], p62["mean_net_per_trade_from_trades"])
                c3.check(cid, "top10.p62.trades_rows", s["trade_count"], p62["trades_rows"])
                c3.check(cid, "top10.p62.tercile_means", g["G5d_tercile_means"], p62["tercile_means"])
                for k in range(1, 7):
                    c3.check(cid, "top10.p62.per_fold_sums", s["per_fold"][str(k)], p62["per_fold_sums"].get(str(k)))
                for m in sorted(s["per_month"]):
                    v = p62["per_month_sums"].get(m)
                    c3.check(cid, "top10.p62.per_month_sums", s["per_month"][m], v.get("sum") if isinstance(v, dict) else v)
                for q in sorted(s["per_quarter"]):
                    v = p62["per_quarter"].get(q)
                    c3.check(cid, "top10.p62.per_quarter.sum", s["per_quarter"][q], v.get("sum") if isinstance(v, dict) else v)
                ro, do = r["reported_only"], t10["reported_only"]
                for f in ("n_rows", "rho_chosen_ev_net_rows", "rho_chosen_ev_net_trades", "top_decile_mean_net",
                          "top_decile_n", "mid_sign_hit_rate"):
                    c3.check(cid, "top10.reported_only." + f, ro[f], do.get(f))
                for f in ("n_used", "n_nan", "n_zero"):
                    c3.check(cid, "top10.reported_only.mid_sign." + f, ro["mid_sign"][f], do["mid_sign"].get(f))
        report[c3.name] = c3.summary()
        report["D_stats_sha256_note"] = "compared after own numbers were written"
    else:
        report["own_vs_D_stats"] = "StatsCoder comparison pending"

    # 4. three dates per configuration: the 3 dates with the most trades (ties by date), filled by
    # the first OOF dates when fewer than 3 dates traded; on each the pipeline's trades.parquet rows
    # are compared with the own re-simulation (already row-equal for every date; this is the listing).
    three = {}
    for cid in ids:
        r = json.load(open(vc.OUT / "resim" / f"{cid}.json"))
        n_tr = r["n_trades_per_date"]
        order = sorted(range(len(dates)), key=lambda j: (-n_tr[j], dates[j]))
        pick = [j for j in order if n_tr[j] > 0][:3]
        for j in range(len(dates)):
            if len(pick) >= 3:
                break
            if j not in pick:
                pick.append(j)
        pt = pq.read_table(vc.SEARCH / cid / "trades.parquet", columns=["date"]).to_pandas()
        own_t = pq.read_table(vc.OUT / "resim" / f"{cid}.trades.parquet", columns=["date"]).to_pandas()
        three[cid] = [{"date": dates[j], "own_trades": int(n_tr[j]),
                       "pipeline_trades_rows": int((pt["date"] == dates[j]).sum()),
                       "own_trades_rows": int((own_t["date"] == dates[j]).sum()),
                       "X_D_own": r["X_D"][j]} for j in pick]
    three_ok = all(all(e["own_trades"] == e["pipeline_trades_rows"] == e["own_trades_rows"] for e in v)
                   for v in three.values())
    vc.write_json(vc.OUT / "three_dates.json", {"all_equal": three_ok, "per_config": three})
    report["three_dates_all_equal"] = three_ok
    vc.write_json(vc.OUT / "compare.json", report)
    for k, v in report.items():
        if isinstance(v, dict) and "n_agree" in v:
            vc.log(f"{k}: agree {v['n_agree']}, differ {v['n_differ']}, by field {v['differ_by_field']}")
        else:
            vc.log(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
