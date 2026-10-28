"""Stage E.33 P4.2 search proofs runner (ProofCoder).

Per seed: synth33 writes the synthetic tables under <proofs-dir>/seed<s>/ (null seeds 1-20, planted 101-120),
run_search33 runs S5 x {F15, T30} x the 10 grid points (20 configurations, 120 fits; P5 thread cap, nice 10,
DONE markers per configuration and fold), then select33 applies P8 with the production thresholds at N = 838
(b_test from p7_final.py) and the Tier A walk. After every seed the summary is rewritten.

Resumable: synth/DONE, the engine's DONE markers and selection.DONE are skipped on restart. A run manifest pins
the sha256 of the code it runs; a restart with different code stops (P4.2: each seed runs exactly once per
pipeline hash; after a logged fix all 40 rerun under a new --proofs-dir). Fold models of every seed are kept
(seed 1's are needed by LT7).

  uv run python run_proofs33.py                      # the 40 production seeds (the lead launches this)
  uv run python run_proofs33.py --seeds 9001 --kind planted --n-oof 120 --proofs-dir DIR --summary FILE
  uv run python run_proofs33.py --summary-only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
for _p in (str(REPO), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import select33  # noqa: E402
import synth33  # noqa: E402

PROOFS_DIR = Path("/mnt/large-storage/market_data/PropExperiment/derived/e33/proofs")
SUMMARY = HERE.parent / "B5_proofs.md"
RUNNER = HERE / "run_search33.py"
PRODUCTION_SEEDS = synth33.NULL_SEEDS + synth33.PLANTED_SEEDS
LABELS = ("F15", "T30")      # P5 label order inside S5: FH15 before TB30
IDS = tuple(f"E33-S5{lab}{g}" for lab in LABELS for g in select33.GRID_ORDER)
N_PROOF = 838                 # P4.2: the thresholds at the expected N 838
NULL_FAIL_AT = 2              # P4.2: the null proof fails if Tier A is non-empty in 2 or more of 20 seeds
PLANTED_PASS_AT = 14          # P4.2: passes if Tier A is non-empty in at least 14 of 20 planted seeds
HASHED = ("synth33.py", "select33.py", "run_proofs33.py", "search33.py", "run_search33.py", "cal33.py",
          "data33.py", "guard33.py")
P7_FILES = (REPO / "reports/stage_e32_briefs/protocol/p7_final.py",
            REPO / "reports/stage_e32_briefs/protocol/p7_thresholds.py")
PT = ZoneInfo("America/Vancouver")


def now() -> str:
    return datetime.now(PT).strftime("%Y-%m-%d %H:%M:%S %Z")


def log(msg: str) -> None:
    print(f"{now()} {msg}", flush=True)


def pipeline_closure(roots=("run_proofs33", "synth33", "select33", "search33", "run_search33")) -> list:
    """The pipeline/ modules the proofs execute: the roots and every pipeline/ module they import, transitively
    (the same AST walk as search33.pipeline_files, from the proof's own entry points)."""
    import ast
    seen: dict = {}
    todo = list(roots)
    while todo:
        name = todo.pop()
        path = HERE / f"{name}.py"
        if name in seen or not path.exists():
            continue
        seen[name] = path
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                todo += [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                todo.append(node.module.split(".")[0])
    return [seen[n] for n in sorted(seen)]


def code_hashes() -> dict:
    files = pipeline_closure()
    missing = set(HASHED) - {f.name for f in files}
    if missing:
        raise RuntimeError(f"pipeline files not found: {sorted(missing)}")
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files + list(P7_FILES)}


def run_versions() -> dict:
    """Library versions and the uv.lock sha256 (run_search33.versions(); ProofReview SF2)."""
    import run_search33
    return run_search33.versions()


def parse_seeds(text: str) -> list:
    out = []
    for part in text.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return out


def check_manifest(pdir: Path, seeds: list, args) -> dict:
    """Pin the code hashes of this run; a resume with other code stops (exactly once per pipeline hash)."""
    path = pdir / "run_manifest.json"
    import search33
    cur = {"code_sha256": code_hashes(), "engine_pipeline_sha": search33.PIPELINE_SHA,
           "versions": run_versions(), "n": args.n, "n_oof": args.n_oof, "ids": list(IDS),
           "plant_beta": synth33.PLANT_BETA, "plant_feature": synth33.PLANT_FEATURE}
    if path.exists():
        old = json.loads(path.read_text())
        diff = sorted(k for k in cur if old.get(k) != cur[k])
        if diff:
            raise SystemExit(f"refused: {path} was written by other code or settings ({diff}); a rerun after a "
                             "logged fix goes to a new --proofs-dir (P4.2)")
        old.setdefault("starts", []).append({"time": now(), "seeds": seeds, "pid": os.getpid()})
        out = old
    else:
        out = dict(cur, created=now(), starts=[{"time": now(), "seeds": seeds, "pid": os.getpid()}])
    pdir.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(out, indent=1, sort_keys=True))
    tmp.replace(path)
    return out


def wait_window() -> None:
    import run_search33
    while run_search33.in_collector_window():
        log("collector window 15:30-16:00 PT: waiting")
        time.sleep(30)


def run_seed(seed: int, kind: str, pdir: Path, args) -> dict:
    root = pdir / f"seed{seed}"
    timing_path = root / "proof_timing.json"
    timing = json.loads(timing_path.read_text()) if timing_path.exists() else {}
    if (root / "selection.DONE").exists():
        log(f"seed {seed}: selection DONE, skipped")
        return timing
    wait_window()
    t0 = time.time()
    man = synth33.write_seed(seed, root, kind, args.n_oof)
    timing.setdefault("generate_s", man.get("seconds"))
    ids_file = root / "ids.txt"
    ids_file.write_text("\n".join(IDS) + "\n")
    cmd = [sys.executable, str(RUNNER), "--root", str(root), "--ids-file", str(ids_file),
           "--max-procs", str(args.max_procs), "--lgbm-threads", str(args.lgbm_threads),
           "--expected-n", "0" if args.n_oof else str(select33.T_DISC)]
    log(f"seed {seed} ({kind}): search {' '.join(cmd[1:])}")
    t1 = time.time()
    rc = subprocess.call(cmd, cwd=str(REPO))
    timing.setdefault("search_runs", []).append({"start": t1, "end": time.time(), "rc": rc})
    if rc != 0:
        raise SystemExit(f"seed {seed}: run_search33 exited {rc}; stopping (see {root}/search/_logs)")
    dates, sigma, configs = select33.load_root(root, IDS)
    res = select33.select(configs, dates, sigma, args.n, strict=args.n_oof is None)
    res["seed"], res["kind"] = seed, kind
    tmp = root / "selection.json.tmp"
    tmp.write_text(json.dumps(res, indent=1, sort_keys=True, default=float))
    tmp.replace(root / "selection.json")
    timing.update({"total_s": time.time() - t0, "search_s": sum(r["end"] - r["start"] for r in timing["search_runs"]),
                   "done": now()})
    timing_path.write_text(json.dumps(timing, indent=1))
    (root / "selection.DONE").write_text(json.dumps({"time": now(), "tier_a": res["tier_a"],
                                                     "select33_sha256": code_hashes()["select33.py"]}))
    log(f"seed {seed}: Tier A {res['tier_a']}; best {res['best_config']} SR_d {res['best_sharpe']}")
    return timing


# ---------------------------------------------------------------- summary (B5_proofs.md)
def _load(pdir: Path, seed: int) -> dict | None:
    root = pdir / f"seed{seed}"
    if not (root / "selection.DONE").exists():
        return None
    sel = json.loads((root / "selection.json").read_text())
    oracle = root / "synth" / "oracle.json"
    timing = root / "proof_timing.json"
    return {"sel": sel, "oracle": json.loads(oracle.read_text()) if oracle.exists() else None,
            "timing": json.loads(timing.read_text()) if timing.exists() else {}}


def failed_fits(pdir: Path, seed: int, sel: dict) -> dict:
    """{config: [failed folds]} of one seed (stats.json errors of the failed configurations; ProofReview SF1)."""
    out = {}
    for r in sel["configs"]:
        if r["failed"]:
            stats = pdir / f"seed{seed}" / "search" / r["config"] / "stats.json"
            errs = json.loads(stats.read_text()).get("errors", {}) if stats.exists() else {}
            out[r["config"]] = sorted(int(k) for k in errs)
    return out


def _fmt(v, nd: int = 4) -> str:
    return "n/a" if v is None else f"{v:.{nd}f}"


def _seed_rows(pdir: Path, seeds: list, with_oracle: bool) -> tuple:
    rows, loaded = [], {}
    for s in seeds:
        d = _load(pdir, s)
        if d is None:
            rows.append(f"| {s} | not run | | | | |" + (" |" if with_oracle else ""))
            continue
        d["failed"] = failed_fits(pdir, s, d["sel"])
        loaded[s] = d
        sel = d["sel"]
        fun = sel["funnel"]["in_order"]
        fun_txt = " / ".join(str(fun[k]) for k in fun)
        alone = " / ".join(str(v) for v in sel["funnel"]["alone"].values())
        tier = ", ".join(c[4:] for c in sel["tier_a"]) or "-"
        best = sel["best_config"][4:] if sel["best_config"] else "-"
        cells = [str(s), tier, f"failed fits: {len(d['failed'])}", best, _fmt(sel["best_sharpe"]),
                 f"{fun_txt} (alone {alone})"]
        if with_oracle:
            cells.insert(5, _fmt(d["oracle"]["sharpe"]) if d["oracle"] else "n/a")
        mins = d["timing"].get("search_s")
        cells.append(f"{mins / 60:.1f}" if mins else "n/a")
        rows.append("| " + " | ".join(cells) + " |")
    return rows, loaded


def null_sharpe_sd(loaded: dict) -> dict:
    """SD of the 400 null daily Sharpes, each centred on its configuration's mean over the seeds (P4.2). Centring
    removes one degree of freedom per configuration, so sqrt(k / (k - 1)) x the population SD is printed too
    (ProofReview N2); under independence the centred population SD has reference sqrt(19/20) x 0.0354 = 0.0345."""
    per_cfg: dict = {}
    for d in loaded.values():
        for r in d["sel"]["configs"]:
            if r["defined"]:
                per_cfg.setdefault(r["config"], []).append((r["sharpe"], r["constant"]))
    dev_all, dev_live, df_all, df_live = [], [], 0, 0
    for vals in per_cfg.values():
        mu = statistics.fmean(v for v, _ in vals)
        dev_all += [v - mu for v, _ in vals]
        df_all += len(vals) - 1
        live = [v for v, c in vals if not c]
        if len(live) >= 2:
            mu_l = statistics.fmean(live)
            dev_live += [v - mu_l for v in live]
            df_live += len(live) - 1

    def sd(dev, df):
        if len(dev) < 2 or df < 1:
            return None, None
        p = statistics.pstdev(dev)
        return p, (sum(x * x for x in dev) / df) ** 0.5
    sd_all, sd_all_df = sd(dev_all, df_all)
    sd_live, sd_live_df = sd(dev_live, df_live)
    return {"n_all": len(dev_all), "sd_all": sd_all, "sd_all_df": sd_all_df, "n_live": len(dev_live),
            "sd_live": sd_live, "sd_live_df": sd_live_df,
            "n_constant": sum(1 for vals in per_cfg.values() for _, c in vals if c)}


def _failed_lines(loaded: dict) -> list:
    bad = {s: d["failed"] for s, d in loaded.items() if d["failed"]}
    if not bad:
        return ["- Seeds with at least one failed configuration (P5): 0."]
    detail = "; ".join(f"seed {s}: " + ", ".join(f"{c[4:]} folds {f}" for c, f in cf.items())
                       for s, cf in bad.items())
    return [f"- Seeds with at least one failed configuration (P5): {len(bad)} ({detail})."]


def write_summary(pdir: Path, path: Path, null_seeds: list, planted_seeds: list) -> None:
    man_path = pdir / "run_manifest.json"
    man = json.loads(man_path.read_text()) if man_path.exists() else {}
    writer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    man_sha = man.get("code_sha256", {}).get("run_proofs33.py")
    head = ["# Stage E.33 B5 synthetic search proofs (P4.2)", "",
            f"Written {now()} by run_proofs33.py from {pdir}. Thresholds at N = {N_PROOF} (P4.2: the expected N; "
            f"if the registered N differs the proofs are not rerun). Configurations: S5 x {{F15, T30}} x 10 grid "
            f"points (20 per seed, 120 fits). Plant: {synth33.PLANT_FEATURE}, beta = {synth33.PLANT_BETA} ticks "
            f"per minute per unit (synth33; oracle calibration in ProofCoder_calibration.json). The plant is the "
            f"only source of signal; under it the past-path features (F4, F2_7) carry derived momentum, so F4 weight "
            f"in a planted fold model is not a leak (ProofReview N1). The oracle (P3.5 with the true class "
            f"probabilities and class-level means) is a calibration anchor, not a ceiling: P3.5 is not "
            f"Bayes-optimal, so a fitted configuration can exceed it (ProofReview N3).",
            "", f"Code sha256 (run manifest): `{json.dumps(man.get('code_sha256', {}), sort_keys=True)}`",
            f"Engine PIPELINE_SHA (manifest): `{man.get('engine_pipeline_sha')}`; versions (manifest): "
            f"`{json.dumps(man.get('versions', {}), sort_keys=True)}`",
            f"run_proofs33.py that wrote this summary: `{writer_sha}`"
            + ("" if writer_sha == man_sha else f" (DIFFERS from the manifest's `{man_sha}`)"),
            "Starts (manifest): " + "; ".join(f"{st['time']} seeds {st['seeds']}" for st in man.get("starts", [])),
            "",
            "Columns: Tier A members; failed fits = configurations that failed (P5; they fail G1 and have no "
            "series); the best configuration over all 20 (P8 total order, gates ignored) and its SR_d; the funnel in "
            "order G1 / G1..G2 / ... / G1..G5 (and each gate alone); search wall minutes.",
            "Counting rule (ProofReview SF1): a seed with any failed configuration is never a clean empty Tier A. "
            "Null: it counts against the proof together with the seeds whose Tier A is non-empty. Planted: it does "
            "not count toward the pass count, even with Tier A non-empty. Both raw counts are printed.", ""]
    out = list(head)
    if null_seeds:
        rows, loaded = _seed_rows(pdir, null_seeds, False)
        out += ["## Null seeds", "", "| seed | Tier A | failed | best | best SR_d | funnel | search min |",
                "|---|---|---|---|---|---|---|"] + rows
        nonempty = {s for s, d in loaded.items() if d["sel"]["tier_a"]}
        failed = {s for s, d in loaded.items() if d["failed"]}
        best = sorted(d["sel"]["best_sharpe"] for d in loaded.values() if d["sel"]["best_sharpe"] is not None)
        sd = null_sharpe_sd(loaded)
        out += ["", f"- Seeds run: {len(loaded)} of {len(null_seeds)}. Tier A non-empty: {len(nonempty)}; seeds "
                f"with any failed configuration: {len(failed)}; counted against the null proof (either): "
                f"{len(nonempty | failed)} (P4.2 criterion: the null proof fails at {NULL_FAIL_AT} or more of 20)."]
        out += _failed_lines(loaded)
        out += [f"- Best SR_d over seeds: min {_fmt(best[0] if best else None)}, median "
                f"{_fmt(statistics.median(best) if best else None)}, max {_fmt(best[-1] if best else None)}; "
                f"values {[round(b, 4) for b in best]}.",
                f"- SD of the null daily Sharpes centred on each configuration's mean: {_fmt(sd['sd_all'])} "
                f"(df-corrected {_fmt(sd['sd_all_df'])}) over {sd['n_all']} (all series; {sd['n_constant']} "
                f"constant no-trade series count as 0) and {_fmt(sd['sd_live'])} (df-corrected "
                f"{_fmt(sd['sd_live_df'])}) over {sd['n_live']} non-constant series; reference 1/sqrt(796) = 0.0354 "
                f"(0.0345 for the uncorrected centred SD over 20 seeds).", ""]
    if planted_seeds:
        rows, loaded = _seed_rows(pdir, planted_seeds, True)
        out += ["## Planted seeds", "",
                "| seed | Tier A | failed | best | best SR_d | oracle SR_d (F15) | funnel | search min |",
                "|---|---|---|---|---|---|---|---|"] + rows
        nonempty = {s for s, d in loaded.items() if d["sel"]["tier_a"]}
        failed = {s for s, d in loaded.items() if d["failed"]}
        per_cfg: dict = {c: 0 for c in IDS}
        for d in loaded.values():
            for c in d["sel"]["tier_a"]:
                per_cfg[c] = per_cfg.get(c, 0) + 1
        orc = [d["oracle"]["sharpe"] for d in loaded.values() if d["oracle"]]
        out += ["", f"- Seeds run: {len(loaded)} of {len(planted_seeds)}. Tier A non-empty: {len(nonempty)}; "
                f"seeds with any failed configuration: {len(failed)}; pass count (Tier A non-empty and no failed "
                f"configuration): {len(nonempty - failed)} (P4.2 criterion: passes at {PLANTED_PASS_AT} or more "
                f"of 20)."]
        out += _failed_lines(loaded)
        out += [f"- Oracle SR_d at F15 on the seeds' own series: mean {_fmt(statistics.fmean(orc) if orc else None)} "
                f"(calibrated target 0.35 in expectation).",
                "- Seeds in which each configuration entered Tier A: "
                + ", ".join(f"{c[4:]} {n}" for c, n in per_cfg.items()), ""]
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text("\n".join(out) + "\n")
    tmp.replace(path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seeds", default="1-20,101-120")
    ap.add_argument("--kind", choices=("null", "planted"), help="required for non-proof seeds")
    ap.add_argument("--proofs-dir", type=Path, default=PROOFS_DIR)
    ap.add_argument("--max-procs", type=int, default=8)
    ap.add_argument("--lgbm-threads", type=int, choices=(4, 8), default=4)
    ap.add_argument("--n", type=int, default=N_PROOF)
    ap.add_argument("--n-oof", type=int, help="tests only: the first N OOF dates")
    ap.add_argument("--summary", type=Path)
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--allow-partial", action="store_true", help="run a subset of the 40 production seeds")
    args = ap.parse_args(argv)
    seeds = parse_seeds(args.seeds)
    prod = [s for s in seeds if s in PRODUCTION_SEEDS]
    if prod and len(prod) != len(seeds):
        raise SystemExit("refused: production and test seeds in one run")
    if prod and (args.n_oof or args.kind or args.n != N_PROOF):
        raise SystemExit("refused: production seeds run at full size, their own kind and N 838 only")
    if prod and sorted(prod) != sorted(PRODUCTION_SEEDS) and not args.allow_partial:
        raise SystemExit("refused: the 40 production seeds run together (P4.2); --allow-partial to override")
    if not prod and (args.summary is None or args.summary.resolve() == SUMMARY.resolve()):
        raise SystemExit("refused: test seeds need their own --summary path")
    summary = args.summary or SUMMARY
    kinds = {s: (args.kind or synth33.kind_of_seed(s)) for s in seeds}
    null_seeds = [s for s in seeds if kinds[s] == "null"]
    planted_seeds = [s for s in seeds if kinds[s] == "planted"]
    if args.summary_only:
        write_summary(args.proofs_dir, summary, null_seeds, planted_seeds)
        return 0
    if not 1 <= args.max_procs <= 8:
        raise SystemExit("--max-procs must be 1..8 (P5 thread cap)")
    if os.nice(0) < 10:
        os.nice(10 - os.nice(0))
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[var] = "1"
    check_manifest(args.proofs_dir, seeds, args)
    log(f"proofs: seeds {seeds} under {args.proofs_dir}; max-procs {args.max_procs}, lgbm threads "
        f"{args.lgbm_threads}; N {args.n}")
    for s in seeds:
        run_seed(s, kinds[s], args.proofs_dir, args)
        write_summary(args.proofs_dir, summary, null_seeds, planted_seeds)
    log(f"all seeds done; summary {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
