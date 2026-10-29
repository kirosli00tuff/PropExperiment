"""FactTable (Stage E.32b, C1), output 1: briefs/F4_facts_unmasked.json (SCHEMA.md section 2 field names).

Assembles facts only: E.28 F1 facts (A3_facts.json, A3_firm_products.json), F2 reader items, F2_data_access.json
(LR-D0..D3 already applied there), F3_vol.json (main session, median close for the leader computation). The LR-S
readings are data in f4_rulings.py. Run: uv run python reports/stage_e32b_briefs/work/facts/build_f4.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import f4_rulings as R  # noqa: E402

REPO = HERE.parents[3]
B = REPO / "reports" / "stage_e32b_briefs"
E28 = REPO / "reports" / "stage_e28_briefs"
SPEC_SHA256 = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"
FAMILIES = {
    "crude": ("MCL", "QM", "CL"), "natgas": ("MNG", "QG", "NG"),
    "metals": ("MGC", "GC", "SIL", "SI", "MHG", "HG"), "fx": ("M6E", "6E", "M6A", "6A"),
    "crypto": ("MET", "ETH", "MBT", "BTC"), "equity": ("M2K", "RTY", "MYM", "YM", "MNQ", "NQ"),
    "rates": ("2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN", "ZB"),
    "grains": ("MZC", "MZS", "MZW", "MZL", "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM"),
}
FAMILY_OF = {c: f for f, cs in FAMILIES.items() for c in cs}
FIRMS = ("topstep", "lucid", "tradeify", "mffu", "bulenox")
F2_FAMILY_FILES = [f"F2_{f}.json" for f in FAMILIES] + ["F2_shared_cftc_automation.json",
                                                        "F2_shared_baltussen.json"]
SAME_PRICE_GROUPS = (
    ("MCL", "QM", "CL"), ("MNG", "QG", "NG"), ("MGC", "GC"), ("SIL", "SI"), ("MHG", "HG"), ("M6E", "6E"),
    ("M6A", "6A"), ("MET", "ETH"), ("MBT", "BTC"), ("M2K", "RTY"), ("MYM", "YM"), ("MNQ", "NQ"),
    ("MZC", "XC", "ZC"), ("MZS", "XK", "ZS"), ("MZW", "XW", "ZW"), ("MZL", "ZL"), ("MZM", "ZM"))


def load(p: Path) -> dict:
    return json.loads(p.read_text())


def now_pdt() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M %Z")


def dec(x) -> float | int:
    """A clean JSON number from an exact Fraction."""
    f = Fraction(x)
    return int(f) if f.denominator == 1 else float(f)


class Items:
    """Every F2 item by id, with the file it came from."""

    def __init__(self) -> None:
        self.by_id: dict[str, dict] = {}
        self.file_of: dict[str, str] = {}
        for name in F2_FAMILY_FILES:
            for it in load(B / name).get("items", []):
                if it["id"] in self.by_id:
                    raise SystemExit(f"duplicate item id {it['id']}")
                self.by_id[it["id"]] = it
                self.file_of[it["id"]] = name

    def need(self, iid: str) -> dict:
        if iid not in self.by_id:
            raise SystemExit(f"item {iid} not found in the F2 files")
        return self.by_id[iid]

    def ref(self, iid: str) -> dict:
        it = self.need(iid)
        return {"id": iid, "file": f"reports/stage_e32b_briefs/{self.file_of[iid]}", "topic": it.get("topic"),
                "verified": it.get("verified")}

    def naming(self, code: str) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for iid, it in self.by_id.items():
            if code in (it.get("codes") or []):
                out.setdefault(it.get("topic") or "?", []).append(iid)
        return out


# ---------------------------------------------------------------- codes
def adv_block(code: str, a3: dict, items: Items) -> dict:
    rec = a3["candidates"][code]["ADV"]
    flags = rec.get("flags") or []
    kind = ("v0_front_median" if "OC2_owned_v0_front" in flags else
            "published_all_expiry" if "OC2_published" in flags else "unknown")
    out = {"value": rec.get("value"), "kind": kind if rec.get("value") is not None else "unknown",
           "unit": rec.get("unit"), "window": rec.get("window"),
           "source": f"reports/stage_e28_briefs/A3_facts.json:candidates.{code}.ADV ({rec.get('provenance')})",
           "flags": flags, "newer_beside": []}
    if rec.get("value") is None:
        out["reason"] = "E.28 ADV unknown (E.28 OC-A3-7: no qualifying published figure); spec: L = 1 (u)"
    newer = {"QM": ("CRUDE-24", 4480.5, "median daily volume 2025-10-01..2026-09-30 (program measurement, E.31)"),
             "RTY": ("EQUITY-53", 217000, "2025 to October (FTSE Russell insight page)"),
             "M2K": ("EQUITY-53", 85000, "2025 to October (FTSE Russell insight page)"),
             "BTC": ("CRYPTO-5", 12167, "5-day average 2026-01-05..09 (CME Bitcoin futures report)")}
    if code in newer:
        iid, v, w = newer[code]
        items.need(iid)
        out["newer_beside"].append({"value": v, "window": w, "item": iid, "used": False,
                                    "note": "shown beside E.28's ADV, not substituted (spec 1)"})
    return out


def spread_block(code: str, items: Items) -> dict:
    if code in R.SPREAD_QUALIFYING:
        clause, ids, note = R.SPREAD_QUALIFYING[code]
        for i in ids:
            items.need(i)
        return {"value": 1, "sourced": True, "item": ids[0], "items": ids, "clause": f"LR-S {clause}",
                "note": f"S = 1 tick: {note}"}
    ids, why = R.SPREAD_NOT_QUALIFYING.get(code, ([], "no spread figure found by the reader"))
    for i in ids:
        items.need(i)
    return {"value": None, "sourced": False, "item": None, "items_considered": ids,
            "clause": "none: S = 1 (u)", "note": why}


def touch_block(code: str, items: Items) -> dict:
    if code in R.TOUCH_QUALIFYING:
        v, ids, note = R.TOUCH_QUALIFYING[code]
        for i in ids:
            items.need(i)
        return {"value": v, "sourced": True, "item": ids[0], "clause": "LR-S touch: sourced median", "note": note}
    ids, why = R.TOUCH_NOT_QUALIFYING.get(code, ([], "no touch figure found by the reader"))
    for i in ids:
        items.need(i)
    return {"value": None, "sourced": False, "item": None, "items_considered": ids,
            "clause": "none (not counted)", "note": why}


def settles_block(code: str, items: Items, f2pc: dict) -> dict:
    basis = (f2pc.get(code) or {}).get("settlement_basis")
    if code in R.SETTLES_OFF:
        sib, ids = R.SETTLES_OFF[code]
        for i in ids:
            items.need(i)
        return {"value": True, "sibling": sib, "item": ids[0], "items": ids, "basis": basis}
    return {"value": False, "sibling": None, "item": (f2pc.get(code) or {}).get("settlement_item"),
            "basis": basis or R.SETTLES_NOT.get(code)}


def pauses_for(code: str) -> list[dict]:
    fam = FAMILY_OF[code]
    if fam == "grains":
        return [dict(p) for p in R.PAUSE_SETS["grains"]]
    if code in ("2YY", "5YY", "10Y", "30Y"):
        return [dict(p) for p in R.PAUSE_SETS["yields_break"]]
    if fam == "crypto":
        return [dict(p) for p in R.PAUSE_SETS["crypto_break"]]
    p = dict(R.PAUSE_SETS["cme_ct_break"][0])
    p["item"] = R.PAUSE_ITEM_BY_FAMILY[fam]
    if fam in ("crude", "equity"):
        p["what"] = "daily 60-minute break 17:00-18:00 ET"
    return [p]


def data_access_block(code: str, da: dict) -> dict:
    x = da["codes"][code]
    k = x.get("k_usd_month")
    method = str(x.get("k_method") or "")
    kind = "unknown" if k is None else ("ledger MBO quote" if "ledger MBO" in method else "estimate")
    o_raw, p_raw = x.get("o_owned_36m"), x.get("p_all_read")
    pb = x.get("p_brief") or {}
    return {
        "mbo_start": x.get("mbo_start"), "k_usd_month": k, "k_kind": kind,
        "o_owned_36m": None if o_raw is None else (o_raw == 0),
        "p_all_read": None if p_raw is None else (p_raw == 1),
        "source": f"reports/stage_e32b_briefs/F2_data_access.json:codes.{code} (primary fields, LR-D0..D3 applied)",
        "f2_raw": {"o_owned_36m": o_raw, "o": x.get("o"), "p_all_read": p_raw, "p": x.get("p"), "h": x.get("h"),
                   "k": x.get("k"), "k_method": x.get("k_method")},
        "conversion_note": "F2_data_access writes o_owned_36m and p_all_read as the D5 o and p scores (equal to its "
                           "'o' and 'p' fields: o 0 = owned >= 36 months; p 1 = every window read). SCHEMA.md reads "
                           "booleans, so o_owned_36m = (F2 o == 0), p_all_read = (F2 p == 1). Values are copied, "
                           "not recomputed.",
        "k_ZM": x.get("k_ZM"),
        "p_brief": {**pb, "p_all_read": None if pb.get("value") is None else (pb.get("value") == 1)},
    }


def leaders(codes: dict, f3: dict) -> None:
    """Leader = the sibling with the largest USD-notional ADV (ADV x multiplier x F3 median close; a code without
    a close borrows its same-price sibling's). Where it cannot be computed, the readers' per_code leader is used."""
    same = {c: g for g in SAME_PRICE_GROUPS for c in g}

    def close(c: str):
        v = (f3["roots"].get(c) or {}).get("median_close")
        if v is None:
            for s in same.get(c, ()):
                v = (f3["roots"].get(s) or {}).get("median_close")
                if v is not None:
                    return Fraction(str(v))
            return None
        return Fraction(str(v))

    for c, rec in codes.items():
        group = [c] + [s for s in rec["siblings"] if s != c]
        notional = {}
        for g in group:
            a, m, px = codes[g]["adv"]["value"], codes[g]["multiplier"], close(g)
            notional[g] = None if None in (a, m, px) else Fraction(str(a)) * Fraction(str(m)) * px
        known = {g: v for g, v in notional.items() if v is not None}
        if len(group) == 1:
            rec["leader"], basis = c, "no sibling under spec 0 / 2.4"
        elif known and len(known) == len(group):
            rec["leader"], basis = max(known, key=known.get), "computed: largest USD-notional ADV"
        elif known and not rec.get("_reader_leader"):
            best = max(known, key=known.get)
            rec["leader"] = best
            basis = (f"computed among siblings with a known notional ({sorted(known)}); unknown for "
                     f"{sorted(set(group) - set(known))}")
        elif known:
            best = max(known, key=known.get)
            rec["leader"] = rec["_reader_leader"]
            basis = (f"readers' per_code leader (notional unknown for {sorted(set(group) - set(known))}; the "
                     f"largest known notional is {best})")
        else:
            rec["leader"], basis = rec.pop("_reader_leader", None) or c, "readers' per_code leader (notional unknown)"
        rec.pop("_reader_leader", None)
        rec["leader_basis"] = basis
        rec["notional_adv_usd"] = {g: (None if v is None else float(v)) for g, v in notional.items()}


def build_codes(items: Items) -> dict:
    a3 = load(E28 / "A3_facts.json")
    f3 = load(B / "F3_vol.json")
    da = load(B / "F2_data_access.json")
    f2pc: dict = {}
    for f in FAMILIES:
        f2pc.update(load(B / f"F2_{f}.json").get("per_code") or {})
    codes = {}
    for code in FAMILY_OF:
        c3 = a3["candidates"][code]
        ts, tv = c3["tick_size"]["value"], c3["tick_value"]["value"]
        ts_note = f"E.28 unit: {c3['tick_size'].get('unit')}"
        if "cent" in str(c3["tick_size"].get("unit")).lower():  # grains quoted in cents: F3 prices are in USD
            ts = dec(Fraction(str(ts)) / 100)
            ts_note += "; converted to USD (/100) to match F3's price unit"
        mult = Fraction(str(tv)) / Fraction(str(ts))
        cross = items.naming(code)
        if code in R.IIP_CODES:
            cross.setdefault("T2b", [])
            if "RATES-11" not in cross["T2b"]:
                cross["T2b"].append("RATES-11")
        rec = {
            "family": FAMILY_OF[code], "underlying": da["codes"][code]["underlying"],
            "product_name": c3.get("product_name"),
            "excluded": code == "NQ",
            "tick_size": ts, "tick_value_usd": tv, "multiplier": dec(mult),
            "multiplier_note": "USD per price unit = tick_value_usd / tick_size (E.28 A3_facts.json tick fields)",
            "tick_sources": {"tick_size": c3["tick_size"].get("provenance"), "tick_size_note": ts_note,
                             "tick_value_usd": c3["tick_value"].get("provenance")},
            "adv": adv_block(code, a3, items),
            "spread_S": spread_block(code, items),
            "touch": touch_block(code, items),
            "siblings": list(da["codes"][code]["siblings"]),
            "_reader_leader": (f2pc.get(code) or {}).get("leader"),
            "settles_off_sibling": settles_block(code, items, f2pc),
            "main_session_pt": (f3["roots"].get(code) or {}).get("main_session_pt"),
            "pauses": pauses_for(code),
            "listing": {"date": da["codes"][code].get("listing_date"),
                        "source": da["codes"][code].get("listing_source")},
            "data_access": data_access_block(code, da),
            "f2_items": cross,
            "iip_line": R.IIP_CODES.get(code),
        }
        if code == "NQ":
            rec["excluded_reason"] = "excluded (V49); facts kept: MNQ's leader, counts in family shares (D2 c)"
        codes[code] = rec
    leaders(codes, f3)
    return codes


# ---------------------------------------------------------------- firms and pairs
def build_firms() -> dict:
    f2 = load(B / "F2_firms.json")["firms"]
    fp = load(E28 / "A3_firm_products.json")["firms"]
    out = {}
    for f in FIRMS:
        t, e = f2[f], fp[f]
        v = lambda k: (t.get(k) or {}).get("value")  # noqa: E731
        dll = v("dll_50k") or {}
        mll = v("mll_50k") or {}
        fb = v("flat_by_close") or {}
        pit = e["P_items"]
        out[f] = {
            "name": e.get("name"),
            "plan_modelled": v("plan") or (e["plan"].get("plan_50k.plan_name") or {}).get("value"),
            "dll_50k": "none" if f in R.DLL_NONE else dll.get("amount"),
            "dll_note": R.DLL_NONE.get(f) or dll.get("kind"),
            "mll_50k": mll.get("amount"),
            "mll_type": "; ".join(str(x) for x in (mll.get("type"), mll.get("lock")) if x),
            "bc_accepts": v("bc_accepted"),
            "flat_by_close": {"time": fb.get("time"), "tz": fb.get("zone").split()[0]} if fb.get("time") else None,
            "flat_by_close_detail": fb,
            "overnight": {"allowed": bool((v("overnight") or {}).get("evaluation")) or
                          bool((v("overnight") or {}).get("funded")), **(v("overnight") or {})},
            "payout": v("payout_qualification"),
            "payout_changed_vs_e28": (t.get("payout_qualification") or {}).get("changed"),
            "payout_old": (t.get("payout_qualification") or {}).get("old_value"),
            "news_windows": [v("news_windows")] + ([v("news_other_rules")] if t.get("news_other_rules") else []),
            "automation": v("automation"),
            "p_inputs": {"native_api": not (pit["no_documented_api"]["value"]),
                         "oco_api": not (pit["no_api_oco_bracket"]["value"]),
                         "vps_chicago": R.VPS[f], "api_rate_limit_per_s": R.RATE[f]},
            "p_inputs_sources": {"e28_P_items": {k: x.get("value") for k, x in pit.items()},
                                 "e28_rule": "E.28 A3_facts.md OC-A3-8",
                                 "f2_p_inputs": v("p_inputs")},
            "rel_facts": {k: {"value": v(k), "changed": (t.get(k) or {}).get("changed"),
                              "source": (t.get(k) or {}).get("source")}
                          for k in ("rel_founded", "rel_payout_disputes_12m", "rel_rule_changes_12m",
                                    "rel_regulatory")},
            "lookup": {"f2_generated_pdt": "2026-10-28 23:32 PDT",
                       "fetched_utc": sorted({str(((t.get(k) or {}).get("source") or {}).get("fetched_utc"))
                                              for k in t if isinstance(t.get(k), dict)} - {"None"})},
            "sources": {k: (t.get(k) or {}).get("source") for k in ("dll_50k", "mll_50k", "flat_by_close",
                                                                   "overnight", "bc_accepted", "news_windows")},
        }
    return out


def news_items_for(firm: str, code: str, fam: str, firms_f2: dict) -> list[dict]:
    nw = (firms_f2[firm].get("news_windows") or {}).get("value") or {}
    out = []
    if firm == "topstep":
        if code in (nw.get("blocked_among_47") or []):
            out.append({"rule": "Tier 1 news window: no new opening transactions 5 min before to 5 min after CPI, "
                                "FOMC decision, FOMC press conference, NFP, PPI", "effect": "blocked (full-size)",
                        "stages": nw.get("stages"), "item": "F2_firms.json:firms.topstep.news_windows"})
        elif code in (nw.get("capped_among_47_one_lot_still_allowed") or []):
            cap = (nw.get("capped_micros_50k") or {}).get(code)
            out.append({"rule": "Tier 1 news window (same events): micro capped", "effect": f"capped at {cap} at "
                        "50K (one lot allowed)", "stages": nw.get("stages"),
                        "item": "F2_firms.json:firms.topstep.news_windows"})
    elif firm == "mffu":
        cls = {"crude": "energy", "natgas": "energy", "grains": "agricultural"}.get(fam)
        out.append({"rule": "T1 news (FOMC, minutes, Employment, CPI; EIA for energy traders; agricultural reports "
                            "for agricultural traders): 2 min before/after, restricted accounts only (Rapid, Pro "
                            "Sim Funded); Builder 50K unrestricted (page wording conflict noted by FirmRules)",
                    "effect": "none on the Builder 50K plan", "class": cls,
                    "item": "F2_firms.json:firms.mffu.news_windows"})
    elif firm == "lucid":
        out.append({"rule": "LucidPro: no news window; red-folder rule applies to the Daily plan only",
                    "effect": "none", "item": "F2_firms.json:firms.lucid.news_windows"})
    else:
        out.append({"rule": "no news rule", "effect": "none", "item": f"F2_firms.json:firms.{firm}.news_windows"})
    return out


def build_pairs(codes: dict) -> tuple[dict, list[str]]:
    fp = load(E28 / "A3_firm_products.json")
    f2 = load(B / "F2_firms.json")["firms"]
    notes = []
    by = {(p["firm"], p["code"]): p for p in fp["pairs"]}
    listed = {}
    for (f, c), p in by.items():
        val = (p.get("listed_50k") or {}).get("value")
        listed[(f, c)] = {"yes": True, "no": False}.get(val)
    # F2 change check: the F2 lists must equal E.28's
    for f in FIRMS:
        pv = f2[f]["products_50k"]["value"]
        for c in pv["listed"]:
            if listed[(f, c)] is not True:
                notes.append(f"{f}|{c}: F2 lists it, E.28 listed_50k {listed[(f, c)]}")
        for c in pv["not_listed"]:
            if listed[(f, c)] is not False:
                notes.append(f"{f}|{c}: F2 not listed, E.28 listed_50k {listed[(f, c)]}")
        if pv.get("changes_vs_e28"):
            notes.append(f"{f}: F2 changes_vs_e28 {pv['changes_vs_e28']}")

    def fee(f, c):
        return ((by[(f, c)].get("fee_rt_usd") or {}).get("value"))

    pairs = {}
    for f in FIRMS:
        for c in FAMILY_OF:
            p = by[(f, c)]
            rec = {"listed_50k": listed[(f, c)],
                   "listed_source": (p.get("listed_50k") or {}).get("provenance"),
                   "listed_note": (p.get("listed_50k") or {}).get("note"),
                   "position_or_cap": p.get("product_cap") or p.get("position_limit_50k"),
                   "restrictions_text": p.get("restrictions_text"),
                   "news_window_items": news_items_for(f, c, FAMILY_OF[c], f2)}
            if f == "lucid":
                others = {g: fee(g, c) for g in FIRMS if g != "lucid" and fee(g, c) is not None}
                stated = fee(f, c)
                if others:
                    g = max(others, key=others.get)
                    rec.update({"fee_rt_usd": others[g], "fee_kind": "RR-05 (u)",
                                "fee_basis": f"highest round trip for {c} at the other four firms: {g} "
                                             f"{others[g]} (all: {others})",
                                "fee_lucid_commission_rt": stated})
                else:
                    rec.update({"fee_rt_usd": None, "fee_kind": "RR-05 (u)",
                                "fee_basis": "no fee for this product at the other four firms",
                                "fee_lucid_commission_rt": stated})
            else:
                rec.update({"fee_rt_usd": fee(f, c), "fee_kind": "stated" if fee(f, c) is not None else None,
                            "fee_basis": (p.get("fee_rt_usd") or {}).get("provenance"),
                            "fee_note": (p.get("fee_rt_usd") or {}).get("note")})
            if rec["listed_50k"] is True and rec["fee_rt_usd"] is None:
                notes.append(f"{f}|{c}: listed but fee unknown")
            pairs[f"{f}|{c}"] = rec
    return pairs, notes


def main() -> int:
    if (B / "F4_unmasked_READY.txt").exists():
        raise SystemExit("refused: F4_unmasked_READY.txt exists, F4_facts_unmasked.json is FROZEN "
                         "(corrections go to F4_corrections.json)")
    items = Items()
    codes = build_codes(items)
    firms = build_firms()
    pairs, notes = build_pairs(codes)
    doc = {"spec_sha256": SPEC_SHA256, "generated_by": "reports/stage_e32b_briefs/work/facts/build_f4.py",
           "generated_pdt": now_pdt(),
           "conventions": {
               "spread_S": "value 1 with sourced true for an LR-S qualifying figure; null with sourced false "
                           "otherwise (scripts then use S = 1 (u)). clause names the LR-S clause.",
               "touch": "sourced true only for a sourced median (LR-S).",
               "dll_50k": "'none' = the firm's modelled 50K plan has no daily loss limit (SCHEMA.md 2).",
               "data_access": "o_owned_36m / p_all_read converted to booleans from F2's 0/1 scores (see each "
                              "code's conversion_note).",
               "lucid_fees": "RR-05 (u): the highest round trip for that product at the other four firms."},
           "codes": codes, "firms": firms, "pairs": pairs, "build_notes": notes}
    out = B / "F4_facts_unmasked.json"
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    tmp.replace(out)
    n_l = sum(1 for p in pairs.values() if p["listed_50k"] is True)
    n_n = sum(1 for p in pairs.values() if p["listed_50k"] is False)
    print(f"codes {len(codes)} firms {len(firms)} pairs {len(pairs)} listed {n_l} unlisted {n_n} "
          f"unknown {len(pairs) - n_l - n_n}; S sourced {sum(c['spread_S']['sourced'] for c in codes.values())}; "
          f"touch sourced {sum(c['touch']['sourced'] for c in codes.values())}; notes {len(notes)}")
    for n in notes:
        print("  note:", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
