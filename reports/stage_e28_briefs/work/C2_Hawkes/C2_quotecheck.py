import re, sys, json, os
P = "pages/C2_Hawkes/"
md = open("C2_Hawkes.md").read()
sec = md.split("## Evidence table")[1].split("## Gaps")[0]
norm = lambda s: re.sub(r"\s+", " ", s).strip()
bad = 0
for line in sec.splitlines():
    if not line.startswith("|") or line.startswith("|---") or line.startswith("| claim"):
        continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    if len(cells) < 4: continue
    quote, f = cells[-2], cells[-1]
    qs = re.findall(r'"([^"]+)"', quote)
    base = f.replace(".pdf", ".txt")
    path = P + f + ".txt" if os.path.exists(P + f + ".txt") else P + base
    txt = norm(open(path, errors="ignore").read())
    txt2 = txt.replace("- ", "")  # de-hyphenation across line breaks
    for q in qs:
        nq = norm(q)
        if nq in txt or nq in txt2 or nq.replace("- ", "") in txt2:
            continue
        bad += 1
        print("MISSING:", f, "|", nq[:120])
print("checked; missing =", bad)
