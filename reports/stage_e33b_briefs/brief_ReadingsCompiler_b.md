# Brief: ReadingsCompiler-OpusXHigh (Stage E.33b, PipelineReview SF1: the readings file's coder entries)

You are a worker (Opus 5.5, xhigh) for the E.33b lead, in a fresh context. Do not spawn workers; do not ask questions.
Do not edit any code and do not edit reports/stage_e33_protocol_readings.md (the lead writes it).

## Why
Protocol P0.2 (reports/stage_e32_discovery_protocol.md section 0.2, read it): every reading of the protocol the code
embodies is written into reports/stage_e33_protocol_readings.md before the freeze, the file is hashed into the freeze
list and C1, and after C1 a question the file does not answer stops that part of the stage. PipelineReview SF1
(reports/stage_e33_briefs/review/PipelineReview.md lines 53-75) lists the readings still missing; its section
"Readings" (lines 178-256) gives the reviewer's view on each.

## Objective
Compile a complete draft of the coder entries, for the lead to decide, at reports/stage_e33b_briefs/readings_compiled.md:
- Sources: every readings file: reports/stage_e33_briefs/work/{DataCoder,FeatureCoder,LabelCoder,SearchCoder,ProofCoder,
  StatsCostCoder,TestCoder}_readings.md and work/implB/{FeatureCoder2,LabelCoder2}_readings.md (find any other
  *_readings.md under work/), the reviews' readings views (review/PipelineReview.md, SearchReview.md, ProofReview.md,
  MathReview.md), and work/B3_agreement.md for the FD rulings already in the readings file.
- One entry per reading; where Coder-A and Coder-B chose the same, one entry naming both IDs. Each entry: the IDs, the
  protocol line quoted verbatim (with its P-section), the readings considered, the choice made in the code, whether the
  two implementations agree (from B3: 0 cells, or the FD number), every reviewer's view with its file:line, the stated
  effect on data if any, and a PROPOSED decision (agree / disagree / needs the lead) with one line of why. Mark any
  reading where a reviewer disagreed, where A and B differ, or where the choice is not the literal or the more
  conservative one, as NEEDS LEAD.
- Skip nothing: superseded readings are listed as superseded with the ruling that replaced them.
- End with a coverage table: per source file, the IDs found, the IDs compiled, and any ID the SF1 list names that you
  could not find.
Read the files by section (grep for the ID patterns first); keep quotes short and exact.

## Return
The path, the entry count, the NEEDS LEAD list (IDs and one line each), and a summary of at most 200 words.
