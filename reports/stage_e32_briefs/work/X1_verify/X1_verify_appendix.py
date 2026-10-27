"""Map each line of X1_tableC_appendix.md to its stats31.md source line (via the SOURCE markers) and compare.
Sample: every 5th appendix table data row (rows 1, 6, 11, ... in appendix order), i.e. a 20% systematic sample;
also reports a full-line count for completeness. Prints only line numbers and match flags."""
import re
A = open("reports/stage_e32_briefs/work/X1_exposure/X1_tableC_appendix.md").read().split("\n")
S = open("reports/stage_e31_briefs/work/pilot/runs/stats31.md").read().split("\n")
mapping = []  # (appendix_line_no, source_line_no)
cur = None
for i, l in enumerate(A, 1):
    m = re.match(r"<!-- SOURCE .* lines (\d+)-(\d+) :", l)
    if m:
        cur = [int(m.group(1)), int(m.group(2))]; continue
    if cur and cur[0] <= cur[1]:
        mapping.append((i, cur[0])); cur[0] += 1
datarows = [(a, s) for a, s in mapping if A[a-1].startswith("|") and not A[a-1].startswith("|---") and not re.match(r"^\| (family|statistic|h|symbol) \|", A[a-1])]
sample = datarows[0::5]
bad = [(a, s) for a, s in sample if A[a-1] != S[s-1]]
print("appendix lines mapped", len(mapping), "table data rows", len(datarows), "sample size", len(sample), "sample mismatches", len(bad))
print("sample (appendix line -> stats31 line):", " ".join(f"{a}->{s}" for a, s in sample))
full_bad = [(a, s) for a, s in mapping if A[a-1] != S[s-1]]
print("full-line mismatches over all mapped lines:", len(full_bad), full_bad[:5])
