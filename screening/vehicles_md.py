"""Markdown beside reports/stage_e2a_vehicle_sizes.json (Stage E.2a Task 9, phase 1)."""

from __future__ import annotations

from pathlib import Path

CAUSE_HEAD = (("roll_blackout", "roll"), ("vendor_degraded", "degraded"),
              ("closure_or_early_close_at_or_before_C", "early close <= C"),
              ("no_bar_in_window", "no bar"))


def _row(product: str, c: dict) -> str:
    head = f"| {c['exposure']} | {product} | {c['O_X']}-{c['C_X']} |"
    if c["status"] != "computed":
        return head + f" pending | | | | | | | | cap {c['cap_c']} | | | {c['reason']} |"
    n = c["dates_excluded_count_by_cause"]
    causes = " | ".join(str(n[k]) for k, _ in CAUSE_HEAD)
    cap = f"{c['cap_c']} ({c['cap_source']})"
    note = "R7: not a candidate" if c["r7_non_candidate"] else ""
    return (f"{head} {c['trade_dates_in_parquet']} | {c['dates_used_count']} | {causes} | "
            f"{c['exact_bar_missing']['either_count']} | {c['r_c_usd']:.2f} | {cap} | "
            f"{c['q_c']} | {c['rho_c']:.4f} | {note} |")


def _checks(contracts: dict) -> list[str]:
    done = {p: c for p, c in contracts.items() if c["status"] == "computed"}
    scaled = sorted(p for p, c in done.items() if c["vendor_price_factor"] != 1)
    off_list = {p: c["input_checks"]["trade_dates_off_list_with_flagged_bars_outside_window"]
                for p, c in done.items()}
    off_dates = sorted({d for ds in off_list.values() for d in ds})
    missing_cal = {p: c["calendar_trade_dates_without_bars"] for p, c in done.items()
                   if c["calendar_trade_dates_without_bars"]}
    foreign = {p: c["other_trade_date_bars_in_window"] for p, c in done.items()
               if c["other_trade_date_bars_in_window"]}
    lines = [
        f"- Vendor tick: every price of all {len(done)} parquets lies on the vendor-unit grid, "
        "and at least 10% lie off the 2x and the 10x grid (so the tick is not too fine); the "
        "scale agrees with BarsCoder's grid probe and CostCoder's vendor_price_factor for every "
        f"contract. 100 x the E.0 tick: {', '.join(scaled)}.",
        "- Roll blackout: BarsCoder's recorded list (L-8) equals the parquet metadata and a "
        "recomputation from the group calendar (splice trade date and the 2 group trade dates "
        "before it); the is_roll_session flag marks exactly the splice trade dates.",
        "- Vendor-degraded: the list (research trade dates on Databento's degraded UTC-date "
        "list, as BarsCoder records it) equals the parquet metadata, and inside every "
        "[O_X, C_X) window the per-bar flag agrees with it (0 mismatches).",
        f"- Trade dates off the list with a flagged bar outside the window: {off_dates or 'none'}"
        " (question Q-2 below).",
        f"- Calendar trade dates with no bar in the parquet: {missing_cal or 'none'}.",
        f"- Bars of another trade date inside a window (L-10): {foreign or 'none'}.",
    ]
    flagged = {p: c["bars_json_calendar_check"] for p, c in done.items()
               if c["bars_json_calendar_check"]["passed"] is False}
    cells = [f"{p} {len(k['discrepancy_days'])}/{len(k['discrepancy_days_used_for_r_c'])}"
             for p, k in flagged.items()]
    lines.append(
        "- BarsCoder's step-4b calendar check (reports/stage_e2a_bars.json) lists days on "
        f"{len(flagged)} contracts (days listed / of which used for r_c): {'; '.join(cells)}. "
        "Nearly all are 'early stop' findings: no trade in the last minutes before C_X on a "
        "thin contract (BarsCoder's thin-trading class; lead rulings L-5 and L-7 for the "
        "named days; MBT's 14 are the monthly-expiry Fridays, all inside its roll blackout). "
        "Every such day that r_c uses is in that contract's R3 close-bar-missing list (the "
        "last traded minute before C_X was used); the rest ('listed entry not observed') "
        "concern halts after C_X or dates R2 excludes. Kinds and full lists per contract: "
        "bars_json_calendar_check in the JSON.")
    return lines


def _off_list_used(contracts: dict) -> str:
    counts = {p: len(c["degraded_off_list_dates_used_for_r_c"]) for p, c in contracts.items()
              if c["status"] == "computed" and c["degraded_off_list_dates_used_for_r_c"]}
    if not counts:
        return "on no contract"
    return (f"on {len(counts)} contracts, {min(counts.values())} to {max(counts.values())} "
            "dates each; lists per contract: degraded_off_list_dates_used_for_r_c in the JSON")


def _off_list(contracts: dict) -> list[str]:
    done = [c for c in contracts.values() if c["status"] == "computed"]
    key = "trade_dates_off_list_with_flagged_bars_outside_window"
    return sorted({d for c in done for d in c["input_checks"][key]})


def write_md(result: dict, path: Path) -> None:
    contracts = result["contracts"]
    lines = [
        "# Stage E.2a Task 9, phase 1: r_c, q_c and rho_c per admissible contract",
        "",
        f"Generated {result['generated_pdt']} by screening/vehicles_run.py "
        "(VehicleCoder-OpusXHigh). Rule: docs/STAGE_E_DESIGN.md D2 read as R1-R6 of "
        "reports/stage_e2a_vehicle_rule_readings.md (sha256 checked). Full data, date lists "
        "and input hashes: reports/stage_e2a_vehicle_sizes.json.",
        "",
        "r_c = mean over the R2 dates of |close(C_X - 1 min) - open(O_X)| in ticks of the "
        "vendor's price units x tick_value_usd (R3, R4); q_c = min(cap_c, max(1, round-half-up("
        "R*/r_c))), R* = $360.68; rho_c = q_c r_c / R* (R5, R6). Excluded-date columns count "
        "each cause separately (a date can have two causes); 'exact bar missing' counts used "
        "dates where the bar at O_X or at C_X - 1 min was missing and the nearest traded "
        "minute inside the window was used (R3).",
        "",
        "Rulings applied: " + "; ".join(f"{k} {t}" for k, t in result["rulings_applied"].items())
        + ".",
        "",
        "| Exposure | Contract | O-C (CT) | Trade dates | Used | "
        + " | ".join(h for _, h in CAUSE_HEAD)
        + " | Exact bar missing | r_c (USD) | cap_c (source) | q_c | rho_c | Note |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        *(_row(p, c) for p, c in contracts.items()),
        "",
        "## Input checks",
        "",
        *_checks(contracts),
        "",
        "## Notes and questions for the lead",
        "",
        "- Q-1 (R5, SI and HG): D9.11 quotes Topstep's 50K figure for SI and HG as 0. R5's list "
        "of what D9.11 lowers (SIL, MHG) and D9.11's own 'Encoded:' sentence leave SI and HG "
        "out (D9.11 handles them by D2's SIL/MHG preference), so cap_c is D9.5's 1 here. A "
        "literal min(D9.5, 0) would give cap 0 and q_c = 0, which R6 and D8's depth term "
        "cannot use. It cannot change a vehicle: SI and HG move 5 and 10 times SIL and MHG, "
        "so if SIL (MHG) has rho > 2 at q = 1, SI (HG) does too, and if SIL (MHG) is a "
        "candidate it is the vehicle (R9).",
        "- Q-2 (R2, vendor-degraded dates): R2 excludes the research trade dates on "
        "Databento's degraded UTC-date list (reports/stage_e2a_bars.json "
        "degraded.on_research_trade_dates, as the brief directs; D.1e also treated the list as "
        "dates). A degraded UTC date also covers the evening session (17:00-19:00 CT) that "
        f"opens the NEXT trade date, so {', '.join(_off_list(contracts))} carry flagged "
        "evening bars on most contracts (not grains or livestock, whose evening opens at "
        "00:00 UTC). Their [O_X, C_X) bars lie on a clean UTC date; where no other cause "
        f"excludes them they are used ({_off_list_used(contracts)}). Reading 'any flagged bar "
        "of the trade date' would drop them too; no r_c was computed under that reading.",
        "- BarsCoder's limitation carries over: symbology covers UTC dates to 2026-06-20, so a "
        "roll splice on 2026-06-21/22 would put 2026-06-18/19 into a blackout no report can "
        "show from research-window metadata.",
        *(["- Pending contracts (" + ", ".join(result["counts"]["pending"]) + ") are written "
           "with q_c null; sim.cost_report.build_table raises KeyError for a root without q_c, "
           "so CostCoder's depth-term rebuild waits for them."] if result["counts"]["pending"]
          else ["- No contract is pending: all 45 have q_c (MBT's parquet and bars.json entry "
                "exist; L-9 and L-10 applied)."]),
        "",
    ]
    path.write_text("\n".join(lines))
