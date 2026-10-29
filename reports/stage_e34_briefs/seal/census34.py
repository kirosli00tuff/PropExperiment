"""Stage E.34 Part 0.1: names-only census of soy-complex files against the E.32 test seal.

Reads directory listings and os.stat (size, mtime) only. It never opens, decodes or hashes a data
file. Window: CME trade dates 2017-05-01..2020-11-30; raw vendor UTC spans are tested against
[2017-04-30T21:00Z, 2020-11-30T22:00Z) exactly as reports/stage_e32_briefs/seal/soy_test_seal.py does.

Usage: uv run python reports/stage_e34_briefs/seal/census34.py <out.tsv>
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[3]
PT = ZoneInfo("America/Vancouver")
SEAL_TIME = datetime(2026, 10, 26, 22, 55, 11, tzinfo=PT)
WIN_UTC = (datetime(2017, 4, 30, 21, tzinfo=timezone.utc), datetime(2020, 11, 30, 22, tzinfo=timezone.utc))
FIRST_TD, LAST_TD = "2017-05-01", "2020-11-30"
SCAN_ROOTS = (REPO, Path("/mnt/large-storage"), Path.home() / ".cache", Path("/tmp/claude-1000"))
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SOY_TOKEN = re.compile(r"(?i)(?<![a-z0-9])(m?z[lsm]|soy[a-z]*)(?![a-z0-9])")
DATA_EXT = (".dbn", ".zst", ".parquet", ".npy", ".npz", ".csv", ".feather", ".arrow", ".pkl", ".pickle",
            ".h5", ".hdf5", ".jsonl", ".gz", ".sealed")
R_RANGE = re.compile(r"(\d{4}-\d{2}-\d{2}(?:T\d{6}Z)?)_(\d{4}-\d{2}-\d{2}(?:T\d{6}Z)?)")
R_BATCH = re.compile(r"(?<!\d)(\d{8})-(\d{8})(?!\d)")
R_DAY = re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2})(?!\d)")


def stamp(text: str) -> datetime:
    if "T" in text:
        return datetime.strptime(text, "%Y-%m-%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    return datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def name_span(name: str) -> tuple[str, bool | None]:
    """(span text, touches window) from a file name; ("", None) when the name carries no span."""
    m = R_RANGE.search(name)
    if m:
        a, b = m.group(1), m.group(2)
        if name.startswith("range=") or "T" in a:  # raw vendor file: [start, end) in UTC
            sa, sb = stamp(a), stamp(b)
            return f"{a}..{b} (UTC, end excl.)", sa < WIN_UTC[1] and sb > WIN_UTC[0]
        return f"{a}..{b} (trade dates)", a <= LAST_TD and b >= FIRST_TD  # store: inclusive
    m = R_BATCH.search(name)
    if m:
        sa = datetime.strptime(m.group(1), "%Y%m%d").replace(tzinfo=timezone.utc)
        sb = datetime.strptime(m.group(2), "%Y%m%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
        return f"{m.group(1)}-{m.group(2)} (batch, end incl.)", sa < WIN_UTC[1] and sb > WIN_UTC[0]
    days = R_DAY.findall(name)
    if len(days) == 1:
        d = days[0]
        return f"{d} (single date)", FIRST_TD <= d <= LAST_TD
    return "", None


def manifest_paths() -> tuple[set[str], set[str]]:
    m = json.loads((REPO / "docs/soy_test/SOY_TEST_MANIFEST.json").read_text())
    originals = {r["original_relpath"] for r in m["raw_files"]}
    sealed = {r["sealed_relpath"] for r in m["raw_files"]}
    return originals, sealed


def derived_exceptions() -> set[str]:
    with open(REPO / "reports/stage_e32_briefs/seal/derived_unsealed_files.tsv") as fh:
        return {row["path"] for row in csv.DictReader(fh, delimiter="\t")}


def classify(path: Path, rel: str, soy: bool, originals: set[str], sealed: set[str],
             derived: set[str]) -> tuple[str, str]:
    span, touches = name_span(path.name)
    if rel.endswith(".sealed") and rel in sealed:
        return span, "sealed_blob"
    if "/sealed/" in str(path) or str(path).endswith(".sealed"):
        return span, "sealed_blob_other"
    if rel in originals:
        return span, "PROBLEM_manifest_original_in_plaintext"
    if str(path) in derived or rel in derived:
        return span, "derived_exception_OC-0.5"
    if "/rolls/" in str(path):
        return span, "rolls_exception_OC-0.4"
    if not soy:
        return span, "post_seal_data_no_soy_token"
    if touches is True:
        return span, "PROBLEM_span_touches_window"
    if touches is False:
        return span, "span_outside_window"
    return span, "soy_token_no_span"


def walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def main(out: str) -> int:
    originals, sealed = manifest_paths()
    derived = derived_exceptions()
    rows, seen = [], set()
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in walk(root):
            try:
                st = path.lstat()
            except OSError:
                continue
            if path.is_symlink() or not path.is_file():
                continue
            real = os.path.realpath(path)
            if real in seen:
                continue
            seen.add(real)
            soy = any(SOY_TOKEN.search(p) for p in path.parts[-4:])
            mtime = datetime.fromtimestamp(st.st_mtime, tz=PT)
            is_data = path.name.lower().endswith(DATA_EXT) or ".dbn" in path.name
            if not soy and not (is_data and mtime > SEAL_TIME):
                continue
            rel = os.path.relpath(real, os.path.realpath(REPO)) if real.startswith(str(REPO)) else str(path)
            rel_spelled = os.path.relpath(path, REPO) if str(path).startswith(str(REPO)) else rel
            span, cls = classify(path, rel_spelled, soy, originals, sealed, derived)
            if cls.startswith("PROBLEM") or cls == "soy_token_no_span":
                span2, cls2 = classify(path, rel, soy, originals, sealed, derived)
                if not cls2.startswith("PROBLEM") and cls2 != "soy_token_no_span":
                    span, cls = span2, cls2
            rows.append((str(path), st.st_size, mtime.strftime("%Y-%m-%d %H:%M:%S %Z"), span, cls))
    rows.sort()
    with open(out, "w") as fh:
        fh.write("path\tbytes\tmtime_local\tname_span\tclass\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    counts = Counter(r[4] for r in rows)
    print(f"census34: {len(rows)} rows -> {out}")
    for cls, n in sorted(counts.items()):
        print(f"  {cls}: {n}")
    tops = Counter()
    for p, _, _, _, cls in rows:
        if cls in ("post_seal_data_no_soy_token", "soy_token_no_span"):
            q = Path(p)
            tops[(cls, str(q.parent.parent) if len(q.parts) > 3 else str(q.parent))] += 1
    print("  by class and grandparent dir (no-span and post-seal no-token rows):")
    for (cls, d), n in sorted(tops.items()):
        print(f"    {cls} | {d}: {n}")
    problems = [r for r in rows if r[4].startswith("PROBLEM")]
    print(f"  PROBLEM rows: {len(problems)}")
    for r in problems[:50]:
        print("   ", r[0], r[3], r[4])
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "census34.tsv"))
