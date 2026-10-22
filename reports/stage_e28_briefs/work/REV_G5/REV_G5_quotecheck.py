#!/usr/bin/env python3
"""REV_G5 quote checker (MathReviewer-FableXHigh, Stage E.28).

Extracts every double-quoted string from a reviewed markdown file and searches
the saved source texts under the reader's pages/<ROOT>/ folder after
normalizing whitespace, hyphenation, ligatures, quotes and dashes.
Quotes are split into fragments at ellipses and at bracketed editorial
insertions; a quote matches when every fragment of >= MIN_FRAG chars matches.

Usage: python3 -I REV_G5_quotecheck.py <md file> <pages dir> <out tsv>
Reads only; writes the TSV and prints a summary.
"""
import html
import re
import sys
import unicodedata
from pathlib import Path

MIN_QUOTE = 12   # shorter quoted strings are labels, not source quotes
MIN_FRAG = 10

DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")
QUOTES = {ord("‘"): "'", ord("’"): "'", ord("“"): '"', ord("”"): '"',
          ord("´"): "'", ord("′"): "'"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)          # ligatures fi fl ffi -> ascii
    s = s.translate(DASHES).translate(QUOTES)
    s = s.replace("­", "")                   # soft hyphen
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def alnum(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s)


def load_source(p: Path):
    raw = p.read_text(errors="replace")
    if p.suffix == ".html" and not p.name.endswith(".html.txt"):
        raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
        raw = re.sub(r"<[^>]+>", " ", raw)
        raw = html.unescape(raw)
    # version A: line-break hyphenation removed  ("predict-\nability" -> "predictability")
    a = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", raw)
    a = norm(a)
    # version B: hyphen kept, whitespace collapsed ("predict- ability")
    b = norm(raw)
    return a, b, alnum(a), alnum(b)


def fragments(q: str):
    parts = re.split(r"\s*(?:\.\.\.|…)\s*|\s*\[[^\]]*\]\s*", q)
    return [p for p in (norm(x) for x in parts) if len(p) >= MIN_FRAG]


def find_quotes(md: str):
    """Quotes may span line breaks (the md is wrapped at ~110 cols). Straight
    double quotes are paired consecutively inside each unit (a paragraph, or a
    table cell), so a short quote such as "up" cannot swallow the text after it.
    Units with an odd number of quote marks are reported."""
    out = []
    pos = 0
    units = []
    for para in md.split("\n\n"):
        if para.lstrip().startswith("|"):
            # table: each cell is a unit
            cpos = pos
            for row in para.split("\n"):
                rpos = cpos
                for cell in row.split("|"):
                    units.append((rpos, cell))
                    rpos += len(cell) + 1
                cpos += len(row) + 1
        else:
            units.append((pos, para))
        pos += len(para) + 2
    odd = 0
    for upos, text in units:
        idx = [m.start() for m in re.finditer(r'["“”]', text)]
        if len(idx) % 2:
            odd += 1
            print(f"  WARN odd quote count in unit at line {md.count(chr(10), 0, upos) + 1}: {text[:70]!r}")
        for a, b in zip(idx[0::2], idx[1::2]):
            q = text[a + 1:b]
            if len(q) < MIN_QUOTE:
                continue
            line = md.count("\n", 0, upos + a) + 1
            out.append((line, re.sub(r"\s*\n\s*", " ", q)))
    return sorted(out)


def main():
    md_path, pages, out_tsv = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    md = md_path.read_text()
    files = sorted([p for p in pages.iterdir()
                    if p.suffix in (".txt",) or (p.suffix == ".html" and not (p.with_suffix(".html.txt")).exists())])
    sources = {p.name: load_source(p) for p in files}
    quotes = find_quotes(md)
    rows = []
    n_match = n_miss = n_skip = 0
    for line, q in quotes:
        frags = fragments(q)
        if not frags:
            n_skip += 1
            rows.append((line, "SKIP(no fragment)", "", q))
            continue
        hits_all = None
        miss_frag = None
        for f in frags:
            fa = alnum(f)
            hit = set()
            for name, (a, b, aa, bb) in sources.items():
                if f in a or f in b or (len(fa) >= 8 and (fa in aa or fa in bb)):
                    hit.add(name)
            if not hit:
                miss_frag = f
                hits_all = set()
                break
            hits_all = hit if hits_all is None else (hits_all & hit or hits_all | hit)
        if miss_frag is None:
            n_match += 1
            rows.append((line, "MATCH", ";".join(sorted(hits_all)), q))
        else:
            n_miss += 1
            rows.append((line, "MISS", "frag=" + miss_frag[:80], q))
    with out_tsv.open("w") as fh:
        fh.write("line\tstatus\tfiles_or_missing_fragment\tquote\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"{md_path.name}: quotes={len(quotes)} matched={n_match} missed={n_miss} skipped={n_skip}")
    for r in rows:
        if r[1] == "MISS":
            print(f"  MISS line {r[0]}: {r[3][:110]!r}  [{r[2]}]")


if __name__ == "__main__":
    main()
