"""Stage E.29 review, static checks (tasks 3 and 4): reads files only, writes check_static.json beside itself.

Independent of the E.29 code except where named (cell_point_fn for the B3 law-B check, run fingerprints):
members from A3_econ.json pair records (not A3_inputs.json), the trade split from declaration section 2, M and S
from section 3, the edge settings from section 5, the best-basket rule of section 6 and the beats rule of section 7
re-implemented on integer grid indices.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ST = REPO / "reports" / "stage_e29_briefs"
CELLS = ST / "work" / "basket" / "cells"
E28 = json.loads((REPO / "reports" / "stage_e28_briefs" / "A3_econ.json").read_text())
J = json.loads((ST / "E29_cells.json").read_text())
TABLES = (ST / "E29_tables.md").read_text().splitlines()

SPLIT = {"B0": {"QM": 20}, "B1": {"QM": 10, "ZM": 10}, "B2": {"QM": 10, "MGC": 10},
         "B3": {"QM": 7, "ZM": 7, "MGC": 6}, "B4": {"QM": 10, "MNQ": 10}}
FIRMS = ("topstep", "lucid", "tradeify", "mffu", "bulenox")
OTHER = ("B1", "B2", "B3", "B4")
RHOS = (0.0, 0.25, 0.5, 0.75)
issues: list[str] = []
counts: dict[str, int] = {}


def bump(k: str, n: int = 1) -> None:
    counts[k] = counts.get(k, 0) + n


def flag(msg: str) -> None:
    issues.append(msg)


def pair(firm: str, code: str) -> dict[str, Any]:
    return next(p for p in E28["pairs"] if p["firm"] == firm and p["code"] == code)


def gx(v: Any) -> int | None:
    """Grid index of a threshold value; None for '> 4' / '> 12'."""
    return None if isinstance(v, str) or v is None else int(round(float(v) * 100))


# ---------------------------------------------------------------- provenance ----
def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


decl_sha = sha(REPO / "reports" / "stage_e29_model.md")
prov = {"declaration_sha_ok": decl_sha == "f393759f4af712a889646a7a4cdb2c45f2f3b8496a6403be56467de7eb0d8164"}
w28 = REPO / "reports" / "stage_e28_briefs" / "work" / "A3_econ"
cur28 = {n: sha(w28 / n) for n in J["e28_sha256"] if n != "A3_econ.json"}
cur28["A3_econ.json"] = sha(REPO / "reports" / "stage_e28_briefs" / "A3_econ.json")
prov["e28_sha_ok"] = cur28 == J["e28_sha256"]
prov["code_sha_ok"] = all(sha(ST / "work" / "basket" / n) == v for n, v in J["code_sha256"].items())
sys.path.insert(0, str(ST / "work" / "basket"))
import e29_run as RUN  # noqa: E402  (fingerprint helpers only)

cfp = RUN.code_fingerprint()
prov["code_fingerprint_ok"] = cfp == J["code_fingerprint"]
stale = []
for p in sorted(CELLS.glob("*.json")):
    rec = json.loads(p.read_text())
    if rec.get("fingerprint") != RUN.cell_fp(cfp, rec["spec"]):
        stale.append(p.name)
prov["cell_files"] = len(list(CELLS.glob("*.json")))
prov["stale_cell_files"] = stale
if not all(v for k, v in prov.items() if k.endswith("_ok")) or stale:
    flag(f"provenance: {prov}")

# ---------------------------------------------------------------- E.28 inputs ----
inp = json.loads((w28 / "A3_inputs.json").read_text())
for f in FIRMS:
    for c in ("QM", "ZM", "MGC", "MNQ"):
        e, cand = pair(f, c), inp["candidates"][c]
        ip = next(p for p in inp["pairs"] if p["firm"] == f and p["code"] == c)
        ok = (cand["v_usd"] == e["v"] and cand["sigma_1m_ticks"] == e["sigma_T"] and ip["F_rt_usd"] == e["F_rt_usd"]
              and cand["S_rt_ticks"] == e["S_rt_ticks"] == 1.0
              and abs(ip["F_rt_usd"] / cand["v_usd"] - e["c_lim_ticks"]) < 1e-12)
        bump("input_pairs_checked")
        if not ok:
            flag(f"inputs differ from A3_econ.json at {f} {c}")

# ---------------------------------------------------------------- alone records ----
alone = {(a["firm"], a["code"]): a for a in J["alone"]}
alone_rows = []
for (f, c), a in alone.items():
    e = pair(f, c)
    gl, gm = gx(a["limit"]["mu_star"]), gx(a["market"]["mu_star"])
    row = {"firm": f, "code": c, "e28": [e["mu_star_lim"], e["mu_star_mkt"]],
           "e29": [a["limit"]["mu_star"], a["market"]["mu_star"]]}
    for case, g, e28v in (("limit", gl, e["mu_star_lim"]), ("market", gm, e["mu_star_mkt"])):
        if isinstance(e28v, str):
            row[f"{case}_consistent"] = g is None or g > 400
        else:
            row[f"{case}_consistent"] = g == gx(e28v)
    row["mkt_eq_lim_plus_1"] = (gl is None and gm is None) or (gl is not None and gm == gl + 100)
    alone_rows.append(row)
    if not (row["limit_consistent"] and row["market_consistent"]):
        flag(f"alone {f} {c} inconsistent with E.28: {row}")


def mu_alone(f: str, c: str, market: bool) -> float | None:
    v = pair(f, c)["mu_star_mkt" if market else "mu_star_lim"]
    if not isinstance(v, str):
        return float(v)
    x = alone[(f, c)]["market" if market else "limit"]["mu_star"]
    return None if isinstance(x, str) else float(x)


# ---------------------------------------------------------------- per cell ----
def members(f: str, b: str) -> list[dict[str, Any]]:
    out = []
    for c, t in SPLIT[b].items():
        e = pair(f, c)
        out.append({"code": c, "T": t, "v": e["v"], "sigma": e["sigma_T"], "c": e["c_lim_ticks"], "srt": 1.0})
    return out


def law(mem: list[dict[str, Any]], mus: list[float], rho: float, market: bool) -> tuple[float, float]:
    m = sum(x["T"] * (mu - x["c"] - (x["srt"] if market else 0.0)) * x["v"] for x, mu in zip(mem, mus))
    s = [math.sqrt(x["T"]) * x["sigma"] * x["v"] for x in mem]
    var = sum(y * y for y in s) + 2 * rho * sum(s[i] * s[j] for i in range(len(s)) for j in range(i + 1, len(s)))
    return m, math.sqrt(var)


def mus_at(mem: list[dict[str, Any]], setting: str, x: float, ms: dict[str, float] | None) -> list[float]:
    if setting == "i":
        return [x * ms[m["code"]] for m in mem]
    return [x if m["code"] == "QM" else 0.0 for m in mem]


def bisect_ok(ev: dict[int, dict[str, Any]], g: int | None, key: str, top: int) -> bool:
    f = (lambda r: r["ev"]) if key == "ev" else (lambda r: r["p10k"] - 0.5)
    if g is None:
        return top in ev and f(ev[top]) < 0
    if g not in ev or f(ev[g]) < 0:
        return False
    return g == 0 or (g - 1 in ev and f(ev[g - 1]) < 0)


cells = {c["cell_id"]: c for c in J["cells"]}
n_eval_rows = max_rel_m = max_rel_s = 0.0
na_cells = []
for cid, c in cells.items():
    full = json.loads((CELLS / f"{cid}.json").read_text())
    f, b, s, case, form = c["firm"], c["basket"], c["setting"], c["case"], c["form"]
    rho = 0.0 if c["rho"] is None else c["rho"]
    market = case == "market"
    mem = members(f, b)
    got = [(m["code"], m["T"]) for m in c["members"]]
    if got != [(m["code"], m["T"]) for m in mem]:
        flag(f"{cid}: members/T {got}")
    for gm, mm in zip(c["members"], mem):
        if (gm["v"], gm["sigma"], gm["s_rt"]) != (mm["v"], mm["sigma"], mm["srt"]) or abs(gm["c_lim"] - mm["c"]) > 1e-12:
            flag(f"{cid}: member params {gm['code']}")
    _, s_ref = law(mem, [0.0] * len(mem), rho, market)
    if abs(c["S_usd"] - s_ref) > 1e-9 * s_ref or abs(c["S_over_MLL"] - s_ref / pair(f, "QM")["MLL_usd"]) > 1e-12:
        flag(f"{cid}: S {c['S_usd']} vs {s_ref}")
    bump("cells_S_checked")
    # edge units (section 5)
    if s == "i":
        want = {m["code"]: mu_alone(f, m["code"], market) for m in mem}
        if c["status"] == "n/a":
            na_cells.append(cid)
            if all(v is not None for v in want.values()):
                flag(f"{cid}: n/a but every alone break-even exists")
            continue
        if any(abs(c["mu_star"][k] - v) > 1e-12 for k, v in want.items()):
            flag(f"{cid}: mu_star {c['mu_star']} vs {want}")
        bump("cells_mu_star_checked")
    elif c["status"] != "computed":
        flag(f"{cid}: status {c['status']}")
        continue
    ms = c["mu_star"]
    ev = {}
    for r in full["evaluations"]:
        m_ref, s_ref = law(mem, mus_at(mem, s, r["x"], ms), rho, market)
        rel_m = abs(r["M"] - m_ref) / max(abs(m_ref), 1e-9)
        if abs(r["M"] - m_ref) > 1e-9 * max(abs(m_ref), 1.0) or abs(r["S"] - s_ref) > 1e-9 * s_ref:
            flag(f"{cid} g {r['g']}: M/S {r['M']},{r['S']} vs {m_ref},{s_ref}")
        max_rel_m = max(max_rel_m, rel_m if abs(m_ref) > 1e-6 else 0.0)
        max_rel_s = max(max_rel_s, abs(r["S"] - s_ref) / s_ref)
        n_eval_rows += 1
        if r["g"] != round(r["x"] * 100):
            flag(f"{cid}: g/x mismatch")
        ev[r["g"]] = r
    g_t = c["threshold"]["g"]
    if c["threshold"]["value"] != (f"> 4" if g_t is None else round(g_t * 0.01, 2)):
        flag(f"{cid}: threshold value/g")
    if not bisect_ok(ev, g_t, "ev", 400):
        flag(f"{cid}: EV bracket at threshold not shown by evaluations")
    bump("cells_bracket_checked")
    if not market:
        g_p = c["x10K"]["g"]
        if not bisect_ok(ev, g_p, "p10k", 400):
            flag(f"{cid}: P10K bracket not shown")
        rep = [100, 150, 200] if s == "i" else [gx(pair(f, "QM")["mu_star_lim"]), 50, 100]
        if [r["g"] for r in c["reporting"]] != rep:
            flag(f"{cid}: reporting points {[r['g'] for r in c['reporting']]} vs {rep}")
        for r in c["reporting"]:
            e_r = ev.get(r["g"])
            if e_r is not None and (e_r["ev"], e_r["p_pass_attempt"], e_r["p_any_payout"]) != (
                    r["ev"], r["p_pass_attempt"], r["p_any_payout"]):
                flag(f"{cid}: reporting row g {r['g']} differs from its evaluation")
        if 0 not in ev or ev[0]["p_pass_attempt"] != c["at_zero_edge"]["p_pass_attempt"] or \
                ev[0]["ev"] != c["at_zero_edge"]["ev"]:
            flag(f"{cid}: zero-edge stats not the g=0 evaluation")
    if c["threshold"]["status"] != "bisection, unconfirmed":
        flag(f"{cid}: status {c['threshold']['status']}")

# cost per attempt: zero edge identical in (i) and (ii); B0 = E.28
for f in FIRMS:
    for b in ("B0", *OTHER):
        for rho in ([None] if b == "B0" else RHOS):
            r = "rNA" if rho is None else f"r{rho:.2f}"
            ci, cii = cells.get(f"limit__primary__{f}__{b}__i__{r}"), cells.get(f"limit__primary__{f}__{b}__ii__{r}")
            if ci and cii and ci["status"] == "computed" and ci["cost_per_attempt_usd"] != cii["cost_per_attempt_usd"]:
                flag(f"cost per attempt (i) != (ii) at {f} {b} {r}")
            bump("cost_pairs_checked")

# ---------------------------------------------------------------- B3 law B (sensitivity) ----
import e29_basket as BB  # noqa: E402

inputs = BB.load_inputs()
for s, ms in (("i", cells["limit__b3_sens__topstep__B3__i__r0.50"]["mu_star"]), ("ii", None)):
    for rho in RHOS:
        pt = BB.cell_point_fn("topstep", "B3", s, rho, False, "b3_sens", ms, inputs)
        for g in (0, 50, 97, 150):
            la, lb = pt(g)
            mem_b = [m for m in members("topstep", "B3") if m["code"] != "MGC"]
            mb, sb = law(mem_b, mus_at(mem_b, s, g * 0.01, ms), rho, False)
            ma, sa = law(members("topstep", "B3"), mus_at(members("topstep", "B3"), s, g * 0.01, ms), rho, False)
            if abs(lb.m - mb) > 1e-9 or abs(lb.s - sb) > 1e-9 or abs(la.m - ma) > 1e-9 or abs(la.s - sa) > 1e-9:
                flag(f"b3_sens law at {s} {rho} {g}")
            bump("b3_sens_laws_checked")

# ---------------------------------------------------------------- best basket (section 6) ----
def thr_g(cid: str) -> float:
    c = cells.get(cid)
    if c is None or c["status"] != "computed" or c["threshold"]["g"] is None:
        return math.inf
    return c["threshold"]["g"]


best = {}
for f in FIRMS:
    rows = sorted(OTHER, key=lambda b: (thr_g(f"limit__primary__{f}__{b}__i__r0.50"),
                                        thr_g(f"limit__primary__{f}__{b}__ii__r0.50"), OTHER.index(b)))
    best[f] = rows[0]
    jb = next(x["best"] for x in J["best_basket"] if x["firm"] == f)
    if jb != best[f]:
        flag(f"best basket {f}: JSON {jb} vs rule {best[f]}")
    for s in ("i", "ii"):
        for rho in RHOS:
            if f"market__primary__{f}__{best[f]}__{s}__r{rho:.2f}" not in cells:
                flag(f"market cell missing for best basket {f} {best[f]} {s} {rho}")
    ki = [(b, thr_g(f"limit__primary__{f}__{b}__i__r0.50")) for b in OTHER]
    ki.sort(key=lambda t: t[1])
    best[f + "_margin_g"] = ki[1][1] - ki[0][1]
mk_bask = {(c["firm"], c["basket"]) for c in J["cells"] if c["case"] == "market" and c["basket"] != "B0"}
if mk_bask != {(f, best[f]) for f in FIRMS}:
    flag(f"market cells baskets {sorted(mk_bask)}")


# ---------------------------------------------------------------- beats (section 7) ----
def gpair(c: dict[str, Any]) -> tuple[float, float]:
    t = c["threshold"]["g"]
    p = c["x10K"]["g"]
    return (math.inf if t is None else t), (math.inf if p is None else p)


beats = {}
both_inf_x10 = []
for f in FIRMS:
    for s in ("i", "ii"):
        b0 = cells[f"limit__primary__{f}__B0__{s}__rNA"]
        t0, p0 = gpair(b0)
        for b in OTHER:
            for rho in RHOS:
                cid = f"limit__primary__{f}__{b}__{s}__r{rho:.2f}"
                c = cells[cid]
                if c["status"] != "computed":
                    beats[cid] = "-"
                    continue
                t, p = gpair(c)
                if math.isinf(p) and math.isinf(p0):
                    both_inf_x10.append(cid)
                beats[cid] = "yes" if (t <= t0 - 2 and p <= p0) else "no"


# ---------------------------------------------------------------- tables vs JSON ----
def fnum(s: str) -> Any:
    s = s.strip()
    if s in ("-", ""):
        return s
    try:
        return float(s)
    except ValueError:
        return s


firm = None
in_main = False
n_tab = n_tab_bad = n_flag = n_flag_bad = n_rep = 0
for line in TABLES:
    m = re.match(r"^### (\w+)$", line)
    if m:
        firm, in_main = m.group(1), True
        continue
    if line.startswith("Reporting points"):
        in_main = False
    if line.startswith("## "):
        firm, in_main = None, False
    if not firm or not line.startswith("| B"):
        continue
    cols = [x.strip() for x in line.strip("|").split("|")]
    if in_main and len(cols) == 11:
        b, rho, s = cols[0], cols[1], cols[2]
        r = "rNA" if rho == "-" else f"r{float(rho):.2f}"
        c = cells[f"limit__primary__{firm}__{b}__{s}__{r}"]
        b0 = cells[f"limit__primary__{firm}__B0__{s}__rNA"]
        exp = [round(c["S_usd"], 1), round(c["S_over_MLL"], 3)]
        got = [float(cols[3]), float(cols[4])]
        if c["status"] == "computed":
            t, p = c["threshold"]["value"], c["x10K"]["value"]
            exp += [t if isinstance(t, str) else round(t, 2), p if isinstance(p, str) else round(p, 2),
                    round(c["cost_per_attempt_usd"], 2)]
            got += [fnum(cols[5]), fnum(cols[7]), fnum(cols[9])]
            if b != "B0" and not isinstance(t, str) and not isinstance(b0["threshold"]["value"], str):
                tb = b0["threshold"]["value"]
                exp.append(round(t / tb - 1, 3) if s == "i" else round(t - tb, 2))
                got.append(float(cols[6]))
        n_tab += len(exp)
        bad = [(e, g) for e, g in zip(exp, got) if (e != g if isinstance(e, str) or isinstance(g, str)
                                                     else abs(e - g) > 1e-9)]
        if bad:
            n_tab_bad += 1
            flag(f"table {firm} {b} {rho} {s}: {bad}")
        if b != "B0":
            n_flag += 1
            if cols[10] != beats[c["cell_id"]]:
                n_flag_bad += 1
                flag(f"beats flag {c['cell_id']}: table {cols[10]} vs rule {beats[c['cell_id']]}")
    elif not in_main and len(cols) == 7:
        b, rho, s, x = cols[0], cols[1], cols[2], float(cols[3])
        r = "rNA" if rho == "-" else f"r{float(rho):.2f}"
        c = cells[f"limit__primary__{firm}__{b}__{s}__{r}"]
        rr = next(q for q in c["reporting"] if abs(q["x"] - x) < 1e-9)
        exp = [round(rr["p_pass_attempt"], 4), round(rr["p_any_payout"], 4), round(rr["ev"])]
        got = [float(cols[4]), float(cols[5]), float(cols[6])]
        n_rep += 3
        if any(abs(e - g) > 1e-9 for e, g in zip(exp, got)):
            flag(f"reporting table {firm} {b} {rho} {s} {x}: {exp} vs {got}")

yes = sorted(k for k, v in beats.items() if v == "yes")
out = {"provenance": prov, "counts": counts, "n_eval_rows_checked": n_eval_rows, "max_rel_err_M": max_rel_m,
       "max_rel_err_S": max_rel_s, "na_cells": na_cells, "alone": alone_rows, "best": best,
       "table_numbers_checked": n_tab, "table_rows_bad": n_tab_bad, "reporting_numbers_checked": n_rep,
       "beats_flags_checked": n_flag, "beats_flags_bad": n_flag_bad, "beats_yes": yes,
       "beats_yes_count": len(yes), "both_x10K_gt4": both_inf_x10, "issues": issues}
(HERE / "check_static.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k not in ("alone", "beats_yes", "na_cells")}, indent=0)[:3000])
