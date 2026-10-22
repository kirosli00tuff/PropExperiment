"""Header rows of 'All Futures and Options', LEGEND rows about matching / notes / implied, and QG rows."""
import sys
import xlrd  # type: ignore

book = xlrd.open_workbook(sys.argv[1])
sh = book.sheet_by_name("All Futures and Options")
for r in range(0, 4):
    vals = [str(sh.cell_value(r, c)).strip().replace("\n", " ") for c in range(sh.ncols)]
    print(f"HDR{r}:", [f"{i}:{v}" for i, v in enumerate(vals) if v])
for r in range(sh.nrows):
    vals = [str(sh.cell_value(r, c)).strip() for c in range(sh.ncols)]
    if vals[4] in ("QG", "QG-QG") or vals[4].startswith("QG"):
        print(f"ROW{r}:", [f"{i}:{v}" for i, v in enumerate(vals) if v])
lg = book.sheet_by_name("LEGEND")
for r in range(lg.nrows):
    vals = [str(lg.cell_value(r, c)).strip().replace("\n", " ") for c in range(lg.ncols)]
    j = " | ".join(v for v in vals if v)
    low = j.lower()
    if "note 4" in low or "match" in low or "implied" in low or "fifo" in low or j.startswith("F ") or " f " in low:
        print(f"LEGEND{r}: {j[:300]}")
