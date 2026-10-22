"""Print the CME Globex Product Reference Sheet rows for given Globex codes (lead's check of matching algorithms)."""
import sys
import xlrd

for path in sys.argv[2:]:
    book = xlrd.open_workbook(path)
    sh = book.sheet_by_name("All Futures and Options")
    for r in range(sh.nrows):
        row = [str(c.value) for c in sh.row(r)]
        if len(row) > 10 and row[4] in sys.argv[1].split(","):
            print(path.rsplit("/", 1)[-1], r, row[:11])
