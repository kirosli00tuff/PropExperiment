"""K8 inventory builder (Stage E.23 P1.1). Reads only K8 module docstrings; writes K8.json and K8.md."""
import ast
import json
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e23_briefs/inventory"
FREEZE = "reports/stage_e_k8_member_freeze.json"


def doc(mod):
    return ast.get_docstring(ast.parse((REPO / f"strategy/members/k8/{mod}.py").read_text()), clean=False)


def between(text, start, end):
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return " ".join(text[i:j].split())


FL, OC, WB = doc("flight"), doc("oilcad"), doc("wkndbtc")

REL_W_EXT = "reports/stage_e14_cal_releases.json (coverage 2010-06-01..2019-05-31; FOMC 72 rows, WPSR 470 rows, NGS 470 rows)"
NOT_FOUND = ("not found: searched reports/, strategy/, base_rules/, data/calendars/, screening/, multiday/ for "
             "pre-2019 row ids of this release; data/calendars/hist2010/*.json are session calendars only")
GUARD_PATH = "strategy/members/k8/_releases.py GUARD_INSTANTS (from reports/stage_e2b_release_calendar.json, sha256 839f2437...)"
GUARD_RANGE = "TABLE_RANGE 2019-05-01..2026-06-19 (frozen module; e2b calendar coverage 2019-05-01..2026-06-21)"


def guard_inputs(root, kinds):
    rows = []
    for k in kinds:
        in_e14 = k in ("FOMC", "WPSR")
        rows.append({
            "input": f"C6 release guard [R, R+2 min) on {root}: {k} instants",
            "covers_w_ext": True if in_e14 else False,
            "covers_w_cf": True,
            "path": f"W_cf: {GUARD_PATH}; W_ext: " + (REL_W_EXT if in_e14 else NOT_FOUND),
            "stated_range": GUARD_RANGE + ("; W_ext table 2010-06-01..2019-05-31" if in_e14 else "; W_ext none"),
        })
    return rows


def cal_input(table, groups, crypto=False):
    hist = ", ".join(f"data/calendars/hist2010/{g}.json" for g in groups)
    return {
        "input": f"member date table {table} (full sessions of {' & '.join(groups + (['crypto'] if crypto else []))})",
        "covers_w_ext": False if crypto else "unknown",
        "covers_w_cf": True,
        "path": (f"W_cf: strategy/members/k8/_calendar.py {table}; W_ext: the frozen table has no W_ext dates; "
                 f"group session calendars exist at {hist} (coverage 2010-06-01..2019-05-31)"
                 + ("; crypto: not found (no data/calendars/hist2010/crypto.json)" if crypto else "")
                 + "; whether they reproduce the table's rule (no early halt and engine F 15:08) is not stated"),
        "stated_range": "TABLE_RANGE 2019-05-01..2026-06-19; hist2010 coverage 2010-06-01..2019-05-31",
    }


E9 = "reports/E.9_RETURN.md Task 5 table (lines 236-242) and Tier table (lines 13-18); reports/stage_e9_k8_screen/"
E22P = "reports/E.22_RETURN.md section 3.1 K8 row (line 281); reports/stage_e22_STATE.md A3c/A3e; reports/stage_e22_power_k8/"
E22C = "reports/E.22_RETURN.md '#### K8' table (lines 315-325); reports/stage_e22_confirm_k8/; reports/stage_e22_k8_verdict.json"
E2A = ("reports/E.2a_RETURN.md Task 11 (lines 270-278); reports/stage_e2a_STATE.md row 11: source-window amendment set "
       "K8-flight-01 and K8-oilcad-01 from 'source-overlap (fallback)' to 'not source-overlap' (catalog label, no bars read)")

GC_SETTLE = ("GC 12:30 CT (window 12:29:00-12:30:00, primary) for 2010-06-07..2024-02-29, reports/stage_e16_settlement.json "
             "products.GC.settle (no MGC entry; GC is MGC's price path)")


def flight_row(label, tier, exit_start, exit_end, e22_line, verdict_e9):
    return {
        "trigger_id": label,
        "cluster_or_stage": "K8 (Stage E.9)",
        "member_id": "K8-flight-01",
        "module": "strategy.members.k8.flight (" + ("make_h30" if "H30" in label else "make_heod") + ")",
        "freeze_file": FREEZE,
        "traded_root": "MGC",
        "vehicle": "MGC (GC bars as MGC's price path in E.22, R-E22-A4)",
        "w_ext_root": "GC",
        "signal_legs": ["MES"],
        "definition_verbatim": between(FL, "- Blocks B_k", "- Exit:"),
        "trigger_event": "first 5-minute MES block return r_k at t_k (08:35..14:55) with r_k <= Q(d) (the ceil(0.005 n)-th "
                         "smallest of the 20 prior FLIGHT_DATES' block returns, n >= 1,200) and r_k < 0, not C6-skipped; "
                         "one entry per date",
        "decision_time_ct": "t_k = 08:35..14:55 every 5 min; latest bar used = MES bar opening t_k - 1 (08:34..14:54 CT); "
                            "fill at the open of the MGC bar at t_k",
        "side_rule": "BUY q_c MGC, market intent on the view at t_k - 1 whose MGC bar is the bar at t_k - 1 (S0.6), "
                     "filling at the open of the MGC bar at t_k.",
        "side_kind": "other: always long MGC; the trigger requires a negative extreme MES (signal-leg) move, the side is fixed",
        "intraday_hold": True,
        "exit_rule_verbatim": between(FL, exit_start, exit_end),
        "expected_events_per_year": "at most one entry per FLIGHT_DATE, on dates where an MES block return reaches the "
                                    "trailing 0.5% lower quantile; counts reported: E.9 research 55 trips on 280 window "
                                    "dates; E.22 confirmation 231 trips on 944 window dates (2020-02-04..2024-02-29)",
        "inputs_needed": [
            {"input": "MES 1-minute bars (signal leg)", "covers_w_ext": False, "covers_w_cf": True,
             "path": "W_cf: data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet (MES's Stage D "
                     "store, E.22 R-E22-A7, S = 2020-02-03; not the sealed data/sealed/MES_holdout_v*); W_ext: none (MES "
                     "and ES are not among the 17 W_ext roots)",
             "stated_range": "file name 2019-05-01..2024-02-29; MES s_x 2020-02-03 (E.22 confirmation record)"},
            {"input": "MGC price path (GC 1-minute bars)", "covers_w_ext": True, "covers_w_cf": True,
             "path": "W_ext: data/processed_hist/ext2010/GC/ohlcv-1m_GC_v_0_2010-06-07_2019-04-30_ext2010.parquet; W_cf: "
                     "data/processed_step2/GC/ohlcv-1m_GC_v_0_2019-05-06_2024-02-29_step2.parquet (reports/stage_e17_run_manifest.json)",
             "stated_range": "ext2010 2010-06-07..2019-04-30; step2 2019-05-06..2024-02-29; MGC s_x 2019-05-06"},
            cal_input("FLIGHT_DATES", ["equity", "metals"]),
        ] + guard_inputs("MGC", ["FOMC", "NFP", "CPI", "G17"]),
        "stages_read": [
            {"stage": "E.9", "window_dates": "research 2025-04-01..2026-06-12 (280 dates)", "purpose": "screen", "source": E9},
            {"stage": "E.22", "window_dates": "research 2025-04-01..2026-06-12 (280 dates; re-run for D4 power, supply_days 944)",
             "purpose": "power", "source": E22P},
            {"stage": "E.22", "window_dates": "confirmation 2020-02-04..2024-02-29 (944 dates)", "purpose": "confirmation",
             "source": E22C},
        ],
        "tier": tier,
        "verdicts": [verdict_e9, e22_line, "K8 cluster: \"**K8: NULL.**\" (reports/E.22_RETURN.md line 17)"],
        "settlement_note": GC_SETTLE + "; decision times 08:35..14:55 straddle 12:30 (before it for t_k <= 12:30, after "
                           "for later blocks); the exit (" + ("<= 15:04" if "H30" in label else "15:04") + ") can fall after it",
        "exclusion": None,
        "notes": [E2A, "No W_ext read found: E.10, E.17 and E.21 returns mention K8 only as freeze checks."],
    }


rows = [
    flight_row("K8-flight-01 H30 MGC", "B", "- Exit:", "- Not here",
               "E.22: H30 status \"null\", 231 trips, p_upper +0.5969 (reports/E.22_RETURN.md line 319)",
               "E.9: \"Tier B\" (reports/E.9_RETURN.md line 17)"),
    flight_row("K8-flight-01 HEOD MGC", "A", "- Exit:", "- Not here",
               "E.22: \"**NULL**, no edge. UCB95 +2.25 against 71; Holm p 0.574\" (reports/E.22_RETURN.md line 17)",
               "E.9: \"Tier A\" (reports/E.9_RETURN.md line 15)"),
]

rows.append({
    "trigger_id": "K8-oilcad-01 6C",
    "cluster_or_stage": "K8 (Stage E.9)",
    "member_id": "K8-oilcad-01",
    "module": "strategy.members.k8.oilcad (make_6c)",
    "freeze_file": FREEZE,
    "traded_root": "6C",
    "vehicle": "6C",
    "w_ext_root": None,
    "signal_legs": ["MCL"],
    "definition_verbatim": between(OC, "- Decision times T", "- Exit:"),
    "trigger_event": "a 5-minute MCL block return r_t at t (08:05..13:25) with |r_t / s(d)| >= 2.0, s(d) the stdev of the "
                     "20 prior OILCAD_DATES' block returns (n >= 1,000), account flat on 6C, not C6-skipped; repeatable within a day",
    "decision_time_ct": "t = 08:05..13:25 every 5 min; latest bars used = MCL bar opening t - 1 (08:04..13:24 CT) and the "
                        "6C bar at t - 1; fill at the open of the 6C bar at t",
    "side_rule": "BUY if c1 > c6, SELL if c1 < c6.",
    "side_kind": "momentum (sign of the trigger block's move on the signal leg MCL, not the traded root)",
    "intraday_hold": True,
    "exit_rule_verbatim": between(OC, "- Exit:", "- Never an intent"),
    "expected_events_per_year": "every decision time with |z_t| >= 2.0 while flat (several per day possible); counts "
                                "reported: E.9 research 552 trips (190 days) on 255 window dates; E.22 confirmation 1,438 "
                                "trips on 569 window dates (2021-07-12..2024-02-29), max 12 entries per product day",
    "inputs_needed": [
        {"input": "6C 1-minute bars (traded leg)", "covers_w_ext": False, "covers_w_cf": True,
         "path": "W_cf: data/processed_step2/6C/ohlcv-1m_6C_v_0_2019-05-06_2024-02-29_step2.parquet; W_ext: none (6C is not "
                 "among the 17 roots; reports/stage_e17_run_manifest.json stores.6C.ext2010 has no path)",
         "stated_range": "step2 2019-05-06..2024-02-29; 6C s_x 2019-05-06"},
        {"input": "MCL 1-minute bars (signal leg; W_ext equivalent CL)", "covers_w_ext": True, "covers_w_cf": True,
         "path": "W_ext: data/processed_hist/ext2010h/CL/ohlcv-1m_CL_v_0_2010-07-01_2019-04-30_ext2010h.parquet (CL, not MCL); "
                 "W_cf: data/processed_step2/MCL/ohlcv-1m_MCL_v_0_2019-05-06_2024-02-29_step2.parquet (E.22 used MCL from "
                 "s_x 2021-07-12); CL step2 2019-05-06..2024-02-29 also in the E.17 manifest",
         "stated_range": "CL ext2010h 2010-07-01..2019-04-30 (first month 2010-07); MCL s_x 2021-07-12"},
        cal_input("OILCAD_DATES", ["energy", "fx"]),
    ] + guard_inputs("6C", ["FOMC", "NFP", "WPSR"]),
    "stages_read": [
        {"stage": "E.9", "window_dates": "research 2025-04-01..2026-06-16 (255 dates)", "purpose": "screen", "source": E9},
        {"stage": "E.22", "window_dates": "research 2025-04-01..2026-06-16 (255 dates; re-run for D4 power, supply_days 569)",
         "purpose": "power", "source": E22P},
        {"stage": "E.22", "window_dates": "confirmation 2021-07-12..2024-02-29 (569 dates)", "purpose": "confirmation",
         "source": E22C},
    ],
    "tier": "B",
    "verdicts": ["E.9: \"Tier B\" (reports/E.9_RETURN.md line 18; 2 MLL liquidations, line 241)",
                 "E.22: status \"null\", 1438 trips, p_upper +1.0000 (reports/E.22_RETURN.md line 321)",
                 "K8 cluster: \"**K8: NULL.**\" (reports/E.22_RETURN.md line 17)"],
    "settlement_note": "6C 14:00 CT (window 13:59:30-14:00:00, lead grade secondary) for 2010-06-07..2024-02-29, "
                       "reports/stage_e16_settlement.json products.6C.settle; decision times 08:05..13:25 and exits "
                       "(T_e + 15, at most about 13:40) are before it. Signal leg CL settles 13:30 CT (same file); "
                       "decision times <= 13:25 are before it",
    "exclusion": None,
    "notes": [E2A, "No W_ext read found: E.10, E.17 and E.21 returns mention K8 only as freeze checks."],
})

rows.append({
    "trigger_id": "K8-wkndbtc-01 MNQ",
    "cluster_or_stage": "K8 (Stage E.9)",
    "member_id": "K8-wkndbtc-01",
    "module": "strategy.members.k8.wkndbtc (make_mnq)",
    "freeze_file": FREEZE,
    "traded_root": "MNQ",
    "vehicle": "MNQ (NQ bars as price path in E.22's start rule, R-E22-A7)",
    "w_ext_root": "NQ",
    "signal_legs": ["MBT"],
    "definition_verbatim": between(WB, "- Dates: Monday", "- Exit:"),
    "trigger_event": "Monday trade date d (d and Friday d - 3 in WKNDBTC_DATES) with weekend MBT move G = P_S / P_F - 1 "
                     "nonzero (P_F Friday 14:59 bar close, P_S Sunday 17:59 bar close); not C6-skipped",
    "decision_time_ct": "Sunday 18:00 CT (decision on the view at Sunday 17:59); latest bars used = MBT bar 17:59 on CT "
                        "date d - 1 (trade_date d) and the MNQ bar at 17:59 on CT date d - 1; fill at the 18:00 MNQ open",
    "side_rule": "G > 0 BUYS q_c of MNQ, G < 0 SELLS, G = 0 is no trade.",
    "side_kind": "momentum (sign of the weekend move of the signal leg MBT, not the traded root)",
    "intraday_hold": True,
    "exit_rule_verbatim": between(WB, "- Exit:", "- Never an intent"),
    "expected_events_per_year": "at most one per eligible Monday (every eligible Monday with G != 0); counts reported: "
                                "E.9 research 39 trips on 250 window dates; E.22 power supply 34 days in the MBT-limited "
                                "confirmation window (from MBT s_x 2024-01-02)",
    "inputs_needed": [
        {"input": "MBT 1-minute bars (signal leg: Friday 14:59 and Sunday 17:59 bars)", "covers_w_ext": False,
         "covers_w_cf": "partial",
         "path": "W_cf: data/processed_step2/MBT/ohlcv-1m_MBT_v_0_2019-05-06_2024-02-29_step2.parquet, usable from s_x "
                 "2024-01-02 (reports/stage_e_start_rule_K8.json); W_ext: none (MBT has no W_ext data; full-size BTC bars "
                 "not owned, E.22 R-E22-A6/A9)",
         "stated_range": "MBT s_x 2024-01-02..2024-02-29 (34 supply days, E.22 power)"},
        {"input": "MNQ price path (NQ 1-minute bars)", "covers_w_ext": True, "covers_w_cf": True,
         "path": "W_ext: data/processed_hist/ext2010/NQ/ohlcv-1m_NQ_v_0_2010-06-07_2019-04-30_ext2010.parquet; W_cf: "
                 "data/processed_step2/NQ/ohlcv-1m_NQ_v_0_2019-05-06_2024-02-29_step2.parquet. MNQ step 2 not owned "
                 "(E.22 R-E22-A3); E.22's not-run reason notes the strict reading of A2 gives no NQ path for MNQ",
         "stated_range": "ext2010 2010-06-07..2019-04-30; step2 2019-05-06..2024-02-29; NQ s_x 2019-05-06"},
        cal_input("WKNDBTC_DATES", ["equity"], crypto=True),
    ] + guard_inputs("MNQ", ["FOMC", "NFP", "CPI", "ISM_SERVICES"]),
    "stages_read": [
        {"stage": "E.9", "window_dates": "research 2025-04-01..2026-06-12 (250 dates)", "purpose": "screen", "source": E9},
        {"stage": "E.22", "window_dates": "research 2025-04-01..2026-06-12 (250 dates; re-run for D4 power, supply_days 34)",
         "purpose": "power", "source": E22P},
        {"stage": "E.22", "window_dates": None, "purpose": "confirmation",
         "source": E22C + "; status not_run (reports/stage_e22_notrun_K8.json): no confirmation-window outcome read"},
    ],
    "tier": "A",
    "verdicts": ["E.9: \"Tier A\" (reports/E.9_RETURN.md line 16)",
                 "E.22: \"**INCONCLUSIVE BY DESIGN** (D4: MBT-limited window 34 days < n_b 43; BTC not owned); not run.\" "
                 "(reports/E.22_RETURN.md line 18)",
                 "K8 cluster: \"**K8: NULL.**\" (reports/E.22_RETURN.md line 17)"],
    "settlement_note": "NQ 15:15 CT for 2010-06-07..2020-10-25 and 15:00 CT (window 14:59:30-15:00:00) for "
                       "2020-10-26..2024-02-29, reports/stage_e16_settlement.json products.NQ.settle (no MNQ entry); the "
                       "decision (Sunday 18:00, start of trade date d) and the exit (Monday 14:59) are before trade date "
                       "d's settlement; the signal's P_F (Friday 14:59) is before Friday's 15:00/15:15 settlement",
    "exclusion": None,
    "notes": ["Hold spans Sunday 18:00 to Monday 14:59 CT within one trade date d (overnight plus day session).",
              "No W_ext read found: E.10, E.17 and E.21 returns mention K8 only as freeze checks."],
})

SOURCES = [
    "reports/stage_e23_briefs/brief_inventory.md (whole)",
    "reports/stage_e_k8_member_freeze.json (whole, 2.5 KB)",
    "strategy/members/k8/flight.py docstring (lines 1-42)",
    "strategy/members/k8/oilcad.py docstring (lines 1-28)",
    "strategy/members/k8/wkndbtc.py docstring (lines 1-25)",
    "strategy/members/k8/_calendar.py docstring (lines 1-23), TABLE_RANGE (line 50), *_NOT_FULL heads",
    "strategy/members/k8/_releases.py docstring (lines 1-19), constants (lines 23-28), GUARD_ROWS counted by row-id prefix",
    "data/calendars/hist2010/{energy,equity,fx,metals}.json: products and coverage fields only; directory listing (no crypto.json)",
    "reports/stage_e14_cal_releases.json: coverage, counts, release kinds only",
    "reports/stage_e2b_release_calendar.json: coverage only; sha256",
    "reports/stage_e17_run_manifest.json: stores paths only",
    "reports/stage_e16_settlement.json: window and settle periods for GC, 6C, NQ, CL",
    "base_rules/constants.py lines 95-108 (settlement constants)",
    "reports/stage_e21_briefs/lead_spec.md lines 12-22",
    "reports/E.9_RETURN.md: grep K8; lines 11-22, 234-242, 376-384",
    "reports/stage_e9_STATE.md: grep K8",
    "reports/E.22_RETURN.md: grep K8 and MES; lines 276-292, 315-325, 636-637",
    "reports/stage_e22_STATE.md: grep K8",
    "reports/stage_e22_confirm_k8/*_confirmation.json: scalar fields (window_dates, s_x, series, trade_rate, status, reason)",
    "reports/stage_e22_power_k8/*_research.json and reports/stage_e9_k8_screen/*_research.json: window_dates, power, series.n_trips",
    "reports/stage_e_start_rule_K8.json: top-level fields, products.MES head, inputs paths",
    "reports/E.2a_RETURN.md lines 268-282; reports/stage_e2a_STATE.md row 11 (grep)",
    "reports/E.10_RETURN.md, reports/E.17_RETURN.md, reports/E.21_RETURN.md: grep K8/flight/oilcad/wkndbtc (freeze checks only)",
    "docs/STAGES.md, progress.md: grep K8",
    "docs/prompts/STAGE_E.23.md lines 120-132 (barred list); data/holdout.py lines 9-10, 127-135 (sealed MES paths)",
]

data = {"assignment": "K8", "rows": rows, "excluded": [], "sources_read": SOURCES, "not_finished": []}
(OUT / "K8.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def yn(v):
    return {True: "yes", False: "no"}.get(v, str(v))


md = ["# K8 inventory (Stage E.23 P1.1)", "",
      "Assignment K8: reports/stage_e_k8_member_freeze.json, 4 members (3 member modules). Rows: 4. Excluded: 0.",
      "Full fields (verbatim rule text, inputs, sources per stage) are in K8.json.", "",
      "| Trigger | Traded / W_ext root | Signal legs | Decision time CT | Side | Exit | Tier | Read on | Verdicts |",
      "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    reads = "; ".join(f"{s['stage']} {s['purpose']} {s['window_dates'] or 'not run'}" for s in r["stages_read"])
    md.append(f"| {r['trigger_id']} | {r['traded_root']} / {r['w_ext_root'] or 'none'} | {', '.join(r['signal_legs'])} | "
              f"{r['decision_time_ct']} | {r['side_kind']} | {r['exit_rule_verbatim'][:90]}... | {r['tier']} | {reads} | "
              f"{' / '.join(r['verdicts'])} |")
md += ["", "## Non-bar inputs: W_ext / W_cf coverage", "",
       "| Trigger | Input | W_ext | W_cf | Path / range |", "|---|---|---|---|---|"]
for r in rows:
    for i in r["inputs_needed"]:
        md.append(f"| {r['trigger_id']} | {i['input']} | {yn(i['covers_w_ext'])} | {yn(i['covers_w_cf'])} | "
                  f"{i['path']} ({i['stated_range']}) |")
md += ["", "## Settlement", ""] + [f"- {r['trigger_id']}: {r['settlement_note']}" for r in rows]
md += ["", "## Notes", "", f"- {E2A}",
       "- No W_ext (2010-06..2019-04) read of any K8 trigger was found; E.10, E.17 and E.21 mention K8 only as freeze checks.",
       "- W_ext gaps: flight needs MES (no W_ext data); oilcad trades 6C (no W_ext data); wkndbtc needs MBT (no W_ext data). "
       "Release guards: FOMC and WPSR have W_ext rows (stage_e14_cal_releases.json); NFP, CPI, G17 and ISM_SERVICES were not found.",
       "", "## Excluded", "", "None: every K8 member is a single-root intraday trigger.", "",
       "## Sources read", ""] + [f"- {s}" for s in SOURCES] + [""]
(OUT / "K8.md").write_text("\n".join(md))
print("rows", len(rows), "inputs", sum(len(r["inputs_needed"]) for r in rows))
