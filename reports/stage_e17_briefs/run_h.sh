#!/usr/bin/env bash
# Stage E.17 step 13: run ONE base-rule test once (H1..H4 with the run manifest; H5 without), detached-safe.
# Usage: run_h.sh <H1|H2|H3|H4|H5>. Log: reports/stage_e17_briefs/run_<test>.log (rc line at the end).
set -u
cd "$(dirname "$0")/../.."
T=${1:?test}
L=reports/stage_e17_briefs/run_$T.log
P=$(mktemp -d /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0dcecb5d-5f79-4bc8-8a23-a1ca768d375b/scratchpad/e17pyc.XXXXXX)
FREEZE="--freeze reports/stage_e16_freeze.json --freeze-sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4"
MAN="--manifest reports/stage_e17_run_manifest.json --manifest-sha256 256a5410c03065a746d229c2cddbc85240de8fe57db2e8fe77467c1483ffa74d"
[ "$T" = "H5" ] && MAN=""
CMD="uv run --no-sync python -m base_rules.run run --test $T $FREEZE $MAN"
{ TZ=America/Vancouver date; echo "\$ nice -n 10 $CMD"; } > "$L"
PYTHONPYCACHEPREFIX=$P /usr/bin/time -v nice -n 10 $CMD >> "$L" 2>&1
echo "rc=$?" >> "$L"
TZ=America/Vancouver date >> "$L"
