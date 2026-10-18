"""Stage E.24 A1 pin inventory: for every file the loader fix may touch (or add), which freeze or
guardrail pins it. Read-only: reads freeze JSON files and runs `git diff --quiet`; writes nothing
but the markdown it prints (redirected to reports/stage_e24_briefs/loader/pins.md by the caller).

    uv run python reports/stage_e24_briefs/loader/pin_inventory.py \
        > reports/stage_e24_briefs/loader/pins.md
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

CANDIDATES = [
    "base_rules/context.py", "base_rules/store.py", "base_rules/NEW.py",
    "multiday/book.py", "multiday/run.py", "multiday/evaluate.py", "multiday/daily.py",
    "multiday/NEW.py",
    "trigger_hold/book.py", "trigger_hold/run.py", "trigger_hold/evaluate.py",
    "trigger_hold/NEW.py",
    "tests/test_multiday_NEW.py", "tests/test_trigger_hold_NEW.py", "tests/test_base_rules_NEW.py",
    "mdio/__init__.py", "mdio/bounded.py", "mdio/book_files.py",
    "tests/test_mdio_bounded.py", "tests/test_mdio_book_files.py",
    "reports/stage_e24_briefs/loader/replay_e23.py",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(rel: str) -> dict:
    return json.loads((REPO / rel).read_text())


def paths_of(obj) -> set[str]:  # noqa: ANN001
    """Every repo-relative path named in a freeze: dict keys and 'path' values, list strings."""
    out: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and "/" in k and "." in k.rsplit("/", 1)[-1]:
                out.add(k)
            if k == "path" and isinstance(v, str):
                out.add(v)
            out |= paths_of(v)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, str) and "/" in v and "." in v.rsplit("/", 1)[-1]:
                out.add(v)
            else:
                out |= paths_of(v)
    return out


def sources() -> list[tuple[str, set[str], list[str]]]:
    """(source name, exact paths, globs enforced by that source's verify)."""
    src: list[tuple[str, set[str], list[str]]] = []
    h = load("reports/stage_e2b_harness_freeze.json")
    src.append(("harness v13 manifest (stage_e2b_harness_freeze.json files)", set(h["files"]),
                [f"{d}/*" for d in h["harness_dirs"]] + [f"{d}/**" for d in h["harness_dirs"]]))
    src.append(("E.16 guardrail git diff 8f388c8", set(),
                ["base_rules/*", "base_rules/**", "tests/test_base_rules_*.py",
                 "reports/stage_e16_prereg_*.md"]))
    e16 = load("reports/stage_e16_freeze.json")
    src.append(("stage_e16_freeze.json", paths_of(e16["files"]), list(e16["frozen_globs"])))
    src.append(("stage_e20_h6_freeze.json", paths_of(load("reports/stage_e20_h6_freeze.json")),
                []))
    src.append(("stage_e1_freeze.json", paths_of(load("reports/stage_e1_freeze.json")), []))
    e21 = load("reports/stage_e21_freeze.json")
    src.append(("stage_e21_freeze.json (verify globs multiday/*.py, tests/test_multiday_*.py, "
                "base_rules/*.py)", paths_of(e21["files"]) | set(e21["inputs"].values()),
                ["multiday/*.py", "tests/test_multiday_*.py", "base_rules/*.py"]))
    e23 = load("reports/stage_e23_freeze.json")
    src.append(("stage_e23_freeze.json (verify globs trigger_hold/*.py, "
                "tests/test_trigger_hold_*.py + reused multiday/*.py, base_rules/*.py)",
                paths_of(e23["files"]) | set(e23["inputs"].values()),
                ["trigger_hold/*.py", "tests/test_trigger_hold_*.py", "multiday/*.py",
                 "base_rules/*.py"]))
    for k in range(1, 9):
        rel = f"reports/stage_e_k{k}_member_freeze.json"
        if (REPO / rel).is_file():
            d = load(rel)
            src.append((Path(rel).name, paths_of(d.get("files", {})),
                        [f"{d['members_dir']}/*"] if d.get("members_dir") else []))
    lines = (REPO / "reports/stage_e22_f1_files.sha256").read_text().split("\n")
    src.append(("stage_e22_f1_files.sha256", {ln.split()[1] for ln in lines if ln.strip()}, []))
    for rel in ("reports/stage_e18_freeze.json", "reports/stage_e20_search_freeze.json",
                "reports/stage_d1f_harness_freeze.json", "reports/stage_e12_ml_v2_freeze.json",
                "reports/stage_e2a_ml_freeze.json", "reports/stage_e14_c1_freeze_inputs.json"):
        if (REPO / rel).is_file():
            src.append((Path(rel).name + " (extra)", paths_of(load(rel)), []))
    return src


def main() -> None:
    src = sources()
    rc = subprocess.run(["git", "diff", "--quiet", "8f388c8", "--", "base_rules",
                         *sorted(str(p.relative_to(REPO)) for p in
                                 REPO.glob("tests/test_base_rules_*.py")),
                         *sorted(str(p.relative_to(REPO)) for p in
                                 REPO.glob("reports/stage_e16_prereg_*.md"))],
                        cwd=REPO, check=False).returncode
    print("# Stage E.24 A1 pin inventory (written before any code change)\n")
    print("Generated by reports/stage_e24_briefs/loader/pin_inventory.py (read-only). `NEW` rows "
          "stand for a file that would be ADDED in that directory (directory globs enforced by "
          "a freeze's verify refuse unlisted new files too).\n")
    print(f"E.16 guardrail `git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py "
          f"reports/stage_e16_prereg_*.md`: exit {rc} (must stay 0).\n")
    print("Harness v13 manifest sha256 (reports/stage_e2b_harness_freeze.json): "
          f"{sha(REPO / 'reports/stage_e2b_harness_freeze.json')} (E.23 prereg names "
          "dd2bcc60...).\n")
    print("| File | Exists | sha256 (now) | Pinned by |")
    print("|---|---|---|---|")
    for rel in CANDIDATES:
        p = REPO / rel
        hits = []
        for name, exact, globs in src:
            if rel in exact:
                hits.append(f"{name} [listed]")
            elif any(fnmatch.fnmatch(rel, g) for g in globs):
                hits.append(f"{name} [glob]")
        exists = p.is_file()
        print(f"| {rel} | {'yes' if exists else 'no'} | "
              f"{sha(p)[:16] + '...' if exists else '-'} | "
              f"{'; '.join(hits) if hits else 'UNPINNED'} |")
    print("\nSources read:")
    for name, exact, globs in src:
        print(f"- {name}: {len(exact)} listed paths; globs {globs if globs else 'none'}")


if __name__ == "__main__":
    main()
