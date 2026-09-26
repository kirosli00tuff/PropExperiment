"""Markdown beside reports/stage_e2a_vehicles.json (Stage E.2a Task 9, phase 2)."""

from __future__ import annotations

from pathlib import Path


def _exposure_row(e: dict) -> str:
    vehicle = e["vehicle"] or "-"
    q = e["q_c"] if e["q_c"] is not None else "-"
    eps = e["eps_X_net_ticks"] if e["eps_X_net_ticks"] is not None else "-"
    return (f"| {e['exposure']} | {e['cluster']} | {', '.join(e['admissible'])} | "
            f"{', '.join(e['candidates']) or 'none'} | {', '.join(e['preferred']) or 'none'} | "
            f"{e['status']} | {vehicle} | {q} | {eps} |")


def _contract_row(p: str, c: dict) -> str:
    note = "R7" if c["r7_non_candidate"] else ""
    return (f"| {p} | {c['exposure']} | {c['r_c_usd']:.2f} | {c['q_c']} | {c['rho_c']:.4f} | "
            f"{c['commission_rt_usd']:.2f} | {c['one_side_slippage_ticks']:.4f} | "
            f"{c['one_side_slippage_usd']:.4f} | {c['round_turn_cost_usd_per_contract']:.4f} | "
            f"{c['cost_per_dollar_of_risk']:.6f} | {note} |")


def write_choice_md(result: dict, path: Path) -> None:
    exposures, contracts = result["exposures"], result["contracts"]
    questions = [e for e in exposures if e["status"] == "question"]
    lines = [
        "# Stage E.2a Task 9, phase 2: the vehicle per exposure",
        "",
        f"Generated {result['generated_pdt']} by screening/vehicles_choice.py "
        "(VehicleCoder-OpusXHigh). Rule: docs/STAGE_E_DESIGN.md D2 read as R1-R12 of "
        "reports/stage_e2a_vehicle_rule_readings.md. Full data: reports/stage_e2a_vehicles.json. "
        "Nothing here is chosen by judgment: each result follows from R7-R12 and the numbers "
        "shown; a case the readings do not settle is listed as a question.",
        "",
        "Inputs: r_c, q_c, rho_c from reports/stage_e2a_vehicle_sizes.json (phase 1; re-derived "
        f"from the parquets with the current code: {result['phase1_reproduced']['differences']} "
        "differences); costs from the frozen D8 table reports/stage_e2a_costs.json (sha256 "
        f"{result['inputs_sha256']['reports/stage_e2a_costs.json']}). "
        + result["stale_hash_note"],
        "",
        "Lead answers applied: " + "; ".join(f"{k} {t}" for k, t in
                                             result["lead_answers"].items()) + ".",
        "",
        "R8: cost per dollar of risk = (commission_c + 2 x one-side slippage_c) / r_c, the "
        "one-side slippage being the minute-weighted mean over the day session [O_X, C_X) of "
        "D8's per-side cost at q_c, (buy side + sell side) / 2 per 30-minute bucket (s_b plus "
        "the mean of the two sides' depth terms). R9: candidates rho_c <= 2.0 less R7 (M6E, "
        "M6A); preferred rho_c >= 0.5; lowest R8 cost among the preferred; an exact tie to the "
        "higher D1 ADV; SIL (MHG) is the vehicle whenever it is a candidate. R10: candidates "
        "but none preferred: the cheapest candidate at its cap, 'undersized'. R11: no "
        "candidate: not traded in Stage E. R12: eps_X = floor($85.00 / (q_c x tick value)).",
        "",
        "## Result per exposure",
        "",
        "| Exposure | Cluster | Admissible | Candidates | Preferred | Status | Vehicle | q_c | "
        "eps_X (net ticks) |",
        "|---|---|---|---|---|---|---|---|---|",
        *(_exposure_row(e) for e in exposures),
        "",
        "Counts: " + "; ".join(f"{k} {len(v)}" for k, v in result["counts"]["by_status"].items())
        + ".",
        "",
        "## Per contract (r_c, q_c, rho_c from phase 1; costs at q_c)",
        "",
        "| Contract | Exposure | r_c (USD) | q_c | rho_c | Commission RT (USD) | One-side "
        "(ticks) | One-side (USD) | Round turn (USD) | Cost per $ of risk | Note |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
        *(_contract_row(p, c) for p, c in contracts.items()),
        "",
        "## Arithmetic per exposure",
        "",
    ]
    for e in exposures:
        head = f"{e['status']}" + (f": {e['vehicle']}" if e["vehicle"] else "")
        lines += [f"### {e['exposure']} ({e['cluster']}): {head}", ""]
        lines += [f"- {a}" for a in e["arithmetic"]]
        lines.append("")
    lines += ["## Questions for the lead", ""]
    lines += ([f"- {e['exposure']}: {e['deciding']}" for e in questions]
              or ["- None: R1-R12 settle every exposure (no cost tie, no SIL/MHG corner case)."])
    changed = result["calendar_modules_changed_since_phase1"]
    lines += ["", "## Input and code sha256", ""]
    if changed:
        lines.append(f"Calendar modules changed since phase 1 (current hashes below): {changed}.")
        lines.append("")
    lines += [f"- {k}: {h}" for k, h in result["inputs_sha256"].items()]
    lines += [f"- {k}: {h}" for k, h in result["code_sha256"].items()]
    lines.append("")
    path.write_text("\n".join(lines))
