"""Shared helpers for score32b.py and r3_score.py (Stage E.32b, ScoreCoder).

Exact arithmetic: every input number becomes a fractions.Fraction built from its decimal text (the repr of the JSON
float), so a value written on a band boundary lands on the boundary exactly and goes to the side the spec names
(spec section 3 D1: boundaries to the higher score). Floats appear only in the JSON output.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

SPEC_SHA256 = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"
REPO = Path(__file__).resolve().parents[4]
SPEC_PATH = REPO / "reports" / "stage_e32b_ranking_spec.md"
E28_TABLE = REPO / "reports" / "stage_e28_briefs" / "A3_ranking_table.json"

INF = math.inf
HALF = Fraction(1, 2)

# Spec section 0: the 47 codes in E.28's 8 families.
FAMILIES = {
    "crude": ("MCL", "QM", "CL"),
    "natgas": ("MNG", "QG", "NG"),
    "metals": ("MGC", "GC", "SIL", "SI", "MHG", "HG"),
    "fx": ("M6E", "6E", "M6A", "6A"),
    "crypto": ("MET", "ETH", "MBT", "BTC"),
    "equity": ("M2K", "RTY", "MYM", "YM", "MNQ", "NQ"),
    "rates": ("2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN", "ZB"),
    "grains": ("MZC", "MZS", "MZW", "MZL", "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM"),
}
FAMILY_OF = {c: f for f, cs in FAMILIES.items() for c in cs}
ALL_CODES = tuple(FAMILY_OF)
NQ = "NQ"            # V49: listed as "excluded (V49)", never scored or ranked
BASELINE = "MNQ"     # shown as the baseline (spec 0)
FIRMS = ("topstep", "lucid", "tradeify", "mffu", "bulenox")
FIRM_SORT_NAME = {"topstep": "Topstep", "lucid": "Lucid Trading", "tradeify": "Tradeify",
                  "mffu": "My Funded Futures", "bulenox": "Bulenox"}   # E.28 A3_common.py, for the tie rule

# Codes quoted on the same price of the same underlying (spec 2.4's transfer pairs, plus the pairs whose members are
# both owned or both unowned). Used only where a price cancels: the Sat (i) ADV ratio and "larger-size sibling", the
# leader, and a code without an F3 median close borrowing its same-price sibling's close for the notional (D2 c).
# The rates codes form no group: the micro yields are yield-quoted (spec 2.4) and ZT ZF ZN ZB are different tenors.
SAME_PRICE_GROUPS = (
    ("MCL", "QM", "CL"), ("MNG", "QG", "NG"), ("MGC", "GC"), ("SIL", "SI"), ("MHG", "HG"), ("M6E", "6E"),
    ("M6A", "6A"), ("MET", "ETH"), ("MBT", "BTC"), ("M2K", "RTY"), ("MYM", "YM"), ("MNQ", "NQ"),
    ("MZC", "XC", "ZC"), ("MZS", "XK", "ZS"), ("MZW", "XW", "ZW"), ("MZL", "ZL"), ("MZM", "ZM"),
)
SAME_PRICE_OF = {c: frozenset(g) for g in SAME_PRICE_GROUPS for c in g}


class SpecHashError(RuntimeError):
    """The frozen spec, or an input's recorded spec hash, is not the one this script implements."""


class InputError(ValueError):
    """An input file breaks the data contract (work/score/SCHEMA.md)."""


@dataclass(frozen=True)
class Params:
    """One scoring run. The primary is Params(); each declared variant flips exactly one field (spec 5)."""
    slip: Fraction = HALF            # slippage allowance per round trip, ticks (slip0: 0, slip1: 1.0)
    dispersion: str = "sigma"        # "sigma" or "mad" (m_h in place of sigma_h in D1 and the gate)
    d1_all: bool = False             # D1 over 5, 15, 30, 60, 120, 240 and OC
    e_dir60: bool = False            # E from econ32b.json's E_dir60 block
    oc1_off: bool = False            # no sibling transfer: OC1 codes have unknown F3 statistics
    sat_deduction: int = 2           # sat1: 1
    d2_own: bool = False             # satellites use their own D2 a, b, c
    l1min2: bool = False             # extra Layer 1 gate L1 >= 2.00
    spread1: bool = False            # S = 1 for every code (D1, gate, L) and econ32b.json's spread1 block

    def econ_block(self) -> str:
        if self.e_dir60 and self.spread1:
            raise InputError("e_dir60 and spread1 both set: not a declared variant")
        return "spread1" if self.spread1 else ("E_dir60" if self.e_dir60 else "primary")


DECLARED_VARIANTS = {
    "slip0": {"slip": Fraction(0)}, "slip1": {"slip": Fraction(1)}, "mad": {"dispersion": "mad"},
    "D1_all": {"d1_all": True}, "E_dir60": {"e_dir60": True}, "OC1_off": {"oc1_off": True},
    "sat1": {"sat_deduction": 1}, "D2_own": {"d2_own": True}, "L1min2": {"l1min2": True},
    "spread1": {"spread1": True},
}


def params_from(overrides: dict) -> Params:
    """Params from a JSON-style dict (a lead-ruling variant); numbers given as text or numbers."""
    known = set(Params.__dataclass_fields__)
    bad = set(overrides) - known
    if bad:
        raise InputError(f"unknown params {sorted(bad)}; allowed {sorted(known)}")
    vals = dict(overrides)
    if "slip" in vals:
        vals["slip"] = q(vals["slip"], "params.slip")
    if "sat_deduction" in vals:
        vals["sat_deduction"] = int(vals["sat_deduction"])
    if vals.get("dispersion", "sigma") not in ("sigma", "mad"):
        raise InputError("params.dispersion must be sigma or mad")
    p = Params(**vals)
    p.econ_block()
    return p


def file_sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_spec(path=SPEC_PATH) -> str:
    """Refuse to run unless the frozen spec's sha256 is the recorded one."""
    p = Path(path)
    if not p.is_file():
        raise SpecHashError(f"spec not found: {p}; refusing to run")
    got = file_sha256(p)
    if got != SPEC_SHA256:
        raise SpecHashError(f"spec sha256 {got} != frozen {SPEC_SHA256}; refusing to run")
    return got


def check_doc_hash(doc, name: str) -> None:
    """An input that records a spec hash must record the frozen one."""
    h = doc.get("spec_sha256") if isinstance(doc, dict) else None
    if h is not None and h != SPEC_SHA256:
        raise SpecHashError(f"{name}: spec_sha256 {h} != frozen {SPEC_SHA256}; refusing to run")


def q(x, what: str = "") -> Fraction | None:
    """Exact Fraction from a JSON number (via its decimal repr) or decimal text; None stays None."""
    if x is None:
        return None
    if isinstance(x, bool):
        raise InputError(f"{what}: boolean where a number is required")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, float):
        if not math.isfinite(x):
            raise InputError(f"{what}: non-finite number {x}")
        return Fraction(repr(x))
    if isinstance(x, str):
        try:
            return Fraction(x.strip())
        except (ValueError, ZeroDivisionError) as exc:
            raise InputError(f"{what}: not a number: {x!r}") from exc
    raise InputError(f"{what}: not a number: {x!r}")


def positive(x, what: str = "") -> Fraction | None:
    """q(x), which must be > 0 when present (sigma, multipliers, prices)."""
    v = q(x, what)
    if v is not None and v <= 0:
        raise InputError(f"{what}: must be > 0, got {x}")
    return v


def nonneg(x, what: str = "") -> Fraction | None:
    v = q(x, what)
    if v is not None and v < 0:
        raise InputError(f"{what}: must be >= 0, got {x}")
    return v


def band_le(x, steps) -> int:
    """First score whose limit x does not exceed (x <= limit: the boundary takes the higher score); else 0."""
    for limit, score in steps:
        if x <= limit:
            return score
    return 0


def band_ge(x, steps) -> int:
    """First score whose floor x reaches (x >= floor: the boundary takes the higher score); else 0."""
    for floor, score in steps:
        if x >= floor:
            return score
    return 0


def round2(x) -> Fraction:
    """Half-up rounding to 2 decimals, exact (spec 5 and 8.3 ties)."""
    return Fraction(math.floor(Fraction(x) * 100 + HALF), 100)


def s_fn(x: Fraction, x0: Fraction) -> Fraction:
    """s(x; x0) = 4 max(0, 1 - x / x0) (spec 4)."""
    return 4 * max(Fraction(0), 1 - x / x0)


def fmt_num(x) -> str:
    """Short text for S and the slippage in the gate string (1, 0.5, 1.25)."""
    return format(float(x), "g")


def fmt_two(x, y) -> tuple[str, str]:
    """x and y at 2 decimals, more when the rounding would hide their order."""
    a, b = "", ""
    for nd in (2, 4, 6, 8):
        a, b = f"{float(x):.{nd}f}", f"{float(y):.{nd}f}"
        if a != b or x == y:
            break
    return a, b


def to_jsonable(o):
    """Fractions to floats, inf to the string "inf", tuples and sets to lists; recursive."""
    if isinstance(o, Fraction):
        return float(o)
    if isinstance(o, float):
        return "inf" if math.isinf(o) else o
    if isinstance(o, dict):
        return {str(k): to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, (set, frozenset)):
        return sorted(to_jsonable(v) for v in o)
    return o


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(to_jsonable(obj), fh, indent=1, sort_keys=False)
        fh.write("\n")
    tmp.replace(path)


def apply_patches(docs: dict, patches: list) -> dict:
    """A deep copy of docs with each patch {"file", "path": [...], "value"} applied (lead-ruling variants).
    Every container on the path but the last key must exist."""
    out = copy.deepcopy(docs)
    for i, p in enumerate(patches or []):
        name, path = p.get("file"), p.get("path")
        if name not in out or not isinstance(path, list) or not path or "value" not in p:
            raise InputError(f"patch {i}: needs file in {sorted(out)}, a non-empty path list and a value")
        node = out[name]
        try:
            for k in path[:-1]:
                node = node[int(k)] if isinstance(node, list) else node[k]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise InputError(f"patch {i}: path {path} not found in {name}") from exc
        last = path[-1]
        if isinstance(node, list):
            node[int(last)] = copy.deepcopy(p["value"])
        elif isinstance(node, dict):
            node[last] = copy.deepcopy(p["value"])
        else:
            raise InputError(f"patch {i}: path {path} does not end in a container")
    return out


def now_pdt() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M:%S %Z")


def blind_rated(rating, rule, allowed, cap=None, what: str = ""):
    """(value, note) from a blind rating R = {"value", "unknown", "reason"[, "unverified"]}.

    A missing rating, unknown = true or value = null takes the criterion's unknown rule `rule`, noted "(u)". With
    unverified = true (the rating rests only on an abstract or a snippet), `cap` applies spec section 1's evidence cap.
    """
    if not isinstance(rating, dict):
        return Fraction(rule), f"{what}: rating missing -> {fmt_num(rule)} (u)"
    if rating.get("unknown") is True or rating.get("value") is None:
        return Fraction(rule), f"{what}: unknown -> {fmt_num(rule)} (u)"
    v = q(rating["value"], what)
    if v not in {Fraction(a) for a in allowed}:
        raise InputError(f"{what}: value {rating['value']} not in {sorted(float(a) for a in allowed)}")
    if cap is not None and rating.get("unverified") is True:
        capped = cap(v)
        if capped != v:
            return capped, f"{what}: {fmt_num(v)} capped to {fmt_num(capped)} (abstract or snippet only, spec 1)"
    return v, None


def cap_extreme_0_4(v: Fraction) -> Fraction:
    """Spec 1 evidence cap for D6 and Q2: at most 2 from above, at least 1 from below."""
    if v >= 3:
        return Fraction(2)
    if v == 0:
        return Fraction(1)
    return v


def cap_s12(v: Fraction) -> Fraction:
    """Spec 1 evidence cap for D3 s1 and s2: 2 becomes 1."""
    return Fraction(1) if v == 2 else v
