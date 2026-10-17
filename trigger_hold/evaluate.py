"""The discovery and confirmation computations on a run context (lead_spec sections 4 and 7).
No guard here: trigger_hold.run checks the freeze, the registration, the stores and writes the
run-once marker before calling these. Roots are loaded one at a time; a refused store marks its
trigger-holds "store refused" (R-B3), never raises.

Discovery reads W_ext only, on a context whose last date is 2019-04-30 (Questions for the lead
Q6), and never a trigger-hold that the power table marks inconclusive by design on W_ext.
Confirmation reads W_cf only, for discovery survivors that pass the power gate at
b = max(2.0, z_{1 - 0.05/S}); the others are INCONCLUSIVE BY DESIGN (gated) or UNCONFIRMABLE ON
OWNED DATA (no W_cf events file or no W_cf book date) and are never read.
"""

from __future__ import annotations

import gc
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from base_rules.common import RunContext, load_or_exclude, lock_rule
from trigger_hold import constants as K
from trigger_hold.book import (
    book_summary,
    buy_hold_returns,
    daily_series,
    prepare_root,
    regressor_on,
    unit_book,
)
from trigger_hold.config import Config, TriggerHold
from trigger_hold.power import nonoverlapping, power_at
from trigger_hold.stats import (
    case_record,
    confirmation_hurdle,
    confirmation_verdicts,
    discovery_survivors,
    dsr,
    dsr_with_variance,
    pbo_cscv,
)
from trigger_hold.trend import load_trend
from trigger_hold.units import BarMarks, book_days, build_units, in_market_fraction, window_for


def read_root(ctx: RunContext, root: str, ths: Sequence[TriggerHold], window: str, *,
              trend_dir: Path = K.TREND_DIR, use_locks: bool = True) -> dict[str, dict]:
    """Every listed trigger-hold of one root on one window (section 4)."""
    notes: dict = {}
    load_counts: Counter = Counter()
    bars = load_or_exclude(ctx, root, load_counts, notes)
    if bars is None:
        return {th.id: {"status": "store refused", "notes": notes} for th in ths}
    locks = lock_rule(ctx, bars) if use_locks else None
    rd = prepare_root(ctx, bars, root, locks=locks)
    src = BarMarks(ctx, bars, root, rd.path.marks)
    staged = {}
    for th in ths:
        ev = th.events_file(window)
        win = window_for(src, window, th.s_x)
        units, ucounts = build_units(src, ev.events if ev else (), win, m=th.m, h=th.h)
        staged[th.id] = (th, win, units, ucounts, book_days(src, win, units))
    del bars, locks, src
    gc.collect()
    trend = load_trend(root, trend_dir)
    bh_counts: Counter = Counter()
    bh = buy_hold_returns(rd, bh_counts)
    out = {}
    for tid, (th, win, units, ucounts, days) in staged.items():
        book = unit_book(rd, units)
        c: Counter = Counter()
        series = daily_series(book, days, c)
        dates = [d for d, _ in series[K.BASE]]
        x1, x2 = regressor_on(trend["T1"], dates), regressor_on(trend["T2"], dates)
        x3 = regressor_on(bh, dates)
        out[tid] = {"status": "read", "root": root, "window": window, "first": str(win.first),
                    "last": str(win.last), "m": th.m, "h": th.h, "units": len(units),
                    "nonoverlapping": nonoverlapping(units), "n_dates": len(dates),
                    "in_market_fraction_units": in_market_fraction(units, dates),
                    "buy_hold_counts": dict(bh_counts),
                    "unit_counts": dict(sorted(ucounts.items())),
                    "book_counters": dict(sorted((book.counters + c).items())),
                    **book_summary(book),
                    "cases": {cs: case_record(series[cs], x1, x2, th.h, x3) for cs in K.CASES},
                    "series": {cs: [[str(d), v] for d, v in series[cs]] for cs in K.CASES}}
    return out


def _read(ctx: RunContext, cfg: Config, ids: Sequence[str], window: str,
          trend_dir: Path) -> dict[str, dict]:
    want = [th for th in cfg.rows if th.id in set(ids)]
    out: dict[str, dict] = {}
    for root in cfg.roots:
        ths = [th for th in want if th.root == root]
        if ths:
            out.update(read_root(ctx, root, ths, window, trend_dir=trend_dir))
    return out


def screen_row(rec: Mapping[str, Any] | None) -> dict[str, Any]:
    if not rec or rec.get("status") != "read":
        return {"p_alpha": None, "t_nw": None, "sharpe": None}
    base = rec["cases"][K.BASE]
    return {"p_alpha": base["alpha"]["p_alpha"], "t_nw": base["alpha"]["t_nw"],
            "sharpe": base["raw"]["sharpe"]}


def base_values(rec: Mapping[str, Any]) -> list[float]:
    return [v for _, v in rec["series"][K.BASE]]


def base_series(rec: Mapping[str, Any]) -> list[tuple[date, float]]:
    return [(date.fromisoformat(d), v) for d, v in rec["series"][K.BASE]]


def discovery(ctx: RunContext, cfg: Config, power: Mapping[str, Any], n_trials: int, *,
              trend_dir: Path = K.TREND_DIR) -> dict[str, Any]:
    rows = power["rows"]
    gated = {th.id: rows[th.id][K.W_EXT]["inconclusive_by_design"] for th in cfg.rows}
    recs = _read(ctx, cfg, [i for i, g in gated.items() if not g], K.W_EXT, trend_dir)
    for i, g in gated.items():
        if g:
            recs[i] = {"status": K.INCONCLUSIVE, "power": rows[i][K.W_EXT]}
    screen = discovery_survivors({i: screen_row(recs.get(i)) for i in cfg.ids})
    read = {i: r for i, r in recs.items() if r.get("status") == "read"}
    return {"phase": "discovery", "window": K.W_EXT, "k": len(cfg.ids), "n_trials": n_trials,
            "trigger_holds": recs, "screen": screen,
            "dsr_descriptive": dsr({i: base_values(r) for i, r in read.items()}, n_trials),
            "pbo_descriptive": pbo_cscv({i: base_series(r) for i, r in read.items()})}


def survivors_from(disc: Mapping[str, Any], cfg: Config) -> list[str]:
    """The survivors re-derived by code from the discovery rows (must equal the stored ones)."""
    screen = discovery_survivors({i: screen_row(disc["trigger_holds"].get(i)) for i in cfg.ids})
    if screen["survivors"] != disc["screen"]["survivors"]:
        raise RuntimeError("the discovery file's survivors differ from the rule's (code error)")
    return list(screen["survivors"])


def confirmation_gate(th: TriggerHold, power: Mapping[str, Any], s: int) -> tuple[str, dict]:
    row = power["rows"][th.id].get(K.W_CF)
    if not th.events.get(K.W_CF) or row is None or row["n_dates"] == 0:
        return K.UNCONFIRMABLE, {"power": row}
    b = confirmation_hurdle(s)
    pw = power_at(b, row["n_dates"])
    info = {"hurdle": b, "power_at_hurdle": pw, "nonoverlapping": row["nonoverlapping"],
            "n_dates": row["n_dates"]}
    if row["nonoverlapping"] < K.MIN_NONOVERLAP or pw < K.POWER_MIN:
        return K.INCONCLUSIVE, info
    return "read", info


def confirmation(ctx: RunContext, cfg: Config, power: Mapping[str, Any],
                 disc: Mapping[str, Any], n_trials: int, *,
                 trend_dir: Path = K.TREND_DIR) -> dict[str, Any]:
    surv = survivors_from(disc, cfg)
    by_id = {th.id: th for th in cfg.rows}
    gates = {i: confirmation_gate(by_id[i], power, len(surv)) for i in surv}
    recs = _read(ctx, cfg, [i for i, (g, _) in gates.items() if g == "read"], K.W_CF, trend_dir)
    disc_read = {i: base_values(r) for i, r in disc["trigger_holds"].items()
                 if r.get("status") == "read"}
    pbo_disc = (disc.get("pbo_descriptive") or {}).get("pbo")
    vrows = {}
    for i in surv:
        g, info = gates[i]
        rec = recs.get(i)
        if g != "read" or rec is None or rec.get("status") != "read":
            vrows[i] = {"status": g if g != "read" else K.UNCONFIRMABLE, "gate": info}
            recs.setdefault(i, {"status": vrows[i]["status"], "gate": info})
            continue
        base, stress = rec["cases"][K.BASE], rec["cases"][K.STRESS]
        d = dsr_with_variance(base_values(rec), disc_read, n_trials)
        rec["dsr"] = d
        vrows[i] = {"status": "read", "gate": info, "p_alpha": base["alpha"]["p_alpha"],
                    "t_nw": base["alpha"]["t_nw"], "sharpe_base": base["raw"]["sharpe"],
                    "sharpe_stress": stress["raw"]["sharpe"], "dsr": d.get("dsr"),
                    "pbo_discovery": pbo_disc}
    return {"phase": "confirmation", "window": K.W_CF, "survivors": surv, "s": len(surv),
            "n_trials": n_trials, "trigger_holds": recs, "verdict_inputs": vrows,
            "verdicts": confirmation_verdicts(vrows)}


__all__ = ["base_series", "base_values", "confirmation", "confirmation_gate", "discovery",
           "read_root", "screen_row", "survivors_from"]
