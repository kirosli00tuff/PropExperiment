"""REV_G1 quote checker (independent of the readers' own scripts).

Usage: python3 -I REV_G1_quotecheck.py <md_file> <pages_dir> <out_report>

For every double-quoted segment in the markdown file, search the saved source
texts after normalising whitespace, hyphenation, ligatures, quotes and all
non-alphanumeric characters (so dropped Greek letters, hats and fractions do
not matter). Evidence-table rows name their saved file; the quote is checked
against that file first and then, on a miss, against every saved file (to
catch misattribution). Body quotes are checked against every saved file.
"""
import html
import re
import sys
from pathlib import Path

LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
       "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-",
       "­": ""}


def norm(s: str) -> str:
    for k, v in LIG.items():
        s = s.replace(k, v)
    s = re.sub(r"-\s*\n\s*", "", s)          # line-break hyphenation
    s = s.lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def load_sources(pages: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in sorted(pages.iterdir()):
        if p.name == "log.tsv" or p.is_dir():
            continue
        if p.suffix in (".txt", ".md", ".json", ".tsv", ".csv"):
            out[p.name] = norm(p.read_text(encoding="utf-8", errors="replace"))
        elif p.suffix in (".html", ".htm", ".js"):
            raw = p.read_text(encoding="utf-8", errors="replace")
            raw = re.sub(r"<script.*?</script>", " ", raw, flags=re.S)
            raw = re.sub(r"<style.*?</style>", " ", raw, flags=re.S)
            raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
            out[p.name] = norm(raw)
    return out


def file_key(name: str, sources: dict[str, str]) -> list[str]:
    """Map a cited file name to the saved text files that hold its text."""
    name = name.strip().strip("`")
    stem = re.sub(r"\.(pdf|html|htm|txt|json)$", "", name)
    hits = [k for k in sources if k == name or k.startswith(stem + ".") or k == stem + ".txt"]
    return hits


QUOTE_RE = re.compile(r'"([^"]{8,})"')


def segments(cell: str) -> list[str]:
    segs: list[str] = []
    for q in QUOTE_RE.findall(cell):
        # drop bracketed reader notes about typography, keep citation brackets like [35] or [0, t]
        q = re.sub(r"\[[^\]]*(dropped|typeset|extraction|hyphen|unverified|lost|column|sic|omitted)[^\]]*\]",
                   " ", q, flags=re.I)
        for part in re.split(r"\s*\.\.\.\s*|\s*…\s*", q):
            if len(norm(part)) >= 12:
                segs.append(part.strip())
    return segs


def main() -> None:
    md = Path(sys.argv[1]).read_text(encoding="utf-8")
    pages = Path(sys.argv[2])
    out = Path(sys.argv[3])
    sources = load_sources(pages)
    lines = md.splitlines()
    rows: list[str] = ["# quote check: " + sys.argv[1], "", "sources loaded: " + str(len(sources)), ""]
    n_tab = n_tab_ok = n_tab_other = n_tab_miss = 0
    n_body = n_body_ok = n_body_miss = 0
    tab_lines: set[int] = set()
    quote_col = 2
    for i, line in enumerate(lines, 1):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or set(cells[0]) <= set("-: "):
            continue
        low = [c.lower() for c in cells]
        if any("quote" in c for c in low) and any("file" in c for c in low):
            quote_col = next(k for k, c in enumerate(low) if "quote" in c)   # header row
            continue
        if quote_col >= len(cells):
            continue
        quote_cell, file_cell = cells[quote_col], cells[-1]
        segs = segments(quote_cell)
        if not segs:
            continue
        tab_lines.add(i)
        keys = file_key(file_cell, sources)
        for seg in segs:
            n_tab += 1
            nseg = norm(seg)
            ok_named = any(nseg in sources[k] for k in keys)
            if ok_named:
                n_tab_ok += 1
                continue
            others = [k for k, v in sources.items() if nseg in v]
            if others:
                n_tab_other += 1
                rows.append(f"- L{i} OTHER-FILE: cited {file_cell!r}, found in {others}: \"{seg[:90]}\"")
            else:
                n_tab_miss += 1
                rows.append(f"- L{i} MISS (cited {file_cell!r}, keys {keys}): \"{seg[:120]}\"")
    rows.append("")
    # body scan over the joined text so that quotes spanning markdown line breaks are caught
    body_parts: list[str] = []
    for i, line in enumerate(lines, 1):
        body_parts.append("" if (i in tab_lines or line.startswith("|")) else line)
    body = "\n".join(body_parts)
    starts = [0]
    for ch_i, ch in enumerate(body):
        if ch == "\n":
            starts.append(ch_i + 1)
    import bisect
    for m in re.finditer(r'"([^"]{8,}?)"', body, flags=re.S):
        i = bisect.bisect_right(starts, m.start())
        for seg in segments('"' + m.group(1).replace("\n", " ") + '"'):
            words = len(seg.split())
            if words < 3:
                continue
            n_body += 1
            nseg = norm(seg)
            found = [k for k, v in sources.items() if nseg in v]
            if found:
                n_body_ok += 1
                rows.append(f"- L{i} body OK in {found[0]}: \"{seg[:70]}\"")
            else:
                n_body_miss += 1
                rows.append(f"- L{i} body MISS: \"{seg[:120]}\"")
    rows.insert(4, f"evidence-table segments: {n_tab}, matched named file: {n_tab_ok}, "
                   f"matched other file only: {n_tab_other}, missed everywhere: {n_tab_miss}")
    rows.insert(5, f"body quoted segments (>=3 words): {n_body}, found in some saved file: {n_body_ok}, "
                   f"missed: {n_body_miss}")
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("\n".join(rows[:6]))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
