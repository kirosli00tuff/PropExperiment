"""Auditor's mutant driver (Task 3 item 13). Each mutant replaces one unique source fragment of one
K8 module; the mutated text is written under audit_k8/mutants/ and installed by k8audit_mutplugin
through sys.modules, so no file under strategy/ or tests/ is modified. The six K8 test files run
per mutant; the sha256 of every K8 source and test file is checked unchanged at the end."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
AUDIT = REPO / "reports/stage_e9_briefs/audit_k8"
MUT_DIR = AUDIT / "mutants"
LOG_DIR = AUDIT / "mutlogs"
TESTS = [
    "tests/test_k8_members_tables.py", "tests/test_k8_members_flight.py",
    "tests/test_k8_members_flight_exits.py", "tests/test_k8_members_flight_engine.py",
    "tests/test_k8_members_oilcad.py", "tests/test_k8_members_wkndbtc.py",
]
MODULES = {
    "flight": "strategy/members/k8/flight.py",
    "oilcad": "strategy/members/k8/oilcad.py",
    "wkndbtc": "strategy/members/k8/wkndbtc.py",
    "_releases": "strategy/members/k8/_releases.py",
    "_calendar": "strategy/members/k8/_calendar.py",
}
GUARDED = [*MODULES.values(), *TESTS, "strategy/members/k8/__init__.py"]

# (id, module, what, old, new)
MUTANTS: list[tuple[str, str, str, str, str]] = [
    # ---------------------------------------------------------------- flight: literals and clocks
    ("AF01", "flight", "block clock starts 08:31", "BLOCK_CLOCK_START = time(8, 30)", "BLOCK_CLOCK_START = time(8, 31)"),
    ("AF02", "flight", "4-minute blocks", "BLOCK_MINUTES = 5", "BLOCK_MINUTES = 4"),
    ("AF03", "flight", "78 blocks", "BLOCKS = 77 ", "BLOCKS = 78 "),
    ("AF04", "flight", "76 blocks", "BLOCKS = 77 ", "BLOCKS = 76 "),
    ("AF05", "flight", "end bar t_k - 2", "END_BAR_BEFORE_T_MIN = 1 ", "END_BAR_BEFORE_T_MIN = 2 "),
    ("AF06", "flight", "start bar t_k - 5", "START_BAR_BEFORE_T_MIN = 6 ", "START_BAR_BEFORE_T_MIN = 5 "),
    ("AF07", "flight", "start bar t_k - 7", "START_BAR_BEFORE_T_MIN = 6 ", "START_BAR_BEFORE_T_MIN = 7 "),
    ("AF08", "flight", "19 reference dates", "REFERENCE_DATES = 20 ", "REFERENCE_DATES = 19 "),
    ("AF09", "flight", "21 reference dates", "REFERENCE_DATES = 20 ", "REFERENCE_DATES = 21 "),
    ("AF10", "flight", "n >= 1,199", "MIN_VALUES = 1200 ", "MIN_VALUES = 1199 "),
    ("AF11", "flight", "n >= 1,201", "MIN_VALUES = 1200 ", "MIN_VALUES = 1201 "),
    ("AF12", "flight", "tail 1/199", "TAIL_DIVISOR = 200 ", "TAIL_DIVISOR = 199 "),
    ("AF13", "flight", "m = floor(n/200)", "    m = (n + TAIL_DIVISOR - 1) // TAIL_DIVISOR", "    m = n // TAIL_DIVISOR"),
    ("AF14", "flight", "(m+1)-th smallest", "[m - 1]", "[m]"),
    ("AF15", "flight", "H30 intent T_e + 30", "H30_INTENT_AFTER_FILL_MIN = 29 ", "H30_INTENT_AFTER_FILL_MIN = 30 "),
    ("AF16", "flight", "H30 intent T_e + 28", "H30_INTENT_AFTER_FILL_MIN = 29 ", "H30_INTENT_AFTER_FILL_MIN = 28 "),
    ("AF17", "flight", "exit bar 15:05", "LAST_EXIT_BAR = time(15, 4)", "LAST_EXIT_BAR = time(15, 5)"),
    ("AF18", "flight", "exit bar 15:03", "LAST_EXIT_BAR = time(15, 4)", "LAST_EXIT_BAR = time(15, 3)"),
    # ---------------------------------------------------------------- flight: comparisons and arithmetic
    ("AF19", "flight", "float compare", "    lhs, rhs = a[0] * b[1], b[0] * a[1]", "    lhs, rhs = a[0] / a[1], b[0] / b[1]"),
    ("AF20", "flight", "c6 = 0 allowed", "    if c6 <= 0:\n        return None\n    return (c1 - c6, c6)", "    if c6 < 0:\n        return None\n    return (c1 - c6, c6)"),
    ("AF21", "flight", "r over c1", "    return (c1 - c6, c6)", "    return (c1 - c6, c1)"),
    ("AF22", "flight", "no r < 0 condition", "    return r[0] < 0 and compare(r, q) <= 0", "    return compare(r, q) <= 0"),
    ("AF23", "flight", "r < Q strict", "    return r[0] < 0 and compare(r, q) <= 0", "    return r[0] < 0 and compare(r, q) < 0"),
    ("AF24", "flight", "ticks truncated", "    return round(Decimal(repr(price)) / tick)", "    return int(Decimal(repr(price)) / tick)"),
    # ---------------------------------------------------------------- flight: guards and state
    ("AF25", "flight", "no MES instrument guard", "        if start_id != bar.instrument_id:", "        if False:"),
    ("AF26", "flight", "no MES CT-date check", "        if opened.date() != day:\n            return None  # the previous CT evening: no block bar of trade date d", "        if False:\n            return None"),
    ("AF27", "flight", "d need not be a FLIGHT date", "        if day not in _FLIGHT_SET:", "        if False:"),
    ("AF28", "flight", "no warm-up", "        if len(refs) < REFERENCE_DATES or self._first_day is None or refs[0] < self._first_day:", "        if len(refs) < REFERENCE_DATES:"),
    ("AF29", "flight", "fewer than 20 refs accepted", "        if len(refs) < REFERENCE_DATES or self._first_day is None or refs[0] < self._first_day:", "        if self._first_day is None or (refs and refs[0] < self._first_day):"),
    ("AF30", "flight", "C6 tests the entry-bar minute", "        if in_guard(TRADED, view.decision_ts_ns):", "        if in_guard(TRADED, view.ts_event_ns):"),
    ("AF31", "flight", "no C6", "        if in_guard(TRADED, view.decision_ts_ns):", "        if False:"),
    ("AF32", "flight", "C6 skip uses the day's entry", "            return ()  # C6: the fill minute t_k is guarded; skipped, the day's entry kept", "            self._done = True\n            return ()"),
    ("AF33", "flight", "missing entry bar does not end the day",
     "        self._done = True  # the first non-skipped trigger uses the day's entry (E.3-L-08)\n        bar = view.bar(TRADED)\n        if bar is None or bar.trade_date != day:\n            return ()  # K8-L-06: the entry bar at t_k - 1 is missing: no trade on d",
     "        bar = view.bar(TRADED)\n        if bar is None or bar.trade_date != day:\n            return ()\n        self._done = True"),
    ("AF34", "flight", "entry bar trade date unchecked", "        if bar is None or bar.trade_date != day:\n            return ()  # K8-L-06", "        if bar is None:\n            return ()  # K8-L-06"),
    ("AF35", "flight", "entry while pending", "        if account.position(TRADED) or account.pending.get(TRADED, 0):", "        if account.position(TRADED):"),
    ("AF36", "flight", "sells", '        return (leg_market_intent(view, TRADED, "buy", self._q_c),)', '        return (leg_market_intent(view, TRADED, "sell", self._q_c),)'),
    ("AF37", "flight", "q_c + 1", '        return (leg_market_intent(view, TRADED, "buy", self._q_c),)', '        return (leg_market_intent(view, TRADED, "buy", self._q_c + 1),)'),
    ("AF38", "flight", "every trigger enters", "        if self._done or self._q is None or r is None or not triggers(r, self._q):", "        if self._q is None or r is None or not triggers(r, self._q):"),
    ("AF39", "flight", "HEOD exits like H30", '        if self.variant == "HEOD":\n            return cap_ns', "        pass"),
    ("AF40", "flight", "H30 uncapped", "        return min(t_e_ns + H30_INTENT_AFTER_FILL_MIN * NS_PER_MIN, cap_ns)", "        return t_e_ns + H30_INTENT_AFTER_FILL_MIN * NS_PER_MIN"),
    ("AF41", "flight", "T_e one minute late", "            self._t_e_ns = view.ts_event_ns", "            self._t_e_ns = view.ts_event_ns + NS_PER_MIN"),
    ("AF42", "flight", "exit while pending", "        if bar is None or account.pending.get(TRADED, 0):\n            return ()\n        if self._exit_ns", "        if bar is None:\n            return ()\n        if self._exit_ns"),
    ("AF43", "flight", "exit one bar late", "        if self._exit_ns is None or bar.ts_event_ns < self._exit_ns:", "        if self._exit_ns is None or bar.ts_event_ns <= self._exit_ns:"),
    ("AF44", "flight", "exit side reversed", '        side = "sell" if position > 0 else "buy"\n        return (leg_market_intent(view, TRADED, side, abs(position)),)\n\n    # -- the member contract', '        side = "buy" if position > 0 else "sell"\n        return (leg_market_intent(view, TRADED, side, abs(position)),)\n\n    # -- the member contract'),
    ("AF45", "flight", "exit quantity + 1", "        return (leg_market_intent(view, TRADED, side, abs(position)),)", "        return (leg_market_intent(view, TRADED, side, abs(position) + 1),)"),
    ("AF46", "flight", "T_e not reset when flat", "        self._t_e_ns, self._exit_ns = None, None", "        pass"),
    ("AF47", "flight", "only negative r recorded", "            if r is not None:  # every defined r_k is a future reference value, traded or not", "            if r is not None and r[0] < 0:"),
    ("AF48", "flight", "prune the oldest reference", "        self._history = {d: v for d, v in merged.items() if d >= oldest}", "        self._history = {d: v for d, v in merged.items() if d > oldest}"),
    ("AF49", "flight", "a filed date keeps no values", "            merged = {**merged, self._sig_day: self._today}", "            merged = {**merged}"),
    ("AF50", "flight", "signal leg declared first", "        self.legs = (LegSpec(TRADED, True), LegSpec(SIGNAL, False))", "        self.legs = (LegSpec(SIGNAL, False), LegSpec(TRADED, True))"),
    ("AF51", "flight", "label order", '        self.name = f"{MEMBER_ID} {self.variant} {TRADED}"', '        self.name = f"{MEMBER_ID} {TRADED} {self.variant}"'),
    ("AF52", "flight", "MGC window ends 15:05", "                                     shift(LAST_EXIT_BAR, 2)),),", "                                     shift(LAST_EXIT_BAR, 1)),),"),
    # ---------------------------------------------------------------- oilcad: literals and clocks
    ("AO01", "oilcad", "first t 08:00", "FIRST_DECISION_CT = time(8, 5)", "FIRST_DECISION_CT = time(8, 0)"),
    ("AO02", "oilcad", "last t 13:30", "LAST_DECISION_CT = time(13, 25)", "LAST_DECISION_CT = time(13, 30)"),
    ("AO03", "oilcad", "last t 13:20", "LAST_DECISION_CT = time(13, 25)", "LAST_DECISION_CT = time(13, 20)"),
    ("AO04", "oilcad", "10-minute step", "STEP_MIN = 5 ", "STEP_MIN = 10 "),
    ("AO05", "oilcad", "c1 bar t - 2", "LAST_BAR_BEFORE_T_MIN = 1 ", "LAST_BAR_BEFORE_T_MIN = 2 "),
    ("AO06", "oilcad", "c6 bar t - 5", "FIRST_BAR_BEFORE_T_MIN = 6 ", "FIRST_BAR_BEFORE_T_MIN = 5 "),
    ("AO07", "oilcad", "19 reference dates", "REFERENCE_DATES = 20 ", "REFERENCE_DATES = 19 "),
    ("AO08", "oilcad", "n >= 999", "MIN_VALUES = 1000 ", "MIN_VALUES = 999 "),
    ("AO09", "oilcad", "n >= 1001", "MIN_VALUES = 1000 ", "MIN_VALUES = 1001 "),
    ("AO10", "oilcad", "|z| >= 1.9999", "Z_THRESHOLD = 2.0 ", "Z_THRESHOLD = 1.9999 "),
    ("AO11", "oilcad", "|z| >= 2.0001", "Z_THRESHOLD = 2.0 ", "Z_THRESHOLD = 2.0001 "),
    ("AO12", "oilcad", "exit T_e + 13", "EXIT_AFTER_FILL_MIN = 14 ", "EXIT_AFTER_FILL_MIN = 13 "),
    ("AO13", "oilcad", "exit T_e + 15", "EXIT_AFTER_FILL_MIN = 14 ", "EXIT_AFTER_FILL_MIN = 15 "),
    # ---------------------------------------------------------------- oilcad: arithmetic and comparisons
    ("AO14", "oilcad", "c6 = 0 allowed", "    if c6 <= 0:\n        return None\n    return (c1 - c6) / c6", "    if c6 < 0:\n        return None\n    return (c1 - c6) / c6"),
    ("AO15", "oilcad", "r over c1", "    return (c1 - c6) / c6", "    return (c1 - c6) / c1"),
    ("AO16", "oilcad", "pstdev (ddof 0)", "    s = statistics.stdev(values)", "    s = statistics.pstdev(values)"),
    ("AO17", "oilcad", "n < MIN -> <=", "    if len(values) < MIN_VALUES:", "    if len(values) <= MIN_VALUES:"),
    ("AO18", "oilcad", "s = 0 allowed", "    if s <= 0:", "    if s < 0:"),
    ("AO19", "oilcad", "|z| > 2 strict", "    return abs(r / s) >= Z_THRESHOLD", "    return abs(r / s) > Z_THRESHOLD"),
    ("AO20", "oilcad", "no abs (one side)", "    return abs(r / s) >= Z_THRESHOLD", "    return (r / s) >= Z_THRESHOLD"),
    # ---------------------------------------------------------------- oilcad: guards and state
    ("AO21", "oilcad", "no MCL instrument guard", "        if first is not None and first[1] == bar.instrument_id:", "        if first is not None:"),
    ("AO22", "oilcad", "no MCL CT-date check", "        if opened.date() != day:\n            return None  # the previous CT evening's bars hold no block", "        if False:\n            return None"),
    ("AO23", "oilcad", "t-6 store not reset per day", "        self._mcl_day, self._firsts = day, {}", "        self._mcl_day = day"),
    ("AO24", "oilcad", "prune the oldest reference", "        self._history = {d: v for d, v in self._history.items() if d >= oldest}", "        self._history = {d: v for d, v in self._history.items() if d > oldest}"),
    ("AO25", "oilcad", "no warm-up", "        warm = (len(refs) == REFERENCE_DATES and self._first_day is not None\n                and refs[0] >= self._first_day)", "        warm = len(refs) == REFERENCE_DATES"),
    ("AO26", "oilcad", "fewer than 20 refs accepted", "        warm = (len(refs) == REFERENCE_DATES and self._first_day is not None\n                and refs[0] >= self._first_day)", "        warm = (len(refs) >= 1 and self._first_day is not None\n                and refs[0] >= self._first_day)"),
    ("AO27", "oilcad", "T_e not reset when flat", "        if position == 0:\n            self._te_ns = None", "        if False:\n            self._te_ns = None"),
    ("AO28", "oilcad", "T_e one minute late", "            self._te_ns = view.ts_event_ns", "            self._te_ns = view.ts_event_ns + NS_PER_MIN"),
    ("AO29", "oilcad", "entry while pending", "        if account.pending.get(TRADED, 0):\n            return ()  # K8-L-11: a pending order is not flat", "        pass"),
    ("AO30", "oilcad", "exit while pending", "        if account.pending.get(TRADED, 0) or self._te_ns is None:", "        if self._te_ns is None:"),
    ("AO31", "oilcad", "exit one bar late", "        if bar.ts_event_ns < self._te_ns + EXIT_AFTER_FILL_MIN * NS_PER_MIN:", "        if bar.ts_event_ns <= self._te_ns + EXIT_AFTER_FILL_MIN * NS_PER_MIN:"),
    ("AO32", "oilcad", "exit side reversed", '        side = "sell" if position > 0 else "buy"', '        side = "buy" if position > 0 else "sell"'),
    ("AO33", "oilcad", "exit quantity + 1", "        return (leg_market_intent(view, TRADED, side, abs(position)),)", "        return (leg_market_intent(view, TRADED, side, abs(position) + 1),)"),
    ("AO34", "oilcad", "no 6C CT-date check", "        if ct_open(bar).date() != day:\n            return ()", "        if False:\n            return ()"),
    ("AO35", "oilcad", "d need not be an OILCAD date", "        if day not in _OILCAD_SET:", "        if False:"),
    ("AO36", "oilcad", "C6 tests t - 1", "        if in_guard(TRADED, bar.ts_event_ns + NS_PER_MIN):", "        if in_guard(TRADED, bar.ts_event_ns):"),
    ("AO37", "oilcad", "no C6", "        if in_guard(TRADED, bar.ts_event_ns + NS_PER_MIN):", "        if False:"),
    ("AO38", "oilcad", "entry side reversed", '        side = "buy" if diff > 0 else "sell"', '        side = "sell" if diff > 0 else "buy"'),
    ("AO39", "oilcad", "q_c + 1", "        return (leg_market_intent(view, TRADED, side, self._q),)", "        return (leg_market_intent(view, TRADED, side, self._q + 1),)"),
    ("AO40", "oilcad", "signal leg declared first", "        self.legs = (LegSpec(TRADED, True), LegSpec(SIGNAL, False))", "        self.legs = (LegSpec(SIGNAL, False), LegSpec(TRADED, True))"),
    ("AO41", "oilcad", "6C window ends 13:40", "                                     shift(last_exit_fill, 1)),),", "                                     last_exit_fill),),"),
    ("AO42", "oilcad", "only positive r filed", "            if r is not None:\n                self._history", "            if r is not None and r > 0:\n                self._history"),
    # ---------------------------------------------------------------- wkndbtc
    ("AW01", "wkndbtc", "Tuesday", "MONDAY = 0 ", "MONDAY = 1 "),
    ("AW02", "wkndbtc", "Friday d - 2", "FRIDAY_OFFSET_DAYS = -3 ", "FRIDAY_OFFSET_DAYS = -2 "),
    ("AW03", "wkndbtc", "Sunday d - 2", "SUNDAY_OFFSET_DAYS = -1 ", "SUNDAY_OFFSET_DAYS = -2 "),
    ("AW04", "wkndbtc", "P_F 14:58", "FRIDAY_BAR_CT = time(14, 59)", "FRIDAY_BAR_CT = time(14, 58)"),
    ("AW05", "wkndbtc", "P_F 15:00", "FRIDAY_BAR_CT = time(14, 59)", "FRIDAY_BAR_CT = time(15, 0)"),
    ("AW06", "wkndbtc", "P_S 17:58", "SUNDAY_BAR_CT = time(17, 59)", "SUNDAY_BAR_CT = time(17, 58)"),
    ("AW07", "wkndbtc", "P_S 18:00", "SUNDAY_BAR_CT = time(17, 59)", "SUNDAY_BAR_CT = time(18, 0)"),
    ("AW08", "wkndbtc", "exit bar 14:57", "EXIT_BAR_CT = time(14, 58)", "EXIT_BAR_CT = time(14, 57)"),
    ("AW09", "wkndbtc", "exit bar 14:59", "EXIT_BAR_CT = time(14, 58)", "EXIT_BAR_CT = time(14, 59)"),
    ("AW10", "wkndbtc", "weekday check removed", "    return day.weekday() == MONDAY and day in _WKNDBTC_SET and friday in _WKNDBTC_SET", "    return day in _WKNDBTC_SET and friday in _WKNDBTC_SET"),
    ("AW11", "wkndbtc", "d full-session check removed", "    return day.weekday() == MONDAY and day in _WKNDBTC_SET and friday in _WKNDBTC_SET", "    return day.weekday() == MONDAY and friday in _WKNDBTC_SET"),
    ("AW12", "wkndbtc", "Friday full-session check removed", "    return day.weekday() == MONDAY and day in _WKNDBTC_SET and friday in _WKNDBTC_SET", "    return day.weekday() == MONDAY and day in _WKNDBTC_SET"),
    ("AW13", "wkndbtc", "G = 0 buys", '    if g_ticks > 0:\n        return "buy"', '    if g_ticks >= 0:\n        return "buy"'),
    ("AW14", "wkndbtc", "sides swapped", '    if g_ticks > 0:\n        return "buy"\n    if g_ticks < 0:\n        return "sell"', '    if g_ticks > 0:\n        return "sell"\n    if g_ticks < 0:\n        return "buy"'),
    ("AW15", "wkndbtc", "P_F CT-date check removed", "        if opened.time() == FRIDAY_BAR_CT and opened.date() == bar.trade_date:", "        if opened.time() == FRIDAY_BAR_CT:"),
    ("AW16", "wkndbtc", "entry CT-date check removed", "        if opened.time() != SUNDAY_BAR_CT or opened.date() != sunday:", "        if opened.time() != SUNDAY_BAR_CT:"),
    ("AW17", "wkndbtc", "P_S trade_date check removed", "        if mbt is None or mbt.trade_date != day:", "        if mbt is None:"),
    ("AW18", "wkndbtc", "P_F date check removed (stale Friday)", "        if self._friday is None or self._friday[0] != friday:", "        if self._friday is None:"),
    ("AW19", "wkndbtc", "instrument guard removed", "        if p_f_id != mbt.instrument_id:", "        if False:"),
    ("AW20", "wkndbtc", "C6 tests 17:59", "        if in_guard(TRADED, mnq.ts_event_ns + NS_PER_MIN):", "        if in_guard(TRADED, mnq.ts_event_ns):"),
    ("AW21", "wkndbtc", "no C6", "        if in_guard(TRADED, mnq.ts_event_ns + NS_PER_MIN):", "        if False:"),
    ("AW22", "wkndbtc", "exit instant on the Sunday", "        self._exit_ns = ct_ns(day, EXIT_BAR_CT)", "        self._exit_ns = ct_ns(sunday, EXIT_BAR_CT)"),
    ("AW23", "wkndbtc", "exit while pending", "        if account.pending.get(TRADED, 0) or self._exit_ns is None:", "        if self._exit_ns is None:"),
    ("AW24", "wkndbtc", "exit one bar late", "        if bar.ts_event_ns < self._exit_ns:", "        if bar.ts_event_ns <= self._exit_ns:"),
    ("AW25", "wkndbtc", "exit side reversed", '        side = "sell" if position > 0 else "buy"', '        side = "buy" if position > 0 else "sell"'),
    ("AW26", "wkndbtc", "exit quantity + 1", "        return (leg_market_intent(view, TRADED, side, abs(position)),)", "        return (leg_market_intent(view, TRADED, side, abs(position) + 1),)"),
    ("AW27", "wkndbtc", "entry while pending", "        if account.pending.get(TRADED, 0):\n            return ()  # S0.6: never an entry while an order is pending", "        pass"),
    ("AW28", "wkndbtc", "q_c + 1", "        return (leg_market_intent(view, TRADED, side, self._q),)", "        return (leg_market_intent(view, TRADED, side, self._q + 1),)"),
    ("AW29", "wkndbtc", "signal leg declared first", "        self.legs = (LegSpec(TRADED, True), LegSpec(SIGNAL, False))", "        self.legs = (LegSpec(SIGNAL, False), LegSpec(TRADED, True))"),
    ("AW30", "wkndbtc", "G sign flipped", "        side = side_of(to_ticks(mbt.close, self._mbt_tick) - p_f)", "        side = side_of(p_f - to_ticks(mbt.close, self._mbt_tick))"),
    ("AW31", "wkndbtc", "MNQ Monday window ends 14:59", "                     TradingInterval(EXIT_BAR_CT, time(15, 0))),", "                     TradingInterval(EXIT_BAR_CT, time(14, 59))),"),
    # ---------------------------------------------------------------- the tables
    ("AR01", "_releases", "1-minute guard", "GUARD_SECONDS = 120 ", "GUARD_SECONDS = 60 "),
    ("AR02", "_releases", "3-minute guard", "GUARD_SECONDS = 120 ", "GUARD_SECONDS = 180 "),
    ("AR03", "_releases", "R itself not guarded", "        if instants[mid] * NS_PER_S <= t_ns:", "        if instants[mid] * NS_PER_S < t_ns:"),
    ("AR04", "_releases", "R + 120 s guarded", "    return lo > 0 and t_ns < (instants[lo - 1] + GUARD_SECONDS) * NS_PER_S", "    return lo > 0 and t_ns <= (instants[lo - 1] + GUARD_SECONDS) * NS_PER_S"),
    ("AC01", "_calendar", "previous_dates includes d", "    return tuple(dates[max(0, lo - k):lo])  # k <= 0: an empty slice", "    return tuple(dates[max(0, lo - k + 1):lo + 1])"),
    ("AC02", "_calendar", "previous_dates k - 1", "    return tuple(dates[max(0, lo - k):lo])  # k <= 0: an empty slice", "    return tuple(dates[max(0, lo - k + 1):lo])"),
    ("AC03", "_calendar", "FLIGHT_DATES a union", "tuple(sorted(EQUITY_FULL_SESSIONS & METALS_FULL_SESSIONS))", "tuple(sorted(EQUITY_FULL_SESSIONS | METALS_FULL_SESSIONS))"),
    ("AC04", "_calendar", "OILCAD_DATES energy only", "tuple(sorted(ENERGY_FULL_SESSIONS & FX_FULL_SESSIONS))", "tuple(sorted(ENERGY_FULL_SESSIONS))"),
    ("AC05", "_calendar", "WKNDBTC_DATES equity only", "tuple(sorted(EQUITY_FULL_SESSIONS & CRYPTO_FULL_SESSIONS))", "tuple(sorted(EQUITY_FULL_SESSIONS))"),
    # ---------------------------------------------------------------- batch 2 (auditor, after reading the tests)
    ("AF53", "flight", "missing entry bar checked BEFORE C6 ends the day",
     "        if in_guard(TRADED, view.decision_ts_ns):\n            return ()  # C6: the fill minute t_k is guarded; skipped, the day's entry kept\n        self._done = True  # the first non-skipped trigger uses the day's entry (E.3-L-08)\n        bar = view.bar(TRADED)\n        if bar is None or bar.trade_date != day:\n            return ()  # K8-L-06: the entry bar at t_k - 1 is missing: no trade on d",
     "        bar = view.bar(TRADED)\n        if bar is None or bar.trade_date != day:\n            self._done = True\n            return ()\n        if in_guard(TRADED, view.decision_ts_ns):\n            return ()\n        self._done = True"),
    ("AF54", "flight", "C6 on the wrong root (6C)", "        if in_guard(TRADED, view.decision_ts_ns):", '        if in_guard("6C", view.decision_ts_ns):'),
    ("AF55", "flight", "a late MES bar (at t_k) used as the t_k - 1 bar", "        k_end = self._k_of_end_bar.get(minute)", "        k_end = self._k_of_end_bar.get(minute) or self._k_of_end_bar.get(minute - 1)"),
    ("AF56", "flight", "t_k - 6 store not reset per MES day", "        self._sig_day, self._starts, self._today = day, {}, ()", "        self._sig_day, self._today = day, ()"),
    ("AF57", "flight", "any variant accepted", "        if self.variant not in VARIANTS:\n            raise ValueError", "        if False:\n            raise ValueError"),
    ("AF59", "flight", "blocks shifted to 08:30..14:50", "    return tuple(shift(BLOCK_CLOCK_START, BLOCK_MINUTES * k) for k in range(1, BLOCKS + 1))", "    return tuple(shift(BLOCK_CLOCK_START, BLOCK_MINUTES * k) for k in range(0, BLOCKS))"),
    ("AO43", "oilcad", "a late MCL bar (at t) used as the t - 1 bar", "        t = self._t_of_last_bar.get(at)", "        t = self._t_of_last_bar.get(at) or self._t_of_last_bar.get(shift(at, -1))"),
    ("AO44", "oilcad", "C6 on the wrong root (MGC)", "        if in_guard(TRADED, bar.ts_event_ns + NS_PER_MIN):", '        if in_guard("MGC", bar.ts_event_ns + NS_PER_MIN):'),
    ("AW32", "wkndbtc", "the 18:00 MNQ bar also accepted as the entry bar", "        if opened.time() != SUNDAY_BAR_CT or opened.date() != sunday:", "        if opened.time() not in (SUNDAY_BAR_CT, time(18, 0)) or opened.date() != sunday:"),
    ("AW33", "wkndbtc", "the Friday 15:00 MBT bar also accepted as P_F", "        if opened.time() == FRIDAY_BAR_CT and opened.date() == bar.trade_date:", "        if opened.time() in (FRIDAY_BAR_CT, time(15, 0)) and opened.date() == bar.trade_date:"),
    ("AW34", "wkndbtc", "C6 on the wrong root (6C)", "        if in_guard(TRADED, mnq.ts_event_ns + NS_PER_MIN):", '        if in_guard("6C", mnq.ts_event_ns + NS_PER_MIN):'),
    ("AF41b", "flight", "exit clock computed from T_e + 1 min (the real T_e mutant; AF41 only moved a flag)", "            self._exit_ns = self._exit_due_ns(view.ts_event_ns)", "            self._exit_ns = self._exit_due_ns(view.ts_event_ns + NS_PER_MIN)"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_pytest(env: dict[str, str], log: Path) -> tuple[int, int, list[str], str]:
    cmd = ["nice", "-n", "10", "uv", "run", "pytest", "-q", "-rf", "-p", "no:cacheprovider",
           "-p", "k8audit_mutplugin", *TESTS]
    proc = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, text=True, timeout=900)
    text = proc.stdout + "\n" + proc.stderr
    log.write_text(text, encoding="utf-8")
    failed = re.findall(r"^FAILED (\S+)", text, flags=re.M)
    errors = re.findall(r"^ERROR (\S+)", text, flags=re.M)
    m = re.search(r"(\d+) passed", text)
    passed = int(m.group(1)) if m else 0
    return passed, len(failed) + len(errors), failed + errors, text.strip().splitlines()[-1] if text.strip() else ""


def main() -> None:
    only = set(sys.argv[1:])
    MUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    before = {p: sha(REPO / p) for p in GUARDED}
    sources = {m: (REPO / p).read_text(encoding="utf-8") for m, p in MODULES.items()}
    base_env = {k: v for k, v in os.environ.items() if k != "PYTHONPYCACHEPREFIX"}
    base_env["PYTHONPATH"] = str(AUDIT)
    base_env["PYTHONDONTWRITEBYTECODE"] = "1"
    results = []
    t0 = time.time()
    # no-op injection: the real source installed through the plugin must pass everything
    for mod in ("flight", "oilcad", "wkndbtc", "_releases", "_calendar"):
        if only and f"NOOP-{mod}" not in only and only != {"all"}:
            continue
        env = dict(base_env, K8_MUT_MODULE=f"strategy.members.k8.{mod}",
                   K8_MUT_SOURCE=str(REPO / MODULES[mod]), K8_MUT_REALPATH=str(REPO / MODULES[mod]))
        passed, nfail, names, last = run_pytest(env, LOG_DIR / f"NOOP-{mod}.log")
        results.append({"id": f"NOOP-{mod}", "module": mod, "what": "no-op injection (control)",
                        "passed": passed, "failed": nfail, "failing": names[:6], "status":
                        "control_ok" if nfail == 0 and passed > 0 else "CONTROL_FAILED"})
        print(results[-1]["id"], results[-1]["status"], passed, nfail, flush=True)
    for mid, mod, what, old, new in MUTANTS:
        if only and mid not in only and only != {"all"}:
            continue
        src = sources[mod]
        n = src.count(old)
        if n != 1:
            results.append({"id": mid, "module": mod, "what": what, "status": "BAD_MUTANT",
                            "detail": f"fragment occurs {n} times"})
            print(mid, "BAD_MUTANT", n, flush=True)
            continue
        mutated = src.replace(old, new)
        mpath = MUT_DIR / f"{mid}.py"
        mpath.write_text(mutated, encoding="utf-8")
        env = dict(base_env, K8_MUT_MODULE=f"strategy.members.k8.{mod}", K8_MUT_SOURCE=str(mpath),
                   K8_MUT_REALPATH=str(REPO / MODULES[mod]))
        passed, nfail, names, last = run_pytest(env, LOG_DIR / f"{mid}.log")
        status = "killed" if nfail > 0 else "SURVIVED"
        results.append({"id": mid, "module": mod, "what": what, "passed": passed, "failed": nfail,
                        "failing": names[:4], "status": status})
        print(mid, status, passed, nfail, names[:2], flush=True)
    after = {p: sha(REPO / p) for p in GUARDED}
    changed = [p for p in GUARDED if before[p] != after[p]]
    summary = {"elapsed_s": round(time.time() - t0, 1), "guarded_files_changed": changed,
               "n_mutants": sum(1 for r in results if not r["id"].startswith("NOOP")),
               "killed": sum(1 for r in results if r["status"] == "killed"),
               "survived": sum(1 for r in results if r["status"] == "SURVIVED"),
               "bad": sum(1 for r in results if r["status"] == "BAD_MUTANT"),
               "results": results}
    out_name = "mutants_results.json" if not only or only == {"all"} else \
        f"mutants_results_{sorted(only)[0]}.json"
    (AUDIT / out_name).write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}), flush=True)


if __name__ == "__main__":
    main()
