"""REV_G3 quote check, pass 2: quotes may span line breaks and may contain '...' ellipses.
The brief is read as one string with newlines collapsed; each quote is split at '...' or '…'
into fragments; every fragment of >= 12 chars must be found (after normalization) in at least
one saved source file for the quote to count as FOUND. Usage:
python -I REV_G3_quotecheck2.py <brief.md> <pages_dir> <out.tsv>"""
import json
import re
import sys
import unicodedata
from pathlib import Path

LIG = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "’": "'", "‘": "'", "“": '"',
    "”": '"', "–": "-", "—": "-", "−": "-", "­": "", " ": " ", " ": " ",
    " ": " ", "→": "->", "×": "x", "≤": "<=", "≥": ">=", "⩽": "<=", "⩾": ">=",
    "≳": ">~", "≲": "<~", "∞": "infinity", "σ": "sigma", "θ": "theta", "γ": "gamma",
    "δ": "delta", "λ": "lambda", "µ": "mu", "μ": "mu",
}
MIN_CHARS = 12


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    for k, v in LIG.items():
        s = s.replace(k, v)
    return s.lower()


def source_variants(text: str):
    t = norm(text)
    dehyph = re.sub(r"-\s*\n\s*", "", t)
    return (re.sub(r"\s+", " ", t), re.sub(r"\s+", " ", dehyph),
            re.sub(r"\s+", "", t), re.sub(r"\s+", "", dehyph), re.sub(r"[-\s]+", "", t))


def frag_variants(q: str):
    t = norm(q)
    return re.sub(r"\s+", " ", t).strip(), re.sub(r"\s+", "", t), re.sub(r"[-\s]+", "", t)


def extract_quotes(md: str):
    """Return (line, quote) for every double-quoted span inside one paragraph (no blank line
    inside the span, at most 400 chars), so a closing quote is never paired with the next
    paragraph's opening quote."""
    out = []
    pos = 0
    for para in re.split(r"\n\s*\n", md):
        start = md.index(para, pos) if para else pos
        pos = start + len(para)
        line0 = md.count("\n", 0, start) + 1
        flat = " ".join(para.split())
        for m in re.finditer(r'"([^"]{%d,400}?)"|\u201c([^\u201d]{%d,400}?)\u201d' % (MIN_CHARS, MIN_CHARS), flat):
            q = m.group(1) or m.group(2)
            if q is None or q[0] in ",;:)" or q.startswith("/ "):
                continue
            out.append((line0, q.strip()))
    return out


def load_sources(pages: Path):
    srcs = {}
    for p in sorted(pages.iterdir()):
        try:
            if p.suffix in (".txt", ".md"):
                srcs[p.name] = source_variants(p.read_text(errors="replace"))
            elif p.suffix == ".ipynb":
                nb = json.loads(p.read_text(errors="replace"))
                cells = "\n".join("".join(c.get("source", [])) for c in nb.get("cells", []))
                srcs[p.name] = source_variants(cells)
            elif p.suffix == ".json":
                srcs[p.name] = source_variants(p.read_text(errors="replace"))
        except (OSError, ValueError):
            pass
    return srcs


def find_frag(frag: str, srcs):
    fa, fc, fe = frag_variants(frag)
    hits = []
    for name, (a, b, c, d, e) in srcs.items():
        if fa in a or fa in b:
            hits.append(f"{name}:ws")
        elif fc in c or fc in d:
            hits.append(f"{name}:nospace")
        elif fe in e:
            hits.append(f"{name}:nohyphen")
    return hits


def main():
    brief, pages, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    md = brief.read_text(errors="replace")
    quotes = extract_quotes(md)
    srcs = load_sources(pages)
    rows, n_found, n_miss = [], 0, 0
    for line, q in quotes:
        frags = [f.strip(" ,;.") for f in re.split(r"\.\.\.|…", q)]
        frags = [f for f in frags if len(f) >= MIN_CHARS]
        if not frags:
            rows.append((line, "SKIP", q, "fragments too short"))
            continue
        per = [find_frag(f, srcs) for f in frags]
        if all(per):
            n_found += 1
            rows.append((line, "FOUND", q, "; ".join(sorted({h for hs in per for h in hs})[:4])))
        else:
            n_miss += 1
            missing = [f for f, h in zip(frags, per) if not h]
            rows.append((line, "MISS", q, "missing fragment(s): " + " || ".join(missing)))
    with out.open("w") as f:
        f.write("line\tstatus\tquote\thits_or_missing\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    print(f"{brief.name}: quotes={len(quotes)} found={n_found} miss={n_miss} skip={len(quotes) - n_found - n_miss} -> {out}")


if __name__ == "__main__":
    main()
