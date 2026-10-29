"""FactTable outputs 2 and 3: briefs/F4_smean.json (LR-S declared variant S_mean) and briefs/F4_venue_ibkr.json
(own-broker venue facts from F2_nonprop.json). Facts only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import f4_rulings as R  # noqa: E402
from build_f4 import B, FAMILY_OF, SPEC_SHA256, Items, load, now_pdt  # noqa: E402


def smean(items: Items) -> dict:
    f4 = load(B / "F4_facts_unmasked.json")["codes"]
    codes, unchanged = {}, {}
    for c in FAMILY_OF:
        s_q, t_q = f4[c]["spread_S"]["sourced"], f4[c]["touch"]["sourced"]
        s_new = None if s_q else R.SMEAN_SPREAD.get(c)
        t_new = None if t_q else R.SMEAN_TOUCH.get(c)
        for x in (s_new, t_new):
            if x:
                items.need(x["item"])
        if s_new or t_new:
            codes[c] = {"spread_S_mean": dict(s_new) if s_new else None,
                        "spread_note": ("primary S qualifies under LR-S (kept)" if s_q else
                                        R.SMEAN_UNCHANGED_SPREAD_REASON.get(c, "no sourced mean or average spread")
                                        if not s_new else "S_mean replaces S = 1 (u)"),
                        "touch_mean": dict(t_new) if t_new else None,
                        "touch_note": ("primary touch is a sourced median (kept)" if t_q else
                                       "no sourced mean touch" if not t_new else "touch_mean (no sourced median)")}
        else:
            unchanged[c] = ("S and touch qualify under LR-S (primary kept)" if s_q and t_q else
                            "S qualifies (kept); no sourced mean touch" if s_q else
                            R.SMEAN_UNCHANGED_SPREAD_REASON.get(c, "no sourced mean or average spread or touch"))
    return {"spec_sha256": SPEC_SHA256, "generated_pdt": now_pdt(),
            "rule": "LR-S declared variant S_mean: for a code with no qualifying figure, S (and touch) = its sourced "
                    "mean or average (main session, US day hours, whole day or unstated session; not another named "
                    "session; not snippet-only), the figure whose window is nearest 2022-11-01..2023-10-31. "
                    "Per quantity: a qualifying primary value is kept.",
            "codes": codes, "unchanged": unchanged,
            "counts": {"spread_changes": sum(1 for v in codes.values() if v["spread_S_mean"]),
                       "touch_changes": sum(1 for v in codes.values() if v["touch_mean"])}}


def ibkr() -> dict:
    d = load(B / "F2_nonprop.json")
    com = d["commission"]
    out = {}
    for c in FAMILY_OF:
        p = d["products"][c]
        fee, mg = p.get("fee") or {}, p.get("margin_usd_per_contract") or {}
        side = fee.get("all_in_usd_per_side")

        def num(x):
            try:
                return float(x)
            except (TypeError, ValueError):
                return None
        out[c] = {
            "fee_per_side_usd": side, "fee_rt_usd": None if side is None else round(2 * side, 6),
            "fee_status": fee.get("status"),
            "fee_components_per_side": {"ibkr_execution": fee.get("ibkr_execution_usd"),
                                        "exchange_non_member_tier1": fee.get("exchange_fee_usd_non_member_tier1"),
                                        "clearing": fee.get("clearing_usd"), "regulatory": fee.get("regulatory_usd"),
                                        "formula": fee.get("sum_formula")},
            "fee_items": {"exchange_row_quote": fee.get("exchange_fee_row_quote"),
                          "exchange_page": fee.get("exchange_page"), "regulatory_source": fee.get("regulatory_source"),
                          "commission_page": com.get("page"), "mapping_note": fee.get("mapping_note")},
            "margin_intraday_initial_usd": num(mg.get("intraday_initial")),
            "margin_overnight_initial_usd": num(mg.get("overnight_initial")),
            "margin_overnight_maintenance_usd": num(mg.get("overnight_maintenance")),
            "margin_item": {"source": mg.get("source"), "row_quote": mg.get("row_quote"),
                            "trading_class": mg.get("trading_class")},
        }
    return {"spec_sha256": SPEC_SHA256, "generated_pdt": now_pdt(), "venue": d.get("venue"),
            "source": "reports/stage_e32b_briefs/F2_nonprop.json (fetched " + str(d.get("fetched_pdt")) + ")",
            "fee_rule": com.get("all_in_rule"), "overnight_position_fee": com.get("overnight_position_fee"),
            "market_data": d.get("market_data"), "account_minimum_usd": (d.get("account") or {}).get("minimum_usd"),
            "account_minimum_quote": (d.get("account") or {}).get("minimum_quote"),
            "overnight_holds_allowed": True, "overnight_note": "own account: overnight holds allowed subject to "
                                                              "overnight margin (margin columns above)",
            "dll": None, "mll": None, "flat_by_close": None,
            "limits_note": "own account: no DLL, MLL or flat-by-close rule",
            "capital_ceiling_usd": None,
            "capital_ceiling_note": "none recorded in docs/DECISIONS.md: spec 8.3 uses USD 6,000 (u)",
            "capital_ceiling_search": d.get("capital_ceiling"), "not_done": d.get("not_done"),
            "codes": out}


def main() -> int:
    items = Items()
    for name, doc in (("F4_smean.json", smean(items)), ("F4_venue_ibkr.json", ibkr())):
        (B / name).write_text(json.dumps(doc, indent=1, ensure_ascii=False))
        print(name, "written", doc.get("counts", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
