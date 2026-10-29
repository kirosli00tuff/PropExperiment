import json, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / ".." / "stage_e34_data_facts.md"
OUT = (HERE.parents[2] / "stage_e34_data_facts.md").resolve()
a = json.load(open(HERE / "agg_zl.json")); sd = json.load(open(HERE / "schema_defs.json"))
now = datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M %Z")
t = a["tot"]; fl = a["flags"]; sd_rows = sd["zl_defs"]
sym = {k: v["raw_symbol"] for k, v in sd_rows.items()}
roll = ["| trade date | from id (symbol) | to id (symbol) |", "|---|---|---|"]
for c in a["dominant_id_changes"]:
    roll.append(f"| {c['date']} | {c['from']} ({sym[c['from']]}) | {c['to']} ({sym[c['to']]}) |")
deft = ["| instrument_id | raw_symbol | expiration (UTC) | min_price_increment (1e-9 units) | definition records |", "|---|---|---|---|---|"]
for i, r in sorted(sd_rows.items(), key=lambda kv: kv[1]["expiration_utc_ns"]):
    exp = datetime.fromtimestamp(r["expiration_utc_ns"] / 1e9, timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    deft.append(f"| {i} | {r['raw_symbol']} | {exp} | {r['min_price_increment']:,} | {r['n_records']} |")
opens = (HERE / "opens.log").read_text().splitlines()
first = opens[0].split("\t")[0]
side = ", ".join(f"{k} {v:,}" for k, v in sorted(a["side"].items()))
subs = {"NOW": now, "NOPENS": str(len(opens)), "DRYTIME": first, "DRYCHECK": (HERE / "dry_check.out").read_text().rstrip(),
        "DEC": f"{t['ts_recv_decreases']}", "EVAFTER": f"{t['ts_event_after_ts_recv']:,}",
        "EVAFTERPCT": f"{100*t['ts_event_after_ts_recv']/a['records_read']:.3f}", "EVB1S": f"{t['ts_event_before_ts_recv_by_over_1s']:,}",
        "EVB1D": f"{t['ts_event_before_ts_recv_by_over_1d']:,}", "FLAST": f"{fl['F_LAST']:,}", "FSNAP": f"{fl['F_SNAPSHOT']:,}",
        "FBADTS": f"{fl['F_BAD_TS_RECV']:,}", "FBADBOOK": f"{fl['F_MAYBE_BAD_BOOK']:,}", "SIDE": side,
        "DECSEC": f"{a['decode_seconds_sum']}", "TAB_DAILY": (HERE / "tab_daily.md").read_text().rstrip(),
        "TAB_ACT": (HERE / "tab_action_seg.md").read_text().rstrip(), "TAB_BARS": (HERE / "tab_bars.md").read_text().rstrip(),
        "TAB_BARSY": (HERE / "tab_bars_year.md").read_text().rstrip(), "ROLLTAB": "\n".join(roll), "DEFTAB": "\n".join(deft),
        "DFTIME": now}
s = (HERE / "report_template.md").read_text()
for k, v in subs.items(): s = s.replace("{{" + k + "}}", v)
assert "{{" not in s, [x for x in s.split("{{")[1:3]]
OUT.write_text(s)
print(OUT, len(s.splitlines()))
