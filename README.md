# PropExperiment

Automated futures trading bot targeting the Topstep Combine and Express
Funded Account (XFA) via the TopstepX / ProjectX Gateway API.

**Scope lock (2026-09): XFA only.** No LFA rules engine, no second-firm
adapter, no IBKR adapter, no broker-agnostic abstraction layer built ahead
of need. Those are notes, not code, until a strategy is profitable and the
call-up question becomes real. See docs/DECISIONS.md.

Instrument: MES (primary). Venue: TopstepX API. Data: Databento GLBX.MDP3.
