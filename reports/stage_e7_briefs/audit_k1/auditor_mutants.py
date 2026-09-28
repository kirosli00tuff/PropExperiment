"""Stage E.7 Task 3 audit (MemberAuditor-K1-FableXHigh): the auditor's own mutant sweep over the K1
member modules (brief item 12). Independent of the coders' mutant lists.

Every mutant is applied in a scratch MIRROR of the repository under the session scratchpad: every
top-level entry is a symlink to the repository except strategy/ and tests/, which are real
directories whose children are symlinks except strategy/members/k1 (a real copy) and the seven
tests/test_k1_members*.py files (real copies, so that their REPO = parents[1] is the mirror). The
repository's own files are never written. The mirror's K1 copies are restored after each mutant
and their sha256 checked against the repository at the end.

Run: nice -n 10 uv run python reports/stage_e7_briefs/audit_k1/auditor_mutants.py
Results: auditor_mutants_result.jsonl and auditor_mutants_summary.md next to this script.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCRATCH = Path("/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/"
               "99bb7678-38d8-413c-82c8-d103cf2d3163/scratchpad")
MIRROR = SCRATCH / "auditor_mut_repo"
PYC = SCRATCH / "auditor_mut_pyc"
PYTHON = REPO / ".venv" / "bin" / "python"
K1 = "strategy/members/k1"
PDT = ZoneInfo("America/Vancouver")

PORTS = ["tests/test_k1_members_ports.py", "tests/test_k1_members_ports_cp2.py",
         "tests/test_k1_members_ports_cp3.py", "tests/test_k1_members_ports_events.py"]
VXN = ["tests/test_k1_members_vxnband.py", "tests/test_k1_members_tables.py"]
VWAP = ["tests/test_k1_members_vwap.py"]
COMMON = ["tests/test_k1_members_vxnband.py", "tests/test_k1_members_vwap.py"]
TABLES = ["tests/test_k1_members_tables.py", "tests/test_k1_members_vxnband.py",
          "tests/test_k1_members_vwap.py"]

# (id, file, old, new, tests, what it changes)
MUTANTS: list[tuple[str, str, str, str, list[str], str]] = [
    # _port_common.py
    ("PC-1", "_port_common.py", "opened.time() < exit_at", "opened.time() <= exit_at", PORTS,
     "exit one minute late (14:59 instead of 14:58)"),
    ("PC-2", "_port_common.py", 'side = "sell" if position > 0 else "buy"',
     'side = "buy" if position > 0 else "sell"', PORTS, "exit side flipped"),
    ("PC-3", "_port_common.py", "return round(Decimal(repr(price)) / tick)",
     "return int(Decimal(repr(price)) / tick)", PORTS, "ticks by truncation"),
    ("PC-4", "_port_common.py", "return account.position(root) == 0 and not account.pending.get(root, 0)",
     "return account.position(root) == 0", PORTS, "is_flat ignores pending"),
    ("PC-5", "_port_common.py", "if position == 0 or account.pending.get(root, 0):",
     "if position == 0:", PORTS, "exit sent while an order is pending"),
    ("PC-6", "_port_common.py", "if opened.date() != day or opened.time() < exit_at:",
     "if opened.time() < exit_at:", PORTS, "exit bar not tied to CT date d"),
    # cp1.py
    ("C1-1", "cp1.py", "SIGNAL_AFTER_O_MIN = 29", "SIGNAL_AFTER_O_MIN = 28", PORTS, "signal bar 08:58"),
    ("C1-2", "cp1.py", "ENTRY_BEFORE_C_MIN = 31", "ENTRY_BEFORE_C_MIN = 30", PORTS, "entry bar 14:30"),
    ("C1-3", "cp1.py", "EXIT_BEFORE_C_MIN = 2  # the first bar at or after C-2 = 14:58",
     "EXIT_BEFORE_C_MIN = 1  # the first bar at or after C-2 = 14:58", PORTS, "exit bar 14:59"),
    ("C1-4", "cp1.py", "GLOBEX_OPEN_CT = time(17, 0)", "GLOBEX_OPEN_CT = time(17, 1)", PORTS,
     "first bar 17:01"),
    ("C1-5", "cp1.py", "s = signal_close - first_open", "s = first_open - signal_close", PORTS,
     "signal sign flipped"),
    ("C1-6", "cp1.py", "if s == 0:\n            return None  # zero signal",
     "if s == 0:\n            return \"buy\"  # zero signal", PORTS, "zero signal buys"),
    ("C1-7", "cp1.py", "if first_id != signal_id:\n            return None",
     "if False:\n            return None", PORTS, "signal-bar instrument guard removed"),
    ("C1-8", "cp1.py", 'return "buy" if s > 0 else "sell"', 'return "sell" if s > 0 else "buy"',
     PORTS, "direction flipped"),
    ("C1-9", "cp1.py", "if opened.date() == day - ONE_DAY and at == GLOBEX_OPEN_CT:",
     "if opened.date() == day - ONE_DAY and at >= GLOBEX_OPEN_CT:", PORTS,
     "first bar = the last evening bar"),
    ("C1-10", "cp1.py", "self._entered = True  # the one entry decision of the trade date",
     "pass  # the one entry decision of the trade date", PORTS, "entry decision repeatable"),
    ("C1-11", "cp1.py", "return (leg_market_intent(view, self.root, side, self._leg.q),)",
     "return (leg_market_intent(view, self.root, side, 1),)", PORTS, "size literal 1 (not q_c)"),
    ("C1-12", "cp1.py", "self._signal = (to_ticks(bar.close, self._leg.tick), bar.instrument_id)",
     "self._signal = (to_ticks(asdict(bar)[\"open\"], self._leg.tick), bar.instrument_id)", PORTS,
     "signal uses the 08:59 open"),
    ("C1-13", "cp1.py", "if at != self._entry_at or self._entered or not is_flat(account, self.root):",
     "if at != self._entry_at or self._entered:", PORTS, "entry while not flat"),
    # cp2.py
    ("C2-1", "cp2.py", "RANGE_MINUTES = 15", "RANGE_MINUTES = 14", PORTS, "range [08:30, 08:44)"),
    ("C2-2", "cp2.py", "BUFFER_TICKS = 4", "BUFFER_TICKS = 3", PORTS, "buffer 3 ticks"),
    ("C2-3", "cp2.py", "HOLD_BARS = 75", "HOLD_BARS = 74", PORTS, "hold 74 bars"),
    ("C2-4", "cp2.py", "if close >= to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:",
     "if close > to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:", PORTS, "buy compare strict"),
    ("C2-5", "cp2.py", "elif close <= to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:",
     "elif close < to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:", PORTS, "sell compare strict"),
    ("C2-6", "cp2.py", 'side = "buy"\n        elif', 'side = "sell"\n        elif', PORTS,
     "up-break sells"),
    ("C2-7", "cp2.py", "if not self._range_end <= at < self._leg.c or not is_flat(account, self.root):",
     "if not self._range_end <= at <= self._leg.c or not is_flat(account, self.root):", PORTS,
     "entry allowed on the 15:00 bar"),
    ("C2-8", "cp2.py", "if self._held < HOLD_BARS or account.pending.get(self.root, 0):",
     "if self._held <= HOLD_BARS or account.pending.get(self.root, 0):", PORTS, "exit on the 76th bar"),
    ("C2-9", "cp2.py", "self._triggered = True  # one entry per trade date, even if the engine refuses it",
     "pass  # one entry per trade date, even if the engine refuses it", PORTS, "re-entry allowed"),
    ("C2-10", "cp2.py", "self._hi = bar.high if self._hi is None else max(self._hi, bar.high)",
     "self._hi = bar.close if self._hi is None else max(self._hi, bar.close)", PORTS,
     "range high from closes"),
    ("C2-11", "cp2.py", "if self._leg.o <= at < self._range_end:", "if self._leg.o < at < self._range_end:",
     PORTS, "08:30 bar not a range bar"),
    ("C2-12", "cp2.py", "if self._held < HOLD_BARS or account.pending.get(self.root, 0):\n            return ()",
     "if self._held < HOLD_BARS:\n            return ()", PORTS, "hold exit sent while pending"),
    ("C2-13", "cp2.py", "if opened.date() != bar.trade_date:\n            return ()  # the evening",
     "if False:\n            return ()  # the evening", PORTS, "evening bars enter the range"),
    # cp3.py
    ("C3-1", "cp3.py", 'CLV_BUY_AT_OR_ABOVE = Decimal("0.8")', 'CLV_BUY_AT_OR_ABOVE = Decimal("0.81")',
     PORTS, "buy cut 0.81"),
    ("C3-2", "cp3.py", 'CLV_SELL_AT_OR_BELOW = Decimal("0.2")', 'CLV_SELL_AT_OR_BELOW = Decimal("0.19")',
     PORTS, "sell cut 0.19"),
    ("C3-3", "cp3.py", "CLOSE_BEFORE_C_MIN = 1", "CLOSE_BEFORE_C_MIN = 2", PORTS, "C_d = 14:58 close"),
    ("C3-4", "cp3.py", "EXIT_BEFORE_C_MIN = 2  # the first bar at or after C-2 = 14:58",
     "EXIT_BEFORE_C_MIN = 1  # the first bar at or after C-2 = 14:58", PORTS, "exit bar 14:59"),
    ("C3-5", "cp3.py", "if num * buy_d >= buy_n * span:", "if num * buy_d > buy_n * span:", PORTS,
     "buy compare strict"),
    ("C3-6", "cp3.py", "if num * sell_d <= sell_n * span:", "if num * sell_d < sell_n * span:", PORTS,
     "sell compare strict"),
    ("C3-7", "cp3.py", 'return "buy"\n    if num * sell_d', 'return "sell"\n    if num * sell_d', PORTS,
     "high CLV sells"),
    ("C3-8", "cp3.py", "if span <= 0:\n        return None", "if span < 0:\n        return None", PORTS,
     "zero range allowed"),
    ("C3-9", "cp3.py", "if bar.early_halt_ct is not None:\n            return None  # an early-halt day d",
     "if False:\n            return None  # an early-halt day d", PORTS, "halt day d traded"),
    ("C3-10", "cp3.py", "if prior.instrument_id != bar.instrument_id:\n            return None",
     "if False:\n            return None", PORTS, "instrument guard removed"),
    ("C3-11", "cp3.py", "complete = (self._has_open_bar and self._close is not None and not self._halt",
     "complete = (self._has_open_bar and self._close is not None", PORTS, "halt day complete"),
    ("C3-12", "cp3.py", "and len(self._ids) == 1)", "and len(self._ids) >= 1)", PORTS,
     "two-id day complete"),
    ("C3-13", "cp3.py", "if at != self._leg.o or self._entered or not is_flat(account, self.root):",
     "if at < self._leg.o or self._entered or not is_flat(account, self.root):", PORTS,
     "entry on any bar from 08:30"),
    ("C3-14", "cp3.py", "self._lo = bar.low if self._lo is None else min(self._lo, bar.low)",
     "self._lo = bar.close if self._lo is None else min(self._lo, bar.close)", PORTS,
     "daily low from closes"),
    ("C3-15", "cp3.py", "if opened.date() != day:\n            return ()  # the evening",
     "if False:\n            return ()  # the evening", PORTS, "evening bars enter the daily bar"),
    # _event_common.py
    ("EC-1", "_event_common.py", "if minute != expected:", "if minute > expected + 1:", COMMON,
     "one-minute gaps allowed"),
    ("EC-2", "_event_common.py", "SELL if position > 0 else BUY, abs(position)",
     "BUY if position > 0 else SELL, abs(position)", COMMON, "close_items side flipped"),
    ("EC-3", "_event_common.py", "if position == 0 or account.pending.get(root, 0):\n        return ()",
     "if position == 0:\n        return ()", COMMON, "close_items while pending"),
    ("EC-4", "_event_common.py", "dict(zip(_TRADE_DATES[1:], _TRADE_DATES[:-1],",
     "dict(zip(_TRADE_DATES[2:], _TRADE_DATES[:-2],", COMMON, "d-2 instead of d-1"),
    ("EC-5", "_event_common.py", "return day in FULL_SESSIONS", "return True", COMMON,
     "every date a full session"),
    ("EC-6", "_event_common.py", "return (value > 0) - (value < 0)", "return (value < 0) - (value > 0)",
     COMMON, "sign flipped"),
    ("EC-7", "_event_common.py", "return account.position(root) == 0 and not account.pending.get(root, 0)",
     "return account.position(root) == 0", COMMON, "is_flat ignores pending"),
    # vxnband.py
    ("VB-1", "vxnband.py", "BAND_DIVISOR = 1600", "BAND_DIVISOR = 1500", VXN, "divisor 1500"),
    ("VB-2", "vxnband.py", "VXN_LOW_CUT = Decimal(20)", "VXN_LOW_CUT = Decimal(21)", VXN, "low cut 21"),
    ("VB-3", "vxnband.py", "VXN_HIGH_CUT = Decimal(30)", "VXN_HIGH_CUT = Decimal(29)", VXN, "high cut 29"),
    ("VB-4", "vxnband.py", "SCAN_END_CT = time(14, 29)", "SCAN_END_CT = time(14, 30)", VXN,
     "scan to 14:30"),
    ("VB-5", "vxnband.py", "HOLD_MINUTES = 30", "HOLD_MINUTES = 31", VXN, "hold 31"),
    ("VB-6", "vxnband.py", "CLOSE_BEFORE_C_MIN = 1", "CLOSE_BEFORE_C_MIN = 2", VXN, "C_prev = 14:58 close"),
    ("VB-7", "vxnband.py", "return v < VXN_LOW_CUT or v >= VXN_HIGH_CUT",
     "return v <= VXN_LOW_CUT or v >= VXN_HIGH_CUT", VXN, "low cut non-strict"),
    ("VB-8", "vxnband.py", "return v < VXN_LOW_CUT or v >= VXN_HIGH_CUT",
     "return v < VXN_LOW_CUT or v > VXN_HIGH_CUT", VXN, "high cut strict"),
    ("VB-9", "vxnband.py", "if move > width:\n        return SELL", "if move >= width:\n        return SELL",
     VXN, "upper breach non-strict"),
    ("VB-10", "vxnband.py", "if move < -width:\n        return BUY", "if move <= -width:\n        return BUY",
     VXN, "lower breach non-strict"),
    ("VB-11", "vxnband.py", "if move > width:\n        return SELL\n    if move < -width:\n        return BUY",
     "if move > width:\n        return BUY\n    if move < -width:\n        return SELL", VXN,
     "fade direction flipped"),
    ("VB-12", "vxnband.py", "return None if prior is None else _VXN.get(prior)",
     "return None if prior is None else _VXN.get(day)", VXN, "V of d itself (leak)"),
    ("VB-13", "vxnband.py", "if prior is None or prior.instrument_id != bar.instrument_id:",
     "if prior is None:", VXN, "instrument guard removed"),
    ("VB-14", "vxnband.py", "if side is not None:\n            self._searching = False",
     "if side is not None:\n            pass", VXN, "second entries allowed"),
    ("VB-15", "vxnband.py", "if self._exit_at is None or minute < self._exit_at:",
     "if self._exit_at is None or minute <= self._exit_at:", VXN, "exit one minute late"),
    ("VB-16", "vxnband.py", "self._searching = is_full_session(day)", "self._searching = True", VXN,
     "non-full sessions traded"),
    ("VB-17", "vxnband.py", "if minute == self._o:\n            self._setup = self._day_setup(bar)",
     "if self._setup is None:\n            self._setup = self._day_setup(bar)", VXN,
     "V read on a later bar when 08:30 fails"),
    ("VB-18", "vxnband.py", "self._close is None or self._halt\n", "self._close is None\n", VXN,
     "halt day complete for C_prev"),
    ("VB-19", "vxnband.py", "if not self._o <= minute < self._c:\n            return\n        self._ids",
     "if not self._o <= minute <= self._c:\n            return\n        self._ids", VXN,
     "15:00 bar in the id set"),
    ("VB-20", "vxnband.py", "if self._run is None or not self._run.see(minute):",
     "if False:", VXN, "gap check removed"),
    ("VB-21", "vxnband.py", "if setup is None or bar.instrument_id != setup.instrument_id:",
     "if setup is None:", VXN, "scan instrument change ignored"),
    ("VB-22", "vxnband.py", "if not self._searching or not self._o <= minute < self._scan_end:",
     "if not self._searching or not self._o < minute < self._scan_end:", VXN, "08:30 bar not scanned"),
    ("VB-23", "vxnband.py", "self._exit_at = minute + HOLD_MINUTES",
     "self._exit_at = minute + HOLD_MINUTES + 1", VXN, "exit at intent + 31"),
    ("VB-24", "vxnband.py", "if side is None or not is_flat(account, self.root):",
     "if side is None:", VXN, "entry while not flat"),
    ("VB-25", "vxnband.py", "return (leg_market_intent(view, self.root, side, self._leg.q),)",
     "return (leg_market_intent(view, self.root, side, 2),)", VXN, "size literal 2"),
    ("VB-26", "vxnband.py", "if opened.date() != self._day:\n            return ()  # the previous CT evening",
     "if False:\n            return ()  # the previous CT evening", VXN, "evening bars read"),
    ("VB-27", "vxnband.py", "if v is None or not in_regime(v):", "if v is None:", VXN,
     "regime filter removed"),
    # vwap.py
    ("VW-1", "vwap.py", "TP_PARTS = 3", "TP_PARTS = 2", VWAP, "TP parts 2"),
    ("VW-2", "vwap.py", "RULE_END_CT = time(14, 57)", "RULE_END_CT = time(14, 58)", VWAP, "rule to 14:58"),
    ("VW-3", "vwap.py", "EXIT_BEFORE_C_MIN = 2", "EXIT_BEFORE_C_MIN = 1", VWAP, "final exit 14:59"),
    ("VW-4", "vwap.py", "MAX_ENTRIES = 20", "MAX_ENTRIES = 21", VWAP, "cap 21"),
    ("VW-5", "vwap.py", "MIN_HOLD_MINUTES = 1", "MIN_HOLD_MINUTES = 0", VWAP, "exit on the fill bar"),
    ("VW-6", "vwap.py", "MIN_HOLD_MINUTES = 1", "MIN_HOLD_MINUTES = 2", VWAP, "exit from k+2"),
    ("VW-7", "vwap.py", "side = sign(TP_PARTS * close * self._sum_vol - self._sum_hlc_vol)",
     "side = sign(self._sum_hlc_vol - TP_PARTS * close * self._sum_vol)", VWAP, "sign flipped"),
    ("VW-8", "vwap.py", "if side != 0:\n            self._s = side", "self._s = side", VWAP,
     "tie resets the sign"),
    ("VW-9", "vwap.py", "hlc = to_ticks(bar.high, tick) + to_ticks(bar.low, tick) + close",
     "hlc = close + close + close", VWAP, "VWAP of closes"),
    ("VW-10", "vwap.py", "self._sum_vol += bar.volume", "self._sum_vol += 1", VWAP, "unweighted"),
    ("VW-11", "vwap.py", "can_enter = self._entries < MAX_ENTRIES and not self._gap and not self._id_changed",
     "can_enter = self._entries < MAX_ENTRIES and not self._id_changed", VWAP, "gap ignored"),
    ("VW-12", "vwap.py", "can_enter = self._entries < MAX_ENTRIES and not self._gap and not self._id_changed",
     "can_enter = self._entries < MAX_ENTRIES and not self._gap", VWAP, "id change ignored for entries"),
    ("VW-13", "vwap.py", "or bar.ts_event_ns < self._held_from_ns + MIN_HOLD_MINUTES * NS_PER_MINUTE):",
     "or bar.ts_event_ns <= self._held_from_ns + MIN_HOLD_MINUTES * NS_PER_MINUTE):", VWAP,
     "hold one bar longer"),
    ("VW-14", "vwap.py", "if not can_enter:\n            return (exit_item,)",
     "if False:\n            return (exit_item,)", VWAP, "reversal leg despite the cap"),
    ("VW-15", "vwap.py", "if position and (self._id_changed or minute >= self._final_exit):",
     "if position and (self._id_changed or minute > self._final_exit):", VWAP, "final exit 14:59"),
    ("VW-16", "vwap.py", "if minute >= self._rule_end or self._sum_vol == 0:",
     "if minute > self._rule_end or self._sum_vol == 0:", VWAP, "rule on the 14:57 bar"),
    ("VW-17", "vwap.py", "self._entries += 1  # counted when sent (K1-L-08)",
     "pass  # counted when sent (K1-L-08)", VWAP, "entries never counted"),
    ("VW-18", "vwap.py", "if minute < self._o:\n            return ()", "if False:\n            return ()",
     VWAP, "VWAP from bars before 08:30"),
    ("VW-19", "vwap.py", "self._day, self._active = day, is_full_session(day)",
     "self._day, self._active = day, True", VWAP, "non-full sessions traded"),
    ("VW-20", "vwap.py", "BUY if direction > 0 else SELL", "SELL if direction > 0 else BUY", VWAP,
     "entry direction flipped"),
    ("VW-21", "vwap.py", "if s == 0 or sign(position) == s:\n            return ()",
     "if s == 0 or sign(position) != s:\n            return ()", VWAP, "reverse on the same sign"),
    ("VW-22", "vwap.py", "if position != self._seen_position:", "if True:", VWAP,
     "hold restarts every bar"),
    ("VW-23", "vwap.py", "if position and (self._id_changed or minute >= self._final_exit):",
     "if position and (minute >= self._final_exit):", VWAP, "no instrument-change exit"),
    ("VW-24", "vwap.py", "if account.pending.get(self.root, 0):\n            return ()  # no intent while",
     "if False:\n            return ()  # no intent while", VWAP, "intents while pending"),
    ("VW-25", "vwap.py", "return (exit_item, self._entry(view, s))", "return (self._entry(view, s), exit_item)",
     VWAP, "reversal order entry-then-exit"),
    ("VW-26", "vwap.py", "if position == 0:\n            if s == 0 or not can_enter:",
     "if position == 0:\n            if not can_enter:", VWAP, "flat entry on s = 0"),
    ("VW-27", "vwap.py", "if self._sum_vol == 0:\n            return  # no action on this bar",
     "if False:\n            return  # no action on this bar", VWAP, "sum(vol) = 0 acts (sign 0)"),
    ("VW-28", "vwap.py", "if not self._active or opened.date() != self._day:",
     "if not self._active:", VWAP, "evening bars read"),
    ("VW-29", "vwap.py", "if minute == self._o:\n            self._ref_id = bar.instrument_id",
     "if self._ref_id is None:\n            self._ref_id = bar.instrument_id", VWAP,
     "reference id from the first bar"),
    # tables
    ("CAL-1", "_calendar.py", '"2025-05-21", ', '', TABLES, "a full session removed from both tables"),
    ("VX-1", "_vxn.py", '("2019-04-30", "16.600000")', '("2019-04-30", "16.610000")', TABLES,
     "one CLOSE string changed"),
    ("VX-2", "_vxn.py", '("2021-04-05", ', '("2021-04-02", "17.000000"), ("2021-04-05", ', TABLES,
     "a dropped row put back"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_mirror() -> None:
    if MIRROR.exists():
        shutil.rmtree(MIRROR)
    MIRROR.mkdir(parents=True)
    skip = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "strategy", "tests"}
    for entry in REPO.iterdir():
        if entry.name in skip:
            continue
        (MIRROR / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())
    (MIRROR / "strategy").mkdir()
    for entry in (REPO / "strategy").iterdir():
        if entry.name == "__pycache__":
            continue
        if entry.name != "members":
            (MIRROR / "strategy" / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())
    (MIRROR / "strategy" / "members").mkdir()
    for entry in (REPO / "strategy" / "members").iterdir():
        if entry.name == "__pycache__":
            continue
        if entry.name != "k1":
            (MIRROR / "strategy" / "members" / entry.name).symlink_to(
                entry, target_is_directory=entry.is_dir())
    (MIRROR / K1).mkdir()
    for entry in (REPO / K1).glob("*.py"):
        shutil.copyfile(entry, MIRROR / K1 / entry.name)
    (MIRROR / "tests").mkdir()
    for entry in (REPO / "tests").iterdir():
        if entry.name == "__pycache__":
            continue
        if entry.name.startswith("test_k1_members"):
            shutil.copyfile(entry, MIRROR / "tests" / entry.name)
        else:
            (MIRROR / "tests" / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())


def run_tests(files: list[str]) -> tuple[int, int, list[str], float]:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPYCACHEPREFIX=str(PYC),
               PYTHONPATH=str(MIRROR))
    t0 = time.time()
    proc = subprocess.run([str(PYTHON), "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=no",
                           "-rf", *files], cwd=MIRROR, env=env, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    failed = [line.split()[1] for line in out.splitlines() if line.startswith("FAILED ")]
    m_f = re.search(r"(\d+) failed", out)
    m_p = re.search(r"(\d+) passed", out)
    errors = len(re.findall(r"(\d+) errors?", out))
    n_failed = int(m_f.group(1)) if m_f else 0
    if errors and not m_f:
        n_failed = -1  # collection error: treat as killed but flag
    return n_failed, int(m_p.group(1)) if m_p else 0, failed, time.time() - t0


def main() -> None:
    build_mirror()
    originals = {p.name: p.read_bytes() for p in (REPO / K1).glob("*.py")}
    results_path = HERE / "auditor_mutants_result.jsonl"
    results_path.write_text("", encoding="utf-8")
    started = datetime.now(PDT)
    print(f"start {started:%H:%M:%S} PDT, {len(MUTANTS)} mutants, mirror {MIRROR}", flush=True)
    # baseline
    for name, files in (("ports", PORTS), ("vxn", VXN), ("vwap", VWAP), ("tables", TABLES)):
        nf, np_, failed, secs = run_tests(files)
        print(f"baseline {name}: failed {nf} passed {np_} in {secs:.0f}s {failed[:3]}", flush=True)
        assert nf == 0 and np_ > 0, (name, nf, np_, failed)
    rows = []
    for mid, fname, old, new, files, what in MUTANTS:
        target = MIRROR / K1 / fname
        src = originals[fname].decode("utf-8")
        count = src.count(old)
        if count != 1:
            row = {"id": mid, "file": fname, "what": what, "status": f"PATTERN x{count}"}
            rows.append(row)
            results_path.open("a").write(json.dumps(row) + "\n")
            print(f"{mid}: pattern count {count}, skipped", flush=True)
            continue
        target.write_text(src.replace(old, new), encoding="utf-8")
        try:
            nf, np_, failed, secs = run_tests(files)
        finally:
            target.write_bytes(originals[fname])
        status = "killed" if nf != 0 else "SURVIVED"
        row = {"id": mid, "file": fname, "what": what, "status": status, "failed": nf,
               "passed": np_, "first_failing": failed[:3], "seconds": round(secs, 1)}
        rows.append(row)
        results_path.open("a").write(json.dumps(row) + "\n")
        print(f"{mid} {status} ({nf} failed) {what}: {failed[:1]}", flush=True)
    # restore check
    mismatch = [n for n, b in originals.items() if (MIRROR / K1 / n).read_bytes() != b]
    repo_ok = all(sha(REPO / K1 / n) == hashlib.sha256(b).hexdigest() for n, b in originals.items())
    ended = datetime.now(PDT)
    killed = sum(1 for r in rows if r["status"] == "killed")
    survived = [r for r in rows if r["status"] == "SURVIVED"]
    skipped = [r for r in rows if r["status"].startswith("PATTERN")]
    lines = [f"# Auditor mutant sweep (K1), {started:%Y-%m-%d %H:%M}-{ended:%H:%M} PDT",
             "", f"Mutants {len(rows)}: killed {killed}, survived {len(survived)}, "
             f"pattern-skipped {len(skipped)}. Mirror restored: {not mismatch}. "
             f"Repository K1 files unchanged: {repo_ok}.", "",
             "| Id | File | Change | Result | Failed | First killing test |", "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['id']} | {r['file']} | {r['what']} | {r['status']} | "
                     f"{r.get('failed', '')} | {(r.get('first_failing') or [''])[0]} |")
    (HERE / "auditor_mutants_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"done {ended:%H:%M:%S} PDT: killed {killed} survived {len(survived)} skipped {len(skipped)} "
          f"mirror_restored {not mismatch} repo_unchanged {repo_ok}", flush=True)
    for r in survived + skipped:
        print("  ", r["id"], r["status"], r["what"])
    sys.exit(0 if repo_ok and not mismatch else 1)


if __name__ == "__main__":
    main()
