"""B4 LT3 addition (protocol P4.1 LT3 last clause, P6.1): the embargo of 21 trade dates covers every label's span and
every feature look-back. SearchCoder's pipeline/tests/test_search33.py carries the other LT3 unit tests (training
rows, scaler, calibrator, mu_k, early stopping, LightGBM bins); this file adds the embargo check on the real
796-date fold layout (calendar only; no market data and no outcome is read).

Look-back of each feature in trade dates before D, derived from P0.3 and P4 (the declared table below):
- sigma_X(D), every trailing 20-date reference (C.5 Vbar, F2.8-F2.11 Obar, F3.1-F3.4 Obar and Dbar, F3.10 sbar,
  F3.11 rbar, F3.12 median slope) and C.6: the 20 trade dates before D -> 20.
- F1.3: the 10 trade dates before D -> 10.
- F1.7 and F4.7: sd over the 20 trade dates before D of a gap that uses the 13:15 mid of the trade date before each
  of them -> 21 (P6.1: "reach the 13:15 mid of the 21st date back").
- Windows in minutes (C.5 V(15), F1.1 30, F1.2 120, F1.4, F1.5, F2.*, F3.* up to 60, F4.1-F4.5 up to 60, F4.10-F4.12)
  stay inside D's own ts_recv window ([D-1 16:00, D 16:00) CT) except on a scheduled late open or after an early
  close, where the open-time axis reaches the previous trade date -> at most 1 (B-LATE-1).
- C.7 (expiration), C.8-C.10, C.15: calendar or the front's definition as of 08:30 on D -> 0 market-data dates.
- Labels: every span ends on D by 13:13 (P3.6 rule 2) -> 0 dates after D.
"""

from __future__ import annotations

import sys
from pathlib import Path

PIPE = Path(__file__).resolve().parents[1]
if str(PIPE) not in sys.path:
    sys.path.insert(0, str(PIPE))

import cal33  # noqa: E402
import search33 as s  # noqa: E402

LOOKBACK_TRADE_DATES = {
    "sigma_and_20_date_references": 20,
    "F1_3_ols_10_dates": 10,
    "F1_7_F4_7_gap_sd": 21,
    "minute_windows_late_open": 1,
    "calendar_and_definitions": 0,
}
LABEL_SPAN_DATES_AFTER_D = 0
MAX_LOOKBACK = max(LOOKBACK_TRADE_DATES.values())


def test_oof_dates_are_the_universe_after_burn_in() -> None:
    """Fold arithmetic in OOF positions equals arithmetic in trade dates (excluded dates stay in the OOF list)."""
    td = list(cal33.trade_dates())
    oof = list(cal33.oof_dates())
    assert len(td) == 816 and len(oof) == 796 and oof == td[20:]


def test_embargo_covers_longest_lookback_and_label_spans() -> None:
    assert s.EMBARGO == 21 and MAX_LOOKBACK == 21
    assert s.EMBARGO >= MAX_LOOKBACK  # equality suffices: see the per-fold check below
    oof = [d.isoformat() for d in cal33.oof_dates()]
    pos = {d: k for k, d in enumerate(oof)}
    for f in s.make_folds(oof):
        ev = [pos[d] for d in f.eval_dates]
        lo, hi = min(ev), max(ev)
        tr = [pos[d] for d in f.train_dates]
        after = [p for p in tr if p > hi]
        before = [p for p in tr if p < lo]
        # a training date after the block: its earliest look-back date lies after the evaluation block
        if after:
            assert min(after) - MAX_LOOKBACK > hi, f.k
            assert min(after) == hi + 1 + s.EMBARGO, f.k
        # a training date before the block: its label ends on its own date, before the block
        if before:
            assert max(before) + LABEL_SPAN_DATES_AFTER_D < lo, f.k
        assert not set(tr) & set(ev)


def test_builders_load_at_most_21_history_dates() -> None:
    """Coder-A's feature builder keeps N_HIST = 21 history dates; Coder-B's builder N_HIST_RAW = 21."""
    import build_features33 as bf
    import feat33 as fa

    assert fa.N_HIST == 21
    d = cal33.oof_dates()[100]
    hist = bf.history(d)
    assert len(hist) == 21 and hist[0] == cal33.previous_trade_dates(d, 21)[0]
    implb = PIPE.parent / "implB" / "build_featB.py"
    assert "N_HIST_RAW = 21" in implb.read_text()
