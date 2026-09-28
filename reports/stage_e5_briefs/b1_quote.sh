#!/usr/bin/env bash
# Stage E.5 Task B1: the fresh step 2 quote (free) of the purchase-mode set, under the committed v5 code.
# The frozen quote writer updates reports/stage_e2b_step2_quotes.{json,md} (E.2b's record); the E.5 result is copied to
# reports/stage_e5_step2_quotes.{json,md} and E.2b's files are restored from git, so E.2b's record stays as it was.
set -u
cd /home/kiros-li/Documents/GitHub/PropExperiment
SCR=/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/b56ee083-7d81-4a9a-b281-328c8ac9ffa4/scratchpad
mkdir -p "$SCR"
P=$(mktemp -d "$SCR/e5pyc.XXXXXX")
echo "start $(TZ=America/Vancouver date +%H:%M:%S)"
echo "ledger before: $(wc -l < ledger/databento_spend.jsonl) lines $(sha256sum ledger/databento_spend.jsonl | cut -c1-16)"
PYTHONPYCACHEPREFIX=$P uv run python -m data.pull_step2 --quote-only --set clusters-legs 2>&1 | tail -4
echo "rc ${PIPESTATUS[0]} end $(TZ=America/Vancouver date +%H:%M:%S)"
echo "ledger after: $(wc -l < ledger/databento_spend.jsonl) lines $(sha256sum ledger/databento_spend.jsonl | cut -c1-16)"
