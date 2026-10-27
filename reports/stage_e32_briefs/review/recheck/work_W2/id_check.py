"""Test the protocol v0.3 P7.1 registry IDs against screening.trial_registry's regexes.

Reads the regex objects only; never calls register() or touches the ledger.
"""
from __future__ import annotations

import itertools
import re
import sys

sys.path.insert(0, "/home/kiros-li/Documents/GitHub/PropExperiment")
from screening import trial_registry as tr  # noqa: E402

SETS = ["S1", "S2", "S3", "S4", "S5"]
LABELS = ["F05", "F15", "F30", "F60", "T15", "T30"]
GRID = ["L001A", "L001E", "L010A", "L010E", "L100A", "L100E",
        "G2050", "G2200", "G3050", "G3200"]
TEST = "E33"


def main() -> None:
    print("_ID pattern:", tr._ID.pattern)
    print("_TEST pattern:", tr._TEST.pattern)
    ids = [f"{TEST}-{s}{lab}{g}" for s, lab, g in itertools.product(SETS, LABELS, GRID)]
    print("count:", len(ids), "unique:", len(set(ids)))
    bad = [i for i in ids if not tr._ID.fullmatch(i) or not i.startswith(f"{TEST}-")]
    print("fullmatch failures:", bad)
    print("test label fullmatch:", bool(tr._TEST.fullmatch(TEST)))
    print("max suffix length:", max(len(i.split("-", 1)[1]) for i in ids))
    for example in ["E33-S5F15L010A", "E33-S5F15L100E", "E33-S5F15G3050", "E33-S1F05L001A",
                    "E33-S5T30G3200"]:
        print(example, "in set:", example in set(ids), "fullmatch:", bool(tr._ID.fullmatch(example)))
    # Old v0.2 forms, for the record
    for old in ["E33-S1-FH05-L-C0.01-r0", "E33-S5-TB30-G-d3-m200"]:
        print(old, "fullmatch:", bool(tr._ID.fullmatch(old)))
    # The generic pattern the brief states
    pat = re.compile(r"E33-S[1-5](F05|F15|F30|F60|T15|T30)(L001A|L001E|L010A|L010E|L100A|L100E|G2050|G2200|G3050|G3200)")
    print("all ids match brief pattern:", all(pat.fullmatch(i) for i in ids))
    print("current_n (read-only):", tr.current_n())


if __name__ == "__main__":
    main()
