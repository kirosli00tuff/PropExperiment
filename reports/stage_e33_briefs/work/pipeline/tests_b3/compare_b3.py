"""E.33 B3 agreement harness (prompt B3, protocol P4 G7): Coder-A (pipeline/) against Coder-B (implB/).

Families compared on the 20 B3 dates (rule in reports/stage_e33_STATE.md, 14:45: OOF = the 796 dates sorted;
idx = numpy.random.default_rng(20261028).choice(796, 20, replace=False); dates = sorted(OOF[idx])):

- labels (INTERFACE 4.2), per (label, date), joined on i:
  exact columns (EXACT_LABEL_COLS): i, t_ns, entry_ok, row_ok, y, n_long, n_short, span_end_ns and every per-side
  outcome field (made, net, entry_ns, exit_ns, flags). Float columns compare exactly (a == b, or both NaN).
  w: |a - b| <= 1e-12 * max(|a|, |b|), or both NaN (a float mean of 1/c_m; the summation order may differ).
- features (INTERFACE 4.1), per date, joined on i: date and t_ns exactly; the 59 feature columns with
  |a - b| <= max(1e-9 * max(|a|, |b|), 1e-12) (G7: 1e-9 relative, 1e-12 absolute near 0), or both NaN
  (NaN cells are also counted separately: G3 says invalid features are 0, never NaN).
- sigma: sigma_ZM(D) (ticks) from A's features _day, B's features _day and B's label builder _day (B's own sigma
  when its features did not exist), compared with the feature rule. sigma_ZS and sigma_ZL too when both feature
  _day files exist. sigma is a feature-layer scale, not an outcome, so its values may be printed.

INTERFACE rule 1: on real data this script prints and reports COUNTS and mismatch LOCATIONS only. No statistic of
label values (class shares, means of nets) is computed. The mismatching cells with both values go only to
DERIVED/b3/mismatches_<run>.parquet (the brief's equality-comparison record); they are never printed.

Usage (repo root):
  uv run python reports/stage_e33_briefs/work/pipeline/tests_b3/compare_b3.py --run r1 \
      [--families labels,features,sigma] [--a-labels DIR] [--b-labels DIR] [--a-features DIR] [--b-features DIR]
      [--dates b3|D1,D2,...] [--labels F05,...] [--md PATH]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
if str(PIPE) not in sys.path:
    sys.path.insert(0, str(PIPE))

import cal33  # noqa: E402
import guard33 as g  # noqa: E402

DERIVED = g.DERIVED
WORK = PIPE.parent
RUNS_DIR = WORK / "b3_runs"  # per-run tables; B3_agreement.md is the summary with diagnoses
B3_SEED = 20261028
N_B3 = 20

LABELS = ("F05", "F15", "F30", "F60", "T15", "T30")
FEATURE_COLS = tuple(
    [f"C_{k}" for k in range(1, 16)]
    + [f"F1_{k}" for k in range(1, 9)]
    + [f"F2_{k}" for k in range(1, 12)]
    + [f"F3_{k}" for k in range(1, 13)]
    + [f"F4_{k}" for k in range(1, 14)]
)
assert len(FEATURE_COLS) == 59
SIDE_COLS = ("made", "net", "entry_ns", "exit_ns", "flags")
EXACT_LABEL_COLS = (
    "t_ns", "entry_ok", "row_ok", "y", "n_long", "n_short", "span_end_ns",
    *[f"long_{c}" for c in SIDE_COLS], *[f"short_{c}" for c in SIDE_COLS],
)
LABEL_COLS = ("i", *EXACT_LABEL_COLS[:6], "w", *EXACT_LABEL_COLS[6:])
FEAT_REL, FEAT_ABS = 1e-9, 1e-12
W_REL = 1e-12
ROW_COL = "__row__"  # a row present on one side only


def b3_dates() -> list[str]:
    oof = sorted(cal33.oof_dates())
    if len(oof) != 796:
        raise SystemExit(f"expected 796 OOF dates, got {len(oof)}")
    idx = np.random.default_rng(B3_SEED).choice(len(oof), N_B3, replace=False)
    return sorted(oof[int(k)].isoformat() for k in idx)


# ---- cell rules (pure; unit-tested in tests_b4/test_compare_b3.py) ----

def eq_exact(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Exact equality; for floats NaN == NaN counts as equal."""
    if a.dtype.kind == "f" or b.dtype.kind == "f":
        af, bf = a.astype(np.float64), b.astype(np.float64)
        return (af == bf) | (np.isnan(af) & np.isnan(bf))
    return a == b


def eq_feature(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """G7: |a - b| <= max(1e-9 max(|a|, |b|), 1e-12), or both NaN."""
    af, bf = a.astype(np.float64), b.astype(np.float64)
    with np.errstate(invalid="ignore"):
        tol = np.maximum(FEAT_REL * np.maximum(np.abs(af), np.abs(bf)), FEAT_ABS)
        ok = np.abs(af - bf) <= tol
    both_nan = np.isnan(af) & np.isnan(bf)
    same_inf = np.isinf(af) & (af == bf)
    return ok | both_nan | same_inf


def eq_weight(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Weights: |a - b| <= 1e-12 max(|a|, |b|), or both NaN (exact zero equals zero)."""
    af, bf = a.astype(np.float64), b.astype(np.float64)
    with np.errstate(invalid="ignore"):
        ok = np.abs(af - bf) <= W_REL * np.maximum(np.abs(af), np.abs(bf))
    return ok | (np.isnan(af) & np.isnan(bf))


# ---- frame comparison ----

@dataclass
class Tally:
    agree: dict[str, int] = field(default_factory=dict)
    disagree: dict[str, int] = field(default_factory=dict)
    rows_with_mismatch: int = 0
    rows: int = 0

    def add(self, col: str, n_ok: int, n_bad: int) -> None:
        self.agree[col] = self.agree.get(col, 0) + n_ok
        self.disagree[col] = self.disagree.get(col, 0) + n_bad


def _fmt(v: object) -> str:
    if isinstance(v, (float, np.floating)):
        return repr(float(v))
    if isinstance(v, (np.integer,)):
        return str(int(v))
    return str(v)


def compare_frames(
    a: pd.DataFrame, b: pd.DataFrame, rules: dict[str, str], key: str = "i"
) -> tuple[Tally, list[dict]]:
    """Join on key; apply rule per column ('exact', 'feature', 'weight'). Returns the tally and the mismatch
    cells as dicts (key, column, a, b as strings). Rows on one side only are mismatches of column __row__."""
    tally = Tally()
    cells: list[dict] = []
    for name, df in (("A", a), ("B", b)):
        if df[key].duplicated().any():
            raise ValueError(f"side {name}: duplicate {key}")
    ka, kb = set(a[key].tolist()), set(b[key].tolist())
    for k in sorted(ka - kb):
        cells.append({key: int(k), "column": ROW_COL, "a": "present", "b": "absent"})
    for k in sorted(kb - ka):
        cells.append({key: int(k), "column": ROW_COL, "a": "absent", "b": "present"})
    tally.add(ROW_COL, len(ka & kb), len(ka ^ kb))
    m = a.merge(b, on=key, how="inner", suffixes=("_a", "_b"))
    tally.rows = len(m)
    bad_any = np.zeros(len(m), dtype=bool)
    keys = m[key].to_numpy()
    for col, rule in rules.items():
        if col == key:
            continue
        ca, cb = f"{col}_a", f"{col}_b"
        if ca not in m.columns or cb not in m.columns:
            missing = [s for s, c in (("A", ca), ("B", cb)) if c not in m.columns]
            tally.add(col, 0, len(m))
            cells.append({key: -1, "column": col, "a": "missing column" if "A" in missing else "",
                          "b": "missing column" if "B" in missing else ""})
            continue
        va, vb = m[ca].to_numpy(), m[cb].to_numpy()
        fn = {"exact": eq_exact, "feature": eq_feature, "weight": eq_weight}[rule]
        ok = fn(va, vb)
        tally.add(col, int(ok.sum()), int((~ok).sum()))
        bad_any |= ~ok
        for j in np.flatnonzero(~ok):
            cells.append({key: int(keys[j]), "column": col, "a": _fmt(va[j]), "b": _fmt(vb[j])})
    tally.rows_with_mismatch = int(bad_any.sum())
    return tally, cells


# ---- locating inputs ----

def _sha_dir(root: Path) -> Path:
    """A folder of per-date files directly, or the single <sha12> subfolder holding manifest.json."""
    if (root / "manifest.json").exists() and not any(
        p.is_dir() and (p / "manifest.json").exists() for p in root.iterdir()
    ):
        return root
    subs = sorted(p for p in root.iterdir() if p.is_dir() and (p / "manifest.json").exists())
    if len(subs) != 1:
        raise SystemExit(f"{root}: {len(subs)} code folders with manifest.json; pass the folder explicitly")
    return subs[0]


def _manifest_sha(folder: Path) -> str:
    mp = folder / "manifest.json"
    if not mp.exists():
        return "?"
    m = json.loads(mp.read_text())
    return str(m.get("code_sha12", "?"))


def _read(path: Path) -> pd.DataFrame:
    return pd.read_parquet(g.check_path(path))


# ---- families ----

def compare_labels(a_root: Path, b_root: Path, dates: list[str], labels: list[str]) -> dict:
    per_label: dict[str, Tally] = {}
    per_date: dict[tuple[str, str], tuple[int, int, int]] = {}
    missing: list[str] = []
    cells: list[dict] = []
    rules = {c: ("weight" if c == "w" else "exact") for c in LABEL_COLS}
    for lab in labels:
        tl = Tally()
        for d in dates:
            pa, pb = a_root / lab / f"{d}.parquet", b_root / lab / f"{d}.parquet"
            if not pa.exists() or not pb.exists():
                missing.append(f"{lab} {d}: " + ("A missing " if not pa.exists() else "")
                               + ("B missing" if not pb.exists() else ""))
                continue
            t, c = compare_frames(_read(pa), _read(pb), rules)
            for col in set(t.agree) | set(t.disagree):
                tl.add(col, t.agree.get(col, 0), t.disagree.get(col, 0))
            tl.rows += t.rows
            tl.rows_with_mismatch += t.rows_with_mismatch
            per_date[(lab, d)] = (t.rows, t.rows_with_mismatch, sum(t.disagree.values()))
            for x in c:
                cells.append({"family": "labels", "label": lab, "date": d, **x})
        per_label[lab] = tl
    return {"per_label": per_label, "per_date": per_date, "missing": missing, "cells": cells}


def compare_features(a_root: Path, b_root: Path, dates: list[str]) -> dict:
    rules: dict[str, str] = {"date": "exact", "t_ns": "exact"}
    rules.update({c: "feature" for c in FEATURE_COLS})
    tot = Tally()
    per_date: dict[str, tuple[int, int, int]] = {}
    nan_cells = {"A": 0, "B": 0}
    missing: list[str] = []
    cells: list[dict] = []
    for d in dates:
        pa, pb = a_root / f"{d}.parquet", b_root / f"{d}.parquet"
        if not pa.exists() or not pb.exists():
            missing.append(f"{d}: " + ("A missing " if not pa.exists() else "")
                           + ("B missing" if not pb.exists() else ""))
            continue
        fa, fb = _read(pa), _read(pb)
        for name, df in (("A", fa), ("B", fb)):
            cols = [c for c in FEATURE_COLS if c in df.columns]
            nan_cells[name] += int(np.isnan(df[cols].to_numpy(dtype=np.float64)).sum())
            extra = [c for c in df.columns if c not in ("date", "i", "t_ns", *FEATURE_COLS)]
            order = [c for c in df.columns if c in FEATURE_COLS]
            if extra or order != list(FEATURE_COLS):
                missing.append(f"{d}: side {name} schema differs (extra {extra}, order ok "
                               f"{order == list(FEATURE_COLS)})")
        t, c = compare_frames(fa, fb, rules)
        for col in set(t.agree) | set(t.disagree):
            tot.add(col, t.agree.get(col, 0), t.disagree.get(col, 0))
        tot.rows += t.rows
        tot.rows_with_mismatch += t.rows_with_mismatch
        per_date[d] = (t.rows, t.rows_with_mismatch, sum(t.disagree.values()))
        for x in c:
            cells.append({"family": "features", "label": "", "date": d, **x})
    return {"total": tot, "per_date": per_date, "nan_cells": nan_cells, "missing": missing, "cells": cells}


MISSING = "missing"  # no _day file on that side (distinct from a null value)


def _sigma_from(path: Path, keys: tuple[str, ...]) -> float | None | str:
    if not path.exists():
        return MISSING
    obj = json.loads(path.read_text())
    for k in keys:
        if k in obj:
            v = obj[k]
            return None if v is None else float(v)
    return MISSING


def compare_sigma(a_feat: Path | None, b_feat: Path | None, b_lab: Path | None, dates: list[str]) -> list[dict]:
    out = []
    for d in dates:
        row: dict = {"date": d}
        for name, folder in (("A_feat", a_feat), ("B_feat", b_feat)):
            for x in ("zm", "zs", "zl"):
                row[f"{name}_{x}"] = (
                    _sigma_from(folder / "_day" / f"{d}.json", (f"sigma_{x}",)) if folder else MISSING
                )
        row["B_lab_zm"] = (
            _sigma_from(b_lab / "_day" / f"{d}.json", ("sigma_zm_ticks", "sigma_zm")) if b_lab else MISSING
        )
        out.append(row)
    return out


def _sig_eq(a: float | None | str, b: float | None | str) -> str:
    if a == MISSING or b == MISSING:
        return "n/a (file missing)"
    if a is None and b is None:
        return "both null"
    if a is None or b is None:
        return "one null"
    return "agree" if bool(eq_feature(np.array([a]), np.array([b]))[0]) else "DISAGREE"


# ---- report ----

def write_md(path: Path, run: str, meta: dict, lab: dict | None, feat: dict | None,
             sig: list[dict] | None, n_cells: int, cells_path: Path) -> None:
    L: list[str] = []
    L.append(f"# B3 agreement ({run}): Coder-A (pipeline/) vs Coder-B (implB/)")
    L.append("")
    L.append(f"Written by TestCoder-OpusXHigh, {time.strftime('%Y-%m-%d %H:%M %Z')}. Script "
             "reports/stage_e33_briefs/work/pipeline/tests_b3/compare_b3.py. INTERFACE rule 1: counts and "
             "mismatch locations only; the mismatching cells with values are in the parquet named below, never here.")
    L.append("")
    for k, v in meta.items():
        L.append(f"- {k}: {v}")
    L.append(f"- mismatch cells: {n_cells} -> {cells_path}")
    L.append("")
    L.append("Tolerances: labels, classes, flags, made, fill times, n_long, n_short and per-side nets exactly "
             "(a == b, NaN == NaN); w within 1e-12 relative (|a-b| <= 1e-12 max(|a|,|b|); a float mean of 1/c_m); "
             "features |a-b| <= max(1e-9 max(|a|,|b|), 1e-12) (G7), NaN == NaN; rows joined on i "
             f"(`{ROW_COL}` counts rows present on one side only).")
    L.append("")
    if lab is not None:
        L.append("## Labels: disagreeing cells per column (sum over dates; agree / disagree)")
        L.append("")
        labs = list(lab["per_label"])
        L.append("| column | " + " | ".join(labs) + " |")
        L.append("|---|" + "---|" * len(labs))
        for col in (ROW_COL, *[c for c in LABEL_COLS if c != "i"]):
            L.append(f"| {col} | " + " | ".join(
                f"{lab['per_label'][x].agree.get(col, 0)} / {lab['per_label'][x].disagree.get(col, 0)}"
                for x in labs) + " |")
        L.append("| rows joined / rows with any mismatch | " + " | ".join(
            f"{lab['per_label'][x].rows} / {lab['per_label'][x].rows_with_mismatch}" for x in labs) + " |")
        L.append("")
        L.append("## Labels: per date (rows with any mismatch / disagreeing cells; rows joined in brackets)")
        L.append("")
        dates = sorted({d for (_, d) in lab["per_date"]})
        L.append("| date | " + " | ".join(labs) + " |")
        L.append("|---|" + "---|" * len(labs))
        for d in dates:
            parts = []
            for x in labs:
                v = lab["per_date"].get((x, d))
                parts.append("n/a" if v is None else f"{v[1]} / {v[2]} [{v[0]}]")
            L.append(f"| {d} | " + " | ".join(parts) + " |")
        if lab["missing"]:
            L.append("")
            L.append("Missing (label, date) files: " + "; ".join(lab["missing"]))
        L.append("")
    if feat is not None:
        t = feat["total"]
        L.append("## Features: disagreeing cells per column (sum over dates)")
        L.append("")
        L.append(f"Rows joined {t.rows}; rows with any mismatch {t.rows_with_mismatch}; NaN cells A "
                 f"{feat['nan_cells']['A']}, B {feat['nan_cells']['B']}.")
        L.append("")
        L.append("| column | agree | disagree |")
        L.append("|---|---|---|")
        for col in (ROW_COL, "date", "t_ns", *FEATURE_COLS):
            L.append(f"| {col} | {t.agree.get(col, 0)} | {t.disagree.get(col, 0)} |")
        L.append("")
        L.append("| date | rows joined | rows with any mismatch | disagreeing cells |")
        L.append("|---|---|---|---|")
        for d, v in sorted(feat["per_date"].items()):
            L.append(f"| {d} | {v[0]} | {v[1]} | {v[2]} |")
        if feat["missing"]:
            L.append("")
            L.append("Missing or schema notes: " + "; ".join(feat["missing"]))
        L.append("")
    if sig is not None:
        L.append("## sigma_ZM(D), sigma_ZS(D), sigma_ZL(D) (ticks; feature-layer scales, not outcomes)")
        L.append("")
        L.append("| date | A feat zm | B feat zm | B label-builder zm | A vs B feat | A feat vs B lab | "
                 "B feat vs B lab | zs A/B | zl A/B |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for r in sig:
            def f(v: float | None | str) -> str:
                return v if isinstance(v, str) else ("null" if v is None else f"{v:.12g}")
            L.append(
                f"| {r['date']} | {f(r['A_feat_zm'])} | {f(r['B_feat_zm'])} | {f(r['B_lab_zm'])} | "
                f"{_sig_eq(r['A_feat_zm'], r['B_feat_zm'])} | {_sig_eq(r['A_feat_zm'], r['B_lab_zm'])} | "
                f"{_sig_eq(r['B_feat_zm'], r['B_lab_zm'])} | {_sig_eq(r['A_feat_zs'], r['B_feat_zs'])} | "
                f"{_sig_eq(r['A_feat_zl'], r['B_feat_zl'])} |")
        L.append("")
    path.write_text("\n".join(L) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--families", default="labels,features,sigma")
    ap.add_argument("--dates", default="b3")
    ap.add_argument("--labels", default=",".join(LABELS))
    ap.add_argument("--a-labels", default=None)
    ap.add_argument("--b-labels", default=str(DERIVED / "implB" / "labels"))
    ap.add_argument("--a-features", default=None)
    ap.add_argument("--b-features", default=None)
    ap.add_argument("--md", default=None, help="default: work/b3_runs/<run>.md")
    args = ap.parse_args(argv)
    os.nice(10)
    fams = {x.strip() for x in args.families.split(",") if x.strip()}
    dates = b3_dates() if args.dates == "b3" else [x.strip() for x in args.dates.split(",") if x.strip()]
    labels = [x.strip() for x in args.labels.split(",") if x.strip()]
    meta: dict = {"dates": f"{len(dates)} ({'B3 rule seed 20261028' if args.dates == 'b3' else 'given'}): "
                  + ", ".join(dates)}
    a_lab = b_lab = a_feat = b_feat = None
    if "labels" in fams or "sigma" in fams:
        b_lab = Path(args.b_labels)
        b_lab = _sha_dir(b_lab) if b_lab.exists() else None
    if "labels" in fams:
        a_lab = _sha_dir(Path(args.a_labels) if args.a_labels else DERIVED / "labels")
        meta["A labels"] = f"{a_lab} (code_sha12 {_manifest_sha(a_lab)})"
        meta["B labels"] = f"{b_lab} (code_sha12 {_manifest_sha(b_lab) if b_lab else '?'})"
    if "features" in fams or "sigma" in fams:
        pa = Path(args.a_features) if args.a_features else DERIVED / "features"
        pb = Path(args.b_features) if args.b_features else DERIVED / "implB" / "features"
        a_feat = _sha_dir(pa) if pa.exists() else None
        b_feat = _sha_dir(pb) if pb.exists() else None
        meta["A features"] = f"{a_feat} (code_sha12 {_manifest_sha(a_feat) if a_feat else '-'})"
        meta["B features"] = f"{b_feat} (code_sha12 {_manifest_sha(b_feat) if b_feat else '-'})"
    lab = compare_labels(a_lab, b_lab, dates, labels) if "labels" in fams else None
    feat = None
    if "features" in fams:
        if a_feat is None or b_feat is None:
            print("features: a side is missing; skipped", flush=True)
            meta["features"] = "skipped (a side missing)"
        else:
            feat = compare_features(a_feat, b_feat, dates)
    sig = compare_sigma(a_feat, b_feat, b_lab, dates) if "sigma" in fams else None
    cells = (lab["cells"] if lab else []) + (feat["cells"] if feat else [])
    out_dir = DERIVED / "b3"
    out_dir.mkdir(parents=True, exist_ok=True)
    cells_path = out_dir / f"mismatches_{args.run}.parquet"
    cdf = pd.DataFrame(cells, columns=["family", "label", "date", "i", "column", "a", "b"])
    cdf.insert(0, "run", args.run)
    cdf["i"] = cdf["i"].astype("int64")
    cdf.to_parquet(cells_path, index=False)
    md_path = Path(args.md) if args.md else RUNS_DIR / f"{args.run}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    write_md(md_path, args.run, meta, lab, feat, sig, len(cdf), cells_path)
    # stdout: counts only
    if lab:
        for x, t in lab["per_label"].items():
            print(f"labels {x}: rows {t.rows} rows_with_mismatch {t.rows_with_mismatch} "
                  f"cells_disagree {sum(t.disagree.values())}", flush=True)
        if lab["missing"]:
            print(f"labels missing files: {len(lab['missing'])}", flush=True)
    if feat:
        t = feat["total"]
        print(f"features: rows {t.rows} rows_with_mismatch {t.rows_with_mismatch} cells_disagree "
              f"{sum(t.disagree.values())}", flush=True)
    print(f"mismatch cells {len(cdf)} -> {cells_path}; md {md_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
