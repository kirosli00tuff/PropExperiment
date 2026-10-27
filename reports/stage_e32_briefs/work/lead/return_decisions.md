D1. Keep or drop the protocol-added test DSR (DSR > 0.95 at N with V = 1/(T_test - 1)). Recommendation: keep. It is
    the conservative reading of V43's "DSR at N" and does not depend on how similar the tested candidates are.
    Keeping it: b_test 0.1649, binding selection threshold 0.2007 (t 5.66), 1.22 ticks net per 15-minute trade at 4
    a date. Dropping it: b_test 0.1017 (t > 3 alone), G4 0.1373, binding threshold 0.1724 (G3), about 1.05 ticks at
    the same rate (scaled from P7.2's random-walk line, 1.22 x 0.1724/0.2007; an estimate). Deadline: before E.33's
    C1 registration, as a protocol amendment (a new version hashed before C1, P7.2 restated); after C1 it cannot
    change (P7.2).
D2. Amend V14 (c) for this test so that the program verdict's DSR uses V = 1/(T_test - 1) (ProtocolReview AR-1).
    Recommendation: amend, before the test is registered. As coded, V takes the population variance of the 2-3
    tested Sharpes, so SR0 = 3.2045 x their SD: beside one null companion no true Sharpe passes (SR0 = 1.60 x the
    strong member's), and beside a weaker real one the pass probability falls with the gap (true 0.25 beside 0.15:
    about 0.84; beside 0.10: about 0.09). Amending makes the DSR part of the verdict equal to the protocol-added
    check, whose power P7.2 tabulates; Holm, t > 3 and PBO stay. Amending can only loosen the combined bar to that
    point, so the discovery outcomes cannot steer it further.
D3. Launch E.33 (docs/prompts/STAGE_E.33.md, run the frozen protocol). Recommendation: launch after D1 is recorded,
    on Max, under its prompt's deadlines (search cut 07:00 PDT 2026-10-28, nothing after 09:00). Compute (P5, a
    guess until E.33's probe): ZM book rebuild 9-18 minutes; ZS/ZL re-split about 90 s of decoding and up to 32.5 GB
    of disk; features 1-3 CPU-hours; synthetic proofs 4,800 fits, 0.9-1.4 h of wall time at the balanced probes
    (1.5-9 h at the guesses); the search 1,800 fits, 1-4 h of wall time at <= 8 threads; memory far under the 70%
    rule. Usage: this stage used {{E32_TOTAL}} tokens over its three lead sessions (section 8); E.33 has more
    code to write and test (split, sampler, labels, simulator, purged CV, guard, P8) and fewer readers, so expect the
    same order (an estimate from this stage's measured total, not a measurement of E.33).
D4. Test-data quote plan (P9). Recommendation: no quote until a funded Databento account exists and E.33 has a
    non-empty Tier A; then one quote for ZM.v.0 MBO, ZS.v.0 and ZL.v.0 MBP-1 and the ZM, ZS and ZL definitions,
    2017-05-21..2020-11-30 (trade dates from 2017-05-22), logged before approval. Scale: E.31 paid 121.65 USD for the
    39 months of 2020-12..2024-02 in these schemas; 43 months at the same rates would be about 134 USD (an estimate
    by proportion; 2017-2019 volumes were lower, so it may cost less). If Tier A is empty, nothing is bought.
D5. DATABENTO_API_KEY3 was still non-empty in .env at the start check (V50 said wipe and remove). Recommendation:
    the user removes it (checked by name only; never printed).
D6. The testable window starts 2017-05-22 (MBO from 2017-05-21): the E.33 prompt's "2017-05-01" is superseded by
    protocol P9. Recommendation: note it in the E.33 prompt or a decision line; the seal keeps covering 2017-05-01
    onward (sealing three extra weeks costs nothing).
D7. tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha fails (1 of 8,125
    in the full suite). Cause: the E.20 H6 test (last changed in 498fd05, 2026-10-11) asserts the preflight refuses
    for a "freeze manifest" reason, but the preflight now stops earlier because the harness freeze is v14
    (2e908c81...) and the test expects ece91ae8e699...; it fails identically at HEAD 3a75f3b in a clean worktree,
    and E.29 and E.31 recorded it as the known by-design failure since harness v13. E.32 did not cause it (no
    tracked file changed). Recommendation: a small separate change that re-pins the test to the current harness or
    marks it xfail with the reason, so the suite is green again and a new failure stands out.
D8. E.33's deadlines are quoted by value in P10 from the prompt as amended at 08:16 and the prompt's current times
    govern. Recommendation: if the E.33 times change again, change only the prompt; the protocol need not change.
