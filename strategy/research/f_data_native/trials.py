"""Stage D.1b Family F: the hypotheses formalized in Task 2c. Deliberately empty.

The selection rule in reports/stage_d1b_family_f_declaration.md (section 2, fixed before
any computation) admitted no stylized fact: the only directional-eligible statistics that
survived BH at FDR 10% (F1.2 VR5 RTH, F1.2 VR60 ETH) imply at most ~0.12 ticks per trade
of gross edge, far below the declared 2.11-tick bar (and the 0.98-tick passive bar). Zero
hypotheses formalized means zero Family F trials; see progress.md, Stage D.1b, Task 2c.
"""

from __future__ import annotations

from collections.abc import Callable

F_TRIALS: tuple[tuple[str, Callable[[], object]], ...] = ()
