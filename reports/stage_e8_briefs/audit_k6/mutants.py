"""Auditor's mutant run for the K6 members (Stage E.8 Task 3, item 12).

Runs ONLY against an out-of-tree copy of the repository (COPY below); never touches the
repository's strategy/ or tests/. For each mutant: read the pristine source from the MAIN repo,
assert the old string occurs exactly once, write the mutated text into the COPY, run the named
test files there with the main venv's interpreter at nice 10 (-x: stop at the first failure),
record killed / survived, and restore the COPY's file from the pristine text.

    PYTHONPATH=. uv run python reports/stage_e8_briefs/audit_k6/mutants.py [ids...]

Appends one JSON line per mutant to reports/stage_e8_briefs/audit_k6/mutants.jsonl and prints a
summary table.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

MAIN = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
COPY = Path("/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/"
            "94d6572b-fdf2-4814-9116-60c2521d80a0/scratchpad/auditor/repo")
PY = MAIN / ".venv" / "bin" / "python"
OUT = MAIN / "reports/stage_e8_briefs/audit_k6/mutants.jsonl"
K6 = "strategy/members/k6/"
T = "tests/"
PORTS = (T + "test_k6_members_ports.py",)
CP2 = (T + "test_k6_members_ports_cp2.py",)
CP3 = (T + "test_k6_members_ports_cp3.py",)
CG = (T + "test_k6_members_crushgap.py",)
LC = (T + "test_k6_members_limitcont.py",)
WD = (T + "test_k6_members_wasde.py",)
TB = (T + "test_k6_members_tables.py",)
ALL_A = PORTS + CP2 + CP3 + CG
ALL_B = LC + WD

# (id, file, old, new, tests, what it tests)
MUTANTS: list[tuple[str, str, str, str, tuple[str, ...], str]] = [
    # ---- cp1
    ("A-C1-01", K6 + "cp1.py", "SIGNAL_AFTER_O_MIN = 29", "SIGNAL_AFTER_O_MIN = 30", PORTS, "signal bar 08:59"),
    ("A-C1-02", K6 + "cp1.py", "ENTRY_BEFORE_C_MIN = 31", "ENTRY_BEFORE_C_MIN = 30", PORTS, "entry bar C-31"),
    ("A-C1-03", K6 + "cp1.py", "EXIT_BEFORE_C_MIN = 2  #", "EXIT_BEFORE_C_MIN = 1  #", PORTS, "exit bar C-2"),
    ("A-C1-04", K6 + "cp1.py", 'return "buy" if s > 0 else "sell"', 'return "sell" if s > 0 else "buy"', PORTS, "direction"),
    ("A-C1-05", K6 + "cp1.py", "GRAIN_EVENING_OPEN_CT = time(19, 0)", "GRAIN_EVENING_OPEN_CT = time(18, 0)", PORTS, "19:00 evening open"),
    ("A-C1-06", K6 + "cp1.py", "if first_id != signal_id:", "if False:", PORTS, "signal-bar instrument guard"),
    ("A-C1-07", K6 + "cp1.py", "if s == 0:\n            return None", "if False:\n            return None", PORTS, "zero signal no trade"),
    ("A-C1-08", K6 + "cp1.py", "return opened.date() == day and opened.time() == self._leg.o", "return opened.date() == day and opened.time() >= self._leg.o", PORTS, "livestock first bar exact 08:30 (K6-L-02)"),
    ("A-C1-09", K6 + "cp1.py", "if self._first is not None:\n            return False", "if False:\n            return False", PORTS, "earliest bar only (K6-L-01)"),
    ("A-C1-10", K6 + "cp1.py", 'return to_ticks(asdict(bar)["open"], tick)', 'return to_ticks(asdict(bar)["close"], tick)', PORTS, "first bar OPEN"),
    ("A-C1-11", K6 + "cp1.py", "return (leg_market_intent(view, self.root, side, self._leg.q),)", "return (leg_market_intent(view, self.root, side, self._leg.q + 1),)", PORTS, "size q_c"),
    ("A-C1-12", K6 + "cp1.py", "self._signal = (to_ticks(bar.close, self._leg.tick), bar.instrument_id)", 'self._signal = (to_ticks(asdict(bar)["open"], self._leg.tick), bar.instrument_id)', PORTS, "signal bar CLOSE"),
    ("A-C1-13", K6 + "cp1.py", "return opened >= datetime.combine(day - ONE_DAY, GRAIN_EVENING_OPEN_CT, tzinfo=CT)", "return opened >= datetime.combine(day - ONE_DAY, GRAIN_EVENING_OPEN_CT, tzinfo=CT) and opened.date() == day", PORTS, "grain first bar may be on CT date d-1"),
    # ---- cp2
    ("A-C2-01", K6 + "cp2.py", "RANGE_MINUTES = 15", "RANGE_MINUTES = 16", CP2, "OR 15 minutes"),
    ("A-C2-02", K6 + "cp2.py", "BUFFER_TICKS = 4", "BUFFER_TICKS = 3", CP2, "buffer 4 ticks"),
    ("A-C2-03", K6 + "cp2.py", "HOLD_BARS = 75", "HOLD_BARS = 74", CP2, "hold 75 bars"),
    ("A-C2-04", K6 + "cp2.py", "if close >= to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:", "if close > to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:", CP2, "non-strict >= on the high"),
    ("A-C2-05", K6 + "cp2.py", "elif close <= to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:", "elif close < to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:", CP2, "non-strict <= on the low"),
    ("A-C2-06", K6 + "cp2.py", 'side = "buy"\n        elif close', 'side = "sell"\n        elif close', CP2, "direction (up break buys)"),
    ("A-C2-07", K6 + "cp2.py", "if not self._range_end <= at < self._leg.c or not is_flat(account, self.root):", "if not self._range_end <= at <= self._leg.c or not is_flat(account, self.root):", CP2, "no entry from C on"),
    ("A-C2-08", K6 + "cp2.py", "if self._held < HOLD_BARS or account.pending.get(self.root, 0):", "if self._held <= HOLD_BARS or account.pending.get(self.root, 0):", CP2, "exit on the 75th bar"),
    ("A-C2-09", K6 + "cp2.py", "self._triggered = True  # one entry per trade date, even if the engine refuses it", "pass  # one entry per trade date, even if the engine refuses it", CP2, "one entry per trade date"),
    ("A-C2-10", K6 + "cp2.py", "F_REGULAR_CT = {GRAINS: time(13, 18), LIVESTOCK: time(13, 3)}", "F_REGULAR_CT = {GRAINS: time(13, 15), LIVESTOCK: time(13, 0)}", CP2 + PORTS, "trading window to F"),
    ("A-C2-11", K6 + "cp2.py", "self._hi = bar.high if self._hi is None else max(self._hi, bar.high)", "self._hi = bar.close if self._hi is None else max(self._hi, bar.close)", CP2, "OR_high from highs"),
    ("A-C2-12", K6 + "cp2.py", "if self._leg.o <= at < self._range_end:", "if self._leg.o < at < self._range_end:", CP2, "08:30 bar in the range"),
    # ---- cp3
    ("A-C3-01", K6 + "cp3.py", 'CLV_BUY_AT_OR_ABOVE = Decimal("0.8")', 'CLV_BUY_AT_OR_ABOVE = Decimal("0.75")', CP3, "CLV 0.8"),
    ("A-C3-02", K6 + "cp3.py", 'CLV_SELL_AT_OR_BELOW = Decimal("0.2")', 'CLV_SELL_AT_OR_BELOW = Decimal("0.25")', CP3, "CLV 0.2"),
    ("A-C3-03", K6 + "cp3.py", "if num * buy_d >= buy_n * span:", "if num * buy_d > buy_n * span:", CP3, "non-strict >= 0.8"),
    ("A-C3-04", K6 + "cp3.py", "if num * sell_d <= sell_n * span:", "if num * sell_d < sell_n * span:", CP3, "non-strict <= 0.2"),
    ("A-C3-05", K6 + "cp3.py", 'return "buy"\n    if num * sell_d', 'return "sell"\n    if num * sell_d', CP3, "direction"),
    ("A-C3-06", K6 + "cp3.py", "CLOSE_BEFORE_C_MIN = 1", "CLOSE_BEFORE_C_MIN = 2", CP3, "C_d = close of C-1"),
    ("A-C3-07", K6 + "cp3.py", "EXIT_BEFORE_C_MIN = 2  #", "EXIT_BEFORE_C_MIN = 3  #", CP3, "exit C-2"),
    ("A-C3-08", K6 + "cp3.py", "if span <= 0:", "if span < 0:", CP3, "range > 0"),
    ("A-C3-09", K6 + "cp3.py", "if prior.instrument_id != bar.instrument_id:", "if False:", CP3, "instrument guard"),
    ("A-C3-10", K6 + "cp3.py", "complete = (self._has_open_bar and self._close is not None and not self._halt", "complete = (self._has_open_bar and self._close is not None", CP3, "halt day incomplete"),
    ("A-C3-11", K6 + "cp3.py", "if bar.early_halt_ct is not None:\n            return None  # an early-halt day d", "if False:\n            return None  # an early-halt day d", CP3, "halt day d not traded"),
    ("A-C3-12", K6 + "cp3.py", "and len(self._ids) == 1)", "and len(self._ids) >= 1)", CP3, "one instrument_id over [O, C)"),
    ("A-C3-13", K6 + "cp3.py", "if at != self._leg.o or self._entered or not is_flat(account, self.root):", "if at != shift(self._leg.o, 1) or self._entered or not is_flat(account, self.root):", CP3, "entry on the 08:30 bar"),
    ("A-C3-14", K6 + "cp3.py", "self._lo = bar.low if self._lo is None else min(self._lo, bar.low)", "self._lo = bar.close if self._lo is None else min(self._lo, bar.close)", CP3, "L from lows"),
    ("A-C3-15", K6 + "cp3.py", "if not self._leg.o <= at < self._leg.c:\n            return", "if not self._leg.o <= at <= self._leg.c:\n            return", CP3, "daily bar [O, C)"),
    # ---- crushgap
    ("A-CG-01", K6 + "crushgap.py", '"ZM": Decimal("0.022")', '"ZM": Decimal("0.024")', CG, "weight 0.022"),
    ("A-CG-02", K6 + "crushgap.py", '"ZL": Decimal("11")', '"ZL": Decimal("10")', CG, "weight 11"),
    ("A-CG-03", K6 + "crushgap.py", '"ZS": Decimal("-1")', '"ZS": Decimal("1")', CG, "minus P_ZS"),
    ("A-CG-04", K6 + "crushgap.py", 'FILTER_USD_PER_BU = Decimal("0.02")', 'FILTER_USD_PER_BU = Decimal("0.03")', CG, "filter 0.02"),
    ("A-CG-05", K6 + "crushgap.py", 'if g_units >= FILTER_UNITS:\n            return "buy"\n        if g_units <= -FILTER_UNITS:\n            return "sell"', 'if g_units >= FILTER_UNITS:\n            return "sell"\n        if g_units <= -FILTER_UNITS:\n            return "buy"', CG, "direction (gap up buys ZS)"),
    ("A-CG-06", K6 + "crushgap.py", "if g_units >= FILTER_UNITS:", "if g_units > FILTER_UNITS:", CG, "non-strict >="),
    ("A-CG-07", K6 + "crushgap.py", "if g_units <= -FILTER_UNITS:", "if g_units < -FILTER_UNITS:", CG, "non-strict <="),
    ("A-CG-08", K6 + "crushgap.py", "if day not in GRAIN_FULL_SESSIONS:", "if day not in GRAIN_TRADE_DATES:", CG, "C4 full-session table"),
    ("A-CG-09", K6 + "crushgap.py", "if last is None or last[0] != prev:", "if last is None or last[0] > prev:", CG, "13:14 bar is d-1's (K6-L-04)"),
    ("A-CG-10", K6 + "crushgap.py", "if close_id != bar.instrument_id:", "if False:", CG, "per-leg instrument guard"),
    ("A-CG-11", K6 + "crushgap.py", "EXIT_BEFORE_C_MIN = 2  #", "EXIT_BEFORE_C_MIN = 1  #", CG, "exit 13:13"),
    ("A-CG-12", K6 + "crushgap.py", "if opened.date() != day or opened.time() != zs.o:", "if opened.date() != day or opened.time() != shift(zs.o, 1):", CG, "entry on the 08:30 bar"),
    ("A-CG-13", K6 + "crushgap.py", 'return to_ticks(asdict(bar)["open"], tick)', 'return to_ticks(asdict(bar)["close"], tick)', CG, "08:30 OPEN"),
    ("A-CG-14", K6 + "crushgap.py", "close = to_ticks(bar.close, self._facts[r].tick)", 'close = to_ticks(asdict(bar)["open"], self._facts[r].tick)', CG, "13:14 CLOSE"),
    ("A-CG-15", K6 + "crushgap.py", "CLOSE_BEFORE_C_MIN = 1", "CLOSE_BEFORE_C_MIN = 2", CG, "13:14 bar"),
    ("A-CG-16", K6 + "crushgap.py", "if bar is None:\n                return None  # K6-L-05: a missing 08:30 bar on any leg", "if bar is None:\n                continue  # K6-L-05: a missing 08:30 bar on any leg", CG, "missing 08:30 bar on a signal leg"),
    ("A-CG-17", K6 + "crushgap.py", "if opened.date() == bar.trade_date and opened.time() == self._close_at[r]:", "if opened.time() == self._close_at[r]:", CG, "13:14 bar on its trade date's CT date"),
    # ---- _port_common
    ("A-PC-01", K6 + "_port_common.py", "if opened.date() != day or opened.time() < exit_at:", "if opened.date() != day or opened.time() <= exit_at:", ALL_A, "exit at or after C-2"),
    ("A-PC-02", K6 + "_port_common.py", 'side = "sell" if position > 0 else "buy"\n    return (leg_market_intent(view, root, side, abs(position)),)', 'side = "buy" if position > 0 else "sell"\n    return (leg_market_intent(view, root, side, abs(position)),)', ALL_A, "exit side"),
    ("A-PC-03", K6 + "_port_common.py", "if position == 0 or account.pending.get(root, 0):", "if position == 0:", ALL_A, "no exit while pending"),
    ("A-PC-04", K6 + "_port_common.py", "return round(Decimal(repr(price)) / tick)", "return int(Decimal(repr(price)) / tick)", ALL_A, "round vs truncate (expected equivalent on-grid)"),
    # ---- limitcont
    ("B-LC-01", K6 + "limitcont.py", "ENTRY_BAR = time(8, 44)", "ENTRY_BAR = time(8, 45)", LC, "entry bar 08:44"),
    ("B-LC-02", K6 + "limitcont.py", "EXIT_LEAD_MINUTES = 2", "EXIT_LEAD_MINUTES = 1", LC, "exit C-2"),
    ("B-LC-03", K6 + "limitcont.py", "if moved_exactly(s1, s2, l1, self._tick):\n            return BUY\n        if moved_exactly(s1, s2, -l1, self._tick):\n            return SELL", "if moved_exactly(s1, s2, l1, self._tick):\n            return SELL\n        if moved_exactly(s1, s2, -l1, self._tick):\n            return BUY", LC, "direction"),
    ("B-LC-04", K6 + "limitcont.py", "if moved_exactly(s2, s3, l2, self._tick) or moved_exactly(s2, s3, -l2, self._tick):", "if False:", LC, "d-2 guard (K6-L-07)"),
    ("B-LC-05", K6 + "limitcont.py", "if d1 in self._dropped or d2 in self._dropped:", "if False:", LC, "R-1b-2 dropped dates"),
    ("B-LC-06", K6 + "limitcont.py", "or d not in LIVESTOCK_FULL_SESSIONS:", "or d not in LIVESTOCK_TRADE_DATES:", LC, "C4 full-session table"),
    ("B-LC-07", K6 + "limitcont.py", "if value is None or ids != {c}:", "if value is None:", LC, "S's bars carry c"),
    ("B-LC-08", K6 + "limitcont.py", "return (nn * od - on * nd) * td == ticks * tn * nd * od", "return abs((nn * od - on * nd) * td - ticks * tn * nd * od) <= tn * nd * od", LC, "exact equality (K6-L-08)"),
    ("B-LC-09", K6 + "limitcont.py", "if first <= day <= last:", "if first < day <= last:", LC + TB, "period boundary"),
    ("B-LC-10", K6 + "limitcont.py", "if halt is None or halt > end:", "if True:", LC + TB, "early-halt window"),
    ("B-LC-11", K6 + "limitcont.py", "if ts_ns >= self.lo_ns and volume > 0:", "if ts_ns >= self.lo_ns and volume >= 0:", LC, "volume > 0 in the VWAP"),
    ("B-LC-12", K6 + "limitcont.py", "if bar.ts_event_ns == ct_open_ns(d, self._open):", "if bar.ts_event_ns == ct_open_ns(d, time(8, 31)):", LC, "c = the 08:30 bar's id"),
    ("B-LC-13", K6 + "limitcont.py", "if c is None or bar.instrument_id != c:", "if c is None:", LC, "entry bar carries c"),
    ("B-LC-14", K6 + "limitcont.py", "l1, l2 = limit_ticks(self.root, d1), limit_ticks(self.root, d2)", "l1, l2 = limit_ticks(self.root, d2), limit_ticks(self.root, d1)", LC, "L(d-1) for d-1's move"),
    ("B-LC-15", K6 + "limitcont.py", "if ts_ns >= self.end_ns:\n            return", "if ts_ns > self.end_ns:\n            return", LC, "window end exclusive"),
    ("B-LC-16", K6 + "limitcont.py", "lo = time(start.hour, start.minute)", "lo = start", LC, "window start floored to the minute"),
    ("B-LC-17", K6 + "limitcont.py", "return (leg_market_intent(view, self.root, side, self._q),)", "return (leg_market_intent(view, self.root, side, self._q + 1),)", LC, "size q_c"),
    # ---- wasdepre
    ("B-WP-01", K6 + "wasdepre.py", "ENTRY_BAR = time(10, 29)", "ENTRY_BAR = time(10, 30)", WD, "entry 10:29"),
    ("B-WP-02", K6 + "wasdepre.py", "EXIT_BAR = time(11, 14)", "EXIT_BAR = time(11, 15)", WD, "exit 11:14"),
    ("B-WP-03", K6 + "wasdepre.py", "DRIFT_START_BAR = time(8, 30)", "DRIFT_START_BAR = time(8, 31)", WD, "drift from the 08:30 open"),
    ("B-WP-04", K6 + "wasdepre.py", "side = BUY if drift > 0 else SELL", "side = SELL if drift > 0 else BUY", WD, "direction"),
    ("B-WP-05", K6 + "wasdepre.py", "if drift == 0:\n            return ()", "if False:\n            return ()", WD, "zero drift no trade"),
    ("B-WP-06", K6 + "wasdepre.py", "if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SESSIONS:", "if d not in GRAIN_FULL_SESSIONS:", WD, "WASDE dates only"),
    ("B-WP-07", K6 + "wasdepre.py", "if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SESSIONS:", "if not _wasde.is_wasde_date(d):", WD, "C4 full-session table"),
    ("B-WP-08", K6 + "wasdepre.py", "if bar.instrument_id != start_id:", "if False:", WD, "instrument guard"),
    ("B-WP-09", K6 + "wasdepre.py", "self._start = (price_ticks(bar_open(bar), self._tick), bar.instrument_id)", "self._start = (price_ticks(bar.close, self._tick), bar.instrument_id)", WD, "08:30 OPEN"),
    # ---- wasdepost
    ("B-WO-01", K6 + "wasdepost.py", "SIGNAL_BAR = time(10, 59)", "SIGNAL_BAR = time(11, 0)", WD, "signal 10:59"),
    ("B-WO-02", K6 + "wasdepost.py", "ENTRY_BAR = time(11, 14)", "ENTRY_BAR = time(11, 15)", WD, "entry 11:14"),
    ("B-WO-03", K6 + "wasdepost.py", "EXIT_BAR = time(13, 13)", "EXIT_BAR = time(13, 14)", WD, "exit 13:13"),
    ("B-WO-04", K6 + "wasdepost.py", "side = BUY if response > 0 else SELL", "side = SELL if response > 0 else BUY", WD, "direction"),
    ("B-WO-05", K6 + "wasdepost.py", "if response == 0:\n            return ()", "if False:\n            return ()", WD, "zero response no trade"),
    ("B-WO-06", K6 + "wasdepost.py", "if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SESSIONS:", "if d not in GRAIN_FULL_SESSIONS:", WD, "WASDE dates only"),
    ("B-WO-07", K6 + "wasdepost.py", "if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SESSIONS:", "if not _wasde.is_wasde_date(d):", WD, "C4 full-session table"),
    ("B-WO-08", K6 + "wasdepost.py", "if bar.instrument_id != signal_id:", "if False:", WD, "instrument guard"),
    ("B-WO-09", K6 + "wasdepost.py", "self._signal = (price_ticks(bar.close, self._tick), bar.instrument_id)", "self._signal = (price_ticks(bar_open(bar), self._tick), bar.instrument_id)", WD, "10:59 CLOSE (needs bar_open import: expect crash-kill or NameError)"),
    # ---- _event_common
    ("B-EC-01", K6 + "_event_common.py", "if bar is None or not position or exit_ns is None or bar.ts_event_ns < exit_ns:", "if bar is None or not position or exit_ns is None or bar.ts_event_ns <= exit_ns:", ALL_B, "exit at or after the named bar"),
    ("B-EC-02", K6 + "_event_common.py", "side = SELL if position > 0 else BUY", "side = BUY if position > 0 else SELL", ALL_B, "exit side"),
    ("B-EC-03", K6 + "_event_common.py", "if pending and (pending > 0) != (position > 0):", "if False:", ALL_B, "no duplicate exit while one is pending"),
    # ---- tables
    ("B-TB-01", K6 + "_wasde.py", '"2025-11-14",', '"2025-11-10",', TB + WD, "moved WASDE date"),
    ("B-TB-02", K6 + "_limits.py", "        date(2026, 6, 18): _LE_DROP_REASON,\n", "", TB + LC, "a dropped LE date"),
    ("B-TB-03", K6 + "_calendar.py", '    ("2025-12-24", "early halt 12:05; F 11:45"),\n', '', TB + CG, "the grain not-full row 2025-12-24 removed (the livestock row reads 12:15, so the string is unique)"),
]


import os

# Second pass (item 12): MUT_K="<pytest -k expression>" deselects the literal-pin tests so a kill
# must come from a behavioural test; MUT_OUT names a separate log file.
EXTRA_K = os.environ.get("MUT_K", "")
if os.environ.get("MUT_OUT"):
    OUT = MAIN / "reports/stage_e8_briefs/audit_k6" / os.environ["MUT_OUT"]


def run_tests(tests: tuple[str, ...]) -> tuple[str, int, str]:
    cmd = ["nice", "-n", "10", str(PY), "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
           "--no-header", *(["-k", EXTRA_K] if EXTRA_K else []), *tests]
    env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(COPY),
           "HOME": "/home/kiros-li"}
    t0 = time.time()
    p = subprocess.run(cmd, cwd=COPY, env=env, capture_output=True, text=True, timeout=900)
    out = p.stdout + p.stderr
    tail = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
    first = ""
    for ln in out.splitlines():
        if ln.startswith("FAILED") or "Error" in ln and "::" in ln:
            first = ln.strip()[:160]
            break
    return ("killed" if p.returncode != 0 else "survived"), round(time.time() - t0, 1), (first or tail[0])[:200]


def main() -> None:
    only = set(sys.argv[1:])
    rows = []
    with OUT.open("a", encoding="utf-8") as log:
        for mid, rel, old, new, tests, what in MUTANTS:
            if only and mid not in only:
                continue
            pristine = (MAIN / rel).read_text(encoding="utf-8")
            n = pristine.count(old)
            target = COPY / rel
            if n != 1:
                rec = {"id": mid, "file": rel, "what": what, "result": f"skipped: old string occurs {n} times"}
                print(f"{mid:8s} {rec['result']}")
                rows.append(rec)
                log.write(json.dumps(rec) + "\n")
                continue
            try:
                target.write_text(pristine.replace(old, new), encoding="utf-8")
                result, secs, note = run_tests(tests)
            finally:
                target.write_text(pristine, encoding="utf-8")
            rec = {"id": mid, "file": rel, "what": what, "old": old, "new": new,
                   "tests": tests, "result": result, "seconds": secs, "note": note}
            rows.append(rec)
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"{mid:8s} {result:8s} {secs:6.1f}s  {what}  | {note[:90]}")
    killed = sum(r["result"] == "killed" for r in rows)
    survived = [r["id"] for r in rows if r["result"] == "survived"]
    skipped = [r["id"] for r in rows if r["result"].startswith("skipped")]
    print(f"TOTAL {len(rows)}: killed {killed}, survived {len(survived)} {survived}, skipped {skipped}")


if __name__ == "__main__":
    main()
