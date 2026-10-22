#!/usr/bin/env python3
"""REV_G2: check every quoted passage in the lead's C0/C3/C4 drafts against the file and
line it cites. A quote is a straight-double-quoted span of >= 15 chars; its citation is
the nearest parenthesised reference after it in the same paragraph, of the forms
(progress.md:902), (E.20_RETURN.md:562-564; :332), (docs/DECISIONS.md:394-395),
(C2_OFI section 13), (C1 section 3). Output: one TSV row per quote with the match level
(WS exact after whitespace collapse, NOWS, SEG for '...' quotes, MISS), the line(s)
where the text was found, and the cited line(s).

Usage: python REV_G2_lead_quotes.py <repo_root> <md_file> [<md_file> ...] --out <tsv>
"""
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(sys.argv[1])
FILES = [Path(a) for a in sys.argv[2:] if not a.startswith("--") and a != sys.argv[sys.argv.index("--out") + 1]]
OUT = Path(sys.argv[sys.argv.index("--out") + 1])


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for k, v in {"’": "'", "‘": "'", "“": '"', "”": '"', "−": "-", "–": "-", "—": "-", " ": " "}.items():
        s = s.replace(k, v)
    return re.sub(r"\s+", " ", s).lower()


def nows(s):
    return re.sub(r"[\s\-]", "", s)


def resolve(ref):
    """Map a citation token to a repo path."""
    ref = ref.strip()
    m = re.match(r"(E\.\d+[a-z]?)_RETURN\.md", ref)
    if m:
        return REPO / "reports" / f"{m.group(1)}_RETURN.md"
    if ref.startswith("progress.md"):
        return REPO / "progress.md"
    if ref.startswith("docs/DECISIONS.md"):
        return REPO / "docs/DECISIONS.md"
    m = re.match(r"C1\b", ref)
    if m:
        return REPO / "reports/stage_e28_briefs/C1_inventory.md"
    m = re.match(r"(C2_[A-Za-z]+)", ref)
    if m:
        return REPO / "reports/stage_e28_briefs" / f"{m.group(1)}.md"
    return None


CITE_RE = re.compile(r"\(([^()]*?(?:progress\.md|_RETURN\.md|DECISIONS\.md|\bC1\b|\bC2_[A-Za-z]+)[^()]*)\)")

cache = {}


def load(p):
    if p not in cache:
        txt = p.read_text(encoding="utf-8", errors="replace").splitlines() if p.exists() else None
        cache[p] = txt
    return cache[p]


def find(q, p):
    lines = load(p)
    if lines is None:
        return "NOFILE", ""
    qn = norm(q).strip(' "')
    joined = norm("\n".join(lines))
    # map char offsets to line numbers in the normalised joined text
    def line_of(pos):
        cnt = 0
        for i, ln in enumerate(lines, 1):
            cnt += len(norm(ln)) + 1
            if cnt > pos:
                return i
        return len(lines)
    if qn in joined:
        return "WS", str(line_of(joined.find(qn)))
    jw = nows(joined)
    qw = nows(qn)
    if qw in jw:
        # approximate line via no-space prefix count
        tgt = jw.find(qw)
        cnt = 0
        for i, ln in enumerate(lines, 1):
            cnt += len(nows(norm(ln)))
            if cnt > tgt:
                return "NOWS", str(i)
        return "NOWS", "?"
    segs = [s.strip() for s in re.split(r"\.\.\.|…", qn) if len(s.strip()) >= 8]
    if len(segs) > 1 and all(nows(s) in jw for s in segs):
        return "SEG", ""
    return "MISS", ""


rows = []
for md in FILES:
    text = md.read_text(encoding="utf-8").splitlines()
    # paragraphs: contiguous non-empty lines (list items joined)
    buf, start = [], None
    paras = []
    for i, ln in enumerate(text, 1):
        if ln.strip() == "":
            if buf:
                paras.append((start, i - 1, "\n".join(buf)))
            buf, start = [], None
            continue
        if not buf:
            start = i
        buf.append(ln)
    if buf:
        paras.append((start, len(text), "\n".join(buf)))
    for s, e, block in paras:
        b = re.sub(r"`[^`]*`", " ", block)
        qpos = [m.start() for m in re.finditer(r'"', b)]
        cites = [(m.start(), m.group(1)) for m in CITE_RE.finditer(b)]
        for a, z in zip(qpos[0::2], qpos[1::2]):
            q = b[a + 1:z]
            if len(q) < 15:
                continue
            after = [c for c in cites if c[0] > z]
            cite = after[0][1] if after else (cites[-1][1] if cites else "")
            # several refs may be in one parenthesis: take each file token
            refs = re.findall(r"(?:E\.\d+[a-z]?_RETURN\.md|progress\.md|docs/DECISIONS\.md|\bC1\b|\bC2_[A-Za-z]+)", cite) or [""]
            paths = [resolve(r) for r in refs]
            best = ("MISS", "", "")
            for r, p in zip(refs, paths):
                if p is None:
                    continue
                lvl, ln = find(q, p)
                if lvl in ("WS", "NOWS", "SEG"):
                    best = (lvl, str(p.relative_to(REPO)), ln)
                    break
                best = (lvl, str(p.relative_to(REPO)), ln)
            rows.append((md.name, f"{s}-{e}", best[0], best[1], best[2], cite.replace("\t", " ")[:80], q.replace("\n", " ")[:170]))

hdr = "md\tmd_lines\tlevel\tfile_found\tline_found\tcitation\tquote"
OUT.write_text(hdr + "\n" + "\n".join("\t".join(r) for r in rows) + "\n", encoding="utf-8")
from collections import Counter
print("quotes:", len(rows), dict(Counter(r[2] for r in rows)))
for r in rows:
    flag = "" if r[2] in ("WS", "NOWS", "SEG") else "<<"
    print(f"{flag}{r[0]} {r[1]}\t{r[2]}\t{r[3]}:{r[4]}\tcited[{r[5]}]\t{r[6][:90]}")
