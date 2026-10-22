#!/bin/bash
E=$(grep -E '^OPENALEX_EMAIL=' /home/kiros-li/Documents/GitHub/PropExperiment/.env | cut -d= -f2- | tr -d "\"'")
for d in "$@"; do
  curl -s "https://api.openalex.org/works/https://doi.org/${d}?mailto=${E}" | python3 -I -c "import json,sys; d=json.load(sys.stdin); print(d.get('display_name'), d.get('publication_year'), d.get('open_access',{}).get('oa_status'), d.get('open_access',{}).get('oa_url'), (d.get('best_oa_location') or {}).get('pdf_url'), d.get('cited_by_count'))"
  sleep 1
done
