"""Check 4 (VerdictVerifier-FableXHigh, Stage E.17): order of events and leakage in C1's run.

Read-only. Establishes from the log, the file times and the two JSON files that: the marker was
written before any bar was read (log order; marker mtime before result mtime; the marker's inputs
hold nothing bar-derived); the result and the log carry counts only (every numeric leaf outside the
pre-marker inputs block is an integer count, and the log's numbers after the marker are the C10
counts); no T1/T2 statistic, trade or verdict number exists (mean, t_B, p_one_sided, trades_sha256,
tests, descriptive, n_trades, r_hat absent). Writes reports/stage_e17_c1_verify/order_leakage.json.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

os.nice(10)

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports" / "stage_e17_c1_verify" / "order_leakage.json"
RESULT = REPO / "reports" / "stage_e14_c1_result.json"
MARKER = REPO / "reports" / "stage_e14_c1_RUN_ONCE.json"
LOG = REPO / "reports" / "stage_e17_briefs" / "c1_evaluate.log"
STAT_KEYS = ("mean", "mean_gross_ticks", "t_B", "p_one_sided", "trades_sha256", "tests", "descriptive",
             "n_trades", "r_hat", "bar_ticks", "decision", "c14_slippage_1_5x", "c15", "trades")
STAT_WORDS = ("mean", "t_B", "p_one_sided", "trades_sha256", "n_trades", "r_hat", "PASS", "FAIL")
# Non-integer numeric leaves allowed outside `inputs`: none. Inside `inputs` the pre-marker
# records hold shares (C12, calendar unsourced shares) and q (training-derived, in the model JSON).


def leaves(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, obj


def key_hits(obj, keys, path=""):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if k in keys:
                hits.append(p)
            hits += key_hits(v, keys, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += key_hits(v, keys, f"{path}[{i}]")
    return hits


def main() -> int:
    result = json.loads(RESULT.read_bytes())
    marker = json.loads(MARKER.read_bytes())
    log_lines = LOG.read_text().splitlines()
    rec: dict = {"schema": "stage_e17_c1_verify/order_leakage/1"}

    # Log order: the marker line precedes every C10 line and the verdict line.
    idx_marker = next(i for i, l in enumerate(log_lines) if l.startswith("C1 marker written"))
    idx_c10 = [i for i, l in enumerate(log_lines) if l.startswith("C10 ")]
    idx_verdict = next(i for i, l in enumerate(log_lines) if l.startswith("C1 verdict"))
    pre_marker = log_lines[:idx_marker]
    pre_marker_numbers = [l for l in pre_marker if re.search(r"\b\d+\b", l)
                          and not l.startswith("$ nice") and not re.match(r"^\w{3} \w{3}\s+\d+ ", l)]
    rec["log"] = {"lines": len(log_lines), "marker_line_index": idx_marker, "c10_line_indices": idx_c10,
                  "verdict_line_index": idx_verdict,
                  "marker_before_c10_and_verdict": all(idx_marker < i for i in idx_c10 + [idx_verdict]),
                  "pre_marker_lines": pre_marker,
                  "pre_marker_lines_with_numbers_other_than_date_and_command": pre_marker_numbers,
                  "post_marker_non_c10_lines": [l for l in log_lines[idx_marker + 1:]
                                                if not l.startswith("C10 ") and l.strip()][:12],
                  "stat_words_in_log": {w: sum(1 for l in log_lines if re.search(rf"\b{re.escape(w)}\b", l))
                                        for w in STAT_WORDS}}
    # Log C10 lines: every token after the signal name is an integer count.
    c10_tokens_non_int = []
    for i in idx_c10:
        body = log_lines[i].split("applicable rows per signal", 1)[1]
        for part in body.split(","):
            name, _, n = part.strip().rpartition(" ")
            if not re.fullmatch(r"\d+", n):
                c10_tokens_non_int.append(part.strip())
    rec["log"]["c10_tokens_not_integer"] = c10_tokens_non_int

    # File times.
    def mtime(p: Path) -> str:
        return datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat(timespec="microseconds")
    rec["mtimes"] = {"marker": mtime(MARKER), "result": mtime(RESULT), "log": mtime(LOG),
                     "marker_before_result": MARKER.stat().st_mtime < RESULT.stat().st_mtime,
                     "marker_started_local": marker["started_local"],
                     "result_started_local": result["started_local"],
                     "result_finished_local": result["finished_local"]}

    # The marker holds nothing bar-derived: its keys and the kinds of its inputs leaves.
    marker_keys = sorted(marker.keys())
    rec["marker"] = {"keys": marker_keys,
                     "has_guards_world_panel_or_tests": any(k in marker for k in ("guards", "world", "panel_counts", "tests", "descriptive")),
                     "inputs_keys": sorted(marker["inputs"].keys()),
                     "inputs_equal_result_inputs": marker["inputs"] == result["inputs"]}

    # Result: numeric leaves outside `inputs` are integer counts; stat keys absent.
    outside = {k: v for k, v in result.items() if k != "inputs"}
    non_int = [(p, type(v).__name__) for p, v in leaves(outside)
               if isinstance(v, (int, float)) and not isinstance(v, bool) and not isinstance(v, int)]
    numeric_outside = sum(1 for _, v in leaves(outside) if isinstance(v, (int, float)) and not isinstance(v, bool))
    float_inside = [p for p, v in leaves(result["inputs"]) if isinstance(v, float)]
    rec["result"] = {"top_keys": list(result.keys()), "verdict": result["verdict"],
                     "stop_reason": result["stop_reason"],
                     "numeric_leaves_outside_inputs": numeric_outside,
                     "non_integer_numeric_leaves_outside_inputs": non_int,
                     "float_leaves_inside_inputs": float_inside,
                     "stat_key_hits": key_hits(result, set(STAT_KEYS)),
                     "stat_word_hits_in_text": {w: len(re.findall(rf"\b{re.escape(w)}\b", RESULT.read_text()))
                                                for w in STAT_WORDS},
                     "guards_keys": sorted(result["guards"].keys()),
                     "world_roots": sorted(result["world"]["roots"].keys())}
    checks = {
        "marker_precedes_c10_and_verdict_in_log": rec["log"]["marker_before_c10_and_verdict"],
        "no_numbers_before_marker_except_date_and_command": not pre_marker_numbers,
        "log_c10_values_all_integer_counts": not c10_tokens_non_int,
        "marker_mtime_before_result_mtime": rec["mtimes"]["marker_before_result"],
        "marker_holds_no_bar_derived_block": not rec["marker"]["has_guards_world_panel_or_tests"],
        "marker_inputs_equal_result_inputs": rec["marker"]["inputs_equal_result_inputs"],
        "result_numeric_outside_inputs_all_integer": not non_int,
        "no_stat_keys_in_result": not rec["result"]["stat_key_hits"],
        "no_stat_words_in_result_text": all(n == 0 for n in rec["result"]["stat_word_hits_in_text"].values()),
        "no_stat_words_in_log": all(n == 0 for n in rec["log"]["stat_words_in_log"].values()),
        "guards_only_c10": rec["result"]["guards_keys"] == ["C10"],
    }
    rec["checks"] = checks
    rec["all_pass"] = all(checks.values())
    OUT.write_text(json.dumps(rec, indent=1, default=str) + "\n")
    for k, v in checks.items():
        print(f"{k}: {'ok' if v else 'FAIL'}")
    print(f"float leaves inside inputs (pre-marker records): {len(float_inside)} -> {float_inside[:12]}")
    print(f"post-marker non-C10 log lines: {rec['log']['post_marker_non_c10_lines'][:4]}")
    print(f"all pass: {rec['all_pass']}; written {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
