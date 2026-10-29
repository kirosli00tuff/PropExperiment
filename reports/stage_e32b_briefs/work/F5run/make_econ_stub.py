"""Build econ_stub_layer1only.json: a stub econ file so score32b.py can run before econ32b.json exists.

Stage E.32b, C5a F5Runner (Opus 5.5, xhigh), 2026-10-29. Layer 1 (D1-D6 and its gate) does not read the econ file,
so the stub lets the exact Layer 1 be computed now. Every E, L2, S, pair rank and top 15 that score32b.py computes
from this stub is MEANINGLESS and must not be copied anywhere.

For every pair score32b.py requires (work/score/SCHEMA.md section 4: listed_50k true, code not NQ, F3 status owned
or OC1), the blocks primary, E_dir60 and spread1 each get: above_cap {mu_star: true, mu10K: true}; mu_star_mkt,
mu10K_mkt, m_star and m10K null; cost_per_attempt 0; grid_cap 0; sigma60 from F3; "stub": true.

Usage: uv run python make_econ_stub.py  (paths fixed below; prints counts only)
"""
import hashlib
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEFS = os.path.abspath(os.path.join(HERE, "..", ".."))
F3_PATH = os.path.join(BRIEFS, "F3_vol.json")
F4_PATH = os.path.join(BRIEFS, "F4_facts_unmasked.json")
OUT_PATH = os.path.join(HERE, "econ_stub_layer1only.json")
SPEC_SHA = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"
BLOCKS = ("primary", "E_dir60", "spread1")
NQ = "NQ"


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stub_block(sigma60) -> dict:
    return {"mu_star_mkt": None, "mu10K_mkt": None, "above_cap": {"mu_star": True, "mu10K": True},
            "cost_per_attempt": 0, "sigma60": sigma60, "m_star": None, "m10K": None, "grid_cap": 0, "stub": True}


def required_pairs(f3: dict, f4: dict) -> list:
    roots = f3["roots"]
    out = []
    for key, pf in sorted(f4["pairs"].items()):
        code = key.split("|")[1]
        if code == NQ or pf.get("listed_50k") is not True:
            continue
        if (roots.get(code) or {}).get("status") not in ("owned", "OC1"):
            continue
        out.append(key)
    return out


def build(f3: dict, f4: dict, now_pdt: str) -> dict:
    pairs = {}
    for key in required_pairs(f3, f4):
        code = key.split("|")[1]
        s60 = (((f3["roots"][code].get("h") or {}).get("60")) or {}).get("sigma")
        pairs[key] = {b: stub_block(s60) for b in BLOCKS}
    return {
        "spec_sha256": SPEC_SHA,
        "stub": True,
        "STUB_WARNING": ("LAYER 1 ONLY. This is not econ32b.json. Every E, L2, S, pair rank and top 15 computed "
                         "from this file is meaningless and must not be copied anywhere."),
        "generated_pdt": now_pdt,
        "generated_by": "F5Runner-OpusXHigh (Stage E.32b C5a), make_econ_stub.py",
        "inputs": {"F3": {"path": F3_PATH, "sha256": sha256(F3_PATH)},
                   "F4": {"path": F4_PATH, "sha256": sha256(F4_PATH)}},
        "grid": {"stub": True},
        "pairs": pairs,
    }


def main() -> int:
    with open(F3_PATH, encoding="utf-8") as fh:
        f3 = json.load(fh)
    with open(F4_PATH, encoding="utf-8") as fh:
        f4 = json.load(fh)
    now = subprocess.run(["date", "+%Y-%m-%d %H:%M %Z"], capture_output=True, text=True,
                         env={**os.environ, "TZ": "America/Vancouver"}).stdout.strip()
    doc = build(f3, f4, now)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
    n_null = sum(1 for p in doc["pairs"].values() if p["primary"]["sigma60"] is None)
    print(f"wrote {OUT_PATH}: {len(doc['pairs'])} pairs x {len(BLOCKS)} blocks; sigma60 null in {n_null}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
