The lead (Opus 5.5 xhigh) kept the decomposition, the Part 1 request, the spec and its v2 rulings, every lead ruling
(OC list), the purchases' approvals, the verdict reading and this synthesis. Workers (worker-* agent files; times,
tokens and status in section 8's final table). Briefs are in reports/stage_e31_briefs/brief_*.md.

| Agent (role) | Model asked / ran | Brief | Artifacts |
|---|---|---|---|
| FableProbe-FableMed (availability probe) | fable / sonnet 5.5 | inline | none |
| VolumeCoder-OpusHigh (Part 1 measures) | opus / opus | brief_volume.md | work/pilot/vol_measure.py, tests, stage_e31_volume.md |
| VolumeVerifier (Part 1 check) | fable / sonnet 5.5 | brief_volverify.md | work/verify_vol/VERIFY_volume.md |
| KResearch-OpusHigh (K algorithm) | opus / opus | brief_kresearch.md | research/K_algorithm.md, K_fetch_log.md, pages/K/ |
| DataResearch-OpusHigh (Databento, USDA, limits, specs) | opus / opus | brief_dataresearch.md | research/data_facts.md, usda_releases.csv |
| UsdaExt-OpusHigh (USDA 2020-12..2022-10) | opus / opus | brief_usdaext.md | research/usda_releases_ext.csv |
| PullCoder-OpusXHigh (purchase, verify) | opus / opus | brief_pullcoder.md | pilot31_common.py, pull31.py, verify31.py, README31.md |
| StatsCoder-OpusXHigh (statistics, kill rule) | opus / opus | brief_statscoder.md | stats31*.py, tests |
| SimCoder-OpusXHigh (engine) | opus / opus | brief_simcoder.md | mbo_book31.py, kalgo31.py, measure31*.py, README_measure31.md |
| FixCoder-OpusXHigh (pass-1 fixes, canary check) | opus / opus | brief_fixcoder.md | pull31 retry and lock, verify31 checks, canary_check31.py |
| SpecReviewer (pass 1) | fable / sonnet 5.5 | brief_specreview.md | R_spec31.md |
| EngineReviewer (pass 2) | fable / sonnet 5.5 | brief_enginereview.md | R_engine31.md |
| ReCheck (both passes) | fable / sonnet 5.5 | brief_recheck.md | R_recheck31.md |
| PilotVerifier (verdict numbers) | fable / sonnet 5.5 | brief_pilotverify.md | work/verify_pilot/VERIFY_pilot.md |
| OpusVerifier-OpusXHigh (verdict numbers, Pro branch) | opus / opus | brief_opusverify.md | work/verify_pilot_opus/VERIFY_pilot_opus.md |

At most 4 workers ran at once. Workers cut by usage limits were resumed from their transcripts (SendMessage), never
restarted; a second copy of this session (tmux claude-retry-*, 10-23 01:07, closed by the planner) made one edit, which
the lead reviewed and superseded (OC-6).
