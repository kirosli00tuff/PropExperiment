"""Per-trade join of the independent H6 reconstruction against the lead's result (step 2).

Writes reports/stage_e20_briefs/h6_verify_trade_diff.json.
"""
from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

REPO = Path(__file__).resolve().parents[2]
MINE = json.loads((REPO / "reports/stage_e20_briefs/h6_verify_independent.json").read_text())
LEAD = json.loads((REPO / "reports/stage_e20_H6_result.json").read_text())
OUT = REPO / "reports/stage_e20_briefs/h6_verify_trade_diff.json"
TOL_TICKS = 0.0001


def mine_trades(window: str, test: str) -> dict[str, dict]:
    out = {}
    for r in MINE["trades"]:
        if r["window"] != window or "gross_ticks" not in r:
            continue
        if test == "T2" and not r.get("t2"):
            continue
        if test == "T3" and not r.get("t3"):
            continue
        out[r["date"]] = r
    return out


def lead_trades(window: str, test: str) -> dict[str, dict]:
    block = LEAD["tests"][test] if window == "verdict" else LEAD["overlap"][test]
    return {t["trade_date"]: t for t in block["trades"]}


def stats_from(trades: list[dict], gross_key: str, net_key: str, cost_key: str,
               n_window: int, dates: list[str]) -> dict:
    net = np.array([t[net_key] for t in trades], dtype=float)
    gross = np.array([t[gross_key] for t in trades], dtype=float)
    c = np.array([t[cost_key] for t in trades], dtype=float)
    n = net.size
    t_b = float(net.mean() / (net.std(ddof=1) / math.sqrt(n))) if n > 1 else float("nan")
    p = float(student_t.sf(t_b, n - 1)) if n > 1 else 1.0
    daily = dict(zip((t["trade_date"] if "trade_date" in t else t["date"] for t in trades),
                     net * 0.5))
    pnl = np.array([daily.get(d, 0.0) for d in dates])
    sharpe = float(pnl.mean() / pnl.std(ddof=1) * math.sqrt(252))
    return {"n": n, "mean_gross": float(gross.mean()), "mean_c": float(c.mean()),
            "mean_net": float(net.mean()), "t_b": t_b, "p": p, "sharpe": sharpe,
            "sum_net_usd": float(net.sum() * 0.5)}


def window_dates(window: str) -> list[str]:
    lo, hi = (("2020-06-01", "2024-02-29") if window == "verdict" else ("2019-05-06", "2020-05-29"))
    # every equity trade date of the window: the dates my per-date rows cover (all trade dates)
    return sorted({r["date"] for r in MINE["trades"] if lo <= r["date"] <= hi} |
                  set(_all_trade_dates(lo, hi)))


def _all_trade_dates(lo: str, hi: str) -> list[str]:
    from data.group_session import _equity_calendar, trade_dates_between
    cal = _equity_calendar()
    return [d.isoformat() for d in trade_dates_between(cal, date.fromisoformat(lo),
                                                       date.fromisoformat(hi))]


report: dict = {"tolerance_ticks": TOL_TICKS, "windows": {}}
for window in ("verdict", "overlap"):
    wd = _all_trade_dates(*(("2020-06-01", "2024-02-29") if window == "verdict"
                            else ("2019-05-06", "2020-05-29")))
    report["windows"][window] = {"n_window_dates": len(wd), "tests": {}}
    for test in ("T1", "T2", "T3"):
        mine, lead = mine_trades(window, test), lead_trades(window, test)
        only_mine = sorted(set(mine) - set(lead))
        only_lead = sorted(set(lead) - set(mine))
        both = sorted(set(mine) & set(lead))
        mism = []
        for d in both:
            a, b = mine[d], lead[d]
            diffs = {}
            if a["side"] != b["side"]:
                diffs["side"] = (a["side"], b["side"])
            for ka, kb in (("entry_px", "entry_price"), ("exit_px", "exit_price"),
                           ("gross_ticks", "gross_ticks"), ("c_ticks", "cost_ticks"),
                           ("net_ticks", "net_ticks")):
                if abs(float(a[ka]) - float(b[kb])) > TOL_TICKS:
                    diffs[kb] = (a[ka], b[kb])
            mine_c_cents = int(round(a["c_cents"]))
            lead_c_cents = int(b["commission_cents"]) + int(b["slippage_cents"])
            if mine_c_cents != lead_c_cents:
                diffs["c_cents"] = (mine_c_cents, lead_c_cents)
            if diffs:
                mism.append({"date": d, "diffs": diffs, "lead_exit_type": b.get("exit_type"),
                             "lead_exit_reason": b.get("exit_reason"),
                             "lead_account_index": b.get("account_index"),
                             "lead_entry_fill_utc": b.get("entry_fill_utc"),
                             "lead_exit_fill_utc": b.get("exit_fill_utc"),
                             "mine_entry_ct": a.get("entry_ts_ct"),
                             "mine_exit_ct": a.get("exit_ts_ct"),
                             "lead_n_fills": b.get("n_fills")})
        lead_list = [lead[d] for d in sorted(lead)]
        mine_list = [mine[d] for d in sorted(mine)]
        lead_block = LEAD["tests"][test] if window == "verdict" else LEAD["overlap"][test]
        s_lead = stats_from(lead_list, "gross_ticks", "net_ticks", "cost_ticks", len(wd), wd)
        s_mine = stats_from(mine_list, "gross_ticks", "net_ticks", "c_ticks", len(wd), wd)
        # the lead's trades with the mismatching dates replaced by mine: does that recover mine?
        hybrid = [mine[d] if d in {m["date"] for m in mism} else lead[d] for d in sorted(lead)]
        s_hybrid = stats_from(
            [{"trade_date": t.get("trade_date", t.get("date")), "gross_ticks": t["gross_ticks"],
              "net_ticks": t["net_ticks"], "cost_ticks": t.get("cost_ticks", t.get("c_ticks"))}
             for t in hybrid], "gross_ticks", "net_ticks", "cost_ticks", len(wd), wd)
        gross_gap = sum(float(lead[m["date"]]["gross_ticks"]) - float(mine[m["date"]]["gross_ticks"])
                        for m in mism)
        report["windows"][window]["tests"][test] = {
            "n_mine": len(mine), "n_lead": len(lead), "matched_dates": len(both),
            "only_mine": only_mine, "only_lead": only_lead,
            "n_mismatched_trades": len(mism), "mismatches": mism,
            "gross_ticks_gap_lead_minus_mine_on_mismatches": gross_gap,
            "gross_ticks_gap_total": float(sum(t["gross_ticks"] for t in lead_list)
                                           - sum(t["gross_ticks"] for t in mine_list)),
            "stats_from_lead_trades": s_lead,
            "stats_from_my_trades": s_mine,
            "stats_lead_trades_with_mismatches_replaced_by_mine": s_hybrid,
            "lead_reported": {k: lead_block.get(k) for k in (
                "n_trades", "mean_gross_ticks", "mean_cost_ticks", "mean_net_ticks", "t_b",
                "p_one_sided", "annualized_net_sharpe", "net_usd_total", "exit_types",
                "engine_counters", "schedule_exclusions", "scheduled_entries")},
            "mine_reported": {k: MINE["tests"][window][test].get(k) for k in (
                "n_trades", "mean_gross_ticks", "mean_c_ticks", "mean_net_ticks", "t_b", "p",
                "annualized_net_sharpe" if False else "sharpe_net_annual", "sum_net_usd")},
        }
OUT.write_text(json.dumps(report, indent=1), encoding="utf-8")
for window in ("verdict", "overlap"):
    for test, r in report["windows"][window]["tests"].items():
        print(window, test, "mine", r["n_mine"], "lead", r["n_lead"], "only_mine", r["only_mine"],
              "only_lead", r["only_lead"], "mismatched", r["n_mismatched_trades"],
              "gap_on_mismatches", round(r["gross_ticks_gap_lead_minus_mine_on_mismatches"], 4),
              "gap_total", round(r["gross_ticks_gap_total"], 4))
        for m in r["mismatches"][:6]:
            print("   ", json.dumps(m))
        sl, sm, sh = (r["stats_from_lead_trades"], r["stats_from_my_trades"],
                      r["stats_lead_trades_with_mismatches_replaced_by_mine"])
        print("    lead-trades stats", {k: round(v, 6) for k, v in sl.items()})
        print("    lead reported    ", {k: (round(v, 6) if isinstance(v, float) else v)
                                        for k, v in r["lead_reported"].items()
                                        if k in ("mean_gross_ticks", "mean_net_ticks", "t_b",
                                                 "p_one_sided", "annualized_net_sharpe",
                                                 "net_usd_total")})
        print("    hybrid == mine?  ", {k: round(sh[k] - sm[k], 9) for k in sh})
print("wrote", OUT)
