"""Stage E.6 Task 3 audit: the mutant campaign (brief item 12). Each mutant is a one-place text
change applied to a COPY of strategy/members/k7 under the scratchpad; the K7 test files are run
against that copy through mutant_plugin.py (K7_MUTANT_DIR shadows the package). The repository
tree is never modified. Output: reports/stage_e6_briefs/audit_k7/mutants.json and mutants.md.

Run: PYTHONPATH=.:reports/stage_e6_briefs/audit_k7 nice -n 10 uv run python \
    reports/stage_e6_briefs/audit_k7/run_mutants.py [mutant-id ...]
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
K7 = REPO / "strategy" / "members" / "k7"
AUDIT = REPO / "reports" / "stage_e6_briefs" / "audit_k7"
SCRATCH = Path("/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/"
               "0f52aad4-207e-43da-84df-b6a0ead28371/scratchpad/mut")
PORT_TESTS = ["tests/test_k7_members_ports.py", "tests/test_k7_members_ports_cp2.py",
              "tests/test_k7_members_ports_cp3.py"]
EVENT_TESTS = ["tests/test_k7_members_events.py", "tests/test_k7_members_events_rev2h.py",
               "tests/test_k7_members_events_montrend.py"]
ALL_TESTS = PORT_TESTS + EVENT_TESTS

# (id, file, old, new, what it tests)
MUTANTS: list[tuple[str, str, str, str, str]] = [
    # ---- CP1 (cp1.py)
    ("cp1-signal-29", "cp1.py", "SIGNAL_AFTER_O_MIN = 29", "SIGNAL_AFTER_O_MIN = 30",
     "signal bar O+29 (08:59)"),
    ("cp1-entry-31", "cp1.py", "ENTRY_BEFORE_C_MIN = 31", "ENTRY_BEFORE_C_MIN = 30",
     "entry bar C-31 (14:29)"),
    ("cp1-exit-2", "cp1.py", "EXIT_BEFORE_C_MIN = 2  # the first", "EXIT_BEFORE_C_MIN = 3  # the first",
     "exit bar C-2 (14:58)"),
    ("cp1-first-1700", "cp1.py", "GLOBEX_OPEN_CT = time(17, 0)", "GLOBEX_OPEN_CT = time(17, 1)",
     "first bar 17:00 on CT date d-1"),
    ("cp1-first-day", "cp1.py", "if opened.date() == day - ONE_DAY and at == GLOBEX_OPEN_CT:",
     "if at == GLOBEX_OPEN_CT:", "first bar by clock alone (K7-L-01)"),
    ("cp1-direction", "cp1.py", 'return "buy" if s > 0 else "sell"', 'return "sell" if s > 0 else "buy"',
     "direction with the signal"),
    ("cp1-zero", "cp1.py", "if s == 0:\n            return None  # zero signal",
     "if s == 0:\n            return 'buy'  # zero signal", "zero signal: no trade"),
    ("cp1-idguard", "cp1.py", "if first_id != signal_id:\n            return None",
     "if False:\n            return None", "two instrument_ids: no trade"),
    ("cp1-first-open", "cp1.py", 'return to_ticks(asdict(bar)["open"], tick)',
     'return to_ticks(asdict(bar)["close"], tick)', "signal uses the first bar's OPEN"),
    ("cp1-signal-close", "cp1.py", "self._signal = (to_ticks(bar.close, self._leg.tick), bar.instrument_id)",
     "self._signal = (to_ticks(bar.high, self._leg.tick), bar.instrument_id)",
     "signal uses the 08:59 CLOSE"),
    ("cp1-otherdate", "cp1.py", "if opened.date() != day:\n            return ()  # weekend",
     "if False:\n            return ()  # weekend", "bars of another CT date never read"),
    ("cp1-once", "cp1.py", "if at != self._entry_at or self._entered or not is_flat(account, self.root):",
     "if at != self._entry_at or not is_flat(account, self.root):", "one entry decision per date"),
    # ---- _port_common (exit plumbing)
    ("pc-exit-lt", "_port_common.py", "if opened.date() != day or opened.time() < exit_at:",
     "if opened.date() != day or opened.time() <= exit_at:", "exit at or AFTER the named bar"),
    ("pc-exit-date", "_port_common.py", "if opened.date() != day or opened.time() < exit_at:",
     "if opened.time() < exit_at:", "exit only on CT date d"),
    ("pc-exit-pending", "_port_common.py", "if position == 0 or account.pending.get(root, 0):\n        return ()\n    if opened",
     "if position == 0:\n        return ()\n    if opened", "no exit while an order is pending"),
    ("pc-ticks-trunc", "_port_common.py", "return round(Decimal(repr(price)) / tick)",
     "return int(Decimal(repr(price)) / tick)", "integer ticks by round()"),
    ("pc-flat-pending", "_port_common.py", "return account.position(root) == 0 and not account.pending.get(root, 0)",
     "return account.position(root) == 0", "flat means no pending order"),
    # ---- CP2 (cp2.py)
    ("cp2-range-15", "cp2.py", "RANGE_MINUTES = 15", "RANGE_MINUTES = 16", "range [O, O+15)"),
    ("cp2-buffer-3", "cp2.py", "BUFFER_TICKS = 4  #", "BUFFER_TICKS = 3  #", "buffer 4 ticks (20.00)"),
    ("cp2-buffer-5", "cp2.py", "BUFFER_TICKS = 4  #", "BUFFER_TICKS = 5  #", "buffer 4 ticks (20.00)"),
    ("cp2-hold-74", "cp2.py", "HOLD_BARS = 75", "HOLD_BARS = 74", "75-bar count"),
    ("cp2-hold-76", "cp2.py", "HOLD_BARS = 75", "HOLD_BARS = 76", "75-bar count"),
    ("cp2-hold-count-start", "cp2.py", "if self._triggered and account.position(self.root):\n            return self._hold_exit(view, account)",
     "if self._triggered and (account.position(self.root) or account.pending.get(self.root, 0)):\n            return self._hold_exit(view, account)",
     "count starts after the fill (present bars with a position)"),
    ("cp2-ge", "cp2.py", "if close >= to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:",
     "if close > to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:", "close >= OR_high + buffer"),
    ("cp2-le", "cp2.py", "elif close <= to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:",
     "elif close < to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:", "close <= OR_low - buffer"),
    ("cp2-direction", "cp2.py", '            side = "buy"\n        elif close <=', '            side = "sell"\n        elif close <=',
     "break direction"),
    ("cp2-elig-c", "cp2.py", "if not self._range_end <= at < self._leg.c or not is_flat(account, self.root):",
     "if not self._range_end <= at <= self._leg.c or not is_flat(account, self.root):", "no entry from C on"),
    ("cp2-elig-start", "cp2.py", "if not self._range_end <= at < self._leg.c or not is_flat(account, self.root):",
     "if not self._range_end < at < self._leg.c or not is_flat(account, self.root):", "the 08:45 bar is eligible"),
    ("cp2-range-end", "cp2.py", "if self._leg.o <= at < self._range_end:", "if self._leg.o <= at <= self._range_end:",
     "the 08:45 bar is not a range bar"),
    ("cp2-range-start", "cp2.py", "if self._leg.o <= at < self._range_end:", "if self._leg.o < at < self._range_end:",
     "the 08:30 bar is a range bar"),
    ("cp2-otherdate", "cp2.py", "if opened.date() != bar.trade_date:\n            return ()  # another CT date",
     "if False:\n            return ()  # another CT date", "bars of another CT date never read"),
    ("cp2-once", "cp2.py", "if self._triggered or self._hi is None or self._lo is None:",
     "if self._hi is None or self._lo is None:", "one entry per trade date"),
    ("cp2-c2exit", "cp2.py", "if self._held < HOLD_BARS or account.pending.get(self.root, 0):",
     "if (self._held < HOLD_BARS and ct_open(view.bar(self.root)).time() < shift(self._leg.c, -2)) or account.pending.get(self.root, 0):",
     "no C-2 exit (E.3-L-07)"),
    ("cp2-window-f", "cp2.py", "F_REGULAR_CT = time(15, 8)", "F_REGULAR_CT = time(15, 0)",
     "trading window to F 15:08"),
    # ---- CP3 (cp3.py)
    ("cp3-buy-079", "cp3.py", 'CLV_BUY_AT_OR_ABOVE = Decimal("0.8")', 'CLV_BUY_AT_OR_ABOVE = Decimal("0.79")',
     "CLV >= 0.8 buys"),
    ("cp3-buy-081", "cp3.py", 'CLV_BUY_AT_OR_ABOVE = Decimal("0.8")', 'CLV_BUY_AT_OR_ABOVE = Decimal("0.81")',
     "CLV >= 0.8 buys"),
    ("cp3-sell-021", "cp3.py", 'CLV_SELL_AT_OR_BELOW = Decimal("0.2")', 'CLV_SELL_AT_OR_BELOW = Decimal("0.21")',
     "CLV <= 0.2 sells"),
    ("cp3-sell-019", "cp3.py", 'CLV_SELL_AT_OR_BELOW = Decimal("0.2")', 'CLV_SELL_AT_OR_BELOW = Decimal("0.19")',
     "CLV <= 0.2 sells"),
    ("cp3-ge", "cp3.py", "if num * buy_d >= buy_n * span:", "if num * buy_d > buy_n * span:", "non-strict buy cut"),
    ("cp3-le", "cp3.py", "if num * sell_d <= sell_n * span:", "if num * sell_d < sell_n * span:", "non-strict sell cut"),
    ("cp3-direction", "cp3.py", '        return "buy"\n    if num * sell_d', '        return "sell"\n    if num * sell_d',
     "direction by CLV"),
    ("cp3-close-1", "cp3.py", "CLOSE_BEFORE_C_MIN = 1", "CLOSE_BEFORE_C_MIN = 2", "C_d = close of 14:59"),
    ("cp3-exit-2", "cp3.py", "EXIT_BEFORE_C_MIN = 2  # the first", "EXIT_BEFORE_C_MIN = 3  # the first",
     "exit bar C-2 (14:58)"),
    ("cp3-range0", "cp3.py", "if span <= 0:\n        return None", "if span < 0:\n        return None", "Range > 0"),
    ("cp3-halt-entry", "cp3.py", "if bar.early_halt_ct is not None:\n            return None  # an early-halt",
     "if False:\n            return None  # an early-halt", "an early-halt day d is not traded"),
    ("cp3-halt-complete", "cp3.py", "and not self._halt\n", "and True\n", "a halt day's bar is incomplete"),
    ("cp3-idguard", "cp3.py", "if prior.instrument_id != bar.instrument_id:\n            return None",
     "if False:\n            return None", "instrument guard d-1 vs the 08:30 bar"),
    ("cp3-oneid", "cp3.py", "and len(self._ids) == 1)", "and len(self._ids) >= 1)", "one instrument_id per daily bar"),
    ("cp3-needs-open", "cp3.py", "complete = (self._has_open_bar and self._close is not None",
     "complete = (self._close is not None", "the 08:30 bar must exist for a complete day"),
    ("cp3-needs-close", "cp3.py", "complete = (self._has_open_bar and self._close is not None",
     "complete = (self._has_open_bar and True", "the 14:59 bar must exist for a complete day"),
    ("cp3-otherdate", "cp3.py", "if opened.date() != day:\n            return ()  # another CT date",
     "if False:\n            return ()  # another CT date", "bars of another CT date never read"),
    ("cp3-window", "cp3.py", "if not self._leg.o <= at < self._leg.c:\n            return",
     "if not self._leg.o <= at <= self._leg.c:\n            return", "daily bar over [O, C)"),
    ("cp3-entry-bar", "cp3.py", "if at != self._leg.o or self._entered or not is_flat(account, self.root):",
     "if at != shift(self._leg.o, 1) or self._entered or not is_flat(account, self.root):", "entry on the 08:30 bar"),
    ("cp3-incomplete-used", "cp3.py", "if finished is not None:\n            self._prior = finished",
     "if self._hi is not None and self._lo is not None and self._close is not None and self._ids:\n            self._prior = finished or DailyBar(self._day, to_ticks(self._hi, self._leg.tick), to_ticks(self._lo, self._leg.tick), to_ticks(self._close, self._leg.tick), next(iter(self._ids)))",
     "incomplete days are dropped, never used as d-1"),
    # ---- expiry (expiry.py)
    ("exp-entry-300", "expiry.py", "ENTRY_FILL_BEFORE_T_MIN = 300", "ENTRY_FILL_BEFORE_T_MIN = 299",
     "entry bar T_exp - 301"),
    ("exp-exit-1", "expiry.py", "EXIT_FILL_BEFORE_T_MIN = 1", "EXIT_FILL_BEFORE_T_MIN = 2", "exit bar T_exp - 2"),
    ("exp-delay", "expiry.py", "ct_open_ns(day, t - ENTRY_FILL_BEFORE_T_MIN - FILL_DELAY_MIN)",
     "ct_open_ns(day, t - ENTRY_FILL_BEFORE_T_MIN)", "entry intent one bar before the fill"),
    ("exp-direction", "expiry.py", "return (leg_market_intent(view, self.root, BUY, self._leg.q),)",
     "return (leg_market_intent(view, self.root, 'sell', self._leg.q),)", "long only"),
    ("exp-dates", "expiry.py", "if not is_entry_date(day):\n            continue", "if False:\n            continue",
     "C4 exclusions (full sessions, vendor-degraded)"),
    ("exp-exit-early", "expiry.py", "if bar.ts_event_ns < self._exit_ns:\n                return ()",
     "if False:\n                return ()", "no exit before the exit bar"),
    ("exp-exact-bar", "expiry.py", "if times is None or bar.ts_event_ns != times[0] or not is_flat(account, self.root):",
     "if times is None or bar.ts_event_ns < times[0] or not is_flat(account, self.root):",
     "entry on the exact T_exp - 301 bar only"),
    ("exp-window", "expiry.py", "WINDOW_START_CT = time(5, 0)", "WINDOW_START_CT = time(6, 0)", "trading window (05:00, 11:00)"),
    # ---- rev2h (rev2h.py)
    ("rev-direction", "rev2h.py", "DIRECTION = -1", "DIRECTION = 1", "against sign(r)"),
    ("rev-block-119", "rev2h.py", "BLOCK_MINUTES = 120", "BLOCK_MINUTES = 119", "120-minute blocks"),
    ("rev-one-decision", "rev2h.py", "DECISION_BLOCKS = (1, 2)", "DECISION_BLOCKS = (1,)", "decisions at 10:30 and 12:30"),
    ("rev-final-1", "rev2h.py", "FINAL_EXIT_BEFORE_END_MIN = 1", "FINAL_EXIT_BEFORE_END_MIN = 2", "final exit on 14:29"),
    ("rev-sigend-1", "rev2h.py", "SIGNAL_END_BEFORE_T_MIN = 1", "SIGNAL_END_BEFORE_T_MIN = 2", "r closes on the t-1 bar"),
    ("rev-start", "rev2h.py", "decisions.append(Decision(ct_open_ns(day, t - BLOCK_MINUTES),",
     "decisions.append(Decision(ct_open_ns(day, t - BLOCK_MINUTES + 1),", "r opens on the block's first bar"),
    ("rev-dates", "rev2h.py", "if is_entry_date(self._day) else None)", "if True else None)",
     "C4 exclusions (full sessions, vendor-degraded)"),
    ("rev-window", "rev2h.py", "WINDOW_END_AFTER_BLOCKS_MIN = 1", "WINDOW_END_AFTER_BLOCKS_MIN = 0", "trading window to 14:31"),
    # ---- montrend (montrend.py)
    ("mon-direction", "montrend.py", "DIRECTION = 1  # momentum", "DIRECTION = -1  # momentum", "with s_t"),
    ("mon-first-1900", "montrend.py", "FIRST_DECISION = (SUNDAY_OFFSET_DAYS, time(18, 0))",
     "FIRST_DECISION = (SUNDAY_OFFSET_DAYS, time(19, 0))", "first decision Sunday 18:00"),
    ("mon-first-1700", "montrend.py", "FIRST_DECISION = (SUNDAY_OFFSET_DAYS, time(18, 0))",
     "FIRST_DECISION = (SUNDAY_OFFSET_DAYS, time(17, 0))", "no decision at Sunday 17:00"),
    ("mon-last-1400", "montrend.py", "LAST_DECISION = (0, time(13, 0))", "LAST_DECISION = (0, time(14, 0))",
     "last decision Monday 13:00"),
    ("mon-last-1200", "montrend.py", "LAST_DECISION = (0, time(13, 0))", "LAST_DECISION = (0, time(12, 0))",
     "20 decisions"),
    ("mon-step-30", "montrend.py", "STEP_MINUTES = 60", "STEP_MINUTES = 30", "hourly decisions"),
    ("mon-lookback-59", "montrend.py", "LOOKBACK_MINUTES = 60", "LOOKBACK_MINUTES = 59", "t - 60 open"),
    ("mon-sigend-1", "montrend.py", "SIGNAL_END_BEFORE_T_MIN = 1", "SIGNAL_END_BEFORE_T_MIN = 2", "t - 1 close"),
    ("mon-flat-1401", "montrend.py", "FLAT_AT = (0, time(14, 0))", "FLAT_AT = (0, time(14, 1))", "flat at 14:00"),
    ("mon-final-1", "montrend.py", "FINAL_EXIT_BEFORE_FLAT_MIN = 1", "FINAL_EXIT_BEFORE_FLAT_MIN = 0",
     "final exit on the 13:59 bar"),
    ("mon-weekday", "montrend.py", "MONDAY = 0", "MONDAY = 1", "Mondays only"),
    ("mon-dates", "montrend.py", "return day.weekday() == MONDAY and is_entry_date(day)",
     "return day.weekday() == MONDAY", "C4 exclusions (full sessions, vendor-degraded)"),
    ("mon-window", "montrend.py", "start = decision_minutes()[0] - LOOKBACK_MINUTES  # Sunday 17:00",
     "start = decision_minutes()[0]  # Sunday 17:00", "trading window from Sunday 17:00"),
    # ---- _event_common (DecisionBook)
    ("ec-hold", "_event_common.py", "if ts >= self.schedule.final_exit_ns or sign(position) != self._target:",
     "if ts >= self.schedule.final_exit_ns or self._entry is not None and self._entry[0] == self._next - 1 and ts == self.schedule.decisions[self._entry[0]].end_ns:",
     "hold on an equal target (flatten only on a sign change)"),
    ("ec-flatten-zero", "_event_common.py", "if ts >= self.schedule.final_exit_ns or sign(position) != self._target:",
     "if ts >= self.schedule.final_exit_ns or (self._target != 0 and sign(position) != self._target):",
     "s_t = 0 flattens"),
    ("ec-final-ge", "_event_common.py", "if ts >= self.schedule.final_exit_ns or sign(position) != self._target:",
     "if ts > self.schedule.final_exit_ns or sign(position) != self._target:", "final exit at or after the named bar"),
    ("ec-missed", "_event_common.py", "while self._next < len(decisions) and decisions[self._next].end_ns < ts:\n            self._target = 0",
     "while self._next < len(decisions) and decisions[self._next].end_ns < ts:\n            pass",
     "a missing t-1 bar gives target 0 (K7-L-08)"),
    ("ec-idguard", "_event_common.py", "if start is None or start[1] != bar.instrument_id:\n            target = 0",
     "if start is None:\n            target = 0", "signal endpoints with two ids: target 0"),
    ("ec-missing-start", "_event_common.py", "if start is None or start[1] != bar.instrument_id:\n            target = 0",
     "if start is not None and start[1] != bar.instrument_id:\n            target = 0\n        elif start is None:\n            target = self.direction * sign(to_ticks(bar.close, self.tick) - to_ticks(bar.close, self.tick) + 1)",
     "a missing start bar gives target 0"),
    ("ec-entry-id", "_event_common.py", "or bar.instrument_id != signal_id or not is_flat(account, self.root)):",
     "or not is_flat(account, self.root)):", "the entry bar carries the signal bars' id"),
    ("ec-entry-exact", "_event_common.py", "if (target == 0 or ts != self.schedule.decisions[index].entry_ns",
     "if (target == 0 or ts < self.schedule.decisions[index].entry_ns", "entry on the exact t bar only"),
    ("ec-entry-zero", "_event_common.py", "if (target == 0 or ts != self.schedule.decisions[index].entry_ns",
     "if (ts != self.schedule.decisions[index].entry_ns", "target 0: no entry"),
    ("ec-entry-flat", "_event_common.py", "or bar.instrument_id != signal_id or not is_flat(account, self.root)):",
     "or bar.instrument_id != signal_id or account.position(self.root)):", "entry only when flat (no pending)"),
    ("ec-close-pending", "_event_common.py", "if position == 0 or account.pending.get(root, 0):\n        return ()\n    return (leg_market_intent(view, root, SELL if position > 0 else BUY, abs(position)),)",
     "if position == 0:\n        return ()\n    return (leg_market_intent(view, root, SELL if position > 0 else BUY, abs(position)),)",
     "no flatten while an order is pending"),
    ("ec-close-side", "_event_common.py", "SELL if position > 0 else BUY, abs(position)", "BUY if position > 0 else SELL, abs(position)",
     "the flatten closes the position"),
    ("ec-start-open", "_event_common.py", "self._starts = {**self._starts, i: (open_ticks(bar, self.tick), bar.instrument_id)}",
     "self._starts = {**self._starts, i: (to_ticks(bar.close, self.tick), bar.instrument_id)}",
     "the signal uses the start bar's OPEN"),
    ("ec-end-close", "_event_common.py", "target = self.direction * sign(to_ticks(bar.close, self.tick) - start[0])",
     "target = self.direction * sign(open_ticks(bar, self.tick) - start[0])", "the signal uses the end bar's CLOSE"),
    ("ec-q", "_event_common.py", "return (leg_market_intent(view, self.root, BUY if target > 0 else SELL, self.q),)",
     "return (leg_market_intent(view, self.root, BUY if target > 0 else SELL, self.q + 1),)", "size q_c"),
    ("ec-ticks-trunc", "_event_common.py", "return round(Decimal(repr(price)) / tick)", "return int(Decimal(repr(price)) / tick)",
     "integer ticks by round()"),
    ("ec-entry-dates", "_event_common.py", "date.fromisoformat(d) for d in CRYPTO_FULL_SESSIONS if d not in frozenset(VENDOR_DEGRADED))",
     "date.fromisoformat(d) for d in CRYPTO_FULL_SESSIONS)", "ENTRY_DATES excludes VENDOR_DEGRADED"),
    # ---- _calendar (one row each)
    ("cal-full-drop", "_calendar.py", '"2025-06-02", ', "", "CRYPTO_FULL_SESSIONS row"),
    ("cal-degraded-drop", "_calendar.py", '"2026-04-10",\n)', ")", "VENDOR_DEGRADED row"),
    ("cal-mbtx-texp", "_calendar.py", '("2026-03-27", "11:00")', '("2026-03-27", "10:00")', "T_exp 11:00 on 2026-03-27"),
    ("cal-mbtx-drop", "_calendar.py", '("2025-09-26", "10:00"), ', "", "an MBTX row"),
    ("cal-mbtx-add", "_calendar.py",
     '("2026-01-30", "10:00"), ("2026-02-27", "10:00"), ("2026-03-27", "11:00"),',
     '("2025-12-26", "10:00"), ("2026-01-30", "10:00"), ("2026-02-27", "10:00"), ("2026-03-27", "11:00"),',
     "R-1b-1: CME's 2025-12-26 not added"),
]


def apply(mutant_dir: Path, file: str, old: str, new: str) -> None:
    shutil.copytree(K7, mutant_dir / "k7")
    target = mutant_dir / "k7" / file
    text = target.read_text(encoding="utf-8")
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{file}: pattern occurs {n} times: {old[:60]!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def run(mutant_dir: Path, tests: list[str]) -> tuple[str, list[str], int]:
    env = {**os.environ, "K7_MUTANT_DIR": str(mutant_dir),
           "PYTHONPATH": f"{REPO}:{AUDIT}"}
    cmd = ["nice", "-n", "10", "uv", "run", "pytest", "-q", "-p", "mutant_plugin",
           "-p", "no:cacheprovider", "-x" if False else "--no-header", *tests]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    failed = sorted(set(re.findall(r"^FAILED (\S+)", out, re.M)))
    errors = sorted(set(re.findall(r"^ERROR (\S+)", out, re.M)))
    summary = [ln for ln in out.splitlines() if re.search(r"\d+ (passed|failed|error)", ln)]
    return (summary[-1] if summary else out[-400:]), failed + errors, int(time.time() - t0)


def main(argv: list[str]) -> None:
    wanted = set(argv)
    results = []
    for mid, file, old, new, what in MUTANTS:
        if wanted and mid not in wanted:
            continue
        mdir = SCRATCH / mid
        if mdir.exists():
            shutil.rmtree(mdir)
        mdir.mkdir(parents=True)
        try:
            apply(mdir, file, old, new)
        except RuntimeError as exc:
            results.append({"id": mid, "file": file, "what": what, "status": "PATTERN-MISS",
                            "detail": str(exc)})
            print(mid, "PATTERN-MISS", exc, flush=True)
            continue
        tests = PORT_TESTS if file in ("cp1.py", "cp2.py", "cp3.py", "_port_common.py") else (
            ALL_TESTS if file == "_calendar.py" else EVENT_TESTS)
        summary, failed, secs = run(mdir, tests)
        status = "KILLED" if failed else "SURVIVED"
        results.append({"id": mid, "file": file, "what": what, "status": status,
                        "summary": summary, "killed_by": failed, "seconds": secs})
        print(f"{mid:22s} {status:9s} {summary[:70]}  by {len(failed)} tests", flush=True)
        shutil.rmtree(mdir, ignore_errors=True)
    out = AUDIT / "mutants.json"
    prev = json.loads(out.read_text()) if out.exists() and wanted else []
    keep = [r for r in prev if r["id"] not in {x["id"] for x in results}]
    out.write_text(json.dumps(keep + results, indent=1), encoding="utf-8")
    print("wrote", out, len(keep + results), "mutants")


if __name__ == "__main__":
    main(sys.argv[1:])
