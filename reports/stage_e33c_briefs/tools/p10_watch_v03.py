"""P10 3x stop under protocol 0.3 (V53) for the resumed E.33 search, plus the 2 GB memory rule (lead tool, outside the
selection pipeline; constants from reports/stage_e33c_briefs/ref_v03.json and protocol 0.3, P5).

Measured = 6,774.8 s at the 0.2 stop (build 2,387.0 + fits 4,387.8; p10_stop.json) + the resumed fits' wall time from the
resumed run's first fold start, net of logged collector-window pauses. Stop at once (TERM, then KILL the search's
process group) when measured > 3 x R_0.3 = 36,044.7 s. Memory: if MemAvailable stays below 2,048 MB for 60 s, stop the
same way (E.33 prompt: stop a job if free memory falls below 2 GB). A heartbeat line every 60 s. Exits when the
search ends. Usage: p10_watch_v03.py <pgid> <search log> <stop json>
"""
import json
import os
import re
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

PGID = int(sys.argv[1])
LOG = Path(sys.argv[2])
OUT = Path(sys.argv[3])
SO_FAR_S = 6774.8
STOP_AT_S = 36044.7
MEM_FLOOR_MB = 2048
MEM_GRACE_CHECKS = 6
CHECK_S = 10
TS = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),(\d{3}) ")


def stamp(line: str) -> float | None:
    m = TS.match(line)
    return None if not m else datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").timestamp() + int(m.group(2)) / 1000


def iso(t: float | None) -> str | None:
    return None if t is None else datetime.fromtimestamp(t).isoformat(timespec="seconds")


def avail_mb() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) // 1024
    return -1


def alive() -> bool:
    try:
        os.killpg(PGID, 0)
        return True
    except ProcessLookupError:
        return False


def scan(lines: list, now: float) -> dict:
    first = None
    pauses, p0 = [], None
    done = final = 0
    for line in lines:
        if first is None and " INFO start E33-" in line:
            first = stamp(line)
        if "pausing submissions" in line:
            p0 = stamp(line)
        elif "collector window over: resuming" in line and p0 is not None:
            pauses.append((p0, stamp(line)))
            p0 = None
        if re.search(r" fold \d done [\d.]+ s$", line):
            done += 1
        if " finalized (" in line:
            final += 1
    pause_s = sum(b - a for a, b in pauses) + ((now - p0) if p0 is not None else 0.0)
    resumed = 0.0 if first is None else max(0.0, now - first - pause_s)
    return {"first_start": first, "pauses": pauses, "open_pause": p0, "pause_s": pause_s, "resumed_net_s": resumed,
            "measured_s": SO_FAR_S + resumed, "folds_done": done, "finalized": final}


def stop(event: str, info: dict, extra: dict) -> None:
    rec = {"event": event, "stop_time": datetime.now().isoformat(timespec="seconds"),
           "resumed_first_start": iso(info["first_start"]), "pauses": [[iso(a), iso(b)] for a, b in info["pauses"]],
           "pause_s": round(info["pause_s"], 1), "resumed_net_s": round(info["resumed_net_s"], 1),
           "so_far_at_0.2_stop_s": SO_FAR_S, "measured_s": round(info["measured_s"], 1),
           "stop_at_s": STOP_AT_S, "folds_done_in_resumed_log": info["folds_done"], **extra}
    os.killpg(PGID, signal.SIGTERM)
    for _ in range(30):
        time.sleep(1)
        if not alive():
            break
    rec["killed_with"] = "SIGTERM" if not alive() else "SIGKILL"
    if alive():
        os.killpg(PGID, signal.SIGKILL)
    OUT.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps(rec), flush=True)


def main() -> None:
    low, min_avail, last_beat = 0, 10 ** 9, 0.0
    print(json.dumps({"event": "watcher start", "time": datetime.now().isoformat(timespec="seconds"), "pgid": PGID,
                      "log": str(LOG), "so_far_s": SO_FAR_S, "stop_at_s": STOP_AT_S}), flush=True)
    while True:
        now = time.time()
        lines = LOG.read_text().splitlines() if LOG.exists() else []
        info = scan(lines, now)
        mem = avail_mb()
        min_avail = min(min_avail, mem)
        if any(line.startswith("rc=") for line in lines) or not alive():
            print(json.dumps({"event": "search ended", "time": datetime.now().isoformat(timespec="seconds"),
                              "rc_line": next((x for x in lines if x.startswith("rc=")), None),
                              "resumed_net_s": round(info["resumed_net_s"], 1),
                              "measured_s": round(info["measured_s"], 1), "folds_done": info["folds_done"],
                              "finalized": info["finalized"], "min_avail_mb": min_avail}), flush=True)
            return
        if info["measured_s"] > STOP_AT_S:
            stop("P10 3x stop (protocol 0.3)", info, {"min_avail_mb": min_avail})
            return
        low = low + 1 if 0 <= mem < MEM_FLOOR_MB else 0
        if low >= MEM_GRACE_CHECKS:
            stop("memory stop (2 GB rule)", info, {"avail_mb": mem, "min_avail_mb": min_avail})
            return
        if now - last_beat >= 60:
            last_beat = now
            print(json.dumps({"beat": datetime.now().isoformat(timespec="seconds"),
                              "resumed_net_s": round(info["resumed_net_s"], 1),
                              "measured_s": round(info["measured_s"], 1), "folds_done": info["folds_done"],
                              "finalized": info["finalized"], "avail_mb": mem}), flush=True)
        time.sleep(CHECK_S)


if __name__ == "__main__":
    main()
