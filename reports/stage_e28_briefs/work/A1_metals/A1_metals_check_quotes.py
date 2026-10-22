import json, re
from pathlib import Path
def norm(s): return re.sub(r"\s+", " ", s.replace("’", "'").replace("‒","-")).strip()
d = json.load(open("reports/stage_e28_briefs/A1_metals.json"))
bad = ok = 0
def check(src, q, where):
    global bad, ok
    if not src or not q: return
    s = src.split(";")[0].strip()
    if s.endswith(".zip"): return
    p = Path(s)
    if p.suffix == ".pdf": p = p.with_suffix(".txt")
    elif p.suffix == ".html": p = Path(str(p) + ".txt")
    if not p.exists(): print("MISSING", where, p); bad += 1; return
    if norm(q) in norm(p.read_text(errors="ignore")): ok += 1
    else: print("NOTFOUND", where, q[:80]); bad += 1
for c in d:
    for k, v in c.items():
        if isinstance(v, dict) and "quote" in v:
            check(v["source_file"], v["quote"], c["candidate"] + "." + k)
            if isinstance(v["value"], list):
                for r in v["value"]: check(r.get("source_file"), r.get("quote"), c["candidate"] + "." + k + ".item")
print("ok", ok, "bad", bad)
