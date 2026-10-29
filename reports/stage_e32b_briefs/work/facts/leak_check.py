"""Leak check of the masked sheets: every universe code (case-sensitive, whole token), product name, firm name and
platform name (case-insensitive), "http", "www", ".com", "reports/", ".json", ".md" and every E.28 label. Prints the
count per pattern with hits and the total; exit 1 if any hit."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mask_vocab as V  # noqa: E402
from build_f4 import B, E28, FAMILY_OF, load  # noqa: E402


def patterns() -> list[tuple[str, re.Pattern]]:
    pats = []
    for c in FAMILY_OF:
        pats.append((f"code {c}", re.compile(r"(?<![A-Za-z0-9_])" + re.escape(c) + r"(?:[FGHJKMNQUVXZ]\d{1,2})?(?![A-Za-z0-9_])")))
    for n in V.PRODUCT_NAMES:
        pats.append((f"name {n}", re.compile(re.escape(n), re.I)))
    for f, names in V.FIRM_NAMES.items():
        for n in names + [f]:
            pats.append((f"firm {n}", re.compile(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])", re.I)))
    plat = set(V.PLATFORMS) | set(load(E28 / "A3_mask_key.json")["platforms"].values())
    for p in sorted(plat):
        pats.append((f"platform {p}", re.compile(r"(?<![A-Za-z])" + re.escape(p) + r"(?![A-Za-z])", re.I)))
    for k, n in load(E28 / "A2_platforms.json").items():
        if not k.startswith("_"):
            for part in re.split(r"[_]", k):
                if len(part) >= 4 and part not in ("engine", "latency", "canada", "tax", "sim"):
                    pats.append((f"platform-key {part}", re.compile(r"(?<![A-Za-z])" + re.escape(part)
                                                                    + r"(?![A-Za-z])", re.I)))
    for lp in V.LITIGATION_LEAK:
        pats.append((f"litigation {lp}", re.compile(lp, re.I)))
    for lit in ("http", "www", ".com", "reports/", ".json", ".md"):
        pats.append((f"literal {lit}", re.compile(re.escape(lit), re.I)))
    key = load(E28 / "A3_mask_key.json")
    for grp in ("contracts", "firms", "platforms", "other_products"):
        for lab in key[grp]:
            pats.append((f"E28 label {lab}", re.compile(r"(?<![A-Za-z0-9])" + re.escape(lab) + r"(?![0-9])")))
    for oc in key["other_products"].values():
        if len(oc) >= 2 and oc not in ("US", "GE", "LE", "HE", "BIT", "ON"):
            pats.append((f"other code {oc}", re.compile(r"(?<![A-Za-z0-9_])" + re.escape(oc) + r"(?![A-Za-z0-9_])")))
    return pats


def strings(x):
    if isinstance(x, dict):
        for k, v in x.items():
            yield str(k)
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)
    elif x is not None:
        yield str(x)


def main() -> int:
    total = 0
    pats = patterns()
    for name in ("F4_masked_contracts.json", "F4_masked_firms.json"):
        texts = list(strings(load(B / name)))
        hits = {}
        for label, r in pats:
            n = sum(len(r.findall(t)) for t in texts)
            if n:
                hits[label] = n
        total += sum(hits.values())
        print(f"{name}: {len(pats)} patterns, {sum(hits.values())} hits")
        for k, v in sorted(hits.items(), key=lambda x: -x[1])[:60]:
            ex = next((t for t in texts if dict(pats)[k].search(t)), "")
            m = dict(pats)[k].search(ex)
            print(f"   {k}: {v}  e.g. ...{ex[max(0, m.start()-60):m.end()+40]!r}")
    print("TOTAL HITS", total)
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
