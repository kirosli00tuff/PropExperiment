#!/usr/bin/env bash
# Adds or replaces DATABENTO_API_KEY3 in .env from hidden input.
# The key is never echoed, printed, logged or passed on the command line.
# Run it yourself in a terminal on this laptop:  bash scripts/set_databento_key3.sh
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
tmp=""
trap '[ -z "$tmp" ] || rm -f "$tmp"' EXIT
read -r -s -p "Paste the new Databento API key (hidden), then press Enter: " KEY
echo
KEY=${KEY//$'\r'/}
if [ -z "${KEY}" ]; then echo "Nothing entered; .env unchanged."; exit 1; fi
if [ -d .env ]; then echo ".env is a directory; refusing."; exit 1; fi
touch .env
tmp="$(mktemp .env.XXXXXX)"
grep -Ev '^[[:space:]]*(export[[:space:]]+)?DATABENTO_API_KEY3[[:space:]]*=' .env > "$tmp" || true
printf 'DATABENTO_API_KEY3=%s\n' "$KEY" >> "$tmp"
unset KEY
mv -T "$tmp" .env
chmod 600 .env
echo "DATABENTO_API_KEY3 set in .env (value not shown)."
