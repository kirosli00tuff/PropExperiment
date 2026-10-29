"""Pure-extraction parser for the E.33 search log (stdlib only).

Usage: python3 -I parse_fold_times.py <log> <outdir>
Writes <outdir>/fold_times_real.csv and <outdir>/fold_times_summary.md.
No value is adjusted, ranked or interpreted; unmatched lines are listed.
"""

import csv
import os
import re
import sys
from collections import defaultdict

TS = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})"
LINE_RE = re.compile(r"^" + TS + r" ([A-Z]+) (.*)$")
CFG = (
    r"E33-(S[1-5])(F05|F15|F30|F60|T15|T30)"
    r"(L001A|L001E|L010A|L010E|L100A|L100E|G2050|G2200|G3050|G3200)"
)
START_RE = re.compile(r"^start " + CFG + r" fold (\d+) \((\d+) thr; pid (\d+); (\d+) MB available\)$")
DONE_RE = re.compile(r"^" + CFG + r" fold (\d+) done (\d+\.\d+) s$")
FIN_RE = re.compile(r"^" + CFG + r" finalized \((\w+)\) in (\d+\.\d+) s$")
WIN_PAUSE_RE = re.compile(r"^collector window \d{2}:\d{2}-\d{2}:\d{2} PT: pausing submissions$")
WIN_OVER_RE = re.compile(r"^collector window over: resuming$")
HDR_REGISTRY_RE = re.compile(r"^registration checked for \d+ ids$")
HDR_MANIFEST_RE = re.compile(r"^manifest \{.*$")
HDR_TASKS_RE = re.compile(r"^\d+ fold tasks to run \(\d+ configs\)$")
MODEL_BY_GRID = {"L": "LOGIT", "G": "LGBM"}
SNIPPET_LEN = 100


def split_line(raw):
    """Return (timestamp or None, body) for one raw log line."""
    match = LINE_RE.match(raw)
    if match:
        return match.group(1), match.group(3)
    return None, raw


def config_parts(set_id, label, grid):
    return {
        "config_id": f"E33-{set_id}{label}{grid}",
        "set": set_id,
        "label": label,
        "model": MODEL_BY_GRID[grid[0]],
        "grid": grid,
    }


def parse_log(log_path):
    """Scan the log once. Returns dict of parsed records and counters."""
    starts = {}      # (config, fold) -> dict with first/last/n/line
    dones = {}       # (config, fold) -> list of (ts, seconds, line)
    done_orphans = []
    finalized = defaultdict(list)  # status -> list of (line, ts)
    windows_pause, windows_over = [], []
    headers, unmatched = [], []
    first_start_ts, last_line = None, None
    line_count = 0
    with open(log_path, encoding="utf-8", errors="replace") as handle:
        for line_no, raw in enumerate(handle, start=1):
            text = raw.rstrip("\r\n")
            line_count = line_no
            if text.strip():
                last_line = (line_no, text)
            ts, body = split_line(text)
            if _take_start(body, ts, line_no, starts) is not None:
                first_start_ts = first_start_ts or ts
                continue
            if _take_done(body, ts, line_no, dones):
                continue
            fin = FIN_RE.match(body)
            if fin and ts is not None:
                finalized[fin.group(4)].append((line_no, ts))
                continue
            if WIN_PAUSE_RE.match(body) and ts is not None:
                windows_pause.append((line_no, ts, text))
                continue
            if WIN_OVER_RE.match(body) and ts is not None:
                windows_over.append((line_no, ts, text))
                continue
            if _is_header(body):
                headers.append((line_no, text))
                continue
            unmatched.append((line_no, text))
    return {
        "starts": starts,
        "dones": dones,
        "done_orphans": done_orphans,
        "finalized": finalized,
        "windows_pause": windows_pause,
        "windows_over": windows_over,
        "headers": headers,
        "unmatched": unmatched,
        "first_start_ts": first_start_ts,
        "last_line": last_line,
        "line_count": line_count,
    }


def _take_start(body, ts, line_no, starts):
    match = START_RE.match(body)
    if not match or ts is None:
        return None
    key = (f"E33-{match.group(1)}{match.group(2)}{match.group(3)}", int(match.group(4)))
    record = starts.get(key)
    if record is None:
        record = {"first": ts, "last": ts, "n": 0, "last_line": line_no}
        starts[key] = record
    record["n"] += 1
    record["last"] = ts
    record["last_line"] = line_no
    return True


def _take_done(body, ts, line_no, dones):
    match = DONE_RE.match(body)
    if not match or ts is None:
        return False
    key = (f"E33-{match.group(1)}{match.group(2)}{match.group(3)}", int(match.group(4)))
    dones.setdefault(key, []).append((ts, match.group(5), line_no))
    return True


def _is_header(body):
    return bool(
        HDR_REGISTRY_RE.match(body) or HDR_MANIFEST_RE.match(body) or HDR_TASKS_RE.match(body)
    )


def build_rows(parsed):
    rows = []
    for (config_id, fold), start in parsed["starts"].items():
        set_id, label, grid = _split_config(config_id)
        done_list = parsed["dones"].get((config_id, fold), [])
        done = done_list[0] if done_list else None
        rows.append({
            "config_id": config_id,
            "set": set_id,
            "label": label,
            "model": MODEL_BY_GRID[grid[0]],
            "grid": grid,
            "fold": fold,
            "n_starts": start["n"],
            "first_start": start["first"],
            "last_start": start["last"],
            "start_line": start["last_line"],
            "done_time": done[0] if done else "",
            "done_line": done[2] if done else "",
            "seconds": done[1] if done else "",
            "status": "done" if done else "cut",
            "_done_count": len(done_list),
        })
    rows.sort(key=lambda r: (r["first_start"], r["config_id"], int(r["fold"])))
    return rows


def _split_config(config_id):
    match = re.match(r"^E33-(S[1-5])(F05|F15|F30|F60|T15|T30|T\d\d)(\w+)$", config_id)
    return match.group(1), match.group(2), match.group(3)


CSV_COLUMNS = [
    "config_id", "set", "label", "model", "grid", "fold", "n_starts",
    "first_start", "last_start", "start_line", "done_time", "done_line",
    "seconds", "status",
]


def write_csv(rows, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _stats(values):
    if not values:
        return None
    total = sum(values)
    return {
        "count": len(values),
        "sum": total,
        "mean": total / len(values),
        "min": min(values),
        "max": max(values),
    }


def _fmt(value):
    return f"{value:.1f}"


def summary_lines(parsed, rows):
    out = ["# Fold timing summary (E.33c, FoldTimes-HaikuMed)", ""]
    out.append(f"Source: reports/stage_e33_briefs/work/logs/search_real.log ({parsed['line_count']} lines).")
    out.append("")
    out.append(f"- Total rows: {len(rows)}")
    status_counts = defaultdict(int)
    for row in rows:
        status_counts[row["status"]] += 1
    for status in sorted(status_counts):
        out.append(f"- Rows with status `{status}`: {status_counts[status]}")
    out.append(f"- Rows with more than one done line: {sum(1 for r in rows if r['_done_count'] > 1)}")
    out.append("")
    out.append("## Seconds per (set, model), done rows only")
    out.append("")
    out.append("| set | model | count done | sum | mean | min | max |")
    out.append("|---|---|---|---|---|---|---|")
    groups = defaultdict(list)
    for row in rows:
        if row["status"] == "done":
            groups[(row["set"], row["model"])].append(float(row["seconds"]))
    for set_id in sorted({r["set"] for r in rows}):
        for model in ("LOGIT", "LGBM"):
            stats = _stats(groups.get((set_id, model), []))
            if stats is None:
                out.append(f"| {set_id} | {model} | 0 | | | | |")
            else:
                out.append(
                    f"| {set_id} | {model} | {stats['count']} | {_fmt(stats['sum'])} | "
                    f"{_fmt(stats['mean'])} | {_fmt(stats['min'])} | {_fmt(stats['max'])} |"
                )
    out.append("")
    out.append("## Finalized lines")
    out.append("")
    for status in sorted(set(parsed["finalized"]) | {"ok", "failed"}):
        out.append(f"- `finalized ({status})`: {len(parsed['finalized'].get(status, []))}")
    out.append("")
    out.append("## Collector window lines")
    out.append("")
    for line_no, ts, text in parsed["windows_pause"]:
        out.append(f"- line {line_no} at {ts}: `{text}`")
    for line_no, ts, text in parsed["windows_over"]:
        out.append(f"- line {line_no} at {ts}: `{text}`")
    if not parsed["windows_pause"] and not parsed["windows_over"]:
        out.append("- None found.")
    out.append("")
    out.append("## Header lines (matched the brief's header formats)")
    out.append("")
    for line_no, text in parsed["headers"]:
        out.append(f"- line {line_no}: {text[:SNIPPET_LEN]}")
    out.append("")
    out.append("## Timing anchors")
    out.append("")
    out.append(f"- First start line timestamp: {parsed['first_start_ts']}")
    if parsed["last_line"]:
        last_no, last_text = parsed["last_line"]
        out.append(f"- Last non-empty line {last_no}: `{last_text}`")
    out.append("")
    out.append("## Done lines with no matching start line")
    out.append("")
    out.append(f"- Count: {len(parsed['done_orphans'])}")
    out.append("")
    out.append("## Unmatched lines (matched no format)")
    out.append("")
    out.append(f"- Count: {len(parsed['unmatched'])}")
    for line_no, text in parsed["unmatched"]:
        out.append(f"- line {line_no}: {text[:SNIPPET_LEN]}")
    out.append("")
    return out


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: parse_fold_times.py <log> <outdir>\n")
        return 2
    log_path, outdir = argv[1], argv[2]
    os.makedirs(outdir, exist_ok=True)
    parsed = parse_log(log_path)
    orphan_keys = set(parsed["dones"]) - set(parsed["starts"])
    for key in sorted(orphan_keys):
        for ts, seconds, line_no in parsed["dones"][key]:
            parsed["done_orphans"].append((line_no, key[0], key[1]))
    rows = build_rows(parsed)
    write_csv(rows, os.path.join(outdir, "fold_times_real.csv"))
    with open(os.path.join(outdir, "fold_times_summary.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(summary_lines(parsed, rows)) + "\n")
    print(f"rows={len(rows)} unmatched={len(parsed['unmatched'])} "
          f"finalized={sum(len(v) for v in parsed['finalized'].values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
