"""Assemble reports/stage_e32_methods_brief.md from the lead's front, the reader files (as corrected)
and the lead's verification part. Headings of each reader file are demoted by two levels so they
nest under the brief's Part headings. No content is changed.

    uv run python reports/stage_e32_briefs/work/lead/assemble_brief.py
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BRIEFS = ROOT / "reports" / "stage_e32_briefs"
LEAD = BRIEFS / "work" / "lead"
OUT = ROOT / "reports" / "stage_e32_methods_brief.md"

PART_R = [("R1", "R1_alpha_process.md", "Alpha research process at proprietary firms and systematic funds"),
          ("R2", "R2_ag_desks.md", "Commodity and agricultural trading desks"),
          ("R3a", "R3a_crush.md", "Soybean complex economics: crush, cointegration, spreads, oil-share regime"),
          ("R3b", "R3b_microstructure.md", "Soybean complex microstructure: K algorithm, implieds, rolls, liquidity"),
          ("R4", "R4_events.md", "Event structure: USDA releases, limits, gaps, settlement"),
          ("R5", "R5_ml_evidence.md", "Out-of-sample ML evidence at 1-240 minutes, competitions, decay")]
PART_M = [("M1", "M1_order_flow.md", "Order-flow measures"),
          ("M2", "M2_lead_lag.md", "Lead-lag and cross-asset structure"),
          ("M3", "M3_labels.md", "Labels and sampling"),
          ("M4", "M4_models.md", "Model families"),
          ("M5a", "M5a_validation.md", "Validation and overfitting control (CV, DSR, PBO, FWER/FDR)"),
          ("M5b", "M5b_power.md", "Feature importance, stability and power"),
          ("M6", "M6_prop_strategy.md", "From prediction to a prop-firm strategy")]


def demote(text: str, levels: int = 2) -> str:
    return re.sub(r"^(#{1,6}) ", lambda m: "#" * min(6, len(m.group(1)) + levels) + " ", text, flags=re.M)


def section(code: str, name: str, title: str) -> str:
    body = (BRIEFS / name).read_text()
    digest = hashlib.sha256(body.encode()).hexdigest()
    return (f"## {code}. {title}\n\nSource file: reports/stage_e32_briefs/{name} (sha256 {digest}).\n\n"
            + demote(body).rstrip() + "\n\n")


def main() -> None:
    parts = [(LEAD / "brief_front.md").read_text().rstrip() + "\n\n",
             "## Contents\n\n- Front and verdict table (above)\n- Part R: R1-R5\n- Part M: M1-M6\n"
             "- Part V: verification, the lead's rulings and the fixes\n\n",
             "# Part R. How professionals build short-horizon directional strategies\n\n"]
    parts += [section(*row) for row in PART_R]
    parts.append("# Part M. The mathematics and ML for directional signals\n\n")
    parts += [section(*row) for row in PART_M]
    parts.append((LEAD / "brief_part_v.md").read_text().rstrip() + "\n")
    OUT.write_text("".join(parts))
    print(OUT, OUT.stat().st_size, "bytes", hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
