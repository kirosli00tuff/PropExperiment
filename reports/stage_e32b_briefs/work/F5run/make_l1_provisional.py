"""Extract the provisional Layer 1 (spec section 3) from the stub score run into L1_provisional.json and .md.

Stage E.32b, C5a F5Runner (Opus 5.5, xhigh), 2026-10-29. Reads only the Layer 1 fields of
score_stub_layer1only.json (primary.layer1, primary.layer1_survivors, primary.L1_below_2, primary.f5_handoff) and
the Layer-1 lead notes. Nothing about E, L2, the pair score S, pair ranks or the top 15 is read or written: in the
stub run those are meaningless. Also writes F5_selection_survivors.json (survivors, top15 empty) for part (c).

Usage: uv run python make_l1_provisional.py  (prints counts only)
"""
import hashlib
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEFS = os.path.abspath(os.path.join(HERE, "..", ".."))
SCORE = os.path.join(HERE, "score_stub_layer1only.json")
F4_PATH = os.path.join(BRIEFS, "F4_facts_unmasked.json")
OUT_JSON = os.path.join(HERE, "L1_provisional.json")
OUT_MD = os.path.join(HERE, "L1_provisional.md")
OUT_SEL = os.path.join(HERE, "F5_selection_survivors.json")
SPEC_SHA = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"
DLL_REF = 1000.0
WARNING = ("PROVISIONAL LAYER 1 ONLY. It comes from a score32b.py run on a STUB econ file "
           "(econ_stub_layer1only.json). Everything that run wrote about E, L2, the pair score S, pair ranks or the "
           "top 15 is MEANINGLESS and is not copied here; use none of it. Layer 1 (D1-D6, L1, the gate) does not "
           "read the econ file, so the Layer 1 values below are the exact spec-3 values for these inputs.")
ROW_KEYS = ("family", "status", "f3_status", "S", "S_sourced", "slip", "c_RT", "D1_horizons", "D1_bands", "D1",
            "D2", "D3", "D4", "D5", "D6", "D2_parts", "D3_parts", "D5_parts", "D6_parts", "L1", "L1_below_2",
            "gate_pass", "gate_reasons", "gate_arithmetic", "r", "r_5", "r_15", "r_OC", "rd_p99", "u", "lead")


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def now_pdt() -> str:
    return subprocess.run(["date", "+%Y-%m-%d %H:%M %Z"], capture_output=True, text=True,
                          env={**os.environ, "TZ": "America/Vancouver"}).stdout.strip()


def val(fact):
    return fact.get("value") if isinstance(fact, dict) else fact


def sat_rule(dp: dict, u_notes: list) -> str:
    """Which spec-3 D4 Sat rule set Sat, in words (from the script's flags and notes)."""
    if not dp.get("Sat"):
        iii_u = any(n.startswith("Sat (iii): unknown") for n in u_notes)
        return "none of (i)-(iii)" + ("; (iii) unknown -> 0 (u)" if iii_u else "")
    rules = []
    if dp.get("sat_i"):
        ratio = dp.get("sib_ratio_max")
        rules.append(f"(i) sibling notional-ADV ratio {ratio:.1f} >= 5" if ratio is not None
                     else "(i) ADV ratio to a larger-size sibling unknown -> holds (u)")
    if dp.get("sat_ii"):
        rules.append("(ii) financially settled off a sibling's settlement (sourced)")
    if dp.get("sat_iii"):
        rules.append("(iii) price-discovery share >= 75% elsewhere (blind)")
    return "; ".join(rules) + f"; leader {dp.get('leader')}"


def l_inputs(cf: dict) -> dict:
    sp, tc = cf.get("spread_S") or {}, cf.get("touch") or {}
    return {"adv": val(cf.get("adv")), "adv_kind": (cf.get("adv") or {}).get("kind"),
            "spread_sourced": sp.get("sourced"), "spread_value": sp.get("value"),
            "touch_sourced": tc.get("sourced"), "touch_value": tc.get("value")}


def code_row(code: str, r: dict, cf: dict) -> dict:
    out = {"code": code}
    out.update({k: r.get(k) for k in ROW_KEYS})
    dp = r.get("D4_parts")
    if dp is None:                       # NQ: excluded (V49), not scored
        out["D4_L"] = out["D4_J"] = out["D4_Sat"] = out["Sat_rule"] = None
        return out
    v = cf.get("tick_value_usd")
    rd = r.get("rd_p99")
    out.update({"D4_L": dp.get("L"), "D4_J": dp.get("J"), "D4_Sat": dp.get("Sat"),
                "Sat_flags": {"i": dp.get("sat_i"), "ii": dp.get("sat_ii"), "iii": dp.get("sat_iii")},
                "sib_ratio_max": dp.get("sib_ratio_max"), "leader": dp.get("leader"),
                "sat_deduction": dp.get("sat_deduction"), "Sat_rule": sat_rule(dp, r.get("u") or []),
                "L_inputs": l_inputs(cf), "tick_value_usd": v,
                "J_input_usd": (rd * v if rd is not None and v is not None else None), "J_ref_usd": DLL_REF})
    return out


def fmt(x, nd=2):
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.{nd}f}".rstrip("0").rstrip(".") if nd > 2 else f"{x:.{nd}f}"
    return str(x)


def write_md(doc: dict) -> None:
    rows = doc["codes"]
    lines = [f"# Stage E.32b provisional Layer 1 (C5a F5Runner, {doc['generated_pdt']})", "",
             f"**{WARNING}**", "",
             "Run note: score32b.py refused the original F2_attention.json (`codes` is a space-separated string, "
             "the script iterates a list: \"code M under two underlyings (crude oil, crude oil)\"). The run used "
             "F2_attention_listcodes.json, a format-only copy (`codes` split on spaces; every other field "
             "unchanged). The lead decides how the real run handles this.", "",
             f"Survivors ({len(doc['survivors'])}): {', '.join(doc['survivors'])}", "",
             f"Gate failures ({len(doc['gate_failures'])}):", ""]
    for reason, codes in doc["gate_failures_by_reason"].items():
        lines.append(f"- {reason}: {', '.join(codes)} ({len(codes)})")
    lines += ["", f"L1 < 2.00 (flagged, variant L1min2): {', '.join(doc['L1_below_2']) or 'none'}", "",
              "## Per code (survivors first, then failures; alphabetical)", "",
              "| code | family | F3 | S | c_RT | D1 | D2 | D3 | D4 | D5 | D6 | L1 | gate | arithmetic | L | J | Sat |"
              " Sat rule |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    order = sorted(rows, key=lambda c: (not rows[c]["gate_pass"], c))
    for c in order:
        r = rows[c]
        gate = "pass" if r["gate_pass"] else "FAIL: " + "; ".join(r["gate_reasons"] or [])
        lines.append(f"| {c} | {r['family']} | {r['f3_status'] or '-'} | {fmt(r['S'])} | {fmt(r['c_RT'])} | "
                     f"{fmt(r['D1'])} | {fmt(r['D2'])} | {fmt(r['D3'])} | {fmt(r['D4'])} | {fmt(r['D5'])} | "
                     f"{fmt(r['D6'])} | {fmt(r['L1'], 3)} | {gate} | {r['gate_arithmetic'] or '-'} | "
                     f"{fmt(r['D4_L'])} | {fmt(r['D4_J'])} | {fmt(r['D4_Sat'])} | {r['Sat_rule'] or '-'} |")
    lines += ["", "## D4 inputs and unknown notes", "",
              "| code | ADV (kind) | spread sourced | touch sourced | J: R_d p99 x v (USD) vs 1,000 | u notes |",
              "|---|---|---|---|---|---|"]
    for c in order:
        r = rows[c]
        li = r.get("L_inputs")
        if li is None:
            lines.append(f"| {c} | excluded (V49) | - | - | - | - |")
            continue
        sp = f"yes, {li['spread_value']}" if li["spread_sourced"] else "no"
        tc = f"yes, {li['touch_value']}" if li["touch_sourced"] else "no"
        lines.append(f"| {c} | {fmt(li['adv'], 0) if li['adv'] is not None else 'unknown'} ({li['adv_kind']}) | "
                     f"{sp} | {tc} | {fmt(r['J_input_usd'], 0) if r['J_input_usd'] is not None else 'unknown'} | "
                     f"{'; '.join(r['u'] or []) or '-'} |")
    lines += ["", "## Layer 1 notes the script raised for the lead", ""]
    lines += [f"- {n}" for n in doc["layer1_lead_notes"]] or ["- none"]
    lines += ["", "## Inputs", ""] + [f"- {k}: {v['path']} (sha256 {v['sha256']})" for k, v in doc["inputs"].items()]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    with open(SCORE, encoding="utf-8") as fh:
        score = json.load(fh)
    with open(F4_PATH, encoding="utf-8") as fh:
        f4 = json.load(fh)
    p = score["primary"]
    layer1 = p["layer1"]
    rows = {c: code_row(c, r, f4["codes"].get(c) or {}) for c, r in sorted(layer1.items())}
    survivors = sorted(c for c, r in rows.items() if r["gate_pass"])
    if survivors != sorted(p["layer1_survivors"]):
        raise SystemExit(f"survivor mismatch: gate_pass {survivors} vs layer1_survivors {p['layer1_survivors']}")
    by_reason = {}
    for c, r in rows.items():
        if not r["gate_pass"]:
            for reason in r["gate_reasons"] or ["(no reason given)"]:
                by_reason.setdefault(reason, []).append(c)
    lead_notes = sorted({n for r in rows.values() for n in (r.get("lead") or [])})
    stamp = now_pdt()
    inputs = {k: v for k, v in score["inputs"].items()}
    inputs["score_stub_layer1only"] = {"path": SCORE, "sha256": sha256(SCORE)}
    doc = {"spec_sha256": SPEC_SHA, "WARNING": WARNING, "generated_pdt": stamp,
           "generated_by": "F5Runner-OpusXHigh (Stage E.32b C5a), make_l1_provisional.py",
           "run_deviation": ("F2_attention.json refused by score32b.py (codes is a space-separated string); the run "
                             "used work/F5run/F2_attention_listcodes.json, a format-only copy (codes split on "
                             "spaces, nothing else changed)"),
           "inputs": inputs, "survivors": survivors, "n_survivors": len(survivors),
           "gate_failures": sorted(c for c, r in rows.items() if not r["gate_pass"]),
           "gate_failures_by_reason": by_reason, "L1_below_2": p["L1_below_2"],
           "layer1_lead_notes": lead_notes,
           "input_checks_soft": sorted(set(x.split(":")[0].split(".")[-1] for x in score["input_checks"])),
           "n_input_checks_soft": len(score["input_checks"]),
           "f5_handoff_survivors": p["f5_handoff"]["layer1_survivors"], "codes": rows}
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
    write_md(doc)
    sel = {"spec_sha256": SPEC_SHA, "source": OUT_JSON, "generated_pdt": stamp,
           "note": "minimal selection for part (c): provisional Layer 1 survivors, top15 empty (lead's real "
                   "selection comes later)", "layer1_survivors": survivors, "top15": []}
    with open(OUT_SEL, "w", encoding="utf-8") as fh:
        json.dump(sel, fh, indent=1)
    print(f"survivors {len(survivors)}; failures {len(doc['gate_failures'])}; reasons "
          f"{ {k: len(v) for k, v in by_reason.items()} }")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
