"""Multi-day reads and book files (Stage E.24 Part A, V41; E.23 VerdictVerifier NOTE-2, NOTE-5).

A new package because every file the notes name is frozen: base_rules/*.py (the E.16 guardrail
and the E.16, E.21, E.23 freezes), multiday/*.py (E.21, E.23) and trigger_hold/*.py (E.23); those
freezes also refuse any NEW file in those directories (reports/stage_e24_briefs/loader/pins.md).

- ``mdio.bounded``: a run context's bars loaded only through the read window's last trade date
  (ctx.last): stores whose name puts them after it are never opened, parquet row groups wholly
  after it are never decoded, a straddling row group is filtered before any row reaches pandas,
  and every loaded row is checked against the bound.
- ``mdio.book_files``: per-unit and per-fill records of multi-day books in E.21's per-root layout.
- ``mdio.trigger_books``: the E.23 trigger-hold read of one root (trigger_hold.evaluate.read_root,
  mirrored line for line) that also returns the per-root book record.
"""
