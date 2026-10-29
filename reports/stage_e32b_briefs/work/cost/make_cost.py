"""Stage E.32b session cost: tokens per model, per worker spawn, per session, and delegation share, for the four lead
sessions of the stage and every subagent transcript under them.

Adapted from reports/stage_e26_briefs/cost.py (itself reports/stage_e10_briefs/cost.py with rglob over
subagents/**/agent-*.jsonl). The scan is the E.10 scan: a streamed assistant message is logged once per content block
with growing usage, so the per-field MAXIMUM over a message's records (its final usage) is kept, keyed by
(message id, request id). E.4's first-record scan undercounts output and is not used.

Usage: python3 reports/stage_e32b_briefs/work/cost/make_cost.py <to ISO UTC> [<from ISO UTC>]
  <to>   exclusive upper bound, e.g. 2026-10-29T17:30:00Z (the stage's final end time, UTC).
  <from> inclusive lower bound, default 2026-10-29T05:00:00Z (the stage started 22:06 PDT = 05:06 UTC; session 1's
         first record is 05:06:09Z, so no pre-stage usage is in any of the four transcripts; see README.md).
Writes cost_raw.txt and ret_cost_tokens.md next to this script. Token counts only, read from the transcripts'
message.usage fields; nothing is estimated. Reads only those transcripts and their *.meta.json files.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PROJ = Path.home() / ".claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment"
OUT = Path(__file__).resolve().parent
PDT = ZoneInfo("America/Vancouver")
SESSIONS = (
    (1, "3d79635b-4dfe-4992-b743-c48717efe7fc"),
    (2, "7e35d21b-f567-499d-aaa7-6117610c9a16"),
    (3, "3860d0d1-cf19-46b3-a4da-6fda65b58c32"),
    (4, "0d036ce2-d1e2-4d45-9a12-484b421ab30e"),
)
DEFAULT_FROM = "2026-10-29T05:00:00Z"
FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
PAUSE_MIN = 30  # idle gap (minutes) over the union of a session's lead and subagent timestamps reported as a pause


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def pdt(ts: str | None) -> str:
    return "-" if not ts else parse_ts(ts).astimezone(PDT).strftime("%m-%d %H:%M:%S")


def tier(model: str) -> str:
    m = model.lower()
    for name in ("opus", "sonnet", "haiku", "fable"):
        if name in m:
            return name
    return "other"


def scan(path: Path, lo: str, hi: str):
    """Return (per_model {model: [in, out, cread, ccreate]}, msgs, first_usage_ts, last_usage_ts, all_ts list)."""
    per_msg: dict = {}
    model_of: dict = {}
    first = last = None
    stamps: list[str] = []
    for line in path.open(encoding="utf-8"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = e.get("timestamp") or ""
        if not (lo <= ts < hi):
            continue
        stamps.append(ts)
        msg = e.get("message") or {}
        if e.get("type") != "assistant" or not isinstance(msg, dict) or "usage" not in msg:
            continue
        key = (msg.get("id"), e.get("requestId"))
        u = msg["usage"] or {}
        cur = per_msg.setdefault(key, [0, 0, 0, 0])
        for i, f in enumerate(FIELDS):
            cur[i] = max(cur[i], int(u.get(f) or 0))
        model_of[key] = msg.get("model", "unknown")
        first = first or ts
        last = ts
    per_model: dict = defaultdict(lambda: [0, 0, 0, 0])
    msgs: dict = defaultdict(int)
    for key, vals in per_msg.items():
        for i, v in enumerate(vals):
            per_model[model_of[key]][i] += v
        msgs[model_of[key]] += 1
    return per_model, msgs, first, last, stamps


def worker_identity(path: Path) -> tuple[str, str, str]:
    """(role name, agent file, requested model) from the meta file, else the first prompt's 'You are <Name>'."""
    meta = path.with_suffix(".meta.json")
    name = agent = model = ""
    if meta.exists():
        try:
            d = json.loads(meta.read_text(encoding="utf-8"))
            name, agent, model = d.get("description", ""), d.get("agentType", ""), d.get("model", "")
        except (json.JSONDecodeError, OSError):
            pass
    if not name:
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("type") == "user":
                    m = re.search(r"You are ([A-Z][A-Za-z0-9]+-[A-Za-z]+)", json.dumps(e.get("message"))[:3000])
                    name = m.group(1) if m else ""
                    break
    return name or "UNNAMED", agent or "?", model or "?"


def add(a: list[int], b: list[int]) -> list[int]:
    return [x + y for x, y in zip(a, b)]


def row(cells: list) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def fmt(v: list[int]) -> list[str]:
    return [f"{x:,}" for x in v] + [f"{sum(v):,}"]


def gaps(stamps: list[str]) -> list[tuple[str, str, float]]:
    s = sorted(set(stamps))
    out = []
    for a, b in zip(s, s[1:]):
        d = (parse_ts(b) - parse_ts(a)).total_seconds() / 60
        if d >= PAUSE_MIN:
            out.append((a, b, d))
    return out


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    hi = sys.argv[1]
    lo = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_FROM
    raw: list[str] = [f"# make_cost.py window {lo} <= ts < {hi} (UTC); run {datetime.now(timezone.utc).isoformat()}"]
    total_by_model: dict = defaultdict(lambda: [0, 0, 0, 0])
    msgs_by_model: dict = defaultdict(int)
    lead_tier: dict = defaultdict(lambda: [0, 0, 0, 0])
    work_tier: dict = defaultdict(lambda: [0, 0, 0, 0])
    spawns: list = []
    sess_rows: list = []
    sess_pauses: list = []
    problems: list[str] = []
    for n, sid in SESSIONS:
        files = [("lead", PROJ / f"{sid}.jsonl")] + [
            (p.stem, p) for p in sorted((PROJ / sid / "subagents").rglob("agent-*.jsonl"))]
        lead = [0, 0, 0, 0]
        workers = [0, 0, 0, 0]
        all_stamps: list[str] = []
        lead_stamps: list[str] = []
        for name, path in files:
            if not path.exists():
                problems.append(f"session {n}: {path} missing")
                continue
            try:
                pm, msgs, first, last, stamps = scan(path, lo, hi)
            except (OSError, UnicodeDecodeError) as exc:
                problems.append(f"session {n}: {path.name} unreadable: {exc}")
                continue
            all_stamps += stamps
            ident = ("lead", "-", "-") if name == "lead" else worker_identity(path)
            if name == "lead":
                lead_stamps = stamps
            tot = [0, 0, 0, 0]
            for model, v in pm.items():
                raw.append(f"s{n} {name} {model} msgs={msgs[model]} first={first} last={last} in={v[0]} out={v[1]} "
                           f"cread={v[2]} ccreate={v[3]} total={sum(v)}")
                tot = add(tot, v)
                total_by_model[model] = add(total_by_model[model], v)
                msgs_by_model[model] += msgs[model]
                bucket = lead_tier if name == "lead" else work_tier
                bucket[tier(model)] = add(bucket[tier(model)], v)
            if name == "lead":
                lead = tot
            else:
                workers = add(workers, tot)
                spawns.append((n, ident, sorted(pm), first, last, tot, sum(msgs.values())))
        stamps_sorted = sorted(all_stamps)
        sess_rows.append((n, sid, lead, workers, stamps_sorted[0] if stamps_sorted else None,
                          stamps_sorted[-1] if stamps_sorted else None,
                          sum(1 for s in spawns if s[0] == n)))
        for a, b, d in gaps(all_stamps):
            sess_pauses.append((n, a, b, d))

    # ---- markdown tables
    md: list[str] = [f"# Stage E.32b session cost (tokens from transcript message.usage; times PDT)\n",
                     f"Window: {lo} <= ts < {hi} UTC ({pdt(lo)} to {pdt(hi)} PDT). Scan keeps each message's final "
                     f"usage (per-field max over its records). Token counts only, never estimated.\n"]
    if problems:
        md.append("UNREADABLE OR MISSING: " + "; ".join(problems) + "\n")
    md += ["## 1. Tokens per model, whole stage (lead + workers, four sessions)\n",
           row(["Model", "Messages", "Input", "Output", "Cache read", "Cache creation", "Total"]),
           "|---|---|---|---|---|---|---|"]
    allv = [0, 0, 0, 0]
    for model, v in sorted(total_by_model.items()):
        md.append(row([model, f"{msgs_by_model[model]:,}"] + fmt(v)))
        allv = add(allv, v)
    md.append(row(["all", f"{sum(msgs_by_model.values()):,}"] + fmt(allv)))

    md += ["\n## 2. One line per worker spawn\n",
           row(["Session", "Role (Agent description)", "Agent file", "Requested model", "Model(s) in transcript",
                "First (PDT)", "Last (PDT)", "Msgs", "Input", "Output", "Cache read", "Cache creation", "Total"]),
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, (name, agent, req), models, first, last, tot, nm in sorted(spawns, key=lambda s: (s[0], s[3] or "")):
        md.append(row([n, name, agent, req, ", ".join(models) or "-", pdt(first), pdt(last), nm] + fmt(tot)))
    md.append(f"\nWorker spawns listed: {len(spawns)}. Distinct models seen in worker transcripts: "
              f"{', '.join(sorted({m for s in spawns for m in s[2]})) or '-'}.")

    md += ["\n## 3. Per session\n",
           row(["Session", "Id", "First record (PDT)", "Last record (PDT)", "Wall-clock", "Lead tokens", "Worker spawns",
                "Worker tokens", "Session total"]),
           "|---|---|---|---|---|---|---|---|---|"]
    for n, sid, lead, workers, first, last, ns in sess_rows:
        wc = "-"
        if first and last:
            sec = int((parse_ts(last) - parse_ts(first)).total_seconds())
            wc = f"{sec // 3600}h{sec % 3600 // 60:02d}m"
        md.append(row([n, sid[:8], pdt(first), pdt(last), wc, f"{sum(lead):,}", ns, f"{sum(workers):,}",
                       f"{sum(lead) + sum(workers):,}"]))
    md += ["\nIdle gaps >= %d min inside a session (union of lead and subagent timestamps), candidate pauses:" % PAUSE_MIN]
    md += [f"- session {n}: {pdt(a)} to {pdt(b)} PDT, {d:.0f} min" for n, a, b, d in sess_pauses] or ["- none"]
    md += ["\nGaps between sessions (last record of one to first record of the next, PDT):"]
    for (n1, _, _, _, _, l1, _), (n2, _, _, _, f2, _, _) in zip(sess_rows, sess_rows[1:]):
        gap = f"{(parse_ts(f2) - parse_ts(l1)).total_seconds() / 60:.0f} min" if l1 and f2 else "-"
        md.append(f"- session {n1} to {n2}: {pdt(l1)} to {pdt(f2)}, {gap}")

    lead_all = sum(sum(v) for v in lead_tier.values())
    work_all = sum(sum(v) for v in work_tier.values())
    grand = lead_all + work_all
    md += ["\n## 4. Delegation share\n",
           row(["Group", "Tokens", "Share of all tokens"]), "|---|---|---|",
           row(["lead (four sessions)", f"{lead_all:,}", f"{lead_all / grand:.1%}" if grand else "-"]),
           row(["workers (all spawns)", f"{work_all:,}", f"{work_all / grand:.1%}" if grand else "-"]),
           "", row(["Model tier", "Lead tokens", "Worker tokens", "Total", "Share of all tokens"]),
           "|---|---|---|---|---|"]
    for t in sorted(set(lead_tier) | set(work_tier)):
        a, b = sum(lead_tier[t]), sum(work_tier[t])
        md.append(row([t, f"{a:,}", f"{b:,}", f"{a + b:,}", f"{(a + b) / grand:.1%}" if grand else "-"]))
    md.append("\nNote: cache-read tokens dominate the totals; the shares are by raw token count, not by cost.")

    (OUT / "cost_raw.txt").write_text("\n".join(raw) + "\n", encoding="utf-8")
    (OUT / "ret_cost_tokens.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"models={len(total_by_model)} spawns={len(spawns)} sessions={len(sess_rows)} problems={len(problems)} "
          f"grand_total={grand:,}")
    for model, v in sorted(total_by_model.items()):
        print(f"{model}: {sum(v):,}")


if __name__ == "__main__":
    main()
