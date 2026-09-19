"""H4 -- Cost-aware passive-fill specification wrapper (methodological, applies to H1-H3).

PRE-REGISTRATION AND CAPABILITY LIMITATION (written before any backtest run;
this file intentionally implements NOTHING and is not screened).

Mechanism as formalized in the research stage: any of H1-H3, but specified
from the start to require resting/limit-style fills (an order left at or
better than the signal bar's close) rather than aggressive market-order
fades, sized against the modelled $2.64/RT MES cost. Robert Carver
(qoppac.blogspot.com, "Very... slow... mean reversion...") is explicit that
"There is no possibility that you would be able to overcome trading costs
unless you were passively filled, with all that implies," after tracing an
apparently strong fast-mean-reversion backtest (Sharpe > 2.0) to a look-ahead
bug once he checked the fill assumption. This is the single most
load-bearing methodological lesson available to this family.

WHY THIS IS NOT IMPLEMENTED HERE: ``strategy/interface.py`` states the
timing contract this project's harness enforces structurally (not a policy
choice this file could opt out of):

    "An accepted intent is a market order. It fills at the NEXT bar's open
    (``sim/fill_model.py``), never at a price the strategy has already seen."

There is no limit/resting order type anywhere in ``strategy/interface.py``,
``rules/xfa_rules.py`` (``OrderIntent`` carries only ``symbol``, ``side``,
``quantity_micros``, ``ts_utc`` -- no limit price, no time-in-force) or
``sim/fill_model.py`` (``side_cost`` prices a market fill against the
calibrated slippage table; there is no queue-position or passive-fill
model). Building a resting-order fill simulator would mean modifying
``sim/engine.py`` and/or ``sim/fill_model.py`` and/or
``strategy/interface.py``, which ABSOLUTE PROHIBITION #4 in this task
explicitly forbids: "Do not modify sim/engine.py, sim/fill_model.py,
strategy/interface.py, ... If your hypothesis needs a capability the harness
lacks, record it as a LIMITATION, do not build around it." A hand-rolled
passive-fill approximation bolted onto a market-order strategy (e.g.
pretending a fill happened only when a later bar's range crossed the
signal-bar close) would not be a real resting-order simulation -- it would
have no queue position, no partial-fill risk, and no adverse-selection
skew, and would risk reproducing exactly the kind of look-ahead bug Carver
traced his own result to. That is a worse outcome than not running it.

WHAT THIS MEANS FOR H1-H3: every fill measured for H1, H2 and H3 in this
Stage D.1 screening is a MARKET fill at the next bar's open, priced against
the modelled $2.64/RT MES slippage+commission table. Per Carver's finding
and per this repository's own ORBExperiment lesson (measured slippage ran
11.27x the assumed model on a sibling project), any pass those three
hypotheses show under a market-fill assumption should be read as an UPPER
BOUND on what a passive-fill version could achieve, not a result that has
already cleared the passive-fill bar. A hypothesis that only clears the
robust screen at market-fill cost has NOT satisfied H4's constraint, and
should be reported to the lead as "passed under an aggressive-fill
assumption only" rather than as a clean pass.

SUPPORT CONDITION: not applicable -- H4 is a constraint on how H1-H3 would
need to be re-specified with a passive-fill capability this harness does
not have, not an independently testable signal. It cannot be supported or
refuted by this session's data; the honest status is "untestable this
session," recorded as a LIMITATION, not a null result.

REFUTE CONDITION: not applicable, for the same reason.

STATUS: NOT IMPLEMENTED. NOT SCREENED. Recorded as a LIMITATION of this
Stage D.1 run: the harness has no passive/limit order capability, so no
formalization of H4 can be backtested this session.

Stage D.1b (2026-09-18): implemented as h4_passive_fill_reversal.py using
limit_intent (interface v2); screened as trial #24.
"""

from __future__ import annotations

H4_IMPLEMENTED = False
H4_STATUS = "not_implemented_capability_limitation"
