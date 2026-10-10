"""Stage E.17: print a guardrail-check file for the return document, verbatim except that the long runs of untracked
evidence-page lines from earlier stages (reports/stage_e12/13/14/16_briefs/pages, margin_pages) are collapsed into one
line naming their count, as E.16's return did. Usage: python3 collapse_checks.py <checks.txt>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAGES = re.compile(r"^\?\? reports/stage_e1[2346]_briefs/(pages|margin_pages)")


def main() -> int:
    lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    out, run = [], 0
    for line in lines:
        if PAGES.match(line):
            run += 1
            continue
        if run:
            out.append(f"?? reports/stage_e12/e13/e14/e16_briefs page files: {run} lines (collapsed; full text in "
                       f"{sys.argv[1]})")
            run = 0
        out.append(line)
    if run:
        out.append(f"?? reports/stage_e12/e13/e14/e16_briefs page files: {run} lines (collapsed)")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
