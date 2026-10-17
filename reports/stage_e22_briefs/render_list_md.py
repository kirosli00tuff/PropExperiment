"""Stage E.22 Part A: render reports/stage_e22_confirmation_list.md from the four hashed list JSONs
(reports/stage_e22_k{3,5,6,8}_confirmation_list.json). The JSONs govern; this file restates them and embeds
each JSON's sha256. Lead script; run once, after the JSONs and before the list commit.

Usage: uv run python reports/stage_e22_briefs/render_list_md.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLUSTERS = ("K5", "K3", "K6", "K8")
OUT = ROOT / "reports/stage_e22_confirmation_list.md"


def power_cell(pw: dict | None) -> str:
    if isinstance(pw, dict) and pw.get("status") == "run":
        return f"{pw['supply_days']}, {pw['n_b_chosen']}, {pw['label']}"
    return "not run" if not pw else str(pw.get("status") or pw)


def main() -> int:
    docs = []
    for k in CLUSTERS:
        p = ROOT / f"reports/stage_e22_{k.lower()}_confirmation_list.json"
        raw = p.read_bytes()
        docs.append((k, p, hashlib.sha256(raw).hexdigest(), json.loads(raw)))
    first = docs[0][3]
    L = ["# Stage E.22 Part A confirmation lists (hashed before any confirmation read)", "",
         "STATUS: FROZEN at the commit \"E.22 confirmation lists\". Written by the E.22 lead against docs/prompts/STAGE_E.22.md",
         "Part A, before any bar of any confirmation window was read by any run. After the commit nothing in this file or its",
         "JSONs changes. The machine-read lists are the four JSONs below (they govern where this file differs); each is read by",
         "screening/stage_e_verdict.py and named to the runner's run-once marker.", "",
         "## 0. Provenance and rules", "",
         f"- Harness: {first['harness_sha256']} (reports/stage_e2b_harness_freeze.json, v13).",
         f"- Holm K = {first['k_holm']} (R-E22-A10: clusters with a non-empty Tier A: K3, K4, K5, K6, K8; V14 (b)'s K = 9 shown descriptively in the return).",
         f"- Program N for DSR = {first['program_n']} (R-E22-A11: 532 + E22-F1, registered in this stage).",
         "- Price paths declared before any read: reports/stage_e22_price_paths.json (MGC on GC bars, MNQ on NQ bars, each with the",
         "  micro's costs, tick value and q_c; R-E22-A4, R-E22-A5). Rulings: reports/stage_e22_briefs/partA_rulings.md.",
         f"- Bootstrap: stationary, mean block {first['bootstrap']['mean_block']}, B = {first['bootstrap']['resamples']:,}, "
         f"a fresh generator per trial seeded {first['bootstrap']['seed_base']} + list ordinal, np.quantile {first['bootstrap']['ucb_quantile']}.",
         "- One confirmation run per cluster, behind its run-once marker (reports/stage_e22_K*_RUN_ONCE.json).", "",
         "| Cluster | List JSON | sha256 | Cluster freeze sha256 | Trials (run / listed) |", "|---|---|---|---|---|"]
    for k, p, h, d in docs:
        n_run = sum(1 for t in d["trials"] if t["run"])
        L.append(f"| {k} | {p.relative_to(ROOT)} | {h} | {d['cluster_freeze_sha256']} | {n_run} / {len(d['trials'])} |")
    for k, p, h, d in docs:
        L += ["", f"## {k}", "", "Windows (D4):", "", "| Root (as keyed) | S_X | Window | Price path |", "|---|---|---|---|"]
        for r, s in d["start_dates"].items():
            w = d["confirmation_window"][r]
            L.append(f"| {r} | {s} | {w[0]}..{w[1]} | {d.get('price_paths', {}).get(r, '-')} |")
        L += ["", "| Ord | Trial | Vehicle | Legs | q_c | eps_X ticks ($/day) | Tier | Run | Labels | Seed | Power (supply, n_b, label) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for t in d["trials"]:
            L.append(f"| {t['ordinal']} | {t['member']} | {t['vehicle']} | {' '.join(t['legs'])} | {t['q_c']} | "
                     f"{t['eps_ticks']} (${t['eps_usd_per_day_at_q']:.2f}) | {t['tier']} | {'yes' if t['run'] else 'no'} | "
                     f"{', '.join(t['labels']) or '-'} | {t['bootstrap_seed']} | {power_cell(t['power'])} |")
        notes = [(t["member"], n) for t in d["trials"] for n in t.get("notes", [])]
        if notes:
            L += ["", "Notes (descriptive, not verdict labels):"]
            seen = set()
            for m, n in notes:
                if (m, n) not in seen:
                    seen.add((m, n)); L.append(f"- {m}: {n}")
    L += ["", "## Tests and decision rules (fixed now; identical in every JSON's `rules`)", ""]
    L += [f"- **{name}.** {text}" for name, text in first["rules"].items()]
    L += ["", "## Hashing record", "",
          "Each JSON was written first (sha256 above); this file embeds those hashes and is hashed second; all hashes go into the",
          "commit message \"E.22 confirmation lists\". Each cluster's confirmation run happens only after that commit, once."]
    OUT.write_text("\n".join(L) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} sha256 {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
