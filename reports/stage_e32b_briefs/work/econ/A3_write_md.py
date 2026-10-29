"""Compose reports/stage_e28_briefs/A3_econ.md from A3_econ.json, the generated tables and the fixed prose below.
Usage: uv run python A3_write_md.py
"""

from __future__ import annotations

if __name__ == "__main__":  # E.32b guard (added to the copy only)
    raise SystemExit("E.32b copy of an E.28 script: reference only (it writes E.28 paths or regenerates "
                     "A3_inputs.json); do not run")

import json
from collections import Counter
from pathlib import Path
from typing import Any

WORK = Path(__file__).resolve().parent
REPO = WORK.parents[3]
DOC = REPO / "reports" / "stage_e28_briefs" / "A3_econ.json"
OUT = REPO / "reports" / "stage_e28_briefs" / "A3_econ.md"
FIRMS = ("topstep", "lucid", "tradeify", "mffu", "bulenox")


def _f(x: Any, nd: int = 2) -> str:
    if x is None:
        return "-"
    if isinstance(x, str):
        return x
    return f"{x:,.{nd}f}"


def mapping_md(doc: dict[str, Any]) -> list[str]:
    out = []
    for firm in FIRMS:
        fm = doc["firm_models"][firm]
        fees = fm["fees"]
        out += [f"### 3.{FIRMS.index(firm) + 1} {firm}: {fm['plan']}", "",
                f"Fees in the model: start {_f(fees['start_usd'])}; "
                + (f"rebill {_f(fees['rebill_usd'])} every {fees['rebill_period_trading_days']} trading days "
                   f"(credit {fees['rebill_adds_reset_credit']}, reset pushes rebill {fees['reset_pushes_rebill']}); "
                   if fees["rebill_usd"] else "no rebill; ")
                + f"reset or re-purchase {_f(fees['reset_usd'])}; activation {_f(fees['activation_usd'])}; "
                f"trader split {fees['split']:.0%}; API {_f(fm['api_monthly_usd'])} per started "
                f"{fm['api_period_trading_days']}-trading-day period; attempt cap {fees['attempt_cap']}; "
                f"evaluation horizon {fm['attempt_max_days']} trading days; drawdown trailing "
                f"{fm['evaluation_trailing']} in the evaluation.", "",
                "| rule | firm value (A2 record) | model form | kind |", "|---|---|---|---|"]
        out += [f"| {m['rule']} | {m['firm_value']} | {m['model_form']} | {m['kind']} |" for m in fm["mapping"]]
        out.append("")
    return out


def inputs_md(doc: dict[str, Any]) -> list[str]:
    used = sorted({p["code"] for p in doc["pairs"]})
    out = ["| code | tick | v USD | sigma_1m ticks | R_d ticks | source of sigma_1m and R_d | S_rt | ADV owned (A0 v_0) "
           "| A1 published ADV fields |", "|---|---|---|---|---|---|---|---|---|"]
    for c in used:
        r = doc["candidates"][c]
        adv = r["ADV_owned_v0"]["value"] if r["ADV_owned_v0"] else None
        pub = ", ".join(r["ADV_published_A1"].keys()) or "-"
        srt = f"1 ({r['S_rt_status']}" + (f"; mean {r['S_rt_mean_sourced']:g}" if r["S_rt_mean_sourced"] else "") + ")"
        out.append(f"| {c} | {r['tick_size']} {r['tick_unit']} | {_f(r['v_usd'], 4)} | {_f(r['sigma_1m_ticks'], 3)} | "
                   f"{_f(r['R_d_ticks'], 1)} | {r['magnitude_source']} | {srt} | {_f(adv, 0)} | {pub} |")
    return out


def sens_md(doc: dict[str, Any]) -> list[str]:
    out = ["| firm | code | mu*_lim | ex-API mu*_lim | alt fee USD | mu*_lim at alt fee | S_rt mean | mu*_mkt at mean |",
           "|---|---|---|---|---|---|---|---|"]
    for p in doc["pairs"]:
        s = p.get("sensitivities") or {}
        if not s:
            continue
        alt = s.get("alt_fee") or {}
        sm = s.get("S_rt_mean") or {}
        out.append(f"| {p['firm']} | {p['code']} | {_f(p['mu_star_lim'])} | {_f(s.get('mu_star_lim_ex_api'))} | "
                   f"{_f(alt.get('F_rt_usd'))} | {_f(alt.get('mu_star_lim'))} | {_f(sm.get('S_rt_ticks'), 3)} | "
                   f"{_f(sm.get('mu_star_mkt'))} |")
    return out


def opt2_md(doc: dict[str, Any]) -> list[str]:
    o1 = {p["code"]: p for p in doc["pairs"] if p["firm"] == "bulenox"}
    out = ["| code | Option 1 mu*_lim / mu*_mkt / mu10K | Option 2 mu*_lim / mu*_mkt / mu10K |", "|---|---|---|"]
    for r in sorted(doc["sensitivity_bulenox_option2"], key=lambda r: r["code"]):
        a = o1.get(r["code"], {})
        out.append(f"| {r['code']} | {_f(a.get('mu_star_lim'))} / {_f(a.get('mu_star_mkt'))} / {_f(a.get('mu10K'))} "
                   f"| {_f(r['mu_star_lim'])} / {_f(r['mu_star_mkt'])} / {_f(r['mu10K'])} |")
    return out


def mono_md(doc: dict[str, Any]) -> list[str]:
    m = doc["checks"]["monotone_scan"]
    if not m:
        return ["(not run)"]
    out = ["| firm | code | EV per cycle at mu = 0, 0.25, ..., 4 (USD, limit case) | EV nondecreasing | "
           "P10K nondecreasing |", "|---|---|---|---|---|"]
    for r in m["rows"]:
        out.append(f"| {r['firm']} | {r['code']} | {' '.join(f'{x:,.0f}' for x in r['ev'])} | "
                   f"{r['ev_nondecreasing']} | {r['p10k_nondecreasing']} |")
    return out


def summary_counts(doc: dict[str, Any]) -> list[str]:
    out = ["| firm | pairs | computed | mu*_lim <= 4 | mu*_mkt <= 4 | mu10K <= 4 | not computed (sigma unknown) |",
           "|---|---|---|---|---|---|---|"]
    for firm in FIRMS:
        ps = [p for p in doc["pairs"] if p["firm"] == firm]
        comp = [p for p in ps if p.get("computed")]
        num = lambda k: sum(1 for p in comp if isinstance(p[k], (int, float)))  # noqa: E731
        out.append(f"| {firm} | {len(ps)} | {len(comp)} | {num('mu_star_lim')} | {num('mu_star_mkt')} | "
                   f"{num('mu10K')} | {', '.join(p['code'] for p in ps if not p.get('computed')) or '-'} |")
    return out


def _mono_text(txt: str, doc: dict[str, Any], viol: Counter) -> str:
    g = doc["checks"]["grid_confirmation_summary"]
    grid = (f"{g['pairs_all_thresholds_confirmed']} of {g['pairs_checked']} pairs confirmed on every threshold, "
            f"{len(g['pairs_with_correction'])} corrected; stored point recomputed bit-for-bit in {g['repro_equal']} "
            f"of {g['repro_checked']} pairs; {g['points_evaluated_total']:,} lattice points in all, "
            f"{g['new_evaluations_total']:,} of them new")
    return (txt.replace("{VIOL}", ", ".join(f"{k} {v}" for k, v in sorted(viol.items())) or "none")
            .replace("{NPTS}", f"{g['points_evaluated_total']:,}")
            .replace("{NDROP}", str(g["pairs_with_ev_decreasing_steps"])).replace("{GRID}", grid))


def main() -> int:
    doc = json.loads(DOC.read_text())
    import A3_prose

    prose = A3_prose.PROSE
    tables = (WORK / "A3_tables.md").read_text()
    viol = Counter(p["firm"] for p in doc["pairs"] if p.get("monotone_violations"))
    parts = [prose["head"], "", "## 1. Summary", "", *summary_counts(doc), "", prose["summary"], "",
             prose["method"], "", "## 3. The 50K plans mapped onto the funnel", "", prose["mapping_intro"], "",
             *mapping_md(doc), prose["conservative"], "", "## 5. Inputs per candidate", "", prose["inputs"], "",
             *inputs_md(doc), "", "## 6. Results per pair (limit case unless named; no scores)", "",
             prose["results_intro"], "", tables, "", "## 7. Sensitivities", "", prose["sens"], "", *sens_md(doc), "",
             "Bulenox Option 2 (EOD drawdown, DLL 1,100) beside the spec's Option 1:", "", *opt2_md(doc), "",
             "## 8. Tests and checks", "", prose["tests"], "", "Monotonicity scan:", "", *mono_md(doc), "",
             _mono_text(prose["monotone"], doc, viol),
             "", prose["runtime"], "", prose["choices"], ""]
    OUT.write_text("\n".join(parts))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
