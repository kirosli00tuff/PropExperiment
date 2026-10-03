"""Stage E.11 Task 4: the v2 portfolio on the frozen Stage E engine (docs/STAGE_E_ML_V2_DESIGN.md
V2.8 "The simulator"). Real frozen products and D8 costs, synthetic bars only
(ml_route.synthetic.synthetic_bars) and a synthetic release calendar.

(a) a single-product schedule at sizes <= q_c through PortfolioRules reproduces the same intents
    through the frozen StageERules fill for fill (with a roll-blackout date: one product, the
    same set); (b) a hand-computed two-product day to the cent; (c) the forced flatten closes
    everything at F; (d) the XFA gate refuses a size above the tier; (e) an MLL breach
    liquidates and the account restarts. Plus the pinned parent methods, the combined MLL audit
    (lead ruling 2026-10-03), the cost beyond q_c (design review D-08a: one extra tick a side
    per contract beyond q_c, to the cent), the per-product roll blackout (V2.2, design fix 8)
    and the member's daily risk budget (design review D-03)."""

from __future__ import annotations

import hashlib
import inspect
from datetime import UTC, date, datetime, time
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from ml_route.synthetic import synthetic_bars
from ml_route_v2.constants import UNIVERSE
from ml_route_v2.simulate import PortfolioRules, build_rules, run_portfolio
from screening.stage_e_engine import AccountStart, DayClose, Fill, IntentRecord, run_engine
from screening.stage_e_frozen import leg_inputs, load_frozen_tables
from screening.stage_e_rules import StageERules, release_calendar_from_dict
from strategy.stage_e.interface import LegSpec, leg_market_intent

CT = ZoneInfo("America/Chicago")
FIRST, DAY, LAST = date(2019, 6, 3), date(2019, 6, 5), date(2019, 6, 6)
SPEC = {"MNQ": ("equity", 0.25, 8000.0), "MGC": ("metals", 0.1, 2000.0),
        "MYM": ("equity", 1.0, 30000.0), "MCL": ("energy", 0.01, 55.0)}
PARENT_OPENING_REFUSAL_SHA256 = "e309ebda558c2748012f0b1263d9f46ba3c2b9499d773d565563b784301ff500"
PARENT_FILL_COST_SHA256 = "14b2ccafa314521a8c00f8dc6004da3a4c7934cb2ebb2e642df8d8d6df3df512"
PARENT_CLOSE_COST_SHA256 = "a4a1ccfe049e658de8fbdfd76a7e85aac8a0f4df796f4d47c0a760c69df1852b"


# ---- fixtures ------------------------------------------------------------------------------
def ct_ns(day: date, hh: int, mm: int) -> int:
    return int(pd.Timestamp(datetime.combine(day, time(hh, mm)), tz=CT).value)


def calendar(releases: list[dict] | None = None):
    raw = {"schema": "stage_e_release_calendar/1",
           "coverage": {"first": "2019-05-01", "last": "2019-07-31"}, "releases": releases or []}
    return release_calendar_from_dict(raw, "e" * 64, "synthetic calendar (Task 4 tests)")


def release(day: date, hh: int, mm: int, roots: list[str], cpi: bool = False) -> dict:
    at = datetime.combine(day, time(hh, mm), tzinfo=CT).astimezone(UTC)
    return {"id": f"r{day}{hh}{mm}", "instant_utc": at.isoformat().replace("+00:00", "Z"),
            "products": roots, "cpi": cpi, "source": "test"}


def flat(root: str, last: date = LAST) -> pd.DataFrame:
    group, tick, p0 = SPEC[root]
    f = synthetic_bars(root, group, FIRST, last, 7, tick, p0)
    return f.assign(open=p0, high=p0, low=p0, close=p0)


def priced(frame: pd.DataFrame, day: date, steps: list[tuple[time, float]]) -> pd.DataFrame:
    """Every bar of ``day`` from each step's CT time on trades flat at that step's price."""
    ct = pd.to_datetime(frame["ts_event"], utc=True).dt.tz_convert(CT).dt.time
    on_day = frame["trade_date"] == day.isoformat()
    out = frame.copy()
    for start, price in steps:
        m = on_day & (ct >= start)
        out.loc[m, ["open", "high", "low", "close"]] = price
    return out


def row(root: str, day: date, t: tuple[int, int], exit_: tuple[int, int], side: int,
        horizon: str = "h60", cost: float = 3.0, edge: float = 1.0, rw: bool = False) -> dict:
    return {"root": root, "cluster": UNIVERSE[root][0], "trade_date": pd.Timestamp(day),
            "decision_ts_ns": ct_ns(day, *t), "horizon": horizon,
            "exit_ts_ns": ct_ns(day, *exit_), "side": side, "r_hat_ticks": 10.0 * side,
            "cost_ticks": cost, "edge_over_cost": edge, "release_window": rw}


def risk(spec: dict[str, tuple[float, float]]) -> pd.DataFrame:
    return pd.DataFrame([{"root": r, "horizon": h, "sigma_ticks": s, "loss_ticks": loss}
                         for r, (s, loss) in spec.items() for h in ("h60", "h120", "hF")])


class Replay:
    """A minimal member that issues given intents at given minutes (keyed by bar open ns)."""

    def __init__(self, intents, roots) -> None:
        self.name = "replay"
        self.trading_windows = {}
        self._by = {}
        for ts, it in intents:
            self._by.setdefault(ts, []).append(it)

    def on_minute(self, view, account):
        return list(self._by.get(view.ts_event_ns, ()))


def fills_on(result, day: date) -> list[Fill]:
    return [f for f in result.events(Fill) if f.trade_date == day]


def ct_of(ns: int) -> time:
    return datetime.fromtimestamp(ns / 1e9, tz=UTC).astimezone(CT).time()


# ---- the override ----------------------------------------------------------------------------
def test_the_overridden_parent_method_is_the_one_reviewed() -> None:
    src = inspect.getsource(StageERules._opening_refusal)
    assert hashlib.sha256(src.encode()).hexdigest() == PARENT_OPENING_REFUSAL_SHA256
    assert "others = [r for r in run.traded if r != root and run.exposure(r)]" in src
    assert "after = {r: run.exposure(r) for r in run.traded}" in src
    for name, sha in (("fill_cost", PARENT_FILL_COST_SHA256),
                      ("close_cost", PARENT_CLOSE_COST_SHA256)):
        parent = inspect.getsource(getattr(StageERules, name))
        assert hashlib.sha256(parent.encode()).hexdigest() == sha, name
    own = {k for k, v in vars(PortfolioRules).items() if callable(v) and not k.startswith("__")}
    # nothing else is overridden; _beyond_q_c is the cost overrides' own helper
    assert own == {"_opening_refusal", "fill_cost", "close_cost", "_beyond_q_c"}
    assert "_beyond_q_c" not in vars(StageERules)


# ---- (a) equivalence with the frozen rules -------------------------------------------------------
def single_product_case():
    last = date(2019, 6, 14)
    frame = synthetic_bars("MNQ", "equity", FIRST, last, 31, 0.25, 8000.0)
    days = sorted(date.fromisoformat(d) for d in frame["trade_date"].unique())
    rel = [release(d, 10, 59, ["MNQ"]) for d in days[2::3]]  # fill guard + event cost at 11:00
    rel.append(release(days[4], 13, 0, ["MNQ"], cpi=True))  # CPI: the micro cap of 3
    rows = []
    for d in days[1:]:
        rows += [row("MNQ", d, (9, 0), (10, 0), 1, edge=2.0),
                 row("MNQ", d, (9, 30), (10, 30), -1),  # meets the open position: skipped
                 row("MNQ", d, (11, 0), (13, 0), -1, "h120"),
                 row("MNQ", d, (13, 0), (15, 8), 1, "hF")]
    return frame, days, calendar(rel), pd.DataFrame(rows)


def frozen_replay(frame, days, cal, run, blackout=frozenset()):
    kw = dict(legs={"MNQ": leg_inputs("MNQ", traded=True)}, window_dates=frozenset(days),
              blackout=frozenset(blackout), releases=cal)
    return run_engine({"MNQ": frame}, Replay(run.intents, ["MNQ"]), (LegSpec("MNQ", True),),
                      StageERules(**kw))


def test_a_single_product_run_matches_the_frozen_rules_fill_for_fill() -> None:
    """At sizes <= q_c (MNQ: 1) the cost override adds nothing; one product's own roll blackout
    is the frozen rules' union, so the per-product check is the same rule."""
    frame, days, cal, sched = single_product_case()
    roll = frozenset({days[6]})
    rk = risk({"MNQ": (200.0, 100.0)})  # one sigma $100 -> 1 contract (115.47 / 100)
    run = run_portfolio({"MNQ": frame}, sched, rk,
                        rules_kwargs={"releases": cal, "product_blackout": {"MNQ": roll}})
    frozen = frozen_replay(frame, days, cal, run, roll)
    assert run.engine_result.ledger == frozen.ledger
    assert run.engine_result.final_state == frozen.final_state
    assert dict(run.engine_result.counters) == dict(frozen.counters)
    fills = run.engine_result.events(Fill)
    assert len(fills) >= 40 and any(f.event_window for f in fills)
    assert {f.qty for f in fills} == {1}  # at q_c
    assert run.engine_result.counters.get("fill_guard_deferral", 0) > 0
    refused = {r.refusal.reason for r in run.engine_result.events(IntentRecord) if r.refusal}
    assert "engine_roll_blackout" in refused
    assert not fills_on(run.engine_result, days[6])  # no entry on the roll date
    reasons = {d.reason for d in run.decisions}
    assert "product_open" in reasons and "" in reasons
    assert {f.reason for f in fills} >= {"strategy", "forced_flatten"}
    assert run.combined_mll_breaches == () and not run.breached_combined  # one product


def test_a_the_member_folds_the_cpi_cap() -> None:
    frame, days, cal, sched = single_product_case()
    run = run_portfolio({"MNQ": frame}, sched, risk({"MNQ": (20.0, 100.0)}),
                        rules_kwargs={"releases": cal})
    cpi_day = [f for f in fills_on(run.engine_result, days[4]) if f.opening
               and ct_of(f.fill_ts_ns) >= time(12, 55)]
    assert [f.qty for f in cpi_day] == [3]  # the member folded D9.12's cap


def test_a_above_q_c_every_fill_pays_exactly_the_extra_ticks() -> None:
    """The same schedule at up to 9 contracts (one sigma $10 -> n_risk 11, the loss cap 500 /
    51.5 -> 9) against the frozen rules: every fill identical except its slippage, which is
    higher by exactly (qty - q_c) x 1 tick x 50 cents (D-08a)."""
    frame, days, cal, sched = single_product_case()
    run = run_portfolio({"MNQ": frame}, sched, risk({"MNQ": (20.0, 100.0)}),
                        rules_kwargs={"releases": cal})
    frozen = frozen_replay(frame, days, cal, run)
    mine, base = run.engine_result.events(Fill), frozen.events(Fill)
    assert len(mine) == len(base) >= 40 and max(f.qty for f in mine) == 9
    key = [(f.root, f.fill_ts_ns, f.side, f.qty, f.price, f.commission_cents, f.reason)
           for f in mine]
    assert key == [(f.root, f.fill_ts_ns, f.side, f.qty, f.price, f.commission_cents, f.reason)
                   for f in base]
    assert [a.slippage_cents - b.slippage_cents for a, b in zip(mine, base, strict=True)] == [
        max(f.qty - 1, 0) * 50 for f in mine]


def test_cost_override_hand_computed_per_fill() -> None:
    bar = SimpleNamespace(open_ts_utc=datetime(2019, 6, 5, 14, 0, tzinfo=UTC),
                          ts_event_ns=ct_ns(DAY, 9, 0))
    for root, tv_cents in (("MNQ", 50), ("ZT", 781.25)):
        rules = build_rules([root], {}, {"releases": calendar(), "window_dates": {DAY}})
        frozen = StageERules(rules.legs, rules.window_dates, rules.blackout, rules.releases)
        q_c = rules.legs[root].vehicle.q_c
        assert q_c == 1
        market = SimpleNamespace(root=root, is_passive=False)
        for qty in (1, 2, 3, 4):
            mine, ev = rules.fill_cost(None, market, bar, qty, "buy", "strategy")
            base, ev0 = frozen.fill_cost(None, market, bar, qty, "buy", "strategy")
            # (qty - q_c) extra ticks, rounded up to the cent: MNQ 50 cents a tick; ZT 781.25
            extra = -(-(qty - q_c) * tv_cents // 1) if qty > q_c else 0
            assert mine.slippage_cents - base.slippage_cents == extra, (root, qty)
            assert (mine.commission_cents, mine.qty_micros, ev) == (base.commission_cents, qty,
                                                                   ev0)
            if qty <= q_c:
                assert mine == base  # at or below q_c the parent's cost, unchanged
            close, _ = rules.close_cost(None, root, bar, qty, "sell")
            close0, _ = frozen.close_cost(None, root, bar, qty, "sell")
            assert close.slippage_cents - close0.slippage_cents == extra
        passive = SimpleNamespace(root=root, is_passive=True)
        assert rules.fill_cost(None, passive, bar, 3, "buy", "strategy") == frozen.fill_cost(
            None, passive, bar, 3, "buy", "strategy")  # a resting order pays no slippage


# ---- (b) the hand-computed two-product day -----------------------------------------------------
@pytest.fixture(scope="module")
def two_product_day():
    mnq = priced(flat("MNQ"), DAY, [(time(9, 30), 8005.00), (time(10, 0), 8010.25)])
    mgc = priced(flat("MGC"), DAY, [(time(10, 0), 1998.5), (time(10, 30), 1995.3)])
    sched = pd.DataFrame([row("MNQ", DAY, (9, 0), (10, 0), 1),
                          row("MGC", DAY, (9, 30), (10, 30), -1)])
    rk = risk({"MNQ": (70.0, 100.0), "MGC": (50.0, 100.0)})
    return run_portfolio({"MNQ": mnq, "MGC": mgc}, sched, rk,
                         rules_kwargs={"releases": calendar()})


def test_b_the_frozen_cost_values_used_by_hand() -> None:
    t = load_frozen_tables().costs
    side = {(r, b.key): b.side_ticks for r in ("MNQ", "MGC") for b in t[r].buckets}
    assert (t["MNQ"].commission_side_cents, t["MGC"].commission_side_cents) == (61, 96)
    assert side[("MNQ", "09:00")]["buy"] == 0.9031496008866111
    assert side[("MNQ", "10:00")]["sell"] == 0.8278767445171111
    assert side[("MGC", "09:30")]["sell"] == 1.0264453952502222
    assert side[("MGC", "10:30")]["buy"] == 1.0290423222583334


def test_b_two_products_hand_computed_to_the_cent(two_product_day) -> None:
    run = two_product_day
    got = [(f.root, f.side, f.qty, f.price, ct_of(f.fill_ts_ns), f.commission_cents,
            f.slippage_cents, f.gross_realized_cents, f.position_after)
           for f in fills_on(run.engine_result, DAY)]
    # Sizes at D_open $2,000 (b = $115.47): MNQ sigma 70 x $0.50 = $35 -> 3 (loss cap 500 / 51.5
    # -> 9); MGC sigma 50 x $1.00 = $50 -> 2 (loss cap at D_now 1,995.81: 498.95 / 103 -> 4).
    # The daily budget (D-03) does not bind: 105^2 + 100^2 = 21,025 <= 200^2.
    # Slippage = ceil(qty x side ticks x tick value in cents), plus (qty - q_c) x 1 tick for the
    # contracts beyond q_c = 1 (D-08a): MNQ + 2 x 50 = 100 cents, MGC + 1 x 100 = 100 cents a fill.
    #   MNQ buy  09:00: 3 x 0.9031496 x 50 = 135.47 -> 136 + 100 = 236 ; commission 3 x 61 = 183
    #   MGC sell 09:30: 2 x 1.0264454 x 100 = 205.29 -> 206 + 100 = 306 ; commission 2 x 96 = 192
    #   MNQ sell 10:00: 3 x 0.8278767 x 50 = 124.18 -> 125 + 100 = 225 ; gross 3 x (8010.25 -
    #                    8000) / 0.25 = 3 x 41 ticks x 50 = 6,150
    #   MGC buy  10:30: 2 x 1.0290423 x 100 = 205.81 -> 206 + 100 = 306 ; gross 2 x (2000.0 -
    #                    1995.3) / 0.1 = 2 x 47 ticks x 100 = 9,400
    assert got == [
        ("MNQ", "buy", 3, 8000.0, time(9, 0), 183, 236, 0, 3),
        ("MGC", "sell", 2, 2000.0, time(9, 30), 192, 306, 0, -2),  # both hold positions here
        ("MNQ", "sell", 3, 8010.25, time(10, 0), 183, 225, 6150, 0),
        ("MGC", "buy", 2, 1995.3, time(10, 30), 192, 306, 9400, 0),
    ]
    # MNQ net 6,150 - 183 - 236 - 183 - 225 = 5,323; MGC net 9,400 - 192 - 306 - 192 - 306
    # = 8,404; the day: 13,727 cents = $137.27; floor max(-2,000, min(137.27 - 2,000, 0))
    assert sorted((t.root, t.net_cents, t.contracts) for t in run.trips) == [
        ("MGC", 8404, 2), ("MNQ", 5323, 3)]
    close = [e for e in run.engine_result.events(DayClose) if e.trade_date == DAY][0]
    assert (close.balance_cents, close.day_net_cents, close.floor_after_cents) == (
        13727, 13727, -186273)
    assert run.daily[pd.Timestamp(DAY)] == pytest.approx(137.27, abs=1e-9)
    assert run.daily.drop(pd.Timestamp(DAY)).eq(0.0).all()


def test_b_day_records_per_contract(two_product_day) -> None:
    day = [d for d in two_product_day.days if d.trade_date == DAY][0]
    assert [d.trade_date for d in two_product_day.days] == [date(2019, 6, i) for i in (3, 4, 5, 6)]
    mnq, mgc = day.trades  # entry order
    # MNQ: net $53.23 / 3 = $17.7433; cost (6150 - 5323) / 3 = $2.7567 a contract; the price
    # never went below the entry over [09:00, 10:00): worst = 0 - 2.7567
    assert (mnq.root, mnq.contracts, mnq.horizon, mnq.cluster) == ("MNQ", 3, "h60", "K1")
    assert mnq.pnl_usd_per_contract == pytest.approx(53.23 / 3, abs=1e-9)
    assert mnq.worst_usd_per_contract == pytest.approx(-8.27 / 3, abs=1e-9)
    # MGC: $84.04 / 2 = $42.02; cost (9400 - 8404) / 2 = $4.98; no adverse move: worst -4.98
    assert mgc.pnl_usd_per_contract == pytest.approx(42.02, abs=1e-9)
    assert mgc.worst_usd_per_contract == pytest.approx(-4.98, abs=1e-9)
    assert (mnq.q_c, mgc.q_c) == (1, 1)  # the q_c the engine charged, for payout re-sizing
    assert (mnq.sigma_ticks, mnq.loss_ticks, mnq.cost_ticks, mnq.tick_value_usd,
            mnq.lot_equiv) == (70.0, 100.0, 3.0, 0.5, 0.1)
    assert mnq.entry_ts_ns == ct_ns(DAY, 9, 0) and mnq.exit_ts_ns == ct_ns(DAY, 10, 0)


# ---- (c) the forced flatten ---------------------------------------------------------------------
def test_c_the_forced_flatten_closes_every_product_at_f() -> None:
    sched = pd.DataFrame([row("MNQ", DAY, (13, 0), (15, 8), 1, "hF"),
                          row("MGC", DAY, (13, 30), (15, 8), -1, "hF")])
    run = run_portfolio({"MNQ": flat("MNQ"), "MGC": flat("MGC")}, sched,
                        risk({"MNQ": (70.0, 100.0), "MGC": (50.0, 100.0)}),
                        rules_kwargs={"releases": calendar()})
    closes = [f for f in fills_on(run.engine_result, DAY) if f.position_after == 0]
    assert [(f.root, f.reason, ct_of(f.fill_ts_ns)) for f in closes] == [
        ("MGC", "forced_flatten", time(15, 8)), ("MNQ", "forced_flatten", time(15, 8))]
    assert run.engine_result.final_state.balance_cents == sum(t.net_cents for t in run.trips)


# ---- (d) the XFA gate ----------------------------------------------------------------------------
def test_d_the_xfa_gate_refuses_a_size_above_the_tier() -> None:
    frames = {r: flat(r) for r in ("MNQ", "MGC", "MYM")}
    legs = tuple(LegSpec(r, True) for r in frames)
    minute = ct_ns(DAY, 8, 59)

    class Burst:
        name, trading_windows = "burst", {}

        def on_minute(self, view, account):
            if view.ts_event_ns != minute:
                return []
            return [leg_market_intent(view, "MNQ", "buy", 10),  # 1.0 lot
                    leg_market_intent(view, "MGC", "buy", 10),  # 2.0 lots: at the tier
                    leg_market_intent(view, "MYM", "buy", 1)]  # 2.1 lots > 2 (base tier)

    rules = build_rules(list(frames), frames, {"releases": calendar()})
    res = run_engine(frames, Burst(), legs, rules)
    recs = [(r.root, r.accepted, r.refusal.reason if r.refusal else None)
            for r in res.events(IntentRecord)]
    assert recs == [("MNQ", True, None), ("MGC", True, None),
                    ("MYM", False, "position_limit_exceeded")]
    frozen = run_engine(frames, Burst(), legs, StageERules(
        rules.legs, rules.window_dates, rules.blackout, rules.releases))
    assert [r.refusal.reason for r in frozen.events(IntentRecord) if r.refusal] == [
        "engine_second_leg_position", "engine_second_leg_position"]


def test_d_the_member_stays_a_tenth_under_the_tier() -> None:
    sched = pd.DataFrame([row("MNQ", DAY, (9, 0), (10, 0), 1, edge=3.0),
                          row("MGC", DAY, (9, 0), (10, 0), 1, edge=2.0),
                          row("MCL", DAY, (9, 0), (10, 0), 1, edge=1.0)])
    run = run_portfolio({r: flat(r) for r in ("MNQ", "MGC", "MCL")}, sched,
                        risk({"MNQ": (1.0, 1.0), "MGC": (1.0, 1.0), "MCL": (1.0, 1.0)}),
                        rules_kwargs={"releases": calendar()})
    assert [(d.root, d.contracts, d.reason) for d in run.decisions] == [
        ("MNQ", 10, ""), ("MGC", 9, ""), ("MCL", 0, "size_zero")]  # 1.0 + 0.9 = 1.9 lots
    assert all(r.accepted for r in run.engine_result.events(IntentRecord))


def test_member_cap_applies_per_product_under_portfolio_rules() -> None:
    frames = {r: flat(r) for r in ("MNQ", "MGC")}
    minute = ct_ns(DAY, 8, 59)

    class Over:
        name, trading_windows = "over", {}

        def on_minute(self, view, account):
            if view.ts_event_ns != minute:
                return []
            return [leg_market_intent(view, "MNQ", "buy", 11),
                    leg_market_intent(view, "MGC", "buy", 10)]

    res = run_engine(frames, Over(), tuple(LegSpec(r, True) for r in frames),
                     build_rules(list(frames), frames, {"releases": calendar()}))
    assert [(r.root, r.refusal.reason if r.refusal else None)
            for r in res.events(IntentRecord)] == [("MNQ", "member_product_cap_exceeded"),
                                                  ("MGC", None)]


# ---- (e) an MLL breach ---------------------------------------------------------------------
def test_e_an_mll_breach_liquidates_and_the_account_restarts() -> None:
    mnq = flat("MNQ")
    ct = pd.to_datetime(mnq["ts_event"], utc=True).dt.tz_convert(CT).dt.time
    crash = (mnq["trade_date"] == DAY.isoformat()) & (ct == time(9, 30))
    mnq.loc[crash, ["low", "close"]] = [7890.0, 7895.0]
    sched = pd.DataFrame([row("MNQ", DAY, (9, 0), (10, 0), 1),
                          row("MNQ", LAST, (9, 0), (10, 0), 1)])
    run = run_portfolio({"MNQ": mnq}, sched, risk({"MNQ": (1.0, 1.0)}),
                        rules_kwargs={"releases": calendar()})
    day = fills_on(run.engine_result, DAY)
    # long 10 at 8000.00 (32,000 ticks); balance after the entry -(610 + 452 + 9 x 50 beyond
    # q_c) = -1,512 cents. Touch: (floor - balance + basis x tv) / (q x tv) = (-200,000 + 1,512
    # + 320,000 x 50) / 500 = 31,603.024 -> floor 31,603 ticks = 7,900.75 < the 9:30 open:
    # liquidated there.
    assert [(f.reason, f.qty, f.price, ct_of(f.fill_ts_ns)) for f in day] == [
        ("strategy", 10, 8000.0, time(9, 0)), ("mll_liquidation", 10, 7900.75, time(9, 30))]
    close = [e for e in run.engine_result.events(DayClose) if e.trade_date == DAY][0]
    assert close.status_after == "breached"
    starts = run.engine_result.events(AccountStart)
    assert [(s.account_index, s.trade_date, s.balance_cents, s.floor_cents) for s in starts] == [
        (0, FIRST, 0, -200_000), (1, LAST, 0, -200_000)]
    nxt = fills_on(run.engine_result, LAST)
    assert nxt and {f.account_index for f in nxt} == {1} and nxt[0].qty == 10
    assert run.engine_result.accounts_started == 2
    assert run.combined_mll_breaches == ()  # one leg: the engine's own check is the account's


# ---- the combined MLL audit (lead ruling 2026-10-03) ------------------------------------------
def dip(root: str, low: float, at: time = time(9, 40)) -> pd.DataFrame:
    f = flat(root)
    ct = pd.to_datetime(f["ts_event"], utc=True).dt.tz_convert(CT).dt.time
    m = (f["trade_date"] == DAY.isoformat()) & (ct == at)
    f.loc[m, "low"] = low
    return f


def both_long(mnq_low: float, mgc_low: float):
    sched = pd.DataFrame([row("MNQ", DAY, (9, 0), (10, 0), 1, edge=2.0),
                          row("MGC", DAY, (9, 0), (10, 0), 1)])
    return run_portfolio({"MNQ": dip("MNQ", mnq_low), "MGC": dip("MGC", mgc_low)}, sched,
                         risk({"MNQ": (1.0, 1.0), "MGC": (1.0, 1.0)}),
                         rules_kwargs={"releases": calendar()})


def test_the_audit_catches_a_combined_intraday_breach_the_engine_misses() -> None:
    run = both_long(7945.0, 1987.7)
    assert sorted((f.root, f.qty) for f in fills_on(run.engine_result, DAY)
                  if f.opening) == [("MGC", 9), ("MNQ", 10)]
    assert not any(f.reason == "mll_liquidation" for f in run.engine_result.events(Fill))
    close = [e for e in run.engine_result.events(DayClose) if e.trade_date == DAY][0]
    assert close.status_after == "active"  # the engine checks each leg alone
    # Entries at the 09:00 open: MNQ 10 at 8000.00, commission 10 x 61 = 610, slippage
    # ceil(10 x 0.9031496 x 50 = 451.57) = 452 + 9 x 50 beyond q_c = 902; MGC 9 at 2000.0,
    # commission 9 x 96 = 864, slippage ceil(9 x 1.0910981 x 100 = 981.99) = 982 + 8 x 100 =
    # 1,782 -> balance -4,158 cents = -$41.58.
    # 09:40 lows: MNQ 7945.00 = -220 ticks x 10 x $0.50 = -$1,100.00; MGC 1987.7 = -123 ticks
    # x 9 x $1.00 = -$1,107.00. Combined -41.58 - 1,100 - 1,107 = -$2,248.58 <= floor -$2,000.
    # Alone: -41.58 - 1,107 = -1,148.58 and -41.58 - 1,100 = -1,141.58, both above the floor.
    t = load_frozen_tables().costs
    assert [b.side_ticks["buy"] for b in t["MGC"].buckets if b.key == "09:00"] == [
        1.0910980706522222]
    assert run.breached_combined
    assert len(run.combined_mll_breaches) == 1
    b = run.combined_mll_breaches[0]
    assert (b.trade_date, ct_of(b.ts_ns), b.account_index) == (DAY, time(9, 40), 0)
    assert b.combined_worst_usd == pytest.approx(-2248.58, abs=1e-9)
    assert b.floor_usd == -2000.0
    assert b.legs == (("MGC", 9, pytest.approx(-1107.0)), ("MNQ", 10, pytest.approx(-1100.0)))


def test_the_audit_ignores_a_minute_the_engine_breached_itself() -> None:
    # MNQ alone: 10 x (7900 - 8000) / 0.25 x $0.50 = -$2,000 -> the engine liquidates at 09:40;
    # MGC is liquidated at the next open; no minute with two legs is left past the floor.
    run = both_long(7900.0, 1987.7)
    liq = [(f.root, ct_of(f.fill_ts_ns)) for f in run.engine_result.events(Fill)
           if f.reason == "mll_liquidation"]
    assert liq == [("MNQ", time(9, 40)), ("MGC", time(9, 41))]
    assert run.combined_mll_breaches == () and not run.breached_combined


def test_overlap_above_the_floor_reports_none(two_product_day) -> None:
    assert two_product_day.combined_mll_breaches == ()
    run = both_long(7960.0, 1990.0)  # -41.58 - 800 - 900 = -1,741.58 > -2,000
    assert run.combined_mll_breaches == () and not run.breached_combined


def test_run_portfolio_refuses_a_non_50k_account() -> None:
    from ml_route_v2.account import ACCOUNT_150K

    with pytest.raises(ValueError, match="encodes 50K only"):
        run_portfolio({}, pd.DataFrame([row("MNQ", DAY, (9, 0), (10, 0), 1)]),
                      risk({"MNQ": (1.0, 1.0)}), account=ACCOUNT_150K)


# ---- the per-product roll blackout (V2.2, lead ruling 2026-10-03, design fix 8) ------------------
def entries_on_day(rules_kwargs: dict) -> dict[str, str | None]:
    sched = pd.DataFrame([row("MNQ", DAY, (9, 0), (10, 0), 1, edge=2.0),
                          row("MGC", DAY, (9, 0), (10, 0), 1)])
    run = run_portfolio({"MNQ": flat("MNQ"), "MGC": flat("MGC")}, sched,
                        risk({"MNQ": (200.0, 100.0), "MGC": (100.0, 100.0)}),
                        rules_kwargs={"releases": calendar(), **rules_kwargs})
    return {r.root: (r.refusal.reason if r.refusal else None)
            for r in run.engine_result.events(IntentRecord)}


def test_an_entry_is_refused_on_its_own_products_roll_date() -> None:
    got = entries_on_day({"product_blackout": {"MNQ": {DAY}, "MGC": set()}})
    assert got == {"MNQ": "engine_roll_blackout", "MGC": None}


def test_an_entry_on_another_products_roll_date_is_accepted() -> None:
    got = entries_on_day({"product_blackout": {"MNQ": set(), "MGC": {DAY}}})
    assert got == {"MNQ": None, "MGC": "engine_roll_blackout"}
    # the frozen D4 union (no product_blackout) refuses both: the behaviour v2 replaces
    assert entries_on_day({"blackout": {DAY}}) == {"MNQ": "engine_roll_blackout",
                                                   "MGC": "engine_roll_blackout"}


def test_every_traded_leg_needs_its_own_blackout_set() -> None:
    frames = {r: flat(r) for r in ("MNQ", "MGC")}
    with pytest.raises(ValueError, match="blackout_missing"):
        build_rules(list(frames), frames, {"releases": calendar(),
                                           "product_blackout": {"MNQ": set()}})


# ---- the member's daily risk budget (design review D-03) ---------------------------------------
def test_the_member_spends_the_daily_risk_budget() -> None:
    # One sigma $110 for each: MNQ and MYM 220 ticks x $0.50, MGC and MCL 110 x $1.00 -> 1 contract
    # (115.47 / 110). D_open $2,000: the budget is 200^2 = 40,000; three entries use 3 x 110^2 =
    # 36,300; the fourth needs 12,100 > 3,700 and is refused; the next date has a new budget.
    sched = pd.DataFrame([row("MNQ", DAY, (9, 0), (9, 20), 1), row("MGC", DAY, (9, 30), (9, 50), 1),
                          row("MCL", DAY, (10, 0), (10, 20), 1),
                          row("MYM", DAY, (10, 30), (10, 50), 1),
                          row("MYM", LAST, (9, 0), (9, 20), 1)])
    run = run_portfolio({r: flat(r) for r in ("MNQ", "MGC", "MCL", "MYM")}, sched,
                        risk({"MNQ": (220.0, 100.0), "MGC": (110.0, 100.0),
                              "MCL": (110.0, 100.0), "MYM": (220.0, 100.0)}),
                        rules_kwargs={"releases": calendar()})
    assert [(d.root, d.contracts, d.reason) for d in run.decisions] == [
        ("MNQ", 1, ""), ("MGC", 1, ""), ("MCL", 1, ""), ("MYM", 0, "risk_budget_spent"),
        ("MYM", 1, "")]


def test_the_member_sizes_from_each_rows_own_risk_and_skips_an_unknown_one() -> None:
    """Code review C-04 and C-02: schedule rows that carry sigma_ticks and loss_ticks (the table
    of the split that produced them) are sized from those values, not from the risk table, and
    the trade records carry them; a row whose sigma is NaN is skipped as risk_unknown.
    MNQ: one sigma 55 x $0.50 = $27.50 -> floor(115.47 / 27.5) = 4 (the table's 220 would give
    1); MGC: 110 x $1.00 -> 1; MCL: NaN -> skipped."""
    sched = pd.DataFrame([row("MNQ", DAY, (9, 0), (9, 20), 1), row("MGC", DAY, (9, 30), (9, 50), 1),
                          row("MCL", DAY, (10, 0), (10, 20), 1)])
    sched = sched.assign(sigma_ticks=[55.0, 110.0, float("nan")], loss_ticks=[100.0] * 3)
    run = run_portfolio({r: flat(r) for r in ("MNQ", "MGC", "MCL")}, sched,
                        risk({"MNQ": (220.0, 100.0), "MGC": (110.0, 100.0),
                              "MCL": (110.0, 100.0)}),
                        rules_kwargs={"releases": calendar()})
    assert [(d.root, d.contracts, d.reason) for d in run.decisions] == [
        ("MNQ", 4, ""), ("MGC", 1, ""), ("MCL", 0, "risk_unknown")]
    trades = [t for d in run.days for t in d.trades]
    assert [(t.root, t.contracts, t.sigma_ticks) for t in trades] == [("MNQ", 4, 55.0),
                                                                      ("MGC", 1, 110.0)]


# ---- V23 item 11 (E.12 lead rule P-5): the release window in the engine-run portfolio --------
def _window_run(flag: bool, with_mnq: bool = True):
    """MNQ at 09:00 (its 1-lot product cap: sigma 1, loss 1) and MGC at 09:10 whose schedule
    row carries ``flag`` (targets.py's release_window); 50K base tier 2 lots, half = 1.0."""
    rows = [row("MGC", DAY, (9, 10), (9, 40), 1, rw=flag)]
    if with_mnq:
        rows.insert(0, row("MNQ", DAY, (9, 0), (10, 0), 1, edge=3.0))
    roots = ("MNQ", "MGC") if with_mnq else ("MGC",)
    return run_portfolio({r: flat(r) for r in roots}, pd.DataFrame(rows),
                         risk({"MNQ": (1.0, 1.0), "MGC": (1.0, 1.0)}),
                         rules_kwargs={"releases": calendar()})


def test_the_member_refuses_a_window_entry_above_half_the_tier_and_records_it() -> None:
    """MNQ's 1.0 lot is open; MGC's 9 micros (the room under the 1.9-lot cap) would make 1.9
    lots > 1.0: refused with reason "release_window" in the member's decisions. Unflagged, the
    same MGC entry is admitted (control)."""
    flagged = _window_run(True)
    assert [(d.root, d.contracts, d.reason) for d in flagged.decisions] == [
        ("MNQ", 10, ""), ("MGC", 0, "release_window")]
    assert sum(d.reason == "release_window" for d in flagged.decisions) == 1
    plain = _window_run(False)
    assert [(d.root, d.contracts, d.reason) for d in plain.decisions] == [
        ("MNQ", 10, ""), ("MGC", 9, "")]


def test_a_window_entry_at_half_the_tier_trades_and_its_record_carries_the_flag() -> None:
    """MGC alone: 10 micros = 1.0 lot, exactly half the base tier, so the flagged entry trades;
    its TradeRecord carries release_window for payout_sim's re-sizing."""
    run = _window_run(True, with_mnq=False)
    assert [(d.root, d.contracts, d.reason) for d in run.decisions] == [("MGC", 10, "")]
    trades = [t for d in run.days for t in d.trades]
    assert [(t.root, t.contracts, t.release_window) for t in trades] == [("MGC", 10, True)]
    assert all(not t.release_window for d in _window_run(False).days for t in d.trades)
