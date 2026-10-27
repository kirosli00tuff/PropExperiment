"""Copy verbatim line ranges of stats31.md into an appendix with line references. Computes nothing."""
import re
SRC = "reports/stage_e31_briefs/work/pilot/runs/stats31.md"
OUT = "reports/stage_e32_briefs/work/X1_exposure/X1_tableC_appendix.md"
lines = open(SRC).read().split("\n")
heads = [(i + 1, l) for i, l in enumerate(lines) if l.startswith("## ") or l.startswith("### ")]
ranges = [("Primary population, three models (## section)", 21, 80),
          ("Net results for the five firms (## section)", 81, 102),
          ("All cells: (c) trade-through (gate), ZM.v.0, DAY", 585, 644),
          ("All cells: (c) trade-through (gate), ZM.v.0, OVERNIGHT", 645, 704),
          ("All cells: (c) trade-through (gate), ZM.v.1, DAY", 705, 764),
          ("All cells: (c) trade-through (gate), ZM.v.1, OVERNIGHT", 765, 824),
          ("All cells: (a) K, ZM.v.0, DAY", 105, 164),
          ("All cells: (b) FIFO back of queue, ZM.v.0, DAY", 345, 404),
          ("Splits, all twelve blocks (## Splits section)", 1071, 1554),
          ("Feasible round trips: the loop", 1555, 1564),
          ("Implied-liquidity check", 1565, 1575),
          ("Exclusions", 1576, 1582)]
with open(OUT, "w") as f:
    f.write("# X1 Table C appendix: verbatim copy of stats31.md line ranges (no computation)\n\n")
    f.write("Source: %s (1595 lines). Each block below is preceded by its section name and source line range.\n\n" % SRC)
    for name, a, b in ranges:
        f.write("\n<!-- SOURCE %s lines %d-%d : %s -->\n" % (SRC, a, b, name))
        f.write("\n".join(lines[a - 1:b]) + "\n")
print("ok", len(lines))
