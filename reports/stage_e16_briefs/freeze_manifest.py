"""Stage E.16 Task 4: write or verify the base-rule freeze manifest reports/stage_e16_freeze.json.

    uv run python reports/stage_e16_briefs/freeze_manifest.py write    # the lead, at the freeze
    uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected <manifest sha256>   # E.17, first

The manifest lists every frozen file (path, sha256, bytes) in FROZEN_GLOBS order, plus the pins (harness v10,
C1's freeze file). It never lists or opens a market-data file: anything under data/processed*, data/vendor or
data/sealed is refused. verify: the manifest's own sha256 equals --expected, every entry matches, every pin
matches, and no frozen glob matches a file the manifest lacks. Exit 0 iff all pass. Reads bytes only; writes only
the manifest (write mode).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "reports" / "stage_e16_freeze.json"
SCHEMA = "stage_e16_freeze/1"
# Every frozen input, in order. Globs are relative to the repo root.
FROZEN_GLOBS = (
    # the pre-registration and the lead's and workers' tables
    "reports/stage_e16_prereg_H1.md",
    "reports/stage_e16_prereg_H2.md",
    "reports/stage_e16_prereg_H3.md",
    "reports/stage_e16_prereg_H4.md",
    "reports/stage_e16_prereg_H5.md",
    "reports/stage_e16_prereg_common.md",
    "reports/stage_e16_briefs/lead_spec.md",
    "reports/stage_e16_rulings.md",
    "reports/stage_e16_review.md",
    "reports/stage_e16_settlement.json",
    "reports/stage_e16_settlement.md",
    "reports/stage_e16_overlap.md",
    "reports/stage_e16_calendars/*.json",
    "reports/stage_e16_calendars/scripts/*.py",
    "reports/stage_e16_calendars.md",
    "reports/stage_e16_power.json",
    "reports/stage_e16_power.md",
    "reports/stage_e16_windows.json",
    "reports/stage_e16_briefs/release_touch.md",
    "reports/stage_e16_briefs/derive_windows.py",
    "reports/stage_e16_briefs/make_prereg.py",
    "reports/stage_e16_briefs/freeze_manifest.py",
    # the code and its tests
    "base_rules/*.py",
    "base_rules/README.md",
    "tests/test_base_rules_*.py",
    "tests/_base_rules_fixtures.py",
    # frozen program inputs the runner reads
    "reports/stage_e12_quotes_ext2010.json",
    "reports/stage_e2b_release_calendar.json",
    "reports/stage_e14_cal_releases.json",
    "reports/stage_e2a_costs.json",
    "reports/stage_e2a_vehicles.json",
    "reports/stage_e2a_vehicle_sizes.json",
    "reports/stage_e2a_epsilon.json",
    "data/calendars/hist2010/energy.json",
    "data/calendars/hist2010/equity.json",
    "data/calendars/hist2010/fx.json",
    "data/calendars/hist2010/grains.json",
    "data/calendars/hist2010/metals.json",
    "data/calendars/hist2010/rates.json",
    "data/calendars/__init__.py",
    "data/calendars/energy.py",
    "data/calendars/equity.py",
    "data/calendars/fx.py",
    "data/calendars/grains.py",
    "data/calendars/livestock.py",
    "data/calendars/metals.py",
    "data/calendars/rates.py",
    # frozen program modules the runner imports (review F-06; data/hist_calendar.py and data/config.py are left
    # out on purpose: E.17's later harness changes them by rulings R-C6 and U1)
    "screening/stage_e_engine.py",
    "screening/stage_e_frozen.py",
    "screening/stage_e_rules.py",
    "screening/stage_e_verdict.py",
    "screening/trial_registry.py",
    "rules/products.py",
    "rules/price_limits.py",
    "data/stage_e_bars.py",
    "data/hist_bars.py",
    "data/group_session.py",
    "data/session.py",
    "strategy/stage_e/interface.py",
)
PINS = {
    "harness_v10_manifest_sha256": "fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b",
    "c1_freeze_file": ["reports/stage_e14_prereg_C1.md",
                       "afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b"],
}
REFUSED_PREFIXES = ("data/processed", "data/vendor", "data/sealed")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def frozen_files() -> list[Path]:
    out: list[Path] = []
    for pattern in FROZEN_GLOBS:
        hits = sorted(p for p in REPO.glob(pattern) if p.is_file() and "__pycache__" not in p.parts)
        if not hits and "*" not in pattern:
            raise SystemExit(f"REFUSED: frozen file missing: {pattern}")
        for p in hits:
            rel = p.relative_to(REPO).as_posix()
            if rel.startswith(REFUSED_PREFIXES):
                raise SystemExit(f"REFUSED: market-data path in the freeze: {rel}")
            if p not in out:
                out.append(p)
    return out


def check_pins() -> list[str]:
    path, want = PINS["c1_freeze_file"]
    return [] if sha256(REPO / path) == want else [f"pin mismatch: {path}"]


def write() -> int:
    errors = check_pins()
    if errors:
        print("\n".join(errors))
        return 1
    files = [{"path": p.relative_to(REPO).as_posix(), "sha256": sha256(p), "bytes": p.stat().st_size}
             for p in frozen_files()]
    body = {"schema": SCHEMA,
            "created_pdt": datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M:%S"),
            "pins": PINS, "frozen_globs": list(FROZEN_GLOBS), "files": files}
    MANIFEST.write_text(json.dumps(body, indent=1) + "\n")
    print(f"wrote {MANIFEST.relative_to(REPO)}: {len(files)} files; manifest sha256 {sha256(MANIFEST)}")
    return 0


def verify(expected: str) -> int:
    errors = []
    got = sha256(MANIFEST)
    if got != expected:
        errors.append(f"manifest sha256 {got} != expected {expected}")
    body = json.loads(MANIFEST.read_text())
    if body.get("schema") != SCHEMA or body.get("pins") != PINS:
        errors.append("schema or pins differ from this script's")
    listed = {e["path"] for e in body["files"]}
    for e in body["files"]:
        p = REPO / e["path"]
        if not p.is_file():
            errors.append(f"missing: {e['path']}")
        elif sha256(p) != e["sha256"] or p.stat().st_size != e["bytes"]:
            errors.append(f"changed: {e['path']}")
    for p in frozen_files():
        if p.relative_to(REPO).as_posix() not in listed:
            errors.append(f"unlisted file matches a frozen glob: {p.relative_to(REPO).as_posix()}")
    errors += check_pins()
    print("\n".join(errors) if errors else f"E.16 freeze OK: {len(listed)} files; manifest sha256 {got}")
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("write", "verify"))
    ap.add_argument("--expected")
    a = ap.parse_args()
    if a.mode == "write":
        return write()
    if not a.expected:
        ap.error("verify needs --expected")
    return verify(a.expected)


if __name__ == "__main__":
    sys.exit(main())
