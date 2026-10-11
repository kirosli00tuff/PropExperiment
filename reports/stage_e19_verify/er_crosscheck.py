"""EconReviewer Phase B: per-path cross-check of my simulator against prop_econ on IDENTICAL shocks.

Separates model differences from Monte Carlo noise: prop_econ's scalar reference (funnel.run_attempt /
run_xfa) and vectorized code (vec.simulate_attempts / simulate_xfas, assemble.assemble_cycles) are run on
MY ShockSet (er_sim.draw_shocks) and compared row by row with my er_sim results; cycles are compared on the
same index draws against assemble.assemble_cycle (scalar) and assemble_cycles (vectorized).
Writes crosscheck.json.
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import fields
from pathlib import Path

import numpy as np

os.nice(10)
REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "reports" / "stage_e19_verify"))
os.environ.setdefault("ER_N_PATHS", "20000")
import er_sim as E  # noqa: E402  (my simulator; its module load reads only my own files)
from prop_econ.assemble import assemble_cycle, assemble_cycles, fee_terms  # noqa: E402
from prop_econ.funnel import ATTEMPT_PASS, Policy, run_attempt, run_xfa  # noqa: E402
from prop_econ.rules import load_rules, size_rules  # noqa: E402
from prop_econ.types import ProductSpec, ShockSet  # noqa: E402
from prop_econ.vec import simulate_attempts, simulate_xfas  # noqa: E402

OUT = REPO / "reports" / "stage_e19_verify"
BOOK = load_rules(REPO / "reports" / "stage_e19_rules.json")
N_SCALAR = int(os.environ.get("ER_N_SCALAR", "1500"))
N_CYC_SCALAR = 400
report: dict = {"n_paths": E.N_PATHS, "n_scalar_rows": N_SCALAR, "checks": []}


def specs(prods: dict) -> tuple[ProductSpec, ...]:
    out = []
    for i, r in enumerate(E.ROOTS):
        hm = bool(prods["has_micro"][i])
        out.append(ProductSpec(r, float(prods["sig_full"][i]), float(prods["rt_full"][i]),
                               E.MICRO[r] if hm else None,
                               float(prods["sig_micro"][i]) if hm else None,
                               float(prods["rt_micro"][i]) if hm else None))
    return tuple(out)


def add(name: str, ok: bool, **kw) -> None:
    report["checks"].append({"name": name, "ok": bool(ok), **kw})
    print(("ok  " if ok else "BAD ") + name, {k: v for k, v in kw.items() if k != "detail"}, flush=True)


def main() -> None:
    t0 = time.time()
    prods = E.products()
    sp = specs(prods)
    za, wa, pa = E.draw_shocks(E.N_PATHS, E.N_DAYS, E.SEED_SHOCKS_ATTEMPT, prods)
    zx, wx, px = E.draw_shocks(E.N_PATHS, E.N_DAYS, E.SEED_SHOCKS_XFA, prods)
    sa = ShockSet(za, wa, pa.astype(np.int16), sp)
    sx = ShockSet(zx, wx, px.astype(np.int16), sp)
    configs = [("50K", "zero_k1", "zero", 0.0, 1, 0.25), ("150K", "sharpe_0.5", "sharpe", 0.5, 1, 0.15),
               ("100K", "zero_k1", "zero", 0.0, 1, 0.05)]
    for size_name, edge_name, edge, S, k, f in configs:
        size = E.RULES["sizes"][size_name]
        rules = size_rules(BOOK, size_name)
        tag = f"{size_name} {edge_name} f={f}"
        # ---- attempts: mine (vectorized) vs their vec vs their scalar, same shocks
        mine = E.run_attempts(za, wa, pa, size, f, edge, S, k, prods)
        pol = Policy(f=f, edge=edge, sharpe=S, k=k)
        theirs = simulate_attempts(sa, rules, pol)
        same_pass = np.array_equal(mine["passed"], theirs.passed)
        same_len = np.array_equal(mine["length"], theirs.length.astype(np.int64))
        add(f"attempts vec {tag}: passed equal", same_pass, n=E.N_PATHS, mine_p=float(mine["passed"].mean()),
            theirs_p=float(theirs.passed.mean()), n_diff_pass=int((mine["passed"] != theirs.passed).sum()))
        add(f"attempts vec {tag}: length equal", same_len, n_diff=int((mine["length"] != theirs.length).sum()),
            mine_mean=float(mine["length"].mean()), theirs_mean=float(theirs.length.mean()))
        sc_pass, sc_len = [], []
        for r in range(N_SCALAR):
            o = run_attempt(sa, r, rules, pol)
            sc_pass.append(o.passed); sc_len.append(o.length)
        sc_pass, sc_len = np.array(sc_pass), np.array(sc_len)
        add(f"attempts scalar(theirs) vs mine {tag}", np.array_equal(sc_pass, mine["passed"][:N_SCALAR])
            and np.array_equal(sc_len, mine["length"][:N_SCALAR]),
            n_diff_pass=int((sc_pass != mine["passed"][:N_SCALAR]).sum()),
            n_diff_len=int((sc_len != mine["length"][:N_SCALAR]).sum()))
        add(f"attempts scalar(theirs) vs vec(theirs) {tag}", np.array_equal(sc_pass, theirs.passed[:N_SCALAR])
            and np.array_equal(sc_len, theirs.length[:N_SCALAR]),
            n_diff_pass=int((sc_pass != theirs.passed[:N_SCALAR]).sum()))
        # ---- XFAs
        for path in E.PATHS:
            mx = E.run_xfas(zx, wx, px, size, path, f, edge, S, k, prods)
            polx = Policy(f=f, edge=edge, sharpe=S, k=k, payout_path=path, max_payouts=192)
            tx = simulate_xfas(sx, rules, polx)
            d_gross = np.abs(mx["gross"] - tx.total_gross)
            add(f"xfa vec {tag} {path}: n_payouts equal", np.array_equal(mx["n_pay"], tx.n_payouts.astype(np.int64)),
                n_diff=int((mx["n_pay"] != tx.n_payouts).sum()), mine_mean=float(mx["n_pay"].mean()),
                theirs_mean=float(tx.n_payouts.mean()))
            add(f"xfa vec {tag} {path}: total_gross to the cent", bool(np.all(d_gross < 0.005)),
                max_abs_diff=float(d_gross.max()), mine_mean=float(mx["gross"].mean()),
                theirs_mean=float(tx.total_gross.mean()))
            add(f"xfa vec {tag} {path}: end_day equal", np.array_equal(mx["end_day"], tx.end_day.astype(np.int64)),
                n_diff=int((mx["end_day"] != tx.end_day).sum()))
            fd_mine = np.where(mx["first_day"] > 0, mx["first_day"] - 1, -1)  # mine 1-based -> their 0-based index
            add(f"xfa vec {tag} {path}: first_payout_day equal (index shift)", np.array_equal(fd_mine, tx.first_payout_day),
                n_diff=int((fd_mine != tx.first_payout_day).sum()))
            sc = [run_xfa(sx, r, rules, polx) for r in range(N_SCALAR)]
            sc_n = np.array([o.n_payouts for o in sc]); sc_g = np.array([o.total_gross for o in sc])
            sc_e = np.array([o.end_day for o in sc])
            add(f"xfa scalar(theirs) vs mine {tag} {path}", np.array_equal(sc_n, mx["n_pay"][:N_SCALAR])
                and np.all(np.abs(sc_g - mx["gross"][:N_SCALAR]) < 0.005) and np.array_equal(sc_e, mx["end_day"][:N_SCALAR]),
                n_diff_n=int((sc_n != mx["n_pay"][:N_SCALAR]).sum()),
                max_gross_diff=float(np.abs(sc_g - mx["gross"][:N_SCALAR]).max()))
            add(f"xfa scalar(theirs) vs vec(theirs) {tag} {path}", np.array_equal(sc_n, tx.n_payouts[:N_SCALAR])
                and np.all(np.abs(sc_g - tx.total_gross[:N_SCALAR]) < 0.005),
                n_diff_n=int((sc_n != tx.n_payouts[:N_SCALAR]).sum()))
            # ---- cycles on identical pools and index draws
            terms = fee_terms(rules, pricing_path="standard", dll_chosen=False, b2f_on=False)
            rng = np.random.Generator(np.random.PCG64(E.SEED_CYCLES))
            cyc_mine = E.assemble_cycles(mine, mx, size, rng, E.N_CYCLES)
            rng2 = np.random.Generator(np.random.PCG64(E.SEED_CYCLES))
            att_idx = rng2.integers(0, E.N_PATHS, size=(E.N_CYCLES, 60))
            xidx = rng2.integers(0, E.N_PATHS, size=E.N_CYCLES)
            batch = assemble_cycles(att_idx, np.column_stack([xidx] * (1 + terms.b2f_max)), theirs, tx, terms)
            d_net = np.abs(cyc_mine["net_noapi"] - batch.net)
            add(f"cycles vec(theirs) vs mine {tag} {path}: net ex API to the cent", bool(np.all(d_net < 0.005)),
                max_abs_diff=float(d_net.max()), mine_mean=float(cyc_mine["net_noapi"].mean()),
                theirs_mean=float(batch.net.mean()),
                purchases_equal=bool(np.array_equal(cyc_mine["purchases"], batch.purchases)),
                end_equal=bool(np.array_equal(cyc_mine["cycle_end"], batch.end)),
                mine_purch=float(cyc_mine["purchases"].mean()), theirs_purch=float(batch.purchases.mean()))
            sc_nets, sc_purch, sc_end = [], [], []
            for c in range(N_CYC_SCALAR):
                cy = assemble_cycle(att_idx[c], [xidx[c]] * (1 + terms.b2f_max), theirs, tx, terms)
                sc_nets.append(cy.net); sc_purch.append(cy.purchases); sc_end.append(cy.end)
            sc_nets = np.array(sc_nets)
            add(f"cycles scalar(theirs) vs mine {tag} {path}", bool(np.all(np.abs(sc_nets - cyc_mine["net_noapi"][:N_CYC_SCALAR]) < 0.005))
                and np.array_equal(np.array(sc_purch), cyc_mine["purchases"][:N_CYC_SCALAR])
                and np.array_equal(np.array(sc_end), cyc_mine["cycle_end"][:N_CYC_SCALAR]),
                max_abs_diff=float(np.abs(sc_nets - cyc_mine["net_noapi"][:N_CYC_SCALAR]).max()))
            add(f"cycles scalar(theirs) vs vec(theirs) {tag} {path}", bool(np.all(np.abs(sc_nets - batch.net[:N_CYC_SCALAR]) < 0.005))
                and np.array_equal(np.array(sc_purch), batch.purchases[:N_CYC_SCALAR]),
                max_abs_diff=float(np.abs(sc_nets - batch.net[:N_CYC_SCALAR]).max()))
    report["cyclebatch_fields"] = [f.name for f in fields(batch)]
    report["elapsed_s"] = round(time.time() - t0, 1)
    report["all_ok"] = all(c["ok"] for c in report["checks"])
    (OUT / "crosscheck.json").write_text(json.dumps(report, indent=1, default=str))
    print("all_ok", report["all_ok"], "elapsed", report["elapsed_s"])


if __name__ == "__main__":
    main()
