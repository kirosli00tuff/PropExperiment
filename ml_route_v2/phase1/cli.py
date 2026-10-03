"""``python -m ml_route_v2.phase1 <step>``: the phase-1 entry point (Stage E.12 Task 1b; Task 6
runs it after the freeze and the purchase).

    python -m ml_route_v2.phase1 build --harness-sha256 SHA --freeze-sha256 SHA
    python -m ml_route_v2.phase1 register --harness-sha256 SHA --freeze-sha256 SHA
    python -m ml_route_v2.phase1 run --harness-sha256 SHA --freeze-sha256 SHA \
        --expected-list-sha256 SHA

Canonical paths only (freeze review F-2): no flag names a path. Every step refuses to start unless
screening.harness_freeze.preflight accepts --harness-sha256 and verify_v2_freeze accepts
--freeze-sha256 on the canonical manifest reports/stage_e12_ml_v2_freeze.json (freeze.
FREEZE_MANIFEST under the repository root); both run before any store, state or ledger is read.
The reports go to the repository's reports/, the Gate 0 tests to ledger/ml_v2_config_ledger.jsonl,
the state to ~/.cache/propexp_e12_phase1 (outside the repository, as E.11's probe cache). The
phase-1 vehicles are not an input (review F-3): ``build`` derives them from the ranking's subset,
reports/stage_e12_ranking.json (build.py, world.phase1_subset). The module constants below are
the only places these paths live; tests monkeypatch them, the command line cannot change them.
After the gates the process lowers its priority (nice 10, compute.platform.lower_priority). Each
step is resumable (build: per stage file; register: idempotent; run: from gate0's family B state,
once). The steps print counts, paths and sha256s; build and register print no return, mean or t.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Any

from data.config import REPO_ROOT

STEPS = ("build", "register", "run")
FREEZE_ROOT = REPO_ROOT  # the manifest is FREEZE_ROOT / freeze.FREEZE_MANIFEST
REPORTS_DIR = REPO_ROOT / "reports"
LEDGER_PATH = REPO_ROOT / "ledger" / "ml_v2_config_ledger.jsonl"
STATE_DIR = Path("~/.cache/propexp_e12_phase1").expanduser()
# The stores are data.config's (phase1_world's defaults); the tests' fixture stores only
WORLD_KW: Mapping[str, Any] = MappingProxyType({})


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m ml_route_v2.phase1",
                                description="ML route v2 phase 1: build, register, run Gate 0")
    sub = p.add_subparsers(dest="step", required=True)
    for step in STEPS:
        s = sub.add_parser(step)
        s.add_argument("--harness-sha256", required=True)
        s.add_argument("--freeze-sha256", required=True)
        if step == "run":
            s.add_argument("--expected-list-sha256", required=True)
    return p


def _gates(args: argparse.Namespace) -> tuple[str, str]:
    """Harness preflight, then the v2 freeze check on the canonical manifest; nothing else runs
    before both pass."""
    from ml_route_v2.phase1.freeze import FREEZE_MANIFEST, verify_v2_freeze
    from screening import harness_freeze

    harness = harness_freeze.preflight(args.harness_sha256)
    verify_v2_freeze(Path(FREEZE_ROOT) / FREEZE_MANIFEST, args.freeze_sha256, root=FREEZE_ROOT)
    return harness, args.freeze_sha256


def _build(gates: tuple[str, str]) -> int:
    from ml_route_v2.phase1.build import panel_peak_note, run_build

    got = run_build(state_dir=STATE_DIR, reports_dir=REPORTS_DIR, world_kw=dict(WORLD_KW),
                    harness_sha256=gates[0], freeze_sha256=gates[1])
    for line in [*got["lines"], *panel_peak_note(got["stages"])]:
        print(line)
    print(f"bars report {got['bars_report']}")
    print(f"c/sigma report {got['c_sigma_report']}")
    print(f"constants {got['fingerprints']['constants']}")
    print(f"inputs {got['fingerprints']['inputs']}")
    return 0


def _register() -> int:
    from ml_route_v2.phase1.gate0_stage import run_register

    got = run_register(STATE_DIR, ledger_path=LEDGER_PATH, reports_dir=REPORTS_DIR)
    print(f"Gate 0 list {got['list']}")
    print(f"list sha256 {got['sha256']}")
    print(f"|A| {got['n_a']}  |B| {got['n_b']}  newly registered {got['n_new']}  ledger entries "
          f"{got['n_registered']}")
    return 0


def _run(args: argparse.Namespace, gates: tuple[str, str]) -> int:
    from ml_route_v2.phase1.gate0_stage import run_gate0

    got = run_gate0(STATE_DIR, ledger_path=LEDGER_PATH, reports_dir=REPORTS_DIR,
                    expected_list_sha256=args.expected_list_sha256, harness_sha256=gates[0],
                    freeze_sha256=gates[1])
    print(f"Gate 0 verdict {got['verdict']} ({got['n_passing']} passing pairs; |A| {got['n_a']}, "
          f"|B| {got['n_b']})")
    print(f"report {got['json']} sha256 {got['json_sha256']}")
    print(f"markdown {got['md']} sha256 {got['md_sha256']}")
    print(f"ledger unchanged by the run: {got['ledger_unchanged']}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """The CLI (module docstring)."""
    args = _parser().parse_args(argv)
    gates = _gates(args)
    from compute.platform import lower_priority

    lower_priority()
    if args.step == "build":
        return _build(gates)
    if args.step == "register":
        return _register()
    return _run(args, gates)


if __name__ == "__main__":
    sys.exit(main())
