"""P10 3x stop for the E.33 search (lead, decided in STATE before any result).

Measured = feature build 2,387 s + fits wall time from the first real-outcome fit (14:29:04), net of the logged
collector-window pause ('pausing submissions' to 'collector window over: resuming'). Stop at once (TERM, then KILL
the search's process group) when measured > 6,767.5 s, i.e. fits net > 4,380.5 s. Exits early if the search ends.
"""
import json
import os
import re
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

LOG = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e33_briefs/work/logs/search_real.log")
OUT = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e33_briefs/work/logs/p10_stop.json")
PGID = int(sys.argv[1])
START = datetime(2026, 10, 28, 14, 29, 4).timestamp()
BUILD_S = 2387.0
REF_3X = 6767.5
TS = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),(\d{3}) ")


def stamp(line: str) -> float | None:
    m = TS.match(line)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").timestamp() + int(m.group(2)) / 1000


def pause_seconds(lines: list, now: float) -> tuple:
    p0 = p1 = None
    for line in lines:
        if "pausing submissions" in line:
            p0 = stamp(line)
        elif "collector window over: resuming" in line:
            p1 = stamp(line)
    if p0 is None:
        return 0.0, p0, p1
    return ((p1 if p1 is not None else now) - p0), p0, p1


def alive() -> bool:
    try:
        os.killpg(PGID, 0)
        return True
    except ProcessLookupError:
        return False


while True:
    now = time.time()
    lines = LOG.read_text().splitlines()
    if any(line.startswith("rc=") for line in lines) or not alive():
        print(json.dumps({"event": "search ended by itself", "time": datetime.now().isoformat(timespec="seconds")}))
        break
    pause, p0, p1 = pause_seconds(lines, now)
    fits_net = now - START - pause
    measured = BUILD_S + fits_net
    if measured > REF_3X:
        rec = {"event": "P10 3x stop", "stop_time": datetime.now().isoformat(timespec="seconds"),
               "first_fit": datetime.fromtimestamp(START).isoformat(timespec="seconds"),
               "pause_start": p0 and datetime.fromtimestamp(p0).isoformat(timespec="seconds"),
               "pause_end": p1 and datetime.fromtimestamp(p1).isoformat(timespec="seconds"),
               "pause_s": round(pause, 1), "fits_net_s": round(fits_net, 1), "build_s": BUILD_S,
               "measured_s": round(measured, 1), "reference_3x_s": REF_3X}
        os.killpg(PGID, signal.SIGTERM)
        for _ in range(30):
            time.sleep(1)
            if not alive():
                break
        rec["killed_with"] = "SIGTERM" if not alive() else "SIGKILL"
        if alive():
            os.killpg(PGID, signal.SIGKILL)
        OUT.write_text(json.dumps(rec, indent=1) + "\n")
        print(json.dumps(rec))
        break
    time.sleep(10)
