"""Patch the FINAL masked sheets in place (lead follow-up after F4_audit.md B1, S2, S3). Keeps every existing
contract, firm, pair and item label; mask_build.py is not run. Writes F4_masked_contracts.json, F4_masked_firms.json,
F4_mask_key.json and a patch log. Refuses if the inputs are not the F4_masks_FINAL.txt set or if FINAL2 exists."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mask_vocab as V  # noqa: E402

B = HERE.parents[1]
FILES = ("F4_masked_contracts.json", "F4_masked_firms.json", "F4_mask_key.json")
LOG: list[str] = []


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_inputs() -> None:
    if (B / "F4_masks_FINAL2.txt").exists():
        raise SystemExit("refused: F4_masks_FINAL2.txt exists (patch already applied)")
    final = (B / "F4_masks_FINAL.txt").read_text().split()
    want = dict(zip(final[0:6:2], final[1:6:2]))
    for f in FILES:
        if sha(B / f) != want[f]:
            raise SystemExit(f"refused: {f} is not the F4_masks_FINAL.txt version")


# ---------------------------------------------------------------- B1: Lucid plan names in the firm sheet
LUCID_SUBS = [  # applied in order, case-sensitive, substring (no word boundary needed: names are glued)
    ("LucidBLACK", "plan P5"), ("LucidDaily", "plan P4"), ("LucidMaxx", "plan P6"), ("LucidLive", "live stage"),
    ("new Live structure", "new live-stage structure"), ("Daily Trading", "plan P4"),
    (r"(?<![A-Za-z])Flex(?![A-Za-z])", "plan P2"), (r"(?<![A-Za-z])Pro(?![A-Za-z])", "plan P1"),
    (r"(?<![A-Za-z])Direct(?![A-Za-z])", "plan P3"),
]
PLAN_KEY = {"lucid": {"plan P1": "LucidPro", "plan P2": "LucidFlex", "plan P3": "LucidDirect",
                      "plan P4": "LucidDaily (the 'Daily plan')", "plan P5": "LucidBLACK (legacy)",
                      "plan P6": "LucidMaxx", "live stage": "LucidLive"}}


# Further plan-name leaks found by leak_check_v2 (substring) in other firms' sheets; per firm, in order.
OTHER_FIRM_SUBS = {
    "topstep": [("funded_xfa", "funded_stage"), ("live_lfa_api", "live_stage_api"), ("xfa_50k", "funded_50k"),
                (r"(?i)live funded accounts?", "live-stage account(s)"),
                (r"(?<![A-Za-z])Pro(?![A-Za-z])", "plan P2")],
    "tradeify": [(r"(?i)live funded accounts?", "live-stage account(s)")],
    "mffu": [(r"(?i)Pro sim funded", "plan P3 sim funded"), (r"(?<![A-Za-z])Pro(?![A-Za-z])", "plan P3"),
             (r"(?<![A-Za-z])Flex(?![A-Za-z])", "plan P5")],
}
PLAN_KEY_EXTRA = {"topstep": {"plan P2": "'Pro' (the third column of the 50K caps table: Combine/XFA/Pro)"},
                  "mffu": {"plan P3": "Pro (Pro Sim Funded)", "plan P5": "Flex"}}


def patch_other_firms(firms: dict, key: dict) -> dict:
    out = dict(firms)
    for firm, subs in OTHER_FIRM_SUBS.items():
        lab = next(l for l, f in key["firms"].items() if f == firm)
        n = {"hits": 0}

        def fn(s: str, subs=subs, n=n) -> str:
            for pat, rep in subs:
                s, k = re.subn(pat, rep, s)
                n["hits"] += k
            return s

        out["firms"] = {l: (walk_sub(v, fn) if l == lab else v) for l, v in out["firms"].items()}
        out["pairs"] = {p: (walk_sub(v, fn) if p.startswith(lab + "|") else v) for p, v in out["pairs"].items()}
        LOG.append(f"B1-extension: {n['hits']} substitutions in firm {lab}")
    return out


def walk_sub(x, fn):
    if isinstance(x, dict):
        return {k: walk_sub(v, fn) for k, v in x.items()}
    if isinstance(x, list):
        return [walk_sub(v, fn) for v in x]
    if isinstance(x, str):
        return fn(x)
    return x


def patch_firms(firms: dict, key: dict) -> dict:
    lab = next(l for l, f in key["firms"].items() if f == "lucid")
    n = {"hits": 0}

    def fn(s: str) -> str:
        for pat, rep in LUCID_SUBS:
            s, k = re.subn(pat, rep, s)
            n["hits"] += k
        rest = re.subn(r"Lucid", lab, s)
        n["hits"] += rest[1]
        return rest[0]

    out = dict(firms)
    out["firms"] = {l: (walk_sub(v, fn) if l == lab else v) for l, v in firms["firms"].items()}
    out["pairs"] = {p: (walk_sub(v, fn) if p.startswith(lab + "|") else v) for p, v in firms["pairs"].items()}
    LOG.append(f"B1: {n['hits']} substitutions in firm {lab} and its pairs")
    return out


# ---------------------------------------------------------------- S2: the IIP item per code
NAMED = {"CL", "QM", "QG", "NG", "GC", "SI", "HG", "MGC", "SIL"}
IIP_ROW = {
    "6E": "[size class] Foreign Exchange – Futures* (excluding FX Link) $0.54",
    "6A": "[size class] Foreign Exchange – Futures* (excluding FX Link) $0.54",
    "M6E": "[size class] Foreign Exchange Contracts $0.15", "M6A": "[size class] Foreign Exchange Contracts $0.15",
    "NQ": "[size class] Equity Index – Futures* (Outrights & Spreads excluding Dividend Index Futures) $0.75",
    "RTY": "[size class] Equity Index – Futures* (Outrights & Spreads excluding Dividend Index Futures) $0.75",
    "MNQ": "[size class] Equity Index – Futures $0.18", "M2K": "[size class] Equity Index – Futures $0.18",
    "MYM": "[size class] Dow Futures $0.18", "YM": "[size class] Dow/DJ U.S. Real Estate $0.75",
    **{c: "[size class] Agricultural Futures Contracts1 $1.11" for c in ("ZC", "ZS", "ZW", "ZL", "ZM")},
    **{c: "[size class] Agricultural Contracts $0.90" for c in ("XC", "XK", "XW")},
    **{c: "[size class] Treasury Yield Futures $0.21" for c in ("2YY", "5YY", "10Y", "30Y")},
    **{c: "U.S. Treasury Futures $0.54" for c in ("ZT", "ZF", "ZN", "ZB")},
    "NG": "[product name] ({L})1 $0.90", "CL": "[product name] ({L})1 $0.90", "QM": "[product name] ({L}) $0.88",
    "QG": "[product name] ({L}) $0.45", "GC": "Core Metal ({L}, [another product], [another product])1 $1.00",
    "SI": "Core Metal ([another product], {L}, [another product])1 $1.00",
    "HG": "Core Metal ([another product], [another product], {L})1 $1.00", "MGC": "[product name] ({L})1 $0.20",
    "SIL": "[product name] ({L}) $0.40",
}
IIP_TEXT = (
    "The purpose of this Program is to incentivize proprietary trading firms located outside North America to trade "
    "the products listed below. The resulting increase in liquidity in the products listed below benefits all "
    "participant segments in the market. | Only proprietary trading firms located outside of North America and "
    "traders located outside of North America are eligible. | For continued eligibility and incentive "
    "qualification, IIP participants must maintain a combined average daily volume (\"ADV\") in the Products of 250 "
    "contracts (sides) measured over a given calendar quarter. [size class] Equity Index products will be excluded "
    "from this ADV requirement. | 1. Fee Discounts: Participants will be eligible to receive fee discounts for the "
    "Products in accordance with the following tables | 2. CME Products Progressive Volume Discount Incentives: "
    "Subject to the restrictions set forth in #3 below, participants in the Program that maintain a monthly an ADV of "
    "5,000 combined contract sides traded in the respective CME Products denoted above are eligible to receive "
    "progressive volume fee discounts in those Products | Start date is December 16, 2011. End date is January 31, "
    "2025 January 31, 2026, or the date on which the Exchanges determine to modify, extend, or terminate the Program.")
IIP_DETAIL = (
    "Fee-discount program (IIP all-in fees per side, CME Globex) for proprietary trading firms and traders located "
    "outside North America, with a combined volume floor; the filing states no quoting, two-sided-market or "
    "time-in-market obligation. The quote gives this contract's row of the fee table, then the program's purpose, "
    "eligibility, volume requirement, discount types and term verbatim. Term: start 2011-12-16; end 2026-01-31 or as "
    "the Exchanges modify; an extension past 2026-01-31 was not found.")


def patch_iip(contracts: dict, key: dict) -> int:
    lab_of = {c: l for l, c in key["contracts"].items()}
    n = 0
    for mid, meta in key["items"].items():
        if meta["source_item"] != "RATES-11":
            continue
        code = meta["for"]
        sheet = contracts["contracts"][lab_of[code]]
        for it in sheet["D2b_programs"]:
            if it["id"] != mid:
                continue
            rel = "this contract" if code in NAMED else "the product group"
            it["applies_to"] = rel
            it["quote"] = "Fee table row: " + IIP_ROW[code].replace("{L}", lab_of[code]) + " | " + IIP_TEXT
            it["detail"] = IIP_DETAIL
            n += 1
            for r in key["relations"][code]:
                if r["masked"] == mid:
                    r["applies_to"] = rel
    LOG.append(f"S2: {n} IIP items rewritten (this contract: {sorted(NAMED)}; the product group: the others)")
    return n


# ---------------------------------------------------------------- S3: sizes, notionals, ticks, multipliers
YEAR = r"(?:19|20)\d\d"
S3_SUBS = [
    (r"\s*\([\d,.]+ bbl[^)]*\)", ""),                                    # (100 bbl, 0.01 tick)
    (r"\b(?:1:4|4:1|10:1|1:10|5:1|1:5)\b", "[ratio]"),                    # size ratios
    (r"\((?:1/10|1/5|one-tenth|one-fifth) size\)", ""),
    (r"[Ss]pread tick \d+(?:\.\d+)?", "spread tick [figure removed]"),
    (r"\[ratio\] 0\.\d+", "[ratio] [figure removed]"),
    (r"\b(?:EUR|AUD) [\d,]+\b", "[contract size]"),       # EUR 12,500
    (r"\(\$\d+(?:\.\d+)? [Mm]ultiplier\)", "([multiplier])"),             # ($5 Multiplier)
    (r"\$\d+(?:\.\d+)? [Mm]ultiplier", "[multiplier]"),
]
CRYPTO_SPREAD_ITEMS = {"CRYPTO-34"}


MULT_SUBS = S3_SUBS[-2:]  # outside s1 only the multiplier statements are removed ("10:1 leverage" is not a size)


def s3_text(s: str, crypto_figures: bool, s1: bool = True) -> tuple[str, int]:
    n = 0
    for pat, rep in (S3_SUBS if s1 else MULT_SUBS):
        s, k = re.subn(pat, rep, s)
        n += k
    if crypto_figures:
        s, k = re.subn(r"(?<![\d.])(?!" + YEAR + r"\b)\$?\d+(?:\.\d+)?(?: index points?)?(?:/bitcoin)?", "[figure]", s)
        n += k
    return s, n


def patch_sizes(contracts: dict, key: dict) -> dict:
    counts = {"s1_items_changed": 0, "other_items_changed": 0, "subs": 0}
    for lab, sheet in contracts["contracts"].items():
        for sec, items in sheet.items():
            if not isinstance(items, list):
                continue
            for it in items:
                src = key["items"][it["id"]]["source_item"]
                changed = False
                for f in ("value", "detail", "quote", "window"):
                    if isinstance(it.get(f), str):
                        new, k = s3_text(it[f], src in CRYPTO_SPREAD_ITEMS and sec == "D3_s1_relationships",
                                         s1=sec == "D3_s1_relationships")
                        if k:
                            it[f], changed = new, True
                            counts["subs"] += k
                if changed:
                    counts["s1_items_changed" if sec == "D3_s1_relationships" else "other_items_changed"] += 1
    LOG.append(f"S3: {counts}")
    return counts


def main() -> int:
    check_inputs()
    contracts, firms, key = (json.loads((B / f).read_text()) for f in FILES)
    patch_iip(contracts, key)
    patch_sizes(contracts, key)
    firms = patch_firms(firms, key)
    firms = patch_other_firms(firms, key)
    key["plan_labels"] = {"lucid": PLAN_KEY["lucid"],
                          **{f: {**{lab: name for name, lab in V.PLAN_NAMES[f]}, **PLAN_KEY_EXTRA.get(f, {})}
                             for f in V.PLAN_NAMES if f != "lucid"}}
    key["patches"] = {"script": "work/facts/mask_patch.py", "after": "F4_audit.md B1, S2, S3", "log": LOG}
    for name, doc in zip(FILES, (contracts, firms, key)):
        (B / name).write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    for line in LOG:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
