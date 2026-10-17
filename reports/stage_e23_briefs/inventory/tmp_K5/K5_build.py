"""K5 inventory builder (Stage E.23 P1.1, InventoryReaderK5). Reads module docstrings by ast only
(no import, no execution of member code) and writes K5.json and K5.md. Facts below come from the
returns and records cited in each row; nothing here reads bars."""

import ast
import json
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e23_briefs/inventory"
FREEZE = "reports/stage_e_k5_member_freeze.json"


def doc(mod: str) -> str:
    return ast.get_docstring(ast.parse((REPO / f"strategy/members/k5/{mod}.py").read_text()))


def bullets(text: str) -> list[str]:
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("- "):
            if cur is not None:
                out.append(cur)
            cur = line
        elif cur is not None and line.startswith("  "):
            cur += " " + line.strip()
        else:
            if cur is not None:
                out.append(cur)
            cur = None
    if cur is not None:
        out.append(cur)
    return out


def rule_text(mod: str) -> str:
    d = doc(mod)
    lines = d.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("Rule") or ln.startswith("MGC only"):
            return "\n".join(lines[i:])
    return d


def bullet(mod: str, *prefixes: str) -> str:
    hits = [b for b in bullets(doc(mod)) if any(b.lower().startswith(p.lower()) for p in prefixes)]
    return " | ".join(hits) if hits else None


# ---- shared inputs ----
CLOCK = {"input": "frozen D6 day-session clock O_X/C_X (MGC 07:20/12:30, MHG 07:10/12:00), read by "
                  "_port_common.leg_facts via screening.stage_e_frozen.load_frozen_tables().day_session_ct",
         "covers_w_ext": True, "covers_w_cf": True,
         "path": "reports/stage_e2a_vehicle_sizes.json (contracts.O_X/C_X; screening/stage_e_frozen.py:225-237)",
         "stated_range": "not date-indexed (fixed clock); GC and HG rows carry the same O_X/C_X"}
CAL_CF = {"input": "metals group calendar EC-CAL (trade dates, early_halt_ct, closures, engine F; roll "
                   "blackout = data.group_session.roll_blackout over the store's splices)",
          "covers_w_ext": False, "covers_w_cf": True, "path": "data/calendars/metals.py",
          "stated_range": "CALENDAR_COVERAGE = (2019-05-01, 2026-06-19)"}
CAL_EXT = {"input": "metals 2010-2019 group calendar (hist2010; products GC, MGC, SI, SIL, HG, MHG)",
           "covers_w_ext": True, "covers_w_cf": False, "path": "data/calendars/hist2010/metals.json",
           "stated_range": "coverage first 2010-06-01, last 2019-05-31 (counts: 2323 trade dates, 73 early halts, 0 unsourced)"}
SETTLE_GC = ("GC settlement 12:30 CT (window 12:29:00-12:30:00), 2010-06-07..2024-02-29, grade primary "
             "(reports/stage_e16_settlement.json products.GC.settle; MGC itself is not listed, GC is its price path in E.22).")
SETTLE_HG = ("HG settlement 12:00 CT (window 11:59:00-12:00:00), rows 2010-06-07..2017-09-25 and 2017-09-26..2024-02-29 "
             "(reports/stage_e16_settlement.json products.HG.settle; MHG itself is not listed).")

# ---- stage reads ----
E4B = {"stage": "E.4b", "window_dates": "research 2025-04-01..2026-06-17, 295 trade dates on both roots (record window_dates)",
       "purpose": "screen",
       "source": "reports/E.4b_RETURN.md:12-16 (tier table); reports/E.4_RETURN.md:392-402; reports/stage_e4b_k5_screen/"}
E5 = {"stage": "E.5", "window_dates": "research window 2025-04-01..2026-06-17 (power simulation only; K5 stopped before its list, R-D-1, confirmation window never read)",
      "purpose": "power",
      "source": "reports/stage_e5_k5_start_power.md:18-29; reports/E.5_RETURN.md:24, 283-293, 396-399"}
E12_ML = ("E.12", "ML route v2 Gate 0, training window 2019-05..2024-02 (n_dates 1067-1068), MGC rows on GC bars, MHG rows on HG bars",
          "reports/E.12_RETURN.md:9, 19; reports/stage_e12_gate0.md")
E20 = ("E.20", "Part C search features on the step2 search stores, S_X 2019-05-06 (GC)..2024-02-29; the ext2010 backward stores never read (search FAIL, no backward read)",
       "reports/E.20_RETURN.md:16-24, 475, 508, 559; reports/stage_e20_product_summary.md (F6 KEPT list, lines 41-45, 74-75)")
E22P = {"stage": "E.22", "window_dates": "research window (E.5 method power re-run under v13; matched screening records)",
        "purpose": "power", "source": "reports/E.22_RETURN.md:281-284; reports/stage_e22_power_k5/"}


def e22c(window: str, note: str) -> dict:
    return {"stage": "E.22", "window_dates": window, "purpose": "confirmation",
            "source": "reports/E.22_RETURN.md:278, 296-313; reports/stage_e22_confirm_k5/ (" + note + ")"}


MGC_CF = "W_cf 2019-05-06..2024-02-29, 1174 days after roll-blackout exclusions; MGC on GC bars (price_path {'MGC': 'GC'}, U8 via V39)"
MHG_CF = "W_cf 2022-06-01..2024-02-29 (MHG S_X), 425 days; MHG bars"


def ml(stage: tuple, feature: str) -> dict:
    return {"stage": stage[0], "window_dates": stage[1], "purpose": "other",
            "source": stage[2] + f"; ML-route feature {feature}, not the frozen member run"}


def row(**kw) -> dict:
    base = dict(cluster_or_stage="K5 (Stage E.4b)", freeze_file=FREEZE, signal_legs=[], intraday_hold=True,
                exclusion=None)
    base.update(kw)
    keys = ["trigger_id", "cluster_or_stage", "member_id", "module", "freeze_file", "traded_root", "vehicle",
            "w_ext_root", "signal_legs", "definition_verbatim", "trigger_event", "decision_time_ct", "side_rule",
            "side_kind", "intraday_hold", "exit_rule_verbatim", "expected_events_per_year", "inputs_needed",
            "stages_read", "tier", "verdicts", "settlement_note", "exclusion"]
    return {k: base.get(k) for k in keys}


def common(root: str) -> dict:
    mgc = root == "MGC"
    return dict(traded_root=root, vehicle=root, w_ext_root="GC" if mgc else None)


rows = []

# cp1
for root, sig, ent, ex in (("MGC", "07:49", "11:59", "12:28"), ("MHG", "07:39", "11:29", "11:58")):
    mgc = root == "MGC"
    stages = [dict(E4B, window_dates=E4B["window_dates"] + ("" if mgc else "; excluded_before_screening, coverage 0.9196 < 0.95, not screened"))]
    if mgc:
        stages += [E5, ml(E12_ML, "cp1_ret (K1..K7 CP1 ports pooled, all 28 vehicles; reports/stage_e11_signal_coverage.md:40)"),
                   ml(E20, "cp1_ret on GC rows (pooled CP1 port)"), E22P,
                   e22c(MGC_CF, "K5_K5-cp1-01_MGC_confirmation.json, coverage 0.9967, 1132 trips")]
    else:
        stages += [e22c(MHG_CF, "K5_K5-cp1-01_MHG_confirmation.json: excluded_before_screening, coverage 0.6303; not run")]
    rows.append(row(
        trigger_id=f"K5-cp1-01 {root}", member_id="K5-cp1-01", module="strategy/members/k5/cp1.py", **common(root),
        definition_verbatim=rule_text("cp1"),
        trigger_event=f"every trade date: sign of (close of the O+29 bar {sig} CT minus open of the 17:00 CT Globex-open bar of the prior calendar day); zero or missing signal bar: no trade",
        decision_time_ct=f"{sig} (signal bar, last bar the decision reads); entry intent on the {ent} bar (C-31), fill at the next open",
        side_rule=bullet("cp1", "- Entry"), side_kind="momentum",
        exit_rule_verbatim=bullet("cp1", "- Exit"),
        expected_events_per_year="every trade date with a nonzero signal (one entry decision per trade date). Counts: " +
            ("E.4b 284 trips in 295 dates (E.4_RETURN.md:392); E.22 1132 trips in 1174 days (E.22_RETURN.md:300)" if mgc
             else "none: never screened (coverage) and not run in E.22"),
        inputs_needed=[CLOCK, CAL_CF, CAL_EXT],
        stages_read=stages,
        tier="B" if mgc else "n/a",
        verdicts=(["E.4b: Tier B; screen fail, 284 trips, mean -0.6037, t -0.131 (E.4_RETURN.md:392; partA_facts_K5_K3.md row 1)",
                   "E.5: \"not run (K5 stopped, R-D-1) | supply 0, n_b 9, inconclusive by design\" (E.5_RETURN.md:283)",
                   "E.22: \"| 1 | K5-cp1-01 MGC | B | null | 1174 | 1132 | -3.2051 | -2.1072 |\" (E.22_RETURN.md:300); cluster K5 \"no statement\""]
                  if mgc else
                  ["E.4b: \"excluded (OC-H) | cp1 MHG, cp2 MHG (coverage 0.9196, 0.8966: not screened)\" (E.4b_RETURN.md:15)",
                   "E.5: \"excluded | not run (K5 stopped, R-D-1) | coverage_below_0.95\" (E.5_RETURN.md:284)",
                   "E.22: \"| 2 | K5-cp1-01 MHG | excluded | not run |\" (E.22_RETURN.md:301)"]),
        settlement_note=(SETTLE_GC if mgc else SETTLE_HG) + f" Decision data {sig} and entry bar {ent}: before settlement; exit bar {ex}: before settlement.",
    ))

# cp2
for root, rng, elig, cut in (("MGC", "[07:20, 07:35)", "07:35..12:29", "12:30"), ("MHG", "[07:10, 07:25)", "07:25..11:59", "12:00")):
    mgc = root == "MGC"
    stages = [dict(E4B, window_dates=E4B["window_dates"] + ("" if mgc else "; excluded_before_screening, coverage 0.8966 < 0.95, not screened"))]
    if mgc:
        stages += [E5, ml(E12_ML, "cp2_range, cp2_brk (K1..K7 CP2 ports pooled; reports/stage_e11_signal_coverage.md:41)"),
                   ml(E20, "cp2_range, cp2_brk on GC rows (pooled CP2 port)"), E22P,
                   e22c(MGC_CF, "K5_K5-cp2-01_MGC_confirmation.json, coverage 0.9978, 1166 trips")]
    else:
        stages += [e22c(MHG_CF, "K5_K5-cp2-01_MHG_confirmation.json: excluded_before_screening, coverage 0.6308; not run")]
    rows.append(row(
        trigger_id=f"K5-cp2-01 {root}", member_id="K5-cp2-01", module="strategy/members/k5/cp2.py", **common(root),
        definition_verbatim=rule_text("cp2"),
        trigger_event=f"first bar opening in {elig} CT whose close is >= OR_high + 4 ticks or <= OR_low - 4 ticks of the opening range {rng}; one entry per trade date",
        decision_time_ct=f"variable: the first qualifying eligible bar, {elig} CT (the intent is sent on that bar)",
        side_rule=bullet("cp2", "- Entry"), side_kind="momentum",
        exit_rule_verbatim=bullet("cp2", "- Exit"),
        expected_events_per_year="every trade date with a breakout bar before C (one entry per trade date). Counts: " +
            ("E.4b 295 trips in 295 dates (E.4_RETURN.md:394); E.22 1166 trips in 1174 days (E.22_RETURN.md:302)" if mgc
             else "none: never screened (coverage) and not run in E.22"),
        inputs_needed=[CLOCK, CAL_CF, CAL_EXT],
        stages_read=stages,
        tier="B" if mgc else "n/a",
        verdicts=(["E.4b: Tier B; screen fail, 295 trips, mean +10.5570, t 0.906 (E.4_RETURN.md:394)",
                   "E.5: \"not run (K5 stopped, R-D-1) | supply 0, n_b 44, inconclusive by design\" (E.5_RETURN.md:285)",
                   "E.22: \"| 3 | K5-cp2-01 MGC | B | null | 1174 | 1166 | -3.8527 | -0.3417 |\" (E.22_RETURN.md:302); cluster K5 \"no statement\""]
                  if mgc else
                  ["E.4b: \"excluded (OC-H) | cp1 MHG, cp2 MHG (coverage 0.9196, 0.8966: not screened)\" (E.4b_RETURN.md:15)",
                   "E.5: \"excluded | not run (K5 stopped, R-D-1) | coverage_below_0.95\" (E.5_RETURN.md:286)",
                   "E.22: \"| 4 | K5-cp2-01 MHG | excluded | not run |\" (E.22_RETURN.md:303)"]),
        settlement_note=(SETTLE_GC if mgc else SETTLE_HG) + f" Entry decision bars {elig}: all before settlement ({cut}); the exit 75 present bars after entry (or the engine's F, 15:08 CT on a regular metals day) can fall after settlement.",
    ))

# cp3
for root, obar, cbar, exb in (("MGC", "07:20", "12:29", "12:28"), ("MHG", "07:10", "11:59", "11:58")):
    mgc = root == "MGC"
    stages = [E4B, E5]
    if mgc:
        stages += [ml(E12_ML, "cp3_clv (K1..K7 CP3 ports pooled; reports/stage_e11_signal_coverage.md:42)"),
                   ml(E20, "cp3_clv on GC rows (pooled CP3 port)"), E22P,
                   e22c(MGC_CF, "K5_K5-cp3-01_MGC_confirmation.json, coverage 0.9983, 489 trips")]
    else:
        stages += [ml(E12_ML, "cp3_clv (pooled CP3 port; MHG rows on HG bars)"), E22P,
                   e22c(MHG_CF, "K5_K5-cp3-01_MHG_confirmation.json: excluded_before_screening, coverage 0.7735; no series")]
    rows.append(row(
        trigger_id=f"K5-cp3-01 {root}", member_id="K5-cp3-01", module="strategy/members/k5/cp3.py", **common(root),
        definition_verbatim=rule_text("cp3"),
        trigger_event=f"on the O bar ({obar} CT) of trade date d: CLV of the most recent complete prior daily bar (bars [O, C), close of the {cbar} bar) >= 0.8 buys, <= 0.2 sells",
        decision_time_ct=f"{obar} (the O bar of d, which carries the early-halt and instrument guards; the signal itself uses d-1's bars through {cbar})",
        side_rule=bullet("cp3", "- On the bar at O"), side_kind="other: side fixed by the prior complete day's close location (CLV >= 0.8 buy, <= 0.2 sell), not by a trigger-day move",
        exit_rule_verbatim=bullet("cp3", "- Exit"),
        expected_events_per_year="trade dates whose prior complete day closes in its top or bottom 20% of range. Counts: " +
            ("E.4b 101 trips in 295 dates (E.4_RETURN.md:396); E.22 489 trips in 1174 days (E.22_RETURN.md:304)" if mgc
             else "E.4b 126 trips in 295 dates (E.4_RETURN.md:397); E.22 none (no series)"),
        inputs_needed=[CLOCK, CAL_CF, CAL_EXT],
        stages_read=stages,
        tier="B",
        verdicts=(["E.4b: Tier B; screen fail, 101 trips, mean +8.4945, t 0.793; \"would pass the screen (t 1.25) without its two XFA liquidations\" (E.4b_RETURN.md:121-122)",
                   "E.5: \"not run (K5 stopped, R-D-1) | supply 0, n_b 62, inconclusive by design\" (E.5_RETURN.md:287)",
                   "E.22: \"| 5 | K5-cp3-01 MGC | B | null | 1174 | 489 | -5.1667 | -1.5998 |\" (E.22_RETURN.md:304); cluster K5 \"no statement\""]
                  if mgc else
                  ["E.4b: Tier B; screen fail, 126 trips, mean +3.2468, t 0.695 (E.4_RETURN.md:397)",
                   "E.5: \"not run (K5 stopped, R-D-1) | supply 425, n_b 52, power sufficient\" (E.5_RETURN.md:288)",
                   "E.22: \"| 6 | K5-cp3-01 MHG | B | inconclusive |\" (E.22_RETURN.md:305); \"blocking: K5-cp3-01 MHG (inconclusive: record status 'excluded_before_screening': no series)\" (E.22_RETURN.md:312)"]),
        settlement_note=(SETTLE_GC if mgc else SETTLE_HG) + f" Decision bar {obar}: before settlement; exit bar {exb}: before settlement.",
    ))

# preauc
AM = {"input": "GOLD_AM_AUCTIONS (LBMA gold AM auction days and CT instant T, 04:30 or 05:30 CT) with NO_AUCTION_DAYS",
      "covers_w_ext": False, "covers_w_cf": True, "path": "strategy/members/k5/_releases.py (generated from reports/stage_e2b_release_calendar.json + reports/stage_e4b_release_check.json)",
      "stated_range": "TABLE_RANGE = (2019-05-01, 2026-06-19); 1802 AM days (124 at 05:30 CT). W_ext: not found; reports/stage_e20_product_summary.md:61 \"no gold fix calendar for 2010-2019 on disk (GC reader)\"; grep of data/calendars/hist2010/, reports/stage_e14_cal_releases.json (NGS, WPSR, FOMC only) and reports/stage_e2b_release_calendar.json (coverage 2019-05-01..2026-06-21, no LBMA rows) found none. E.4b_RETURN.md:185-186: its 2019-2024 no-auction days need the K5-L-01 re-check if it reaches Tier A"}
rows.append(row(
    trigger_id="K5-preauc-01 MGC", member_id="K5-preauc-01", module="strategy/members/k5/preauc.py", **common("MGC"),
    definition_verbatim=rule_text("preauc"),
    trigger_event="every scheduled gold AM auction day of GOLD_AM_AUCTIONS (10:30 London = T, 04:30 or 05:30 CT): unconditional sell at T-30",
    decision_time_ct="03:59 (or 04:59 in 5-hour weeks): the entry bar T-31 is the only bar read; fill at the T-30 open",
    side_rule=bullet("preauc", "- entry"), side_kind="calendar",
    exit_rule_verbatim=bullet("preauc", "- exit"),
    expected_events_per_year="every London AM auction day (weekdays less England-and-Wales bank holidays): table 1802 days 2019-05-01..2026-06-19. Counts: E.4b 280 trips in 295 dates (E.4_RETURN.md:398); E.22 1115 trips (E.22_RETURN.md:306)",
    inputs_needed=[CLOCK, AM, CAL_CF, CAL_EXT],
    stages_read=[E4B, E5, ml(E12_ML, "k5_preauc_msince (minutes since the AM auction instant)"), E22P,
                 e22c(MGC_CF, "K5_K5-preauc-01_MGC_confirmation.json, coverage 0.9998, 1115 trips")],
    tier="B",
    verdicts=["E.4b: Tier B; screen fail, 280 trips, mean +1.3052, t 0.358 (E.4_RETURN.md:398)",
              "E.5: \"not run (K5 stopped, R-D-1) | supply 0, n_b 6, inconclusive by design\" (E.5_RETURN.md:289)",
              "E.20: k5_preauc_msince DROPPED by F6, \"no gold fix calendar for 2010-2019 on disk (GC reader)\" (stage_e20_product_summary.md:61)",
              "E.22: \"| 7 | K5-preauc-01 MGC | B | null | 1174 | 1115 | -4.0368 | -3.0145 |\" (E.22_RETURN.md:306); cluster K5 \"no statement\""],
    settlement_note=SETTLE_GC + " Entry 03:59/04:59 and exit bar T-2 (04:28/05:28): before settlement.",
))

# pmfix
PM = dict(AM, input="GOLD_PM_AUCTIONS (LBMA gold PM auction days and CT instant T_P, 09:00 or 10:00 CT), less the 14 PM no-auction days",
          stated_range=AM["stated_range"].replace("1802 AM days (124 at 05:30 CT)", "1788 PM days, 14 no-auction rows"))
rows.append(row(
    trigger_id="K5-pmfix-01 MGC", member_id="K5-pmfix-01", module="strategy/members/k5/pmfix.py", **common("MGC"),
    definition_verbatim=rule_text("pmfix"),
    trigger_event="every scheduled gold PM auction day of GOLD_PM_AUCTIONS (15:00 London = T_P, 09:00 or 10:00 CT): sign of close(T_P+1) - close(T_P-1); zero: no trade",
    decision_time_ct="09:01 (or 10:01 in 5-hour weeks): the T_P+1 bar; fill at the T_P+2 open",
    side_rule=bullet("pmfix", "- entry"), side_kind="momentum",
    exit_rule_verbatim=bullet("pmfix", "- exit"),
    expected_events_per_year="every London PM auction day with a nonzero move: table 1788 days 2019-05-01..2026-06-19. Counts: E.4b 278 trips (E.4_RETURN.md:399); E.22 1080 trips in the record (trips file n_trips; executed by --all, \"present and not used\", E.22_RETURN.md:606)",
    inputs_needed=[CLOCK, PM, CAL_CF, CAL_EXT],
    stages_read=[E4B, E5, ml(E12_ML, "k5_pmfix_move (close(T_P+1) - close(T_P-1))"), E22P,
                 e22c(MGC_CF, "K5_K5-pmfix-01_MGC_confirmation.json, status run, label mean_holding_below_10min, 1080 trips, not used in the verdict")],
    tier="n/a",
    verdicts=["E.4b: \"pmfix MGC (mean hold 9.964 min: screened, t -2.194)\" excluded (OC-H) (E.4b_RETURN.md:15); \"excluded only because one liquidation at its 09:02 entry bar made a 0.0-minute trip\" (E.4b_RETURN.md:121-125)",
              "E.5: \"excluded | not run (K5 stopped, R-D-1) | supply 0, n_b 11, inconclusive by design\" (E.5_RETURN.md:290)",
              "E.20: k5_pmfix_move DROPPED by F6, \"no gold fix calendar for 2010-2019 on disk (GC reader)\" (stage_e20_product_summary.md:61)",
              "E.22: \"| 8 | K5-pmfix-01 MGC | excluded | not run |\" (E.22_RETURN.md:307)"],
    settlement_note=SETTLE_GC + " Decision 09:01/10:01 and exit bar T_P+11 (09:11/10:11): before settlement.",
))

# fomc
FOMC_CF = {"input": "FOMC_STATEMENT_DATES (FOMC statement rows at 13:00 CT)", "covers_w_ext": False, "covers_w_cf": True,
           "path": "strategy/members/k5/_releases.py (from reports/stage_e2b_release_calendar.json FOMC rows)",
           "stated_range": "TABLE_RANGE = (2019-05-01, 2026-06-19); 57 dates, 2019-05-01..2026-06-17"}
FOMC_EXT = {"input": "2010-2019 FOMC statement calendar (E.14)", "covers_w_ext": True, "covers_w_cf": False,
            "path": "reports/stage_e14_cal_releases.json (release FOMC)",
            "stated_range": "coverage 2010-06-01..2019-05-31; 72 FOMC rows 2010-06-23..2019-05-01 (14 time:inferred, 58 time:official). Instants in CT (computed from instant_utc): 50 at 13:00 CT (2013-03-20..2019-05-01), 14 at 13:15, 4 at 11:30, 3 at 11:35, 1 at 11:20. The frozen member reads only its own literal table, which starts 2019-05-01; stage_e20_product_summary.md:67-76 (the Kept-with-recorded-partial-row-loss paragraph) notes the frozen 13:00 CT filter matches 2010-2019 statements only from 2013-03-20"}
rows.append(row(
    trigger_id="K5-fomc-01 MGC", member_id="K5-fomc-01", module="strategy/members/k5/fomc.py", **common("MGC"),
    definition_verbatim=rule_text("fomc"),
    trigger_event="every FOMC statement date of FOMC_STATEMENT_DATES (13:00 CT): sign of close(13:04) - close(12:59); zero: no trade",
    decision_time_ct="13:04 (the entry decision bar); fill at the 13:05 open",
    side_rule=bullet("fomc", "- entry"), side_kind="momentum",
    exit_rule_verbatim=bullet("fomc", "- exit"),
    expected_events_per_year="8 scheduled FOMC statements a year (57 dates 2019-05..2026-06). Counts: E.4b 8 trips (10 FOMC dates in the window, 2 roll blackouts untraded; E.4b_RETURN.md:13, 78, 153-154); E.22 34 trips (E.22_RETURN.md:290, 308)",
    inputs_needed=[CLOCK, FOMC_CF, FOMC_EXT, CAL_CF, CAL_EXT],
    stages_read=[E4B, E5, E22P, e22c(MGC_CF, "K5_K5-fomc-01_MGC_confirmation.json, coverage 0.9957, 34 trips; Tier A, Holm K = 5")],
    tier="A",
    verdicts=["E.4b: \"| A | K5-fomc-01 MGC | 8 | +2.3498 | 1.846 |\" (E.4b_RETURN.md:13)",
              "E.5: \"| K5 | none: stopped before its list (R-D-1) | K5-fomc-01 MGC | not run | ... | inconclusive by design: supply 0 |\" (E.5_RETURN.md:24)",
              "E.11: excluded from the v2 signal library, \"known after the last decision time\" (E.11_RETURN.md:221)",
              "E.22: \"K5-fomc-01 MGC (on GC bars, U8): NULL, no edge. UCB95 +0.09 against eps 71 ticks; Holm p 0.894.\" (E.22_RETURN.md:12); \"| K5 | no statement | K5-fomc-01 MGC | null | -0.3129 | +0.0930 | +71 | 34 | 0.8938 (not rejected) | -1.253 | 5.43e-12 | +0.043 | no edge (first failing: holm) |\" (E.22_RETURN.md:290)"],
    settlement_note=SETTLE_GC + " Decision 13:04 CT: AFTER the 12:30 CT GC settlement.",
))

# ovr
FULL = {"input": "METALS_FULL_SESSIONS (20 reference dates: metals trade dates with no early halt)",
        "covers_w_ext": False, "covers_w_cf": True, "path": "strategy/members/k5/_calendar.py (generated from data/calendars/metals.py)",
        "stated_range": "2019-05-01..2026-06-19, 1784 dates. W_ext: no literal table on disk; stage_e20_product_summary.md:74-75 says k5_ovr_*'s \"full-session tables derive from the 2010-2019 group calendars\" (data/calendars/hist2010/metals.json)"}
for root, ts, last, n_e4b, mgc in (("MGC", "08:20, 09:20, 10:20, 11:20, 12:20", "12:19", 289, True),
                                   ("MHG", "08:10, 09:10, 10:10, 11:10", "11:09", 190, False)):
    if mgc:
        stages = [E4B, E5, ml(E12_ML, "k5_ovr_ret, k5_ovr_pct"), ml(E20, "k5_ovr_ret, k5_ovr_pct on GC rows (KEPT by F6)"), E22P,
                  e22c(MGC_CF, "K5_K5-ovr-01_MGC_confirmation.json, coverage 0.9979, 1221 trips")]
    else:
        stages = [E4B, E5, ml(E12_ML, "k5_ovr_ret, k5_ovr_pct (MHG rows on HG bars)"), E22P,
                  e22c(MHG_CF, "K5_K5-ovr-01_MHG_confirmation.json: excluded_before_screening, coverage 0.7688; no series")]
    rows.append(row(
        trigger_id=f"K5-ovr-01 {root}", member_id="K5-ovr-01", module="strategy/members/k5/ovr.py", **common(root),
        definition_verbatim=rule_text("ovr"),
        trigger_event=f"at each decision time t ({ts} CT): the trailing 60-minute return r(t) at or below P10 (buy) or at or above P90 (sell) of the same-clock values over the 20 prior full sessions; flat only",
        decision_time_ct=f"t-1 for each t: {', '.join(x.strip()[:3] + str(int(x.strip()[3:]) - 1).zfill(2) for x in ts.split(','))} CT (last {last}); fill at the open of t",
        side_rule=bullet("ovr", "- Entry"), side_kind="fade",
        exit_rule_verbatim=bullet("ovr", "- Exit"),
        expected_events_per_year=f"up to {5 if mgc else 4} decision times per trade date, entries only in the 10% tails and only when flat. Counts: " +
            (f"E.4b {n_e4b} trips in 295 dates (E.4_RETURN.md:401); E.22 1221 trips in 1174 days (E.22_RETURN.md:309)" if mgc
             else f"E.4b {n_e4b} trips in 295 dates (E.4_RETURN.md:402); E.22 none (no series)"),
        inputs_needed=[CLOCK, FULL, CAL_CF, CAL_EXT],
        stages_read=stages,
        tier="B",
        verdicts=(["E.4b: Tier B; screen fail, 289 trips, mean -3.5608, t -0.330 (E.4_RETURN.md:401)",
                   "E.5: \"not run (K5 stopped, R-D-1) | supply 0, n_b 29, inconclusive by design\" (E.5_RETURN.md:292)",
                   "E.22: \"| 10 | K5-ovr-01 MGC | B | null | 1174 | 1221 | -5.5728 | -2.8922 |\" (E.22_RETURN.md:309); cluster K5 \"no statement\""]
                  if mgc else
                  ["E.4b: Tier B; screen fail, 190 trips, mean -3.3977, t -1.201 (E.4_RETURN.md:402)",
                   "E.5: \"not run (K5 stopped, R-D-1) | supply 425, n_b 18, power sufficient\" (E.5_RETURN.md:293)",
                   "E.22: \"| 11 | K5-ovr-01 MHG | B | inconclusive |\" (E.22_RETURN.md:310); blocking, \"record status 'excluded_before_screening': no series\" (E.22_RETURN.md:312)"]),
        settlement_note=(SETTLE_GC if mgc else SETTLE_HG) + f" All decision bars (last {last}) before settlement; the exit at t+58 for the last t ({'13:18' if mgc else '12:08'}) is after it.",
    ))

doc_out = {
    "assignment": "K5",
    "rows": rows,
    "excluded": [],
    "notes": [
        "All 11 frozen K5 trials have a row; none falls in the brief's exclusion list (no ML model member, no search configuration, no multi-day rule, no combination book). The OC-H exclusions (cp1 MHG, cp2 MHG coverage; pmfix MGC mean hold) are screening tier outcomes, recorded under tier/verdicts, not brief exclusions.",
        "W_ext: MGC maps to GC (ext2010 store data/processed_hist/ext2010/GC/ohlcv-1m_GC_v_0_2010-06-07_2019-04-30_ext2010.parquet per reports/stage_e17_run_manifest.json stores.GC; first trade date 2010-06-07 from the file name, not opened). HG is not one of the 17 roots and has no manifest entry: MHG rows have no W_ext data.",
        "Program N: E.4b added 9 screened K5 trials (cp1 MHG and cp2 MHG never screened; pmfix screened then excluded, counts) (E.4_RETURN.md:440-442).",
        "C1 (E.13-E.17 ML model, NG rows) lists k5_ovr_pct, k5_ovr_ret, k5_pmfix_move, k5_preauc_msince among its feature names (reports/stage_e14_c1_model.json); C1 stopped at guard C10 in E.17 with no statistic (E.17_RETURN.md:7-10). Not entered as a read of the K5 triggers (ML model, NG rows).",
        "MGC confirmation used GC bars as MGC's price path with MGC's costs and tick (R-E22-A4, E.22_RETURN.md:627; verifier note E.22_RETURN.md:606).",
    ],
    "sources_read": [
        "docs/prompts: none; reports/stage_e23_briefs/brief_inventory.md (full)",
        "reports/stage_e_k5_member_freeze.json (full, 4690 bytes)",
        "strategy/members/k5/cp1.py (full), cp2.py (full), cp3.py (lines 1-60), fomc.py (1-45), pmfix.py (1-45), preauc.py (1-50), ovr.py (1-70)",
        "strategy/members/k5/_releases.py (lines 1-28, 1279-1292; top-level names by grep)",
        "strategy/members/k5/_calendar.py (lines 1-23)",
        "strategy/members/k5/_port_common.py (lines 1-37, 60-82)",
        "screening/stage_e_frozen.py (lines 218-242, grep of table paths)",
        "reports/stage_e2a_vehicle_sizes.json (contracts O_X/C_X for MGC, MHG, GC, HG only)",
        "reports/stage_e22_briefs/partA_facts_K5_K3.md (lines 1-87, 140-150)",
        "reports/E.4b_RETURN.md (lines 10-17; others via partA_facts quotes)",
        "reports/E.4_RETURN.md (grep K5: 392-402, 437-445)",
        "reports/E.5_RETURN.md (grep K5-: 24, 283-293, 332, 397)",
        "reports/E.22_RETURN.md (grep K5; lines 10-16, 268-300)",
        "reports/E.1, E.2a, E.2b, E.6-E.21 _RETURN.md (grep K5 only)",
        "reports/E.11_RETURN.md (lines 205-225); reports/E.12_RETURN.md (grep Gate 0 / window); reports/E.20_RETURN.md (lines 8-24, grep windows); reports/E.17_RETURN.md (lines 1-25)",
        "reports/stage_e12_gate0.md (header lines 1-14, grep k5_)",
        "reports/stage_e20_product_summary.md (lines 30-80, 125-146)",
        "reports/stage_e11_signal_coverage.md (grep cp1_ret/cp2_brk/cp3_clv)",
        "ml_route_v2/signals/k5.py (lines 1-40)",
        "reports/stage_e22_confirm_k5/*_confirmation.json (fields window, status, coverage, labels, price_path, bars.path only); K5_K5-pmfix-01_MGC_confirmation_trips.json (n_trips only)",
        "reports/stage_e14_cal_releases.json (coverage, counts, FOMC rows' instant_utc/date only)",
        "reports/stage_e14_c1_model.json (k5_* names only)",
        "reports/stage_e2b_release_calendar.json (coverage; release names and date ranges only)",
        "data/calendars/hist2010/metals.json (coverage, products, counts only)",
        "data/calendars/metals.py (grep CALENDAR_COVERAGE)",
        "reports/stage_e16_settlement.json (window; products GC and HG settle rows)",
        "reports/stage_e17_run_manifest.json (stores.GC only)",
        "base_rules/common.py (lines 85-110), base_rules/constants.py (SETTLEMENT_PATH), data/group_session.py (grep roll_blackout)",
        "docs/STAGES.md (grep K5)",
    ],
    "not_finished": [
        "progress.md K5 lines were not read individually (docs/STAGES.md and the returns were used); no stage beyond those listed was found by grep of the returns.",
        "The roll-blackout input for W_ext (GC splices on the ext2010 store) was not checked: it is derived from bars, which this brief forbids opening.",
    ],
}
(OUT / "K5.json").write_text(json.dumps(doc_out, indent=1) + "\n")

# ---- markdown ----
md = ["# Stage E.23 P1.1 inventory: K5 (InventoryReaderK5-OpusHigh)", "",
      f"Rows: {len(rows)} (all 11 frozen K5 trials). Excluded: 0. Freeze: {FREEZE} (11 members, cluster sha256 1d0c974f...).", "",
      "| Trigger | Root (W_ext) | Event | Decision CT | Side | Tier | Inputs W_ext / W_cf | Stages read | Settlement |",
      "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    inp = "; ".join(f"{i['input'].split(' (')[0]}: {'Y' if i['covers_w_ext'] else 'N'}/{'Y' if i['covers_w_cf'] else 'N'}"
                     for i in r["inputs_needed"])
    st = "; ".join(f"{s['stage']} {s['purpose']}" for s in r["stages_read"])
    md.append(f"| {r['trigger_id']} | {r['traded_root']} ({r['w_ext_root'] or 'none'}) | {r['trigger_event']} | "
              f"{r['decision_time_ct']} | {r['side_kind']} | {r['tier']} | {inp} | {st} | "
              f"{r['settlement_note'].split('. ')[-1]} |")
md += ["", "Verdicts (verbatim, with the return line) are in K5.json per row.", "",
       "## Inputs not owned for W_ext", "",
       "- GOLD_AM_AUCTIONS / GOLD_PM_AUCTIONS (preauc, pmfix): 2019-05-01..2026-06-19 only; no 2010-2019 gold auction table found (stage_e20_product_summary.md:61).",
       "- FOMC_STATEMENT_DATES (fomc): literal table 2019-05-01..2026-06-17; a 2010-2019 FOMC calendar exists in reports/stage_e14_cal_releases.json (50 statements at 13:00 CT, from 2013-03-20).",
       "- METALS_FULL_SESSIONS (ovr): literal table 2019-05-01..2026-06-19; derivable from data/calendars/hist2010/metals.json (2010-06-01..2019-05-31) per E.20's F6 note.",
       "- MHG (all MHG rows): HG is not one of the 17 W_ext roots.", "",
       "## Excluded", "", "None (see notes in K5.json).", "",
       "## Notes", ""] + [f"- {n}" for n in doc_out["notes"]] + ["", "## Sources read", ""] + \
      [f"- {s}" for s in doc_out["sources_read"]] + ["", "## Not finished", ""] + [f"- {s}" for s in doc_out["not_finished"]]
(OUT / "K5.md").write_text("\n".join(md) + "\n")
print("rows", len(rows), "none-fields", sum(1 for r in rows for k, v in r.items() if v is None and k not in ("w_ext_root", "exclusion")))
