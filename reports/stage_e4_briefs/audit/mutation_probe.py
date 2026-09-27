"""Task 3 audit: do the K4 tests bite on the literals? Each mutant patches one module constant
in memory (no file changes), runs the tests that should catch it, and reports killed/survived.
Run: PYTHONPATH=. uv run python reports/stage_e4_briefs/audit/mutation_probe.py
"""
from __future__ import annotations

from datetime import time
from decimal import Decimal

from strategy.members.k4 import apipre, cp1, cp2, cp3, eiafade, eiamom, ngpre, ovr
from tests import test_e4_k4_members_a as ta
from tests import test_e4_k4_members_a_ovr as to
from tests import test_e4_k4_members_b as tb
from tests import test_e4_k4_members_b_eia as te

MUTANTS = [
    ("ngpre.SIDE = buy", ngpre, "SIDE", "buy",
     [("ngpre sells", lambda: tb.test_ngpre_standard_thursday_sells_at_0800_and_exits_at_1000())]),
    ("ngpre entry T-90", ngpre, "ENTRY_DECISION_OFFSET_MIN", -90,
     [("ngpre 07:59 decision", lambda: tb.test_ngpre_standard_thursday_sells_at_0800_and_exits_at_1000())]),
    ("ngpre exit T+30", ngpre, "EXIT_DECISION_OFFSET_MIN", 30,
     [("ngpre 09:59 decision", lambda: tb.test_ngpre_standard_thursday_sells_at_0800_and_exits_at_1000())]),
    ("apipre signal end 15:40", apipre, "SIGNAL_END_CT", time(15, 40),
     [("apipre buys", lambda: tb.test_apipre_r_api_from_the_tuesday_1524_and_1539_closes_buys())]),
    ("apipre entry 07:30", apipre, "ENTRY_DECISION_CT", time(7, 30),
     [("apipre buys", lambda: tb.test_apipre_r_api_from_the_tuesday_1524_and_1539_closes_buys())]),
    ("apipre exit 09:29", apipre, "EXIT_DECISION_CT", time(9, 29),
     [("apipre buys", lambda: tb.test_apipre_r_api_from_the_tuesday_1524_and_1539_closes_buys())]),
    ("eiafade threshold 1/199", eiafade, "THRESHOLD_DENOMINATOR", 199,
     [("exact -0.5% buys", lambda: te.test_eiafade_m_at_exactly_minus_half_percent_buys()),
      ("side rule exact", lambda: te.test_eiafade_the_side_rule_is_exact_on_integer_ticks())]),
    ("eiafade threshold 1/201", eiafade, "THRESHOLD_DENOMINATOR", 201,
     [("just inside no trade", lambda: te.test_eiafade_just_inside_either_threshold_is_no_trade(-te.HALF_PCT + 1)),
      ("side rule exact", lambda: te.test_eiafade_the_side_rule_is_exact_on_integer_ticks())]),
    ("eiafade entry T+15", eiafade, "ENTRY_DECISION_OFFSET_MIN", 15,
     [("exact -0.5% buys", lambda: te.test_eiafade_m_at_exactly_minus_half_percent_buys())]),
    ("eiafade base T-2", eiafade, "BASE_OFFSET_MIN", -2,
     [("exact -0.5% buys", lambda: te.test_eiafade_m_at_exactly_minus_half_percent_buys())]),
    ("eiafade bound 13:14", eiafade, "LATEST_ENTRY_FILL_CT", time(13, 14),
     [("13:13 bound", lambda: te.test_eiafade_the_1600_ct_row_and_the_1313_bound())]),
    ("eiafade exit 13:29", eiafade, "EXIT_DECISION_CT", time(13, 29),
     [("exact -0.5% buys", lambda: te.test_eiafade_m_at_exactly_minus_half_percent_buys())]),
    ("eiamom signal end 10:00", eiamom, "SIGNAL_END_CT", time(10, 0),
     [("r3 positive buys", lambda: te.test_eiamom_r3_positive_buys_at_1430_and_exits_at_1459())]),
    ("eiamom entry 14:30", eiamom, "ENTRY_DECISION_CT", time(14, 30),
     [("r3 positive buys", lambda: te.test_eiamom_r3_positive_buys_at_1430_and_exits_at_1459())]),
    ("eiamom exit 14:59", eiamom, "EXIT_DECISION_CT", time(14, 59),
     [("r3 positive buys", lambda: te.test_eiamom_r3_positive_buys_at_1430_and_exits_at_1459())]),
    ("cp1 entry C-30", cp1, "ENTRY_BEFORE_C_MIN", 30,
     [("cp1 buys 13:00", lambda: ta.test_cp1_buys_on_a_positive_signal_at_1300_and_exits_at_1329("MCL"))]),
    ("cp1 signal O+30", cp1, "SIGNAL_AFTER_O_MIN", 30,
     [("cp1 buys 13:00", lambda: ta.test_cp1_buys_on_a_positive_signal_at_1300_and_exits_at_1329("MCL"))]),
    ("cp1 exit C-1", cp1, "EXIT_BEFORE_C_MIN", 1,
     [("cp1 buys 13:00", lambda: ta.test_cp1_buys_on_a_positive_signal_at_1300_and_exits_at_1329("MCL"))]),
    ("cp2 hold 74", cp2, "HOLD_BARS", 74,
     [("cp2 75 bars", lambda: ta.test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars("MCL"))]),
    ("cp2 buffer 3", cp2, "BUFFER_TICKS", 3,
     [("cp2 buffer exact", lambda: ta.test_cp2_the_buffer_is_exactly_four_ticks_either_side("NG"))]),
    ("cp2 range 16", cp2, "RANGE_MINUTES", 16,
     [("cp2 75 bars", lambda: ta.test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars("MCL"))]),
    ("cp3 buy cut 0.81", cp3, "CLV_BUY_AT_OR_ABOVE", Decimal("0.81"),
     [("clv 0.8 buys", lambda: ta.test_cp3_prior_clv_at_08_buys_on_the_0800_bar_and_exits_at_1329("MCL")),
      ("cuts exact", lambda: ta.test_cp3_clv_cuts_are_compared_exactly(10, 8, "buy"))]),
    ("cp3 sell cut 0.19", cp3, "CLV_SELL_AT_OR_BELOW", Decimal("0.19"),
     [("clv 0.2 sells", lambda: ta.test_cp3_prior_clv_at_02_sells())]),
    ("cp3 close bar C-2", cp3, "CLOSE_BEFORE_C_MIN", 2,
     [("clv 0.8 buys", lambda: ta.test_cp3_prior_clv_at_08_buys_on_the_0800_bar_and_exits_at_1329("MCL"))]),
    ("ovr exit t+59", ovr, "EXIT_AFTER_T_MIN", 59,
     [("ovr buys", lambda: to.test_ovr_buys_at_or_below_p10_fills_at_t_and_exits_at_t_plus_59("MCL"))]),
    ("ovr min values 79", ovr, "MIN_VALUES", 79,
     [("79 values no trade", lambda: to.test_ovr_a_date_with_missing_bars_contributes_fewer_values(frozenset({5, 6, 7, 8}), False))]),
    ("ovr min values 81", ovr, "MIN_VALUES", 81,
     [("80 values trade", lambda: to.test_ovr_absent_dates_keep_their_slot_and_80_values_are_needed(frozenset({5, 6, 7, 8}), True))]),
    ("ovr percentile nearest", ovr, "PERCENTILE_METHOD", "nearest",
     [("linear", lambda: to.test_percentile_side_uses_numpy_linear())]),
    ("ovr low percentile 11", ovr, "LOW_PERCENTILE", 11,
     [("ladder cuts", lambda: to.test_ovr_cut_boundaries_on_the_ladder())]),
    ("ovr reference dates 19", ovr, "REFERENCE_DATES", 19,
     [("20 refs", lambda: to.test_reference_dates_are_the_20_full_sessions_strictly_before_d()),
      ("only 20 most recent", lambda: to.test_ovr_only_the_20_most_recent_dates_are_referenced())]),
    ("ovr signal 61 min", ovr, "SIGNAL_MINUTES", 61,
     [("t-60 open", lambda: to.test_ovr_r_uses_the_t_minus_60_open_and_the_t_minus_1_close())]),
]


def main() -> None:
    survived = 0
    for name, module, attr, value, tests in MUTANTS:
        original = getattr(module, attr)
        setattr(module, attr, value)
        try:
            outcomes = []
            for label, fn in tests:
                try:
                    fn()
                    outcomes.append(f"{label}: SURVIVED")
                except AssertionError:
                    outcomes.append(f"{label}: killed")
                except Exception as exc:  # noqa: BLE001
                    outcomes.append(f"{label}: killed by {type(exc).__name__}")
        finally:
            setattr(module, attr, original)
        killed = all("killed" in o for o in outcomes)
        survived += 0 if killed else 1
        print(f"{'ok  ' if killed else 'WEAK'} {name}: {'; '.join(outcomes)}")
    print(f"mutants: {len(MUTANTS)}, with a surviving test: {survived}")


if __name__ == "__main__":
    main()
