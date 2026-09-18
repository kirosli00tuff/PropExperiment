# Power gate (Stage B, Task 4)

Generated 2026-09-18T00:21:27.712505+00:00 · `uv run python -m funnel.power_gate` · 8,000 runs per grid point · 2 micros · structured data: `reports/power_gate.json`, `reports/power_gate.csv`; lookup: `funnel.power_gate.screen(...)`

This is the screening criterion Stage D.1 runs **before** spending research time on a
candidate strategy. It answers one question: given a candidate's estimated per-trade
quality, would the resulting income distribution actually beat a zero-edge trader at a
stated confidence level, or is it inside the noise the null already produces?

The grid is 120 points — win probability p in {0.40, 0.45, 0.50, 0.55, 0.60}, average
win/loss ratio R in {0.75, 1.0, 1.5, 2.0}, round turns per day T in {1, 2, 4}, across both
payout paths — each simulated 8,000 times, for 960,000 simulated 12-month careers in total.

**Two nulls, and the second one is the honest one.** The *matched* null is a zero-edge
trader at the same size and activity as the candidate. The *robust* null is the most
favorable zero-edge result available at **any** size on the ladder — a coin-flipper who
happens to pick the best size to gamble with (6-7 micros on the Standard path, 5-6 on
Consistency). Beating the matched null says the edge is real. Beating the robust null says
the edge beats the best thing luck alone would have produced. Nine cells pass the first
test and fail the second; treat those as unproven.

**Confidence level.** 80% is the headline, as the task suggested, and 90% and 95% panels
are computed alongside it so the choice is visible rather than baked in. The verdict rule
is deliberately conservative: a cell passes only if `power - 1.96*se >= 0.80`, so the
*lower* bound of the power estimate must clear the bar, not the point estimate. A cell
whose point estimate clears 0.80 but whose lower bound does not is marked `marginal`
rather than promoted — exactly one cell in the grid (standard, T=2, p=0.45, R=2.0) lands
there at 95%.

**What the grid actually says.** The win/loss ratio dominates the win rate. No cell with
R = 0.75 passes anywhere in the grid, under either null, at any confidence level or
activity level — 0 of 30. At 1 round turn/day, only a single cell with R <= 1 passes at
all. Raising p from 0.40 to 0.60 cannot rescue a strategy whose losers are as big as its
winners; raising R from 1.0 to 2.0 repeatedly can. At the 80% matched null, 46 of 120
cells pass; against the robust null, 37. The practical reading for Stage D.1: a candidate
needs R >= 1.5 with p >= 0.55, or R = 2.0 with p >= 0.50, before this harness can tell its
income apart from luck at one round turn per day.

Cost is not the binding constraint at these sizes but it is not free either: the modelled
round turn costs $2.64 per micro at 1 RT/day, $2.61 at 2, and $2.59 at 4. At p = 0.50 and
R = 1.0 the gross edge is exactly zero by construction, and cost alone is what makes that
configuration lose money.

Verdict rule: pass if power - 1.96*se >= 0.80; marginal if power >= 0.80; else fail.

Headline critical values: the MATCHED null (zero edge, same size, same round turns/day), monthly net income quantile:

| Path | RT/day | c = 80% | c = 90% | c = 95% |
|---|---|---|---|---|
| standard | 1 | $43 | $199 | $391 |
| standard | 2 | $20 | $142 | $304 |
| standard | 4 | -$17 | $66 | $195 |
| consistency | 1 | $2 | $129 | $292 |
| consistency | 2 | -$11 | $91 | $235 |
| consistency | 4 | -$38 | $24 | $125 |

Robust critical values: the MOST FAVORABLE null over every size and activity (a zero-edge trader who picks the best size to gamble with):

| Path | c = 80% | c = 90% | c = 95% | at micros / RT per day |
|---|---|---|---|---|
| standard | $420 | $874 | $1,423 | 6 / 1 |
| consistency | $185 | $477 | $829 | 5 / 1 |

Mean round-turn cost per micro (commission + modelled slippage, lower bound): 1 RT/day $2.64, 2 RT/day $2.61, 4 RT/day $2.59

## Headline (matched null), confidence 80%

**Standard path, 1 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (2%) | fail (16%) | fail (50%) |
| 0.45 | fail (2%) | fail (7%) | fail (41%) | fail (80%) |
| 0.50 | fail (5%) | fail (19%) | fail (73%) | PASS (96%) |
| 0.55 | fail (15%) | fail (46%) | PASS (93%) | PASS (100%) |
| 0.60 | fail (38%) | fail (76%) | PASS (99%) | PASS (100%) |

**Standard path, 2 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (1%) | fail (17%) | fail (67%) |
| 0.45 | fail (0%) | fail (4%) | fail (54%) | PASS (94%) |
| 0.50 | fail (2%) | fail (20%) | PASS (89%) | PASS (100%) |
| 0.55 | fail (12%) | fail (58%) | PASS (99%) | PASS (100%) |
| 0.60 | fail (43%) | PASS (90%) | PASS (100%) | PASS (100%) |

**Standard path, 4 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (17%) | PASS (84%) |
| 0.45 | fail (0%) | fail (2%) | fail (69%) | PASS (100%) |
| 0.50 | fail (1%) | fail (20%) | PASS (98%) | PASS (100%) |
| 0.55 | fail (9%) | fail (72%) | PASS (100%) | PASS (100%) |
| 0.60 | fail (50%) | PASS (98%) | PASS (100%) | PASS (100%) |

**Consistency path, 1 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (1%) | fail (16%) | fail (51%) |
| 0.45 | fail (1%) | fail (5%) | fail (43%) | PASS (82%) |
| 0.50 | fail (4%) | fail (20%) | fail (76%) | PASS (97%) |
| 0.55 | fail (15%) | fail (49%) | PASS (95%) | PASS (100%) |
| 0.60 | fail (41%) | PASS (82%) | PASS (99%) | PASS (100%) |

**Consistency path, 2 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (18%) | fail (68%) |
| 0.45 | fail (0%) | fail (3%) | fail (56%) | PASS (95%) |
| 0.50 | fail (2%) | fail (20%) | PASS (91%) | PASS (100%) |
| 0.55 | fail (11%) | fail (60%) | PASS (99%) | PASS (100%) |
| 0.60 | fail (45%) | PASS (93%) | PASS (100%) | PASS (100%) |

**Consistency path, 4 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (17%) | PASS (85%) |
| 0.45 | fail (0%) | fail (2%) | fail (70%) | PASS (100%) |
| 0.50 | fail (1%) | fail (20%) | PASS (98%) | PASS (100%) |
| 0.55 | fail (9%) | fail (73%) | PASS (100%) | PASS (100%) |
| 0.60 | fail (52%) | PASS (99%) | PASS (100%) | PASS (100%) |

## Headline (matched null), confidence 90%

**Standard path, 1 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (1%) | fail (8%) | fail (33%) |
| 0.45 | fail (1%) | fail (2%) | fail (25%) | fail (67%) |
| 0.50 | fail (2%) | fail (10%) | fail (57%) | PASS (90%) |
| 0.55 | fail (7%) | fail (29%) | PASS (85%) | PASS (99%) |
| 0.60 | fail (22%) | fail (60%) | PASS (97%) | PASS (100%) |

**Standard path, 2 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (8%) | fail (52%) |
| 0.45 | fail (0%) | fail (1%) | fail (38%) | PASS (88%) |
| 0.50 | fail (1%) | fail (10%) | fail (79%) | PASS (99%) |
| 0.55 | fail (5%) | fail (40%) | PASS (98%) | PASS (100%) |
| 0.60 | fail (27%) | PASS (81%) | PASS (100%) | PASS (100%) |

**Standard path, 4 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (9%) | fail (73%) |
| 0.45 | fail (0%) | fail (1%) | fail (54%) | PASS (99%) |
| 0.50 | fail (0%) | fail (10%) | PASS (96%) | PASS (100%) |
| 0.55 | fail (4%) | fail (57%) | PASS (100%) | PASS (100%) |
| 0.60 | fail (34%) | PASS (96%) | PASS (100%) | PASS (100%) |

**Consistency path, 1 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (7%) | fail (35%) |
| 0.45 | fail (0%) | fail (1%) | fail (28%) | fail (71%) |
| 0.50 | fail (1%) | fail (10%) | fail (63%) | PASS (93%) |
| 0.55 | fail (6%) | fail (33%) | PASS (89%) | PASS (99%) |
| 0.60 | fail (25%) | fail (68%) | PASS (99%) | PASS (100%) |

**Consistency path, 2 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (8%) | fail (55%) |
| 0.45 | fail (0%) | fail (1%) | fail (41%) | PASS (91%) |
| 0.50 | fail (0%) | fail (10%) | PASS (84%) | PASS (100%) |
| 0.55 | fail (5%) | fail (45%) | PASS (99%) | PASS (100%) |
| 0.60 | fail (30%) | PASS (87%) | PASS (100%) | PASS (100%) |

**Consistency path, 4 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (8%) | fail (77%) |
| 0.45 | fail (0%) | fail (1%) | fail (58%) | PASS (99%) |
| 0.50 | fail (0%) | fail (10%) | PASS (97%) | PASS (100%) |
| 0.55 | fail (4%) | fail (61%) | PASS (100%) | PASS (100%) |
| 0.60 | fail (37%) | PASS (98%) | PASS (100%) | PASS (100%) |

## Headline (matched null), confidence 95%

**Standard path, 1 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (4%) | fail (23%) |
| 0.45 | fail (0%) | fail (1%) | fail (16%) | fail (55%) |
| 0.50 | fail (1%) | fail (5%) | fail (43%) | PASS (84%) |
| 0.55 | fail (3%) | fail (18%) | fail (75%) | PASS (97%) |
| 0.60 | fail (13%) | fail (46%) | PASS (95%) | PASS (100%) |

**Standard path, 2 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (4%) | fail (38%) |
| 0.45 | fail (0%) | fail (1%) | fail (26%) | marg (81%) |
| 0.50 | fail (0%) | fail (5%) | fail (68%) | PASS (98%) |
| 0.55 | fail (2%) | fail (27%) | PASS (95%) | PASS (100%) |
| 0.60 | fail (16%) | fail (71%) | PASS (100%) | PASS (100%) |

**Standard path, 4 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (5%) | fail (61%) |
| 0.45 | fail (0%) | fail (0%) | fail (39%) | PASS (98%) |
| 0.50 | fail (0%) | fail (5%) | PASS (91%) | PASS (100%) |
| 0.55 | fail (2%) | fail (42%) | PASS (100%) | PASS (100%) |
| 0.60 | fail (21%) | PASS (92%) | PASS (100%) | PASS (100%) |

**Consistency path, 1 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (3%) | fail (25%) |
| 0.45 | fail (0%) | fail (0%) | fail (18%) | fail (61%) |
| 0.50 | fail (0%) | fail (5%) | fail (51%) | PASS (89%) |
| 0.55 | fail (3%) | fail (22%) | PASS (84%) | PASS (99%) |
| 0.60 | fail (15%) | fail (56%) | PASS (97%) | PASS (100%) |

**Consistency path, 2 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (4%) | fail (43%) |
| 0.45 | fail (0%) | fail (0%) | fail (29%) | PASS (86%) |
| 0.50 | fail (0%) | fail (5%) | fail (76%) | PASS (99%) |
| 0.55 | fail (2%) | fail (33%) | PASS (97%) | PASS (100%) |
| 0.60 | fail (19%) | fail (79%) | PASS (100%) | PASS (100%) |

**Consistency path, 4 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (4%) | fail (68%) |
| 0.45 | fail (0%) | fail (0%) | fail (46%) | PASS (99%) |
| 0.50 | fail (0%) | fail (5%) | PASS (95%) | PASS (100%) |
| 0.55 | fail (1%) | fail (49%) | PASS (100%) | PASS (100%) |
| 0.60 | fail (26%) | PASS (96%) | PASS (100%) | PASS (100%) |

## Robust (most favorable null), confidence 80%

**Standard path, 1 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (3%) | fail (21%) |
| 0.45 | fail (0%) | fail (1%) | fail (14%) | fail (53%) |
| 0.50 | fail (1%) | fail (4%) | fail (41%) | PASS (83%) |
| 0.55 | fail (3%) | fail (17%) | fail (74%) | PASS (97%) |
| 0.60 | fail (12%) | fail (45%) | PASS (94%) | PASS (100%) |

**Standard path, 2 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (3%) | fail (31%) |
| 0.45 | fail (0%) | fail (0%) | fail (20%) | fail (76%) |
| 0.50 | fail (0%) | fail (3%) | fail (61%) | PASS (97%) |
| 0.55 | fail (1%) | fail (21%) | PASS (94%) | PASS (100%) |
| 0.60 | fail (12%) | fail (64%) | PASS (100%) | PASS (100%) |

**Standard path, 4 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (2%) | fail (46%) |
| 0.45 | fail (0%) | fail (0%) | fail (25%) | PASS (95%) |
| 0.50 | fail (0%) | fail (2%) | PASS (84%) | PASS (100%) |
| 0.55 | fail (0%) | fail (26%) | PASS (100%) | PASS (100%) |
| 0.60 | fail (11%) | PASS (84%) | PASS (100%) | PASS (100%) |

**Consistency path, 1 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (5%) | fail (31%) |
| 0.45 | fail (0%) | fail (1%) | fail (24%) | fail (68%) |
| 0.50 | fail (1%) | fail (7%) | fail (59%) | PASS (92%) |
| 0.55 | fail (5%) | fail (28%) | PASS (87%) | PASS (99%) |
| 0.60 | fail (21%) | fail (64%) | PASS (98%) | PASS (100%) |

**Consistency path, 2 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (5%) | fail (46%) |
| 0.45 | fail (0%) | fail (0%) | fail (33%) | PASS (88%) |
| 0.50 | fail (0%) | fail (6%) | fail (78%) | PASS (99%) |
| 0.55 | fail (3%) | fail (37%) | PASS (98%) | PASS (100%) |
| 0.60 | fail (22%) | PASS (81%) | PASS (100%) | PASS (100%) |

**Consistency path, 4 round turn(s)/day**: cell = verdict (power); rows = win probability, columns = avg win / avg loss

| p \ R | 0.75 | 1 | 1.5 | 2 |
|---|---|---|---|---|
| 0.40 | fail (0%) | fail (0%) | fail (3%) | fail (64%) |
| 0.45 | fail (0%) | fail (0%) | fail (41%) | PASS (98%) |
| 0.50 | fail (0%) | fail (4%) | PASS (94%) | PASS (100%) |
| 0.55 | fail (1%) | fail (44%) | PASS (100%) | PASS (100%) |
| 0.60 | fail (21%) | PASS (94%) | PASS (100%) | PASS (100%) |

## Economics behind the cells (80%)

| Path | RT/day | p | R | gross edge $/trade/micro | net mean $/mo | net p50 | P(payout ≤12m) | P(beat random null) | power (matched) | verdict (matched) | verdict (robust) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| standard | 1 | 0.40 | 0.75 | -62.47 | -$114 | -$113 | 5% | 17% | 0.5% | fail | fail |
| standard | 1 | 0.40 | 1 | -36.07 | -$98 | -$104 | 15% | 27% | 1.8% | fail | fail |
| standard | 1 | 0.40 | 1.5 | -0.00 | -$17 | -$80 | 57% | 48% | 16.3% | fail | fail |
| standard | 1 | 0.40 | 2 | 25.50 | $266 | $43 | 87% | 71% | 50.0% | fail | fail |
| standard | 1 | 0.45 | 0.75 | -44.25 | -$102 | -$108 | 14% | 24% | 1.6% | fail | fail |
| standard | 1 | 0.45 | 1 | -18.03 | -$71 | -$96 | 38% | 36% | 6.6% | fail | fail |
| standard | 1 | 0.45 | 1.5 | 18.41 | $161 | -$2 | 84% | 66% | 41.5% | fail | fail |
| standard | 1 | 0.45 | 2 | 44.63 | $955 | $483 | 98% | 87% | 80.0% | fail | fail |
| standard | 1 | 0.50 | 0.75 | -26.03 | -$82 | -$100 | 32% | 32% | 4.9% | fail | fail |
| standard | 1 | 0.50 | 1 | 0.00 | -$1 | -$76 | 66% | 50% | 19.4% | fail | fail |
| standard | 1 | 0.50 | 1.5 | 36.81 | $632 | $289 | 96% | 83% | 73.2% | fail | fail |
| standard | 1 | 0.50 | 2 | 63.76 | $2,459 | $1,737 | 100% | 96% | 95.6% | pass | pass |
| standard | 1 | 0.55 | 0.75 | -7.81 | -$29 | -$86 | 59% | 45% | 15.1% | fail | fail |
| standard | 1 | 0.55 | 1 | 18.03 | $187 | $20 | 89% | 68% | 45.8% | fail | fail |
| standard | 1 | 0.55 | 1.5 | 55.22 | $1,757 | $1,102 | 100% | 95% | 92.6% | pass | fail |
| standard | 1 | 0.55 | 2 | 82.89 | $5,125 | $4,580 | 100% | 99% | 99.5% | pass | pass |
| standard | 1 | 0.60 | 0.75 | 10.41 | $112 | -$20 | 85% | 63% | 37.8% | fail | fail |
| standard | 1 | 0.60 | 1 | 36.07 | $681 | $332 | 98% | 85% | 75.8% | fail | fail |
| standard | 1 | 0.60 | 1.5 | 73.62 | $4,020 | $3,247 | 100% | 99% | 99.1% | pass | pass |
| standard | 1 | 0.60 | 2 | 102.01 | $8,536 | $8,814 | 100% | 100% | 100.0% | pass | pass |
| standard | 2 | 0.40 | 0.75 | -42.39 | -$127 | -$125 | 1% | 9% | 0.1% | fail | fail |
| standard | 2 | 0.40 | 1 | -24.48 | -$108 | -$109 | 7% | 21% | 0.6% | fail | fail |
| standard | 2 | 0.40 | 1.5 | -0.00 | -$26 | -$84 | 58% | 46% | 17.1% | fail | fail |
| standard | 2 | 0.40 | 2 | 17.31 | $444 | $157 | 94% | 78% | 66.6% | fail | fail |
| standard | 2 | 0.45 | 0.75 | -30.03 | -$114 | -$117 | 4% | 17% | 0.3% | fail | fail |
| standard | 2 | 0.45 | 1 | -12.24 | -$88 | -$100 | 27% | 31% | 3.9% | fail | fail |
| standard | 2 | 0.45 | 1.5 | 12.49 | $239 | $44 | 90% | 71% | 54.1% | fail | fail |
| standard | 2 | 0.45 | 2 | 30.29 | $1,897 | $1,210 | 100% | 95% | 94.0% | pass | fail |
| standard | 2 | 0.50 | 0.75 | -17.66 | -$98 | -$104 | 19% | 26% | 2.5% | fail | fail |
| standard | 2 | 0.50 | 1 | 0.00 | -$17 | -$80 | 65% | 48% | 20.3% | fail | fail |
| standard | 2 | 0.50 | 1.5 | 24.98 | $1,157 | $658 | 99% | 91% | 88.6% | pass | fail |
| standard | 2 | 0.50 | 2 | 43.27 | $5,356 | $4,810 | 100% | 99% | 99.6% | pass | pass |
| standard | 2 | 0.55 | 0.75 | -5.30 | -$53 | -$92 | 52% | 41% | 12.4% | fail | fail |
| standard | 2 | 0.55 | 1 | 12.24 | $252 | $65 | 93% | 73% | 57.7% | fail | fail |
| standard | 2 | 0.55 | 1.5 | 37.47 | $3,756 | $2,912 | 100% | 99% | 99.2% | pass | pass |
| standard | 2 | 0.55 | 2 | 56.25 | $10,109 | $10,625 | 100% | 100% | 100.0% | pass | pass |
| standard | 2 | 0.60 | 0.75 | 7.07 | $117 | -$10 | 87% | 64% | 43.2% | fail | fail |
| standard | 2 | 0.60 | 1 | 24.48 | $1,209 | $727 | 100% | 92% | 90.4% | pass | fail |
| standard | 2 | 0.60 | 1.5 | 49.96 | $8,337 | $8,428 | 100% | 100% | 100.0% | pass | pass |
| standard | 2 | 0.60 | 2 | 69.23 | $14,089 | $14,535 | 100% | 100% | 100.0% | pass | pass |
| standard | 4 | 0.40 | 0.75 | -28.45 | -$148 | -$149 | 0% | 2% | 0.0% | fail | fail |
| standard | 4 | 0.40 | 1 | -16.43 | -$120 | -$121 | 2% | 13% | 0.1% | fail | fail |
| standard | 4 | 0.40 | 1.5 | -0.00 | -$48 | -$88 | 50% | 42% | 17.3% | fail | fail |
| standard | 4 | 0.40 | 2 | 11.62 | $739 | $346 | 97% | 85% | 84.0% | pass | fail |
| standard | 4 | 0.45 | 0.75 | -20.15 | -$128 | -$125 | 1% | 9% | 0.1% | fail | fail |
| standard | 4 | 0.45 | 1 | -8.21 | -$102 | -$104 | 13% | 25% | 2.4% | fail | fail |
| standard | 4 | 0.45 | 1.5 | 8.38 | $322 | $94 | 93% | 75% | 68.7% | fail | fail |
| standard | 4 | 0.45 | 2 | 20.33 | $4,147 | $3,383 | 100% | 99% | 99.5% | pass | pass |
| standard | 4 | 0.50 | 0.75 | -11.86 | -$110 | -$112 | 6% | 20% | 0.8% | fail | fail |
| standard | 4 | 0.50 | 1 | 0.00 | -$43 | -$88 | 55% | 43% | 20.0% | fail | fail |
| standard | 4 | 0.50 | 1.5 | 16.77 | $2,356 | $1,584 | 100% | 97% | 98.1% | pass | pass |
| standard | 4 | 0.50 | 2 | 29.04 | $10,459 | $10,985 | 100% | 100% | 100.0% | pass | pass |
| standard | 4 | 0.55 | 0.75 | -3.56 | -$79 | -$96 | 35% | 34% | 9.0% | fail | fail |
| standard | 4 | 0.55 | 1 | 8.21 | $334 | $117 | 95% | 77% | 71.7% | fail | fail |
| standard | 4 | 0.55 | 1.5 | 25.15 | $7,943 | $7,904 | 100% | 100% | 100.0% | pass | pass |
| standard | 4 | 0.55 | 2 | 37.75 | $15,268 | $15,563 | 100% | 100% | 100.0% | pass | pass |
| standard | 4 | 0.60 | 0.75 | 4.74 | $107 | -$16 | 86% | 64% | 50.3% | fail | fail |
| standard | 4 | 0.60 | 1 | 16.43 | $2,309 | $1,552 | 100% | 97% | 98.4% | pass | pass |
| standard | 4 | 0.60 | 1.5 | 33.53 | $14,017 | $14,466 | 100% | 100% | 100.0% | pass | pass |
| standard | 4 | 0.60 | 2 | 46.46 | $18,443 | $18,561 | 100% | 100% | 100.0% | pass | pass |
| consistency | 1 | 0.40 | 0.75 | -62.47 | -$116 | -$117 | 1% | 26% | 0.1% | fail | fail |
| consistency | 1 | 0.40 | 1 | -36.07 | -$105 | -$108 | 5% | 35% | 0.9% | fail | fail |
| consistency | 1 | 0.40 | 1.5 | -0.00 | -$48 | -$96 | 30% | 47% | 15.6% | fail | fail |
| consistency | 1 | 0.40 | 2 | 25.50 | $224 | $9 | 66% | 68% | 51.5% | fail | fail |
| consistency | 1 | 0.45 | 0.75 | -44.25 | -$109 | -$109 | 5% | 32% | 0.7% | fail | fail |
| consistency | 1 | 0.45 | 1 | -18.03 | -$90 | -$104 | 17% | 40% | 5.2% | fail | fail |
| consistency | 1 | 0.45 | 1.5 | 18.41 | $131 | -$26 | 62% | 64% | 43.2% | fail | fail |
| consistency | 1 | 0.45 | 2 | 44.63 | $967 | $520 | 91% | 87% | 82.2% | pass | fail |
| consistency | 1 | 0.50 | 0.75 | -26.03 | -$96 | -$104 | 15% | 38% | 3.8% | fail | fail |
| consistency | 1 | 0.50 | 1 | 0.00 | -$31 | -$92 | 42% | 50% | 20.2% | fail | fail |
| consistency | 1 | 0.50 | 1.5 | 36.81 | $694 | $318 | 88% | 84% | 75.8% | fail | fail |
| consistency | 1 | 0.50 | 2 | 63.76 | $2,589 | $2,002 | 99% | 97% | 96.9% | pass | pass |
| consistency | 1 | 0.55 | 0.75 | -7.81 | -$54 | -$96 | 38% | 47% | 14.7% | fail | fail |
| consistency | 1 | 0.55 | 1 | 18.03 | $173 | -$3 | 73% | 68% | 49.2% | fail | fail |
| consistency | 1 | 0.55 | 1.5 | 55.22 | $1,989 | $1,389 | 98% | 96% | 94.6% | pass | pass |
| consistency | 1 | 0.55 | 2 | 82.89 | $5,208 | $4,912 | 100% | 100% | 99.7% | pass | pass |
| consistency | 1 | 0.60 | 0.75 | 10.41 | $89 | -$37 | 70% | 64% | 40.6% | fail | fail |
| consistency | 1 | 0.60 | 1 | 36.07 | $782 | $395 | 94% | 87% | 81.6% | pass | fail |
| consistency | 1 | 0.60 | 1.5 | 73.62 | $4,363 | $3,865 | 100% | 99% | 99.5% | pass | pass |
| consistency | 1 | 0.60 | 2 | 102.01 | $8,531 | $8,536 | 100% | 100% | 100.0% | pass | pass |
| consistency | 2 | 0.40 | 0.75 | -42.39 | -$127 | -$125 | 0% | 16% | 0.0% | fail | fail |
| consistency | 2 | 0.40 | 1 | -24.48 | -$111 | -$112 | 2% | 31% | 0.5% | fail | fail |
| consistency | 2 | 0.40 | 1.5 | -0.00 | -$52 | -$100 | 31% | 46% | 18.0% | fail | fail |
| consistency | 2 | 0.40 | 2 | 17.31 | $451 | $135 | 80% | 76% | 67.9% | fail | fail |
| consistency | 2 | 0.45 | 0.75 | -30.03 | -$116 | -$117 | 1% | 26% | 0.1% | fail | fail |
| consistency | 2 | 0.45 | 1 | -12.24 | -$99 | -$104 | 10% | 37% | 3.5% | fail | fail |
| consistency | 2 | 0.45 | 1.5 | 12.49 | $232 | $18 | 72% | 69% | 55.7% | fail | fail |
| consistency | 2 | 0.45 | 2 | 30.29 | $2,138 | $1,550 | 98% | 96% | 94.9% | pass | pass |
| consistency | 2 | 0.50 | 0.75 | -17.66 | -$105 | -$108 | 7% | 34% | 1.7% | fail | fail |
| consistency | 2 | 0.50 | 1 | 0.00 | -$42 | -$96 | 39% | 48% | 20.2% | fail | fail |
| consistency | 2 | 0.50 | 1.5 | 24.98 | $1,384 | $848 | 96% | 92% | 90.7% | pass | fail |
| consistency | 2 | 0.50 | 2 | 43.27 | $5,613 | $5,373 | 100% | 100% | 99.8% | pass | pass |
| consistency | 2 | 0.55 | 0.75 | -5.30 | -$73 | -$101 | 28% | 43% | 11.4% | fail | fail |
| consistency | 2 | 0.55 | 1 | 12.24 | $269 | $49 | 79% | 73% | 59.8% | fail | fail |
| consistency | 2 | 0.55 | 1.5 | 37.47 | $4,272 | $3,740 | 100% | 99% | 99.5% | pass | pass |
| consistency | 2 | 0.55 | 2 | 56.25 | $10,208 | $10,293 | 100% | 100% | 100.0% | pass | pass |
| consistency | 2 | 0.60 | 0.75 | 7.07 | $101 | -$28 | 69% | 64% | 45.1% | fail | fail |
| consistency | 2 | 0.60 | 1 | 24.48 | $1,496 | $948 | 98% | 94% | 92.7% | pass | pass |
| consistency | 2 | 0.60 | 1.5 | 49.96 | $8,725 | $8,735 | 100% | 100% | 100.0% | pass | pass |
| consistency | 2 | 0.60 | 2 | 69.23 | $14,966 | $15,057 | 100% | 100% | 100.0% | pass | pass |
| consistency | 4 | 0.40 | 0.75 | -28.45 | -$149 | -$149 | 0% | 5% | 0.0% | fail | fail |
| consistency | 4 | 0.40 | 1 | -16.43 | -$120 | -$121 | 0% | 23% | 0.1% | fail | fail |
| consistency | 4 | 0.40 | 1.5 | -0.00 | -$70 | -$100 | 23% | 43% | 17.0% | fail | fail |
| consistency | 4 | 0.40 | 2 | 11.62 | $834 | $424 | 90% | 85% | 84.7% | pass | fail |
| consistency | 4 | 0.45 | 0.75 | -20.15 | -$128 | -$129 | 0% | 16% | 0.0% | fail | fail |
| consistency | 4 | 0.45 | 1 | -8.21 | -$106 | -$108 | 4% | 34% | 2.0% | fail | fail |
| consistency | 4 | 0.45 | 1.5 | 8.38 | $350 | $89 | 79% | 75% | 70.2% | fail | fail |
| consistency | 4 | 0.45 | 2 | 20.33 | $4,545 | $4,145 | 100% | 99% | 99.7% | pass | pass |
| consistency | 4 | 0.50 | 0.75 | -11.86 | -$112 | -$112 | 2% | 30% | 0.7% | fail | fail |
| consistency | 4 | 0.50 | 1 | 0.00 | -$64 | -$100 | 30% | 45% | 20.2% | fail | fail |
| consistency | 4 | 0.50 | 1.5 | 16.77 | $2,803 | $2,202 | 99% | 98% | 98.4% | pass | pass |
| consistency | 4 | 0.50 | 2 | 29.04 | $10,788 | $10,861 | 100% | 100% | 100.0% | pass | pass |
| consistency | 4 | 0.55 | 0.75 | -3.56 | -$91 | -$104 | 17% | 39% | 9.3% | fail | fail |
| consistency | 4 | 0.55 | 1 | 8.21 | $387 | $115 | 84% | 77% | 73.2% | fail | fail |
| consistency | 4 | 0.55 | 1.5 | 25.15 | $8,449 | $8,413 | 100% | 100% | 100.0% | pass | pass |
| consistency | 4 | 0.55 | 2 | 37.75 | $17,199 | $17,249 | 100% | 100% | 100.0% | pass | pass |
| consistency | 4 | 0.60 | 0.75 | 4.74 | $99 | -$32 | 68% | 64% | 52.2% | fail | fail |
| consistency | 4 | 0.60 | 1 | 16.43 | $2,884 | $2,213 | 100% | 98% | 98.7% | pass | pass |
| consistency | 4 | 0.60 | 1.5 | 33.53 | $15,173 | $15,253 | 100% | 100% | 100.0% | pass | pass |
| consistency | 4 | 0.60 | 2 | 46.46 | $23,122 | $23,154 | 100% | 100% | 100.0% | pass | pass |

## Assumptions and limits

- **Everything the null baseline assumes, this inherits.** Fee schedule, gross payouts with
  no profit split applied, the greedy payout policy, one Combine attempt at a time, and a
  maximum of 5 live XFAs. See `reports/funnel_null_baseline.md` for the full list. If
  Topstep keeps a share of payouts, every income figure here is optimistic by that share.
- **Costs are a lower bound.** $1.22 round-turn commission is still a blocking TODO to
  reconfirm at checkout, and the slippage model rests on two days of book data and excludes
  latency, adverse selection and queue position. A candidate that only passes the gate at
  modelled cost does not pass.
- **The quality model is a Bernoulli caricature, deliberately.** Each trade is an independent
  draw with fixed win probability and fixed win/loss ratio. Real strategies have serially
  correlated returns, regime dependence, and variable trade sizing, none of which are
  modelled. This is a screen for ruling candidates *out*, not a forecast of what a candidate
  will earn. Passing is necessary, not sufficient.
- **Monte Carlo error.** 8,000 runs per grid point gives a standard error on power of about
  0.5 percentage points near power = 0.5, tighter at the extremes. The `power_lower95`
  column carries this explicitly, and the verdict rule already spends it.
- **The grid is coarse.** 5 x 4 x 3 points. Interpolating between cells is not validated; a
  candidate that lands between rungs should be screened by re-running
  `funnel.power_gate.screen(...)`, which returns the nearest grid point and its full
  economics rather than an interpolated number.
- **The robust null is intentionally punitive.** It compares a candidate at 2 micros against
  a coin-flipper free to choose any size up to 30. That is not a fair fight, and it is not
  meant to be — it is the bar that survives the objection "you only beat the null because
  you happened to size differently."
- **Re-scoring without re-simulating.** `reports/power_gate_samples.npz` holds every grid
  point's sorted monthly-net-income samples, so verdicts can be recomputed against any
  other critical value or confidence level without paying the 48-minute run again.
