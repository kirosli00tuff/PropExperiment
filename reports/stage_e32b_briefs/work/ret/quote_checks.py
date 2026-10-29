"""Quote a checks.sh output verbatim for the return's section 2, except the `git status --short` listing, which is
replaced by its counts plus every tracked-change line and every line naming this stage (E.32b) verbatim.
Usage: python3 quote_checks.py <checks file>"""
import sys
from pathlib import Path

lines = Path(sys.argv[1]).read_text().splitlines()
out, block, inside = [], [], False
for ln in lines:
    if ln == "$ git status --short":
        out.append(ln); inside = True; continue
    if inside and ln.startswith("$ "):
        inside = False
        keep = [b for b in block if not b.startswith("??") or "32b" in b or "32B" in b]
        out.append(f"[{len(block)} lines: {sum(b.startswith('??') for b in block)} untracked, "
                   f"{sum(not b.startswith('??') for b in block)} tracked changes; quoted below: every tracked change "
                   f"and every line naming E.32b ({len(keep)})]")
        out.extend(keep)
    if inside:
        block.append(ln); continue
    out.append(ln)
print("\n".join(out))
