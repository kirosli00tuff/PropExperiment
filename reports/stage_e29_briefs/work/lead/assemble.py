"""Stage E.29: fill reports/E.29_RETURN.md from work/lead/return_skeleton.md and the lead's section files.

Reads only work/lead/*.md, start_checks.txt and end_checks.txt; writes only reports/E.29_RETURN.md. Fails if an
input is missing or a marker is left. Check-file lines longer than 200 characters are cut, with a note.
"""
from __future__ import annotations

import sys
from pathlib import Path

LEAD = Path(__file__).resolve().parent
BRIEFS = LEAD.parent.parent
OUT = BRIEFS.parent / "E.29_RETURN.md"
MAX = 200


def text(name: str) -> str:
    return (LEAD / name).read_text().strip()


def checks(name: str) -> str:
    lines = []
    for ln in (BRIEFS / name).read_text().rstrip("\n").splitlines():
        lines.append(ln if len(ln) <= MAX else f"{ln[:MAX]} [line cut at {MAX} of {len(ln)} characters]")
    return "\n".join(lines)


def split_answers() -> tuple[str, str, str]:
    a = text("answers.md").replace("@@COMPACT@@", text("compact_tables.md"))
    tables, rest = a.split("### 3.4 Answers", 1)
    answers, ranking = rest.split("### 3.5", 1)
    return tables.strip(), answers.strip(), ranking.split("\n", 1)[1].strip()


def main() -> int:
    tables, answers, ranking = split_answers()
    fill = {
        "@@SUMMARY@@": text("summary.md"),
        "@@START@@": checks("start_checks.txt"),
        "@@END@@": checks("end_checks.txt"),
        "@@PYTEST@@": text("pytest.md"),
        "@@TABLES@@": tables,
        "@@ANSWERS@@": answers,
        "@@RANKING@@": ranking,
        "@@DELEGATION@@": text("delegation.md"),
        "@@VERIFICATION@@": text("verification.md"),
        "@@OC@@": text("oc.md"),
        "@@DECISIONS@@": text("decisions.md"),
        "@@COST@@": text("cost.md"),
    }
    doc = (LEAD / "return_skeleton.md").read_text()
    for k, v in fill.items():
        if doc.count(k) != 1:
            print(f"marker {k} found {doc.count(k)} times")
            return 1
        doc = doc.replace(k, v)
    if "@@" in doc:
        print("marker left")
        return 1
    OUT.write_text(doc)
    print(f"wrote {OUT} ({len(doc.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
