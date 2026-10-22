"""REV_G6 quote check: extract every double-quoted span (>= MINLEN chars) from a reviewed .md file,
split it at '...' into verbatim segments, normalise (NFKC, quotes, dashes, soft hyphens, ligatures,
whitespace, case) and search ALL saved text files under the given pages ROOT, in both a plain and a
de-hyphenated form. Reports, per segment: line in the .md, cited file (if a file name appears on that
line), matched files, and status (OK / OK-dehyph / MISS).

Usage: python3 -I REV_G6_quotecheck.py <reviewed.md> <pages_root> <out.tsv> [minlen]
"""
import html
import os
import re
import sys
import unicodedata

MD, ROOT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MINLEN = int(sys.argv[4]) if len(sys.argv) > 4 else 20


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("­", "")  # soft hyphen
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("′", "'"),
                 ("‐", "-"), ("‑", "-"), ("‒", "-"), ("–", "-"), ("—", "-"),
                 ("−", "-"), (" ", " "), ("…", "..."), ("´", "'"), ("`", "'")):
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def dehyph(s: str) -> str:
    # join line-break hyphenation: 'pa- rameters' -> 'parameters'; also 'autocorrelation- corrected'
    return re.sub(r"(\w)- (\w)", r"\1\2", s)


def load_corpus(root: str):
    corpus = {}
    for fn in sorted(os.listdir(root)):
        p = os.path.join(root, fn)
        if not os.path.isfile(p) or fn == "log.tsv":
            continue
        if fn.endswith(".pdf") or fn.endswith(".js"):
            continue  # text siblings exist
        try:
            raw = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if fn.endswith((".html", ".htm")):
            raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
            raw = re.sub(r"<[^>]+>", " ", raw)
            raw = html.unescape(raw)
        n = norm(raw)
        # markdown/html markup-stripped variant
        n2 = norm(re.sub(r"[*_#`]", "", raw))
        corpus[fn] = (n + " || " + n2, dehyph(n) + " || " + dehyph(n2))
    return corpus


corpus = load_corpus(ROOT)
file_names = sorted(corpus.keys(), key=len, reverse=True)

rows = []
with open(MD, encoding="utf-8") as fh:
    for ln, line in enumerate(fh, 1):
        # cited file names on this line
        cited = [f for f in file_names if f in line]
        # also bare stems like man_overfitting_investor_2015.html when corpus has .html.txt
        spans = re.findall(r'"([^"\n]{%d,})"' % MINLEN, line)
        # also curly-quoted spans
        spans += re.findall(r"“([^”\n]{%d,})”" % MINLEN, line)
        for sp in spans:
            segs = [s for s in re.split(r"\s*(?:\.\.\.|…)\s*", sp) if len(s.strip()) >= 8]
            for seg in segs:
                q = norm(seg)
                q = re.sub(r'^[\'"\s]+|[\'"\s]+$', "", q)
                qd = dehyph(q)
                hits, hits_d = [], []
                for fn, (txt, txtd) in corpus.items():
                    if q in txt:
                        hits.append(fn)
                    elif qd in txtd:
                        hits_d.append(fn)
                if hits:
                    status = "OK"
                elif hits_d:
                    status = "OK-dehyph"
                else:
                    status = "MISS"
                in_cited = any(c in hits + hits_d or c + ".txt" in hits + hits_d or
                               c.replace(".txt", "") in [h.replace(".txt", "") for h in hits + hits_d]
                               for c in cited) if cited else None
                rows.append((ln, status, ";".join(cited)[:80], "in_cited=%s" % in_cited,
                             ";".join((hits + hits_d)[:3]), seg[:140]))

with open(OUT, "w", encoding="utf-8") as fo:
    fo.write("md_line\tstatus\tcited_files_on_line\tin_cited\tmatched_files\tsegment\n")
    for r in rows:
        fo.write("\t".join(str(x) for x in r) + "\n")

n = len(rows)
ok = sum(1 for r in rows if r[1] == "OK")
okd = sum(1 for r in rows if r[1] == "OK-dehyph")
miss = sum(1 for r in rows if r[1] == "MISS")
wrongfile = sum(1 for r in rows if r[1] != "MISS" and r[3] == "in_cited=False")
print(f"{os.path.basename(MD)}: segments={n} OK={ok} OK-dehyph={okd} MISS={miss} matched_but_not_in_cited_file={wrongfile}")
print("MISSES:")
for r in rows:
    if r[1] == "MISS":
        print(f"  L{r[0]} cited={r[2] or '-'} | {r[5]}")
print("MATCHED BUT NOT IN THE FILE CITED ON THAT LINE:")
for r in rows:
    if r[1] != "MISS" and r[3] == "in_cited=False":
        print(f"  L{r[0]} cited={r[2]} matched={r[4]} | {r[5][:80]}")
