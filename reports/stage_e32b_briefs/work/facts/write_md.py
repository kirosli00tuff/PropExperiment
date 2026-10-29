"""FactTable output 7: briefs/F4_facts.md, readable unmasked tables from F4_facts_unmasked.json, F4_smean.json and
F4_venue_ibkr.json. Run after the JSON outputs exist."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f4_rulings as R  # noqa: E402
from build_f4 import B, FIRMS, load, now_pdt  # noqa: E402


def f(x) -> str:
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return f"{x:g}"
    return str(x)


def main() -> int:
    d = load(B / "F4_facts_unmasked.json")
    sm = load(B / "F4_smean.json")
    ib = load(B / "F4_venue_ibkr.json")
    ready = (B / "F4_unmasked_READY.txt").read_text().strip()
    L = [f"# F4 facts (Stage E.32b, FactTable C1), unmasked", "",
         f"Generated {now_pdt()} from F4_facts_unmasked.json (READY line: `{ready}`), F4_smean.json, "
         "F4_venue_ibkr.json. Facts only; no score. Item ids are the F2 readers' ids (reports/stage_e32b_briefs/"
         "F2_*.json). '-' = unknown or not applicable.", "",
         "## 1. Codes", "",
         "| code | family | tick | v USD | mult | ADV (E.28) | ADV kind | leader | siblings | settles off sibling "
         "| main session PT | listing |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c, x in d["codes"].items():
        so = x["settles_off_sibling"]
        L.append(f"| {c}{' (excluded V49)' if x['excluded'] else ''} | {x['family']} | {f(x['tick_size'])} | "
                 f"{f(x['tick_value_usd'])} | {f(x['multiplier'])} | {f(x['adv']['value'])} | {x['adv']['kind']} | "
                 f"{x['leader']} | {' '.join(x['siblings']) or '-'} | "
                 f"{('yes: ' + so['sibling'] + ' (' + ', '.join(so.get('items') or []) + ')') if so['value'] else 'no'}"
                 f" | {'-'.join(x['main_session_pt'] or []) or '-'} | {f(x['listing']['date'])} |")
    L += ["", "Newer ADV figures shown beside (not used): " + "; ".join(
        f"{c} {n['value']} ({n['window']}, {n['item']})" for c, x in d["codes"].items()
        for n in x["adv"]["newer_beside"]) + ".", "",
          "Leader basis: computed from USD-notional ADV (ADV x multiplier x F3 median close) where every sibling's "
          "notional is known; the readers' leader otherwise (QM, BTC/MBT, SI/SIL, ETH/MET, the mini and micro "
          "grains, ZL/MZL, ZM/MZM).", "",
          "## 2. Spread S and touch (LR-S)", "",
          "| code | S | sourced | clause | items | touch | touch sourced | touch item | note |",
          "|---|---|---|---|---|---|---|---|---|"]
    for c, x in d["codes"].items():
        s, t = x["spread_S"], x["touch"]
        L.append(f"| {c} | {f(s['value']) if s['sourced'] else '1 (u)'} | {f(s['sourced'])} | {s['clause']} | "
                 f"{', '.join(s.get('items') or s.get('items_considered') or []) or '-'} | {f(t['value'])} | "
                 f"{f(t['sourced'])} | {f(t['item'])} | {s['note'][:150]} |")
    L += ["", "## 3. S_mean variant (F4_smean.json)", "",
          "| code | S_mean | item | window | touch_mean | item |", "|---|---|---|---|---|---|"]
    for c, x in sm["codes"].items():
        s, t = x["spread_S_mean"], x["touch_mean"]
        L.append(f"| {c} | {f(s and s['value'])} | {f(s and s['item'])} | {f(s and s['window'])} | "
                 f"{f(t and t['value'])} | {f(t and t['item'])} |")
    L += ["", f"Counts: {sm['counts']}. Unchanged: {len(sm['unchanged'])} codes.", "",
          "## 4. Firms", "",
          "| firm | modelled plan | DLL 50K | MLL 50K | MLL type | BC | flat by | overnight | P inputs |",
          "|---|---|---|---|---|---|---|---|---|"]
    for fm in FIRMS:
        x = d["firms"][fm]
        fb = x["flat_by_close"] or {}
        p = x["p_inputs"]
        L.append(f"| {fm} | {x['plan_modelled']} | {f(x['dll_50k'])} | {f(x['mll_50k'])} | {x['mll_type'][:80]} | "
                 f"{f(x['bc_accepts'])} | {fb.get('time')} {fb.get('tz')} | {f(x['overnight']['allowed'])} | "
                 f"native {f(p['native_api'])}, OCO {f(p['oco_api'])}, VPS {p['vps_chicago']}, rate "
                 f"{p['api_rate_limit_per_s']} |")
    L += ["", "DLL 'none': " + "; ".join(f"{k}: {v}" for k, v in R.DLL_NONE.items()) + ". The econ firm check "
          "reports these as 'unverifiable' (not a mismatch); every number matches E.28's firm models.", "",
          "Payout changed since E.28: " + ", ".join(fm for fm in FIRMS if d["firms"][fm]["payout_changed_vs_e28"])
          + " (F2_firms.json payout_qualification).", "",
          "## 5. Pairs (listed on the 50K plan)", "",
          "| firm | listed | codes (fee RT USD) |", "|---|---|---|"]
    for fm in FIRMS:
        ps = {k.split("|")[1]: v for k, v in d["pairs"].items() if k.startswith(fm + "|")}
        lst = [c for c, v in ps.items() if v["listed_50k"]]
        L.append(f"| {fm} | {len(lst)} | " + ", ".join(f"{c} ({f(ps[c]['fee_rt_usd'])}"
                                                      f"{' u' if ps[c]['fee_kind'] == 'RR-05 (u)' else ''})"
                                                      for c in lst) + " |")
    L += ["", "Lucid fees are RR-05 (u): the highest round trip for the product at the other four firms "
          "(fee_basis per pair). Topstep news windows: blocked full-size RTY YM NQ GC SI HG; capped micros M2K MYM MNQ "
          "MGC MHG SIL (one lot allowed).", "",
          "## 6. Cross-family program items", "",
          "The International Incentive Program item (RATES-11, a volume-fee incentive, 2011-12-16 to 2026-01-31) "
          "is attached to every code its fee table names: " + ", ".join(sorted(R.IIP_CODES)) + ". Not named: MCL, "
          "MNG, MHG, the crypto codes, the micro grains. Every other F2 item is attached to every code it lists "
          "(codes.<CODE>.f2_items, by topic).", "",
          "## 7. Data access (copied from F2_data_access.json primary fields)", "",
          "| code | MBO start | k USD/month | k kind | owned >= 36 m | all read |", "|---|---|---|---|---|---|"]
    for c, x in d["codes"].items():
        a = x["data_access"]
        L.append(f"| {c} | {f(a['mbo_start'])} | {f(a['k_usd_month'])} | {a['k_kind']} | {f(a['o_owned_36m'])} | "
                 f"{f(a['p_all_read'])} |")
    L += ["", "F2_data_access writes o_owned_36m and p_all_read as the D5 o and p scores (0/1); F4 holds the "
          "booleans the score script reads (owned = F2 o 0; all read = F2 p 1). The score script's soft cross-check "
          "therefore lists 47 'o_owned_36m' differences (format, not value).", "",
          "## 8. Own-broker venue (F4_venue_ibkr.json)", "",
          f"Venue: {ib['venue']}. Account minimum USD {ib['account_minimum_usd']}; overnight holds allowed; no DLL, MLL "
          f"or flat-by-close; capital ceiling: {ib['capital_ceiling_note']}. SIL exchange fee not published "
          "(fee unknown). Per-code fees and margins in the JSON.", "",
          "## 9. Unknowns the scripts meet", "",
          "- ADV unknown (L = 1 u): QM, BTC, MZC MZS MZW MZL MZM. ADV 0 (E.28 published YTD 2026 figure): 2YY 5YY 30Y.",
          "- F3 sigma unknown (gate): SIL SI MET ETH 2YY 5YY 10Y 30Y (status unknown in F3_vol.json).",
          "- k unknown: ETH BTC, the micro yields, the micro and mini grains. MBO start unknown: SI.",
          "- Lucid fee for every listed pair: RR-05 (u). IBKR SIL fee unknown.", ""]
    (B / "F4_facts.md").write_text("\n".join(L))
    print(f"F4_facts.md: {len(L)} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
