"""Verify every evidence quote is a verbatim substring (whitespace-normalised) of its saved file's text.
Usage: python3 -I C2_Firms_verify.py <evidence.tsv>  ; prints failures only plus a count."""
import sys, re, os, subprocess
D = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_Firms"
def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("‑", "-").replace("–", "-").replace("—", "-").replace("ﬂ", "fl").replace("ﬁ", "fi")
    return re.sub(r"\s+", " ", s).strip().lower()
cache = {}
def text(f):
    if f in cache: return cache[f]
    p = os.path.join(D, f); t = ""
    for cand in (p + ".txt", p + ".raw.txt"):
        if os.path.exists(cand): t += open(cand, encoding="utf-8", errors="ignore").read() + " "
    if f.endswith(".pdf"):
        t += subprocess.run(["pdftotext", p, "-"], capture_output=True, text=True).stdout
    if not t and os.path.exists(p): t = open(p, encoding="utf-8", errors="ignore").read()
    # also strip markdown/html markup variants
    t2 = re.sub(r"<[^>]+>", " ", t); t2 = re.sub(r"[*_#`]", "", t2)
    cache[f] = norm(t) + " || " + norm(t2)
    return cache[f]
ok = bad = 0
for line in open(sys.argv[1], encoding="utf-8"):
    if not line.strip() or line.startswith("id\t"): continue
    parts = line.rstrip("\n").split("\t")
    eid, quote, f = parts[0], parts[3], parts[4]
    segs = [s.strip() for s in quote.split("...") if s.strip()]
    t = text(f)
    miss = [s for s in segs if norm(s.strip('"')) not in t]
    if miss: bad += 1; print("FAIL", eid, f, "|", miss[0][:90])
    else: ok += 1
print(f"ok={ok} fail={bad}")
