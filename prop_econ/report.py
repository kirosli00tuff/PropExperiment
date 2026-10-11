"""Stage E.19 aggregator: reports/stage_e19_runs/ -> reports/stage_e19_results.json and
reports/stage_e19_briefs/results_tables.md (brief_grid.md "Outputs").

Derived quantities (all on the headline: bootstrap tail, random direction, d8 costs, continuous
contracts, every rule at readings[0], payout policy max, Back2Funded off, API fee included):
- break-even net Sharpe per (size, path, dll, pricing) at each f and at the best band f (the
  envelope: at each S the band f with the highest cycle mean net), by linear interpolation of the
  cycle mean net over S in {0, 0.15, 0.3, 0.5, 0.75, 1.0}; "< 0" when the net is already positive
  at S = 0, "> 1.0" when it is still negative at S = 1.0; the first upward crossing otherwise.
- the in-simulation optimum f per (size, path, dll, pricing, edge): the f with the highest cycle
  mean net (ties: the smaller f), its Monte Carlo SE and the paired SE of its gap to the runner-up
  (cycles share index draws across f, so the per-cycle differences are paired); separately over
  all seven f including the diagnostic 0.35 and 0.50.

CLI: ``python -m prop_econ.report``.
"""

from __future__ import annotations

import json
import math
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from prop_econ.grid import (
    EDGES,
    F_ALL,
    F_BAND,
    F_DIAG,
    HEADLINE,
    PAYOUT_PATHS,
    PRICING_PATHS,
    RUNS_DIR,
    SHARPES,
    SIZES,
    ZERO_EDGES,
    Job,
    Settings,
    enumerate_jobs,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_JSON = REPO_ROOT / "reports" / "stage_e19_results.json"
TABLES_MD = REPO_ROOT / "reports" / "stage_e19_briefs" / "results_tables.md"
FINGERPRINT_NOTE = (
    "The settings fingerprint hashes the rules file bytes. The lead re-serialized "
    "reports/stage_e19_rules.json for reviewer finding RR-4 (file mtime 2026-10-10 18:01:15 PDT; "
    "only prohibited[P35].bot_implication, a text field the simulator never reads, changed). "
    "Fingerprint before the edit: 1509fa8a6926cde9 (a partial run, discarded at 18:02 when the "
    "grid was restarted to add the RR-1 churn fields); after: d4644acce4988b94. The lead ruled "
    "both valid; the aggregator accepts any fingerprint and lists those found.")
SHARPE_EDGES = tuple(f"S{s:g}" for s in SHARPES)
T4_EDGES = ("zero_k1", "S0.3", "S0.5", "S1")
DLLS = (False, True)


# ------------------------------------------------------------------------------ loading ----
def load_runs(out_dir: Path = RUNS_DIR) -> dict[str, dict[str, Any]]:
    docs = {}
    for p in sorted(out_dir.glob("*.json")):
        try:
            doc = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if doc.get("complete"):
            docs[doc["job_id"]] = doc
    return docs


def flatten(doc: Mapping[str, Any]) -> list[dict[str, Any]]:
    """One flat record per (payout path, pricing, Back2Funded) of a job."""
    j = doc["job"]
    base = {"job_id": doc["job_id"], "family": j["family"], "sc_id": j["sc_id"], **j["sc"],
            "size": j["size"], "edge": j["edge"], "f": j["f"], "f_label": j["f_label"],
            "dll": j["dll"], "variant": j["variant"], "headline": j["headline"]}
    att = {f"att_{k}": v for k, v in doc["attempts"].items()}
    out = []
    for r in doc["records"]:
        xfa = {f"xfa_{k}": v for k, v in doc["xfa"][r["path"]].items()}
        rec = {**base, **att, **xfa, "path": r["path"], "pricing": r["pricing"], "b2f": r["b2f"]}
        for k, v in r.items():
            if k in ("path", "pricing", "b2f"):
                continue
            if k in ("net", "net_ex_api"):
                rec[f"{k}_mean"], rec[f"{k}_se"] = v["mean"], v["se"]
            elif k == "mean_fees_by_type":
                rec.update({f"fees_{t}": x for t, x in v.items()})
            elif k == "post_hoc":
                for name, ms in v.items():
                    rec[f"ph_{name}_mean"], rec[f"ph_{name}_se"] = ms["mean"], ms["se"]
            elif k == "churn":
                rec.update({f"churn_{t}": x for t, x in v.items()})
            else:
                rec[k] = v
        out.append(add_churn(rec))
    return out


# ------------------------------------------------------------------------ churn (RR-1) ----
CHURN_PERIOD = 21  # trading days per billing period
CHURN_LOW, CHURN_MEDIUM = 2.0, 4.0  # lead rule L-19: purchases per 21 Combine-phase days
CAMPAIGN_SLOTS = 5
WINDOW_DAYS = 252


def _rate(num: Any, days: Any) -> float | None:
    return None if num is None or not days else CHURN_PERIOD * num / days


def churn_label(rate: float | None) -> str | None:
    if rate is None:
        return None
    return "low" if rate <= CHURN_LOW else "medium" if rate <= CHURN_MEDIUM else "high"


def add_churn(rec: dict[str, Any]) -> dict[str, Any]:
    """Rates as ratios of cycle means (long-run rates): Combine purchases (start + rebills + paid
    resets) and Combine MLL breaches per 21 Combine-phase days, XFA MLL breaches per 21 XFA days;
    5 slots over the first 252 trading days = 5 x one slot chained from consecutive cycles."""
    if "churn_combine_days_mean" not in rec:
        return rec
    rate = _rate(rec["mean_purchases"], rec["churn_combine_days_mean"])
    w = rec.get("churn_slot_first252_purchases_mean")
    rec.update({
        "purchases_per_21_combine_days": rate,
        "combine_breaches_per_21_combine_days": _rate(rec["churn_combine_breaches_mean"],
                                                      rec["churn_combine_days_mean"]),
        "xfa_breaches_per_21_xfa_days": _rate(rec["churn_xfa_breaches_mean"],
                                              rec["churn_xfa_days_mean"]),
        "slots5_purchases_per_21_days_first252": None if w is None
        else CAMPAIGN_SLOTS * w * CHURN_PERIOD / WINDOW_DAYS,
        "churn_label": churn_label(rate),
        "forfeiture_net": -rec["mean_fees_total"],  # all payouts denied (API fee included)
    })
    camp = rec.get("campaigns", {}).get(f"slots{CAMPAIGN_SLOTS}")
    if camp:
        rec["slots5_purchases_per_21_days_reached"] = {
            t: camp[t].get("purchases_per_21d_reached_mean") for t in ("5000", "10000")}
    return rec


# ------------------------------------------------------------------------------ derived ----
def break_even(s_vals: Sequence[float], means: Sequence[float]) -> float | str:
    """Net Sharpe where the cycle mean net first crosses 0 from below (linear interpolation)."""
    if len(s_vals) != len(means) or not s_vals:
        raise ValueError("s_vals and means must be non-empty and of equal length")
    if means[0] > 0:
        return "< 0"
    if means[0] == 0:
        return float(s_vals[0])
    for i in range(1, len(s_vals)):
        if means[i] >= 0:
            s0, s1, m0, m1 = s_vals[i - 1], s_vals[i], means[i - 1], means[i]
            return float(s0 + (0.0 - m0) * (s1 - s0) / (m1 - m0))
    return f"> {s_vals[-1]:g}"


def select_optimum(fs: Sequence[float], nets: Mapping[float, np.ndarray]) -> dict[str, Any]:
    """Best f by cycle mean net (ties: the first in ``fs``), its SE, and the paired SE of the
    per-cycle gap to the runner-up."""
    means = np.array([float(np.mean(nets[f])) for f in fs])
    order = np.argsort(-means, kind="stable")
    best, runner = fs[int(order[0])], fs[int(order[1])] if len(fs) > 1 else None
    x = nets[best]
    out = {"best_f": best, "mean": float(means[order[0]]),
           "se": float(np.std(x, ddof=1) / math.sqrt(x.size)), "runner_up_f": runner,
           "means": {f"{f:.2f}": float(m) for f, m in zip(fs, means, strict=True)}}
    if runner is not None:
        d = x - nets[runner]
        out["gap"] = float(d.mean())
        out["gap_paired_se"] = float(np.std(d, ddof=1) / math.sqrt(d.size))
    return out


def paired_diff(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    d = a - b
    return {"diff": float(d.mean()), "paired_se": float(np.std(d, ddof=1) / math.sqrt(d.size))}


def _headline_index(records: Sequence[Mapping[str, Any]]) -> dict[tuple, Mapping[str, Any]]:
    return {(r["size"], r["path"], r["dll"], r["pricing"], r["edge"], r["f"]): r
            for r in records if r["headline"] and not r["b2f"]}


def _load_nets(out_dir: Path, job_id: str) -> dict[str, np.ndarray] | None:
    p = out_dir / f"{job_id}.npz"
    if not p.exists():
        return None
    with np.load(p) as z:
        return {k: z[k] for k in z.files}


def _headline_job(size: str, edge: str, f: float, dll: bool) -> Job:
    return Job(HEADLINE, size, edge, f, dll, "base", "headline")


def derive_break_even(idx: Mapping[tuple, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for size in SIZES:
        for path in PAYOUT_PATHS:
            for dll in DLLS:
                for pricing in PRICING_PATHS:
                    key = (size, path, dll, pricing)
                    row: dict[str, Any] = {"size": size, "path": path, "dll": dll,
                                           "pricing": pricing}
                    try:
                        for f in F_ALL:
                            means = [idx[(*key, e, f)]["net_mean"] for e in SHARPE_EDGES]
                            row[f"f{f:.2f}"] = break_even(SHARPES, means)
                        env, best_fs = [], []
                        for e in SHARPE_EDGES:
                            m = {f: idx[(*key, e, f)]["net_mean"] for f in F_BAND}
                            bf = max(F_BAND, key=lambda f, m=m: (m[f], -f))
                            env.append(m[bf])
                            best_fs.append(bf)
                        row["best_band_f"] = break_even(SHARPES, env)
                        row["best_band_f_by_S"] = dict(zip(SHARPE_EDGES, best_fs, strict=True))
                    except KeyError as exc:
                        row["missing"] = str(exc)
                    rows.append(row)
    return rows


def derive_optimum(out_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    band_rows, diag_rows = [], []
    for size in SIZES:
        for dll in DLLS:
            for edge in EDGES:
                loaded = {f: _load_nets(out_dir, _headline_job(size, edge, f, dll).id)
                          for f in F_ALL}
                for path in PAYOUT_PATHS:
                    for pricing in PRICING_PATHS:
                        head = {"size": size, "path": path, "dll": dll, "pricing": pricing,
                                "edge": edge}
                        if any(v is None for v in loaded.values()):
                            band_rows.append({**head, "missing": True})
                            diag_rows.append({**head, "missing": True})
                            continue
                        nets = {f: loaded[f][f"{path}|{pricing}"] for f in F_ALL}
                        band_rows.append({**head, **select_optimum(F_BAND, nets)})
                        diag = {**head, "all_f": select_optimum(F_ALL, nets)}
                        for f in F_DIAG:
                            diag[f"f{f:.2f}_minus_f0.25"] = paired_diff(nets[f], nets[0.25])
                        diag_rows.append(diag)
    return band_rows, diag_rows


def derive_eff_sharpe(docs: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for doc in docs.values():
        if "eff_sharpe" not in doc:
            continue
        j = doc["job"]
        rows.append({"sc_id": j["sc_id"], "family": j["family"], "size": j["size"],
                     "edge": j["edge"], "f": j["f"], "dll": j["dll"], "variant": j["variant"],
                     **{ph: doc["eff_sharpe"][ph] for ph in ("attempt", "xfa", "pooled")}})
    return sorted(rows, key=lambda r: (r["sc_id"], r["size"], r["edge"], r["dll"], r["f"]))


# ------------------------------------------------------------------------------- tables ----
def _d(x: Any) -> str:
    return "-" if x is None else f"{x:,.0f}"


def _p(x: Any) -> str:
    return "-" if x is None else f"{x:.3f}"


def _ms(mean: Any, se: Any) -> str:
    return "-" if mean is None else f"{mean:,.0f} ({se:,.0f})"


def _s(x: Any) -> str:
    return x if isinstance(x, str) else ("-" if x is None else f"{x:.2f}")


def _churn(r: Mapping[str, Any]) -> str:
    rate = r.get("purchases_per_21_combine_days")
    return "-" if rate is None else f"{r['churn_label']} ({rate:.2f})"


def _low(low: tuple[float, Mapping[str, Any]] | None) -> str:
    return "none low" if low is None else f"{low[0]:.2f}: {_d(low[1]['net_mean'])}"


def _table(header: Sequence[str], rows: Sequence[Sequence[Any]]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out


def best_band(idx: Mapping[tuple, Mapping[str, Any]], size: str, path: str, dll: bool,
              pricing: str, edge: str, low_only: bool = False
              ) -> tuple[float, Mapping[str, Any]] | None:
    """Band f with the highest cycle mean net (ties: smaller f); ``low_only`` restricts the
    choice to rule sets labelled 'low' churn (L-19)."""
    cands = [(f, idx.get((size, path, dll, pricing, edge, f))) for f in F_BAND]
    cands = [(f, r) for f, r in cands
             if r is not None and (not low_only or r.get("churn_label") == "low")]
    if not cands:
        return None
    return max(cands, key=lambda c: (c[1]["net_mean"], -c[0]))


def better_pricing(idx: Mapping[tuple, Mapping[str, Any]], size: str, path: str, dll: bool,
                   edge: str) -> str | None:
    """Pricing path with the higher cycle mean net at its own best band f."""
    vals = {p: best_band(idx, size, path, dll, p, edge) for p in PRICING_PATHS}
    vals = {p: v for p, v in vals.items() if v is not None}
    return max(vals, key=lambda p: vals[p][1]["net_mean"]) if vals else None


def _rec_b2f(records: Sequence[Mapping[str, Any]]) -> dict[tuple, Mapping[str, Any]]:
    return {(r["job_id"], r["path"], r["pricing"]): r for r in records if r["b2f"]}


def table_t1(idx: Mapping, b2f: Mapping) -> list[str]:
    lines = ["## T1 Headline at zero_k1 and S 0.5, best band f per row",
             "", "Configuration: bootstrap tail, random direction, d8 costs, continuous "
             "contracts, payout policy max, call-up none (discretionary), every rule at "
             "readings[0], Back2Funded off (last column on), API fee included (ex-API column "
             "excludes it). Best f = band f with the highest cycle mean net, with its churn "
             "label (L-19: Combine purchases per 21 Combine-phase days, low <= 2.0, medium "
             "<= 4.0, else high); 'low-churn best f' = the best band f among 'low' rule sets "
             "and its cycle mean net. Dollars per cycle (SE in brackets).", ""]
    rows = []
    for edge in ("zero_k1", "S0.5"):
        for size in SIZES:
            for path in PAYOUT_PATHS:
                for dll in DLLS:
                    for pricing in PRICING_PATHS:
                        bb = best_band(idx, size, path, dll, pricing, edge)
                        if bb is None:
                            continue
                        f, r = bb
                        on = b2f.get((r["job_id"], path, pricing))
                        low = best_band(idx, size, path, dll, pricing, edge, low_only=True)
                        rows.append([edge, size, path, "on" if dll else "off", pricing, f"{f:.2f}",
                                     _churn(r), _low(low),
                                     _p(r["att_p_pass"]), _p(r["xfa_p_any_payout"]),
                                     _ms(r["net_mean"], r["net_se"]), _d(r["net_ex_api_mean"]),
                                     f"{_d(r['net_p5'])} / {_d(r['net_p50'])} / "
                                     f"{_d(r['net_p95'])}", _p(r["p_no_payout"]),
                                     f"{r['mean_purchases']:.1f}", _d(r["net_per_purchase"]),
                                     _d(r["per_funded_xfa"]), _d(r["mean_cycle_days"]),
                                     _d(r["mean_days_to_first_payout"]),
                                     _d(on["net_mean"]) if on else "-"])
    return lines + _table(["edge", "size", "path", "DLL", "pricing", "best f",
                           "churn (purch/21 Combine d)", "low-churn best f: net", "P(pass)",
                           "XFA P(any payout)", "net mean (SE)", "net ex API",
                           "net P5 / P50 / P95", "P(no payout)", "purchases", "net/purchase",
                           "per funded XFA", "cycle days", "days to 1st payout",
                           "net B2F on"], rows) + [""]


def table_t2(idx: Mapping) -> list[str]:
    lines = ["## T2 Cycle mean net (SE) by f x edge, DLL off, cheaper pricing per cell", "",
             "Headline configuration as T1, DLL off, Back2Funded off, API fee included. "
             "Cheaper pricing = the pricing path with the lower mean total fees in that cell "
             "(suffix s = standard, n = no_activation_fee). f 0.35 and 0.50 are diagnostic, "
             "outside the policy band.", ""]
    for size in SIZES:
        for path in PAYOUT_PATHS:
            rows = []
            for edge in EDGES:
                row = [edge]
                for f in F_ALL:
                    cells = [idx.get((size, path, False, p, edge, f)) for p in PRICING_PATHS]
                    cells = [c for c in cells if c is not None]
                    if not cells:
                        row.append("-")
                        continue
                    c = min(cells, key=lambda c: c["mean_fees_total"])
                    tag = "s" if c["pricing"] == "standard" else "n"
                    row.append(f"{_ms(c['net_mean'], c['net_se'])} {tag}")
                rows.append(row)
            lines += [f"### {size}, {path} path", ""]
            lines += _table(["edge"] + [f"f {f:.2f}" + ("*" if f in F_DIAG else "")
                                        for f in F_ALL], rows) + [""]
    return lines


def table_t3(be: Sequence[Mapping[str, Any]], eff: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = ["## T3 Break-even net Sharpe", "",
             "Headline configuration, Back2Funded off, API fee included. Linear interpolation "
             "of the cycle mean net over S in {0, 0.15, 0.3, 0.5, 0.75, 1.0}; '< 0' = positive "
             "already at S = 0, '> 1' = still negative at S = 1.0. 'best band f' uses at each S "
             "the band f with the highest mean net. f 0.35 / 0.50 diagnostic.", ""]
    rows = [[r["size"], r["path"], "on" if r["dll"] else "off", r["pricing"]]
            + [_s(r.get(f"f{f:.2f}")) for f in F_ALL] + [_s(r.get("best_band_f"))] for r in be]
    lines += _table(["size", "path", "DLL", "pricing"] + [f"f {f:.2f}" for f in F_ALL]
                    + ["best band f"], rows) + [""]
    lines += ["### Effective net Sharpe of the zero edge (headline shocks, DLL off)", "",
              "Computed from the vehicle mix actually traded: the scalar reference replays the "
              "first 200 attempt rows and the first 200 XFA rows (standard path) of each job "
              "with a day log; risk-weighted S_eff = -sqrt(252) x sum(n x k x rt_u) / "
              "sum(n x sigma_u) over all traded days of both phases (expected cost per dollar of "
              "daily sd); day-weighted = -sqrt(252) x mean(k x rt_u / sigma_u). 'full share' = "
              "share of traded days on the full-size contract.", ""]
    rows = [[r["size"], r["edge"], f"{r['f']:.2f}", _s(r["pooled"]["risk_weighted"]),
             _s(r["pooled"]["day_weighted"]), _p(r["pooled"]["full_share"]),
             r["pooled"]["days"]]
            for r in eff if r["sc_id"] == HEADLINE.id and r["variant"] == "base"
            and not r["dll"]]
    return lines + _table(["size", "edge", "f", "S_eff risk-weighted", "S_eff day-weighted",
                           "full share", "days logged"], rows) + [""]


def table_t4(idx: Mapping) -> list[str]:
    lines = ["## T4 Campaigns at the best band f", "",
             "Headline configuration, DLL off, Back2Funded off, API fee included in fees (one per "
             "user, per started 21-trading-day period). Pricing = the path with the higher cycle "
             "mean net at its best band f. P50 / P80 = the K reached with 50% / 80% probability "
             "('-' when the share reaching the target is below that); cap 400 purchases. Churn "
             "label of the best f as in T1; the last column gives the best band f among 'low' "
             "churn rule sets and its $5k purchases P50 / P80; purchases per 21 elapsed days = "
             "mean over the replications that reached $5k.", ""]
    rows = []
    for edge in T4_EDGES:
        for size in SIZES:
            for path in PAYOUT_PATHS:
                pricing = better_pricing(idx, size, path, False, edge)
                if pricing is None:
                    continue
                f, r = best_band(idx, size, path, False, pricing, edge)
                low = best_band(idx, size, path, False, pricing, edge, low_only=True)
                for slots in ("slots1", "slots5"):
                    c = r.get("campaigns", {}).get(slots)
                    if c is None:
                        continue
                    row = [edge, size, path, pricing, f"{f:.2f}", _churn(r), slots[5:]]
                    for tgt in ("5000", "10000"):
                        t = c[tgt]
                        row += [_p(t["share_not_reached"]),
                                f"{_d(t['purchases_p50'])} / {_d(t['purchases_p80'])}",
                                f"{_d(t['fees_p50'])} / {_d(t['fees_p80'])}",
                                f"{_d(t['days_p50'])} / {_d(t['days_p80'])}"]
                    rate = c["5000"].get("purchases_per_21d_reached_mean")
                    row.append("-" if rate is None else f"{rate:.2f}")
                    lc = None if low is None else low[1].get("campaigns", {}).get(slots)
                    row.append("none low" if lc is None else
                               f"{low[0]:.2f}: {_d(lc['5000']['purchases_p50'])} / "
                               f"{_d(lc['5000']['purchases_p80'])}")
                    rows.append(row)
    hdr = ["edge", "size", "path", "pricing", "best f", "churn (purch/21 Combine d)", "slots"]
    for tgt in ("$5k", "$10k"):
        hdr += [f"{tgt} not reached", f"{tgt} purchases P50/P80", f"{tgt} fees P50/P80",
                f"{tgt} days P50/P80"]
    hdr += ["$5k purchases per 21 elapsed d (reached)", "low-churn best f: $5k purch P50/P80"]
    return lines + _table(hdr, rows) + [""]


def table_t8(idx: Mapping) -> list[str]:
    lines = ["## T8 Churn (reviewer finding RR-1, lead rule L-19)", "",
             "Headline configuration, DLL off, Back2Funded off, cheaper pricing per cell (lower "
             "mean total fees; s / n). Churn = Combine purchases (start + rebills + paid resets) "
             "per 21 Combine-phase trading days, the ratio of the cycle means (Combine-phase "
             "days = the cycle's exact attempt days; a reset starts the next attempt the next "
             "trading day, so there are no gap days); label low <= 2.0, medium <= 4.0, else "
             "high. Breaches: Combine MLL breaches per 21 Combine-phase days, XFA MLL breaches "
             "per 21 XFA days. 5-slot first year: 5 x the purchases of one slot (consecutive "
             "cycles back to back) in its first 252 trading days, per 21 days. Forfeiture = cycle "
             "mean net if every payout were denied (= minus mean total fees incl. API), shown "
             "for medium and high churn. f 0.35 / 0.50 diagnostic.", ""]
    rows = []
    for size in SIZES:
        for path in PAYOUT_PATHS:
            for edge in T4_EDGES:
                for f in F_ALL:
                    cells = [idx.get((size, path, False, p, edge, f)) for p in PRICING_PATHS]
                    cells = [c for c in cells if c is not None]
                    if not cells:
                        continue
                    c = min(cells, key=lambda c: c["mean_fees_total"])
                    lab = c.get("churn_label")
                    rows.append([size, path, edge, f"{f:.2f}",
                                 "s" if c["pricing"] == "standard" else "n",
                                 _ms(c["net_mean"], c["net_se"]), _churn(c),
                                 _s(c.get("combine_breaches_per_21_combine_days")),
                                 _s(c.get("xfa_breaches_per_21_xfa_days")),
                                 _s(c.get("slots5_purchases_per_21_days_first252")),
                                 _d(c["forfeiture_net"]) if lab in ("medium", "high") else ""])
    return lines + _table(["size", "path", "edge", "f", "pricing", "net mean (SE)",
                           "churn (purch/21 Combine d)", "Combine breaches/21 d",
                           "XFA breaches/21 d", "5-slot purch/21 d, first 252 d",
                           "forfeiture net"], rows) + [""]


def _twin_key(r: Mapping[str, Any]) -> tuple:
    return (r["size"], r["path"], False, r["pricing"], r["edge"])


def table_t5(records: Sequence[Mapping[str, Any]], idx: Mapping) -> list[str]:
    lines = ["## T5 Sensitivities against the headline twin", "",
             "DLL off, Back2Funded off, API fee included. Twin = the headline record with the "
             "same size, path, pricing, edge (and f where shown). Pricing = the twin's better "
             "pricing (higher mean net at its best band f). 'best' columns: each side at its own "
             "best band f; 'at twin f': the sensitivity at the twin's best band f, minus the "
             "twin; SE of differences unpaired (sqrt(se1^2 + se2^2), conservative where the "
             "seeds are shared).", ""]
    sens: dict[tuple, dict[float, Mapping[str, Any]]] = {}
    for r in records:
        if r["headline"] or r["b2f"]:
            continue
        sens.setdefault((r["family"], *_twin_key(r)), {})[r["f"]] = r
    rows = []
    for key in sorted(sens):
        fam, size, path, _, pricing, edge = key
        if pricing != better_pricing(idx, size, path, False, edge):
            continue
        by_f = sens[key]
        tw = best_band(idx, size, path, False, pricing, edge)
        if tw is None:
            continue
        tf, trec = tw
        sf = max(by_f, key=lambda f: (by_f[f]["net_mean"], -f))
        cmp_fs = [tf] if tf in by_f else []
        if fam in ("scaling_upper", "ccons_inclusive"):
            cmp_fs = sorted(by_f)
        for f in cmp_fs or [None]:
            twin = idx.get((size, path, False, pricing, edge, f)) if f is not None else None
            s = by_f.get(f) if f is not None else None
            diff = se = None
            if twin and s:
                diff = s["net_mean"] - twin["net_mean"]
                se = math.hypot(s["net_se"], twin["net_se"])
            rows.append([fam, size, path, pricing, edge, f"{tf:.2f}",
                         _ms(trec["net_mean"], trec["net_se"]), f"{sf:.2f}",
                         _ms(by_f[sf]["net_mean"], by_f[sf]["net_se"]),
                         "-" if f is None else f"{f:.2f}",
                         _ms(s["net_mean"], s["net_se"]) if s else "-",
                         _ms(diff, se) if diff is not None else "-"])
    lines += _table(["family", "size", "path", "pricing", "edge", "twin best f",
                     "twin mean (SE)", "sens best f", "sens mean (SE)", "at f",
                     "sens at f (SE)", "sens - twin (SE)"], rows) + [""]
    lines += ["### Post hoc wallet sensitivities on the headline (no new simulation)", "",
              "DLL off, Back2Funded off, best band f, better pricing. ACH: $30 per payout "
              "(global.payout_fee_usd.ach). Close: XFAs alive at the horizon closed for split x "
              "min(0.5 x end balance, $5,000) (rules file values). Copy x5: five accounts "
              "trading the same fills = 5 x (cash - Combine/activation fees) - one API fee.", ""]
    rows = []
    for edge in ("zero_k1", "S0.5"):
        for size in SIZES:
            for path in PAYOUT_PATHS:
                pricing = better_pricing(idx, size, path, False, edge)
                if pricing is None:
                    continue
                f, r = best_band(idx, size, path, False, pricing, edge)
                rows.append([edge, size, path, pricing, f"{f:.2f}",
                             _ms(r["net_mean"], r["net_se"]),
                             _ms(r["net_ex_api_mean"], r["net_ex_api_se"]),
                             _ms(r["ph_payout_fee_ach_mean"], r["ph_payout_fee_ach_se"]),
                             _ms(r["ph_voluntary_close_mean"], r["ph_voluntary_close_se"]),
                             _ms(r["ph_copy_traded_mean"], r["ph_copy_traded_se"])])
    return lines + _table(["edge", "size", "path", "pricing", "f", "headline", "API excluded",
                           "ACH $30/payout", "voluntary close", "copy x5"], rows) + [""]


def table_t6(opt: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = ["## T6 In-simulation optimum f in the policy band", "",
             "Headline configuration, Back2Funded off, API fee included. Best f = highest cycle "
             "mean net among f 0.05..0.25 (ties: smaller f); gap = best minus runner-up, paired "
             "SE over the shared cycle draws.", ""]
    rows = [[r["size"], r["path"], "on" if r["dll"] else "off", r["pricing"], r["edge"],
             f"{r['best_f']:.2f}", _ms(r["mean"], r["se"]), f"{r['runner_up_f']:.2f}",
             _ms(r["gap"], r["gap_paired_se"])] for r in opt if not r.get("missing")]
    return lines + _table(["size", "path", "DLL", "pricing", "edge", "best f",
                           "mean net (SE)", "runner-up f", "gap (paired SE)"], rows) + [""]


def table_t7(diag: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = ["## T7 Diagnostic f (0.35, 0.50; outside the policy band)", "",
             "Headline configuration, Back2Funded off, API fee included. Does the cycle mean net "
             "keep rising above f 0.25? Differences paired over the shared cycle draws; 'best of "
             "all 7' over f 0.05..0.50.", ""]
    rows = []
    for r in diag:
        if r.get("missing"):
            continue
        a = r["all_f"]
        m = a["means"]
        rows.append([r["size"], r["path"], "on" if r["dll"] else "off", r["pricing"], r["edge"],
                     _d(m["0.25"]), _d(m["0.35"]), _d(m["0.50"]),
                     _ms(r["f0.35_minus_f0.25"]["diff"], r["f0.35_minus_f0.25"]["paired_se"]),
                     _ms(r["f0.50_minus_f0.25"]["diff"], r["f0.50_minus_f0.25"]["paired_se"]),
                     f"{a['best_f']:.2f}", _ms(a["gap"], a["gap_paired_se"])])
    return lines + _table(["size", "path", "DLL", "pricing", "edge", "f 0.25", "f 0.35",
                           "f 0.50", "0.35 - 0.25 (SE)", "0.50 - 0.25 (SE)", "best of all 7",
                           "gap to runner-up (SE)"], rows) + [""]


# --------------------------------------------------------------------------------- main ----
def build(out_dir: Path = RUNS_DIR) -> dict[str, Any]:
    docs = load_runs(out_dir)
    expected = enumerate_jobs()
    missing = [j.id for j in expected if j.id not in docs]
    records = [r for d in docs.values() for r in flatten(d)]
    idx = _headline_index(records)
    band, diag = derive_optimum(out_dir)
    return {
        "generated_pdt": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "settings": Settings().__dict__, "zero_edges": ZERO_EDGES,
        "n_jobs_expected": len(expected), "n_jobs_found": len(docs), "missing": missing,
        "fingerprints_found": sorted({d.get("fingerprint") for d in docs.values()}),
        "fingerprint_note": FINGERPRINT_NOTE,
        "jobs": [{"job_id": k, **d["job"], "attempts": d["attempts"], "seeds": d["seeds"],
                  "seconds": d["seconds"], "eff_sharpe": d.get("eff_sharpe")}
                 for k, d in sorted(docs.items())],
        "records": records,
        "derived": {"break_even": derive_break_even(idx), "eff_sharpe": derive_eff_sharpe(docs),
                    "optimum_band": band, "optimum_all_f": diag},
    }


def tables(res: Mapping[str, Any]) -> str:
    records = res["records"]
    idx = _headline_index(records)
    b2f = _rec_b2f(records)
    der = res["derived"]
    lines = ["# Stage E.19 grid results (machine-generated by prop_econ/report.py)", "",
             f"Generated {res['generated_pdt']}; jobs found {res['n_jobs_found']} of "
             f"{res['n_jobs_expected']}; missing {len(res['missing'])}. Dollars rounded to "
             "whole dollars, probabilities to 3 decimals. Per configuration: 20,000 attempts, "
             "20,000 XFAs, 20,000 cycles, 20,000 campaign replications; horizon 756 trading "
             "days; attempt cap 60 per cycle; base seed 20261019.", ""]
    lines += table_t1(idx, b2f)
    lines += table_t2(idx)
    lines += table_t3(der["break_even"], der["eff_sharpe"])
    lines += table_t4(idx)
    lines += table_t5(records, idx)
    lines += table_t6(der["optimum_band"])
    lines += table_t7(der["optimum_all_f"])
    lines += table_t8(idx)
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    res = build()
    RESULTS_JSON.write_text(json.dumps(res, allow_nan=False, default=list))
    TABLES_MD.write_text(tables(res))
    print(f"jobs {res['n_jobs_found']}/{res['n_jobs_expected']}, records {len(res['records'])},"
          f" missing {len(res['missing'])}; wrote {RESULTS_JSON} and {TABLES_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
