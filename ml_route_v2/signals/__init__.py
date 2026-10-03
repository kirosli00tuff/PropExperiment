"""V2.3 signal library of ML route v2: every K1-K9 member family's decision variable and the
generic features G1-G17 (G18/G19 identifiers are built in ml_route_v2/panel.py).

docs/STAGE_E_ML_V2_DESIGN.md V2.3; contract reports/stage_e11_interfaces.md section 3; family
list reports/stage_e11_briefs/member_inventory.md (54 rows); coverage and readings
reports/stage_e11_signal_coverage.md.

- REGISTRY: name -> SignalSpec, in a fixed order (pooled ports CP1-CP3, members K1..K8, K9's
  announcement-day flag k9_anncday (V23 item 8; signals/k9.py), generic G1..G17).
- EXCLUDED: family id -> the logged reason it enters as no feature.
- FAMILY_SIGNALS: each of the 54 inventory families -> the signal names that carry it ((): an
  EXCLUDED family). The 21 port families map to the pooled port signals (lead ruling); K2-aucpre-01
  and K2-aucpost-01 share one event and its two signals; K9-anncday-01 maps to k9_anncday, a
  "flag" spec (not normalized), added here by name since only "member" specs are collected
  automatically (V23 item 8).
- ALWAYS_APPLICABLE: signals whose applicability is 1 on every decision row by construction (their
  app_ column is left out of the panel's feature_cols, reading PN-1).
- compute_signals(ctx, names): raw_<name>, app_<name>, avail_<name> per signal, with the V2.2
  signal-leg roll-blackout rule applied centrally (signals._core.apply_leg_blackout with
  ctx.blackout: on a roll-blackout date of a root a signal reads other than the row's own price
  path, the signal is not applicable; the row is kept); assert_causal has run on the result.
- assert_causal(frame, rows): raises CausalityError when any present value is available after its
  row's decision time (or has no availability), or a frame breaks the contract.
"""

from __future__ import annotations

from collections.abc import Sequence
from types import MappingProxyType

import numpy as np
import pandas as pd

from ml_route_v2.signals import generic, k1, k2, k3, k4, k5, k6, k7, k8, k9, ports
from ml_route_v2.signals._core import (
    CausalityError,
    SignalContext,
    SignalInputMissing,
    SignalSpec,
    apply_leg_blackout,
)

_ALL: tuple[SignalSpec, ...] = (*ports.SPECS, *k1.SPECS, *k2.SPECS, *k3.SPECS, *k4.SPECS,
                                *k5.SPECS, *k6.SPECS, *k7.SPECS, *k8.SPECS, *k9.SPECS,
                                *generic.SPECS)
if len({s.name for s in _ALL}) != len(_ALL):
    raise ImportError("duplicate signal names in the V2.3 library")

REGISTRY = MappingProxyType({s.name: s for s in _ALL})

EXCLUDED = MappingProxyType({
    "K5-fomc-01": (
        "not available at any decision time: the FOMC 5-minute move s = close(13:04) - "
        "close(12:59) is known at 13:05 CT (strategy/members/k5/fomc.py:39-40), after the last "
        "metals decision time 12:50 CT (V2.2), so its most recent value on the same trade date is "
        "never available at t"),
    "K6-wasdepost-01": (
        "not available at any decision time: the WASDE 5-minute move R = close(11:14) - "
        "close(10:59) is known at 11:15 CT (strategy/members/k6/wasdepost.py:44-45), after the "
        "last grain decision time 11:00 CT (V2.2), so its most recent value on the same trade "
        "date is never available at t"),
    # K9-anncday-01 left this table in E.12 (V23 item 8): the EC-K9 calendar for 2019-2024 is
    # built from official pages in the freeze session (signals/k9.py)
})


def _family_signals() -> dict[str, tuple[str, ...]]:
    out: dict[str, list[str]] = {fam: list(names) for fam, names in ports.FAMILIES.items()}
    for s in _ALL:
        if s.kind == "member" and s.family not in ports.PORT_SIGNALS:
            out.setdefault(s.family, []).append(s.name)
    for fam, names in k2.SHARED.items():
        out.setdefault(fam, []).extend(names)
    for s in k9.SPECS:  # a "flag" spec of a member family (V23 item 8)
        out.setdefault(s.family, []).append(s.name)
    for fam in EXCLUDED:
        out[fam] = []
    return {k: tuple(v) for k, v in out.items()}


FAMILY_SIGNALS = MappingProxyType(_family_signals())
ALWAYS_APPLICABLE = frozenset(ports.ALWAYS_APPLICABLE | generic.ALWAYS_APPLICABLE)


def _check_frame(name: str, frame: pd.DataFrame, rows: pd.DataFrame) -> None:
    if list(frame.columns) != ["value", "applicable", "avail_ts_ns"]:
        raise CausalityError(f"{name}: columns {list(frame.columns)}")
    if not frame.index.equals(rows.index):
        raise CausalityError(f"{name}: the frame is not aligned to the decision rows")
    if frame["avail_ts_ns"].dtype != np.int64:
        raise CausalityError(f"{name}: avail_ts_ns is {frame['avail_ts_ns'].dtype}, not int64")


def compute_signals(ctx: SignalContext, names: Sequence[str] | None = None) -> pd.DataFrame:
    """raw_<name>, app_<name>, avail_<name> for each signal (REGISTRY order when ``names`` is
    None), aligned to ctx.rows, after the V2.2 leg roll-blackout rule (module docstring);
    assert_causal has run on it."""
    names = tuple(REGISTRY) if names is None else tuple(names)
    unknown = [n for n in names if n not in REGISTRY]
    if unknown:
        raise KeyError(f"unknown signals: {unknown}")
    cols: dict[str, np.ndarray] = {}
    for name in names:
        spec = REGISTRY[name]
        frame = spec.fn(ctx)
        _check_frame(name, frame, ctx.rows)
        frame, n_blanked = apply_leg_blackout(spec, frame, ctx)
        if n_blanked and name in ALWAYS_APPLICABLE:
            raise CausalityError(f"{name}: the V2.2 leg roll-blackout rule blanks {n_blanked} rows "
                                 "of an always-applicable signal, whose app_ flag is no feature")
        cols[f"raw_{name}"] = frame["value"].to_numpy(np.float64)
        cols[f"app_{name}"] = frame["applicable"].to_numpy(np.float64)
        cols[f"avail_{name}"] = frame["avail_ts_ns"].to_numpy(np.int64)
    out = pd.DataFrame(cols, index=ctx.rows.index)
    assert_causal(out, ctx.rows)
    return out


def signal_names(frame: pd.DataFrame) -> tuple[str, ...]:
    return tuple(c[4:] for c in frame.columns if c.startswith("raw_"))


def assert_causal(signal_frame: pd.DataFrame, rows: pd.DataFrame) -> None:
    """Every present value is available at or before its row's decision time; a not-applicable
    value is 0; applicability is 0 or 1. Raises CausalityError naming the signals and counts."""
    t = rows["decision_ts_ns"].to_numpy(np.int64)
    if not signal_frame.index.equals(rows.index):
        raise CausalityError("the signal frame is not aligned to the decision rows")
    bad = []
    for name in signal_names(signal_frame):
        raw = signal_frame[f"raw_{name}"].to_numpy(np.float64)
        app = signal_frame[f"app_{name}"].to_numpy(np.float64)
        avail = signal_frame[f"avail_{name}"].to_numpy(np.int64)
        present = np.isfinite(raw)
        late = present & ((avail > t) | (avail < 0))
        odd_app = ~np.isin(app, (0.0, 1.0))
        leak_na = (app == 0) & (raw != 0)
        if late.any() or odd_app.any() or leak_na.any():
            bad.append(f"{name} (late {int(late.sum())}, applicable not 0/1 "
                       f"{int(odd_app.sum())}, non-zero while not applicable {int(leak_na.sum())})")
    if bad:
        raise CausalityError("signal values not causal at t: " + "; ".join(bad))


__all__ = [
    "ALWAYS_APPLICABLE", "EXCLUDED", "FAMILY_SIGNALS", "REGISTRY", "CausalityError",
    "SignalContext", "SignalInputMissing", "SignalSpec", "assert_causal", "compute_signals",
    "signal_names",
]
