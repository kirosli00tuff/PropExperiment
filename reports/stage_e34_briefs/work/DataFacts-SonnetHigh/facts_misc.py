import json
from datetime import date
from pathlib import Path
HERE = Path(__file__).resolve().parent
TD = [date.fromisoformat(x) for x in json.loads((HERE / "trade_dates_e33rule.json").read_text())]
m = json.loads((HERE / "manifest_facts.json").read_text()); a = json.loads((HERE / "agg_zl.json").read_text())
iv = set()
for f in m["files"]:
    if f["series"] == "Z3":
        for e in f["mappings"]["ZL.v.0"]: iv.add((date.fromisoformat(e["start_date"]), date.fromisoformat(e["end_date"]), e["symbol"]))
def inst_on(day):
    found = {s for x, y, s in iv if x <= day < y}
    assert len(found) <= 1, (day, found)
    return next(iter(found)) if found else None
iid_by_day = {}
for f in sorted((HERE / "counts").glob("zl_*.json")):
    r = json.load(open(f))
    for d, v in r["per_day_instrument"].items():
        for k, c in v.items(): iid_by_day.setdefault(d, {}); iid_by_day[d][k] = iid_by_day[d].get(k, 0) + c
agree = disagree = 0; nonfront = 0; total = 0; dis_dates = []; mapping_change_days = []
prev = None
for d in TD:
    mp = inst_on(d); v = iid_by_day[d.isoformat()]
    dom = max(v, key=v.get)
    if mp == dom: agree += 1
    else: disagree += 1; dis_dates.append(d.isoformat())
    nonfront += sum(c for k, c in v.items() if k != mp); total += sum(v.values())
    if prev is not None and mp != prev: mapping_change_days.append((d.isoformat(), prev, mp))
    prev = mp
out = {"dates": len(TD), "dominant_equals_mapping": agree, "dominant_differs_from_mapping": disagree, "differing_dates": dis_dates,
       "records_not_on_mapped_front": nonfront, "records_total": total, "mapping_front_changes": len(mapping_change_days),
       "mapping_front_change_list": mapping_change_days}
(HERE / "facts_misc.json").write_text(json.dumps(out, indent=1))
print({k: v for k, v in out.items() if k != "mapping_front_change_list"})
print(mapping_change_days == [(c["date"], c["from"], c["to"]) for c in a["dominant_id_changes"]])
