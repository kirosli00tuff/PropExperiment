"""K2 inventory builder (Stage E.23 P1.1, InventoryReaderK2). Reads only code, freezes and reports.

Writes reports/stage_e23_briefs/inventory/K2.json and K2.md. Opens no bar store.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "reports/stage_e23_briefs/inventory"
FREEZE = "reports/stage_e_k2_member_freeze.json"
K2DIR = REPO / "strategy/members/k2"
ROOTS = ("ZT", "ZF", "ZN", "TN", "ZB", "UB")
TENOR = {"ZT": "2Y", "ZF": "5Y", "ZN": "10Y", "TN": "10Y", "ZB": "30Y", "UB": "30Y"}

E3_ORD = {}  # label -> (ordinal, trips) from reports/E.3_RETURN.md section 3 table
E3_TABLE = REPO / "reports/E.3_RETURN.md"


def e3_rows() -> None:
    for line in E3_TABLE.read_text(encoding="utf-8").splitlines()[228:275]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 13 and cells[0].isdigit():
            E3_ORD[cells[1]] = {"ordinal": int(cells[0]), "trips": int(cells[2]),
                                "mean": cells[3], "t": cells[5], "screen": cells[6],
                                "tier": cells[12]}


def docstring_rule(module: str) -> str:
    src = (K2DIR / f"{module}.py").read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    lines = doc.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(("Rule", "On each", "ZN and ZB only")):
            return "\n".join(lines[i:]).strip()
    return doc.strip()


# ---------------------------------------------------------------- shared inputs
W_EXT_FIRST = {"ZN": "2010-06 (ext2010 store, trade dates from 2010-06-07)",
               "ZT": "2010-07 (ext2010h store, from 2010-07-01)",
               "ZF": "2010-07 (ext2010h store, from 2010-07-01)",
               "ZB": "2010-07 (ext2010h store, from 2010-07-01)",
               "UB": "2010-07 (ext2010h store, from 2010-07-01)",
               "TN": "2016-01 (ext2010h store named from 2010-07-01, but TN was listed 2016-01-11: "
                     "reports/E.16_RETURN.md line 213; 'TN from 2016-01', reports/E.17_RETURN.md line 25)"}


def bars_input(root: str) -> dict:
    plan = "ext2010" if root == "ZN" else "ext2010h"
    start = "2010-06-07" if root == "ZN" else "2010-07-01"
    return {
        "input": f"price bars of the traded vehicle {root} (own root; vehicle = exposure, "
                 "reports/stage_e2a_vehicles.json)",
        "covers_w_ext": True, "covers_w_cf": True,
        "path": f"W_ext: data/processed_hist/{plan}/{root}/ohlcv-1m_{root}_v_0_{start}_2019-04-30_{plan}.parquet; "
                f"W_cf: data/processed_step2/{root}/ohlcv-1m_{root}_v_0_2019-05-06_2024-02-29_step2.parquet "
                "(paths from reports/stage_e17_run_manifest.json stores; files not opened)",
        "stated_range": f"W_ext first month {W_EXT_FIRST[root]}..2019-04-30; W_cf 2019-05-06..2024-02-29",
    }


CAL = {
    "input": "rates trade-date calendar (trade dates, full closures, early_halt_ct, Globex session) "
             "for the six rates roots",
    "covers_w_ext": True, "covers_w_cf": True,
    "path": "W_ext: data/calendars/hist2010/rates.json (schema e14_hist_calendar/1); "
            "W_cf: data/calendars/rates.py (CALENDAR_COVERAGE, line 182)",
    "stated_range": "hist2010/rates.json coverage 2010-06-01..2019-05-31 (2,324 trade dates, 25 full closures, "
                    "97 early halts, 0 unsourced); rates.py 2019-05-01..2026-06-19",
}

SESSION_OC = {
    "input": "rates day session O/C = 07:20/14:00 CT (D6), read by the member from "
             "load_frozen_tables().day_session_ct",
    "covers_w_ext": True, "covers_w_cf": True,
    "path": "reports/stage_e2a_vehicle_sizes.json contracts.<root>.O_X/C_X via screening/stage_e_frozen.py "
            "(date-independent); data/calendars/hist2010/rates.json sessions[].day_session_ct",
    "stated_range": "frozen table has no dates (07:20, 14:00 for all six); hist2010 rates.json states "
                    "day_session_ct 07:20-14:00 for 2010-06-01..2011-09-30 and 2011-10-03..2019-05-31",
}

AUCTIONS = {
    "input": "tenor-matched Treasury auctions with T_a (competitive close in CT); member reads "
             "strategy/members/k2/_releases.TREASURY_AUCTIONS",
    "covers_w_ext": False, "covers_w_cf": True,
    "path": "W_cf: strategy/members/k2/_releases.py TREASURY_AUCTIONS (from reports/stage_e2b_release_calendar.json, "
            "sha256 839f2437...). W_ext (not in the member's table): reports/stage_e16_calendars/ec_auc_2010_2019.json "
            "(E.2b row format); the frozen generator's transform of it is coded in pattern_search/backward.py S5 "
            "(reports/stage_e20_briefs/backward_swap_table.md row S5); base_rules/auctions.py loads the same rows for H3",
    "stated_range": "member table 340 rows 2019-05-08..2026-06-11 (231 in 2019-05-06..2024-02-29: 2Y 58, 5Y 56, "
                    "10Y 59, 30Y 58); ec_auc_2010_2019.json 684 rows 2010-01-12..2019-06-27, of which 2/5/10/30Y 447 rows "
                    "2010-01-13..2019-06-26; in 2010-07-01..2019-04-30 2Y 97, 5Y 107, 10Y 106, 30Y 106, T_a 12:00 CT (433) "
                    "or 10:30 CT (14) (swap table S5). So W_ext is covered only through that derivation, not by the "
                    "member's frozen table",
}

FOMC = {
    "input": "FOMC statement dates whose statement instant is 13:00 CT; member reads "
             "strategy/members/k2/_releases.FOMC_STATEMENT_DATES",
    "covers_w_ext": False, "covers_w_cf": True,
    "path": "W_cf: strategy/members/k2/_releases.py FOMC_STATEMENT_DATES; W_ext (not in the member's table): "
            "reports/stage_e14_cal_releases.json FOMC rows",
    "stated_range": "member table 57 dates 2019-05-01..2026-06-17 (37 in 2019-05-06..2024-02-29); "
                    "stage_e14_cal_releases.json coverage 2010-06-01..2019-05-31, FOMC 72 rows 2010-06-23..2019-05-01, "
                    "time_local 14:00 ET (= 13:00 CT) on 50 rows, the first 2013-03-20 (2013: 7, 2014-2018: 8 each, "
                    "2019: 3); the other 22 at 14:15 (14), 12:30 (4), 12:35 (3), 12:20 (1) ET. No 2010-2019 table in the "
                    "member's own format; the E.20 swap table marks S13 (FOMC_STATEMENT_DATES) 'NOT NEEDED' "
                    "(k2_fomc_mto dropped)",
}

ISM = {
    "input": "ISM Services release dates at 09:00 CT; member reads strategy/members/k2/_releases.ISM_SERVICES_DATES",
    "covers_w_ext": False, "covers_w_cf": True,
    "path": "W_cf: strategy/members/k2/_releases.py ISM_SERVICES_DATES (from reports/stage_e2b_release_calendar.json). "
            "W_ext: not found. Looked in data/calendars/hist2010/*.json, reports/stage_e14_cal_releases.json "
            "(NGS, WPSR, FOMC only), reports/stage_e16_calendars/, base_rules/, reports/stage_e2b_release_calendar.json "
            "(ISM_SERVICES 2019-05-03..2026-06-03 only), a repo grep for ISM_SERVICES / 'ISM Services' in *.py, *.json, "
            "*.md; reports/stage_e20_briefs/backward_swap_table.md S11 lists ISM_SERVICES among the release types "
            "with no 2010-2019 rows",
    "stated_range": "member table 86 dates 2019-05-03..2026-06-03 (57 in 2019-05-06..2024-02-29); none before 2019-05",
}

MONTH_END = {
    "input": "month-end event dates N-1 and N per calendar month; member reads "
             "strategy/members/k2/_month_end.MONTH_END",
    "covers_w_ext": False, "covers_w_cf": True,
    "path": "W_cf: strategy/members/k2/_month_end.py (generated from data/calendars/rates.py by "
            "reports/stage_e3_briefs/gen_k2_month_end.py). W_ext (not in the member's table): the generator's rule on "
            "data/calendars/hist2010/rates.json, coded in pattern_search/backward.py S6 "
            "(reports/stage_e20_briefs/backward_swap_table.md row S6)",
    "stated_range": "member table 85 months 2019-05..2026-05 (116 event dates in 2019-05-06..2024-02-29); S6 "
                    "derivation 108 months 2010-06..2019-05, 212 event dates in the window, 11 of them early-halt "
                    "trade dates; equal to the frozen table on the 2019-05 overlap",
}

GLOBEX_NOTE = {
    "input": "the trade date's first bar at 17:00 CT on day d-1 (cp1's GLOBEX_OPEN_CT literal, cp1.py line 46)",
    "covers_w_ext": "unknown", "covers_w_cf": True,
    "path": "data/calendars/hist2010/rates.json sessions[] (segments start_ct)",
    "stated_range": "hist2010 rates.json: Globex start 17:30 CT on day -1 for 2010-06-01..2011-09-30, 17:00 CT for "
                    "2011-10-03..2019-05-31. The member's literal 17:00 bar would not be the first bar in "
                    "2010-06..2011-09 (fact from the calendar file; no bar file opened)",
}

# ---------------------------------------------------------------- per-member facts
SETTLE = ("Rates S_p = 14:00 CT, settlement window 13:59:30-14:00:00, 2010-06-07..2024-02-29, grade primary "
          "(reports/stage_e16_settlement.json products.<root>.settle; reports/E.16_RETURN.md Task 1 table)")

M = {
    "cp1": dict(
        member_id="K2-cp1-01",
        trigger_event="every trade date on which s = sign(close of the 07:49 bar - open of the trade date's first "
                      "bar, the 17:00 CT bar of day d-1) is nonzero, both bars present with one instrument_id",
        decision_time_ct="13:29 (the entry decision bar; the signal reads only the 17:00 CT day d-1 bar and the 07:49 bar)",
        side_rule="buy if s > 0, sell if s < 0",
        side_kind="momentum",
        exit_rule_verbatim="Exit: market intent on the first present bar at or after C-2 = 13:58 (fills nominally at "
                           "the 13:59 open), resent while refused (S0.7, L-22). The engine's forced flatten at F is "
                           "the backstop.",
        hold="13:30 open to 13:59 open (about 29 minutes)",
        expected="every trade date with a nonzero signal; E.3 research screen counted 264-276 trips per trial in "
                 "299 dates (reports/E.3_RETURN.md section 3 table)",
        inputs=["bars", CAL, SESSION_OC, GLOBEX_NOTE],
        gate0="gate0A_cp1_ret (the generic CP1 port signal, pooled over the 27 exposures)",
        e20="cp1_ret (kept feature)",
        settle_before="decision 13:29 and exit fill 13:59 are before the 14:00 settlement end",
    ),
    "cp2": dict(
        member_id="K2-cp2-01",
        trigger_event="the first bar opening in [07:35, 14:00) of CT date d whose close is >= OR_high + 4 ticks or "
                      "<= OR_low - 4 ticks, OR = present bars opening in [07:20, 07:35)",
        decision_time_ct="variable, 07:35..13:59 (the first qualifying bar)",
        side_rule="the first eligible bar whose close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells",
        side_kind="momentum",
        exit_rule_verbatim="Exit: 75 minutes after the fill, counted as the MES module counts it (B-H1, "
                           "strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py lines "
                           "147-152; L-07): the present bars seen while the position is non-zero, from the bar after "
                           "the entry decision bar; on the 75th, a market intent closing the position (fills at the "
                           "next open), resent while refused (L-22). Or the engine's forced flatten at F if earlier. "
                           "There is NO exit at C-2: the template's C-2 exit is not part of CP2 (L-07).",
        hold="75 present bars (E.3 mean hold 74.8-75.9 min)",
        expected="every trade date with a breakout; E.3 research screen counted 265-291 trips per trial in 299 dates",
        inputs=["bars", CAL, SESSION_OC],
        gate0="gate0A_cp2_range and gate0A_cp2_brk (the generic CP2 port signals, pooled)",
        e20="cp2_range, cp2_brk (kept features)",
        settle_before="entry decision always before 14:00; a late entry's 75-bar hold can run past 14:00 (up to the "
                      "F flatten at 15:08)",
    ),
    "cp3": dict(
        member_id="K2-cp3-01",
        trigger_event="the 07:20 bar of CT date d when d-1 (the most recent complete daily bar) has Range > 0 and "
                      "CLV >= 0.8 or CLV <= 0.2",
        decision_time_ct="07:20 (the entry decision bar; the condition reads d-1's bars in [07:20, 14:00), close "
                         "of its 13:59 bar)",
        side_rule="CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict), else no trade",
        side_kind="other: side from d-1's close location in its 07:20-14:00 range (buy when d-1 closed in its top "
                  "20%, sell in its bottom 20%); not a signed price move of the trigger day",
        exit_rule_verbatim="Exit: market intent on the first present bar at or after C-2 = 13:58 (fills nominally at "
                           "the 13:59 open), resent while refused (S0.7, L-10, L-22). The engine's forced flatten at F "
                           "is the backstop.",
        hold="07:21 open to 13:59 open (E.3 mean hold 376.5-397.5 min)",
        expected="trade dates whose prior complete day closed at CLV >= 0.8 or <= 0.2; E.3 research screen counted "
                 "121-136 trips per trial in 299 dates",
        inputs=["bars", CAL, SESSION_OC],
        gate0="gate0A_cp3_clv (the generic CP3 port signal, pooled)",
        e20="cp3_clv (kept feature)",
        settle_before="decision 07:20 and exit fill 13:59 are before the 14:00 settlement end; the signal uses "
                      "d-1's 13:59 close, before d-1's settlement end",
    ),
    "aucpre": dict(
        member_id="K2-aucpre-01",
        trigger_event="each tenor-matched Treasury auction date (ZT 2Y, ZF 5Y, ZN and TN 10Y, ZB and UB 30Y)",
        decision_time_ct="T_a - 181 min: 08:59 for T_a 12:00, 07:29 for T_a 10:30 (one T_a 09:00 date, "
                         "2019-12-24, would give 05:59, outside the 07:29-12:00 trading window; E.3 N-6: an early halt)",
        side_rule="SELL q_c: market intent on the bar at T_a - 181 min (fills at the T_a - 180 open)",
        side_kind="calendar",
        exit_rule_verbatim="exit: market intent on the first bar at or after T_a - 2 min (fills nominally at T_a - 1).",
        hold="179 minutes",
        expected="about 12 per year per tenor (member table: 12 per tenor in each of 2020-2023, 5Y 11 in 2022); "
                 "E.3 research screen counted 10-15 trips per trial",
        inputs=["bars", AUCTIONS, CAL],
        gate0="gate0A_k2_auction_mto and gate0A_k2_auction_msince (minutes to / since T_a, pooled; shared with aucpost)",
        e20="k2_auction_mto, k2_auction_msince (kept features)",
        settle_before="decision and exit before 14:00 (exit fill T_a - 1 = 11:59 or 10:29)",
    ),
    "aucpost": dict(
        member_id="K2-aucpost-01",
        trigger_event="each tenor-matched Treasury auction date (the event set and T_a of K2-aucpre-01)",
        decision_time_ct="T_a + 4 min: 12:04 for T_a 12:00, 10:34 for T_a 10:30",
        side_rule="BUY q_c: market intent on the bar at T_a + 4 min (fills at the T_a + 5 open)",
        side_kind="calendar",
        exit_rule_verbatim="exit: market intent on the bar at T_a + 184 min (fills at the T_a + 185 open); a missing "
                           "exit bar: the first later bar; the engine's flatten at F if earlier.",
        hold="180 minutes",
        expected="about 12 per year per tenor (as aucpre); E.3 research screen counted 10-15 trips per trial",
        inputs=["bars", AUCTIONS, CAL],
        gate0="gate0A_k2_auction_mto and gate0A_k2_auction_msince (pooled; shared with aucpre)",
        e20="k2_auction_mto, k2_auction_msince (kept features)",
        settle_before="decision 12:04 / 10:34 before 14:00; the hold spans the 14:00 settlement on T_a 12:00 dates "
                      "(exit fill 15:05), ends 13:35 on T_a 10:30 dates",
    ),
    "fomcpost": dict(
        member_id="K2-fomcpost-01",
        trigger_event="each scheduled FOMC statement date whose statement is released at 13:00 CT",
        decision_time_ct="13:29",
        side_rule="BUY q_c: market intent on the bar at 13:29 (fills at the 13:30 open)",
        side_kind="calendar",
        exit_rule_verbatim="exit: market intent on the bar at 15:04 (fills at the 15:05 open); a missing exit bar: "
                           "the first later bar; the engine's flatten at F if earlier.",
        hold="95 minutes",
        expected="8 per year (member table: 8 in each of 2021-2025); E.3 research screen counted 10 trips per trial",
        inputs=["bars", FOMC, CAL],
        gate0="gate0A_k2_fomc_mto (pooled)",
        e20=None,
        settle_before="decision 13:29 before 14:00; the hold spans the 14:00 settlement (exit fill 15:05)",
    ),
    "predrift": dict(
        member_id="K2-predrift-01",
        trigger_event="each ISM Services release date (release T = 09:00 CT) with s = sign(close of the 08:49 bar "
                      "- open of the 08:30 bar) nonzero, both bars with one instrument_id",
        decision_time_ct="08:49",
        side_rule="entry: market intent on the bar at 08:49 in direction s, q_c (fills at the 08:50 open)",
        side_kind="momentum",
        exit_rule_verbatim="exit: market intent on the bar at 09:04 (fills at the 09:05 open, T + 5); a missing exit "
                           "bar: the first later bar.",
        hold="15 minutes",
        expected="12 per year (member table: 12 in each of 2020-2025); E.3 research screen counted 11-12 trips per trial",
        inputs=["bars", ISM, CAL],
        gate0="gate0A_k2_predrift_move (pooled)",
        e20=None,
        settle_before="decision 08:49 and exit 09:05, before 14:00",
    ),
    "monthend": dict(
        member_id="K2-monthend-01",
        trigger_event="trade dates N-1 and N (the last two EC-CAL rates trade dates of each calendar month), each "
                      "independently",
        decision_time_ct="07:20",
        side_rule="Entry: BUY, unconditional, market intent on the bar at O = 07:20 of CT date d (that exact bar, "
                  "S0.6, L-04), filling at the 07:21 open.",
        side_kind="calendar",
        exit_rule_verbatim="Exit: market intent on the bar at 15:04 (fills at the 15:05 open); a missing exit bar "
                           "sends it on the first later bar; resent while refused (S0.7, L-22); or the engine's forced "
                           "flatten at F.",
        hold="07:21 open to 15:05 open (464 min)",
        expected="24 per year (N-1 and N of 12 months); E.3 research screen counted 18 trips per trial",
        inputs=["bars", MONTH_END, CAL, SESSION_OC],
        gate0="gate0A_k2_monthend_msince (pooled)",
        e20="k2_monthend_msince (kept feature)",
        settle_before="decision 07:20 before 14:00; the hold spans the 14:00 settlement (exit fill 15:05)",
    ),
}


def stages_read(module: str, label: str, root: str) -> list[dict]:
    e3 = E3_ORD[label]
    out = [
        {"stage": "E.3", "window_dates": "research window 2025-04-01..2026-06-17, 299 trade dates (15 roll-blackout "
                                          "and 2 UR-1 dates removed per trial)",
         "purpose": "screen",
         "source": f"reports/E.3_RETURN.md section 3, 'The screen per member and exposure' table, ordinal "
                   f"{e3['ordinal']}; reports/stage_e3_k2_screen/K2_{label}_research.json"},
        {"stage": "E.4", "window_dates": "research window 2025-04-01..2026-06-17 (the E.3 command replayed)",
         "purpose": "other",
         "source": "reports/E.4_RETURN.md Task H2 (regression replay, 44/44 records matched E.3); "
                   "reports/stage_e4_k2_regression.md"},
    ]
    if (module, root) in {("cp1", "ZN"), ("aucpost", "ZN"), ("predrift", "ZN"), ("predrift", "ZB")}:
        out.append({"stage": "E.3 (auditor replay)", "window_dates": "research window 2025-04-01..2026-06-17",
                    "purpose": "other",
                    "source": "reports/E.3_RETURN.md section 2 lines 122-124 (R-T6-1 in-memory replay, equal to its record)"})
    out.append({"stage": "E.12 (ML v2 Gate 0, family A)",
                "window_dates": "ML phase-1 panel 2019-05..2024-02 (D4 S_X 2019-05-06 for 25 paths, ZF 2020-10-01, "
                                "ZT 2021-10-01; 1,068 dates in the family A rows)",
                "purpose": "other",
                "source": f"reports/stage_e12_gate0.md Family A rows {M[module]['gate0']}; reports/E.12_RETURN.md "
                          "Task 6. A feature derived from this member, pooled over exposures, not this trigger's trade"})
    if M[module]["e20"]:
        out.append({"stage": "E.20 (ML pattern search)", "window_dates": "2019-05..2024-02, 17 roots (E.20-B1 "
                                                                         "2010-2019 backward read never run)",
                    "purpose": "other",
                    "source": f"reports/stage_e20_search_freeze.json feature list ({M[module]['e20']}); "
                              "reports/E.20_RETURN.md lines 23-24 and 553-554. A feature, not this trigger's trade"})
    return out


def build() -> dict:
    e3_rows()
    freeze = json.loads((REPO / FREEZE).read_text(encoding="utf-8"))
    rows = []
    for m in freeze["members"]:
        module = m["module"].rsplit(".", 1)[1]
        root = m["legs"][0]["root"]
        label = m["label"]
        f = M[module]
        e3 = E3_ORD[label]
        inputs = [bars_input(root) if x == "bars" else x for x in f["inputs"]]
        rows.append({
            "trigger_id": label,
            "cluster_or_stage": "K2 (Stage E.3)",
            "member_id": f["member_id"],
            "module": f"strategy/members/k2/{module}.py ({m['factory']})",
            "freeze_file": f"{FREEZE} (cluster freeze sha256 8815a775...; ordinal {m['ordinal']})",
            "traded_root": root,
            "vehicle": f"{root} (q_c 1; status {'undersized' if root in ('ZT', 'ZF') else 'chosen'}, "
                       "reports/stage_e2a_vehicles.json)",
            "w_ext_root": root,
            "signal_legs": [],
            "definition_verbatim": docstring_rule(module),
            "trigger_event": f["trigger_event"] + (f" (tenor {TENOR[root]})" if module.startswith("auc") else ""),
            "decision_time_ct": f["decision_time_ct"],
            "side_rule": f["side_rule"],
            "side_kind": f["side_kind"],
            "intraday_hold": f"true: {f['hold']}; flat by F (15:08 CT on a regular rates day)",
            "exit_rule_verbatim": f["exit_rule_verbatim"],
            "expected_events_per_year": f["expected"] + f"; this trial {e3['trips']} trips",
            "inputs_needed": inputs,
            "stages_read": stages_read(module, label, root),
            "tier": e3["tier"],
            "verdicts": [f"E.3 screen: '{e3['screen']}' (mean {e3['mean']} net ticks/contract/day, daily t {e3['t']}); "
                         "Tier B ('fails the D5 screen'), reports/E.3_RETURN.md section 3 table and line 276",
                         "Confirmation (W_cf): not run; 'Stage E.3b onward - K2's confirmation session ... (planned)', "
                         "docs/STAGES.md line 190; no later return reports a K2 confirmation"],
            "settlement_note": SETTLE + ("; TN has no settlement row before its 2016-01-11 listing" if root == "TN"
                                         else "") + ". " + f["settle_before"],
            "exclusion": None,
        })
    excluded = [
        {"id": "K2-ml-01", "reason": "ML model member; excluded by U6 (reports/stage_e0_catalog_K2.md line 4: "
                                     "'superseded by the Stage E ML route'); not in the freeze"},
    ] + [{"id": x, "reason": "excluded at E.0 (reports/stage_e0_catalog_K2.md section 2, lines 674-682); never "
                             "frozen or computed, not a trigger" + extra}
         for x, extra in (("X-01 K2-scalp-01", ""), ("X-02 K2-hftbook-01", ""),
                          ("X-03 K2-auc5d-01", " (multi-day; the same-day slices are aucpre/aucpost)"),
                          ("X-04 K2-eom2d-01", " (multi-day; the day-session slices are monthend)"),
                          ("X-05 K2-basis-01", ""), ("X-06 K2-aucother-01", ""), ("X-07 K2-btc-01", ""),
                          ("X-08 K2-surprise-01", ""), ("X-09 K2-rollspread-01", ""))]
    sources = [
        "reports/stage_e23_briefs/brief_inventory.md (whole)",
        f"{FREEZE} (cluster, created_utc, members, files keys)",
        "strategy/members/k2/cp1.py, cp2.py (whole); cp3.py lines 1-80; aucpre.py, aucpost.py, fomcpost.py (whole); "
        "predrift.py lines 1-60; monthend.py lines 1-50",
        "strategy/members/k2/_releases.py (docstring lines 1-60; tables parsed by ast for counts and ranges)",
        "strategy/members/k2/_month_end.py (docstring lines 1-30; MONTH_END parsed by ast)",
        "strategy/members/k2/_event_common.py lines 1-40 and grep (RATES_EXPOSURES, AUCTION_TENOR); "
        "_port_common.py lines 1-30 and grep",
        "screening/stage_e_frozen.py (grep; lines 180-184, 210-237)",
        "reports/stage_e2a_vehicles.json (exposures of cluster K2); reports/stage_e2a_vehicle_sizes.json (contracts O_X/C_X)",
        "reports/E.3_RETURN.md lines 1-29, 120-126, 216-295, outline grep",
        "reports/E.4_RETURN.md (grep K2; lines 126-131)",
        "reports/E.4b, E.4c, E.5, E.6, E.7, E.8, E.9, E.10, E.11, E.13-E.15, E.17-E.22 _RETURN.md (grep K2 and member "
        "names: only freeze-OK lines or other clusters)",
        "reports/E.1_RETURN.md, E.2a_RETURN.md (lines 268-280), E.2b_RETURN.md, E.12_RETURN.md (lines 480-550, grep), "
        "E.16_RETURN.md (lines 190-240), E.20_RETURN.md (lines 1-30, grep) (grep K2)",
        "reports/stage_e3_STATE.md, reports/stage_e2a_STATE.md (grep member ids)",
        "progress.md, docs/STAGES.md (grep K2; STAGES lines 180-192)",
        "reports/stage_e0_catalog_K2.md (headings and section 2 grep)",
        "reports/stage_e17_run_manifest.json (stores.<rates root> paths only)",
        "data/calendars/hist2010/rates.json (coverage, sessions, counts keys)",
        "data/calendars/rates.py (grep CALENDAR_COVERAGE)",
        "reports/stage_e2b_release_calendar.json (ISM_SERVICES, FOMC, TREASURY_AUCTION date ranges; coverage)",
        "reports/stage_e14_cal_releases.json (coverage; FOMC rows date/time_local counts)",
        "reports/stage_e16_calendars/ec_auc_2010_2019.json (header; row date/tenor/time counts)",
        "base_rules/auctions.py lines 1-40",
        "reports/stage_e16_settlement.json (window, conventions, products.<rates root>.settle)",
        "reports/stage_e20_briefs/backward_swap_table.md lines 30-60; pattern_search/backward.py lines 1-40",
        "reports/stage_e12_gate0.md (header lines 1-10, 97-104; k2_ rows)",
        "reports/stage_e14_c1_result.json, reports/stage_e18_c1b_result.json (k2_ keys: guards.C10.*.applicable = 0)",
        "reports/stage_e20_dry_check_step6.md (lines 1-27, 55-64); reports/stage_e16_overlap.md (grep K2)",
        "ml_route_v2/signals/k2.py lines 1-40",
    ]
    notes = [
        "All 44 trials are single-leg, own-root, on the six rates roots, all six in the 17 W_ext roots; no micro mapping.",
        "No K2 trial has been run on W_cf or W_ext as a trade rule. Its only trade-rule reads are E.3's screen and "
        "E.4's replay, both on the barred research window. K2 member-derived features entered pooled ML work on "
        "2019-05..2024-02 (E.12 Gate 0, E.20 search); E.14 C1 and E.18 C1b list the five k2_ features with 0 "
        "applicable rows (NG model).",
        "The member tables for the event inputs (auctions, FOMC, ISM, month-end) start 2019-05. W_ext coverage for "
        "auctions and month-end exists only as derivations coded in pattern_search/backward.py (S5, S6), checked "
        "equal on the 2019-05 overlap. FOMC 2010-2019 rows exist in reports/stage_e14_cal_releases.json "
        "(13:00 CT instants only from 2013-03-20). ISM Services 2010-2019: not found.",
        "E.16 related tests that are not reads of these triggers: H2 is related to K2-monthend-01 (ZN), and H3 to "
        "K2-aucpre-01 and K2-aucpost-01 (reports/E.16_RETURN.md lines 226-227; reports/stage_e16_overlap.md "
        "lines 72, 86, 135).",
        "D4 start rule for K2: no reports/stage_e_start_rule_K2.json exists (the E.3 power check was not_run, "
        "StartRuleMissing). The S_X dates quoted above are from E.12's ML panel.",
    ]
    return {"assignment": "K2", "rows": rows, "excluded": excluded, "sources_read": sources,
            "not_finished": [], "notes": notes}


def md(doc: dict) -> str:
    lines = ["# Stage E.23 P1.1 inventory: K2 (rates)", "",
             f"Rows: {len(doc['rows'])} triggers (8 members x roots, from {FREEZE}). Excluded: "
             f"{len(doc['excluded'])}. All Tier B (E.3 research screen); no confirmation run.", "",
             "| # | trigger_id | decision CT | side_kind | side rule | exit | events/yr | E.3 trips, t | "
             "W_ext root | non-bar inputs W_ext / W_cf | stages read |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(doc["rows"], 1):
        e3 = E3_ORD[r["trigger_id"]]
        nonbar = [x for x in r["inputs_needed"] if not x["input"].startswith("price bars")]
        cov = "; ".join(f"{x['input'].split(';')[0].split(' (')[0][:40]}: {x['covers_w_ext']}/{x['covers_w_cf']}"
                        for x in nonbar)
        st = ", ".join(s["stage"] + " " + s["purpose"] for s in r["stages_read"])
        lines.append(f"| {i} | {r['trigger_id']} | {r['decision_time_ct'].split(' (')[0]} | "
                     f"{r['side_kind'].split(':')[0]} | {r['side_rule'][:60]} | "
                     f"{r['exit_rule_verbatim'][:50]}... | {r['expected_events_per_year'].split(';')[0][:45]} | "
                     f"{e3['trips']}, {e3['t']} | {r['w_ext_root']} | {cov} | {st} |")
    lines += ["", "Settlement: " + SETTLE + ". TN has no settlement row before 2016-01-11.", "",
              "## Excluded", ""]
    lines += [f"- {x['id']}: {x['reason']}" for x in doc["excluded"]]
    lines += ["", "## Notes", ""] + [f"- {n}" for n in doc["notes"]]
    lines += ["", "## Sources read", ""] + [f"- {s}" for s in doc["sources_read"]]
    lines += ["", "## Not finished", "", "- none"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    doc = build()
    (OUT / "K2.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "K2.md").write_text(md(doc), encoding="utf-8")
    print(len(doc["rows"]), "rows;", len(doc["excluded"]), "excluded")
