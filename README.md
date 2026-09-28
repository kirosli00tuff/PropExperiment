# PropExperiment

Automated futures trading bot targeting the Topstep Combine and Express
Funded Account (XFA) via the TopstepX / ProjectX Gateway API.

## About this project

I'm building a self-running trading bot for prop firm funded accounts,
focused on CME micro futures, starting with Topstep's XFA. The goal is a
bot that trades on its own through the TopstepX API and stays inside the
firm's rules: flat by 3:10 PM CT, within the trailing drawdown and the
lot limits.

I build it with Claude Code and my own programming knowledge. I set the
direction, make the decisions and review every result. Claude Code
sessions do most of the coding, research and checking from written stage
prompts, and a second model audits their work. Machine learning is used
only offline, to search for strategies. The bot that trades runs plain,
fixed rules.

The research is pre-registered. Every strategy is written down and frozen
before it sees data, screened once on recent data, and confirmed on older
data it has never seen before any edge is claimed. Most ideas fail, and
the failures are kept as results. No strategy has passed yet (see
progress.md).

**Scope lock (2026-09): XFA only.** No LFA rules engine, no second-firm
adapter, no IBKR adapter, no broker-agnostic abstraction layer built ahead
of need. Those are notes, not code, until a strategy is profitable and the
call-up question becomes real. See docs/DECISIONS.md.

Instrument: MES (primary). Venue: TopstepX API. Data: Databento GLBX.MDP3.
