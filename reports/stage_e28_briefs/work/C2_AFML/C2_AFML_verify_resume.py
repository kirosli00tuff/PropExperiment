import re, sys, pathlib, unicodedata
base = pathlib.Path("reports/stage_e28_briefs")
md = (base/"C2_AFML.md").read_text()
sec = md.split("## Evidence table",1)[1].split("## Gaps",1)[0]
pages = base/"pages/C2_AFML"
def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("’","'").replace("‘","'").replace("“",'"').replace("”",'"').replace("-\n","")
    return re.sub(r"\s+"," ",s).strip().lower()
ok=bad=0
for line in sec.splitlines():
    if not line.startswith("|") or line.startswith("|---") or "verbatim" in line.lower() and "claim" in line.lower(): continue
    cells=[c.strip() for c in line.strip("|").split("|")]
    if len(cells)<4: continue
    quote=cells[2]; f=cells[3]
    m=re.search(r'"(.+)"',quote)
    if not m: print("NOQUOTE",cells[0][:50]); continue
    q=m.group(1)
    fn=re.match(r"[`]?([\w.\-]+\.(?:txt|md|html|tsv|json))",f)
    if not fn: print("NOFILE",cells[0][:50],f[:40]); continue
    p=pages/fn.group(1)
    if not p.exists():
        p2=base/"work/C2_AFML"/fn.group(1)
        p = p2 if p2.exists() else p
    if not p.exists(): print("MISSINGFILE",fn.group(1)); bad+=1; continue
    t=norm(p.read_text(errors="ignore"))
    parts=[x for x in re.split(r"\s*(?:\.\.\.|…|\[\.\.\.\])\s*",q) if x]
    if all(norm(x) in t for x in parts): ok+=1
    else:
        bad+=1; print("FAIL",fn.group(1),"|",q[:90])
print("ok",ok,"bad",bad)
