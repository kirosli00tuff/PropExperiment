"""One-off generator of strategy/members/k4/_releases.py after Stage E.5 Task C3 (MemberCoder).

Not imported by any member. Run from the repository root:

    uv run python reports/stage_e5_briefs/gen_k4_releases_e5.py

It renders the Stage E.4 module with reports/stage_e4_briefs/gen_k4_releases.py (unchanged: the
same two sources, the same section-11 drops, the same layout) and applies exactly one amendment:

- Source: reports/stage_e5_ngs_check.json (sha256 E5_CHECK_SHA256), the confirmation-window check
  of every calendar NGS row in S_NG = 2019-05-06..2024-02-29 (its "window"), one row per calendar
  row. Its verdicts must be "keep" or "drop_actual_differs" and nothing else.
- Drops (lead ruling R-C3-1, C9's first drop rule): its rows with verdict "drop_actual_differs"
  inside its window. The dates must equal R_C3_1_NGS or the generator stops. Written as
  DROPPED_NGS_CONFIRMATION, reason = the verdict, ": ", then the check's "reason" verbatim. The
  Friday releases the check found are not added as rows (the frozen rule allows only a drop).
- NGS: those rows removed in place. A line of the E.4 rendering that loses rows keeps its other
  rows in order; a line that loses every row is removed; every other line is byte-identical, so
  every research-window row (2025-04-01..2026-06-19) keeps its exact line.
- Docstring (sources and counts), E5_NGS_CHECK_SHA256, CONFIRMATION_CHECK_WINDOW and __all__.

tests/test_e4_k4_members_b.py loads this file and asserts the module equals amend(...). It prints
counts only.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
E4_GENERATOR = REPO_ROOT / "reports" / "stage_e4_briefs" / "gen_k4_releases.py"
E5_CHECK = REPO_ROOT / "reports" / "stage_e5_ngs_check.json"
E5_CHECK_SHA256 = "ddfecb3e1575dc817aaeebc0f8795ebcbbbd10e78b4a936ec8b454d277706b44"
S_NG = ("2019-05-06", "2024-02-29")
DROP_VERDICT = "drop_actual_differs"  # C9's first drop rule
E5_VERDICTS = frozenset({"keep", DROP_VERDICT})
# Lead ruling R-C3-1 (reports/stage_e5_briefs/C3_member_coder.md): the rows to remove.
R_C3_1_NGS = ("2019-12-26", "2020-01-02", "2020-11-12", "2021-01-21", "2023-11-09")
ALL_WIDTH = 99


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_e4_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gen_k4_releases", E4_GENERATOR)
    assert spec is not None and spec.loader is not None
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


def e4_text(gen: ModuleType, calendar: dict, check: dict) -> str:
    """The Stage E.4 module, exactly as the E.4 generator renders it."""
    gen.check_window_rows(calendar, check)
    dropped_wpsr = gen.drops(check, "WPSR", gen.SECTION11_WPSR)
    dropped_ngs = gen.drops(check, "NGS", gen.SECTION11_NGS)
    return gen.render(gen.wpsr_rows(calendar, {d for d, _ in dropped_wpsr}),
                      gen.ngs_rows(calendar, {d for d, _ in dropped_ngs}), dropped_wpsr,
                      dropped_ngs, gen.api_dropped(check), gen.federal_mondays(check),
                      gen.nyse_not_full(check), gen.unverified_ngs(check), check["window"])


def check_e5_rows(calendar: dict, e5_check: dict, research_window: list[str]) -> None:
    """The E.5 check's rows are the calendar's NGS rows in S_NG, one for one (date and ET time)."""
    first, last = e5_check["window"]
    assert (first, last) == S_NG, (first, last)
    assert last < research_window[0], "the confirmation window overlaps the research window"
    cal = sorted((r["date"], r["time_local"]) for r in calendar["releases"]
                 if r["release"] == "NGS" and first <= r["date"] <= last)
    chk = sorted((r["date"], r["time_et"]) for r in e5_check["ngs"])
    assert cal == chk, "E.5 check rows differ from the calendar's NGS rows in S_NG"
    verdicts = {r["verdict"] for r in e5_check["ngs"]}
    assert verdicts == E5_VERDICTS, sorted(verdicts)


def e5_drops(e5_check: dict) -> list[tuple[str, str]]:
    first, last = e5_check["window"]
    found = sorted((r["date"], f"{r['verdict']}: {r['reason']}") for r in e5_check["ngs"]
                   if r["verdict"] == DROP_VERDICT and first <= r["date"] <= last)
    assert tuple(d for d, _ in found) == R_C3_1_NGS, [d for d, _ in found]
    for _, reason in found:
        assert '"' not in reason and "\\" not in reason, reason  # literal-safe, no escaping
    return found


def _replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old[:80]
    return text.replace(old, new)


def _wrap_names(names: list[str]) -> str:
    lines, line = [], "   "
    for name in names:
        item = f' "{name}",'
        if len(line) + len(item) > ALL_WIDTH:
            lines.append(line)
            line = "   "
        line += item
    lines.append(line)
    return "\n".join(lines)


def docstring(n_wpsr: int, n_std: int, n_ngs: int, n_holidays: int, n_nyse: int,
              window: list[str]) -> str:
    return f'''"""K4 event and calendar tables (Stage E.4; specs S0.11, K4-L-01/02/04, section 11).

GENERATED by reports/stage_e5_briefs/gen_k4_releases_e5.py, which renders the Stage E.4 module
with reports/stage_e4_briefs/gen_k4_releases.py from the frozen release calendar
reports/stage_e2b_release_calendar.json (sha256 RELEASE_CALENDAR_SHA256) and Task 1b's release check
reports/stage_e4_release_check.json (sha256 RELEASE_CHECK_SHA256), then applies the E.5 drops from
reports/stage_e5_ngs_check.json (sha256 E5_NGS_CHECK_SHA256). Do not edit by hand:
tests/test_e4_k4_members_b.py recomputes every table from those three files and asserts equality.

- WPSR: (date, T_W "HH:MM" CT, weekday 0-6 with Monday 0, standard) for every calendar WPSR row
  2019-05-01..2026-06-17 less DROPPED_WPSR. T_W = the row's instant_utc in America/Chicago
  (K4-L-02); standard = a Wednesday at 10:30 America/New_York.
- NGS: (date, T_N "HH:MM" CT) for every calendar NGS row less DROPPED_NGS and
  DROPPED_NGS_CONFIRMATION.
- Research-window drops ({window[0]}..{window[1]}, section 11; C9's drop rules are applied
  there, K4-L-01): DROPPED_WPSR 2025-12-29, 2026-05-28 (K4-L-15 for the latter; 2025-07-16 is
  kept by ruling R-T3-1); DROPPED_NGS 2025-12-29. API_DROPPED_WEEKS (K4-L-04) is empty.
- Confirmation-window drops (CONFIRMATION_CHECK_WINDOW {S_NG[0]}..{S_NG[1]}; Stage E.5 ruling
  R-C3-1, C9's first drop rule): DROPPED_NGS_CONFIRMATION {", ".join(R_C3_1_NGS[:3])},
  {", ".join(R_C3_1_NGS[3:])}, the E.5 check's "{DROP_VERDICT}" rows. The four Friday releases
  it found are not added as rows (the frozen rule allows only a drop).
- NGS_UNVERIFIED_IN_WINDOW: storage releases kept with the calendar's value, labelled
  "unverifiable" (the return's "calendar partly unverified" label for K4-ngpre-01).
- FEDERAL_MONDAY_HOLIDAYS: US federal holidays on a Monday, 2019-05-01..2026-06-19 (OPM, Task 1b).
- NYSE_NOT_FULL: NYSE full closures and early closes, 2019-05-01..2026-06-19 (Task 1b).
Counts: {n_wpsr} WPSR rows ({n_std} standard), {n_ngs} NGS rows,
{n_holidays} federal Monday holidays, {n_nyse} NYSE dates.
"""
'''


def amend(gen: ModuleType, calendar: dict, check: dict, e5_check: dict) -> str:
    """The Stage E.4 rendering with exactly the Stage E.5 amendment applied."""
    text = e4_text(gen, calendar, check)
    check_e5_rows(calendar, e5_check, check["window"])
    confirmation = e5_drops(e5_check)
    removed = {d for d, _ in confirmation}
    dropped_ngs = gen.drops(check, "NGS", gen.SECTION11_NGS)
    assert not removed & {d for d, _ in dropped_ngs}
    e4_ngs = gen.ngs_rows(calendar, {d for d, _ in dropped_ngs})
    assert removed <= {d for d, _ in e4_ngs}
    per_line = gen.PER_LINE["NGS"]
    old_lines, new_lines = [], []
    for i in range(0, len(e4_ngs), per_line):
        chunk = e4_ngs[i:i + per_line]
        old_lines.append("    " + " ".join(f'("{d}", "{t}"),' for d, t in chunk))
        kept = [(d, t) for d, t in chunk if d not in removed]
        if kept:
            new_lines.append("    " + " ".join(f'("{d}", "{t}"),' for d, t in kept))
    head = "NGS: tuple[tuple[str, str], ...] = (\n"
    text = _replace_once(text, head + "\n".join(old_lines) + "\n)\n",
                         head + "\n".join(new_lines) + "\n)\n")
    # docstring
    end = text.index('\n"""\n') + len('\n"""\n')
    wpsr_dropped = {d for d, _ in gen.drops(check, "WPSR", gen.SECTION11_WPSR)}
    wpsr = gen.wpsr_rows(calendar, wpsr_dropped)
    n_ngs = len(e4_ngs) - len(removed)
    text = docstring(len(wpsr), sum(1 for r in wpsr if r[3]), n_ngs,
                     len(gen.federal_mondays(check)), len(gen.nyse_not_full(check)),
                     check["window"]) + text[end:]
    # constants
    window_line = f'RESEARCH_CHECK_WINDOW = ("{check["window"][0]}", "{check["window"][1]}")\n'
    text = _replace_once(text, window_line,
                         window_line + f'E5_NGS_CHECK_SHA256 = "{E5_CHECK_SHA256}"\n'
                         f'CONFIRMATION_CHECK_WINDOW = ("{S_NG[0]}", "{S_NG[1]}")\n')
    # the drop record, after DROPPED_NGS
    ngs_block = gen.render_drops("DROPPED_NGS", dropped_ngs) + "\n"
    text = _replace_once(text, ngs_block, ngs_block + gen.render_drops(
        "DROPPED_NGS_CONFIRMATION", confirmation) + "\n")
    # __all__
    start = text.index("__all__ = [\n")
    names = sorted({*all_names(text[start:]), "CONFIRMATION_CHECK_WINDOW",
                    "DROPPED_NGS_CONFIRMATION", "E5_NGS_CHECK_SHA256"})
    return text[:start] + "__all__ = [\n" + _wrap_names(names) + "\n]\n"


def all_names(block: str) -> list[str]:
    body = block[block.index("[") + 1:block.index("]")]
    return [x.strip().strip('"') for x in body.split(",") if x.strip()]


def main() -> None:
    gen = load_e4_generator()
    assert sha256_file(gen.CALENDAR) == gen.CALENDAR_SHA256, "release calendar changed"
    assert sha256_file(gen.CHECK) == gen.CHECK_SHA256, "release check changed"
    assert sha256_file(E5_CHECK) == E5_CHECK_SHA256, "E.5 NGS check changed"
    calendar = json.loads(gen.CALENDAR.read_text())
    check = json.loads(gen.CHECK.read_text())
    e5_check = json.loads(E5_CHECK.read_text())
    text = amend(gen, calendar, check, e5_check)
    gen.OUT.write_text(text)
    print(f"wrote {gen.OUT.relative_to(REPO_ROOT)}: removed NGS {len(R_C3_1_NGS)}; "
          f"sha256 {sha256_file(gen.OUT)}")


if __name__ == "__main__":
    main()
