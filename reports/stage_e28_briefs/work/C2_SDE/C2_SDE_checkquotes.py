import re, html, sys
from pathlib import Path
md = Path("C2_SDE.md").read_text()
sec = md[md.index("## 12. Evidence table"):md.index("## 13.")]
pages = Path("pages/C2_SDE")
def norm(t): return re.sub(r"\s+", " ", t.replace("­","")).strip()
cache = {}
def text(fn):
    if fn not in cache:
        p = pages / fn
        if fn.endswith(".pdf"): p = p.with_suffix(".txt")
        t = p.read_text(encoding="utf-8", errors="ignore")
        r = Path("work/C2_SDE/raw")/p.name
        if r.exists(): t = t + " " + r.read_text(encoding="utf-8", errors="ignore")
        if fn.endswith(".html"):
            t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S); t = html.unescape(re.sub(r"<[^>]+>", " ", t))
        cache[fn] = norm(t)
    return cache[fn]
bad = 0
for row in sec.splitlines():
    if not row.startswith("| ") or row.startswith("| claim") or row.startswith("|---"): continue
    cells = [c.strip() for c in row.strip("|").split("|")]
    fn = cells[-1]
    if fn == "rules/products.py": continue
    quotes = re.findall(r'"([^"]+)"', cells[2])
    for q in quotes:
        qn = norm(q)
        ok = qn in text(fn)
        if not ok:
            # try fragments of 40 chars
            frags = [qn[i:i+40] for i in range(0, max(1,len(qn)-40), 40)]
            hit = sum(f in text(fn) for f in frags)
            print(f"MISS ({hit}/{len(frags)} frags) {fn}: {qn[:90]}")
            bad += 1
print("misses", bad)
