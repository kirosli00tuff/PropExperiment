"""IDEAS helper: imports IDEAS_build and writes the JSON (partial while families are being added)."""
import json
import sys
import IDEAS_build as b

final = len(sys.argv) > 1 and sys.argv[1] == "final"
out = dict(b.HEADER)
out["families"] = b.FAMILIES
out["finished_pdt"] = b.now_pdt() if final else None
for k in ("searched_not_found", "gaps", "notices"):
    out[k] = getattr(b, k.upper(), [])
with open(b.OUT, "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(len(b.FAMILIES), "families;", sum(len(x["evidence"]) for x in b.FAMILIES), "evidence rows")
