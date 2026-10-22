"""Print +-W chars of context around a keyword in a file (whitespace-collapsed). Usage: ctx.py file keyword [W] [maxhits]"""
import re, sys, html
f, kw = sys.argv[1], sys.argv[2]; W = int(sys.argv[3]) if len(sys.argv) > 3 else 120; mx = int(sys.argv[4]) if len(sys.argv) > 4 else 4
t = open(f, encoding="utf-8", errors="ignore").read()
if f.endswith((".html", ".htm")):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
t = re.sub(r"\s+", " ", t)
n = 0
for m in re.finditer(re.escape(kw), t, flags=re.I):
    print(f"[{f.split('/')[-1][:40]} @{m.start()}] ...{t[max(0,m.start()-W):m.end()+W]}...")
    n += 1
    if n >= mx: break
if n == 0: print(f"[{f.split('/')[-1][:40]}] NO HIT for {kw!r}")
