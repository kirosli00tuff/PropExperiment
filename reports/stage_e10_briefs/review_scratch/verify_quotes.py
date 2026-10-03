"""Re-verify every quoted passage in the K9 draft catalog against the saved source files.

Reads: reports/stage_e10_catalog_K9.md and every file under reports/stage_e10_research/ (and the
repo files the catalog quotes: rulings, design target, STAGE_E_DESIGN.md, topstep facts, K8 catalog,
regime log). Writes: review_scratch/quote_check.tsv. Prints counts and the NOT FOUND list only.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "reports/stage_e10_catalog_K9.md"
OUT = ROOT / "reports/stage_e10_briefs/review_scratch/quote_check.tsv"
SRC_DIRS = [ROOT / "reports/stage_e10_research"]
EXTRA_FILES = [
    ROOT / "reports/stage_e10_briefs/task4_lead_rulings.md",
    ROOT / "reports/stage_e10_design_target.md",
    ROOT / "docs/STAGE_E_DESIGN.md",
    ROOT / "reports/stage_e0_topstep_facts.json",
    ROOT / "reports/stage_e0_catalog_K8.md",
    ROOT / "reports/stage_e10_research_regime.md",
    ROOT / "reports/stage_e10_research_calendar.md",
]
MIN_LEN = 14


def norm(s: str) -> str:
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("−", "-").replace("­", "")
    s = s.replace("ﬁ", "fi").replace("ﬂ", "fl").replace(" ", " ")
    s = s.replace("¤", "ff")  # "di¤erential" in Savor-Wilson's PDF text layer
    s = re.sub(r"-\n\s*", "", s)  # join line-break hyphenation
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def norm_nohyph(s: str) -> str:
    return re.sub(r"(?<=[a-z])- (?=[a-z])", "", norm(s))


def load_sources() -> list[tuple[Path, str, list[int]]]:
    files: list[Path] = []
    for d in SRC_DIRS:
        files += [p for p in d.rglob("*") if p.is_file() and p.suffix in {".txt", ".html", ".md", ".tsv", ".json"}]
    files += [p for p in EXTRA_FILES if p.exists()]
    out = []
    for p in files:
        raw = p.read_text(errors="replace")
        # map normalized offsets back to raw line numbers: build normalized text per line, joined by space
        lines = raw.split("\n")
        starts: list[int] = []
        parts: list[str] = []
        pos = 0
        for i, ln in enumerate(lines):
            n = norm(ln)
            starts.append(pos)
            parts.append(n)
            pos += len(n) + 1
        joined = " ".join(parts)
        out.append((p, joined, starts))
    return out


def line_of(starts: list[int], off: int) -> int:
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
    # quoted strings in straight double quotes; the catalog's own quotes are straight
    quotes = re.findall(r'"([^"\n]{%d,}?)"' % MIN_LEN, text)
    # also quotes spanning a line break inside the markdown
    quotes += re.findall(r'"([^"]{%d,}?)"' % MIN_LEN, text.replace("\n  ", " ").replace("\n", " "))
    seen = set()
    uniq = []
    for q in quotes:
        k = norm(q)
        if k in seen or len(k) < MIN_LEN:
            continue
        seen.add(k)
        uniq.append(q)
    sources = load_sources()
    rows = []
    not_found = []
    for q in uniq:
        nq = norm(q)
        hits = []
        for p, joined, starts in sources:
            off = joined.find(nq)
            mode = "verbatim-norm"
            if off < 0:
                # try removing hyphen-space joins on both sides
                nq2 = norm_nohyph(q)
                j2 = re.sub(r"(?<=[a-z])- (?=[a-z])", "", joined)
                off2 = j2.find(nq2)
                if off2 >= 0:
                    # approximate line: locate first 25 chars of nq2 in joined
                    probe = nq2[:25]
                    off = joined.find(probe)
                    mode = "hyphen-joined"
            if off >= 0:
                hits.append(f"{p.relative_to(ROOT)}:{line_of(starts, off)} [{mode}]")
        if not hits:
            # try the splice pieces around "[...]"
            pieces = [x.strip() for x in re.split(r"\[\.\.\.\]|\.\.\.", q) if len(x.strip()) >= MIN_LEN]
            piece_hits = []
            if len(pieces) >= 2:
                for pc in pieces:
                    npc = norm(pc)
                    ph = [f"{p.relative_to(ROOT)}:{line_of(st, j.find(npc))}" for p, j, st in sources if j.find(npc) >= 0]
                    piece_hits.append(ph[0] if ph else "NOT FOUND")
            status = "PIECES: " + " | ".join(piece_hits) if piece_hits and all(x != "NOT FOUND" for x in piece_hits) else "NOT FOUND"
            if status == "NOT FOUND":
                not_found.append(q)
        else:
            status = "; ".join(hits[:3])
        rows.append((q[:90].replace("\t", " "), status))
    OUT.write_text("quote\tstatus\n" + "\n".join(f"{a}\t{b}" for a, b in rows) + "\n")
    print(f"quotes checked {len(rows)}; found {len(rows) - len(not_found)}; not found {len(not_found)}")
    for q in not_found:
        print("NOT FOUND:", q[:160])


if __name__ == "__main__":
    sys.exit(main())
