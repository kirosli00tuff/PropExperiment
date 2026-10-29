"""r2_common.py: shared paths, constants and helpers for the Stage E.32b R2 scripts (DossierWriter, step 3b).

Facts only: nothing here reads market data or any strategy outcome. Constants come from the frozen spec
(reports/stage_e32b_ranking_spec.md, sections 7, 8.2 and 9.2).
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BRIEFS = REPO / "reports" / "stage_e32b_briefs"
WORK = BRIEFS / "work" / "R2"
SPEC_PATH = REPO / "reports" / "stage_e32b_ranking_spec.md"
SPEC_SHA256 = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"

# Inputs (read only)
F5_PATH = BRIEFS / "F5_holding.json"
F4_PATH = BRIEFS / "F4_facts_unmasked.json"
F4_IBKR_PATH = BRIEFS / "F4_venue_ibkr.json"
SR80_PATH = BRIEFS / "work" / "F5" / "SR80.json"
SCORE_PATH = BRIEFS / "score32b_out.json"
R2F_PATH = BRIEFS / "R2_idea_families.json"
R1_PATH = BRIEFS / "R1_closed_lines.json"
DATA_PATH = BRIEFS / "F2_data_access.json"
F2_FIRMS_PATH = BRIEFS / "F2_firms.json"
E16_WINDOWS_PATH = REPO / "reports" / "stage_e16_windows.json"

# Outputs
GROUNDWORK_JSON = WORK / "groundwork.json"
GROUNDWORK_MD = WORK / "groundwork.md"
COMBOS_DETAIL = WORK / "combos_detail.json"
COMBOS_UNRATED = BRIEFS / "R2_combinations_unrated.json"
DOSSIERS_MD = BRIEFS / "R2_dossiers.md"
DOSSIERS_RATING_MD = BRIEFS / "R2_dossiers_for_rating.md"
Q_RATINGS = BRIEFS / "R2_Q_ratings.json"
COMBOS_RATED = BRIEFS / "R2_combinations.json"

# Spec 9.2 and 7
T_DISC = 796
T_TEST = 870
DAYS_PER_YEAR = 252
ENTRY_CAP = 20
NORMAL_FACTOR = 1.596
BAND_H = ("5", "15", "30", "60", "120", "240", "OC")
MONTHS_DISC = 39
MONTHS_TEST = 43
DAYS_PER_MONTH = 30.4375          # mean calendar month, for window lengths in months
WEEKS_PER_YEAR = 365.25 / 7

FIRMS = ("topstep", "lucid", "tradeify", "mffu", "bulenox")
OWN_BROKER = "ibkr"
VENUES = FIRMS + (OWN_BROKER,)


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_spec() -> str:
    got = sha256_file(SPEC_PATH)
    if got != SPEC_SHA256:
        raise SystemExit(f"REFUSED: spec sha256 {got} != frozen {SPEC_SHA256}")
    return got


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check_hash(doc: dict, name: str) -> None:
    h = doc.get("spec_sha256") if isinstance(doc, dict) else None
    if h is not None and h != SPEC_SHA256:
        raise SystemExit(f"REFUSED: {name} spec_sha256 {h} != frozen {SPEC_SHA256}")


def write_json(path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False, allow_nan=False)
        fh.write("\n")
    tmp.replace(path)


def write_text(path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def now_pdt() -> str:
    out = subprocess.run(["date", "+%Y-%m-%d %H:%M:%S %Z"], capture_output=True, text=True,
                         env={"TZ": "America/Vancouver"}, check=True)
    return out.stdout.strip()


def inputs_meta(paths: dict) -> dict:
    return {k: {"path": str(Path(p).relative_to(REPO)), "sha256": sha256_file(p)} for k, p in paths.items()}


def r(x, nd: int = 4):
    """Round a float for reporting (None passes through)."""
    if x is None:
        return None
    if isinstance(x, float) and not math.isfinite(x):
        raise ValueError(f"non-finite number {x}")
    return round(float(x), nd)


def fmt(x, nd: int = 3) -> str:
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return str(x)
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def n_cap(h: str, l_main) -> int:
    """Spec 7: n_cap(h) = min(20, floor(L_main / h)); OC 1 a day."""
    if h == "OC":
        return 1
    return min(ENTRY_CAP, int(math.floor(l_main / int(h))))
