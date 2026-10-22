"""Task 2: pick two non-B0 limit primary cells at random (numpy default_rng(20261022)).

Pick 1 from the eligible cells with rho > 0; pick 2 from all remaining eligible cells. Eligible: case limit, form
primary, basket != B0, status computed, from E29_cells.json, sorted by cell_id.
"""
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
d = json.loads((REPO / "reports/stage_e29_briefs/E29_cells.json").read_text())
elig = sorted(c["cell_id"] for c in d["cells"] if c["case"] == "limit" and c["form"] == "primary"
              and c["basket"] != "B0" and c["status"] == "computed")
rng = np.random.default_rng(20261022)
pos = [c for c in elig if not c.endswith("r0.00")]
a = pos[int(rng.integers(len(pos)))]
rest = [c for c in elig if c != a]
b = rest[int(rng.integers(len(rest)))]
print(len(elig), "eligible;", len(pos), "with rho > 0; picks:", a, b)
