"""Stage E.14 (harness v10): the append-only trial registry, ledger/trial_registrations.jsonl.

    uv run python -m screening.trial_registry status
    uv run python -m screening.trial_registry register --test C2 --ids C2-T1 C2-T2 \
        --freeze reports/stage_e14_prereg_C2.md --freeze-sha256 <sha> --harness-sha256 <sha>
    uv run python -m screening.trial_registry init      # writes the baseline line once

The program's cumulative trial count N carries forward (CLAUDE.md). Every registered test adds to
it at registration, whatever its outcome. One JSON object per line, never rewritten:
- the first line is the baseline record, N = 471, citing reports/E.12_RETURN.md:561 ("New program
  N = 198 + 273 = 471");
- every later line registers one test (C2, C1, ...): its test ids, its freeze file's path and
  sha256 (checked against the file), the harness manifest sha256 (the preflight passes first),
  N before and after (after = before + number of ids), and the local time (America/Vancouver).
The registry's N is the last line's ``n_after``. A duplicate test or test id is refused, as is a
ledger whose lines do not chain (each ``n_before`` equal to the previous ``n_after``), whose first
line is not the baseline, or that does not parse. The purchase path (data.pull_hist) and test C2's
evaluation (screening.stage_e14_c2) refuse to start unless their test ids are registered here.

Tests pass a temporary ``path``; nothing in the test suite appends to the real file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from data.config import REPO_ROOT

REGISTRY_PATH = REPO_ROOT / "ledger" / "trial_registrations.jsonl"
SCHEMA = "trial_registration/1"
LOCAL_TZ = ZoneInfo("America/Vancouver")
BASELINE_ENTRY_ID = "baseline"
BASELINE_N = 471
BASELINE_SOURCE = "reports/E.12_RETURN.md:561"
BASELINE_QUOTE = "New program N = 198 + 273 = 471"
FIELDS = ("schema", "entry_id", "test", "test_ids", "freeze_path", "freeze_sha256",
          "harness_sha256", "n_before", "n_after", "time_local", "source", "note")
_TEST = re.compile(r"[A-Z][A-Za-z0-9]{0,15}")
_ID = re.compile(r"[A-Z][A-Za-z0-9]{0,15}-[A-Za-z0-9]{1,16}")
_SHA = re.compile(r"[0-9a-f]{64}")
RC_REFUSED = 2


class TrialRegistryError(RuntimeError):
    """The registry is malformed, or a registration or a check was refused."""


def _now() -> str:
    return datetime.now(LOCAL_TZ).isoformat(timespec="seconds")


def _sha(value: Any, what: str) -> str:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise TrialRegistryError(f"{what} {value!r} is not a sha256 (64 lowercase hex)")
    return value


def baseline_record(time_local: str | None = None) -> dict[str, Any]:
    """The first line: N = 471 after E.12, no test registered by it."""
    return {"schema": SCHEMA, "entry_id": BASELINE_ENTRY_ID, "test": None, "test_ids": [],
            "freeze_path": None, "freeze_sha256": None, "harness_sha256": None,
            "n_before": None, "n_after": BASELINE_N, "time_local": time_local or _now(),
            "source": BASELINE_SOURCE,
            "note": f"baseline: the program's N after Stage E.12 (\"{BASELINE_QUOTE}\")"}


# ------------------------------------------------------------------ reading ----
def _check_line(entry: Any, i: int, previous: dict | None) -> dict[str, Any]:
    where = f"line {i + 1}"
    if not isinstance(entry, dict) or set(entry) != set(FIELDS) or entry["schema"] != SCHEMA:
        raise TrialRegistryError(f"{where}: not a {SCHEMA} record with fields {list(FIELDS)}")
    n_after = entry["n_after"]
    if not isinstance(n_after, int) or isinstance(n_after, bool):
        raise TrialRegistryError(f"{where}: n_after {n_after!r} is not an integer")
    if previous is None:
        if entry["entry_id"] != BASELINE_ENTRY_ID or n_after != BASELINE_N or entry["test_ids"]:
            raise TrialRegistryError(f"{where}: the first line must be the baseline N = "
                                     f"{BASELINE_N}")
        return entry
    ids = entry["test_ids"]
    if not isinstance(ids, list) or not ids or entry["n_before"] != previous["n_after"] \
            or n_after != entry["n_before"] + len(ids):
        raise TrialRegistryError(f"{where}: does not chain (n_before must be the previous "
                                 "n_after, n_after = n_before + the number of test ids)")
    return entry


def read_registry(path: Path = REGISTRY_PATH) -> list[dict[str, Any]]:
    """Every line, checked: baseline first, chained N, unique entry ids, tests and test ids."""
    path = Path(path)
    if not path.is_file():
        raise TrialRegistryError(f"{path} does not exist (run `python -m "
                                 "screening.trial_registry init` once)")
    entries: list[dict[str, Any]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            raise TrialRegistryError(f"{path.name} line {i + 1} is blank")
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TrialRegistryError(f"{path.name} line {i + 1} is not JSON: {exc}") from exc
        entries.append(_check_line(raw, i, entries[-1] if entries else None))
    if not entries:
        raise TrialRegistryError(f"{path} is empty: the baseline line is missing")
    ids = [x for e in entries for x in e["test_ids"]]
    tests = [e["test"] for e in entries[1:]]
    entry_ids = [e["entry_id"] for e in entries]
    if len(set(ids)) != len(ids) or len(set(tests)) != len(tests) \
            or len(set(entry_ids)) != len(entry_ids):
        raise TrialRegistryError(f"{path.name}: a test, test id or entry id repeats")
    return entries


def current_n(path: Path = REGISTRY_PATH) -> int:
    """The program's N: the last line's n_after."""
    return int(read_registry(path)[-1]["n_after"])


def registration_of(test_id: str, path: Path = REGISTRY_PATH) -> dict[str, Any] | None:
    for entry in read_registry(path):
        if test_id in entry["test_ids"]:
            return entry
    return None


def require_registered(test_ids: Sequence[str], *, test: str | None = None,
                       freeze_sha256: str | None = None,
                       path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """The one registration holding every id in ``test_ids`` (of ``test``, under
    ``freeze_sha256`` when given); TrialRegistryError otherwise."""
    if not test_ids:
        raise TrialRegistryError("no test ids to check")
    entries = read_registry(path)
    holders: dict[str, dict[str, Any]] = {}
    for test_id in test_ids:
        holder = next((e for e in entries if test_id in e["test_ids"]), None)
        if holder is None:
            raise TrialRegistryError(f"test id {test_id} is not registered in "
                                     f"{Path(path).name}: register the test first (order of "
                                     "events)")
        holders[holder["entry_id"]] = holder
    if len(holders) != 1:
        raise TrialRegistryError(f"test ids {list(test_ids)} are not registered together")
    entry = next(iter(holders.values()))
    if test is not None and entry["test"] != test:
        raise TrialRegistryError(f"{list(test_ids)} are registered under test "
                                 f"{entry['test']!r}, not {test!r}")
    if freeze_sha256 is not None and entry["freeze_sha256"] != freeze_sha256:
        raise TrialRegistryError(f"{list(test_ids)} were registered with freeze sha256 "
                                 f"{str(entry['freeze_sha256'])[:12]}..., not "
                                 f"{freeze_sha256[:12]}...")
    return entry


# ------------------------------------------------------------------ writing ----
def _append(path: Path, entry: dict[str, Any]) -> None:
    with Path(path).open("a", encoding="utf-8") as fh:  # append-only, never rewritten
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def init_registry(path: Path = REGISTRY_PATH, *, time_local: str | None = None
                  ) -> dict[str, Any]:
    """Create the registry with its baseline line. Refused if the file exists at all."""
    path = Path(path)
    if path.exists():
        raise TrialRegistryError(f"{path} exists: the baseline is written once, never again")
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = baseline_record(time_local)
    with path.open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def _freeze_record(freeze: Path, freeze_sha256: str) -> str:
    freeze = Path(freeze)
    if not freeze.is_file():
        raise TrialRegistryError(f"freeze file {freeze} does not exist")
    got = hashlib.sha256(freeze.read_bytes()).hexdigest()
    if got != freeze_sha256:
        raise TrialRegistryError(f"freeze file {freeze.name}: sha256 {got[:12]}... is not the "
                                 f"given {freeze_sha256[:12]}...")
    resolved = freeze.resolve()
    return str(resolved.relative_to(REPO_ROOT)) if resolved.is_relative_to(REPO_ROOT) \
        else str(resolved)


def register(test: str, test_ids: Sequence[str], freeze: Path, freeze_sha256: str,
             harness_sha256: str, *, path: Path = REGISTRY_PATH,
             preflight: Callable[[str], str] | None = None, note: str = "",
             time_local: str | None = None) -> dict[str, Any]:
    """Append one registration: N goes from the registry's N to N + len(test_ids).
    ``preflight`` (the harness preflight; the CLI passes screening.harness_freeze.preflight)
    runs first and must return ``harness_sha256``."""
    _sha(harness_sha256, "harness sha256")
    _sha(freeze_sha256, "freeze sha256")
    if preflight is not None and preflight(harness_sha256) != harness_sha256:
        raise TrialRegistryError("the harness preflight did not confirm the given sha256")
    if not isinstance(test, str) or not _TEST.fullmatch(test):
        raise TrialRegistryError(f"test {test!r} is not a test label such as C2")
    ids = list(test_ids)
    if not ids or len(set(ids)) != len(ids) or any(
            not isinstance(t, str) or not _ID.fullmatch(t) or not t.startswith(f"{test}-")
            for t in ids):
        raise TrialRegistryError(f"test ids {ids} must be distinct ids of the form {test}-T1")
    entries = read_registry(path)
    taken = {x for e in entries for x in e["test_ids"]}
    if set(ids) & taken or any(e["test"] == test for e in entries):
        raise TrialRegistryError(f"{test} or one of {ids} is already registered: a registration "
                                 "is never repeated or amended")
    n_before = int(entries[-1]["n_after"])
    entry = {"schema": SCHEMA, "entry_id": f"r{len(entries):03d}-{test}", "test": test,
             "test_ids": ids, "freeze_path": _freeze_record(freeze, freeze_sha256),
             "freeze_sha256": freeze_sha256, "harness_sha256": harness_sha256,
             "n_before": n_before, "n_after": n_before + len(ids),
             "time_local": time_local or _now(), "source": None, "note": note}
    _append(path, entry)
    read_registry(path)  # the file still parses and chains with the new line
    return entry


# ------------------------------------------------------------------ CLI ----
def main(argv: list[str] | None = None, *, path: Path = REGISTRY_PATH,
         preflight: Callable[[str], str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m screening.trial_registry")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="print N and the registered tests")
    sub.add_parser("init", help="write the baseline line (once; refused if the file exists)")
    reg = sub.add_parser("register", help="register one test (N += number of ids)")
    reg.add_argument("--test", required=True)
    reg.add_argument("--ids", nargs="+", required=True)
    reg.add_argument("--freeze", required=True)
    reg.add_argument("--freeze-sha256", required=True)
    reg.add_argument("--harness-sha256", required=True)
    reg.add_argument("--note", default="")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            entry = init_registry(path)
            print(f"wrote {Path(path).name}: baseline N = {entry['n_after']}")
            return 0
        if args.command == "status":
            entries = read_registry(path)
            print(f"N = {entries[-1]['n_after']} ({len(entries)} lines)")
            for e in entries[1:]:
                print(f"{e['entry_id']}: {e['test']} {e['test_ids']} N {e['n_before']} -> "
                      f"{e['n_after']} at {e['time_local']}")
            return 0
        if preflight is None:
            from screening import harness_freeze

            preflight = harness_freeze.preflight
        entry = register(args.test, args.ids, Path(args.freeze), args.freeze_sha256,
                         args.harness_sha256, path=path, preflight=preflight, note=args.note)
    except Exception as exc:  # noqa: BLE001 — every refusal is reported, nothing half-written
        print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return RC_REFUSED
    print(f"registered {entry['test']} {entry['test_ids']}: N {entry['n_before']} -> "
          f"{entry['n_after']} ({entry['entry_id']}, {entry['time_local']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
