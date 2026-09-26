"""Stage E.2a Task 7 reports: reports/stage_e2a_bars.json/.md and the calendar bar checks
(reports/stage_e2a_calendar_bar_checks.json/.md). Counts, dates, CT minutes and flags only.

Calendar-check classification (Task 6's done-when, D.1f Task 3's rule): a discrepancy seen on a
thin contract but not on its group's most liquid contract (the highest ohlcv-1m record count in
reports/stage_e1_purchase.json) is "thin_trading": thin trading is never a calendar error and is
never fixed by a fake early close. One seen on the most liquid contract (the same kind on the
same day) is a "calendar_question" for the lead, who rules; no calendar module is edited here.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from data.calendars import GROUP_OF_PRODUCT, GROUPS

THIN = "thin_trading"
QUESTION = "calendar_question"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.is_file() else {}


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text)
    tmp.replace(path)


def merge_product(path: Path, summary: dict, header: dict) -> dict:
    """Add or replace one product's summary in the bars report and rewrite its .md."""
    doc = load_json(path) or {**header, "products": {}}
    doc.update({k: v for k, v in header.items() if k != "products"})
    doc.setdefault("products", {})[summary["product"]] = summary
    doc["generated_utc"] = datetime.now(UTC).isoformat()
    doc["refusals"] = [{"product": p, "causes": s.get("refusal_causes", [])}
                       for p, s in sorted(doc["products"].items()) if s.get("status") != "built"]
    _atomic_write(path, json.dumps(doc, indent=1, default=str))
    _atomic_write(path.with_suffix(".md"), render_bars_md(doc))
    return doc


def set_section(path: Path, key: str, value: Any, header: dict) -> dict:  # noqa: ANN401
    doc = load_json(path) or {**header, "products": {}}
    doc[key] = value
    _atomic_write(path, json.dumps(doc, indent=1, default=str))
    _atomic_write(path.with_suffix(".md"), render_bars_md(doc))
    return doc


def _n(d: dict | None) -> int:
    return sum(d.values()) if d else 0


def render_bars_md(doc: dict) -> str:
    win = doc.get("window_trade_dates", ["", ""])
    utc = doc.get("data_utc", ["", ""])
    lines = ["# Stage E.2a Task 7: research-window bar builds", "",
             f"Generated {doc.get('generated_utc', '')}. Trade dates {win[0]}..{win[1]}; "
             f"files {utc[0]}..{utc[1]} UTC "
             "(end exclusive). Counts, dates and flags only: no return, volatility, volume or "
             "coverage statistic and no price summary. Full records: stage_e2a_bars.json.", ""]
    lines += [str(x) for x in doc.get("notes", [])]
    lines += ["", "## Per product", "",
              "| Product | Group | Status | Bars | Trade dates | First | Last | Rolls | "
              "Blackout dates in window | Degraded on trade dates | Drops (window / coverage / "
              "no outright) | Calendar discrepancies | Build s | Peak MB |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for p, s in sorted(doc.get("products", {}).items(), key=lambda kv: (kv[1]["group"], kv[0])):
        rolls = s.get("rolls", {})
        drops = s.get("drops", {})
        cal = s.get("calendar_check", {})
        lines.append(
            f"| {p} | {s['group']} | {s['status']} | {s.get('bars', '')} | "
            f"{s.get('trade_dates', '')} | {s.get('first_trade_date', '')} | "
            f"{s.get('last_trade_date', '')} | {len(rolls.get('boundaries', []))} | "
            f"{len(rolls.get('roll_blackout_dates_in_window', []))} | "
            f"{len(s.get('degraded', {}).get('on_research_trade_dates', []))} | "
            f"{_n(drops.get('trade_date_before_window'))
               + _n(drops.get('trade_date_after_window'))}"
            f" / {drops.get('past_calendar_coverage', '')} / "
            f"{drops.get('no_outright_on_bar_utc_date', {}).get('total', '')} | "
            f"{len(cal.get('discrepancies', []))} | {s.get('build_seconds', '')} | "
            f"{s.get('peak_rss_mb', '')} |")
    lines += ["", "## Refusals", ""]
    refusals = doc.get("refusals", [])
    lines += [f"- {r['product']}: {'; '.join(r['causes']) or 'see JSON'}" for r in refusals] or \
        ["- none"]
    for p, s in sorted(doc.get("products", {}).items()):
        lines += _product_md(p, s)
    if "mes_regression" in doc:
        lines += ["", "## MES regression", "", "```json",
                  json.dumps(doc["mes_regression"], indent=1, default=str), "```"]
    return "\n".join(lines) + "\n"


def _product_md(p: str, s: dict) -> list[str]:
    rolls = s.get("rolls", {})
    out = ["", f"### {p} ({s['group']}, {s['status']})", ""]
    if s.get("refusal_causes"):
        out.append(f"- Refusal causes: {'; '.join(s['refusal_causes'])}")
    if s.get("closure_bars"):
        out.append("- Bars inside a scheduled closure (kept, flagged in_scheduled_closure; ruling "
                   "L-3): " + "; ".join(f"{c['ct']} CT -> trade date {c['trade_date']}"
                                        f"{' (close minute)' if c['close_minute'] else ''}"
                                        for c in s["closure_bars"]))
    if "parquet" in s:
        out.append(f"- Parquet: `{s['parquet']['path']}` sha256 `{s['parquet']['sha256']}`, "
                   f"{s['parquet']['rows']} rows, read-only")
    out.append(f"- Tick {s['tick']['tick']} ({s['tick']['source']}); raw off-tick prices "
               f"{s.get('raw_checks', {}).get('off_tick_prices', '')}; grid-scale probe "
               f"{s.get('raw_checks', {}).get('grid_scale_probe', {})}")
    out.append(f"- Calendar modules: {s.get('calendar_modules', {})}")
    out.append(f"- Rolls ({rolls.get('source', '')}): " + "; ".join(
        f"{b['date_utc']} {b['from']}->{b['to']} (splice trade date {b['splice_trade_date']})"
        for b in rolls.get("boundaries", [])))
    out.append(f"- Roll blackout dates (group calendar, splice + 2 sessions before): "
               f"{', '.join(rolls.get('roll_blackout_dates', []))}")
    if rolls.get("sim_engine_roll_blackout_differs"):
        out.append(f"- sim.engine.roll_blackout_dates (equity calendar) differs on: "
                   f"{rolls['sim_engine_roll_blackout_differs']}")
    sc = rolls.get("splice_check", {})
    out.append(f"- Splice check: {sum(r['consistent'] for r in sc.get('per_roll', []))}/"
               f"{len(sc.get('per_roll', []))} consistent; instrument changes in bars "
               f"{sc.get('instrument_changes_in_bars', '')}, unexplained "
               f"{sc.get('unexplained_instrument_changes', '')}")
    off = rolls.get("bars_off_symbology_mapping")
    if off is not None:
        out.append(f"- Bars whose instrument is not symbology's mapping on their UTC date: "
                   f"{off['bars']} {off['utc_dates'][:10]}")
    cross = rolls.get("embedded_mapping_crosscheck")
    if cross is not None:
        out.append(f"- Embedded-mapping cross-check: {cross['utc_dates_compared']} UTC dates, "
                   f"{len(cross['disagreements'])} disagreements "
                   f"{cross['disagreements'][:5]}")
    deg = s.get("degraded", {})
    if deg:
        out.append(f"- Vendor-degraded dates on research trade dates: "
                   f"{deg.get('on_research_trade_dates', [])}; bars flagged "
                   f"{deg.get('bars_flagged', '')}")
    drops = s.get("drops", {})
    if drops:
        out.append(f"- Drops: before window {drops.get('trade_date_before_window', {})}; after "
                   f"window {drops.get('trade_date_after_window', {})}; past calendar coverage "
                   f"{drops.get('past_calendar_coverage', 0)}; no outright "
                   f"{drops.get('no_outright_on_bar_utc_date', {}).get('total', 0)}")
    val = s.get("validation", {})
    if val:
        out.append(f"- Validation: hard failures {val.get('hard_failures', [])}; zero-volume bars "
                   f"{val.get('zero_volume_bars', '')}; gap runs {val.get('gap_runs_total', '')}"
                   f" {val.get('gap_runs_by_length', {})}")
    if s.get("flag_counts"):
        out.append(f"- Flag counts: {s['flag_counts']}")
    return out


# ------------------------------------------------------------ calendar classification ----
def classify_group(group: str, products: dict[str, dict], records: dict[str, int]) -> dict:
    members = sorted(p for p, g in GROUP_OF_PRODUCT.items() if g == group and p in records)
    present = [p for p in members if "calendar_check" in products.get(p, {})
               and "error" not in products[p]["calendar_check"]]
    out: dict[str, Any] = {"group": group, "contracts": members,
                           "record_counts": {p: records[p] for p in members}}
    if not members:
        return {**out, "status": "no admissible contract"}
    liquid = max(members, key=lambda p: records[p])
    out["most_liquid"] = liquid
    if liquid not in present or len(present) < len(members):
        return {**out, "status": "pending",
                "missing": sorted(set(members) - set(present))}
    checks = {p: products[p]["calendar_check"] for p in present}
    liquid_keys = {(d["kind"], d["day"]) for d in checks[liquid]["discrepancies"]}
    entries = checks[liquid]["entries_checked"]
    per: dict[str, Any] = {}
    counts: Counter[str] = Counter()
    for p in present:
        rows = []
        for d in checks[p]["discrepancies"]:
            label = QUESTION if (p == liquid or (d["kind"], d["day"]) in liquid_keys) else THIN
            counts[label] += 1
            row = {**d, "classification": label}
            if label == QUESTION:
                row["lead_ruling"] = lead_ruling(group, d["day"])
            rows.append(row)
        not_obs = {d["day"] for d in checks[p]["discrepancies"]
                   if d["kind"] == "listed_entry_not_observed"}
        per[p] = {"weekdays_checked": checks[p]["weekdays_checked"],
                  "entries_observed": sum(e["day"] not in not_obs for e in entries),
                  "discrepancies": rows, "notes": checks[p]["notes"],
                  "observations": checks[p].get("observations", []),
                  "outage_gap_runs": outage_gap_runs(products[p]),
                  "closure_bars": products[p].get("closure_bars", []),
                  "day_session_close_ct": checks[p].get("day_session_close_ct")}
    questions = []
    for d in checks[liquid]["discrepancies"]:
        also = [p for p in present if p != liquid and any(
            (x["kind"], x["day"]) == (d["kind"], d["day"]) for x in checks[p]["discrepancies"])]
        questions.append({**d, "most_liquid_contract": liquid, "also_on": also,
                          "lead_ruling": lead_ruling(group, d["day"])})
    unruled = sorted({(r["day"], r["kind"]) for p in present for r in per[p]["discrepancies"]
                      if r["classification"] == QUESTION and not r.get("lead_ruling")})
    return {**out, "status": "complete", "entries_checked": entries,
            "calendar_questions_without_ruling": [{"day": d, "kind": k} for d, k in unruled],
            "entries_observed_on_most_liquid": per[liquid]["entries_observed"],
            "counts_by_classification": dict(counts), "calendar_questions": questions,
            "per_contract": per}


OUTAGE = "documented_cme_outage"
OUTAGE_WINDOW_CT = ("2025-11-27 17:00", "2025-11-28 07:30")


def outage_citation() -> dict:
    """The CME source for the 2025-11-28 Globex outage (rates module's LATE_OPEN_SOURCES)."""
    from datetime import date

    from data.calendars.rates import LATE_OPEN_SOURCES

    c = LATE_OPEN_SOURCES[date(2025, 11, 28)]
    return {"module": "data/calendars/rates.py LATE_OPEN_SOURCES[2025-11-28]",
            "status_url": c.status_url, "status_quote": c.status_quote}


def outage_gap_runs(summary: dict) -> list[dict]:
    """Gap runs starting inside the documented outage (2025-11-27 17:00 to 2025-11-28 07:30
    CT): classified as the CME outage, never as a calendar error (lead ruling L-4)."""
    out = []
    for run in summary.get("validation", {}).get("gap_runs_over_30min", []):
        stamp = run["start_ct"][:10] + " " + run["start_ct"][-5:]
        if OUTAGE_WINDOW_CT[0] <= stamp < OUTAGE_WINDOW_CT[1]:
            out.append({**run, "classification": OUTAGE})
    return out


MBT_EXPIRY_NOTE = (
    "MBT (the only crypto contract, so every discrepancy is a calendar question by the rule): "
    "the Friday early stops at 09:58-10:00 CT (10:58-11:00 CT on 2025-10-31 and 2026-03-27) "
    "fall on the last Friday of each month, the expiry day of CME's monthly bitcoin futures; "
    "each is followed by a vendor roll on the next UTC date (rolls in stage_e2a_bars.json), so "
    "the volume-ranked series holds the expiring contract after its last trade. Diagnosis for "
    "the lead: contract expiry in the continuous series, not a calendar entry; every such "
    "Friday lies inside the roll blackout (splice trade date and the two sessions before)."
)


# The lead's rulings on the calendar questions (Stage E.2a, 2026-09-25 PDT), keyed by group and
# CT date; ``None`` as the date means every calendar question of the group.
_L7_THIN = ("L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, "
            "so the early-stop test does not apply there. No calendar change.")
LEAD_RULINGS: dict[tuple[str, str | None], str] = {
    ("fx", "2025-11-27"): "L-5: thin holiday trading (Thanksgiving, FX keeps its regular "
                          "hours); no calendar change.",
    ("metals", "2025-05-29"): _L7_THIN,
    ("metals", "2025-07-30"): _L7_THIN,
    ("metals", "2025-11-26"): _L7_THIN,
    ("metals", "2026-01-29"): _L7_THIN,
    ("metals", "2026-05-28"): _L7_THIN,
    ("metals", "2026-02-25"): "L-7: an unscheduled halt (GC, MGC, SI, SIL about 12:00-13:45 CT; "
                              "HG, MHG, NG, MNG gaps), unsourced; recorded, not a calendar "
                              "entry.",
    ("crypto", None): "L-11: monthly contract expiry while the volume-ranked series holds the "
                      "expiring contract (the last Friday of the month, and 2026-05-29); not a "
                      "calendar error; every such date lies inside a roll blackout.",
}


def lead_ruling(group: str, day: str) -> str | None:
    return LEAD_RULINGS.get((group, day)) or LEAD_RULINGS.get((group, None))


def calendar_report(bars_doc: dict, records: dict[str, int]) -> dict:
    products = bars_doc.get("products", {})
    groups = {g: classify_group(g, products, records) for g in GROUPS}
    totals: Counter[str] = Counter()
    unruled = []
    for g in groups.values():
        totals.update(g.get("counts_by_classification", {}))
        unruled += [{"group": g["group"], **q} for q in g.get("calendar_questions_without_ruling",
                                                               [])]
    return {"generated_utc": datetime.now(UTC).isoformat(),
            "stage": "E.2a Task 6 done-when / Task 7 (calendar bar checks, step-4b style)",
            "window_trade_dates": bars_doc.get("window_trade_dates"),
            "rules": [
                "(a) every weekday with no bar in its regular session span is a listed full "
                "closure",
                "(b) every weekday whose last bar before the day-session close C opens before "
                "C minus one minute is a listed early halt whose halt time equals the observed "
                "last minute plus one",
                "(c) every listed 2025-2026 entry inside the window is observed (early halt, "
                "full closure, LATE_OPENS)",
                "classification: seen on the group's most liquid contract (highest ohlcv-1m "
                "record count) -> calendar_question; seen only on thinner contracts -> "
                "thin_trading (never a calendar error, never fixed by a fake early close)"],
            "outage_2025_11_28": {
                "classification": OUTAGE, "window_ct": list(OUTAGE_WINDOW_CT),
                "ruling": "L-4 revised (01:21 PDT): no closed window in any group; the outage "
                          "is a reported gap run; LATE_OPENS is checked only (the first bar "
                          "of 2025-11-28 at or after 07:30 CT). The equity module does not list "
                          "it; its gap runs there are the same documented outage.",
                "citation": outage_citation()},
            "notes": [MBT_EXPIRY_NOTE],
            "totals_by_classification": dict(totals),
            "calendar_questions_without_ruling": unruled, "groups": groups}


def render_calendar_md(doc: dict) -> str:
    lines = ["# Stage E.2a calendar bar checks (step-4b style, per group)", "",
             f"Generated {doc['generated_utc']}. Research window "
             f"{doc['window_trade_dates'][0]}..{doc['window_trade_dates'][1]}. Evidence is CT "
             "minutes and bar counts only. No calendar module was edited: every calendar "
             "question is for the lead.", ""]
    lines += [f"- {r}" for r in doc["rules"]]
    out = doc.get("outage_2025_11_28")
    if out:
        lines += ["", f"2025-11-28 CME Globex outage ({out['classification']}): {out['ruling']} "
                  f"Source: {out['citation']['module']}, {out['citation']['status_url']}, "
                  f"quote: {out['citation']['status_quote']}"]
    lines += ["", *[f"Note: {n}" for n in doc.get("notes", [])]]
    lines += ["", f"Calendar questions without a lead ruling: "
              f"{doc.get('calendar_questions_without_ruling') or 'none'}"]
    lines += ["", f"Totals by classification: {doc['totals_by_classification']}", "",
              "| Group | Status | Contracts | Most liquid | Entries checked | Observed on most "
              "liquid | Thin trading | Calendar questions |", "|---|---|---|---|---|---|---|---|"]
    for g, x in doc["groups"].items():
        c = x.get("counts_by_classification", {})
        lines.append(f"| {g} | {x['status']} | {', '.join(x['contracts'])} | "
                     f"{x.get('most_liquid', '')} | {len(x.get('entries_checked', []))} | "
                     f"{x.get('entries_observed_on_most_liquid', '')} | {c.get(THIN, 0)} | "
                     f"{c.get(QUESTION, 0)} |")
    for g, x in doc["groups"].items():
        if x["status"] != "complete":
            continue
        lines += ["", f"## {g}", "", f"Most liquid: {x['most_liquid']}. Entries checked: " +
                  ", ".join(f"{e['day']} {e['kind']}" for e in x["entries_checked"]), "",
                  "### Calendar questions", ""]
        lines += [f"- {q['day']} {q['kind']}: {q['detail']} (also on: "
                  f"{', '.join(q['also_on']) or 'none'}). **Lead ruling:** "
                  f"{q.get('lead_ruling') or 'NONE YET'}" for q in x["calendar_questions"]] or \
            ["- none"]
        lines += ["", "### Per contract", ""]
        for p, r in x["per_contract"].items():
            lines.append(f"- **{p}**: weekdays {r['weekdays_checked']}, entries observed "
                         f"{r['entries_observed']}/{len(x['entries_checked'])}, discrepancies "
                         f"{len(r['discrepancies'])}, bars inside a scheduled closure "
                         f"{len(r.get('closure_bars', []))}"
                         + "".join(f" ({c['ct']} CT, close minute {c['close_minute']})"
                                   for c in r.get("closure_bars", [])[:5]))
            lines += [f"  - [{d['classification']}] {d['day']} {d['kind']}: {d['detail']}"
                      + (f" Lead ruling: {d['lead_ruling']}" if d.get("lead_ruling") else "")
                      for d in r["discrepancies"]]
            lines += [f"  - note {n['day']}: {n['note']}" for n in r["notes"]]
            lines += [f"  - bars on {o['day']} ("
                      + ("late open, checked only (ruling L-4)" if o.get("kind") == "late_open"
                         else "listed without an entry") + "): "
                      + ", ".join(f"{k} {v}" for k, v in o.items()
                                  if k not in ("day", "module_note", "kind"))
                      for o in r.get("observations", [])]
            lines += [f"  - [{o['classification']}] gap run from {o['start_ct']} CT, "
                      f"{o['minutes']} minutes" for o in r.get("outage_gap_runs", [])]
    return "\n".join(lines) + "\n"


def write_calendar_report(bars_json: Path, out_json: Path, records: dict[str, int]) -> dict:
    doc = calendar_report(load_json(bars_json), records)
    _atomic_write(out_json, json.dumps(doc, indent=1, default=str))
    _atomic_write(out_json.with_suffix(".md"), render_calendar_md(doc))
    return doc
