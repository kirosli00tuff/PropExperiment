"""Stage E.12 Task 3: write the ML route v2 freeze manifest reports/stage_e12_ml_v2_freeze.json.

    uv run python reports/stage_e12_briefs/build_v2_freeze.py --harness-sha256 <v7 sha>

Hashes the frozen design, every ml_route_v2/ file, the tests/test_ml_v2_*.py files and every data
input Gate 0, the filter, the K9 signal and the phase-1 ranking read; regenerates the V2.1 universe
table from cost_wall.json and checks it against the design; records the Gate 0 bar and the decided
constants as built, the lead rules P-1..P-6 and the program N with its sources. Then verifies the
manifest with ml_route_v2.phase1.freeze.verify_v2_freeze and prints its sha256. Refuses to overwrite
an existing manifest (the freeze is written once).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "reports/stage_e12_ml_v2_freeze.json"
DESIGN = "docs/STAGE_E_ML_V2_DESIGN.md"
INPUTS = {  # path -> role (each read by the frozen v2 code or the phase-1 ranking)
    "reports/stage_e10_research/cost_wall.json": "cost wall: V2.1 RT_X, the universe table",
    "reports/stage_e12_cme_margins.json": "Task 2a: the CME margin attempt (blocked; not used, V2.1 step 6)",
    "reports/stage_e12_topstep_150k.md": "Task 2b: 150K MLL, scaling plan, Combine and reset prices",
    "reports/stage_e12_ec_k9_2019_2024.json": "Task 2c: EC-K9 for the training window (k9_anncday)",
    "reports/stage_e12_ec_k9_2019_2024.md": "Task 2c: its CAL-E12 source rows",
    "reports/stage_e10_catalog_K9.json": "EC-K9 research-window rows; K9-anncday-01's vehicles",
    "reports/stage_e2b_release_calendar.json": "the frozen release calendar (G13-G15, costs, P-5)",
    "reports/stage_e2a_epsilon.json": "E|m_1|: the phase-1 ranking's proxy (V2.1 step 6)",
    "reports/stage_e0_liquidity.json": "the D1 ADV census: the ranking's tiers",
    "reports/stage_e2a_costs.json": "D8 cost surface (c, event-window rule)",
    "reports/stage_e2a_vehicles.json": "D2 vehicles and q_c",
    "reports/stage_e2a_vehicle_sizes.json": "D6 sessions (O_X, C_X)",
    "reports/stage_e0_topstep_facts.json": "Topstep facts (50K, payout caps, DLL)",
    "reports/stage_d1f_step5_start_rule.json": "MES's D4 start (2020-02-03)",
    "reports/stage_e12_briefs/rank_phase1.py": "the phase-1 subset rule as applied (lead rule P-4)",
}
RULES = {
    "P-1": "Roots available to features: the phase-1 price paths plus MES; micro stores MCL, MGC, MHG never read; a signal is computed iff own_path_only or every root it reads is available, else a coverage exclusion (V2.3), listed.",
    "P-1a": "If the frozen loader refuses MES's confirmation store, MES is unavailable and its signals are coverage exclusions, logged; a refused price-path store stops the run.",
    "P-2": "Gate 0 list: A = every panel signal x 3 horizons on admissible-pair rows (a test with < 2 dates has t NaN, p 1, counted); B = every admissible (product, horizon) at tau 0.167; registered in ledger/ml_v2_config_ledger.jsonl and hashed before any statistic.",
    "P-3": "S_X per price path by D4's frozen start rule (volume only, never a price); MES fixed at 2020-02-03; bars cut at S_X.",
    "P-4": "Subset rule as applied: tier by vehicle YTD-2026 ADV >= median of 28; c/sigma_proxy ascending within tier (ties alphabetical); pass 1 = the 7 cluster-best in rank order; pass 2 = the rest; acct-1 if quote x 1.03 fits, else acct-2, else skip; NG $0. Proxy: frozen E|m_1| for the whole ranking (CME blocked).",
    "P-5": "Release window: an entry with a fill in [r - 5, r + 30) of a release concerning p is refused if open lot-equivalents including it would exceed half the tier's maximum position size.",
    "P-6": "N_program = 198.",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def entry(rel: str) -> dict:
    p = ROOT / rel
    return {"path": rel, "sha256": sha256(p), "bytes": p.stat().st_size}


def code_files() -> list[str]:
    files = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "ml_route_v2").rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    tests = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("test_ml_v2_*.py"))
    return files + tests + ["tests/ml_v2_fixtures.py"]  # imported by the tests (review F-6)


def universe_check() -> dict:
    from ml_route_v2.constants import UNIVERSE
    wall = {r["vehicle"]: r for r in json.loads(
        (ROOT / "reports/stage_e10_research/cost_wall.json").read_text())["rows"]}
    text = (ROOT / DESIGN).read_text(encoding="utf-8")
    rows = re.findall(r"^\| (K\d) \| ([^|]+?) \| (\w+) \| (\w+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|$",
                      text, flags=re.M)
    problems, regenerated = [], []
    if len(rows) != 28:
        problems.append(f"design table has {len(rows)} rows, not 28")
    for cl, exp, veh, path, tick, rt_t, rt_usd in rows:
        w = wall.get(veh)
        if w is None:
            problems.append(f"{veh}: not in cost_wall.json")
            continue
        # The design table is a display (E.11's generator): ticks are rt_wall_ticks formatted with
        # Python's "%.2f" (checked exactly); RT_X $ is the 2-dp ticks times the tick value, shown to
        # the cent with E.11's rounding (checked to +/- $0.01). Code uses unrounded rt_wall_ticks.
        t2 = float("%.2f" % w["rt_wall_ticks"])
        gen = (w["cluster"], veh, UNIVERSE[veh][1], w["tick_value_usd"], t2,
               round(t2 * w["tick_value_usd"], 2))
        regenerated.append(dict(zip(("cluster", "vehicle", "price_path", "tick_usd", "rt_ticks",
                                     "rt_usd"), gen)))
        design = (cl, veh, path, float(tick), float(rt_t), float(rt_usd))
        if UNIVERSE.get(veh) != (cl, path):
            problems.append(f"{veh}: design ({cl}, {path}) vs constants.UNIVERSE {UNIVERSE.get(veh)}")
        if abs(gen[3] - design[3]) > 1e-9 or abs(gen[4] - design[4]) > 1e-9 \
                or abs(gen[5] - design[5]) > 0.0100001:
            problems.append(f"{veh}: design {design[3:]} vs cost wall {gen[3:]}")
    return {"rows_checked": len(rows), "problems": problems, "regenerated": regenerated,
            "ok": not problems and len(rows) == 28}


def gate0_snapshot() -> dict:
    import ml_route_v2.constants as c
    names = ("COST_GATE_READING", "COST_GATE_KS", "C_SIGMA_TAU", "GATE0_COST_MULTIPLE", "GATE0_T_MIN",
             "GATE0_FAMILY_ALPHA", "GATE0_TOP_FRACTION", "GATE0_MIN_TRADES",
             "GATE0_HOLM_INCLUDES_FAMILY_A", "GATE0_RIDGE_LAMBDA", "HORIZONS", "N_BLOCKS",
             "N_TEST_BLOCKS", "EMBARGO_DATES", "MIN_TRADES", "N_PROGRAM_AT_FREEZE",
             "N_CONFIGURATIONS", "RELEASE_WINDOW_BEFORE_MIN", "RELEASE_WINDOW_AFTER_MIN",
             "RELEASE_WINDOW_TIER_FRACTION", "PAYOUT_RESET_DELAY_DATES", "TRAIN_LAST", "FORBIDDEN_FROM")
    return {n: (str(v) if not isinstance(v, (int, float, str, bool, tuple, list)) else v)
            for n in names for v in [getattr(c, n)]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness-sha256", required=True)
    a = ap.parse_args()
    if OUT.exists():
        raise SystemExit(f"{OUT.name} exists: the freeze is written once")
    uni = universe_check()
    if not uni["ok"]:
        raise SystemExit(f"universe table check failed: {uni['problems']}")
    from ml_route_v2.fingerprint import constants_fingerprint
    files = [entry(DESIGN)] + [entry(f) for f in code_files()] + [entry(f) for f in INPUTS]
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    doc = {
        "schema": "ml_v2_freeze/1",
        "stage": "E.12 Task 3",
        "written_pdt": datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds"),
        "design": DESIGN, "status": "FROZEN (V23)",
        "decisions": "docs/DECISIONS.md V18-V23 (V23: all V2.12 items decided except item 18)",
        "git_head_at_write": head,
        "harness_at_freeze": {"version": "v7", "manifest_sha256": a.harness_sha256,
                              "constraint": "Gate 0 runs under harness v8. v8 may change only "
                                            "data/config.py, data/pull_step2.py, docs/ACCESS.md and "
                                            "their tests, and no data/config.py name the phase-1 path "
                                            "imports; the Task 4 v8 review verifies both (review F-4, "
                                            "F-9). Every phase-1 step runs the harness preflight and "
                                            "this manifest's check."},
        "lead_rules": RULES,
        "gate0_list_rule": "design V2.2b 'The phase-1 test list' (P-1, P-1a, P-2, P-3); the list "
                           "itself is generated and hashed at Task 6 (reports/stage_e12_gate0_list.json)",
        "program_n": {"n_program": 198, "sources": [
            "docs/STAGES.md line 114 (E.9: N = 198)", "reports/E.9_RETURN.md line 21 (194 + 4 = 198)",
            "V21: E.10 screened nothing", "code review C-08: E.11 synthetic runs add nothing"],
            "note": "no machine-readable program-N ledger exists; read from the stage records"},
        "constants_fingerprint": constants_fingerprint(),
        "gate0_and_decided_constants": gate0_snapshot(),
        "universe_check": uni,
        "inputs_roles": INPUTS,
        "context_sha256_at_write_informational": {p: sha256(ROOT / p) for p in (
            "docs/DECISIONS.md", "docs/prompts/STAGE_E.12.md")},
        "files": files,
    }
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    digest = sha256(OUT)
    from ml_route_v2.phase1.freeze import verify_v2_freeze
    verify_v2_freeze(OUT, digest)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(files)} files; sha256 {digest}; verified")


if __name__ == "__main__":
    main()
