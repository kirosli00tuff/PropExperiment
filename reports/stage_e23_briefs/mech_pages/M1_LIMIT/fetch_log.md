# M1_LIMIT fetch log (Stage E.23 P1.2)

| URL | fetch time (PDT) | sha256 | tool | saved file |
|---|---|---|---|---|
| https://repub.eur.nl/robots.txt | 2026-10-17T02:18:04-07:00 | 38521675b54e81b02e57533ef47ca802adc2fd80338081d99a2c677e69ba51cd | curl (http 200) | eur_robots.txt |
| https://repub.eur.nl/pub/76539 | 2026-10-17T02:18:06-07:00 | 41a34f279db8083f348f12aacfc8022f0581842e891b6feef05403ee84e94ce5 | curl (http 200) | eur_76539.html |
| https://eprints.gla.ac.uk/robots.txt | 2026-10-17T02:18:07-07:00 | 29433f0f68d8783f37823f841258d1162da7a4f1f75991bd4004555a15a86cbd | curl (http 200) | gla_robots.txt |
| https://eprints.gla.ac.uk/74442/ | 2026-10-17T02:18:08-07:00 | 4081046974e02e60b8db712810749e16ee7a2ade93cfb1fbc3bd292a5274e69a | curl (http 200) | gla_74442.html |
| https://dspace.stir.ac.uk/robots.txt | 2026-10-17T02:18:09-07:00 | 2b8c61fd9799e3625549724a8a4f5a425c152e019723794f9a71794a8ef8dd06 | curl (http 200) | stir_robots.txt |
| https://dspace.stir.ac.uk/handle/1893/11985?mode=full | 2026-10-17T02:18:10-07:00 | 83d81b68f6e8b783d3722376916003cc5af4fa7d02fa4be2dec4cb6e6fdf37ea | curl (http 200) | stir_11985.html |
| https://mpra.ub.uni-muenchen.de/35927/1/MPRA_paper_35927.pdf | 2026-10-17T02:18:52-07:00 | 716dbac87ea84d1a616c5c8116abb587b5bf8687dcc0ce9b3272e58067463549 | curl (http 200) | reiffen_buyuksahin_mpra35927.pdf |
| https://opus.lib.uts.edu.au/robots.txt | 2026-10-17T02:18:55-07:00 | c5277b72eb00a71f28799cea065764d7a9d099fb27b8553c535b8461db25ee75 | curl (http 200) | uts_robots.txt |
| https://opus.lib.uts.edu.au/handle/10453/5375 | 2026-10-17T02:18:57-07:00 | f13a62c9cf3dc27b54fc6f24c33763a1f99954a339c844d44ada07be07348dd1 | curl (http 200) | uts_5375.html |
| https://www.efmaefm.org/robots.txt | 2026-10-17T02:18:57-07:00 | fb2d9f058c2010c57f86a05ae33d282f33e3825290c66b8b120cd177416c6bdf | curl (http 503) | efma_robots.txt |
| https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/fut.21999 | 2026-10-17T02:20:11-07:00 | 61b0cd4740ed5a15dbddeebea451fa00425e56366ae60a6dd763d23ca9accda0 | Firecrawl scrape, pdf parser, query directQuote (scrapeId 01a14928-ea6c-75c9-800e-78320741d793); curl/Scrapling 403 per E.20 log 2026-10-11 | jqr2019_jfm_fig4_firecrawl.md |
| (derived) pdftotext of reiffen_buyuksahin_mpra35927.pdf | 2026-10-17T02:20:11-07:00 | 90a14eee10ef13da81ca658b7634190edb68b347f312a74d1f6c390133e9ea94 | pdftotext (plain) | rb_plain.txt |
| https://ageconsearch.umn.edu/record/309645/files/Blair_Janzen_NCCC-134_2020.pdf | 2026-10-17T02:20:59-07:00 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | curl (http 202) | janzen_nccc134_2020.pdf |
| https://ageconsearch.umn.edu/record/309645/files/Blair_Janzen_NCCC-134_2020.pdf | 2026-10-17T02:21:2x-07:00 | (none) | scrapling extract get refused (.pdf output not supported); empty curl file deleted | (none) |
| https://ageconsearch.umn.edu/record/309645?ln=en | 2026-10-17T02:21:29-07:00 | 940a6dc1bbdda082fd7e167426ce4763ef56407b81ae4f4ecb8c8f5dd5dc82f4 | WebFetch 403; scrapling extract get | ageconsearch_309645.md |
| https://ageconsearch.umn.edu/record/309645/files/Blair_Janzen_NCCC-134_2020.pdf | 2026-10-17T02:22:22-07:00 | 0cc7181ce1616dc24aac85fabbd8352b1040f8fb2cb20c01f5eb4e554c6f14ec | Firecrawl scrape directQuote (scrapeId 01a1492a-ac7e-72e0-9c87-89fdec0c07da) after curl 202-empty and scrapling bot-check | fontinelle_janzen_nccc134_2020_firecrawl.md |
| https://www.qmul.ac.uk/robots.txt | 2026-10-17T02:22:44-07:00 | 0e0226948e2b764b28a0b5c14cabd2693bf6de1a9dbcfcc8c06e8e3272ef5207 | curl (http 200) | qmul_robots.txt |
| https://qmul.ac.uk/sef/media/econ/research/workingpapers/2006/items/wp579.pdf | 2026-10-17T02:22:51-07:00 | 4d45df9c3670e78fd9e57e74fbcbdc444a36d2ae20926fe36ce85d2c46cc5323 | curl (http 200) | qmul_wp579.pdf |
| (derived) pdftotext of qmul_wp579.pdf | 2026-10-17T02:22:58-07:00 | 6132e9d467873ad06c69dc1a82edaf423c3f4ed111ce61dbfee436438696d9c0 | pdftotext | qmul_wp579.txt |
| (derived) pdftotext -layout of reiffen_buyuksahin_mpra35927.pdf | 2026-10-17T02:19 | ca83a44efc3b55c8bcbe079a9c1139beb99c78b10bb92006875a9224ad478cad | pdftotext -layout | reiffen_buyuksahin_mpra35927.txt |
| https://ideas.repec.org/robots.txt | 2026-10-17T02:23:29-07:00 | 4620fbdb346382486937732e10fb82fe1cab79fa1d839d85de8a4798c1702d46 | curl (http 200) | ideas_robots.txt |
| https://ideas.repec.org/a/eee/finana/v12y2003i3p311-328.html | 2026-10-17T02:23:30-07:00 | 9f1244f965e67d8c3d76e30d9d3086e8067a2fae28e02de83fe23aba1152469c | curl (http 200) | ideas_veld_merkoulova_2003.html |
| https://ideas.repec.org/a/wly/jfutmk/v20y2000i5p445-466.html | 2026-10-17T02:23:33-07:00 | 7f81190816a823b57af30fbf12dc42ab58e8d20a420b3533b85d6e217bfafd68 | curl (http 200) | ideas_park_2000.html |
| https://ideas.repec.org/a/bla/jfinan/v52y1997i2p885-99.html | 2026-10-17T02:23:37-07:00 | 63fdd166199290b81efbf8323b24156e3eda15536f151540057635691acba9b8 | curl (http 200) | ideas_kim_rhee_1997.html |
