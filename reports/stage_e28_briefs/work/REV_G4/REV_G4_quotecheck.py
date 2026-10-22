"""REV_G4 quote check: extract every double-quoted string (>= MINLEN chars) from a
reviewed markdown file and search for it in the saved source texts after
normalizing whitespace, hyphenation, ligatures and quote glyphs.

Usage: python -I REV_G4_quotecheck.py <md_file> <pages_dir> <out_tsv> [extra_dir ...]

Two match levels:
  STRICT: lower-case, ligatures expanded, curly quotes/dashes mapped, hyphen+newline
          joined, whitespace collapsed to one space.
  LOOSE : ASCII letters and digits only, lower-case (the readers' own level).
A quote containing " ... " or "[...]" is split into fragments; every fragment must
match (same file) for the quote to count as matched.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

MINLEN = 18

LIG = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl",
    "‘": "'", "’": "'", "“": '"', "”": '"', "–": "-",
    "—": "-", "−": "-", " ": " ", "…": "...",
}


def strict_norm_chars(text: str):
    """Return (normalized string, list of source line numbers per char)."""
    out: list[str] = []
    lines: list[int] = []
    # join hyphenation across line breaks first (track lines by scanning)
    i = 0
    n = len(text)
    line_no = 1
    prev_space = False
    while i < n:
        ch = text[i]
        if ch == "\n":
            line_no += 1
            # hyphenation: previous char '-' directly before newline -> drop the hyphen
            if out and out[-1] == "-" and i + 1 < n and text[i + 1].isalpha():
                out.pop()
                lines.pop()
                prev_space = out[-1] == " " if out else True
                i += 1
                continue
            ch = " "
        ch = LIG.get(ch, ch)
        if len(ch) > 1:
            for c in ch:
                out.append(c.lower())
                lines.append(line_no)
            prev_space = False
            i += 1
            continue
        if ch.isspace():
            if not prev_space and out:
                out.append(" ")
                lines.append(line_no)
            prev_space = True
        else:
            out.append(ch.lower())
            lines.append(line_no)
            prev_space = False
        i += 1
    return "".join(out), lines


def loose_norm_chars(text: str):
    out: list[str] = []
    lines: list[int] = []
    line_no = 1
    for ch in text:
        if ch == "\n":
            line_no += 1
            continue
        ch2 = LIG.get(ch, ch)
        for c in ch2:
            if c.isascii() and c.isalnum():
                out.append(c.lower())
                lines.append(line_no)
    return "".join(out), lines


def strict_norm(q: str) -> str:
    s, _ = strict_norm_chars(q)
    return s.strip()


def loose_norm(q: str) -> str:
    s, _ = loose_norm_chars(q)
    return s


def split_fragments(q: str) -> list[str]:
    parts = re.split(r"\s*(?:\[\.\.\.\]|\.\.\.|…)\s*", q)
    return [p for p in (x.strip(" ,;") for x in parts) if len(loose_norm(p)) >= 8]


def load_sources(dirs: list[Path]):
    srcs = {}
    for d in dirs:
        for f in sorted(d.glob("*.txt")):
            try:
                text = f.read_text(errors="replace")
            except OSError:
                continue
            srcs[f.name] = (strict_norm_chars(text), loose_norm_chars(text))
    return srcs


def find_in(norm_pair, needle: str):
    s, lines = norm_pair
    pos = s.find(needle)
    if pos < 0:
        return None
    return lines[pos], lines[min(pos + len(needle) - 1, len(lines) - 1)]


def extract_quotes(md: str):
    """Yield (md_line, quote, cited_file_hint)."""
    md_lines = md.split("\n")
    for ln, line in enumerate(md_lines, 1):
        hint = ""
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells:
                m = re.findall(r"[A-Za-z0-9_\-\.]+\.txt", cells[-1])
                hint = ",".join(m)
        for m in re.finditer(r'"([^"\n]{%d,}?)"' % MINLEN, line):
            yield ln, m.group(1), hint
        for m in re.finditer(r'“([^”\n]{%d,}?)”' % MINLEN, line):
            yield ln, m.group(1), hint


def main():
    md_path, pages, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    extra = [Path(p) for p in sys.argv[4:]]
    srcs = load_sources([pages] + extra)
    md = md_path.read_text()
    rows = []
    n_strict = n_loose = n_miss = 0
    for ln, q, hint in extract_quotes(md):
        frags = split_fragments(q)
        if not frags:
            continue
        best = None  # (level, file, l1, l2)
        for fname, (sn, lo) in srcs.items():
            # all fragments must match in this file
            res_s = [find_in(sn, strict_norm(f)) for f in frags]
            if all(r is not None for r in res_s):
                cand = ("STRICT", fname, min(r[0] for r in res_s), max(r[1] for r in res_s))
                if best is None or best[0] != "STRICT" or (hint and fname in hint):
                    best = cand
                    if hint and fname in hint:
                        break
                continue
            res_l = [find_in(lo, loose_norm(f)) for f in frags]
            if all(r is not None for r in res_l):
                cand = ("LOOSE", fname, min(r[0] for r in res_l), max(r[1] for r in res_l))
                if best is None or (best[0] == "LOOSE" and hint and fname in hint):
                    best = cand
        if best is None:
            status, fname, l1, l2 = "MISS", "", "", ""
            n_miss += 1
        else:
            status, fname, l1, l2 = best
            if status == "STRICT":
                n_strict += 1
            else:
                n_loose += 1
        hint_ok = ""
        if hint:
            hint_ok = "cited-file-ok" if (fname and fname in hint) else ("cited-file-MISMATCH" if fname else "")
        rows.append((ln, status, fname, l1, l2, hint, hint_ok, q[:160]))
    with out.open("w") as fh:
        fh.write("md_line\tstatus\tfound_file\tsrc_line_from\tsrc_line_to\tcited_file\tcited_check\tquote\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"{md_path.name}: quotes={len(rows)} strict={n_strict} loose={n_loose} miss={n_miss}")
    for r in rows:
        if r[1] == "MISS" or r[6] == "cited-file-MISMATCH":
            print("  ", r[1], r[6], f"md:{r[0]}", r[2], "|", r[7][:110])


if __name__ == "__main__":
    main()
