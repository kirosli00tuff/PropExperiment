"""Stage E.7 Task 3 audit (MemberAuditor-K1-FableXHigh): recompute the K1 literal tables from their
sources with code independent of the generator and of coder B's tests (brief item 5).

Read-only: EC-CAL through data.group_session, the engine's F through rules.sessions, the saved Cboe
file through the csv module and raw line splitting, and the member modules' tuples. Prints counts and
every difference; writes a JSON summary next to this script. No bar file is read.

Run: PYTHONPYCACHEPREFIX=<fresh dir> uv run python reports/stage_e7_briefs/audit_k1/auditor_recompute_tables.py
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

from data.group_session import load_group_calendar
from rules import sessions
from strategy.members.k1 import _calendar as cal_mod
from strategy.members.k1 import _event_common as common
from strategy.members.k1 import _vxn as vxn_mod
from strategy.members.k1 import vxnband

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "auditor_recompute_tables.json"
ROOTS = ("MNQ", "M2K", "MYM")
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
VXN_FIRST = date(2019, 4, 30)
RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
VXN_FILE = REPO / "data/vendor/index_history/vxn/VXN_History.csv"
SPEC_SHA = "f1b00135c4922ea756cd22cfeaa1d483700a6aed580f8da562f61574b5e1cdcc"
SPEC_DROPS = {"2021-04-02", "2021-12-24", "2024-02-01"}
REGULAR_F = time(15, 8)


def days(first: date, last: date) -> list[date]:
    return [first + timedelta(n) for n in range((last - first).days + 1)]


def main() -> None:
    out: dict = {}
    cal = load_group_calendar("equity")

    # ---- EQUITY_TRADE_DATES -------------------------------------------------------------
    trade = [d for d in days(FIRST, LAST) if cal.is_trade_date(d)]
    mine_trade = tuple(d.isoformat() for d in trade)
    out["trade_dates"] = {
        "mine": len(mine_trade), "module": len(cal_mod.EQUITY_TRADE_DATES),
        "equal": mine_trade == cal_mod.EQUITY_TRADE_DATES,
        "only_mine": sorted(set(mine_trade) - set(cal_mod.EQUITY_TRADE_DATES)),
        "only_module": sorted(set(cal_mod.EQUITY_TRADE_DATES) - set(mine_trade)),
        "first": mine_trade[0], "last": mine_trade[-1],
        "sorted_unique": list(mine_trade) == sorted(set(mine_trade)),
    }

    # ---- EQUITY_FULL_SESSIONS (K3-L-11: no early halt AND F 15:08 on all three roots) ------
    full, disagree, f_differs = [], [], []
    for d in trade:
        halt = cal.early_halt_ct(d)
        fs = {r: sessions.flatten_time_ct(r, d) for r in ROOTS}
        if len(set(fs.values())) != 1:
            f_differs.append((d.isoformat(), {r: str(t) for r, t in fs.items()}))
        f = fs["MNQ"]
        no_halt, regular = halt is None, f == REGULAR_F
        if no_halt and regular:
            full.append(d.isoformat())
        if no_halt != regular:
            disagree.append((d.isoformat(), str(halt), str(f)))
    mine_full = tuple(full)
    removed = [d for d in mine_trade if d not in set(mine_full)]
    out["full_sessions"] = {
        "mine": len(mine_full), "module": len(cal_mod.EQUITY_FULL_SESSIONS),
        "equal": mine_full == cal_mod.EQUITY_FULL_SESSIONS,
        "only_mine": sorted(set(mine_full) - set(cal_mod.EQUITY_FULL_SESSIONS)),
        "only_module": sorted(set(cal_mod.EQUITY_FULL_SESSIONS) - set(mine_full)),
        "removed_total": len(removed),
        "removed_research": [d for d in removed
                             if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()],
        "halt_vs_F_disagree": disagree, "F_differs_between_roots": f_differs,
        "common_FULL_SESSIONS_equal": frozenset(date.fromisoformat(d) for d in mine_full)
        == common.FULL_SESSIONS,
    }

    # ---- PREVIOUS_TRADE_DATE -----------------------------------------------------------
    prev = {b: a for a, b in zip(trade, trade[1:], strict=False)}
    out["previous_trade_date"] = {
        "equal": prev == common.PREVIOUS_TRADE_DATE, "entries": len(prev),
        "first_date_has_no_predecessor": FIRST not in common.PREVIOUS_TRADE_DATE,
    }

    # ---- source sha256 pinned in _calendar.py ------------------------------------------
    pinned = dict(cal_mod.SOURCE_SHA256)
    out["calendar_sources"] = {rel: hashlib.sha256((REPO / rel).read_bytes()).hexdigest() == sha
                              for rel, sha in pinned.items()}
    out["calendar_sources"]["cal_module_sha256_keys"] = sorted(cal.module_sha256())

    # ---- VXN_CLOSE ------------------------------------------------------------------------
    raw = VXN_FILE.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    text = raw.decode("ascii")
    lines = text.splitlines()
    rows = list(csv.reader(io.StringIO(text)))
    header, body = rows[0], rows[1:]
    # raw last-field check: the CLOSE string exactly as written (no csv normalisation)
    raw_close = {}
    for line in lines[1:]:
        parts = line.split(",")
        assert len(parts) == 5, line
        raw_close[parts[0]] = parts[4]
    in_range = []
    for r in body:
        d = datetime.strptime(r[0], "%m/%d/%Y").date()
        if VXN_FIRST <= d <= LAST:
            assert raw_close[r[0]] == r[4]
            in_range.append((d.isoformat(), r[4]))
    kept = tuple((d, c) for d, c in in_range if d not in SPEC_DROPS)
    dates_in_range = [d for d, _ in in_range]
    dup = len(dates_in_range) - len(set(dates_in_range))
    module_rows = vxn_mod.VXN_CLOSE
    diffs = []
    mine_map, mod_map = dict(kept), dict(module_rows)
    for d in sorted(set(mine_map) | set(mod_map)):
        if mine_map.get(d) != mod_map.get(d):
            diffs.append((d, mine_map.get(d), mod_map.get(d)))
    trade_set = set(mine_trade)
    on_non_trade_before = [d for d, _ in in_range if d >= FIRST.isoformat() and d not in trade_set]
    on_non_trade_after = [d for d, _ in kept if d >= FIRST.isoformat() and d not in trade_set]
    have = set(mod_map)
    no_v = [d for p, d in zip(mine_trade, mine_trade[1:], strict=False) if p not in have]
    no_v_research = [d for d in no_v if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()]
    weekday_no_row = [d.isoformat() for d in days(VXN_FIRST, LAST)
                      if d.weekday() < 5 and d.isoformat() not in dict(in_range)]
    out["vxn"] = {
        "file_sha256_equals_spec": sha == SPEC_SHA, "file_sha256": sha,
        "module_pins_spec_sha": dict(vxn_mod.VXN_SOURCE_SHA256).get(
            "data/vendor/index_history/vxn/VXN_History.csv") == SPEC_SHA,
        "header": header, "rows_total": len(body), "first_row": body[0][0],
        "last_row": body[-1][0], "rows_in_range": len(in_range), "duplicate_dates_in_range": dup,
        "rows_kept": len(kept), "module_rows": len(module_rows),
        "equal_exact_strings_and_order": kept == module_rows, "differences": diffs,
        "dropped_module": [d for d, _ in vxn_mod.DROPPED_VXN],
        "dropped_spec": sorted(SPEC_DROPS),
        "dropped_rows_present_in_file": sorted(d for d in SPEC_DROPS if d in dict(in_range)),
        "all_close_6_decimals": all(Decimal(c).as_tuple().exponent == -6 for _, c in kept),
        "member_map_equals_module": {date.fromisoformat(d): Decimal(c) for d, c in module_rows}
        == vxnband._VXN,
        "rows_in_range_on_non_trade_dates_before_drops": on_non_trade_before,
        "rows_on_non_trade_dates_after_drops": on_non_trade_after,
        "weekdays_in_range_without_row": len(weekday_no_row),
        "trade_dates_without_V_total": len(no_v),
        "trade_dates_without_V_research": no_v_research,
        "vxn_for_checks": {
            "2025-04-21 (after Good Friday) -> 04-17 row": str(vxnband.vxn_for(date(2025, 4, 21)))
            + " vs " + str(mod_map.get("2025-04-17")),
            "2025-05-27 (after Memorial Day)": str(vxnband.vxn_for(date(2025, 5, 27))),
            "2019-05-01 (table's first date)": str(vxnband.vxn_for(date(2019, 5, 1))),
            "2019-05-06 (S_X)": str(vxnband.vxn_for(date(2019, 5, 6))),
            "2024-02-02 (R-1b-2)": str(vxnband.vxn_for(date(2024, 2, 2))),
            "2021-04-05 (R-1b-3)": str(vxnband.vxn_for(date(2021, 4, 5))),
            "2026-06-19 (last)": str(vxnband.vxn_for(date(2026, 6, 19))),
        },
    }
    # the two R-1b-3 rows repeat the prior close; the R-1b-2 row's CLOSE
    idx = {r[0]: i for i, r in enumerate(body)}
    out["vxn"]["r1b3_rows_repeat_prior_close"] = {
        d: body[idx[d]][1:] == [body[idx[d] - 1][4]] * 4
        for d in ("04/02/2021", "12/24/2021")}
    out["vxn"]["r1b2_row_close_now"] = body[idx["02/01/2024"]][4]

    OUT.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    t, f, v = out["trade_dates"], out["full_sessions"], out["vxn"]
    print(f"EQUITY_TRADE_DATES: mine {t['mine']} module {t['module']} equal {t['equal']} "
          f"only_mine {t['only_mine']} only_module {t['only_module']}")
    print(f"EQUITY_FULL_SESSIONS: mine {f['mine']} module {f['module']} equal {f['equal']} "
          f"only_mine {f['only_mine']} only_module {f['only_module']} removed {f['removed_total']} "
          f"disagree {f['halt_vs_F_disagree']} F_differs {f['F_differs_between_roots']} "
          f"common_equal {f['common_FULL_SESSIONS_equal']}")
    print(f"removed research: {f['removed_research']}")
    print(f"PREVIOUS_TRADE_DATE equal {out['previous_trade_date']}")
    print(f"calendar source sha256 pins: {out['calendar_sources']}")
    print(f"VXN: sha_ok {v['file_sha256_equals_spec']} header {v['header']} total {v['rows_total']} "
          f"{v['first_row']}..{v['last_row']} in_range {v['rows_in_range']} dup {v['duplicate_dates_in_range']} "
          f"kept {v['rows_kept']} module {v['module_rows']} equal {v['equal_exact_strings_and_order']} "
          f"diffs {v['differences']} member_map_equal {v['member_map_equals_module']}")
    print(f"VXN drops module {v['dropped_module']} present_in_file {v['dropped_rows_present_in_file']} "
          f"r1b3 {v['r1b3_rows_repeat_prior_close']} r1b2_now {v['r1b2_row_close_now']}")
    print(f"VXN rows on non-trade dates: before drops {v['rows_in_range_on_non_trade_dates_before_drops']} "
          f"after {v['rows_on_non_trade_dates_after_drops']}; weekdays without row {v['weekdays_in_range_without_row']}")
    print(f"trade dates without V: total {v['trade_dates_without_V_total']} research {v['trade_dates_without_V_research']}")
    for k, val in v["vxn_for_checks"].items():
        print(f"  vxn_for {k}: {val}")
    print("written", OUT)


if __name__ == "__main__":
    main()
