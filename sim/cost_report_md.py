"""Markdown rendering of the frozen Stage E cost table (reports/stage_e2a_costs.md)."""

from __future__ import annotations

from pathlib import Path

COMPUTE_NOTE = (
    "Compute (overnight profile): `free -m` before each run showed 10.3 GB available; peak "
    "estimate 1 GB per process (1M-record decode chunks, derived arrays and the per-contract "
    "histogram line), kept under a third of available memory with at most two processes at "
    "once. Measured peaks 0.54 and 0.84 GB RSS (the 44-contract run, 02:02-02:03 PDT, two "
    "single-threaded processes) and 0.89 GB (MBT, 02:13 PDT, after the crypto calendar "
    "loaded); nice 10; resumable per contract (one JSONL line per finished contract under the "
    "session scratchpad, `costs/calibration_raw_*.jsonl`). A first run at 01:44 PDT, made "
    "before the 10x-grid scale counter was added, was discarded whole and re-run with the "
    "final code; its figures were identical where comparable."
)


def _n(x: float | None, nd: int = 3) -> str:
    return "-" if x is None else f"{x:.{nd}f}"


def _summary(table: dict) -> list[str]:
    out = [
        "| Contract | Group | Tick | Tick $ | Comm. RT $ | Comm. ticks | q_c | Day buckets "
        "| RT ticks mean [min, max] | RT $ mean [min, max] | Event side ticks buy / sell "
        "| Fallback buckets (all / day) |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for root, p in table["products"].items():
        if not p["calibrated"]:
            out.append(f"| {root} | {p['group']} | {p['tick_size']} | {p['tick_value_usd']} | "
                       f"{p['commission_rt_usd']:.2f} | {_n(p['commission_rt_ticks'])} | "
                       f"{p['q_c'] if p['q_c'] is not None else 'pending'} | - | UNCALIBRATED: "
                       f"{p['uncalibrated_reason']} | - | - | - |")
            continue
        h = p["headline_day_session"]
        rt, usd = h["round_turn_ticks"], h["round_turn_usd"]
        ev = p["event_window_side_ticks"]
        out.append(
            f"| {root} | {p['group']} | {p['tick_size']} | {p['tick_value_usd']} | "
            f"{p['commission_rt_usd']:.2f} | {_n(p['commission_rt_ticks'])} | "
            f"{p['q_c'] if p['q_c'] is not None else 'pending'} | {h['n_buckets']} "
            f"({h['first_bucket']}-{h['last_bucket']}) | {_n(rt['mean'])} [{_n(rt['min'])}, "
            f"{_n(rt['max'])}] | {_n(usd['mean'], 2)} [{_n(usd['min'], 2)}, {_n(usd['max'], 2)}] "
            f"| {_n(ev['buy'])} / {_n(ev['sell'])} | {len(p['fallback_buckets'])} / "
            f"{len(h['fallback_buckets'])} |")
    return out


def _flags(table: dict) -> list[str]:
    out: list[str] = []
    for root, p in table["products"].items():
        if not p["calibrated"]:
            out.append(f"- **{root}: the rule cannot calibrate it** ({p['uncalibrated_reason']}); "
                       "no extra data were used.")
        elif p["fallback_buckets"]:
            dates = {b["key"]: b["dates_with_quotes"] for b in p["buckets"]}
            items = ", ".join(f"{k} ({dates[k]}/5)" for k in p["fallback_buckets"])
            out.append(f"- {root}: fallback buckets {items}")
        if not p["vendor_tick_check"]["passed"]:
            out.append(f"- **{root}: vendor tick check FAILED** "
                       f"(min quoted spread {p['vendor_tick_check']['min_quoted_spread_ticks']} "
                       "ticks)")
    return out or ["- none: every bucket of every contract is quoted on at least 3 of 5 dates."]


def _depth(table: dict) -> list[str]:
    if table["depth_term"] != "applied":
        return ["- pending the Task 9 sizes file."]
    out = ["A contract with q_c = 1 never pays a depth term (a valid book has at least one "
           "contract at the top). Contracts with a non-zero depth term in any bucket:", ""]
    for root, p in table["products"].items():
        if not p["calibrated"]:
            continue
        hit = [b for b in p["buckets"]
               if (b["depth_ticks"]["buy"] or 0) > 0 or (b["depth_ticks"]["sell"] or 0) > 0]
        if hit:
            day = [b for b in hit if b["day_session"]]
            worst = max(max(b["depth_ticks"]["buy"] or 0, b["depth_ticks"]["sell"] or 0)
                        for b in hit)
            out.append(f"- {root} (q_c {p['q_c']}): {len(hit)} of {len(p['buckets'])} buckets "
                       f"({len(day)} in the day session), largest one-side depth term "
                       f"{worst:.3f} ticks")
    return out if len(out) > 2 else ["- none."]


def _calendar_changes(table: dict) -> list[str]:
    changed = sorted(r for r, p in table["products"].items()
                     if p.get("calendar_sha256_at_build", p["calendar_sha256"])
                     != p["calendar_sha256"])
    if not changed:
        return []
    return [f"Calendar modules changed after calibration for {', '.join(changed)} (for the "
            "equity group, data/calendars/equity.py appeared at 02:26 PDT). The build "
            "recomputed every sample date's buckets from the current modules and found them "
            "identical to the nanosecond, so the calibration stands; both hashes are in the "
            "json (calendar_sha256 at calibration, calendar_sha256_at_build).", ""]


def _data_notes(table: dict) -> list[str]:
    out = [
        "| Contract | Records | Midnight snapshots | Instrument switches | Empty rec / s | "
        "Locked rec / s | Crossed rec / s | Unknown s | Vendor factor | Prices off tick grid "
        "| Prices off 10x grid / checked | Min spread ticks | Scale check |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for root, p in table["products"].items():
        ds = p["date_stats"].values()
        recs = sum(d["records"] for d in ds)
        snaps = sum(d.get("snapshot_records", 0) for d in ds)
        sw = sum(len(d["instrument_switches"]) for d in ds)
        buckets = p["buckets"] if p["calibrated"] else []
        drop = {k: (sum(b["dropped"][k]["records"] for b in buckets),
                    sum(b["dropped"][k]["seconds"] for b in buckets))
                for k in ("empty", "locked", "crossed")}
        unk = sum(b["unknown_seconds"] for b in buckets)
        vt = p["vendor_tick_check"]
        out.append(f"| {root} | {recs:,} | {snaps} | {sw} | {drop['empty'][0]:,} / "
                   f"{drop['empty'][1]:.1f} | {drop['locked'][0]:,} / {drop['locked'][1]:.1f} | "
                   f"{drop['crossed'][0]:,} / {drop['crossed'][1]:.1f} | {unk:.3f} | "
                   f"{vt['vendor_price_factor']} | {vt['prices_off_vendor_tick_grid']} | "
                   f"{vt['prices_off_10x_vendor_tick_grid']:,} / "
                   f"{vt['valid_bid_ask_prices_checked']:,} | {vt['min_quoted_spread_ticks']} | "
                   f"{'pass' if vt['passed'] else 'FAIL'} |")
    return out


def _mes(table: dict) -> list[str]:
    m = table["mes_check"]
    out = [m["method"], "", "Source: " + m["source"] + ".", "",
           "| Bucket CT | D.1 MES 15-min half-spreads | MES s_b (D8) | MES RT ticks | MES RT $ "
           "| MNQ s_b | MNQ RT ticks | MNQ RT $ |",
           "|---|---|---|---|---|---|---|---|"]
    for r in m["rows"]:
        if "mes_s_b_ticks" not in r:
            out.append(f"| {r['key']} | {r['note']} | | | | | | |")
            continue
        out.append(f"| {r['key']} | {r['mes_d1_15min'][0]:.4f}, {r['mes_d1_15min'][1]:.4f} | "
                   f"{r['mes_s_b_ticks']:.4f} | {r['mes_round_turn_ticks']:.4f} | "
                   f"{r['mes_round_turn_usd']:.3f} | {_n(r.get('mnq_half_spread_ticks'), 4)} | "
                   f"{_n(r.get('mnq_round_turn_ticks'), 4)} | {_n(r.get('mnq_round_turn_usd'))} |")
    day = m["day_session_0830_1500"]
    out += ["", "Day session 08:30-15:00 CT (13 buckets), mean [min, max]:", ""]
    for key, label in (("mes_s_b_ticks", "MES s_b ticks"),
                       ("mes_round_turn_ticks", "MES round turn ticks"),
                       ("mes_round_turn_usd", "MES round turn USD"),
                       ("mnq_half_spread_ticks", "MNQ s_b ticks"),
                       ("mnq_round_turn_ticks", "MNQ round turn ticks"),
                       ("mnq_round_turn_usd", "MNQ round turn USD")):
        s = day.get(key)
        text = "-" if s is None else (
            f"{s['mean']:.4f} [{s['min']:.4f}, {s['max']:.4f}] (n={s['n']})")
        out.append(f"- {label}: {text}")
    out += ["", "All buckets (every 30-minute bucket both tables have), mean [min, max]:", ""]
    for key, s in m["all_buckets"].items():
        text = "-" if s is None else (
            f"{s['mean']:.4f} [{s['min']:.4f}, {s['max']:.4f}] (n={s['n']})")
        out.append(f"- {key}: {text}")
    out += ["", m["d8_text_reference"], ""]
    out += ["", "Documented differences:"] + [f"- {d}" for d in m["differences"]]
    return out


def _contract(root: str, p: dict) -> list[str]:
    out = [f"### {root} ({p['group']})", "",
           f"Tick {p['tick_size']} (vendor units {p['vendor_tick']}, factor "
           f"{p['vendor_price_factor']}), tick value ${p['tick_value_usd']}; commission "
           f"${p['commission_rt_usd']:.2f} round turn = {p['commission_rt_ticks']:.4f} ticks "
           f"({p['commission_source']}); q_c "
           f"{p['q_c'] if p['q_c'] is not None else 'PENDING (depth term not applied)'}; D6 day "
           f"session {p['day_session_ct']['open']}-{p['day_session_ct']['close']} CT.", ""]
    if not p["calibrated"]:
        return out + [f"UNCALIBRATED: {p['uncalibrated_reason']}", ""]
    ev = p["event_window_side_ticks"]
    out += [f"Event-window one-side slippage: buy {ev['buy']:.4f}, sell {ev['sell']:.4f} ticks "
            f"(round turn inside a window {p['event_window_round_turn_ticks']:.4f} ticks).", "",
            "| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid "
            "| Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in p["buckets"]:
        d = b["depth_ticks"]
        s = b["side_ticks"]
        out.append(
            f"| {b['start']}-{b['end']} | {'D' if b['day_session'] else ''} | "
            f"{b['dates_with_quotes']}/5 | {'FALLBACK' if b['fallback'] else ''} | "
            f"{_n(b['half_spread_ticks'], 4)} | {_n(b['half_spread_ticks_equal_date_weights'], 4)}"
            f" | {b['median_top_size']['bid'] if b['median_top_size']['bid'] is not None else '-'}"
            f" | {b['median_top_size']['ask'] if b['median_top_size']['ask'] is not None else '-'}"
            f" | {_n(d['buy'], 3)} / {_n(d['sell'], 3)} | {s['buy']:.4f} / {s['sell']:.4f} | "
            f"{b['round_turn_ticks']:.4f} | {b['round_turn_usd']:.3f} |")
    out += ["", "Input files (sha256 verified against reports/stage_e1_purchase.json before "
            "decoding):", ""]
    out += [f"- `{x['path']}` {x['sha256']} ({x['records']:,} records)" for x in p["files"]]
    return out + [""]


def _sensitivity(table: dict) -> list[str]:
    worst = []
    for root, p in table["products"].items():
        for b in p.get("buckets", []) if p["calibrated"] else []:
            a, e = b["half_spread_ticks"], b["half_spread_ticks_equal_date_weights"]
            if a is not None and e is not None:
                worst.append((abs(a - e), root, b["key"], a, e))
    worst.sort(reverse=True)
    out = ["Reading R2's alternative (each date weighted equally instead of by its valid time) "
           "changes s_b by at most the following (largest five over all buckets):", ""]
    out += [f"- {r} {k}: pooled {a:.4f} vs equal-date {e:.4f} (|diff| {d:.4f})"
            for d, r, k, a, e in worst[:5]]
    return out


def write_md(table: dict, path: Path) -> None:
    pending = table["depth_term"] == "pending"
    lines = [
        "# Stage E.2a Task 8: per-product cost model (design D8)", "",
        f"Generated {table['generated_pdt']} by CostCoder-OpusXHigh. Rule: {table['rule']}. "
        f"Machine-readable table: reports/stage_e2a_costs.json (loaded by "
        "`sim.product_costs`). Code: sim/cost_inputs.py, sim/calibrate_costs.py, "
        "sim/cost_rule.py, sim/cost_report.py, sim/cost_report_md.py, sim/product_costs.py; "
        "tests: tests/test_e2a_costs.py.", "",
    ]
    if pending:
        lines += ["**STATUS: PROVISIONAL. The depth term is PENDING the Task 9 sizes file "
                  "(reports/stage_e2a_vehicle_sizes.json); every side and round-turn figure "
                  "below is the half-spread part only (depth term 0).** "
                  "`sim.product_costs.load_cost_table` refuses this table unless asked for a "
                  "provisional one.", ""]
    else:
        vs = table["vehicle_sizes"]
        lines += [f"STATUS: FROZEN. Depth term applied at q_c from `{vs['path']}` "
                  f"(sha256 {vs['sha256']}).", ""]
    lines += [
        f"Sample: mbp-1, the five trade dates {', '.join(table['sample_dates'])}; "
        f"{len(table['products_calibrated'])} of {table['products_expected']} contracts "
        f"calibrated; not calibrated: {', '.join(table['products_uncalibrated']) or 'none'}; "
        f"missing from this build: "
        f"{', '.join(sorted(set(_expected()) - set(table['products']))) or 'none'}.", "",
        "## Headline per contract (day session, O to C of D6)", "",
        "Round turn (RT) = commission/tick value + buy-side + sell-side slippage in the same "
        "bucket; mean and range over the buckets overlapping [O, C) (reading R9).", "",
        *_summary(table), "",
        "## Flags", "", *_flags(table), "",
        "## Depth term at q_c", "", *_depth(table), "",
        "## Readings of the rule", "",
        *[f"- {r}" for r in table["readings"]], "",
        *_sensitivity(table), "",
        "## Known limitations (recorded, not corrected)", "",
        *[f"- {x}" for x in table["limitations"]], "",
        "## Data handling", "",
        "Every file's sha256 was checked against the E.1 manifest before decoding, and its "
        "record count against the manifest after. Databento writes one snapshot record per "
        "file at 00:00:00 UTC (flags SNAPSHOT and BAD_TS_RECV, ts_event = the book's last "
        "change, which is why 11 files show a first ts_event before their request window); it "
        "restates the standing book and is used as a state. RB's v.0 changed instrument at "
        "00:00 UTC on 2025-05-14, 2025-08-13 and 2025-11-12 (the new instrument's first record "
        "is that snapshot, so the old book ends exactly there). MNQ 2025-11-12 and 2026-02-11 "
        "are three contiguous request pieces each, streamed as one.", "",
        "Price scale (declared in sim/cost_inputs.py VENDOR_PRICE_FACTOR, verified here per "
        "product on every valid book state of the five dates): Databento quotes ZC, ZW, ZS, ZL, "
        "HE and LE in US cents, so their vendor-unit tick is 100 x the E.0 tick_size (USD); all "
        "others are factor 1. The check passes when every valid bid and ask lies on the "
        "vendor-unit tick grid (any off-grid price refuses the calibration), some lie off the "
        "grid of 10 x that tick, and a one-tick quoted spread occurs. Half-spreads are in "
        "vendor-unit ticks; USD = ticks x tick_value_usd.", "",
        "Crossed books inside open time are short (seconds) and cluster in a few buckets (for "
        "example CL and MCL 18:30 CT on 2026-04-15, GC and MGC 04:30 CT on 2026-02-11), which "
        "looks like CME's brief reserve states after fast moves; they are dropped as D8 says "
        "and counted below.", "",
        *_calendar_changes(table),
        *_data_notes(table), "",
        COMPUTE_NOTE, "",
        "## MES check", "",
        *_mes(table), "",
        "## Per-contract tables", "",
        "Columns: dates quoted (of 5); s_b = pooled time-weighted mean half-spread (ticks); "
        "s_b equal-date = R2's alternative (not used); median top sizes (lower, time-weighted); "
        "depth term per side at q_c; final one-side slippage per side (fallback applied); round "
        "turn in ticks and USD. 'D' marks a day-session bucket.", "",
    ]
    for root, p in table["products"].items():
        lines += _contract(root, p)
    path.write_text("\n".join(lines) + "\n")


def _expected() -> list[str]:
    from sim.cost_inputs import mbp1_files

    return sorted(mbp1_files())
