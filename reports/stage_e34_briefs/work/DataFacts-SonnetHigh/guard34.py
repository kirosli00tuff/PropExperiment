"""DataFacts E.34 data guard: explicit allowlist, real-path comparison, opens.log.

Allowed: the 39 ZL MBP-1 files + manifest.json of Z3_ZL_v_0; the 39 definition files + manifest.json
of Z4_ZM_FUT-ZS_FUT-ZL_FUT; the ohlcv-1m files range=2020-12-01_2021-01-01 .. range=2024-02-01_2024-03-01
(39 each) of ZL_v_0, ZS_v_0, ZM_v_0. Everything else raises GuardRefused.
Record level: check_ts() refuses ts_recv outside [2020-11-30T22:00Z, 2024-03-01T00:00Z).
CLI: python guard34.py dry-check
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
VENDOR = REPO / "data" / "vendor" / "databento" / "GLBX.MDP3"
MBP1_DIR = VENDOR / "mbp-1" / "Z3_ZL_v_0"
DEF_DIR = VENDOR / "definition" / "Z4_ZM_FUT-ZS_FUT-ZL_FUT"
OHLCV = {r: VENDOR / "ohlcv-1m" / f"{r}_v_0" for r in ("ZL", "ZS", "ZM")}
OPENS_LOG = HERE / "opens.log"
PDT = ZoneInfo("America/Vancouver")
NS = 1_000_000_000
SEAL_END_NS = 1_606_773_600 * NS      # 2020-11-30T22:00:00Z
CUTOFF_NS = 1_709_251_200 * NS        # 2024-03-01T00:00:00Z
OHLCV_FIRST, OHLCV_LAST_START = "range=2020-12-01_2021-01-01", "range=2024-02-01_2024-03-01"


class GuardRefused(RuntimeError):
    pass


def _ohlcv_names(root_dir: Path) -> set[str]:
    names = {p.name for p in root_dir.glob("range=*.dbn.zst")}
    keep = {n for n in names
            if n[: len("range=YYYY-MM-DD_YYYY-MM-DD")] >= OHLCV_FIRST
            and n[: len("range=YYYY-MM-DD_YYYY-MM-DD")] <= OHLCV_LAST_START}
    return {str((root_dir / n).resolve()) for n in keep}


def _build() -> frozenset[str]:
    allowed: set[str] = set()
    for d in (MBP1_DIR, DEF_DIR):
        allowed.add(str((d / "manifest.json").resolve()))
        allowed |= {str(p.resolve()) for p in d.glob("range=*.dbn.zst")}
    for d in OHLCV.values():
        allowed |= _ohlcv_names(d)
    if len(allowed) != 2 + 39 + 39 + 3 * 39:
        raise GuardRefused(f"allowlist has {len(allowed)} entries, expected {2 + 39 + 39 + 117}")
    return frozenset(allowed)


ALLOWED = _build()


def check(path: str | Path) -> Path:
    real = Path(path).expanduser().resolve(strict=False)
    if str(real) not in ALLOWED:
        raise GuardRefused(f"REFUSED (not on the DataFacts allowlist): {path}")
    stamp = datetime.now(PDT).strftime("%Y-%m-%d %H:%M:%S %Z")
    with OPENS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp}\t{real}\n")
    return real


def check_ts(ts_recv: np.ndarray, where: str) -> None:
    if len(ts_recv) == 0:
        return
    if int(ts_recv.min()) < SEAL_END_NS or int(ts_recv.max()) >= CUTOFF_NS:
        raise GuardRefused(f"{where}: ts_recv outside [2020-11-30T22:00Z, 2024-03-01T00:00Z)")


def dry_check() -> int:
    sealed = sorted((REPO / "data" / "sealed").glob("SOY_test_v1*"))
    cases = {
        "sealed blob under data/sealed": (sealed[0] if sealed else REPO / "data/sealed/SOY_test_v1/x"),
        "in-window raw ZL ohlcv-1m 2020-11": OHLCV["ZL"] / "range=2020-11-01_2020-12-01.dbn.zst",
        "ZL ohlcv-1m 2024-03": OHLCV["ZL"] / "range=2024-03-01_2024-04-01.dbn.zst",
        "ZS ohlcv-1m 2025": OHLCV["ZS"] / "range=2025-08-01_2025-09-01.dbn.zst",
        "rolls file": VENDOR.parent / "rolls" / "ZL_v_0_2019-05-01_2024-03-01.jsonl",
        "FRED csv": REPO / "reports/stage_e20_briefs/pages/ZL/fred_PSOILUSDM.csv",
        "E.32 derived tsv": REPO / "reports/stage_e32_briefs/seal/derived_unsealed_files.tsv",
        "E.12 ML cache": Path.home() / ".cache" / "propexp_e12" / "x",
        ".env": REPO / ".env",
    }
    ok = True
    for label, p in cases.items():
        try:
            check(p)
            print(f"FAIL  {label}: allowed (should refuse)")
            ok = False
        except GuardRefused as e:
            print(f"OK    {label}: refused")
    first = sorted(MBP1_DIR.glob("range=*.dbn.zst"))[0]
    check(first)
    print(f"OK    positive control: first ZL MBP-1 file allowed ({first.name})")
    print(f"allowlist entries: {len(ALLOWED)}")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["dry-check"]:
        sys.exit(dry_check())
    print(__doc__)
