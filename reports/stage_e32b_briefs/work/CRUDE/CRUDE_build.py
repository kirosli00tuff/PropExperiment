"""CRUDE_build.py: assemble F2_crude.json from CRUDE_items.jsonl and CRUDE_meta.json (CrudeReader helper)."""
import json, sys, pathlib
W = pathlib.Path(__file__).parent
OUT = W.parent.parent / "F2_crude.json"
meta = json.loads((W / "CRUDE_meta.json").read_text())
items = [json.loads(l) for f in sorted(W.glob("CRUDE_items_*.jsonl")) for l in f.read_text().splitlines() if l.strip()]
ids = [i["id"] for i in items]
dup = {x for x in ids if ids.count(x) > 1}
if dup:
    sys.exit(f"duplicate ids: {dup}")
req = ["id","codes","topic","field","value","scope","window","detail","quote","source","verified","pointer","negative"]
for i in items:
    miss = [k for k in req if k not in i]
    if miss:
        sys.exit(f"{i.get('id')} missing {miss}")
doc = {"family": "crude", "worker": "CrudeReader-OpusHigh", "codes": ["MCL","QM","CL"]}
doc.update({k: meta[k] for k in ["started_pdt","finished_pdt","websearch_calls","fulltext_reads_t6","notices"]})
doc["items"] = items
for k in ["searched_not_found","per_code","gaps"]:
    doc[k] = meta[k]
OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
print(f"wrote {OUT.name}: {len(items)} items, topics", sorted({i['topic'] for i in items}))
