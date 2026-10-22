"""Put the repo root and the B_pilot folder on sys.path for these tests (run only this dir)."""

import sys
from pathlib import Path

PILOT = Path(__file__).resolve().parents[1]
REPO = PILOT.parents[3]
for entry in (str(REPO), str(PILOT), str(Path(__file__).resolve().parent)):
    if entry not in sys.path:
        sys.path.insert(0, entry)
