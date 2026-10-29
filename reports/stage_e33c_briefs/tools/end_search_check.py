"""Step 5 of the E.33c RESUME HERE block: end-of-search checks that open no outcome (lead tool, outside the pipeline).

Reads only: the resumed search log (timestamps, counts, the runner's "finished:" line, the wrapper's "rc=" line); the
"status" key of each configuration's DONE marker (the marker holds config, status, time, output sha256s, pipeline sha
and table fingerprint; search33.py 957, 992); the names of fold<k>.DONE / fold<k>.FAILED files (existence only); the
line count of fold<k>.attempts (start, pid and pipeline sha per attempt); the trial registry's N. It never opens
stats.json, daily/trades/not_made parquet, fold*.npz or fold*.model.json.
Usage: end_search_check.py <search root> <resumed log>
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SO_FAR_S = 6774.8  # measured at the 0.2 stop: build 2,387.0 + fits 4,387.8 s (protocol 0.3, P5; STATE)
STOP_AT_S = 36044.7  # 3 x R_0.3 (protocol 0.3, P5 and P10)
TS = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),(\d{3}) ")
SETS = ("S5", "S1", "S3", "S2", "S4")
LABELS = ("F15", "F30", "F05", "F60", "T15", "T30")
GRID = ("L001A", "L001E", "L010A", "L010E", "L100A", "L100E", "G2050", "G2200", "G3050", "G3200")


def stamp(line: str) -> float | None:
    m = TS.match(line)
    return None if not m else datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").timestamp() + int(m.group(2)) / 1000


def log_summary(lines: list) -> dict:
    first = finished_t = None
    finished_line = rc_line = None
    pauses, p0 = [], None
    fold_done, fit_s = 0, 0.0
    counts = {k: 0 for k in ("finalized (ok)", "finalized (failed)", "FAILED", "died", "raised", "WARNING", "ERROR")}
    for line in lines:
        if first is None and " INFO start E33-" in line:
            first = stamp(line)
        if "pausing submissions" in line:
            p0 = stamp(line)
        elif "collector window over: resuming" in line and p0 is not None:
            pauses.append((p0, stamp(line)))
            p0 = None
        m = re.search(r" fold \d done ([\d.]+) s$", line)
        if m:
            fold_done += 1
            fit_s += float(m.group(1))
        for k in counts:
            counts[k] += k in line
        if " finished: " in line:
            finished_line, finished_t = line, stamp(line)
        if line.startswith("rc="):
            rc_line = line
    pause_s = sum(b - a for a, b in pauses)
    resumed = None if first is None or finished_t is None else finished_t - first - pause_s
    return {"first_start": first, "finished_t": finished_t, "finished_line": finished_line, "rc_line": rc_line,
            "pauses": pauses, "open_pause": p0, "pause_s": pause_s, "resumed_net_s": resumed, "fold_done_lines": fold_done,
            "fold_fit_seconds_sum": fit_s, "counts": counts}


def marker_summary(root: Path, ids: list) -> dict:
    status, missing = {}, []
    fold_done = fold_failed = both = neither = multi_attempt = 0
    for cid in ids:
        base = root / "search" / cid
        done = base / "DONE"
        if not done.exists():
            missing.append(cid)
        else:
            status[cid] = json.loads(done.read_text()).get("status")
        for k in range(1, 7):
            d, f = (base / f"fold{k}.DONE").exists(), (base / f"fold{k}.FAILED").exists()
            fold_done += d
            fold_failed += f
            both += d and f
            neither += not d and not f
            att = base / f"fold{k}.attempts"
            if att.exists() and sum(1 for x in att.read_text().splitlines() if x.strip()) >= 2:
                multi_attempt += 1
    tally = {}
    for v in status.values():
        tally[v] = tally.get(v, 0) + 1
    return {"done_markers": len(status), "missing": missing, "status_tally": tally,
            "failed_configs": sorted(c for c, v in status.items() if v != "ok"), "fold_done": fold_done,
            "fold_failed": fold_failed, "fold_both": both, "fold_neither": neither,
            "folds_with_2plus_attempts": multi_attempt}


def main() -> int:
    root, log = Path(sys.argv[1]), Path(sys.argv[2])
    ids = [f"E33-{s}{lab}{g}" for s in SETS for lab in LABELS for g in GRID]
    assert len(ids) == 300 and len(set(ids)) == 300
    lg = log_summary(log.read_text().splitlines())
    mk = marker_summary(root, ids)
    iso = lambda t: None if t is None else datetime.fromtimestamp(t).isoformat(timespec="milliseconds")
    print(f"log {log}: first fold start {iso(lg['first_start'])}; finished line at {iso(lg['finished_t'])}")
    print(f"runner: {lg['finished_line']}")
    print(f"wrapper: {lg['rc_line']}")
    print(f"log counts: fold done lines {lg['fold_done_lines']} (fit seconds summed {lg['fold_fit_seconds_sum']:.1f}); "
          + "; ".join(f"{k} {v}" for k, v in lg["counts"].items()))
    print(f"pauses in the resumed log: {len(lg['pauses'])} ({lg['pause_s']:.1f} s); open pause: {lg['open_pause']}")
    if lg["resumed_net_s"] is not None:
        tot = SO_FAR_S + lg["resumed_net_s"]
        print(f"protocol 0.3 measured: {SO_FAR_S} (0.2 run) + {lg['resumed_net_s']:.1f} (resumed, first start to "
              f"finished line, net of pauses) = {tot:.1f} s against the 3x stop {STOP_AT_S} s: "
              f"{'BELOW' if tot <= STOP_AT_S else 'ABOVE'} ({tot / STOP_AT_S:.3f} of the stop)")
    print(f"config DONE markers {mk['done_markers']}/300; missing {len(mk['missing'])} {mk['missing'][:10]}; "
          f"status {mk['status_tally']}; not ok {mk['failed_configs']}")
    print(f"fold markers: DONE {mk['fold_done']}, FAILED {mk['fold_failed']}, both {mk['fold_both']}, "
          f"neither {mk['fold_neither']} (of 1,800); folds with 2+ attempt records {mk['folds_with_2plus_attempts']}")
    from screening import trial_registry as tr
    tr.require_registered(ids, test="E33")
    print(f"registry: require_registered(300, test=E33) ok; current_n {tr.current_n()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
