"""E.20 lead: build reports/stage_e20_h6_freeze.json (schema stage_e20_h6_freeze/1) over H6's code, tests,
text, rulings, inputs and the frozen modules it calls. Run once, last, before the "E.20 H6 freeze" commit.
Usage: uv run python reports/stage_e20_briefs/h6_freeze_manifest.py write|verify <sha256>"""
import glob, hashlib, json, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from h6_rod import constants as K
from h6_rod.preflight import manifest_body

FILES = sorted(set(
    glob.glob("h6_rod/*.py") + glob.glob("tests/test_h6_rod_*.py") + ["tests/_h6_rod_synth.py"]
    + glob.glob("ml_route_v2/**/*.py", recursive=True)
    + ["reports/stage_e20_prereg_H6.md", "reports/stage_e20_review_h6.md", "reports/stage_e20_briefs/h6_rulings_at_freeze.md",
       "reports/stage_e20_briefs/product_NQ.md", "reports/stage_e20_briefs/product_NQ.json",
       "reports/stage_e20_briefs/h6_build.md", "docs/prompts/STAGE_E.20.md",
       "screening/stage_e_engine.py", "screening/stage_e_rules.py", "screening/stage_e_frozen.py",
       "screening/trial_registry.py", "rules/sessions.py", "rules/xfa_rules.py", "rules/products.py",
       "strategy/members/k1/cp1.py", "strategy/members/k1/_port_common.py",
       "data/stage_e_bars.py", "data/group_session.py", "data/calendars/equity.py",
       "reports/stage_e17_run_manifest.json", "reports/stage_e2b_release_calendar.json",
       K.GEX_CSV_REL, K.NQ_STORE_REL if hasattr(K, "NQ_STORE_REL") else "data/processed_step2/NQ/ohlcv-1m_NQ_v_0_2019-05-06_2024-02-29_step2.parquet"]))
OUT = Path("reports/stage_e20_h6_freeze.json")

def write():
    missing = [f for f in FILES if not Path(f).is_file()]
    if missing: sys.exit(f"missing: {missing}")
    if OUT.exists(): sys.exit(f"{OUT} exists; delete it explicitly before rebuilding")
    body = manifest_body([Path(f) for f in FILES], created_pdt=datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds"),
                         pins={"harness_v12": "ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32",
                               "v2_freeze": "a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b",
                               "registry_label": K.REGISTRY_LABEL, "test_ids": dict(K.TEST_IDS),
                               "t3_registered": K.T3_REGISTERED, "engine_lead_in_dates": K.ENGINE_LEAD_IN_DATES,
                               "gex_sha256": K.GEX_CSV_SHA256})
    OUT.write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    print(OUT, hashlib.sha256(OUT.read_bytes()).hexdigest(), len(body["files"]), "files")

def verify(expected):
    got = hashlib.sha256(OUT.read_bytes()).hexdigest()
    body = json.loads(OUT.read_bytes()); bad = []
    for e in body["files"]:
        p = Path(e["path"])
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != e["sha256"]: bad.append(e["path"])
    print("manifest", got, "expected", expected, "match", got == expected, "files", len(body["files"]), "bad", bad)
    sys.exit(0 if got == expected and not bad else 1)

if __name__ == "__main__":
    write() if sys.argv[1] == "write" else verify(sys.argv[2])
