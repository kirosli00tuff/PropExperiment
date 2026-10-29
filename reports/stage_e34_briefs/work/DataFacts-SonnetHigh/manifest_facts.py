"""Metadata-only read of the discovery manifest (identical copy in the ZL MBP-1 folder): per-file bytes,
records, delivered_record_bytes, record counts by instrument_id, for series Z1 (ZM MBO), Z2 (ZS MBP-1), Z3 (ZL MBP-1), Z4."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import guard34
p = guard34.check(guard34.MBP1_DIR / "manifest.json")
m = json.loads(p.read_text())
out = {"top": {k: m[k] for k in ("months","n_planned","n_verified","missing","exit_code","written")},
       "plan_checks": m["plan_checks"], "files": []}
for f in m["files"]:
    h = f["header"]
    out["files"].append({"series": f["series"], "month": f["month"], "name": Path(f["path"]).name,
        "bytes": f["bytes"], "sha256": f["sha256"], "records": f["records"],
        "delivered_record_bytes": f["delivered_record_bytes"],
        "records_by_rtype": f["records_by_rtype"], "records_by_instrument_id": f["records_by_instrument_id"],
        "ts_recv_min": f["ts_recv_min"], "ts_recv_max": f["ts_recv_max"],
        "ts_event_min": f["ts_event_min"], "ts_event_max": f["ts_event_max"],
        "header_version": h.get("version"), "schema": h.get("schema"), "dataset": h.get("dataset"),
        "stype_in": h.get("stype_in"), "stype_out": h.get("stype_out"), "symbols": h.get("symbols"),
        "mappings": h.get("mappings"), "header_start": h.get("start"), "header_end": h.get("end"),
        "request": f["request"], "checks_failed": [c["name"] for c in f.get("checks", []) if not c.get("passed")]})
Path(__file__).with_name("manifest_facts.json").write_text(json.dumps(out, indent=1))
print(len(out["files"]), {s: sum(1 for f in out["files"] if f["series"]==s) for s in ("Z1","Z2","Z3","Z4")})
