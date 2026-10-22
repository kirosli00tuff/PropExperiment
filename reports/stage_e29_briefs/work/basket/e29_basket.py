"""Stage E.29 basket model (reports/stage_e29_model.md, sha256 f393759f4af712a8...) on E.28's economic model.

E.28's model files (reports/stage_e28_briefs/work/A3_econ/: A3_funnel.py, A3_models.py, A3_run.py and the
prop_econ code they import) are imported by path, read-only; nothing here edits or copies them. E.28 feeds its
funnel one pair's daily law DayLaw(m, s); this module builds, per firm, basket, rho and edge setting, the combined
daily law of declaration section 3 and feeds it at the same place, on E.28's common random numbers:

  member i:  m_i = T_i (mu_i - c_i) v_i,  s_i = sqrt(T_i) sigma_i v_i       (c_i = c_lim, or c_lim + S_rt market)
  account:   M = sum_i m_i,  S = sqrt(sum_i s_i^2 + 2 rho sum_{i<j} s_i s_j)

E.28 cached evaluations by d = mu - c for one pair; here they are cached by the law (M, S) itself. E.28's search
(bisection on the integer grid index, invariant f(lo) < 0 <= f(hi)) and its grid confirmation (A3_econ.md 2.4,
A3_gridcheck.py) are kept in logic and applied to the grid of k (setting i) or mu_QM (setting ii).

Topstep B3 sensitivity (declaration section 4): on every Topstep funded day at the 2-lot XFA tier, B3 trades without
MGC (QM 7, ZM 7). simulate_xfas_b3 is a thin wrapper that mirrors prop_econ.vec.simulate_xfas day for day and only
chooses, per path and day, which of two laws the day step uses (law A off the tier, law B on it); it reuses
prop_econ's own state, request, stop and finish helpers unchanged.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import resource
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
E28_WORK = REPO / "reports" / "stage_e28_briefs" / "work" / "A3_econ"
E28_JSON = REPO / "reports" / "stage_e28_briefs" / "A3_econ.json"
E28_INPUTS = E28_WORK / "A3_inputs.json"
DECL = REPO / "reports" / "stage_e29_model.md"
DECL_SHA = "f393759f4af712a889646a7a4cdb2c45f2f3b8496a6403be56467de7eb0d8164"
E28_FILES = ("A3_funnel.py", "A3_models.py", "A3_run.py", "A3_inputs.py", "A3_gridcheck.py", "A3_inputs.json")
for _p in (str(REPO), str(E28_WORK)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import A3_funnel as F  # noqa: E402
import A3_run as R  # noqa: E402
from prop_econ.funnel import FunnelError, Policy, callup_after, payout_cap, payout_rules, xfa_phase  # noqa: E402
from prop_econ.rules import SizeRules  # noqa: E402
from prop_econ.types import ShockSet  # noqa: E402
from prop_econ.vec import (  # noqa: E402
    DEFAULT_CHUNK,
    XfaPool,
    _check_shocks,
    _chunk_columns,
    _finish,
    _products,
    _request_payouts,
    _stop_after_payout,
    _XfaOut,
    _XfaState,
    day_step_vec,
    simulate_attempts,
    tier_cap_vec,
)

STEP = 0.01
GRID_N = 400  # k or mu_QM = 0.01 g, g = 0..400 (0 to 4)
GRID_EXT = 1200  # extended alone break-evens, 0 to 12 ticks (declaration section 5)
COARSE, DENSE_BELOW = 10, 10  # A3_gridcheck: 0.10-tick sub-grid, dense 0.10 ticks below each threshold
NEAR_SE, NEAR_USD, NEAR_P = 5.0, 100.0, 0.40  # A3_gridcheck "near the threshold"
T_TOTAL = 20
FIRMS = ("topstep", "lucid", "tradeify", "mffu", "bulenox")
BASKETS: dict[str, tuple[str, ...]] = {"B0": ("QM",), "B1": ("QM", "ZM"), "B2": ("QM", "MGC"),
                                       "B3": ("QM", "ZM", "MGC"), "B4": ("QM", "MNQ")}
RHOS = (0.0, 0.25, 0.5, 0.75)
LOTS = {"QM": 1.0, "ZM": 1.0, "MGC": 0.1, "MNQ": 0.1}  # 10:1 micro-to-mini at all five firms (section 4)
FIRM_CAP_LOTS = {"topstep": 5, "lucid": 4, "tradeify": 4, "mffu": 4, "bulenox": 7}  # section 4
REPORT_K = (100, 150, 200)  # setting (i) reporting points k = 1.0, 1.5, 2.0
REPORT_MU = (50, 100)  # setting (ii): B0's E.28 mu*_lim at the firm, 0.50, 1.00
B3_SENS_DROP = "MGC"  # dropped on Topstep funded days at the 2-lot tier
UNCONFIRMED = "bisection, unconfirmed"


# ----------------------------------------------------------------------------- provenance ----
def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def e28_shas() -> dict[str, str]:
    return {name: sha256_file(E28_WORK / name) for name in E28_FILES} | {"A3_econ.json": sha256_file(E28_JSON)}


# ---------------------------------------------------------------------- baskets (section 2) ----
def trade_split(n: int, total: int = T_TOTAL) -> tuple[int, ...]:
    """T_i = floor(total / n); the remainder goes one trade each to the members in basket order."""
    base = total // n
    rem = total - base * n
    return tuple(base + (1 if i < rem else 0) for i in range(n))


def basket_lots(codes: tuple[str, ...]) -> float:
    return round(sum(LOTS[c] for c in codes), 10)


@dataclass(frozen=True)
class Member:
    code: str
    T: int
    v: float
    sigma: float
    c_lim: float  # F_rt / v (E.28's c_lim)
    s_rt: float  # E.28's S_rt (ticks)

    def cost(self, market: bool) -> float:
        return self.c_lim + self.s_rt if market else self.c_lim

    @property
    def s_usd(self) -> float:
        return math.sqrt(self.T) * self.sigma * self.v


def load_inputs() -> dict[str, Any]:
    return json.loads(E28_INPUTS.read_text())


def make_member(firm: str, code: str, t: int, inputs: dict[str, Any], f_rt_usd: float | None = None) -> Member:
    cand = inputs["candidates"][code]
    pair = next(p for p in inputs["pairs"] if p["firm"] == firm and p["code"] == code)
    fee = pair["F_rt_usd"] if f_rt_usd is None else f_rt_usd
    return Member(code, t, cand["v_usd"], cand["sigma_1m_ticks"], fee / cand["v_usd"], cand["S_rt_ticks"])


def members_for(firm: str, codes: tuple[str, ...], inputs: dict[str, Any],
                split: tuple[int, ...] | None = None) -> tuple[Member, ...]:
    ts = trade_split(len(codes)) if split is None else split
    return tuple(make_member(firm, c, t, inputs) for c, t in zip(codes, ts, strict=True))


# ------------------------------------------------------------------- combined law (section 3) ----
def combined_sd(members: tuple[Member, ...], rho: float) -> float:
    s = [m.s_usd for m in members]
    var = sum(x * x for x in s) + 2.0 * rho * sum(s[i] * s[j] for i in range(len(s)) for j in range(i + 1, len(s)))
    return math.sqrt(var)


def combined_law(members: tuple[Member, ...], mus: list[float], rho: float, market: bool) -> F.DayLaw:
    """M = sum_i T_i (mu_i - c_i) v_i (each term in E.28's operation order: T * d * v) and S of section 3."""
    m = sum(mem.T * (mu - mem.cost(market)) * mem.v for mem, mu in zip(members, mus, strict=True))
    return F.DayLaw(m=m, s=combined_sd(members, rho))


def edge_mus(members: tuple[Member, ...], setting: str, x: float, mu_star: dict[str, float] | None) -> list[float]:
    """Setting (i): mu_i = k mu*_i (alone break-even); setting (ii): QM at mu_QM, every other member at 0."""
    if setting == "i":
        assert mu_star is not None
        return [x * mu_star[m.code] for m in members]
    return [x if m.code == "QM" else 0.0 for m in members]


# --------------------------------------------------------------- Topstep B3 sensitivity wrapper ----
def _trade_day_b3(st: _XfaState, skip: np.ndarray, d: int, cols: tuple[np.ndarray, ...], out: _XfaOut,
                  r0: int, rules: SizeRules, policy: Policy, phase: Any, pr: Any, prods: Any,
                  lots: float) -> int:
    """prop_econ.vec._trade_day, except that paths whose tier cap is below the basket's lots trade law B
    (product 1) that day instead of law A (product 0). Returns the number of such path-days."""
    za, wa, zb, wb = cols
    x = rules.xfa
    d_open = st.balance - st.floor
    if (d_open <= 0).any():
        bad = int(r0 + st.ids[np.argmax(d_open <= 0)])
        raise FunnelError(f"row {bad} day {d}: D_open <= 0 after a payout")
    cap_minis = tier_cap_vec(st.close, phase)
    low = cap_minis < lots
    z = np.where(low, zb[d, st.ids], za[d, st.ids])
    w = np.where(low, wb[d, st.ids], wa[d, st.ids])
    pnl, breach = day_step_vec(st.balance, st.floor, low.astype(np.int64), z, w, policy, cap_minis,
                               phase.dll_usd, prods)
    st.balance = st.balance + pnl
    if breach.any():
        _finish(st, breach, out, r0, d + 1, F.XFA_BREACH)
        pnl, skip = pnl[~breach], skip[~breach]
    add = ~skip
    if pr.path == "standard":
        st.win_n = st.win_n + (add & (pnl >= pr.winning_day_usd))
    st.win_net = np.where(add, st.win_net + pnl, st.win_net)
    st.win_days = st.win_days + add
    st.win_best = np.where(add, np.maximum(st.win_best, pnl), st.win_best)
    trailed = np.maximum(st.floor, np.minimum(st.balance - x.mll_usd, x.mll_floor_lock_usd))
    st.floor = np.where(st.fixed, st.floor, trailed)
    st.close = st.balance
    return int(low.sum())


def simulate_xfas_b3(sh_a: ShockSet, sh_b: ShockSet, rules: SizeRules, policy: Policy, lots: float,
                     chunk: int = DEFAULT_CHUNK) -> tuple[XfaPool, int, int]:
    """prop_econ.vec.simulate_xfas with a day-dependent law: (pool, path-days at the low tier, path-days traded)."""
    phase = xfa_phase(rules, policy)
    max_days, max_pay = policy.xfa_max_days, policy.max_payouts
    _check_shocks(sh_a, max_days)
    _check_shocks(sh_b, max_days)
    if sh_a.n_paths != sh_b.n_paths:
        raise ValueError("law A and law B shock sets differ in paths")
    pr, cap = payout_rules(rules, policy), payout_cap(rules, policy)
    stop_after = callup_after(rules)
    n_all = sh_a.n_paths
    out = _XfaOut(pay_days=np.full((n_all, max_pay), -1, dtype=np.int32), pay_gross=np.zeros((n_all, max_pay)),
                  npay=np.zeros(n_all, dtype=np.int32), total=np.zeros(n_all),
                  first=np.full(n_all, -1, dtype=np.int32), end_day=np.zeros(n_all, dtype=np.int32),
                  reason=np.zeros(n_all, dtype=np.int8), end_balance=np.zeros(n_all),
                  overflow=np.zeros(n_all, dtype=bool))
    prods = _products(sh_a.products + sh_b.products)
    low_days = all_days = 0
    for r0 in range(0, n_all, chunk):
        r1 = min(r0 + chunk, n_all)
        za, wa, _ = _chunk_columns(sh_a, r0, r1, max_days)
        zb, wb, _ = _chunk_columns(sh_b, r0, r1, max_days)
        st = _XfaState(r1 - r0, rules.xfa.start_balance_usd, rules.xfa.mll_usd)
        for d in range(max_days):
            if st.ids.size == 0:
                break
            skip = _request_payouts(st, d, out, r0, rules, policy, pr, cap)
            skip = _stop_after_payout(st, skip, d, out, r0, rules, stop_after)
            if st.ids.size == 0:
                break
            all_days += st.ids.size
            low_days += _trade_day_b3(st, skip, d, (za, wa, zb, wb), out, r0, rules, policy, phase, pr, prods,
                                      lots)
        if st.ids.size:
            _finish(st, np.ones(st.ids.size, dtype=bool), out, r0, max_days, F.XFA_HORIZON)
    pool = XfaPool(payout_days=out.pay_days, payout_gross=out.pay_gross, n_payouts=out.npay,
                   total_gross=out.total, first_payout_day=out.first, end_day=out.end_day,
                   end_reason=out.reason, end_balance=out.end_balance, overflow=out.overflow)
    return pool, low_days, all_days


def simulate_pools_b3(model: F.FirmModel, law_a: F.DayLaw, law_b: F.DayLaw, d_att: F.Draws, d_xfa: F.Draws,
                      lots: float, chunk: int = F.CHUNK) -> tuple[F.Pools, int, int]:
    """A3_funnel.simulate_pools for Topstep with the funded stage on simulate_xfas_b3 (the Combine is
    unaffected: its 5-lot cap holds every basket)."""
    if model.xfa_rules is None or model.eval_trail != "eod":
        raise ValueError("the B3 sensitivity applies to Topstep's XFA only")
    pol = F.size1_policy(model.attempt_max_days)
    a_parts, x_parts, low, alld = [], [], 0, 0
    for r0 in range(0, d_att.z.shape[0], chunk):
        sh, _ = F.shock_set(d_att, law_a, slice(r0, r0 + chunk))
        a_parts.append(simulate_attempts(sh, model.eval_rules, pol))
    for r0 in range(0, d_xfa.z.shape[0], chunk):
        sh_a, _ = F.shock_set(d_xfa, law_a, slice(r0, r0 + chunk))
        sh_b, _ = F.shock_set(d_xfa, law_b, slice(r0, r0 + chunk))
        pool, lo, al = simulate_xfas_b3(sh_a, sh_b, model.xfa_rules, pol, lots)
        x_parts.append(pool)
        low, alld = low + lo, alld + al
    return F.Pools(F._concat_attempts(a_parts), F._concat_xfas(x_parts)), low, alld


# ------------------------------------------------------------------------------ evaluation ----
Point = F.DayLaw | tuple[F.DayLaw, F.DayLaw]


def law_key(p: Point) -> tuple[float, ...]:
    if isinstance(p, tuple):
        return (round(p[0].m, 9), round(p[0].s, 9), round(p[1].m, 9), round(p[1].s, 9))
    return (round(p.m, 9), round(p.s, 9))


class LawEval:
    """Evaluations of one firm's funnel keyed by the daily law (M, S) (or a pair of laws for the B3 sensitivity),
    on E.28's common random numbers. A3_run.PairEval.at in all but the key."""

    def __init__(self, model: F.FirmModel, draws: tuple[F.Draws, F.Draws], idx: tuple[np.ndarray, np.ndarray],
                 lots: float | None = None) -> None:
        self.model, (self.da, self.dx), (self.att, self.xfa), self.lots = model, draws, idx, lots
        self.cache: dict[tuple[float, ...], dict[str, Any]] = {}
        self.n_evals = 0

    def compute(self, p: Point, need_p: bool) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        if isinstance(p, tuple):
            pools, lo, al = simulate_pools_b3(self.model, p[0], p[1], self.da, self.dx, float(self.lots))
            extra = {"low_tier_days": lo, "funded_days": al, "low_tier_share": lo / al if al else None}
            law = p[0]
        else:
            pools = F.simulate_pools(self.model, p, self.da, self.dx)
            law = p
        st = F.cycle_stats(self.model, pools, self.att, self.xfa)
        pr = F.campaign_p_reach(self.model, pools) if need_p else None
        self.n_evals += 1
        return {"m": law.m, "s": law.s, "ev": st.ev, "se": st.se, "ev_ex_api": st.ev_ex_api, "p10k": pr,
                "stats": st.__dict__, **extra}

    def at(self, p: Point, need_p: bool) -> dict[str, Any]:
        key = law_key(p)
        r = self.cache.get(key)
        if r is None or (need_p and r["p10k"] is None):
            r = self.compute(p, need_p)
            self.cache[key] = r
        return r


class Line:
    """One lattice g = 0..n of one cell: point_fn(g) gives the law at x = 0.01 g."""

    def __init__(self, ev: LawEval, point_fn: Callable[[int], Point], n: int = GRID_N) -> None:
        self.ev, self.point_fn, self.n = ev, point_fn, n
        self.pts: dict[int, dict[str, Any]] = {}
        self.src: dict[int, str] = {}
        self.phase = "search"

    def get(self, g: int, need_p: bool) -> dict[str, Any]:
        r = self.ev.at(self.point_fn(g), need_p)
        if g not in self.pts or (need_p and self.pts[g]["p10k"] is None):
            self.src.setdefault(g, self.phase)
        self.pts[g] = r
        return r

    def f(self, g: int, what: str) -> float:
        r = self.get(g, what == "p10k")
        return r["ev"] if what == "ev" else r["p10k"] - 0.5

    def smallest(self, what: str, need_p: bool = True, lo: int = 0, hi: int | None = None) -> int | None:
        """A3_run.PairEval.smallest: smallest g in [lo, hi] with f(g) >= 0, f assumed nondecreasing; None if
        f(hi) < 0. need_p mirrors E.28 (its search computed P10K at every point) for limit cells."""
        hi = self.n if hi is None else hi

        def fv(g: int) -> float:
            r = self.get(g, need_p or what == "p10k")
            return r["ev"] if what == "ev" else r["p10k"] - 0.5

        if fv(hi) < 0:
            return None
        if fv(lo) >= 0:
            return lo
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if fv(mid) >= 0:
                hi = mid
            else:
                lo = mid
        return hi


# ------------------------------------------------------------- grid confirmation (A3 2.4) ----
def _near_ev(r: dict[str, Any]) -> bool:
    return r["ev"] >= -max(NEAR_SE * r["se"], NEAR_USD)


def _fill(line: Line, region: set[int], is_p: bool, p_region: set[int]) -> int:
    filled = 0
    js = sorted(j for j in line.pts if j in region and (not is_p or line.pts[j]["p10k"] is not None))
    for a, b in zip(js, js[1:], strict=False):
        if b - a <= 1:
            continue
        ra, rb = line.pts[a], line.pts[b]
        near = (ra["p10k"] >= NEAR_P or rb["p10k"] >= NEAR_P) if is_p else (_near_ev(ra) or _near_ev(rb))
        if near:
            for j in range(a + 1, b):
                line.get(j, j in p_region)
            filled += 1
    return filled


def _verdict(line: Line, region: set[int], is_p: bool, k: int | None) -> dict[str, Any]:
    top = k if k is not None else line.n + 1
    key = "p10k" if is_p else "ev"
    js = sorted(j for j in line.pts if 0 <= j < top and j in region and line.pts[j][key] is not None)
    if not js:
        return {"n_checked": 0, "violations": [], "confirmed": True}
    vals = [(j, line.pts[j][key]) for j in js]
    thr = 0.5 if is_p else 0.0
    viol = [j for j, x in vals if x >= thr]
    jmax, xmax = max(vals, key=lambda t: t[1])
    out: dict[str, Any] = {"n_checked": len(js),
                           "n_dense_points": sum(1 for j in js if line.src.get(j) == "gridcheck"),
                           "max_below": {"g": jmax, "value": xmax, "se": None if is_p else line.pts[jmax]["se"]},
                           "violations": viol, "confirmed": not viol}
    if viol:
        first = viol[0]
        prev = max([j for j in js if j < first], default=0)
        for j in range(prev, first):
            line.get(j, is_p)
        allv = [j for j in range(0, first + 1) if j in line.pts and line.pts[j][key] is not None
                and line.pts[j][key] >= thr]
        out["corrected_g"] = min(allv)
    return out


def grid_confirm(line: Line, k_ev: int | None, k_p: int | None, with_p: bool) -> dict[str, Any]:
    """A3_gridcheck.check_pair on one lattice: 0.10-tick sub-grid below each threshold, dense 0.10 ticks below
    each threshold found, dense fill of every gap with an end near the threshold, then the verdicts."""
    line.phase = "gridcheck"
    n = line.n
    ev_reg = set(range(0, k_ev if k_ev is not None else n + 1))
    p_reg = set(range(0, k_p if k_p is not None else n + 1)) if with_p else set()
    pts = {j for j in ev_reg | p_reg if j % COARSE == 0}
    if ev_reg:
        pts |= {min(ev_reg), max(ev_reg)}
    if p_reg:
        pts |= {0, max(p_reg)}
    for k in (k_ev, k_p if with_p else None):
        if k is not None:
            pts |= set(range(max(k - DENSE_BELOW, 0), k))
    for j in sorted(pts):
        line.get(j, j in p_reg)
    n_fill = _fill(line, ev_reg, False, p_reg) + (_fill(line, p_reg, True, p_reg) if p_reg else 0)
    checks = {"ev": _verdict(line, ev_reg, False, k_ev)}
    if with_p:
        checks["p10k"] = _verdict(line, p_reg, True, k_p)
    line.phase = "report"
    return {"checks": checks, "n_dense_filled_gaps": n_fill}


def final_g(k: int | None, check: dict[str, Any]) -> int | None:
    return check.get("corrected_g", k)


def fmt_x(g: int | None, n: int = GRID_N) -> float | str:
    return f"> {n // 100}" if g is None else round(g * STEP, 2)


# ---------------------------------------------------------------------------------- cells ----
@functools.lru_cache(maxsize=1)
def _e28_pairs() -> tuple[dict[str, Any], ...]:
    return tuple(json.loads(E28_JSON.read_text())["pairs"])


def e28_pair(firm: str, code: str) -> dict[str, Any]:
    return next(r for r in _e28_pairs() if r["firm"] == firm and r["code"] == code)


def _num(x: Any) -> float | None:
    return None if isinstance(x, str) or x is None else float(x)


def cell_point_fn(firm: str, basket: str, setting: str, rho: float, market: bool, form: str,
                  mu_star: dict[str, float] | None, inputs: dict[str, Any]) -> Callable[[int], Point]:
    codes = BASKETS[basket]
    mem = members_for(firm, codes, inputs)
    if form == "b3_sens":
        keep = tuple(c for c in codes if c != B3_SENS_DROP)
        split_b = tuple(m.T for m in mem if m.code != B3_SENS_DROP)
        mem_b = members_for(firm, keep, inputs, split_b)

        def pt2(g: int) -> Point:
            x = g * STEP
            return (combined_law(mem, edge_mus(mem, setting, x, mu_star), rho, market),
                    combined_law(mem_b, edge_mus(mem_b, setting, x, mu_star), rho, market))
        return pt2

    def pt(g: int) -> Point:
        return combined_law(mem, edge_mus(mem, setting, g * STEP, mu_star), rho, market)
    return pt


def _eval_row(g: int, r: dict[str, Any], src: str) -> dict[str, Any]:
    st = r["stats"]
    row = {"g": g, "x": round(g * STEP, 2), "M": r["m"], "S": r["s"], "ev": r["ev"], "se": r["se"],
           "ev_ex_api": r["ev_ex_api"], "p10k": r["p10k"], "p_pass_attempt": st["p_pass_attempt"],
           "p_any_payout": 1.0 - st["p_no_payout"], "src": src}
    if "low_tier_share" in r:
        row["low_tier_share"] = r["low_tier_share"]
    return row


def _report_row(line: Line, g: int) -> dict[str, Any]:
    r = line.get(g, False)
    st = r["stats"]
    row = {"g": g, "x": round(g * STEP, 2), "ev": r["ev"], "se": r["se"], "p_pass_attempt": st["p_pass_attempt"],
           "p_any_payout": 1.0 - st["p_no_payout"], "mean_attempts": st["mean_attempts"]}
    if "low_tier_share" in r:
        row["low_tier_share_sens"] = r["low_tier_share"]
    return row


def primary_low_share(model: F.FirmModel, law: F.DayLaw, d_xfa: F.Draws, lots: float) -> dict[str, Any]:
    """Share of funded path-days at a tier below the basket's lots, primary form (law A on every day: the
    wrapper with law B = law A is the primary simulation, test e)."""
    pol = F.size1_policy(model.attempt_max_days)
    low = alld = 0
    for r0 in range(0, d_xfa.z.shape[0], F.CHUNK):
        sh, _ = F.shock_set(d_xfa, law, slice(r0, r0 + F.CHUNK))
        _, lo, al = simulate_xfas_b3(sh, sh, model.xfa_rules, pol, lots)
        low, alld = low + lo, alld + al
    return {"low_tier_days": low, "funded_days": alld, "share": low / alld if alld else None}


def run_cell(spec: dict[str, Any], state: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """One cell = firm x basket x rho x edge setting x case (x form). Every quantity of declaration section 6."""
    t0 = time.time()
    firm, basket, setting, case, form = spec["firm"], spec["basket"], spec["setting"], spec["case"], spec["form"]
    rho = 0.0 if spec["rho"] is None else float(spec["rho"])
    market = case == "market"
    codes = BASKETS[basket]
    model = state["models"][firm]
    mem = members_for(firm, codes, inputs)
    mu_star = spec.get("mu_star")
    s_usd = combined_sd(mem, rho)
    base = {**spec, "members": [m.__dict__ | {"s_usd": m.s_usd} for m in mem], "lots": basket_lots(codes),
            "S_usd": s_usd, "MLL_usd": model.mll_usd, "S_over_MLL": s_usd / model.mll_usd}
    if setting == "i" and any(mu_star is None or mu_star.get(c) is None for c in codes):
        return {**base, "status": "n/a", "reason": "a member's alone break-even is above 12 ticks (section 5)",
                "runtime_s": round(time.time() - t0, 2)}
    lots = basket_lots(codes)
    ev = LawEval(model, state["draws"][firm], state["idx"], lots if form == "b3_sens" else None)
    line = Line(ev, cell_point_fn(firm, basket, setting, rho, market, form, mu_star, inputs))
    need_p = not market
    k_ev = line.smallest("ev", need_p)
    k_p = line.smallest("p10k") if not market else None
    out: dict[str, Any] = {}
    if not market:
        st0 = line.get(0, False)["stats"]
        out["cost_per_attempt_usd"] = st0["eval_fees_per_attempt"]
        out["cost_per_attempt_variants"] = {"eval_fees_plus_api": st0["eval_fees_api_per_attempt"],
                                            "all_fees_incl_activation_and_api": st0["all_fees_per_attempt"]}
        out["at_zero_edge"] = {k: st0[k] for k in ("ev", "se", "p_pass_attempt", "mean_attempts", "p_no_payout",
                                                    "mean_cycle_days")}
    bisect_only = spec.get("mode") == "bisection"
    if bisect_only:
        gc = {"status": UNCONFIRMED}
        g_ev, g_p = k_ev, k_p
    else:
        gc = grid_confirm(line, k_ev, k_p, with_p=not market)
        g_ev = final_g(k_ev, gc["checks"]["ev"])
        g_p = final_g(k_p, gc["checks"]["p10k"]) if not market else None
    if not market:
        rep = list(REPORT_K) if setting == "i" else [spec["report_g_b0"], *REPORT_MU]
        out["reporting"] = [_report_row(line, g) for g in rep]
    if firm == "topstep" and basket == "B3" and not market and form == "primary":
        out["low_tier_primary"] = _low_tier_block(line, model, state, lots, g_ev, rep)
    repro: dict[str, Any] = {"status": "skipped (bisection-only mode)"}
    if not bisect_only:
        g_rep = g_ev if g_ev is not None else line.n
        fresh = ev.compute(line.point_fn(g_rep), need_p)
        stored = line.pts[g_rep]
        repro = {"g": g_rep, "ev_cached": stored["ev"], "ev_recomputed": fresh["ev"],
                 "p10k_cached": stored["p10k"], "p10k_recomputed": fresh["p10k"],
                 "equal": fresh["ev"] == stored["ev"] and fresh["p10k"] == stored["p10k"]}
    thr_name = "k_star" if setting == "i" else "mu_star_QM"
    rec = {**base, "status": "computed", thr_name: fmt_x(g_ev),
           "threshold": {"name": thr_name, "value": fmt_x(g_ev), "g": g_ev, "g_bisection": k_ev,
                         "status": UNCONFIRMED if bisect_only else "grid-confirmed"},
           "grid_check": gc, "repro": repro, **out}
    if not market:
        rec["x10K"] = {"name": "k10K" if setting == "i" else "mu10K_QM", "value": fmt_x(g_p), "g": g_p,
                       "g_bisection": k_p, "status": UNCONFIRMED if bisect_only else "grid-confirmed"}
    rec["evaluations"] = [_eval_row(g, line.pts[g], line.src.get(g, "?")) for g in sorted(line.pts)]
    rec["n_evaluations"] = ev.n_evals
    rec["runtime_s"] = round(time.time() - t0, 2)
    rec["maxrss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    return rec


def _low_tier_block(line: Line, model: F.FirmModel, state: dict[str, Any], lots: float, g_ev: int | None,
                    rep: list[int]) -> dict[str, Any]:
    """Primary-form share of Topstep B3 funded days at the 2-lot tier at the threshold and reporting points."""
    dx = state["draws"]["topstep"][1]
    gs = sorted({*([g_ev] if g_ev is not None else []), *rep})
    rows = []
    for g in gs:
        p = line.point_fn(g)
        law = p[0] if isinstance(p, tuple) else p
        rows.append({"g": g, "x": round(g * STEP, 2), **primary_low_share(model, law, dx, lots)})
    return {"rows": rows, "tiers": [list(t) for t in model.xfa_rules.xfa.scaling],
            "boundary": model.xfa_rules.xfa.scaling_boundary, "basket_lots": lots}


def run_alone(firm: str, code: str, state: dict[str, Any], inputs: dict[str, Any],
              bisect_only: bool = False) -> dict[str, Any]:
    """Extended alone break-evens (section 5): E.28's single-pair model (T = 20) on the 0 to 12 tick grid,
    limit and market case, same search and grid confirmation (EV only)."""
    t0 = time.time()
    model = state["models"][firm]
    mem = (make_member(firm, code, T_TOTAL, inputs),)
    ev = LawEval(model, state["draws"][firm], state["idx"])
    res: dict[str, Any] = {"firm": firm, "code": code, "grid_top_ticks": GRID_EXT // 100,
                           "c_lim_ticks": mem[0].c_lim, "c_mkt_ticks": mem[0].cost(True)}
    e28 = e28_pair(firm, code)
    res["e28"] = {"mu_star_lim": e28["mu_star_lim"], "mu_star_mkt": e28["mu_star_mkt"]}
    for case in ("limit", "market"):
        mkt = case == "market"
        line = Line(ev, lambda g, mk=mkt: combined_law(mem, [g * STEP], 0.0, mk), GRID_EXT)
        k = line.smallest("ev", False)
        if bisect_only:
            gc, g = {"status": UNCONFIRMED}, k
        else:
            gc = grid_confirm(line, k, None, with_p=False)
            g = final_g(k, gc["checks"]["ev"])
        res[case] = {"mu_star": fmt_x(g, GRID_EXT), "g": g, "g_bisection": k, "grid_check": gc,
                     "status": UNCONFIRMED if bisect_only else "grid-confirmed",
                     "evaluations": [_eval_row(j, line.pts[j], line.src.get(j, "?")) for j in sorted(line.pts)]}
    res["n_evaluations"] = ev.n_evals
    res["runtime_s"] = round(time.time() - t0, 2)
    res["maxrss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    return res
