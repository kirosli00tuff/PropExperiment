"""CDE inventory builder (Stage E.23 P1.1, InventoryReaderCDE). Reads code, freezes, preregs and
report JSON fields only; never opens a bar store. Writes inventory/CDE.json and inventory/CDE.md.
Every *_verbatim field is cut from its source file and asserted to occur there."""
import ast
import json
import re
from pathlib import Path

ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = ROOT / "reports/stage_e23_briefs/inventory"
SOURCES = []


def src(path, section):
    SOURCES.append({"path": path, "section": section})


def doc(path):
    return ast.get_docstring(ast.parse((ROOT / path).read_text())) or ""


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def cut(text, start, end=None):
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j].strip()


def check(snippet, text, where):
    if norm(snippet) not in norm(text):
        raise AssertionError(f"not verbatim in {where}: {snippet[:80]}")
    return snippet


def consts(path):
    s = (ROOT / path).read_text()
    out = []
    for n in ast.parse(s).body:
        if isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id.isupper() and not t.id.startswith("_") for t in n.targets):
            seg = ast.get_source_segment(s, n)
            if seg and len(seg) < 160:
                out.append(norm(seg))
    return out


def line_starting(path, prefix):
    for ln in (ROOT / path).read_text().splitlines():
        if ln.startswith(prefix):
            return ln
    raise AssertionError(f"{prefix} not in {path}")


# ------------------------------------------------------------------ shared facts
CL_LIST = "reports/stage_d1f_confirmation_list.md"
RUN_TABLES = "reports/stage_d1f_run_tables.json"
t1 = {r["id"]: r for r in json.loads((ROOT / RUN_TABLES).read_text())["t1_tier_a"]}
acc_d1d = {r["label"]: r for r in json.loads((ROOT / "reports/stage_d1d_accounting.json").read_text())["runs"]}
acc_d1 = json.loads((ROOT / "reports/stage_d1_accounting.json").read_text())
d1_labels = set(acc_d1["accounting"]["per_trial"].keys())
reg_d1a = json.loads((ROOT / "reports/stage_d1a_regression.json").read_text())
d1a_windows = {}
for r in reg_d1a["runs"]:
    d1a_windows.setdefault(r["label"], set()).add((r["window"], r.get("first_date"), r.get("last_date")))
ffacts = {r["id"]: r for r in json.loads((ROOT / "reports/stage_d1b_family_f_facts.json").read_text())["tested_statistics"]}
gfacts = {r["id"]: r for r in json.loads((ROOT / "reports/stage_d1d_family_g_facts.json").read_text())["tested_statistics"]}
retests = json.loads((ROOT / "reports/stage_d1d_retests.json").read_text())
src(CL_LIST, "1.1-1.4 data and windows; 2.1 A1/A2/A3 Tier A tables and Family H mechanics; 2.2 Tier B; 2.3 classes")
src(RUN_TABLES, "t1_tier_a fields id, n_days, n_activity, holm_reject, composite, status, labels (theta values not copied)")
src("reports/stage_d1f_run_tables.md", "T1 header, T4 Holm line (rejected [])")
src("reports/stage_d1d_accounting.json", "runs[].label/verdict/robust/drift_verdict/n_trips (train_union, 31 trials)")
src("reports/stage_d1_accounting.json", "windows (fold0_train, train_union), per_trial labels")
src("reports/stage_d1a_regression.json", "runs[].label/window/first_date/last_date")
src("reports/stage_d1b_accounting.json", "window, n_trials_cumulative 24")
src("reports/stage_d1b_ch4_fold0.json", "label, window")
src("reports/stage_d1d_retests.json", "meta.windows")
src("reports/stage_d1b_family_f_declaration.md", "0 data discipline; 1 F1-F6 declared features")
src("reports/stage_d1b_family_f_facts.json", "meta.eda_date_range, n_eda_dates_after_exclusions; tested_statistics id/n/bh_reject")
src("reports/stage_d1d_timeframe_declaration.md", "2 re-tests table RT1-RT7; 3 Family G definitions and table")
src("reports/stage_d1d_family_g_facts.json", "tested_statistics id/n_events/eligible/bh_reject/selection")
src("reports/stage_d1e_members_trials.json", "window (289 train-union dates)")
src("reports/stage_d1e_members_events.json", "meta.eda_dates (139 EDA dates)")
src("reports/stage_d1e_power.md", "line 25 (ranges end 2024-02-29; holdout-2 239 dates)")
src("docs/STAGES.md", "Stage C, D.1..D.1g, E.13..E.18 lines 17-60 and 131-163")
src("progress.md", "2026-09-23 Stage D.1f (run) header and guardrail table (lines 2092-2130); D.1e line 'Seven classes, 101 members: 95 measured and 6 projected'")
src("reports/E.2b_RETURN.md", "section 3, 'MES regressions (bit for bit)' table lines 141-149")

D1F_CONF = {"stage": "D.1f", "window_dates": "2020-02-03..2024-02-29 (S = 2020-02-03 by the start rule, 1,055 window days; MES.v.0 ohlcv-1m bought 2019-05..2025-03 in D.1f; holdout-2 2024-04-01..2025-03-31 and the March 2024 embargo sealed, not read)",
            "purpose": "confirmation", "source": "reports/stage_d1f_confirmation_list.md 1.3 and 2.1; reports/stage_d1f_run_tables.md T1; progress.md 2026-09-23 Stage D.1f (run)"}
D1F_CONT = {"stage": "D.1f", "window_dates": "2025-04-01..2026-05-13 (train union, continuity rerun to the cent; research window)", "purpose": "other",
            "source": "reports/stage_d1f_confirmation_list.md 1.4 (continuity); progress.md D.1f run 'continuity 33/33'"}
D1E_TRIAL = {"stage": "D.1e", "window_dates": "2025-04-01..2026-05-13 (289 train-union dates; research window)", "purpose": "power",
             "source": "reports/stage_d1e_members_trials.json window; reports/stage_d1e_power.md"}
D1E_EVENT = {"stage": "D.1e", "window_dates": "139 EDA dates 2025-10-17..2026-05-13 (research window)", "purpose": "power",
             "source": "reports/stage_d1e_members_events.json meta.eda_dates; reports/stage_d1e_power.md"}

MES_SETTLE = ("The repo's settlement table (reports/stage_e16_settlement.json; reports/stage_e16_prereg_common.md section 5) has no MES or ES row. "
              "Its equity-index rows (NQ, YM, RTY) state S_p 15:15 CT to 2020-10-25 and 15:00 CT from 2020-10-26. "
              "MES's D.1f confirmation window 2020-02-03..2024-02-29 spans that change. Whether decision_time_ct is before it: see decision_time_ct (by clock).")


def mes_inputs(extra=None):
    base = [{"input": "MES 1-minute bars (MES.v.0)", "covers_w_ext": False, "covers_w_cf": True,
             "path": "MES confirmation-window bars built by D.1f (reports/stage_d1f_confirmation_build.json); not opened",
             "stated_range": "W_ext: MES is not one of the 17 ext2010/ext2010h roots and maps to no full-size W_ext root (ES not owned before 2019-05). W_cf: D.1f confirmation window 2020-02-03..2024-02-29 (MES bars bought 2019-05..2025-03; 2024-03..2025-03 sealed as holdout-2/embargo)"}]
    return base + (extra or [])


def tier_a_verdict(tid):
    r = t1[tid]
    return {"D.1f": f"composite {r['composite']}; Holm reject {r['holm_reject']}; status {r['status']}" + (f"; labels {r['labels']}" if r["labels"] else ""),
            "D.1f_ref": "reports/stage_d1f_run_tables.md T1 (Holm m = 58, rejected [])"}


def d1f_count(tid):
    r = t1[tid]
    return f"D.1f n_activity {r['n_activity']} over n_days {r['n_days']} (count; reports/stage_d1f_run_tables.json t1_tier_a)"


# ------------------------------------------------------------------ the 31 trials (A1)
T = []  # list of spec dicts


def trial(**kw):
    T.append(kw)


A = "strategy/research/a_session_clock/"
B = "strategy/research/b_reference_breakout/"
C = "strategy/research/c_short_horizon_reversal/"
D = "strategy/research/d_volatility_state/"
E = "strategy/research/e_calendar_event/"
G = "strategy/research/g_timeframe/retests.py"

trial(id="A-H1 european-open overnight drift", module=A + "h1_european_open_overnight_drift.py", cls="C1",
      parts=[("Formalization:", "SUPPORT CONDITION")],
      side=("Flat\nbefore the window; at the first bar whose decision time falls in\n[02:00, 03:00) ET, if flat and not already traded today, buy QUANTITY_MICROS."),
      exit_=("Exit unconditionally at the first bar whose decision time reaches 03:00 ET"),
      kind="calendar", event="every trade date, at the 02:00 ET (01:00 CT) clock window", dt="01:00 CT (first bar with decision time in [02:00, 03:00) ET); exit at 02:00 CT",
      hold="about 60 minutes (01:00-02:00 CT, inside the ETH session)", epy="every trade date (about 250 a year; at most one round trip a day)")
trial(id="A-H2 rth close window (buy)", module=A + "h2_rth_close_window_session_position.py", cls="C1",
      parts=[("Formalization:", "SUPPORT CONDITION")],
      side="once per trade date, at the first bar whose decision time\nenters [15:30, 16:00) ET, if flat and not already traded today, enter\nQUANTITY_MICROS in ``direction``.",
      exit_="Exit unconditionally at the first bar\nwhose decision time reaches 16:00 ET.", kind="calendar", event="every trade date, 15:30 ET (14:30 CT); direction=\"buy\"",
      dt="14:30 CT; exit 15:00 CT", hold="30 minutes (14:30-15:00 CT)", epy="every trade date (about 250 a year)")
trial(id="A-H2 rth close window (sell)", module=A + "h2_rth_close_window_session_position.py", cls="C1",
      parts=[("Formalization:", "SUPPORT CONDITION")],
      side="once per trade date, at the first bar whose decision time\nenters [15:30, 16:00) ET, if flat and not already traded today, enter\nQUANTITY_MICROS in ``direction``.",
      exit_="Exit unconditionally at the first bar\nwhose decision time reaches 16:00 ET.", kind="calendar", event="every trade date, 15:30 ET (14:30 CT); direction=\"sell\"",
      dt="14:30 CT; exit 15:00 CT", hold="30 minutes (14:30-15:00 CT)", epy="every trade date (about 250 a year)")
trial(id="A-H3 weekend effect", module=A + "h3_weekend_effect.py", cls="C1", parts=[("Formalization:", "SUPPORT CONDITION")],
      side="at the first RTH bar (09:30 ET) on a Monday, if flat, SELL\nQUANTITY_MICROS; on a Friday, if flat, BUY QUANTITY_MICROS.",
      exit_="Exit unconditionally at the first\nbar whose decision time reaches 16:00 ET (RTH close).", kind="calendar", event="Monday and Friday trade dates (weekday of bar.trade_date)",
      dt="08:30 CT (09:30 ET); exit 15:00 CT", hold="about 6.5 hours (08:30-15:00 CT)", epy="about 100 a year (Mondays and Fridays)")
trial(id="A-H4 eth leg", module=A + "h4_eth_vs_rth_decomposition.py", cls="C1", parts=[("Formalization:", "SUPPORT CONDITION")],
      side="for ``session=\"eth\"``, enter long at the FIRST bar of a new\ntrade date (the session's own open)",
      exit_="exit unconditionally at the first bar\nwhose decision time enters RTH (09:30 ET).", kind="calendar", event="every trade date, at the session open",
      dt="first bar of the trade date (about 17:00 CT the prior calendar evening); exit 08:30 CT", hold="about 15.5 hours (ETH, 17:00 CT prior evening to 08:30 CT)", epy="every trade date (about 250 a year)")
trial(id="A-H4 rth leg", module=A + "h4_eth_vs_rth_decomposition.py", cls="C1", parts=[("Formalization:", "SUPPORT CONDITION")],
      side="For ``session=\"rth\"``, enter long\nat the first bar whose decision time enters RTH (09:30 ET)",
      exit_="exit\nunconditionally at the first bar whose decision time reaches RTH close\n(16:00 ET).", kind="calendar", event="every trade date, at 09:30 ET",
      dt="08:30 CT; exit 15:00 CT", hold="about 6.5 hours (08:30-15:00 CT)", epy="every trade date (about 250 a year)")

for hold in (5, 75):
    trial(id=f"B-H1 opening-range breakout (hold {hold})", module=B + "h1_friction_aware_opening_range_breakout.py", cls="C2",
          parts=[("Mechanism:", "Rationale"), ("Fixed (not gridded) parameters", None)],
          side="enter one unit in the\nbreakout direction (long above the range high, short below the range low).",
          exit_="Hold for a fixed, pre-registered horizon, then exit unconditionally.", kind="momentum",
          event="first bar after the 08:30-08:45 CT opening range whose close is beyond the range high/low by at least 4 ticks",
          dt="variable: the first close-through bar, from the 08:45 CT bar on (entries bounded by the engine's 15:08 CT no-new-positions time)",
          hold=f"{hold} minutes (hold_minutes={hold})", epy="at most one a day, on days with a close-through")
trial(id="B-H2 prior-day stop cascade", module=B + "h2_prior_day_stop_cascade.py", cls="C2",
      parts=[("Mechanism:", "Rationale"), ("Fixed (not gridded) parameters", None)],
      side="enter one unit in the breakout direction.",
      exit_="Exit at\nthe first of:\n  (a) ``MAX_HOLD_MINUTES`` bars since entry (a short, fixed cap -- this\n      strategy targets the burst itself, not a sustained trend), or\n  (b) a volume-decay signal: ``DECAY_LOOKBACK`` consecutive bars whose\n      volume is below ``DECAY_VOLUME_RATIO`` of the entry bar's volume,\n      read as the post-trigger liquidity burst fading.",
      kind="momentum", event="first RTH bar whose close trades through the prior completed session's high or low by at least 4 ticks",
      dt="variable: the first RTH close-through bar (08:30 CT on)", hold="at most 15 minutes (volume-decay exit can end it sooner)", epy="at most one a day")
trial(id="B-H3 breakout leg", module=B + "h3_breakout_vs_fade_horse_race.py", cls="C2",
      parts=[("Mechanism:", "Rationale:"), ("Fixed (not gridded) parameters", None)],
      side="``H3BreakoutLeg``: enter in the breakout direction (continuation).", exit_="Both hold a fixed ``hold_minutes`` and exit unconditionally.",
      kind="momentum", event="first bar after the 08:30-09:00 CT opening range whose close is beyond the range by at least 4 ticks",
      dt="variable: the first close-through bar, from the 09:00 CT bar on", hold="30 minutes", epy="at most one a day")
trial(id="B-H3 fade leg", module=B + "h3_breakout_vs_fade_horse_race.py", cls="C2",
      parts=[("Mechanism:", "Rationale:"), ("Fixed (not gridded) parameters", None)],
      side="``H3FadeLeg``: enter AGAINST the breakout direction (reversal back into\n    the range) at the same bar and price.", exit_="Both hold a fixed ``hold_minutes`` and exit unconditionally.",
      kind="fade", event="first bar after the 08:30-09:00 CT opening range whose close is beyond the range by at least 4 ticks",
      dt="variable: the first close-through bar, from the 09:00 CT bar on", hold="30 minutes", epy="at most one a day")
trial(id="B-H4 narrow-range breakout", module=B + "h4_narrow_range_contraction_breakout.py", cls="C2",
      parts=[("Mechanism:", "Rationale"), ("Fixed (not gridded) parameters", None)],
      side="Only take the breakout signal -- otherwise identical to H1's\ntrigger and exit -- if today's OR width sits at or below the\n``CONTRACTION_PERCENTILE`` of that trailing baseline (an unusually narrow\nrange).",
      exit_="HOLD_MINUTES = 30           (fixed exit; one setting, not searched)", kind="momentum",
      event="OR15 (08:30-08:45 CT) width at or below the 40th percentile of the last 20 sessions' OR widths, then the first close-through by 4 ticks",
      dt="variable: the first close-through bar, from the 08:45 CT bar on", hold="30 minutes", epy="at most one a day, on narrow-OR days")
trial(id="C-H1 magnitude-conditioned reversal", module=C + "h1_magnitude_conditioned_reversal.py", cls="C3",
      parts=[("Concretely:", "SUPPORT CONDITION")],
      side="enter opposite the\n   sign of r_t: sell after a positive return, buy after a negative one.",
      exit_="Hold exactly K_MINUTES bars, then exit unconditionally (flat market exit).", kind="fade",
      event="any bar whose trailing 5-minute return magnitude ranks in [0.20, 0.60] of the last 120 absolute returns, when flat",
      dt="variable: any bar close in the session", hold="5 minutes", epy="many per day (any flat bar can fire)")
trial(id="C-H2 post-spike exhaustion fade", module=C + "h2_post_spike_exhaustion_fade.py", cls="C3",
      parts=[("1. Maintain rolling", "ENTRY-TIMING LIMITATION"), ("Parameters (ONE setting", "SUPPORT CONDITION")],
      side="fade its direction: sell if the\n   trigger bar closed above its open (an up bar), buy if it closed below its\n   open (a down bar).",
      exit_="Hold for HOLD_BARS bars after the fill, then exit unconditionally.", kind="fade",
      event="a 1-minute bar with volume z > 3.0 or range ratio > 3.0 against the trailing 60 bars", dt="variable: any spike bar close", hold="2 bars (2 minutes)", epy="many per day")
trial(id="C-H3 close-location-value reversal", module=C + "h3_close_location_value_reversal.py", cls="C3",
      parts=[("1. CLV_t", "This is deliberately"), ("Parameters (ONE setting", "SUPPORT CONDITION")],
      side="fade the extreme: sell if\n   CLV_t >= CLV_THRESHOLD (close pinned to the high -- one-sided buying\n   exhausted), buy if CLV_t <= -CLV_THRESHOLD (close pinned to the low).",
      exit_="Hold for HOLD_BARS bars after the fill, then exit unconditionally.", kind="fade",
      event="a 1-minute bar with |CLV| >= 0.80 and range > 1.5x its trailing 60-bar mean", dt="variable: any trigger bar close", hold="3 bars (3 minutes)", epy="many per day")
trial(id="C-H4 passive-fill reversal", module=C + "h4_passive_fill_reversal.py", cls="C6",
      parts=[("Mechanics, exactly as specified", "SUPPORT CONDITION")],
      side="If the percentile lands\n   in [BAND_LOW, BAND_HIGH], fade: sell after a positive return, buy after a\n   negative one.",
      exit_="EXIT is passive first, then a market fallback.", kind="fade", event="C-H1's signal, entered with a resting limit 1 tick off the signal bar's close (TTL 5 bars)",
      dt="variable: any bar close in the session", hold="5 bars after the fill, then a passive exit (TTL 5) with market fallback", epy="many per day")
trial(id="D-H1 trailing-vol regime gate", module=D + "h1_trailing_volatility_regime_gate.py", cls="C4",
      parts=[("State construction", None)],
      side="on a day classified \"low,\" go long 1 micro at bar offset\nENTRY_BAR_OFFSET counted from that trade date's first bar in the on-disk\nseries",
      exit_="hold HOLD_MINUTES bars,\nthen flatten unconditionally.", kind="calendar",
      event="trade dates whose trailing EWMA vol (snapshotted before the date's first bar) ranks in the bottom tercile of the last 60 snapshots",
      dt="the trade date's bar index 60 (about 18:00 CT the prior calendar evening when the session has no missing minutes); the gate uses bars strictly before the trade date",
      hold="30 one-minute bars", epy="about one third of trade dates (low-vol tercile)")
trial(id="D-H2 inverse-vol sizing", module=D + "h2_inverse_volatility_sizing.py", cls="C4",
      parts=[("Base entry", None)],
      side="go long at a\nfixed bar offset ENTRY_BAR_OFFSET from each trade date's first bar in the\non-disk series, every trade date (no filter)",
      exit_="hold HOLD_MINUTES bars, then\nflatten unconditionally.", kind="calendar", event="every trade date; size 1-5 micros by inverse EWMA vol",
      dt="the trade date's bar index 60 (about 18:00 CT the prior calendar evening)", hold="30 one-minute bars", epy="every trade date")
trial(id="D-H3 range-compression gate", module=D + "h3_range_compression_gate.py", cls="C4",
      parts=[("State construction", None)],
      side="if flat AND the current bar is compressed, and\nbar.close > max(high) over the trailing BREAKOUT_LOOKBACK bars BEFORE this\none, go long; if bar.close < min(low) over that same trailing window, go\nshort.",
      exit_="Hold HOLD_MINUTES bars,\nthen flatten unconditionally", kind="momentum",
      event="a bar whose trailing 20-bar range is below the 20th percentile of the last 250, closing beyond the prior 20-bar high/low",
      dt="variable: any bar close (no trade-date reset)", hold="15 minutes", epy="many per day")
trial(id="D-H4 overnight gap fade", module=D + "h4_overnight_gap_fade.py", cls="C4",
      parts=[("State construction", None)],
      side="on a small-to-moderate gap day, at\nthat trade date's first bar's decision time, go opposite the gap's sign\n(sell after an up-gap, buy after a down-gap)",
      exit_="hold\nHOLD_MINUTES bars, then flatten unconditionally.", kind="fade",
      event="trade dates whose |gap| (first bar open vs prior trade date's last close) ranks in [0.20, 0.80] of the last 60",
      dt="the trade date's first bar (about 17:00 CT the prior calendar evening, the Globex reopen)", hold="30 minutes", epy="about 60% of trade dates (band 0.20-0.80)")
trial(id="E-H1 scheduled macro drift", module=E + "h1_scheduled_macro_drift.py", cls="C5",
      parts=[("Mechanism:", "This directly targets"), ("Because FOMC's 2:00pm ET", "This is recorded as a designed adaptation")],
      side="go long once\nat the very start of that trade date's session",
      exit_="hold through to just before the release, then flatten.", kind="calendar",
      event="trade dates carrying a scheduled FOMC statement (14:00 ET) or CPI/NFP release (08:30 ET), from the release table",
      dt="first bar of the release trade date (about 17:00 CT the prior calendar evening); exit at the release (07:30 CT CPI/NFP, 13:00 CT FOMC)",
      hold="about 14.5 to 20 hours (overnight session into the release)", epy="about 32 a year (8 FOMC + 12 CPI + 12 NFP, one per date after collisions are dropped)")
trial(id="E-H2 post-release momentum", module=E + "h2_post_release_momentum.py", cls="C5",
      parts=[("Mechanism:", "Source citation:"), ("Parameters (ONE setting", None)],
      side="enter in the\ndirection of the reaction window's net return",
      exit_="hold for HOLD_MINUTES bars, then exit\nunconditionally.", kind="momentum",
      event="release minute (CPI/NFP 08:30 ET, FOMC 14:00 ET) whose 5-minute reaction-window range exceeds 2.0x the baseline-scaled range",
      dt="end of the 5-minute reaction window after the release (about 07:35 CT CPI/NFP, 13:05 CT FOMC)", hold="10 minutes", epy="at most about 32 a year (release dates with range expansion)")
trial(id="E-H3 quarterly witching short", module=E + "h3_quarterly_witching.py", cls="C5",
      parts=[("Mechanism:", "LOWEST DATA-RISK"), ("Parameters (ONE setting", None)],
      side="on the quarterly witching Friday (3rd Friday of March / June /\nSeptember / December), short MES for the last LAST_MINUTES_BEFORE_CLOSE of\nthe regular session",
      exit_="hold LAST_MINUTES_BEFORE_CLOSE minutes, then flatten.", kind="calendar", event="3rd Friday of Mar/Jun/Sep/Dec",
      dt="14:30 CT; exit 15:00 CT", hold="30 minutes", epy="4 a year")
trial(id="E-H4 turn-of-month long", module=E + "h4_turn_of_month.py", cls="C5",
      parts=[("Mechanism:", "HARNESS-COMPATIBILITY"), ("Parameters (ONE setting", None)],
      side="go long once at the start of each session that is EITHER the last\ntrading day of its calendar month OR one of the first TOM_FOLLOWING_DAYS\ntrading days of the following month",
      exit_="holding to a fixed self-managed exit\nlate in that same session", kind="calendar", event="last trading day of a month and the first 3 trading days of the next",
      dt="first bar of the trade date (about 17:00 CT the prior calendar evening); exit 15:00 CT", hold="about 22 hours (whole trade-date session to 15:00 CT)", epy="about 48 a year (4 per month)")

RT = {
    "RT1 B-H1 ORB 5-min bars (hold 1 bar)": ("**RT1**", "momentum", "first RTH 5-min bar at slot >= 6 (09:00 CT on) closing >= OR high + 4 ticks or <= OR low - 4 ticks; OR = 08:30-09:00 CT", "variable: completion of the first close-through 5-min bar, 09:00 CT on", "1 five-minute bar"),
    "RT2 B-H1 ORB 5-min bars (hold 15 bars)": ("**RT2**", "momentum", "as RT1", "variable: as RT1", "15 five-minute bars (75 minutes), earlier if the RTH segment ends"),
    "RT3 B-H3 breakout leg 5-min bars": ("**RT3**", "momentum", "as RT1 (OR 08:30-09:00 CT, +/- 4 ticks)", "variable: as RT1", "6 five-minute bars (30 minutes)"),
    "RT4 B-H3 fade leg 5-min bars": ("**RT4**", "fade", "as RT3", "variable: as RT1", "6 five-minute bars (30 minutes)"),
    "RT5 C-H2 spike fade 5-min bars": ("**RT5**", "fade", "a 5-min bar with volume z > 3.0 or range ratio > 3.0 against the trade date's previous 20 coarse bars", "variable: any 5-min bar completion (ETH or RTH)", "1 five-minute bar"),
    "RT6 D-H1 daily-vol regime gate": ("**RT6**", "calendar", "trade dates whose daily-observation EWMA vol V_d ranks in the bottom tercile of the trailing 60", "the trade date's 1-minute bar index 60 (about 18:00 CT the prior calendar evening)", "30 one-minute bars"),
    "RT7 D-H2 daily-vol sizing": ("**RT7**", "calendar", "every trade date; size 1-5 by daily V_d", "the trade date's 1-minute bar index 60", "30 one-minute bars"),
}
RT_SIDE = {"momentum": "Enter in the break direction.", "fade": "entering **against** the break direction."}

DECL_G = "reports/stage_d1d_timeframe_declaration.md"
DECL_F = "reports/stage_d1b_family_f_declaration.md"
ftext = (ROOT / DECL_F).read_text()
gtext = (ROOT / DECL_G).read_text()
cltext = (ROOT / CL_LIST).read_text()

rows = []


def common_row(tid, cls):
    return {"trigger_id": tid, "cluster_or_stage": f"Stage D (D.1f Tier A, class {cls})", "member_id": tid, "freeze_file": "reports/stage_d1f_harness_freeze.json (manifest d3bd21e5...; list reports/stage_d1f_confirmation_list.md, list sha256 c19cbac1...)",
            "traded_root": "MES", "vehicle": "MES", "w_ext_root": None, "signal_legs": [], "tier": "A (D.1f Tier A, Holm family m = 58)", "settlement_note": MES_SETTLE, "exclusion": None}


for s in T:
    d = doc(s["module"])
    pieces = [cut(d, a, b) for a, b in s["parts"]]
    defin = "\n...\n".join(pieces)
    cst = consts(s["module"])
    src(s["module"], "module docstring (" + "; ".join(f"from '{a}'" + (f" to '{b}'" if b else " to end") for a, b in s["parts"]) + ") and module constants")
    row = common_row(s["id"], s["cls"])
    lab = s["id"]
    in_d1 = lab in d1_labels
    stages = []
    if in_d1:
        stages.append({"stage": "D.1", "window_dates": "fold0_train 2025-04-01..2025-10-16 (142 dates); train_union 2025-04-01..2026-05-13 (289 dates) (research window)", "purpose": "screen", "source": "reports/stage_d1_accounting.json windows, fold0_rerun, train_union_run"})
        w = sorted(d1a_windows.get(lab, []))
        stages.append({"stage": "D.1a", "window_dates": "; ".join(f"{a} {b}..{c}" for a, b, c in w) + " (research window)", "purpose": "other", "source": "reports/stage_d1a_regression.json runs (regression of D.1's 23 trials)"})
        stages.append({"stage": "D.1b", "window_dates": "train_union 2025-04-01..2026-05-13 (continuity rerun)", "purpose": "other", "source": "reports/stage_d1b_accounting.json runs"})
    if lab.startswith("C-H4"):
        stages.append({"stage": "D.1b", "window_dates": "fold0_train 2025-04-01..2025-10-16; train_union 2025-04-01..2026-05-13 (research window)", "purpose": "screen", "source": "reports/stage_d1b_ch4_fold0.json; reports/stage_d1b_accounting.json runs (trial #24)"})
    stages.append({"stage": "D.1d", "window_dates": "train_union 2025-04-01..2026-05-13 (continuity rerun in the 31-trial accounting)", "purpose": "other", "source": "reports/stage_d1d_accounting.json runs"})
    stages += [D1E_TRIAL, D1F_CONT, D1F_CONF]
    if lab in ("A-H2 rth close window (buy)", "B-H1 opening-range breakout (hold 75)", "D-H2 inverse-vol sizing"):
        stages.append({"stage": "E.2b", "window_dates": "train_union 2025-04-01..2026-05-13 (289 dates; regression bit for bit)", "purpose": "other", "source": "reports/E.2b_RETURN.md section 3 'MES regressions (bit for bit)'"})
    a = acc_d1d[lab]
    verd = {"D.1/D.1d train_union": f"verdict {a['verdict']}; robust {a['robust']}; drift_verdict {a['drift_verdict']}", "D.1/D.1d_ref": "reports/stage_d1d_accounting.json runs[]"}
    verd.update(tier_a_verdict(lab))
    extra = []
    if lab.startswith("E-H1") or lab.startswith("E-H2"):
        extra = [{"input": "FOMC statement, CPI and NFP release dates and times", "covers_w_ext": False, "covers_w_cf": True,
                  "path": "strategy/research/e_calendar_event/_release_table_2019_2024.py (RELEASE_TABLE_2019_2024) | strategy/research/e_calendar_event/h1_scheduled_macro_drift.py (RELEASE_TABLE_ET)",
                  "stated_range": "RELEASE_TABLE_2019_2024: 2019-05-01..2024-02-29 (module docstring line 1; one release per date, collisions dropped); RELEASE_TABLE_ET: 2025-04-01..2026-06-12. For 2010-2019: reports/stage_e14_cal_releases.json covers FOMC (with EIA NGS, WPSR) 2010-06-01..2019-05-31 but no CPI or NFP; no 2010-2019 CPI/NFP table found (searched data/, strategy/members/*/_releases.py (TABLE_RANGE 2019-05-01..2026-06-19), reports/stage_e14*, reports/stage_e16*). Moot for W_ext since MES has no W_ext bars."}]
    if lab.startswith("E-H4"):
        extra = [{"input": "CME equity holiday calendar (data.cme_calendar.HOLIDAYS)", "covers_w_ext": False, "covers_w_cf": True, "path": "data/cme_calendar.py",
                  "stated_range": "2019-2026 (module docstring: 2019-2024 entries from D.1f Task 3b, 2025-2026 from 9cbd815); hist2010 equity calendar data/calendars/hist2010/equity.json covers 2010-06-01..2019-05-31 for ES/MES but is not the module E-H4 imports"}]
    row.update({"module": s["module"], "definition_verbatim": defin + ("\nModule constants: " + "; ".join(cst) if cst else ""),
                "trigger_event": s["event"], "decision_time_ct": s["dt"], "side_rule": check(s["side"], d, s["module"]), "side_kind": s["kind"],
                "intraday_hold": s["hold"], "exit_rule_verbatim": check(s["exit_"], d, s["module"]),
                "expected_events_per_year": s["epy"] + "; " + d1f_count(lab) + f"; D.1d train_union n_trips {a['n_trips']} (count)",
                "inputs_needed": mes_inputs(extra), "stages_read": stages, "verdicts": verd})
    rows.append(row)

# RT1..RT7
src(G, "module docstring and constants; classes OrbRetest, SpikeFadeRetest, DailyVolRegimeGateRetest, DailyVolSizingRetest")
for lab, (tag, kind, event, dt, hold) in RT.items():
    decl_row = line_starting(DECL_G, f"| {tag} |")
    fac_row = line_starting(CL_LIST, f"| {lab} |")
    row = common_row(lab, t1[lab]["class"])
    side = {"**RT1**": "Trigger: the first RTH 5-min bar at slot ≥ 6 whose close ≥ OR high + 4 ticks (long) or ≤ OR low − 4 ticks (short)",
            "**RT2**": "As RT1, **hold 15 bars**", "**RT3**": "Enter in the break direction.", "**RT4**": "As RT3, entering **against** the break direction.",
            "**RT5**": "Fade the bar's direction; close == open means no trade.", "**RT6**": "The base entry is unchanged: long 1 micro at 1-minute bar index 60 of the trade date, held 30 one-minute bars.",
            "**RT7**": "The base entry is unchanged: long at 1-minute bar index 60, every day, held 30 one-minute bars."}[tag]
    exit_ = {"**RT1**": "**Hold 1 bar** (bar+1): exit on completion of the next 5-min bar.", "**RT2**": "**hold 15 bars** (bar+15 = 75 min), exiting earlier only if the RTH segment ends first.",
             "**RT3**": "**Hold 6 bars** (30 min, the original's hold; the source states none for this comparison).", "**RT4**": "As RT3, entering **against** the break direction.",
             "**RT5**": "**Hold 1 bar** (bar+1, where the source's reversal was measured; the original held 2 one-minute bars).", "**RT6**": "held 30 one-minute bars.", "**RT7**": "held 30 one-minute bars."}[tag]
    a = acc_d1d[lab]
    verd = {"D.1d train_union": f"verdict {a['verdict']}; robust {a['robust']}; drift_verdict {a['drift_verdict']}", "D.1d_ref": "reports/stage_d1d_accounting.json runs[]; reports/stage_d1d_retests.json"}
    verd.update(tier_a_verdict(lab))
    row.update({"module": G, "definition_verbatim": decl_row + "\n" + fac_row, "trigger_event": event, "decision_time_ct": dt,
                "side_rule": check(side, decl_row, DECL_G), "side_kind": kind, "intraday_hold": hold, "exit_rule_verbatim": check(exit_, decl_row, DECL_G),
                "expected_events_per_year": ("every trade date (RT7) / low-vol tercile days (RT6)" if tag in ("**RT6**", "**RT7**") else "at most one a day" if tag != "**RT5**" else "several per day possible") + "; " + d1f_count(lab) + f"; D.1d train_union n_trips {a['n_trips']} (count)",
                "inputs_needed": mes_inputs(),
                "stages_read": [{"stage": "D.1d", "window_dates": "fold0_train 2025-04-01..2025-10-16; train_union 2025-04-01..2026-05-13 (research window)", "purpose": "screen", "source": "reports/stage_d1d_retests.json meta.windows; reports/stage_d1d_accounting.json"},
                                D1E_TRIAL, D1F_CONT, D1F_CONF],
                "verdicts": verd})
    rows.append(row)

# ------------------------------------------------------------------ the 21 event statistics (A2)
F_SPEC = {
    "F3_2": ("**F3.2**", None),
    "F3_3": ("**F3.3**", None),
    "F4_4": ("**F4.4 Round numbers.**", None),
    "F4_1": ("**F4.1 RTH open.**", None),
    "F6_1": ("**F6.1**", None),
}


def fbullet(tag):
    i = ftext.index("- " + tag)
    j = ftext.find("\n- ", i + 3)
    k = ftext.find("\n\n", i)
    end = min(x for x in (j, k) if x != -1)
    return ftext[i:end].strip()


def bucket_times(k):
    start = 8 * 60 + 30 + 30 * (k - 1)
    return f"{start // 60:02d}:{start % 60:02d}", f"{(start + 30) // 60:02d}:{(start + 30) % 60:02d}"


GROW = {g: line_starting(DECL_G, f"| **{g} ") for g in ("G1", "G2", "G3", "G4", "G5")}
G_COMMON = cut(gtext, "Every G statistic is an **event statistic**:", "**Trailing same-slot baselines")
A2_RULE = cut(cltext, "Confirmation\ndirection s = the sign of the recorded implied edge", "per-event definitions being exactly")
src(CL_LIST, "2.1 A2 paragraph 'Confirmation direction s = ...' (used verbatim in each statistic's side_rule)")

stat_ids = [r["id"] for r in t1.values() if r["kind"] == "statistic"]
for sid in stat_ids:
    tbl = line_starting(CL_LIST, f"| {sid} |")
    s_val = int(tbl.split("|")[4].strip())
    row = common_row(sid, t1[sid]["class"])
    row["module"] = None
    if sid.startswith("F"):
        fam = sid[:4]
        bul = fbullet(F_SPEC[fam][0])
        fa = ffacts[sid]
        defin = bul + "\n" + tbl
        module = "strategy/research/f_data_native/_stylized_facts.py (statistic builder); strategy/research/_d1e_event_series.py (event values); D.1f wrapper per confirmation list 5.4"
        disc = {"stage": "D.1b", "window_dates": "EDA dates 2025-10-17..2026-05-13 (139 after exclusions; research window)", "purpose": "screen", "source": "reports/stage_d1b_family_f_declaration.md section 0; reports/stage_d1b_family_f_facts.json meta"}
        d1verd = f"bh_reject {fa['bh_reject']} (Family F selection rule admitted zero hypotheses, docs/STAGES.md D.1b)"
        cnt = f"D.1b EDA n {fa['n']} (count)"
        if fam == "F3_2":
            m = re.match(r"F3_2_bucket(\d\d)_bucket(\d\d)", sid)
            k = int(m.group(1))
            a0, a1 = bucket_times(k)
            b0, b1 = bucket_times(k + 1)
            ev = f"every trade date: bucket {k:02d} ({a0}-{a1} CT) return as predictor of bucket {k+1:02d} ({b0}-{b1} CT)"
            dt = f"{a1} CT (close of bucket {k:02d}; last 1-minute bar opening {int(a1[:2]) - (1 if a1[3:] == '00' else 0):02d}:{(int(a1[3:]) - 1) % 60:02d} CT)"
            hold = f"30 minutes ({b0}-{b1} CT)"
            kind = "fade" if s_val < 0 else "momentum"
            epy = "one per trade date"
        elif sid == "F3_3_overnight_to_close_momentum":
            ev, dt, hold, kind, epy = ("every trade date: return from the trade date's first bar to 09:00 CT as predictor of the 14:30-15:00 CT return",
                                        "predictor complete at 09:00 CT; position taken over 14:30-15:00 CT", "30 minutes (14:30-15:00 CT)", "fade" if s_val < 0 else "momentum", "one per trade date")
        elif sid == "F3_3_opening_30min_to_close_momentum":
            ev, dt, hold, kind, epy = ("every trade date: 08:30-09:00 CT return as predictor of the 14:30-15:00 CT return",
                                        "predictor complete at 09:00 CT; position taken over 14:30-15:00 CT", "30 minutes (14:30-15:00 CT)", "fade" if s_val < 0 else "momentum", "one per trade date")
        elif sid == "F6_1_overnight_range_position":
            ev, dt, hold, kind, epy = ("every trade date: position of the 08:30 CT open in the ETH high-low range as predictor of the 08:30-09:30 CT return",
                                        "08:30 CT (the 08:30 bar's open; ETH bars before it)", "60 minutes (08:30-09:30 CT)",
                                        "other: side = s x sign(position - 0.5), s = +1 (buy when the 08:30 open is in the upper half of the ETH range, the event value in strategy/research/f_data_native/_stylized_facts.py F6.1 builder)", "one per trade date")
        elif sid.startswith("F4_4"):
            ev, dt, hold, kind, epy = ("approach of a multiple of 100 index points (previous close below L <= current high, or above L >= current low), any session, 30-min refractory per level",
                                        "variable: the approach bar, any session", "15 minutes from L",
                                        "fade (s = -1: side = minus the approach-through direction; statistic positive = continuation through L)", "variable (several per week)")
        elif sid.startswith("F4_1"):
            ev, dt, hold, kind, epy = ("a bar opening 09:00..14:29 CT whose close crosses the 08:30 CT open from the previous close; 15-min refractory",
                                        "variable: the crossing bar, 09:00-14:29 CT", "15 minutes", "fade (s = -1: against the crossing direction)", "variable (up to several per day)")
        stage_list = [disc, D1E_EVENT, D1F_CONF]
    else:
        g, seg, tf = sid.split(".")
        ga = gfacts[sid]
        defin = G_COMMON + "\n" + GROW[g] + "\n" + tbl
        module = "strategy/research/g_timeframe/_stylized_facts.py (statistic builder); strategy/research/_d1e_event_series.py (event values); D.1f wrapper per confirmation list 5.4"
        disc = {"stage": "D.1d", "window_dates": "EDA dates 2025-10-17..2026-05-13 (research window)", "purpose": "screen", "source": "reports/stage_d1d_timeframe_declaration.md sections 3 and 5; reports/stage_d1d_family_g_facts.json"}
        d1verd = f"bh_reject {ga['bh_reject']}; eligible {ga['eligible']}; selection {ga['selection']} (declared sweep admitted zero hypotheses, docs/STAGES.md D.1d)"
        cnt = f"D.1d EDA n_events {ga['n_events']} (count)"
        tfm = int(tf)
        dirn = "momentum" if s_val > 0 else "fade"
        if g == "G1":
            ev = f"{seg} {tf}-min slot whose |body| / trailing same-slot mean |body| >= Q80"
        elif g == "G2":
            ev = f"{seg} {tf}-min slot (not the segment's first) closing beyond the max high / min low of the segment's earlier slots"
        elif g == "G3":
            ev = f"first RTH {tf}-min slot j >= 1 closing beyond the opening range of RTH slot 0 (08:30-{8 + (30 + tfm) // 60:02d}:{(30 + tfm) % 60:02d} CT); at most one per day"
        elif g == "G5":
            ev = f"first RTH {tf}-min slot closing above the ETH high or below the ETH low; up to 2 per day"
        else:
            ev = f"{seg} {tf}-min slot event per declaration"
        dt = f"variable: completion of the event {tf}-min slot ({'08:30-15:00 CT RTH' if seg == 'RTH' else 'ETH, 17:00 CT prior evening to 08:30 CT'})"
        hold = "to the RTH segment end (about 15:00 CT)" if g == "G3" else f"{tf} minutes (next slot)"
        kind = f"{dirn} (s = {s_val:+d}; d = sign of the event bar's move or break direction)"
        epy = "variable (event count per declaration)"
        stage_list = [disc, D1E_EVENT, D1F_CONF]
    side = A2_RULE
    src(DECL_F if sid.startswith("F") else DECL_G, f"{sid}: declaration bullet/table row")
    verd = {"D.1b/D.1d discovery": d1verd}
    verd.update(tier_a_verdict(sid))
    row.update({"module": module, "definition_verbatim": defin, "trigger_event": ev, "decision_time_ct": dt,
                "side_rule": f"s = {s_val:+d} (D.1f Tier A table). " + check(side, cltext, CL_LIST), "side_kind": kind, "intraday_hold": hold,
                "exit_rule_verbatim": None, "expected_events_per_year": epy + "; " + d1f_count(sid) + "; " + cnt,
                "inputs_needed": mes_inputs(), "stages_read": stage_list, "verdicts": verd})
    row["exit_rule_note"] = "event statistic: no exit rule; the tested quantity is the per-event net value over the declared forward window (confirmation list 2.1 A2)"
    rows.append(row)

# ------------------------------------------------------------------ Family H (A3)
HM = cut(cltext, "- Breakout entry (H1 to H4):", "- Parameters, all fixed here:")
H_FILES = {"H1 NR4 opening-range breakout": "h1_nr4_breakout.py", "H2 NR7 opening-range breakout": "h2_nr7_breakout.py",
           "H3 inside-day opening-range breakout": "h3_inside_day_breakout.py", "H4 bottom-tercile prior range, breakout": "h4_bottom_tercile_breakout.py",
           "H5 top-tercile prior range, opening-range fade": "h5_top_tercile_fade.py", "H6 prior-close location follow-through": "h6_prior_close_location.py"}
src("strategy/research/h_daily_bar/h1..h6 *.py", "module docstrings and constants (LOOKBACK, GUARDED_BARS, ENTRY)")
for hid, fn in H_FILES.items():
    tbl = line_starting(CL_LIST, f"| {hid.split(' ')[0]} ")
    mod = "strategy/research/h_daily_bar/" + fn
    row = common_row(hid, "C7")
    is6 = hid.startswith("H6")
    is5 = hid.startswith("H5")
    side = ("Open entry (H6): market_intent on the 08:30 bar (fills at the 08:31 open)." if is6 else
            "Fade entry (H5): the same triggers, opposite side." if is5 else
            "on the first 1-minute bar with CT time in [09:00, 14:30)\n  whose close > OR_high, emit market_intent BUY 2 micros; whose close < OR_low, emit\n  market_intent SELL 2 micros.")
    row.update({"module": mod, "definition_verbatim": tbl + "\n" + HM + "\nModule docstring: " + doc(mod).split("\n\n")[1].replace("\n", " "),
                "trigger_event": {"H1": "Range[d-1] < each of Range[d-2..d-4] (NR4), then the first OR30 close-through", "H2": "NR7, then the first OR30 close-through",
                                  "H3": "inside day d-1, then the first OR30 close-through", "H4": "Range[d-1] <= P33.33 of the prior 60 ranges, then the first OR30 close-through",
                                  "H5": "Range[d-1] >= P66.67 of the prior 60 ranges, then the first OR30 close-through (faded)",
                                  "H6": "CLV of day d-1 >= 0.8 (buy) or <= 0.2 (sell), Range[d-1] > 0"}[hid[:2]],
                "decision_time_ct": "08:30 CT bar of day d (fills 08:31); condition uses day d-1's RTH bars through 14:59 CT" if is6 else "variable: the first close-through 1-minute bar in [09:00, 14:30) CT; condition uses complete daily bars before d",
                "side_rule": check(side, cltext, CL_LIST) + (" CLV >= 0.8 buys, CLV <= 0.2 sells, otherwise no trade" if is6 else ""),
                "side_kind": "other: side follows day d-1's close location in its range (CLV >= 0.8 buy, <= 0.2 sell), a follow-through of d-1's position, not a trigger-day move" if is6 else ("fade" if is5 else "momentum"),
                "intraday_hold": "08:31 to 14:58 CT" if is6 else "entry to 14:58 CT", "exit_rule_verbatim": check("Exit for every H test: a market_intent to flatten emitted on the first bar the strategy\n  sees with CT time >= 14:58 and before the engine's no-new-positions time (fills at the next\n  open)", cltext, CL_LIST),
                "expected_events_per_year": ("days with CLV >= 0.8 or <= 0.2" if is6 else "condition days with an OR30 close-through") + "; " + d1f_count(hid),
                "inputs_needed": mes_inputs(),
                "stages_read": [{"stage": "D.1e", "window_dates": None, "purpose": "power", "source": "progress.md D.1e: 'Seven classes, 101 members: 95 measured and 6 projected' (Family H projected, no bar read)"}, D1F_CONF],
                "verdicts": tier_a_verdict(hid)})
    row["tier"] = "A (D.1f Tier A, class C7; new in D.1f, never screened on the research window)"
    rows.append(row)

# ------------------------------------------------------------------ E.16 H1 and H4
P1 = "reports/stage_e16_prereg_H1.md"
P4 = "reports/stage_e16_prereg_H4.md"
PC = "reports/stage_e16_prereg_common.md"
p1 = (ROOT / P1).read_text()
p4 = (ROOT / P4).read_text()
pc = (ROOT / PC).read_text()
src(P1, "1 hypothesis (verbatim prompt), 2 operational definition, 3 fixed parameters, 5 power")
src(P4, "1 hypothesis, 2 operational definition, 3 fixed parameters")
src(PC, "1-5: sources, rulings U1-U3b, windows, splice rule, settlement minutes and opens")
src("reports/stage_e16_briefs/lead_spec.md", "lines 62-67 price path and vehicle per E.12 (D2)")
src("reports/E.17_RETURN.md", "1 verdict summary; 3 Part 2 steps 9-14 (A3 selection, fallback, buy, run manifest, runs, verdict table)")
src("reports/stage_e17_run_manifest.json", "stores per root: ext2010/ext2010h plan and path names, step2 path names (no file opened)")
src("reports/E.16_RETURN.md", "STAGES.md summary of E.16 Part A (frozen, nothing read)")
src("multiday/constants.py", "ROOTS (17), LISTING_FIRST, LE_FIRST, WINDOW_LAST, HIST_LAST, STEP2_FIRST")
ROOTS27 = ["NQ", "YM", "RTY", "ZT", "ZF", "ZN", "TN", "ZB", "UB", "6E", "6A", "6B", "6C", "6J", "6S", "6N", "CL", "NG", "GC", "HG", "ZC", "ZW", "ZS", "ZM", "ZL", "LE", "HE"]
WEXT17 = ["NG", "NQ", "ZN", "6E", "GC", "ZC", "ZT", "ZF", "ZB", "UB", "TN", "CL", "ZL", "ZS", "RTY", "HE", "LE"]
VEH = {"NQ": "MNQ", "YM": "MYM", "RTY": "M2K", "CL": "MCL", "GC": "MGC", "HG": "MHG"}
wext_map = {r: (r if r in WEXT17 else None) for r in ROOTS27}
E17_WIN = ("E.17 run once (registered r002-E16, N 473 -> 478): 2010-07-01..2024-02-29 for the 17 W_ext roots (ext2010 stores NG NQ ZN 6E GC ZC from 2010-06-07, "
           "ext2010h stores ZT ZF ZB UB TN CL ZL ZS RTY HE LE from 2010-07-01, to 2019-04-30; then step2 2019-05-06..2024-02-29), with TN from 2016-01-04 "
           "(no unit before listing 2016-01-11), RTY from 2017-06-01 (no unit before 2017-07-10), HE from 2017-07-03, LE: no H1 or H4 unit 2010-06-07..2014-12-14 (R-S3, weak settlement grade); "
           "fallback 2019-05-06..2024-02-29 for YM HG 6S 6J 6A 6B 6N ZM ZW 6C (not funded)")
SETTLE_INPUT = {"input": "settlement minute S_p and day-session open O_p per product and date", "covers_w_ext": True, "covers_w_cf": True,
                "path": "reports/stage_e16_settlement.json (table in reports/stage_e16_prereg_common.md section 5)", "stated_range": "2010-06-07..2024-02-29 for all 27 products (RTY from 2017-07-10, TN from 2016-01-11; LE/HE 2010-06-07..2014-12-14 graded weak)"}
CAL_INPUT = {"input": "CME trade-date calendars (closures, early halts, sessions)", "covers_w_ext": True, "covers_w_cf": True,
             "path": "data/calendars/hist2010/{equity,rates,fx,energy,metals,grains,livestock}.json (2010-2019); data/calendars/<group>.py (2019-05 on); reports/stage_e16_calendars/hist2010_livestock.json",
             "stated_range": "hist2010 coverage 2010-06-01..2019-05-31 (each file's coverage field); group calendars 2019-05-01..2026-06-19 (data/calendars/equity.py docstring); hist2010_livestock.json 2010-06-01..2019-05-31"}
BARS_INPUT = {"input": "1-minute bars of each of the 27 price paths", "covers_w_ext": "true for the 17 W_ext roots; false for YM 6A 6B 6C 6J 6S 6N HG ZW ZM", "covers_w_cf": True,
              "path": "stores named in reports/stage_e17_run_manifest.json (not opened)", "stated_range": "ext2010 2010-06-07..2019-04-30 (6 roots), ext2010h 2010-07-01..2019-04-30 (11 roots), step2 2019-05-06..2024-02-29 (27 roots)"}
for tid, pfile, ptext, kind, side_v, exit_v, dt, hold, ev, n, verdict_line in [
    ("E16-H1", P1, p1, "momentum",
     "Signal s = sign(close of bar(p,d,S_p-31) -\nPS(p,d-1)). s = 0: no trade (counted). Entry: open of bar(p,d,S_p-30), direction s.",
     "Exit: open of\nbar(p,d,S_p).",
     "close of bar S_p-31 on d (equity 14:29 CT from 2020-10-26, 14:44 CT before; rates and FX 13:29; CL and NG 12:59; GC 11:59; HG 11:29; grains 12:44 (13:29 2012-06-25..2013-04-07); livestock 12:29); the reference is the prior eligible date's settlement-minute price",
     "30 minutes (S_p-30 to S_p)", "every eligible product-date with a nonzero signal",
     "E.17 base n 3,380 date units; H1's 55,070 traded product units (counts; reports/E.17_RETURN.md section 3 step 14)",
     "H1 FAIL (Holm no, mean > 0 no, years 15 / 0; DSR at N = 478 0.0) reports/E.17_RETURN.md section 3 step 14; 'E16-H1..H5: all five FAIL' section 1; Fable: H1-H4 VERIFIED"),
    ("E16-H4", P4, p4, "fade",
     "m = open of\nbar(p,d-1,S_p) - open of bar(p,d-1,S_p-30) (H1's gross window move on d-1, d-1 per section 2).\nm = 0: no trade. Direction -sign(m).",
     "exit: open of\nbar(p,d,S_p-31).",
     "the side is fixed by d-1's settlement-window move (last input: open of bar(p,d-1,S_p) on d-1); entry at the open of bar O_p+1 on d (equity 08:31 CT, rates/FX/GC 07:21, CL/NG 08:01, HG 07:11, grains 08:31 (09:31 to 2013-04-07), livestock per era)",
     "O_p+1 to S_p-31 on d (about 6 hours on equity)", "every eligible product-date whose prior date had a nonzero H1 window move",
     "E.17 base n 3,381 date units (count; reports/E.17_RETURN.md section 3 step 14)",
     "H4 FAIL (Holm no, mean > 0 no, years 15 / 0; DSR at N = 478 0.0) reports/E.17_RETURN.md section 3 step 14; Fable: H1-H4 VERIFIED"),
]:
    defin = cut(ptext, "## 1. The hypothesis", "## 2.").split("```")[1] + "\n" + cut(ptext, "## 2. The operational definition", "## 3.").split("```")[1]
    rows.append({"trigger_id": tid, "cluster_or_stage": "Stage E.16 (frozen) / E.17 (registered and run once)", "member_id": tid, "module": "base_rules/ (run.py, intraday.py as hashed in reports/stage_e16_freeze.json)",
                 "freeze_file": "reports/stage_e16_freeze.json (commit 8f388c8, manifest 5274aa97...); prereg " + pfile + " and " + PC,
                 "traded_root": ROOTS27, "vehicle": {r: VEH.get(r, r) for r in ROOTS27}, "w_ext_root": wext_map, "signal_legs": [],
                 "definition_verbatim": defin.strip(), "trigger_event": ev, "decision_time_ct": dt,
                 "side_rule": check(side_v, ptext, pfile), "side_kind": kind, "intraday_hold": hold, "exit_rule_verbatim": check(exit_v, ptext, pfile),
                 "expected_events_per_year": ev + "; " + n,
                 "inputs_needed": [BARS_INPUT, SETTLE_INPUT, CAL_INPUT, {"input": "per-product windows", "covers_w_ext": True, "covers_w_cf": True, "path": "reports/stage_e16_windows.json", "stated_range": "2010-07-01..2024-02-29 (24 products), RTY 2017-06-01.., TN 2016-01-04.., HE 2017-07-03.. (prereg common section 3)"}],
                 "stages_read": [{"stage": "E.16 Part A", "window_dates": None, "purpose": "other", "source": "docs/STAGES.md E.16 'nothing read, bought or registered'; frozen only"},
                                 {"stage": "E.16 Part A", "window_dates": "priors only, no bars", "purpose": "power", "source": pfile + " section 5 / reports/stage_e16_power.json"},
                                 {"stage": "E.17", "window_dates": E17_WIN, "purpose": "other", "source": "reports/E.17_RETURN.md section 1 and section 3 steps 9-14 (registered one-shot test, the only bar read; no later stage re-read it: grep of reports/E.18..E.22 returns finds only the registry line r002-E16)"}],
                 "tier": "n/a", "verdicts": {"E.17": verdict_line},
                 "settlement_note": "S_p per product from reports/stage_e16_settlement.json (prereg common section 5). " + ("Decision at S_p-31, before S_p by construction; equity S_p 15:15 CT before 2020-10-26 is past Topstep's 15:08 flatten (R-S6), counted and reported." if tid == "E16-H1" else "Side fixed at d-1's settlement minute; the d trade ends at S_p-31 on d, before d's settlement."),
                 "exclusion": None})

# ------------------------------------------------------------------ exclusions
excluded = [
    {"item": "Stage C (harness build)", "reason": "no trading rule: strategy/null_strategy.py and strategy/random_baseline.py are baselines; Stage C built the harness, leakage suite and holdout (docs/STAGES.md lines 17-21)"},
    {"item": "D.1f Tier B, 43 null-side coverage statistics (F1_1 x10, F2_4 x2, F3_2 buckets 03_04/09_10/11_12, F4_2, F4_4 x50, F5_1 x2, F5_2 x2, F5_3, 21 G statistics)",
     "reason": "not counted as trials (N counted 58 = the Tier A list); 'Tier B members enter the class null ... and never an edge claim' (confirmation list 2.2). Not one of the brief's exclusion categories; listed for the lead's ruling. Same MES-only data facts as the Tier A rows (no W_ext; W_cf read in D.1f)."},
    {"item": "D.1f non-directional facts (F1_2 variance ratios, F2_1, F2_2, F2_3, F4_3 gap-fill rates, G0) and F3.1", "reason": "descriptive only, no side ('a variance ratio has no side', confirmation list 2.2); F3.1 ineligible (Family F declaration F3)"},
    {"item": "D.1b Family F and D.1d Family G declared spaces as such", "reason": "their directional statistics appear as the 21 Tier A rows (or Tier B above); the selection rules admitted zero hypotheses (docs/STAGES.md D.1b, D.1d)"},
    {"item": "D.1g C6 (MBO passive execution)", "reason": "not run; closed by the user 2026-09-23 (docs/STAGES.md D.1g); C-H4's trade-through lower bound is the C-H4 row"},
    {"item": "D.1c", "reason": "constraint audit, no code or rule (docs/STAGES.md)"},
    {"item": "D.1e", "reason": "design only (criteria, power, quotes); its reads are listed in the rows' stages_read"},
    {"item": "E.13 C1 draft (reports/stage_e13_prereg_ngrepl.md) and C2 draft (reports/stage_e13_prereg_gexmom.md)", "reason": "drafts, 'Nothing here is frozen' (gexmom status line); C1 is an ML model (below); C2 see E.14"},
    {"item": "E.14 C2 GEX-conditioned S&P late-session momentum", "reason": "never frozen: stopped at its power rule before its freeze (reports/E.14_RETURN.md lines 8-13; 'No freeze, no registration, no purchase, no evaluation' line 165). Also needs SqueezeMetrics GEX and ES 2011-2019 bars, neither in the repo's owned stores (not one of the 17 W_ext roots)."},
    {"item": "E.14/E.15/E.17 C1 (backward NG replication; C1-T1 NG h60, C1-T2 NG hF)", "reason": "ML model: 'Model M1: the frozen Gate 0 family B ridge (lambda 0.1)' (reports/stage_e14_prereg_C1.md section 3); E.17 STOPPED at guard C10"},
    {"item": "E.18 C1b (C1b-T1, C1b-T2)", "reason": "ML model (C1 re-registered with the C10 fix; reports/stage_e18_prereg_C1b.md); FAIL in E.18"},
    {"item": "E16-H2 month-end NQ/ZN pair", "reason": "already multi-day (brief; H2 is E.21 T4)"},
    {"item": "E16-H3 Treasury auction cycle", "reason": "already multi-day (brief)"},
    {"item": "E16-H5 equal-risk combination of H1 to H4", "reason": "a combination book, not itself a trigger (reports/stage_e16_prereg_H5.md section 1: 'The equal-risk daily combination of H1 to H4's net daily P&L series')"},
    {"item": "docs/STAGE_E_DESIGN.md CP1..CPn ports of D.1 rules to other products (e.g. CP2 = B-H1 hold 75)", "reason": "Stage E cluster members, outside the CDE assignment (K1..K8 readers)"},
]

out = {"assignment": "CDE", "rows": rows, "excluded": excluded, "sources_read": SOURCES,
       "not_finished": [
           "decision_time_ct for D.1 rules that enter at the trade date's bar index 60 or first bar is stated by clock from the docstrings (session reopen about 17:00 CT); the exact minute depends on the bars, which were not opened.",
           "E-H2's exact decision minute (end of the 5-minute reaction window) and F4_4/G event counts per year were not derived beyond the rule text; counts given are D.1f n_activity and EDA n.",
           "MES settlement minute: no MES row in the repo's settlement table; the equity-index rows (NQ, YM, RTY) are cited instead.",
       ]}
(OUT / "CDE.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("rows", len(rows), "excluded", len(excluded), "sources", len(SOURCES))
