"""Mutation runner for MemberCoder-B's K7 files: change, run, restore (bytes and mtime)."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = Path(__file__).with_name("results.json")
TESTS = ["tests/test_k7_members_events.py", "tests/test_k7_members_events_rev2h.py",
         "tests/test_k7_members_events_montrend.py"]
C = "strategy/members/k7/_event_common.py"
E = "strategy/members/k7/expiry.py"
R = "strategy/members/k7/rev2h.py"
M = "strategy/members/k7/montrend.py"
K = "strategy/members/k7/_calendar.py"
MUTANTS = [
    # id, file, old, new, what
    ("C01", C, 'ROOT = "MBT"', 'ROOT = "MES"', "leg root"),
    ("C02", C, "FILL_DELAY_MIN = 1", "FILL_DELAY_MIN = 2", "C2 fill delay (expiry bars)"),
    ("C03", C, "for d in CRYPTO_FULL_SESSIONS if d not in frozenset(VENDOR_DEGRADED))",
     "for d in CRYPTO_FULL_SESSIONS if True)", "S0.8 degraded exclusion dropped"),
    ("C04", C, "return day in ENTRY_DATES", "return True", "S0.8 entry-date test dropped"),
    ("C05", C, "return int(hours) * MINUTES_PER_HOUR + int(minutes)",
     "return int(hours) * MINUTES_PER_HOUR", "HH:MM minutes dropped"),
    ("C06", C, "return at.hour * MINUTES_PER_HOUR + at.minute", "return at.hour * MINUTES_PER_HOUR",
     "time minutes dropped"),
    ("C07", C, "if not -MINUTES_PER_DAY <= minute < MINUTES_PER_DAY:",
     "if not -MINUTES_PER_DAY < minute < MINUTES_PER_DAY:", "ct_open_ns lower bound"),
    ("C08", C, "if not -MINUTES_PER_DAY <= minute < MINUTES_PER_DAY:",
     "if not -MINUTES_PER_DAY <= minute <= MINUTES_PER_DAY:", "ct_open_ns upper bound"),
    ("C09", C, "on = day + timedelta(days=minute // MINUTES_PER_DAY)", "on = day",
     "previous CT date ignored"),
    ("C12", C, "return round(Decimal(repr(price)) / tick)", "return int(Decimal(repr(price)) / tick)",
     "tick rounding"),
    ("C13", C, 'return to_ticks(asdict(bar)["open"], tick)', 'return to_ticks(asdict(bar)["close"], tick)',
     "start bar open -> close"),
    ("C14", C, "return (value > 0) - (value < 0)", "return (value >= 0) - (value < 0)", "sign(0)"),
    ("C15", C, "return account.position(root) == 0 and not account.pending.get(root, 0)",
     "return account.position(root) == 0", "flat ignores pending"),
    ("C16", C, "if position == 0 or account.pending.get(root, 0):", "if position == 0:",
     "exit while pending"),
    ("C17", C, "SELL if position > 0 else BUY, abs(position)", "BUY if position > 0 else SELL, abs(position)",
     "exit side"),
    ("C18", C, "SELL if position > 0 else BUY, abs(position)", "SELL if position > 0 else BUY, position",
     "exit quantity sign"),
    ("C19", C, "decisions[self._next].end_ns < ts:", "decisions[self._next].end_ns <= ts:",
     "missed-decision comparison"),
    ("C20", C, "self._target = 0  # its t - 1 bar is missing", "pass  # its t - 1 bar is missing",
     "missed decision keeps the old target"),
    ("C21", C, "if i is not None and i >= self._next:", "if i is not None and i > self._next:",
     "start bar of the next decision"),
    ("C22", C, "if start is None or start[1] != bar.instrument_id:", "if start is None:",
     "signal-bar id guard dropped"),
    ("C23", C, "if start is None or start[1] != bar.instrument_id:",
     "if start is None or start[1] == bar.instrument_id:", "signal-bar id guard inverted"),
    ("C24", C, "target = self.direction * sign(to_ticks(bar.close, self.tick) - start[0])",
     "target = sign(to_ticks(bar.close, self.tick) - start[0])", "direction dropped"),
    ("C25", C, "target = self.direction * sign(to_ticks(bar.close, self.tick) - start[0])",
     "target = self.direction * sign(start[0] - to_ticks(bar.close, self.tick))", "r reversed"),
    ("C26", C, "if ts >= self.schedule.final_exit_ns or", "if ts > self.schedule.final_exit_ns or",
     "final exit comparison"),
    ("C27", C, "or sign(position) != self._target:", "or sign(position) == self._target:",
     "flatten on equal sign"),
    ("C28", C, "or sign(position) != self._target:", "or False:", "no flatten"),
    ("C29", C, "if (target == 0 or ts != self.schedule.decisions[index].entry_ns",
     "if (ts != self.schedule.decisions[index].entry_ns", "entry on target 0"),
    ("C30", C, "if (target == 0 or ts != self.schedule.decisions[index].entry_ns",
     "if (target == 0 or ts < self.schedule.decisions[index].entry_ns", "entry on a later bar"),
    ("C31", C, "or bar.instrument_id != signal_id or not is_flat(account, self.root)):",
     "or not is_flat(account, self.root)):", "entry-bar id guard dropped"),
    ("C32", C, "or bar.instrument_id != signal_id or not is_flat(account, self.root)):",
     "or bar.instrument_id != signal_id):", "entry while not flat"),
    ("C33", C, "(view, self.root, BUY if target > 0 else SELL, self.q)",
     "(view, self.root, SELL if target > 0 else BUY, self.q)", "entry side"),
    ("E01", E, "ENTRY_FILL_BEFORE_T_MIN = 300", "ENTRY_FILL_BEFORE_T_MIN = 299", "entry 300 -> 299"),
    ("E02", E, "ENTRY_FILL_BEFORE_T_MIN = 300", "ENTRY_FILL_BEFORE_T_MIN = 301", "entry 300 -> 301"),
    ("E03", E, "EXIT_FILL_BEFORE_T_MIN = 1", "EXIT_FILL_BEFORE_T_MIN = 0", "exit 1 -> 0"),
    ("E04", E, "EXIT_FILL_BEFORE_T_MIN = 1", "EXIT_FILL_BEFORE_T_MIN = 2", "exit 1 -> 2"),
    ("E05", E, 'T_EXP_SLOTS: tuple[str, ...] = ("10:00", "11:00")',
     'T_EXP_SLOTS: tuple[str, ...] = ("10:00", "12:00")', "T_exp slot"),
    ("E06", E, "WINDOW_START_CT = time(5, 0)", "WINDOW_START_CT = time(5, 1)", "window start"),
    ("E07", E, "WINDOW_END_CT = time(11, 0)", "WINDOW_END_CT = time(10, 59)", "window end"),
    ("E08", E, "        if not is_entry_date(day):\n            continue\n", "", "event set not S0.8"),
    ("E09", E, "if bar.ts_event_ns < self._exit_ns:", "if bar.ts_event_ns <= self._exit_ns:",
     "exit comparison"),
    ("E11", E, "if times is None or bar.ts_event_ns != times[0] or not is_flat(account, self.root):",
     "if times is None or bar.ts_event_ns < times[0] or not is_flat(account, self.root):",
     "entry on a later bar"),
    ("E12", E, "if times is None or bar.ts_event_ns != times[0] or not is_flat(account, self.root):",
     "if times is None or bar.ts_event_ns != times[0]:", "entry while not flat"),
    ("E13", E, "(view, self.root, BUY, self._leg.q)", '(view, self.root, "sell", self._leg.q)',
     "long only"),
    ("E14", E, "times = self._events.get(bar.trade_date)",
     "times = self._events.get(bar.trade_date - timedelta(days=0) if False else bar.trade_date)",
     "(no-op control, must survive)"),
    ("R01", R, "BLOCK_MINUTES = 120", "BLOCK_MINUTES = 119", "block 119"),
    ("R02", R, "BLOCK_MINUTES = 120", "BLOCK_MINUTES = 121", "block 121"),
    ("R03", R, "BLOCKS = 3", "BLOCKS = 2", "3 blocks -> 2"),
    ("R04", R, "DECISION_BLOCKS = (1, 2)", "DECISION_BLOCKS = (1,)", "one decision"),
    ("R05", R, "SIGNAL_END_BEFORE_T_MIN = 1", "SIGNAL_END_BEFORE_T_MIN = 2", "t-1 -> t-2"),
    ("R06", R, "FINAL_EXIT_BEFORE_END_MIN = 1", "FINAL_EXIT_BEFORE_END_MIN = 0", "exit bar 14:30"),
    ("R07", R, "WINDOW_END_AFTER_BLOCKS_MIN = 1", "WINDOW_END_AFTER_BLOCKS_MIN = 0", "window end"),
    ("R08", R, "DIRECTION = -1", "DIRECTION = 1", "reversal -> momentum"),
    ("R09", R, "if is_entry_date(self._day) else None)", "if True else None)", "dates not S0.8"),
    ("R10", R, "self._anchor = clock_minute(self._leg.o)", "self._anchor = clock_minute(self._leg.c)",
     "anchor O -> C"),
    ("R11", R, "decisions.append(Decision(ct_open_ns(day, t - BLOCK_MINUTES),",
     "decisions.append(Decision(ct_open_ns(day, t - BLOCK_MINUTES + 1),", "start bar"),
    ("M01", M, "MONDAY = 0", "MONDAY = 1", "Monday -> Tuesday"),
    ("M02", M, "SUNDAY_OFFSET_DAYS = -1", "SUNDAY_OFFSET_DAYS = -2", "Sunday -> Saturday"),
    ("M03", M, "FIRST_DECISION = (SUNDAY_OFFSET_DAYS, time(18, 0))",
     "FIRST_DECISION = (SUNDAY_OFFSET_DAYS, time(19, 0))", "first decision 19:00"),
    ("M04", M, "LAST_DECISION = (0, time(13, 0))", "LAST_DECISION = (0, time(14, 0))",
     "last decision 14:00"),
    ("M05", M, "LAST_DECISION = (0, time(13, 0))", "LAST_DECISION = (0, time(12, 0))",
     "last decision 12:00"),
    ("M06", M, "STEP_MINUTES = 60", "STEP_MINUTES = 30", "step 30"),
    ("M07", M, "LOOKBACK_MINUTES = 60", "LOOKBACK_MINUTES = 59", "lookback 59"),
    ("M08", M, "SIGNAL_END_BEFORE_T_MIN = 1", "SIGNAL_END_BEFORE_T_MIN = 2", "t-1 -> t-2"),
    ("M09", M, "FLAT_AT = (0, time(14, 0))", "FLAT_AT = (0, time(14, 1))", "flat 14:01"),
    ("M10", M, "FINAL_EXIT_BEFORE_FLAT_MIN = 1", "FINAL_EXIT_BEFORE_FLAT_MIN = 0", "exit bar 14:00"),
    ("M11", M, "DIRECTION = 1", "DIRECTION = -1", "momentum -> reversal"),
    ("M12", M, "return day.weekday() == MONDAY and is_entry_date(day)",
     "return day.weekday() == MONDAY", "dates not S0.8"),
    ("M13", M, "return day.weekday() == MONDAY and is_entry_date(day)",
     "return is_entry_date(day)", "any weekday"),
    ("K01", K, '"2025-06-03", "2025-06-04",', '"2025-06-04",', "a full session removed"),
    ("K02", K, '"2024-07-03",\n)', '"2024-07-02",\n)', "early-F list"),
    ("K03", K, '"2024-09-18", "2025-09-17",', '"2024-09-18",', "a degraded date removed"),
    ("K04", K, '("2025-09-26", "10:00"), ("2025-10-31", "11:00")',
     '("2025-09-26", "10:00"), ("2025-10-31", "10:00")', "a T_exp changed"),
    ("K05", K, '("2025-06-27", "10:00")', '("2025-06-26", "10:00")', "an MBTX date changed"),
    ("S01", K, 'beb9501d6235299cd716868a8c14cf1df1b3cc71fa0b58c4e9780e9035b07d28',
     'beb9501d6235299cd716868a8c14cf1df1b3cc71fa0b58c4e9780e9035b07d29', "a source sha256"),
    ("F01", E, 'MEMBER_ID = "K7-expiry-01"', 'MEMBER_ID = "K7-expiry-1"', "label"),
    ("F02", M, 'MEMBER_ID = "K7-montrend-01"', 'MEMBER_ID = "K7-montrend-02"', "label"),
    ("F03", R, 'MEMBER_ID = "K7-rev2h-01"', 'MEMBER_ID = "K7-rev2h-1"', "label"),
    ("SK", K, "from __future__ import annotations\n", "from __future__ import annotations\nimport os\n", "banned import"),
    ("ZK", K, "from __future__ import annotations\n", "from __future__ import annotations\nfrom zoneinfo import ZoneInfo\n_LONDON = ZoneInfo('Europe/London')\n", "a London zone"),
    ("SC", C, "from __future__ import annotations\n", "from __future__ import annotations\nimport os\n", "banned import"),
    ("ZC", C, "from __future__ import annotations\n", "from __future__ import annotations\nfrom zoneinfo import ZoneInfo\n_LONDON = ZoneInfo('Europe/London')\n", "a London zone"),
    ("SE", E, "from __future__ import annotations\n", "from __future__ import annotations\nimport os\n", "banned import"),
    ("ZE", E, "from __future__ import annotations\n", "from __future__ import annotations\nfrom zoneinfo import ZoneInfo\n_LONDON = ZoneInfo('Europe/London')\n", "a London zone"),
    ("SR", R, "from __future__ import annotations\n", "from __future__ import annotations\nimport os\n", "banned import"),
    ("ZR", R, "from __future__ import annotations\n", "from __future__ import annotations\nfrom zoneinfo import ZoneInfo\n_LONDON = ZoneInfo('Europe/London')\n", "a London zone"),
    ("SM", M, "from __future__ import annotations\n", "from __future__ import annotations\nimport os\n", "banned import"),
    ("ZM", M, "from __future__ import annotations\n", "from __future__ import annotations\nfrom zoneinfo import ZoneInfo\n_LONDON = ZoneInfo('Europe/London')\n", "a London zone"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    files = sorted({m[1] for m in MUTANTS})
    before = {f: sha(REPO / f) for f in files}
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPYCACHEPREFIX"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    results = []
    only = set(sys.argv[1:])
    for mid, rel, old, new, what in MUTANTS:
        if only and mid not in only:
            continue
        path = REPO / rel
        original = path.read_bytes()
        st = os.stat(path)
        text = original.decode()
        n = text.count(old)
        if n != 1:
            results.append({"id": mid, "file": rel, "what": what, "error": f"old occurs {n}x"})
            continue
        try:
            path.write_text(text.replace(old, new), encoding="utf-8")
            proc = subprocess.run(
                ["nice", "-n", "10", "uv", "run", "pytest", "-q", "-p", "no:cacheprovider",
                 "--tb=no", "-rf", *TESTS], cwd=REPO, env=env, capture_output=True, text=True,
                timeout=600)
        finally:
            path.write_bytes(original)
            os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
        failed = [ln.split(" ", 1)[1].split(" - ")[0] for ln in proc.stdout.splitlines()
                  if ln.startswith("FAILED ")]
        errors = [ln for ln in proc.stdout.splitlines() if ln.startswith("ERROR ")]
        tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr[-200:]
        results.append({"id": mid, "file": rel, "what": what, "killed": bool(failed or errors
                        or proc.returncode != 0), "failed": failed, "errors": errors[:3],
                        "summary": tail})
        print(mid, "KILLED" if results[-1]["killed"] else "SURVIVED", len(failed), tail[:80],
              flush=True)
    after = {f: sha(REPO / f) for f in files}
    assert before == after, "a file was not restored"
    OUT.write_text(json.dumps(results, indent=1))
    print("restored ok;", sum(r.get("killed", False) for r in results), "killed of", len(results))


if __name__ == "__main__":
    main()
