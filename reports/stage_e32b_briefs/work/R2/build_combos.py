"""build_combos.py: phase 2 of the R2 dossiers (Stage E.32b step 3b, DossierWriter).

Builds the combinations of lead ruling LR-R2a (top-15 pairs x applicable families, IBKR x the top-15 codes, pools)
with LR-R2b's band (the pair's F5 band B; a pool: the intersection of its members' bands) and h_c (the member of B
with the lowest G; a pool: the lowest worst-member G), and computes per spec 8.2: c_f in ticks, the gross edge and hit
rates needed at h_c, K_year, trades in the discovery (796 dates) and test (870 dates) windows, e80, the prop fit, the
gate flags, the data costs and, on Rithmic routes only, a queue-limit variant c_lim (reported beside, never scored).

Writes briefs/R2_combinations_unrated.json (work/score/SCHEMA.md section 7, Q1-Q3 absent) and
work/R2/combos_detail.json (every computed number, for the dossiers). Does not run r3_score.py.

Run: uv run python reports/stage_e32b_briefs/work/R2/build_combos.py
Facts and arithmetic only: no market data, no strategy outcome.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import groundwork_facts as GF  # noqa: E402
from r2_common import (  # noqa: E402
    BAND_H, COMBOS_DETAIL, COMBOS_UNRATED, DAYS_PER_YEAR, F4_PATH, F5_PATH, GROUNDWORK_JSON, NORMAL_FACTOR,
    OWN_BROKER, SCORE_PATH, SR80_PATH, T_DISC, T_TEST, check_hash, check_spec, inputs_meta, load, now_pdt, r,
    write_json,
)

FAMILY_SHORT = {"F01": "F01 intraday momentum into the close", "F03": "F03 USDA and NOPA report drift",
                "F04": "F04 US macro release drift", "F05": "F05 FOMC post-statement drift",
                "F08": "F08 session and overnight-to-day handoff", "F09": "F09 cross-market lead-lag",
                "F10": "F10 order-book state at 5 min and longer", "F11": "F11 own-price-path trend and reversal",
                "F12": "F12 expiry and option-hedging days"}
PRODUCT_ORDER = ("YM", "MYM", "MNQ", "RTY", "ZL")
ASSET_CLASS = {"YM": "equity", "MYM": "equity", "MNQ": "equity", "RTY": "equity", "ZL": "grains"}  # LR-R2c
# Payout: the firm's daily payout-qualification threshold (USD) on the modelled plan (F4 firms.<firm>.payout;
# F2_firms payout_qualification; E.28/E.32b econ model win_threshold). 0 = no daily threshold stated.
PAYOUT_DAILY = {
    "topstep": (150.0, "Standard path: '5 winning days of $150+ net P&L' (F4 firms.topstep.payout.standard_path)"),
    "tradeify": (150.0, "'5 or more of the Trading Days must show a profit greater than: ... $150 in profit for 50k "
                        "accounts' (F2_firms tradeify payout_qualification)"),
    "lucid": (0.0, "no daily threshold: 'winning_day_minimum': null; the cycle needs USD 500 with the largest day "
                   "<= 40% (F2_firms lucid payout_qualification, verified)"),
    "mffu": (0.0, "no daily threshold: 'min_profit_per_day': null; 2 traded days per cycle, 50% consistency, USD 500 "
                  "above the buffer (F2_firms mffu payout_qualification, verified)"),
    "bulenox": (0.0, "no daily threshold: 'min_profit_per_day': null; 10 trading days per cycle, 40% consistency, "
                     "min payout USD 1,000 (F2_firms bulenox payout_qualification, verified)"),
}
RITHMIC_ROUTES = {
    "bulenox": "Rithmic only ('Rithmic Paper Trading'; E.32 methods brief 5.3 firm-route table)",
    "lucid": "Rithmic route (default in the pricing config) beside a CQG route (methods brief 5.3)",
    "tradeify": "Rithmic route among Tradovate and WealthCharts; broker fixed at checkout (methods brief 5.3)",
}
E31_TT_MARKOUT = 0.970     # E.31: gross 10 s markout per passive fill, model (c) trade-through, ZM front DAY
SLIP_PER_LEG = 0.25        # OC-5: 0.5 tick slippage a round trip on market orders
CONTINUOUS_STOPPED = ("F09", "F10", "F11")
# Documented exit time (PT) of the family's core trade, for the flat-by-close gate.
EXIT_PT = {"F01": {"equity": "13:00", "grains": "11:20"}, "F03": {"grains": "11:20"}, "F04": {"equity": "08:00"},
           "F05": {"equity": "13:00"}, "F08": {"equity": "07:00", "grains": "07:00"},
           "F12": {"equity": "13:00"}}


def hm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


# ------------------------------------------------------------------------------------------- venue rows
def venue_rows(f5: dict, top15: list) -> dict:
    """{(venue, code): row} for the top-15 pairs and the IBKR rows of the five codes."""
    out = {}
    for t in top15:
        key = f"{t['firm']}|{t['code']}"
        out[(t["firm"], t["code"])] = {"kind": "prop", "rank": t["rank"], **f5["pairs"][key]}
    for c in PRODUCT_ORDER:
        out[(OWN_BROKER, c)] = {"kind": "own_broker", "rank": None, **f5["own_broker"]["rows"][f"{OWN_BROKER}|{c}"]}
    return out


def band_of(row: dict) -> list:
    return [h for h in BAND_H if h in row["band"]["members"]]


def h_c_of(rows_by_member: list, band: list) -> tuple[str, dict]:
    """The band member with the lowest worst-member G (one member: its own G)."""
    worst = {h: max(rw["rows"][h]["G"] for rw in rows_by_member) for h in band}
    h_c = min(band, key=lambda h: (worst[h], BAND_H.index(h)))
    return h_c, worst


# ------------------------------------------------------------------------------------------- members
def k_year(fid: str, timing: dict, ncap: int) -> float:
    kind = GF.FAMILY_KIND[fid]
    if kind == "continuous":
        return float(ncap * DAYS_PER_YEAR)
    return float(timing["events_per_year"]) * float(timing["trades_per_event"])


def news_stop(firm: str, code: str, fid: str, f4: dict, t1: dict) -> tuple[float, str]:
    """Scheduled events a week around which the firm's news windows stop the family (rule in the dossier header)."""
    if firm != "topstep":
        return 0.0, f"{firm}: no news window on the modelled plan (F4 firms.{firm}.news_windows)"
    nw = f4["firms"]["topstep"]["news_windows"][0]
    if code not in nw["blocked_among_47"]:
        if code in nw["capped_among_47_one_lot_still_allowed"]:
            return 0.0, "Topstep Tier 1: micro capped, one lot allowed (not stopped)"
        return 0.0, "Topstep Tier 1 windows do not name this product"
    if fid in CONTINUOUS_STOPPED:
        return t1["all_t1_events_per_week"], ("Topstep Tier 1 blocks new openings 5 min before to 5 min after CPI, "
                                              "PPI, NFP, FOMC decision and press conference: a continuous family is "
                                              "stopped around each (frozen-calendar rate)")
    if fid == "F04":
        return t1["f04_events_per_week (CPI, PPI, NFP)"], ("windows on CPI, PPI, NFP (3 of the 6 counted release "
                                                           "types); the family's entries at +5..+10 min fall after "
                                                           "the window")
    if fid == "F05":
        return t1["f05_events_per_week (FOMC)"], ("windows on the FOMC decision (13:00 CT) and press conference "
                                                  "(13:30 CT); the documented equity trade (last half-hour) falls "
                                                  "after them")
    return 0.0, "the family's fixed trade times lie outside every Tier 1 window"


def gates(kind: str, firm: str, code: str, fid: str, pair: dict, f4: dict) -> tuple[dict, list]:
    notes = []
    covers = False
    if kind == "prop" and firm == "topstep" and code in f4["firms"]["topstep"]["news_windows"][0]["blocked_among_47"] \
            and fid in ("F04", "F05"):
        notes.append("news gate false: the documented entry (F04 at release +5..+10 min; F05 at the FOMC-day last "
                     "half-hour) lies after the +5 min end of Topstep's window; an entry inside the first 5 minutes "
                     "would be blocked (borderline at exactly +5 min)")
    overnight = False
    notes.append("overnight gate false: every band is intraday and no family's core trade holds across the daily "
                 "close (the F08 European-open variant trades inside the Globex trading day)")
    past = False
    if kind == "prop":
        flat = pair["flat_by_close"]["pt"]
        ex = EXIT_PT.get(fid, {}).get(ASSET_CLASS[code])
        if ex is not None and flat is not None:
            past = hm(ex) > hm(flat)
            notes.append(f"flat-by-close gate: documented exit {ex} PT vs flat-by-close {flat} PT")
        elif flat is not None:
            notes.append(f"flat-by-close gate: continuous family inside the main session; F5 says the h_c hold fits "
                         f"(flat-by-close {flat} PT)")
    return ({"news_window_covers_event_trade": covers, "overnight_needed_but_prohibited": overnight,
             "holds_past_flat_by_close": past}, notes)


def data_for(code: str, fid: str, g: dict) -> dict:
    plan = g["codes"][code]["data_plan"]
    clean = plan["clean_test_window"]["months"]
    if fid == "F10":
        bk = plan["book"]
        disc, test = bk["discovery_cost_usd"], bk["test_cost_usd"]
        basis = bk["cost_basis"] + ("; " + bk["note"] if bk.get("note") else "")
        quotes = bk["quotes_to_obtain"]
        schema = f"mbo ({bk['root']}; MBO from {bk['mbo_start']})"
        alt = bk.get("alternative")
    else:
        bars = plan["bars"]
        disc, test = bars["discovery_cost_usd"], bars["test_cost_usd"]
        basis, quotes = bars["cost_basis"], list(bars["quotes_to_obtain"])
        schema = f"ohlcv-1m ({bars['root']} price path)"
        alt = None
        if fid == "F09" and code == "RTY":
            basis += "; leader leg NQ ohlcv-1m owned 2010-06..2024-02 (read)"
            schema += " + NQ leader bars"
        if fid == "F09" and code == "ZL":
            basis += ("; crush legs ZS and ZM ohlcv-1m: discovery owned (2020-12..2024-02), test inside the sealed "
                      "soy-test files (every schema)")
            schema += " + ZS, ZM legs"
    tw = plan["test_window"]
    return {"schema": schema, "discovery_cost_usd": disc, "test_cost_usd": test,
            "all_data_cost_usd": None if disc is None or test is None else r(disc + test, 2),
            "clean_test_window_months": clean,
            "windows": {"discovery": f"{plan['discovery_window']['start']}..{plan['discovery_window']['end']} "
                                     f"(39 months; bars owned: {plan['discovery_window']['bars_owned']})",
                        "test": (f"{tw['start']}..{tw['end']} (43 months; {tw['status']})" if tw["start"]
                                 else tw["status"]),
                        "clean_test_window": f"{clean} months ({plan['clean_test_window']['kind']}: "
                                             f"{plan['clean_test_window']['window']})"},
            "cost_basis": basis, "quotes_to_obtain": quotes, "alternative": alt,
            "unpriced_extras": GF.EXTRAS.get(fid, [])}


def member_calc(code: str, venue: str, vrow: dict, h_c: str, fid: str, g: dict, f4: dict, sr80: dict,
                t1: dict) -> tuple[dict, dict]:
    kind = vrow["kind"]
    und = g["codes"][code]["underlying"]
    timing = g["underlyings"][und]["families"][fid]["timing"]
    row = vrow["rows"][h_c]
    sigma, m, ncap = row["sigma"], row["m"], row["n_cap"]
    c_f, v, S = vrow["c_f"], vrow["tick_value_usd"], vrow["S"]
    l_main = g["codes"][code]["L_main"]
    ky = k_year(fid, timing, ncap)
    k_disc, k_test = ky * T_DISC / DAYS_PER_YEAR, ky * T_TEST / DAYS_PER_YEAR
    n_day = ky / DAYS_PER_YEAR
    e80 = {"disc_G3G4": sr80["disc_G3G4"] * math.sqrt(T_DISC) * sigma / math.sqrt(k_disc),
           "disc_G3": sr80["disc_G3"] * math.sqrt(T_DISC) * sigma / math.sqrt(k_disc),
           "test": sr80["test"] * math.sqrt(T_TEST) * sigma / math.sqrt(k_test)}
    g_be, g_1 = c_f, c_f + 1.0
    det = {"code": code, "venue": venue, "underlying": und, "family_kind": GF.FAMILY_KIND[fid],
           "c_f_ticks": r(c_f), "S": S, "fee_rt_usd": vrow["fee_rt_usd"], "fee_ticks": r(vrow["fee_ticks"]),
           "fee_kind": vrow.get("fee_kind") or vrow.get("fee_status"), "tick_value_usd": v, "h_c": h_c,
           "sigma_hc_ticks": r(sigma), "m_hc_ticks": r(m), "n_cap_hc": ncap, "G_hc": r(row["G"]),
           "g_be_ticks": r(g_be), "g_1_ticks": r(g_1),
           "p_be_emp": r(0.5 + g_be / (2 * m)), "p_1_emp": r(0.5 + g_1 / (2 * m)),
           "p_be_norm": r(0.5 + g_be / (NORMAL_FACTOR * sigma)), "p_1_norm": r(0.5 + g_1 / (NORMAL_FACTOR * sigma)),
           "events_per_year": timing["events_per_year"], "trades_per_event": timing["trades_per_event"],
           "K_year": r(ky, 3), "K_disc": r(k_disc, 3), "K_test": r(k_test, 3), "n_per_day": r(n_day, 6),
           "e80_ticks": {k: r(x) for k, x in e80.items()},
           "gross_needed_for_detection_ticks": {k: r(c_f + x) for k, x in e80.items()},
           "x_cost_per_sigma": r(c_f / sigma, 6), "q_test_edge_per_sigma": r(sr80["test"] * math.sqrt(T_TEST / k_test), 6),
           "f5_check_e80_test_continuous": r(row["e80_test"]) if GF.FAMILY_KIND[fid] == "continuous" else None}
    # prop fit
    if kind == "prop":
        firm = venue
        thr, thr_src = PAYOUT_DAILY[firm]
        reach = math.sqrt(n_day) * sigma * v
        ev, ev_note = news_stop(firm, code, fid, f4, t1)
        gate, gnotes = gates(kind, firm, code, fid, vrow, f4)
        dll_none = str(vrow["dll_source"]).startswith("mll_50k")
        det["prop_fit"] = {
            "dll_usd": "none" if dll_none else vrow["DLL_f"], "dll_source": vrow["dll_source"],
            "mll_usd": vrow["MLL_f"], "mll_type": vrow["mll_type"],
            "dll_ratio_hc": r(row["dll_ratio"]), "mll_ratio_hc": r(row["mll_ratio"]),
            "flat_by_close_pt": vrow["flat_by_close"]["pt"], "latest_start_pt_hc": row["latest_start_pt"],
            "fits_flat_by_close_hc": row["fits_flat_by_close"], "overnight_allowed": vrow["overnight_allowed"],
            "payout_threshold_usd": thr, "payout_source": thr_src,
            "sqrt_n_sigma_v_usd": r(reach, 2), "payout_threshold_exceeds": thr > reach,
            "news_stop_events_per_week": r(ev), "news_note": ev_note, "news_window_items": vrow["news_window_items"],
            "gate": gate, "gate_notes": gnotes}
        if firm in RITHMIC_ROUTES:
            one = c_f - (S / 2 + SLIP_PER_LEG) + E31_TT_MARKOUT
            both = c_f - (S + 2 * SLIP_PER_LEG) + 2 * E31_TT_MARKOUT
            det["queue_limit_variant"] = {
                "route": RITHMIC_ROUTES[firm], "c_lim_passive_entry_market_exit_ticks": r(one),
                "c_lim_both_legs_passive_ticks": r(both),
                "basis": (f"each passive leg replaces a market leg's half-spread S/2 and {SLIP_PER_LEG} slippage with "
                          f"E.31's measured trade-through markout {E31_TT_MARKOUT} ticks per fill (model c, ZM front "
                          "month, DAY; the only measurement). Rithmic's fill rule (forum pointer) under the joint "
                          "reading is at least as strict as trade-through, so this is an optimistic bound; transfer "
                          "from ZM to this product is an assumption; fills that never happen are not priced. Reported "
                          "beside, never scored.")}
    else:
        q6 = vrow["Q6_inputs"]
        gate = {"news_window_covers_event_trade": False, "overnight_needed_but_prohibited": False,
                "holds_past_flat_by_close": False}
        det["own_broker_fit"] = {
            "initial_margin_usd": q6["margin_intraday_initial_usd"],
            "margin_basis": "intraday initial (every band is intraday); overnight initial beside",
            "margin_overnight_initial_usd": q6["margin_overnight_initial_usd"],
            "capital_ceiling_usd": q6["capital_ceiling_usd"], "capital_ceiling_u": q6["capital_ceiling_u"],
            "sigma_day_ticks": r(q6["sigma_cc_ticks"]), "sigma_day_usd": r(q6["sigma_day_usd"], 2),
            "sigma_day_basis": q6["sigma_day_basis"], "sigma_OC_ticks": r(q6["sigma_OC_ticks"]),
            "latest_start_pt_hc": row.get("latest_start_pt"), "fits_main_session_hc": row.get("fits_main_session"),
            "gate": gate,
            "queue_limit_variant": "not computed: spec 8.2 names a Rithmic queue-limit variant; the IBKR route is a "
                                   "real exchange order and no platform fact is recorded in F2_nonprop or "
                                   "F4_venue_ibkr"}
    det["data"] = data_for(code, fid, g)
    pf = det.get("prop_fit") or {}
    ob = det.get("own_broker_fit") or {}
    member = {"code": code, "asset_class": ASSET_CLASS[code], "c_f_ticks": c_f, "sigma_hc_ticks": sigma,
              "tick_value_usd": v, "K_test": k_test, "L_main": l_main, "n_per_day": n_day,
              "dll_usd": pf.get("dll_usd"), "mll_usd": pf.get("mll_usd"),
              "payout_threshold_usd": pf.get("payout_threshold_usd"),
              "news_stop_events_per_week": pf.get("news_stop_events_per_week", 0.0 if kind == "own_broker" else None),
              "gate": pf.get("gate") or ob.get("gate"),
              "initial_margin_usd": ob.get("initial_margin_usd"), "sigma_day_ticks": ob.get("sigma_day_ticks")}
    return member, det


def combo_data(dets: list) -> dict:
    ds = [x["data"] for x in dets]
    disc = None if any(x["discovery_cost_usd"] is None for x in ds) else r(sum(x["discovery_cost_usd"] for x in ds), 2)
    alld = None if any(x["all_data_cost_usd"] is None for x in ds) else r(sum(x["all_data_cost_usd"] for x in ds), 2)
    clean = min(x["clean_test_window_months"] for x in ds)
    return {"discovery_cost_usd": disc, "all_data_cost_usd": alld, "clean_test_window_months": clean,
            "windows": {x_d["code"]: x["windows"] for x_d, x in zip(dets, ds, strict=True)}}


def doc_horizon_vs_band(timing: dict, band: list) -> dict:
    mins = [int(h) for h in band if h != "OC"]
    lo, hi = (min(mins), max(mins)) if mins else (None, None)
    dh = timing.get("horizon_minutes") or []
    inside = [x for x in dh if lo is not None and lo <= x <= hi]
    outside = [x for x in dh if x not in inside]
    return {"documented_minutes": dh, "band_minutes": [lo, hi], "inside_band": inside, "outside_band": outside,
            "statement": ("documented horizon inside B" if not outside else
                          f"documented horizon(s) {outside} min lie outside B ({lo}-{hi} min)")}


# ------------------------------------------------------------------------------------------- build
def build() -> tuple[dict, dict]:
    spec = check_spec()
    g, f5, f4, sr80doc, score = (load(p) for p in (GROUNDWORK_JSON, F5_PATH, F4_PATH, SR80_PATH, SCORE_PATH))
    for doc, name in ((g, "groundwork"), (f5, "F5_holding"), (f4, "F4_facts_unmasked"), (sr80doc, "SR80"),
                      (score, "score32b_out")):
        check_hash(doc, name)
    if not sr80doc["cross_check"]["pass"]:
        raise SystemExit("REFUSED: SR80 cross-check did not pass")
    sr80 = sr80doc["SR80"]
    top15 = score["primary"]["top15"]
    vrows = venue_rows(f5, top15)
    t1 = g["topstep_t1_event_rates"]
    venue_order = [(t["firm"], t["rank"]) for t in top15]

    combos, details, skipped = [], [], []
    seq = [0]

    def add(product, pool, venue, fid, band, h_c, worst, mems):
        und_any = g["codes"][mems[0][0]]["underlying"]
        timing = g["underlyings"][und_any]["families"][fid]["timing"]
        members, dets = [], []
        for code, vrow in mems:
            mb, dt = member_calc(code, venue, vrow, h_c, fid, g, f4, sr80, t1)
            members.append(mb)
            dets.append(dt)
        seq[0] += 1
        cid = f"C{seq[0]:03d}"
        data = combo_data(dets)
        combos.append({"id": cid, "product": product, "pool": pool, "venue": venue, "family": FAMILY_SHORT[fid],
                       "band": band, "h_c": h_c, "members": members, "data": data})
        details.append({"id": cid, "dossier": f"{product or pool['name']}|{fid}", "product": product, "pool": pool,
                        "venue": venue, "family": fid, "family_name": FAMILY_SHORT[fid], "band": band,
                        "band_shortest": band[0], "band_longest": band[-1], "h_c": h_c,
                        "worst_member_G_by_h": {h: r(x) for h, x in worst.items()},
                        "horizon_vs_band": doc_horizon_vs_band(timing, band), "members": dets, "data": data})

    def venues_for(code):
        return [t["firm"] for t in sorted(top15, key=lambda t: t["rank"]) if t["code"] == code] + [OWN_BROKER]

    for code in PRODUCT_ORDER:
        und = g["codes"][code]["underlying"]
        fams = [f for f in GF.FAMILIES if g["underlyings"][und]["families"][f]["applies"]]
        for fid in fams:
            for venue in venues_for(code):
                vrow = vrows[(venue, code)]
                band = band_of(vrow)
                if not band:
                    skipped.append({"what": f"{venue}|{code} {fid}", "reason": "empty F5 band (LR-R2b)"})
                    continue
                h_c, worst = h_c_of([vrow], band)
                add(code, None, venue, fid, band, h_c, worst, [(code, vrow)])
    for p in g["pools"]:
        venues = [f for f, _ in venue_order if all((f, m) in vrows for m in p["members"])]
        venues = list(dict.fromkeys(venues)) + [OWN_BROKER]
        for venue in venues:
            mrows = [vrows[(venue, m)] for m in p["members"]]
            band = [h for h in BAND_H if all(h in band_of(x) for x in mrows)]
            if not band:
                skipped.append({"what": f"{p['name']} at {venue}", "reason": "empty band intersection"})
                continue
            h_c, worst = h_c_of(mrows, band)
            for fid in p["shared_families"]:
                add(None, {"name": p["name"], "members": list(p["members"])}, venue, fid, band, h_c, worst,
                    list(zip(p["members"], mrows, strict=True)))
        for f in dict.fromkeys(f for f, _ in venue_order):
            missing = [m for m in p["members"] if (f, m) not in vrows]
            if missing:
                skipped.append({"what": f"{p['name']} at {f}", "reason": f"no F5 band for {missing} at {f} "
                                "(not top-15 pairs; LR-R2a/b)"})
    skipped = list({s["what"]: s for s in skipped}.values())

    meta = inputs_meta({"groundwork": GROUNDWORK_JSON, "F5_holding": F5_PATH, "F4_facts_unmasked": F4_PATH,
                        "SR80": SR80_PATH, "score32b_out": SCORE_PATH})
    unrated = {
        "spec_sha256": spec, "generated_pdt": now_pdt(),
        "generated_by": "reports/stage_e32b_briefs/work/R2/build_combos.py (DossierWriter-OpusXHigh)",
        "inputs": meta,
        "sr80_test": {"value": sr80["test"], "source": "briefs/work/F5/SR80.json SR80.test"},
        "own_account_capital_ceiling_usd": {"value": None, "source": "docs/DECISIONS.md: none recorded "
                                            "(briefs/F4_venue_ibkr.json capital_ceiling_search); r3_score then uses "
                                            "USD 6,000 (u)"},
        "rho_measured": {},
        "notes": ["Q1-Q3 absent: the CombinationScorer rates them (briefs/R2_Q_ratings.json); work/R2/merge_q.py "
                  "merges them into briefs/R2_combinations.json.", GF.E29_MEASURED,
                  "K_test = K_year x 870 / 252 (continuous: n_cap(h_c) x 870); n_per_day = K_year / 252.",
                  "Every number per combination, with sources, is in work/R2/combos_detail.json."],
        "combinations": combos}
    detail = {"spec_sha256": spec, "generated_pdt": unrated["generated_pdt"], "inputs": meta,
              "SR80": sr80, "T_disc": T_DISC, "T_test": T_TEST, "topstep_t1_event_rates": t1,
              "payout_daily": {k: {"usd": v[0], "source": v[1]} for k, v in PAYOUT_DAILY.items()},
              "rithmic_routes": RITHMIC_ROUTES, "skipped": skipped, "combinations": details}
    return unrated, detail


def main() -> int:
    unrated, detail = build()
    write_json(COMBOS_UNRATED, unrated)
    write_json(COMBOS_DETAIL, detail)
    from collections import Counter
    cnt = Counter(c["venue"] for c in unrated["combinations"])
    npool = sum(1 for c in unrated["combinations"] if c["pool"])
    print(f"combinations {len(unrated['combinations'])} (pools {npool}); by venue {dict(cnt)}; "
          f"skipped {len(detail['skipped'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
