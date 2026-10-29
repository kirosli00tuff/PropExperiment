"""CRUDE_quotecheck.py: check each item's quote pieces appear (whitespace-normalised) in the cited saved file."""
import json, re, pathlib
R = pathlib.Path("/home/kiros-li/Documents/GitHub/PropExperiment")
d = json.load(open(R / "reports/stage_e32b_briefs/F2_crude.json"))
norm = lambda s: re.sub(r"\s+", " ", s.replace("’", "'").replace("…", "fi")).strip().lower()
for it in d["items"]:
    f = it["source"].get("file")
    if not f or it["verified"] in ("snippet",):
        print(it["id"], "SKIP", it["verified"]); continue
    p = R / f
    cands = [p, p.with_name(p.name + ".txt"), p.with_suffix(".txt")]
    p = next((c for c in cands if c.exists() and c.suffix in (".txt", ".md")), None)
    if p is None:
        print(it["id"], "NOFILE", f); continue
    txt = norm(p.read_text(errors="ignore"))
    bad = []
    for piece in it["quote"].split(" | "):
        for sub in piece.split(" ... "):
            s = norm(sub.strip("\" "))
            if s and s not in txt and not s.startswith(("22:00 row", "0:00 row", "3:00 row")):
                bad.append(sub[:70])
    print(it["id"], "OK" if not bad else "MISS " + " || ".join(bad))
