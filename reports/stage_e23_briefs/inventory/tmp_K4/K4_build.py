"""K4 inventory builder (InventoryReaderK4). Reads only module docstrings and the K4 freeze JSON."""
import ast, json, pathlib
ROOT = pathlib.Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = ROOT / "reports/stage_e23_briefs/inventory"
FREEZE = "reports/stage_e_k4_member_freeze.json"
fr = json.loads((ROOT / FREEZE).read_text())

def doc(mod):
    return ast.get_docstring(ast.parse((ROOT / f"strategy/members/k4/{mod}.py").read_text()))

def rule_text(mod):
    d = doc(mod)
    paras = d.split("\n\n", 1)
    return paras[1] if len(paras) > 1 else d

def verb(mod, s):
    d = doc(mod)
    flat = " ".join(d.split())
    if " ".join(s.split()) not in flat:
        raise SystemExit(f"not verbatim in {mod}: {s[:60]}")
    return s

RES = "2025-04-01..2026-06-19"
CF = {"MCL": "2021-07-12..2024-02-29", "NG": "2019-05-06..2024-02-29"}
SETTLE = ("CL and NG settle at 13:30 CT (settlement window 13:28:00-13:30:00 CT), 2010-06-07..2024-02-29, both eras "
          "graded primary: reports/stage_e16_settlement.json products.CL.settle / products.NG.settle (MCL: the repo "
          "states CL's; no separate MCL row). ")

# E.4 screen rows: trips, mean, t, screen, tier ; E.5 rows: days, trips, theta, UCB95, null verdict, labels
E4 = {
 ("cp1","MCL"):(258,"+0.7996","0.347","fail","B"), ("cp1","NG"):(257,"-1.3700","-1.011","fail","B"),
 ("cp2","MCL"):(269,"-7.5264","-1.649","fail","B"), ("cp2","NG"):(268,"-2.4909","-0.976","fail","B"),
 ("cp3","MCL"):(105,"-0.6230","-0.130","fail","B"), ("cp3","NG"):(114,"-4.4076","-1.126","fail","B"),
 ("ngpre","NG"):(50,"+3.2277","1.814","pass","A"), ("apipre","MCL"):(46,"-1.2124","-0.592","fail","B"),
 ("eiafade","MCL"):(12,"+0.2701","0.226","fail","B"), ("eiamom","MCL"):(48,"-0.5351","-1.155","fail","B"),
 ("ovr","MCL"):(275,"-1.8383","-0.500","fail","B"), ("ovr","NG"):(252,"-1.9921","-1.024","fail","B")}
E5 = {
 ("cp1","MCL"):(586,563,"null","source-overlap"), ("cp1","NG"):(1070,1024,"null","source-overlap"),
 ("cp2","MCL"):(586,585,"null","source-overlap"), ("cp2","NG"):(1070,1061,"null","source-overlap"),
 ("cp3","MCL"):(586,280,"null","source-overlap"), ("cp3","NG"):(1070,455,"null","source-overlap"),
 ("ngpre","NG"):(1070,198,"null","calendar partly unverified"), ("apipre","MCL"):(586,93,"null","source-overlap"),
 ("eiafade","MCL"):(586,55,"null","source-overlap"), ("eiamom","MCL"):(586,100,"null","source-overlap"),
 ("ovr","MCL"):(586,587,"null","source-overlap"), ("ovr","NG"):(1070,1091,"null","source-overlap")}

FEAT = {"cp1":["cp1_ret"], "cp2":["cp2_range","cp2_brk"], "cp3":["cp3_clv"], "ngpre":["k4_ngpre_mto","k4_ngpre_msince"],
        "apipre":["k4_apipre_ret"], "eiafade":["k4_eiafade_move"], "eiamom":["k4_eiamom_r3"], "ovr":["k4_ovr_ret","k4_ovr_pct"]}
E20_DROPPED = {"apipre": "k4_apipre_ret DROPPED: 'its API dropped-weeks table is undetermined for 2010-2019 (no 2010-2019 API calendar; CL reader)'",
               "eiamom": "k4_eiamom_r3 DROPPED: 'needs the NYSE-not-full-session table, which has no 2010-2019 file and is not derivable from the CME calendars (CL reader)'"}

CAL_ENERGY = {"input": "energy session/early-halt calendar (engine F, early_halt_ct, D6 O/C row 08:00/13:30)",
    "covers_w_ext": True, "covers_w_cf": True,
    "path": "W_ext: data/calendars/hist2010/energy.json; W_cf: data/calendars/energy.py (EC-CAL)",
    "stated_range": "hist2010/energy.json coverage 2010-06-01..2019-05-31 (stage_e16_settlement.json day_open note: 'hist2010/energy.json marks O UNVERIFIED for 2015-09-21..2019-05-31'); EC-CAL 2019-05-01..2026-06-19 (k4/_calendar.py docstring)"}
REL_ENGINE = {"input": "engine release calendar for D8 event cost and D9.5a fill guard: FOMC, WPSR, NGS rows",
    "covers_w_ext": True, "covers_w_cf": True,
    "path": "W_ext: reports/stage_e14_cal_releases.json (releases FOMC, NGS, WPSR only); W_cf: reports/stage_e2b_release_calendar.json",
    "stated_range": "E.14 coverage 2010-06-01..2019-05-31 (NGS 470, WPSR 470 with 1 time unverified, FOMC 72); E.2b coverage 2019-05-01..2026-06-21"}
REL_API = {"input": "engine release calendar API_WSB rows (release_products maps API_WSB to CL, MCL; not NG)",
    "covers_w_ext": False, "covers_w_cf": True,
    "path": "W_cf: reports/stage_e2b_release_calendar.json (API_WSB 372 rows 2019-05-07..2026-06-16); W_ext: not found (stage_e14_cal_releases.json holds FOMC, NGS, WPSR only; reports/stage_e20_product_summary.md: 'the 2010-2019 release calendars hold FOMC (and NG storage, WPSR) but not ... API')",
    "stated_range": "2019-05-01..2026-06-21 only"}
EFS = {"input": "ENERGY_FULL_SESSIONS (energy trade dates without early halt)",
    "covers_w_ext": True, "covers_w_cf": True,
    "path": "W_cf: strategy/members/k4/_calendar.py ENERGY_FULL_SESSIONS; W_ext: reports/stage_e14_cal_energy_full_sessions.json (derived from reports/stage_e14_cal_energy.json, same rule text)",
    "stated_range": "_calendar.py 2019-05-01..2026-06-19; E.14 file range 2010-06-01..2019-05-31, count 2250"}
WPSR = lambda which: {"input": f"WPSR release table ({which})", "covers_w_ext": True, "covers_w_cf": True,
    "path": "W_cf: strategy/members/k4/_releases.py WPSR (generated from reports/stage_e2b_release_calendar.json); W_ext: reports/stage_e14_cal_releases.json release WPSR (no frozen-module table built for 2010-2019)",
    "stated_range": "_releases.WPSR 2019-05-01..2026-06-17 (369 rows, 317 standard); E.14 WPSR 470 rows 2010-06-01..2019-05-31, 'time:unverified' 1 (WPSR-2012-11-01)"}
NGS = {"input": "NGS (EIA weekly storage) release table", "covers_w_ext": True, "covers_w_cf": True,
    "path": "W_cf: strategy/members/k4/_releases.py NGS (less DROPPED_NGS, DROPPED_NGS_CONFIRMATION); W_ext: reports/stage_e14_cal_releases.json release NGS (no frozen-module table or C9 drop check built for 2010-2019)",
    "stated_range": "_releases.NGS 367 rows, calendar 2019-05-01..2026-06-21, confirmation-window drops checked 2019-05-06..2024-02-29 (E.5: 252 releases, 5 dropped); E.14 NGS 470 rows 2010-06-01..2019-05-31, all evidence official"}
FMH = {"input": "FEDERAL_MONDAY_HOLIDAYS", "covers_w_ext": False, "covers_w_cf": True,
    "path": "W_cf: strategy/members/k4/_releases.py FEDERAL_MONDAY_HOLIDAYS (OPM, Task 1b); W_ext: not found (looked in data/calendars/hist2010/, reports/stage_e14_cal_*.json, reports/stage_e16_calendars/, grep for FEDERAL_MONDAY across repo: only the 2019-2026 table)",
    "stated_range": "2019-05-01..2026-06-19 (46 dates)"}
APIDROP = {"input": "API_DROPPED_WEEKS", "covers_w_ext": "unknown", "covers_w_cf": True,
    "path": "W_cf: strategy/members/k4/_releases.py API_DROPPED_WEEKS (empty, K4-L-04); W_ext: none; reports/stage_e20_product_summary.md: 'its API dropped-weeks table is undetermined for 2010-2019 (no 2010-2019 API calendar; CL reader)'",
    "stated_range": "2019-05..2026-06 (empty table)"}
NYSE = {"input": "NYSE_NOT_FULL (NYSE full closures and early closes)", "covers_w_ext": False, "covers_w_cf": True,
    "path": "W_cf: strategy/members/k4/_releases.py NYSE_NOT_FULL (Task 1b); W_ext: not found; reports/stage_e20_product_summary.md: 'needs the NYSE-not-full-session table, which has no 2010-2019 file and is not derivable from the CME calendars'",
    "stated_range": "2019-05-01..2026-06-19 (84 dates)"}

BASE = [CAL_ENERGY, REL_ENGINE]
INPUTS = {"cp1": BASE, "cp2": BASE, "cp3": BASE, "ngpre": BASE + [NGS], "ovr": BASE + [EFS],
          "apipre": BASE + [WPSR("standard rows, Wednesday 10:30 ET"), EFS, FMH, APIDROP],
          "eiafade": BASE + [WPSR("all rows with T_W + 15 <= 13:13 CT")],
          "eiamom": BASE + [WPSR("standard rows"), NYSE]}

SPEC = {
 "cp1": dict(event="every trade date: sign of (close of 08:29 bar - open of the 17:00 CT Globex-open first bar); zero signal no trade",
   dt="12:59 (entry bar; signal fixed at 08:29)", side="Entry: market intent on the bar at C-31 = 12:59 (fills at the 13:00 open), buy if s > 0, sell if s < 0",
   kind="momentum", kind_note="side = sign of the trade date's move from the Globex open (prior calendar day 17:00 CT) to 08:29 close",
   hold="13:00 to 13:29 CT, same trade date",
   exit="Exit: market intent on the first present bar at or after C-2 = 13:28 (fills nominally at the 13:29 open), resent while refused (S0.7, E.3-L-22).",
   epy="every trade date with nonzero signal and both signal bars present (about 250 a year)", dts="before 13:30 (12:59); the hold 13:00-13:29 ends inside the 13:28-13:30 settlement window"),
 "cp2": dict(event="first bar opening in [08:15, 13:30) whose close >= OR_high + 4 ticks or <= OR_low - 4 ticks (OR = [08:00, 08:15))",
   dt="variable: the qualifying bar, 08:15..13:29", side="Entry: the first eligible bar whose close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells; a market intent on that bar.",
   kind="momentum", kind_note="breakout direction of the trade-date price relative to the 08:00-08:15 range",
   hold="75 present bars after the entry decision bar, or F (15:08 CT) if earlier",
   exit="Exit: 75 minutes after the fill, counted as the MES module counts it (B-H1; E.3-L-07): the present bars seen while the position is non-zero, from the bar after the entry decision bar; on the 75th, a market intent closing the position (fills at the next open), resent while refused (E.3-L-22). Or the engine's forced flatten at F if earlier.",
   epy="at most one per trade date, on dates with a breakout (most trade dates)", dts="decision before 13:30 (latest 13:29); the 75-minute hold can run past the 13:30 settlement up to F 15:08"),
 "cp3": dict(event="every trade date whose prior complete day's CLV >= 0.8 or <= 0.2",
   dt="08:00 (entry bar; uses d-1's complete daily bar)", side="CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict), else no trade.",
   kind="other", kind_note="side = location of the prior complete day's 13:29 close in its 08:00-13:30 range (high: buy, low: sell); not the sign of a move",
   hold="08:01 to 13:29 CT",
   exit="Exit: market intent on the first present bar at or after C-2 = 13:28 (fills nominally at the 13:29 open), resent while refused (S0.7, E.3-L-10, E.3-L-22).",
   epy="trade dates with prior-day CLV in the top or bottom 20% of the range", dts="before 13:30 (08:00); exit fill 13:29 inside the settlement window"),
 "ngpre": dict(event="every EC-NGS storage release date in _releases.NGS",
   dt="T - 91 (07:59 for a 09:30 CT release; 09:29 for an 11:00 CT release)", side="entry: SELL, market intent on the bar at T - 91 (standard 07:59), filling at the T - 90 open (08:00)",
   kind="calendar", kind_note="always short", hold="T-90 to T+30 (standard 08:00 to 10:00 CT)",
   exit="exit: market intent on the bar at T + 29 (standard 09:59), filling at the T + 30 open (10:00); a missing exit bar: the first later present bar (S0.7)",
   epy="weekly NGS releases (about 52 a year)", dts="before 13:30"),
 "apipre": dict(event="standard WPSR Wednesdays W (Tuesday a full session, Monday not a federal holiday, not in API_DROPPED_WEEKS) with R_API != 0",
   dt="07:29 of W (entry bar; signal from W-1's 15:24 and 15:39 closes)", side="entry: market intent on the bar at 07:29 of W, side sign(R_API), filling at the 07:30 open",
   kind="momentum", kind_note="side = sign of the prior trade date W-1's 15:24-to-15:39 CT move (after W-1's settlement and F), not a move on the entry date",
   hold="07:30 to 09:29 CT on W",
   exit="exit: market intent on the bar at 09:28 of W, filling at the 09:29 open, before the 09:30 release; a missing exit bar: the first later present bar (S0.7).",
   epy="standard WPSR Wednesdays passing the filters (up to about 50 a year)", dts="before 13:30 on W (07:29); the signal bars 15:24/15:39 of W-1 are after W-1's 13:30 settlement"),
 "eiafade": dict(event="WPSR release rows with T_W + 15 <= 13:13 CT and |M| >= 0.005 (M = 14-minute post-release move)",
   dt="T_W + 14 (09:44 for the 09:30 slot; up to 12:14 for the 12:00 slot)", side="entry (K4-L-05, exact integers): BUY if 200 x (t14 - t0) <= -t0 (M <= -0.005), SELL if 200 x (t14 - t0) >= t0 (M >= +0.005), else no trade",
   kind="fade", kind_note="side = minus the sign of the T_W-1 to T_W+14 move, when |M| >= 0.5%", hold="T_W + 15 to 13:29 CT",
   exit="exit: market intent on the first present bar at or after 13:28 (C - 2), filling nominally at the 13:29 open (S0.7).",
   epy="weekly WPSR rows whose 14-minute move is at least 0.5% in size (a minority of the ~52 a year)", dts="before 13:30"),
 "eiamom": dict(event="standard WPSR Wednesdays not in NYSE_NOT_FULL, r3 != 0",
   dt="14:29 (entry bar; signal from the 09:29 and 09:59 closes)", side="entry: market intent on the bar at 14:29, side sign(r3), filling at the 14:30 open",
   kind="momentum", kind_note="side = sign of the trigger day's 09:29-to-09:59 release half-hour move", hold="14:30 to 14:59 CT",
   exit="exit: market intent on the first present bar at or after 14:58, filling nominally at the 14:59 open (S0.7), 9 minutes before F.",
   epy="standard WPSR Wednesdays on NYSE full days (about 48-50 a year)", dts="AFTER the 13:30 settlement (14:29 decision, 14:30-14:59 hold)"),
 "ovr": dict(event="each decision time t in {09:00, 10:00, 11:00, 12:00, 13:00} where r(t) <= P10 or >= P90 of the 20-day reference values",
   dt="t-1: 08:59, 09:59, 10:59, 11:59, 12:59", side="Entry: r(t) <= P10 buys, r(t) >= P90 sells; both at once (P10 = P90 = r) is no trade (K4-L-10); otherwise no trade.",
   kind="fade", kind_note="side = minus the sign of an extreme prior-hour move (bottom decile buys, top decile sells)", hold="t to t+59 (latest 13:00-13:59)",
   exit="Exit: market intent on the first present bar at or after t+58 (fills nominally at t+59), resent while refused (S0.7, E.3-L-22).",
   epy="up to 5 per trade date, non-overlapping; about 20% of decision times by construction", dts="decisions before 13:30; the 13:00 entry's hold to 13:59 crosses the 13:30 settlement"),
}

def stages(mod, root):
    e4 = E4[(mod, root)]; e5 = E5[(mod, root)]
    out = [
     {"stage": "E.4", "window_dates": RES + " (research window; 270 MCL / 269 NG trade dates after roll blackouts and UR-1)", "purpose": "screen",
      "source": "reports/E.4_RETURN.md, Task 5 'The screen per trial' table", "counts": f"trips {e4[0]}, mean {e4[1]} ticks, daily t {e4[2]}"},
     {"stage": "E.5", "window_dates": RES + " (research-window re-runs under v5/v6 for the replay and the D4 power check)", "purpose": "power",
      "source": "reports/E.5_RETURN.md Task C1 start rules / 'all 12 K4 trials sufficient'; reports/stage_e5_STATE.md rows A3 replay, C2 power", "counts": None},
     {"stage": "E.5", "window_dates": CF[root] + f" (S_{root} {CF[root][:10]})", "purpose": "confirmation",
      "source": "reports/E.5_RETURN.md Task C5 verdict table (run once 19:15:54-19:22:07)", "counts": f"days {e5[0]}, closed trips {e5[1]}"},
     {"stage": "E.5", "window_dates": "MCL 2021-07-12, NG 2019-05-06, to 2024-02-29", "purpose": "null statement",
      "source": "reports/E.5_RETURN.md 'The K4 null statement'", "counts": None},
     {"stage": "E.12", "window_dates": "2019-05..2024-02 (phase-1 training window; " + ("MCL rows on CL bars" if root=="MCL" else "NG rows") + ")",
      "purpose": "other", "source": "reports/stage_e12_gate0.md family A rows gate0A_" + "/".join(FEAT[mod]) + "_h60/h120/hF; ml_route_v2/signals/k4.py",
      "counts": "ML v2 Gate 0 family A test of the member-signal feature(s) " + ", ".join(FEAT[mod]) + " (pooled over products); all 'no'"},
     {"stage": "E.14", "window_dates": "2019-05..2024-02 (E.12 state; no new bars)", "purpose": "other",
      "source": "reports/stage_e14_c1_model.md section 3 (M1: ridge on E.12's whole training panel, 81 pairs pooled, 150 features)", "counts": "C1 M1 refit on the E.12 panel; features include the E.12-live member features"},
    ]
    if root == "NG":
        out += [
         {"stage": "E.17", "window_dates": "NG 2010-07..2019-04 (ext2010 store 2010-06-07..2019-04-30)", "purpose": "other",
          "source": "reports/E.17_RETURN.md summary (C1 STOPPED at C10); reports/E.18_RETURN.md section 6 item 3 ('C1's stopped run (C10 counts) ... read these six stores')",
          "counts": "C1 (NG ML replication) features " + ", ".join(FEAT[mod]) + " on NG rows; stopped at guard C10, no T1/T2 statistic"},
         {"stage": "E.18", "window_dates": "NG 2010-07..2019-04 (W_ext)", "purpose": "other",
          "source": "reports/E.18_RETURN.md Step 5 (C10: 'every non-exempt feature live in E.12 applies')",
          "counts": "C1b ML replication on NG; T1 814 trades / T2 627; FAIL"}]
    if mod in E20_DROPPED:
        out.append({"stage": "E.20", "window_dates": "2019-05..2024-02 (17 roots)", "purpose": "other",
                    "source": "reports/stage_e20_product_summary.md DROPPED table", "counts": "not read: " + E20_DROPPED[mod]})
    else:
        out.append({"stage": "E.20", "window_dates": "2019-05..2024-02 (S_X 2019-05-06; 17 roots incl. CL, NG); backward 2010-2019 stores not read (no backward test)",
                    "purpose": "other", "source": "reports/stage_e20_product_summary.md KEPT list; reports/E.20_RETURN.md summary ('Search screen: FAIL')",
                    "counts": "ML search features " + ", ".join(FEAT[mod]) + " kept"})
    return out

def verdicts(mod, root):
    e4 = E4[(mod, root)]; e5 = E5[(mod, root)]
    v = [f"E.4 screen: {e4[3]}, Tier {e4[4]} (reports/E.4_RETURN.md Task 5 table)",
         f"E.5 null verdict: {e5[2]}; labels: {e5[3]} (reports/E.5_RETURN.md Task C5 table)",
         "E.5 K4 statement: 'null' (reports/E.5_RETURN.md summary table)"]
    if mod == "ngpre":
        v.append("E.5 Holm (K = 9): 'p 0.5375, no'; chain 'no edge' (reports/E.5_RETURN.md summary table)")
    v.append("E.12 Gate 0: FAIL (reports/E.12_RETURN.md line 1)")
    if root == "NG":
        v += ["E.17 C1: STOPPED (C10) (reports/E.17_RETURN.md)", "E.18 C1b-T1, C1b-T2: FAIL (reports/E.18_RETURN.md)"]
    if mod not in E20_DROPPED:
        v.append("E.20 search screen: FAIL (reports/E.20_RETURN.md)")
    return v

rows = []
for m in fr["members"]:
    mod = m["module"].split(".")[-1]; root = m["legs"][0]["root"]; s = SPEC[mod]
    verb(mod, s["side"]); verb(mod, s["exit"])
    label = m["label"]
    rows.append({
     "trigger_id": label, "cluster_or_stage": "K4 (Stage E.4 screen, E.5 confirmation)", "member_id": label.split(" ")[0],
     "module": m["module"].replace(".", "/") + ".py", "freeze_file": FREEZE, "traded_root": root,
     "vehicle": f"{root} (q_c {'4' if root=='MCL' else '1'})", "w_ext_root": "CL" if root == "MCL" else "NG",
     "signal_legs": [], "definition_verbatim": rule_text(mod), "trigger_event": s["event"],
     "decision_time_ct": s["dt"], "side_rule": s["side"], "side_kind": s["kind"], "side_kind_note": s["kind_note"],
     "intraday_hold": s["hold"], "exit_rule_verbatim": s["exit"],
     "expected_events_per_year": s["epy"] + f"; counts reported: E.4 research {E4[(mod,root)][0]} trips; E.5 confirmation {E5[(mod,root)][1]} closed trips over {E5[(mod,root)][0]} days",
     "inputs_needed": INPUTS[mod] + ([REL_API] if root == "MCL" else []), "stages_read": stages(mod, root), "tier": E4[(mod, root)][4],
     "verdicts": verdicts(mod, root), "settlement_note": SETTLE + "Decision vs settlement: " + s["dts"] + ".",
     "exclusion": None})
data = {"assignment": "K4", "rows": rows, "excluded": [],
 "notes": ["K4 freeze lists 12 members (8 rules); every one is a single-leg intraday trigger; no ML model member, no combination book in K4.",
           "MCL rows' W_ext equivalent is CL (ext2010h store 2010-07-01..2019-04-30); NG's is NG (ext2010 store 2010-06-07..2019-04-30); both step2 stores 2019-05-06..2024-02-29 (reports/stage_e17_run_manifest.json stores.CL/NG).",
           "ENERGY_FULL_SESSIONS, the frozen K4 tables (WPSR, NGS, FEDERAL_MONDAY_HOLIDAYS, NYSE_NOT_FULL, API_DROPPED_WEEKS) cover 2019-05..2026-06 only; a W_ext run needs 2010-2019 equivalents built: E.14 calendars give WPSR/NGS/FOMC and energy full sessions; federal Monday holidays, NYSE not-full days, API weeks and API_WSB release rows were not found for 2010-2019.",
           "E.9 return 7(d): K4's frozen tables keep 2024-07-03 (outside W_ext and W_cf)."],
 "sources_read": [
  "reports/stage_e23_briefs/brief_inventory.md (whole)", FREEZE + " (members, members_dir)",
  "strategy/members/k4/{cp1,cp2,cp3,ngpre,apipre,eiafade,eiamom,ovr}.py (module docstrings)",
  "strategy/members/k4/_releases.py (docstring, window constants, drop lists)", "strategy/members/k4/_calendar.py (docstring)",
  "reports/E.4_RETURN.md (K4 lines; Task 5 screen table; Task 7)", "reports/E.5_RETURN.md (summary table; Tasks C1, C5; null statement)",
  "reports/stage_e5_STATE.md (K4 rows)", "reports/stage_e4_member_specs.md (section headings; F 15:08 line 19, 28)",
  "reports/E.{1,2a,2b,4b,4c,6,7,8,9,11..22}_RETURN.md (grep K4/k4_ lines)", "docs/STAGES.md (E.4-E.20 entries)",
  "reports/E.9_RETURN.md 7(d)", "reports/E.12_RETURN.md (summary; ranking rows)", "reports/stage_e12_gate0.md (gate0A_ cp*/k4_* rows)",
  "docs/STAGE_E_ML_V2_DESIGN.md V2.2b", "ml_route_v2/signals/k4.py (docstring)", "reports/stage_e14_c1_model.md (sections 1-3)",
  "reports/E.14_RETURN.md Task 5", "reports/E.17_RETURN.md (summary, Part 1/2 lines)", "reports/E.18_RETURN.md (Steps 3-5, section 6)",
  "reports/E.20_RETURN.md (section 6 item 3, summary)", "reports/stage_e20_product_summary.md (KEPT/DROPPED, feature table)",
  "reports/stage_e14_cal_releases.json (schema, coverage, counts, release names)", "reports/stage_e14_cal_energy_full_sessions.json (rule, range, count)",
  "data/calendars/hist2010/energy.json (coverage, counts)", "reports/stage_e2b_release_calendar.json (coverage, release_products, per-release date ranges)",
  "reports/stage_e16_settlement.json (window; products.CL/NG settle, day_open)", "base_rules/constants.py (SETTLEMENT_PATH)",
  "reports/stage_e17_run_manifest.json (stores.CL, stores.NG paths only)"],
 "not_finished": []}
(OUT / "K4.json").write_text(json.dumps(data, indent=1))

def cell(x): return str(x).replace("|", "/").replace("\n", " ")
L = ["# Stage E.23 P1.1 inventory: K4 (InventoryReaderK4-OpusHigh)", "",
     f"Rows: {len(rows)} (12 triggers, 8 rules). Excluded: 0. Freeze: {FREEZE}. Full fields in K4.json.", "",
     "| Trigger | Module | Root (W_ext) | Event | Decision CT | Side kind | Hold | Tier | E.4 / E.5 | Inputs not covering W_ext |",
     "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    miss = [i["input"].split(" (")[0] + ("?" if i["covers_w_ext"] == "unknown" else "") for i in r["inputs_needed"] if i["covers_w_ext"] is not True]
    mod = r["module"].split("/")[-1][:-3]
    e4 = E4[(mod, r["traded_root"])]; e5 = E5[(mod, r["traded_root"])]
    L.append("| " + " | ".join(cell(x) for x in [r["trigger_id"], r["module"], f"{r['traded_root']} ({r['w_ext_root']})", r["trigger_event"],
             r["decision_time_ct"], r["side_kind"], r["intraday_hold"], r["tier"], f"{e4[3]} {e4[0]} trips / {e5[2]} {e5[1]} trips",
             ", ".join(miss) or "none"]) + " |")
L += ["", "Stages read (every row): E.4 screen and E.5 power on the research window 2025-04-01..2026-06-19; E.5 confirmation and",
      "null statement on MCL 2021-07-12 / NG 2019-05-06 ..2024-02-29; E.12 Gate 0 and E.14 M1 refit (ML features) on 2019-05..2024-02.",
      "NG rows also: E.17 C1 (stopped at C10) and E.18 C1b (FAIL) on NG 2010-07..2019-04 (W_ext) via the ML features.",
      "E.20 ML search on 2019-05..2024-02 used cp1_ret, cp2_*, cp3_clv, k4_eiafade_move, k4_ngpre_*, k4_ovr_*; it dropped k4_apipre_ret and",
      "k4_eiamom_r3 (no 2010-2019 API / NYSE tables). No K4 member rule was run on W_ext bars.", "",
      "Settlement: CL and NG 13:30 CT (window 13:28:00-13:30:00), reports/stage_e16_settlement.json. Only eiamom decides after it (14:29).", "",
      "Excluded: none (no ML model member or combination book in K4).", "", "## Notes"] + ["- " + n for n in data["notes"]] + \
     ["", "## Sources read"] + ["- " + s for s in data["sources_read"]]
(OUT / "K4.md").write_text("\n".join(L) + "\n")
print("rows", len(rows))
