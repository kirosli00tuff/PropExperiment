"""pytest plugin for the K7 audit's mutants: when K7_MUTANT_DIR is set, the copy of the K7
package under it (<dir>/k7/*.py) shadows strategy/members/k7 for every import made after
configuration. The repository tree is never modified."""

from __future__ import annotations

import os


def pytest_configure(config) -> None:  # noqa: ARG001
    mdir = os.environ.get("K7_MUTANT_DIR")
    if not mdir:
        return
    import strategy.members  # the harness-provided empty package

    path = list(strategy.members.__path__)
    if mdir not in path:
        strategy.members.__path__ = [mdir, *path]  # type: ignore[attr-defined]
