"""Stage E.25: assemble reports/E.25_RETURN.md from the parts in reports/stage_e25_briefs/.

Parts: ret_summary.md (1), start_checks.txt + end_checks.txt + ret_events.md (2), synthesis.md + ret_sources.md (3),
the delegation table from cost_raw.txt with each spawn's status (4), ret_verification.md (5), ret_open_choices.md (6),
ret_decisions.md (7), ret_cost.md (8). Usage: python3 -I reports/stage_e25_briefs/assemble_return.py
"""
import re
from datetime import datetime, timedelta
from pathlib import Path

B = Path(__file__).resolve().parent
OUT = B.parent / "E.25_RETURN.md"


def read(name):
    return (B / name).read_text().rstrip() + "\n"


def demote(text, levels=1):
    return re.sub(r"^(#+) ", lambda m: "#" * (len(m.group(1)) + levels) + " ", text, flags=re.M)


def pdt(ts):
    t = datetime.fromisoformat(ts.replace("Z", "+00:00")) - timedelta(hours=7)
    return t.strftime("%H:%M")


# Spawns cut by a usage limit (by role name and the window their transcript ends in, PDT).
CUT_W1 = {"SourceReader-0DTEAcademic-OpusHigh", "SourceReader-0DTEVendor-OpusHigh", "SourceReader-OrderFlow-OpusHigh",
          "SourceReader-VolumeTradeSide-OpusHigh", "SourceReader-News-OpusHigh", "SourceReader-SchedEvents-OpusHigh",
          "SourceReader-LiveRecords-OpusHigh", "SourceReader-PropOutcomes-OpusHigh", "RedigReader-EquityIndex-OpusHigh",
          "RedigReader-Rates-OpusHigh", "RedigReader-EnergyMetals-OpusHigh", "RedigReader-InfoSources-OpusHigh",
          "NearMissExtractor-SonnetMed", "SourceReader-MakerNative-OpusHigh", "SourceReader-QueueFill-OpusHigh",
          "SourceReader-Podcasts-OpusHigh", "SourceReader-NicheMarkets-OpusHigh", "SourceReader-NicheAccess-OpusHigh"}
CUT_W2 = {"DeepReader-NoiseAreaMomentum-OpusHigh", "DeepReader-ThirdFriday-OpusHigh", "DeepReader-TreasuryDrifts-OpusHigh",
          "SourceReader-PropOutcomes-OpusHigh", "RedigReader-EnergyMetals-OpusHigh", "RedigReader-InfoSources-OpusHigh",
          "RedigReader-E20Planning-OpusHigh", "ExecTriage-OpusXHigh"}
RESUMED = {"NearMissExtractor-SonnetMed", "SourceReader-MakerNative-OpusHigh", "SourceReader-QueueFill-OpusHigh",
           "SourceReader-Podcasts-OpusHigh", "SourceReader-NicheMarkets-OpusHigh", "SourceReader-NicheAccess-OpusHigh"}


def status(name, first, last):
    f, l = pdt(first), pdt(last)
    if name in RESUMED and f < "02:05" and l >= "06:00":
        return "cut by the usage limit about 01:58; resumed by message 06:12; done"
    if name in CUT_W1 and l < "02:05":
        return "cut by the usage limit about 01:58 (partial files on disk)"
    if name == "RedigReader-E20Planning-OpusHigh" and "06:20" <= f <= "06:40":
        return "cut by the usage limit about 06:35 after its md and json were complete"
    if name in CUT_W2 and "06:20" <= f <= "06:40" and l <= "06:40":
        return "cut by the usage limit about 06:35 (partial files on disk)"
    return "done"


def delegation():
    rows = []
    for line in read("cost_raw.txt").splitlines():
        m = re.match(r"(\S+) (.+?) (claude-\S+) effort=(\S+) msgs=\d+ first=(\S+) last=(\S+) .* total=(\d+)$", line)
        if not m:
            continue
        stem, name, model, eff, first, last, tot = m.groups()
        if stem == "lead":
            continue
        rows.append((first, name, model.replace("claude-", ""), eff, first, last, int(tot)))
    rows.sort()
    out = ["## 4. Delegation record", "",
           "One row per spawn (transcripts; times PDT; tokens are each message's final usage, all four fields). Agent ",
           "file: worker-medium, worker-high or worker-xhigh by effort (wave-1 and wave-2 readers ran as workflow agents ",
           "at the same model and effort). The lead's own row is in section 8.", "",
           "| # | Agent (role name) | Model | Effort | Start | End | Tokens | Status |", "|---|---|---|---|---|---|---|---|"]
    for i, (_, name, model, eff, first, last, tot) in enumerate(rows, 1):
        out.append(f"| {i} | {name} | {model} | {eff} | {pdt(first)} | {pdt(last)} | {tot:,} | {status(name, first, last)} |")
    return "\n".join(out) + "\n"


def main():
    parts = [
        "# Stage E.25 return: untapped sources, a deep research pass for a prop-compatible intraday edge\n",
        "Prompt: docs/prompts/STAGE_E.25.md (research only; V42). Lead: Opus 5.5, xhigh, ultracode. Session "
        "37fc9660-82d1-49fd-be83-50b822ab0a5b. Times PDT. Every working file is under reports/stage_e25_briefs/; "
        "STATE in reports/stage_e25_STATE.md.\n",
        read("ret_summary.md"),
        "## 2. Guardrail evidence\n\nScript: reports/stage_e25_briefs/checks.sh (no pytest: E.24 owns the suite). Every line "
        "is quoted verbatim; `git status --short` prints its tracked lines and the count of untracked (`??`) lines, "
        "which are raw pages of earlier stages and this stage (Open choice 6).\n",
        "### 2.1 Start checks\n\n```\n" + read("start_checks.txt") + "```\n",
        "### 2.2 End checks\n\n```\n" + read("end_checks.txt") + "```\n",
        read("ret_events.md"),
        "## 3. Results\n\nThe synthesis (S1-S3, the execution triage of addenda 4-5, the re-dig section of addendum 1, the prop "
        "landscape), as reviewed and fixed (section 5), follows; per-reader source lists close the section.\n",
        demote(read("synthesis.md").split("\n", 1)[1]),
        "### Per-reader source lists\n\nFrom each reader's JSON evidence rows (fetch counts from its fetch log). R4 and R7 "
        "were cut before writing a JSON: their sources are in R4_volume_tradeside.md and R7_live_records.md section 3. "
        "R0 lists: r0_prior_sources.md (253 sources earlier passes read), r0_e20_evidence_index.md (157 rows).\n",
        demote(read("ret_sources.md").split("\n", 1)[1], 2),
        delegation(),
        read("ret_verification.md"),
        "## 6. Open choices\n\nEvery decision the lead made on its own, with the reason (user-directed changes are marked).\n",
        read("ret_open_choices.md").split("\n", 1)[1],
        read("ret_decisions.md"),
        read("ret_cost.md"),
    ]
    OUT.write_text("\n".join(p.rstrip() + "\n" for p in parts))
    print(OUT, len(OUT.read_text().splitlines()), "lines")


if __name__ == "__main__":
    main()
