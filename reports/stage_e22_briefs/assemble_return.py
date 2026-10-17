"""Stage E.22: assemble reports/E.22_RETURN.md from reports/stage_e22_briefs/ret_body.md and its fragments.

Usage: python3 reports/stage_e22_briefs/assemble_return.py
Fragments: start_checks.txt / end_checks.txt (untracked `??` lines dropped), pytest_end.out (summary and rc lines),
ret_partA_tables.md, the microbook report's sections 1 and 4-8 (headings demoted), ret_verify.md, ret_open_choices.md,
ret_cost.md, and ret_vars.json ({"VERIFY_END", "PYTEST_END", "VERIFY_STATUS"}). Refuses if a placeholder is left.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "reports/stage_e22_briefs"


def checks(name: str) -> str:
    return "\n".join(l for l in (B / name).read_text().splitlines() if not l.startswith("??"))


def pytest_end() -> str:
    lines = (B / "pytest_end.out").read_text().splitlines()
    start = next(l for l in lines if l.startswith("start "))
    summ = [l for l in lines if re.search(r"\d+ passed", l)][-1]
    fails = [l for l in lines if l.startswith("FAILED ")]
    rc = [l for l in lines if l.startswith("rc ")][-1]
    return "\n".join([f"$ uv run pytest -q -p no:cacheprovider (detached, {start.split()[1]}-{rc.split()[-1]})", *fails, summ, rc])


def microbook_sections() -> str:
    text = (ROOT / "reports/stage_e22_microbook.md").read_text()
    parts = re.split(r"(?m)^(## .*)$", text)
    keep, out = ("## 1.", "## 4.", "## 5.", "## 6.", "## 7.", "## 8."), []
    for i in range(1, len(parts), 2):
        head, body = parts[i], parts[i + 1]
        if head.startswith(keep):
            body = "\n".join(l for l in body.splitlines()
                             if "they are a design study and not evidence of edge" not in l)
            out.append("#### " + head[3:] + "\n" + body.strip() + "\n")
    return "\n".join(out)


def main() -> int:
    body = (B / "ret_body.md").read_text()
    v = json.loads((B / "ret_vars.json").read_text())
    rep = {
        "START_CHECKS": checks("start_checks.txt"),
        "END_CHECKS": checks("end_checks.txt"),
        "END_PYTEST": pytest_end(),
        "PARTA_TABLES": (B / "ret_partA_tables.md").read_text().strip(),
        "PARTB_TABLES": microbook_sections().strip(),
        "VERIFY_SECTION": (B / "ret_verify.md").read_text().strip(),
        "OPEN_CHOICES": (B / "ret_open_choices.md").read_text().strip(),
        "COST": (B / "ret_cost.md").read_text().strip(),
        **v,
    }
    for k, val in rep.items():
        body = body.replace("{{" + k + "}}", val)
    left = re.findall(r"\{\{[A-Z_]+\}\}", body)
    if left:
        raise SystemExit(f"placeholders left: {left}")
    (ROOT / "reports/E.22_RETURN.md").write_text(body)
    words = len(body.split("## 1. Summary")[1].split("## 2.")[0].split())
    print(f"wrote reports/E.22_RETURN.md ({len(body.splitlines())} lines; section 1 {words} words)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
