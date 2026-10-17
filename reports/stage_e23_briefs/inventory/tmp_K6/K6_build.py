"""K6 inventory builder (Stage E.23 P1.1, InventoryReaderK6). Reads code docstrings, the K6 freeze
and two return tables only; never opens a bar store. Writes K6.json and K6.md."""
import ast
import json
import re
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e23_briefs/inventory"
FREEZE = "reports/stage_e_k6_member_freeze.json"
FREEZE_SHA = "a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604"


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def doc(mod):
    p = REPO / f"strategy/members/k6/{mod}.py"
    return ast.get_docstring(ast.parse(p.read_text()))


def rule_text(mod):
    paras = [p for p in doc(mod).split("\n\n")]
    keep = [p for i, p in enumerate(paras) if i > 0 and not p.startswith("Copied in structure")]
    return norm(" ".join(keep))


def check(mod, s):
    assert norm(s) in norm(doc(mod)), (mod, s)
    return norm(s)


# ---------------------------------------------------------------- return tables
def table_rows(path, lo, hi):
    lines = (REPO / path).read_text().splitlines()[lo - 1:hi]
    out = {}
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        out[cells[1]] = cells
    return out


E8 = table_rows("reports/E.8_RETURN.md", 215, 241)    # Ord Trial Status Trips Days Mean t MinCov Hold MLL D97exits D97ref Tier
E22 = table_rows("reports/E.22_RETURN.md", 369, 395)  # Ord Trial Tier Status Days Trips theta UCB SE eps power p_upper

freeze = json.loads((REPO / FREEZE).read_text())
members = freeze["members"]

W_EXT = {  # file names in reports/stage_e17_run_manifest.json `stores` (path strings only; no store opened)
    "ZC": ("ZC", "2010-06-07..2019-04-30 (ext2010 store name in the E.17 manifest)"),
    "ZS": ("ZS", "2010-07-01..2019-04-30 (ext2010h store name in the E.17 manifest)"),
    "ZL": ("ZL", "2010-07-01..2019-04-30 (ext2010h store name in the E.17 manifest)"),
    "HE": ("HE", "store 2010-07-01..2019-04-30 (ext2010h); reports/stage_e16_windows.json HE window_start_on_or_after 2017-07-01 (start_month 2017-07; E.20 plan line 48 'HE 2017-07-01')"),
    "LE": ("LE", "store 2010-07-01..2019-04-30 (ext2010h); E.21 R-S3 (multiday/constants.py LE_FIRST; reports/stage_e21_briefs/lead_spec.md section 0): 2010-06-07..2014-12-14 excluded, first mark date on or after 2014-12-15"),
    "ZW": (None, "no W_ext store: reports/stage_e17_run_manifest.json stores.ZW.ext2010 = null"),
    "ZM": (None, "no W_ext store: reports/stage_e17_run_manifest.json stores.ZM.ext2010 = null"),
}
GROUP = {"ZC": "grains", "ZW": "grains", "ZS": "grains", "ZM": "grains", "ZL": "grains", "HE": "livestock", "LE": "livestock"}

SETTLE = {
    "grains": ("reports/stage_e16_settlement.json products.<root>.settle (identical for ZC ZW ZS ZM ZL): 13:15 CT 2010-06-07..2012-06-24; "
               "14:00 CT 2012-06-25..2013-04-07; 13:15 CT 2013-04-08..2015-07-05; 13:15 CT window 13:14:00-13:15:00 2015-07-06..2024-02-29 "
               "(all grade primary, basis direct). base_rules/constants.py PRIOR_SETTLE_CT grains 13:15."),
    "livestock": ("reports/stage_e16_settlement.json products.<root>.settle (identical for HE LE): 13:00 CT 2010-06-07..2014-12-14 "
                  "(primary, basis inferred, window null: pit-based); 13:00 CT window 12:59:30-13:00:00 2014-12-15..2024-02-29 (primary, direct). "
                  "rules/price_limits.py SETTLEMENT_WINDOW_CT livestock [12:59:30, 13:00:00) CT; strategy/members/k6/_limits.py SETTLEMENT_WINDOW_LIVESTOCK."),
}

# ---------------------------------------------------------------- shared input facts
IN_BARS = lambda r: {"input": f"{r} 1-minute bars (own traded root)", "covers_w_ext": W_EXT[r][0] is not None,
                     "covers_w_cf": True, "path": f"reports/stage_e17_run_manifest.json stores.{r}",
                     "stated_range": f"W_ext: {W_EXT[r][1]}; W_cf: step2 store 2019-05-06..2024-02-29"}
IN_SESSION = {"input": "frozen day-session clock O, C (and engine F) per root: grains O 08:30 C 13:15 F 13:18; livestock O 08:30 C 13:00 F 13:03",
              "covers_w_ext": "unknown", "covers_w_cf": True,
              "path": "screening/stage_e_frozen.py load_frozen_tables (E.2a tables; reports/stage_e2a_vehicle_sizes.json per reports/stage_e_start_rule_K6.json day_session); _calendar.py GRAIN_REGULAR_F_CT / LIVESTOCK_REGULAR_F_CT",
              "stated_range": "undated constants. Fact for W_ext: data/calendars/hist2010/grains.json sessions give the grain day session 09:30-13:15 (2010-06-01..2012-05-18), one segment 17:00-14:00 (2012-05-21..2013-04-05), 08:30-13:15 (2013-04-08..2015-07-03), 08:30-13:20 (2015-07-06..2019-05-31); livestock.json: 09:05-13:00 (2010-06-01..2014-10-24, secondary), 08:00-13:00 (2014-10-27..2016-02-26), 08:30-13:00 (from 2016-02-29)"}
IN_GROUPCAL = lambda g: {"input": f"{g} group trade calendar (trade dates, full closures, early halts, late opens) as the engine/bars carry it",
                         "covers_w_ext": True, "covers_w_cf": True,
                         "path": f"W_cf: data/calendars/{g}.py (CALENDAR_COVERAGE 2019-05-01..2026-06-19); W_ext: data/calendars/hist2010/{g}.json",
                         "stated_range": f"data/calendars/hist2010/{g}.json coverage 2010-06-01..2019-05-31" + (" (25 unsourced trade dates, 1.1%)" if g == "livestock" else " (0 unsourced)")}
IN_K6CAL = lambda what: {"input": f"K6 frozen calendar table(s) {what} (strategy/members/k6/_calendar.py)",
                         "covers_w_ext": False, "covers_w_cf": True, "path": "strategy/members/k6/_calendar.py",
                         "stated_range": "TABLE_RANGE 2019-05-01..2026-06-19 (generated literal; a 2010-2019 equivalent would come from data/calendars/hist2010/*.json, which exists, but no such K6 table is on disk)"}
IN_WASDE = {"input": "WASDE release dates (EC-WASDE, 12:00 ET; T = 11:00 CT fixed)", "covers_w_ext": False, "covers_w_cf": True,
            "path": "strategy/members/k6/_wasde.py (from reports/stage_e2b_release_calendar.json)",
            "stated_range": "WASDE_RANGE 2019-05-01..2026-06-19 (85 dates: 2019 8, 2020-2024 12 each, 2025 11, 2026 6); release calendar coverage 2019-05-01..2026-06-21. Not found for 2010-2019: 0 WASDE hits in reports/stage_e14_cal_releases.json (2010-06-01..2019-05-31: NGS, WPSR, FOMC only) and in data/calendars/hist2010/*.json; reports/stage_e20_briefs/shared/grains_class_notes.md line 109 'no WASDE, Crop Production, Crop Progress or Grain Stocks calendar exists on disk'; E.20 plan line 132 dropped k6_wasdepre_drift '(WASDE calendar)'"}
IN_LIMITS = {"input": "HE/LE initial daily price limits (LIMIT_PERIODS) and DROPPED_LIMIT_DATES", "covers_w_ext": False, "covers_w_cf": True,
             "path": "strategy/members/k6/_limits.py (from rules/price_limits.py LIMITS)",
             "stated_range": "LIMIT_RANGE 2019-05-01..2026-06-19; rules/price_limits.py TABLE_WINDOW 2019-05-01..2026-06-19; base_rules/limits.py docstring 'the table starts 2019-05-01'; E.20 plan line 131 dropped k6_limitcont_dir '(limit table starts 2019-05)'. No 2010-2019 limit table found (looked: base_rules/, multiday/, rules/price_limits.py, reports/stage_e16_*)"}
IN_SETTLEWIN = {"input": "D9.7 settlement-proxy window (livestock [12:59:30, 13:00:00) CT; early-halt variant)", "covers_w_ext": "unknown", "covers_w_cf": True,
                "path": "rules/price_limits.py SETTLEMENT_WINDOW_CT / settlement_window_ct; _limits.py SETTLEMENT_WINDOW_LIVESTOCK; _calendar.py LIVESTOCK_EARLY_HALT_CT (2019-05-01..2026-06-19)",
                "stated_range": "window constant; reports/stage_e16_settlement.json: the 12:59:30-13:00:00 window applies 2014-12-15 on; 2010-06-07..2014-12-14 settlement pit-based, 13:00 inferred, window null. LIVESTOCK_EARLY_HALT_CT covers 2019-05..2026-06 only"}
IN_ZM = {"input": "ZM 1-minute bars (signal leg)", "covers_w_ext": False, "covers_w_cf": True, "path": "reports/stage_e17_run_manifest.json stores.ZM",
         "stated_range": "W_ext: stores.ZM.ext2010 = null (no W_ext data); W_cf: step2 2019-05-06..2024-02-29"}
IN_ZL = {"input": "ZL 1-minute bars (signal leg)", "covers_w_ext": True, "covers_w_cf": True, "path": "reports/stage_e17_run_manifest.json stores.ZL",
         "stated_range": "W_ext: ext2010h 2010-07-01..2019-04-30; W_cf: step2 2019-05-06..2024-02-29"}
IN_PRODUCTS = {"input": "vendor tick and vendor_price_factor (rules.products)", "covers_w_ext": "unknown", "covers_w_cf": True,
               "path": "rules/products.py", "stated_range": "undated constants; E.8 label for cp2: 'tick history not source-verified for the research window' (K6-L-16 item 13(a))"}

# ---------------------------------------------------------------- per-module facts
MOD = {
    "cp1": dict(
        trigger_event="every trade date: sign of (close of the 08:59 bar minus open of the trade date's first bar) is nonzero",
        decision={"grains": "12:44", "livestock": "12:29"},
        decision_note="entry intent on the C-31 bar (grains 12:44, livestock 12:29); the signal itself uses bars from the trade date's first bar (grains: 19:00 CT evening bar of the prior calendar day; livestock: 08:30) through the 08:59 bar",
        side_rule=["Signal s = sign(close of the bar at O+29 = 08:59 minus open of the trade date's first bar), in vendor ticks.",
                   "buy if s > 0, sell if s < 0; that exact bar only (S0.6, E.3-L-04)."],
        side_kind="momentum", side_note="side = sign of the trade date's move from its first bar's open to the 08:59 close",
        hold={"grains": "fill 12:45 to exit fill nominally 13:14 (about 29 minutes)", "livestock": "fill 12:30 to exit fill 12:59 (about 29 minutes)"},
        exit_rule="Exit: market intent on the first present bar of CT date d at or after C-2 (grains 13:13, fills nominally 13:14; livestock 12:58, fills 12:59), resent while refused (S0.7, E.3-L-22). The engine's forced flatten at F and its D9.7 exit are the backstops; after either, the member sends nothing more that trade date.",
        events="every trade date with nonzero signal (both signal bars present, one instrument_id)",
        inputs=lambda r: [IN_BARS(r), IN_SESSION, IN_GROUPCAL(GROUP[r]), IN_PRODUCTS],
    ),
    "cp2": dict(
        trigger_event="first bar in [08:45, C) of CT date d whose close is >= OR_high + 4 ticks or <= OR_low - 4 ticks, OR = [08:30, 08:45)",
        decision={"grains": "variable 08:45..13:14", "livestock": "variable 08:45..12:59"},
        decision_note="the decision bar is the first qualifying eligible bar (opening in [O+15, C)); fills at the next open",
        side_rule=["Entry: the first eligible bar whose close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells (non-strict); a market intent on that bar."],
        side_kind="momentum", side_note="side = direction of the trigger-day breakout of the 08:30-08:45 opening range",
        hold={"grains": "75 bars after the entry decision bar, or F (13:18) if earlier", "livestock": "75 bars after the entry decision bar, or F (13:03) if earlier"},
        exit_rule="Exit: 75 minutes after the fill, counted as the MES module counts it (E.3-L-07): the present bars seen while the position is non-zero, from the bar after the entry decision bar; on the 75th, a market intent closing the position (fills at the next open), resent while refused (E.3-L-22). Or the engine's forced flatten at F if earlier. There is NO exit at C-2.",
        events="every trade date with a qualifying breakout bar (at most one entry per trade date)",
        inputs=lambda r: [IN_BARS(r), IN_SESSION, IN_GROUPCAL(GROUP[r]), IN_PRODUCTS],
    ),
    "cp3": dict(
        trigger_event="on the 08:30 bar of d: CLV of the last complete prior daily bar [O, C) is >= 0.8 or <= 0.2",
        decision={"grains": "08:30", "livestock": "08:30"},
        decision_note="decision on the 08:30 bar (fills at the 08:31 open); the condition reads d-1's complete daily bar",
        side_rule=["CLV = (C - L) / (H - L) in ticks, CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict), else no trade."],
        side_kind="other", side_note="side set by the prior complete trade date's close location in its range (close near the high buys, near the low sells): continuation of d-1's location, not a trigger-day move on d",
        hold={"grains": "fill 08:31 to exit fill nominally 13:14", "livestock": "fill 08:31 to exit fill 12:59"},
        exit_rule="Exit: market intent on the first present bar of CT date d at or after C-2 (grains 13:13, fills nominally 13:14; livestock 12:58, fills 12:59), resent while refused (S0.7, E.3-L-10, E.3-L-22). The engine's forced flatten at F and its D9.7 exit are the backstops; after either, nothing more that date.",
        events="trade dates whose prior complete daily bar has CLV >= 0.8 or <= 0.2",
        inputs=lambda r: [IN_BARS(r), IN_SESSION, IN_GROUPCAL(GROUP[r]), IN_PRODUCTS],
    ),
    "crushgap": dict(
        trigger_event="G(d) = GPM_open(d) - GPM_close(d-1) <= -0.02 or >= +0.02 USD/bu, GPM = 0.022 P_ZM + 11 P_ZL - P_ZS, on d in GRAIN_FULL_SESSIONS",
        decision={"grains": "08:30"},
        decision_note="reads the three legs' 08:30 opens of d and 13:14 closes of the prior EC-CAL grain trade date; entry on the 08:30 ZS bar, fill 08:31",
        side_rule=["Entry: G <= -0.02 USD/bu sells ZS; G >= +0.02 buys ZS (non-strict); otherwise no trade."],
        side_kind="other", side_note="side = sign of the overnight change in the crush margin GPM (margin down sells ZS, up buys ZS); since ZS enters GPM with weight -1, a ZS-led margin fall means selling after ZS rose relative to ZM and ZL. The move is a three-leg spread, not ZS's own price",
        hold={"grains": "fill 08:31 to exit fill nominally 13:14"},
        exit_rule="Exit: market intent on the first ZS bar of CT date d at or after C-2 = 13:13 (fills nominally at the 13:14 open), resent while refused (S0.7, E.3-L-22). The engine's forced flatten at F and its D9.7 exit are the backstops; after either, nothing more that trade date.",
        events="grain full-session dates with |G| >= 0.02 USD/bu (all three legs' bars present with matching instrument_id)",
        inputs=lambda r: [IN_BARS(r), IN_ZM, IN_ZL, IN_SESSION, IN_K6CAL("GRAIN_TRADE_DATES, GRAIN_FULL_SESSIONS"), IN_GROUPCAL("grains"), IN_PRODUCTS],
    ),
    "limitcont": dict(
        trigger_event="d-1's D9.7 settlement proxy moved exactly +L or -L ticks (the initial limit) from d-2, and d-2 was not itself a limit close; d in LIVESTOCK_FULL_SESSIONS",
        decision={"livestock": "08:44"},
        decision_note="entry on the 08:44 bar (fills 08:45); the event reads settlement proxies of d-1, d-2, d-3 and the 08:30 bar's instrument_id of d",
        side_rule=["event: S(c, d-1) - S(c, d-2) = +L(d-1) ticks (BUY) or -L(d-1) ticks (SELL), exactly (K6-L-08)"],
        side_kind="momentum", side_note="side = sign of the limit move into d-1's settlement (the event day is d-1; the trade is on d)",
        hold={"livestock": "fill 08:45 to exit fill 12:59, or earlier by D9.7 forced exit"},
        exit_rule="exit: market intent on the first bar at or after C - 2 = 12:58 (fills at the 12:59 open), or earlier by the engine's D9.7 forced exit (S0.7).",
        events="rare: trade dates after an initial-limit settlement move",
        inputs=lambda r: [IN_BARS(r), IN_LIMITS, IN_SETTLEWIN, IN_K6CAL("LIVESTOCK_TRADE_DATES, LIVESTOCK_FULL_SESSIONS, LIVESTOCK_EARLY_HALT_CT"), IN_GROUPCAL("livestock"), IN_PRODUCTS],
    ),
    "wasdepre": dict(
        trigger_event="WASDE date (is_wasde_date) in GRAIN_FULL_SESSIONS with Dr = close(10:29) - open(08:30) nonzero",
        decision={"grains": "10:29"},
        decision_note="entry on the 10:29 bar, fill 10:30; release at 11:00 CT",
        side_rule=["entry: market intent on the bar at 10:29 (fills at the 10:30 open) in the direction of sign(Dr)"],
        side_kind="momentum", side_note="side = sign of the 08:30-10:29 pre-release drift on the WASDE date",
        hold={"grains": "fill 10:30 to exit fill 11:15 (45 minutes, through the 11:00 CT release)"},
        exit_rule="exit: market intent on the bar at 11:14 (fills at the 11:15 open); if the 11:14 bar is missing, on the first later bar (K6-L-12, S0.7).",
        events="WASDE dates: 12 a year (frozen table 2020-2024: 12 each)",
        inputs=lambda r: [IN_BARS(r), IN_WASDE, IN_K6CAL("GRAIN_FULL_SESSIONS"), IN_SESSION, IN_GROUPCAL("grains"), IN_PRODUCTS],
    ),
    "wasdepost": dict(
        trigger_event="WASDE date (is_wasde_date) in GRAIN_FULL_SESSIONS with R = close(11:14) - close(10:59) nonzero",
        decision={"grains": "11:14"},
        decision_note="entry on the 11:14 bar, fill 11:15; the move spans the 11:00 CT release",
        side_rule=["entry: market intent on the bar at 11:14 (fills at the 11:15 open) in the direction of sign(R)"],
        side_kind="momentum", side_note="side = sign of the 10:59-11:14 release-window move",
        hold={"grains": "fill 11:15 to exit fill 13:14"},
        exit_rule="exit: market intent on the first bar at or after 13:13 (fills at the 13:14 open; S0.7).",
        events="WASDE dates: 12 a year (frozen table 2020-2024: 12 each)",
        inputs=lambda r: [IN_BARS(r), IN_WASDE, IN_K6CAL("GRAIN_FULL_SESSIONS"), IN_SESSION, IN_GROUPCAL("grains"), IN_PRODUCTS],
    ),
}
FEATURE = {"crushgap": "k6_crushgap_gap", "limitcont": "k6_limitcont_dir", "wasdepre": "k6_wasdepre_drift"}
CP_FEATURE = {"cp1": "cp1_ret", "cp2": "cp2_range, cp2_brk", "cp3": "cp3_clv"}
ML_VEHICLES = {"ZC", "ZS", "ZL", "HE", "LE"}  # E.20 plan section 'K6 | ZC, ZS, ZL, HE, LE'


def stages(mod, label, root):
    e8, e22 = E8[label], E22[label]
    out = [
        {"stage": "E.8", "window_dates": "research window from 2025-04-01 (to 2026-06-19); "
                                         f"{e8[4]} dates for this trial", "purpose": "screen",
         "source": "reports/E.8_RETURN.md section 'Task 5' table (lines 213-241) and Tiers paragraph",
         "counts": f"trips {e8[3]}, days {e8[4]}, mean {e8[5]} net ticks/day, daily t {e8[6]}"},
        {"stage": "E.22", "window_dates": "research window (power re-run, E.5's method, under W1 and v13)", "purpose": "power",
         "source": "reports/E.22_RETURN.md section 3.1 'Power re-runs'; reports/stage_e22_STATE.md rows A3c, A3e; reports/stage_e22_power_k6/",
         "counts": "replay matched the screening records (K6 54/55; the one difference the cluster record's power-undefined list)"},
        {"stage": "E.22", "window_dates": "2019-05-06..2024-02-29 (S_X 2019-05-06, reports/stage_e22_k6_confirmation_list.json confirmation_window)",
         "purpose": "confirmation", "source": "reports/E.22_RETURN.md section 3.2 '#### K6' table (lines 365-398); verdict file reports/stage_e22_k6_verdict.json",
         "counts": f"days {e22[4]}, trips {e22[5]}, theta_hat {e22[6]}, UCB95 {e22[7]}, p_upper {e22[11]}"},
    ]
    if mod in FEATURE:
        f = FEATURE[mod]
        out.append({"stage": "E.12", "window_dates": "2019-05-06..2024-02 training window (1,068 dates in the K6 Family A tests)", "purpose": "other",
                    "source": "reports/stage_e12_gate0.json tests gate0A_" + f + "_{h60,h120,hF}; reports/E.12_RETURN.md 'Task 6'",
                    "counts": f"ML route v2 Gate 0 Family A pooled signal test of feature {f} (not the member): all three NOT REJECTED; Gate 0 verdict FAIL"})
        out.append({"stage": "E.17 (C1) and E.18 (C1b)", "window_dates": "2010-06-07..2019-04-30 (W_ext; world roots NG NQ ZN 6E GC ZC)", "purpose": "other",
                    "source": "reports/stage_e14_c1_result.json and reports/stage_e18_c1b_result.json guards.C10.{h60,hF}.applicable",
                    "counts": f"ML model feature {f}: 0 applicable rows at h60 and hF (no K6 event read on W_ext)"})
    if mod in CP_FEATURE and root in ML_VEHICLES:
        out.append({"stage": "E.12 / E.17 C1 / E.18 C1b / E.20 search", "window_dates": "E.12 Gate 0 and E.20 search: 2019-05-06..2024-02-29; C1/C1b: 2010-06-07..2019-04-30 (ZC only of K6's roots)",
                    "purpose": "other",
                    "source": "reports/stage_e12_gate0.json (signals cp1_ret, cp2_brk, cp2_range, cp3_clv, family A, root null); reports/stage_e14_c1_result.json guards.C10.hF.applicable (cp* 4538 rows, pooled over 6 roots); reports/stage_e20_plan.md KEPT list",
                    "counts": f"pooled CP-port ML feature(s) {CP_FEATURE[mod]} over all clusters' ports (21 CP ports pooled into 4, reports/E.11_RETURN.md); not this member's own trades"})
    return out


rows = []
for m in members:
    label = m["label"]
    mod = m["module"].split(".")[-1]
    root = [l["root"] for l in m["legs"] if l["traded"]][0]
    sig = [l["root"] for l in m["legs"] if not l["traded"]]
    f = MOD[mod]
    g = GROUP[root]
    e8, e22 = E8[label], E22[label]
    side = " ".join(check(mod, s) for s in f["side_rule"])
    exitr = check(mod, f["exit_rule"])
    dt = f["decision"][g]
    rows.append({
        "trigger_id": label,
        "cluster_or_stage": "K6 (frozen Stage E.8, cluster freeze sha256 " + FREEZE_SHA + ")",
        "member_id": label.split(" ")[0],
        "module": m["module"] + " (factory " + m["factory"] + ")",
        "freeze_file": FREEZE,
        "traded_root": root,
        "vehicle": root + " (q_c 1; full-size, the freeze leg root)",
        "w_ext_root": W_EXT[root][0],
        "w_ext_note": W_EXT[root][1],
        "signal_legs": sig,
        "definition_verbatim": rule_text(mod),
        "trigger_event": f["trigger_event"],
        "decision_time_ct": dt,
        "decision_time_note": f["decision_note"],
        "side_rule": side,
        "side_kind": f["side_kind"],
        "side_note": f["side_note"],
        "intraday_hold": True,
        "hold_note": f["hold"][g],
        "exit_rule_verbatim": exitr,
        "expected_events_per_year": f["events"] + f"; counts reported: E.8 research-window trips {e8[3]} over {e8[4]} dates; E.22 W_cf trips {e22[5]} over {e22[4]} dates",
        "inputs_needed": f["inputs"](root),
        "stages_read": stages(mod, label, root),
        "tier": e8[12],
        "verdicts": [f"E.8 screen: Tier {e8[12]} (reports/E.8_RETURN.md Task 5 table row {e8[0]})",
                     f"E.22 confirmation: Tier {e22[2]}, status '{e22[3]}' (reports/E.22_RETURN.md 3.2 K6 table row {e22[0]})",
                     "E.22 cluster K6: 'no statement'; Tier A K6-limitcont-01 HE 'null by inactivity', 'no edge (first failing: holm)' (reports/E.22_RETURN.md 3.2)"],
        "settlement_note": SETTLE[g] + f" decision_time_ct {dt} is before the {'13:15' if g == 'grains' else '13:00'} CT settlement on every period"
                           + (" (13:14 is the last possible cp2 grain decision bar)" if mod == "cp2" and g == "grains" else "")
                           + (" (12:59 is the last possible cp2 livestock decision bar, inside the 12:59:30-13:00 window's minute)" if mod == "cp2" and g == "livestock" else "")
                           + ("; limitcont reads d-1's settlement proxy, so its decision on d is after d-1's settlement" if mod == "limitcont" else "")
                           + ("; grain settlement was 14:00 CT on 2012-06-25..2013-04-07" if g == "grains" else ""),
        "exclusion": None,
    })

excluded = [
    {"id": "K6-ml-01", "reason": "ML model member: superseded by the Stage E ML route (user decision 2026-09-24, U6); never frozen as a K6 member",
     "source": "reports/stage_e0_catalog_K6.md lines 4, 832-834"},
    {"id": "K6-ovr-01", "reason": "not frozen: excluded by the lead at E.0 (01:52 PDT, question 6), 0 trials; not in reports/stage_e_k6_member_freeze.json",
     "source": "reports/stage_e0_catalog_K6.md lines 6, 745-747"},
    {"id": "K6 catalog excluded list X-01..X-09 and later (K6-crush3-01, K6-crushavg-01, K6-surprise-01, K6-stocksrev-01, K6-relmin-01, K6-cpfade-01, K6-lvrpt-01, K6-expsales-01, ...)",
     "reason": "catalog candidates excluded before freezing; never members, 0 trials", "source": "reports/stage_e0_catalog_K6.md section 2 (line 912 on)"},
    {"id": "ML-route features k6_crushgap_gap, k6_limitcont_dir, k6_wasdepre_drift (E.12 Gate 0, E.17 C1, E.18 C1b, E.20 search)",
     "reason": "ML models and E.20 search configurations, not triggers; listed only as reads under the member rows' stages_read",
     "source": "ml_route_v2/signals/k6.py docstring; reports/stage_e12_gate0.json; reports/stage_e14_c1_result.json; reports/stage_e20_plan.md lines 128-146"},
]

sources = [
    "reports/stage_e23_briefs/brief_inventory.md (whole)",
    "reports/stage_e_k6_member_freeze.json (cluster, created_utc, members, files, members_dir)",
    "strategy/members/k6/{cp1,cp2,cp3,crushgap,limitcont,wasdepre,wasdepost,_wasde,_limits,_calendar,_event_common,_port_common}.py (module docstrings; imports)",
    "strategy/members/k6/_wasde.py lines 21-60 (WASDE_RANGE, dates per year)",
    "strategy/members/k6/_limits.py lines 26-75 (LIMIT_RANGE, LIMIT_PERIODS, SETTLEMENT_WINDOW_LIVESTOCK)",
    "strategy/members/k6/_calendar.py lines 41-46 (TABLE_RANGE, regular F)",
    "reports/E.8_RETURN.md lines 1-30, 200-282 (verdict summary, Task 5 screen table, labels, tiers)",
    "reports/E.22_RETURN.md lines 1-20, 276-300, 360-410 (Part A, K6 confirmation table, verdict); grep K6 over the whole file",
    "reports/stage_e22_STATE.md (grep K6: rows A1a, A3c, A3e, R7, R9)",
    "reports/stage_e_start_rule_K6.json (top-level fields)",
    "reports/stage_e22_k6_confirmation_list.json (top-level fields, start_dates, confirmation_window)",
    "reports/E.{1,2a,2b,6,7,9,10,11,12,13,14,15,16,17,18,19,20,21}_RETURN.md (grep K6; E.11 lines 205-235; E.12 lines 523-560; E.17, E.18 headers; E.20 lines 1-25, 475-485)",
    "progress.md and docs/STAGES.md (grep K6)",
    "reports/stage_e12_gate0.json (tests with signal k6_* and cp*; verdict)",
    "reports/stage_e14_c1_result.json, reports/stage_e18_c1b_result.json (inputs.window, inputs.calendar_inputs, world.roots keys, guards.C10 applicable, panel_counts cp*)",
    "reports/stage_e14_c1_model.json (signals, feature_cols k6)",
    "ml_route_v2/signals/k6.py (docstring)",
    "reports/stage_e11_signal_coverage.md (grep k6)",
    "reports/stage_e16_overlap.md (grep K6/WASDE)",
    "reports/stage_e20_plan.md lines 20-30, 40-52, 108-146",
    "reports/stage_e20_briefs/shared/macro_calendars.md lines 50-64; reports/stage_e20_briefs/shared/grains_class_notes.md lines 104-118",
    "reports/stage_e17_run_manifest.json (stores for ZC ZS ZL HE LE ZW ZM: path strings only)",
    "reports/stage_e16_windows.json (products ZC ZS ZL HE LE)",
    "reports/stage_e16_settlement.json (products settle periods for the 7 roots)",
    "reports/stage_e21_briefs/lead_spec.md lines 10-35; multiday/constants.py lines 15-45",
    "base_rules/constants.py lines 95-112; base_rules/limits.py docstring",
    "rules/price_limits.py (grep TABLE_WINDOW, SETTLEMENT_WINDOW_CT lines 726-772)",
    "data/calendars/hist2010/grains.json, livestock.json (coverage, products, counts, sessions); reports/stage_e16_calendars/ (listing, hist2010_livestock.json coverage)",
    "reports/stage_e14_cal_releases.json (keys, coverage; WASDE count 0); reports/stage_e2b_release_calendar.json (coverage, WASDE rows 85)",
    "data/calendars/grains.py line 183 (CALENDAR_COVERAGE); data/calendars/livestock.py header",
    "screening/stage_e_frozen.py lines 242-262",
    "reports/stage_e0_catalog_K6.md (grep: excluded entries, member headings)",
]

doc_out = {"assignment": "K6", "rows": rows, "excluded": excluded, "sources_read": sources,
           "not_finished": []}
(OUT / "K6.json").write_text(json.dumps(doc_out, indent=1, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- markdown
md = ["# K6 inventory (Stage E.23 P1.1), InventoryReaderK6-OpusHigh", "",
      f"Freeze: {FREEZE} (sha256 {FREEZE_SHA}), 27 members, all intraday. Rows: {len(rows)}. Excluded: {len(excluded)} entries (none of them a frozen trial).",
      "Full fields (verbatim rule text, inputs, stages_read) are in K6.json.", "",
      "| trigger_id | root | W_ext root | signal legs | decision CT | side kind | hold | E.8 trips (research) | E.22 trips (W_cf) | E.8 tier | E.22 status | inputs not covering W_ext (bars or tables) |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    e8, e22 = E8[r["trigger_id"]], E22[r["trigger_id"]]
    miss = [i["input"].split(" (")[0] for i in r["inputs_needed"] if i["covers_w_ext"] is False]
    unk = [i["input"].split(" (")[0].split(":")[0] for i in r["inputs_needed"] if i["covers_w_ext"] == "unknown"]
    md.append(f"| {r['trigger_id']} | {r['traded_root']} | {r['w_ext_root'] or 'none'} | {', '.join(r['signal_legs']) or '-'} | {r['decision_time_ct']} | {r['side_kind']} | {r['hold_note']} | {e8[3]} | {e22[5]} | {e8[12]} | {e22[3]} | "
              + ("; ".join(miss) or "none") + (" (unknown: " + "; ".join(unk) + ")" if unk else "") + " |")
md += ["", "## Facts used by every row", "",
       "- W_ext roots: ZC 2010-06-07..2019-04-30; ZS, ZL 2010-07-01..2019-04-30; HE store 2010-07-01.. but window from 2017-07-01 (stage_e16_windows.json); LE store 2010-07-01.. but E.21 R-S3 excludes up to 2014-12-14. ZW and ZM: no W_ext store (manifest ext2010 null).",
       "- WASDE dates exist only 2019-05-01..2026-06-19 (k6/_wasde.py; release calendar 2019-05-01..2026-06-21). No 2010-2019 WASDE table found (stage_e14_cal_releases.json, hist2010 calendars, E.20 grains notes line 109).",
       "- HE/LE limit tables exist only 2019-05-01..2026-06-19 (k6/_limits.py, rules/price_limits.py TABLE_WINDOW, base_rules/limits.py).",
       "- K6 _calendar.py tables (GRAIN/LIVESTOCK trade dates, full sessions, livestock early halts): 2019-05-01..2026-06-19. Group calendars for 2010-2019 exist: data/calendars/hist2010/grains.json, livestock.json (2010-06-01..2019-05-31).",
       "- Session eras in W_ext (hist2010 calendars): grain day session opened 09:30 until 2012-05-18, ran as one 17:00-14:00 segment 2012-05-21..2013-04-05, 08:30 from 2013-04-08; livestock opened 09:05 until 2014-10-24, 08:00 until 2016-02-26, 08:30 from 2016-02-29. The frozen K6 clock is O 08:30 for all seven roots.",
       "- Settlement (stage_e16_settlement.json): grains 13:15 CT (14:00 on 2012-06-25..2013-04-07; window 13:14-13:15 from 2015-07-06); livestock 13:00 CT (window 12:59:30-13:00 from 2014-12-15; before, inferred, window null). Every K6 decision time is before the same day's settlement.",
       "- Stages that read K6 members' own trades: E.8 screen (research window), E.22 power replay (research window), E.22 confirmation (2019-05-06..2024-02-29). No stage ran a K6 member on W_ext. ML-route reads of K6-derived features (E.12 Gate 0 on W_cf; E.17 C1 and E.18 C1b on W_ext with 0 applicable K6-feature rows; E.20 search on W_cf with pooled CP features only) are listed per row as purpose 'other'.",
       "- Verdicts: E.8 Tier A K6-limitcont-01 HE only (one trip), 26 Tier B; E.22 K6 'no statement' (limitcont HE 'null by inactivity', 10 trips; limitcont LE 'inconclusive', 0 trips; 25 'null').",
       "", "## Excluded", ""]
for e in excluded:
    md.append(f"- {e['id']}: {e['reason']} ({e['source']})")
md += ["", "## Sources read", ""] + [f"- {s}" for s in sources] + ["", "## Not finished", "", "- none"]
(OUT / "K6.md").write_text("\n".join(md) + "\n")
print("rows", len(rows), "excluded", len(excluded))
