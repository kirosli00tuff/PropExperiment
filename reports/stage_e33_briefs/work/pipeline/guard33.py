"""E.33 data guard (protocol P1.2; brief_DataCoder deliverable 1).

Every E.33 real-data read goes through this module. It refuses, by raising ``GuardRefused``:

- any path under data/sealed/SOY_test_v1 (both spellings, symlinks resolved) and any original
  location of a sealed file listed in docs/soy_test/SOY_TEST_MANIFEST.json;
- any ZM, ZS or ZL data dated 2017-05-01..2020-11-30 (the soy test window), by requested trade
  date and by any date span readable from a path component (file or folder name);
- any date on or after 2024-03-01;
- any path listed in reports/stage_e32_briefs/seal/derived_unsealed_files.tsv (or a folder that
  holds one);
- anything under reports/stage_e31_briefs/work/pilot/runs/ (E.31's measured outputs);
- any other file: the allowlist is exactly the 156 discovery files of manifest 09396842... (plus
  the four identical manifest.json copies and their four folders), E.31's ZM MBO per-day split
  store derived/e31/Z1, the E.33 DERIVED tree derived/e33, and the two USDA release calendars of
  P3.6 (reference data, sha256-pinned by the protocol).

API: ``check_path(path)``, ``check_date(D)``, ``check_request(path, first_date, last_date)``,
``check_records(ts_recv, ts_event, where)``. CLI: ``python guard33.py dry-check``.

Dates: a trade date D is allowed only inside the discovery universe 2020-12-01..2024-02-29
(dates before 2020-12-01 outside the test window are refused too: no allowed file holds them;
READING DG-2). Record level: ts_recv must be >= 2020-11-30T22:00:00Z (the seal window's end) and
both ts_recv and ts_event must be < 2024-03-01T00:00:00Z (READING DG-1).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import UTC, date, datetime, timedelta
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PILOT = REPO / "reports" / "stage_e31_briefs" / "work" / "pilot"
for _p in (str(REPO), str(PILOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

NS = 1_000_000_000
DISCOVERY_MANIFEST_SHA256 = "09396842c4fd5d742c166e5b6ca1327c5eeebfed9b112952b84d15f254c23261"
VENDOR = REPO / "data" / "vendor" / "databento" / "GLBX.MDP3"
DISCOVERY_DIRS = {
    "Z1": VENDOR / "mbo" / "Z1_ZM_v_0-ZM_v_1",
    "Z2": VENDOR / "mbp-1" / "Z2_ZS_v_0",
    "Z3": VENDOR / "mbp-1" / "Z3_ZL_v_0",
    "Z4": VENDOR / "definition" / "Z4_ZM_FUT-ZS_FUT-ZL_FUT",
}
N_DISCOVERY_FILES = 156
LARGE = Path("/mnt/large-storage/market_data/PropExperiment")
E31_Z1 = LARGE / "derived" / "e31" / "Z1"
DERIVED = LARGE / "derived" / "e33"
SEALED = REPO / "data" / "sealed" / "SOY_test_v1"
SEAL_MANIFEST = REPO / "docs" / "soy_test" / "SOY_TEST_MANIFEST.json"
UNSEALED_TSV = REPO / "reports" / "stage_e32_briefs" / "seal" / "derived_unsealed_files.tsv"
E31_RUNS = PILOT / "runs"
RESEARCH31 = REPO / "reports" / "stage_e31_briefs" / "research"
REFERENCE_FILES = {  # P3.6 rule 3: the release calendars, read as reference data
    RESEARCH31 / "usda_releases.csv":
        "0743c0e27ac963d2d47a691a8b644f10208cb64b8f629a09ac788d829ad45119",
    RESEARCH31 / "usda_releases_ext.csv":
        "55df3b14f4565f607294e313c0b8fc26f3652df1d4de02a732861b47ba9feb88",
}

TEST_FIRST, TEST_LAST = date(2017, 5, 1), date(2020, 11, 30)  # P1.2, seal manifest
DISC_FIRST, DISC_LAST = date(2020, 12, 1), date(2024, 2, 29)  # P1.4
CUTOFF_DATE = date(2024, 3, 1)
CUTOFF_NS = 1_709_251_200 * NS  # 2024-03-01T00:00:00Z
SEAL_START_NS = 1_493_586_000 * NS  # 2017-04-30T21:00:00Z (seal manifest window_utc[0])
SEAL_END_NS = 1_606_773_600 * NS  # 2020-11-30T22:00:00Z (seal manifest window_utc[1])


class GuardRefused(RuntimeError):
    """A path, date or record E.33 may not read (P1.2)."""


def _refuse(kind: str, detail: str) -> GuardRefused:
    return GuardRefused(f"REFUSED (P1.2 {kind}): {detail}")


# ------------------------------------------------------------------ spellings ----
def _spellings(path: str | Path) -> tuple[Path, Path]:
    """The absolute path as written (no symlink resolution) and fully resolved."""
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    absolute = Path(*_normalise(p.parts))
    return absolute, p.resolve(strict=False)


def _normalise(parts: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for part in parts:
        if part == "..":
            if len(out) > 1:
                out.pop()
        elif part != ".":
            out.append(part)
    return out


def _under(p: Path, root: Path) -> bool:
    return p == root or root in p.parents


def _roots(root: Path) -> tuple[Path, Path]:
    return _spellings(root)


# ------------------------------------------------------------------ lists ----
@lru_cache(maxsize=1)
def _seal() -> dict:
    data = json.loads(SEAL_MANIFEST.read_text(encoding="utf-8"))
    window = [datetime.fromisoformat(w) for w in data["window_utc"]]
    if (int(window[0].timestamp()) * NS, int(window[1].timestamp()) * NS) != \
            (SEAL_START_NS, SEAL_END_NS):
        raise GuardRefused(f"seal manifest window {data['window_utc']} differs from the guard's")
    if (data["first_trade_date"], data["last_trade_date"]) != \
            (TEST_FIRST.isoformat(), TEST_LAST.isoformat()):
        raise GuardRefused("seal manifest trade-date range differs from the guard's")
    originals: set[Path] = set()
    for rec in data.get("raw_files", []):
        if rec.get("original_path"):
            originals.update(_spellings(rec["original_path"]))
        if rec.get("original_relpath"):
            originals.update(_spellings(REPO / rec["original_relpath"]))
    return {"originals": frozenset(originals),
            "first_sealed_relpath": (data.get("raw_files") or [{}])[0].get("sealed_relpath")}


@lru_cache(maxsize=1)
def _unsealed() -> frozenset[Path]:
    out: set[Path] = set()
    lines = UNSEALED_TSV.read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        raw = line.split("\t")[0].strip()
        p = Path(raw) if Path(raw).is_absolute() else REPO / raw
        out.update(_spellings(p))
    return frozenset(out)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=1)
def discovery_manifest() -> dict:
    """The discovery manifest (identical copy in each of the four folders), sha256-checked."""
    texts = {}
    for series, folder in DISCOVERY_DIRS.items():
        path = folder / "manifest.json"
        digest = _sha256(path)
        if digest != DISCOVERY_MANIFEST_SHA256:
            raise GuardRefused(f"{path}: sha256 {digest} is not the discovery manifest "
                               f"{DISCOVERY_MANIFEST_SHA256}")
        texts[series] = path.read_text(encoding="utf-8")
    data = json.loads(texts["Z1"])
    if len(data["files"]) != N_DISCOVERY_FILES:
        raise GuardRefused(f"discovery manifest lists {len(data['files'])} files, not 156")
    return data


@lru_cache(maxsize=1)
def _allowed_files() -> frozenset[Path]:
    out: set[Path] = set()
    for f in discovery_manifest()["files"]:
        out.update(_spellings(f["path"]))
    for folder in DISCOVERY_DIRS.values():
        out.update(_spellings(folder / "manifest.json"))
        out.update(_spellings(folder))
    for ref in REFERENCE_FILES:
        out.update(_spellings(ref))
    return frozenset(out)


# ------------------------------------------------------------------ dates in names ----
_STAMP = r"(\d{4}-\d{2}-\d{2})(?:T(\d{2})(\d{2})(\d{2})Z)?"
_RANGE = re.compile(rf"range={_STAMP}_{_STAMP}")  # end exclusive (Databento request range)
_BATCH = re.compile(r"(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})")  # end inclusive
_DAY = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
_MONTH = re.compile(r"(?<!\d)(\d{4})-(\d{2})(?![\d-])")


def _instant(day: str, hh: str | None, mm: str | None, ss: str | None) -> int:
    d = date.fromisoformat(day)
    moment = datetime(d.year, d.month, d.day, int(hh or 0), int(mm or 0), int(ss or 0),
                      tzinfo=UTC)
    return int(moment.timestamp()) * NS


def _day_ns(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp()) * NS


def _check_span_ns(start_ns: int, end_ns: int, where: str) -> None:
    """A UTC span [start, end) read from a name: refuse if it meets the seal window, reaches
    2024-03-01 or starts before the seal window's end without being wholly before it."""
    if start_ns < SEAL_END_NS and end_ns > SEAL_START_NS:
        raise _refuse("soy test window", f"{where}: its date span meets the sealed window "
                      "2017-04-30T21:00Z..2020-11-30T22:00Z (trade dates 2017-05-01..2020-11-30)")
    if end_ns > CUTOFF_NS:
        raise _refuse("on or after 2024-03-01", f"{where}: its date span reaches past "
                      "2024-03-01T00:00:00Z")
    if start_ns < SEAL_START_NS:
        raise _refuse("outside the discovery span", f"{where}: its date span lies before "
                      "2020-12-01 (no allowed file holds it)")


def _check_name(component: str, where: str) -> None:
    rest = component
    for m in _RANGE.finditer(component):
        start = _instant(m.group(1), m.group(2), m.group(3), m.group(4))
        end = _instant(m.group(5), m.group(6), m.group(7), m.group(8))
        _check_span_ns(start, end, where)
        rest = rest.replace(m.group(0), " ")
    for m in _BATCH.finditer(rest):
        first, last = date.fromisoformat(m.group(1)), date.fromisoformat(m.group(2))
        _check_date_span(first, last, where)
        rest = rest.replace(m.group(0), " ")
    for m in _DAY.finditer(rest):
        try:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        check_date(d, where=where)
    rest = _DAY.sub(" ", rest)
    for m in _MONTH.finditer(rest):
        year, month = int(m.group(1)), int(m.group(2))
        if not 1 <= month <= 12 or year < 1990:
            continue
        first = date(year, month, 1)
        last = (first.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        _check_date_span(first, last, where)


def _check_date_span(first: date, last: date, where: str) -> None:
    if first > last:
        raise _refuse("bad request", f"{where}: first date {first} is after last date {last}")
    if first <= TEST_LAST and last >= TEST_FIRST:
        raise _refuse("soy test window", f"{where}: dates {first}..{last} meet the soy test "
                      "window 2017-05-01..2020-11-30")
    check_date(first, where=where)
    check_date(last, where=where)


# ------------------------------------------------------------------ API ----
def _as_date(d: date | datetime | str | np.datetime64) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, np.datetime64):
        return date.fromisoformat(str(d.astype("datetime64[D]")))
    return date.fromisoformat(str(d)[:10])


def check_date(d: date | datetime | str, where: str = "") -> date:
    """Refuse a trade date in the soy test window (2017-05-01..2020-11-30), on or after
    2024-03-01, or otherwise outside the discovery universe 2020-12-01..2024-02-29."""
    day = _as_date(d)
    label = f"{where}: " if where else ""
    if TEST_FIRST <= day <= TEST_LAST:
        raise _refuse("soy test window", f"{label}date {day} lies in the sealed soy test window "
                      "2017-05-01..2020-11-30 (ZM, ZS, ZL)")
    if day >= CUTOFF_DATE:
        raise _refuse("on or after 2024-03-01", f"{label}date {day} is on or after 2024-03-01")
    if day < DISC_FIRST:
        raise _refuse("outside the discovery span", f"{label}date {day} is before 2020-12-01 "
                      "(no allowed file holds it)")
    return day


def check_path(path: str | Path) -> Path:
    """Refuse every path class of P1.2; return the resolved path when allowed."""
    absolute, resolved = _spellings(path)
    where = str(path)
    seal = _seal()
    for root in _roots(SEALED):
        if _under(absolute, root) or _under(resolved, root):
            raise _refuse("sealed soy test data", f"{where} lies under data/sealed/SOY_test_v1")
    if absolute in seal["originals"] or resolved in seal["originals"]:
        raise _refuse("sealed soy test data", f"{where} is the original location of a sealed "
                      "file (SOY_TEST_MANIFEST.json raw_files)")
    for root in _roots(E31_RUNS):
        if _under(absolute, root) or _under(resolved, root):
            raise _refuse("E.31 measured outputs", f"{where} lies under "
                          "reports/stage_e31_briefs/work/pilot/runs/")
    unsealed = _unsealed()
    if absolute in unsealed or resolved in unsealed or any(
            _under(u, absolute) or _under(u, resolved) for u in unsealed):
        raise _refuse("derived_unsealed_files.tsv", f"{where} is (or holds) a file listed in "
                      "reports/stage_e32_briefs/seal/derived_unsealed_files.tsv")
    for spelling in {absolute, resolved}:
        for part in spelling.parts:
            _check_name(part, where)
    if absolute in _allowed_files() or resolved in _allowed_files():
        return resolved
    for root in (*_roots(E31_Z1), *_roots(DERIVED)):
        if _under(absolute, root) or _under(resolved, root):
            return resolved
    raise _refuse("not on the E.33 allowlist", f"{where} is not one of the 156 discovery "
                  "files, E.31's derived/e31/Z1 store, the E.33 DERIVED tree derived/e33 or the "
                  "P3.6 release calendars (any other root's market data is refused)")


def check_request(path: str | Path, first_date: date | str, last_date: date | str) -> Path:
    """check_path plus every trade date in [first_date, last_date]."""
    resolved = check_path(path)
    _check_date_span(_as_date(first_date), _as_date(last_date), str(path))
    return resolved


def check_records(ts_recv: np.ndarray, ts_event: np.ndarray | None, where: str) -> None:
    """Record level: ts_recv inside [2020-11-30T22:00Z, 2024-03-01T00:00Z) and ts_event before
    2024-03-01T00:00Z (READING DG-1: snapshot records carry the resting order's original
    ts_event, which may precede the window; their ts_recv is the owned capture time)."""
    if len(ts_recv) == 0:
        return
    lo, hi = int(np.min(ts_recv)), int(np.max(ts_recv))
    if lo < SEAL_END_NS:
        raise _refuse("soy test window", f"{where}: a record has ts_recv before "
                      "2020-11-30T22:00:00Z (the sealed window's end)")
    if hi >= CUTOFF_NS or (ts_event is not None and len(ts_event)
                           and int(np.max(ts_event)) >= CUTOFF_NS):
        raise _refuse("on or after 2024-03-01", f"{where}: a record is dated on or after "
                      "2024-03-01T00:00:00Z")


def check_reference(path: str | Path) -> Path:
    """check_path plus the protocol's sha256 pin for the P3.6 release calendars."""
    resolved = check_path(path)
    for ref, digest in REFERENCE_FILES.items():
        if resolved == ref.resolve():
            found = _sha256(resolved)
            if found != digest:
                raise _refuse("reference data", f"{path}: sha256 {found} != protocol {digest}")
            return resolved
    raise _refuse("reference data", f"{path} is not a pinned P3.6 release calendar")


# ------------------------------------------------------------------ CLI ----
def dry_check() -> int:
    seal = _seal()
    sealed_rel = seal["first_sealed_relpath"] or "ZM_mbo_2019-03.dbn.zst.sealed"
    trials = [
        ("sealed test-window path", lambda: check_path(SEALED / sealed_rel)),
        ("test-window date 2019-03-05", lambda: check_date("2019-03-05")),
        ("date 2024-03-01", lambda: check_date("2024-03-01")),
        ("E.31 runs/ path", lambda: check_path(E31_RUNS / "measure31")),
    ]
    refused = 0
    for name, call in trials:
        try:
            call()
        except GuardRefused as exc:
            refused += 1
            print(f"[{name}] {exc}")
        else:
            print(f"[{name}] NOT REFUSED")
    print(f"dry-check: {refused} of {len(trials)} refused")
    return 0 if refused == len(trials) else 1


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args != ["dry-check"]:
        print("usage: guard33.py dry-check")
        return 2
    return dry_check()


if __name__ == "__main__":
    raise SystemExit(main())
