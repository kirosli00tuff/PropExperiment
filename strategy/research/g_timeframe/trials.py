"""Family G hypotheses formalized under the declaration's selection rule (section 5).

Filled only from ``reports/stage_d1d_family_g_facts.json`` -> ``selection.formalized``,
after the sweep ran; each entry would be built mechanically from the declared template
(traded side = sign(statistic) x d, market entry on the event bar's completion, exit on
the next coarse bar's completion or, for G3, at the RTH segment end, 1 micro, frozen Q80).
An empty tuple means the rule admitted nothing, which the declaration allows for.
"""

from __future__ import annotations

from collections.abc import Callable

G_TRIALS: tuple[tuple[str, Callable[[], object]], ...] = ()
