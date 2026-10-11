"""Stage E.19 lead: assemble reports/stage_e19_results.md = the lead's narrative + key numbers (generated from
reports/stage_e19_results.json by key_numbers.py) + the machine tables T1-T8 (prop_econ/report.py) verbatim.
Usage: python3 reports/stage_e19_briefs/make_results_md.py"""
import subprocess
import sys
from pathlib import Path

B = Path("reports/stage_e19_briefs")
key = subprocess.run([sys.executable, str(B / "key_numbers.py")], capture_output=True, text=True, check=True).stdout
(B / "key_numbers.md").write_text(key)
tables = (B / "results_tables.md").read_text().split("\n", 1)[1]  # drop the machine file's title line
out = ((B / "results_narrative.md").read_text().rstrip() + "\n\n## 7. Key numbers (generated from the results JSON)\n\n"
       "Headline configuration (bootstrap tails, random direction, D8 costs, continuous contracts, payout policy max,\n"
       "Standard pricing, API fee included), at each rule set's best band f; 'B2F on' = Back2Funded reactivations used.\n\n"
       + key.rstrip() + "\n\n## Appendix: machine tables T1-T8 (verbatim from reports/stage_e19_briefs/results_tables.md)\n"
       + tables)
Path("reports/stage_e19_results.md").write_text(out)
print("reports/stage_e19_results.md", len(out.split()), "words")
