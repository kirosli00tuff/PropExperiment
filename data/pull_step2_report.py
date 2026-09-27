"""Stage E.2b Task 4: reports/stage_e2b_step2_quotes.md from the quotes JSON (costs, counts).

``render_markdown`` turns data.pull_step2's quotes payload (one section per request set) into
the markdown table the lead reads: set totals, per cluster, per contract, failures, and the
acct-2 top-up each set needs. Pure: no ledger read, no vendor call.
"""

from __future__ import annotations

from typing import Any

SET_TITLES = {
    "ml-route": "(a) ML route: the 31 price-path contracts (docs/STAGE_E_ML_DESIGN.md M1)",
    "clusters": "(b) Each cluster's chosen vehicles (reports/stage_e2a_vehicles.json, status "
                "\"chosen\")",
    "clusters-legs": "(b2) Each cluster's purchase: traded vehicles (chosen or undersized, R10) "
                     "plus every leg root its members read (frozen catalog; MES excluded; K8 "
                     "legs only)",
}


def _usd(x: float | None) -> str:
    return "n/a" if x is None else f"${x:,.2f}"


def _account(payload: dict[str, Any]) -> list[str]:
    a = payload.get("account", {})
    return [
        "## acct-2 by the gate's own arithmetic",
        "",
        f"- Spent on {a.get('account')} (sum of `usd` over this repo's {a.get('account')} ledger "
        f"lines, SpendGate.account_spent_usd): **${a.get('spent_usd', 0):.6f}**",
        f"- Account cap ACCOUNT_2_CAP_USD: ${a.get('account_cap_usd', 0):.2f}; cap headroom "
        f"**${a.get('cap_headroom_usd', 0):.6f}**",
        f"- Credit when opened (U5): ${a.get('account_credit_usd', 0):.2f}; credit left "
        f"**${a.get('credit_left_usd', 0):.6f}**",
        f"- Session {payload.get('session_id')}: session cap "
        f"${payload.get('session_cap_usd', 0):.2f}, request cap "
        f"${payload.get('request_cap_usd', 0):.2f} (quotes only)",
        "",
    ]


def _set_lines(section: dict[str, Any]) -> list[str]:
    title = SET_TITLES.get(section["set"], section["set"])
    status = "complete" if section["complete"] else (
        f"INCOMPLETE: {section['chunks_failed']} chunk quote(s) failed")
    lines = [
        f"## {title}",
        "",
        f"- {section['contracts']} contracts, {section['chunks']} chunks, "
        f"{section['chunks_quoted']} quoted, {status}",
        f"- **Total quoted {_usd(section['total_usd'])}**; with 10% (D13's session-cap rule) "
        f"{_usd(section['total_usd'] * 1.10)}",
        f"- acct-2 top-up needed: {_usd(section['topup_usd_at_quote'])} at the quote, "
        f"{_usd(section['topup_usd_at_quote_plus_10pct'])} at quote + 10%; ACCOUNT_2_CAP_USD "
        f"would have to be at least {_usd(section['account_cap_needed_usd_at_quote'])} "
        f"({_usd(section['account_cap_needed_usd_at_quote_plus_10pct'])} with 10%)",
        "",
        "| Cluster | Contracts | Quoted | Top-up at quote | Top-up at quote + 10% | Complete |",
        "|---|---|---:|---:|---:|---|",
    ]
    for cluster, row in section["per_cluster"].items():
        lines.append(f"| {cluster} | {', '.join(row['contracts']) or '(none)'} | "
                     f"{_usd(row['usd'])} | {_usd(row['topup_usd_at_quote'])} | "
                     f"{_usd(row['topup_usd_at_quote_plus_10pct'])} | "
                     f"{'yes' if row['complete'] else 'NO'} |")
    lines += ["", "| Contract | Cluster | Quoted | 2019-05..2024-02 (kept) | "
              "2024-03..2025-03 (sealed) | Largest chunk | Chunks quoted | Failed chunks |",
              "|---|---|---:|---:|---:|---:|---:|---|"]
    for root, row in section["per_contract"].items():
        failed = ", ".join(row["failed"][:6]) + (" ..." if len(row["failed"]) > 6 else "")
        lines.append(f"| {root} | {row['cluster']} | {_usd(row['usd'])} | "
                     f"{_usd(row['usd_unsealed_2019_05_2024_02'])} | "
                     f"{_usd(row['usd_sealed_2024_03_2025_03'])} | "
                     f"{_usd(row['largest_chunk_usd'])} | {row['quoted']}/{row['chunks']} | "
                     f"{failed or '-'} |")
    return [*lines, ""]


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage E.2b step 2 quotes (free; $0.00 quote lines only)",
        "",
        f"Session {payload.get('session_id')}, {payload.get('dataset')} "
        f"{payload.get('schema')}, {payload.get('range')}. Written by "
        "`python -m data.pull_step2 --quote-only`; costs, bytes and counts only. Nothing was "
        "bought and no cap was changed.",
        "",
        *_account(payload),
        "Reading the tables: a set's top-up buys the whole set against today's credit; a "
        "cluster's top-up is that cluster ALONE against today's credit (cluster top-ups do not "
        "add up). Lead ruling OC-R: a contract listed after 2019-05 is planned from its first "
        "vendor-priceable month (MBT 2021-04, MCL 2021-06, MHG 2022-04); earlier months are not "
        "requested and not counted. A failed chunk quote inside a plan carries its cause in the "
        "ledger's quote line and is priced at nothing in these totals.",
        "",
    ]
    for name in ("ml-route", "clusters", "clusters-legs"):
        if name in payload.get("sets", {}):
            lines += _set_lines(payload["sets"][name])
    return "\n".join(lines) + "\n"
