"""CRUDE_lib.py: helpers for CrudeReader item scripts (source lookup in pages/CRUDE/log.tsv)."""
import csv, json, pathlib
W = pathlib.Path(__file__).parent
P = "reports/stage_e32b_briefs/pages/CRUDE/"
def _log():
    d = {}
    with open(W.parent.parent / "pages/CRUDE/log.tsv") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) >= 6 and row[5] not in ("-", "", "file"):
                d[row[5]] = (row[0], row[1], row[4])
    return d
LOG = _log()
def src(fn, field=None):
    base = fn[:-4] if fn.endswith(".txt") else fn
    u, t, s = LOG[base]
    return {"file": P + fn, "field": field, "url": u, "fetched_utc": t, "sha256": s}
def it(i, codes, topic, field, value, scope, window, detail, quote, source, verified, negative=False, pointer=False):
    return {"id": f"CRUDE-{i}", "codes": codes, "topic": topic, "field": field, "value": value, "scope": scope,
            "window": window, "detail": detail, "quote": quote, "source": source, "verified": verified,
            "pointer": pointer, "negative": negative}
def write(name, items):
    (W / f"CRUDE_items_{name}.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in items) + "\n")
    print(name, len(items), "items")
