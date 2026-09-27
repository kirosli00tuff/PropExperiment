"""E.ML-test's entry (M5 step 5, M6, M7.6, M7.8, M9 row 4): every frozen route rule, once, on the
research window, through the Stage E engine and the runner's trip and series code.

    uv run python -m ml_route.test --route-dir <E.ML-train out dir> \
        --route-manifest-sha256 <sha256 of the committed route_manifest.json> \
        --research-root data/processed --out-dir <new dir> --harness-sha256 <sha256>

ORDER (each step refuses by name; nothing is read before step 1, no bar before step 6):
1. ``screening.harness_freeze.preflight(--harness-sha256)``; its return goes into every output.
2. M7.8's scope: the harness manifest lists every ml_route module and every M7 test
   (``ml_route.freeze_scope.check_harness_scope``).
3. The frozen route (M5 step 5, M7.6): route_manifest.json hashes to --route-manifest-sha256 and
   to its own body hash, and was made under this harness; every ledger chain verifies and its
   fits equal the manifest's; every selected model file hashes to its recorded sha256
   (``verify_model_file``); every surrogate tree in the candidates files hashes to the manifest's;
   M5 step 4 re-run on the candidates' survivors gives exactly the manifest's rules; each rule
   file hashes to its rule_sha256 (``rule_spec_from_json``), equals the kept rule, agrees with its
   manifest entry and names the manifest's model, tree and harness; RULES.md is the rendering of
   the rules; the rules directory holds nothing else. Then M6's training-window accounting
   (``ml_route.accounting``) is computed from the verified ledgers.
4. Frozen inputs: the vehicle and cost tables (sha256-checked) and the release calendar; all
   three hashes equal the manifest's, and the calendar covers the research window.
5. Every rule's exposure runs are planned and their legs checked (lead ruling OC-P: one run per
   exposure with ONE traded leg, its vehicle, plus its price path and F16 lead as signal legs;
   each leg a recorded research parquet sha256); the output directory is new.
6. Per rule: every leg's research bars (``data.stage_e_bars.load_research_leg``, hash-checked,
   holdout rows refused); per exposure, its run's member window (D4, UR-1), D9's coverage on
   the D6 day session, the Stage E engine with ``StageERules`` (D8 costs, the D9 constraint set,
   D9.5a), the trips and D9's floor labels (``screening.stage_e_runner``), the decisions and the
   exposure's own series in net ticks per contract of its vehicle (the per-exposure null
   series). Then the rule's daily series (OC-P, M5 step 1): on each date, the mean over the
   exposures with rows on that date of their daily values, the values in NULL_CRITERIA_E 3's
   unit (the exposure's net USD at its q_c / (q_c x tick value) of the rule's primary leg,
   ML-A15); the same mean in M5's own sigma_X,d units is recorded beside it (descriptive, so no
   second research-window read is ever needed to switch units). D.1's daily moments and the
   daily t (``harvey_liu_zhu_verdict``) of the rule's series. One record per rule.
7. The summary: M6's trial accounting (one trial per tested rule; the training-window DSR and PBO
   beside every rule) and the route family's research-window figures the frozen text fixes (the
   Sharpe variance over the tested rules' daily Sharpes, ML-A15; PBO on 8 contiguous blocks).
   What it leaves open is written as a named "not computed" entry, never guessed (user
   questions, lead ruling on Q-T1..Q-T4): Holm at alpha = 0.05 / (K + 1) (K and the p-value
   construction are not frozen inputs of this job), DSR at the cumulative program N (N at the
   time of the test has no frozen source), the composite verdict (the Stage E runner has none),
   and the per-exposure null test (its bootstrap seed uses a member ordinal a route rule does
   not have).

READINGS (in the summary; accepted or open in reports/stage_e2b_g4_mltest_worker.md):
- RT-1: the legs and trading windows of ml_route.stage_e_adapter (one traded vehicle per run,
  price-path and lead signal legs, D6 day session).
- RT-2: a rule excluded by D9's coverage check or refused by the engine is not tested and adds
  nothing to N; it is listed by name.
- RT-3: the family PBO puts the tested rules on the union of their series dates, zeros elsewhere.
- RT-4 (lead ruling on RT-4): an exposure "has rows" on a window date of its run when the
  rule's wrapper has a decision with complete features there (training's rows less the target,
  unknown at a decision). Route rules are tested as ordinary members (NULL_CRITERIA_E 3, U6), so
  the member convention governs the series dates: every research-window date after the runner's
  exclusions (the union of the exposure runs' member windows), zeros on dates without a trip.
  On a date where at least one exposure has rows the value is M5's mean over those exposures;
  on a window date where none has rows (the F17 warm-up included) it is 0.0, and the count of
  such dates is recorded.
- RT-5: the rule is the member for D9's coverage check: if any exposure run's leg is below 0.95,
  the rule is excluded before screening; an engine-refused case in any run refuses the rule.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

SUMMARY_SCHEMA = "ml_route_test_summary/1"
RECORD_SCHEMA = "ml_route_test_record/1"
NOT_COMPUTED = "not computed"


class RouteTestRefusal(RuntimeError):
    """E.ML-test cannot run as frozen; the case is named."""


def _preflight(expected: str) -> str:
    from screening.harness_freeze import preflight

    return preflight(expected)


def _prepare_process() -> None:
    from compute.platform import apply_thread_limits, lower_priority

    lower_priority()
    apply_thread_limits(1)


# -------------------------------------------------------------- the frozen route ----
@dataclass(frozen=True)
class FrozenRoute:
    route_dir: Path
    manifest: dict
    manifest_sha256: str
    rules: tuple[dict, ...]  # in the manifest's order


def _refuse(what: str) -> RouteTestRefusal:
    return RouteTestRefusal(f"REFUSED: {what}")


def _load_manifest(route_dir: Path, expected_sha256: str, harness: str) -> tuple[dict, str]:
    from ml_route.ledger import canonical, sha256_bytes

    path = route_dir / "route_manifest.json"
    if not path.is_file():
        raise _refuse(f"{path} does not exist")
    raw = path.read_bytes()
    sha = sha256_bytes(raw)
    if sha != expected_sha256:
        raise _refuse(f"route_manifest.json hashes to {sha[:12]}, the committed manifest is "
                      f"{expected_sha256[:12]}")
    manifest = json.loads(raw)
    body = {k: v for k, v in manifest.items() if k != "manifest_body_sha256"}
    if sha256_bytes(canonical(body)) != manifest.get("manifest_body_sha256"):
        raise _refuse("route_manifest.json's body no longer hashes to its manifest_body_sha256")
    if manifest.get("harness_sha256") != harness:
        frozen = str(manifest.get("harness_sha256"))[:12]
        raise _refuse(f"the route was frozen under harness {frozen}, this run's is "
                      f"{harness[:12]} (M7.8)")
    return manifest, sha


def _check_models_and_trees(route_dir: Path, manifest: dict, harness: str) -> list[dict]:
    from ml_route.ledger import canonical, sha256_bytes, verify_model_file
    from ml_route.manifest import ledger_fits, load_candidates

    if ledger_fits(route_dir) != manifest["fits"]:  # verify_chain on every ledger first
        raise _refuse("the ledgers' fits differ from the manifest's")
    for _key, sel in sorted(manifest["selected"].items()):
        verify_model_file(route_dir / "models" / sel["model_file"], sel["model_sha256"])
    candidates = load_candidates(route_dir)
    survivors: list[dict] = []
    for (ch, h), cand in candidates.items():
        key = f"{ch}_{h}"
        trees = [{"cluster": s["cluster"], "tree_sha256": sha256_bytes(canonical(s["tree"]))}
                 for s in cand["surrogates"]]
        if trees != manifest["surrogates"].get(key):
            raise _refuse(f"candidates/{key}.json: surrogate trees differ from the manifest's")
        if cand.get("model_sha256") != manifest["selected"][key]["model_sha256"]:
            raise _refuse(f"candidates/{key}.json names another model than the manifest")
        if cand.get("harness_sha256") != harness:
            raise _refuse(f"candidates/{key}.json was made under another harness")
        survivors += cand["survivors"]
    return survivors


def _check_rules(route_dir: Path, manifest: dict, harness: str, survivors: list[dict]
                 ) -> tuple[dict, ...]:
    from ml_route.rule_wrapper import rule_spec_from_json
    from ml_route.surrogate import keep_per_cluster, render_entry

    kept = keep_per_cluster(survivors)
    entries = manifest["rules"]
    if [r["rule_sha256"] for r in kept] != [e["rule_sha256"] for e in entries]:
        raise _refuse("M5 step 4 on the candidates' survivors does not give the manifest's rules")
    rules_dir = route_dir / "rules"
    want = {f"{e['rule_sha256']}.json" for e in entries} | {"RULES.md"}
    have = {p.name for p in rules_dir.iterdir()} if rules_dir.is_dir() else set()
    if have != want:
        raise _refuse(f"rules/ holds {sorted(have - want)} beyond, and lacks {sorted(want - have)}"
                      " of, the manifest's rules")
    rules = []
    for entry, kept_rule in zip(entries, kept, strict=True):
        rule = json.loads((rules_dir / f"{entry['rule_sha256']}.json").read_text(encoding="utf-8"))
        rule_spec_from_json(rule)  # RuleIntegrityError on any change after hashing
        if rule != kept_rule or rule["rule_sha256"] != entry["rule_sha256"]:
            raise _refuse(f"rule {entry['rule_sha256'][:12]}: the file differs from the kept rule")
        if any(rule[f] != entry[f] for f in ("cluster", "challenger", "horizon")):
            raise _refuse(f"rule {entry['rule_sha256'][:12]}: differs from its manifest entry")
        key = f"{rule['challenger']}_{rule['horizon']}"
        prov = rule["provenance"]
        trees = {s["cluster"]: s["tree_sha256"] for s in manifest["surrogates"][key]}
        if (prov.get("model_sha256") != manifest["selected"][key]["model_sha256"]
                or prov.get("surrogate_sha256") != trees.get(rule["cluster"])
                or prov.get("harness_sha256") != harness):
            raise _refuse(f"rule {entry['rule_sha256'][:12]}: its provenance (model, tree, "
                          "harness) differs from the manifest")
        rules.append(rule)
    rendered = "".join(render_entry(r) + "\n" for r in rules)
    if (rules_dir / "RULES.md").read_text(encoding="utf-8") != rendered:
        raise _refuse("rules/RULES.md is not the rendering of the frozen rules")
    return tuple(rules)


def load_frozen_route(route_dir: Path, manifest_sha256: str, harness: str) -> FrozenRoute:
    """Step 3: every hash of the frozen route, or a named refusal (HashChainError,
    RuleIntegrityError or RouteTestRefusal)."""
    route_dir = Path(route_dir)
    manifest, sha = _load_manifest(route_dir, manifest_sha256, harness)
    survivors = _check_models_and_trees(route_dir, manifest, harness)
    return FrozenRoute(route_dir, manifest, sha,
                       _check_rules(route_dir, manifest, harness, survivors))


# --------------------------------------------------------------- frozen inputs ----
@dataclass(frozen=True)
class RouteTestInputs:
    products: Mapping
    costs: Mapping
    events: Any  # ml_route.inputs.EventCalendar


def load_test_inputs(manifest: Mapping) -> RouteTestInputs:
    """Step 4: the frozen tables and calendar, each hash equal to the manifest's record."""
    from ml_route.constants import COSTS_SHA256, RESEARCH_WINDOW, VEHICLES_SHA256
    from ml_route.inputs import load_event_calendar, load_products, load_vehicle_costs

    products = load_products()
    costs = load_vehicle_costs(products)
    events = load_event_calendar(products)
    recorded = manifest["inputs"]
    for name, now in (("costs_sha256", COSTS_SHA256), ("vehicles_sha256", VEHICLES_SHA256),
                      ("event_calendar_sha256", events.sha256)):
        if recorded.get(name) != now:
            raise _refuse(f"{name}: the route was trained with {str(recorded.get(name))[:12]}, "
                          f"the frozen input is now {now[:12]}")
    events.require_coverage(RESEARCH_WINDOW[0], RESEARCH_WINDOW[1], "the research window")
    return RouteTestInputs(products, costs, events)


def _leg_inputs(legs: Sequence) -> dict:
    """One exposure run's frozen leg inputs (OC-P: exactly one traded leg, a Stage E vehicle;
    every leg needs its recorded research parquet sha256)."""
    from screening.stage_e_frozen import leg_inputs, load_frozen_tables

    traded = [leg.root for leg in legs if leg.traded]
    if len(traded) != 1:
        raise _refuse(f"an exposure run needs exactly one traded leg, got {traded} (OC-P)")
    tables = load_frozen_tables()
    out = {leg.root: leg_inputs(leg.root, traded=leg.traded, tables=tables) for leg in legs}
    missing = sorted(r for r, li in out.items() if li.research_parquet_sha256 is None)
    if missing:
        raise _refuse(f"no recorded research parquet sha256 for {missing}")
    return out


# -------------------------------------------------------------------- one rule ----
def _moments_and_t(values: Sequence[float]) -> dict:
    from funnel.multiple_comparisons import harvey_liu_zhu_verdict
    from ml_route.accounting import moments

    m = moments(list(values))
    if m["sd"] <= 0 or m["n"] < 2:
        return {"moments": m, "daily_t": {"status": "undefined", "reason": "sd = 0 or n < 2"}}
    return {"moments": m, "daily_t": {"status": "computed",
                                      **harvey_liu_zhu_verdict(m["mean"], m["sd"], m["n"])}}


def rule_daily_series(values: Sequence[Mapping], rows: Sequence[set], window_dates: Sequence
                      ) -> tuple[list, list[float]]:
    """OC-P / M5 step 1 on the member convention (RT-4 ruling): on every window date, the mean
    over the exposures with rows on that date of their daily values (0 for a date with rows and
    no trade), and 0.0 on a window date where no exposure has rows."""
    if len(values) != len(rows):
        raise ValueError("one value map and one row set per exposure")
    dates = sorted(set(window_dates))
    outside = set().union(*rows) - set(dates) if rows else set()
    if outside:
        raise ValueError(f"rows on {len(outside)} dates outside the window, e.g. {min(outside)}")
    out = []
    for d in dates:
        vals = [float(v.get(d, 0.0)) for v, r in zip(values, rows, strict=True) if d in r]
        out.append(sum(vals) / len(vals) if vals else 0.0)
    return dates, out


@dataclass(frozen=True)
class ExposureRun:
    """One exposure's engine run, before the rule's series is combined."""

    record: dict
    rows: set  # window dates with a decision with complete features ("rows", RT-4)
    window: tuple  # the run's member window dates
    primary_units: Mapping  # date -> net USD at q_c / (q_c x tick value of the primary leg)
    sigma_units: Mapping  # date -> sum of trips' net vehicle ticks per contract / sigma_X,d


def _sigma_by_date(frame: Any, path_root: str, products: Mapping, trade_dates: Sequence
                   ) -> dict:
    """sigma_X,d of the price path on each trade date (vehicle ticks; causal, as the wrapper's)."""
    import pandas as pd

    from ml_route.features import Bars, build_daily
    from ml_route.stage_e_adapter import session_times

    bars = Bars(path_root, frame["ts_event"].to_numpy(np.int64),
                frame["open"].to_numpy(np.float64), frame["high"].to_numpy(np.float64),
                frame["low"].to_numpy(np.float64), frame["close"].to_numpy(np.float64),
                frame["volume"].to_numpy(np.float64), frame["instrument_id"].to_numpy(np.int64),
                pd.to_datetime(frame["trade_date"]).to_numpy().astype("datetime64[D]"))
    spec = products[path_root]
    daily = build_daily(bars, spec, session_times(path_root, spec.group, trade_dates))
    return {d.astype(object): float(s) for d, s in zip(daily.dates, daily.sigma, strict=True)}


def run_exposure(rule: dict, plan: Any, inputs: Mapping, frames: Mapping, tests: RouteTestInputs,
                 releases: Any, primary: str) -> ExposureRun | dict:
    """One exposure's engine run (OC-P). Returns the run, or the record of an exposure that is
    excluded by D9's coverage (``{"status": "excluded_before_screening", ...}``)."""
    from data.stage_e_bars import RESEARCH
    from ml_route.stage_e_adapter import build_exposure_member
    from screening import stage_e_rules
    from screening import stage_e_stats as st
    from screening.stage_e_align import member_coverage, member_window
    from screening.stage_e_engine import run_engine
    from screening.stage_e_runner import LABEL_COVERAGE, extract_trips, floor_labels, trade_rate

    legs = plan.legs
    mine = {leg.root: frames[leg.root] for leg in legs}
    mw = member_window(mine, RESEARCH)
    if not mw.dates:
        raise _refuse(f"{plan.path_root}: the research window is empty after exclusions")
    if not releases.covers(mw.dates):
        raise _refuse(f"{plan.path_root}: the release calendar does not cover the window")
    member = build_exposure_member(rule, plan, tests.products, tests.costs, tests.events,
                                   {r: frames[r].trade_dates for r in plan.paths_read},
                                   {r: frames[r].roll_blackout for r in plan.paths_read})
    coverage = member_coverage(mine, mw.dates, member.trading_windows)
    record: dict[str, Any] = {
        "path_root": plan.path_root, "vehicle": plan.vehicle, "q_c": plan.exposure.q_c,
        "legs": [{"root": leg.root, "traded": leg.traded} for leg in legs],
        "bars": {r: {"path": Path(f.path).name, "sha256": f.sha256, "rows": len(f.frame)}
                 for r, f in mine.items()},
        "window_dates": {"n": len(mw.dates), "first": mw.dates[0], "last": mw.dates[-1],
                         "excluded": {k: list(v) for k, v in mw.excluded.items()}},
        "coverage": {r: {"present": c.present, "expected": c.expected, "ratio": c.ratio,
                         "passes": c.passes} for r, c in coverage.items()},
    }
    if not all(c.passes for c in coverage.values()):
        return {**record, "status": "excluded_before_screening", "labels": [LABEL_COVERAGE]}
    rules = stage_e_rules.StageERules(inputs, frozenset(mw.dates), frozenset(mw.blackout_union),
                                      releases)
    result = run_engine({r: f.frame for r, f in mine.items()}, member, legs, rules)
    trips = extract_trips(result)
    rate = trade_rate(result, trips)
    window = set(mw.dates)
    rows = {d.trade_date for d in member.decisions if d.features_complete
            and d.trade_date in window}
    own = st.daily_series_from_trips(
        f"{member.name}", plan.vehicle,
        [st.Trip(t.trade_date, t.net_usd, t.contracts) for t in trips], mw.dates)
    usd: dict = {}
    for t in trips:
        usd[t.trade_date] = usd.get(t.trade_date, 0.0) + t.net_usd
    in_primary = st.daily_series_from_leg_dollars(member.name, primary, usd, mw.dates,
                                                  len(trips))
    sigma = _sigma_by_date(frames[plan.path_root].frame, plan.path_root, tests.products,
                           frames[plan.path_root].trade_dates)
    tick_usd = st.frozen_epsilon(plan.vehicle).tick_value_usd
    sig_units: dict = {}
    for t in trips:
        s = sigma.get(t.trade_date, float("nan"))
        if not np.isfinite(s) or s <= 0:
            raise _refuse(f"{plan.path_root} {t.trade_date}: a trip on a date without sigma_X,d")
        sig_units[t.trade_date] = (sig_units.get(t.trade_date, 0.0)
                                   + t.net_usd / (t.contracts * tick_usd) / s)
    dec = member.decisions
    record.update(
        status="run", labels=list(floor_labels(rate)), trade_rate=rate,
        engine={"bars": result.bars_processed, "minutes": result.minutes_processed,
                "accounts_started": result.accounts_started, "counters": dict(result.counters)},
        decisions={"decision_times": len(dec), "complete": sum(d.features_complete for d in dec),
                   "fired": sum(d.fired for d in dec), "acted": sum(d.acted for d in dec)},
        rows_dates=sorted(rows),
        series_own_vehicle={"unit": "net ticks per contract per day of the exposure's vehicle "
                                    "(NULL_CRITERIA_E 3; the per-exposure null series)",
                            "dates": list(own.dates), "values": list(own.values),
                            "n_trips": own.n_trips, **_moments_and_t(own.values)})
    return ExposureRun(record, rows, tuple(mw.dates),
                       dict(zip(in_primary.dates, in_primary.values, strict=True)), sig_units)


def run_rule(rule: dict, plans: Sequence, tests: RouteTestInputs, research_root: Path) -> dict:
    """Step 6 for one rule: each exposure's own engine run (OC-P), then the rule's series."""
    from data.stage_e_bars import load_research_leg
    from screening import stage_e_rules
    from screening.stage_e_engine import EngineRefusedCase
    from screening.stage_e_runner import LABEL_COVERAGE

    label = f"route_rule_{rule['rule_sha256'][:12]}"
    shas: dict[str, str] = {}
    for plan, inputs in plans:
        for leg in plan.legs:
            shas[leg.root] = inputs[leg.root].research_parquet_sha256
    frames = {r: load_research_leg(r, Path(research_root), expected_sha256=sha)
              for r, sha in shas.items()}
    releases = stage_e_rules.load_release_calendar()
    if releases.sha256 != tests.events.sha256:
        raise _refuse(f"{label}: the engine's release calendar is not the route's")
    primary = plans[0][0].vehicle
    record: dict[str, Any] = {
        "schema": RECORD_SCHEMA, "rule_sha256": rule["rule_sha256"], "label": label,
        "cluster": rule["cluster"], "challenger": rule["challenger"], "horizon": rule["horizon"],
        "primary_vehicle": primary, "release_calendar_sha256": releases.sha256,
        "aggregation": "OC-P: one engine run per exposure; the rule's daily value is the mean over "
                       "the exposures with rows on that date (M5 step 1, ML-A10)",
    }
    runs: list = []
    try:
        for plan, inputs in plans:
            runs.append(run_exposure(rule, plan, inputs, frames, tests, releases, primary))
    except EngineRefusedCase as exc:
        record.update(status="refused_case", refusal=f"{plans[len(runs)][0].path_root}: {exc}",
                      labels=[], exposures=[r.record if isinstance(r, ExposureRun) else r
                                            for r in runs])
        return record
    exposures = [r.record if isinstance(r, ExposureRun) else r for r in runs]
    record["exposures"] = exposures
    if any(not isinstance(r, ExposureRun) for r in runs):  # RT-5: the rule is the member
        record.update(status="excluded_before_screening", labels=[LABEL_COVERAGE])
        return record
    window = sorted(set().union(*(r.window for r in runs)))
    dates, values = rule_daily_series([r.primary_units for r in runs], [r.rows for r in runs],
                                      window)
    _, sig_values = rule_daily_series([r.sigma_units for r in runs], [r.rows for r in runs],
                                      window)
    no_rows = sum(1 for d in dates if not any(d in r.rows for r in runs))
    labels = sorted({lab for r in runs for lab in r.record["labels"]})
    record.update(
        status="run", labels=labels,
        series={"unit": f"net ticks per contract per day of the primary vehicle {primary}: each "
                        "exposure's daily net USD at its q_c / (q_c x tick value of the primary) "
                        "(NULL_CRITERIA_E 3, ML-A15), then M5's mean over the exposures with "
                        "rows on the date (OC-P)",
                "dates": dates, "values": values,
                "n_trips": sum(r.record["trade_rate"]["n_trips"] for r in runs),
                "exposures_with_rows": [sum(d in r.rows for r in runs) for d in dates],
                "window_dates": len(dates), "window_dates_without_rows": no_rows,
                "first_date_with_rows": next((d for d in dates
                                              if any(d in r.rows for r in runs)), None)},
        statistics=_moments_and_t(values),
        series_m5_sigma={"unit": "sigma_X,d units per day: each trip's net vehicle ticks per "
                                 "contract / sigma_X,d of its price path, summed per exposure "
                                 "and date, then M5's mean (M5 step 1's own unit; descriptive)",
                         "values": sig_values, **_moments_and_t(sig_values)})
    return record


# --------------------------------------------------------------------- summary ----
def _not_computed(reason: str) -> dict:
    return {"status": NOT_COMPUTED, "reason": reason}


def route_family(records: Sequence[dict]) -> dict:
    """Step 7's research-window figures over the tested rules (ML-A15, RT-3)."""
    from ml_route.accounting import pbo

    tested = [r for r in records if r["status"] == "run"]
    sharpes = [r["statistics"]["moments"]["sharpe"] for r in tested]
    out: dict[str, Any] = {
        "tested_rules": [r["rule_sha256"] for r in tested],
        "sharpe_variance_over_tested_rules": (statistics.pvariance(sharpes) if sharpes
                                              else None),
    }
    if len(tested) >= 2:
        dates = sorted({d for r in tested for d in r["series"]["dates"]})
        matrix = np.array([[dict(zip(r["series"]["dates"], r["series"]["values"],
                                     strict=True)).get(d, 0.0) for d in dates] for r in tested])
        out["pbo_research_window"] = pbo(matrix)
    else:
        out["pbo_research_window"] = {"status": "degenerate",
                                      "reason": "PBO needs at least 2 tested rules"}
    out["holm"] = {
        **_not_computed(
            "Holm across the route's tested rules at alpha = 0.05 / (K + 1) (V6, ML-A14): K + 1 "
            "is screening.stage_e_stats.k_from_tiers(tiers, route_tested=True), the clusters "
            "with a non-empty Tier A plus the route family (at most 9), and the alpha is "
            "screening.stage_e_stats.holm_alpha_k(K + 1); the clusters' tiers when the route is "
            "tested and the one-sided p-value construction for route rules are not frozen "
            "inputs of this job (question for the user)"),
        "k_function": "screening.stage_e_stats.k_from_tiers(tiers, route_tested=True)",
        "alpha_function": "screening.stage_e_stats.holm_alpha_k",
        "alpha_rule": "0.05 / (K + 1), K = clusters with a non-empty Tier A (review F-4)"}
    out["dsr_at_program_n"] = _not_computed(
        "DSR > 0.95 at the cumulative program N: N at the time of the test has no frozen source "
        "this job can read; the Sharpe inputs are in each record (question for the lead)")
    out["composite_verdict"] = _not_computed(
        "the Stage E runner has no composite verdict (robust zero-edge gate and drift "
        "sub-checks) yet (question for the lead)")
    out["nulls_per_exposure"] = _not_computed(
        "NULL_CRITERIA_E 3 seeds each member's bootstrap with its ordinal in the hashed list; a "
        "route rule has none (question for the lead); per-exposure series are in each record")
    return out


def _write_once(obj: dict, out_dir: Path, name: str) -> Path:
    from screening.stage_e_runner import write_record

    return write_record(obj, out_dir, name)


def run_test(route_dir: Path, route_manifest_sha256: str, research_root: Path, out_dir: Path,
             harness_sha256: str) -> dict:
    harness = _preflight(harness_sha256)  # FIRST: before any file is read
    _prepare_process()
    from ml_route import freeze_scope
    from ml_route.accounting import route_training_accounting
    from ml_route.stage_e_adapter import exposure_plans

    freeze_scope.check_harness_scope()
    route = load_frozen_route(Path(route_dir), route_manifest_sha256, harness)
    training = route_training_accounting(route.route_dir, route.manifest)
    tests = load_test_inputs(route.manifest)
    plans = []
    for rule in route.rules:
        plans.append((rule, [(plan, _leg_inputs(plan.legs))
                             for plan in exposure_plans(rule, tests.products)]))
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise _refuse(f"{out_dir} is not empty: E.ML-test runs once (M9) and writes once")
    records = []
    for rule, rule_plans in plans:
        record = run_rule(rule, rule_plans, tests, Path(research_root))
        key = f"{rule['challenger']}_{rule['horizon']}"
        record.update(harness_sha256=harness, route_manifest_sha256=route.manifest_sha256,
                      training_window=training["selected"][key],
                      created_utc=datetime.now(UTC).isoformat(timespec="seconds"))
        _write_once(record, out_dir / "rules", rule["rule_sha256"])
        records.append(record)
    tested = [r["rule_sha256"] for r in records if r["status"] == "run"]
    summary = {
        "schema": SUMMARY_SCHEMA, "harness_sha256": harness,
        "route_manifest_sha256": route.manifest_sha256,
        "research_root": str(research_root),
        "readings": ["RT-1", "RT-2", "RT-3", "RT-4", "RT-5"],
        "rules": [{"rule_sha256": r["rule_sha256"], "cluster": r["cluster"],
                   "challenger": r["challenger"], "horizon": r["horizon"],
                   "status": r["status"], "labels": r.get("labels", []),
                   "window_dates": r.get("series", {}).get("window_dates"),
                   "window_dates_without_rows": r.get("series", {}).get(
                       "window_dates_without_rows")} for r in records],
        "warm_up_finding": "window dates on which no exposure of a rule had rows (the F17 "
                           "warm-up of about 139 trade dates included) enter the rule's series "
                           "as 0.0 (lead ruling on RT-4); counted per rule above, for the user",
        "trial_accounting": {
            "rule": "M6: each distilled rule is one trial and adds 1 to the program's cumulative "
                    "N when it is tested",
            "program_trials_added": len(tested), "tested": tested,
            "not_tested": [{"rule_sha256": r["rule_sha256"], "status": r["status"]}
                           for r in records if r["status"] != "run"],
            "training_window_search": route.manifest.get("trial_counts"),
            "training_window": training},
        "route_family": route_family(records),
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    _write_once(summary, out_dir, "route_test_summary")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--route-dir", type=Path, required=True)
    parser.add_argument("--route-manifest-sha256", required=True)
    parser.add_argument("--research-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--harness-sha256", required=True)
    args = parser.parse_args(argv)
    run_test(args.route_dir, args.route_manifest_sha256, args.research_root, args.out_dir,
             args.harness_sha256)
    return 0


if __name__ == "__main__":
    sys.exit(main())
