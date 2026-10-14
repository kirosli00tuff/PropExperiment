"""Stage E.21 return tables: exact markdown tables from the run's result files (read-only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

RUNS = Path("reports/stage_e21_runs")
TESTS = ("T1", "T2", "T3", "T4")
CASES = ("base", "stress", "slip150")
CASE_LABEL = {"base": "base (D8)", "stress": "D8 + 1 tick/side", "slip150": "1.5 x slippage"}


def load(test: str) -> dict:
    return json.loads((RUNS / f"{test}_result.json").read_text())


def fmt(x: float | None, nd: int = 3) -> str:
    return "n/a" if x is None else f"{x:.{nd}f}"


def verdict_table(verdict: dict) -> list[str]:
    out = ["| Test | n | mean (capital units/day) | sd | t | t NW | p (t) | p (NW) | p | Sharpe (ann.) | "
           "95% CI | Holm rejects | Sharpe >= 0.3 | Verdict |", "|" + "---|" * 14]
    for t in TESTS:
        v = verdict["tests"][t]
        r = load(t)["stats"]["base"]
        ci = v["sharpe_ci95"]
        out.append(f"| {t} | {v['n']} | {v['mean']:.6g} | {r['sd']:.6g} | {v['t']:.3f} | "
                   f"{v['t_nw']:.3f} | {v['p_t']:.4f} | {v['p_nw']:.4f} | {v['p']:.4f} | "
                   f"{v['sharpe_annualized']:.3f} | [{ci['lo']:.3f}, {ci['hi']:.3f}] | "
                   f"{v['checks']['holm_rejects']} | {v['checks']['sharpe_at_least_bar']} | "
                   f"{'PASS' if v['pass'] else 'FAIL'} |")
    return out


def cost_table() -> list[str]:
    out = ["| Test | Case | t | p | Sharpe | gross | costs | net | costs / gross |", "|" + "---|" * 9]
    for t in TESTS:
        r = load(t)
        for c in CASES:
            s, g = r["stats"][c], r.get("gross_costs", {}).get(c, {})
            out.append(f"| {t} | {CASE_LABEL[c]} | {s['t']:.3f} | {s['p']:.4f} | "
                       f"{s['sharpe_annualized']:.3f} | {fmt(g.get('gross'), 4)} | "
                       f"{fmt(g.get('costs'), 4)} | {fmt(g.get('net'), 4)} | "
                       f"{fmt(g.get('costs_share_of_gross'), 3)} |")
    return out


def year_table() -> list[str]:
    per = {t: load(t)["per_year_base"] for t in TESTS}
    years = sorted(set().union(*(set(p) for p in per.values())))
    out = ["| Year | " + " | ".join(f"{t} n | {t} Sharpe" for t in TESTS) + " |",
           "|" + "---|" * (1 + 2 * len(TESTS))]
    for y in years:
        cells = []
        for t in TESTS:
            e = per[t].get(y)
            cells += ([str(e["n"]), fmt(e.get("sharpe_annualized"), 2)] if e else ["", ""])
        out.append(f"| {y} | " + " | ".join(cells) + " |")
    return out


def root_table(test: str) -> list[str]:
    pr = load(test)["per_root"]
    out = [f"| Root ({test}) | contribution (sum, base) | own t | fills | gross | costs (base) |",
           "|" + "---|" * 6]
    for root, v in sorted(pr.items(), key=lambda kv: -kv[1]["contribution_base"]):
        out.append(f"| {root} | {v['contribution_base']:.4f} | {fmt(v.get('own_t'), 2)} | "
                   f"{v.get('fills')} | {fmt(v.get('gross'), 4)} | {fmt(v['costs']['base'], 4)} |")
    return out


def exclusion_lines(test: str) -> list[str]:
    ex = load(test)["exclusions"]
    items = sorted(((k, v) for k, v in ex.items() if isinstance(v, (int, float))),
                   key=lambda kv: -kv[1])
    return [f"- {test}: " + "; ".join(f"{k} {v}" for k, v in items)]


def main() -> int:
    verdict = json.loads((RUNS / "verdict.json").read_text())
    parts = ["### Verdict table (base case; Holm step-down at family alpha 0.025; N 532)", "",
             *verdict_table(verdict), "", "### Cost cases (reported; the prompt's stress case is "
             "1.5 x slippage)", "", *cost_table(), "", "### Per calendar year (base case)", "",
             *year_table(), ""]
    for t in ("T1", "T2", "T3"):
        parts += [f"### Per root, {t} (base case)", "", *root_table(t), ""]
    parts += ["### Fills by kind", ""]
    for t in TESTS:
        parts.append(f"- {t}: " + json.dumps(load(t).get("fills_by_kind", {})))
    parts += ["", "### Exclusions and counters (all reasons, per test)", ""]
    for t in TESTS:
        parts += exclusion_lines(t)
    parts += ["", "### Fill diagnostics (T1 notes)", "",
              "```", json.dumps(load("T1")["notes"].get("fill_diagnostics"), indent=1)[:3000], "```"]
    Path(sys.argv[1]).write_text("\n".join(parts) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
