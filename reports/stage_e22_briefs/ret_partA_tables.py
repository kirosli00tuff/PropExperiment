"""Stage E.22 return: render Part A's tables from the four verdict JSONs (reports/stage_e22_k{5,8,3,6}_verdict.json).

Usage: python3 reports/stage_e22_briefs/ret_partA_tables.py > reports/stage_e22_briefs/ret_partA_tables.md
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLUSTERS = ("K5", "K8", "K3", "K6")


def f(x, nd=4):
    return "-" if x is None else (f"{x:+.{nd}f}" if isinstance(x, float) else str(x))


def main() -> None:
    out = []
    summary = ["| Cluster | Statement | Tier A trial | Status | theta_hat | UCB95 | eps_X | Trips | Holm p (K = 5; alpha 0.01) | t | DSR (N 533) | PBO | Chain |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in CLUSTERS:
        p = ROOT / f"reports/stage_e22_{k.lower()}_verdict.json"
        d = json.loads(p.read_bytes())
        ec = d["edge_chain"]
        rows = {r["member"]: r for r in d["trials"]}
        for h in ec["holm"]["rows"]:
            r = rows[h["member"]]
            tr = ec["trials"].get(h["member"], {})
            summary.append(f"| {k} | {d['statement']['verdict']} | {h['member']} | {r.get('status')} | {f(r.get('theta_hat'))} | "
                           f"{f(r.get('ucb95'))} | {f(r.get('eps_ticks'), 0) if r.get('eps_ticks') is not None else '-'} | "
                           f"{r.get('n_trips', '-')} | {h['p_value']:.4f} ({'reject' if h['reject'] else 'not rejected'}) | "
                           f"{f(tr.get('t_stat'), 3)} | {('%.2e' % tr['dsr']) if tr.get('dsr') is not None else tr.get('dsr_undefined')} | "
                           f"{f(tr.get('pbo'), 3)} | {tr.get('verdict')} (first failing: {tr.get('first_failing_step')}) |")
        out += ["", f"#### {k} (verdict sha256 {hashlib.sha256(p.read_bytes()).hexdigest()[:12]}...; statement: "
                f"{d['statement']['verdict']})", "",
                "| Ord | Trial | Tier | Status | Days | Trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | p_upper |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in d["trials"]:
            out.append(f"| {r['ordinal']} | {r['member']} | {r['tier']} | {r['status']} | {r.get('n_days', '-')} | "
                       f"{r.get('n_trips', '-')} | {f(r.get('theta_hat'))} | {f(r.get('ucb95'))} | "
                       f"{f(r.get('se_boot')) if r.get('se_boot') is not None else '-'} | "
                       f"{r.get('eps_ticks', '-')} | {f(r.get('null_power'), 3)} | {f(r.get('p_upper'), 4)} |")
        st = d["statement"]
        out += ["", f"Covered: {len(st.get('covered', []))}; not covered: "
                + "; ".join(f"{x['member']} ({x['reason']})" for x in st.get("not_covered", []))
                + "; blocking: " + ("; ".join(f"{b['member']} ({b['status']}: {', '.join(b['reasons'])})" for b in st.get("blocking", [])) or "none")
                + "; null by inactivity: " + (", ".join(st.get("null_by_inactivity", [])) or "none") + ".",
                f"Edge chain: Holm K = {ec['holm']['k']} (m = {ec['holm']['m']}); descriptive K = 9: "
                + ", ".join(f"{r['member']} p {r['p_value']:.4f} vs {r['threshold']:.5f}" for r in ec['holm_descriptive_k9']['rows'])
                + f"; DSR variance {ec['dsr']['sharpe_variance']:.6g} over {len(ec['dsr']['variance_over'])} series;"
                + f" PBO {f(ec['pbo'].get('pbo'), 4)} over {len(ec['pbo'].get('over') or [])} series."]
    print("\n".join(summary + out))


if __name__ == "__main__":
    main()
