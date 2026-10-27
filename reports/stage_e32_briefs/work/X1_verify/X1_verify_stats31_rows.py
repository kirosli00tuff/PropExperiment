"""Count markdown table data rows (excluding header and separator) per heading block in stats31.md."""
import sys, re
lines = open(sys.argv[1]).read().splitlines()
blocks = []; cur = None
for i, l in enumerate(lines, 1):
    if l.startswith("#"):
        cur = [i, l[:70], 0, 0]; blocks.append(cur); continue
    if cur and l.startswith("|"):
        if re.match(r"^\|[-| :]+\|$", l): cur[3] += 1; continue
        cur[2] += 1
for b in blocks:
    # data rows = table lines minus one header per table (tables = separator count)
    print(b[0], b[1], "table_lines", b[2], "tables", b[3], "data_rows", b[2]-b[3])
