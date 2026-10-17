"""K1 inventory builder (Stage E.23 P1.1, InventoryReaderK1-OpusHigh). Writes K1.json and K1.md.

Every value below was copied from the sources listed in SOURCES (code docstrings, freeze, returns,
reports); nothing is computed from bars.
"""
import ast
import json
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e23_briefs/inventory"
FREEZE = "reports/stage_e_k1_member_freeze.json (cluster K1, sha256 cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2, commit 9113abd)"


def rule_bullets(module_file):
    """The module docstring from 'Rule' on (the rule text), verbatim."""
    doc = ast.get_docstring(ast.parse((REPO / module_file).read_text()))
    i = doc.find("Rule")
    return doc[i:] if i >= 0 else doc


# ------------------------------------------------------------------ shared inputs
CAL = {
    "input": "equity group calendar (trade dates, exchange holidays, early halts, engine F; roll blackouts)",
    "covers_w_ext": True,
    "covers_w_cf": True,
    "path": "W_cf: data/calendars/equity.py with data/cme_calendar.py; W_ext: data/calendars/hist2010/equity.json (products ES, MES, NQ, MNQ, RTY, M2K, YM, MYM)",
    "stated_range": "equity.py docstring '2019-05-01..2026-06-19' (CALENDAR_COVERAGE 2019-01-01..2026-12-31); hist2010/equity.json coverage first 2010-06-01, last 2019-05-31, 0 unsourced",
}
TOPSTEP = {
    "input": "engine flatten F (rules.sessions TOPSTEP_HOLIDAYS / TOPSTEP_EARLY_CLOSE_LEAD; 'O 08:30, C 15:00, F 15:08' on regular dates)",
    "covers_w_ext": False,
    "covers_w_cf": True,
    "path": "rules/sessions.py; for 2010-2018 no on-disk table: C1 and E.20 derive Rule H-1 rows in memory with c1_replication/tables.py h1_rows (reports/stage_e20_briefs/backward_swap_table.md row S3: '95 Rule H-1 rows before 2019-05-01')",
    "stated_range": "rules/sessions.py docstring: derived rows 'cover trade dates 2019-05-01..2023-12-31', schedule rows 2024-2026",
}
REL_CF = {
    "input": "release instants read by the ENGINE, not the member (FOMC and ISM_SERVICES for the D9.5a fill guard, NFP, CPI for D9.12, event-window cost); E.7: 'No member reads a release (FOMC 10, NFP 14, ISM_SERVICES 15 rows per root are harness inputs)'",
    "covers_w_ext": False,
    "covers_w_cf": True,
    "path": "W_cf: reports/stage_e2b_release_calendar.json (FOMC, NFP, CPI, ISM_SERVICES, ...); W_ext: reports/stage_e14_cal_releases.json holds FOMC (with NGS, WPSR) only",
    "stated_range": "e2b calendar coverage 2019-05-01..2026-06-21; e14 calendar coverage 2010-06-01..2019-05-31 for FOMC, NGS, WPSR; no 2010-2019 NFP, CPI or ISM Services calendar (reports/stage_e20_product_summary.md: 'no ISM Services release calendar for 2010-2019'; 'the 2010-2019 release calendars hold FOMC (and NG storage, WPSR) but not NFP, CPI, PPI, GDP, ISM, ...')",
}
FULLSESS = {
    "input": "EQUITY_TRADE_DATES and EQUITY_FULL_SESSIONS literal tables (entry dates; 'trade date d-1')",
    "covers_w_ext": False,
    "covers_w_cf": True,
    "path": "strategy/members/k1/_calendar.py (generator reports/stage_e7_briefs/gen_k1_tables.py); W_ext: no on-disk table found; E.20 derived it in memory from hist2010/equity.json (reports/stage_e20_briefs/backward_swap_table.md row S4: '2247 dates 2010-06-01..2019-05-31 ... Overlap: 22 = 22 dates, equal', verdict NEEDS-DERIVATION)",
    "stated_range": "TABLE_RANGE = (\"2019-05-01\", \"2026-06-19\"); EQUITY_TRADE_DATES 1,846, EQUITY_FULL_SESSIONS 1,779 (E.7 return Task 2)",
}
VXN = {
    "input": "VXN daily close (Cboe VXN_History.csv), V = close of the EQUITY_TRADE_DATES entry before d",
    "covers_w_ext": False,
    "covers_w_cf": True,
    "path": "strategy/members/k1/_vxn.py (literal, from data/vendor/index_history/vxn/VXN_History.csv; raw file not opened, its own first date is not stated in any doc read)",
    "stated_range": "VXN_RANGE = (\"2019-04-30\", \"2026-06-19\"), 1,794 rows = 1,797 less DROPPED_VXN {2021-04-02, 2021-12-24, 2024-02-01} (W_cf dates 2021-04-05 and 2024-02-02 have no V); reports/stage_e20_product_summary.md: 'the VXN literal table does not cover 2010-2019 (NQ reader)'",
}


def bars_input(root, w_ext_root):
    if w_ext_root == "NQ":
        ext = (True, "data/processed_hist/ext2010/NQ/ohlcv-1m_NQ_v_0_2010-06-07_2019-04-30_ext2010.parquet (manifest only; not opened)",
               "ext2010 NQ file 2010-06-07..2019-04-30; reports/stage_e16_windows.json NQ start_month 2010-07")
    elif w_ext_root == "RTY":
        ext = (True, "data/processed_hist/ext2010h/RTY/ohlcv-1m_RTY_v_0_2010-07-01_2019-04-30_ext2010h.parquet (manifest only; not opened)",
               "file named 2010-07-01..2019-04-30, but reports/stage_e16_windows.json RTY start_month 2017-06 and reports/stage_e16_settlement.md 'RTY's first CME trade date is 2017-07-10'")
    else:
        ext = (False, "none: YM/MYM has no ext2010 entry (reports/stage_e17_run_manifest.json YM ext2010 null)", "none")
    cf_root = {"MNQ": "NQ", "M2K": "RTY", "MYM": "YM"}[root]
    return {
        "input": f"price bars of the traded vehicle {root} (price path {cf_root} in E.12 / v13 'MNQ -> NQ' declaration, reports/E.22_RETURN.md line 703)",
        "covers_w_ext": ext[0],
        "covers_w_cf": True,
        "path": f"W_ext: {ext[1]}; W_cf: data/processed_step2/{cf_root}/ohlcv-1m_{cf_root}_v_0_2019-05-06_2024-02-29_step2.parquet (manifest only; not opened); no {root} step2 store (E.7: a K1 confirmation 'would need MNQ, M2K and MYM step 2')",
        "stated_range": f"W_ext: {ext[2]}; W_cf: {cf_root} S_X 2019-05-06..2024-02-29 (reports/stage_e12_phase1_bars.json)",
    }


SETTLE = {
    "NQ": "reports/stage_e16_settlement.md: NQ, YM settlement 15:15 CT 2010-06-07..2020-10-25 (period 15:14:30-15:15:00), 15:00 CT 2020-10-26..2024-02-29 (14:59:30-15:00:00); the frozen C 15:00 'disagrees' before 2020-10-26.",
    "RTY": "reports/stage_e16_settlement.md: RTY not listed on CME before 2017-07-10; settlement 15:15 CT 2017-07-10..2020-10-25, 15:00 CT 2020-10-26..2024-02-29.",
    "YM": "reports/stage_e16_settlement.md: NQ, YM settlement 15:15 CT 2010-06-07..2020-10-25, 15:00 CT 2020-10-26..2024-02-29 (MYM itself not listed there).",
}

E7_SCREEN = {
    "stage": "E.7",
    "window_dates": "research window 2025-04-01..2026-06-12, 299 trade dates (316 less 15 roll-blackout dates and 2 UR-1 dates)",
    "purpose": "screen",
    "source": "reports/E.7_RETURN.md section 2, Task 5 (screen table); reports/stage_e7_k1_screen/<trial>_research.json",
}
E7_POWER = {
    "stage": "E.7",
    "window_dates": None,
    "purpose": "power",
    "source": "reports/E.7_RETURN.md Task 5: 'Power `not_run` (StartRuleMissing) on every record' (record field power = not_run)",
}


def e12(root, feats):
    veh_row = {"MNQ": "gate0B_MNQ_h60/h120/hF", "M2K": "gate0B_M2K_h60/h120/hF", "MYM": "gate0B_MYM_h60/h120/hF"}[root]
    return {
        "stage": "E.12",
        "window_dates": "W_cf training window S_X 2019-05-06..2024-02-29 (price path " + {"MNQ": "NQ", "M2K": "RTY", "MYM": "YM"}[root] + ")",
        "purpose": "other",
        "source": f"ML route v2 Gate 0 (reports/stage_e12_gate0.md Family A rows {feats} pooled over vehicles; Family B {veh_row}; feature definitions docs/STAGE_E_ML_V2_DESIGN.md V2.3, reports/stage_e11_signal_coverage.md lines 43-44). The member's decision variable entered as a feature at the model's decision times; not a test of the member's own entry/exit.",
    }


def e20(feats, root):
    return {
        "stage": "E.20",
        "window_dates": "W_cf search window 2019-05-06..2024-02-29 (step2 " + {"MNQ": "NQ", "M2K": "RTY"}[root] + " store); backward W_ext read NOT run",
        "purpose": "other",
        "source": f"reports/stage_e20_plan.md sections 1-2 (K1 vehicles MNQ (NQ), M2K (RTY)) and reports/stage_e20_product_summary.md KEPT list ({feats}); reports/E.20_RETURN.md section 1: 'Search screen: FAIL' and 'A failed screen ends Part C: no freeze, no backward read, E20-B1 not run'. Feature in a pooled ML search, not a test of the member.",
    }


E12_VERDICT = "E.12 Gate 0 (ML, pooled): 'Verdict: **FAIL**. Passing pairs: none.' (reports/stage_e12_gate0.md); vehicle row(s) {} decision 'FAIL'"
E20_VERDICT = "E.20 ML search: 'Search screen: FAIL.' (reports/E.20_RETURN.md section 1)"


def e7_verdict(label, mean, t, trips):
    return (f"E.7: Tier 'B'; screen record passes False (mean {mean} net ticks/contract/day, daily t {t}, {trips} trips; "
            "reports/E.7_RETURN.md Task 5 table); 'Tier A is empty, so K1 has no Holm family and no edge candidate.' (Task 7)")


E7 = {  # label: (mean, t, trips) from reports/E.7_RETURN.md Task 5 table
    "K1-cp1-01 MNQ": ("+4.4725", "+0.333", 284), "K1-cp1-01 M2K": ("-2.9538", "-0.975", 285),
    "K1-cp1-01 MYM": ("-8.2648", "-1.822", 286), "K1-cp2-01 MNQ": ("-8.4855", "-0.293", 296),
    "K1-cp2-01 M2K": ("+2.8543", "+0.366", 297), "K1-cp2-01 MYM": ("-10.7871", "-1.071", 295),
    "K1-cp3-01 MNQ": ("+10.3082", "+0.285", 118), "K1-cp3-01 M2K": ("-14.1300", "-1.287", 140),
    "K1-cp3-01 MYM": ("-16.1497", "-1.218", 131), "K1-vxnband-01 MNQ": ("-11.5237", "-0.775", 25),
    "K1-vwap-01 MNQ": ("-56.3758", "-1.115", 3502),
}

MEMBERS = {
    "cp1": dict(
        file="strategy/members/k1/cp1.py",
        trigger_event="every equity trade date: s = sign(close of the 08:59 bar - open of the trade date's first bar, the 17:00 CT bar of CT date d-1), nonzero, both bars present with one instrument_id",
        decision_time_ct="08:59 (signal bar; last bar the decision reads); entry intent on the 14:29 bar, fill at the 14:30 open",
        side_rule="buy if s > 0, sell if s < 0",
        side_kind="momentum",
        exit_rule="Exit: market intent on the first present bar of CT date d at or after C-2 = 14:58 (fills nominally at the 14:59 open), resent while refused (S0.7, E.3-L-22). The engine's forced flatten at F and its D9.7 exit are the backstops; after either, the member sends nothing more that trade date.",
        events="every equity trade date with nonzero signal (about 250 a year); E.7 research window counts: MNQ 284, M2K 285, MYM 286 trips in 299 dates",
        feats_e12="gate0A_cp1_ret_h60/h120/hF", feats_e20="cp1_ret", extra_inputs=[],
    ),
    "cp2": dict(
        file="strategy/members/k1/cp2.py",
        trigger_event="first bar opening in [08:45, 15:00) of CT date d whose close >= OR_high + 4 vendor ticks (buy) or <= OR_low - 4 ticks (sell); OR = [08:30, 08:45) bars",
        decision_time_ct="variable: the close of the first qualifying bar in [08:45, 15:00); latest possible decision bar 14:59",
        side_rule="the first eligible bar whose close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells",
        side_kind="momentum",
        exit_rule="Exit: 75 minutes after the fill, counted as the MES module counts it (B-H1; E.3-L-07): the present bars seen while the position is non-zero, from the bar after the entry decision bar; on the 75th, a market intent closing the position (fills at the next open), resent while refused (E.3-L-22). Or the engine's forced flatten at F if earlier. There is NO exit at C-2 (E.3-L-07). After an engine-forced exit (F, D9.7) the member sends nothing more that trade date.",
        events="every equity trade date with a breakout beyond the 15-minute range (at most one entry a day); E.7 research window counts: MNQ 296, M2K 297, MYM 295 trips in 299 dates",
        feats_e12="gate0A_cp2_range / gate0A_cp2_brk h60/h120/hF", feats_e20="cp2_range, cp2_brk",
        extra_inputs=[{
            "input": "vendor tick size of the traded vehicle (4-tick buffer); label 'tick history not source-verified' (E.7, C7)",
            "covers_w_ext": "unknown", "covers_w_cf": "unknown",
            "path": "rules.products (date-independent); reports/E.7_RETURN.md section 1 label and section 6 (R-T3-2)",
            "stated_range": "not stated by date; E.7: 'the tick-history confirmation (C7) owed before any K1 confirmation bar is read'",
        }],
    ),
    "cp3": dict(
        file="strategy/members/k1/cp3.py",
        trigger_event="on the 08:30 bar of CT date d: prior COMPLETE day's CLV = (C - L)/(H - L) of its [08:30, 15:00) bars >= 0.8 (buy) or <= 0.2 (sell); Range > 0; no early_halt_ct on the 08:30 bar; instrument guard",
        decision_time_ct="08:30 (entry intent on the 08:30 bar at its close, fill at the 08:31 open; the condition reads only d-1's daily bar, closed at 14:59 on d-1)",
        side_rule="CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict), else no trade",
        side_kind="other: side from the PRIOR complete day's close location in its range (continuation of d-1's close location), not a trigger-day move",
        exit_rule="Exit: market intent on the first present bar of CT date d at or after C-2 = 14:58 (fills nominally at the 14:59 open), resent while refused (S0.7, E.3-L-10, E.3-L-22). The engine's forced flatten at F and its D9.7 exit are the backstops; after either, nothing more that date.",
        events="equity trade dates after a complete day with CLV >= 0.8 or <= 0.2; E.7 research window counts: MNQ 118, M2K 140, MYM 131 trips in 299 dates",
        feats_e12="gate0A_cp3_clv_h60/h120/hF", feats_e20="cp3_clv", extra_inputs=[],
    ),
    "vxnband": dict(
        file="strategy/members/k1/vxnband.py",
        trigger_event="EQUITY_FULL_SESSIONS date with V (VXN close of the prior equity trade date) < 20 or >= 30, and a bar in [08:30, 14:29) whose close breaches C_prev x (1 +/- V/1600); first breach only",
        decision_time_ct="variable: the close of the first breach bar in [08:30, 14:29); latest possible entry-intent bar 14:28 (V itself read on the 08:30 bar, at 08:31)",
        side_rule="sell iff 1600 x (close_t - C_prev) > C_prev x V, buy iff 1600 x (close_t - C_prev) < -(C_prev x V), strict",
        side_kind="fade",
        exit_rule="Exit (K1-L-05): market intent on the first present bar of CT date d opening at or after the entry-intent bar + 30 minutes, while the position is non-zero and nothing is pending; resent while refused (S0.7). The latest entry-intent bar is 14:28, so the latest exit intent bar is 14:58 (fill 14:59). The engine's flatten at F is the backstop; after an engine closure the member sends nothing more that date.",
        events="full-session dates in the VXN regime with a band breach (at most one a day); E.7 research window: '97 of 287 full-session window dates had V in regime ... 25 traded (13 at V >= 30, 12 at V < 20)'",
        feats_e12="gate0A_k1_vxn_regime / gate0A_k1_vxn_band h60/h120/hF", feats_e20=None,
        extra_inputs=[VXN, FULLSESS],
    ),
    "vwap": dict(
        file="strategy/members/k1/vwap.py",
        trigger_event="every bar t in [08:30, 14:57) of an EQUITY_FULL_SESSIONS date: s_t = sign(close_t vs session VWAP from 08:30); flat -> enter s_t; opposite position with 1-minute hold met -> exit and reverse; at most 20 entry intents a day",
        decision_time_ct="variable: every bar opening in [08:30, 14:57); latest rule-intent bar 14:56",
        side_rule="flat, s_t != 0, fewer than 20 entry intents today: a market intent of q_c in direction s_t; position opposite to s_t (s_t != 0) and the minimum hold met: an exit intent closing the position, then, if fewer than 20 entry intents today, an entry intent of q_c in direction s_t",
        side_kind="other: stop-and-reverse; side = sign of the bar close against the running session VWAP (3 x C_t x sum(vol) - sum((H + L + C) x vol)), not a single trigger-day move",
        exit_rule="Final exit: a market intent on the first present bar at or after C-2 = 14:58 (fills at the 14:59 open), resent while refused; no rule intent from the 14:57 bar on. (Reversal exits as in the rule window; instrument-change exit per K1-L-07.)",
        events="every EQUITY_FULL_SESSIONS date, up to 20 entries a day; E.7 research window: 3,502 trips, 'vwap traded 286 dates, about 12 trips a day, 61 dates at the cap of 20'",
        feats_e12="gate0A_k1_vwap_dist_h60/h120/hF", feats_e20="k1_vwap_dist", extra_inputs=[FULLSESS],
    ),
}

freeze = json.loads((REPO / "reports/stage_e_k1_member_freeze.json").read_text())
rows = []
for m in freeze["members"]:
    key = m["module"].rsplit(".", 1)[1]
    spec = MEMBERS[key]
    label = m["label"]
    member_id, root = label.split(" ")
    w_ext_root = {"MNQ": "NQ", "M2K": "RTY", "MYM": None}[root]
    settle_root = {"MNQ": "NQ", "M2K": "RTY", "MYM": "YM"}[root]
    stages = [E7_SCREEN, E7_POWER, e12(root, spec["feats_e12"])]
    verdicts = [e7_verdict(label, *E7[label]),
                E12_VERDICT.format("gate0B_" + root + "_h60/h120/hF")]
    if spec["feats_e20"] and root in ("MNQ", "M2K") and not (key == "vwap" and root != "MNQ"):
        stages.append(e20(spec["feats_e20"], root))
        verdicts.append(E20_VERDICT)
    inputs = [bars_input(root, w_ext_root), CAL, TOPSTEP, REL_CF] + spec["extra_inputs"]
    dec = spec["decision_time_ct"]
    if key == "cp2":
        timing = (" cp2's entry decision can be as late as the 14:59 bar (close 15:00, fill at the 15:00 open) and its exit is 75 bars"
                  " after entry or the engine F 15:08, so a cp2 position can be open through the 15:00 settlement (2020-10-26 on) but is"
                  " flat by 15:08, before the 15:15 settlement of the earlier regime.")
    else:
        timing = (" The decision time and the latest exit fill (14:59 open) precede 15:00, so they precede the settlement in both regimes.")
    settle = SETTLE[settle_root] + timing
    if label == "K1-cp3-01 MNQ":
        verdicts.append("E.7: 'K1-cp3-01 MNQ's Tier B rests on four MLL-liquidated days (flagged)' (section 1); 'The lead's reading: the tier stands.' (Task 7)")
    rows.append({
        "trigger_id": label,
        "cluster_or_stage": "K1 (Stage E.7)",
        "member_id": member_id,
        "module": m["module"] + " (" + spec["file"] + ", factory " + m["factory"] + ")",
        "freeze_file": FREEZE,
        "traded_root": root,
        "vehicle": root + " q_c " + {"MNQ": "1", "M2K": "3", "MYM": "3"}[root],
        "w_ext_root": w_ext_root,
        "signal_legs": [],
        "definition_verbatim": rule_bullets(spec["file"]),
        "trigger_event": spec["trigger_event"],
        "decision_time_ct": dec,
        "side_rule": spec["side_rule"],
        "side_kind": spec["side_kind"],
        "intraday_hold": True,
        "exit_rule_verbatim": spec["exit_rule"],
        "expected_events_per_year": spec["events"],
        "inputs_needed": inputs,
        "stages_read": stages,
        "tier": "B",
        "verdicts": verdicts,
        "settlement_note": settle,
        "exclusion": None,
    })

EXCLUDED = [
    {"id": "K1-ml-01", "reason": "ML model member; excluded in the E.0 catalog (no code, not in the freeze); reports/stage_e11_briefs/member_inventory.md line 413, reports/E.7_RETURN.md K1-L-01 ('KF1 is K1-ml-01's feature row (excluded, U6)')"},
    {"id": "K1-predrift-01", "reason": "excluded by E.0 with 0 trials (not frozen, no module); progress.md line 2488 'K1-predrift-01 excluded (MES's E family re-run on the Dow)'; reports/E.10_RETURN.md line 143"},
    {"id": "K1 cluster book (reports/stage_e7_k1_screen/K1_research_cluster.json)", "reason": "a cluster summary of the 11 trials, not itself a trigger"},
]

SOURCES = [
    "reports/stage_e23_briefs/brief_inventory.md (whole)",
    "reports/stage_e_k1_member_freeze.json (cluster, created_utc, members, files)",
    "strategy/members/k1/cp1.py, cp2.py, cp3.py, vxnband.py, vwap.py, _event_common.py, _port_common.py (module docstrings)",
    "strategy/members/k1/_vxn.py (docstring, VXN_RANGE line 25, dropped-rows comment lines 27-42); strategy/members/k1/_calendar.py (docstring, TABLE_RANGE line 33, REGULAR_F_CT line 35)",
    "reports/E.7_RETURN.md lines 1-30, 170-245 (Tasks 1b-7, screen table), K1 grep lines (sections 5-6)",
    "reports/stage_e7_k1_screen/K1_K1-*_research.json (screen scalar fields and power status only)",
    "reports/E.*_RETURN.md grep for K1 (E.1, E.2a, E.2b, E.6, E.8-E.22: only freeze checks except E.2a labels, E.12 ranking, E.20 universe, E.22 line 703)",
    "reports/stage_e7_STATE.md, reports/stage_e0_STATE.md (grep K1); progress.md (grep K1); docs/STAGES.md lines 105-107",
    "reports/E.11_RETURN.md lines 1-30; docs/STAGE_E_ML_V2_DESIGN.md lines 117, 145-147, 435-470",
    "reports/stage_e11_briefs/member_inventory.md (grep K1); reports/stage_e11_signal_coverage.md lines 43-44, 152, 194",
    "reports/E.12_RETURN.md lines 1-12, 470-486; reports/stage_e12_gate0.md (headers, gate0A k1/cp rows, gate0B MNQ/M2K/MYM rows); reports/stage_e12_phase1_bars.json (NQ, RTY, YM scalar fields)",
    "reports/E.14_RETURN.md lines 1-25; reports/stage_e14_c1_model.json lines 20-34 (k1 applicability 0); reports/stage_e18_c1b_result.json lines 115-126; reports/E.18_RETURN.md lines 1-25",
    "reports/E.20_RETURN.md lines 1-25, grep; reports/stage_e20_plan.md lines 15-45, 330-360; reports/stage_e20_product_summary.md lines 42-125",
    "reports/stage_e20_briefs/backward_swap_table.md lines 25-36, 51 (rows S1-S7)",
    "data/calendars/hist2010/equity.json (coverage, products, counts only); data/calendars/equity.py (docstring grep)",
    "reports/stage_e14_cal_releases.json and reports/stage_e2b_release_calendar.json (top-level coverage fields only)",
    "data/vendor/index_history/vxn/manifest.jsonl (fields, no data rows); reports/stage_e7_member_specs.md (headings, VXN range lines)",
    "reports/stage_e17_run_manifest.json (NQ, RTY, YM entries); reports/stage_e16_windows.json (NQ, RTY entries); reports/stage_e16_settlement.md (equity rows lines 32-37, 57-104)",
    "multiday/constants.py and reports/stage_e21_briefs/lead_spec.md (grep equity/settle); rules/sessions.py (docstring grep); c1_replication/tables.py h1_rows signature",
]

NOTES = [
    "E.14 (C1), E.17 (C1 run, stopped) and E.18 (C1b) list k1_vwap_dist, k1_vxn_regime and k1_vxn_band in the frozen feature list, but they apply on 0 NG rows (reports/stage_e14_c1_model.json, reports/stage_e18_c1b_result.json C10 'applicable' 0); the cp1/cp2/cp3 features there are NG's own ports (K4), so no K1 trigger was read in those stages.",
    "No K1 trial was ever confirmed or read on W_ext as a member: E.7 lists the confirmation as needing MNQ, M2K, MYM step 2 (not bought); E.20's backward read was not run.",
    "W_cf data exist for NQ, RTY and YM (E.12 phase-1 step2 stores, S_X 2019-05-06); W_ext data exist for NQ (2010-06-07 store, window 2010-07) and RTY (window 2017-06, CME listing 2017-07-10); none for YM/MYM.",
    "E.12 and E.20 reads are ML feature reads at the model's own decision times and horizons (h60, h120, hF), not the members' entries and exits.",
]

doc = {"assignment": "K1", "rows": rows, "excluded": EXCLUDED, "sources_read": SOURCES,
       "not_finished": [], "notes": NOTES}
(OUT / "K1.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------ markdown
def cell(s):
    return str(s).replace("|", "/").replace("\n", " ")

md = ["# Stage E.23 P1.1 inventory: K1 (equity index)", "",
      "Writer InventoryReaderK1-OpusHigh, 2026-10-17. Brief reports/stage_e23_briefs/brief_inventory.md. "
      "Freeze " + FREEZE + ". Full rows (verbatim rule text, inputs, sources) in K1.json.", "",
      f"**Rows: {len(rows)}. Excluded: {len(EXCLUDED)}.** All 11 trials: Tier B (E.7), intraday, one traded leg, no other root read.", "",
      "| # | trigger_id | module | w_ext_root | trigger_event | decision_time_ct | side_kind | exit | expected events | stages_read | tier |",
      "|---|---|---|---|---|---|---|---|---|---|---|"]
for i, r in enumerate(rows, 1):
    sr = "; ".join(f"{s['stage']} {s['purpose']}" for s in r["stages_read"])
    ex = {"cp1": "14:58 bar (fill 14:59)", "cp2": "75 bars after entry or F", "cp3": "14:58 bar (fill 14:59)",
          "vxnband": "entry bar + 30 min (latest 14:58)", "vwap": "reverse on signal; final 14:58 bar"}[r["module"].split(" ")[0].rsplit(".", 1)[1]]
    md.append(f"| {i} | {r['trigger_id']} | {r['module'].split(' ')[0]} | {r['w_ext_root']} | {cell(r['trigger_event'])} | "
              f"{cell(r['decision_time_ct'])} | {cell(r['side_kind'])} | {ex} | {cell(r['expected_events_per_year'])} | {sr} | {r['tier']} |")
md += ["", "## Inputs (per member; covers W_ext / W_cf)", "",
       "| member | input | W_ext | W_cf | path / stated range |", "|---|---|---|---|---|"]
seen = set()
for r in rows:
    mid = r["member_id"]
    for inp in r["inputs_needed"]:
        k = (mid, inp["input"][:40]) if not inp["input"].startswith("price bars") else (r["trigger_id"], "bars")
        if k in seen:
            continue
        seen.add(k)
        md.append(f"| {r['trigger_id'] if k[1]=='bars' else mid} | {cell(inp['input'])} | {inp['covers_w_ext']} | {inp['covers_w_cf']} | {cell(inp['path'])}; {cell(inp['stated_range'])} |")
md += ["", "## Stages read", "",
       "- E.7 screen: research window 2025-04-01..2026-06-12 (299 dates), all 11; power not_run (StartRuleMissing).",
       "- E.12 Gate 0 (other, ML feature): W_cf 2019-05-06..2024-02-29 on NQ, RTY, YM paths; all 11 members' variables (cp1_ret, cp2_range/brk, cp3_clv, k1_vwap_dist, k1_vxn_regime/band). Verdict FAIL.",
       "- E.20 ML search (other, ML feature): W_cf 2019-05-06..2024-02-29 on NQ and RTY; cp1/cp2/cp3 (MNQ, M2K rows) and k1_vwap_dist (MNQ); k1_vxn_* dropped (no 2010-2019 VXN). Backward read not run. Verdict FAIL.",
       "- Not read: W_ext as a member or feature (none); E.14/E.17/E.18 (K1 features applicable on 0 NG rows).", "",
       "## Settlement", "",
       "- " + SETTLE["NQ"], "- " + SETTLE["RTY"], "- " + SETTLE["YM"],
       "- cp1, cp3, vxnband, vwap: decision and latest exit fill (14:59 open) before 15:00 CT. cp2: entry decision up to the 14:59 bar, exit 75 bars later or at F 15:08, so it can hold through the 15:00 settlement (2020-10-26 on); flat before 15:15 (earlier regime).", "",
       "## Excluded", ""]
md += [f"- {e['id']}: {e['reason']}" for e in EXCLUDED]
md += ["", "## Notes", ""] + [f"- {n}" for n in NOTES]
md += ["", "## Sources read", ""] + [f"- {s}" for s in SOURCES]
md += ["", "## Not finished", "", "- none"]
(OUT / "K1.md").write_text("\n".join(md) + "\n")
print("rows", len(rows), "excluded", len(EXCLUDED))
