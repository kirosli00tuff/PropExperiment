"""build_groundwork.py: phase 1 of the R2 dossiers (Stage E.32b step 3b, DossierWriter).

For each top-15 code's underlying and each idea family F01-F12: applies or not (with the deciding fact), and where
it applies the mechanism, timing, evidence rows (copied verbatim from briefs/R2_idea_families.json), R1 overlaps
(closing sentences copied from briefs/R1_closed_lines.json), the data needed (census estimates from
briefs/F2_data_access.json) and pool candidates. Writes work/R2/groundwork.json and groundwork.md.

Run: uv run python reports/stage_e32b_briefs/work/R2/build_groundwork.py
Facts only: no market data, no strategy outcome.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import groundwork_facts as GF  # noqa: E402
from r2_common import (  # noqa: E402
    DATA_PATH, DAYS_PER_MONTH, E16_WINDOWS_PATH, F5_PATH, GROUNDWORK_JSON, GROUNDWORK_MD, MONTHS_DISC, MONTHS_TEST,
    R1_PATH, R2F_PATH, SCORE_PATH, SPEC_SHA256, WEEKS_PER_YEAR, check_hash, check_spec, fmt, inputs_meta, load,
    now_pdt, r, write_json, write_text,
)

TOP15_CODES = ("YM", "MNQ", "RTY", "MYM", "ZL")
CUTOFF = date(2024, 3, 1)           # spec 8.3 Q7: clean test windows before 2024-03
DISC_WINDOW = ("2020-12-01", "2024-02-29")
# Test windows chosen per underlying (43 months each): the never-read DOW stretch ends 2019-05-06, so the 43 months
# just before it; ZL's sealed soy-test window is exactly 43 months.
TEST_WINDOW = {"DOW": ("2015-10-01", "2019-04-30", "never read, unsealed, not owned: buy"),
               "SOYOIL": ("2017-05-01", "2020-11-30", "sealed for a future test (V51, every schema)")}
BAR_ROOT = {"YM": "YM", "MYM": "YM", "MNQ": "NQ", "RTY": "RTY", "ZL": "ZL"}   # price path used for bars (F3 OC-1)
UND_OF = {c: u for u, v in GF.UNDERLYINGS.items() for c in v["codes"]}


def d(s: str) -> date:
    return date.fromisoformat(s[:10])


def months(a: date, b: date) -> float:
    return (b - a).days / DAYS_PER_MONTH


# ------------------------------------------------------------------------------------------- evidence
def evidence_index(r2f: dict) -> dict:
    idx = {}
    for fam in r2f["families"]:
        fid = fam["id"].replace("R2-", "")
        for i, e in enumerate(fam["evidence"], 1):
            idx[f"{fid}.E{i:02d}"] = e
    return idx


def evidence_rows(key, ev_idx: dict) -> list:
    out = []
    for rid, relation in GF.EVIDENCE.get(key, []):
        e = ev_idx[rid]
        out.append({"row_id": rid, "relation_to_product": relation, "study": e["source"],
                    "item_ids": e.get("item_ids") or [], "product_in_study": e["product"], "horizon": e["horizon"],
                    "data_period": e["period"], "in_or_out_of_sample": e["in_or_out_of_sample"],
                    "net_of_costs": e["net_of_costs"], "finding": e["finding"], "sign": e["sign"],
                    "verified_level": e["verified"], "venue_type": e["venue_type"], "quote": e["quote"],
                    "file": e["file"]})
    return out


# ------------------------------------------------------------------------------------------- R1
def r1_rows(key, r1: dict) -> list:
    lines = {ln["id"]: ln for ln in r1["lines"]}
    out = []
    for lid, relation, config, reading in GF.R1_OVERLAP.get(key, []):
        ln = lines[lid]
        cl = ln.get("closing") or {}
        out.append({"line": lid, "type": ln["type"], "relation_to_product": relation, "configuration": config,
                    "line_horizons": ln.get("horizons"), "line_windows": ln.get("windows"),
                    "n_trials": ln.get("n_trials"), "closing_decision": cl.get("decision"),
                    "closing_quote": cl.get("quote"), "closing_source": cl.get("source"),
                    "exceptions": ln.get("exceptions"), "lr_r1_reading": reading})
    return out


# ------------------------------------------------------------------------------------------- events
def f04_events_per_year() -> tuple[float, str]:
    a, b = d(GF.F04_WINDOW[0]), d(GF.F04_WINDOW[1])
    years = ((b - a).days + 1) / 365.25
    total = sum(GF.F04_COUNTS.values())
    return total / years, f"{total} releases in {years:.3f} years = {total / years:.2f} a year ({GF.F04_SOURCE})"


def topstep_t1_events_per_week() -> dict:
    a, b = d(GF.F04_WINDOW[0]), d(GF.F04_WINDOW[1])
    years = ((b - a).days + 1) / 365.25
    per_week = {k: v / years / WEEKS_PER_YEAR for k, v in GF.TOPSTEP_T1_COUNTS.items()}
    return {"window": list(GF.F04_WINDOW), "years": r(years), "counts": GF.TOPSTEP_T1_COUNTS,
            "per_week": {k: r(v) for k, v in per_week.items()},
            "all_t1_events_per_week": r(sum(per_week.values())),
            "f04_events_per_week (CPI, PPI, NFP)": r(per_week["CPI"] + per_week["PPI"] + per_week["NFP"]),
            "f05_events_per_week (FOMC)": r(per_week["FOMC"]),
            "source": "reports/stage_e20_briefs/shared/macro_calendars.md section 3 (frozen calendar counts)"}


# ------------------------------------------------------------------------------------------- data plans
def merge_windows(ws: list) -> list:
    ws = sorted(ws)
    out = []
    for a, b in ws:
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def clean_window(census_code: dict) -> dict:
    """Longest clean stretch before 2024-03-01: never read (counts_for_p reads) and unsealed, or sealed for a test."""
    start = d(census_code["p_history_start"])
    one = timedelta(days=1)          # census read-window ends are inclusive trade dates
    reads = merge_windows([(d(w["start"]), d(w["end"]) + one) for w in census_code["read_windows"]
                           if w["counts_for_p"]])
    sealed = [(d(s["start"]), d(s["end"])) for s in census_code["sealed_windows"]]
    gaps, cur = [], start
    for a, b in reads:
        if a > cur:
            gaps.append((cur, min(a, CUTOFF)))
        cur = max(cur, b)
    if cur < CUTOFF:
        gaps.append((cur, CUTOFF))
    # a gap that overlaps a sealed window is reported via the sealed window
    best_gap = max(gaps, key=lambda g: (g[1] - g[0]).days, default=None)
    best_seal = max(sealed, key=lambda s: (s[1] - s[0]).days, default=None)
    gap_m = months(*best_gap) if best_gap else 0.0
    seal_m = months(best_seal[0], best_seal[1]) + 1 / DAYS_PER_MONTH if best_seal else 0.0
    if seal_m >= gap_m and best_seal:
        kind, win, m = "sealed for a future test", best_seal, seal_m
    elif best_gap:
        kind, win, m = "never read, unsealed", best_gap, gap_m
    else:
        kind, win, m = "none", None, 0.0
    return {"months": r(m, 2), "kind": kind, "window": [str(win[0]), str(win[1])] if win else None,
            "census_unread_stretches": census_code["p_unread_stretches"], "census_p_basis": census_code["p_basis"],
            "reads_merged": [[str(a), str(b)] for a, b in reads],
            "sealed": [[str(a), str(b)] for a, b in sealed]}


def owned_covers(census_code: dict, schema: str, root: str, a: str, b: str) -> bool:
    for o in census_code["owned"]:
        if o["schema"] == schema and o["root"] == root and d(o["first_day"]) <= d(a) and d(o["end_exclusive"]) > d(b):
            return True
    return False


def data_plan(code: str, census: dict, e16: dict) -> dict:
    und = UND_OF[code]
    bar_root = BAR_ROOT[code]
    c_bar = census["codes"][bar_root if bar_root in census["codes"] else code]
    c_code = census["codes"][code]
    clean = clean_window(c_code)
    disc_owned = owned_covers(c_bar, "ohlcv-1m", bar_root, *DISC_WINDOW)
    test = TEST_WINDOW.get(und)
    plan = {"code": code, "underlying": und, "bar_price_path_root": bar_root,
            "discovery_window": {"start": DISC_WINDOW[0], "end": DISC_WINDOW[1], "months": MONTHS_DISC,
                                 "bars_owned": disc_owned,
                                 "bars_read_before": [w for w in c_bar["read_windows"] if w["counts_for_p"]
                                                      and d(w["end"]) >= d(DISC_WINDOW[0])]},
            "clean_test_window": clean}
    # bars, test window
    if test is None:
        plan["test_window"] = {"start": None, "end": None, "months": 0,
                               "status": "no clean window of 36 months or more before 2024-03: every pre-2024-03 "
                                         "month of the underlying was read (census p_basis) and none is sealed; a "
                                         "test would need 2024-03 onward (not sealed for these codes; outside Q7's "
                                         "pre-2024-03 rule)"}
        bar_test_cost, bar_test_note = 0.0, "no clean pre-2024-03 test window: nothing to buy before 2024-03"
    else:
        a, b, status = test
        plan["test_window"] = {"start": a, "end": b, "months": MONTHS_TEST, "status": status}
        if und == "SOYOIL":
            bar_test_cost, bar_test_note = 0.0, ("ZL ohlcv-1m for the window is owned inside the sealed files "
                                                 "(docs/soy_test/SOY_TEST_MANIFEST.json: 44 raw ohlcv-1m files, 2 "
                                                 "stores, 1 cache for ZL); unlock only in a registered test")
        else:
            q = e16["products"][bar_root]
            per_month = q["e12_quoted_usd"] / q["chunks_2010_to_2019_04"]
            bar_test_cost = per_month * MONTHS_TEST
            bar_test_note = (f"estimate: E.12 quote USD {q['e12_quoted_usd']:.5f} for {q['chunks_2010_to_2019_04']} "
                             f"monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json "
                             f"products.{bar_root}) = USD {per_month:.4f}/month x {MONTHS_TEST}")
    plan["bars"] = {"schema": "ohlcv-1m", "root": bar_root, "discovery_cost_usd": 0.0 if disc_owned else None,
                    "test_cost_usd": r(bar_test_cost, 2), "cost_basis": bar_test_note,
                    "quotes_to_obtain": ([f"GLBX.MDP3 ohlcv-1m {bar_root}.v.0 {test[0]}..{test[1]}"]
                                         if test and und != "SOYOIL" else [])}
    # book (MBO), census estimate k USD/month
    broot = GF.BOOK_SOURCE[code]
    cb = census["codes"][broot]
    k = cb["k_usd_month"]
    disc_book_owned = False
    disc_cost = k * MONTHS_DISC if k is not None else None
    test_cost = (k * MONTHS_TEST if (k is not None and test is not None) else 0.0)
    alt = None
    if code == "ZL":
        mbp1 = cb["k_inputs"].get("mbp1_usd_per_month_mean")
        alt = {"schema": "mbp-1", "discovery": "owned (E.31 purchase, ZL front MBP-1 2020-12..2024-02; read by "
               "E.31/E.33: V50 item 4)", "discovery_cost_usd": 0.0,
               "test_cost_usd": r(mbp1 * MONTHS_TEST, 2) if mbp1 else None,
               "basis": f"census mbp-1 whole-month mean USD {mbp1}/month x {MONTHS_TEST} (estimate)"}
    plan["book"] = {"schema": "mbo", "root": broot, "mbo_start": cb["mbo_start"], "k_usd_month": k,
                    "k_kind": cb["k_method"], "discovery_owned": disc_book_owned,
                    "discovery_cost_usd": r(disc_cost, 2), "test_cost_usd": r(test_cost, 2),
                    "cost_basis": f"census estimate k = USD {k}/month (F2_data_access codes.{broot}.k_usd_month, "
                                  f"{cb['k_method']}) x months",
                    "note": GF.BOOK_SOURCE_NOTE.get(code), "alternative": alt,
                    "quotes_to_obtain": [f"GLBX.MDP3 mbo {broot}.v.0 {DISC_WINDOW[0]}..{DISC_WINDOW[1]}"]
                    + ([f"GLBX.MDP3 mbo {broot}.v.0 {test[0]}..{test[1]} (MBP-10 before 2017-05-21)"] if test else [])}
    if code == "ZL":
        plan["sealed_window_caveat"] = ("the soy-test seal (2017-05-01..2020-11-30) was set by E.32 Part 0 after E.16 "
                                        "(r002) and E.21 (r006) had read ZL bars over 2010-07..2024-02; the census "
                                        "still counts the seal (p_basis), and spec 8.3 Q7 counts sealed windows as "
                                        "clean")
    return plan


# ------------------------------------------------------------------------------------------- assemble
def build() -> dict:
    spec = check_spec()
    r2f, r1, census, f5, e16, score = (load(p) for p in (R2F_PATH, R1_PATH, DATA_PATH, F5_PATH, E16_WINDOWS_PATH,
                                                         SCORE_PATH))
    for doc, name in ((r2f, "R2_idea_families"), (f5, "F5_holding"), (score, "score32b_out")):
        check_hash(doc, name)
    top15 = score["primary"]["top15"]
    codes_top = sorted({row["code"] for row in top15}, key=TOP15_CODES.index)
    if tuple(codes_top) != TOP15_CODES:
        raise SystemExit(f"REFUSED: top-15 codes {codes_top} differ from the lead's list {TOP15_CODES}")
    ev_idx = evidence_index(r2f)
    fam_by_id = {f["id"].replace("R2-", ""): f for f in r2f["families"]}
    f04_rate, f04_note = f04_events_per_year()

    unds = {}
    for u, meta in GF.UNDERLYINGS.items():
        fams = {}
        for fid in GF.FAMILIES:
            applies, why, items = GF.APPLIES[(u, fid)]
            fam = fam_by_id[fid]
            entry = {"family": fid, "name": fam["name"], "applies": applies,
                     "decided_by": {"fact": why, "items": items}}
            if applies:
                tm = dict(GF.TIMING[(u, fid)])
                if fid == "F04":
                    tm["events_per_year"] = r(f04_rate, 3)
                    tm["events_source"] = f04_note
                tm["kind"] = GF.FAMILY_KIND[fid]
                entry.update({
                    "mechanism": fam["mechanism"],
                    "retail_size": (fam["mechanism"].get("why_retail_edge_could_exist") + " One contract moves no "
                                    "price; at tens of milliseconds to a second without co-location only effects "
                                    "lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, "
                                    "ZN, CL: E.25)."),
                    "codes_in_r2": fam["codes"], "timing": tm,
                    "absorption_under_5min": fam["absorption_under_5min"],
                    "evidence": evidence_rows((u, fid), ev_idx),
                    "r1_overlap": r1_rows((u, fid), r1),
                    "data": {"schema": GF.SCHEMA[fid], "extras": GF.EXTRAS.get(fid, []),
                             "r2_data_needs": fam["data_needs"]},
                    "open_questions": fam["open_questions"]})
            fams[fid] = entry
        unds[u] = {**meta, "families": fams,
                   "other_closed_lines_on_product": [{"line": a, "what": b} for a, b in GF.PRODUCT_OTHER_LINES[u]]}

    f5s = f5["survivors"]
    codes = {}
    for c in TOP15_CODES:
        s = f5s[c]
        codes[c] = {"underlying": UND_OF[c], "asset_class": GF.UNDERLYINGS[UND_OF[c]]["asset_class"],
                    "f3_status": s["status"], "oc1_source": s["oc1_source"], "tick_size": s["tick_size"],
                    "tick_value_usd": s["tick_value_usd"], "L_main": s["L_main"],
                    "main_session_pt": s["main_session_pt"], "pauses": s["pauses"],
                    "data_plan": data_plan(c, census, e16)}

    pools = []
    for p in GF.POOLS:
        shared = [fid for fid in GF.FAMILIES
                  if all(GF.APPLIES[(UND_OF[m], fid)][0] for m in p["members"])]
        pools.append({**p, "asset_class": "equity", "shared_families": shared,
                      "rho": {"measured": {}, "note": GF.E29_MEASURED, "rule": "r3_score: 0.5 within an asset class, "
                              "0.3 across, when no measured value"}})

    for_lead = [
        "F09 not applied to YM/MYM (EQUITY-14: no sourced lead-lag) or MNQ (EQUITY-13: NQ leads, nothing leads it); "
        "applied to RTY only.",
        "F06 (pre-scheduled drift) not applied to equity: R2 lists F06 for rates and natgas; the pre-FOMC equity "
        "drift is evidence against under F05 (EQUITY-21, gone after 2015).",
        "F01 applied to ZL although its product row is null (SB-22): the structural precondition (a close) holds; "
        "the null is evidence for the rater.",
        "F01, F08 counted as daily families (252 events a year, 1 trade each), not n_cap x 252: they trade once a "
        "day at a fixed clock.",
        "F04 events: 67.65 a year from the E.20 frozen-calendar counts (NFP, CPI, PPI, GDP first/last, ISM services "
        "and manufacturing, 2019-05..2024-02); IP 09:15 not counted (no calendar file). The 08:30 ET releases fall "
        "before the equity main session (05:30 PT), where F3's main-session sigma understates event-time sigma.",
        "F03 (ZL): 27 events a year = 15 major USDA days + 12 NOPA; overlapping days not netted.",
        "Clean test windows: DOW 107 months never read (2010-06..2019-05, buy bars); NASDAQ 0.8 and RUSSELL 0 "
        "(all read); ZL 43 months sealed, but read by E.16 and E.21 before the seal.",
        "MYM bars use YM's price path (F3 OC-1), including a test window that predates MYM's 2019-05-06 listing.",
        "Book data (F10) priced as MBO at the census k (estimate); MYM via YM's book; MNQ on its own MBO (NQ's book "
        "cheaper but V49).",
        "Pools: EQ3 {YM, MNQ, RTY} and EQ3m {MYM, MNQ, RTY}; no sub-pools; no measured rho among members.",
    ]
    return {"spec_sha256": spec, "generated_pdt": now_pdt(),
            "generated_by": "reports/stage_e32b_briefs/work/R2/build_groundwork.py (DossierWriter-OpusXHigh)",
            "inputs": inputs_meta({"R2_idea_families": R2F_PATH, "R1_closed_lines": R1_PATH,
                                   "F2_data_access": DATA_PATH, "F5_holding": F5_PATH,
                                   "stage_e16_windows": E16_WINDOWS_PATH, "score32b_out": SCORE_PATH}),
            "rulings_applied": ["LR-R1", "LR-R2a", "LR-R2b", "LR-R2c", "LR-Q6d", "LR-F5-IBKR"],
            "scope": {"top15": [{"rank": t["rank"], "firm": t["firm"], "code": t["code"]} for t in top15],
                      "codes": list(TOP15_CODES), "excluded": "NQ (V49): never a candidate or pool member"},
            "cross_family_facts": GF.CROSS_FACTS,
            "topstep_t1_event_rates": topstep_t1_events_per_week(),
            "underlyings": unds, "codes": codes, "pools": pools, "pools_not_built": GF.POOLS_NOT_BUILT,
            "for_lead": for_lead}


# ------------------------------------------------------------------------------------------- markdown
def to_md(g: dict) -> str:
    L = ["# R2 groundwork (Stage E.32b step 3b, phase 1): DossierWriter-OpusXHigh", "",
         f"Generated {g['generated_pdt']} by {g['generated_by']}. Facts only: no rating, no outcome. Evidence rows "
         "(FNN.ENN) are the rows of briefs/R2_idea_families.json in file order; quotes and closing sentences are "
         "copied in groundwork.json. Spec sha256 " + SPEC_SHA256[:16] + "...", "",
         "## Scope", "",
         "Top-15 pairs: " + ", ".join(f"{t['firm']}|{t['code']}" for t in g["scope"]["top15"]) + ". Codes: "
         + ", ".join(g["scope"]["codes"]) + ". " + g["scope"]["excluded"] + ".", "",
         "## Cross-family facts", ""]
    L += [f"- {x}" for x in g["cross_family_facts"]]
    L += ["", "## Applicability (underlying x family)", "",
          "| underlying | codes | " + " | ".join(GF.FAMILIES) + " |",
          "|---|---|" + "---|" * len(GF.FAMILIES)]
    for u, ud in g["underlyings"].items():
        L.append(f"| {u} | {' '.join(ud['codes'])} | "
                 + " | ".join("yes" if ud["families"][f]["applies"] else "no" for f in GF.FAMILIES) + " |")
    n_yes = sum(ud["families"][f]["applies"] for ud in g["underlyings"].values() for f in GF.FAMILIES)
    L += ["", f"Applied: {n_yes} of {len(g['underlyings']) * len(GF.FAMILIES)} underlying-family cells.", "",
          "### Deciding facts for 'no'", ""]
    for u, ud in g["underlyings"].items():
        for f in GF.FAMILIES:
            e = ud["families"][f]
            if not e["applies"]:
                L.append(f"- {u} {f}: {e['decided_by']['fact']}")
    L += ["", "## Per underlying and family", ""]
    for u, ud in g["underlyings"].items():
        L += [f"### {u} ({ud['name']}; {', '.join(ud['codes'])})", "", ud["note"], ""]
        for f in GF.FAMILIES:
            e = ud["families"][f]
            if not e["applies"]:
                continue
            tm = e["timing"]
            L += [f"#### {u} {f}: {e['name']}", "",
                  f"- Applies: {e['decided_by']['fact']}",
                  f"- Mechanism (whose flow): {e['mechanism'].get('whose_flow')}",
                  f"- Why predictable: {e['mechanism'].get('why_predictable')}",
                  f"- Retail size: {e['retail_size']}",
                  f"- Horizon: {tm['documented_horizon']}. Timing: {tm['timing_pt']}. Kind: {tm['kind']}; events a "
                  f"year: {fmt(tm['events_per_year'], 2)} ({tm['events_source']}); trades per event: "
                  f"{fmt(tm['trades_per_event'])}.",
                  "- Evidence rows: " + "; ".join(
                      f"{x['row_id']} {x['study']} [{x['relation_to_product']}; {x['horizon']}; {x['data_period']}; "
                      f"{x['in_or_out_of_sample']}; net {x['net_of_costs']}; {x['verified_level']}, "
                      f"{x['venue_type']}]: {x['finding']}" for x in e["evidence"]),
                  "- R1 overlap: " + "; ".join(
                      f"{x['line']} ({x['relation_to_product']}): {x['configuration']}; {x['closing_decision']}: "
                      f"\"{x['closing_quote']}\" ({x['closing_source']}); {x['lr_r1_reading']}"
                      for x in e["r1_overlap"]),
                  f"- Data: {e['data']['schema']}; " + "; ".join(e["data"]["extras"]), ""]
    L += ["## Data plans per code (discovery 39 months, test 43 months; census estimates)", "",
          "| code | bars root | discovery (owned?) | test window | clean test window | bar test USD | MBO k USD/mo |"
          " MBO disc USD | MBO test USD |", "|---|---|---|---|---|---|---|---|---|"]
    for c, cd in g["codes"].items():
        p = cd["data_plan"]
        tw = p["test_window"]
        cw = p["clean_test_window"]
        L.append(f"| {c} | {p['bar_price_path_root']} | {p['discovery_window']['start']}..{p['discovery_window']['end']}"
                 f" ({fmt(p['discovery_window']['bars_owned'])}) | {tw['start'] or '-'}..{tw['end'] or '-'} | "
                 f"{cw['months']} ({cw['kind']}) | {fmt(p['bars']['test_cost_usd'], 2)} | {p['book']['k_usd_month']} |"
                 f" {fmt(p['book']['discovery_cost_usd'], 2)} | {fmt(p['book']['test_cost_usd'], 2)} |")
    L += ["", "Notes: " + " ".join(f"{c}: {cd['data_plan']['bars']['cost_basis']}." for c, cd in g["codes"].items()
                                   if cd["data_plan"]["bars"]["test_cost_usd"]), ""]
    zl = g["codes"]["ZL"]["data_plan"]
    L += [f"ZL: {zl['sealed_window_caveat']}. Book alternative: {zl['book']['alternative']}.", "",
          "## Topstep Tier 1 event rates (frozen calendar counts)", "", str(g["topstep_t1_event_rates"]), "",
          "## Pools", ""]
    for p in g["pools"]:
        L.append(f"- {p['name']} {p['members']}: {p['mechanism']}. Shared families: {', '.join(p['shared_families'])}. "
                 f"rho: {p['rho']['note']}")
    L += ["", "Not built:"] + [f"- {x['candidate']}: {x['reason']}" for x in g["pools_not_built"]]
    L += ["", "## For the lead", ""] + [f"- {x}" for x in g["for_lead"]]
    return "\n".join(L) + "\n"


def main() -> int:
    g = build()
    write_json(GROUNDWORK_JSON, g)
    write_text(GROUNDWORK_MD, to_md(g))
    n_yes = sum(ud["families"][f]["applies"] for ud in g["underlyings"].values() for f in GF.FAMILIES)
    print(f"groundwork: {len(g['underlyings'])} underlyings, {n_yes} families applied, {len(g['pools'])} pools")
    return 0


if __name__ == "__main__":
    sys.exit(main())
