"""E.32 P1: verify the 156 discovery files against the E.31 manifest's sha256 (bytes hashed, nothing decoded)."""
import hashlib, json, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[4]
m = json.loads((REPO / "data/vendor/databento/GLBX.MDP3/mbo/Z1_ZM_v_0-ZM_v_1/manifest.json").read_text())
ok = bad = missing = 0
bad_names = []
for f in m["files"]:
    p = Path(f["path"])
    p = p if p.is_absolute() else REPO / p
    if not p.is_file():
        missing += 1; bad_names.append(("missing", p.name)); continue
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    if h.hexdigest() == f["sha256"] and p.stat().st_size == f["bytes"]:
        ok += 1
    else:
        bad += 1; bad_names.append(("mismatch", p.name))
print(json.dumps({"files": len(m["files"]), "ok": ok, "mismatch": bad, "missing": missing, "problems": bad_names[:20]}))
