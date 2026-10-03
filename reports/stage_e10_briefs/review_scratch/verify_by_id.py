"""Per-passage-id re-verification of the K9 draft catalog's quotes.

For every row of the catalog's section 8 table, locate in the catalog text each quoted string that is
followed (within 120 characters) by that passage id, and search the quote in the saved file the row
names, with the same normalization as verify_quotes.py. Writes review_scratch/quote_by_id.tsv and
prints one compact line per id.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "reports/stage_e10_catalog_K9.md"
OUT = ROOT / "reports/stage_e10_briefs/review_scratch/quote_by_id.tsv"


def norm(s: str) -> str:
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("−", "-").replace("­", "")
    s = s.replace("ﬁ", "fi").replace("ﬂ", "fl").replace(" ", " ").replace("¤", "ff")
    s = re.sub(r"-\n\s*", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def nohyph(s: str) -> str:
    return re.sub(r"(?<=[a-z])- (?=[a-z])", "", s)


def line_index(raw: str):
    lines = raw.split("\n")
    starts, parts, pos = [], [], 0
    for ln in lines:
        n = norm(ln)
        starts.append(pos)
        parts.append(n)
        pos += len(n) + 1
    return " ".join(parts), starts


def line_of(starts, off):
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= off:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


def main() -> None:
    text = CATALOG.read_text()
    flat = re.sub(r"\n\s*", " ", text)
    # section 8 rows: | id | file | line | status | use |
    rows = re.findall(r"^\| ((?:P|C|CAL|RUL|DT|LOG|D9|F9|K8)-[A-Za-z0-9#.-]+(?: \([^)]*\))?) \| ([^|]+?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \|$", text, flags=re.M)
    cache: dict[str, tuple[str, list[int]]] = {}
    out_lines = ["id\tfile\tclaimed_line\tquotes_located\tresult"]
    summary = {"ok": 0, "notfound": 0, "noquote": 0}
    for pid_full, fpath, claimed, status, use in rows:
        pid = re.sub(r"#\d+$", "", pid_full.split(" ")[0])
        base = re.sub(r"\.\d+$", "", pid)
        f = ROOT / fpath.strip()
        if not f.exists():
            out_lines.append(f"{pid_full}\t{fpath}\t{claimed}\t0\tFILE MISSING")
            continue
        if fpath not in cache:
            cache[fpath] = line_index(f.read_text(errors="replace"))
        joined, starts = cache[fpath]
        # quotes followed by this id (allow the id to appear as part of a list like (P-X-a, -b))
        pat = re.compile(r'"([^"]{10,}?)"[^"]{0,160}?' + re.escape(pid))
        quotes = [m.group(1) for m in pat.finditer(flat)]
        # also the short-id form "-26" inside "(C-K9R-001-25, -26)": search for the base with suffix
        results = []
        for q in quotes:
            nq = norm(q)
            off = joined.find(nq)
            how = "verbatim"
            if off < 0:
                off2 = nohyph(joined).find(nohyph(nq))
                if off2 >= 0:
                    off = joined.find(nq[:20]) if joined.find(nq[:20]) >= 0 else off2
                    how = "hyphen"
            if off < 0 and "[...]" in q:
                pieces = [norm(p) for p in q.split("[...]") if len(p.strip()) >= 10]
                if pieces and all(joined.find(p) >= 0 for p in pieces):
                    off = joined.find(pieces[0])
                    how = "pieces"
            if off >= 0:
                results.append(f"L{line_of(starts, off)}:{how}")
            else:
                results.append("NOTFOUND")
        if not quotes:
            res = "no quote located for this id in the catalog text (evidence-only or quoted under another id)"
            summary["noquote"] += 1
        elif all(r != "NOTFOUND" for r in results):
            res = "OK " + ",".join(results)
            summary["ok"] += 1
        else:
            res = "NOT FOUND " + ",".join(results)
            summary["notfound"] += 1
        out_lines.append(f"{pid_full}\t{fpath.strip()}\t{claimed.strip()}\t{len(quotes)}\t{res}")
    OUT.write_text("\n".join(out_lines) + "\n")
    print("rows", len(rows), summary)
    for ln in out_lines[1:]:
        cols = ln.split("\t")
        if cols[4].startswith("NOT FOUND") or cols[4].startswith("FILE"):
            print("  ", cols[0], cols[4][:120])


if __name__ == "__main__":
    sys.exit(main())
