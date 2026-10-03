"""Stage E.11 Task 4: kill switches KS1-KS5 (docs/STAGE_E_ML_V2_DESIGN.md V2.8, the table).
Every trigger and every reset; transitions are pure (the old state never changes)."""

from __future__ import annotations

import dataclasses

import pytest

from ml_route_v2.killswitch import KillSwitches, ks4_fires, ks5_blocks_entry, ks5_flatten_due

MIN = 60_000_000_000
T = 1_000_000 * MIN  # an arbitrary decision time


def test_state_is_frozen_and_transitions_return_new_states() -> None:
    ks = KillSwitches(2000.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ks.halted = True  # type: ignore[misc]
    after = ks.start_day(2000.0)
    assert after is not ks and ks.d_open == 0.0 and after.d_open == 2000.0


def test_ks1_fires_at_thirty_percent_of_d_open_and_rearms_next_day() -> None:
    ks = KillSwitches(2000.0).start_day(2000.0)  # threshold 0.30 x 2000 = 600
    assert ks.ks1_threshold() == pytest.approx(600.0)
    assert not ks.on_day_pnl(-599.99).ks1_tripped
    tripped = ks.on_day_pnl(-600.0)
    assert tripped.ks1_tripped and tripped.entries_blocked
    assert not tripped.on_entry(2000.0)[1]
    assert not tripped.start_day(1400.0).ks1_tripped  # the next trade date re-arms it


def test_ks1_uses_the_dll_when_it_is_nearer() -> None:
    ks = KillSwitches(4500.0, dll_usd=1000.0).start_day(4000.0)  # min(1200, 1000)
    assert ks.ks1_threshold() == 1000.0
    ks = KillSwitches(2000.0, dll_usd=1000.0).start_day(2000.0)  # min(600, 1000)
    assert ks.ks1_threshold() == 600.0


def test_ks2_halves_size_below_half_the_mll_and_restores_at_it() -> None:
    ks = KillSwitches(2000.0)
    assert ks.size_multiplier(999.99) == 0.5
    assert ks.size_multiplier(1000.0) == 1.0


def test_ks2b_halts_below_a_quarter_of_the_mll_and_stays_halted() -> None:
    ks = KillSwitches(2000.0).start_day(1000.0)
    state, allowed = ks.on_entry(500.0)  # exactly 0.25 x MLL: not below
    assert allowed and not state.halted
    state, allowed = ks.on_entry(499.99)
    assert state.halted and not allowed
    assert not state.on_entry(2000.0)[1]  # sticky
    assert state.start_day(2000.0).halted
    assert KillSwitches(2000.0).start_day(499.0).halted  # at the start of a date too


def test_ks3_blocks_the_date_after_five_losing_dates_then_resets() -> None:
    ks = KillSwitches(2000.0)
    for _ in range(5):
        ks = ks.start_day(2000.0).end_day(-10.0)
    assert ks.losing_streak == 5
    blocked = ks.start_day(2000.0)
    assert blocked.skip_today and blocked.losing_streak == 0
    assert not blocked.on_entry(2000.0)[1]
    nxt = blocked.end_day(0.0).start_day(2000.0)
    assert not nxt.skip_today


def test_ks3_run_is_broken_by_a_flat_or_winning_date() -> None:
    ks = KillSwitches(2000.0)
    for pnl in (-1.0, -1.0, -1.0, -1.0, 0.0, -1.0):
        ks = ks.start_day(2000.0).end_day(pnl)
    assert ks.losing_streak == 1 and not ks.start_day(2000.0).skip_today


def test_ks4_fires_only_with_a_full_window_below_the_band() -> None:
    mu, sd = 20.0, 100.0  # band: 20 - 3 x 100 / sqrt(40) = 20 - 47.434 = -27.434
    assert not ks4_fires([-100.0] * 39, mu, sd)
    assert ks4_fires([-27.5] * 40, mu, sd)
    assert not ks4_fires([-27.4] * 40, mu, sd)
    assert not ks4_fires([-1000.0] * 10 + [0.0] * 40, mu, sd)  # only the trailing 40 count


def test_ks5_stale_or_missing_inputs_block_entries() -> None:
    # a bar opening at t - 3 min closes at t - 2 min: age 2 min, not older than 2 -> allowed
    assert not ks5_blocks_entry(T - 3 * MIN, T, True)
    assert ks5_blocks_entry(T - 4 * MIN, T, True)  # closed 3 min before t
    assert ks5_blocks_entry(T - MIN, T, False)  # a missing input
    assert ks5_blocks_entry(None, T, True)


def test_ks5_live_flatten_after_five_minutes_without_a_bar() -> None:
    assert not ks5_flatten_due(T - 5 * MIN, T)  # closed 4 min ago
    assert ks5_flatten_due(T - 6 * MIN, T)  # closed 5 min ago
    assert ks5_flatten_due(None, T)


def test_bad_mll_raises() -> None:
    with pytest.raises(ValueError, match="killswitch_bad_mll"):
        KillSwitches(0.0)
