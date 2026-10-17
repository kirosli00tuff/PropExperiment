"""K7 inventory builder (InventoryReaderK7). Reads only member module docstrings; writes K7.json and K7.md."""
import ast
import json
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e23_briefs/inventory"
FREEZE = "reports/stage_e_k7_member_freeze.json"


def doc(mod):
    return ast.get_docstring(ast.parse((REPO / f"strategy/members/k7/{mod}.py").read_text()))


def bullets(text):
    """Split the docstring into its '- ' bullets (continuation lines joined)."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("- "):
            if cur is not None:
                out.append(cur)
            cur = line[2:].strip()
        elif cur is not None and line.startswith("  "):
            cur += " " + line.strip()
        else:
            if cur is not None:
                out.append(cur)
            cur = None
    if cur is not None:
        out.append(cur)
    return out


def pick(bs, prefix):
    return [b for b in bs if b.startswith(prefix)]


def sub(text, start, end=None):
    text = " ".join(text.split())
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return " ".join(text[i:j].split())


CAL = "strategy/members/k7/_calendar.py"
IN_FULL = {"input": "CRYPTO_FULL_SESSIONS (EC-CAL crypto trade dates without early halt and with regular engine F 15:08 CT)",
           "covers_w_ext": False, "covers_w_cf": True, "path": CAL,
           "stated_range": "coverage 2019-05-01..2026-06-19 (_calendar.py docstring; EC_CAL_COVERAGE)"}
IN_DEG = {"input": "VENDOR_DEGRADED (crypto trade dates whose ISO date is a degraded Databento GLBX.MDP3 UTC date)",
          "covers_w_ext": False, "covers_w_cf": True, "path": CAL,
          "stated_range": "same range as CRYPTO_FULL_SESSIONS, 2019-05-01..2026-06-19"}
IN_GCAL = {"input": "crypto group calendar (EC-CAL; trade-date booking, early halts, engine F)",
           "covers_w_ext": False, "covers_w_cf": True, "path": "data/calendars/crypto.py",
           "stated_range": "CALENDAR_COVERAGE = (2019-05-01, 2026-06-19)"}
IN_MBTX = {"input": "MBTX table (MBT last trading days and T_exp = 16:00 Europe/London in CT)",
           "covers_w_ext": False, "covers_w_cf": True, "path": CAL,
           "stated_range": "MBTX_MONTHS 2021-05..2026-06; less 2021-12-30 and 2025-12-24 (R-1b-1); rows before the "
                           "research window are the rule's output, unchecked (E.6_RETURN Task 7: 'all but 2021-12-30 unchecked')"}
IN_UKH = {"input": "England-and-Wales bank holidays (used at generation of MBTX)", "covers_w_ext": "unknown",
          "covers_w_cf": "unknown", "path": "reports/stage_e4c_release_check.json (ec_ew)",
          "stated_range": None}
IN_BARS_NOTE = ("MBT bars themselves: no W_ext data (MBT is not one of the 17 ext2010 roots; MBT listed 2021-05-03, "
                "E.18_RETURN item 7); W_cf store bought in E.12 (2021-04..2024-02 chunks, 'MBT 35'), D4 S_X MBT 2024-01-02 "
                "(E.12_RETURN Task 6 line 536; E.22_RETURN line 281), so W_cf for MBT = 2024-01-02..2024-02-29 (41 dates)")

SCREEN = {"stage": "E.6", "window_dates": "research 2025-04-01..2026-06-17, 265 trade dates after 42 roll-blackout dates and 1 UR-1 date",
          "purpose": "screen", "source": "reports/E.6_RETURN.md, Task 5 (screen table) and Task 6; reports/stage_e6_k7_screen/"}
E12_PORT = {"stage": "E.12", "window_dates": "W_cf MBT path S_X 2024-01-02..2024-02-29 (41 dates)",
            "purpose": "other",
            "source": "reports/E.12_RETURN.md lines 18-21 and 536: ML route v2 Gate 0 panel used the pooled port signals "
                      "(cp1_ret / cp2_range, cp2_brk / cp3_clv, reports/stage_e11_signal_coverage.md lines 13-16, 40-42) "
                      "on all vehicles; 'MBT has no Gate 0 row (D4 start 2024-01-02, all 41 dates lost to warm-up)'. "
                      "Not a test of this member."}


def e12_own(sig):
    return {"stage": "E.12", "window_dates": "W_cf MBT path S_X 2024-01-02..2024-02-29 (41 dates)", "purpose": "other",
            "source": f"reports/stage_e11_signal_coverage.md lines 66-68 ({sig} on MBT); reports/E.12_RETURN.md lines "
                      "18-21: 'MBT has no Gate 0 row (D4 start 2024-01-02, all 41 dates lost to warm-up)'. "
                      "Not a test of this member."}


NO_CONF = ("No confirmation or null-side run of any K7 trial in any later return (grep of reports/E.7..E.22_RETURN.md "
           "for K7 member ids finds only freeze-OK lines; E.6_RETURN Task 7 lists it as an open question).")

SETTLE = ("data/calendars/crypto.py _D6_NOTE: 'C 15:00 CT matches CME's daily settlement period for Bitcoin futures, "
          "14:59:00-15:00:00 CT, from which MBT's settlement is copied'.")


def row(mid, mod, cp, **kw):
    d = doc(mod)
    bs = bullets(d)
    base = {
        "trigger_id": f"{mid} MBT", "cluster_or_stage": "K7 (Stage E.6)", "member_id": mid,
        "module": f"strategy/members/k7/{mod}.py", "freeze_file": FREEZE, "traded_root": "MBT",
        "vehicle": "MBT (Micro Bitcoin), q_c 1", "w_ext_root": None, "signal_legs": [],
        "tier": "B",
    }
    base.update(kw)
    base["_bullets"] = bs
    base["_doc"] = d
    return base


def build():
    rows = []
    # cp1
    d = doc("cp1"); bs = bullets(d)
    rows.append(dict(
        trigger_id="K7-cp1-01 MBT", cluster_or_stage="K7 (Stage E.6)", member_id="K7-cp1-01",
        module="strategy/members/k7/cp1.py", freeze_file=FREEZE, traded_root="MBT", vehicle="MBT, q_c 1",
        w_ext_root=None, signal_legs=[],
        definition_verbatim=pick(bs, "Signal") + pick(bs, "Both signal") + pick(bs, "Entry"),
        trigger_event="every trade date with nonzero signal s = sign(close of the 08:59 bar minus open of the trade date's first bar, the 17:00 CT bar of the previous CT date)",
        decision_time_ct="08:59 (signal bar; last bar the decision reads); entry intent on the 14:29 bar, fill at the 14:30 open",
        side_rule=sub(d, "buy if", "; that exact"),
        side_kind="momentum", intraday_hold="yes: 14:30 fill to 14:59 open (about 29 min)",
        exit_rule_verbatim=pick(bs, "Exit"),
        expected_events_per_year="every trade date with nonzero signal; E.6 research screen: 261 trips over 265 trade dates (2025-04-01..2026-06-17)",
        inputs_needed=[IN_GCAL, IN_FULL | {"input": "frozen tables day_session_ct (O 08:30, C 15:00) and engine F 15:08 (rules.sessions); no CRYPTO_FULL_SESSIONS filter in the port (the engine's F governs)", "path": "data/calendars/crypto.py; rules/sessions.py", "stated_range": "crypto calendar coverage 2019-05-01..2026-06-19"}],
        stages_read=[SCREEN, E12_PORT],
        verdicts=["E.6: screen 'fail', Tier 'B' (mean -7.4610 ticks, daily t -1.790, coverage 0.9985; reports/E.6_RETURN.md Task 5 table row 1)"],
        settlement_note=SETTLE + " Decision bar 08:59 and entry fill 14:30 are before the 14:59-15:00 settlement period; the exit fills at the 14:59 open.",
        exclusion=None))
    # cp2
    d = doc("cp2"); bs = bullets(d)
    rows.append(dict(
        trigger_id="K7-cp2-01 MBT", cluster_or_stage="K7 (Stage E.6)", member_id="K7-cp2-01",
        module="strategy/members/k7/cp2.py", freeze_file=FREEZE, traded_root="MBT", vehicle="MBT, q_c 1",
        w_ext_root=None, signal_legs=[],
        definition_verbatim=pick(bs, "Opening range") + pick(bs, "Buffer") + pick(bs, "Eligible") + pick(bs, "Entry"),
        trigger_event="first bar opening in [08:45, 15:00) of CT date d whose close breaks the 08:30-08:45 opening range by 4 ticks",
        decision_time_ct="variable: the first qualifying bar in [08:45, 14:59]; latest possible 14:59 (E.6 Task 6: entries observed 08:46-13:00)",
        side_rule=sub(d, "the first eligible bar whose close", "; a market intent"),
        side_kind="momentum", intraday_hold="yes: 75 bars after the fill, or engine F 15:08 if earlier",
        exit_rule_verbatim=pick(bs, "Exit"),
        expected_events_per_year="at most one per trade date, on dates with a breakout; E.6 research screen: 263 trips over 265 trade dates",
        inputs_needed=[IN_GCAL | {"input": "crypto group calendar and frozen tables day_session_ct (O 08:30, C 15:00), engine F 15:08"}],
        stages_read=[SCREEN, E12_PORT],
        verdicts=["E.6: screen 'fail', Tier 'B' (mean -14.3785 ticks, daily t -1.350, coverage 0.9969, 1 MLL liquidation; reports/E.6_RETURN.md Task 5 row 2)"],
        settlement_note=SETTLE + " Decision bars range up to 14:59, which is the settlement-period minute itself, so a decision is not always before settlement; exits can run to engine F 15:08 (after settlement).",
        exclusion=None))
    # cp3
    d = doc("cp3"); bs = bullets(d)
    rows.append(dict(
        trigger_id="K7-cp3-01 MBT", cluster_or_stage="K7 (Stage E.6)", member_id="K7-cp3-01",
        module="strategy/members/k7/cp3.py", freeze_file=FREEZE, traded_root="MBT", vehicle="MBT, q_c 1",
        w_ext_root=None, signal_legs=[],
        definition_verbatim=pick(bs, "Daily bar") + pick(bs, "Complete day") + pick(bs, "d-1") + pick(bs, "On the bar at O"),
        trigger_event="trade date whose previous complete daily bar (08:30-15:00 CT) has CLV >= 0.8 or <= 0.2",
        decision_time_ct="08:30 (the 08:30 bar of CT date d; the signal itself is d-1's 08:30-14:59 daily bar), fill at the 08:31 open",
        side_rule=sub(d, "CLV >= 0.8 buys", " The cuts"),
        side_kind="other: side = sign of the prior day's close location within its range (CLV >= 0.8 long, <= 0.2 short), i.e. continuation of the prior-day close location; not a trigger-day move",
        intraday_hold="yes: 08:31 fill to 14:59 open",
        exit_rule_verbatim=pick(bs, "Exit"),
        expected_events_per_year="trade dates with prior-day CLV in the tails; E.6 research screen: 101 trips over 265 trade dates",
        inputs_needed=[IN_GCAL | {"input": "crypto group calendar (early_halt_ct flags carried on bars; frozen day_session_ct O 08:30, C 15:00; engine F 15:08)"}],
        stages_read=[SCREEN, E12_PORT],
        verdicts=["E.6: screen 'fail', Tier 'B' (mean -3.1197 ticks, daily t -0.259, coverage 0.9969; reports/E.6_RETURN.md Task 5 row 3)"],
        settlement_note=SETTLE + " Decision at 08:30 is before settlement; the signal day d-1's close C_d is the 14:59 bar, the settlement minute.",
        exclusion=None))
    # expiry
    d = doc("expiry"); bs = bullets(d)
    rows.append(dict(
        trigger_id="K7-expiry-01 MBT", cluster_or_stage="K7 (Stage E.6)", member_id="K7-expiry-01",
        module="strategy/members/k7/expiry.py", freeze_file=FREEZE, traded_root="MBT", vehicle="MBT, q_c 1",
        w_ext_root=None, signal_legs=[],
        definition_verbatim=pick(bs, "Event set") + pick(bs, "T_exp") + pick(bs, "Entry"),
        trigger_event="each MBT last trading day (MBTX date) in CRYPTO_FULL_SESSIONS and not VENDOR_DEGRADED",
        decision_time_ct="04:59 or 05:59 (the T_exp - 301 min bar; no signal read), fill at 05:00 or 06:00",
        side_rule="Long only.",
        side_kind="calendar", intraday_hold="yes: T_exp - 300 min fill to T_exp - 1 min (about 5 h)",
        exit_rule_verbatim=pick(bs, "Exit"),
        expected_events_per_year="12 MBTX dates a year (monthly last trading day); E.6 research screen: 0 trips (12 member-eligible MBTX dates, all roll-blackout dates; 5 refused BUY intents; E.6_RETURN Task 6 item 4)",
        inputs_needed=[IN_MBTX, IN_FULL, IN_DEG, IN_UKH],
        stages_read=[SCREEN | {"source": SCREEN["source"] + "; not traded: every MBTX date a roll-blackout date (K7-L-05)"}, e12_own("k7_expiry_mto, k7_expiry_msince")],
        verdicts=["E.6: screen 'fail', Tier 'B', 'none (calendar partly unverified; not traded)', 0 trips, t 'undefined' (reports/E.6_RETURN.md Task 5 row 4)"],
        settlement_note=SETTLE + " Decision 04:59/05:59 CT is before the 14:59-15:00 daily settlement; the event is the BRR final settlement at T_exp (16:00 London = 10:00 or 11:00 CT).",
        exclusion=None))
    # rev2h
    d = doc("rev2h"); bs = bullets(d)
    rows.append(dict(
        trigger_id="K7-rev2h-01 MBT", cluster_or_stage="K7 (Stage E.6)", member_id="K7-rev2h-01",
        module="strategy/members/k7/rev2h.py", freeze_file=FREEZE, traded_root="MBT", vehicle="MBT, q_c 1",
        w_ext_root=None, signal_legs=[],
        definition_verbatim=pick(bs, "Dates") + pick(bs, "Blocks") + pick(bs, "Decision 10:30") + pick(bs, "Orders"),
        trigger_event="every full, non-degraded trade date: decisions at 10:30 (block 08:30-10:29) and 12:30 (block 10:30-12:29) with nonzero block return",
        decision_time_ct="10:29 and 12:29 (signal bars), entries on the 10:30 / 12:30 bars, fills one minute later",
        side_rule=sub(d, "target1 =", "; 0 if r1"),
        side_kind="fade", intraday_hold="yes: up to 14:29 bar (final exit fills at 14:30 open)",
        exit_rule_verbatim=pick(bs, "Final exit") + pick(bs, "A position the engine"),
        expected_events_per_year="every trade date with nonzero block return, at most 2 entries a date; E.6 research screen: 384 trips on 259 eligible dates (125 with two trips)",
        inputs_needed=[IN_FULL, IN_DEG, IN_GCAL],
        stages_read=[SCREEN, e12_own("k7_rev2h_ret")],
        verdicts=["E.6: screen 'fail', Tier 'B' (mean -28.9198 ticks, daily t -2.285, coverage 0.9967, 2 MLL liquidations; reports/E.6_RETURN.md Task 5 row 5)"],
        settlement_note=SETTLE + " Both decisions (10:29, 12:29) and the 14:30 exit are before settlement.",
        exclusion=None))
    # montrend
    d = doc("montrend"); bs = bullets(d)
    rows.append(dict(
        trigger_id="K7-montrend-01 MBT", cluster_or_stage="K7 (Stage E.6)", member_id="K7-montrend-01",
        module="strategy/members/k7/montrend.py", freeze_file=FREEZE, traded_root="MBT", vehicle="MBT, q_c 1",
        w_ext_root=None, signal_legs=[],
        definition_verbatim=pick(bs, "Dates") + pick(bs, "Bars read") + pick(bs, "20 decision") + pick(bs, "Signal") + pick(bs, "Flatten") + pick(bs, "Entry"),
        trigger_event="Monday trade dates (full, non-degraded): 20 hourly decisions Sunday 18:00..Monday 13:00 CT on the prior hour's sign",
        decision_time_ct="hourly t - 1 min bars: Sunday 17:59 .. Monday 12:59 (entries on the t bar, fill t + 1 min); latest 12:59 Monday",
        side_rule="an entry intent of q in direction s_t (fills at t + 1 min); s_t = sign(close of the bar at t - 1 min - open of the bar at t - 60 min)",
        side_kind="momentum", intraday_hold="yes, within the Monday trade date (Sunday 18:01 CT at the earliest, final exit at Monday 14:00 open); spans CT calendar dates Sunday-Monday",
        exit_rule_verbatim=pick(bs, "Final exit") + pick(bs, "A position the engine"),
        expected_events_per_year="about 50 Mondays a year, at most 20 entries each; E.6 research screen: 466 trips on 44 eligible Mondays (932 fills, at most 15 entries a day)",
        inputs_needed=[IN_FULL, IN_DEG, IN_GCAL],
        stages_read=[SCREEN, e12_own("k7_montrend_ret")],
        verdicts=["E.6: screen 'fail', Tier 'B' (mean -4.7260 ticks, daily t -0.441, coverage 0.9596; reports/E.6_RETURN.md Task 5 row 6)"],
        settlement_note=SETTLE + " Every decision (latest Monday 12:59) and the 14:00 final exit are before Monday's settlement; the Sunday-evening decisions fall after the prior trade date's settlement.",
        exclusion=None))
    for r in rows:
        r["bars_note"] = IN_BARS_NOTE
        r["confirmation_note"] = NO_CONF
    return rows


SOURCES = [
    "docs/prompts/STAGE_E.23.md not read (worker reads the brief only); reports/stage_e23_briefs/brief_inventory.md (all 71 lines)",
    "reports/stage_e_k7_member_freeze.json (whole file, 3,244 bytes: 6 members, legs, modules)",
    "strategy/members/k7/cp1.py, cp2.py, cp3.py, expiry.py, rev2h.py, montrend.py (module docstrings, via ast)",
    "strategy/members/k7/_event_common.py, _port_common.py, _calendar.py (module docstrings; _calendar.py literal ranges EC_CAL_COVERAGE, MBTX_MONTHS)",
    "data/calendars/crypto.py (lines 1-23 grep, 91-92, 201, 336-348 _D6_NOTE settlement period)",
    "reports/E.6_RETURN.md (grep K7; lines 180-250: Task 5 screen table, Task 6 recomputation, Task 7 reading)",
    "reports/E.7..E.22_RETURN.md, E.1, E.2a, E.2b (grep K7 / MBT / k7_ lines only)",
    "reports/E.12_RETURN.md lines 18-24, 530-540 (MBT S_X 2024-01-02, no Gate 0 row)",
    "reports/E.18_RETURN.md lines 413-417 (MBT listing 2021-05-03)",
    "reports/E.22_RETURN.md lines 18, 281 (MBT S_X 2024-01-02)",
    "reports/stage_e11_signal_coverage.md lines 1-20, 40-42, 66-68 (K7 signals in ML route v2)",
    "reports/stage_e16_overlap.md line 77; reports/stage_e10_design_target.md lines 64, 161-166 (grep K7)",
    "progress.md and docs/STAGES.md (grep K7)",
    "reports/stage_e21_briefs/lead_spec.md, multiday/constants.py, base_rules/common.py (grep settle / MBT / crypto: no MBT settlement time there)",
    "file lists: grep -l for K7 member ids under reports/ and docs/",
]

EXCLUDED = []

NOT_FINISHED = [
    "Rows of MBTX and VENDOR_DEGRADED for the W_cf window (2024-01-02..2024-02-29) were not enumerated (tables are non-literal date tuples; ranges taken from the docstrings).",
    "England-and-Wales bank-holiday range in reports/stage_e4c_release_check.json (ec_ew) not checked; marked unknown.",
    "reports/stage_e6_member_specs.md and reports/stage_e6_STATE.md were not read section by section (the frozen module docstrings were used as the rule text, as the brief directs).",
]


def main():
    rows = build()
    data = {"assignment": "K7", "rows": rows, "excluded": EXCLUDED, "sources_read": SOURCES, "not_finished": NOT_FINISHED}
    (OUT / "K7.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    md = ["# E.23 P1.1 inventory: K7 (bitcoin, MBT)", "",
          "InventoryReaderK7-OpusHigh, 2026-10-17. Extraction only; no judgment. Full fields in K7.json.", "",
          f"Rows: {len(rows)}. Excluded: {len(EXCLUDED)} (none: all six K7 members are intraday triggers on MBT; K7 has no ML member and no combination book).", "",
          "| trigger_id | module | trigger_event | decision_time_ct | side_kind | hold | events (counts) | W_ext | W_cf | stages_read | tier / verdict |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        stages = "; ".join(f"{s['stage']} {s['purpose']}" for s in r["stages_read"])
        md.append("| " + " | ".join([
            r["trigger_id"], r["module"], r["trigger_event"], r["decision_time_ct"], r["side_kind"].split(":")[0],
            r["intraday_hold"], r["expected_events_per_year"], "none (MBT not an ext2010 root; w_ext_root null)",
            "MBT S_X 2024-01-02..2024-02-29 (41 dates)", stages, r["verdicts"][0]]) + " |")
    md += ["", "## Inputs (all rows)", "",
           "- MBT bars: " + IN_BARS_NOTE + ".",
           f"- {IN_GCAL['path']}: {IN_GCAL['stated_range']} (W_ext no, W_cf yes).",
           f"- {CAL} CRYPTO_FULL_SESSIONS and VENDOR_DEGRADED: {IN_FULL['stated_range']} (rev2h, montrend, expiry; W_ext no, W_cf yes).",
           f"- {CAL} MBTX (expiry only): {IN_MBTX['stated_range']}.",
           "- E&W bank holidays for MBTX generation: reports/stage_e4c_release_check.json (ec_ew), range not checked (unknown).",
           "- No signal legs: every member reads MBT only. No release calendar is read (cp1, cp2, cp3 docstrings: 'No release instant is read').",
           "", "## Settlement", "", "- " + SETTLE, "",
           "## Confirmation", "", "- " + NO_CONF, "",
           "## Excluded", "", "- none", "",
           "## Sources read", ""] + [f"- {s}" for s in SOURCES] + ["", "## Not finished", ""] + [f"- {s}" for s in NOT_FINISHED] + [""]
    (OUT / "K7.md").write_text("\n".join(md))
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
