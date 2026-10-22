#!/usr/bin/env python3
"""REV_G2 quote check: extract every double-quoted string of >= MINLEN chars from a
markdown file and search the saved source text files after normalising whitespace,
hyphenation, ligatures and typographic punctuation.

Usage: python REV_G2_quotecheck.py <markdown> <pages_dir> [--min 25] [--out report.tsv]

For each quote the script looks for file names (*.txt, *.pdf, *.html, *.json) in the
same paragraph or table row and searches those files first; if none is named, or the
named files miss, it searches every .txt/.json in pages_dir and reports which match.
Match levels: WS (whitespace-collapsed exact), NOWS (all whitespace removed),
SEG (every '...'-separated segment matched at NOWS level), MISS.
"""
import re
import sys
import unicodedata
from pathlib import Path

LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
       "’": "'", "‘": "'", "“": '"', "”": '"', "−": "-",
       "–": "-", "—": "-", " ": " ", "­": "", "§": "±", " ": " ",
       " ": " "}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    for k, v in LIG.items():
        s = s.replace(k, v)
    s = re.sub(r"-\s*\n\s*", "", s)          # join hyphenated line breaks
    s = re.sub(r"\s+", " ", s)
    return s.lower()


def nows(s: str) -> str:
    return re.sub(r"[\s\-]", "", s)


def file_tokens(block: str):
    toks = re.findall(r"`?([A-Za-z0-9_\-]+\.(?:txt|pdf|html|json))`?", block)
    out = []
    for t in toks:
        if t.endswith(".pdf"):
            t = t[:-4] + ".txt"
        elif t.endswith(".html"):
            t = t + ".txt"
        if t not in out:
            out.append(t)
    return out


def paragraphs(lines):
    """Yield (start_line, end_line, text) for contiguous non-empty blocks; table rows are
    their own block."""
    buf, start = [], None
    for i, ln in enumerate(lines, 1):
        if ln.strip() == "":
            if buf:
                yield start, i - 1, "\n".join(buf)
                buf, start = [], None
            continue
        if ln.lstrip().startswith("|"):
            if buf:
                yield start, i - 1, "\n".join(buf)
                buf, start = [], None
            yield i, i, ln
            continue
        if not buf:
            start = i
        buf.append(ln)
    if buf:
        yield start, len(lines), "\n".join(buf)


def main():
    args = sys.argv[1:]
    md = Path(args[0])
    pages = Path(args[1])
    minlen = 25
    out = None
    if "--min" in args:
        minlen = int(args[args.index("--min") + 1])
    if "--out" in args:
        out = Path(args[args.index("--out") + 1])
    lines = md.read_text(encoding="utf-8").splitlines()
    cache = {}

    def load(fn):
        p = pages / fn
        if fn not in cache:
            if p.exists():
                raw = p.read_text(encoding="utf-8", errors="replace")
                n = norm(raw)
                cache[fn] = (raw, n, nows(n))
            else:
                cache[fn] = None
        return cache[fn]

    allfiles = sorted([p.name for p in pages.iterdir() if p.suffix in (".txt", ".json")])

    def search(q, fn):
        d = load(fn)
        if d is None:
            return "NOFILE", -1
        raw, n, nw = d
        qn = norm(q).strip(' "')
        if qn in n:
            pos = n.find(qn)
            return "WS", pos
        qw = nows(qn)
        if qw and qw in nw:
            return "NOWS", nw.find(qw)
        segs = [s.strip() for s in re.split(r"\.\.\.|\[[^\]]*\]", qn) if len(s.strip()) >= 8]
        if segs and all(nows(s) in nw for s in segs):
            return "SEG", nw.find(nows(segs[0]))
        return "MISS", -1

    def approx_line(fn, level, pos):
        d = load(fn)
        if d is None or pos < 0:
            return ""
        raw, n, nw = d
        # map position in normalised text back to a raw line by cumulative no-space chars
        if level == "WS":
            target = len(nows(n[:pos]))
        else:
            target = pos
        cnt = 0
        for i, ln in enumerate(raw.splitlines(), 1):
            cnt += len(nows(norm(ln)))
            if cnt >= target:
                return str(i)
        return "?"

    rows = []
    for s, e, block in paragraphs(lines):
        quotes = re.findall(r'"([^"\n]{%d,})"' % minlen, block)
        if not quotes:
            continue
        named = file_tokens(block)
        for q in quotes:
            best = ("MISS", None, -1)
            tried = []
            for fn in named:
                lvl, pos = search(q, fn)
                tried.append(f"{fn}:{lvl}")
                if lvl in ("WS", "NOWS", "SEG"):
                    best = (lvl, fn, pos)
                    break
            if best[0] == "MISS":
                hits = []
                for fn in allfiles:
                    lvl, pos = search(q, fn)
                    if lvl in ("WS", "NOWS", "SEG"):
                        hits.append((lvl, fn, pos))
                if hits:
                    hits.sort(key=lambda h: ("WS", "NOWS", "SEG").index(h[0]))
                    best = hits[0]
                    best = (best[0] + "*", best[1], best[2])   # * = found in a file not named in the block
            lvl, fn, pos = best
            rows.append((s, e, lvl, fn or "-", approx_line(fn, lvl.rstrip("*"), pos) if fn else "",
                         ";".join(tried) if tried else "(no file named)", q[:160].replace("\t", " ")))

    hdr = "md_line\tlevel\tfile\tsrc_line\tnamed_files_tried\tquote"
    body = "\n".join(f"{s}-{e}\t{lvl}\t{fn}\t{sl}\t{tr}\t{q}" for s, e, lvl, fn, sl, tr, q in rows)
    if out:
        out.write_text(hdr + "\n" + body + "\n", encoding="utf-8")
    from collections import Counter
    c = Counter(r[2] for r in rows)
    print(f"quotes checked: {len(rows)}")
    for k in sorted(c):
        print(f"  {k}: {c[k]}")
    for r in rows:
        if r[2].startswith("MISS") or r[2] == "NOFILE" or r[2].endswith("*"):
            print(f"  {r[2]}\tmd {r[0]}-{r[1]}\t{r[3]}\t{r[4]}\t{r[6][:110]}")


if __name__ == "__main__":
    main()
