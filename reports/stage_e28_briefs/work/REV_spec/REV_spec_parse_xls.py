"""Print header row and every row mentioning QG / E-mini Natural Gas from the CME Globex product reference sheet."""
import sys
import xlrd  # type: ignore

path = sys.argv[1]
book = xlrd.open_workbook(path)
for sh in book.sheets():
    print(f"== sheet {sh.name!r} rows={sh.nrows} cols={sh.ncols}")
    hdr_row = None
    for r in range(min(sh.nrows, 15)):
        vals = [str(sh.cell_value(r, c)).strip() for c in range(sh.ncols)]
        if any(v.lower().startswith("product") or "match" in v.lower() for v in vals):
            hdr_row = r
            print("HEADER", r, [f"{i}:{v}" for i, v in enumerate(vals) if v])
            break
    hits = 0
    for r in range(sh.nrows):
        vals = [str(sh.cell_value(r, c)).strip() for c in range(sh.ncols)]
        joined = " | ".join(vals)
        low = joined.lower()
        if ("e-mini natural gas" in low or "emini natural gas" in low or "e-mini henry hub" in low
                or any(v == "QG" for v in vals)):
            hits += 1
            if hits <= 12:
                print(f"ROW {r}:", [f"{i}:{v}" for i, v in enumerate(vals) if v])
    print(f"hits={hits}")
