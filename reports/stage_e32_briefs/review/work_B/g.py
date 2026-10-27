"""Tiny context grep for saved pages: g.py FILE PATTERN [MAXLINES] [WIDTH]
Prints line number and a window of WIDTH chars around the first match on each line.
Case-insensitive, plain substring after whitespace normalisation."""
import re
import sys

path, pat = sys.argv[1], sys.argv[2]
maxn = int(sys.argv[3]) if len(sys.argv) > 3 else 3
width = int(sys.argv[4]) if len(sys.argv) > 4 else 200
pl = pat.lower()
n = 0
with open(path, errors="replace") as fh:
    for i, line in enumerate(fh, 1):
        s = re.sub(r"\s+", " ", line).strip()
        k = s.lower().find(pl)
        if k < 0:
            continue
        a = max(0, k - width // 3)
        print(f"{i}: {s[a:a + width]}")
        n += 1
        if n >= maxn:
            break
if n == 0:
    print(f"NOMATCH {pat!r} in {path.rsplit('/', 1)[-1]}")
