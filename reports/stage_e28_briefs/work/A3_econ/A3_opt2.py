"""A3 sensitivity: Bulenox Qualification 50K Option 2 (EOD drawdown, soft DLL, scaling), the second-listed risk
model. The spec rule selects the first-listed plan (Option 1, trailing intraday), which A3_econ.json reports; the
A2 reader left the option to the lead, so Option 2 is computed beside it with the same machinery.

Option 2 (A2_firm_bulenox.md 1.2-1.3): drawdown 2,500 on the closing balance (EOD), locks at +100; DLL 1,100 soft
(trading stops for the day), removed once the drawdown locks (kept throughout here: conservative); contracts 2 / 4
/ 7 by cash on hand (size 1 fits); same fees, 30-day access, Master payout rules and API fee as Option 1.
Writes pairs/opt2__bulenox__<code>.json. Usage: uv run python A3_opt2.py --workers 4
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from dataclasses import replace
from pathlib import Path

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK))

import A3_run as R  # noqa: E402


def opt2_model():  # noqa: ANN201
    import A3_models as M

    m = M.firm_models()["bulenox"]
    ev = replace(m.eval_rules, combine=replace(m.eval_rules.combine, dll_usd=1100.0))
    return replace(m, plan="Qualification 50K, Option 2 EOD (USD 175 one-time, 30 days) [sensitivity]",
                   eval_rules=ev, eval_trail="eod", eval_dll_usd=1100.0,
                   funded=replace(m.funded, trail="eod", dll_usd=1100.0), dll_usd=1100.0)


def _task(args: tuple[str, str]) -> tuple[str, float, str]:
    code, fp = args
    inputs = json.loads(R.INPUTS.read_text())
    rec = R.run_pair("bulenox", code, inputs, fp, R._STATE)
    rec["flags"].append("SENSITIVITY: Bulenox Option 2 (EOD), not the spec's first-listed plan")
    out = R.PAIRS_DIR / f"opt2__bulenox__{code}.json"
    out.write_text(json.dumps(rec, indent=1))
    return code, rec["runtime_s"], f"{rec['mu_star_lim']} {rec['mu_star_mkt']} {rec['mu10K']}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    fp = R._fingerprint()
    inputs = json.loads(R.INPUTS.read_text())
    codes = [p["code"] for p in inputs["pairs"] if p["firm"] == "bulenox"
             and not (R.PAIRS_DIR / f"opt2__bulenox__{p['code']}.json").exists()]
    R.build_state(["topstep"])  # plain draws only: Option 2 has no intraday rule
    R._STATE["models"]["bulenox"] = opt2_model()
    R._STATE["draws"]["bulenox"] = R._STATE["draws"]["topstep"]
    print(f"{time.strftime('%H:%M:%S')} Option 2: {len(codes)} pairs", flush=True)
    with mp.get_context("fork").Pool(min(a.workers, R.MAX_WORKERS), initializer=R._init_worker) as pool:
        for code, sec, mus in pool.imap_unordered(_task, [(c, fp) for c in codes]):
            print(f"{time.strftime('%H:%M:%S')} bulenox-opt2 {code} {sec:.0f}s {mus}", flush=True)
    os.sync()
    return 0


if __name__ == "__main__":
    sys.exit(main())
