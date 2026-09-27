"""MemberAuditor-K5 (Task 3, item 11): mutation check of the K5 tests, run on a SCRATCH COPY of the
repository (never on the repository itself). Each mutant is one textual replacement in one K5
member file; the relevant test files run; a mutant is "killed" when at least one test fails.
Prints one line per mutant: id, killed?, failed-test count, up to 3 failing test names.

Usage: python mutants.py <scratch_repo> <project_dir>
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRATCH, PROJECT = Path(sys.argv[1]), Path(sys.argv[2])
K5 = SCRATCH / "strategy/members/k5"
A = "tests/test_e4_k5_members_a.py"
AO = "tests/test_e4_k5_members_a_ovr.py"
B = "tests/test_e4_k5_members_b.py"
BS = "tests/test_e4_k5_members_b_signal.py"

# (id, file, old, new, test files)
MUTANTS = [
    ("preauc entry T-31 -> T-30", "preauc.py", "ENTRY_DECISION_OFFSET_MIN = -31", "ENTRY_DECISION_OFFSET_MIN = -30", [B]),
    ("preauc exit T-2 -> T-3", "preauc.py", "EXIT_DECISION_OFFSET_MIN = -2", "EXIT_DECISION_OFFSET_MIN = -3", [B]),
    ("preauc side SELL -> buy", "preauc.py", "SIDE = SELL", 'SIDE = "buy"', [B]),
    ("preauc early-halt check removed", "preauc.py",
     "if account.pending.get(self.root, 0) or bar.early_halt_ct is not None:",
     "if account.pending.get(self.root, 0):", [B]),
    ("preauc 5h window end 05:30 -> 05:29", "preauc.py", "TradingInterval(time(4, 59), time(5, 30))",
     "TradingInterval(time(4, 59), time(5, 29))", [B]),
    ("preauc entry_done flag removed", "preauc.py", "self._entry_done = True  # the named entry bar",
     "pass  # the named entry bar", [B]),
    ("pmfix signal start T_P-1 -> T_P-2", "pmfix.py", "SIGNAL_START_OFFSET_MIN = -1", "SIGNAL_START_OFFSET_MIN = -2", [BS]),
    ("pmfix entry T_P+1 -> T_P+2", "pmfix.py", "ENTRY_DECISION_OFFSET_MIN = 1", "ENTRY_DECISION_OFFSET_MIN = 2", [BS]),
    ("pmfix exit T_P+11 -> T_P+12", "pmfix.py", "EXIT_DECISION_OFFSET_MIN = 11", "EXIT_DECISION_OFFSET_MIN = 12", [BS]),
    ("fomc signal 12:59 -> 12:58", "fomc.py", "SIGNAL_START_CT = time(12, 59)", "SIGNAL_START_CT = time(12, 58)", [BS]),
    ("fomc entry 13:04 -> 13:05", "fomc.py", "ENTRY_DECISION_CT = time(13, 4)", "ENTRY_DECISION_CT = time(13, 5)", [BS]),
    ("fomc exit 13:14 -> 13:15", "fomc.py", "EXIT_DECISION_CT = time(13, 14)", "EXIT_DECISION_CT = time(13, 15)", [BS]),
    ("event s==0 no-trade removed", "_event_common.py", "if s == 0:", "if False:", [BS]),
    ("event sign flipped", "_event_common.py", "BUY if s > 0 else SELL", "SELL if s > 0 else BUY", [BS]),
    ("event instrument guard removed", "_event_common.py", "if start[1] != bar.instrument_id:", "if False:", [BS]),
    ("event exit one bar later (<=)", "_event_common.py", "bar.ts_event_ns < exit_ns", "bar.ts_event_ns <= exit_ns", [B, BS]),
    ("event pending-exit check removed", "_event_common.py",
     "if pending and (pending > 0) != (position > 0):", "if False:", [B, BS]),
    ("event early-halt check removed", "_event_common.py",
     "if account.pending.get(self.root, 0) or bar.early_halt_ct is not None:",
     "if account.pending.get(self.root, 0):", [BS]),
    ("cp1 signal O+29 -> O+28", "cp1.py", "SIGNAL_AFTER_O_MIN = 29", "SIGNAL_AFTER_O_MIN = 28", [A]),
    ("cp1 entry C-31 -> C-30", "cp1.py", "ENTRY_BEFORE_C_MIN = 31", "ENTRY_BEFORE_C_MIN = 30", [A]),
    ("cp1 exit C-2 -> C-3", "cp1.py", "EXIT_BEFORE_C_MIN = 2", "EXIT_BEFORE_C_MIN = 3", [A]),
    ("cp1 id guard removed", "cp1.py", "if first_id != signal_id:", "if False:", [A]),
    ("cp1 zero signal -> sell", "cp1.py", "if s == 0:", "if False:", [A]),
    ("cp1 globex bar date check removed", "cp1.py", "if opened.date() == day - ONE_DAY and at == GLOBEX_OPEN_CT:",
     "if at == GLOBEX_OPEN_CT:", [A]),
    ("cp2 buffer 4 -> 3", "cp2.py", "BUFFER_TICKS = 4", "BUFFER_TICKS = 3", [A]),
    ("cp2 hold 75 -> 74", "cp2.py", "HOLD_BARS = 75", "HOLD_BARS = 74", [A]),
    ("cp2 range 15 -> 14", "cp2.py", "RANGE_MINUTES = 15", "RANGE_MINUTES = 14", [A]),
    ("cp2 entry allowed at C", "cp2.py", "if not self._range_end <= at < self._leg.c", "if not self._range_end <= at <= self._leg.c", [A]),
    ("cp2 sell trigger strict", "cp2.py", "elif close <= to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:",
     "elif close < to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:", [A]),
    ("cp3 buy cut 0.8 -> 0.81", "cp3.py", 'CLV_BUY_AT_OR_ABOVE = Decimal("0.8")', 'CLV_BUY_AT_OR_ABOVE = Decimal("0.81")', [A]),
    ("cp3 sell cut 0.2 -> 0.19", "cp3.py", 'CLV_SELL_AT_OR_BELOW = Decimal("0.2")', 'CLV_SELL_AT_OR_BELOW = Decimal("0.19")', [A]),
    ("cp3 C_d at C-2", "cp3.py", "CLOSE_BEFORE_C_MIN = 1", "CLOSE_BEFORE_C_MIN = 2", [A]),
    ("cp3 day-d halt check removed", "cp3.py",
     "        if bar.early_halt_ct is not None:\n            return None  # an early-halt day d",
     "        if False:\n            return None  # an early-halt day d", [A]),
    ("cp3 instrument guard removed", "cp3.py", "if prior.instrument_id != bar.instrument_id:", "if False:", [A]),
    ("cp3 zero range allowed", "cp3.py", "if span <= 0:", "if span < 0:", [A]),
    ("cp3 incomplete (two ids) day kept", "cp3.py", "and len(self._ids) == 1)", "and len(self._ids) >= 1)", [A]),
    ("ovr exit t+58 -> t+57", "ovr.py", "EXIT_AFTER_T_MIN = 58", "EXIT_AFTER_T_MIN = 57", [AO]),
    ("ovr reference dates 20 -> 19", "ovr.py", "REFERENCE_DATES = 20", "REFERENCE_DATES = 19", [AO]),
    ("ovr floor 80% -> 79%", "ovr.py", "VALUE_FLOOR_PERCENT = 80", "VALUE_FLOOR_PERCENT = 79", [AO]),
    ("ovr floor 80% -> 81%", "ovr.py", "VALUE_FLOOR_PERCENT = 80", "VALUE_FLOOR_PERCENT = 81", [AO]),
    ("ovr percentiles 10/90 -> 11/89", "ovr.py", "LOW_PERCENTILE, HIGH_PERCENTILE = 10, 90", "LOW_PERCENTILE, HIGH_PERCENTILE = 11, 89", [AO]),
    ("ovr C10 open<=0 -> open<0", "ovr.py", "if open_ticks <= 0:", "if open_ticks < 0:", [AO]),
    ("ovr early-halt check removed", "ovr.py",
     "        if bar.early_halt_ct is not None:\n            return None  # an early-halt trade date",
     "        if False:\n            return None  # an early-halt trade date", [AO]),
    ("ovr warm-up removed", "ovr.py",
     "if len(refs) < REFERENCE_DATES or self._first_day is None or refs[0] < self._first_day:",
     "if len(refs) < REFERENCE_DATES:", [AO]),
    ("ovr floor off by one", "ovr.py", "if len(values) < self._min_values:", "if len(values) < self._min_values - 1:", [AO]),
    ("ovr t=C excluded", "ovr.py", "range(DECISION_STEP_MIN, span + 1, DECISION_STEP_MIN)", "range(DECISION_STEP_MIN, span, DECISION_STEP_MIN)", [AO]),
    ("ovr tie -> buy", "ovr.py", "if at_low == at_high:", "if False:", [AO]),
    ("ovr entry while pending allowed", "ovr.py", "if t is None or not is_flat(account, self.root):", "if t is None or account.position(self.root):", [AO]),
    ("ovr per-t id guard removed", "ovr.py", "if open_id != bar.instrument_id:", "if False:", [AO]),
    ("releases: extra FOMC date", "_releases.py", "__all__ = [", 'FOMC_STATEMENT_DATES = FOMC_STATEMENT_DATES + ("2025-06-19",)\n__all__ = [', [B]),
    ("releases: PM no-auction day added back", "_releases.py", "__all__ = [", 'GOLD_PM_AUCTIONS = GOLD_PM_AUCTIONS + (("2025-12-31", "09:00"),)\n__all__ = [', [B]),
    ("releases: one AM row dropped", "_releases.py", '("2025-10-28", "05:30"),', "", [B]),
    ("calendar: early-halt date added", "_calendar.py", "\n# ISO dates, oldest first", '\nMETALS_FULL_SESSIONS_EXTRA = ("2025-07-04",)\n# ISO dates, oldest first', [A]),
]
EXTRA = [
    ("calendar: early-halt date inserted in the table", "_calendar.py", '"2025-07-03",',
     '"2025-07-03", "2025-07-04",', [A, AO]),
    ("ovr history pruning drops the oldest reference date", "ovr.py",
     "self._history = {d: v for d, v in merged.items() if d >= oldest}",
     "self._history = {d: v for d, v in merged.items() if d > oldest}", [AO]),
    ("cp3 complete day without the O bar", "cp3.py",
     "complete = (self._has_open_bar and self._close is not None and not self._halt",
     "complete = (self._close is not None and not self._halt", [A]),
    ("cp2 range end exclusive -> inclusive", "cp2.py", "if self._leg.o <= at < self._range_end:",
     "if self._leg.o <= at <= self._range_end:", [A]),
    ("cp2 hold count not reset across days", "cp2.py",
     "self._day, self._hi, self._lo, self._triggered, self._held = day, None, None, False, 0",
     "self._day, self._hi, self._lo, self._triggered = day, None, None, False", [A]),
]
if len(sys.argv) > 3 and sys.argv[3] == "--extra":
    MUTANTS = EXTRA


def run_tests(files: list[str]) -> tuple[int, list[str]]:
    cmd = ["nice", "-n", "10", "uv", "run", "--project", str(PROJECT), "python", "-m", "pytest",
           "-q", "-rf", "-p", "no:cacheprovider", *files]
    env = {"PYTHONPATH": str(SCRATCH), "PATH": subprocess.os.environ["PATH"],
           "HOME": subprocess.os.environ["HOME"]}
    out = subprocess.run(cmd, cwd=SCRATCH, capture_output=True, text=True, env=env).stdout
    failed = [l.split("::")[-1].split(" ")[0] for l in out.splitlines() if l.startswith("FAILED")]
    m = re.search(r"(\d+) failed", out)
    n = int(m.group(1)) if m else 0
    if "error" in out.lower() and n == 0 and "passed" not in out:
        return -1, [out.strip().splitlines()[-1][:120]]
    return n, failed


def main() -> None:
    pristine = {f.name: f.read_text() for f in K5.glob("*.py")}
    try:
        survivors = []
        for mid, fname, old, new, tests in MUTANTS:
            src = pristine[fname]
            if src.count(old) != 1:
                print(f"SKIP {mid}: pattern count {src.count(old)}")
                continue
            (K5 / fname).write_text(src.replace(old, new))
            n, failed = run_tests(tests)
            (K5 / fname).write_text(src)
            status = "killed" if n > 0 else ("ERROR" if n < 0 else "SURVIVED")
            if n <= 0:
                survivors.append(mid)
            print(f"{status:8} {n:3} | {mid} | {', '.join(failed[:3])}")
        print("survivors:", survivors)
    finally:
        for name, src in pristine.items():
            (K5 / name).write_text(src)
        shutil.rmtree(K5 / "__pycache__", ignore_errors=True)


if __name__ == "__main__":
    main()
