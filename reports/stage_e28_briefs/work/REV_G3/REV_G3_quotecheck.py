"""REV_G3 quote check: extract every double-quoted string from a reviewed brief and
search the deep dive's saved sources after normalizing whitespace, hyphenation and
ligatures. Usage: python -I REV_G3_quotecheck.py <brief.md> <pages_dir> <out.tsv>
Prints counts only; full rows go to the TSV."""
import json
import re
import sys
import unicodedata
from pathlib import Path

LIG = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl",
    "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-",
    "—": "-", "−": "-", "­": "", " ": " ", " ": " ",
    " ": " ", "→": "->", "×": "x", "≤": "<=", "≥": ">=",
    "⩽": "<=", "⩾": ">=", "≳": ">~", "≲": "<~",
}
MIN_CHARS = 12


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    for k, v in LIG.items():
        s = s.replace(k, v)
    return s.lower()


def variants(text: str):
    """Return normalized source variants: (a) whitespace collapsed, (b) line-end
    hyphens removed then whitespace collapsed, (c) all whitespace removed,
    (d) line-end hyphens removed then all whitespace removed."""
    t = norm(text)
    a = re.sub(r"\s+", " ", t)
    dehyph = re.sub(r"-\s*\n\s*", "", t)
    b = re.sub(r"\s+", " ", dehyph)
    c = re.sub(r"\s+", "", t)
    d = re.sub(r"\s+", "", dehyph)
    # (e) every hyphen dropped, whitespace dropped: catches "well-known" vs "well known"
    e = re.sub(r"[-\s]+", "", t)
    return a, b, c, d, e


def quote_variants(q: str):
    t = norm(q)
    a = re.sub(r"\s+", " ", t).strip()
    c = re.sub(r"\s+", "", t)
    e = re.sub(r"[-\s]+", "", t)
    return a, c, e


def extract_quotes(md: str):
    out = []
    for lineno, line in enumerate(md.splitlines(), 1):
        # straight and curly double quotes
        for m in re.finditer(r'"([^"]+)"|“([^”]+)”', line):
            q = m.group(1) or m.group(2)
            if q is None:
                continue
            q = q.strip()
            if len(q) >= MIN_CHARS:
                out.append((lineno, q))
    return out


def load_sources(pages: Path):
    srcs = {}
    for p in sorted(pages.iterdir()):
        if p.suffix in (".txt", ".md"):
            try:
                srcs[p.name] = variants(p.read_text(errors="replace"))
            except OSError:
                pass
        elif p.suffix == ".ipynb":
            try:
                nb = json.loads(p.read_text(errors="replace"))
                cells = "\n".join("".join(c.get("source", [])) for c in nb.get("cells", []))
                srcs[p.name] = variants(cells)
            except (OSError, ValueError):
                pass
    return srcs


def main():
    brief, pages, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    md = brief.read_text(errors="replace")
    quotes = extract_quotes(md)
    srcs = load_sources(pages)
    rows = []
    n_found = n_miss = 0
    for lineno, q in quotes:
        qa, qc, qe = quote_variants(q)
        hits = []
        for name, (a, b, c, d, e) in srcs.items():
            how = None
            if qa in a:
                how = "exact-ws"
            elif qa in b:
                how = "dehyph"
            elif qc in c or qc in d:
                how = "nospace"
            elif qe in e:
                how = "nohyphen"
            if how:
                hits.append(f"{name}:{how}")
        if hits:
            n_found += 1
            rows.append((lineno, "FOUND", q, "; ".join(hits[:4])))
        else:
            n_miss += 1
            rows.append((lineno, "MISS", q, ""))
    with out.open("w") as f:
        f.write("line\tstatus\tquote\thits\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    print(f"{brief.name}: quotes={len(quotes)} found={n_found} miss={n_miss} -> {out}")


if __name__ == "__main__":
    main()
