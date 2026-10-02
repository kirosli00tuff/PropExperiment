"""Auditor: static check of every K8 file, the factories' names, legs, windows and sizes, and the
fields each member touches on a bar (Task 3 items 4, 6, 10, 12)."""

from __future__ import annotations

import os

os.nice(10)

import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))

from screening.stage_e_freeze import ALLOWED_IMPORTS, check_member_source  # noqa: E402
from screening.stage_e_frozen import load_frozen_tables  # noqa: E402
from strategy.members.k8 import flight, oilcad, wkndbtc  # noqa: E402
from strategy.stage_e.interface import StageEMember  # noqa: E402

K8 = REPO / "strategy/members/k8"
for path in sorted(K8.glob("*.py")):
    rel = path.relative_to(REPO).as_posix()
    problems = check_member_source(rel, path.read_text(encoding="utf-8"), "K8")
    print(f"[static] {rel}: {len(path.read_bytes())} bytes, problems {problems}")
print(f"[static] fractions allowed: {'fractions' in ALLOWED_IMPORTS}; statistics allowed: "
      f"{'statistics' in ALLOWED_IMPORTS}")

tables = load_frozen_tables()
for root in ("MGC", "6C", "MNQ"):
    print(f"[vehicle] {root} q_c {tables.vehicles[root].q_c}")

for factory in (flight.make_h30, flight.make_heod, oilcad.make_6c, wkndbtc.make_mnq):
    m = factory()
    print(f"[decl] {factory.__module__}.{factory.__name__}: name={m.name!r} legs="
          f"{[(leg.root, leg.traded) for leg in m.legs]} protocol={isinstance(m, StageEMember)}")
    for root, ivs in m.trading_windows.items():
        print(f"       window {root}: " + "; ".join(
            f"[{iv.start_ct:%H:%M} d{iv.start_offset_days:+d}, {iv.end_ct:%H:%M} d{iv.end_offset_days:+d})"
            for iv in ivs))
    q = getattr(m, "_q_c", None) or getattr(m, "_q", None)
    print(f"       size attribute {q}")

# bar attributes each member touches
for name in ("flight.py", "oilcad.py", "wkndbtc.py"):
    src = (K8 / name).read_text(encoding="utf-8")
    attrs = sorted(set(re.findall(r"\b(?:bar|mbt|mnq|b)\.([a-z_]+)", src)))
    print(f"[fields] {name}: {attrs}")
    acct = sorted(set(re.findall(r"account\.([a-z_]+)", src)))
    view = sorted(set(re.findall(r"view\.([a-z_]+)", src)))
    print(f"[fields] {name}: account.{acct} view.{view}")
    lits = sorted(set(re.findall(r"leg_market_intent\([^)]*\)", src)))
    print(f"[intents] {name}: {lits}")
