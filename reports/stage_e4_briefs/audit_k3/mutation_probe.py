"""MemberAuditor-K3, item 11: do the signal-field tests discriminate the field they claim?
Each member's plan is mutated IN MEMORY (the repository is untouched) so that a signal read takes
the other bar field, and the test's own scenario is re-run through the engine. A scenario that
still produces the expected fills under the mutation does not pin the field. Also runs two
scenarios the tests do not cover (a fill deferred past the exit bar; ldnrev with opens and closes
that disagree). Run: PYTHONPATH=. uv run python reports/stage_e4_briefs/audit_k3/mutation_probe.py
"""

from __future__ import annotations

from strategy.members.k3 import ldnmom, ldnrev
from strategy.members.k3._event_common import CLOSE, OPEN, Plan
from tests.test_e4_k3_members_b import fills, flat, hm, intents, run, trade
from tests.test_e4_k3_members_b_ldn import ME_STD, STD, day, mom_day, rev_day


def mutate(member, which: str) -> None:
    """Swap the field of the reads: 'all' -> OPEN, 'entry' -> the entry-bar read to OPEN,
    'start' -> the first read to CLOSE."""
    new = {}
    for d, p in member._core.plans.items():
        reads = list(p.reads)
        if which == "all":
            reads = [(ns, OPEN) for ns, _ in reads]
        elif which == "entry":
            reads = [(ns, OPEN if ns == p.entry_ns else f) for ns, f in reads]
        elif which == "start":
            reads = [(ns, CLOSE if i == 0 else f) for i, (ns, f) in enumerate(reads)]
        new[d] = Plan(tuple(reads), p.entry_ns, p.exit_ns)
    member._core.plans = new


# 1. test_ldnrev_signal_reads_closes_not_opens: paths from the test file (line 103)
paths = {hm(9, 49): (-5, 0, -5, 0), hm(9, 59): (9, 9, 1, 1)}
expected = trade(ME_STD, "10:05", "10:20", side="sell")
base = run(ldnrev.make_6j(), [day(ME_STD, paths=paths)])
m = ldnrev.make_6j()
mutate(m, "all")
mut = run(m, [day(ME_STD, paths=paths)])
print("ldnrev closes-not-opens: unmutated passes:", fills(base) == expected,
      "| reads OPEN instead: still passes:", fills(mut) == expected)
# a discriminating scenario: opens fall, closes rise
paths2 = {hm(9, 49): (5, 5, -2, -2), hm(9, 59): (-4, 3, -4, 3)}  # open 5 -> -4 (fall); close -2 -> 3 (rise)
b2 = run(ldnrev.make_6j(), [day(ME_STD, paths=paths2)])
m2 = ldnrev.make_6j()
mutate(m2, "all")
x2 = run(m2, [day(ME_STD, paths=paths2)])
print("  discriminating scenario: code gives", [f[2] for f in fills(b2)], "(expected sell);",
      "OPEN mutation gives", [f[2] for f in fills(x2)])

# 2. the rev_day-based sign tests (flat bars: open == close on the signal bars)
b = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3)])
m3 = ldnrev.make_6e()
mutate(m3, "all")
x3 = run(m3, [rev_day(ME_STD, hm(10, 0), 3)])
print("ldnrev rise-sells (rev_day): unmutated", fills(b) == expected, "| OPEN mutation still passes:",
      fills(x3) == expected)

# 3. test_ldnmom_signal_is_the_open_of_t_l_minus_15_to_the_close_of_t_l_minus_13 (line 243)
paths = {hm(9, 44): flat(-20), hm(9, 45): (-3, 6, -3, 5), hm(9, 46): flat(30),
         hm(9, 47): (8, 8, 1, 1)}
expected = trade(STD, "09:48", "10:05", side="buy")
base = run(ldnmom.make_6e(), [day(STD, paths=paths)])
for which in ("entry", "start", "all"):
    m = ldnmom.make_6e()
    mutate(m, which)
    mut = run(m, [day(STD, paths=paths)])
    print(f"ldnmom open(9:45)->close(9:47): unmutated passes: {fills(base) == expected} | "
          f"mutation {which!r} still passes: {fills(mut) == expected}")
# a discriminating scenario for the entry bar's field: open(9:47) high, close(9:47) low
paths3 = {hm(9, 45): (-3, 6, -3, 5), hm(9, 47): (8, 8, -6, -6)}  # close - open(9:45) = -3 (sell); open - open = +11 (buy)
b3 = run(ldnmom.make_6e(), [day(STD, paths=paths3)])
m4 = ldnmom.make_6e()
mutate(m4, "entry")
x4 = run(m4, [day(STD, paths=paths3)])
print("  discriminating scenario: code gives", [f[2] for f in fills(b3)], "(expected sell);",
      "entry-OPEN mutation gives", [f[2] for f in fills(x4)])

# 4. a fill deferred past the exit bar (no bars 10:05..10:24 after the 10:04 entry decision)
gap = frozenset(range(hm(10, 5), hm(10, 25)))
res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3, skip=gap)])
print("ldnrev entry fill deferred past the exit bar: intents", intents(res))
print("  fills", fills(res))

# 5. ldnmom: the same deferral (no bars 09:48..10:06)
gap = frozenset(range(hm(9, 48), hm(10, 7)))
res = run(ldnmom.make_6e(), [mom_day(STD, hm(10, 0), 3, skip=gap)])
print("ldnmom entry fill deferred past the exit bar: intents", intents(res))
print("  fills", fills(res))
