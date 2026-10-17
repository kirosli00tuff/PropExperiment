"""K3 inventory builder (Stage E.23 P1.1, InventoryReaderK3). Reads only K3 member docstrings (ast) and
the freeze's member list; every other fact below was read by grep/line ranges and is cited in the row."""

import ast
import json
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e23_briefs/inventory"
FREEZE = "reports/stage_e_k3_member_freeze.json"
ROOTS_EXT = {"6E": "6E"}  # only 6E of the K3 roots is among the 17 W_ext roots

SETTLE = ("reports/stage_e16_settlement.json products.{r}.settle: 14:00 CT (window_ct 13:59:30-14:00:00), "
          "2010-06-07..2024-02-29, basis inferred (S10, S40). ")

E4C = "reports/E.4c_RETURN.md section 3 'The screen per trial' (= reports/E.4_RETURN.md final section)"
E22 = "reports/E.22_RETURN.md section 3.2, '#### K3' table (verdict reports/stage_e22_k3_verdict.json)"

# research trips (E.4c) and confirmation trips (E.22); None = not run
RES = {
    "cp1": {"6E": 284, "6A": 282, "6B": 264, "6C": 276, "6J": 275, "6S": None, "6N": None},
    "cp2": {"6E": 294, "6A": 295, "6B": 296, "6C": 293, "6J": 291, "6S": 293, "6N": None},
    "cp3": {"6E": 112, "6A": 130, "6B": 123, "6C": 118, "6J": 140, "6S": 138, "6N": 138},
    "ldnrev": {"6E": 12, "6J": 13, "6S": 13},
    "ldnmom": {"6E": 254, "6J": 237},
    "mehedge": {"6J": 13}, "ecbfix": {"6E": 561}, "tkypre": {"6J": 52}, "tkypost": {"6J": 269},
}
CONF = {
    "cp1": {"6E": 1134, "6A": 1100, "6B": 1107, "6C": 1131, "6J": 1118, "6S": "not run", "6N": "not run"},
    "cp2": {"6E": 1183, "6A": 1184, "6B": 1186, "6C": 1182, "6J": 1173, "6S": "inconclusive",
            "6N": "not run"},
    "cp3": {"6E": 513, "6A": 544, "6B": 548, "6C": 538, "6J": 543, "6S": 497, "6N": "inconclusive"},
    "ldnrev": {"6E": 55, "6J": 53, "6S": 55},
    "ldnmom": {"6E": 1063, "6J": 1033},
    "mehedge": {"6J": 55}, "ecbfix": {"6E": 2301}, "tkypre": {"6J": 224}, "tkypost": {"6J": 1091},
}
COVERAGE_EXCLUDED = {("cp1", "6S"): "0.9373", ("cp1", "6N"): "0.9209", ("cp2", "6N"): "0.9461"}

CAL = "strategy/members/k3/_calendar.py"
CLK = "strategy/members/k3/_clocks.py"
HIST_FX = "data/calendars/hist2010/fx.json"
NO_W_EXT = ("W_ext: no table found. Looked in strategy/members/k3/, strategy/members/k5/_releases.py and "
            "k7/_calendar.py (TABLE_RANGE / EC_CAL_COVERAGE 2019-05-01..2026-06-19), data/calendars/ and "
            "data/calendars/hist2010/*.json, reports/stage_e4c_release_check.json, reports/stage_e14_cal_releases.json, "
            "repo-wide grep for bank holiday / TARGET / gotobi / Tokyo business day / EC-EW / EC-TGT / EC-JP")


def inp(name, ext, cf, path, rng):
    return {"input": name, "covers_w_ext": ext, "covers_w_cf": cf, "path": path, "stated_range": rng}


def bars(root):
    if root == "6E":
        return inp("6E 1-minute bars (traded leg)", True, True,
                   "W_ext: data/processed_hist/ext2010/6E/ohlcv-1m_6E_v_0_2010-06-07_2019-04-30_ext2010.parquet; "
                   "W_cf: data/processed_step2/6E/ohlcv-1m_6E_v_0_2019-05-06_2024-02-29_step2.parquet "
                   "(reports/stage_e17_run_manifest.json stores.6E)",
                   "ext2010 2010-06-07..2019-04-30; step2 2019-05-06..2024-02-29; S_X 2019-05-06 (E.22 section 3.1)")
    return inp(f"{root} 1-minute bars (traded leg)", False, True,
               f"W_ext: none ({root} is not among the 17 W_ext roots; not in reports/stage_e17_run_manifest.json); "
               f"W_cf: data/processed_step2/{root}/ohlcv-1m_{root}_v_0_2019-05-06_2024-02-29_step2.parquet "
               "(file name; bought in E.12, reports/E.12_RETURN.md lines 488-512)",
               "step2 2019-05-06..2024-02-29; S_X 2019-05-06 (E.22 section 3.1)")


FULL = inp("FX_FULL_SESSIONS (EC-CAL FX trade dates with no early halt and engine F 15:08, K3-L-11)", False, True,
           f"{CAL} FX_FULL_SESSIONS (generated from data/calendars/fx.py CALENDAR_COVERAGE 2019-05-01..2026-06-19). "
           f"W_ext: the frozen table has no pre-2019 dates; {HIST_FX} (group fx, products 6E 6A 6B 6C 6J 6S 6N and "
           "micros) lists trade dates, full closures, early halts and late opens 2010-06-01..2019-05-31; whether it "
           "reproduces K3-L-11's engine-F test is not stated. Note: 14 kept dates 2022-01-17..2023-11-23 that "
           "harness v5 flattens at 11:30 (reports/E.5_RETURN.md R-A2-1; carried as frozen, E.22 R-E22-A15)",
           "EC_CAL_COVERAGE 2019-05-01..2026-06-19; 1797 dates, first 2019-05-01, last 2026-06-18; "
           "hist2010 fx coverage 2010-06-01..2019-05-31")
MONTH = inp("MONTH_ENDS (ME(m) = last EC-CAL FX trade date of month m)", False, True,
            f"{CAL} MONTH_ENDS. W_ext: no table; trade dates for 2010-06..2019-05 exist in {HIST_FX} "
            "(a month-end list is not stated there)",
            "85 months 2019-05..2026-05 (2019-05-31 .. 2026-05-29)")
EW = inp("EW_BANK_HOLIDAYS (England-and-Wales bank holidays, EC-EW)", False, True,
         f"{CAL} EW_BANK_HOLIDAYS. {NO_W_EXT}",
         "docstring 2019-04..2026-06; 63 dates, 2019-04-19 .. 2026-05-25")
TL = inp("T_L clock (16:00 Europe/London per weekday, CT HH:MM: 10:00 or 11:00)", False, True,
         f"{CLK} T_L (CLOCK_RANGE). {NO_W_EXT}; the clock is a zoneinfo rule but no pre-2019 literal table exists",
         "CLOCK_RANGE 2019-04-01..2026-06-19; 1885 rows")
TE = inp("T_E clock (14:15 Europe/Berlin per weekday, CT HH:MM: 07:15 or 08:15)", False, True,
         f"{CLK} T_E. {NO_W_EXT}", "CLOCK_RANGE 2019-04-01..2026-06-19; 1885 rows")
TT = inp("T_T clock (09:55 Asia/Tokyo per Tokyo business day, CT HH:MM on d-1: 18:55 CST or 19:55 CDT)", False,
         True, f"{CLK} T_T. {NO_W_EXT}", "CLOCK_RANGE 2019-04-01..2026-06-19; 1761 rows")
TGT = inp("TGT_CLOSING_DAYS (TARGET closing days, EC-TGT)", False, True, f"{CAL} TGT_CLOSING_DAYS. {NO_W_EXT}",
          "docstring 'six a year 2019-2026'; 48 dates, 2019-01-01 .. 2026-12-26")
TKY = inp("TOKYO_BUSINESS_DAYS (EC-JP)", False, True, f"{CAL} TOKYO_BUSINESS_DAYS. {NO_W_EXT}",
          "TOKYO_RANGE 2019-04-01..2026-06-19; 1761 dates")
GOTO = inp("GOTOBI_OR_TOKYO_MONTH_END (EC-JP days with day of month 5/10/15/20/25/30 or last Tokyo business day)",
           False, True, f"{CAL} GOTOBI_OR_TOKYO_MONTH_END. {NO_W_EXT}",
           "404 dates, 2019-04-05 .. 2026-06-15 (within TOKYO_RANGE 2019-04-01..2026-06-19)")
REQ = inp("MEHEDGE_R_EQ_6J (Nikkei 225 month log return R_eq(m), literal table)", False, True,
          "strategy/members/k3/_mehedge_signal.py MEHEDGE_R_EQ_6J (from data/vendor/index_history/"
          "nikkei_stock_average_daily_en.csv and three Wayback captures; sha256s in the module). W_ext: no table; "
          "the raw Nikkei file was not opened (its range is not stated in the module; E.4c line 89 says 1,761 closes)",
          "85 months 2019-05..2026-05, 0 None")
SESS = inp("day_session_ct O/C (FX row 07:20 / 14:00) and vehicle q_c (frozen tables)", True, True,
           "screening/stage_e_frozen.py load_frozen_tables() (constant per root); W_ext restated in "
           f"{HIST_FX} sessions[0].day_session_ct (6E..6N 07:20-14:00)",
           "constant; hist2010 session valid 2010-06-01..2019-05-31")
EARLY = inp("bar field early_halt_ct (cp3's complete-day and 07:20-bar tests)", "unknown", True,
            "a column of the stage_e bar stores (data/stage_e_bars.py line 90). W_ext: "
            f"{HIST_FX} holds early halts 2010-06-01..2019-05-31 (96 early_halts, data/hist_calendar.py maps them); "
            "whether the ext2010 store carries the column was not checked (stores not opened)",
            "step2 stores 2019-05-06..2024-02-29; hist2010 fx 2010-06-01..2019-05-31")
ENGINE = inp("engine-level, not read by the member: release calendar for D8 event-window cost and the D9.5a "
             "fill guard [release, release + 2 min)", False, True,
             "W_cf: reports/stage_e2b_release_calendar.json (coverage 2019-05-01..2026-06-21; rows mapped to "
             "6E/6A/6B/6J/6S/6N: FOMC 57, NFP 85; 6C adds WPSR 371). W_ext: reports/stage_e14_cal_releases.json "
             "(coverage 2010-06-01..2019-05-31; kinds FOMC, NGS, WPSR only; FX roots: FOMC 72, 6C adds WPSR 470); "
             "no NFP rows before 2019 found (grep NFP-201[0-8] in reports/)",
             "2019-05-01..2026-06-21; 2010-06-01..2019-05-31 (FOMC/NGS/WPSR only)")

T = {
    "cp1": dict(
        trigger_event="every FX trade date: sign of (07:49 bar close - Globex-open 17:00 CT (d-1) bar open), nonzero",
        decision_time_ct="13:29 (entry decision bar; signal bars: 17:00 CT on d-1 open and 07:49 close)",
        side_rule="buy if s > 0, sell if s < 0",
        side_kind="momentum",
        exit_rule_verbatim="Exit: market intent on the first present bar at or after C-2 = 13:58 (fills nominally "
                           "at the 13:59 open), resent while refused (S0.7, E.3-L-22). The engine's forced flatten "
                           "at F and its D9.7 exit are the backstops; after either, the member sends nothing more "
                           "that trade date.",
        hold="13:30 open to about 13:59 on trade date d",
        events="every trade date with nonzero signal and both signal bars present (no event calendar)",
        inputs=[SESS], settle_dec="13:29 is before 14:00: yes"),
    "cp2": dict(
        trigger_event="first bar in [07:35, 14:00) whose close >= OR_high + 4 ticks or <= OR_low - 4 ticks "
                      "(OR = bars in [07:20, 07:35))",
        decision_time_ct="variable 07:35..13:59 (the first qualifying bar's close)",
        side_rule="the first eligible bar whose close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells",
        side_kind="momentum",
        side_note="breakout: side = direction of the close beyond the 07:20-07:35 opening range",
        exit_rule_verbatim="Exit: 75 minutes after the fill, counted as the MES module counts it (B-H1, "
                           "strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py lines "
                           "147-152; E.3-L-07): the present bars seen while the position is non-zero, from the bar "
                           "after the entry decision bar; on the 75th, a market intent closing the position (fills "
                           "at the next open), resent while refused (E.3-L-22). Or the engine's forced flatten at F "
                           "if earlier. There is NO exit at C-2",
        hold="75 present bars after the fill, or F 15:08 if earlier",
        events="every trade date with a qualifying breakout bar (at most one entry per date)",
        inputs=[SESS],
        settle_dec="decision bars up to 13:59; all open before 14:00, but the 13:59 bar's close is 14:00:00, "
                   "inside the 13:59:30-14:00:00 settlement window; a hold can run past 14:00 to F 15:08"),
    "cp3": dict(
        trigger_event="trade date d whose previous complete daily bar (07:20-14:00) has CLV >= 0.8 or <= 0.2",
        decision_time_ct="07:20 (bar at O on CT date d; reads d-1's complete daily bar)",
        side_rule="CLV = (C - L) / (H - L) in ticks, CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict), else no trade",
        side_kind="other",
        side_note="side from d-1's close location value (prior-day bar), not a trigger-day move",
        exit_rule_verbatim="Exit: market intent on the first present bar at or after C-2 = 13:58 (fills nominally "
                           "at the 13:59 open), resent while refused (S0.7, E.3-L-10, E.3-L-22). The engine's "
                           "forced flatten at F and its D9.7 exit are the backstops; after either, nothing more "
                           "that trade date.",
        hold="07:21 open to about 13:59 on d",
        events="trade dates where d-1's CLV is in the tails (no event calendar)",
        inputs=[SESS, EARLY], settle_dec="07:20 is before 14:00: yes (d-1's bar ends 14:00, at d-1's settlement)"),
    "ldnrev": dict(
        trigger_event="month-end ME(m) (FX full session, not an E&W bank holiday): 10-minute pre-London-fix move "
                      "M = close(T_L - 1) - close(T_L - 11), nonzero",
        decision_time_ct="T_L + 4 = 10:04 (11:04 in C9 mismatch weeks); signal bars 09:49 and 09:59 closes",
        side_rule="BUY if M < 0, SELL if M > 0 (contrarian in the futures' own quote, C 429-433)",
        side_kind="fade",
        exit_rule_verbatim="exit: market intent on the bar at T_L + 19, filling at the T_L + 20 open; a missing exit "
                           "bar: the first later present bar (C 434-435, S0.7).",
        hold="T_L + 5 to T_L + 20 (10:05-10:20 CT standard)",
        events="12 month-ends a year less excluded ME(m) (no shift)",
        inputs=[MONTH, FULL, EW, TL], settle_dec="10:04 (11:04) is before 14:00: yes"),
    "ldnmom": dict(
        trigger_event="every FX full session not an E&W bank holiday: S = close(T_L - 13) - open(T_L - 15), nonzero",
        decision_time_ct="T_L - 13 = 09:47 close (10:47 in C9 mismatch weeks)",
        side_rule="BUY if S > 0, SELL if S < 0",
        side_kind="momentum",
        exit_rule_verbatim="exit: market intent on the bar at T_L + 4, filling at the T_L + 5 open (10:05 CT "
                           "standard); a missing exit bar: the first later present bar (C 518-519, S0.7).",
        hold="T_L - 12 to T_L + 5 (09:48-10:05 CT standard)",
        events="every full-session trade date that is not an E&W bank holiday, with nonzero S",
        inputs=[FULL, EW, TL], settle_dec="09:47 (10:47) is before 14:00: yes"),
    "mehedge": dict(
        trigger_event="month-end ME(m) (FX full session, not an E&W bank holiday) with nonzero Nikkei R_eq(m)",
        decision_time_ct="T_L - 61 = 08:59 (09:59 in C9 mismatch weeks); signal is the literal Nikkei table",
        side_rule="SELL if R_eq > 0, BUY if R_eq < 0",
        side_kind="other",
        side_note="side = minus the sign of the Nikkei 225's month-to-date log return (a non-bar index input, "
                  "not the traded root's move)",
        exit_rule_verbatim="Exit: market intent on the first present bar at or after T_L - 4 (fills nominally at "
                           "the T_L - 3 open: 09:57 or 10:57 CT), resent while refused (S0.7, E.3-L-22); sent "
                           "whatever the bar's instrument_id (K3-L-03). The engine's forced flatten at F and its "
                           "D9.7 exit are the backstops; after either, the member sends nothing more that date.",
        hold="T_L - 60 to T_L - 3 (09:00-09:57 CT standard)",
        events="12 month-ends a year less excluded ME(m)",
        inputs=[MONTH, FULL, EW, TL, REQ], settle_dec="08:59 (09:59) is before 14:00: yes"),
    "ecbfix": dict(
        trigger_event="every FX full session not a TARGET closing day: leg 1 SELL from 01:00 CT to T_E, then "
                      "leg 2 BUY from T_E + 1 to 15:05",
        decision_time_ct="leg 1: 00:59 CT on d; leg 2: T_E = 07:15 (08:15 in C9 mismatch weeks)",
        side_rule="leg 1 (SELL) ... leg 2 (BUY)",
        side_kind="calendar",
        exit_rule_verbatim="leg 1 Exit: market intent on the bar at T_E - 1, filling at the T_E open; a missing exit "
                           "bar: the first later present bar (S0.7). leg 2 Exit: market intent on the bar at 15:04 "
                           "CT, filling at the 15:05 open; a missing exit bar: the first later present bar (the "
                           "engine's F at 15:08 is the backstop).",
        hold="01:00 to 07:15 (leg 1) and 07:16 to 15:05 (leg 2), CT on d",
        events="every full-session trade date that is not a TARGET closing day (two legs per date)",
        inputs=[FULL, TGT, TE],
        settle_dec="00:59 and 07:15 (08:15) are before 14:00: yes; leg 2's hold runs past 14:00 to 15:05"),
    "tkypre": dict(
        trigger_event="trade date d in FX_FULL_SESSIONS that, as a Tokyo date, is a gotobi day or the last Tokyo "
                      "business day of its month",
        decision_time_ct="17:29 CT on calendar day d-1",
        side_rule="entry: SELL (a rise in USD/JPY is a fall in 6J, C8)",
        side_kind="calendar",
        exit_rule_verbatim="exit: market intent on the bar at T_T - 1 on d-1, filling at the T_T open (C 760-762); "
                           "a missing exit bar: the first later present bar (S0.7).",
        hold="17:30 to T_T (18:55 CST / 19:55 CDT) on calendar day d-1 (trade date d's evening)",
        events="gotobi and Tokyo month-end days (404 in 2019-04-05..2026-06-15)",
        inputs=[FULL, GOTO, TT],
        settle_dec="17:29 on d-1 is after d-1's 14:00 settlement and before d's: decision and hold lie in trade "
                   "date d's evening session"),
    "tkypost": dict(
        trigger_event="every trade date d in FX_FULL_SESSIONS that is a Tokyo business day",
        decision_time_ct="T_T on calendar day d-1 = 18:55 CST / 19:55 CDT",
        side_rule="entry: BUY (dollar weakness is a rise in 6J)",
        side_kind="calendar",
        exit_rule_verbatim="exit: market intent on the bar at 00:59 CT on d, filling at the 01:00 open (C 825-826); "
                           "a missing exit bar: the first later present bar (S0.7).",
        hold="T_T + 1 on d-1 to 01:00 CT on d",
        events="every Tokyo business day that is an FX full session",
        inputs=[FULL, TKY, TT],
        settle_dec="18:55/19:55 on d-1 is after d-1's 14:00 settlement and before d's; the hold ends 01:00 on d"),
}


def rule_text(module):
    doc = ast.get_docstring(ast.parse((REPO / f"strategy/members/k3/{module}.py").read_text()))
    paras = doc.split("\n\n")
    return " ".join(" ".join(paras[1:]).split()) if len(paras) > 1 else " ".join(doc.split())


ML_FEAT = {"ldnmom": "k3_ldnmom_trend", "ldnrev": "k3_ldnrev_move", "mehedge": "k3_mehedge_req",
           "ecbfix": "k3_ecbfix_mto, k3_ecbfix_msince", "tkypost": "k3_tkypost_msince",
           "tkypre": "k3_tkypre_msince"}


def stages(short, root):
    out = []
    key = (short, root)
    if key in COVERAGE_EXCLUDED:
        out.append({"stage": "E.4c", "window_dates": "research 2025-04-01..2026-06-17 (299 trade dates)",
                    "purpose": "screen", "note": f"excluded_before_screening (coverage_below_0.95, "
                    f"{COVERAGE_EXCLUDED[key]}); not screened, not in N",
                    "source": E4C + "; reports/stage_e4c_k3_screen/ window_dates"})
    else:
        out.append({"stage": "E.4c", "window_dates": "research 2025-04-01..2026-06-17 (299 trade dates)",
                    "purpose": "screen", "note": f"{RES[short][root]} trips",
                    "source": E4C + "; window from reports/stage_e4c_k3_screen/K3_K3-cp1-01_6A_research.json "
                              "window_dates"})
    c = CONF[short][root]
    if c == "not run":
        out.append({"stage": "E.22", "window_dates": "confirmation 2019-05-06..2024-02-29 (1191 trade dates)",
                    "purpose": "confirmation", "note": "not run: excluded (not Tier A or B)", "source": E22})
    elif c == "inconclusive":
        out.append({"stage": "E.22", "window_dates": "confirmation 2019-05-06..2024-02-29 (1191 trade dates)",
                    "purpose": "confirmation", "note": "inconclusive: record status 'excluded_before_screening': "
                    "no series (confirmation-window coverage; E.22 lines 362, 401-403)", "source": E22})
    else:
        out.append({"stage": "E.22", "window_dates": "confirmation 2019-05-06..2024-02-29 (1191 trade dates)",
                    "purpose": "confirmation", "note": f"{c} trips; status null",
                    "source": E22 + "; reports/stage_e22_confirm_k3/ (ldnrev 6E record window_dates checked)"})
        out.append({"stage": "E.22", "window_dates": "confirmation 2019-05-06..2024-02-29",
                    "purpose": "power", "note": "D4 power check: 'all sufficient (supply 1,191; ldnrev n_b 1)'",
                    "source": "reports/E.22_RETURN.md section 3.1 table, K3 row (line 279)"})
    if short == "ldnrev" and root == "6E":
        out.append({"stage": "E.22", "window_dates": "confirmation 2019-05-06..2024-02-29",
                    "purpose": "null statement", "note": "Tier A trial of the K3 cluster statement: 'no statement'",
                    "source": "reports/E.22_RETURN.md lines 14, 293, 327, 399-403"})
    if short in ML_FEAT:
        out.append({"stage": "E.12", "window_dates": "training window 2019-05..2024-02 (reports/E.12_RETURN.md line 19)",
                    "purpose": "other",
                    "note": f"ML route v2 Gate 0 family A tested the member's signal as a feature ({ML_FEAT[short]}; "
                            "rows gate0A_<feature>_h60/h120/hF, pooled over the signal's roots, rejected: no); an "
                            "ML test, not a run of this trigger",
                    "source": "reports/stage_e12_gate0.md Family A table (lines 99-260)"})
        if root == "6E":
            out.append({"stage": "E.14 C1 / E.18 C1b", "window_dates": "W_ext ext2010 6E 2010-06-07..2019-04-30",
                        "purpose": "other",
                        "note": f"ML models (excluded as triggers) list {ML_FEAT[short]} as features; "
                                "guards.C10.{h60,hF}.applicable for each k3_* feature = 0; 6E is in the model world",
                        "source": "reports/stage_e14_c1_result.json and reports/stage_e18_c1b_result.json "
                                  "(guards.C10, world.roots.6E)"})
    return out


def tier_and_verdicts(short, root):
    key = (short, root)
    if key in COVERAGE_EXCLUDED:
        tier = "n/a"
        v = [f"'excluded_before_screening (coverage_below_0.95)' ({E4C})",
             f"'not run: excluded (not Tier A or B)' ({E22}, line 362)"]
        return tier, v
    tier = "A" if key == ("ldnrev", "6E") else "B"
    v = [f"Tier {tier} (E.4c screen; {E4C})"]
    c = CONF[short][root]
    if c == "inconclusive":
        v.append(f"'inconclusive' (E.22; {E22}, line 362: blocking)")
    else:
        v.append(f"'null' (E.22 Status; {E22})")
    if key == ("ldnrev", "6E"):
        v.append("'K3-ldnrev-01 6E: NULL, no edge. UCB95 +0.10 against 12; Holm p 0.797.' and 'no edge (first "
                 "failing: holm)' (reports/E.22_RETURN.md lines 14, 293)")
    v.append("cluster K3: 'no statement' (reports/E.22_RETURN.md line 293, 401-403)")
    return tier, v


def main():
    freeze = json.loads((REPO / FREEZE).read_text())
    rows = []
    for m in freeze["members"]:
        mod = m["module"].rsplit(".", 1)[1]
        root = m["legs"][0]["root"]
        member_id = m["label"].split()[0]
        t = T[mod]
        res = RES[mod][root]
        conf = CONF[mod][root]
        tier, verdicts = tier_and_verdicts(mod, root)
        side_kind = t["side_kind"] if "side_note" not in t else f"{t['side_kind']}: {t['side_note']}"
        rows.append({
            "trigger_id": m["label"], "cluster_or_stage": "K3 (Stage E.4 Part 3 = E.4c)", "member_id": member_id,
            "module": f"strategy/members/k3/{mod}.py ({m['module']}.{m['factory']})", "freeze_file": FREEZE,
            "traded_root": root, "vehicle": root, "w_ext_root": ROOTS_EXT.get(root), "signal_legs": [],
            "definition_verbatim": rule_text(mod), "trigger_event": t["trigger_event"],
            "decision_time_ct": t["decision_time_ct"], "side_rule": t["side_rule"], "side_kind": side_kind,
            "intraday_hold": True, "hold_window_ct": t["hold"], "exit_rule_verbatim": t["exit_rule_verbatim"],
            "expected_events_per_year": f"{t['events']}; counts: E.4c research trips "
                                        f"{res if res is not None else 'not screened'} in 299 dates; E.22 "
                                        f"confirmation trips {conf} in 1191 dates",
            "inputs_needed": [bars(root)] + t["inputs"] + [ENGINE], "stages_read": stages(mod, root),
            "tier": tier, "verdicts": verdicts,
            "settlement_note": SETTLE.format(r=root) + t["settle_dec"], "exclusion": None,
        })
    excluded = [
        {"item": "K3-mehedge-01 6E (EUR, EURO STOXX 50)", "reason": "never declared: no factory, not in the freeze "
         "('the EURO STOXX 50's free history was not obtained, so the 6E trial is not declared and has no factory', "
         "strategy/members/k3/mehedge.py docstring; reports/E.4c_RETURN.md line 19); not in N"},
        {"item": "ML-route features k3_ldnmom_trend, k3_ldnrev_move, k3_mehedge_req, k3_ecbfix_mto, "
                 "k3_ecbfix_msince, k3_tkypost_msince, k3_tkypre_msince (ml_route_v2/signals/k3.py)",
         "reason": "ML models (E.12 Gate 0, E.14 C1, E.18 C1b): not triggers; their reads are listed under the "
                   "matching members' stages_read as 'other'"},
    ]
    sources = [
        f"{FREEZE} (cluster, members: 30 labels, legs, modules, factories)",
        "strategy/members/k3/cp1.py, cp2.py, cp3.py, ldnrev.py, ldnmom.py, ecbfix.py, tkypre.py, tkypost.py, "
        "mehedge.py (module docstrings and constants)",
        "strategy/members/k3/_port_common.py, _event_common.py (docstrings)",
        "strategy/members/k3/_calendar.py, _clocks.py, _mehedge_signal.py (docstrings; table lengths, first/last rows)",
        "reports/E.4_RETURN.md lines 371-450 (final section table)",
        "reports/E.4c_RETURN.md lines 7-24, 104-160, 188-216",
        "reports/stage_e4c_k3_screen/K3_K3-cp1-01_6A_research.json (window, window_dates first/last/n)",
        "reports/E.22_RETURN.md lines 1-14, 274-293, 325-363, 399-403, 608, 645",
        "reports/stage_e22_confirm_k3/K3_K3-ldnrev-01_6E_confirmation.json (window, window_dates first/last/n)",
        "reports/E.5_RETURN.md lines 352-424 (R-A2-1, K3's 14 FX dates); reports/E.9_RETURN.md lines 217, 392-394",
        "reports/E.2a_RETURN.md lines 277-280 (source-overlap classification; no window read)",
        "reports/E.10_RETURN.md lines 105-115 (lead saw a K3-ldnrev-01 6E figure; no read)",
        "reports/E.6..E.21 RETURN.md grep 'K3' (cluster freeze checks only); reports/E.20_RETURN.md line 262 "
        "(6E search proposals p6e_mehedge_nq, p6e_post_ldnfix not accepted; E.20 search configs belong to CDE's "
        "exclusion, not K3 members)",
        "reports/E.12_RETURN.md line 19; reports/stage_e12_gate0.md (Family A K3 rows)",
        "reports/E.11_RETURN.md (grep K3/window); reports/stage_e11_signal_coverage.md lines 49-54",
        "reports/stage_e14_c1_result.json, reports/stage_e18_c1b_result.json (guards.C10, world.roots)",
        "ml_route_v2/signals/k3.py docstring",
        "reports/stage_e17_run_manifest.json stores.6E",
        "data/processed_step2/<FX root>/ directory listings (file names only)",
        "data/calendars/hist2010/fx.json (coverage, counts, products, sessions; entries not loaded into context)",
        "data/calendars/fx.py CALENDAR_COVERAGE line",
        "reports/stage_e14_cal_releases.json, reports/stage_e2b_release_calendar.json (coverage; release counts "
        "per FX root)",
        "reports/stage_e16_settlement.json products.6E/6A/6B/6C/6J/6S/6N settle",
        "reports/stage_e4c_release_check.json (top-level keys)",
        "strategy/members/k5/_releases.py, strategy/members/k7/_calendar.py (ranges)",
        "data/vendor/index_history/manifest.jsonl (file names, notes)",
        "screening/stage_e_rules.py, stage_e_engine.py (D9.5a grep); data/stage_e_bars.py line 90",
        "docs/STAGES.md lines 96-98, 184-186; progress.md grep K3 member ids",
        "reports/stage_e21_briefs/lead_spec.md and multiday/constants.py (grep settle)",
    ]
    data = {"assignment": "K3", "rows": rows, "excluded": excluded, "sources_read": sources, "not_finished": []}
    (OUT / "K3.json").write_text(json.dumps(data, indent=1) + "\n")

    md = ["# Stage E.23 P1.1 inventory: K3 (FX)", "",
          f"Rows: {len(rows)} (30 frozen member trials, {FREEZE}, cluster freeze c4fb5da4...). Excluded: "
          f"{len(excluded)} (not triggers). Only 6E (6 rows) has a W_ext root; 6A 6B 6C 6J 6S 6N have no W_ext bars.",
          "", "Windows: E.4c screen = research 2025-04-01..2026-06-17 (299 dates); E.22 confirmation = "
          "2019-05-06..2024-02-29 (1191 dates). Settlement (reports/stage_e16_settlement.json): 14:00 CT on all "
          "seven FX roots, 2010-06-07..2024-02-29.", "",
          "| Trigger | Root | W_ext | Decision CT | Side kind | Non-bar inputs (W_ext / W_cf) | Res trips | "
          "Conf trips | Tier | E.22 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        nb = "; ".join(f"{i['input'].split(' (')[0]} ({i['covers_w_ext']}/{i['covers_w_cf']})"
                       for i in r["inputs_needed"][1:-1]) or "-"
        mod = r["member_id"].split("-")[1]
        res = RES[mod][r["traded_root"]]
        conf = CONF[mod][r["traded_root"]]
        e22 = conf if isinstance(conf, str) else "null"
        md.append(f"| {r['trigger_id']} | {r['traded_root']} | {r['w_ext_root'] or '-'} | {r['decision_time_ct']} | "
                  f"{r['side_kind'].split(':')[0]} | {nb} | {res if res is not None else 'excl.'} | "
                  f"{conf if not isinstance(conf, str) else '-'} | {r['tier']} | {e22} |")
    md += ["", "Every row also needs the engine's release calendar (D8 cost, D9.5a guard): W_cf "
           "reports/stage_e2b_release_calendar.json 2019-05-01..2026-06-21 (FOMC, NFP; 6C adds WPSR); W_ext "
           "reports/stage_e14_cal_releases.json 2010-06-01..2019-05-31 has FOMC/NGS/WPSR only, no NFP found.", "",
           "Inputs with no W_ext table (all K3 fix/event members): FX_FULL_SESSIONS, MONTH_ENDS, EW_BANK_HOLIDAYS, "
           "TGT_CLOSING_DAYS, TOKYO_BUSINESS_DAYS, GOTOBI_OR_TOKYO_MONTH_END, the T_L/T_E/T_T clocks (all "
           "2019-04/05..2026-06) and MEHEDGE_R_EQ_6J (2019-05..2026-05). data/calendars/hist2010/fx.json gives FX "
           "trade dates and early halts 2010-06-01..2019-05-31 only. For 6E's W_ext reading: cp1 and cp2 need no "
           "non-bar table beyond the constant clock; cp3 needs the bar field early_halt_ct (unknown on ext2010); "
           "ldnrev, ldnmom and ecbfix need tables that do not exist before 2019-04.", "",
           "Other reads (ML, not trigger runs): E.12 Gate 0 family A tested the K3 fix signals on 2019-05..2024-02; "
           "E.14 C1 and E.18 C1b list them as features on ext2010 (6E in the world), applicable = 0 at guard C10.",
           "", "## Excluded", ""]
    md += [f"- {e['item']}: {e['reason']}" for e in excluded]
    md += ["", "## Sources read", ""] + [f"- {s}" for s in sources] + ["", "## Not finished", "", "- none"]
    (OUT / "K3.md").write_text("\n".join(md) + "\n")
    print(len(rows), "rows;", len(excluded), "excluded")


if __name__ == "__main__":
    main()
