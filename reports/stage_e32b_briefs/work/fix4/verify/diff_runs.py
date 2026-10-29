"""FixVerifier (F4): own diff of score run 2 (05:40:30) against run 3 (08:51:03). Reads the two JSON outputs only.
Prints differing paths grouped by leaf key, and named equality checks on scores, gates, ranks, ties, top lists and variants."""
import json
from collections import Counter
from pathlib import Path

B = Path(__file__).resolve().parents[3]
run2 = json.loads((B / "work/score/score32b_out_run2.json").read_text())
run3 = json.loads((B / "score32b_out.json").read_text())


def flat(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, f"{p}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from flat(v, f"{p}/{i}")
    else:
        yield p, o


a, b = dict(flat(run2)), dict(flat(run3))
only2 = [k for k in a if k not in b]
only3 = [k for k in b if k not in a]
changed = [k for k in a if k in b and a[k] != b[k]]
leaf = lambda k: k.rsplit("/", 1)[-1]
print("paths run2", len(a), "run3", len(b))
print("only in run2:", len(only2), Counter(leaf(k) for k in only2).most_common(10))
print("only in run3:", len(only3), Counter(leaf(k) for k in only3).most_common(10))
print("changed:", len(changed), Counter(leaf(k) for k in changed).most_common(12))
ALLOWED = {"cost_per_attempt", "cost_per_attempt_lim", "generated_pdt"}
odd = [k for k in changed if leaf(k) not in ALLOWED and "/input_checks/" not in k and "/inputs/" not in k]
print("changed outside allowed fields:", len(odd), odd[:20])
odd3 = [k for k in only3 if leaf(k) != "cost_per_attempt_lim" and "/input_checks/" not in k]
print("new paths outside cost_per_attempt_lim / input_checks:", len(odd3), odd3[:20])
# input_checks
ic2, ic3 = run2["input_checks"], run3["input_checks"]
print("input_checks", len(ic2), "->", len(ic3), "; run2 subset of run3:", set(ic2) <= set(ic3))
new_ic = [c for c in ic3 if c not in ic2]
print("new input checks:", len(new_ic))
for c in new_ic:
    print("  ", c[:160])
# inputs
print("inputs differing:", [k for k in run2["inputs"] if run2["inputs"][k] != run3["inputs"][k]])

# named checks on the primary
p2, p3 = run2["primary"], run3["primary"]
print("primary keys:", list(p3.keys()))
pairs2 = p2["pairs"] if "pairs" in p2 else p2.get("ranked")
pairs3 = p3["pairs"] if "pairs" in p3 else p3.get("ranked")
print("pairs", len(pairs2), len(pairs3), "same order:",
      [(r["firm"], r["code"]) for r in pairs2] == [(r["firm"], r["code"]) for r in pairs3])
FIELDS = ("S", "S_rounded", "L1", "L2", "E", "R", "A", "D", "Rel", "P", "m_star", "m10K", "status", "gate_reasons",
          "rank", "econ_block", "room_a", "room_b")
mism = Counter()
for r2, r3 in zip(pairs2, pairs3):
    for f in FIELDS:
        if r2.get(f) != r3.get(f):
            mism[f] += 1
print("field mismatches over pairs:", dict(mism) or "none")
ranked2 = [r for r in pairs2 if r.get("rank") is not None]
ranked3 = [r for r in pairs3 if r.get("rank") is not None]
print("ranked", len(ranked2), len(ranked3))
# cost columns
eq_lim = sum(1 for r2, r3 in zip(ranked2, ranked3) if r2["cost_per_attempt"] == r3["cost_per_attempt_lim"])
diff_mkt = sum(1 for r2, r3 in zip(ranked2, ranked3) if r2["cost_per_attempt"] != r3["cost_per_attempt"])
print("run2 cost == run3 cost_lim on ranked:", eq_lim, "; market differs from limit on:", diff_mkt)
for k in ("ties", "top5", "top_5", "top15", "top_15", "mnq_ranks", "MNQ_ranks", "survivors", "n_ranked", "L1_below_2",
          "f5_handoff", "moves_vs_e28", "for_lead", "layer1"):
    if k in p2 or k in p3:
        print(f"  {k}: equal = {p2.get(k) == p3.get(k)}")
# cost-decided ties
for t in p3.get("ties", []):
    for s in t.get("steps", []):
        if "cost" in str(s.get("decided_by", "")).lower():
            print("  cost-decided tie:", t.get("S_rounded"), s)
# variants
v2, v3 = run2.get("variants", {}), run3.get("variants", {})
print("variants", len(v2), len(v3), "identical:", v2 == v3)
if v2 != v3:
    for name in v3:
        if v2.get(name) != v3.get(name):
            print("  variant differs:", name)
