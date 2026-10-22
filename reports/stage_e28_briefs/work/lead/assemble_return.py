"""Builds reports/E.28_RETURN.md from return_src.md: @@INCLUDE path@@, @@INCLUDE_LINES path a b@@, @@OPEN_CHOICES@@
(return_oc.md) and @@NAME@@ blocks from return_fill.md and return_cost.md ("=== NAME ===" headers). Exits 1 if a
marker is left. Usage: python3 assemble_return.py (from the repo root)"""
import re, sys
from pathlib import Path
L = Path("reports/stage_e28_briefs/work/lead")
blocks = {}
for f in ("return_fill.md", "return_cost.md"):
    if (L / f).exists():
        for name, body in re.findall(r"^=== (\w+) ===\n(.*?)(?=^=== \w+ ===\n|\Z)", (L / f).read_text(), re.S | re.M):
            blocks[name] = body.rstrip("\n")
blocks["OPEN_CHOICES"] = (L / "return_oc.md").read_text().rstrip("\n")
text = (L / "return_src.md").read_text()
text = re.sub(r"@@INCLUDE_LINES (\S+) (\d+) (\d+)@@",
              lambda m: "".join(Path(m[1]).read_text().splitlines(True)[int(m[2]) - 1:int(m[3])]).rstrip("\n"), text)
text = re.sub(r"@@INCLUDE (\S+)@@", lambda m: Path(m[1]).read_text().rstrip("\n") if Path(m[1]).exists() else m[0], text)
for _ in range(3):
    text = re.sub(r"@@([A-Z0-9_]+)@@", lambda m: blocks.get(m[1], m[0]), text)
text = re.sub(r"@@INCLUDE (\S+)@@", lambda m: Path(m[1]).read_text().rstrip("\n") if Path(m[1]).exists() else m[0], text)
left = sorted(set(re.findall(r"@@[A-Z0-9_]+@@|@@INCLUDE[^@]*@@", text)))
Path("reports/E.28_RETURN.md").write_text(text)
sec1 = text.split("## 1. Summary", 1)[1].split("## 2.", 1)[0]
print(f"written reports/E.28_RETURN.md: {len(text.splitlines())} lines; section 1 words {len(sec1.split())}; markers left {left}")
sys.exit(1 if left else 0)
